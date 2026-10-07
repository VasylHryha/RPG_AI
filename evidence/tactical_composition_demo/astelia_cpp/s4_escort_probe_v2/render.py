"""Render available evidence; never turn missing combat into a result."""
from common import *
FIELDS=('elimination_wins','timeouts','S','enemy_guns_destroyed','own_guns_lost','own_losses','ranged_enemy_ranged_last_hits_lt20','ranged_enemy_ranged_last_hits_lt30','early_nearest_enemy_ranged','targeting_share','gun_HP_by_source_and_time','ranged_losses_and_killers','victims_per_shell_both_teams','raw_clipped_arrival','clearance_collisions_and_spacing','escort_targeted_shell_multiplicity','artillery_enemy_ranged_last_hits_lt20_lt30','gun_survival_10_60','window_threat_opportunities_and_selection','P12_anchor_and_shifted_goal_arrival')
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
  c=dict(status='PARTIAL' if partial or claims else 'NOT_RUN',completed_fights=len(partial),declared_fights=120,P12_sanity=json.loads((HERE/'P12_SANITY.json').read_text()) if (HERE/'P12_SANITY.json').exists() else dict(status='NOT_RUN',reason='Fresh control not executed'),engineering=json.loads((HERE/'ENGINEERING.json').read_text())['status'] if (HERE/'ENGINEERING.json').exists() else 'NOT_RUN',rows=rows,reading='No outcome reading applies until all sealed measurements are available',entropy_claimed=bool(claims))
  write(HERE/'COMPACT.json',c)
 text=c['status']+'\n\nFresh P12 control first: '+json.dumps(c['P12_sanity'])+'\n\n'
 if complete:
  text+='| Arm/head | Wins /20 | Timeouts | Mean S | Gun kills / own gun losses | Own losses | Our shells→enemy guns / enemy shells→our guns | Raw/clipped arrival |\n|---|---|---|---|---|---|---|---|\n'
  for r in c['rows']:
   text+=f"| {r['arm']} {r['head']} | {r['elimination_wins']} | {r['timeouts']} | {r['mean_S']} | {r['mean_enemy_guns_destroyed']} / {r['mean_own_guns_lost']} | {r['mean_own_losses']} | {r['sides'][0]['gun_victims_per_successful_shell']} / {r['sides'][1]['gun_victims_per_successful_shell']} | {r['escort']['raw_arrival_fraction']} / {r['escort']['clipped_arrival_fraction']} |\n"
  for r in c['rows']:text+='\n'+r['arm']+' '+r['head']+': '+json.dumps(dict(escort=r['escort'],spacing=r['spacing_audit'],own_ranged_killers=r['own_ranged_killers'],escort_shells=r['escort_shells'],gun_survival=r['gun_survival']))+'\n'
  text+='\nDeclared descriptive readings: '+json.dumps(c['reading'])+'\n'
 else:
  text+=f"Completed panel fights {c['completed_fights']}/120; engineering {c['engineering']}; entropy claimed {c['entropy_claimed']}. Combat is reserved for Claude.\n\n"
  for r in c['rows']:text+=r['arm']+' '+r['head']+': '+json.dumps(r['measurements'])+'\n\n'
 text+='\nP12 is exactly native EscortProbeV1 arm12 (d60) from the sealed v1 source. P14 changes only ranged target priority to the nearest geometrically reachable enemy ranged threatening any own gun. P15 changes only ranged goals by simultaneous ascending-id current-centre repulsion below58px, lower-id -x/higher-id +x at exact coincidence; add to raw P12 goal then native clip, error>2 multiplier, stop0. P12 anchor and shifted-goal arrival are separate. Both batteries must be living at prepare and baseline integration accepted; no stale override. No global splash-safety claim. Successful enemy escort-targeted multiplicity counts distinct own ranged positively damaged per successful shell; null is unavailable. Gun curves remove deaths<=sample and hold terminal survivors after early endings. Twenty fights per arm/head share ten paired development clusters. No population-rate, v7 authorization, judging, acceptance or resonator/source claim.\n\n'
 text+='See [POLICY.md](POLICY.md), [DECLARATION.json](DECLARATION.json), [VALIDATION.json](VALIDATION.json), [OWNER_RECHECK.md](OWNER_RECHECK.md) and [COMPACT.json](COMPACT.json). Raw claims/requests/results and interrupted streams stay local and gitignored. Resume with engineering.py, run.py, analyze.py, render.py in that order; every unexecuted combat block/resume rechecks pgrep and waits for0h. Verified completions are skipped; possibly executed/ambiguous fights are never replayed. No script edits are needed.\n'
 (HERE/'S4_ESCORT_PROBE.md').write_text(text)
if __name__=='__main__':caffeinate();main()
