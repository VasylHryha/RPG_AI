"""Shared development code for experiment 0e (own entropy; scratch; NOT a recorded run)."""
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import tactics as T  # noqa: E402
import zd_models as Z  # noqa: E402
import ze_core as E  # noqa: E402
import ze_flat as F  # noqa: E402
from tcd_common.fileio import stream  # noqa: E402

SPEC = json.loads((HERE/'DEV_SPEC.json').read_text())
ENTROPY = SPEC['entropy']
CFG = SPEC['config']
CACHE = Path(os.environ.get('ZE_CACHE', '/tmp/ze_cache'))


def make_data(seed):
    """Training and independent validation pools (episode-level split) with the teacher's labels; cached outside the repository."""
    path = CACHE/('dev0e_seed%d_%d_%d.npz' % (seed, CFG['train_episodes'], CFG['val_episodes']))
    if path.exists():
        z = np.load(path)
        return [({'own': z[p+'own'], 'enemies': z[p+'enemies']}, {k: z[p+k] for k in ('scores', 'target', 'move', 'fire')}) for p in ('tr_', 'va_')]
    CACHE.mkdir(parents=True, exist_ok=True)
    out, save = [], {}
    for p, key, eps in (('tr_', 1, CFG['train_episodes']), ('va_', 2, CFG['val_episodes'])):
        pool = T.collect(stream(ENTROPY, key, seed), eps, T.SEEN_MIXES)
        lab = T.labels(pool)
        out.append((pool, lab))
        save[p+'own'], save[p+'enemies'] = pool['own'], pool['enemies']
        save.update({p+k: v for k, v in lab.items()})
    np.savez_compressed(path, **save)
    return out


def arrays(seed):
    (tr, trl), (va, val) = make_data(seed)
    return Z.Arrays(tr, trl), Z.Arrays(va, val)


def source(A_tr, seed, n=None):
    return stream(ENTROPY, 4, seed).permutation(A_tr.n)[:n or CFG['n_states']]


def fit_L(A_tr, idx, seed):
    return Z.fit_composed(A_tr, idx, CFG['L_recipe'], stream(ENTROPY, 3, seed, 1))


def fit_J(A_tr, idx, seed):
    return Z.fit_s1(A_tr, idx, CFG['J_recipe'], stream(ENTROPY, 3, seed, 2))
