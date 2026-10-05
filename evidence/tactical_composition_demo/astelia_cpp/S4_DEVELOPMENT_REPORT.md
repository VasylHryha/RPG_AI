STOP

# S4 development report

Implementer family: Codex (GPT-6). Date: 2026-10-05. Owner-authorized development under decision 0028; design revision 3, **original S4 request at ebb8d5a**. Claude review remains pending. No registration, judging seeds, recorded S5 run, milestone status change or frozen-file modification.

The tuned resonator’s final novice mean S is -6.92188 after its full 7,680-fight budget. This triggers the declared STOP. Its regular mean is -10.20312. No tactical superiority or equivalence verdict is assigned. The sampling and power proposals below do not override this stop.

## Request changed during execution

**This completes the original protocol only; it does not satisfy the amended S4 request.** The [exact original request](s4_development/S4_REQUEST_ORIGINAL.md) was read before implementation. Commit ee21545, at 12:25:26 local time while fights were running, replaced the race/2-SE rule with a standard continuous optimizer (CMA-ES recommended), required result_cache.py plus a per-use s4_seeds.json ledger, raised validation to at least 100 clusters per comparison, and moved the stop gate to A or B. This change was discovered on the final pre-commit HEAD check. The original run was not silently relabelled as CMA-ES and no judging seeds were drawn.

The original Stage B validation is already negative for all four arms; under the revised A/B gate it would also stop, but its optimizer and validation size do not qualify it as the revised run. Stage A resonator mean +0.9531 versus Stage B novice −10.9844 is stated separately. A removes the projectile observation asymmetry; B/C include opponents that can read shots/shells while these controllers cannot. Army composition also changes, so these observations do not isolate projectile visibility as the cause or refute the law itself. Stage C metrics have zero forks, search calls and artillery rollouts.

The revised request and DESIGN_0G.md section 5 disagree on the optimizer acceptance rule; current owner steering can supersede the older design, but the completed run must remain under its original declared protocol. The owner explicitly chose to execute the amended protocol separately after preserving this STOP evidence. The amended run will use new files and development seeds; this evidence remains unchanged. The remaining work for the amended request is CMA-ES/standard-optimizer implementation, the specified persistent cache/per-use ledger, and ≥100-cluster validation with the earlier stop gate. This is not self-acceptance or revised-protocol completion.

## Anomaly finding

Morale’s inversion reproduces on eight matched clusters: novice −16.6875, regular −4.3125. Novice skills with line formation score +1.1250; regular skills with alone brain score −30.1875. Line improves the matchup under both bundles; regular skills strengthen the enemy within either brain. This is an intended configuration/matchup effect, not a defect. Four fights were inspected before tuning. See [the finding and configuration table](s4_anomaly/ANOMALY_FINDING.md). No equations were changed.

## Declared optimizer, budget and seeds

[S4_PROTOCOL.md](S4_PROTOCOL.md) and [the seed ledger](S4_SEED_LEDGER.json) were committed before tuning (9690d67; compressed replay/anomaly follow-up 0a9e002). Eight rounds per stage; eight candidates sampled uniformly within bound-clipped incumbent neighbourhoods. Half are joint moves, half single-knob moves; radius = 0.5×0.8^round. Race 8→16→32 clusters, retaining 4 then 2 by score. Accept only paired gain > max(1 survivor, 2 SE). Rank elimination is a search heuristic. The same algorithm, seeds and budget apply to all tuned arms. Nearest is untuned. Each next stage starts at preceding tuning best; validation never selects knobs.

Accounting: 576 candidates logged, 7,680 evaluations per tuned arm, 23,040 tuning fights; 3,712 validation fights; 64 anomaly diagnostic fights; 16 additional trace-capture fights. Total 26,832; zero cache hits and zero controller failures. All 16 captured replay summaries equal their original fight summaries. All forks, search calls and artillery rollouts are zero. See [AUDIT.json](s4_development/AUDIT.json).

Actual main tuning/validation/replay duration: 34.48 minutes. Anomaly duration: 33.51 seconds. Initial estimate 10–20 minutes was low; at 17.2 minutes the remaining estimate was revised to 10–15 minutes in the execution log. No code edits occurred during the long run.

## Stage results and best knobs

S = survivors minus enemy survivors. Means, sample cluster SD and SE below are descriptive development measurements; both orientations are averaged before statistics. The 95% mean intervals are in each validation JSON. C has 16 shared seed blocks across 19 doctrines; panel mean uncertainty uses those blocks, retaining cross-doctrine covariance. A has 32 novice clusters; B and final C have 32 per head level.

### Stage A

[Exact best knobs](s4_development/A_best.json) · [validation and keyed scores](s4_development/A_validation.json)

| Knob | Resonator | Morale | Push-pull |
|---|---:|---:|---:|
| K | 4.59063 | 1.9516 | — |
| K_t | 4.02636 | 2.18133 | — |
| kappa | 38.4145 | 38.3776 | — |
| beta | 1.31643 | 0.0802308 | — |
| G | 3.31174 | 3.61799 | 3.03632 |
| w | 2.45627 | 2.16612 | — |
| f | 0.809378 | 0.895942 | 0.318394 |
| gamma | 0.795909 | 1.44517 | — |
| omega_melee | -0.300448 | — | — |
| omega_ranged | -1.51762 | — | — |
| lambda_melee | — | 1.11231 | — |
| lambda_ranged | — | 0.833425 | — |

| Arm | Validation setting | Mean S | Cluster SD | SE |
|---|---|---:|---:|---:|
| resonator | s4_melee10|novice | 0.9531 | 2.0998 | 0.3712 |
| morale | s4_melee10|novice | 4.3281 | 1.1682 | 0.2065 |
| pushpull | s4_melee10|novice | 0.7656 | 2.3314 | 0.4121 |
| nearest | s4_melee10|novice | 1.2969 | 2.1808 | 0.3855 |

| Tuned arm | Final-round development mean S | SD | Accepted rounds in stage |
|---|---:|---:|---:|
| resonator | 1.3281 | 2.0265 | 2 / 8 |
| morale | 4.1562 | 1.3225 | 3 / 8 |
| pushpull | 2.0938 | 2.3121 | 2 / 8 |

### Stage B

[Exact best knobs](s4_development/B_best.json) · [validation and keyed scores](s4_development/B_validation.json)

| Knob | Resonator | Morale | Push-pull |
|---|---:|---:|---:|
| K | 2.27586 | 3.44859 | — |
| K_t | 1.53589 | 1.99375 | — |
| kappa | 48.2144 | 25.1241 | — |
| beta | 2.29839 | 0.226645 | — |
| G | 3.29717 | 3.59876 | 3.98911 |
| w | 0.973772 | 0.763635 | — |
| f | 1.01051 | 0.820855 | 1.14367 |
| gamma | 0.931835 | 1.07896 | — |
| omega_melee | 1.49108 | — | — |
| omega_ranged | -0.569584 | — | — |
| lambda_melee | — | 1.69706 | — |
| lambda_ranged | — | 0.86572 | — |

| Arm | Validation setting | Mean S | Cluster SD | SE |
|---|---|---:|---:|---:|
| resonator | s4_full_head|novice | -10.9844 | 2.1608 | 0.3820 |
| resonator | s4_full_head|regular | -10.0156 | 2.9986 | 0.5301 |
| morale | s4_full_head|novice | -5.2812 | 2.9701 | 0.5250 |
| morale | s4_full_head|regular | -0.9688 | 1.3316 | 0.2354 |
| pushpull | s4_full_head|novice | -4.2031 | 3.1670 | 0.5599 |
| pushpull | s4_full_head|regular | -0.8594 | 1.3751 | 0.2431 |
| nearest | s4_full_head|novice | -18.1406 | 3.7871 | 0.6695 |
| nearest | s4_full_head|regular | -21.2031 | 6.1642 | 1.0897 |

| Tuned arm | Final-round development mean S | SD | Accepted rounds in stage |
|---|---:|---:|---:|
| resonator | -9.7812 | 2.3893 | 1 / 8 |
| morale | -2.5156 | 2.5128 | 3 / 8 |
| pushpull | -2.6719 | 2.9501 | 5 / 8 |

### Stage C

[Exact best knobs](s4_development/C_best.json) · [validation and keyed scores](s4_development/C_validation.json)

| Knob | Resonator | Morale | Push-pull |
|---|---:|---:|---:|
| K | 0.354077 | 2.81509 | — |
| K_t | 0.150436 | 1.4001 | — |
| kappa | 41.8355 | 33.6991 | — |
| beta | 1.45693 | 0.715708 | — |
| G | 2.6095 | 4.07228 | 4.03018 |
| w | 1.89056 | 2.2321 | — |
| f | 1.12593 | 0.874848 | 1.14367 |
| gamma | 1.58909 | 0.593565 | — |
| omega_melee | 0.892952 | — | — |
| omega_ranged | -1.33997 | — | — |
| lambda_melee | — | 1.61371 | — |
| lambda_ranged | — | 0.741756 | — |

| Arm | Validation setting | Mean S | Cluster SD | SE |
|---|---|---:|---:|---:|
| resonator | s4_full_head|novice | -6.9219 | 6.1881 | 1.0939 |
| resonator | s4_full_head|regular | -10.2031 | 7.4453 | 1.3162 |
| resonator | P2/P3 pool, 304 config clusters / 16 seed blocks | 1.7270 | 13.7570 | 0.6295 (block) |
| morale | s4_full_head|novice | -16.7656 | 5.1775 | 0.9153 |
| morale | s4_full_head|regular | -17.4219 | 9.8980 | 1.7497 |
| morale | P2/P3 pool, 304 config clusters / 16 seed blocks | 1.4260 | 14.5881 | 0.4548 (block) |
| pushpull | s4_full_head|novice | -4.9375 | 2.5864 | 0.4572 |
| pushpull | s4_full_head|regular | -0.6719 | 1.7162 | 0.3034 |
| pushpull | P2/P3 pool, 304 config clusters / 16 seed blocks | -5.7780 | 5.6824 | 0.1193 (block) |
| nearest | s4_full_head|novice | -17.5469 | 3.8129 | 0.6740 |
| nearest | s4_full_head|regular | -22.1719 | 7.3623 | 1.3015 |
| nearest | P2/P3 pool, 304 config clusters / 16 seed blocks | -20.0658 | 8.6390 | 0.2298 (block) |

| Tuned arm | Final-round development mean S | SD | Accepted rounds in stage |
|---|---:|---:|---:|
| resonator | -0.0156 | 13.4149 | 2 / 8 |
| morale | 0.8125 | 16.3977 | 1 / 8 |
| pushpull | -4.9375 | 5.6551 | 1 / 8 |

## Paired spreads, δ and bounded power proposal

Proposed **δ = 3.5 survivors**, from the predeclared max(1, 0.25×maximum validation pooled paired SD), rounded upward to 0.5. It has not been approved by the owner and was never reduced to obtain a pass.

| Endpoint | Paired mean | Config-cluster SD | Shared-seed-block SD | Block SE | Block mean 95% interval | SD upper (pooled / block) |
|---|---:|---:|---:|---:|---|---|
| P2: resonator_minus_morale | 0.3010 | 12.8691 | 3.1594 | 0.7898 | [-1.2471, 1.8491] | 13.8437 / 3.7426 |
| P3: resonator_minus_pushpull | 7.5049 | 13.3691 | 2.6333 | 0.6583 | [6.2146, 8.7953] | 14.0528 / 3.1754 |

SD uncertainty is the bootstrap 95th-percentile upper value, 2,000 resamples with seed 811005; intervals are descriptive normal approximations. Power is a normal planning approximation at one-sided alpha .0025 and power .90. P1 plans a positive δ effect above zero; P2/P3 plan true mean 2δ against margin δ. Required n = ceil((z_(.9975)+z_(.90))²×variance/δ²), with floors 32 per head and 16 per doctrine. Use the larger development/validation noise allowance, retain seed-block covariance, and count all configurations against the 2,000-cluster endpoint bound.

| Endpoint | Proposed n | Total configuration clusters | Within 2,000? |
|---|---|---:|---|
| P1 | 105 per head level | 210 | yes |
| P2 | 22 per doctrine / shared seed blocks | 418 | yes |
| P3 | 16 per doctrine / shared seed blocks | 304 | yes |

These n values assume the stated hypothetical beneficial effect; a larger sample cannot turn the observed negative novice mean into a supported result. S4 is STOP. [POWER_PLANNING_CORRECTION.json](s4_development/POWER_PLANNING_CORRECTION.json) supplies both-split spreads, covariance-aware uncertainty and all calculations. The initial power.json is retained unchanged as superseded output.

## Watching fights

Open any linked HTML locally in a browser. Each file includes its compressed replay and has no external dependencies. Play/pause, 1×/4×/10×, timeline scrub and targets are available. Blue/orange outlines are teams; fill is resonator phase or morale commitment; HP bars show health. Grey units have no controller state. The standalone [viewer](s4_replay.html) also loads a `.replay.json.gz`. Raw 30 Hz traces are retained; display payloads sample 10 Hz with the terminal frame included.

| Stage | Resonator | Morale | Push-pull | Nearest |
|---|---|---|---|---|
| A | [resonator](s4_development/replays/A_resonator.html) | [morale](s4_development/replays/A_morale.html) | [pushpull](s4_development/replays/A_pushpull.html) | [nearest](s4_development/replays/A_nearest.html) |
| B | [resonator](s4_development/replays/B_resonator.html) | [morale](s4_development/replays/B_morale.html) | [pushpull](s4_development/replays/B_pushpull.html) | [nearest](s4_development/replays/B_nearest.html) |
| C | [resonator](s4_development/replays/C_resonator.html) | [morale](s4_development/replays/C_morale.html) | [pushpull](s4_development/replays/C_pushpull.html) | [nearest](s4_development/replays/C_nearest.html) |

The Stage A resonator example has nonzero role rates and five of ten unit trajectories span more than 2π in unwrapped phase (maximum span 7.82 rad). This exercises the review note, without claiming rotating phases are necessary or that candidate groups meet C4/C5 qualification.

## Checks, deviations and remaining gate

The current native/controller suite passed 220 tests in 32.89 seconds before fights; replay packaging then passed its eight affected checks. The final affected planning checks passed 10 tests in 0.49 seconds. Browser checks passed all 12 new replays with no JavaScript errors. Independent raw-summary reconstruction matched 17,984 cluster entries, replayed the declared sampler and recomputed all paired gains; no new fights. Receipts are retained in s4_checks. RRG source pin, native binary/source admission, exact budget totals, paired orientations, candidate acceptance, code identity and replay equality were reconstructed from retained evidence.

Deviations: (1) initial test collection included archived duplicate test names and stopped before running tests; corrected to current top-level test files. (2) Large replay payloads were compressed after the anomaly diagnostic, without rerunning fights or changing raw traces. (3) Temporary implementation helpers/logs initially used /private/tmp; after owner correction they were moved/copied into s4_checks and subsequent work stayed in the project. (4) The initial runtime estimate was too low and was revised during execution. (5) Initial power output used only validation and independent-stratum variance; the final supplemental calculation uses both splits, shared-seed blocks and a common P1 n, leaving initial output unchanged. (6) The request changed during execution; the original protocol is preserved and does not fulfill amended requirements. No equation changes, budget restarts, controller failures, new knobs, new arms or judging seeds.

Remaining gate for this original run: independent Claude review of these original-protocol development artifacts. The owner must decide what follows the STOP and separately approve any δ or future S5 specification. This report does not self-accept S4, authorize S5, or alter milestone status.
