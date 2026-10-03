"""Mechanics checks for revision 2 of the change-cost harness and verdict rules (synthetic rows, guards, one tiny real seed).

Run once from the repository root after the code is final:
    .venv/bin/python -m pytest -q -p no:cacheprovider evidence/tactical_composition_demo/test_change2.py
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import change2 as C  # noqa: E402

CFG = dict(C.CONFIG)
GRID = CFG['grid']
A, S, RAW = C.AGREE, C.STEP, C.RAW


def row(seed=0, same=0.68, old=0.67, pre=(0.966, 0.739, 0.90), pre_step=(1.5, 10.7, 6.0),
        wired=((0.83, 0.88, 0.96, 0.99, 1.0, 1.0), (0.91, 0.94, 0.98, 0.998, 1.0, 1.0), (2.5, 2.4, 2.3, 2.2, 2.2, 2.2)),
        big=((0.50, 0.57, 0.63, 0.66, 0.735, 0.74), (0.75, 0.79, 0.81, 0.83, 0.87, 0.88), (33.0, 21.0, 18.0, 14.0, 12.5, 11.5)),
        large=((0.4, 0.5, 0.6, 0.7, 0.8, 0.9), (0.7, 0.75, 0.78, 0.82, 0.88, 0.92), (30.0, 20.0, 15.0, 10.0, 8.0, 6.5))):
    """Each design is (chance-corrected agreement by n, raw tie-aware agreement by n, step angle by n). Defaults: the wired unit recovers its own 0.966 (bar 0.936) at 1000 rows
    and reaches raw 0.80 at 100; the equal-size big controller recovers its own 0.739 (bar 0.709, step bar 13.7) at 6000 rows and reaches raw 0.80 at 1000."""
    r = {'seed': seed, 'same_target_teacher1_teacher2_multi': same, 'old_composed_%s_vs_new' % RAW: old, 'old_mono_eq_%s_vs_new' % RAW: 0.6, 'seconds': 120.0,
         'pre_composed_chance_tie_aware_multi': 0.45}
    for prefix, p, ps in zip(('composed', 'mono_eq', 'mono_large'), pre, pre_step):
        r['pre_%s_%s' % (prefix, A)], r['pre_%s_%s' % (prefix, S)] = p, ps
    for prefix, (corr, raw, step) in (('composed', wired), ('mono_eq', big), ('mono_large', large)):
        for i, n in enumerate(GRID):
            r['%s_%d_%s' % (prefix, n, A)], r['%s_%d_%s' % (prefix, n, RAW)], r['%s_%d_%s' % (prefix, n, S)] = corr[i], raw[i], step[i]
            r['ft_%s_%d_%s' % (prefix, n, A)], r['ft_%s_%d_%s' % (prefix, n, RAW)], r['ft_%s_%d_%s' % (prefix, n, S)] = corr[i]-0.1, raw[i]-0.05, step[i]+3
            r['build_%s_%d' % (prefix, n)] = 1.0
    for n in GRID:
        r['scratch_steps_%d' % n] = 500
        r['composed_%d_tie_share_multi' % n] = 0.29
        r['composed_%d_chance_tie_aware_multi' % n] = 0.55
    for cell, v in (('teacher2', 0.6), ('rush', 0.4), ('composed_old', 0.55), ('mono_eq_old', 0.5)):
        for o in C.OPPONENTS:
            r['score_%s_%s' % (cell, o)] = v
    for n in GRID:
        for cell, v in (('composed_%d' % n, 0.6), ('mono_eq_%d' % n, 0.55)):
            for o in C.OPPONENTS:
                r['score_%s_%s' % (cell, o)] = v
    return r


def verdicts(rows):
    ev = C.evaluate(rows, CFG)
    return {k: v['verdict'] for k, v in ev.items() if 'verdict' in v}, ev


def test_supported_when_both_views_agree_the_wired_unit_recovers_far_sooner():
    v, ev = verdicts([row(s) for s in range(20)])
    assert v == {'C1_the_change_is_real': 'SUPPORTED', 'C2_cheap_change_for_the_wired_unit': 'SUPPORTED', 'C3_cheaper_than_retraining_the_big_controller': 'SUPPORTED'}
    c3 = ev['C3_cheaper_than_retraining_the_big_controller']
    assert c3['relative_view_rows_needed_by_half_of_seeds'] == {'wired': 1000.0, 'big_equal': 6000.0, 'big_large': 12000.0}
    assert c3['common_level_view_rows_needed_by_half_of_seeds'] == {'wired': 100.0, 'big_equal': 1000.0, 'big_large': 3000.0}


def test_c3_is_indeterminate_when_the_two_views_disagree():
    easy_big = ((0.50, 0.57, 0.63, 0.66, 0.735, 0.74), (0.85, 0.86, 0.87, 0.88, 0.89, 0.9), (33.0, 21.0, 18.0, 14.0, 12.5, 11.5))   # raw 0.80 already at 100 rows
    v, ev = verdicts([row(big=easy_big) for _ in range(20)])
    c3 = ev['C3_cheaper_than_retraining_the_big_controller']
    assert c3['relative_view_verdict'] == 'SUPPORTED' and c3['common_level_view_verdict'] == 'REFUTED' and v['C3_cheaper_than_retraining_the_big_controller'] == 'INDETERMINATE'


def test_c1_uses_the_median_only_so_a_borderline_share_cannot_gate_the_rest():
    rows = [row(s, same=0.71 if s < 6 else 0.66) for s in range(20)]            # 70% of seeds at or below 0.70, median 0.66
    v, ev = verdicts(rows)
    assert v['C1_the_change_is_real'] == 'SUPPORTED' and v['C2_cheap_change_for_the_wired_unit'] == 'SUPPORTED'
    assert abs(ev['C1_the_change_is_real']['share_of_seeds_with_same_target_at_most_0.70'] - 0.70) < 1e-9
    assert verdicts([row(same=0.90) for _ in range(20)])[0]['C1_the_change_is_real'] == 'REFUTED'
    assert verdicts([row(same=0.75) for _ in range(20)])[0]['C1_the_change_is_real'] == 'INDETERMINATE'
    assert verdicts([row(old=0.90) for _ in range(20)])[0]['C1_the_change_is_real'] == 'INDETERMINATE'


def test_c2_is_gated_on_c1_in_both_directions():
    weak = ((0.3,)*6, (0.5,)*6, (2.0,)*6)
    for kwargs in ({'same': 0.75}, {'same': 0.90}):
        v = verdicts([row(wired=weak, **kwargs) for _ in range(20)])[0]
        assert v['C2_cheap_change_for_the_wired_unit'] == 'INDETERMINATE' and v['C3_cheaper_than_retraining_the_big_controller'] == 'INDETERMINATE'


def test_c2_branches_and_the_seventy_five_percent_boundary():
    late = ((0.80, 0.85, 0.90, 0.99, 1.0, 1.0), (0.9, 0.9, 0.95, 0.99, 1.0, 1.0), (2.5,)*6)                  # recovers at 3000 rows, not 1000
    assert verdicts([row(wired=late) for _ in range(20)])[0]['C2_cheap_change_for_the_wired_unit'] == 'INDETERMINATE'
    stuck = ((0.5, 0.6, 0.7, 0.75, 0.78, 0.8), (0.8,)*6, (2.5,)*6)                                           # 0.8 < 0.966 - 0.15 at 12,000 rows
    assert verdicts([row(wired=stuck) for _ in range(20)])[0]['C2_cheap_change_for_the_wired_unit'] == 'REFUTED'
    bad_step = ((0.83, 0.88, 0.96, 0.99, 1.0, 1.0), (0.91, 0.94, 0.98, 0.998, 1.0, 1.0), (2.5, 2.4, 15.0, 2.2, 2.2, 2.2))
    assert verdicts([row(wired=bad_step) for _ in range(20)])[0]['C2_cheap_change_for_the_wired_unit'] == 'INDETERMINATE'   # the step must recover too
    for recovered, expected in ((15, 'SUPPORTED'), (14, 'INDETERMINATE')):                                   # exactly 75% against just under
        rows = [row(s) for s in range(recovered)]+[row(s, wired=late) for s in range(recovered, 20)]
        assert verdicts(rows)[0]['C2_cheap_change_for_the_wired_unit'] == expected, recovered


def test_c3_branches():
    quick_big = ((0.74,)*6, (0.82,)*6, (3.0,)*6)                                                             # the big controller recovers and reaches 0.80 at 100 rows
    v = verdicts([row(big=quick_big) for _ in range(20)])[0]
    assert v['C3_cheaper_than_retraining_the_big_controller'] == 'REFUTED'
    never_big = ((0.5,)*6, (0.7,)*6, (30.0,)*6)
    v = verdicts([row(big=never_big) for _ in range(20)])[0]
    assert v['C3_cheaper_than_retraining_the_big_controller'] == 'SUPPORTED'                                  # never within the grid on both views
    slow_wired = ((0.83, 0.88, 0.96, 0.99, 1.0, 1.0), (0.7, 0.75, 0.85, 0.9, 0.95, 0.95), (2.5,)*6)             # recovers at 1000 rows and reaches raw 0.80 at 1000 rows
    v = verdicts([row(wired=slow_wired, big=((0.5, 0.5, 0.74, 0.74, 0.74, 0.74), (0.7, 0.7, 0.82, 0.82, 0.82, 0.82), (30, 30, 3, 3, 3, 3))) for _ in range(20)])[0]
    assert v['C3_cheaper_than_retraining_the_big_controller'] == 'REFUTED'                                    # 1000 against 1000 on both views
    v = verdicts([row(wired=slow_wired, big=((0.5, 0.5, 0.5, 0.74, 0.74, 0.74), (0.7, 0.7, 0.7, 0.82, 0.82, 0.82), (30, 30, 30, 3, 3, 3))) for _ in range(20)])[0]
    assert v['C3_cheaper_than_retraining_the_big_controller'] == 'SUPPORTED'                                  # 3000 rows = 3 x 1000 on both views
    v = verdicts([row(wired=((0.5, 0.5, 0.5, 0.5, 0.97, 0.99), (0.9,)*6, (2.5,)*6), big=never_big) for _ in range(20)])[0]
    assert v['C3_cheaper_than_retraining_the_big_controller'] == 'INDETERMINATE'                               # the wired unit failed C2: no credit


def test_rows_by_share_is_a_grid_value_never_interpolated():
    needs = np.array([100.0]*9+[float('inf')]*11)
    assert C.rows_by_share(needs, CFG) == float('inf')                                                        # 45% by 100 rows
    needs = np.array([100.0]*10+[3000.0]*10)
    assert C.rows_by_share(needs, CFG) == 100.0                                                               # exactly half by 100 rows
    needs = np.array([1000.0]*6+[3000.0]*6+[float('inf')]*8)
    assert C.rows_by_share(needs, CFG) == 3000.0 and C.ratio_verdict(1000.0, 3000.0) == 'SUPPORTED' and C.ratio_verdict(1000.0, 1000.0) == 'REFUTED'
    assert C.ratio_verdict(1000.0, 2000.0) == 'INDETERMINATE' and C.ratio_verdict(1000.0, float('inf')) == 'SUPPORTED'


def test_needs_relative_and_level_views():
    rows = [row(s) for s in range(4)]
    assert list(C.needs_relative(rows, 'composed', 'composed', CFG)) == [1000.0]*4 and list(C.needs_relative(rows, 'mono_eq', 'mono_eq', CFG)) == [6000.0]*4
    assert list(C.needs_level(rows, 'composed', 0.80, CFG)) == [100.0]*4 and list(C.needs_level(rows, 'mono_eq', 0.80, CFG)) == [1000.0]*4
    slow = row(big=((0.5,)*5+(0.70,), (0.7,)*6, (30.0,)*6))                                                    # corrected 0.70 < 0.739 - 0.03: not recovered anywhere
    assert np.isinf(C.needs_relative([slow], 'mono_eq', 'mono_eq', CFG)).all() and np.isinf(C.needs_level([slow], 'mono_eq', 0.80, CFG)).all()
    d = C.evaluate([row(s) for s in range(20)], CFG)['descriptive']
    assert d['rows_to_reach_an_absolute_agreement_level_by_half_of_seeds']['composed']['0.9'] == 100.0
    assert d['rows_to_reach_an_absolute_agreement_level_by_half_of_seeds']['mono_eq']['0.95'] == float('inf')
    assert d['fine_tuning_protocol_of_the_first_revision']['ft_composed']['rows_needed_by_half_of_seeds_relative_view'] == float('inf')   # the secondary protocol recovers worse (built into the row)


def test_tie_best_step_chance_baseline_and_corrected_agreement():
    import tactics as T
    own = np.array([[1.0, 0.3, 6.0, 7.0, 5.0, 1.0, 1.0, 0.0]]*2)
    enemies = np.zeros((2, 3, 7))
    for k in range(2):
        enemies[k, 0, :] = [1, 8.0, 0.0, 8.0, 1.0, 6.0, 9.0]       # two tied-best enemies on opposite sides
        enemies[k, 1, :] = [1, -8.0, 0.0, 8.0, 1.0, 6.0, 9.0]
        enemies[k, 2, :] = [1, 0.0, 15.0, 15.0, 1.0, 6.0, 5.0]     # a weaker one
    pool = {'own': own, 'enemies': enemies}
    lab = T.labels(pool, T.teacher2_scores)
    to_right, to_left, up = np.array([[1.0, 0.0]]*2), np.array([[-1.0, 0.0]]*2), np.array([[0.0, 1.0]]*2)
    m = T.change_metrics(np.array([1, 1]), to_right, pool, lab)       # chose the left enemy (tied-best) but steps right (toward the other tied-best one)
    assert m['agree_tie_aware_multi'] == 1.0 and m['step_tiebest_median_angle_deg'] < 0.01                     # any tied-best step is correct
    assert m['step_move_median_angle_deg'] > 170                                                                # the chosen-enemy step metric would have penalised it
    assert abs(m['chance_tie_aware_multi'] - 2/3) < 1e-9 and m['agree_corrected_multi'] == 1.0
    m = T.change_metrics(np.array([0, 0]), up, pool, lab)
    assert m['step_tiebest_median_angle_deg'] > 80                                                              # a step toward neither tied-best enemy is wrong
    m = T.change_metrics(np.array([2, 2]), to_left, pool, lab)
    assert m['agree_tie_aware_multi'] == 0.0 and m['agree_corrected_multi'] < 0


def test_schedules_scale_with_the_rows_and_are_shared():
    steps = {n: C.scratch_steps(n, CFG) for n in GRID}
    assert steps == {100: 500, 300: 500, 1000: 1329, 3000: 3985, 6000: 7969, 12000: 15938}
    assert [C.ft_steps(n, CFG) for n in GRID] == [200, 282, 938, 2000, 2000, 2000]


def test_spec_json_matches_the_code_constants_and_stage0_settings():
    spec = json.loads((HERE/'SPEC_CHANGE2.json').read_text())
    assert spec['config'] == json.loads(json.dumps(C.CONFIG)) and spec['smoke_overrides'] == json.loads(json.dumps(C.SMOKE))
    stage0 = json.loads((HERE/'SPEC.json').read_text())['config']
    assert CFG['stage0'] == {k: stage0[k] for k in ('n_aim', 'n_move', 'piece_hidden', 'piece_steps', 'batch', 'lr')}
    assert CFG['mono_equal'] == stage0['monolith'][0] and CFG['mono_large'] == stage0['monolith'][2]
    learn = json.loads((HERE/'dev_learnability.json').read_text())
    assert learn['learnable'] is True and learn['medians']['aim_scratch_3000'] >= 0.95                                # the development rule held
    assert CFG['grid'] == [100, 300, 1000, 3000, 6000, 12000] and CFG['c2_rows'] in CFG['grid'] and CFG['common_level'] in CFG['absolute_agreement_levels']


def test_latch_and_preflight(tmp_path, monkeypatch):
    spec = json.loads((HERE/'SPEC_CHANGE2.json').read_text())
    (tmp_path/'SPEC_CHANGE2.json').write_text(json.dumps(spec))
    (tmp_path/'smoke_run_change2').mkdir()
    monkeypatch.setattr(C, 'HERE', tmp_path)
    with pytest.raises(SystemExit) as raised:
        C.main_run(True)
    assert 'latch' in str(raised.value) and not list((tmp_path/'smoke_run_change2').iterdir())
    folder = tmp_path/'evidence'/'tactical_composition_demo'
    folder.mkdir(parents=True)
    for name in C.FILES:
        (folder/name).write_text('x')
    git = lambda *a: subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *a], cwd=tmp_path, capture_output=True, text=True, check=True)
    git('init', '-q')
    monkeypatch.setattr(C, 'HERE', folder)
    monkeypatch.setattr(C, 'ROOT', tmp_path)
    with pytest.raises(SystemExit) as raised:
        C.preflight(False)
    assert 'not committed' in str(raised.value)
    git('add', '.')
    git('commit', '-q', '-m', 'x')
    assert C.preflight(False)['git_head']
    (folder/'change2.py').write_text('changed')
    with pytest.raises(SystemExit) as raised:
        C.preflight(False)
    assert 'uncommitted' in str(raised.value)
    (folder/'change2.py').write_text('x')
    (folder/'run_change2').mkdir()
    assert C.preflight(False)['git_head']


def test_one_tiny_seed_end_to_end_is_finite_and_repeatable():
    cfg = dict(C.CONFIG, **C.SMOKE)
    cfg.update({'train_episodes': 14, 'test_episodes': 4, 'eval_episodes': 2, 'grid': [30, 60], 'scratch_steps_floor': 20, 'scratch_steps_cap': 40,
                'ft_steps_floor': 10, 'ft_steps_cap': 20, 'c2_rows': 30,
                'stage0': {'n_aim': 120, 'n_move': 120, 'piece_hidden': 16, 'piece_steps': 60, 'batch': 64, 'lr': 0.003},
                'mono_equal': {'rows': 240, 'hidden': 15, 'steps': 60}, 'mono_large': {'rows': 600, 'hidden': 60, 'steps': 60}})
    first, second = C.run_seed(cfg, 4242, 0), C.run_seed(cfg, 4242, 0)
    keys = [k for k, v in first.items() if isinstance(v, float) and not k.startswith(('build_', 'seconds'))]
    assert all(np.isfinite(first[k]) and first[k] == second[k] for k in keys)
    assert {'composed_30_%s' % A, 'mono_eq_60_%s' % RAW, 'mono_large_30_%s' % S, 'ft_composed_30_%s' % A, 'ft_mono_eq_60_%s' % A, 'score_composed_60_rush',
            'score_mono_eq_30_kiter', 'pre_mono_eq_%s' % A, 'old_composed_%s_vs_new' % RAW, 'scratch_steps_30', 'pre_composed_chance_tie_aware_multi'} <= set(first)
    assert C.seed_job((cfg, 4242, 0)).get('status') != 'ERROR'
    assert C.seed_job((dict(cfg, mono_large={'rows': 10**7, 'hidden': 60, 'steps': 10}), 4242, 0))['status'] == 'ERROR'
