"""Noncombat native preparation and synthetic provenance/measurement cases only."""
import importlib.util,gzip,pytest
from common import *
from metrics import point_for,reading

def load(name):
 spec=importlib.util.spec_from_file_location('escort_test_'+name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test_native_prepare_fixture():
 m=json.loads(BINARY.with_suffix('.build.json').read_text());argv=m['commands'][0];obj=CPP/'build/escort_v2_fixture.o';argv=argv[:argv.index('-c')]+['-c',str(HERE/'fixture.cpp'),'-o',str(obj)];subprocess.run(argv,check=True,timeout=120)
 objects=[o for o in m['link'][1:-2] if not o.endswith('escort_v2_host.o')];exe=CPP/'build/escort_v2_fixture';subprocess.run([m['link'][0],str(obj),*objects,'-o',str(exe)],check=True,timeout=120)
 r=subprocess.run([str(exe)],capture_output=True,text=True,check=True,timeout=30);(HERE/'FIXTURE.log').write_text(r.stdout)

def test_pgrep_fail_closed_and_receipts(monkeypatch,tmp_path):
 import common
 monkeypatch.setattr(common,'HERE',tmp_path)
 for rc,out,err in ((3,'','Cannot get process list'),(1,'','sysmon error'),(0,'12 python pilot rev711_diag','')):
  monkeypatch.setattr(common.subprocess,'run',lambda *a,**k:subprocess.CompletedProcess([],rc,out,err))
  with pytest.raises(RuntimeError):common.pilot_gate(wait=False)
 monkeypatch.setattr(common.subprocess,'run',lambda *a,**k:subprocess.CompletedProcess([],1,'',''));common.pilot_gate()
 assert len(list(tmp_path.glob('PILOT_GATE_*.json')))==4

def test_receipt_skip_and_ambiguous_refusal(monkeypatch,tmp_path):
 import run
 monkeypatch.setattr(run,'RAW',tmp_path);monkeypatch.setattr(run,'HERE',tmp_path);monkeypatch.setattr(run,'admit',lambda p:dict(binary='test'))
 req=dict(options=dict(seed=1));write(tmp_path/'DECLARATION.json',{})
 assert run.verified('a',req) is None
 gate=tmp_path/'gate.json';write(gate,dict(status='CLEAR',declaration_sha256=sha(tmp_path/'DECLARATION.json'),binary=dict(binary='test')))
 exclusive(tmp_path/'a_CLAIM.json',dict(declaration_sha256=sha(tmp_path/'DECLARATION.json'),binary=dict(binary='test'),request_sha256=__import__('hashlib').sha256((json.dumps(req,indent=2)+'\n').encode()).hexdigest(),gate=dict(path='gate.json',sha256=sha(gate))))
 with pytest.raises(AssertionError,match='ambiguous'):run.verified('a',req)
 exclusive(tmp_path/'a_request.json',req);(tmp_path/'a.jsonl.gz').write_bytes(b'synthetic');(tmp_path/'a_stderr.log').write_text('{}')
 r=dict(claim_sha256=sha(tmp_path/'a_CLAIM.json'),binary=dict(binary='test'),request_sha256=sha(tmp_path/'a_request.json'),raw_bytes=9,raw_sha256=sha(tmp_path/'a.jsonl.gz'),stderr_sha256=sha(tmp_path/'a_stderr.log'),summary=dict(controllerStatus='completed',controllerFailures=[0,0]))
 exclusive(tmp_path/'a_COMPLETE.json',r);assert run.verified('a',req)==r
 (tmp_path/'a.jsonl.gz').write_bytes(b'tampered')
 with pytest.raises(AssertionError):run.verified('a',req)

def test_independent_oracle_zero_and_ties():
 u=[3,0,1,500,400,100,9,259,0];own=[[2,0,2,500,400,100,10,320,0]];enemy=[[12,1,2,400,400,100,10,320,0],[11,1,2,600,400,100,10,320,0]]
 p=point_for(u,own,enemy,[],60,1400,800);assert p['direction']==3 and p['raw']==[560,400]
 enemy=[[11,1,2,500,400,100,10,320,0]];assert point_for(u,own,enemy,[],60,1400,800)['direction']==0

def test_exact_thresholds_and_null_readings():
 def row(arm,wins,multiplicity):return dict(arm=arm,head='regular',elimination_wins=wins,sides=[{},dict(gun_victims_per_successful_shell=multiplicity)])
 out=reading([row('P12',5,1),row('P14',8,1.5),row('P15',7,None)])
 assert out[0]['clearly_above_P12'] and out[0]['spacing_lost'] is False and not out[0]['observed_owner_criterion']
 assert out[1]['spacing_lost'] is None and not out[1]['clearly_above_P12']
 out=reading([row('P12',9,1),row('P14',11,1),row('P15',12,1)])
 assert not out[0]['clearly_above_P12'] and out[0]['observed_owner_criterion'] and out[1]['clearly_above_P12']

def test_synthetic_arrival_damage_and_clocks(monkeypatch,tmp_path):
 a=load('analyze');folder=tmp_path/'raw';folder.mkdir();monkeypatch.setattr(a,'HERE',tmp_path)
 gun=[1,0,2,500,400,100,10,320,0];r=[2,0,1,540,400,100,9,259,0];e=[11,1,2,900,400,100,10,320,0];er=[12,1,1,778,400,100,9,259,0]
 initial=dict(observerV1=True,step=0,t=0,units=[gun,r,e,er],damage=[],actions=[])
 post=dict(observerV1=True,step=1,t=1/30,units=[gun,[*r[:3],560,400,*r[5:]],e,er],damage=[],actions=[[2,0,12,560,400,1,0,0,True]])
 point=dict(id=2,gun=1,threat=12,direction=1,raw=[560,400],clipped=[560,400],baseTarget=12,base=[550,400,1,0,12,False],command=[560,400,1,0,12,False])
 audit=dict(escortProbe=True,step=1,t=1/30,prepareTime=0,prepare=[gun,r,e,er],points=[point],dose=60,width=1400,height=800,applied=True,accepted=True)
 terminal=dict(controllerStatus='completed',t=1/30);fight=dict(id='fixture',summary=terminal)
 with gzip.open(folder/'fixture.jsonl.gz','wt') as f:
  for row in (initial,post,audit,terminal):f.write(json.dumps(row)+'\n')
 g=a.escort_geometry(fight);assert g['counts']['prepare_living_ranged_ticks']==1 and g['counts']['raw_arrival_ticks']==1 and g['counts']['first_arrival_units']==1
 assert g['values']['actual_displacement']==[20] and g['counts']['target_opportunity_ticks']==1 and g['counts']['threat_selected_ticks']==1
 # Removed post ranged centre remains in arrival denominator, unavailable and never arrived.
 post['units']=[gun,e,er]
 with gzip.open(folder/'fixture.jsonl.gz','wt') as f:
  for row in (initial,post,audit,terminal):f.write(json.dumps(row)+'\n')
 g=a.escort_geometry(fight);assert g['counts']['arrival_unavailable_ticks']==1 and g['counts']['clipped_arrival_ticks']==0 and g['counts']['first_arrival_censored_units']==1

def test_stage_failure_budget(monkeypatch,tmp_path):
 import common
 monkeypatch.setattr(common,'HERE',tmp_path)
 @common.stage('failure',.01)
 def work():time.sleep(.1)
 with pytest.raises(TimeoutError):work()
 r=json.loads(next(tmp_path.glob('STAGE_failure_*.json')).read_text());assert r['status']=='STOP' and r['awake_seconds']>0 and r['utc_start'] and r['utc_end']

def test_pins_and_catalog():
 d=pins();assert d['arms']==['P12','P14','P15'];assert len(set(d['development_seeds']+[d['engineering_seed']]))==11
 assert d['parameters']['d_P12']==60 and d['parameters']['S_P15']==58 and d['parameters']['S_P11']==60
 assert not d['judging_ledger_read'];admit(BINARY)

def test_shell_multiplicity_and_ambiguity():
 from metrics import ShellAudit,shell_summary
 guns=[1,0,2,0,0,100,10,320,0];r=[2,0,1,0,0,100,9,259,0];r2=[3,0,1,0,0,100,9,259,0];e=[11,1,2,0,0,100,10,320,0]
 a=ShellAudit();a.observe(dict(t=0,units=[guns,r,r2,e],damage=[]))
 launch=[11,2,1,0,0,1/30,2/30,40,False,False]
 a.observe(dict(t=1/30,launches=[launch],damage=[]))
 def damage(uid,hp):return dict(source=11,sourceTeam=1,sourceRole='artillery',target=uid,targetTeam=0,targetRole='ranged',dealt=hp,t=2/30)
 a.observe(dict(t=2/30,launches=[],damage=[damage(2,8),damage(2,4),damage(3,10)]))
 result=shell_summary(a.counts());assert result['own_ranged_victims_per_successful_enemy_escort_targeted_shell']==2
 assert result['counts']['escort_targeted_own_ranged_hp']==22
 assert shell_summary({})['own_ranged_victims_per_successful_enemy_escort_targeted_shell'] is None
 b=ShellAudit();b.observe(dict(t=0,units=[guns,r,r2,e],damage=[]));b.observe(dict(t=1/30,launches=[launch,launch],damage=[]))
 with pytest.raises(AssertionError,match='ambiguous'):b.observe(dict(t=2/30,launches=[],damage=[damage(2,8)]))

def test_exact_survival_event_boundary_and_terminal_hold():
 from metrics import gun_curve
 initial={1:[1,0,2],2:[2,0,2],3:[3,0,1]}
 c=gun_curve(initial,[dict(target=1,t=10),dict(target=3,t=5)])
 assert c==[dict(t=t,alive=1) for t in (10,20,30,45,60)]

def test_spacing_oracle_and_target_boundaries():
 from metrics import shift_for,target_for
 r=[2,0,1,560,400,100,9,259,0];other=[3,0,1,560,400,100,9,259,0]
 assert shift_for(r,[r,other])==[-58,0] and shift_for(other,[other,r])==[58,0]
 other[3]=618;assert shift_for(r,[r,other])==[0,0]
 own=[[1,0,2,0,400,100,10,320,0],[4,0,2,1000,400,100,10,320,0]]
 er=[12,1,1,837,400,100,9,259,0]
 assert target_for(r,own,[er])==12;er[3]=837.0001;assert target_for(r,own,[er])==0

def test_new_raw_file_without_completion_is_ambiguous(monkeypatch,tmp_path):
 import run
 monkeypatch.setattr(run,'RAW',tmp_path)
 (tmp_path/'fight_request.json').write_text('{}')
 with pytest.raises(AssertionError,match='ambiguous'):run.verified('fight',{})

@pytest.mark.parametrize('arm',[14,15])
def test_overlay_analysis_matches_shifted_goal_and_target_only(monkeypatch,tmp_path,arm):
 a=load('analyze');folder=tmp_path/'raw';folder.mkdir();monkeypatch.setattr(a,'HERE',tmp_path)
 gun=[1,0,2,500,400,100,10,320,0];ours=[[2,0,1,540,400,100,9,259,0],[3,0,1,540,400,100,9,259,0]]
 enemy=[11,1,2,900,400,100,10,320,0];er=[12,1,1,778,400,100,9,259,0];prepare=[gun,*ours,enemy,er]
 initial=dict(observerV1=True,step=0,t=10-1/30,units=prepare,damage=[],actions=[])
 points=[];actions=[];postunits=[gun,enemy,er]
 for u in ours:
  x=560 if arm==14 else (502 if u[0]==2 else 618);target=12 if arm==14 else 0
  base=[550,400,1,0,0,False];p12=[560,400,1,0,0,False];command=[x,400,1,0,target,False]
  points.append(dict(id=u[0],gun=1,threat=12,direction=1,raw=[x,400],clipped=[x,400],p12Raw=[560,400],p12Clipped=[560,400],p12=p12,baseTarget=0,base=base,command=command))
  actions.append([u[0],0,target,x,400,1,0,0,True]);postunits.append([*u[:3],x,400,*u[5:]])
 post=dict(observerV1=True,step=1,t=10,units=postunits,damage=[],actions=actions)
 audit=dict(escortProbe=True,arm=arm,step=1,t=10,prepareTime=10-1/30,prepare=prepare,points=points,dose=60,width=1400,height=800,applied=True,accepted=True)
 terminal=dict(controllerStatus='completed',t=10);fight=dict(id='overlay',summary=terminal)
 with gzip.open(folder/'overlay.jsonl.gz','wt') as f:
  for row in (initial,post,audit,terminal):f.write(json.dumps(row)+'\n')
 e=a.escort_geometry(fight);q=a.escort_summary(e['counts'],e['values'],e['gun_hp_loss_bins'])
 assert q['clipped_arrival_fraction']==1 and q['window_threat_selection'][0]['opportunities']==2
 assert q['p12_clipped_anchor_arrival_fraction']==(1 if arm==14 else 0)
 assert q['window_threat_selection'][0]['fraction']==(1 if arm==14 else 0)
 assert e['values']['realized_ranged_to_ranged_nearest_10_20']==([0,0] if arm==14 else [116,116])
