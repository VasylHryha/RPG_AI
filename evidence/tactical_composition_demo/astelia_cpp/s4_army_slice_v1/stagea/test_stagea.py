"""Focused contracts and real native stored-sequence inference; no fights/training."""
import copy
import json
from pathlib import Path
import sys
import numpy as np
import pytest
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ARMS,BINARY,LOCAL,write
from data import labels,pack
from models import Policy,export,initial
from parity import compare,replay,sequence
from training import environment
environment()
from training_control import TrainingDeadline,atomic_checkpoint,last_checkpoint,training_cap

def fixture():
    rows=[]
    for tick in range(37):
        units=[];history={};own=[]
        for side in (0,1):
            for role in range(3):
                id=side*3+role+1
                if tick>=20 and id==5:continue
                units.append([id,side,role,250+side*220+tick*.5,200+role*50,15,0,100,100,10,60,300,40,0,1,0,tick,tick*2,100 if role==2 else 0,tick,tick*2,0,0]);history[str(id)]=[tick*.01]*16
                if side==0:own.append([id,0,.2,.2,1,100,0,False,3,.4])
        rows.append(dict(stageA=True,t=tick/30,dt=1/30,width=1000,height=800,units=units,own=own,shells=[[.25,.25,.25,.25,.3,.4,0]] if tick%3 else [],shots=[],fields=[],casts=[],history=history,pairModes={'1:4':True},labels=[dict(id=id,role=('melee','ranged','artillery')[id-1],executed=dict(goal=[300,250],target=4,multiplier=1,aim=[600,300] if id==3 else None,fire='automatic'),ready=True,active=False,engineRelease=0) for id in (1,2,3)]))
    return rows

def test_input_channels_and_masks():
    row=fixture()[3];plain,ids,enemies=pack(row,'N1');hist,_,_=pack(row,'N1h')
    assert np.all(plain['tokens'][:,48:]==0) and np.all(plain['query'][:,48:]==0)
    assert np.any(hist['tokens'][:,48:]!=0) and hist['query'][0,64]==1
    assert len(ids)==3 and len(enemies)==3 and labels(row,ids,enemies)[2]['aim_mask']
    overflow=copy.deepcopy(row);overflow['shots']=[[0]*7]*65
    with pytest.raises(ValueError,match='overflow'):pack(overflow,'N1')
    broken=copy.deepcopy(row);broken['labels'][0]['executed']['target']=999
    with pytest.raises(ValueError,match='missing label'):labels(broken,ids,enemies)

@pytest.mark.parametrize('arm',ARMS)
def test_native_full_sequence_parity(arm,tmp_path):
    if not BINARY.exists():pytest.fail('build Stage A host first')
    torch.manual_seed(77);m=Policy(arm).double();rows=fixture();path=tmp_path/(arm+'.json');weights=export(m,path)
    native=replay(weights,rows);python=sequence(m,rows);r=compare(python,native)
    assert r['max_abs_error']<1e-9 and r['categorical_mismatches']==0
    # Memory is initialized again at a new fight; same complete sequence repeats.
    again=replay(weights,rows);assert compare(native,again)['max_abs_error']==0
    if arm in ('N2','N2J0'):assert np.any(np.abs(native[0][:,8:10])>0)


def test_near_tie_and_none_target_parity(tmp_path):
    m=Policy('N1').double()
    with torch.no_grad():
        for v in m.parameters():v.zero_()
        m.out.bias[3]=1e-12;m.out.bias[8]=1e-12
    rows=fixture();weights=export(m,tmp_path/'near.json');a=sequence(m,rows);b=replay(weights,rows)
    assert compare(a,b)['categorical_mismatches']==0
    assert (a[0][:,3:6].argmax(1)==0).all() and (a[0][:,10:].argmax(1)==0).all()


def test_J_gradient_and_J0_control():
    # Check differentiable physical channel without any optimizer/training steps.
    from training import forward
    row=fixture()[0];models=[]
    for arm in ('N2','N2J0'):
        torch.manual_seed(9);m=Policy(arm).float();y,*_=forward(m,row,initial(arm,[]),[],None,(0,[]));y['drift'].square().sum().backward();models.append(m)
    assert abs(float(models[0].law.grad[2]))>1e-8
    assert float(models[1].law.grad[2])==0


def test_checkpoint_transaction_and_cap(tmp_path):
    write(tmp_path/'_local/TRAIN_CAP.json',dict(cap_seconds=10800,approved_by='owner',date='2026-10-09'))
    assert training_cap(tmp_path)['cap_seconds']==10800
    atomic_checkpoint(tmp_path/'epochs/epoch_0001.pt',dict(epoch=1,budget_sha256='abc',model={}))
    assert last_checkpoint(tmp_path/'epochs','abc')['epoch']==1
    with pytest.raises(RuntimeError,match='mismatch'):last_checkpoint(tmp_path/'epochs','other')


def test_source_hashes_exclude_living_docs():
    from common import sources
    assert all(not p.endswith('.md') and 'TRAIN_CAP' not in p and 'PLAN_CURRENT' not in p for p in sources())


def test_memoryless_conflicts_use_own_query_and_cached_bank(tmp_path,monkeypatch):
    import contextlib
    import gzip
    import time
    import common,data,jobs
    monkeypatch.setattr(common,'HERE',tmp_path);monkeypatch.setattr(data,'LOCAL',tmp_path);monkeypatch.setattr(data,'sources',lambda:{})
    write(tmp_path/'_local/TRAIN_CAP.json',dict(cap_seconds=300,approved_by='owner',date='2026-10-09'))
    @contextlib.contextmanager
    def offline(seconds):
        class Monitor:
            def live_memory(self,pid):return 0
        yield time.monotonic()+seconds,Monitor()
    monkeypatch.setattr(jobs,'admitted',offline)
    original=fixture()[:2];other=copy.deepcopy(original)
    # A peer's fresh prep is invisible to unit1 between encoder refreshes.
    other[1]['own'][1][2]=.1
    other[1]['labels'][0]['executed']['goal']=[310,250]
    original[1]['labels'][2]['executed']['aim']=None
    third=copy.deepcopy(original)
    third[1]['own'][1][2]=.15
    third[1]['labels'][2]['executed']['aim']=[620,300]
    fights=[]
    for i,(split,rows) in enumerate((('train',original),('validation',other),('test',third))):
        path=tmp_path/f'{i}.gz'
        with gzip.open(path,'wt') as f:
            for row in rows:f.write(json.dumps(row)+'\n')
        fights.append(dict(seed=i+1,split=split,raw_file=path.name,raw_sha256=__import__('common').sha(path),frames=2))
    index=dict(fights=fights);write(tmp_path/'INDEX.json',index)
    result=data.audit(index)
    assert result['status']=='BLOCKED' and result['counts']['N1']['move']['exact_conflicts']>0
    assert result['counts']['N1h']['move']['exact_conflicts']>0
    # First no aim, then aim A, then aim B under the same actual unit input.
    assert result['counts']['N1']['aim']['exact_conflicts']>0
    assert result['counts']['N1h']['aim']['exact_conflicts']>0
