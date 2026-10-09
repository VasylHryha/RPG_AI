# B2PROF host handoff

Wait for the existing Stage B job to finish. The sample measured all five arms below1.5s/step; it is TEST_ONLY. The full-cache estimate is4.80GB with limited headroom, and production measurement must establish admission under the unchanged caps.

The native build may take1–3 minutes. Fresh coverage and full-cache production measurement may take20–45 minutes at one thread, depending on the dataset and host load. Full training is a separate admitted run capped at4.5 hours; the current sample projects3.22h including the20% margin using four CPU lanes. Do not launch that run while Stage B is active. Stop at any failed command. Current checked ADMITTED budgets are reused; only stale budgets are archived. A current REFUSED identity stops for a revision fix. No caps or receipts should be edited to force admission.

```sh
set -e
cd /Users/new/RiderProjects/ai_RPG_test
B2="$PWD/evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stageb2"
ML="$PWD/evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/_local/mlenv/bin/python"
export B2_VARIANT=react_on PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
nice -n 15 "$ML" "$B2/build.py"
nice -n 15 "$ML" "$B2/baseline.py" --round 1
nice -n 15 "$ML" "$B2/train.py" prepare --round 0
nice -n 15 "$ML" "$B2/coverage.py" --round 0 --preserve-stale
nice -n 15 "$ML" - "$B2" <<'PY'
import datetime,sys,uuid
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import runtime as r
from train import checked
local=r.LOCAL/'round0';path=local/'TRAIN_BUDGET.json'
if path.exists():
    b=r.read(path)
    stale=(b['sources']!=r.sources() or b['index_sha256']!=r.sha(local/'INDEX.json')
           or b.get('coverage_sha256')!=r.sha(local/'COVERAGE.json')
           or b.get('variant')!=r.VARIANT)
    if stale:
        stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        backup=path.with_name('TRAIN_BUDGET.before_B2PROF.'+stamp+'.'+uuid.uuid4().hex+'.json')
        path.rename(backup)
        print('Preserved stale budget:',backup)
    else:
        current=checked(local)
        if current['status']!='ADMITTED':
            raise SystemExit('Current identity is REFUSED; fix the revision before another measurement.')
        print('Reusing current checked ADMITTED budget; measurement will not repeat.')
PY
nice -n 15 "$ML" "$B2/train.py" measure --round 0
# Continue only after the fresh production measurement returns ADMITTED.
nice -n 15 "$ML" "$B2/train.py" run --round 0
nice -n 15 "$ML" "$B2/parity_run.py" --round 0
```

Existing packet caches, refused budgets, checkpoints and coverage history are retained. The prepared cache has its own marker and authenticates metadata, row headers, content hashes, raw identity and relevant source files. Source changes make old budgets/coverage stale. The independent TEST_ONLY profiling sample did not write a production budget or bypass the production process gate. Do not repeat a successful measurement for the same production identity. Subsequent DAgger and look20/50 work follows the existing B2 pipeline and is outside this profiling handoff.
