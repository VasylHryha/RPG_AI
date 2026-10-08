CHANGES_REQUIRED — initial quick build recheck

Reviewer family: Codex (separate same-family agent; cross-family review not performed).
Reviewed HEAD: `7959a107b57b1c93db16e17ac145ce1bfa0c35c4`.
Scope: new S0/S1 files and handoff, against revision-3 design commit `cac370a4ab08af98d59cccd63ecaa7c3f66a81ac`, decisions 0035/0036/0037, and unchanged native lifecycle/planner sources. Static inspection only: no tests, project code, native build or fights run. This is a development build recheck, not independent acceptance of experiment results. PLAN_CURRENT.md remains unchanged under the owner's explicit instruction.

Owner request received verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Initial inspected SHA256:

| File | SHA256 |
|---|---|
| s0_analysis.py | 7d510f43b42c99a8e22d212f1d8ca0a4fb32033cbbdd03dda8e07edb8f986961 |
| s1_pilot.py | a7e9a81f572f711841eaddb0e953f8d450756119bfbc9282b31919170944cb39 |
| s1_metrics.py | 144bf09ccc9f6f670efc6cecfeafb881887a44ea26da8eb14f9e9cd74d489378 |
| s1_controller.cpp | cd7490cbdafeb0a34a91a58909fc69a956b001efc3e9a0ac5e4e5db3cfeea740 |

### Findings requiring correction before host fights

1. **Historical seed exclusion is incomplete.** `s1_pilot.forbidden_seeds()` scans the current slice and three local subtrees only. It misses historical shape-lab/mechanism/fixture/partial-attempt seed ledgers, including `../s4_shape_lab_v4/raw/SEED_LEDGER.json`. Fresh entropy makes a collision unlikely but does not enforce §7's symmetric exclusion requirement. Inventory all relevant historical ledgers and request/attempt seed records; retain a compact hashed source inventory and test exclusion of a seed outside this slice.

2. **Contestedness admission omits changed commanded assignment.** `s1_metrics.summarize()` increments `changed` when paired launch aim patterns differ at a plan-origin decision. It never verifies that the proposed command differs from autonomous focus/assignment on that decision, and it does not retain an impact-pattern comparison. Aim-point differences or chaotic timing divergence alone cannot establish the design's combined changed-assignment and physical shell/impact response gate. Record per-plan commanded versus autonomous assignment at the shared wrapper-arm state, join native starts/launches by plan/cast identity, and report assignment response and physical response separately with explicit denominators. Use their required conjunction for admission.

3. **S0 treats independent Singles as a multi-gun assigned plan.** `s0_analysis.analyze()` sets `multi_assigned_ticks` from `len(teacher_planner diagnostics)>=2`; historical `teacher.cpp` emits that diagnostic for Singles and Left as well. This can pass the 5% readiness/cell stop while no joint group command exists. Separate all assigned rows from non-Singles/non-Left multi-gun coverage; if distinct joint-plan identity cannot be reconstructed, mark that denominator/stop unresolved instead of reporting a definite pass.

4. **Twenty-pair extension can proceed after wrapper defects.** `s1_pilot.run('extend', ...)` currently blocks admitted cells and some already-resolved detectability cases, but permits extension after lock/residual/snap/raw-miss failures whenever detectability is also unresolved. The design calls for revising the wrapper on these failures, and the handoff explicitly prohibits extending them. Refuse extension when either wrapper correctness or raw moving-miss stop is YES; only unresolved miss coverage or detectability may qualify.

5. **Required enemy dash count is absent.** Decision 0037's addendum specifically requires S1 to count enemy dash events, with zero expected because native dash reacts to player shots. `measure()` counts existing collector stages but there is no explicit enemy dash hook/counter; absence of a stage is not a measured zero. Add a new-file instrumentation seam that observes actual enemy dash transitions and reports an explicit count in every per-fight/cell receipt. Keep movement stepping and dash events distinct.

6. **Mutable cap authority is an operative hash pin.** `pins()['cap_authority']=cap()` includes the mutable LAB_CAP SHA256, and `inventory()` compares the full pins dictionary. §7 excludes mutable cap files from operative execution hash manifests. Retain the approved commit/code pins separately; read and validate current cap authority at each stage, record the actually used authority/hash as invocation provenance, and enforce a numeric ceiling that cannot silently enlarge the sealed pilot extent. Do not make a mutable cap document part of the immutable source-pin comparison.

### Bounded positive checks and remaining limits

The code uses new-file generated native seams, a copied planner with explicit candidate focus provenance, script-only arms, shared native action projection, one cached release refresh, paired raw misses, Gaussian SD inflation at both final sample sizes, ratio-of-totals jackknife spread, all-draw outcomes, fail-closed process discovery and charged failed-attempt accounting. Existing originals and collected data are not edited by the inspected code. These checks do not establish compile success, native correctness, actual wrapper-miss coverage, runtime admission or cell utility; the host sample and focused end-of-batch tests remain necessary.

Implementer owns fixes and a concise disposition here. Recheck repetition is needed only for these actual defects, under decision 0036. No numeric quality score assigned.

### Correction reread within the same quick recheck

The implementer corrected all six findings during this review. Static reread confirms: historical inventory/seed/ledger discovery spans the tactical workspace; per-decision changed focus or gun-bound aim assignment is counted alongside paired launch/impact response; S0 excludes Singles/Left from the group-command numerator; extension explicitly refuses correctness/raw-miss failures; a new rules overlay records enemy dash transitions and reports explicit zero counts; and cap authority is separated from immutable source pins while read live for execution. New rules objects replace the ancestor rules object in the link, preserving the original.

Corrected disposition: **no unresolved blocking finding in this bounded static recheck**. Remaining validation is focused end-of-batch tests and host compilation/sample/admission. Actual runtime, memory, legal native coverage and moving miss cannot be certified from source inspection. Spatial assignment here means a changed focus or changed gun-bound commanded aim point; it does not assert that the focus pointer must change on every joint plan.

## Implementer disposition

All six findings corrected before host fights: workspace-wide historical/partial/fixture seed inventory; same-state spatial assignment changes plus joined native root-shell/impact response; non-Singles/non-Left S0 coverage; explicit wrapper-defect extension refusal; a native enemy-dash instrumentation overlay and explicit per-fight/cell count; mutable owner cap separated from immutable execution pins. Spatial assignment includes focus or supported gun-bound point, with splash/4 response thresholds. The physical admission numerator uses same-state shadows, not cross-arm chaotic trajectories.

The reviewer reread the six correction seams and reported no remaining definite static blocker within the time cap. Build/tests/read-only S0 and host native-sample validation are separate bounded checks. Requested revision-3 raw wrapper-miss veto remains operative; later design-review suggestions do not silently relax it. PLAN_CURRENT.md remains unchanged.

## Verification/disposition evidence

- Native bridge compilation: PASS, 11.3408 s, zero physical fights. The first preflight exposed the existing committed BUILD_TOOLING_AMENDMENT; the build now uses the repository’s admission() implementation instead of rejecting its authorized tooling amendment.
- S0: 200 sealed raw fights analyzed in 221.7391 s; read-only. Strict boundary masks use an isolated native-libm adapter, matching the existing stage1_arithmetic recipe without importing Torch. Raw data/receipt hashes were checked. Ready-only non-Singles group coverage is below 5%; missing group provenance and sparse collision coverage remain explicit.
- Final focused tests: 16 passed, 0.3676 s total (pytest 0.16 s). One prior fixture test failed because its threat horizon did not permit physical escape; its result is preserved, then the fixture was corrected before the final batch.
- S0 commit: blocked by sandbox `.git/index.lock` permission; exact scoped host command in S0S1_HOST.md. No fights, S1 cell verdict, measured S1 projection or outcome entropy allocated here.
- Markdown presentation fixed after S0, without recomputing measurements; the executed source digest is retained separately from the final formatter digest.

Final reporting completeness correction: explicit per-arm won/lost/timeout descriptive splits, fire-opportunity rates with null zero-denominator handling, and own-splash-hit counts are now included. Paired admission still uses all draws. The complete focused batch passed 16 tests in 0.5181 s (pytest 0.30 s); receipt S0S1_TESTS_COMPLETE.json. No native code changed after its successful build.
