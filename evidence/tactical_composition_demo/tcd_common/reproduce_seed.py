"""Re-run ONE seed of a recorded harness at the current HEAD and compare every stored number with the recorded per-seed file (determinism check).

    .venv/bin/python evidence/tactical_composition_demo/tcd_common/reproduce_seed.py stage0 0 change_r2 0

This is not a rerun of the recorded run and re-analyses nothing: it calls the harness's own `run_seed` for one seed on the recorded entropy and writes only
`SEED_REPRODUCTION.json` here. The run directories and the one-shot latch are not touched. Timing keys are excluded from the comparison.
"""
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '1')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tcd_common import PARENT, fileio  # noqa: E402

TARGETS = {'stage0': ('demo', 'SPEC.json', 'run'), 'change_r1': ('change', 'SPEC_CHANGE.json', 'run_change'), 'change_r2': ('change2', 'SPEC_CHANGE2.json', 'run_change2')}


def volatile(key):
    return key == 'seconds' or key.startswith('build_seconds') or key.startswith('build_') and key.split('_')[-1].isdigit()


def main(argv):
    out_path = Path(__file__).resolve().parent/'SEED_REPRODUCTION.json'
    results = json.loads(out_path.read_text()) if out_path.exists() else {}
    for name, seed in zip(argv[::2], argv[1::2]):
        module, spec_file, run_dir = TARGETS[name]
        harness = __import__(module)
        spec = json.loads((PARENT/spec_file).read_text())
        stored = json.loads((PARENT/run_dir/'seeds'/('seed_%02d.json' % int(seed))).read_text())
        started = time.time()
        fresh = fileio.jsonable(harness.run_seed(dict(spec['config']), spec['entropy'], int(seed)))
        stored, fresh = fileio.jsonable(stored), fileio.jsonable(fresh)
        keys = sorted(set(stored)|set(fresh))
        compared = [k for k in keys if not volatile(k)]
        differs = [k for k in compared if stored.get(k) != fresh.get(k)]
        results['%s_seed%s' % (name, seed)] = {'keys_compared': len(compared), 'keys_excluded_as_timing': len(keys)-len(compared), 'identical': not differs,
                                                'differing_keys': differs[:20], 'seconds': round(time.time()-started, 1)}
        print(name, seed, results['%s_seed%s' % (name, seed)])
    fileio.write_json(out_path, results)
    return 0 if all(r['identical'] for r in results.values()) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
