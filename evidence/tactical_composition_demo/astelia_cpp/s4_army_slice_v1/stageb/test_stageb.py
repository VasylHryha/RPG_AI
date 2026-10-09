"""Focused revision contracts and tiny real-host fixtures. No new full fights."""
from pathlib import Path
import sys,copy,json,secrets,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
import runtime as r
import numpy as np,pytest,torch
from calibration import choose,fire_classes
from train import project
from models import Policy,export
from oracle import oracle
from recording import rows

def test_calibration_matches_rate_and_reports_precision_recall():
    v=choose([.1,.2,.3,.4],[True,False,True,False],[True]*4)
    assert v['oracle_active']==v['predicted_active']==2 and v['tp']==v['fp']==v['fn']==1
    assert v['precision']==v['recall']==.5
    assert choose([1,2],[True,True],[False,False])['predicted_active']==0
    with pytest.raises(ValueError):choose([float('nan')],[True],[True])

def test_role_threshold_decoding_and_ties():
    a=np.array([[0.,1.,0.]]*3)
    assert fire_classes(a,[0,1,2],[-2,-1,0]).tolist()==[0,0,1]

def test_four_lane_budget_and_no_per_arm_legacy_hour_guard():
    samples={a:dict(epoch_seconds=600,tail_seconds=100) for a in r.ARMS}
    p=project(samples,10,4)
    assert len(p['groups'])==4 and p['projected_seconds']==7320
    assert project(samples,10,1)['projected_seconds']>10800

def test_source_manifest_excludes_living_docs():
    assert all(Path(k).suffix in ('.py','.cpp','.h','.lock') for k in r.sources())
    assert not any('PLAN_CURRENT' in k or 'TRAIN_CAP' in k for k in r.sources())

def test_training_loss_does_not_inverse_weight_absent_release():
    import training
    import importlib.util
    spec=importlib.util.spec_from_file_location('stagea_test_fixture',r.STAGEA/'test_stagea.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    row=m.fixture()[1];model=Policy('N1');from models import initial
    y,*_=training.forward(model,row,initial('N1',[]),[],None,(0,[]));loss,heads=training.objective(y,row,[1,2,3],[4,5,6],None)
    assert torch.isfinite(loss) and heads['fire']>0

def host_fixture(tmp_path,arm,shadow,thresholds):
    from execution import execute
    from fixture_host import FixtureMonitor
    model=Policy(arm).double()
    with torch.no_grad():
        for p in model.parameters():p.zero_()
        model.out.bias[3]=.2;model.out.bias[4]=.4;model.out.bias[8]=-4
    weights=export(model,tmp_path/(arm+'.json'));weights['fireThresholds']=thresholds
    req=r.collect.a0().request('O','regular',731451,0);req['options']['duration']=.4;req['stageA']=dict(collect=True,shadow=shadow,weights=weights)
    tag='host_fixture_'+secrets.token_hex(8);path=r.LOCAL/'requests'/(tag+'.json');r.write(path,req,exclusive=True);job=dict(tag=tag,request_sha256=r.sha(path),split='integration',arm=arm)
    c=execute(job,time.monotonic()+120,FixtureMonitor(),'FIXTURE_ONLY');return c,[x for x in rows(r.LOCAL/c['raw_file']) if x.get('stageA')]

@pytest.mark.parametrize('arm',r.ARMS)
def test_real_host_shadow_isolation_and_role_calibration(tmp_path,arm):
    c,a=host_fixture(tmp_path,arm,True,[-100,100,-100]);d,b=host_fixture(tmp_path,arm,False,[-100,100,-100])
    assert c['stats']==d['stats'] and len(a)==len(b)==c['frames'] and c['frames']>=12
    for x,y in zip(a,b):
        assert x['units']==y['units'] and x['labels']==y['labels'] and x['networkState']==y['networkState']
        assert {v['id'] for v in x['shadowLabels']}=={v['id'] for v in x['labels']}
    commands={v['role']:v['raw']['fire'] for v in a[0]['labels']} if 'raw' in a[0]['labels'][0] else {v['role']:v['executed']['fire'] for v in a[0]['labels']}
    assert commands==dict(melee='automatic',ranged='hold',artillery='automatic')

def test_real_offline_oracle_against_tiny_live_teacher():
    from execution import execute
    from fixture_host import FixtureMonitor
    req=r.collect.a0().request('O','regular',731452,1);req['options']['duration']=.4;req['stageA']=dict(collect=True,shadow=True)
    tag='host_fixture_'+secrets.token_hex(8);p=r.LOCAL/'requests'/(tag+'.json');r.write(p,req,exclusive=True);j=dict(tag=tag,request_sha256=r.sha(p),split='integration',arm='O')
    c=execute(j,time.monotonic()+120,FixtureMonitor(),'FIXTURE_ONLY')
    with oracle(req,timeout=30) as label:
        for row in rows(r.LOCAL/c['raw_file']):
            if not row.get('stageA'):continue
            offline=label(row)
            for a,b in zip(offline,row['shadowLabels']):
                assert a['id']==b['id'];assert a['executed']['fire']==b['executed']['fire'];assert a['executed']['target']==b['executed']['target']
                assert np.allclose(a['executed']['goal'],b['executed']['goal'],atol=1e-8)

def test_geometric_loss_has_useful_pixel_gradient():
    import training
    from loss import install,BASE_OBJECTIVE
    import importlib.util
    spec=importlib.util.spec_from_file_location('stagea_loss_fixture',r.STAGEA/'test_stagea.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    row=m.fixture()[1];model=Policy('N2');from models import initial
    y,_,ids,enemies,*_=training.forward(model,row,initial('N2',[]),[],None,(0,[]))
    install({role:dict(weights=[1.,2.]) for role in ('melee','ranged','artillery')})
    try:
        value,heads=training.objective(y,row,ids,enemies);value.backward()
        assert torch.isfinite(value) and heads['move']>0
        assert model.out.weight.grad is not None and torch.isfinite(model.out.weight.grad).all()
    finally:training.objective=BASE_OBJECTIVE

def test_calibrated_parity_rejects_uncertified_threshold_flip():
    from calibrated_parity import compare_calibrated
    row=dict(t=.1,units=[[1,0,0]])
    a=np.zeros((1,11));b=a.copy();a[0,3]=1e-3
    proof=compare_calibrated([a],[b],[np.array([1])],[row],[.0005]*3)
    assert proof['native_mismatches']==0 and proof['uncertified_mismatches']==1

def test_fixture_monitor_cannot_run_sealed_jobs():
    from execution import execute
    from fixture_host import FixtureMonitor
    tag='outcome_FORBIDDEN';p=r.LOCAL/'requests'/(tag+'.json');r.write(p,dict(options=dict(duration=150),stageA=dict(collect=True)))
    with pytest.raises(RuntimeError,match='fixture envelope'):execute(dict(tag=tag,split='outcome'),time.monotonic()+120,FixtureMonitor(),'FIXTURE_ONLY')

def test_native_replay_calibrated_roles(tmp_path):
    import importlib.util
    from calibrated_parity import replay
    from fixture_host import FixtureMonitor
    spec=importlib.util.spec_from_file_location('stagea_parity_fixture',r.STAGEA/'test_stagea.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    model=Policy('N1').double()
    with torch.no_grad():
        for parameter in model.parameters():parameter.zero_()
        model.out.bias[3]=.2
    weights=export(model,tmp_path/'replay.json');weights['fireThresholds']=[-100,100,-100]
    classes=[];output=replay(weights,m.fixture(),fixture_monitor=FixtureMonitor(),fire_classes=classes)
    for row,actual in zip(m.fixture(),classes):
        assert actual.tolist()==[0 if u[2]!=1 else 1 for u in sorted(row['units']) if u[1]==0]
    assert output

def test_global_training_bank_cannot_change_held_out_split():
    from train import validate_index
    baseline=[dict(f,raw_file=str((r.A_LOCAL/f['raw_file']).resolve())) for f in r.read(r.A_LOCAL/'INDEX.json')['fights']]
    index=dict(stagea_index_sha256=r.sha(r.A_LOCAL/'INDEX.json'),round=0,arm_fights={a:baseline for a in r.ARMS},fights=baseline)
    validate_index(index)
    index['fights']=copy.deepcopy(baseline);index['fights'][0]['split']='validation'
    with pytest.raises(RuntimeError,match='global dataset union'):validate_index(index)

def test_round_aggregation_cannot_relabel_student_arm(monkeypatch):
    import train,dagger
    job=dict(tag='sealed',arm='N1',split='train',seed=7,panel='regular')
    completion=dict(status='DONE',job=job,ledger_sha256='hash',raw_file='raw.xz',raw_sha256='hash',frames=1)
    fight=dict(job,arm='N2',raw_file='raw.xz',raw_sha256='hash',frames=1)
    result=dict(status='DONE',round=1,ledger_sha256='hash',fights=[fight])
    monkeypatch.setattr(dagger,'check',lambda n:dict(jobs=[job]));monkeypatch.setattr(r,'sha',lambda p:'hash')
    monkeypatch.setattr(r,'read',lambda p:result if str(p).endswith('DAGGER_ROUND1.json') else completion)
    with pytest.raises(RuntimeError,match='completion drift'):train.verified_dagger(1)

def test_n2_readout_uses_recorded_phase_forcing_spacing(monkeypatch):
    import readout_run
    row=dict(stageA=True,networkKind='N2',networkState=[[1,2,0,0,0,0,.5,0,0,3,4]],labels=[],t=1.)
    second=dict(row,t=2.,networkState=[[1,4,0,0,0,0,1.,0,0,0,0]])
    monkeypatch.setattr(readout_run,'rows',lambda p:iter([row,second]))
    result=readout_run.mechanism('ignored')
    assert result['phase_samples']==2 and result['phase_abs_rate_sum']==2
    assert result['forcing_abs_sum']==1.5 and result['spacing_norm_sum']==5

def test_early_refusal_writes_invocation_readout(tmp_path,monkeypatch):
    import readout_run
    monkeypatch.setattr(r,'HERE',tmp_path)
    def refuse(round):raise RuntimeError('fixture provenance refusal')
    monkeypatch.setattr(readout_run,'check',refuse)
    with pytest.raises(RuntimeError,match='provenance refusal'):readout_run.run(1,20)
    files=list(tmp_path.glob('READOUT_STAGEB_RUN_*.json'))
    assert len(files)==1 and r.read(files[0])['status']=='REFUSED'
