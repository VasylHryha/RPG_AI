ENGINEERING_REPAIR: ACCEPTABLE_WITHIN_REVIEW_SCOPE (static and stored-artifact scope; full-world behaviour NOT_VERIFIED) · C6: BLOCKED (unchanged) · ROUTE: prospective scientific-model redesign, preceded by one apparatus-sensitivity pilot · No hypothesis verdict assigned

Reviewer family: Claude
Model: claude-opus-5-5 (Claude Code), 2026-10-03. Revision 2 of this report. It replaces the uncommitted first draft written earlier in the same session, after an owner-requested recheck.
Implementer family: Codex
Authority: [decision 0026 (revision 2)](../decisions/0026-authorize-c6-unblocking-review.md); [brief revision 2](c6_unblocking_review_request.md)

# C6 unblocking review — Claude

## Bottom line

1. **The post-stop repair is sound within static and artifact scope.** All five claimed fixes are in the code. No live defect was found. It has never run a world.
2. **Runtime is not the deepest blocker.**
   - Under the registered rule, the per-world limit is `180 s × workers`.
   - The R006 gap (561 s against 360 s at 2 workers) is mostly a resource-allocation question on a 10-core machine. Exact arithmetic and caching gains are bounded, at about 1.4× on native time.
   - Contention at higher worker counts is unmeasured.
3. **The decisive problem is apparatus sensitivity.** The recorded states show the following, with the cause traced to the approved equations:
   - **Quiet medium.** In a background that never received output, the medium stays near zero amplitude (|z| ≤ 0.038 at all 25 sites). New populations are then almost uncoupled and form units in 26/26 recorded cases.
   - **Exposed medium.** A unit's output flips 6–8 sites into the high-amplitude basin, and they stay there; this is real retained background change. Their heterogeneous frequencies then beat against later populations. That breaks the collective-frequency stationarity rule, which is the only criterion that fails in every recorded rejection and source loss.
   - **Consequence.** The registered H-RBG witness `(true,false,false)` requires the turn-1 NO-BACKREACTION control to *fail*. In this apparatus that control is the quiet ceiling case.
   - **What R4 can still deliver.** At most a change in background response (H-BG) and suppression of later formation (H-PS, negative direction). Its recursive-enablement claim is close to structurally unreachable. Faster code cannot change this.
4. **Recommendation.**
   - First, run one pre-registered limiting-case pilot that checks this mechanism at population level, without units or treatments.
   - Then draft a prospective redesign whose control formation is below ceiling and whose retained background can, in principle, *enable* as well as suppress.
   - Fallback: the unchanged model with a prospective worker-count change and the gate-supervisor repairs, under unchanged readiness rules.

## Header

| Item | Value |
|---|---|
| Reviewed HEAD | `70ecb99`. The review began at `31f5925`. `70ecb99` landed mid-review. It is documentation-only (0026 revision 2, brief revision 2, `c6_unblocking_brief_recheck_chatgpt.md`) and changes nothing in geomind/native/tools/tests/experiments/milestones/evidence or STATUS.json (diff checked). The committed brief is byte-identical to the owner-supplied revision this review followed. The ChatGPT file is a brief-consistency recheck, not a review of the repair, so there is no output-path collision. No owner decision is newer than 0026 revision 2. |
| Tested source commit | `8561ab596220387ac4c8bc90b8985d85ea2e0f13` |
| R006 world implementation | `def6fd75e83f3e80c4551172a8829f28a127a33f`. `native/c6_r4/field.cpp`, `tools/c6_r4_design_gate.py`, `tools/build_c6_r4.py`, `geomind/run_c6_r4.py`, `geomind/c6_r4_field_reference.py` and `experiments/c6_r4_protocol.json` are byte-identical from `def6fd7` to HEAD. The repair changed Python files only. |
| CHECKS SHA-256 (computed independently from bytes) | `4d3e6d1e02e253f2ccf5c88ccbbc2aa5da05bfde23750d27ae2aeee5720a05b0`, which matches the pin. Git blob `f061b010178003979690f0252656973f0dd8d894` at `7a1e89e` and HEAD. |
| Prior involvement (disclosed) | This reviewer family has no authorship of C6 implementation code. Claude authored the earlier C6 engineering reviews, including READY_FOR_DEVELOPMENT in `c6_r006_performance_recheck_claude.md` for `7ac1e33`, the speed repair that ran in R006. Claude also co-assisted the R006 registration commit `def6fd7` (review files and namespace update). This review therefore partly judges consequences of an earlier Claude verdict. That earlier review explicitly excluded whole-world readiness, and this review does not soften F2 or F3 on its account. |
| Project execution | None. Inspection used no project imports, runners, tests, builds or native loading, only: git; text reading; stdlib SHA-256, gzip, JSON and XML parsing; arithmetic on stored values; and `sysctl` for host core and memory counts. Two read-only sub-reviews (repair code; cost and profile structure) ran under the same rules. Every load-bearing claim taken from them was re-checked against source or artifacts. |
| Files written | This report only. The owner-requested copy of the brief revision is identical to the committed `70ecb99` version. |

### Inspected vs not inspected

| Inspected | NOT_REVIEWED, and its effect |
|---|---|
| AGENTS.md; STATUS.json (C6); `research/rrg/CURRENT.md`; v0.2.1 04 §§1–2 and §11; 08 (H01/H06/H10/O1/O2); 07 (rows on background vs coarse-graining and mode creation); foundation ERRATA | Full R5 text and 04 §§3–4 were not reread. Effect: the route rests on 04 §§1–2/11, 08 and the proposal's own hypothesis rules. Nothing here depends on unread R5 wording. If R5 is read as making one-link H-BG/H-PS sufficient for C6's purpose, §5's ranking of the routes would need revisiting. |
| Decisions 0019, 0020, 0023–0026; the whole R4 proposal; protocol budget, numerics and model; manifest summary; `milestones/c6.json`; the Codex post-stop audit; the ChatGPT brief recheck | Manifest endpoint rules were not re-traced one by one. Effect: 79-endpoint coverage is not re-certified. |
| The full repair diff `def6fd7..8561ab5` in geomind/tools/tests. All of `native/c6_r4/field.cpp`, `tools/c6_r4_design_gate.py`, `tools/build_c6_r4.py`, `tools/c6_r4_performance_report.py`. The changed regions of `c6_r4_field.py`, `_assay.py` and `_protocol.py`. The world writer in `tools/c6_r3_design_gate.py`. The new regression tests. | Not inspected: `c4_detect` statistics, the bootstrap and endpoint logic in `c6_r4_field_analysis.py` (only the changed `b_costs` lines), mutant semantics, `tools/milestones.py`, and tests that predate the repair. Effect: verdict machinery is unreviewed. It is untouched by the repair, so the repair verdict is unaffected. |
| CHECKS and all six artifacts it references (hashes recomputed). JUnit: 79 testcases, all in `tests.test_c6_r4_field`, 0 failures/errors/skips. COMPARISON, VALIDATED_HISTORICAL_COMPARISON, GATED_STAGES, EARLY_STOP, R006 `results.json`. Both R006 world files: hashes recomputed, decompressed and parsed, including check rows, episodes, persistence windows and full stored owner states. Both R006 `sample` profiles (via sub-review, shares spot-checked). The four withdrawn R004 world files (summary fields only). | `optimized.json` vs `baseline.json` raw arrays were not re-compared value by value. The comparison maxima are **SUMMARY_ONLY**, though both files' SHA-256 match the record. R005 profiles were seen only through the sub-review summary. Hashes inside the C1/C2/R3 receipt-bound inventories were not re-verified. |

## 1. Verified record

| Record | Status |
|---|---|
| R006 STOP: 561.151037333 s and 546.816802416 s; tuple `(true,false,true)` in both worlds; turn-2 loss at 315 / 301 | **Verified** against `EARLY_STOP.json` and the raw world files. `invalid: null` and `controls_passed: true` in both turns. Loss statistics agree across the three grids to ≈3e-13. |
| 392.095 s lower bound | **Verified**: 394.095 s between sample timestamps, minus 2 s sampling. |
| Pre-R006 descriptor 83.3329 → 4.8511 s, error < 7e-14 | **Verified** from the performance-checks COMPARISON. VALIDATED_HISTORICAL_COMPARISON is byte-identical (`94cfda9f…`) to `c6_r006_performance_checks/REPRODUCED_COMPARISON.json` (added `8570072`). It is a re-validation of stored outputs, as stated. |
| Post-stop: 79 contracts + smoke; 6.072003625 s; 6.88338275267597e-14 at 1e-10 | **Verified** from the JUnit XML and CHECKS. The 79 **pytest contracts** are unrelated to the 79 **manifest endpoints**. **53 mutation targets are registered and 0 were executed.** |
| CHECKS `source_hashes` | All 10 match `8561ab5`. `STATUS.json` and the Codex audit differ at `7a1e89e`/HEAD only by the legitimate evidence-publication edits. All code files match at HEAD. |
| No development worlds, mutants, panel or final entropy in the repair batch | **Verified** for C6 (CHECKS flags; manifest `final_entropy: null`). |
| Brief pin note "31f5925 = the two instruction documents" | **Minor discrepancy.** `31f5925` added only the brief. 0026 was added in `3da527d`. Nothing depends on it. |

## 2. Findings, ranked

Classes: **CD** = confirmed defect; **RO** = recorded limited observation; **PR** = protocol/authorization requirement; **PD** = proposed diagnostic; **UA** = unsupported assumption.

### F1 — CRITICAL for C6's purpose — RO with an equation-level mechanism. The R4 apparatus is near-structurally unable to show recursive enablement.

All values below are stored values; no verdict is assigned and nothing is rescored.

**(a) Control backgrounds are a quiet medium, and formation there is at ceiling.**
- At B0 and in every NO-BACKREACTION turn-1 background, the stored medium has max |z| = 0.031–0.038 across all 25 sites, at t = 100, 200 and 300.
- The approved incoming term is `.2·Im(g e^{-iθ})`, with |g| ≤ max|h(z)| ≈ 0.038. A population there is therefore driven by at most about 0.0076 rad/C0.
- Its own coupling is K=1 and J=.8, and its frequency half-spread is .25. Locking is expected, and every recorded quiet-background candidate locks:
  - R006 initial sources: 2/2.
  - NO-BACKREACTION episodes 0–4: 10/10.
  - B_before episodes: 8/8.
  - The four **withdrawn** R004 worlds (0020; their defect was in the operation-window join, not the initial qualification): 4/4 initial sources, used here as corroboration only.
  - Total: **26/26**.
- The largest quiet-background frequency change recorded is 0.0082, so the worst case already uses about 80% of the 0.01/C0 tolerance.

**(b) Unit output produces a retained, real background change.** The quiet medium has two stable states per site: near zero, or a high-amplitude basin at r ≈ 0.874 (|h| ≈ 0.658). The unstable boundary between them is at r ≈ 0.485, and relaxation is fast (slopes −0.18 and −0.81, relaxation times ≲ 6 C0).

| Sites in the high basin | INTACT | NO-R | NO-BACKREACTION |
|---|---|---|---|
| World 0 at t=200 | 8/25 | 2/25 | 0/25 |
| World 1 at t=200 | 8/25 | 4/25 | 0/25 |

The switched sites are still switched at t=300 in each branch carrier. This bistable retention is the mechanism R4 intended for H-BG. Recorded response gain rose under INTACT in both worlds:
- world 0: 0.1404 vs 0.0944 (NO-BACKREACTION) and 0.0987 (NO-R);
- world 1: 0.1092 vs 0.0946 and 0.0992.

**(c) The retained change suppresses formation and destroys persistence, through one criterion.**
- The switched sites oscillate at their own heterogeneous Ω_a ∈ [−.3, .7].
- A later population sampling them receives coupling of order .2 × |g|, which is several times the quiet bound. It beats at the frequency differences.
- The rule that fails is exactly the one that registers this: the half-window collective-frequency change above 0.01/C0.
  - All **15/15** rejected turn-1 candidates fail it, with values 0.0106–0.0294; one also fails the pattern rule.
  - Both turn-2 source losses fail it alone (0.01189 at t=315; 0.01292 at t=301).
  - World 1's R1 qualified at 0.00962 and failed one C0 later.
  - Intact-background units that do qualify sit near the threshold (0.0033, 0.0051, 0.0096). Continued drift then removes them.

Turn-1 formation, episodes 1–4:

| World | INTACT | NO-R | NO-BACKREACTION |
|---|---|---|---|
| World 0 | 0/4 | 2/4 | 4/4 |
| World 1 | 1/4 | 0/4 | 4/4 |

**(d) The consequence for the registered claims.**
- Readiness needs ≥5/10 mechanically complete chains, and each needs an R1 that persists in this drifting background.
- H-RBG SUPPORTED needs ≥10 worlds whose **turn-1** tuple is `(true,false,false)`. That requires the NO-BACKREACTION control, which is the quiet ceiling case, to fail.
- So the apparatus can register background change (H-BG) and suppression (H-PS, a valid two-sided CHANGE). It is close to structurally unable to register *enablement*, which is the recursion claim C6 exists to test (04 §2: persistent structures become conditions "from which subsequent structures emerge").
- The proposal's own self-audit flagged "baseline formation might saturate". This is that risk, now observed and explained.

**Bounds.**
- This rests on two development worlds, corroborated by four withdrawn worlds and the equations. It is not a population rate.
- The coupling-magnitude argument is an order-of-magnitude consistency check, not a derivation of the observed values.
- It does **not** show that RRG is false. It shows that this apparatus cannot discriminate one direction.

**Not allowed in response:** loosening the 0.01/C0 rule; reclassifying these worlds; choosing favourable worlds.

### F2 — HIGH — RO/PR. The runtime blocker is real under the registered rule, but its size depends on the resource parameter.

- **The rule.** `max(world_seconds) · 40 / workers · 1.5 ≤ 10800` (`tools/c6_r4_design_gate.py:114,119`; `budget.workers = 2`). That gives a per-world limit of **180 s × workers**: 360 s at 2, 720 s at 4, 1080 s at 6.
- **This is the registered rule, not a hardware limit.** The host has 10 cores (Apple M1 Pro) and 32 GiB. R006 workers peaked at 0.56–0.58 GB RSS.
- **Measured R006 cost.**

| Quantity | World 0 | World 1 |
|---|---|---|
| Model time per grid (re-derived from check rows) | 8720 C0 | 8600 C0 |
| Descriptors (identical in both worlds) | 4080 C0 | 4080 C0 |
| Active-cohort integration | 4640 C0 | 4520 C0 |
| Of which turn-1 formation prefixes | 2000 | 2000 |
| Recovery + causal | 1800 + 240 | 1680 + 240 |
| Operation | 600 | 600 |

- **Descriptors are minor.** The worlds differ by 14.33 s over 120 active C0, a marginal cost of 0.119 s/C0. That matches the average of 0.121 s/C0, so descriptor work is small (consistent with the 5–6 s fixture per descriptor pair). Active native integration dominates. This two-point slope comes from two concurrent runs on a shared machine, so it is indicative only.
- **Inference, not measurement.**
  - A chain-complete world adds about 19 turn-2 episode qualifications, roughly 3500 active C0 with two ancestors, giving about 980 s.
  - That passes at 6 workers only if contention inflates per-world time by less than 10%.
  - 561 s passes at 4 workers only if inflation is below 28%.
  - Contention at higher worker counts is **unmeasured**.
- **Current code.** No world has run on `8561ab5`. The descriptor ratios (17.18× and 13.72×) must not be transferred to a world. R006 already contained the 17× change and still took 561 s.

### F3 — MEDIUM — CD (live, `tools/c6_r4_design_gate.py:146–157`). The readiness driver cannot stop promptly.

1. **No in-flight check of the impossibility condition.** Each worker's timeout is the remaining 1800 s development cap (`:149`), not the per-world limit implied by the rule. R006 needed a manual stop (0024). Without it, the gate would have run all queued worlds to the 1800 s cap.
2. **Queued work runs after a failure.** If a world raises, leaving `with ThreadPoolExecutor` calls `shutdown(wait=True)` without `cancel_futures` (Python 3.9). Queued worlds still start while `remaining > 0`, and the STOP receipt is delayed until they finish.
3. **Non-atomic writes.** `save()` (`:140`) and `write_world` (`tools/c6_r3_design_gate.py:52–55`, an exclusive create but not atomic) are not atomic, so a kill can leave a torn file.
4. **No accounting of failed work.**

Smallest correction, made prospectively under a new authorization:
- a per-world supervisor limit derived from the registered rule and the chosen worker count;
- `cancel_futures=True`;
- killing only the worker's own process group;
- temp-file plus `os.replace` for every write;
- a failed-work ledger.

A killed world is `INCOMPLETE_RESOURCE_STOP`, not a scientific failure.

### F4 — MEDIUM — CD/PD. The native kernel is bound by transcendental functions; exact gains are bounded.

- **Work per evaluation.** Per active cohort per right-hand-side evaluation (`field.cpp:78–98`):
  - 276 pair terms, each with `sqrt`, a merged `sin`/`cos` of the same phase (`__sincos_stret` in the profile) and `exp(-d²)`;
  - 600 site–member Gaussians `exp(-|q−x|²/8)`;
  - 24 `polar` and 25 `sqrt`.
  - In total about 876 `exp`, 300 `sincos` and 300 `sqrt`.
- **Consistency with the measured rate.** 0.12 s per active C0 across three grids is 1400 RK4 steps × 4 evaluations = 5600 evaluations, about 21 µs each. That is consistent with roughly 1450 libm calls. The early R006 profile shows 85% of samples in `evaluate`, of which libm `exp` is about 38% and `sincos` 12.7%.
- **Two exact reformulations of the same real arithmetic:**
  1. `cos/sin(θj−θi)` from the phasors already computed at `:78`, which removes 276 `sincos` per evaluation;
  2. the site Gaussian separated in the square-lattice basis (5+5 instead of 25 exponentials per member; this survives rotation and translation because the lattice is orthogonal), which takes 600 `exp` down to 240.
- **Bounded saving.** Applying the profile shares gives about 27% of native samples, i.e. **≈1.37× on native time**, and less at world level. This is an upper bound from a single 1.8 s profile, not a measurement.
- **Status of these changes.** They are not bitwise identical, so they are an implementation change requalified by the existing 1e-10 reference battery. They are not a model change and not "fast math". Last-bit decision flips are implausible: the three grids, whose truncation errors are ~1e-9 to 1e-11, agree on the near-threshold statistics to about 3e-13. They must still be checked.
- **Conclusion.** Exact work alone cannot be shown to reach even 1.56×. A resource decision is unavoidable for this engine and model.

### F5 — LOW — CD/UA. Residual guard and tooling gaps. None is reachable in practice; none blocks.

- `c6_r4_field_assay.py:237` and `c6_r4_field_protocol.py:129` use `max(...) > tol`, which a NaN passes. Reaching it needs an overflow to inf−inf, from finite, native-checked, saturating dynamics. Fix: `if not np.isfinite(g).all() or not (max(...) <= tol): raise`.
- `tools/c6_r4_performance_report.py:56` `compare` never asserts the baseline/optimized sides or that the two files differ. Swapped inputs invert the speedup, and the same file twice passes.
- `descriptor_contract` ties per-probe gains to raw responses on grid 0 only. It does not recheck `|g_k − g_2| ≤ .001`, and it hard-codes `.05` and 100 rows.
- `tools/build_c6_r4.py:10–17` compiles in place, so concurrent processes against a stale build could race. Pre-building in the parent mitigates this. Fix: temp path plus `os.replace`.
- `tools/c6_r4_design_gate.py:50,62` uses `max(maximum, np.max(...))`, which could hide a NaN. It is unreachable (finiteness is checked natively, and the reference ends with `validate()`).
- `c6_r4_field.py:151–155` re-hashes the C++ source and dylib on every `native()` call under a global lock, ≥2.7k times per world inside the timer. It is small but is pure overhead.

### F6 — LOW — RO. Stale governance text. Not edited here; the files are dependency-hashed.

- `experiments/c6_proposal_r4.md:3` still reads "DRAFT FOR OWNER APPROVAL … No implementation … has run", and §11 row 1 says to await approval. Decision 0019 approved it.
- `research/rrg/CURRENT.md` (final paragraph) says the C6 R4 draft "needs owner approval". 0026 revision 2 §2 already records that 0019 governs.
- 0025's last stop row ties REVIEW_READY to "independent scientific acceptance". The repair needed only an independent engineering review, which this document provides within its scope. 0026 revision 2 §3 already says so.
- The R006 STOP bars an automatic retry. It is not a finding that engineering cannot improve. RRG publication does not depend on C6 (08 O1 calls even two causally connected stages a useful contribution).

Record the corrections in the next decision rather than editing hashed files.

### Verified OK (the repair itself)

All five 0025 repairs are present in the code. None was inferred from the report.

1. **Sampled rows.** Copies are kept (`c6_r4_field_assay.py:43–44`). At most one prior block can be alive, which is bounded. A weakref regression and a mutant cover it.
2. **Caches (`c6_r4_field.py:215–233`).**
   - Lookup, insert and evict happen under one lock. Computation is outside the lock, with a recheck on insert.
   - Results are `writeable=False`, and consumers copy them.
   - Results larger than the limit are returned uncached, so eviction terminates under the byte limit.
   - The emission key binds `q`, the selected `x`/`θ` trajectories (shape included), `sigma` and the coefficient. These are exactly the channel's inputs. Native code also emits from actual `x` in every mode (`field.cpp:96–97`).
   - The passive key is the full owner `identity()` plus `duration`/`dt`/`sample_dt`. Grids, and actual vs carrier states, cannot alias.
   - No random draws are cached. Caches are per process.
3. **Native boundary.**
   - `!(denom>1e-12)` also catches NaN (`field.cpp:102`).
   - Nonfinite output is rejected per evaluation and per step (`:106,135`).
   - The wrappers raise on any error code.
   - `state_errors` validates layouts, finiteness, scales, differences before any max, and the derived errors (`assay.py:65–83`).
4. **Compute-before-mask.** The channel is computed whenever `selected` is set, and `max(0,mask)` is applied after (`field.cpp:96–98`). The OFF marker counts in the normalizer.
5. **Comparison validator.** Fails closed on the 25×2 inventory, the 51 scopes, finite shaped arrays, clocks and hashes.

**Repair verdict: ACCEPTABLE_WITHIN_REVIEW_SCOPE.** It does **not** establish:
- full-world equivalence;
- memory release under production load;
- race absence under real concurrency;
- mutant kills;
- compiler behaviour;
- runtime readiness.

## 3. Readiness gate vs claims

`readiness` (`tools/c6_r4_design_gate.py:108–122`) requires:
- ten complete worlds;
- no invalid world;
- ≥5 qualified sources and ≥5 **mechanically complete** chains;
- a projection over **all** rows within 10800 s.

It reports `enabled_witness` but does not require it. Exclusive witnesses and positive primary effects are not readiness conditions.

H-BG and H-PS are two-sided, so the suppression in F1 is a scientifically valid direction. The `(true,false,false)` witness is the stronger H-RBG scope condition only. It does not redefine RRG or erase valid first-turn evidence. F1 matters because C6's stated purpose is source recursion, and because the chain quorum gates even the first-turn evidence.

Arm B has no direct-part hierarchy or upper predictor. H-COMP, H-PRED, H-AI and H-EFF and the Arm A contracts do not apply.

Eligibility, physical source loss and engine-invalid status are distinct in the rows:
- both turn-2 losses are `SOURCE_LOST_DURING_OPERATION` with `invalid: null`;
- the sham/source equality checks passed.

## 4. Remaining cost, ranked by attributable evidence

| Rank | Function / stage | Profile / source version | Observed work or complexity | Proposed change | Plausible saving and basis | Semantic / memory risk | Smallest verification |
|---|---|---|---|---|---|---|---|
| 1 | Registered `budget.workers` (`protocol.json`; gate `:114`; panel `run_c6_r4.py:57`) | rule arithmetic; host 10 cores / 32 GiB; 0.58 GB RSS per world | Per-world limit is 180 s × workers | Prospective resource change, e.g. 4–6 workers, with the limit restated from the new value | 360 → 720/1080 s per-world limit. **Net effect depends on unmeasured contention inflation.** | None to the equations. It is a **protocol/resource change** that needs an owner decision. | Measure per-world wall and CPU at the proposed worker count (the §6 pilot does this) |
| 2 | Native `evaluate` (`field.cpp:78–98`) | early profile `def6fd7`: 85% `evaluate`, `exp` ≈38%, `sincos` 12.7% | ~876 `exp` + 300 `sincos` + 300 `sqrt` per cohort-evaluation; ≈21 µs measured | Phasor identities for the pair `sin`/`cos`; lattice-separable site Gaussian | ≤ ≈1.37× native (upper bound from shares of a single 1.8 s profile) | Not bitwise identical. Implementation change requalified by the 1e-10 reference battery. | Reference battery + fixture + check that grid agreement is unchanged |
| 3 | Three grids sequential in `GridSet.run` (`assay.py:38–50`) | early profile: GIL-releasing native | Step multiples 1+2+4; the finest is 4/7 | Run the grids concurrently in threads | ≤1.75× native per world | Bit-identical. It is a resource-semantics change: the same CPU spent on more cores per world. Same owner decision as rank 1; do not count both. | Byte-identical flows vs sequential |
| 4 | Passive-ancestor re-integration (`c6_r4_field.py:193–208`) | structural; hit rate **unrecorded** | Up to ≈3880 passive cohort-C0 per world; 64 MiB LRU of ≈1.95 MB entries | Turn-scoped or pinned exact-key cache | Unknown; measure hits first | Exact; ≈0.59 MB per C0 per ancestor | Hit/miss counters |
| 5 | Duplicate 10-C0 causal/recovery-control runs (`assay.py:110,139`) | structural | ≈170 of 4640 active C0 | Exact-input reuse | ≈3.7% | Low; all rows still emitted | Byte-identical rows |
| 6 | Per-call `native()` re-hash; 4-entry drive cache | code; `drive` 3.9% of early profile | ≥2.7k hashes per world | Hash once per run; enlarge the cache | Small (<1–4%) | Coarser identity guard | Contract tests |

**Excluded:** fewer probes, truncated horizons, coarser grids, skipping zero-mask channels, shared random draws, fast-math, and a longer timeout alone.

**Accounting outside the timer** (`protocol.py:134–176`): per world, 60.1 MB of JSON (81% descriptor raw), gzip, process start, imports, native load, and the reference battery. These must be recorded separately in `b_costs`, without changing the registered timing variable.

## 5. Route

Runtime and feasibility are separate questions:
- F2 and F4: runtime is solvable in principle by an explicit resource decision, possibly with exact native work.
- F1: feasibility of the recursion claim is not solvable by any engineering under this model.

**Recommended: prospective scientific-model redesign (a new C6 proposal revision), preceded by the §6 limiting-case pilot.** Reasons:

1. **The unchanged model probably cannot pass the gate.** Readiness needs ≥5 complete chains, which need persistent R1 units in a drifting background. Both recorded R1 units failed on the same mechanism.
2. **Even a passing gate leaves the central claim untestable.** A passing gate and panel could still not support enablement, because the turn-1 control sits at ceiling. Spending engineering and panel compute on an apparatus that cannot discriminate the central claim is the poorest use of the next step.
3. **The redesign has clear, principled targets taken from the equations, not from favourable outcomes:**
   1. Control-background unaided formation must be below ceiling and above zero, so that enablement and suppression are both observable.
   2. The retained background must be able to supply coherent, frequency-stationary input. An example is a medium whose switched region holds a common mode rather than heterogeneous beats. Then entrainment can *raise* formation, and persistence criteria remain meaningful.
   3. Keep the unit, closure and frequency criteria unchanged unless 04 §1.4 justifies a change independently of these worlds.
4. **The redesign keeps the engine.** It carries F3 and F5, the rank-2/4/5 work and an explicit worker count. Its own fresh development gate measures runtime prospectively.

**Fallback: the unchanged model.** Applies a prospective worker-count change (rank 1), the F3 supervisor and the F5 guards, under **unchanged readiness rules**, on fresh development entropy (R007). Choose it if:
- the pilot's quiet-medium arm rejects the ceiling (§6 outcome B); or
- the owner wants a population-level measurement of R4 before redesigning.

Expect a chain-quorum STOP to be likely. A world-0 regression replay of `8561ab5` should precede it, to qualify the repair at world scope. Its specification belonged to this report's first draft and can be restored on request.

**Not recommended without an explicit, disclosed owner decision:** reducing R4 to turn-1-only readiness so that H-BG/H-PS can run while chain readiness is waived. It would be a scope change made after seeing development chains fail. It would not test recursion. Brief §6 bars lowering a readiness requirement in response to observed failures.

**Pause** is reasonable if the owner prioritises RRG publication, which does not depend on C6.

## 6. One bounded next diagnostic (specified, not executed)

| Field | Specification |
|---|---|
| Purpose / decision answered | Are F1's two properties general at population level and caused by the identified mechanism? (i) Unaided formation at ceiling in a quiet medium. (ii) Formation suppressed by a heterogeneous retained high-basin patch, failing on frequency stationarity. Does a *coherent* retained patch instead allow entrainment-raised formation in any pre-declared lower-coupling regime? This decides between the redesign (recommended) and the fallback, and gives the redesign its target property. It also measures per-population wall/CPU at the proposed worker count, which provides the contention data that ranks 1/3 lack. |
| Design | No units, no outputs, no treatment conditions. **Backgrounds**, all supplied, all starting from an R4 quiet medium evolved for 100 C0 under the approved law: Q = quiet; H = the 8 sites nearest the introduction centre (2,0) set to radius 0.8744 with independent uniform phases and R4 Ω_a; C = the same 8 sites at 0.8744 with a common phase and Ω_a = 0.2 (limiting-case positive control, explicitly a model variant). **Coupling scales:** K and J multiplied by {1, ½, ¼}, pre-declared and not adaptive. 3 backgrounds × 3 scales = 9 cells × 16 populations = 144. Each population uses the R4 generator at (2,0) and the full R4 qualification procedure (100-C0 prefix, recovery, causal forks, three-grid refinement, unchanged thresholds). |
| Inputs / entropy | A new pilot namespace, disjoint from every development, smoke, bootstrap, reference and final namespace (none of which exists yet for final). Prior exposure: none. R006 inputs are not reused. Populations are paired across cells by index (same initial arrays and kicks). |
| Code and record | Owner-requested pilot rules (AGENTS): scratch script outside `geomind/`, calling approved R4 functions read-only. Script, raw results and a status README are committed to `evidence/c6_dev_pilot/r4_sensitivity/` (the AGENTS pilot location; existing pilot files untouched) in the same session. The cell list, counts, caps and the outcome table below are committed before execution. |
| Measured | Per population: qualified; every failing criterion and value; frequency-change trajectories; background max/median |z| and number of high-basin sites at introduction and at qualification; wall and CPU seconds; worker count; peak RSS. Per run: total wall, CPU and serialized bytes. |
| Semantic checks | Unchanged detector and thresholds. Grid agreement of decisions recorded. Background construction validated (Q has 0 sites above r = 0.485; H and C have exactly 8). Every population reported, with no exclusion; invalid populations stay counted. |
| Limits | 6 worker processes (P-core count minus margin). Total wall cap 45 min, including setup and shutdown. 2 GiB RSS per worker. Rationale: ≈26 s per population is estimated from the R006 marginal rate (≈0.12 s/C0 × ≈220 active C0). 144 populations is ≈63 CPU-min, ≈11 min at 6 workers before contention, so the 4× margin covers contention. |
| Stop / cancellation | Parent monotonic deadline. Per-population limit 300 s. `cancel_futures=True`; no submissions after STOP. Kill only the pilot's own process group. Append-only JSONL flushed per population. Atomic final summary. No retry or rerun. A partial run is `INCOMPLETE`, with completed cells reported. |
| Outcomes, fixed in advance | **A (ceiling and mechanism confirmed):** Q at scale 1 qualifies ≥14/16 **and** H at scale 1 rejects mainly on frequency stationarity. Redesign route confirmed. The redesign targets the C-vs-Q contrast at the scale whose Q formation lies nearest 0.4 (control-only selection rule). **B (ceiling not general):** Q at scale 1 ≤ 8/16. F1 is downgraded and the fallback route becomes primary. **C (no coherent benefit):** at no scale with Q below ceiling does C exceed Q by ≥3/16. The coherence mechanism is unsupported, and the redesign needs a different enabling mechanism, or the owner pauses. **Otherwise INDETERMINATE:** report and return to the owner. No verdict is assigned to any C6 hypothesis. |
| Boundaries | This is not C6 evidence. It runs no units, cannot qualify any apparatus and cannot count toward readiness. The supplied backgrounds are not unit-produced, so the confirmatory test of recursion stays with the redesigned registered experiment on fresh entropy. The control-only selection rule prevents choosing a regime by the C result. C results are disclosed to the drafter as exploratory. |
| Authorization | New owner decision required. 0026 is review-only, and AGENTS forbids pilots without explicit owner request. |

## 7. Forward sequence

This report performs none of these steps.

1. **This review.** Repair ACCEPTABLE_WITHIN_REVIEW_SCOPE. C6 BLOCKED. No claim status. No automatic lifecycle change.
2. **Owner decision** before any pilot, repair or run. Per 0026 revision 2 §2, no existing authority covers this work:
   - 0025's execution scope (fixture, then pipeline through smoke) is consumed;
   - 0023's one-shot replacement is consumed (0024);
   - 0024 requires a new owner-directed revision before development;
   - 0026 is review-only.
3. **Commit the pilot specification and script** before generating its inputs or running it. No final entropy.
4. **Run the pilot once.** Retain all results. Map the outcome (A/B/C/indeterminate) to the route. No retry.
5. **Outcome A.** The drafter writes the new C6 proposal revision. It includes:
   - the F1 mechanism and pilot results, disclosed as exploratory;
   - a normalization ledger;
   - fixed equations, regime and thresholds;
   - an explicit worker count, with the per-world limit derived from it;
   - the F3 supervisor and F5 guards;
   - rank-2/4/5 work;
   - stage, cache and CPU cost fields.

   Then: owner approval, implementation, one end-of-batch test run, and one fresh development gate on new namespaces. **Outcome B:** take the fallback, with its own registration (R007 is unused in this checkout). R006 is preserved unchanged.
6. **Only after a complete readiness PASS:** final entropy, then committed final registration, then the ordered pipeline (preflight → tests → smoke → mutation → panel), then cross-family review.

## 8. Proposed owner decision text

> **PROPOSED, NOT APPROVED.**
>
> 1. **Scope.** C6 unblocking, step 1 of the route in `docs/reviews/c6_unblocking_review_claude.md` §5.
> 2. **Model and protocol changes:** none to R4. The pilot's limiting-case backgrounds and coupling scales are exploratory variants confined to the pilot.
> 3. **Authorized:** one owner-requested apparatus-sensitivity pilot exactly as specified in §6:
>    - 9 cells × 16 populations;
>    - a fresh pilot entropy namespace;
>    - scratch code outside `geomind/`;
>    - output `evidence/c6_dev_pilot/r4_sensitivity/` (the AGENTS pilot location; existing pilot files untouched).
>
>    Its specification and script are committed before execution.
> 4. **Resource caps:** 6 workers, 45 min total wall, 2 GiB RSS per worker, 300 s per population.
> 5. **Stop behaviour:** deadline and cancellation as in §6; no retry; partial results retained as INCOMPLETE.
> 6. **Conditionally covered**, only on outcome A: the drafter may write the next C6 proposal revision, which is not implemented until approved. Only on outcome B: the implementer may prepare the fallback's registration and the F3/F5 batch, but runs nothing until approved.
> 7. **Not authorized:** R007 or any development world, final entropy, mutation, panel, R4 threshold or readiness changes, rescoring of R004–R006, and C6 status changes.

## 9. Self-attack

- **The F1 inference rests on 2 + 4 worlds.** The pilot exists to test it at population level, with outcome B pre-declared to downgrade it.
- **Counterexample to the mechanism.** The drift might come from the introduced population's own transients rather than the medium. *Detection:* pilot arm Q uses the same generator and location without switched sites. Arm H differs only in the supplied patch.
- **Selection by outcome.** The pilot selects the redesign regime by control-only formation (Q nearest 0.4). It never uses C or any treatment effect. Every cell is reported.
- **Cache warmup and workstation noise.** The pilot's timing is a single observation on a shared host. It informs contention only roughly, and no statistical timing claim is made. CPU and wall are both recorded.
- **Differing instrumentation.** None is added inside `geomind/`. Timing is per population at the harness level.
- **Cache aliasing, cross-grid or cross-treatment contamination.** Keys were traced (§2). The pilot has no treatments. Rank-4 reuse is exact-key only.
- **Floating-point ordering (rank 2).** Requalified at 1e-10. Grid agreement to ≈3e-13 on the near-threshold statistics suggests last-bit robustness, but this must still be checked on the redesign's battery. A near-threshold boolean that flips across builds is reported as a sensitivity finding, not hidden.
- **Nonfinite concealment.** F5 paths are unreachable in practice but not proven unreachable. They should be fixed in the next batch.
- **Omitted ancestor or zero-mask work.** No proposal skips either. Compute-before-mask was verified.
- **Memory amplification.** Ranks 1/3/4 raise peak memory. At 0.6 GB per world and 32 GiB host memory, 6 workers is bounded, but it must be measured.
- **Altered denominators or missingness.** The pilot counts every population, including invalid ones. No proposal changes episode counts or masks.
- **Claims carried from old code to new code.** R006 timings belong to `def6fd7`. No speed claim is made for `8561ab5`.
- **Control effects and negatives stay visible.** Suppression, ceiling-level control formation and source loss are reported as observations, not converted into verdicts or hidden as engineering failures.
- **Counterexample to the worker-count fix.** Memory-bandwidth or thermal contention at 6 workers could inflate per-world time by more than 50%, and an E-core landing would add to it. Then 1080 s would not cover a chain-complete world. *Detection:* the pilot records wall/CPU per population at 6 workers, against the R006 rate at 2. If contention is high, ranks 2 and 3 are needed or the budget must change.

## 10. Yes/no stops

| Yes/no condition | One action | Responsible role | Status here |
|---|---|---|---|
| Critical evidence missing/mismatched or changed code unqualified? | Mark the affected conclusion NOT_VERIFIED. | Reviewer | Full-world behaviour of `8561ab5` is NOT_VERIFIED. All evidence hashes match. |
| A point needs new execution? | Describe the diagnostic without running it. | Reviewer | §6. |
| A proposed speedup changes the approved scientific contract? | Label it a prospective protocol/model change. | Reviewer | Ranks 1 and 3: resource change. Rank 2: implementation change requalified by the battery. Pilot arm C: an exploratory model variant. |
| A missing measurement is being treated as a demonstrated failure? | Replace the inference with its actual bounded status. | Reviewer | Chain-complete cost, contention and population-level ceiling are labelled inference or pilot questions. |
| A next execution lacks applicable authorization? | Leave it unexecuted at the owner-decision gate. | Implementer | Nothing executed. §8 is PROPOSED. |
| The review cap ends with critical scope uninspected? | Deliver findings with an explicit non-acceptance boundary. | Reviewer | Analysis/bootstrap and `c4_detect` are NOT_REVIEWED. Repair acceptance is limited to the inspected diff. |

C6 stays BLOCKED at R006 STOP. This review accepts no C6 result, assigns no hypothesis verdict, does not resolve scientific readiness, and does not change the source theory.
