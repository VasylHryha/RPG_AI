"""Mechanics checks for the tactical sandbox, teacher, data and pieces. Known-answer cases, not the scientific predictions.

Run once from the repository root after the code is final:
    .venv/bin/python -m pytest -q -p no:cacheprovider evidence/tactical_composition_demo/test_tactics.py
"""
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tactics as T  # noqa: E402


def world(mix_a=(T.FIGHTER, T.ARCHER, T.MAGE), mix_b=(T.FIGHTER, T.ARCHER, T.MAGE), seed=0):
    return T.World(mix_a, mix_b, np.random.default_rng(seed))


def idle():
    return [[(np.zeros(2), 0, False)]*3, [(np.zeros(2), 0, False)]*3]


def test_world_is_deterministic_and_stays_inside_the_arena():
    a, b = world(seed=5), world(seed=5)
    assert np.array_equal(a.pos, b.pos)
    rng = np.random.default_rng(1)
    for _ in range(50):
        acts = [[T.random_action(rng, a.observe(t, i)[1]) if a.alive[t, i] else (np.zeros(2), 0, False) for i in range(3)] for t in (0, 1)]
        a.step(acts)
    assert (a.pos >= 0).all() and (a.pos <= T.ARENA).all()


def test_health_never_rises_and_dead_units_stay_dead_and_the_episode_ends():
    rng = np.random.default_rng(2)
    w = world(seed=3)
    last = w.hp.copy()
    while not w.done:
        acts = [[T.teacher_policy(*w.observe(t, i)) if w.alive[t, i] else (np.zeros(2), 0, False) for i in range(3)] for t in (0, 1)]
        w.step(acts)
        assert (w.hp <= last+1e-12).all() and ((last > 0) | (w.hp == 0)).all()
        last = w.hp.copy()
    assert w.t <= T.MAX_TICKS and w.score(0) in (0.0, 0.5, 1.0)


def test_speed_limit_and_move_clipping():
    w = world()
    before = w.pos.copy()
    acts = idle()
    acts[0][0] = (np.array([30.0, 0.0]), 0, False)     # an absurd move is clipped to unit length
    w.step(acts)
    moved = np.hypot(*(w.pos[0, 0]-before[0, 0]))
    assert moved <= w.speed[0, 0]+1e-9 and moved > 0.9*w.speed[0, 0]


def test_basic_attack_needs_range_and_cooldown():
    w = world(mix_a=(T.ARCHER,)*3, mix_b=(T.FIGHTER,)*3)
    w.pos[0, 0], w.pos[1, 0] = [10.0, 10.0], [10.0, 14.0]     # 4 apart: inside archer range 6, outside fighter range 1.5
    acts = idle()
    acts[0][0] = (np.zeros(2), 0, False)
    hp = w.hp[1, 0]
    w.step(acts)
    assert w.hp[1, 0] == hp-T.UNIT_TYPES[T.ARCHER]['damage']
    w.step(acts)                                            # on cooldown now
    assert w.hp[1, 0] == hp-T.UNIT_TYPES[T.ARCHER]['damage']
    assert w.hp[0, 0] == w.hpmax[0, 0]                      # the fighter could not reach


def test_burst_hits_everything_in_the_radius_once_and_goes_on_cooldown():
    w = world(mix_a=(T.MAGE, T.ARCHER, T.ARCHER), mix_b=(T.FIGHTER,)*3)
    w.pos[0, 0] = [10.0, 10.0]
    w.pos[1, 0], w.pos[1, 1], w.pos[1, 2] = [13.0, 10.0], [13.5, 10.5], [16.0, 16.0]   # two inside the blast, one far away
    acts = idle()
    acts[0][0] = (np.zeros(2), 0, True)
    hp = w.hp.copy()
    w.step(acts)
    assert w.hp[1, 0] == hp[1, 0]-T.BURST['damage'] and w.hp[1, 1] == hp[1, 1]-T.BURST['damage'] and w.hp[1, 2] == hp[1, 2]
    w.step(acts)                                            # burst on cooldown; a basic attack lands instead
    assert w.hp[1, 0] == hp[1, 0]-T.BURST['damage']-T.UNIT_TYPES[T.MAGE]['damage'] or w.hp[1, 0] == hp[1, 0]-T.BURST['damage']


def test_observation_shapes_and_values():
    w = world()
    own, enemies = w.observe(0, 2)
    assert own.shape == (T.OWN_DIM,) and enemies.shape == (T.N_UNITS, T.ENEMY_DIM)
    assert own[7] == 1.0 and own[0] == 1.0 and (enemies[:, 0] == 1).all()
    assert np.allclose(enemies[:, 3], np.hypot(enemies[:, 1], enemies[:, 2]))
    assert T.mono_features(own, enemies).shape == (T.MONO_IN,)
    assert T.ability_features(own, enemies, 0).shape == (T.ABILITY_DIM,)
    assert T.aim_features(own, enemies, 0).shape == (T.AIM_DIM,) and T.move_features(enemies[0, 1:3], own[4]).shape == (T.MOVE_DIM,)


def test_teacher_rules_known_answers():
    own = np.array([1.0, 0.3, 6.0, 7.0, 5.0, 1.0, 1.0, 0.0])
    enemies = np.array([[1, 10.0, 0.0, 10.0, 1.0, 1.5, 9.0], [1, 3.0, 0.0, 3.0, 0.2, 1.5, 9.0], [0, 1.0, 0.0, 1.0, 0.1, 1.5, 9.0]])
    assert int(np.argmax(T.teacher_scores(own, enemies))) == 1 and T.teacher_scores(own, enemies)[2] == -9.0
    assert np.allclose(T.teacher_move(np.array([10.0, 0.0]), 5.0), [1, 0])           # too far: close in
    assert np.allclose(T.teacher_move(np.array([2.0, 0.0]), 5.0), [-1, 0])           # too close for a ranged unit: back off
    assert np.allclose(T.teacher_move(np.array([5.0, 0.0]), 5.0), [0, 0])            # at the preferred range: hold
    assert np.allclose(T.teacher_move(np.array([1.0, 0.0]), 1.2), [0, 0])            # a fighter never backs off
    mage = np.array([1.0, 0.25, 4.0, 5.0, 3.5, 1.0, 1.0, 1.0])
    cluster = np.array([[1, 3.0, 0.0, 3.0, 1, 1.5, 9], [1, 3.5, 0.5, 3.5, 1, 1.5, 9], [1, 12.0, 8.0, 14.0, 1, 1.5, 9]])
    assert T.teacher_fire(mage, cluster, 0) and not T.teacher_fire(mage, cluster, 2)
    lone = np.array([[1, 3.0, 0.0, 3.0, 1.0, 1.5, 9], [1, 12.0, 8.0, 14.0, 1.0, 1.5, 9], [1, -9.0, 8.0, 12.0, 1.0, 1.5, 9]])
    assert not T.teacher_fire(mage, lone, 0)                                       # one healthy enemy alone: no burst
    lone[0, 4] = 0.2
    assert T.teacher_fire(mage, lone, 0)                                           # one nearly dead enemy: finisher
    lone[0, 3] = 6.0
    assert not T.teacher_fire(mage, lone, 0)                                       # outside burst range
    mage_not_ready = mage.copy()
    mage_not_ready[6] = 0.0
    assert not T.teacher_fire(mage_not_ready, cluster, 0) and not T.teacher_fire(own, cluster, 0)


def test_baselines_act_on_alive_enemies_only():
    own = np.array([1.0, 0.3, 6.0, 7.0, 5.0, 1.0, 1.0, 0.0])
    enemies = np.array([[0, 1.0, 0.0, 1.0, 1.0, 1.5, 9.0], [1, 8.0, 0.0, 8.0, 1.0, 1.5, 9.0], [1, 4.0, 0.0, 4.0, 1.0, 1.5, 9.0]])
    for policy in (T.teacher_policy, T.rush_policy, T.kiter_policy, T.make_random_policy(np.random.default_rng(0))):
        for _ in range(10):
            assert enemies[policy(own, enemies)[1], 0] > 0
    assert T.rush_policy(own, enemies)[1] == 2


def test_collection_labels_and_datasets_have_the_right_shapes():
    rng = np.random.default_rng(7)
    pool = T.collect(rng, 6, T.SEEN_MIXES)
    lab = T.labels(pool)
    n = len(pool['own'])
    assert lab['scores'].shape == (n, 3) and lab['move'].shape == (n, 2) and lab['fire'].shape == (n,)
    assert (pool['enemies'][np.arange(n), lab['target'], 0] > 0).all()                 # the teacher never picks a dead enemy
    data = T.piece_datasets(pool, lab, 50, 50, np.random.default_rng(8))
    assert data['AIM'][0].shape[1] == T.AIM_DIM and data['MOVE'][0].shape == (50, T.MOVE_DIM) and data['MOVE'][1].shape == (50, 2)
    assert 'ABILITY' not in data and not lab['fire'].any()                          # Stage 0: no burst anywhere
    assert T.piece_datasets(pool, lab, 20, 20, np.random.default_rng(8), n_ability=5)['ABILITY'][0].shape[1] == T.ABILITY_DIM
    X, Y = T.mono_dataset(pool, lab, 40, np.random.default_rng(9))
    assert X.shape == (40, T.MONO_IN) and Y.shape == (40, T.MONO_OUT)


def test_unseen_type_is_really_unseen():
    assert all(T.SKIRMISHER not in mix for mix in T.SEEN_MIXES)
    assert all(T.SKIRMISHER in mix for mix in T.UNSEEN_MIXES)
    pool = T.collect(np.random.default_rng(11), 20, T.SEEN_MIXES)
    combos = {(round(float(r), 2), round(float(p), 2)) for r, p in zip(pool['own'][:, 2], pool['own'][:, 4])}
    new = T.UNIT_TYPES[T.SKIRMISHER]
    assert (new['range'], new['pref']) not in combos                                     # no logged state has the new range-with-preferred-range


def test_mlp_learns_a_known_function_with_multiple_outputs():
    rng = np.random.default_rng(3)
    X = rng.random((2000, 3))
    Y = np.c_[X[:, 0]+X[:, 1], X[:, 2]**2]
    net = T.MLP(3, 16, 2, np.random.default_rng(4)).fit(X, Y, np.random.default_rng(5), 1500)
    Xt = rng.random((500, 3))
    assert np.sqrt(np.mean((net.predict(Xt)-np.c_[Xt[:, 0]+Xt[:, 1], Xt[:, 2]**2])**2)) < 0.05
    assert T.MLP.parameter_count(3, 16, 2) == sum(w.size for w in net.W)+sum(b.size for b in net.b)


def test_composed_and_monolith_policies_return_valid_actions():
    rng = np.random.default_rng(31)
    pool = T.collect(rng, 6, T.SEEN_MIXES)
    lab = T.labels(pool)
    data = T.piece_datasets(pool, lab, 200, 200, rng)
    aim = T.MLP(T.AIM_DIM, 8, 1, rng).fit(*data['AIM'], rng, 50)
    move = T.MLP(T.MOVE_DIM, 8, 2, rng).fit(*data['MOVE'], rng, 50)
    X, Y = T.mono_dataset(pool, lab, 200, rng)
    mono = T.MLP(T.MONO_IN, 8, T.MONO_OUT, rng).fit(X, Y, rng, 50)
    own, enemies = T.World((0, 1, 2), (0, 1, 2), rng).observe(0, 0)
    enemies[1, 0] = 0.0                                                              # one dead enemy: never chosen
    for policy in (T.composed_policy(aim, move), T.mono_policy(mono)):
        move_vec, target, fire = policy(own, enemies)
        assert target in (0, 2) and np.isfinite(move_vec).all() and fire is False
    assert T.play(T.composed_policy(aim, move), (0, 1, 2), T.rush_policy, (0, 1, 1), np.random.default_rng(32)) in (0.0, 0.5, 1.0)
    assert set(T.fidelity({'AIM': aim, 'MOVE': move}, pool, lab)) >= {'aim_top1', 'aim_nearest_enemy_floor', 'move_median_angle_deg'}


def test_play_is_repeatable_and_policies_run():
    a = T.play(T.teacher_policy, (T.FIGHTER, T.ARCHER, T.MAGE), T.rush_policy, (T.FIGHTER, T.ARCHER, T.ARCHER), np.random.default_rng(21))
    b = T.play(T.teacher_policy, (T.FIGHTER, T.ARCHER, T.MAGE), T.rush_policy, (T.FIGHTER, T.ARCHER, T.ARCHER), np.random.default_rng(21))
    assert a == b and a in (0.0, 0.5, 1.0)
    assert 0.0 <= T.win_score(T.rush_policy, T.SEEN_MIXES, T.kiter_policy, np.random.default_rng(22), 3) <= 1.0


def test_move_metrics_see_back_off_and_hold_errors():
    rel = np.array([[10.0, 0.0], [2.0, 0.0], [5.0, 0.0], [10.0, 0.0]])
    truth = np.array([[1.0, 0.0], [-1.0, 0.0], [0.0, 0.0], [1.0, 0.0]])
    good = T.move_metrics(truth.copy(), truth, rel)
    assert good['move_median_angle_deg'] < 0.01 and good['move_hold_agreement'] == 1.0 and good['move_backoff_median_angle_deg'] < 0.01
    never_backs_off = truth.copy()
    never_backs_off[1] = [1.0, 0.0]
    bad = T.move_metrics(never_backs_off, truth, rel)
    assert bad['move_backoff_median_angle_deg'] > 170 and bad['move_median_angle_deg'] < 0.01      # the median alone would not see it
    assert bad['move_share_backoff'] == 0.25


def test_new_unit_type_is_a_new_combination_of_in_range_inputs():
    new = T.UNIT_TYPES[T.SKIRMISHER]
    seen = [T.UNIT_TYPES[t] for t in (T.FIGHTER, T.ARCHER, T.MAGE)]
    for key in ('speed', 'range', 'damage', 'pref', 'hp'):
        values = [u[key] for u in seen]
        assert min(values) <= new[key] <= max(values), key                                          # every input inside the trained span
    assert not any(u['range'] == new['range'] and u['pref'] == new['pref'] for u in seen)         # but the combination is new
    assert all(abs(u['pref']-new['pref']) > 0.2 or abs(u['range']-new['range']) > 0.2 for u in seen)


def test_mono_fidelity_reports_agreement_with_the_teacher():
    rng = np.random.default_rng(41)
    pool = T.collect(rng, 6, T.SEEN_MIXES)
    lab = T.labels(pool)
    X, Y = T.mono_dataset(pool, lab, len(pool['own']), rng)
    model = T.MLP(T.MONO_IN, 24, T.MONO_OUT, rng).fit(X, Y, rng, 1500)
    f = T.mono_fidelity(model, pool, lab)
    assert 0.5 < f['aim_top1'] <= 1.0 and f['move_median_angle_deg'] < 45
