# Tactical composition demo, Stage 0 — results (exploratory; NOT a milestone, NOT C6 evidence)

Status: COMPLETE. One execution after the specification commit `bc5ce29`. 20 of 20 seeds, no errors, no retry, 174 s wall, 1,012 s CPU
(8 workers), peak 0.29 GB per worker. No milestone status, accepted file, threshold or historical record was changed. Raw per-seed results and
the accounting are in `run/` (`SUMMARY.json` is the record).

## What was tested

One unit made of two small pieces, AIM (which enemy to hit) and MOVE (where to step), taught separately from a scripted expert and wired together,
against one big controller taught directly on the same expert's decisions (equal rows and equal size, then scaled up), on a 3-against-3 sandbox
with three seen unit types and one never-seen type. Win score: win 1, draw 0.5, loss 0, against two scripted opponents (rush and kiter).

## Verdicts (the rules in SPECIFICATION.md, applied as written)

| Prediction | Result (median over 20 seeds, paired) | Verdict |
|---|---|---|
| P1 pieces learn | AIM agrees with the expert 0.979 (nearest-enemy floor 0.862); MOVE median angle 1.4 degrees, hold agreement 0.985, back-off angle 1.6 degrees; all 20 seeds meet every bar | SUPPORTED |
| P2 composed unit plays | composed 0.631, expert 0.652, rush 0.375: composed minus expert -0.027, composed minus rush +0.250; 95% of seeds meet the bar | SUPPORTED |
| P3 composition beats one big controller (equal size and rows) | seen mixes: composed minus big +0.240; new unit type: +0.110 (quartiles 0.056 to 0.168, fewer than 75% of seeds reach +0.10) | INDETERMINATE (the unseen part fails the 75% rule) |
| P4 data needed to match | big controller: 0.388 (6,000 rows, 770 parameters), 0.535 (24,000 rows, 1,985 parameters), 0.581 (96,000 rows, 5,765 parameters); composed 0.631; none matches | SUPPORTED |
| P5 new unit type without retraining | composed 0.708, expert 0.827, rush 0.508: minus expert -0.121, minus rush +0.192; only 65% of seeds meet both bars | INDETERMINATE |

Baseline adequacy held: the largest big controller beat rush by 0.204 (needs 0.15), so the big controller is a real baseline, not an under-fit.

## Reading

- **Two small separately taught pieces, wired, play almost as well as the scripted expert** (0.631 against 0.652) and far better than the
  rush rule, from 787 parameters and 6,000 rows, built in about 1 second.
- **One big controller of the same size and rows is much weaker** (0.388). Its target choice is no better than "nearest enemy" (0.854 against the 0.862 floor).
  It needs 16 times the rows and 7.5 times the parameters to reach 0.581, and still trails the composed unit (0.631). It was still improving (0.388,
  0.535, 0.581), so it might catch up with more.
- **Where the advantage comes from.** The wired unit has structure the big controller must learn: one scorer shared by all enemies, a step that
  depends on the chosen target, and designer-chosen inputs. The results show that this *structure* is data-efficient here. They do not show that
  separate teaching is what matters.
- **A new unit type (an archer's stats with a short preferred range) is handled less cleanly.** The composed unit loses 0.12 to the expert (0.03 on seen
  types) and beats the equal-size big controller by 0.11, but not on every seed, and the larger big controllers reach or exceed the composed score on
  that type (scores on the new type: composed 0.696 averaged over opponents; big 4x 0.715; big 16x 0.750). The unseen type changes only the combination of
  inputs, so this is interpolation, and it is a weak test.

## What this does not show

One invented sandbox, scripted teachers and opponents, ordinary small networks inside the pieces, independent units with no squad coordination, and
only Stage 0 (no goal memory, no enemy memory, no map, no burst piece). The big controller is a plain network over fixed enemy slots; a big controller
with the same shared-scorer structure but trained end to end was not tested and might do as well. That is the natural follow-up to separate
"structure" from "separate teaching". Nothing here tests oscillators, "vibration" or the RRG physics. It is not a claim that this works for real
tactics or the real simulator.

## Build cost (descriptive)

Pieces: 1.0 s together. Big controllers: 1.2 s (equal), 3.4 s (24,000 rows), 10.2 s (96,000 rows). Rows: 3,000 + 3,000 for the pieces against 6,000, 24,000
and 96,000. Training pool about 117,000 states per seed (actual row counts asserted).

## Limits and the record

Task, sizes and the unseen type were calibrated on their own entropy and never on a composed or big-controller result; several of my own calibration
rules were wrong and corrected before the recorded run (listed in SPECIFICATION.md section 8 and the self-audit). The mage's burst piece was deferred to
Stage 0b. An independent review of the specification and code before the run produced seven fixes, all applied. No post-hoc analysis was done on this run.
