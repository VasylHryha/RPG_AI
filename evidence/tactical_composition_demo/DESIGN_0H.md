# Design 0h, revision 1: growing shapes, the exact contract (DRAFT for a Codex review; no growth experiment run)

From `PROPOSAL_0H_GROWING_SHAPES.md` revision 2 (the direction was approved [R], decision 0028 item 17). The engine parts are being built in parallel:
- `growing_shapes/world/`: the 2D task world;
- `growing_shapes/medium/`: the C4 medium.

This design fixes what the experiment does with them. Where a value says **(dev)**, it is chosen once by the procedure in section 7 on development seeds of the atom tasks, then frozen for every level. Claim boundary: proposal sections 1-2.

## 1. Levels, units and timescales (the ledger)

| Quantity | Unit | Value |
|---|---|---|
| Medium length | m.u. (model unit) | element interaction radius 3 m.u., as C4 |
| Medium time step | s_m (medium seconds) | dt_m = 0.02, as C4 |
| World step | s_w (world seconds) | dt_w fixed by the world. The medium runs n_sub = dt_w / dt_m RK4 steps per world step |
| Activity (beat) | τ_a | 1 / band rate (section 2) |
| Reshaping (C4 position law and rate adaptation) | τ_g | ≥ 10 τ_a; enforced by the plasticity rates η (section 4) |
| Birth and death checks | τ_l | every 10 τ_g |
| Level-1 shape (atom) timescale | measured | collective period of the locked group; expected ≥ 3 τ_a (C5: 3.4×) |
| Level-2 shape timescale | measured | expected ≥ 3 × the level-1 period |

The world's coordinates and the medium's coordinates are **separate spaces**. The arena is the outside world; the medium is the "brain space". They are connected only by encoding (section 2) and decoding (section 3).

## 2. Encoding: the rhythm language (inputs)

**Bands:** four frequency bands, each a natural-rate range around a centre ω_b, with ω_b fixed (dev):

| Band | Carries | Centre (initial proposal; dev) |
|---|---|---|
| D (direction) | direction to a seen thing | ω_D = 1.0 /s_m |
| M (memory) | a held direction | ω_M = 0.25 /s_m (slow) |
| C (choice) | a candidate for selection | ω_C = 2.0 /s_m |
| A (action) | the direction and strength of a step | ω_A = 0.5 /s_m |

**Band clock:** each band has a reference phase φ_b(t) = ω_b t. A direction α is encoded as a phase **offset** α relative to the band clock.

**Drive sites:**
- Each observation item drives a **sensor site** at a fixed place in the medium: ψ_s(t) = φ_b(t) + α_item, with strength k_s = f(item).
- Distance enters as strength: k = k_0 · exp(−d / d_0) (dev). HP weakness and in-range status, for the choice task, also enter as strength.
- The sensor layout is fixed: one sensor region per band, on a ring of radius r_sens around a fixed centre, with enough sites for the maximum number of items.
- Items take sites in a fixed order. **Item order never carries meaning:** each task is generated with random item order.

## 3. Decoding: outputs

- **A readout site per output band:** kernel-weighted order parameter R e^{iΦ} of the elements near it.
- **The direction output** is Φ − φ_b(t), wrapped to (−π, π].
- **The strength output** is R, mapped to the speed multiplier by min(1, R / R_0) (dev).
- **Choice:** the candidate whose sensor site has the highest phase-locking value with the C-readout group over the last window W. Ties go to the lowest id.

## 4. Learning: resonance always; selection only in the reward arm

Parameters that learn, per element:
- position (by the C4 law, which is unchanged);
- natural rate ω_i;
- input gain g_i (the multiplier on drive terms reaching i).

**Resonance (both arms):**
- **Rate adaptation:** dω_i/dt = η_ω · (ω̂_i − ω_i), where ω̂_i is i's observed mean phase velocity over W. An element tunes to the rhythm it actually follows.
- Positions follow the C4 law. That law is the resonance-to-geometry rule: in-phase elements attract.
- **Gain adaptation (stability arm):** dg_i/dt = η_g · (PLV(i, its strongest site) − g_i). Gain grows with sustained locking to an input.

**Selection (reward arm only):**
- Each element keeps an eligibility trace e_i (decay τ_e, dev) of its lock with active drive and readout sites.
- At the task reward time: Δg_i = η_r · (r − r̄) · e_i and Δω_i = η_r' · (r − r̄) · e_i · (ω̂_i − ω_i). Here r̄ is the running mean reward, and the bounds keep g in [0, g_max] and ω in its band range.

**Yardsticks:**
- **Fixed-size medium:** same rules, birth and death off, N fixed at the grown arm's final N.
- **Gradient medium:** the same parameters (positions, ω, g) trained by backpropagation through time on the task loss over the same episodes. AKOrN-like. A yardstick only.
- **Neural network:** a GRU, so that memory is possible, with the same count of learnable scalars, trained by gradient on the same episodes.

## 5. Growth and death (proposal section 3), exact

- **B1 Novelty:** a sensor site s has drive strength above k_min and **no** element within 2 m.u. with PLV(i, s) ≥ L_on, for ≥ T_nov. One element is born at a random point within 1 m.u. of s, with ω = ω_b of s's band and θ = ψ_s(t).
- **B2 Strain split:** S(i) ≥ S_split and L(i) < L_on for ≥ T_split. Element i is replaced by two, at the two cluster phases, ±0.1 m.u. along a random direction. Each copy inherits ω and g.
- **B3 Need (reward arm):** the running task error of an atom task above E_need for ≥ T_need, with no birth within 2 m.u. of that task's sensor region in the last T_need. One element is born at the region's centroid, in its band.
- **D1 Unlocked:** L(i) < L_off for ≥ T_death.
- **D2 Useless (reward arm):** |U(i)| < ε_U in K consecutive utility checks. U(i) is the change of mean reward over one evaluation block with i silenced.
- **D3 Budget:** while cost = c_e · N + c_c · (active couplings) > C_max, remove the element with the lowest L(i) (stability arm) or the lowest U(i) (reward arm).
- **Order and caps:**
  - in one check, D rules before B rules;
  - a newborn is protected for T_protect;
  - N ≤ N_max;
  - at most n_birth births per check (dev) to avoid bursts.

## 6. Shapes, locking, identity cards and bonds

- **A shape** is a locked group from the medium's group detector: lock graph above L_group, the C4 spatial link rule, persistent over ≥ 3 windows.
- **The atom criterion** (locking a shape as an atom):
  - its task score ≥ the registered atom threshold (section 8);
  - it passes the recovery test: phase kick RMS 0.3 rad and position kick RMS 0.1 × the median spacing, with recovery within T_rec and Jaccard of membership ≥ 0.9 (C4-style);
  - N within the size cap.
- **Locking:** ω, g and relative positions are frozen. The group moves as a rigid body under the C4 forces from outside. Its internal couplings stay active.
- **The identity card:**
  - the bands of its sensor and readout regions;
  - the collective rate;
  - size;
  - relative geometry (positions and phase offsets);
  - stability (recovery time);
  - task scores.
- **The sameness check:** two cards are the same type if their bands are equal, size is within ±10%, collective rate is within 5%, and **behaviour** is the same (task scores within the registered tolerance on 50 shared dev episodes).
- **A bond between placed shapes A and B (through the medium):**
  - possible only if A's output band equals B's input band;
  - **measured** as the PLV between A's readout order parameter and B's sensor-region order parameter over W;
  - **kept** if PLV ≥ L_bond and, in the reward arm, the joint task score beats both (a) the best single shape and (b) A and B placed far apart (no bond) by the registered margin;
  - a kick test applies, as for atoms.

## 7. Choosing the (dev) values, once

On dev seeds of the four atom tasks only, before any combined task:
1. A small declared grid (at most 3 values per threshold, at most 200 configurations in total, sampled by Latin hypercube).
2. Pick the configuration that maximizes the mean atom formation rate (G1) subject to G0' (growth levels off) on dev seeds.
3. Freeze it for every arm, every task and every level.
4. Report all evaluated configurations.

No later retuning. If no configuration reaches G1 on dev seeds, the stop row (section 10) applies.

## 8. Tasks, scores and atom thresholds

- **The tasks** are exactly the world's atomic and combined tasks (`growing_shapes/world/WORLD_REPORT.md`, once READY).
- **Atom threshold:** a task score at least halfway from the world's random baseline to its scripted reference, on validation seeds. **Combined-task threshold:** the same rule.
- **Training:**
  - the four atom tasks rotate in blocks of n_block episodes (changing goals, proposal section 5);
  - a total episode budget per arm is fixed before training;
  - the yardsticks get the same budget.

## 9. Predictions: operational definitions (registration later; these are the development read-outs)

| ID | Metric |
|---|---|
| G0 | The fraction of births within 2 m.u. of an active novel sensor site or a strained element, against the same count of births at random places and times (a control run) |
| G0' | The slope of N over the last 20% of training, compared with zero |
| G1 | The atom formation rate: atoms meeting the section 6 criterion per atom task, over seeds |
| G2 | Bonds formed between matched against mismatched bands, against random bonding at equal rate |
| G3 | Episodes to reach the combined-task threshold, and N, against the fixed-size, gradient and GRU yardsticks |
| G4 | The count of combined types using an identical atom type unchanged |
| G5 | Atom task scores after level-2 training, compared with before |
| G6 | G0, G0', G1, G2 and G5 in the stability arm alone |
| G7 | Duplicate instances: their stable phase offset and the difference in their output statistics |
| G8 | Library growth rate and reuse counts over the task sequence |

## 10. Stop rows (yes/no; one action; one role)

| Question | Yes → action | Role |
|---|---|---|
| Does the world or the medium report NOT_READY? | Fix it before section 7 starts | implementer |
| Does no (dev) configuration reach G1 on dev seeds? | Stop; report which atoms fail and why; the owner decides | drafter |
| Do births not track novelty or strain (G0 at chance) on dev? | Stop the growth claim; report | drafter |
| Does N grow without levelling (G0' fails) at the frozen values? | Stop; report | drafter |
| Is an outcome-informed rule change made after section 7? | Log it; restart that arm | implementer |

## 11. Open points for the review

- Whether the gain rule in the stability arm already acts as hidden selection. It rewards locking to inputs, not task success. The drafter's reading: it is resonance, not reward. To be checked.
- Whether rigid locking of an atom is too strict for bonding. The alternative is "frozen ω and g only".
- The GRU is the right neural yardstick for memory tasks; an MLP for the memoryless atoms.
