"""Development step 3: adequacy gates, the spread of every contrast, and the seed count S (PROPOSAL_0D.md sections 4-5), on 10 development seeds that tuning never saw
(seeds 5-14), at the tuned settings of tuned2.json (F0 at its recorded recipe). Not a recorded run; no verdict is computed from these seeds.
"""
import concurrent.futures as cf
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dev_common as D  # noqa: E402

SEEDS = range(5, 15)
NAMES = ('F0', 'F1', 'F2', 'C', 'S1')
RECORDED_F0 = {'hidden': 15, 'lr': 0.003, 'wd': 0.0, 'steps': 8000}


def job(args):
    name, hp, seed = args
    return D.fit_and_score(name, hp, seed)


def main():
    tuned = json.loads((Path(__file__).resolve().parent/'tuned2.json').read_text())
    hps = {n: tuned['chosen'][n]['hp'] for n in ('F1', 'F2', 'C', 'S1')}
    hps['F0'] = RECORDED_F0
    f_star = tuned['comparator_F_star']
    started = time.time()
    with cf.ProcessPoolExecutor(max_workers=8, mp_context=mp.get_context('spawn')) as pool:
        list(pool.map(D.make_data, SEEDS))
        rows = list(pool.map(job, [(n, hps[n], s) for s in SEEDS for n in NAMES], chunksize=1))
    A = {n: np.array([next(r for r in rows if r['model'] == n and r['seed'] == s)['a_joint'] for s in SEEDS]) for n in NAMES}
    contrasts = {'E0': A['C']-A['F0'], 'E1': A['C']-A[f_star], 'E2': A['C']-A['S1'], 'E3': A['S1']-A[f_star], 'T1': A[f_star]-A['F0'], 'T2': A['F2']-A['F1']}
    sd = {k: float(np.std(v, ddof=1)) for k, v in contrasts.items()}
    worst = max(sd.values())
    seeds_needed = next((S for S in (30, 45, 60) if 1.96*1.253*worst/np.sqrt(S) <= 0.015), 60)
    reachable = 1.96*1.253*worst/np.sqrt(seeds_needed) <= 0.015
    by = lambda n, k: np.mean([r[k] for r in rows if r['model'] == n])
    gates = {'C_a_joint_mean': float(A['C'].mean()), 'C_adequate_ge_0.90': bool(A['C'].mean() >= 0.90),
             'S1_scorer_admissible_mean': float(by('S1', 'aim_alone_admissible')), 'S1_step_success_moving_mean': float(np.mean([r['strata'].get('a_joint_stratum_moving') for r in rows if r['model'] == 'S1' and r['strata'].get('a_joint_stratum_moving') is not None])),
             'strata_adequate_share': {n: float(np.mean([all(r['strata'].get('a_joint_stratum_'+s) is not None for s in ('hold', 'moving', 'backoff')) for r in rows if r['model'] == n])) for n in NAMES}}
    gates['S1_adequate'] = bool(gates['S1_scorer_admissible_mean'] >= 0.85 and gates['S1_step_success_moving_mean'] >= 0.85)
    out = {'note': 'development gates and precision; seeds 5-14; tuned settings from tuned2.json', 'hps': hps, 'F_star': f_star, 'a_joint_by_model': {n: A[n].tolist() for n in NAMES},
           'contrast_medians': {k: float(np.median(v)) for k, v in contrasts.items()}, 'contrast_sd': sd, 'max_sd': worst, 'seeds_needed_S': seeds_needed,
           'equivalence_reachable_at_S': bool(reachable), 'gates': gates, 'per_model': {n: {'n_params': next(r['n_params'] for r in rows if r['model'] == n),
           'fit_seconds_mean': float(by(n, 'fit_seconds')), 'connection_gap_mean': float(by(n, 'connection_gap')), 'aim_alone_mean': float(by(n, 'aim_alone_admissible')),
           'move_alone_mean': float(by(n, 'move_alone_joint_on_teacher_target'))} for n in NAMES}, 'seconds': round(time.time()-started, 1), 'rows': rows}
    (Path(__file__).resolve().parent/'gates_results.json').write_text(json.dumps(out, indent=1, default=float))
    for n in NAMES:
        print('%-3s a_joint median %.3f | aim alone %.3f | move alone %.3f | gap %+.3f | fit %.1fs | params %d' % (
            n, np.median(A[n]), out['per_model'][n]['aim_alone_mean'], out['per_model'][n]['move_alone_mean'], out['per_model'][n]['connection_gap_mean'],
            out['per_model'][n]['fit_seconds_mean'], out['per_model'][n]['n_params']))
    print('contrast sd', {k: round(v, 4) for k, v in sd.items()})
    print('S =', seeds_needed, '| equivalence reachable:', reachable, '| gates', gates)


if __name__ == '__main__':
    main()
