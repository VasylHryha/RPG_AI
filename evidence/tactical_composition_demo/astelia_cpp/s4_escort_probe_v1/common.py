"""Identity, atomic receipts, cumulative budget and mandatory fail-closed pgrep."""
import contextlib,functools,hashlib,json,os,pathlib,signal,subprocess,sys,time,uuid
HERE=pathlib.Path(__file__).resolve().parent
CPP=HERE.parent
REPO=CPP.parents[2]
BINARY=CPP/'build/astelia_native_escort_probe_v1'
sys.path.insert(0,str(CPP))
from build_admission import admit
from s4_deadline import Deadline,BoundedPool

def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def utc():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
def write(p,v):
 p=pathlib.Path(p);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
 with tmp.open('x') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def exclusive(p,v):
 with pathlib.Path(p).open('x') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def pins():
 d=json.loads((HERE/'DECLARATION.json').read_text());seal=json.loads((HERE/'SEAL.json').read_text())
 assert sha(HERE/'DECLARATION.json')==seal['declaration_sha256'],'declaration drift'
 for n,h in {**d['protected'],**d['implementation_hashes']}.items():assert sha(REPO/n)==h,('drift',n)
 assert sha(HERE/'POLICY.md')==d['policy_sha256']
 assert sha(HERE/'DEVELOPMENT_SEED_LEDGER.json')==d['development_ledger_sha256']
 for head,h in d['template_sha256'].items():assert sha(HERE/(head.upper()+'_REQUEST_TEMPLATE.json'))==h
 return d
_stage_deadline=None
def spent():return sum(json.loads(p.read_text())['awake_seconds'] for p in HERE.glob('STAGE_*.json'))
def remaining():
 available=3600-spent()
 return min(available,_stage_deadline-time.monotonic()) if _stage_deadline else available
def caffeinate():
 if os.environ.get('ESCORT_PROBE_CAFFEINATED')!='1':
  os.environ['ESCORT_PROBE_CAFFEINATED']='1';os.execv('/usr/bin/caffeinate',['caffeinate','-i','-s',sys.executable,*sys.argv])
def pilot_gate(wait=True):
 pattern=r'(^|/|[[:space:]])[Pp]ython[^[:space:]]*[[:space:]].*(rev711_diag.*pilot|pilot.*rev711_diag|medium_variants.*telemetry|telemetry.*medium_variants)'
 path=HERE/('PILOT_GATE_'+uuid.uuid4().hex+'.json');start=time.monotonic();rows=[]
 while True:
  argv=['pgrep','-fl',pattern]
  try:
   r=subprocess.run(argv,capture_output=True,text=True,timeout=10)
   status='CLEAR' if r.returncode==1 and not r.stderr.strip() else 'ACTIVE' if r.returncode==0 and not r.stderr.strip() else 'UNAVAILABLE'
   row=dict(utc=utc(),argv=argv,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
  except (OSError,subprocess.TimeoutExpired) as e:status='UNAVAILABLE';row=dict(utc=utc(),argv=argv,error=str(e))
  rows.append(row);write(path,dict(status=status,attempts=rows,utc_start=rows[0]['utc'],utc_end=utc(),wait_wall_seconds=time.monotonic()-start,declaration_sha256=sha(HERE/'DECLARATION.json') if (HERE/'DECLARATION.json').exists() else None,binary=admit(BINARY) if BINARY.exists() else None))
  if status=='CLEAR':return dict(path=str(path.relative_to(HERE)),sha256=sha(path))
  if status=='UNAVAILABLE':raise RuntimeError('mandatory pgrep unavailable; STOP before combat')
  if not wait:raise RuntimeError('0h batch active; STOP before combat')
  print('Waiting for 0h pilot batches; recheck in30s',flush=True);time.sleep(30)
def stage(name,cap=1200):
 def decorate(fn):
  @functools.wraps(fn)
  def wrapped(*a,**kw):
   global _stage_deadline
   group='run_' if name.startswith('run_') else name+'_'
   prior=sum(json.loads(p.read_text())['awake_seconds'] for p in HERE.glob('STAGE_'+group+'*.json'))
   allowance=min(cap-prior,remaining());assert allowance>0,'stage/compute cap exhausted'
   begin=utc();start=time.monotonic();_stage_deadline=start+allowance;error=None
   path=HERE/('STAGE_'+name+'_'+uuid.uuid4().hex+'.json')
   def expired(*_):raise TimeoutError(name+' stage/total compute cap')
   previous=signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,allowance)
   try:return fn(*a,**kw)
   except BaseException as e:error=type(e).__name__+': '+str(e);raise
   finally:
    signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous);_stage_deadline=None
    write(path,dict(stage=name,status='STOP' if error else 'PASS',error=error,utc_start=begin,utc_end=utc(),cap_seconds=allowance,awake_seconds=time.monotonic()-start))
  return wrapped
 return decorate
@contextlib.contextmanager
def owned_deadline():
 deadline=Deadline(time.monotonic()+remaining());timer=__import__('threading').Timer(remaining(),deadline.stop);timer.daemon=True;timer.start()
 try:yield deadline
 finally:timer.cancel();deadline.stop()
