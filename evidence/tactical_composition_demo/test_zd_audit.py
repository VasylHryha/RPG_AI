"""Additional mechanics checks for experiment 0d Part A, added AFTER the recorded run (2026-10-04 recheck) because the audits found untested branches. A new file: test_zd.py, zd_run.py,
zd_models.py and tcd_common/ are hashed into the run record and are not edited. Run once from the repository root:

    .venv/bin/python -m pytest -q -p no:cacheprovider evidence/tactical_composition_demo/test_zd_audit.py
"""
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tactics as T  # noqa: E402
import test_zd as TZ  # noqa: E402
import verify_run_0d as V  # noqa: E402
import zd_models as Z  # noqa: E402
import zd_run as R  # noqa: E402

FLAT = {'F0': 0.47, 'F1': 0.55, 'F2': 0.54}


def evaluate(means, win, **cfg_kw):
    cfg = TZ.cfg_for(**cfg_kw)
    return R.evaluate(TZ.synthetic_rows(means, win=win, cfg=cfg), cfg)


def win(**over):
    base = {'teacher': 0.65, 'rush': 0.40, 'F0': 0.40, 'F*': 0.42, 'C': 0.63, 'S1': 0.62}
    base.update(over)
    return base


def test_v1_refuted_is_discordant_when_play_says_the_wired_unit_is_clearly_better():
    # fidelity: C is only 0.02 ahead (below delta_sup 0.06 -> REFUTED); play: C is 0.30 ahead (lo(W) >= delta_sup) -> discordant
    out = evaluate(dict(F0=0.50, F1=0.50, F2=0.50, C=0.52, S1=0.52), win(**{'C': 0.70, 'F*': 0.40, 'S1': 0.70}))
    assert 'discordant' in out['V1_the_wired_unit_beats_the_tuned_flat_model']['verdict']
    quiet = evaluate(dict(F0=0.50, F1=0.50, F2=0.50, C=0.52, S1=0.52), win(**{'C': 0.50, 'F*': 0.50, 'S1': 0.50}))
    assert quiet['V1_the_wired_unit_beats_the_tuned_flat_model']['verdict'] == 'REFUTED'


def test_each_v2_discordance_branch():
    # SEPARATE_BETTER (C 0.15 ahead on fidelity) but play says S1 is clearly better (hi(W) < 0) -> discordant
    out = evaluate(dict(FLAT, C=0.95, S1=0.80), win(**{'C': 0.55, 'S1': 0.70}))
    assert 'discordant' in out['V2_training_mode_C_versus_S1']['verdict'] and out['V2_training_mode_C_versus_S1']['label_before_gates'] == 'SEPARATE_BETTER'
    # JOINT_BETTER (S1 ahead on fidelity) but play says C is clearly better (lo(W) > 0) -> discordant
    out = evaluate(dict(FLAT, C=0.90, S1=0.99), win(**{'C': 0.70, 'S1': 0.60}))
    assert 'discordant' in out['V2_training_mode_C_versus_S1']['verdict'] and out['V2_training_mode_C_versus_S1']['label_before_gates'] == 'JOINT_BETTER'
    # EQUIVALENT but play says S1 is better by at least delta_eq (hi(W) <= -delta_eq) -> discordant
    out = evaluate(dict(FLAT, C=0.95, S1=0.94), win(**{'C': 0.60, 'S1': 0.70}))
    assert 'discordant' in out['V2_training_mode_C_versus_S1']['verdict'] and out['V2_training_mode_C_versus_S1']['label_before_gates'] == 'EQUIVALENT'
    # and the matching consistent cases are not discordant
    assert evaluate(dict(FLAT, C=0.95, S1=0.80), win(**{'C': 0.70, 'S1': 0.60}))['V2_training_mode_C_versus_S1']['verdict'] == 'SEPARATE_BETTER'
    assert evaluate(dict(FLAT, C=0.90, S1=0.99), win(**{'C': 0.60, 'S1': 0.70}))['V2_training_mode_C_versus_S1']['verdict'] == 'JOINT_BETTER'


def test_the_comparator_follows_f_star():
    means = dict(F0=0.47, F1=0.55, F2=0.70, C=0.95, S1=0.94)                       # F2 is the better flat model here
    as_f1 = evaluate(means, win(), f_star='F1')
    as_f2 = evaluate(means, win(), f_star='F2')
    assert as_f1['V1_the_wired_unit_beats_the_tuned_flat_model']['E1']['median'] == pytest.approx(0.40, abs=0.01)
    assert as_f2['V1_the_wired_unit_beats_the_tuned_flat_model']['E1']['median'] == pytest.approx(0.25, abs=0.01)
    assert as_f2['V1_the_wired_unit_beats_the_tuned_flat_model']['F_star'] == 'F2'
    assert as_f2['V4_the_recorded_baseline_was_under_tuned']['T1']['median'] == pytest.approx(0.23, abs=0.01)    # T1 = A(F*) - A(F0)


def test_the_recorded_flat_recipe_is_forced_for_f0_and_the_step_cap_applies():
    cfg = TZ.cfg_for(hps_step_cap=50)
    assert R.hp_for(cfg, 'F0') == {'hidden': 15, 'lr': 0.003, 'wd': 0.0, 'steps': 50}
    assert R.hp_for(TZ.cfg_for(), 'F0') == R.RECORDED_F0 and R.hp_for(TZ.cfg_for(), 'C') == TZ.cfg_for()['hps']['C']


def test_a_stratum_below_the_minimum_stops_the_seed_instead_of_recording_it():
    cfg = dict(TZ.tiny_cfg(), require_strata=True, min_stratum=10**6)
    out = R.seed_job((cfg, 2**90+9, 0))
    assert out['status'] == 'ERROR' and 'stratum below' in out['error']


def test_nested_source_states_and_the_saved_models_are_the_primary_n(tmp_path):
    cfg = dict(TZ.tiny_cfg(), run_dir=str(tmp_path))
    entropy = 2**90+11
    stored = R.run_seed(cfg, entropy, 0)
    n = cfg['n_primary']
    # the saved weights are the primary-N models: rebuilt, they reproduce the recorded primary-N scores exactly (and not the other Ns')
    pool = T.collect(V.stream(entropy, 2, 0), cfg['test_episodes'], T.SEEN_MIXES)
    A = Z.Arrays(pool, T.labels(pool))
    R.A_ANGLE[0], R.A_MIN[0] = cfg['angle_deg'], cfg['min_stratum']
    assert R.seed_digest(pool) == stored['test_digest']
    for name in R.MODELS:
        z = np.load(tmp_path/'models'/('seed_00_%s.npz' % name))
        score = R.score_model(V.rebuild(name, z, None), A)['a_joint']
        assert score == stored['a_joint_%s_%d' % (name, n)], name
    # nested: the source states of the smaller N are a prefix of those of the larger N (one permutation)
    order = V.stream(entropy, 4, 0).permutation(len(T.collect(V.stream(entropy, 1, 0), cfg['train_episodes'], T.SEEN_MIXES)['own']))
    assert list(order[:100]) == list(order[:300][:100])


def test_the_enforced_and_unenforced_gates_are_what_the_specification_says():
    """c_adequate is recorded in the configuration but, unlike s1_adequate, is not read by evaluate(): it was fixed True from development before the run (a known gap)."""
    src = (HERE/'zd_run.py').read_text()
    assert src.count("cfg['s1_adequate']") >= 1 and "cfg['c_adequate']" not in src.split('def evaluate')[1].split('def build_config')[0]
