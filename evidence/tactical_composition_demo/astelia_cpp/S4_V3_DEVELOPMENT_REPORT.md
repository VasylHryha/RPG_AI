READY_FOR_S5

# S4 v3 development report

Implementer family: Codex (GPT-6). Exploratory development under decision 0028 items 16-18 and the owner’s explicit two-part request. Independent Claude review remains required; no self-acceptance is claimed.

**READY_FOR_S5 means completed development.** The final resonator regular-head mean S is −1.655, and the pooled resonator-minus-morale mean S is +0.460, below the proposed, unapproved δ = 3.5. These descriptive results do not establish tactical superiority or scientific acceptance.

**2026-10-06 recheck correction:** Claude's review is now present at `../astelia_cpp_review_claude/S4_V3_REVIEW.md` (APPROVE_WITH_NOTES). The owner's adversarial recheck is [S4_V3_RECHECK_REPORT.md](S4_V3_RECHECK_REPORT.md). Its two additional diagnostic captures reproduce recorded regular-validation orientations; they are separate diagnostic evidence, not additions to the 107,106 original executions or new validation clusters. Recorded results and receipts remain unchanged.

Section 14 replaces the out-ranged interpolation with per-own-unit/enemy binary commit/escape memory: initial commit for c >= 0, otherwise escape; switch only for c > +0.2 or c < -0.2, retaining the closed hysteresis band. Commit uses the effective artillery distance max(f_c R_i, 1.05 Rmin); escape uses R_e + w R_i. Mode memory survives movement truncation, is cloned independently and removed on either death. The kite band is unchanged. Section 13 retains threat-precise unanswered status at the producing tick, range-aware centre-distance movement, eight nearest plus threats capped deterministically at sixteen, and damage-weighted means. Gamma is fixed at 1; stateful dimensions are 11/11 and push-pull uses G/f_c/m_k (3). Q3 explicitly sets own artillery committed distance to max(f_c R_i, 1.05 Rmin), including the kite case. v0/v1/v2 remain selectable and byte-identical on their fixtures. The contract-stop report stays in history; the effective artillery lower bound was clarified at f983764.

Part 1 implementation commit: `cb9c9df2fb16c80501096078521d75361d10901e`. [v0/v1/v2 fixture parity and v3 contract checks](s4_v3_checks/PART1_PARITY.json); [affected tests](s4_v3_checks/tests.stdout.txt): **113 passed in 83.54 seconds**, with the two predecessor receipt-writing tests excluded. The new receipt verifies **408 byte-identical v0/v1/v2 fixture summaries**, plus 38 v3 engineering fixtures per stateful arm with maximum refinement 0.0020615 < 0.02. No historical receipt was rewritten. A copied trailing space was removed after the tests; Python AST identity was verified, so no behavioral change or test rerun was needed. Build time was 111.29 seconds.

[Amended protocol](S4_AMENDED_PROTOCOL.md), unchanged optimizer/budget: pycma 4.5.0 ask/tell; population 16; sigma 0.25; sixteen generations; 19 fixed common tuning clusters per candidate; 9,766 fight evaluations per tuned arm/stage including cache hits. A starts at midpoints, B/C at the preceding tuning-selected best. All objective values enter covariance adaptation; highest mean retains the earlier tie. Validation never selects knobs. Dimensions are 11/11/3 under Q1, nearest untuned. B tuning uses ten novice/nine regular clusters; validation uses 100 per level.

[Fresh development seed declaration](S4_V3_SEEDS.json) and [all candidate/generation/orientation/cache uses](s4_v3_development/s4_seeds.json). Independent development bases 710000000/711000000/712000000, validation +100000, final C heads +101000; these were declared before fights and do not derive from the judging root. No judging-root contents were read by the harness. Source/build/cache/pycma inputs are pinned in [run identity](s4_v3_development/run_identity.json).

Expected duration was logged before the first evaluation: 150–240 minutes with ten workers if all stages run; measured 167.62 minutes. The amended combined-time accounting retains 34.48 prior minutes and the 360-minute cap (325.52-minute allowance), authorized and logged as a pre-v3-fight resource change because v2 Stage C hit the projection cap. Every generation checks the conservative remaining-work projection; every evaluation checks the deadline.

The deadline check is at evaluation **launch**, not within its queued fight tasks; replay launch is also checked. Consequently the historical harness does not enforce a strict interruption deadline during validation or pool shutdown. The measured original execution ended well inside the allowance, so there was no observed cap violation. The combined 202.13 minutes means v3 plus the protocol's retained original 34.48 minutes; it excludes the intervening amended/v1/v2 executions. It is not cumulative development cost or summed CPU-minutes. A future resource-capped runner must bound task submission and subprocess timeouts by the remaining allowance before it is used again. The pinned historical runner is retained unchanged.

[Reconstruction audit](s4_v3_development/AUDIT.json): 107,094 accounted fights, 107,094 fresh and 0 cache hits, plus 12 captures; 2304 evaluated CMA candidates. Zero controller failures; all C metrics have zero forks, search calls and artillery rollouts. Both orientations, raw scores, budgets, retention and CMA ask/tell were reconstructed. Total native executions including captures: **107,106**. The runner measured 167.62 minutes; the outer execution wrapper measured 167.65 minutes including ledger close, giving 202.13 combined minutes with the retained 34.48 prior minutes. [Execution timing](s4_v3_checks/EXECUTION.json) and [audit timing](s4_v3_checks/REPORT_TIMING.json) are retained; reconstruction executed no fights or tests.

| Stage | Resonator evaluations | Morale evaluations | Push-pull evaluations | Validation |
|---|---:|---:|---:|---|
| A | 9,766 | 9,766 | 9,766 | complete, all four arms |
| B | 9,766 | 9,766 | 9,766 | complete, all four arms |
| C | 9,766 | 9,766 | 9,766 | complete, all four arms |

| Stage | Resonator novice mean S | Novice stop gate |
|---|---:|---|
| A | 5.7400 | pass |
| B | 17.3500 | pass |
| C | 8.0700 | descriptive; amended stop gates are A/B |

Validation is cluster-averaged across both orientations. Intervals below are descriptive normal 95% intervals, with no registered scientific verdict. For the pooled doctrine result, SE/interval use shared-seed blocks to retain cross-doctrine covariance. A removes projectile observation asymmetry; B/C restore full armies. Army composition also changes, so A/B differences cannot be attributed solely to projectile visibility.

## Stage A validation

| Arm | Endpoint | Mean S | SD | SE | Descriptive 95% interval | Timeouts / fights | Mean enemy artillery alive |
|---|---|---:|---:|---:|---|---|---:|
| resonator | s4_melee10 / novice | 5.7400 | 1.4538 | 0.1454 | [5.4551, 6.0249] | 0 / 200 | 0.0000 |
| morale | s4_melee10 / novice | 3.2100 | 1.3280 | 0.1328 | [2.9497, 3.4703] | 56 / 200 | 0.0000 |
| pushpull | s4_melee10 / novice | -2.1200 | 2.4935 | 0.2494 | [-2.6087, -1.6313] | 0 / 200 | 0.0000 |
| nearest | s4_melee10 / novice | 1.3650 | 2.1531 | 0.2153 | [0.9430, 1.7870] | 0 / 200 | 0.0000 |

Regular head-to-head is not_run in A: the declared stage is novice melee-only. All artillery counts are zero by army construction.

| Arm | Selected tuning mean S | Cluster SD | Stage evaluations |
|---|---:|---:|---:|
| resonator | 6.1053 | 1.7526 | 9,766 |
| morale | 3.8421 | 1.5639 | 9,766 |
| pushpull | -1.2105 | 2.4626 | 9,766 |

## Stage B validation

| Arm | Endpoint | Mean S | SD | SE | Descriptive 95% interval | Timeouts / fights | Mean enemy artillery alive |
|---|---|---:|---:|---:|---|---|---:|
| resonator | s4_full_head / novice | 17.3500 | 5.8833 | 0.5883 | [16.1969, 18.5031] | 0 / 200 | 0.0250 |
| resonator | s4_full_head / regular | -7.5700 | 1.6018 | 0.1602 | [-7.8840, -7.2560] | 23 / 200 | 8.0700 |
| morale | s4_full_head / novice | 24.6800 | 8.1298 | 0.8130 | [23.0866, 26.2734] | 0 / 200 | 0.0300 |
| morale | s4_full_head / regular | 8.5500 | 6.8437 | 0.6844 | [7.2086, 9.8914] | 191 / 200 | 8.9600 |
| pushpull | s4_full_head / novice | -7.2500 | 2.4531 | 0.2453 | [-7.7308, -6.7692] | 0 / 200 | 6.9000 |
| pushpull | s4_full_head / regular | -12.2500 | 2.8538 | 0.2854 | [-12.8093, -11.6907] | 0 / 200 | 9.9950 |
| nearest | s4_full_head / novice | -17.4050 | 3.6829 | 0.3683 | [-18.1269, -16.6831] | 0 / 200 | 9.8900 |
| nearest | s4_full_head / regular | -23.6450 | 6.9418 | 0.6942 | [-25.0056, -22.2844] | 0 / 200 | 10.0000 |

| Arm | Selected tuning mean S | Cluster SD | Stage evaluations |
|---|---:|---:|---:|
| resonator | 7.3421 | 14.2936 | 9,766 |
| morale | 18.1053 | 13.7463 | 9,766 |
| pushpull | -8.2895 | 4.2502 | 9,766 |

## Stage C validation

| Arm | Endpoint | Mean S | SD | SE | Descriptive 95% interval | Timeouts / fights | Mean enemy artillery alive |
|---|---|---:|---:|---:|---|---|---:|
| resonator | s4_p23 / line | 8.1900 | 3.3783 | 0.3378 | [7.5278, 8.8522] | 145 / 200 | 6.7650 |
| resonator | s4_p23 / wide line | 5.1950 | 4.1699 | 0.4170 | [4.3777, 6.0123] | 176 / 200 | 6.7550 |
| resonator | s4_p23 / wedge | 10.3450 | 2.9273 | 0.2927 | [9.7712, 10.9188] | 92 / 200 | 4.2250 |
| resonator | s4_p23 / box | 11.8700 | 3.7656 | 0.3766 | [11.1319, 12.6081] | 89 / 200 | 3.5400 |
| resonator | s4_p23 / column | 19.7150 | 2.1582 | 0.2158 | [19.2920, 20.1380] | 100 / 200 | 5.0000 |
| resonator | s4_p23 / loose | 20.0950 | 2.5758 | 0.2576 | [19.5901, 20.5999] | 200 / 200 | 9.8400 |
| resonator | s4_p23 / screen | 0.5500 | 4.3961 | 0.4396 | [-0.3116, 1.4116] | 29 / 200 | 2.5100 |
| resonator | s4_p23 / crescent | 8.2850 | 3.4962 | 0.3496 | [7.5997, 8.9703] | 126 / 200 | 6.1700 |
| resonator | s4_p23 / ring | 33.3100 | 4.7836 | 0.4784 | [32.3724, 34.2476] | 80 / 200 | 1.9700 |
| resonator | s4_p23 / wedge hold | 8.3800 | 6.5305 | 0.6530 | [7.1000, 9.6600] | 126 / 200 | 5.1550 |
| resonator | s4_p23 / line anvil | 7.9450 | 3.4778 | 0.3478 | [7.2633, 8.6267] | 136 / 200 | 7.9500 |
| resonator | s4_p23 / wedge flank | 11.1900 | 3.3475 | 0.3348 | [10.5339, 11.8461] | 101 / 200 | 4.8850 |
| resonator | s4_p23 / loose free | 17.3150 | 4.0518 | 0.4052 | [16.5208, 18.1092] | 200 / 200 | 9.7950 |
| resonator | s4_p23 / swarm | 25.1850 | 1.3974 | 0.1397 | [24.9111, 25.4589] | 200 / 200 | 10.0000 |
| resonator | s4_p23 / loose skirmish | 15.9600 | 3.6720 | 0.3672 | [15.2403, 16.6797] | 200 / 200 | 9.6600 |
| resonator | s4_p23 / loose berserk | 20.7650 | 2.8351 | 0.2835 | [20.2093, 21.3207] | 200 / 200 | 9.8750 |
| resonator | s4_p23 / storm | 4.7400 | 3.0554 | 0.3055 | [4.1411, 5.3389] | 181 / 200 | 7.6000 |
| resonator | s4_p23 / wolfpack | 17.6650 | 4.3444 | 0.4344 | [16.8135, 18.5165] | 200 / 200 | 9.8100 |
| resonator | s4_p23 / alone | -10.0850 | 2.1824 | 0.2182 | [-10.5128, -9.6572] | 0 / 200 | 8.9550 |
| resonator | s4_full_head / novice | 8.0700 | 3.1286 | 0.3129 | [7.4568, 8.6832] | 0 / 200 | 0.0950 |
| resonator | s4_full_head / regular | -1.6550 | 4.2018 | 0.4202 | [-2.4786, -0.8314] | 21 / 200 | 3.6100 |
| resonator | nineteen-doctrine pool | 12.4534 | 10.0934 | 0.0965 (block) | [12.2643, 12.6426] (block) | 2581 / 3800 | 6.8663 |
| morale | s4_p23 / line | 12.1250 | 6.0258 | 0.6026 | [10.9439, 13.3061] | 199 / 200 | 9.7150 |
| morale | s4_p23 / wide line | 10.7850 | 7.2514 | 0.7251 | [9.3637, 12.2063] | 200 / 200 | 10.0000 |
| morale | s4_p23 / wedge | 9.4650 | 7.7408 | 0.7741 | [7.9478, 10.9822] | 171 / 200 | 9.1400 |
| morale | s4_p23 / box | 17.3250 | 7.8818 | 0.7882 | [15.7802, 18.8698] | 175 / 200 | 9.7350 |
| morale | s4_p23 / column | 15.1100 | 6.7313 | 0.6731 | [13.7907, 16.4293] | 179 / 200 | 9.3000 |
| morale | s4_p23 / loose | 17.6650 | 4.2546 | 0.4255 | [16.8311, 18.4989] | 200 / 200 | 9.9050 |
| morale | s4_p23 / screen | 18.1300 | 6.5082 | 0.6508 | [16.8544, 19.4056] | 189 / 200 | 9.8450 |
| morale | s4_p23 / crescent | 15.5350 | 6.6375 | 0.6638 | [14.2340, 16.8360] | 198 / 200 | 9.6250 |
| morale | s4_p23 / ring | 6.2900 | 8.6209 | 0.8621 | [4.6003, 7.9797] | 186 / 200 | 6.9900 |
| morale | s4_p23 / wedge hold | 5.0250 | 8.0492 | 0.8049 | [3.4474, 6.6026] | 177 / 200 | 8.7750 |
| morale | s4_p23 / line anvil | 15.0600 | 5.3989 | 0.5399 | [14.0018, 16.1182] | 200 / 200 | 9.8500 |
| morale | s4_p23 / wedge flank | 12.7350 | 6.9408 | 0.6941 | [11.3746, 14.0954] | 183 / 200 | 9.7000 |
| morale | s4_p23 / loose free | 20.6150 | 4.7252 | 0.4725 | [19.6889, 21.5411] | 199 / 200 | 9.8850 |
| morale | s4_p23 / swarm | 24.7300 | 1.2399 | 0.1240 | [24.4870, 24.9730] | 200 / 200 | 10.0000 |
| morale | s4_p23 / loose skirmish | 10.1000 | 10.4105 | 1.0411 | [8.0595, 12.1405] | 178 / 200 | 9.3550 |
| morale | s4_p23 / loose berserk | 16.3450 | 6.2634 | 0.6263 | [15.1174, 17.5726] | 199 / 200 | 9.8050 |
| morale | s4_p23 / storm | 18.8900 | 5.7122 | 0.5712 | [17.7704, 20.0096] | 199 / 200 | 9.8000 |
| morale | s4_p23 / wolfpack | 4.4000 | 13.2667 | 1.3267 | [1.7997, 7.0003] | 159 / 200 | 9.5900 |
| morale | s4_p23 / alone | -22.4550 | 3.0311 | 0.3031 | [-23.0491, -21.8609] | 0 / 200 | 9.9250 |
| morale | s4_full_head / novice | 8.5450 | 10.9931 | 1.0993 | [6.3903, 10.6997] | 0 / 200 | 1.9900 |
| morale | s4_full_head / regular | 4.9950 | 7.8947 | 0.7895 | [3.4476, 6.5424] | 181 / 200 | 9.4450 |
| morale | nineteen-doctrine pool | 11.9934 | 11.9839 | 0.1688 (block) | [11.6625, 12.3243] (block) | 3391 / 3800 | 9.5232 |
| pushpull | s4_p23 / line | -13.8950 | 1.8509 | 0.1851 | [-14.2578, -13.5322] | 0 / 200 | 9.8450 |
| pushpull | s4_p23 / wide line | -13.7400 | 1.9482 | 0.1948 | [-14.1218, -13.3582] | 0 / 200 | 9.7100 |
| pushpull | s4_p23 / wedge | -13.6300 | 1.2342 | 0.1234 | [-13.8719, -13.3881] | 0 / 200 | 9.9750 |
| pushpull | s4_p23 / box | -13.5950 | 1.3553 | 0.1355 | [-13.8606, -13.3294] | 0 / 200 | 9.9800 |
| pushpull | s4_p23 / column | -9.7850 | 1.0231 | 0.1023 | [-9.9855, -9.5845] | 0 / 200 | 7.5000 |
| pushpull | s4_p23 / loose | -11.9900 | 1.1009 | 0.1101 | [-12.2058, -11.7742] | 0 / 200 | 8.5000 |
| pushpull | s4_p23 / screen | -14.7550 | 1.6073 | 0.1607 | [-15.0700, -14.4400] | 0 / 200 | 10.0000 |
| pushpull | s4_p23 / crescent | -12.1750 | 1.1132 | 0.1113 | [-12.3932, -11.9568] | 0 / 200 | 9.6150 |
| pushpull | s4_p23 / ring | -19.2700 | 3.6205 | 0.3621 | [-19.9796, -18.5604] | 0 / 200 | 3.8750 |
| pushpull | s4_p23 / wedge hold | -13.8650 | 1.2966 | 0.1297 | [-14.1191, -13.6109] | 0 / 200 | 9.9850 |
| pushpull | s4_p23 / line anvil | -14.7700 | 2.7028 | 0.2703 | [-15.2997, -14.2403] | 0 / 200 | 9.9650 |
| pushpull | s4_p23 / wedge flank | -13.6000 | 1.3390 | 0.1339 | [-13.8624, -13.3376] | 0 / 200 | 9.9950 |
| pushpull | s4_p23 / loose free | -9.9350 | 1.0509 | 0.1051 | [-10.1410, -9.7290] | 0 / 200 | 7.4850 |
| pushpull | s4_p23 / swarm | -8.2200 | 0.9778 | 0.0978 | [-8.4117, -8.0283] | 0 / 200 | 6.7150 |
| pushpull | s4_p23 / loose skirmish | -11.2850 | 1.1038 | 0.1104 | [-11.5014, -11.0686] | 0 / 200 | 8.1500 |
| pushpull | s4_p23 / loose berserk | -11.6600 | 1.1098 | 0.1110 | [-11.8775, -11.4425] | 0 / 200 | 8.9050 |
| pushpull | s4_p23 / storm | -13.1250 | 1.1772 | 0.1177 | [-13.3557, -12.8943] | 0 / 200 | 9.7200 |
| pushpull | s4_p23 / wolfpack | -10.3700 | 0.9146 | 0.0915 | [-10.5493, -10.1907] | 0 / 200 | 7.9950 |
| pushpull | s4_p23 / alone | -29.3650 | 1.9499 | 0.1950 | [-29.7472, -28.9828] | 0 / 200 | 9.9950 |
| pushpull | s4_full_head / novice | -6.7400 | 2.7418 | 0.2742 | [-7.2774, -6.2026] | 0 / 200 | 6.5700 |
| pushpull | s4_full_head / regular | -12.3850 | 3.0041 | 0.3004 | [-12.9738, -11.7962] | 0 / 200 | 9.9950 |
| pushpull | nineteen-doctrine pool | -13.6332 | 4.6773 | 0.0391 (block) | [-13.7098, -13.5565] (block) | 0 / 3800 | 8.8374 |
| nearest | s4_p23 / line | -22.8500 | 6.3614 | 0.6361 | [-24.0968, -21.6032] | 0 / 200 | 9.9900 |
| nearest | s4_p23 / wide line | -23.6350 | 5.4388 | 0.5439 | [-24.7010, -22.5690] | 0 / 200 | 9.9600 |
| nearest | s4_p23 / wedge | -19.2200 | 1.4639 | 0.1464 | [-19.5069, -18.9331] | 0 / 200 | 10.0000 |
| nearest | s4_p23 / box | -19.6600 | 1.5273 | 0.1527 | [-19.9594, -19.3606] | 0 / 200 | 10.0000 |
| nearest | s4_p23 / column | -17.5800 | 1.4834 | 0.1483 | [-17.8708, -17.2892] | 0 / 200 | 9.9950 |
| nearest | s4_p23 / loose | -22.8800 | 4.7509 | 0.4751 | [-23.8112, -21.9488] | 0 / 200 | 9.2050 |
| nearest | s4_p23 / screen | -23.4100 | 1.9891 | 0.1989 | [-23.7999, -23.0201] | 0 / 200 | 10.0000 |
| nearest | s4_p23 / crescent | -13.3350 | 2.4762 | 0.2476 | [-13.8203, -12.8497] | 0 / 200 | 9.9750 |
| nearest | s4_p23 / ring | -38.3000 | 3.3552 | 0.3355 | [-38.9576, -37.6424] | 0 / 200 | 9.6050 |
| nearest | s4_p23 / wedge hold | -18.8600 | 1.3597 | 0.1360 | [-19.1265, -18.5935] | 0 / 200 | 10.0000 |
| nearest | s4_p23 / line anvil | -17.6100 | 4.7977 | 0.4798 | [-18.5504, -16.6696] | 0 / 200 | 9.9950 |
| nearest | s4_p23 / wedge flank | -18.9650 | 1.7469 | 0.1747 | [-19.3074, -18.6226] | 0 / 200 | 10.0000 |
| nearest | s4_p23 / loose free | -10.4950 | 1.5723 | 0.1572 | [-10.8032, -10.1868] | 0 / 200 | 8.3000 |
| nearest | s4_p23 / swarm | -7.3600 | 1.9721 | 0.1972 | [-7.7465, -6.9735] | 0 / 200 | 6.5000 |
| nearest | s4_p23 / loose skirmish | -12.5850 | 1.9772 | 0.1977 | [-12.9725, -12.1975] | 0 / 200 | 9.1850 |
| nearest | s4_p23 / loose berserk | -24.7950 | 3.1695 | 0.3170 | [-25.4162, -24.1738] | 0 / 200 | 9.4300 |
| nearest | s4_p23 / storm | -17.4350 | 3.5238 | 0.3524 | [-18.1257, -16.7443] | 0 / 200 | 9.9550 |
| nearest | s4_p23 / wolfpack | -12.8800 | 2.4496 | 0.2450 | [-13.3601, -12.3999] | 0 / 200 | 9.5300 |
| nearest | s4_p23 / alone | -40.4450 | 1.0869 | 0.1087 | [-40.6580, -40.2320] | 0 / 200 | 10.0000 |
| nearest | s4_full_head / novice | -17.2150 | 4.0077 | 0.4008 | [-18.0005, -16.4295] | 0 / 200 | 9.9150 |
| nearest | s4_full_head / regular | -23.4100 | 6.8178 | 0.6818 | [-24.7463, -22.0737] | 0 / 200 | 10.0000 |
| nearest | nineteen-doctrine pool | -20.1211 | 8.6622 | 0.0773 (block) | [-20.2725, -19.9696] (block) | 0 / 3800 | 9.5592 |

| Arm | Selected tuning mean S | Cluster SD | Stage evaluations |
|---|---:|---:|---:|
| resonator | 12.1842 | 10.2811 | 9,766 |
| morale | 15.4474 | 11.3111 | 9,766 |
| pushpull | -12.5789 | 4.1408 | 9,766 |

## Margin and sample-size planning

Proposed δ = 3.5 survivors, from one quarter the maximum pooled paired validation SD, rounded upward to 0.5 with minimum 1. Owner approval is required; the margin was not reduced to obtain a pass.

Noise planning uses 2,000 bootstrap resamples (seed 811005), 95th-percentile upper SD from both selected tuning and validation; C shared-seed blocks retain cross-doctrine covariance. Alpha .0025 one-sided, power .90; floors 32/head and 16/doctrine. P1 hypothetically targets δ above zero; P2/P3 target 2δ above margin δ. These are beneficial-effect planning assumptions, not observed effect claims.

| Endpoint | Paired mean | Config-cluster SD | Seed-block SD | Block SE | Block 95% interval | Upper SD pooled / block / tuning |
|---|---:|---:|---:|---:|---|---|
| P2 | 0.4600 | 12.7163 | 1.8399 | 0.1840 | [0.0994, 0.8206] | 13.1067 / 2.0067 / 13.1528 |
| P3 | 26.0866 | 8.9207 | 1.0854 | 0.1085 | [25.8738, 26.2993] | 9.2824 / 1.2021 / 11.4570 |

P2/P3 use maximum validation block upper variance, tuning pooled upper variance/19, and independent-stratum floor. P1 uses larger B-selected tuning/C validation upper SD and common n for both levels. B tuning has earlier knobs and ten/nine clusters; it is exploratory noise allowance. [Full calculations and both splits](s4_v3_development/POWER_PLANNING.json).

These n values are known-variance normal approximations at hypothetical beneficial effects. They do not guarantee 90% power for a finite-sample t or bootstrap judging procedure, particularly with 16 independent seed blocks. Dividing tuning pooled variance by 19 assumes independent doctrine contributions for that allowance; the validation block term retains the measured covariance, but does not bound unseen future covariance. S5 must specify the inference procedure and check its calibration before treating these counts as a power guarantee. Bootstrap resampling of selected spreads does not undo tuning selection or validate the proposed effect sizes.

| Endpoint | Proposed n | Total configuration clusters | Within 2,000? |
|---|---|---:|---|
| P1 | 99 per head | 198 | yes |
| P2 | 16 per doctrine / shared seed blocks | 304 | yes |
| P3 | 16 per doctrine / shared seed blocks | 304 | yes |

## Viewer exports

| Arm | Stage A | Stage B | Stage C |
|---|---|---|---|
| resonator | [Replay](s4_v3_development/replays/A_resonator.html) | [Replay](s4_v3_development/replays/B_resonator.html) | [Replay](s4_v3_development/replays/C_resonator.html) |
| morale | [Replay](s4_v3_development/replays/A_morale.html) | [Replay](s4_v3_development/replays/B_morale.html) | [Replay](s4_v3_development/replays/C_morale.html) |
| pushpull | [Replay](s4_v3_development/replays/A_pushpull.html) | [Replay](s4_v3_development/replays/B_pushpull.html) | [Replay](s4_v3_development/replays/C_pushpull.html) |
| nearest | [Replay](s4_v3_development/replays/A_nearest.html) | [Replay](s4_v3_development/replays/B_nearest.html) | [Replay](s4_v3_development/replays/C_nearest.html) |

## End-state diagnostics and remaining gate

Enemy artillery is counted directly from living occupied enemy artillery at fight end. Validation means and counts per arm/setting are retained in VALIDATION_END_STATES.json; END_STATES_BY_SPLIT.json additionally covers every executed tuning setting, with reused-seed tuning diagnostics kept separate. Timeout means reaching the 150-second duration; it remains an ordinary scored fight. Every endpoint above has 100 clusters / 200 fights; the doctrine pool has 1,900 configuration clusters with 100 independent shared-seed blocks. Counts are descriptive and do not change the survivor-first objective.

Selected knobs per stage are in A_best.json, B_best.json and C_best.json where executed. [Raw fight log](s4_v3_development/fights.jsonl.gz), candidate logs, all validation scores and matching replay captures are retained. HTML replays are generated artifacts; no browser qualification is claimed for this run.

No outcome-informed equation changes during the v3 run, tuning restarts, budget extensions during execution, judging-seed use, S5 registration, recorded run, SPEC_0G.json edits, frozen GeoMind edits, committed receipt edits or milestone status changes occurred. The authorized outcome-informed v3 equation change and 360-minute resource amendment preceded every v3 fight. No tactical superiority, equivalence, RRG recursion or C4/C5 qualification is inferred from development readiness. Claude's independent development review is complete with notes; δ and a fresh S5 specification remain owner decisions.

The binary law constrains each out-ranged pair's preferred distance. It does not ensure that the summed enemy and ally motion leaves the kill zone. Nor do the separately tuned comparisons identify the skeleton as the main causal source of performance, or isolate the circular state: the arms differ in pressure processing, state law, threat weighting and retreat capability as well as selected knobs. Those causal claims require fresh matched ablations in a later revision; the present comparisons measure the declared controller packages under common world conditions and evaluation budgets.

Delivery: shared `.git` is read-only. Part 1 and the completed development evidence are committed in an isolated temporary clone with repository hooks enabled. See [delivery note](s4_v3_checks/DELIVERY_NOTE.md) and the verified `s4_v3_checks/commits.bundle`. The workspace already contains the delivered files; unrelated growing_shapes and C6 work remains outside this delivery.
