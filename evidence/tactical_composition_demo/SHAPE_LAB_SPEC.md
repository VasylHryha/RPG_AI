# Shape lab and ten-fight series: specification (0g, development tooling)

**Date:** 2026-10-08. **Drafter:** Claude (claude-opus-5-5). **Implementer:** Codex. **Executor:** Claude.
**Status:** owner-approved build. These are development drills on fresh development entropy: no judging seeds, no registered endpoint, no verdict.

## 1. Owner decisions this rests on (2026-10-08, verbatim intent)

- **The damage rule:** a damaged unit may move behind others but **must never leave the fight**. Leaving loses firepower, and the army then loses. v7's escape (the v6 action) and the edge-running in the replays violate this.
- **The current losses are too heavy:** v7 loses 40.7 of 50 on average even when it wins. And we fought one enemy formation only.
- **"Good work" comes first:** define what good work is for **each small shape**, show which shapes exist, and show how each performs **alone (against dummies)** and **combined (against dummies and opponents)**, visually.
- **The owner's yardstick is the fight series (amended in §5 to 10 fights; the streak is the measure):**
  - The army must win **as many fights in a row as possible**, up to 10.
  - Units lost stay lost; **survivors heal** between fights.
  - **Each fight draws the enemy tactic at random** from the pool, so some tactics suit us and some don't.
  - The enemy is a fresh full army each fight.
  - In the owner's earlier improved AI, which passed this, **artillery carried most of the impact**, and the final fight was about 10 units against 50.
- **Answer to "build it?":** yes, with the six good-work criteria below as a draft for the owner to correct.

## 2. Shapes in v7 (from DESIGN_0G §20.1 R9) and draft good-work criteria

Measured values: stored v7c validation, 40 fights against regular (`astelia_cpp/s4_checks/shape_scorecard_v1/SCORECARD.json`, `c82ce59`). They are means over the 32 wins.

| Shape | Job | Draft good work (owner to correct) | v7 now |
|---|---|---|---|
| **G1 gun focus (P16)** | Kill enemy guns first, from a post just inside range | All enemy guns dead while losing ≤ 1 own gun; ≥ 60% of gun damage on enemy guns while any is alive | Guns wiped at 29.2 s; 4.4 own guns lost; 33% of all gun damage on guns |
| **G2 gun spacing (P11)** | One enemy shell hits few of ours | ≤ 1.5 own units hit per enemy shell | 3.92 |
| **R1 escort screen (P12)** | Keep enemy infantry off our guns | About 0 damage to own guns from enemy ranged and melee | 420 + 105 |
| **M1 melee (v6 law)** | Intercept and trade | Exchange better than 1:1; most melee survive | 10/10 of our melee die |
| **Q1 gate (oscillator)** | Decide when to press | Never takes a unit out of the fight; damaged units rotate back but stay in range | 12% of unit time escaping (24% in non-wins); survivors run to the edge |
| **A whole army** | Win the series | Long series streaks; about ≤ 4 losses per fight (§5) | Loses 40.7 |

## 3. Engine capability (new files only; nothing pinned or frozen is edited)

- **A scenario request:**
  - **Explicit unit lists per side:** role, kind (catalog default per role), position, heading, and the HP fraction (1.0 for healed survivors). This replaces the standard 50 v 50 spawn.
  - **Deterministic placement** for a reduced army: the surviving units take the first N standard spawn slots of their role, in a fixed order.
- **Controllers per side:**
  - **ours:** any delivered arm (v7 at θ*, forcedP16, v6) or an Astelia scripted level/doctrine (as a reference);
  - **the enemy:** an Astelia level (novice, regular, veteran, elite), a doctrine from `POOL` (19 entries), or a **dummy:**
    - `dummy_static`: stands still and never attacks;
    - `dummy_static_fire`: stands still and attacks whatever comes into reach, by catalog targeting;
    - `dummy_advance`: walks toward the nearest enemy gun at catalog speed and does not attack;
    - `dummy_advance_fire`: walks toward the nearest enemy gun and attacks in reach.
- **Output:** the existing observer-v1 stream (units, damage, launches, dodges) plus v7 telemetry when the arm is v7, so the stored-fight viewer and the scorecard read it unchanged.
- **Checks before any drill:**
  - a standard 50 v 50 scenario request reproduces a delivered v7c validation fight byte for byte (same seed, same terminal);
  - dummies never deal damage (static) and never move (static);
  - placement is deterministic;
  - survivors-heal carry-over restores full HP and keeps the dead removed.

## 4. Drills (each shape alone, then combined)

Each drill runs for every arm in {v7 θ*, forcedP16}, plus v6 where the shape is v6's. Each uses 10 fresh development seeds (5 clusters × 2 orientations), drawn from new entropy in a new ledger.

| Drill | Our side | Enemy side | Good-work metrics |
|---|---|---|---|
| **D1 guns** | 10 guns | 10 guns `dummy_static_fire` + 20 ranged `dummy_static` in a line, 450–600 px away | time to kill all enemy guns; own guns lost; share of gun damage on enemy guns; shells with no hit |
| **D2 spacing** | 10 guns + 20 ranged, our arm | 10 guns `dummy_static_fire` only | own units hit per enemy shell; damage taken per shell |
| **D3 screen** | 10 guns + 20 ranged | 15 ranged `dummy_advance_fire` toward our guns | damage reaching our guns; escorts lost; enemy ranged killed |
| **D4 melee** | 10 melee | 10 melee, regular | exchange ratio; survivors |
| **D5 rotation** (owner rule) | 30 ranged in a line | 30 ranged `dummy_static_fire` | firepower retained (alive-unit seconds within weapon reach / alive-unit seconds); units out of the fight; losses |
| **C1 combined, passive** | full 50 | full 50 `dummy_static` | time to eliminate; losses (expected about 0) |
| **C2 combined, fire** | full 50 | full 50 `dummy_static_fire` | time to eliminate; losses |
| **C3 combined, opponent** | full 50 | regular, and each of the 19 `POOL` doctrines | the win; losses; time |

## 5. The ten-fight series (S10X; amended 2026-10-08 by the owner)

- **The owner's correction:** the series is **10 fights in a row**, and the measure is **how many consecutive fights are won**. The owner's earlier improved AI typically reached **6 wins, sometimes 8**. That was **before abilities were added**; abilities are a separate story.
- **One run:** up to 10 fights. In fight k our army is the survivors of fight k−1, **healed to full HP**; the dead stay dead.
- **The enemy:** a fresh full 50 each fight. Its tactic is drawn **uniformly at random with replacement from the 19-entry `POOL`**, at the regular skill set, from the run's seed.
- **Abilities are off on both sides** in the series (`abilities: "off"`), to match the owner's reference conditions. A second, labelled variant with the catalog's default abilities may be reported for context only.
- **The run ends at the first fight not won by elimination.** The streak is the number of fights won before it; a full pass is 10/10.
- **The reference band:** a typical streak of 6, sometimes 8 (the owner's earlier improved AI, without abilities).
- **Arms:**
  - v7 θ*;
  - forcedP16;
  - **the Astelia elite AI as our side** (the in-engine reference), playing the same series draws.
- **Runs:** 10 series per arm, from fresh development entropy.
- **Reported:** the streak distribution (mean, median, min, max), the fight reached, units left before each fight, and per-tactic losses and units lost across all fights (which tactics hurt us).
- **The draft good-work target for the whole army** becomes about **≤ 4 losses per fight on average,** so that 10 wins stay feasible from 50 units. It is reported against the reference band.

## 6. Visual output

- Every drill and series fight writes the observer stream to gitignored raw storage.
- A compact replay extractor (the `viz_0g/make_v7_replays.py` format, generalized) produces a lab JSON for the viewer: one picker group per drill.
- The scorecard script runs on lab output unchanged.

## 7. Boundaries

- **New files only,** under `astelia_cpp/s4_shape_lab_v1/` and new native sources:
  - no edits to delivered v7c, P16, v6, morale or catalog bytes;
  - no edits to `astelia_cpp/.gitignore` (it is hash-pinned; local ignores go in `.git/info/exclude`);
  - no hash manifest pins `docs/PLAN_CURRENT.md`, `DESIGN_0G.md`, `DESIGN_0H_REV7.md` or this file.
- **The raw ledgers stay out of git;** each committed file is under 45 MB.
- **Cost:** the drills are short. The series is at most 3 arms × 10 series × 10 fights = 300 fights. The projection is reported before running; decision 0031 applies.
- **No outcome of a drill changes v7.** Changing a shape is a later, owner-approved revision on fresh seeds.

## 8. Stop rows

| Yes/no | Action | Role |
|---|---|---|
| Does the 50 v 50 scenario request fail to reproduce a delivered fight byte for byte? | Fix before any drill | implementer |
| Does a dummy deal damage or move when it must not? | Fix before any drill | implementer |
| Does the projection exceed 1 h before 22:00? | Ask the owner | Claude |
| Would the build need to edit a pinned or frozen file? | Stop and report; use a new file | implementer |

## 9. Amendment 2 (owner, 2026-10-08): per-role ideal runs, and split-and-compare actions

The owner, on what comes next:
- select tools that can raise our efficiency;
- split melee, ranged and artillery;
- do ideal runs;
- split the action of each shape, and compare or repeat it;
- copy game-AI best practice (as AlphaStar learned from StarCraft play).

**This amendment adds three things to the lab. It is built after the current build; nothing in §3–§5 changes.**

1. **Ideal runs per role (the teacher arms).** Every drill D1–D5 and C1–C3 also runs with a teacher on our side:
   - **T-elite:** the Astelia elite AI, which is the best scripted play in this engine;
   - **T-search:** later, the best achievable play found by search with the engine's forward model (chosen from the research note `docs/research/GAME_AI_BEST_PRACTICE_RESEARCH.md`).
   - The teacher's per-role good-work numbers become the **reference line** for each shape.
2. **Shadow actions (split and compare on the same state).**
   - While a teacher controls our side, our shapes (v7's gun focus, gun spacing, escort and melee law, plus the gate) compute their action for every unit on every decision tick, **from the same observation, without executing it.** This is the same mechanism v7 already uses to compute P16's and v6's commands side by side.
   - **Recorded per unit per tick:** the role, the teacher's target and movement, and our shape's target, goal and gate mode.
   - **Reported per role:**
     - target agreement;
     - the goal distance between our shape and the teacher;
     - where our shape would leave the fight while the teacher stays;
     - the situations of largest disagreement, as replay timestamps for the viewer.
   - **The reverse comparison:** our shape in control, with the teacher shadowed.
3. **Repeat (copy the teacher), as one labelled change per role, later and owner-approved:**
   - either fit the shape's own parameters to maximise agreement with the teacher on the shadow records (imitation, in the manner of behaviour cloning);
   - or adopt the teacher's rule for that role as a new shape;
   - then re-measure in the drill and in the series.
   - **Each copied shape names its source** (the teacher's rule or skill) and how it differs.

**Viewer:** the drill replays get a "teacher vs ours" layer that draws both targets and goals for the selected role.

**Boundaries:** §7 applies. The shadow computation must not change the teacher's trajectory, which is checked by byte-identical output with shadowing on and off.

## 10. Amendment 3 (owner, 2026-10-08): primitives (move, attack, react), and losses are avoided, not budgeted

**The owner's corrections:**
- **There is no loss budget.** Losses are avoided. Most losses come from artillery, whose area damage is the unfair part.
- **Split the shapes further into primitives** (move, attack, react). Copy a simple, efficient move set from the teacher: how it moves, attacks and reacts against melee or artillery. Then compare it with our shapes, or try to rebuild it from our shapes, because we may be lacking something.

**What the stored data show** (`astelia_cpp/s4_checks/shape_scorecard_v1/KILLERS_V7_REGULAR.txt`; 40 v7 fights against regular):
- **Artillery causes our losses:** 74% of our deaths and 77% of the damage we take come from enemy artillery. It kills 86% of our dead ranged units and 63% of our dead melee.
- **We never react to shells:** the enemy makes about 2,940 shell dodges per fight, and our side makes 0. Our controller side runs no reaction primitive, while the regular level has `dodgeShells` on.
- **Our guns are inefficient:** we fire 184 shells per fight against the enemy's 105 for similar kills.

**The primitive catalogue.** Each primitive is measured alone in the drills, and teacher against ours by shadow actions (§9):

| Primitive | Ours now (v7) | Teacher source in the engine | Good work (draft) |
|---|---|---|---|
| **Move:** formation and post | P16 post, escort point, v6 law | formation presets, `standoff`, `kite` | stay at the useful distance; never out of the fight |
| **Attack:** target choice | splash value V, v6 alignment | `killSpeed`, `meleeFocus`, `fireControl`, `artyFire: plan` | damage on the right targets; no overkill |
| **Attack:** aim | none | `lead` (smooth) | shells and shots land on moving targets |
| **React:** shells and shots | **none** | `dodgeShells` (smart), `castDodge`, `dodgeShots`, `shotReact` | own units hit per enemy shell → about 0–1 |
| **Rotate:** damaged units | escape = leave (violates the owner rule) | `saveWounded` (backs away, still near) | damaged units survive and stay in reach |
| **Volley timing** | none | `waves`, `holdFire.sync` | shells land together; fewer dodged |

**The first change to test, once the lab's checks pass:** the **react** primitive, copied from the engine's `dodgeShells: "smart"` and `castDodge` as a labelled shape for our side. It is measured in D2 (spacing under fire), C2 and the series against v7 without it. It is one change, and it names its source.

## 11. Amendment 4 (owner, 2026-10-08): coordinated artillery volleys

**The owner:**
- Artillery is efficient when the guns **work together**: fire at one time and cover the maximum area, so the opponent cannot dodge or escape the corner.
- Or **force them to dodge into one place, then cover that place.**

**The data:** we fire 184 shells per fight, one gun at a time. The enemy makes about 2,940 shell dodges per fight (§10).

**The volley primitive, split into two parts and staged after the react primitive:**

| Part | Job | Teacher in the engine | Our shape (RRG form) | Good work (draft) |
|---|---|---|---|---|
| **V1 timing** | guns fire together, so a dodge from one shell lands in another | `holdFire: {sync}`, `waves` | **the guns as coupled phase oscillators:** each gun's firing phase is pulled toward its neighbours' (Kuramoto-type coupling), and a gun releases when its phase crosses the shared firing point. Synchrony decides when the battery fires | the spread of shell landing times within one volley; enemy dodge success against our shells; hits per shell; shells per kill |
| **V2 geometry** | cover the area, or herd and trap | `artyFire: plan` (trap, sweep, net, wall), `artyHerd`, `artyRollout` (2 s look-ahead), `artyModel: exact` | a volley pattern chosen per volley by forward-model scoring: copied first, then compared and simplified | the same, plus enemy units caught per volley and damage per volley |

**The order:**
1. react (§10);
2. V1 timing;
3. V2 geometry (copy the teacher, then compare with our shape).

Each is one labelled change, measured in D1/D2 (guns against guns, and under fire), C2 and the series, with shadow comparison against T-elite (§9). The guns' synchrony is the oscillator's intended job. It replaces the commit/escape gate, which showed no gain (v7 32/40 against always-commit 31/40) and which violates the owner's rule.

**The closest known methods, and the difference:**
- **Time-on-target artillery fire** (real-world doctrine: shells timed to land at once);
- **Kuramoto synchronization;**
- **Astelia's own `holdFire.sync`.**
- **The difference:** the timing emerges from local coupling between guns, not from a central scheduler.

## 12. Amendment 5 (2026-10-08): the interface prerequisite for react, aim and volleys (from Codex's research recheck F2)

`docs/reviews/game_ai_research_recheck_codex.md` (F2, High) found three gaps in the delivered controller interface (`astelia_cpp/src/native/controller.h`):
- **The observation** has time, arena size and unit records only. It has **no incoming shells, shots or slow fields, and no enemy cast preparation**.
- **`UnitDecision`** has movement, target and failure fields only. It has **no explicit aim point, no hold/release, and no joint volley**.
- **So our shapes cannot see a shell coming**, which also explains our zero dodges, and they cannot time a volley. Copying the teacher's react, aim or volley primitives therefore first needs a new interface.

**Required before the react change (new files only; pinned interfaces unchanged):**
1. **An observation adapter** exposes immutable, legally observable projectile and cast data for our side: in-flight shells (position, predicted landing point, landing time, radius), aimed shots, slow fields, and enemy guns winding up (target, release time). It exposes the same information the scripted side's `dodge.cpp` uses, no more.
2. **A command adapter** carries an explicit aim point, a hold/release intent per gun, and volley membership.
3. **The arbitration rules:**
   - react takes temporary precedence over movement;
   - it is defined which attacks stay possible during a dodge;
   - a unit returns to its useful position after a dodge;
   - reacting affects volley readiness;
   - copied rotation stays inside the owner's participation rule. The teacher's `saveWounded` backs toward home without a range limit, so it is not assumed to comply.
4. **Recording:** primitive activation, the candidate and executed intent, the arbitration winner and reason, readiness and volley membership, next to targets and goals. This feeds the §9 shadow comparison.
5. **Shadow state:** the teacher's and the student's state and random draws are separate, and are advanced consistently on the same decision state. The byte-identical shadow-on/off check (§9) still applies.

**The order of changes** (owner, §§10–11) is unchanged: react → V1 timing → V2 geometry. Each is one labelled change measured in the drills and the series.

**Series evaluation (F3):** the streak is the primary series measure. Secondary measures:
- the probability of reaching each fight;
- survivors by role before each fight;
- losses on won and lost fights, reported separately with their denominators.

Any search or tuning objective is defined explicitly (terms, units, weights, terminal rules) before use.

## 13. Amendment 6 (owner, 2026-10-08): find and confirm the few high-impact mechanisms

**The owner:** in Astelia and in our older AI versions, a few mechanisms brought most of the success, and the rest added small amounts on top. Identify or confirm those high-impact ones and work on them.

**Stored evidence, before any run:**
- **Astelia skill search** (`astelia_compose/README.md`; the earlier JS engine; development data, not comparable with C++ scores):
  - **The dodge trio is the largest:** dodgeShots, smart dodgeShells and castDodge. From novice, these 3 pieces alone gave 100% wins and beat regular by +24 and veteran by +25, 8 below the hand-built elite-fast. castDodge and smart dodging work only as a pair (+9.3 together, 0 alone).
  - **Artillery coordination:** planned artillery fire with 3 attack waves, +2.8 as a pair. The artillery rollout, +6.5 alone at about 10× the time per fight.
  - **Structure:** the rules brain with a formation, −6.1 and +1.9 alone, +6.8 together.
  - Everything else was small or zero.
- **Our own line** (DESIGN_0G §19):
  - splash-value gun focus took regular wins from 0/20 to 19/20 (P16);
  - escorts added a little (6–8/20);
  - spacing added about nothing (2/20);
  - the oscillator commit/escape gate added nothing (32/40 against 31/40).
- **v7 has none of the top mechanism:** 0 shell dodges per fight against the enemy's ~2,940 (§10).

**Confirmation in the C++ engine (the impact ranking IR; runs after the §4–5 lab run; new files only):**
- **Leave-one-out:** our side is elite-fast, and separately elite without the rollout. Each high-impact candidate is switched off one at a time:
  - the dodge trio as a unit, and each member alone;
  - artyFire plan, waves, holdFire, artyRollout;
  - the rules brain and the formation preset;
  - saveWounded, killSpeed, meleeFocus, lead.
- **Add-one-in:** our side is novice, plus each candidate (and each known pair) one at a time.
- **Measured** in the ten-fight series (abilities off, paired series draws across arms) and in C3 against the 19 doctrines:
  - the streak distribution;
  - the probability of reaching each fight;
  - losses on won and lost fights, reported separately;
  - each piece's time cost per fight.
- **Output:** an impact table ranking mechanisms by streak gain, with the time cost of each. The top few become the work list for our shapes, in the order react → volley timing → volley geometry (§§10–11), unless the ranking shows otherwise. Any change of order goes to the owner.
- **Cost:** projected before running (decision 0031); the elite rollout arm is the expensive one.

## 14. Amendment 7 (owner, 2026-10-08): script atoms against RRG mechanisms; the first RRG test is battery synchrony (V1)

**The owner:** "the scenarios in the lab are not our AI, they are programmed things." Agreed:
- P16, the copied dodge, the elite, the enemy tactics and the dummies are scripts.
- The copied-dodge gain (shape lab v4: 26/50 → 46/50 wins against the 20 tactics; own units hit per landed enemy shell 3.84 → 1.71) is a **script gain**.
- From now on every result is labelled **script** or **RRG mechanism**, and each RRG mechanism is tested against its scripted equivalent on identical fights (decision 0033 sizing).

**The V1 test.** The base is always-commit + react (forcedP16+react).

**The arms, all paired:**
- **(a) the base:** guns fire as soon as they are ready (script);
- **(b) the base + scripted central sync:** a copy of the engine's `holdFire: {sync}` / `waves` rule. A central rule holds a ready gun until enough guns are ready, then releases them together (script);
- **(c) the base + battery oscillator** (RRG mechanism), detailed below.

**The battery oscillator, arm (c):**
- Each gun i has a phase φ_i (rad), with **dφ_i/dt = ω_i + (K/n_i) Σ_{j∈N_i} sin(φ_j − φ_i)**.
- **ω_i = 2π / T_i**, where T_i is the gun's own reload cycle (cooldown + windup, s), from the catalog.
- **N_i** = the living own guns within the coupling radius R_c (px). It is local, with no central scheduler.
- **Release:** a gun releases its cast (through the §12 command adapter: hold/release with an aim point) when φ_i crosses 0 mod 2π **and** it is ready **and** a legal target is in reach.
- **Otherwise it holds.** A ready gun is never held longer than one cycle T_i, a bound that limits lost firepower.
- **Phase reset on release:** the phase drops to the release point.
- Guns still choose their **target and aim by P16's rule;** only the timing changes.

**The normalization ledger:**
- φ in rad; ω, K in 1/s; T in s; R_c in px.
- **The knobs:** K and R_c only, with ranges declared before fights:
  - K ∈ {0.5, 1, 2} / T;
  - R_c ∈ {200, 400, ∞} px;
  - one development pick on the mechanism stage only.
- Every gun applies the same law; nothing is tuned per level.

**The mechanism metrics** (read first, 10–20 paired fights):
- the spread of our shells' landing times within each volley (s);
- the enemy dodge success against our shells (enemy units that escape a blast they were inside at launch / units inside at launch);
- hits per own shell; shells per kill;
- hold-induced idle time per gun (s) and fired shells per gun-minute;
- behaviour with only 1–2 guns left.

**The outcome metrics** (decision 0033):
- C3 against regular + the 19 tactics, paired looks at 50/100/200;
- the ten-fight series, with the streak primary;
- losses on won and lost fights reported separately.

**The reading** (declared now; development, not acceptance):
- **"RRG earns this job":** (c) is clearly better than (a) on the mechanism and on outcome at the decision-0033 effect size, **and** (c) is not clearly worse than (b).
- **"The script is better":** (b) is clearly better than (c). Then (b) is kept as the atom, and the oscillator gets a different job.
- **Anything else:** no difference at this size, so we do not chase it (decision 0033).

**The closest known methods, and the difference:**
- **Time-on-target fire**, the engine's `holdFire.sync`, and pulse-coupled oscillator synchrony (Mirollo–Strogatz; identical all-to-all oscillators only).
- **The difference:** heterogeneous guns, local coupling only, with release gated by readiness and legality inside a battle.
