# 0h revision 5.1 runner

Exploratory implementation under decision 0028 item 17. Claude independently
reviews the medium follow-up and runner; engine verification does not approve
section 10. See `RUNNER_REPORT.md` for the measured delivery state.

From the repository root, explicit build and the one engineering verification:

```sh
.venv/bin/python evidence/tactical_composition_demo/growing_shapes/runner/verify.py
```

The CLI accepts only `--smoke` and 1–10 dev episodes. It freezes reference/random
validation 0–255 first, then runs one continuous engineering smoke. It cannot
select judging entropy, a development run, or the 200-episode cost projection.
The delivered smoke is eight episodes on seed 105051; its raw events and drives
are in `SMOKE.json`, labelled engineering-only and not development evidence.
Do not repeat already passing verification for unchanged code.

`protocol.py` contains pure bindings, calibration, template/hash and read-out
contracts; `qualification.py` imports the frozen C4 functions and adapts actual
601-frame driven histories and complete-state recovery futures. `evaluator.py`
creates fresh isolated copies on validation 0–127. `control.py` implements the
FIFO random growth control. `run.py` orchestrates continuous clocks, adaptation,
growth, snapshot admission, exposure and accounting. `readouts.py` pairs seed
units. `development.py` contains dormant future orchestration; calling it needs
the owner's authorization and completed review/dependency gates.

Medium defaults remain selectable via the original `Medium` API. Revision 5.1
uses `medium/design_0h.py:DesignMedium` with world-step sampling, carried site
history, historical partner eligibility, offset-aware coverage, undirected pair
cost, spiral placement, and B1/D1/D3 only. Native gain is inside every RK4 stage.
New v2 native snapshots retain options and gain; v1 snapshots remain readable.
Build identity is checked before native loading. Frozen C4 source and the exact
revision-5.1 design identity are checked before runner construction.

Aliasing is a warning screen, not an absence certificate. Driven qualification
does not establish autonomous persistence or internally maintained closure.
G5 is a copy-covariance numerical check. No efficiency, background, combination,
scientific acceptance, development verdict, or public-release claim is made.
