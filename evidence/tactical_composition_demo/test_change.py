"""Mechanics checks for the change-cost harness and verdict rules (synthetic rows, guards, one tiny real seed).

Run once from the repository root after the code is final:
    .venv/bin/python -m pytest -q -p no:cacheprovider evidence/tactical_composition_demo/test_change.py
"""
import copy
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import change  # noqa: E402
import tactics as T  # noqa: E402

CFG = dict(change.CONFIG)
GRID = CFG['grid']


A, S = change.AGREE, change.STEP


def row(seed=0, same=0.55, old=0.62, pre=(0.97, 0.85, 0.95), pre_step=(1.5, 10.0, 6.0), composed=(0.80, 0.96, 0.97, 0.97),
        mono_eq=(0.60, 0.70, 0.80, 0.84), mono_large=(0.70, 0.85, 0.92, 0.94), angles=(3.0, 3.0, 3.0, 3.0),
        mono_angles=(20.0, 15.0, 13.0, 12.0), large_angles=(15.0, 10.0, 8.0, 7.0)):
    """Defaults: the wired unit is back within 0.02 of its own pre-change 0.97 at 300 rows; the equal-size big controller (own 0.85) at 3000 rows;
    the large one (own 0.95) at 3000 rows."""
    r = {'seed': seed, 'same_target_teacher1_teacher2_multi': same, 'old_composed_%s_vs_new' % A: old, 'old_mono_eq_%s_vs_new' % A: 0.6, 'seconds': 90.0}
    for prefix, p, ps in zip(('composed', 'mono_eq', 'mono_large'), pre, pre_step):
        r['pre_%s_%s' % (prefix, A)], r['pre_%s_%s' % (prefix, S)] = p, ps
    for prefix, tops, angs in (('composed', composed, angles), ('mono_eq', mono_eq, mono_angles), ('mono_large', mono_large, large_angles)):
        for n, top, ang in zip(GRID, tops, angs):
            r['%s_%d_%s' % (prefix, n, A)], r['%s_%d_%s' % (prefix, n, S)] = top, ang
            r['build_%s_%d' % (prefix, n)], r['train_rmse_%s_%d' % (prefix, n)] = 1.0, 0.1
    for n in GRID:
        r['ft_steps_%d' % n] = 200
        r['composed_%d_tie_share_multi' % n] = 0.1
    for cell, v in (('teacher2', 0.6), ('rush', 0.4), ('composed_old', 0.55), ('mono_eq_old', 0.5)):
        for o in change.OPPONENTS:
            r['score_%s_%s' % (cell, o)] = v
    for n in GRID:
        for cell, v in (('composed_%d' % n, 0.6), ('mono_eq_%d' % n, 0.55)):
            for o in change.OPPONENTS:
                r['score_%s_%s' % (cell, o)] = v
    return r


def verdicts(rows):
    ev = change.evaluate(rows, CFG)
    return {k: v['verdict'] for k, v in ev.items() if 'verdict' in v}, ev


def test_all_supported_when_the_wired_unit_recovers_cheaply_and_the_big_one_slowly():
    v, ev = verdicts([row(s) for s in range(20)])
    assert v == {'C1_the_change_is_real': 'SUPPORTED', 'C2_cheap_change_for_the_wired_unit': 'SUPPORTED',
                 'C3_cheaper_than_retraining_the_big_controller': 'SUPPORTED'}
    c3 = ev['C3_cheaper_than_retraining_the_big_controller']
    assert c3['rows_needed_wired_median'] == 300 and c3['rows_needed_big_equal_median'] == 3000 and c3['rows_needed_big_large_median'] == 3000


def test_the_bar_is_each_designs_own_pre_change_quality_not_an_absolute_number():
    # the equal-size big controller never reached 0.95 even before the change (own 0.85): it must be judged against 0.85, so "infinite rows"
    # cannot come from baseline capacity alone
    rows = [row(s, mono_eq=(0.60, 0.70, 0.80, 0.84), pre=(0.97, 0.85, 0.95)) for s in range(4)]
    assert list(change.rows_needed(rows, 'mono_eq', CFG)) == [3000.0]*4
    rows = [row(s, mono_eq=(0.60, 0.70, 0.80, 0.82), pre=(0.97, 0.85, 0.95)) for s in range(4)]     # 0.82 < 0.85 - 0.02 -> not recovered
    assert np.isinf(change.rows_needed(rows, 'mono_eq', CFG)).all()
    rows = [row(s, mono_eq=(0.60, 0.70, 0.80, 0.84), mono_angles=(20, 15, 13, 14.0), pre_step=(1.5, 10.0, 6.0)) for s in range(4)]       # step 14 > 10 + 3
    assert np.isinf(change.rows_needed(rows, 'mono_eq', CFG)).all()
    d = change.evaluate([row(s) for s in range(20)], CFG)['descriptive']
    assert d['share_of_seeds_meeting_the_absolute_bars_0.95_and_10deg']['mono_eq']['3000'] == 0.0   # reported, not used as the bar


def test_c1_requires_a_real_change_and_gates_c2_in_both_directions():
    assert verdicts([row(same=0.90) for _ in range(20)])[0]['C1_the_change_is_real'] == 'REFUTED'
    assert verdicts([row(same=0.75) for _ in range(20)])[0]['C1_the_change_is_real'] == 'INDETERMINATE'
    assert verdicts([row(old=0.90) for _ in range(20)])[0]['C1_the_change_is_real'] == 'INDETERMINATE'
    for kwargs in ({'same': 0.75}, {'same': 0.90}):                                          # no real change: C2 gets neither credit nor blame
        v = verdicts([row(composed=(0.5, 0.5, 0.5, 0.5), **kwargs) for _ in range(20)])[0]
        assert v['C2_cheap_change_for_the_wired_unit'] == 'INDETERMINATE' and v['C3_cheaper_than_retraining_the_big_controller'] == 'INDETERMINATE'


def test_c2_branches():
    assert verdicts([row(composed=(0.8, 0.90, 0.93, 0.93)) for _ in range(20)])[0]['C2_cheap_change_for_the_wired_unit'] == 'INDETERMINATE'
    assert verdicts([row(composed=(0.7, 0.8, 0.85, 0.85)) for _ in range(20)])[0]['C2_cheap_change_for_the_wired_unit'] == 'REFUTED'      # 0.85 < 0.97 - 0.10
    assert verdicts([row(angles=(3.0, 15.0, 3.0, 3.0)) for _ in range(20)])[0]['C2_cheap_change_for_the_wired_unit'] == 'INDETERMINATE'   # the step must recover too
    mixed = [row(s) for s in range(14)]+[row(s, composed=(0.8, 0.90, 0.98, 0.98)) for s in range(14, 20)]
    assert verdicts(mixed)[0]['C2_cheap_change_for_the_wired_unit'] == 'INDETERMINATE'                   # only 70% of seeds recover at 300 rows


def test_c3_branches():
    v = verdicts([row(mono_eq=(0.86, 0.87, 0.88, 0.89), mono_angles=(3, 3, 3, 3)) for _ in range(20)])[0]
    assert v['C3_cheaper_than_retraining_the_big_controller'] == 'REFUTED'                               # the big one recovers at 100 rows, the wired one at 300
    v = verdicts([row(mono_eq=(0.6, 0.7, 0.86, 0.88), mono_angles=(20, 15, 3, 3)) for _ in range(20)])[0]
    assert v['C3_cheaper_than_retraining_the_big_controller'] == 'SUPPORTED'                             # 1000 rows >= 3 x 300
    v = verdicts([row(mono_eq=(0.6, 0.86, 0.88, 0.89), mono_angles=(20, 3, 3, 3)) for _ in range(20)])[0]
    assert v['C3_cheaper_than_retraining_the_big_controller'] == 'REFUTED'                               # equal: 300 against 300
    v = verdicts([row(mono_eq=(0.6, 0.86, 0.88, 0.89), mono_angles=(20, 3, 3, 3), composed=(0.5, 0.5, 0.97, 0.97)) for _ in range(20)])[0]
    assert v['C3_cheaper_than_retraining_the_big_controller'] == 'INDETERMINATE'                         # the wired unit failed C2: no credit
    v = verdicts([row(mono_eq=(0.6, 0.7, 0.8, 0.84)) for _ in range(20)])[0]
    assert v['C3_cheaper_than_retraining_the_big_controller'] == 'SUPPORTED'                             # 3000 >= 3 x 300, and it did recover within the grid


def test_fine_tuning_schedule_scales_with_the_rows_the_same_for_every_design():
    steps = {n: change.ft_steps(n, CFG) for n in GRID}
    assert steps == {100: 200, 300: 282, 1000: 938, 3000: 2000}
    assert all(steps[a] <= steps[b] for a, b in zip(GRID[:-1], GRID[1:]))


def test_spec_json_matches_the_code_constants():
    spec = json.loads((HERE/'SPEC_CHANGE.json').read_text())
    assert spec['config'] == json.loads(json.dumps(change.CONFIG))
    assert spec['smoke_overrides'] == json.loads(json.dumps(change.SMOKE))


def test_stage0_training_settings_are_the_ones_in_the_stage0_spec():
    stage0 = json.loads((HERE/'SPEC.json').read_text())['config']
    cfg = change.CONFIG
    assert cfg['stage0'] == {k: stage0[k] for k in ('n_aim', 'n_move', 'piece_hidden', 'piece_steps', 'batch', 'lr')}
    assert cfg['mono_equal'] == stage0['monolith'][0] and cfg['mono_large'] == stage0['monolith'][2]


def test_doctrine_two_picks_the_most_dangerous_enemy_and_labels_follow_it():
    own = np.array([1.0, 0.3, 6.0, 7.0, 5.0, 1.0, 1.0, 0.0])
    enemies = np.array([[1, 3.0, 0.0, 3.0, 0.2, 1.5, 9.0], [1, 8.0, 0.0, 8.0, 1.0, 6.0, 5.0], [0, 1.0, 0.0, 1.0, 1.0, 1.5, 12.0]])
    assert int(np.argmax(T.teacher2_scores(own, enemies))) == 0 and T.teacher2_scores(own, enemies)[2] == -9.0
    assert int(np.argmax(T.teacher_scores(own, enemies))) == 0                                     # both like the weak close one here
    enemies[0, 4], enemies[0, 6] = 1.0, 5.0
    enemies[1, 6] = 9.0
    assert int(np.argmax(T.teacher2_scores(own, enemies))) == 1                                    # now the stronger hitter wins
    pool = T.collect(np.random.default_rng(3), 5, T.SEEN_MIXES)
    a, b = T.labels(pool), T.labels(pool, T.teacher2_scores)
    assert (a['target'] != b['target']).any() and (pool['enemies'][np.arange(len(b['target'])), b['target'], 0] > 0).all()
    assert T.teacher2_policy(own, enemies)[1] == 1


def test_fine_tuning_keeps_the_scaling_and_changes_the_weights():
    rng = np.random.default_rng(5)
    X = rng.random((200, 3))
    net = T.MLP(3, 8, 1, rng).fit(X, X[:, :1]*3, rng, 100)
    mx, my = net.mx.copy(), net.my.copy()
    tuned = copy.deepcopy(net).fit(X, X[:, :1]*5, rng, 50, 32, 0.002, keep_scaling=True)
    assert np.array_equal(tuned.mx, mx) and np.array_equal(tuned.my, my) and not np.array_equal(tuned.W[0], net.W[0])
    assert np.array_equal(net.mx, mx)                                                                # the original model is untouched
    fresh = copy.deepcopy(net).fit(X, X[:, :1]*5, rng, 10)
    assert not np.array_equal(fresh.mx, mx) or not np.array_equal(fresh.my, my)


def test_tie_aware_agreement_and_step_toward_the_chosen_enemy():
    own = np.array([[1.0, 0.3, 6.0, 7.0, 5.0, 1.0, 1.0, 0.0]]*2)
    enemies = np.zeros((2, 3, 7))
    enemies[:, 0, :] = [1, 8.0, 0.0, 8.0, 1.0, 6.0, 9.0]          # two undamaged enemies with the same damage: an exact tie
    enemies[:, 1, :] = [1, 0.0, 9.0, 9.0, 1.0, 6.0, 9.0]
    enemies[:, 2, :] = [1, 20.0, 0.0, 20.0, 1.0, 6.0, 5.0]
    pool = {'own': own, 'enemies': enemies}
    lab = T.labels(pool, T.teacher2_scores)
    assert lab['target'].tolist() == [0, 0]                         # argmax takes the lowest slot
    m = T.change_metrics(np.array([1, 1]), np.array([[0.0, 1.0], [0.0, 1.0]]), pool, lab)
    assert m['agree_tie_aware_multi'] == 1.0 and m['agree_strict_multi'] == 0.0 and m['tie_share_multi'] == 1.0
    assert m['step_move_median_angle_deg'] < 0.01                   # the step is judged toward the enemy it chose (slot 1, straight up)
    m = T.change_metrics(np.array([2, 2]), np.array([[1.0, 0.0], [1.0, 0.0]]), pool, lab)
    assert m['agree_tie_aware_multi'] == 0.0                        # the weaker hitter is not a tie


def test_single_enemy_states_do_not_inflate_agreement():
    own = np.array([[1.0, 0.3, 6.0, 7.0, 5.0, 1.0, 1.0, 0.0]]*2)
    enemies = np.zeros((2, 3, 7))
    enemies[0, 0, :] = [1, 8.0, 0.0, 8.0, 1.0, 6.0, 9.0]
    enemies[1, 0, :] = [1, 8.0, 0.0, 8.0, 1.0, 6.0, 9.0]
    enemies[1, 1, :] = [1, 0.0, 9.0, 9.0, 1.0, 6.0, 5.0]
    pool = {'own': own, 'enemies': enemies}
    lab = T.labels(pool, T.teacher2_scores)
    m = T.change_metrics(np.array([0, 1]), np.array([[1.0, 0.0], [0.0, 1.0]]), pool, lab)           # right on the one-enemy state, wrong on the two-enemy one
    assert m['agree_tie_aware_all'] == 0.5 and m['agree_tie_aware_multi'] == 0.0


def test_change_fidelity_functions_run_on_real_states():
    rng = np.random.default_rng(7)
    pool = T.collect(rng, 6, T.SEEN_MIXES)
    lab = T.labels(pool, T.teacher2_scores)
    X, Y = T.aim_dataset(pool, lab, 80, rng)
    assert X.shape == (80, T.AIM_DIM) and Y.shape == (80, 1)
    aim = T.MLP(T.AIM_DIM, 8, 1, rng).fit(X, Y, rng, 100)
    move = T.MLP(T.MOVE_DIM, 8, 2, rng).fit(*T.piece_datasets(pool, lab, 20, 80, rng)['MOVE'], rng, 100)
    f = T.change_fidelity_composed(aim, move, pool, lab)
    assert 0.0 <= f['agree_tie_aware_multi'] <= 1.0 and 'step_move_median_angle_deg' in f and f['agree_tie_aware_multi'] >= f['agree_strict_multi']
    Xm, Ym = T.mono_dataset(pool, lab, 80, rng)
    g = T.change_fidelity_mono(T.MLP(T.MONO_IN, 8, T.MONO_OUT, rng).fit(Xm, Ym, rng, 100), pool, lab)
    assert 0.0 <= g['agree_tie_aware_multi'] <= 1.0


def test_latch_and_preflight(tmp_path, monkeypatch):
    spec = json.loads((HERE/'SPEC_CHANGE.json').read_text())
    (tmp_path/'SPEC_CHANGE.json').write_text(json.dumps(spec))
    (tmp_path/'smoke_run_change').mkdir()
    monkeypatch.setattr(change, 'HERE', tmp_path)
    with pytest.raises(SystemExit) as raised:
        change.main_run(True)
    assert 'latch' in str(raised.value) and not list((tmp_path/'smoke_run_change').iterdir())
    folder = tmp_path/'evidence'/'tactical_composition_demo'
    folder.mkdir(parents=True)
    for name in change.FILES:
        (folder/name).write_text('x')
    git = lambda *a: subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *a], cwd=tmp_path, capture_output=True, text=True, check=True)
    git('init', '-q')
    monkeypatch.setattr(change, 'HERE', folder)
    monkeypatch.setattr(change, 'ROOT', tmp_path)
    with pytest.raises(SystemExit) as raised:
        change.preflight(False)
    assert 'not committed' in str(raised.value)
    git('add', '.')
    git('commit', '-q', '-m', 'x')
    assert change.preflight(False)['git_head']
    (folder/'change.py').write_text('changed')
    with pytest.raises(SystemExit) as raised:
        change.preflight(False)
    assert 'uncommitted' in str(raised.value)
    (folder/'change.py').write_text('x')
    (folder/'run_change').mkdir()
    assert change.preflight(False)['git_head']


def test_one_tiny_seed_end_to_end_is_finite_and_repeatable():
    cfg = dict(change.CONFIG, **change.SMOKE)
    cfg.update({'train_episodes': 14, 'test_episodes': 4, 'eval_episodes': 2, 'grid': [30, 60], 'ft_steps_floor': 10, 'ft_steps_cap': 30,
                'stage0': {'n_aim': 120, 'n_move': 120, 'piece_hidden': 16, 'piece_steps': 60, 'batch': 64, 'lr': 0.003},
                'mono_equal': {'rows': 240, 'hidden': 15, 'steps': 60}, 'mono_large': {'rows': 600, 'hidden': 60, 'steps': 60}})
    first, second = change.run_seed(cfg, 4242, 0), change.run_seed(cfg, 4242, 0)
    keys = [k for k, v in first.items() if isinstance(v, float) and not k.startswith(('build_', 'seconds'))]
    assert all(np.isfinite(first[k]) and first[k] == second[k] for k in keys)
    assert {'composed_30_%s' % A, 'mono_eq_60_%s' % A, 'mono_large_30_%s' % S, 'score_composed_60_rush', 'score_teacher2_kiter', 'pre_mono_eq_%s' % A,
            'old_composed_%s_vs_new' % A, 'same_target_teacher1_teacher2_multi', 'train_rmse_composed_30', 'ft_steps_30'} <= set(first)
    assert change.seed_job((cfg, 4242, 0)).get('status') != 'ERROR'
    bad = dict(cfg, mono_large={'rows': 10**7, 'hidden': 60, 'steps': 10})
    assert change.seed_job((bad, 4242, 0))['status'] == 'ERROR'
