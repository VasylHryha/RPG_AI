# Design 0h, revision 5: the bootstrap of atoms and the library (DRAFT for a Codex re-review; no growth experiment run)

Revision 5 answers the fourth review (`docs/reviews/tactical_0h_design_review_codex_r4.md`, CHANGES_REQUIRED, R4-1 … R4-9). Revision 4 answered the third (`…_r3.md`, R3-1 … R3-10), revision 3 the second (`…_r2.md`, R2-1 … R2-10) and revision 2 the first (`…codex.md`, 14 findings). The self-audits are in section 14. Earlier revisions are in git history (`85c656b`, `fc55cd2`, `b323803`, `69cc18c`).

**Scope:** the **bootstrap** only: atoms grow in one continuously running medium, are qualified structurally, and are copied into a snapshot library.
- Combinations, bonds, duplicates, library trends, yardstick efficiency claims and background claims are **deferred**.
- H-BG, H-PS and H-RBG are NOT_TESTED.

**Authorization:** decision 0028 item 17 covers engine parts and drafting. The development run of section 10 needs the owner's go-ahead after a passing Codex review.

**Dependencies:**
- the world `growing_shapes/world` with the additive `remember_static` (task id 7): READY, reviewed APPROVE_WITH_NOTES, merged at `9a797db`;
- the medium `growing_shapes/medium`: READY, reviewed APPROVE_WITH_NOTES (`growing_shapes_review_claude/MEDIUM_REVIEW.md`). **Its design-specific follow-up batch must be closed before section 10** (R4-2): a per-element gain inside the full driven RK4 RHS; world-step sampling with carried active-site histories (a strength change does not invalidate samples); undirected internal-pair cost; offset-aware coverage and partner eligibility; spiral placement. Engine readiness is not 0h implementation readiness.

The world's constants used here: dt_w = 0.1 s, 160 decisions = 16 s per episode, arena [−10, 10]², K ∈ {3, …, 8}.

## 1. Claim and assumption ledger

| Element | Status |
|---|---|
| C4 element law; the C4 criterion **functions** 1-5 and their thresholds; C5 interface fields | **accepted, reused** |
| The driven-history **adapter** for those criterion functions (section 6) | **new**: not accepted C4 evidence. **Atoms here are structurally qualified driven snapshots** (R3-9): a recovery under drive can come from common-input entrainment, so internally maintained closure and autonomous persistence are **not claimed** |
| The driven phase term (input drive) | **an addition** (as in the C6 R4 design) |
| Rate and gain adaptation; novelty birth; unlocked death; the budget | **motivated hypotheses** |
| One carrier band; the sensor ring and readout layout; distance salience; task-to-action bindings | **engineering choices** |
| The task reward (reward arm) and the choice of atom tasks | **additions** |

No arm is called "theory alone". The **task-blind arm** never uses a task score in learning, growth, death, qualification, snapshotting or the library.

## 2. Time, clocks and units

- **One continuous run clock** t (s). The medium is **never reset between episodes** (R2-2): positions, phases, ω, g, histories, timers and ids all carry over. Episodes follow each other with no gap.
- **Medium step:** n_sub = 5 RK4 steps of dt_m = 0.02 s per world step (dt_w = 0.1 s, exact).
- **The carrier** runs on the run clock: φ(t) = ω_D t, with ω_D = π rad/s (P_D = 2 s; 8 periods per episode). It is **not** reset per episode, so phase meaning is continuous.
- **Units:**
  - drive k: rad/s;
  - g: dimensionless, in [0, 2];
  - η_ω and η_g: 1/s;
  - PLV and coherence: in [0, 1];
  - the reward r: in [0, 1] (section 9);
  - cost: element units.
- **Measured timescales** (reported per atom; no separation is claimed):
  - P_D;
  - the phase relaxation τ_θ and the geometric relaxation τ_x, from the paired recovery futures of section 6, as the time for the RMS deviation between kicked and unkicked futures to fall below 1/e of its initial value, censored at the recovery horizon;
  - the adaptation times 1/η_ω and 1/η_g.

## 3. The forward map

**Sensors:**
- 8 sensor sites, evenly on a ring of radius 4 m.u. around the medium origin.
- **Logical slots and physical sites** (R4-3): each task's items occupy **logical slots** 0 … (number of items − 1), in the order the table below gives (perceive and choose: enemies in world id order; move: the target record = slot 0; remember_static: the enemy = slot 0). At each **episode start**, a permutation π_e of the 8 physical sites, drawn from the episode seed, maps logical slot j to physical site π_e(j). **This applies to every task**, single-item tasks included. The assignment holds for the episode, unused sites get k = 0, and the realized assignment is recorded for replay. **The per-task strength formulas in the table govern** every task.
- A site whose item changes between episodes jumps in ψ. Windows that cross that jump record lower PLV. This is accepted and declared.

**Per-task input binding** (legal observation fields only; R3-4):

| Task | Items → sites | Direction α | Strength k |
|---|---|---|---|
| perceive | each visible enemy → its slot's site | enemy angle | 2 · exp(−distance / 10) |
| move | the single target record → site 0 | target_angle if target_distance ≥ desired_range, else target_angle + π (retreat) | 2 · min(1, abs(target_distance − desired_range) / 2) |
| remember_static | the enemy → site 0 while visible; k = 0 while hidden | enemy angle | 2 · exp(−distance / 10) while visible |
| choose | each enemy → its slot's site | enemy angle | 2 · exp(−d / 10) × (1 + (1 − HP/100)) × (1 if d ≤ 2.5 else 0.5) |

- The move binding is a declared engineering transform of observed fields (desired range enters only through the retreat sign and the strength), and the controller may legitimately fail keep-mode episodes.
- The action's `choice` is −1 for every non-choice task.
- `remember_static` is the world's additive stationary-target task (id 7).

**Drive on element i:**

    dθ_i/dt += g_i · Σ_s k_s(t) · K(|x_i − q_s|) · sin(ψ_s(t) − θ_i),    K(r) = exp(−r²/2) for r ≤ 3, else 0 (σ_d = 1 m.u.)

with ψ_s(t) = φ(t) + α_s(t), where α_s is the item's world angle relative to the agent, from the observation.

**Strength:**
- k_s = 2 · exp(−d_s / 10) rad/s, with d in arena units.
- For choose, also × (1 + (1 − HP_s/100)) × (1 if d_s ≤ 2.5 else 0.5). These are disclosed priors.
- k_s = 0 for an invisible item (remember after disappearance) and for unused slots.

Observations are held over the 5 substeps.

**Readout:**
- Elements within 2 m.u. of the origin, weighted by K; Z = Σ w_i e^{iθ_i} / Σ w_i; coherence C = |Z|.
- **Abstain** if Σ w = 0 or C < 0.05.
- Decoded direction β = wrap(arg Z − φ(t)).

**Task-to-action table** (R2-6; legal world actions):

| Task | Action | On abstain |
|---|---|---|
| perceive | angle β; magnitude = clip(10 · ln(1/C), 0, √800) (a fixed monotone distance decode) | angle 0, magnitude 0 (scored as error) |
| move | angle β; magnitude min(1, C/0.8) (coherence-controlled speed) | angle 0, magnitude 0 |
| remember_static | angle β; magnitude 0 | angle 0, magnitude 0 |
| choose | choice = the live item with the smallest abs(wrap(β − α_s)), ties by lowest id; angle 0; magnitude 0 | the lowest live id (declared default) |

## 4. Initial state, update order and arms

**Initial state (run start only):**
- N_0 = 24 elements, uniform in a disk of radius 5 m.u.;
- phases uniform;
- ω_i = π · (1 + U(−0.1, 0.1));
- g_i = 0.5;
- ids 0-23, from a monotone id counter.

**Sampling contract** (R3-2):
- **Indexed contract** (R4-1): at world step k, after integration, sample k = (t_k, θ_i(t_k), and per site ψ_s(t_k), k_s(t_k)) is **appended first**. Every statistic of step k then uses samples **k − 99 … k** (the last 100, the current one included), pairing θ_i(t_j) with ψ_s(t_j) at the same t_j; the rate estimate also uses the endpoint k − 100. Adaptation, then timers and coverage, then (at their times) growth and qualification, all use this same window.
- **Rate estimate:** ω̂_i = (θ_i(t_k) − θ_i(t_{k−100})) / 10 s, unwrapped. It needs both endpoints (101 samples).
- **Gain signal:** P_i is defined only if i has samples k − 100 … k and s* (the site with the largest k_s · K at step k; ties by lowest site id) was active in ≥ 80 of samples k − 99 … k; then P_i = PLV(θ_i, ψ_s*) over those active samples. **Otherwise, including when no active site reaches i, P_i is undefined and g_i is unchanged this step** (the only no-drive rule).
- **Coverage** additionally requires the candidate element to have ≥ 101 samples.
- **Reward eligibility:** e_i is the mean of the defined P_i values in the episode, and 0 if none is defined.
- g is clipped to [0, 2] after every update, including reward updates.

**Per world step:**
1. read the observation and set the drives;
2. 5 × (one RK4 step of the full driven C4 RHS, with neighbours held per step);
3. append sample k (indexed contract);
4. adaptation (below), using samples up to and including k;
5. update the timers (section 5);
6. every τ_l = 20 s (200 world steps), run the growth check (section 5);
7. every 60 s, run the qualification check (section 6);
8. decode and act (section 3).

**Adaptation (both arms, identical):**
- dω_i/dt = η_ω (ω̂_i − ω_i), with ω̂_i from the sampling contract, applied only when it is defined. ω is clipped to π · [0.5, 1.5].
- dg_i/dt = η_g (P_i − g_i) when P_i is defined (sampling contract); otherwise no change. g is clipped to [0, 2].
- η_ω = η_g = 0.05 /s; forward Euler per world step.

**The two arms (R2-1):** both have the **same structural qualification, snapshots and library** (sections 6-7).
- The **task-blind arm** has no reward term.
- The **reward arm** adds exactly one term at each episode end:
  - Δg_i = 0.5 · (r − r̄) · e_i, with e_i from the sampling contract, then g clipped to [0, 2];
  - then r̄ ← r̄ + 0.1 (r − r̄), with r̄ = 0.5 at the run start and never reset;
  - r is the bounded reward of section 9.

  **There is no task-based admission in either arm.** Competence is measured for both, afterwards, by the evaluator.

## 5. Growth and death: B1, D1, D3 (R2-4, R2-7)

**Samples:** histories hold one sample per world step (10 per second). The window W = 10 s = 100 samples.

**Active partners:**
- A sensor site counts as a partner of element i for a sample only if k_s > 0 and K(|x_i − q_s|) > 0 at that sample.
- A C4 neighbour (k ≤ 8 within radius 3, as C4) counts at the samples where it is a neighbour.
- A partner is **eligible** if it was active in ≥ 80 of the last 100 samples. Its PLV is computed over those active samples only.

**Measurements:**
- **Lock** L(i) = the maximum PLV over eligible partners. It is undefined until i has 100 samples (a newborn's warm-up); with no eligible partner, L(i) = 0.
- **Coverage of site s:** some element within 3 m.u. of q_s with PLV(θ_i, ψ_s) ≥ 0.8 **and** |circular mean of wrap(θ_i − ψ_s)| ≤ 0.5 rad, over the samples where s was active, with s active in ≥ 80 of the last 100 samples.

**Timers** (updated every world step):
- **D1 timer of i:** increases by dt_w while L(i) is defined and < 0.5; resets to 0 when L(i) ≥ 0.5 or is undefined.
- **B1 timer of s:** increases while s is active and not covered; resets to 0 when covered, inactive, or after a birth at s.

**Growth check every 20 s, in order:**

| Step | Rule | Condition | Action |
|---|---|---|---|
| 1 | D1 | not protected, and D1 timer ≥ 40 s | remove i |
| 2 | D3 | cost > 64 | remove unprotected elements by lowest L(i) (undefined counts as 0), ties by lowest id, recomputing cost after each, until cost ≤ 64; if only protected elements remain, flag a **protected over-budget** state and block births this check |
| 3 | B1 | B1 timer of s ≥ 20 s | in site-id order, at most 2 births: each accepted only if N + 1 ≤ 64 **and** the cost with the newborn ≤ 64; a rejection is logged with its reason (`cap` or `cost`) |

- **Cost** = N + 0.1 × the number of **undirected neighbour pairs** (the union of the directed k ≤ 8 lists within radius 3). It is recomputed after every removal or birth.
- **Placement of a newborn at site s:** the first point on the fixed spiral q_s + 0.1 j (cos j·2.39996, sin j·2.39996), j = 0 … 49, that is ≥ 0.05 m.u. from every element. If none exists, the birth is rejected and logged (`placement`).
- **Newborn:** phase ψ_s(t), ω = π, g = 1, the next monotone id, empty histories, protected for 20 s.
- **Logging:** every event is logged with its time, rule, ids, the triggering values and the cost.

## 6. Structural qualification: the C4 criterion functions on a driven adapter (R2-3)

**Every 60 s, a qualification check:**
- **Cohort:** the elements alive for the whole last 60 s (immutable ids). Entrants and leavers in the window are excluded from that check; missing frames are impossible within the cohort.
- **Frames** (R3-1): **601 endpoint-inclusive frames** at t_check − 60 + 0.1 j, j = 0 … 600, giving two exact 30-second halves for the frozen window function. The id mapping is fixed. A cohort with fewer than 3 elements yields no candidate (logged).
- **Aliasing** (R3-10): the revision-2 counter-example (rates 0.5ω_D and 1.5ω_D) remains a negative contract. No general rate bound is claimed: coupling and drive add to the intrinsic spread. Each check reports the maximum wrapped per-frame relative-phase increment among candidate pairs; a check with any increment > π/2 is flagged **possibly aliased**, and its candidates are not snapshotted. The flag is a **warning screen only**: a wrapped increment cannot see whole turns of 2π between frames, so it does not certify the absence of aliasing (R4-9).
- **Criteria 1-4:** the accepted criterion functions on these frames, with C4 thresholds and C5-style scaling by **T = 2** (s per C4 time unit):

| Threshold | C4 value | Here |
|---|---|---|
| window | 30 | 60 s |
| link factor, min size, membership Jaccard, shape CV, lock SD, pattern tol | 1.5, 3, 0.95, 0.05, 0.1 rad, 0.1 rad | same |
| frequency tolerance | 0.01 per C4 time unit | 0.005 rad/s |
| recovery time | 30 | 60 s |
| kick: position RMS, phase RMS | 0.1 × the median spacing, 0.3 rad | same |
| recovery Jaccard | 0.9 | same |

**The check-time state** (R3-3):
- At t_check the **complete live medium state** is saved immutably: all elements alive then, including entrants, with their coefficients and the clock.
- The recovery futures start from it **with all elements present**, so entrants exert their forces.
- Membership comparisons are restricted to the cohort (entrants masked out), and the claim is labelled cohort-restricted.
- **The template is taken from this saved state.** Admission is at completion (t_check + 60), with both timestamps recorded. A later death of the live source does not affect an admitted snapshot.
- Recovery never modifies the live run.

**Criterion 5, recovery** (paired futures from the snapshot at the check):
- **Open-loop input replay:** both futures receive the **recorded drive schedule** of the next 60 s of the actual run: per world step and site, ψ_s on the original run clock and k_s, with each episode's sensor assignment already applied.
- **Relaxation estimators** over the candidate's cohort members:
  - phase: RMS of wrap(θ_kick − θ_ctrl) after removing the circular-mean difference;
  - position: RMS of (x_kick − x_ctrl) after removing the centroid shift;
  - τ is the first fall below 1/e of the initial deviation, censored at 60 s (flagged).
- **Plasticity, growth and reward are off** in both futures.
- The kicked future applies the kicks of the table above. Both futures integrate the driven C4 law.
- **Pass** if all three Jaccards are ≥ 0.9 and the recovered pair-pattern error is ≤ 0.1 rad.
- τ_θ and τ_x are measured from the same futures.

**A diagnostic, not required:** the same recovery with the drive off (autonomous persistence).

**A qualified group becomes a snapshot (section 7). The live group is not frozen:** the library is a snapshot and does not alter the run. A live group that qualifies again later is snapshotted again only if its template hash differs from all its earlier snapshots.

**Failures:** degenerate groups (size < 3, zero spacing, a degenerate hull) fail.

## 7. Templates, copies and identity (R2-6)

- **Template:**
  - per member: position relative to the medium origin, phase minus φ(t_snap), ω, g;
  - the task bindings as a **rule**, not a realized list: {"binding_rule": "episode_seed_permutation_v1", "physical_sites": 8, "slot_order": "per-task table, section 3"} (R4-3). Evaluation copies apply the same rule with each evaluation episode's seed.
  - the constants version.
- **Content hash** (R3-8, R4-3): sha256 of the canonical JSON: members in **ascending persistent id**, each [rel x, rel y, phase offset, ω, g]; the binding rule object above; the constants version; sorted keys; floats by repr.
- **Copy for evaluation** (an isolated extracted group): an **empty** medium (no other elements) with the same sensor ring and readout geometry. The members are placed at their stored positions (identity pose). Phases are θ = stored offset + φ(t_copy), a uniform shift, so zero-resultant groups are handled.
- **Plasticity and growth are off** during evaluation. The drive is on, from the evaluation episodes. **A fresh copy is made for each evaluation episode** (R3-8), with its run clock starting at the copy time.
- A copy whose readout region contains no member **abstains**. That is scored, not dropped.
- **Type id** = the content hash (immutable). Instances get monotone ids.

## 8. Competence (evaluator only)

- **Panel:** validation episodes 0-127 of each usable atom task, fixed.
- **Per-episode fresh copies** (R4-6): for every evaluation episode, a new isolated copy is instantiated from the saved template (section 7) at carrier offset 0, so its first frame has φ(t_copy) ≡ 0 mod 2π, with the episode's seeded binding. Positions and phases are never carried between episodes. The same procedure applies to the final whole-medium competence of G0, with the whole live state as the template. An empty-readout abstention is a scored episode.
- **Competence** is the unclipped normalized score n (section 9) per task. The reports give n per task and the best task per atom.
- In **both arms** the library holds every qualified snapshot. Competence never changes the library or the run.

## 9. Scores, reward and usable tasks (R2-5)

**Primary score per task:**

| Task | Primary score | Orientation |
|---|---|---|
| perceive | angular error | error, so negate |
| move | goal error | negate |
| remember_static | hidden angular error | negate |
| choose | correct-choice rate | as is |

**Normalized score:** n = (s − s_rand) / (s_ref − s_rand), on the oriented scores.
- The reference and random estimates come from the world's validation episodes 0-255.
- They are **frozen before any medium training.**

**Usable task:** the paired difference (reference − random) over those 256 episodes has
- mean > 0;
- mean > 3 × SE, with SE = the sample SD of the differences / √256;
- a finite, positive denominator.

The usable list is **frozen before training** and shared by both arms. The world report shows wide separation for all four tasks, including `remember_static` (reference 0 against random 1.58 rad); the frozen list is computed by the rule above from the world's validation episodes 0-255.

**The reward** (reward arm only) is r = clip(n, 0, 1) on the episode's task.

## 10. The development run (attainability only)

- **All constants above are fixed.**
- **Per arm:** 8 independent medium seeds, 2,000 episodes per seed. At 16 s per episode that is **32,000 s** of run time (R3-5).
- **Fixed rotation** (R4-5): the order perceive, move, remember_static, choose, **filtered through the frozen usable-task list**, in blocks of 20 episodes, cyclic. The same schedule applies to both arms and their controls. The run clock is t = 16 · episode + 0.1 · step.
- **Qualification checks** start at t = 60 m, m = 1 … 532. The last start is 31,920 s, whose replay ends at 31,980 s. No check is scheduled whose replay would exceed the run, and the reported horizon is 32,000 s.
- **Exposure ledger, reported:**
  - training world steps and episodes;
  - qualification frames (they include driven observations but no task score);
  - recovery-future simulated time;
  - evaluator episodes (separate, validation namespace);
  - for the reward arm, reward-carrying episodes.
- **Accounting, reported and not compared:** learned coefficients 2 per element (peak and final), retained state (positions and phases), unique template storage (scalars per template) and instantiated evaluation copies.
- **Yardsticks (GRU, MLP, fixed-size medium, gradient medium) are deferred** (R2-9). There is no efficiency claim in this revision.

## 11. Development read-outs (seed = unit; 8 per arm; PASS / FAIL / INCONCLUSIVE / INVALID)

| ID | Estimand per seed | PASS | FAIL | INCONCLUSIVE |
|---|---|---|---|---|
| **G0** (narrowed, R3-6: **two budget-constrained growth policies compared**, conditional against random placement-and-phase; not a matched-placement effect) | **Coverage** = the mean, over samples in the last 20% with ≥ 1 active site, of the fraction of active sites covered (eligible exposure reported; a seed with no eligible sample is INVALID). **Medium competence** = the mean n over usable tasks of the whole live medium at the end, by the per-episode copy procedure (section 8), on the evaluator panel. **Control:** see the control-queue rule below the table | conditional > control on both, in ≥ 6 of 8 unflagged seeds | conditional ≤ control on both, in ≥ 6 of 8 | otherwise |
| **G0'** (narrowed, R3-7: **count stability under the declared budget**; budget regulation is reported, not excluded) | the OLS slope of N over the growth checks in the last 20%; no birth rejected for cap, cost or placement and no protected-over-budget state in the last 20%; D3 removals and turnover reported | slope within ±0.5 per 100 episodes and no rejection, in ≥ 6 of 8 seeds | outside the band or any rejection, in ≥ 3 of 8 | otherwise |
| **G1** | ≥ 1 qualified snapshot in the run | in ≥ 6 of 8 seeds | in ≤ 2 of 8 | otherwise |
| **G1c** | competence of the snapshots, descriptive (per task and best task) | (descriptive) | | |
| **G5** (**copy-covariance numerical check**, R4-9; not a test of usefulness or persistence: two copies differing only by a uniform carrier-phase shift are mathematically equivalent, so D should be 0 up to numerics) | per snapshot, D = the maximum over usable tasks of abs(n₁ − n₂) between two per-episode copies at carrier offsets 0 and π on the same panel and bindings; per seed, the fraction of its snapshots with D ≤ 0.1 | by the ordered rule below the table | | |

**G0 control-queue rule** (R4-4):
- The control run has **B1 off**. D1 and D3 are as in the intact run.
- At each growth check, the control **enqueues** one request for every birth the intact run made at that check, in a first-in first-out queue.
- Then it attempts up to **2 placements per check** from the head of the queue, retries included.
- **A placement draw:** a position uniform in the disk of radius 5 m.u. and a phase uniform in [0, 2π). Draws come from the control's own entropy domain ("g0_control", paired by medium seed) and are redrawn on every attempt.
- **Feasible** if N + 1 ≤ 64, the cost with the newborn ≤ 64, and the position is ≥ 0.05 m.u. from every element. A feasible newborn has ω = π, g = 1 and the same protection as an intact newborn.
- **A request is attempted at most twice** (once, plus one retry at a later check), then dropped and logged. Requests still pending after the last check (t = 32,000 s) are dropped and logged.
- **A seed with any dropped request is flagged, and a flagged seed counts as non-PASS.**
- **Reported:** actual control additions, deaths, retries and drops against the intact run.

**G5 ordered rule** (R4-7):
1. INVALID if an execution or measurement failure applies;
2. else INCONCLUSIVE if fewer than 6 seeds have ≥ 1 snapshot (the no-formation count is reported);
3. else PASS if the fraction is ≥ 0.8 in ≥ 6 snapshot-bearing seeds;
4. else FAIL if the fraction is < 0.5 in ≥ 3 snapshot-bearing seeds;
5. else INCONCLUSIVE.

The same order applies to every row: INVALID first, then the row's own cuts.

**INVALID**, not FAIL: a non-finite measurement, zero usable tasks, or an incomplete or interrupted run. The raw evidence is kept, and the reason is reported.

## 12. Stop rows (yes/no; one action; one role)

| Question | Yes → action | Role |
|---|---|---|
| Is the world, `remember_static` or the medium missing or NOT_READY, **or is the medium's design-specific follow-up batch (R4-2) not closed and reviewed**? | Do not start section 10 | implementer |
| Is the usable-task list empty? | Report INVALID; do not start section 10 | implementer |
| Is a read-out INVALID? | Report it with the raw evidence; do not reinterpret it as FAIL or PASS | implementer |
| Does G1 FAIL in the task-blind arm? | Write the failure report; stop development | drafter |
| Does G0' FAIL? | Write the failure report; stop development | drafter |
| Is **any** protocol element (constant, schedule, reset rule, control, estimator, binding) changed after seeing development results? | Make a new design revision with fresh development seeds, and identify any reused evidence | drafter |
| Has development stopped and is a next step needed? | Ask the owner to decide | owner |

## 13. What this revision tests, in one sentence

Whether, in a continuously driven C4 medium with novelty birth, unlocked death and a budget: **structurally qualified driven groups (atoms) form**; **conditional growth beats a random growth policy**; **the element count is stable under the budget**; and **atoms copy reproducibly**. Competence on simple tasks is measured afterwards, and never fed back in the task-blind arm.

## 14. Self-audits

**Revision-2 findings:**

| # | Finding | Fix | Cause |
|---|---|---|---|
| R2-1 | Arms differed by reward **and** admission; the freeze lifecycle conflicted | One admission rule for both arms (structural); live groups never frozen; the library is snapshots | I mixed policy with lifecycle |
| R2-2 | Episode boundaries undefined | One continuous run clock; no resets; carried state; declared site jumps | I assumed per-episode media |
| R2-3 | The detector adapter was incomplete; P_D sampling aliases | Fixed cohort, 0.1 s frames (with the counter-example as a negative contract), a scaled threshold table, open-loop replay futures with plasticity off | I named the procedure without an adapter |
| R2-4 | Window, timer and event semantics | Active-partner eligibility, timers every step, an exact check order, the spiral placement, monotone ids | Underspecified |
| R2-5 | n is not a bounded reward; screening | r = clip(n); n unclipped for reports; an exact usable-task rule frozen before training | I conflated reward and score |
| R2-6 | Copies not reproducible | An isolated empty-medium copy, identity pose, a uniform phase shift, the canonical hash, the action table | Underspecified |
| R2-7 | Settling could be cost-forced | Any rejection reason disqualifies; the claim is count settling only | The cap was defined narrowly |
| R2-8 | G0 and G5 not executable | Exact control and estimands; G5 as behavioural reproducibility with seed aggregation | Underspecified |
| R2-9 | Comparator accounting discretionary | Yardsticks deferred; accounting reported, not compared | Out of the active scope |
| R2-10 | Revision rules limited to constants | Every protocol change becomes a new revision; INVALID and INCOMPLETE dispositions; yes/no rows | Too narrow |

**Revision-3 findings:**

| # | Finding | Fix | Cause |
|---|---|---|---|
| R3-1 | 600 frames break the frozen window function | 601 endpoint-inclusive frames; a small-cohort disposition | Off-by-one; I did not read the function's indexing |
| R3-2 | Short-history cases | A timestamped sampling contract; undefined P leaves g unchanged; coverage needs history; newborn eligibility | Gaps |
| R3-3 | Recovery population and snapshot timing | A full check-time state; cohort-restricted membership; the template from the saved state; exact drive-schedule replay; estimators | Underspecified |
| R3-4 | Move lacked an input binding | A per-task input table; choice = −1 | I assumed enemies in every task |
| R3-5 | 2,000 episodes are 32,000 s | Corrected; the rotation; the last qualifying check | An arithmetic error |
| R3-6 | G0 denominator and an unmatched control | An eligible-exposure denominator; narrowed; flagged seeds non-PASS | Underspecified |
| R3-7 | G0' allowed D3-enforced settling | Narrowed to count stability under the budget | Overclaim |
| R3-8 | G5 aggregation and copy identity | A per-snapshot scalar, thresholds, a no-formation rule, fixed offsets, per-episode copies, canonical order | Underspecified |
| R3-9 | Driven recovery can be entrainment | Atoms are driven snapshots; closure and autonomy not claimed | Missed the drive's restoring force |
| R3-10 | A false rate bound | Removed; aliasing diagnostics and a flag; the counter-example kept | Wrong reasoning |

**Revision-4 findings:**

| # | Finding | Fix | Cause |
|---|---|---|---|
| R4-1 | Two no-drive gain rules; endpoint ambiguity | One rule (undefined, so unchanged); an indexed contract: append first, then every statistic over samples k − 99 … k | A clause left from revision 3 |
| R4-2 | Engine readiness is not design readiness | The dependency and stop row require the medium follow-up batch | Not referenced |
| R4-3 | Site assignment and template bindings differed | Logical slots and physical sites; one permutation rule for all tasks; the binding rule hashed, not a list | Mixed concepts |
| R4-4 | G0 control retry queue and terminal case undefined | A FIFO queue, 2 attempts per check, 2 per request, a redraw domain, a terminal drop rule, flags | Underspecified |
| R4-5 | Rotation ignored the usable list | Filtered through the frozen list | An oversight |
| R4-6 | Section 8 kept the old copy lifecycle | Per-episode fresh copies everywhere, carrier offset 0 | Partial edit |
| R4-7 | Two G5 verdicts possible | An ordered rule | No precedence |
| R4-8 | Stale dependency prose; table pipes | Refreshed; abs() | Cleanup |
| R4-9 | Alias flag and G5 overread | The flag labelled a warning screen; G5 labelled a copy-covariance numerical check | Overclaim |

**Revision-1 findings** (14, fixed in revision 2 except as refined later): see revision 2 in git history (`fc55cd2`, section 13).
