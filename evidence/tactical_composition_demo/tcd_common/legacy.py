"""Regression gate: the current tactics.py reproduces the recorded versions on every primitive reachable from the recorded harnesses.

The recorded runs pin their own tactics.py by hash in RUN_STARTED.json (Stage 0 c0d849..., change r1 d64667..., change r2 37fa0a...). Those files
are recovered from git at the commit each run started from (`git show <head>:<path>`), loaded as separate modules, and compared with the current
file on the same random streams. Equality is exact (bit for bit), not approximate.
"""
import hashlib
import subprocess
import types
from pathlib import Path

import numpy as np

from . import PARENT

ROOT = PARENT.parents[1]
REL = str(PARENT.relative_to(ROOT))+'/tactics.py'
# run -> the commit it started from and the tactics.py hash in its RUN_STARTED.json
RECORDED = {'stage0': ('bc5ce29b357fb29e078d2e47fd9cd7070c0bf1f2', 'c0d849'), 'change_r1': ('d32485aa6e6d0610daac3cbdb8148fc04fdc13e1', 'd64667'),
            'change_r2': ('3381e03a786efc933a4da1f88628bb63ef8e728c', '37fa0a')}


def source_at(rev):
    out = subprocess.run(['git', 'show', '%s:%s' % (rev, REL)], cwd=ROOT, capture_output=True)
    if out.returncode:
        raise LookupError('revision %s is not available: %s' % (rev, out.stderr.decode()[:200]))
    return out.stdout


def load(source, name):
    module = types.ModuleType(name)
    exec(compile(source, name, 'exec'), module.__dict__)
    return module


def identity(source):
    return hashlib.sha256(source).hexdigest()


def stream(entropy, *key):
    return np.random.default_rng(np.random.SeedSequence([entropy, *key]))


def same(a, b):
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, np.ndarray):
        return a.shape == b.shape and bool(np.array_equal(a, b))
    return a == b


def trace(T, seed, episodes=10, n_aim=400, n_move=400, hidden=16, steps=200, eval_episodes=3):
    """Everything the recorded Stage 0 / change harnesses call, on fixed streams. Returns plain data for exact comparison."""
    out = {}
    pool = T.collect(stream(7, 1, seed), episodes, T.SEEN_MIXES)
    out['pool'] = pool
    lab = T.labels(pool)
    out['labels'] = lab
    data = T.piece_datasets(pool, lab, n_aim, n_move, stream(7, 2, seed))
    out['datasets'] = {k: v for k, v in data.items()}
    aim = T.MLP(T.AIM_DIM, hidden, 1, stream(7, 3, seed)).fit(*data['AIM'], stream(7, 4, seed), steps)
    move = T.MLP(T.MOVE_DIM, hidden, 2, stream(7, 5, seed)).fit(*data['MOVE'], stream(7, 6, seed), steps)
    out['aim_w'], out['move_w'] = aim.W+aim.b, move.W+move.b
    X, Y = T.mono_dataset(pool, lab, 300, stream(7, 7, seed))
    out['mono_data'] = (X, Y)
    mono = T.MLP(T.MONO_IN, 15, T.MONO_OUT, stream(7, 8, seed)).fit(X, Y, stream(7, 9, seed), steps)
    out['mono_w'] = mono.W+mono.b
    out['fidelity'] = T.fidelity({'AIM': aim, 'MOVE': move}, pool, lab)
    out['mono_fidelity'] = T.mono_fidelity(mono, pool, lab)
    for name, mixes in (('seen', T.SEEN_MIXES), ('unseen', T.UNSEEN_MIXES)):
        for opp in ('rush', 'kiter'):
            out['win_composed_%s_%s' % (name, opp)] = T.win_score(T.composed_policy(aim, move), mixes, T.OPPONENTS[opp], stream(7, 10, seed), eval_episodes)
            out['win_mono_%s_%s' % (name, opp)] = T.win_score(T.mono_policy(mono), mixes, T.OPPONENTS[opp], stream(7, 11, seed), eval_episodes)
        out['win_teacher_%s' % name] = T.win_score(T.teacher_policy, mixes, T.OPPONENTS['rush'], stream(7, 12, seed), eval_episodes)
    return out


def compare(current, recorded, seeds=(0, 1), **kw):
    """{'equal': bool, 'differs': [keys]} over the given seeds."""
    differs = []
    for seed in seeds:
        a, b = trace(current, seed, **kw), trace(recorded, seed, **kw)
        differs += ['%s@seed%d' % (k, seed) for k in a if not same(a[k], b[k])]
    return {'equal': not differs, 'differs': differs}
