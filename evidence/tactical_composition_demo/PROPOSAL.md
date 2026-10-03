# Tactical composition demo — PROPOSAL (draft for owner approval)

Status: DRAFT. Nothing is implemented or run. Not a milestone, not C6 evidence; it changes no status, accepted file or threshold.
Drafter: Claude, 2026-10-03, at the owner's request after the arithmetic demo (`evidence/geometric_composition_demo/REPORT.md`).
Authority: owner goal ("AI as geometry, small pieces that combine into bigger ones that act as one"), RRG 01 §13 and 03 §21,
GeoTactics R3 §1.1 (hierarchy is deferred there), AGENTS pilot rule (own entropy, scratch code outside `geomind/`).

## 1. Goal and the question

Arithmetic was the wrong test: matrix methods are near-perfect there, and the demo could not separate two questions. Tactics is
natural for geometry (positions, ranges, directions). This demo asks two separate questions on a small tactical game:

1. **Does composition help?** Small pieces, each taught one job, wired into a unit controller and then a squad controller, against one
   big controller taught directly.
2. **Does geometry help?** Pieces made of points in space (as in the arithmetic demo) against pieces made of an ordinary small neural
   network, wired the same way.

The four cells of that 2 x 2 table (geometric or ordinary, composed or one big controller) answer both questions without mixing them.

## 2. The world, the pieces, the compositions

A small 2-D arena (our own sandbox, numpy only, deterministic given a seed; the real Astelia simulator is out of scope, see §8). Three
units per side from three types: fighter (short range, tough), archer (long range, fragile), mage (medium range, one area-burst
ability with a cooldown). Opponents are scripted policies (rush nearest, kite, focus weakest). All stats are invented and fixed.

Level-1 pieces, each taught only its own job from a scripted teacher for that job:

| Piece | Takes | Gives |
|---|---|---|
| AIM | positions and health of the visible enemies, relative to the unit | a score per enemy (the highest is the target); one scorer shared by all enemies |
| MOVE | the vector to the chosen target and the unit's preferred range | a move direction (close in, hold or back off) |
| ABILITY | enemy positions relative to the unit and the cooldown | fire or hold |

Level 2, UNIT: AIM feeds MOVE and ABILITY. Wired, no further training; promoted into one piece (as in the arithmetic demo, closure
measured). Level 3, SQUAD: a FOCUS piece (taught its own job: pick one enemy for the whole squad) feeds the three UNIT pieces.
One AIM, MOVE and ABILITY are reused across all three units and across unit types; types differ only by their stats as inputs.

## 3. The comparison (2 x 2) and the fairness rules

- Composed: pieces taught separately, wired. One big controller: a single map from the whole squad state to all three units' actions,
  taught from the same scripted full controller's actions (end-to-end labels).
- Equal accounting: the same total training samples and the same total parameters (points or weights) for composed and one big.
  Scaled rows (4x and 16x) for the one big controller to show how much it needs to catch up. The composed version receives extra
  supervision (each piece is taught its own job); that is the idea being tested and is stated, not hidden.
- Baselines for context: the scripted full controller (the teacher), a simple "rush the nearest enemy" rule, and a random policy.
- Team-size change (3 to 5 units) is structurally impossible for a fixed-input big controller. It is reported as a capability, never
  scored as a win.

## 4. What is measured

Primary: **closed-loop win rate** and mean health advantage against the scripted opponents on fresh episodes (200 per cell per seed,
20 seeds), not just copying accuracy. Also per level: fidelity of each piece to its teacher, error after wiring, error after
promotion, and change in win rate when a level is added (so error build-up over depth is visible, the lesson of the arithmetic demo).
Unseen condition: squad type mixes never seen in training (for example a squad with two mages when training had at most one).

## 5. Predictions and pass/fail (stated now, numbers fixed after the development calibration, then frozen)

Verdict words as before: SUPPORTED if the median and at least 75% of seeds meet the bar; REFUTED if the median misses by the stated
margin; INDETERMINATE otherwise. Every claim also needs a floor: the controller must beat the "rush nearest" rule, or it proves
nothing.

| | Claim | Bar |
|---|---|---|
| P1 | Each piece learns its job (both representations) | agreement with its teacher >= 0.95 on held-out states (move: direction error <= 10 degrees) |
| P2 | The composed geometric squad plays | win rate within 10 points of the teacher and at least 15 points above "rush nearest" |
| P3 | Composition helps (same representation, equal data) | composed beats one big controller by >= 10 points on trained mixes and >= 15 points on unseen mixes; REFUTED if the gap is under 3 points |
| P4 | Data to match | the equal-data big controller does not match the composed win rate; report the scale at which it does |
| P5 | Geometry competes with ordinary pieces | composed geometric within 10 points of composed ordinary; REFUTED (not competitive) if more than 20 points below |
| P6 | No error build-up | each added level costs at most 5 win-rate points against the teacher at that level |

Reading, as written: P3 SUPPORTED with P5 not refuted means composed geometric pieces are useful for this tactical control. P3
REFUTED means one big controller does as well and composition adds nothing here. P5 REFUTED means geometry was not competitive
with ordinary pieces in this setting, even if composition helped. Either result is reported as it is. It would still be one
sandbox, not a general claim.

## 6. Lessons from the arithmetic demo, built in

1. **Difficulty check before bars.** A development run on its own entropy checks that the task is neither trivial nor impossible:
   the teacher should beat the scripted opponents well but not always, and "rush nearest" should be clearly worse than the teacher.
   Only the task is calibrated there (never a composition result); piece sizes are set by a rule written before it runs.
2. **Straight-line floor equivalent:** every claim is also compared with the simple rule baseline.
3. **Own-level time and units:** pieces take inputs in their own relative coordinates (vectors in the unit's frame), so levels are
   not mixed in one check.
4. **Gate each level:** a level is only built on pieces that passed their own bar; the report states where accuracy stops.
5. **Independent review of the specification and code before the one recorded run;** one-shot latch, own entropy, recorded
   hashes, guarded finalisation, a self-audit table of every defect found.

## 7. Plan and cost

Draft specification and sandbox (with invariant tests: determinism, mirror symmetry, no teleporting, health never increasing) ->
independent review -> development calibration (task difficulty and piece sizes, separate entropy) -> specification commit ->
mechanics tests -> smoke -> one recorded run -> report. Expected effort: about one working session to build and review. Expected
compute: minutes for training, perhaps 10 to 60 minutes for the closed-loop episodes (unmeasured; python simulation speed is the
risk; the development run measures it before the cap is chosen).

## 8. Limits and out of scope

One invented sandbox and one set of scripted opponents; the teachers are scripted rules, so this tests whether pieces can learn and
compose known skills, not whether they discover tactics. The pieces are prototype maps or small networks, not oscillators and not the
C4 law; the RRG physics is not tested. The real Astelia simulator needs its own repair first (GeoTactics R3, GT0) and is the follow-up
(route B) if this design survives. No learning against live users, no balance tuning, no hardware or efficiency claims.

## 9. Normalization ledger

| Quantity | Normalization |
|---|---|
| Positions and ranges | in the acting unit's own frame, divided by the arena size |
| Time | ticks; cooldowns and horizons fixed per episode |
| Health | fraction of the unit's maximum |
| Win rate | fraction of fresh episodes won; health advantage = mean (own - enemy remaining health fraction) |
| Budget | points or weights counted once per distinct taught piece; samples summed over taught pieces |

## 10. Stop conditions (yes/no, one action, one role)

| Condition | Action | Role |
|---|---|---|
| Owner has not approved this proposal? | Build and run nothing | Drafter |
| Development run: the teacher does not clearly beat both baselines, or the task is trivial? | Adjust the sandbox stats once, record it, then freeze | Implementer |
| A piece misses its P1 bar? | Report it and do not build the level above it | Implementer |
| Specification or code uncommitted, or `run/` exists? | Refuse to run | Implementer |
| A seed fails numerically? | Record it missing, never replace it | Implementer |
| Result tempts a retune or a rerun on new seeds? | Do not; return to the owner | Implementer |

## 11. Decisions for the owner

1. Approve this scope (own sandbox first, real Astelia simulator later)?
2. Are the three unit types and the three pieces (aim, move, ability, plus a focus piece for the squad) the right ones, or do you want
   different pieces?
3. Are the bars acceptable (composed beats one big controller by 10 points, 15 on unseen mixes; geometry within 10 points of ordinary
   pieces)? They are fixed only after the development calibration, then frozen.
