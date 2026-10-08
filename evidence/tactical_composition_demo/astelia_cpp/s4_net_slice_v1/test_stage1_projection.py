"""Projection and crash/resume fixtures only: no real optimizer steps or fights."""
from collections import Counter
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
import torch
from stage1_training_control import (FITS,TrainingDeadline,training_cap,measured_cores,lanes,project,
                                     atomic_checkpoint,last_checkpoint,validate_resume)


def sample():
    # Smallest sample is overhead dominated; proxy should remain comparison only.
    return dict(samples={k:[dict(wall_seconds=v,work_units=w,cpu_seconds=v*2)
                           for v,w in ((.8,3000),(.9,28716),(1.,61500))] for k in ('N1','N1r','N2')},
                refresh_pass={k:dict(wall_seconds=100) for k in ('N1','N1r','N2')},
                diagnostic_timing={k:dict(validation=2,test=3) for k in ('N1','N1r','N2')},
                parity_timing={k:dict(projected_seconds=10) for k in ('N1','N1r','N2')},
                preprocessing_seconds=5)


def budget(epochs=10):
    return dict(epochs=epochs,steps_per_epoch=516,work_units_per_epoch={k:1e7 for k in ('N1','N1r','N2')})


def test_projection_uses_step_walls_keeps_proxy_and_sequential_parity():
    p=project(sample(),budget(),dict(slots=5))
    assert p['per_arm']['N2']['training_seconds']==5160
    assert p['per_arm']['N2']['old_proxy_training_seconds']==pytest.approx(1e8*.8/3000)
    assert p['per_arm']['N2']['warm_up']['excluded']
    assert p['per_arm']['N2']['included_sample_indices']==[1,2]
    assert p['sequential_parity_seconds']==50
    assert p['total_projected_seconds']==5+max(g['wall_seconds'] for g in p['concurrent_groups'])+50
    assert p['old_proxy_sequential_seconds']>p['total_projected_seconds']
    assert sorted(n for g in p['concurrent_groups'] for n in g['arms'])==sorted(n for k,s,n in FITS)


def test_epoch_reduction_and_resume_remain_matched():
    p=project(sample(),budget(3),dict(slots=2))
    assert all(v['training_seconds']==3*516 for v in p['per_arm'].values())
    after=project(sample(),budget(3),dict(slots=2),{n:2 for k,s,n in FITS})
    assert after['total_projected_seconds']<p['total_projected_seconds']
    assert all(v['training_seconds']==3*516 for v in after['per_arm'].values())
    finalized=project(sample(),budget(3),dict(slots=2),{n:3 for k,s,n in FITS},
                      sealed_arms=[n for k,s,n in FITS],sealed_parity=True)
    assert all(v==0 for v in finalized['per_fit_seconds'].values())
    assert finalized['sequential_parity_seconds']==0
    assert finalized['total_projected_seconds']==sample()['preprocessing_seconds']
    with pytest.raises(ValueError):
        project(sample(),budget(3),dict(slots=2),{'N2':4})


def test_cap_missing_malformed_owner_and_live_reduction(tmp_path,monkeypatch):
    now=[1000.]
    monkeypatch.setattr('stage1_training_control.time.monotonic',lambda:now[0])
    assert training_cap(tmp_path)['cap_seconds']==3600
    path=tmp_path/'_local/TRAIN_CAP.json'; path.parent.mkdir()
    def write(seconds,owner='owner'):
        path.write_text(json.dumps(dict(cap_seconds=seconds,approved_by=owner,date='2026-10-08')))
    write(9000); deadline=TrainingDeadline(tmp_path,10000,9000)
    assert deadline-1000==9000 and not (9999>=deadline)
    assert min(deadline,11000) is deadline
    assert min(deadline,9000)==9000
    now[0]+=1.
    write(7000); assert 8000>=deadline and deadline-1000==7000
    now[0]+=1.
    write(12000); assert deadline-1000==7000  # increase never extends this invocation
    for seconds in (0,-1,True,float('inf')):
        write(seconds)
        with pytest.raises(ValueError):
            training_cap(tmp_path)
    write(9000,'Claude')
    with pytest.raises(ValueError):
        training_cap(tmp_path)


def test_topology_measures_both_sysctls_and_is_conservative(monkeypatch):
    calls=[]
    def probe(command,**kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=0,stdout='8' if command[-1].endswith('physicalcpu') else '12')
    monkeypatch.setattr('stage1_training_control.subprocess.run',probe)
    assert measured_cores()['slots']==4
    assert [c[-1] for c in calls]==['hw.perflevel0.physicalcpu','hw.ncpu']
    monkeypatch.setattr('stage1_training_control.subprocess.run',lambda *a,**k:SimpleNamespace(returncode=1,stdout=''))
    assert measured_cores()['slots']==1


def test_checkpoint_atomic_gap_identity_and_partial_file(tmp_path,monkeypatch):
    atomic_checkpoint(tmp_path/'epoch_0001.pt',dict(epoch=1,budget_sha256='budget',model={'x':torch.tensor(1.)}))
    (tmp_path/'epoch_0002.pt.partial').write_text('unfinished')
    assert last_checkpoint(tmp_path,'budget')['epoch']==1
    with pytest.raises(RuntimeError):
        last_checkpoint(tmp_path,'other')
    original=torch.save
    monkeypatch.setattr(torch,'save',lambda *a,**k:(_ for _ in ()).throw(OSError('disk full')))
    with pytest.raises(OSError):
        atomic_checkpoint(tmp_path/'epoch_0002.pt',dict(epoch=2))
    monkeypatch.setattr(torch,'save',original)
    assert last_checkpoint(tmp_path,'budget')['epoch']==1
    atomic_checkpoint(tmp_path/'epoch_0003.pt',dict(epoch=3,budget_sha256='budget'))
    with pytest.raises(RuntimeError,match='gap'):
        last_checkpoint(tmp_path,'budget')


def test_resume_pins_epochs_and_data():
    b=dict(sources={'hot':'one'},dataset_index_sha256='data',epochs=10)
    validate_resume(b,{'hot':'one'},'data',None)
    for sources,index,epochs in (({'hot':'two'},'data',10),({'hot':'one'},'other',10),({'hot':'one'},'data',5)):
        with pytest.raises(RuntimeError):
            validate_resume(b,sources,index,epochs)


def test_fit_kill_mid_epoch_restores_completed_optimizer_rng_and_best(tmp_path,monkeypatch):
    import stage1_training_worker as worker
    from collection import atomic,read,sha
    class Model:
        kind='N1'
        def __init__(self):
            self.x=torch.tensor(0.)
        def state_dict(self):
            return {'x':self.x.clone()}
        def load_state_dict(self,state):
            self.x=state['x'].clone()
    class Optimizer:
        def __init__(self):
            self.count=0
        def state_dict(self):
            return {'count':self.count}
        def load_state_dict(self,state):
            self.count=state['count']
    calls=[]; kill_at=[5]
    def fake_step(model,optimizer,rows,weights):
        calls.append(rows[0])
        if len(calls)==kill_at[0]:
            raise KeyboardInterrupt('fixture kill before completed third epoch')
        optimizer.count+=1
        model.x+=torch.rand(())  # fixture accounting; no real optimizer or training
        return dict(decision_rows=1,wall_seconds=.1,cpu_seconds=.2,phase_rhs_evaluations=0,rss_bytes=10)
    def make(kind,seed):
        torch.manual_seed(seed)
        return Model(),Optimizer()
    b=dict(epochs=3,steps_per_epoch=2,decision_rows_per_epoch=2,decision_rows_per_arm=6,gradient_steps_per_arm=6,
           training_only_fire_class_weights=[],majority_modes={},sources={},dataset_index_sha256='index')
    bp=tmp_path/'budget.json'; atomic(bp,b)
    tr=SimpleNamespace(read=read,sha=lambda p:'index' if Path(p).name=='INDEX.json' else sha(p),DATA=tmp_path,
                       sources=lambda:{},make=make,STORED=None,atomic=atomic,step=fake_step,
                       schedule=lambda fights,epoch:[[epoch*2],[epoch*2+1]],
                       evaluate=lambda *a,**k:dict(weighted_masked_loss=1.),law_statistics=lambda *a:None,
                       export=lambda model,p:atomic(p,{'x':float(model.x)}))
    monkeypatch.setattr(worker,'setup',lambda *a:[])
    out=tmp_path/'resumed'; out.mkdir()
    with pytest.raises(KeyboardInterrupt):
        worker.fit(tr,'N1',41001,'N1',bp,None,out,1e20)
    state=last_checkpoint(out/'epochs/N1',sha(bp))
    assert state['epoch']==2 and state['optimizer']['count']==4
    assert state['best_epoch']==1  # exact tie keeps earliest
    worker.fit(tr,'N1',41001,'N1',bp,None,out,1e20)
    final=last_checkpoint(out/'epochs/N1',sha(bp))
    assert calls==[0,1,2,3,4,4,5]  # only unfinished epoch retries
    assert final['rows_seen']==6 and final['optimizer']['count']==6
    kill_at[0]=999; calls.clear(); continuous=tmp_path/'continuous'; continuous.mkdir()
    worker.fit(tr,'N1',41001,'N1',bp,None,continuous,1e20)
    reference=last_checkpoint(continuous/'epochs/N1',sha(bp))
    torch.testing.assert_close(final['model']['x'],reference['model']['x'],atol=0,rtol=0)
    assert len((out/'N1.steps.jsonl').read_text().splitlines())==6
    calls.clear(); worker.fit(tr,'N1',41001,'N1',bp,None,out,1e20)
    assert not calls  # completed epochs are never repeated during finalization


def test_isolated_workers_share_parent_gate_and_obey_lanes(tmp_path,monkeypatch):
    import stage1_training_worker as worker
    import stage1_jobs
    import time
    launched=set(); calls=[]; stored={}
    monkeypatch.setattr(stage1_jobs,'ACTIVE_LOCK_FDS',(101,102))
    class Child:
        returncode=0
        def __init__(self,command,**options):
            name=command[command.index('--arm')+1]; launched.add(name)
            calls.append((name,command,options)); self.pid=999
        def poll(self):
            return 0
    monkeypatch.setattr(worker.subprocess,'Popen',Child)
    monkeypatch.setattr(worker,'completed_outcome',lambda tr,out,name,digest:dict(budget_sha256=digest) if name in launched else None)
    def save(path,value):
        stored[Path(path).name]=copy.deepcopy(value)
    tr=SimpleNamespace(sha=lambda path:'budget',atomic=save)
    projection=dict(concurrent_groups=[dict(arms=['N2','N1']),dict(arms=['N1r','N1_seed41101','N1_seed41201'])])
    deadline=TrainingDeadline(tmp_path,time.monotonic()+3600,3600)
    result=worker.execute(tr,tmp_path/'budget',None,tmp_path,projection,deadline)
    assert len(result)==5 and len(calls)==5
    assert [n for n,c,o in calls][:2]==['N2','N1r']
    for name,command,options in calls:
        assert options['pass_fds']==(101,102) and options['start_new_session']
        assert options['env']['OMP_NUM_THREADS']=='2'
        assert '--admitted-cap' in command and '--gate-fds' in command
        assert stored[name+'.outcome.json']['coordinator_observed_invocation_wall_seconds']>=0
    monkeypatch.setattr(stage1_jobs,'ACTIVE_LOCK_FDS',())
    with pytest.raises(RuntimeError,match='locks required'):
        worker.execute(tr,tmp_path/'budget',None,tmp_path,projection,deadline)


def test_worker_failure_cleans_live_process_groups(tmp_path,monkeypatch):
    import stage1_training_worker as worker
    import stage1_jobs
    import time
    monkeypatch.setattr(stage1_jobs,'ACTIVE_LOCK_FDS',(101,102))
    children=[]; killed=[]; waited=[]
    class Child:
        def __init__(self,command,**options):
            self.pid=100+len(children); children.append(self)
            self.returncode=1 if len(children)==1 else None
        def poll(self):
            return self.returncode
        def wait(self,timeout=None):
            waited.append(self.pid); self.returncode=-15
    monkeypatch.setattr(worker.subprocess,'Popen',Child)
    monkeypatch.setattr(worker.os,'killpg',lambda pid,sig:killed.append(pid))
    monkeypatch.setattr(worker,'completed_outcome',lambda *a:None)
    tr=SimpleNamespace(sha=lambda path:'budget',atomic=lambda *a:None)
    projection=dict(concurrent_groups=[dict(arms=['N2']),dict(arms=['N1r'])])
    with pytest.raises(RuntimeError,match='exited 1'):
        worker.execute(tr,tmp_path/'budget',None,tmp_path,projection,TrainingDeadline(tmp_path,time.monotonic()+3600,3600))
    assert killed==[100,101] and waited==[100,101]
