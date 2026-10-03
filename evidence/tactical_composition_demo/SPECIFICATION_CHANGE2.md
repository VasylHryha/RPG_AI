# Change-cost test, revision 2 (Stage 0c-r2) — specification (committed before the recorded run)

Status: SPECIFICATION. Exploratory demo under the AGENTS pilot rule (own entropy, scratch code outside `geomind/`, everything committed here). Not a milestone, not C6 evidence; it changes
no status, accepted file or threshold. Motivation: `MOTIVATION.md`. It replaces the first revision (`SPECIFICATION_CHANGE.md`, `REPORT_CHANGE.md`, inconclusive, kept unchanged) and reuses
Stage 0's sandbox, teacher, pieces and training settings (`SPECIFICATION.md`).

## 1. Why a second revision, and what changed

The first revision could not measure change cost: no design recovered its own quality. I first blamed the new doctrine; a development check (`dev_learnability.json`) showed the doctrine is
**learnable** (an AIM piece trained from scratch on 3,000 rows reaches 0.998 tie-aware agreement, 0.979 at 1,000 rows, 0.939 at 300). The defect was the update procedure: fine-tuning from the old
weights (original output scaling kept) stalled at 0.84 to 0.89. Changes in this revision, all decided before the recorded run:

1. **Primary protocol: retrain from scratch on the new rows.** The wired unit retrains only AIM (MOVE untouched); each big controller retrains whole, from a fresh initialization, on the same number
   of new rows. Fine-tuning (the first revision's protocol) is a secondary comparison: relative-view rows needed and raw agreement by rows are reported; nothing more.
2. **A wider grid** {100, 300, 1000, 3000, 6000, 12000}, so the big controller, originally taught on 6,000 rows, is tested at its original data size and beyond.
3. **C1 is judged on the median only** (a borderline share of seeds, 70% against 75%, gated everything in the first revision).
4. **Two views for C3, both required to agree.** After an independent review (below): a *relative* view (each design against its own pre-change quality) and a *common-level* view (every design against
   the same absolute level that each of them reached before the change). The relative view alone sits on the equal-size big controller's plateau (about 0.83 raw), where "rows needed" is mostly noise.
5. **Chance-corrected agreement in the relative view.** Agreement under the old doctrine (no ties) and under the new doctrine (29% ties, which a tie-aware measure forgives) are not comparable raw; each is corrected
   by the tie-aware agreement of a uniformly random living pick, (agreement - chance) / (1 - chance).
6. **The step is judged against the best-matching tied-best enemy** (the new keys `step_tiebest_*`): a big controller's step head cannot know which of several tied enemies its own score head will pick, and
   the step label is the lowest-index tied enemy's. The wired unit's MOVE sees the target AIM chose and has no such penalty. Counting any tied-best enemy's step as correct removes the confound for both designs.
7. **"Rows needed" is a grid value, never interpolated:** the smallest grid value by which at least half of the seeds have recovered.
8. **The retraining schedule uses the batch actually used** so the effective epochs are what is stated (item 3 of section 2). A learnability rule with a development record (section 6).

Unchanged: the doctrine ("threat first": 4.0 x enemy damage / 10 + 0.1 x missing health), the tie-aware agreement, multi-enemy states only, the sandbox, the held-out evaluation and the paired closed-loop sanity check.

## 2. The change and the controllers

Per seed (20 seeds) the controllers are taught first exactly as in Stage 0 on the old doctrine (AIM and MOVE: 16 hidden units, 3,000 + 3,000 rows, 4,000 steps; the equal-size big controller: 15 hidden
units, 6,000 rows, 8,000 steps; the large big controller: 60 hidden units, 96,000 rows, 32,000 steps). Then, for each number of new rows n in the grid, drawn from the same training pool and labelled by the new doctrine:

- **Wired unit (primary):** a fresh AIM (16 hidden units) is trained on n one-enemy rows; MOVE is the same object as before.
- **Big controllers (primary):** a fresh equal-size (15 hidden units) and a fresh large (60 hidden units) controller are trained on n full-decision rows (all labels under the new doctrine).
- Retraining recipe, the same for every design: Stage 0's (Adam, learning rate 0.003, batch min(128, n)) with 170 epochs over the n rows at the batch actually used, at least 500 and at most 16,000 steps.
  Effective epochs: 500 at n = 100, 213 at n = 300, and 170 from n = 1,000 up (the cap never binds on the grid).
- **Secondary (fine-tuning):** copies of the old models fine-tuned on the same rows with the first revision's recipe (60 epochs, at least 200 and at most 2,000 steps, batch min(64, n), learning rate 0.002,
  original scaling kept).

Rows are counted as labelled decisions; a big-controller row carries more labels than an AIM row, which is conservative for the wired unit. The large big controller trained on 96,000 of the pool's roughly
117,000 states, so its retraining rows overlap its old training rows (descriptive only).

## 3. Measurement

On 60 held-out episodes' states with more than one living enemy: tie-aware target agreement with the new doctrine (any enemy tied for the new teacher's best score counts), its chance baseline and chance-corrected
value, and the median angle between the controller's step and the step toward the best-matching tied-best enemy (the wired unit: MOVE applied to AIM's target, end to end). Each design's **own quality before the
change** is measured the same way against the old doctrine on the same held-out states. A design has *followed the new doctrine* (relative view) when its chance-corrected agreement is back within 0.03 of its own
pre-change value and its step angle is within 3 degrees above its own pre-change step angle. In the *common-level view* it has followed it at the first grid value where its raw tie-aware agreement reaches 0.80;
that level is the highest of the listed absolute levels (0.80, 0.90, 0.95) at or below every design's own raw quality before the change (Stage 0 and the first revision: the equal-size big controller 0.83 to 0.85).
Per seed the rows needed are the smallest n in the grid at which it holds (infinite if never); the summary is the smallest grid value by which at least half the seeds have it (infinite if none).
Reported alongside: rows to reach the other absolute levels; the share of seeds meeting 0.95 agreement with a step angle of 10 degrees; the tie share and the chance baselines under both doctrines; closed-loop
win scores against rush and the kiter (40 episodes per cell, the same episodes for every controller, seen mixes, retraining protocol only); build seconds. The equal-size big controller plateaus near 0.84 even with
12,000 rows (development check), well below the wired unit; that is why the relative bar alone is not enough.

## 4. Predictions (stated before the recorded run; each can fail)

Verdict words: SUPPORTED if the median and at least 75% of seeds meet the bar (where the bar is stated for seeds); REFUTED if the median misses by the stated margin; INDETERMINATE otherwise.

- C1 (the change is real): the old doctrine's choice is among the new doctrine's tied-best on at most 0.70 of multi-enemy held-out states (median), and the unchanged wired unit's raw tie-aware agreement with the
  new doctrine is at most 0.75 (median). REFUTED if the old choice is tied-best on more than 0.85.
- C2 (cheap change for the wired unit): with **1,000 new rows** (a third of its original 3,000) the wired unit has followed the new doctrine (relative view) in at least 75% of seeds, with the median
  chance-corrected agreement within 0.03 of its pre-change median. REFUTED if its median chance-corrected agreement at 12,000 rows is still more than 0.15 below its pre-change median. Gated on C1: INDETERMINATE
  unless C1 is SUPPORTED.
- C3 (cheaper than retraining the big controller): in each view, the equal-size big controller's rows needed (half-of-seeds grid value) are at least 3 times the wired unit's (infinite counts) -> that view says
  SUPPORTED; at most the wired unit's -> REFUTED; otherwise INDETERMINATE. C3 is SUPPORTED or REFUTED only if **both views agree** and C2 holds; otherwise INDETERMINATE.

Descriptive, no verdict: everything listed in section 3, the large big controller's rows, and the fine-tuning results.

Reading, as written: C2 and C3 SUPPORTED means that, in this sandbox, a rule change in one piece costs far fewer new examples than retraining a single block of the same size, because the other piece is reused. C3 REFUTED
means the block adapts as cheaply here. **Caveats:** only AIM's job changes and the wired unit is told to retrain only AIM, so part of C2 and C3 restates how the design is built; the relative view compares each design
with its own earlier level (a weaker design is not penalised) and the common-level view compares them at one level; it is one sandbox with scripted teachers and an imitation measure of the change. A change that
touches only MOVE, or both pieces, is a natural follow-up. Nothing here tests oscillators or "vibration".

## 5. Rules of the run

Own entropy (SPEC_CHANGE2.json, generated once; its config copy is refreshed from the code before the commit; tests check that it agrees with the code, with Stage 0's settings in SPEC.json and with the learnability
record). Seeds run in parallel (8 workers), numpy only. The run refuses to start unless the files listed in `change2.py` (which include the specification, both spec files, the code, the tests and the development
records) are committed and clean; creating the exclusive `run_change2/` directory is the one-shot latch; every post-latch failure is recorded in `run_change2/SUMMARY.json`; a failed seed is recorded and never
replaced, and INCOMPLETE takes precedence over any verdict. Soft stop at 45 minutes, independent watchdog at 50. Expected duration 6 to 9 minutes (one full-size seed was timed at 90 s with the earlier
schedule; the 16,000-step cap adds some). No retry, no seed replacement, no change of any bar, recipe, grid or rule after a recorded result.

## 6. Development record

`dev_learnability.py` / `dev_learnability.json` (own entropy, second run; the first, agreement only, is kept in `history_ability_attempt/`): rule fixed in advance (AIM from scratch at 3,000 rows reaches median
tie-aware agreement 0.95); result 0.998 (learnable). The rule's number had been written in the first revision's report and a scratch look at 0.994 preceded the record; the margin makes this immaterial. Information
recorded (medians of 5 seeds): AIM from scratch, raw agreement 0.912 / 0.939 / 0.979 / 0.998 / 0.999 / 1.000 at 100 / 300 / 1,000 / 3,000 / 6,000 / 12,000 rows, step angle 2.2 to 2.5 degrees throughout;
the equal-size big controller from scratch 0.749 / 0.787 / 0.807 / 0.826 / 0.869 / 0.830, step angle 33.6 / 20.9 / 17.7 / 13.6 / 12.1 / 11.4 degrees; own quality before the change (chance-corrected): wired
0.966 with step 1.5 degrees, equal-size big 0.739 with step 10.7 degrees; fine-tuning an AIM at 3,000 rows 0.887. Seeing these numbers I changed no bar, recipe or grid. The doctrine and its selection record are
those of the first revision (`dev_doctrine.json`).

## 7. Normalization ledger

As in the first revision and Stage 0 (`SPECIFICATION.md` section 7; `SPECIFICATION_CHANGE.md` section 7). Rows: labelled decisions (one-enemy rows for AIM, full-decision rows for a big controller).
Chance-corrected agreement: (tie-aware agreement - chance) / (1 - chance), chance being the tie-aware agreement of a uniformly random living pick on the same multi-enemy states.

## 8. Stop conditions (yes/no, one action, one role)

| Condition | Action | Role |
|---|---|---|
| Specification or code not committed, or not clean? | Refuse to run | Implementer |
| `run_change2/` already exists? | Refuse; no resume, no retry | Implementer |
| A seed fails numerically or a pool is too small for the requested rows? | Record it missing, never replace it; INCOMPLETE | Implementer |
| Soft cap reached? | Stop, record INCOMPLETE | Implementer |
| Result tempts a retune of a bar, recipe or grid, or a rerun on new seeds? | Do not; return to the owner | Implementer |

## 9. Drafter self-audit

| Issue found | Cause | Fix |
|---|---|---|
| First revision: no design recovered; I blamed the doctrine, wrongly | I did not test what I asserted; the doctrine is learnable from scratch (0.998 at 3,000 rows) | Amendment to `REPORT_CHANGE.md`; learnability record; the update procedure was the defect |
| First revision used fine-tuning from old weights, which stalled | A recipe chosen without a development check of the update procedure | Retraining from scratch is primary; fine-tuning is secondary and reported |
| C1's 75% share rule gated everything and failed by chance (70%) | I applied a share rule to a property of the task, not of a design | C1 uses the median only |
| The grid stopped at 3,000 rows, below the big controller's original 6,000 | Grid chosen before comparing data sizes | Grid extended to 12,000 |
| Independent review: the step bar was confounded by ties (29% exact ties; a score head and a step head cannot coordinate on a tied slot), never measured in development | I fixed the step metric for the first revision and did not examine it for the second | Step judged against the best-matching tied-best enemy; development record includes it |
| Independent review: the relative bar sat on the big controller's plateau (a noisy crossing) and the 3x test was one grid step wide | Relative bars chosen to avoid measuring baseline capacity, without checking the plateau | Common-level view co-primary; both must agree; grid-value summary by half of seeds; the level chosen from pre-change quality, not from new numbers |
| Independent review: raw agreement before (no ties) and after (29% ties) the change is not comparable | The tie-aware measure forgives ties only under the new doctrine | Chance baselines under both doctrines; the relative view is chance-corrected |
| Independent review: the schedule's effective epochs differed from the stated 170 (fixed denominator 128 against batch min(128, n)) and the cap damped the top of the grid | Steps computed with the full batch size | Steps use the batch actually used; cap raised to 16,000; effective epochs stated |
| Independent review: a vacuous assertion; no boundary tests; the spec claimed fine-tuning gets all measures; FILES omitted `SPEC.json` and the doctrine record | Written quickly | Assertion fixed; boundary and tie-aware step tests added; spec corrected; FILES extended |
