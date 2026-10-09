"""Focused speed contracts: exact native banks/state, cache integrity and sampling."""
import copy,time
import numpy as np
import pytest
import torch
import runtime as r
from test_stageb2 import frame
from candidates import bank,mapped_labels,pack_candidates
from native_candidates import batch,unpack,packed
from models import Policy,initial
from training import forward

@pytest.mark.parametrize('mutate',[False,True])
def test_batch_matches_python_order_features_sources(mutate):
    row=frame()
    if mutate:
        row['units'].reverse();row['longVelocity']={'7':[8.,-12.]}
        row['shots']=[];row['fields']=[];row['casts']=[]
    banks=unpack(batch(row));ids=sorted(banks);arrays=packed(banks,ids)
    for i,id in enumerate(ids):
        reference,_=bank(row,id)
        for key in reference:np.testing.assert_allclose(arrays[key][i],reference[key],atol=1e-12,rtol=1e-12)
    expected=mapped_labels(row,ids,np.ones((len(ids),2)))
    row['_candidate_banks']=banks
    assert mapped_labels(row,ids,np.ones((len(ids),2)))==expected

@pytest.mark.parametrize('kind',list(r.ARMS))
def test_state_only_preserves_prefix_including_removal(kind):
    torch.manual_seed(73);model=Policy(kind).double().eval()
    full=(initial(kind,[],torch.float64),[],None,(0,[]));fast=copy.deepcopy(full)
    with torch.no_grad():
        for at in range(4):
            row=frame();row['t']=(at+1)/30
            if at==3:
                row['units']=[u for u in row['units'] if u[0]!=4];row['own']=row['own'][:1]
            y,state,ids,_,cache,clock,_=forward(model,row,*full);full=(state,ids,cache,clock)
            z,state2,ids2,_,cache2,clock2,_=forward(model,row,*fast,state_only=True);fast=(state2,ids2,cache2,clock2)
            torch.testing.assert_close(y['drift'],z['drift'],rtol=0,atol=0)
            torch.testing.assert_close(state,state2,rtol=0,atol=0)
            assert ids==ids2


def test_cache_roundtrip_reuse_and_corruption(tmp_path):
    import candidate_cache as cc
    rows=[frame(),frame()];raw=tmp_path/'raw';raw.write_text('fixture')
    f=dict(tag='fixture',raw_file=str(raw),raw_sha256=r.sha(raw),frames=2)
    def stream(path):yield from copy.deepcopy(rows)
    index=dict(fights=[f]);cc.prepare(tmp_path,index,stream,time.monotonic()+30)
    cc.activate(tmp_path,index,stream)
    loaded=list(cc.frames(raw))
    for original,cached in zip(rows,loaded):
        for key,value in pack_candidates(original,[1,4]).items():np.testing.assert_allclose(pack_candidates(cached,[1,4])[key],value,atol=1e-12,rtol=1e-12)
    path=cc.location(tmp_path,f);first=path.stat().st_mtime_ns
    cc.prepare(tmp_path,index,stream,time.monotonic()+30);assert path.stat().st_mtime_ns==first
    path.write_bytes(b'corrupt')
    with pytest.raises(RuntimeError,match='content drift'):list(cc.frames(raw))
    cc.ACTIVE=None


def test_empty_aim_audit_and_native_validation():
    row=frame();row['units'][0][18]=1000;row['units'][0][11]=1500
    with pytest.raises(ValueError,match='empty required'):batch(row)
    row['_candidate_banks']=unpack(batch(row,allow_missing_aim=True))
    assert mapped_labels(row,[1])[0]['aim']['distance'] is None
    row=frame();row['units'][0][7]=float('nan')
    with pytest.raises(ValueError,match='nonfinite'):batch(row)


def test_declared_sampling_bounds_and_panel_timing():
    from coverage import accumulate,population,error_bounds,STRIDE
    from train import timing_fights
    counts={};pop={};row=frame()
    for at in range(12):
        population(pop,row)
        if at%STRIDE==0:accumulate(counts,row)
    for value in error_bounds(counts,pop).values():
        assert value['population_rows']==12 and value['rows']==2
        for metric,bound in value['deterministic_error_bound'].items():
            assert bound['lower']<=value[metric]<=bound['upper']
    fights=[dict(panel=p,frames=n,tag=str(n)) for p,n in [('C3',10),('C3',20),('regular',12)]]
    assert [f['frames'] for f in timing_fights(fights)]==[20,12]


def test_evaluation_timing_fields_and_memoryless_stored(monkeypatch):
    import training
    from loss import install
    install({role:dict(weights=[1,1]) for role in ('melee','ranged','artillery')})
    rows=[frame(),frame()]
    monkeypatch.setattr(training,'frames',lambda path:iter(copy.deepcopy(rows)))
    model=Policy('N1').float()
    real_forward=training.forward
    monkeypatch.setattr(training,'forward',lambda *args,**kwargs:(_ for _ in ()).throw(AssertionError('memoryless prefix forward')))
    loaded,saved,_=training.stored(model,dict(raw_file='fixture'),4,time.monotonic()+10)
    assert list(saved)==[0] and len(loaded)==2
    monkeypatch.setattr(training,'forward',real_forward)
    diag=training.evaluate(model,[dict(raw_file='fixture')],4,None,time.monotonic()+10)
    assert diag['window_ticks']==2 and 0<=diag['prefix_seconds']<=diag['wall_seconds']
