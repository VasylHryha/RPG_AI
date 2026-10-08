# Shape lab v6 — paired geometry, engagement and lethal rotation

Prepare only. Zero fights at delivery. Development tooling, no registration,
qualification, outcome acceptance or claim of RRG source recursion.

One paired multi-arm batch: `base` = forcedP16+react, fire when ready. `V2` adds
copied artillery geometry (script/search); `E1` adds the engagement floor
(script); `R1` adds predicted-lethal rotation (script). `E1+R1` adds exactly R1
to E1, and measures rotation against an active ranged reference. R1 versus base
is diagnostic. These are fixed-rule atoms under decision 0034, not new RRG
mechanisms. P16 selector and react stay unchanged. Ability policy is off in all
stages and arms to isolate the atoms. V1–v5 and the adapter are read-only inputs.

V2 copies candidate generation, reachable assignment and model scoring from
`src/native/artillery.cpp::artilleryVolley` (`artyFire: plan`). Options declared:
`artyModel=simple`, `artyRobust=.5`, `artyHerd=0`, `artyBattery=true`,
`artyRollout=false`, `artyFollow=false`. Cluster shortlist, singles/focus/net/
wall/herd/split/trap/sweep/battery geometry stays copied. Ready guns alone join;
future-gun assignments are empty, so delayed trap finishers and sweep shots
are excluded by the engine's assignment predicate. Unassigned ready guns use
singles. Aim points must be legal at the current and predicted post-move position and inside the arena; otherwise the inherited aim fires normally, with rejection logged. No queued release, extra hold, waves or formation movement. Rollout
code is retained for traceability and disabled; full clone search would need
its own F12 parity/cost contract. This is a geometry-only subset of the teacher,
not the historical full planner/rollout result or a claim to reproduce its gain.

The internal model receives a fresh value-only projection: public live unit
IDs, team, role, position, current velocity, body radius, speed, HP/max HP,
weapon range/damage/reload cycle and current visible targets; eligible own gun
IDs, current P16 target, catalog windup/projectile speed/blast and release
eligibility; publicly visible live shells. Own anchor is the centroid of
eligible guns. Enemy cooldown/prep/energy and tactic are absent; model defaults
are neutral. It assumes every enemy uses a fixed simple radial shell dodge,
uses observed velocity as the smooth velocity proxy, and uses a private fixed
seed 1 (the prediction scorer is deterministic). No living World clone, enemy
RNG, actual enemy dodge policy, hidden target choice or future cooldown enters.
Planner parity fixtures compare this declared projection with the engine's
planner on persisted synthetic public states; they are not real-fight parity.

E1 is ranged-only: terminal/body/failure → react → committed own attack/prep
→ floor → inherited move. The unchanged selected visible target must exist and
be outside own legal reach. Advance to the closest point inside the arena inset by own body radius and within
`range + own radius + target radius − 1 px`, matching engine gap semantics.
Circle/rectangle intersections handle corners. Occupied endpoints are legal in the engine; its separation step resolves overlaps after damage. E1 adds no collision optimization. No kiting or new selector.

R1 is ranged-only. Threats are visible in-flight shells/aimed shots and enemy
artillery casts already committed to a visible target. Own protection is public
self-state; incoming damage uses engine floor rounding after it. No future
cooldowns, choices or HP-threshold withdrawal. Damage is evaluated along the
same reachable speed/stop/multiplier trajectories for base+react and each
candidate. Shots use continuous segment intersection at <=1/120 s subdivisions.
Targeted casts track the candidate trajectory until their advertised release;
landing time is the adapter's current estimate (not an oracle future landing).
Reaction is evaluated first. A committed own attack and body/invalid states
cannot be extracted. Rotation requires D_base >= HP and D_p < D_base − 1 damage,
preferring D_p < HP. Candidate endpoints are behind living friends relative to
the visible enemy centroid, body-safe, farther from that centroid, at most 100
px from self and at least radius+24 px from the arena edge. No map-edge walk.
Participation: remain in reach, or next legal shot <=2 s (move + return to reach,
cooldown, own public energy regeneration, windup after re-entry, and a conservative target-velocity displacement bound); otherwise only the nearest bounded
behind-friend survival candidate, and only if no participating candidate exists.
No candidate means inherit base+react. Future movement/target motion, body
collision/separation and shields are not predicted; raw same-state forecasts with reachable base/candidate commands, self geometry/protection and the committed threat records at activation
are retained and actual triggered survival is observed, not causal proof.

Mechanism: V2 = 10 D1 non-dodger + 10 V2D2 dodger gun fights; E1 = 20 D5
ranged fights; rotation = 20 RD active-ranged-with-friends fights against
regular/storm/line anvil. Rotation mechanism is blocked until E1 mechanism is
read as activated. Shared base/E1 RD receipts are reused. Mechanism read must
show activation AND improvement of the declared metric; otherwise park. Native
gates enforce activation; Claude owns metric movement/tradeoff judgment.
V2 metrics: damage/shell, targets/shell, shells/kill, fire rate, expected damage.
E1: ready time, in-range time, firepower utilization (eligible ready time / all
ready time), actual shots, reaction overrides, ranged deaths. R1: activations,
base/candidate predicted lethal damage, triggered-unit survival, trigger-contract violations and an explicitly unevaluated false-extraction endpoint, rotation time, paired shots lost (actual shot-count difference).
Counterfactual predicted deaths are not measured deaths prevented. False extractions remain not_evaluated because the untreated continuation is absent; trigger violations are separate; prediction error requires reviewing
retained forecasts and actual survival, not assuming all survivors were saved.

C3: 50/100/200 total shared paired draws across regular + 19 pool tactics.
All 20 cells, including missing cells, both axes over ALL fights, won/lost/
timeout split, own deaths/fight, kills/own death (ratio of totals; zero denominator
null plus raw counts), damage/shell/shot and kills/minute. Single-fight wins are
descriptive. One chart shows paired deaths saved versus kills gained, with
paired sample size. Read each look, stop when clear or park at 200; no expansion.
Series only for outcome survivors: ten paired ten-fight series; strict elimination
before 150 s, first non-win stops; healed arm-specific survivor rosters, fresh
enemy per fight, shared independent draw/placement stream with replacement.
Streak primary, reach probabilities and failure tactic/role roster reported.

Shared timing slot: `TIMING_CONFIG.json` declares fire-when-ready. After V1 is
read, `configure-timing` can select base/central_sync/battery_oscillator for ALL
arms without code changes, exactly once before any fight claim. If omitted,
first calibration seals base automatically. No timing change after fights open.
The copied v5 timing law/grid/engine sync settings are unchanged. An oscillator
selection labels the shared timing as RRG battery phase only; all v6 atoms remain
script. F5 TOT and F9 kiting are read as boundaries and are not implemented here.

Same owner cap `../s4_shape_lab_v1/raw/LAB_CAP.json`, default 3600 s if absent;
six workers, caffeinate, measured projection, immutable completions and
repository-scoped process gate. Calibration uses allocated cells (no rehearsal).
The repository gate also protects any running V1/lab. Raw is ignored. Only C3
pairs 0/1 and series 0 per arm get replay exports, capped at 8 MB each. Heavy
diagnostics off; light damage/launch/shot and candidate arbitration audit on.
Frozen local copies of AGENTS, B9 plan, decisions, spec, R3 and sandbox history
are hashed; living docs and Downloads paths are never execution pins.

Claude commands from repository root (v6 preparation is supplied):

```sh
LAB=evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v6/lab.py
# Optional ONCE, before any v6 fight; choose the actual V1 winner:
.venv/bin/python -B "$LAB" configure-timing --mode base --note "<actual V1 reading: fire-when-ready retained>"
# E1 must be read before R1/E1+R1 mechanism. V2 can run independently.
.venv/bin/python -B "$LAB" calibrate --arm E1 --stage mechanism
.venv/bin/python -B "$LAB" run --arm E1 --stage mechanism
.venv/bin/python -B "$LAB" report --arm E1
# Read MECHANISM_E1_SUMMARY.json. Use stop if inactive/metric unchanged:
.venv/bin/python -B "$LAB" review --arm E1 --stage mechanism --decision continue --note "<actual activation/utilization and survival reading>"
# Repeat for V2, then R1 (diagnostic), then E1+R1 (primary rotation):
.venv/bin/python -B "$LAB" calibrate --arm V2 --stage mechanism
.venv/bin/python -B "$LAB" run --arm V2 --stage mechanism
.venv/bin/python -B "$LAB" report --arm V2
.venv/bin/python -B "$LAB" review --arm V2 --stage mechanism --decision continue --note "<actual geometry/throughput and deaths reading>"
# For each activated arm, set ARM to V2 / E1 / R1 / E1+R1:
ARM=E1
.venv/bin/python -B "$LAB" calibrate --arm "$ARM" --stage outcome --look 50
.venv/bin/python -B "$LAB" run --arm "$ARM" --stage outcome --look 50
.venv/bin/python -B "$LAB" report --arm "$ARM"
.venv/bin/python -B "$LAB" review --arm "$ARM" --stage outcome --look 50 --decision continue --note "<actual paired two-axis reading; continue only if unclear>"
.venv/bin/python -B "$LAB" run --arm "$ARM" --stage outcome --look 100
.venv/bin/python -B "$LAB" review --arm "$ARM" --stage outcome --look 100 --decision continue --note "<actual reading; continue only if unclear>"
.venv/bin/python -B "$LAB" run --arm "$ARM" --stage outcome --look 200
.venv/bin/python -B "$LAB" review --arm "$ARM" --stage outcome --look 200 --decision stop --survivor --note "<actual final reading: clearly survives; omit --survivor if parked>"
.venv/bin/python -B "$LAB" calibrate --arm "$ARM" --stage series
.venv/bin/python -B "$LAB" run --arm "$ARM" --stage series
.venv/bin/python -B "$LAB" report --arm "$ARM"
```

At a clear early C3 look record stop and omit later looks. Series is only for a
survivor, and that decision is recorded with `--survivor` (see final handoff).
Repeat a compute command only for PAUSED_CAP; passing cells are verified/reused.

| Stop question (yes/no) | Action | Responsible |
|---|---|---|
| Has a timing selection or fight already been sealed? Yes | Block timing change | implementer |
| Is E1 activated/frozen before rotation? No | Block rotation mechanism | implementer |
| Is mechanism inactive or metric unchanged? Yes | Park arm | reviewer |
| Is mechanism read missing or stopped? Yes | Block C3 | implementer |
| Is previous C3 look unread? Yes | Block next look | implementer |
| Is the effect clear at a look? Yes | Record stop and survivor/park | reviewer |
| Is 200 reached with no clear effect? Yes | Park | reviewer |
| Is stopped C3 not marked survivor? Yes | Block series | implementer |
| Does projection exceed the owner cap? Yes | Request resource decision | implementer |
| Is process discovery unavailable or identity inconsistent? Yes | Stop and investigate | implementer |
