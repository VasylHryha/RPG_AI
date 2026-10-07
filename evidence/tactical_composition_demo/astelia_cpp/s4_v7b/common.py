"""Identity fences, immutable receipts, owned deadlines and repository process gate."""
import contextlib, hashlib, json, math, os, pathlib, re, signal, subprocess, sys, threading, time, uuid
HERE=pathlib.Path(__file__).resolve().parent;CPP=HERE.parent;REPO=CPP.parents[2]
BINARY=HERE/'build/astelia_native_v7';sys.path.append(str(CPP))
from build_admission import admit
from s4_deadline import Deadline,BoundedPool
FORBIDDEN={'PLAN_CURRENT.md','DESIGN_0G.md','DESIGN_0H_REV7.md'}

def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def utc():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
def read(p):return json.loads(pathlib.Path(p).read_text())
def write(p,v):
 p=pathlib.Path(p);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
 with tmp.open('x') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def exclusive(p,v):
 with pathlib.Path(p).open('x') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def pins():
 d=read(HERE/'DECLARATION.json');s=read(HERE/'SEAL.json')
 if sha(HERE/'DECLARATION.json')!=s['declaration_sha256']:raise RuntimeError('declaration drift')
 for n,h in d['hashes'].items():
  if pathlib.Path(n).name in FORBIDDEN:raise RuntimeError('forbidden mutable document pin')
  if sha(REPO/n)!=h:raise RuntimeError('input drift: '+n)
 if admit(BINARY)!=d['binary']:raise RuntimeError('binary drift')
 return d

def caffeinate():
 if os.environ.get('S4_V7_CAFFEINATED')!='1':
  os.environ['S4_V7_CAFFEINATED']='1';os.execv('/usr/bin/caffeinate',['caffeinate','-i','-s',sys.executable,*sys.argv])

def process_pattern():
 # Anchor the EXECUTABLE, so a concurrent pgrep containing this pattern cannot match.
 root=re.escape(str(REPO))
 py=r'([^[:space:]]*/)?[Pp]ython[0-9.]*[[:space:]]+'
 location=r'('+root+r'/|\./?evidence/tactical_composition_demo/|evidence/tactical_composition_demo/)'
 rootedpy=root+r'/\.venv/bin/[Pp]ython[0-9.]*([[:space:]]|$)'
 relativepy=r'(\./)?\.venv/bin/[Pp]ython[0-9.]*([[:space:]]|$)'
 native=location+r'[^[:space:]]*astelia_native[^[:space:]]*([[:space:]]|$)'
 return r'^('+rootedpy+r'|'+relativepy+r'|'+py+r'([^[:space:]]+[[:space:]]+)*'+location+r'[^[:space:]]*|'+native+r')'

def process_gate(wait=True):
 path=HERE/('GATE_'+uuid.uuid4().hex+'.json');attempts=[];start=time.monotonic()
 while True:
  argv=['pgrep','-fl',process_pattern()]
  try:
   p=subprocess.run(argv,text=True,capture_output=True,timeout=10)
   active=[]
   if p.returncode==0 and not p.stdout.strip():raise ValueError('pgrep zero with empty output')
   if p.returncode==0 and not p.stderr.strip():
    for line in p.stdout.splitlines():
     pieces=line.split(None,1)
     if len(pieces)!=2 or not pieces[0].isdigit():raise ValueError('unparseable pgrep output')
     if int(pieces[0])!=os.getpid():active.append(line)
   status='CLEAR' if p.returncode==1 and not p.stderr.strip() or p.returncode==0 and not p.stderr.strip() and not active else 'ACTIVE' if p.returncode==0 and not p.stderr.strip() else 'UNAVAILABLE'
   row=dict(utc=utc(),argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,active=active)
  except (OSError,subprocess.TimeoutExpired,ValueError) as e:status='UNAVAILABLE';row=dict(utc=utc(),argv=argv,error=str(e))
  attempts.append(row);write(path,dict(status=status,attempts=attempts,wait_wall_seconds=time.monotonic()-start,declaration_sha256=sha(HERE/'DECLARATION.json'),binary=admit(BINARY)))
  if status=='CLEAR':return dict(path=path.name,sha256=sha(path))
  if status=='UNAVAILABLE':raise RuntimeError('mandatory process gate unavailable; STOP before fights')
  if not wait:raise RuntimeError('repository python/native work active; STOP before fights')
  print('Waiting for repository work, including 0h rev711_diag/medium_variants batches; next check in 30 s',flush=True);time.sleep(30)

def spent():
 total=read(HERE/'ENGINEERING.json')['total_seconds'] if (HERE/'ENGINEERING.json').exists() else 0
 if (HERE/'SEAL.json').exists():total+=read(HERE/'SEAL.json').get('seconds',0)
 for p in HERE.glob('ATTEMPT_*.json'):
  r=read(p)
  if r['status']=='RUNNING':raise RuntimeError('unclosed attempt; compute/resume ambiguous: '+p.name)
  total+=r['seconds']
 return total

@contextlib.contextmanager
def attempt(stage,gate):
 prior=spent();remaining=3600-prior
 if remaining<=0:raise TimeoutError('cumulative 3600 s cap exhausted')
 start=time.monotonic();path=HERE/('ATTEMPT_'+uuid.uuid4().hex+'.json')
 initial=dict(stage=stage,status='RUNNING',utc_start=utc(),prior_seconds=prior,allowance_seconds=remaining,gate=gate,declaration_sha256=sha(HERE/'DECLARATION.json'),binary=admit(BINARY))
 exclusive(path,initial);dl=Deadline(start+remaining);timer=threading.Timer(remaining,dl.stop);timer.daemon=True;timer.start();error=None
 def expired(*_):raise TimeoutError('cumulative 3600 s cap')
 previous=signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,remaining)
 try:yield dl,prior,start
 except BaseException as e:error=type(e).__name__+': '+str(e);raise
 finally:
  signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous);timer.cancel();dl.stop();write(path,dict(initial,status='STOP' if error else 'PASS',error=error,seconds=time.monotonic()-start,utc_end=utc()))

def projection_warmup(stage_batches):
 if type(stage_batches) is not int or stage_batches<1:raise ValueError('positive stage batch allocation required')
 return min(10,math.ceil(stage_batches*.05))

def project(prior,start,done,total,batches,stage_batches):
 elapsed=time.monotonic()-start
 if not all(math.isfinite(x) for x in (prior,elapsed)) or prior<0 or elapsed<=0:raise ValueError('invalid projection time')
 if any(type(x) is not int for x in (done,total,batches)) or not 0<batches<=stage_batches or not batches<=done<=total:raise ValueError('invalid projection completion count')
 threshold=projection_warmup(stage_batches)
 # Counts include every worker completion in this attempt, never cached fights.
 # The rate is already aggregate wall throughput; do not multiply by workers.
 ready=batches>=threshold
 rate=done/elapsed if ready else None
 projected=prior+elapsed+(total-done)/rate+120 if ready else None
 write(HERE/'PROJECTION.json',dict(status='PROJECTED' if ready else 'WARMUP',projected_seconds=projected,cap_seconds=3600,prior_seconds=prior,elapsed_wall_seconds=elapsed,completed_this_attempt=done,completed_batches_this_attempt=batches,stage_batches_remaining_at_start=stage_batches,warmup_batches=threshold,completed_fights_per_wall_second=rate,total_remaining_at_start=total,analysis_reserve_s=120))
 if prior+elapsed>=3600:raise TimeoutError('cumulative 3600 s cap exhausted')
 if ready and projected>3600:raise TimeoutError('projected compute exceeds 3600 s; preserve completions')
