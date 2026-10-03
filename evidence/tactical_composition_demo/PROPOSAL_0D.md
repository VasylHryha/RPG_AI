# Experiment 0d, Part A — structure versus composition (REVISION 2, DRAFT for owner approval; nothing is built or run)

Exploratory line under decision 0028; not a milestone, not C6 evidence. Revision 1 (commit `3084b68`) was reviewed by Codex (cross-family; `docs/reviews/tactical_composition_0d_review_codex.md`,
verdict CHANGES_REQUIRED, R1–R8). This revision narrows the experiment to **Part A only** and fixes the defects the review found; each fix and its cause is in section 9.
**Before approval no project code runs** (AGENTS.md). If approved, code goes in new files only (`tcd_common` plus `zd_*.py`); `tactics.py` and the recorded harnesses stay frozen.

Not part of this approval: a MOVE-only or both-piece change test (old Part B), an extrapolated unit type (old Part C), learning from outcomes, the squad level, an outside benchmark, geometry,
oscillators, "vibration". Appendix A records what Part B and C would need before they could be proposed.

## 1. The question

The wired unit (AIM + MOVE) copies the teacher's computation graph; the recorded baseline was a plain network over fixed enemy slots, trained with the composed recipe unchanged. Part A asks, on the
Stage 0 task and with one data budget:

1. Is the recorded flat baseline under-tuned? (concurrent comparison, not against an old number)
2. Does a tuned flat model, with or without a discrete move head, still lose to the wired unit?
3. Does a structured network of the same graph, trained jointly with its own selection feeding its movement, do as well as the separately taught pieces?

Only the third needs new mechanism. A positive result bounds a claim about imitation of a scripted teacher in one sandbox; it says nothing about geometry or RRG.

## 2. Design

**Task, teacher, opponents, mixes:** exactly as Stage 0 (`tactics.py`): 3 against 3, teacher scores per enemy, argmax, step rule; opponents rush and kiter; seen mixes only. Pools come from the teacher's play with 30% random actions.

**Splits by independent episode (no state-level leakage):** per seed, a training pool of 600 episodes and an independent held-out test pool of 100 episodes. Development uses its own entropy with a training pool of 400 episodes and an independent validation pool of 100.

**One shared supervision (matched source states and label content):** per seed, `N` source states are drawn from the training pool (primary `N = 3,000`; descriptive `N = 1,000` and `N = 9,000`, using the settings tuned at 3,000). Every model sees the same states and the same label content: the teacher's score for every living enemy and the teacher's step toward its own chosen target. Packaging differs by design: C's AIM rows are the living (state, enemy) pairs and its MOVE rows the (relative target position, preferred range) pairs; flat and structured models see one row per state. Reported for every model: unique source states, scalar supervision count, parameters, trainable parameters.

**Models (every family gets the same search space and the same 12 trials):**

| Id | Model | Role |
|---|---|---|
| F0 | flat network, recorded recipe (15 hidden, lr 0.003, 8,000 steps, batch 128), **not tuned** | the historical baseline, now concurrent |
| F1 | flat network over fixed enemy slots, tuned | fair flat baseline, squared-error step head |
| F2 | F1 with a discrete move head (hold or one of 8 directions, cross-entropy; a move step is the unit direction) | does the step head's output form explain the flat model's loss? |
| C | composed: AIM (a shared per-enemy scorer) and MOVE (target-conditioned step) taught separately and wired; one tuned setting applied to both pieces | the design under test |
| S1 | structured **own-selection** network, below | joint training with its own selection feeding movement |

**S1, fully specified.** Scorer `g`: the AIM-piece architecture, one weight set applied to every living enemy (inputs `aim_features`). Move head `f`: the MOVE-piece architecture (inputs `move_features`: relative position of the selected enemy and own preferred range). Standardization of inputs and outputs is learned from the training rows at the start and then frozen. Training selection: straight-through hard selection. The forward pass takes the hard argmax enemy (identical to inference); the backward pass uses the softmax weights `w = softmax(z)` over living enemies with `z` the standardized scores, so the step loss sends gradient to the scorer through `w` (`h = onehot(argmax) + w − stopgrad(w)`, selected relative position `Σ_j h_j rel_j`). Masks: dead enemies have `-inf` score. Loss: `L = L_score + L_step`, equal weights, both on standardized targets: `L_score` is the squared error of `g` on the teacher's scores of living enemies; `L_step` is the squared error of `f` against the teacher's step rule **applied to the enemy S1 itself selected** (the teacher's movement rule is an analytic function, so this is an oracle query on S1's own choice). This gives S1 more supervision than C (C's MOVE only ever sees the teacher's chosen enemy); the extra information favours S1, so a C-versus-S1 result where C is not worse is conservative for C. One Adam optimizer over all parameters, one shared set of minibatches of source states. Inference: argmax enemy, then `f`.
**Teacher-forced structured training is not a recorded arm.** Feeding `f` the teacher's chosen enemy with disjoint parameters and additive losses is mechanically separable and reduces to C; it appears only as a unit test of the training code (matched batches reproduce separate training), as a mechanics reference.

**Tuning (development entropy only):** search space (same for every family): hidden `{8, 16, 32}`, learning rate `{0.001, 0.003, 0.01}`, L2 weight decay `{0, 1e-4, 1e-3}`, steps `{4000, 8000, 16000}`; batch 128; 12 random trials per family (C: one trial = one setting used by both pieces, so C also gets 12), 5 development seeds per trial, selection objective = mean development-validation `a_joint` (section 3), ties broken by fewer parameters then lower trial index. If a chosen value lies on the boundary of the grid, the grid is extended once on the same family and the extra trials are added to its budget (budget reported). F0 is deliberately untuned. The comparator `F*` is whichever of F1 and F2 has the higher development-validation objective (ties to F1), fixed before the recorded run.

**Saved for every recorded model:** weights (compressed), the held-out state set digest, and the seed's stream keys, so metrics can be recomputed later.

## 3. Primary estimand (the joint action) and strata

On held-out **multi-enemy** states (single-enemy states agree trivially and are excluded). A state succeeds (`a_joint`) when the chosen enemy is **tied-best** for the registered teacher **and** the step toward that enemy matches the teacher's step for that enemy: a hold (`|step| < 0.5`) where the teacher holds, otherwise a move (`|step| ≥ 0.5`) within **10°** of the teacher's step. The teacher's movement function is passed explicitly to evaluation. Strata, defined by the teacher's own label toward its own target (independent of the controller): hold, moving, back-off (moving away from the target). Every stratum's success rate, count and denominator are reported; a stratum rate is reported only with at least 30 states per seed. Diagnostics (not verdict inputs): tie-aware chance-corrected target agreement, step angle on moving states, and the forgiving tie-set step score in which every eligible state counts (a wrong hold and a wrong move on a hold state each count 90°).
The evaluation stops (run INCOMPLETE, no value invented) on an empty multi-enemy population, a chosen enemy that is not alive, non-finite data, or a stratum below 30 states in a seed. Implemented in `tcd_common.metrics.joint_action` (new, with hand-computed tests before any run).

## 4. Endpoints and pre-registered verdicts (words are exploratory vocabulary)

Everything is paired within seed and built from explicit seed identities (`tcd_common.stats.paired_by_seed`; a missing or non-finite endpoint is an error, never a dropped seed). `A(M)` is the model's per-seed `a_joint` at N = 3,000. Each contrast is the median over seeds of the paired difference with a 95% percentile bootstrap interval `I(·) = [lo, hi]`.
Fixed practical margins (set now by design, not from development comparisons): **equivalence δ_eq = 0.03**, **superiority δ_sup = 0.06**, in units of `a_joint`.

| Contrast | Definition |
|---|---|
| E0 | A(C) − A(F0) |
| E1 | A(C) − A(F*) |
| E2 | A(C) − A(S1) |
| E3 | A(S1) − A(F*) |
| T1 | A(F*) − A(F0) (tuning effect) |
| T2 | A(F2) − A(F1) (output form) |

Executable rules (strict inequalities; the three outcomes of each row are mutually exclusive and exhaustive):

| Row | SUPPORTED | REFUTED | INDETERMINATE |
|---|---|---|---|
| V1 the wired unit beats the tuned flat model | `lo(E1) > δ_sup` | `hi(E1) < δ_sup` | otherwise |
| V2 training mode (C versus S1) | label SEPARATE_BETTER if `lo(E2) > δ_sup`; JOINT_BETTER if `hi(E2) < −δ_sup`; EQUIVALENT if `−δ_eq < lo(E2)` and `hi(E2) < δ_eq` | (labels, not a refutation) | otherwise |
| V3 structure explains the gain | `V1` SUPPORTED and `lo(E3) > δ_sup` and V2 EQUIVALENT | V1 SUPPORTED and (V2 SEPARATE_BETTER or `hi(E3) < δ_sup`) | otherwise (including V1 not SUPPORTED) |
| V4 the recorded baseline was under-tuned | `lo(T1) > δ_eq` | `−δ_eq < lo(T1)` and `hi(T1) < δ_eq` | otherwise |
| V5 a discrete move head matters | `lo(T2) > δ_eq` | `−δ_eq < lo(T2)` and `hi(T2) < δ_eq` | otherwise |

Prerequisite gates: **S1 adequacy** (on the development validation set, at its tuned setting, its scorer's tie-aware agreement is at least 0.85 and its step success on moving states at least 0.85; and the finite-difference and straight-through consistency tests pass). If S1 is inadequate the V2 and V3 rows are INDETERMINATE ("baseline inadequate") and S1's numbers are reported only. **C adequacy** (development `a_joint` of C at least 0.90). If C fails it, the experiment's premise fails and the run does not start.
Closed-loop win score (200 paired episodes per cell, seen mixes, both opponents, for the teacher, rush, F0, F*, C, S1) is **secondary and exploratory**: it enters no verdict except discordance: if the win-score paired interval for the same contrast as V1 or V2 excludes 0 with the opposite sign to the fidelity verdict, that row becomes INDETERMINATE (discordant). No multiplicity adjustment is applied: the five rows are separately pre-registered and every interval is labelled unadjusted. Seeds are replicates of one environment, not independent tasks; the intervals describe seed noise only.

Because `E1 = E2 + E3` holds within seed only for the same comparator, V3 uses the directly estimated E1, E2 and E3, never sums of medians.

## 5. Seeds and precision (fixed before the recorded run)

On development entropy, from 10 development seeds run through the full pipeline, estimate the standard deviation `sd` of the per-seed paired differences E1, E2, E3, T1, T2. The seed count `S` is the smallest of `{30, 45, 60}` for which `1.96 × 1.253 × max(sd) / √S ≤ 0.015` (half of δ_eq; the factor 1.253 is the large-sample inflation of the median's standard error over the mean's); if even 60 fails, `S = 60` and the report states that EQUIVALENT cannot be reached at this precision. `S` and the estimated `sd` are written into the specification. This is a sensitivity calculation under a normal approximation, not a measured power.

## 6. Normalization ledger

| Quantity | Level | Unit | Normalization |
|---|---|---|---|
| a_joint, strata rates | decision (multi-enemy state) | share | teacher-defined success; no cross-level use |
| target agreement | decision | share | tie-aware; chance-corrected by the uniform living pick; None if chance = 1 |
| step angle | decision | degrees | toward the chosen enemy; 90° for a hold/move violation; only moving states |
| inputs | per piece or per model | feature units as in `tactics.py` | standardized by training-row mean and std, frozen after the start (for fine-tuning there is none in Part A) |
| outputs | per model | step: vector in sandbox length; scores: teacher score units | standardized for training; evaluated unstandardized |
| win score | episode | win 1, draw 0.5, loss 0 | teacher-relative (minus the teacher's score on the same cell) |
| rows | decision | labelled rows | reported with unique source states, scalar supervision count, parameters |
| cost | run | wall and CPU seconds | jobs, evaluation and total reported separately |
| time | none | ticks | no across-level time is compared; one level only (piece into unit) |

The same procedure, search space and trial budget apply to every family. No squad-level or oscillator quantity appears.

## 7. Stop conditions (measurable yes/no; one action; one role)

| Condition | Action | Role |
|---|---|---|
| Is the proposal unapproved by the owner? | build and run nothing | drafter |
| Is any dependency of the run uncommitted, or does the registration commit differ from the clean tree at run time? | refuse to start (preflight) | implementer |
| Is the run directory already present (latch consumed)? | refuse to start; no resume | implementer |
| Does a finite-difference or straight-through consistency test fail? | fix before any run | implementer |
| Does C fail its development adequacy gate (a_joint ≥ 0.90)? | stop; report the premise failed | drafter |
| Does S1 fail its adequacy gate at its tuned setting? | keep S1 as reported-only; mark V2 and V3 INDETERMINATE | implementer |
| Is any tuned value on the boundary of the grid? | extend the grid once for that family on development entropy | implementer |
| Does the measured full-size single-seed development run predict more than the cap set from it? | report to the owner; narrow N or seeds, never thresholds | implementer |
| Is any planned endpoint missing, non-finite or not-run for any seed? | run is INCOMPLETE; no seed dropped or replaced | implementer |
| Is the recorded run INCOMPLETE (cap, error, missing seed)? | report; no resume, no retry | implementer |
| Would any margin, row or bar change after a recorded result exists? | no change; register a new revision on fresh entropy | drafter |
| Did the pre-run review (see 8) return CHANGES_REQUIRED? | fix and re-review before the run | drafter |

## 8. Cost and order

Inventory per seed: pool collection (600 + 100 episodes), fits for F0, F1, F2, C (two pieces), S1 at three values of N (15 fits + 3 reference F0 fits), `a_joint` evaluation of five models on the test pool, and closed-loop cells (6 policies × 2 opponents × 200 episodes). Stage 0, for scale, took 174 s wall on 8 workers for 20 seeds with 60 episodes per cell; the closed-loop cells dominate. **No time estimate is claimed here.** A full-size single-seed development run (not a smoke multiplication: the worker count, config and evaluation differ) sets: jobs soft cap = 1.5 × the measured per-wave time × the number of waves, hard cap = soft cap + 300 s, evaluation cap (`eval_cap`) = 300 s. Jobs, evaluation and total wall and CPU seconds are recorded separately. Before the recorded run I state the measured time. If the budget is insufficient the experiment is narrowed (N values, win cells, seeds), never the thresholds.
Order: (1) owner approval; (2) development on its own entropy, committed with raw results and a README: gradient and straight-through tests, tuning, adequacy gates, `sd` and `S`, full-size cost; (3) specification, `SPEC_0D.json` (tuned settings, margins, S, caps), code, tests, committed — **this commit is the registration boundary**; (4) a same-family review of the registered files before the run, and a Codex review if the owner wants one; (5) smoke on its own entropy; (6) one recorded run from a clean tree at the registration commit; (7) report with corrections-first wording. Test timing: tests run once at the end of each change batch, with any earlier run preceded by its blocking need.

## 9. Review disposition (the drafter's defects, causes and fixes — AGENTS.md)

| Review item | Defect in revision 1 | Cause | Fix in this revision |
|---|---|---|---|
| R1 H-change cannot measure a MOVE-only change; wrong teacher in metric | raw target agreement levels cannot see a movement change; metric code defaulted to the old movement rule | I picked one level for both changes and reused `change_metrics` without checking its interface | Part B removed from this approval; `joint_action` takes the registered `teacher_move` explicitly; Appendix A lists the n = 0 negative control and strata Part B must add |
| R2 S1 unspecified; teacher forcing collapses the comparison | "softmax selection … own selected enemy" had several implementations | I described intent, not training | section 2: straight-through selection, masks, loss, features, normalization, label access; teacher-forced training demoted to a unit test |
| R3 verdict rules ambiguous, margins not fixed | one margin for two scales; "better of F1 and F2" undefined; asymmetric H-struct; sum-of-medians inference | rules written as prose | section 4: one estimand, fixed δ, strict inequalities, symmetric V2, V3 from direct E1–E3, comparator chosen on development only, discordance rule |
| R4 frozen-head control weaker than a full retrained piece | head-only freezing is a poorer control | defined "head" as final layer | Part B removed; Appendix A requires full affected-branch retraining as the matched control |
| R5 movement metric hides failures | wrong move on an all-hold state dropped; denominators depended on correctness; chance = 1 undefined | I special-cased the mixed tie and stopped | `metrics.py`: every eligible state scored, strata with counts, stop on undefined populations; tests |
| R6 extrapolated type confounded | speed is not an AIM/MOVE input; type, stats and opponent unspecified | I added a condition without checking inputs | Part C removed; Appendix A |
| R7 tuning and ledger incomplete | space, splits, objective, per-piece budgets, stop rows not defined | drafted as an outline | sections 2, 6, 7 |
| R8 power and timing | no precision basis; 30/2 smoke scaling; accounting omitted controls | optimistic estimate | section 5 precision rule, section 8 inventory, measured caps, separate evaluation bound |

## Appendix A — what Part B and C would need (not approved)

- **Part B (MOVE-only or both-piece change):** the exact new stepping rule and affected strata fixed in advance; recovery defined as a conjunction of target quality, movement quality, hold accuracy and back-off quality with tolerances and minimum stratum counts; the registered movement teacher passed explicitly to evaluation; an unchanged old controller scored at n = 0 and required to fail recovery in the changed behaviour, with a minimum change magnitude declared; full affected-branch retraining of the structured policy as the matched control (final-layer controls only as additional); a complete grid fixed once; the row-cost statistic, censoring and two-failure rule defined; B3's AIM and MOVE rows allocated explicitly.
- **Part C (extrapolated type):** all type statistics, mixes and opponent rules fixed; type-only, opponent-only and combined conditions separated; input differences disclosed (speed reaches the flat model but not the pieces); teacher headroom and stratum coverage gated; an in-domain positive control on separate development entropy; no zero-shot policy trained on the held-out type; an absolute teacher-fidelity gate.
