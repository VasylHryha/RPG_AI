# Tactical composition demo — exploratory line, NOT a milestone, NOT C6 evidence

Authority and scope: `docs/decisions/0028-owner-directed-exploratory-composable-shapes.md`. Verdict words here (SUPPORTED, REFUTED, INDETERMINATE) are
exploratory vocabulary, not milestone verdicts. The work is outside the GeoTactics GT0–GT5 plan. No cross-family review exists and none is claimed.
**Read `CORRECTIONS.md` before quoting any number from the reports.**

**The idea:** build an AI unit from small pieces, each with one job, instead of one big learned block. A unit is two pieces, **AIM** (which enemy to hit)
and **MOVE** (where to step), wired together. The questions: do the wired pieces play as well as one big controller of the same size taught on the same
examples; do they cope with a unit type nobody trained on; how cheap are they to build and to change.

**What is established (one invented sandbox, scripted teachers, imitation, ordinary small networks):** the wired pieces match the scripted expert within about
0.03 on seen mixes and beat an equal-size flat block widely; retraining only AIM after a targeting-rule change needs at least ten times fewer new rows than
retraining the flat block. **Not established:** that the advantage comes from composition rather than from the structure copied from the teacher (no structured
end-to-end baseline), anything about a second level (squad), learning from outcomes, geometry, oscillators or "vibration". Why this exists: `MOTIVATION.md`.

## Runs (each one-shot; the run directory is the latch)

| Step | Specification | Code | Spec/entropy | Started from | Record | Report |
|---|---|---|---|---|---|---|
| Stage 0 (AIM + MOVE) | `SPECIFICATION.md` | `demo.py`, `tactics.py` | `SPEC.json` | `bc5ce29` | `run/` (smoke: `smoke_run/`) | `REPORT.md` |
| Change-cost r1 | `SPECIFICATION_CHANGE.md` | `change.py` | `SPEC_CHANGE.json` | `d32485a` | `run_change/` (`smoke_run_change/`) | `REPORT_CHANGE.md` (INDETERMINATE; amended) |
| Change-cost r2 | `SPECIFICATION_CHANGE2.md` | `change2.py` | `SPEC_CHANGE2.json` | `3381e03` | `run_change2/` (`smoke_run_change2/`) | `REPORT_CHANGE2.md` |

Names: Stage 0 = AIM + MOVE; 0b = the mage's burst piece (deferred); 0c = the change-cost test, r1 and r2 its revisions. Each `RUN_STARTED.json` carries the
hashes of the files the run depends on. The current `tactics.py` differs from the Stage 0 and r1 versions (additive changes); `tcd_common/LEGACY_EQUIVALENCE.json`
records an exact match on every primitive the harnesses call, and `tcd_common/SEED_REPRODUCTION.json` an exact re-run of seed 0 of Stage 0 and of change-cost r2. `MOTIVATION.md` has been edited since the change runs hashed it, so its hash in those records no longer
matches HEAD; the `SPEC*`, specification and code hashes do.

## Superseded or history (kept, do not use as current)

- `PROPOSAL.md`: the draft proposal, never approved as written; replaced by the specifications and the owner messages in decision 0028.
- `history_ability_attempt/`: the first design with the mage's burst (cannot run as stored).
- `REPORT_CHANGE.md`'s explanation of the r1 failure: corrected by its own amendment.
- `dev_calibration.*`, `dev_doctrine.*`, `dev_learnability.*`: development records on separate entropy. **Do not run or import the `.py` files**: they execute at import
  and overwrite their committed JSON. They are hashed into the run records and unchanged.

## Current work

- `tcd_common/`: repaired shared tooling (see `tcd_common/CHANGES.md`); new experiments use it, the recorded harnesses stay frozen.
- `PROPOSAL_0D.md` (draft, not approved): the next experiment. Nothing in it runs before the owner approves it.

## Tests

The demo tests live here, outside the repository's `testpaths`, so the normal suite does not run them. Run each once after a change batch, from the repository root:
`.venv/bin/python -m pytest -q -p no:cacheprovider evidence/tactical_composition_demo/test_tactics.py` (and `test_demo.py`, `test_change.py`, `test_change2.py`,
`tcd_common/test_common.py`).
