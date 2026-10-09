# Hierarchical B2 host commands

The code/tests are ready; 4.5 h timing admission and <1.5 GiB RSS remain unmeasured.
The sandbox attempt refused at the required process gate, before optimization.
Run on the host when earlier jobs have finished. Stop on any failed gate. Keep
old receipts, caches and checkpoints; source locks reject their reuse as current
qualification. Current round0 INDEX is reusable (same five arms/data). No owner
caps change. Coverage must be refreshed because source/model identity changed.

```sh
cd /Users/new/RiderProjects/ai_RPG_test
B2=evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stageb2
ML=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/_local/mlenv/bin/python
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 B2_VARIANT=react_on
# Build: approximately 1–3 minutes; no fights.
nice -n 15 "$ML" "$B2/build.py"
nice -n 15 "$ML" "$B2/baseline.py" --round 1
nice -n 15 "$ML" "$B2/train.py" prepare --round 0
# Needed: preserve previous coverage, then recheck full strata + reachability.
nice -n 15 "$ML" "$B2/coverage.py" --round 0 --preserve-stale
# Optional TEST_ONLY sample, <=20 steps; fresh hier_speed_test receipt.
# Do not repeat this if it has already completed for this source revision.
nice -n 15 "$ML" "$B2/train.py" measure --round 0 --test-mode
# Real production measurement; refuse if lane projection x1.2 >16200 s.
# If a prior TRAIN_BUDGET exists from another revision, preserve that file
# under a unique name first; never edit its sources or admit it manually.
nice -n 15 "$ML" "$B2/train.py" measure --round 0
nice -n 15 "$ML" "$B2/train.py" run --round 0
nice -n 15 "$ML" "$B2/parity_run.py" --round 0
# Look20 requires the existing round1 DAgger/refit pipeline.
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
```

Measurement is expected to take 5–20 minutes, currently unqualified. Every optimizer step and live training memory check
enforces the exclusive 1.5 GiB worker RSS bound. The fresh test-only JSON is
_local/react_on/round0/hier_speed_test/SPEED_MEASURE_TEST.json; the real measured
projection is round0/TRAIN_BUDGET.json. Ten epochs × four windows × five arms
must fit 16200 s **after** multiplying the measured lane projection by1.2;
therefore the corresponding projection before margin must be <=13500 s.

The process gate and all owner caps remain binding. The 5–10 round declared
DAgger schedule and subsequent look50 are unchanged; this snippet reaches the
first look20, not final readiness/acceptance.
