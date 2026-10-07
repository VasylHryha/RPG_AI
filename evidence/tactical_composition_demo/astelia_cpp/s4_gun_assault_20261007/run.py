"""Declare once, then execute exactly 120 fresh fights under a hard daytime cap."""
import argparse,concurrent.futures,datetime,gzip,json,os,secrets,subprocess,time,threading
from common import *
from s4_deadline import Deadline

def prepare():
 from build_admission import admit
 from s4_development import verify_sources
 if RAW.exists():raise RuntimeError('refuse output/entropy reuse')
 # Only development declarations: never open judging entropy.
 old=set();prior={}
 def visit(v):
  if isinstance(v,dict):
   for x in v.values():visit(x)
  elif isinstance(v,list):
   for x in v:visit(x)
  elif type(v) is int:old.add(v)
 for p in [*CPP.glob('s4*development*/s4_seeds.json'),*CPP.glob('s4*development*/s4_v*_seeds.json'),*CPP.glob('s4*diagnostic*/raw/DEVELOPMENT_SEED_LEDGER.json')]:
  visit(json.loads(p.read_text()));prior[str(p.relative_to(REPO))]=sha(p)
 values=[]
 while len(values)<13:
  s=3000000000+secrets.randbelow(1000000000)
  if s not in old and s not in values:values.append(s)
 RAW.mkdir()
 write(RAW/'DEVELOPMENT_SEED_LEDGER.json',dict(status='FRESH_DEVELOPMENT_ONLY',judging_root=None,
  entropy='independent OS secrets, uniform [3000000000,4000000000), development rejection only',
  seeds=values[:10],engineering_seeds=values[10:],prior_development_declarations=prior,
  arms=ARMS,heads=['novice','regular'],orientations=[0,1],controlled_team=0,fights=120,
  purpose='descriptive gun-assault diagnostic; no tuning, registration or qualification',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 tracked=subprocess.check_output(['git','ls-files','evidence/tactical_composition_demo/astelia_cpp','evidence/tactical_composition_demo/astelia_snapshot','STATUS.json','docs/PLAN_CURRENT.md','evidence/tactical_composition_demo/DESIGN_0G.md'],cwd=REPO,text=True).splitlines()
 protected={n:sha(REPO/n) for n in tracked if (REPO/n).is_file()}
 record=dict(protected=protected,knob_files={str(p.relative_to(REPO)):sha(p) for p in KNOB_FILES.values()},
  selected_knobs=selected(),ledger_sha256=sha(RAW/'DEVELOPMENT_SEED_LEDGER.json'),rrg=verify_sources(),
  observer_build=admit(BINARY),v6_build=admit(CPP/'build/astelia_native_v6'),
  script_hashes={p.name:sha(p) for p in HERE.glob('*.py')},test_sha256=sha(CPP/'test_observer_v1.py'),
  projection_minutes=[15,30],daytime_stop_seconds=3600,combat_cap_seconds=1200,
  definitions=dict(approach='directed native move/ability crossing from outside maximum range into inclusive gun band, exact movement-time geometry; all roles, each unit/gun pair',
   approach_window_seconds=3,prekill_window_seconds=3,phase='early [0,20), middle [20,60), late [60,end]; also gun-only iff no enemy non-gun alive before tick',
   outcome='elimination win iff enemySurvivors=0, survivors>=1, t<150; timeout iff t>=150',
   distance='native px centre-to-centre at damage application, not launch; amount=mitigated HP decrement, dealt=capped actual HP',
   direction='angle at entry to axis from gun to centroid of other living enemy guns; 0 toward supporting guns, 180 opposite; null if no support',
   simultaneous='same gun: distinct attackers legally within own reach per observed tick; assaults: distinct approachers active in its band'))
 write(HERE/'INPUT_IDENTITY.json',record)
 print(json.dumps(dict(prepared=True,protected_files=len(protected),fights=120,projection_minutes=[15,30])))

def one(task,deadline):
 arm,head,cluster,orientation,seed=task;tag=f'{arm}_{head}_c{cluster:02d}_o{orientation}'
 req=request_for(arm,head,seed,orientation);write(RAW/(tag+'_request.json'),req)
 with deadline.lock:
  deadline.remaining();child=subprocess.Popen([str(BINARY),'--metrics'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True);deadline.children.add(child)
 p=RAW/(tag+'.jsonl.gz');last=None;lines=0
 try:
  child.stdin.write((json.dumps(req)+'\n').encode());child.stdin.close()
  with gzip.GzipFile(filename=str(p),mode='wb',compresslevel=1,mtime=0) as out:
   for line in child.stdout:deadline.remaining();out.write(line);last=line;lines+=1
  err=child.stderr.read();child.wait(timeout=deadline.remaining());(RAW/(tag+'_stderr.log')).write_bytes(err)
  if child.returncode:raise RuntimeError(err.decode())
  result=json.loads(last);metrics=json.loads(err)
  assert 'error' not in result,result
  assert result['controllerStatus']=='completed' and not any(result['controllerFailures']),result
  assert metrics['executed_fights']==1 and all(metrics[k]==0 for k in ('forks','search_calls','branch_steps','artillery_rollouts'))
  return dict(id=tag,arm=arm,head=head,cluster=cluster,orientation=orientation,summary=result,metrics=metrics,
              raw_file=str(p.relative_to(HERE)),raw_sha256=sha(p),raw_bytes=p.stat().st_size,lines=lines,
              request_sha256=sha(RAW/(tag+'_request.json')))
 except BaseException:
  deadline.stop();raise
 finally:
  with deadline.lock:deadline.children.discard(child)

def execute():
 assert_pins()
 parity=json.loads((HERE/'PARITY.json').read_text());assert parity['status']=='PASS'
 with (RAW/'CLAIMED_ONCE.json').open('x') as f:json.dump(dict(ledger_sha256=sha(RAW/'DEVELOPMENT_SEED_LEDGER.json')),f)
 ledger=json.loads((RAW/'DEVELOPMENT_SEED_LEDGER.json').read_text());start=time.time();awake=time.monotonic();deadline=Deadline(awake+1200);watchdog=threading.Timer(1200,deadline.stop);watchdog.daemon=True;watchdog.start()
 write(HERE/'RUN_START.json',dict(argv=['/usr/bin/caffeinate','-i','-s',str(REPO/'.venv/bin/python'),str(HERE/'run.py'),'--execute'],projection_minutes=[3,12],cap_seconds=1200,workers=4,load=os.getloadavg(),start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 tasks=[(a,h,c,o,s) for a in ARMS for h in ('novice','regular') for c,s in enumerate(ledger['seeds']) for o in (0,1)];records=[];success=False
 try:
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
   futures=[pool.submit(one,t,deadline) for t in tasks]
   for future in concurrent.futures.as_completed(futures):
    records.append(future.result());write(HERE/'FIGHTS_PARTIAL.json',sorted(records,key=lambda r:r['id']))
    if len(records)%10==0:print(json.dumps(dict(completed=len(records),elapsed=time.time()-start)),flush=True)
    if len(records)>=8:
     projection=(time.monotonic()-awake)*120/len(records)
     if projection>3600:deadline.stop();raise TimeoutError(f'daytime projection {projection:.1f}s exceeds 1h')
  assert len(records)==120;assert_pins();write(HERE/'FIGHTS.json',sorted(records,key=lambda r:r['id']));success=True
 finally:
  watchdog.cancel();deadline.stop();write(HERE/'RUN_TIMING.json',dict(elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake,completed=len(records),status='DONE' if success else 'STOP',load=os.getloadavg()))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--execute',action='store_true');a=ap.parse_args()
 if a.prepare:prepare()
 elif a.execute:execute()
 else:ap.error('choose --prepare or --execute')
