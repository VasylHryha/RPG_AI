READY_FOR_S5

# S4 amended development report

Implementer family: Codex (GPT-6). Date: 2026-10-05. **Claude development review: APPROVE_WITH_NOTES.** This is development readiness under the amended A/B-only gates, as explicitly directed by the owner. This S4 run performed no S5 registration, judging-seed use, recorded S5 run, milestone status change or frozen GeoMind modification.

**Resonator novice validation: A +2.765; B +5.920; final C −6.565.** Final C regular is −8.945. Stage C panel tuning lost the earlier positive novice result. The owner explicitly chose the amended A/B-only gates after seeing the final negative novice result; see [the preserved decision](s4_checks/AMENDED_GATE_OWNER_DECISION.json). This report does not claim P1 support, tactical superiority, equivalence, RRG recursion or C4/C5 group qualification.

The original racing-protocol run reached STOP and remains preserved at commit d456a4f: [original report](s4_development/S4_DEVELOPMENT_REPORT_ORIGINAL.md), [original data](s4_development/summary.json). The owner then authorized a separate amended run. Request ee21545 changed during the original run; the amended CMA-ES protocol, resources and harness were committed at 8c89561 before amended tuning. Historical S4_REPORT_RECEIPT.json is unchanged and resolves historical root-file hashes at d456a4f; the new run has its own S4_AMENDED_REPORT_RECEIPT.json.

Claude reviewed the original run at a837561 (correction at e12f259): [APPROVE_WITH_NOTES; original STOP stands](../astelia_cpp_review_claude/S4_ORIGINAL_REVIEW.md). Claude separately reviewed the amended run and retained report during finalization: [APPROVE_WITH_NOTES](../astelia_cpp_review_claude/S4_AMENDED_REVIEW.md), committed at e12f259 and updated at 5460380. Subsequent final-report edits add provenance, formatting and the review links; the measurements are unchanged.

## Anomaly finding

The original diagnostic compared eight matched clusters and both orientations: morale novice/alone −16.6875; regular/line −4.3125; novice skills/line +1.1250; regular skills/alone −30.1875. Line formation improves the matchup under both skill bundles; regular skills strengthen the opponent within either brain. This explains the inversion as a configuration/matchup effect. Four fights were inspected; no genuine controller defect was found and no equations were changed. [Finding and watched fights](s4_anomaly/ANOMALY_FINDING.md).

## Declared optimizer, budgets and seed use

[Amended protocol](S4_AMENDED_PROTOCOL.md): pycma 4.5.0 CMAEvolutionStrategy ask/tell, bounds-normalized knobs in [0,1], population 16, initial sigma 0.25, sixteen generations, default active covariance adaptation, no restart and no two-SE acceptance. Every candidate uses nineteen fixed common tuning clusters per stage. All objective values enter CMA; the highest mean evaluated configuration, including the initial configuration, is retained with earlier ties. Validation never chooses knobs. A starts at midpoints; B/C start at preceding tuning best. Dimensions are 10/10/2 for resonator/morale/push-pull; nearest is untuned.

Each tuned arm receives **9,766 evaluations per stage**, including cache hits: 38 initial fights plus 16×16×38 candidate fights. Across three stages that is **29,298 per arm**, 87,894 tuning fights and 2,304 candidates. A uses nineteen novice melee clusters; B uses ten novice and nine regular full-army clusters; C uses one cluster per doctrine. The slight B tuning imbalance is explicit; validation has 100 per level.

The final audit reconstructs **107,094 raw tuning/validation fights**, **0 cache hits**, and twelve additional replay captures: **107,106 executed fights**. Zero controller failures, zero equation changes and zero forks/search calls/artillery rollouts in every retained fight metric and replay metric. All twelve capture summaries equal their original played-fight summaries. [Audit](s4_amended_development/AUDIT.json).

[Per-use seed ledger](s4_amended_development/s4_seeds.json) records every stage, split, arm, candidate, seed, opponent, orientation and hit status, including capture reuse. Tuning ranges are 410000000/411000000/412000000 + [0,18]; validation uses each stage base +100000+[0,99], shared across arms/configurations. Final C head checks use +101000+[0,99]. No judging generator or judging seeds were used. result_cache.py supplies the admitted binary/source/schema/helper namespace; archived pycma sources and dependency metadata are in s4_amended_resources/.

Ten native workers. Actual amended tuning/validation/capture duration: **128.85 minutes**; original main run 34.48 minutes, combined **163.33 minutes**, below the 180-minute native-run cap. The initial 90–120-minute amended estimate and later completion estimates were too short, particularly for full validation; updates and revisions were reported during execution. No run code or test edits occurred while the amended run was active.

## Stage results and best knobs

S is survivors minus enemy survivors. Both orientations are averaged into one cluster before statistics. Each head comparison has 100 validation clusters. C has 100 clusters per doctrine (1,900 configuration clusters), sharing 100 seeds across all nineteen doctrines; panel mean SE uses the 100 seed-block means. SDs, SEs and normal 95% intervals are descriptive development measurements, not registered verdicts.

A has no projectile asymmetry. B/C scripted brains can see shots and shells while our controllers cannot. However, native config_codec.cpp lines 244–245 explicitly disable shot/shell dodging for novice; regular enables shell dodging and raw shot leading. Projectile dodging therefore cannot explain losses against novice. Army composition changes from A to B, and tuning objective/knobs change from B to C; these comparisons do not isolate the cause of full-army losses.

### Stage A

[Exact knobs](s4_amended_development/A_best.json) · [validation and keyed scores](s4_amended_development/A_validation.json)

| Knob | Resonator | Morale | Push-pull |
|---|---:|---:|---:|
| K | 3.06216 | 1.00575 | — |
| K_t | 2.50571 | 4.81765 | — |
| kappa | 10.3238 | 41.6793 | — |
| beta | 0.335063 | 0.458999 | — |
| G | 2.12239 | 3.29393 | 4.99956 |
| w | 2.75309 | 1.32453 | — |
| f | 1.05569 | 0.941449 | 0.303754 |
| gamma | 0.64583 | 1.86026 | — |
| omega_melee | -0.0420122 | — | — |
| omega_ranged | -0.19272 | — | — |
| lambda_melee | — | 0.3331 | — |
| lambda_ranged | — | 0.0697923 | — |

| Arm | Validation comparison | Mean S | Cluster SD | SE | 95% mean interval |
|---|---|---:|---:|---:|---|
| resonator | s4_melee10 / novice | 2.7650 | 1.9943 | 0.1994 | [2.3741, 3.1559] |
| morale | s4_melee10 / novice | 4.5250 | 0.8569 | 0.0857 | [4.3571, 4.6929] |
| pushpull | s4_melee10 / novice | 1.4050 | 2.4697 | 0.2470 | [0.9209, 1.8891] |
| nearest | s4_melee10 / novice | 1.3550 | 2.4332 | 0.2433 | [0.8781, 1.8319] |

| Arm | Selected tuning mean S | Tuning cluster SD | Evaluations in stage |
|---|---:|---:|---:|
| resonator | 3.0263 | 2.5738 | 9,766 |
| morale | 4.6316 | 0.7040 | 9,766 |
| pushpull | 2.8684 | 2.0605 | 9,766 |

### Stage B

[Exact knobs](s4_amended_development/B_best.json) · [validation and keyed scores](s4_amended_development/B_validation.json)

| Knob | Resonator | Morale | Push-pull |
|---|---:|---:|---:|
| K | 0.467111 | 0.0417454 | — |
| K_t | 2.16114 | 4.28162 | — |
| kappa | 47.8344 | 49.7907 | — |
| beta | 0.0914775 | 1.90797 | — |
| G | 4.98582 | 4.99579 | 4.94564 |
| w | 1.39887 | 0.545455 | — |
| f | 0.623753 | 1.04151 | 1.13 |
| gamma | 1.45537 | 1.63724 | — |
| omega_melee | 0.756052 | — | — |
| omega_ranged | 1.88943 | — | — |
| lambda_melee | — | 1.32512 | — |
| lambda_ranged | — | 0.00212886 | — |

| Arm | Validation comparison | Mean S | Cluster SD | SE | 95% mean interval |
|---|---|---:|---:|---:|---|
| resonator | s4_full_head / novice | 5.9200 | 4.3343 | 0.4334 | [5.0705, 6.7695] |
| resonator | s4_full_head / regular | -8.6850 | 0.7023 | 0.0702 | [-8.8226, -8.5474] |
| morale | s4_full_head / novice | -7.6150 | 6.5981 | 0.6598 | [-8.9082, -6.3218] |
| morale | s4_full_head / regular | 3.1000 | 6.2817 | 0.6282 | [1.8688, 4.3312] |
| pushpull | s4_full_head / novice | -2.4050 | 2.7668 | 0.2767 | [-2.9473, -1.8627] |
| pushpull | s4_full_head / regular | -0.9800 | 1.6095 | 0.1610 | [-1.2955, -0.6645] |
| nearest | s4_full_head / novice | -16.6150 | 3.9131 | 0.3913 | [-17.3820, -15.8480] |
| nearest | s4_full_head / regular | -23.8050 | 6.2595 | 0.6259 | [-25.0319, -22.5781] |

| Arm | Selected tuning mean S | Tuning cluster SD | Evaluations in stage |
|---|---:|---:|---:|
| resonator | 0.8158 | 9.0940 | 9,766 |
| morale | 0.0000 | 7.8863 | 9,766 |
| pushpull | -1.6842 | 3.1101 | 9,766 |

### Stage C

[Exact knobs](s4_amended_development/C_best.json) · [validation and keyed scores](s4_amended_development/C_validation.json)

| Knob | Resonator | Morale | Push-pull |
|---|---:|---:|---:|
| K | 0.114601 | 0.267131 | — |
| K_t | 2.86132 | 1.68746 | — |
| kappa | 49.7991 | 37.1589 | — |
| beta | 2.11563 | 0.399393 | — |
| G | 3.04199 | 4.23887 | 4.99392 |
| w | 1.74582 | 2.52393 | — |
| f | 1.14087 | 1.13974 | 1.13814 |
| gamma | 1.98402 | 1.73683 | — |
| omega_melee | -1.92665 | — | — |
| omega_ranged | 1.36789 | — | — |
| lambda_melee | — | 0.254088 | — |
| lambda_ranged | — | 0.0451582 | — |

| Arm | Validation comparison | Mean S | Cluster SD | SE | 95% mean interval |
|---|---|---:|---:|---:|---|
| resonator | s4_full_head / novice | -6.5650 | 5.3981 | 0.5398 | [-7.6230, -5.5070] |
| resonator | s4_full_head / regular | -8.9450 | 5.9679 | 0.5968 | [-10.1147, -7.7753] |
| resonator | nineteen-doctrine pool | 2.2392 | 13.2123 | 0.1898 (block) | [1.8672, 2.6112] (block) |
| morale | s4_full_head / novice | -11.0700 | 10.5385 | 1.0539 | [-13.1356, -9.0044] |
| morale | s4_full_head / regular | -10.0550 | 10.1097 | 1.0110 | [-12.0365, -8.0735] |
| morale | nineteen-doctrine pool | 3.3324 | 14.3193 | 0.2442 (block) | [2.8538, 3.8109] (block) |
| pushpull | s4_full_head / novice | -4.7550 | 3.1136 | 0.3114 | [-5.3653, -4.1447] |
| pushpull | s4_full_head / regular | -0.4150 | 1.0542 | 0.1054 | [-0.6216, -0.2084] |
| pushpull | nineteen-doctrine pool | -5.0761 | 5.4899 | 0.0624 (block) | [-5.1984, -4.9537] (block) |
| nearest | s4_full_head / novice | -17.2600 | 3.9832 | 0.3983 | [-18.0407, -16.4793] |
| nearest | s4_full_head / regular | -23.9300 | 6.4944 | 0.6494 | [-25.2029, -22.6571] |
| nearest | nineteen-doctrine pool | -19.9282 | 8.6055 | 0.0745 (block) | [-20.0743, -19.7821] (block) |

| Arm | Selected tuning mean S | Tuning cluster SD | Evaluations in stage |
|---|---:|---:|---:|
| resonator | 7.5789 | 12.8336 | 9,766 |
| morale | 10.0526 | 13.8031 | 9,766 |
| pushpull | -4.1579 | 5.6913 | 9,766 |

## Paired spreads, margin and bounded power proposal

Proposed **δ = 4.0 survivors**: max(1, quarter the maximum pooled validation SD of the two paired differences), rounded upward to 0.5. This applies the predeclared rule to amended validation; it is an owner decision and was not reduced to get a pass.

| Endpoint | Paired mean | Config-cluster SD | Shared-seed-block SD | Block SE | Block 95% interval | Upper SD, pooled / block / tuning |
|---|---:|---:|---:|---:|---|---|
| P2: resonator_minus_morale | -1.0932 | 14.1523 | 3.0226 | 0.3023 | [-1.6856, -0.5007] | 14.5426 / 3.3571 / 11.5602 |
| P3: resonator_minus_pushpull | 7.3153 | 12.9566 | 2.0907 | 0.2091 | [6.9055, 7.7250] | 13.2506 / 2.3110 / 12.8498 |

Noise uncertainty uses 2,000 bootstrap resamples, seed 811005, 95th-percentile upper SD. C seed blocks retain cross-doctrine covariance. Normal planning uses one-sided support alpha .0025 and power .90: n = ceil((z(.9975)+z(.90))²×variance/δ²), with floors 32 per head level and 16 per doctrine. P1 plans a hypothetical true mean δ above zero; P2/P3 plan true mean 2δ above margin δ. These are beneficial-effect planning assumptions, not fitted effect claims.

P2/P3 use the maximum of validation block upper variance, selected tuning pooled upper variance/19, and the independent-stratum upper variance floor. P1 uses the larger B tuning/C validation upper SD and a common n for both levels. B tuning uses earlier knobs and only ten/nine clusters; it is an exploratory noise allowance, not validation of final C knobs. All calculations and both-split summaries are in [POWER_PLANNING.json](s4_amended_development/POWER_PLANNING.json).

| Endpoint | Proposed n | Total configuration clusters | Within 2,000? |
|---|---|---:|---|
| P1 | 49 per head level | 98 | yes |
| P2 | 16 per doctrine / shared seed blocks | 304 | yes |
| P3 | 16 per doctrine / shared seed blocks | 304 | yes |

A larger n cannot reverse the observed negative final head means. No support/refutation/equivalence verdict is assigned to unregistered development data. The owner must approve δ and a future S5 specification separately; any endpoint over the 2,000-cluster bound requires an owner tradeoff.

S5 must explicitly pin its P1 knob source: this report supplies both B-tuned and final C-tuned head results; the current P1 planning calculation uses final C validation. Choosing B instead changes that planning input and requires a new declared calculation from the retained B data. S5 must also register its inference unit: these P2/P3 n values count independent shared-seed blocks (nineteen configurations each), while δ uses pooled configuration-cluster spread. The original Claude review also recommends controller-cost work before further large runs; no new native optimization or cost benchmark was performed here.

## Watching fights

Open a linked HTML locally in a browser. Each file embeds its compressed replay and needs no external dependencies. Play/pause, 1×/4×/10×, timeline scrub and target lines are available. Team outlines are blue/orange; fill shows resonator phase or morale commitment (the bounded transform of its state); grey units have no controller state; HP bars show health. Raw traces retain 30 Hz; display payloads retain 10 Hz plus the terminal frame. [Standalone loader](s4_replay.html) also opens .replay.json.gz files.

| Stage | Resonator | Morale | Push-pull | Nearest |
|---|---|---|---|---|
| A | [resonator](s4_amended_development/replays/A_resonator.html) | [morale](s4_amended_development/replays/A_morale.html) | [pushpull](s4_amended_development/replays/A_pushpull.html) | [nearest](s4_amended_development/replays/A_nearest.html) |
| B | [resonator](s4_amended_development/replays/B_resonator.html) | [morale](s4_amended_development/replays/B_morale.html) | [pushpull](s4_amended_development/replays/B_pushpull.html) | [nearest](s4_amended_development/replays/B_nearest.html) |
| C | [resonator](s4_amended_development/replays/C_resonator.html) | [morale](s4_amended_development/replays/C_morale.html) | [pushpull](s4_amended_development/replays/C_pushpull.html) | [nearest](s4_amended_development/replays/C_nearest.html) |

All twelve HTML viewers loaded with no browser runtime errors; play/pause, scrub and target controls were exercised. [Browser receipt](s4_checks/AMENDED_BROWSER_RECEIPT.json). Phase state is prepared at the tick boundary while commitment is newly computed; this display timing does not change played fights.

The selected amended Stage A resonator has nonzero role rates, but its ten captured tracks span less than 2π (maximum 3.96 rad). The separately retained original Stage A replay has five tracks spanning more than 2π, demonstrating available rotating trajectories without forcing the amended optimizer toward them. No locking/rotation necessity or qualifying candidate-group claim follows from these examples.

## Checks, deviations and remaining gate

The original current native/controller batch passed 220 tests in 32.89 seconds. The final amended optimizer/cache/schema batch passed 31 checks before this run. End-of-session report checks are retained in s4_checks. The audit reconstructs all candidate and validation scores from raw summaries, replays CMA ask/tell and best retention, confirms all budgets and both orientations, verifies all 100-cluster endpoints, checks every C fight metric (both orientations), rechecks admitted source/binary/optimizer identity, and compares every captured summary to its original fight.

Deviations: (1) the request changed during the original run; its completed STOP evidence was preserved and the owner authorized a separate amended run. (2) The amended request supersedes the old racing/2-SE optimizer and, by explicit owner clarification, the full-budget novice gate with A/B-only gates. (3) B tuning allocates ten novice and nine regular clusters. (4) The existing shared closed result schema was extended for S3 summaries; cache helper and native controller equations were unchanged. (5) pycma was installed only under project build/, with dependency metadata and source archive retained; frozen environment files were untouched. (6) Runtime/completion estimates were revised as full validation ran more slowly; the native-run cap was respected. (7) Earlier temporary helpers/logs were moved/copied into the project after owner correction; amended scripts, cache, logs, evidence and test temp roots stayed in the project. No controller failures, outcome-informed equations, budget restarts, new knobs/arms, judging seeds or recorded S5 execution.

**Remaining gate: owner approval of δ and the future S5 specification.** Claude approved this development record with notes, including pinning the knob source per endpoint, preserving both P1 levels and fixing the inference unit before judging. READY_FOR_S5 is the owner-directed development label, not permission to execute S5. A concurrent S5 draft was created separately; it is outside this S4 implementation commit.
