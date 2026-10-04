"""Development step 2 (0f): the level-2 gate (PROPOSAL_0F.md section 5). Does focusing the whole squad on one shared target beat three independent teacher units on V3?
Scripted policies only; development seeds 10-14 of the 0f entropy; 200 episodes per opponent on the confirmation roster key. Also tests the two-step lookahead variant of the
greedy procedure on the step-1 selection tables (no new games). NOT a recorded run.

    .venv/bin/python evidence/tactical_composition_demo/dev_0f/dev_step2_level2_gate.py
"""
import concurrent.futures as cf
import json
import multiprocessing as mp
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import tactics as T  # noqa: E402
import tactics_e2 as T2  # noqa: E402
import zf_core as G  # noqa: E402

SPEC = json.loads((HERE/'DEV_SPEC.json').read_text())
ENT = SPEC['entropy']
SEEDS = range(10, 15)
EPIS = 200
KW = dict(world_fn=T2.world_fn('V3'), mixes=T2.MIXES)
doctrine = T2.doctrine_scores('V3')


def independent(own, en, unit):
    t = int(np.argmax(doctrine(own, en)))
    return T.teacher_move(en[t, 1:3], own[4]), t, False


def focus(rule):
    """All units attack one shared target computed from what every unit sees alike (enemy statistics, not distances); each steps toward it with the teacher's rule."""
    def policy(own, en, unit):
        alive = en[:, 0] > 0
        if rule == 'damage':
            s = en[:, 6]/10.0+(1.0-en[:, 4])
        else:
            s = 1.0-en[:, 4]
        t = int(np.argmax(np.where(alive, s, -9.0)))
        return T.teacher_move(en[t, 1:3], own[4]), t, False
    return policy


def job(seed):
    out = {'seed': seed}
    for name, p in (('independent', independent), ('focus_damage', focus('damage')), ('focus_weakest', focus('weakest'))):
        out[name] = float(np.mean([G.play_cell(lambda rng, p=p: p, o, ENT, seed, EPIS, 17, **KW) for o in ('rush', 'kiter')]))
    return out


def two_step(table, margin, start=G.DEFAULT):
    """Greedy with a two-step lookahead: if no single change clears the margin, try every pair of changes before stopping."""
    path, cur = [start], start
    while True:
        best = max(G.neighbours(cur), key=lambda s: table[s])
        if table[best]-table[cur] > margin:
            cur = best
            path.append(cur)
            continue
        pairs = {n2 for n1 in G.neighbours(cur) for n2 in G.neighbours(n1) if n2 != cur}
        best2 = max(pairs, key=lambda s: table[s])
        if table[best2]-table[cur] > margin:
            cur = best2
            path.append(cur)
            continue
        return path


def main():
    with cf.ProcessPoolExecutor(max_workers=5, mp_context=mp.get_context('spawn')) as ex:
        rows = list(ex.map(job, SEEDS))
    gain = {k: [r[k]-r['independent'] for r in rows] for k in ('focus_damage', 'focus_weakest')}
    step1 = json.loads((HERE/'step1_results.json').read_text())
    lookahead = {}
    inv = {G.label(s): s for s in G.all_assemblies()}
    for r in step1['rows']:
        table = {inv[k]: v for k, v in r['selection'].items()}
        lookahead[r['seed']] = {str(m): [G.label(s) for s in two_step(table, m)] for m in (0.01, 0.02, 0.03)}
    out = {'note': '0f development step 2: level-2 gate (seeds 10-14, 200 episodes per opponent) and the two-step lookahead on the step-1 selection tables',
           'rows': rows, 'focus_gain_over_independent': gain, 'two_step_paths': lookahead}
    (HERE/'step2_results.json').write_text(json.dumps(out, indent=1))
    for r in rows:
        print(r)
    print('focus gain over independent units:', {k: [round(x, 3) for x in v] for k, v in gain.items()})
    for seed, paths in lookahead.items():
        print('two-step lookahead seed', seed, 'margin 0.02:', paths['0.02'][-1])


if __name__ == '__main__':
    main()
