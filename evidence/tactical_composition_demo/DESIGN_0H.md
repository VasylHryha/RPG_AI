# Design 0h, revision 2: the bootstrap of atoms and the library (DRAFT for a Codex re-review; no growth experiment run)

Revision 2 answers the Codex review of revision 1 (`docs/reviews/tactical_0h_design_review_codex.md`, CHANGES_REQUIRED, 14 findings). The self-audit is section 13; revision 1 is in git history (`85c656b`).
- **Scope (narrowed, finding 13):** only the **bootstrap**: atoms grow, are qualified and enter the library.
  - Combinations, bonds, duplicates and library trends (proposal G2-G4, G7, G8) are **deferred** to a later design, which waits for the C6 background pilot (tracker W1).
  - H-BG, H-PS and H-RBG are NOT_TESTED here.
- **Authorization:** decision 0028 item 17 authorizes engine parts and this drafting, **not** a growth or development run. Running section 9 needs the owner's go-ahead after a Codex re-review.

## 1. Claim and assumption ledger (finding 13)

| Element | Status |
|---|---|
| C4 element law (positions and phases), the C4 detector criteria 1-5, the C5 published-interface fields | **accepted, reused unchanged** |
| A driven phase term (input drive), as in the C6 R4 design | **an addition**, already used by C6's design |
| Natural-rate and gain adaptation; novelty birth; unlocked death; a budget | **motivated hypotheses** (resonance and stability), not derived and not accepted |
| One direction carrier band; the sensor and readout layout; the item salience (distance) | **engineering choices** |
| Task reward (reward arm only); the choice of atomic tasks | **additions** (machine learning) |

"Theory alone" is **not** claimed for any arm (finding 1). The stability arm is called the **task-blind arm**: no task score enters its learning, survival, locking, admission, copying or placement.

## 2. Units, clocks and timescales (finding 4)

- **Medium time** s_m, with the C4 step dt_m.
  - The world step dt_w comes from the world's report.
  - n_sub = ceil(dt_w / 0.02), and dt_m = dt_w / n_sub, so a world step is exactly n_sub medium steps with no remainder.
  - One medium second equals one world second (1 s_m = 1 s_w).
- **Carrier:** one direction band for the bootstrap (finding 3's simplest cut), with rate ω_D = 2π / P_D and carrier period P_D = 2 s.
  - The band clock is φ(t) = ω_D t, reset to 0 at each episode start.
- **Timescales are measured, not assumed:**
  - carrier period P_D (fixed);
  - phase relaxation τ_θ and geometric relaxation τ_x: kick-relaxation times, measured with the C4/C5 procedure;
  - adaptation times 1/η_ω and 1/η_g (fixed).

  Reported for each atom. No separation is promised; C5's 3.4 was a kick-relaxation ratio. A level-separation claim is deferred with combinations.
- **Units:**
  - η_ω and η_g: 1/s_m;
  - drive strength k: rad/s_m;
  - gain g: dimensionless, in [0, g_max];
  - PLV, eligibility and coherence: dimensionless, in [0, 1];
  - reward: the task's normalized score, in [0, 1] (section 8);
  - η_r: per episode, per unit reward;
  - cost: element units.

## 3. The forward map: world observation → drive → dynamics → action (finding 3)

**Encoding (one carrier band):**
- Each atom task has a fixed number of item slots: perceive 8, move 1, remember 1, choose 8. The world's K is in {3, …, 8} (world review note 1); unused slots have k = 0.
- At episode start, items are assigned to sensor sites by a permutation drawn from the episode seed. **The assignment holds for the whole episode** (stable item bookkeeping); item order carries no meaning.
- Sensor sites sit at fixed medium coordinates, evenly on a ring of radius 4 m.u. Readout sites are in the ring's centre region (section 3, decoding).
- **The drive on element i**, added to its phase rate:

      dθ_i/dt += g_i · Σ_s k_s · K(|x_i − q_s|) · sin(ψ_s(t) − θ_i),    K(r) = exp(−r² / (2 σ_d²)) for r ≤ 3 σ_d, else 0,    σ_d = 1 m.u.

  with ψ_s(t) = φ(t) + α_s, where α_s is the item's direction relative to the agent (world frame).
- **Strength from legal observations only:**
  - k_s = k_0 · exp(−d_s / d_0) for perceive, move, remember (while visible) and choose;
  - choose also multiplies by (1 + h_s), where h_s = 1 − HP_s / HP_max (weakness), and by 1 or 0.5 for in range or not. These are disclosed task priors, given to every yardstick as inputs too.
  - Constants: k_0 = 2 rad/s_m, d_0 = half the arena size.
- **Observations are held** for the n_sub substeps of a world step. An absent item (invisible or missing) has k_s = 0.
- **The encoder holds nothing.** Remembering must come from the medium's own state.

**Decoding:**
- The readout region is the elements within 2 m.u. of the ring centre, weighted by K.
- Order parameter Z = Σ_i w_i e^{iθ_i} / Σ_i w_i, with coherence C = |Z|, which is labelled **coherence, not amplitude**.
- If Σ w_i = 0 or C < 0.05, the output is **abstain**:
  - for direction outputs, the agent holds;
  - for choice, no target.
- **Direction output:** arg(Z) − φ(t), wrapped to (−π, π].
- **Speed** (move task): min(1, C / 0.8), declared as coherence-controlled speed.
- **Distance output** (perceive): decoded from C by one fixed monotone map, set before running: d̂ = d_0 · ln(k_0 / (C · k_0)), clipped to the arena. Its error is reported but not used for atom qualification.
- **Choice (finding 2):** the candidate s with the smallest wrapped angular error |wrap(arg(Z) − φ(t) − α_s)|. Ties go to the lowest item id; abstain gives no target. **Contract examples:**
  - static candidates at unequal directions must give distinguishable choices;
  - an opposite-direction input must flip the choice.

## 4. Initial state and the update sequence (finding 5)

- **Initial medium:** N_0 = 24 elements, positions uniform in a disk of radius 5 m.u. around the ring centre, phases uniform, ω_i = ω_D · (1 + U(−0.1, 0.1)), g_i = 0.5. Everything is drawn from the medium seed.
- **Per medium substep, in order:**
  1. the drive terms from the held observation;
  2. one C4 RK4 step with the drive added to the phase rate (positions by the unchanged C4 law; neighbours held through the step);
  3. adaptation (forward Euler, then clipped);
  4. the measurement windows are updated.
- **Adaptation (shared by both arms):**
  - dω_i/dt = η_ω · (ω̂_i − ω_i), where ω̂_i is the unwrapped mean phase velocity over the last W = 5 P_D (no adaptation before the window is full), clipped to ω_D · [0.5, 1.5];
  - dg_i/dt = η_g · (P_i − g_i), where P_i = the PLV of θ_i with its strongest-drive site over W (strongest = the largest k_s · K at the window's last step; ties go to the lowest site id; 0 if no drive reaches i), clipped to [0, g_max];
  - η_ω = η_g = 0.05 /s_m; g_max = 2.
- **Reward arm only, at episode end:**
  - eligibility e_i is the episode mean of P_i (dimensionless);
  - Δg_i = η_r · (r − r̄) · e_i, clipped;
  - then r̄ ← r̄ + 0.1 · (r − r̄);
  - r̄ starts at 0.5 and is never reset within a run;
  - η_r = 0.5.

  The reward arm **adds only this update**; everything else is identical (the confound is named: the arms differ in exactly this term).
- **Cases:**
  - zero drive: P_i = 0, so g decays;
  - r = r̄: no change;
  - a window not yet full: no adaptation and no growth check for that element.

## 5. Growth and death for the bootstrap: B1, D1, D3 only (finding 6)

B2 (strain split), B3 (need) and D2 (utility) are **deferred**: their quantities are not yet exact.

**Lock L(i):** the maximum PLV over W of θ_i with:
- each C4 neighbour (k ≤ 8 within radius 3, as C4); and
- each sensor site with K(|x_i − q_s|) > 0.

An isolated element with no partner and no site in range has L(i) = 0.

**Coverage of site s:** covered if some element within 3 σ_d of q_s has a PLV with ψ_s ≥ L_on **and** a wrapped offset |wrap(θ_i − ψ_s)| ≤ δ_off (the content check, finding 2), both over W.

**State-transition table**, checked every τ_l = 10 P_D, in this order:

| Step | Rule | Exact condition | Action |
|---|---|---|---|
| 1 | D1 | element i not protected, and L(i) < L_off continuously for T_death = 20 P_D (the timer resets when L(i) ≥ L_off) | remove i |
| 2 | D3 | cost > C_max after step 1 | remove unprotected elements by lowest L(i), ties by lowest id, until cost ≤ C_max; if only protected elements remain, stop removing and block births this check |
| 3 | B1 | site s active (k_s > 0) and not covered continuously for T_nov = 10 P_D (the timer resets when covered or inactive) | births in site-id order, at most n_birth = 2 per check, each accepted only if N + 1 ≤ N_max and the cost after the birth ≤ C_max; position: q_s + a uniform point in a 0.5 m.u. disk, nudged by 0.05 m.u. steps until at distance ≥ 0.05 m.u. from every element; phase ψ_s(t); ω = ω_D; g = 1; empty windows; protected for T_protect = 10 P_D |

- **Constants:** L_on = 0.8, L_off = 0.5 (hysteresis), δ_off = 0.5 rad, N_max = 64, cost = 1 per element + 0.1 per undirected C4 neighbour pair within radius 3, C_max = 64.
- **A birth goes before D-rules of the next check only.** Every event is logged.

## 6. Atoms: qualification without task scores (findings 1, 7)

**Freezing an atom (locking):** the group's learned coefficients **ω_i and g_i are frozen**. Positions and phases **keep evolving** under the full driven C4 law: no rigid body and no projection.

**The atom criterion is structural only** (task-blind). A candidate is a group from the **accepted C4 detector procedure**, applied to the driven history with an adapter that reads frames every P_D over the last 30 P_D. It must pass:
- criteria 1-4 (size ≥ 3, link factor, membership Jaccard, shape coefficient of variation, all-pairs lock, frequency stationarity and pair pattern, with the C4 thresholds, times scaled by P_D);
- criterion 5 recovery:
  - paired kicked and unkicked futures with **drive on** as in the episode (driven persistence);
  - all three Jaccards ≥ 0.9;
  - the recovered phase pattern error ≤ 0.1 rad.

**Reported separately:** the same recovery with drive off (autonomous persistence); it is not required.

Degenerate groups (singletons, zero spacing, a degenerate hull) fail.

**Task competence is measured only afterwards, by the evaluator:**
- the qualified atom is **copied into a fresh medium** (template, section 7);
- it is driven with the task's legal observations;
- it is scored on held-out episodes.

**In the task-blind arm**, nothing about the score changes the library. Every qualified atom enters, and competence is a recorded property. **In the reward arm**, admission additionally requires the competence threshold, and this arm is labelled **supervised outer selection plus online reward**.

## 7. Templates, identity and the library (finding 8)

| Part | Content | Who reads it |
|---|---|---|
| **Template** (private) | per element: ω, g, relative position and phase at the qualification frame; sensor and readout bindings; a content hash | copy and reset only |
| **Interface** (public, C5-style) | effective position, size, collective rate, mode signature, boundary ports, stability (recovery times) | later levels |
| **Evaluator record** | task competence per task, panel results | evaluator only |

- **Copy:** place the template's elements at a chosen origin and orientation (the default is identity). Phases are offset so that the group's mean phase equals the current band clock plus its recorded mean offset.
- **Type and instance ids are immutable.** "Unchanged reuse" means **the same template hash**.
- **The fuzzy similarity of interfaces is descriptive only:** it never merges types in this revision.

## 8. Tasks and scores

- **Tasks:** the world's four atomic tasks (`growing_shapes/world/WORLD_REPORT.md` once READY), with their exact definitions and scripted reference and random baseline scores.
- **Primary score per task** (world review note 2; the other metrics are descriptive):
  - perceive: angular error;
  - move: goal error;
  - remember: angular error on hidden decisions, **on a static-target variant** (enemy speed 0; world review note 3). The world gets this as an additive generator option before development.
  - choose: correct-choice rate.
- **Normalized score:** n = (score − random) / (reference − random), oriented so that higher is better (errors are negated).
- **Separation check:** a task is **usable** only if its reference beats random by a margin of at least 3 standard errors on validation episodes. An unusable task is reported and excluded, not silently kept.
- **Competence threshold:** n ≥ 0.5 on the held-out evaluator panel.

## 9. Development procedure (finding 10: fixed values, attainability only)

**All constants in sections 2-5 are fixed in this revision. There is no search.** Development checks **attainability**:
- one development run per arm;
- 8 independent medium seeds;
- the four atom tasks rotated in blocks of 20 episodes;
- 2,000 episodes per seed.

If the results fall short, the stop rows of section 12 apply. A changed constant is a **new design revision** with fresh development seeds, never a retune of this one.

**Exposure ledger (finding 12):**
- training episodes (counted);
- qualification frames (no task data);
- evaluator episodes (held out, never fed back in the task-blind arm);
- all counted and reported per arm.

## 10. Yardsticks and accounting (finding 12)

| Model | Learned scalars | Notes |
|---|---|---|
| Medium (each arm) | 2 per element (ω, g), counted at peak N and at final N, plus unique template scalars in the library | positions and phases are state, not parameters |
| Fixed-size medium | 2 · N_fix, with N_fix = each seed's final N (a declared final-size match, fresh initialization) | same rules, growth off |
| GRU (memory) and MLP (no memory) | the smallest hidden size h whose parameter count is ≥ the medium's peak count | trained by Adam on the same episodes, inputs = the same legal observations and priors (section 3) |

The gradient-trained medium (AKOrN-like) is **deferred**: hard neighbour and readout operations need a separate specification.

## 11. Development read-outs (findings 11, 14), with PASS / FAIL / INCONCLUSIVE

The unit of analysis is the independent medium seed (8 per arm). These are development read-outs only. A registration later sets the final statistics.

| ID | Read-out | PASS | FAIL | INCONCLUSIVE |
|---|---|---|---|---|
| G0 | Births by reason (only B1 here) against a **matched randomized-birth control** (same count and times, random positions): held-out task competence and coverage | conditional births improve coverage and competence over the control in ≥ 6 of 8 seeds | in ≤ 2 of 8 | otherwise |
| G0' | N settles: the slope of N over the last 20% within ±0.5 elements per 100 episodes, **with** no cap saturation (N < N_max and no birth rejected for the cap in the last 20%) | both hold in ≥ 6 of 8 seeds | slope outside the band, or cap saturation, in ≥ 3 seeds | otherwise |
| G1 | Atom formation: per task, the fraction of seeds yielding ≥ 1 qualified atom (section 6) | ≥ 6 of 8 seeds **for each usable task** | ≤ 2 of 8 for any usable task | otherwise |
| G1c | Atom competence (evaluator): the fraction of qualified atoms with n ≥ 0.5 | reported; in the reward arm admission requires it | | |
| G5 | Copies keep competence: a template copied into a fresh medium reaches the same competence (paired, non-inferiority margin 0.1) | ≥ 80% of atoms | < 50% | otherwise |

G2-G4, G6 (as a conjunction), G7 and G8 are deferred with combinations.

## 12. Stop rows (one action, one role each)

| Question | Yes → action | Role |
|---|---|---|
| Is the world or medium report missing or NOT_READY? | Stop before section 9 | implementer |
| Is a task unusable (section 8)? | Exclude it and report; continue with the usable tasks | implementer |
| Does G1 FAIL in the task-blind arm? | Stop development; write the failure report | drafter |
| Does G0' FAIL (no settling, or the cap binds)? | Stop development; write the failure report | drafter |
| Is a constant changed after seeing development results? | Make it a new design revision with fresh development seeds; keep this revision's evidence unchanged | drafter |
| After a stop, what next? | The owner decides | owner |

## 13. Self-audit: revision-1 review findings, fixes and causes

| # | Finding | Fix | Cause |
|---|---|---|---|
| 1 | Task selection inside the "stability" arm | A task-blind arm: structural qualification only; competence measured afterwards; the reward arm labelled supervised outer selection | I used task score as an atom criterion |
| 2 | PLV ties different directions | Choice by the smallest decoded-direction error; novelty with an offset condition; contract examples | I treated lock as content |
| 3 | Incomplete forward map; coherence called amplitude | A full map, held observations, abstain rules, one carrier band, coherence-controlled speed, no encoder memory | Left to the implementer |
| 4 | Periods, relaxations and clocks mixed | 2π/ω periods; measured relaxation times; an exact world-medium conversion; units | Wrote 1/ω; misread C5's 3.4 |
| 5 | Learning discretionary | Initial state, update order, estimators, clipping, eligibility, baseline; arms differ by one named term | Not specified |
| 6 | Birth/death not executable | B1/D1/D3 only, an exact state table; B2/B3/D2 deferred | Too many rules too early |
| 7 | Rigid locking changed the law; weak atom test | Freeze ω and g only; the full C4 detector procedure with paired recovery | I invented rigidity |
| 8 | Identity not reproducible | Template, interface and evaluator record; hash identity | The card mixed roles |
| 9 | Bonds correlational | Deferred with combinations; causal transfer controls required then | Out of bootstrap scope |
| 10 | Section 7 an overfittable search | All constants fixed; development checks attainability only | I wrote a search |
| 11 | Read-outs pass by construction | Bootstrap read-outs with PASS/FAIL/INCONCLUSIVE and matched controls; the rest deferred | Metrics restated rules |
| 12 | Equal size and budget undefined | An accounting table, a declared final-size match, an exposure ledger | Not specified |
| 13 | Claims beyond the test | A claim ledger; scope narrowed to the bootstrap; background claims NOT_TESTED | Overreach |
| 14 | Stop rows | One action per role; constant changes become new revisions | Too loose |
