"""No simulation imports: identity, budget and mandatory process gate."""
import hashlib,json,pathlib,subprocess,time,os,sys,functools,signal
HERE=pathlib.Path(__file__).resolve().parent
CPP=HERE.parent
REPO=CPP.parents[2]
BINARY=CPP/'build/astelia_native_spacing_probe_v1'
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,v):pathlib.Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def pins():
 d=json.loads((HERE/'DECLARATION.json').read_text())
 for n,h in {**d['protected'],**d['implementation_hashes']}.items():assert sha(REPO/n)==h,('drift',n)
 assert sha(HERE/'DEVELOPMENT_SEED_LEDGER.json')==d['development_ledger_sha256']
 for head,expected in d['template_sha256'].items():assert sha(HERE/(head.upper()+'_REQUEST_TEMPLATE.json'))==expected
 return d
def caffeinate():
 if os.environ.get('SPACING_PROBE_CAFFEINATED')!='1':
  os.environ['SPACING_PROBE_CAFFEINATED']='1';os.execv('/usr/bin/caffeinate',['caffeinate','-i','-s',sys.executable,*sys.argv])
_stage_deadline=None
def remaining():
 used=120+sum(json.loads(p.read_text())['awake_seconds'] for p in HERE.glob('STAGE_*.json'))
 return min(3600-used,_stage_deadline-time.monotonic()) if _stage_deadline is not None else 3600-used
def pilot_gate(wait=False):
 # On macOS -f matches full argv; -l prints it. Match python processes, never our pgrep.
 pattern=r'(^|/|[[:space:]])[Pp]ython[^[:space:]]*[[:space:]].*(rev711_diag.*pilot|pilot.*rev711_diag|medium_variants.*telemetry|telemetry.*medium_variants)'
 start=time.time();attempts=[]
 while True:
  r=subprocess.run(['pgrep','-fl',pattern],capture_output=True,text=True,timeout=10)
  row=dict(utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),argv=['pgrep','-fl',pattern],returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
  attempts.append(row);status='CLEAR' if r.returncode==1 and not r.stderr.strip() else 'ACTIVE' if r.returncode==0 and not r.stderr.strip() else 'UNAVAILABLE'
  write(HERE/'PILOT_GATE.json',dict(status=status,attempts=attempts,wait_wall_seconds=time.time()-start))
  if status=='CLEAR':return
  if status=='UNAVAILABLE':raise RuntimeError('mandatory pgrep gate unavailable; no combat authorized')
  if not wait:raise RuntimeError('0h pilot active; wait before combat')
  print('Waiting for active 0h pilot batch; next pgrep in30s',flush=True);time.sleep(30)

def stage(name,cap=1200,scope='development preparation/execution'):
 def decorate(fn):
  @functools.wraps(fn)
  def wrapped(*args,**kwargs):
   global _stage_deadline
   allowance=min(cap,remaining());assert allowance>0, 'total compute cap exhausted before stage'
   start=time.monotonic();wall=time.time();_stage_deadline=start+allowance
   suffix='';index=1
   while (HERE/('STAGE_'+name+suffix+'.json')).exists():index+=1;suffix='_'+str(index).zfill(2)
   path=HERE/('STAGE_'+name+suffix+'.json');ok=False;error=None
   def expired(*_):raise TimeoutError('absolute '+name+' stage/total compute cap')
   previous=signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,allowance)
   try:
    result=fn(*args,**kwargs)
    if remaining()<=0:raise TimeoutError('late stage completion exceeds cap')
    ok=True;return result
   except BaseException as e:error=type(e).__name__+': '+str(e);raise
   finally:
    signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous);_stage_deadline=None
    write(path,dict(stage=name,status='PASS' if ok else 'STOP',returncode=0 if ok else 1,error=error,scope=scope,cap_seconds=allowance,awake_seconds=time.monotonic()-start,elapsed_seconds=time.time()-wall))
  return wrapped
 return decorate
