"""Focused Stage-1 tests. No physical fights, entropy allocation or fits."""
import copy
import json
from pathlib import Path
import numpy as np
import pytest
import torch
from collection import HERE,ROOT,read,sha
from stage1_data import admit,frame_rows,decision,convert_fight,HEADS
from stage1_runtime import n2_tick,Replay
from models import Policy,assert_imitation_optimizer
from dynamics import graph
from schema import encode,slots
from labels import join
from stage1_export import rpc,compare


@pytest.fixture(scope='module')
def records():
    inv=admit(); row=next(r for r in inv['rows'] if r['split']=='test' and r['guns']==2 and r['cell']=='D2-shellfire')
    frames=[]
    for frame in frame_rows(ROOT/(row['group']+'.jsonl')):
        if len(frames)==7:
            break
        frames.append(frame)
    return row,frames


def test_streaming_converter_schema_masks_and_native_parity(records,tmp_path):
    row,frames=records; source=tmp_path/'input.jsonl'
    source.write_text(''.join(json.dumps(f)+'\n' for f in frames)+json.dumps(dict(terminal=True,cell=row['cell']))+'\n')
    out=tmp_path/'arrays'; meta=convert_fight(row,source,7,out)
    assert meta['counts']['decision_rows']==4 and meta['ids']==frames[0]['gun_ids']
    x=np.load(out/'x.npy',mmap_mode='r'); labels=np.load(out/'labels.npy',mmap_mode='r'); masks=np.load(out/'masks.npy',mmap_mode='r')
    assert x.dtype==np.float32
    for tick in (1,7):
        f=frames[tick-1]
        for g,id in enumerate(f['gun_ids']):
            s={**f['joint'],'self':id}; native=rpc(dict(operation='encode',snapshot=s)); python,info=encode(s)
            assert native['features']==pytest.approx(python,abs=1e-12,rel=0)
            np.testing.assert_array_equal(x[(tick-1)//6,g],np.asarray(python,dtype=np.float32))
            action=next(e['value'] for e in f['events'] if e['unit']==id and e['stage']=='intent')
            lab,mask,_,_=decision(s,action)
            np.testing.assert_array_equal(labels[(tick-1)//6,g],lab)
            np.testing.assert_array_equal(masks[(tick-1)//6,g],mask)
    with pytest.raises(RuntimeError):
        convert_fight(row,source,7,out)


def test_teacher_repeat_consistency_on_heldout_decisions(records):
    _,frames=records
    for f in (frames[0],frames[6]):
        snapshots=[{**f['joint'],'self':i} for i in f['gun_ids']]
        a=rpc(dict(operation='teacher',snapshots=snapshots)); b=rpc(dict(operation='teacher',snapshots=snapshots))
        assert a==b
        for item in a['actions']:
            original=next(e['value'] for e in f['events'] if e['stage']=='intent' and e['unit']==item['id'])
            assert compare(item['action'],original)<=1e-9


@pytest.mark.parametrize('ab',['intact','K0','frozen_phase','topology_only','no_geometry_to_mode','no_mode_to_geometry','no_reset'])
def test_vectorized_joint_matches_contract_and_finite_gradients(records,ab):
    _,frames=records; f=frames[0]; ids=f['gun_ids']; snapshots=[{**f['joint'],'self':i} for i in ids]
    x=torch.tensor([encode(s)[0] for s in snapshots],dtype=torch.float64)
    pos=torch.tensor([[u[k] for k in ('x','y')] for i in ids for u in f['joint']['units'] if u['id']==i],dtype=torch.float64)
    th=torch.tensor([.1,.3],dtype=torch.float64,requires_grad=True)
    targets=[encode(s)[1]['enemy_ids']+[0]*(12-len(encode(s)[1]['enemy_ids'])) for s in snapshots]
    assigns=[targets[0][0],targets[1][0]]; m=Policy('N2'); held=torch.tanh(m.force(x)).squeeze(-1) if ab=='no_geometry_to_mode' else None
    expected,phase,_=m.joint(x,pos,ids,th,targets,assignments=assigns,ablation=ab,fixed=graph(pos,ids),held_force=held)
    actual,phase2=n2_tick(m,x,pos,ids,th,targets,assigns,1/30,ab,graph(pos,ids),held)
    assert torch.allclose(actual,expected,atol=1e-12,rtol=1e-12)
    assert torch.allclose(phase,phase2,atol=1e-12,rtol=1e-12)
    actual.square().mean().backward()
    assert torch.isfinite(th.grad).all()
    if ab!='frozen_phase':
        assert m.force.weight.grad.abs().sum()>0
    if m.law.grad is not None:
        assert (m.law.grad[[0,1,2,5]]==0).all()


@pytest.mark.parametrize('kind',['N1','N1r','N2'])
def test_heldout_native_full_sequence_with_launch_and_death(records,kind):
    _,frames=records; extended=[]; launches=[]
    for t in range(18):
        f=copy.deepcopy(frames[t%len(frames)])
        snapshots=[{**f['joint'],'self':id,'tick':t+1,'t':(t+1)/30} for id in f['gun_ids']]
        if t>=12:
            snapshots=snapshots[:1]
            for s in snapshots:
                s['units']=[u for u in s['units'] if u['id']!=f['gun_ids'][1]]
        extended.append(snapshots); launches.append([f['gun_ids'][0]] if t==5 else [])
    from models import export
    model=Policy(kind); weights={'version':'NS1','kind':kind,'dtype':'float64','parameters':{k:dict(shape=list(v.shape),values=v.detach().reshape(-1).tolist()) for k,v in model.state_dict().items()}}
    native=rpc(dict(operation='stage1_sequence',weights=weights,frames=extended,launches=launches,ablation='intact'))
    with torch.no_grad():
        expected=Replay(model).deployment(extended,launches)
    compare(native,expected)


def test_no_sample_or_physical_execution_on_import_and_sealed_splits():
    from stage1_dagger import CELLS
    from stage1_mechanism import ARMS
    assert len(CELLS)==10 and len(ARMS)==10
    rows=admit()['rows']
    assert len(rows)==200 and sum(r['split']=='report' for r in rows)==20
    assert not (HERE/'_local/stage1/jobs/dagger_r1/INVENTORY.json').exists()
    assert not (HERE/'_local/stage1/jobs/mechanism/INVENTORY.json').exists()


def test_dagger_inventory_balanced_and_excluded(monkeypatch):
    import stage1_dagger as d
    monkeypatch.setattr(d,'pins',lambda weights:{'fixture':True})
    inv=d.inventory(1,'fixture-entropy',dict(N1='n1',N1r='n1r',N2='n2'),[12345])
    assert len(inv['rows'])==30
    for arm in d.ARMS:
        rows=[r for r in inv['rows'] if r['visitor']==arm]
        assert len(rows)==10 and all(r['request']['shadow'] for r in rows)
        assert sum(r['guns']==1 and r['cell']=='D1-static' for r in rows)==2
        assert sum(r['guns']==1 and r['cell']=='D2-shellfire' for r in rows)==2
        assert all(r['request']['seed']>9999 and r['request']['seed']!=12345 for r in rows)
    for i in range(0,30,3):
        assert len({r['request']['seed'] for r in inv['rows'][i:i+3]})==1


def test_mechanism_inventory_pairing_and_no_outcome_reading(monkeypatch):
    import stage1_mechanism as m
    monkeypatch.setattr(m,'pins',lambda weights:{'fixture':True})
    value=m.inventory('fixture-entropy',12,dict(N1='n1',N1r='n1r',N2='n2'),[])
    assert len(value['rows'])==120
    for i in range(0,120,10):
        rows=value['rows'][i:i+10]
        assert len({r['draw'] for r in rows})==1 and len({r['request']['seed'] for r in rows})==1
        assert rows[-1]['request']['ablation']=='no_reset'
    with pytest.raises(ValueError):
        m.inventory('fixture',9,{},[])


def test_optimizer_and_no_detached_joint_gradient(records):
    _,frames=records; model=Policy('N2'); replay=Replay(model)
    ids=frames[0]['gun_ids']; f=frames[0]; snapshots=[{**f['joint'],'self':i} for i in ids]
    x=torch.tensor([encode(s)[0] for s in snapshots],dtype=torch.float64)
    pos=torch.tensor([[u[k] for k in ('x','y')] for i in ids for u in f['joint']['units'] if u['id']==i],dtype=torch.float64)
    targets=[[3,4]+[0]*10 for _ in ids]
    with torch.no_grad():
        replay.tick(ids,x,pos,targets,[0,0],1/30,True)
    replay.detach()
    y=replay.tick(ids,x,pos,targets,[3,4],1/30,False)
    y[0].square().sum().backward()
    assert torch.isfinite(model.force.weight.grad).all() and model.force.weight.grad.abs().sum()>0
    optimizer=torch.optim.Adam(model.parameters(),weight_decay=.01)
    with pytest.raises(ValueError):
        assert_imitation_optimizer(model,optimizer)


def test_global_weighting_survives_single_stratum_batches(monkeypatch):
    import stage1_train as tr
    model=Policy('N1')
    def fake_window(m,g,s,e):
        n=1 if g=='small' else 3
        logits=m.readout.bias[None,:].expand(n,-1)
        labs=np.zeros((n,5),dtype=np.int64); labs[:,1]=1 if g=='small' else 2
        masks=np.zeros((n,5),dtype=bool); masks[:,1]=True
        return logits,labs,masks,np.ones((n,79),dtype=bool)
    monkeypatch.setattr(tr,'window',fake_window)
    monkeypatch.setattr(tr,'ROW_WEIGHTS',{'small':.5,'large':1/6})
    monkeypatch.setattr(tr,'HEAD_MASS',{'target':1.})
    monkeypatch.setattr(tr,'STEPS_PER_EPOCH',1)
    small=tr.batch(model,[('small',0,1)],(1,1))[0]
    large=tr.batch(model,[('large',0,1)],(1,1))[0]
    joint=tr.batch(model,[('small',0,1),('large',0,1)],(1,1))[0]
    torch.testing.assert_close(small+large,joint)
    first=torch.autograd.grad(small+large,model.readout.bias,retain_graph=True)[0]
    second=torch.autograd.grad(joint,model.readout.bias)[0]
    torch.testing.assert_close(first,second)


@pytest.mark.parametrize('a,b',[(float('nan'),0.),(0.,float('nan')),(float('inf'),float('inf')),(True,1.)])
def test_nonfinite_parity_cannot_pass(a,b):
    with pytest.raises(AssertionError):
        compare(a,b)


def test_sparse_near_canceling_phase_group_uses_subgroup_mean():
    import math
    model=Policy('N2'); ids=[1,2,3,4,5]
    x=torch.zeros((5,1008),dtype=torch.float64); pos=torch.tensor([[0.,i*10.] for i in ids],dtype=torch.float64)
    theta=torch.tensor([.2,0.,math.pi-2.2e-6,.5,.8],dtype=torch.float64)
    candidates=[[123]+[0]*11 for _ in ids]; assignments=[0,123,123,0,0]
    expected,phase,_=model.joint(x,pos,ids,theta,candidates,assignments=assignments,ablation='frozen_phase')
    actual,phase2=n2_tick(model,x,pos,ids,theta,candidates,assignments,1/30,'frozen_phase')
    torch.testing.assert_close(actual,expected,atol=1e-12,rtol=1e-12)


def test_vector_recurrent_message_matches_native_contract_with_sparse_groups():
    from stage1_runtime import n1r_message
    from models import recurrent_message
    ids=[1,2,3,4,5]; pos=torch.tensor([[0.,i*10] for i in ids],dtype=torch.float64)
    memory=torch.tensor([[.1*i]*(8) for i in ids],dtype=torch.float64,requires_grad=True)
    targets=[[123,345]+[0]*10 for _ in ids]; assignments=[0,123,123,345,0]
    fast=n1r_message(memory,pos,ids,assignments,targets)
    reference=recurrent_message(memory,pos,ids,assignments,targets)
    torch.testing.assert_close(fast,reference,atol=1e-12,rtol=1e-12)
    fast.sum().backward(); assert torch.isfinite(memory.grad).all()


def test_n2_neighbor_leaf_phase_gradient_remains_attached():
    model=Policy('N2'); ids=[1,2]
    x=torch.zeros((2,1008),dtype=torch.float64)
    pos=torch.tensor([[0.,0.],[30.,0.]],dtype=torch.float64)
    theta=torch.tensor([.1,.4],dtype=torch.float64,requires_grad=True)
    y,phase=n2_tick(model,x,pos,ids,theta,[[3]+[0]*11]*2,[3,3],1/30)
    neighbor=torch.autograd.grad(phase[0],theta)[0][1]
    assert neighbor.abs()>1e-6 and torch.isfinite(neighbor)


def test_exact_native_impact_metrics_keep_late_and_identical_shells(tmp_path):
    from stage1_metrics import metrics
    impacts=[]
    for source,damage in ((1,10),(2,12)):
        impacts.append(dict(unit=source,stage='shell_impact',value=dict(source_team=0,born=0.,landing_at=1.,aim=[650,400],radius=40,
                       hits=[dict(id=3,team=1,gun=True,damage=damage,killed=False)],living_targets=[])))
    frames=[dict(tick=1,joint=None,gun_ids=[],events=impacts,phase_state=[]),
            dict(terminal=True,own_guns_alive=0,enemy_alive=1,time=2,
                 native_shell_totals=dict(enemy_damage=22,friendly_damage=0,enemy_kills=0,resolved_shells=2))]
    path=tmp_path/'late.jsonl'; path.write_text(''.join(json.dumps(f)+'\n' for f in frames))
    result=metrics(path,dict(draw='fixture',arm='N2',guns=2,cell='D2-shellfire',orientation=0))
    assert result['enemy_damage']==22 and result['counts']['own_shell_arrivals']==2
    assert result['counts']['own_shell_target_censored']==2


def test_sealed_range_boundary_uses_native_hypot_without_epsilon():
    from stage1_arithmetic import encode as native_encode,opportunities as native_opportunities
    from stage1_arithmetic import native_hypot
    group='NS1-d208feef747b50163038e32b682618fe'
    for frame in frame_rows(ROOT/(group+'.jsonl')):
        if frame.get('tick')==361:
            break
    s={**frame['joint'],'self':5}; action=next(e['value'] for e in frame['events'] if e['stage']=='intent' and e['unit']==5)
    me=next(u for u in s['units'] if u['id']==5); target=next(u for u in s['units'] if u['id']==23)
    assert native_hypot(target['x']-me['x'],target['y']-me['y'])==320.
    assert action['start'] and native_opportunities(s,target,action['aim'])[0]
    labels,masks,legal,_=decision(s,action)
    assert masks[2] and legal[46] and labels[2]==1
    native=rpc(dict(operation='encode',snapshot=s))
    assert native['features']==pytest.approx(native_encode(s)[0],abs=1e-12,rel=0)
    outside=copy.deepcopy(s)
    next(u for u in outside['units'] if u['id']==23)['x']+=1e-8
    bad={**action,'aim':[900+1e-8,360]}
    with pytest.raises(ValueError,match='permission without'):
        decision(outside,bad)
    # Pinned ancestors/global Python math retain their original arithmetic.
    import math
    assert math.hypot(target['x']-me['x'],target['y']-me['y'])>320


def test_pre_adapter_mmaps_cannot_be_reused():
    from stage1_data import validate_arithmetic
    from stage1_arithmetic import identity
    with pytest.raises(RuntimeError,match='arithmetic'):
        validate_arithmetic({})
    with pytest.raises(RuntimeError,match='arithmetic'):
        validate_arithmetic(dict(arithmetic=identity(),arithmetic_source_sha256='stale'))
    validate_arithmetic(dict(arithmetic=identity(),arithmetic_source_sha256=sha(HERE/'stage1_arithmetic.py')))


def test_empty_world_tail_windows_preserve_last_live_decision(tmp_path,monkeypatch):
    import stage1_train as tr
    target=tmp_path/'world'; target.mkdir()
    alive=np.zeros((1959,2),dtype=bool); alive[:541,0]=True
    np.save(target/'alive.npy',alive); monkeypatch.setattr(tr,'DATA',tmp_path)
    meta=dict(group='world',split='train',ticks=1959,counts={'decision_rows':91})
    windows=tr.windows([meta])
    assert windows[-1]==('world',540,630) and len(windows)==7
    assert sum(int(alive[s:e:6].sum()) for _,s,e in windows)==91
    assert len(tr.schedule([meta]))==2
    with pytest.raises(RuntimeError,match='lost or duplicated'):
        tr.windows([{**meta,'counts':{'decision_rows':92}}])


def test_all_empty_training_split_is_refused(tmp_path,monkeypatch):
    import stage1_train as tr
    target=tmp_path/'empty'; target.mkdir(); np.save(target/'alive.npy',np.zeros((90,1),dtype=bool))
    monkeypatch.setattr(tr,'DATA',tmp_path)
    with pytest.raises(ValueError,match='no supervised'):
        tr.schedule([dict(group='empty',split='train',ticks=90,counts={'decision_rows':0})])


@pytest.mark.parametrize('historical,live_cap,deadline,expected',[
    (0,50,90,10),
    (60,100,150,10),
])
def test_physical_wait_rechecks_remaining_child_time(tmp_path,monkeypatch,historical,live_cap,deadline,expected):
    import stage1_jobs as jobs
    clock=[50.]; observed=[]
    monkeypatch.setattr(jobs.time,'monotonic',lambda:clock[0])
    monkeypatch.setattr(jobs,'cap',lambda:{'cap_seconds':live_cap})
    monkeypatch.setattr(jobs,'clear',lambda *a:clock.__setitem__(0,80.))
    def native(request,output,stderr,seconds):
        observed.append(seconds); output.write_text('fixture\n'); stderr.write_text('')
        return dict(exit_code=0,timed_out=False,wall_seconds=1,cpu_seconds=1,rss_bytes=1)
    monkeypatch.setattr(jobs.collection,'native',native)
    monkeypatch.setattr(jobs.collection,'measurements',lambda *a:dict(decision_count=1,record_count=1,terminal={}))
    directory=tmp_path/'wait'; directory.mkdir()
    if historical:
        (directory/'attempts').mkdir()
        (directory/'attempts/001.json').write_text(json.dumps(dict(status='FAILED',resources=dict(wall_seconds=historical))))
    row=dict(fight='fixture',request=dict(fight='fixture'))
    jobs.execute(directory,row,'seal',tmp_path/'unused-binary',30,deadline)
    assert observed==[float(expected)]


@pytest.mark.parametrize('live_after_wait,expected',[(100,10),(95,5)])
def test_physical_resumed_budget_spans_children_and_live_reductions(tmp_path,monkeypatch,live_after_wait,expected):
    import stage1_jobs as jobs
    clock=[50.]; live=[100.]; observed=[]
    monkeypatch.setattr(jobs.time,'monotonic',lambda:clock[0])
    monkeypatch.setattr(jobs,'cap',lambda:{'cap_seconds':live[0]})
    def clear(*args):
        clock[0]=80.; live[0]=live_after_wait
    monkeypatch.setattr(jobs,'clear',clear)
    def native(request,output,stderr,seconds):
        observed.append(seconds); clock[0]+=seconds
        output.write_text('fixture\n'); stderr.write_text('')
        return dict(exit_code=0,timed_out=False,wall_seconds=seconds,cpu_seconds=1,rss_bytes=1)
    monkeypatch.setattr(jobs.collection,'native',native)
    monkeypatch.setattr(jobs.collection,'measurements',lambda *a:dict(decision_count=1,record_count=1,terminal={}))
    directory=tmp_path/'resume'; (directory/'attempts').mkdir(parents=True)
    (directory/'attempts/001.json').write_text(json.dumps(dict(status='FAILED',resources=dict(wall_seconds=60))))
    budget=jobs.physical_budget(directory)
    jobs.execute(directory,dict(fight='first',request=dict(fight='first')),'seal','binary',30,budget)
    assert observed==[float(expected)]
    monkeypatch.setattr(jobs,'clear',lambda *a:pytest.fail('exhausted invocation must not wait or relaunch'))
    with pytest.raises(TimeoutError,match='exhausted'):
        jobs.execute(directory,dict(fight='second',request=dict(fight='second')),'seal','binary',30,budget)
    assert observed==[float(expected)]


@pytest.mark.parametrize('state',['RUNNING','NATIVE_DONE'])
def test_physical_unresolved_attempt_never_relaunches(tmp_path,monkeypatch,state):
    import stage1_jobs as jobs
    directory=tmp_path/'job'; (directory/'attempts').mkdir(parents=True)
    (directory/'attempts/001.json').write_text(json.dumps(dict(status=state,request=dict(fight='old'),resources=dict(wall_seconds=1))))
    monkeypatch.setattr(jobs,'completed',lambda *a:None)
    monkeypatch.setattr(jobs,'clear',lambda *a:pytest.fail('must refuse before gate/native'))
    with pytest.raises(RuntimeError,match='unresolved'):
        jobs.execute(directory,dict(fight='new',request={}), 'seal','binary',30,1000000000)
