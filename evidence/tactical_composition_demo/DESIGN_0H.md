# Design 0h, revision 3: the bootstrap of atoms and the library (DRAFT for a Codex re-review; no growth experiment run)

Revision 3 answers the Codex re-review of revision 2 (`docs/reviews/tactical_0h_design_review_codex_r2.md`, CHANGES_REQUIRED, 10 findings R2-1 … R2-10). Revision 1 had 14 findings (`docs/reviews/tactical_0h_design_review_codex.md`). The self-audits are section 14. Earlier revisions are in git history (`85c656b`, `fc55cd2`, `d0264cb`).

**Scope:** the **bootstrap** only: atoms grow in one continuously running medium, are qualified structurally, and are copied into a snapshot library.
- Combinations, bonds, duplicates, library trends, yardstick efficiency claims and background claims are **deferred**.
- H-BG, H-PS and H-RBG are NOT_TESTED.

**Authorization:** decision 0028 item 17 covers engine parts and drafting. The development run of section 10 needs the owner's go-ahead after a passing Codex review.

**Dependencies:**
- the world `growing_shapes/world` (READY, reviewed APPROVE_WITH_NOTES), plus its additive `remember_static` task (being added);
- the medium `growing_shapes/medium` (being built).

The world's constants used here: dt_w = 0.1 s, 160 decisions = 16 s per episode, arena [−10, 10]², K ∈ {3, …, 8}.

## 1. Claim and assumption ledger

| Element | Status |
|---|---|
| C4 element law; the C4 criterion **functions** 1-5 and their thresholds; C5 interface fields | **accepted, reused** |
| The driven-history **adapter** for those criterion functions (section 6) | **new**: its driven qualification is not accepted C4 evidence |
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
- At each **episode start**, the episode's items are assigned to sites by a permutation drawn from the episode seed. The assignment holds for the episode, and unused sites get k = 0.
- A site whose item changes between episodes jumps in ψ. Windows that cross that jump record lower PLV. This is accepted and declared.

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
| choose | choice = the live item with the smallest |wrap(β − α_s)|, ties by lowest id; angle 0; magnitude 0 | the lowest live id (declared default) |

## 4. Initial state, update order and arms

**Initial state (run start only):**
- N_0 = 24 elements, uniform in a disk of radius 5 m.u.;
- phases uniform;
- ω_i = π · (1 + U(−0.1, 0.1));
- g_i = 0.5;
- ids 0-23, from a monotone id counter.

**Per world step:**
1. read the observation;
2. 5 × (drive + one C4 RK4 step, with neighbours held per step);
3. adaptation (section 4, below);
4. append samples to the histories;
5. update the timers (section 5);
6. every τ_l = 20 s (200 world steps), run the growth check (section 5);
7. every 60 s, run the qualification check (section 6);
8. decode and act (section 3).

**Adaptation (both arms, identical):**
- dω_i/dt = η_ω (ω̂_i − ω_i), with ω̂_i = (unwrapped θ_i(t) − θ_i(t − W)) / W − (drive-free bias: none). It is applied only once i has a full window W = 10 s. ω is clipped to π · [0.5, 1.5].
- dg_i/dt = η_g (P_i − g_i), with P_i = PLV(θ_i, ψ_s*) over W, where s* is the site with the largest k_s · K at the step (ties by lowest site id). P_i = 0 when no active site reaches i. g is clipped to [0, 2].
- η_ω = η_g = 0.05 /s; forward Euler per world step.

**The two arms (R2-1):** both have the **same structural qualification, snapshots and library** (sections 6-7).
- The **task-blind arm** has no reward term.
- The **reward arm** adds exactly one term at each episode end:
  - Δg_i = 0.5 · (r − r̄) · e_i, where e_i is the episode mean of P_i, clipped;
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
- **Frames:** every world step (0.1 s; 600 frames). This **avoids the stroboscopic aliasing** of carrier-period sampling: the relative phase rate is ≤ π rad/s, so the step is ≤ 0.31 rad per frame. The S3-style contract includes the reviewer's counter-example (rates 0.5ω_D and 1.5ω_D), which must **not** register as locked.
- **Criteria 1-4:** the accepted criterion functions on these frames, with C4 thresholds and C5-style scaling by **T = 2** (s per C4 time unit):

| Threshold | C4 value | Here |
|---|---|---|
| window | 30 | 60 s |
| link factor, min size, membership Jaccard, shape CV, lock SD, pattern tol | 1.5, 3, 0.95, 0.05, 0.1 rad, 0.1 rad | same |
| frequency tolerance | 0.01 per C4 time unit | 0.005 rad/s |
| recovery time | 30 | 60 s |
| kick: position RMS, phase RMS | 0.1 × the median spacing, 0.3 rad | same |
| recovery Jaccard | 0.9 | same |

**Criterion 5, recovery** (paired futures from the snapshot at the check):
- **Open-loop input replay:** both futures receive the **identical recorded legal observations** of the next 60 s of the actual run. If the run has not produced them yet, the check completes after 60 s.
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
  - the task bindings (task id, slot-to-site map rule);
  - the constants version.
- **Content hash:** sha256 of the canonical JSON (sorted keys, floats by repr).
- **Copy for evaluation** (an isolated extracted group): an **empty** medium (no other elements) with the same sensor ring and readout geometry. The members are placed at their stored positions (identity pose). Phases are θ = stored offset + φ(t_copy), a uniform shift, so zero-resultant groups are handled.
- **Plasticity and growth are off** during evaluation. The drive is on, from the evaluation episodes.
- A copy whose readout region contains no member **abstains**. That is scored, not dropped.
- **Type id** = the content hash (immutable). Instances get monotone ids.

## 8. Competence (evaluator only)

- **Panel:** validation episodes 0-127 of each usable atom task, fixed.
- **Each snapshot is copied once and run on each usable task's panel** in its own isolated copy.
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

The usable list is **frozen before training** and shared by both arms. The world report already shows wide separation for all four tasks (remember_static is pending).

**The reward** (reward arm only) is r = clip(n, 0, 1) on the episode's task.

## 10. The development run (attainability only)

- **All constants above are fixed.**
- **Per arm:** 8 independent medium seeds; usable atom tasks rotated in blocks of 20 episodes; 2,000 episodes per seed (8,000 s of run time).
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
| **G0** | coverage = the time-average fraction of active sites covered over the last 20%; medium competence = the mean n over usable tasks of the **whole live medium** (copied at the end, isolated rules as section 7) on the evaluator panel. The control: the same run with B1 births at the **same times**, placed uniformly in a disk of radius 5 m.u., phase uniform, ω = π, g = 1, same protection and budget. An infeasible control birth is retried at the next check once; otherwise it is dropped and logged, and the match is reported | conditional > control on **both** estimands in ≥ 6 of 8 seeds | conditional ≤ control on both in ≥ 6 of 8 seeds | otherwise |
| **G0'** (count settling, not demand) | the OLS slope of N over the growth checks in the last 20%, with **no** cap, cost, placement or protected-over-budget rejection in the last 20%; turnover and uncovered-site time reported | slope within ±0.5 per 100 episodes with no rejections, in ≥ 6 of 8 seeds | outside the band, or any rejection, in ≥ 3 of 8 | otherwise |
| **G1** | ≥ 1 qualified snapshot in the run | in ≥ 6 of 8 seeds | in ≤ 2 of 8 | otherwise |
| **G1c** | competence of the snapshots, descriptive (per task and best task) | (descriptive) | | |
| **G5** (behavioural reproducibility) | for each snapshot, two isolated copies made at different copy times (different φ) on the same panel: |n₁ − n₂| ≤ 0.1 on every usable task; the per-seed value is the median over its snapshots | median passes in ≥ 6 of 8 seeds (with ≥ 1 snapshot) | in ≤ 2 of 8 | otherwise |

**INVALID**, not FAIL: a non-finite measurement, zero usable tasks, or an incomplete or interrupted run. The raw evidence is kept, and the reason is reported.

## 12. Stop rows (yes/no; one action; one role)

| Question | Yes → action | Role |
|---|---|---|
| Is the world, `remember_static` or the medium missing or NOT_READY? | Do not start section 10 | implementer |
| Is the usable-task list empty? | Report INVALID; do not start section 10 | implementer |
| Is a read-out INVALID? | Report it with the raw evidence; do not reinterpret it as FAIL or PASS | implementer |
| Does G1 FAIL in the task-blind arm? | Write the failure report; stop development | drafter |
| Does G0' FAIL? | Write the failure report; stop development | drafter |
| Is **any** protocol element (constant, schedule, reset rule, control, estimator, binding) changed after seeing development results? | Make a new design revision with fresh development seeds, and identify any reused evidence | drafter |
| Has development stopped and is a next step needed? | Ask the owner to decide | owner |

## 13. What this revision tests, in one sentence

Whether, in a continuously driven C4 medium with novelty birth, unlocked death and a budget, **structurally qualified groups (atoms) form**, whether **conditional growth beats random growth**, whether **the element count settles without hitting limits**, and whether **atoms copy reproducibly**, with competence on simple tasks measured afterwards and never fed back in the task-blind arm.

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

**Revision-1 findings** (14, fixed in revision 2 except as refined above): see revision 2's table in git history (`fc55cd2`, section 13).
