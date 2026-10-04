"""Experiment 0f (PROPOSAL_0F.md): bottom-up structure by measured connections. Pieces with declared ports, assemblies, the fixed greedy procedure, and closed-loop
play that tells each policy which unit it controls (for the self-connection's memory). Exploratory; NOT a milestone. A NEW file; frozen modules are imported read-only.

Ports. Target producers (AIM, HP, NEAR, RAND) emit a living enemy identity. Step producers (MOVE, APPROACH, DRIFT) emit a step; MOVE and APPROACH consume a position
message (the relative position of an enemy) and own statistics, DRIFT consumes nothing. An assembly = (attack producer, self-loop on or off, step producer, message source),
where the message source is 'ATTACK' (the coherent wiring: the enemy actually attacked) or any target producer. The default assembly (NEAR, no self-loop, APPROACH, ATTACK)
is exactly the rush rule.
"""
import itertools

import numpy as np

from tcd_common import PARENT  # noqa: F401
import tactics as T
import zd_models as Z
import ze_core as E
from tcd_common.fileio import stream

N = T.N_UNITS
TARGETS = ('AIM', 'HP', 'NEAR', 'RAND')
STEPS = ('MOVE', 'APPROACH', 'DRIFT')
MESSAGES = ('ATTACK',)+TARGETS
DEFAULT = ('NEAR', False, 'APPROACH', 'ATTACK')
HAND_WIRED = ('AIM', False, 'MOVE', 'ATTACK')
OPP_CODE = {'rush': 0, 'kiter': 1}


# ------------------------------------------------------------------ pieces

class ScorerPiece:
    """A learned target producer: a scorer shared by every enemy (the AIM architecture), argmax over living enemies."""

    def __init__(self, net, xs, ys, name):
        self.net, self.xs, self.ys, self.name = net, xs, ys, name

    def choose(self, A, rng=None):
        out, _ = self.net.forward(self.xs.f(A.AIMX.reshape(-1, A.AIMX.shape[2])))
        return Z.masked_argmax(self.ys.inv(out).reshape(A.n, N), A.alive)


class Near:
    name = 'NEAR'

    def choose(self, A, rng=None):
        return E.nearest_living(A)


class Rand:
    name = 'RAND'

    def choose(self, A, rng):
        return np.array([int(rng.choice(np.flatnonzero(a))) for a in A.alive])


class MovePiece:
    name = 'MOVE'

    def __init__(self, wired):
        self.inner = E.MoveWired(wired, 'MOVE')

    def step(self, A, rel):
        return self.inner.step(A, rel)


class Approach:
    """The rush rule's step: walk straight at the message until within 90% of own range."""
    name = 'APPROACH'

    def step(self, A, rel):
        d = np.hypot(rel[:, 0], rel[:, 1])
        go = (d > 0.9*A.own[:, 2]) & (d > 1e-9)
        return np.where(go[:, None], rel/np.maximum(d, 1e-9)[:, None], 0.0)


class Drift:
    name = 'DRIFT'

    def step(self, A, rel):
        return np.tile([1.0, 0.0], (A.n, 1))


def fit_scorer(A, idx, label_fn, hp, rng):
    """A target producer with the AIM architecture trained on another job: label_fn(A, idx) gives one value per living (state, enemy) pair."""
    alive = A.alive[idx]
    X = A.AIMX[idx][alive]
    Y = label_fn(A, idx)[alive][:, None]
    xs, ys = Z.Std(X), Z.Std(Y)
    net = Z.Net(X.shape[1], hp['hidden'], 1, rng)
    Zi, Tn = xs.f(X), ys.f(Y)

    def grad_fn(b):
        out, cache = net.forward(Zi[b])
        return net.backward(cache, 2.0*(out-Tn[b])/len(b))[0]
    Z.adam_train(net.params(), grad_fn, len(Zi), hp['steps'], Z.BATCH, hp['lr'], hp['wd'], rng, [True]*3+[False]*3)
    return net, xs, ys


def missing_health(A, idx):
    return 1.0-A.en[idx][:, :, 4]


def build_pool(L, hp_piece):
    """The level-1 pool. L: a 0e-style wired model (its scorer is AIM, its head is MOVE); hp_piece: (net, xs, ys) trained on missing health."""
    return {'AIM': ScorerPiece(L.scorer, L.xa, L.ya, 'AIM'), 'HP': ScorerPiece(*hp_piece, 'HP'), 'NEAR': Near(), 'RAND': Rand(),
            'MOVE': MovePiece(L), 'APPROACH': Approach(), 'DRIFT': Drift()}


# ------------------------------------------------------------------ assemblies

def all_assemblies():
    """Every type-compatible assembly; DRIFT consumes no message, so its message source is fixed to 'ATTACK' (no duplicates)."""
    out = []
    for attack, loop, step in itertools.product(TARGETS, (False, True), STEPS):
        for msg in (MESSAGES if step != 'DRIFT' else ('ATTACK',)):
            out.append((attack, loop, step, msg))
    return out


def label(spec):
    attack, loop, step, msg = spec
    return '%s%s>%s<%s' % (attack, '+self' if loop else '', step, msg)


def make_policy(pool, spec):
    """Closed-loop factory: make(rng) -> policy(own, enemies, unit). The self-loop keeps each unit's previous target while it lives (memory per unit, reset each episode)."""
    attack, loop, step, msg = spec

    def make(rng):
        memory = {}

        def policy(own, enemies, unit):
            A = Z.Arrays({'own': own[None], 'enemies': enemies[None]})
            t = int(pool[attack].choose(A, rng)[0])
            if loop and unit in memory and enemies[memory[unit], 0] > 0:
                t = memory[unit]
            memory[unit] = t
            E.validate_choice(A, np.array([t]))
            m = t if msg == 'ATTACK' else int(pool[msg].choose(A, rng)[0])
            rel = enemies[m, 1:3][None]
            s = E.validate_vectors(pool[step].step(A, rel), 1, 'the step')[0]
            return s, t, False
        return policy
    return make


def unit_policy(fn):
    """Adapt a stateless (own, enemies) policy (teacher, rush) to the unit-aware play loop."""
    def make(rng):
        return lambda own, enemies, unit: fn(own, enemies)
    return make


def play_episode(make, rng_policy, mix_a, opponent, mix_b, rng, world_fn):
    policy = make(rng_policy)
    world = world_fn(mix_a, mix_b, rng)
    while not world.done:
        actions = [[None]*N, [None]*N]
        for i in range(N):
            actions[0][i] = (np.zeros(2), 0, False) if not world.alive[0, i] else policy(*world.observe(0, i), i)
            actions[1][i] = (np.zeros(2), 0, False) if not world.alive[1, i] else opponent(*world.observe(1, i))
        world.step(actions)
    return world.score(0)


def play_cell(make, opponent, entropy, seed, episodes, roster, world_fn, mixes):
    """Paired roster `roster` (selection and confirmation use different keys): episode i draws mixes and world from stream(entropy, roster, seed, opp, i), the policy's own
    randomness from stream(entropy, roster+1, seed, opp, i)."""
    code = OPP_CODE[opponent]
    scores = []
    for i in range(episodes):
        rng = stream(entropy, roster, seed, code, i)
        mix_a = tuple(rng.permutation(mixes[int(rng.integers(len(mixes)))]))
        mix_b = tuple(rng.permutation(mixes[int(rng.integers(len(mixes)))]))
        scores.append(play_episode(make, stream(entropy, roster+1, seed, code, i), mix_a, T.OPPONENTS[opponent], mix_b, rng, world_fn))
    return float(np.mean(scores))


# ------------------------------------------------------------------ the fixed procedure

def neighbours(spec):
    """Every single change: swap the attack producer, toggle the self-loop, swap the step producer, rewire the message (type-compatible only)."""
    attack, loop, step, msg = spec
    out = [(a, loop, step, msg) for a in TARGETS if a != attack]
    out.append((attack, not loop, step, msg))
    for s in STEPS:
        if s != step:
            out.append((attack, loop, s, 'ATTACK' if s == 'DRIFT' else msg))
    if step != 'DRIFT':
        out += [(attack, loop, step, m) for m in MESSAGES if m != msg]
    return out


def greedy(table, margin, start=DEFAULT):
    """From `start`, take the best single change if it beats the current assembly by more than `margin`; stop when none does. table: spec -> score."""
    path, cur = [start], start
    while True:
        best = max(neighbours(cur), key=lambda s: table[s])
        if table[best]-table[cur] > margin:
            cur = best
            path.append(cur)
        else:
            return path


def pairs_table(table):
    """The owner's level-1 table: every coherent pair (target producer feeding both the attack and the step producer), with and without the self-loop."""
    return {(a, s, loop): table[(a, loop, s, 'ATTACK')] for a in TARGETS for s in STEPS for loop in (False, True)}
