# Design 0g: the AI plug and the resonator controller (DRAFT for the owner; no controller code exists)

Companion to `PLAN_RESONATOR_AI.md` (sessions S2 and S3). Development may revise the controller before registration (S5). Every revision is recorded here with its reason,
and registration freezes it.

## 1. The plug (S2): what our AI sees and what it may do

**Where:** in the game's tick (`formation_sim.js` `step`, line ~2908 `for (const u of order) decide(w, u)`), side 0 units with brain `external` skip the game's `decide`. They get their
decision from our controller instead. Everything after the decision is the game's rules, unchanged and identical for every arm:
- the wind-up and release of attacks;
- cooldowns and aim checks (`act`, `prepared`, `aimClear`);
- damage, shots and shells, the dodge reflexes of a kind (`gameDash`, `gameBlock`, part of a unit's body, not its mind).

For side 0 with brain `external`, the pack-level planning is off (`lookahead`, `directorStep`, `commander`, `formationPlan`, the artillery planner), since that is the game's decision code.

**What one decision sees** (one snapshot per tick, built once, read-only; the same shape as Astelia's C++ `World` plus the fields below):

| | Fields |
|---|---|
| world | t, dt, width, height |
| own unit | id, role (melee / ranged / artillery), x, y, vx, vy, hp, maxhp, r (radius), speed, range, dmg, cd, cdMax, current target id, **recent damage dealt, recent damage taken** |
| every living ally | the same fields |
| every living enemy | id, role, x, y, vx, vy, hp, maxhp, r, range, **recent damage dealt (to our side), recent damage taken (from our side)** |

Recent damage is an exponential average of the hit points lost and dealt, with time constant T_d (a knob). The game already records every hit, so the plug only passes it through.

All units are visible (as in Astelia's lab: "policies read true positions"). A sight limit is a later fidelity step.

Declared after the S2 review (`astelia_cpp_review_claude/S2_REVIEW.md`, notes 1 and 2):
- **Every unit's current target is visible, the enemy's included.** Who attacks whom is visible on screen.
- **Timing:** a controlled side sees one snapshot taken at the start of each tick, while a built-in side decides unit by unit within the tick. This is the same for every controller arm.
- **`passthrough` is test-only** and is never an arm.

**What it returns per unit:** a move goal (x, y, speed multiplier 0-1, stop distance) and a target id (a living enemy, or none). The attack type comes from the role, as the game's own
`decide` sets it (melee / direct / art). Abilities: v0 leaves them to the game's `auto` reflex, the same for every arm (declared as part of the world). Controlling them is a later version.

**Plug tests (S2 acceptance):**
- an external copy of the game's `alone` brain is bit-identical to the built-in one on 40 fights;
- a poisoned hidden field (one not in the table above) is never read;
- the `nearest` controller plays 114 fights with no error.

## 2. The resonator controller v0 (S3)

**Pieces.** Each of our units i is a C4 element:
- its real position x_i, scaled by a length L (px per model unit, a knob);
- a phase θ_i;
- a rate ω_role(i).

**Enemy units are observed elements.** Their phase is **read from what happens**, never set (the owner, 2026-10-04: "we need damage we do and damage we get").

**Damage drives the beats.** This is the input coupling, the same form as the C6 R4 drive (a pull of the phase toward a reference phase):

    dθ_i/dt = ω_role(i) + K · mean_{j in allies N_i} exp(-r_ij²) sin(θ_j − θ_i) + K_t · sin(ψ_target(i) − θ_i)
              + κ_out · out_i · sin(0 − θ_i) + κ_in · in_i · sin(π − θ_i)

- out_i and in_i: the unit's recent damage dealt and taken, divided by its max hp.
- **Dealing damage pulls its beat toward 0, "attack"; taking damage pulls it toward π, "pull back".**
- The K term shares beats with neighbours, so a wounded unit's pull-back spreads and the group falls back together, while a winning group presses on together. The group decides as one through
  synchronization; no rule says "retreat when hurt".
- N_i: up to 8 nearest allies within radius 3 (C4 values).
- ψ_j, an enemy's **group phase**: arg Σ_{i targeting j} e^{iθ_i}, or φ_j when nobody targets it.
- Integration: one RK4 step (C4: dt 0.02 model units) per game tick, with model time scaled by a knob τ.

**An enemy's beat** φ_j follows the same law from its own exchange with us, computed by our controller from observations:
- damage it deals to us pulls φ_j toward 0 (it is winning);
- damage it takes from us pulls φ_j toward π (it is losing);
- it relaxes at ω_enemy.

**Position law → move goal.**

    v_i = mean_{j in N_i} û_ij [A (1 + J cos(θ_j − θ_i)) − B / r_ij]                    (allies: the C4 law, unchanged)
        + mean_{e in E_i} û_ie A_e,role (1 + J_e cos(φ_e − θ_i)) (1 − d_role / r_ie)       (enemies: approach to the preferred distance d_role, scaled by phase agreement)

- E_i: up to 8 nearest enemies.
- d_role: melee about its reach, ranged and artillery about their range (knobs as fractions of range).
- The enemy term uses the unit's own commit level cos θ_i and the enemy's state: A_e,role (1 + J_e cos θ_i) (1 + J_f (−cos φ_e)) (1 − d_role / r_ie). A unit near "attack" moves in, and a unit near "pull back" (J_e > 1) **backs off**.
  Every unit is drawn more to enemies that are losing (φ_e near π) than to enemies that are winning.
- Goal = x_i + v_i · L · h (h a knob), at full speed. The goal is clipped to the field.

**Target.** Among enemies in reach, i targets the one with the highest cos(θ_i − ψ_j) − J_f cos φ_j (in phase with its group, and losing). It switches only when the gain beats a hysteresis knob.
Units in phase with each other target the same enemy, so **focus fire comes from synchronization**. No rule says "focus".

**Groups (diagnostic and P4).** Each second, the C4 detector (`geomind/c4_detect.py` criteria 1-5, ported) runs on our units' scaled positions and phases and publishes groups. A
group's members share its phase through the K term. When a group breaks, its units keep running the same law alone.

**Knobs (about 20, all tuned by the bench):**
- L, τ, h;
- K, K_t, J, A, B (allies);
- A_e and J_e (per role, 3 + 1), J_f;
- κ_out, κ_in, T_d, ω_enemy;
- d per role (3);
- ω per role (3);
- the hysteresis.

The initial phases come from the seed.

## 3. Score and arms (simplified at the owner's request, 2026-10-04: "why you complicate it")

**Score (the owner's two numbers):**
1. **Units left at the end**: our survivors minus the enemy's. This is the main score and the margin used so far.
2. **Damage difference**: damage we dealt minus damage we took, in hit points. It is the second score and separates fights with similar unit counts.

Won and lost fights are reported alongside these two scores.

**Arms (four; every arm gets the same knob count and the same tuning budget):**

| Arm | What it is | Question it answers |
|---|---|---|
| **resonator** | section 2 | the AI under test |
| **plain morale** | the same controller with each phase replaced by one real number (morale): damage pulls it up or down, neighbours average it, enemies get the same number | does the beat (a circular phase that can label several groups at once) matter, or would a number do? |
| **push-pull** | forces only, target = nearest in reach (physicomimetics-style) | is this just known swarm control? |
| **nearest** | walk to the nearest enemy and attack it | the floor |

The ablations J=0, K=0, no groups and no damage input are **development diagnostics only**: run to understand the controller, never registered as claims.

**Knobs:** at most about 10, shared across roles where possible (for example one A_e with a role factor fixed by range). The same count for every arm.

**Development order (owner, point 3):**
1. 10 vs 10, melee only, against novice.
2. Full armies (50 vs 50, all roles) against novice and regular.
3. The full ladder.

Each step's fights are recorded and **watched** in Astelia's fight viewers (copies in our snapshot folder; owner, point 4) before moving on.

**Review (owner, point 5):** Codex reviews this design before any controller code is written.

## 4. Reference values for the S3 check

The JS (later C++) phase and position laws must equal `geomind/c4_model.py` `rhs` on 5 fixed states with no enemies (the C4 case), to 1e-9. The 5 states and their
`rhs` outputs are computed once with the accepted Python code and committed as `c4_reference_states.json` before the controller exists. Doing this runs the accepted C4 model on 5 states: a
computation, not an experiment, and it waits for the owner's go-ahead on this design.

## 5. Owner decisions (2026-10-04)

1. **Abilities:** v0 leaves them to the game's `auto` reflex, the same for every arm. Approved ("1 ok").
2. **What drives the beats:** damage dealt and damage taken (the owner: "we need damage we do and damage we get"). This replaces the weapon-cycle proposal. Section 2 above.
3. **Sight:** all units visible in v0, as in Astelia's lab. Approved ("3 ok").
