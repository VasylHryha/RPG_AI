# What `tcd_common` repairs, and what it leaves frozen

New exploratory experiments import this package only. `demo.py`, `change.py`, `change2.py`, `tactics.py`, their tests and specifications stay byte-for-byte as
recorded (their hashes are in each run's `RUN_STARTED.json`). Tests: `.venv/bin/python -m pytest -q -p no:cacheprovider evidence/tactical_composition_demo/tcd_common/test_common.py`
(outside `testpaths`, so the normal suite does not run them).

The three-version comparison of `tactics.py` against the recorded runs was run once (commit `6e92322`: all three matched, with the full sha256 of each recovered file equal to its run record) and then removed; its coverage excluded the changed-doctrine and fine-tuning paths, and the r2 version is byte-identical to the current file. The hash pin and `reproduce_seed.py` replace it.

| Module | Repair | Recorded behaviour it replaces |
|---|---|---|
| `fileio.atomic_write` | temporary name unique per process, thread and call; cleanup on failure; directory fsync | `...tmp<pid>` shared by the watchdog and main thread |
| `stats.ratio_verdict` | inf against inf is INDETERMINATE | returned SUPPORTED |
| `stats.by_seed`, `paired_by_seed`, `bootstrap_median_ci`, `paired_median_ci` | differences built from explicit seed identities; a missing, duplicate or non-finite endpoint is an error; shapes must match; percentile intervals over seeds (seeds replicate one environment, not independent tasks) | `col()` dropped missing values per column, so seeds could mispair; no intervals |
| `metrics.joint_action` (new) | the primary estimand: chosen enemy tied-best AND step matches the registered teacher's step toward that enemy; the registered movement rule is passed explicitly; strata hold, moving, back-off with counts | no joint criterion; movement scored against whichever rule `tactics` hardcodes |
| `metrics.agreement`, `step_*` | multi-enemy states only; every eligible state scored (a wrong hold and a wrong move on a hold state count 90 degrees and are reported); stop on empty population, dead chosen enemy, non-finite data; chance level 1 gives None | step over all states; a wrong move on an all-hold state dropped; correct holds scored as errors |
| `supervise.run_jobs` | `done` only if every job was submitted and finished | last job finishing after the deadline reported `deadline` |
| `supervise.Watchdog` | cancel and expiry mutually exclusive; cleanup by process handle then `pkill`; failures recorded in `HARD_STOP.json`; injectable exit | cancelled only after evaluation; `pkill` failures swallowed |
| `harness.preflight` | exact repo-relative paths from `git status -z --untracked-files=all` | substring matching (`'/run_change'`); empty-directory test |
| `harness.run_experiment` | jobs watchdog cancelled before evaluation; evaluation and the summary write run under their own `eval_cap` bound; jobs, evaluation and total seconds recorded separately; RSS in bytes | evaluation unbounded and unaccounted, or inside the jobs watchdog window; `ru_maxrss` in platform units |
| `reproduce_seed.py` | re-runs one seed of a recorded harness at HEAD and compares every stored number; records HEAD, file hashes, environment and a digest of the fresh values (`SEED_REPRODUCTION.json`: Stage 0 and change-cost r2, seed 0 only) | no determinism check existed |
| `fileio.stream` | refuses entropy under 65 bits: `SeedSequence` pads short lists with zeros, so keys (1, 1, 0) and (1, 1, 0, 0) alias; the recorded streams use 96-bit entropy and are unaffected | unchecked |
| `test_common.py` hash pin | `tactics.py` is frozen and must hash to the value recorded by the latest recorded run (`run_change2/RUN_STARTED.json`) | the file had been edited after Stage 0 with no gate |

Not repaired (kept as history, see `../CORRECTIONS.md` section D): the three `dev_*.py` scripts that execute at import, `history_ability_attempt/`, the
`USE_BURST` global, `change.py`'s superseded protocol (imported by `change2.py`).
