# Stage B diagnosis and correction

The nets fail through interacting target, geometry and fire errors. Fire calibration alone is insufficient: all five nets choose no melee target on every recorded melee row, and make no melee attacks in the ten matched fights per arm. Artillery aims are wrong even on the training distribution. Ranged/artillery target errors grow when the student controls the fight, supporting full-fight DAgger after correcting the fitting objective. These are descriptive findings from existing raw fights, not causal intervention results or evidence that Stage B will win.

Baseline: HEAD a795ee4ffc641f0398c2131bd2d186297f6445e4. Owner stopped Stage A look 20. There are 73 completed recordings: ten each for N1/N1h/N1r and nine each for N2/N2J0/O/T in regular fights, plus one C3 fight per policy. Each net has ten valid O-matched pairs: nine regular and one C3. Three student-only regular completions remain unmatched and are excluded from paired comparisons. No new full fights were run for this diagnosis.

## Matched outcome and target collapse

| Policy | Wins / 10 | Mean own deaths | Mean enemy body deaths | Mean end time, s | Target=None %, melee / ranged / artillery |
|---|---:|---:|---:|---:|---|
| N1 | 0 | 49.2 | 3.2 | 83.75 | 100 / 76.6 / 85.9 |
| N1h | 0 | 49.1 | 6.3 | 80.89 | 100 / 35.8 / 65.0 |
| N1r | 0 | 49.1 | 3.8 | 81.00 | 100 / 73.8 / 84.5 |
| N2 | 0 | 50.0 | 4.9 | 72.57 | 100 / 91.2 / 93.1 |
| N2J0 | 0 | 50.0 | 4.6 | 72.54 | 100 / 98.8 / 98.1 |
| O | 10 | 33.7 | 50.0 | 41.62 | 87.0 / 38.0 / 36.4 |
| T | 10 | 34.7 | 50.0 | 40.53 | — |

The legacy `enemy_kills` endpoint counts enemy body deaths. It does not attribute their source. N2J0 causes zero own-attributed damage across the ten paired fights, so its 46 enemy deaths are enemy friendly fire. N2 causes 52 damage and makes some ranged/artillery attacks. N2 and N2J0 therefore have distinct raw behavior. Dropping N2J0 saves one training lane; it does not establish that J is irrelevant.

## Opportunity-conditioned fire and observed attack starts

An opportunity is an alive physical tick with some enemy in legal range, cooldown <=0, enough energy, and no guard/busy/react veto. Repeated eligible ticks are prolonged chances, not independent opportunities. Prep starts count observed zero-to-positive prep transitions, so zero-windup starts may be missed. Engine-release intent ticks are separately retained in the counts JSON and must not be interpreted as projectile births.

| Policy | Active fire on eligible ticks %, melee / ranged / artillery | Observed prep starts over ten pairs, melee / ranged / artillery |
|---|---|---|
| N1 | 11.9 / 54.7 / 69.1 | 0 / 103 / 128 |
| N1h | 3.1 / 61.1 / 71.4 | 0 / 423 / 1003 |
| N1r | 8.0 / 50.7 / 68.9 | 0 / 44 / 66 |
| N2 | 10.8 / 62.2 / 65.6 | 0 / 14 / 38 |
| N2J0 | 13.4 / 62.1 / 69.4 | 0 / 0 / 0 |
| O | 100 / 100 / 100 | 195 / 1879 / 2271 |

Active-fire intent without a valid target does not start an attack. This explains why substantial artillery active-fire percentages coexist with negligible attacks. The original offline “active predictions / oracle active rows” ratio (60–78%) is also not recall: it does not identify true positives.

## Position, formation and death attribution

Within-role mean RMS formation radius is about 25–30 px for net artillery versus 100.2 px for O, and about 36–39 px for net ranged versus 100.7 px for O. Net melee radii are 53–58 px versus 73.2 px for O. Those are descriptive occupancy measurements; enemy approach and the longer losing fights change their denominator. Per-role approach/retreat/stationary ticks, nearest-enemy distance, chosen-target counts and out-of-range seconds are retained in the counts JSON. A lower out-of-range fraction during a losing fight does not establish improved positioning.

Enemy artillery accounts for the largest absolute own-death count. The largest *excess versus matched O* is enemy melee: O loses seven units to enemy melee over ten pairs, whereas nets lose 137–180, an excess of 130–173. Enemy artillery kills 254 O units versus 307–335 net units, an excess of 53–81. O loses 37 units to its own ranged/artillery fire, versus 0–23 for nets. Death source team/role/id and timestamps are preserved, along with first real projectile births and censored melee first-damage events in `causal_audit`.

Every net's first command divergence from shadow O occurs at t=1/30 s. The first paired position divergence is recorded separately; command disagreement at the opening is not itself the point at which the world state has changed.

## O replay control and distribution comparison

Offline O labels reproduce recorded O executed commands with exactly zero total error over 447,270 labeled unit rows across the ten completed O fights, including aim. Replay reconstructs public predecision snapshots and advances O's own history without a physical step. This is strong control evidence on these recorded trajectories; unrecorded private/smoothed state remains a limitation for other occupancy. Tiny native shadow-on/off fixtures additionally check that labeling cannot alter student actions or world state.

The training-distribution comparison replays each whole training prefix for learned memory, then evaluates the same four 90-tick windows used for fitting. On-policy comparison uses every living unit tick in completed paired student fights. Both compare with O executed labels on the *same* public state. Categorical fire/target and multiplier errors are comparable. Native raw movement is already clamped and artillery aim projected; offline Python movement/aim are not. Movement/aim measurements therefore retain an adapter difference and are not reported as pure distribution gaps.

Artillery on-policy aim disagreement is 15,618/15,620 for N1, 35,793/35,793 for N1h, 50,101/50,101 for N1r and 5,293/5,293 for N2. N2J0 has no shadow-O aim rows and its rate is unavailable. Training aim disagreement is approximately 99.7% for the first three nets: poor geometric fitting predates student occupancy. Movement disagreements are also near universal on training and student states. The original arena-normalized MSE contributes little relative to categorical CE despite large pixel errors.

## Completed distribution-gap readout

Rates below are disagreement percentages (training → on-policy raw command), with target gap in percentage points. Counts and full denominators are in the JSON. They are whole correlated rollout rows versus four sampled training windows, not independent samples or significance tests.

| Arm | Role | Fire training → on-policy % | Target training → on-policy % | Target gap, pp |
|---|---|---:|---:|---:|
| N1 | melee | 32.4 → 27.0 | 14.4 → 13.0 | -1.4 |
| N1 | ranged | 28.4 → 26.5 | 34.1 → 68.6 | +34.5 |
| N1 | artillery | 27.3 → 22.5 | 39.9 → 81.7 | +41.8 |
| N1h | melee | 31.9 → 24.4 | 11.5 → 14.9 | +3.4 |
| N1h | ranged | 28.0 → 23.5 | 32.0 → 48.0 | +16.1 |
| N1h | artillery | 28.7 → 16.9 | 37.6 → 70.3 | +32.6 |
| N1r | melee | 32.7 → 25.9 | 14.3 → 15.1 | +0.8 |
| N1r | ranged | 28.6 → 26.7 | 34.0 → 66.5 | +32.5 |
| N1r | artillery | 27.4 → 23.2 | 39.8 → 81.9 | +42.0 |
| N2 | melee | 32.5 → 26.4 | 14.0 → 15.9 | +1.9 |
| N2 | ranged | 29.1 → 25.8 | 26.4 → 74.5 | +48.2 |
| N2 | artillery | 32.2 → 26.3 | 32.8 → 80.0 | +47.2 |
| N2J0 | melee | 32.5 → 25.8 | 14.0 → 14.8 | +0.8 |
| N2J0 | ranged | 29.1 → 26.3 | 26.4 → 77.0 | +50.6 |
| N2J0 | artillery | 32.2 → 24.7 | 32.8 → 83.6 | +50.9 |

Fire gap is not consistently positive: fitting already suppresses fire. The strongest positive occupancy gap is ranged/artillery targeting; melee failure and geometric errors already exist on oracle occupancy. Multiplier errors are included per role/head in JSON and are small on policy.

## Actual first attacks and eligible-tick denominators

First-attack medians are over units with an observed event; `never` units are right censored. Ranged events use actual projectile born times; artillery uses actual launches; melee uses first dealt-to-enemy event. Observer timestamps include the engine clock origin. These medians must be read alongside censoring and target/fire counts.

| Arm | Role | Eligible ticks | Prep starts / eligible ticks | Actual projectile births | First-attack median, s | Never / observed units |
|---|---|---:|---:|---:|---:|---:|
| N1 | melee | 3306 | 0 / 3306 | 0 | NA | 100 / 100 |
| N1 | ranged | 164745 | 103 / 164745 | 79 | 41.73 | 274 / 300 |
| N1 | artillery | 118586 | 128 / 118586 | 111 | 25.63 | 79 / 100 |
| N1h | melee | 3385 | 0 / 3385 | 0 | NA | 100 / 100 |
| N1h | ranged | 190270 | 423 / 190270 | 387 | 41.07 | 233 / 300 |
| N1h | artillery | 95339 | 1003 / 95339 | 942 | 17.78 | 50 / 100 |
| N1r | melee | 3639 | 0 / 3639 | 0 | NA | 100 / 100 |
| N1r | ranged | 144599 | 44 / 144599 | 27 | 28.22 | 292 / 300 |
| N1r | artillery | 124874 | 66 / 124874 | 35 | 37.30 | 85 / 100 |
| N2 | melee | 3847 | 0 / 3847 | 0 | NA | 100 / 100 |
| N2 | ranged | 228109 | 14 / 228109 | 7 | 31.90 | 296 / 300 |
| N2 | artillery | 111155 | 38 / 111155 | 29 | 21.03 | 93 / 100 |
| N2J0 | melee | 3367 | 0 / 3367 | 0 | NA | 100 / 100 |
| N2J0 | ranged | 222505 | 0 / 222505 | 0 | NA | 300 / 300 |
| N2J0 | artillery | 126032 | 0 / 126032 | 0 | NA | 100 / 100 |
| O | melee | 198 | 195 / 198 | 0 | 14.13 | 15 / 100 |
| O | ranged | 43683 | 1879 / 43683 | 1735 | 16.80 | 7 / 300 |
| O | artillery | 2516 | 2271 / 2516 | 2173 | 9.62 | 0 / 100 |

## Death-time and first world-state divergence

| Arm | Own death-time median, s | Enemy melee deaths | Enemy artillery deaths | First paired position divergence, s |
|---|---:|---:|---:|---|
| N1 | 25.20 | 140 | 334 | 0.06667 |
| N1h | 25.40 | 149 | 308 | 0.06667 |
| N1r | 24.97 | 137 | 335 | 0.06667 |
| N2 | 27.18 | 171 | 310 | 0.06667 |
| N2J0 | 26.73 | 180 | 307 | 0.06667 |
| O | 23.00 | 7 | 254 | control |

The missing-arm replay plus full causal/hash audit took 362.6 s. Earlier archived raw-shadow and four retained training replays were completed separately; their combined exact elapsed time was not retained after the N2J0 registry stop and is not invented. Supplemental source hashes and historical archive bindings remain separate in the JSON.

## Correction and execution boundary

Stage B adds ordinary fire CE plus validation-only role thresholds chosen to match O active counts as closely as attainable under shared safety precedence, with precision/recall and untouched-threshold test reports. It adds training-only per-role None/nonzero target balancing and goal/aim SmoothL1 in the policy's existing 100-pixel geometry units. Ten epochs and four windows per fight remain fixed. Four arms train concurrently under a measured projection, 20% margin, and maximum three-hour live cap; completed epochs resume.

Full-fight DAgger collects 22 fresh fights per student per round (two regular, twenty C3), student actions only, O labels on a separate cloned world. Each student aggregates only its own occupancy with round 0. One round is the default; a measured second round is supported. Full-sequence calibrated native parity gates each collection/readout. New paired outcomes run look 20 then 50; unique invocation receipts include stops and partial summaries. The protocol contains normalization and yes/no stop ledgers.

Actual ten-epoch training, DAgger and fresh looks have not run. The local Claude CLI is logged out, so the user-required Claude-authored Stage B TRAIN_CAP cannot be created here. No cap authorship was impersonated. Authenticated host commands and measured/expected times are in HOST_COMMANDS_STAGEB.md. Stage A files and trained artifacts remain unchanged, docs/PLAN_CURRENT.md is untouched, and this is a new uncommitted development revision.
