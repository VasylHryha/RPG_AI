"""One-time development-only entropy and exact v3 identity seal; no combat."""
import secrets
from common import *
def main():
 begin=utc();awake=time.monotonic()
 assert not any((HERE/n).exists() for n in ('DECLARATION.json','SEAL.json','raw'))
 old=CPP/'s4_escort_probe_v3';prior=json.loads((old/'DECLARATION.json').read_text())
 assert sha(old/'DECLARATION.json')==json.loads((old/'SEAL.json').read_text())['declaration_sha256']
 identity=admit(BINARY);assert identity==json.loads((old/'BUILD.json').read_text())['identity']==json.loads((old/'CHECKS.json').read_text())['binary_identity']
 for name,h in prior['implementation_hashes'].items():assert sha(REPO/name)==h
 used=set();ledgers={}
 def collect(v):
  if type(v) is int:used.add(v)
  elif isinstance(v,list):
   for x in v:collect(x)
  elif isinstance(v,dict):
   for x in v.values():collect(x)
 names=list(json.loads((CPP/'s4_collective_probe_v1/DECLARATION.json').read_text())['previous_development_ledgers'])
 names += [str(p.relative_to(REPO)) for pattern in ('*/DEVELOPMENT_SEED_LEDGER.json','s4_*probe_v*/DECLARATION.json') for p in sorted(CPP.glob(pattern)) if p.parent!=HERE]
 for name in sorted(set(names)):
  assert 'JUDG' not in name.upper() and pathlib.Path(name).name!='S4_SEED_LEDGER.json'
  p=REPO/name;collect(json.loads(p.read_text()));ledgers[name]=sha(p)
 seeds=[]
 while len(seeds)<21:
  seed=0xC0000000+secrets.randbelow(0x40000000)
  if seed not in used and seed not in seeds:seeds.append(seed)
 write(HERE/'DEVELOPMENT_SEED_LEDGER.json',dict(status='fresh development only; unconsumed until per-fight claim after pgrep',seeds=seeds[:20],engineering_seed=seeds[20],previous_development_ledgers=ledgers,collision_check='all prior declared development integers, plus own 21 unique',judging_ledger_read=False))
 for head in prior['heads']:
  req=json.loads((old/(head.upper()+'_REQUEST_TEMPLATE.json')).read_text());req['options']['seed']=seeds[0];write(HERE/(head.upper()+'_REQUEST_TEMPLATE.json'),req)
 # Pin actual executable/manifest, code, measurement dependencies, policy and ledgers.
 # Evolving plan/design/report documents are intentionally outside the seal.
 protected={name:sha(REPO/name) for name in prior['protected'] if pathlib.Path(name).suffix in ('.py','.cpp','.h') or name.startswith('research/rrg/')}
 protected.update(prior['implementation_hashes'])
 protected.update({str((old/n).relative_to(REPO)):sha(old/n) for n in ('DECLARATION.json','SEAL.json','DEVELOPMENT_SEED_LEDGER.json','REGULAR_REQUEST_TEMPLATE.json','NOVICE_REQUEST_TEMPLATE.json','BUILD.json','CHECKS.json')})
 protected.update(ledgers)
 for binary in (BINARY,CPP/'build/astelia_native_escort_probe_v1'):
  admit(binary)
  for p in (binary,binary.with_suffix('.build.json')):protected[str(p.relative_to(REPO))]=sha(p)
 for name in ('AGENTS.md','STATUS.json'):protected[name]=sha(REPO/name)
 assert 'docs/PLAN_CURRENT.md' not in protected and 'evidence/tactical_composition_demo/DESIGN_0G.md' not in protected
 impl={str(p.relative_to(REPO)):sha(p) for p in sorted(HERE.iterdir()) if p.suffix in ('.py','.cpp','.h') or p.name in ('POLICY.md','.gitignore','README.md')}
 write(HERE/'DECLARATION.json',dict(status='DECLARED_BEFORE_FIGHTS',created_utc=utc(),design_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),design_authority='DESIGN_0G 19.12 at 69e13a2; plan/design deliberately not pinned',exact_v3=dict(declaration_sha256=sha(old/'DECLARATION.json'),binary_identity=identity,implementation_hashes=prior['implementation_hashes'],policy_sha256=sha(old/'POLICY.md')),development_seeds=seeds[:20],engineering_seed=seeds[20],clusters=20,panel_fights=160,fights_per_cell=40,arms=['P12','P16'],heads=['regular','novice'],orientations=[0,1],controlled_team=0,knobs=prior['knobs'],catalog=prior['catalog'],parameters=dict(prior['parameters'],analysis_reserve_s=900),reading_rules=dict(replicated='P16 regular>=26/40 AND both means S>0 AND novice>=21/40 AND no failures AND P16>P12 in>=12/20 paired regular clusters',not_replicated='P16 regular<=20/40; all other non-replicated conjunction failures descriptive',uncertainty='Cluster averages of paired orientations; sample SD/sqrt(20), approximate t95 19 df factor2.093024054; unbounded descriptive interval, no population guarantee'),protected=protected,implementation_hashes=impl,policy_sha256=sha(HERE/'POLICY.md'),development_ledger_sha256=sha(HERE/'DEVELOPMENT_SEED_LEDGER.json'),template_sha256={h:sha(HERE/(h.upper()+'_REQUEST_TEMPLATE.json')) for h in prior['heads']},judging_ledger_read=False))
 exclusive(HERE/'SEAL.json',dict(status='SEALED_BEFORE_FIGHTS',declaration_sha256=sha(HERE/'DECLARATION.json'),utc=utc()))
 exclusive(HERE/('STAGE_seal_'+uuid.uuid4().hex+'.json'),dict(stage='seal',status='PASS',utc_start=begin,utc_end=utc(),awake_seconds=time.monotonic()-awake))
 print('Sealed 20 fresh development clusters + separate engineering seed; unchanged v3 binary; no combat.')
if __name__=='__main__':main()
