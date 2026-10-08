"""Host-only isolated arm workers; parent owns one gate for the whole job."""
import argparse
from collections import Counter
import copy
import fcntl
import json
import math
import os
from pathlib import Path
import random
import signal
import subprocess
import sys
import time
import numpy as np
import torch
from stage1_training_control import FITS,atomic_checkpoint,last_checkpoint,validate_resume,TrainingDeadline


def setup(tr,budget,aggregate,out):
    tr.environment()
    validate_resume(budget,tr.sources(),tr.sha(aggregate or tr.DATA/'INDEX.json'),budget['epochs'])
    fights=tr.index(aggregate)
    tr.OUT=out
    tr.ROW_WEIGHTS={m['group']:m.get('row_weight',1.) for m in fights}
    tr.HEAD_MASS={k:sum(m['counts'].get(k+'_active',0)*tr.ROW_WEIGHTS[m['group']] for m in fights if m['split']=='train') for k in tr.HEADS}
    tr.STEPS_PER_EPOCH=budget['steps_per_epoch']
    return fights


def fit(tr,kind,seed,name,budget_path,aggregate,out,deadline):
    start=time.monotonic(); cpu_start=time.process_time()
    budget=tr.read(budget_path); digest=tr.sha(budget_path)
    fights=setup(tr,budget,aggregate,out); directory=out/'epochs'/name
    state=last_checkpoint(directory,digest)
    model,optimizer=tr.make(kind,seed)
    if state is None:
        state=dict(epoch=0,best=math.inf,best_epoch=None,best_model=None,history=[],rows_seen=0,
                   resources={},wall_seconds=0.,cpu_seconds=0.,steps=[])
    else:
        if state['kind']!=kind or state['seed']!=seed:
            raise RuntimeError('checkpoint arm/seed mismatch')
        model.load_state_dict(state['model']); optimizer.load_state_dict(state['optimizer'])
        random.setstate(state['python_rng']); np.random.set_state(state['numpy_rng']); torch.set_rng_state(state['torch_rng'])
    prior_wall=state['wall_seconds']; prior_cpu=state['cpu_seconds']; resources=Counter(state['resources'])
    weights=budget['training_only_fire_class_weights']; modes=budget['majority_modes']
    for epoch in range(state['epoch'],budget['epochs']):
        validate_resume(budget,tr.sources(),tr.sha(aggregate or tr.DATA/'INDEX.json'),budget['epochs'])
        tr.STORED=tr.StoredStates() if kind!='N1' else None
        if tr.STORED:
            cpu=time.process_time(); seconds=tr.STORED.refresh(model,tr.windows(fights),tr.prepare,deadline)
            resources['refresh_wall_seconds']+=seconds; resources['refresh_cpu_seconds']+=time.process_time()-cpu
        # Only the checkpoint's log counts. Unfinished epoch work is never committed.
        for step_id,rows in enumerate(tr.schedule(fights,epoch)):
            if time.monotonic()>=deadline:
                raise TimeoutError('training cap; last completed epoch preserved')
            measured=tr.step(model,optimizer,rows,weights)
            state['rows_seen']+=measured['decision_rows']
            state['steps'].append(dict(epoch=epoch+1,step=step_id,windows=rows,**measured))
            resources['peak_rss_bytes']=max(resources['peak_rss_bytes'],measured['rss_bytes'])
            for key in ('wall_seconds','cpu_seconds','phase_rhs_evaluations'):
                resources[key]+=measured[key]
        tr.STORED=None
        diagnostic=tr.evaluate(model,fights,'validation',weights,modes,deadline)
        value=diagnostic['weighted_masked_loss']
        if not math.isfinite(value):
            raise FloatingPointError('nonfinite validation objective')
        state['history'].append(dict(epoch=epoch+1,validation=value))
        if value<state['best']:
            state.update(best=value,best_epoch=epoch+1,best_model=copy.deepcopy(model.state_dict()))
        state.update(epoch=epoch+1,kind=kind,seed=seed,budget_sha256=digest,
                     model=model.state_dict(),optimizer=optimizer.state_dict(),
                     python_rng=random.getstate(),numpy_rng=np.random.get_state(),torch_rng=torch.get_rng_state(),
                     resources=dict(resources),wall_seconds=prior_wall+time.monotonic()-start,
                     cpu_seconds=prior_cpu+time.process_time()-cpu_start)
        expected=(epoch+1)*budget['decision_rows_per_epoch']
        if state['rows_seen']!=expected:
            raise RuntimeError('unequal epoch decision-row budget')
        atomic_checkpoint(directory/f'epoch_{epoch+1:04}.pt',state)
        print(name,'epoch',epoch+1,'validation',value,flush=True)
    if state['rows_seen']!=budget['decision_rows_per_arm']:
        raise RuntimeError('unequal decision-row budget')
    # Best weights and final diagnostics can be rebuilt after interrupted finalization.
    model.load_state_dict(state['best_model'])
    atomic_checkpoint(out/(name+'.pt'),dict(kind=kind,model=state['best_model'],epoch=state['best_epoch'],seed=seed,budget=budget))
    tr.export(model,out/(name+'.weights.json'))
    test=tr.evaluate(model,fights,'test',weights,modes,deadline)
    validation=tr.evaluate(model,fights,'validation',weights,modes,deadline)
    law=tr.law_statistics(model,fights,deadline)
    validate_resume(budget,tr.sources(),tr.sha(aggregate or tr.DATA/'INDEX.json'),budget['epochs'])
    # Reconstruct the sole authoritative step ledger from completed checkpoints.
    log=out/(name+'.steps.jsonl'); temporary=log.with_suffix('.jsonl.tmp')
    with temporary.open('w') as f:
        for entry in state['steps']:
            f.write(json.dumps(entry,allow_nan=False)+'\n')
        f.flush(); os.fsync(f.fileno())
    os.replace(temporary,log)
    outcome=dict(kind=kind,seed=seed,checkpoint_epoch=state['best_epoch'],history=state['history'],
                 gradient_steps=budget['gradient_steps_per_arm'],decision_rows=state['rows_seen'],
                 resources=dict(resources),learned_law=law,test=test,validation=validation,
                 wall_seconds=prior_wall+time.monotonic()-start,cpu_seconds=prior_cpu+time.process_time()-cpu_start,
                 resource_scope='completed checkpoint invocations plus current preparation/finalization; interrupted uncheckpointed work excluded',
                 invocation_process_cpu_seconds=time.process_time(),
                 checkpoint_sha256=tr.sha(out/(name+'.pt')),export_sha256=tr.sha(out/(name+'.weights.json')),
                 budget_sha256=digest,steps_sha256=tr.sha(log))
    tr.atomic(out/(name+'.outcome.json'),outcome)
    return outcome


def completed_outcome(tr,out,name,budget_hash):
    path=out/(name+'.outcome.json')
    if not path.exists():
        return None
    value=tr.read(path)
    if (value['budget_sha256']!=budget_hash or value['checkpoint_sha256']!=tr.sha(out/(name+'.pt')) or
        value['export_sha256']!=tr.sha(out/(name+'.weights.json')) or value['steps_sha256']!=tr.sha(out/(name+'.steps.jsonl'))):
        raise RuntimeError('completed arm outcome drift')
    return value


def execute(tr,budget_path,aggregate,out,projection,deadline):
    from stage1_jobs import ACTIVE_LOCK_FDS
    if len(ACTIVE_LOCK_FDS)!=2:
        raise RuntimeError('whole-job repository locks required before launching arm workers')
    budget_hash=tr.sha(budget_path); queues=[list(g['arms']) for g in projection['concurrent_groups']]
    live={}; handles=[]; outcomes={}; fits={n:(k,s) for k,s,n in FITS}
    def interrupted(signum,frame):
        raise KeyboardInterrupt('training coordinator interrupted')
    old=signal.signal(signal.SIGTERM,interrupted)
    try:
        while any(queues) or live:
            if time.monotonic()>=deadline:
                raise TimeoutError('whole training job cap exhausted')
            for lane,queue in enumerate(queues):
                if lane in live or not queue:
                    continue
                name=queue.pop(0)
                done=completed_outcome(tr,out,name,budget_hash)
                if done:
                    outcomes[name]=done; continue
                kind,seed=fits[name]
                log=(out/(name+'.worker.log')).open('a'); handles.append(log)
                command=[sys.executable,str(Path(__file__).resolve()),'--arm',name,'--budget',str(budget_path),
                         '--out',str(out),'--deadline',str(deadline),'--admitted-cap',str(deadline.admitted_cap),'--gate-fds',*(str(fd) for fd in ACTIVE_LOCK_FDS)]
                if aggregate:
                    command+=['--aggregate',str(aggregate)]
                env={**os.environ,'OMP_NUM_THREADS':'2','MKL_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2'}
                child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,pass_fds=ACTIVE_LOCK_FDS,
                                       env=env,start_new_session=True)
                live[lane]=(child,name,time.monotonic())
            for lane,(child,name,started) in list(live.items()):
                if child.poll() is None:
                    continue
                if child.returncode:
                    raise RuntimeError(f'{name} worker exited {child.returncode}; inspect its log and resume')
                outcomes[name]=completed_outcome(tr,out,name,budget_hash)
                if outcomes[name] is None:
                    raise RuntimeError('successful worker without sealed outcome')
                outcomes[name]['coordinator_observed_invocation_wall_seconds']=time.monotonic()-started
                tr.atomic(out/(name+'.outcome.json'),outcomes[name])
                print(name,'completed',round(time.monotonic()-started,2),'s',flush=True)
                del live[lane]
            if live:
                time.sleep(.2)
    finally:
        # Include native parity descendants if future workers use them.
        for child,name,started in live.values():
            try:
                os.killpg(child.pid,signal.SIGTERM)
            except ProcessLookupError:
                pass
        for child,name,started in live.values():
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid,signal.SIGKILL); child.wait()
        for handle in handles:
            handle.close()
        signal.signal(signal.SIGTERM,old)
    return outcomes


def verify_inherited_locks(tr,fds):
    from stage1_jobs import JOBS
    for fd,path in zip(fds,(JOBS/'SLICE_JOB.lock',tr.HERE/'_local/collection/RUN.lock')):
        st=os.fstat(fd); target=path.stat()
        if (st.st_dev,st.st_ino)!=(target.st_dev,target.st_ino):
            raise RuntimeError('worker repository lock identity mismatch')
        fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--arm',choices=[n for k,s,n in FITS],required=True)
    p.add_argument('--budget',type=Path,required=True); p.add_argument('--aggregate',type=Path)
    p.add_argument('--out',type=Path,required=True); p.add_argument('--deadline',type=float,required=True)
    p.add_argument('--admitted-cap',type=float,required=True)
    p.add_argument('--gate-fds',type=int,nargs=2,required=True); a=p.parse_args()
    import stage1_train as tr
    verify_inherited_locks(tr,a.gate_fds); os.nice(10)
    kind,seed=next((k,s) for k,s,n in FITS if n==a.arm)
    fit(tr,kind,seed,a.arm,a.budget,a.aggregate,a.out,TrainingDeadline(tr.HERE,a.deadline,a.admitted_cap))
