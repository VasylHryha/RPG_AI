CHANGES_REQUIRED
Reviewer family: Codex
Reviewed commit: ea34db460a3b14339d7159a142877774a1bb9de7 (ea34db4)
Reviewer model: GPT-6
Review date: 2026-10-07

## Scope and conclusion

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Reviewed the R2 report, analyzer, ten comparison receipts, summary and reconciliation; the original study and round-1 F1–F6; the proposed tolerance, performance deep-dive, protocol, sequential and parallel evaluators, detector, analysis guards, stored run/build receipts and selected compressed raw worlds. This is a cross-family owner recheck of Claude's engineering diagnostic, not milestone acceptance or authorization to adopt a numerical change.

**The measured conclusion is supported:** small observed numerical differences, no recorded outcome change in the ten sampled worlds, and approximately 25% lower measured compute CPU. R2 correctly withdraws `SAFE_UNDER_PROPOSED_TOLERANCE` and the panel-risk estimate. Kernel identity and the exact baseline remain substantiated. I found no observed flip in the raw spot-checks.

**Two medium corrections remain:** the reproduction script does not enforce every input/dependency identity it claims to enforce, and the decision ledger still omits or misclassifies stored-data validity checks. Neither finding demonstrates corrupted current inputs or changed outcomes. Both can be corrected in a new stored-data-only delivery; no worlds or panel computation are needed.

## Round-1 dispositions

| Finding | R2 disposition | Review result |
|---|---|---|
| F1 — decision coverage | Paired-gain refinement added; grid-dt persistence/endpoint pair windows reconstructed; missing trajectories/fine grids and primary analysis disclosed | **PARTIALLY RESOLVED.** The important scope correction is sound. Remaining guard inventory and the claim that every stored-value family is assessed need correction; see R2-F1. |
| F2 — unsupported panel probability | Removed; future-panel risk explicitly unquantified | **RESOLVED.** No probability or conservative bound is established or required by the revised observation. |
| F3 — margin arithmetic and closest lock | Separate signed margins, moving causal thresholds, strict operators, emitted flips and corrected lock case | **RESOLVED for the stated assessed families.** Raw arithmetic spot-checks agree; pair links are explicitly NumPy recomputations. See N2 for a reconstruction-validation limit. |
| F4 — relaxed tolerance | Absolute difference ≤1e-8 retained, including monitors; relative errors reported separately; OS-build timing disclosed | **RESOLVED.** The largest observed change is about 3 times inside that bound. The current OS build is not retrospective proof of the run-time build, as R2 now states. |
| F5 — reproduction | Explicit roots, fixed world inventory, separate batteries, no overwrite, reconciliation | **PARTIALLY RESOLVED.** Layout and aggregation are corrected; complete expected-identity enforcement remains missing. See R2-F2. |
| F6 — runtime/load caveat | 396.1-second failure restored; CPU observation and wall/concurrency limitations stated | **RESOLVED.** The ratios agree with stored costs. Panel readiness remains unassessed. |
| Low accuracy note | Unsupported equal/approximately-one-ulp accuracy claim withdrawn | **RESOLVED.** Scalar-versus-vector disagreement is distinguished from mathematical accuracy. |

## Findings and concrete fixes

### R2-F1 — Medium: the ledger still silently omits stored-record guards and misclassifies continuous checks

`INEXACT_IMPACT_REPORT_R2.md:109` groups candidate minimum size, positive geometry/spacing, finite checks and selection as “Discrete or integer branches with no margin.” Minimum size and selection are discrete, but **radius of gyration >0 and median nearest-neighbor spacing >0 are continuous threshold decisions**. Their grid-dt inputs are available in stored qualification frames/states; relevant snapshots also exist on refined grids. They are unassessed margins, not quantities without margins. The normalization checks in `GridSet.run`, recovery and phase-probe setup should likewise be named with their actual available/missing contexts (`c6_r4_field_assay.py:25–27,96–109,174–177`). Observed absence of an invalid run remains useful indirect evidence, but it is not an assessment of each margin.

There is also no explicit ledger entry for **stored-record validation** in `c6_r4_field_analysis.py:45–99`: publication fields/finite values, positive publication size, candidate/member identity, `S` matching the selected candidate, matched inputs/perturbations across controls, witness consistency, chain clocks within 1e-7, and continuity of background/carrier/previous-source snapshots. These checks operate on individual stored records. They do **not** inherently require a registered 40-world bootstrap panel. The existing “Primary analysis” row lists contrasts, masks, bootstrap and hypothesis combination and does not identify these guards. In particular, `invalid is null` in `run_world` does not prove that the later `validate_world`/`publication_valid` checks ran and passed: `run_world` does not call them.

Per-grid causal-floor predicates are now assessed, so their **causal grid-agreement guard** is derivable from stored values. Name that composite explicitly, alongside the disclosed structural/recovery/persistence grid-agreement contexts, rather than leaving the reader to infer its status.

Consequently, §7's “every family with a stored value is assessed” and the implication that closing all remaining gaps requires new instrumented runs are too strong. The narrowed headline can remain; the complete-family ledger claim cannot yet remain.

**Concrete fix:** in a new corrective report/analysis revision, split discrete guards, continuous positivity/normalization checks, stored-record validity and final-panel statistics into explicit rows. For each, state the actual operator, units, available context, count if evaluated, and `ASSESSED` or `UNASSESSED` with a reason. Stored guards may be assessed with small stored-data calculations, or honestly labelled unassessed without executing them. Correct the universal §7 claim. Retain the unassessed fine-grid trajectories and future-panel verdicts; do not run worlds to close these documentation gaps. Owner/drafter records disposition in `docs/PLAN_CURRENT.md` after this one-file review.

### R2-F2 — Medium: reproduction records some hashes instead of checking their expected identity

`scripts/analyze_r2.py:325–329` compares SHA-256/byte count with `RAW_FILES_OUTSIDE_GIT.json` **only when an input is inside the study directory**. Three exact inputs are outside it:

- smoke 0: `evidence/c6_option_b/reference_smoke_0/world.json.gz`;
- development 0: `evidence/c6_option_b/audited_v3_development_0/world.json.gz`;
- development 1: `evidence/c6_option_b/quiet_session_20261006_161801/worlds/reference_development_1/world.json.gz`.

For these files, the script computes a hash and puts it into a newly produced inventory; it never compares that hash to an expected identity. A replaced external baseline is therefore accepted rather than producing the promised mismatch stop. **All 20 current exact/inexact inputs do match the hashes and sizes in committed `SUMMARY_R2.json`; this finding is about the reproduction guard, not a current artifact mismatch.**

The script also imports the supplied repository's current `geomind.c4_detect` at lines 313–314 without checking its identity or that of its numerical helpers. Thresholds/window size are hard-coded at lines 35–39 without a protocol identity check. They match the reviewed protocol now, but future dependency drift would silently change the reproduction. This matters because the pair-level and reconstruction claims use those imported calculations.

**Concrete fix:** in a new analyzer revision, consume a fixed expected inventory for all 20 inputs, including the three external references, and compare both bytes and hashes before analysis. Pin/verify the detector and numerical helper dependencies and the protocol identity, or archive a fully identified standalone statistical evaluator. Record the expected identities separately from newly observed identities. Correct the report's “every input hash-checked / fails on mismatched input” claim until that is implemented.

Also provide a separate `--output-root` (or read-only verification mode) and a concrete reproduction command. The current documented command deliberately stops on the committed `results_r2/`; changing `--study-root` also moves the required raw inputs and metadata. Refusing to overwrite is appropriate. A separate destination makes reproduction reviewable while preserving all committed R1/R2 outputs. This usability point alone would be a note; incomplete identity enforcement is the substantive remaining F5 defect. No queue, builds, batteries or worlds belong in this reproduction route.

## Nonblocking notes

### N1 — Low: “every string” includes the explicitly changed digest strings

The opening says every string is identical, whereas the reconciliation correctly reports **45,592 changed digest strings**. Say “every non-digest label/string” and explain the permitted trace/snapshot identity changes at the opening. Distinguish those digests from semantic candidate/member identity hashes, which should stay equal for unchanged memberships.

`walk()` excludes every pair of 64-hex strings from discrete comparison, irrespective of its role. That is sufficient for counting permitted physical digests but is not a generic check of all semantic identity requirements. Use a field-aware exclusion or separately check selected/candidate/member hashes in a future correction. No changed semantic candidate identity was demonstrated here.

### N2 — Low: reconstruction validation is exact-engine-only

`pair_level()` validates the prefix mapping and stored persistence statistics for **E**, then applies the same reconstruction to **I** without independently validating its mapping/statistics (`analyze_r2.py:224–240`). The receipts' 39 valid cells therefore certify exact-engine reconstruction. Label that limitation, or validate both engines and assert matching window/frame/context inventories before pairing; current `zip` operations would otherwise truncate a mismatched inventory.

This does not overturn the current counts: the full value comparison records no structural mismatches, and my smoke-1 spot-check confirms prefix/operation mapping in both engines. It is a useful strengthening of the reconstruction guard, not evidence of a current incorrect pairing.

## Stored evidence independently checked

- **Identity/preservation:** HEAD is the reviewed commit. It adds the 14 R2 files; the original study's existing files are unchanged from `7954445`. All **20** current inputs match the committed R2 input inventory's SHA-256 and byte count, including the 17 study-local compressed files.
- **Aggregation:** adding the ten R2 comparison receipts reproduces **17,413,140 floats**, **8,907,030 changed**, **77,342 scalar instances**, **1,142,364 lock tests** and **3,121,284 link tests**, with zero reported flips and zero unmatched scalar decisions. The 39 recorded exact reconstruction validations all pass. This is receipt reaggregation, not a rerun of all underlying pair computations.
- **Absolute maximum, raw development 2 `/checks/323/max_errors/position`:** 7.3999889039608e-5 → 7.399654856345048e-5; absolute change **3.3404761575145728e-9**. The monitor margin uses `0.05 − value` independently on each side.
- **Relative monitor maximum, raw smoke 0 `/checks/809/max_errors/position`:** 9.907616180352751e-11 → 9.406776773112684e-11; change **5.008394072400671e-12**, relative **0.05055094970607099** under `abs(E−I)/max(abs(E),abs(I))`. This is a different value from the absolute maximum.
- **Non-monitor maximum, raw development 7:** `/turns/0/before_formation/1/qualification/candidates/0/recovery_by_dt/2/recovery_pattern_error` is 0.029817592666880444 → 0.02981759290559083, change **2.3871038479228446e-10**. Its recovery-pattern margin remains positive in both engines.
- **Closest scalar case, raw development 0, second turn, intact persistence window 29:** frequency is 0.010000007263912924 → 0.010000007263912841 at grid 0; signed margin **−7.2639129242851874e-9**, change **8.326672684688674e-17**. At grid 2 the change is **4.163336342344337e-16** and distance/change **17,449,085.0875**. It fails in both engines. This observed ratio is not a future-panel risk bound.
- **Moving causal margins, raw development-0 source m→g:** spread signed-margin change is **8.049116928532385e-15** and ablation signed-margin change **6.106226635438361e-15**, including each engine's moving threshold. The previous zero-ablation-value/infinite-ratio error is corrected. Per-grid floor decisions use strict `>`.
- **Paired-gain example, raw development-0 first turn, intact minus NO-R:** refinement margins **0.0009999999909926357** and **0.0009999999909920112**, change **6.245004513516506e-16**, passing on both sides. The operation's eligibility condition matches the analyzer's inclusion rule.
- **Closest qualification lock, raw smoke 1 `/turns/0/before_formation/3`, pair (0,22):** 0.1001632847400453 → 0.1001632847400464; signed margin **−1.632847400452886e-4**, change **1.1102230246251565e-15**. Both are unlocked.
- **Closest reconstructed persistence lock, raw smoke 1, first-turn NO-R window 94, pair (7,18):** **0.10000148720862774 in both engines**, signed margin **−1.4872086277345486e-6**. Prefix endpoint equals operation frame 0 in each engine. Lock recomputation uses the detector's clipping and square-root policy.
- **Exact baseline:** a fresh recursive type/binary-float equality comparison of local exact smoke 1 with `reference_smoke_1/world.json.gz`, excluding only root cost/build metadata, finds **zero mismatches**, including **1,365,412 float leaves** and **1,396 Boolean leaves**.
- **Built-kernel identity:** all archived study START records consistently identify exact source `9ebe2acf7dd873d3437b5d645091e41bb9ed1a3e69a56a6fc36ebdfdfff96920`, binary `3e269f1464b328e660b5b37ee16a72ed7273c090ee00dd27370129f60ff38f90`, versus inexact source `d27d46bb6053bed84acbed330e0c28fa2c174ae417ad80bd9e4d1f6c5338582d`, binary `e9c3a10fecb81d63558253d4e6eda35cf6b631f4659a05c0e75a4e3d6fd69ec1`. Both surviving scratch sources/binaries match their records. Static `otool -L` and `nm -u` confirm Accelerate linkage and `_vvexp`/`_vvsincos` imports for the inexact binary. The unchanged loader verifies source/flags/binary before selection and build identity after use; this was not merely an inexact source file paired with the exact binary.
- **Stored diagnostics:** both reference/equivariance batteries pass. Reference maxima are **9.46687173097871e-13** exact and **1.278033234797249e-12** inexact; scene equivariance **7.549516567451064e-15**, renaming zero. None was rerun.
- **Speed under shared load:** recomputed six nontrivial pair mean CPU ratio **0.7467061076503366**, range **0.7193794288053382–0.7679028382788675**; seven-pair mean **0.7553286775461542**. Wall ratios **0.6402407685601228–0.8328890465247973**. Receipts record changing loads approximately 27–79 on ten CPUs. These are compute observations under contention, not demonstrated two-worker panel throughput or quiet-machine timings. R2 restores the deep-dive's separate **396.1-second** exact-engine failure at load about 85.
- **OS/build caveat:** current `sw_vers` reports 26.6.2 / **25G83**, consistent with R2's after-the-fact observation; archived platform release strings do not prove that precise OS build at run time.

## Reviewed R2 artifact SHA-256

Paths below are under `evidence/c6_option_b/inexact_study/`.

| Artifact | SHA-256 |
|---|---|
| `INEXACT_IMPACT_REPORT_R2.md` | `fd26e0a1ead668069e7e6ee26bc2b39cc6a293944c00d6698ee69382625659d8` |
| `scripts/analyze_r2.py` | `bfa3a45544f342a1bc215b609a7b9a82876bf60a0b25c1018915079f9768819b` |
| `SUMMARY_R2.json` | `65a325129f739e67ad916625561e48617c74401662e453534abe9bf3ffe92940` |
| `RECONCILIATION_R2.json` | `5afff6d26ed82001f5b3413ded85cc71ed11e55bc08156d55a04152ce5bccdc9` |

## Delivery and command scope

The author should address R2-F1/R2-F2 in a new corrective revision, preserving all current world artifacts and comparison receipts. No observed outcome change is alleged, and no scientific verdict is being recomputed. Owner adoption, decision 0029's contract change, generation of new references and registered runtime readiness remain separate decisions/gates.

Used read-only inspection, hashing/static binary inspection and small Python reads/calculations on stored JSON. No C6 world, native load/build, test suite, battery, mutation probe, bootstrap or panel ran. The raw arithmetic was independently recomputed for selected cases, not exhaustively for all 17 million floats or all pair decisions.

A separate Codex reviewer received the owner's request verbatim and corroborated the two remaining findings and nonblocking wording/coverage notes. This secondary check is same-family; the main review is cross-family against the Claude-authored R2 revision. The owner/author should record this review and disposition in `docs/PLAN_CURRENT.md`; it is already dirty and the user expressly forbids editing any existing file in this task.

Only this new review file was written. `.git` is read-only in this session, so the review is left uncommitted. Existing files and unrelated work were preserved.
