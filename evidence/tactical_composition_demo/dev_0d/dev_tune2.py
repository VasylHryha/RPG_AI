"""Development step 2b: the one registered grid extension (PROPOSAL_0D.md section 2: a tuned value on the grid boundary extends the grid once, extra trials added to the
budget). Round 1 (tuned.json) put values on the boundary for every family. Round 2: 12 more settings, the same for every family, drawn uniformly from the extended
grid points that were not in the original grid; selection is over all 24 settings. After this round a boundary value is accepted and reported. Not a recorded run.
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
import dev_tune as R1  # noqa: E402

EXT = {'hidden': (4, 8, 16, 32, 64), 'lr': (0.0003, 0.001, 0.003, 0.01, 0.03), 'wd': (0.0, 1e-4, 1e-3, 1e-2), 'steps': (2000, 4000, 8000, 16000, 32000)}


def main():
    first = json.loads((Path(__file__).resolve().parent/'tuned.json').read_text())
    old = first['trials']
    ext = [dict(zip(EXT, v)) for v in itertools.product(*EXT.values())]
    new_points = [p for p in ext if p not in old and not all(p[k] in D.Z.GRID[k] for k in D.Z.GRID)]
    pick = D.stream(D.ENTROPY, 6).choice(len(new_points), R1.TRIALS, replace=False)
    round2 = [new_points[i] for i in sorted(pick)]
    started = time.time()
    with cf.ProcessPoolExecutor(max_workers=8, mp_context=mp.get_context('spawn')) as pool:
        jobs = [(f, R1.TRIALS+t, hp, s) for f in R1.FAMILIES for t, hp in enumerate(round2) for s in R1.TUNE_SEEDS]
        rows2 = list(pool.map(R1.job, jobs, chunksize=1))
    rows = first['rows']+rows2
    trials = old+round2
    chosen, table = {}, {}
    for f in R1.FAMILIES:
        scored = []
        for t in range(len(trials)):
            rr = [r for r in rows if r['family'] == f and r['trial'] == t]
            scored.append((-float(np.mean([r['a_joint'] for r in rr])), rr[0]['n_params'], t))
        scored.sort()
        best = scored[0][2]
        hp = trials[best]
        chosen[f] = {'trial': best, 'hp': hp, 'objective': -scored[0][0], 'n_params': scored[0][1], 'trials_in_budget': len(trials),
                     'on_extended_grid_boundary': [k for k, v in hp.items() if v in (min(EXT[k]), max(EXT[k])) and not (k == 'wd' and v == 0.0)],
                     'runner_up_objectives': [round(-s[0], 4) for s in scored[1:4]]}
        table[f] = [{'trial': t, 'hp': trials[t], 'mean_a_joint': float(np.mean([r['a_joint'] for r in rows if r['family'] == f and r['trial'] == t]))} for t in range(len(trials))]
    f_star = 'F2' if chosen['F2']['objective'] > chosen['F1']['objective'] else 'F1'
    out = {'note': 'development tuning, round 1 + one extension round (24 settings per family, same for every family); seeds 0-4; objective mean validation a_joint',
           'trials': trials, 'round2_trials': round2, 'chosen': chosen, 'comparator_F_star': f_star, 'table': table, 'seconds_round2': round(time.time()-started, 1), 'rows': rows}
    (Path(__file__).resolve().parent/'tuned2.json').write_text(json.dumps(out, indent=1, default=float))
    for f in R1.FAMILIES:
        print(f, chosen[f]['hp'], 'objective %.4f' % chosen[f]['objective'], 'params', chosen[f]['n_params'], 'boundary', chosen[f]['on_extended_grid_boundary'], 'next', chosen[f]['runner_up_objectives'])
    print('F* =', f_star, '| round 2 seconds', out['seconds_round2'])


if __name__ == '__main__':
    main()
