PARTIAL

# Shape lab v1: development tooling and observations

Implements SHAPE_LAB_SPEC §§3–6. No judging seeds, registered endpoints, policy changes or scientific acceptance.
All changes are new files in this folder. docs/PLAN_CURRENT.md is not edited; owner recheck and disposition are local.

## Section-3 checks

| Check | Result |
|---|---|
| 50v50 entire output byte equality | PASS |
| dummy_static no damage/no launches/no movement | PASS |
| dummy_static_fire attacks and never moves | PASS |
| dummy_advance catalog speed, gun pursuit, fire contract | PASS |
| dummy_advance_fire catalog speed, gun pursuit, fire contract | PASS |
| static body stays fixed under collision | PASS |
| placement deterministic and first role slots | PASS |
| carry-over heals survivors, dead stay absent | PASS |

Compatibility output stream SHA256: `336df649bbe1409b63fa5429737fdb0a6f8b3698e44074b110bc3dac555f9e75`.
Measured full-output compatibility fight: 18.266 seconds.

Required check receipt status: PASS

## Projection and process gate

```json
{
  "status": "ESTIMATED",
  "drill_fights": 560,
  "series_fights_max": 300,
  "workers_max": 6,
  "observed_v7_seconds_per_fight": 18.265599875,
  "full_duration_v7_proxy_seconds": 67.20784909035119,
  "non_elite_serial_proxy_seconds": 51077.965308666906,
  "elite_fights_max": 100,
  "elite_seconds_per_fight_estimate": 91.43536194241376,
  "elite_estimate_source": "native_benchmark_r1/benchmark.json",
  "elite_estimate_source_sha256": "4654be44fd9330e29fab3732b6f12d32582993aa411f789a7214f24fd78414dc",
  "elite_historical_max_seconds_per_step": 0.0005382695590327167,
  "elite_margin_multiplier": 10,
  "total_projected_seconds": 175939.0019383123,
  "total_projected_minutes": 2932.316698971872,
  "postprocessing_estimate_seconds": 115597.50043540404,
  "analysis_reserve_seconds": 120,
  "assumption": "Serial costs; no worker speedup. Full-output compatibility scaled to 150s. Historical full-elite planning rate scaled to 4501 ticks, 10x margin; two more full-stream analysis passes plus 120s reserve.",
  "limits": "Historical elite benchmark is a different engine revision/short fights, without observer output. Current full-elite series and 6-worker throughput have not been timed; this is a conservative planning estimate, not a measured upper bound.",
  "cap_seconds": 3600
}
```

Process gate: **UNAVAILABLE**. sysmon request failed with error: sysmond service not found
pgrep: Cannot get process list

## Per-drill results

Criteria apply per fight; the table reports how many fights met the complete conjunction. Missing observations are **not met (not evaluated)**, not measured failures. Conditional times and shares show evaluated denominators in JSON.

### D1

all enemy guns dead; own guns lost ≤1; gun damage share while enemy guns alive ≥60%

| Arm | Opponent | Completed / planned | Section-4 metrics (means) | Draft criteria |
|---|---|---:|---|---|
| v7 | specified dummy/regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | specified dummy/regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |

### D2

≤1.5 own units hit per landed enemy shell

| Arm | Opponent | Completed / planned | Section-4 metrics (means) | Draft criteria |
|---|---|---:|---|---|
| v7 | specified dummy/regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | specified dummy/regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |

### D3

0 enemy ranged/melee damage to own guns

| Arm | Opponent | Completed / planned | Section-4 metrics (means) | Draft criteria |
|---|---|---:|---|---|
| v7 | specified dummy/regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | specified dummy/regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |

### D4

exchange >1:1; majority of melee survive

| Arm | Opponent | Completed / planned | Section-4 metrics (means) | Draft criteria |
|---|---|---:|---|---|
| v7 | specified dummy/regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | specified dummy/regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v6 | specified dummy/regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |

### D5

no units out of weapon reach during fight

| Arm | Opponent | Completed / planned | Section-4 metrics (means) | Draft criteria |
|---|---|---:|---|---|
| v7 | specified dummy/regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | specified dummy/regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v6 | specified dummy/regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |

### C1

elimination before 150s; no own losses

| Arm | Opponent | Completed / planned | Section-4 metrics (means) | Draft criteria |
|---|---|---:|---|---|
| v7 | specified dummy/regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | specified dummy/regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |

### C2

elimination before 150s; whole-army draft ≤4 own losses

| Arm | Opponent | Completed / planned | Section-4 metrics (means) | Draft criteria |
|---|---|---:|---|---|
| v7 | specified dummy/regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | specified dummy/regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |

### C3

elimination before 150s; whole-army draft ≤4 own losses

| Arm | Opponent | Completed / planned | Section-4 metrics (means) | Draft criteria |
|---|---|---:|---|---|
| v7 | regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | line | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | wide line | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | wedge | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | box | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | column | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | loose | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | screen | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | crescent | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | ring | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | wedge hold | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | line anvil | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | wedge flank | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | loose free | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | swarm | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | loose skirmish | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | loose berserk | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | storm | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | wolfpack | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| v7 | alone | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | regular | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | line | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | wide line | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | wedge | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | box | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | column | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | loose | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | screen | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | crescent | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | ring | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | wedge hold | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | line anvil | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | wedge flank | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | loose free | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | swarm | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | loose skirmish | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | loose berserk | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | storm | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | wolfpack | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |
| forcedP16 | alone | 0 / 10 | {"status":"not_run"} | not met (not evaluated) |

## S10X: abilities off; regular skills, uniform POOL replacement draws

| Arm | Series completed / 10 | Streak mean / median / min / max | Fight reached | Mean own losses per fight | Draft ≤4 losses |
|---|---:|---|---|---|---|
| v7 | 0 / 10 | null | not_run | not_run | not met (not evaluated) |
| forcedP16 | 0 / 10 | null | not_run | not_run | not met (not evaluated) |
| elite | 0 / 10 | null | not_run | not_run | not met (not evaluated) |

Reference band: owner recollection of typical streak 6, sometimes 8; no statistical population claim.

### Units before each fight and per-tactic losses

| Arm | Series | Streak | Fight reached | Units before each fight |
|---|---:|---:|---:|---|
| v7 / forcedP16 / elite | — | not_run | not_run | not_run |

| Arm | Tactic | Fights | Non-wins | Units lost total / mean |
|---|---|---:|---:|---|
| v7 / forcedP16 / elite | not_run | 0 | not_run | not_run |

## Limits and definitions

- Drills planned: 560 fights; series at most 300. v6 uses delivered attempt-2 θ_v6 in D4 and D5; v7/forcedP16 use θ* ordinal 161. Elite retains full catalog planning and rollout behavior.
- D1 line axial separation is 500 px; cross-line diagonal distances can exceed 600 px. D5 starts 250 px apart. These geometries are declared before drills.
- Lab heading is radians stored as native guard direction; this engine has no general unit-facing state. Army-facing remains the scripted pack direction.
- Static dummies disable reflex dodges and restore their fixed post after native collision separation; other units still receive native collision pushes.
- All enemy-shell multiplicities use landed shells including zero-hit shells; unresolved shells at termination are censored. Firepower uses native range/gap with no extra margin and integrates all alive-unit seconds.
- D1 gun damage share includes only enemy damage while any enemy gun lives; friendly damage is excluded. Null shares mean no qualifying damage. Conditional kill times do not impute a 150-second success.
- The unchanged scorecard can read these observer streams via its RAW constant. Its hardcoded 50/10 denominators and reach+50 differ from reduced drills; it is explicitly auxiliary.
- Replay files retain every executed drill/series fight; deterministic sampling reduces FPS to enforce 8,000,000-byte limit. Replay index lists actual FPS. No replay is fabricated for an unrun fight.
- Slow-field launches are excluded from damaging-shell denominators. Raw entropy, requests, native streams and claims stay in ignored raw/. Immutable completions verify request/code/raw identity; interrupted cells are never automatically replayed.
- Delivery: UNCOMMITTED_READ_ONLY. The managed permission profile grants read-only access to the main .git directory. All task files are new in s4_shape_lab_v1; no files are staged, no commit/bundle/substitute repository is created.
- Process gate: UNAVAILABLE. Drills and series are NOT_RUN. The full projection includes a disclosed historical elite estimate; current full-elite throughput remains unmeasured. Execution requires a clear pgrep gate and an estimate within 60 minutes.

## New uncommitted files

- `s4_shape_lab_v1/.gitignore`
- `s4_shape_lab_v1/BUILD.json`
- `s4_shape_lab_v1/C1_SUMMARY.json`
- `s4_shape_lab_v1/C2_SUMMARY.json`
- `s4_shape_lab_v1/C3_SUMMARY.json`
- `s4_shape_lab_v1/CHECKS.json`
- `s4_shape_lab_v1/D1_SUMMARY.json`
- `s4_shape_lab_v1/D2_SUMMARY.json`
- `s4_shape_lab_v1/D3_SUMMARY.json`
- `s4_shape_lab_v1/D4_SUMMARY.json`
- `s4_shape_lab_v1/D5_SUMMARY.json`
- `s4_shape_lab_v1/DECLARATION.json`
- `s4_shape_lab_v1/DELIVERY.json`
- `s4_shape_lab_v1/FINAL_VERIFICATION.json`
- `s4_shape_lab_v1/OWNER_RECHECK.md`
- `s4_shape_lab_v1/PROCESS_GATE.json`
- `s4_shape_lab_v1/PROJECTION.json`
- `s4_shape_lab_v1/PROJECTION_INTERPRETATION.md`
- `s4_shape_lab_v1/README.md`
- `s4_shape_lab_v1/REPLAY_INDEX.json`
- `s4_shape_lab_v1/REVIEW_DISPOSITION.md`
- `s4_shape_lab_v1/S10X_SUMMARY.json`
- `s4_shape_lab_v1/TESTS.json`
- `s4_shape_lab_v1/TESTS.stderr.log`
- `s4_shape_lab_v1/TESTS.stdout.log`
- `s4_shape_lab_v1/build.py`
- `s4_shape_lab_v1/checks.py`
- `s4_shape_lab_v1/lab.py`
- `s4_shape_lab_v1/lab_dispatch.cpp`
- `s4_shape_lab_v1/lab_native.h`
- `s4_shape_lab_v1/metrics.py`
- `s4_shape_lab_v1/replays.py`
- `s4_shape_lab_v1/report.py`
- `s4_shape_lab_v1/test_lab.py`
- `s4_shape_lab_v1/SHAPE_LAB_REPORT.md`

Build products and raw ledgers are new ignored files under `s4_shape_lab_v1/build/` and `s4_shape_lab_v1/raw/`.

## Owner recheck

See OWNER_RECHECK.md and REVIEW_DISPOSITION.md in this folder (separate Codex reviewer, same family).
These replace plan tracking for this task because the owner prohibits edits to existing files.

## Final verification

Focused suite: **17 passed** in 0.71 s; measured caffeinated process time 1.270 s. Run once after all planned code and review-driven edits. Fixtures cover invalid native scenarios, catalog kind stats, role capacities/orientations, strict series stopping and healed cohort carry-over, shell miss/Slow denominators, expired deadlines, receipt tampering, failed-check rendering and replay size fallback. Native test scenarios have duration 0; no drills, series or judging runs occurred.

FINAL_VERIFICATION.json records current source/binary identities, empty tracked diff, local ignore evidence and candidate file sizes. All task files remain uncommitted because .git is read-only in the managed permission profile. No staging, hook bypass, bundle or push.

Separate Codex owner recheck: all six code findings resolved; see OWNER_RECHECK.md and REVIEW_DISPOSITION.md. Viewer limitation is explicit: these JSON files have the requested stored replay schema, but the delivered HTML hardcodes validation labels and its first pick; a future viewer adapter is required for arbitrary lab tags. Visual usability/acceptance is not claimed.

Execution stop: conservative projection is 48.87 hours serial (idealized division by six is 8.15 hours, unmeasured). This exceeds 60 minutes, so no drill or series was started. The independent pgrep failure also prevents verifying an exclusive compute window. Claude asks the owner before any longer continuation; do not rerun successful checks for unchanged code.
