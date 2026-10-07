"""One-time fresh development entropy + immutable precombat declaration."""
import secrets
from common import *
def main():
 begin=utc();awake=time.monotonic()
 assert not (HERE/'DECLARATION.json').exists() and not (HERE/'raw').exists() and not (HERE/'SEAL.json').exists()
 prior=json.loads((CPP/'s4_spacing_probe_v1/DECLARATION.json').read_text());collective=json.loads((CPP/'s4_collective_probe_v1/DECLARATION.json').read_text())
 used=set();ledgers={}
 def collect(v):
  if type(v) is int:used.add(v)
  elif isinstance(v,list):
   for x in v:collect(x)
  elif isinstance(v,dict):
   for x in v.values():collect(x)
 names=list(collective['previous_development_ledgers'])
 names += [str(p.relative_to(REPO)) for p in sorted(CPP.glob('*/DEVELOPMENT_SEED_LEDGER.json')) if p.parent!=HERE]
 # Development-only probe declarations carry separate engineering entropy.
 names += [str(p.relative_to(REPO)) for p in sorted(CPP.glob('s4_*probe_v*/DECLARATION.json')) if p.parent!=HERE]
 for name in sorted(set(names)):
  assert 'JUDG' not in name.upper() and pathlib.Path(name).name!='S4_SEED_LEDGER.json'
  p=REPO/name;collect(json.loads(p.read_text()));ledgers[name]=sha(p)
 seeds=[]
 while len(seeds)<11:
  s=0xC0000000+secrets.randbelow(0x40000000)
  if s not in used and s not in seeds:seeds.append(s)
 catalog=CPP/'src/native/catalog_data.h';data=json.loads(catalog.read_text().split('R"astelia(',1)[1].split(')astelia"',1)[0]);g=data['GAME']['artillery'];r=data['GAME']['ranged'];assert (g['radius'],g['r'],r['r'])==(40,10,9)
 write(HERE/'DEVELOPMENT_SEED_LEDGER.json',dict(status='fresh development only; unconsumed until per-fight claim after pgrep',seeds=seeds[:10],engineering_seed=seeds[10],previous_development_ledgers=ledgers,collision_check='all prior development integers plus own11 unique',judging_ledger_read=False))
 for head in ('regular','novice'):
  req=json.loads((CPP/'s4_spacing_probe_v1'/(head.upper()+'_REQUEST_TEMPLATE.json')).read_text());req['options']['seed']=seeds[0];req['options']['ai'][0].update(controller='P12',skeleton='escort_probe_v3');write(HERE/(head.upper()+'_REQUEST_TEMPLATE.json'),req)
 tracked=subprocess.check_output(['git','ls-files','-z'],cwd=REPO).decode().split('\0')
 protected={n:sha(REPO/n) for n in tracked if n and (REPO/n).is_file() and (n.startswith(('evidence/tactical_composition_demo/astelia_cpp/','research/rrg/')) or n in ('AGENTS.md','STATUS.json','docs/PLAN_CURRENT.md','evidence/tactical_composition_demo/DESIGN_0G.md')) and 'JUDG' not in n.upper() and pathlib.Path(n).name!='S4_SEED_LEDGER.json'}
 protected['docs/reviews/tactical_0g_s1911_probe_review_codex.md']=sha(REPO/'docs/reviews/tactical_0g_s1911_probe_review_codex.md')
 impl={str(p.relative_to(REPO)):sha(p) for p in sorted(HERE.iterdir()) if p.suffix in ('.py','.cpp','.h') or p.name in ('POLICY.md','.gitignore')}
 write(HERE/'DECLARATION.json',dict(clarifications=dict(P16='ordering only: descending inclusive prepare V, ascending HP/id; preserve reachable sets, union-reachable anchor/global fallback, v6 soft target, focus geometry, P11 spacing and pre-spacing multiplier',V='living enemies any role, count centre distance<=40+observed victim radius, includes gun; static footprint, not release/impact prediction',P17='melee movement only using unchanged P12 geometry-only helper; d60, clip, error>2, stop0; unavailable direction complete P12',phase='accepted prepare with both living batteries; clear all overrides each prepare',control='P12 all40 first, broad bounds flag-only, novice20 expected flag-only',chosen_V='sum/count over prepare own gun ticks selecting living enemy gun; focus/anchor separately, null on zero',shell_success='own gun-targeted shell succeeds on positive capped opposing HP of ANY role; distinct opposing victims, role breakdown, gun-only success denominator separate, unique attribution or STOP',melee_arrival='all prepare living own melee during both-battery phase; raw/clipped <=20 post centres; degenerate and post deaths unavailable/nonarrival; baseline arms hypothetical goal diagnostic only',gun_curve_samples_s=[10,20,30,45,60],curves='death<=sample; terminal survivors held',reading='regular>=10 and>=P12+3 clearly above; observed owner requires BOTH heads>=11 and BOTH means S>0, no controller/integration failures; ten paired clusters, no v7 permission',historical_motivation='10.5/5.8 are P11 win/nonwin associations; P12 is14.5/10.71; neither causal'),exact_P12=dict(controller='EscortProbeV1 arm12',source_hashes={str((CPP/'s4_escort_probe_v1'/n).relative_to(REPO)):sha(CPP/'s4_escort_probe_v1'/n) for n in ('escort.cpp','escort.h')},declaration_sha256=sha(CPP/'s4_escort_probe_v1/DECLARATION.json')),status='DECLARED_BEFORE_FIGHTS',created_utc=utc(),design_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),development_seeds=seeds[:10],engineering_seed=seeds[10],arms=['P12','P16','P17'],heads=['regular','novice'],orientations=[0,1],controlled_team=0,knobs=prior['knobs'],catalog=dict(path=str(catalog.relative_to(REPO)),sha256=sha(catalog),splash_px=40,gun_body_px=10,ranged_body_px=9,melee_body_px=data['GAME']['melee']['r'],unrounded_d_px=59),parameters=dict(S_P11=60,d_P12=60,d_P17=60,clipped_error_tolerance_px=2,arrival_tolerance_px=20,threat_cutoff_px=400,degenerate_length_px=1e-9,workers=2,total_compute_cap_s=3600,stage_cap_s=1200,analysis_reserve_s=600),protected=protected,implementation_hashes=impl,policy_sha256=sha(HERE/'POLICY.md'),development_ledger_sha256=sha(HERE/'DEVELOPMENT_SEED_LEDGER.json'),template_sha256={h:sha(HERE/(h.upper()+'_REQUEST_TEMPLATE.json')) for h in ('regular','novice')},judging_ledger_read=False))
 exclusive(HERE/'SEAL.json',dict(declaration_sha256=sha(HERE/'DECLARATION.json'),utc=utc(),status='SEALED_BEFORE_FIGHTS'))
 exclusive(HERE/('STAGE_seal_'+uuid.uuid4().hex+'.json'),dict(stage='seal',status='PASS',utc_start=begin,utc_end=utc(),awake_seconds=time.monotonic()-awake))
 print('Sealed10 fresh unused development seeds + separate engineering seed; no fights.')
if __name__=='__main__':main()
