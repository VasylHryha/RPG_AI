APPROVE

Reviewer family: Claude (claude-opus-5-5)
Reviewed: `astelia_cpp/s6_run.py` (sha256 `95609f7fba04f934fee98d13c0c810a1b0cdfb95e845add831b1dbeefa2e928c`, commit `7441bf0`) and `test_s6_run.py`, against `SPEC_0G.json` revision 4 (sha256 `158031e9…f8c8335`, Codex review r4 APPROVE_WITH_NOTES)
Date: 2026-10-05

## Checked

- **Requests:** `request_for` produced requests **identical** to `s3_runner.request` (the builder that produced the S4 fights) in four cases, with fake seeds:
  - HEAD novice resonator;
  - HEAD regular nearest, swapped;
  - POOL "wedge flank" morale, swapped;
  - POOL "alone" resonator with diagnostics.

  The diagnostics flag is set only for the registered subset: resonator, POOL blocks 0-2, orientation false.
- **Seeds:** `derive_seed` is the registered byte-exact rule. I did not derive the real seeds.
- **Score:**
  - S = survivors − enemySurvivors on side 0;
  - D from the cross-team counters on side 0;
  - a timeout is t ≥ duration − dt/2 with both sides alive;
  - a controller failure is detected by status or count;
  - malformed or non-finite summaries are rejected.
- **t bounds:** my independent check against SciPy, `t.ppf`, matched all four quantiles in use to 9 decimals:
  - (1/400, df 99) 2.871307661;
  - (1/2400, 99) 3.447052261;
  - (1/400, 31) 3.022117834;
  - (1/1200, 31) 3.443507241.

  Zero SD gives bounds equal to the mean; comparisons are strict.
- **Verdicts:**
  - Each P1 level is tested against 0 at 1/400 support and 1/2400 refutation. The joint verdict is SUPPORTED only if both levels pass, and REFUTED if either is refuted.
  - P2 and P3 use block means of key-joined differences against δ, at 1/400 and 1/1200.
  - Any invalid or missing required fight makes that endpoint `not_run` / INDETERMINATE with its failures listed. Endpoints are independent.
- **Tests:** I ran `test_s6_run.py` once: **177 passed** in 15.5 s.

## Not checked

- The native batching and timeout code path was not exercised against the real engine; no real fight is allowed before authorization.
- The gate and latch code was read in the tests, not traced line by line.

## Remaining gates (unchanged)

The owner approves δ = 4.0 and n (100 per level, 32 blocks), and writes the authorization naming the specification's sha256. Only then may `s6_run.py` run, once.
