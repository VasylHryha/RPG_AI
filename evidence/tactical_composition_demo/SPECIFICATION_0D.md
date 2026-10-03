# Experiment 0d Part A — SPECIFICATION (registered at the commit that adds this file; exploratory; NOT a milestone, NOT C6 evidence)

Design and rationale: `PROPOSAL_0D.md` revision 2 (reviewed by Codex, `docs/reviews/tactical_composition_0d_review_codex.md`; each defect and its fix are in the proposal's section 9).
Authority: decision 0028, item 7 **[R]** (development phase), then the owner's "ok go ahead" to "do 1 then 2" (finish Part A cheaply, then the squad level), read as approval to
register and run Part A once. This file fixes everything the run does; the proposal's verdict rules (section 4) are reproduced here without change except where noted.
Nothing in this file was chosen after seeing a recorded result: there is none. Development results (`dev_0d/`) set only the settings, the seed count and the caps below.

## 1. What runs

One job per seed (`zd_run.py`, `run_seed`), 30 seeds, 8 workers, spawn pool, through `tcd_common.harness.run_experiment` (one-shot latch: `run_0d/`; smoke: `smoke_run_0d/`).
Per seed: a training pool of 600 teacher-play episodes and an independent test pool of 100 episodes (seen mixes, rush and kiter opponents, 30% random actions, as Stage 0);
the registered teacher's labels; one permutation of the training states from which the source states of every N are taken (nested: N = 1,000 ⊂ 3,000 ⊂ 9,000; primary N = 3,000).
Five models are fitted for each N on the same source states and label content: F0 (recorded flat recipe, untuned), F1 (tuned flat, squared-error step head), F2 (tuned flat, 32-direction head),
C (AIM and MOVE taught separately, wired; one setting for both pieces), S1 (structured own-selection network, straight-through, one optimizer). Tuned settings are in `SPEC_0D.json`
(`config.hps`), chosen on development entropy by the registered procedure (`dev_0d/tuned2.json`: 24 shared settings per family, one grid extension; boundary values accepted and reported).
Each seed also records the closed-loop win score (200 paired episodes per cell, seen mixes, both opponents) of the teacher, rush, F0, F* (= F1), C and S1 at N = 3,000, and saves the weights
and frozen standardizers of every N = 3,000 model with the digest of the test states.

## 2. Primary estimand and population

`a_joint` on held-out multi-enemy test states: the chosen enemy is tied-best for the registered teacher AND the step toward that enemy matches the teacher's step for it (hold where it holds;
otherwise a move within 10 degrees). Strata (hold, moving, back-off) are defined by the teacher's own label toward its own target; a stratum rate needs at least 30 states in the seed. A seed whose
test pool has a stratum below 30 states, an empty multi-enemy population, a dead chosen enemy or non-finite data makes the run INCOMPLETE (`config.require_strata`). Implemented in
`tcd_common.metrics.joint_action`; tested by hand-computed cases.

## 3. Contrasts, margins and verdict rules (unchanged from `PROPOSAL_0D.md` section 4)

Paired within seed by explicit seed identity (`stats.paired_by_seed`); median over seeds with a 95% percentile bootstrap interval (4,000 resamples, bootstrap entropy in `SPEC_0D.json`).
Margins: equivalence δ_eq = 0.03; superiority δ_sup = 0.06 (units of `a_joint`; the same margins on the win-score scale for discordance).
E0 = A(C) − A(F0); E1 = A(C) − A(F\*); E2 = A(C) − A(S1); E3 = A(S1) − A(F\*); T1 = A(F\*) − A(F0); T2 = A(F2) − A(F1) (A = `a_joint` at N = 3,000).

| Row | SUPPORTED | REFUTED | INDETERMINATE |
|---|---|---|---|
| V1 the wired unit beats the tuned flat model | lo(E1) > δ_sup | hi(E1) < δ_sup | otherwise |
| V2 training mode (labels) | SEPARATE_BETTER: lo(E2) > δ_sup; JOINT_BETTER: hi(E2) < −δ_sup; EQUIVALENT: lo(E2) > −δ_eq and hi(E2) < δ_eq | (labels) | otherwise |
| V3 structure explains the gain | V1 SUPPORTED and lo(E3) > δ_sup and V2 EQUIVALENT | V1 SUPPORTED and (V2 SEPARATE_BETTER or hi(E3) < δ_sup) | otherwise |
| V4 the recorded baseline was under-tuned | lo(T1) > δ_eq | lo(T1) > −δ_eq and hi(T1) < δ_eq | otherwise |
| V5 a discrete move head matters | lo(T2) > δ_eq | lo(T2) > −δ_eq and hi(T2) < δ_eq | otherwise |

Discordance with the closed-loop win score (exploratory; enters no verdict except here): with W the paired interval of the same contrast on the win score, V1 SUPPORTED and V2 SEPARATE_BETTER
are discordant if hi(W) < 0; V1 REFUTED is discordant if lo(W) ≥ δ_sup; V2 JOINT_BETTER if lo(W) > 0; V2 EQUIVALENT if lo(W) ≥ δ_eq or hi(W) ≤ −δ_eq; a discordant row becomes INDETERMINATE.
Gates from development (fixed in `SPEC_0D.json`): C adequate (mean development `a_joint` 0.957 ≥ 0.90) and S1 adequate (scorer admissible 0.967 ≥ 0.85, step success on moving states 0.921 ≥ 0.85);
if `s1_adequate` were false V2 and V3 would be INDETERMINATE. No multiplicity adjustment: five separately pre-registered rows, every interval unadjusted. Seeds replicate one environment, not independent tasks.
Equality cases are strict (`>` and `<`). V3 uses the directly estimated E1, E2 and E3.

## 4. Caps and cost (measured in `dev_0d/cost_run/`, one wave of 8 full-size seeds on fresh development entropy)

Measured: one wave of 8 full-size seeds on 8 workers took **577 s** wall (evaluation 0.1 s, children CPU 1,335 s, peak 0.33 GB per worker; per-seed time 563 to 576 s: S1 fits 61 s,
C 17 s, F2 10 s, F0 3 s, F1 3 s per N; 175 s of closed-loop play per seed; three values of N per model). Thirty seeds on 8 workers are four waves (8, 8, 8, 6), so the expected wall time is
**about 38 minutes**. Caps: jobs soft cap **3,600 s** (1.5 times the expected time), hard cap **3,900 s**, evaluation and summary write bound (`eval_cap`) **300 s**. The cost run also exercised
the harness, the evaluation and the verdict code at full size on development entropy (its output is not used: see `dev_0d/README.md`). If the soft cap is reached the run is INCOMPLETE; no thresholds,
seeds or N values are changed afterwards.

## 5. Normalization ledger, stop conditions

As `PROPOSAL_0D.md` sections 6 and 7, with these concretizations: tuning budget 24 shared settings per family (reported); parameters, supervision labels and S1's oracle queries are recorded per model;
the jobs, evaluation and total wall seconds are recorded separately; every planned endpoint must be finite for every seed or the run is INCOMPLETE (no seed is dropped or replaced); a recorded run is never
resumed; the registration boundary is the commit that adds this file together with `SPEC_0D.json`, `zd_run.py`, `zd_models.py`, `test_zd.py`, `tcd_common/` and `dev_0d/` (the harness hashes them into `RUN_STARTED.json`
and refuses a dirty tree).

## 6. Self-audit (weaknesses the drafter knows)

| Weakness | Consequence | Acknowledgement |
|---|---|---|
| S1 was tuned to 9,283 parameters, 12 times C's 787 | C-versus-S1 compares unequal capacity; "equivalent" is then conservative for C, "joint better" is confounded with capacity | parameter counts are reported; the grid and trial budget were the same for every family |
| S1 queries the teacher's rule on its own selection; C does not | S1 gets extra supervision | counted and reported (`oracle_queries`); favours S1 |
| `a_joint` has a 10 degree step tolerance | flat models are penalized for angular noise below the tolerance's scale as well as for gross errors | the median step angle on moving states and the strata are reported |
| The teacher is a hand-written rule; everything is imitation | no claim about learning from outcomes | the next experiment |
| One sandbox; 30 seeds replicate it | intervals describe seed noise only | stated |
| Margins 0.03 and 0.06 were set by design, not measured | may be loose or tight | the report shows raw intervals so any other margin can be applied |
| Development already pointed toward "structure explains the gain" | risk of confirming a prior | the verdict rules, margins, seeds and settings were fixed before the recorded run; the run can refute (E2 or E3 outside its bounds) |
| 10 development seeds estimate the spread; S = 30 satisfies a normal-approximation rule | not a measured power | stated |
