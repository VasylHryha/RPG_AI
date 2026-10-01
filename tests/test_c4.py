"""Focused C4 contracts: model, ablations, interventions, detector, statistics, runner and registration."""

import copy
from unittest.mock import patch
import inspect
import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from geomind import c4_detect, run_c4
from geomind.c4_detect import active_unit, criteria_checks, detect, kick, locked_pairs, window_statistics
from geomind.c4_experiment import (ARMS, bootstrap_ci, causality_verdict, dose_response_verdict, evaluate_arm,
                                   gm_states, gm_statistic, hypothesis_verdicts, mg_phases, mg_states, mg_statistic,
                                   model_params, numerical_checks, probe_kick, wilson)
from geomind.c4_model import ABLATIONS, INTACT, Batch, neighbors, rhs, simulate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "experiments/c4_manifest.json").read_text())


def naive_neighbors(x, i, p):
    dist = [(np.linalg.norm(x[j] - x[i]), j) for j in range(len(x)) if j != i]
    ordered = sorted(range(len(dist)), key=lambda q: dist[q][0])[:p.k]
    return [dist[q][1] for q in ordered if dist[q][0] < p.radius]


def naive_rhs(x, th, omega, p, topology_positions=None):
    """Independent per-element reference of the R4 C4 equations; with a frozen phase topology the phase
    coupling uses the neighbors that topology_positions would have."""
    n = len(x)
    x_dot, th_dot = np.zeros_like(x), np.array(omega, dtype=float)
    for i in range(n):
        near = naive_neighbors(x, i, p)
        if near:
            fx = np.zeros(2)
            for j in near:
                r = np.linalg.norm(x[j] - x[i])
                fx += (x[j] - x[i]) / max(r, p.eps) * (p.A * (1 + p.J * np.cos(th[j] - th[i])) - p.B / max(r, p.eps))
            x_dot[i] = fx / len(near)
        coupled = naive_neighbors(topology_positions, i, p) if p.frozen_phase_topology else near
        if coupled:
            ft = 0.0
            for j in coupled:
                r = np.linalg.norm(x[j] - x[i])
                ft += p.K * (np.exp(-r * r) if p.distance_weighted else 1.0) * np.sin(th[j] - th[i])
            th_dot[i] += ft / len(coupled)
    return x_dot, th_dot


@pytest.mark.parametrize("name", sorted(ABLATIONS))
def test_rhs_matches_naive_reference(name):
    p = replace(ABLATIONS[name], k=4)
    rng = np.random.default_rng(1)
    x = rng.normal(size=(2, 10, 2)) * 2.0
    x[1, 0] += 50.0  # an isolated element: no neighbors within the radius
    th, omega = rng.uniform(-np.pi, np.pi, (2, 10)), rng.uniform(-0.5, 0.5, (2, 10))
    batch = Batch(p, 2)
    earlier = x + rng.normal(size=x.shape)  # a different configuration whose neighbors form the frozen topology
    got = rhs(x, th, omega, *neighbors(x, batch), batch, neighbors(earlier, batch))
    for b in range(2):
        want = naive_rhs(x[b], th[b], omega[b], p, earlier[b])
        assert np.allclose(got[0][b], want[0], atol=1e-13) and np.allclose(got[1][b], want[1], atol=1e-13)
    assert np.array_equal(got[0][1, 0], [0.0, 0.0]) and got[1][1, 0] == omega[1, 0]


def test_mixed_batch_equals_separate_runs():
    rng = np.random.default_rng(2)
    x, th, omega = rng.normal(size=(1, 12, 2)), rng.uniform(-3, 3, (1, 12)), np.zeros((1, 12))
    names = sorted(ABLATIONS)
    topology = neighbors(x, Batch(INTACT, 1))
    stacked = tuple(np.repeat(a, len(names), 0) for a in topology)
    mixed = simulate(np.repeat(x, len(names), 0), np.repeat(th, len(names), 0), np.repeat(omega, len(names), 0),
                     [ABLATIONS[n] for n in names], 0.02, 50, phase_topology=stacked)
    for i, n in enumerate(names):
        alone = simulate(x, th, omega, ABLATIONS[n], 0.02, 50, phase_topology=topology)
        assert np.allclose(mixed[0][i], alone[0][0], atol=1e-13) and np.allclose(mixed[1][i], alone[1][0], atol=1e-13)


def test_two_element_analytic_case():
    x = np.array([[[0.0, 0.0], [1.0, 0.0]]])
    th = np.array([[0.0, 0.5]])
    batch = Batch(INTACT, 1)
    x_dot, th_dot = rhs(x, th, np.zeros((1, 2)), *neighbors(x, batch), batch)
    assert x_dot[0, 0, 0] == pytest.approx(1.0 + 0.8 * np.cos(0.5) - 1.0, abs=1e-15)
    assert th_dot[0, 0] == pytest.approx(np.exp(-1.0) * np.sin(0.5), abs=1e-15)
    # An in-phase pair settles at r* = B / (A (1 + J)).
    end, _, _ = simulate(x, np.zeros((1, 2)), np.zeros((1, 2)), INTACT, 0.02, 2000)
    assert np.linalg.norm(end[0, 1] - end[0, 0]) == pytest.approx(1.0 / 1.8, abs=1e-9)


def test_numerical_checks_pass_on_development_worlds():
    out = numerical_checks(MANIFEST, model_params(MANIFEST), MANIFEST["seeds"]["development_entropy"])
    assert out["verdict"] == "PASS"
    for arm in ARMS:
        assert out[arm]["held_order_ratio"] > 12 and out[arm]["equivariance_error"] < 1e-12


def test_ablations_remove_exactly_their_coupling_term():
    rng = np.random.default_rng(3)
    x = rng.normal(size=(1, 12, 2))
    th_a, th_b = rng.uniform(-3, 3, (1, 12)), rng.uniform(-3, 3, (1, 12))
    omega = rng.uniform(-0.5, 0.5, (1, 12))
    blind = ABLATIONS["no_mode_to_geometry"]
    # J = 0: positions never depend on phases (bit for bit).
    assert np.array_equal(simulate(x, th_a, omega, blind, 0.02, 100)[0], simulate(x, th_b, omega, blind, 0.02, 100)[0])
    assert not np.array_equal(simulate(x, th_a, omega, INTACT, 0.02, 100)[0], simulate(x, th_b, omega, INTACT, 0.02, 100)[0])
    # Complete geometry -> mode ablation: phases never depend on positions (bit for bit).
    blind_phases = ABLATIONS["no_geometry_to_mode"]
    topology = neighbors(x, Batch(INTACT, 1))
    assert np.array_equal(simulate(x, th_a, omega, blind_phases, 0.02, 100, phase_topology=topology)[1],
                          simulate(1.5 * x + 0.3, th_a, omega, blind_phases, 0.02, 100, phase_topology=topology)[1])
    for single in ("no_distance_weight", "frozen_topology"):
        assert not np.array_equal(simulate(x, th_a, omega, ABLATIONS[single], 0.02, 100, phase_topology=topology)[1],
                                  simulate(1.5 * x + 0.3, th_a, omega, ABLATIONS[single], 0.02, 100, phase_topology=topology)[1])
    with pytest.raises(ValueError, match="phase_topology"):
        simulate(x, th_a, omega, blind_phases, 0.02, 1)
    # w = 1: with the same neighbor sets, phase velocities do not depend on distances.
    batch = Batch(ABLATIONS["no_distance_weight"], 1)
    held = neighbors(x, batch)
    stretched = x * 1.3
    assert np.array_equal(rhs(x, th_a, omega, *held, batch)[1], rhs(stretched, th_a, omega, *held, batch)[1])
    intact = Batch(INTACT, 1)
    assert not np.array_equal(rhs(x, th_a, omega, *held, intact)[1], rhs(stretched, th_a, omega, *held, intact)[1])
    # J = K = 0: phases advance at their intrinsic rates only.
    clump = Batch(ABLATIONS["clump"], 1)
    assert np.array_equal(rhs(x, th_a, omega, *neighbors(x, clump), clump)[1], omega)


def test_interventions_hold_their_variables_bit_for_bit():
    rng = np.random.default_rng(4)
    x, th = rng.normal(size=(12, 2)), rng.uniform(-3, 3, 12)
    members = np.array([1, 3, 4, 7])
    delta = probe_kick(rng, len(members), 0.3)
    assert abs(delta.mean()) < 1e-15 and np.sqrt((delta ** 2).mean()) == pytest.approx(0.3, abs=1e-15)
    (cx, cth), (tx, tth) = gm_states(x, th, members, delta, 1.5)
    assert np.array_equal(cth, tth) and np.array_equal(cx, x) and np.array_equal(cth[members], th[members] + delta)
    others = np.setdiff1d(np.arange(12), members)
    assert np.array_equal(tx[others], x[others]) and np.array_equal(cth[others], th[others])
    assert np.allclose(tx[members].mean(0), x[members].mean(0), atol=1e-14)
    assert np.allclose(np.linalg.norm(tx[members] - tx[members[0]], axis=1),
                       1.5 * np.linalg.norm(x[members] - x[members[0]], axis=1), atol=1e-13)
    partial = mg_phases(rng, th, members, "rms:0.5") - th[members]
    assert abs(partial.mean()) < 1e-15 and np.sqrt((partial ** 2).mean()) == pytest.approx(0.5, abs=1e-15)
    new = mg_phases(rng, th, members, "uniform")
    assert np.all(np.abs(new) <= np.pi)
    (cx, cth), (tx, tth) = mg_states(x, th, members, new)
    assert np.array_equal(cx, tx) and np.array_equal(cth, th) and np.array_equal(tth[members], new)
    assert np.array_equal(tth[others], th[others])


def test_kick_has_fixed_size():
    rng = np.random.default_rng(5)
    x, th = rng.normal(size=(10, 2)), rng.normal(size=10)
    members = np.arange(2, 8)
    kx, kt = kick(x, th, members, rng, 0.05, 0.3)
    dx, dth = kx[members] - x[members], kt[members] - th[members]
    assert np.sqrt((dx ** 2).sum(1).mean()) == pytest.approx(0.05, abs=1e-15)
    assert abs(dth.mean()) < 1e-15 and np.sqrt((dth ** 2).mean()) == pytest.approx(0.3, abs=1e-15)
    assert np.array_equal(kx[:2], x[:2]) and np.array_equal(kt[8:], th[8:])


def mini_manifest():
    m = copy.deepcopy(MANIFEST)
    m["integration"]["horizon"] = 60.0
    m["detector"]["window"] = 20.0
    m["detector"]["recovery_time"] = 20.0
    m["interventions"]["mg_window"] = 6.0
    m["statistics"]["bootstrap_resamples"] = 200
    return m


@pytest.fixture(scope="module")
def mini_run():
    m = mini_manifest()
    return m, run_c4.execute(m, m["seeds"]["development_entropy"], 2)


def test_mini_run_covers_every_endpoint_and_passes_gates(mini_run):
    m, body = mini_run
    assert all(body["gates"].values()), body["gates"]
    assert set(body["endpoint_coverage"]["evaluated"]) == set(m["endpoints"]) and not body["endpoint_coverage"]["not_run"]
    for value in body["endpoint_coverage"]["evaluated"].values():
        assert value["verdict"] in ("PASS", "FAIL", "INCONCLUSIVE", "REPORTED", "NOT_TESTED")


def test_mini_run_detects_resonators_rejects_clumps_and_measures_two_way_effects(mini_run):
    _, body = mini_run
    identical = body["records"]["identical"]
    assert sum(w["resonators"] for w in identical["worlds"]) >= 1
    clump = body["evaluations"]["identical"]["not_a_clump"]
    assert clump["accepted_resonators"] == 0 and clump["rejections_by_criterion"]["5_recovery"] == clump["candidates"] > 0
    for world in identical["worlds"]:
        if world["resonators"]:
            assert world["effects"]["m_to_g/intact"] > 0 and world["effects"]["m_to_g/no_mode_to_geometry"] == 0.0
            assert world["effects"]["g_to_m/intact"] > 0 and world["effects"]["g_to_m/no_geometry_to_mode"] == 0.0
            assert world["effects"]["g_to_m/intact"] == world["effects"]["g_to_m_dose/1.5"]
            assert len(world["resonator_effects"]) == world["resonators"]
            unit = world["units"][0]
            assert "members" not in unit and set(unit) == {"effective_position", "characteristic_size", "mode_signature",
                                                           "boundary_ports", "stability"}


def test_detector_receives_no_labels():
    params = list(inspect.signature(detect).parameters)
    assert params == ["xs", "ths", "omega", "params", "dt", "frame_dt", "thresholds", "rngs"]
    source = inspect.getsource(c4_detect)
    for word in ("identical", "heterogeneous", "manifest", "c4_experiment", "import geomind.c4_experiment"):
        assert word not in source


def test_active_unit_boundary_ports_are_the_hull():
    x = np.array([[0.0, 0.0], [2.0, 0.0], [2.0, 2.0], [0.0, 2.0], [1.0, 1.0]])
    stats = {k: 0.0 for k in ("membership_jaccard", "shape_cv", "lock_std", "freq_change", "pattern_change", "recovery_jaccard",
                              "recovery_original_to_control", "recovery_original_to_kicked", "recovery_control_to_kicked",
                              "recovery_pattern_error", "state_error_position", "state_error_size", "state_error_frequency")}
    unit = active_unit(x, np.zeros(5), 0.0, np.arange(5), stats)
    assert len(unit["boundary_ports"]) == 4 and unit["effective_position"] == [1.0, 1.0]
    assert unit["mode_signature"]["coherence"] == pytest.approx(1.0)


def test_statistics_and_verdict_rules():
    assert wilson(8, 10) == pytest.approx([0.4901625, 0.9433178], abs=1e-6)
    assert bootstrap_ci([2.0, 2.0, 2.0], np.random.default_rng(0), 100) == [2.0, 2.0]
    up = {"mean": 1.0, "ci": [0.5, 1.5], "n_worlds": 12}
    assert causality_verdict(up, {"mean": 0.05, "ci": [0.01, 0.09]}, 0.2, 10) == "PASS"
    assert causality_verdict(up, {"mean": 0.0, "ci": [-0.1, 0.1]}, 0.2, 10) == "PASS"
    assert causality_verdict(up, {"mean": 0.5, "ci": [0.4, 0.6]}, 0.2, 10) == "INCONCLUSIVE"
    assert causality_verdict({**up, "n_worlds": 9}, {"mean": 0.0, "ci": [0.0, 0.0]}, 0.2, 10) == "INCONCLUSIVE"
    assert causality_verdict({"mean": 0.1, "ci": [-0.1, 0.3], "n_worlds": 12}, {"mean": 0.0, "ci": [0.0, 0.0]}, 0.2, 10) == "FAIL"
    assert causality_verdict({"mean": None, "ci": None, "n_worlds": 0}, {"mean": None, "ci": None}, 0.2, 10) == "INCONCLUSIVE"
    doses = [{"mean": 0.1}, {"mean": 0.2}, {"mean": 0.4}]
    assert dose_response_verdict(doses, {"ci": [0.1, 0.4], "n_worlds": 12}, 10) == "PASS"
    assert dose_response_verdict(doses[::-1], {"ci": [-0.4, -0.1], "n_worlds": 12}, 10) == "FAIL"
    assert dose_response_verdict([{"mean": 0.1}, {"mean": 0.5}, {"mean": 0.4}], {"ci": [0.1, 0.4], "n_worlds": 12}, 10) == "INCONCLUSIVE"
    assert dose_response_verdict(doses, {"ci": [0.1, 0.4], "n_worlds": 9}, 10) == "INCONCLUSIVE"
    rules = MANIFEST["verdict_rules"]

    def verdicts(formation, gm, mg, dose, state):
        arm = {"formation": {"verdict": formation}, "g_to_m": {"verdict": gm}, "m_to_g": {"verdict": mg},
               "dose_response": {"verdict": dose}, "effective_state": {"verdict": state}}
        out = hypothesis_verdicts(arm, rules)
        return out["H-M"], out["H-C_precursor"]

    S, N, I = "SUPPORTED_WITHIN_SCOPE", "NOT_SUPPORTED", "INCONCLUSIVE"
    # The registered truth table, row by row (manifest verdict_rules.truth_table).
    assert verdicts("PASS", "PASS", "PASS", "PASS", "PASS") == (S, S)
    for failing in range(3):
        endpoints = ["PASS", "PASS", "PASS"]
        endpoints[failing] = "FAIL"
        assert verdicts("PASS", *endpoints, "PASS") == (N, I)
        assert verdicts("FAIL", *endpoints, "PASS") == (N, I)  # an endpoint FAIL wins over formation failure
    endpoints_mixed = ("FAIL", "INCONCLUSIVE", "PASS")
    assert verdicts("PASS", *endpoints_mixed, "PASS")[0] == N
    assert verdicts("FAIL", "PASS", "PASS", "PASS", "PASS") == (I, I)  # formation failure alone is inconclusive
    assert verdicts("FAIL", "INCONCLUSIVE", "INCONCLUSIVE", "INCONCLUSIVE", "INCONCLUSIVE") == (I, I)  # too few worlds
    assert verdicts("PASS", "PASS", "INCONCLUSIVE", "PASS", "PASS") == (I, I)
    assert verdicts("PASS", "INCONCLUSIVE", "PASS", "PASS", "PASS") == (I, I)
    assert verdicts("PASS", "PASS", "PASS", "INCONCLUSIVE", "PASS") == (I, I)  # dose-response is required
    assert verdicts("PASS", "PASS", "PASS", "PASS", "FAIL") == (S, N)
    assert verdicts("FAIL", "INCONCLUSIVE", "INCONCLUSIVE", "INCONCLUSIVE", "FAIL") == (I, N)
    assert verdicts("PASS", "PASS", "PASS", "PASS", "INCONCLUSIVE") == (S, I)
    assert set(rules["truth_table"]) == {"H-M", "H-C_precursor"}


def test_registration_and_seed_separation(tmp_path, monkeypatch):
    manifest = run_c4.load_manifest()
    assert set(manifest["endpoints"]) == set(run_c4.ENDPOINTS)
    seeds = manifest["seeds"]
    assert seeds["final_entropy"] != seeds["development_entropy"]
    seen = []

    def fake_execute(m, entropy, worlds):
        seen.append(entropy)
        return {"gates": {"ok": True}, "hypothesis_status_by_arm": {}, "seconds": 0.0}

    monkeypatch.setattr(run_c4, "execute", fake_execute)
    assert run_c4.smoke(tmp_path / "smoke.json") == 0
    assert seen == [seeds["development_entropy"]]


def test_panel_refuses_to_start_when_the_gate_is_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(run_c4, "panel_gate", lambda: (["earlier stages not verified"], None))
    with pytest.raises(SystemExit, match="gate blocked"):
        run_c4.panel(tmp_path / "out", tmp_path / "contracts.xml")
    assert not (tmp_path / "out").exists()


def test_lock_mask_and_window_statistics_on_a_synthetic_group():
    frames = 31
    x = np.tile(np.array([[0.0, 0.0], [0.5, 0.0], [0.0, 0.5], [0.5, 0.5]]), (frames, 1, 1))
    t = np.arange(frames, dtype=float)[:, None]
    ths = np.hstack([0.2 * t + np.array([0.0, 0.3, -0.2]), 0.3 * t])  # three locked at rate 0.2, one drifting
    locked = locked_pairs(ths, 0.1)
    assert locked[0, 1] and locked[1, 2] and not locked[0, 3] and not locked[2, 3]
    stats = window_statistics(x, ths, np.arange(3), 1.0, 1.5, np.ones((4, 4), bool))
    assert stats["lock_std"] < 1e-6 and stats["freq_change"] < 1e-12 and stats["pattern_change"] < 1e-12
    assert stats["shape_cv"] < 1e-12 and stats["membership_jaccard"] < 1  # the drifter is spatially linked when unmasked
    with_drifter = window_statistics(x, ths, np.arange(4), 1.0, 1.5, np.ones((4, 4), bool))
    assert with_drifter["lock_std"] > 0.5 and with_drifter["membership_jaccard"] == 1.0


def test_each_detector_criterion_rejects_on_its_own():
    t = MANIFEST["detector"]
    good = {"size": 5, "membership_jaccard": 1.0, "shape_cv": 0.0, "lock_std": 0.0, "freq_change": 0.0, "pattern_change": 0.0,
            "recovery_jaccard": 1.0, "recovery_pattern_error": 0.0}
    assert all(criteria_checks(good, t).values())
    breaks = {"1_membership": [("size", 2), ("membership_jaccard", 0.9)], "2_shape": [("shape_cv", 0.06)],
              "3_mode_lock": [("lock_std", 0.11)], "4_signature": [("freq_change", 0.02), ("pattern_change", 0.11)],
              "5_recovery": [("recovery_jaccard", 0.8), ("recovery_pattern_error", 0.11)]}
    for criterion, changes in breaks.items():
        for key, value in changes:
            failed = [k for k, ok in criteria_checks({**good, key: value}, t).items() if not ok]
            assert failed == [criterion], (key, failed)


def test_effect_statistics_on_synthetic_trajectories():
    members = np.array([0, 1, 2])
    reference = np.zeros(3)
    ths = np.zeros((3, 3))
    ths[1, 1], ths[2, 2] = 0.3, 0.6
    # Pairs (0,1), (0,2), (1,2): frame 1 deviations (0.3, 0, -0.3), frame 2 (0, 0.6, 0.6); t0 is excluded.
    assert gm_statistic(ths, members, reference) == pytest.approx((np.sqrt(0.06) + np.sqrt(0.24)) / 2, abs=1e-15)
    base = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    xs = np.stack([base, 2.0 * base, 1.5 * base])
    rg0 = float(np.sqrt(((base - base.mean(0)) ** 2).sum(1).mean()))
    assert mg_statistic(xs, members, rg0) == pytest.approx(2.0, abs=1e-14)


def synthetic_records(effects, units_ok, clump_accepted=0):
    unit = lambda ok: {"stability": {"state_error_position": 0.0 if ok else 1.0, "state_error_size": 0.0, "state_error_frequency": 0.0}}
    worlds = [{"resonators": 1 if e is not None else 0, "effects": e or {}, "units": [unit(ok)] if e is not None else []}
              for e, ok in zip(effects, units_ok)]
    formation = {"worlds_with_resonator": 0, "accepted_resonators": 0, "candidates": 0, "rejections_by_criterion": {}}
    return {"worlds": worlds, "ablation_formation": {"no_mode_to_geometry": formation, "no_distance_weight": formation,
                                                     "clump": {**formation, "accepted_resonators": clump_accepted}}}


def synthetic_effect(scale=1.0, dose_order=(0.005, 0.02, 0.04)):
    gm = dict(zip(("1.25", "1.5", "2.0"), dose_order))
    return {"g_to_m/intact": gm["1.5"] * scale, "g_to_m/no_geometry_to_mode": 0.0, "g_to_m/no_distance_weight": 0.001,
            "g_to_m/frozen_topology": 0.019, "m_to_g/intact": 1.0 * scale, "m_to_g/no_mode_to_geometry": 0.0,
            **{f"g_to_m_dose/{k}": v * scale for k, v in gm.items()},
            "m_to_g_dose/rms:0.5": 0.05 * scale, "m_to_g_dose/rms:1.0": 0.3 * scale, "m_to_g_dose/uniform": 1.0 * scale}


def test_endpoint_evaluation_on_synthetic_records():
    m = copy.deepcopy(MANIFEST)
    m["statistics"]["bootstrap_resamples"] = 200
    rng = np.random.default_rng(0)
    effects = [synthetic_effect(1 + 0.05 * i) for i in range(10)] + [None]
    ok = evaluate_arm(synthetic_records(effects, [True] * 11), m, rng)
    assert ok["formation"]["fraction"] == 10 / 11 and ok["formation"]["verdict"] == "PASS"
    assert ok["g_to_m"]["verdict"] == ok["m_to_g"]["verdict"] == "PASS"
    assert ok["dose_response"]["verdict"] == "PASS"
    assert ok["g_to_m_channels"]["frozen_topology"]["fraction_of_intact"] == pytest.approx(
        0.019 / (0.02 * np.mean([1 + 0.05 * i for i in range(10)])), rel=1e-12)
    assert ok["effective_state"]["fraction_within_bounds"] == 1.0 and ok["effective_state"]["verdict"] == "PASS"
    assert hypothesis_verdicts(ok, m["verdict_rules"]) == {"H-M": "SUPPORTED_WITHIN_SCOPE", "H-C_precursor": "SUPPORTED_WITHIN_SCOPE"}
    reversed_dose = [synthetic_effect(1 + 0.05 * i, dose_order=(0.04, 0.02, 0.005)) for i in range(10)]
    assert evaluate_arm(synthetic_records(reversed_dose, [True] * 10), m, rng)["dose_response"]["verdict"] == "FAIL"
    assert ok["not_a_clump"]["verdict"] == "NOT_TESTED"  # no clump candidates: nothing was tested
    bad = evaluate_arm(synthetic_records(effects[:7] + [None] * 3, [True] * 5 + [False] * 5, clump_accepted=1), m, rng)
    assert bad["formation"]["verdict"] == "FAIL" and bad["not_a_clump"]["verdict"] == "FAIL"
    assert bad["g_to_m"]["verdict"] == "INCONCLUSIVE"  # 7 worlds < 10
    assert bad["effective_state"]["fraction_within_bounds"] == 5 / 7 and bad["effective_state"]["verdict"] == "FAIL"


def test_implementation_gates():
    m = MANIFEST
    clean = {a: {"not_a_clump": {"verdict": "PASS"}} for a in ARMS}
    records = {a: {"worlds": [{}] * 3} for a in ARMS}
    coverage = {"evaluated": dict.fromkeys(m["endpoints"]), "not_run": {}}
    assert all(run_c4.implementation_gates(m, records, clean, {"verdict": "PASS"}, coverage, 3).values())
    vacuous_secondary = {**clean, "heterogeneous": {"not_a_clump": {"verdict": "NOT_TESTED"}}}
    assert run_c4.implementation_gates(m, records, vacuous_secondary, {"verdict": "PASS"}, coverage, 3)["detector_rejects_clumps"]
    vacuous_primary = {**clean, "identical": {"not_a_clump": {"verdict": "NOT_TESTED"}}}
    assert not run_c4.implementation_gates(m, records, vacuous_primary, {"verdict": "PASS"}, coverage, 3)["detector_rejects_clumps"]
    dirty = {**clean, "heterogeneous": {"not_a_clump": {"verdict": "FAIL"}}}
    assert run_c4.implementation_gates(m, records, dirty, {"verdict": "PASS"}, coverage, 3) == {
        "complete_panel": True, "numerical_checks": True, "detector_rejects_clumps": False, "endpoint_coverage": True}
    assert run_c4.implementation_gates(m, records, clean, {"verdict": "FAIL"}, {"evaluated": {}, "not_run": {}}, 4) == {
        "complete_panel": False, "numerical_checks": False, "detector_rejects_clumps": True, "endpoint_coverage": False}


def recovery_case(future_end):
    """A stationary, phase-locked six-member group whose recovery futures (control and kicked) both end at
    future_end; the integration is replaced so only the detector's recovery logic is exercised."""
    x = np.array([[0., 0.], [1., 0.], [2., 0.], [0., 1.], [1., 1.], [2., 1.]])
    xs, ths = np.repeat(x[None, None], 31, axis=0), np.zeros((31, 1, 6))

    def future(bx, bt, bw, params, dt, steps, **kw):
        return np.repeat(future_end[None], len(bx), axis=0), np.zeros_like(bt), None

    with patch("geomind.c4_detect.simulate", future):
        return detect(xs, ths, np.zeros((1, 6)), INTACT, 0.02, 1.0, MANIFEST["detector"], [np.random.default_rng(1)])[0][0]


def test_recovery_rejects_a_group_that_fragments_in_both_futures():
    # Codex review R1 (C4 R002): identical fragmentation in control and kicked futures must not count as recovery.
    split = np.array([[0., 0.], [.5, 0.], [0., .5], [10., 0.], [10.5, 0.], [10., .5]])
    case = recovery_case(split)
    assert not case["accepted"] and case["failed"] == ["5_recovery"]
    assert case["stats"]["recovery_original_to_control"] == 0.5 and case["stats"]["recovery_original_to_kicked"] == 0.5
    assert case["stats"]["recovery_control_to_kicked"] == 1.0 and case["stats"]["recovery_jaccard"] == 0.5


def test_recovery_accepts_a_group_that_stays_whole():
    whole = np.array([[0., 0.], [.5, 0.], [1., 0.], [0., .5], [.5, .5], [1., .5]])
    case = recovery_case(whole)
    assert case["accepted"] and case["stats"]["recovery_jaccard"] == 1.0
