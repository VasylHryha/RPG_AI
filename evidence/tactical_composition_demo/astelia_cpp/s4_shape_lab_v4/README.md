# Shape lab v4: staged, paired REACT development comparison

Decision 0033: compare `forcedP16` (always commit, base) with
`forcedP16+react` (the admitted copied engine dodge). No elite rerun or optional
v7 arm. V1–v3 and the REACT adapter are read-only inputs. The v3 elite series
remains a historical, unpaired reference. This is development tooling, not a
registered experiment or scientific acceptance.

Preparation compiles a lightweight JSON host and observer collectors in
this folder. Adapter combat/controller objects with explicit hash pins are linked
unchanged; its unbound local objects are rebuilt here from admitted sources.
The overlay removes v7/react decision audits, gun-entry/kill attribution geometry
collectors and their output. Every fight uses observer-v1 units/dodges/damage/
launches, needed for mechanism measures and carry-over identity. No decision,
trace, debug, attribution or controller-audit streams. No controller/engine policy
changes or tuning. Raw compressed observer streams stay ignored in `raw/`.
Only C3 pairs 0 and 1 per arm and S10X series 0 per arm become viewer replays,
with deterministic FPS reduction and an 8 MB/file ceiling.

All future seeds, orientations and tactic draws are allocated during `prepare`,
excluding known development inventories, including v1–v3. Judging ledgers are
never read. Both arms share the allocated draws; controller RNG consumption
cannot change the draw schedule. S10X preserves each arm's own surviving cohort,
heals its members and fills the first slots of each role in the common map.
Dead IDs never return; first non-win stops that arm. The series can therefore
have unequal reached-fight counts. Only jointly reached positions have paired
fight differences, with their n and the survival-conditioning caveat.

Sizing, fixed before any fights:

- Mechanism: D2 under dummy artillery fire, 10 paired seeds / 20 actual fights.
- C3: regular + the 19 POOL tactics, 50/100/200 **total paired fights**, not per
  tactic (100/200/400 actual arm fights at the looks). First 20 pairs are the
  calibration samples and belong to the first look. Balanced fixed round-robin
  tactics yield 2–3/5/10 pairs per tactic; no fine per-tactic claims.
- S10X: 10 paired series per arm, up to 100 scheduled paired positions / 200
  actual fights. Early termination reduces execution. Streak distribution is
  primary; reach, role counts before each fight, and per-tactic won/non-win
  losses are secondary.

C3 retains v3 ability settings. S10X forces abilities off. Elimination wins
require enemy survivors = 0, own survivors > 0 and time < 150 seconds; all other
outcomes are non-wins. Mechanism metrics are own successful dodge intent ticks
per fight, distinct own units hit per landed enemy shell, and damage HP per
landed enemy shell. Zero-hit landed shells count; unresolved shells are censored.
Unmatched artillery damage is disclosed separately. Null ratios have no landed
shell denominator. Pooled ratios weight shells; paired differences average
per-fight ratios with both denominators and explicitly give n. Own losses on
wins and non-wins are reported separately, including pairs where both won or
both did not win.

The cap is the same mutable owner file as v3:
`../s4_shape_lab_v1/raw/LAB_CAP.json` (missing = 3600 seconds). Each invocation
snapshots its bytes/hash and uses the native deadline. A cap pause preserves
unfinished streams in `raw/interrupted/` and reuses all immutable completions.
No other incomplete cells or unclosed attempts are automatically retried.
Cap changes do not reseed or invalidate completed evidence. Standalone report
and post-fight bookkeeping are outside the native execution cap.

Calibration is stage-specific, runs only allocated fights, and cannot bypass
read gates: one mechanism pair, one C3 pair per opponent, then series 0/fight 1
per arm. No series fight is calibrated before C3 has been read and finished.
Costs are measured per arm/opponent, scaled conservatively to 150 simulated
seconds, with actual six-worker utilization, a sequential-series suffix bound
and 20% margin. Over-cap projection stops for the owner. Calibration timing is
an estimate, not a guarantee; host load/tactics/survivors can differ. Repeating
calibration verifies its samples and does not execute them again.

`calibrate` and `run` re-exec under caffeinate, hold an exclusive v4 process lock,
and use the v3 repository-scoped pgrep/lsof gate, extended to REACT native hosts.
Foreign repository processes are ignored; this repository's heavy jobs wait;
unavailable discovery stops. No fights may start on an unavailable gate.
Sources/native/input identities are sealed and checked before execution and
receipt reuse. Source changes after preparation require a new version.

The implementer runs focused tests once after the separate quick tooling review
and its real defect fixes, then builds and prepares without fights. Tests use
synthetic observer streams and mocked run control, never coreStep/fights:

```sh
.venv/bin/python -B -m pytest -q -x evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v4/test_lab.py --basetemp=evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v4/.pytest_cache/test_tmp
nice -n 15 .venv/bin/python -B evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v4/build.py
.venv/bin/python -B evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v4/lab.py prepare
```

Claude's host commands from the repository root (the delivered preparation is
already complete, so do not rebuild/reprepare):

```sh
LAB=evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v4/lab.py
.venv/bin/python -B "$LAB" calibrate --stage mechanism
.venv/bin/python -B "$LAB" run --stage mechanism
.venv/bin/python -B "$LAB" report
```

Read `MECHANISM_SUMMARY.json` / `SHAPE_LAB_REPORT.md` before further fights.
Claude records its actual observation, using either `continue` or `stop`:

```sh
.venv/bin/python -B "$LAB" review --stage mechanism --decision continue --note "<Claude's actual mechanism observation>"
.venv/bin/python -B "$LAB" calibrate --stage outcome --look 50
.venv/bin/python -B "$LAB" run --stage outcome --look 50
```

Read `OUTCOME_LOOK_50.json`. If unclear, record continue and advance:

```sh
.venv/bin/python -B "$LAB" review --stage outcome --look 50 --decision continue --note "<Claude's actual observation at 50>"
.venv/bin/python -B "$LAB" run --stage outcome --look 100
.venv/bin/python -B "$LAB" review --stage outcome --look 100 --decision continue --note "<Claude's actual observation at 100>"
.venv/bin/python -B "$LAB" run --stage outcome --look 200
.venv/bin/python -B "$LAB" review --stage outcome --look 200 --decision stop --note "<Claude's actual observation at 200; stop or park>"
```

At a clear earlier look, use `--decision stop` at that look and skip later C3
commands. No automatic numerical verdict or significance threshold is invented.
At 200 there are no further allocations; stop/park without expanding the run.
Once C3 has finished and been read:

```sh
.venv/bin/python -B "$LAB" calibrate --stage series
.venv/bin/python -B "$LAB" run --stage series
.venv/bin/python -B "$LAB" report
```

A mechanism `stop` blocks outcomes/series. An outcome `stop` ends additional C3
fights and still permits the declared series observation. Inspect `RUN_<stage>.json`
for DONE versus PAUSED_CAP; resume the same command after a cap pause. Reports
also render partial data with unmatched counts; partial data cannot open a gate.

| Stop question | Action | Responsible role |
|---|---|---|
| Is mechanism complete and read by Claude? No | Do not start C3 or its calibration | implementer |
| Did Claude stop at mechanism? Yes | Block all later stages | implementer |
| Has previous outcome look been read? No | Do not cross the look | implementer |
| Is a C3 result clear at this look? Yes | Record stop and skip remaining C3 looks | reviewer |
| Did C3 reach 200 pairs without a clear effect? Yes | Stop/park; do not enlarge | reviewer |
| Is C3 finished and read? No | Do not start series/calibration | implementer |
| Does measured remaining projection exceed cap? Yes | Stop and ask owner | implementer |
| Is repository process discovery unavailable? Yes | Stop and investigate | implementer |
| Are sources/receipts inconsistent or an attempt unclosed? Yes | Preserve artifacts and investigate | implementer |

Tooling review/disposition: `OWNER_RECHECK.md` and `DISPOSITION.md`.
No run or report-result review is claimed by this preparation. Claude performs
the mechanism read and later development-result review. Plan tracking stays
unstaged; the delivery commit contains only new files in this directory.
