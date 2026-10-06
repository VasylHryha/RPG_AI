NOT_READY

# S4 v4 development report

Implementer family: Codex (GPT-6). Owner-authorized exploratory development under decision 0028 items 16–18 and DESIGN_0G section 15 revision 7, clarified at 914dda4. The contract-stop report remains in history. Independent Claude review, owner margin and a fresh S5 specification remain separate gates.

**NOT_READY:** the conservative projection guard stopped before Stage C push-pull generation 14. A/B novice gates passed, but C validation and C replays were not run. Stage B resonator mean S was +9.365 against novice and −22.175 against regular. This record establishes completed v4 engineering and partial development, with no final C comparison or S5 readiness.

Travel-time holds start only on out-ranged binary mode switches: |d_escape − d_commit| / observed own speed, with no hold at speed ≤ 1 px/s or on first pair initialization. Crossings during a hold are ignored; expiry or the 0.1-own-reach band releases it. All underlying controller states keep evolving. Commit focus selects the highest damage-weight committed out-ranged pair among living pairs, tie by lowest id; fallback uses the inherited E_i weighted mean and ally forces remain unchanged. Push-pull has constant c=1 and no switches. No new knobs (11/11/3).

Output-only 30 Hz decision records retain focus, pair modes/remaining holds, c and feasibility. Feasibility uses prepare(k) geometry and realized tick-k displacement after collision and clipping. Undefined values are null with the four specified reasons and excluded from cosine means. Per-pair holds and focus are clone-owned and death removes them. The six section-15 checks and fake-worker deadline/cleanup tests passed in the completed Part 1 batch; v0–v3 predecessor fixture parity is recorded in s4_v4_checks/PART1_PARITY.json.

Part 1 commit: `9e780c016afde5b9304072b53e7b16dccb578367`. Native, source, optimizer and code identities are pinned in [run_identity.json](s4_v4_development/run_identity.json).

Exactly the amended CMA-ES allocation: pycma 4.5.0, ask/tell, population 16, sigma .25, 16 generations, 19 common tuning clusters and 9,766 evaluations per tuned arm/stage. A starts at midpoints; B/C inherit tuning winners. Earlier ties retain the incumbent; all scores enter adaptation. Nearest is untuned. B tuning has ten novice/nine regular; validation has 100 clusters per endpoint, both orientations. All arms finish A/B validation before the resonator novice mean S≤0 gate. C has nineteen elite-no-rollout doctrines and fresh novice/regular heads; every metric is checked for zero planner work.

Fresh development bases 940000000/941000000/942000000, validation +100000 and C heads +101000; disjoint from prior S4 revisions and S3. The new local s4_seeds.json ledger records every use. No judging root was consulted and no judging entropy, registration or recorded run was used. Raw replays, seed dumps and logs remain local, outside commits.

Expected duration 150–240 minutes with ten workers; measured 239.46 minutes. The original owner-authorized task cap is 360 minutes, retaining 70.12 prior execution minutes and 289.88 minutes for this fresh restart. Bounded submission carries one absolute monotonic deadline to workers, clamps subprocess timeouts to remaining allowance, cancels pending work and kills active child process groups on stop. Replays use that same deadline. Cleanup has a separate bounded two-second child-reaping allowance. Conservative remaining-work projection runs before each generation.

Execution stopped at stage C: TimeoutError('projected combined runtime 360.0 minutes exceeds 360; stop before continuing'). Partial budgets: {'resonator': 29298, 'morale': 29298, 'pushpull': 27474}. Incomplete stages are not validation comparisons.

| Stage | Resonator novice mean S | A/B gate |
|---|---:|---|
| A | 5.2000 | pass |
| B | 9.3650 | pass |

Intervals are descriptive normal 95% intervals. Doctrine pool intervals use independent shared-seed blocks to retain covariance. A uses melee only; B/C add ranged/artillery and projectile observation asymmetry. Their differences do not isolate projectile visibility.

## Stage A validation

| Arm | Endpoint | Mean S | SD | SE | 95% interval | Timeouts / fights | Mean enemy guns alive |
|---|---|---:|---:|---:|---|---|---:|
| resonator | s4_melee10 / novice | 5.2000 | 1.4302 | 0.1430 | [4.9197, 5.4803] | 0 / 200 | 0.0000 |
| morale | s4_melee10 / novice | 4.9900 | 1.4616 | 0.1462 | [4.7035, 5.2765] | 0 / 200 | 0.0000 |
| pushpull | s4_melee10 / novice | 7.5050 | 0.8242 | 0.0824 | [7.3435, 7.6665] | 0 / 200 | 0.0000 |
| nearest | s4_melee10 / novice | 0.9400 | 2.3669 | 0.2367 | [0.4761, 1.4039] | 0 / 200 | 0.0000 |

Regular is not_run in A: novice melee-only is declared. Guns are zero by army construction.

| Arm | Selected tuning mean S | SD | Stage evaluations |
|---|---:|---:|---:|
| resonator | 5.9211 | 1.0706 | 9,766 |
| morale | 5.4474 | 0.9559 | 9,766 |
| pushpull | 7.5000 | 0.9574 | 9,766 |

## Stage B validation

| Arm | Endpoint | Mean S | SD | SE | 95% interval | Timeouts / fights | Mean enemy guns alive |
|---|---|---:|---:|---:|---|---|---:|
| resonator | s4_full_head / novice | 9.3650 | 4.0439 | 0.4044 | [8.5724, 10.1576] | 0 / 200 | 0.1200 |
| resonator | s4_full_head / regular | -22.1750 | 4.7871 | 0.4787 | [-23.1133, -21.2367] | 0 / 200 | 9.0650 |
| morale | s4_full_head / novice | 17.2300 | 4.3863 | 0.4386 | [16.3703, 18.0897] | 0 / 200 | 0.0050 |
| morale | s4_full_head / regular | -15.4050 | 10.1913 | 1.0191 | [-17.4025, -13.4075] | 76 / 200 | 9.6450 |
| pushpull | s4_full_head / novice | -18.5100 | 2.7015 | 0.2701 | [-19.0395, -17.9805] | 0 / 200 | 9.9900 |
| pushpull | s4_full_head / regular | -7.2550 | 13.1904 | 1.3190 | [-9.8403, -4.6697] | 163 / 200 | 10.0000 |
| nearest | s4_full_head / novice | -17.5850 | 3.7194 | 0.3719 | [-18.3140, -16.8560] | 0 / 200 | 9.9350 |
| nearest | s4_full_head / regular | -22.6750 | 7.0812 | 0.7081 | [-24.0629, -21.2871] | 0 / 200 | 9.9950 |

| Arm | Selected tuning mean S | SD | Stage evaluations |
|---|---:|---:|---:|
| resonator | -4.5263 | 16.3652 | 9,766 |
| morale | 3.3947 | 17.5028 | 9,766 |
| pushpull | -10.8158 | 9.6727 | 9,766 |

## Stage C validation

not_run for all arms and endpoints: the runtime projection stopped C tuning before C validation.


Completed Stage C tuning is not C validation. The retained partial push-pull incumbent below is not promoted to a final C configuration.

| C tuning arm | Completed generations | Evaluations / planned | Selected tuning mean S | SD |
|---|---:|---|---:|---:|
| resonator | 16 / 16 | 9,766 / 9,766 | -1.6842 | 15.3534 |
| morale | 16 / 16 | 9,766 / 9,766 | 14.6316 | 11.0112 |
| pushpull | 13 / 16 | 7,942 / 9,766 | -3.3158 | 9.3023 |

C novice/regular heads and all nineteen doctrine endpoints are not_run for every arm, as are all four C replay exports. Fresh P2/P3 spreads, margin and sample-size planning are not_run because C validation is absent. No missing C result is replaced with a tuning score.

[Partial reconstruction](s4_v4_development/AUDIT.json) independently checks 88,470 scored fights (all fresh; zero cache hits), eight matching capture fights and 2,256 CMA candidates. A/B use 9,766 evaluations for each tuned arm; C resonator/morale use 9,766 each, C push-pull uses 7,942. Both orientations, all completed endpoint scores, all evaluated ask/tell generations, stable retention, raw/ledger configs, source/build/optimizer pins and replay equality reconstruct. Zero controller failures and zero planner counters. Coverage explicitly marks 12 A/B arm-endpoints evaluated and 84 C arm-endpoints not_run. The separate read-only auditor ran in 19.69 seconds with zero combat executions; seven focused report/auditor tests passed in 0.29 seconds. The launch/report source hashes remain unchanged.

## Decision trace diagnostics

These are exported-replay measurements, not telemetry across the entire validation population. A exports novice; B/C export regular for each arm. Full 30 Hz records stay in the local replay package/HTML. Means include only defined cosine samples; undefined counts are separate.

| Replay | Holds started | Ended early | Mean completed hold s | Reversals / unit-minute | Mean cosine | Focus fraction |
|---|---:|---:|---:|---:|---:|---:|
| [A_resonator.html](s4_v4_development/replays/A_resonator.html) | 596 | 122 | 2.5096 | 7.4976 | 0.5654 | 0.5303 |
| [A_morale.html](s4_v4_development/replays/A_morale.html) | 0 | 0 | null | 0.0000 | 0.9059 | 1.0000 |
| [A_pushpull.html](s4_v4_development/replays/A_pushpull.html) | 0 | 0 | null | 0.0000 | 0.8707 | 1.0000 |
| [B_resonator.html](s4_v4_development/replays/B_resonator.html) | 3364 | 1718 | 6.1526 | 35.6712 | 0.9185 | 0.7652 |
| [B_morale.html](s4_v4_development/replays/B_morale.html) | 343 | 26 | 11.1349 | 1.5284 | 0.8125 | 0.4956 |
| [B_pushpull.html](s4_v4_development/replays/B_pushpull.html) | 0 | 0 | null | 0.0000 | 0.3247 | 1.0000 |

[DECISION_TRACE_SUMMARY.json](s4_v4_development/DECISION_TRACE_SUMMARY.json) contains expiry/disappearance counts, planned holds, terminal censoring, pair reversals, cosine distribution/quartiles and undefined counts per reason. Nearest has no skeleton modes, holds or focus.

| Historical v3 regular replay | Threshold reversals / unit-minute |
|---|---:|
| C_regular_morale.jsonl.gz | 0.6588 |
| C_regular_resonator.jsonl.gz | 33.6628 |

Historical v3 regular diagnostic replays use different seeds and independently tuned knobs. Unit reversal ticks count at most one change per unit/tick; v4 additionally counts every pair change. V3 reconstruction is a threshold proxy for persistent out-ranged pairs; no v3 hold, focus or feasibility telemetry exists. No causal or population-wide claim follows.

Mean completed hold includes expired, early-band and disappearance releases; terminal active holds are censored separately. Early releases mean target_band, not death. All values come from exported 30 Hz decisions, not validation-population telemetry.

Preferred pair distance and commitment do not guarantee global progress: ally forces, changing threats, collision and arena clipping can still oppose movement. Feasibility measures that gap; a changed trace distribution does not prove a combat mechanism caused a score difference. Separately tuned arms are controller-package comparisons, with different state laws and knob dimensions.


| Replay | Planned hold mean s | Expired | Disappeared | Active at terminal |
|---|---:|---:|---:|---:|
| A_resonator.html | 2.8773 | 446 | 25 | 3 |
| A_morale.html | null | 0 | 0 | 0 |
| A_pushpull.html | null | 0 | 0 | 0 |
| B_resonator.html | 11.3488 | 393 | 1237 | 16 |
| B_morale.html | 17.0663 | 220 | 97 | 0 |
| B_pushpull.html | null | 0 | 0 | 0 |

All immobile-release counts were zero. Early endings in the main table are target-band releases; disappearance/death and terminal censoring are separate.

| Replay | Defined cosine samples | no_reference | coincident | at_distance | zero_displacement |
|---|---:|---:|---:|---:|---:|
| A_resonator.html | 18726 | 0 | 0 | 0 | 0 |
| A_morale.html | 12451 | 0 | 0 | 0 | 0 |
| A_pushpull.html | 13623 | 0 | 0 | 0 | 0 |
| B_resonator.html | 23868 | 0 | 0 | 0 | 0 |
| B_morale.html | 26824 | 0 | 0 | 0 | 13218 |
| B_pushpull.html | 225050 | 0 | 0 | 0 | 0 |

| Regular replay comparison | v4 B reversals / unit-minute | Historical v3 C threshold proxy | Arithmetic difference |
|---|---:|---:|---:|
| resonator | 35.6712 | 33.6628 | +2.0084 |
| morale | 1.5284 | 0.6588 | +0.8696 |

This available comparison is v4 Stage B versus historical v3 Stage C, on unmatched seeds and independently tuned knobs; v3 provides a threshold proxy rather than exported pair-mode telemetry. These snapshots do not demonstrate reduced reversal rates. No matched C-v4 comparison exists because C exports were not run. B resonator has a high mean defined feasibility cosine (0.9185) despite regular mean S −22.175 and 9.065 enemy guns alive per fight. Directional movement feasibility alone does not establish tactical success.

## Margin and sample-size planning

not_run: C was not completed; no fresh P2/P3 δ/spread/n.

[Validation end states](s4_v4_development/VALIDATION_END_STATES.json) and [all tuning/validation end states](s4_v4_development/END_STATES_BY_SPLIT.json) report timeouts and living enemy artillery separately. A timeout reaches 150 seconds and is an ordinary scored fight. Raw fight/seed/replay files remain local and are hash-bound by LOCAL_ARTIFACTS.json; small summaries travel in the bundle.

No outcome-informed equation change during execution, budget extension, judging-seed use, S5 registration, recorded run, milestone status change or scientific acceptance. READY_FOR_S5, if reached, means completed development. No browser qualification or general tactical superiority is claimed.

## Execution accounting and preserved attempts

The projection error displays 360.0 minutes rounded to one decimal; its strict condition was projected combined runtime >360. The absolute deadline had not expired. Final runner time was 239.459811 minutes, outer wrapper 239.494224 minutes. Including both earlier attempts, actual wrapper execution was 309.612259 minutes, below 360. The remaining actual allowance was not used after the conservative stop. No worker timeout or outcome-dependent budget adjustment caused this stop.

The first attempt, preserved in `s4_v4_development_failed_r1/`, stopped after 38 initial fights, zero candidates and zero validation, on the normal-zip closure bug. It used 0.009453 minutes. The second, preserved in `s4_v4_development_failed_r2/`, stopped after 54,000 scored fights and four A captures, on an unrelated live DESIGN_0G append explicitly outside v4. It used 70.108582 minutes. The exact approved 914dda4 design was then pinned and all budgets restarted on wholly fresh 940/941/942 million bases, from original midpoint starts. Neither failed attempt selected restart knobs, margins or seeds. Their original receipts/raw files remain unchanged; both times are charged to the original allowance.

[Local artifact inventory](s4_v4_development/LOCAL_ARTIFACTS.json) binds all current and preserved-attempt evidence with SHA256 and sizes. Raw fights, candidates, seed declarations/ledgers, replay packages/HTML and console logs are available in this workspace and excluded from commits. Bundle-only review can verify small summaries and source identities; full reconstruction additionally needs those local raw artifacts. The earlier contract-stop report remains in Git history.

[Delivery note](s4_v4_checks/DELIVERY_NOTE.md) identifies the scoped, hook-checked commits and independently imported bundle. No registration, judging seeds, recorded run, milestone status change, push or acceptance occurred.
