"""Development step 2 (0e): qualify the conventional flat family F*-plus (PROPOSAL_0E.md section 3). A bounded frozen search: heads {mse, disc, perslot} x width
{32, 64, 128} x depth {2, 3}, lr 0.003, weight decay 1e-4, 32,000 steps, N = 3,000 source states (the primary N), development seeds 0-2. Selection on closed-loop
development score (both opponents, 100 episodes each), tie-break on the macro average of the disjoint hold/approach/back-off fidelity strata, then fewer parameters.
The gate (lower bound of the median gain over rush > 0.03, and positive per opponent) is applied to the selected candidate on seeds 3-9 in step 3. NOT a recorded run.

    ZE_CACHE=/tmp/ze_cache .venv/bin/python evidence/tactical_composition_demo/dev_0e/dev_step2_flatplus.py
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
import dev_common_e as D  # noqa: E402

E, F = D.E, D.F
SEEDS = (0, 1, 2)
EPISODES = 100
GRID = [{'head': h, 'hidden': w, 'depth': d, 'lr': 0.003, 'wd': 1e-4, 'steps': 32000} for h, w, d in itertools.product(('mse', 'disc', 'perslot'), (32, 64, 128), (2, 3))]


def job(args):
    k, hp, seed = args
    A_tr, A_va = D.arrays(seed)
    idx = D.source(A_tr, seed)
    t0 = time.time()
    m = F.FlatPlus(hp['head']).fit(A_tr, idx, hp, D.stream(D.ENTROPY, 3, seed, 100+k))
    fit_s = time.time()-t0
    j = E.joint3(*m.act(A_va), A_va)

    def make(rng, m=m):
        def policy(own, enemies):
            A = D.Z.Arrays({'own': own[None], 'enemies': enemies[None]})
            chosen, step = m.act(A)
            return step[0], int(chosen[0]), False
        return policy
    t1 = time.time()
    sc = {o: E.play_cell(make, o, D.ENTROPY, seed, EPISODES)['score'] for o in ('rush', 'kiter')}
    return {'k': k, 'hp': hp, 'seed': seed, 'a_joint': j['a_joint'], 'macro': j['a_macro'], 'hold': j['a_hold'], 'approach': j['a_approach'], 'backoff': j['a_backoff'],
            'score_rush': sc['rush'], 'score_kiter': sc['kiter'], 'score': (sc['rush']+sc['kiter'])/2, 'n_params': m.n_params, 'fit_seconds': fit_s, 'play_seconds': time.time()-t1}


def main():
    started = time.time()
    step1 = json.loads((Path(__file__).resolve().parent/'step1_results.json').read_text())
    rush_ref = {r['seed']: np.mean([r['score_rush_rush']['score'], r['score_rush_kiter']['score']]) for r in step1['rows']}
    with cf.ProcessPoolExecutor(max_workers=8, mp_context=mp.get_context('spawn')) as pool:
        rows = list(pool.map(job, [(k, hp, s) for k, hp in enumerate(GRID) for s in SEEDS], chunksize=1))
    table = []
    for k, hp in enumerate(GRID):
        rr = [r for r in rows if r['k'] == k]
        table.append({'k': k, 'hp': hp, 'score': float(np.mean([r['score'] for r in rr])), 'macro': float(np.mean([r['macro'] for r in rr])),
                      'a_joint': float(np.mean([r['a_joint'] for r in rr])), 'backoff': float(np.mean([r['backoff'] for r in rr])),
                      'gain_over_rush': float(np.mean([r['score']-rush_ref[r['seed']] for r in rr])), 'n_params': rr[0]['n_params'],
                      'fit_seconds': float(np.mean([r['fit_seconds'] for r in rr]))})
    order = sorted(table, key=lambda t: (-round(t['score'], 6), -t['macro'], t['n_params']))
    best = order[0]
    out = {'note': '0e development step 2: F*-plus search; seeds 0-2; %d episodes per opponent; selection on closed-loop score, tie-break macro strata, then parameters' % EPISODES,
           'selected': best, 'table': order, 'rows': rows, 'wall_seconds': round(time.time()-started, 1)}
    (Path(__file__).resolve().parent/'step2_results.json').write_text(json.dumps(out, indent=1, default=float))
    for t in order:
        print('%-7s w%3d d%d | score %.3f gain/rush %+.3f | a_joint %.3f macro %.3f backoff %.3f | params %5d fit %.0fs' % (
            t['hp']['head'], t['hp']['hidden'], t['hp']['depth'], t['score'], t['gain_over_rush'], t['a_joint'], t['macro'], t['backoff'], t['n_params'], t['fit_seconds']))
    print('selected', best['hp'], '| wall', out['wall_seconds'])


if __name__ == '__main__':
    main()
