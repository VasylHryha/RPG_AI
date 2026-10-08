# REACT adapter v1

Development implementation of SHAPE_LAB_SPEC §12; new files only. Arms `v7+react`
and `forcedP16+react` use the delivered v7 controller with the caller's v7 θ*.
`requests.py` obtains θ* from `s4_v7c/THETA_ORIGIN.json`, preserving its bytes.
REACT is copied from `dodge.cpp::dodgeGoal` (smartShells, castDodge, slow fields),
and the `decisions.cpp::decideUnit` dodgeShots block, including shotReact=0.12 s.
No fit, calibration, drill, series, search or scientific acceptance is performed.

From the repository root:

```sh
nice -n 15 python3 -B evidence/tactical_composition_demo/astelia_cpp/s4_react_adapter_v1/build.py
.venv/bin/python -B -m pytest -q -x evidence/tactical_composition_demo/astelia_cpp/s4_react_adapter_v1/test_adapter.py
```

Compilation is sequential. Build output remains in this folder's ignored `build/`.
The build derives new host/combat/shot-aim call sites from admitted delivered files,
and links hash-checked parent objects; it never writes into a parent build folder.
`BUILD.json` and binary sidecars bind source, generated source, object and binary
identities. Run `build_admission.admit` before any later execution.

The standalone JSONL host is `build/tactics_react_host`. REACT v1 requires Game
rules (Sandbox REACT requests fail before world creation). It accepts the lab v2
request format, with `options.ai[side].controller` = `v7+react` or
`forcedP16+react`, and `skeleton` = `v7`. Optional `labReact: {"shadow": true}`
enables the isolated engine REACT shadow. It preserves observer-v1 and v7Telemetry
rows and adds `reactV1` rows when killerTelemetry is enabled. Both sides are supported.

`requests.request`, `requests.drill_request`, and `requests.series_request` are
pure constructors for Claude's later executor. They reuse lab v2 placements,
dummy/opponent profiles and healed-survivor construction. Series requests force
abilities off. They allocate no entropy and execute nothing. Example:

```python
# Import requests.py by path (avoid the unrelated HTTP requests package).
req = adapter.request('v7+react', {'level': 'regular'}, seed,
                      abilities_off=True, shadow=True)
# Claude later writes the request to the new admitted host, with fresh development
# entropy and a newly sealed execution declaration/cap projection.
```

The sealed v2 runner/ledger/binary identity is unchanged: do not monkeypatch its
ARMS or BINARY, add these arms to its old entropy, or claim its old capability
receipt admits this new binary. A new execution version/declaration is required
for drills/series. This delivery supplies the selectable native arms and request
constructors, not authorization to run them or edits to the sealed executor.

The information boundary is the current engine's scripted REACT access, not a new
fog-of-war policy. `Snapshot` owns value copies; controllers receive it through a
`shared_ptr<const Snapshot>` without World, UnitRef, config or RNG access. Unit
records match `prepareControllers`' existing Observation. Additional fields:

| Input | Boundary |
|---|---|
| Shells | resolved enemy sources, at > now; position/landing = engine Shell.pos, at, splash, slow |
| Aimed shots | resolved enemy sources; pos, direction, born, speed, remaining distance; homing excluded |
| Fields | enemy position, radius, from/until |
| Enemy gun casts | alive enemy artillery with prep > 0 and living friendly target; target ID/position, predicted release and impact times, blast radius |
| Own execution state | guard, preparation/windup, time rate, energy/cost, active body ability; used for arbitration/readiness |

`Shell.pos` is the engine's immutable landing footprint, not a simulated airborne
3-D position. Both API fields equal it. No launch-origin trajectory is fabricated.
Cast release = now + max(0,windup−prep)/timeRate; impact adds target distance divided
by effective lob speed. These are the exact predictions used by dodgeGoal, not
guaranteed future impacts. The cast aimed at the reacting unit itself is excluded
by REACT exactly as in the teacher. Retained dead projectile sources remain visible.
The scripted REACT paths do not use the engine perception-filtered foe list for
shell/cast scanning; this adapter uses the same scope. No enemy doctrine, skills,
energy, tactical plan, forward simulation, damage prediction or RNG is exposed.

`Command` adds optional explicit aim, Automatic/Hold/Release, and a uint64 volley
ID (0 = absent; bounded to exact JSON integers). `Controller::submit` is the future
primitive seam; default REACT commands use automatic aim and no volley. Hold
suppresses attack release and new preparation; existing preparation continues under
the native windup clock. Release permits the normal mechanics checks, never bypassing
cooldown, reach, energy, guarding or windup. Explicit aim is used at the actual
shot/shell call sites. Volley IDs are recorded per gun; they do not implement V1
coupling or V2 geometry, which remain the owner's next stages.

Arbitration is deterministic: body guard/failure/active body ability precedes REACT;
REACT precedes movement; remaining movement obeys the participation constraint.
Engaged melee does not dodge, matching the unformed scripted path. All ordinary
attack release pauses during a dodge (the unformed teacher behavior); no DodgeFire
or saveWounded is added. Guns reacting, guarded, busy, failed, holding or out of
range are unready. Ready means range/body/cooldown/windup/energy prerequisites to
start preparation or release are met on the observation snapshot. `readinessReason`
distinguishes start, prepared, winding, cooldown and blocked states. Native lane
clearance, attacker caps and within-tick mechanics may still block a launch.
Volley membership on a submitted command survives that tick's reaction; future
V1 must re-submit membership/release each tick. This stateless command adapter
does not retain a pending battery schedule. Body abilities retain native authority, including
already active ability actions; abilities-off series avoid that interaction.

After a dodge the useful position is freshly recomputed by v7, so stale targets
and old posts are not resumed. Withdrawal goals outside every enemy engagement
band are projected back into our own reachable band; out-of-range units pursue
that band. This is a separately recorded participation correction within both new
arms, not a copy of unconstrained saveWounded. Temporary dodge motion may leave
weapon reach; return is immediate on the next threat-free decision. Participation
is a command endpoint constraint, not a claim that all collision/body-ability
motion, inaccessible minimum-range geometry, or evolving enemy motion is certified.

Each row records role, primitive activation, v7 candidate, REACT candidate, executed
adapter command, winner/reason, readiness, and volley membership. Executed means
post-bridge decision intent; observer-v1 records subsequent movement/damage/launches.
Teacher REACT shadow uses an isolated World copy on the same pre-decision state
with its own RNG and scratch state. It runs decideUnit with only the dodge trio,
unformed and without standoff, rotation or search. It is labelled primitive REACT,
not full T-elite. The trio is stateless and draws no random numbers; advancing it
consistently therefore leaves its separate RNG unchanged. Controller clones copy
student/shadow RNG and memory independently; immutable snapshots may be shared.
The same shadow record compares copied and engine REACT in both directions on the
state supplied; full teacher-driven fight collection remains Claude's later work.

Fixtures never call coreStep. They cover observation fields/filtering/ownership,
engine decision parity on recorded synthetic states, arbitration, return,
participation, aim/hold/release/membership, and byte-identical eight-tick
decision/movement trajectories with shadow on/off. This is no-fight fixture parity,
not full-fight identity, effectiveness, loss reduction or series performance.

| Yes/no stop | Action | Role |
|---|---|---|
| Does source/object/binary admission fail? | Rebuild new output before use | implementer |
| Does fixture parity or shadow identity fail? | Fix before handing to executor | implementer |
| Is an old sealed runner/declaration being reused for new arms? | Create a new execution version/declaration | Claude executor |
| Is a drill/series/calibration requested in this implementation session? | Leave it for Claude's later authorized run | implementer |
