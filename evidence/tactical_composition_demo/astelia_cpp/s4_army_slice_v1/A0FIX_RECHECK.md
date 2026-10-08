Recheck complete; findings resolved. Native host validation remains subject to the recorded test result.
Reviewer family: Codex (separate reviewer agent; other-family reviewer unavailable in this session).

Owner request sent verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Scope: compact JSONL transport; actual host CLI and observer/terminal output; explicit pre-data tooling recovery; sealed ledger/request and failed evidence preservation; fresh retry attempt IDs; three-arm real-host smoke.

Finding: when recovery exists, later wall-cap retries could be logged with the legacy JSON failure cause. Fixed by recording each prior attempt's cause separately in the retry notice and new attempt receipt. Added regression coverage with both legacy JSON and cap-interrupted attempts. Reviewer confirmed the disposition with no remaining blocking findings.

The actual legacy stream includes 103 `invalid JSON`, 218 `invalid JSON number` and 755 `trailing JSON input` rows. The third error is confirmed as a parser error in `src/js_value.h:455`. Reviewer confirmed permitting all three while continuing to reject valid rows or unknown errors.

The reviewer confirmed that observer/terminal stdout is independent of `--metrics`, which adds stderr counters only, and that rebuilding is required to refresh the runner source fingerprint before recovery or testing. No tests or host runs were performed by the reviewer.

Decision 0036 quick tooling recheck only; this is not scientific acceptance. As explicitly requested by the owner, no PLAN_CURRENT update or living-document pin was made.
