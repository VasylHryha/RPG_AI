# Shape lab v2: measured timing and local cap

Owner decision, 2026-10-08: "Measure, then run ≤3 h". Claude executes fights on the
host; Codex only implements and tests the controls. No judging, tuning, registration
or scientific acceptance is added.

V1's committed evidence, preparation, entropy and native code are preserved. The
v2 folder is the documented new-version route for a runner-control change. `prepare`
allocates fresh development entropy, excluding every v1 seed, and seals the v2
sources. V2 reuses the exact admitted v1 binary and inherited passing capability
checks because the native engine, request construction and metrics are unchanged.
Parent source/binary/ledger hashes are verified on admission. Checks are not repeated.

From the repository root, after implementation/review/testing is complete:

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v2/lab.py prepare
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v2/lab.py calibrate
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v2/lab.py run
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v2/lab.py report
```

Run each command only after the preceding command succeeds. If calibration's
measured remaining projection exceeds the local cap, Claude stops and asks the
owner. `run` also refuses over-cap projections. A `PAUSED_CAP` receipt authorizes
resume with the same `run` command and unchanged code. Inspect `RUN.json`: do not
mistake a cap pause for DONE. If calibration reaches the cap before finishing, resume with the same `calibrate`
command; its completed samples are reused. Generate `report` after completion or
to inspect a partial run. `calibrate` and `run` re-exec under caffeinate and retain the identical
host pgrep gate; UNAVAILABLE stops execution, ACTIVE waits, CLEAR permits work.

The setting lives at `../s4_shape_lab_v1/raw/LAB_CAP.json`, already ignored by
v1's `/raw/` rule. It is intentionally outside all preparation/binary/source
identities. Missing means 3600 seconds. A present file must contain a positive
integer cap and owner approval/date, for example:

```json
{"cap_seconds": 10800, "approved_by": "owner", "date": "2026-10-08"}
```

Each invocation snapshots the value and SHA256 of the exact bytes read in its
attempt receipt; calibration, run gate and run receipts also record them. Changing
the local setting does not invalidate entropy or completed fights. The cap is
per invocation, permitting the owner's resume instruction; cumulative elapsed
compute is disclosed in attempt receipts, not subtracted from the next allowance.
The cap bounds native child execution. In-flight compression, hashing and initial
metrics are allowed to finish and may add bookkeeping time at the boundary.
Standalone report/replay rendering is outside the compute cap and unmeasured.

Calibration uses exactly 59 existing allocations: cluster 0/orientation 0 of
each drill/arm/opponent cell (56, including v6 D4/D5 and all C3 opponents), plus
series 0/fight 1 for v7, forcedP16 and full elite (3). It writes ordinary immutable
fight receipts. All are the same fights the full run uses; completed fights are
verified and reused, never executed again. The three series samples do not advance
past fight 1; a non-win finalizes naturally on the full run.

`CALIBRATION.json` records the subset, actual six-worker wall time, sample and timing-attempt hashes
and method. Per-category measured cost is scaled to the 150-second simulated
horizon, then remaining drill and worst-case series work is divided by measured
throughput (actual worker count and observed utilization). Series time is at least
the longest remaining sequential series suffix. Apply a declared 20% margin. First non-wins remove
unreachable series fights from the remaining count. Resume recomputes remaining
work from validated completed receipts. The old serial projection is historical.
This is an estimate; later tactics, survivors and host load can change throughput.

When the native deadline expires, the child is terminated by subprocess timeout;
its partial request/claim/streams are preserved under ignored `raw/interrupted/`
with their hashes and an explicit retryable interruption receipt. Only that
unfinished fight restarts on the next invocation. Completed receipts are never
moved or repeated. External kills, unclosed attempts, identity drift and incomplete
cells from other failures stop for investigation; no automatic cleanup or replay.
No source edits during calibration/run. A sealed v2 source change requires another
new version, not editing the v2 declaration or its allocated entropy.

Owner recheck: `OWNER_RECHECK_CONTROL.md`; disposition: `CONTROL_DISPOSITION.md`.
Tracking in `docs/PLAN_CURRENT.md` is left unstaged by owner instruction.
Focused tests use zero-duration native admission only; control-flow timing/run
fixtures are mocked and execute no drill, series or calibration fight:

```sh
mkdir -p evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v2/.pytest_cache
.venv/bin/python -m pytest -q -x evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v2/test_lab.py --basetemp=evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v2/.pytest_cache/test_tmp
```
