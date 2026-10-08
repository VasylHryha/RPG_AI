PASS_WITH_NONBLOCKING_NOTE
Reviewer family: Codex

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Separate read-only reviewer: disk_recheck. Quick development-tool recheck under decision 0036; not a scientific result acceptance. No tests or combat were run by the reviewer. No other model family was available through delegation in this session.

Finding and disposition: pending/active recovery markers initially used direct exclusive JSON writes. An interruption could leave an unreadable marker. Resolved before testing: both markers now use a temporary file, fsync and atomic replacement while both repository locks are held. The reviewer inspected the final helper and confirmed resolution. Added a replacement-interruption regression and the existing interruption/resume test.

The reviewer caught an unfinished synthetic target test: two fights projected 47 MB, so expecting 5 GB contradicted the policy. Corrected its synthetic byte rate to project 4.7 GB; the compatible small-projection test explicitly checks retention of 4 GB.

No further blocking findings in source-change restrictions, unchanged native binary and request identity, preservation of earlier evidence, logged completion reuse/resampling, all-600 A0 length provenance, byte-rate projection, or the unchanged worst-case free-space formula.

Nonblocking note: if all old calibration recordings are incompatible, recovery retains the original 4 GB target until fresh measurements exist. Those fights use registered new completion destinations. A later projection above that target stops safely and requires another explicit target revision; this recovery does not silently increase an unmeasured target. The supplied host has six compatible completed samples, so it selects and logs 5 GB during recovery. This edge does not block the requested host continuation.

Disposition is recorded here as instructed. docs/PLAN_CURRENT.md is untouched; no living documentation is source-pinned. Focused verification is recorded separately after the complete source and test change batch.

Recovery schema correction: the reviewer verified the A0 producer writes successful COMPLETE receipts without a status field. Removing the invented status check retains immutable look membership, completion hash, exact job and ledger checks. No further findings on this correction.

Corrective source revision: the first focused test attempt stopped after 25 passing tests because the synthetic worst-case expectation grouped floating operations differently from the preserved production formula. Corrected the test to the exact original expression. The failed test source, stdout/stderr and receipt remain preserved. The passing native fixture suites had not yet run in that attempt.

The follow-up Python revision is registered through recover-disk, with new ledger/manifest identity and snapshots of the previous active/pending markers. Reused receipts retain their original ledger provenance and completion locations. During this separate recheck, the reviewer found that earlier disk ledgers were not inherited into preserved_evidence across a third revision. Resolved before final testing: each new revision adds its previous ledger to the inherited preservation map. The reviewer confirmed the correction and no unresolved blocking findings. The final regression covers three revisions, interrupted sequential activation, unchanged original receipt hashes/paths, and rejection of earlier-ledger tampering.

Final focused batch: 40 passed in 40.46 seconds, measured wall 41.14 seconds, including both real-host fixture suites in test mode. No skips. The source files were complete before this batch and were not edited afterwards. The first test failure justified this corrective batch; no passed suite was routinely repeated.

Production disk check against six sealed samples passes: projected collection 4.231704 GB, declared target 5 GB, 174 remaining fights, unchanged required-free formula gives 13.181294 GB against 17.140494 GB available. Native binary unchanged; zero sealed collection fights launched by this task. All 290 inventoried prior artifacts besides the intentionally revised build manifest remain unchanged; the original manifest is preserved. The live gate's earlier diagnostic is preserved in recovery snapshots. docs/PLAN_CURRENT.md remains unchanged.

Final report recheck: the separate reviewer inspected the passing test log, validation receipt and continuation instructions. No new findings. It confirmed all 40 tests passed without skips, the production disk numbers match the receipt, and the commands match current CLIs and retain outcome gates. No source changes or tests followed the successful batch.
