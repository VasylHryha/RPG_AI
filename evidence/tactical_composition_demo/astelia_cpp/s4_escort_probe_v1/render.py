"""Render available evidence; never turn missing combat into a result."""
from common import *
FIELDS=('elimination_wins','timeouts','S','enemy_guns_destroyed','own_guns_lost','own_losses','ranged_enemy_ranged_last_hits_lt20','ranged_enemy_ranged_last_hits_lt30','early_nearest_enemy_ranged','targeting_share','gun_HP_by_source_and_time','ranged_losses_and_killers','victims_per_shell_both_teams','raw_clipped_arrival','clearance_collisions_and_spacing')
def main():
 d=pins();complete=(HERE/'SUMMARY.json').exists() and (HERE/'FIGHTS.json').exists()
 if complete:
  c=json.loads((HERE/'COMPACT.json').read_text());assert c['fights_sha256']==sha(HERE/'FIGHTS.json') and c['declaration_sha256']==sha(HERE/'DECLARATION.json')
 else:
  partial=json.loads((HERE/'PARTIAL.json').read_text()) if (HERE/'PARTIAL.json').exists() else []
  claims=list((HERE/'raw').glob('*_CLAIM.json')) if (HERE/'raw').exists() else []
  rows=[]
  for arm in d['arms']:
   for head in d['heads']:
    subset=[r for r in partial if (r['arm'],r['head'])==(arm,head)]
    rows.append(dict(arm=arm,head=head,completed_fights=len(subset),measurements={f:dict(status='not_analyzed' if subset else 'not_run',value=None,reason='Combat execution/analysis reserved for Claude; see stage and gate receipts') for f in FIELDS}))
  c=dict(status='PARTIAL' if partial or claims else 'NOT_RUN',completed_fights=len(partial),declared_fights=120,P11_sanity=json.loads((HERE/'P11_SANITY.json').read_text()) if (HERE/'P11_SANITY.json').exists() else dict(status='NOT_RUN',reason='Fresh control not executed'),engineering=json.loads((HERE/'ENGINEERING.json').read_text())['status'] if (HERE/'ENGINEERING.json').exists() else 'NOT_RUN',rows=rows,reading='No outcome reading applies until all sealed measurements are available',entropy_claimed=bool(claims))
  write(HERE/'COMPACT.json',c)
 text=c['status']+'\n\nFresh P11 control first: '+json.dumps(c['P11_sanity'])+'\n\n'
 if complete:
  text+='| Arm/head | Wins /20 | Timeouts | Mean S | Gun kills / own gun losses | Own losses | Own/enemy shell victims | Raw/clipped arrival |\n|---|---|---|---|---|---|---|---|\n'
  for r in c['rows']:
   text+=f"| {r['arm']} {r['head']} | {r['elimination_wins']} | {r['timeouts']} | {r['mean_S']} | {r['mean_enemy_guns_destroyed']} / {r['mean_own_guns_lost']} | {r['mean_own_losses']} | {r['sides'][0]['gun_victims_per_successful_shell']} / {r['sides'][1]['gun_victims_per_successful_shell']} | {r['escort']['raw_arrival_fraction']} / {r['escort']['clipped_arrival_fraction']} |\n"
  for r in c['rows']:text+='\n'+r['arm']+' '+r['head']+': '+json.dumps(dict(escort=r['escort'],spacing=r['spacing_audit'],own_ranged_killers=r['own_ranged_killers']))+'\n'
  text+='\nDeclared descriptive readings: '+json.dumps(c['reading'])+'\n'
 else:
  text+=f"Completed panel fights {c['completed_fights']}/120; engineering {c['engineering']}; entropy claimed {c['entropy_claimed']}. Combat is reserved for Claude.\n\n"
  for r in c['rows']:text+=r['arm']+' '+r['head']+': '+json.dumps(r['measurements'])+'\n\n'
 text+='\nP11 is exactly the historical native spacing controller S60. P12/P13 change only ranged movement: nearest living own gun, threat within inclusive400, deterministic centroid/nearest-gun fallback, raw d60/d120, native-clipped goal, full multiplier iff error>2, stop0. Targeting is prepared v6; dead/degenerate fallthrough is complete. No collision correction or avoidance. Arrival does not prove splash safety. Own spacing lost means opponent-shell own-gun multiplicity>1.5; null is unavailable. No population-rate, v7 permission, judging, acceptance or resonator/source claim.\n\n'
 text+='See [POLICY.md](POLICY.md), [DECLARATION.json](DECLARATION.json), [VALIDATION.json](VALIDATION.json), [OWNER_RECHECK.md](OWNER_RECHECK.md) and [COMPACT.json](COMPACT.json). Raw claims/requests/results and interrupted streams stay local and gitignored. Resume with engineering.py, run.py, analyze.py, render.py in that order; every unexecuted combat block/resume rechecks pgrep and waits for0h. Verified completions are skipped; possibly executed/ambiguous fights are never replayed. No script edits are needed.\n'
 (HERE/'S4_ESCORT_PROBE.md').write_text(text)
if __name__=='__main__':caffeinate();main()
