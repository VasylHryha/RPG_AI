# Experiment 0d Part A — results (exploratory; NOT a milestone, NOT C6 evidence)

Status: COMPLETE. One execution from the registration commit `c747e76` (`SPECIFICATION_0D.md`, `SPEC_0D.json`). 30 of 30 seeds, no errors, no retry, no post-hoc analysis. Wall **1,487 s** (25 minutes;
the pre-run estimate from a loaded machine was 38), evaluation 0.1 s, children CPU 4,824 s, peak 0.36 GB per worker, 8 workers. **The machine was loaded by another project's jobs**: load averages (1, 5, 15 minutes)
at the start 16.8, 40.7, 67.3 (10 cores) and about 70, 99, 101 afterwards; the run did not hit a cap. Raw per-seed records, the saved weights of every N = 3,000 model and the accounting are in `run_0d/`
(`SUMMARY.json` is the record). Verdict words are exploratory vocabulary, not milestone verdicts. No cross-family review of this result exists and none is claimed. Read `CORRECTIONS.md` and the limits below first.

## What was tested

Whether the advantage of the wired unit (AIM + MOVE) over one flat block comes from its **structure** (one scorer shared by all enemies and a step conditioned on the chosen enemy) or from teaching the pieces **separately**.
Five models on the same source states and label content (3,000 states, descriptive 1,000 and 9,000): F0 the recorded flat recipe, untuned; F1 flat, tuned; F2 flat with a 32-direction move head, tuned; C the pieces
taught separately and wired; S1 a structured network of the same graph trained jointly, its own selection feeding the step head. Primary measure `a_joint` on held-out multi-enemy states: the chosen enemy is tied-best for
the teacher and the step toward it matches the teacher's step (hold where it holds, otherwise within 10 degrees). Everything is imitation of one scripted teacher in one invented sandbox.

## Verdicts (the rules of `SPECIFICATION_0D.md` section 3, applied as written; median over 30 seeds with a 95% paired bootstrap interval)

| Row | Result | Verdict |
|---|---|---|
| V1 the wired unit beats the tuned flat model | E1 = A(C) − A(F1) = **+0.419** [0.407, 0.426] (bar: lower bound above 0.06); closed-loop win score +0.414 [0.396, 0.431] | SUPPORTED |
| V2 training mode (C versus S1) | E2 = A(C) − A(S1) = **+0.021** [0.017, 0.022], inside ±0.03; win score +0.006 [−0.007, 0.015] | **EQUIVALENT** |
| V3 structure explains the gain | V1 supported, E3 = A(S1) − A(F1) = **+0.399** [0.387, 0.408], V2 equivalent | SUPPORTED |
| V4 the recorded baseline was under-tuned | T1 = A(F1) − A(F0) = +0.059 [0.051, 0.068] (bar: lower bound above 0.03); concurrent gap E0 = A(C) − A(F0) = +0.473 [0.463, 0.483] | SUPPORTED **on held-out fidelity only (see below)** |
| V5 a discrete move head matters | T2 = A(F2) − A(F1) = −0.008 [−0.017, −0.004], inside ±0.03 | REFUTED (it does not help here) |

## What this shows, in plain words

- **In this sandbox the gain is the structure, not the separate teaching.** S1, the same graph trained jointly end to end, scores within 0.02 of the separately taught pieces (0.940 against 0.960), and both are about 0.4 above every flat model.
  Teaching the pieces separately adds no detectable benefit once the structure is given; a tuned flat block, with or without a discrete move head, does not reach either.
- **The pieces connect without loss.** For C the joint score (0.960) equals the product of its two parts (right enemy 0.987, step when told the teacher's target 0.973; connection gap 0.000). The flat models lose at the **step**: told what to act on,
  their step success is 0.58 to 0.60 against 0.97, their median step angle on moving states is 16 to 22 degrees against 0.9 (C) and 1.4 (S1), and the tuned flat model almost never backs off (back-off success 0.002).
- **The result holds at every data size.** E1 is +0.414 at 1,000 states and +0.422 at 9,000; the flat models gain little from data (F1 0.530, 0.544, 0.543) while C gains slowly (0.946, 0.960, 0.963). At 1,000 states C is ahead of S1 by +0.032 [0.026, 0.037]
  (descriptive, outside V2) and the gap falls to +0.019 at 9,000; S1 has 12 times C's parameters.
- **Closed-loop play agrees on the main contrast.** Win score against rush and kiter: teacher 0.791 and 0.525; C 0.779 and 0.476; S1 0.774 and 0.476; rush 0.495 and 0.291; the tuned flat model 0.198 and 0.231; F0 0.379 and 0.340.
  C is 0.031 below the teacher (interval 0.024 to 0.034), S1 0.034 below.

## Limits and caveats (stated plainly)

- **V4 is a claim about held-out fidelity and the search, not about play.** Tuning raised the flat model's `a_joint` (0.485 to 0.544) but **lowered its closed-loop play** (mean win score 0.215 against 0.360 for F0, averaged over the two opponents: minus 0.446 against minus 0.292 relative to the teacher), because
  tuning picked a heavily regularized small network that never backs off (back-off success 0.002; F0 0.156). With more data the untuned recipe catches up on fidelity (F0 0.539 at 9,000 states against F1 0.543). Read V4 as "the recorded baseline was weaker than a tuned one on this measure",
  not "the recorded comparison was unfair"; the gap to the wired unit (E0 +0.473) is larger than the tuning effect (+0.059).
- **V2 applies to this straight-through design.** S1's step head sees only (relative position, preferred range); the coupling to the scorer is the straight-through gradient. EQUIVALENT says that this design, trained jointly, does not beat or lose to separate
  teaching by more than the margin; it does not say joint and separate training are equivalent in general.
- **S1 is a different size and gets more supervision.** S1 tuned to 9,283 parameters against C's 787 (F1 357, F2 3,204, F0 770) and queried the teacher's rule 2,048,000 times on its own selection (C none, same label content otherwise). Both favour S1; C still matched or beat it, and
  V2 EQUIVALENT is therefore conservative for C. The development data had put the interval for E2 close to the margin (0.027 against 0.03) and the recorded interval is 0.022: the verdict was not guaranteed in advance and could have been INDETERMINATE.
- **The measure has a 10-degree step tolerance.** The flat models' failure is gross (16 to 22 degrees median), so the tolerance does not drive V1 or V3; V5 and V4 are claims about this search (24 shared settings per family, one grid extension, boundary values accepted: F1 learning rate and decay, F2 learning rate and decay, C steps, S1 hidden size).
- **Scope.** One invented sandbox; one scripted teacher and two scripted opponents; imitation, not learning from outcomes; independent units (one level: pieces into a unit); 30 seeds replicate one environment (intervals describe seed noise only); five rows separately registered, intervals unadjusted.
  The development phase (including an 8-seed cost run on separate entropy) had previewed the likely answer (disclosed in `dev_0d/README.md`); nothing was chosen from it. **Nothing here tests geometry, oscillators, "vibration" or any RRG hypothesis.**
- **Not computed:** the forgiving tie-set step diagnostic; stream keys are not stored (derivable, listed in the specification).

## What this changes for the project (one line each)

The "composition beats flat" claim of Stage 0 is now explained: it is the structure of the unit, reproduced by a jointly trained network of the same graph. The change-cost result (C reached 0.80 at the grid floor against 1,000 rows for a flat block) remains a statement about retraining
the affected piece, which a structured baseline was not tested on (Appendix A of `PROPOSAL_0D.md`). The next questions are the ones this experiment cannot answer: a second level (units into a squad), and learning the pieces from outcomes instead of from a teacher.

## Process notes

Revision 1 of the proposal was rejected by Codex (CHANGES_REQUIRED); revision 2 narrowed the experiment and fixed the listed defects. A same-family pre-run review of the registered files recommended FIX FIRST: its findings (machine load and cap margin, provenance of the cost run, a V3 rule differing from the specification when V2 is discordant, a missing test, a stale header, expectation notes) were applied before the run in `c747e76`
(`docs/reviews/tactical_0d_prerun_review_claude.md`). The recorded run started from `c747e76` with a clean tree; the smoke run on the final code is `smoke_run_0d/`.
