Numerical prerequisite for Track B B4d; docs/PLAN_CURRENT.md is maintained by Claude and is not edited here.

1. Read design 18 + 18.1 + 18.2, approved round-3 review and v5 commit 240aea2. DONE.
2. Pin existing tracked files and the complete numerical fixture matrix before testing. DONE; S4_V6_PRESERVATION_PIN.json; generated FIXTURES.json before execution.
3. Implement the separate complex RHS, group/similarity/alignment contract and exact 18.2 trial policy. DONE pending engineering review and checks.
4. Send the owner request verbatim to the reviewer; fix implementation findings before the test batch. IN PROGRESS. Claude CLI returned Not logged in; separate Codex reviewer is the disclosed fallback.
5. Build the no-combat fixture executable; run the numerical fixture suite once after the completed change batch. PENDING. This early prerequisite result is required to decide whether controller integration is permitted. Section 18.2 explicitly requires implementation to stop if accuracy fails anywhere.
6. If that prerequisite passes, integrate v6 dispatch/controller/host and complete counter/clone/action/gate fixtures, review, then test that complete change batch before any fight. Otherwise mark the dependent checks not_run and STOP implementation.
7. Only on all checks passing, declare fresh development entropy and execute A/B once under caffeinate with 10 workers. No low-load wait.
8. Report, verbatim owner recheck, disposition, scoped normal-hook commit or independently verified bundle. No S5/judging/registration/status changes.

Owner request, verbatim:
> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.
