# Exact current Stage A host sequence

Run from the repository root. The delivered build is admitted, and the 20 focused tests already passed once. Host tests were blocked by sandbox process discovery; run both once on the real host. The prospective slim recovery is already registered locally; its command checks it idempotently. The same 180 requests/timing tags remain sealed. Old evidence and old lab raw files must remain. Do not run prepare/recover-memory or rebuild unchanged sources. No living documents are pinned.

Initial planning times: host tests 1–5 minutes; sample 4–10 minutes; remaining collection 25–75 minutes; audit 15–60 minutes; train measurement 5–20 minutes. Actual measurements and live LAB_CAP/TRAIN_CAP govern each command. Collection stops if its full-duration measured maximum projects above 4 decimal GB or `bytes/fight * remaining * 2 + 5 decimal GB` exceeds actual free disk. The existing owner TRAIN_CAP remains operational authority; never overwrite a live reduction.

```sh
cd /Users/new/RiderProjects/ai_RPG_test
set -e
export STAGEA=evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stagea
export STAGEA_PYTHON=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/_local/mlenv/bin/python
export PYTHONPYCACHEPREFIX="$STAGEA/_local/pycache"
"$STAGEA_PYTHON" -c 'import sys; from pathlib import Path; sys.path.insert(0, str(Path(sys.argv[1]).resolve())); from collect import identity; print(identity()["binary_sha256"])' "$STAGEA"
STAGEA_HOST_TEST=1 "$STAGEA_PYTHON" -m pytest -q -x -s "$STAGEA/test_stagea_host.py" "$STAGEA/test_stagea_memory_host.py"
"$STAGEA_PYTHON" "$STAGEA/collect.py" recover-slim
"$STAGEA_PYTHON" "$STAGEA/collect.py" sample
"$STAGEA_PYTHON" "$STAGEA/collect.py" run
"$STAGEA_PYTHON" "$STAGEA/collect.py" audit
"$STAGEA_PYTHON" "$STAGEA/train.py" measure --epochs 2 --windows 4
```

A refusal stops the chain under `set -e`; do not bypass admission. Repeat only a failed command to resume completed fights/epochs. Collection run revalidates and reuses the twenty sample completions. A successful measurement seals the budget before fitting. Stop here if only measurement is intended. The subsequent admitted fit is `"$STAGEA_PYTHON" "$STAGEA/train.py" run`; full validation-sequence parity must pass before outcome prepare/run. The development outcome progression stays 20, then 50, then 100 only when prior gates permit it. No scientific acceptance is implied.
