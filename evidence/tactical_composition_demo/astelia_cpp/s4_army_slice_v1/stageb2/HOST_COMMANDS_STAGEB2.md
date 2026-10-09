# Host commands (prepared, not executed)

Use after the running Stage B finishes and its outcomes show a need for B2. Keep this revision unchanged during admitted jobs. Commands below write only B2 output paths; external modules are read with bytecode disabled. Training/fights were not run in this delivery.

```sh
cd /Users/new/RiderProjects/ai_RPG_test
B2=evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stageb2
ML=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/_local/mlenv/bin/python
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export B2_VARIANT=react_on
# Optional N1h: export B2_N1H=1 before ANY preparation, consistently per revision.
```

Only if the owner approves a **three-hour maximum per B2 training invocation**, the owner can execute this authority-record command. Executing it is the approval; the agent has not executed it or reused Stage B's authorization. A shorter cap is permitted; every prospective timing checks the live cap. Claude writes the actual TRAIN_CAP in the next command.

```sh
"$ML" -c 'import json,pathlib; p=pathlib.Path("evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stageb2/_local/react_on/CAP_AUTHORITY.json"); p.parent.mkdir(parents=True,exist_ok=True); p.open("x").write(json.dumps(dict(cap_seconds=10800,approved_by="owner",date="2026-10-09",approval_reference="Owner executed the B2 three-hour cap authority command"))+"\n")'
nice -n 15 "$ML" "$B2/claude_train_cap.py"
```

The Claude command needs an authenticated CLI; expected under one minute. If logged out it refuses; no authorship is impersonated. Existing cap files are preserved, including live owner reductions.

```sh
# Build only after the shared Stage B job lock is free. Expected 1–3 minutes.
nice -n 15 "$ML" "$B2/build.py"
# Bind the completed Stage B checkpoint used as network-only comparator.
# Use --round 0 if the owner chooses round-0 Stage B as the baseline.
nice -n 15 "$ML" "$B2/baseline.py" --round 1
# Prepare round 0 from existing sealed data; expected seconds.
nice -n 15 "$ML" "$B2/train.py" prepare --round 0
# Whole-trajectory candidate coverage; no fights/optimization.
# Time is unknown until first-fight projection, bounded by the live cap.
nice -n 15 "$ML" "$B2/coverage.py" --round 0
# Real timing samples: one complete training prefix + up to four windows/arm.
# This DOES execute small training samples; expected 5–20 minutes, unmeasured.
nice -n 15 "$ML" "$B2/train.py" measure --round 0
# Exact expected time: _local/react_on/round0/TRAIN_BUDGET.json projected_seconds.
# Run or resume ten epochs, at most live TRAIN_CAP (initially 10800 seconds).
nice -n 15 "$ML" "$B2/train.py" run --round 0
# Complete validation sequences, native/Python heads and calibrated fire decoder.
# Expected minutes to tens of minutes, unmeasured; live cap enforced.
nice -n 15 "$ML" "$B2/parity_run.py" --round 0
# Full-fight DAgger: 22 fresh fights per arm, student-only actions, O shadow labels.
nice -n 15 "$ML" "$B2/dagger.py" prepare --round 1
nice -n 15 "$ML" "$B2/dagger.py" run --round 1
# Aggregate only each student's own occupancy; coverage then measured refit.
nice -n 15 "$ML" "$B2/train.py" prepare --round 1
nice -n 15 "$ML" "$B2/coverage.py" --round 1
nice -n 15 "$ML" "$B2/train.py" measure --round 1
nice -n 15 "$ML" "$B2/train.py" run --round 1
nice -n 15 "$ML" "$B2/parity_run.py" --round 1
# Zero-combat baseline bridge, all validation sequences; expected minutes,
# unmeasured. Required before same paired fights compare network-only exports.
nice -n 15 "$ML" "$B2/baseline_parity.py" --round 1
nice -n 15 "$ML" "$B2/readout_run.py" prepare --round 1
nice -n 15 "$ML" "$B2/readout_run.py" run --round 1 --look 20
nice -n 15 "$ML" "$B2/readout_run.py" run --round 1 --look 50
```

DAgger has 66 fights for the three core arms: a rough inherited Stage A/B reference is 20 s per network fight, about 22 minutes serial before B2 overhead/shadow recording. Look 20 has 320 fights (three B2, three network-only, O/T ×40 pairs): rough inherited arithmetic 85 minutes. Look 50 has 800 total fights, 480 additional after 20: about 128 minutes additional at 16 s mean. These are **unmeasured expectations**, not B2 speed results; candidate computation and recording may raise them substantially. Each command measures actual sample fights and refuses an over-cap tail, retaining valid completions. It does not reduce the declared look or epoch budget. Collection/readout use the existing live LAB_CAP, whose approved scope must cover the B2 host work. If it is too short, the owner must set the appropriate cap before execution. No host performance or safety qualification is claimed here.

The learned-dodge arm is later work, after non-harmful react-on look 50 with actual wins in both panels for all core arms. Enable verifies the successful look/ledger/completions, calibrated fit, export, checkpoint and parity chain, then binds matched parent checkpoints; hashing archived raw files can take minutes. This is a behavioural eligibility gate, not teacher acceptance.

```sh
nice -n 15 "$ML" "$B2/enable_dodge.py" --round 1
export B2_VARIANT=learned_dodge
# Owner executes this only when approving the later three-hour invocation cap.
"$ML" -c 'import json,pathlib; p=pathlib.Path("evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stageb2/_local/learned_dodge/CAP_AUTHORITY.json"); p.parent.mkdir(parents=True,exist_ok=True); p.open("x").write(json.dumps(dict(cap_seconds=10800,approved_by="owner",date="2026-10-09",approval_reference="Owner executed the learned-dodge three-hour authority command"))+"\n")'
nice -n 15 "$ML" "$B2/claude_train_cap.py"
nice -n 15 "$ML" "$B2/baseline.py" --round 1
nice -n 15 "$ML" "$B2/train.py" prepare --round 0
nice -n 15 "$ML" "$B2/coverage.py" --round 0
nice -n 15 "$ML" "$B2/train.py" measure --round 0
nice -n 15 "$ML" "$B2/train.py" run --round 0
nice -n 15 "$ML" "$B2/parity_run.py" --round 0
nice -n 15 "$ML" "$B2/dagger.py" prepare --round 1
nice -n 15 "$ML" "$B2/dagger.py" run --round 1
nice -n 15 "$ML" "$B2/train.py" prepare --round 1
nice -n 15 "$ML" "$B2/coverage.py" --round 1
nice -n 15 "$ML" "$B2/train.py" measure --round 1
nice -n 15 "$ML" "$B2/train.py" run --round 1
nice -n 15 "$ML" "$B2/parity_run.py" --round 1
nice -n 15 "$ML" "$B2/baseline_parity.py" --round 1
nice -n 15 "$ML" "$B2/readout_run.py" prepare --round 1
nice -n 15 "$ML" "$B2/readout_run.py" run --round 1 --look 20
nice -n 15 "$ML" "$B2/readout_run.py" run --round 1 --look 50
```

Learned-dodge look 20 has 440 fights, about 120–150 minutes by inherited speed arithmetic; look 50 adds 660 fights, roughly 3–4 hours before B2 overhead. Actual sample-based projection and live LAB_CAP decide admission. Reports compare with the frozen matched react-on B2 parent, network-only Stage B and O/T on exactly the same pairs. The ON parent's training budget is reported separately from additional OFF refitting; this is a warm-start ablation, not equal-total-training compute.

Focused tests, when changed code requires them (no fights/training):

```sh
B2_VARIANT=react_on nice -n 15 "$ML" -m pytest -q -x -o cache_dir="$B2/_local/pytest_cache" "$B2/test_stageb2.py"
```

Expected under 30 seconds: one small tool executable, one no-combat replay executable, four architectures on three synthetic ticks, mathematical/loss/provenance/resume checks plus adversarial padding, empty aim, malformed twin inputs, synthetic parent look/checkpoint binding and nonzero warm-start law fixtures. These tests do not acquire the heavy-job lock or run the current Stage B binary. The no-combat executable has no fight entrypoint. PyTorch uses one thread. Full production engine build, arbitration and performance remain later host checks.
