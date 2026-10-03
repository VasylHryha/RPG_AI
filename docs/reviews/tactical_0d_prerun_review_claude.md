# Pre-run review of experiment 0d Part A (same model family; author's summary of a subagent report)

Reviewer: a Claude subagent (same family as the author; **not** a cross-family review), read-only, ran the unit tests once. Reviewed commit `ad8a17b`. Recommendation: **FIX FIRST**. This file summarizes
the report and records what was done; the subagent's own text was returned in the session and is not stored verbatim.

| # | Finding (severity) | Disposition |
|---|---|---|
| 1 | The machine was heavily loaded by another project's jobs (load above 100 on 10 cores); the soft cap of 3,600 s against an expected 2,300 s could end the one-shot run INCOMPLETE (high) | Confirmed. Caps raised to 7,200 and 7,500 s; load average and CPU count now recorded in `RUN_STARTED.json`; the run started only when the one-minute load was about 17 |
| 2 | The cost run used code that differs from the registered code; no file hashes in that run (medium-high) | Listed what changed (`dev_0d/README.md`); seed 0 of the cost run re-runs identically (286 values) under the registered code (`dev_0d/COST_SEED_REPRODUCTION.json`) |
| 3 | V3 returned INDETERMINATE whenever V2 was discordant, the specification did not (medium) | Code aligned to the specification and the specification clarified; test added |
| 4 | V2 EQUIVALENT was borderline (development per-seed E2 0.008 to 0.029; 8-seed upper bound 0.027 against 0.03) (medium) | Stated in the specification self-audit; the recorded interval was [0.017, 0.022] |
| 5 | S1's joint training is weakly joint; the 12-times parameter gap (medium) | Stated in the specification and the report as the scope of V2 |
| 6 | Flat search limited; F1 and F2 at grid edges; V5 least robust (low-medium) | Stated; no fitting bug found |
| 7 | The promised teacher-forced equivalence test was missing (low) | Added (`test_zd.py`) |
| 8 | Stale proposal header; `step_tiebest` not computed; stream keys not saved (low) | Header fixed; both listed as not computed/derivable in the specification |

Checked clean by the reviewer: stream keys and the entropy-length rule, nesting of the source states, standardizers from training states only, seed pairing, paired win-score episodes, stratum margins (minimum 1,928 test states against 30), registration boundary.
