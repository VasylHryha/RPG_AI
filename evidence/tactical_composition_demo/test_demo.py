"""Mechanics checks for the tactical demo harness and verdict rules (synthetic rows, guards, one tiny real seed).

Run once from the repository root after the code is final:
    .venv/bin/python -m pytest -q -p no:cacheprovider evidence/tactical_composition_demo/test_demo.py
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import demo  # noqa: E402

CELLS = ('teacher', 'rush', 'composed', 'mono_0', 'mono_1', 'mono_2')


def row(seed=0, aim=0.98, angle=2.0, hold=0.97, teacher=0.7, rush=0.3, composed=0.65, monos=(0.4, 0.5, 0.6),
        u_teacher=0.8, u_rush=0.35, u_composed=0.7, u_mono=(0.4, 0.5, 0.6), backoff=8.0):
    r = {'seed': seed, 'fid_aim_top1': aim, 'fid_aim_nearest_enemy_floor': 0.87, 'fid_move_median_angle_deg': angle,
         'fid_move_hold_agreement': hold, 'fid_move_backoff_median_angle_deg': backoff,
         'build_seconds_pieces': 2.0, 'pieces_rows': 6000, 'pieces_parameters': 787, 'seconds': 50.0, 'pool_states': 110000}
    for j in range(3):
        r['build_seconds_mono_%d' % j] = 3.0*(j+1)
        r['mono_%d_parameters' % j] = 770
        r['mono_%d_rows_actual' % j] = (6000, 24000, 96000)[j]
        r['fid_mono_%d_aim_top1' % j], r['fid_mono_%d_move_median_angle_deg' % j] = 0.9, 5.0
        r['fid_mono_%d_move_hold_agreement' % j], r['fid_mono_%d_move_backoff_median_angle_deg' % j] = 0.9, 15.0
    values = {'seen': {'teacher': teacher, 'rush': rush, 'composed': composed, 'mono_0': monos[0], 'mono_1': monos[1], 'mono_2': monos[2]},
              'unseen': {'teacher': u_teacher, 'rush': u_rush, 'composed': u_composed, 'mono_0': u_mono[0], 'mono_1': u_mono[1], 'mono_2': u_mono[2]}}
    for mix, cells in values.items():
        for cell, v in cells.items():
            for opp in demo.OPPONENTS:
                r['score_%s_%s_%s' % (cell, mix, opp)] = v
    return r


CFG = dict(demo.CONFIG)


def verdicts(rows):
    ev = demo.evaluate(rows, CFG)
    return {k: v['verdict'] for k, v in ev.items() if 'verdict' in v}, ev


def test_all_supported_when_every_bar_is_met():
    v, ev = verdicts([row(s) for s in range(20)])
    assert v == {'P1_pieces_learn': 'SUPPORTED', 'P2_composed_unit_plays': 'SUPPORTED', 'P3_composition_beats_one_big_controller': 'SUPPORTED',
                 'P4_data_needed_to_match': 'SUPPORTED', 'P5_new_unit_type_without_retraining': 'SUPPORTED'}
    assert ev['P4_data_needed_to_match']['smallest_matching_scale_index'] is None


def test_p1_branches():
    assert verdicts([row(aim=0.93) for _ in range(20)])[0]['P1_pieces_learn'] == 'INDETERMINATE'
    assert verdicts([row(aim=0.85) for _ in range(20)])[0]['P1_pieces_learn'] == 'REFUTED'
    assert verdicts([row(angle=25.0) for _ in range(20)])[0]['P1_pieces_learn'] == 'REFUTED'
    mixed = [row(aim=0.98) for _ in range(14)]+[row(aim=0.9) for _ in range(6)]       # median fine, only 70% of seeds meet every bar
    assert verdicts(mixed)[0]['P1_pieces_learn'] == 'INDETERMINATE'
    assert verdicts([row(backoff=40.0) for _ in range(20)])[0]['P1_pieces_learn'] == 'INDETERMINATE'   # a missing back-off behaviour is seen
    assert verdicts([row(backoff=None) for _ in range(20)])[0]['P1_pieces_learn'] == 'SUPPORTED'        # no back-off states at all is not a failure


def test_p2_needs_the_teacher_gap_and_the_rush_floor():
    assert verdicts([row(composed=0.55) for _ in range(20)])[0]['P2_composed_unit_plays'] == 'INDETERMINATE'   # 0.15 under the teacher
    assert verdicts([row(composed=0.40, teacher=0.7, rush=0.38) for _ in range(20)])[0]['P2_composed_unit_plays'] == 'REFUTED'  # barely above rush
    assert verdicts([row(composed=0.40, rush=0.30) for _ in range(20)])[0]['P2_composed_unit_plays'] == 'REFUTED'              # 0.30 under the teacher
    assert verdicts([row(composed=0.61, rush=0.50) for _ in range(20)])[0]['P2_composed_unit_plays'] == 'INDETERMINATE'        # not 0.15 above rush


def test_p3_and_p4_branches_and_gating():
    v = verdicts([row(monos=(0.64, 0.65, 0.66)) for _ in range(20)])[0]
    assert v['P3_composition_beats_one_big_controller'] == 'REFUTED' and v['P4_data_needed_to_match'] == 'REFUTED'
    v = verdicts([row(monos=(0.58, 0.5, 0.5)) for _ in range(20)])[0]                 # gap 0.07: neither refuted nor supported
    assert v['P3_composition_beats_one_big_controller'] == 'INDETERMINATE'
    v = verdicts([row(monos=(0.4, 0.64, 0.5)) for _ in range(20)])[0]                 # only the 4x big controller catches up
    assert v['P4_data_needed_to_match'] == 'INDETERMINATE'
    v = verdicts([row(monos=(0.4, 0.5, 0.64)) for _ in range(20)])[0]                 # only the LARGEST catches up (review finding)
    assert v['P4_data_needed_to_match'] == 'INDETERMINATE'
    v = verdicts([row(monos=(0.2, 0.25, 0.3)) for _ in range(20)])[0]                 # the biggest controller never beats rush: baseline did not learn
    assert v['P3_composition_beats_one_big_controller'] == 'INDETERMINATE' and v['P4_data_needed_to_match'] == 'INDETERMINATE'
    v = verdicts([row(composed=0.5, rush=0.40, monos=(0.2, 0.2, 0.5)) for _ in range(20)])[0]   # the composite does not clear P2: no P3/P4 credit
    assert v['P3_composition_beats_one_big_controller'] != 'SUPPORTED' and v['P4_data_needed_to_match'] == 'INDETERMINATE'
    v = verdicts([row(u_mono=(0.65, 0.65, 0.65)) for _ in range(20)])[0]              # seen gap fine, unseen type gap too small
    assert v['P3_composition_beats_one_big_controller'] == 'INDETERMINATE'


def test_p2_and_p5_gates_use_paired_differences():
    rows = [row(seed=s, teacher=0.9 if s % 2 else 0.5, rush=0.3, composed=(0.9 if s % 2 else 0.5)-0.05) for s in range(20)]
    assert verdicts(rows)[0]['P2_composed_unit_plays'] == 'SUPPORTED'                  # tracks the teacher within 0.05 on every seed
    rows = [row(seed=s, teacher=0.9 if s % 2 else 0.5, rush=0.3, composed=0.7) for s in range(20)]
    v, ev = verdicts(rows)
    assert ev['P2_composed_unit_plays']['share_of_seeds_meeting_bar'] == 0.5 and v['P2_composed_unit_plays'] == 'INDETERMINATE'


def test_p5_branches():
    assert verdicts([row(u_composed=0.5) for _ in range(20)])[0]['P5_new_unit_type_without_retraining'] == 'INDETERMINATE'
    assert verdicts([row(u_composed=0.37, u_rush=0.35) for _ in range(20)])[0]['P5_new_unit_type_without_retraining'] == 'REFUTED'


def test_descriptive_reports_build_cost_and_budgets():
    ev = demo.evaluate([row(s) for s in range(20)], CFG)['descriptive']
    assert ev['rows_pieces'] == 6000 and ev['rows_monolith_actual'] == [6000, 24000, 96000]
    assert ev['monolith_fidelity_to_teacher']['mono_0']['aim_top1']['median'] == 0.9
    assert ev['parameters_pieces'] == 787 and len(ev['build_seconds_monolith']) == 3


def test_spec_json_matches_the_code_constants():
    spec = json.loads((HERE/'SPEC.json').read_text())
    assert spec['config'] == json.loads(json.dumps(demo.CONFIG))
    assert spec['smoke_overrides'] == json.loads(json.dumps(demo.SMOKE))


def test_equal_budget_rows_and_parameters_are_consistent():
    c = demo.CONFIG
    assert c['n_aim']+c['n_move'] == c['monolith'][0]['rows']                               # equal rows
    import tactics as T
    pieces = T.MLP.parameter_count(T.AIM_DIM, c['piece_hidden'], 1)+T.MLP.parameter_count(T.MOVE_DIM, c['piece_hidden'], 2)
    mono = T.MLP.parameter_count(T.MONO_IN, c['monolith'][0]['hidden'], T.MONO_OUT)
    assert abs(mono-pieces)/pieces < 0.05                                                   # equal size within 5%
    assert [m['rows'] for m in c['monolith']] == [6000, 24000, 96000]


def test_latch_refuses_an_existing_run(tmp_path, monkeypatch):
    spec = json.loads((HERE/'SPEC.json').read_text())
    (tmp_path/'SPEC.json').write_text(json.dumps(spec))
    (tmp_path/'smoke_run').mkdir()
    monkeypatch.setattr(demo, 'HERE', tmp_path)
    with pytest.raises(SystemExit) as raised:
        demo.main_run(True)
    assert 'latch' in str(raised.value) and not list((tmp_path/'smoke_run').iterdir())


def test_preflight_requires_committed_clean_files(tmp_path, monkeypatch):
    folder = tmp_path/'evidence'/'tactical_composition_demo'
    folder.mkdir(parents=True)
    for name in demo.FILES:
        (folder/name).write_text('x')
    git = lambda *a: subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *a], cwd=tmp_path, capture_output=True, text=True, check=True)
    git('init', '-q')
    monkeypatch.setattr(demo, 'HERE', folder)
    monkeypatch.setattr(demo, 'ROOT', tmp_path)
    with pytest.raises(SystemExit) as raised:
        demo.preflight(False)
    assert 'not committed' in str(raised.value)
    git('add', '.')
    git('commit', '-q', '-m', 'x')
    assert demo.preflight(False)['git_head']
    (folder/'tactics.py').write_text('changed')
    with pytest.raises(SystemExit) as raised:
        demo.preflight(False)
    assert 'uncommitted' in str(raised.value)
    (folder/'tactics.py').write_text('x')
    (folder/'run').mkdir()
    assert demo.preflight(False)['git_head']


def _sleep_job(job):
    time.sleep(job[0])
    return {'seed': job[2]}


def test_run_jobs_respects_the_deadline_and_collects_results():
    import concurrent.futures as cf
    import multiprocessing as mp
    pool = cf.ProcessPoolExecutor(max_workers=2, mp_context=mp.get_context('spawn'))
    seen = []
    status, submitted, finished = demo.run_jobs(pool, _sleep_job, [(0.01, None, s) for s in range(5)], lambda j, r: seen.append(r), time.monotonic()+30, 2)
    assert status == 'done' and finished == 5 and len(seen) == 5
    started = time.monotonic()
    status, _, _ = demo.run_jobs(pool, _sleep_job, [(8.0, None, s) for s in range(6)], lambda j, r: seen.append(r), started+2.0, 2)
    demo.terminate(pool)
    assert status == 'deadline' and time.monotonic()-started < 12


def test_one_tiny_seed_end_to_end_is_finite_and_repeatable():
    cfg = dict(demo.CONFIG, **demo.SMOKE)
    cfg.update({'train_episodes': 12, 'test_episodes': 4, 'eval_episodes': 2, 'n_aim': 120, 'n_move': 120, 'piece_steps': 60,
                'monolith': [{'rows': 240, 'hidden': 15, 'steps': 60}, {'rows': 480, 'hidden': 30, 'steps': 60}, {'rows': 960, 'hidden': 60, 'steps': 60}]})
    first = demo.run_seed(cfg, 4242, 0)
    second = demo.run_seed(cfg, 4242, 0)
    keys = [k for k, v in first.items() if isinstance(v, float) and not k.startswith(('build_seconds', 'seconds'))]
    assert all(np.isfinite(first[k]) and first[k] == second[k] for k in keys)
    assert {'score_composed_seen_rush', 'score_mono_2_unseen_kiter', 'fid_aim_top1', 'score_teacher_unseen_rush'} <= set(first)
    out = demo.seed_job((cfg, 4242, 0))
    assert out.get('status') != 'ERROR' and out['seed'] == 0


def test_evaluation_episodes_are_paired_across_controllers():
    import tactics as T
    a = T.win_score(T.teacher_policy, T.SEEN_MIXES, T.rush_policy, demo.stream(5, 9, 0, 0, 0), 6)
    b = T.win_score(T.teacher_policy, T.SEEN_MIXES, T.rush_policy, demo.stream(5, 9, 0, 0, 0), 6)
    assert a == b
    # the draws of mixes and start positions do not depend on the controller: a different controller sees the same episodes
    r1, r2 = demo.stream(5, 9, 0, 0, 0), demo.stream(5, 9, 0, 0, 0)
    for _ in range(3):
        mixes_a = (tuple(r1.permutation(T.SEEN_MIXES[int(r1.integers(len(T.SEEN_MIXES)))])), tuple(r1.permutation(T.SEEN_MIXES[int(r1.integers(len(T.SEEN_MIXES)))])))
        w1 = T.World(mixes_a[0], mixes_a[1], r1)
        T.play(T.rush_policy, mixes_a[0], T.rush_policy, mixes_a[1], np.random.default_rng(0))
        mixes_b = (tuple(r2.permutation(T.SEEN_MIXES[int(r2.integers(len(T.SEEN_MIXES)))])), tuple(r2.permutation(T.SEEN_MIXES[int(r2.integers(len(T.SEEN_MIXES)))])))
        w2 = T.World(mixes_b[0], mixes_b[1], r2)
        assert mixes_a == mixes_b and np.array_equal(w1.pos, w2.pos)


def test_run_seed_refuses_a_pool_smaller_than_the_requested_rows():
    cfg = dict(demo.CONFIG, **demo.SMOKE)
    cfg.update({'train_episodes': 2, 'test_episodes': 2, 'eval_episodes': 1, 'n_aim': 50, 'n_move': 50, 'piece_steps': 10,
                'monolith': [{'rows': 10**7, 'hidden': 15, 'steps': 10}]})
    with pytest.raises(RuntimeError):
        demo.run_seed(cfg, 99, 0)
    assert demo.seed_job((cfg, 99, 0))['status'] == 'ERROR'
