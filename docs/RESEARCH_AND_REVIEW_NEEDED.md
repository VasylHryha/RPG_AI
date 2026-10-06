# What needs deeper research, and what needs review (2026-10-06)

This document is meant to be given, whole, to a research assistant that cannot see the repository. Sections A and B are self-contained. Section C lists what is already closed. Section D lists what needs review, and by whom.

## A. Context, for the researcher

We are building an AI from a different foundation than neural networks trained by backpropagation. It does not replace them; the point is to test whether this foundation works.

**The foundation:**
- Many small **oscillators** (phase θ, natural frequency ω), coupled to near neighbours with Kuramoto-like coupling.
- Inputs are **phase drives**: a sensor site pushes nearby oscillators toward the phase that encodes a direction.
- Things connect by **matching rhythm**. Groups that lock together act as one and become a reusable "shape".
- The structure **grows and dies** under explicit rules:
  - a birth near a sensor that no element has locked to for 20 s;
  - death of an element that has not locked to anything for 40 s;
  - removal of the weakest elements when a cost budget (N + 0.1 × neighbour pairs ≤ 64) is exceeded.
- Locked groups are **qualified** with fixed structural tests and copied into a **library**. The long-term plan is that library shapes combine into larger shapes, level by level.
- **Output:** the phase coherence of elements near the medium's centre is decoded into an action (a direction, a speed or a choice), or the medium abstains when coherence is too low.

There are two test beds:
1. **"0h", growing shapes:** a tiny 2D world with four atom tasks:
   - perceive the direction of an enemy;
   - move toward a target;
   - remember a hidden target;
   - choose the best enemy.
2. **"0g", the resonator controller:** in a rich real-time tactical battle game (dozens of units, melee and guns), a phase oscillator per unit sets its commitment (attack or escape) from the damage it deals and takes. The goal is to beat the game's scripted AI.

**What happened (the facts to research against):**
- **0h:** the growth machinery works. 11,862 structures formed and qualified over 16 runs of 2,000 episodes, and their copies reproduce exactly.

  But **the medium never acted**. All growth happens at the sensor ring (radius 4), while the read-out looks only within radius 2 of the centre. No rule ever grows a path from the sensors to the read-out, so every episode abstains. The population also fills its cost budget (about 44 elements) and then just churns, covering only 6–22% of the sensor sites.

  A later recheck found that nothing keeps structures in place. Locked groups drift away freely, up to 246 units from the centre, and 80% of the qualified structures (9,493 of 11,862) end up out of reach of every sensor. Only 64 perceive, 51 memory and 1 choose structure, out of the 320 scored, did better than both doing nothing and random. None did for move.
- **0g:**
  - The oscillator controller beats the weaker ("novice") script by a wide margin, but loses to the stronger ("regular") one.
  - A simpler non-oscillating "morale" variable beats both scripts.
  - Diagnosis: the oscillator's built-in rotation flips each unit between attacking and escaping about every 3.4 s. That is too fast to cross the 270 → 606 px gap between the two safe distances against guns, so units waver in between.

## B. Research questions

For each question we need:
- **what is known**, with sources (papers and the year, with links);
- **which approach fits our foundation**, meaning oscillators, phase, locking, growth and death, and no backpropagation through the whole system;
- **what it would repeat from existing AI**, so we can avoid rebuilding a standard neural network under another name;
- one concrete **mechanism or rule we could adopt**, with its conditions stated as numbers or formulas where the literature allows.

### B1. Getting an action out of an oscillator network (most important)

1. How do networks of coupled oscillators produce task outputs? Cover:
   - Kuramoto-style networks for machine learning (for example AKOrN, "Artificial Kuramoto Oscillatory Neurons", ICLR 2025);
   - oscillatory neural networks and phase-based computing hardware;
   - reservoir computing with oscillators;
   - binding by synchrony;
   - central pattern generators.
2. What read-outs work **without** a large trained output layer? Examples: phase of a designated output oscillator, synchrony between groups, winner-take-all by first-to-lock, order parameters per cluster.
3. How do they avoid the **trivial echo**? A read-out next to a sensor just copies the input phase; we need read-outs that score only when the structure transforms the input (for example remembering, choosing, or combining two inputs).
5. How do self-organizing oscillator or particle media keep structures **anchored** to their inputs and outputs, rather than drifting away? Cover anchoring forces, boundaries, chemotaxis-like attraction to active sites, and death on losing contact. Which of these preserve the free self-organization?
4. In growing systems, how does the structure **reach the output**? Is there known work where growth is driven by output demand: growth cones, axon guidance analogies, activity-dependent wiring toward targets, developmental neural networks?

### B2. Networks that grow and prune units

1. How do growing networks give credit to a newly added unit, and decide whether it stays? Cover:
   - NEAT and HyperNEAT;
   - cascade-correlation;
   - growing neural gas;
   - neurogenesis and synaptic-pruning models;
   - neural cellular automata;
   - developmental encodings.
2. How is a growing population judged **stable** when it lives at its resource budget with steady turnover? Are there standard criteria that separate budget-limited from need-limited growth?
3. How do such systems avoid "fill the budget, then churn" (our 0h result)? Do they use births that need a measured benefit, birth rates that fall with crowding, or protected periods tied to progress?

### B3. Local credit without backpropagation

1. How do local rules tie a group of units to the job it helps with? Cover:
   - three-factor learning (Hebbian plus a reward or neuromodulator signal);
   - e-prop;
   - reward-modulated STDP;
   - cell assemblies (Hebb), and the assembly calculus of Papadimitriou et al.
2. Which of these work when the units are **phase oscillators**, so that the learned quantities are frequency, coupling gain and phase offset rather than weights?

### B4. Measuring whether a module is useful

1. How do researchers show that a discovered module or sub-circuit is useful for a task? Cover ablation and lesion tests, mutual information with task variables, causal tracing, and mechanistic interpretability (circuits, lottery tickets).
2. Which methods work for **small dynamical modules** that can be copied into an empty medium and run alone?

### B5. Stopping a rhythmic controller from wavering (0g)

1. In oscillator- or CPG-based control, how is a decision kept stable long enough to finish an action? Cover:
   - gait-transition hysteresis;
   - dwell times;
   - phase resetting;
   - decision models with commitment (drift-diffusion with collapsing bounds, winner-take-all attractors with hysteresis).
2. How should a minimum commitment time scale with the travel time to the goal (here, distance gap ÷ speed)? Is there a principled rule?
3. Is there work where the oscillation itself carries the decision (for example a phase-locked "attack window"), rather than being suppressed?

### B6. Novelty check

Which existing methods are **closest** to our foundation (oscillators that lock into reusable shapes, grow and die, form a library, and combine level by level)? For each one, what is the key difference? If something already does exactly this, we must know.

### B7 (optional). Nested synchronization across levels

When a group of locked oscillators acts as one unit at a higher level, does the higher level's rhythm (the "background") disturb or suppress the lower groups' locking? What does the hierarchical and nested oscillation literature say: theta–gamma nesting, multiscale Kuramoto, chimera states?

**How to return the research:** one section per question, B1–B7. Each section has a short answer, sources with links, the "fits our foundation / repeats existing AI" assessment, and the one adoptable mechanism. Mark anything uncertain as uncertain.

## C. What is closed (Claude's part, committed)

| Item | Where | Commit |
|---|---|---|
| The 0h development run imported, without its 14 GB raw ledgers (kept on disk, identified by hash) | `growing_shapes/runner/development_20261006/LEDGERS_NOT_IN_GIT.md` | `7e5f6b0` |
| Claude's review of the run, with the addendum showing the identical-to-every-digit floor and the budget-pinned population | `growing_shapes_review_claude/DEVELOPMENT_REVIEW.md` | `a5394e9`, `6960d39` |
| **The failure report and the revision-6 draft:** the root cause (no path from sensors to read-out) and fixes R6-1, R6-2 and R6-4 | `evidence/tactical_composition_demo/DESIGN_0H_REV6_DRAFT.md` | this commit |
| The 0g v3 recheck reviewed (the wavering diagnosis) | `astelia_cpp_review_claude/S4_V3_REVIEW.md` | `bcff7b1` |
| Delivery records tracked; bundles ignored | `.gitignore` | `ca4d973` |
| Process: keep unattended runs awake; raw ledgers out of git | memory, and R6-4 | n/a |

## D. What should be reviewed, and by whom

| # | What | Reviewer | When | Status |
|---|---|---|---|---|
| 1 | The 0h development run and Claude's root-cause finding (the owner's recheck prompt) | Codex | automatically, after the C6 timing | QUEUED |
| 2 | The C6 quiet-machine timing (is every world ≤ 360 s?) | Claude | when Codex's `evidence/c6_option_b/QUIET_REPORT.md` lands | RUNNING since 08:44 |
| 3 | The 0h revision 6, once R6-3 is chosen with the research above | Codex (cross-family), then the owner's approval | after B1–B4 return | WAITING ON RESEARCH |
| 4 | A 0g resonator v4: a mode dwell tied to travel time, a vector-feasibility check, and decision traces | drafted by Claude, reviewed by Codex | after B5 returns, if the owner wants it | WAITING ON THE OWNER |

**Decisions for the owner:**
- **W4:** what to register for 0g S5: the design as written, or that plus a separately labelled morale endpoint.
- Whether to do the resonator v4.
- Confirming Claude's readings of decision 0028, items 16–18.
- After the research: which output mechanism 0h revision 6 uses, from options (a)–(d) in the draft.
- Where to keep the 14 GB of 0h ledgers long-term: an external disk or cloud storage. They are on the laptop now, and the disk is 93% full.
