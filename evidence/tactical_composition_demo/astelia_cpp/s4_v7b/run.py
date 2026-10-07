"""Claude executor: tuning/validation with sealed identities and no ambiguous replay."""
import argparse, gzip, threading
from common import *
from protocol import *
RAW=HERE/'raw'

def request(arm,head,seed,orientation,params,telemetry=False):
 req=read(HERE/(head.upper()+'_REQUEST_TEMPLATE.json'))
 req['options'].update(seed=seed,swapSides=bool(orientation),duration=150)
 req['options']['ai'][0].update(controller=arm,skeleton='v7',params=params)
 req.update(trace=False,diagnostics=False,killerTelemetry=telemetry,decisionTrace=telemetry,decisionDiagnostics=telemetry,attributionDiagnostics=telemetry)
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
 for tag in sorted(tags):verified(tag)

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
  # For tuning this is a two-orientation native batch; validation is a singleton.
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

def candidate(params,ordinal,executor):
 normalized(params);ledger=read(HERE/'DEVELOPMENT_SEED_LEDGER.json');tasks=[];prior=[]
 for h in HEADS:
  for c,s in enumerate(ledger['tuning']):
   tag=f'tune_e{ordinal:03d}_{h}_c{c:02d}';reqs=[request('v7',h,s,o,params) for o in (0,1)]
   item=verified(tag,reqs)
   if item:prior.append(item)
   else:tasks.append((tag,reqs,dict(stage='tuning',ordinal=ordinal,head=h,cluster=c),executor.gate))
 records=prior+list(executor.tasks(tasks));rows=[]
 for r in records:
  for o,s in enumerate(r['summaries']):rows.append(dict(head=r['meta']['head'],cluster=r['meta']['cluster'],orientation=o,summary=s))
 selected=selection(rows,ordinal)
 receipt=dict(ordinal=ordinal,params=params,selection=selected,records={r['tag']:sha(RAW/(r['tag']+'_COMPLETE.json')) for r in records},declaration_sha256=sha(HERE/'DECLARATION.json'))
 path=HERE/f'CANDIDATE_{ordinal:03d}.json'
 if path.exists():
  if read(path)!=receipt:raise RuntimeError('candidate identity drift')
 else:exclusive(path,receipt)
 return receipt

def tuning(executor):
 d=pins();ledger=read(HERE/'DEVELOPMENT_SEED_LEDGER.json')
 from s4_v6 import cma
 if cma.__version__!=d['optimizer']['version']:raise RuntimeError('optimizer drift')
 es=cma.CMAEvolutionStrategy(normalized(d['historical_theta']),.25,dict(bounds=[0,1],popsize=16,seed=ledger['optimizer_seed'],verbose=-9,verb_log=0))
 records=[candidate(d['historical_theta'],0,executor)];best=records[0]
 for generation in range(16):
  solutions=es.ask();batch=[]
  for i,x in enumerate(solutions):
   r=candidate(knobs(x),1+generation*16+i,executor);records.append(r);batch.append(r)
   if rank(r['selection'])<rank(best['selection']):best=r
  es.tell(solutions,cma_losses([r['selection'] for r in batch]))
  print(json.dumps(dict(generation=generation+1,best=best['selection'])),flush=True)
 if len(records)!=257:raise RuntimeError('257-evaluation budget mismatch')
 result=dict(status='SELECTED' if best['selection']['eligible'] else 'NOT_READY_NO_ELIGIBLE_CANDIDATE',selected=best,selected_params=best['params'],evaluations=257,accounted_fights=8224,candidates={str(r['ordinal']):sha(HERE/f"CANDIDATE_{r['ordinal']:03d}.json") for r in records},declaration_sha256=sha(HERE/'DECLARATION.json'))
 if (HERE/'TUNING.json').exists():
  if read(HERE/'TUNING.json')!=result:raise RuntimeError('tuning receipt drift')
 else:exclusive(HERE/'TUNING.json',result)
 return result

def tuning_receipt():
 d=pins();r=read(HERE/'TUNING.json')
 if r['evaluations']!=257 or r['accounted_fights']!=8224 or r['declaration_sha256']!=sha(HERE/'DECLARATION.json'):raise RuntimeError('invalid tuning completion')
 for n,h in r['candidates'].items():
  path=HERE/f'CANDIDATE_{int(n):03d}.json'
  if sha(path)!=h:raise RuntimeError('candidate receipt drift')
  value=read(path)
  for tag,known in value['records'].items():
   if sha(RAW/(tag+'_COMPLETE.json'))!=known:raise RuntimeError('candidate fight drift')
   verified(tag)
 best=min((read(HERE/f'CANDIDATE_{i:03d}.json') for i in range(257)),key=lambda v:rank(v['selection']))
 if best!=r['selected'] or best['params']!=r['selected_params']:raise RuntimeError('incumbent drift')
 return r

def validation(executor):
 d=pins();t=tuning_receipt();ledger=read(HERE/'DEVELOPMENT_SEED_LEDGER.json');records=[];tasks=[]
 for arm in ARMS:
  params=d['historical_theta'] if arm=='historicalP16' else t['selected_params']
  for h in HEADS:
   for c,s in enumerate(ledger['validation']):
    for o in (0,1):
     tag=f'validation_{arm}_{h}_c{c:02d}_o{o}';reqs=[request(arm,h,s,o,params,True)]
     prior=verified(tag,reqs)
     if prior:records.append(prior)
     else:tasks.append((tag,reqs,dict(stage='validation',arm=arm,head=h,cluster=c,orientation=o),executor.gate))
 records+=list(executor.tasks(tasks))
 if len(records)!=400:raise RuntimeError('validation allocation mismatch')
 result=dict(status='COMPLETE',fights=400,tuning_sha256=sha(HERE/'TUNING.json'),selected_params=t['selected_params'],omega0_duplicate=t['selected_params']['omega_ranged']==0,records={r['tag']:sha(RAW/(r['tag']+'_COMPLETE.json')) for r in records},declaration_sha256=sha(HERE/'DECLARATION.json'))
 if (HERE/'VALIDATION.json').exists():
  if read(HERE/'VALIDATION.json')!=result:raise RuntimeError('validation receipt drift')
 else:exclusive(HERE/'VALIDATION.json',result)
 return result

def main():
 parser=argparse.ArgumentParser();parser.add_argument('stage',choices=('tune','validate'));args=parser.parse_args()
 d=pins();engineering=read(HERE/'ENGINEERING.json')
 if sha(HERE/'ENGINEERING.json')!=d['engineering_sha256'] or engineering['binary']!=admit(BINARY):raise RuntimeError('engineering receipt drift')
 RAW.mkdir(exist_ok=True);audit_raw()
 # Already completed stages verify through reconstruction; they need no process gate or fights.
 if args.stage=='validate':tuning_receipt()
 complete=sum(len(read(p)['summaries']) for p in RAW.glob('*_COMPLETE.json'))
 if args.stage=='tune' and (HERE/'TUNING.json').exists():tuning_receipt();print('Tuning completion verified; no fights');return
 if args.stage=='validate' and (HERE/'VALIDATION.json').exists():
  r=read(HERE/'VALIDATION.json')
  if len(r['records'])!=400 or r['tuning_sha256']!=sha(HERE/'TUNING.json') or r['declaration_sha256']!=sha(HERE/'DECLARATION.json'):raise RuntimeError('validation drift')
  for tag,h in r['records'].items():
   if sha(RAW/(tag+'_COMPLETE.json'))!=h:raise RuntimeError('validation completion drift')
  print('Validation completion verified; no fights');return
 estimate=spent()+(FIGHTS-complete)*.062+120
 write(HERE/'PROJECTION_BEFORE_FIGHTS.json',dict(projected_seconds=estimate,cap_seconds=3600,remaining_fights=FIGHTS-complete,inherited_conservative_seconds_per_fight=.062,analysis_reserve_s=120))
 if estimate>3600:raise TimeoutError('pre-fight projection exceeds 3600 s')
 gate=process_gate(wait=True)
 with attempt(args.stage,gate) as (dl,prior,start):
  stage_name='tuning' if args.stage=='tune' else 'validation'
  stage_done=sum(len(read(p)['summaries']) for p in RAW.glob('*_COMPLETE.json') if read(p)['meta']['stage']==stage_name)
  stage_batches=(8224-stage_done)//2 if args.stage=='tune' else 400-stage_done
  executor=Executor(dl,gate,prior,start,FIGHTS-complete,stage_batches)
  try:tuning(executor) if args.stage=='tune' else validation(executor)
  finally:executor.close()
if __name__=='__main__':caffeinate();main()
