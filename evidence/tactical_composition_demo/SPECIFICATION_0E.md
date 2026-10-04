# Experiment 0e — replacement and connection, two pieces (SPECIFICATION; exploratory; NOT a milestone, NOT C6 evidence)

Design: `PROPOSAL_0E.md` (after the GPT plan review `docs/reviews/tactical_0e_plan_review_gpt.md`), decisions in its section 12 (taken under the owner's delegation, decision 0028 item 9, **[R]**).
Development: `dev_0e/README.md` (steps 1 to 5, own entropy). Code: `ze_run.py` (the job and the verdict rules), `ze_core.py`, `ze_flat.py`, `tactics_e2.py`; tests `test_ze.py`, `test_ze_run.py`.
**First registered in `9583017`; corrected after the Codex pre-run review (`docs/reviews/tactical_0e_registration_review_codex.md`, CHANGES_REQUIRED, R1 to R5) in the commit that follows it, before any run. The run starts only from the corrected registration.** No recorded run may start until (1) Codex has reviewed the registered files and every fix has been re-reviewed, and (2) the owner has approved this specification in an explicit message that names it** (proposal section 7). Nothing here was chosen after a recorded result: none exists.

## 1. Changes from the proposal made in development (with their reason)

| Change | Reason (development record) |
|---|---|
| Task revision V3 of `tactics_e2.py` instead of the original sandbox | In the original sandbox the teacher with nearest-enemy targeting plays as well as the teacher, and a nearest-enemy message plays as well as the intact one: the teacher-necessity gate fails, so the connection cannot be shown useful there (step 3). V3 was selected by a fixed rule (step 4). **The author wrote the three variants and the rule before running step 4; git first records them together with the step-4 results (`9583017`), so this prospective timing is the author's account, not verified by the repository.** V3: glass-cannon ranged units (archer 40 hp, 12 damage; mage 45 hp, 8 damage), tank fighters (140 hp), random starts, mixed teams only, a damage-first targeting doctrine; the stepping rule and the opponents are unchanged. |
| Conventional comparator `Fp` is a per-slot structured conventional policy | None of the **tested flat recipes** clearly beats rush at 3,000 states (search: widths 32, 64, 128; depths 2, 3; continuous and 32-direction heads; one learning rate, decay and duration; the proposal's width 16, depth 4, mixture heads and duration/regularization tuning were **not** searched). On V3 the best flat recipe (width 128, the largest searched, depth 2) scored 0.452 against a paired rush mean of 0.410 (+0.042) over three search seeds, too few for an exact interval; whether it qualifies is decided by its gate in the recorded run. In the original task the best gain was 0.002. This is a statement about the tested recipes, not about flat networks in general. The per-slot policy (one network over the observation, one step per enemy slot, the step of the chosen slot) is the competent ordinary policy; it is named a structured conventional policy, not a flat one. The best flat network `Fflat` is reported and gated. |
| Stability under scale faults judged relative to the teacher | A ±10% scale fault changes the correct action near the task's sharp hold band: it costs the teacher as much as the learned unit (step 5). Noise and wrong-target faults stay absolute. |
| 300 episodes per opponent per cell | Measured spread (step 5): the exact intervals at 30 seeds are narrow against the bars; about an hour of wall time. |

## 2. What runs

One job per seed (`ze_run.run_seed`), **30 seeds**, 8 workers, through `tcd_common.harness.run_experiment` (one-shot latch `run_0e/`, smoke `smoke_run_0e/`). Per seed, on task V3: a training pool of 600 teacher-play episodes and an independent test pool of 100
(episode-level split), the doctrine's labels, 3,000 source states. Fitted once and frozen: **L** (AIM and MOVE taught separately; hidden 16, lr 0.001, decay 1e-4, 32,000 steps), **J** (the jointly trained conditional policy, 0d's S1 design;
hidden 64, lr 0.003, decay 1e-3, 16,000 steps), **Fp** (per-slot, width 32, depth 2), **Fflat** (continuous head, width 128, depth 2). Scripted: **O** (teacher AIM and MOVE), **D** (nearest-enemy AIM; approach-only MOVE), **R** (rush).
Closed-loop cells (300 paired episodes per opponent, rush and kiter, both mixes drawn from the V3 mixes on a roster keyed by seed, opponent and episode; wire-fault draws from a separate stream): R, Fp, Fflat; OO, LO, OL, LL, JJ, JL, LJ, DO, OD, OO|default,
FpO, OFp (output-channel hybrids taken from **Fp**, the per-slot policy: action-channel replacements, not target-conditioned module swaps); LL with the cuts default, wrong, zero; LL with the faults noise 0.02, 0.05, 0.10 (fractions of the reference distance 4.97), wrong-target 0.01, 0.05, 0.10, scale 0.9, 1.1, 0.5, 2;
OO with noise 0.02, wrong-target 0.01, scale 0.9, 1.1. Fixed-state joint fidelity on the test pool for every cell plus the directed control (reverse) and the semantics-preserving controls (relabel, sham). Weights and standardizers of L, J, Fp, Fflat
are saved per seed; the test-state digest is recorded.

## 3. Estimands

Win score W = mean of win 1, draw 0.5, loss 0 over the 300 episodes, averaged over the two opponents (actual win, loss, draw, timeout counts reported). Joint fidelity = share of multi-enemy test states where the chosen enemy is tied-best for the teacher's
doctrine AND the step matches the teacher's step toward that enemy (hold where it holds, otherwise within 10 degrees); disjoint strata hold, approach, back-off. Every contrast is paired within seed. Intervals: exact order-statistic intervals for the median of
per-seed values (two-sided, error 0.01 = the claim error for five claims; negative witnesses at 0.01 / m, m = the claim's number of components), Clopper-Pearson for the seed share, order-statistic bounds for the IQR, and normalized gains as the ratio of a numerator interval
and the headroom interval, each at half the error (for a negative witness, half of error / m each). No bootstrap enters a verdict. Strict inequalities; a value on a bar is INDETERMINATE.

## 4. Gates (enforced in code) and the five claims

**Gates and what each gates (enforced in code; `evaluate()` records this map).** Headroom D = W(OO) − W(R): lower bound > 0.15, and > 0.10 against each opponent → gates **B1**. Connection necessity (lower bound of W(OO) − W(OO|default) > 0.03) → gates **B1**.
Fp qualification (lower bound of the gain over rush > 0.03, positive against each opponent) → gates **B3**; Fflat's qualification is reported. **J qualification** (the same rule for JJ over rush) → gates **A2**. AIM necessity (DO) and MOVE necessity (OD) are **diagnostics only**: the task was qualified on them in development (step 4); they gate no claim.
Pool counts per seed: at least 100 uniquely-best multi-enemy states and 30 per stratum, else the seed errors and the run is INCOMPLETE. Start: the one-minute load must be at most 20. Invalid actions (a chosen identity out of range or not alive, a non-finite message or step, a snapshot with no living enemy) raise, so the seed records ERROR and the run is INCOMPLETE.

| Claim | Components (a positive claim needs every component; REFUTED needs a negative witness; otherwise INDETERMINATE) |
|---|---|
| **A1. Learned pieces replace the scripted ones** | L prequalification: AIM admissible > 0.85, MOVE success > 0.90, each stratum > 0.85; win LO−OO, OL−OO, LL−OO > −0.05 overall and per opponent; fidelity of each > −0.05 |
| **A2. Swap compatibility with the conventional conditional policy J** | win and fidelity JL−JJ and LJ−JJ > −0.03. Gated on J qualifying as a host. |
| **B1. Useful connection** | win LL − LL\|cut > 0.02 for cut = default, wrong, zero; normalized gain > 0.05 for each (positive interval at the claim error; negative witness at error / 7, like every other component); directed control: fidelity LL − LL\|reverse > 0.10. Gated on connection necessity and headroom. |
| **B2. Stable within the tested envelope** | function: win LL − R > 0.03; noise 0.02 and wrong-target 0.01: win loss < 0.03 and fidelity loss < 0.03; scale 0.9 and 1.1: (LL's loss) − (the teacher's loss under the same fault) < 0.03 for win and for fidelity; share of seeds with W(LL) − W(R) > 0.10: Clopper-Pearson lower bound > 0.80; IQR of W(LL) upper bound < 0.05 |
| **B3. Stronger than the qualified conventional baseline** | win LL − Fp > 0.03. Gated on Fp qualifying. Reported alongside: LL − Fflat and Fflat's gate. |

Development (step 5, five seeds, 100 episodes) suggests A1, A2, B1 and B2 will pass and B3 will not (Fp 0.747 against LL 0.742). That is an expectation, not a result; the recorded run decides.

## 5. Caps, cost, stop conditions

Measured cost about 600 s per seed (fits about 110 s, closed loop about 480 s); about an hour on 8 workers under the machine's typical load. Soft cap 7,200 s, hard cap 7,500 s, evaluation and summary bound 600 s. The run starts from a tree that is clean in the demo folder (the harness preflight checks that folder, not the whole repository, and records HEAD; it does not compare HEAD with the registration commit), with the load recorded. A missing, erroring or undersized seed makes the run INCOMPLETE: no seed is dropped or replaced, no resume, no retry. The stop rows of `PROPOSAL_0E.md` section 7 apply.

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
| Fault draws come from one sequential stream per episode, not keyed by tick, unit and edge | A different number of decisions (for example after a death) shifts later draws; episode starts stay paired. Closed-loop applied-fault counts are not recorded (only fixed-pool applied shares): no claim about realized closed-loop fault percentages. |
| Fidelity is measured on a common held-out pool, not on the states each policy meets in play | Stated; play itself is measured by the win score. |
| Not emitted: step magnitudes, the full AIM x MOVE matrix, switching envelopes, worst-case summaries, bootstrap descriptions, an IQR-difference endpoint | Deferred, not claimed; the registered cell set is the one listed in section 2; the IQRs of LL and Fp are reported descriptively only. |
| Stability under scale faults is relative to the teacher | A large absolute loss passes if the teacher loses as much; any report must name this qualification. |
| `Fp` computes per-slot labels for every slot (9,000 at 3,000 states) but is supervised only on living slots | Both counts are recorded (`oracle_queries`, `Fp_labels_computed`); no query-efficiency claim follows. |
| A1's prequalification covers L only; J's development back-off fidelity was 0.838 in one seed (seed 23) | J's competence enters only through A2's host gate (closed-loop play over rush). |
| Development step 5's fixed-state fault draws used Python's salted `hash` for stream keys | Raw development observations are kept; their exact regeneration is not established; the registered code uses stable enumerated keys. |
