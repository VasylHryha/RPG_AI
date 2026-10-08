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
