# Experiment 0d Part A — results (exploratory; NOT a milestone, NOT C6 evidence)

**Corrected 2026-10-04** after a recheck (four same-family audits and a flat-baseline probe): several sentences below were rewritten where the data do not support the first wording; the first text is in git history (`eae0b29`). **The headline reading is narrower than first written: the flat baseline is weak (it plays worse than the trivial rush rule), so the size of the gap is a statement about small flat networks at N up to 9,000 states, not about flat networks in general.** See "Post-run recheck" at the end.

Status: COMPLETE. One execution from the registration commit `c747e76` (`SPECIFICATION_0D.md`, `SPEC_0D.json`). 30 of 30 seeds, no errors, no retry, no post-hoc analysis. Wall **1,487 s** (25 minutes;
the pre-run estimate from a loaded machine was 38), evaluation 0.1 s, children CPU 4,824 s, peak 0.36 GB per worker, 8 workers. **The machine was loaded by another project's jobs**: the run record has the load averages (1, 5, 15 minutes)
at the start only (16.8, 40.7, 67.3 on 10 cores); per-seed times fall from about 515 s in the first wave to about 165 s in the last (6 seeds), so the load eased during the run. The run did not hit a cap. Raw per-seed records, the saved weights of every N = 3,000 model and the accounting are in `run_0d/`
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

- **In this sandbox the gain is consistent with coming from the graph the pieces were given, not from teaching them separately.** S1, the same graph trained jointly end to end, scores about 0.02 below the separately taught pieces (0.940 against 0.960), and both are 0.40 to 0.47 above the flat models at N = 3,000. That is matched performance of two recipes that were both given the teacher's graph, against weak flat baselines: it does not isolate which element of the graph matters, and it is not a statement about all training regimes.
  Teaching the pieces separately gives a **small but consistent benefit of about +0.02** (C is ahead of S1 in 30 of 30 seeds; the interval [0.017, 0.022] excludes 0 but sits inside the registered ±0.03 margin, and S1 had 12 times the parameters and extra oracle queries). A small tuned flat block, with or without a discrete move head, does not reach either.
- **The connection gap is near zero for the wired unit (a diagnostic, not proof of lossless wiring).** For C the joint score (0.960) is within ±0.0004 per seed of the product of its two parts (right enemy 0.987; step success against the teacher's own target 0.973), and S1 likewise. That product compares different target distributions and errors may correlate, so a near-zero gap does not establish lossless causal wiring. The flat models lose at the **step**: their step success against the teacher's own target is 0.58 to 0.60 against 0.97
  (for a flat model this is not an intervention: it has one step output and cannot be told which enemy to act on), their median step angle on moving states is 16 to 22 degrees against 0.9 (C) and 1.4 (S1), and the tuned flat model almost never backs off (back-off success 0.002; exactly 0 in 8 seeds). The failure is general, not only back-off: the tuned flat model's success on moving states is 0.38.
- **V1's direction holds at every N tested, but the flat model was tuned only at N = 3,000.** E1 is +0.414 at 1,000 states and +0.422 at 9,000, with F1 held at its N = 3,000 setting (hidden 8, 357 parameters; 0.530, 0.544, 0.543 across N). That plateau is a property of that small, heavily regularized setting, **not** of flat networks: the probe below shows larger flat models climbing with capacity, data and training.
  C moves 0.946, 0.960, 0.963. At 1,000 states C is ahead of S1 by +0.032 [0.026, 0.037], beyond the ±0.03 margin (descriptive; V2 is a statement at N = 3,000), and the gap falls to +0.019 at 9,000; S1 has 12 times C's parameters.
- **Closed-loop play agrees on the main contrast.** Win score against rush and kiter: teacher 0.791 and 0.525; C 0.779 and 0.476; S1 0.774 and 0.476; rush 0.495 and 0.291; the tuned flat model 0.198 and 0.231; F0 0.379 and 0.340.
  C is 0.031 below the teacher (interval 0.024 to 0.034), S1 0.034 below. (The policy means above are medians over seeds of each policy's mean over the two opponents; the contrasts are medians of per-seed paired differences, so they differ slightly from differences of the means: for example F* minus teacher is −0.446 as a paired median and −0.443 as a difference of means.)

## Limits and caveats (stated plainly)

- **The tuned flat baseline is not an adequate baseline in play.** Its mean win score (0.215) is below the trivial scripted rush rule (0.395) in all 30 seeds, and below the untuned F0 (0.360) in all 30 seeds; F0 itself is below rush in 24 of 30. Stage 0 required its big flat controller to beat rush by 0.15; no 0d flat model passes that. The V1 and V3 gaps are therefore gaps against weak flat players.
- **V4 is a claim about held-out fidelity and the search, not about play.** Tuning raised the flat model's `a_joint` (0.485 to 0.544) but **lowered its closed-loop play** (mean win score 0.215 against 0.360 for F0, averaged over the two opponents: minus 0.446 against minus 0.292 relative to the teacher), because
  tuning picked a heavily regularized small network that never backs off (back-off success 0.002; F0 0.156). With more data the untuned recipe catches up on fidelity (F0 0.539 at 9,000 states against F1 0.543). Read V4 as "the recorded baseline was weaker than a tuned one on this measure",
  not "the recorded comparison was unfair"; the gap to the wired unit (E0 +0.473) is larger than the tuning effect (+0.059).
- **V2 applies to this straight-through design.** S1's step head sees only (relative position, preferred range); the coupling to the scorer is the straight-through gradient. EQUIVALENT says that this design, trained jointly, does not beat or lose to separate
  teaching by more than the margin; it does not say joint and separate training are equivalent in general.
- **S1 is a different size and gets more supervision.** S1 tuned to 9,283 parameters against C's 787 (F1 357, F2 3,204, F0 770) and queried the teacher's rule 2,048,000 times on its own selection (C none, same label content otherwise). Both favour S1; C still matched or beat it, and
  V2 EQUIVALENT is therefore conservative for C. The development data had put the interval for E2 close to the margin (0.027 against 0.03) and the recorded interval is 0.022: the verdict was not guaranteed in advance and could have been INDETERMINATE.
- **The flat search was small.** Hidden sizes over the 24 settings were 4 (four settings), 8 (nine), 16 (six), 32 (three), 64 (two); two layers; tuning at N = 3,000 only; the chosen F1 and F2 sit at the lowest learning rate and highest decay of the extended grid; the objective (overall `a_joint`) picked the model that never backs off and plays worst. A development probe (below) shows the flat family reaches 0.61 at N = 9,000 and 0.74 at N = 60,000 with larger networks and longer training.
- **The measure has a 10-degree step tolerance.** The flat models' failure is gross (16 to 22 degrees median), so the tolerance does not drive V1 or V3; V5 and V4 are claims about this search (24 shared settings per family, one grid extension, boundary values accepted: F1 learning rate and decay, F2 learning rate and decay, C steps, S1 hidden size).
- **Scope.** One invented sandbox; one scripted teacher and two scripted opponents; imitation, not learning from outcomes; independent units (one level: pieces into a unit); 30 seeds replicate one environment (intervals describe seed noise only); five rows separately registered, intervals unadjusted.
  The development phase (including an 8-seed cost run on separate entropy) had previewed the likely answer (disclosed in `dev_0d/README.md`); nothing was chosen from it. **Nothing here tests geometry, oscillators, "vibration" or any RRG hypothesis.**
- **Not computed:** the forgiving tie-set step diagnostic; stream keys are not stored (derivable, listed in the specification). Strata are not disjoint: back-off is a subset of moving (hold 31%, back-off 15% of multi-enemy test states).
- **Approval.** The run started on the author's reading of the owner's message "og go ahead do we need new seiso nor do it in this one ?" as approval to register and run Part A; that reading is flagged **[R]** (decision 0028 item 8) and awaits the owner's ratification.
- **No cross-family review of the registered code or of this report exists.** Codex reviewed revision 1 of the proposal; the same-family pre-run review had no re-review after its fixes (the run started about 90 seconds after the fix commit).

## What this changes for the project (one line each)

The "composition beats flat" claim of Stage 0 is now explained at the level this experiment can reach: it is the structure of the unit (the teacher's graph, which both C and S1 were given), reproduced by a jointly trained network of the same graph, against small flat networks. The change-cost result (C reached 0.80 at the grid floor against 1,000 rows for a flat block) remains a statement about retraining
the affected piece, which a structured baseline was not tested on (Appendix A of `PROPOSAL_0D.md`). The next questions are the ones this experiment cannot answer: a second level (units into a squad), and learning the pieces from outcomes instead of from a teacher.

## Process notes

Revision 1 of the proposal was rejected by Codex (CHANGES_REQUIRED); revision 2 narrowed the experiment and fixed the listed defects. A same-family pre-run review of the registered files recommended FIX FIRST: its findings (machine load and cap margin, provenance of the cost run, a V3 rule differing from the specification when V2 is discordant, a missing test, a stale header, expectation notes) were applied before the run in `c747e76`
(`docs/reviews/tactical_0d_prerun_review_claude.md`). The recorded run started from `c747e76` with a clean tree; the smoke run on the final code is `smoke_run_0d/`.

## Post-run recheck (2026-10-04)

Four same-family audits (numbers and verdicts; scientific validity; code and reproducibility; governance and documents) and two checks of my own followed the report. Nothing changes a verdict: all five verdicts re-derive from the per-seed files (intervals within 0.001), and the numbers in this report match the data except the wording corrected above.

- **Round trip.** Every saved N = 3,000 model (30 seeds × 5) was rebuilt from its weights and scored on a regenerated test pool: the joint scores and strata match the recorded values exactly (maximum difference 0.0) and all 30 test-state digests match (`verify_run_0d.py`, `verify_run_0d_result.json`).
- **Flat-capacity probe** (development seeds 5 to 7, not registered, affects no verdict; `dev_0d/probe_flat_capacity.py`, `dev_0d/POSTRUN_NOTES.md`): an F1-type flat network with 64 hidden units reaches `a_joint` 0.446 at N = 3,000 (below the tuned small F1, which is better at that N), 0.613 at 9,000, 0.696 at 27,000, 0.737 at 60,000 (hidden 128: 0.486, 0.585, 0.706, 0.735), against C at 0.957 at 3,000. So the wired unit at 3,000 states beats a flat model at 60,000 states, an observed comparison at 3,000 versus 60,000 states in this sandbox and for this measure (no strong-baseline threshold or continuous data requirement was measured); the gap at one N overstated what a flat model tuned at that N would do. This is a post-hoc probe after the result and does not replace a registered flat-baseline experiment.
- **Additional tests** for branches the audits found untested (`test_zd_audit.py`, 7 checks; six deliberate mutations of the verdict code are caught); the registered files were not edited after the run (their hashes are in `run_0d/RUN_STARTED.json`).
- **Notes on the registered files** (not edited): see `CORRECTIONS.md` section G.
- **What would make the structure claim convincing** (recommended next experiment, not yet proposed): a registered flat-baseline experiment with per-N tuning, larger and deeper flat networks, per-slot or mixture step heads, selection on closed-loop play and on a macro average over strata, a gate that the flat baseline beats rush, and a data-efficiency statement (the N at which the best flat model comes within 0.03 of C); then a squad-level test whose baselines share the structure.
