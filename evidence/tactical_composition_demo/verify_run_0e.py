"""Round-trip check of the recorded run 0e (NEW file, not among the files hashed into the run): rebuild every saved model (L, J, Fp, Fflat) from
run_0e/models, regenerate each seed's test pool from the recorded entropy, recompute every fixed-state score (including the faulted wires, with
their registered streams) and the prequalification values, and compare them with run_0e/seeds; replay a sample of closed-loop cells exactly.
Writes verify_run_0e_result.json. Reads only.

    .venv/bin/python evidence/tactical_composition_demo/verify_run_0e.py
"""
import os
for _v in ('OMP_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_v] = '1'
import concurrent.futures as cf
import hashlib
import json
import multiprocessing as mp
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tactics_e2 as T2  # noqa: E402
import zd_models as Z  # noqa: E402
import ze_core as E  # noqa: E402
import ze_flat as F  # noqa: E402
import ze_run as R  # noqa: E402
from tcd_common.fileio import stream, write_json  # noqa: E402

REPLAY = {0: ['LL', 'LL|default', 'Fp'], 17: ['OO', 'JL', 'LL|noise_0.02']}      # closed-loop cells replayed exactly (both opponents)


def _net(cls, z, prefix):
    keys = sorted([k for k in z.files if k.startswith(prefix+'_')], key=lambda k: int(k.split('_')[-1]))
    L = len(keys)//2
    n = cls.__new__(cls)
    n.W, n.b = [z[k] for k in keys[:L]], [z[k] for k in keys[L:]]
    return n


def _std(z, name):
    s = Z.Std.__new__(Z.Std)
    s.m, s.s = z[name+'_m'], z[name+'_s']
    return s


def rebuild(seed, name):
    z = np.load(HERE/'run_0e'/'models'/('seed_%02d_%s.npz' % (seed, name)))
    if name in ('L', 'J'):
        m = Z.Wired(name)
        m.scorer, m.head = _net(Z.Net, z, 'scorer'), _net(Z.Net, z, 'head')
        for k in ('xa', 'ya', 'xm', 'ym'):
            setattr(m, k, _std(z, k))
        return m
    m = F.FlatPlus('perslot' if name == 'Fp' else 'mse')
    m.net = _net(F.DeepNet, z, 'net')
    m.xs, m.ss, m.ms = _std(z, 'xs'), _std(z, 'ss'), _std(z, 'ms')
    return m


def check(seed):
    spec = json.loads((HERE/'SPEC_0E.json').read_text())
    cfg, entropy = spec['config'], spec['entropy']
    stored = json.loads((HERE/'run_0e'/'seeds'/('seed_%02d.json' % seed)).read_text())
    te = T2.collect(cfg['task'], stream(entropy, 2, seed), cfg['test_episodes'])
    A = Z.Arrays(te, T2.labels(cfg['task'], te))
    h = hashlib.sha256()
    h.update(np.ascontiguousarray(te['own']).tobytes())
    h.update(np.ascontiguousarray(te['enemies']).tobytes())
    L, J, Fp, Ff = (rebuild(seed, n) for n in ('L', 'J', 'Fp', 'Fflat'))
    out = {'seed': seed, 'digest_matches': h.hexdigest() == stored['test_digest'], 'max_diff_fixed': 0.0, 'max_diff_prequal': 0.0, 'cells_checked': 0, 'replay': {}}
    rows = np.arange(A.n)
    for name, model in (('L', L), ('J', J)):
        aim, move = E.AimWired(model, name), E.MoveWired(model, name)
        ch = aim.choose(A)
        a = E.joint3(ch, E.MoveOracle().step(A, A.REL[rows, ch]), A)
        m = E.move_alone(move, A)
        fresh = {'aim_admissible': a['a_target_admissible'], 'move_success': m['a_joint'], 'hold': m['a_hold'], 'approach': m['a_approach'], 'backoff': m['a_backoff']}
        out['max_diff_prequal'] = max(out['max_diff_prequal'], max(abs(fresh[k]-stored['prequal'][name][k]) for k in fresh))
    cells, fixed_only = R.cell_assemblies(cfg, L, J, Fp)
    for code, (name, asm) in enumerate(list(cells.items())+list(fixed_only.items())):
        ch, st, _ = asm.act(A, stream(entropy, 9, seed, code))
        j = E.joint3(ch, st, A)
        out['max_diff_fixed'] = max(out['max_diff_fixed'], max(abs(j[k]-stored['fixed'][name][k]) for k in ('a_joint', 'a_macro', 'a_target_admissible')))
        out['cells_checked'] += 1
    for name, m in (('Fp', Fp), ('Fflat', Ff)):
        j = E.joint3(*m.act(A), A)
        out['max_diff_fixed'] = max(out['max_diff_fixed'], abs(j['a_joint']-stored['fixed'][name]['a_joint']))
        out['cells_checked'] += 1
    policies = {'Fp': R.flat_policy(Fp)}
    policies.update({n: a.policy for n, a in cells.items()})
    for name in REPLAY.get(seed, []):
        for opp in R.OPP:
            fresh = E.play_cell(policies[name], opp, entropy, seed, cfg['episodes'], world_fn=T2.world_fn(cfg['task']), mixes=T2.MIXES)
            out['replay']['%s_%s' % (name, opp)] = fresh == stored['play']['%s_%s' % (name, opp)]
    return out


def main():
    with cf.ProcessPoolExecutor(max_workers=8, mp_context=mp.get_context('spawn')) as pool:
        rows = list(pool.map(check, range(30)))
    out = {'note': 'run_0e round trip from saved weights and regenerated test pools; fixed-state values and prequalification compared for every seed; closed-loop cells replayed for seeds 0 and 17',
           'all_digests_match': all(r['digest_matches'] for r in rows), 'max_diff_fixed': max(r['max_diff_fixed'] for r in rows),
           'max_diff_prequal': max(r['max_diff_prequal'] for r in rows), 'cells_checked': sum(r['cells_checked'] for r in rows),
           'replays_identical': all(v for r in rows for v in r['replay'].values()), 'replays': sum(len(r['replay']) for r in rows), 'rows': rows}
    write_json(HERE/'verify_run_0e_result.json', out)
    print({k: v for k, v in out.items() if k != 'rows'})
    return 0 if out['all_digests_match'] and out['max_diff_fixed'] == 0 and out['replays_identical'] else 1


if __name__ == '__main__':
    sys.exit(main())
