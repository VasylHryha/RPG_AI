import copy
import json
import math
from pathlib import Path
import subprocess
import pytest
import torch
from schema import encode,decode,check,inverse_point
from fixtures import snapshot,unit,threat,reflected
from models import Policy,export,recurrent_message
from dynamics import graph,phase_step,movement,ABLATIONS
from losses import losses
from labels import join
from protocol import split,aggregate,rank,rank_utilities,SliceES,reading
from project import projection

HERE=Path(__file__).resolve().parent
LOCAL=HERE/'_local'

def rpc(payload,okay=True):
    p=subprocess.run([str(LOCAL/'build/net_host')],input=json.dumps(payload,allow_nan=False)+'\n',text=True,capture_output=True,timeout=30)
    if okay:
        assert p.returncode==0,p.stderr
        return json.loads(p.stdout)
    assert p.returncode!=0
    return p.stderr

@pytest.fixture(scope='session')
def native_record():
    m=Policy('N1')
    with torch.no_grad():
        for p in m.parameters():p.zero_()
        m.readout.bias[34]=1;m.readout.bias[46:48]=1
    weights=export(m,LOCAL/'neutral_fixture_weights.json')
    p=subprocess.run([str(LOCAL/'build/native_fixture')],input=json.dumps({'weights':weights,'planner_states':json.loads((HERE/'fixtures/PLANNER_STATES.json').read_text())})+'\n',text=True,capture_output=True,timeout=30)
    assert p.returncode==0,p.stderr
    record=json.loads(p.stdout);(HERE/'NATIVE_FIXTURES.json').write_text(json.dumps(record,indent=2)+'\n');return record

@pytest.mark.parametrize('s',[snapshot(1),snapshot(2),snapshot(10),reflected(snapshot(2))])
def test_encoder_parity(s):
    x,meta=encode(s);native=rpc({'operation':'encode','snapshot':s})
    assert len(x)==1008
    assert native['features']==pytest.approx(x,abs=1e-12)
    for key in ('enemy_ids','friend_overflow','enemy_overflow','threat_overflow'):assert native[key]==meta[key]

@pytest.mark.parametrize('key',['energy','prep','tactic','skills','rng','plan'])
def test_enemy_boundary(key):
    s=snapshot();s['units'][-1][key]=123
    with pytest.raises(ValueError):encode(s)
    assert 'allowlist' in rpc({'operation':'encode','snapshot':s},False)

def test_masks_padding_target_unavailable_and_overflow():
    s=snapshot(1);s['threats']*=3
    for i,t in enumerate(s['threats']):t=copy.deepcopy(t);t['ordinal']=i+1;s['threats'][i]=t
    s['units'][0]['target']=999
    s['units'] += [unit(200+i,1,x=700+i) for i in range(14)]
    x,meta=encode(s);assert x[16]==-1 and x[32]==0 and meta['enemy_overflow'] and meta['threat_overflow']==4
    native=rpc({'operation':'encode','snapshot':s});assert native['features']==pytest.approx(x)
    s['units'][0]['target']=0;assert encode(s)[0][16]==0

def test_mirroring_roundtrip():
    s=snapshot();r=reflected(s);assert encode(s)[0]==pytest.approx(encode(r)[0]);assert reflected(r)==s
    p=inverse_point(s,30,-40);q=inverse_point(r,30,-40);assert p[0]+q[0]==1400 and p[1]==q[1]

@pytest.mark.parametrize('move,aim,target',[(0,0,1),(4,8,2),(32,32,1),(0,0,0)])
def test_decoder_parity(move,aim,target):
    s=snapshot();y=[-2.]*81;y[move]=3;y[33+target]=3;y[46]=y[47]=1;y[48+aim]=3
    p=decode(s,y);n=rpc({'operation':'decode','snapshot':s,'logits':y})
    for k in p:
        assert n[k]==pytest.approx(p[k]) if isinstance(p[k],list) else n[k]==p[k]

def test_invalid_and_no_legal_aim():
    s=snapshot();s['units'][0]['range']=50;y=[0.]*81;y[34]=1
    assert decode(s,y)['aim'] is None and not decode(s,y)['start']
    with pytest.raises(ValueError):decode(s,[math.nan]*81)
    bad=copy.deepcopy(s);bad['private']=0;rpc({'operation':'encode','snapshot':bad},False)

def test_native_state_collector_shadow_and_planner(native_record):
    assert native_record['checks']>=70 and native_record['fights']==0 and native_record['shells']>=1
    labels=join(native_record['events']);assert labels
    assert all(v['action']['target']==2 for v in labels.values())
    launches=[e for e in native_record['events'] if e['stage']=='launch']
    assert launches and all(e['value']['aim']==[650,400] for e in launches)
    # Outcomes remain acknowledgements; intent at tick1 starts, later release is not backfilled.
    assert ('fixture',1,1) in labels
    assert all(e['tick']>=key[1] for key,v in labels.items() for e in v['outcomes'])

def test_host_neutrality_source():
    h=(HERE/'host.h').read_text();cpp=(HERE/'host.cpp').read_text()
    assert 'public astelia::control::Controller' in h
    for forbidden in ('S4V7Controller','S4V6Controller','forcedP16','react_v1::','artilleryVolley(','net_public::react('):assert forbidden not in h+cpp
    assert 'if(teacher&&decision)' in cpp and 'if(shadow&&decision)' in cpp

@pytest.mark.parametrize('kind,count',[('N1',69841),('N1r',71385),('N2',71880)])
def test_exported_forward_parity(kind,count):
    torch.manual_seed(33);m=Policy(kind);assert sum(p.numel() for p in m.parameters())==count
    x=torch.tensor(encode(snapshot())[0],dtype=torch.float64)[None]
    state=torch.tensor([[.1,.9,-.3,.4] if kind=='N2' else [.1]*8],dtype=torch.float64)
    msg=torch.tensor([[.2]*12 if kind=='N2' else [-.2]*8],dtype=torch.float64)
    y,mem=m(x,state,msg) if kind!='N1' else m(x)
    weights=export(m,LOCAL/(kind+'_fixture_weights.json'))
    native=rpc({'operation':'forward','weights':weights,'features':x[0].tolist(),'state':state[0].tolist(),'message':msg[0].tolist()})
    assert native['logits']==pytest.approx(y[0].detach().tolist(),abs=1e-9,rel=1e-9)
    if mem is not None:assert native['memory']==pytest.approx(mem[0].detach().tolist(),abs=1e-9)

@pytest.mark.parametrize('ab',sorted(ABLATIONS))
def test_phase_motion_parity_bounds(ab):
    pos=torch.tensor([[400.,400.],[450.,400.],[550.,430.]],dtype=torch.float64);ids=[1,2,3];theta=torch.tensor([.2,1.1,-.8],dtype=torch.float64);f=torch.tensor([.4,-.2,.1],dtype=torch.float64)
    law=[.7,.4,.8,1.3,.6,.2];omega=torch.full((3,),law[4],dtype=torch.float64);fixed=graph(pos,ids)
    q=phase_step(theta,pos,ids,omega,torch.tensor(law[3],dtype=torch.float64),f,.2,ab,fixed);v=movement(q,pos,ids,*[torch.tensor(law[i],dtype=torch.float64) for i in (0,1,2,5)],torch.tensor([80.]*3),ab)
    n=rpc({'operation':'dynamics','positions':pos.tolist(),'ids':ids,'phases':theta.tolist(),'forcing':f.tolist(),'law':law,'dt':.2,'ablation':ab,'speeds':[80.]*3})
    assert n['phases']==pytest.approx(q.tolist(),abs=1e-8)
    assert torch.allclose(torch.tensor(n['motion'],dtype=torch.float64),v,atol=1e-8,rtol=1e-8)
    assert (q-theta).abs().max()<=1+1e-9 and torch.linalg.vector_norm(v,dim=1).max()<=20

def test_ablation_isolation_and_joint_gradients():
    pos=torch.tensor([[0.,0.],[50.,0.]],dtype=torch.float64);moved=torch.tensor([[0.,0.],[250.,0.]],dtype=torch.float64);ids=[1,2];fixed=graph(pos,ids);theta=torch.tensor([.2,1.],dtype=torch.float64,requires_grad=True);omega=torch.zeros(2,dtype=torch.float64);K=torch.tensor(1.,requires_grad=True,dtype=torch.float64);f=torch.zeros(2,dtype=torch.float64)
    fn=lambda p,ab:phase_step(theta,p,ids,omega,K,f,ablation=ab,fixed=fixed)
    assert not torch.allclose(fn(pos,'intact'),fn(moved,'intact'))
    assert torch.allclose(fn(pos,'no_geometry_to_mode'),fn(moved,'no_geometry_to_mode'))
    assert not torch.allclose(fn(pos,'topology_only'),fn(moved,'topology_only'))
    q=fn(pos,'intact');q[0].backward();assert theta.grad[1]!=0 and K.grad!=0 and torch.isfinite(theta.grad).all()
    epsilon=1e-6
    def scalar(k):return phase_step(theta.detach(),pos,ids,omega,torch.tensor(k,dtype=torch.float64),f)[0].item()
    assert K.grad.item()==pytest.approx((scalar(1+epsilon)-scalar(1-epsilon))/(2*epsilon),rel=.03,abs=1e-5)
    theta2=theta.detach()+torch.tensor([0.,1.]);params=[torch.tensor(v,dtype=torch.float64) for v in (.5,.5,.9,.2)];speeds=torch.ones(2)*80
    assert torch.allclose(movement(theta.detach(),pos,ids,*params,speeds,'no_mode_to_geometry'),movement(theta2,pos,ids,*params,speeds,'no_mode_to_geometry'))

def test_long_sparse_numerics_and_refinement():
    ids=[1,2];p=torch.tensor([[0.,0.],[0.,0.]],dtype=torch.float64);th=torch.tensor([0.,1.]);om=torch.tensor([2.,-2.]);k=torch.tensor(2.);f=torch.tensor([1.,-1.])
    for _ in range(300):th=phase_step(th,p,ids,om,k,f)
    assert torch.isfinite(th).all()
    coarse=phase_step(th,p,ids,om,k,f,.2);fine=th
    for _ in range(8):fine=phase_step(fine,p,ids,om,k,f,.025)
    assert torch.allclose(coarse,fine,atol=1e-3,rtol=1e-5)
    with pytest.raises(ValueError):phase_step(th,p,ids,om,k,f,.3)

@pytest.mark.parametrize('kind',['N1r','N2'])
def test_recurrent_sequence_parity(kind):
    torch.manual_seed(44);m=Policy(kind);weights=export(m,LOCAL/(kind+'_sequence_weights.json'));base=snapshot(2);base['threats']=[];frames=[]
    for tick in range(1,13):
        s=copy.deepcopy(base);s['tick']=tick;s['t']=tick/30;s['units'][1]['x']+=tick*3
        frames.append([s,{**copy.deepcopy(s),'self':2}])
    native=rpc({'operation':'sequence','weights':weights,'frames':frames,'ablation':'intact'})
    phases=torch.tensor([math.pi/8,math.pi/4],dtype=torch.float64);mem=torch.zeros((2,8),dtype=torch.float64);assign=[0,0];ids=[1,2];held=None
    for tick,frame in enumerate(frames,1):
        pos=torch.tensor([[s['units'][i]['x'],s['units'][i]['y']] for i,s in enumerate(frame)],dtype=torch.float64)
        if (tick-1)%6==0:held=torch.tensor([encode(s)[0] for s in frame],dtype=torch.float64)
        candidates=[encode(s)[1]['enemy_ids']+[0]*(12-len(encode(s)[1]['enemy_ids'])) for s in frame]
        if kind=='N2':y,phases,drift=m.joint(held,pos,ids,phases,candidates,assignments=assign)
        else:y,mem=m(held,mem,recurrent_message(mem,pos,ids,assign,candidates))
        if (tick-1)%6==0:
            actions=[decode(s,yy.detach().tolist()) for s,yy in zip(frame,y)]
            assign=[a['target'] for a in actions]
            for i,a in enumerate(actions):
                n=native[tick-1]['actions'][i]['action'];assert n['target']==a['target'] and n['start']==a['start'] and n['release']==a['release']
        if kind=='N2':assert [p[1] for p in native[tick-1]['phases']]==pytest.approx(phases.detach().tolist(),abs=1e-9)

def test_safe_loss_masks_and_backward():
    y=torch.zeros((2,81),dtype=torch.float64,requires_grad=True);labels={k:torch.tensor([0,16]) for k in ('move','target','aim')};labels['target']=torch.tensor([0,1]);labels.update(start=torch.tensor([0.,1.]),release=torch.tensor([1.,0.]));masks={k:torch.tensor([True,True]) for k in labels};legal={'move':torch.ones(2,33,dtype=torch.bool),'target':torch.ones(2,13,dtype=torch.bool),'aim':torch.ones(2,33,dtype=torch.bool)}
    masks['aim'][0]=False;loss,parts=losses(y,labels,masks,legal);loss.backward();assert torch.isfinite(y.grad).all() and (y.grad[0,48:]==0).all()
    # Opposite move modes remain separate categorical labels.
    assert y.grad[0,0]<0 and y.grad[1,16]<0
    legal['move'][1,16]=False
    with pytest.raises(ValueError):losses(y,labels,masks,legal)

def test_protocol_caps_splits_ranks_and_projection():
    row=dict(opportunities=10,launches=5,enemy_kills=10,completed=8,own_gun_deaths=0,seconds=400)
    passive={**row,'launches':0};assert rank(row)<rank(passive)
    assert rank_utilities([row,row])==[0,0];es=SliceES(13);assert len(es.candidates())==16;es.update([row]*16);assert es.mean==[0.]*16
    assert split('whole-series')==split('whole-series');data=[dict(group='g'+str(i),round=r,visitor=a,frames=[1,2,3]) for i in range(20) for r in range(3) for a in ('N1','N1r','N2')];result=aggregate(data);assert result and all(split(x['group'])=='train' for x in result)
    assert reading(200,[0.]*200,[0.]*200,[0.]*200)[0]=='PARK'
    assert reading(50,[-1.]*50,[0.]*50,[0.]*50)[0]=='NEGATIVE'
    p=projection(40);assert p['decision_rows']==400000 and p['decision_bytes']==1676800000 and p['joint_bytes']==2549760000

@pytest.mark.parametrize('field,value',[('tick',1.5),('self',1.2),('t',-.01),('fight',12)])
def test_wire_identity_root(field,value):
    s=snapshot();s[field]=value
    with pytest.raises(ValueError):check(s)
    rpc({'operation':'encode','snapshot':s},False)

def test_fractional_unit_identity_and_label_chronology(native_record):
    s=snapshot();s['units'][0]['id']=1.2
    with pytest.raises(ValueError):check(s)
    rpc({'operation':'encode','snapshot':s},False)
    events=copy.deepcopy(native_record['events']);events.reverse()
    with pytest.raises(ValueError):join(events)
    events=[e for e in native_record['events'] if e['stage']!='snapshot']
    with pytest.raises(ValueError):join(events)
    launches=[e for e in native_record['events'] if e['stage']=='launch']
    assert launches[0]['tick']>=7 and launches[0]['decision_tick']==1
    joined=join(native_record['events'])
    assert not joined[('fixture',7,1)]['masks']['target']

def test_n2_hold_drift_and_imitation_law_mask():
    m=Policy('N2')
    with torch.no_grad():
        for p in m.parameters():p.zero_()
        m.readout.bias[0]=2;m.readout.bias[34]=2
    s=snapshot();s['threats']=[];weights=export(m,LOCAL/'hold_drift_weights.json')
    result=rpc({'operation':'sequence','weights':weights,'frames':[[s,{**copy.deepcopy(s),'self':2}]],'ablation':'intact'})
    action=result[0]['actions'][0]['action']
    assert action['move_index']==0 and action['multiplier']==1 and action['goal']!=[400,400]
    m.law.sum().backward();assert m.law.grad.tolist()==[0,0,0,1,1,0]

def test_extreme_legal_loss_isolation():
    y=torch.full((1,81),-1e12,dtype=torch.float64,requires_grad=True);labels={'move':torch.tensor([0]),'target':torch.tensor([0]),'aim':torch.tensor([0]),'start':torch.tensor([0.]),'release':torch.tensor([0.])};masks={k:torch.tensor([k=='move']) for k in labels};legal={'move':torch.zeros(1,33,dtype=torch.bool),'target':torch.ones(1,13,dtype=torch.bool),'aim':torch.ones(1,33,dtype=torch.bool)};legal['move'][0,0]=True
    total,parts=losses(y,labels,masks,legal);assert total.item()==0

def test_teacher_selected_target_range_and_same_cadence():
    s=snapshot(1);s['threats']=[];s['units'][1]['x']=725;s['units'][2]['x']=800
    action=rpc({'operation':'teacher','snapshots':[s]})['actions'][0]['action']
    assert not action['start'] # Aim offset can be legal while target center is out of native range.
    s['units'][1]['x']=650;action=rpc({'operation':'teacher','snapshots':[s]})['actions'][0]['action'];assert action['start'] and not action['release']

def test_imitation_optimizer_guard_without_updates():
    from models import assert_imitation_optimizer
    m=Policy('N2');optimizer=torch.optim.Adam(m.parameters(),lr=.001,weight_decay=0)
    assert_imitation_optimizer(m,optimizer)
    optimizer.state[m.law]={'exp_avg':torch.ones_like(m.law)}
    with pytest.raises(ValueError):assert_imitation_optimizer(m,optimizer)


def test_joint_wire_reconstruction_and_slice_requests(native_record):
    from labels import unpack_frame
    from requests import drill
    s=snapshot();events=[e for e in native_record['events'] if e['tick']==1]
    reduced=copy.deepcopy(events)
    for e in reduced:
        if e['stage']=='snapshot':e['value']={'self':e['unit']}
    unpacked=unpack_frame({'joint':s,'events':reduced})
    assert next(e for e in unpacked if e['stage']=='snapshot')['value']['self']==1
    a=drill('D1-static',2,13);b=drill('D2-shellfire',2,13)
    assert len(a['roster'])==8 and len(b['roster'])==6
