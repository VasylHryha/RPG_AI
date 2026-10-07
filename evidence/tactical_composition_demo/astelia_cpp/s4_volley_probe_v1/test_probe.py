import pathlib,json,subprocess,sys,hashlib
HERE=pathlib.Path(__file__).resolve().parent;CPP=HERE.parent;REPO=CPP.parents[2];sys.path.insert(0,str(CPP))
from build_admission import sha,admit

def test_prerequisites():
 r=json.loads((HERE/'PREREQUISITES.json').read_text())['rows']
 assert [x['own_launches'] for x in r]==[0,2,0]
 assert all(x['auto'] and not x['abilities'] for x in r)
 assert not r[2]['manual_ability_succeeded']

def test_overlay_fixture():
 m=json.loads((CPP/'build/astelia_native_volley_probe_v1.build.json').read_text());argv=m['commands'][0][:];argv=argv[:argv.index('-c')]+['-c',str(HERE/'fixture.cpp'),'-o',str(HERE/'fixture.o')];subprocess.run(argv,check=True)
 objects=[o for o in m['link'][1:-2] if not o.endswith('observer_v1_host_observer_v1.o')]
 subprocess.run([m['link'][0],str(HERE/'fixture.o'),*objects,'-o',str(HERE/'fixture')],check=True)
 r=subprocess.run([str(HERE/'fixture')],capture_output=True,check=True,text=True);(HERE/'FIXTURE.log').write_text(r.stdout)

def test_historical_contracts():
 rows=[]
 for arg in ('--attribution-contract','--v6-contract'):
  outputs=[subprocess.run([str(CPP/'build'/name),arg],capture_output=True,check=True,timeout=60) for name in ('astelia_native_v6','astelia_native_observer_v1','astelia_native_volley_probe_v1')]
  assert all(r.stdout==outputs[0].stdout and r.stderr==outputs[0].stderr for r in outputs)
  rows.append(dict(argument=arg,bytes=len(outputs[0].stdout),sha256=hashlib.sha256(outputs[0].stdout).hexdigest()))
 (HERE/'HISTORICAL_FIXTURES.json').write_text(json.dumps(dict(status='PASS',rows=rows),indent=2)+'\n')

def test_protected_files():
 for n,h in json.loads((HERE/'DECLARATION.json').read_text())['protected'].items():assert sha(REPO/n)==h,n
 admit(CPP/'build/astelia_native_volley_probe_v1')


def test_p0_engineering_bytes():
 d=json.loads((HERE/'DECLARATION.json').read_text());rows=[]
 from s3_v6_runner import request
 for head in ('regular','novice'):
  req=request(dict(arm='resonator',skeleton='v6',params=d['knobs'],opponent=head,seed=d['engineering_seed'],setting='s4_full_head',controlledSide=0,endCounts=True,trace=True));req['options']['duration']=2;req['killerTelemetry']=True;req['decisionTrace']=True
  a=subprocess.run([str(CPP/'build/astelia_native_observer_v1'),'--metrics'],input=json.dumps(req)+'\n',capture_output=True,text=True,check=True,timeout=30)
  req['options']['ai'][0].update(controller='P0',skeleton='volley_probe_v1')
  b=subprocess.run([str(CPP/'build/astelia_native_volley_probe_v1'),'--metrics'],input=json.dumps(req)+'\n',capture_output=True,text=True,check=True,timeout=30)
  assert a.stdout==b.stdout and a.stderr==b.stderr
  rows.append(dict(head=head,bytes=len(a.stdout.encode()),sha256=hashlib.sha256(a.stdout.encode()).hexdigest(),byte_identical=True))
 (HERE/'P0_PARITY.json').write_text(json.dumps(dict(status='PASS',duration_s=2,engineering_fights=4,rows=rows),indent=2)+'\n')
