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
