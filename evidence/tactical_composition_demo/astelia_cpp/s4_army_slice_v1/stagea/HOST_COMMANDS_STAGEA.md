# Exact host sequence

Run from `/Users/new/RiderProjects/ai_RPG_test`. No sandbox fights/training are authorized. Build and focused checks are measured here; fight/training estimates remain planning values until the bounded samples replace them. A0 rev2 measured 7.27–8.00 seconds per full-150-second script equivalent; Stage A recording/native network overhead is still unmeasured. Stop on a refused projection or gate; do not bypass it. Repeat a failed invocation to resume completed fights/epochs; do not repeat passing tests, samples or looks for unchanged code. After source changes rebuild and use a prospectively new local dataset/budget directory rather than editing old receipts.

```sh
cd /Users/new/RiderProjects/ai_RPG_test
export STAGEA=evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stagea
export STAGEA_PYTHON=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/_local/mlenv/bin/python
export PYTHONPYCACHEPREFIX="$STAGEA/_local/pycache"
```

1. Claude records the already approved training cap (seconds). Less than one second. This file is live operational authority, excluded from source hashes.

```sh
mkdir -p "$STAGEA/_local"
cat > "$STAGEA/_local/TRAIN_CAP.json" <<'JSON'
{"cap_seconds":10800,"approved_by":"owner","date":"2026-10-09","written_by":"Claude","scope":"Stage A concurrent training invocation"}
JSON
```

2. Admit the delivered build. If absent/stale, rebuild using `"$STAGEA_PYTHON" "$STAGEA/build.py"`. Build if the delivered host identity is absent/stale; measured 24.33 seconds here; allow 1–3 minutes on host. Then run the focused tests and **one** real-host integration test together at the end; about 20–120 seconds. The delivered nonfight tests passed (11 passed, 1 host-only skip in 3.06 seconds). With unchanged admitted sources, run only `test_stagea_host.py` once on host.

```sh
"$STAGEA_PYTHON" -c 'import sys; from pathlib import Path; sys.path.insert(0, str(Path(sys.argv[1]).resolve())); from collect import identity; print(identity()["binary_sha256"])' "$STAGEA"
STAGEA_HOST_TEST=1 "$STAGEA_PYTHON" -m pytest -q -x "$STAGEA/test_stagea_host.py"
```

3. Prepare fresh whole-fight collection, less than a minute; twenty training-only timing fights, initially allow 4–10 minutes; collect remaining O fights, initially 25–75 minutes. The measured full-150-second rate with 20% margin and LAB_CAP gates continuation. Both collection commands require process discovery. `run` reuses the twenty completed sample fights.

```sh
"$STAGEA_PYTHON" "$STAGEA/collect.py" prepare
"$STAGEA_PYTHON" "$STAGEA/collect.py" sample
"$STAGEA_PYTHON" "$STAGEA/collect.py" run
"$STAGEA_PYTHON" "$STAGEA/collect.py" audit
```

4. Audit initially budgets 15–60 minutes (disk-backed five-arm exact conflicts across full histories; twenty existing shards measure the remaining projection before proceeding). Do not train unless `_local/DECIDABILITY.json` says PASS. Measure twenty total optimizer steps plus state refresh/validation, initially allow 5–20 minutes. Seal budget before fitting; a refusal is a stop requiring prospective budget revision. No timing checkpoint is selected. Train concurrent arms: measured projection governs, <=1 hour each fit and <=3 hours whole invocation. Resume by repeating only `train.py run`.

```sh
"$STAGEA_PYTHON" "$STAGEA/train.py" measure --epochs 2 --windows 4
"$STAGEA_PYTHON" "$STAGEA/train.py" run
```

5. Full validation sequence export parity; initially allow 10–40 minutes, measure actual time. No combat steps. Required PASS before outcomes.

```sh
"$STAGEA_PYTHON" "$STAGEA/parity.py"
```

6. Prepare paired fresh outcomes, less than a minute. Run the 20-pair mechanism look, then 50 and 100 only if prior gates allow it. Seven arms across two panels means 280 / 700 / 1,400 cumulative fights. Initially allow 2–4 / 5–10 / 10–20 hours serial; actual fourteen-fight timing sample gates each invocation against LAB_CAP. These broad estimates are not authorization to exceed the cap. A refused complete-look projection must be reported to the owner; existing completed fights stay intact.

```sh
"$STAGEA_PYTHON" "$STAGEA/readout.py" prepare
"$STAGEA_PYTHON" "$STAGEA/readout.py" run --look 20
"$STAGEA_PYTHON" "$STAGEA/readout.py" run --look 50
"$STAGEA_PYTHON" "$STAGEA/readout.py" run --look 100
```
