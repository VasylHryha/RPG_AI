PLANNING: REVIEW_READY_FOR_CLAUDE_CONFIRMATION (pilot approval gate still open) · ENGINEERING_REPAIR: original Claude ACCEPTABLE_WITHIN_REVIEW_SCOPE retained; full-world behaviour NOT_VERIFIED · C6: BLOCKED (unchanged) · ROUTE: Claude source/route confirmation, then owner decision on one current-R4 Q-versus-H diagnostic · No hypothesis verdict assigned

Reviewer family: Codex:GPT-6 (Revision 3 editorial recheck; not independent implementation acceptance)
Original reviewer family: Claude:claude-opus-5-5
Original review model: claude-opus-5-5 (Claude Code), 2026-10-03.
Revision 3 editor: Codex (GPT-6), 2026-10-03, at the owner's explicit request to revise this file using [the ChatGPT recheck](c6_unblocking_review_recheck_chatgpt.md), followed by an owner-requested adversarial self-recheck. This revision is a documentation correction, not a new Claude review or independent acceptance. Claude did not perform the additional source reading described below; Codex did. The recheck's explicit Claude full-source-read requirement remains OPEN; this edit does not discharge it by changing attribution.
Implementer family: Codex
Authority: current owner instruction to revise this document only; [decision 0026 (revision 2)](../decisions/0026-authorize-c6-unblocking-review.md); [brief revision 2](c6_unblocking_review_request.md). The direct instruction authorizes editing the existing report despite the older brief's report-ownership restriction. It authorizes no execution or acceptance.

# C6 unblocking review — Claude, Revision 3

## Bottom line

1. **The original repair assessment is retained within static and artifact scope.** No live regression was found in the five inspected post-stop repair areas. Separate live readiness/tooling defects F3/F5 remain. Full-world behaviour of the repaired code remains NOT_VERIFIED.
2. **Runtime is a confirmed blocker under the registered resource rule.**
   - Under the registered rule, the per-world limit is `180 s × workers`.
   - The historical R006 gap is 561 s against 360 s at 2 workers. A prospective resource change could help; the original profile-based estimate of exact native gains is about 1.4× and is not a measured world speedup.
   - Contention at higher worker counts is unmeasured.
3. **A second, provisional concern is apparatus discriminability.** The recorded states and approved equations suggest the following:
   - **Quiet medium.** In a background that never received output, the medium stays near zero amplitude (|z| ≤ 0.038 at all 25 sites). New populations are then almost uncoupled and form units in 26/26 recorded cases.
   - **Exposed medium.** Output leaves high-basin sites in the recorded backgrounds. Heterogeneous site-frequency beating is a plausible explanation for the frequency-stationarity failures common to the recorded rejections and source losses; it is not yet an isolated causal demonstration.
   - **Consequence.** The registered H-RBG witness `(true,false,false)` requires the turn-1 NO-BACKREACTION control to fail. Near-ceiling quiet-background formation would make this witness difficult to obtain in this apparatus.
   - **Claim boundary.** H-BG background change and H-PS suppression remain meaningful bounded directions. Neither these few worlds nor the equation-level consistency argument establishes a population ceiling, impossibility of enablement, or a defect in universal RRG.
4. **Recommendation.**
   - First, Claude confirms the full required source read and the corrected route, then owner review of Revision 3; only after those gates and explicit authorization, one prospectively specified current-R4 Q-versus-H diagnostic on fresh paired pilot populations.
   - If that diagnostic supports both the ceiling and suppression/stationarity concern, a separate prospective redesign study is the leading provisional route. Return its result to the owner before choosing that study.
   - Otherwise downgrade F1 as appropriate and return to the owner for unchanged-R4 engineering/resource continuation, a new registered revision, or pause. Incomplete and indeterminate results authorize no next run.

## Header

| Item | Value |
|---|---|
| Original reviewed HEAD | `70ecb99`; review began at `31f5925`. The original reviewer recorded a documentation-only change between them and no engineering change. This is historical inspection metadata, not a fresh dependency comparison by the Revision 3 editor. |
| Revision 3 input identity | The ChatGPT recheck records repository HEAD `9a5671a5f6d365ff0b1e2bba0d4b72e314995409` and Claude review blob `1fdc7bdf937fa049503f7d3bd4eab98282788271`. These identities are copied from that recheck, not independently recomputed here. Revision 3 reads current files and changes only this report. |
| Tested source commit | `8561ab596220387ac4c8bc90b8985d85ea2e0f13` |
| R006 world implementation | `def6fd75e83f3e80c4551172a8829f28a127a33f`. The original reviewer recorded unchanged native kernel, readiness driver, builder, runner, reference and protocol through its reviewed HEAD; repair changes were Python-only. Revision 3 does not renew that historical identity check. |
| CHECKS SHA-256 (independently computed in the original review) | `4d3e6d1e02e253f2ccf5c88ccbbc2aa5da05bfde23750d27ae2aeee5720a05b0`; recorded Git blob `f061b010178003979690f0252656973f0dd8d894`. Preserved provenance, not a new hash calculation. |
| Prior involvement (disclosed) | This reviewer family has no authorship of C6 implementation code. Claude authored the earlier C6 engineering reviews, including READY_FOR_DEVELOPMENT in `c6_r006_performance_recheck_claude.md` for `7ac1e33`, the speed repair that ran in R006. Claude also co-assisted the R006 registration commit `def6fd7` (review files and namespace update). This review therefore partly judges consequences of an earlier Claude verdict. That earlier review explicitly excluded whole-world readiness, and this review does not soften F2 or F3 on its account. |
| Original inspection scope | The original Claude review recorded Git/text inspection, stdlib hashing/parsing/arithmetic and host inventory, with two read-only sub-reviews. Those activities are historical; they were not repeated for Revision 3. |
| Revision 3 execution scope | Document and source-text reads and this report edit only. No project imports, tests, builds, native loading, experiments, pilots, verdict recomputation, hashing scripts, delegation, or Git mutations. The self-recheck additionally traced `Owner`/`Cohort`, medium/population generation, native loading/build fallback, `GridSet.run`, qualification selection, rolling persistence and `operation`. The original static/artifact findings and verification labels remain historical, not independently re-certified by this edit. |
| Files written | This report only; no evidence, source, implementation, protocol, gate, or milestone-status changes. |

### Inspected vs not inspected

The repair/artifact rows below describe the original Claude inspection. Only the complete source-reading row and the Revision 3 supplementary text reads are new.

| Inspected | NOT_REVIEWED, and its effect |
|---|---|
| Revision 3 editor read the **full** GeoMind R5 and current audited v0.2.1 README, **full 04 §§0–43**, full 07, full 08 and full foundation ERRATA. Also read full 05, `research/rrg/CURRENT.md`, AGENTS.md, the owner alignment handoff's supplied sections, and current C6 status. | No release checksum audit or package checks were rerun. Pin status is the recorded status in CURRENT.md. The original Claude reviewer has not performed this additional full-source read in Revision 3; editorial completion must not be described as a new Claude acceptance. |
| Revision 3 supplementary reads: ChatGPT recheck; brief; decision 0026; current R4 protocol; qualification/recovery/causal helper text and introduction/rolling-persistence helper text, to specify §6 without executing them. | No fresh full repair, evidence-tree, performance, or implementation review. Historical acceptance and hash observations remain bounded to the original review. |
| Decisions 0019, 0020, 0023–0026; the whole R4 proposal; protocol budget, numerics and model; manifest summary; `milestones/c6.json`; the Codex post-stop audit; the ChatGPT brief recheck | Manifest endpoint rules were not re-traced one by one. Effect: 79-endpoint coverage is not re-certified. |
| The full repair diff `def6fd7..8561ab5` in geomind/tools/tests. All of `native/c6_r4/field.cpp`, `tools/c6_r4_design_gate.py`, `tools/build_c6_r4.py`, `tools/c6_r4_performance_report.py`. The changed regions of `c6_r4_field.py`, `_assay.py` and `_protocol.py`. The world writer in `tools/c6_r3_design_gate.py`. The new regression tests. | Not inspected: `c4_detect` statistics, the bootstrap and endpoint logic in `c6_r4_field_analysis.py` (only the changed `b_costs` lines), mutant semantics, `tools/milestones.py`, and tests that predate the repair. Effect: verdict machinery is unreviewed. It is untouched by the repair, so the repair verdict is unaffected. |
| CHECKS and all six artifacts it references (hashes recomputed). JUnit: 79 testcases, all in `tests.test_c6_r4_field`, 0 failures/errors/skips. COMPARISON, VALIDATED_HISTORICAL_COMPARISON, GATED_STAGES, EARLY_STOP, R006 `results.json`. Both R006 world files: hashes recomputed, decompressed and parsed, including check rows, episodes, persistence windows and full stored owner states. Both R006 `sample` profiles (via sub-review, shares spot-checked). The four withdrawn R004 world files (summary fields only). | `optimized.json` vs `baseline.json` raw arrays were not re-compared value by value. The comparison maxima are **SUMMARY_ONLY**, though both files' SHA-256 match the record. R005 profiles were seen only through the sub-review summary. Hashes inside the C1/C2/R3 receipt-bound inventories were not re-verified. |

## 1. Original Claude verified record (retained)

The verification labels in this section describe the original inspection. Revision 3 does not repeat artifact parsing or identity verification.

| Record | Status |
|---|---|
| R006 STOP: 561.151037333 s and 546.816802416 s; tuple `(true,false,true)` in both worlds; turn-2 loss at 315 / 301 | **Verified** against `EARLY_STOP.json` and the raw world files. `invalid: null` and `controls_passed: true` in both turns. Loss statistics agree across the three grids to ≈3e-13. |
| 392.095 s lower bound | **Verified**: 394.095 s between sample timestamps, minus 2 s sampling. |
| Pre-R006 descriptor 83.3329 → 4.8511 s, error < 7e-14 | **Verified** from the performance-checks COMPARISON. VALIDATED_HISTORICAL_COMPARISON is byte-identical (`94cfda9f…`) to `c6_r006_performance_checks/REPRODUCED_COMPARISON.json` (added `8570072`). It is a re-validation of stored outputs, as stated. |
| Post-stop: 79 contracts + smoke; 6.072003625 s; 6.88338275267597e-14 at 1e-10 | **Verified** from the JUnit XML and CHECKS. The 79 **pytest contracts** are unrelated to the 79 **manifest endpoints**. **53 mutation targets are registered and 0 were executed.** |
| CHECKS `source_hashes` | The original reviewer recorded all 10 matching `8561ab5`, with later status/audit differences limited to evidence publication and code matching its reviewed HEAD. This edit does not extend that check to a new HEAD. |
| No development worlds, mutants, panel or final entropy in the repair batch | **Verified** for C6 (CHECKS flags; manifest `final_entropy: null`). |
| Brief pin note "31f5925 = the two instruction documents" | **Minor discrepancy.** `31f5925` added only the brief. 0026 was added in `3da527d`. Nothing depends on it. |

## 2. Findings, ranked

Classes: **CD** = confirmed defect; **RO** = recorded limited observation; **PR** = protocol/authorization requirement; **PD** = proposed diagnostic; **UA** = unsupported assumption.

### F1 — HIGH, provisional for this apparatus — RO/PD. Quiet-background ceiling and exposed-background instability may limit the registered enablement witness.

All values below are stored values; no verdict is assigned and nothing is rescored.

**(a) Recorded control backgrounds are quiet, with near-ceiling formation in the inspected cases.**
- At B0 and in every NO-BACKREACTION turn-1 background, the stored medium has max |z| = 0.031–0.038 across all 25 sites, at t = 100, 200 and 300.
- The approved incoming term is `.2·Im(g e^{-iθ})`, with |g| ≤ max|h(z)| ≈ 0.038. A population there is therefore driven by at most about 0.0076 rad/C0.
- Its own coupling is K=1 and J=.8, and its frequency half-spread is .25. Locking is expected, and every recorded quiet-background candidate locks:
  - R006 initial sources: 2/2.
  - NO-BACKREACTION episodes 0–4: 10/10.
  - B_before episodes: 8/8.
  - The four **withdrawn** R004 worlds (0020; their defect was in the operation-window join, not the initial qualification): 4/4 initial sources, used here as corroboration only.
  - Total: **26/26**.
- The largest quiet-background frequency change recorded is 0.0082, so the worst case already uses about 80% of the 0.01/C0 tolerance.

**(b) Recorded output is associated with retained background change.** The uncoupled, unforced radial drift has stable branches at zero and r ≈ 0.874 (saturated amplitude ≈0.658), separated by r ≈0.485, with local slopes −0.18 and −0.81. These scalar values are useful diagnostics, not proven equilibria/basin boundaries or relaxation guarantees for the full driven, diffusive medium. The recorded retention below is separate evidence; the supplied pilot patch must demonstrate its own retention.

| Sites in the high basin | INTACT | NO-R | NO-BACKREACTION |
|---|---|---|---|
| World 0 at t=200 | 8/25 | 2/25 | 0/25 |
| World 1 at t=200 | 8/25 | 4/25 | 0/25 |

The switched sites are still switched at t=300 in each branch carrier. This bistable retention is the mechanism R4 intended for H-BG. Recorded response gain rose under INTACT in both worlds:
- world 0: 0.1404 vs 0.0944 (NO-BACKREACTION) and 0.0987 (NO-R);
- world 1: 0.1092 vs 0.0946 and 0.0992.

**(c) Recorded exposed backgrounds show suppression and source loss; frequency stationarity is the common failing criterion.**
- The switched sites retain heterogeneous natural-frequency parameters Ω_a ∈ [−.3, .7]. Their actual frequencies also depend on diffusion and external drive; parameter heterogeneity alone does not establish the observed beating.
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
- H-BG and H-PS permit background change and suppression as meaningful two-sided CHANGE. The inspected cases raise concern that this particular registered H-RBG witness is difficult to discriminate; they do not establish that enablement or a mechanically complete chain is impossible.
- The proposal's self-audit flagged baseline saturation. These limited observations are consistent with that risk; §6 asks whether it persists in fresh paired populations under the unchanged law.

**Bounds.**
- This rests on two development worlds, corroborated by four withdrawn worlds and the equations. It is not a population rate.
- The coupling-magnitude argument is an order-of-magnitude consistency check, not a derivation of the observed values.
- It does **not** show that RRG is false or establish that the apparatus cannot discriminate enablement. Full source reading reinforces that termination, destruction, suppression, coexistence and reorganization can all be informative. R5 §§2/5–6, audited 04 §§4/9/11/13/28/37, 07 §2 and 08 H09/H13/O3/O1 keep those outcomes distinct from the stronger registered witness.
- The Q-versus-H contrast can isolate the effect of the supplied background construction. It cannot uniquely identify frequency heterogeneity as the cause: a later orthogonal intervention would be needed to separate it from other changes in the patch.

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

### F4 — MEDIUM — RO/PD. Historical native samples favour transcendental work; the two proposed savings are estimates.

- **Work per evaluation.** Per active cohort per right-hand-side evaluation (`field.cpp:78–98`):
  - 276 pair terms, each with `sqrt`, a merged `sin`/`cos` of the same phase (`__sincos_stret` in the profile) and `exp(-d²)`;
  - 600 site–member Gaussians `exp(-|q−x|²/8)`;
  - 24 `polar` and 25 `sqrt`.
  - In total about 876 `exp`, 300 `sincos` and 300 `sqrt`.
- **Consistency with the measured rate.** 0.12 s per active C0 across three grids is 1400 RK4 steps × 4 evaluations = 5600 evaluations, about 21 µs each. That is consistent with roughly 1450 libm calls. The early R006 profile shows 85% of samples in `evaluate`, of which libm `exp` is about 38% and `sincos` 12.7%.
- **Two exact reformulations of the same real arithmetic:**
  1. `cos/sin(θj−θi)` from the phasors already computed at `:78`, which removes 276 `sincos` per evaluation;
  2. the site Gaussian separated in the square-lattice basis (5+5 instead of 25 exponentials per member; this survives rotation and translation because the lattice is orthogonal), which takes 600 `exp` down to 240.
- **Estimated saving for these two transformations.** Applying historical profile shares gives about 27% of native samples, i.e. **≈1.37× on native time**, and less at world level. This is a rough profile-based scenario from a single 1.8 s sample, not a measured speedup or a proven upper bound on all exact optimizations.
- **Status of these proposed changes.** They are not bitwise identical and would need requalification by the existing 1e-10 reference battery. They are not a model change or "fast math". Historical grid agreement to about 3e-13 on near-threshold statistics cannot certify a future reformulation; decision flips must still be checked.
- **Conclusion.** The two proposed changes do not establish the required complete-world gain. Other exact optimizations are not ruled out, and the evidence does not prove that a resource change is unavoidable. The owner can consider a resource route after separate complete-world qualification.

### F5 — LOW — CD/UA. Live tooling gaps and guarded nonfinite paths; none changes the bounded five-area repair assessment.

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
| 1 | Registered `budget.workers` (`protocol.json`; gate `:114`; panel `run_c6_r4.py:57`) | rule arithmetic; host 10 cores / 32 GiB; 0.58 GB RSS per world | Per-world limit is 180 s × workers | Prospective resource change, e.g. 4–6 workers, with the limit restated from the new value | 360 → 720/1080 s per-world limit. **Net effect depends on unmeasured contention inflation.** | None to the equations. It is a **protocol/resource change** that needs an owner decision. | Separate authorized complete-world resource diagnostic if the owner chooses that route; §6 keeps 2 workers and cannot qualify increased-worker contention |
| 2 | Native `evaluate` (`field.cpp:78–98`) | early profile `def6fd7`: 85% `evaluate`, `exp` ≈38%, `sincos` 12.7% | ~876 `exp` + 300 `sincos` + 300 `sqrt` per cohort-evaluation; ≈21 µs estimated from historical marginal cost | Phasor identities for the pair `sin`/`cos`; lattice-separable site Gaussian | ≈1.37× native scenario for these two changes, from one 1.8 s historical profile; no global optimization bound | Not bitwise identical. Proposed implementation change needing the 1e-10 reference battery. | Reference battery + fixture + check that grid agreement is unchanged |
| 3 | Three grids sequential in `GridSet.run` (`assay.py:38–50`) | early profile: GIL-releasing native | Step multiples 1+2+4; the finest is 4/7 | Run the grids concurrently in threads | ≤1.75× native per world | Bit-identical. It is a resource-semantics change: the same CPU spent on more cores per world. Same owner decision as rank 1; do not count both. | Byte-identical flows vs sequential |
| 4 | Passive-ancestor re-integration (`c6_r4_field.py:193–208`) | structural; hit rate **unrecorded** | Up to ≈3880 passive cohort-C0 per world; 64 MiB LRU of ≈1.95 MB entries | Turn-scoped or pinned exact-key cache | Unknown; measure hits first | Exact; ≈0.59 MB per C0 per ancestor | Hit/miss counters |
| 5 | Duplicate 10-C0 causal/recovery-control runs (`assay.py:110,139`) | structural | ≈170 of 4640 active C0 | Exact-input reuse | ≈3.7% | Low; all rows still emitted | Byte-identical rows |
| 6 | Per-call `native()` re-hash; 4-entry drive cache | code; `drive` 3.9% of early profile | ≥2.7k hashes per world | Hash once per run; enlarge the cache | Small (<1–4%) | Coarser identity guard | Contract tests |

**Excluded:** fewer probes, truncated horizons, coarser grids, skipping zero-mask channels, shared random draws, fast-math, and a longer timeout alone.

**Accounting outside the timer** (`protocol.py:134–176`): per world, 60.1 MB of JSON (81% descriptor raw), gzip, process start, imports, native load, and the reference battery. These must be recorded separately in `b_costs`, without changing the registered timing variable.

## 5. Route

Runtime and feasibility are separate questions:
- F2/F4: a prospective resource decision and qualified exact implementation work may address cost. Complete-world sufficiency and contention remain unmeasured.
- F1: fresh data are needed to distinguish an apparatus-level discriminability concern from an overgeneralization of a few worlds. Faster code preserves the model's dynamics at the same inputs; that does not prove the population concern.

**Recommended next step: Claude source-read/route confirmation, then owner review of Revision 3.** The ChatGPT recheck specifically requires Claude to complete the full source read before pilot approval; Codex's editorial source read does not close that role-specific gate. Once confirmed, the owner may authorize the bounded current-R4 Q-versus-H diagnostic in §6. It addresses one question before any search for an enabling model or stronger resource regime. Sixteen pairs are a fixed exploratory workload, not a demonstrated statistically minimal sample size.

**Conditional leading route: a separate prospective scientific-model redesign study if outcome A supports the ceiling and suppression/stationarity concern.** Its purpose would be to test a discriminating apparatus for the stronger registered recursion witness. The pilot does not approve that study, select its equations or establish that R4 cannot work. The owner chooses after reviewing the recorded result.

A later redesign study should keep unit/closure criteria prospective, preserve two-sided effects and avoid turning suppression into a universal failure. If phase organization and site-frequency heterogeneity are candidate mechanisms, vary them as orthogonal prospective factors. The removed Revision 2 C arm changed both common phase and Ω_a to 0.2: it would test a combined existence construction, not identify coherence or entrainment as the cause. No such arm or K/J search belongs in the first diagnostic.

**Fallback: engineering/resource continuation of unchanged R4 under unchanged readiness rules**, if outcome B weakens the ceiling concern or the owner prefers further R4 measurement. F3/F5 corrections, exact kernel work, full-world repair qualification, any worker-count change and fresh development registration need their own concrete approved scope. Availability of the next revision identifier must be checked then; this report neither reserves nor authorizes R007.

**Indeterminate/incomplete:** return the result to the owner without choosing redesign or starting another diagnostic. Pause C6 remains a real option. RRG publication does not depend on C6, and valid first-turn H-BG/H-PS directions are not erased by a failed stronger witness. Waiving chain readiness after observed failures would be a disclosed scope change, not an engineering repair; it is not proposed here.

## 6. One bounded next diagnostic (specified, not executed)

| Field | Specification |
|---|---|
| Purpose / decision answered | Under the current R4 law, does quiet Q show near-ceiling formation, and does a supplied heterogeneous high-basin H background reduce formation or persistence with frequency-stationarity failures? This diagnoses the apparatus concern; it does not identify the unique cause of beating or choose a new model. |
| Fixed design | **16 fresh paired populations × Q/H = 32 qualification attempts**, current K=1 and J=0.8 only. No coupling search, coherent arm, Ω_a replacement, descriptor assay, source-operation treatment branches, or recursive world. For pair indices 0–15, construct `medium(rng(pilot_entropy, pair, 1), settings['model'])`, use three independent grid owners, and evolve for 100 C0 without cohorts. Clone the evolved grid separately for Q/H with separate check lists. Q is unchanged. In H, set the 8 nearest sites to the generation-1 centre (2,0), transformed by the unchanged scene frame, to radius 0.8744 with independent uniform phases from `rng(pilot_entropy, pair, 90)`; tie-break by site identity and use the same assigned phases on all grids. Keep every other field entry, Ω_a, geometry, drive, boundary, absolute time and scene frame unchanged. This supplied initial condition is not a unit-produced background. |
| Exact workload / helpers | Preserve the `qualify_episode` sequence but call its existing helpers in the scratch harness: `introduce(background, pilot_entropy, pair, 1, 0)`; current `physical_perturbations(rng(pilot_entropy, pair, 20, 1, 0), owner)`; `grid.run(settings['formation'], scope)`; then `qualification(grid, prefix, perturbations, scope)`. Save the introduced state and returned three-grid formation prefix before qualification. Keep the current 24-element generator, 100-C0 formation, 30-C0 detector window, recovery/causal checks and three grids. Do not pre-stage a unit. For each qualified candidate, clone its qualification-end grid, assign its selected member inventory on each owner and keep output=0, then run one 100-C0 continuation. Apply `rolling_persistence(prefix[k], continuation[k], end_owner[k], members, settings)` on each grid, retaining the original formation prefix and clock; require identical pass/fail masks across grids. This is **initial qualification plus rolling structural retention**, not continued full qualification: it omits the endpoint recovery/causal check used by `operation`. Do not call `operation` or `run_world`. |
| Inputs / entropy | Prospectively commit a new pilot-only entropy namespace disjoint from every registered development, smoke, bootstrap, reference, fixture and final purpose before generating inputs. No final entropy is generated. R004–R006 inputs are not reused. Each pair shares material positions/phases/rates, identities/priorities and perturbations across Q/H and grids. Field/carrier arrays retain their own arm's background, as the current generator requires; H phases use a separate named purpose. Prior exposure: none. Schedule pairs in index order, with Q first for even indices and H first for odd indices; no outcome-dependent scheduling. |
| Code and record | Scratch harness outside `geomind/`, approved R4 functions used read-only. Specification, script, dependency identities, pairing/schedule and resource rules committed before execution. Scripts, all raw outcomes and a README declaring exploratory status committed in the same session under `evidence/c6_dev_pilot/r4_sensitivity/`; existing pilot files remain untouched. No source, protocol, accepted-code, evidence-receipt or gate-stamp edits. |
| Dependency / implicit-build guard | Before any native call, record and compare current Python/helper, protocol, environment, audited-source, native-source, dylib and BUILD.json identities against the prospectively approved inventory. `_native_checked` can call `build.build()` on a stale/missing artifact; the pilot authorizes no build. Missing/mismatched source or binary therefore stops before native loading. Do not patch the loader, bypass its guards or permit concurrent build/source writes. An unexpected rebuild attempt or dependency drift makes the pilot incomplete; return to the owner for a separately scoped build/requalification decision. |
| Measured | Every attempt's returned qualification object, production-grid candidate inventory/raw structural values, returned three-grid recovery/causal values, stage checks and three-grid formation prefixes with input/owner identities. `qualification` returns structural candidate rows only for grid 0: retain the finer raw prefixes, label unavailable finer structural rows explicitly, and never claim the helper emitted them. For qualified candidates, retain all three continuation trajectories and rolling rows, first loss time and criteria. Save actual and carrier field amplitudes by site throughout formation/continuation. Wall/CPU split into setup, background, formation, combined qualification, continuation and serialization; separate recovery/causal timing and native/cache counts remain unmeasured unless existing outputs expose them. No monkey-patching or new observer inside project code. |
| Semantic / retention checks | Same equations, generator, detector, thresholds, perturbations, grids and refinement rules. At introduction, Q has no site above radius 0.485206 and H exactly 8; a mismatch is a construction/integrity stop, with no redraw. For a retained-patch inference, each of H's 8 original sites must stay above that radius in the candidate's carrier at every saved formation/continuation frame on all grids; Q must remain below it. Record any failure without replacement; it makes the retained-patch route inference INDETERMINATE, not an invalid scientific failure. Actual and carrier may not be confused: material incoming drive reads the cohort's carrier (`field.cpp::evaluate`), initialized from its own arm by `population`. Check Q/H material arrays and perturbations agree exactly, allowing the intended field/carrier difference. Numerical/nonfinite/grid inconsistency makes the run incomplete. |
| Normalization ledger | One material/field level only; no upper-level prediction API. Positions and sizes: L0, existing radius/spacing normalization. Phases: rad; half-window frequency change: rad/C0, unchanged tolerance 0.01. Formation/window/continuation: C0, current dt=0.005, factors 1/2/4. Field amplitude: current dimensionless z units; site count out of 25. Initial qualification and initially-qualified/structurally-retained proportions: fixed denominator 16 per arm, with unqualified attempts counted as not retained and recorded separately. All four paired outcomes are reported, including Q failure/H success. Conditional retention summaries name their smaller denominators and cannot replace the fixed-denominator contrast. Wall/CPU: seconds; RSS/storage: bytes. Raw reads remain owner/evaluator-side. |
| Limits / rationale | Keep the current **2 worker processes**, at most one arm per worker; no worker-count experiment. Hard total wall cap **900 s (15 min)** including setup and shutdown, aggregate run CPU cap **1800 s**, **2 GiB RSS per worker**, and **300 s wall per arm** including qualification and continuation. These are pilot resource limits, not altered C6 readiness limits. Historical marginal cost suggests roughly 26 s for qualification plus 12 s for continuation per arm, about 10 min for 32 arms at 2 workers before setup/contention. That estimate is unverified; the cap may yield an incomplete result and is never extended automatically. |
| Automatic deadline / cancellation | Parent monitors monotonic wall, aggregate CPU including descendants, per-arm wall and RSS during native calls; do not rely on a future timeout that waits for executor shutdown. At 870 s global wall stop submissions, cancel queued futures with `cancel_futures=True`, and terminate only this pilot's worker process groups; allow at most 5 s grace then kill survivors, with summary/shutdown inside the 900 s deadline. Apply the same cancellation on any per-arm/CPU/RSS cap or integrity failure. Use worker-owned processes and tracked IDs; never kill unrelated processes. Count setup, failures and canceled work. No retry or replacement. |
| Partial-evidence preservation | Prewrite the 16-pair Q/H inventory and flush atomic parent-owned checkpoints after background, introduction, formation, qualification and continuation returns. Flush completed arm records as JSONL; retain only complete lines after interruption. The existing helpers expose no in-call checkpoint callback: an interrupted native/qualification call may lose its in-flight trajectory/fork arrays. Record that stage as incomplete and retain the last completed checkpoint; do not promise or reconstruct unseen partial frames. Keep completed/failed/interrupted states and all failed work. A killed arm is `INCOMPLETE_RESOURCE_STOP`, never a scientific rejection. No retries, replacement, exclusions, denominator shrinkage or A/B classification from partial results. |
| Outcomes, fixed prospectively | **INCOMPLETE takes precedence** for any missing arm/required trajectory, numerical/integrity failure or resource stop. With all 32 attempts complete, let q/h be initial qualification counts and sQ/sH be initially-qualified candidates whose rolling structural masks pass throughout continuation, out of 16. If q≤8, **B (quiet-formation concern weakened)** downgrades only the ceiling part of F1; report retention/patch status separately. Otherwise a retained-patch failure yields **INDETERMINATE** for the apparatus mechanism. With retained patch and q≥14, evaluate two predeclared A rules separately: the qualification rule needs q−h≥4 and the retention rule needs sQ−sH≥4; each additionally needs at least 4 Q-success/H-failure pairs with its strict stationarity association below, comprising more than half of that contrast's discordances in that direction. **A (concern supported)** if either rule passes; report both rules, both paired contrasts and reverse discordances without pooling or dropping the weaker result. **Otherwise INDETERMINATE.** These exploratory counts do not establish a population rate, unique mechanism or C6 verdict. |
| Stationarity association / counterexample control | Report qualification and structural-retention contrasts separately; outcome A identifies which, if either, meets its predeclared rule. For a qualification contrast, H must be unqualified with no structurally accepted candidate, and at least one minimum-size candidate must pass every other structural criterion while failing frequency stationarity. This is a structural association only: its untested recovery/causal validity remains unknown. For a retention contrast, H must initially qualify and its selected candidate's **first failed rolling window** must fail frequency alone, with other structural criteria passing on all grids; the paired Q must remain structurally retained. Unrelated rejected clusters, mixed failures, no candidate, recovery failure or causal failure do not count as stationarity association. Example: an H population fails recovery while an unrelated rejected cluster exceeds freq_tol; that cannot support A. |
| Boundaries | Exploratory pilot only: no C6 evidence/readiness, no H-BG/H-PS/H-RBG verdict, no full-world repair qualification and no increased-worker contention claim. H is supplied, not generated by a qualified source; Q/H combines patch amplitude and phase initialization, so it cannot uniquely isolate frequency heterogeneity or prove entrainment. No regime/model/threshold selection follows automatically. Return the recorded result for review before any further study or registered development revision. |
| Authorization | First close the recheck's Claude full-source-read/route confirmation gate. Then a new explicit owner pilot authorization is required; 0026 and this edit are review-only. §8 covers only this diagnostic and recording its result, with no build or conditional later execution. |

## 7. Forward sequence

This report performs none of these steps.

1. **Revision 3 documentation and self-recheck only.** Retain the original repair assessment ACCEPTABLE_WITHIN_REVIEW_SCOPE. Codex completed its source reading and corrected the planning defects; **Claude must still confirm its own full required source read and this route** before pilot approval under the ChatGPT recheck. No fresh independent acceptance or hypothesis verdict. C6 remains BLOCKED.
2. **After that confirmation, owner decision** before any pilot, repair or run. Per 0026 revision 2 §2, no existing authority covers this work:
   - 0025's execution scope (fixture, then pipeline through smoke) is consumed;
   - 0023's one-shot replacement is consumed (0024);
   - 0024 requires a new owner-directed revision before development;
   - 0026 is review-only.
3. **If authorized, prepare and commit only the §6 pilot specification and harness**, complete any authorized harness validation as one batch, then generate pilot inputs. No new scientific model, K/J search, source changes or final entropy.
4. **Execute that diagnostic once.** Preserve raw and partial results, commit scripts/results/status README in the same session, and return the result for review. No retries, replacement populations or automatic search.
5. **Owner chooses after that review:** unchanged-R4 engineering/resource continuation, a separate prospective redesign study, a new registered C6 revision, or pause. Outcome A favours considering the separate redesign study; B weakens F1; INDETERMINATE/INCOMPLETE retains uncertainty. No outcome authorizes another execution. A later study separating phase organization and frequency heterogeneity must specify those factors prospectively; a combined positive control can establish only existence within its supplied model variant.
6. **Any future registered revision:** approved proposal and normalization ledger; fresh namespaces and registration; F3/F5 repairs and selected optimization/resource work as authorized; one end-of-batch validation; then one complete fresh development readiness gate. Retain R006 and its STOP unchanged. Only after complete readiness/integrity PASS may the authorized final-entropy/registration lifecycle and ordered pipeline (preflight → tests → smoke → mutation → panel) proceed, followed by cross-family evidence review. This edit supplies none of those gates.

## 8. Proposed owner decision text

> **PROPOSED, NOT APPROVED.**
>
> **Prerequisite:** Claude has completed and explicitly confirmed the full required current-source read and the corrected Revision 3 route. This proposed text cannot itself waive that open recheck requirement.
>
> 1. **Scope.** One minimal current-R4 Q-versus-H diagnostic exactly as specified in Revision 3 §6; no other C6 execution.
> 2. **Model and protocol changes:** none. Keep current K=1, J=0.8, heterogeneous site frequencies, qualification/detector thresholds and three-grid numerics. Q/H differ only by the prospectively specified supplied high-basin patch; no coherent-medium variant or coupling search.
> 3. **Authorized:** prepare and commit the pilot specification, scratch harness and any required harness-only validation as one batch before pilot execution, then execute once:
>    - 16 paired populations, 32 qualification attempts, with the specified fixed persistence continuation for qualified candidates;
>    - a fresh pilot entropy namespace;
>    - scratch code outside `geomind/`;
>    - output `evidence/c6_dev_pilot/r4_sensitivity/` (the AGENTS pilot location; existing pilot files untouched).
>
>    Commit the specification, script and dependency/entropy policy before generating pilot inputs. Commit scripts, raw results and the exploratory-status README in the same session.
> 4. **Resource caps:** 2 workers, 900 s total wall including setup/shutdown, 1800 s aggregate CPU, 2 GiB RSS per worker, 300 s wall per arm. Begin global cancellation at 870 s; no cap extension.
> 5. **Stop behaviour:** automatic in-call supervision, queued cancellation, tracked worker-process-group termination, atomic preservation and failed-work accounting exactly as in §6. No retry or replacement; partial/invalid runs remain INCOMPLETE.
> 6. **Return gate:** report and review the stored result, then obtain the owner's route decision. No later redesign study, implementation or development execution is conditionally covered.
> 7. **Not authorized:** builds or implicit rebuilds, any registered development world, final entropy, mutation, panel, increased-worker benchmark, coherent arm, K/J search, R4 threshold/readiness changes, rescoring of R004–R006, or C6 status changes. Missing/stale native artifacts stop before loading, as in §6.

## 9. Self-attack

- **The F1 inference rests on 2 + 4 worlds.** Recorded candidates share backgrounds and are not 26 independent population trials. The 16-pair pilot is exploratory, cannot establish a population ceiling, and has explicit downgrade/indeterminate outcomes.
- **Counterexample to the mechanism.** Drift might come from population transients: similar frequency failures in paired Q defeat an H-specific explanation. H may suppress through patch amplitude or phase relationships rather than site-frequency heterogeneity: the first pilot cannot separate these causes. *Detection:* all Q/H criterion and trajectory rows remain visible; a later orthogonal intervention needs a separate approved design.
- **Selection by outcome.** Only two fixed backgrounds and current K/J. No regime target, coherent arm, adaptive count or control-only regime selection. All 16 pairs remain in the inventory.
- **Cache warmup and workstation noise.** Alternating arm order reduces a simple first-arm bias but does not eliminate contention. Timing is cost accounting on this host, not performance qualification or a higher-worker resource recommendation. Both CPU and wall include failed work.
- **Differing instrumentation.** None is added inside `geomind/`. Timing is per population at the harness level.
- **Cache aliasing, cross-grid or cross-treatment contamination.** Keys were traced (§2). The pilot has no treatments. Rank-4 reuse is exact-key only.
- **Floating-point ordering (rank 2).** Proposed exact reformulations remain unimplemented and need requalification at 1e-10. The historical ≈3e-13 grid agreement is not qualification of a future kernel. Any decision flip is a sensitivity finding, not hidden.
- **Nonfinite concealment.** The original review traced guards on F5's nonfinite paths, without proving them unreachable. Its separate live tooling defects remain; collect prospective corrections in the next authorized batch.
- **Omitted ancestor or zero-mask work.** No proposal skips either. Compute-before-mask was verified.
- **Memory amplification.** Ranks 1/3/4 may raise peak memory and need separate measurement. This pilot keeps 2 workers with monitored RSS and no larger cache.
- **Altered denominators or missingness.** The pilot counts every population, including invalid ones. No proposal changes episode counts or masks.
- **Claims carried from old code to new code.** R006 timings belong to `def6fd7`. No speed claim is made for `8561ab5`.
- **Control effects and negatives stay visible.** Suppression, ceiling-level control formation and source loss are reported as observations, not converted into verdicts or hidden as engineering failures.
- **Counterexample to the worker-count fix.** Memory-bandwidth or thermal contention at 6 workers could inflate complete-world cost beyond the proposed budget. The first diagnostic cannot detect or qualify that fix; a separate authorized complete-world resource measurement would be needed if the owner chooses resource continuation.
- **Supplied-background limitation.** H could leave the high basin early or behave differently from a source-produced field. *Detection:* record every site's amplitude and frequency alongside the candidate trajectories. Report that limiting-condition failure as indeterminate rather than changing the patch or rerunning.
- **Cancellation is part of the apparatus.** `cancel_futures=True` alone cannot stop an in-flight native call. Parent process-group supervision and the shutdown reserve must exist before the pilot starts. A partial pair never becomes a completed negative and cannot satisfy A/B.
- **False stationarity attribution.** An unrelated small cluster can fail freq_tol while the chosen population outcome fails recovery. Counting that cluster would falsely favour redesign. §6 now counts only explicitly linked qualification/first-loss associations, with mixed/recovery/causal failures reported separately.
- **Structural survival is narrower than unit persistence.** All rolling structural windows can pass while an endpoint causal or recovery test would fail. §6 reports initial qualification plus structural retention, not a continued qualified unit or a complete C6 chain; no extra endpoint assay is silently added to this diagnostic.
- **Hidden rebuild.** A first `native()` call can compile and rewrite BUILD.json if the loader sees stale artifacts. §6 requires a pinned, existing matching artifact and stops before loading on mismatch. This is a scope guard, not permission to bypass the native integrity checks.
- **Unobservable partial work.** A worker killed inside `qualification` cannot return its in-flight forks. Save introduction/formation first; mark interrupted qualification incomplete with the last returned checkpoint. Atomic writes do not recover arrays the helper never exposed.

## 10. Yes/no stops

| Yes/no condition | One action | Responsible role | Status here |
|---|---|---|---|
| Critical evidence missing/mismatched or changed code unqualified? | Mark the affected conclusion NOT_VERIFIED. | Reviewer | Full-world behaviour of `8561ab5` is NOT_VERIFIED. Hash matches are historical original-review observations, not new checks. |
| Claude has not confirmed its full required source read and corrected route? | Keep the planning report at REVIEW_READY_FOR_CLAUDE_CONFIRMATION. | Reviewer | **OPEN.** Codex source reading does not satisfy the role-specific ChatGPT recheck condition. |
| First diagnostic adds K/J search or a coherent-medium variant? | Remove that work from the first diagnostic. | Drafter | §6 includes only current-R4 Q/H. |
| Two changed causal factors are attributed to one mechanism? | Narrow the attribution to the combined construction. | Reviewer | No unique frequency/coherence inference; any later separating study must vary factors prospectively. |
| Complete pilot fails to support ceiling/suppression? | Return the downgraded or indeterminate F1 assessment to the owner. | Reviewer | B/INDETERMINATE defined before execution. |
| Deadline, CPU, RSS or per-arm limit reached? | Cancel and preserve an INCOMPLETE result. | Implementer | No retry, denominator shrinkage or A/B classification. |
| Native/source/environment identity is missing, mismatched or changing? | Stop before native loading with an incomplete dependency record. | Implementer | Pilot build/requalification is not authorized. |
| Supplied H does not retain the patch while Q stays quiet? | Report retained-patch mechanism as INDETERMINATE. | Reviewer | Complete quiet-formation counts may still weaken the ceiling concern; no patch retuning. |
| Pilot outcome is being counted as C6 evidence/readiness? | Withdraw that interpretation. | Reviewer | §6 cannot qualify C6 or assign a hypothesis verdict. |
| A point needs new execution? | Describe the diagnostic without running it. | Reviewer | §6. |
| A proposed speedup changes the approved scientific contract? | Label it a prospective protocol/model change. | Reviewer | Ranks 1/3: resource changes; rank 2: proposed implementation change needing requalification. None is included in the first diagnostic. |
| A missing measurement is being treated as a demonstrated failure? | Replace the inference with its actual bounded status. | Reviewer | Chain-complete cost, contention and population-level ceiling are labelled inference or pilot questions. |
| A next execution lacks applicable authorization? | Leave it unexecuted at the owner-decision gate. | Implementer | Nothing executed. §8 is PROPOSED. |
| The review cap ends with critical scope uninspected? | Deliver findings with an explicit non-acceptance boundary. | Reviewer | Analysis/bootstrap and `c4_detect` are NOT_REVIEWED. Repair acceptance is limited to the inspected diff. |

## 11. Revision 3 correction ledger

Finding IDs here refer to the ChatGPT recheck; §2 retains the original Claude finding IDs.

| Recheck finding | Correction / remaining boundary |
|---|---|
| F1 — incomplete source reading | **PARTIAL / ROLE GATE OPEN.** Codex read full R5, audited README, full 04, full 07/08, ERRATA and 05 and corrected the interpretation. Claude's own required source-read/route confirmation remains outstanding before pilot approval. |
| F2 — nonminimal pilot | Replace 144 populations/9 cells with 16 paired Q/H populations under unchanged current R4. One fixed persistence continuation addresses the stated persistence question; no additional design/performance search. |
| F3 — coherent-arm confounding | Remove C entirely. Any later combined phase/frequency construction is existence-only unless separated by prospective orthogonal factors. |
| F4 — repair wording contradiction | Restrict the favorable wording to the five inspected repairs and keep live F3/F5 defects explicit. |
| F5 — route overstatement | F1 is an apparatus concern, not impossibility. Redesign is conditional/provisional; fallback, indeterminate, incomplete and pause remain real. |
| F6 — bounded independence | Preserve the original involvement disclosure and ACCEPTABLE_WITHIN_REVIEW_SCOPE. Disclose Codex editorial authorship; no fresh cross-family acceptance or lifecycle change. |
| F7 — metadata format | Current editorial reviewer correctly identified as Codex:GPT-6; original reviewer explicitly retained as Claude:claude-opus-5-5. No original-family label is used as a current acceptance stamp. |

## 12. Owner-requested adversarial self-recheck

This is the correction record for defects in the first Codex Revision 3 edit; the revision number stays 3. No project execution was used to check or repair them.

| Finding | Evidence / defect | Correction and remaining boundary |
|---|---|---|
| S1 — HIGH — reviewer-role gate | Recheck F1 explicitly requires Claude's full source read; Codex completion cannot be relabelled as Claude completion. | Actual editorial reviewer identified; gate OPEN in verdict, sequence, stops and proposed decision. |
| S2 — HIGH — overclaimed persistence | `rolling_persistence` checks structural windows; `operation` separately calls endpoint `qualification`. The pilot omitted that latter check. | Name the endpoint initial qualification plus structural retention; no full-unit persistence or readiness claim. |
| S3 — HIGH — false failure attribution | `qualification` returns all production-grid candidate rows, including unrelated rejected clusters. | Strict association rules and a recovery-failure counterexample; report mixed causes and reverse paired outcomes. |
| S4 — HIGH — implicit execution outside pilot scope | `c6_r4_field._native_checked` calls `build.build()` on missing/stale binary metadata. | Prospective dependency/native-artifact guard; no builds or loader bypasses. Live binary identities are not checked by this document edit. |
| S5 — MEDIUM — infeasible observation/checkpoint promise | Qualification returns structural rows only for grid 0 and exposes no in-call checkpoint callback; GridSet checks are shared through clones. | Save independent arm check inventories and returned three-grid prefixes, stage checkpoints before qualification, and explicit missing fine-row/in-flight data. Combined qualification timing replaces unsupported recovery/causal timing splits. |
| S6 — MEDIUM — retention assumption not enforced | Radius 0.485206 comes from the scalar unforced drift, not a guaranteed boundary in the full diffusive/driven medium. | Record carrier-site retention prospectively and return indeterminate on failure; no retuning or redraw. |
| S7 — MEDIUM — false global optimization bound | One short historical profile and two candidate reformulations cannot rule out all exact optimization paths. | Savings labelled a scenario; remove the claim that changing resources is unavoidable. |

**Remaining gates:** Claude full-source/route confirmation; owner decision; a committed, dependency-pinned harness with functioning supervision and recording; then one authorized exploratory diagnostic. The harness is specified, not implemented or operationally validated in this report. No repair, readiness, mechanism or independent-acceptance gate is supplied by prose alone.

C6 stays BLOCKED at R006 STOP. Revision 3 accepts no C6 result, assigns no hypothesis verdict, does not resolve scientific readiness, and does not change the source theory. Planning remains REVIEW_READY_FOR_CLAUDE_CONFIRMATION before owner pilot approval; this is not a new independent Claude acceptance.
