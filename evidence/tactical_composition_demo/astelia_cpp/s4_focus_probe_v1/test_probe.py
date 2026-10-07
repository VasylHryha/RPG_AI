import pathlib,json,subprocess,sys,hashlib
HERE=pathlib.Path(__file__).resolve().parent;CPP=HERE.parent;REPO=CPP.parents[2];sys.path.insert(0,str(CPP))
from build_admission import sha,admit

def test_inherited_prerequisites():
 r=json.loads((CPP/'s4_volley_probe_v1/PREREQUISITES.json').read_text())['rows']
 assert [x['own_launches'] for x in r]==[0,2,0]
 assert all(x['auto'] and not x['abilities'] for x in r)
 assert not r[2]['manual_ability_succeeded']
 d=json.loads((HERE/'DECLARATION.json').read_text())
 assert d['parameters']['commit_margin_px']==12 and d['arms']==['P0','P4','P5','P6']

def test_overlay_fixture():
 m=json.loads((CPP/'build/astelia_native_focus_probe_v1.build.json').read_text());argv=m['commands'][0][:];argv=argv[:argv.index('-c')]+['-c',str(HERE/'fixture.cpp'),'-o',str(HERE/'fixture.o')];subprocess.run(argv,check=True)
 objects=[o for o in m['link'][1:-2] if not o.endswith('observer_v1_host_observer_v1.o')]
 subprocess.run([m['link'][0],str(HERE/'fixture.o'),*objects,'-o',str(HERE/'fixture')],check=True)
 r=subprocess.run([str(HERE/'fixture')],capture_output=True,check=True,text=True);(HERE/'FIXTURE.log').write_text(r.stdout)

def test_historical_contracts():
 rows=[]
 for arg in ('--attribution-contract','--v6-contract'):
  outputs=[subprocess.run([str(CPP/'build'/name),arg],capture_output=True,check=True,timeout=60) for name in ('astelia_native_v6','astelia_native_observer_v1','astelia_native_volley_probe_v1','astelia_native_focus_probe_v1')]
  assert all(r.stdout==outputs[0].stdout and r.stderr==outputs[0].stderr for r in outputs)
  rows.append(dict(argument=arg,bytes=len(outputs[0].stdout),sha256=hashlib.sha256(outputs[0].stdout).hexdigest()))
 (HERE/'HISTORICAL_FIXTURES.json').write_text(json.dumps(dict(status='PASS',rows=rows),indent=2)+'\n')

def test_protected_files():
 for n,h in json.loads((HERE/'DECLARATION.json').read_text())['protected'].items():assert sha(REPO/n)==h,n
 admit(CPP/'build/astelia_native_focus_probe_v1')


def test_p0_engineering_bytes():
 d=json.loads((HERE/'DECLARATION.json').read_text());rows=[]
 from s3_v6_runner import request
 for head in ('regular','novice'):
  req=request(dict(arm='resonator',skeleton='v6',params=d['knobs'],opponent=head,seed=d['engineering_seed'],setting='s4_full_head',controlledSide=0,endCounts=True,trace=True));req['options']['duration']=2;req['killerTelemetry']=True;req['decisionTrace']=True
  a=subprocess.run([str(CPP/'build/astelia_native_observer_v1'),'--metrics'],input=json.dumps(req)+'\n',capture_output=True,text=True,check=True,timeout=30)
  req['options']['ai'][0].update(controller='P0',skeleton='focus_probe_v1')
  b=subprocess.run([str(CPP/'build/astelia_native_focus_probe_v1'),'--metrics'],input=json.dumps(req)+'\n',capture_output=True,text=True,check=True,timeout=30)
  assert a.stdout==b.stdout and a.stderr==b.stderr
  rows.append(dict(head=head,bytes=len(a.stdout.encode()),sha256=hashlib.sha256(a.stdout.encode()).hexdigest(),byte_identical=True))
 (HERE/'P0_PARITY.json').write_text(json.dumps(dict(status='PASS',duration_s=2,engineering_fights=4,rows=rows),indent=2)+'\n')

def test_stored_telemetry_metrics(tmp_path,monkeypatch):
 import gzip,importlib.util
 spec=importlib.util.spec_from_file_location('focus_analysis',HERE/'analyze.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);monkeypatch.setattr(mod,'HERE',tmp_path)
 raw=tmp_path/'raw';raw.mkdir()
 units=[[i,0 if i<=50 else 1,2 if 41<=i<=50 or 91<=i<=100 else 0,0,0,181,10,320,80] for i in range(1,101)]
 def damage(source,target,team,targetTeam,role,died):return dict(source=source,target=target,sourceTeam=team,targetTeam=targetTeam,sourceRole=role,targetRole='artillery',dealt=15,t=1,died=died)
 summary=dict(survivors=48,enemySurvivors=49,artilleryAlive=[8,9],t=2)
 # One aimed launch splashes two guns; one soft-target launch incidentally kills a gun.
 trace=[dict(observerV1=True,step=0,t=0,units=units,launches=[],damage=[],dodges=[]),dict(observerV1=True,step=1,t=1,units=units,launches=[[41,91,0,0,0,0,1,40,False,False],[42,51,0,0,0,0,1,40,False,False]],damage=[damage(41,91,0,1,'artillery',False),damage(41,92,0,1,'artillery',False),damage(42,93,0,1,'artillery',True),damage(91,41,1,0,'artillery',True),damage(43,42,0,0,'artillery',True)],dodges=[]),summary]
 p=raw/'synthetic.jsonl.gz'
 with gzip.open(p,'wt') as f:
  for row in trace:f.write(json.dumps(row)+'\n')
 r=dict(id='synthetic',arm='P4',head='regular',cluster=0,orientation=0,summary=summary,raw_sha256=mod.sha(p));a=mod.analyze(r)
 assert a['shells_fired_at_enemy_guns']==1 and a['shell_hits_on_enemy_guns']==1 and a['own_damage_shells']==2
 assert a['time_to_first_enemy_gun_kill_s']==1 and a['enemy_guns_destroyed']==1
 assert {(x['team'],x['source'],x['target']) for x in a['own_gun_killers']}=={(1,91,41),(0,43,42)}
 summary=dict(survivors=50,enemySurvivors=50,artilleryAlive=[10,10],t=150)
 with gzip.open(p,'wt') as f:
  f.write(json.dumps(trace[0])+'\n');f.write(json.dumps(summary)+'\n')
 r.update(summary=summary,raw_sha256=mod.sha(p));a=mod.analyze(r)
 assert a['time_to_first_enemy_gun_kill_s'] is None and a['shells_fired_at_enemy_guns']==a['shell_hits_on_enemy_guns']==0 and a['timeout'] and not a['elimination_win']
