# Experiment 0e — replacement and connection, two pieces (SPECIFICATION; exploratory; NOT a milestone, NOT C6 evidence)

Design: `PROPOSAL_0E.md` (after the GPT plan review `docs/reviews/tactical_0e_plan_review_gpt.md`), decisions in its section 12 (taken under the owner's delegation, decision 0028 item 9, **[R]**).
Development: `dev_0e/README.md` (steps 1 to 5, own entropy). Code: `ze_run.py` (the job and the verdict rules), `ze_core.py`, `ze_flat.py`, `tactics_e2.py`; tests `test_ze.py`, `test_ze_run.py`.
**This specification is registered at the commit that adds it together with `SPEC_0E.json`. No recorded run may start until (1) Codex has reviewed the registered files and every fix has been re-reviewed, and (2) the owner has approved this specification in an explicit message that names it** (proposal section 7). Nothing here was chosen after a recorded result: none exists.

## 1. Changes from the proposal made in development (with their reason)

| Change | Reason (development record) |
|---|---|
| Task revision V3 of `tactics_e2.py` instead of the original sandbox | In the original sandbox the teacher with nearest-enemy targeting plays as well as the teacher, and a nearest-enemy message plays as well as the intact one: the teacher-necessity gate fails, so the connection cannot be shown useful there (step 3). V3 was selected by a rule fixed before measurement (step 4): glass-cannon ranged units (archer 40 hp, 12 damage; mage 45 hp, 8 damage), tank fighters (140 hp), random starts, mixed teams only, a damage-first targeting doctrine; the stepping rule and the opponents are unchanged. |
| Conventional comparator `Fp` is a per-slot structured conventional policy | No truly flat network beats rush by more than 0.04 at 3,000 states in either task (steps 2 and 5). The per-slot policy (one network over the observation, one step per enemy slot, the step of the chosen slot) is the competent ordinary policy; it is named a structured conventional policy, not a flat one. The best flat network `Fflat` is reported and gated. |
| Stability under scale faults judged relative to the teacher | A ±10% scale fault changes the correct action near the task's sharp hold band: it costs the teacher as much as the learned unit (step 5). Noise and wrong-target faults stay absolute. |
| 300 episodes per opponent per cell | Measured spread (step 5): the exact intervals at 30 seeds are narrow against the bars; about an hour of wall time. |

## 2. What runs

One job per seed (`ze_run.run_seed`), **30 seeds**, 8 workers, through `tcd_common.harness.run_experiment` (one-shot latch `run_0e/`, smoke `smoke_run_0e/`). Per seed, on task V3: a training pool of 600 teacher-play episodes and an independent test pool of 100
(episode-level split), the doctrine's labels, 3,000 source states. Fitted once and frozen: **L** (AIM and MOVE taught separately; hidden 16, lr 0.001, decay 1e-4, 32,000 steps), **J** (the jointly trained conditional policy, 0d's S1 design;
hidden 64, lr 0.003, decay 1e-3, 16,000 steps), **Fp** (per-slot, width 32, depth 2), **Fflat** (continuous head, width 128, depth 2). Scripted: **O** (teacher AIM and MOVE), **D** (nearest-enemy AIM; approach-only MOVE), **R** (rush).
Closed-loop cells (300 paired episodes per opponent, rush and kiter, both mixes drawn from the V3 mixes on a roster keyed by seed, opponent and episode; wire-fault draws from a separate stream): R, Fp, Fflat; OO, LO, OL, LL, JJ, JL, LJ, DO, OD, OO|default,
FhO, OFh (flat-output hybrids, labelled action-channel replacements); LL with the cuts default, wrong, zero; LL with the faults noise 0.02, 0.05, 0.10 (fractions of the reference distance 4.97), wrong-target 0.01, 0.05, 0.10, scale 0.9, 1.1, 0.5, 2;
OO with noise 0.02, wrong-target 0.01, scale 0.9, 1.1. Fixed-state joint fidelity on the test pool for every cell plus the directed control (reverse) and the semantics-preserving controls (relabel, sham). Weights and standardizers of L, J, Fp, Fflat
are saved per seed; the test-state digest is recorded.

## 3. Estimands

Win score W = mean of win 1, draw 0.5, loss 0 over the 300 episodes, averaged over the two opponents (actual win, loss, draw, timeout counts reported). Joint fidelity = share of multi-enemy test states where the chosen enemy is tied-best for the teacher's
doctrine AND the step matches the teacher's step toward that enemy (hold where it holds, otherwise within 10 degrees); disjoint strata hold, approach, back-off. Every contrast is paired within seed. Intervals: exact order-statistic intervals for the median of
per-seed values (two-sided, error 0.0125 = the claim error; negative witnesses at 0.0125 / m, m = the claim's number of components), Clopper-Pearson for the seed share, order-statistic bounds for the IQR, and normalized gains as the ratio of a numerator interval
and the headroom interval, each at half the error. No bootstrap enters a verdict. Strict inequalities; a value on a bar is INDETERMINATE.

## 4. Gates (enforced in code) and the four claims

**Gates.** Headroom D = W(OO) − W(R): lower bound > 0.15, and > 0.10 against each opponent. Teacher necessity (lower bound of W(OO) minus the alternative > 0.03): AIM (DO), connection (OO|default), MOVE (OD). Baseline qualification (Fp, and Fflat): lower bound of the gain over rush > 0.03 and positive
against each opponent. Pool counts per seed: at least 100 uniquely-best multi-enemy states and 30 per stratum, else the seed errors and the run is INCOMPLETE. Start: the one-minute load must be at most 20.

| Claim | Components (a positive claim needs every component; REFUTED needs a negative witness; otherwise INDETERMINATE) |
|---|---|
| **A. Replacement** | L prequalification: AIM admissible > 0.85, MOVE success > 0.90, each stratum > 0.85; win LO−OO, OL−OO, LL−OO > −0.05 overall and per opponent; fidelity of each > −0.05; win and fidelity JL−JJ and LJ−JJ > −0.03 |
| **B1. Useful connection** | win LL − LL\|cut > 0.02 for cut = default, wrong, zero; normalized gain > 0.05 for each; directed control: fidelity LL − LL\|reverse > 0.10. Gated on connection necessity and headroom. |
| **B2. Stable within the tested envelope** | function: win LL − R > 0.03; noise 0.02 and wrong-target 0.01: win loss < 0.03 and fidelity loss < 0.03; scale 0.9 and 1.1: (LL's loss) − (the teacher's loss under the same fault) < 0.03 for win and for fidelity; share of seeds with W(LL) − W(R) > 0.10: Clopper-Pearson lower bound > 0.80; IQR of W(LL) upper bound < 0.05 |
| **B3. Stronger than the qualified conventional baseline** | win LL − Fp > 0.03. Gated on Fp qualifying. Reported alongside: LL − Fflat and Fflat's gate. |

Development (step 5, five seeds, 100 episodes) suggests A, B1 and B2 will pass and B3 will not (Fp 0.747 against LL 0.742). That is an expectation, not a result; the recorded run decides.

## 5. Caps, cost, stop conditions

Measured cost about 600 s per seed (fits about 110 s, closed loop about 480 s); about an hour on 8 workers under the machine's typical load. Soft cap 7,200 s, hard cap 7,500 s, evaluation and summary bound 600 s. The run starts from a clean tree at the registration commit (preflight)
with the load recorded. A missing, erroring or undersized seed makes the run INCOMPLETE: no seed is dropped or replaced, no resume, no retry. The stop rows of `PROPOSAL_0E.md` section 7 apply.

## 6. Self-audit (known weaknesses)

| Weakness | Acknowledgement |
|---|---|
| The task was revised in development to make the connection matter, and the variant was chosen by a rule fixed before measuring it | The selection rule and all three variants are recorded (`tactics_e2.py`, step 4); V3 is the only variant that passed; the claims are statements about V3. |
| The interface is hand-specified; nothing here tests discovery of a connection | Stated; discovery is the next proposal. |
| One sandbox, scripted teacher, imitation; 30 seeds replicate one environment | Intervals describe seed noise only; no RRG, geometry or oscillator claim. |
| J was not re-tuned for V3 (0d's S1 recipe), L uses 0d's C recipe | Both pass prequalification on V3 (step 5); the replacement bars are noninferiority against O and against J. |
| `Fp` gets counterfactual teacher queries for every living slot (per-slot labels); J queries the teacher on its own choice | Counted and reported (`oracle_queries`). |
| B3 is expected to fail | It is kept as registered: a competent conventional policy matching the pieces is an informative result for the owner's question. |
| The margins (0.02 to 0.05) are design choices | Raw intervals are reported so other margins can be applied. |
| Development previewed most outcomes on separate seeds | Disclosed (`dev_0e/README.md`); every setting was fixed from development before registration. |
