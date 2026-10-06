SAFE_UNDER_PROPOSED_TOLERANCE

# C6 option B: what the faster inexact math changes

**Date:** 2026-10-06. **Author:** Claude (claude-opus-5-5).
**Status:** engineering diagnostic only.
- **What it is:** a measurement of what changes, made at the owner's request.
- **What it is not:** an approval. Using the inexact engine still needs the owner's decision and a decision record, because it ends the zero-tolerance contract of decision 0029, item 3.
- **What was not touched:** final entropy, registration, gates, STATUS.json and C0–C5. No repository source file changed; both engines ran from scratch copies of `a52ddbd`.

## Answer in plain words

**How big is the difference?**
- The largest change to any number in 10 complete worlds was **3.3 × 10⁻⁹**, and it was in a grid-error diagnostic, not a decision value. On numbers that decisions actually use, the largest change was **2.4 × 10⁻¹⁰**.
- About half of all numbers change in their last digits, 8.9 million of 17.4 million.

**Did any outcome change?** No.
- Every decision in all 10 worlds came out the same. That covers:
  - 76,703 threshold decisions;
  - 55,200 phase-lock pair tests;
  - 1.7 million geometric link tests;
  - every discrete field, outcome, chain and witness.
- **How far is a flip?** The decision closest to flipping sits **7.3 × 10⁻⁹** from its threshold. The inexact math moved its value by **4 × 10⁻¹⁶**, about **17 million times less** than the distance to a flip.
- **Comparison with the exact engine's own noise:** the exact engine's three time-step grids already disagree on that same number by 7.3 × 10⁻¹³, which is 1,700 times more than the inexact change.

**Speed:**
- **CPU:** **about 25% less** per world (paired ratio 0.72–0.77 on non-trivial worlds).
- **Wall time:** about 25% less on average, but noisy (0.64–0.83), because the paired runs could not be launched together while the 0g run was using the machine.

**What we would give up:**
- **Bit-identity with old receipts:** the inexact engine no longer matches stored receipts bit for bit. Every state digest changes; 45,592 changed in these worlds.
- **Reproducibility across OS updates:** Apple may change the Accelerate math library in a macOS update. So even new inexact references would need the OS build pinned, or a re-baseline after each update.
- **Not a loss of accuracy:** the exact engine is not "more correct". Apple's ordinary math library is not correctly rounded either (memo §3, item 6). Both are accurate to about 1 unit in the last place. "Exact" means reproducible against what we stored, not truer.

**Recommendation:**
- **Safe to use:** the difference is far too small to change any outcome we measured. It meets every condition of the prepared tolerance (memo §7), with one correction (see "Correction to the prepared tolerance").
- **No need yet:** the exact engine already meets the 360 s rule with about 2.4× headroom.
- **Suggestion:** turn it on when time matters, for example the 40-world panel on a busy machine. If the owner approves, follow the adoption steps at the end.

## 1. What was compared

| Item | Detail |
|---|---|
| **Exact engine** | Current option B, `field.cpp` `9ebe2acf…` (the committed final code). Re-verified here: smoke world 1 matches the stored reference **bit for bit** (1,460,200 numbers and 1,396 decisions, max error 0; `results/exact_smoke_1_vs_reference_EXACT.json`). |
| **Inexact engine** | The same code with only the two round-2 hunks (`scripts/inexact_kernel.patch`): Apple Accelerate `vvsincos`/`vvexp` for the pair terms, and separable `exp(a)·exp(b)` site Gaussians through `vvexp`; builds with `-framework Accelerate`. Nothing else changed. |
| **Worlds** | The 4 stored references (smoke 0 and 1, entropy 46036002; development 0 and 1, entropy 46036001), plus **development worlds 2–7** (entropy 46036001, inside the 10-world development set). Worlds 2–7 ran on **both** engines. |
| **Runs** | One world at a time, because the 0g v5 run was using the machine (load 27–80 on 10 cores; `runs/QUEUE.log`). Every run used `--parallel` (5 threads) under `caffeinate`. |
| **Tools** | `scripts/impact.py` compares one world pair; `scripts/summarize.py` aggregates; `scripts/run_impact.sh` maps each world to its exact reference; `scripts/battery.py` runs the registered numeric diagnostics. The worlds 0–7 option in the scratch check tool is `scripts/check_tool_worlds_0_7.patch`. |

## 2. Per world

| World | Values changed | Max deviation | > 1e-10 | > 1e-8 | Discrete changes | Decisions | Closest decision to its threshold | Outcome (identical in both) |
|---|---:|---:|---:|---:|---:|---:|---|---|
| smoke 0 | 1,603,002 / 2,856,122 | 4.3e-10 | 2 | 0 | 0 | 12,498 | 1.7e-4 (freq_change) | T1, T2 persistent unit; **chain complete** |
| smoke 1 | 483,809 / 1,365,412 | 4.3e-11 | 0 | 0 | 0 | 6,139 | 6.1e-4 (freq_change) | T1 persistent unit |
| development 0 | 1,596,575 / 2,492,801 | 5.1e-10 | 2 | 0 | 0 | 11,296 | **7.3e-9** (freq_change) | T1 persistent unit; T2 source lost |
| development 1 | 1,601,090 / 2,491,871 | 2.2e-11 | 0 | 0 | 0 | 11,254 | 1.2e-5 (freq_change) | T1 persistent unit; T2 source lost |
| development 2 | 1,557,136 / 2,494,661 | 3.3e-9 | 14 | 0 | 0 | 11,380 | 5.2e-5 (freq_change) | T1 persistent unit; T2 source lost at 331 s |
| development 3 | 551,584 / 1,360,762 | 1.9e-9 | 4 | 0 | 0 | 5,929 | 1.0e-3 (response refinement) | T1 persistent unit |
| development 4 | 460,022 / 1,363,356 | 5.1e-11 | 0 | 0 | 0 | 6,043 | 1.0e-3 (response refinement) | T1 persistent unit |
| development 5 | 604,935 / 1,362,426 | 1.6e-10 | 1 | 0 | 0 | 6,001 | 5.1e-4 (pattern_change) | T1 persistent unit |
| development 6 | 2,042 / 263,303 | 1.3e-13 | 0 | 0 | 0 | 162 | 1.0e-3 (response refinement) | no source qualified |
| development 7 | 446,835 / 1,362,426 | 1.3e-9 | 6 | 0 | 0 | 6,001 | 3.4e-4 (freq_change) | T1 persistent unit |
| **All 10** | **8,907,030 / 17,413,140** | **3.3e-9** | **29** | **0** | **0** | **76,703** | **7.3e-9** | **all identical** |

"Outcome" covers the following fields, and every one of them is identical in the two engines:
- validity (`invalid`) and chain completion;
- the enabled witness;
- the link count;
- per turn: operation eligibility, physical outcome, first loss time, witness tuple and controls.

## 3. Where the differences are

- **All 29 values above 1e-10 are numerical monitors, not decisions:**
  - 28 are grid-error diagnostics, the difference between the dt, dt/2 and dt/4 solutions, around 1e-5 in size. These monitors have a limit of 0.05, and every one stays at least 0.048 below it.
  - 1 is a recovery pattern error, 2.4e-10, against a threshold distance of at least 9e-3.
- **State values themselves** (positions, phases, fields, qualification windows) change by **≤ 5.4e-11** absolute and **≤ 3.2e-8** relative.
- **Over time:** the operation frames span 100 s per turn and condition, and their deviation stays between 1e-15 and 2e-12. It does **not** blow up over the 100 s exposures, nor from turn 1 to turn 2.
- **Discrete changes:** none. All 45,592 changed digests are state identities. They must change once any last bit changes.

## 4. How far each kind of decision is from flipping

Every decision the protocol takes from a number was checked against its own threshold; the counts are 3 grids × all candidates, windows and checks.

| Decision | Count | Closest to threshold | Largest inexact change | Smallest (distance ÷ change) |
|---|---:|---:|---:|---:|
| membership Jaccard ≥ 0.95 | 12,069 | 6.5e-3 | 0 | ∞ |
| shape CV ≤ 0.05 | 12,069 | 2.4e-2 | 9.3e-14 | 5.2e11 |
| lock std ≤ 0.1 | 12,069 | 3.6e-3 | 5.5e-12 | 2.0e10 |
| **freq change ≤ 0.01** | 12,069 | **7.3e-9** | 4.1e-14 | **1.7e7** |
| pattern change ≤ 0.1 | 12,069 | 1.8e-4 | 7.3e-12 | 5.4e9 |
| recovery Jaccard ≥ 0.9 | 558 | 5.8e-2 | 0 | ∞ |
| recovery pattern error ≤ 0.1 | 558 | 9.1e-3 | 2.4e-10 | 2.9e8 |
| causal floor (intact > 1e-8) | 368 | 5.9 decades | 4.9e-12 | 1.7e12 |
| causal refinement spread | 368 | 8.8e-4 | 1.5e-11 | 5.8e9 |
| causal ablation vanishes | 368 | 1.8e-3 | 0 | ∞ |
| grid error, position / phase / field ≤ 0.05 | 4,695 each | 0.048 / 0.050 / 0.050 | 3.3e-9 / 3.2e-10 / 3.4e-12 | 1.5e7 / 1.5e8 / 1.5e10 |
| response refinement ≤ 0.001 | 53 | 1.0e-3 | 2.8e-15 | 3.5e11 |

**The underlying pair decisions** were recomputed on every stored qualification window (grid dt): 200 windows, 55,200 pair lock tests and 1,711,200 pair link tests. **0 flips.**
- **Closest lock test:** 1.8e-3 from 0.1 (development 4), against an inexact change of 8.8e-15.
- **Closest link test:** 6.3e-7 relative to its threshold (smoke 0), against an inexact change of 4.3e-15 relative.

**The single closest decision** is a frequency-change test in development world 0, turn 2. Persistence window 29 measures 0.010000007264 against the 0.01 limit. That decision is why turn 2's source counts as lost there, and it is the same in both engines.
- The inexact engine moved this value by 8e-17 to 4e-16, depending on the grid.
- The exact engine's own dt and dt/4 grids differ on it by 7.3e-13.
- A case this close is decided by the time-step grid long before the math library could matter. If the grids disagreed on a decision, the protocol would stop on its own refinement check ("grid-dependent persistence"); it would not silently flip.

**Risk of an outcome change in a full 40-world panel:**
- **Conservative estimate, about 2 × 10⁻⁴** (roughly 1 panel in 5,000). It assumes every decision moves by the worst change seen on any decision value (2.4e-10). Near-threshold density is taken from the 21 decision instances that sat within 1e-4 of their threshold here; many are copies of one decision across grids and conditions, which makes the estimate conservative.
- **Using each kind's own changes:** for frequency tests, which hold every near-threshold case seen, the change is ≤ 4e-14, and the risk falls below 10⁻⁷.
- Neither figure is a guarantee. They are estimates from 10 worlds.

## 5. Registered numeric diagnostics, which the prepared tolerance requires to still pass

Both diagnostics were run under each option-B engine (`scripts/battery.py`; `results/results_battery_*.json`, about 80 s each):

| Diagnostic | Limit | Exact engine | Inexact engine |
|---|---:|---:|---:|
| `b_reference_equivalence` (5 conditions, probe, recovery, isolated periodic solutions) | 1e-10 | PASS, max 9.5e-13 | **PASS, max 1.3e-12** |
| `b_transform_equivariance` (rotation, shift, phase, permutations, renaming) | 1e-9 | PASS, 7.5e-15 / 0 | **PASS, 7.5e-15 / 0** |

## 6. Speed

| Pair (run one after the other) | Exact CPU s | Inexact CPU s | CPU ratio | Wall ratio |
|---|---:|---:|---:|---:|
| development 2 | 248 | 191 | 0.768 | 0.799 |
| development 3 | 191 | 143 | 0.747 | 0.750 |
| development 4 | 204 | 151 | 0.741 | 0.758 |
| development 5 | 201 | 151 | 0.752 | 0.652 |
| development 7 | 205 | 147 | 0.719 | 0.833 |
| smoke 1 | 221 | 166 | 0.752 | 0.640 |
| development 6 (trivial, 7 s) | 7 | 5 | 0.807 | 0.810 |

- **CPU:** −25% on the six non-trivial pairs (mean ratio 0.747).
  - This agrees with the round-2 memo's pair launched together (−26.2%).
- **Wall:** −25% on average. Treat it as indicative only, because the machine load moved between the two runs of each pair.

## 7. Correction to the prepared tolerance (memo §7)

The memo proposed "absolute difference ≤ 1e-8 on every float, about 20× margin", based on 5.1e-10. With 10 worlds, the largest is 3.3e-9, so the margin is **3×, not 20×**. All of the largest values are grid-error monitors, whose relative change reaches 5% because they are small differences.

**Proposed tolerance, corrected:**
1. **Decision identity is the gate.** Every Boolean, integer, label, membership set, chain, witness, invalid field and stop reason must be identical. This is unchanged.
2. **State and statistic values:** ≤ 1e-8 absolute. The largest observed is 2.4e-10, a 40× margin.
3. **Grid-error diagnostics:** compared relatively, ≤ 10% of their value, and they must stay below their 0.05 limit. The largest change observed is 5% of a value that is itself about 1e-5, while each value sits at least 0.048 below the limit.
4. **Registered diagnostics:** `b_reference_equivalence` (1e-10) and `b_transform_equivariance` (1e-9) must pass. They do.

## 8. Limits of this study

- **10 worlds, not 40.** No final entropy was used, and that is correct. Development world 6 qualified no source, so it tests little.
- **Pairs ran one after the other, not side by side.** CPU ratios are reliable; wall ratios are indicative only.
- **One machine and one OS build** (macOS 26.6.2, arm64, Apple clang 21). Accelerate results may change with OS updates.
- **The prototype has no bounds guard.** The separable path assumes n·(unique site x or y) ≤ 4096; here that is 24 × 5. A production version needs an explicit guard with a fallback, plus native contract tests like the existing ones.
- **Detection (`detection.cpp`) is unchanged in both engines.** The pair-level recheck is an independent recomputation on stored windows, at grid dt only.

## 9. If the owner approves using it

1. Record a decision that replaces decision 0029 item 3 with the corrected tolerance (section 7).
2. Add the inexact kernel as a **selectable** build. Keep the exact engine as the default and as the reference. Add the bounds guard and native contract tests.
3. Before using it for anything recorded, run all 10 development worlds on both engines. Any decision flip rejects it.
4. Generate new bit-exact references with the inexact engine. Record the macOS build, and re-baseline after OS updates.

## 10. Owner recheck applied to this report

The owner's prompt, applied verbatim: "Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps." No numeric score is assigned.

**Found and fixed during the recheck:**
1. **Gap: margins were missing.** At first I compared only values, as in round 2. I added a margin check for every thresholded decision, plus a recomputation of the pair-level lock and link tests. The 7.3e-9 case in development 0 surfaced only that way.
2. **Conflict: the memo's "20× margin" for 1e-8 was wrong** with more worlds. It is 3× on monitors, and 40× on decision values. The tolerance is corrected in section 7.
3. **Gap: the registered diagnostics.** The tolerance requires them, but round 2 never ran them. Both now run under both engines, and both pass.
4. **Issue: an untrusted baseline.** Before comparing anything, I re-verified that the scratch exact engine is bit-identical to a stored reference (smoke 1, tolerance 0).
5. **Gap: growth over time.** I measured deviation along the 100 s operation frames, per turn and condition. It shows no growth that matters.
6. **Issue: outputs in the wrong places.** `links` in the output dumped digest lists, so it was reduced to a count; equality is still covered by the full walk. The battery results were moved out of the per-world aggregation.

**Remaining, disclosed:**
- Pairs ran one after the other, so wall ratios are noisy.
- There are 10 worlds, not 40.
- The OS can drift.
- The prototype has no bounds guard (section 8).

**Is this the best we can do?** For deciding "is the difference too big", yes. Every decision type, the pair-level tests, the registered diagnostics and growth over time are covered on 10 worlds. Two extensions would strengthen it: running the pairs side by side once the machine is free, for a clean wall ratio; and covering development worlds 8–9 when we adopt.

## Files

- `SUMMARY.json`: aggregates, per-world rows, costs and paired speed.
- `results/<world>.json`: the per-world comparison, with value families, all margins, the pair-level check, growth over time and outcomes.
- `results/results_battery_exact.json` and `results/results_battery_inexact.json`: the registered diagnostics.
- `results/exact_smoke_1_vs_reference_EXACT.json`: the baseline re-verification.
- `runs/<engine>_<entropy>_<world>/START.json` and `COSTS.json`: run metadata, load and timings. `runs/QUEUE.log` is the run order.
- `scripts/`: `impact.py`, `summarize.py`, `run_impact.sh`, `queue.sh`, `battery.py`, `inexact_kernel.patch` and `check_tool_worlds_0_7.patch`. They ran from the scratch directory named in `queue.sh`.
- `raw_worlds/`: the 17 complete world artifacts, 248 MB. They stay on disk and out of git; sizes and SHA256 are in `RAW_FILES_OUTSIDE_GIT.json`.
