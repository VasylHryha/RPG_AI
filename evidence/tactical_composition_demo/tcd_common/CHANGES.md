# What `tcd_common` repairs, and what it leaves frozen

New exploratory experiments import this package only. `demo.py`, `change.py`, `change2.py`, `tactics.py`, their tests and specifications stay byte-for-byte as
recorded (their hashes are in each run's `RUN_STARTED.json`). Tests: `.venv/bin/python -m pytest -q -p no:cacheprovider evidence/tactical_composition_demo/tcd_common/test_common.py`
(outside `testpaths`, so the normal suite does not run them).

| Module | Repair | Recorded behaviour it replaces |
|---|---|---|
| `fileio.atomic_write` | temporary name unique per process, thread and call; cleanup on failure; directory fsync | `...tmp<pid>` shared by the watchdog and main thread |
| `stats.ratio_verdict` | inf against inf is INDETERMINATE | returned SUPPORTED |
| `stats.bootstrap_median_ci`, `paired_median_ci` | percentile intervals over seeds (seeds replicate one environment, not independent tasks) | no intervals |
| `metrics.agreement`, `step_*` | every quantity on multi-enemy states; tie-best step accepts a hold when any tied-best label is a hold; a wrong hold counts 90 degrees and is reported | step over all states; correct holds scored as angle errors |
| `supervise.run_jobs` | `done` only if every job was submitted and finished | last job finishing after the deadline reported `deadline` |
| `supervise.Watchdog` | cancel and expiry mutually exclusive; cleanup by process handle then `pkill`; failures recorded in `HARD_STOP.json`; injectable exit | cancelled only after evaluation; `pkill` failures swallowed |
| `harness.preflight` | exact repo-relative paths from `git status -z --untracked-files=all` | substring matching (`'/run_change'`); empty-directory test |
| `harness.run_experiment` | watchdog cancelled before evaluation; RSS normalised to bytes; resource errors recorded | evaluation inside the watchdog window; `ru_maxrss` in platform units |
| `reproduce_seed.py` | re-runs one seed of a recorded harness at HEAD and compares every stored number (`SEED_REPRODUCTION.json`: Stage 0 and change-cost r2, seed 0, identical) | no determinism check existed |
| `fileio.stream` | refuses entropy under 65 bits: `SeedSequence` pads short lists with zeros, so keys (1, 1, 0) and (1, 1, 0, 0) alias; the recorded streams use 96-bit entropy and are unaffected | unchecked |
| `legacy.py`, `verify_legacy.py` | bit-exact comparison of every primitive the harnesses call against the three recorded `tactics.py` versions (recovered with `git show <run head>`) | no regression gate; `LEGACY_EQUIVALENCE.json` is its record |

Not repaired (kept as history, see `../CORRECTIONS.md` section D): the three `dev_*.py` scripts that execute at import, `history_ability_attempt/`, the
`USE_BURST` global, `change.py`'s superseded protocol (imported by `change2.py`).
