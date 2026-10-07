"""One declared development run, streaming exact observer data; never tuning."""
import pathlib,sys,json,subprocess,time,threading,concurrent.futures,gzip,os
HERE=pathlib.Path(__file__).resolve().parent;CPP=HERE.parent;REPO=CPP.parents[2];RAW=HERE/'raw';sys.path.insert(0,str(CPP))
from build_admission import sha,admit
from s3_v6_runner import request
from s4_deadline import Deadline
BINARY=CPP/'build/astelia_native_volley_probe_v1'
def write(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def pins():
 d=json.loads((HERE/'DECLARATION.json').read_text())
 for n,h in d['protected'].items():assert sha(REPO/n)==h,n
 admit(BINARY)
 return d

def one(task,deadline):
 arm,head,c,o,seed,knobs=task;tag=f'{arm}_{head}_c{c:02d}_o{o}';req=request(dict(arm='resonator',skeleton='v6',params=knobs,opponent=head,seed=seed,swapSides=bool(o),controlledSide=0,setting='s4_full_head',endCounts=True));req['options']['ai'][0].update(controller=arm,skeleton='volley_probe_v1');req.update(killerTelemetry=True,decisionTrace=True);write(RAW/(tag+'_request.json'),req)
 with deadline.lock:
  deadline.remaining();child=subprocess.Popen([str(BINARY),'--metrics'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True);deadline.children.add(child)
 try:
  child.stdin.write((json.dumps(req)+'\n').encode());child.stdin.close();path=RAW/(tag+'.jsonl.gz');last=None
  with gzip.GzipFile(filename=str(path),mode='wb',compresslevel=1,mtime=0) as out:
   for l in child.stdout:deadline.remaining();out.write(l);last=l
  err=child.stderr.read();child.wait(timeout=deadline.remaining());(RAW/(tag+'_stderr.log')).write_bytes(err);assert child.returncode==0
  s=json.loads(last);assert 'error' not in s,s;assert s['controllerStatus']=='completed' and not any(s['controllerFailures']),s
  m=json.loads(err);assert m['executed_fights']==1 and all(m[k]==0 for k in ('forks','search_calls','branch_steps','artillery_rollouts'))
  return dict(id=tag,arm=arm,head=head,cluster=c,orientation=o,summary=s,metrics=m,raw_sha256=sha(path),raw_bytes=path.stat().st_size,request_sha256=sha(RAW/(tag+'_request.json')))
 except BaseException:deadline.stop();raise
 finally:
  with deadline.lock:deadline.children.discard(child)

def main():
 d=pins();RAW.mkdir();(RAW/'CLAIMED_ONCE.json').write_text(json.dumps(dict(ledger_sha256=sha(HERE/'DECLARATION.json'))));start=time.time();awake=time.monotonic();deadline=Deadline(awake+1200);timer=threading.Timer(1200,deadline.stop);timer.daemon=True;timer.start();rows=[];ok=False
 code={str(p.relative_to(REPO)):sha(p) for p in [HERE/'run.py',HERE/'analyze.py',CPP/'src/native/s4_volley_probe_v1.cpp',CPP/'src/native/s4_volley_probe_v1.h',CPP/'src/native/s4_volley_probe_v1_dispatch.cpp']};write(HERE/'RUN_START.json',dict(argv=['/usr/bin/caffeinate','-i','-s',str(REPO/'.venv/bin/python'),str(HERE/'run.py')],workers=4,projection_minutes=[3,12],cap_seconds=1200,load=os.getloadavg(),code=code,binary=admit(BINARY)))
 tasks=[(a,h,c,o,s,d['knobs']) for a in d['arms'] for h in d['heads'] for c,s in enumerate(d['development_seeds']) for o in d['orientations']]
 try:
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
   for f in concurrent.futures.as_completed([pool.submit(one,t,deadline) for t in tasks]):
    rows.append(f.result());write(HERE/'PARTIAL.json',sorted(rows,key=lambda r:r['id']))
    if len(rows)%10==0:print(json.dumps(dict(completed=len(rows),elapsed_s=time.time()-start)),flush=True)
    if len(rows)>=8 and (time.monotonic()-awake)*len(tasks)/len(rows)>3600:
     deadline.stop();raise TimeoutError('projection exceeds 1h')
  assert len(rows)==160;pins()
  for n,h in code.items():assert sha(REPO/n)==h,n
  write(HERE/'FIGHTS.json',sorted(rows,key=lambda r:r['id']));ok=True
 finally:
  timer.cancel();deadline.stop();write(HERE/'RUN_TIMING.json',dict(status='DONE' if ok else 'STOP',completed=len(rows),elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake))
if __name__=='__main__':main()
