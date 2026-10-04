"""Experiment 0e (replacement and connection, PROPOSAL_0E.md) core: pieces, the AIM -> MOVE wire, assemblies, closed-loop play on paired episode rosters,
joint-action fidelity with disjoint strata, and exact intervals. Exploratory; NOT a milestone, NOT C6 evidence.

A NEW file. It imports the frozen `tactics.py`, `zd_models.py` and `tcd_common` read-only and changes none of them.

The connection under test (PROPOSAL_0E.md section 2): AIM emits the identity of a living enemy slot in one observation snapshot; the connector gathers that enemy's
relative position (arena units, own frame); MOVE receives that message and the unit's own preferred range and emits a step. The attack always uses the enemy AIM chose;
wire faults change only the message MOVE receives.
"""
import math

import numpy as np

from tcd_common import PARENT  # noqa: F401  (puts this folder on sys.path)
import tactics as T
import zd_models as Z
from tcd_common.fileio import stream

N = T.N_UNITS
HOLD = 0.5
ANGLE_OK = 10.0
OPP_CODE = {'rush': 0, 'kiter': 1}


# ------------------------------------------------------------------ the teacher, vectorized

def teacher_scores_batch(A):
    """`tactics.teacher_scores` for every state at once (tested equal to the scalar rule)."""
    e, own = A.en, A.own
    s = (1.0-e[:, :, 4])+0.6*(e[:, :, 3] <= own[:, 2:3])-0.08*e[:, :, 3]
    return np.where(A.alive, s, -9.0)


def nearest_living(A):
    return np.argmin(np.where(A.alive, A.en[:, :, 3], np.inf), axis=1)


# ------------------------------------------------------------------ AIM pieces: choose(A) -> one living enemy slot per state

class AimOracle:
    """The teacher's targeting; `scorer` is a batch scoring function (default: the original sandbox's teacher)."""
    name, kind = 'O', 'scripted'

    def __init__(self, scorer=None):
        self.scorer = scorer or teacher_scores_batch

    def choose(self, A):
        return np.argmax(self.scorer(A), axis=1)


class AimNearest:
    name, kind = 'D', 'degraded'

    def choose(self, A):
        return nearest_living(A)


class AimWired:
    """The scorer branch of a wired model (L: separately taught pieces; J: the jointly trained conditional policy)."""
    kind = 'learned'

    def __init__(self, model, name):
        self.model, self.name = model, name

    def choose(self, A):
        return Z.masked_argmax(self.model.scores(A), A.alive)


class AimFlatOutput:
    """Hybrid diagnostic: the target output of a whole flat policy (its argmax over enemy slots)."""
    kind = 'hybrid'

    def __init__(self, model, name):
        self.model, self.name = model, name

    def choose(self, A):
        return self.model.act(A)[0]


# ------------------------------------------------------------------ MOVE pieces: step(A, rel) -> one step per state, from the message rel

class MoveOracle:
    name, kind = 'O', 'scripted'

    def step(self, A, rel):
        return Z.teacher_move_batch(rel, A.PREF)


class MoveApproach:
    """Degraded: always walk straight at the message position (never holds, never backs off)."""
    name, kind = 'D', 'degraded'

    def step(self, A, rel):
        d = np.hypot(rel[:, 0], rel[:, 1])
        return np.where((d > 1e-9)[:, None], rel/np.maximum(d, 1e-9)[:, None], 0.0)


class MoveWired:
    """The step-head branch of a wired model, fed the message (the gathered relative position) and own preferred range."""
    kind = 'learned'

    def __init__(self, model, name):
        self.model, self.name = model, name

    def step(self, A, rel):
        out, _ = self.model.head.forward(self.model.xm.f(A.move_input(rel, A.PREF)))
        return self.model.ym.inv(out)


class MoveFlatOutput:
    """Hybrid diagnostic: the step output of a whole flat policy. It IGNORES the message (a flat model cannot be told which enemy to act on): an action-channel
    replacement, not a target-conditioned module swap."""
    kind = 'hybrid'

    def __init__(self, model, name):
        self.model, self.name = model, name

    def step(self, A, rel):
        return self.model.act(A)[1]


# ------------------------------------------------------------------ the wire: chosen slot -> message for MOVE

def _other_living(A, chosen):
    """The next living slot after `chosen`, cyclically; equal to `chosen` when it is the only living enemy (then the fault is not applicable)."""
    n = A.n
    out = chosen.copy()
    for step in (1, 2):
        cand = (chosen+step) % N
        take = (out == chosen) & A.alive[np.arange(n), cand]
        out = np.where(take, cand, out)
    return out


class Wire:
    """kind: intact | default | wrong | zero | noise (value = radius as a fraction of the reference distance) | wrongfrac (value = probability) | scale (value = factor)
    | reverse (directed control: the opposite direction) | relabel (consistent encode/decode through a random slot permutation: must equal intact) | sham (an
    order change at a place MOVE never reads: must equal intact). Returns (message, applied mask)."""

    def __init__(self, kind='intact', value=None, ref=1.0):
        self.kind, self.value, self.ref = kind, value, ref

    @property
    def label(self):
        return self.kind if self.value is None else '%s_%g' % (self.kind, self.value)

    def __call__(self, A, chosen, rng):
        n = A.n
        rows = np.arange(n)
        rel = A.REL[rows, chosen]
        k, v = self.kind, self.value
        applied = np.ones(n, bool)
        if k in ('intact', 'sham'):
            if k == 'sham':
                rng.permutation(N)                     # the draw happens; nothing MOVE reads changes
            return rel, np.zeros(n, bool) if k == 'intact' else applied
        if k == 'default':
            other = nearest_living(A)
            return A.REL[rows, other], other != chosen
        if k == 'wrong':
            other = _other_living(A, chosen)
            return A.REL[rows, other], other != chosen
        if k == 'wrongfrac':
            other = _other_living(A, chosen)
            hit = (rng.random(n) < v) & (other != chosen)
            return np.where(hit[:, None], A.REL[rows, other], rel), hit
        if k == 'zero':
            return np.zeros_like(rel), applied
        if k == 'noise':
            r = v*self.ref*np.sqrt(rng.random(n))
            a = rng.uniform(0, 2*np.pi, n)
            return rel+np.stack([r*np.cos(a), r*np.sin(a)], axis=1), applied & (v > 0)
        if k == 'scale':
            return rel*v, applied & (v != 1)
        if k == 'reverse':
            return -rel, applied
        if k == 'relabel':
            perm = np.array([rng.permutation(N) for _ in range(n)])         # encode: slot j is published as perm[j]
            inv = np.argsort(perm, axis=1)
            published = perm[rows, chosen]
            decoded = inv[rows, published]                                    # decode with the same convention
            enc_rel = A.REL[rows[:, None], inv]                               # the receiver's view of the enemies in the encoded order
            return enc_rel[rows, perm[rows, decoded]], applied
        raise ValueError('unknown wire kind %r' % k)


# ------------------------------------------------------------------ assemblies

class Assembly:
    def __init__(self, aim, move, wire=None):
        self.aim, self.move, self.wire = aim, move, wire or Wire()

    @property
    def name(self):
        return '%s_%s%s' % (self.aim.name, self.move.name, '' if self.wire.kind == 'intact' else '|'+self.wire.label)

    def act(self, A, rng):
        chosen = self.aim.choose(A)
        rel, applied = self.wire(A, chosen, rng)
        return chosen, self.move.step(A, rel), applied

    def policy(self, rng):
        def policy(own, enemies):
            A = Z.Arrays({'own': own[None], 'enemies': enemies[None]})
            chosen, step, _ = self.act(A, rng)
            return step[0], int(chosen[0]), False
        return policy


# ------------------------------------------------------------------ closed-loop play on a paired episode roster

def play_episode(policy_a, mix_a, opponent, mix_b, rng, world_fn=None):
    """`tactics.play`, also returning the outcome: win, loss, draw (both sides lost their last unit together) or timeout. `world_fn` builds the world (task revision)."""
    world = (world_fn or T.World)(mix_a, mix_b, rng)
    while not world.done:
        actions = [[None]*N, [None]*N]
        for team, policy in ((0, policy_a), (1, opponent)):
            for i in range(N):
                actions[team][i] = (np.zeros(2), 0, False) if not world.alive[team, i] else policy(*world.observe(team, i))
        world.step(actions)
    a, b = world.alive_count(0), world.alive_count(1)
    outcome = 'win' if (a > 0 and b == 0) else 'loss' if (a == 0 and b > 0) else 'draw' if (a == 0 and b == 0) else 'timeout'
    return world.score(0), outcome


def play_cell(make_policy, opponent, entropy, seed, episodes, world_fn=None, mixes=None):
    """The registered roster: episode i of (seed, opponent) draws both mixes and the world from stream(entropy, 7, seed, opp, i); the policy's own randomness (wire
    faults) comes from stream(entropy, 8, seed, opp, i). Every policy therefore meets exactly the same starts."""
    scores, outcomes = [], {'win': 0, 'loss': 0, 'draw': 0, 'timeout': 0}
    code = OPP_CODE[opponent]
    for i in range(episodes):
        rng = stream(entropy, 7, seed, code, i)
        pool = mixes or T.SEEN_MIXES
        mix_a = tuple(rng.permutation(pool[int(rng.integers(len(pool)))]))
        mix_b = tuple(rng.permutation(pool[int(rng.integers(len(pool)))]))
        score, outcome = play_episode(make_policy(stream(entropy, 8, seed, code, i)), mix_a, T.OPPONENTS[opponent], mix_b, rng, world_fn)
        scores.append(score)
        outcomes[outcome] += 1
    return {'score': float(np.mean(scores)), 'episodes': episodes, **outcomes}


# ------------------------------------------------------------------ joint-action fidelity with disjoint strata

def joint3(chosen, step, A, angle_deg=ANGLE_OK):
    """Success on a multi-enemy state: the chosen enemy is tied-best for the teacher AND the step matches the teacher's step toward THAT enemy (hold where it holds,
    otherwise a move within `angle_deg`). Strata are disjoint and defined by the teacher's own step toward its own target: hold, approach, back-off."""
    rows = np.arange(A.n)
    scores = np.where(A.alive, A.scores, -np.inf)
    tied = (scores >= scores.max(1)[:, None]-1e-9) & A.alive
    multi = A.alive.sum(1) > 1
    if not multi.any():
        raise ValueError('no multi-enemy state')
    if not A.alive[rows, chosen].all():
        raise ValueError('a chosen enemy is not alive')
    if not np.isfinite(step).all():
        raise ValueError('non-finite step')
    ok_target = tied[rows, chosen]
    v = Z.teacher_move_batch(A.REL[rows, chosen], A.PREF)
    vh = np.hypot(v[:, 0], v[:, 1]) < HOLD
    ph = np.hypot(step[:, 0], step[:, 1])
    cos = (step*v).sum(1)/(ph*np.hypot(v[:, 0], v[:, 1])+1e-9)
    ang = np.degrees(np.arccos(np.clip(cos, -1, 1)))
    ok_step = np.where(vh, ph < HOLD, (ph >= HOLD) & (ang <= angle_deg))
    ok = ok_target & ok_step
    truth = A.move
    rel_t = A.REL[rows, A.target]
    moving = np.hypot(truth[:, 0], truth[:, 1]) > HOLD
    toward = (truth*rel_t).sum(1) > 0
    strata = {'hold': ~moving, 'approach': moving & toward, 'backoff': moving & ~toward}
    out = {'n_multi': int(multi.sum()), 'n_unique_best': int((multi & (tied.sum(1) == 1)).sum()),
           'a_joint': float(ok[multi].mean()), 'a_target_admissible': float(ok_target[multi].mean()),
           'a_step_given_admissible': float(ok_step[multi & ok_target].mean()) if (multi & ok_target).any() else None}
    for name, m in strata.items():
        mm = m & multi
        out['n_'+name] = int(mm.sum())
        out['a_'+name] = float(ok[mm].mean()) if mm.any() else None
    out['a_macro'] = float(np.mean([out['a_'+s] for s in strata if out['a_'+s] is not None]))
    return out


def move_alone(move, A, angle_deg=ANGLE_OK):
    """MOVE prequalification: success of the step when the message is the teacher's own target (the situation it was taught in), by disjoint stratum."""
    rel = A.REL[np.arange(A.n), A.target]
    return joint3(A.target, move.step(A, rel), A, angle_deg)


# ------------------------------------------------------------------ exact intervals (PROPOSAL_0E.md section 4)

def _binom_cdf(k, n, p):
    """P(X <= k) for X ~ Binomial(n, p)."""
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    return float(sum(math.comb(n, i)*p**i*(1-p)**(n-i) for i in range(k+1)))


def median_interval(x, a):
    """Distribution-free order-statistic interval for the median at error a (two-sided): the largest j with 2 P(Bin(n, 1/2) < j) <= a gives [x_(j), x_(n-j+1)].
    Returns (lo, hi, j); (-inf, inf, 0) if no finite interval has that confidence (abstain)."""
    x = np.sort(np.asarray(x, float))
    n = len(x)
    best = 0
    for j in range(1, n//2+1):
        if 2*_binom_cdf(j-1, n, 0.5) <= a:
            best = j
    if best == 0:
        return -np.inf, np.inf, 0
    return float(x[best-1]), float(x[n-best]), best


def clopper_pearson(k, n, a):
    """Exact two-sided interval for a binomial proportion at error a."""
    def solve(f, target):
        lo, hi = 0.0, 1.0
        for _ in range(80):
            mid = (lo+hi)/2
            if f(mid) > target:
                lo = mid
            else:
                hi = mid
        return (lo+hi)/2
    lower = 0.0 if k == 0 else solve(lambda p: -(1-_binom_cdf(k-1, n, p)), -a/2)
    upper = 1.0 if k == n else solve(lambda p: _binom_cdf(k, n, p), a/2)
    return lower, upper


def quantile_bounds(x, p, a, support=(0.0, 1.0)):
    """Order-statistic confidence bounds for the population p-quantile, each tail at a/4 (so an IQR built from two quantiles has joint error a)."""
    x = np.sort(np.asarray(x, float))
    n = len(x)
    lo_idx = [l for l in range(1, n+1) if _binom_cdf(l-1, n, p) <= a/4]
    hi_idx = [u for u in range(1, n+1) if 1-_binom_cdf(u-1, n, p) <= a/4]
    lo = float(x[max(lo_idx)-1]) if lo_idx else support[0]
    hi = float(x[min(hi_idx)-1]) if hi_idx else support[1]
    return lo, hi


def iqr_bounds(x, a, support=(0.0, 1.0)):
    l25, u25 = quantile_bounds(x, 0.25, a, support)
    l75, u75 = quantile_bounds(x, 0.75, a, support)
    return max(0.0, l75-u25), u75-l25


def ratio_bounds(num, den):
    """Bounds of num/den from intervals (each already at half the error). None if the denominator interval is not strictly positive."""
    if den[0] <= 0:
        return None
    q = [num[0]/den[0], num[0]/den[1], num[1]/den[0], num[1]/den[1]]
    return min(q), max(q)


def above(lo, hi, t):
    """Lower-bound predicate x > t: SUPPORTED if lo > t, REFUTED if hi < t, else INDETERMINATE (equality is INDETERMINATE)."""
    return 'SUPPORTED' if lo > t else 'REFUTED' if hi < t else 'INDETERMINATE'


def below(lo, hi, t):
    """Upper-bound predicate x < t."""
    return 'SUPPORTED' if hi < t else 'REFUTED' if lo > t else 'INDETERMINATE'
