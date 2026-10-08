# A0 rev-1 paired decomposition diagnosis

Status: post-hoc diagnostic of the existing 50-pair look; no new fights, no changed verdict. All 300 outcome streams and completion receipts were hash-checked against `A0_LOOK_50.json`; every counted own death matches its completion statistic. Reproduce with `.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/diagnose_a0_decomposition.py`. Full counts, sums, per-fight rows, descriptive paired intervals and source hashes are in `A0_DECOMPOSITION_COUNTS.json`.

The top readout is enemy-artillery loss of ranged units. The strongest policy discrepancy is replacement of T’s public-history baseline and physical-tick cadence, not omission of a single-gun lead equation. These arms have different trajectories, so the data locate losses and describe mechanisms; they cannot estimate causal shares for target memory, cadence, spread, or multi-gun planning separately.

## 1. Extra deaths are mostly ranged units killed by enemy splash

Counts below are totals across 50 fights. Differences are paired O minus T; divide totals by 50 for deaths/fight. Friendly artillery and ranged damage are retained, because omitting them would fail casualty reconciliation.

| Panel / victim | O deaths | O+G deaths | T deaths | O − T total | O − T / fight |
|---|---:|---:|---:|---:|---:|
| regular / melee | 478 | 475 | 470 | +8 | +0.16 |
| regular / ranged | 1348 | 1351 | 1251 | +97 | +1.94 |
| regular / artillery | 18 | 9 | 9 | +9 | +0.18 |
| C3 / melee | 484 | 480 | 475 | +9 | +0.18 |
| C3 / ranged | 1278 | 1251 | 1181 | +97 | +1.94 |
| C3 / artillery | 66 | 54 | 26 | +40 | +0.80 |

| Panel / victim / killing source | O | O+G | T | Paired O − T total |
|---|---:|---:|---:|---:|
| regular / melee / enemy artillery | 237 | 237 | 187 | +50 |
| regular / melee / enemy ranged | 101 | 93 | 180 | -79 |
| regular / melee / enemy melee | 45 | 66 | 34 | +11 |
| regular / melee / friendly artillery | 91 | 76 | 64 | +27 |
| regular / melee / friendly ranged | 4 | 3 | 5 | -1 |
| regular / ranged / enemy artillery | 1225 | 1227 | 1075 | +150 |
| regular / ranged / enemy ranged | 11 | 13 | 22 | -11 |
| regular / ranged / enemy melee | 27 | 21 | 34 | -7 |
| regular / ranged / friendly artillery | 49 | 42 | 61 | -12 |
| regular / ranged / friendly ranged | 36 | 48 | 59 | -23 |
| regular / artillery / enemy artillery | 18 | 9 | 9 | +9 |
| regular / artillery / enemy ranged | 0 | 0 | 0 | +0 |
| regular / artillery / enemy melee | 0 | 0 | 0 | +0 |
| regular / artillery / friendly artillery | 0 | 0 | 0 | +0 |
| regular / artillery / friendly ranged | 0 | 0 | 0 | +0 |
| C3 / melee / enemy artillery | 269 | 261 | 237 | +32 |
| C3 / melee / enemy ranged | 87 | 83 | 125 | -38 |
| C3 / melee / enemy melee | 42 | 44 | 33 | +9 |
| C3 / melee / friendly artillery | 82 | 88 | 76 | +6 |
| C3 / melee / friendly ranged | 4 | 4 | 4 | +0 |
| C3 / ranged / enemy artillery | 1108 | 1116 | 995 | +113 |
| C3 / ranged / enemy ranged | 31 | 26 | 25 | +6 |
| C3 / ranged / enemy melee | 33 | 20 | 31 | +2 |
| C3 / ranged / friendly artillery | 70 | 54 | 84 | -14 |
| C3 / ranged / friendly ranged | 36 | 35 | 46 | -10 |
| C3 / artillery / enemy artillery | 64 | 45 | 19 | +45 |
| C3 / artillery / enemy ranged | 0 | 0 | 0 | +0 |
| C3 / artillery / enemy melee | 0 | 2 | 3 | -3 |
| C3 / artillery / friendly artillery | 1 | 6 | 4 | -3 |
| C3 / artillery / friendly ranged | 1 | 1 | 0 | +1 |

Regular totals are 1,844 O deaths versus 1,730 T (+114 / +2.28 per fight); C3 is 1,828 versus 1,682 (+146 / +2.92). Ranged contributes +97 in each panel (+1.94/fight), or 85.1% and 66.4% of the net gap. Enemy-artillery killing blows increase by +209 regular (+4.18/fight) and +190 C3 (+3.80/fight) across all own roles; other causes offset some of that increase. These are final-blow counts, not credit for all prior damage. Abilities are off, so artillery damage here is ordinary shell splash; friendly ordinary ranged projectiles can also kill.

| Panel / time | O deaths | O+G deaths | T deaths | Paired O − T |
|---|---:|---:|---:|---:|
| regular / early_0_30s | 1396 | 1388 | 1320 | +76 (+1.52/fight) |
| regular / late_30s_plus | 448 | 447 | 410 | +38 (+0.76/fight) |
| C3 / early_0_30s | 1429 | 1408 | 1343 | +86 (+1.72/fight) |
| C3 / late_30s_plus | 399 | 377 | 339 | +60 (+1.20/fight) |

“Early” is the fixed absolute t < 30 s window, selected descriptively for this diagnosis. It is not half of each fight. Extra losses are +76 early/+38 late regular and +86/+60 C3. Per-role early/late counts are included in JSON.

| Panel / shell measure | O | O+G | T | Paired O − T / fight |
|---|---:|---:|---:|---:|
| regular / enemy shells launched | 9690 | 9461 | 8908 | +15.64 |
| regular / own-unit hits by enemy shells | 15955 | 15938 | 14638 | +26.34 |
| regular / enemy shells hitting ≥2 own units | 3625 | 3639 | 3256 | +7.38 |
| regular / enemy shells hitting ≥3 own units | 1740 | 1815 | 1545 | +3.90 |
| regular / hits / enemy shell launched (mean of fight ratios) | 1.653 | 1.690 | 1.648 | +0.005 |
| regular / hits / enemy shell with ≥1 hit (mean of fight ratios) | 1.775 | 1.805 | 1.748 | +0.027 |
| C3 / enemy shells launched | 8547 | 8551 | 8170 | +7.54 |
| C3 / own-unit hits by enemy shells | 15264 | 15127 | 13992 | +25.44 |
| C3 / enemy shells hitting ≥2 own units | 3236 | 3203 | 3058 | +3.56 |
| C3 / enemy shells hitting ≥3 own units | 1765 | 1761 | 1509 | +5.12 |
| C3 / hits / enemy shell launched (mean of fight ratios) | 1.813 | 1.785 | 1.731 | +0.083 |
| C3 / hits / enemy shell with ≥1 hit (mean of fight ratios) | 1.940 | 1.906 | 1.851 | +0.090 |

Shell hits match source ID and landing time within one physical tick; no ambiguous/unmatched enemy-shell damage hits were found. Launch-based ratios include shells still in flight at the fight end, with zero observed hits. Regular has almost identical hits/launch (1.653 O vs 1.648 T), but O allows 782 more enemy launches and 1,317 more hits. C3 combines 377 more launches and 1,272 more hits with more multi-victim exposure (1.813 vs 1.731 hits/launch). This supports both longer enemy-gun survival/exposure and some tighter splash exposure, rather than claiming all deaths came from failure to dodge.

## 2. T preserves a history-based movement/target policy; O substitutes nearest enemies

P16 begins each unit with `S4V6Controller::decide`. It replaces ranged escort points and gun focus/repulsion points, but preserves baseline target choices for ranged and the entire baseline movement for melee, plus artillery fallback when no enemy gun is reachable/present. T updates the baseline every physical tick. Rev-1 O starts from `a0_oracle.cpp::base` (nearest legal enemy, otherwise nearest living enemy, role-specific range point), and `a0_build.py` caches it for 0.2 s. T’s baseline includes public-counter filters, derived complex-state ally geometry and enemy pressure, legal-target scoring and a 0.2 score-retention margin. It is not just nearest-target selection.

The following state proxies sample every second at absolute t = 5..30 s. Values are means of each fight’s role average; displayed differences are paired means. “Commit” below means preparation or close contact, not the omitted v6 latent commitment.

| Panel / role / metric | O | O+G | T | Paired O − T |
|---|---:|---:|---:|---:|
| regular / melee / spread_rms_px | 81.413 | 80.493 | 82.594 | -1.181 |
| regular / melee / nearest_enemy_px | 167.103 | 168.883 | 170.889 | -3.787 |
| regular / melee / target_range_px | 167.496 | 169.290 | 45.808 | +121.688 |
| regular / melee / focus_hhi | 0.503 | 0.508 | 0.609 | -0.105 |
| regular / melee / max_target_share | 0.568 | 0.575 | 0.661 | -0.092 |
| regular / melee / target_switches | 49.380 | 49.820 | 17.380 | +32.000 |
| regular / melee / switch_fraction | 0.368 | 0.369 | 0.132 | +0.236 |
| regular / melee / no_target_fraction | 0.006 | 0.006 | 0.800 | -0.794 |
| regular / melee / legal_target_per_live_sample | 0.221 | 0.219 | 0.198 | +0.024 |
| regular / melee / prep_fraction | 0.066 | 0.067 | 0.074 | -0.008 |
| regular / melee / close_contact_fraction | 0.254 | 0.250 | 0.233 | +0.021 |
| regular / ranged / spread_rms_px | 101.148 | 100.615 | 105.366 | -4.218 |
| regular / ranged / nearest_enemy_px | 207.439 | 207.631 | 211.449 | -4.011 |
| regular / ranged / target_range_px | 207.758 | 207.863 | 212.492 | -4.734 |
| regular / ranged / focus_hhi | 0.404 | 0.396 | 0.517 | -0.112 |
| regular / ranged / max_target_share | 0.505 | 0.498 | 0.622 | -0.117 |
| regular / ranged / target_switches | 252.800 | 254.220 | 223.420 | +29.380 |
| regular / ranged / switch_fraction | 0.448 | 0.450 | 0.390 | +0.058 |
| regular / ranged / no_target_fraction | 0.009 | 0.010 | 0.224 | -0.215 |
| regular / ranged / legal_target_per_live_sample | 0.785 | 0.786 | 0.773 | +0.012 |
| regular / ranged / prep_fraction | 0.306 | 0.316 | 0.330 | -0.024 |
| regular / ranged / close_contact_fraction | 0.040 | 0.040 | 0.043 | -0.003 |
| regular / artillery / spread_rms_px | 92.904 | 92.105 | 93.791 | -0.887 |
| regular / artillery / nearest_enemy_px | 252.555 | 252.283 | 254.812 | -2.257 |
| regular / artillery / target_range_px | 272.163 | 272.951 | 268.453 | +3.710 |
| regular / artillery / focus_hhi | 0.369 | 0.361 | 0.531 | -0.162 |
| regular / artillery / max_target_share | 0.476 | 0.469 | 0.623 | -0.147 |
| regular / artillery / target_switches | 131.780 | 132.860 | 129.960 | +1.820 |
| regular / artillery / switch_fraction | 0.549 | 0.554 | 0.542 | +0.007 |
| regular / artillery / no_target_fraction | 0.008 | 0.009 | 0.229 | -0.221 |
| regular / artillery / legal_target_per_live_sample | 0.780 | 0.779 | 0.761 | +0.018 |
| regular / artillery / prep_fraction | 0.482 | 0.493 | 0.520 | -0.038 |
| regular / artillery / close_contact_fraction | 0.002 | 0.002 | 0.005 | -0.003 |
| C3 / melee / spread_rms_px | 76.252 | 76.419 | 76.596 | -0.343 |
| C3 / melee / nearest_enemy_px | 156.483 | 156.836 | 157.644 | -1.161 |
| C3 / melee / target_range_px | 156.905 | 157.011 | 46.365 | +110.539 |
| C3 / melee / focus_hhi | 0.571 | 0.568 | 0.645 | -0.074 |
| C3 / melee / max_target_share | 0.634 | 0.632 | 0.694 | -0.060 |
| C3 / melee / target_switches | 46.660 | 45.920 | 20.260 | +26.400 |
| C3 / melee / switch_fraction | 0.344 | 0.343 | 0.161 | +0.182 |
| C3 / melee / no_target_fraction | 0.006 | 0.005 | 0.769 | -0.763 |
| C3 / melee / legal_target_per_live_sample | 0.237 | 0.248 | 0.228 | +0.009 |
| C3 / melee / prep_fraction | 0.067 | 0.076 | 0.095 | -0.027 |
| C3 / melee / close_contact_fraction | 0.271 | 0.285 | 0.276 | -0.005 |
| C3 / ranged / spread_rms_px | 96.051 | 97.726 | 101.359 | -5.308 |
| C3 / ranged / nearest_enemy_px | 200.766 | 202.701 | 200.033 | +0.733 |
| C3 / ranged / target_range_px | 201.069 | 202.635 | 202.749 | -1.680 |
| C3 / ranged / focus_hhi | 0.479 | 0.476 | 0.557 | -0.078 |
| C3 / ranged / max_target_share | 0.575 | 0.573 | 0.652 | -0.077 |
| C3 / ranged / target_switches | 224.560 | 230.000 | 222.620 | +1.940 |
| C3 / ranged / switch_fraction | 0.430 | 0.430 | 0.400 | +0.030 |
| C3 / ranged / no_target_fraction | 0.006 | 0.009 | 0.209 | -0.203 |
| C3 / ranged / legal_target_per_live_sample | 0.799 | 0.798 | 0.789 | +0.010 |
| C3 / ranged / prep_fraction | 0.285 | 0.290 | 0.299 | -0.015 |
| C3 / ranged / close_contact_fraction | 0.097 | 0.087 | 0.110 | -0.013 |
| C3 / artillery / spread_rms_px | 93.765 | 93.885 | 98.732 | -4.967 |
| C3 / artillery / nearest_enemy_px | 241.070 | 242.792 | 242.071 | -1.001 |
| C3 / artillery / target_range_px | 269.361 | 268.558 | 265.935 | +3.426 |
| C3 / artillery / focus_hhi | 0.435 | 0.430 | 0.525 | -0.089 |
| C3 / artillery / max_target_share | 0.536 | 0.531 | 0.619 | -0.083 |
| C3 / artillery / target_switches | 120.040 | 116.300 | 121.840 | -1.800 |
| C3 / artillery / switch_fraction | 0.504 | 0.490 | 0.512 | -0.008 |
| C3 / artillery / no_target_fraction | 0.007 | 0.007 | 0.193 | -0.187 |
| C3 / artillery / legal_target_per_live_sample | 0.809 | 0.813 | 0.799 | +0.010 |
| C3 / artillery / prep_fraction | 0.500 | 0.497 | 0.526 | -0.026 |
| C3 / artillery / close_contact_fraction | 0.032 | 0.035 | 0.049 | -0.017 |

T’s target is often absent while no legal enemy exists; O usually names an out-of-range enemy. Consequently **conditional** in-range rates and target-range distances are selection-biased. The JSON’s `legal_target_per_live_sample` includes targetless units: O does not have materially less legal-target presence overall. HHI and maximum share use only current live enemy targets and likewise are conditional, not proof that concentrating fire caused survival. Switching includes transitions to/from no target and is sampled at 1 Hz, not every dispatch. Gun/ranged RMS spread is modestly larger for T, while nearest-enemy distances are close. There is no evidence of a radically different formation or a blanket melee withdrawal. Own external units have no native formation slots; both retain P16/participation/react rules.

| Panel / role | O react activations | O+G activations | T activations | O react tick fraction | T react tick fraction |
|---|---:|---:|---:|---:|---:|
| regular / melee | 7137 | 7070 | 7635 | 0.179 | 0.185 |
| regular / ranged | 64583 | 62899 | 67208 | 0.327 | 0.316 |
| regular / artillery | 29908 | 27862 | 26424 | 0.192 | 0.182 |
| C3 / melee | 7310 | 7180 | 7214 | 0.188 | 0.183 |
| C3 / ranged | 56144 | 59909 | 59565 | 0.298 | 0.290 |
| C3 / artillery | 25419 | 25405 | 22350 | 0.166 | 0.151 |

An activation is false→true per unit, including first observed true. These labels are per-physical-tick; deaths remove later opportunities, so totals are exposure-dependent. The full JSON also reports dodge tick records, ready labels and damage/hits by victim/source. O has **more** gun reaction activations (+3,484 regular, +3,069 C3) and more gun reaction occupancy, but still takes more splash. Ranged occupancy is also slightly higher for O. Both call the same react function; recorded labels omit primitive kind, so shell versus direct-shot reaction activations cannot be separated exactly. More reactions are not evidence of better avoidance.

## 3. Single-gun inputs differ; the Singles lead formula does not

| Panel / single-ready launch metric | O | O+G | T | Paired O − T total |
|---|---:|---:|---:|---:|
| regular / own launches on single-ready events | 8502 | 8594 | 8426 | +76 |
| regular / named melee target | 2979 | 3007 | 2470 | +509 |
| regular / named ranged target | 568 | 544 | 1040 | -472 |
| regular / named artillery target | 4955 | 5043 | 4916 | +39 |
| regular / aim exactly at named target’s pre-step position | 5469 | 5524 | 5737 | -268 |
| regular / mean point offset from named pre-step target (px/fight mean) | 39.754 | 39.371 | 35.363 | +4.392 |
| C3 / own launches on single-ready events | 8435 | 8544 | 8368 | +67 |
| C3 / named melee target | 2779 | 2792 | 2322 | +457 |
| C3 / named ranged target | 707 | 643 | 1056 | -349 |
| C3 / named artillery target | 4949 | 5109 | 4990 | -41 |
| C3 / aim exactly at named target’s pre-step position | 5390 | 5441 | 5641 | -251 |
| C3 / mean point offset from named pre-step target (px/fight mean) | 44.269 | 45.702 | 40.682 | +3.586 |

In Game rules, copied `artillery.cpp` Singles selects the gun’s current legal named target and uses **its unled position**. Focus/cluster candidates use `leadVelocity` and the planner flight estimate. The raw T audit identifies Singles, while rev-1 O omits its planner family/score, so an exact candidate-by-candidate O Singles/Focus counterfactual is unavailable. The common copied planner and sanitized public projection are the same in both arms; the baseline/cadence determines targets, movement, eligibility and observed velocity on different trajectories.

T audit records 7,564/7,427 Singles assignments regular/C3. Of those, 7,419/7,345 can be joined to actual launches with the named target in the preceding frame; **all** joined launches aim exactly at that target’s pre-step position. Audit assignments without a joined launch are not silently counted as shots. At single-ready launch events, the identifiable T families are 5,734 Singles, 2,535 Focus and 146 Battery (regular), and 5,633 Singles, 2,600 Focus and 125 Battery (C3); some launches have no successful planner audit. O versus T names ranged targets 568 versus 1,040 regular and 707 versus 1,056 C3. T names fewer melee targets, and similar numbers of guns. Aim offset mixes target choice with non-Singles families; it is not a measured lead-error difference.

Therefore no missing single-gun solver is established. The repair is to restore the same public-history baseline and cadence before comparing the singleton versus joint planner. The original O+G recovers only 9 total deaths regular and 43 C3 (+0.18/+0.86 per fight); it leaves +105/+103 deaths versus T. Multi-gun event frequency (~12%) alone does not attribute the rest to a specific single-gun calculation.

## Revision and limits

`rev2/A0_REV2_PROTOCOL.md` supersedes the stateless/5 Hz A0 oracle simplification prospectively. O independently reconstructs T’s unit policy from its own public history, preserving all unit-decided behavior; only ready multi-gun aim coupling remains in G. Same-state equivalence compares separate O+G and T controller histories and actual bridge/command outputs, with near-zero (required zero in fixtures) mismatch by role/type. It uses state fixtures, not new fights. Fresh pilot and outcome entropy and the unchanged look-50 protocol are sealed separately.

The raw data cannot recover latent v6 commitment, executed move points/multipliers (decision trace was disabled), O planner family/rejected points, exact own cooldown/resources, or typed react primitives. It also cannot assign causal contributions to hysteresis versus cadence or measure a same-state rev-1 counterfactual with all original fields. The counts support revising these code-level differences, not a claim of causal mediation or successful revised combat outcomes. No new runs, training or source-recursion qualification is claimed.
