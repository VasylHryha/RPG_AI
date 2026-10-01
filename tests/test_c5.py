"""Focused C5 contracts: units, assembly, rigid operations, decoupling, level-2 detector, coarse model,
interventions, statistics, truth tables, runner and registration."""

import inspect
import itertools
import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from geomind import c5_coarse, c5_compose, c5_detect, c5_experiment as E, c5_units, run_c5
from geomind.c4_model import INTACT, Batch, neighbors, simulate, wrap

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "experiments/c5_manifest.json").read_text())
C4 = E.load_c4(MANIFEST)
S = E.settings(MANIFEST, C4)
PARAMS = E.model_params(C4)


def hex_unit(rng):
    """A compact in-phase 7-element cluster, settled with the intact C4 law (a small level-1 stand-in)."""
    a = 0.6 * np.r_[[[0, 0]], [[np.cos(t), np.sin(t)] for t in np.arange(6) * np.pi / 3]]
    x, th, _ = simulate((a + rng.normal(scale=0.01, size=a.shape))[None], np.zeros((1, 7)), np.zeros((1, 7)), INTACT, 0.02, 1500)
    return {"x": x[0] - x[0].mean(0), "th": th[0] * 0.0}


@pytest.fixture(scope="module")
def world():
    rng = np.random.default_rng(3)
    templates = [hex_unit(rng) for _ in range(3)]
    x, th, om, labels = c5_compose.assemble(templates, np.random.default_rng(4), 3, 0.01, 1.6, 0.6)
    x, th, _ = simulate(x[None], th[None], om[None], INTACT, 0.02, 1000)
    return x[0], th[0], om, labels


# ---------------------------------------------------------------- units
def test_unit_phase_is_circular_mean_across_whole_turns():
    th = np.array([[0.1, 0.1 + 2 * np.pi, 0.1 - 4 * np.pi]])
    assert np.allclose(c5_units.unit_phases(th, np.zeros(3, int), [0]), 0.1)


def test_resonator_state_hides_members_and_has_interface_fields(world):
    x, th, om, labels = world
    s = c5_units.resonator_state(x, th, om, labels, 0, 0.0, {}, INTACT)
    for key in ("level", "effective_position", "characteristic_size", "optional_phase", "collective_rate",
                "natural_rate", "mode_signature", "boundary_ports", "stability", "member_digest"):
        assert key in s
    assert "members" not in json.dumps(s)
    assert s["size"] == 7 and len(s["boundary_ports"]) >= 3


def test_rotating_frame_symmetry_shared_rate():
    """A unit whose members share rate w is the w = 0 unit in a frame rotating at w (C4 acceptance transfers)."""
    rng = np.random.default_rng(5)
    u = hex_unit(rng)
    th0 = rng.normal(scale=0.2, size=7)
    a = simulate(u["x"][None], th0[None], np.zeros((1, 7)), INTACT, 0.02, 500)
    b = simulate(u["x"][None], th0[None], np.full((1, 7), 0.37), INTACT, 0.02, 500)
    assert np.abs(a[0] - b[0]).max() < 1e-9
    assert np.abs(wrap(b[1] - a[1] - 0.37 * 10.0)).max() < 1e-9


def test_port_overlap_detects_interpenetration():
    sq = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0.5, 0.5]], float)
    labels = np.r_[np.zeros(5, int), np.ones(5, int)]
    apart = np.vstack([sq, sq + [3, 0]])
    inside = np.vstack([sq, sq * 0.4 + [0.3, 0.3]])
    assert c5_units.port_overlap(apart, labels, [0, 1]) == [0.0, 0.0]
    assert c5_units.port_overlap(inside, labels, [0, 1])[1] == 1.0


# ---------------------------------------------------------------- assembly, rigid operations, decoupling
def test_assembly_rates_shared_per_unit_and_gap(world):
    x, th, om, labels = world
    for u in range(3):
        assert np.ptp(om[labels == u]) == 0.0
    t = [{"x": np.zeros((3, 2)) + [[0, 0], [0.5, 0], [0, 0.5]], "th": np.zeros(3)}] * 4
    x2, _, _, lab = c5_compose.assemble(t, np.random.default_rng(1), 4, 0.03, 3.0, 0.6)
    d = np.linalg.norm(x2[:, None] - x2[None], axis=-1)
    assert d[lab[:, None] != lab[None]].min() >= 0.6


def test_rigid_operations_keep_internal_state_bit_identical(world):
    x, th, om, labels = world
    units = [0, 2]
    moved = c5_compose.scale_units(x, labels, units, 1.37)
    shifted = c5_compose.shift_units(x, labels, [1], [np.array([0.3, -0.2])])
    rotated = c5_compose.rotate_units(th, labels, units, [0.4, -0.4])
    for u in range(3):
        m = labels == u
        for y in (moved, shifted):
            assert np.array_equal(y[m] - y[m][0], x[m] - x[m][0]) or np.allclose(y[m] - y[m][0], x[m] - x[m][0], atol=1e-15)
        assert np.allclose(np.diff(rotated[m]), np.diff(th[m]), atol=1e-15)
    assert np.allclose(shifted[labels == 1] - x[labels == 1], [0.3, -0.2])
    c = [x[labels == u].mean(0) for u in units]
    cm = [moved[labels == u].mean(0) for u in units]
    g = np.mean(c, 0)
    assert np.allclose(cm[0] - g, 1.37 * (c[0] - g)) and np.allclose(moved[labels == 1], x[labels == 1])
    assert np.allclose(rotated[labels == 0] - th[labels == 0], 0.4) and np.array_equal(rotated[labels == 1], th[labels == 1])


def test_decoupling_removes_every_cross_link_and_equals_alone(world):
    x, th, om, labels = world
    off = c5_compose.decouple_offsets(labels, [0, 1, 2])
    idx, mask, _ = neighbors((x + off)[None], Batch(INTACT, 1))
    assert not ((mask[0] > 0) & (labels[idx[0]] != labels[:, None])).any()
    idx0, mask0, _ = neighbors(x[None], Batch(INTACT, 1))
    assert ((mask0[0] > 0) & (labels[idx0[0]] != labels[:, None])).any(), "fixture must be in contact"
    dec = simulate((x + off)[None], th[None], om[None], INTACT, 0.02, 200)
    for u in range(3):
        m = labels == u
        alone = simulate(x[m][None], th[m][None], om[m][None], INTACT, 0.02, 200)
        assert np.abs(dec[0][0, m] - off[m] - alone[0][0]).max() < 1e-9
        assert np.abs(dec[1][0, m] - alone[1][0]).max() < 1e-9


def test_padding_is_inert(world):
    x, th, om, labels = world
    bx, bt, bw, bl = c5_compose.pad([(x, th, om, labels)], n=len(x) + 6)
    a = simulate(x[None], th[None], om[None], INTACT, 0.02, 100)
    b = simulate(bx, bt, bw, INTACT, 0.02, 100)
    assert np.abs(a[0][0] - b[0][0, :len(x)]).max() < 1e-12
    assert np.array_equal(b[0][0, len(x):], bx[0, len(x):])


# ---------------------------------------------------------------- level-2 detector
T2 = S["t2"]


def test_level2_thresholds_scale_only_times():
    t1 = C4["detector"]
    t2 = c5_detect.level2_thresholds(t1, 3.2)
    for k, v in t1.items():
        if k in ("window", "frame_dt", "recovery_time"):
            assert t2[k] == v * 3.2
        elif k == "freq_tol":
            assert t2[k] == v / 3.2
        else:
            assert t2[k] == v
    assert E.same_rule_audit(MANIFEST)["verdict"] == "PASS"


def series(rates, F=31, dt=1.0, spacing=1.0):
    X = np.zeros((F, len(rates), 2))
    X[:, :, 0] = np.arange(len(rates)) * spacing
    Th = np.arange(F)[:, None] * dt * np.asarray(rates)[None]
    return X, Th


def test_detector_finds_locked_group_and_rejects_drift():
    X, Th = series([0.01, 0.01, 0.01])
    found, _ = c5_detect.candidates(X, Th, 1.0, T2)
    assert len(found) == 1 and list(found[0][0]) == [0, 1, 2]
    assert c5_detect.criteria_checks({**found[0][1], "parts_alive": True, "recovery_jaccard": 1.0,
                                      "recovery_pattern_error": 0.0}, T2)["3_mode_lock"]
    X, Th = series([0.0, 0.05, -0.05])
    assert c5_detect.candidates(X, Th, 1.0, T2)[0] == []
    (units, stats), = c5_detect.imposed(X, Th, [[0, 1, 2]], 1.0, T2)[0]
    checks = c5_detect.criteria_checks({**stats, "parts_alive": True, "recovery_jaccard": 1.0, "recovery_pattern_error": 0.0}, T2)
    assert not checks["3_mode_lock"]


def test_recovery_rule_keeps_the_original_group():
    X = np.array([[0, 0], [1, 0], [2, 0], [9, 0]], float)
    Th = np.zeros(4)
    locked = np.ones((4, 4), bool)
    units = np.array([0, 1, 2])
    ok = c5_detect.recovery(units, X, Th, X, Th, locked, T2)
    assert ok["recovery_jaccard"] == 1.0 and ok["recovery_pattern_error"] == 0.0
    split = np.array([[0, 0], [1, 0], [7, 0], [9, 0]], float)  # the same fragmentation in both futures
    bad = c5_detect.recovery(units, split, Th, split, Th, locked, T2)
    assert bad["recovery_control_to_kicked"] == 1.0 and bad["recovery_jaccard"] < T2["recovery_jaccard"]
    stats = {"size": 3, "membership_jaccard": 1.0, "shape_cv": 0.0, "lock_std": 0.0, "freq_change": 0.0,
             "pattern_change": 0.0, "parts_alive": True, **bad}
    assert "5_recovery" in [k for k, v in c5_detect.criteria_checks(stats, T2).items() if not v]
    static = c5_detect.recovery(units, X, Th, X, Th + np.array([0.3, -0.3, 0.0, 0.0]), locked, T2)
    assert static["recovery_pattern_error"] > T2["pattern_tol"]


def test_criterion6_rejects_merger_and_broken_units():
    good = {"shape_cv": 0.0, "lock_std": 0.0, "freq_change": 0.0, "pattern_change": 0.0, "port_overlap": 0.0}
    t1 = C4["detector"]
    assert c5_detect.parts_alive([good] * 3, [0, 1, 2], t1, 0.2)[0]
    assert not c5_detect.parts_alive([good, {**good, "port_overlap": 0.4}, good], [0, 1, 2], t1, 0.2)[0]
    assert not c5_detect.parts_alive([good, {**good, "lock_std": 0.2}, good], [0, 1, 2], t1, 0.2)[0]
    stats = {"size": 3, "membership_jaccard": 1.0, "shape_cv": 0.0, "lock_std": 0.0, "freq_change": 0.0,
             "pattern_change": 0.0, "recovery_jaccard": 1.0, "recovery_pattern_error": 0.0, "parts_alive": False}
    assert not c5_detect.criteria_checks(stats, T2)["6_parts_alive"]
    assert c5_detect.criteria_checks({**stats, "parts_alive": True}, T2)["6_parts_alive"]


def test_detector_never_receives_members_rates_or_labels():
    for name in ("candidates", "imposed", "unit_kick", "recovery", "criteria_checks", "level2_thresholds"):
        params = set(inspect.signature(getattr(c5_detect, name)).parameters)
        assert not params & {"labels", "omega", "members", "x", "th"}
    code = inspect.getsource(c5_detect).split('"""', 2)[2]
    assert "simulate" not in code and "c5_units" not in code and "c5_compose" not in code and "omega" not in code


def test_outcome_order():
    acc = {"accepted": True, "failed": []}
    merged = {"accepted": False, "failed": ["6_parts_alive"]}
    drift = {"accepted": False, "failed": ["3_mode_lock"]}
    assert c5_detect.outcome([merged, acc], True) == "FORMED"
    assert c5_detect.outcome([drift, merged], True) == "MERGED"
    assert c5_detect.outcome([drift], True) == "DRIFTING"
    assert c5_detect.outcome([], True) == "DRIFTING"
    assert c5_detect.outcome([], False) == "APART"


# ---------------------------------------------------------------- coarse model
def state(X, theta, rate, ports, own, size=7):
    return {"effective_position": X, "optional_phase": theta, "natural_rate": rate, "size": size,
            "boundary_ports": [{"offset": p, "phase_offset": 0.0, "own_neighbour_distances": own} for p in ports]}


RING = [[0.6 * np.cos(t), 0.6 * np.sin(t)] for t in np.arange(6) * np.pi / 3]


def test_coarse_isolated_units_follow_natural_rates():
    states = [state([0, 0], 0.0, 0.02, RING, [0.6] * 3), state([50, 0], 1.0, -0.01, RING, [0.6] * 3)]
    r = c5_coarse.run(states, INTACT, 0.02, 100, 10)
    X, th = r["X"], r["theta"]
    assert np.allclose(X, X[0]) and r["reopens"] == 0 and r["flagged"] == 0
    assert np.allclose(th[-1] - th[0], [0.02 * 2.0, -0.01 * 2.0])


def test_coarse_couples_through_ports_and_locks_phases():
    states = [state([0, 0], 0.0, 0.0, RING, [0.6] * 3), state([1.5, 0], 0.5, 0.0, RING, [0.6] * 3)]
    cs = c5_coarse.CoarseState(states, INTACT.k)
    sel, _, _ = c5_coarse.links(cs, cs.X, INTACT)
    assert sel.any()
    th = c5_coarse.run(states, INTACT, 0.02, 2000, 100)["theta"]
    assert abs(wrap(th[-1, 1] - th[-1, 0])) < 0.5 * 0.5


def test_coarse_reopens_when_invalid():
    states = [state([0, 0], 0.0, 0.0, RING, [0.6] * 3), state([1.5, 0], 0.0, 3.0, RING, [0.6] * 3)]
    calls = []

    def reopen(frame):
        calls.append(frame)
        return states

    r = c5_coarse.run(states, INTACT, 0.02, 200, 10, reopen)
    assert r["reopens"] >= 1 and calls
    open_loop = c5_coarse.run(states, INTACT, 0.02, 200, 10)
    assert open_loop["reopens"] == 0 and open_loop["flagged"] >= 1, "open loop flags but never injects full states"


def test_coarse_reads_only_resonator_states():
    params = set(inspect.signature(c5_coarse.CoarseState.__init__).parameters)
    assert params == {"self", "states", "k"}
    source = inspect.getsource(c5_coarse)
    assert "labels" not in source and "members" not in source.split('"""', 2)[2]


# ---------------------------------------------------------------- interventions on a fixture group
@pytest.fixture(scope="module")
def runs(world):
    x, th, om, labels = world
    row = {"x0": x, "th0": th, "omega": om, "labels": labels}
    return E.group_runs(row, [0, 1, 2], S, PARAMS, MANIFEST, np.random.default_rng(11))


def test_complete_ablations_remove_their_pathway(runs):
    assert abs(runs["effects"]["g_to_m/no_geometry_to_mode"]) < 1e-12
    assert abs(runs["effects"]["m_to_g/no_mode_to_geometry"]) < 1e-12
    for key in ("g_to_m/intact", "m_to_g/intact", "g_to_m/no_distance_weight", "g_to_m/frozen_topology"):
        assert np.isfinite(runs["effects"][key])


def test_group_runs_report_every_registered_quantity(runs):
    iv = MANIFEST["interventions"]
    for s in iv["gm_scales"]:
        assert f"g_to_m_dose/{s}/intact" in runs["effects"]
    for d in iv["mg_doses"]:
        assert f"m_to_g_dose/{d}/intact" in runs["effects"]
    assert runs["effects"]["g_to_m/intact"] == runs["effects"][f"g_to_m_dose/{iv['gm_scale']}/intact"]
    assert abs(runs["transfer_decoupled"]) < 1e-9, "decoupled units cannot transfer a pulse"
    assert len(runs["downward_units"]) == 3 and all("boundary_shift" in u for u in runs["downward_units"])
    c = runs["coarse"]
    assert set(c["excitations"]) == {"pulse", "push"}
    for b in ("no_transfer", "rigid_transfer", "relaxation"):
        assert f"gain_vs_{b}" in c
    assert runs["tau2"] > 0 and isinstance(runs["tau2_censored"], bool)
    assert runs["downward_effect"] > 1e-6, "units in contact feel their neighbours at the boundary"


# ---------------------------------------------------------------- statistics and verdict rules
def summ(lo, hi, n=12):
    return {"ci": [lo, hi], "n_worlds": n, "mean": (lo + hi) / 2}


def test_margin_verdict_rows():
    m = 0.01
    assert E.margin_verdict(summ(0.02, 0.03, 9), m, 10) == "INCONCLUSIVE"
    assert E.margin_verdict(summ(0.001, 0.005), m, 10) == "FAIL"
    assert E.margin_verdict(summ(0.011, 0.03), m, 10) == "PASS"
    assert E.margin_verdict(summ(0.005, 0.03), m, 10) == "INCONCLUSIVE"
    assert E.margin_verdict(summ(1e-12, 2e-12), m, 10) == "FAIL", "numerical noise must not pass"


def test_coarse_verdict_rows():
    good = summ(0.1, 0.2)
    assert E.coarse_verdict([summ(0.1, 0.2, 5)] * 3, 10) == "INCONCLUSIVE"
    for k in range(3):
        bad = [good] * 3
        bad[k] = summ(-0.3, -0.1)
        assert E.coarse_verdict(bad, 10) == "FAIL", k
        weak = [good] * 3
        weak[k] = summ(-0.05, 0.1)
        assert E.coarse_verdict(weak, 10) == "INCONCLUSIVE", k
    assert E.coarse_verdict([good, summ(0.05, 0.1), summ(0.01, 0.02)], 10) == "PASS"


def test_separation_verdict_rows():
    assert E.separation_verdict(summ(2.0, 3.0, 9), 10) == "INCONCLUSIVE"
    assert E.separation_verdict(summ(0.5, 0.9), 10) == "FAIL"
    assert E.separation_verdict(summ(1.2, 3.0), 10) == "PASS"
    assert E.separation_verdict(summ(0.9, 3.0), 10) == "INCONCLUSIVE"


def test_relaxation_baseline_and_response_error():
    t = np.array([0.0, 1.0, 1e6])
    p = E.relaxation_prediction(t, 4, 0.5, 2.0)
    assert p.shape == (3, 1) and p[0, 0] == 0.0 and abs(p[-1, 0] - 0.125) < 1e-12
    assert abs(p[1, 0] - 0.125 * (1 - np.exp(-0.5))) < 1e-12
    v = E.relaxation_prediction(t, 2, np.array([0.2, 0.0]), 1.0)
    assert v.shape == (3, 2) and abs(v[-1, 0] - 0.1) < 1e-12
    fT = np.zeros((3, 3))
    fX = np.zeros((3, 3, 2))
    pT = fT.copy()
    pT[:, 1] = 0.3
    pX = fX.copy()
    pX[:, 2, 0] = 0.4
    L = np.array([1.0, 1.0, 2.0])
    assert abs(E.response_error(fT, fX, pT, pX, [1, 2], L) - (np.sqrt(0.09 / 2) + np.sqrt(0.04 / 2))) < 1e-12
    assert E.response_error(fT, fX, pT, pX, [0], L) == 0.0, "the excited unit is not scored"


def test_mg_doses_are_one_fixed_size_family_increasing_in_effective_size():
    doses = MANIFEST["interventions"]["mg_doses"]
    assert all(d.startswith("rms:") for d in doses)
    sizes = [E.mg_dose_rms(d) for d in doses]
    assert sizes == [0.5, 1.0, 1.5] and MANIFEST["interventions"]["mg_dose"] == "rms:1.0"
    for bad in ("uniform", "uniform:1.0"):
        with pytest.raises(ValueError):
            E.mg_dose_rms(bad)
    rng = np.random.default_rng(0)
    i, j = np.triu_indices(3, 1)
    effective = []
    for a in sizes:
        k = c5_compose.unit_kick(rng, 3, a)
        assert abs(k.mean()) < 1e-12 and abs(np.sqrt((k ** 2).mean()) - a) < 1e-12
        effective.append(np.sqrt((wrap(k[j] - k[i]) ** 2).mean()))
    assert effective == sorted(effective)


def test_control_verdict_never_passes_empty():
    assert E.control_verdict([[]])["verdict"] == "NOT_TESTED"
    assert E.control_verdict([[{"accepted": False, "failed": ["3_mode_lock"]}]])["verdict"] == "PASS"
    assert E.control_verdict([[{"accepted": True, "failed": []}]])["verdict"] == "FAIL"


def reference_truth_table(formation, upper, causal, composition):
    """Independent transcription of the manifest truth table rows."""
    if "FAIL" in causal:
        hm = "NOT_SUPPORTED"
    elif formation == "PASS" and all(v == "PASS" for v in causal):
        hm = "SUPPORTED_WITHIN_SCOPE"
    else:
        hm = "INCONCLUSIVE"
    if upper < 0.25:
        hc = "NOT_SUPPORTED"
    elif "FAIL" in composition:
        hc = "NOT_SUPPORTED"
    elif hm == "SUPPORTED_WITHIN_SCOPE" and len(composition) == 5 and all(v == "PASS" for v in composition):
        hc = "SUPPORTED_WITHIN_SCOPE"
    else:
        hc = "INCONCLUSIVE"
    return {"H-M_level2": hm, "H-C_first_transition": hc}


def test_truth_tables_every_combination():
    values = ("PASS", "FAIL", "INCONCLUSIVE")
    rows = MANIFEST["verdict_rules"]["truth_table"]
    assert len(rows["H-M_level2"]) == 3 and len(rows["H-C_first_transition"]) == 4
    count = 0
    for formation, upper in itertools.product(("PASS", "FAIL"), (0.1, 0.6)):
        for causal in itertools.product(values, repeat=3):
            for comp in itertools.product(values, repeat=5):
                e = {"formation_l2": {"verdict": formation, "wilson_95": [0.0, upper]},
                     "g_to_m_l2": {"verdict": causal[0]}, "m_to_g_l2": {"verdict": causal[1]},
                     "dose_response_l2": {"verdict": causal[2]}, "downward_effect": {"verdict": comp[0]},
                     "emergent_transfer": {"verdict": comp[1]}, "effective_state_l2": {"verdict": comp[2]},
                     "coarse_vs_full": {"verdict": comp[3]}, "timescale_separation": {"verdict": comp[4]}}
                assert E.hypothesis_verdicts(e) == reference_truth_table(formation, upper, causal, comp)
                count += 1
    assert count == 2 * 2 * 27 * 243


def fake_world(formed, groups=(), outcome="FORMED"):
    cand = [{"units": [0, 1, 2], "accepted": formed, "failed": [] if formed else ["3_mode_lock"],
             "stats": {"state_error_position": 0.0, "state_error_size": 0.0, "state_error_frequency": 0.0}}]
    return {"seed_index": 0, "candidates": cand, "groups": list(groups), "outcome": outcome,
            "spread_sweep": {"1.0": {"formed": formed}}, "controls": {"decoupled_spread": [], "decoupled_static": []},
            "unit_validity": [{}] * 3, "level1_redetected": [True] * 3, "tau1": [1.5] * 3,
            "c4_single_component": [True] * len(groups)}


def group(value):
    effects = {f"g_to_m_dose/{s}/intact": value * (k + 1) for k, s in enumerate(MANIFEST["interventions"]["gm_scales"])}
    effects.update({f"m_to_g_dose/{d}/intact": value * (k + 1) for k, d in enumerate(MANIFEST["interventions"]["mg_doses"])})
    effects.update({"g_to_m/intact": value, "m_to_g/intact": value, "g_to_m/no_geometry_to_mode": 0.0,
                    "m_to_g/no_mode_to_geometry": 0.0, "g_to_m/no_distance_weight": 0.0, "g_to_m/frozen_topology": 0.0})
    exc = {"error_coarse": 0.0, "error_coarse_reopened": 0.0, "error_no_transfer": 0.1, "error_rigid_transfer": 0.1,
           "error_relaxation": 0.1, "frequency_error": 0.0, "recovery_error": 0.0, "reopens": 0, "flagged_samples": 0}
    return {"units": [0, 1, 2], "effects": effects, "downward_effect": 0.05, "entrainment": 0.01, "emergent_transfer": 0.1,
            "tau2": 4.0 + value, "tau2_censored": False,
            "coarse": {"gain_vs_no_transfer": 0.1, "gain_vs_rigid_transfer": 0.1, "gain_vs_relaxation": 0.1,
                       "excitations": {"pulse": exc, "push": exc},
                       "work_full_pair_evaluations": 1, "work_coarse_pair_evaluations": 1}}


def evaluate(worlds):
    pool = {"c4_worlds": 1}
    return E.evaluate(worlds, pool, MANIFEST, S, np.random.default_rng(0))


def test_formation_and_min_worlds_rules():
    rng = np.random.default_rng(1)
    worlds = [fake_world(True, [group(0.01 + 0.001 * rng.random())]) for _ in range(9)] + [fake_world(False, outcome="DRIFTING")]
    e = evaluate(worlds)
    assert e["formation_l2"]["verdict"] == "FAIL", "fewer than 10 formed worlds cannot pass"
    for name in ("g_to_m_l2", "m_to_g_l2", "dose_response_l2", "downward_effect", "emergent_transfer",
                 "effective_state_l2", "coarse_vs_full", "timescale_separation"):
        assert e[name]["verdict"] == "INCONCLUSIVE", name
    worlds = [fake_world(True, [group(0.01 + 0.001 * rng.random())]) for _ in range(12)]
    e = evaluate(worlds)
    for name in ("formation_l2", "g_to_m_l2", "m_to_g_l2", "dose_response_l2", "downward_effect",
                 "emergent_transfer", "effective_state_l2", "coarse_vs_full", "timescale_separation"):
        assert e[name]["verdict"] == "PASS", name
    assert E.hypothesis_verdicts(e) == {"H-M_level2": "SUPPORTED_WITHIN_SCOPE", "H-C_first_transition": "SUPPORTED_WITHIN_SCOPE"}
    worlds = [fake_world(True, [group(0.01)]) for _ in range(12)] + [fake_world(False, outcome="DRIFTING")] * 13
    assert evaluate(worlds)["formation_l2"]["verdict"] == "FAIL", "below 0.5 fails"


def test_effective_state_bound_uses_scaled_frequency():
    w = fake_world(True, [group(0.01)])
    w["candidates"][0]["stats"]["state_error_frequency"] = 0.005  # within 0.01, outside 0.01 / T
    e = evaluate([w] * 12)
    assert e["effective_state_l2"]["verdict"] == "FAIL"


# ---------------------------------------------------------------- runner and registration
def test_manifest_registered_with_every_endpoint():
    assert MANIFEST["status"] == "REGISTERED" and MANIFEST["seeds"]["final_entropy"]
    assert set(MANIFEST["endpoints"]) == set(run_c5.ENDPOINTS)
    assert MANIFEST["seeds"]["final_entropy"] != MANIFEST["seeds"]["development_entropy"]
    assert run_c5.load_manifest()["experiment_id"] == MANIFEST["experiment_id"]


def test_endpoint_coverage_lists_every_endpoint():
    e = {name: {"verdict": "REPORTED"} for name in run_c5.ENDPOINTS}
    cov = run_c5.endpoint_coverage(e)
    assert set(cov["evaluated"]) == set(MANIFEST["endpoints"]) and not cov["not_run"]


def test_smoke_uses_development_entropy(tmp_path):
    seen = {}

    def fake(manifest, entropy, worlds, jobs=4):
        seen["entropy"] = entropy
        return {"gates": {"g": True}, "hypothesis_status": {}, "seconds": 0.0}

    with patch.object(run_c5, "execute", fake):
        run_c5.smoke(tmp_path / "s.json")
    assert seen["entropy"] == MANIFEST["seeds"]["development_entropy"]


def test_runner_calls_the_gate_itself():
    assert 'milestones.check("c5", "panel")' in inspect.getsource(run_c5)
    assert "panel_gate()" in inspect.getsource(run_c5.panel)


def test_gates_require_non_vacuous_controls():
    e = {"numerical_checks": {"verdict": "PASS"}, "not_independent": {"verdict": "NOT_TESTED"},
         "not_a_clump_l2": {"verdict": "PASS"}, "level1_pool": {"verdict": "PASS"}, "same_rule_audit": {"verdict": "PASS"}}
    cov = {"evaluated": {k: {} for k in MANIFEST["endpoints"]}, "not_run": {}}
    gates = run_c5.implementation_gates(MANIFEST, [0] * 3, e, cov, 3)
    assert not gates["controls_non_vacuous_reject"]


def test_frozen_c4_manifest_hash_is_checked():
    bad = json.loads(json.dumps(MANIFEST))
    bad["level1"]["c4_manifest_sha256"] = "0" * 64
    with pytest.raises(ValueError):
        E.load_c4(bad)


def test_separation_uses_group_units_tau1():
    w = fake_world(True, [group(0.0)])
    w["tau1"] = [1.0, 2.0, 3.0, 100.0]
    w["groups"][0]["units"] = [0, 1, 2]
    e = evaluate([w] * 12)
    assert abs(e["timescale_separation"]["ratio"]["mean"] - 4.0 / 2.0) < 1e-12


def test_coarse_must_beat_the_relaxation_baseline():
    worlds = []
    for _ in range(12):
        g = group(0.01)
        g["coarse"]["gain_vs_relaxation"] = -0.05
        worlds.append(fake_world(True, [g]))
    assert evaluate(worlds)["coarse_vs_full"]["verdict"] == "FAIL"
