FASTER_AND_EXACT; meets 360 s at the observed normal loads, not under the load-40-to-85 overload of the review-fix pair (engineering observation; not a registered readiness verdict)

# C6 option B: performance deep-dive (revised after Codex review)

**Date:** 2026-10-06. **Author:** Claude (claude-opus-5-5).
**Authority:** decision 0029 (engineering and runtime work, exact equivalence; the science is unchanged). Runs under one hour need no approval (decision 0031).
**Not done:** final entropy, registration, STATUS.json, mutation probe, recorded panel, or any change to C0–C5 or R4 files. C6 stays `BLOCKED / R006 STOP`.
**Revision:** Codex's cross-family review (`docs/reviews/c6_option_b_perf_review_codex.md`, CHANGES_REQUIRED on commit 8214f39) is answered in §0. Every timing and rule value below is derived from the raw COSTS.json receipts by `performance_deepdive/REPORT_VALUES.py` (output `REPORT_VALUES.json`). Display rounding: seconds and rule values to 0.1 s, ratios to 3 decimals.

## 0. Review disposition (F1–F4)

| Finding | Severity | Fix | Evidence |
|---|---|---|---|
| **F1** Batched grid runs (recovery, causal) lost earlier checks and could raise a different first error than the sequential run. | Blocking | `run_many` now only computes; it returns one terminal **Outcome** per request and publishes nothing. Inside a request, a block's three grid results are merged coarse-to-fine only after all three finish, so the first error is the one the sequential run meets first: grid k before k+1, the diagnostic after the three grids, the check after the last block. Set-up statements run in `GridSet.run`'s order. Callers `publish()` outcomes in the original order, interleaved with their own statements: recovery publishes control, then kicked; causal publishes control, treated and its measurement, fork by fork; a single run publishes at once. `publish` raises the request's own error with no check, or appends its check and then raises `NumericalFailure` if the check failed. Every submitted job is drained before a batch returns. The task level (`ordered()`) was already ordered, and is now exact through nested levels. The fork set-up in causal runs first; its only raising statement (`normalize_phase` of the same probe and members) is identical for every fork, so it raises at the first fork, as sequentially. | New tests in `tests/test_c6_option_b_parallel.py`. **(a)** Three named review cases, under both submission orders: passing control with failing kick; earlier numerical failure with later worker failure; earlier worker error with later diagnostic error. **(b)** Fuzzed failures that depend only on a request's inputs (worker, numerical and diagnostic), 14 salts under both orders, landing at many positions in recovery and causal. **(c)** The same fuzzing nested inside the concurrent operation's stage tasks, 8 cases: in descriptors, in a stage-1 exposure, and in before/condition episodes' formation and recovery runs. Sequential and concurrent results compare equal at tolerance 0, including the error type and message. Against the reviewed version (8214f39), 8 of the 11 new recovery/fuzz tests **fail**; all pass now. |
| **F2** The limits governed retained bytes, not peak allocation; a disabled drive cache lost its streaming fallback. | Medium | Each store now has `admits(bytes)`. A value that would not be retainable (disabled or oversized) is **never allocated**: the drive streams the identical per-stage expression; the medium integrates **directly into the caller's frame layout** (new `out_stride`); material skips lookup, lease and payload copy. An allocation failure in any optional path falls back the same way instead of returning −1, and frames stay exact. | C++ contract with a counting allocator. With storage disabled, the peak live native allocation during a 2,000-step run stays below 256 KiB for all five cases: no cohort; OFF retired; OFF control; ON; two cohorts. The reviewed version peaked at **3,270,992 bytes** on the no-cohort case and fails this test. With storage enabled but every allocation above 256 KiB refused, results are bit-identical, return 0, and nothing is retained. Remaining Python-side and peak-RSS composition: §4. |
| **F3** Single-flight deregistration happened before publication. | Low | `finish()` now sets the flight's `done`/`value` and removes its registration in one critical section under the store lock (lock order store → flight), and notifies afterwards. A requester can no longer find neither a registration nor a completed flight while followers still wait. | C++ contract: with nothing retained, a waiting follower receives the leader's published value (one miss, one wait, no entry), and the next request leads again. Two different full keys forced onto the **same index hash** stay distinct, each returning its own value. |
| **F4** Displayed rule values and timing ranges were rounded inconsistently or covered only a subset. | Low | All values come from `REPORT_VALUES.py` on the stored receipts; stage ranges now cover every new run. | `REPORT_VALUES.json`. |

**After the fixes:**

- **Tests:** the option-B suite gives **128 passed** in one final run (53.1 s).
- **Recheck tool:** `tools/c6_option_b_recheck.py` passes on the final build (`fixes/recheck_tool/`).
- **Exact world:** one smoke-0 world on the final code matches its reference **exactly**: 3,045,093 numeric and 2,847 Boolean values, max error 0, no digest changes (`fixes/fixed_smoke_0_EXACT.json`).
- **Identity:** the measured fixed code is identical to the committed final code: `field.cpp` `9ebe2acf…`, `c6_option_b_parallel.py` `6bb6f55d…`, binary `b395c590…`.

## Summary

Smoke world 0, old and new code run as two world processes at the same time, so both see the same load:

| Pair | Old wall s | New wall s | Wall ratio | Old CPU s | New CPU s | CPU ratio | Load (1 min) start → end |
|---|---:|---:|---:|---:|---:|---:|---|
| 1 (new = 8214f39) | 329.5 | 133.5 | 0.405 | 700.8 | 463.3 | 0.661 | 6.8 → 13.5 |
| 2 (new = 8214f39) | 345.4 | 152.6 | 0.442 | 713.7 | 481.8 | 0.675 | 14.4 → 23.8 |
| Review fix (new = final) | 663.1 | **396.1** | 0.597 | 743.7 | **493.8** | **0.664** | 13.6 → **84.6** |

- **CPU:** the new code uses about one third less in every pair (ratios 0.661, 0.675, 0.664). The fixes did not change that.
- **Wall:** this depends on the cores a world can get.
  - At the loads of pairs 1–2, and in the other new worlds (loads up to about 60), every new world finished in **≤ 166.5 s**. The slowest unaudited one took 152.6 s, rule value **4578.8 s ≤ 10800**.
  - In the review-fix pair, the machine reached a 1-minute load of 85 on 10 CPUs. Each world got only about 1.1–1.25 cores. The final code took **396.1 s** (rule value 11884.2 s, above the limit) and the old code 663.1 s.
- **Requirement:** the new engine stays under 360 s while a world gets on average at least 493.8 / 360 ≈ **1.37 cores**. The old one needs ≥ 743.7 / 360 ≈ 2.07 cores, and its structure cannot use more than about 2.1.

## 1. Profile: where the time went (old code, smoke world 0)

**Method.** `sample` and `xctrace` cannot attach to the hardened system Python (`task_for_pid` is refused). The profile therefore uses built-in timers:

- a scratch harness, `profile/tools/profile_world.py`, wraps the native `field_run` entry and the Python hot spots. It records per-thread CPU (`thread_time`), wall time, scheduler barriers and a SHA-256 of every native call's complete input bytes;
- a C++ microbenchmark (`profile/tools/micro.cpp`) and a kernel A/B bench (`profile/tools/bench.py`) cover the native law.

The harness used the unchanged option-B code (`profile/baseline/`). That world took 323.8 s wall and 688.7 s CPU, at load about 8 to 10.

| Hotspot (CPU, all threads) | CPU s | Share |
|---|---:|---:|
| Native integration of distinct OFF single-cohort material (passive sources, unselected controls) | 366.2 | 53.2% |
| Native **re-integration of byte-identical OFF material**: missed because the memo was thread-local or still in probation | 113.5 (+4.2 in real hits) | 17.1% |
| Native no-cohort actual-medium runs: distinct 10.2 s, **byte-identical repeats 42.7 s** | 52.9 | 7.7% |
| Native emitting (ON) cohorts | 30.8 | 4.5% |
| Python outgoing channels (`F.emissions`): numpy Gaussian/phasor recomputed after evictions from a 16 MiB cache | 73.2 | 10.6% |
| Python wrappers on workers (advance, arguments, pack/unpack, validate, clone, identity) | 15.7 | 2.3% |
| Coordinator Python (merging, trace hashing, `state_errors` 7.5 s, detection/persistence about 9 s, descriptors, snapshots) | 32.3 | 4.7% |

Across the whole world, 4,946 of 9,758 native calls repeated an input that had already been computed. They cost **161 s, 23% of all CPU**.

**Inside the native law.** One material evaluation (24 members, 25 sites) makes:

- about 876 `exp` calls (3.16 ns each);
- about 300 `__sincos_stret` calls (6.13 ns each).

That is about 4.6 µs of roughly 7.4 µs, so about 62% of the evaluation is libm. Exact equality forbids vector libm, so the scalar evaluator is close to its exact floor.

**Thread use.** CPU/wall was **2.13** out of 5 threads. The time divided into barriers as follows:

| Barrier kind | Barriers | Wall s | Share of 324 s |
|---|---:|---:|---:|
| One scope, 3 grid jobs (formation, exposure, descriptor probes) | 858 | 211.6 | 65% |
| Recovery, 6 jobs | 126 | 66.4 | 21% |
| Causal, 24 jobs | 42 | 37.6 | 12% |

A one-scope block cannot finish before its dt/4 grid, which is 4/7 of the block's work. So the 4 workers were mostly idle while the 19 independent formation episodes and the 3 treatment conditions of each turn ran one after another.

Serialization (about 7 s) lies outside the world time.

## 2. What changed, and why it is exact

These are ranked by measured gain. Every change keeps each floating-point operation's operands, order and libm function, or returns a byte-for-byte copy of a value computed earlier from byte-identical inputs. Compiler flags are unchanged: `-std=c++17 -O2 -fno-fast-math -ffp-contract=off`.

1. **Process-wide exact native caches** (`native/c6_option_b/field.cpp`). The thread-local material memo, its probation list and the drive cache are replaced by three **shared, single-flight stores**:
   - material, 1 GiB, the same envelope as the old 4 × 256 MiB;
   - no-cohort actual medium, 64 MiB, new;
   - drive, 128 MiB, the same as 4 × 32 MiB.

   Each store is indexed by an FNV hash, and equality is always a full comparison of the complete byte key. A thread that requests a key being computed waits for that leader instead of recomputing. A failed leader publishes failure exactly once, and one waiter then leads again. Every input still participates in the key.

   No-cohort runs are now memoized too, including the actual medium recomputed on every material hit (with z = 0 that medium is identical for all passive cohorts in a block).

   Measured effect, using the same harness: CPU 688.7 → 516.4 s, and native CPU spent on repeated inputs 161 → 8 s (`profile/shared_caches/`).

2. **Concurrent protocol tasks** (`geomind/c6_option_b_parallel.py`, `parallel_operation`). `P.operation` is selected, like `GridSet`/`recovery`/`causal`, by a port that runs each turn's independent tasks concurrently:
   - **stage 1:** the 3 treatment conditions (exposure, persistence, endpoint qualification);
   - **stage 2:** the 4 response descriptors and, when the turn is eligible, the 4 before-formation and 15 condition episodes.

   Each task writes a **private checks list**. The lists are joined in the original order, and the first failure in that order is re-raised after exactly the checks the sequential loop would have made. Branches and the continuation grid are re-pointed to the shared list, as `grid.clone()` and `introduce()` do.

   A **coordinator compute token** keeps at most 5 threads computing at once: the 4 grid workers plus the one coordinator holding the token. Up to 4 protocol-task threads exist, but they compute only while holding the token and release it around every wait. Nested task batches are refused.

   Stage 2 took 53.4–182.7 s per turn over all new runs (§4). CPU/wall rose from 2.1 to 3.2–3.5 at moderate load.

3. **Exact evaluator restructuring** (`evaluate`):
   - pair and site arguments are formed first, `__sincos`/`exp` run back to back, and accumulation then runs in the original ascending order;
   - terms that are exact signed zeros are skipped only when their operands are finite: J = 0 for modes 1 and 3, K = 0 for mode 1, and emission terms whose every mask is ≤ 0. Nonfinite operands keep the original evaluation, so error codes are kept;
   - mode-2 origin Gaussians are computed once per run.

   The original build already merged each sin/cos pair into `__sincos_stret`; this file calls that same entry explicitly. Kernel bench, bit-identical in every case (ratio of new to old time):

   | Case | Ratio |
   |---|---:|
   | Intact or OFF cohorts | 0.85–0.89 |
   | Mode 2 | 0.71 |
   | `no_r` | 0.59 |
   | All cases | 0.83 |

4. **Split OFF material misses.** On a cache miss, the OFF material is integrated without the actual medium, which it never reads. The actual medium is taken from the shared no-cohort store; its derivative here gets only exact signed-zero emissions and so equals the no-cohort law, as on a hit.

   If the material run fails, the original inline integration decides the error code. A dedicated test covers every combination of material and medium failure. The gain is about 2% (bench with a warm medium store).

5. **Python cache budgets.** Inside the native backend, the existing exact emission cache gets 128 MiB instead of 16 MiB, and the passive cache keeps 64 MiB. Retained bytes are tracked incrementally instead of summed on every insert.

   Simulation on the logged keys (`profile/concurrent/pycache.jsonl`, `lru_sim.py`): 128 MiB keeps all 414 distinct channels. It saves about 23 s of channel recomputation in a world.

The FNV index, the store accounting and the cost counters are bookkeeping only. `computed_*_steps` and `*_single_flight_waits` are reported in COSTS.json.

## 3. Changes that would alter floating-point results (flagged, not implemented)

Each would need a declared tolerance under decision 0029 item 3 and the owner's approval, because the strict-equality contract would end:

- vector libm (Accelerate vForce, SLEEF) for `exp` and `sincos`. These dominate the remaining native time, and the gain could be about 30–40% of native CPU. V1 measured last-bit differences up to 8e-15;
- separable site Gaussians on the 5×5 lattice, exp(a+b) = exp(a)·exp(b): 600 → 240 `exp` calls per evaluation;
- reciprocal multiplication instead of division, FMA contraction, or `-ffast-math`;
- sharing outgoing channels between numpy and native code, which use different `exp` implementations.

## 4. Before and after (same conditions, back to back)

**Pairs.** The old arm is a detached worktree of 8214f39^ / f7e4a7d: option-B sources `124c0381…`, the same as the 392 s quiet session, built in place. The pairs are tabled in the Summary. CPU/wall (old → new) was 2.127 → 3.471 in pair 1, 2.066 → 3.157 in pair 2, and 1.122 → 1.247 in the overloaded review-fix pair.

**Other new-code worlds** (8214f39 arithmetic; run two at a time):

| World | Wall s | CPU s | Rule value s (≤ 10800) | Load (1 min) start → end |
|---|---:|---:|---:|---|
| Smoke 0, reverse schedule | 152.2 | 474.3 | 4564.6 | 38.2 → 33.0 |
| Smoke 1, with full audit | 166.5 | 523.5 | 4994.6 | 10.4 → 42.4 |
| Development 0 | 96.0 | 260.6 | 2879.3 | 10.4 → 47.9 |
| Development 1 | 93.9 | 249.6 | 2815.8 | 38.2 → 59.9 |

**Concurrent stage walls** (all new runs, every batch):

- stage 1 (3 tasks): 8.4–23.5 s;
- stage 2 (23 tasks): 53.4–182.7 s.

The upper ends come from the overloaded review-fix world.

**Memory.** Post-serialization peak RSS, in GiB:

| Code | Peak RSS |
|---|---:|
| New, 8214f39 | 1.92–2.49 |
| Final | 2.23 |
| Old | 1.45–1.99 |

**What bounds memory.** Retained native values are bounded per store: material 1 GiB, medium 64 MiB, drive 128 MiB, the same envelope as before plus the medium store. Beyond that:

- **Native, per in-flight call:** optional allocation is at most one admissible value. Nothing optional is allocated when a store is disabled, and allocation failures fall back (F2).
- **Python:**
  - passive and emission caches: 64 + 128 MiB of array payload; keys and containers are extra;
  - at most 4 submitted grid jobs per coordinator, and at most 4 coordinators, so ≤ 16 jobs submitted (all measured runs reached 16). A result is merged as soon as its block's three grids finish;
  - the full flows of at most one block per in-flight request;
  - serialization buffers.

These counters are not an RSS cap. The measured peaks above are the evidence. The machine has 32 GiB. Knobs: `O.CACHE_LIMITS`, `O.EMISSION_CACHE_BYTES`, `TASK_COORDINATORS`.

## 5. Equivalence

**Full worlds.** Each world was compared with `tools/c6_option_b_compare.py --exact`: tolerance 0, float bit/type checks, digests unchanged, every Boolean and discrete value included.

| Output | Reference | Numeric values | Boolean values | Max error | Digests changed |
|---|---|---:|---:|---:|---:|
| ab1_new_smoke_0, ab2_new_smoke_0, new_smoke_0_reverse | reference_smoke_0 | 3,045,093 each | 2,847 | 0 | 0 |
| new_smoke_1_audit | reference_smoke_1 | 1,460,200 | 1,396 | 0 | 0 |
| new_development_0 | profile_run/reference_world_000 | 2,601,660 | 2,512 | 0 | 0 |
| new_development_1 | quiet_session…/reference_development_1 | 2,600,554 | 2,501 | 0 | 0 |
| ab1_old_smoke_0, ab2_old_smoke_0 (control) | reference_smoke_0 | 3,045,093 each | 2,847 | 0 | 0 |
| fixes/fixed_smoke_0 (final code) | reference_smoke_0 | 3,045,093 | 2,847 | 0 | 0 |

All pass. Smoke 0 completed its chain; the other worlds ended without a chain, as before; `invalid` is null everywhere. So the concurrent operation port ran both its eligible and its non-eligible path.

**Per-call audit (smoke 1).** 3,863 of 3,863 returned full arrays (796,159,608 float64 values) are bit-identical to the original kernel on identical inputs, including every cache hit and every split-path result. All 30,558 detector calls matched.

**Profiling worlds.** Two more smoke 0 worlds also pass exactly: `profile/shared_caches/prof_v6_EXACT.json` and `profile/concurrent/prof_v7_EXACT.json`.

**Tests.** For 8214f39, `tests/test_c6_option_b.py` and `tests/test_c6_option_b_parallel.py` gave **110 passed**. For the final code they give **128 passed**, adding the F1–F3 contracts in §0. The new contracts are:

- concurrent operation equals sequential operation at tolerance 0, for forced-eligible with continuation, non-eligible, NO-R failure, and injected failures in stage 1, stage 2 and the before-episodes;
- the coordinator token bounds Python to one coordinator; nested task batches are refused;
- shared single-flight stores are exact under 4-way concurrency, with exact miss and hit counts;
- the C++ store is tested under allocation failure, leader failure, follower wait and byte limits;
- nonfinite raw-boundary inputs keep their codes for all modes;
- the split path keeps every failure code;
- the pressure and churn tests run on the shared limits.

`tools/c6_option_b_recheck.py` was updated for the process-wide API and passes on the final build: 342 calls and 1,357,236 values, all bit-compared (`performance_deepdive/recheck_tool/CHECKS.json`).

## 6. Remaining opportunities (exact)

- **Python overhead,** about 60–70 s per world:
  - coordinator merging, trace hashing, `state_errors`, detection and persistence statistics;
  - worker wrappers (about 34k `validate` calls);
  - emission digests.

  Porting these to typed code with numpy-identical arithmetic could save about 10% of CPU.
- **Drive recomputation:** 2.8 M drive steps were computed (about 10 s). A larger or time-indexed drive store could trim 1–2%.
- **Parallelism:** batching the recoveries of several structural candidates, or pipelining coarse grids ahead within a scope, would only shorten the short sequential parts (the initial source episode and stage 1, about 22 s of the 134 s world).
- **Scheduling:** tuning `TASK_COORDINATORS` (4) against memory.

## 7. Owner recheck applied to this work

The owner's prompt, verbatim: "Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps." No numeric score is assigned here (AGENTS.md); these are the findings.

**Fixed before the final measurement:**

- **Gap:** OFF material misses still integrated the actual medium inline. They are now split (item 2.4), with an exact fallback for failure codes and a test.
- **Conflict:** `tools/c6_option_b_recheck.py` used the old per-thread 4-limit API and reset per-worker caches. It now uses the process-wide API, with concurrent churn under shared limits.
- **Robustness:**
  - the parallel context released the coordinator token unconditionally on exit; it now releases it only if held;
  - the signed-zero emission skip now explicitly requires a finite output scale;
  - new tests cover nonfinite phases, positions and output scale for every mode.
- **Gap:** the emission-cache budget was chosen from the logged keys instead of guessed.

**Fixed after the measurement:** a nested `run_tasks` call from a task thread could exhaust the task pool, so it is now refused (guard and test). This one-line guard is the only difference between the measured `c6_option_b_parallel.py` (`6da954ad…`) and the final one (`76fc4d3e…`). Every other measured source is identical to the final source: `field.cpp` `2625a7ef…`, binary `a90ba072…`.

**Disclosed:**

- **Memory:** about +0.5 GB RSS per world (§4).
- **Process rule:** `c6_option_b_parallel.py` was edited while the scratch profiling run v6 was in progress. That run had already imported the module, so its results were unaffected, but this broke the rule of no edits during long runs. No edits were made during any later run.
- **Binary hash:** rebuilding identical sources gives a new binary hash (Mach-O UUID). The old arm's binary is `b1685fa5…` from sources `124c0381…`.
- **Load:** every timing here ran under other heavy jobs, at load 7–60. Wall comparisons are valid only within a pair; CPU is the robust measure.
- **Unchanged semantics:**
  - `-0.` replay guard: the medium derivative adds the forcing last and so is never `-0.`. The guard that replays such entries is therefore expected never to trigger, and it is kept as a safeguard;
  - hits: as before, the actual medium on a material hit comes from the no-cohort law.

### Owner recheck applied to the review fixes

The owner's prompt, verbatim: "Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps."

**Findings and actions:**

- **Do the tests detect the defect?** They were run against the reviewed module. 8 of the 11 new recovery/fuzz tests fail there, and the reviewed native code fails the peak contract (3.27 MB). So they are real regression tests, not tautologies.
- **Statement order at set-up.** `run_many` evaluated its set-up statements in a different order from `GridSet.run` (scales before `pack`). It now follows `GridSet.run` exactly (`_initial_state`).
- **Nested coverage.** The first fuzz of the operation landed almost always in the first descriptor. Input-only gates (`only=`) now steer failures into stage-1 runs and into episode formation and recovery runs, and the positions were checked.
- **Causal fork set-up** still runs before the runs. It is equivalent because its only raising statement is identical for all forks; this is documented in code.
- **Not changed:**
  - Python-side memory is still bounded structurally, not by a byte cap (§4);
  - after a failed task or request, its concurrent siblings run to completion: the work is wasted but has no effect;
  - the 360 s margin depends on the cores available (§Summary). Under the load 42–85 of the review-fix pair, neither engine met it.

## 8. Files

**Changed:**

- `native/c6_option_b/field.cpp`
- `geomind/c6_option_b.py`
- `geomind/c6_option_b_parallel.py`
- `tools/c6_option_b_check.py` (metadata)
- `tools/c6_option_b_recheck.py`
- `tests/test_c6_option_b.py`
- `tests/test_c6_option_b_parallel.py`

**Review fixes:**

- `geomind/c6_option_b_parallel.py` (Outcome/publish, ordered merge);
- `native/c6_option_b/field.cpp` (`admits`, streaming drive, direct strided medium, allocation fallbacks, publication order);
- both option-B test files;
- `performance_deepdive/REPORT_VALUES.py` and `.json`;
- `performance_deepdive/fixes/` (RUN_PAIR.py, EVENTS, START/COSTS, EXACT, recheck_tool).

**New evidence:** `evidence/c6_option_b/performance_deepdive/`, containing:

- `RUN_MEASUREMENTS.py`, `SUMMARIZE.py`, `MEASUREMENTS.json`, `EVENTS.jsonl` (load samples);
- per-world `START.json` and `COSTS.json`, and the `*_EXACT.json` comparisons;
- `profile/` (baseline, shared_caches, concurrent; tools);
- `recheck_tool/`.

World dumps and logs stay outside git, as before.

**Unchanged:** all C0–C5 and R4 sources (source pin PASS in every run), the comparator, the build flags, STATUS.json and every receipt.
