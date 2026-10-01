Verdict: **ACCEPTED**.

Reviewer family: Codex

Reviewed experiment: `geomind-c4-r4-003` (C4 R003).
Reviewed evidence commit: `a774d441f0409b7010a7321e52976539f48ca435`.
Registered manifest commit: `e79622688304fbc34bb9980300e5e81a4aa24204`.
Verified source commit, including the contract correction: `fc5c2b6b886958fa37956c4de54b4a235dc60567`.
Reviewed `evidence/c4_r003/results.json` SHA256, verified against the handoff: `5a95025fc65487e00cf1012044535745fe212077d9b2f0ed2683b5ad6b42b1ab`.

Date: 2026-10-01. One independent review of committed code and evidence, within the approximately 20-minute cap. Started at `evidence/c4_r003/HANDOFF.md` and `docs/decisions/0003-c4-r003-review-fixes.md`. Implementer family: Claude; reviewer family: Codex. No recorded panel, pipeline smoke, mutation probe, or final-world simulation was rerun. Review probes evaluate stored records or synthetic evaluator inputs; the everyday test suite uses its existing development/synthetic fixtures. No accepted C4 implementation, manifest, committed receipt, or gate stamp was changed. The subsequent owner-requested process audit adds separate freeze enforcement, described below.

At the owner's subsequent request, I audited this same review and its acceptance metadata. This amendment retains the verdict and strengthens the existing audit helper; it does not constitute a second independent review.

The bounded C4 implementation is accepted. Both blocking R002 findings are fixed, and I found no remaining blocker against the registered R003 protocol. The identical-omega arm supports H-M and the H-C **precursor** within the stated scope. The heterogeneous arm remains H-M INCONCLUSIVE and H-C precursor NOT_SUPPORTED. Acceptance does not establish recursive H-C, generic heterogeneous closure, novelty, task usefulness, or efficiency.

**R002 findings, checked through code, isolated controls, and the receipt.**

**R1 — Recovery accepting common fragmentation: fixed.** `geomind/c4_detect.py` now computes original-to-control, original-to-kicked, and control-to-kicked membership scores. Their minimum is the `recovery_jaccard` consumed by criterion 5; the paired phase-pattern comparison remains intact. All three scores are retained per candidate and in each accepted unit's stability summary. This prevents a smaller surviving control component from redefining successful recovery.

The original six-member common-fragmentation reproduction now fails only criterion 5: scores are (0.5, 0.5, 1.0), minimum 0.5. A whole-group positive control passes. Independent cases also reject fragmentation in only the control, fragmentation in only the kicked future, and disagreement between two otherwise qualifying futures. In the last case, a twenty-member group has original-to-control and original-to-kicked scores of 0.9, but control-to-kicked is 0.8, so recovery correctly fails. No dynamics are integrated in these probes; future states are supplied through the mocked integration seam.

For every recorded intact candidate, I checked that the reported minimum equals the minimum of the three stored scores, and that no accepted candidate is below the registered 0.9 threshold. The identical arm has 39 candidates and no failed original-membership matches. The heterogeneous arm has 44 candidates, seven with an original-to-future score below 0.9; all seven are rejected by criterion 5. These scores establish membership change, without distinguishing fragmentation from merger in the absence of retained future component identities. The successful mutation record detects `recovery_ignores_original`.

**R2 — Conflicting formation-failure rules: fixed.** The R003 manifest registers an ordered truth table. A causal or dose FAIL takes precedence and gives H-M NOT_SUPPORTED; formation PASS plus all three causal/dose PASS results gives SUPPORTED_WITHIN_SCOPE; the remaining cases are INCONCLUSIVE. Effective-state FAIL gives H-C precursor NOT_SUPPORTED; otherwise support requires supported H-M and effective-state PASS. The code follows those rows. I checked all 162 combinations of formation PASS/FAIL and the three-valued causal, dose, and effective-state verdicts, including mixed FAIL/INCONCLUSIVE cases.

Formation failure alone is now explicitly INCONCLUSIVE for H-M, while remaining FAIL for the formation endpoint. Decision 0003 reconciles this with the approved proposal and corrects decision 0002. Choosing the approved proposal's semantics before R003's panel is a defensible resolution of the design conflict; it does not convert the heterogeneous formation failure into a success. R001 and R002 retain their original receipts and outcomes. The insufficient-world rule still makes the five-world heterogeneous causal/dose endpoints inconclusive despite their positive descriptive estimates. The successful mutation record detects `hm_ignores_formation`, `formation_fail_not_supported`, and `hm_ignores_dose`.

**Vacuous clump-control observation: fixed.** An empty candidate population now reports NOT_TESTED, rather than PASS. A detected clump causes FAIL; the implementation gate requires a non-vacuous PASS in the primary arm and no arm FAIL. Synthetic endpoint and gate cases verify all these branches. In the actual R003 receipt, both controls are non-vacuous: twenty primary candidates and five heterogeneous candidates, none accepted. All twenty primary clump candidates fail recovery. The stricter gate is registered in R003.

**Provenance, pipeline, and evaluator checks.**

- The initial working tree was clean, and `tools/milestones.py check c4 review` passed before review artifacts were created. The R003 manifest was committed before the panel and is byte-identical in the registration commit, verified source commit, and receipt. Its final entropy is distinct from development, R001, and R002 entropy. Model values, integration, doses, numerical tolerances, effective-state bounds, and numeric detector thresholds are unchanged from R002.
- All thirteen dependency hashes match both current files and the committed verified source. The dependency fingerprint and all successful pipeline artifact hashes match. Accepted C1 R006 and C2 R002 receipt-bound files are unchanged. Every file in the R001 and R002 evidence folders still matches its original evidence commit; the R002 review is also unchanged in the R003 commit range.
- The first R003 attempt stopped at mutation when `hm_ignores_dose` survived. Its local stamps contain only preflight, tests, and smoke, and its mutation report records that survivor. The next commit adds the missing dose-inconclusive contract without changing the manifest. This changes the dependency fingerprint, so verifying the preceding stages again is legitimate. The successful committed attestation records preflight → tests → smoke → mutation → panel, totaling 212.40 seconds. It contains 26 passing contracts and 32/32 detected mutants, with no unexpected survivors or timeouts. The failed attempt is transparently reported; evidence supports one successful recorded panel.
- All sixteen registered endpoints are evaluated, with values and verdicts and no silent omission. Receipt-only evaluation reproduces both arm summaries and endpoint coverage exactly. Independently, world means recomputed from per-resonator values, formation counts/Wilson intervals, stored candidate decisions, and effective-state counts agree. Independent bootstrap arithmetic reproduces all 28 effect, dose, and paired-difference summaries to absolute tolerance `1e-14`, using the recorded resampling seed and ordering. Resampling stored effects does not simulate final worlds or change their verdicts.
- Thirty independent scalar evaluations of the registered RHS agree with the vectorized implementation, including the frozen-topology ablations: maximum absolute error `8.88e-16`. `intervene` retains per-condition paired controls, identical G→M probe kicks, topology frozen from the unperturbed formed state, the registered doses, and aggregation by independent world. The runner checks the panel gate itself. Finite-state checks remain in the integration loop.

The receipt does not archive the complete formation/recovery trajectories and component identities. Thus raw future membership scores cannot be independently reconstructed from this receipt alone. Acceptance rests on the hash-bound caller/code, the recorded scores and contracts, independent arithmetic, and the additional synthetic negative controls. I do not claim a separate trajectory replication.

**Registered results and limits.**

| Primary-arm endpoint | Recomputed result | Registered verdict |
|---|---|---|
| Formation | 20/20; Wilson 95% CI [0.838875, 1.000000] | PASS |
| G→M | Mean 0.01324890 rad; CI [0.01204148, 0.01451079]; complete ablation 0 | PASS |
| M→G | Mean 1.15286423 in relative-radius units; CI [0.93900561, 1.38309734]; J=0 ablation 0 | PASS |
| G→M dose response | Means 0.005981 → 0.013249 → 0.032211; high-minus-low CI [0.023427, 0.029227] | PASS |
| M→G dose response | Means 0.055925 → 0.301419 → 1.152864; high-minus-low CI [0.887883, 1.329114] | PASS |
| Effective state | 39/39 units within all bounds; worst position error 0.089851 L | PASS |

The heterogeneous arm forms in 5/20 worlds, with Wilson CI [0.111862, 0.468701], and has four of five units within bounds. These correctly yield formation FAIL, causal/dose INCONCLUSIVE for fewer than ten formed worlds, effective-state FAIL, H-M INCONCLUSIVE, and H-C precursor NOT_SUPPORTED.

Recorded numerical checks pass: held-neighbor RK4 ratios 17.12–17.13, switching-model dt error at most `5.33e-4`, and equivariance error at most `7.11e-15`. These establish the registered limited numerical controls, rather than accuracy of every transient.

Complete-ablation effects vanish by construction; intact paired effects and the registered dose response carry the empirical causal result. The primary arm is a synchronizing fixture with intrinsic frequency zero, and G→M measures restoring response to a shared phase probe. Formation/effective-state results come from one N, one parameter set, and one neighbor rule. Effective-state prediction covers centroid, size, and frequency in this setting; it does not validate upper-level coupling, boundary-excitation response, or recursive composition. Earlier revisions informed R003, and the accepted scope remains a mechanism probe of the specified dynamics.

**Validation and disposition.**

`REVIEW_CHECKS.py` beside this report preserves the hash, arithmetic, scalar RHS, recovery, verdict-table, and clump-control checks. Run `.venv/bin/python -B evidence/c4_r003_review_codex/REVIEW_CHECKS.py`; it passed without executing a panel or trajectory. The everyday suite `.venv/bin/python -m pytest -q -x` passed all 135 tests in 48.33 seconds.

C4 R003 is recorded as ACCEPTED in `STATUS.json`, and README is regenerated through `python3 tools/status.py --write`. The thirteen files named in the accepted receipt's `file_hashes` are frozen at those exact hashes; the C4 entry's `frozen_hashes`, accepted receipt path, and receipt digest record that identity. The receipt's historical REVIEW_READY value remains unchanged. C5–C8 remain NOT_STARTED and require their own approved proposals and registration; no dependent milestone was started by this review. The review and status changes are local and uncommitted.

The owner-requested audit also checks the acceptance declaration, review family/digest, complete receipt and passing gates, contract digest, exact dependency inventory, finite recorded values, independently computed worst-unit errors, unchanged hypothesis labels, and README consistency. Five synthetic inconsistencies in acceptance status, receipt metadata, freeze inventory, or the review verdict must be rejected without writing any of those fixtures into the repository.

The further owner-requested recheck found a process gap: existing hooks did not enforce the declared freeze inventory. This is now addressed by the new `tools/accepted_freeze.py`, wired into the active `.githooks/pre-commit` before the existing guards. It reads the accepted receipt from HEAD, verifies the exact inventory and digest, and checks both staged and working files. Once committed, freeze metadata cannot be removed or replaced to permit an altered receipt or source. New acceptance metadata must reference a complete, passing receipt for the correct milestone and a matching acceptance review; the review must also remain consistent while status declares ACCEPTED. Legacy entries without this metadata retain their existing checks. This is commit enforcement, not a filesystem write lock, and retains the documented limits of local hooks.

The guard and thirteen focused tests are new files; the hook is not bound by any accepted receipt. Tests use disposable repositories and cover staged edits followed by working-file restoration, deletions, coordinated receipt/metadata changes, wrong-milestone or failing receipts, invalid reviews, valid acceptance, and unrelated additions. A real commit through the copied pre-commit hook rejects a staged frozen-source change. Existing accepted tools, all thirteen C4 dependency hashes, and C1/C2 receipt-bound files remain unchanged. This process addition does not modify the accepted model or require a new panel.

Self-audit validation: the strengthened review checks passed; the earlier 135-test suite passed in 38.49 seconds after the helper change. Following the separate freeze-enforcement addition, all 148 everyday tests passed in 38.57 seconds. The active repository pre-commit hook passed against the current files. Review format/family/digest validation, generated status consistency, and whitespace checks passed. The committed R003 evidence, prior R002 review, accepted dependency hashes, HEAD, and index remain unchanged. The process changes, review, and acceptance metadata remain local and uncommitted. No new acceptance blocker was found.
