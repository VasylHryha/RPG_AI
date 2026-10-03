# Change-cost test (Stage 0c) — specification (committed before the recorded run)

Status: SPECIFICATION. Exploratory demo under the AGENTS pilot rule (own entropy, scratch code outside `geomind/`, everything committed here). Not a
milestone, not C6 evidence; it changes no status, accepted file or threshold. Motivation: `MOTIVATION.md`. It builds on Stage 0 (`SPECIFICATION.md`,
`REPORT.md`), whose sandbox, teacher, pieces and training settings it reuses unchanged.

## 1. Question

When a rule changes, how much new data does each design need to follow the new rule? The wired unit (AIM + MOVE) retrains **only AIM** and reuses MOVE
as it is; the one big controller must relearn everything. This tests the "quick to change" hypothesis directly.

## 2. The change

The targeting doctrine changes from the Stage 0 rule (weak, in-range and near enemies first) to **threat first**: score = 4.0 x enemy damage / 10 + 0.1 x
missing health (the in-range and distance terms are dropped). The stepping rule is unchanged. The doctrine was chosen on its own development entropy by a
rule fixed in advance (`dev_doctrine.py`, `dev_doctrine.json`): the weakest change, among candidates whose tied-best set contains the old doctrine's choice
on at most 70% of multi-enemy states, that still plays sensibly (average win score against rush and the kiter within 0.08 of the old doctrine's and at least
0.15 above rush). The chosen candidate contains the old doctrine's choice on 67.7% of those states and scores 0.605 against 0.620 for the old doctrine (rush
0.370). It plays about as well as the old doctrine, so closed-loop win rate cannot measure the change; what the change asks for is that a controller **makes the
new doctrine's decisions**. Win score is reported only as a sanity check.

**Ties.** A doctrine of damage and health gives exact ties between same-type enemies at full health: 28.8% of multi-enemy states. A tie-free variant ("back line
first") changed 64% of decisions but played 0.116 worse, so it was not eligible; adding a nearest-first tie-break would make the new doctrine agree with the old one
on 75% of decisions, too small a change. So ties are kept and handled in the measure: **agreement counts any enemy tied for the new teacher's best score**, and the
step is judged against the new rule's step toward the enemy the controller itself chose. The wired unit's shared scorer cannot see an enemy's slot, while the big
controller has one output per slot and could learn a slot-order bias; counting any tied-best choice removes that edge.

## 3. Controllers and fine-tuning

Per seed (20 seeds) the controllers are taught first exactly as in Stage 0 (AIM and MOVE, 16 hidden units, 3,000 + 3,000 rows, 4,000 steps; the equal-size
big controller, 15 hidden units, 6,000 rows, 8,000 steps; the large big controller, 60 hidden units, 96,000 rows, 32,000 steps), on the old doctrine. Then, for
each number of new rows n in {100, 300, 1000, 3000}, drawn from the same training pool and labelled by the new doctrine:

- **Wired unit:** a copy of AIM is fine-tuned on n one-enemy rows; MOVE is the same object as before (not retrained).
- **Big controllers (equal size and large):** a copy is fine-tuned on n full-decision rows (all labels under the new doctrine: the enemy scores and the step).

The same fine-tuning schedule for every model: 60 epochs over the n rows (steps = 60 n / batch, at least 200 and at most 2,000), batch min(64, n), learning rate
0.002, original input and output scaling kept (the new scores lie several standard deviations from the old output mean, which costs both designs some steps; this is
not neutral in size but is the same for both). Rows are counted as labelled decisions; a big-controller row carries more labels than an AIM row, which is conservative
for the wired unit. The large big controller trained on 96,000 of the pool's roughly 117,000 states, so its fine-tuning rows overlap its old training rows; that is
descriptive only. Both big controllers share fine-tuning row draws and batch order by construction. Final training error is recorded for every fine-tuned model.

## 4. Measurement

On the states of 60 held-out episodes labelled by the new doctrine, **restricted to states with more than one living enemy** (single-enemy states agree trivially;
this is also the population C1 uses): tie-aware target agreement, and the median angle between the controller's step and the new rule's step toward the controller's
own chosen enemy (for the wired unit, MOVE applied to the target AIM chose, end to end). Each design is judged against **its own quality before the change**,
measured the same way against the old doctrine on the same held-out states: a design has followed the new doctrine when its agreement is back within 0.02 of its own
pre-change agreement and its step angle is within 3 degrees above its own pre-change step angle. This makes the bar a measure of change cost, not of how good the
design was to begin with: the equal-size big controller agreed with the old doctrine on only 0.854 of decisions in Stage 0, so an absolute 0.95 bar would measure
baseline capacity. The number of rows needed is, per seed, the smallest n in the grid at which a design has followed the new doctrine (infinite if never in the grid).
The absolute bars (0.95 and 10 degrees) are reported alongside. Closed-loop win scores against rush and the kiter (40 episodes per cell, the same episodes for every
controller, seen mixes) are a sanity check. Build seconds, rows, parameters and the tie share are reported, never scored.

## 5. Predictions (stated before the recorded run; each can fail)

Verdict words: SUPPORTED if the median and at least 75% of seeds meet the bar; REFUTED if the median misses by the stated margin; INDETERMINATE otherwise.

- C1 (the change is real): the old doctrine's choice is among the new doctrine's tied-best on at most 0.70 of multi-enemy held-out states, and the unchanged wired unit's
  tie-aware agreement with the new doctrine is at most 0.75 (so there is something to learn). REFUTED if the old choice is tied-best on more than 0.85.
- C2 (cheap change for the wired unit): with 300 new rows the wired unit has followed the new doctrine (agreement back within 0.02 of its own pre-change value and the
  step bar), in at least 75% of seeds, with the median agreement within 0.02 of its pre-change median. REFUTED if its median agreement with 3,000 rows is still more than
  0.10 below its pre-change median. **Gated on C1 in both directions:** INDETERMINATE unless C1 is SUPPORTED.
- C3 (cheaper than retraining the big controller): the median rows needed by the equal-size big controller is at least 3 times the wired unit's (infinite counts, and
  the bar is its own pre-change quality) and C2 holds -> SUPPORTED; REFUTED if the equal-size big controller needs no more rows than the wired unit; INDETERMINATE
  otherwise or if C2 does not hold.

Descriptive, no verdict: rows needed by the large big controller; agreement and step angle by number of rows for all three; the share of seeds meeting the absolute bars;
each design's own pre-change quality; win score minus the new teacher's by rows and before the change; final training error, fine-tuning steps and build seconds by rows.

Reading, as written: C2 and C3 SUPPORTED means that, in this sandbox, a rule change in one piece costs far fewer examples than relearning a single block, because the other
piece is reused unchanged. C3 REFUTED means a single block of the same size adapts as cheaply here. **Caveat on the design:** only AIM's job changes, and the wired unit is told to
retrain only AIM, so part of C2 and C3 restates how the design is built; what is measured is how little data that one retraining needs against a block that must relearn two
outputs together. It remains one sandbox with scripted teachers and an imitation measure of the change, and the unseen-type result of Stage 0 (indeterminate) is not revisited.
A change that touches only MOVE, or both pieces, is a natural follow-up. Nothing here tests oscillators or "vibration".

## 6. Rules of the run

Own entropy (SPEC_CHANGE.json, generated once; its config copy is refreshed from the code before the commit and a test checks they agree; a second test checks the Stage 0
settings it reuses against SPEC.json). Seeds run in parallel (8 workers), numpy only. The run refuses to start unless the files listed in `change.py` are committed and
clean; creating the exclusive `run_change/` directory is the one-shot latch; every post-latch failure is recorded in `run_change/SUMMARY.json`; a failed seed is recorded
and never replaced, and INCOMPLETE takes precedence over any verdict. Soft stop at 45 minutes, independent watchdog at 50. Expected duration about 3 minutes (a
full-size seed was timed at 46 s, 0.28 GB, on a scratch entropy). No retry, no seed replacement, no change of any bar, size or rule after a recorded result.

## 7. Normalization ledger

| Quantity | Normalization |
|---|---|
| Features, health, time, win score | as in Stage 0 (`SPECIFICATION.md` section 7) |
| Rows | labelled decisions: one-enemy rows for AIM, full-decision rows for a big controller |
| Agreement | share of multi-enemy held-out states where the controller's chosen enemy is tied for the new teacher's best score |
| Step angle | median angle between the controller's step and the new rule's step toward the controller's own chosen enemy, over states where that step is non-zero |

## 8. Stop conditions (yes/no, one action, one role)

| Condition | Action | Role |
|---|---|---|
| Specification or code not committed, or not clean? | Refuse to run | Implementer |
| `run_change/` already exists? | Refuse; no resume, no retry | Implementer |
| A seed fails numerically or a pool is too small for the requested rows? | Record it missing, never replace it; INCOMPLETE | Implementer |
| Soft cap reached? | Stop, record INCOMPLETE | Implementer |
| Result tempts a retune of a bar, schedule or rule, or a rerun on new seeds? | Do not; return to the owner | Implementer |

## 9. Drafter self-audit

| Issue found | Cause | Fix |
|---|---|---|
| The planned "structure versus separate teaching" test cannot separate the two: separate parameters with their own labels make joint and separate training the same computation | I proposed it before working out what training mode could change | Replaced by the change-cost test, which does differ between designs (what must be retrained); recorded in `MOTIVATION.md` |
| Candidate doctrines were no stronger than the old one, so closed-loop win rate could not measure the change | I first planned to judge by win rate | The measure is agreement with the new doctrine (what a designer asks for); win score is a sanity check only |
| The first doctrine candidate agreed with the old one on 84% of decisions, too small a change | Chosen before looking at decisions | A rule picks the weakest change that differs on at least 30%; candidates and agreements are recorded |
| A test assertion accepted any verdict | Written loosely | Replaced by the specific gated answer |
| Independent review: exact ties under the new doctrine (28.8% of multi-enemy states) cap a slot-blind scorer's agreement and favour a slot-aware big controller | The doctrine uses damage and health only, and same-type enemies are common | Tie-aware agreement and a step judged toward the chosen enemy; the tie share is reported; the doctrine record uses the same measure |
| Independent review: an absolute 0.95 bar the equal-size big controller never reached even before the change would make "infinite rows" mean baseline capacity | I set the bar before looking at the big controller's old quality (0.854 in Stage 0) | Each design is judged against its own pre-change quality; the absolute bars are reported alongside |
| Independent review: a fixed 1,000 steps confounded the number of rows with the amount of training; final losses were not logged | A single schedule for all n | Steps scale with n (60 epochs, floored and capped), the same for every design; final training error recorded |
| Independent review: C2 could read REFUTED when the change was not real; agreement over single-enemy states inflated it | Gating written one way; population not matched to C1 | C2 is INDETERMINATE unless C1 holds; agreement is on multi-enemy states only |
