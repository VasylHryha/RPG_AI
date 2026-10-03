"""Mechanics checks for the geometric composition demo (known-answer cases, not the scientific predictions).

Run once from the repository root after the code is final:
    .venv/bin/python -m pytest -q -p no:cacheprovider evidence/geometric_composition_demo/test_demo.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import demo  # noqa: E402


def test_squared_distance_identity_matches_direct():
    rng = np.random.default_rng(0)
    U, P = rng.random((50, 4)), rng.random((7, 4))
    direct = ((U[:, None, :]-P[None])**2).sum(-1)
    assert np.allclose(demo.squared_distances(U, P), direct, atol=1e-12)


def test_geomap_reproduces_a_linear_law_and_chunking_is_irrelevant():
    rng = np.random.default_rng(1)
    X = demo.uniform(rng, 800, [0, 0], [20, 20])
    y = X[:, 0]+X[:, 1]
    a = demo.GeoMap([0, 0], [20, 20], 16, chunk=4000).fit(X, y, np.random.default_rng(2))
    b = demo.GeoMap([0, 0], [20, 20], 16, chunk=137).fit(X, y, np.random.default_rng(2))
    Xt = demo.uniform(rng, 500, [0, 0], [20, 20])
    assert demo.rel_error(a.predict(Xt), Xt[:, 0]+Xt[:, 1]) < 1e-4
    assert np.allclose(a.predict(Xt), b.predict(Xt), atol=1e-7)


def test_geomap_beats_a_constant_on_a_nonlinear_law_and_is_deterministic():
    rng = np.random.default_rng(3)
    X = demo.uniform(rng, 600, [0, 0], [5, 5])
    y = X[:, 0]*X[:, 1]
    first = demo.GeoMap([0, 0], [5, 5], 32).fit(X, y, np.random.default_rng(4)).predict(X)
    second = demo.GeoMap([0, 0], [5, 5], 32).fit(X, y, np.random.default_rng(4)).predict(X)
    assert np.array_equal(first, second)
    assert demo.rel_error(first, y) < 0.5*demo.rel_error(np.full_like(y, y.mean()), y)


class Oracle:
    """A perfect piece, used only to check the wiring logic."""
    def __init__(self, f, lo, hi):
        self.f, self.lo, self.hi = f, np.asarray(lo, float), np.asarray(hi, float)

    def predict(self, X):
        return self.f(np.asarray(X, float))


def test_wiring_with_perfect_pieces_is_exact():
    pieces = {'ADD': Oracle(demo.PIECE_FUNCTIONS['ADD'], [-2, -2], [20, 20]),
              'MUL': Oracle(demo.PIECE_FUNCTIONS['MUL'], [1, 1], [5, 5]),
              'SQRT': Oracle(demo.PIECE_FUNCTIONS['SQRT'], [1], [40])}
    rng = np.random.default_rng(5)
    X = demo.uniform(rng, 200, [1.0]*4, [3.0]*4)
    counter = {}
    got = demo.diag4(lambda a, b: demo.wired_distance(pieces, a, b, counter), X)
    assert np.allclose(got, np.sqrt((X**2).sum(1)), atol=1e-12)
    assert counter.get('MUL', 0) == 0 and counter['calls_MUL'] == 200*2*3
    far = demo.wired_distance(pieces, np.array([9.0]), np.array([9.0]), counter)  # 9 > MUL domain [1, 5]
    assert counter['MUL'] == 2 and np.isfinite(far).all()


def test_mix_wiring_with_perfect_pieces_is_exact_and_linear_baseline_is_linear():
    pieces = {'ADD': Oracle(demo.PIECE_FUNCTIONS['ADD'], [-2, -2], [20, 20]),
              'MUL': Oracle(demo.PIECE_FUNCTIONS['MUL'], [1, 1], [5, 5]),
              'SQRT': Oracle(demo.PIECE_FUNCTIONS['SQRT'], [1], [40]),
              'DIV': Oracle(demo.PIECE_FUNCTIONS['DIV'], [0.3, 0.3], [4, 3])}
    rng = np.random.default_rng(9)
    X = demo.uniform(rng, 300, demo.CONFIG['mix_lo'], demo.CONFIG['mix_hi'])
    counter = {}
    assert np.allclose(demo.wired_mix(pieces, X, counter), demo.mix_truth(X), atol=1e-12)
    assert counter['MUL'] == 0 and counter['DIV'] == 0 and counter['ADD'] == 0 and counter['SQRT'] == 0
    Xl = demo.uniform(rng, 500, [0, 0, 0, 0], [1, 1, 1, 1])
    yl = Xl@np.array([1.0, 2.0, -1.0, 0.5])+3
    assert np.allclose(demo.linear_baseline(Xl, yl, Xl), yl, atol=1e-9)


def test_mlp_learns_a_linear_law():
    rng = np.random.default_rng(6)
    X = demo.uniform(rng, 1500, [1.0]*4, [3.0]*4)
    y = X.sum(1)
    net = demo.MLP(4, 16, np.random.default_rng(7)).fit(X, y, np.random.default_rng(8), 60, 128, 0.01)
    Xt = demo.uniform(rng, 500, [1.0]*4, [3.0]*4)
    assert demo.rel_error(net.predict(Xt), Xt.sum(1)) < 0.05


def test_rel_error_and_streams():
    t = np.array([0.0, 1.0, 2.0])
    assert demo.rel_error(t+0.1, t) == pytest.approx(0.05)
    a = demo.stream(123, 1, 2, 3).random(3)
    assert np.array_equal(a, demo.stream(123, 1, 2, 3).random(3))
    assert not np.array_equal(a, demo.stream(123, 1, 2, 4).random(3))
    assert not np.array_equal(a, demo.stream(124, 1, 2, 3).random(3))


def rows_for(piece=0.005, distance=0.01, diag=0.02, mono=(0.2, 0.05, 0.01), closure=0.005, diag_p=0.02, mlp=(0.1, 0.03), n=20,
             linear=0.1, mix=None, linear_distance=0.03, linear_diag=0.05):
    out = []
    mix = diag if mix is None else mix
    for i in range(n):
        row = {'seed': i, 'seconds': 1.0, 'distance': distance, 'diag4': diag, 'mix4': mix, 'closure': closure, 'diag4_promoted': diag_p,
               'linear_mix4': linear, 'linear_distance': linear_distance, 'linear_diag4': linear_diag,
               'promoted_distance': 0.01,
               'violations_distance': {'MUL': 0, 'ADD': 0, 'SQRT': 0, 'calls_MUL': 10, 'calls_ADD': 10, 'calls_SQRT': 10},
               'violations': {'MUL': 0, 'ADD': 0, 'SQRT': 0, 'calls_MUL': 10, 'calls_ADD': 10, 'calls_SQRT': 10},
               'violations_mix': {'MUL': 0, 'DIV': 0, 'ADD': 0, 'SQRT': 0, 'calls_MUL': 10, 'calls_DIV': 10, 'calls_ADD': 10, 'calls_SQRT': 10}}
        for name in demo.PIECE_ORDER:
            row['piece_'+name] = piece
        for j, m in enumerate(mono):
            row['monolith_%d' % j] = m
        for j, m in enumerate(mlp):
            row['mlp_%d' % j] = m
        out.append(row)
    return out


CFG = dict(demo.CONFIG, monolith=[{'M': 1, 'N': 1, 'seeds': 20}] * 3, mlp=[{'N': 1, 'epochs': 1}] * 2)


def test_verdict_logic_supported_and_refuted_branches():
    ev = demo.evaluate(rows_for(), CFG)
    assert [ev[k]['verdict'] for k in ('P1_pieces_learn', 'P2_wiring_works', 'P3_composition_beats_one_big_map',
                                       'P4_data_needed_to_match', 'P5_promotion_keeps_it_one_piece')] == ['SUPPORTED']*5
    assert ev['P4_data_needed_to_match']['smallest_matching_scale_index'] == 2
    refuted = demo.evaluate(rows_for(piece=0.03, distance=0.05, diag=0.02, mono=(0.02, 0.02, 0.02), closure=0.03, diag_p=0.07), CFG)
    assert refuted['P1_pieces_learn']['verdict'] == 'REFUTED' and refuted['P2_wiring_works']['verdict'] == 'REFUTED'
    assert refuted['P3_composition_beats_one_big_map']['verdict'] == 'REFUTED'
    assert refuted['P4_data_needed_to_match']['verdict'] == 'REFUTED'
    assert refuted['P5_promotion_keeps_it_one_piece']['verdict'] == 'REFUTED'
    middle = demo.evaluate(rows_for(piece=0.015, distance=0.03, diag=0.02, mono=(0.05, 0.015, 0.01)), CFG)
    # a composite that clears its absolute bar but not the straight-line floor is not SUPPORTED
    floor = demo.evaluate(rows_for(mix=0.03, linear=0.05), CFG)
    assert floor['P3_composition_beats_one_big_map']['verdict'] != 'SUPPORTED'
    weak = demo.evaluate(rows_for(distance=0.019, linear_distance=0.03), CFG)
    assert weak['P2_wiring_works']['verdict'] == 'INDETERMINATE'
    assert middle['P1_pieces_learn']['verdict'] == 'INDETERMINATE' and middle['P2_wiring_works']['verdict'] == 'INDETERMINATE'
    assert middle['P3_composition_beats_one_big_map']['verdict'] == 'INDETERMINATE'
    assert middle['P4_data_needed_to_match']['verdict'] == 'INDETERMINATE'


def test_one_seed_end_to_end_is_finite_and_repeatable():
    cfg = dict(demo.CONFIG, **demo.SMOKE)
    cfg['monolith'] = [{'M': 320, 'N': 600, 'seeds': 1}]
    cfg['mlp'] = [{'N': 600, 'epochs': 5}]
    first = demo.run_seed(cfg, 424242, 0)
    second = demo.run_seed(cfg, 424242, 0)
    keys = [k for k, v in first.items() if isinstance(v, float) and k != 'seed']
    assert all(np.isfinite(first[k]) for k in keys) and all(first[k] == second[k] for k in keys)
    assert {'distance', 'diag4', 'mix4', 'linear_mix4', 'closure', 'diag4_promoted', 'monolith_0', 'mlp_0'} <= set(first)


def test_latch_refuses_an_existing_run(tmp_path, monkeypatch):
    spec = json.loads((HERE/'SPEC.json').read_text())
    (tmp_path/'SPEC.json').write_text(json.dumps(spec))
    (tmp_path/'smoke_run').mkdir()
    monkeypatch.setattr(demo, 'HERE', tmp_path)
    with pytest.raises(SystemExit) as raised:
        demo.main_run(True)
    assert 'latch' in str(raised.value) and not list((tmp_path/'smoke_run').iterdir())


def test_preflight_requires_committed_clean_files(tmp_path, monkeypatch):
    import subprocess
    folder = tmp_path/'evidence'/'geometric_composition_demo'
    folder.mkdir(parents=True)
    for name in ('README.md', 'SPECIFICATION.md', 'SPEC.json', 'demo.py', 'test_demo.py'):
        (folder/name).write_text('x')
    git = lambda *a: subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *a], cwd=tmp_path,
                                    capture_output=True, text=True, check=True)
    git('init', '-q')
    monkeypatch.setattr(demo, 'HERE', folder)
    monkeypatch.setattr(demo, 'ROOT', tmp_path)
    with pytest.raises(SystemExit) as raised:
        demo.preflight(False)
    assert 'not committed' in str(raised.value)
    git('add', '.')
    git('commit', '-q', '-m', 'x')
    assert demo.preflight(False)['git_head']
    (folder/'demo.py').write_text('changed')
    with pytest.raises(SystemExit) as raised:
        demo.preflight(False)
    assert 'uncommitted' in str(raised.value)
    (folder/'run').mkdir()
    (folder/'demo.py').write_text('x')
    assert demo.preflight(False)['git_head']  # a run directory alone never blocks the check


def test_p4_and_p5_are_gated_by_the_composite_clearing_its_floor():
    poor = demo.evaluate(rows_for(mix=0.03, linear=0.05, mono=(0.2, 0.1, 0.08)), CFG)   # worse than the monolith series, but no floor
    assert poor['P3_composition_beats_one_big_map']['composite_clears_its_bar'] is False
    assert poor['P4_data_needed_to_match']['verdict'] == 'INDETERMINATE'
    matched = demo.evaluate(rows_for(mono=(0.01, 0.01, 0.01)), CFG)                       # the equal-budget monolith matches
    assert matched['P4_data_needed_to_match']['verdict'] == 'REFUTED'
    flat = demo.evaluate(rows_for(diag=0.03), CFG)                                        # wired diag4 0.03 vs straight line 0.05: no floor
    assert flat['P5_promotion_keeps_it_one_piece']['wired_diag4_clears_straight_line_floor'] is False
    assert flat['P5_promotion_keeps_it_one_piece']['verdict'] == 'INDETERMINATE'


def test_p4_pairs_seeds_for_the_ten_seed_monolith():
    rows = rows_for(mono=(0.2, 0.1, 0.5))
    for r in rows[10:]:
        r.pop('monolith_2')
        r['mix4'] = 0.9          # seeds without the large monolith must not enter its comparison
    ev = demo.evaluate(rows, dict(CFG, monolith=[{'M': 1, 'N': 1, 'seeds': 20}, {'M': 1, 'N': 1, 'seeds': 20}, {'M': 1, 'N': 1, 'seeds': 10}]))
    assert ev['P4_data_needed_to_match']['composite_median_same_seeds'][2] == pytest.approx(0.02)


def test_spec_json_matches_the_code_constants():
    spec = json.loads((HERE/'SPEC.json').read_text())
    assert spec['config'] == json.loads(json.dumps(demo.CONFIG))
    assert spec['smoke_overrides'] == json.loads(json.dumps(demo.SMOKE))
