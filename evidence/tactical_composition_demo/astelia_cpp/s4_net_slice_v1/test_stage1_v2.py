"""Stage1 corrective fixtures; no fights, fitted optimizer steps or fresh entropy."""
import copy
import json
import math
import numpy as np
import pytest
import torch
from models import Policy
from stage1_runtime import Replay
from stage1_stored import PreparedFight,TensorReplay,StoredStates
from requests_v2 import drill
from stage1_uniqueness import gate,converted_hash,state_hash


def fixture():
    rng=np.random.default_rng(14); ticks=180; guns=3
    meta=dict(group='fixture',ids=[1,2,5],guns=guns,ticks=ticks,arrays={})
    alive=np.ones((ticks,guns),dtype=bool); alive[90:,1]=False; alive[110:,2]=False
    pos=np.zeros((ticks,guns,2)); pos[:,:,0]=np.arange(guns)*30
    pos[:,:,1]=np.arange(ticks)[:,None]*.1
    launch=np.zeros((ticks,guns),dtype=bool)
    launch[29,0]=True; launch[59,2]=True; launch[89,0]=True; launch[100,0]=True; launch[109,2]=True
    targets=np.zeros((ticks,guns,12),dtype='int64'); targets[:,:,:2]=[10,20]
    a=dict(x=rng.normal(0,.1,(30,guns,1008)).astype('float32'),pos=pos,alive=alive,launch=launch,
           targets=targets,assignments=np.full((ticks,guns),10,dtype='int64'),dt=np.full(ticks,1/30))
    return meta,a


@pytest.mark.parametrize('kind',['N1r','N2'])
def test_stored_burnin_full_prefix_exact_with_boundary_launch_and_deaths(kind):
    torch.manual_seed(111); model=Policy(kind); meta,a=fixture(); f=PreparedFight(meta,a)
    states=StoredStates(); states.refresh(model,[('fixture',0,90),('fixture',90,180)],lambda _:f)
    fast=states.start(model,f,90); full=Replay(model)
    with torch.no_grad():
        for t in range(90):
            f.tick(full,t)
        for t in range(90,180):
            y0=f.tick(full,t); y1=f.tick(fast,t)
            torch.testing.assert_close(y0,y1,atol=1e-9,rtol=0)
            gs=f.active[t]
            torch.testing.assert_close(torch.stack([full.phase[i] for i in f.ids[t]]),fast.phase[gs],atol=1e-9,rtol=0)
            torch.testing.assert_close(torch.stack([full.memory[i] for i in f.ids[t]]),fast.memory[gs],atol=1e-9,rtol=0)
            torch.testing.assert_close(torch.stack([full.held[i] for i in f.ids[t]]),fast.held[gs],atol=0,rtol=0)
    assert states.generation==1
    assert states.states['fixture',60]['fixed_ids']==meta['ids']
    assert not any(v.requires_grad for st in states.states.values() for v in st.values() if torch.is_tensor(v))
    assert fast.live==[1]


@pytest.mark.parametrize('kind',['N1r','N2'])
def test_tensor_replay_keeps_neighbors_and_bptt_gradients(kind):
    model=Policy(kind); meta,a=fixture(); f=PreparedFight(meta,a)
    state=StoredStates(); state.refresh(model,[('fixture',90,180)],lambda _:f)
    replay=state.start(model,f,90)
    ys=[f.tick(replay,t,emit=t%6==0) for t in range(90,108)]
    sum(y.square().mean() for y in ys if y is not None).backward()
    assert all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None)
    if kind=='N2':
        assert model.force.weight.grad.abs().sum()>0
        assert (model.law.grad[[0,1,2,5]]==0).all()


@pytest.mark.parametrize('cell',['D1-static','D2-shellfire'])
@pytest.mark.parametrize('guns',[1,2,10])
def test_versioned_draw_variation_is_seeded_bounded_and_paired(cell,guns):
    rows=[drill(cell,guns,20000+i,0,fight=str(i)) for i in range(20)]
    assert len({json.dumps(r['roster'],sort_keys=True) for r in rows})==20
    a=drill(cell,guns,20000,0,'N1','weights','a'); b=drill(cell,guns,20000,1,'N2','other','b')
    assert a['roster']==b['roster'] and a['variation']==b['variation']
    for row in rows:
        assert len(row['roster'])==2*guns+(4 if cell=='D1-static' else 2)
        assert all(0<u['position'][0]<1400 and 0<u['position'][1]<800 for u in row['roster'])
        assert row['variation']['version']=='NS1-drill-2'


def test_uniqueness_rejects_identity_only_changes(tmp_path):
    values=[]
    for i in range(12):
        path=tmp_path/f'{i}.jsonl'; path.write_text(json.dumps(dict(joint=dict(fight=str(i),seed=i,x=10)))+'\n')
        values.append(dict(cell='D1-static',guns=1,orientation=0,records=100,decision_rows=10,first_k_state_sha256=state_hash(path)))
    assert gate(values)['status']=='FAIL'
    for i,v in enumerate(values):
        v['first_k_state_sha256']=str(i)
    assert gate(values)['status']=='PASS'
    a={k:np.zeros((2,3)) for k in ('x','labels','pos','launch')}; b=copy.deepcopy(a)
    assert converted_hash(a)==converted_hash(b)
    b['launch'][1,1]=1
    assert converted_hash(a)!=converted_hash(b)


def test_v2_inventory_does_not_mutate_legacy_and_uses_all_strata(monkeypatch):
    import collection_v2 as c
    from collection import inventory as legacy
    monkeypatch.setitem(c.namespace,'legacy_seeds',lambda:set())
    inv=c.inventory('fixture-collection','fixture-report')
    assert inv['version']=='NS1-collection-2' and len(inv['rows'])==200
    assert all(r['request']['variation']['version']=='NS1-drill-2' for r in inv['rows'])
    assert 'variation' not in legacy('fixture-collection','fixture-report')['rows'][0]['request']
    assert c.ROOT.name=='collection_v2'


def test_fire_minority_class_weighting_and_repeat_refusal(tmp_path,monkeypatch):
    import stage1_train as tr
    logits=torch.zeros(2,dtype=torch.float64); truth=torch.tensor([0.,1.])
    weighted=tr.fire_loss(logits,truth,(10.,1.))
    assert weighted[0]==pytest.approx(10*weighted[1])
    monkeypatch.setattr(tr,'HERE',tmp_path)
    (tmp_path/'TRAINING_PROJECTION_03.json').write_text('{}')
    marker=tmp_path/'STAGE1_BUDGET_03.json'; marker.write_text('original')
    monkeypatch.setattr(tr,'environment',lambda:pytest.fail('must refuse before environment/sampling'))
    with pytest.raises(RuntimeError,match='already recorded'):
        tr.run()
    assert marker.read_text()=='original'


def test_dagger_training_covers_each_cell_gun_and_validation_rotation(monkeypatch):
    import stage1_dagger as d
    monkeypatch.setattr(d,'pins',lambda _: {})
    for round_id in (1,2):
        rows=d.inventory(round_id,'fixture',dict(N1='w1',N1r='wr',N2='w2'),[])['rows']
        train=[r for r in rows if r['split']=='train' and r['visitor']=='N1']
        assert {(r['cell'],r['guns']) for r in train}=={(c,g) for c in ('D1-static','D2-shellfire') for g in (1,2,10)}
        val=[r for r in rows if r['split']=='validation' and r['visitor']=='N1']
        assert {r['guns'] for r in val}=={1,2 if round_id==1 else 10}


def test_direct_mechanism_network_contrasts():
    from stage1_mechanism import report,ARMS
    rows=[]
    for arm in ARMS:
        rows.append(dict(draw='d',arm=arm,cell='D2-shellfire',guns=2,seconds=10,
            own_gun_deaths=0 if arm=='N2' else 1,enemy_kills=2 if arm=='N2' else 1,
            survival_loss_fraction=0 if arm=='N2' else .5,offense_kill_fraction=1 if arm=='N2' else .5,
            launch_opportunity_fraction=.5,reading='ACTIVATES',
            counts=dict(start_opportunities=10,launches=5,phase_order_sum=1,phase_order_ticks=2,command_realized_dot_sum=2,command_realized_pairs=2)))
    direct=report(rows)['direct_network_contrasts']
    for key in ('N2-minus-N1','N2-minus-N1r'):
        assert direct[key]['paired'][0]['deaths']==-1
        assert direct[key]['paired'][0]['kills']==1
        assert direct[key]['reading']=='DESCRIPTIVE'


def test_complete_held_sequence_has_no_90_tick_cutoff(monkeypatch):
    import stage1_export as ex
    monkeypatch.setattr(ex,'frame_rows',lambda _:iter([dict(joint={},gun_ids=[1],events=[],tick=t) for t in range(1,151)]+[dict(terminal=True)]))
    frames,launches=ex.sequence(dict(group='fixture'))
    assert len(frames)==150 and len(launches)==150


def test_tensor_replay_neighbor_and_earlier_tick_derivatives():
    model=Policy('N2'); meta,a=fixture(); f=PreparedFight(meta,a)
    replay=TensorReplay(model,3)
    replay.phase=torch.tensor([.1,.4,.7],dtype=torch.float64,requires_grad=True)
    initial=replay.phase
    f.tick(replay,0,False)
    first_phase=replay.phase
    for t in range(1,7):
        y=f.tick(replay,t)
    # Gun0's later phase depends on neighboring gun1's earlier phase.
    coupled=torch.autograd.grad(replay.phase[0],initial,retain_graph=True)[0][1]
    assert coupled.abs()>1e-6
    earlier=torch.autograd.grad(y[0,46],first_phase,retain_graph=True)[0]
    assert earlier.abs().sum()>1e-6 and torch.isfinite(earlier).all()


@pytest.mark.parametrize('kind',['N1r','N2'])
def test_native_stream_chunk_boundaries_preserve_full_state(kind):
    from collection import ROOT,read
    from stage1_data import admit,frame_rows
    from stage1_export import rpc,compare
    from stage1_stream import Session,CHUNK
    row=next(r for r in admit()['rows'] if r['split']=='test' and r['guns']==2 and r['cell']=='D2-shellfire')
    first=next(frame_rows(ROOT/(row['group']+'.jsonl')))
    frames=[]; launches=[]; wires=[]
    for t in range(36):
        joint=copy.deepcopy(first['joint']); joint['tick']=t+1; joint['t']=(t+1)/30
        ids=first['gun_ids'][:] if t<12 else first['gun_ids'][:1]
        if t>=12:
            joint['units']=[u for u in joint['units'] if u['id']!=first['gun_ids'][1]]
        launched=[ids[0]] if t in (11,19) else []
        snapshots=[{**joint,'self':i} for i in ids]
        frames.append(snapshots); launches.append(launched); wires.append(dict(joint=joint,ids=ids,launches=launched))
    model=Policy(kind)
    weights=dict(version='NS1',kind=kind,dtype='float64',parameters={k:dict(shape=list(v.shape),values=v.detach().reshape(-1).tolist()) for k,v in model.state_dict().items()})
    reference=rpc(dict(operation='stage1_sequence',weights=weights,frames=frames,launches=launches,ablation='intact'))
    session=Session(weights,'intact'); actual=[]
    try:
        for t in range(0,len(wires),CHUNK):
            actual+=session.call(dict(operation='stage1_stream_frames',frames=wires[t:t+CHUNK]))
        resources=session.close()
    except Exception:
        session.close(kill=True);raise
    assert resources['exit_code']==0 and resources['peak_rss_bytes']<512*1024**2
    compare(actual,reference)
