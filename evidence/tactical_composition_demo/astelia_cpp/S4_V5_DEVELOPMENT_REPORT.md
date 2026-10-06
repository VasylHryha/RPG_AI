NOT_READY

# S4 v5 development report

Implementer family: Codex (GPT-6). Owner-authorized single exploratory development run under decision 0031 and amended DESIGN_0G section 17. A/B only; no C, judging, registration, S5 execution or scientific acceptance.

Stage B resonator: novice mean S **+5.6000**; regular mean S **-6.0250**. Regular minus the declared section-16 v3 baseline: **+1.5950**. Novice validation predicate: **True**; regular progress predicate: **True**.

Runner outcome: **PROGRESS**; report outcome: **NOT_READY**. The amended protocol reports PROGRESS after passing B and explicitly precludes READY_FOR_S5. Continuing to C requires a later declared allocation; PROGRESS does not establish beating regular or authorize S5.

The resonator still loses to regular on mean S. Relative to historical v3 B, regular mean rises 1.545 points while novice mean falls 11.750 points; morale regular mean is +9.530 with 198/200 timeouts and 9.700 living enemy guns per fight. This descriptive development improvement does not satisfy the owner’s W4 condition of beating regular. The native v5 policy is the v3 skeleton: range-aware movement and binary commit/escape with ±0.2 hysteresis; travel-time hold and commit focus are disabled. H/F/HF/v4 remain labelled variants. Dimensions remain 11/11/3; nearest is untuned. No experiment code was changed by this task.

CMA-ES 4.5.0, population 16, sigma .25 and 16 generations; 19 fixed common tuning clusters, both orientations. A starts at midpoints and selects novice melee mean S. B inherits A's tuning winners and ranks separately averaged ten novice/nine regular clusters by (novice mean ≥0 eligibility, regular mean S), with eligibility first and earlier exact ties retained. The same ordering feeds CMA adaptation and incumbent retention; validation never chooses knobs. Each completed arm/stage accounts for 9,766 tuning evaluations, including cache hits.

After all four arms validate, resonator novice mean must be strictly positive at both A and B. After all-arm B validation, resonator regular mean must be strictly greater than −7.62; equality stops. Novice tuning eligibility (≥0) and novice validation (>0) are separate predicates. S = own survivors − enemy survivors is the only score; guns, damage, timeouts and elimination times are descriptive.

Expected 4–6 hours, ten workers. Runner elapsed/awake monotonic time: **64.189 min**. Outer wall elapsed: **64.198 min**; outer awake: **64.197 min**; exit 0. The full 360-minute absolute monotonic allowance starts at runner entry. Projection checks, bounded submissions, clamped subprocess deadlines and child termination remain unchanged. Outer elapsed uses time.time; awake uses macOS time.monotonic/mach_absolute_time (excludes system sleep).

The readiness command launched immediately under /usr/bin/caffeinate -i -s at 23:07:10 local on 2026-10-06 into the new s4_v5_development_20261006_2308 directory. The owner explicitly superseded waits for C6 or low machine load. Existing output was refused and the unused declaration permanently claimed before combat. The earlier unlaunched attempt, reported by the owner as 20:35–23:05, remains unchanged in s4_v5_development_checks; waiting time is not v5 execution or charged to its allowance. LAUNCH.json, LOAD_SUMMARY.json and the local load log record shared-machine conditions honestly.

Implementation commit: `240aea2a2b57d53fc4403338c6f6ce5f5fe80889`. [run_identity.json](s4_v5_development_20261006_2308/run_identity.json) binds the admitted native binary/build, source pin, optimizer and 109 runtime hashes. All runtime identities still match at audit. Fresh development entropy and every orientation/cache/configuration use remain local and hash-bound. No judging-root entropy was used.

[Stored-record audit](s4_v5_development_20261006_2308_checks/AUDIT.json): **60,996 accounted rows**, 60,996 recorded fresh fights, 0 cache hits; 1,536 completed-generation candidates, 0 complete candidates from a partial generation, and 96 CMA generations reconstructed. Every raw row matches its ledger/configuration and declared allocation; complete tuning records reproduce incumbent retention and CMA ask/tell. All completed endpoint scores and descriptive end states reconstruct. Recorded controller-failure rows: 0; zero planner counters in recorded rows. Audit executed zero combat fights. On a worker/deadline failure, unreturned in-flight work is not added to recorded fight totals.


| Stage | Novice validation mean S | Novice >0 | Regular validation mean S | Regular >−7.62 | Runner gate |
| --- | --- | --- | --- | --- | --- |
| A | 5.5600 | True | — | None | CONTINUE |
| B | 5.6000 | True | -6.0250 | True | PROGRESS |


| Stage | Arm | Split | Recorded rows |
| --- | --- | --- | --- |
| A | morale | tuning | 9766 |
| A | morale | validation | 200 |
| A | nearest | validation | 200 |
| A | pushpull | tuning | 9766 |
| A | pushpull | validation | 200 |
| A | resonator | tuning | 9766 |
| A | resonator | validation | 200 |
| B | morale | tuning | 9766 |
| B | morale | validation | 400 |
| B | nearest | validation | 400 |
| B | pushpull | tuning | 9766 |
| B | pushpull | validation | 400 |
| B | resonator | tuning | 9766 |
| B | resonator | validation | 400 |

## Stage A validation

Two orientations are averaged within each of 100 independent seed clusters per endpoint. Intervals are descriptive normal 95% intervals (mean ±1.96 sample SD/√100). Guns/timeouts/damage describe 200 fights per endpoint. Team 0 is the controlled arm in both orientations; side swaps change geometry.

| Arm | Head | Mean S | SD | SE | 95% interval | Own / enemy guns | Timeouts / fights |
| --- | --- | --- | --- | --- | --- | --- | --- |
| resonator | novice | 5.5600 | 1.3527 | 0.1353 | [5.2949, 5.8251] | 0.0000 / 0.0000 | 0 / 200 |
| morale | novice | 1.3650 | 2.4276 | 0.2428 | [0.8892, 1.8408] | 0.0000 / 0.0000 | 0 / 200 |
| pushpull | novice | -2.1250 | 2.6821 | 0.2682 | [-2.6507, -1.5993] | 0.0000 / 0.0000 | 0 / 200 |
| nearest | novice | 0.8400 | 2.5115 | 0.2511 | [0.3478, 1.3322] | 0.0000 / 0.0000 | 0 / 200 |


| Arm | Head | Cross-team damage dealt / taken | Mean terminal s | Own eliminations; mean s | Enemy eliminations; mean s |
| --- | --- | --- | --- | --- | --- |
| resonator | novice | 2578.9650 / 2084.2350 | 78.5745 | 2; 94.1500 | 198; 78.4172 |
| morale | novice | 2516.3250 / 2374.9050 | 65.3407 | 63; 68.2206 | 137; 64.0163 |
| pushpull | novice | 2333.5200 / 2516.4450 | 58.6928 | 144; 56.9560 | 56; 63.1589 |
| nearest | novice | 2512.5150 / 2450.3700 | 64.7682 | 74; 65.3266 | 126; 64.4402 |

## Stage B validation

Two orientations are averaged within each of 100 independent seed clusters per endpoint. Intervals are descriptive normal 95% intervals (mean ±1.96 sample SD/√100). Guns/timeouts/damage describe 200 fights per endpoint. Team 0 is the controlled arm in both orientations; side swaps change geometry.

| Arm | Head | Mean S | SD | SE | 95% interval | Own / enemy guns | Timeouts / fights |
| --- | --- | --- | --- | --- | --- | --- | --- |
| resonator | novice | 5.6000 | 4.4142 | 0.4414 | [4.7348, 6.4652] | 4.7650 / 0.8100 | 0 / 200 |
| resonator | regular | -6.0250 | 2.4478 | 0.2448 | [-6.5048, -5.5452] | 1.2500 / 7.3000 | 89 / 200 |
| morale | novice | 19.7650 | 5.8008 | 0.5801 | [18.6281, 20.9019] | 6.4950 / 0.0600 | 0 / 200 |
| morale | regular | 9.5300 | 6.5156 | 0.6516 | [8.2529, 10.8071] | 6.8300 / 9.7000 | 198 / 200 |
| pushpull | novice | -6.6300 | 3.2315 | 0.3231 | [-7.2634, -5.9966] | 0.1550 / 6.4250 | 0 / 200 |
| pushpull | regular | -11.7200 | 2.6317 | 0.2632 | [-12.2358, -11.2042] | 0.0000 / 9.9950 | 0 / 200 |
| nearest | novice | -17.5200 | 3.9260 | 0.3926 | [-18.2895, -16.7505] | 0.0000 / 9.8750 | 0 / 200 |
| nearest | regular | -23.4550 | 6.2636 | 0.6264 | [-24.6827, -22.2273] | 0.0000 / 10.0000 | 0 / 200 |


| Arm | Head | Cross-team damage dealt / taken | Mean terminal s | Own eliminations; mean s | Enemy eliminations; mean s |
| --- | --- | --- | --- | --- | --- |
| resonator | novice | 5304.5300 / 6673.3000 | 53.9668 | 35; 52.6429 | 165; 54.2477 |
| resonator | regular | 4969.4100 / 7001.5950 | 124.0368 | 111; 103.1928 | 0; — |
| morale | novice | 6354.1050 / 5367.0850 | 46.2930 | 3; 50.2667 | 197; 46.2325 |
| morale | regular | 4890.8500 / 5162.9650 | 149.1107 | 2; 57.7667 | 0; — |
| pushpull | novice | 6140.5100 / 6736.1700 | 26.6173 | 187; 26.4376 | 13; 29.2026 |
| pushpull | regular | 4898.6900 / 6619.2900 | 41.3925 | 200; 41.3925 | 0; — |
| nearest | novice | 5145.1550 / 6910.7550 | 23.3528 | 200; 23.3528 | 0; — |
| nearest | regular | 4282.3200 / 6826.7300 | 28.6212 | 200; 28.6212 | 0; — |

A regular is not_run by design (novice melee only). A/B army composition also changes, so their difference does not isolate projectile observation. Damage is cross-team HP damage; friendly damage is excluded. Elimination times are conditional on actual elimination; timeouts are censored with no imputation. Both armies may be eliminated on the same terminal tick.

## Tuning selections and omega diagnostics

| Stage | Arm | Complete | Generations | Selected novice tuning mean | Selected regular tuning mean | B eligible | Accounted tuning rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | resonator | True | 16/16 | 5.7895 | — | None | 9766 |
| A | morale | True | 16/16 | 2.1053 | — | None | 9766 |
| A | pushpull | True | 16/16 | -0.7105 | — | None | 9766 |
| B | resonator | True | 16/16 | 7.6000 | -4.3333 | True | 9766 |
| B | morale | True | 16/16 | 18.1000 | 13.3333 | True | 9766 |
| B | pushpull | True | 16/16 | -6.2000 | -10.6111 | False | 9766 |


| Stage | Selected melee omega (rad/s) | Selected ranged omega (rad/s) |
| --- | --- | --- |
| A | 0.5428 | -1.9999 |
| B | -0.3583 | -1.9120 |

Latest retained role omega, including any partial stage: `{"melee": -0.35834082706003145, "ranged": -1.911951778821679}` rad/s. These are optimizer diagnostics only, with no matched zero-omega ablation or rotation-necessity inference. Stage A contains no ranged units, so its ranged omega is not identified by that tuning panel. No separate artillery omega is a tuned parameter in this policy. All selected knobs remain in the stage-best and local tuning files. Partial-stage values are not promoted to completed selections.

## Comparison with v3, v4 and section-16 cells

These are descriptive comparisons across fresh, unmatched development seed panels. Historical v3 B and v4 B used separately tuned knobs; section 16 used fixed historical v3 B knobs for all v3/H/F/HF cells. HF is the v4 skeleton at v3 knobs, not the independently retuned v4 package. Differences below are arithmetic differences, not paired estimates, causal attribution, statistical superiority or registered verdicts. The B gate uses the section-16 resonator v3 −7.620 baseline, not historical v3 B −7.570 or v3 C −1.655.

| Arm | Head | Reference | Reference mean S | v5 B mean S | v5 minus reference |
| --- | --- | --- | --- | --- | --- |
| resonator | novice | historical v3 B | 17.3500 | 5.6000 | -11.7500 |
| resonator | novice | historical v4 B | 9.3650 | 5.6000 | -3.7650 |
| resonator | novice | section 16 v3 | 18.1350 | 5.6000 | -12.5350 |
| resonator | novice | section 16 H | 7.8200 | 5.6000 | -2.2200 |
| resonator | novice | section 16 F | 11.4200 | 5.6000 | -5.8200 |
| resonator | novice | section 16 HF | -2.0550 | 5.6000 | 7.6550 |
| resonator | regular | historical v3 B | -7.5700 | -6.0250 | 1.5450 |
| resonator | regular | historical v4 B | -22.1750 | -6.0250 | 16.1500 |
| resonator | regular | section 16 v3 | -7.6200 | -6.0250 | 1.5950 |
| resonator | regular | section 16 H | -9.0150 | -6.0250 | 2.9900 |
| resonator | regular | section 16 F | -12.5850 | -6.0250 | 6.5600 |
| resonator | regular | section 16 HF | -35.3350 | -6.0250 | 29.3100 |
| morale | novice | historical v3 B | 24.6800 | 19.7650 | -4.9150 |
| morale | novice | historical v4 B | 17.2300 | 19.7650 | 2.5350 |
| morale | novice | section 16 v3 | 25.1350 | 19.7650 | -5.3700 |
| morale | novice | section 16 H | 25.8650 | 19.7650 | -6.1000 |
| morale | novice | section 16 F | 14.3850 | 19.7650 | 5.3800 |
| morale | novice | section 16 HF | 13.7600 | 19.7650 | 6.0050 |
| morale | regular | historical v3 B | 8.5500 | 9.5300 | 0.9800 |
| morale | regular | historical v4 B | -15.4050 | 9.5300 | 24.9350 |
| morale | regular | section 16 v3 | 10.1550 | 9.5300 | -0.6250 |
| morale | regular | section 16 H | 10.2000 | 9.5300 | -0.6700 |
| morale | regular | section 16 F | 1.2650 | 9.5300 | 8.2650 |
| morale | regular | section 16 HF | -0.1600 | 9.5300 | 9.6900 |
| pushpull | novice | historical v3 B | -7.2500 | -6.6300 | 0.6200 |
| pushpull | novice | historical v4 B | -18.5100 | -6.6300 | 11.8800 |
| pushpull | regular | historical v3 B | -12.2500 | -11.7200 | 0.5300 |
| pushpull | regular | historical v4 B | -7.2550 | -11.7200 | -4.4650 |
| nearest | novice | historical v3 B | -17.4050 | -17.5200 | -0.1150 |
| nearest | novice | historical v4 B | -17.5850 | -17.5200 | 0.0650 |
| nearest | regular | historical v3 B | -23.6450 | -23.4550 | 0.1900 |
| nearest | regular | historical v4 B | -22.6750 | -23.4550 | -0.7800 |

## Unrun work and delivery boundaries

Stage C and its doctrine/novice/regular endpoints are explicitly not_run: outside the amended v5 A/B scope, even if B reports PROGRESS. P2/P3, fresh margin/sample-size planning, judging and S5 are not_run. No milestone status was changed.

Decision traces, trajectory replays, movement reversal rates and feasibility distributions are not_run for v5: the reviewed readiness runner stores terminal fight records and performs no extra replay fights. Historical v4 and section-16 traces remain unchanged. Terminal records cannot reconstruct trajectories; no claim of improved movement stability is made.

[RAW_FILES_OUTSIDE_GIT.json](s4_v5_development_20261006_2308_checks/RAW_FILES_OUTSIDE_GIT.json) lists SHA256 and byte counts for local raw fight rows, seed declarations/uses, candidate and validation records, permanent claim, and logs. [AUDIT.json](s4_v5_development_20261006_2308_checks/AUDIT.json) carries seed-free summaries and endpoint coverage; local raw files are required for full reconstruction. Every committed payload file is below 50,000,000 bytes. [DELIVERY_NOTE.md](s4_v5_development_20261006_2308_checks/DELIVERY_NOTE.md) describes the normal-hook commit or verified bundle and its separate transport identity.

Owner recheck request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Owner recheck and disposition: COMPLETE — separate Codex reviewer v5_report_recheck returned APPROVE_WITH_NOTES, independently confirming stored results, comparisons, omegas and pins. Closure records reviewer identity, original/final report hashes and dispositions in [OWNER_RECHECK.md](s4_v5_development_20261006_2308_checks/OWNER_RECHECK.md) and docs/PLAN_CURRENT.md. The literal outer caffeinate invocation is now recorded in LAUNCH.json. Claude CLI returned Not logged in, so this is same-family review, not cross-family or scientific acceptance. Final hook/fresh-fetch identities are in the separate delivery transport record.

Shared-machine one-minute load was 8.30 at launch; 30-second samples ranged from 8.30 to 104.52, with sample mean 52.23. These are load averages, not CPU-utilization measurements; see [LOAD_SUMMARY.json](s4_v5_development_20261006_2308_checks/LOAD_SUMMARY.json).

No code/build/test input changed during the run. No test suite was repeated for this execution-only task; stored-data reconstruction and normal commit hooks validate this delivery.
