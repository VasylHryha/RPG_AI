#!/usr/bin/env python3
"""Focused stored-data consistency and immutable-input checks; no engine tests."""
import json,pathlib,subprocess
from analyze import HERE,SOURCE,sha,dump
REPO=HERE.parents[3]
def main():
 old=json.loads((SOURCE/'COMPACT.json').read_text());new=json.loads((HERE/'COMPACT.json').read_text());shell=json.loads((HERE/'SHELL_ATTRIBUTION.json').read_text())
 for c in new['cells']:
  o=next(q for q in old['rows'] if (q['arm'],q['head'])==(c['arm'],c['head']))
  assert (c['n'],c['wins'],c['mean_S'],c['mean_own_losses'])==(o['fights'],o['elimination_wins'],o['mean_S'],o['mean_own_losses'])
  killers={k.replace('enemy_','1_').replace('friendly_','0_'):v for k,v in c['own_ranged_killers'].items()};assert killers==o['own_ranged_killers']
  for b,binrow in enumerate(o['escort']['gun_hp_loss_bins']):
   hp={r['source'].replace('opposing_','enemy_'):r['hp'] for r in c['damage'] if r['bin']==b and r['target']=='own_artillery'};assert hp==binrow['hp'],(c['arm'],c['head'],b)
  def count(k):return sum(r['ticks'] for r in c['selection'] if r['metric']==k)
  assert count('eligible')==o['escort']['counts']['prepare_living_ranged_ticks']
  assert count('opportunity')==o['escort']['counts']['target_opportunity_ticks']
  assert count('selected_threat')==o['escort']['counts']['threat_selected_ticks']
  sc=next(q for q in shell['cells'] if (q['arm'],q['head'])==(c['arm'],c['head']))
  for source in ('enemy','own'):
   launches=sum(r['launches'] for r in c['shell_launches'] if r['source']==source)
   assert launches==sum(r['value'] for r in sc['shells'] if r['source']==source and r['metric']=='shells')
   for target in ('own_artillery','own_ranged','own_melee','enemy_artillery','enemy_ranged','enemy_melee'):
    team=source if target.startswith('own_') else ('own' if source=='enemy' else 'enemy')
    damage_source=('opposing_' if team=='enemy' else 'friendly_')+'artillery'
    # For enemy victims, opposing/friendly is relative to their team.
    actual=sum(r['hp'] for r in c['damage'] if r['target']==target and r['source']==damage_source)
    attributed=sum(r['value'] for r in sc['shells'] if r['source']==source and r['metric']=='hp_to_'+target)
    assert actual==attributed,(source,target,actual,attributed)
 # All original committed probe receipts/scripts except explicitly editable report.
 bound=subprocess.check_output(['git','ls-tree','-r','--name-only','0f8e823','--',str(SOURCE.relative_to(REPO))],cwd=REPO,text=True).splitlines()
 checked=[]
 for name in bound:
  if name.endswith('/S4_ESCORT_PROBE.md'):continue
  original=subprocess.check_output(['git','show','0f8e823:'+name],cwd=REPO)
  assert (REPO/name).read_bytes()==original,name;checked.append(name)
 assert (HERE/'OWNER_RECHECK.md').read_text().startswith('APPROVE')
 assert (REPO/'docs/reviews/tactical_0g_escort_probe_recheck_codex.md').read_text().startswith('APPROVE_WITH_NOTES')
 names=['docs/reviews/tactical_0g_escort_probe_recheck_codex.md',str((SOURCE/'S4_ESCORT_PROBE.md').relative_to(REPO)),str((HERE.parent/'S4_ESCORT_MECHANISM_DIAGNOSTIC.md').relative_to(REPO))]
 names += [str((HERE/n).relative_to(REPO)) for n in ['.gitignore','analyze.py','shell_attribution.py','render.py','validate.py','deliver.py','COMPACT.json','PER_FIGHT.json','SHELL_ATTRIBUTION.json','shell_attribution.log','OWNER_RECHECK.md','part1_recount.py','part1_recount.json','part1_recount.log','part1_supplemental_identity.py','part1_supplemental_identity.json']]
 for name in names:assert (REPO/name).stat().st_size<=45_000_000
 dump(HERE/'VALIDATION.json',dict(status='PASS',checks=['All six new cells agree with immutable original win/S/loss/gun-HP/killers/selection values','Exact shell attribution reconciles all artillery damage to every cohort for both sides','Every committed original probe input/receipt/script unchanged except authorized report','All deliverables below45MB; both reviewer verdicts approve with notes'],original_probe_files_preserved=checked,checked_hashes={n:sha(REPO/n) for n in names}))
 print('PASS: six cells, all artillery damage, original probe identity, scoped sizes/reviews')
if __name__=='__main__':main()
