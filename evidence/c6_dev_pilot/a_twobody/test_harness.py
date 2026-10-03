"""Harness checks for the two-body pilot: synthetic data and one tiny real-engine run. Not scientific evidence.

Run once from the repository root after the harness is final:
    .venv/bin/python -m pytest -q -x -p no:cacheprovider evidence/c6_dev_pilot/a_twobody/test_harness.py
"""
import gzip
import json
import sys
import time
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pilot  # noqa: E402
from geomind import c6_compose as compose, c6_levels as levels  # noqa: E402


def blob(n=8, radius=0.8, seed=0, phase_spread=0.05):
    rng = np.random.default_rng(seed)
    angle = np.linspace(0, 2*np.pi, n, endpoint=False)
    x = radius*np.c_[np.cos(angle), np.sin(angle)] + rng.normal(0, 0.01, (n, 2))
    owner = levels.Owner(tuple(levels.Owner(element=j) for j in range(n)))
    return {'x': x-x.mean(0), 'th': rng.normal(0, phase_spread, n), 'omega': np.zeros(n), 'isolated_rate': 0.0,
            'owner': owner, 'source_world': seed, 'source_paths': [(seed,)]}


def _sleep(seconds):
    time.sleep(seconds)
    return seconds


def test_contact_matches_original_at_default_gap():
    rng = np.random.default_rng(1)
    for _ in range(5):
        cluster = rng.normal(0, 1.2, (12, 2))
        points = rng.normal(0, 1.0, (9, 2))
        direction = [np.cos(rng.uniform(0, 6)), np.sin(rng.uniform(0, 6))]
        original = compose.contact_solve(points, cluster, np.zeros(2), direction)
        ours = pilot.contact_at_gap(points, cluster, np.zeros(2), direction, 0.6)
        assert original is not None and ours is not None
        assert np.allclose(original[0], ours[0], atol=1e-12) and abs(original[1]-ours[1]) < 1e-12


@pytest.mark.parametrize('gap', [0.6, 1.2, 2.0, 2.8, 4.5])
def test_placed_gap_is_exact(gap):
    ta, tb = blob(seed=1), blob(seed=2)
    pr = pilot.pair_randomness(123456789, 1, 0, 3.4)
    x, th, omega, oa, ob = pilot.build_state(ta, tb, pr, gap, 'phase0')
    na = len(ta['x'])
    d = np.linalg.norm(x[:na, None]-x[None, na:], axis=-1).min()
    assert abs(d-gap) < 2e-6
    assert set(oa.members) == set(range(na)) and set(ob.members) == set(range(na, len(x)))


def test_phase_and_rate_construction():
    ta, tb = blob(seed=3), blob(seed=4)
    ta['isolated_rate'], tb['isolated_rate'] = 0.01, -0.02
    pr = pilot.pair_randomness(42, 2, 5, 16.4)
    assert pr == pilot.pair_randomness(42, 2, 5, 16.4)
    assert abs(pr['rate_a']) <= 0.096/16.4 and abs(pr['rate_b']) <= 0.096/16.4
    _, th0, om0, _, _ = pilot.build_state(ta, tb, pr, 1.2, 'phase_pi')
    na = len(ta['x'])
    assert np.allclose(th0[na:]-tb['th'], np.pi) and np.allclose(th0[:na], ta['th'])
    assert np.allclose(om0[:na], -0.01) and np.allclose(om0[na:], 0.02)  # rates zero, isolated rate removed
    _, thn, omn, _, _ = pilot.build_state(ta, tb, pr, 1.2, 'natural')
    assert np.allclose(thn[na:]-tb['th'], pr['phase'])
    assert np.allclose(omn[:na], pr['rate_a']-0.01) and np.allclose(omn[na:], pr['rate_b']+0.02)
    # a different gap or case changes nothing about the pair's own randomness
    assert pr == pilot.pair_randomness(42, 2, 5, 16.4)


def test_frame_plans_are_whole_steps():
    for T, W in ((200.0, 102.0), (200.0, 30.0), (1640.0, 492.0), (130.0, 102.0), (60.0, 30.0)):
        plan = pilot.frame_plan(T, W)
        assert plan[0][0] == 0.0 and plan[-1][1] == T
        for a, b, every in plan:
            steps = round((b-a)/pilot.DT)
            assert abs(steps*pilot.DT-(b-a)) < 1e-9 and steps % every == 0


def test_json_helpers(tmp_path):
    data = {'a': np.float64(1.5), 'b': np.arange(3), 'c': float('inf'), 'd': float('nan')}
    path = tmp_path/'x.json.gz'
    pilot.write_json(path, data, compress=True)
    back = pilot.read_json(path)
    assert back['b'] == [0, 1, 2] and float(back['c']) == float('inf') and np.isnan(float(back['d']))
    assert not list(tmp_path.glob('*.tmp*'))
    (tmp_path/'dup.json').write_text('{"a": 1, "a": 2}')
    with pytest.raises(ValueError):
        pilot.read_json(tmp_path/'dup.json')


def synthetic_record(level, pair, case, gap, locked=True, distinct=False, long=False, T=200.0, separated=False,
                     push=False):
    t = np.r_[np.arange(0, 20.2, 0.2), np.arange(21.0, T+0.5, 1.0)]
    R = np.where(t < 20, 3.0-0.1*t, 1.0)
    if push:
        R = np.where(t <= 3.0, 3.0+0.3*t, 1.0)
    offset = {'phase0': 0.0, 'phase_halfpi': np.pi/2, 'phase_pi': np.pi}.get(case, 1.5)
    if locked:
        dtheta = 0.05 + (offset-0.05)*np.exp(-t/5.0)
    else:
        dtheta = np.full(len(t), offset)
    coupled = gap < 3 and not separated
    dmin = np.full(len(t), 0.5 if coupled else 4.5)
    if gap < 3 and separated:
        dmin = np.where(t < 10, 0.5, 4.5)
    series = {'t': t, 'R': R, 'dtheta': dtheta, 'dmin': dmin, 'rg_a': np.ones(len(t)), 'rg_b': np.ones(len(t))}
    parts = [{'hull_overlap_max': 0.05 if distinct else 0.9, 'degenerate': False, 'dynamic_ok': True,
              'dynamic_reason': None, 'windows': []} for _ in range(2)]
    validity = {'parent': [{'ok': distinct, 'hull_overlap': 0.05 if distinct else 0.9} for _ in range(2)]} if long \
        else {'parts': parts}
    return {'status': 'OK', 'key': 'L%d_p%02d_%s_g%.1f_T%d' % (level, pair, case, gap, int(T)), 'level': level,
            'pair': pair, 'case': case, 'gap': gap, 'T': T, 'long': long, 'series': series, 'validity': validity}


def synthetic_panel(locked=True, distinct=False, pairs=8, push_pi=True, with_long=False):
    records, long_keys = [], []
    for pair in range(pairs):
        for gap in (0.6, 1.2, 2.0, 2.8, 4.5):
            for case in pilot.CASES:
                decoupled = gap > 3
                r = synthetic_record(2, pair, case, gap, locked and not decoupled, distinct,
                                     push=(push_pi and case == 'phase_pi' and gap <= 2.0))
                records.append(r)
        if with_long:
            r = synthetic_record(2, pair, 'natural', 0.6, True, distinct, long=True, T=1640.0)
            records.append(r)
            long_keys.append(r['key'])
    plan = {'expected_keys': [r['key'] for r in records], 'long_keys': long_keys,
            'pairs': {'2': [{'pair': p, 'source_a': 10*p, 'source_b': 10*p+1} for p in range(pairs)],
                      '1': [{'pair': p, 'source_a': 1000+10*p, 'source_b': 1000+10*p+1} for p in range(3)]}}
    return records, plan


def test_derive_known_values():
    rec = synthetic_record(2, 0, 'natural', 0.6, locked=True, distinct=True)
    d = pilot.derive(rec)
    assert d['coupled'] and d['locked'] and d['bound'] and d['distinct'] and d['distinct_bound']
    assert d['category'] == 'DISTINCT_COUPLED' and d['offset0'] > 1.0
    fused = pilot.derive(synthetic_record(2, 0, 'natural', 0.6, locked=True, distinct=False))
    assert fused['category'] == 'FUSED' and not fused['distinct_bound']
    gone = pilot.derive(synthetic_record(2, 0, 'phase_pi', 0.6, locked=False, separated=True))
    assert gone['category'] == 'SEPARATED' and not gone['coupled_end'] and not gone['distinct_bound']
    free = pilot.derive(synthetic_record(2, 0, 'natural', 4.5, locked=False))
    assert not free['coupled'] and not free['locked'] and free['category'] == 'SEPARATED'
    inf = synthetic_record(2, 0, 'natural', 0.6)
    inf['validity']['parts'][0]['hull_overlap_max'] = 'Infinity'
    out = pilot.derive(inf)
    assert out['overlap'] == float('inf') and not out['distinct'] and out['category'] == 'FUSED'
    damaged = synthetic_record(2, 0, 'natural', 0.6, distinct=True)
    damaged['validity']['parts'][1]['dynamic_ok'] = False
    assert pilot.derive(damaged)['category'] == 'PARTS_DAMAGED'


def test_interpretation_fusion_regime_supported():
    records, plan = synthetic_panel(locked=True, distinct=False)
    out = pilot.interpret(records, plan)
    assert out['status'] == 'COMPLETE'
    p = out['predictions']
    assert p['P1_phase_locking']['verdict'] == 'SUPPORTED' and p['P1_phase_locking']['decoupled_baseline'] == 0.0
    assert p['P2_no_distinct_bound_pair']['verdict'] == 'SUPPORTED'
    assert p['P2_no_distinct_bound_pair']['reading'] == 'FUSION_REGIME'
    assert p['P3_phase_push_then_slip']['verdict'] == 'SUPPORTED'


def test_interpretation_bound_regime_refutes_p2():
    records, plan = synthetic_panel(locked=True, distinct=True)
    p = pilot.interpret(records, plan)['predictions']
    assert p['P2_no_distinct_bound_pair']['verdict'] == 'REFUTED'
    assert p['P2_no_distinct_bound_pair']['reading'] == 'DISTINCT_BOUND_REGIME_EXISTS'


def test_repelled_pairs_do_not_count_as_fusion():
    records, plan = synthetic_panel(locked=True, distinct=False)
    for r in records:
        if r['case'] == 'phase_pi' and r['gap'] < 3:
            r.update(synthetic_record(2, r['pair'], 'phase_pi', r['gap'], locked=False, separated=True))
    out = pilot.interpret(records, plan)
    p2 = out['predictions']['P2_no_distinct_bound_pair']
    assert p2['n'] == 8*4*3  # the 32 separated runs left the denominator instead of inflating "no bound pair"
    assert out['tables']['2']['phase_pi|0.6']['categories']['SEPARATED'] == 1.0


def test_decoupled_baseline_gates_phase_locking():
    records, plan = synthetic_panel(locked=True, distinct=False)
    for r in records:
        if abs(r['gap']-4.5) < 1e-9:
            r.update(synthetic_record(2, r['pair'], r['case'], 4.5, locked=True))
    p1 = pilot.interpret(records, plan)['predictions']['P1_phase_locking']
    assert p1['decoupled_baseline'] > 0.10 and p1['verdict'] == 'INDETERMINATE'


def test_p3_needs_effect_size_and_quiet_control():
    records, plan = synthetic_panel(push_pi=False)
    p3 = pilot.interpret(records, plan)['predictions']['P3_phase_push_then_slip']
    assert p3['push_fraction'] == 0.0 and p3['verdict'] == 'REFUTED'


def test_incomplete_takes_precedence_and_scopes_are_separate():
    records, plan = synthetic_panel()
    missing = pilot.interpret(records[1:], plan)
    assert missing['status'] == 'INCOMPLETE' and missing['missing'] == 1 and 'predictions' not in missing
    duplicate = pilot.interpret(records + [records[0]], plan)
    assert duplicate['status'] == 'INCOMPLETE' and duplicate['problems']
    errored = [dict(r) for r in records]
    errored[3]['status'] = 'ERROR'
    assert pilot.interpret(errored, plan)['status'] == 'INCOMPLETE'
    few, few_plan = synthetic_panel(pairs=7)
    out = pilot.interpret(few, few_plan)
    assert out['status'] == 'INCOMPLETE' and 'INCOMPLETE' in out['level2']
    # a lost long run reports INCOMPLETE overall but keeps the short-run verdicts
    withlong, long_plan = synthetic_panel(with_long=True)
    out = pilot.interpret([r for r in withlong if not r['long']], long_plan)
    assert out['status'] == 'INCOMPLETE' and out['short_complete'] and not out['long_complete']
    assert out['predictions']['P2_no_distinct_bound_pair']['verdict'] == 'SUPPORTED'
    shared = json.loads(json.dumps(plan))
    shared['pairs']['2'][1]['source_a'] = shared['pairs']['2'][0]['source_a']
    assert pilot.interpret(records, shared)['problems']


def test_short_runs_are_scheduled_before_long_runs():
    spec = pilot.load_spec()
    cfg = dict(spec['smoke'], long=True)
    pairs = {2: [(blob(seed=1), blob(seed=2))], 1: [(blob(seed=3), blob(seed=4))]}
    jobs = pilot.two_body_jobs(spec, cfg, 7, pairs)
    flags = [j['long'] for j in jobs]
    assert flags == sorted(flags) and any(flags) and not flags[0]
    assert [j['level'] for j in jobs if not j['long']][0] == 2


def test_pairing_uses_one_template_per_source():
    ts = [blob(seed=s) for s in (1, 1, 2, 3, 3, 4)]
    picks = pilot.pick_one_per_source(ts)
    assert [t['source_world'] for t in picks] == [1, 2, 3, 4]
    pairs = pilot.make_pairs(picks, 5)
    assert len(pairs) == 2 and all(a['source_world'] != b['source_world'] for a, b in pairs)


def test_run_one_real_engine_and_error_path():
    ta, tb = blob(seed=5), blob(seed=6)
    pr = pilot.pair_randomness(2024, 1, 0, 3.4)
    job = {'key': 'k', 'level': 1, 'pair': 0, 'case': 'phase0', 'gap': 1.2, 'T': 60.0, 'long': False, 'c_part': 1.0,
           'pr': pr, 'ta': ta, 'tb': tb}
    pilot._init(pilot.load_spec()['entropy'], pilot.load_spec()['identity'])
    rec = pilot.run_one(job)
    assert rec['status'] == 'OK', rec
    s = rec['series']
    assert len(s['t']) == len(s['R']) == len(s['dtheta']) == len(s['dmin'])
    assert abs(s['dmin'][0]-1.2) < 1e-4 and np.isfinite(s['R']).all()
    assert rec['snapshots']['x'].shape[0] == 13 and rec['validity']['window'] == 30.0
    json.dumps(pilot.jsonable(rec))
    bad = dict(job, ta=dict(ta, x=None))
    out = pilot.run_one(bad)
    assert out['status'] == 'ERROR' and out['key'] == 'k'


def test_run_jobs_respects_deadline_and_terminates():
    import concurrent.futures as cf
    import multiprocessing as mp
    pool = cf.ProcessPoolExecutor(max_workers=2, mp_context=mp.get_context('spawn'))
    seen = []
    started = time.monotonic()
    status, submitted, finished = pilot.run_jobs(pool, _sleep, [8.0]*6, lambda j, r: seen.append(r),
                                                 started+2.0, 2)
    pilot.terminate(pool)
    assert status == 'deadline' and time.monotonic()-started < 12 and not seen


def test_run_jobs_collects_results():
    import concurrent.futures as cf
    import multiprocessing as mp
    pool = cf.ProcessPoolExecutor(max_workers=2, mp_context=mp.get_context('spawn'))
    seen = []
    status, submitted, finished = pilot.run_jobs(pool, _sleep, [0.01]*5, lambda j, r: seen.append(r),
                                                 time.monotonic()+30, 2)
    pilot.terminate(pool)
    assert status == 'done' and submitted == finished == 5 and len(seen) == 5


def test_no_worker_entry_point_and_latch(tmp_path, monkeypatch):
    source = (HERE/'pilot.py').read_text()
    assert '--worker' not in source
    spec = pilot.load_spec()
    (tmp_path/'SPEC.json').write_text(json.dumps(spec))
    (tmp_path/'smoke_run').mkdir()
    monkeypatch.setattr(pilot, 'HERE', tmp_path)
    with pytest.raises(SystemExit) as raised:
        pilot.main_run(True)
    assert 'latch' in str(raised.value)
    assert not list((tmp_path/'smoke_run').iterdir())  # refused without touching the existing run


def test_preflight_refuses_changed_dependency(monkeypatch):
    spec = pilot.load_spec()
    changed = json.loads(json.dumps(spec))
    changed['identity']['files']['geomind/c6_levels.py'] = '0'*64
    with pytest.raises(SystemExit) as raised:
        pilot.preflight(changed, True)
    assert 'c6_levels.py' in str(raised.value)
    bad = json.loads(json.dumps(spec))
    bad['identity']['files']['build/c6/element_law.dylib'] = '1'*64
    with pytest.raises(SystemExit):
        pilot.preflight(bad, True)
