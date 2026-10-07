import pathlib,json,subprocess,sys,hashlib,importlib.util,math
HERE=pathlib.Path(__file__).resolve().parent;CPP=HERE.parent;REPO=CPP.parents[2];sys.path.insert(0,str(CPP));from build_admission import sha,admit
BINARY=CPP/'build/astelia_native_collective_probe_v1'
def test_fixture():
 m=json.loads(BINARY.with_suffix('.build.json').read_text());argv=m['commands'][0];argv=argv[:argv.index('-c')]+['-c',str(HERE/'fixture.cpp'),'-o',str(CPP/'build/collective_fixture.o')];subprocess.run(argv,check=True);objects=[o for o in m['link'][1:-2] if not o.endswith('collective_v1_host.o')];exe=CPP/'build/collective_fixture';subprocess.run([m['link'][0],str(CPP/'build/collective_fixture.o'),*objects,'-o',str(exe)],check=True);r=subprocess.run([str(exe)],capture_output=True,text=True,check=True);(HERE/'FIXTURE.log').write_text(r.stdout)
def test_protected_identity():
 d=json.loads((HERE/'DECLARATION.json').read_text())
 for n,h in d['protected'].items():assert sha(REPO/n)==h,n
 assert d['arms']==['P5','P7','P8','P9'];assert len(set(d['development_seeds']))==10;admit(BINARY)
def test_historical_contracts():
 rows=[]
 for arg in ('--attribution-contract','--v6-contract'):
  outputs=[subprocess.run([str(CPP/'build'/name),arg],capture_output=True,check=True,timeout=60) for name in ('astelia_native_v6','astelia_native_observer_v1','astelia_native_volley_probe_v1','astelia_native_focus_probe_v1','astelia_native_collective_probe_v1')]
  assert all(r.stdout==outputs[0].stdout and r.stderr==outputs[0].stderr for r in outputs);rows.append(dict(argument=arg,bytes=len(outputs[0].stdout),sha256=hashlib.sha256(outputs[0].stdout).hexdigest()))
 (HERE/'HISTORICAL_FIXTURES.json').write_text(json.dumps(dict(status='PASS',rows=rows),indent=2)+'\n')
def test_p5_parity():
 d=json.loads((HERE/'DECLARATION.json').read_text());rows=[]
 for head in ('regular','novice'):
  req=json.loads((HERE/(head.upper()+'_REQUEST_TEMPLATE.json')).read_text());req['options']['seed']=d['engineering_seed'];req['options']['duration']=2;req['options']['ai'][0]['skeleton']='focus_probe_v1'
  old=subprocess.run([str(CPP/'build/astelia_native_focus_probe_v1'),'--metrics'],input=(json.dumps(req)+'\n').encode(),capture_output=True,check=True,timeout=30)
  req['options']['ai'][0]['skeleton']='collective_probe_v1';new=subprocess.run([str(BINARY),'--metrics'],input=(json.dumps(req)+'\n').encode(),capture_output=True,check=True,timeout=30)
  assert old.stdout==new.stdout and old.stderr==new.stderr;rows.append(dict(head=head,stdout_sha256=hashlib.sha256(new.stdout).hexdigest(),bytes=len(new.stdout),byte_identical=True))
 (HERE/'P5_PARITY.json').write_text(json.dumps(dict(status='PASS',engineering_fights=4,duration_s=2,rows=rows),indent=2)+'\n')
def test_measurement_axes():
 spec=importlib.util.spec_from_file_location('collective_analysis',HERE/'analyze.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
 assert a.axis([]) is None and a.axis([[1,0,0],[2,0,0]]) is None
 assert a.axis([[1,1,0],[2,-1,0],[3,0,1],[4,0,-1]]) is None
 assert abs(a.angle_change(math.radians(89),math.radians(-89))-2)<1e-9
 assert abs(a.angle_change(0,math.pi/2)-90)<1e-9
 assert a.angle_change(None,0) is None

def test_stored_telemetry_metrics(tmp_path,monkeypatch):
 import gzip,importlib.util
 spec=importlib.util.spec_from_file_location('focus_analysis',HERE/'analyze.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);monkeypatch.setattr(mod.base,'HERE',tmp_path)
 raw=tmp_path/'raw';raw.mkdir()
 units=[[i,0 if i<=50 else 1,2 if 41<=i<=50 or 91<=i<=100 else 0,0,0,181,10,320,80] for i in range(1,101)]
 def damage(source,target,team,targetTeam,role,died):return dict(source=source,target=target,sourceTeam=team,targetTeam=targetTeam,sourceRole=role,targetRole='artillery',dealt=15,t=1,died=died)
 summary=dict(survivors=48,enemySurvivors=49,artilleryAlive=[8,9],t=2)
 # One aimed launch splashes two guns; one soft-target launch incidentally kills a gun.
 trace=[dict(observerV1=True,step=0,t=0,units=units,launches=[],damage=[],dodges=[]),dict(observerV1=True,step=1,t=1,units=units,launches=[[41,91,0,0,0,0,1,40,False,False],[42,51,0,0,0,0,1,40,False,False]],damage=[damage(41,91,0,1,'artillery',False),damage(41,92,0,1,'artillery',False),damage(42,93,0,1,'artillery',True),damage(91,41,1,0,'artillery',True),damage(43,42,0,0,'artillery',True)],dodges=[]),summary]
 p=raw/'synthetic.jsonl.gz'
 with gzip.open(p,'wt') as f:
  for row in trace:f.write(json.dumps(row)+'\n')
 r=dict(id='synthetic',arm='P4',head='regular',cluster=0,orientation=0,summary=summary,raw_sha256=mod.sha(p));a=mod.base.analyze(r)
 assert a['shells_fired_at_enemy_guns']==1 and a['shell_hits_on_enemy_guns']==1 and a['own_damage_shells']==2
 assert a['time_to_first_enemy_gun_kill_s']==1 and a['enemy_guns_destroyed']==1
 assert {(x['team'],x['source'],x['target']) for x in a['own_gun_killers']}=={(1,91,41),(0,43,42)}
 summary=dict(survivors=50,enemySurvivors=50,artilleryAlive=[10,10],t=150)
 with gzip.open(p,'wt') as f:
  f.write(json.dumps(trace[0])+'\n');f.write(json.dumps(summary)+'\n')
 r.update(summary=summary,raw_sha256=mod.sha(p));a=mod.base.analyze(r)
 assert a['time_to_first_enemy_gun_kill_s'] is None and a['shells_fired_at_enemy_guns']==a['shell_hits_on_enemy_guns']==0 and a['timeout'] and not a['elimination_win']
