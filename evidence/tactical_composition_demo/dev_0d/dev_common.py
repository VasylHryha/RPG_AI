"""Shared development code for experiment 0d Part A (own entropy; scratch outside geomind/). Not a recorded run."""
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import tactics as T  # noqa: E402
import zd_models as Z  # noqa: E402
from tcd_common import metrics  # noqa: E402
from tcd_common.fileio import stream  # noqa: E402

SPEC = json.loads((HERE/'DEV_SPEC.json').read_text())
ENTROPY = SPEC['entropy']
CACHE = Path(os.environ.get('ZD_CACHE', '/tmp/zd_cache'))


def make_data(seed, train_episodes=None, val_episodes=None):
    """Training and independent validation pools for one development seed (episode-level split), with the registered teacher's labels. Cached."""
    train_episodes = train_episodes or SPEC['config']['train_episodes']
    val_episodes = val_episodes or SPEC['config']['val_episodes']
    path = CACHE/('dev_seed%d_%d_%d.npz' % (seed, train_episodes, val_episodes))
    if path.exists():
        z = np.load(path)
        out = []
        for pre in ('tr_', 'va_'):
            pool = {'own': z[pre+'own'], 'enemies': z[pre+'enemies']}
            lab = {k: z[pre+k] for k in ('scores', 'target', 'move', 'fire')}
            out.append((pool, lab))
        return out
    CACHE.mkdir(parents=True, exist_ok=True)
    pools = []
    for key, eps in ((1, train_episodes), (2, val_episodes)):
        pool = T.collect(stream(ENTROPY, key, seed), eps, T.SEEN_MIXES)
        pools.append((pool, T.labels(pool)))
    save = {}
    for pre, (pool, lab) in zip(('tr_', 'va_'), pools):
        save[pre+'own'], save[pre+'enemies'] = pool['own'], pool['enemies']
        save.update({pre+k: v for k, v in lab.items()})
    np.savez_compressed(path, **save)
    return pools


def piece_and_connection(model, A):
    """Pieces alone, then connected, then the gap. A = validation Arrays (with teacher labels)."""
    pool, lab = A.pool, A.lab
    chosen, step = model.act(A)
    joint = metrics.joint_action(chosen, step, pool, lab)
    agree = metrics.agreement(chosen, pool, lab)
    # MOVE alone: told the teacher's own target (the situation it was taught in)
    told = model.step_for(A, A.target)
    move_alone = metrics.joint_action(A.target, told, pool, lab)
    independent = joint['a_target_admissible']*move_alone['a_joint']
    return {'a_joint': joint['a_joint'], 'aim_alone_admissible': joint['a_target_admissible'], 'aim_alone_agree_corrected': agree['agree_corrected_multi'],
            'move_alone_joint_on_teacher_target': move_alone['a_joint'], 'step_ok_given_admissible': joint['a_step_given_admissible'],
            'independent_prediction': independent, 'connection_gap': joint['a_joint']-independent,
            'strata': {k: joint[k] for k in joint if k.startswith('a_joint_stratum_') or k.startswith('n_stratum_')},
            'step_angle_median_moving_deg': joint['step_angle_median_moving_deg'], 'n_multi': joint['n_multi']}


def fit_and_score(name, hp, seed, n_states=None):
    """Fit one model family on `n_states` source states of one development seed and score it on the validation pool."""
    n_states = n_states or SPEC['config']['n_states']
    (tr_pool, tr_lab), (va_pool, va_lab) = make_data(seed)
    A_tr, A_va = Z.Arrays(tr_pool, tr_lab), Z.Arrays(va_pool, va_lab)
    rng = stream(ENTROPY, 3, seed, hash_name(name))
    idx = Z.source_states(A_tr.n, n_states, stream(ENTROPY, 4, seed))
    started = time.time()
    model = Z.FITS[name](A_tr, idx, hp, rng)
    fit_seconds = time.time()-started
    out = piece_and_connection(model, A_va)
    out.update({'model': name, 'seed': seed, 'fit_seconds': round(fit_seconds, 2), 'n_params': model.n_params, 'supervision': model.supervision,
                'oracle_queries': getattr(model, 'oracle_queries', 0), 'hp': hp})
    return out


def hash_name(name):
    return {'F0': 0, 'F1': 1, 'F2': 2, 'C': 3, 'S1': 4}[name]
