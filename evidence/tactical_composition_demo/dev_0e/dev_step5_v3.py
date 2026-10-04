"""Development step 5 (0e): repeat steps 2 and 3 on the qualified task revision V3 (tactics_e2.py; selected by step 4's fixed rule).
Phase A: the F*-plus search of step 2 (same grid and selection rule) on development seeds 15-17. Phase B: the step-3 pilot (pieces L and J trained on V3, the selected
F*-plus, the replacement matrix, same-piece wire cuts, fault doses, the teacher under the same faults, the directed and semantics-preserving controls) on seeds 20-24,
100 episodes per opponent per cell. NOT a recorded run; no verdict.

    ZE_CACHE=/tmp/ze_cache .venv/bin/python evidence/tactical_composition_demo/dev_0e/dev_step5_v3.py
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
import dev_step2_flatplus as S2  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tactics_e2 as T2  # noqa: E402

E, F, T, Z = D.E, D.F, D.T, D.Z
TASK = 'V3'
SEARCH_SEEDS, PILOT_SEEDS = (15, 16, 17), (20, 21, 22, 23, 24)
EPISODES = 100
HERE = Path(__file__).resolve().parent
WF, MIXES = T2.world_fn(TASK), T2.MIXES
ORACLE_SCORER = T2.doctrine_scores_batch(TASK)


def flat_policy(m):
    def make(rng):
        def policy(own, enemies):
            A = Z.Arrays({'own': own[None], 'enemies': enemies[None]})
            c, s = m.act(A)
            return s[0], int(c[0]), False
        return policy
    return make


def play(make, opp, seed):
    return E.play_cell(make, opp, D.ENTROPY, seed, EPISODES, world_fn=WF, mixes=MIXES)


def search_job(args):
    k, hp, seed = args
    A_tr, A_va = D.arrays(seed, TASK)
    idx = D.source(A_tr, seed)
    t0 = time.time()
    m = F.FlatPlus(hp['head']).fit(A_tr, idx, hp, D.stream(D.ENTROPY, 3, seed, 100+k))
    j = E.joint3(*m.act(A_va), A_va)
    sc = {o: play(flat_policy(m), o, seed)['score'] for o in ('rush', 'kiter')}
    rush = {o: play(lambda rng: T.rush_policy, o, seed)['score'] for o in ('rush', 'kiter')} if k == 0 else None
    return {'k': k, 'hp': hp, 'seed': seed, 'a_joint': j['a_joint'], 'macro': j['a_macro'], 'backoff': j['a_backoff'], 'score': (sc['rush']+sc['kiter'])/2,
            'rush_ref': None if rush is None else (rush['rush']+rush['kiter'])/2, 'n_params': m.n_params, 'seconds': time.time()-t0}


def cells(L, J, Fp, ref):
    O_a, O_m = E.AimOracle(ORACLE_SCORER), E.MoveOracle()
    La, Lm, Ja, Jm = E.AimWired(L, 'L'), E.MoveWired(L, 'L'), E.AimWired(J, 'J'), E.MoveWired(J, 'J')
    W = lambda k, v=None: E.Wire(k, v, ref)
    out = {'OO': E.Assembly(O_a, O_m), 'LO': E.Assembly(La, O_m), 'OL': E.Assembly(O_a, Lm), 'LL': E.Assembly(La, Lm),
           'JJ': E.Assembly(Ja, Jm), 'JL': E.Assembly(Ja, Lm), 'LJ': E.Assembly(La, Jm),
           'DO': E.Assembly(E.AimNearest(), O_m), 'OD': E.Assembly(O_a, E.MoveApproach()),
           'FhO': E.Assembly(E.AimFlatOutput(Fp, 'Fh'), O_m), 'OFh': E.Assembly(O_a, E.MoveFlatOutput(Fp, 'Fh')),
           'LL|default': E.Assembly(La, Lm, W('default')), 'LL|wrong': E.Assembly(La, Lm, W('wrong')), 'LL|zero': E.Assembly(La, Lm, W('zero')),
           'OO|default': E.Assembly(O_a, O_m, W('default'))}
    for k, v in (('noise', 0.02), ('wrongfrac', 0.01), ('scale', 0.9), ('scale', 1.1), ('noise', 0.05), ('noise', 0.10), ('wrongfrac', 0.05), ('wrongfrac', 0.10),
                 ('scale', 0.5), ('scale', 2.0)):
        out['LL|%s_%g' % (k, v)] = E.Assembly(La, Lm, W(k, v))
    for k, v in (('noise', 0.02), ('wrongfrac', 0.01), ('scale', 0.9), ('scale', 1.1)):
        out['OO|%s_%g' % (k, v)] = E.Assembly(O_a, O_m, W(k, v))
    return out


def pilot_job(args):
    seed, sel, ref = args
    t0 = time.time()
    A_tr, A_va = D.arrays(seed, TASK)
    idx = D.source(A_tr, seed)
    L, J = D.fit_L(A_tr, idx, seed), D.fit_J(A_tr, idx, seed)
    Fp = F.FlatPlus(sel['head']).fit(A_tr, idx, sel, D.stream(D.ENTROPY, 3, seed, 3))
    rows = np.arange(A_va.n)
    out = {'seed': seed, 'fit_seconds': time.time()-t0, 'fixed': {}, 'play': {}, 'prequal': {}}
    for name, model in (('L', L), ('J', J)):
        aim, move = E.AimWired(model, name), E.MoveWired(model, name)
        ch = aim.choose(A_va)
        a = E.joint3(ch, E.MoveOracle().step(A_va, A_va.REL[rows, ch]), A_va)
        m = E.move_alone(move, A_va)
        out['prequal'][name] = {'aim_admissible': a['a_target_admissible'], 'n_unique_best': a['n_unique_best'], 'move_alone': m['a_joint'],
                                'hold': m['a_hold'], 'approach': m['a_approach'], 'backoff': m['a_backoff'], 'n_hold': m['n_hold'], 'n_approach': m['n_approach'],
                                'n_backoff': m['n_backoff']}
    cs = cells(L, J, Fp, ref)
    for name, asm in cs.items():
        out['fixed'][name] = E.joint3(*asm.act(A_va, D.stream(D.ENTROPY, 9, seed, abs(hash(name)) % 10**6))[:2], A_va)
    La, Lm = E.AimWired(L, 'L'), E.MoveWired(L, 'L')
    for name, (k, a_, m_) in {'LL|reverse': ('reverse', La, Lm), 'LL|relabel': ('relabel', La, Lm), 'LL|sham': ('sham', La, Lm),
                             'OO|reverse': ('reverse', E.AimOracle(ORACLE_SCORER), E.MoveOracle())}.items():
        out['fixed'][name] = E.joint3(*E.Assembly(a_, m_, E.Wire(k, None, ref)).act(A_va, D.stream(D.ENTROPY, 9, seed, 7))[:2], A_va)
    out['fixed']['Fp'] = E.joint3(*Fp.act(A_va), A_va)
    t1 = time.time()
    for opp in ('rush', 'kiter'):
        out['play']['R_'+opp] = play(lambda rng: T.rush_policy, opp, seed)
        out['play']['Fp_'+opp] = play(flat_policy(Fp), opp, seed)
        for name, asm in cs.items():
            out['play'][name+'_'+opp] = play(asm.policy, opp, seed)
    out['play_seconds'] = time.time()-t1
    out['seconds'] = time.time()-t0
    return out


def main():
    started = time.time()
    with cf.ProcessPoolExecutor(max_workers=8, mp_context=mp.get_context('spawn')) as pool:
        list(pool.map(D.make_data, SEARCH_SEEDS+PILOT_SEEDS, [TASK]*8))
        srows = list(pool.map(search_job, [(k, hp, s) for k, hp in enumerate(S2.GRID) for s in SEARCH_SEEDS], chunksize=1))
        rush_ref = {r['seed']: r['rush_ref'] for r in srows if r['rush_ref'] is not None}
        table = []
        for k, hp in enumerate(S2.GRID):
            rr = [r for r in srows if r['k'] == k]
            table.append({'k': k, 'hp': hp, 'score': float(np.mean([r['score'] for r in rr])), 'macro': float(np.mean([r['macro'] for r in rr])),
                          'a_joint': float(np.mean([r['a_joint'] for r in rr])), 'gain_over_rush': float(np.mean([r['score']-rush_ref[r['seed']] for r in rr])),
                          'n_params': rr[0]['n_params']})
        order = sorted(table, key=lambda t: (-round(t['score'], 6), -t['macro'], t['n_params']))
        sel = order[0]['hp']
        ref = float(np.median([np.median(D.arrays(s, TASK)[1].en[np.arange(D.arrays(s, TASK)[1].n), E.AimOracle(ORACLE_SCORER).choose(D.arrays(s, TASK)[1]), 3]) for s in SEARCH_SEEDS]))
        prows = list(pool.map(pilot_job, [(s, sel, ref) for s in PILOT_SEEDS]))
    out = {'note': '0e development step 5 on task V3: phase A F*-plus search (seeds 15-17), phase B pilot (seeds 20-24), %d episodes per opponent per cell' % EPISODES,
           'search_table': order, 'selected': sel, 'ref_distance': ref, 'search_rows': srows, 'pilot_rows': prows, 'wall_seconds': round(time.time()-started, 1)}
    (HERE/'step5_results.json').write_text(json.dumps(out, indent=1, default=float))
    for t in order[:8]:
        print('search %-7s w%3d d%d | score %.3f gain/rush %+.3f | a_joint %.3f | params %d' % (t['hp']['head'], t['hp']['hidden'], t['hp']['depth'], t['score'], t['gain_over_rush'], t['a_joint'], t['n_params']))
    print('flat-only best:', max((t for t in order if t['hp']['head'] != 'perslot'), key=lambda t: t['score']))
    print('selected', sel, 'ref distance', round(ref, 2))
    Wm = lambda r, c: np.mean([r['play']['%s_%s' % (c, o)]['score'] for o in ('rush', 'kiter')])
    print('%-18s %7s %7s %7s' % ('cell', 'win', 'a_joint', 'macro'))
    for c in ['R', 'Fp']+list(prows[0]['fixed']):
        w = np.mean([Wm(r, c) for r in prows]) if c+'_rush' in prows[0]['play'] else float('nan')
        fj = np.mean([r['fixed'][c]['a_joint'] for r in prows]) if c in prows[0]['fixed'] else float('nan')
        fm = np.mean([r['fixed'][c]['a_macro'] for r in prows]) if c in prows[0]['fixed'] else float('nan')
        print('%-18s %7.3f %7.3f %7.3f' % (c, w, fj, fm))
    for name in ('L', 'J'):
        print(name, 'prequal', {k: round(float(np.mean([r['prequal'][name][k] for r in prows])), 3) for k in prows[0]['prequal'][name]})
    print('wall', out['wall_seconds'], 'pilot seconds per seed', np.mean([r['seconds'] for r in prows]))


if __name__ == '__main__':
    main()
