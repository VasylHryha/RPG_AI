"""Mechanics checks for experiment 0f (zf_core.py). Run once after the code batch:

    .venv/bin/python -m pytest -q -p no:cacheprovider evidence/tactical_composition_demo/test_zf.py
"""
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tactics as T  # noqa: E402
import tactics_e2 as T2  # noqa: E402
import zd_models as Z  # noqa: E402
import ze_core as E  # noqa: E402
import zf_core as G  # noqa: E402


@pytest.fixture(scope='module')
def world():
    pool = T2.collect('V3', np.random.default_rng(5), 10)
    A = Z.Arrays(pool, T2.labels('V3', pool))
    idx = np.random.default_rng(1).permutation(A.n)[:800]
    L = Z.fit_composed(A, idx, {'hidden': 8, 'lr': 0.01, 'wd': 0.0, 'steps': 300}, np.random.default_rng(2))
    hp = G.fit_scorer(A, idx, G.missing_health, {'hidden': 8, 'lr': 0.01, 'wd': 0.0, 'steps': 600}, np.random.default_rng(3))
    return A, L, G.build_pool(L, hp)


KW = dict(world_fn=T2.world_fn('V3'), mixes=T2.MIXES)


def test_the_default_assembly_is_exactly_the_rush_rule(world):
    _, _, pool = world
    for opp in ('rush', 'kiter'):
        a = G.play_cell(G.make_policy(pool, G.DEFAULT), opp, 2**90+1, 0, 6, 7, **KW)
        b = G.play_cell(G.unit_policy(T.rush_policy), opp, 2**90+1, 0, 6, 7, **KW)
        assert a == b


def test_the_hand_wired_assembly_acts_as_the_0e_unit(world):
    A, L, pool = world
    ref_chosen, ref_step, _ = E.Assembly(E.AimWired(L, 'L'), E.MoveWired(L, 'L')).act(A, np.random.default_rng(0))
    policy = G.make_policy(pool, G.HAND_WIRED)(np.random.default_rng(0))
    for k in (0, 7, A.n//2, A.n-1):
        s, t, fire = policy(A.own[k], A.en[k], 0)
        assert t == ref_chosen[k] and np.allclose(s, ref_step[k]) and fire is False


def test_the_self_loop_keeps_a_living_target_and_releases_a_dead_one(world):
    A, _, pool = world
    k = int(np.flatnonzero(A.alive.sum(1) == 3)[0])
    own, en = A.own[k], A.en[k].copy()
    policy = G.make_policy(pool, ('RAND', True, 'APPROACH', 'ATTACK'))(np.random.default_rng(0))
    first = policy(own, en, 1)[1]
    assert all(policy(own, en, 1)[1] == first for _ in range(20))                # remembered while alive
    other_unit = [policy(own, en, 2)[1] for _ in range(20)]
    en[first, 0] = 0.0                                                           # the remembered target dies
    after = policy(own, en, 1)[1]
    assert after != first and en[after, 0] > 0
    free = G.make_policy(pool, ('RAND', False, 'APPROACH', 'ATTACK'))(np.random.default_rng(0))
    assert len({free(own, A.en[k], 1)[1] for _ in range(30)}) > 1                # without the loop the random producer wanders
    assert len(set(other_unit)) == 1                                             # memory is per unit


def test_decoys_and_defaults_do_what_they_declare(world):
    A, _, pool = world
    r = pool['RAND'].choose(A, np.random.default_rng(1))
    assert A.alive[np.arange(A.n), r].all()
    assert np.array_equal(pool['DRIFT'].step(A, np.zeros((A.n, 2))), np.tile([1.0, 0.0], (A.n, 1)))
    hp_choice = pool['HP'].choose(A)
    missing = np.where(A.alive, 1.0-A.en[:, :, 4], -np.inf)
    tied_best = missing[np.arange(A.n), hp_choice] >= missing.max(1)-1e-6           # any enemy tied for the most missing health is right
    multi = A.alive.sum(1) > 1
    assert np.mean(tied_best[multi]) > 0.8                                         # the HP piece learned its own job


def test_the_assembly_space_and_the_neighbourhood():
    specs = G.all_assemblies()
    assert len(specs) == len(set(specs)) == 88 and G.DEFAULT in specs and G.HAND_WIRED in specs
    for spec in specs:
        for n in G.neighbours(spec):
            assert n in specs and n != spec
            assert sum(a != b for a, b in zip(spec, n)) <= 2                     # one change (a step swap to DRIFT also resets the message)


def test_greedy_follows_the_best_change_and_stops_at_the_margin():
    specs = G.all_assemblies()
    table = {s: 0.0 for s in specs}
    table[G.DEFAULT] = 0.40
    table[('AIM', False, 'APPROACH', 'ATTACK')] = 0.55
    table[('AIM', False, 'MOVE', 'ATTACK')] = 0.70
    table[('AIM', True, 'MOVE', 'ATTACK')] = 0.715                               # below a 0.02 margin: not taken
    path = G.greedy(table, 0.02)
    assert path == [G.DEFAULT, ('AIM', False, 'APPROACH', 'ATTACK'), ('AIM', False, 'MOVE', 'ATTACK')]
    assert G.greedy(table, 0.01)[-1] == ('AIM', True, 'MOVE', 'ATTACK')
    exact = {s: 0.0 for s in specs}
    exact[G.DEFAULT], exact[('AIM', False, 'APPROACH', 'ATTACK')] = 0.5, 0.75      # exactly representable: a gain equal to the margin is not taken
    assert G.greedy(exact, 0.25) == [G.DEFAULT]
    pairs = G.pairs_table(table)
    assert len(pairs) == 24 and pairs[('AIM', 'MOVE', False)] == 0.70
