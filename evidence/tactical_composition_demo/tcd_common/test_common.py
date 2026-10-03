"""Mechanics checks for tcd_common. Run once from the repository root after the code is final:

    .venv/bin/python -m pytest -q -p no:cacheprovider evidence/tactical_composition_demo/tcd_common/test_common.py

Each guard test is written so that it FAILS if the guarded behaviour is removed (see the comment on each).
"""
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tcd_common import fileio, harness, legacy, metrics, selftest_jobs, stats, supervise  # noqa: E402
import tactics as T  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]


# ------------------------------------------------------------------ fileio

def test_atomic_write_unique_temp_names_and_no_leftovers(tmp_path):
    seen = []
    real_replace = os.replace
    os.replace = lambda a, b: (seen.append(Path(a).name), real_replace(a, b))[1]
    try:
        threads = [threading.Thread(target=fileio.atomic_write, args=(tmp_path/'x.json', b'%d' % i)) for i in range(8)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        fileio.atomic_write(tmp_path/'x.json', b'last')
    finally:
        os.replace = real_replace
    assert len(seen) == len(set(seen)) == 9                                  # a shared temp name would collide here
    assert (tmp_path/'x.json').read_bytes() == b'last' and [p.name for p in tmp_path.iterdir()] == ['x.json']


def test_atomic_write_cleans_up_on_failure(tmp_path):
    with pytest.raises(TypeError):
        fileio.atomic_write(tmp_path/'y.json', 'not bytes')
    assert list(tmp_path.iterdir()) == []


def test_jsonable_handles_numpy_and_infinity():
    out = fileio.jsonable({'a': np.float64(1.5), 'b': np.array([1, 2]), 'c': float('inf'), 'd': -float('inf'), 'e': float('nan'), 'f': (np.int64(3),)})
    assert out == {'a': 1.5, 'b': [1, 2], 'c': 'Infinity', 'd': '-Infinity', 'e': 'NaN', 'f': [3]}


def test_streams_differ_by_key_and_entropy_and_refuse_short_entropy():
    e1, e2 = 2**90+12345, 2**90+12346
    draws = {k: fileio.stream(*k).random() for k in [(e1, 1, 0), (e1, 1, 1), (e1, 2, 0), (e2, 1, 0), (e1, 1, 0, 0), (e1, 1)]}
    assert len(set(draws.values())) == 6 and fileio.stream(e1, 1, 0).random() == draws[(e1, 1, 0)]   # trailing-zero keys do not alias for a 96-bit entropy
    with pytest.raises(ValueError):
        fileio.stream(1, 1, 0)                                                                         # with a tiny entropy (1, 1, 0) and (1, 1, 0, 0) would alias


def test_spec_entropies_are_pairwise_distinct():
    values = []
    for path in list(HERE.glob('SPEC*.json'))+[ROOT/'evidence/geometric_composition_demo/SPEC.json', ROOT/'evidence/c6_dev_pilot/a_twobody/SPEC.json']:
        spec = json.loads(path.read_text())
        values += [(path.name, k, spec[k]) for k in ('entropy', 'smoke_entropy') if k in spec]
    assert len(values) >= 6 and len({v for _, _, v in values}) == len(values), values   # isolation between runs rests on distinct entropies


# ------------------------------------------------------------------ stats

def test_ratio_verdict_never_credits_two_infinities():
    inf = float('inf')
    assert stats.ratio_verdict(inf, inf) == 'INDETERMINATE'                  # the recorded rule returned SUPPORTED here
    assert stats.ratio_verdict(1000.0, inf) == 'SUPPORTED' and stats.ratio_verdict(inf, 1000.0) == 'REFUTED'
    assert stats.ratio_verdict(100.0, 300.0) == 'SUPPORTED' and stats.ratio_verdict(100.0, 100.0) == 'REFUTED' and stats.ratio_verdict(100.0, 250.0) == 'INDETERMINATE'


def test_bootstrap_interval_contains_median_and_narrows_with_n():
    rng = np.random.default_rng(5)
    small, big = rng.normal(0.0, 1.0, 10), rng.normal(0.0, 1.0, 400)
    m1, lo1, hi1 = stats.bootstrap_median_ci(small, np.random.default_rng(51))
    m2, lo2, hi2 = stats.bootstrap_median_ci(big, np.random.default_rng(52))
    assert lo1 <= m1 <= hi1 and lo2 <= m2 <= hi2 and (hi2-lo2) < (hi1-lo1)
    m, lo, hi = stats.paired_median_ci(np.full(20, 0.9), np.full(20, 0.6), np.random.default_rng(53))
    assert abs(m-0.3) < 1e-12 and lo > 0.29


# ------------------------------------------------------------------ metrics

def make_pool(enemy_rows, own_pref=1.2):
    """A one-state pool. enemy_rows: list of (alive, dx, dy, dist) for three slots; every other enemy feature is neutral."""
    enemies = np.zeros((1, T.N_UNITS, T.ENEMY_DIM))
    for j, (alive, dx, dy, dist) in enumerate(enemy_rows):
        enemies[0, j, :4] = (alive, dx, dy, dist)
    own = np.zeros((1, T.OWN_DIM))
    own[0, 4] = own_pref
    return {'own': own, 'enemies': enemies}


def test_tiebest_accepts_a_hold_when_one_tied_enemy_is_in_band():
    # pref 1.2 (fighter): enemy 0 at distance 1.2 -> teacher holds; enemy 1 at distance 6 -> teacher moves. Both tied for best.
    pool = make_pool([(1, 1.2, 0.0, 1.2), (1, 6.0, 0.0, 6.0), (0, 0, 0, 0)])
    lab = {'scores': np.array([[1.0, 1.0, -9.0]]), 'target': np.array([0])}
    assert np.hypot(*T.teacher_move(np.array([1.2, 0.0]), 1.2)) < 0.5 < np.hypot(*T.teacher_move(np.array([6.0, 0.0]), 1.2))
    hold = metrics.step_tiebest(np.array([[0.0, 0.0]]), pool, lab)
    assert hold['step_tiebest_median_angle_deg'] == 0.0 and hold['step_tiebest_hold_agreement'] == 1.0     # the recorded metric scored ~90 degrees here
    move = metrics.step_tiebest(np.array([[1.0, 0.0]]), pool, lab)
    assert move['step_tiebest_median_angle_deg'] < 1.0                                                      # moving toward the far tied enemy also matches


def test_tiebest_wrong_hold_counts_as_a_large_error_and_is_reported():
    pool = make_pool([(1, 6.0, 0.0, 6.0), (1, 0.0, 7.0, 7.0), (0, 0, 0, 0)])
    lab = {'scores': np.array([[1.0, 1.0, -9.0]]), 'target': np.array([0])}
    out = metrics.step_tiebest(np.array([[0.0, 0.0]]), pool, lab)
    assert out['step_tiebest_median_angle_deg'] == 90.0 and out['step_tiebest_wrong_hold_share'] == 1.0 and out['step_tiebest_hold_agreement'] is None
    far = metrics.step_tiebest(np.array([[0.0, 1.0]]), pool, lab)                                          # best match is the second tied enemy
    assert far['step_tiebest_median_angle_deg'] < 1.0 and far['step_tiebest_wrong_hold_share'] == 0.0


def test_metrics_use_only_multi_enemy_states():
    single = make_pool([(1, 6.0, 0.0, 6.0), (0, 0, 0, 0), (0, 0, 0, 0)])
    multi = make_pool([(1, 6.0, 0.0, 6.0), (1, 3.0, 0.0, 3.0), (0, 0, 0, 0)])
    pool = {'own': np.concatenate([single['own'], multi['own']]), 'enemies': np.concatenate([single['enemies'], multi['enemies']])}
    lab = {'scores': np.array([[1.0, -9.0, -9.0], [0.2, 0.9, -9.0]]), 'target': np.array([0, 1])}
    assert list(metrics.multi_enemy(pool)) == [False, True]
    right = metrics.agreement(np.array([0, 1]), pool, lab)
    wrong_on_multi = metrics.agreement(np.array([0, 0]), pool, lab)
    assert right['n_multi'] == 1 and right['n_all'] == 2 and right['agree_tie_aware_multi'] == 1.0
    assert wrong_on_multi['agree_tie_aware_multi'] == 0.0 and wrong_on_multi['agree_strict_multi'] == 0.0    # the single-enemy state does not rescue it
    assert abs(right['chance_tie_aware_multi']-0.5) < 1e-12 and abs(right['agree_corrected_multi']-1.0) < 1e-12
    # the step is only judged on the multi-enemy state: a perfect step there with a garbage step on the single-enemy state scores perfectly
    steps = np.array([[-1.0, 0.0], T.teacher_move(np.array([3.0, 0.0]), 1.2)])
    chosen = metrics.step_toward_chosen(steps, np.array([0, 1]), pool)
    assert chosen['step_chosen_move_median_angle_deg'] < 0.01


def test_chance_corrected_agreement_is_zero_for_a_random_like_pick():
    pool = make_pool([(1, 6.0, 0.0, 6.0), (1, 3.0, 0.0, 3.0), (1, 9.0, 0.0, 9.0)])
    lab = {'scores': np.array([[0.1, 0.9, 0.2]]), 'target': np.array([1])}
    out = metrics.agreement(np.array([0]), pool, lab)
    assert out['chance_tie_aware_multi'] == pytest.approx(1/3) and out['agree_tie_aware_multi'] == 0.0 and out['agree_corrected_multi'] == pytest.approx(-0.5)


def test_change_metrics_agrees_with_recorded_tie_aware_agreement_on_real_states():
    rng = np.random.default_rng(9)
    pool = T.collect(rng, 6, T.SEEN_MIXES)
    lab = T.labels(pool, T.teacher2_scores)
    chosen = np.array([int(np.argmax(np.where(e[:, 0] > 0, rng.random(T.N_UNITS), -1))) for e in pool['enemies']])      # a random living pick
    pred = np.array([T.teacher_move(e[c, 1:3], o[4]) for o, e, c in zip(pool['own'], pool['enemies'], chosen)])
    new, old = metrics.change_metrics(chosen, pred, pool, lab), T.change_metrics(chosen, pred, pool, lab)
    for key in ('agree_tie_aware_multi', 'agree_strict_multi', 'tie_share_multi', 'chance_tie_aware_multi', 'agree_corrected_multi'):
        assert new[key] == pytest.approx(old[key])                              # same population, so the agreement keys do not change
    assert 0.0 < new['agree_tie_aware_multi'] < 1.0 and new['step_chosen_move_median_angle_deg'] < 0.01   # the step is exact toward whichever enemy was chosen
    best = np.array([int(np.argmax(np.where(e[:, 0] > 0, s, -np.inf))) for e, s in zip(pool['enemies'], lab['scores'])])    # the teacher's own pick
    pred = np.array([T.teacher_move(e[c, 1:3], o[4]) for o, e, c in zip(pool['own'], pool['enemies'], best)])
    perfect = metrics.change_metrics(best, pred, pool, lab)
    assert perfect['agree_tie_aware_multi'] == 1.0 and perfect['step_tiebest_median_angle_deg'] < 0.01 and perfect['step_tiebest_wrong_hold_share'] == 0.0
    assert old['tie_share_multi'] > 0.05                                         # the doctrine really has ties in this sample


# ------------------------------------------------------------------ supervision

def test_run_jobs_reports_done_only_when_everything_finished():
    class Pool:
        def submit(self, fn, job):
            import concurrent.futures as cf
            f = cf.Future()
            f.set_result(fn(job))
            return f
    got = []
    far = time.monotonic()+60
    status, sub, fin = supervise.run_jobs(Pool(), lambda j: {'seed': j[2]}, [(0, 0, s) for s in range(5)], lambda j, r: got.append(r), far, 2)
    assert (status, sub, fin) == ('done', 5, 5) and len(got) == 5
    status, sub, fin = supervise.run_jobs(Pool(), lambda j: {'seed': j[2]}, [(0, 0, s) for s in range(5)], lambda j, r: got.append(r), time.monotonic()-1, 2)
    assert status == 'deadline' and sub == 0 and fin == 0                       # nothing was submitted: not 'done'


def test_run_jobs_last_job_finishing_at_the_deadline_is_still_done():
    import concurrent.futures as cf

    class Pool:
        def __init__(self):
            self.n = 0
            self.deadline = None

        def submit(self, fn, job):
            f = cf.Future()
            f.set_result(fn(job))
            return f
    pool = Pool()
    deadline = time.monotonic()+0.2

    def slow(job):
        time.sleep(0.3)           # the last (and only) job completes after the deadline has passed
        return {'seed': job[2]}
    status, sub, fin = supervise.run_jobs(pool, slow, [(0, 0, 0)], lambda j, r: None, deadline, 1)
    assert (status, sub, fin) == ('done', 1, 1)                                  # the recorded run_jobs said 'deadline' here


def test_run_jobs_error_results_carry_the_seed():
    import concurrent.futures as cf

    class Pool:
        def submit(self, fn, job):
            f = cf.Future()
            try:
                f.set_result(fn(job))
            except Exception as e:  # noqa: BLE001
                f.set_exception(e)
            return f
    got = {}

    def boom(job):
        raise ValueError('x')
    supervise.run_jobs(Pool(), boom, [(0, 0, 4)], lambda j, r: got.update(r), time.monotonic()+5, 1)
    assert got['status'] == 'ERROR' and got['seed'] == 4 and 'ValueError' in got['error']


def test_watchdog_fires_writes_stop_and_summary_and_exits_3(tmp_path):
    codes, cleaned = [], []
    w = supervise.Watchdog(tmp_path, 0.2, cleanup=lambda: cleaned.append(1), exit_fn=codes.append).start()
    time.sleep(0.8)
    assert codes == [3] and cleaned == [1] and w.fired and not w.cancel()        # cancel after firing reports failure
    stop = json.loads((tmp_path/'HARD_STOP.json').read_text())
    assert stop['status'] == 'HARD_STOP' and ('pkill_returncode' in stop or 'pkill_error' in stop)
    assert json.loads((tmp_path/'SUMMARY.json').read_text())['status'] == 'INCOMPLETE'


def test_watchdog_keeps_an_existing_summary_and_cancel_wins_before_expiry(tmp_path):
    (tmp_path/'SUMMARY.json').write_text('{"status": "COMPLETE"}')
    codes = []
    w = supervise.Watchdog(tmp_path, 0.2, exit_fn=codes.append).start()
    time.sleep(0.6)
    assert json.loads((tmp_path/'SUMMARY.json').read_text())['status'] == 'COMPLETE' and codes == [3]
    other = tmp_path/'b'
    other.mkdir()
    codes.clear()
    w2 = supervise.Watchdog(other, 0.3, exit_fn=codes.append).start()
    assert w2.cancel() and not w2.fired
    time.sleep(0.6)
    assert codes == [] and not (other/'HARD_STOP.json').exists()                 # a cancelled watchdog never fires


def test_watchdog_cleanup_error_is_recorded_not_fatal(tmp_path):
    codes = []

    def bad():
        raise RuntimeError('cleanup failed')
    supervise.Watchdog(tmp_path, 0.1, cleanup=bad, exit_fn=codes.append).start()
    time.sleep(0.6)
    assert codes == [3] and 'cleanup failed' in json.loads((tmp_path/'HARD_STOP.json').read_text())['cleanup_error']


# ------------------------------------------------------------------ preflight (a real throwaway git repository)

def git_repo(tmp_path):
    def git(*a):
        subprocess.run(['git', *a], cwd=tmp_path, check=True, capture_output=True)
    git('init', '-q')
    git('config', 'user.email', 't@t')
    git('config', 'user.name', 't')
    exp = tmp_path/'evidence'/'exp'
    exp.mkdir(parents=True)
    (exp/'a.py').write_text('x=1\n')
    (exp/'SPEC.json').write_text('{}')
    git('add', '.')
    git('commit', '-qm', 'c')
    return exp


def test_preflight_passes_on_a_clean_tree_and_returns_the_head(tmp_path):
    exp = git_repo(tmp_path)
    out = harness.preflight(tmp_path, exp, ('a.py', 'SPEC.json'), ('run', 'smoke_run'), False)
    assert len(out['git_head']) == 40


def test_preflight_ignores_only_the_exact_run_directories(tmp_path):
    exp = git_repo(tmp_path)
    (exp/'run').mkdir()
    (exp/'run'/'RUN_STARTED.json').write_text('{}')
    (exp/'run_other').mkdir()
    (exp/'run_other'/'f.txt').write_text('x')
    with pytest.raises(SystemExit) as e:
        harness.preflight(tmp_path, exp, ('a.py',), ('run',), False)
    assert 'run_other/f.txt' in str(e.value) and 'run/RUN_STARTED' not in str(e.value)    # 'run_other' is not 'run' (the recorded substring match let it through)
    (exp/'run_other'/'f.txt').unlink()
    (exp/'run_other').rmdir()
    assert harness.preflight(tmp_path, exp, ('a.py',), ('run',), False)['git_head']      # a file inside the exact run directory is filtered


def test_preflight_rejects_modified_and_uncommitted_files(tmp_path):
    exp = git_repo(tmp_path)
    (exp/'a.py').write_text('x=2\n')
    with pytest.raises(SystemExit, match='uncommitted'):
        harness.preflight(tmp_path, exp, ('a.py',), ('run',), False)
    subprocess.run(['git', 'checkout', '-q', '--', '.'], cwd=tmp_path, check=True)
    (exp/'new.py').write_text('y=1\n')
    with pytest.raises(SystemExit, match='uncommitted'):
        harness.preflight(tmp_path, exp, ('a.py',), ('run',), False)
    with pytest.raises(SystemExit, match='not committed'):
        harness.preflight(tmp_path, exp, ('new.py',), ('run',), False)
    assert harness.preflight(tmp_path, exp, ('a.py',), ('run',), True) == {'git': 'not enforced for smoke'}


# ------------------------------------------------------------------ the run harness end to end (tiny, real spawned workers)

def spec_for(tmp_path, **cfg):
    config = {'seeds': 4, 'workers': 2, 'soft_cap': 60.0, 'hard_cap': 120.0}
    config.update(cfg)
    path = tmp_path/'SPEC.json'
    path.write_text(json.dumps({'entropy': 12345, 'smoke_entropy': 999, 'config': config, 'smoke_overrides': {'seeds': 2}}))
    return path


def evaluate_echo(rows, cfg):
    return {'X': {'verdict': 'SUPPORTED', 'values': [r['value'] for r in rows]}}


def test_run_experiment_complete_run_latch_and_hashes(tmp_path):
    spec = spec_for(tmp_path)
    (tmp_path/'a.py').write_text('x')
    kw = dict(spec_path=spec, here=tmp_path, root=tmp_path, files=('a.py',), run_dirs=('run', 'smoke_run'), seed_job=selftest_jobs.echo_job, evaluate=evaluate_echo)
    code, summary = harness.run_experiment(run_name='smoke_run', smoke=True, **kw)
    assert code == 0 and summary['status'] == 'COMPLETE' and summary['seeds_complete'] == 2
    run = tmp_path/'smoke_run'
    started = json.loads((run/'RUN_STARTED.json').read_text())
    assert started['hashes']['a.py'] and started['smoke'] is True
    assert sorted(p.name for p in (run/'seeds').iterdir()) == ['seed_00.json', 'seed_01.json'] and not list(run.rglob('*.tmp*'))
    assert json.loads((run/'SUMMARY.json').read_text())['evaluation']['X']['verdict'] == 'SUPPORTED'
    with pytest.raises(SystemExit, match='latch'):
        harness.run_experiment(run_name='smoke_run', smoke=True, **kw)          # no resume, no retry


def test_run_experiment_records_a_failing_seed_and_is_not_complete(tmp_path):
    spec = spec_for(tmp_path, seeds=3)
    code, summary = harness.run_experiment(spec_path=spec, here=tmp_path, root=tmp_path, files=(), run_dirs=('run',), run_name='run', seed_job=selftest_jobs.failing_job,
                                           evaluate=evaluate_echo, smoke=True)
    assert code == 1 and summary['status'] == 'INCOMPLETE' and summary['seed_errors'][0]['seed'] == 1 and 'boom' in summary['seed_errors'][0]['error']
    assert (tmp_path/'run'/'seeds'/'error_01.json').exists() and 'evaluation' not in summary


def test_run_experiment_soft_cap_stops_cleanly_and_never_evaluates(tmp_path):
    spec = spec_for(tmp_path, seeds=4, workers=2, soft_cap=2.0, hard_cap=60.0, sleep=30)
    started = time.monotonic()
    code, summary = harness.run_experiment(spec_path=spec, here=tmp_path, root=tmp_path, files=(), run_dirs=('run',), run_name='run', seed_job=selftest_jobs.slow_job,
                                           evaluate=evaluate_echo, smoke=True)
    assert time.monotonic()-started < 20 and code == 1 and summary['reason'] == 'stopped: deadline' and 'evaluation' not in summary
    assert json.loads((tmp_path/'run'/'SUMMARY.json').read_text())['status'] == 'INCOMPLETE'


def test_run_experiment_cancels_the_watchdog_before_evaluating(tmp_path):
    spec = spec_for(tmp_path, seeds=2, hard_cap=3.0)
    codes = []

    def slow_evaluate(rows, cfg):
        time.sleep(4.0)           # evaluation outlasts the hard cap: a finished run must still be recorded as COMPLETE
        return {'X': {'verdict': 'SUPPORTED'}}
    code, summary = harness.run_experiment(spec_path=spec, here=tmp_path, root=tmp_path, files=(), run_dirs=('run',), run_name='run', seed_job=selftest_jobs.echo_job,
                                           evaluate=slow_evaluate, smoke=True, exit_fn=codes.append)
    assert code == 0 and summary['status'] == 'COMPLETE' and codes == [] and not (tmp_path/'run'/'HARD_STOP.json').exists()


def test_max_rss_is_normalised_to_bytes():
    class U:
        ru_maxrss = 1000
    assert harness.max_rss_bytes(U) == (1000 if sys.platform == 'darwin' else 1000*1024)


# ------------------------------------------------------------------ regression gate against the recorded tactics.py versions

def test_current_tactics_reproduces_every_recorded_version_exactly():
    differs = {}
    for name, (rev, short) in legacy.RECORDED.items():
        try:
            source = legacy.source_at(rev)
        except LookupError:
            pytest.skip('git history for %s is not available in this clone' % rev)
        assert legacy.identity(source).startswith(short), name                     # the recovered file is the one the run recorded
        result = legacy.compare(T, legacy.load(source, 'tactics_'+name), seeds=(0,), episodes=6, n_aim=200, n_move=200, steps=100, eval_episodes=2)
        if not result['equal']:
            differs[name] = result['differs']
    assert not differs, differs


def test_the_gate_detects_a_changed_primitive():
    source = legacy.source_at(legacy.RECORDED['stage0'][0]).decode()
    broken = source.replace("def teacher_move(rel, pref):", "def teacher_move(rel, pref):\n    pref = pref+0.01", 1)
    assert broken != source
    result = legacy.compare(T, legacy.load(broken.encode(), 'tactics_broken'), seeds=(0,), episodes=4, n_aim=100, n_move=100, steps=50, eval_episodes=2)
    assert not result['equal'] and any(k.startswith('labels') or k.startswith('pool') for k in result['differs'])
