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
| 0g v3 (no hovering in the kill zone) | DONE: READY_FOR_S5 (review `astelia_cpp_review_claude/S4_V3_REVIEW.md`; recheck RUNNING) | **morale v3 beats novice (+24.7) and regular (+8.6) head-to-head**; the resonator beats novice (+17.4) but not regular (−7.6); on the pool resonator − morale = +0.46 [0.10, 0.82] (below δ 3.5), resonator − push-pull = +26.1 | `astelia_cpp/S4_V3_DEVELOPMENT_REPORT.md` |
| 0h growing shapes | ADOPTED as the direction [R]; rev 5.1 development FAIL (root cause: no input-to-output path; groups drift; D1-D5). **Revision 6 consolidated** (`DESIGN_0H_REV6.md`): drive-masked output oscillators, frontier bridge growth on the directed influence graph, D4 cut-off death, an engineering wall, control M (B1 only, exact match), G2 task response on perceive with donor-input and path-lesion tests, fixtures F1-F6. Codex reviews: 14 → 11 → 6 → 2 → 1 findings, then **round 6: APPROVE_WITH_NOTES** (revision 6.4; two low notes applied). Revision 6.5 adds the owner's external recheck points (the choose ceiling, move cannot stop, memory baselines). **Integration implemented** (Codex, `437e36a`; 29 contracts pass; fixtures built but not run); **Claude's implementation review running**; then Codex fixes plus the 6.5 additions (F9, memory baselines). Next: **the owner's approval of the F1-F9 fixture run (about 2 min)** | **scope narrowed to the bootstrap** (atoms and the library); combinations, bonds and duplicates deferred until C6; a task-blind arm with structural qualification only | `evidence/tactical_composition_demo/PROPOSAL_0H_GROWING_SHAPES.md` |
| 0g scripted witness P16 (splash-value gun focus) + escorts, 7 Oct | DONE | **34/40 (85%) elimination wins vs regular** (replicated), novice 40/40; first >50% witness. Spacing (enemy splash hit about 4 bunched guns) and escorts were the steps | `astelia_cpp/s4_escort_probe_v3`, `v4`; DESIGN_0G §19.4–19.13 |
| 0g v7 (per-unit oscillator gate; commit = P16 action, escape = v6) | DONE (validation, Codex recheck) | **32/40 (80%) vs regular, mean S +4.68, novice 40/40**; observed match with always-commit (31/40); the resonator's timing adds no measurable win gain yet | `astelia_cpp/S4_V7_VALIDATION_REPORT.md`, DESIGN_0G §20.3/20.3.1 |
| 0g S5 registration of v7 | WAITING (owner) | proposal revision 4, Codex round 4 APPROVE_WITH_NOTES; one-sided betting lower bound, smallest common n ≤ 200 clusters | `S5_V7_REGISTRATION_PROPOSAL.md` |
| 0h coverage line (7–8 Oct) | DONE (exploratory) | V1/RD3 stop D3 cutting live chains (empty start 5/5); ordering is not the lever (COV-A = DEBT, index 1.74); COV-B recycling 2.50; ECO-F inert; ECO-R thinning collapses the gate; front allocation 1.15 components per unserved site | `growing_shapes_review_claude/rev711_diag/medium_variants/*_REPORT.md`, `FRONT_ALLOCATION_DIAGNOSTIC.md` |
| 0h capacity diagnostic (ceiling ×1.5/×2) | DONE (Codex recheck PASS_WITH_NOTES) | **CAPACITY_SCALES_WITH_RESOURCE_CEILING**: index 2.15 → 3.21 → 3.46; far sites ×3; extra material becomes service redundancy while the front tax stays about 29–38; site 5 still starves in the empty start | `CAPACITY_DIAGNOSTIC_REPORT.md`, `docs/reviews/tactical_0h_capacity_result_recheck_codex.md` |

## 3. Waiting for the owner

| # | Decision | Options | Drafter's recommendation |
|---|---|---|---|
| W1 | C6 next step | **DECIDED 2026-10-05: B** (decision 0029): the engineering and runtime port of the unchanged R4 model | (the drafter had recommended A first) |
| W2 | Approve 0h as the direction | **read as approved 2026-10-05 [R]** (decision 0028 item 17): its engine parts are being built | confirm the [R] reading |
| W3 | Confirm the reading of "go ahead" (improve before registering) | confirm, correct | marked [R] in decision 0028 item 16 |
| W4 | What to register for 0g after v3 (S5): (a) the design as written (P1-P3 on the resonator; P1 expected to fail on regular, P2 indeterminate), or (b) add a separately labelled, outcome-informed endpoint for the morale controller's head-to-head result | after the v3 recheck | (a) plus (b), declared as such, judged on fresh seeds |
| W5 | 0h R6-2 control decision | **DECIDED 2026-10-06: both controls**; matched births (ii) registered, as-is (i) descriptive (`DESIGN_0H_REV6_DRAFT.md` section 5) | none |
| W6 | 0h: adopt the root-relative O pin (C2) for a preregistered evaluation, and the multi-key F5 gate (DESIGN_0H_REV7 §19.7) | adopt both; the gate only; neither (push the medium laws first) | the gate in any case (single-key F5 flips under every rule); C2 as the 7.12 candidate, honestly labelled a placement prior; the medium laws continue in parallel |
| W7 | 0g: approve the S5 v7 proposal (S as a reported secondary; the 200-cluster cap) | approve; amend | approve (then Codex builds the sealed spec and the planning receipt, no fights) |
| W8 | 0h after the capacity result | (a) ceiling 96 in the candidate law; (b) keep 64 and test a stall gate on B-path funding (meaningful progress 0.556); (c) (b) first, 96 as the fallback. A narrower root zone was withdrawn (FRONT_TIPS_ROOTZONE: it releases 0.1%); one-active-front targets 17–25% of the front cost | (c) |
| W9 | 0g network route after first trained nets (decisions 0035, 0036) | units act alone + tactical leader on top; stage 2 = search-guided self-improvement (Expert Iteration) instead of ES; full-army fight sooner; RRG tested at the leader (coordination); lighter dev process | **owner approved 2026-10-08** (0035 units/leader; 0036 'overall seems solid, document it'). Recheck table in 0036 | Claude |

## 3b. Recheck rule (owner, 2026-10-05: "don't forget to run recheck script for each serious chunk of work")

Every serious chunk gets the owner's adversarial recheck prompt (verbatim, through Codex), with fixes and equivalence, before the next step builds on it.

| Chunk | Recheck |
|---|---|
| 0h C++ speed pass | DONE (four high findings fixed; Claude review `growing_shapes_review_claude/PERF_RECHECK_REVIEW.md`) |
| C6 option B port and parallel step | DONE (four high and five medium findings fixed; 72 tests pass); full-world zero-tolerance reruns and the official quiet timing **stopped 2026-10-06 09:15 before measuring (the machine was busy with other work); rerun when the laptop is idle** |
| 0g v3 development | DONE (READY; the resonator dithers: its rotation flips commitment every half cycle, about 3.4 s, too fast to reach either safe distance against guns) |
| 0g v4 development | RUNNING (Codex, started 2026-10-06): DESIGN_0G section 15, a travel-time hold on mode switches, commit focus and decision traces, plus the runner deadline repairs; amended S4 protocol, fresh seeds, 360 min |
| 0h development run | DONE (CHANGES_REQUIRED for the next design: the empty read-out confirmed; new D5: no confinement, groups drift up to 246 m.u. away and 9,493/11,862 lose all sensor reach; refinements in `DESIGN_0H_REV6_DRAFT.md` section 4) |

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
| **Collective commitment** (2026-10-07): guns commit together, with a direct screen, onto the end of the enemy gun line (exposure 1 enemy gun instead of 3–4), so the enemy battery cannot pick them off one at a time | PROBE RUNNING (DESIGN_0G §19.4: P5 control, P7 wave, P8 + screen, P9 + end-of-line) | focused, committed guns (P5) rout novice 20/20 but lose all 10 guns to regular; if a scripted collective arm wins the exchange, v7 = target-group synchrony (K_t, a coherence-triggered commit wave) | `DESIGN_0G.md` §19.3–19.4 |

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
| **Ports: each shape has declared input and output ports; growth links only an output port to an input port. Inside: stable and organized; connections only at the ports** (owner, 2026-10-07). Two roles: interior cells (spring-held, ignore the general clumping pull, phases keep evolving) and port cells (the only ones that reach out or accept a link); the tip and stalk analogue of research rank 2 | PROPOSED (after one port-to-port link holds) | stops "everything connects to everything", keeps cost bounded and shapes reusable; bonds or springs would exist only along port links | rev711_diag reports |
| **A router that chooses the shape for a request, done by resonance** (owner idea, 2026-10-07): shapes tuned to signatures; a request drives only the shape that resonates | PROPOSED | the router is frequency matching, not a script. Closest known: communication through coherence (Fries 2005), mixture-of-experts gating, resonant filter banks. Difference: the gate is the shapes' own resonance | — |
| **The connection problem (2026-10-07):** we can make shapes, but cannot yet **grow and hold** a link between them. The cohesive motion law pulls a growing link back into a blob (the swarmalator compact-disc effect; Merks 2008 "round clusters") | ACTIVE | candidates: a root-relative O pin (a placement prior; 8/10 against 3/10 in an exploratory battery, report revision 2 after the Codex recheck; passing runs connect only 3–4 of 8 sensor sites); medium laws (`medium_variants/`: chain bonds 5/10, **chain bonds + screening 6/10, the best medium-only**, weak pull 4/10): they always reach O, but the signal from the roots is lost; **why it is lost is being traced (A6v)**; a third dimension (judged no help: 3D swarmalators form balls). **The F5 gate itself is unreliable with one key:** multi-key gate proposed (DESIGN_0H_REV7 §19.7, owner approval) | `REV711_F5I_DIAGNOSIS.md`, `CHAIN_GROWTH_RESEARCH_MEMO.md`, `validation_712/`, `medium_variants/` |
| **A shape that does one job becomes one node at the next level** (owner, 2026-10-07): inside it, cells keep working at their own small scale and fast clock; outside, the node shows only its ports, its resonance signature (frequency, amplitude, phase) and its cost (one node). Groups of nodes can become nodes again (recursion) | PROPOSED | the RRG recursion B_n → R_n → B_{n+1}; upper levels see summaries only and keep their own timescale (AGENTS.md normalization rules). C5 tested a simpler level-2 interface; check its open note (inherited port capacities, size-weighted natural rate: full versus coarse) before trusting a node summary. Links between nodes can use their own rule (for example port-to-port bonds) | C5, C6, 0h section 7b |
| **Different scales need different interactions, like the four physical forces** (owner, 2026-10-07; scale order per the owner's table: weak inside nucleons, strong in nuclei, electromagnetic from atoms to everyday objects, gravity for planets to galaxies): one fixed set of interactions, the same at every level, each dominating at its own range. Ours: **weak** = a cell changes kind (birth, death, root/port/interior role, frequency band); **strong** = bonds between phase-locked partners hold a shape's core, and **saturate** (at most about 2 per cell, like a nucleon binding only neighbours); **electromagnetic** = phase attraction/repulsion arranges cells and matches ports, and phase waves carry the signal (the "light"), **screened** by balanced shapes; **gravity** = a weak pull gathering shapes toward demand and outputs | PROPOSED; experiments: bonds (saturating, 5/10), bonds + O pin (running), bonds + guidance pull (running), **screening next** (a fully bonded cell stops exerting the clumping pull outside its shape) | the current medium uses one cohesive interaction and is never screened, so the whole cluster pulls every tip back. Same procedure at every level (a fixed set of interactions separated by range); physics is an analogy, not equations to copy (AGENTS.md) | `CHAIN_GROWTH_RESEARCH_MEMO.md` (contact inhibition, guidance field) |
| **Order** (owner and drafter, 2026-10-07): (1) one reliable port-to-port link → (2) the port interface → (3) compose 2–3 shapes through ports, check they don't merge → (4) resonance routing | PROPOSED | the physics of holding a link comes first; ports organize which links may form | — |

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
