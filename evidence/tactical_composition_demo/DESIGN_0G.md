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
| own unit | id, role (melee / ranged / artillery), x, y, vx, vy, hp, maxhp, r (radius), speed, range, dmg, cd, cdMax, current target id |
| every living ally | the same fields |
| every living enemy | id, role, x, y, vx, vy, hp, maxhp, r, range, **weapon readiness** cd/cdMax (visible: the game shows wind-ups) |

All units are visible (as in Astelia's lab: "policies read true positions"). A sight limit is a later fidelity step.

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

**Enemy units are observed elements.** Their phase is **observed**, never set: φ_j = 2π·cd_j/cdMax_j, their weapon cycle. A unit in an enemy's rhythm moves in on it while its weapon recovers; that is a real tactic (stepping in on the cooldown), and nothing tells the units to do it.

**Phase law** (C4 `rhs`, `geomind/c4_model.py:82-102`, plus two observed terms):

    dθ_i/dt = ω_role(i) + K · mean_{j in allies N_i} exp(-r_ij²) sin(θ_j − θ_i) + K_t · sin(ψ_target(i) − θ_i)

- N_i: up to 8 nearest allies within radius 3 (C4 values).
- ψ_j, an enemy's **group phase**: arg Σ_{i targeting j} e^{iθ_i}, or φ_j when nobody targets it.
- Integration: one RK4 step (C4: dt 0.02 model units) per game tick, with model time scaled by a knob τ.

**Position law → move goal.**

    v_i = mean_{j in N_i} û_ij [A (1 + J cos(θ_j − θ_i)) − B / r_ij]                    (allies: the C4 law, unchanged)
        + mean_{e in E_i} û_ie A_e,role (1 + J_e cos(φ_e − θ_i)) (1 − d_role / r_ie)       (enemies: approach to the preferred distance d_role, scaled by phase agreement)

- E_i: up to 8 nearest enemies.
- d_role: melee about its reach, ranged and artillery about their range (knobs as fractions of range).
- With J_e > 1 an anti-phase unit **backs off**: phase decides commit or withdraw.
- Goal = x_i + v_i · L · h (h a knob), at full speed. The goal is clipped to the field.

**Target.** Among enemies in reach, i targets the one with the highest cos(θ_i − ψ_j). It switches only when the gain beats a hysteresis knob.
Units in phase with each other target the same enemy, so **focus fire comes from synchronization**. No rule says "focus".

**Groups (diagnostic and P4).** Each second, the C4 detector (`geomind/c4_detect.py` criteria 1-5, ported) runs on our units' scaled positions and phases and publishes groups. A
group's members share its phase through the K term. When a group breaks, its units keep running the same law alone.

**Knobs (about 16, all tuned by the bench):**
- L, τ, h;
- K, K_t, J, A, B (allies);
- A_e and J_e (per role, 3 + 1);
- d per role (3);
- ω per role (3);
- the hysteresis.

The initial phases come from the seed.

## 3. The arms (every arm gets the same tuning budget; P2 and P3)

| Arm | Differs from the resonator v0 by | Answers |
|---|---|---|
| resonator v0 | none | |
| J=0 | phase does not change motion (J = J_e = 0) | does mode→geometry matter? |
| K=0 | no phase coupling between units or to targets (K = K_t = 0; phases free-run at ω) | does synchronization matter? |
| no groups | ψ_j = φ_j always (no group phase), so units do not share a target through phase | do the groups matter? |
| potential field | forces only (J = J_e = 0, no phases), target = nearest in reach: physicomimetics-style, the closest known method | does any of this beat known swarm control? |
| nearest | walk to the nearest enemy, attack it | the floor |

## 4. Reference values for the S3 check

The JS (later C++) phase and position laws must equal `geomind/c4_model.py` `rhs` on 5 fixed states with no enemies (the C4 case), to 1e-9. The 5 states and their
`rhs` outputs are computed once with the accepted Python code and committed as `c4_reference_states.json` before the controller exists. Doing this runs the accepted C4 model on 5 states: a
computation, not an experiment, and it waits for the owner's go-ahead on this design.

## 5. Open choices (recommendation first)

1. **Abilities:** v0 leaves them to the game's `auto` reflex, the same for all arms (recommended). The alternative is our side without abilities, which handicaps every arm against the ladder.
2. **The enemy phase:** the weapon cycle (recommended: real, observable, tactically meaningful). The alternative is HP-based. Whichever is used, it is declared before tuning.
3. **Sight:** all units visible (as Astelia's lab) in v0. Limited sight later.
