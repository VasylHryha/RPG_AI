# Owner-requested Stage B round-0 offline controls

This is an exploratory same-checkpoint replay, explicitly requested on 2026-10-09 after the Claude CHANGES_REQUIRED recheck. It is not a new training experiment or registered panel. Reuse exactly the original selected epoch-10 N2 weights, original 50 TEST fights and four 90-tick windows. Replay every dynamic intervention from the fight beginning. Do not train, launch simulated fights, change validation thresholds or write outside rrg_ablation/. Nice 15; one Torch worker thread and one interop thread; BLAS thread limits one.

Before reading new results, the controls are:

- N2_indicator_no_phase: exact K=0 dynamics and state/head features, but replace each enemy's neighbour phase-alignment bonus by +2 whenever any masked neighbour is currently assigned to that enemy.
- N2_intact_no_bonus: intact dynamics, remove the target-logit bonus alone.
- N2_forcing_only_cut: effective phase forcing zero, K and omega retained; original raw forcing scalar retained in the head.
- N2_role_shuffle: permute post-update phases within public role groups each tick, using seed 41002 reset per fight. Carry shuffled state forward. Marginals are preserved at each intervention of this perturbed trajectory, not against intact future trajectories.
- N2_forced_synchronous: set all post-update phases to a common zero each tick, carry them forward. This also changes absolute head/fire phase features.
- N2_intact_no_fire_window: intact dynamics and target bonus, remove [2 cos(theta), -2 cos(theta), 2 cos(theta)] from fire logits.

The target and fire additions are output-only on fixed recorded inputs. Their removal arms may reuse exact captured pre-addition logits and intact state; synthetic multi-tick equality tests verify this against independent forwards. No dynamic arm may reuse intact state snapshots.

N2-only inputs missing from the upstream fairness statement are the exact current target-ID assignments of up to eight own allies within 300 px, with unit/peer phase alignment, and the updated absolute phase for the fixed fire-window addition. These supplement the nominal shared 136-coordinate head vector; equal parameter inventory is not equal readout information. The upstream protocol is read-only under this task's scope; both reports carry this correction.

Score target argmax including None, raw fire accuracy, unchanged validation-threshold fire with/without the existing safety mask, movement and masked aim errors. Record every arm's per-fight counts and phase diagnostics. Require exact intact target/fire reproduction per fight, identical scored-row hash and all pinned input hashes before/after replay. Original metrics JSON must remain byte-identical.

Diagnostic: oracle target supported by any masked neighbour's current assignment (all rows and non-None-label denominators). The trivial rule chooses the enemy with most masked neighbours assigned, then nearest distance and lowest persistent ID for ties; otherwise nearest; no enemies => None. Ignore assignments to absent enemies/None. Labels are evaluator-side only.

Interpretation: quantify the fraction of original N2-minus-N1 margin recovered by indicator-no-phase and remaining without the bonus, rather than treating the old alignment cuts as independent corroboration. Report uses descriptive 80%/20% wording bands for most/little, not significance or acceptance thresholds; chiefly-an-enabler wording additionally requires little margin retained without bonus. This is one checkpoint and one training seed, with fixed exogenous positions and assignments. Shuffle/synchrony do not match disturbance magnitude or guarantee equal distribution familiarity. No resonance, memory exclusion, live geometry-mode feedback or recursive RRG qualification.

After replay: light switch tests and a separate owner's recheck, tracked within this folder (owner explicitly excludes docs/PLAN_CURRENT.md). Do not rerun completed inference on unchanged code.
