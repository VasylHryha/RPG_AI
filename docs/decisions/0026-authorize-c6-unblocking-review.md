# 0026 — C6 unblocking review: scope and authorization

**Revision 2 — 3 October 2026.** Corrects this decision's first wording after the owner's recheck request. The earlier text remains in Git history; decisions 0019 and 0023–0025, registered protocols and historical evidence are not amended here.

## 1. What is authorized now

The owner's supplied request authorizes **review and planning only**. The assigned independent reviewer is Claude. The task is to inspect the post-stop engineering repairs and recommend a concrete way forward, using [the review brief](../reviews/c6_unblocking_review_request.md), then write `docs/reviews/c6_unblocking_review_claude.md`.

This task does not authorize implementation changes, tests, builds, experiments, pilots, benchmarks, mutation probes, new development attempts, final entropy, panels, source-release changes, or milestone-status changes. C6 remains BLOCKED / R006 STOP at the recorded baseline.

Allowed inspection includes read-only Git/file operations, diffs, SHA-256 calculation, bounded decompression and parsing of existing JSON/XML/text records, and arithmetic on recorded values using standard utilities or a standalone standard-library script. Do not import project modules, load native binaries, invoke runners/evaluators, recompute scientific verdicts, execute downloaded code or create/modify gate stamps. Reading evidence is not rerunning it.

Only the review report is a repository deliverable of the Claude task. Preserve existing reports; do not overwrite another reviewer's work. Report a path/ownership conflict and continue independent inspection without replacing it.

## 2. Existing authority is not replaced

Use the authority ordering already specified by AGENTS.md and GeoMind R5, including explicit current owner decisions, foundation definitions as qualified by the audited release, and the actual pinned RRG source. RRG v0.2.1 is the source pin at the recorded baseline, not a permanent ban on an explicitly authorized later edition. Do not use an older locked-core hash as sole forward authority or infer source access from a hash alone.

Decision 0019 already approved the identified C6 R4 model. Old `DRAFT` text in the proposal or source index does not undo that approval. Decisions 0023–0025 describe subsequent attempts, STOP and repairs. Decision 0024 requires a **new prospective owner-directed revision before another development attempt**; changing an output directory cannot supply authorization.

This review request neither revokes unrelated existing authorizations nor grants new execution authority. Where later engineering work is already authorized, name the decision and its exact remaining scope rather than inventing an additional approval requirement. Review-only scope still governs this task. A new or changed scope needs an owner decision before execution.

## 3. Separate the conclusions

The reviewer must separate: repair correctness, complete-world/runtime readiness, scientific evidence within the registered claim scope, and authorization to proceed. An engineering review may be favorable while C6 remains blocked. No scientific acceptance is needed merely to assess an engineering repair; no engineering assessment accepts C6.

R5 distinguishes H-COMP, H-BG, H-PS, H-RBG, H-PRED, H-AI and H-EFF. The current R4 experiment is Arm B; do not reactivate stopped Arm A or impose its direct-part/prediction requirements on this model. Preserve the difference between a mechanically complete chain and the protocol's stronger enabled witness. These are operational conditions of this experiment, not definitions of all possible RRG realizations.

The numerical/history summary lives in the brief with its pinned evidence references. It is input to verify, not a second status tracker. This document assigns no hypothesis verdict or acceptance.

## 4. Forward order after the review

The report recommends one route and identifies the authority needed for it. An owner decision may cover a coherent, bounded sequence conditionally; this decision does not require a separate approval for every routine substep.

The order is **review → applicable owner authorization → prospective diagnostic/development registration as required → authorized changes → one affected end-of-batch validation → authorized bounded diagnostic/readiness → later gated stages only if prerequisites pass**. A diagnostic is specified and authorized before its inputs are generated or it runs. Final entropy remains absent until the approved readiness/registration lifecycle permits it. A favorable review does not authorize R007.

Any proposed change to the model, probes, grids, thresholds, controls, evidence rules or budget must be explicit and prospective. Preserved R005/R006 evidence is never overwritten or retrospectively rescored to clear a gate.

## 5. Stops for this review

| Yes/no condition | One action | Responsible role |
|---|---|---|
| A required fact or identity cannot be established from accessible evidence? | Mark the affected conclusion NOT_VERIFIED and continue independent items. | Reviewer |
| Establishing a point would require project execution? | Specify the missing diagnostic without executing it. | Reviewer |
| New work lacks applicable execution authority? | Leave that work at the owner-decision gate. | Implementer |
| Current branch/report differs from the assumed baseline? | Reconcile the changed scope without resetting or overwriting others' work. | Reviewer |
| Review coverage cannot be completed within the agreed review cap? | Deliver the completed findings and explicit unreviewed scope without acceptance. | Reviewer |
| A scientific claim is inferred from two development worlds or an engineering fixture? | Restrict the claim to the evidence actually inspected. | Reviewer |

Revision-2 rationale: [brief recheck](../reviews/c6_unblocking_brief_recheck_chatgpt.md). This is a correction to forward instructions, not a Claude engineering review or a new C6 attempt.
