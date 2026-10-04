"""Development probe (NOT registered, NOT a recorded run; affects no verdict): does the flat model climb with more capacity, data and training?
Flat F1-type models (squared-error step head) on the development validation pools of seeds 5-7, hidden 64 and 128, N up to 60,000 source states, up to 64,000 steps.
Written after the 2026-10-04 recheck raised the concern that the tuned flat baseline (357 parameters, flat from N=1,000 to 9,000) may be too weak.
"""
import concurrent.futures as cf
import itertools
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dev_common as D  # noqa: E402

SEEDS = (5, 6, 7)
CONFIGS = [(hidden, n, steps) for hidden in (64, 128) for n, steps in ((3000, 32000), (9000, 32000), (27000, 64000), (60000, 64000))]


def job(args):
    hidden, n, steps, seed = args
    hp = {'hidden': hidden, 'lr': 0.003, 'wd': 1e-4, 'steps': steps}
    r = D.fit_and_score('F1', hp, seed, n_states=n)
    return {'hidden': hidden, 'n': n, 'steps': steps, 'seed': seed, 'a_joint': r['a_joint'], 'aim_alone': r['aim_alone_admissible'], 'move_alone': r['move_alone_joint_on_teacher_target'],
            'step_angle_median_moving_deg': r['step_angle_median_moving_deg'], 'backoff': r['strata'].get('a_joint_stratum_backoff'), 'n_params': r['n_params'], 'fit_seconds': r['fit_seconds']}


def main():
    started = time.time()
    with cf.ProcessPoolExecutor(max_workers=8, mp_context=mp.get_context('spawn')) as pool:
        rows = list(pool.map(job, [(h, n, s, seed) for (h, n, s) in CONFIGS for seed in SEEDS], chunksize=1))
    out = {'note': 'flat capacity/data probe, development seeds 5-7, F1-type, lr 0.003, wd 1e-4; compare registered tuned F1 0.541 and C 0.957 on the same seeds (gates_results.json)', 'rows': rows, 'seconds': round(time.time()-started, 1)}
    (Path(__file__).resolve().parent/'probe_flat_capacity_results.json').write_text(json.dumps(out, indent=1, default=float))
    for (h, n, s) in CONFIGS:
        rr = [r for r in rows if r['hidden'] == h and r['n'] == n]
        m = lambda k: np.mean([r[k] for r in rr if r[k] is not None])
        print('hidden %3d N %5d steps %5d | a_joint %.3f | aim alone %.3f | move alone %.3f | angle %.1f | backoff %.3f | params %d' % (h, n, s, m('a_joint'), m('aim_alone'), m('move_alone'), m('step_angle_median_moving_deg'), m('backoff'), rr[0]['n_params']))
    print('seconds', out['seconds'])


if __name__ == '__main__':
    main()
