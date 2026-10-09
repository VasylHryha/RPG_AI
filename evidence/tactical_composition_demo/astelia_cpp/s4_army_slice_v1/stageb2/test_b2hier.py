"""Light lossless hierarchy, true-family loss, all-arm native parity checks."""
import copy,json
import numpy as np
import pytest
import torch
import runtime as r
from hierarchy import partition,LAYOUT,FAMILY_SLOTS,MEMBERS
from native_candidates import batch,unpack,packed
from candidates import bank,mapped_labels,MAX_AIM,MAX_MOVE
from models import Policy,initial,export
from training import forward,flat
from test_stageb2 import frame,native_binary,rpc


def test_max_envelope_lossless_nearest_pages():
    row=frame();own=row['units'][:2]
    own=[copy.deepcopy(own[i%2]) for i in range(64)]
    for i,u in enumerate(own):u[0]=i+1;u[3:5]=[30+i*3,60+i*2]
    enemies=[copy.deepcopy(row['units'][2+i%2]) for i in range(64)]
    for i,u in enumerate(enemies):u[0]=100+i;u[3:5]=[200+i*2,180+i]
    row['units']=own+enemies;row['own']=[[u[0],0,0,.4,1,100,10,False,3,.35] for u in own]
    row['shots']=row['shots']*64;row['fields']=row['fields']*32
    row['shells']=row['shells']*64;row['casts']=row['casts']*32
    arrays=packed(unpack(batch(row)),[1])
    for head in ('aim','move'):
        table,mapping=partition(arrays[head+'_features'],arrays[head+'_valid'],head)
        valid=np.flatnonzero(arrays[head+'_valid'][0]);reached=table[table>=0]
        assert sorted(reached)==valid.tolist() and len(set(reached))==len(valid)
        assert table.shape==(1,FAMILY_SLOTS,MEMBERS)
        for j in valid:
            family,member=mapping[0,j];assert table[0,family,member]==j
        assert (table>=0).sum(-1).max()<=64
    # No type23 radial-image loss, even in the largest permitted actor bank.
    assert (arrays['move_features'][0,:,23]>.5).sum()>256


@pytest.mark.parametrize('arm',r.ARMS)
def test_true_family_member_loss_and_gradient(arm):
    from loss import install
    import training
    install({role:dict(weights=[1,1]) for role in ('melee','ranged','artillery')})
    row=frame();model=Policy(arm).float()
    with torch.no_grad():
        # Make the wrong semantic family win; labels must still train their
        # actual family/member without forcing the label into inference inputs.
        model.move_family.weight.zero_();model.move_family.bias.zero_();model.move_family.bias[0]=100
    y,*_=forward(model,row,initial(arm,[]),[],None,(0,[]),supervised=True)
    mapped=mapped_labels(row,[1,4],y['drift'].detach().numpy())
    for name in ('aim','move'):
        assert y[name+'_train_logits'].shape==(2,64)
        for i,lab in enumerate(mapped):
            if lab[name] is None:continue
            assert int(y[name+'_true_family'][i])==lab[name]['family']
            assert int(y[name+'_true_member'][i])==lab[name]['member']
            assert lab[name]['hierarchy_reachable']
    value,heads=training.objective(y,row,[1,4],[7,9]);value.backward()
    assert {'aim_family','move_family','aim_choice','move_choice'}<=heads.keys()
    for name in ('aim','move'):
        assert getattr(model,name+'_family').weight.grad.abs().sum()>0
        assert getattr(model,name+'_hidden').weight.grad.abs().sum()>0
    model.eval()
    with torch.no_grad():
        a,*_=forward(model,row,initial(arm,[]),[],None,(0,[]))
        changed=copy.deepcopy(row);changed['labels']=[]
        b,*_=forward(model,changed,initial(arm,[]),[],None,(0,[]))
    torch.testing.assert_close(flat(a),flat(b),rtol=0,atol=0)


@pytest.mark.parametrize('arm',r.ARMS)
def test_native_paged_family_parity(native_binary,arm,tmp_path):
    row=frame();own=row['units'][0];own[18]=0;own[11]=400
    enemies=[copy.deepcopy(row['units'][2]) for _ in range(64)]
    for i,u in enumerate(enemies):u[0]=100+i;u[3:7]=[150+i,130+i%7,0,0]
    row['units']=[own,*enemies];row['own']=row['own'][:1]
    model=Policy(arm).double().eval()
    with torch.no_grad():
        for name in ('aim','move'):
            layer=getattr(model,name+'_family');layer.weight.zero_();layer.bias.fill_(-100)
            # aim direct page1 holds the 65th direct point; move radial image
            # page2 exists with >128 projected members.
            layer.bias[1 if name=='aim' else 20]=100
        y,*_=forward(model,row,initial(arm,[],torch.float64),[],None,(0,[]))
    weights=export(model,tmp_path/(arm+'.json'))
    actual=rpc(native_binary,[json.dumps(dict(frames=[row],weights=weights))])[0]
    np.testing.assert_allclose(actual['outputs'][0],flat(y).numpy(),rtol=0,atol=1e-8)
    for name in ('aim','move'):
        assert int((y[name+'_logits']>-1e6).sum(-1).max())<=64
    from candidate_audit import observe_prediction,observe_record
    py={};native={};observe_prediction(py,row,[1],y);observe_record(native,actual);assert py==native
