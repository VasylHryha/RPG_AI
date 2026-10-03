"""Re-run seed 0 of the cost run (dev_0d/cost_run) under the REGISTERED code and compare every stored value (provenance of the cost-run claim; the cost run recorded no file hashes).
Writes dev_0d/COST_SEED_REPRODUCTION.json. Not a recorded run.

    .venv/bin/python evidence/tactical_composition_demo/dev_0d/dev_cost_repro.py
"""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import zd_run as R  # noqa: E402
from tcd_common import fileio  # noqa: E402


def main():
    summary = json.loads((HERE/'cost_run'/'SUMMARY.json').read_text())
    spec = json.loads((HERE/'cost_spec.json').read_text())
    cfg = {k: v for k, v in summary['config'].items() if k != 'run_dir'}
    stored = fileio.jsonable(json.loads((HERE/'cost_run'/'seeds'/'seed_00.json').read_text()))
    started = time.time()
    fresh = fileio.jsonable(R.run_seed(cfg, spec['smoke_entropy'], 0))
    volatile = lambda k: k == 'seconds' or k.startswith(('fit_seconds', 'score_seconds'))
    keys = [k for k in sorted(set(stored)|set(fresh)) if not volatile(k)]
    differs = [k for k in keys if stored.get(k) != fresh.get(k)]
    git = lambda *a: subprocess.run(['git', *a], cwd=HERE, capture_output=True, text=True).stdout.strip()
    out = {'keys_compared': len(keys), 'identical': not differs, 'differing_keys': differs[:20], 'seconds': round(time.time()-started, 1),
           'provenance': {'git_head': git('rev-parse', 'HEAD'), 'zd_run_sha256': hashlib.sha256((HERE.parent/'zd_run.py').read_bytes()).hexdigest(),
                          'zd_models_sha256': hashlib.sha256((HERE.parent/'zd_models.py').read_bytes()).hexdigest()}}
    fileio.write_json(HERE/'COST_SEED_REPRODUCTION.json', out)
    print(out)
    return 0 if not differs else 1


if __name__ == '__main__':
    sys.exit(main())
