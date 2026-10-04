"""Development step 3 (0e): pilot of the whole design on development seeds 3-7 (unused by step 2). Closed-loop cells (100 episodes per opponent) and fixed-state
fidelity for: references, the replacement matrix and swaps with J, degraded and hybrid controls, the whole F*-plus policy, same-piece wire cuts, the fault doses and
the teacher under the same faults, plus the directed sensitivity control and the semantics-preserving controls. It measures noise (to set episodes per cell), cost,
and whether every gate and control behaves. NOT a recorded run; no verdict is computed.

    ZE_CACHE=/tmp/ze_cache .venv/bin/python evidence/tactical_composition_demo/dev_0e/dev_step3_matrix.py
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

E, F, T, Z = D.E, D.F, D.T, D.Z
SEEDS = (3, 4, 5, 6, 7)
EPISODES = 100
HERE = Path(__file__).resolve().parent


def cells(L, J, Fp, ref):
    O_a, O_m = E.AimOracle(), E.MoveOracle()
    La, Lm, Ja, Jm = E.AimWired(L, 'L'), E.MoveWired(L, 'L'), E.AimWired(J, 'J'), E.MoveWired(J, 'J')
    W = lambda k, v=None: E.Wire(k, v, ref)
    out = {
        'OO': E.Assembly(O_a, O_m), 'LO': E.Assembly(La, O_m), 'OL': E.Assembly(O_a, Lm), 'LL': E.Assembly(La, Lm),
        'JJ': E.Assembly(Ja, Jm), 'JL': E.Assembly(Ja, Lm), 'LJ': E.Assembly(La, Jm),
        'DO': E.Assembly(E.AimNearest(), O_m), 'OD': E.Assembly(O_a, E.MoveApproach()),
        'FhO': E.Assembly(E.AimFlatOutput(Fp, 'Fh'), O_m), 'OFh': E.Assembly(O_a, E.MoveFlatOutput(Fp, 'Fh')),
        'LL|default': E.Assembly(La, Lm, W('default')), 'LL|wrong': E.Assembly(La, Lm, W('wrong')), 'LL|zero': E.Assembly(La, Lm, W('zero'))}
    for k, v in (('noise', 0.02), ('wrongfrac', 0.01), ('scale', 0.9), ('scale', 1.1), ('noise', 0.05), ('noise', 0.10), ('wrongfrac', 0.05), ('wrongfrac', 0.10),
                 ('scale', 0.5), ('scale', 2.0)):
        out['LL|%s_%g' % (k, v)] = E.Assembly(La, Lm, W(k, v))
    for k, v in (('noise', 0.02), ('wrongfrac', 0.01), ('scale', 0.9), ('scale', 1.1)):
        out['OO|%s_%g' % (k, v)] = E.Assembly(O_a, O_m, W(k, v))
    return out


FIXED_ONLY = {'LL|reverse': ('reverse', None), 'LL|relabel': ('relabel', None), 'LL|sham': ('sham', None), 'OO|reverse': ('reverse', None)}


def job(seed):
    t0 = time.time()
    step1 = json.loads((HERE/'step1_results.json').read_text())['summary']
    sel = json.loads((HERE/'step2_results.json').read_text())['selected']['hp']
    ref = step1['ref_distance']
    A_tr, A_va = D.arrays(seed)
    idx = D.source(A_tr, seed)
    L, J = D.fit_L(A_tr, idx, seed), D.fit_J(A_tr, idx, seed)
    Fp = F.FlatPlus(sel['head']).fit(A_tr, idx, sel, D.stream(D.ENTROPY, 3, seed, 3))
    t1 = time.time()
    out = {'seed': seed, 'fit_seconds': t1-t0, 'fixed': {}, 'play': {}, 'applied_share': {}}
    cs = cells(L, J, Fp, ref)
    rng_fixed = lambda k: D.stream(D.ENTROPY, 9, seed, abs(hash(k)) % 10**6)
    for name, asm in cs.items():
        chosen, step, applied = asm.act(A_va, rng_fixed(name))
        out['fixed'][name] = E.joint3(chosen, step, A_va)
        out['applied_share'][name] = float(applied.mean())
    La, Lm = E.AimWired(L, 'L'), E.MoveWired(L, 'L')
    for name, (k, v) in FIXED_ONLY.items():
        aim, move = (La, Lm) if name.startswith('LL') else (E.AimOracle(), E.MoveOracle())
        chosen, step, applied = E.Assembly(aim, move, E.Wire(k, v, ref)).act(A_va, rng_fixed(name))
        out['fixed'][name] = E.joint3(chosen, step, A_va)
    fp = E.joint3(*Fp.act(A_va), A_va)
    out['fixed']['Fp'] = fp
    t2 = time.time()

    def fp_policy(rng):
        def policy(own, enemies):
            A = Z.Arrays({'own': own[None], 'enemies': enemies[None]})
            c, s = Fp.act(A)
            return s[0], int(c[0]), False
        return policy
    for opp in ('rush', 'kiter'):
        out['play']['R_'+opp] = E.play_cell(lambda rng: T.rush_policy, opp, D.ENTROPY, seed, EPISODES)
        out['play']['Fp_'+opp] = E.play_cell(fp_policy, opp, D.ENTROPY, seed, EPISODES)
        for name, asm in cs.items():
            out['play'][name+'_'+opp] = E.play_cell(asm.policy, opp, D.ENTROPY, seed, EPISODES)
    out['play_seconds'] = time.time()-t2
    out['seconds'] = time.time()-t0
    return out


def main():
    started = time.time()
    with cf.ProcessPoolExecutor(max_workers=8, mp_context=mp.get_context('spawn')) as pool:
        rows = list(pool.map(job, SEEDS))
    (HERE/'step3_results.json').write_text(json.dumps({'note': '0e development step 3 pilot; seeds 3-7; %d episodes per opponent per cell' % EPISODES,
                                                      'rows': rows, 'wall_seconds': round(time.time()-started, 1)}, indent=1, default=float))
    W = lambda r, c: np.mean([r['play']['%s_%s' % (c, o)]['score'] for o in ('rush', 'kiter')])
    names = ['R', 'Fp']+[k for k in rows[0]['fixed'] if k in rows[0]['play'] or k+'_rush' in rows[0]['play']]
    print('%-16s %8s %8s %8s' % ('cell', 'win', 'a_joint', 'macro'))
    for c in names:
        if c+'_rush' not in rows[0]['play']:
            continue
        w = np.mean([W(r, c) for r in rows])
        fj = np.mean([r['fixed'][c]['a_joint'] for r in rows]) if c in rows[0]['fixed'] else float('nan')
        fm = np.mean([r['fixed'][c]['a_macro'] for r in rows]) if c in rows[0]['fixed'] else float('nan')
        print('%-16s %8.3f %8.3f %8.3f' % (c, w, fj, fm))
    for c in FIXED_ONLY:
        print('%-16s %8s %8.3f %8.3f' % (c, '-', np.mean([r['fixed'][c]['a_joint'] for r in rows]), np.mean([r['fixed'][c]['a_macro'] for r in rows])))
    print('seconds per seed', np.mean([r['seconds'] for r in rows]), 'play', np.mean([r['play_seconds'] for r in rows]), 'wall', round(time.time()-started, 1))


if __name__ == '__main__':
    main()
