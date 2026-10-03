# Change-cost test (Stage 0c) — results (exploratory; NOT a milestone, NOT C6 evidence)

Status: COMPLETE, **all three verdicts INDETERMINATE**. One execution after the specification commit `d32485a`. 20 of 20 seeds, no errors, no retry, 170 s wall,
972 s CPU (8 workers), peak 0.32 GB per worker. No milestone status, accepted file, threshold or historical record was changed. Raw per-seed results and the accounting
are in `run_change/` (`SUMMARY.json` is the record). Nothing below re-analyses the run to change a verdict.

## Verdicts (the rules in SPECIFICATION_CHANGE.md, applied as written)

| Prediction | Result (median over 20 seeds) | Verdict |
|---|---|---|
| C1 the change is real | the old doctrine's choice is tied-best under the new one on 0.677 of multi-enemy states (median); the unchanged wired unit agrees with the new doctrine on 0.676; but only 70% of seeds meet the 0.70 bar (the rule needs 75%; upper quartile 0.701) | INDETERMINATE (a borderline share) |
| C2 cheap change for the wired unit | gated on C1, so INDETERMINATE by rule; for the record the wired unit's agreement with the new doctrine was 0.831 at 300 rows and 0.877 at 3,000 rows, against 0.978 before the change; no seed recovered at 300 rows | INDETERMINATE (gated) |
| C3 cheaper than retraining the big controller | gated on C2; rows needed: wired unit never within the grid, equal-size big controller recovered in 20% of seeds (3,000 rows), large one never | INDETERMINATE (gated) |

## What the data show (descriptive; not a verdict)

| Median over seeds | before the change (old doctrine) | 100 rows | 300 rows | 1,000 rows | 3,000 rows |
|---|---|---|---|---|---|
| Wired unit, agreement with the new doctrine | 0.978 own quality (0.676 against the new doctrine) | 0.838 | 0.831 | 0.842 | 0.877 |
| Equal-size big controller | 0.834 own quality (0.671) | 0.730 | 0.779 | 0.809 | 0.834 |
| Large big controller | 0.955 own quality | 0.777 | 0.804 | 0.811 | 0.827 |

- **No design recovered its own quality.** After fine-tuning the wired unit reached 0.88 agreement at best (own quality 0.98); the big controllers reached 0.83. The absolute bars
  (0.95 agreement, 10 degrees) were met in no seed by any design.
- **The reused MOVE piece kept the step correct.** The wired unit's step angle stayed at about 2 degrees after the change (1.4 before); the big controllers' step angle was
  15 to 26 degrees after the change (6 to 14 before), because their step head relies on a target choice that has shifted.
- **Imperfect imitation of the new doctrine made closed-loop play worse, not better.** Win score minus the new expert's: wired unit +0.009 before the change, about -0.14 to -0.15 after;
  equal-size big controller -0.206 before, -0.35 to -0.44 after (below the rush rule's -0.231).
- The wired unit's AIM fits its training rows (training error 0.19 at 100 rows, 0.036 at 3,000 rows in score units) but held-out agreement stays at 0.84 to 0.88.
- Tie share under the new doctrine: 29.9% of multi-enemy states (median), reported as the review required. The tie-aware measure was used for every design.

## Reading

**This run does not measure change cost.** Neither design learned the new doctrine well enough for "rows needed to recover" to mean anything. The most likely reason (an inference,
not tested here) is that my doctrine is badly conditioned for learning: its score is 4.0 x enemy damage plus only 0.1 x missing health, so choosing between two same-type
enemies depends on score differences of 0.01 to 0.1 against a scale of several units, and a small network trained on a few thousand rows rarely resolves that. The Stage 0 doctrine
had no such fine structure, which is why AIM learned it to 0.98.

**Design defect, recorded.** I checked in the development calibration that the new doctrine differs from the old one and plays sensibly, but I did not check that a piece can *learn* it
(the same kind of omission as the divide piece's capacity in the arithmetic demo and the rare burst in Stage 0 calibration). Per AGENTS, a design defect found after results are
recorded is withdrawn through a record and the next revision is registered on fresh seeds; this result stands unchanged. C1's 75% share rule was also borderline by chance
(0.70), which gated everything else.

## What is solid and what is not

- Solid (descriptive, from the recorded data): reusing a piece unchanged keeps its behavior intact (step angle 2 degrees), while fine-tuning a single block moves its step head away from correct.
- Not shown: that retraining one piece is cheaper than retraining the whole block. The run could not answer that, because the new doctrine was not learnable at these data sizes.
- The earlier Stage 0 findings are unaffected (`REPORT.md`).

## Next step (needs the owner's decision)

A second revision (Stage 0c-r2) on fresh entropy, with these changes decided in advance: (1) choose the changed doctrine among candidates by a rule that includes a **learnability
check** on its own development entropy (a piece trained on the new doctrine from scratch with 3,000 rows must reach at least 0.95 tie-aware agreement), in addition to the existing
checks; (2) keep the relative recovery bars, the tie-aware measure and the schedule; (3) keep C1's bar but state it on the median only, so a borderline share cannot gate the rest.
Candidate doctrines to be tried: ones whose score differences are not tiny between same-type enemies (for example threat first with a distance tie-break, a health-first rule, or a
combined rule), judged by the rule, not by this result.

## Amendment (2026-10-03, after the run; the recorded results above are unchanged)

A later development check on separate entropy (`dev_learnability.py`, below, and an earlier scratch look at the same candidates) found that the new doctrine **is** learnable: a piece trained from
scratch on 3,000 one-enemy rows reaches 0.994 tie-aware agreement with it. The "most likely reason" given above, that the doctrine is badly conditioned for learning, is therefore wrong. What the
recorded run did show is that **fine-tuning from the old weights** (60 epochs over the new rows, original output scaling kept, learning rate 0.002) stalled at 0.84 to 0.88 agreement, while training from
scratch on the same 3,000 rows reaches 0.99. So the defect is in the update procedure of this revision, not in the doctrine, and the first revision's inconclusive result stands as recorded.
Revision 2 uses retraining from scratch on the new rows as the primary protocol (the wired unit retrains only AIM, the big controller retrains whole) and keeps fine-tuning as a secondary, reported comparison.
