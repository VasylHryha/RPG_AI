# C6 option B, round 2: research and measurement memo

**Date:** 2026-10-06. **Author:** Claude (claude-opus-5-5), research agent.
**Status:** engineering research only. No repository file was edited. Every experiment ran in a scratch copy made with `git archive` of commit 978e4dd. No final entropy was used, nothing was registered, and no gate was touched.
**Scratch root:** `/private/tmp/claude-501/-Users-new-RiderProjects-ai-RPG-test/266628b5-c225-443d-b8f6-8f99d66d38db/scratchpad/`, abbreviated `$S` below.

## 0. Decision in one paragraph

Only two exact levers are worth more than 1%. One is run-level deduplication of identical material trajectories (3–6% of world CPU). The other is Python bookkeeping (a pool of about 13–15% of world CPU, of which perhaps 5–8% can be recovered exactly, at high verification cost).

Per-call transcendental memoisation, skipping provable zeros, SoA/exact SIMD and a disk cache each give ≤1% or nothing. This is measured, not assumed.

Inexact vector libm plus separable Gaussians cuts world CPU by **26%** with **0 decision flips in 3 worlds**. But the exact engine already meets the 360 s rule with about 2.4× headroom. So I recommend **not** asking the owner for a tolerance now. I prepared one (section 7) in case the time budget ever needs it.

## 1. Method and conditions

**Machine load.** The machine was heavily shared during all runs: load 20–93 on 10 cores. Every comparison is either a bitwise check or a CPU-time ratio from runs launched together. I quote no absolute wall time as a result.

**Instrumented world.** A copy of `field.cpp` counted every exp and sincos argument by bit pattern:
- repeats within an evaluation;
- repeats in the same slot as in the previous evaluation;
- repeats within the last 8 evaluations;
- world-wide repeats, from a consistent 1/4096 hash sample, split into same-run and cross-run.

It also counted:
- arguments in the zero, subnormal and <−36/−20/−10 ranges;
- accumulator additions that changed nothing (`acc+t==acc`);
- one log line per `field_run` call, carrying six byte-key hash variants and thread CPU.

It ran smoke world 0 (forward, 5 threads). The output matched `reference_smoke_0` **at tolerance 0**: 3,045,093 values and 2,847 decisions. So the instrumentation did not perturb the arithmetic.
- Files: `$S/runs/smoke0.json` (counters), `$S/runs/smoke0.jsonl` (8,672 calls), `$S/analyze.py`, `$S/policy.py`.

**Kernel benches:**
- `$S/bench/bench.py`: Python A/B over 10 owner cases (ON/OFF, modes 0–3), with bitwise frame equality.
- `$S/bench/drv.cpp`: a C++ driver that calls `field_run` on the 1-cohort OFF case, 1600 steps, CPU µs per evaluation. Unlike the hardened Python it can be profiled with `sample` (`$S/bench/sample.txt`).

**World A/B (smoke 0).** Three worlds launched together:
- `repo0`: clean HEAD;
- `repo3`: the exact run-level candidate;
- `repo2`: the inexact vForce+separable kernel.

Then smoke 1 and development 0 for `repo2`, and smoke 1 for `repo3`.

**Web research.** A sub-agent read the primary sources (links in section 9). I re-checked the claims that carry weight, and two were checked by measurement here.

## 2. Where the time is (baseline, per smoke-0 world)

| Quantity | Value |
|---|---|
| World CPU / wall (`repo0`, load 21→61) | 468.3 s / 222.5 s |
| Material evaluations actually computed (cohort-evals) | 56.5 M (modes 0/1/2/3: 46.7/2.7/2.4/4.7 M) |
| exp calls | 47.46 G (pair 14.84 G, site 32.49 G, own 0.13 G) |
| sincos calls | 16.19 G (pair 14.84 G, phasor 1.36 G) |
| CPU ns per call (quiet microbench, min of 15) | exp 2.56, `__sincos_stret` 4.92 |
| libm share of one evaluation (`sample`, C++ driver) | about 55%, including 7.4% in dyld stubs |
| Non-libm floor (libm replaced by cheap stubs) | 2.9 of 6.7–7.3 µs per evaluation (43–47%) |
| Python CPU (round-1 report) | about 60–70 s per world |

## 3. Item-by-item evidence

### Item 1. Exact memoisation of repeated transcendental arguments

**Measured on smoke world 0:**

| Category | Repeats within an evaluation | Same slot as previous evaluation | Cross-run repeats (sampled) |
|---|---:|---:|---:|
| Pair exp | 0 | 652.7 M (4.40%) | 13.8% |
| Site exp | 0 | 361.5 M (1.11%) | 12.3% |
| Pair sincos | 0 | 74.4 M (0.50%) | 10.1% |
| Phasor sincos | 0 | 1.7 M (0.12%) | 9.9% |

Same-run repeats that are not adjacent are negligible.

**Explanation:**
- The 4.40% of pair exp is exactly the mode-2 pairs: 2.352 M mode-2 evaluations × 276 = 649 M. Their argument `-(wx²+wy²)` uses fixed origins, so it is constant for the whole run. The code caches the mode-2 *site* weights but not these pair weights.
- The 1.1% of site exp comes from members whose position did not change bitwise within an RK stage, because the update was below half an ulp.
- The cross-run repeats are mostly whole-trajectory redundancy (see "Run-level" below), plus mode-2 constants that first appeared in a mode-0 run at the same positions.

**Gain:**
- Mode-2 pair-Gaussian cache: trivial and exact, like the existing `fixed_w`. It saves 649 M × 2.56 ns ≈ **1.7 s/world (≈0.35% CPU)**.
- Per-member "position unchanged, skip its 25 site exps": ≤1.3 s gross, minus the compare cost, so **≤0.2% net**.

**Run-level (the same idea one level up).** I simulated policies on the call log with unlimited memory:
- **A.** The OFF material key ignores masks and the output scale: 2.95% of heavy native CPU.
- **B.** A, plus single-cohort ON runs publish their material columns under the same key: 6.49%.
- **C.** B, plus prefix/resume for shorter or longer horizons: 6.85%.
- **C0.** Prefix/resume alone: 0.75%.

**Why A and B are exact (by code inspection):**
- For an eligible cohort (all masks ≤ 0), masks enter `evaluate` only through `selected`/`silent`/`emit` and the emission terms. Those write only the actual medium, which the material run never reads.
- An ON cohort's material and carrier derivatives are the same expressions as an OFF cohort's. Emission writes only `out[0,2ns)`, and the RK update is per element.
- **Test.** I built **B** (`$S/exact_candidate.patch`, 35 lines). It is **bit-identical at tolerance 0** on smoke 0 (3,045,093 values, 2,847 decisions, 0 digests changed) and smoke 1 (1,460,200 values, 1,396 decisions).
- **Measured (smoke 0, launched together with `repo0`):**
  - computed material RK steps: 13.23 M → 12.67 M (−4.2%);
  - CPU: 468.3 → 454.3 s (**−3.0%**);
  - wall: 222.5 → 217.5 s;
  - RSS: 2.48 → 2.36 GB.
- **Why less than simulated:** the 1 GiB material store is full (1.07 GB retained) and evicts. Python's own passive cache is also keyed by identity, which includes the selection.
- **Noise:** same-code CPU varied ±2–4% in round 1 (463 vs 482 s). One pair does not prove 3%. It shows a 3–6% effect in the right direction.

### Item 2. Skipping work that provably cannot change results

**Measured (smoke world 0, all evaluations):**
- **Exact zeros and underflow:** 0 exp arguments below −745.13 (result 0) and 0 below −708.40 (subnormal).
- **Small arguments:** 0 below −36. Only 0.11% of pair arguments are below −20 and 2.7% of site arguments below −10. Every member is within reach of every site: lattice ±4, σ=2, so the weights are ≥ e^−20 (0 site arguments were below −20).
- **Additions with no effect:**

| Accumulator | Ineffective additions |
|---|---|
| Coupling (`vt`) | 6 of 14.8 G |
| Weight denominator | 0 of 33.9 G |
| Complex `g` | 0 of 33.9 G |
| Force (all 4 components) | 0 of 15.6 G |

Round 1 already removed the exact signed-zero work (J=0, K=0, silent emission).

**Gain: zero. Skip.** "Out of reach" does not exist in this geometry. A bound-based skip would also need a proof of each accumulator's ulp at each point of the order, for no benefit.

### Item 3. Data layout (SoA, no allocations, locality)

**Measured.** Workspace is already allocated once per integration, and the evaluator scratch is contiguous. Clang already auto-vectorises the pair-argument and site-argument loops in the current file (`-Rpass=loop-vectorize`).

**Prototype.** I wrote an exact SoA evaluator (`$S/bench/var/field.cpp`) with these features:
- x/y copied to separate arrays;
- vectorisable pair-term arrays, then a scatter in the original order;
- transposed site weights;
- members accumulated as lanes, each sequential over sites in the original order;
- a fallback to the original for mode 2, emission and nonfinite inputs.

**Results:**
- **Bit-identical** in all 20 bench cases.
- **Slower:** total ratio 1.04–1.07. OFF intact/mode-3 runs were 1.11–1.29 slower in the floor-only build.

### Item 4. Exact vectorisation of the arithmetic around the math calls

**Where the non-libm time goes.** The `sample` profile shows no single hotspot:
- pair force line 7%;
- pair arguments 4.7%;
- compiler-attributed code 11%;
- medium 3.4%;
- finite scan 1.4%.

**Ablations (timing-only builds):**
- removing every division and sqrt saves about 1–3%;
- removing the whole site accumulation saves about 5%;
- calling exp and `__sincos_stret` directly through `dlsym` pointers to bypass the dyld stub: ratio 0.99, which is noise.

The literature agrees that per-lane IEEE operations without reassociation or FMA are bit-identical (SLEEF paper; Intel FP-consistency guide). The constraint is the gain, not exactness.

**Gain for items 3–4 together:** the theoretical ceiling is the 43–47% floor. My prototype gave 0 or negative, and a careful hand-tuned version might reach 3–8%. Uncertain, and each step needs bit-proofs. **Skip in round 2.**

### Item 5. Porting Python bookkeeping to C++, and a disk cache

**Python pool.** About 60–70 s per world (13–15% of CPU). Largest items in the round-1 `concurrent/PROFILE.json`:
- `emissions` 48 s, of which compute 36 s (the final 128 MiB cache removes about 23 s; the rest is hashing and numpy);
- `state_errors` 10.6 s;
- worker `validate` 6.5 s over 33,654 calls;
- `unpack` + `clone` + `arguments` + `pack` about 13 s;
- window statistics and rolling persistence about 10 s.

**Exactness traps found here:**
1. NumPy float64 `exp`/`sin`/`cos` equal Apple scalar libm: 0 mismatches in 10⁶. NumPy's source says float64 trig and exp "revert to libm" on arm64. `np.exp(1j*x)` equals separate `cos`/`sin`.
2. **But `__sincos_stret`'s sine differs from `sin()`.** It differs on 0.8–1.4% of arguments with |x| < 1 and on 0.2% with |x| < 7. Cosine is identical. This contradicts Apple's 2017 statement that they are equal.
   - So native phasors ≠ NumPy phasors in about 1% of sines. This is the real cause of the round-1 note "numpy and native use different exp".
   - A C++ port of Python code must call `sin` and `cos` **separately and stop clang merging them into `__sincos_stret`**, for example with `-fno-builtin-sin`/`-cos` or calls through volatile pointers.
   - Conversely, the native kernel must never replace `__sincos` with `sin`, for instance when only the sine is needed (mode 3).
3. `np.sum`/`np.mean` use pairwise summation along contiguous axes (8-way unrolled blocks per the NumPy source as I recall it; verify against the installed version). A port must replicate that order exactly.
4. The R4 Python modules are source-pinned. A port can only enter through option-B substitution points, like `F.native`/`F.cached_array` today.

**Expected exact gain:**
- about 25–40 s CPU (5–8%) if `emissions` hashing/compute, `state_errors` and the worker wrappers are ported;
- possibly more in wall time if the GIL is the limit. **This is unmeasured; measure GIL hold time first.**

**Disk cache: no gain for the panel.**
- Every world draws its own medium from (entropy, world), so cross-world key overlap is zero by construction.
- Panel worlds run once.
- A cache keyed by binary hash is invalidated by every rebuild, which is exactly when you would re-run.
- It could also mask a kernel change during verification. **Skip.**

### Item 6. Faster math that changes last bits

**Microbench** (CPU ns per element, cache-resident arrays, min of 15):

| | exp | sincos |
|---|---:|---:|
| Scalar libm | 2.56 | 4.92 |
| Accelerate vForce | 1.67 | 1.95 |

**Bitwise agreement with Apple scalar libm:**

| Function | Arguments differing | Max error |
|---|---:|---|
| `vvexp` | 26.0% | 1 ulp |
| `simd::exp(double2)` | 26.0%, the same cases as `vvexp` | 1 ulp |
| `vvsincos` | about 63–65% | ≤3 ulp |
| Separable exp(a)·exp(b) vs exp(a+b) | 51.9% | ≤33 ulp (a, b ∈ [−20, 0]) |

**Kernel (C++ driver, CPU per evaluation):**
- vForce: **0.73×**;
- vForce + separable 5×5 site Gaussians (240 instead of 600 exps): **0.68×**.

**World (smoke 0, launched together with `repo0`):**
- CPU 468.3 → **345.5 s (−26.2%)**;
- wall 222.5 → 166.4 s (−25.2%);
- the chain still completed.

**Deviation from the stored references:**

| World | Decisions flipped | Max abs. numeric deviation | Values > 1e-10 |
|---|---|---:|---:|
| Smoke 0 | 0 / 2,847 | 4.3e-10 | 6 |
| Smoke 1 | 0 / 1,396 | 4.3e-11 | 0 |
| Development 0 | 0 / 2,512 | 5.1e-10 | 2 |

- About 50% of numeric values differ in their last bits.
- Every state-identity digest changes: 8,558 on smoke 0.
- The largest deviations are on grid-error diagnostics, for example 1.314e-7 → 1.319e-7 against a limit of 0.05.
- In the kernel bench, trajectory differences grow with horizon: 4e-16 at T=2, 3e-15 at T=20, 1e-13 at T=60. The dynamics amplify last-bit changes.

**Correctly-rounded libraries are not an exact route:**
- Apple libm is *not* correctly rounded. Against mpmath at 120 bits, exp is wrong in 0.16% of arguments in [−60, 0], sin in 3.7% and cos in 4.2% in [−7, 7]. Zimmermann et al. (Aug 2026) list Apple at 0.521/0.944/0.948 ulp for exp/sin/cos.
- So CORE-MATH or LLVM-libc would change bits just as vForce does.
- They are also not faster: CORE-MATH exp is about 1.4× glibc in cycles, and neither has double-precision vector versions.
- **Value:** cross-platform reproducibility, not speed.

**No exact vectorisation of Apple exp/sincos exists:**
- Apple's arm64 libm source is not public. The `Libm` drop's ARM `exp.s`/`sincos.s` are empty files.
- vForce's header warns that results "may not be bit-wise identical".
- `-fveclib=Darwin_libsystem_m` silently swaps in `_simd_exp_d2` even without fast-math.

## 4. Expected exact gains (smoke-0 world, about 470 s CPU)

| Item | Exact gain | Evidence | Effort / risk |
|---|---|---|---|
| Run-level key normalisation + ON publish (item 1, trajectory level) | **3% measured, ≤6.5% simulated** | Prototype bit-identical on smoke 0 and smoke 1 | About 35 lines plus tests; low risk with the guard in section 6 |
| Mode-2 pair-Gaussian constant cache (item 1) | about 0.35% | Counter: 649 M constant exps | 10 lines; trivial |
| Unchanged-member slot skip (item 1) | ≤0.2% net | Counter: 1.1% of site exps | Not worth the code |
| Provable zeros / out of reach (item 2) | 0 | 0 zero, 0 subnormal, 6 / 4.8e10 no-op adds | — |
| SoA / exact SIMD (items 3–4) | 0 measured; 3–8% possible, uncertain | Bit-identical prototype, 1.04–1.07× slower | High effort; needs proofs |
| Python bookkeeping port (item 5) | about 5–8% CPU, wall maybe more | Profile; numpy-equivalence traps | High verification cost |
| Disk cache (item 5) | 0 for the panel | Per-world media | Staleness risk |
| **Inexact (item 6)** | **26% CPU / 25% wall** | 3 worlds: 0 flips, max 5.1e-10 | Ends bit-identity; needs owner tolerance |

## 5. Ranked recommendation

1. **Implement in round 2:** run-level material key normalisation plus single-cohort ON publication. It is exact, small and measured, but needs the p[3] guard below.
   - Re-measure with two back-to-back pairs (launch order swapped), as in round 1, before claiming a number.
   - Optionally include the mode-2 pair-Gaussian constant cache in the same change. It is trivial, but its effect alone is below noise.
2. **Measure before deciding:** GIL hold time and Python wall share on the coordinator.
   - If wall is GIL-bound, port only `emissions` (hash plus channel) and `state_errors` to typed code. Use separate `sin`/`cos` with no merge, and replicate NumPy's pairwise order.
   - Bit-compare every ported function on the logged inputs of a full world.
   - Otherwise skip, because the 360 s rule already has about 2.4× headroom.
3. **Skip:**
   - per-call transcendental memoisation beyond mode 2;
   - zero/underflow skipping;
   - SoA/exact SIMD;
   - the disk cache;
   - prefix resume (0.75%).
4. **Item 6: do not ask the owner now.** The exact engine passes the rule with margin, and the inexact route ends bit-identity with every stored reference, receipt and audit.
   - Keep it as a prepared reserve, with the tolerance in section 7, if a future budget (more worlds, a slower machine) needs about 25%.

## 6. Required guard for the round-2 candidate (found during recheck)

**The edge case.** The candidate key drops p[3] (output scale).
- With a **nonfinite** p[3], the current code takes the inline integration for an OFF run with selected members, and returns error code 1 through the actual medium.
- If the key ignores p[3], that call could instead hit an entry stored by a finite-p[3] run and return 0.
- Python's `validate` forbids nonfinite model values, so production cannot reach this. The native contract tests do exercise nonfinite inputs.

**Fix.** Normalise only when `std::isfinite(p[3])`; otherwise append the original p[3] bytes. Add a test: OFF run with p[3]=inf, selected members and a pre-filled store gives code 1.

**Other notes:**
- The candidate is based on 978e4dd. Commit ec82c43 (review fixes) has since changed `field.cpp` in the Store, allocation and `field_run` hunks; the evaluator is untouched. Rebase rather than apply blindly.
- ON publication takes a store lease after the ON run. If another thread is computing the same key, the ON thread waits for it; this is bounded. A non-blocking "publish if absent" would avoid the wait.

## 7. Prepared tolerance for item 6 (only if the owner is ever asked)

**The proposed tolerance:**
- **Discrete:** every Boolean, integer, label, membership, chain or invalid field and stop reason must be identical to the bit-exact engine on the same inputs. Identity digests may change.
- **Numeric:** absolute difference ≤ **1e-8** on every float. The largest observed is 5.1e-10, so this leaves about 20× margin. Values that are themselves differences (grid errors) are reported relatively as well.
- **Registered diagnostics:**
  - `b_reference_equivalence` (1e-10 over 1-unit segments; kernel deviation measured at about 4e-16 at T=2) must still pass;
  - `b_transform_equivariance` (1e-9) must still pass;
  - both must be re-run.
- **Sample:**
  - all 4 stored reference worlds (smoke 0/1, development 0/1), plus at least 6 development worlds;
  - any decision flip rejects the variant;
  - new bit-exact references are then generated with the inexact kernel, and later work is exact against those.

**Rationale.** In chaotic integrations, trajectory-level identity cannot survive a libm change. Climate-model practice replaced bit-for-bit checks with ensemble/statistical consistency tests (Baker et al. 2015; Rosinski & Williamson 1997). Decision-level identity plus a small absolute bound is the strict version of that for this protocol.

**Approvals needed.** This ends the zero-tolerance contract (decision 0029 item 3). It needs owner approval and a decision record before any use.

## 8. Owner recheck applied to this memo

The owner's prompt, applied: "Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps." No numeric score is assigned (AGENTS.md).

**Fixed during the recheck:**
1. **Issue:** the candidate's p[3] normalisation can turn an error code into success for nonfinite p[3] (section 6). The guard and test are now specified.
2. **Gap:** I first read the 4.4% "same-slot pair exp" as general memo potential. The counter arithmetic shows it is exactly the mode-2 constant (649 M of 652.7 M), so the claim is now 0.35%, not 4.4%.
3. **Gap:** I first planned to claim the simulated 6.5% run-level gain. I measured it as a world instead: 3.0%, with the store-capacity and Python-cache reasons given.
4. **Conflict:** the sub-agent's source (Apple, 2017) said `__sincos_stret` equals separate `sin`/`cos`. Measurement here says the sine differs on up to 1.4% of arguments. The measurement governs, and it is now a guardrail for items 5 and 6 and for any future kernel edit.
5. **Gap:** the inexact claim initially rested on one world. It now rests on three (smoke 0/1, development 0), all with 0 flips.

**Conflicts and caveats that remain, disclosed:**
- **Single pair.** The run-level −3.0% comes from one concurrent pair at load 21–61. The same-code noise is ±2–4%, so two swapped pairs are needed before reporting it.
- **Prototype effort.** The SoA prototype was one attempt of about an hour. A better one might find 3–8%. I report "not worth it", not "impossible".
- **Python gains** are estimated from round-1 profile numbers, not re-measured on the final code. GIL effects on wall time are unmeasured.
- **Microbench timings** were taken under load. Only ratios between interleaved runs are used.
- **Inexact-world CPU** for smoke 1 and development 0 came from unpaired runs at load about 90. Those runs were used for deviation only, not for speed.
- **Moving baseline.** The other agent committed ec82c43 during this work. My baselines are 978e4dd. The evaluator is identical in both; the Store changes could shift the cache numbers slightly.

**Is this the best we can do?** For exact work, yes, as far as these measurements show. The remaining exact pool is Python (13–15%) plus run-level redundancy (≤6.5%). Everything at the transcendental-call level is either already done or below 0.5%.

The only large lever left (about 25%) is inexact. It is not needed for the current rule.

A bigger exact rework would change *what* is computed, not *how*, which is a science question for the owner. Examples:
- fewer grid levels (the dt/4 grid is 4/7 of the cost);
- shorter recovery windows.

Those are outside decision 0029's exact-engineering scope, so they are not proposed.

## 9. Sources

- Gladman, Innocente, Mather, Ozaki, Zimmermann, "Accuracy of Mathematical Functions", Aug 2026 (Apple Math Library 26.5.2, M1, clang 21): https://members.loria.fr/PZimmermann/papers/accuracy.pdf
- CORE-MATH project and speed (exp 18 vs glibc 13 cycles): https://core-math.gitlabpages.inria.fr/ ; https://members.loria.fr/PZimmermann/talks/core-math-fpbench2023.pdf
- LLVM libc correctly rounded functions: https://libc.llvm.org/headers/math/index.html ; https://reviews.llvm.org/D158551
- RLIBM (32-bit and below): https://arxiv.org/abs/2504.07409 ; Intel correctly rounded vector library (single precision): https://arxiv.org/abs/2605.15547
- vForce header ("may not be bit-wise identical"): https://jenkins.heirloomcomputing.com/downloads/MacOSX10.8.sdk/System/Library/Frameworks/vecLib.framework/Headers/vForce.h
- Apple Libm open-source drop (empty ARM `exp.s`/`sincos.s`): https://github.com/apple-oss-distributions/Libm
- SLEEF (accuracy classes, bit-wise consistent builds): https://sleef.org/aarch64.xhtml ; https://arxiv.org/abs/2001.09258
- ARM Optimized Routines AdvSIMD bounds: https://github.com/ARM-software/optimized-routines/tree/master/math/aarch64/advsimd
- `-fveclib` mappings: https://raw.githubusercontent.com/llvm/llvm-project/main/llvm/include/llvm/Analysis/VecFuncs.def
- Intel FP consistency (reductions, SVML vs libm): https://intel.com/content/dam/develop/external/us/en/documents/pdf/fp-consistency-121918.pdf
- Apple on `sincos` vs `sin`/`cos` (2017; contradicted by measurement here): https://lists.llvm.org/pipermail/cfe-dev/2017-May/053901.html
- NumPy float64 trig/exp dispatch: https://github.com/numpy/numpy/blob/main/numpy/_core/src/umath/loops_trigonometric.dispatch.cpp
- Gaussian gridding recurrences (Greengard & Lee 2004): https://pure.ewha.ac.kr/en/publications/accelerating-the-nonuniform-fast-fourier-transform/ ; LAMMPS tables: https://docs.lammps.org/pair_modify.html
- Tolerances for chaotic codes: Baker et al. 2015 https://gmd.copernicus.org/articles/8/2829/2015/ ; Rosinski & Williamson 1997 https://epubs.siam.org/doi/10.1137/S1064827594275534 ; Glatard et al. 2015 https://pmc.ncbi.nlm.nih.gov/articles/PMC4408913/

## 10. Scratch artefacts

All under `$S`:

| Area | Files |
|---|---|
| Instrumented world | `repo/native/c6_option_b/field.cpp`, `runs/smoke0.json`, `runs/smoke0.jsonl`, `runs/smoke0/` (EXACT pass) |
| Analyses | `analyze.py`, `policy.py`, `dev.py` |
| Exact candidate | `exact_candidate.patch`, `repo3/`, `runs/w_repo3/`, `runs/w3_smoke1/`, both EXACT pass |
| Inexact kernel | `bench/vfsep/field.cpp`, `repo2/`, `runs/w_repo2/`, `runs/w2_smoke1/`, `runs/w2_dev0/` |
| Baseline | `repo0/`, `runs/w_repo0/` (EXACT pass) |
| Benches | `bench/` (`vf.cpp`, `tm.cpp`, `sc.cpp`, `cr.py`, `drv.cpp`, `sample.txt`, `bench.py`, `tbench.py`, and the `base`/`var`/`nolibm`/`nodiv`/`noacc`/`nostub`/`vfk` variants) |
