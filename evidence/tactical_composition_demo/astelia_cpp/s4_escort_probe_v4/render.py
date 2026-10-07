"""Render replication receipt or explicit NOT_RUN; no combat."""
from common import *
def paired_table(pairs):
 text='| Head/cluster | P12 o0/o1 (win,S) | P16 o0/o1 (win,S) | P12 wins/2 | P16 wins/2 | Win difference | P12 mean S | P16 mean S | S difference |\n|---|---|---|---|---|---|---|---|---|\n'
 for r in pairs:
  vals={a:'; '.join(f"o{v['orientation']}: {'win' if v['win'] else 'nonwin'},{v['S']}" for v in r['orientations'][a]) for a in ('P12','P16')}
  text+=f"| {r['head']} c{r['cluster']:02d} | {vals['P12']} | {vals['P16']} | {r['wins']['P12']} | {r['wins']['P16']} | {r['win_difference']['P16']} | {r['mean_S']['P12']} | {r['mean_S']['P16']} | {r['mean_S_difference']['P16']} |\n"
 return text

def main():
 d=pins();complete=(HERE/'ANALYSIS_VERIFICATION.json').exists()
 if complete:
  receipt=json.loads((HERE/'ANALYSIS_VERIFICATION.json').read_text());assert receipt['status']=='PASS' and receipt['declaration_sha256']==sha(HERE/'DECLARATION.json') and receipt['fights_sha256']==sha(HERE/'FIGHTS.json') and receipt['inventory_sha256']==sha(HERE/'RAW_FILES_LOCAL.json')
  for name,h in receipt['output_hashes'].items():assert sha(HERE/name)==h
  c=json.loads((HERE/'COMPACT.json').read_text())
 else:
  from run import all_completions
  partial=all_completions(d) if (HERE/'raw').exists() else []
  c=dict(status='PARTIAL' if partial else 'NOT_RUN',completed_fights=len(partial),declared_fights=160,P12_sanity=json.loads((HERE/'P12_SANITY.json').read_text()) if (HERE/'P12_SANITY.json').exists() else dict(status='NOT_RUN'),engineering='PASS' if (HERE/'ENGINEERING.json').exists() else 'NOT_RUN',rows=[dict(arm=a,head=h,completed_fights=sum(r['arm']==a and r['head']==h for r in partial),measurements='not_analyzed' if any(r['arm']==a and r['head']==h for r in partial) else 'not_run') for a in d['arms'] for h in d['heads']],reading='Not available until all 160 fights and sealed measurements are verified',entropy_claimed=any((HERE/'raw').glob('*_CLAIM.json')))
  write(HERE/'COMPACT.json',c)
 text=c['status']+'\n\nFresh P12 control first: '+json.dumps(c['P12_sanity'])+'\n\n'
 if complete:
  text+='| Arm/head | Wins /40 | Timeouts | Mean S | Enemy guns destroyed | Own guns lost | Own losses |\n|---|---|---|---|---|---|---|\n'
  for r in c['rows']:text+=f"| {r['arm']} {r['head']} | {r['elimination_wins']} | {r['timeouts']} | {r['mean_S']} | {r['mean_enemy_guns_destroyed']} | {r['mean_own_guns_lost']} | {r['mean_own_losses']} |\n"
  text+='\nMechanism measurements (prepare-target V and actual impact multiplicity use different clocks):\n\n| Arm/head | Chosen gun V | All-role victims per successful gun-targeted shell | Artillery screen kills <20 / <30 s | Gun survival at 10,20,30,45,60 s |\n|---|---|---|---|---|\n'
  for r in c['rows']:
   counts=r['escort']['counts'];text+=f"| {r['arm']} {r['head']} | {r['gun_values']['mean_chosen_target_V']} | {r['escort_shells']['all_opposing_victims_per_successful_own_gun_targeted_shell']} | {counts.get('artillery_enemy_ranged_last_hits_lt20',0)} / {counts.get('artillery_enemy_ranged_last_hits_lt30',0)} | {', '.join(str(v['mean_alive']) for v in r['gun_survival'])} |\n"
  text+='\n'+paired_table(c['paired_clusters'])+'\nDeclared replication reading: '+json.dumps(c['reading'])+'\n'
  # Preserve full inherited measurements/denominators rather than hiding diagnostics.
  for r in c['rows']:text+='\n'+r['arm']+' '+r['head']+' complete measurements: '+json.dumps(r)+'\n'
 else:
  text+=f"Completed panel fights {c['completed_fights']}/160; engineering {c['engineering']}; entropy claimed {c['entropy_claimed']}. Combat is reserved for Claude. All outcome and mechanism measurements are {('not_analyzed' if c['completed_fights'] else 'not_run')}; no replication reading applies.\n\n"
  for r in c['rows']:text+=json.dumps(r)+'\n\n'
 text+='\nP12 and P16 reuse the exact v3 sources and executable. Replicated requires P16 regular >=26/40, positive regular and novice mean S, novice >=21/40, no failures, and more wins than paired P12 in >=12 of 20 regular clusters. Regular <=20/40 is Not replicated; otherwise a failed conjunction is descriptive. Orientations share cluster entropy; uncertainty is computed across 20 cluster averages, not 40 independent trials. No rule/constant changes after any fight. No judging, registration, scientific acceptance or resonator claim. A replicated result supplies the owner-directed scripted witness for revising v7; the draft v7 is not thereby approved.\n\nSee POLICY.md, DECLARATION.json, SEAL.json, README.md and OWNER_RECHECK.md. Claude runs engineering.py, run.py, analyze.py and render.py in order without edits. Each missing combat block/resume checks mandatory pgrep; unavailable process access stops before claiming entropy. Verified completions are skipped; ambiguous possibly executed fights stop and are never replayed. PLAN_CURRENT.md and DESIGN_0G.md are outside the seal.\n'
 (HERE/'S4_ESCORT_PROBE.md').write_text(text)
if __name__=='__main__':main()
