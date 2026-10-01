from dataclasses import replace
import json

import numpy as np
import pytest

from geomind.dataset import generate
from geomind.geometry import Constraint, GeometryState, Observation, Settings, digest
from geomind.references import CompiledCoordinates, DirectEdges, LeastSquares

HASH = digest({"fixture": "c0-contracts-v1"})


def fit(observation, settings=Settings()):
    state = GeometryState(settings)
    trace = state.learn(observation, HASH)
    assert trace["status"] == "PASS", trace
    state.freeze()
    return state, trace


def test_two_node_direction_and_unknown():
    observation = Observation(("a", "b"), (Constraint("a", "b", (3, -2)),))
    state, trace = fit(observation)
    assert state.query("a", "b").displacement == pytest.approx((3, -2), abs=1e-7)
    assert state.query("b", "a").displacement == pytest.approx((-3, 2), abs=1e-7)
    assert state.query("a", "missing").status == "UNKNOWN"
    assert trace["residual_max"] < 1e-7


@pytest.mark.parametrize("inconsistent", [False, True])
def test_triangle_independent_reference_and_residual(inconsistent):
    observation = Observation(("a", "b", "c"), (Constraint("a", "b", (1, 0)), Constraint("b", "c", (0, 1)), Constraint("a", "c", (2 if inconsistent else 1, 1))))
    state, trace = fit(observation)
    reference = LeastSquares(observation)
    assert state.query("a", "c").displacement == pytest.approx(reference.query("a", "c").displacement, abs=1e-7)
    assert trace["energy"] == pytest.approx(reference.energy, abs=1e-10)
    if inconsistent:
        # Hand-derived contradiction: three residuals of magnitude 1/3.
        assert trace["energy"] == pytest.approx(1 / 6, abs=1e-10)
        assert trace["residual_max"] == pytest.approx(1 / 3, abs=1e-7)
    else:
        assert trace["residual_max"] < 1e-7


def test_disconnected_and_singleton_cannot_invent_cross_offset():
    observation = Observation(("a", "b", "x", "y", "alone"), (Constraint("a", "b", (1, 0)), Constraint("x", "y", (0, 2))))
    state, _ = fit(observation)
    for pair in (("a", "x"), ("alone", "b")):
        assert state.query(*pair).status == "UNIDENTIFIABLE"
        assert LeastSquares(observation).query(*pair).status == "UNIDENTIFIABLE"
        assert CompiledCoordinates(observation).query(*pair).status == "UNIDENTIFIABLE"
    assert state.query("alone", "alone").displacement == (0, 0)


def test_id_order_rotation_translation_and_component_rename():
    world = generate(42, "disconnected", 16, 20)
    original, _ = fit(world.observation)
    rotation = np.array([[0.6, -0.8], [0.8, 0.6]])
    names = {node: f"opaque-{i:03d}" for i, node in enumerate(reversed(sorted(world.observation.nodes)))}
    edges = tuple(Constraint(names[e.source], names[e.target], tuple(rotation @ e.offset)) for e in reversed(world.observation.edges))
    transformed, _ = fit(Observation(tuple(names[n] for n in reversed(world.observation.nodes)), edges))
    for a, b in world.queries:
        assert transformed.query(names[a], names[b]).displacement == pytest.approx(rotation @ original.query(a, b).displacement, abs=1e-5)
        translated_truth = {n: np.asarray(p) + (150, -90) for n, p in world.truth.items()}
        assert original.query(a, b).displacement == pytest.approx(translated_truth[b] - translated_truth[a], abs=1e-5)
    for a, b in world.cross_component_queries:
        assert transformed.query(names[a], names[b]).status == "UNIDENTIFIABLE"


@pytest.mark.parametrize("arm", ["lattice", "continuous", "disconnected", "inconsistent", "noisy"])
def test_generator_replay_hidden_edge_identifiability_and_reference(arm):
    world = generate(412, arm)
    assert world == generate(412, arm)
    assert len(world.observation.nodes) == 32
    assert len(world.hidden_edges) == 8
    assert set(world.hidden_edges).isdisjoint(world.observation.edges)
    state, trace = fit(world.observation)
    compiled, ls, direct = CompiledCoordinates(world.observation), LeastSquares(world.observation), DirectEdges(world.observation)
    for a, b in world.queries:
        assert direct.query(a, b).status == "UNKNOWN"
        assert state.query(a, b).displacement == pytest.approx(ls.query(a, b).displacement, abs=1e-5)
        if arm not in ("inconsistent", "noisy"):
            expected = np.asarray(world.truth[b]) - world.truth[a]
            assert state.query(a, b).displacement == pytest.approx(expected, abs=1e-5)
            assert compiled.query(a, b).displacement == pytest.approx(expected, abs=1e-12)
    for edge in world.hidden_edges:
        assert tuple(sorted((edge.source, edge.target))) in world.queries
        assert state.query(edge.source, edge.target).status == "OK"
    assert trace["energy"] == pytest.approx(ls.energy, abs=1e-8)


def test_persistence_query_reset_invariance_and_frozen_memory():
    state, _ = fit(generate(84, "continuous").observation)
    encoded = state.export()
    loaded = GeometryState.load(encoded)
    for node in generate(84, "continuous").observation.nodes:
        assert loaded.query("u0000", node) == state.query("u0000", node)
    assert encoded == state.export() == loaded.export()
    with pytest.raises(RuntimeError):
        loaded.learn(generate(85, "lattice").observation, HASH)


def test_failure_preserves_previous_transaction_and_no_false_convergence():
    state = GeometryState(Settings(max_sweeps=10))
    singleton = Observation(("alone",), ())
    assert state.learn(singleton, HASH)["status"] == "PASS"
    previous = state.export()
    trace = state.learn(Observation(("a", "b"), (Constraint("a", "b", (1e5, 0)),)), HASH)
    assert trace["status"] == "NOT_CONVERGED"
    assert trace["gradient_max"] > 1
    assert state.export() == previous
    invalid = Observation(("a", "b"), (Constraint("a", "b", (float("nan"), 0)),))
    assert state.learn(invalid, HASH)["status"] == "INVALID_STATE"
    assert state.export() == previous


def test_tiny_step_does_not_hide_large_gradient():
    state = GeometryState(Settings(step_factor=1e-15, max_sweeps=20))
    trace = state.learn(Observation(("a", "b"), (Constraint("a", "b", (1, 0)),)), HASH)
    assert trace["update_max"] < 1e-8
    assert trace["gradient_max"] > 0.9
    assert trace["status"] == "NOT_CONVERGED"
    assert state.query("a", "b").status == "NOT_CONVERGED"


@pytest.mark.parametrize("bad", ["checksum", "coordinate", "component", "edge"])
def test_load_rejects_corruption_at_owner(bad):
    state, _ = fit(generate(84, "lattice").observation)
    payload = json.loads(state.export())
    if bad == "checksum":
        payload["checksum"] = "0" * 64
    else:
        payload.pop("checksum")
        if bad == "coordinate":
            payload["coordinates"][0] = [0]
        elif bad == "component":
            payload["components"][1] = 100
        else:
            payload["edges"][0]["source"] = "missing"
        payload["checksum"] = digest(payload)
    with pytest.raises(ValueError):
        GeometryState.load(json.dumps(payload))


def test_direct_baseline_reports_abstention_and_direction():
    direct = DirectEdges(Observation(("a", "b", "c"), (Constraint("a", "b", (1, 0)), Constraint("b", "c", (0, 1)))))
    assert direct.query("b", "a").displacement == (-1, 0)
    assert direct.query("a", "c").status == "UNKNOWN"


def test_protocol_split_seeds_and_settings_are_predeclared():
    from geomind.run_c0 import ROOT
    manifest = json.loads((ROOT / "experiments/c0_manifest.json").read_text())
    seeds = []
    for config in manifest["splits"].values():
        for arm in range(len(manifest["arms"])):
            seeds.extend(config["seed_start"] + arm * manifest["arm_seed_stride"] + i for i in range(config["count"]))
    assert len(seeds) == len(set(seeds))
    assert manifest["settings"] == json.loads(json.dumps(Settings().__dict__))
