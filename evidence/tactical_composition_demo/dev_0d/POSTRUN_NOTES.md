# Post-run notes for experiment 0d Part A (2026-10-04) — a development probe, NOT registered, affects no verdict

This is a NEW file; `dev_0d/README.md` and the other files hashed into `run_0d/RUN_STARTED.json` were not edited after the run.

## Why the probe exists

The 2026-10-04 recheck (owner request: "check if it is the best we can do") noticed in `tuned2.json` and `run_0d` that the tuned flat model F1 is small (hidden 8, 357 parameters) and flat from N = 1,000 to 9,000
(0.530, 0.544, 0.543) because the setting tuned at N = 3,000 was reused at the other Ns. It asked whether a flat model with more capacity, data and training would climb. This is a **post-result** check of the premise of V1 and
V4; the report said "no post-hoc analysis" before it was written and now says so in its "Post-run recheck" section.

## What was run

`probe_flat_capacity.py`: F1-type flat networks (squared-error step head, the registered label content and recipe except the settings below) on the development validation pools of seeds 5, 6 and 7 (development entropy),
hidden 64 and 128, lr 0.003, weight decay 1e-4, N in {3,000, 9,000, 27,000, 60,000} source states from the 400-episode development pool, 32,000 steps (64,000 at N of 27,000 and 60,000). Raw results:
`probe_flat_capacity_results.json` (24 fits, 97 s wall). No tuning per N, no search; one setting per capacity.

## Result (mean `a_joint` over the three seeds)

| hidden (parameters) | N = 3,000 | 9,000 | 27,000 | 60,000 |
|---|---|---|---|---|
| 64 (6,405) | 0.446 | 0.613 | 0.696 | 0.737 |
| 128 (20,997) | 0.486 | 0.585 | 0.706 | 0.735 |

Reference on the same development seeds (`gates_results.json`): registered tuned F1 0.541 at N = 3,000 (0.543 at 9,000 in the recorded run), C 0.957 at N = 3,000, S1 0.939.
Median step angle on moving states for hidden 64 falls from 13.8 to 5.7 degrees and back-off success rises from 0.18 to 0.54 as N grows.

## Reading and limits

- The flat family **does** climb with capacity, data and training; the plateau of the registered F1 is a property of its small, heavily regularized setting. The statement in `REPORT_0D.md` that the flat models gain little from data was corrected accordingly.
- Even so, at 60,000 states the flat models (0.735 to 0.737) are below C at 3,000 states (0.957): a data advantage of at least 20 times for this measure and this sandbox, and the gap at N = 9,000 is nearer 0.35 than 0.42 for a flat model tuned at that N. V1 and V3 keep their direction; their size against "flat networks" is not established.
- Three development seeds, no per-N tuning, no closed-loop play, no depth or architecture changes. It does not replace a registered experiment (recommended next: 0e, see `MOTIVATION.md`).
