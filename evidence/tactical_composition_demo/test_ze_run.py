"""Mechanics checks for the registered 0e harness (ze_run.py): the verdict rules on synthetic seeds, every gate, and one real tiny seed end to end.

    .venv/bin/python -m pytest -q -p no:cacheprovider evidence/tactical_composition_demo/test_ze_run.py
"""
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ze_run as R  # noqa: E402

CELLS = ['OO', 'LO', 'OL', 'LL', 'JJ', 'JL', 'LJ', 'DO', 'OD', 'OO|default', 'FpO', 'OFp', 'LL|default', 'LL|wrong', 'LL|zero',
         'LL|noise_0.02', 'LL|wrongfrac_0.01', 'LL|scale_0.9', 'LL|scale_1.1', 'LL|noise_0.05', 'LL|noise_0.1', 'LL|wrongfrac_0.05', 'LL|wrongfrac_0.1',
         'LL|scale_0.5', 'LL|scale_2', 'OO|scale_0.9', 'OO|scale_1.1', 'OO|noise_0.02', 'OO|wrongfrac_0.01', 'R', 'Fp', 'Fflat']
FIXED = [c for c in CELLS if c not in ('R',)]+['LL|reverse', 'LL|relabel', 'LL|sham', 'OO|reverse']

GOOD_WIN = {'OO': 0.76, 'LO': 0.76, 'OL': 0.74, 'LL': 0.74, 'JJ': 0.74, 'JL': 0.75, 'LJ': 0.73, 'DO': 0.61, 'OD': 0.38, 'OO|default': 0.59, 'FpO': 0.78, 'OFp': 0.74,
            'LL|default': 0.57, 'LL|wrong': 0.48, 'LL|zero': 0.09, 'LL|noise_0.02': 0.739, 'LL|wrongfrac_0.01': 0.741, 'LL|scale_0.9': 0.69, 'LL|scale_1.1': 0.72,
            'LL|noise_0.05': 0.73, 'LL|noise_0.1': 0.73, 'LL|wrongfrac_0.05': 0.72, 'LL|wrongfrac_0.1': 0.70, 'LL|scale_0.5': 0.03, 'LL|scale_2': 0.59,
            'OO|scale_0.9': 0.64, 'OO|scale_1.1': 0.74, 'OO|noise_0.02': 0.76, 'OO|wrongfrac_0.01': 0.757, 'R': 0.43, 'Fp': 0.69, 'Fflat': 0.45}
GOOD_FID = {c: 0.97 for c in FIXED}
GOOD_FID.update({'OO': 1.0, 'LO': 0.99, 'OL': 0.98, 'LL': 0.973, 'JJ': 0.954, 'JL': 0.958, 'LJ': 0.969, 'LL|reverse': 0.22, 'OO|reverse': 0.27, 'LL|relabel': 0.973,
                 'LL|sham': 0.973, 'LL|noise_0.02': 0.969, 'LL|wrongfrac_0.01': 0.964, 'LL|scale_0.9': 0.869, 'LL|scale_1.1': 0.876, 'OO|scale_0.9': 0.881,
                 'OO|scale_1.1': 0.865, 'LL|default': 0.62})


def rows_for(win=None, fid=None, prequal=None, seeds=30, noise=0.004):
    win, fid = dict(GOOD_WIN, **(win or {})), dict(GOOD_FID, **(fid or {}))
    pq = {'aim_admissible': 0.99, 'n_unique_best': 14000, 'move_success': 0.98, 'hold': 0.98, 'approach': 0.98, 'backoff': 0.96, 'n_hold': 3900, 'n_approach': 9300,
          'n_backoff': 1400}
    pq.update(prequal or {})
    rng = np.random.default_rng(0)
    rows = []
    for s in range(seeds):
        shift = rng.normal(0, noise)
        r = {'seed': s, 'seconds': 500.0, 'params': {'L': 787, 'J': 9283, 'Fp': 2313, 'Fflat': 20997}, 'oracle_queries': {'J': 2048000, 'Fp': 8000},
             'prequal': {'L': dict(pq), 'J': dict(pq)}, 'play': {}, 'fixed': {}}
        for c in CELLS:
            for o in R.OPP:
                r['play']['%s_%s' % (c, o)] = {'score': win[c]+shift+rng.normal(0, noise), 'win': 1, 'loss': 1, 'draw': 0, 'timeout': 0}
        for c in FIXED:
            r['fixed'][c] = {k: fid[c]+rng.normal(0, noise/4) for k in ('a_joint', 'a_macro', 'a_hold', 'a_approach', 'a_backoff', 'a_target_admissible')}
        rows.append(r)
    return rows


def cfg():
    c = dict(R.BASE)
    c['ref_distance'] = 4.97
    return c


def test_a_good_world_supports_every_claim_and_passes_every_gate():
    out = R.evaluate(rows_for(), cfg())
    g = out['gates']
    assert g['headroom_ok'] and all(g['teacher_necessity_ok'].values()) and g['baselines']['Fp']['qualified'] and not g['baselines']['Fflat']['qualified']
    assert out['A1_replacement_of_scripted_pieces']['verdict'] == 'SUPPORTED', [c['name'] for c in out['A1_replacement_of_scripted_pieces']['components'] if not c['passed']]
    assert out['A2_swap_with_conventional_policy']['verdict'] == 'SUPPORTED' and g['baselines']['JJ']['qualified']
    assert out['B1_useful_connection']['verdict'] == 'SUPPORTED'
    assert out['B2_stable_within_envelope']['verdict'] == 'SUPPORTED', [c['name'] for c in out['B2_stable_within_envelope']['components'] if not c['passed']]
    assert out['B3_stronger_than_conventional']['verdict'] == 'SUPPORTED'


def test_b3_is_refuted_when_the_conventional_policy_plays_as_well_and_blocked_when_it_is_not_qualified():
    out = R.evaluate(rows_for(win={'Fp': 0.745}), cfg())
    assert out['B3_stronger_than_conventional']['verdict'] == 'REFUTED'                    # LL - Fp about -0.005: clearly below 0.03
    out = R.evaluate(rows_for(win={'Fp': 0.44}), cfg())                                    # conventional baseline barely above rush: gate fails
    assert out['B3_stronger_than_conventional']['verdict'].startswith('INDETERMINATE (gate')


def test_b1_needs_the_connection_necessity_gate_and_a_sensitive_directed_control():
    out = R.evaluate(rows_for(win={'OO|default': 0.76}), cfg())                            # the teacher does not need the connection
    assert out['B1_useful_connection']['verdict'].startswith('INDETERMINATE (gate: connection necessity')
    out = R.evaluate(rows_for(fid={'LL|reverse': 0.95}), cfg())                            # reversing the message barely matters: the assay is insensitive
    assert out['B1_useful_connection']['verdict'] == 'REFUTED'
    out = R.evaluate(rows_for(win={'LL|default': 0.74}), cfg())                            # a default message works as well: the connection is not useful
    assert out['B1_useful_connection']['verdict'] == 'REFUTED'


def test_replacement_is_refuted_by_a_clear_loss_and_prequalification_is_part_of_it():
    out = R.evaluate(rows_for(win={'LL': 0.60, 'OL': 0.60}), cfg())
    assert out['A1_replacement_of_scripted_pieces']['verdict'] == 'REFUTED'
    out = R.evaluate(rows_for(prequal={'backoff': 0.70}), cfg())
    assert out['A1_replacement_of_scripted_pieces']['verdict'] == 'REFUTED'


def test_scale_faults_are_judged_relative_to_the_teacher():
    same_as_teacher = R.evaluate(rows_for(win={'LL|scale_0.9': 0.62, 'OO|scale_0.9': 0.64}, fid={'LL|scale_0.9': 0.86, 'OO|scale_0.9': 0.88}), cfg())
    assert same_as_teacher['B2_stable_within_envelope']['verdict'] == 'SUPPORTED'          # a large loss that the teacher also suffers is the task, not the wire
    worse = R.evaluate(rows_for(win={'LL|scale_0.9': 0.50}), cfg())
    assert worse['B2_stable_within_envelope']['verdict'] == 'REFUTED'                      # 0.24 loss against the teacher's 0.12


def test_an_absolute_fault_loss_and_unrepeatable_seeds_break_stability():
    out = R.evaluate(rows_for(win={'LL|noise_0.02': 0.65}), cfg())
    assert out['B2_stable_within_envelope']['verdict'] == 'REFUTED'
    out = R.evaluate(rows_for(win={'LL': 0.50, 'LO': 0.76}, noise=0.06), cfg())             # LL only 0.07 above rush and noisy
    assert out['B2_stable_within_envelope']['verdict'] != 'SUPPORTED'


def test_a_boundary_value_is_indeterminate():
    """An exactly representable boundary (0.75 - 0.6875 = 0.0625 in binary floating point): a value ON the bar is INDETERMINATE, never SUPPORTED or REFUTED."""
    c = cfg()
    c['bars'] = dict(c['bars'], stronger=0.0625)
    out = R.evaluate(rows_for(win={'LL': 0.75, 'Fp': 0.6875}, noise=0.0), c)
    comp = out['B3_stronger_than_conventional']['components'][0]
    assert comp['interval']['lo'] == comp['interval']['hi'] == 0.0625
    assert out['B3_stronger_than_conventional']['verdict'] == 'INDETERMINATE'


def test_r1_normalized_negative_witness_uses_the_adjusted_error():
    """Codex review R1, adapted to the corrected per-claim error 0.01: headroom exactly 0.60; the default cut's gains are 0.025 in 24 seeds and 0.035 in 6.
    The positive ratio interval (ranks 7 and 24) has upper bound 0.025 / 0.60 < 0.05, but the adjusted negative interval (ranks 6 and 25) reaches 0.035 / 0.60 > 0.05:
    no negative witness, so B1 must be INDETERMINATE, not REFUTED."""
    rows = rows_for(noise=0.0)
    for r in rows:
        for o in R.OPP:
            r['play']['OO_'+o]['score'], r['play']['R_'+o]['score'] = 0.9, 0.3
            r['play']['OO|default_'+o]['score'] = 0.6
            r['play']['LL_'+o]['score'] = 0.8
            r['play']['LL|default_'+o]['score'] = 0.8-(0.025 if r['seed'] < 24 else 0.035)
    out = R.evaluate(rows, cfg())
    comp = next(c for c in out['B1_useful_connection']['components'] if c['name'] == 'normalized win gain over LL|default')
    assert comp['interval']['hi'] < 0.05 < comp['negative_interval']['hi'] and not comp['passed'] and not comp['negative_witness']
    assert out['B1_useful_connection']['verdict'] == 'INDETERMINATE'


def test_a_nonpositive_headroom_gives_no_ratio_and_gates_b1():
    out = R.evaluate(rows_for(win={'R': 0.76}, noise=0.0), cfg())                      # teacher equals rush: headroom 0
    comps = [c for c in out['B1_useful_connection']['components'] if c['name'].startswith('normalized')]
    assert all(c['interval'] is None and not c['negative_witness'] for c in comps)
    assert out['B1_useful_connection']['verdict'].startswith('INDETERMINATE (gate')


def test_r2_aim_and_move_necessity_are_diagnostics_and_gate_no_claim():
    out = R.evaluate(rows_for(win={'DO': 0.76, 'OD': 0.76}), cfg())
    assert not out['gates']['teacher_necessity_ok']['aim'] and not out['gates']['teacher_necessity_ok']['move']
    assert 'diagnostics only' in out['gates']['map']['aim_necessity, move_necessity']
    assert out['A1_replacement_of_scripted_pieces']['verdict'] == 'SUPPORTED' and out['B1_useful_connection']['verdict'] == 'SUPPORTED'


def test_r5_swaps_with_an_unqualified_host_are_gated_but_replacement_of_scripted_pieces_stands():
    out = R.evaluate(rows_for(win={'JJ': 0.43, 'R': 0.43, 'JL': 0.74, 'LJ': 0.74}), cfg())
    assert not out['gates']['baselines']['JJ']['qualified']
    assert out['A2_swap_with_conventional_policy']['verdict'].startswith('INDETERMINATE (gate: J')
    assert out['A1_replacement_of_scripted_pieces']['verdict'] == 'SUPPORTED'


def test_a_real_tiny_seed_runs_end_to_end_and_evaluates(tmp_path):
    c = dict(cfg(), **R.SMOKE)
    c['run_dir'] = str(tmp_path)
    rows = [R.run_seed(c, 2**90+31, s) for s in range(3)]
    for r in rows:
        assert set(r['play']) == {'%s_%s' % (cell, o) for cell in CELLS for o in R.OPP}
        assert set(r['fixed']) == set(FIXED) and r['params']['L'] == 787
        assert r['fixed']['LL|relabel']['a_joint'] == r['fixed']['LL']['a_joint'] == r['fixed']['LL|sham']['a_joint']
    assert sorted(p.name for p in (tmp_path/'models').iterdir())[:2] == ['seed_00_Fflat.npz', 'seed_00_Fp.npz']
    out = R.evaluate(rows, c)
    for k in ('A1_replacement_of_scripted_pieces', 'A2_swap_with_conventional_policy', 'B1_useful_connection', 'B2_stable_within_envelope', 'B3_stronger_than_conventional'):
        assert isinstance(out[k]['verdict'], str)
    with pytest.raises(ValueError, match='undersized'):
        R.run_seed(dict(c, require_counts=True, min_unique_best=10**9), 2**90+31, 0)


def test_the_load_threshold_is_enforced_before_a_recorded_run(monkeypatch, tmp_path):
    import json
    spec = {'config': dict(cfg(), max_load_1min=1.0), 'entropy': 2**90+1, 'smoke_entropy': 2**90+2, 'smoke_overrides': {}}
    monkeypatch.setattr(R, 'HERE', tmp_path)
    (tmp_path/'SPEC_0E.json').write_text(json.dumps(spec))
    monkeypatch.setattr(R.os, 'getloadavg', lambda: (50.0, 50.0, 50.0))
    with pytest.raises(SystemExit, match='load'):
        R.main_run(smoke=False)


def test_a_median_above_the_bar_is_not_enough_the_interval_must_clear_it():
    out = R.evaluate(rows_for(win={'Fp': 0.70}, noise=0.03), cfg())                          # LL - Fp has median about 0.04 > 0.03 but a noisy interval
    comp = out['B3_stronger_than_conventional']['components'][0]
    assert comp['interval']['median'] > 0.03 and comp['interval']['lo'] < 0.03
    assert out['B3_stronger_than_conventional']['verdict'] == 'INDETERMINATE'


def test_the_conventional_policy_path_rejects_invalid_actions():
    """Codex registration review R3 on the flat/per-slot policy path used in closed-loop play."""
    import tactics as T
    rng = np.random.default_rng(1)
    world = T.World(T.SEEN_MIXES[1], T.SEEN_MIXES[2], rng)
    own, enemies = world.observe(0, 0)

    class Bad:
        def __init__(self, ch, st):
            self.ch, self.st = ch, st

        def act(self, A):
            return np.array(self.ch), np.array(self.st, float)
    with pytest.raises(ValueError, match='out of range'):
        R.flat_policy(Bad([-1], [[0.0, 0.0]]))(None)(own, enemies)
    with pytest.raises(ValueError, match='finite'):
        R.flat_policy(Bad([0], [[np.nan, 0.0]]))(None)(own, enemies)
    step, target, fire = R.flat_policy(Bad([1], [[0.5, 0.0]]))(None)(own, enemies)
    assert target == 1 and fire is False and step.tolist() == [0.5, 0.0]
