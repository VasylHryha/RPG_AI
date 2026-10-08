CHANGES_REQUIRED
Reviewer family: Codex (separate tooling reviewer; same family as implementer)

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Read-only, one-pass tooling review of v5b and its explicitly inherited v5
inputs. No tests, calibration, native fights, or other labs were run or
inspected. This is not a Claude/cross-family scientific review or acceptance.
Focused verification remains pending with the implementer.

## Finding

F1: Reject mechanism calibration/run in this sealed continuation before any
writes. `ensure_stage('mechanism', ...)` currently returns successfully;
`run('mechanism', ...)` subsequently overwrites inherited `RUN_GATE_mechanism.json`
and may overwrite `RUN_mechanism.json` or create a new mechanism attempt.
These existing receipt bytes are pinned in `CONTINUATION.json`, so an exposed
CLI command can damage the exact inherited identity and block subsequent
admission even without replaying a fight. `calibrate('mechanism', ...)` also
writes the inherited `CALIBRATION_mechanism_PROJECTION.json`; its bytes can
change with the current cap. The README's instruction not to rerun the
mechanism stage should also be enforced by the command functions. Keep
mechanism receipt verification available to outcome/series admission.

Suggested focused regression: call both mechanism command functions with
execution forbidden, assert immediate rejection, and compare all inherited
receipt bytes before/after. Collect this correction before the single final
test batch.

## Other inspected behavior

- The binary path points to the admitted v5 binary and no rebuilding occurs.
  Requests and metrics match v5; original declaration/entropy/pick/read bytes
  are inherited and sealed. Locally frozen spec/decision copies are checked
  against the original declaration digests.
- Mechanism completion digests bind the already measured receipt statistics
  to the existing compressed stream hashes; admission does not decode raw.
  New completions need a receipt/metrics measurement seal. Missing seals and
  warm-cache receipt edits are covered by the added no-fight regression.
- `records_for('mechanism')` preserves the original receipt order recorded in
  `mechanism_tags`, and checks exact set coverage. This preserves floating
  aggregation order and the existing summary/pick/read identity.
- Outcome planning resolves the pick once per plan. The 166,238-byte
  continuation manifest is still parsed per completion, adding avoidable
  bounded JSON work; this is not evidence of another telemetry decode loop.
  The hard-deadline recorded-receipt test should establish the actual cost.
- Shared parent/local execution locks, process-discovery fail-closed behavior,
  owner cap policy, attempt/resume logic, sequential read gates and immutable
  pick are retained. The abandoned v5 outcome attempt stays historical audit
  material and supplies no v5b calibrated timing.
- The regression distinguishes real recorded-receipt CLI preflight timing
  from synthetic full-calibration control-flow timing. Neither is actual
  outcome fight calibration time; the final handoff must retain that distinction.

## Disposition

Implementer disposition (after the review; no second review pass): F1 fixed.
`ensure_stage('mechanism', ...)` rejects mechanism calibrate/run/review before
any writes or compute attempt. Three parametrized regressions forbid writes
and execution and compare every inherited receipt byte afterwards.

Final focused batch, once after all planned source/test/review edits: 19 PASS
in 19.80 s (process 20.427 s). Real recorded-receipt outcome calibration
preflight: 1.718 s, under a 20 s subprocess deadline. Full calibration control
flow with synthetic outcome samples: 3.179 s. Zero native fights; actual
outcome calibration timing remains Claude's work. See TESTS.json and both
CALIBRATE_*_TIMING.json receipts. Review F1 is resolved; no other blocking
finding was reported. The original CHANGES_REQUIRED verdict above is retained
as the review history, not rewritten into a second reviewer verdict.
