"""Development step 1 (0e): task headroom (teacher versus rush), fit and prequalify the learned pieces L and the conventional conditional policy J, the reference
distance for wire noise, and the cost of one closed-loop cell. Seeds 0-9 of the 0e development entropy. NOT a recorded run.

    ZE_CACHE=/tmp/ze_cache .venv/bin/python evidence/tactical_composition_demo/dev_0e/dev_step1_pieces.py
"""
import concurrent.futures as cf
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dev_common_e as D  # noqa: E402

E, T = D.E, D.T
SEEDS = range(10)
EPISODES = 200


def job(seed):
    t0 = time.time()
    A_tr, A_va = D.arrays(seed)
    idx = D.source(A_tr, seed)
    t1 = time.time()
    L = D.fit_L(A_tr, idx, seed)
    t2 = time.time()
    J = D.fit_J(A_tr, idx, seed)
    t3 = time.time()
    out = {'seed': seed, 'train_states': int(A_tr.n), 'val_states': int(A_va.n), 'seconds_data': t1-t0, 'seconds_fit_L': t2-t1, 'seconds_fit_J': t3-t2}
    rows = np.arange(A_va.n)
    oracle = E.AimOracle().choose(A_va)
    out['ref_distance_median_to_teacher_target'] = float(np.median(A_va.en[rows, oracle, 3]))
    for name, model in (('L', L), ('J', J)):
        aim, move = E.AimWired(model, name), E.MoveWired(model, name)
        a = E.joint3(aim.choose(A_va), E.MoveOracle().step(A_va, A_va.REL[rows, aim.choose(A_va)]), A_va)   # AIM alone (oracle MOVE on its choice)
        m = E.move_alone(move, A_va)                                                                    # MOVE alone (told the teacher's target)
        full = E.joint3(*E.Assembly(aim, move).act(A_va, np.random.default_rng(0))[:2], A_va)
        out[name] = {'aim_admissible': a['a_target_admissible'], 'n_unique_best': a['n_unique_best'], 'move_alone': m['a_joint'],
                     'move_hold': m['a_hold'], 'move_approach': m['a_approach'], 'move_backoff': m['a_backoff'],
                     'n_hold': m['n_hold'], 'n_approach': m['n_approach'], 'n_backoff': m['n_backoff'], 'joint': full['a_joint'], 'macro': full['a_macro'],
                     'n_params': int(model.n_params)}
    t4 = time.time()
    for opp in ('rush', 'kiter'):
        for pname, make in (('teacher', lambda rng: T.teacher_policy), ('rush', lambda rng: T.rush_policy)):
            out['score_%s_%s' % (pname, opp)] = E.play_cell(make, opp, D.ENTROPY, seed, EPISODES)
    t5 = time.time()
    LL = E.Assembly(E.AimWired(L, 'L'), E.MoveWired(L, 'L'))
    out['score_LL_rush'] = E.play_cell(LL.policy, 'rush', D.ENTROPY, seed, EPISODES)
    out.update({'seconds_fixed_state_metrics': t4-t3, 'seconds_reference_cells': t5-t4, 'seconds_one_learned_cell': time.time()-t5, 'seconds_total': time.time()-t0})
    return out


def main():
    started = time.time()
    with cf.ProcessPoolExecutor(max_workers=8, mp_context=mp.get_context('spawn')) as pool:
        rows = list(pool.map(job, SEEDS))
    W = lambda r, p: np.mean([r['score_%s_%s' % (p, o)]['score'] for o in ('rush', 'kiter')])
    D_ = np.array([W(r, 'teacher')-W(r, 'rush') for r in rows])
    per_opp = {o: np.array([r['score_teacher_%s' % o]['score']-r['score_rush_%s' % o]['score'] for r in rows]) for o in ('rush', 'kiter')}
    summary = {'headroom_D_median': float(np.median(D_)), 'headroom_D_min': float(D_.min()), 'headroom_by_opponent_median': {o: float(np.median(v)) for o, v in per_opp.items()},
               'headroom_exact_95': E.median_interval(D_, 0.05)[:2], 'ref_distance': float(np.median([r['ref_distance_median_to_teacher_target'] for r in rows]))}
    for name in ('L', 'J'):
        summary[name] = {k: float(np.mean([r[name][k] for r in rows])) for k in rows[0][name]}
        summary[name]['min_unique_best'] = int(min(r[name]['n_unique_best'] for r in rows))
        summary[name]['min_backoff_states'] = int(min(r[name]['n_backoff'] for r in rows))
    summary['seconds'] = {k: float(np.mean([r[k] for r in rows])) for k in rows[0] if k.startswith('seconds')}
    summary['LL_rush_score_mean'] = float(np.mean([r['score_LL_rush']['score'] for r in rows]))
    summary['wall_seconds'] = round(time.time()-started, 1)
    out = {'note': '0e development step 1; seeds 0-9; %d episodes per opponent per cell' % EPISODES, 'summary': summary, 'rows': rows}
    (Path(__file__).resolve().parent/'step1_results.json').write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(summary, indent=1, default=float))


if __name__ == '__main__':
    main()
