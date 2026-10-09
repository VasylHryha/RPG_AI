"""Light geometry and no-combat native inference contracts; no optimizer/fights."""
import copy,json,math,os,subprocess,sys,time
from pathlib import Path
import numpy as np
import pytest
import torch
import runtime as r
import tools
from candidates import bank,mapped_labels,nearest,MAX_AIM,MAX_MOVE
from models import Policy,initial,export
from training import forward,flat

torch.set_num_threads(1)

def frame():
    def unit(id,team,role,x,y,vx=0,vy=0,reach=180,minimum=0):return [id,team,role,x,y,vx,vy,100,100,8,60,reach,20,0,1,0,0,0,minimum,0,0,0,0]
    units=[unit(1,0,2,35,40,reach=240,minimum=75),unit(4,0,1,50,100),unit(7,1,0,220,140,20,-10),unit(9,1,1,190,155,-5,5)]
    return dict(stageA=True,t=1/30,dt=1/30,width=500,height=300,units=units,own=[[1,0,0,.4,1,100,10,False,3,.35],[4,0,0,.2,1,100,10,False,3,.3]],shells=[[.1,.2,.1,.2,.5,.3,0,1,.1]],shots=[[.1,.2,1,0,.1,3,1]],fields=[[.1,.3,.4,0,1]],casts=[[7/256,1/256,.2,.1,.3,.6,.3]],history={str(u[0]):[0]*16 for u in units},pairModes={},labels=[dict(id=id,role=role,executed=dict(goal=goal,target=7,multiplier=1,fire='automatic',aim=aim),ready=True,active=active,engineRelease=0) for id,role,goal,aim,active in ((1,'artillery',[90,60],[220,140],True),(4,'ranged',[160,180],None,False))])

@pytest.fixture(scope='session')
def tool_binary():
    out=r.HERE/'_local/light_tests';out.mkdir(parents=True,exist_ok=True);binary=out/'tools_fixture'
    subprocess.run(['nice','-n','15','/usr/bin/clang++','-std=c++17','-O0','-ffp-contract=off',str(r.HERE/'tools_fixture.cpp'),'-o',str(binary)],check=True,timeout=30,capture_output=True)
    return binary

def rpc(binary,requests):
    x=subprocess.run(['nice','-n','15',str(binary)],input='\n'.join(requests)+'\n',text=True,capture_output=True,timeout=10)
    assert x.returncode==0,x.stderr
    return [json.loads(line) for line in x.stdout.splitlines()]

def test_all_tool_twins_and_known_values(tool_binary):
    requests=['lead 10 20 4 -2 2','flight 0 0 300 400 250 .2','range -30 20 0 0 50 100 0 0 150 150','range 0 0 0 0 300 350 0 0 100 100','dodge 0 0 10 0 0 10 .5 60 -1','friend 50 50 100 50 20 100 50 30 80 0 0 150 150','cluster 3 10 0 0 10 0 40 0','splash 3 10 0 0 10 0 40 0 5 0','best 3 10 0 0 10 0 40 0 0 0 0 100 -100 -100 100 100','threat 1 0 0 0 10 0 0 0 20 2 10']
    expected=[tools.lead((10,20),(4,-2),2),2.2,tools.range_project((-30,20),(0,0),50,100,(0,0,150,150)),None,tools.dodge_spot((0,0),(10,0),(0,10),.5,60,-1),tools.behind_friend((50,50),(100,50),20,(100,50),30,80,(0,0,150,150)),[(5.,0.),(40.,0.)],2,tools.best_splash([(0,0),(10,0),(40,0)],10,(0,0),0,100,(-100,-100,100,100)),5.]
    actual=rpc(tool_binary,requests)
    for a,b in zip(actual,expected):
        if b is None:assert a is None
        else:np.testing.assert_allclose(a,b,atol=1e-9)
    assert tools.splash_coverage(actual[8],[(0,0),(10,0),(40,0)],10)==2


def test_wall_inner_band_and_empty():
    p=tools.range_project((-50,-50),(2,2),40,80,(0,0,50,50))
    assert p is not None and tools.legal(p,(2,2),40,80,(0,0,50,50))
    assert tools.range_project((0,0),(0,0),200,300,(0,0,20,20)) is None
    assert tools.cluster_centres([(0,0),(9,0),(18,0),(50,0)],10)==[(9.,0.),(50.,0.)]


def test_public_candidates_and_honest_residuals():
    row=frame();a,_=bank(row,1);changed=copy.deepcopy(row);changed['labels']=[];changed['networkState']=[[1,999]];changed['shadowLabels']=[dict(private='no leak')]
    b,_=bank(changed,1)
    for k in a:np.testing.assert_array_equal(a[k],b[k])
    assert a['aim_valid'].sum()>0 and a['move_valid'].sum()>0
    for p in a['aim_points'][a['aim_valid'].astype(bool)]:assert tools.legal(p,(35,40),75,240,(0,0,500,300))
    lab=mapped_labels(row,[1,4]);assert lab[0]['dodge'] and lab[1]['aim'] is None
    poor=nearest([1000,1000],np.asarray([[0.,0.]]),[1],24)
    assert poor['residual']==[1000.,1000.] and not poor['covered'] and not poor['representable']
    none=nearest([1,2],np.zeros((2,2)),[0,0],24);assert none['distance'] is None and not none['covered']

@pytest.fixture(scope='session')
def native_binary():
    from fixture_build import compile_fixture
    return compile_fixture(r.HERE/'_local/light_tests/replay')

@pytest.mark.parametrize('kind',list(r.ARMS))
def test_no_combat_complete_native_heads_and_memory(native_binary,kind):
    torch.manual_seed(77);model=Policy(kind).double().eval();weights=export(model,r.HERE/'_local/light_tests'/f'{kind}.json');weights['fireThresholds']=[.1,.2,.3]
    rows=[]
    for i in range(3):
        row=frame();row['t']=(i+1)/30
        row['units'][0][15]=7;row['units'][1][15]=9
        if i==2:row['units']=[u for u in row['units'] if u[0]!=9]
        rows.append(row)
    requests=[json.dumps(dict(frames=[row],**({'weights':weights} if i==0 else {}))) for i,row in enumerate(rows)]
    native=rpc(native_binary,requests);state=initial(kind,[],torch.float64);ids=[];cache=None;clock=(0,[])
    with torch.no_grad():
        for row,actual in zip(rows,native):
            y,state,ids,enemies,cache,clock,_=forward(model,row,state,ids,cache,clock)
            predicted=flat(y).numpy();observed=np.asarray(actual['outputs'][0]);assert actual['combat_steps']==0
            np.testing.assert_allclose(observed,predicted,atol=1e-8,rtol=0)
            from calibration import fire_classes
            np.testing.assert_array_equal(actual['fireClasses'][0],fire_classes(predicted[:,3:6],[2,1],weights['fireThresholds']))
            assert y['aim_residual'].abs().max()<=12 and y['move_residual'].abs().max()<=24


def test_categorical_residual_loss_and_source_scope():
    from loss import install
    import training
    balance={role:dict(weights=[1,1]) for role in ('melee','ranged','artillery')};install(balance)
    m=Policy('N2').float();row=frame()
    y,*_=forward(m,row,initial('N2',[]),[],None,(0,[]));loss,heads=training.objective(y,row,[1,4],[7,9]);assert torch.isfinite(loss)
    assert {'aim_choice','move_choice','aim_residual','move_residual','target','fire'}<=heads.keys()
    loss.backward();assert m.move_choice.weight.grad is not None and m.aim_offset.weight.grad is not None
    assert not any(Path(p).suffix=='.md' for p in r.sources())
    historical=r.read(r.HERE/'PROTECTED_SOURCE_BASELINE.json')
    protected=r.read(r.HERE/'PROTECTED_SOURCE_BASELINE_HEAD_0040.json')['files']
    assert set(protected)==set(historical)
    assert all(r.sha(r.ARMY/p)==h for p,h in protected.items())


def test_projection_calibration_and_resume_identity(tmp_path,monkeypatch):
    from train import project
    from training_control import atomic_checkpoint,last_checkpoint
    from calibration import choose
    p=project({'N1':dict(epoch_seconds=2,tail_seconds=3),'N2':dict(epoch_seconds=4,tail_seconds=1)},10,2)
    assert p['projected_seconds']==1.2*41
    result=choose([0,0,1,2],[True,False,True,False],[True]*4);assert result['tp']+result['fn']==2
    atomic_checkpoint(tmp_path/'epoch_0001.pt',dict(epoch=1,budget_sha256='a'))
    assert last_checkpoint(tmp_path,'a')['epoch']==1
    with pytest.raises(RuntimeError):last_checkpoint(tmp_path,'b')


def test_variant_native_seams_and_near_tie_head_scope():
    from build import prepare_sources
    out=r.HERE/'_local/light_tests/seams';out.mkdir(parents=True,exist_ok=True);prepare_sources(out)
    assert 'learnedDodge)?Reaction{}' in (out/'react.cpp').read_text()
    assert 'if(s.dodge!=Dodge::None && s.dashReady<=w.time)' in (out/'react_rules.cpp').read_text()
    assert 'learnedDodge' not in (out/'react_rules.cpp').read_text()
    from parity import compare,categories
    x=np.zeros((1,11+MAX_AIM+MAX_MOVE+4));x[:,10]=2;x[:,11]=3;x[:,11+MAX_AIM]=4;y=x.copy();y[:,11]=2;y[:,12]=3
    assert categories(x).tolist()==[[0,0,0,0]]
    detail=compare([x],[y],near_ties=True);assert detail['categorical_mismatches']==1 and detail['mismatches'][0]['head']=='aim_choice' and detail['uncertified_mismatches']==1


def test_no_enemy_or_own_and_undefined_aim():
    row=frame();row['units']=[u for u in row['units'] if u[1]==0]
    model=Policy('N1').double();y,*_=forward(model,row,initial('N1',[],torch.float64),[],None,(0,[]));assert y['target'].shape==(2,1)
    row['units']=[];row['own']=[]
    y,*_=forward(model,row,initial('N1',[],torch.float64),[],None,(0,[]));assert flat(y).shape==(0,11+MAX_AIM+MAX_MOVE+4)
    a,_=bank(frame(),1);assert np.isfinite(a['aim_features']).all()


def test_extreme_logits_cannot_choose_padding(native_binary):
    m=Policy('N1').double().eval()
    with torch.no_grad():
        for head in (m.move_choice,m.aim_choice):head.weight.zero_();head.bias.zero_();head.bias[:11]=-1e9
    row=frame();weights=export(m,r.HERE/'_local/light_tests/extreme.json')
    result=rpc(native_binary,[json.dumps(dict(frames=[row],weights=weights))])[0]
    with torch.no_grad():y,*_=forward(m,row,initial('N1',[],torch.float64),[],None,(0,[]))
    for name in ('aim','move'):
        choice=y[name+'_logits'].argmax(-1)
        assert all(y[name+'_valid'][i,int(j)] for i,j in enumerate(choice))
    np.testing.assert_allclose(result['outputs'][0],flat(y).numpy(),atol=1e-8,rtol=0)


def test_empty_required_aim_stops_native_and_training_but_audits(native_binary):
    row=frame();row['units'][0][18]=1000;row['units'][0][11]=1500
    with pytest.raises(ValueError,match='empty required'):bank(row,1)
    label=mapped_labels(row,[1])[0]['aim'];assert label['distance'] is None and not label['covered']
    from coverage import accumulate
    counts={};accumulate(counts,row);assert counts['artillery','aim','all']['no_candidates']==1
    weights=export(Policy('N1').double(),r.HERE/'_local/light_tests/empty.json')
    x=subprocess.run([str(native_binary)],input=json.dumps(dict(frames=[row],weights=weights))+'\n',text=True,capture_output=True,timeout=10)
    assert x.returncode==1 and 'empty required artillery aim bank' in x.stderr


def test_witness_scoped_splash_tie(tool_binary):
    p=tools.best_splash([(100,0)],10,(0,0),0,200,(-300,-300,300,300))
    # Count is exact; nearest tie is intentionally limited to arrangement witnesses.
    assert p==(100,0) and tools.splash_coverage(p,[(100,0)],10)==1
    assert tools.splash_coverage((90,0),[(100,0)],10)==1
    native=rpc(tool_binary,['best 1 10 100 0 0 0 0 200 -300 -300 300 300'])[0]
    np.testing.assert_array_equal(native,p)


def test_nonfinite_output_and_direct_bank_envelopes(tool_binary):
    for op in ('invalid_flight','invalid_range','overflow_lead','bad_bank'):
        x=subprocess.run([str(tool_binary)],input=op+'\n',text=True,capture_output=True,timeout=10)
        assert x.returncode==1 and x.stderr
    with pytest.raises(ValueError):tools.flight_time((0,0),(1,1),float('nan'))
    with pytest.raises(ValueError):tools.range_project((float('inf'),0),(0,0),0,10,(0,0,20,20))
    with pytest.raises(ValueError):tools.lead((1e308,0),(1e308,0),2)
    row=frame();row['shells'][0].append(1)
    with pytest.raises(ValueError,match='schema'):bank(row,1)
    row=frame();row['width']=float('nan')
    with pytest.raises(ValueError,match='nonfinite'):bank(row,1)
    row=frame();row['units']=[];row['own']=[]
    for i in range(1,66):
        u=frame()['units'][1][:];u[0]=i;row['units'].append(u);s=frame()['own'][1][:];s[0]=i;row['own'].append(s)
    with pytest.raises(ValueError,match='entity envelope'):bank(row,1)


def test_actual_warm_start_initialization_survives_resume(tmp_path,monkeypatch):
    import enable_dodge,initialization
    m=Policy('N2').float()
    with torch.no_grad():m.law.copy_(torch.tensor([.2,.3,.4,.5,.6,.7]))
    monkeypatch.setattr(r,'VARIANT','learned_dodge');monkeypatch.setattr(enable_dodge,'OFF',tmp_path)
    r.write(tmp_path/'DODGE_READY.json',dict(fixture_only=True))
    parent=dict(checkpoints={'N2':dict(path='synthetic_parent.pt',sha256='fixture')})
    monkeypatch.setattr(enable_dodge,'check',lambda:parent)
    value=initialization.capture(m);assert value['law']==pytest.approx([.2,.3,.4,.5,.6,.7]) and value['K']!=1
    assert value['warm_start']['checkpoint']['sha256']=='fixture'
    saved=dict(initialization=value);assert initialization.resumed(saved,value)==value
    drift=copy.deepcopy(value);drift['warm_start']['checkpoint']['sha256']='changed'
    with pytest.raises(RuntimeError,match='identity drift'):initialization.resumed(saved,drift)


def test_dodge_parent_gate_rejects_disconnected_look_and_replaced_checkpoint(tmp_path,monkeypatch):
    import enable_dodge as d
    monkeypatch.setattr(d,'ON',tmp_path);monkeypatch.setattr(r,'ARMS',('N2',))
    local=tmp_path/'round1';training=local/'training';training.mkdir(parents=True)
    r.write(local/'INDEX.json',dict(fixture_only=True));r.write(local/'TRAIN_BUDGET.json',dict(fixture_only=True))
    budget=r.sha(local/'TRAIN_BUDGET.json')
    for name in ('N2.pt','N2.weights.json','N2.calibration.json'):(training/name).write_text('synthetic fixture')
    outcome=dict(status='FIT_CALIBRATED_PARITY_PENDING',budget_sha256=budget,checkpoint_sha256=r.sha(training/'N2.pt'),export_sha256=r.sha(training/'N2.weights.json'),calibration_sha256=r.sha(training/'N2.calibration.json'))
    r.write(training/'N2.outcome.json',outcome)
    parity=dict(status='PASS',budget_sha256=budget,exports={'N2':r.sha(training/'N2.weights.json')});r.write(local/'PARITY_STAGEB2.json',parity)
    jobs=[dict(tag=f'fixture_{panel}_{arm}_{i}',panel=panel,arm=arm,index=i) for panel in ('regular','C3') for arm in ('N2','N2_network_only','O','T') for i in range(50)]
    ledger=dict(variant='react_on',jobs=jobs,parity_sha256=r.sha(local/'PARITY_STAGEB2.json'));path=tmp_path/'OUTCOME_LEDGER_ROUND1.json';r.write(path,ledger)
    look=dict(complete=True,harm_stop=False,look=50,round=1,ledger_sha256='disconnected',report=dict(panels={p:dict(arms={'N2':dict(wins=50)}) for p in ('regular','C3')}))
    r.write(tmp_path/'LOOK_STAGEB2_R1_50.json',look)
    with pytest.raises(RuntimeError,match='disconnected'):d.bindings(1,ledger,parity)
    look['ledger_sha256']=r.sha(path);r.write(tmp_path/'LOOK_STAGEB2_R1_50.json',look)
    raw=tmp_path/'raw';raw.mkdir();(raw/'fixture.dat').write_text('synthetic no-combat fixture')
    for job in jobs:r.write(raw/(job['tag']+'_COMPLETE.json'),dict(fixture_only=True,status='DONE',job=job,ledger_sha256=r.sha(path),raw_file='raw/fixture.dat',raw_sha256=r.sha(raw/'fixture.dat'),stats=dict(win=True,own_deaths=10,enemy_kills=50)))
    valid=d.bindings(1,ledger,parity);assert valid['schema']==2
    (training/'N2.pt').write_text('replaced synthetic parent')
    with pytest.raises(RuntimeError,match='checkpoint/export/fit mismatch'):d.bindings(1,ledger,parity)


def test_middle_collinear_lead_is_selectable_python_and_native(native_binary):
    row=frame();own=row['units'][0];own[3:5]=[40,100];own[18]=0;own[11]=400
    enemies=[]
    for uid,x in ((7,140),(9,240),(11,340)):
        u=row['units'][2][:];u[0]=uid;u[3:7]=[x,100,0,0];enemies.append(u)
    row['units']=[own,*enemies];row['own']=row['own'][:1];row['shells']=[];row['shots']=[];row['fields']=[];row['casts']=[]
    m=Policy('N1').double()
    with torch.no_grad():
        for p in m.parameters():p.zero_()
        # Explicit nonlinear interval score: tanh(dx-1.5)-tanh(dx-2.5).
        m.aim_choice.bias[1]=100
        m.aim_hidden.weight[0,11]=10;m.aim_hidden.bias[0]=-15
        m.aim_hidden.weight[1,11]=10;m.aim_hidden.bias[1]=-25
        m.aim_score.weight[0,0]=1;m.aim_score.weight[0,1]=-1
        y,*_=forward(m,row,initial('N1',[],torch.float64),[],None,(0,[]))
    np.testing.assert_allclose(y['aim'][0].numpy()*[500,300],[240,100],atol=1e-8)
    arrays,items=bank(row,1);choice=int(y['aim_logits'][0].argmax());assert items['aim'][choice][2:]==(1,2)
    weights=export(m,r.HERE/'_local/light_tests/middle.json')
    native=rpc(native_binary,[json.dumps(dict(frames=[row],weights=weights))])[0]
    np.testing.assert_allclose(native['outputs'][0],flat(y).numpy(),atol=1e-8,rtol=0)


def test_candidate_identity_binding_and_nonlinear_gradients():
    row=frame();arrays,items=bank(row,1)
    assert [(c[2],c[3]) for c in items['aim'][1:5]]==[(0,2),(1,2),(0,3),(1,3)]
    assert any(c[3]>=len(row['units']) for c in items['move'])
    m=Policy('N1').float();y,*_=forward(m,row,initial('N1',[]),[],None,(0,[]))
    y['aim_logits'][0,:int(arrays['aim_valid'].sum())].sum().backward()
    assert m.aim_source.weight.grad.abs().sum()>0 and m.aim_hidden.weight.grad.abs().sum()>0


def test_exact_dodge_geometry_and_hazard_features_native_twin(native_binary):
    row=frame();row['units'][0][3:5]=[200,150];row['units'][0][18]=0;row['units'][0][11]=300
    row['shells']=[[.4,.5,.4,.5,.5,.3,0,1,.1]]
    row['shots']=[[.3,.5,1,0,.2,3,1]];row['fields']=[[.36,.5,.5,0,1]];row['casts']=[]
    arrays,items=bank(row,1);dodge=[c[0] for c in items['move'] if c[2]==10]
    assert (200,120) in dodge and (200,180) in dodge and (240,150) in dodge
    extent=60*(.5+.1)
    for fraction in (1.,.6):
        for j in range(16):
            p=np.array([200,150])+extent*fraction*np.array([math.cos(j*math.pi/8),math.sin(j*math.pi/8)])
            assert min(np.linalg.norm(p-np.array(q)) for q in dodge)<1e-8
    assert len(dodge)==35 # two shots, one field, one shared 32-point ring
    assert arrays['move_features'][0,16:18].tolist()==[1,.5]
    native=rpc(native_binary,[json.dumps(dict(candidateFrame=row,id=1))])[0]
    for name in ('aim','move'):
        assert len(native[name])==len(items[name])
        for actual,(p,f,typ,source) in zip(native[name],items[name]):
            np.testing.assert_allclose(actual['point'],p,atol=1e-8)
            index=items[name].index((p,f,typ,source))
            np.testing.assert_allclose(actual['features'],arrays[name+'_features'][index],atol=1e-8)
            assert (actual['type'],actual['source'])==(typ,source)
    row['shells'][0][7]=0;a,items=bank(row,1)
    assert a['move_features'][:,16].sum()==0 and len([c for c in items['move'] if c[2]==10])==3


def test_melee_behind_friend_and_deduplicated_approach():
    row=frame();row['units'][0][2]=0;row['units'][0][18]=0;row['units'][0][11]=15
    arrays,items=bank(row,1);behind=next(c[0] for c in items['move'] if c[2]==6)
    centre=np.mean([u[3:5] for u in row['units'] if u[1]==1],axis=0)
    assert np.linalg.norm(np.array(behind)-centre)>15
    for band in (c for c in items['move'] if c[2]==5):
        assert all(np.linalg.norm(np.array(band[0])-np.array(c[0]))>1e-8 for c in items['move'] if c[2]==7 and c[3]==band[3])
    assert MAX_MOVE==1280


def test_smoothed_public_velocity_and_lead_native_twin(native_binary):
    from public_velocity import attach
    rows=[frame(),frame()];rows[1]['t']=2/30
    actual=list(attach(rows));expected=np.array([20.,-10.])*(1-(1-1/30)**2)
    np.testing.assert_allclose(actual[1]['longVelocity']['7'],expected)
    assert actual[1]['longVelocity']['7']!=rows[1]['units'][2][5:7]
    row=actual[1];arrays,items=bank(row,1)
    native=rpc(native_binary,[json.dumps(dict(candidateFrame=row,id=1))])[0]
    for name in ('aim','move'):
        for i,(c,actual) in enumerate(zip(items[name],native[name])):
            np.testing.assert_allclose(c[0],actual['point'],atol=1e-8)
            np.testing.assert_allclose(arrays[name+'_features'][i],actual['features'],atol=1e-8)


def test_physical_tick_refresh_sees_new_hazard(native_binary):
    m=Policy('N1').double();first=frame();first['shells']=[];second=frame();second['t']=2/30
    with torch.no_grad():
        _,state,ids,_,cache,clock,_=forward(m,first,initial('N1',[],torch.float64),[],None,(0,[]))
        y,*tail=forward(m,second,state,ids,cache,clock)
    assert tail[-1] is True
    native=rpc(native_binary,[json.dumps(dict(frames=[first],weights=export(m,r.HERE/'_local/light_tests/refresh.json'))),json.dumps(dict(frames=[second]))])
    np.testing.assert_allclose(native[1]['outputs'][0],flat(y).numpy(),atol=1e-8,rtol=0)


def test_coverage_threshold_rejects_low_or_missing_and_matches_drift(monkeypatch):
    from coverage_gate import THRESHOLDS,admission,require
    from coverage import accumulate,report
    table={f'{role}:{head}:{category}':dict(rows=10,no_candidates=0,coverage=threshold,bounded_residual_coverage=threshold) for role in ('melee','ranged','artillery') for head in (('move','aim') if role=='artillery' else ('move',)) for category,threshold in THRESHOLDS.items()}
    receipt=dict(thresholds=THRESHOLDS,fit_target_coverage={'train:N2':table})
    assert require(receipt,['N2'])['passed']
    table['artillery:aim:all']['coverage']=0
    with pytest.raises(RuntimeError,match='artillery:aim:all'):require(receipt,['N2'])
    del table['melee:move:dodge']
    assert any(c['rows']==0 for c in admission(receipt,['N2'])['failed'])
    row=frame();arrays,_=bank(row,1);row['labels'][0]['executed']['goal']=(arrays['move_points'][0]+[100,100]).tolist()
    raw={};adjusted={};accumulate(raw,row);accumulate(adjusted,row,[[100,100],[0,0]])
    assert report(adjusted)['artillery:move:dodge']['coverage']==1 and mapped_labels(row,[1],[[100,100]])[0]['move']['distance']==0
    # train admission invokes the numeric gate before timing/worker admission.
    import train
    monkeypatch.setattr(r,'read',lambda p:dict(receipt,status='DONE',index_sha256='idx',sources={}))
    monkeypatch.setattr(r,'sources',lambda:{})
    monkeypatch.setattr(r,'sha',lambda p:'idx')
    monkeypatch.setattr(r,'ARMS',('N2',))
    with pytest.raises(RuntimeError,match='coverage admission refused'):train.coverage_admission(r.LOCAL)


def test_hazard_damage_and_impact_escape_with_death_and_censor():
    from dodge_metrics import DodgeMetrics,aggregate
    row=frame();row['units'][0][3:5]=[200,150];row['shells']=[[.4,.5,.4,.5,.5,.3,0,1,.1]];row['casts']=[];row['shots']=[];row['fields']=[]
    m=DodgeMetrics();m.observe(row)
    observer=dict(observerV1=True,t=row['t']+.5,units=[[1,0,2,280,150,100,8]],damage=[dict(targetTeam=0,targetRole='artillery',hazardType=kind,dealt=value) for kind,value in (('shell',10),('shot',4),('melee',3))])
    m.observe(observer);report=m.finish();c=report['dodge_escape']['artillery']['shell']
    assert c['evaluated']==1 and c['escaped']==1 and c['escape_rate']==1
    assert report['damage_taken_by_role_hazard']['artillery']['shell']==10 and report['damage_taken_by_role_hazard']['artillery']['cast']==0
    assert aggregate([report])['dodge_escape']['artillery']['shell']['escape_rate']==1
    dead=DodgeMetrics();dead.observe(row);dead.observe(dict(observer,units=[],damage=[]));c=dead.finish()['dodge_escape']['artillery']['shell'];assert c['dead']==1 and c['escaped']==0
    pending=DodgeMetrics();pending.observe(row);c=pending.finish()['dodge_escape']['artillery']['shell'];assert c['censored']==1 and c['escape_rate'] is None


def test_b2_dagger_look_cap_and_native_metric_seams():
    from build import prepare_sources
    out=r.HERE/'_local/light_tests/seams';prepare_sources(out)
    assert '"hazardType",stageb2::damageKinds.at(damageIndex++)' in (out/'lean_host.cpp').read_text()
    assert 'DamageScope damageScope("shell")' in (out/'react_combat.cpp').read_text()
    for name in ('dagger.py','readout_run.py'):
        source=(r.HERE/name).read_text();assert 'cap=training_cap(r.HERE)' in source and 'cap=r.collect.a0().owner_cap()' not in source and 'deadline=TrainingDeadline(' in source
    record=r.read((r.A_LOCAL/'build/tactics_react_host_stagea').with_suffix('.build.json'))
    raw=record['commands'][0];includes=[a for a in raw if a.startswith('-I')]
    subprocess.run(['nice','-n','15',raw[0],'-std=c++17','-fsyntax-only','-I'+str(out),'-I'+str(r.HERE),*includes,*[str(out/name) for name in ('react.cpp','react_combat.cpp','lean_observer.cpp','lean_host.cpp')],str(r.HERE/'shadow.cpp')],check=True,capture_output=True,text=True,timeout=45)


def test_factored_scorer_matches_unfactored_and_ignores_padding():
    row=frame();model=Policy('N1').double();x,ids,_=r.data.pack(row,'N1')
    encoded=model.encode(torch.as_tensor(x['tokens']));h=torch.randn((len(ids),64),dtype=torch.float64)
    for name in ('aim','move'):
        features=torch.as_tensor(x[name+'_features']);sources=torch.as_tensor(x[name+'_sources']);valid=torch.as_tensor(x[name+'_valid'])>=.5
        i,j=valid.nonzero(as_tuple=True);source=sources[i,j];embedding=encoded[source.clamp_min(0)]*(source>=0)[:,None]
        layer=getattr(model,name+'_hidden');joined=torch.cat((features[i,j],h[i],embedding),-1)
        exact=layer(joined)
        width=features.shape[-1]
        factored=torch.nn.functional.linear(features[i,j],layer.weight[:,:width],layer.bias)+torch.nn.functional.linear(h,layer.weight[:,width:width+64])[i]+torch.nn.functional.linear(encoded,layer.weight[:,width+64:])[source.clamp_min(0)]*(source>=0)[:,None]
        torch.testing.assert_close(exact,factored,atol=1e-12,rtol=0)
        assert len(i)==int(valid.sum()) and len(i)<valid.numel()
