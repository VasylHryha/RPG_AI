DONE

Section-16 fixed-v3-knob hold × focus attribution, development only. Exactly **3,200 fights and 80 predeclared trace captures** completed once; native exit 0, zero controller failures, cache hits or planner work. S = own survivors − enemy survivors. This completion label is not scientific acceptance, judging, registration, a superiority verdict or authorization for v5/S5.

The regression has two different explanations in these arms. Against regular, **morale mainly loses score because of focus**: focus alone costs 8.890 S, hold alone changes S by +0.045, and HF costs 10.315 S. For **resonator, the hold–focus combination is the dominant failure**: hold alone costs 1.395 S and focus alone 4.965 S, while HF costs 27.715 S. The remaining 21.355 S loss is the negative interaction. The trace subset supports the mechanism: holds can leave a committed pair selecting focus while the unit’s latent state requests escape. That conflict appears in HF, not F.

Execution: readiness command, ten workers, `/usr/bin/caffeinate -i -s`, new `s4_attribution_development/` folder. Started 2026-10-06T15:58:47.846006+00:00, finished 2026-10-06T16:14:31.263580+00:00. Elapsed **943.418 s (15.724 min)**; awake **943.459 s (15.724 min)**. Wall time uses `time.time`; awake time uses macOS `time.monotonic`/mach_absolute_time. Their 0.042 s difference is clock measurement variation; neither approaches the 3,600 s cap. C6’s completion report was checked before launch. This task edited no code during the run, no rebuild or extra replay fight was launched, and the ledger was atomically claimed before fights. All cells used unchanged v3 stage-B `B_best.json` (SHA256 `e80bc2404fa8d90fd46eaf9e7b38042d399d3fb40a06df245b6087890cd83730`).

Statistics use **100 independent seed clusters per arm/head**. The two orientation scores are averaged within each seed. Every interval is the descriptive normal interval mean ± 1.96 × sample SD / √100, not a hypothesis verdict. All contrasts and the interaction are calculated within the same seed before averaging; intervals are not subtracted from one another. Gun means and timeout counts are over 200 fights/cell. Team 0 is the controlled arm in both orientations; swapping sides mirrors geometry, not team identity.

| Arm | Head | Cell | Mean S [descriptive 95% interval] | Own guns alive/fight | Enemy guns alive/fight | Timeouts/200 |
|---|---|---|---|---:|---:|---:|
| resonator | novice | v3 | +18.135 [+17.182, +19.088] | 8.940 | 0.000 | 0 |
| resonator | novice | H | +7.820 [+6.453, +9.187] | 4.315 | 0.715 | 0 |
| resonator | novice | F | +11.420 [+10.162, +12.678] | 5.805 | 0.600 | 0 |
| resonator | novice | HF | -2.055 [-4.161, +0.051] | 2.660 | 3.485 | 0 |
| resonator | regular | v3 | -7.620 [-7.913, -7.327] | 0.220 | 8.025 | 17 |
| resonator | regular | H | -9.015 [-9.396, -8.634] | 0.060 | 8.575 | 17 |
| resonator | regular | F | -12.585 [-13.166, -12.004] | 0.000 | 9.975 | 0 |
| resonator | regular | HF | -35.335 [-35.859, -34.811] | 0.000 | 9.560 | 0 |
| morale | novice | v3 | +25.135 [+23.609, +26.661] | 8.740 | 0.020 | 0 |
| morale | novice | H | +25.865 [+24.410, +27.320] | 8.840 | 0.020 | 0 |
| morale | novice | F | +14.385 [+12.816, +15.954] | 7.920 | 0.030 | 0 |
| morale | novice | HF | +13.760 [+12.236, +15.284] | 7.880 | 0.045 | 0 |
| morale | regular | v3 | +10.155 [+8.929, +11.381] | 7.845 | 9.055 | 197 |
| morale | regular | H | +10.200 [+8.857, +11.543] | 7.780 | 8.895 | 196 |
| morale | regular | F | +1.265 [-0.050, +2.580] | 5.675 | 9.785 | 171 |
| morale | regular | HF | -0.160 [-1.477, +1.157] | 5.225 | 9.825 | 164 |

All six paired differences are included. Positive differences favor the first named cell. Interaction is HF − H − F + v3; a negative value means the combination loses more than the sum of the two isolated effects.

| Paired quantity | Resonator novice | Resonator regular | Morale novice | Morale regular |
|---|---|---|---|---|
| H-v3 | -10.315 [-11.977, -8.653] | -1.395 [-1.842, -0.948] | +0.730 [-0.457, +1.917] | +0.045 [-1.536, +1.626] |
| F-v3 | -6.715 [-8.129, -5.301] | -4.965 [-5.623, -4.307] | -10.750 [-12.910, -8.590] | -8.890 [-10.710, -7.070] |
| HF-v3 | -20.190 [-22.507, -17.873] | -27.715 [-28.287, -27.143] | -11.375 [-13.512, -9.238] | -10.315 [-12.201, -8.429] |
| F-H | +3.600 [+1.684, +5.516] | -3.570 [-4.262, -2.878] | -11.480 [-13.592, -9.368] | -8.935 [-10.772, -7.098] |
| HF-H | -9.875 [-12.443, -7.307] | -26.320 [-26.961, -25.679] | -12.105 [-14.214, -9.996] | -10.360 [-12.235, -8.485] |
| HF-F | -13.475 [-15.837, -11.113] | -22.750 [-23.507, -21.993] | -0.625 [-1.307, +0.057] | -1.425 [-2.930, +0.080] |
| interaction_HF-H-F+v3 | -3.160 [-5.969, -0.351] | -21.355 [-22.255, -20.455] | -1.355 [-2.754, +0.044] | -1.470 [-3.629, +0.689] |

Trace counters cover only the **five predeclared common regular seeds, both orientations: ten fights per arm/cell**. These captures replace ordinary execution inside the 3,200 fights. They are not 100 independent trace seeds. Raw counts depend on living-unit exposure; rates use each cell’s own living unit-minutes. The latent intent proxy initializes at c≥0 and switches at c>0.2/c<−0.2. Pair-mode changes and ticks with any pair change are separate measurements; none measures physical velocity reversals or a v5 policy intent.

| Arm | Cell | Living unit-minutes | Unit-intent proxy changes (per unit-min) | Pair-mode changes (per unit-min) | Unit ticks with any pair change |
|---|---|---:|---:|---:|---:|
| resonator | v3 | 477.533 | 15,884 (33.263) | 425,905 (891.886) | 15,884 |
| resonator | H | 363.131 | 12,107 (33.341) | 50,563 (139.242) | 3,430 |
| resonator | F | 400.182 | 13,201 (32.988) | 391,974 (979.490) | 13,201 |
| resonator | HF | 135.045 | 4,343 (32.160) | 28,637 (212.055) | 3,679 |
| morale | v3 | 708.677 | 457 (0.645) | 13,594 (19.182) | 457 |
| morale | H | 625.280 | 522 (0.835) | 13,257 (21.202) | 603 |
| morale | F | 472.178 | 362 (0.767) | 8,877 (18.800) | 362 |
| morale | HF | 361.292 | 351 (0.972) | 8,225 (22.766) | 472 |

| Arm | Cell | Own unit ticks | Focus ticks | Focus while latent proxy escapes | Focus with c<−0.2 | Expired holds | Expiries inside live gun legal reach |
|---|---|---:|---:|---:|---:|---:|---:|
| resonator | v3 | 859,559 | 0 | 0 | 0 | 0 | 0 |
| resonator | H | 653,635 | 0 | 0 | 0 | 31,948 | 3,932 |
| resonator | F | 720,327 | 356,060 | 0 | 0 | 0 | 0 |
| resonator | HF | 243,081 | 175,754 | 74,143 | 66,055 | 6,495 | 2,626 |
| morale | v3 | 1,275,619 | 0 | 0 | 0 | 0 | 0 |
| morale | H | 1,125,504 | 0 | 0 | 0 | 10,157 | 408 |
| morale | F | 849,920 | 199,538 | 0 | 0 | 0 | 0 |
| morale | HF | 650,325 | 199,647 | 1,453 | 1,380 | 5,547 | 266 |

Expiry exposure is prepare-position coincidence with **any living enemy artillery’s legal annulus**, inclusive minimum/maximum range and excluding the dead zone. It is not proof of a shot, damage, a mode flip or an unsafe movement caused by expiry. Focus while escaping is simultaneous focus and latent escape proxy; the stricter c<−0.2 column is also retained.

Hold releases below count **pair events, not unique dead units**. Own/enemy/both include prepare cleanup and terminal reconciliation. A death on the last tick may have no next prepare; it is reconciled from the final state. Missing-unit releases are separate and excluded from death totals. Living pairs still held at the end are censored.

| Arm | Cell | Holds started | Band releases | Death-released holds | Own-only | Enemy-only | Both | Missing | Death releases at terminal (subset) | Living holds censored |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| resonator | v3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| resonator | H | 50,563 | 4,898 | 13,711 | 9,458 | 4,242 | 11 | 0 | 79 | 6 |
| resonator | F | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| resonator | HF | 28,637 | 8,995 | 13,147 | 12,434 | 703 | 10 | 0 | 125 | 0 |
| morale | v3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| morale | H | 13,257 | 1,847 | 1,253 | 1,149 | 104 | 0 | 0 | 0 | 0 |
| morale | F | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| morale | HF | 8,225 | 1,650 | 1,028 | 1,003 | 25 | 0 | 0 | 42 | 0 |

Every trace balances starts = band releases + expiries + prepare disappearance releases + terminal releases + living censoring. Undefined feasibility samples remain in the exposure accounting, with each reason retained in [ANALYSIS.json](s4_attribution_checks/ANALYSIS.json) and original raw traces; a cosine mean covers defined samples only.

Against regular, HF resonator has **74,143 focus ticks while the latent proxy escapes**, including 66,055 with c<−0.2; these are 42.2% and 37.6% of its 175,754 focus ticks. F has zero such conflicts. Its gun survival and elimination outcomes also deteriorate: HF leaves 9.560 enemy guns/fight, eliminates the controlled army in all 200 fights, and reaches that loss after 27.128 s on average. F also loses every fight, but lasts 74.107 s on average; v3 has 17 timeouts and averages 103.298 s to termination. H greatly reduces pair changes but barely changes latent oscillation per living unit-minute. A held pair is therefore not a coherent held unit intent; adding focus allows a stale commit to dominate movement while the underlying state requests escape.

For morale, focus alone lowers S on both heads (−10.750 novice, −8.890 regular), whereas hold alone’s mean effects (+0.730 novice, +0.045 regular) have descriptive intervals spanning zero. The regular interaction interval also spans zero (−1.470 [−3.629, +0.689]); these data do not separate a modest interaction from descriptive sampling variation. The F regular score remains +1.265 and HF is −0.160, so "regression" means a score loss relative to v3, not that every cell necessarily loses on mean S. Regular F/HF retain roughly 9.8 enemy guns while own guns fall from 7.845 in v3 to 5.675/5.225. The historical focus rule discards other enemy movement terms when any committed out-ranged pair supplies focus, allowing pursuit without preserving all threat avoidance. Focus causes the main fixed-knob morale score loss; hold is a severe amplifier for resonator. Trace exposure and death counts support this reading without attributing individual damage or deaths to particular events.

Against novice, resonator H and F also lose score separately and HF is worse still; morale’s focus loss occurs with or without hold. These effects are specific to the unchanged v3 knobs on this fresh development ledger. HF is the historical v4 **skeleton at v3 knobs**, not the historically independently retuned v4 package. This test does not exactly decompose that old package regression, select or tune v5, or establish general superiority.

Damage and time accounting below retain S as the score. Damage is mean cross-team HP damage dealt/taken by the controlled arm (friendly damage excluded). Terminal time includes timeouts; the two elimination times are conditional means over fights where that army actually reaches zero survivors. "—" means no such elimination. Both armies can be eliminated in the same terminal tick; elimination counts are not mutually exclusive win/loss categories.

| Arm | Head | Cell | Damage dealt / taken | Mean terminal seconds | Own elimination fights; mean seconds | Enemy elimination fights; mean seconds |
|---|---|---|---:|---:|---|---|
| resonator | novice | v3 | 5170.260 / 5819.835 | 53.826 | 0; — | 200; 53.826 |
| resonator | novice | H | 5496.750 / 6500.245 | 52.767 | 34; 58.824 | 166; 51.527 |
| resonator | novice | F | 5608.700 / 6382.185 | 53.663 | 27; 58.590 | 174; 52.941 |
| resonator | novice | HF | 5496.520 / 6438.700 | 38.428 | 109; 36.817 | 92; 40.451 |
| resonator | regular | v3 | 4980.735 / 7107.990 | 103.298 | 183; 98.957 | 0; — |
| resonator | regular | H | 4581.545 / 7137.955 | 97.331 | 183; 92.435 | 0; — |
| resonator | regular | F | 4336.405 / 7023.420 | 74.107 | 200; 74.107 | 0; — |
| resonator | regular | HF | 2432.530 / 6663.190 | 27.128 | 200; 27.128 | 0; — |
| morale | novice | v3 | 5709.885 / 4983.985 | 40.343 | 2; 39.633 | 198; 40.351 |
| morale | novice | H | 5709.055 / 4881.475 | 40.154 | 2; 41.950 | 198; 40.136 |
| morale | novice | F | 6599.950 / 5341.490 | 37.281 | 2; 48.567 | 198; 37.167 |
| morale | novice | HF | 6595.080 / 5385.445 | 37.485 | 4; 41.642 | 196; 37.401 |
| morale | regular | v3 | 4386.710 / 5520.010 | 148.718 | 3; 62.333 | 0; — |
| morale | regular | H | 4449.550 / 5533.775 | 148.333 | 4; 65.000 | 0; — |
| morale | regular | F | 4902.955 / 5719.655 | 137.839 | 29; 65.937 | 0; — |
| morale | regular | HF | 4885.315 / 5848.555 | 134.456 | 36; 63.494 | 0; — |

Integrity and delivery: [VALIDATION.json](s4_attribution_checks/VALIDATION.json) independently reconstructs all S intervals, six paired contrasts and interactions from raw terminal rows, checks all 3,200 unique allocations/fixed knobs, reconciles hold-release conservation and verifies native/source/input/raw-file hashes. Trace counters were produced during the original fights and checked for allocation/conservation; the initial integrity check does not independently recount all raw ticks. [ANALYZE_STORED.py](s4_attribution_checks/ANALYZE_STORED.py) reproduces the seed-free analysis without executing combat. [RUN_RESULT.json](s4_attribution_checks/RUN_RESULT.json) retains command and clocks. Raw traces, fight rows, seed-bearing run identity/SUMMARY and logs remain local, outside Git: 2,664,866,943 bytes, each listed by SHA256 and size in [RAW_FILES_OUTSIDE_GIT.json](s4_attribution_checks/RAW_FILES_OUTSIDE_GIT.json). The predeclared seed ledger and every older receipt remain unchanged.

Owner recheck request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Owner recheck: **APPROVE_WITH_NOTES**, recorded in [OWNER_RECHECK.md](s4_attribution_checks/OWNER_RECHECK.md) and `docs/PLAN_CURRENT.md`. Claude CLI was attempted and returned "Not logged in"; the independent reviewer is Codex, a disclosed same-family fallback, not cross-family acceptance. It independently reconstructed every endpoint/contrast/interaction and checked all raw hashes, then recounted eight complete existing traces (the third predeclared trace seed, orientation false, both arms × all cells). All recounted counters matched exactly. This is eight of 80 full traces, not an independent tick recount of all 80 or a geometric rederivation of every gun-reach flag. Timing formatting was corrected; raw-log inventory/disclosure and bounded review coverage were completed. The commit’s file identities and separate bundle/fresh-fetch verification are recorded in the adjacent `S4_ATTRIBUTION_PART2.delivery.json`; [delivery note](s4_attribution_checks/DELIVERY_PART2_NOTE.md) explains the isolated Git directory and normal hooks.
