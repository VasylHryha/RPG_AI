"""Ten focused C1 checks; scaling belongs to the 16-case experiment."""

from dataclasses import replace
from collections import Counter
import json
from pathlib import Path

import numpy as np
import pytest

from geomind.c1_cases import KINDS, _with_relations, generate_case, save_initial_state
from geomind.c1_reference import SparseLeastSquares
from geomind.geometry import Answer, Constraint, GeometryState, Observation, Settings, digest
from geomind.incremental import IncrementalGeometry
from geomind.references import LeastSquares

HASH = digest({"fixture": "C1 focused contracts"})


@pytest.fixture(scope="module", autouse=True)
def bind_contracts_to_source(record_testsuite_property):
    from geomind.run_c1 import CONTRACT_SCOPE, ROOT, source_hashes
    before = source_hashes(ROOT / "experiments/c1_manifest.json")
    record_testsuite_property("c1_contract_scope", CONTRACT_SCOPE)
    record_testsuite_property("c1_file_hashes", json.dumps(before, sort_keys=True))
    yield
    assert source_hashes(ROOT / "experiments/c1_manifest.json") == before


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
        assert trace["dynamic_edge_visits"] == trace["warm_start_edge_visits"] + trace["local_edge_visits"] + trace["certificate_edge_visits"]
        assert trace["fallbacks"] == 0
        if kind != "inconsistent_edge":
            assert trace["status"] == "PASS", trace
        if trace["status"] == "NOT_CONVERGED":
            assert state.export() == before
        else:
            reference = LeastSquares(case.updated)
            for pair in case.queries:
                actual, expected = state.query(*pair), reference.query(*pair)
                assert actual.status == expected.status
                if actual.status == "OK":
                    assert actual.displacement == pytest.approx(expected.displacement, abs=1e-5)
            assert IncrementalGeometry.load(state.export()).export() == state.export()
        old = GeometryState.load(saved)
        for pair in case.retention_queries:
            assert state.query(*pair).displacement == old.query(*pair).displacement
    # A successful solver trace cannot qualify wrong or missing committed answers.
    from geomind.run_c1 import evaluate_case, validate_manifest
    manifest = validate_manifest(json.loads(Path("experiments/c1_manifest.json").read_text()))
    (tmp_path / "states").mkdir()
    case = generate_case(32, "consistent_edge", 72008)
    for answer in (Answer("OK", (100.0, -100.0)), Answer("UNKNOWN")):
        monkeypatch.setattr(IncrementalGeometry, "query", lambda self, *args: answer)
        row = evaluate_case(case, manifest, tmp_path, {"nodes": 32, "kind": "consistent_edge"})
        assert row["candidate"]["status"] == "PASS"
        assert row["check_status"] == "ASSERTION_FAILURE"
        assert not row["correct_commit"]
        json.dumps(row, allow_nan=False)
    original_query = GeometryState.query
    # One bad query after good answers must not be hidden by max-error logic.
    for invalid in (Answer("OK", (float("nan"), 0.0)), Answer("OK", (1e308, 1e308)), Answer("OK", (True, 0.0)), Answer("OK", (1.0,)), Answer(["OK"])):
        pair = case.affected_queries[-1]
        monkeypatch.setattr(IncrementalGeometry, "query", lambda self, a, b: invalid if (a, b) == pair else original_query(self, a, b))
        row = evaluate_case(case, manifest, tmp_path, {"nodes": 32, "kind": "consistent_edge"})
        assert row["check_status"] == "ASSERTION_FAILURE"
        json.dumps(row, allow_nan=False)


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
    tiny = replace(weighted, edges=tuple(replace(e, weight=e.weight * 1e-14) for e in weighted.edges))
    reference = SparseLeastSquares(tiny)
    assert reference.status == "PASS"
    assert reference.query("a", "b").displacement == pytest.approx((1.75, 0), abs=1e-10)
    for tolerance, budget in ((0, 10), (float("nan"), 10), (1e-11, True), (1e-11, 0)):
        with pytest.raises(ValueError):
            SparseLeastSquares(weighted, tolerance, budget)


def test_bridge_admits_cross_pairs_only_after_successful_commit():
    case = generate_case(32, "bridge", 72004)
    saved, state = branch(case)
    old = GeometryState.load(saved)
    reference = LeastSquares(case.updated)
    cross = [(a, b) for a, b in case.queries if old.query(a, b).status == "UNIDENTIFIABLE" and reference.query(a, b).status == "OK"]
    excluded = [p for p in case.queries if reference.query(*p).status == "UNIDENTIFIABLE"]
    assert cross
    old_hash = state.export()
    trace = state.update(case.updated, HASH, 0)
    assert trace["status"] == "NOT_CONVERGED"
    assert state.export() == old_hash
    assert all(state.query(*p).status == "UNIDENTIFIABLE" for p in cross)
    assert state.update(case.updated, HASH)["status"] == "PASS"
    assert all(state.query(*p).status == "OK" for p in cross)
    assert all(state.query(*p).status == "UNIDENTIFIABLE" for p in excluded)


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
    for encoded in ("null", "[]", "{", '{"schema":"bad"}', '{"schema":[]}'):
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


def test_chained_updates_cycles_duplicates_and_legacy_migration():
    base = Observation(("a", "m", "z"), (Constraint("a", "m", (1.25, -0.5), 2),))
    saved, _ = save_initial_state(base, HASH)
    state = IncrementalGeometry.from_saved(saved)
    stages = [
        (("0-leaf",), (Constraint("0-leaf", "a", (2.5, -1.25), 3),)),
        ((), (Constraint("z", "m", (0.25, 2.0)),)),
        (("x",), (Constraint("m", "x", (0.125, 0.5)), Constraint("m", "x", (0.125, 0.5), 3), Constraint("a", "x", (1.375, 0.0)))),
        ((), (Constraint("a", "m", (2.25, 0.5)), base.edges[0], base.edges[0])),
    ]
    for added_nodes, added_edges in stages:
        old = state.observation()
        updated = Observation(tuple(sorted(old.nodes + added_nodes)), old.edges + added_edges)
        trace = state.update(updated, HASH)
        assert trace["status"] == "PASS", trace
        reference = LeastSquares(updated)
        for a in updated.nodes:
            for b in updated.nodes:
                actual, expected = state.query(a, b), reference.query(a, b)
                assert actual.status == expected.status
                if actual.status == "OK":
                    assert actual.displacement == pytest.approx(expected.displacement, abs=1e-5)
        state.freeze()
        state = IncrementalGeometry.from_saved(state.export())
    before = state.export()
    old = state.observation()
    assert state.update(replace(old, edges=old.edges[:-1]), HASH)["status"] == "INVALID_STATE"
    assert state.export() == before
    payload = json.loads(saved)
    payload.pop("checksum")
    payload.update(schema="geomind.c1.geometry.v1", algorithm="budgeted-active-queue.v1")
    legacy = json.dumps(dict(payload, checksum=digest(payload)))
    migrated = IncrementalGeometry.from_saved(legacy)
    legacy_nodes = json.loads(legacy)["nodes"]
    assert migrated.export() != legacy.strip()
    assert migrated.query(legacy_nodes[0], legacy_nodes[1]).status in ("OK", "UNIDENTIFIABLE")


def test_custom_update_tolerance_and_overflow_are_transactional():
    base = Observation(("a", "b", "c"), (Constraint("a", "b", (1.0, 0.0)), Constraint("b", "c", (0.0, 1.0))))
    settings = Settings(gradient_tolerance=1e-6, update_tolerance=1e-12)
    saved, _ = save_initial_state(base, HASH, settings)
    state = IncrementalGeometry.from_saved(saved)
    updated = replace(base, edges=base.edges + (Constraint("a", "c", (2.0, 1.0)),))
    trace = state.update(updated, HASH)
    assert trace["status"] == "PASS", trace
    assert trace["update_max"] < settings.update_tolerance
    assert IncrementalGeometry.load(state.export()).export() == state.export()
    payload = json.loads(state.export())
    payload.pop("checksum")
    free = next(i for i in range(len(payload["nodes"])) if i not in payload["anchors"])
    payload["coordinates"][free][0] += 1e-8
    with pytest.raises(ValueError, match="update tolerance"):
        IncrementalGeometry.load(json.dumps(dict(payload, checksum=digest(payload))))
    before = state.export()
    old = state.observation()
    broken = replace(old, edges=old.edges + (Constraint("a", "c", (1e308, 1e308)),))
    trace = state.update(broken, HASH)
    assert trace["status"] == "INVALID_STATE"
    assert trace["dynamic_edge_visits"] > 0
    assert state.export() == before and trace["snapshot_retained"]
    json.dumps(trace, allow_nan=False)


def test_evidence_requires_complete_current_checks_and_accepted_source(tmp_path):
    import ast
    import shutil
    import xml.etree.ElementTree as ET
    from geomind.run_c1 import CONTRACT_SCOPE, ROOT, check_c0_acceptance, check_contract_report, check_output_directory, source_hashes
    hashes = source_hashes(ROOT / "experiments/c1_manifest.json")
    names = [n.name for n in ast.parse(Path(__file__).read_text()).body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]

    def report(scope=CONTRACT_SCOPE, expected_hashes=hashes, selected=names):
        suite = ET.Element("testsuite")
        properties = ET.SubElement(suite, "properties")
        ET.SubElement(properties, "property", name="c1_contract_scope", value=scope)
        ET.SubElement(properties, "property", name="c1_file_hashes", value=json.dumps(expected_hashes))
        for name in selected:
            ET.SubElement(suite, "testcase", name=name, classname="tests.test_c1")
        path = tmp_path / "contracts.xml"
        ET.ElementTree(suite).write(path)
        return path

    path = report()
    assert check_contract_report(path, hashes)["status"] == "PASS"
    for kwargs in ({"scope": "unrelated"}, {"expected_hashes": {}}, {"selected": names[:1]}):
        with pytest.raises(ValueError):
            check_contract_report(report(**kwargs), hashes)
    check_output_directory(tmp_path, path)
    sentinel = tmp_path / "states"
    sentinel.mkdir()
    with pytest.raises(FileExistsError):
        check_output_directory(tmp_path, path)
    assert sentinel.exists()
    assert check_c0_acceptance(ROOT)
    # Copy only reviewed C0 inputs into a disposable root and test drift.
    copy_root = tmp_path / "copy"
    folder = copy_root / "evidence/c0_review"
    folder.mkdir(parents=True)
    for name in ("results.json", "ACCEPTANCE.md"):
        shutil.copyfile(ROOT / "evidence/c0_review" / name, folder / name)
    receipt = json.loads((folder / "results.json").read_text())
    for name in receipt["file_hashes"]:
        target = copy_root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    assert check_c0_acceptance(copy_root)
    (copy_root / "geomind/geometry.py").write_text("changed input")
    with pytest.raises(ValueError, match="input changed"):
        check_c0_acceptance(copy_root)
    acceptance = folder / "ACCEPTANCE.md"
    acceptance.write_text(acceptance.read_text().replace("Verdict: **ACCEPTED**.", "Verdict: **NOT_ACCEPTED**."))
    with pytest.raises(ValueError, match="Explicit"):
        check_c0_acceptance(copy_root)
