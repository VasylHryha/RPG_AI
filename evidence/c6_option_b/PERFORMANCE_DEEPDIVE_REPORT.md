MEETS_360_WITH_MARGIN (engineering observation; not a registered readiness verdict)

# C6 option B: performance deep-dive

**Date:** 2026-10-06. **Author:** Claude (claude-opus-5-5).
**Authority:** decision 0029 (engineering and runtime work, exact equivalence; the science is unchanged). Runs under one hour need no approval (decision 0031).
**Not done:** final entropy, registration, STATUS.json, mutation probe, recorded panel, or any change to C0–C5 or R4 files. C6 stays `BLOCKED / R006 STOP`.

## Summary

On smoke world 0, two back-to-back A/B pairs ran the old and new code at the same time, so both saw the same load. Compared with the code that produced the 392 s quiet-session failure:

- **world wall time fell by 56–59%:** 329.5 → 133.5 s and 345.4 → 152.6 s;
- **compute CPU fell by 33–34%:** 700.8 → 463.3 s and 713.7 → 481.8 s.

All 8 complete worlds produced in this work match their stored original-reference worlds **at zero tolerance**. That covers smoke 0 three times (two schedules), smoke 1 with the full per-call audit, development 0 and development 1. The two old-code outputs also match.

The slowest unaudited new world took **152.6 s**, under a machine load of 14–24 on 10 CPUs. The rule value is 152.6 × 40 / 2 × 1.5 = **4578 s ≤ 10800**, leaving 2.4× headroom against the 360 s limit. The audited smoke world 1 took 166.5 s; its audit re-runs the reference kernel on every call.

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

   In the final runs, stage 2 took 53–58 s per turn, and CPU/wall rose from 2.1 to 3.2–3.5.

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

Each pair ran the **old** code and the **new** code as two world processes at once. The old code was a detached worktree of commit `f7e4a7d`; its option-B sources hash to `124c0381…`, the same as the quiet session. Both processes used the declared 5-thread budget, smoke world 0, forward schedule, no audit. Other heavy jobs ran on the machine throughout.

| Pair | Old wall s | New wall s | Wall ratio | Old CPU s | New CPU s | CPU ratio | CPU/wall old → new | Load (1 min) start → end |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 (old launched first) | 329.5 | **133.5** | 0.405 | 700.8 | **463.3** | 0.661 | 2.13 → 3.47 | 6.8 → 13.5 |
| 2 (new launched first) | 345.4 | **152.6** | 0.442 | 713.7 | **481.8** | 0.675 | 2.07 → 3.16 | 14.4 → 23.8 |

Further new-code worlds were run two at a time (each COSTS.json records its load):

| World | Wall s | CPU s | Rule value s (≤ 10800) |
|---|---:|---:|---:|
| Smoke 0, reverse schedule | 152.2 | 474.3 | 4566 |
| Smoke 1, with full audit | 166.5 | 523.5 | 4995 |
| Development 0 | 96.0 | 260.6 | 2880 |
| Development 1 | 93.9 | 249.6 | 2817 |

**Against the 360 s rule.**

- The slowest unaudited new world is 152.6 s. Every new world, audited included, is ≤ 166.5 s.
- To stay under 360 s, the new engine needs on average **482/360 ≈ 1.3 cores per world**.
- The old engine needed 714/360 ≈ 2.0 cores. Its structure could not use more than about 2.1, so it passed only when it got almost all of its structural maximum. That is why it measured 329.5/345.4 s here and 392 s in the quiet session.
- The new engine can use about 3.5 cores and needs about 1.3, which gives the margin the owner asked for on a normally busy laptop.

**Memory.** Post-serialization peak RSS was 2.0–2.55 GB, against the old 1.68–2.04 GB on smoke 0, so about 0.5 GB more per world. The cache envelope is unchanged. The increase comes from:

- the larger emission cache (+112 MiB);
- the new medium store (+64 MiB);
- concurrent tasks' in-flight flows.

The machine has 32 GiB. The knobs and their simulated cost are `O.CACHE_LIMITS`, `O.EMISSION_CACHE_BYTES` and `TASK_COORDINATORS`. For example, a 768 MiB material store costs about 2.5% CPU.

## 5. Equivalence

**Full worlds.** Each world was compared with `tools/c6_option_b_compare.py --exact`: tolerance 0, float bit/type checks, digests unchanged, every Boolean and discrete value included.

| Output | Reference | Numeric values | Boolean values | Max error | Digests changed |
|---|---|---:|---:|---:|---:|
| ab1_new_smoke_0, ab2_new_smoke_0, new_smoke_0_reverse | reference_smoke_0 | 3,045,093 each | 2,847 | 0 | 0 |
| new_smoke_1_audit | reference_smoke_1 | 1,460,200 | 1,396 | 0 | 0 |
| new_development_0 | profile_run/reference_world_000 | 2,601,660 | 2,512 | 0 | 0 |
| new_development_1 | quiet_session…/reference_development_1 | 2,600,554 | 2,501 | 0 | 0 |
| ab1_old_smoke_0, ab2_old_smoke_0 (control) | reference_smoke_0 | 3,045,093 each | 2,847 | 0 | 0 |

All pass. Smoke 0 completed its chain; the other worlds ended without a chain, as before; `invalid` is null everywhere. So the concurrent operation port ran both its eligible and its non-eligible path.

**Per-call audit (smoke 1).** 3,863 of 3,863 returned full arrays (796,159,608 float64 values) are bit-identical to the original kernel on identical inputs, including every cache hit and every split-path result. All 30,558 detector calls matched.

**Profiling worlds.** Two more smoke 0 worlds also pass exactly: `profile/shared_caches/prof_v6_EXACT.json` and `profile/concurrent/prof_v7_EXACT.json`.

**Tests.** `tests/test_c6_option_b.py` and `tests/test_c6_option_b_parallel.py` gave **110 passed** in one final run after the last change (25 s). The new contracts are:

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

## 8. Files

**Changed:**

- `native/c6_option_b/field.cpp`
- `geomind/c6_option_b.py`
- `geomind/c6_option_b_parallel.py`
- `tools/c6_option_b_check.py` (metadata)
- `tools/c6_option_b_recheck.py`
- `tests/test_c6_option_b.py`
- `tests/test_c6_option_b_parallel.py`

**New evidence:** `evidence/c6_option_b/performance_deepdive/`, containing:

- `RUN_MEASUREMENTS.py`, `SUMMARIZE.py`, `MEASUREMENTS.json`, `EVENTS.jsonl` (load samples);
- per-world `START.json` and `COSTS.json`, and the `*_EXACT.json` comparisons;
- `profile/` (baseline, shared_caches, concurrent; tools);
- `recheck_tool/`.

World dumps and logs stay outside git, as before.

**Unchanged:** all C0–C5 and R4 sources (source pin PASS in every run), the comparator, the build flags, STATUS.json and every receipt.
