# Plan: an AI built on the C4/C5 foundation, judged against Astelia's scripted AI (DRAFT for the owner; nothing built or run)

The owner (2026-10-04): our AI must be a different foundation, not a repeat of current AI; it must beat the code; the game gives clear parameters and actions;
"I want to know before we start AI how we are going to do it and how long it can take". This is that plan. Owner approval is needed before any of it is built.

## 1. The three statements every experiment must make

| | This plan |
|---|---|
| What the pieces are made of | The C4 element law, unchanged in form: each piece has a position, a phase and its own rate. Attraction grows when phases agree, there is short-range repulsion, and phases pull together (Kuramoto) more strongly the closer two pieces are (`geomind/c4_model.py:5-6`, `rhs` `:82-102`). No trained weights, no hand-written tactics. |
| How connections form | By themselves. Pieces whose phases lock pull together and become a group (a C4 resonator). Groups that lock become a bigger group (C5). Nobody assigns squads, targets or formations. |
| Closest known methods, and what differs | **Swarmalators** (O'Keeffe, Hong, Strogatz 2017): this is essentially the C4 law. **Physicomimetics** (Spears et al. 2004): virtual-force swarm control. **Potential fields / boids.** What differs here: decisions (who attacks whom, when to commit, which group acts as one) come from phase locking and group formation, the C4 geometry<->mode loop and the C5 levels, not from forces alone. Whether this adds anything over plain forces is **tested, not assumed** (P3). |

## 2. The design: the army is the resonator

- **Our units are the elements.** Each of our 50 units (10 melee, 30 ranged, 10 artillery in the default mirror fight) is one element.
  - Its position is its real position on the field.
  - Its phase is an internal rhythm, with its own rate per role.
- **Enemy units are elements too.** We can observe them but not steer them: they enter our units' equations as fixed sources. Their phase is observed, not set; it is derived from their state (for example, attacking or not), which the adapter provides.
- **What a unit does each decision tick (10 per second):**
  - **Move:** along its position law, plus a pull toward or away from enemies depending on phase agreement. Melee units seek; shooters keep their range; repulsion keeps spacing.
  - **Attack:** the enemy in range it is most phase-locked to. Units locked to the same enemy therefore focus fire on it **because they are synchronized**, not because a rule says so.
  - **Commit or withdraw:** read from the unit's phase relative to its group (in phase: commit; anti-phase: fall back).
- **Groups:**
  - Groups form and break during the fight. The C4 detector, applied to our units' positions and phases, publishes them.
  - A group acts as one through shared phase.
  - When a group breaks (formation destroyed), its units keep running the same law alone. This is the owner's layered unit: alone works without the group, and the group works when it holds. Re-forming is C7's question, measured here only as a diagnostic.
- **Parameters:**
  - 10-20 numbers: the element constants per role pair (us-us, us-enemy), rates per role, the input gains from hit points and threat, and the attack window.
  - They are tuned with our fast bench (quick checks, cache, fresh-seed grading), with the **same fight budget for every arm** (section 4).

## 3. Engineering

1. **Bench (1-2 h):**
   - the fight cache (`astelia_compose/PLAN_CACHE.md`);
   - fix the artillery crash in our copy;
   - freeze the opponent ladder before our AI plays: novice, regular, veteran, run 5's searched best, elite-fast.
2. **Adapter (2-4 h).** In our copy of the game, `decide(w, u)` (`formation_sim.js:2447`) is where every unit decides. A new brain `external` lets side 0 hand each unit's view to our controller and apply what it returns: move, target and, later, ability. The other side keeps its scripted brain. Shaped like Astelia's C++ `Policy` (world snapshot in, moves out), so the AI can later move to the real engine.
   - **Sanity check:** an external copy of the built-in `alone` brain must give the same results as the built-in one on the same seeds.
3. **Controllers (4-8 h):**
   - the resonator AI (section 2);
   - two simpler controllers on the same adapter: **potential field** (the same forces, phases removed) and **nearest** (walk to the nearest enemy, shoot it);
   - the group detector on our units, logged every second.
4. **Speed (owner decision 2026-10-04):**
   - The game is ported to **C++** by **Codex** (`astelia_cpp/PORT_REQUEST_CODEX.md`), with a bit-exact equivalence check against the JS, before the adapter is built.
   - The adapter and the controllers are then written once, in C++.
   - Estimate: about 4-6 hours (a diff tool finds the first differing step automatically), for a 3-10x faster game.
   - The ladder is frozen in JS first (S1), so it is measured on the original game. The exact port makes it valid in C++ too.

## 4. The test (registered after development; predictions that can fail)

**Arms:**
- the resonator AI;
- its ablations: no phase-to-geometry (J=0), no phase coupling (K=0), no groups (each unit alone);
- potential field;
- nearest.

Every arm is tuned with the same number of fights on development seeds, then judged once on fresh seeds against the frozen ladder (19 opponents, both sides).

- **P1 (it works):** the resonator AI beats novice and regular on fresh seeds.
- **P2 (the loop matters):** it beats each of its own ablations by a registered margin. If the J=0 or K=0 version does as well, the geometry<->mode loop is not doing the work.
- **P3 (it differs from known methods):** it beats the potential-field controller by a registered margin. If not, the honest reading is that phases add nothing here and this is physicomimetics.
- **P4 (groups are real and matter):** groups form in most fights. Fights where our groups hold longer are won more. Breaking a group (a forced phase scramble) costs measurably.
- **Stretch, not predicted:** veteran, the searched best, elite.

## 5. Time

| Step | Agent work | Machine time |
|---|---|---|
| Bench: cache, fix, frozen ladder | 1-2 h | 30 min |
| Adapter + sanity check | 2-4 h | 15 min |
| Resonator AI, baselines, detector | 4-8 h | |
| Development runs (tune, look, fix) | | 3-6 runs, about 30-60 min each |
| Registration, Codex review, owner approval | 2-3 h, plus review time | |
| One recorded run + report | 1-2 h | 1-2 h |
| **Total** | **about 2-4 working days** | **about 5-10 h** |

The largest uncertainty is the development step. If the resonator AI cannot beat novice after the tuning budget, we stop and report that before registering anything.

## 5a. Revision 2 of the design (2026-10-05)

After the Codex design review (`docs/reviews/tactical_0g_design_review_codex.md`, CHANGES_REQUIRED), `DESIGN_0G.md` revision 2 is the **single executable contract** for S3-S5. It covers:
- the controllers' equations;
- the knobs;
- the panels;
- inference;
- the stop rows.

Where this plan's older text differs, the design wins. The rows below are updated to match it.

## 5b. Changes after the owner's review (2026-10-04)

`DESIGN_0G.md` section 3 replaces sections 2 and 4 of this plan where they differ:
- the score is units left (main) and damage difference (second);
- four arms (resonator, plain morale, push-pull, nearest), and the J=0 / K=0 / no-groups / no-damage ablations are development diagnostics only;
- at most about 10 knobs;
- start small, then scale;
- watch fights;
- a Codex review of the design before code.

P2 becomes "beats plain morale" and P3 "beats push-pull", with the same rule (a paired difference in units left above a registered margin). P4 stays a diagnostic unless development shows it is attainable.

## 6. Implementation plan: sessions, checks and acceptance criteria

Each session ends with a commit and a short report to the owner. A session that fails its acceptance stops the plan at that point: the next session does not start
until the failure is fixed or the owner decides. Tests run once, at the end of each session's change batch (AGENTS.md).

| Session | Builds | Acceptance (all must hold) | Agent time | Machine |
|---|---|---|---|---|
| **S1 Bench** | `cache.js` (fingerprint, fight memory, spot check, seed ledger), the artillery-crash fix in our copy (recorded in `SOURCE.md`), the frozen ladder file | (a) a repeated identical search plays 0 new fights; (b) a changed game byte gives a new cache folder; (c) the spot check refuses a forged result; (d) the ladder (novice, regular, veteran, run 5 best, elite-fast) has its results on **development** seeds committed with hashes before any controller exists (judging seeds are drawn at S5 and never inspected; design rev 2 section 6); (e) `test_cache.js` passes | 1-2 h | 30 min |
| **S1b C++ port (Codex)** | the whole simulation in C++ (`astelia_cpp/`), host with JSON lines in and out, batch mode | (a) at least 400 check fights identical to the JS, field by field; (b) the full state is equal at every step on 20 fights; (c) determinism; (d) the speed-up measured; (e0) the permanent reference gate (`check_reference.py`, about 80 fights against the frozen JS) prints `identical`, and every later C++ change must keep it so, or change JS and C++ together with a recorded reason; (e) `PORT_REPORT.md` says READY; (f) a Claude review of the port | 4-6 h (Codex) | 1 h |
| **S2 Adapter** | brain `external` at `decide(w, u)` (in the C++ port); what a unit sees (own state, allies and enemies in sight: position, velocity, HP, role, range, cooldown) and what it may return (move vector, target id; abilities later); `nearest` controller | (a) **plumbing:** a pass-through controller that calls the game's own decision gives byte-identical summaries and traces on 40 fights (an outside copy of `alone` cannot work: the built-in brain reads shots, which the observation excludes); (b) `nearest` plays 114 fights with no error; (c) the adapter adds under 20% to fight time; (d) the controller cannot read anything outside its view (a test feeds a poisoned hidden field and checks it is never read) | 2-4 h | 15 min |
| **S3 Controllers (C++)** | the plug extensions and the resonator, plain morale and push-pull controllers on the S2 plug; the group diagnostics (design rev 2 sections 2-4, 7, 8) | every check in design rev 2 section 8: the C4 reference to 1e-9, the enemy-term sign, damage rates, ordering independence, degenerate cases, failure reporting, clone memory, determinism, cost, 38 failure-free fights per arm, step refinement; the 80 reference requests and the S2 passthrough fixtures unchanged | 4-8 h | 30 min |
| **S4 Development** | 10v10 melee first, then full armies (owner); tuning by the one protocol of design rev 2 section 5 (equal budgets for resonator, morale, push-pull; nearest untuned); fights watched; paired spread measured on a development split and a separate validation split | (a) budgets and every candidate logged; (b) the stop rows of design rev 2 section 10; (c) δ proposed and n chosen by a power rule (section 6); (d) raw results committed | 2-4 h | 3-6 runs, 30-60 min each |
| **S5 Registration** | `SPEC_0G.json` (frozen parameters, seeds from the ledger, endpoints, thresholds, alpha) and `SPECIFICATION_0G.md`; prompt for Codex | Codex verdict APPROVE or APPROVE_WITH_NOTES; every endpoint has a verdict rule that code computes | 2-3 h | |
| **S6 Recorded run** | owner approval naming the specification; one run; report | the run uses exactly the registered spec (hash-checked); every endpoint reported as evaluated or not_run with a reason; report states the verdicts and limits | 1-2 h | 1-2 h |
| **S7 Review** | a cross-family review of the committed result | review file with the verdict, reviewer family and results hash | owner/Codex | |

**The experiment's acceptance criteria** are in `DESIGN_0G.md` revision 2, section 6. That section has:
- P1, head-to-head against novice and regular;
- P2, beats plain morale;
- P3, beats the specified push-pull baseline;
- clustered seeds, alpha 0.01/3 per endpoint with a separate refutation budget, and verdict rules.

The older P1-P4 text with "114 fights" and the J=0 / K=0 / no-groups ablations is withdrawn (its causes are in design section 9). Groups are diagnostics only (design section 7).

## 7. Risks, stated now

- Phases may add nothing over forces. P3 would then be refuted, and that is the result.
- Group formation in C5 was about 50% (17/30), so groups may form rarely in fights. P4 measures it, and the controller works without groups (every unit runs the law alone).
- Tuning 10-20 numbers by search is itself ordinary optimization. The claim is about what the tuned law does (P2-P4 against equally tuned ablations and baselines), never that the tuning is new.
- C4/C5 never computed anything (no task or usefulness claim; the C6 drive and readout design was never completed). This would be the first use of the law as a controller.
