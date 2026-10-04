"""Development step 1 (0f): a first try of the bottom-up procedure on development seeds 0-4 of the 0f entropy (task V3). Per seed: train the pieces (AIM and MOVE as 0e's
L, HP on missing health), score all 88 assemblies on the selection roster (100 episodes per opponent), run the greedy procedure from the rush rule at margins
0.01/0.02/0.03, then score on the separate confirmation roster (200 episodes per opponent): each greedy result, the exhaustive best, the hand-wired unit, the rush rule,
the V3 teacher and four random assemblies. NOT a recorded run; nothing is registered from it.

    .venv/bin/python evidence/tactical_composition_demo/dev_0f/dev_step1_greedy.py
"""
import concurrent.futures as cf
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import tactics_e2 as T2  # noqa: E402
import zd_models as Z  # noqa: E402
import zf_core as G  # noqa: E402
from tcd_common.fileio import stream  # noqa: E402

SPEC = json.loads((HERE/'DEV_SPEC.json').read_text())
ENT, CFG = SPEC['entropy'], SPEC['config']
SEEDS = range(5)
CHUNKS = 8
KW = dict(world_fn=T2.world_fn('V3'), mixes=T2.MIXES)


def train(seed):
    tr = T2.collect('V3', stream(ENT, 1, seed), CFG['train_episodes'])
    A = Z.Arrays(tr, T2.labels('V3', tr))
    idx = stream(ENT, 4, seed).permutation(A.n)[:CFG['n_states']]
    L = Z.fit_composed(A, idx, CFG['L_recipe'], stream(ENT, 3, seed, 1))
    hp = G.fit_scorer(A, idx, G.missing_health, CFG['HP_recipe'], stream(ENT, 3, seed, 2))
    return seed, L, hp


def score(pool, spec, seed, episodes, roster):
    return float(np.mean([G.play_cell(G.make_policy(pool, spec), o, ENT, seed, episodes, roster, **KW) for o in ('rush', 'kiter')]))


def select_job(args):
    seed, L, hp, specs = args
    pool = G.build_pool(L, hp)
    return [(seed, spec, score(pool, spec, seed, CFG['selection_episodes'], 7)) for spec in specs]


def confirm_job(args):
    seed, L, hp, specs = args
    pool = G.build_pool(L, hp)
    out = {G.label(s): score(pool, s, seed, CFG['confirmation_episodes'], 17) for s in specs}
    import tactics as T
    for name, fn in (('teacher', T2.teacher_policy('V3')), ('rush_rule', T.rush_policy)):
        out[name] = float(np.mean([G.play_cell(G.unit_policy(fn), o, ENT, seed, CFG['confirmation_episodes'], 17, **KW) for o in ('rush', 'kiter')]))
    return seed, out


def main():
    started = time.time()
    specs = G.all_assemblies()
    with cf.ProcessPoolExecutor(max_workers=8, mp_context=mp.get_context('spawn')) as ex:
        trained = list(ex.map(train, SEEDS))
        jobs = [(seed, L, hp, specs[c::CHUNKS]) for seed, L, hp in trained for c in range(CHUNKS)]
        tables = {s: {} for s in SEEDS}
        for res in ex.map(select_job, jobs):
            for seed, spec, v in res:
                tables[seed][spec] = v
        plan = {}
        for seed in SEEDS:
            t = tables[seed]
            greedy = {m: G.greedy(t, m) for m in CFG['margins']}
            best = max(t, key=t.get)
            rnd = [specs[i] for i in stream(ENT, 30, seed).choice(len(specs), 4, replace=False)]
            plan[seed] = {'greedy': greedy, 'best': best, 'random': rnd}
        cjobs = []
        for seed, L, hp in trained:
            p = plan[seed]
            todo = {G.DEFAULT, G.HAND_WIRED, p['best'], *[g[-1] for g in p['greedy'].values()], *p['random']}
            cjobs.append((seed, L, hp, sorted(todo)))
        confirm = dict(ex.map(confirm_job, cjobs))
    rows = []
    for seed in SEEDS:
        t, p, c = tables[seed], plan[seed], confirm[seed]
        rows.append({'seed': seed, 'selection': {G.label(s): v for s, v in t.items()}, 'pairs': {'%s>%s%s' % (a, s, '+self' if l else ''): v for (a, s, l), v in G.pairs_table(t).items()},
                     'greedy_paths': {str(m): [G.label(s) for s in path] for m, path in p['greedy'].items()}, 'exhaustive_best': G.label(p['best']),
                     'random': [G.label(s) for s in p['random']], 'confirmation': c})
    out = {'note': '0f development step 1; seeds 0-4; selection roster 7 (100 episodes per opponent), confirmation roster 17 (200)', 'rows': rows, 'wall_seconds': round(time.time()-started, 1)}
    (HERE/'step1_results.json').write_text(json.dumps(out, indent=1))
    for r in rows:
        print('seed', r['seed'], '| exhaustive best', r['exhaustive_best'], '%.3f' % r['selection'][r['exhaustive_best']])
        for m, path in r['greedy_paths'].items():
            print('   greedy margin %s: %s' % (m, ' -> '.join(path)))
        c = r['confirmation']
        print('   confirmation: teacher %.3f | hand-wired %.3f | rush %.3f | greedy(0.02) %.3f | best %.3f | random %s' % (
            c['teacher'], c[G.label(G.HAND_WIRED)], c['rush_rule'], c[r['greedy_paths']['0.02'][-1]], c[r['exhaustive_best']], [round(c[x], 3) for x in r['random']]))
    print('wall', out['wall_seconds'])


if __name__ == '__main__':
    main()
