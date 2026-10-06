READY_FOR_FIXTURES
Reviewer family: Claude

This is the execution-gate copy of the "Delta re-check (a660de0)" section of `REV7_INTEGRATION_REVIEW.md`. The original review file still begins with its first-round verdict.

READY_FOR_FIXTURES
Reviewer family: Claude
Reviewed commit: a660de0 (diff 7c32d34..a660de0, growing_shapes only)
Reviewed execution-pin SHA256: 3b6cf5635a29da1b16969155016655c61c534622129d3fbae30605e19fbbb551

**Checks I ran:**
- I read the whole code diff: `rev7_design.py`, `rev7_qualification.py`, `rev7_fixtures.py`, `rev7_reporting.py`, `rev7_run.py`, `rev7_verify.py`, `rev7_delivery.py` and the 13 new contracts in `test_rev7.py`.
- Synthetic suite, run once with temp and cache files in the scratchpad: **47 passed in 0.90 s** (1.16 s wall). The repository tree stayed clean.
- Pin: `sha256(REV7_SOURCE_IDENTITY.json)` = `3b6cf563…b551`.
  - `rev7_identity.assert_inputs()` passes on all 68 pinned files, and the three committed design files match `git show HEAD`.
  - `REV7_SYNTHETIC_CHECKS.json` reports status PASS, binds the same pin, and its `scientific_input_sha256` equals the pinned set.

**Status of each finding:**

| # | Finding | Status | Evidence |
|---|---|---|---|
| 1 | ω̂ start endpoint | **Resolved** | `rev7_design.py:185` now requires `individual_valid(frames[0])` and `individual_valid(frames[-1])`. The new contract covers a start-endpoint flag (the rate is unchanged) and an interior-only flag (the rate adapts), which matches 10.2's "only if an endpoint sample is invalid". |
| 2 | Recovery veto too wide | **Resolved** | `rev7_qualification.py:164-166` screens only `candidate['ids']`: individual samples plus the candidate's own pairs, O included when it is a member. The whole-cohort screen of the saved 60 s window (`start()`) is unchanged, as 10.2 requires. The contract checks that a non-member at E = 2.0 does not veto and that an invalid member pair does. |
| 3 | F1 FAIL hid F2–F4 | **Resolved** | `rev7_fixtures.py:377-382`: an F1–F4 FAIL lets the remaining F2–F4 run and then stops before F5. N1 FAIL, any INVALID, and an F5 or F7 FAIL still stop at once. The stop flags are unchanged. Both sequence contracts are parameterized over F1–F4 FAIL and N1–F4 INVALID. |
| 4 | F5 not-qualified fraction | **Resolved** (descriptive) | `rev7_reporting.f5_qualification_summary` is attached per start as `qualification_validity`. It reports `used_in_verdict=False`, intervals (0,640], (640,720] and (720,800] s assigned by check endpoint, small-cohort starts kept in the denominator, null when there are no windows, and each fast-transient frame counted once. `rev7_run.qualify` now emits `reason`, so the summary has real data to read; a contract covers this. |
| 5 | Anchor-relative wording | **Resolved** | The integration report now says "identical by construction, not an independent measurement". |

**New defects:** none found.
- The not-qualified fraction gives the owner the cohort-screen risk from finding 4 before development. It is still a design property and is reported descriptively only.

**Gate note for the operator:** `Execution.require` reads the review file's **first line** (`rev7_execution.py:28`). This file still starts with the original `CHANGES_REQUIRED`. Before execution, point `integration_review` at a file whose first line is `READY_FOR_FIXTURES`; this delta section can serve as that file's content. The pin and family lines above already satisfy the substring checks.
