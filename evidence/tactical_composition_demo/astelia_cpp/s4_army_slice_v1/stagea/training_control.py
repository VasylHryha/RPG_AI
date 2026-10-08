"""Offline projection, owner time authority and durable epoch transactions.

No model construction, sampling, training or process launch on import.
"""
from datetime import date
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import time

FITS=tuple((arm,41001,arm) for arm in ('N1','N1h','N1r','N2','N2J0'))


def training_cap(here):
    path=Path(here)/'_local/TRAIN_CAP.json'
    if not path.exists():
        raise RuntimeError('Claude-written owner TRAIN_CAP.json required before timing or training')
    from hashlib import sha256
    raw=path.read_bytes(); value=json.loads(raw)
    seconds=value.get('cap_seconds')
    if isinstance(seconds,bool) or not isinstance(seconds,(float,int)) or not math.isfinite(seconds) or seconds<=0:
        raise ValueError('TRAIN_CAP cap_seconds must be finite and positive')
    if value.get('approved_by')!='owner':
        raise ValueError('TRAIN_CAP approved_by must be owner')
    date.fromisoformat(value['date'])
    return dict(**value,path=str(path),sha256=sha256(raw).hexdigest())


class TrainingDeadline:
    """Live owner reductions tighten the admitted deadline; increases cannot extend it."""
    def __init__(self,here,absolute,admitted_cap):
        self.here=here; self.absolute=absolute; self.admitted_cap=admitted_cap
        self.started=absolute-admitted_cap
        self.checked_at=-math.inf; self.owner_cap=admitted_cap

    def current(self):
        now=time.monotonic()
        if now-self.checked_at>=1.:
            self.owner_cap=min(self.owner_cap,training_cap(self.here)['cap_seconds']); self.checked_at=now
        return min(self.absolute,self.started+self.owner_cap)

    def __sub__(self,other):
        return self.current()-other

    def __rsub__(self,other):
        return other-self.current()

    def __lt__(self,other):
        return self.current()<other

    def __gt__(self,other):
        return self.current()>other

    def __le__(self,other):
        return self.current()<=other

    def __ge__(self,other):
        return self.current()>=other

    def __str__(self):
        return str(self.absolute)


def measured_cores():
    values={}
    for key in ('hw.perflevel0.physicalcpu','hw.ncpu'):
        try:
            result=subprocess.run(['sysctl','-n',key],capture_output=True,text=True,timeout=5)
            values[key]=int(result.stdout) if result.returncode==0 else None
        except (OSError,ValueError,subprocess.TimeoutExpired):
            values[key]=None
    # Fail conservatively to one process if performance cores are unavailable.
    cores=values['hw.perflevel0.physicalcpu']
    ncpu=values['hw.ncpu']
    if cores is not None and ncpu is not None:
        cores=min(cores,ncpu)
    return dict(measurements=values,slots=max(1,min(len(FITS),(cores or 2)//2)),
                threads_per_process=2,nice_increment=10,
                fallback='one process when performance core measurement unavailable')


def lanes(costs,slots):
    """Deterministic longest-first lane assignment; each lane runs sequentially."""
    groups=[dict(arms=[],wall_seconds=0.) for _ in range(slots)]
    for name,seconds in sorted(costs.items(),key=lambda item:(-item[1],item[0])):
        lane=min(groups,key=lambda g:g['wall_seconds'])
        lane['arms'].append(name); lane['wall_seconds']+=seconds
    return groups


def project(sample,budget,topology,completed=None,sealed_arms=(),sealed_parity=False):
    completed=completed or {}; epochs=budget['epochs']; arms={}; fit_costs={}
    old_total=sample['preprocessing_seconds']; parity_total=0.
    for kind,stats in sample['samples'].items():
        # The first measurement is retained and explicitly reported as warm-up.
        # Remaining medium/high workload measurements set the conservative step wall.
        measured=stats[1:]
        if not measured or len(stats)>20:
            raise ValueError('need warm-up plus measured steps, bounded to 20 per arm')
        step_wall=max(s['wall_seconds'] for s in measured)
        proxy=max(s['wall_seconds']/s['work_units'] for s in stats)
        units=budget['work_units_per_epoch'][kind]
        diagnostic=sample['diagnostic_timing'][kind]; refresh=sample['refresh_pass'][kind]['wall_seconds']
        parity=sample['parity_timing'][kind]['projected_seconds']
        train=epochs*budget['steps_per_epoch']*step_wall
        diag=(epochs+1)*diagnostic['validation']+diagnostic['test']+diagnostic.get('law',0)
        old=epochs*units*proxy+epochs*refresh+diag+parity
        seeds=3 if kind=='N1' else 1
        old_total+=seeds*old
        arms[kind]=dict(training_seconds=train,refresh_seconds=epochs*refresh,diagnostics_seconds=diag,
                        export_parity_seconds=parity,total_seconds=train+epochs*refresh+diag+parity,
                        seconds_per_step=step_wall,warm_up=dict(sample_index=0,measurement=stats[0],excluded=True),
                        included_sample_indices=list(range(1,len(stats))),seconds_per_work_unit=proxy,
                        old_proxy_training_seconds=epochs*units*proxy,old_proxy_total_seconds=old,seeds=seeds)
    for kind,seed,name in FITS:
        done=completed.get(name,0)
        if not 0<=done<=epochs:
            raise ValueError('completed epoch outside budget')
        remaining=epochs-done; p=arms[kind]; d=sample['diagnostic_timing'][kind]
        # Each fresh worker verifies data and loads its own prepared-state cache.
        fit_costs[name]=(remaining*(budget['steps_per_epoch']*p['seconds_per_step']+
                        sample['refresh_pass'][kind]['wall_seconds']+d['validation'])+
                        d['validation']+d['test']+d.get('law',0)+sample['preprocessing_seconds'])
        if name in sealed_arms:
            fit_costs[name]=0.
        if not sealed_parity:
            parity_total+=p['export_parity_seconds']
    groups=lanes(fit_costs,topology['slots'])
    wall=sample['preprocessing_seconds']+max(g['wall_seconds'] for g in groups)+parity_total
    return dict(total_projected_seconds=wall,total_projected_minutes=wall/60,per_arm=arms,
                per_fit_seconds=fit_costs,concurrent_groups=groups,topology=topology,
                sequential_parity_seconds=parity_total,
                old_proxy_sequential_seconds=old_total,old_proxy_sequential_minutes=old_total/60,
                method='maximum step wall after declared first-step warm-up; measured refresh/diagnostics; '
                       'max of sequential lane sums on measured performance cores; sequential measured parity tail; '
                       'worker preparation allowance; contention is unmeasured')


def atomic_checkpoint(path,value):
    import torch
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=path.name+'.',suffix='.partial',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:
            torch.save(value,f); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
        fd=os.open(path.parent,os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def last_checkpoint(directory,budget_hash):
    import torch
    directory=Path(directory); files=sorted(directory.glob('epoch_*.pt'))
    if not files:
        return None
    for epoch,path in enumerate(files,1):
        if path.name!=f'epoch_{epoch:04}.pt':
            raise RuntimeError('checkpoint epoch gap; preserve and inspect')
    value=torch.load(files[-1],weights_only=False)
    if value['budget_sha256']!=budget_hash or value['epoch']!=len(files):
        raise RuntimeError('checkpoint budget/epoch mismatch')
    return value


def validate_resume(budget,current_sources,index_hash,epochs):
    if budget['sources']!=current_sources or budget['dataset_index_sha256']!=index_hash:
        raise RuntimeError('resume source/data identity drift; do not reuse timings or checkpoints')
    if epochs is not None and epochs!=budget['epochs']:
        raise RuntimeError('resume cannot change the matched epoch budget')
