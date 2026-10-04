# Tactical composition demo — exploratory line, NOT a milestone, NOT C6 evidence

Authority and scope: `docs/decisions/0028-owner-directed-exploratory-composable-shapes.md`. Verdict words here (SUPPORTED, REFUTED, INDETERMINATE) are
exploratory vocabulary, not milestone verdicts. The work is outside the GeoTactics GT0–GT5 plan. No cross-family review of the recorded results exists and none is claimed for them
(Codex reviewed the decision record, the corrections, the tooling, the 0d proposal and the 0e registration; no result).
**Read `CORRECTIONS.md` before quoting any number from the reports.**

**The idea:** build an AI unit from small pieces, each with one job, instead of one big learned block. A unit is two pieces, **AIM** (which enemy to hit)
and **MOVE** (where to step), wired together. The questions: do the wired pieces play as well as one big controller of the same size taught on the same
examples; do they cope with a unit type nobody trained on; how cheap are they to build and to change.

**Latest (0e, `REPORT_0E.md`, corrected 2026-10-04):** on a revised task where target choice matters, learned pieces replace the scripted ones within the 0.05 margin (at most 0.035 worse) and swap with a conventional policy's branches; the AIM-to-MOVE connection is worth about +0.12 against a coherent nearest-enemy unit; small faults on it cost almost nothing, large ones collapse it; pieces are **not** stronger than a conventional per-slot policy (and under imitation could not be: the teacher is the ceiling). Earlier (0d): the Stage 0 advantage over flat networks comes from the per-enemy structure, not from separate teaching. **What the owner must still decide:** `docs/decisions/0028-owner-directed-exploratory-composable-shapes.md`, "Pending owner decisions".

**What is established (one invented sandbox, scripted teachers, imitation, ordinary small networks):** the wired pieces match the scripted expert within about 0.03 on seen mixes and beat small flat blocks widely; after a targeting-rule change, retraining only AIM reached the 0.80 level at the grid floor (100 rows) where the flat block first reached it at 1,000 rows (a ratio of registered first-success grid values, not a bound on the need); a jointly trained network of the same graph does about as well as the separately taught pieces.
**Not established:** that this is composition rather than a hand-given graph (both C and S1 were given the teacher's decomposition and intermediate labels); which element of the graph matters; that flat networks cannot do it (the registered flat baseline is weak); anything about a second level (squad), learning from outcomes, geometry, oscillators or "vibration". Why this exists: `MOTIVATION.md`.

## Runs (each one-shot; the run directory is the latch)

| Step | Specification | Code | Spec/entropy | Started from | Record | Report |
|---|---|---|---|---|---|---|
| Stage 0 (AIM + MOVE) | `SPECIFICATION.md` | `demo.py`, `tactics.py` | `SPEC.json` | `bc5ce29` | `run/` (smoke: `smoke_run/`) | `REPORT.md` |
| Change-cost r1 | `SPECIFICATION_CHANGE.md` | `change.py` | `SPEC_CHANGE.json` | `d32485a` | `run_change/` (`smoke_run_change/`) | `REPORT_CHANGE.md` (INDETERMINATE; amended) |
| Change-cost r2 | `SPECIFICATION_CHANGE2.md` | `change2.py` | `SPEC_CHANGE2.json` | `3381e03` | `run_change2/` (`smoke_run_change2/`) | `REPORT_CHANGE2.md` |
| 0d Part A (structure versus composition) | `SPECIFICATION_0D.md`, `PROPOSAL_0D.md` | `zd_run.py`, `zd_models.py`, `tcd_common/` | `SPEC_0D.json` | `c747e76` | `run_0d/` (`smoke_run_0d/`; development in `dev_0d/`) | `REPORT_0D.md` |
| 0e (replacement and connection) | `SPECIFICATION_0E.md` (design `PROPOSAL_0E.md`) | `ze_run.py`, `ze_core.py`, `ze_flat.py`, `tactics_e2.py` | `SPEC_0E.json` | `1d21533` | `run_0e/` (`smoke_run_0e/`; pre-review smoke `smoke_run_0e_pre_review/`; development `dev_0e/`) | `REPORT_0E.md` |

Names: Stage 0 = AIM + MOVE; 0b = the mage's burst piece (deferred); 0c = the change-cost test, r1 and r2 its revisions; 0d = structure versus composition; 0e = replacement and connection (task V3). Each `RUN_STARTED.json` carries the
hashes of the files the run depends on. The current `tactics.py` differs from the Stage 0 and r1 versions (additive changes, compared once at commit `6e92322` and found identical on the exercised primitives, see `tcd_common/CHANGES.md`);
`tactics.py` is frozen and pinned by hash (`tcd_common/test_common.py`); `tcd_common/SEED_REPRODUCTION.json` records an exact re-run of seed 0 of Stage 0 and of change-cost r2 (one seed each; its HEAD, 13662a4, predates later harness edits that do not touch the seed computation). `MOTIVATION.md` has been edited since the change runs hashed it, so its hash in those records no longer
matches HEAD; the `SPEC*`, specification and code hashes do.

## Superseded or history (kept, do not use as current)

- `PROPOSAL_0E.md`: hashed into the 0e run record, so not edited; its four-claim wording is superseded by `SPECIFICATION_0E.md` (five claims). `smoke_run_0e_pre_review/`: the smoke before the Codex corrections.
- `PROPOSAL.md`: the draft proposal, never approved as written; replaced by the specifications and the owner messages in decision 0028.
- `history_ability_attempt/`: the first design with the mage's burst (cannot run as stored).
- `REPORT_CHANGE.md`'s explanation of the r1 failure: corrected by its own amendment.
- `dev_calibration.*`, `dev_doctrine.*`, `dev_learnability.*`: development records on separate entropy. **Do not run or import the `.py` files**: they execute at import
  and overwrite their committed JSON. They are hashed into the run records and unchanged.

## Current work

- `tcd_common/`: repaired shared tooling (see `tcd_common/CHANGES.md`); new experiments use it, the recorded harnesses stay frozen.
- 0d Part A is complete and was rechecked on 2026-10-04 (`REPORT_0D.md`, "Post-run recheck"): the gain is consistent with coming from the graph both recipes were given, not from separate teaching, against a weak flat baseline. After the run the registered files (`SPECIFICATION_0D.md`, `PROPOSAL_0D.md`, `SPEC_0D.json`, `zd_*.py`, `test_zd.py`, `tcd_common/`, `dev_0d/` records) were **not edited** (their hashes are in `run_0d/RUN_STARTED.json`); post-run additions are new files: `verify_run_0d.py` and `verify_run_0d_result.json` (saved weights reproduce every recorded score), `test_zd_audit.py`, `dev_0d/POSTRUN_NOTES.md` and `dev_0d/probe_flat_capacity*`. `PROPOSAL_0D.md` Appendix A lists what a MOVE-only change test and an extrapolation test would need.
- **0e (replacement and connection, two pieces) — COMPLETE** (`REPORT_0E.md`, run `run_0e/` from `1d21533` after Codex's review and the owner's approval): A1 SUPPORTED (learned pieces replace the scripted ones within 0.03), A2 SUPPORTED (swap with a conventional policy), B1 SUPPORTED (the connection is useful: cutting it costs 0.16 to 0.68), B2 INDETERMINATE (all fault and repeatability components passed; the spread bound 0.054 missed 0.05), B3 REFUTED (pieces play as well as, not better than, a per-slot conventional policy). Task V3 of `tactics_e2.py`; development in `dev_0e/`. Next: a connection-discovery pilot.

## Tests

The demo tests live here, outside the repository's `testpaths`, so the normal suite does not run them. Run each once after a change batch, from the repository root:
`.venv/bin/python -m pytest -q -p no:cacheprovider evidence/tactical_composition_demo/test_tactics.py` (and `test_demo.py`, `test_change.py`, `test_change2.py`,
`tcd_common/test_common.py`, `test_zd.py`, `test_zd_audit.py`, `test_ze.py`, `test_ze_run.py`, `test_ze_audit.py`). Round-trip checks of recorded runs: `verify_run_0d.py`, `verify_run_0e.py`.
