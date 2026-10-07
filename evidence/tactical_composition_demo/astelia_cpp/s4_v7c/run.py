"""Claude executor: validation only with sealed identities and no ambiguous replay."""
import argparse, gzip, threading
from common import *
from protocol import *
RAW=HERE/'raw'

def request(arm,head,seed,orientation,params,telemetry=False):
 req=read(HERE/(head.upper()+'_REQUEST_TEMPLATE.json'))
 req['options'].update(seed=seed,swapSides=bool(orientation),duration=150)
 req['options']['ai'][0].update(controller=arm,skeleton='v7',params=params)
 req.update(trace=telemetry,diagnostics=False,killerTelemetry=telemetry,decisionTrace=telemetry,decisionDiagnostics=telemetry,attributionDiagnostics=telemetry)
 return req

def verified(tag,requests=None):
 done=RAW/(tag+'_COMPLETE.json');claim=RAW/(tag+'_CLAIM.json')
 if not done.exists():
  if any(RAW.glob(tag+'_*')) or (RAW/(tag+'.jsonl.gz')).exists():raise RuntimeError('ambiguous possibly executed fight; never replay: '+tag)
  return None
 r=read(done);c=read(claim);d=pins()
 if r['meta']!=c['meta']:raise RuntimeError('completion/claim metadata drift '+tag)
 if c['declaration_sha256']!=sha(HERE/'DECLARATION.json') or c['binary']!=d['binary'] or r['claim_sha256']!=sha(claim) or r['binary']!=c['binary']:raise RuntimeError('claim/identity drift '+tag)
 req=RAW/(tag+'_request.json')
 if sha(req)!=c['request_sha256'] or sha(req)!=r['request_sha256'] or requests is not None and read(req)!=requests:raise RuntimeError('request drift '+tag)
 gate=HERE/c['gate']['path'];g=read(gate)
 if sha(gate)!=c['gate']['sha256'] or g['status']!='CLEAR' or g['declaration_sha256']!=c['declaration_sha256'] or g['binary']!=c['binary']:raise RuntimeError('process gate drift '+tag)
 for key,suffix in (('raw_sha256','.jsonl.gz'),('stderr_sha256','_stderr.log')):
  if sha(RAW/(tag+suffix))!=r[key]:raise RuntimeError('raw receipt drift '+tag)
 with gzip.open(RAW/(tag+'.jsonl.gz'),'rt') as f:
  last=None
  for line in f:last=json.loads(line)
 summaries=last if isinstance(last,list) else [last]
 if summaries!=r['summaries'] or len(summaries)!=len(read(req)):raise RuntimeError('raw/summary mismatch '+tag)
 for s in summaries:measure(s)
 metrics=read(RAW/(tag+'_stderr.log'))
 if metrics!=r['metrics'] or metrics['executed_fights']!=len(summaries) or any(metrics[k] for k in ('forks','search_calls','branch_steps','artillery_rollouts')):raise RuntimeError('unexpected engine work '+tag)
 return r

def audit_raw():
 if not RAW.exists():return
 tags=set()
 for p in RAW.iterdir():
  matched=re.fullmatch(r'(.+)(_COMPLETE\.json|_CLAIM\.json|_request\.json|_stderr\.log|_FAILURE\.json|\.jsonl\.gz)',p.name)
  if not matched:raise RuntimeError('unknown raw artifact: '+p.name)
  tags.add(matched[1])
 expected={tag:(reqs,meta) for tag,reqs,meta in validation_plan(pins())}
 for tag in sorted(tags):
  if tag not in expected:raise RuntimeError('unexpected validation cell: '+tag)
  reqs,meta=expected[tag];r=verified(tag,reqs)
  if r is not None and r['meta']!=meta:raise RuntimeError('validation cell metadata drift: '+tag)

def execute(task,deadline):
 tag,reqs,meta,gate=task
 prior=verified(tag,reqs)
 if prior:return prior
 pins();identity=admit(BINARY);deadline.remaining()
 exclusive(RAW/(tag+'_request.json'),reqs)
 claim=RAW/(tag+'_CLAIM.json');exclusive(claim,dict(meta=meta,utc_start=utc(),declaration_sha256=sha(HERE/'DECLARATION.json'),binary=identity,gate=gate,request_sha256=sha(RAW/(tag+'_request.json'))))
 child=None
 try:
  with deadline.lock:
   deadline.remaining();child=subprocess.Popen([str(BINARY),'--metrics'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True);deadline.children.add(child)
  # Validation is a singleton native request.
  payload=reqs if len(reqs)>1 else reqs[0]
  child.stdin.write((json.dumps(payload)+'\n').encode());child.stdin.close()
  errors=[]
  def drain():
   try:
    with (RAW/(tag+'_stderr.log')).open('xb') as f:
     while True:
      b=child.stderr.read(65536)
      if not b:break
      f.write(b)
   except BaseException as e:errors.append(str(e));deadline.stop()
  thread=threading.Thread(target=drain);thread.start();last=None
  path=RAW/(tag+'.jsonl.gz')
  with path.open('xb') as f,gzip.GzipFile(filename='',fileobj=f,mode='wb',compresslevel=1,mtime=0) as raw:
   for line in child.stdout:deadline.remaining();raw.write(line);last=line
  child.wait(timeout=deadline.remaining());thread.join(timeout=deadline.remaining())
  if child.returncode or thread.is_alive() or errors:raise RuntimeError('native execution failure')
  result=json.loads(last);summaries=result if isinstance(result,list) else [result]
  if len(summaries)!=len(reqs):raise RuntimeError('native count mismatch')
  for summary in summaries:measure(summary)
  metrics=read(RAW/(tag+'_stderr.log'))
  if metrics['executed_fights']!=len(reqs) or any(metrics[k] for k in ('forks','search_calls','branch_steps','artillery_rollouts')):raise RuntimeError('unexpected native work')
  deadline.remaining();pins()
  record=dict(tag=tag,meta=meta,binary=identity,summaries=summaries,metrics=metrics,claim_sha256=sha(claim),raw_sha256=sha(path),raw_bytes=path.stat().st_size,request_sha256=sha(RAW/(tag+'_request.json')),stderr_sha256=sha(RAW/(tag+'_stderr.log')),utc_end=utc())
  exclusive(RAW/(tag+'_COMPLETE.json'),record);return record
 except BaseException as e:
  deadline.stop()
  exclusive(RAW/(tag+'_FAILURE.json'),dict(error=type(e).__name__+': '+str(e),utc=utc(),never_replay=True))
  if child is not None:child.wait(timeout=2)
  raise
 finally:
  if child is not None:
   with deadline.lock:deadline.children.discard(child)
   for stream in (child.stdin,child.stdout,child.stderr):
    if stream:stream.close()

class Executor:
 def __init__(self,dl,gate,prior,start,total,stage_batches):
  self.dl=dl;self.gate=gate;self.prior=prior;self.start=start;self.total=total;self.done=0;self.batches=0;self.stage_batches=stage_batches;self.completion_lock=threading.Lock();self.pool=BoundedPool(10,dl)
 def completed(self,task,deadline):
  row=execute(task,deadline)
  with self.completion_lock:self.done+=len(row['summaries']);self.batches+=1
  return row
 def tasks(self,tasks):
  for row in self.pool.map(self.completed,tasks):
   with self.completion_lock:done,batches=self.done,self.batches
   project(self.prior,self.start,done,self.total,batches,self.stage_batches);yield row
 def close(self):self.pool.close()

def tuning_receipt():
 pins();return inherited_tuning()

def validation_plan(d):
 t=inherited_tuning();ledger=read(HERE/'VALIDATION_SEED_LEDGER.json')
 if len(ledger['validation'])!=20 or len(set(ledger['validation']))!=20:raise RuntimeError('validation seed allocation')
 for arm in ARMS:
  params=d['historical_theta'] if arm=='historicalP16' else t['selected_params']
  for h in HEADS:
   for c,s in enumerate(ledger['validation']):
    for o in (0,1):
     tag=f'validation_{arm}_{h}_c{c:02d}_o{o}';reqs=[request(arm,h,s,o,params,True)]
     yield tag,reqs,dict(stage='validation',arm=arm,head=h,cluster=c,orientation=o)

def validation(executor):
 d=pins();t=tuning_receipt();records=[];tasks=[]
 for tag,reqs,meta in validation_plan(d):
  prior=verified(tag,reqs)
  if prior:records.append(prior)
  else:tasks.append((tag,reqs,meta,executor.gate))
 records+=list(executor.tasks(tasks))
 if len(records)!=400:raise RuntimeError('validation allocation mismatch')
 result=validation_result(records)
 if (HERE/'VALIDATION.json').exists():
  if read(HERE/'VALIDATION.json')!=result:raise RuntimeError('validation receipt drift')
 else:exclusive(HERE/'VALIDATION.json',result)
 return result

def validation_result(records):
 t=tuning_receipt()
 return dict(status='COMPLETE',fights=400,tuning_sha256=tuning_hash(),selected_params=t['selected_params'],omega0_duplicate=t['selected_params']['omega_ranged']==0,records={r['tag']:sha(RAW/(r['tag']+'_COMPLETE.json')) for r in records},declaration_sha256=sha(HERE/'DECLARATION.json'))

def validation_receipt():
 # Caller owns an attempt or has called spent() before entering this read-only check.
 d=pins();audit_raw();records=[]
 for tag,requests,meta in validation_plan(d):
  r=verified(tag,requests)
  if r is None or r['meta']!=meta:raise RuntimeError('validation completion missing/cell drift: '+tag)
  records.append(r)
 if len(records)!=400:raise RuntimeError('validation allocation mismatch')
 expected=validation_result(records)
 if read(HERE/'VALIDATION.json')!=expected:raise RuntimeError('validation receipt drift')
 return expected

def main():
 parser=argparse.ArgumentParser();parser.add_argument('stage',choices=('validate',));args=parser.parse_args()
 d=pins();spent();engineering=read(HERE/'ENGINEERING.json')
 if sha(HERE/'ENGINEERING.json')!=d['engineering_sha256'] or engineering['binary']!=admit(BINARY):raise RuntimeError('engineering receipt drift')
 RAW.mkdir(exist_ok=True);audit_raw()
 # Already completed stages verify through reconstruction; they need no process gate or fights.
 if args.stage=='validate':tuning_receipt()
 complete=sum(len(read(p)['summaries']) for p in RAW.glob('*_COMPLETE.json'))
 if args.stage=='validate' and (HERE/'VALIDATION.json').exists():
  validation_receipt()
  print('Validation completion verified; no fights');return
 estimate=spent()+(VALIDATION_FIGHTS-complete)*.062+120
 write(HERE/'PROJECTION_BEFORE_FIGHTS.json',dict(projected_seconds=estimate,cap_seconds=3600,remaining_fights=VALIDATION_FIGHTS-complete,inherited_conservative_seconds_per_fight=.062,analysis_reserve_s=120))
 if estimate>3600:raise TimeoutError('pre-fight projection exceeds 3600 s')
 gate=process_gate(wait=True)
 with attempt(args.stage,gate) as (dl,prior,start):
  stage_name='validation'
  stage_done=sum(len(read(p)['summaries']) for p in RAW.glob('*_COMPLETE.json') if read(p)['meta']['stage']==stage_name)
  stage_batches=400-stage_done
  executor=Executor(dl,gate,prior,start,VALIDATION_FIGHTS-complete,stage_batches)
  try:validation(executor)
  finally:executor.close()
if __name__=='__main__':caffeinate();main()
