# 0g network policy: train the AI as a network (plain neural net and RRG resonator net, in parallel)

**Date:** 2026-10-08. **Drafter:** Claude (claude-opus-5-5). **Implementer:** Codex. **Status:** design draft for Codex review and owner approval. No training or data run is authorized by this file alone.

## 1. Owner decisions this rests on (2026-10-08)

- **The AI is a trained network,** not hand-written or copied scripts. Scripts (the copied dodge, the artillery planner, P16 and the elite AI) are **teachers, training data and comparators** only.
- **The networks:** both a plain neural network and our RRG resonator network, trained **in parallel on the same teacher data** and compared on identical fights.
- **Evaluation** follows decisions 0033 and 0034:
  - paired fights, 100–200 at a time;
  - two axes: own deaths per fight, and kills (kills per own death);
  - the ten-fight series streak is primary, with survivors healed and a random tactic each fight;
  - every result is labelled "script" or "network/RRG mechanism".

## 2. Lessons that shape this design

- **The owner's formation sandbox** (`astelia-hunte/experiments/formation_sandbox`): an MLP (64 hidden) imitating the look-ahead commander's *plan choice* matched it as a cheap shortlist, at 3× less CPU, but **"imitation network playing alone" gave no gain and was removed**.
  - So imitation reaches about the teacher at best; stage 2 (optimisation beyond the teacher) is required.
  - DAgger-style data on the student's own states is needed against compounding errors.
- **Our research note** (`docs/research/GAME_AI_BEST_PRACTICE_RESEARCH.md`, revision 3, Codex PASS_WITH_NOTES): copy the teacher, improve with search or optimisation against a weighted opponent pool, then distil. For RTS micro, unit-level control under a fast exact simulator is effective.
- **The project's Python environment is frozen** (`pyproject.toml`/`uv.lock` are bound by C4 acceptance). Training tools live in a **separate, gitignored environment** (e.g., `_local/mlenv` with PyTorch CPU). No change to the project lock. Inference runs **in the C++ engine** from exported weights.

## 3. The task: one policy per unit, shared weights, local information only

**The observation o_i** of unit i, egocentric and fixed-size with masks:
- **self:** role, HP fraction, cooldown and readiness, velocity, current target slot;
- **the 12 nearest friends:** relative position, velocity, role, HP, target-of slot;
- **the 12 nearest enemies:** the same, plus whether the enemy is targeting me;
- **the 8 most relevant visible threats** from the §12 adapter (shells, aimed shots, fields, enemy casts): relative landing point, time to impact, radius, whether I am inside;
- **a global summary:** living counts by role on both sides, and the offsets of both side centroids.
- **No tactic ID and no hidden state:** the same information boundary as the adapter.

**The action a_i** at 5 Hz decisions:
- **move:** a goal offset (dx, dy) within one second of travel;
- **target:** a pointer over the 12 enemy slots, or none;
- **guns only:** fire now or hold, and the aim offset relative to the target;
- **dodging is movement:** the network must learn it; there is no scripted dodge in the network arms.

## 4. The two networks (same inputs, same outputs, same data, same budget)

**N1, the plain neural net** (comparison):
- per-unit attention over the friend, enemy and threat sets, then an MLP with shared weights across units, about 50–150k parameters;
- output heads: move (Gaussian), target (softmax pointer), fire (Bernoulli), aim (Gaussian).
- **Closest known method:** AlphaStar-style entity attention with pointer heads (Vinyals et al. 2019) and SMAC per-agent policies.

**N2, the RRG resonator net** (our foundation):
- **The state:** each unit carries a complex resonator z_i with Stuart-Landau dynamics, as in v6 and C4/C5:
  dz_i/dt = (μ + iω_role)·z_i − |z_i|²·z_i + Σ_{j∈N(i)} K_θ(r_ij, roles)·(z_j − z_i) + W_in·φ(o_i).
  - K_θ is a learned geometry coupling (distance and role).
  - Units in phase form groups, the C5 "many resonators form one".
- **Thin readouts:** linear or very small heads on [z_i, the local field Σ K z_j, φ(o_i)]:
  - **target choice by phase alignment:** a score for enemy e of Re(z_i·conj(ẑ_e)) + a linear term, where ẑ_e is the mean phase of our units currently engaging e. Synchrony therefore produces focus fire;
  - **gun release** when the phase crosses the firing point (the V1 battery mechanism, now learned);
  - **move and aim** from a linear readout of the field.
- **The RRG requirement:** decisions must depend on the resonator state. An ablation with the coupling switched off (K = 0) and with z frozen must hurt.
- **Closest known methods:** coupled-oscillator RNNs (coRNN, Rusch & Mishra 2021), oscillatory reservoir computing, Kuramoto networks.
- **The difference:** a per-unit resonator coupled by battlefield geometry, where grouping through synchrony is the coordination mechanism (C4/C5).
- **Equal budget:** N2 gets the same data and optimisation budget as N1, and its parameter count is reported.

## 5. Data (the teacher)

- **D-teacher:** the elite AI plays our side against regular plus the 19 POOL tactics, both orientations, with fresh development entropy.
  - Record, for every own unit at 5 Hz, o_i and the teacher's executed intent (target, move goal, release, aim point, dodge).
  - The first batch is **200 fights.** The size is projected first (decision 0031).
- **D-student (DAgger):** after stage 1, the student plays while the teacher is shadowed on the student's states (§9 shadow mechanism, separate RNG), and the student's states get the teacher's labels. This is aggregated and refitted.
- **Splits by whole fight:** train, validation and test, plus separate evaluation seeds that are never trained on.

## 6. Training

- **Stage 1, imitation (behaviour cloning, then DAgger)**, for N1 and N2:
  - losses: cross-entropy on target and fire, Gaussian NLL on move and aim;
  - N2 trains through its unrolled dynamics (backpropagation through time over windows of about 3 s).
  - **Report:** held-out accuracy, then lab play (paired).
- **Stage 2, optimisation beyond the teacher:**
  - evolution strategies (CMA-ES or separable/OpenAI-ES) over a declared parameter subset (readouts, coupling) on the paired series objective;
  - lexicographic: elimination win, then fewer deaths, then kills per death;
  - the opponent pool weighted toward tactics we lose to (PFSP polarity per the research note);
  - decision-0033 sizing for every evaluation.
- **Compute:** CPU only, in the separate ML environment; projected before running (decision 0031).

## 7. Evaluation (lab, paired, same fights)

**Arms:**
- the scripted base (forcedP16 + react, and + V2 if V2 passes);
- the elite (reference);
- N1 after stage 1, N1 after stage 2;
- N2 after stage 1, N2 after stage 2;
- the N2 ablations (K = 0, z frozen).

**Metrics:**
- mechanism checks (drills D1–D5 per role);
- C3 against the 20 tactics at 50/100/200 paired fights;
- the ten-fight series;
- both axes, with "network vs script" labels.

**The reading** (declared now):
- **"The network AI works":** an N arm reaches the scripted base on deaths and kills per death in C3, and the series streak is not below it.
- **"It beats the scripts":** clearly better than the scripted base, and at or above the elite on the series.
- **"RRG earns its place":** N2 is at or above N1 at an equal budget, **and** the N2 ablations clearly hurt.

## 8. Stop rows

| Yes/no | Action | Role |
|---|---|---|
| Does the dataset projection exceed 1 h before 22:00? | Ask the owner | Claude |
| Is stage 1 held-out accuracy at about the majority baseline? | Stop; fix the features or labels before any lab play | implementer |
| Is a network arm far below the scripted base after DAgger? | Report; adjust the design (owner) before stage 2 | drafter |
| Do the N2 ablations not hurt? | Report "the resonator state is not used"; redesign the N2 readout | drafter |
| Would training need a project lock change? | No: use the separate environment | implementer |

---

## Revision 2 (answers `docs/reviews/network_policy_design_review_codex.md`, CHANGES_REQUIRED, F1–F11). It overrides the draft where they differ.

**Self-audit (drafter's causes):**
- **F1–F5:** I assumed the react adapter and the native decision trace were neutral, complete per-unit I/O. They are not. The adapter runs v7 and the copied REACT before submitted commands. The trace precedes fire gates and the joint volley planner. The existing shadow is a dodge-trio teacher, not the full elite.
- **F6–F7:** I described Stuart-Landau as the C4/C5 law without reading `geomind/c4_model.py`.
- **F8–F11:** I wrote "same budget", the ES ranking and the readings without the 0033/0034 definitions and without sizing.

### R2.1 The first milestone is a guns-only end-to-end slice (Codex's smallest executable milestone)
- **The networks control only our artillery:** move, target, cast permission and explicit aim, in drills D1 (guns against guns plus static infantry) and D2-like (under shellfire, with dodging needed).
- **Non-gun units are explicit, unchanged scaffolding.** No learned full army yet.
- The cases include 1–2 guns and incoming shells.
- **Order:** the full army comes only after the slice works: mechanism, then C3 50/100/200, then the series.

### R2.2 A neutral network host (F1)
- **A new native host and controller** (new files) reuse only the observation and command legality mechanics: body, range, minRange, legality projection and participation.
- **It never calls** P16, v7, the copied REACT, E1, R1 or the volley planner for network arms.
- Native physics and reflexes are identical across all arms, including the script comparators.
- **Per tick, it records:** the raw network intent, the legality projection and its reason, the executed command, and launch acknowledgements.
- **Dodging is learned** from the threat inputs, with no scripted dodge in network arms.

### R2.3 Action semantics across the 30 Hz tick (F2)
- **Timing:** decisions at 5 Hz, at the observation snapshot of tick t (before `prepare`). An action holds for six ticks.
- **The cache stores absolute values:** goal position, aim point and target identity (stable unit id). Offsets are not re-applied to a moving unit.
- **The gun cast lifecycle:**
  - `permit` allows the start of a windup; `hold` blocks the start of a new windup;
  - a windup already started always completes, then releases at the cached aim if it is still legal, else at the nearest legal point;
  - a completed cast is never held beyond one decision interval;
  - an actual launch is acknowledged into the next observation.
- **Target death or slot churn:** the cache drops the target, and the next decision chooses again.
- **The reaction delay** (up to one interval) is reported and identical for N1 and N2. The script teacher decides every tick, which is a stated asymmetry.

### R2.4 A versioned observation and action schema (F3)
- **Self:** role, HP, preparation state and time-to-release, cooldown, energy, range and minRange, body radius, speed, velocity.
- **Friends and enemies:** k = 12 each, sorted by distance then id; the same fields plus target-of and is-targeting-me.
- **Threats:** typed tokens for shell, aimed shot, field and enemy cast. Each keeps its own geometry and timing:
  - shell: landing point, time and radius;
  - shot: origin, direction, speed and remaining distance;
  - cast: caster, target and release time.
- **Arena:** distances to the arena borders. **Global:** counts by role on both sides.
- **Encoding:** egocentric with an orientation transform (mirror for side), and an inverse transform for actions. Units are px, px/s and game-seconds, scaled with a normalization ledger and masks for missing slots.
- **Decoder:** an absolute goal clipped to legal positions; target = enemy id; aim point = legal splash centre.

### R2.5 A teacher-label collector, and a constrained public teacher for the slice (F4, F5)
- **A new native collector** records, by fight, tick, unit and volley id:
  - the pre-policy public snapshot;
  - the teacher's candidate movement (move flag, stop, multiplier);
  - the post-arbitration intent;
  - cast start, hold and continue;
  - scheduled joint volleys;
  - the actual release, aim and target.
- **Action labels are the post-arbitration intent plus the actual release and aim.** Launch outcomes are kept separate.
- **The slice teacher is a constrained public teacher** for guns: the engine artillery planner (`artyFire: plan`) running on public information over our guns, plus the copied REACT for gun reactions. Labels come at the same tick order as the network's decisions.
- **The full elite** (with commander look-ahead and rollout) remains a **labelled reference arm**, not the label source for the slice. Its labels exceed the action contract and its branch thinking differs (F5).
- **DAgger for the slice:** the constrained teacher is evaluated on student-visited states at the same tick point, from a separate teacher-state copy with its own RNG. No physical time advances for labelling. The byte-identical shadow-on/off check applies.
- A full-elite DAgger oracle is deferred until a defined full-teacher-on-student-state contract exists.

### R2.6 N2 rebuilt on the actual C4 element law (F6, F7)
- **The C4 law** (`geomind/c4_model.py`): x_dot_i = mean_j[û_ij·(A·(1 + J·cos(θ_j − θ_i)) − B/r_ij)] and θ_dot_i = ω_i + mean_j[K·w(r_ij)·sin(θ_j − θ_i)], with w = exp(−r²), up to k nearest neighbours within a radius, degree-normalized, the neighbour set held for each RK4 step.
- **N2 for guns:**
  - each gun is a C4 element: phase θ_i, plus its actual battlefield position as the geometry;
  - **the mode → geometry → mode loop is kept:** phase-dependent spacing (A, J, B) contributes a bounded share of the move goal; the network adds a learned bounded movement term; real positions feed back into the phase coupling;
  - **learned parameters:** the input forcing g·φ(o_i) on θ_dot and ω, the coupling scale K and radius within declared bounds, and thin readouts;
  - **readouts:** permit when the phase is in a window (the learned battery firing point); a target score combining a learned linear term with an alignment term over the local phase order parameter of guns already engaging that target; aim as a learned bounded offset.
- **The tested subset is declared:** a local geometry-mode loop driving battery timing and target grouping. C5 "many become one" is **not claimed** unless group-detection criteria (`c5_detect.py`) are met and reported.
- **Numerics, matching `s4_v6_complex.cpp`:**
  - the bounds, held topology, RK4 and stage monitoring are reused;
  - the training and native integration use the same dt (1/30 s) and substep policy;
  - real or imaginary-free phase state (θ in rad);
  - BPTT over 3 s windows (90 ticks), with gradients through θ and through the readouts, and topology held (no gradient) within a step;
  - gradient clipping, and a failure policy: drop the window and log it.

### R2.7 Controls and fairness (F8)
- **Whole-system comparison** (the owner's request): N1 against N2, with the same observations, decoder, data and optimiser budget. The budget is declared in gradient steps, rows seen and ES evaluations.
- **For attribution to oscillation,** a third network N1r: a bounded recurrent message-passing net (GRU-style) with the same local graph, memory, update cadence and decoder, but no oscillator law.
- **"RRG earns its place"** requires N2 ≥ N1r **and** N2 ≥ N1, plus the ablations:
  - K = 0 (no phase coupling);
  - topology frozen (the geometry → mode channel removed);
  - J = 0 (the mode → geometry channel removed).
- **Ablations are reported as harm or no harm. No harm is not proof of non-use** (F11).

### R2.8 Stage-2 objective and budget (F9)
- **For the slice,** the drill objective is lexicographic, using ratios of totals with a null for a zero denominator:
  1. own guns lost over all paired fights;
  2. enemy kills per own death;
  3. kills per minute.
- **For the full army later,** decisions 0033/0034 apply: streak first, then deaths over all paired fights, then kills per death.
- **ES:** separable CMA-ES over the declared learnable subset, with a fixed paired panel per generation:
  - 16 candidates × 10 paired fights = 160 fights per generation;
  - at most 20 generations, 3,200 fights for the slice;
  - evaluated on fresh seeds after selection.

### R2.9 Sizing and environment (F10)
- **Rows:** Σ over fights and decisions of the living own guns.
  - Slice D1/D2: 200 fights × about 40 s × 5 Hz × at most 10 guns = at most **0.4 M rows**.
  - At about 300 float32 features, that is about 0.5 GB.
  - The full army later: 50 units, about 7.5 M rows at most for 200 fights, so it will be subsampled.
- **The ML environment:** a separate pinned environment with its own lock file in the new folder (PyTorch CPU, NumPy), reproducible from that lock. The project lock is untouched. The torch thread count is fixed at 4 so fights and training share the 10 cores.
- **The projection is reported before** collection and training (decision 0031).

### R2.10 Decidable readings for the slice (F11)
- **Mechanism (10–20 paired drill fights):**
  - **the network arm activates:** it fires, moves and targets legally, with fewer than 1% illegal projections;
  - **reports:** damage per shell, shells per kill, fire rate, own guns lost, the enemy's dodge success against our shells, and launch and landing spread.
- **"The network slice works":** N (stage 1) is within the decision-0033 effect size of the constrained-teacher arm on own guns lost and kills per minute: about ±1 gun lost per fight and ±10% kills per minute.
- **"It beats the teacher" (stage 2):** clearly better than the teacher arm at that size, at the declared paired looks.
- **Held-out imitation quality:** per head, against declared baselines. For targets, top-1 against nearest-target and against the teacher's own repeat consistency. For fire, against a constant hold or permit. For move and aim, error against a zero-offset decoder. These are diagnostics only; the decisions use the paired play.

### R2.11 Updated stop rows

| Yes/no | Action | Role |
|---|---|---|
| Does any network arm call a scripted policy? | Stop; fix the host | implementer |
| Do the collector labels fail parity with the executed actions on recorded fights? | Stop; fix the collector | implementer |
| Is held-out imitation no better than its declared baseline on a head? | Stop before play; fix the features or labels | implementer |
| Is the slice network far outside the effect size below the teacher after DAgger? | Report; redesign with the owner before stage 2 | drafter |
| Does a projection exceed 1 h before 22:00? | Ask the owner | Claude |

---

## Owner approval and the build route (2026-10-08)

- **Codex round 2** (`docs/reviews/network_policy_design_review_r2_codex.md`, CHANGES_REQUIRED, R2-F1…F10) asked for exact engineering contracts:
  - the field allowlist and tensor table;
  - the cast state machine;
  - the constrained-teacher and label join;
  - the N2 gradient and recurrent-state paths;
  - C4 motion numerics in engine units;
  - isolating ablations;
  - safe multimodal losses and the DAgger schedule;
  - resources;
  - the ES optimizer contract;
  - decidable readings.
- **The owner chose "Build now, contract first":** the design direction (revisions 1–2) is approved.
- **Build deliverable 1** is the exact engineering contract answering R2-F1…F10, **in code with tests**, before any training or teacher-data run:
  - the schema and normalization table;
  - the cast state machine;
  - the neutral host;
  - the collector and label join;
  - the N1/N1r/N2 forward passes;
  - the losses;
  - the ablation switches;
  - the resource projection;
  - the readings.
- **Review:** Claude reviews deliverable 1 once (cross-family), then Codex continues with the guns-only slice: teacher data, then stage 1, then DAgger, then the mechanism check.
- **Living documents are never hash-pinned:** frozen copies are kept inside the build folder.
