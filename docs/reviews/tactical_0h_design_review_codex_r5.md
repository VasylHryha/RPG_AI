APPROVE_WITH_NOTES
Reviewer family: Codex
Reviewed DESIGN_0H.md SHA256: 9e2c50813b0695b419ec37ebd4f2370673da169e63e7aac236a832cb8d3a14f2

Reviewed document: `evidence/tactical_composition_demo/DESIGN_0H.md`, revision 5, commit `837a9db2c03e9bb8ec9970ce556e7552f12ff42e`. The working document matches that commit byte-for-byte. Date: 2026-10-05. Scope: bounded documentation/source re-review within the requested approximately 20-minute cap. No project code or experiments were run.

The material R4 findings are resolved in the bootstrap design. R4-2 is explicitly deferred to a reviewed integration batch that blocks section 10; R4-9 is resolved by narrowed interpretations. No new blocking design defect was found. The remaining notes concern wording, exact engine integration boundaries and prospective workload. This verdict approves the bounded design for implementation; it accepts no scientific claim, engine follow-up, development result or milestone, and does not authorize the development run.

## Disposition of R4-1 through R4-9

“Resolved” below means resolved as a design contract, without experimental verification.

| Prior finding | Disposition | Revision-5 evidence |
|---|---|---|
| R4-1: no-drive gain and current endpoint | Resolved for the local statistics | Lines 104-109 and 122-124 append the current sample first, use k−99 through k for local PLV/exposure and k−100 for the rate endpoint, leave g unchanged when P is undefined, and retain gain clipping. The overly broad qualification wording needs the low cleanup in R5-1. |
| R4-2: engine readiness versus integration readiness | Explicitly deferred behind a stop gate | Lines 13 and 299 require the design-specific medium batch to be closed and reviewed before section 10. Gain inside the full driven RK4 RHS, world-step histories carried through strength changes, cost, eligibility, coverage and placement are named. READY does not close this dependency. |
| R4-3: physical sites and template bindings | Resolved by the governing mapping rule | Line 51 makes every task use logical slots mapped through an episode-seeded permutation, including single-item tasks, and gives the per-task strength table precedence. Lines 210-212 hash the binding rule rather than a realized assignment; paired copies use the same evaluation episode seed. Two residual shorthand rows need only the cleanup in R5-2. |
| R4-4: G0 queue, entropy and terminal future | Resolved | Lines 274-282 turn B1 off in the control, specify FIFO requests, at most two attempts per check, uniform position/phase draws in a separate paired entropy domain, redraws, feasibility, at most one later-check retry, terminal drops and non-PASS flags. Read FIFO literally: an unsuccessful head request stays ahead of later requests and cannot consume its retry at that same check. The control remains a budget-constrained policy comparison, not matched placement. |
| R4-5: usable-task rotation | Resolved | Line 253 filters the declared order through the frozen usable list and shares that schedule with both arms and controls. Empty usable lists stop before training. |
| R4-6: evaluator copy lifecycle | Resolved | Lines 214 and 220-223 consistently instantiate a fresh isolated template copy per episode. Primary competence uses carrier offset 0; G0 uses the same procedure for the final whole-medium state. Abstentions remain scored. |
| R4-7: overlapping G5 verdicts | Resolved | Lines 284-289 explicitly order INVALID, fewer-than-six formation INCONCLUSIVE, PASS, FAIL and residual INCONCLUSIVE. Five snapshot-bearing seeds with zero passing fractions now yield INCONCLUSIVE only. |
| R4-8: stale dependencies and broken action row | Resolved | Lines 12-13 and 245 reflect the delivered world/medium and additive memory task; line 92 uses abs(wrap(...)), preserving the Markdown columns. Engine readiness retains its bounded meaning. |
| R4-9: alias screen and equivalent copies | Resolved by narrowed claims | Line 170 explicitly denies an alias-free guarantee; line 272 calls G5 a numerical copy-covariance check and disclaims usefulness/persistence. Competence is reported separately. |

Section 14 accurately records these substantive repairs. Its historical shorthand does not override the current narrowed G5 claim or the separate medium dependency.

## Numbered findings and fixes

1. **R5-1 — Low: limit the new “same window” sentence to local statistics and make initialization explicit.**

   Evidence: design lines 104-107, 137 and 168-169; `geomind/c4_detect.py:100-125`. Line 104 says that every statistic, including qualification, uses the last 100 samples. Section 6 instead gives the correct, specific 601-frame qualification window. These must be separate histories/windows: local PLV uses 100 samples, the rate needs 101 endpoints, and qualification needs 601 endpoint-inclusive state frames. The specific section-6 contract is sufficient to resolve the intended detector input; the general sentence should not be copied literally into an implementation.

   **Fix:** restrict “same window” to local adaptation, lock, coverage and timer statistics; say that qualification uses section 6's separate window at the same current endpoint. Explicitly retain the initial t=0 state for the first qualification window. Keep newborn histories empty as declared. This is a clarification of the existing specific contracts, not a change to their lengths or thresholds.

2. **R5-2 — Low: finish the logical-slot and strength prose cleanup.**

   Evidence: lines 51, 59-60 and 73-76. The governing paragraph now unambiguously maps slot 0 to physical site π_e(0), but the move and memory table rows still say “site 0.” The general strength block also repeats the enemy-distance formula without restating its precedence relative to the move formula.

   **Fix:** write “logical slot 0 → physical site π_e(0)” in those two rows, and label the general strength block as the enemy-task formulas, with move governed by its table row. Preserve the rule-based template serialization and record realized assignments. No binding redesign is needed.

3. **R5-3 — Low integration note: carry exact drive/readout reach conventions into the already required follow-up.**

   Evidence: design lines 69, 81 and 140-146; `growing_shapes/medium/MEDIUM_REPORT.md` drive/readout contracts; `medium.cpp:98-101`. The design's drive kernel includes r=3, whereas the reviewed engine uses strict r<reach. The design's “within 2” readout wording should also be reconciled with the engine's strict reach. This does not invalidate the engine's own READY contract or reopen its review; it is another boundary case for the design-specific integration gate already added in response to R4-2.

   **Fix:** have the drafter record the intended inclusive/exclusive drive and readout boundaries, and have the follow-up preserve that convention consistently in integration, active-partner eligibility, coverage and readout. Include focused exact-boundary verification in that batch. Do not silently substitute the engine defaults for the written design law. No engine edit is made or requested from this reviewer.

4. **R5-4 — Low planning note: the finite protocol does not yet establish practical execution time.**

   Evidence: lines 202, 214, 220, 252-254 and 272. The continuous training horizon, population cap, qualification count and per-episode evaluator panels make the procedure finite and computable. Nevertheless, exact template hashes can differ at every check even when the same live group persists; duplicate suppression does not bound the library to one snapshot per group.

   For the 16 primary runs alone there are 8,512 qualification checks. With at most 64 elements and disjoint candidates of at least three members, an upper bound is 21 admitted snapshots per check, or 178,752 snapshots. With all four tasks usable, the two G5 offsets require 2×4×128×160×5 = 819,200 RK4 substeps per snapshot, up to 146,433,638,400 substeps in this deliberately loose worst case. Training plus the 16 paired G0 controls adds 51,200,000 substeps; recovery futures and detector work are additional. These are arithmetic bounds, not observed formation counts, timings or a prediction that the bound will be reached. The reported synthetic medium speed does not measure this complete workload.

   **Fix:** before an authorized long run, estimate its duration from the completed integration and report that estimate to the owner under AGENTS.md. Use bounded-memory replay/archive handling and resumable evaluation of the unchanged fixed panels. If resource limits interrupt execution, preserve raw evidence and apply the existing incomplete-run INVALID rule. Do not reduce snapshots, panels or seeds after observing results to make the run finish; such a protocol change requires the declared new revision/fresh-seed path. No benchmark or pilot is authorized by this note.

## Recheck of the revision-3 mechanisms

The continuous-run choice remains coherent: the medium, carrier, coefficients, histories, timers and ids carry across 16-second world episodes; sensor reassignment jumps are explicitly allowed in windows. Training lasts 32,000 seconds, qualification starts only through 31,920 and its last replay ends at 31,980. Control retries have a terminal-drop rule, so neither recovery nor queue draining silently adds training episodes.

The driven adapter uses immutable cohort ids and the corrected 601 frames. That array gives the frozen window function two exact 30-second halves; the threshold table preserves the declared T=2 time/frequency scaling. The original stroboscopic negative contract remains. The wrapped-increment flag is a limited warning screen and supplies no universal anti-aliasing or driven-detector qualification claim.

Recovery is computable without a causal loop: the score-independent library does not alter training, so the subsequent actual drive schedule can be recorded before evaluating the paired futures. Both futures use the complete saved check-time population and frozen coefficients, with plasticity/growth/reward off; membership is explicitly cohort-restricted. Admission retains the check-time template even if the source dies later. The original carrier/site assignment is replayed, and aligned relaxation estimators have a finite censoring horizon. This measures recovery under common drive, not autonomous closure or a closed-loop task future.

Local timers, warm-up, active-partner eligibility, protection, death-before-birth order, finite spiral placement, cost recomputation and event logging remain specified. The input/action table consumes legal world fields, handles move's separate target record and stationary hidden-target memory, and supplies choice=−1 outside choose. Isolated per-episode copies preserve pose and carrier-relative phases without requiring a nonzero circular resultant; empty readouts remain scored abstentions. G0 reports eligible exposure and the narrowed policy comparison, G0' reports budget-regulated count stability, G1 reports formation, G1c is descriptive and G5 is numerical covariance. INVALID precedes verdict cuts; no formation is distinguished from measurement failure.

The accepted C4 law/functions are read-only ingredients, not acceptance of this adapter. Composition, bonds, duplicates, efficiency, autonomous persistence and causal background claims remain outside the required bootstrap endpoints. H-BG/H-PS/H-RBG stay NOT_TESTED. No new H-M or H-U qualification is established by this review.

## Evidence and boundary

Read AGENTS.md, revision 5 and its diff from revision 4, the complete R4/R3 reviews and relevant R2 passages, decision 0028 item 17, R5, CURRENT.md and relevant pinned source-04 passages, the C4 model/detector and C5 detector functions, C4 thresholds, both engine reports and their stored Claude reviews, the world ABI and relevant medium ABI/RHS passages. The consulted C4/C5 source hashes match the C5 R003 receipt; source 04 matches CURRENT.md. This is not a new source audit, engine qualification or execution-readiness review.

World report SHA256: `b5ba3f12c62b12f82448518632d83d6458a09eef1de363d5a438125bd4a180fc`. Medium report SHA256: `65c2e64f5111eed347a75307bc7245ed4c0217786e59515cf955455d107dde2b`. Stored checks were read as reported engine evidence; none was rerun. The supplied READY/review boundary is preserved.

The next distinct gate is the completed, reviewed design-specific medium integration and runner; section 10 additionally requires the owner's separate go-ahead stated at line 9. Only `docs/reviews/tactical_0h_design_review_codex_r5.md` was written. No project code, tests, scripts, pilots, experiments or panels were run; no commit, engine/design edit or status change was made. Unrelated untracked work was preserved.
