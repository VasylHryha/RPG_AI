# Experiment 0d — structure versus composition (DRAFT for owner approval; nothing is built or run)

Exploratory line under decision 0028; not a milestone, not C6 evidence. Drafted 2026-10-03 after the recheck (`CORRECTIONS.md`). **Before approval no project code runs**
(AGENTS.md). Code, if approved, goes in new files only (`tcd_common` plus `zd_*.py`), the recorded harnesses stay frozen.

## 1. What this must settle (from the recheck)

1. **Structure or composition?** The wired unit copies the teacher's computation graph (one scorer shared by every enemy, then a step conditioned on the chosen target); the baseline is a
   plain network over fixed enemy slots. Until a baseline with the same structure but trained jointly exists, "composition beats flat" may only mean "structure helps imitation".
2. **Is the change-cost advantage built in?** Only AIM changed and only AIM was retrained. The matching control (a flat or structured network with everything frozen except the head that changed)
   and a change that touches MOVE or both pieces are missing.
3. **Extrapolation, not interpolation.** The recorded "unseen" type sat inside the trained range and probed where a smooth net places the teacher's range threshold.
4. **A fair baseline.** The flat model got the composed recipe unchanged (one learning rate, no search, no weight decay).
5. **Evidence strength.** Verdicts rested on medians and 75%-of-seeds rules, one gate passed by 0.001, no intervals.

Not in scope: the squad level, learning from outcomes, a second sandbox or outside benchmark, geometry, oscillators, "vibration". They follow only if 0d says the pieces idea survives.

## 2. Design

**Task, teacher, opponents, seen mixes:** exactly as Stage 0 (`tactics.py`, `SPECIFICATION.md`): 3 against 3, teacher scores per enemy, argmax, step rule; opponents rush and kiter; training pool from the
teacher's play with 30% random actions. Data row budgets as Stage 0 (3,000 AIM rows plus 3,000 MOVE rows; 6,000 flat rows). Seeds: 30 (the recorded line used 20); an independent entropy in `SPEC_0D.json`.

**Part A, models (the ablation ladder; every one gets the same tuning budget, section 3):**

| Id | Model | Question it answers |
|---|---|---|
| F0 | flat network over fixed enemy slots, recorded recipe | reproduces the Stage 0 baseline |
| F1 | flat network, tuned (hidden size, learning rate, weight decay, steps; parameter count within 10% of the composed unit) | is the recorded baseline just under-tuned? |
| F2 | F1 with a discrete move head (hold or one of 8 directions, cross-entropy) instead of squared error on a multimodal step | does the step head's output form explain the flat model's loss? |
| S1 | structured end to end: one scorer shared by every enemy, softmax selection, a step head that reads the model's own selected enemy; one optimizer, one joint loss on the same rows as F1 | same graph as the composed unit, trained jointly: structure without separate teaching |
| S2 | S1 plus set context (the scorer also sees the mean over living enemies, DeepSets style) | does a standard permutation-aware design do better than the hand-built graph? |
| C | composed unit: AIM and MOVE taught separately and wired (the recorded design, same tuning budget) | the claim under test |
| L | large flat block, 96,000 rows (reference only) | how far data alone goes |

Parameter counts and rows are reported for every model, with the number of labels per row (a flat row carries three scores and a step; an AIM row one score).

**Endpoints (all paired within seed):**
- E1 = C minus the better of F1 and F2; E2 = C minus S1; E3 = S1 minus the better of F1 and F2 (each: seen mixes, win score averaged over the two opponents, and tie-aware chance-corrected agreement).
  Held-out fidelity is the primary measure (at least 2,000 multi-enemy states per seed); closed-loop win score uses 200 paired episodes per cell and is the second measure.
- Each endpoint is the median over 30 seeds of the paired difference with a 95% bootstrap interval (`tcd_common.stats.paired_median_ci`).

**Change-cost (Part B), three changes, each retrained from scratch on n new rows (n = 100, 300, 1,000, 3,000, 6,000, 12,000):**

| Change | Teacher | Wired unit retrains | Flat, structured retrain | Frozen-head control |
|---|---|---|---|---|
| B1 AIM only | doctrine 2 (as r2) | AIM | whole | F1 and S1 with everything frozen except the score head |
| B2 MOVE only | a new stepping rule (for example, ranged units keep a longer standoff band), same targeting | MOVE | whole | F1 and S1 with everything frozen except the step head |
| B3 both | doctrine 2 plus the new stepping rule | AIM and MOVE | whole | none (reported for completeness) |

Rows needed are reported in the relative view (back within a margin of the design's own pre-change quality) and in a common-level view (raw 0.80 and 0.90), using the repaired metrics
(`tcd_common.metrics`: multi-enemy states, hold-aware tie-best step). The unit of comparison is the share of seeds that have recovered at each n, not only the median, and the grid floor is lowered to 30 rows
so the wired unit's need is not truncated.

**Extrapolated unit type (Part C):** one type whose speed and range lie outside every trained value (trained speed 0.25–0.30, trained range 1.5–6.0; the new type has speed 0.45, range 8.0, preferred range 6.5)
and a third scripted opponent that none of the models saw. Zero-shot fidelity to the teacher and win score for F1, F2, S1, S2, C. The teacher must beat rush on this type with margin (section 3), or the type is dropped.

## 3. Development before the recorded run (own entropy, scratch code outside `geomind/`, committed with raw results and a README)

- **Tuning:** 12 random-search trials per model class on development entropy, scored on a development validation split; the chosen settings are written into `SPEC_0D.json` and frozen before the recorded run.
  The search space and trial budget are identical for F1, F2, S1, S2 and C's pieces.
- **Learnability gate (the lesson of three earlier failures):** each new thing must be learnable at its planned size by the design intended to learn it, on development entropy, before any bar is fixed:
  the new stepping rule by a wired MOVE piece (agreement 0.95 or step 5 degrees at 3,000 rows), the discrete head by F2, the structured nets by S1 and S2 (no divergence, loss falling), the extrapolated type
  by the teacher (it beats rush by at least 0.10).
- **Margins:** the equivalence margin for "same as" (E2) is fixed from the development spread of paired differences (not below 0.03) and the superiority margin for "better than" is twice that, both written before the recorded run.
- **Gradient check:** S1 and S2 are trained with hand-written backpropagation; a finite-difference test must pass before any run.

## 4. Pre-registered verdicts (words are exploratory vocabulary)

| Row | SUPPORTED | REFUTED | else |
|---|---|---|---|
| H-struct: the gap is structure | E3 above the superiority margin with lower interval bound above 0, and E2 inside the equivalence margin (interval inside ±margin) | E1 above the superiority margin with lower bound above 0, and E2 above the superiority margin with lower bound above 0 (separate teaching adds) | INDETERMINATE |
| H-base: the recorded baseline was under-tuned | E1 (tuned) smaller than the Stage 0 gap by more than the superiority margin | E1 within the margin of the Stage 0 gap | INDETERMINATE |
| H-change: the change-cost advantage is not specific to AIM or to a built-in freeze | for B1 and B2, the wired unit reaches the common level 0.90 with at least 3 times fewer rows than the better of the frozen-head control and the structured retrain, by the share-of-seeds rule at every grid value | wired needs as many rows as the frozen-head control in either change | INDETERMINATE |
| H-extrap: pieces cope with a truly new type | C within the equivalence margin of the teacher-relative win score of S2, and above F1 by the superiority margin | C below F1 | INDETERMINATE |

Every row is paired within seed; SUPPORTED requires the median and the interval bound to clear the bar, not the median alone. Nothing in this table was fixed after seeing a recorded result.

## 5. Normalization ledger

| Quantity | Level | Unit | Normalization |
|---|---|---|---|
| tie-aware agreement | decision (state), multi-enemy states only | share | chance-corrected by the uniform living pick; no cross-level use |
| step angle | decision | degrees | toward the chosen enemy and against the best-matching tied-best enemy; hold-aware |
| win score | episode | win 1, draw 0.5, loss 0 | teacher-relative (minus the teacher's own score on the same cell) |
| rows | decision | labelled rows | label count per row reported; parameters reported |
| time | none | ticks | no across-level time is compared; one level only (piece into unit) |

The same procedure applies to every model; hyperparameters differ only through the one shared tuning budget. No squad-level or oscillator quantity appears.

## 6. Stop conditions (yes/no, one action, one role)

| Condition | Action | Role |
|---|---|---|
| Owner has not approved this proposal? | build and run nothing | drafter |
| A gradient check or equivalence test fails? | fix before any run | implementer |
| Any learnability gate fails on development entropy? | drop or redesign that item, record it, re-register | drafter |
| Tuning picks a boundary value of the search space for any model? | extend the space once, on development entropy only | implementer |
| The extrapolated teacher does not beat rush by 0.10? | drop Part C, record it | drafter |
| Smoke wall time times 30/2 seeds predicts more than the stated cap? | report to the owner and wait | implementer |
| The recorded run is INCOMPLETE (cap, error, missing seed)? | no resume, no seed replacement; report | implementer |
| A bar or margin would be changed after a recorded result exists? | no; register a new revision on fresh entropy | drafter |
| Cross-family review requested for a qualifying claim? | out of scope for this exploratory run; owner decides | owner |

## 7. Cost and order (estimates; measured on the smoke run first)

Stage 0 took 174 s wall on 8 workers for 20 seeds with 60 episodes per cell. 0d adds seven models, three change types with a 6-point grid and 3 designs each, 200 paired episodes per win cell and 30 seeds.
Estimate: development (tuning, learnability, gradient check) about 15 minutes of CPU on one machine; the recorded run **20 to 40 minutes** wall on 8 workers, dominated by closed-loop episodes and the three change grids.
I will state the measured smoke time before the recorded run. Order: (1) approval; (2) development and the gradient check, committed with raw results; (3) specification, code, tests committed; (4) smoke; (5) one recorded run; (6) report with corrections-first wording; (7) one same-family review before the run (as before), no cross-family claim.

## 8. Self-audit (the drafter's known weaknesses)

| Weakness | Consequence | Mitigation or acknowledgement |
|---|---|---|
| Teachers are hand-written rules, so every result is imitation | a result here does not say pieces can be learned from outcomes | named as the next experiment; not claimed |
| S1 and S2 are my own implementations of structured baselines | a weak implementation would flatter C | gradient check, parameter match, same tuning budget; the numbers of both are reported |
| One sandbox, 30 seeds are replicates of one environment | intervals describe seed noise, not task variety | the intervals are labelled as such; external benchmark listed as later |
| The new stepping rule and the extrapolated type are my design | easy to choose ones that favour C | both are fixed on development entropy under the learnability gate, before any recorded result |
| The margins come from development spread | could be loose or tight | written before the run; the report shows the raw intervals so the reader can apply others |
| "Wired retrains only the changed piece" is built in | B1 and B2 favour C by construction | the frozen-head control exists to take that away; if it closes the gap, H-change is REFUTED |

Files if approved: `SPECIFICATION_0D.md`, `SPEC_0D.json`, `zd_models.py` (F0, F1, F2, S1, S2 with hand-written backpropagation), `zd_run.py`, `test_zd.py`, `dev_0d/` (scripts, raw results, README).
