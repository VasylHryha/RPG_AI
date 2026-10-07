"""Read-only final identity/scope/entropy audit; no combat or simulation execution."""
from common import *

def verify():
 d=pins();old=CPP/'s4_v7';v7=read(old/'DECLARATION.json');preservation=read(HERE/'PRESERVATION.json')
 for name,expected in preservation['preserved_hashes'].items():
  if sha(REPO/name)!=expected:raise RuntimeError('preserved file changed: '+name)
 for row in preservation['raw']:
  p=REPO/row['path']
  if sha(p)!=row['sha256'] or p.stat().st_mtime_ns!=row['mtime_ns']:raise RuntimeError('v7 raw changed: '+row['path'])
 staged=subprocess.check_output(['git','diff','--cached','--binary','--','docs/PLAN_CURRENT.md'],cwd=REPO)
 if hashlib.sha256(staged).hexdigest()!=preservation['plan_staged_diff_sha256']:raise RuntimeError('unrelated plan staging changed')
 for name in ('protocol.py','analyze.py','render.py','NOVICE_REQUEST_TEMPLATE.json','REGULAR_REQUEST_TEMPLATE.json'):
  if (HERE/name).read_bytes()!=(old/name).read_bytes():raise RuntimeError('scientific contract changed: '+name)
 scientific_keys=('design_commit','historical_theta','knob_order','bounds','fights','workers','compute_cap_s','bootstrap','arms','heads','judging_ledger_read','readings','omega0')
 for key in scientific_keys:
  if d[key]!=v7[key]:raise RuntimeError('scientific declaration drift: '+key)
 for key in v7['optimizer']:
  if key!='seed' and d['optimizer'][key]!=v7['optimizer'][key]:raise RuntimeError('optimizer contract drift: '+key)
 if d['binary']!=v7['binary']:raise RuntimeError('sealed binary/source identity changed')
 prefix=str(CPP.relative_to(REPO))+'/'
 for name,h in v7['binary']['sources'].items():
  blob=subprocess.check_output(['git','show','23ba9fc:'+prefix+name],cwd=REPO)
  if hashlib.sha256(blob).hexdigest()!=h:raise RuntimeError('source differs from sealed commit: '+name)
 ledger=read(HERE/'DEVELOPMENT_SEED_LEDGER.json');used=set()
 def collect(value):
  if type(value) is int:used.add(value)
  elif isinstance(value,list):
   for v in value:collect(v)
  elif isinstance(value,dict):
   for v in value.values():collect(v)
 for name,h in ledger['prior_development_inventory'].items():
  if 'JUDG' in name.upper() or pathlib.Path(name).name=='S4_SEED_LEDGER.json':raise RuntimeError('judging ledger in development inventory')
  if sha(REPO/name)!=h:raise RuntimeError('prior entropy inventory drift: '+name)
  collect(read(REPO/name))
 if str((old/'DEVELOPMENT_SEED_LEDGER.json').relative_to(REPO)) not in ledger['prior_development_inventory']:raise RuntimeError('v7 entropy exclusion missing')
 fresh=ledger['tuning']+ledger['validation']+[ledger['engineering_seed'],ledger['optimizer_seed']]
 if len(ledger['tuning'])!=8 or len(ledger['validation'])!=20 or len(fresh)!=len(set(fresh)) or set(fresh)&used:raise RuntimeError('fresh entropy overlap/allocation')
 if ledger['judging_ledger_read'] is not False:raise RuntimeError('judging entropy reused')
 if any(pathlib.Path(name).name in FORBIDDEN for name in d['hashes']):raise RuntimeError('mutable authority pinned')
 if (HERE/'raw').exists() or list(HERE.glob('ATTEMPT_*.json')) or (HERE/'TUNING.json').exists() or (HERE/'VALIDATION.json').exists():raise RuntimeError('unexpected combat attempt in delivery')
 r=dict(status='PASS',noncombat=True,binary=d['binary']['binary_sha256'],manifest=d['binary']['manifest_sha256'],scientific_contracts_identical=True,controller_sources_identical_to_23ba9fc=True,fresh_entropy_count=len(fresh),prior_v7_entropy_excluded=True,judging_ledger_read=False,preceding_v7_claims=preservation['claim_count'],preceding_v7_completions=preservation['completion_count'],preceding_v7_incomplete_claims=preservation['incomplete_claims'],v7_raw_and_protected_files_unchanged=True,mutable_authority_unpinned=True,combat_attempts=0)
 print(json.dumps(r,indent=2));return r
if __name__=='__main__':verify()
