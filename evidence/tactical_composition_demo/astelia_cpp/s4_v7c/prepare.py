"""Allocate fresh validation entropy once, copy unchanged templates, pin committed theta."""
import secrets
from common import *

def collect(value,used):
 if type(value) is int:used.add(value)
 elif isinstance(value,list):
  for v in value:collect(v,used)
 elif isinstance(value,dict):
  for v in value.values():collect(v,used)

def prepare():
 if (HERE/'SEAL.json').exists():raise RuntimeError('already sealed; prepare forbidden')
 if (HERE/'THETA_ORIGIN.json').exists():raise RuntimeError('existing preparation; preserve and audit, never regenerate entropy')
 inputs=('TUNING.json','TUNING_ANALYSIS.json','DECLARATION.json')
 hashes={}
 for name in inputs:
  path=ORIGIN/name;blob=subprocess.check_output(['git','show',ORIGIN_COMMIT+':'+str(path.relative_to(REPO))],cwd=REPO)
  if hashlib.sha256(blob).hexdigest()!=sha(path):raise RuntimeError('origin differs from committed tuning: '+name)
  hashes[name]=sha(path)
 t=read(ORIGIN/'TUNING.json');historical=read(ORIGIN/'DECLARATION.json')['historical_theta']
 exclusive(HERE/'THETA_ORIGIN.json',dict(commit=ORIGIN_COMMIT,hashes=hashes,ordinal=161,selected_params=t['selected_params'],historical_theta=historical,retuning=False,validation_used=False))
 inherited_tuning()
 used=set();prior={}
 candidates=list(CPP.glob('*SEEDS*.json'))+list(CPP.glob('*/DEVELOPMENT_SEED_LEDGER.json'))+list(CPP.glob('*/VALIDATION_SEED_LEDGER.json'))+list(CPP.glob('s4_*probe_v*/DECLARATION.json'))
 candidates += [REPO/n for n in read(CPP/'s4_collective_probe_v1/DECLARATION.json')['previous_development_ledgers']]
 for p in sorted(set(candidates)):
  if p.parent==HERE or 'JUDG' in str(p).upper() or p.name=='S4_SEED_LEDGER.json':continue
  collect(read(p),used);prior[str(p.relative_to(REPO))]=sha(p)
 # v7b validation entropy is read ONLY for exclusion, never for request allocation.
 if str((ORIGIN/'DEVELOPMENT_SEED_LEDGER.json').relative_to(REPO)) not in prior:raise RuntimeError('v7b entropy exclusion missing')
 seeds=[]
 while len(seeds)<20:
  seed=0xC0000000+secrets.randbelow(0x40000000)
  if seed not in used and seed not in seeds:seeds.append(seed)
 exclusive(HERE/'VALIDATION_SEED_LEDGER.json',dict(status='FRESH_UNUSED_VALIDATION_ONLY',validation=seeds,prior_development_inventory=prior,judging_ledger_read=False,tuning_entropy_allocated=False))
 for head in ('regular','novice'):
  name=head.upper()+'_REQUEST_TEMPLATE.json'
  if (HERE/name).exists():raise RuntimeError('partial template already exists')
  (HERE/name).write_bytes((ORIGIN/name).read_bytes())
 print('Pinned committed ordinal 161; allocated 20 fresh unused validation clusters; no fights')

if __name__=='__main__':prepare()
