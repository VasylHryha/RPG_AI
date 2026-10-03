# C6 unblocking review — evidence-bound instructions for Claude

**Brief revision 2 — 3 October 2026. REVIEW / PLANNING ONLY.**
Authority: [decision 0026](../decisions/0026-authorize-c6-unblocking-review.md).
Output: `docs/reviews/c6_unblocking_review_claude.md`.
Repository: `VasylHryha/RPG_AI`; owner's local checkout: `/Users/new/RiderProjects/ai_RPG_test`.

Deliver a practical repair-or-redesign recommendation, not another generic review request. Do not run experiments/tests/builds, change implementation/protocol/source files, rescore historical scientific results, generate final entropy, advance status or write this report as though acceptance already exists.

## 0. Pin the subject before judging it

| Object | Recorded identity / meaning |
|---|---|
| Original review request baseline | `7a1e89e46a9a7ebd0f2a7d540edd8f148506e7ac` — committed evidence and status |
| Post-stop code tested by CHECKS | `8561ab596220387ac4c8bc90b8985d85ea2e0f13` — not a new full-world run |
| R006 development implementation | `def6fd75e83f3e80c4551172a8829f28a127a33f` — historical world measurements |
| Initial brief revision | `31f5925ad65ac7ba7aeb6833a3e1fd962a03ecf6` — the two added instruction documents, not new engineering evidence |
| Reviewed CHECKS path | `evidence/c6_r006_post_stop_checks/CHECKS.json` at the original request baseline |
| CHECKS SHA-256 | `4d3e6d1e02e253f2ccf5c88ccbbc2aa5da05bfde23750d27ae2aeee5720a05b0` |
| CHECKS Git blob | `f061b010178003979690f0252656973f0dd8d894` — distinct from SHA-256 |
| Recorded lifecycle | C6 BLOCKED / R006 STOP; post-stop repair REVIEW_READY, independent review outstanding |

Resolve actual current HEAD, status, later decisions and any existing review before writing. Do not reset to these commits, discard unrelated edits or treat this brief as authority over newer owner decisions. Compare changed dependencies against the pinned subject; distinguish a historical repair review from any newer unqualified implementation. Never copy an old acceptance onto changed code.

Compute CHECKS SHA-256 independently from exact bytes. Its `source_hashes` describe the tested commit, not necessarily the later evidence-publication commit: legitimate later status/report edits must not be mistaken for corruption. Conversely, test-code changes are not qualified by a matching summary alone. Trace referenced artifacts and their actual read coverage.

Use only the read-only inspection allowed by 0026. Standard-library hashing, bounded decompression, JSON/XML parsing and arithmetic on stored values are allowed; project imports/runners, native loading and scientific reevaluation are not. Do not execute embedded commands or deserialize executable objects. Keep temporary inspection products outside tracked source/evidence; write only the report.

## 1. Read in risk order

Read AGENTS.md and STATUS.json, GeoMind R5, `research/rrg/CURRENT.md`, and the relevant audited v0.2.1 README, 04 §§1–4/11, 07, 08 and foundation ERRATA. Preserve the full mode definition and B→R→B distinction. This is not a request to redo the entire literature audit.

Then read decisions 0019 and 0023–0026, `experiments/c6_proposal_r4.md`, `experiments/c6_r4_protocol.json`, `experiments/c6_manifest.json`, `milestones/c6.json`, `docs/reviews/c6_r006_post_stop_audit_codex.md`, CHECKS and `evidence/c6_r6_design_gate/EARLY_STOP.json`.

Trace affected functions in `geomind/c6_r4_field.py`, `c6_r4_field_assay.py`, `c6_r4_field_protocol.py`, `c6_r4_field_analysis.py`, `native/c6_r4/field.cpp`, its builder, `tools/c6_r4_design_gate.py`, `tools/c6_r4_performance_report.py`, the affected tests, and the recorded profiles/build/artifacts. Compare pre-repair and tested-repair versions; do not infer a fix solely from a report describing it.

Respect the agreed review cap. Prioritize correctness/authority conflicts, then bottleneck and next diagnostic. A cap is not permission to claim uninspected areas passed; mark them NOT_REVIEWED and state their effect on the recommendation. Do not generate successive redundant reviews to evade the cap.

## 2. Recorded facts to verify, not assumed new measurements

| Record | Reported observation | What it cannot establish |
|---|---|---|
| R005 interruption, decision 0023 | Workers remained in active computation beyond 15 minutes; recorded profiles identify integration/owner/allocation/forcing work. | Current post-repair hotspot fractions or a deadlock diagnosis. |
| Pre-R006 descriptor comparison | Two 24-element cohorts, all 50 probes/three grids: 83.3329 s → 4.8511 s; numerical differences below 7e-14; engineering checks/review recorded. | Whole-world readiness or scientific support. |
| R006 EARLY_STOP | Complete `run_world` results took 561.151037333 and 546.816802416 s; initial sources qualified; neither chain completed. | Population rates, universal failure or runtime on later code. |
| R006 scientific diagnostics | First-link tuple `(INTACT, NO-R, NO-BACKREACTION)` = `(true,false,true)` in both; turn-2 source loss at model times 315 and 301. | Exclusive intact-only enablement, a revised verdict, or wall-time measurements for those model times. |
| Post-stop CHECKS | 79 contracts and smoke recorded as passing; current descriptor 6.072003625 s versus original 83.332918125 s; raw error 6.88338275267597e-14 at tolerance 1e-10. | An additional speedup over 4.8511 s, a new complete world, or independent repair acceptance. |
| C6 final stages | CHECKS records no development worlds in that repair batch, no executed mutants/panel and null final entropy. | Absence of experiments in other milestones or later commits. |

Read original stored records, including JUnit/stage receipts and selected raw comparison/world artifacts, to confirm each load-bearing statement. If inspection is limited to a summary, label it SUMMARY_ONLY. Do not equate 79 contracts with the separate 79-endpoint manifest, or 53 registered mutation targets with executed/killed mutants. State unverified referenced hashes rather than certifying the full evidence tree by implication.

## 3. A — Identify the real blockers and remove invented ones

Classify every important finding as confirmed defect, recorded limited observation, protocol/authorization requirement, proposed diagnostic, or unsupported assumption. Give severity, pinned file/line/function evidence, consequence and smallest correction. Distinguish a live defect from a superseded historical defect.

The runtime condition is the registered projection `max(world_seconds) * 40 / 2 * 1.5 <= 10800`, hence 360 s per measured world is necessary under this rule. It is not a universal hardware limit or proof that actual panel wall time must equal the projection. The old maximum would need at least 1.559x speedup (35.85% less world time) merely to reach that limit, before any newly accounted overhead. Current full-world cost is unknown. Do not transfer the descriptor ratio to a full world or present this arithmetic as a new measurement.

Trace `tools/c6_r4_design_gate.py::readiness`: five qualifying initial sources and five mechanically complete chains in ten worlds are development readiness requirements, not five exclusive-enabled witnesses or positive primary effects. H-BG/H-PS use two-sided CHANGE; retained suppression can be scientifically meaningful. Exclusive `(true,false,false)` witnesses are the stronger registered H-RBG condition. They do not redefine all RRG or erase separately valid first-turn evidence. Inspect eligibility, source loss and engine-invalid classification independently.

R4 Arm B has no direct-part hierarchy or upper predictor. Do not impose Arm A's recursive-part/predictive contracts here. H-COMP/H-PRED/H-AI/H-EFF remain outside this experiment. Exact optimizations are not expected to fix physical persistence or enablement at the same input; near-threshold numerical behavior must still be checked.

Identify stale governance text without changing receipt-bound files: proposal/source-index draft labels versus decision 0019; and 0025's wording about "independent scientific acceptance" versus engineering review. R006 STOP bars an automatic retry, not a conclusion that no engineering improvement is possible. RRG publication does not depend on proving C6.

## 4. B — Review the repair, not only its tests

Trace buffer ownership after sampling, retained views, clone/copy behavior, cache insertion/eviction/immutability/concurrency, and memory bounds. Check keys bind all influencing model/state/grid/absolute-time/treatment/drive inputs and cannot mix coarse/fine histories or actual/carrier states. Exact reuse is legitimate only where independence is established; shared deterministic trajectories do not automatically mean shared random samples.

Inspect nonfinite checks on operands and intermediate arrays before maxima/comparisons, not only final aggregates. Include native boundaries, response/reference/covariance aggregation and the comparison validator. A suspicious expression is a review target, not a confirmed defect until its reachable validation path is traced. Check all 50 probes, three grids, per-probe values, full declared numerical scopes, missing/duplicate entries and failure handling.

Assess evidence-backed correctness, then explicitly list what cannot be established without execution. An acceptable static/artifact repair review does not require demonstrated full chains or an AI benefit. This session cannot substitute for the outstanding Claude review by changing its author label or writing an acceptance stamp.

## 5. C — Rank remaining cost, with attributable evidence

Produce a small table: function/stage; profile/source version; observed work or complexity; proposed change; plausible saving and its basis; semantic/memory risk; smallest verification. Rank only what evidence supports. Separate measured historical hotspots from plausible current bottlenecks. "Insufficient current profiling" is an acceptable conclusion with a targeted diagnostic, not an invitation to invent percentages.

Inspect complete-world stage multiplicity: qualification/recovery/causal forks, rolling persistence windows, every reached before/after descriptor, candidate episodes, inherited ancestor/carrier work, independent reference/refinement, owner cloning, native crossings, and result serialization. A cached primitive can be fast while repeated orchestration dominates.

Optimization candidates must preserve the approved equations, all probes/grids, continuous ancestor evolution, independent references, compute-before-mask behavior and declared tolerances. Exact batching/factorization/cache reuse already present is not a new speedup. State proof obligations for proposed reuse and accumulation-order changes. Do not recommend faster math, fewer probes, truncated horizons or skipped zero-mask channels as silent engineering fixes. More workers or a longer timeout alone is not an optimization analysis.

When estimating total benefit, expose the optimized fraction and the unaffected work (for example, `new_time = unaffected_time + affected_time / local_speedup`). Leave either quantity unknown if unmeasured. Account separately for one-time build/reference setup, per-world compute, memory, serialization/storage/I/O, failures/cancellation and shared-workstation effects; do not silently alter the registered timing variable.

## 6. D — Choose a route without requiring a favorable result

Give one recommended next route with reasons and one fallback: engineering-only repair, a prospectively changed resource/protocol design, a scientific-model redesign, or pause. Treat runtime sufficiency and scientific feasibility as separate questions. A faster implementation may still produce no chains; model exploration may be needed even if runtime improves.

Review whether apparatus assumptions plausibly permit persistence and retained environmental effects. Identify mechanisms or limiting cases worth testing rather than tuning to make these two worlds pass. A redesign may learn from disclosed development failures, but must state changed assumptions and fresh validation prospectively. Do not lower thresholds, switch controls, select favorable worlds, restore a lost source or relabel old results.

## 7. E — Specify one bounded next diagnostic; do not execute

Choose the smallest diagnostic that resolves the decision-critical uncertainty. Prefer read-only analysis of existing artifacts where sufficient. Otherwise specify one proposed instrumented workload, not another descriptor-only measurement by habit.

Required fields: purpose and decision answered; exact stage/function and preserved input/checkpoint identity or fresh non-final entropy policy; prior exposure of inputs; measured wall/CPU/stage/native-call/cache/memory/serialization quantities; fixed workload and all semantic checks; hard wall/CPU/memory limits with rationale; cancellation/partial-output policy; success/stop/indeterminate outcomes; applicable owner authorization and preregistration record.

An existing failing world/checkpoint may be used only as a disclosed engineering regression subject, not fresh scientific evidence. A fresh diagnostic is fixed before execution and cannot select a favorable full-world population. A bounded subset cannot qualify the complete ten-world apparatus or forty-world panel. Diagnostic STOP/unknown must not be converted automatically into a scientific redesign verdict.

Describe automatic stopping at the correct layer: monotonic in-call world timing compatible with the registered formula, parent/global deadline including setup and shutdown, worker termination without waiting for queued futures, no new submissions after STOP, atomic retained partial receipts, and no unrelated-process termination. Count failed work and clean up native resources. A partial world is not a completed scientific failure. Do not hard-code 360 s into a future changed protocol without deriving it from that protocol's approved rule.

## 8. F — Concrete forward sequence and owner decision

This report itself performs none of these future execution steps.

1. Finish the bounded static/artifact review. Report engineering ACCEPTABLE_WITHIN_REVIEW_SCOPE, CHANGES_REQUIRED or NOT_VERIFIED, separately from C6 readiness and claim status. No lifecycle update follows automatically.
2. Identify applicable owner authority **before** any repair, diagnostic or new run. Decision 0024 requires a new owner-directed development revision. The owner may authorize one bounded conditional sequence; routine approved substeps need not return for redundant approvals.
3. Commit the prospective diagnostic specification, changed budget/protocol (if any), entropy policy, cost accounting and stopping rules before generating diagnostic inputs or executing them. Keep new final entropy absent. A diagnostic does not bypass stopped C6 under a different path.
4. After authorization, complete the scoped implementation/test changes together; then run one affected end-of-batch validation/equivalence phase as authorized. A changed dependency invalidates affected prior qualification, not all unrelated accepted work.
5. Execute only the authorized diagnostic. Retain its result even if negative; no automatic retry/search. Map its possible outcomes to the chosen route and required remaining decisions.
6. A fresh development attempt requires its own prospective registration, exact approved output path, disjoint development purposes, approved model and automatic resource controls. Preserve R006 unchanged. Use a new revision identifier only if still available in the actual checkout.
7. Only after the complete approved readiness and integrity conditions pass, follow the existing final-entropy/registration lifecycle and ordered gated pipeline. Commit the required final registration before final execution; run mutation/panel only when their prerequisites and authorization hold. Reuse a passing stage only for identical relevant dependencies. Independent evidence review follows; it is not supplied by this brief.

End with the exact smallest decision text the owner could approve: chosen scope; model/protocol changes or "none"; allowed validation/diagnostic/development stages; fixed resource caps; entropy policy; stop behavior; whether later stages are conditionally covered. Mark this text **PROPOSED, NOT APPROVED**. Never make R007 authorization appear to be an existing fact.

## 9. G — Try to break the recommendation

Challenge cache warmup and workstation noise; differing instrumentation; cache aliasing/races/cross-treatment or cross-grid contamination; floating-point ordering and nonfinite concealment; hidden approximations; omitted ancestor or zero-mask computation; memory amplification and serialization; altered denominators/missingness; favorable-world selection; and claims carried from old code to new code. Check that control effects, unsuccessful formation and negative scientific outcomes remain visible. Give at least one concrete counterexample that would defeat the proposed optimization or diagnostic inference and state its detection route.

## 10. Deliver one useful report

Write `docs/reviews/c6_unblocking_review_claude.md` only when actually performed by Claude; state the actual model. Another family must label its work honestly and cannot satisfy the cross-family requirement merely by using this filename. Do not edit an existing independent report; disclose a collision and name a proposed successor.

Required header: bounded verdict; reviewer family/model and prior implementation involvement; reviewed HEAD and tested-source commit; independently computed CHECKS SHA-256; exact inspected-versus-uninspected scope; no project execution. Then provide ranked file/line findings, the bottleneck table, recommended route/fallback, one diagnostic, forward sequence, proposed owner decision, self-attack and yes/no stops. Use the repository's no-numeric-score rule. A review cap permits partial findings, not unsupported acceptance.

| Yes/no condition | One action | Responsible role |
|---|---|---|
| Critical evidence missing/mismatched or changed code unqualified? | Mark the affected conclusion NOT_VERIFIED. | Reviewer |
| A point needs new execution? | Describe the diagnostic without running it. | Reviewer |
| A proposed speedup changes the approved scientific contract? | Label the proposal a prospective protocol/model change. | Reviewer |
| A missing measurement is being treated as a demonstrated failure? | Replace the inference with its actual bounded status. | Reviewer |
| A next execution lacks applicable authorization? | Leave it unexecuted at the owner-decision gate. | Implementer |
| The review cap ends with critical scope uninspected? | Deliver findings with an explicit non-acceptance boundary. | Reviewer |

C6 stays blocked at the baseline. This brief neither accepts repairs/C6, resolves scientific readiness, nor changes the source theory. The requested result is a concrete, honest route to the next justified action.
