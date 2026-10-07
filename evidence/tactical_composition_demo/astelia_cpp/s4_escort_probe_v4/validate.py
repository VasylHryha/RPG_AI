"""Final delivery audit, no combat/process listing."""
from common import *
def main():
 d=pins();identity=checked_binary();assert identity==d['exact_v3']['binary_identity']
 assert not (HERE/'raw').exists() and not (HERE/'ENGINEERING.json').exists() and not list(HERE.glob('PILOT_GATE_*.json'))
 assert (REPO/'docs/reviews/tactical_0g_escort_probe_v3_recheck_codex.md').read_text().startswith('APPROVE')
 assert (HERE/'OWNER_RECHECK.md').read_text().startswith('APPROVE')
 assert json.loads((HERE/'COMPACT.json').read_text())['status']=='NOT_RUN'
 assert len(d['development_seeds'])==20 and len(set(d['development_seeds']+[d['engineering_seed']]))==21
 used=set()
 def collect(v):
  if type(v) is int:used.add(v)
  elif isinstance(v,list):
   for x in v:collect(x)
  elif isinstance(v,dict):
   for x in v.values():collect(x)
 ledger=json.loads((HERE/'DEVELOPMENT_SEED_LEDGER.json').read_text())
 for name,h in ledger['previous_development_ledgers'].items():
  assert 'JUDG' not in name.upper() and pathlib.Path(name).name!='S4_SEED_LEDGER.json'
  assert sha(REPO/name)==h;collect(json.loads((REPO/name).read_text()))
 assert not (set(d['development_seeds']+[d['engineering_seed']])&used)
 assert 'docs/PLAN_CURRENT.md' not in d['protected'] and 'evidence/tactical_composition_demo/DESIGN_0G.md' not in d['protected']
 excluded={'VALIDATION.json','GIT_WRITABILITY.json','COMMIT.log','BUNDLE_VERIFY.log','DELIVERY_TRANSPORT.json'}
 files=[p for p in sorted(HERE.iterdir()) if p.is_file() and p.suffix!='.bundle' and p.name not in excluded]
 files += [p for p in sorted((CPP/'s4_escort_probe_v3_recheck_codex').iterdir()) if p.is_file()]
 files += [CPP/'s4_escort_probe_v3/S4_ESCORT_PROBE.md',REPO/'docs/reviews/tactical_0g_escort_probe_v3_recheck_codex.md']
 assert all(p.stat().st_size<=45_000_000 for p in files)
 write(HERE/'VALIDATION.json',dict(status='PASS',scope='stored v3 recount and noncombat v4 replication preparation; Claude combat pending',utc=utc(),checked_hashes={str(p.relative_to(REPO)):sha(p) for p in files},binary_identity=identity,protected_files_verified=len(d['protected']),engineering='NOT_RUN',combat='NOT_RUN',judging_ledger_read=False,limits=['Separate Codex implementation recheck is same-family; Claude CLI is not logged in','No combat or process listing executed; engineering and 160 replication fights belong to Claude']))
 print('PASS: sealed source/binary identity, fresh development ledger, checks, NOT_RUN and delivery files')
if __name__=='__main__':main()
