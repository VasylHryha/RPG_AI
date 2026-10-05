# Ideas, options and roadmap (one place to track and review)

Started 2026-10-05 at the owner's request: "document all this, all options and ideas, in one document to keep track of it and be able to review it later".
- **Use:** read the top three sections for "where are we"; the catalogue for "what did we consider and why"; the roadmap for "what next".
- **Update rule:** every new idea, option, decision or result gets a line here, with its status and a link. Status words: **ADOPTED**, **PROPOSED**, **PARKED**, **REJECTED**, **DONE**, **RUNNING**, **WAITING (owner)**.
- **Authority:** this document tracks; it does not override `STATUS.json` (milestone status), decision records (`docs/decisions/`) or registered specifications.

## 1. The goal, in plain words

Build AI from **shapes** instead of one big learned block:
- small parts with one job each;
- parts connect by **compatibility** (matching rhythm or frequency, the owner's foundation) and act together as a bigger part;
- the bigger parts connect again, level after level;
- structure **grows and dies** by clear conditions;
- reusable shapes are kept in a library, like atoms in a periodic table.

The theory chain is frequency → resonance → resonator → self-recreation → new options → new geometry. In RRG v0.2.1 terms that is background B0 → resonator R0 → changed background B1 → R1 → ….

The test of "real" is that the AI wins against Astelia's scripted AI in a game rich enough that winning cannot be faked.

## 2. Where we are (2026-10-05)

| Line | Status | Short result | Main record |
|---|---|---|---|
| C0-C5 milestones | ACCEPTED (C4, C5: groups form; many resonators become one) | the foundation's accepted results | `STATUS.json`, `evidence/c4_r003_review_codex/`, `evidence/c5_r003_review_codex/` |
| C6 recursion (B → R → B) | BLOCKED (R006 runtime STOP) | too slow (about 550 s per world against 360 s); plus a warning sign: a changed background may suppress the next unit | `docs/decisions/0024…0027`, `docs/reviews/c6_unblocking_synthesis_gpt.md` |
| 0d/0e small trained pieces (AIM, MOVE) | DONE | connection worth +0.124 against a coherent alternative; standard small networks | `evidence/tactical_composition_demo/REPORT_0E.md` |
| Astelia switch search (runs 1-5) | DONE, stopped | finds skill groups bottom-up (pairs that only work together); it tunes the game's own scripted skills, so it is **not** a new foundation; now a bench and opponent | `evidence/tactical_composition_demo/astelia_compose/README.md` |
| Typed C++ game engine | DONE (reviewed APPROVE_WITH_NOTES) | about 12× faster than the JS; same ladder order; compare only within one engine | `astelia_cpp/PORT_REPORT.md`, `astelia_cpp_review_claude/INDEPENDENT_REVIEW.md` |
| AI plug (S2) and controllers (S3) | DONE (reviewed) | our AI controls units through a clean view; resonator, plain morale and push-pull built | `astelia_cpp/S2_*`, `S3_*`, the reviews |
| 0g tuning (S4) | DONE | the resonator beats novice head-to-head (+5.9) but loses to regular (−8.7); it equals or trails plain morale (−1.1); it beats push-pull by about 7.3 | `astelia_cpp/s4_amended_development/`, `astelia_cpp_review_claude/S4_*` |
| 0g final test spec (S5) | WITHDRAWN unrun (marked inside `SPEC_0G.json`; its hash changed, so it can never pass the review gate) | four Codex review rounds, APPROVE_WITH_NOTES; the runner was approved; withdrawn to improve first; seeds never used | `SPEC_0G.json`, `docs/decisions/0028` items 15-16 |
| Replay viewer | DONE | the **retreat trap** found: enemy guns out-range our units, damage keeps them pulled back | `viz_0g/` (claude.ai/artifact/4AhiRJomJTM8QcVRLEWWWL, private until the owner shares it) |
| 0g v1 (two fixes) | DONE: STOP at B | melee: the resonator is ahead of morale for the first time (+5.05 against +4.82); full armies: novice −0.11, regular −9.56, 8 of 10 guns survive. Root cause: the preferred distance exceeded the unit's own reach (f = 1.11), and the unanswered label was too coarse | `astelia_cpp/S4_V1_DEVELOPMENT_REPORT.md`, `astelia_cpp_review_claude/S4_V1_REVIEW.md` |
| 0g v2 (range-aware distance, threats) | DONE (NOT_READY: stage C hit the runtime cap) | **full armies vs novice: resonator +16.4** (morale +9.7); vs regular: resonator −4.1 (improved from −9.6), morale +2.9; most guns still survive. Stage C (P2/P3 pool) still to run | `astelia_cpp/S4_V2_DEVELOPMENT_REPORT.md`, `astelia_cpp_review_claude/S4_V2_REVIEW.md` |
| 0g v3 (no hovering in the kill zone) | RUNNING (Codex: implement, then A/B/C with a 360-minute allowance) | the v2 replay: the line was won by 62 s with 34 units alive, then the guns killed all 34 while they hovered at 294-416 px; v3 makes out-ranged commit/escape binary with hysteresis | `DESIGN_0G.md` section 14 |
| 0h growing shapes | ADOPTED as the direction [R]; engine RUNNING (Codex: 2D task world, C4 medium); `DESIGN_0H.md` **revision 5.1, approved with notes (Codex review r5)** after reviews of 14, 10, 10 and 9 findings; implementation DONE and reviewed (175 tests; a native speed pass, then the owner-requested C++ recheck: four high findings fixed); **the section-10 development run is approved as designed (decision 0028 item 19: "C then A") and starts automatically when 0g v3 finishes**; estimated 21-55 h serial compute, about 4-10 h wall in parallel | **scope narrowed to the bootstrap** (atoms and the library); combinations, bonds and duplicates deferred until C6; a task-blind arm with structural qualification only | `evidence/tactical_composition_demo/PROPOSAL_0H_GROWING_SHAPES.md` |

## 3. Waiting for the owner

| # | Decision | Options | Drafter's recommendation |
|---|---|---|---|
| W1 | C6 next step | **DECIDED 2026-10-05: B** (decision 0029): the engineering and runtime port of the unchanged R4 model | (the drafter had recommended A first) |
| W2 | Approve 0h as the direction | **read as approved 2026-10-05 [R]** (decision 0028 item 17): its engine parts are being built | confirm the [R] reading |
| W3 | Confirm the reading of "go ahead" (improve before registering) | confirm, correct | marked [R] in decision 0028 item 16 |
| W4 | Later: approve δ, n and the run of a new 0g specification | after v1 development | registered only after review |

## 3b. Recheck rule (owner, 2026-10-05: "don't forget to run recheck script for each serious chunk of work")

Every serious chunk gets the owner's adversarial recheck prompt (verbatim, through Codex), with fixes and equivalence, before the next step builds on it.

| Chunk | Recheck |
|---|---|
| 0h C++ speed pass | DONE (four high findings fixed; Claude review `growing_shapes_review_claude/PERF_RECHECK_REVIEW.md`) |
| C6 option B port and parallel step | RUNNING (no full worlds during the timed 0g run; full-world reruns queued for the quiet window) |
| 0g v3 development | after it finishes |
| 0h development run | after it finishes |

## 4. Catalogue of ideas and options

### 4.1 Search and composition (how parts are combined)

| Idea | Status | Why / outcome | Link |
|---|---|---|---|
| Measure connection quality by performance | ADOPTED | the basis of every comparison | decision 0028 |
| Bottom-up growth: pairs, then a 3rd and 4th part while performance rises | DONE | worked; stops at a ceiling | astelia_compose run 1 |
| Synergy: parts that only work together (atoms) | DONE | found automatically (castDodge + smart shells, +9.3 together) | runs 4-5 |
| Quick checks (racing), one change after another | DONE | about 10× fewer fights per round | `compose_seq.js` |
| Two-step check (harmful-alone parts) | DONE | finds pairs that single steps miss | run 4 |
| Grow units separately, then merge (bigger things) | DONE (partly) | units grew; the merges never ran (stopped) | run 5 |
| Fight cache, seed ledger, combination library | DONE | JS search: `astelia_compose/cache.js`. C++ runs use Codex's `astelia_cpp/result_cache.py` and seed ledgers (settled in S4) | both |
| CMA-ES for continuous knobs | ADOPTED | better than the switch rule for smooth knobs | `astelia_cpp/S4_AMENDED_PROTOCOL.md` |

### 4.2 The game bench

| Idea | Status | Why / outcome | Link |
|---|---|---|---|
| Use Astelia's richer JS game (kiting, abilities) | DONE | rich enough to matter | `astelia_snapshot/` |
| Port the game to C++ (owner: Codex does it) | DONE | an exact port first (5× slower), then a typed rewrite about 12× faster | `astelia_cpp/` |
| Keep the JS as the frozen reference | ADOPTED | comparisons are statistical after the typed rewrite | reviews |
| A clean plug for outside AI | DONE | the AI sees positions, HP, ranges and damage dealt and taken; it decides move and target | S2 |
| A replay viewer to watch fights | DONE | how the retreat trap was found | `viz_0g/` |
| Let the AI see projectiles in flight | PARKED | built-in brains read shots; novice does not dodge, so it is not the cause against novice | S4 reviews |
| Controller speed (neighbour grid, fewer updates) | PARKED | our controllers cost about 10× the nearest controller per fight | S4 original review, note 4 |
| Astelia's own C++ lab (real engine) as the final exam | PARKED (later) | movement-only control and 7-27% engine errors today | `astelia-hunte/experiments/tactics_lab` |

### 4.3 The controller (0g)

| Idea | Status | Why / outcome | Link |
|---|---|---|---|
| The army is the resonator (units are C4 elements) | DONE (v0) | beats novice; retreat trap against regular | `DESIGN_0G.md` |
| Damage dealt and taken drive the beats (owner) | ADOPTED | replaced the weapon-cycle idea | design section 2 |
| Focus fire from synchronization | ADOPTED as mechanism; claim removed | not guaranteed (review) | design section 3 |
| Plain morale twin (the beat replaced by a number) | ADOPTED as a comparison | the cleanest test of "does the beat matter"; so far it does not | design section 4 |
| Push-pull (forces only), nearest (floor) | ADOPTED as comparisons | resonator and morale beat push-pull by about 7 | S4 |
| v1: unanswered damage → attack; targets prefer engaged enemies | RUNNING | the fix for the retreat trap; no new knobs | design section 12 |
| Layered unit (alone / formation / group, fall back when broken) | PARKED → C7 / 0h | the owner's idea; natural in a growing medium | this document 4.5 |
| Self-adjusting knobs during play | PARKED | "self-recreation"; after v1 | design section 7 |

### 4.4 Learning (how shapes are made, not hand-written)

| Idea | Status | Why / outcome | Link |
|---|---|---|---|
| Train a big neural network, find the sub-network for a job, cut it out, build a library (the owner) | PROPOSED as a **helper** | lottery tickets and circuits are real, but tangled and hard to transplant | 0h section 9 |
| Neural networks are brute force over paths; the geometry they find is often clean (grokking learns rotations) | INSIGHT | supports "the right shape can be oscillation" | Nanda et al. 2023 |
| Resonance is what shapes neurons; geometry is frozen resonance (the owner) | ADOPTED as a framing | with the addition: resonance learns the **data**, and selection (reward) picks the **job** | 0h section 4 |
| A trainable C4 medium (AKOrN-like, gradient through the dynamics) | PROPOSED as a yardstick | Kuramoto-neuron networks work (AKOrN, ICLR 2025) | 0h section 4 |
| Resonance + selection (three-factor) learning | PROPOSED | the reward arm of 0h | 0h section 4 |

### 4.5 Growing shapes (0h)

| Idea | Status | Why / outcome | Link |
|---|---|---|---|
| Simplest atomic shapes on tiny tasks (perceive, move, remember, choose) | PROPOSED | the bootstrap | 0h section 6 |
| Learn → lock → publish an interface (identity card) → library | PROPOSED | C5 interface; avoids forgetting | 0h sections 4, 7b |
| Bonds: matching type (band) + benefit + stability (atoms) | PROPOSED | form only where possible; keep only where they help and hold | 0h section 6 |
| A common language: direction = phase, strength = amplitude, memory = held phase, kinds = frequency bands | PROPOSED (a design choice) | makes compatibility band matching, not a declared list | 0h section 6 |
| Growth and death as the main mechanism, with exact conditions (the owner) | PROPOSED | novelty birth, strain split, need birth; death when unlocked, useless or over budget | 0h section 3 |
| A shared medium (background); shapes bond through it | PROPOSED | required by RRG background transformation; needs C6 | 0h sections 1, 8 |
| Stability-only arm against stability + reward | PROPOSED | tests the theory alone against our addition (G6) | 0h section 4 |
| Nature's four conditions: changing goals, connection cost, routing by synchrony, staged locking | PROPOSED | modularity research and neuroscience | 0h section 5 |
| Types against instances; duplicates in one shape; shared building blocks (the owner) | PROPOSED | like H2O; a sameness check stops library bloat (G7, G8) | 0h section 7c |

### 4.6 C6 (the recursion milestone)

| Option | Status | Note | Link |
|---|---|---|---|
| A: a pilot, quiet against changed background | NOT CHOSEN (W1) | the apparatus concern stays open | synthesis section 5 |
| B: C++ port of the unchanged R4 model | **ADOPTED / RUNNING** (decision 0029) | profile, port the hot paths, check equivalence, measure world runtime against 360 s | `docs/decisions/0029-c6-option-b-engineering-port.md` |
| C: pause | NOT CHOSEN | | |

## 5. Roadmap (in order)

| Step | What | Depends on | Status |
|---|---|---|---|
| 1 | Finish 0g v1 development, review it, update the replays | Codex run | RUNNING |
| 2 | A new 0g specification on a fresh root; the approved S6 runner adapted and re-reviewed; Codex review; owner approval; one recorded run | step 1, W4 | next |
| 3 | C6 option B: profile and port (Codex), Claude's review | decision 0029 | DONE: equivalence exact; runtime FAIL (worst world 953 s wall, 662 s CPU); 70% of the time was already-native compute. Next: parallel grids and forks inside a world (RUNNING), then a quiet-machine measurement |
| 4 | C6 R007 registration (the owner approves), then one run | step 3 | waiting |
| 5 | 0h design (thresholds fixed) and the tiny 2D task world, Codex review | W2 (**not** C6: the atoms need only a fast C4 medium) | waiting |
| 6 | 0h bootstrap: atoms grow and are locked into the library | step 5 (parallel with steps 3-4) | |
| 7 | 0h combinations: seeded media grow level-2 shapes | steps 6 and 3 (the C6 pilot's answer on background suppression) | |
| 8 | Level-2 and level-3 shapes control units on the Astelia bench | step 7 | |

## 6. Lessons learned (so they are not repeated)

- **Recheck 2026-10-05:**
  - a withdrawn specification must say so inside the governing file, not only in a decision;
  - a formula change must restate its normalization;
  - long runs must bind to committed code;
  - dependencies are split by step, so independent work is not blocked.

- **The line drifted once** into tuning the game's own scripted skills (the switch search). Every experiment now states what its pieces are made of, how connections form, and the closest known method.
- **Specify before building:** design revision 1 had contradicting formulas and a sign error; the S5 specification took four review rounds. Write equations and data formats exactly, and run the sign and degenerate-case checks early.
- **Watch the fights:** the retreat trap was obvious in a replay and invisible in the averages.
- **Speed matters scientifically:** C6 stopped on runtime. A typed C++ engine turned hours into minutes.
- **An exact copy is not the same as a fast copy:** a mechanically translated port was exact but 5× slower; the typed rewrite was fast but only statistically equal.
- **Development seeds and judging seeds are kept apart;** an unrun registration can be withdrawn honestly, a run one cannot.
- **Usefulness is not in the theory:** reward is a labelled addition, tested against stability alone.

## 7. Key files

- **Decisions:** `docs/decisions/0028-owner-directed-exploratory-composable-shapes.md` (this line's owner messages and approvals), `0024`-`0027` (C6).
- **0g:** `evidence/tactical_composition_demo/DESIGN_0G.md`, `PLAN_RESONATOR_AI.md`, `SPEC_0G.json` (withdrawn), `astelia_cpp/` (engine, plug, controllers, S4), `astelia_cpp_review_claude/` (reviews), `viz_0g/`.
- **0h:** `evidence/tactical_composition_demo/PROPOSAL_0H_GROWING_SHAPES.md`.
- **Search and bench:** `evidence/tactical_composition_demo/astelia_compose/`.
- **Reviews from Codex:** `docs/reviews/tactical_0g_*`.
