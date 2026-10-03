# 0025 — Repair C6 engineering defects without reopening the R006 attempt

Date: 2026-10-03. Owner request: recheck the completed work for defects, conflicts and gaps; rework where useful. This authorizes the engineering repair batch and end-of-batch checks. It does not register a new development attempt or revise a recorded scientific verdict.

The audit found retained integration buffers behind sampled-row views, nonfinite/overflow cases that numerical maxima could conceal, unsynchronized Python trajectory-cache operations, and incomplete validation of the performance comparison. The repairs add sample copies, explicit numerical rejection, immutable atomic cache operations, and complete fixture coverage/gain checks. Repeated outgoing calculations now reuse identical full unmasked physical channels with a 16 MiB cache and bounded temporary arrays. The proposal's compute-before-mask requirement remains intact; zero masks do not skip channel computation. The native equations, registered thresholds and experiment settings are unchanged.

Worker CPU time is now recorded; the existing peak-RSS field explicitly excludes result serialization. Neither field supplies the missing complete storage/I/O, reference/build and failed-work cost accounting. These remain prerequisites for future scientific qualification.

Existing R005/R006 receipts, world files and stop records remain unchanged. The changed implementation is not qualified by those historical receipts. Final entropy stays absent, R006 stays STOP, and C6 stays BLOCKED. Engineering validation uses the already reserved descriptor fixture and the gated pipeline through smoke only. All implementation and regression-test edits precede that run. Four additional semantic mutants are registered, but no mutation probe is run without readiness.

| Yes/no stop condition | Action | Responsible role |
|---|---|---|
| Engineering contracts or fixture equivalence fail? | Fix the concrete failure before declaring the repair review-ready. | Implementer |
| New prospective owner-directed revision absent? | Preserve the R006 STOP and do not restart development. | Implementer |
| Full development readiness absent? | Keep final entropy absent and do not run mutation/panel stages. | Implementer |
| Current independent scientific acceptance absent? | Leave the engineering repair at REVIEW_READY rather than ACCEPTED. | Reviewer |

The audit and remaining work are recorded in `docs/reviews/c6_r006_post_stop_audit_codex.md`; validation is recorded separately from scientific evidence.
