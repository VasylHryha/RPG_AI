NOT_READY

# S4 v2 development report

Implementer family: Codex (GPT-6). Exploratory scope: decision 0028 items 15-17 and the owner’s explicit request. Independent Claude review remains required.

**Resource stop before Stage C resonator generation 10.** The conservative projected combined duration was 181.8 minutes, exceeding the unchanged 180-minute cap. Expected duration was declared as 90–120 minutes. Execution measured 91.48 minutes (runner failure snapshot 91.45); adding the protocol’s 34.48 prior minutes gives 125.93 minutes at that snapshot. This was a projection stop before exhausting the actual allowance, not a novice performance stop or controller failure. No budget extension, retry or extra fight followed it.

A and B completed all tuned budgets and all four arms’ validation. Both novice gates passed. C has the resonator’s initial configuration and nine complete generations (5,510 fights), with no morale/push-pull tuning, validation, final selection, or replay. Its partially retained candidate is in C_resonator_tuning.json; failure.json retains the last complete B knobs. Partial C data cannot support P2/P3, δ or n planning.

Part 1 committed before development: `8e6e97ea496f48ddeb85b8882c1dbf292c70d2d6`. [Affected tests](s4_v2_checks/tests.stdout.txt): 87 passed in 75.91 seconds; [parity and engineering receipt](s4_v2_checks/PART1_PARITY.json): 324 v0/v1 fixture summaries byte-identical (152 S3 per skeleton, 12 amended v0 replays and eight v1 replays), plus 38 v2 engineering fixtures per stateful arm, maximum refinement 0.0022835 < 0.02. One contract-test compile variable collision was fixed before tests; its failed build log is retained separately.

Section 13 revision 5 and Clarifications (22cdd21) are implemented: full threat-precise producing-tick attribution; centre-distance kite/outranged laws; deterministic eight nearest plus extra threats capped at sixteen; weighted means; gamma fixed at 1; 11/11/3 knobs. Q3’s explicit own-artillery committed-distance override max(f_c R_i, 1.05 Rmin) applies in both range cases. V0/v1 remain unchanged on their fixtures. The prior contract-stop report stays in git history.

[V2 declaration](S4_V2_PROTOCOL.md) retains the [amended protocol](S4_AMENDED_PROTOCOL.md): pycma 4.5.0 ask/tell, population 16, sigma .25, 16 generations, 19 fixed common tuning clusters, 9,766 evaluations per tuned arm/stage. B uses ten novice/nine regular tuning clusters; validation has 100 per level. A starts at midpoints; later stages start from prior tuning-selected best. Validation never selects knobs. All evaluated scores enter covariance adaptation, and ties retain the earlier best.

[Fresh seed declaration](S4_V2_SEEDS.json): independent development allocations 610000000/611000000/612000000, validation +100000, C heads +101000. [Seed/configuration/orientation/cache uses](s4_v2_development/s4_seeds.json) and [run identity](s4_v2_development/run_identity.json) are retained. No judging root was read or used.

[Post-run partial reconstruction](s4_v2_development/PARTIAL_AUDIT.json) verifies 66,506 fresh logged fights, zero hits, 1,680 CMA candidates, paired orientations, exact ask/tell and retention, all twelve complete 100-cluster validation endpoints and eight matching replay captures. Total native executions: 66,514. Zero controller failures, forks, search calls or artillery rollouts in executed data, including partial C. Run code, source/build, optimizer, design and specification hashes remain unchanged. The separate post-run auditor executes no fights; no full-run readiness is claimed.

| Stage | Resonator | Morale | Push-pull | Validation |
|---|---:|---:|---:|---|
| A | 9,766 | 9,766 | 9,766 | complete, all four arms |
| B | 9,766 | 9,766 | 9,766 | complete, all four arms |
| C | 5,510 (initial + 9 generations) | not_run: cap | not_run: cap | not_run: cap |

Validation S is survivors minus enemy survivors, averaged across both orientations per seed. Intervals below are descriptive normal 95% intervals, not registered verdicts. A uses melee-only armies and removes projectile observation asymmetry; B changes army composition too, so differences are not attributable solely to visibility.

## Stage A validation

| Arm | Endpoint | Mean S | SD | SE | Descriptive 95% interval | Timeouts / fights | Mean enemy guns alive |
|---|---|---:|---:|---:|---|---|---:|
| resonator | s4_melee10 / novice | 3.9000 | 1.2831 | 0.1283 | [3.6485, 4.1515] | 1 / 200 | 0.0000 |
| morale | s4_melee10 / novice | 5.9800 | 0.9071 | 0.0907 | [5.8022, 6.1578] | 3 / 200 | 0.0000 |
| pushpull | s4_melee10 / novice | -2.4850 | 2.6850 | 0.2685 | [-3.0113, -1.9587] | 0 / 200 | 0.0000 |
| nearest | s4_melee10 / novice | 0.8350 | 2.5287 | 0.2529 | [0.3394, 1.3306] | 0 / 200 | 0.0000 |

Novice stop gate: pass (resonator mean S = 3.9000 > 0).

| Arm | Selected tuning mean S | Cluster SD | Stage evaluations |
|---|---:|---:|---:|
| resonator | 4.4474 | 0.9559 | 9,766 |
| morale | 6.3684 | 0.7235 | 9,766 |
| pushpull | -0.3684 | 2.7021 | 9,766 |

## Stage B validation

| Arm | Endpoint | Mean S | SD | SE | Descriptive 95% interval | Timeouts / fights | Mean enemy guns alive |
|---|---|---:|---:|---:|---|---|---:|
| resonator | s4_full_head / novice | 16.3850 | 7.5384 | 0.7538 | [14.9075, 17.8625] | 0 / 200 | 0.2350 |
| resonator | s4_full_head / regular | -4.1000 | 3.5774 | 0.3577 | [-4.8012, -3.3988] | 107 / 200 | 7.8200 |
| morale | s4_full_head / novice | 9.7200 | 9.4781 | 0.9478 | [7.8623, 11.5777] | 0 / 200 | 1.0800 |
| morale | s4_full_head / regular | 2.9300 | 6.3818 | 0.6382 | [1.6792, 4.1808] | 188 / 200 | 8.5900 |
| pushpull | s4_full_head / novice | -5.6900 | 3.4081 | 0.3408 | [-6.3580, -5.0220] | 0 / 200 | 5.7550 |
| pushpull | s4_full_head / regular | -12.4350 | 3.0148 | 0.3015 | [-13.0259, -11.8441] | 0 / 200 | 10.0000 |
| nearest | s4_full_head / novice | -16.0550 | 3.6604 | 0.3660 | [-16.7724, -15.3376] | 0 / 200 | 9.8550 |
| nearest | s4_full_head / regular | -23.5150 | 6.3752 | 0.6375 | [-24.7645, -22.2655] | 0 / 200 | 10.0000 |

Novice stop gate: pass (resonator mean S = 16.3850 > 0).

| Arm | Selected tuning mean S | Cluster SD | Stage evaluations |
|---|---:|---:|---:|
| resonator | 9.1579 | 13.6941 | 9,766 |
| morale | 14.1842 | 10.5465 | 9,766 |
| pushpull | -8.6842 | 3.2838 | 9,766 |

## Stage C and planning

Resonator tuning is partial: 9/16 generations, selected tuning mean S 12.8684 on 19 fixed clusters. This is tuning evidence only; no held-out C comparison is available. Morale and push-pull received no C budget; nearest has no C validation. The unequal partial budgets preclude a C arm comparison.

| Arm | Nineteen-doctrine validation | Fresh novice/regular heads | Timeout/gun validation diagnostics | Replay |
|---|---|---|---|---|
| resonator | not_run: projection cap | not_run: projection cap | not_run: projection cap | not_exported: projection cap |
| morale | not_run: projection cap | not_run: projection cap | not_run: projection cap | not_exported: projection cap |
| pushpull | not_run: projection cap | not_run: projection cap | not_run: projection cap | not_exported: projection cap |
| nearest | not_run: projection cap | not_run: projection cap | not_run: projection cap | not_exported: projection cap |

Fresh P2/P3 paired spread, δ and bounded n: **not_run**, because C validation did not execute. Historical v0/v1 planning is not v2 evidence. [End states for every executed arm/setting, separately by tuning and validation](s4_v2_development/END_STATES_BY_SPLIT.json) retain timeouts and enemy guns alive, including all nineteen partial-C tuning settings; reused tuning seeds across candidates are descriptive, not independent validation.

## Viewer exports

| Arm | Stage A | Stage B | Stage C |
|---|---|---|---|
| resonator | [Replay](s4_v2_development/replays/A_resonator.html) | [Replay](s4_v2_development/replays/B_resonator.html) | not_exported: cap before completed stage |
| morale | [Replay](s4_v2_development/replays/A_morale.html) | [Replay](s4_v2_development/replays/B_morale.html) | not_exported: cap before completed stage |
| pushpull | [Replay](s4_v2_development/replays/A_pushpull.html) | [Replay](s4_v2_development/replays/B_pushpull.html) | not_exported: cap before completed stage |
| nearest | [Replay](s4_v2_development/replays/A_nearest.html) | [Replay](s4_v2_development/replays/B_nearest.html) | not_exported: cap before completed stage |

Each completed stage has one exported replay per arm. Raw gzip captures and packaged viewer data match the corresponding validation orientation exactly. No new browser qualification is claimed.

## Remaining gate and scope

Claude reviews the committed implementation and this partial development record. The cap stop is retained; no continuation or budget change is selected here. Full C development remains incomplete, and any continuation needs an explicit resource/budget decision before new execution. No S5 registration is ready. δ, a fresh specification and judging execution remain owner decisions.

No code edits or tests ran during development. No equation changes, tuning restarts, judging seeds, registration, recorded run, SPEC_0G changes, frozen GeoMind changes, committed receipt changes, milestone status changes or growing_shapes changes were made by this task. No tactical superiority, equivalence or RRG recursion is inferred. [Raw fights](s4_v2_development/fights.jsonl.gz), candidate checkpoints, [failure](s4_v2_development/failure.json) and [execution timing](s4_v2_checks/EXECUTION.json) are retained.
