"""Render Markdown from committed JSON only; no raw trace or sealed runner import.

Run from any directory; --check compares the existing report without writing.
The fixed source commits prevent later HEAD movement from changing measurements.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
CPP = HERE.parents[1]
REPO = CPP.parents[2]
PREFIX = str(CPP.relative_to(REPO))
VALIDATION_COMMIT = 'e44b528'
TUNING_COMMIT = '796d0a8'
OUTPUT = CPP/'S4_V7_VALIDATION_REPORT.md'


def committed(commit, name):
    data = subprocess.check_output(['git','show',commit+':'+PREFIX+'/'+name],cwd=REPO)
    return json.loads(data), hashlib.sha256(data).hexdigest()


def table(lines, headers, rows):
    lines.extend(['', '| '+' | '.join(headers)+' |', '| '+' | '.join(['---']*len(headers))+' |'])
    lines.extend('| '+' | '.join(str(v) for v in row)+' |' for row in rows)


def fraction(a,b):
    return f'{a}/{b} ({a/b:.6f})' if b else 'not available (zero denominator)'


def build():
    a, ah = committed(VALIDATION_COMMIT,'s4_v7c/ANALYSIS.json')
    t, th = committed(TUNING_COMMIT,'s4_v7b/TUNING_ANALYSIS.json')
    v, vh = committed(VALIDATION_COMMIT,'s4_v7c/VALIDATION.json')
    tuning, tuning_h = committed(TUNING_COMMIT,'s4_v7b/TUNING.json')
    if a['validation_sha256']!=vh or a['tuning_sha256']!=tuning_h or t['tuning_sha256']!=tuning_h or v['selected_params']!=t['selected_params']:
        raise RuntimeError('committed source linkage mismatch')
    criterion = 'OBSERVED OWNER CRITERION MET' if a['readings']['observed_owner_criterion'] else 'OBSERVED OWNER CRITERION NOT MET'
    lines=[a['readings']['relative'].upper()+'; '+criterion, '',
           'Descriptive development validation. Generated exclusively from committed JSON; no fights, raw trace parsing, sealed render, or new allowance.', '',
           'Sources: validation/analysis and stored recovery records at `e44b528`; tuning at `796d0a8`. The source documents remain unchanged.', '',
           f'`ANALYSIS.json` SHA256: `{ah}`. `TUNING_ANALYSIS.json` SHA256: `{th}`.', '',
           f'Tuning: {t["evaluations"]} evaluations, {t["fights"]} fights, validation used: {str(t["validation_used"]).lower()}; selected ordinal {t["selected"]["ordinal"]}. Validation: {v["fights"]} fights on 20 fresh clusters × two orientations × five arms × two heads.']
    table(lines,['Knob at θ*','Value'],[(k,repr(x)) for k,x in t['selected_params'].items()])
    lines.extend(['','## Arm results','','A win requires enemy survivors = 0, own survivors ≥ 1 and termination before 150 s. S is own survivors minus enemy survivors. A timeout is a completed outcome, distinct from controller/numerical failure.'])
    table(lines,['Arm','Head','Wins / fights','Mean S','Mean own losses','Failures','Timeouts','Mean end time (s)'],
          [(x['arm'],x['head'],f'{x["wins"]}/{x["fights"]}',f'{x["mean_S"]:.3f}',f'{x["own_losses"]:.3f}',x['failures'],x['timeouts'],f'{x["mean_termination_time"]:.6f}') for x in a['cells']])
    lines.extend(['','forcedP16 is the matched always-commit action map at θ*. forcedv6 is always escape at θ*. ω0 changes the inherited artillery/ranged natural rate to zero. Historical P16 uses θ_v6 and is a separately labelled descriptive witness. All arms share the same paired validation seeds.','',
                  '## Declared readings','',
                  f'Net regular win difference v7 − forcedP16: {a["readings"]["win_difference"]:+d}/40. Comparator below floor: {str(a["readings"]["comparator_underperformance"]).lower()}. Positive / negative / tied regular clusters: {a["positive_clusters"]} / {a["negative_clusters"]} / {a["tied_clusters"]}.', '',
                  'The comparison uses the §20.2 count bands (improvement ≥ +4, match ±3, worse ≤ −4), conditional on forcedP16 ≥ 21/40. The owner criterion independently requires ≥ 21/40 on both heads, positive mean S on both heads and no failures.'])
    b=a['paired_cluster_bootstrap']
    lines.extend(['',f'Paired cluster-bootstrap win-rate difference: mean {b["mean"]:+.3f}, 95% descriptive percentile interval [{b["low"]:+.3f}, {b["high"]:+.3f}]; {b["resamples"]} resamples, seed {b["seed"]}, linear interpolation. Each resampled cluster retains both orientations.'])
    table(lines,['Regular orientation outcome (v7 / forcedP16)','Count'],[(k,x) for k,x in a['orientation_discordance'].items()])
    lines.extend(['','## Paired clusters','','Each entry gives wins across the two orientations; Δ is v7 − forcedP16. Cluster indices are zero based. Mean S is the mean of the two orientations.'])
    arms=['v7','forcedP16','forcedv6','omega0','historicalP16']
    for head in ['regular','novice']:
        lines.extend(['',f'### {head}'])
        table(lines,['Cluster']+arms+['Δ wins','Mean S (arm order above)'],
              [(p['cluster'],*[str(p['wins'][arm])+' ('+'/'.join(str(x) for x in p['orientation_wins'][arm])+')' for arm in arms],
                p['wins']['v7']-p['wins']['forcedP16'],', '.join(f'{p["mean_S"][arm]:.3f}' for arm in arms))
               for p in a['paired_clusters'] if p['head']==head])
    lines.extend(['','## Gate and selected-source diagnostics','',
                  'Counts and shares below pool stored per-fight telemetry within each arm/head. Selected-source shares count unit-ticks across all roles; melee actions are identical in both sources. Gate-mode transitions remain recorded in forced arms; their selected source stays fixed. Pair modes are a separate inherited diagnostic. Historical P16 has no outer-selector telemetry.'])
    aggregates={}
    for cell in a['cells']:
        key=(cell['arm'],cell['head']);rows=[r['telemetry'] for r in a['per_fight'] if (r['arm'],r['head'])==key]
        counts=collections.Counter();pairs=collections.Counter();combos=collections.Counter();shells=collections.Counter();fire=collections.Counter();complex_counts=collections.Counter()
        for r in rows:
            counts.update(r['counts']);pairs.update(r['pair_mode_ticks']);combos.update(r['escort_gun_source_combinations']);shells.update(r['shell_counts']);fire.update(r['firing_targets'])
            for k in ['samples','lowAmplitudeSamples','argRateSamples','argRateAbsSum','retryCount','numericalFailureTicks']:complex_counts[k]+=r['complex_diagnostics'][k]
        aggregates[key]=(counts,pairs,combos,shells,fire,complex_counts)
    table(lines,['Arm','Head','Gate transitions','P16 selected / total','v6 selected / total','Pair commit ticks','Pair escape ticks'],
          [(arm,head,c['gate_transitions'],fraction(c['selected_P16_unit_ticks'],c['selected_P16_unit_ticks']+c['selected_v6_unit_ticks']),fraction(c['selected_v6_unit_ticks'],c['selected_P16_unit_ticks']+c['selected_v6_unit_ticks']),p['commit'],p['escape'])
           for (arm,head),(c,p,_,__,___,____) in aggregates.items()])
    lines.extend(['','## Firing and geometry diagnostics','','Fractions are pooled numerator/denominator ratios, not means of per-fight fractions. Actual in-band time uses P16-selected gun ticks with gun and focus both alive after the step. Post arrival uses the prepared gun centre within 20 px of the clipped post. Escort arrival uses the post-step centre within 20 px. No spacing or shot-range guarantee is implied.'])
    table(lines,['Arm','Head','Own launches','Distinct target IDs','Target differs between sources ticks','Chosen gun-target V','P16 selected gun-target V','Post arrival','Actual in focus band','Escort arrival','Raw goal outside band / selected posts','Clipped goal outside band / selected posts'],
          [(arm,head,sum(f.values()),len(f),c['target_differs_between_sources_ticks'],fraction(c['gun_target_V_sum'],c['gun_target_V_ticks']),fraction(c['P16_selected_target_V_sum'],c['P16_selected_target_V_ticks']),fraction(c['post_arrival_prepare_ticks'],c['selected_gun_post_ticks']),fraction(c['actual_in_focus_band_ticks'],c['post_alive_gun_and_focus_ticks']),fraction(c['escort_arrival_post_ticks'],c['selected_escort_ticks']),fraction(c['raw_goal_outside_band_ticks'],c['selected_gun_post_ticks']),fraction(c['clipped_goal_outside_band_ticks'],c['selected_gun_post_ticks']))
           for (arm,head),(c,_,__,___,f,____) in aggregates.items()])
    table(lines,['Arm','Head','Own gun victims / gun-damaging shells','Enemy gun victims / gun-damaging shells','Own artillery enemy ranged kills <20 s','<30 s','Low amplitude samples / total','Absolute argument-rate sum / valid samples','Retries','Numerical failure ticks'],
          [(arm,head,fraction(s['own_gun_victims'],s['own_gun_damage_successful_shells']),fraction(s['enemy_gun_victims'],s['enemy_gun_damage_successful_shells']),c['artillery_enemy_ranged_kills_lt20'],c['artillery_enemy_ranged_kills_lt30'],fraction(z['lowAmplitudeSamples'],z['samples']),fraction(z['argRateAbsSum'],z['argRateSamples']),z['retryCount'],z['numericalFailureTicks'])
           for (arm,head),(c,_,__,s,___,z) in aggregates.items()])
    table(lines,['Arm','Head','Escort / gun selected source combination','Ticks'],[(arm,head,k,v) for (arm,head),(_,__,combos,___,____,_____) in aggregates.items() for k,v in sorted(combos.items())])
    lines.extend(['','Mean surviving own artillery (death-based curve carries terminal survivors forward):'])
    table(lines,['Arm','Head','10 s','20 s','30 s','45 s','60 s'],[(c['arm'],c['head'],*[f'{p["mean_alive"]:.3f}' for p in c['gun_survival']]) for c in a['cells']])
    lines.extend(['','## Stored recovery and presentation status'])
    attempts=[]
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',VALIDATION_COMMIT,'--',PREFIX+'/s4_v7c'],cwd=REPO,text=True).splitlines()
    for name in names:
        if Path(name).name.startswith('ATTEMPT_') and name.endswith('.json'):
            x,_=committed(VALIDATION_COMMIT,name[len(PREFIX)+1:]);attempts.append((Path(name).name,x))
    table(lines,['Attempt','Stage','Status','Seconds','Prior / allowance (s)','Error'],[(name,x['stage'],x['status'],x.get('seconds','unclosed historical record'),f'{x.get("prior_seconds",0)} / {x.get("allowance_seconds", "n/a")}',x.get('error') or '—') for name,x in sorted(attempts,key=lambda row:row[1]['utc_start'])])
    boot,_=committed(VALIDATION_COMMIT,'s4_v7c/HOST_BOOT_EVIDENCE_20261007.json')
    manifest,_=committed(VALIDATION_COMMIT,'s4_v7c/ANALYSIS_RECOVERY_V2_MANIFEST.json')
    passed=next(x for _,x in attempts if x['stage']=='analyze_validate' and x['status']=='PASS')
    stopped=next(x for _,x in attempts if x['stage']=='render_validate' and x['status']=='STOP')
    omega_wins=next(c['wins'] for c in a['cells'] if (c['arm'],c['head'])==('omega0','regular'))
    v7_wins=next(c['wins'] for c in a['cells'] if (c['arm'],c['head'])==('v7','regular'))
    lines.extend(['',f'Boot evidence: epoch {boot["boot_epoch_seconds"]}; interrupted-analysis charge {manifest["interruption_accounting"]["charged_seconds"]} s. V2 supersedes accounting only; validation was not resealed. V1’s conservative record stays unchanged.', '',
                  f'Analysis PASS consumed {passed["seconds"]} s of the shared {manifest["night_cap_seconds"]} s stored-only night allowance. The sealed HTML render STOP consumed its remaining {stopped["allowance_seconds"]} s allowance (measured {stopped["seconds"]} s, including watchdog overhead). This Markdown report is a separate JSON-only presentation under the owner’s current request; it does not restart the sealed render or renew that allowance.', '',
                  f'Historical cumulative charge remains {passed["historical_seconds"]} s. The two night attempts consumed {passed["seconds"]+stopped["seconds"]} s in total; watchdog overhead beyond the cap is {passed["seconds"]+stopped["seconds"]-manifest["night_cap_seconds"]:.9f} s. No spent time is clipped or reset.', '',
                  '## Limits','',
                  'Observed match is a descriptive count-band label, not superiority, equivalence or proof of no effect. The panel has 20 paired development clusters, not 40 independent samples and not a population-rate estimate. Positive mean S alone does not imply elimination: forcedv6 has positive regular mean S and zero regular wins.', '',
                  a['omega0_interpretation']+f' ω0 − v7 observed regular wins: {omega_wins-v7_wins:+d}; this does not establish that rotation is negligible or unnecessary.', '',
                  'The selector switches between oscillator-containing command packages. The v7/forcedP16 contrast concerns outer selection conditional on θ*. The forcedv6 result does not identify the action map as the sole cause of killing. These data establish no necessity of oscillation, synchrony causality, hierarchy or B→R→B recursion. No S5 or judging authorization or scientific acceptance follows.', '',
                  'The report generator reads committed JSON through git show and writes only this new report. The reviewer’s raw-data verification is recorded separately in s4_checks/v7_validation_recheck/AUDIT.json.'])
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    text=build()
    if args.check:
        if OUTPUT.read_text()!=text:raise RuntimeError('report differs from committed JSON rendering')
        print('Committed-JSON report reproducibility PASS')
    else:
        with OUTPUT.open('x') as f:f.write(text)
        print(OUTPUT)


if __name__=='__main__':
    main()
