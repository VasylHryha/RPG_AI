# Tactical composition demo — exploratory line, NOT a milestone, NOT C6 evidence

Authority and scope: `docs/decisions/0028-owner-directed-exploratory-composable-shapes.md`. Verdict words here (SUPPORTED, REFUTED, INDETERMINATE) are
exploratory vocabulary, not milestone verdicts. The work is outside the GeoTactics GT0–GT5 plan. No cross-family review of the recorded results exists and none is claimed for them
(Codex reviewed the decision record, the corrections, the tooling and the next proposal).
**Read `CORRECTIONS.md` before quoting any number from the reports.**

**The idea:** build an AI unit from small pieces, each with one job, instead of one big learned block. A unit is two pieces, **AIM** (which enemy to hit)
and **MOVE** (where to step), wired together. The questions: do the wired pieces play as well as one big controller of the same size taught on the same
examples; do they cope with a unit type nobody trained on; how cheap are they to build and to change.

**Latest (0d Part A, `REPORT_0D.md`):** a structured network of the same graph trained jointly scores within 0.02 of the separately taught pieces and about 0.4 above every flat model, so the Stage 0 advantage is the structure, not the separate teaching (V3 SUPPORTED, V2 EQUIVALENT).

**What is established (one invented sandbox, scripted teachers, imitation, ordinary small networks):** the wired pieces match the scripted expert within about
0.03 on seen mixes and beat an equal-size flat block widely; after a targeting-rule change, retraining only AIM reached the 0.80 level at the grid floor (100 rows) where the flat block first reached it at 1,000 rows
(a ratio of registered first-success grid values, not a bound on the need). **Not established:** that the advantage comes from composition rather than from the structure copied from the teacher (no structured
end-to-end baseline), anything about a second level (squad), learning from outcomes, geometry, oscillators or "vibration". Why this exists: `MOTIVATION.md`.

## Runs (each one-shot; the run directory is the latch)

| Step | Specification | Code | Spec/entropy | Started from | Record | Report |
|---|---|---|---|---|---|---|
| Stage 0 (AIM + MOVE) | `SPECIFICATION.md` | `demo.py`, `tactics.py` | `SPEC.json` | `bc5ce29` | `run/` (smoke: `smoke_run/`) | `REPORT.md` |
| Change-cost r1 | `SPECIFICATION_CHANGE.md` | `change.py` | `SPEC_CHANGE.json` | `d32485a` | `run_change/` (`smoke_run_change/`) | `REPORT_CHANGE.md` (INDETERMINATE; amended) |
| Change-cost r2 | `SPECIFICATION_CHANGE2.md` | `change2.py` | `SPEC_CHANGE2.json` | `3381e03` | `run_change2/` (`smoke_run_change2/`) | `REPORT_CHANGE2.md` |
| 0d Part A (structure versus composition) | `SPECIFICATION_0D.md`, `PROPOSAL_0D.md` | `zd_run.py`, `zd_models.py`, `tcd_common/` | `SPEC_0D.json` | `c747e76` | `run_0d/` (`smoke_run_0d/`; development in `dev_0d/`) | `REPORT_0D.md` |

Names: Stage 0 = AIM + MOVE; 0b = the mage's burst piece (deferred); 0c = the change-cost test, r1 and r2 its revisions. Each `RUN_STARTED.json` carries the
hashes of the files the run depends on. The current `tactics.py` differs from the Stage 0 and r1 versions (additive changes); `tcd_common/LEGACY_EQUIVALENCE.json`
`tactics.py` is frozen and pinned by hash; `tcd_common/SEED_REPRODUCTION.json` records an exact re-run of seed 0 of Stage 0 and of change-cost r2 (one seed each). `MOTIVATION.md` has been edited since the change runs hashed it, so its hash in those records no longer
matches HEAD; the `SPEC*`, specification and code hashes do.

## Superseded or history (kept, do not use as current)

- `PROPOSAL.md`: the draft proposal, never approved as written; replaced by the specifications and the owner messages in decision 0028.
- `history_ability_attempt/`: the first design with the mage's burst (cannot run as stored).
- `REPORT_CHANGE.md`'s explanation of the r1 failure: corrected by its own amendment.
- `dev_calibration.*`, `dev_doctrine.*`, `dev_learnability.*`: development records on separate entropy. **Do not run or import the `.py` files**: they execute at import
  and overwrite their committed JSON. They are hashed into the run records and unchanged.

## Current work

- `tcd_common/`: repaired shared tooling (see `tcd_common/CHANGES.md`); new experiments use it, the recorded harnesses stay frozen.
- 0d Part A is complete (`REPORT_0D.md`): in this sandbox the gain is the structure, not the separate teaching. `PROPOSAL_0D.md` Appendix A lists what a MOVE-only change test and an extrapolation test would need.
- Next, not yet proposed: the squad level (units into a squad) and learning the pieces from outcomes.

## Tests

The demo tests live here, outside the repository's `testpaths`, so the normal suite does not run them. Run each once after a change batch, from the repository root:
`.venv/bin/python -m pytest -q -p no:cacheprovider evidence/tactical_composition_demo/test_tactics.py` (and `test_demo.py`, `test_change.py`, `test_change2.py`,
`tcd_common/test_common.py`).
