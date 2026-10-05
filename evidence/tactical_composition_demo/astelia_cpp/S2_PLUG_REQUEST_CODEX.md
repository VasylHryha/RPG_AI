# Request to Codex: session S2, the outside-controller plug in the typed C++ simulator

Repository `/Users/new/RiderProjects/ai_RPG_test`. Read `AGENTS.md`.
- **Context:**
  - `../PLAN_RESONATOR_AI.md` (session S2);
  - `../DESIGN_0G.md` section 1 (the plug) and section 5 (the owner's decisions);
  - the review `../astelia_cpp_review_claude/INDEPENDENT_REVIEW.md` (notes 1, 3, 4).
- **Approval:** the owner approved this session ("go ahead", 2026-10-05).
- **Status:** exploratory, under decision 0028. Commit with `Assisted-by: Codex:<model>`.
- **Approval does not cover:** any controller other than the three below, any tuning, or any AI experiment.

## Goal

Let an outside controller decide, for one side, each unit's move goal and target every tick. Everything after the decision stays the game's rules, unchanged and
identical for every controller: wind-up and release, cooldowns, aim checks, damage, projectiles, and the kind's dodge reflexes (`gameDash`, `gameBlock`).
The other side keeps its scripted brain, byte for byte.

## The interface (typed; shaped like Astelia's lab `tactics.h` `Policy`)

- **`struct Observation`, built by the engine for one side once per tick, before that side's units decide; read-only:**
  - **world:** t, dt, width, height;
  - **every living unit of both sides:** stable id (generation-checked, never reused), team, role (melee / ranged / artillery), x, y, vx, vy, hp, maxhp, radius, speed, range, dmg, cd, cdMax, current target id, and
    **cumulative damage dealt and cumulative damage taken** since the fight began, in hit points. The controller computes its own recent averages; the owner decided damage dealt and taken drive the controller.
  - Nothing else: no shots, shells, packs, plans, RNG, world pointer or unit pointers.
- **`struct UnitDecision`:** move goal (x, y), speed multiplier in [0, 1], stop distance ≥ 0, and target id (a living enemy, or none).
- **`class Controller`:**
  - `virtual void prepare(const Observation&)`: once per tick per side, before the units decide;
  - `virtual UnitDecision decide(const Observation&, UnitId self)`: once per unit, **in the game's own shuffled decision order**, so that a pass-through is exact;
  - an owned RNG seeded from the fight seed and the side;
  - per-fight state allowed. A controller never receives `World`.
- **Engine side:**
  - For a side whose profile is `{"controller": "<name>", "params": {...}}`, the engine:
    - skips that side's pack-level planning (lookahead, director, commander, formation plan, artillery planner, coordinated abilities);
    - calls the controller where the game's `decide(w, u)` would run, validates the decision (finite numbers, the goal clipped to the field, the target living and on the other team, else none), and
      sets the unit's move and target;
    - sets the attack relation from the role, as the game's own `decide` does (melee / direct / art).
  - Abilities stay the game's `auto` reflex (owner decision 1).
  - A registry maps names to factories. The JSON host accepts the profile form above on either side.

## Three controllers (only these)

1. `passthrough`: a test-only privileged adapter that calls the game's own `decide` for each unit, for the plumbing check. It is the only code allowed to see `World`. Mark it test-only.
2. `nearest`: target the nearest living enemy, walk to it until within 90% of own range, full speed. This is the floor arm.
3. `hold`: stand still and target nothing. A degenerate case for the validation tests.

## Acceptance (all must pass; commit the outputs)

1. **The plumbing is exact:** `passthrough` on side 0 gives byte-identical summaries **and** full traces to the built-in brain on at least 40 fights (every pool opponent, both sides,
   levels novice / regular / elite-fast on the passthrough side, rules `game`). Do the same with the controller on side 1.
2. **The other side is untouched:** with `nearest` on side 0, side 1's decisions in the first tick equal the built-in run's (a trace check).
3. **The fence:**
   - a compile-time check (a static assert, or a test that does not compile when uncommented) that `Controller` cannot name `World` through `Observation`;
   - a runtime test that the `Observation` field list equals the list above, exactly.
4. **Validation:** non-finite numbers, an out-of-field goal, a dead target and an own-team target are each handled as specified, with a test each.
5. **Cost:** with `nearest` on side 0, the time per fight is at most 1.2 times the built-in `alone` brain's on the same 50 fights, measured as in the qualification.
6. **Nothing else changes:** the existing 158 checks still pass, and a fight with no controller is byte-identical to the admitted build on the 80 reference requests.
7. **Determinism:** two runs with `nearest` give identical output.

## Report

Write `S2_PLUG_REPORT.md`: the first line `READY` or `NOT_READY`, then the check results, the files changed and every deviation with its reason. Claude reviews it afterwards.
Expected effort: about 2-4 hours.
