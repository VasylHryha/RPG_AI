# Stage B evaluation revision recovery

Owner-authorized quick fix under decision 0036, based on HEAD 0b710410064ca2cf45103be79ba6388e432ca346. No changes to PLAN_CURRENT or living-document source pins.

The explicit launcher leaves all original training sources byte-identical, including train.py, runtime.py, models, data, loss, calibration, worker/control and cap code. All original budget sources except the one approved evaluator are conservatively protected. The contemporaneous 9975c289 build additionally proves unchanged generated native and engine sources and unchanged native binary. The recovery receipt seals the original budget hash, old/new source maps, reason, completed training artifact hashes and original parity cache identities/hashes. Protocol hashes describe the committed addendum as historical provenance only.

Use eval_revision.py for recovery, parity, dagger-prepare, dagger-run and later measure commands. It installs receipt-aware train.checked before importing downstream gates. Original direct entrypoints retain their strict refusal; original training/run/worker commands are not modified or exposed through this launcher. Later round measurements register the real current source map, including recovery tooling. A later fit on that newly measured budget can use the original training command.

The round-0 parity launcher preserves the old numeric receipts and their original verdicts. Inside the unchanged process/time/RAM admission it writes separate eval_revision_v1 adjudications under the declared rule, linking each reused receipt's path, hash and original status. Missing sequences use the original calibrated evaluator. An original FAIL is never overwritten. The original DAgger prerequisite gate accepts the newly produced aggregate. No parity or DAgger execution occurred in this change session.

## Separate owner recheck

Reviewer: separate Codex agent, read-only; no other model family was available through the agent interface. Request sent verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Finding: the first launcher delegated to the original parity runner, whose whole-manifest comparison would reject all 184 old cached proofs after the evaluator rebuild. Disposition: fixed with sealed original cache identities and separate deterministic adjudications; original evidence remains unchanged.

Follow-up review: cache handling resolves the blocker; no further material issue by inspection. Reviewer suggested exercising the actual parity_run.gate used by DAgger. Disposition: added that assertion to the cached-manifest transition test before the single test run.

## Validation

Pinned ML Python, focused test_eval_revision.py, one pytest invocation: 38 passed in 1.88 seconds; actual process wall time 2.39 seconds. Fixtures cover training drift before/after sealing, unregistered/deleted sources, unapproved parity edits, receipt/budget/index/raw/export/tool/native drift, idempotence, no living protocol pin, later measurement integration and preserved old-build cache conversion through the actual DAgger prerequisite. Cache fixtures prohibit native replay and check translated-proof drift on resume.

The actual recover-eval-revision --round 0 command succeeded without process admission. Receipt binds original budget SHA256 1d72a6bb4ec7ab781847f61f86a5a3accc863259680eb310c620a598d1461bf1. Every original completed fit and cached parity receipt passed provenance checks. No original budget, trained artifact, build manifest, native binary or cached receipt was rewritten.
