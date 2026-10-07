OBSERVED MATCH; OBSERVED OWNER CRITERION MET

Descriptive development validation. Generated exclusively from committed JSON; no fights, raw trace parsing, sealed render, or new allowance.

Sources: validation/analysis and stored recovery records at `e44b528`; tuning at `796d0a8`. The source documents remain unchanged.

`ANALYSIS.json` SHA256: `f3160cf72e240d2fbfd493b4ba801e79ea4680daac8a4d46a2d0952bdec6bb52`. `TUNING_ANALYSIS.json` SHA256: `1990d998a8d92964b48605a3bad629b72ad9c5f42d34eb9aae2a3196bc562d83`.

Tuning: 257 evaluations, 8224 fights, validation used: false; selected ordinal 161. Validation: 400 fights on 20 fresh clusters × two orientations × five arms × two heads.

| Knob at θ* | Value |
| --- | --- |
| K | 0.37170590833718886 |
| K_t | 3.65326053622193 |
| kappa | 38.800628149830196 |
| beta | 1.5151496229104617 |
| G | 3.457657402346487 |
| w | 1.8741404479412271 |
| f_c | 0.9896720150642289 |
| m_k | 0.3280745938729417 |
| lambda_th | 1.1066977151706074 |
| mu | -1.3995913367114279 |
| omega_ranged | 1.5775291057474368 |

## Arm results

A win requires enemy survivors = 0, own survivors ≥ 1 and termination before 150 s. S is own survivors minus enemy survivors. A timeout is a completed outcome, distinct from controller/numerical failure.

| Arm | Head | Wins / fights | Mean S | Mean own losses | Failures | Timeouts | Mean end time (s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v7 | regular | 32/40 | 4.675 | 42.325 | 0 | 1 | 47.519167 |
| v7 | novice | 40/40 | 26.450 | 23.550 | 0 | 0 | 26.045000 |
| forcedP16 | regular | 31/40 | 2.100 | 44.750 | 0 | 0 | 39.510833 |
| forcedP16 | novice | 40/40 | 21.650 | 28.350 | 0 | 0 | 26.426667 |
| forcedv6 | regular | 0/40 | 1.575 | 38.475 | 0 | 39 | 148.452500 |
| forcedv6 | novice | 0/40 | -7.075 | 50.000 | 0 | 0 | 53.169167 |
| omega0 | regular | 30/40 | 4.100 | 42.650 | 0 | 0 | 47.838333 |
| omega0 | novice | 40/40 | 25.850 | 24.150 | 0 | 0 | 25.535000 |
| historicalP16 | regular | 32/40 | 1.075 | 45.675 | 0 | 0 | 50.840000 |
| historicalP16 | novice | 40/40 | 22.425 | 27.575 | 0 | 0 | 27.055000 |

forcedP16 is the matched always-commit action map at θ*. forcedv6 is always escape at θ*. ω0 changes the inherited artillery/ranged natural rate to zero. Historical P16 uses θ_v6 and is a separately labelled descriptive witness. All arms share the same paired validation seeds.

## Declared readings

Net regular win difference v7 − forcedP16: +1/40. Comparator below floor: false. Positive / negative / tied regular clusters: 4 / 4 / 12.

The comparison uses the §20.2 count bands (improvement ≥ +4, match ±3, worse ≤ −4), conditional on forcedP16 ≥ 21/40. The owner criterion independently requires ≥ 21/40 on both heads, positive mean S on both heads and no failures.

Paired cluster-bootstrap win-rate difference: mean +0.025, 95% descriptive percentile interval [-0.125, +0.200]; 10000 resamples, seed 20261007, linear interpolation. Each resampled cluster retains both orientations.

| Regular orientation outcome (v7 / forcedP16) | Count |
| --- | --- |
| v7_1__forcedP16_1 | 27 |
| v7_1__forcedP16_0 | 5 |
| v7_0__forcedP16_0 | 4 |
| v7_0__forcedP16_1 | 4 |

## Paired clusters

Each entry gives wins across the two orientations; Δ is v7 − forcedP16. Cluster indices are zero based. Mean S is the mean of the two orientations.

### regular

| Cluster | v7 | forcedP16 | forcedv6 | omega0 | historicalP16 | Δ wins | Mean S (arm order above) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 11.000, 6.000, 0.500, 10.500, 5.000 |
| 1 | 2 (1/1) | 1 (1/0) | 0 (0/0) | 2 (1/1) | 0 (0/0) | 1 | 13.500, -7.500, 1.000, 13.000, -20.000 |
| 2 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 8.500, 8.500, 4.500, 11.000, 5.000 |
| 3 | 1 (0/1) | 1 (0/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | -3.000, 0.000, 3.500, 6.500, 7.000 |
| 4 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 1 (1/0) | 1 (1/0) | 0 | 5.000, 4.500, 1.000, -5.500, -7.000 |
| 5 | 1 (0/1) | 2 (1/1) | 0 (0/0) | 1 (0/1) | 2 (1/1) | -1 | -5.500, 5.000, -5.000, -3.500, 5.500 |
| 6 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 7.500, 7.500, 4.000, 8.500, 9.000 |
| 7 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 10.000, 9.000, -0.500, 11.500, 7.000 |
| 8 | 2 (1/1) | 0 (0/0) | 0 (0/0) | 1 (0/1) | 2 (1/1) | 2 | 5.500, -13.000, 3.500, 1.000, 5.500 |
| 9 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 1 (0/1) | 2 (1/1) | 0 | 11.500, 9.000, 3.500, 2.000, 4.500 |
| 10 | 2 (1/1) | 1 (0/1) | 0 (0/0) | 1 (0/1) | 1 (1/0) | 1 | 8.000, -8.000, 7.000, 0.000, -9.500 |
| 11 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 1 (1/0) | 0 | 12.500, 7.500, 5.000, 11.500, -10.000 |
| 12 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 12.500, 6.500, -0.500, 10.500, 3.000 |
| 13 | 2 (1/1) | 1 (0/1) | 0 (0/0) | 2 (1/1) | 1 (0/1) | 1 | 8.000, -2.000, -4.000, 7.000, 0.000 |
| 14 | 0 (0/0) | 1 (0/1) | 0 (0/0) | 1 (1/0) | 2 (1/1) | -1 | -12.500, 1.000, -1.500, 2.500, 3.000 |
| 15 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 8.500, 5.500, 2.500, 9.000, 3.500 |
| 16 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 1 (1/0) | 0 | 9.500, 6.000, -1.000, 9.500, 0.500 |
| 17 | 1 (1/0) | 2 (1/1) | 0 (0/0) | 1 (1/0) | 2 (1/1) | -1 | 0.500, 9.000, 3.000, -5.000, 7.500 |
| 18 | 0 (0/0) | 0 (0/0) | 0 (0/0) | 0 (0/0) | 1 (0/1) | 0 | -12.000, -18.000, 0.500, -16.000, -3.500 |
| 19 | 1 (1/0) | 2 (1/1) | 0 (0/0) | 1 (1/0) | 2 (1/1) | -1 | -5.500, 5.500, 4.500, -2.000, 5.500 |

### novice

| Cluster | v7 | forcedP16 | forcedv6 | omega0 | historicalP16 | Δ wins | Mean S (arm order above) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 26.000, 21.000, -4.500, 27.500, 26.000 |
| 1 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 31.000, 25.000, -9.500, 32.500, 21.500 |
| 2 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 25.500, 21.500, -8.500, 23.500, 26.000 |
| 3 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 18.500, 16.500, -8.000, 17.500, 22.000 |
| 4 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 22.500, 17.500, -7.500, 23.000, 19.000 |
| 5 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 26.000, 24.500, -8.500, 23.000, 24.500 |
| 6 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 25.500, 11.500, -3.000, 19.500, 17.000 |
| 7 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 29.000, 26.500, -7.500, 26.500, 24.000 |
| 8 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 33.500, 28.000, -9.500, 30.500, 25.500 |
| 9 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 21.500, 15.500, -5.000, 26.000, 22.000 |
| 10 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 27.500, 24.500, -6.000, 29.500, 25.000 |
| 11 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 28.000, 25.000, -7.500, 21.500, 20.500 |
| 12 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 23.500, 16.000, -9.000, 19.000, 21.000 |
| 13 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 26.500, 16.000, -9.500, 30.500, 20.000 |
| 14 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 28.500, 26.500, -8.000, 28.500, 30.000 |
| 15 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 23.500, 18.500, -3.000, 23.000, 23.500 |
| 16 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 29.500, 25.000, -7.000, 28.500, 15.000 |
| 17 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 34.500, 31.000, -8.000, 35.500, 31.000 |
| 18 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 20.000, 16.500, -8.500, 23.500, 12.000 |
| 19 | 2 (1/1) | 2 (1/1) | 0 (0/0) | 2 (1/1) | 2 (1/1) | 0 | 28.500, 26.500, -3.500, 28.000, 23.000 |

## Gate and selected-source diagnostics

Counts and shares below pool stored per-fight telemetry within each arm/head. Selected-source shares count unit-ticks across all roles; melee actions are identical in both sources. Gate-mode transitions remain recorded in forced arms; their selected source stays fixed. Pair modes are a separate inherited diagnostic. Historical P16 has no outer-selector telemetry.

| Arm | Head | Gate transitions | P16 selected / total | v6 selected / total | Pair commit ticks | Pair escape ticks |
| --- | --- | --- | --- | --- | --- | --- |
| v7 | regular | 951 | 1095507/1303484 (0.840445) | 207977/1303484 (0.159555) | 32201419 | 3762902 |
| v7 | novice | 1142 | 1066037/1189093 (0.896513) | 123056/1189093 (0.103487) | 27967426 | 2098070 |
| forcedP16 | regular | 863 | 1110864/1110864 (1.000000) | 0/1110864 (0.000000) | 31984395 | 548613 |
| forcedP16 | novice | 1160 | 1111559/1111559 (1.000000) | 0/1111559 (0.000000) | 27607757 | 984143 |
| forcedv6 | regular | 1589 | 0/3484806 (0.000000) | 3484806/3484806 (1.000000) | 56615991 | 21229895 |
| forcedv6 | novice | 2006 | 0/1777646 (0.000000) | 1777646/1777646 (1.000000) | 41498591 | 9126773 |
| omega0 | regular | 811 | 1096807/1329237 (0.825140) | 232430/1329237 (0.174860) | 32103740 | 3970728 |
| omega0 | novice | 1053 | 1064951/1165700 (0.913572) | 100749/1165700 (0.086428) | 28085648 | 1818460 |
| historicalP16 | regular | 0 | not available (zero denominator) | not available (zero denominator) | 31853816 | 751237 |
| historicalP16 | novice | 0 | not available (zero denominator) | not available (zero denominator) | 27101459 | 1965372 |

## Firing and geometry diagnostics

Fractions are pooled numerator/denominator ratios, not means of per-fight fractions. Actual in-band time uses P16-selected gun ticks with gun and focus both alive after the step. Post arrival uses the prepared gun centre within 20 px of the clipped post. Escort arrival uses the post-step centre within 20 px. No spacing or shot-range guarantee is implied.

| Arm | Head | Own launches | Distinct target IDs | Target differs between sources ticks | Chosen gun-target V | P16 selected gun-target V | Post arrival | Actual in focus band | Escort arrival | Raw goal outside band / selected posts | Clipped goal outside band / selected posts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v7 | regular | 7377 | 50 | 138638 | 571795/168434 (3.394772) | 570976/167997 (3.398727) | 166370/322956 (0.515148) | 166155/321581 (0.516682) | 184181/512854 (0.359129) | 51758/322956 (0.160263) | 51758/322956 (0.160263) |
| v7 | novice | 5195 | 50 | 52375 | 347527/60522 (5.742160) | 347527/60522 (5.742160) | 64968/182870 (0.355269) | 58831/181566 (0.324020) | 166695/473192 (0.352278) | 43857/182870 (0.239826) | 43857/182870 (0.239826) |
| forcedP16 | regular | 7552 | 50 | 140007 | 566411/170915 (3.313992) | 566411/170915 (3.313992) | 168035/320941 (0.523570) | 168884/319457 (0.528660) | 185594/515283 (0.360179) | 50320/320941 (0.156789) | 50320/320941 (0.156789) |
| forcedP16 | novice | 5375 | 50 | 53168 | 358063/59676 (6.000117) | 358063/59676 (6.000117) | 64076/180670 (0.354658) | 57784/179390 (0.322114) | 170856/476680 (0.358429) | 43722/180670 (0.241999) | 43722/180670 (0.241999) |
| forcedv6 | regular | 7411 | 50 | 21421 | 25397/11923 (2.130085) | not available (zero denominator) | not available (zero denominator) | not available (zero denominator) | not available (zero denominator) | not available (zero denominator) | not available (zero denominator) |
| forcedv6 | novice | 3954 | 50 | 32357 | 64820/21373 (3.032798) | not available (zero denominator) | not available (zero denominator) | not available (zero denominator) | not available (zero denominator) | not available (zero denominator) | not available (zero denominator) |
| omega0 | regular | 7515 | 50 | 143608 | 575807/171081 (3.365698) | 575325/170788 (3.368650) | 168742/324247 (0.520412) | 168961/322958 (0.523167) | 183586/508361 (0.361133) | 51493/324247 (0.158808) | 51493/324247 (0.158808) |
| omega0 | novice | 5237 | 50 | 49136 | 345398/59213 (5.833145) | 345398/59213 (5.833145) | 63860/181790 (0.351284) | 57494/180513 (0.318503) | 166305/474047 (0.350820) | 44103/181790 (0.242604) | 44103/181790 (0.242604) |
| historicalP16 | regular | 7485 | 50 | 0 | 571270/171728 (3.326598) | 571270/171728 (3.326598) | 168180/320996 (0.523932) | 169717/319628 (0.530983) | 189552/517780 (0.366086) | 50228/320996 (0.156475) | 50228/320996 (0.156475) |
| historicalP16 | novice | 5832 | 50 | 0 | 352761/59934 (5.885824) | 352761/59934 (5.885824) | 64520/181460 (0.355560) | 58045/180152 (0.322200) | 172852/480893 (0.359440) | 44074/181460 (0.242885) | 44074/181460 (0.242885) |

| Arm | Head | Own gun victims / gun-damaging shells | Enemy gun victims / gun-damaging shells | Own artillery enemy ranged kills <20 s | <30 s | Low amplitude samples / total | Absolute argument-rate sum / valid samples | Retries | Numerical failure ticks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v7 | regular | 5057/4209 (1.201473) | 920/898 (1.024499) | 691 | 843 | 830157/1303484 (0.636875) | 140653.75667648602/470521 (0.298932) | 0 | 0 |
| v7 | novice | 5088/1354 (3.757755) | not available (zero denominator) | 573 | 1015 | 643370/1189093 (0.541059) | 178012.9825302726/542164 (0.328338) | 0 | 0 |
| forcedP16 | regular | 5099/4193 (1.216074) | 1051/1018 (1.032417) | 714 | 844 | 665758/1110864 (0.599315) | 126865.41746422251/442543 (0.286674) | 0 | 0 |
| forcedP16 | novice | 5083/1328 (3.827560) | not available (zero denominator) | 554 | 1000 | 588294/1111559 (0.529251) | 173540.145777024/519859 (0.333822) | 0 | 0 |
| forcedv6 | regular | 380/363 (1.046832) | 2587/1168 (2.214897) | 0 | 21 | 2617880/3484806 (0.751227) | 312584.20468347496/862206 (0.362540) | 0 | 0 |
| forcedv6 | novice | 1981/644 (3.076087) | 3878/2398 (1.617181) | 0 | 548 | 1124290/1777646 (0.632460) | 293276.1082774097/648399 (0.452308) | 0 | 0 |
| omega0 | regular | 5100/4289 (1.189088) | 1010/969 (1.042312) | 672 | 787 | 851583/1329237 (0.640656) | 188.49555921538825/474669 (0.000397) | 0 | 0 |
| omega0 | novice | 5117/1333 (3.838710) | not available (zero denominator) | 600 | 1019 | 612133/1165700 (0.525121) | 0/549712 (0.000000) | 0 | 0 |
| historicalP16 | regular | 5152/4251 (1.211950) | 1149/1117 (1.028648) | 716 | 825 | 851570/1163187 (0.732101) | 69663.6918163346/308268 (0.225984) | 0 | 0 |
| historicalP16 | novice | 5104/1311 (3.893211) | not available (zero denominator) | 462 | 1071 | 860429/1133856 (0.758852) | 65360.02275066394/269728 (0.242318) | 0 | 0 |

| Arm | Head | Escort / gun selected source combination | Ticks |
| --- | --- | --- | --- |
| v7 | regular | P16_escort__P16_gun | 512598 |
| v7 | regular | P16_escort__v6_gun | 256 |
| v7 | regular | v6_escort__P16_gun | 93460 |
| v7 | regular | v6_escort__v6_gun | 9288 |
| v7 | novice | P16_escort__P16_gun | 473192 |
| v7 | novice | v6_escort__P16_gun | 34593 |
| forcedP16 | regular | P16_escort__P16_gun | 515283 |
| forcedP16 | novice | P16_escort__P16_gun | 476680 |
| forcedv6 | regular | v6_escort__v6_gun | 1910414 |
| forcedv6 | novice | v6_escort__v6_gun | 1173370 |
| omega0 | regular | P16_escort__P16_gun | 508211 |
| omega0 | regular | P16_escort__v6_gun | 150 |
| omega0 | regular | v6_escort__P16_gun | 106635 |
| omega0 | regular | v6_escort__v6_gun | 6955 |
| omega0 | novice | P16_escort__P16_gun | 474047 |
| omega0 | novice | v6_escort__P16_gun | 30549 |
| historicalP16 | regular | P16_escort__P16_gun | 517780 |
| historicalP16 | novice | P16_escort__P16_gun | 480893 |

Mean surviving own artillery (death-based curve carries terminal survivors forward):

| Arm | Head | 10 s | 20 s | 30 s | 45 s | 60 s |
| --- | --- | --- | --- | --- | --- | --- |
| v7 | regular | 10.000 | 9.750 | 5.750 | 4.525 | 4.475 |
| v7 | novice | 10.000 | 9.975 | 9.925 | 9.925 | 9.925 |
| forcedP16 | regular | 10.000 | 9.875 | 5.975 | 5.375 | 5.250 |
| forcedP16 | novice | 10.000 | 10.000 | 9.975 | 9.975 | 9.975 |
| forcedv6 | regular | 10.000 | 10.000 | 9.975 | 9.525 | 7.425 |
| forcedv6 | novice | 10.000 | 10.000 | 9.775 | 1.450 | 0.050 |
| omega0 | regular | 10.000 | 9.850 | 5.700 | 4.300 | 4.125 |
| omega0 | novice | 10.000 | 9.975 | 9.975 | 9.975 | 9.975 |
| historicalP16 | regular | 10.000 | 9.875 | 5.050 | 4.550 | 4.375 |
| historicalP16 | novice | 10.000 | 10.000 | 10.000 | 10.000 | 10.000 |

## Stored recovery and presentation status

| Attempt | Stage | Status | Seconds | Prior / allowance (s) | Error |
| --- | --- | --- | --- | --- | --- |
| ATTEMPT_dc296a269683490a8bcf6899a51f335a.json | validate | PASS | 227.16235725 | 0 / 3600 | — |
| ATTEMPT_eb681c6dfe8240248636f44adbcd5a4d.json | analyze_validate | RUNNING | unclosed historical record | 227.16235725 / 3372.8376427499998 | — |
| ATTEMPT_a00a3b20e4eb4f9f9fd4a364bf3f4f73.json | analyze_validate | PASS | 6569.993903167 | 0.0 / 7200.0 | — |
| ATTEMPT_1599c2b6060d4cbab32bd5d331bbb425.json | render_validate | STOP | 630.00906 | 6569.993903167 / 630.0060968329999 | TimeoutError: shared cumulative 7200 s night allowance |

Boot evidence: epoch 1791399114.777526; interrupted-analysis charge 2723.777526 s. V2 supersedes accounting only; validation was not resealed. V1’s conservative record stays unchanged.

Analysis PASS consumed 6569.993903167 s of the shared 7200 s stored-only night allowance. The sealed HTML render STOP consumed its remaining 630.0060968329999 s allowance (measured 630.00906 s, including watchdog overhead). This Markdown report is a separate JSON-only presentation under the owner’s current request; it does not restart the sealed render or renew that allowance.

Historical cumulative charge remains 2950.9398832499996 s. The two night attempts consumed 7200.002963167 s in total; watchdog overhead beyond the cap is 0.002963167 s. No spent time is clipped or reset.

## Limits

Observed match is a descriptive count-band label, not superiority, equivalence or proof of no effect. The panel has 20 paired development clusters, not 40 independent samples and not a population-rate estimate. Positive mean S alone does not imply elimination: forcedv6 has positive regular mean S and zero regular wins.

Observed total effect of inherited ranged/artillery natural rate zero; gate transitions and firing target/geometry diagnostics accompany counts. No isolated gate timing inference. ω0 − v7 observed regular wins: -2; this does not establish that rotation is negligible or unnecessary.

The selector switches between oscillator-containing command packages. The v7/forcedP16 contrast concerns outer selection conditional on θ*. The forcedv6 result does not identify the action map as the sole cause of killing. These data establish no necessity of oscillation, synchrony causality, hierarchy or B→R→B recursion. No S5 or judging authorization or scientific acceptance follows.

The report generator reads committed JSON through git show and writes only this new report. The reviewer’s raw-data verification is recorded separately in s4_checks/v7_validation_recheck/AUDIT.json.
