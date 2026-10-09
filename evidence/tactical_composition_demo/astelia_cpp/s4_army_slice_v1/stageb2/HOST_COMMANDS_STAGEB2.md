# B2 decision 0040 host commands (prepared, not executed)

No training or fights were run during implementation. Use the pinned host Python. OWNER_APPROVALS.json is already the owner-approved authority (maximum/live training 16200 s; coverage 1800 s). The legacy Claude cap command only displays this config. Do not change the declared readiness rule after outcomes.

Before running: finish any current Stage B/B2 job, keep its receipts unchanged, archive the existing B2 `_local/react_on` directory under a unique revision name, then prepare the fresh root. The five-arm code changes intentionally refuse old three-arm indexes/budgets/checkpoints. Stage A/B/rev2 remain read-only. A process lock continues to prevent concurrent admitted work.

```sh
cd /Users/new/RiderProjects/ai_RPG_test
B2=evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stageb2
ML=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/_local/mlenv/bin/python
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 B2_VARIANT=react_on
# Once, only after old jobs finish; preserves the complete previous revision.
mv "$B2/_local/react_on" "$B2/_local/react_on_pre0040_$(date +%Y%m%dT%H%M%S)"
# Build: expected 1–3 minutes, no fights.
nice -n 15 "$ML" "$B2/build.py"
# Bind the completed Stage B parent architecture comparators, read-only.
nice -n 15 "$ML" "$B2/baseline.py" --round 1
nice -n 15 "$ML" "$B2/train.py" prepare --round 0
# Coverage: no optimization/fights; first-sample projection, at most 1800 s.
nice -n 15 "$ML" "$B2/coverage.py" --round 0
# Measure: real small optimization samples, <=20 steps; expected 5–20 min,
# unmeasured. Refuses if measured five-arm lane sums +20% exceed the cap.
nice -n 15 "$ML" "$B2/train.py" measure --round 0
# Train: ten matched epochs, sequential sharing of <=4 measured slots,
# bounded by the live 16200 s maximum. Actual projection is TRAIN_BUDGET.json.
nice -n 15 "$ML" "$B2/train.py" run --round 0
# Parity: full validation sequences, no fights; expected minutes to tens of
# minutes, unmeasured. Includes validation candidate-pick counts.
nice -n 15 "$ML" "$B2/parity_run.py" --round 0
```

Declare OWNER_APPROVALS.json dagger.rounds (5–10, default 5) and any optional measured DART noise **before** first dagger prepare seals the schedule. All rounds keep the same schedule and checkpoint identities. Every next round requires the prior paired real-fight look 20, not just collection statistics. Each DAgger collection is 110 fights; each react-on look 20 is 400 fights (five B2, three parent network-only, O/T ×40 pairs). Final look 50 adds 600 fights. Cost is unmeasured; each invocation measures real sample fights and refuses a projection over its configured cap. It retains valid completions and never silently shrinks a look.

```sh
# Repeat for rounds 1..5 (or the prospectively declared 6..10), stopping if
# any command refuses. This loop never changes the schedule after outcomes.
for ROUND in 1 2 3 4 5; do
  nice -n 15 "$ML" "$B2/dagger.py" prepare --round "$ROUND" || break
  nice -n 15 "$ML" "$B2/dagger.py" run --round "$ROUND" || break
  nice -n 15 "$ML" "$B2/train.py" prepare --round "$ROUND" || break
  nice -n 15 "$ML" "$B2/coverage.py" --round "$ROUND" || break
  nice -n 15 "$ML" "$B2/train.py" measure --round "$ROUND" || break
  nice -n 15 "$ML" "$B2/train.py" run --round "$ROUND" || break
  nice -n 15 "$ML" "$B2/parity_run.py" --round "$ROUND" || break
  nice -n 15 "$ML" "$B2/baseline_parity.py" --round "$ROUND" || break
  nice -n 15 "$ML" "$B2/readout_run.py" prepare --round "$ROUND" || break
  nice -n 15 "$ML" "$B2/readout_run.py" run --round "$ROUND" --look 20 || break
done
# Only after the final scheduled round's complete look 20:
nice -n 15 "$ML" "$B2/readout_run.py" run --round 5 --look 50
```

The later learned-dodge variant still requires its matched frozen parent look 50; enable_dodge.py validates that separate eligibility. It gets its own fresh `_local/learned_dodge` root and the same declared config authority. No learned-dodge fight is authorized or run by this delivery.

Focused tests for this batch use synthetic geometry/native inference and syntax-only engine seams; they run no optimizer or fights. A production build and real host coverage/parity/readouts are separate commands above.
