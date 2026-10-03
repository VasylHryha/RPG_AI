"""Mechanics checks for the 0d Part A models (zd_models.py). Run once from the repository root after the code is final:

    .venv/bin/python -m pytest -q -p no:cacheprovider evidence/tactical_composition_demo/test_zd.py
"""
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tactics as T  # noqa: E402
import zd_models as Z  # noqa: E402
from tcd_common import metrics  # noqa: E402


@pytest.fixture(scope='module')
def world():
    rng = np.random.default_rng(3)
    pool = T.collect(rng, 8, T.SEEN_MIXES)
    lab = T.labels(pool)
    return pool, lab, Z.Arrays(pool, lab)


def test_vectorized_teacher_move_equals_the_scalar_rule():
    rng = np.random.default_rng(1)
    rel = rng.normal(0, 6, (4000, 2))
    rel[:5] = 0.0
    pref = rng.choice([1.2, 2.5, 3.5, 5.0], 4000)
    got = Z.teacher_move_batch(rel, pref)
    want = np.array([T.teacher_move(r, p) for r, p in zip(rel, pref)])
    assert np.array_equal(got, want)


def test_array_features_equal_the_recorded_feature_functions(world):
    pool, lab, A = world
    for k in (0, 7, len(A.own)//2, len(A.own)-1):
        own, en = pool['own'][k], pool['enemies'][k]
        assert np.array_equal(A.MONO[k], T.mono_features(own, en))
        for j in range(Z.N):
            assert np.array_equal(A.AIMX[k, j], T.aim_features(own, en, j))
        assert np.array_equal(A.move_input(A.REL[k:k+1, 0], A.PREF[k:k+1])[0], T.move_features(en[0, 1:3], own[4]))


def test_trainer_with_no_weight_decay_reproduces_the_recorded_recipe_exactly(world):
    _, _, A = world
    X, Y = A.MONO[:600], np.c_[A.move[:600], np.where(A.alive[:600], A.scores[:600], -1.0)]
    rec = T.MLP(X.shape[1], 16, 5, np.random.default_rng(5))
    rec.fit(X, Y, np.random.default_rng(6), 300)
    xs, ys = Z.Std(X), Z.Std(Y)
    net = Z.Net(X.shape[1], 16, 5, np.random.default_rng(5))
    Zi, Tn = xs.f(X), ys.f(Y)

    def grad_fn(b):
        out, cache = net.forward(Zi[b])
        return net.backward(cache, 2.0*(out-Tn[b])/(len(b)*5))[0]
    Z.adam_train(net.params(), grad_fn, len(Zi), 300, 128, 0.003, 0.0, np.random.default_rng(6), [True]*3+[False]*3)
    for a, b in zip(rec.W+rec.b, net.params()):
        assert np.allclose(a, b, atol=1e-10)
    assert np.allclose(rec.predict(X[:50]), ys.inv(net.forward(xs.f(X[:50]))[0]), atol=1e-9)


def numeric_grad(f, params, eps=1e-6):
    out = []
    for p in params:
        g = np.zeros_like(p)
        it = np.nditer(p, flags=['multi_index'])
        for _ in it:
            i = it.multi_index
            old = p[i]
            p[i] = old+eps
            hi = f()
            p[i] = old-eps
            lo = f()
            p[i] = old
            g[i] = (hi-lo)/(2*eps)
        out.append(g)
    return out


def small_s1(world, hidden=5, seed=0):
    _, _, A = world
    idx = np.random.default_rng(seed).choice(A.n, 200, replace=False)
    m = Z.Wired('S1')
    m.set_standardizers(A, idx)
    rng = np.random.default_rng(seed+1)
    m.scorer, m.head = Z.Net(7, hidden, 1, rng), Z.Net(3, hidden, 2, rng)
    return A, idx, m


def multi_batch(A, idx, size=24):
    return np.array([k for k in idx if A.alive[k].sum() > 1][:size])


def test_network_backward_matches_finite_differences(world):
    rng = np.random.default_rng(2)
    net = Z.Net(4, 6, 3, rng)
    X, T_ = rng.normal(size=(9, 4)), rng.normal(size=(9, 3))

    def loss():
        return float(np.sum((net.forward(X)[0]-T_)**2))
    out, cache = net.forward(X)
    grads, dX = net.backward(cache, 2.0*(out-T_))
    for a, n in zip(grads, numeric_grad(loss, net.params())):
        assert np.allclose(a, n, rtol=1e-5, atol=1e-7)
    xnum = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            old = X[i, j]
            X[i, j] = old+1e-6
            hi = loss()
            X[i, j] = old-1e-6
            lo = loss()
            X[i, j] = old
            xnum[i, j] = (hi-lo)/2e-6
    assert np.allclose(dX, xnum, rtol=1e-5, atol=1e-7)


def test_s1_soft_mode_gradient_matches_finite_differences(world):
    """The whole differentiable route: score loss, step loss, and the path from the step loss through the selection weights into the scorer."""
    A, idx, m = small_s1(world)
    b = multi_batch(A, idx)
    labels = np.random.default_rng(9).normal(0, 0.7, (len(b), 2))                 # fixed step labels so the derivative is smooth
    params = m.scorer.params()+m.head.params()
    loss, grads, _ = Z.s1_step(m, A, b, 'soft', labels=labels)
    num = numeric_grad(lambda: Z.s1_step(m, A, b, 'soft', labels=labels)[0], params)
    for a, n in zip(grads, num):
        assert np.allclose(a, n, rtol=1e-4, atol=1e-7), np.abs(a-n).max()
    # the selection route is really exercised: with it cut the scorer gradient differs
    assert any(np.abs(g).max() > 1e-8 for g in grads[:6])


def test_s1_straight_through_gradient_equals_the_derivative_of_its_surrogate(world):
    """Forward = hard argmax enemy; backward = softmax derivative. The exact derivative of (hard + soft - stopgrad(soft)) is the ST gradient."""
    A, idx, m = small_s1(world, seed=4)
    b = multi_batch(A, idx)
    _, _, aux = Z.s1_step(m, A, b, 'soft', labels=np.zeros((len(b), 2)))
    ref = aux['soft'].copy()
    labels = np.random.default_rng(11).normal(0, 0.7, (len(b), 2))
    params = m.scorer.params()+m.head.params()
    loss, grads, _ = Z.s1_step(m, A, b, 'st', labels=labels)
    surrogate_loss, surrogate_grads, _ = Z.s1_step(m, A, b, 'surrogate', labels=labels, ref_soft=ref)
    assert surrogate_loss == pytest.approx(loss, rel=1e-12)                       # the surrogate's VALUE is the hard-selection loss
    num = numeric_grad(lambda: Z.s1_step(m, A, b, 'surrogate', labels=labels, ref_soft=ref)[0], params)
    for a, n, s in zip(grads, num, surrogate_grads):
        assert np.allclose(a, n, rtol=1e-4, atol=1e-7), np.abs(a-n).max()
        assert np.allclose(a, s)
    # and the ST route differs from a hard forward with no selection gradient: cutting it changes the scorer gradient
    cut = Z.s1_step(m, A, b, 'st', labels=labels)[1][:6]
    assert any(np.abs(g).max() > 1e-8 for g in cut)


def test_s1_uses_the_oracle_label_on_its_own_selected_enemy(world):
    A, idx, m = small_s1(world, seed=6)
    b = multi_batch(A, idx)
    _, _, aux = Z.s1_step(m, A, b, 'st')
    chosen, _ = m.act(Z.Arrays({'own': A.own[b], 'enemies': A.en[b]}))
    hard = A.REL[b][np.arange(len(b)), chosen]
    labels = Z.teacher_move_batch(hard, A.PREF[b])
    assert Z.s1_step(m, A, b, 'st')[0] == pytest.approx(Z.s1_step(m, A, b, 'st', labels=labels)[0], rel=1e-12)


def test_flat_discrete_head_quantization_error_is_under_the_tolerance():
    rng = np.random.default_rng(0)
    ang = rng.uniform(0, 2*np.pi, 20000)
    step = np.stack([np.cos(ang), np.sin(ang)], axis=1)
    back = Z.class_step(Z.direction_class(step))
    err = np.degrees(np.arccos(np.clip((back*step).sum(1), -1, 1)))
    assert err.max() < 5.7 and err.max() > 5.0                                       # 180/32 = 5.625 degrees
    assert Z.direction_class(np.array([[0.1, 0.0], [0.0, 0.0]])).tolist() == [0, 0]
    assert Z.class_step(np.array([0]))[0].tolist() == [0.0, 0.0]


def test_no_model_sees_a_dead_enemy_as_chosen_and_every_model_trains_and_acts(world):
    pool, lab, A = world
    idx = Z.source_states(A.n, 600, np.random.default_rng(1))
    hp = {'hidden': 8, 'lr': 0.01, 'wd': 1e-4, 'steps': 400}
    for name in ('F0', 'F1', 'F2', 'C', 'S1'):
        model = Z.FITS[name](A, idx, dict(hp, steps=300) if name != 'F0' else hp, np.random.default_rng(2)) if name != 'F0' else None
        if model is None:
            continue
        chosen, step = model.act(A)
        assert chosen.shape == (A.n,) and step.shape == (A.n, 2) and np.isfinite(step).all()
        assert A.alive[np.arange(A.n), chosen].all(), name
        out = metrics.joint_action(chosen, step, pool, lab)
        assert 0.0 <= out['a_joint'] <= 1.0 and model.n_params > 0 and model.supervision > 0


def test_composed_and_s1_have_identical_architecture_and_parameter_count(world):
    _, _, A = world
    idx = Z.source_states(A.n, 400, np.random.default_rng(1))
    hp = {'hidden': 16, 'lr': 0.003, 'wd': 0.0, 'steps': 5}
    c, s = Z.fit_composed(A, idx, hp, np.random.default_rng(1)), Z.fit_s1(A, idx, hp, np.random.default_rng(1))
    assert c.n_params == s.n_params == (7*16+16+16*16+16+16+1)+(3*16+16+16*16+16+16*2+2)
    assert c.supervision == s.supervision and c.oracle_queries == 0 and s.oracle_queries == 5*128   # same label content; S1's extra oracle queries on its own choice are counted, not hidden


def test_matched_supervision_rows_for_the_pieces(world):
    _, _, A = world
    idx = Z.source_states(A.n, 300, np.random.default_rng(1))
    Xa, Ya = Z.aim_rows(A, idx)
    Xm, Ym = Z.move_rows(A, idx)
    assert len(Xa) == int(A.alive[idx].sum()) and len(Xm) == 300 and Xa.shape[1] == 7 and Xm.shape[1] == 3
    assert np.array_equal(Ya[:, 0], A.scores[idx][A.alive[idx]])
    k = idx[0]
    assert np.array_equal(Xm[0], T.move_features(A.pool['enemies'][k][A.target[k], 1:3], A.pool['own'][k][4]))


def test_policy_of_returns_a_valid_sandbox_action(world):
    pool, lab, A = world
    idx = Z.source_states(A.n, 300, np.random.default_rng(1))
    model = Z.fit_composed(A, idx, {'hidden': 8, 'lr': 0.01, 'wd': 0.0, 'steps': 50}, np.random.default_rng(1))
    policy = Z.policy_of(model)
    step, target, fire = policy(pool['own'][3], pool['enemies'][3])
    assert step.shape == (2,) and 0 <= target < Z.N and pool['enemies'][3][target, 0] > 0 and fire is False
    assert T.win_score(policy, T.SEEN_MIXES, T.OPPONENTS['rush'], np.random.default_rng(1), 1) in (0.0, 0.5, 1.0)


# ------------------------------------------------------------------ the registered harness and verdict rules (zd_run.py)

import zd_run as R  # noqa: E402

NS = (3000, 1000, 9000)


def cfg_for(**kw):
    cfg = dict(R.BASE_CONFIG, hps={n: {'hidden': 8, 'lr': 0.01, 'wd': 0.0, 'steps': 60} for n in ('F1', 'F2', 'C', 'S1')}, boot_entropy=2**90+777, resamples=800,
               c_adequate=True, s1_adequate=True, f_star='F1')
    cfg.update(kw)
    return cfg


def synthetic_rows(means, seeds=20, noise=0.004, win=None, cfg=None):
    """Rows with the keys evaluate() reads. means: model -> mean a_joint; win: policy -> mean win score (same for both opponents)."""
    cfg = cfg or cfg_for()
    rng = np.random.default_rng(0)
    win = win or {'teacher': 0.65, 'rush': 0.40, 'F0': 0.40, 'F*': 0.42, 'C': 0.63, 'S1': 0.62}
    rows = []
    for s in range(seeds):
        r = {'seed': s, 'seconds': 100.0}
        for m in R.MODELS:
            for n in NS:
                p = '%s_%d' % (m, n)
                shift = rng.normal(0, noise)
                r['a_joint_'+p] = means[m]+shift
                for k in ('a_target_admissible', 'move_alone_joint_on_teacher_target', 'independent_prediction', 'connection_gap', 'aim_alone_agree_corrected',
                          'step_angle_median_moving_deg', 'a_step_given_admissible', 'n_multi'):
                    r['%s_%s' % (k, p)] = 0.5
                for st in R.STRATA:
                    r['a_joint_stratum_%s_%s' % (st, p)], r['n_stratum_%s_%s' % (st, p)] = 0.5, 100
                r.update({'fit_seconds_'+p: 1.0, 'n_params_'+p: 100, 'supervision_'+p: 1000, 'oracle_queries_'+p: 0})
        for pol in R.POLICIES:
            for o in R.OPPONENTS:
                r['score_%s_%s' % (pol, o)] = win['F*' if pol == 'F*' else pol]+rng.normal(0, noise)
        rows.append(r)
    return rows


FLAT = {'F0': 0.47, 'F1': 0.55, 'F2': 0.54}


def test_verdicts_structure_explains_the_gain_when_s1_matches_c():
    out = R.evaluate(synthetic_rows(dict(FLAT, C=0.95, S1=0.94)), cfg_for())
    assert out['V1_the_wired_unit_beats_the_tuned_flat_model']['verdict'] == 'SUPPORTED'
    assert out['V2_training_mode_C_versus_S1']['verdict'] == 'EQUIVALENT'
    assert out['V3_structure_explains_the_gain']['verdict'] == 'SUPPORTED'
    assert out['V4_the_recorded_baseline_was_under_tuned']['verdict'] == 'SUPPORTED'
    assert out['V5_a_discrete_move_head_matters']['verdict'] == 'REFUTED'
    assert set(out['endpoint_coverage']) >= {'E0', 'E1', 'E2', 'E3', 'T1', 'T2', 'win_C_minus_S1'}


def test_verdicts_separate_teaching_adds_when_c_beats_s1_and_joint_adds_when_s1_beats_c():
    out = R.evaluate(synthetic_rows(dict(FLAT, C=0.95, S1=0.80)), cfg_for())
    assert out['V2_training_mode_C_versus_S1']['verdict'] == 'SEPARATE_BETTER' and out['V3_structure_explains_the_gain']['verdict'] == 'REFUTED'
    win = {'teacher': 0.65, 'rush': 0.40, 'F0': 0.40, 'F*': 0.42, 'C': 0.60, 'S1': 0.66}
    out = R.evaluate(synthetic_rows(dict(FLAT, C=0.90, S1=0.99), win=win), cfg_for())      # the reverse direction is a first-class outcome, not "not C"
    assert out['V2_training_mode_C_versus_S1']['verdict'] == 'JOINT_BETTER' and out['V3_structure_explains_the_gain']['verdict'] == 'INDETERMINATE'


def test_verdict_rows_for_the_flat_comparisons_and_an_inadequate_s1():
    flatwin = {p: 0.5 for p in ('teacher', 'rush', 'F0', 'F*', 'C', 'S1')}
    out = R.evaluate(synthetic_rows(dict(F0=0.50, F1=0.50, F2=0.50, C=0.52, S1=0.52), win=flatwin), cfg_for())
    assert out['V1_the_wired_unit_beats_the_tuned_flat_model']['verdict'] == 'REFUTED'    # C is only 0.02 ahead: below the superiority margin
    assert out['V4_the_recorded_baseline_was_under_tuned']['verdict'] == 'REFUTED' and out['V5_a_discrete_move_head_matters']['verdict'] == 'REFUTED'
    out = R.evaluate(synthetic_rows(dict(FLAT, C=0.95, S1=0.94)), cfg_for(s1_adequate=False))
    assert out['V2_training_mode_C_versus_S1']['verdict'].startswith('INDETERMINATE') and out['V3_structure_explains_the_gain']['verdict'] == 'INDETERMINATE'
    assert out['V1_the_wired_unit_beats_the_tuned_flat_model']['verdict'] == 'SUPPORTED'  # V1 does not depend on S1


def test_discordant_closed_loop_result_downgrades_the_verdict():
    win = {'teacher': 0.65, 'rush': 0.40, 'F0': 0.40, 'F*': 0.42, 'C': 0.70, 'S1': 0.55}   # fidelity says C = S1 but play says C is clearly better (0.15 >= the margin)
    out = R.evaluate(synthetic_rows(dict(FLAT, C=0.95, S1=0.94), win=win), cfg_for())
    assert out['V2_training_mode_C_versus_S1']['label_before_gates'] == 'EQUIVALENT'
    assert 'discordant' in out['V2_training_mode_C_versus_S1']['verdict'] and out['V3_structure_explains_the_gain']['verdict'] == 'INDETERMINATE'
    win = {'teacher': 0.65, 'rush': 0.40, 'F0': 0.40, 'F*': 0.80, 'C': 0.63, 'S1': 0.62}   # fidelity says C beats the flat model, play says the flat model wins
    out = R.evaluate(synthetic_rows(dict(FLAT, C=0.95, S1=0.94), win=win), cfg_for())
    assert 'discordant' in out['V1_the_wired_unit_beats_the_tuned_flat_model']['verdict']


def test_a_tiny_closed_loop_difference_does_not_make_equivalence_unreachable():
    win = {'teacher': 0.65, 'rush': 0.40, 'F0': 0.40, 'F*': 0.42, 'C': 0.63, 'S1': 0.62}   # C - S1 = 0.01 in play, far inside the 0.03 margin, with a tight interval that excludes 0
    out = R.evaluate(synthetic_rows(dict(FLAT, C=0.95, S1=0.94), win=win), cfg_for())
    w = out['V2_training_mode_C_versus_S1']['win_score_C_minus_S1']
    assert w['lo'] > 0 and out['V2_training_mode_C_versus_S1']['verdict'] == 'EQUIVALENT'


def test_boundary_values_are_strict_and_neither_supported_nor_refuted():
    cfg = cfg_for(delta_sup=0.25, delta_eq=0.125)
    means = dict(F0=0.25, F1=0.5, F2=0.5, C=0.75, S1=0.75)                                # C - F* is exactly 0.25 = delta_sup, with no noise
    out = R.evaluate(synthetic_rows(means, noise=0.0, cfg=cfg), cfg)
    assert out['V1_the_wired_unit_beats_the_tuned_flat_model']['verdict'] == 'INDETERMINATE'
    assert out['V1_the_wired_unit_beats_the_tuned_flat_model']['E1']['lo'] == 0.25
    assert out['V4_the_recorded_baseline_was_under_tuned']['verdict'] == 'SUPPORTED'      # T1 = 0.25 > 0.125


def test_a_missing_endpoint_stops_the_evaluation_instead_of_dropping_a_seed():
    rows = synthetic_rows(dict(FLAT, C=0.95, S1=0.94))
    rows[3]['a_joint_C_3000'] = None
    with pytest.raises(ValueError, match='missing'):
        R.evaluate(rows, cfg_for())


def tiny_cfg():
    return cfg_for(train_episodes=14, test_episodes=8, n_primary=200, n_extra=[100, 300], win_episodes=1, hps_step_cap=60, require_strata=False)


def test_a_real_seed_runs_end_to_end_is_deterministic_and_evaluates():
    cfg = tiny_cfg()
    entropy = 2**90+5
    first = R.run_seed(cfg, entropy, 0)
    again = R.run_seed(cfg, entropy, 0)
    keys = [k for k in first if not k.startswith(('seconds', 'fit_seconds', 'score_seconds'))]
    assert all(first[k] == again[k] for k in keys)                                           # deterministic given the entropy
    for m in R.MODELS:
        for n in (200, 100, 300):
            assert 0.0 <= first['a_joint_%s_%d' % (m, n)] <= 1.0 and first['n_params_%s_%d' % (m, n)] > 0
    assert first['oracle_queries_S1_200'] > 0 and first['oracle_queries_C_200'] == 0
    assert len(first['test_digest']) == 64 and all(0.0 <= first['score_%s_%s' % (p, o)] <= 1.0 for p in R.POLICIES for o in R.OPPONENTS)
    rows = [first]+[R.run_seed(cfg, entropy, s) for s in (1, 2)]
    out = R.evaluate(rows, cfg)
    assert all(isinstance(out[k]['verdict'], str) for k in out if k.startswith('V'))


def test_the_nested_source_states_and_weights_are_saved(tmp_path):
    cfg = dict(tiny_cfg(), run_dir=str(tmp_path))
    R.run_seed(cfg, 2**90+6, 0)
    saved = sorted(p.name for p in (tmp_path/'models').iterdir())
    assert saved == ['seed_00_%s.npz' % m for m in sorted(R.MODELS)]
    z = np.load(tmp_path/'models'/'seed_00_C.npz')
    assert 'scorer_0' in z.files and 'xa_m' in z.files and 'ym_s' in z.files
    assert 'mx' in np.load(tmp_path/'models'/'seed_00_F0.npz').files and 'xs_m' in np.load(tmp_path/'models'/'seed_00_F1.npz').files


def test_the_spec_builder_reads_the_committed_development_records(tmp_path):
    cfg = R.build_config()
    assert cfg['f_star'] in ('F1', 'F2') and set(cfg['hps']) == {'F1', 'F2', 'C', 'S1'} and cfg['seeds'] in (30, 45, 60)
    assert cfg['c_adequate'] is True and cfg['s1_adequate'] is True and cfg['delta_eq'] == 0.03 and cfg['delta_sup'] == 0.06
