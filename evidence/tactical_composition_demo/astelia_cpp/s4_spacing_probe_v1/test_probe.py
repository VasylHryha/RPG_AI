"""Focused preparation checks. No world steps or combat are performed."""
import importlib.util,json,pathlib,subprocess,sys
from common import *
sys.path.insert(0,str(CPP));from build_admission import admit

def test_native_prepare_fixture():
 m=json.loads(BINARY.with_suffix('.build.json').read_text());argv=m['commands'][0];argv=argv[:argv.index('-c')]+['-c',str(HERE/'fixture.cpp'),'-o',str(CPP/'build/spacing_fixture.o')];subprocess.run(argv,check=True)
 objects=[o for o in m['link'][1:-2] if not o.endswith('spacing_v1_host.o')];exe=CPP/'build/spacing_fixture';subprocess.run([m['link'][0],str(CPP/'build/spacing_fixture.o'),*objects,'-o',str(exe)],check=True);r=subprocess.run([str(exe)],capture_output=True,text=True,check=True);(HERE/'FIXTURE.log').write_text(r.stdout)
def test_process_gate_fails_closed(monkeypatch,tmp_path):
 import common
 monkeypatch.setattr(common,'HERE',tmp_path)
 for result in (subprocess.CompletedProcess([],3,'','Cannot get process list'),subprocess.CompletedProcess([],1,'','sysmon error'),subprocess.CompletedProcess([],0,'123 python -m rev711_diag.pilot','')):
  monkeypatch.setattr(common.subprocess,'run',lambda *a,**k:result)
  try:common.pilot_gate();assert False,'must refuse combat'
  except RuntimeError:pass
 monkeypatch.setattr(common.subprocess,'run',lambda *a,**k:subprocess.CompletedProcess([],1,'',''));common.pilot_gate()
def test_quantile_shell_denominators_and_reading():
 spec=importlib.util.spec_from_file_location('spacing_analysis',HERE/'analyze.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
 assert a.quantile([], .1) is None and a.quantile([0,10],.1)==1
 s=a.side({'gun_launches':4,'gun_launches_hit_any_gun':2,'gun_target_shell_gun_victims':6,'gun_target_shell_gun_damage':80,'other_target_shell_gun_damage':20})
 assert s['gun_victims_per_successful_shell']==3 and s['artillery_hp_to_opposing_guns']==100
 p=dict(arm='P5',head='regular',elimination_wins=0,mean_gun_exchange=-7,mean_enemy_guns_destroyed=3,sides=[{},dict(gun_victims_per_successful_shell=4)],enemy_over_own_artillery_hp_ratio=2,nearest=[dict(median=20,p10=10)])
 q=dict(p,arm='P10',nearest=[dict(median=60,p10=40)])
 r=dict(p,arm='P11',elimination_wins=1,mean_gun_exchange=-8)
 readings=a.reading([p,q,r]);assert 'no demonstrated splash benefit' in readings[0]['reading'];assert 'candidate' not in readings[1]['reading']
def test_declaration_and_preservation():
 d=pins();assert d['arms']==['P5','P10','P11'] and len(set(d['development_seeds']))==10
 assert d['catalog']['splash_px']==40 and d['catalog']['body_px']==10
 assert d['parameters']['S_P10']==100 and d['parameters']['S_P11']==60
 assert not d['judging_ledger_read'];admit(BINARY)

def test_failed_stage_retains_budget_receipt(monkeypatch,tmp_path):
 import common,time
 monkeypatch.setattr(common,'HERE',tmp_path)
 @common.stage('timeout_fixture',.02)
 def blocked():time.sleep(.2)
 try:blocked();assert False,'absolute deadline must interrupt'
 except TimeoutError:pass
 row=json.loads((tmp_path/'STAGE_timeout_fixture.json').read_text())
 assert row['status']=='STOP' and row['awake_seconds']>0 and row['returncode']==1
 assert common.remaining()<3480

def test_partial_report_retains_measured_control(monkeypatch,tmp_path):
 spec=importlib.util.spec_from_file_location('spacing_render',HERE/'render.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 folder=tmp_path/'probe';folder.mkdir();monkeypatch.setattr(m,'HERE',folder);monkeypatch.setattr(m,'CPP',tmp_path)
 write(folder/'PILOT_GATE.json',dict(status='CLEAR'))
 raw=folder/'raw';raw.mkdir();write(raw/'CLAIMED_ONCE.json',dict(declaration_sha256='fixture'))
 write(folder/'P5_SANITY.json',dict(status='WITHIN_DECLARED_BOUNDS',regular_mean_enemy_guns_destroyed=3,regular_mean_own_gun_losses=10))
 write(folder/'PARTIAL.json',[dict(arm='P5',head='regular',summary=dict(enemySurvivors=30,survivors=1,t=150,artilleryAlive=[0,7]))])
 m.main();c=json.loads((folder/'COMPACT.json').read_text());report=(tmp_path/'S4_SPACING_PROBE.md').read_text()
 assert c['status']=='PARTIAL' and c['completed_fights']==1 and c['entropy_claimed']
 assert c['P5_sanity']['status']=='WITHIN_DECLARED_BOUNDS'
 assert c['rows'][0]['measurements']['enemy_guns_destroyed']['value']==3
 assert c['rows'][0]['measurements']['gun_victims_per_successful_shell_both_sides']['status']=='not_analyzed'
 assert 'no raw fights exist' not in report and 'Entropy claimed: True' in report
