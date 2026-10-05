CHANGES_REQUIRED
Reviewer family: Codex
Reviewed DESIGN_0H.md SHA256: 8f71921ea7f1b2df1b45cfce1b4f3b835644444521282f0fb528a13943929d90

Reviewed document: `evidence/tactical_composition_demo/DESIGN_0H.md`, revision 3, latest touching commit `b323803daf4eb9bf09d193656cfd8c5006453498`. The working document matched that commit byte-for-byte when inspected. Checkout at review start: the same commit. Date: 2026-10-05. Scope: documentation/source re-review within the requested approximately 20-minute cap; no project execution.

Revision 3 resolves the arm/admission conflict, chooses a coherent continuous clock, supplies bounded reward and task screening, and validly defers yardsticks and competence-retention claims. The bootstrap still leaves some measurements and recovery/evaluation transitions undefined. Its section 14 therefore overstates completion of R2-3, R2-4, R2-6, R2-7 and R2-8. These are design repairs for the drafter, not authorization for this reviewer to edit the design or engines.

## Disposition of R2-1 through R2-10

“Resolved” means resolved in the stated document scope, not experimentally verified. A narrowed development claim is allowed; no final experiment or milestone is accepted here.

| Prior finding | Disposition | Revision-3 evidence |
|---|---|---|
| R2-1: arms/admission/freezing | Resolved | Lines 105-112, 169 and 190 give both arms structural admission, make reward the sole additional learning term, and keep library snapshots separate from mutable live groups. Pending snapshot provenance still needs R3-3. |
| R2-2: episode resets/carry | Resolved as a choice of process | Lines 32-34 carry all medium state and the carrier across episodes; lines 51-52 explicitly accept sensor reassignment jumps. Sixteen-second episodes no longer prevent sixty-second windows. The new finite-run/replay boundary needs R3-5. |
| R2-3: driven detector/aliasing | Partial | Cohort ids, finer frames, scaled thresholds and replay/plasticity choices are supplied. The old constant-rate stroboscopic counterexample is addressed. The frozen function cannot consume the stated 600-frame array; recovery population and snapshot timing remain open (R3-1, R3-3). The new rate-bound rationale is incorrect (R3-10). |
| R2-4: timers/events/history | Partial | Lines 118-142 define eligibility, sampled timers, death-before-birth order, pair counting, bounded placement and ids. Gain/coverage warm-up and episodic eligibility are still incomplete (R3-2). |
| R2-5: reward/screening | Resolved | Lines 194-214 orient scores, separate unclipped competence from clipped reward, define paired SE and a finite positive denominator, and freeze the usable list/estimates before training. `remember_static` readiness remains a separate dependency. |
| R2-6: reproducible isolated copies/actions | Partial | Lines 175-183 choose isolated copies, identity pose and a carrier-relative phase reference without a circular-mean singularity. Empty readouts are retained. The movement input binding is absent; copy-panel/identity details need completion (R3-4, R3-8). |
| R2-7: budget-forced settling | Partial | G0' excludes all listed birth rejection reasons and honestly narrows to count settling. Successful D3 budget pruning is not excluded, despite the claim of settling without hitting limits (R3-7). |
| R2-8: G0/G5 read-outs | Partial, with a valid G5 claim reduction | G0 has functional estimands and a specified spatial null. G5 explicitly tests behavioural reproducibility rather than competence retention, so no absolute competence cut is required. Control mismatches, zero-active-site coverage and G5 aggregation still need rules (R3-6, R3-8). |
| R2-9: yardsticks/accounting | Explicitly deferred with narrowed claim | Lines 220-227 report exposure/storage categories and defer all four yardsticks. There is no efficiency comparison. This deferral is sufficient for bootstrap scope. |
| R2-10: revisions/INVALID/stops | Resolved at the policy level | Lines 239-251 distinguish invalid/incomplete execution, stop an empty usable list, cover all outcome-informed protocol changes, and use yes/no rows. Those dispositions do not supply the missing estimators or terminal schedule. |

## Numbered findings and fixes

1. **R3-1 — Blocking: the stated frame count cannot be passed to the frozen window-statistics function.**

   Evidence: design lines 147-155; `geomind/c4_detect.py:100-125`. With 600 frames, `half = 300`, and the function indexes `ths[2 * half]`, `centroid[2 * half]` and `rg[2 * half]`: index 600 is outside an array indexed 0-599. Also, 600 point samples spaced 0.1 seconds apart span 59.9 seconds, not 60 seconds. This is a concrete interface incompatibility, not a request to rerun accepted C4.

   **Fix:** specify 601 endpoint-inclusive state frames at `t_check - 60 + 0.1 j`, `j = 0..600`, giving two exact 30-second halves and 600 integration intervals. Retain the start state and immutable id mapping. Declare the empty/small cohort disposition before calling nearest-neighbour/component functions. Keep the frozen functions unchanged.

2. **R3-2 — High: gain adaptation and coverage still have undefined short-history cases.**

   Evidence: lines 90-103, 108 and 116-129. Natural-rate adaptation waits for a full window, but gain adaptation has no corresponding rule. At the first step, or for a newborn, `PLV over W` is unavailable. A currently strongest site can also have fewer than 80 active partner samples: the gain rule does not say whether it shares section 5's active-sample/eligibility convention or includes inactive-site phase placeholders. Coverage requires the site to have 80 active samples but does not explicitly require the candidate element to have the corresponding history; a newborn's one aligned sample can be treated as PLV=1 unless the eligibility rule is also applied to coverage. The velocity estimator and PLV updates need a common endpoint convention: adaptation precedes appending the current sample, while lock/coverage follow it. The rate estimator can use the current phase plus 100 prior endpoints, but 100 point samples alone span 9.9 seconds. Reward eligibility for elements born during an episode also lacks an averaging denominator and a value during warm-up.

   **Fix:** give one timestamped sampling/update contract that makes both exact velocity endpoints available. Define P and gain updates for insufficient element history, insufficient active-site exposure and no drive; explicitly distinguish those cases if desired. Specify the element/site exposure predicate for coverage and how partial-episode eligibility is averaged for newborns. State which phase/site timestamps are paired and explicitly apply the declared [0,2] gain bound after reward updates. The existing timer/reset and bounded placement choices can stand.

3. **R3-3 — High: replay futures and delayed qualification do not identify the complete dynamical population or the admitted snapshot.**

   Evidence: lines 147, 160-180. The cohort excludes elements born during the window, but those elements remain in the live medium and can affect its C4 forces. “From the snapshot” does not say whether the recovery future contains only the cohort, just the candidate, or all elements alive at the check. These give different recovery outcomes. Running the frozen component functions on the cohort alone can also hide connections to excluded live elements; its membership claim is then restricted to that cohort. A check initiated at t completes at t+60 while the source keeps learning, growing and dying. The document does not say whether the template is taken from the saved state at t, the mutable state at completion, or a recovery endpoint. Only the first of these is the source state whose preceding window was assessed.

   Recorded observations also need the episode boundary/slot assignment and original run-clock alignment to reproduce the drive. An observation alone does not include the episode seed used for its site permutation. The relaxation definition at line 44 does not identify the measured members or whether phase deviation is wrapped, unwrapped or aligned by a collective phase.

   **Fix:** define the recovery population and the id/mask mapping used by the membership comparisons, including how excluded live elements affect forces and graph membership. Explicitly label any cohort-restricted membership claim. Save an immutable check-time state and its coefficient values; specify that delayed acceptance admits that saved template, with separate check/completion timestamps and a rule for subsequent source death. Replay the exact recorded sensor assignment/drive schedule on the original carrier clock. Define the member set and phase/position RMS estimators and their censor flags. Keep recovery score-free and prohibit its result from modifying live training state.

4. **R3-4 — High: the action table is present, but the movement task still lacks an observation-to-drive binding.**

   Evidence: design lines 49-63, 72-79 and 199; `WORLD_REPORT.md:56-64`; committed world ABI `world.h:26-33`. The READY move task has **no enemies**; it exposes `target_angle`, `target_distance`, `desired_range` and approach/keep mode separately. The design assigns “items” to sites and uses item angle/distance/visibility, without mapping that target record to an item/site. Literal enemy-slot encoding therefore produces no drive for move. An implementer can instead synthesize a target item, but then must decide how desired range and retreat are represented; that would complete the scientific procedure by invention. The old design at least listed one move slot; revision 3 removes even that declaration.

   **Fix:** add a per-task legal-observation input table, specifically binding the move target fields to a site/drive and stating how keep/retreat information is used or deliberately omitted. Supply `choice=-1` for all non-choice actions as required by the ABI. Preserve any deliberately limited controller as such; it may legitimately fail the task. Reconcile `remember_static` with the additive stationary-target report rather than the original moving `remember` task.

5. **R3-5 — High: the run duration contradicts the world contract, and terminal checks lack their required future.**

   Evidence: lines 15, 97, 161 and 219. At 16 seconds per episode, 2,000 episodes last **32,000 seconds**, not 8,000. This changes the number of growth/qualification checks and the last-20% interval. With the episode count taken as authoritative, the last scheduled qualification at 31,980 seconds requires replay through 32,040 seconds, beyond the run. Simply leaving that check pending conflicts with the incomplete-run INVALID rule; silently adding episodes changes exposure and the declared protocol.

   **Fix:** choose and reconcile the authoritative episode count/duration. Predeclare the last qualifying start time whose full recovery replay is available, or a separately counted continuation/drain procedure that does not silently add training. Fix the task rotation order and run/episode clock mapping, and define which checks/snapshots belong to the reported horizon. Do not choose this boundary after seeing results.

6. **R3-6 — High: G0 has an undefined coverage denominator and still permits an unmatched control to receive a matched-growth verdict.**

   Evidence: line 233; world report lines 56-64 and 228-239. “Fraction of active sites covered” is 0/0 during move under the literal encoder, and during the 120 hidden decisions of every `remember_static` episode even with a repaired move binding. No zero-active-site convention or eligible-time denominator is specified. Therefore the current G0 estimand can become INVALID throughout an otherwise completed run.

   The control is said to have births at the same times, but a rejected birth may be delayed 20 seconds or dropped. Logging the mismatch does not restore matched additions or determine whether the corresponding seed remains eligible for G0 PASS. Different random birth phases are also part of this control, so it compares a location-and-phase initialization package rather than placement alone.

   **Fix:** specify coverage during zero-active-site intervals, including the aggregation denominator and reported eligible exposure. Either preserve the required birth-time/count match and give infeasible matches a predeclared non-PASS disposition, or explicitly narrow G0 to a comparison of two budget-constrained growth policies, reporting actual birth/death/resource trajectories rather than claiming a matched-placement effect. Declare the control's extra birth suppression, retry draw rule and paired entropy. Retain all delayed/dropped events and identify the phase-initialization intervention.

7. **R3-7 — Medium: G0' still allows count settling enforced by D3.**

   Evidence: lines 136, 139, 234 and 255. Evolving positions can increase neighbour-pair cost between checks. D3 may then remove elements to restore the budget even when no B1 attempt is rejected and no protected-only over-budget state occurs. A low count slope with regular budget pruning can satisfy G0' as written. Reporting turnover makes that visible but does not disqualify the PASS. This is compatible with budget-regulated count stability, but not the summary claim that count settles “without hitting limits.”

   **Fix:** if the intended endpoint is settling without budget enforcement, exclude D3 budget removals and define limit occupancy over the measurement interval as well as birth rejection flags. Otherwise narrow the endpoint/summary to count stability under the declared budget and explicitly report active budget regulation. No task-success requirement is needed for a count-only claim.

8. **R3-8 — Medium: G5 aggregation and copy identity need exact rules.**

   Evidence: lines 175-188 and 237. G5 gives a per-snapshot all-task inequality, then a “median over its snapshots” without stating whether that median is of pass booleans, maximum task differences or a vector of task differences. These are not equivalent. For two snapshots with respective maximum differences 0 and 0.18, a median maximum difference passes the 0.1 cut, but a median Boolean is 0.5 with no declared passing threshold. Empty snapshot sets also need a valid no-formation disposition rather than an undefined median that accidentally becomes a non-finite-measurement INVALID.

   The two copy times are not fixed, and the evaluation-panel lifecycle should explicitly state whether one copy carries across all 128 episodes or is reinstantiated per episode. Sorted JSON keys do not canonicalize the per-member list: source-id ordering and the serialized binding schema must be fixed for the same template to have reproducible identity. The literal pipes in the G5 inequality also split the Markdown table cells.

   **Fix:** define one scalar per snapshot, for example the maximum absolute task-score difference, then its per-seed aggregation, threshold, even-count and empty-set rules. Pin two carrier offsets and the panel/reset order shared by the paired copies. Define canonical member ordering and binding serialization; escape the table's absolute-value bars. Keep the claim as behavioural reproducibility: adding a competence-retention threshold is unnecessary under this valid deferral.

9. **R3-9 — Medium interpretation note: driven recovery no longer inherits C4's clump-rejection argument.**

   Evidence: design lines 21-22 and 160-167; `geomind/c4_detect.py:28-30`; `geomind/c4_model.py:42-48`. The undriven detector's argument is that a phase-uncoupled clump cannot restore a kicked phase pattern. The added external term itself supplies a restoring force: near a fixed drive phase, a phase perturbation obeys approximately `delta_dot = -g k K delta`, even with internal phase coupling removed. Thus driven recovery alone does not distinguish internally maintained geometry-mode closure from common-input entrainment. This does not prove that an entire clump passes every design criterion, nor invalidate a deliberately limited driven-stability assay.

   **Fix:** explicitly define this revision's atoms as structurally qualified **driven** snapshots, with autonomous persistence and new causal closure qualification unclaimed. If a later claim needs newly demonstrated resonator closure, qualify the driven adapter against a matched common-drive/clump control then. No added experiment is required now if the claim remains narrowed. The existing background/composition deferrals stand.

10. **R3-10 — Low: the anti-aliasing grid fixes the old example, but its stated rate bound is false.**

    Evidence: lines 56, 61-62, 101 and 148; `geomind/c4_model.py:100-101`. The clipped **intrinsic** rate spread is at most pi rad/s. Actual relative phase derivatives also include both elements' C4 coupling and external drive, so they are not bounded by that spread. The claimed 0.31-radian maximum increment does not follow. Nevertheless, sampling the previous fixed-rate counterexample every 0.1 seconds instead of every 2 seconds exposes its drifting pair pattern; this specific R2 defect is repaired.

    **Fix:** replace the bound with one derived from the full RHS, gain/drive limits and sensor geometry, and state the sampling guarantee actually supported. Keep the original counterexample as a negative contract. This review has not established a new full-detector aliasing false PASS at the 0.1-second grid and does not require a finer grid merely because the written justification is wrong.

## Evidence and boundary

Read AGENTS.md, the R2 review and relevant R1 passages, revision-3 design/its diff, decision 0028 item 17, R5, CURRENT.md and relevant pinned source-04 passages, frozen C4 model/detector and C5 detector functions, and the world report/action contract. The consulted C4/C5 source hashes match the C5 R003 receipt; source 04 matches CURRENT.md. This is not a new source audit or driven-adapter qualification.

The world report's original READY contract was available at the start. Its `remember_static` addendum arrived during this review and was read through line 272; the observed report SHA256 was `b5ba3f12c62b12f82448518632d83d6458a09eef1de363d5a438125bd4a180fc`. The addendum labels its implementation REVIEW_READY for Claude. Its receipts were not executed or independently qualified here. Original moving `remember` measurements are not evidence for stationary `remember_static`; the addendum supplies its separate reported measurements. The medium implementation was not reviewed.

Other agents changed/staged engine files and advanced HEAD during this review. The reviewed design identity remained unchanged when rechecked; the review is pinned to the named design commit/hash, not to concurrent engine work. No project code, tests, scripts, pilots, experiments or panels were run. Only this review file was written; no commit and no milestone/status changes.

The drafter should finish the remaining bootstrap contract repairs and correct the section-14 dispositions. The continuous-run choice, shared structural admission, bounded reward, descriptive competence and scope deferrals can remain. Engine readiness and this review do not authorize section 10; the separate owner go-ahead remains required after the design passes review.
