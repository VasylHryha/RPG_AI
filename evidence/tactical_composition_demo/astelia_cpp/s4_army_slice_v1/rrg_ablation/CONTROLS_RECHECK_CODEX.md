PASS

Reviewer family: Codex
Date: 2026-10-09
Reviewed controls JSON SHA256: `5a83a5451a3fba12ec9c40dfa2843c4cad362b424ed98a3836e28d3693e501d9`
Original metrics JSON SHA256, independently verified unchanged: `64c1c652fcca0c48d72eb05733abe4b8fc1eee1f8f63458c858d7540d781bc93`

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

No blocking findings for these owner-requested exploratory offline controls and their bounded report. This is a separate Codex review, not a cross-family review or milestone acceptance. The parent reports that Claude CLI authentication is unavailable; I did not independently authenticate Claude.

I reviewed the new inference/model/report/test source, the original replay/data/forward source, both reports, the controls protocol, recorded test output and the original Claude findings. I independently checked stored-result arithmetic and file hashes with standard-library reads only. I did not run inference, tests, training or simulated fights, and changed only this review file.

The result supports substantial dependence on the hand-wired neighbour-target readout. With intact dynamics but that bonus removed, only 1.52% of the original ranged margin and 0.75% of the artillery margin remain over N1. Replacing the bonus by its synchronous indicator while setting K=0 recovers 60.69% and 49.22%, respectively. Thus the readout is needed to express almost all the original margin in this checkpoint, and a large part can be recovered without coupling. The remaining gap does not uniquely establish information carried by dynamics: the learned head still receives absolute and neighbour phase features, and its inputs change under the intervention. The report's partial/mixed-recovery verdict is justified.

Disposition of the original findings, within the owner's permitted folder:

- H1: addressed by exact K=0 indicator substitution and intact-no-bonus removal. K=0 retains original forcing, omega, head features and fire window; the indicator is exactly +2 for any valid assigned neighbour, including no phase-cancellation veto. No-bonus scoring uses captured pre-addition intact logits; this addition cannot affect recurrent state on fixed recorded inputs.
- H2: addressed by the top report-only correction and revised reading in the original Markdown. The metrics JSON is byte-identical. Neither report excludes memory or claims source resonance, live feedback or recursive background transformation.
- M1: addressed by forcing-only removal with learned K/omega retained and raw forcing still supplied to the head. Reports explicitly explain that the earlier three alignment cuts are not independent confirmations.
- M2: the requested same-role shuffle and forced-synchrony controls are present. Shuffle operates after each physical update, within public role groups, and its state is carried forward; the PRNG is reset per fight. Synchrony sets the common absolute phase to zero each tick. The reports correctly retain the limitation that these do not match disturbance magnitude or guarantee familiar joint inputs. This addresses the missing requested controls, not the stronger claim of fully matched distributions.
- M3: both readouts and their fixed transformations are listed in both reports and the local controls protocol. Upstream Stage A documentation remains untouched under the explicit user scope.

Evidence checks:

- All 89 recorded input/source pins match the current files, including the original executed-source snapshot and new control sources. Original JSON identity matches the fixed expected digest.
- Fifty fight tags, window starts and scored-tick counts match the original sequence records. Full-prefix frames sum to 63,897; scored unit rows sum to 592,992. Stored scored-row identity matches the original. Intact rows and target/fire correct counts agree separately for every fight and role.
- Every control's aggregate row, target/fire correct and aim-row counts equal the sums of its per-fight counts. Target/fire/calibrated/safety-calibrated accuracies and movement errors match row-weighted aggregation; aim errors match aim-row weighting. Reported comparison deltas and retained-margin fractions agree with the underlying metrics.
- Diagnostic counts aggregate correctly per role. Support numerators exclude None and cannot exceed non-None oracle denominators; both all-row and non-None fractions and trivial-rule accuracies match their counts. Source uses the same nearest-eight graph with a strict 300-pixel radius and current assignments, excluding dead/None targets. The trivial rule's distance/ID tie breaking and nearest fallback match its description. Its low all-row accuracy is compatible with its inability to choose None while any enemy remains; this does not refute the neighbour feature.
- Removing the fire window leaves target accuracy exactly unchanged. Raw fire accuracy drops by 8.50/7.79/11.18 percentage points for melee/ranged/artillery; unchanged-threshold calibrated accuracy changes by -1.18/+2.46/+0.52 points. The report keeps these distinct and makes no recalibrated-performance claim.
- The source fixes the inherited forcing-definition inconsistency identified in my earlier review, and the shuffle test now carries perturbed state. The stored receipt records 16 synthetic tests passing; I reviewed but did not rerun them. Execution records nice 15 and one Torch thread plus one interop thread; import-time BLAS limits are one.

Limits: counts/hash consistency and source inspection are independently checked; the recorded raw rows were not independently replayed. One checkpoint, one training seed, one shuffle seed, fixed positions/assignments and repeated dependent unit ticks limit causal and architecture claims. Retraining a feature-matched control would answer a different question and is outside this task. No changes to docs/PLAN_CURRENT.md or upstream stage folders are requested by this review.
