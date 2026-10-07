"""Read-only preservation, scientific identity and fresh entropy verification."""
from common import *
from prepare import collect

def tree(root):
 rows=[]
 for p in sorted(root.rglob('*')):
  if p.is_file() and not any(x in ('__pycache__','delivery') for x in p.relative_to(root).parts):rows.append([str(p.relative_to(root)),sha(p),p.stat().st_mtime_ns])
 return dict(files=len(rows),tree_sha256=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest())

def preservation():
 baseline=read(HERE/'PRESERVATION.json')
 for name,h in baseline['protected'].items():
  if sha(REPO/name)!=h:raise RuntimeError('protected document changed: '+name)
 for name,snapshot in baseline['trees'].items():
  if tree(REPO/name)!=snapshot:raise RuntimeError('preserved tree bytes/mtime changed: '+name)
 staged=subprocess.check_output(['git','diff','--cached','--binary','--','docs/PLAN_CURRENT.md'],cwd=REPO)
 if hashlib.sha256(staged).hexdigest()!=baseline['plan_staged_diff_sha256']:raise RuntimeError('plan staging changed')

def entropy():
 ledger=read(HERE/'VALIDATION_SEED_LEDGER.json');used=set()
 for name,h in ledger['prior_development_inventory'].items():
  if 'JUDG' in name.upper() or pathlib.Path(name).name=='S4_SEED_LEDGER.json':raise RuntimeError('judging inventory forbidden')
  if sha(REPO/name)!=h:raise RuntimeError('prior entropy inventory drift')
  collect(read(REPO/name),used)
 for version in ('s4_v7','s4_v7b'):
  if str((CPP/version/'DEVELOPMENT_SEED_LEDGER.json').relative_to(REPO)) not in ledger['prior_development_inventory']:raise RuntimeError('prior validation entropy exclusion missing')
 fresh=ledger['validation']
 if len(fresh)!=20 or len(set(fresh))!=20 or set(fresh)&used or any(type(s) is not int or not 0xC0000000<=s<=0xffffffff for s in fresh):raise RuntimeError('fresh validation entropy overlap/allocation')
 if ledger['judging_ledger_read'] is not False or ledger['tuning_entropy_allocated'] is not False:raise RuntimeError('invalid entropy scope')

def verify():
 d=pins();preservation();entropy();inherited_tuning()
 old=read(ORIGIN/'DECLARATION.json')
 for key in ('design_commit','historical_theta','knob_order','bounds','workers','bootstrap','arms','heads','readings','omega0','projection'):
  if d[key]!=old[key]:raise RuntimeError('scientific declaration drift: '+key)
 if d['binary']!=old['binary']:raise RuntimeError('native source/binary identity changed')
 for name in ('protocol.py','NOVICE_REQUEST_TEMPLATE.json','REGULAR_REQUEST_TEMPLATE.json'):
  if (HERE/name).read_bytes()!=(ORIGIN/name).read_bytes():raise RuntimeError('scientific template/rules drift: '+name)
 if d['fights']!={'tuning':0,'validation':400} or d['compute_cap_s']!=3600 or d['retuning'] is not False:raise RuntimeError('validation scope drift')
 if any(pathlib.Path(n).name in FORBIDDEN for n in d['hashes']):raise RuntimeError('mutable authority pinned')
 if (HERE/'raw').exists() or list(HERE.glob('ATTEMPT_*.json')) or (HERE/'TUNING.json').exists() or (HERE/'VALIDATION.json').exists():raise RuntimeError('unexpected combat artifacts in delivery')
 audit=read(HERE/'REQUEST_AUDIT.json')
 if audit['requests']!=400 or audit['executed_fights'] or audit['executed_steps'] or audit['worlds_created']:raise RuntimeError('noncombat audit invalid')
 result=dict(status='PASS',combat_attempts=0,executed_fights=0,executed_steps=0,native_parsed_requests=400,binary=d['binary']['binary_sha256'],selected_ordinal=161,retuning=False,fresh_validation_clusters=20,scientific_rules_unchanged=True,protected_trees_unchanged=True,mutable_authority_unpinned=True,judging_ledger_read=False)
 print(json.dumps(result,indent=2));return result

if __name__=='__main__':verify()
