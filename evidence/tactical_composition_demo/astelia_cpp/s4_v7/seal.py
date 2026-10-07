"""One pre-fight seal, development entropy only, no mutable design/plan pins."""
import secrets
from common import *
from protocol import *

def seal():
 started=time.monotonic()
 if (HERE/'SEAL.json').exists():pins();print('Existing seal verified');return
 if (HERE/'DECLARATION.json').exists() or (HERE/'raw').exists():raise RuntimeError('partial seal or execution artifacts; stop')
 expected=read(REPO/'research/rrg/v0.2.1.expected.json')
 for name,known in expected['expected_sha256'].items():
  if sha(REPO/'research/rrg/v0.2.1'/name)!=known:raise RuntimeError('current audited RRG source mismatch: '+name)
 release=REPO/'research/rrg/v0.2.1';manifest=read(release/'MANIFEST.json')
 if len(manifest['files'])!=23:raise RuntimeError('RRG manifest allocation drift')
 for row in manifest['files']:
  p=release/row['path']
  if sha(p)!=row['sha256'] or p.stat().st_size!=row['bytes']:raise RuntimeError('RRG manifest mismatch: '+row['path'])
 for line in (release/'SHA256SUMS.txt').read_text().splitlines():
  known,name=line.split(maxsplit=1)
  if sha(release/name.lstrip('*'))!=known:raise RuntimeError('RRG checksum mismatch: '+name)
 engineering=read(HERE/'ENGINEERING.json')
 if engineering['status']!='PASS' or engineering['binary']!=admit(BINARY):raise RuntimeError('engineering not current')
 # Inherit executable bounds/order exactly; importing the tuner does not run fights.
 from s4_v6 import BOUNDS as inherited, cma
 if list(BOUNDS.items())!=list(inherited['resonator'].items()) or cma.__version__!='4.5.0':raise RuntimeError('inherited optimizer contract drift')
 used=set();prior={}
 def collect(v):
  if type(v) is int:used.add(v)
  elif isinstance(v,list):
   for x in v:collect(x)
  elif isinstance(v,dict):
   for x in v.values():collect(x)
 candidates=list(CPP.glob('*SEEDS*.json'))+list(CPP.glob('*/DEVELOPMENT_SEED_LEDGER.json'))
 candidates+=list(CPP.glob('s4_*probe_v*/DECLARATION.json'))
 # Explicit inherited development inventory includes pre-v6 development entropy.
 earlier=read(CPP/'s4_collective_probe_v1/DECLARATION.json')['previous_development_ledgers']
 candidates += [REPO/n for n in earlier]
 for p in sorted(set(candidates)):
  if p.parent==HERE or 'JUDG' in str(p).upper() or p.name=='S4_SEED_LEDGER.json':continue
  collect(read(p));prior[str(p.relative_to(REPO))]=sha(p)
 seeds=[]
 while len(seeds)<29:
  s=0xC0000000+secrets.randbelow(0x40000000)
  if s not in used and s not in seeds:seeds.append(s)
 ledger=dict(status='FRESH_DEVELOPMENT_ONLY',tuning=seeds[:8],validation=seeds[8:28],optimizer_seed=1+secrets.randbelow(2**31-2),engineering_seed=seeds[28],prior_development_inventory=prior,judging_ledger_read=False)
 exclusive(HERE/'DEVELOPMENT_SEED_LEDGER.json',ledger)
 start=read(CPP/'s4_escort_probe_v3/REGULAR_REQUEST_TEMPLATE.json')['options']['ai'][0]['params'];normalized(start)
 for head in HEADS:
  template=read(CPP/'s4_escort_probe_v3'/(head.upper()+'_REQUEST_TEMPLATE.json'))
  exclusive(HERE/(head.upper()+'_REQUEST_TEMPLATE.json'),template)
 hashes={}
 paths=[CPP/n for n in admit(BINARY)['sources']]
 paths += list(HERE.glob('*.py'))+list(HERE.glob('*.md'))+list(HERE.glob('*REQUEST_TEMPLATE.json'))
 paths += [HERE/'DEVELOPMENT_SEED_LEDGER.json',CPP/'s4_escort_probe_v3/metrics.py',CPP/'s4_v6.py',CPP/'s4_v4.py',CPP/'s4_deadline.py',CPP/'build_admission.py',REPO/'research/rrg/CURRENT.md',REPO/'research/rrg/v0.2.1.expected.json']
 paths += list((REPO/'research/rrg/v0.2.1').rglob('*'))
 paths += list(pathlib.Path(cma.__file__).parent.rglob('*.py'))
 for p in paths:
  if p.is_file() and p.name not in FORBIDDEN:hashes[str(p.relative_to(REPO))]=sha(p)
 exclusive(HERE/'DECLARATION.json',dict(status='SEALED_BEFORE_FIGHTS',created_utc=utc(),design_commit='01f6c05',base_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),binary=admit(BINARY),hashes=hashes,ledger_sha256=sha(HERE/'DEVELOPMENT_SEED_LEDGER.json'),historical_theta=start,knob_order=list(BOUNDS),bounds=BOUNDS,optimizer=dict(version=cma.__version__,seed=ledger['optimizer_seed'],sigma=.25,population=16,generations=16,evaluations=257,initial_ordinal=0,earlier_ordinal_ties=True),fights=dict(tuning=8224,validation=400),workers=10,compute_cap_s=3600,bootstrap=dict(seed=20261007,resamples=10000,interval='95% percentile, linear interpolation'),arms=ARMS,heads=HEADS,engineering_sha256=sha(HERE/'ENGINEERING.json'),judging_ledger_read=False,readings='20.2 descriptive only; independent v7 owner criterion; comparator floor21; net count bands +/-3 and >=4; no cluster-majority rule',omega0='total parameter effect, not isolated timing; duplicated if selected omega==0'))
 exclusive(HERE/'SEAL.json',dict(declaration_sha256=sha(HERE/'DECLARATION.json'),created_utc=utc(),seconds=time.monotonic()-started));pins()
 print('Sealed 8 tuning +20 validation clusters; 257 evaluations; 400 validation fights; no fights run')
if __name__=='__main__':seal()
