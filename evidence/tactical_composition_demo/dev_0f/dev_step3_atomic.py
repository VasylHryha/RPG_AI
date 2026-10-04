"""Development step 3 (0f rethink): why did the procedure build only 2-3 pieces? Hypothesis: the pieces were too big (AIM already does the whole targeting job) and the
grammar had two slots. Here targeting is split into ATOMIC scorer pieces (one factor each) plus a decoy; connecting a piece means adding its score into the unit's target score
with a weight. Greedy growth from 'nearest enemy' (DIST alone): each round tries every single change (add a piece with weight 0.5, 1 or 2; change a weight; remove a piece;
toggle the self-loop memory) on the selection roster (100 episodes per opponent) and keeps the best if it gains more than the margin 0.02. The step is the teacher's
stepping rule toward the attacked enemy (coherent). Confirmation on a fresh roster (200 episodes per opponent) against the V3 teacher, rush and the start. Seeds 20-23.
NOT a recorded run.

    .venv/bin/python evidence/tactical_composition_demo/dev_0f/dev_step3_atomic.py
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
import tactics as T  # noqa: E402
import tactics_e2 as T2  # noqa: E402
import zf_core as G  # noqa: E402

SPEC = json.loads((HERE/'DEV_SPEC.json').read_text())
ENT = SPEC['entropy']
SEEDS = (20, 21, 22, 23)
SEL, CONF, MARGIN = 100, 200, 0.02
WEIGHTS = (0.5, 1.0, 2.0)
PIECES = ('DMG', 'MISS', 'INR', 'DIST', 'RANGED', 'NOISE')        # NOISE is the decoy
KW = dict(world_fn=T2.world_fn('V3'), mixes=T2.MIXES)


def features(own, en, rng):
    return {'DMG': en[:, 6]/10.0, 'MISS': 1.0-en[:, 4], 'INR': (en[:, 3] <= own[2]).astype(float), 'DIST': -en[:, 3]/10.0,
            'RANGED': (en[:, 5] > 3.0).astype(float), 'NOISE': rng.normal(0.0, 1.0, len(en))}


def make(spec):
    weights, loop = dict(spec[0]), spec[1]

    def factory(rng):
        memory = {}

        def policy(own, en, unit):
            f = features(own, en, rng)
            s = sum(w*f[p] for p, w in weights.items())
            alive = en[:, 0] > 0
            t = int(np.argmax(np.where(alive, s, -np.inf)))
            if loop and unit in memory and en[memory[unit], 0] > 0:
                t = memory[unit]
            memory[unit] = t
            return T.teacher_move(en[t, 1:3], own[4]), t, False
        return policy
    return factory


def key(weights, loop):
    return (tuple(sorted(weights.items())), loop)


def neighbours(spec):
    weights, loop = dict(spec[0]), spec[1]
    out = []
    for p in PIECES:
        if p not in weights:
            out += [key({**weights, p: w}, loop) for w in WEIGHTS]
        else:
            out += [key({**weights, p: w}, loop) for w in WEIGHTS if w != weights[p]]
            if len(weights) > 1:
                out.append(key({k: v for k, v in weights.items() if k != p}, loop))
    out.append(key(weights, not loop))
    return out


def score(spec, seed, episodes, roster):
    return float(np.mean([G.play_cell(make(spec), o, ENT, seed, episodes, roster, **KW) for o in ('rush', 'kiter')]))


def run(seed):
    t0 = time.time()
    cache = {}
    cur = key({'DIST': 1.0}, False)
    cache[cur] = score(cur, seed, SEL, 7)
    path = [(cur, cache[cur])]
    while True:
        cands = neighbours(cur)
        for c in cands:
            if c not in cache:
                cache[c] = score(c, seed, SEL, 7)
        best = max(cands, key=lambda c: cache[c])
        if cache[best]-cache[cur] > MARGIN:
            cur = best
            path.append((cur, cache[cur]))
        else:
            break
    final = cur
    conf = {'final': score(final, seed, CONF, 17), 'start': score(path[0][0], seed, CONF, 17),
            'teacher': float(np.mean([G.play_cell(G.unit_policy(T2.teacher_policy('V3')), o, ENT, seed, CONF, 17, **KW) for o in ('rush', 'kiter')])),
            'rush': float(np.mean([G.play_cell(G.unit_policy(T.rush_policy), o, ENT, seed, CONF, 17, **KW) for o in ('rush', 'kiter')]))}
    show = lambda s: {'pieces': dict(s[0]), 'memory': s[1]}
    return {'seed': seed, 'path': [{'spec': show(s), 'selection': v} for s, v in path], 'final': show(final), 'n_pieces_final': len(final[0]),
            'evaluations': len(cache), 'confirmation': conf, 'seconds': time.time()-t0}


def main():
    started = time.time()
    with cf.ProcessPoolExecutor(max_workers=len(SEEDS), mp_context=mp.get_context('spawn')) as ex:
        rows = list(ex.map(run, SEEDS))
    out = {'note': '0f development step 3: atomic scorer pieces, greedy growth from nearest-enemy; seeds 20-23', 'rows': rows, 'wall_seconds': round(time.time()-started, 1)}
    (HERE/'step3_results.json').write_text(json.dumps(out, indent=1))
    for r in rows:
        print('seed', r['seed'], '| pieces connected:', r['n_pieces_final'], r['final'], '| evaluations', r['evaluations'])
        for step in r['path']:
            print('    ', step['spec'], round(step['selection'], 3))
        c = r['confirmation']
        print('    confirmation: final %.3f | teacher %.3f | start (nearest) %.3f | rush %.3f' % (c['final'], c['teacher'], c['start'], c['rush']))
    print('wall', out['wall_seconds'])


if __name__ == '__main__':
    main()
