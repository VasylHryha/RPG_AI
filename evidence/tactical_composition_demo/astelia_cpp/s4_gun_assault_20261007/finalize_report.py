"""Reproduce final explanatory prose from stored summaries, no combat or tests."""
import json
from common import *
import report

def main():
 report.main();path=CPP/'S4_GUN_ASSAULT_DIAGNOSTIC.md';s=path.read_text();summary=json.loads((HERE/'SUMMARY.json').read_text())
 novice=[v for k,v in summary.items() if k.endswith('|novice')];regular=[v for k,v in summary.items() if k.endswith('|regular')]
 gun_kills=sum(x['kills'] for v in novice for x in v['gun_killers'].values());artillery=sum(v['gun_killers'].get('0:artillery',{}).get('kills',0) for v in novice);ranged=sum(v['gun_killers'].get('0:ranged',{}).get('kills',0) for v in novice)
 phases=('early_0_20','middle_20_60','late_60_end')
 own_deaths=sum(x['kills'] for v in regular for p in phases for x in v['own_deaths_by_phase_killer'][p].values());enemy_artillery=sum(v['own_deaths_by_phase_killer'][p].get('1:artillery',{}).get('kills',0) for v in regular for p in phases);gun_only=sum(x['kills'] for v in regular for x in v['own_deaths_by_phase_killer']['gun_only'].values())
 text=f'The central attribution result: novice guns are killed overwhelmingly by our artillery, not by melee or direct gun assaults. Across the three arms, our guns deliver {artillery} of {gun_kills} gun kills ({100*artillery/gun_kills:.1f}%); ranged units deliver nine and melee units none. Enemy artillery also causes {enemy_artillery:,} of {own_deaths:,} own deaths against regular ({100*enemy_artillery/own_deaths:.1f}%). Only {gun_only} of those deaths occur in the separately defined gun-only phase, so the gun threat is already lethal during the mixed-army fight. These are exact lethal-source observations, not attribution from nearby units.\n\n'
 assert ranged==9
 s=s.replace('An elimination win requires',text+'An elimination win requires',1).replace('Enemy dodge decisions','Enemy dodge-goal returns')
 v6=summary['v6_resonator|regular']['approaches'];morale=summary['v6_morale|regular']['approaches'];v5=summary['v5_resonator|regular']['approaches']
 cover=[v['approaches']['entry_cover']['mean'] for v in regular]
 text=f'The regular entries rarely turn into exchanges with a gun. Only {v6["ever_reached_own_range"]:,}/{v6["count"]:,} v6 resonator episodes and {morale["ever_reached_own_range"]:,}/{morale["count"]:,} morale episodes ever reach the entrant’s own legal range; nine and 16 episodes respectively deal gun damage while open. V5 reaches own range in {v5["ever_reached_own_range"]:,}/{v5["count"]:,} episodes and deals damage in {v5["ever_dealt_damage"]}, but still has no regular elimination wins. Entrants are usually covered by several other gun bands (mean {min(cover):.2f}–{max(cover):.2f}), and most episodes end with the entrant dying. Pair counts repeat a unit across guns and across entries: they are not distinct casualty counts. Successful novice gun removal is mostly an artillery exchange, while direct entry counts alone do not demonstrate effective gun assault.\n\n'
 assert (v6['ever_dealt_damage'],morale['ever_dealt_damage'])==(9,16)
 s=s.replace('Regular dodge and line observations.',text+'Regular dodge and line observations.',1)
 checks=json.loads((HERE/'CHECK_TIMING.json').read_text());failed=json.loads((HERE/'FAILED_FIRST_CHECK_TIMING.json').read_text());run=json.loads((HERE/'RUN_TIMING.json').read_text());analysis=json.loads((HERE/'ANALYSIS_VERIFICATION.json').read_text())
 total=sum([checks['build']['elapsed_seconds'],checks['tests']['elapsed_seconds'],failed['build']['elapsed_seconds'],failed['tests']['elapsed_seconds'],run['elapsed_seconds'],analysis['elapsed_seconds']])
 s=s.replace('No code was edited during runs.',f'No code was edited during runs. Including the preserved initial build and failed test batch, measured build/test/combat/analysis compute was {total:.1f} s ({total/60:.2f} minutes); failed evidence is separate from final PASS accounting.')
 path.write_text(s);write(HERE/'REPORT_RENDER.json',dict(report_sha256=sha(path),base_renderer_sha256=sha(HERE/'report.py'),finalizer_sha256=sha(HERE/'finalize_report.py'),stored_inputs_sha256={n:sha(HERE/n) for n in ('SUMMARY.json','RUN_TIMING.json','ANALYSIS_VERIFICATION.json','PARITY.json','CHECK_TIMING.json','FAILED_FIRST_CHECK_TIMING.json')},fights_executed=0))
if __name__=='__main__':main()
