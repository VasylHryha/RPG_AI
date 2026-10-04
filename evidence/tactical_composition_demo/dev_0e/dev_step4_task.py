"""Development step 4 (0e): qualify a task revision in which the AIM-to-MOVE connection can matter (tactics_e2.py; variants declared there before this ran).
Scripted policies only (no learning), development seeds 10-14, 200 episodes per opponent per cell, paired rosters.

Gates per variant (fixed before measurement): headroom = W(teacher) - W(rush) median > 0.15 and > 0.10 per opponent; AIM necessity = W(teacher) - W(nearest-enemy
targeting, teacher stepping) median > 0.05 and > 0.03 in at least 4 of 5 seeds; CONNECTION necessity = W(teacher) - W(teacher targeting, stepping toward the nearest
enemy's position) with the same rule; MOVE necessity = W(teacher) - W(teacher targeting, approach-only stepping) with the same rule.
Selection rule (fixed): among variants passing every gate, the one with the largest minimum of the three necessity medians; ties in declared order. NOT a recorded run.

    .venv/bin/python evidence/tactical_composition_demo/dev_0e/dev_step4_task.py
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tactics_e2 as T2  # noqa: E402

E, T = D.E, D.T
SEEDS = (10, 11, 12, 13, 14)
EPISODES = 200
HERE = Path(__file__).resolve().parent


def policies(variant):
    sc = T2.doctrine_scores(variant)

    def teacher(own, en):
        t = int(np.argmax(sc(own, en)))
        return T.teacher_move(en[t, 1:3], own[4]), t, False

    def nearest_aim(own, en):
        alive = T.alive_slots(en)
        t = int(alive[np.argmin(en[alive, 3])])
        return T.teacher_move(en[t, 1:3], own[4]), t, False

    def nearest_msg(own, en):
        t = int(np.argmax(sc(own, en)))
        alive = T.alive_slots(en)
        n = int(alive[np.argmin(en[alive, 3])])
        return T.teacher_move(en[n, 1:3], own[4]), t, False

    def approach(own, en):
        t = int(np.argmax(sc(own, en)))
        rel = en[t, 1:3]
        d = float(np.hypot(*rel))
        return (rel/d if d > 1e-9 else np.zeros(2)), t, False

    def old_aim(own, en):
        t = int(np.argmax(T.teacher_scores(own, en)))
        return T.teacher_move(en[t, 1:3], own[4]), t, False
    return {'teacher': teacher, 'rush': T.rush_policy, 'nearest_aim': nearest_aim, 'nearest_msg': nearest_msg, 'approach': approach, 'old_aim': old_aim}


def job(args):
    variant, seed = args
    pol = policies(variant)
    wf = T2.world_fn(variant)
    out = {'variant': variant, 'seed': seed}
    for name, p in pol.items():
        for opp in ('rush', 'kiter'):
            out['%s_%s' % (name, opp)] = E.play_cell(lambda rng, p=p: p, opp, D.ENTROPY, seed, EPISODES, world_fn=wf, mixes=T2.MIXES)
    return out


def main():
    started = time.time()
    with cf.ProcessPoolExecutor(max_workers=8, mp_context=mp.get_context('spawn')) as pool:
        rows = list(pool.map(job, [(v, s) for v in T2.VARIANTS for s in SEEDS], chunksize=1))
    W = lambda r, p: np.mean([r['%s_%s' % (p, o)]['score'] for o in ('rush', 'kiter')])
    report = {}
    for v in T2.VARIANTS:
        rr = [r for r in rows if r['variant'] == v]
        diff = lambda a, b: np.array([W(r, a)-W(r, b) for r in rr])
        head = diff('teacher', 'rush')
        per_opp = {o: float(np.median([r['teacher_%s' % o]['score']-r['rush_%s' % o]['score'] for r in rr])) for o in ('rush', 'kiter')}
        nec = {k: diff('teacher', k) for k in ('nearest_aim', 'nearest_msg', 'approach')}
        gates = {'headroom': bool(np.median(head) > 0.15 and min(per_opp.values()) > 0.10)}
        for k, x in nec.items():
            gates[k] = bool(np.median(x) > 0.05 and (x > 0.03).sum() >= 4)
        report[v] = {'scores': {p: float(np.median([W(r, p) for r in rr])) for p in policies(v)}, 'headroom_median': float(np.median(head)), 'headroom_by_opponent': per_opp,
                     'necessity_medians': {k: float(np.median(x)) for k, x in nec.items()}, 'necessity_per_seed': {k: x.tolist() for k, x in nec.items()},
                     'gates': gates, 'passes_all': all(gates.values()), 'min_necessity': float(min(np.median(x) for x in nec.values())),
                     'timeouts_teacher': int(sum(r['teacher_%s' % o]['timeout'] for r in rr for o in ('rush', 'kiter')))}
    passing = [v for v in T2.VARIANTS if report[v]['passes_all']]
    selected = max(passing, key=lambda v: (report[v]['min_necessity'], -list(T2.VARIANTS).index(v))) if passing else None
    out = {'note': '0e development step 4: task-revision gates; seeds 10-14; %d episodes per opponent' % EPISODES, 'report': report, 'selected': selected,
           'rows': rows, 'wall_seconds': round(time.time()-started, 1)}
    (HERE/'step4_results.json').write_text(json.dumps(out, indent=1, default=float))
    for v, r in report.items():
        print(v, 'scores', {k: round(x, 3) for k, x in r['scores'].items()})
        print('   headroom %.3f %s | necessity %s | gates %s' % (r['headroom_median'], {k: round(x, 3) for k, x in r['headroom_by_opponent'].items()},
                                                             {k: round(x, 3) for k, x in r['necessity_medians'].items()}, r['gates']))
    print('selected', selected, '| wall', out['wall_seconds'])


if __name__ == '__main__':
    main()
