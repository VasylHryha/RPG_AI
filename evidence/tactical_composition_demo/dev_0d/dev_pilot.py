"""Development pilot 1: every model at one default setting on a few development seeds. Checks the pipeline end to end, shows each model's pieces alone and connected,
and measures cost. NOT a recorded run; no bar is fixed from it.

    ZD_CACHE=/tmp/zd_cache .venv/bin/python evidence/tactical_composition_demo/dev_0d/dev_pilot.py 3
"""
import concurrent.futures as cf
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dev_common as D  # noqa: E402

DEFAULT = {'hidden': 16, 'lr': 0.003, 'wd': 0.0, 'steps': 8000}
NAMES = ('F0', 'F1', 'F2', 'C', 'S1')


def job(args):
    name, seed = args
    return D.fit_and_score(name, DEFAULT, seed)


def main(n_seeds):
    started = time.time()
    with cf.ProcessPoolExecutor(max_workers=8, mp_context=mp.get_context('spawn')) as pool:
        # build the data first (one job per seed), so fits do not race on the cache
        list(pool.map(D.make_data, range(n_seeds)))
        data_seconds = time.time()-started
        results = list(pool.map(job, [(n, s) for s in range(n_seeds) for n in NAMES]))
    out = {'note': 'development pilot 1; default setting %s; seeds 0..%d of DEV_SPEC entropy' % (DEFAULT, n_seeds-1), 'data_seconds': round(data_seconds, 1),
           'total_seconds': round(time.time()-started, 1), 'results': results}
    (Path(__file__).resolve().parent/'pilot1_results.json').write_text(json.dumps(out, indent=1, default=float))
    for n in NAMES:
        rows = [r for r in results if r['model'] == n]
        mean = lambda k: sum(r[k] for r in rows)/len(rows)
        print('%-3s a_joint %.3f | aim alone %.3f | move alone %.3f | indep %.3f | gap %+.3f | fit %.1fs | params %d' % (
            n, mean('a_joint'), mean('aim_alone_admissible'), mean('move_alone_joint_on_teacher_target'), mean('independent_prediction'), mean('connection_gap'),
            mean('fit_seconds'), rows[0]['n_params']))
    print('data %.0fs, total %.0fs' % (data_seconds, out['total_seconds']))


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
