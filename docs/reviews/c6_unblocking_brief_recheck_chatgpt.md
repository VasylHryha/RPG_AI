# C6 review-brief recheck — corrections to our instructions

**3 October 2026. Author: ChatGPT / GPT-6 Astra Pro (OpenAI family).**
**Scope: documentation and authorization consistency, not independent Claude repair acceptance.**

The owner requested a recheck and permitted rework. The inspected branch was `31f5925ad65ac7ba7aeb6833a3e1fd962a03ecf6`; the engineering/evidence baseline remains `7a1e89e46a9a7ebd0f2a7d540edd8f148506e7ac`. This report corrects the two instruction files added by the preceding session. It does not run or accept C6.

## Findings and repairs

| Priority | Finding in the first brief / decision | Evidence at the inspected branch | Revision-2 repair |
|---|---|---|---|
| High | Sequence F listed engineering changes and a diagnostic before the owner decision, while 0026 required approval before both. | `c6_unblocking_review_request.md`, §F and owner option A; `0026-authorize-c6-unblocking-review.md`, final authorization section. | Approval precedes execution; diagnostic specification/registration precedes new inputs and runs. |
| High | Fresh development/final namespaces were grouped into one future registration step, risking premature final entropy. | Brief §F item 6; `experiments/c6_manifest.json` has null final entropy; decision 0019 defers it until readiness. | Development and final lifecycles separated; no final entropy before the approved readiness/registration boundary. |
| High | Fixed historical HEAD was not accompanied by a current-checkout/report reconciliation rule. | Brief header; CHECKS binds tested commit `8561ab5`, while evidence was published at `7a1e89e`. | Distinguish live HEAD, tested source, historical development and instruction revisions; do not reset or inherit acceptance across dependency changes. |
| High | The latest workflow could be confused with awaiting first approval, and scientific acceptance with engineering review. | Proposal header and `research/rrg/CURRENT.md` still say draft; decision 0019 approved R4. Decision 0025's final stop row uses scientific-acceptance wording. | Name approval/STOP separately; ask for bounded engineering judgment without advancing C6. Flag stale wording without changing receipt-bound source. |
| Medium | Demanding identification of the current bottleneck could invite unsupported certainty from old profiles. | Brief §§C–D; CHECKS explicitly records no post-stop development worlds. | Version every profile, separate measured/candidate hotspots, allow unknown attribution and require a decision-focused diagnostic. |
| Medium | Broad theory/chain wording did not explain the model's actual readiness versus witness conditions. | R4 proposal §§6/9; `tools/c6_r4_design_gate.py::readiness` uses mechanical chains and merely reports enabled witnesses. | Separate mechanical readiness, two-sided H-BG/H-PS and stricter H-RBG witnesses; do not impose Arm A requirements on Arm B. |
| Medium | "No project code" did not clearly distinguish permitted evidence inspection from forbidden reevaluation; review coverage had no cap outcome. | Decision 0026 inspection paragraph; AGENTS independent-review cap. | Explicitly allow inert hashing/parsing/decompression; forbid project imports/runners/native loading; require NOT_REVIEWED/NOT_VERIFIED on uncovered scope. |
| Medium | Repeated approval wording could be read as creating a new global engineering policy. | Decision 0026 final section and brief option list. | This task remains review-only; existing unrelated authority is neither revoked nor expanded; one owner decision can authorize a bounded conditional sequence. |
| Medium | Runtime arithmetic lacked a complete-workload boundary and automatic shutdown specification. | Design-gate `readiness` and `main`; old worlds lacked completed chains and timing excludes later serialization. | Preserve the registered rule; distinguish necessary budget fit from full-workload readiness; require parent/worker cancellation and explicit cost scopes in any future proposal. |
| Low | Earlier commit trailers asserted `ChatGPT:GPT-5.6-Sol` without a reliable identity basis in this review. | The two instruction commits' metadata. | Preserve history; identify this author truthfully and do not impersonate the requested Claude reviewer. |

## Evidence and actual checks

Read the two original instruction files, AGENTS, the relevant R5/source-index sections, decision 0019, the R4 model/protocol/manifest sections, design-gate code, provenance parser and the baseline CHECKS. Earlier decision/STOP summaries were available in this conversation; this is not a fresh hash audit of their referenced profiles or world arrays. The independent reviewer still needs those artifacts.

The CHECKS UTF-8 content was copied from the live connector read and its local Git blob hash was recomputed as `f061b010178003979690f0252656973f0dd8d894`, matching GitHub. Independently computed SHA-256: `4d3e6d1e02e253f2ccf5c88ccbbc2aa5da05bfde23750d27ae2aeee5720a05b0` (4,120 bytes). This verifies the inspected receipt identity, not every file it references.

Arithmetic on the recorded values confirms the descriptor ratio 13.724121932651185 and the registered 360-second world limit. The historical maximum would require at least 1.5587528814805556x speedup, or 35.846149% less measured world time, just to reach that limit. These are derived checks, not new timing measurements or predicted optimization gains.

Static design-gate inspection confirms the distinction between mechanical readiness and enabled-witness reporting. It also shows that readiness evaluation occurs after collecting futures, while subprocess timeouts use the remaining global budget. That supports requesting review of automatic early budget cancellation; it does not measure current hotspots or prove that every error path leaks a worker.

No project tests, experiments, builds, native execution, new entropy, mutation probe or panel ran. No implementation, status, protocol, source-release or historical scientific evidence is changed by this documentation repair. No claim is made that the post-stop repair is independently accepted, that its current whole-world speed is known, or that source persistence/recursive enablement is solved.

## Forward result

Decision 0026 and the stable review-request path now contain one consistent review-only instruction set. The Claude output path remains unfilled by this author. The next task is the bounded independent review, not R007 or an automatically authorized benchmark. Repository publication and file-integrity verification of these documentation edits are reported separately in the delivery record; they are not scientific checks.
