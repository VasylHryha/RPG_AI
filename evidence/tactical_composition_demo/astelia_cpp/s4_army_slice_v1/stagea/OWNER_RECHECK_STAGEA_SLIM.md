APPROVE_WITH_HOST_VALIDATION_PENDING
Reviewer family: Codex
Baseline: 28e5ff8
Separate reviewer: /root/stagea_slim_recheck; static review, no code execution.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Finding: duration normalization originally multiplied observed bytes by 150/t_end, slightly discounting a valid full-duration native fight. Disposition: normalize shorter measurements to the engine's accumulated last-tick horizon; never discount observed bytes. A regression covers the full-duration case and the exact remaining-fights/free-space formula.

Evidence qualification: the early codec's partial trace projected almost 4 GB, and the separated-army memory fixture does not measure combat/threat/event volume. Disposition: retain the initial measurements, tighten the representation of A0 metric events, qualify every offline estimate, and require the actual collection sample's disk gate before continuation. The final partial estimate is 3.80 GB; this is not completed-collection evidence.

Final reviewer response: "The disk undercount is fixed: projection uses the native last-tick horizon and never discounts observed bytes. The regression test covers a full-duration fight. The compact A0 event arrays preserve every field consumed by metric endpoints. Label/event ordering changes leave their independent aggregates unchanged; the added full-versus-slim comparison covers those endpoints. The excluded max_frame_bytes appropriately reflects serialized representation. No unresolved implementation findings. Full host tests and the measured collection sample remain necessary to establish the size target."

Validation disposition: 20 focused tests passed once after the complete code/review batch. A test-launcher failure occurred before pytest could start because resolving the virtualenv symlink selected the base Python; its receipt remains unchanged, and the corrected launcher preserves the virtualenv path. Host tests were attempted once and stopped at the existing process-discovery gate before a fight; the second host fixture was not reached under -x. The exact host continuation is documented. Recovery registered the same 180 sealed jobs prospectively, preserved both invalid-end-time attempts and the original RSS failure, and ran no collection retry. No plan file was edited.

The separate reviewer also checked the final receipts, recovery and host-command chain without execution or edits. It found no report/command gap: the focused-pass receipt, preserved launcher failure, pre-combat process-discovery refusal, original RSS plus both time-boundary failures, qualified partial-size projection and refusal-stopping host commands all match the delivery. Its remaining bookkeeping request was completed by creating the final path-only change inventory. Host tests and the actual sample remain pending; nothing upgrades those gates to PASS.
