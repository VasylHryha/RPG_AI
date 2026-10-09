"""Synthetic inference/settings/readout checks only; no training or fights."""
import copy
import json
import numpy as np
import pytest
import torch
import runtime as r
from models import Policy,initial,export
from training import forward,flat
from test_stageb2 import frame,native_binary,rpc

def graph_frame():
    row=frame();enemy=copy.deepcopy(row['units'][2:])
    own=[]
    for i in range(10):
        u=copy.deepcopy(row['units'][1]);u[0]=20+i;u[3:5]=[50+i*10,100];u[15]=7 if i==9 else 9
        own.append(u)
    row['units']=own+enemy;row['own']=[[u[0],0,0,.2,1,100,10,False,3,.3] for u in own]
    row['labels']=[];return row

@pytest.mark.parametrize('parent,bonus',[('N1','N1b'),('N1r','N1rb')])
def test_indicator_graph_budget_and_native(native_binary,parent,bonus,tmp_path):
    row=graph_frame();base=Policy(parent).double().eval();control=Policy(bonus).double().eval();control.load_state_dict(base.state_dict())
    assert sum(p.numel() for p in base.parameters())==sum(p.numel() for p in control.parameters())
    with torch.no_grad():
        a,*_=forward(base,row,initial(parent,[],torch.float64),[],None,(0,[]))
        y,state,ids,_,_,_,_=forward(control,row,initial(bonus,[],torch.float64),[],None,(0,[]))
    # Unit 20's ninth nearest ally targets 7: it is excluded. Eight peers
    # target 9 but give +2 once, with no effect on none or other outputs.
    np.testing.assert_allclose((y['target']-a['target'])[0].numpy(),[0,0,2],atol=1e-12)
    np.testing.assert_allclose((y['target']-a['target'])[-1].numpy(),[0,0,2],atol=1e-12)
    for key in ('move','fire','drift','aim','move_logits','aim_logits'):torch.testing.assert_close(y[key],a[key],rtol=0,atol=0)
    weights=export(control,tmp_path/(bonus+'.weights.json'))
    result=rpc(native_binary,[json.dumps(dict(frames=[row],weights=weights))])[0]
    np.testing.assert_allclose(np.asarray(result['outputs'][0]),flat(y).numpy(),atol=1e-8,rtol=0)
    from candidate_audit import observe_prediction,observe_record,report
    python={};native={};observe_prediction(python,row,ids,y);observe_record(native,result)
    assert python==native and report(python)['ranged']['move']['chosen']==10
    # Strict 300 px graph bound and no self bonus, even with own assignment.
    row=frame();row['units'][0][15]=7;row['units'][1][15]=9;row['units'][1][3:5]=[335,40]
    with torch.no_grad():
        a,*_=forward(base,row,initial(parent,[],torch.float64),[],None,(0,[]))
        y,*_=forward(control,row,initial(bonus,[],torch.float64),[],None,(0,[]))
    torch.testing.assert_close(y['target'],a['target'],rtol=0,atol=0)

def outcome_rows(look=20):
    return [dict(panel=p,arm=a,pair_key=str(i),seed=i+1,orientation=i%2,tactic='regular',stats=dict(win=i<10 if a=='T' else i<9,own_deaths=5 if a=='T' else 8)) for p in ('regular','C3') for a in ('N1b','T') for i in range(look)]

def test_readiness_exact_boundary_missing_pairs_and_zero_teacher():
    from readiness import evaluate
    rows=outcome_rows();assert evaluate(rows,20,['N1b'])['READY']=='YES'
    changed=copy.deepcopy(rows);next(v for v in changed if v['arm']=='N1b')['stats']['own_deaths']=9
    assert evaluate(changed,20,['N1b'])['READY']=='NO'
    changed=copy.deepcopy(rows);next(v for v in changed if v['arm']=='N1b')['seed']=999
    assert evaluate(changed,20,['N1b'])['READY']=='NO'
    assert evaluate(rows[:-1],20,['N1b'])['READY']=='NO'
    for v in rows:
        if v['arm']=='T':v['stats']['win']=False
    assert evaluate(rows,20,['N1b'])['READY']=='NO'

def test_approvals_history_exclusion_live_reduction_and_code_lock(tmp_path,monkeypatch):
    import owner_approvals as owner
    from training_control import training_cap,TrainingDeadline
    cfg=owner.load();path=tmp_path/'OWNER_APPROVALS.json';path.write_text(json.dumps(cfg));monkeypatch.setattr(owner,'PATH',path);monkeypatch.setattr(owner,'HERE',tmp_path)
    pins=r.sources();one=owner.snapshot();cap=training_cap(r.HERE)
    deadline=TrainingDeadline(r.HERE,1000+cap['cap_seconds'],cap['cap_seconds'])
    monkeypatch.setattr('training_control.time.monotonic',lambda:1001)
    cfg['training']['cap_seconds']=100;path.write_text(json.dumps(cfg));two=owner.snapshot()
    assert one['sha256']!=two['sha256'] and r.sources()==pins and deadline.current()==1100
    cfg['training']['cap_seconds']=16200;path.write_text(json.dumps(cfg));monkeypatch.setattr('training_control.time.monotonic',lambda:1003)
    assert deadline.current()==1100
    log=[json.loads(x) for x in (tmp_path/'_local/owner_approvals/CHANGES.jsonl').read_text().splitlines()]
    assert log[1]['previous_sha256']==log[0]['sha256']
    from train import checked
    budget=dict(arms=list(r.ARMS),variant=r.VARIANT,sources=dict(pins,changed='code'),index_sha256='hash',candidate_cache='cache',coverage_sha256='hash')
    monkeypatch.setattr(r,'read',lambda p:'cache' if p.name=='PREPARED_CACHE.json' else budget)
    monkeypatch.setattr(r,'sha',lambda _: 'hash');monkeypatch.setattr('train.validate_index',lambda _:None);monkeypatch.setattr('train.coverage_admission',lambda _:None)
    with pytest.raises(RuntimeError,match='code/index drift'):checked(tmp_path)

def test_dagger_schedule_request_mix_and_round_gate(tmp_path,monkeypatch):
    import dagger,dagger_schedule
    from types import SimpleNamespace
    monkeypatch.setattr(r,'LOCAL',tmp_path);monkeypatch.setattr(dagger,'gate',lambda _:None)
    monkeypatch.setattr(dagger,'used_seeds',lambda:set());monkeypatch.setattr(r.collect,'identity',lambda:'binary')
    monkeypatch.setattr(r.collect,'a0',lambda:SimpleNamespace(CELLS=['c3'],request=lambda *args:dict(options={})))
    (tmp_path/'round0/training').mkdir(parents=True)
    for a in r.ARMS:(tmp_path/'round0/training'/(a+'.weights.json')).write_text('{}')
    (tmp_path/'round0/PARITY_STAGEB2.json').write_text('{}')
    schedule=dagger_schedule.declared();assert schedule['rounds']==5 and schedule['teacher_driving_share']==[.5,.375,.25,.125,0]
    ledger=dagger.prepare(1)
    for i in range(3):
        group=[j for j in ledger['jobs'] if j['tag'].endswith(f'_{i:03}')]
        assert len(group)==5 and len({(j['seed'],j['teacher_driving']) for j in group})==1
        for j in group:
            cfg=r.read(tmp_path/'requests'/(j['tag']+'.json'))['stageA']['dagger']
            assert cfg['teacher_driving']==j['teacher_driving'] and cfg['movement_sigma_px']==cfg['target_replace_probability']==0
    with pytest.raises((FileNotFoundError,RuntimeError)):dagger.prepare(2)
    with pytest.raises(ValueError):dagger.prepare(6)

def test_candidate_counts_preserved_in_compact_recording(tmp_path):
    import lzma
    from recording import Writer,rows
    row=frame();row['candidatePicks']=[dict(id=1,role='artillery',head='aim',type=1),dict(id=1,role='artillery',head='move',type=18)]
    path=tmp_path/'rows.xz'
    with lzma.open(path,'wb') as f:Writer(f).write(row)
    assert next(rows(path))['candidatePicks']==row['candidatePicks']
