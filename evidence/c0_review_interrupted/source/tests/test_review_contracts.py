"""Regression probes for review findings, including evaluator negative controls."""

from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from geomind.dataset import generate
from geomind.geometry import Answer, Constraint, GeometryState, Observation, Settings, digest
from geomind.run_c0 import ROOT, aggregate, evaluate_world, qualification_gates, validate_manifest

HASH = digest({"fixture": "review-c0-v2"})


def manifest():
    return json.loads((ROOT / "experiments/c0_manifest.json").read_text())


def fitted():
    state = GeometryState()
    assert state.learn(Observation(("a", "b"), (Constraint("a", "b", (1, 0)),)), HASH)["status"] == "PASS"
    state.freeze()
    return state


@pytest.mark.parametrize("change", ["wrong_finite", "string_coordinate", "boolean_coordinate", "settings_float", "bad_hash", "extra_field", "missing_field", "wrong_anchor", "old_schema"])
def test_checksum_is_not_semantic_validation(change):
    payload = json.loads(fitted().export())
    payload.pop("checksum")
    if change == "wrong_finite":
        payload["coordinates"][1][0] = 12.0
    elif change == "string_coordinate":
        payload["coordinates"][1][0] = "1"
    elif change == "boolean_coordinate":
        payload["coordinates"][1][0] = True
    elif change == "settings_float":
        payload["settings"]["max_sweeps"] = 10000.0
    elif change == "bad_hash":
        payload["training_manifest_hash"] = "z" * 64
    elif change == "extra_field":
        payload["hidden_truth"] = {"a": [1, 2]}
    elif change == "missing_field":
        del payload["coordinates"]
    elif change == "wrong_anchor":
        payload["anchors"] = [1]
    else:
        payload["schema"] = "geomind.c0.geometry.v1"
    payload["checksum"] = digest(payload)
    with pytest.raises(ValueError):
        GeometryState.load(json.dumps(payload))


@pytest.mark.parametrize("encoded", ["null", "[]", "{", '{"checksum":"x"}', '{"x":1,"x":2}'])
def test_load_errors_have_one_public_type(encoded):
    with pytest.raises(ValueError):
        GeometryState.load(encoded)


@pytest.mark.parametrize("setting,value", [("max_sweeps", True), ("max_sweeps", 10.5), ("stable_sweeps", float("inf")), ("step_factor", "0.25"), ("gradient_tolerance", True), ("update_tolerance", float("nan"))])
def test_invalid_settings_rejected_before_mutation(setting, value):
    with pytest.raises(ValueError):
        GeometryState(replace(Settings(), **{setting: value}))


def test_mutable_input_and_overflow_rejected_transactionally():
    state = GeometryState()
    assert state.learn(Observation(("a",), ()), HASH)["status"] == "PASS"
    old = state.export()
    for observation in (Observation(["a"], ()), Observation(("a", "b"), (Constraint("a", "b", [1, 0]),)), Observation(("a", "b"), (Constraint("a", "b", (1e308, 0), 1e308),))):
        trace = state.learn(observation, HASH)
        assert trace["status"] == "INVALID_STATE"
        json.dumps(trace, allow_nan=False)
        assert state.export() == old
    assert state.query([], "a").status == "INVALID_STATE"


def test_readonly_settings_and_isolated_many_components_cost():
    state = GeometryState()
    with pytest.raises(AttributeError):
        state.settings = Settings(max_sweeps=1)
    observation = Observation(tuple(f"u{i:04d}" for i in range(128)), ())
    trace = state.learn(observation, HASH)
    assert trace["status"] == "PASS"
    assert trace["preprocessing_work"]["anchor_node_visits"] == 128
    assert state.query("u0000", "u0127").status == "UNIDENTIFIABLE"


def test_weak_weights_cannot_fake_equilibrium_with_wrong_coordinates():
    observation = Observation(("a", "b"), (Constraint("a", "b", (1, 0), 1e-20),))
    state = GeometryState(Settings(max_sweeps=20))
    trace = state.learn(observation, HASH)
    assert trace["status"] == "NOT_CONVERGED"
    assert trace["normalized_gradient_max"] > 0.99
    assert state.query("a", "b").status == "NOT_CONVERGED"
    payload = json.loads(fitted().export())
    payload.pop("checksum")
    payload["edges"][0]["weight"] = 1e-20
    payload["coordinates"][1] = [12, 0]
    payload["checksum"] = digest(payload)
    with pytest.raises(ValueError, match="normalized force"):
        GeometryState.load(json.dumps(payload))


def test_weighted_inconsistent_case_against_hand_solution():
    # x minimizes .5*(x-1)^2 + .5*3*(x-2)^2 -> x=7/4; E=3/8.
    observation = Observation(("a", "b"), (Constraint("a", "b", (1, 0), 1), Constraint("a", "b", (2, 0), 3)))
    state = GeometryState()
    trace = state.learn(observation, HASH)
    assert trace["status"] == "PASS"
    assert state.query("a", "b").displacement == pytest.approx((1.75, 0), abs=1e-7)
    assert trace["energy"] == pytest.approx(0.375, abs=1e-10)


def test_public_relation_mapping_and_consistent_id_permutation():
    world = generate(616, "lattice")
    catalog = dict(world.observation.relations)
    assert set(catalog.values()) == {e.offset for e in world.observation.edges}
    assert all(catalog[e.relation_id] == e.offset for e in world.observation.edges)
    names = {name: f"label-{i}" for i, name in enumerate(reversed(list(catalog)))}
    observation = replace(world.observation, relations=tuple((names[n], v) for n, v in world.observation.relations), edges=tuple(replace(e, relation_id=names[e.relation_id]) for e in world.observation.edges))
    left, right = GeometryState(), GeometryState()
    assert left.learn(world.observation, HASH)["status"] == right.learn(observation, HASH)["status"] == "PASS"
    assert [left.query(*p) for p in world.queries] == [right.query(*p) for p in world.queries]
    bad = replace(observation, edges=(replace(observation.edges[0], relation_id="missing"),) + observation.edges[1:])
    assert GeometryState().learn(bad, HASH)["status"] == "INVALID_STATE"


@pytest.mark.parametrize("change", ["zero_count", "missing_arm", "overlap", "loose_tolerance", "bad_queries", "unknown_algorithm", "bad_uncertainty"])
def test_invalid_protocol_cannot_vacuously_qualify(change):
    m = manifest()
    if change == "zero_count":
        m["splits"]["test"]["count"] = 0
    elif change == "missing_arm":
        m["arms"].pop()
    elif change == "overlap":
        m["splits"]["test"]["seed_start"] = m["splits"]["train"]["seed_start"]
    elif change == "loose_tolerance":
        m["displacement_tolerance"] = 1
    elif change == "bad_queries":
        m["queries_per_world"] = 0
    elif change == "unknown_algorithm":
        m["algorithm"] = "other"
    else:
        m["uncertainty"]["replicates"] = 0
    with pytest.raises(ValueError):
        validate_manifest(m)
    assert not all(qualification_gates([], manifest(), ["test"]).values())


def test_new_worlds_disjoint_from_original_final_worlds():
    new = manifest()
    old = json.loads((ROOT / "experiments/c0_r4_001_manifest.json").read_text())
    def seeds(m):
        return {c["seed_start"] + a * m["arm_seed_stride"] + i for c in m["splits"].values() for a in range(len(m["arms"])) for i in range(c["count"])}
    assert seeds(new).isdisjoint(seeds(old))


def test_noisy_evaluator_has_separate_metrics_and_work():
    m = manifest()
    result = evaluate_world(generate(617, "noisy"), Settings(), HASH, m["displacement_tolerance"])
    assert result["candidate"]["status"] == "PASS"
    assert result["methods"]["candidate"]["indirect"]["total_least_squares_accuracy"] == 1
    assert result["methods"]["candidate"]["indirect"]["total_truth_accuracy"] < 1
    assert result["methods"]["direct_edge"]["indirect"]["coverage"] == 0
    assert result["methods"]["direct_edge"]["indirect"]["conditional_truth_accuracy"] is None
    assert result["methods"]["direct_edge"]["direct"]["coverage"] == 1
    assert result["reported_energy_gap"] < 1e-10
    assert result["energy_gap"] < 1e-8
    assert result["query_immutable"] and result["reload_equal"]
    summary = aggregate([dict(result, split="train", arm="noisy")], m)["train/noisy"]
    assert summary["endpoint"] == "least-squares agreement"
    assert summary["fraction"] == 1


def test_evaluator_rejects_wrong_candidate_even_if_trace_says_pass(monkeypatch):
    actual = GeometryState.query
    def wrong(self, a, b):
        answer = actual(self, a, b)
        return Answer("OK", (0.0, 0.0)) if answer.status == "OK" else answer
    monkeypatch.setattr(GeometryState, "query", wrong)
    result = evaluate_world(generate(618, "continuous"), Settings(), HASH, 1e-5)
    assert result["primary_fraction"] < 0.99
    assert result["methods"]["candidate"]["indirect"]["total_least_squares_accuracy"] < 0.99
    assert result["reported_energy_gap"] > 1e-8


def test_nonconvergent_candidate_still_produces_metrics():
    result = evaluate_world(generate(619, "continuous"), Settings(max_sweeps=1), HASH, 1e-5)
    assert result["candidate"]["status"] == "NOT_CONVERGED"
    assert result["primary_fraction"] == 0
    assert result["methods"]["candidate"]["indirect"]["coverage"] == 0
    assert result["energy_gap"] is None
    json.dumps(result, allow_nan=False)


def test_cli_refuses_to_overwrite_completed_evidence(tmp_path):
    report = tmp_path / "contracts.xml"
    report.write_text('<testsuites><testsuite><testcase name="fixture"/></testsuite></testsuites>')
    results = tmp_path / "results.json"
    results.write_text("preserve me")
    run = subprocess.run([sys.executable, "-m", "geomind.run_c0", "--output", str(tmp_path), "--contract-report", str(report)], capture_output=True, text=True, cwd=ROOT)
    assert run.returncode != 0
    assert "Evidence already exists" in run.stderr
    assert results.read_text() == "preserve me"


def test_run_retains_every_infrastructure_failure_and_source_snapshot(tmp_path, monkeypatch):
    from geomind import run_c0
    report = tmp_path / "contracts.xml"
    report.write_text('<testsuites><testsuite><testcase name="fixture"/></testsuite></testsuites>')
    def broken(*args):
        raise RuntimeError("injected generation failure")
    monkeypatch.setattr(run_c0, "generate", broken)
    monkeypatch.setattr(sys, "argv", ["geomind.run_c0", "--output", str(tmp_path), "--contract-report", str(report)])
    assert run_c0.main() == 1
    receipt = json.loads((tmp_path / "results.json").read_text())
    assert receipt["implementation_status"] == "ACTIVE"
    assert not receipt["gates"]["infrastructure"]
    assert len(receipt["instances"]) == 1250
    assert all(r["check_status"] == "INFRASTRUCTURE_FAILURE" for r in receipt["instances"])
    assert len((tmp_path / "instances.jsonl").read_text().splitlines()) == 1250
    assert (tmp_path / "source/geomind/geometry.py").read_bytes() == (ROOT / "geomind/geometry.py").read_bytes()
