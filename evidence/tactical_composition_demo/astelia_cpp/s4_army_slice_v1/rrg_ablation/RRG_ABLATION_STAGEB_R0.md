> Report-only correction (2026-10-09; H2/M1/M3): original metrics JSON is unchanged. The earlier commit wording “geometry-driven phase coupling (not memory) carries the gain” is unsupported. The original replay establishes sensitivity to phase alignment with an N2-only engineered neighbour-target readout; it does not distinguish information in dynamics from synchrony enabling that feature. See RRG_ABLATION_STAGEB_R0_CONTROLS.md for the separately requested controls. Committed history is unchanged.

# Stage B round-0 RRG mechanism check

Offline float32 inference on the selected trained checkpoints. No retraining and no fights. The exact sealed TEST split has 50 fights, 63,897 replayed physical ticks, and 592,992 scored unit rows. Each dynamic intervention gets its own full-prefix state replay; scoring uses the same four 90-tick windows as the original outcomes. The tested exact identities reuse intact computation: reset-disabled changes nothing, and drift-only removal zeros output drift while retaining identical state and heads.

N2’s ranged/artillery target advantage does **not** survive K=0, frozen phase, or no geometry→mode. For this trained checkpoint on these fixed test rows, the original gain is sensitive to disrupted neighbour phase alignment. Alignment weights an N2-only exact neighbour-target feature, so this loss does not distinguish information carried by phase dynamics from an on-switch for that engineered feature. Phase is recurrent state, and N1r lacks the feature, so “not memory” is unsupported. This does not establish resonance, a live geometry↔mode feedback loop, or recursive RRG.

| Policy / intervention | Melee target | Ranged target | Artillery target |
|---|---:|---:|---:|
| N1 | 0.8839 | 0.6535 | 0.6383 |
| N1h | 0.8893 | 0.6615 | 0.6517 |
| N1r | 0.8840 | 0.6585 | 0.6398 |
| N2_intact | 0.9008 | 0.8015 | 0.7936 |
| N2_k_zero | 0.8790 | 0.6531 | 0.6183 |
| N2_frozen_phase | 0.8815 | 0.6529 | 0.6189 |
| N2_reset_disabled | 0.9008 | 0.8015 | 0.7936 |
| N2_topology_only | 0.8985 | 0.7862 | 0.7864 |
| N2_no_mode_to_geometry | 0.9008 | 0.8015 | 0.7936 |
| N2_no_geometry_to_mode | 0.8815 | 0.6529 | 0.6190 |

Intact N2 minus N1 target accuracy is melee: +1.69 percentage points, ranged: +14.80 percentage points, artillery: +15.53 percentage points.

k_zero: change from intact is ranged -14.84 points, artillery -17.53 points; remaining advantage over N1 is ranged -0.04 points, artillery -2.00 points.
frozen_phase: change from intact is ranged -14.86 points, artillery -17.47 points; remaining advantage over N1 is ranged -0.06 points, artillery -1.94 points.
topology_only: change from intact is ranged -1.53 points, artillery -0.72 points; remaining advantage over N1 is ranged +13.27 points, artillery +14.81 points.
no_geometry_to_mode: change from intact is ranged -14.86 points, artillery -17.46 points; remaining advantage over N1 is ranged -0.06 points, artillery -1.93 points.

At least one cut erases the observed margin over N1. This establishes checkpoint sensitivity to that intervention on these rows, without proving resonance or a general architecture effect.

Reset disabled is exactly intact: this implementation never resets phase on attack. Removing mode→geometry zeros drift and can change movement error, but leaves target/fire/aim unchanged in this replay. Recorded positions cannot react to the removed drift. Neither identity result tests a live feedback loop.

Frozen phase retains ID-dependent sin/cos features, peer phase summaries and the explicit target-alignment/fire-window readouts. No geometry→mode removes learned input-dependent forcing from the phase equation and removes geometry-weighted coupling; learned omega and the direct forcing feature supplied to the head remain. Topology-only freezes edges, distances and direction vectors at the first recorded tick, while tokens and target assignments stay live. The K=0, frozen-phase and no-geometry→mode cuts largely repeat one alignment disruption; they are not three independent confirmations. Frozen-phase and omega-only have the same relative phases. Topology-only also freezes which peers supply the target-assignment readout; its surviving gain does not isolate geometry’s causal role. These are checkpoint interventions, not trained replacement architectures. No phase-free retrained model is compared. No causal background transformation or recursive RRG claim is tested.

Fire below is raw three-class accuracy, matching the outcome metric. The JSON also gives fire accuracy with each original validation threshold unchanged, both before and after the calibration safety mask. Move and masked aim errors are mean SmoothL1 with beta=1, in 100-pixel units; lower is better. Aim uses only oracle rows with an aim label.

Melee heads:

| Policy | Fire accuracy | Move error | Aim error |
|---|---:|---:|---:|
| N1 | 0.8612 | 0.2597 | N/A |
| N1h | 0.8558 | 0.2514 | N/A |
| N1r | 0.8600 | 0.2536 | N/A |
| N2_intact | 0.8499 | 0.2717 | N/A |
| N2_k_zero | 0.8508 | 0.2713 | N/A |
| N2_frozen_phase | 0.8483 | 0.2708 | N/A |
| N2_reset_disabled | 0.8499 | 0.2717 | N/A |
| N2_topology_only | 0.8501 | 0.2719 | N/A |
| N2_no_mode_to_geometry | 0.8499 | 0.2742 | N/A |
| N2_no_geometry_to_mode | 0.8486 | 0.2712 | N/A |

Ranged heads:

| Policy | Fire accuracy | Move error | Aim error |
|---|---:|---:|---:|
| N1 | 0.8041 | 0.1190 | N/A |
| N1h | 0.7901 | 0.1208 | N/A |
| N1r | 0.8054 | 0.1228 | N/A |
| N2_intact | 0.7979 | 0.1309 | N/A |
| N2_k_zero | 0.7941 | 0.1309 | N/A |
| N2_frozen_phase | 0.7932 | 0.1309 | N/A |
| N2_reset_disabled | 0.7979 | 0.1309 | N/A |
| N2_topology_only | 0.7976 | 0.1317 | N/A |
| N2_no_mode_to_geometry | 0.7979 | 0.1313 | N/A |
| N2_no_geometry_to_mode | 0.7936 | 0.1311 | N/A |

Artillery heads:

| Policy | Fire accuracy | Move error | Aim error |
|---|---:|---:|---:|
| N1 | 0.8596 | 0.2183 | 0.5129 |
| N1h | 0.8521 | 0.2036 | 0.4630 |
| N1r | 0.8607 | 0.2170 | 0.4670 |
| N2_intact | 0.8595 | 0.2330 | 0.4724 |
| N2_k_zero | 0.8601 | 0.2322 | 0.4713 |
| N2_frozen_phase | 0.8606 | 0.2320 | 0.4700 |
| N2_reset_disabled | 0.8595 | 0.2330 | 0.4724 |
| N2_topology_only | 0.8603 | 0.2340 | 0.4711 |
| N2_no_mode_to_geometry | 0.8595 | 0.2337 | 0.4724 |
| N2_no_geometry_to_mode | 0.8604 | 0.2322 | 0.4703 |

Learned N2 K=1.009403; omega=0.025655 rad/s. Forcing is the learned tanh output from query/context, separate from coupling. At scored test ticks:

| Role | Forcing mean ± SD (rad/s) | Mean absolute forcing | Mean R (≥2 units) | Pair fraction within 30° |
|---|---:|---:|---:|---:|
| melee | -0.8029 ± 0.2839 | 0.8168 | 0.4789 | 0.2261 |
| ranged | -0.4534 ± 0.5442 | 0.6338 | 0.5301 | 0.3148 |
| artillery | 0.1738 ± 0.7023 | 0.6977 | 0.5720 | 0.3681 |

With K=0, mean R falls to melee 0.2022, ranged 0.1297, artillery 0.1192. Thus lower phase alignment accompanies the lost target-accuracy advantage.

R is the length of the mean unit phase vector: near one means global alignment; low R can mean dispersed phases or opposing clusters. Singleton R values are excluded from the displayed means. The pair fraction is a descriptive clustering measure, not a fitted number of clusters. JSON includes every intervention, phase histograms, early/middle/late R and per-fight head metrics. Alignment alone cannot establish that coupling causes the accuracy gain. The JSON coupling statistic is the instantaneous post-step RHS term, not the realized whole-step average; it is hypothetical under frozen phase, whose actual phase rate is zero.

Original outcome reproduction: all row and target/fire correct counts match exactly.

Inference took 697.2 s wall / 678.6 s CPU; nice 15, one Torch thread and one interop thread. All input/source hashes were checked again after inference. Results describe this held-out offline replay and are exploratory; repeated unit ticks are not independent fights.

N2-only readout inputs (M3 protocol correction within this report; upstream STAGEA_PROTOCOL.md left unchanged by owner scope):

| Readout | Additional input and transformation |
|---|---|
| Neighbour-target alignment | Exact current engine target IDs of up to eight own allies strictly within 300 px, plus the unit/peer phases. Add +2 times cosine alignment to each matching enemy logit; absent/cancelling phase groups give zero. |
| Fire window | Updated absolute phase; add [2 cos(theta), -2 cos(theta), 2 cos(theta)] to automatic/hold/release logits. |

N1/N1h/N1r lack these hard-wired readouts. Equal parameter inventory and the same 136-coordinate head vector do not imply matched readout inputs. One training seed and the final selected epoch per arm support a fixed-budget comparison, not convergence or seed-to-seed generality.
