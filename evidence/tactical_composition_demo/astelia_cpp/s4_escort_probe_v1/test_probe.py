"""Noncombat native preparation and synthetic provenance/measurement cases only."""
import importlib.util,gzip,pytest
from common import *
from metrics import point_for,reading

def load(name):
 spec=importlib.util.spec_from_file_location('escort_test_'+name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test_native_prepare_fixture():
 m=json.loads(BINARY.with_suffix('.build.json').read_text());argv=m['commands'][0];obj=CPP/'build/escort_fixture.o';argv=argv[:argv.index('-c')]+['-c',str(HERE/'fixture.cpp'),'-o',str(obj)];subprocess.run(argv,check=True,timeout=120)
 objects=[o for o in m['link'][1:-2] if not o.endswith('escort_v1_host.o')];exe=CPP/'build/escort_fixture';subprocess.run([m['link'][0],str(obj),*objects,'-o',str(exe)],check=True,timeout=120)
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
 exclusive(tmp_path/'a_CLAIM.json',dict(declaration_sha256=sha(tmp_path/'DECLARATION.json'),binary=dict(binary='test')))
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
 def row(arm,wins,arrival,kills,multiplicity):return dict(arm=arm,head='regular',elimination_wins=wins,mean_own_guns_lost=10,sides=[{},dict(gun_victims_per_successful_shell=multiplicity)],escort=dict(clipped_arrival_fraction=arrival,counts=dict(ranged_enemy_ranged_last_hits_lt20=kills)))
 p=row('P11',2,.1,4,1);q=row('P12',5,.5,8,1.5);r=row('P13',4,None,0,None)
 out=reading([p,q,r]);assert out[0]['clearly_above_P11'] and out[0]['arrive_and_engage'] and out[0]['spacing_lost'] is False
 assert out[1]['arrive_and_engage'] is None and out[1]['spacing_lost'] is None and not out[1]['clearly_above_P11']

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
 d=pins();assert d['arms']==['P11','P12','P13'];assert len(set(d['development_seeds']+[d['engineering_seed']]))==11
 assert d['parameters']['d_P12']==60 and d['parameters']['d_P13']==120 and d['parameters']['S_P11']==60
 assert not d['judging_ledger_read'];admit(BINARY)
