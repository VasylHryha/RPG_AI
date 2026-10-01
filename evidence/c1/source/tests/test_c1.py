"""Seven focused C1 checks; sizes belong to the 16-case experiment, not CI."""

from dataclasses import replace
from collections import Counter
import json

import numpy as np
import pytest

from geomind.c1_cases import KINDS, _with_relations, generate_case, save_initial_state
from geomind.c1_reference import SparseLeastSquares
from geomind.geometry import Answer, Constraint, GeometryState, Observation, digest
from geomind.incremental import IncrementalGeometry
from geomind.references import LeastSquares

HASH = digest({"fixture": "C1 focused contracts"})


def branch(case):
    encoded, _ = save_initial_state(case.base, HASH)
    return encoded, IncrementalGeometry.from_saved(encoded)


def test_four_transactions_match_references_or_explicitly_reject(tmp_path, monkeypatch):
    for kind in KINDS:
        case = generate_case(32, kind, 72001)
        saved, state = branch(case)
        before = state.export()
        trace = state.update(case.updated, HASH)
        assert trace["status"] in ("PASS", "NOT_CONVERGED"), trace
        assert trace["dynamic_edge_visits"] <= 100000
        assert trace["dynamic_edge_visits"] == trace["local_edge_visits"] + trace["certificate_edge_visits"]
        assert trace["fallbacks"] == 0
        if trace["status"] == "NOT_CONVERGED":
            assert state.export() == before
        else:
            reference = LeastSquares(case.updated)
            for pair in case.queries:
                assert state.query(*pair).displacement == pytest.approx(reference.query(*pair).displacement, abs=1e-5)
            assert IncrementalGeometry.load(state.export()).export() == state.export()
        old = GeometryState.load(saved)
        for pair in case.retention_queries:
            assert state.query(*pair).displacement == old.query(*pair).displacement
    # A successful solver trace cannot qualify wrong or missing committed answers.
    from geomind.run_c1 import evaluate_case, validate_manifest
    from pathlib import Path
    manifest = validate_manifest(json.loads(Path("experiments/c1_manifest.json").read_text()))
    (tmp_path / "states").mkdir()
    case = generate_case(32, "consistent_edge", 72008)
    for answer in (Answer("OK", (100.0, -100.0)), Answer("UNKNOWN")):
        monkeypatch.setattr(IncrementalGeometry, "query", lambda self, *args: answer)
        row = evaluate_case(case, manifest, tmp_path, {"nodes": 32, "kind": "consistent_edge"})
        assert row["candidate"]["status"] == "PASS"
        assert row["check_status"] == "ASSERTION_FAILURE"
        assert not row["correct_commit"]


def test_budget_exhaustion_and_invalid_inputs_preserve_snapshot():
    case = generate_case(32, "bridge", 72002)
    saved, state = branch(case)
    before = state.export()
    for budget in (0, 1, -1, True, float("nan")):
        trace = state.update(case.updated, HASH, budget)
        assert trace["status"] in ("NOT_CONVERGED", "INVALID_STATE")
        assert trace["snapshot_retained"]
        assert state.export() == before
        json.dumps(trace, allow_nan=False)
    invalid = replace(case.updated, edges=case.updated.edges[1:])
    assert state.update(invalid, HASH)["status"] == "INVALID_STATE"
    assert state.export() == before


def test_sparse_reference_matches_dense_and_hand_computed_weighted_case():
    triangle = Observation(("a", "b", "c"), (Constraint("a", "b", (1, 0), 2), Constraint("b", "c", (0, 1), 1), Constraint("a", "c", (2, 1), 3)))
    for observation in (triangle, generate_case(32, "inconsistent_edge", 72003).updated):
        sparse, dense = SparseLeastSquares(observation), LeastSquares(observation)
        assert sparse.status == "PASS"
        assert sparse.energy == pytest.approx(dense.energy, abs=1e-10)
        for node in observation.nodes:
            actual, expected = sparse.query(observation.nodes[0], node), dense.query(observation.nodes[0], node)
            assert actual.status == expected.status
            if actual.status == "OK":
                assert actual.displacement == pytest.approx(expected.displacement, abs=1e-8)
    weighted = Observation(("a", "b"), (Constraint("a", "b", (1, 0), 1), Constraint("a", "b", (2, 0), 3)))
    reference = SparseLeastSquares(weighted)
    assert reference.query("a", "b").displacement == pytest.approx((1.75, 0), abs=1e-10)
    assert reference.energy == pytest.approx(0.375, abs=1e-10)


def test_bridge_admits_cross_pairs_only_after_successful_commit():
    case = generate_case(32, "bridge", 72004)
    saved, state = branch(case)
    old = GeometryState.load(saved)
    cross = [(a, b) for a, b in case.queries if old.query(a, b).status == "UNIDENTIFIABLE"]
    assert cross
    old_hash = state.export()
    trace = state.update(case.updated, HASH, 0)
    assert trace["status"] == "NOT_CONVERGED"
    assert state.export() == old_hash
    assert all(state.query(*p).status == "UNIDENTIFIABLE" for p in cross)


def test_frozen_state_forks_and_queries_do_not_mutate_parent_or_sibling():
    case = generate_case(32, "consistent_edge", 72005)
    saved, state = branch(case)
    sibling = IncrementalGeometry.from_saved(saved)
    before = sibling.export()
    assert state.update(case.updated, HASH)["status"] == "PASS"
    state.freeze()
    encoded = state.export()
    for pair in case.queries:
        state.query(*pair)
    assert state.export() == encoded
    assert sibling.export() == before
    with pytest.raises(RuntimeError):
        state.update(case.updated, HASH)
    assert GeometryState.load(saved).export() == saved


def test_gauge_shift_preserves_unaffected_component_and_bad_artifacts_fail():
    case = generate_case(32, "new_node", 72006)
    saved, state = branch(case)
    for encoded in ("null", "[]", "{", '{"schema":"bad"}'):
        with pytest.raises(ValueError):
            IncrementalGeometry.from_saved(encoded)
    before = state.export()
    wrong = replace(case.updated, relations=case.updated.relations + ((case.updated.relations[0][0], (100, 100)),))
    assert state.update(wrong, HASH)["status"] == "INVALID_STATE"
    assert state.export() == before
    record = json.loads(saved)
    main = record["components"][record["nodes"].index(case.updated.edges[-1].source)]
    degrees = Counter(n for e in case.base.edges for n in (e.source, e.target))
    options = [n for i, n in enumerate(record["nodes"]) if record["components"][i] == main and i not in record["anchors"]]
    a = max(options, key=lambda n: degrees[n])
    b = case.updated.edges[-1].source
    if a == b:
        b = next(n for n in options if n != a)
    vector = state.query(a, b).displacement
    edges, relations = _with_relations(case.base, (Constraint(a, b, vector),))
    shifted = replace(case.base, edges=edges, relations=relations)
    assert state.update(shifted, HASH)["status"] == "PASS"
    assert json.loads(state.export())["anchors"] != record["anchors"]
    original = GeometryState.load(saved)
    for pair in case.retention_queries:
        assert state.query(*pair) == original.query(*pair)


def test_saved_state_setup_uses_public_constraints_and_is_exact():
    case = generate_case(128, "consistent_edge", 72007)
    saved, setup = save_initial_state(case.base, HASH)
    state = GeometryState.load(saved)
    assert setup["total_seconds"] >= setup["compile_seconds"]
    assert setup["compile_edge_visits"] == 2 * len(case.base.edges)
    for pair in case.queries:
        actual = state.query(*pair)
        if actual.status == "OK":
            assert actual.displacement == pytest.approx(np.asarray(case.truth[pair[1]]) - case.truth[pair[0]], abs=1e-12)
