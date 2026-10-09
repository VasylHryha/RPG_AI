"""Report generation only; no model calls or metric recomputation."""
import numpy as np

ROLES = ('melee', 'ranged', 'artillery')
INPUTS = '''N2-specific readout inputs (protocol correction M3; Stage A protocol left untouched by owner scope):

| Readout | Extra input and fixed transformation |
|---|---|
| Target bonus | Up to 8 own allies within 300 px, their exact current engine target IDs, and unit/peer phases. Per enemy: +2 times cosine alignment with the normalized mean phase of peers assigned to that enemy; zero for absent or cancelling groups. None gets no bonus. |
| Fire window | Updated absolute unit phase. Add [2 cos(theta), -2 cos(theta), 2 cos(theta)] to automatic/hold/release logits. |

N1/N1h/N1r lack these hard-wired additions. Equal registered parameter counts and the shared 136-coordinate head input do not establish matched readout information. Public targets also appear as scalar IDs in tokens, but exact neighbour-ID matching is privileged in N2.'''


def report(result, old):
    m = result['metrics']; base = old['metrics']['N1']; intact = m['N2_intact']
    comparisons = {}
    for name, roles in m.items():
        comparisons[name] = {}
        for r in ROLES:
            a = roles[r]['target_accuracy']; b = base[r]['target_accuracy']; full = intact[r]['target_accuracy']
            differences = [100*(s['metrics'][name][r]['target_accuracy']-s['metrics']['N2_intact'][r]['target_accuracy'])
                           for s in result['sequences'] if s['metrics'][name][r]['rows']]
            comparisons[name][r] = dict(delta_from_intact_pp=100*(a-full), delta_from_N1_pp=100*(a-b),
                                        original_N2_minus_N1_pp=100*(full-b),
                                        fraction_of_original_margin=(a-b)/(full-b) if full != b else None,
                                        per_fight_delta_from_intact_pp=dict(min=min(differences), median=float(np.median(differences)),
                                                                           max=max(differences), positive=sum(d>0 for d in differences),
                                                                           zero=sum(d==0 for d in differences), negative=sum(d<0 for d in differences)))
    result['comparisons'] = comparisons
    retained = [comparisons['N2_indicator_no_phase'][r]['fraction_of_original_margin'] for r in ('ranged','artillery')]
    no_bonus_retained = [comparisons['N2_intact_no_bonus'][r]['fraction_of_original_margin'] for r in ('ranged','artillery')]
    if min(retained) >= .8 and max(no_bonus_retained) <= .2:
        verdict = ('Most of the target gain is reproducible by the hand-wired neighbour-target feature with coupling switched off. '
                   'Phase coupling is therefore chiefly an enabler of that engineered readout in this checkpoint; these controls do not support the earlier claim that phase dynamics carry the gain themselves.')
    elif min(retained) >= .8:
        verdict = ('Most of the target gain is reproducible by the hand-wired neighbour-target feature with coupling switched off. '
                   'The intact head also retains a material part of the gain without that bonus, so the contribution is mixed. '
                   'Phase coupling is not necessary to recover most of the margin once the engineered feature is enabled; unique attribution to phase dynamics is unsupported.')
    elif max(retained) <= .2:
        verdict = ('The synchronised neighbour-target indicator with coupling switched off recovers little of the target gain. '
                   'Phase-dependent information or phase-dependent head behaviour beyond that indicator remains plausible, but these checkpoint interventions do not isolate a learned resonance mechanism.')
    else:
        verdict = ('The hand-wired neighbour-target feature explains part of the target gain with coupling switched off; recovery differs by role or is incomplete. '
                   'The remaining gap cannot be assigned uniquely to phase dynamics because the trained head also consumes phase features. This replay does not isolate a learned resonance mechanism.')
    result['verdict'] = verdict
    result['verdict_reading_rule'] = 'Exploratory wording only: indicator >=80% margin retained in both ranged/artillery => most; no-bonus <=20% in both additionally supports chiefly an enabler. Indicator <=20% in both => little; otherwise partial/mixed. Descriptive thresholds, not a registered acceptance rule.'
    lines = ['# Stage B round-0 controls', '', verdict, '',
             f"Same N2 epoch-10 checkpoint, 50 original TEST fights, {result['test']['full_prefix_frames']:,} full-prefix ticks, "
             f"{result['test']['scored_unit_rows']:,} scored unit rows, same four 90-tick windows and exact original row hash. "
             'No retraining, new fights, recalibration or changes to the original metrics JSON. Intact target/fire counts reproduce exactly in every fight.', '',
             '| Control | Melee target | Ranged target | Artillery target |', '|---|---:|---:|---:|']
    lines.append('| Original N1 reference | '+' | '.join(f"{base[r]['target_accuracy']:.4f}" for r in ROLES)+' |')
    for n, roles in m.items(): lines.append('| '+n+' | '+' | '.join(f"{roles[r]['target_accuracy']:.4f}" for r in ROLES)+' |')
    lines += ['', '| Comparison | Ranged | Artillery |', '|---|---:|---:|']
    for n in m:
        if n == 'N2_intact': continue
        lines.append('| '+n+' change from intact (pp) | '+' | '.join(f"{comparisons[n][r]['delta_from_intact_pp']:+.2f}" for r in ('ranged','artillery'))+' |')
    lines += ['', 'The K=0 synchronised-indicator control retains '+', '.join(
        f"{r}: {100*comparisons['N2_indicator_no_phase'][r]['fraction_of_original_margin']:.1f}% of the original N2-minus-N1 margin "
        f"({comparisons['N2_indicator_no_phase'][r]['delta_from_N1_pp']:+.2f} pp over N1)" for r in ('ranged','artillery'))+'.', '',
        'Intact phase dynamics without the target bonus lose '+', '.join(
        f"{r}: {-comparisons['N2_intact_no_bonus'][r]['delta_from_intact_pp']:.2f} pp" for r in ('ranged','artillery'))+'. '
        'This is removal from a head trained with the bonus, not a retrained feature-matched architecture comparison.', '',
        'Forcing-only retains K and the original forcing feature in the head; it isolates forcing removal from coupling removal. '
        'The earlier K=0, frozen-phase and no-geometry-to-mode cuts largely share one alignment disruption; they are not three independent confirmations. '
        'In particular, frozen and omega-only phases share relative phases.', '',
        'Same-role shuffle permutes phases after each physical update and carries the permutation forward. It preserves that tick’s role marginal, '
        'but later marginals evolve on the perturbed trajectory. Forced synchrony overwrites all phases with zero each tick. '
        'These are disturbance controls, not proof of equal disturbance magnitude or equally familiar joint inputs. '
        'The synchrony arm also changes absolute-phase head/fire inputs, so its difference from intact cannot uniquely identify target-alignment information.', '',
        '| Role | Oracle target among neighbour targets / all rows | Among non-None oracle rows | Trivial plurality-else-nearest accuracy |', '|---|---:|---:|---:|']
    for r, v in result['neighbor_diagnostic'].items():
        lines.append(f"| {r} | {v['oracle_among_neighbor_targets_fraction']:.4f} | {v['oracle_among_neighbor_targets_fraction_non_none']:.4f} | {v['trivial_rule_accuracy']:.4f} |")
    lines += ['', 'The diagnostic uses the identical up-to-eight within-300-px graph, across all own roles. None/dead-target assignments are ignored. '
              'Plurality ties use nearest distance, then smallest enemy ID; no valid assigned target falls back to nearest, and no living enemy returns None. '
              'Oracle labels are used only to score the diagnostic. Support fraction is a descriptive overlap, not a bound on total model accuracy.', '',
              'Fire-window contribution (raw three-class accuracy and unchanged original N2 validation thresholds; no recalibration):', '',
              '| Role | Intact raw | No window raw | Raw change (pp) | Intact calibrated | No window calibrated | Calibrated change (pp) |', '|---|---:|---:|---:|---:|---:|---:|']
    for r in ROLES:
        a = intact[r]; b = m['N2_intact_no_fire_window'][r]
        lines.append(f"| {r} | {a['fire_accuracy']:.4f} | {b['fire_accuracy']:.4f} | {100*(b['fire_accuracy']-a['fire_accuracy']):+.2f} | "
                     f"{a['calibrated_fire_accuracy']:.4f} | {b['calibrated_fire_accuracy']:.4f} | {100*(b['calibrated_fire_accuracy']-a['calibrated_fire_accuracy']):+.2f} |")
    lines += ['', 'No-bonus and no-fire-window arms reuse intact state but use exact logits captured before their respective additions. '
              'The additions never feed back into recurrent state on these fixed rows. Light multi-tick tests check the identities against separate switch forwards. '
              'All other interventions replay full prefixes independently. JSON includes per-fight metrics, head errors, safety-masked calibrated fire and phase diagnostics.', '', INPUTS, '',
              'Limitations: one training seed/checkpoint per architecture; a matched epoch/budget comparison, not convergence. '
              'N1 lacks the exact peer-target readout, so it cannot serve as a feature-matched memory control. Phase is recurrent state. '
              'A retrained N1 plus the same neighbour-target feature would test the architecture question. '
              'Fixed recorded positions and assignments cannot respond to altered policy actions; neither live geometry-mode feedback nor recursive background transformation is tested. '
              'Per-fight deltas are descriptive; repeated unit ticks are not independent replications.', '',
              f"Execution: {result['execution']['seconds']:.1f} s wall / {result['execution']['cpu_seconds']:.1f} s CPU, "
              f"nice {result['execution']['nice']}, one Torch thread and one interop thread. All original input pins and new inference source hashes rechecked after replay. "
              'Original metrics JSON SHA256: `'+result['original_metrics_sha256']+'`.']
    return '\n'.join(lines)+'\n'
