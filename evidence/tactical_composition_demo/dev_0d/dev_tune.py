"""Development step 2: the registered tuning (PROPOSAL_0D.md section 2). 12 random trials from the shared grid, the SAME 12 settings for every family, 5 development
seeds per trial, objective = mean validation a_joint, ties by fewer parameters then lower trial index. F0 is not tuned. Not a recorded run.

    ZD_CACHE=/tmp/zd_cache .venv/bin/python evidence/tactical_composition_demo/dev_0d/dev_tune.py
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

FAMILIES = ('F1', 'F2', 'C', 'S1')
TUNE_SEEDS = range(0, 5)
TRIALS = 12


def trial_settings():
    grid = [dict(zip(D.Z.GRID, v)) for v in itertools.product(*D.Z.GRID.values())]
    pick = D.stream(D.ENTROPY, 5).choice(len(grid), TRIALS, replace=False)
    return [grid[i] for i in sorted(pick)]


def job(args):
    family, t, hp, seed = args
    r = D.fit_and_score(family, hp, seed)
    return {'family': family, 'trial': t, 'seed': seed, 'a_joint': r['a_joint'], 'n_params': r['n_params'], 'fit_seconds': r['fit_seconds'],
            'aim_alone_admissible': r['aim_alone_admissible'], 'move_alone': r['move_alone_joint_on_teacher_target']}


def main():
    trials = trial_settings()
    started = time.time()
    with cf.ProcessPoolExecutor(max_workers=8, mp_context=mp.get_context('spawn')) as pool:
        list(pool.map(D.make_data, TUNE_SEEDS))
        jobs = [(f, t, hp, s) for f in FAMILIES for t, hp in enumerate(trials) for s in TUNE_SEEDS]
        rows = list(pool.map(job, jobs, chunksize=1))
    chosen, table = {}, {}
    for f in FAMILIES:
        scored = []
        for t, hp in enumerate(trials):
            rr = [r for r in rows if r['family'] == f and r['trial'] == t]
            scored.append((-float(np.mean([r['a_joint'] for r in rr])), rr[0]['n_params'], t))
        scored.sort()
        best = scored[0][2]
        chosen[f] = {'trial': best, 'hp': trials[best], 'objective': -scored[0][0], 'n_params': scored[0][1]}
        table[f] = [{'trial': t, 'hp': trials[t], 'mean_a_joint': float(np.mean([r['a_joint'] for r in rows if r['family'] == f and r['trial'] == t])),
                     'sd_a_joint': float(np.std([r['a_joint'] for r in rows if r['family'] == f and r['trial'] == t]))} for t in range(TRIALS)]
        hp = trials[best]
        chosen[f]['on_grid_boundary'] = [k for k, v in hp.items() if v in (min(D.Z.GRID[k]), max(D.Z.GRID[k]))]
    f_star = 'F2' if chosen['F2']['objective'] > chosen['F1']['objective'] else 'F1'
    out = {'note': 'development tuning; same 12 settings for every family; seeds 0-4; objective mean validation a_joint', 'trials': trials, 'chosen': chosen,
           'comparator_F_star': f_star, 'table': table, 'seconds': round(time.time()-started, 1), 'rows': rows}
    (Path(__file__).resolve().parent/'tuned.json').write_text(json.dumps(out, indent=1, default=float))
    for f in FAMILIES:
        print(f, chosen[f]['hp'], 'objective %.3f' % chosen[f]['objective'], 'params', chosen[f]['n_params'], 'boundary', chosen[f]['on_grid_boundary'])
    print('F* =', f_star, '| seconds', out['seconds'])


if __name__ == '__main__':
    main()
