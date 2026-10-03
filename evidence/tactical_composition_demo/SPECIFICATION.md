# Tactical composition demo, Stage 0 — specification (committed before the recorded run)

Status: SPECIFICATION. Exploratory demo under the AGENTS pilot rule (own entropy, scratch code outside `geomind/`, everything committed here).
Not a milestone, not C6 evidence; it changes no status, accepted file or threshold. Owner direction: "it's up to you", so scope and
bars below are the drafter's decision, recorded with their reasons.

## 1. Scope: what is enough for one unit

A unit is given its own stats and what it sees. Those are inputs, not pieces: its health fraction, speed, range, damage, preferred range,
whether its attack is ready; and for each of the three enemy slots: alive, position relative to the unit, distance, health fraction,
the enemy's range and damage. Stage 0 has **two pieces**, the smallest set that lets one unit work on an open field with full vision:

| Piece | Job | Takes | Gives | Teacher (scripted rule) |
|---|---|---|---|---|
| AIM | which enemy to hit | one enemy's features (relative position and distance over 20, health fraction, enemy range over 6, enemy damage over 10, own range over 6) | a score; the highest score among the living enemies is the target (one scorer shared by all enemies) | weak, in-range and near enemies first: (1 - health) + 0.6 x in range - 0.08 x distance |
| MOVE | where to step | the vector to the chosen target over 10 and the preferred range over 5 | a move direction | close in beyond the preferred range + 0.3; back off (ranged units only) inside it - 0.5; otherwise hold |

Unit controller = AIM feeds MOVE; wired, no joint training. The mage's burst (ABILITY piece), enemy MEMORY, GOAL memory and MAP are later
stages (0b, 2, 1, 3), each added only with a scenario that fails without it. Stage 0 was narrowed to AIM + MOVE after the development
calibration (section 8): the burst decision was too rare to teach fairly and needed a data design of its own.

## 2. The world (our own sandbox, `tactics.py`)

A 20 x 20 open arena, three units per side, simultaneous resolution, at most 300 ticks, deterministic given a seed. A unit moves up to its
speed per tick, attacks one chosen enemy in range when its attack is ready, and its health never rises. A win scores 1, a draw or timeout
0.5, a loss 0. Four unit types (all stats invented and fixed): fighter (health 100, speed 0.30, range 1.5, damage 9, cooldown 4,
preferred range 1.2), archer (60, 0.30, 6.0, 7, 4, 5.0), mage (50, 0.25, 4.0, 5, 4, 3.5; its burst is switched off in Stage 0) and
skirmisher (70, 0.45, 3.5, 6, 3, 3.0), which is **never used in training**. Seen team mixes: seven combinations of fighter, archer and at
most one mage. Unseen mixes: five combinations that contain a skirmisher. Opponent teams are drawn from the seen mixes.

Scripted opponents: **rush** (nearest enemy, walk straight at it, never backs off) and **kiter** (focus the weakest, keep the preferred range).
Baselines: the **teacher** (the full scripted unit controller of section 1) and **rush**. Our three units each act independently with the same
controller; there is no squad coordination in Stage 0.

## 3. Teaching and the comparison

Training states come from play: 600 episodes where the teacher acts with 30% random actions, against the two opponents, on the seen mixes,
each state labelled with the teacher's answers. AIM is taught 3,000 one-enemy rows and MOVE 3,000 one-decision rows (their own jobs); both
are ordinary small networks (two hidden layers of 16, tanh, Adam, 4,000 steps, batch 128, learning rate 0.003; 787 parameters in total).
The **one big controller** is a single network from the whole unit observation (29 inputs) to the move direction and the three enemy scores,
taught on the same teacher's decisions: 6,000 full-decision rows (the pieces' rows summed), 15 hidden units (770 parameters, equal size),
8,000 steps. Scaled rows for it: 24,000 rows, 30 hidden units (1,985 parameters), 16,000 steps; and 96,000 rows, 60 hidden units (5,765
parameters), 32,000 steps. The big controller therefore sees at least as many distinct states as the pieces do; each row carries all its
labels; it is not handicapped.

## 4. Measurement

Per seed (20 seeds, independent): fidelity of each piece, and of each big controller, to the teacher on the states of 60 held-out episodes; and
win score (mean over episodes) against each opponent on the seen mixes and on the unseen (skirmisher) mixes, 60 episodes per cell, for the
teacher, rush, the composed unit controller and the three big controllers. **Every controller plays the same episodes** (same team mixes and start
positions; no policy uses the random stream), so differences are paired. A cell score is the mean over the two opponents. Row counts are
asserted and recorded (a pool smaller than the requested rows is an error, never a silent truncation). Build cost (wall-clock to teach the
pieces and each big controller, rows and parameters) is reported, never scored.

## 5. Predictions (stated before the recorded run; each can fail)

Verdict words: SUPPORTED if the median and at least 75% of seeds meet the bar; REFUTED if the median misses by the stated margin;
INDETERMINATE otherwise. All comparisons between controllers are **paired per seed** (the difference is taken within a seed, then the
median and the share of seeds are read). Every claim has the rush floor: it must beat the "rush the nearest" rule by 0.15, or it proves nothing.

- P1 (pieces learn): AIM top-1 agreement with the teacher >= 0.95 (floor: the nearest-enemy rule agrees about 0.85 to 0.89), MOVE median
  angle error <= 10 degrees, MOVE hold agreement >= 0.90, and, where the teacher backs off, the median angle on back-off states alone <= 20 degrees
  (the overall median cannot see a missing back-off). REFUTED if median AIM top-1 < 0.90 or median angle > 20 degrees.
- P2 (the composed unit plays): composed minus teacher >= -0.10 AND composed minus rush >= 0.15 (seen mixes). REFUTED if the median of
  composed minus rush is below 0.05 or composed minus teacher is below -0.20.
- P3 (composition beats one big controller at equal size and rows): composed minus the equal-budget big controller >= 0.10 on the seen mixes
  AND on the unseen type mixes (median and 75% of seeds), P2 holds, **and the baseline is adequate**: the largest big controller (96,000 rows,
  5,765 parameters) beats rush by at least 0.15 on the seen mixes (otherwise a poor result for the big controller could be under-fitting, not
  architecture, and P3 and P4 are INDETERMINATE). REFUTED if the median seen gap is under 0.03.
- P4 (data to match): REFUTED if the equal-budget big controller is within 0.03 of, or above, the composed score (median of the paired
  difference). INDETERMINATE if P2 does not hold, the baseline is not adequate, or **any** scaled big controller (24,000 or 96,000 rows,
  larger networks) matches. SUPPORTED only if none matches and P2 holds and the baseline is adequate.
- P5 (a new unit type without retraining): on the unseen mixes composed minus teacher >= -0.15 AND composed minus rush >= 0.15 (median and
  75% of seeds). REFUTED if the median of composed minus rush is below 0.05.

Descriptive, no verdict: scores by opponent for every controller on both mix sets, each big controller's fidelity to the teacher on the held-out
states, build seconds, actual rows and parameters.

Reading, as written: P2 and P3 SUPPORTED means the wired unit controller (a weight-shared target scorer, a target-conditioned step, designer-chosen
inputs) plays at least as well as one big controller of the same size and rows on this task. That is a statement about this wired *structure*; it
does not by itself show that separate teaching is what matters, because the pieces also carry structure the big controller must learn. P3 REFUTED
means one big controller does as well and the wiring adds nothing here. Either result is reported as it is. It is one sandbox with scripted
teachers, so it tests whether pieces learn and compose known skills, not whether tactics are discovered. The unseen type changes only the
combination of inputs, not any single input's range, so P5 shows interpolation to a new combination, not extrapolation. This stage tests no
"vibration" or oscillator claim.

## 6. Rules of the run

Own entropy (SPEC.json, generated once; the config copy is refreshed from the code before the specification commit and a test checks they
agree). Seeds run in parallel (8 workers, spawn), numpy only. The implementer runs the mechanics tests before the commit; the run records
file hashes. The run refuses to start unless PROPOSAL.md, SPECIFICATION.md, SPEC.json, demo.py, tactics.py and both test files are committed
and clean; creating the exclusive `run/` directory is the one-shot latch; every post-latch failure is recorded in `run/SUMMARY.json`. A failed
seed is recorded and never replaced; INCOMPLETE takes precedence over any verdict. Soft stop at 45 minutes (no new seeds, workers
terminated), independent watchdog at 50 minutes. Expected duration 3 to 6 minutes (one full-size seed measured at 45 s, 0.22 GB, on a scratch
entropy). No retry, no seed replacement, no change of any bar, size or rule after a recorded result.

## 7. Normalization ledger

| Quantity | Normalization |
|---|---|
| Positions and ranges | relative to the acting unit, divided by the scales in section 1 |
| Health | fraction of the unit's maximum |
| Time | ticks; cooldowns and the 300-tick horizon fixed |
| Win score | mean over fresh episodes of 1 / 0.5 / 0 |
| Budget | rows and parameters counted for the pieces together and for the one big controller |

## 8. Development record and corrections (all before the recorded run; own development entropy each time)

1. First calibration (design with the mage's burst piece): the burst fired in 1.1% of mage states; the ABILITY piece had no job. Adjustment
   allowed once: blast radius 2 -> 3, range 4.5 -> 5. Second calibration: still 2.0%. Files: `history_ability_attempt/`.
2. My rule C ("burst fires in 10-60% of mage states") was mis-specified: the burst has a 15-tick cooldown, so at most 1 in 15 decisions can fire.
   Restricting to ready-mage states gave 3.9%; a finisher clause (also burst on a nearly dead target) was measured on the task alone at 12.2%
   and adopted. Third calibration: the rate was 6.5% in its pool and the ABILITY piece reached only 0.70 to 0.81 balanced accuracy at 3,000 rows;
   rush against rush read 0.605 on a symmetry band I had made too tight for 100 episodes.
3. Decision (drafter's, recorded): narrow Stage 0 to AIM + MOVE and defer ABILITY to Stage 0b with its own data design; replace the "two mages"
   unseen condition (meaningless for per-unit controllers) by a new unit type, the skirmisher, never seen in training; power the symmetry check with
   500 episodes. The code for the burst stays, switched off (`USE_BURST = False`).
4. The independent review found that the first unseen type (a skirmisher with speed 0.45) differed in an input the pieces never see and that lay
   outside the trained range, so any gap on it could be extrapolation on an irrelevant input. It was replaced by a never-seen combination of in-range
   inputs; that version (hp 70, cooldown 3) proved overpowered at calibration (teacher 0.98 against rush, rush against rush 0.77, no headroom), and
   became an archer's stats with a short preferred range. A seen-mix gap check also missed by 0.011 with the task unchanged because 100-episode cells
   are too noisy for a 0.20 margin; gap checks now use 300 episodes. All earlier calibration files are kept in `history_ability_attempt/`.
5. Final calibration for this design (`dev_calibration.json`): all task checks passed (teacher 0.768 against rush and 0.52 against the kiter; rush
   0.494 against rush and 0.278 against the kiter; random 0.01; on the unseen mixes teacher 0.92 and 0.757, rush 0.617 and 0.497); every piece size
   in the grid met the rule and the smallest, 16, was taken (AIM top-1 0.981 against a 0.853 floor, MOVE median angle 1.3 degrees, back-off angle 1.6
   degrees, hold agreement 0.99). The big controller's size was set by equal parameter count (15 hidden units).
6. Task and sizes were calibrated on their own entropy and never on a composed or big-controller result, so nothing about the comparison
   influenced them. Several calibration passes were needed because several of my rules were wrong, not because of any model result.

## 9. Stop conditions (yes/no, one action, one role)

| Condition | Action | Role |
|---|---|---|
| Specification or code not committed, or not clean? | Refuse to run | Implementer |
| `run/` already exists? | Refuse; no resume, no retry | Implementer |
| A seed fails numerically or the pool breaks? | Record it missing, never replace it; INCOMPLETE | Implementer |
| Soft cap reached? | Stop, record INCOMPLETE | Implementer |
| Result tempts a retune of a bar, size or rule, or a rerun on new seeds? | Do not; return to the owner | Implementer |

## 10. Drafter self-audit

| Issue found | Cause | Fix |
|---|---|---|
| ABILITY piece had no job (burst too rare); rule C impossible under the cooldown; symmetry band too tight | My rules were set before measuring the task | Section 8: restricted domain, finisher rule, then a recorded scope decision to Stage 0 = AIM + MOVE |
| "Two mages" as the unseen condition tests nothing for per-unit controllers | The unit is controlled one at a time, so team mix barely matters to it | A new unit type, never trained on |
| Fidelity measures that could be hollow (a model that never fires scores high accuracy; "median angle" from a median cosine) | Written quickly | Balanced accuracy for rare events (Stage 0b), true median angle, a nearest-enemy floor for AIM |
| Independent review: P4 ignored the largest big controller | Wrote the rule for two scales and the code read two entries | SUPPORTED needs that no scaled controller matches; tested for the largest-only case |
| Independent review: the unseen type's gap could come from extrapolation on speed (an input only the big controller sees) | The new type differed in an unused, out-of-range input | A never-seen combination of in-range inputs; checked by a test |
| Independent review: the big controller had no diagnostics and no floor | Only closed-loop scores were recorded | Its fidelity to the teacher is recorded; an adequacy gate (largest one beats rush by 0.15) |
| Independent review: the MOVE angle bar could not see a missing back-off; row truncation was silent; P2/P5 compared medians of marginals; stale docstring | Written incrementally | Back-off gate; asserted and recorded rows; paired differences; docstring updated |
| Evaluation episodes were not paired across controllers | Each cell had its own random stream | One stream per (opponent, mix set) shared by all controllers; tested |
