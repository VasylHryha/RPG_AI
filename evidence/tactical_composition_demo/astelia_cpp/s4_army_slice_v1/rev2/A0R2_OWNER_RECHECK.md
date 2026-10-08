# A0 revision 2 owner recheck and disposition

Verdict: no remaining code blocker found; focused validation passed; real-host integration is blocked and unverified.
Reviewer family: Codex. Separate reviewer agent `/root/a0r2_recheck`; same family as implementer, not cross-family milestone acceptance. This A0 delivery is a development revision, not registered milestone evidence.

The owner's request was sent verbatim for both implementation/diagnosis and final evidence:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

The owner explicitly forbids `docs/PLAN_CURRENT.md`; this local record is its authorized substitute for this delivery.

| Finding | Disposition |
|---|---|
| The final six synthetic frames reset cumulative public damage counters, potentially producing equal failure holds instead of healthy reactions. | Fixed before testing. Those frames continue monotonic counters and positions. The C++ checker rejects failed unit-policy outputs; coverage requires healthy output and actual react/guard/body winners. Reviewer inspected the fix and found no remaining defect. |
| Readiness classification should use the exact native geometry eligibility predicate. | Fixed before testing: native prepared, in-reach, living target, non-held fire and react/guard/body/failure exclusions match geometry. |
| A nonempty zero-mismatch table can pass without actually exercising planner commands. | Fixed before testing. The Python proof asserts actual applied singleton and multi-gun aims, plus reaction/body/guard and target-removal coverage. |
| Host integration cannot run under unavailable process discovery. | Diagnosed environment block, not a pass or skipped-success. All three cases attempted once; each gate receipt has pgrep exit 3, `sysmond service not found` and `Cannot get process list`. Each stopped before `execute()`. No retry, bypass or host launch. |

The reviewer checked the public-history ownership, historical V2 routing, transport/parser, fresh entropy separation, casualty reconciliation and conditional target/focus caveats. After fixes, it reported no further blocking code defect. It independently read final receipts and confirmed these results:

- 20 focused tests passed; three host integration cases blocked before launch; one test invocation, 17.36 seconds total. Raw capture is preserved in `A0R2_TESTS.json` and `_local/A0R2_TEST_OUTPUT.txt`.
- 5,436 identical-state frames, including 5,400 recorded-position fixtures and 36 synthetic frames. No combat advancement.
- 210,422 healthy final executed unit-command comparisons: melee 29,727, ranged 126,733 and artillery 53,962. All base-movement/target, participation/react/body, native-bridge and executed-command mismatch rates are zero.
- Artillery no-ready/single-ready/multi-ready comparison denominators are 13,830 / 3,113 / 37,019. Actual planner applications are 316 single-ready and 15,777 multi-ready. Coverage includes 20,583 reaction rows, one guard row, one body row and 365 frames with removed units.
- The recorded fixtures use declared estimates/defaults for fields missing from telemetry. These receipts establish same-state action equivalence, not reproduction of historical execution or repaired combat effectiveness.
- No revision-2 `_local/raw` exists; no pilot/outcome or integration host launches occurred. Fresh 206 pair seeds, all disjoint from the 206 rev-1 seeds, and 618 three-arm requests are sealed separately.

Final source-identity inspection also verified the original rev-1 behavioral hashes still equal `A0_TOOLING_RECOVERY.json`. The analysis script was named `diagnose_a0_decomposition.py` so it does not enter the original runner's `a0_*.py` fingerprint set. Rev-1 declarations, look, report, binary and raw files were preserved. No living-document pins, plan edits, commits or training runs were made.

Remaining gate: run the real-host integration command once on a host with working repository process discovery. Pilot and look-50 commands are prepared for a later owner-operated run; they were not executed by this delivery.
