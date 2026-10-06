# Scoped v5 Part 1 plan and recheck

Owner scope overrides the repository tracking location: this file tracks rechecks because docs/PLAN_CURRENT.md and DESIGN_0G.md are explicitly excluded. Other tracks and pre-existing s4_v5_checks artifacts remain unchanged.

1. Read AGENTS.md, sections 13–17/amendments, attribution and v4 recheck, round-1 review — complete.
2. Cross-family Codex round-2 review of Claude's amended design — APPROVE_WITH_NOTES. F1–F3 resolved. Separate reviewer design_r2_recheck confirmed the scope/ranking/gates without execution.
3. Implement native v5=v3 alias preserving H/F/HF/v4, exact B ranking/selection and validation gates, A/B only, omega diagnostics, fresh independent ledger and full 360-minute bounded deadline — complete.
4. Mandatory implementation recheck — reviewer v5_implementation_recheck. Initial findings: stale interrupted incumbent/omega and missing failed-run timing. Disposition: shared partial/completed selection state, immediate omega output, failure elapsed/allowance and timing finally; nonzero-omega interruption and failed-run timing fixtures added before tests. Claude CLI attempted; returned Not logged in. Same-family fallback disclosed, no cross-family implementation acceptance.
5. One native build, then the final affected test batch (v5 and existing deadline tests), after the documented failed-fixture attempt, all code/test/review-driven edits complete beforehand — complete.
6. Readiness, scoped normal-hook commit in an isolated Git directory, verified bundle and delivery sidecar, files under 50 MB — completed by normal-hook isolated commit and verified bundle; see PART1_DELIVERY.json.

Owner request sent verbatim to both separate reviewers:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Root-plan handoff for its owner: B4 design round 2 APPROVE_WITH_NOTES; Part 1 implements amended A/B-only v5. Record final build/test and verified-bundle identities from adjacent receipts. Do not claim development completion, C authority, S5 readiness, judging, registration or scientific acceptance. Development still awaits its separate authorized scheduled launch after tonight's C6 timing.

| Yes/no condition | Action | Responsible role |
|---|---|---|
| Did design round 2 approve? | Complete conditional Part 1. | implementer |
| Did implementation recheck find a defect? | Repair the full batch before tests. | implementer |
| Are build/tests/delivery identities unresolved? | Report NOT_READY. | implementer |
| Did Part 1 checks and delivery pass? | Deliver READY_TO_RUN and stop without development. | implementer |

Final checks: native build exit 0, 6.052 seconds; 27 affected tests passed in 1.73 seconds. One failed fixture attempt is preserved separately; one successful retry after the reviewed test-only allowance repair. Source/cache final-batch identity finding also repaired before final build/tests. READY_TO_RUN; development not executed, no C authority.
