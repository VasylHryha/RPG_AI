#!/bin/bash
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
