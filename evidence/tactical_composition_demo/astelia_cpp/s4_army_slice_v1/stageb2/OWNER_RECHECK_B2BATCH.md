APPROVE_WITH_NOTES
Reviewer family: Codex (separate read-only reviewer agent)

Owner request, sent verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

The reviewer performed a quick separate read-only check of decision 0040's fairness graph/indicator, native/Python branches, five-arm scheduling, candidate audit, prospective readiness, config hashing/source exclusion and DAgger mixture/noise/round gates. No reviewer execution, edits, training, fights or numeric quality scores. PLAN_CURRENT was not touched under the owner's explicit instruction.

Findings and disposition:

- Teacher mixture was declared seed-derived but used a separate entropy RNG draw. Fixed: a deterministic Random((seed << 8) ^ round) draw, shared by every arm on that fight, now matches the sealed declaration.
- Recursive ancestry verification could repeat previous fit/look work many times at rounds 5–10. Fixed: round_check directly binds the previous real-fight ledger/source/binary/parity and completion receipts; prior DAGGER checks are memoized only within one top-level nested gate check, then discarded before the next check/epoch. No identity guard is waived.
- Optional raw-drift hardening of the per-round check. Adopted: check completion status, exact registered job, ledger hash and referenced raw hash as well as completion coverage/hash.
- Historical protected inventory failed on a committed Stage B calibrated-parity update. Followup reviewer confirmed the old inventory is a historical preservation snapshot and that B2SPEED_REPORT already recorded this stale entry. Preserved it unchanged; the new HEAD_0040 inventory uses the same path set and git-show bytes at the captured HEAD, records the old inventory hash and changed hash, and never blesses dirty protected code. Parent receipt/binary pins are unchanged.
- A second pre-existing test assertion expected the earlier 896 movement slots although HEAD already uses 1280. Updated only the B2 assertion to the current movement contract.

Additional checks: full-validation candidate shares now come from native float64 choices, with separate Python float32 counts; this avoids silently attributing certified near-tie differences to the deployed native policy. All five arms have the same parameter count and matched epoch/window/fight-count procedure; N1b/N1rb use their parent Stage B network-only comparator rather than nonexistent new baseline exports.

Verification: 45 unique focused checks passed in a resumed batch (28.25 s total reported pytest time). The first two invocations stopped at the stale assertions above; only failed/unexecuted checks continued, so no successful test was repeated. TESTS_B2BATCH.json records final source/config hashes and bounded evidence. No training, fights, coverage, production build or full validation execution took place. All protected code matches the captured HEAD inventory; existing dirty/untracked work was preserved.

Remaining host qualification: production build and real host coverage/budget/parity, teacher-driving safety and DART effectiveness, per-round student-only fight checks, and look-20/look-50 readiness. Prepared commands are in HOST_COMMANDS_STAGEB2.md. This review approves the implementation batch's bounded engineering delivery, not outcomes, training execution, RRG superiority, source recursion or owner behavioral acceptance.
