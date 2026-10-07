"""Report completed measurements or explicit nonexecution; never invent values."""
from common import *
FIELDS=('elimination_wins','timeouts','S','enemy_guns_destroyed','own_guns_lost','own_losses','gun_victims_per_successful_shell_both_sides','nearest_own_gun_median_px','nearest_own_gun_p10_px','enemy_over_own_artillery_hp_ratio','already_dead_before_impact_both_sides','killers','realization_audits')
def main():
 if not (HERE/'FIGHTS.json').exists() or not (HERE/'SUMMARY.json').exists():
  gate=json.loads((HERE/'PILOT_GATE.json').read_text())
  partial=json.loads((HERE/'FIGHTS.json').read_text()) if (HERE/'FIGHTS.json').exists() else json.loads((HERE/'PARTIAL.json').read_text()) if (HERE/'PARTIAL.json').exists() else []
  raw=HERE/'raw';claims=raw.exists() and any(raw.glob('*CLAIMED_ONCE.json'))
  status='PARTIAL' if partial or claims else 'NOT_RUN'
  reason='Mandatory pgrep process-list gate '+gate['status']+'; no clearance for combat.' if gate['status']!='CLEAR' else 'Combat/analysis incomplete; see preserved stage receipts and raw records.'
  sanity=json.loads((HERE/'P5_SANITY.json').read_text()) if (HERE/'P5_SANITY.json').exists() else dict(status='NOT_RUN',reported_first=True,regular_own_gun_losses=None,regular_enemy_gun_kills=None,reason='P5 control block not completed')
  rows=[]
  for a in ('P5','P10','P11'):
   for h in ('regular','novice'):
    subset=[r for r in partial if (r['arm'],r['head'])==(a,h)]
    m={f:dict(status='not_analyzed' if subset else 'not_run',value=None,reason='stored raw measurement not analyzed' if subset else reason) for f in FIELDS}
    if subset:
     n=len(subset);summaries=[r['summary'] for r in subset]
     values=dict(elimination_wins=sum(x['enemySurvivors']==0 and x['survivors']>=1 and x['t']<150 for x in summaries),timeouts=sum(x['t']>=150 for x in summaries),S=sum(x['survivors']-x['enemySurvivors'] for x in summaries)/n,enemy_guns_destroyed=sum(10-x['artilleryAlive'][1] for x in summaries)/n,own_guns_lost=sum(10-x['artilleryAlive'][0] for x in summaries)/n,own_losses=sum(50-x['survivors'] for x in summaries)/n)
     m.update({k:dict(status='evaluated',value=v,reason=None) for k,v in values.items()})
    rows.append(dict(arm=a,head=h,completed_fights=len(subset),measurements=m))
  c=dict(status=status,completed_fights=len(partial),declared_fights=120,reason=reason,P5_sanity=sanity,rows=rows,reading='No §19.6 outcome reading applies: complete combat measurements are unavailable.',engineering_parity=json.loads((HERE/'ENGINEERING.json').read_text())['status'] if (HERE/'ENGINEERING.json').exists() else 'NOT_RUN',entropy_claimed=bool(claims))
  write(HERE/'COMPACT.json',c)
  files=[dict(path=str(p.relative_to(HERE)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(raw.iterdir()) if p.is_file()] if raw.exists() else []
  write(HERE/'RAW_FILES_LOCAL.json',dict(files=files,completed_fights=len(partial)))
 else:c=json.loads((HERE/'COMPACT.json').read_text())
 text=c['status']+'\n\nP5 sanity first: '+json.dumps(c['P5_sanity'])+'\n\n'
 if c['status']!='DONE':
  text+=c['reason']+' Completed development fights: '+str(c['completed_fights'])+'/120; engineering parity: '+c['engineering_parity']+'. Entropy claimed: '+str(c['entropy_claimed'])+'. No historical measurement substitutes for a new control.\n\n'
  text+='| Arm/head | Completed fights | Measurements |\n|---|---|---|\n'
  for row in c['rows']:
   text+=f"| {row['arm']} {row['head']} | {row['completed_fights']}/20 | "+'; '.join(k+': '+(str(v['value']) if v['status']=='evaluated' else v['status']) for k,v in row['measurements'].items())+' |\n'
  text+='\n'+c['reading']+'\n\n'
 else:
  text+='|Arm/head|Wins/timeouts|Mean S|Gun kills/own losses|All own losses|Victims/success own/enemy|Nearest own median/p10 px|Enemy/own artillery HP ratio|\n|---|---|---|---|---|---|---|---|\n'
  for r in c['rows']:text+=f"|{r['arm']} {r['head']}|{r['elimination_wins']}/{r['timeouts']}|{r['mean_S']}|{r['mean_enemy_guns_destroyed']}/{r['mean_own_guns_lost']}|{r['mean_own_losses']}|{r['sides'][0]['gun_victims_per_successful_shell']}/{r['sides'][1]['gun_victims_per_successful_shell']}|{r['nearest'][0]['median']}/{r['nearest'][0]['p10']}|{r['enemy_over_own_artillery_hp_ratio']}|\n"
  for r in c['rows']:text+='\n'+r['arm']+' '+r['head']+': dead-before-impact own/enemy '+str([s['already_dead_before_impact'] for s in r['sides']])+'; own gun killers '+json.dumps(r['own_gun_killers_by_team_role'])+'; realization '+json.dumps(r['audit'])+'; gun-range fractions '+str(r['gun_range_fraction'])+'.\n'
  text+='\n'+json.dumps(c['reading'])+'\n\n'
 text+='P10 S=100px, P11 S=60px, from GAME splash40/body10; literal simultaneous Cartesian sum on P5, unchanged targets/multiplier/stop. The sum can oppose308px commitment and push guns outside320px reach; P5 multiplier0 remains0. These are soft repulsion thresholds, with no dynamic separation guarantee. Clipping and impact timing remain native. The complete precombat measurement definitions, pooling, singularity conventions, outcome comparisons and yes/no stops are in [POLICY.md](s4_spacing_probe_v1/POLICY.md) and [DECLARATION.json](s4_spacing_probe_v1/DECLARATION.json).\n\n'
 text+='Implementation: new controller/host/factory, admitted native binary, bounded two-worker P5-first runner, stored-only analyzer, renderer and focused prepare-only fixtures. '+('Combat-based historical contract/parity checks remain gated and unverified for this delivery.' if c['status']=='NOT_RUN' else 'Combat-based historical contract/parity availability is recorded in ENGINEERING.json when present.')+' Historical tracked inputs/outputs retain their recorded SHA256; PLAN_CURRENT and DESIGN_0G are unchanged. [VALIDATION.json](s4_spacing_probe_v1/VALIDATION.json) records final checks and limitations. [COMPACT.json](s4_spacing_probe_v1/COMPACT.json) lists every measurement with availability. [OWNER_RECHECK.md](s4_spacing_probe_v1/OWNER_RECHECK.md) records the verbatim request and dispositions. Raw is local/gitignored, hashed in [RAW_FILES_LOCAL.json](s4_spacing_probe_v1/RAW_FILES_LOCAL.json); '+('no raw fights exist in this NOT_RUN delivery.' if c['status']=='NOT_RUN' else 'completed and interrupted raw records remain local.')+' No delivered file exceeds45MB.\n\n'
 text+='Resume only where process-list access works: `python3 s4_spacing_probe_v1/engineering.py` then `python3 s4_spacing_probe_v1/run.py`, `python3 s4_spacing_probe_v1/analyze.py`, `python3 s4_spacing_probe_v1/render.py`, from astelia_cpp, with caffeinate as declared. Both combat entrypoints repeat the mandatory pgrep gate. Do not replay a claimed seed ledger; do not alter rules after a fight. Finish a fresh owner recheck and validation before delivery of any future run.\n'
 (CPP/'S4_SPACING_PROBE.md').write_text(text)
if __name__=='__main__':
 from common import caffeinate
 caffeinate();main()
