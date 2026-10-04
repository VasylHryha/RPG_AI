"""Mechanics checks for experiment 0e (ze_core.py, ze_flat.py). Run once from the repository root after the code batch:

    .venv/bin/python -m pytest -q -p no:cacheprovider evidence/tactical_composition_demo/test_ze.py
"""
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tactics as T  # noqa: E402
import ze_core as E  # noqa: E402
import ze_flat as F  # noqa: E402
import zd_models as Z  # noqa: E402
from tcd_common import metrics  # noqa: E402


@pytest.fixture(scope='module')
def world():
    rng = np.random.default_rng(4)
    pool = T.collect(rng, 10, T.SEEN_MIXES)
    lab = T.labels(pool)
    return pool, lab, Z.Arrays(pool, lab)


@pytest.fixture(scope='module')
def pieces(world):
    _, _, A = world
    idx = Z.source_states(A.n, 600, np.random.default_rng(1))
    c = Z.fit_composed(A, idx, {'hidden': 8, 'lr': 0.01, 'wd': 0.0, 'steps': 300}, np.random.default_rng(2))
    return c


def test_vectorized_teacher_scores_and_the_oracle_assembly_equal_the_scalar_teacher(world):
    pool, _, A = world
    s = E.teacher_scores_batch(A)
    for k in (0, 5, A.n//2, A.n-1):
        assert np.array_equal(s[k], T.teacher_scores(pool['own'][k], pool['enemies'][k]))
    chosen, step, applied = E.Assembly(E.AimOracle(), E.MoveOracle()).act(A, np.random.default_rng(0))
    for k in (0, 5, A.n//2, A.n-1):
        mv, tgt, _ = T.teacher_policy(pool['own'][k], pool['enemies'][k])
        assert tgt == chosen[k] and np.array_equal(mv, step[k])
    assert not applied.any()


def test_joint3_matches_the_registered_joint_action_and_its_strata_are_disjoint(world):
    pool, lab, A = world
    rng = np.random.default_rng(3)
    chosen = np.array([int(rng.choice(np.flatnonzero(a))) for a in A.alive])
    step = rng.normal(0, 1, (A.n, 2))
    step[::3] = Z.teacher_move_batch(A.REL[np.arange(A.n), chosen], A.PREF)[::3]
    mine, ref = E.joint3(chosen, step, A), metrics.joint_action(chosen, step, pool, lab, min_stratum=1)
    assert mine['a_joint'] == pytest.approx(ref['a_joint']) and mine['a_target_admissible'] == pytest.approx(ref['a_target_admissible'])
    assert mine['n_hold']+mine['n_approach']+mine['n_backoff'] == mine['n_multi']
    assert mine['n_backoff'] == ref['n_stratum_backoff'] and mine['n_hold'] == ref['n_stratum_hold']


def test_each_wire_kind_does_what_its_contract_says(world):
    _, _, A = world
    rows = np.arange(A.n)
    chosen = E.AimOracle().choose(A)
    rng = np.random.default_rng(5)
    intact, app = E.Wire()(A, chosen, rng)
    assert np.array_equal(intact, A.REL[rows, chosen]) and not app.any()
    for kind in ('relabel', 'sham'):
        msg, _ = E.Wire(kind)(A, chosen, np.random.default_rng(6))
        assert np.array_equal(msg, intact), kind                                   # semantics-preserving positive controls
    msg, app = E.Wire('default')(A, chosen, rng)
    assert np.array_equal(msg, A.REL[rows, E.nearest_living(A)])
    msg, app = E.Wire('wrong')(A, chosen, rng)
    multi = A.alive.sum(1) > 1
    assert app[multi].all() and not app[~multi].any()
    other = np.array([np.flatnonzero((A.REL[k] == msg[k]).all(1))[0] for k in rows])
    assert A.alive[rows, other].all() and (other[multi] != chosen[multi]).all()
    assert np.array_equal(E.Wire('zero')(A, chosen, rng)[0], np.zeros_like(intact))
    assert np.allclose(E.Wire('scale', 2.0)(A, chosen, rng)[0], 2*intact)
    assert np.array_equal(E.Wire('reverse')(A, chosen, rng)[0], -intact)
    noisy, _ = E.Wire('noise', 0.1, ref=3.0)(A, chosen, rng)
    d = np.hypot(*(noisy-intact).T)
    assert d.max() <= 0.3+1e-12 and d.mean() > 0.05
    msg, hit = E.Wire('wrongfrac', 0.5)(A, chosen, np.random.default_rng(7))
    assert 0.3 < hit[multi].mean() < 0.7 and np.array_equal(msg[~hit], intact[~hit])


def test_learned_pieces_through_the_intact_wire_reproduce_the_wired_model(world, pieces):
    _, _, A = world
    c = pieces
    chosen, step, _ = E.Assembly(E.AimWired(c, 'L'), E.MoveWired(c, 'L')).act(A, np.random.default_rng(0))
    ref_chosen, ref_step = c.act(A)
    assert np.array_equal(chosen, ref_chosen) and np.allclose(step, ref_step)


def test_play_episode_matches_the_recorded_play_and_cells_are_paired_and_deterministic():
    rng1, rng2 = np.random.default_rng(9), np.random.default_rng(9)
    mixes = (T.SEEN_MIXES[0], T.SEEN_MIXES[3])
    score, outcome = E.play_episode(T.teacher_policy, mixes[0], T.rush_policy, mixes[1], rng1)
    assert score == T.play(T.teacher_policy, mixes[0], T.rush_policy, mixes[1], rng2) and outcome in ('win', 'loss', 'draw', 'timeout')
    entropy = 2**90+21
    oracle = E.Assembly(E.AimOracle(), E.MoveOracle())
    a = E.play_cell(oracle.policy, 'rush', entropy, 0, 4)
    b = E.play_cell(oracle.policy, 'rush', entropy, 0, 4)
    assert a == b and a['win']+a['loss']+a['draw']+a['timeout'] == 4
    teacher = E.play_cell(lambda rng: T.teacher_policy, 'rush', entropy, 0, 4)
    assert teacher['score'] == a['score']                                          # the vectorized oracle assembly plays exactly as the scalar teacher


def test_exact_intervals_against_known_values():
    lo, hi, j = E.median_interval(np.arange(30), 0.05)
    assert (lo, hi, j) == (9.0, 20.0, 10)                                          # ranks 10 and 21 for n = 30 at 95%
    assert E.median_interval(np.arange(4), 0.05)[2] == 0                          # too few seeds: abstain
    assert E.clopper_pearson(30, 30, 0.0125)[0] == pytest.approx(0.00625**(1/30), abs=1e-6)
    assert E.clopper_pearson(0, 10, 0.05)[1] == pytest.approx(1-0.025**(1/10), abs=1e-6)
    lo, hi = E.clopper_pearson(15, 30, 0.05)
    assert 0.31 < lo < 0.32 and 0.68 < hi < 0.69
    x = np.linspace(0, 1, 30)
    l25, u25 = E.quantile_bounds(x, 0.25, 0.05)
    assert l25 < 0.25 < u25
    ilo, ihi = E.iqr_bounds(x, 0.05)
    assert 0 <= ilo < 0.5 < ihi
    assert E.ratio_bounds((0.1, 0.2), (0.0, 0.3)) is None and E.ratio_bounds((0.1, 0.2), (0.2, 0.4)) == (0.25, 1.0)
    assert E.above(0.06, 0.1, 0.05) == 'SUPPORTED' and E.above(0.05, 0.1, 0.05) == 'INDETERMINATE' and E.above(-0.1, 0.04, 0.05) == 'REFUTED'
    assert E.below(0.0, 0.02, 0.03) == 'SUPPORTED' and E.below(0.0, 0.03, 0.03) == 'INDETERMINATE' and E.below(0.04, 0.05, 0.03) == 'REFUTED'


def test_deep_network_backward_matches_finite_differences():
    rng = np.random.default_rng(2)
    net = F.DeepNet(5, 4, 3, 2, rng)
    X, Y = rng.normal(size=(7, 5)), rng.normal(size=(7, 2))

    def loss():
        return float(np.sum((net.forward(X)[0]-Y)**2))
    out, hs = net.forward(X)
    grads = net.backward(hs, 2.0*(out-Y))
    for p, g in zip(net.params(), grads):
        num = np.zeros_like(p)
        it = np.nditer(p, flags=['multi_index'])
        for _ in it:
            i = it.multi_index
            old = p[i]
            p[i] = old+1e-6
            hi = loss()
            p[i] = old-1e-6
            lo = loss()
            p[i] = old
            num[i] = (hi-lo)/2e-6
        assert np.allclose(g, num, rtol=1e-5, atol=1e-7)


@pytest.mark.parametrize('head', ['mse', 'disc', 'perslot'])
def test_flat_plus_heads_train_and_act_validly(world, head):
    _, _, A = world
    idx = Z.source_states(A.n, 500, np.random.default_rng(1))
    m = F.FlatPlus(head).fit(A, idx, {'hidden': 16, 'depth': 3, 'lr': 0.003, 'wd': 1e-4, 'steps': 200}, np.random.default_rng(3))
    chosen, step = m.act(A)
    assert chosen.shape == (A.n,) and step.shape == (A.n, 2) and np.isfinite(step).all() and A.alive[np.arange(A.n), chosen].all()
    assert 0.0 <= E.joint3(chosen, step, A)['a_joint'] <= 1.0
    if head == 'perslot':
        other = (chosen+1) % 3
        assert not np.allclose(m.step_for(A, other), step) and m.oracle_queries == int(A.alive[idx].sum())   # conditioned on the slot; counterfactual queries counted
    else:
        assert np.array_equal(m.step_for(A, (chosen+1) % 3), step) and m.oracle_queries == 0                  # unconditional


def test_degraded_pieces_are_really_degraded(world):
    _, _, A = world
    oracle = E.joint3(*E.Assembly(E.AimOracle(), E.MoveOracle()).act(A, np.random.default_rng(0))[:2], A)
    nearest = E.joint3(*E.Assembly(E.AimNearest(), E.MoveOracle()).act(A, np.random.default_rng(0))[:2], A)
    approach = E.joint3(*E.Assembly(E.AimOracle(), E.MoveApproach()).act(A, np.random.default_rng(0))[:2], A)
    assert oracle['a_joint'] == 1.0 and nearest['a_joint'] < 0.95 and approach['a_hold'] == 0.0 and approach['a_approach'] == 1.0
