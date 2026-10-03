# Change-cost test, revision 2 (Stage 0c-r2) — results (exploratory; NOT a milestone, NOT C6 evidence)

Status: COMPLETE. One execution after the specification commit `3381e03`. 20 of 20 seeds, no errors, no retry, 352 s wall, 1,799 s CPU (8 workers), peak 0.33 GB per worker. No milestone status,
accepted file, threshold or historical record was changed. Raw per-seed results and the accounting are in `run_change2/` (`SUMMARY.json` is the record). No post-hoc analysis was done on this run.

## What was tested

The targeting doctrine changes ("threat first"). The wired unit retrains **only its AIM piece** from scratch on n new labelled rows and reuses MOVE untouched; one big controller (equal size, 770 parameters,
and a large one, 5,765) retrains whole from scratch on the same n rows. How many new rows does each need to follow the new rule? Two views, which had to agree: each design against its own quality before the
change (chance-corrected, with the step judged against the best-matching tied-best enemy), and every design against one common level (raw agreement 0.80).

## Verdicts (the rules in SPECIFICATION_CHANGE2.md, applied as written)

| Prediction | Result (median over 20 seeds) | Verdict |
|---|---|---|
| C1 the change is real | the old doctrine's choice is tied-best under the new one on **0.699** of multi-enemy states (bar: at most 0.70; a margin of 0.001, and only 55% of seeds are at or below 0.70); the unchanged wired unit agrees with the new doctrine on 0.699 (bar 0.75) | SUPPORTED (marginal) |
| C2 cheap change for the wired unit | with 1,000 new rows: chance-corrected agreement 0.967 against its own 0.964 before the change; raw 0.984; 95% of seeds recovered (bar 75%) | SUPPORTED |
| C3 cheaper than retraining the big controller | relative view: the wired unit by 1,000 rows, the equal-size big controller never within 12,000 (75% of seeds never; the large one in no seed); common-level view (0.80): the wired unit by 100 rows, the big controllers by 1,000; both views agree | SUPPORTED |

## What the data show (descriptive)

| Median over seeds, raw tie-aware agreement with the new doctrine | 100 rows | 300 | 1,000 | 3,000 | 6,000 | 12,000 |
|---|---|---|---|---|---|---|
| Wired unit (AIM retrained, MOVE reused) | 0.930 | 0.930 | 0.984 | 0.998 | 0.999 | 1.000 |
| Equal-size big controller (retrained whole) | 0.731 | 0.764 | 0.801 | 0.815 | 0.839 | 0.833 |
| Large big controller (retrained whole) | 0.742 | 0.775 | 0.799 | 0.821 | 0.856 | 0.875 |

- **Rows to reach an absolute level (half of seeds):** 0.80: wired 100, big controllers 1,000. 0.90: wired 100, big controllers never within 12,000. 0.95: wired 1,000, big controllers never.
- **The reused MOVE kept the step correct:** the wired unit's step angle was about 2.3 degrees at every n (1.4 before the change); the big controllers' step angle was 29 degrees at 100 rows and 11 to 13 degrees at
  12,000 (10.6 and 5.7 before the change).
- **Closed-loop play (sanity only):** win score minus the new expert's: wired unit -0.013 before the change, -0.06 to -0.09 after retraining; equal-size big controller -0.216 before, -0.30 to -0.49 after (below the
  rush rule's -0.212 at most row counts).
- **Fine-tuning from the old weights (the first revision's protocol, secondary):** no design recovered in any seed; the AIM piece fine-tuned reached only 0.83 to 0.88 raw agreement while the same piece retrained
  from scratch reaches 0.93 to 1.00. Reusing the old AIM weights hurt; reusing MOVE helped.
- Build time was not a differentiator: retraining AIM took 0.4 to 2.9 s and a big controller 0.1 to 6.0 s (rows 100 to 12,000).
- Tie share under the new doctrine 28.2% of multi-enemy states; chance agreement 0.363 (old doctrine) and 0.495 (new).

## Reading

**In this sandbox, when one rule changes, retraining only the affected piece needs roughly ten times fewer new examples than retraining a single block of the same size** (about 100 rows against about 1,000 for a common
quality level, and the block does not reach 0.90 agreement within 12,000 rows), the unchanged piece keeps its behaviour exactly (step angle 2 degrees), and play degrades less. Together with Stage 0, this supports
the engineering half of the owner's hypothesis: small pieces are quick to build and quick to change.

## Caveats (stated plainly)

- **C1 is marginal.** The old rule's pick is among the new rule's tied-best on 69.9% of decisions, 0.1 point inside the bar. The change is modest (about 30% of decisions differ), and the C1 share of seeds at or below
  0.70 was 55%. The verdict follows the pre-registered median rule.
- **Part of this restates the design.** Only AIM's job changed and the wired unit was told to retrain only AIM. What is measured is how little data that retraining needs against a block that must relearn two outputs together.
- **The block's "never recovers" is partly a limit of the block on this doctrine, not only change cost:** retrained from scratch on 12,000 rows it reaches 0.68 chance-corrected agreement, below the 0.76 it had on the old
  doctrine with 6,000 rows, so the new rule is harder for the block to learn than the old one. The common-level view (finite numbers, 100 against 1,000 rows) agrees, which is why C3 required both views.
- **Row accounting is conservative for the wired unit:** a big-controller row carries more labels (all scores and the step) than an AIM row (one enemy).
- One invented sandbox; scripted teachers; ordinary small networks inside the pieces; an imitation measure of the change; independent units (no squad coordination); a change in one piece only.
- Nothing here tests oscillators, "vibration" or the RRG physics.

## Process notes

The first revision (`REPORT_CHANGE.md`) was inconclusive and is kept unchanged, with an amendment correcting my wrong explanation. This revision was reviewed independently before its run; the review changed the step metric,
added the common-level view, chance correction and the grid-value summary, and fixed the schedule (all recorded in the specification's self-audit). A development learnability record on separate entropy preceded the run.

## Natural next steps

(1) A change that touches only MOVE, or both pieces, to check the result is not specific to AIM. (2) The squad level: units as pieces under a focus piece, the second level of composition (so far only pieces into a unit
have been tested). (3) Stage 1 (goal memory), Stage 2 (enemy memory) and Stage 3 (a map), each added with a situation that fails without it. (4) The real simulator after its repairs.
