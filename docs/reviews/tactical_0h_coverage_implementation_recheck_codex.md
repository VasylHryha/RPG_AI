APPROVE_WITH_NOTES

Reviewer family: Codex
Base commit: `0bf4210eca8f5615adf08567cef20d43595c64ea`
Scope: new coverage scratch laws, builder/worktrees, observer, worker, scheduler,
report writer, focused synthetic checks and USAGE. No experimental acceptance.

Owner recheck request sent verbatim to separate reviewer
`/root/coverage_r2_recheck`:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

The separate Codex reviewer inspected the complete implementation statically,
before the focused test batch. It reported CHANGES_REQUIRED for four delivery
defects; all were fixed together before testing:

| Finding | Disposition |
|---|---|
| One incomplete slot discarded every valid partial completion | Verify per slot; retain valid rows and report each missing/invalid slot. Missing runs/integrity pairs keep the arm INCOMPLETE. |
| RD3 control lacked site birth/request/first-cost comparisons | Recover site-named retained terminals from committed COVERAGE_DIAGNOSTIC.json into new outputs, alongside unchanged coverage/assays. |
| Initial candidate cost refusals silently expanded C | Keep initial refusals in separate records and report them explicitly. C retains terminal cost-refusal evidence; a successful recycle does not manufacture C. Only B's boundary definition changes. |
| Build checks allowed current source beside stale copied helpers | Compare current helper/spec/harness bytes and copied worktree inputs to build-receipt hashes before granting or reusing a job. |

Its final static pass returned APPROVE_WITH_NOTES, with no remaining severe gap
in arm semantics, boundary observation, kernel-first imports, build identity,
resume or partial reporting. The minor request to flag a receipt-listed completion
whose local summary has disappeared was also implemented before testing.

The reviewer adversarially confirmed literal cap/cost-only resource-stop
inheritance and B1's existing clearance/count/cost admission. COVA clocks are
kernel-owned and clone-copied at completed integrate boundaries before
adapt/timers/growth, independent of the observer; no intra-check update occurs.
The revised observer samples outages open before the birth, excludes restoring
terminals/gaps from B and retains zero-duration restoration evidence.

The scheduler's projection stop is material: the ten relevant historical RD3
workers have maximum elapsed/CPU duration 1329.3264 seconds. Twenty-two remaining
jobs at ten workers conservatively require three waves (3987.9791 seconds),
above the fixed 3600-second cap. A fresh schedule therefore cannot launch under
this conservative gate. The reviewer confirmed this is a legitimate stop and
USAGE discloses it. No cap increase, plan reduction, new arm rule or approval is
invented. Claude reports the stop to the owner/drafter when executing the gate.

All reviewer passes were read-only: no tests, pilots or process listing. The
implementer performs the single focused synthetic test batch after completing
these changes; its measured outcome and hashes are recorded in
COVERAGE_DELIVERY_VERIFICATION.json. Native builds compile sources without
executing medium trajectories or assays. Full on/off and runtime clone checks
remain NOT_RUN for both coverage arms until a permitted main phase actually
finishes. RD3 B remains separately labelled legacy_B where retained traces cannot
establish all intermediate birth boundaries.

Only Codex-family reviewers are available; this separate pass is not a Claude
acceptance review. Tracking stays in this new artifact because the owner
prohibits edits to docs/PLAN_CURRENT.md. Existing scripts, designs and committed
receipts are preserved; COVERAGE_PRESERVATION.json records their byte identities.

Final validation disposition: 32 focused synthetic tests passed once in 0.92 s
(caffeinate wrapper elapsed/awake 1.145 s). The separate reviewer rechecked the
source/review/test-log hashes and the synthetic PARTIAL report fixture after
this batch, returned APPROVE_WITH_NOTES, and found no further defect requiring
code changes or another test run. Runtime integrity remains NOT_RUN. Primary
Git index writes were denied; delivery uses the explicitly authorized verified
bundle fallback, with repository hooks and only the scoped coverage paths.
