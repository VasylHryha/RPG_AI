"""P12 first; immutable per-fight claims/completions; ambiguous claims never replay."""
import gzip,threading
from common import *
RAW=HERE/'raw'

def request(arm,head,seed,orientation,duration=150,skeleton='escort_probe_v3'):
 req=json.loads((HERE/(head.upper()+'_REQUEST_TEMPLATE.json')).read_text())
 req['options'].update(seed=seed,swapSides=bool(orientation),duration=duration)
 req['options']['ai'][0].update(controller=arm,skeleton=skeleton)
 return req

def verified(tag,req,binary=BINARY):
 complete=RAW/(tag+'_COMPLETE.json');claim=RAW/(tag+'_CLAIM.json')
 if not complete.exists():
  assert not claim.exists() and not any(RAW.glob(tag+'_*')) and not (RAW/(tag+'.jsonl.gz')).exists(),('ambiguous possibly executed fight; never replay',tag)
  return None
 r=json.loads(complete.read_text());assert claim.exists()
 c=json.loads(claim.read_text());assert c['declaration_sha256']==sha(HERE/'DECLARATION.json') and c['binary']==admit(binary)
 assert r['claim_sha256']==sha(claim) and r['binary']==c['binary']
 p=RAW/(tag+'_request.json');assert sha(p)==r['request_sha256']==c['request_sha256'] and json.loads(p.read_text())==req
 gate=HERE/c['gate']['path'];assert sha(gate)==c['gate']['sha256']
 g=json.loads(gate.read_text());assert g['status']=='CLEAR' and g['declaration_sha256']==c['declaration_sha256'] and g['binary']==admit(BINARY)
 p=RAW/(tag+'.jsonl.gz');assert p.stat().st_size==r['raw_bytes'] and sha(p)==r['raw_sha256']
 p=RAW/(tag+'_stderr.log');assert sha(p)==r['stderr_sha256']
 assert r['summary']['controllerStatus']=='completed' and not any(r['summary']['controllerFailures'])
 assert r['summary']['complexDiagnostics']['numericalFailureTicks']==0
 return r

def execute(tag,req,deadline,gate,binary=BINARY,meta=None):
 prior=verified(tag,req,binary)
 if prior:return prior
 deadline.remaining();identity=admit(binary);started=utc()
 exclusive(RAW/(tag+'_request.json'),req)
 claim=RAW/(tag+'_CLAIM.json');exclusive(claim,dict(utc_start=started,declaration_sha256=sha(HERE/'DECLARATION.json'),binary=identity,gate=gate,request_sha256=sha(RAW/(tag+'_request.json'))))
 child=None
 try:
  with deadline.lock:
   deadline.remaining();child=subprocess.Popen([str(binary),'--metrics'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True);deadline.children.add(child)
  child.stdin.write((json.dumps(req)+'\n').encode());child.stdin.close()
  path=RAW/(tag+'.jsonl.gz');last=None
  # stderr redirected by a concurrent drainer to avoid pipe backpressure.
  errors=[]
  def drain():
   try:
    with (RAW/(tag+'_stderr.log')).open('xb') as f:
     while True:
      b=child.stderr.read(65536)
      if not b:break
      f.write(b)
   except BaseException as e:errors.append(e);deadline.stop()
  thread=threading.Thread(target=drain);thread.start()
  with path.open('xb') as f,gzip.GzipFile(filename='',fileobj=f,mode='wb',compresslevel=1,mtime=0) as out:
   for line in child.stdout:deadline.remaining();out.write(line);last=line
  child.wait(timeout=deadline.remaining());thread.join(timeout=deadline.remaining());assert not thread.is_alive() and not errors
  deadline.remaining();assert child.returncode==0
  summary=json.loads(last);assert 'error' not in summary and summary['controllerStatus']=='completed' and not any(summary['controllerFailures']),summary
  assert summary['complexDiagnostics']['numericalFailureTicks']==0,'numerical integration failure'
  metrics=json.loads((RAW/(tag+'_stderr.log')).read_text());assert metrics['executed_fights']==1 and all(metrics[k]==0 for k in ('forks','search_calls','branch_steps','artillery_rollouts'))
  r=dict(id=tag,**(meta or {}),utc_start=started,utc_end=utc(),binary=identity,summary=summary,metrics=metrics,claim_sha256=sha(claim),raw_sha256=sha(path),raw_bytes=path.stat().st_size,request_sha256=sha(RAW/(tag+'_request.json')),stderr_sha256=sha(RAW/(tag+'_stderr.log')))
  exclusive(RAW/(tag+'_COMPLETE.json'),r);return r
 except BaseException:
  deadline.stop()
  if child is not None:child.wait(timeout=2)
  raise
 finally:
  if child is not None:
   with deadline.lock:deadline.children.discard(child)
   for stream in (child.stdin,child.stdout,child.stderr):
    if stream:stream.close()

def task(d,arm,head,c,o):
 tag=f'{arm}_{head}_c{c:02d}_o{o}'
 return tag,request(arm,head,d['development_seeds'][c],o),dict(arm=arm,head=head,cluster=c,orientation=o)
def all_completions(d):
 out=[]
 for arm in d['arms']:
  for head in d['heads']:
   for c in range(10):
    for o in d['orientations']:
     tag,req,_=task(d,arm,head,c,o);r=verified(tag,req)
     if r:out.append(r)
 return out

def phase(arm,d,gate,verified_rows):
 @stage('run_'+arm)
 def work():
  begin=time.monotonic();initial=spent();done=0;rows=list(verified_rows);known={r['id'] for r in rows}
  tasks=[]
  for head in d['heads']:
   for c in range(10):
    for o in d['orientations']:
     t=task(d,arm,head,c,o)
     if t[0] not in known:tasks.append(t)
  with owned_deadline() as deadline:
   pool=BoundedPool(2,deadline)
   def one(t,dl):return execute(t[0],t[1],dl,gate,meta=t[2])
   try:
    for r in pool.map(one,tasks):
     done+=1;rows.append(r);write(HERE/'PARTIAL.json',rows)
     elapsed=time.monotonic()-begin
     if done%8==0:
      completed=len(rows);projection=initial+elapsed+(120-completed)*elapsed/done+600
      write(HERE/'PROJECTION.json',dict(completed=completed,projected_total_s=projection,limit_s=3600,utc=utc(),analysis_reserve_s=600))
      print(json.dumps(dict(arm=arm,completed=completed,elapsed_s=elapsed,projected_total_s=projection)),flush=True)
      assert projection<=3600,'honest compute projection exceeds1h; STOP'
   finally:pool.close()
  pins();admit(BINARY);return rows
 return work()

def sanity(rows):
 assert len(rows)==40 and all(r['arm']=='P12' for r in rows)
 cells=[]
 for head in ('regular','novice'):
  s=[r['summary'] for r in rows if r['head']==head];assert len(s)==20
  cells.append(dict(head=head,fights=20,elimination_wins=sum(x['enemySurvivors']==0 and x['survivors']>=1 and x['t']<150 for x in s),timeouts=sum(x['t']>=150 for x in s),mean_S=sum(x['survivors']-x['enemySurvivors'] for x in s)/20,mean_enemy_guns_destroyed=sum(10-x['artilleryAlive'][1] for x in s)/20,mean_own_guns_lost=sum(10-x['artilleryAlive'][0] for x in s)/20,mean_own_losses=sum(50-x['survivors'] for x in s)/20))
 r=cells[0];return dict(status='FLAG' if r['mean_enemy_guns_destroyed']<4 or r['mean_own_guns_lost']<7 else 'WITHIN_DECLARED_BOUNDS',novice_sanity_flag=cells[1]['elimination_wins']<20,reported_before_interventions=True,cells=cells,control_ids=[r['id'] for r in rows],utc=utc(),declaration_sha256=sha(HERE/'DECLARATION.json'))

def main():
 d=pins();checked_binary()
 engineering=json.loads((HERE/'ENGINEERING.json').read_text());assert engineering['status']=='PASS' and engineering['binary_identity']==admit(BINARY) and engineering['declaration_sha256']==sha(HERE/'DECLARATION.json')
 for head in d['heads']:
  for version,name in (('escort_probe_v1','astelia_native_escort_probe_v1'),('escort_probe_v3','astelia_native_escort_probe_v3')):
   tag=f'engineering_{head}_{version}';req=request('P12',head,d['engineering_seed'],0,duration=2,skeleton=version)
   assert verified(tag,req,CPP/'build'/name),'engineering completion missing'
 RAW.mkdir(exist_ok=True);rows=all_completions(d)
 for arm in d['arms']:
  # Check every completion AND ambiguous claim before launching anything new.
  present=[r for r in rows if r['arm']==arm]
  if len(present)<40:
   gate=pilot_gate(wait=True);rows=phase(arm,d,gate,rows)
  if arm=='P12':
   control=[r for r in rows if r['arm']=='P12'];value=sanity(control)
   p=HERE/'P12_SANITY.json'
   if p.exists():assert json.loads(p.read_text())['control_ids']==value['control_ids']
   else:exclusive(p,value)
   print(json.dumps(dict(P12_sanity=json.loads(p.read_text()))),flush=True)
 assert len(rows)==120
 rows=sorted(rows,key=lambda r:r['id'])
 if not (HERE/'FIGHTS.json').exists():exclusive(HERE/'FIGHTS.json',rows)
 else:assert json.loads((HERE/'FIGHTS.json').read_text())==rows
 write(HERE/'RAW_FILES_LOCAL.json',dict(files=[dict(path=str(p.relative_to(HERE)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(RAW.iterdir()) if p.is_file()]))
if __name__=='__main__':caffeinate();main()
