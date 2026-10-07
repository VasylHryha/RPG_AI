"""One-time declaration; refuses any previous declaration or raw claim."""
import json,secrets,subprocess,time,re
from common import *
def main():
 assert not (HERE/'DECLARATION.json').exists() and not (HERE/'raw').exists()
 prior=json.loads((CPP/'s4_collective_probe_v1/DECLARATION.json').read_text())
 used=set();ledgers={}
 def collect(v):
  if type(v) is int:used.add(v)
  elif isinstance(v,list):
   for x in v:collect(x)
  elif isinstance(v,dict):
   for x in v.values():collect(x)
 names=list(prior['previous_development_ledgers'])+[str((CPP/'s4_collective_probe_v1/DEVELOPMENT_SEED_LEDGER.json').relative_to(REPO))]
 for name in names:
  if 'JUDG' in name.upper() or pathlib.Path(name).name=='S4_SEED_LEDGER.json':continue
  p=REPO/name;collect(json.loads(p.read_text()));ledgers[name]=sha(p)
 seeds=[]
 while len(seeds)<11:
  s=0xC0000000+secrets.randbelow(0x40000000)
  if s not in used and s not in seeds:seeds.append(s)
 catalog=CPP/'src/native/catalog_data.h';data=json.loads(catalog.read_text().split('R"astelia(',1)[1].split(')astelia"',1)[0]);gun=data['GAME']['artillery'];S10=2*(gun['radius']+gun['r']);S11=gun['radius']+2*gun['r'];assert (S10,S11)==(100,60)
 tracked=subprocess.check_output(['git','ls-files','-z'],cwd=REPO).decode().split('\0')
 protected={n:sha(REPO/n) for n in tracked if n and (REPO/n).is_file() and (n.startswith(('evidence/tactical_composition_demo/astelia_cpp/','geomind/','experiments/','milestones/','research/rrg/')) or n in ('AGENTS.md','STATUS.json','pyproject.toml','uv.lock','docs/PLAN_CURRENT.md','evidence/tactical_composition_demo/DESIGN_0G.md'))}
 write(HERE/'DEVELOPMENT_SEED_LEDGER.json',dict(status='fresh development only; unconsumed until raw/CLAIMED_ONCE.json',seeds=seeds[:10],engineering_seed=seeds[10],previous_development_ledgers=ledgers,judging_ledger_read=False))
 for head in ('regular','novice'):
  req=json.loads((CPP/'s4_collective_probe_v1'/(head.upper()+'_REQUEST_TEMPLATE.json')).read_text());req['options']['seed']=seeds[0];req['options']['ai'][0].update(controller='P5',skeleton='spacing_probe_v1');write(HERE/(head.upper()+'_REQUEST_TEMPLATE.json'),req)
 impl={str(p.relative_to(REPO)):sha(p) for p in sorted(HERE.iterdir()) if p.suffix in ('.py','.cpp','.h','.md')}
 write(HERE/'DECLARATION.json',dict(status='DECLARED_BEFORE_FIGHTS',created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),design_commit='c123ec59333e7e470146a4b052a0137f77fe0bbc',development_seeds=seeds[:10],engineering_seed=seeds[10],arms=['P5','P10','P11'],heads=['regular','novice'],orientations=[0,1],controlled_team=0,knobs=prior['knobs'],catalog=dict(path=str(catalog.relative_to(REPO)),sha256=sha(catalog),splash_px=gun['radius'],body_px=gun['r']),parameters=dict(S_P10=S10,S_P11=S11,workers=2,total_compute_cap_s=3600,stage_cap_s=1200,preparation_reserve_s=120,analysis_reserve_s=600,commit_margin_px=12),protected=protected,implementation_hashes=impl,policy_sha256=sha(HERE/'POLICY.md'),development_ledger_sha256=sha(HERE/'DEVELOPMENT_SEED_LEDGER.json'),template_sha256={h:sha(HERE/(h.upper()+'_REQUEST_TEMPLATE.json')) for h in ('regular','novice')},judging_ledger_read=False))
 print('Declared10 fresh development clusters and one engineering seed; no fights.')
if __name__=='__main__':main()
