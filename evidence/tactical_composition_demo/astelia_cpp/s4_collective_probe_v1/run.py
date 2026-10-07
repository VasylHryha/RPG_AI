"""One development claim; controls first; bounded workers and honest total projection."""
import pathlib,sys,json,subprocess,time,threading,gzip,os
HERE=pathlib.Path(__file__).resolve().parent;CPP=HERE.parent;REPO=CPP.parents[2];RAW=HERE/'raw';sys.path.insert(0,str(CPP));from build_admission import sha,admit
from s4_deadline import Deadline,BoundedPool
BINARY=CPP/'build/astelia_native_collective_probe_v1'
def write(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def pins():
 d=json.loads((HERE/'DECLARATION.json').read_text())
 for n,h in d['protected'].items():assert sha(REPO/n)==h,n
 admit(BINARY);return d
def budget():
 used=60+sum(json.loads(p.read_text())['awake_seconds'] for p in HERE.glob('STAGE_*.json'))
 return 3600-used
def one(task,deadline):
 arm,head,c,o,seed=task;tag=f'{arm}_{head}_c{c:02d}_o{o}';req=json.loads((HERE/(head.upper()+'_REQUEST_TEMPLATE.json')).read_text());req['options']['seed']=seed;req['options']['swapSides']=bool(o);req['options']['ai'][0]['controller']=arm;write(RAW/(tag+'_request.json'),req)
 with deadline.lock:
  deadline.remaining();child=subprocess.Popen([str(BINARY),'--metrics'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True);deadline.children.add(child)
 try:
  child.stdin.write((json.dumps(req)+'\n').encode());child.stdin.close();path=RAW/(tag+'.jsonl.gz');last=None
  with gzip.GzipFile(filename=str(path),mode='wb',compresslevel=1,mtime=0) as out:
   for line in child.stdout:deadline.remaining();out.write(line);last=line
  err=child.stderr.read();child.wait(timeout=deadline.remaining());(RAW/(tag+'_stderr.log')).write_bytes(err);assert child.returncode==0
  summary=json.loads(last);assert 'error' not in summary and summary['controllerStatus']=='completed' and not any(summary['controllerFailures']),summary
  metrics=json.loads(err);assert metrics['executed_fights']==1 and all(metrics[k]==0 for k in ('forks','search_calls','branch_steps','artillery_rollouts'))
  return dict(id=tag,arm=arm,head=head,cluster=c,orientation=o,summary=summary,metrics=metrics,raw_sha256=sha(path),raw_bytes=path.stat().st_size,request_sha256=sha(RAW/(tag+'_request.json')))
 except BaseException:deadline.stop();child.wait(timeout=2);raise
 finally:
  with deadline.lock:deadline.children.discard(child)
def main():
 d=pins();RAW.mkdir();write(RAW/'CLAIMED_ONCE.json',dict(declaration_sha256=sha(HERE/'DECLARATION.json')));start=time.time();awake=time.monotonic();allowance=min(1200,budget());deadline=Deadline(awake+allowance);timer=threading.Timer(allowance,deadline.stop);timer.daemon=True;timer.start();rows=[];ok=False
 code={str(p.relative_to(REPO)):sha(p) for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py','.cpp','.h','.md','.json') and p.name not in ('BUILD_TIMING.json','CHECK_TIMING.json','OWNER_RECHECK.md')}
 write(HERE/'RUN_START.json',dict(workers=2,remaining_budget_seconds=budget(),cap_seconds=allowance,load=os.getloadavg(),code=code,binary=admit(BINARY)))
 tasks=[(a,h,c,o,s) for a in d['arms'] for h in d['heads'] for c,s in enumerate(d['development_seeds']) for o in d['orientations']]
 try:
  for phase in ('control','interventions'):
   block=tasks[:40] if phase=='control' else tasks[40:];pool=BoundedPool(2,deadline)
   try:
    for row in pool.map(one,block):
     rows.append(row);write(HERE/'PARTIAL.json',sorted(rows,key=lambda r:r['id']))
     if len(rows)%8==0:
      elapsed=time.monotonic()-awake;projected=elapsed*160/len(rows)+900
      write(HERE/'PROJECTION.json',dict(completed=len(rows),combat_projection_s=elapsed*160/len(rows),analysis_review_reserve_s=900,total_projected_s=projected+3600-budget(),budget_s=3600,load=os.getloadavg()))
      print(json.dumps(dict(phase=phase,completed=len(rows),elapsed_s=elapsed,projected_total_s=projected+3600-budget())),flush=True)
      if projected>budget():deadline.stop();raise TimeoutError('honest compute projection exceeds1h; STOP')
   finally:
    # Successful block must not stop shared deadline.
    pool.pool.shutdown(wait=True,cancel_futures=True)
   if phase=='control':
    a=[r['summary'] for r in rows if r['head']=='regular'];kills=sum(10-r['artilleryAlive'][1] for r in a)/20;loss=sum(10-r['artilleryAlive'][0] for r in a)/20
    sanity=dict(status='FLAG' if loss<7 or loss>10 or kills<1 or kills>6 else 'WITHIN_DECLARED_BOUNDS',regular_mean_enemy_guns_destroyed=kills,regular_mean_own_gun_losses=loss,reported_before_other_arms=True,control_completed=40)
    write(HERE/'P5_SANITY.json',sanity);print(json.dumps(dict(P5_sanity=sanity)),flush=True)
  assert len(rows)==160;pins()
  for name,h in code.items():assert sha(REPO/name)==h,name
  write(HERE/'FIGHTS.json',sorted(rows,key=lambda r:r['id']));ok=True
 finally:
  timer.cancel();deadline.stop();write(HERE/'RUN_TIMING.json',dict(status='DONE' if ok else 'STOP',completed=len(rows),elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake))
if __name__=='__main__':main()
