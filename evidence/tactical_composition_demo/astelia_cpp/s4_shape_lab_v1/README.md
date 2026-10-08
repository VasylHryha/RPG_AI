# Shape lab v1

Owner-approved development tooling for SHAPE_LAB_SPEC sections 3–6. It changes no delivered controller, catalog, judging ledger, registered experiment or accepted source. No development observation constitutes acceptance or a scientific verdict.

From the repository root:

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v1/build.py
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v1/lab.py prepare
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v1/lab.py checks
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v1/lab.py project
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v1/lab.py run
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v1/lab.py report
```

`prepare` allocates development entropy once in ignored `raw/SEED_LEDGER.json`. It commits neither raw entropy nor large traces. It refuses an unsealed prior allocation. Existing sealed preparation checks source, theta, entropy and binary identities. Never edit an allocated ledger or replay an incomplete raw cell. A behavior change requires a separate lab version and fresh entropy; current files/evidence remain intact.

`checks` runs the exact stored-output compatibility check and dummy/placement/healing checks before any drill. The compatibility comparison is the owner-authorized exception using one delivered validation seed; all other checks and drills use new development entropy. A failure stops the runner and generates a stopped report. CLI checks and runs use caffeinate.

`project` uses measured full-output v7 timing scaled to 150 seconds, historical full-elite per-step timings scaled to 4501 ticks with a declared tenfold margin, analysis passes and a reserve. It assumes serial work, giving no credit for six-worker speedup. This is an estimate; historical elite profiles and current full-elite throughput differ. A projection above 3600 seconds stops before drills; Claude asks the owner. `run` additionally requires a working, clear pgrep gate, waits for any named heavy native/medium runner, and limits active work to six threads. It accounts for closed prior attempts and never restarts an hour's allowance on resume. An unclosed attempt or incomplete fight stops for investigation. No source edits during a run.

A scenario request adds `labScenario: {sides: [our_units, enemy_units]}` to the delivered request. Each unit has `role`, optional `kind` (catalog default if omitted/null), `position: {x,y}`, `heading` in radians and `hp_fraction` in (0,1]. It supports up to the standard role capacities per side (10 melee, 30 ranged, 10 guns). Lists use fixed first standard role slots; carried units are sorted by persistent cohort identity, healed and reassigned to those slots. Native ids describe current slots; the series receipt retains original cohort identities, so no dead cohort returns. Heading sets native guard orientation; the simulator has no general facing state for ordinary units.

Named dummies are `dummy_static`, `dummy_static_fire`, `dummy_advance`, and `dummy_advance_fire`. Optional role overrides use codes 0–3 in that order; D1 sets ranged=0 while guns fire. All dummy abilities are disabled independently of the other side. Static bodies remain fixed after native separation. Advance targets the nearest enemy gun at catalog speed and holds when none remains. Fire targets the nearest legal enemy by native role reach/gap, ties by native id. Delivered arms use v7 theta* or v6's delivered attempt-2 vector. Elite is the full scripted catalog level, with its lookahead and artillery rollout retained.

Drills: D1–D5 and C1–C2 run v7 and forcedP16 on five new clusters with both orientations; D4 and D5 also run v6. C3 runs both main arms against regular and each of the 19 doctrines (20 opponents), on the same ten fresh paired seeds. Total: 560 drills. S10X has ten series per main arm plus elite, up to ten fights, fresh 50 enemies, regular skills, uniform replacement doctrine draws from the run seed, no abilities, healed survivors, dead removed, and first non-elimination stopping. At most 300 series fights.

Metrics use actual starting armies, HP dealt, seconds and native range/gap. Gun damage share conditions on enemy guns still alive; enemy shell means include landed misses and exclude unresolved shells/Slow fields. Firepower integrates alive-unit seconds, not a sampled reach-plus-margin proxy. Results preserve conditional-time/share denominators. Criteria are reported per fight with an explicit count; unrun criteria are labeled not evaluated. Whole-army ≤4 losses is the owner's draft yardstick, reported descriptively.

`report` writes compact drill summaries, S10X distribution/run/tactic summaries, and replay groups. Each drill gets a single viewer-format JSON; each series gets a JSON containing all its fights. The extractor reduces sampling deterministically and fails if it cannot fit all fights within 8,000,000 bytes. `REPLAY_INDEX.json` lists actual FPS and files. Unrun groups have no fabricated replay. The unchanged scorecard is imported with its RAW path redirected and reports auxiliary results; its fixed 50-unit/10-gun and reach+50 conventions do not govern reduced drills.

The JSON uses the stored `viz_0g/replays_v7.json` schema (`fights`, frames, goals, guns, escorts). The delivered viewer hardcodes validation story names and its initial pick; arbitrary lab groups require a viewer adapter/picker mapping. The extractor supplies its data schema, but direct lab viewer usability is not claimed. No delivered viewer file is edited. Raw streams are available separately for full-resolution inspection.

Final focused tests, once after the complete change/review batch:

```sh
/usr/bin/caffeinate -i -s .venv/bin/python -m pytest -q -x evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v1/test_lab.py
```

The owner's separate Codex recheck and disposition live here because this task forbids edits to existing plan files. Main `.git` is read-only in the current managed permission profile; the report inventories new uncommitted files. No alternate repository, bundle, push or hook bypass is used.
