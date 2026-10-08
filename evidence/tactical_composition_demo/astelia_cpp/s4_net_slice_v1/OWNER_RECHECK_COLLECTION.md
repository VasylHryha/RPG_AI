PASS_WITH_NOTES
Reviewer family: Codex
Date: 2026-10-08
Review type: one quick same-family static implementation check under decision 0033 §9.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Scope: only this pre-data slice. Read AGENTS.md, the Claude round-2 notes, contract, teacher/baseline enforcement, collection/process gates, projection and synthetic tests. No tests, build, fights, entropy allocation, collection or training were run by this reviewer. Build and the implementer's single final focused test batch are pending at review time. This is implementation review, not experimental acceptance or Claude's drafter approval.

Findings from this one pass and dispositions observed before completion:

- **R1 — Live cap reduction could permit another launch after spent time exceeded the reduced cap.** Initial `execute()` bounded the next child by the current cap itself and an earlier invocation deadline, without subtracting charged wall. The implementer corrected both the CLI deadline (current live cap minus initially charged wall, accounting for elapsed invocation time before/after waits) and direct execution admission (current cap minus the reconciled charged ledger). A synthetic no-launch regression is present. Resolved by source inspection; runtime verification remains in the final batch.
- **R2 — Sample overflow aggregate omitted its promised totals and denominator.** Per-fight receipts already included own-shell/enemy-threat omission counts, but `sample_measurements()` initially dropped them. The implementer added the two-kind totals and summed decision denominator to SAMPLE/PROJECTION measurements, with a synthetic aggregate assertion. Resolved by source inspection.
- **R3 — Popen.kill could steal the exact child usage in an exit/timeout race.** Python's Popen signal helper may poll/reap an already-exited child before the following `wait4`, losing the sole source of exact per-child CPU/RSS and raising ChildProcessError. Timeout and cleanup now signal through `os.kill(..., SIGKILL)`, tolerate a vanished PID, and retain `wait4` as the sole reaper. A synthetic non-engine child usage test is present. Resolved by source inspection.

No additional blocking defect found in the inspected scope. TEACHER queries add the phase-free spacing drift once after categorical decoding (including same-state shadows); deployment does not add it a second time. N2 export/native admission enforce its frozen baseline coordinates. Overflow is emitted for every gun decision, including zeros. Projection requires measured mean/maximum rows and a complete stratified timing sample, and refuses stale sample/cap inputs. Inventory is sealed before launch, balanced across all twelve strata, assigned whole-group splits, and separates reporting entropy/draws from sampling and fitting. Process ownership follows repository paths, native executable/cwd resolution and encoded Claude scratch paths; ignored foreign processes carry reasons and a vanished-process discovery gets one retry. Complete raw/receipt crash boundaries reconcile without replay; interrupted or failed attempts remain separate and count against physical-launch caps.

Limits to carry forward: a launcher death cannot recover exact child CPU/RSS, so the ledger explicitly records unavailable usage and conservatively charges elapsed wall. Failed launches consume the twenty-sample/two-hundred-total budgets and can therefore prevent completing the full sealed pool; that is the declared hard-cap behavior. The sample predicts resource use, not collection/training feasibility or scientific usefulness. No dataset packer or trainer is delivered here. The frozen collection contract must match the final approved implementation before the build/seal; living documents and the mutable LAB_CAP authority must remain unpinned.

No second reviewer round is requested. Resolve implementation/test failures in the authorized final change batch and record the final build/test receipts separately.
