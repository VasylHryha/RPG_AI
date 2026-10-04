"""Round-trip check of the recorded run 0d: rebuild every saved N = 3,000 model from its weights (run_0d/models/*.npz), regenerate each seed's test pool from the
recorded entropy, and compare the recomputed a_joint, test-state digest and strata with the values stored in run_0d/seeds/. Reads only; writes verify_run_0d_result.json.
NEW FILE written after the 2026-10-04 recheck; it is not one of the files hashed into the run record.

    .venv/bin/python evidence/tactical_composition_demo/verify_run_0d.py
"""
import os
for _v in ('OMP_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_v] = '1'          # the recorded run used one BLAS thread per worker
import concurrent.futures as cf
import json
import multiprocessing as mp
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tactics as T  # noqa: E402
import zd_models as Z  # noqa: E402
import zd_run as R  # noqa: E402
from tcd_common.fileio import stream, write_json  # noqa: E402


def std_from(z, name):
    s = Z.Std.__new__(Z.Std)
    s.m, s.s = z[name+'_m'], z[name+'_s']
    return s


def rebuild(name, z, f_star_kind):
    if name in ('C', 'S1'):
        m = Z.Wired(name)
        m.scorer, m.head = _prefixed(z, 'scorer'), _prefixed(z, 'head')
        for k in ('xa', 'ya', 'xm', 'ym'):
            setattr(m, k, std_from(z, k))
        return m
    if name in ('F1', 'F2'):
        m = Z.Flat('mse' if name == 'F1' else 'disc')
        m.net = _flat_net(z)
        m.xs, m.ys = std_from(z, 'xs'), std_from(z, 'ys')
        return m
    net = T.MLP.__new__(T.MLP)
    net.W = [z['net_%d' % i] for i in range(3)]
    net.b = [z['net_%d' % i] for i in range(3, 6)]
    net.mx, net.sx, net.my, net.sy = z['mx'], z['sx'], z['my'], z['sy']
    return Z.F0(net)


def _prefixed(z, prefix):
    net = Z.Net.__new__(Z.Net)
    net.W = [z['%s_%d' % (prefix, i)] for i in range(3)]
    net.b = [z['%s_%d' % (prefix, i)] for i in range(3, 6)]
    return net


def _flat_net(z):
    net = Z.Net.__new__(Z.Net)
    net.W = [z['net_%d' % i] for i in range(3)]
    net.b = [z['net_%d' % i] for i in range(3, 6)]
    return net


def check_seed(seed):
    spec = json.loads((HERE/'SPEC_0D.json').read_text())
    cfg = spec['config']
    R.A_ANGLE[0], R.A_MIN[0] = cfg['angle_deg'], cfg['min_stratum']
    stored = json.loads((HERE/'run_0d'/'seeds'/('seed_%02d.json' % seed)).read_text())
    pool = T.collect(stream(spec['entropy'], 2, seed), cfg['test_episodes'], T.SEEN_MIXES)
    A = Z.Arrays(pool, T.labels(pool))
    out = {'seed': seed, 'digest_matches': R.seed_digest(pool) == stored['test_digest'], 'models': {}}
    for name in R.MODELS:
        z = np.load(HERE/'run_0d'/'models'/('seed_%02d_%s.npz' % (seed, name)))
        r = R.score_model(rebuild(name, z, None), A)
        out['models'][name] = {'recomputed': r['a_joint'], 'stored': stored['a_joint_%s_%d' % (name, cfg['n_primary'])],
                               'abs_diff': abs(r['a_joint']-stored['a_joint_%s_%d' % (name, cfg['n_primary'])]),
                               'admissible_diff': abs(r['a_target_admissible']-stored['a_target_admissible_%s_%d' % (name, cfg['n_primary'])])}
    return out


def main():
    with cf.ProcessPoolExecutor(max_workers=8, mp_context=mp.get_context('spawn')) as pool:
        rows = list(pool.map(check_seed, range(json.loads((HERE/'SPEC_0D.json').read_text())['config']['seeds'])))
    worst = max(m['abs_diff'] for r in rows for m in r['models'].values())
    out = {'note': 'a_joint recomputed from the saved N=3000 weights and a regenerated test pool, against run_0d/seeds', 'seeds': len(rows), 'all_digests_match': all(r['digest_matches'] for r in rows),
           'max_abs_diff_a_joint': worst, 'max_abs_diff_admissible': max(m['admissible_diff'] for r in rows for m in r['models'].values()),
           'models_checked': len(rows)*len(R.MODELS), 'rows': rows}
    write_json(HERE/'verify_run_0d_result.json', out)
    print({k: v for k, v in out.items() if k != 'rows'})
    return 0 if out['all_digests_match'] and worst < 1e-9 else 1


if __name__ == '__main__':
    sys.exit(main())
