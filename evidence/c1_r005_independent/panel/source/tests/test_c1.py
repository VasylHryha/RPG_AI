"""Focused C1 checks; scaling belongs to the registered two-arm panel."""

from collections import Counter
from dataclasses import replace
import gzip
import json
from pathlib import Path

import numpy as np
import pytest

from geomind.c1_cases import KINDS, _with_relations, generate_case, save_initial_state
from geomind.c1_reference import SparseLeastSquares
from geomind.geometry import Answer, Constraint, GeometryState, Observation, Settings, digest
from geomind.incremental import TRACE_COUNTERS, IncrementalGeometry, _C1V2State, _C1V3State, _C1V4State
from geomind.references import LeastSquares

HASH = digest({"fixture": "C1 focused contracts"})
FALLBACK = 5_000_000


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


def matches_reference(state, observation, pairs=None, tolerance=1e-5):
    reference = LeastSquares(observation)
    pairs = pairs if pairs is not None else [(a, b) for a in observation.nodes for b in observation.nodes]
    for pair in pairs:
        actual, expected = state.query(*pair), reference.query(*pair)
        assert actual.status == expected.status, pair
        if actual.status == "OK":
            assert actual.displacement == pytest.approx(expected.displacement, abs=tolerance)


def test_both_arms_match_references_or_explicitly_reject():
    for kind in KINDS:
        case = generate_case(32, kind, 72001)
        saved, _ = branch(case)
        old = GeometryState.load(saved)
        for fallback in (0, FALLBACK):
            state = IncrementalGeometry.from_saved(saved)
            before = state.export()
            trace = state.update(case.updated, HASH, 100000, fallback)
            assert trace["status"] in ("PASS", "NOT_CONVERGED"), trace
            assert trace["charged_operations"] == sum(trace[c] for c in TRACE_COUNTERS) <= 100000
            assert trace["fallbacks"] == int(trace["queue_exhausted"]) and (fallback or not trace["fallbacks"])
            if kind != "inconsistent_edge" or fallback:
                assert trace["status"] == "PASS", trace
            if trace["status"] == "PASS":
                matches_reference(state, case.updated, case.queries)
                loaded = IncrementalGeometry.load(state.export())
                assert loaded.export() == state.export()
                assert all(loaded.query(*p) == state.query(*p) for p in case.queries)
            else:
                assert state.export() == before
            for pair in case.retention_queries:
                assert state.query(*pair) == old.query(*pair)


def test_mid_relaxation_refusal_restores_every_structure():
    case = generate_case(32, "inconsistent_edge", 72002)
    saved, _ = branch(case)
    base = case.base
    a = next(e.source for e in Counter(case.updated.edges) - Counter(base.edges))
    third = case.retention_queries[0][1]
    vector = tuple(float(v) for v in np.asarray(case.truth[third]) - case.truth[a])
    # One delta mixing a new node, a bridge into the third component and a contradiction.
    added_edges = tuple((Counter(case.updated.edges) - Counter(base.edges)).elements()) + (
        Constraint(a, "zz-new", (0.5, 0.5)), Constraint(a, third, vector))
    edges, relations = _with_relations(base, added_edges)
    delta = (("zz-new",), edges[len(base.edges):], tuple(r for r in relations if r[0] not in dict(base.relations)))
    for budget in (0, 1, -1, True, float("nan"), 2000):
        state = IncrementalGeometry.from_saved(saved)
        before = state.export()
        trace = state.apply(*delta, HASH, budget)
        assert trace["status"] in ("NOT_CONVERGED", "INVALID_STATE")
        assert state.export() == before
        json.dumps(trace, allow_nan=False)
        if budget == 2000:
            assert trace["status"] == "NOT_CONVERGED"
            assert trace["node_updates"] > 0 and trace["translated_nodes"] > 0 and trace["journal_entries_undone"] > 0
            # Internal structures, not just the export, are restored: the same
            # delta then behaves exactly like it does on a fresh fork.
            fresh = IncrementalGeometry.from_saved(saved)
            first, second = state.apply(*delta, HASH, 100000, FALLBACK), fresh.apply(*delta, HASH, 100000, FALLBACK)
            assert first["status"] == second["status"] == "PASS" and state.export() == fresh.export()
            assert {k: first[k] for k in TRACE_COUNTERS} == {k: second[k] for k in TRACE_COUNTERS}
            matches_reference(state, Observation(tuple(sorted(base.nodes + ("zz-new",))), edges, relations))
    invalid = replace(case.updated, edges=case.updated.edges[1:])
    state = IncrementalGeometry.from_saved(saved)
    before = state.export()
    assert state.update(invalid, HASH)["status"] == "INVALID_STATE" and state.export() == before


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
    assert cross and excluded
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
    with pytest.raises(RuntimeError):
        state.apply((), (), (), HASH)
    assert IncrementalGeometry.load(encoded).export() == encoded
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
    assert state.apply((), (), ((case.base.relations[0][0], (100.0, 100.0)),), HASH)["status"] == "INVALID_STATE"
    assert state.export() == before
    record = json.loads(saved)
    anchor = record["nodes"][record["anchors"][0]]
    degrees = Counter(n for e in case.base.edges for n in (e.source, e.target))
    # Consistent edges into one non-anchor node lift it above the old anchor.
    options = sorted((n for i, n in enumerate(record["nodes"]) if record["components"][i] == 0 and n != anchor), key=lambda n: (-degrees[n], n))
    target = options[0]
    linked = {(e.source, e.target) for e in case.base.edges} | {(e.target, e.source) for e in case.base.edges}
    extra = [n for n in options[1:] if (n, target) not in linked][:degrees[anchor] - degrees[target] + 1]
    added = tuple(Constraint(n, target, state.query(n, target).displacement) for n in extra)
    edges, relations = _with_relations(case.base, added)
    assert state.update(replace(case.base, edges=edges, relations=relations), HASH)["status"] == "PASS"
    assert json.loads(state.export())["anchors"][0] != record["anchors"][0]
    original = GeometryState.load(saved)
    for pair in case.retention_queries + case.queries:
        if original.query(*pair).status == "OK":
            assert state.query(*pair).displacement == pytest.approx(original.query(*pair).displacement, abs=1e-12)


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


def test_chained_updates_cycles_duplicates_and_real_artifact_migration():
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
        trace = state.update(updated, HASH, 100000, FALLBACK)
        assert trace["status"] == "PASS", trace
        matches_reference(state, updated)
        state.freeze()
        state = IncrementalGeometry.from_saved(state.export())
    before = state.export()
    old = state.observation()
    copy = next(e for e, n in Counter(old.edges).items() if n > 1)
    edges = list(old.edges)
    edges.remove(copy)  # remove exactly one duplicate copy
    assert state.update(replace(old, edges=tuple(edges)), HASH)["status"] == "INVALID_STATE"
    assert state.export() == before
    from geomind.run_c1 import ROOT
    for adapter, path in ((_C1V2State, "evidence/c1_review/states/32_inconsistent_edge_after.json"),
                          (_C1V3State, "evidence/c1_r003/states/32_bridge_w0_after.json"),
                          (_C1V4State, "evidence/c1_r004/states/32_bridge_w0_queue_after.json.gz")):
        path = ROOT / path
        archived = (gzip.open(path, "rt").read() if path.suffix == ".gz" else path.read_text()).rstrip("\n")
        original, migrated = adapter.load(archived), IncrementalGeometry.from_saved(archived)
        nodes = json.loads(archived)["nodes"]
        assert json.loads(migrated.export())["schema"] == IncrementalGeometry.schema
        assert all(original.query(a, b) == migrated.query(a, b) for a in nodes for b in nodes)


def test_custom_update_tolerance_and_overflow_are_transactional():
    base = Observation(("a", "b", "c"), (Constraint("a", "b", (1.0, 0.0)), Constraint("b", "c", (0.0, 1.0))))
    settings = Settings(gradient_tolerance=1e-6, update_tolerance=1e-12)
    saved, _ = save_initial_state(base, HASH, settings)
    state = IncrementalGeometry.from_saved(saved)
    # A contradiction forces real relaxation under the stricter step bound.
    updated = replace(base, edges=base.edges + (Constraint("a", "c", (2.25, 0.75)),))
    trace = state.update(updated, HASH)
    assert trace["status"] == "PASS", trace
    assert trace["node_updates"] > 0 and trace["update_max"] < settings.update_tolerance
    matches_reference(state, updated)
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
    for fallback in (0, FALLBACK):
        trace = state.update(broken, HASH, 100000, fallback)
        assert trace["status"] == "INVALID_STATE"
        assert trace["charged_operations"] > 0
        assert state.export() == before
        json.dumps(trace, allow_nan=False)


def test_exact_operation_accounting_and_exhaustion_point():
    base = Observation(("a", "b", "c", "d"), (Constraint("a", "b", (1.0, 0.0)), Constraint("c", "d", (0.0, 1.0))))
    saved, _ = save_initial_state(base, HASH)
    bridge = (Constraint("b", "c", (2.0, 0.5)),)
    state = IncrementalGeometry.from_saved(saved)
    trace = state.apply((), bridge, (), HASH)
    # 1 input; degree lists of b and c (1 + 1) plus 2 inserts; 1 frame read plus
    # 2 discovery and 2 placement reads; anchor candidates {a, b, c} pick b
    # (degree 2, then smallest ID), so {a, b} is re-stored around b and {c, d}
    # is placed: 4 writes; quiet pops of freed anchors a (degree 1) and c
    # (degree 2); certificate of written/freed non-anchors a, c, d (1 + 2 + 1).
    assert {k: trace[k] for k in TRACE_COUNTERS} == {"input_records": 1, "degree_reads": 4, "frame_edge_reads": 5, "translation_writes": 4,
                                                     "anchor_reads": 3, "local_edge_reads": 3, "certificate_reads": 4}
    assert trace["charged_operations"] == 24 and trace["node_updates"] == 0 and trace["certificate_passes"] == 1
    assert trace["translated_nodes"] == 4 and trace["regauged_components"] == 1
    assert json.loads(state.export())["anchors"] == [1] and state.query("a", "d").displacement == pytest.approx((3.0, 1.5))
    short = IncrementalGeometry.from_saved(saved)
    before = short.export()
    trace = short.apply((), bridge, (), HASH, 23)
    assert trace["status"] == "NOT_CONVERGED" and trace["budget_exhaustion_required"] == 1 and trace["charged_operations"] == 23
    assert short.export() == before
    # The compatibility path charges the full observation and current state it diffs.
    full = IncrementalGeometry.from_saved(saved).update(replace(base, edges=base.edges + bridge), HASH)
    assert full["input_records"] == 1 + (4 + 3 + 0) + (4 + 2) and full["charged_operations"] == 23 + full["input_records"]


def node_forces(encoded):
    """Global C0 force per non-anchor node name, from an exported snapshot."""
    from geomind.geometry import _gradient, _prepare
    record = json.loads(encoded)
    observation = Observation(tuple(record["nodes"]), tuple(Constraint(e["source"], e["target"], tuple(e["offset"]), e["weight"], e["relation_id"]) for e in record["edges"]))
    nodes, index, edges, source, target, offsets, weights, degree, components, anchors = _prepare(observation)
    _, _, gradient = _gradient(np.array(record["coordinates"], dtype=np.float64).reshape(-1, 2), source, target, offsets, weights, anchors)
    return {name: (None if i in anchors else gradient[i]) for i, name in enumerate(nodes)}


def random_chains(seed, trials, scale_range):
    """Chained random deltas from candidate-produced states; every commit is audited globally."""
    from geomind.geometry import _prepare
    rng = np.random.default_rng(seed)
    outcomes = Counter()
    for trial in range(trials):
        scale = 10 ** rng.uniform(*scale_range)
        count = int(rng.integers(3, 10))
        nodes = tuple(f"n{trial:02d}{k}" for k in range(count))
        position = {n: rng.normal(scale=scale, size=2) for n in nodes}
        edges = []
        for k in range(1, count):
            if rng.random() < 0.8:
                j = int(rng.integers(0, k))
                edges.append(Constraint(nodes[j], nodes[k], tuple(float(v) for v in position[nodes[k]] - position[nodes[j]]), float(rng.uniform(0.25, 3))))
        try:
            saved, _ = save_initial_state(Observation(nodes, tuple(edges)), HASH)
        except ValueError:
            outcomes["INIT_SKIPPED"] += 1  # compiled setup rounding above 1e-10 at extreme scales
            continue
        state = IncrementalGeometry.from_saved(saved)
        for stage in range(3):
            fresh = tuple(f"m{trial:02d}{stage}{k}" for k in range(int(rng.integers(0, 3))))
            for name in fresh:
                position[name] = rng.normal(scale=scale, size=2)
            universe = list(state.observation().nodes) + list(fresh)
            added = []
            for _ in range(int(rng.integers(1, 5))):
                s, t = (str(v) for v in rng.choice(universe, 2, replace=False))
                noise = rng.normal(scale=0.5, size=2) if rng.random() < 0.4 else np.zeros(2)
                added.append(Constraint(s, t, tuple(float(v) for v in position[t] - position[s] + noise), float(rng.uniform(0.25, 3))))
            before = state.export()
            forces_before = node_forces(before)
            # A smaller queue cap keeps this soundness check fast; the cap is not under test here.
            trace = state.apply(fresh, tuple(added), (), HASH, 20000, FALLBACK if rng.random() < 0.5 else 0)
            outcomes[trace["status"]] += 1
            if trace["status"] != "PASS":
                assert state.export() == before, trace
                break
            # The accepted C0 validator must accept every commit, with identical answers.
            exported = state.export()
            loaded = IncrementalGeometry.load(exported)
            observation = state.observation()
            assert all(loaded.query(a, b) == state.query(a, b) for a in observation.nodes for b in observation.nodes)
            if scale < 100:
                matches_reference(loaded, observation, tolerance=1e-6)
            # Degrees equal the C0 validator's bit for bit.
            degree = _prepare(observation)[7]
            assert all(state._deg[state._id[name]] == float(value) for name, value in zip(sorted(state._names), degree))
            # Export-gauge soundness: any node whose C0 force changed at all was certified.
            forces_after = node_forces(exported)
            changed = {n for n, f in forces_after.items() if f is not None and (n not in forces_before or forces_before[n] is None or not np.array_equal(f, forces_before[n]))}
            assert changed <= state._last_certified, changed - state._last_certified
    return outcomes


def test_local_certificate_agrees_with_global_validation_on_random_chains():
    outcomes = random_chains(20261002, 60, (0, 1))
    assert outcomes["PASS"] >= 100 and set(outcomes) <= {"PASS", "NOT_CONVERGED"}
    # A relaxation frontier: a contradicting triangle t0-t1-t2 anchored at hub t2.
    # The leaf hangs on t2 (weight 1) and on t1 (weight 1e-9): when t1 moves its
    # force changes by under the tolerance, so it is popped quiet and never
    # moves. Only the neighbors-of-moved-nodes rule certifies it.
    edges = [Constraint("t0", "t1", (1.0, 0.0)), Constraint("t1", "t2", (0.0, 1.0)),
             Constraint("t1", "leaf", (0.5, 0.5), 1e-9), Constraint("t2", "leaf", (0.5, -0.5))]
    edges += [Constraint("t2", f"hub{k}", (float(k + 1), 0.0)) for k in range(3)]
    base = Observation(("hub0", "hub1", "hub2", "leaf", "t0", "t1", "t2"), tuple(edges))
    saved, _ = save_initial_state(base, HASH)
    state = IncrementalGeometry.from_saved(saved)
    before = node_forces(state.export())
    trace = state.apply((), (Constraint("t0", "t2", (1.5, 1.25)),), (), HASH)
    assert trace["status"] == "PASS" and trace["node_updates"] > 0
    after = node_forces(state.export())
    changed = {n for n, f in after.items() if f is not None and (before[n] is None or not np.array_equal(f, before[n]))}
    assert "leaf" in changed and changed <= state._last_certified, changed - state._last_certified
    matches_reference(IncrementalGeometry.load(state.export()), state.observation())


def test_incremental_compiled_baseline_is_exact_and_atomic():
    from geomind.c1_reference import IncrementalCompiled
    base = Observation(("a", "b", "c", "d", "e"), (Constraint("a", "b", (1.0, 0.0)), Constraint("b", "c", (0.0, 1.0)), Constraint("d", "e", (2.0, 2.0))))
    # Both translation branches: the smaller component holds the source, then the target.
    # Operations: input records plus every translated node (ties move the source side).
    for added, operations in (((Constraint("d", "a", (-3.0, 0.5)),), 1 + 2), ((Constraint("a", "d", (3.0, -0.5)),), 1 + 2),
                              ((Constraint("e", "x", (1.0, 1.0)), Constraint("x", "c", (0.25, -4.0))), 3 + 1 + 3)):
        nodes = ("x",) if any("x" in (e.source, e.target) for e in added) else ()
        baseline = IncrementalCompiled(base)
        assert baseline.apply(nodes, added) == ("PASS", operations)
        updated = Observation(tuple(sorted(base.nodes + nodes)), base.edges + added)
        matches_reference(baseline, updated, tolerance=1e-12)
    baseline = IncrementalCompiled(base)
    before = dict(baseline.coordinates)
    assert baseline.apply(("x",), (Constraint("d", "a", (-3.0, 0.5)), Constraint("a", "e", (9.0, 9.0)), Constraint("a", "x", (1.0, 1.0))))[0] == "NOT_CONVERGED"
    assert baseline.coordinates == before and "x" not in baseline.coordinates


def test_export_gauge_certificate_holds_at_large_coordinates_and_reanchoring():
    # Independent review F2(c): candidate-only chains at coordinate scales 1e3-1e6.
    outcomes = random_chains(20261003, 60, (3, 6))
    assert outcomes["PASS"] >= 60 and set(outcomes) <= {"PASS", "NOT_CONVERGED", "INIT_SKIPPED"}
    # F2(a): a near-tolerance node in a frame translated by a large bridge offset.
    chain_a, chain_b = ("a0", "a1", "a2", "a3"), ("p", "q", "r")
    base = Observation(tuple(sorted(chain_a + chain_b)), (Constraint("a0", "a1", (1.0, 0.0)), Constraint("a1", "a2", (1.0, 0.0)), Constraint("a2", "a3", (1.0, 0.0)),
                                                         Constraint("p", "q", (0.1, 0.0)), Constraint("q", "r", (0.3, 0.7))))
    saved, _ = save_initial_state(base, HASH)
    record = json.loads(saved)
    record.pop("checksum")
    record["coordinates"][record["nodes"].index("r")][0] += 0.9999e-8
    near = json.dumps(dict(record, checksum=digest(record)), sort_keys=True, separators=(",", ":"))
    GeometryState.load(near)
    for shift in (1e3, 1e5, 1e6):
        state = IncrementalGeometry.from_saved(near)
        trace = state.apply((), (Constraint("a0", "p", (shift + 0.37, 0.11)),), (), HASH)
        assert trace["status"] == "PASS" and "r" in state._last_certified
        assert IncrementalGeometry.load(state.export()).export() == state.export()
    # F2(b): three new leaves make a distant node the anchor (re-gauge).
    for far, gap in ((1e3, 1e-14), (1e5, 1e-12), (1e5, 1e-13), (1e6, 1e-11)):
        base = Observation(("p", "q", "r", "z"), (Constraint("q", "p", (far, 0.0)), Constraint("q", "r", (0.3, 0.7)), Constraint("q", "z", (0.0, -1.0))))
        saved, _ = save_initial_state(base, HASH)
        record = json.loads(saved)
        record.pop("checksum")
        record["coordinates"][record["nodes"].index("r")][0] = 0.3 + (1e-8 - gap)
        near = json.dumps(dict(record, checksum=digest(record)), sort_keys=True, separators=(",", ":"))
        GeometryState.load(near)
        state = IncrementalGeometry.from_saved(near)
        trace = state.apply(("s0", "s1", "s2"), tuple(Constraint("p", f"s{k}", (float(k), 1.0)) for k in range(3)), (), HASH)
        assert trace["status"] == "PASS" and trace["regauged_components"] == 1 and "r" in state._last_certified
        exported = state.export()
        assert json.loads(exported)["nodes"][json.loads(exported)["anchors"][0]] == "p"
        loaded = IncrementalGeometry.load(exported)
        assert all(loaded.query(a, b) == state.query(a, b) for a in ("p", "q", "r", "z") for b in ("p", "q", "r", "z"))


def test_overflow_and_invalid_inputs_never_commit_unpersistable_state():
    # Independent review F3: a duplicate 1e308-weight edge overflows the degree.
    big = Observation(("a", "b", "c"), (Constraint("a", "b", (1.0, 0.0), 1e308), Constraint("b", "c", (0.0, 1.0))))
    saved, _ = save_initial_state(big, HASH)
    state = IncrementalGeometry.from_saved(saved)
    before = state.export()
    trace = state.apply((), (Constraint("a", "b", (1.0, 0.0), 1e308),), (), HASH)
    assert trace["status"] == "INVALID_STATE" and "degree" in trace["reason"] and state.export() == before
    # Huge residuals cannot be certified: the rounding bound exceeds the tolerance,
    # so the update refuses explicitly instead of committing an unpersistable state.
    pair = Observation(("a", "b"), (Constraint("a", "b", (0.0, 0.0)),))
    saved, _ = save_initial_state(pair, HASH)
    state = IncrementalGeometry.from_saved(saved)
    before = state.export()
    trace = state.apply((), (Constraint("a", "b", (4e150, 0.0)),), (), HASH, 1000, FALLBACK)
    assert trace["status"] == "NOT_CONVERGED" and state.export() == before
    # F7: an invalid delta larger than the cap is INVALID_STATE, not NOT_CONVERGED.
    small = Observation(("a", "b"), (Constraint("a", "b", (1.0, 0.0)),))
    saved, _ = save_initial_state(small, HASH)
    state = IncrementalGeometry.from_saved(saved)
    oversized = tuple(f"x{k:06d}" for k in range(100001)) + ("",)
    assert state.apply(oversized, (), (), HASH)["status"] == "INVALID_STATE"
    assert state.apply(oversized[:-1], (), (), HASH)["status"] == "NOT_CONVERGED"


def test_delta_validation_reads_no_stored_relations():
    """Independent review F1: no in-memory step may scan state proportional to its size."""
    from collections.abc import MutableMapping

    class Counting(MutableMapping):
        def __init__(self, data):
            self.data, self.scans, self.lookups = dict(data), 0, 0

        def __getitem__(self, key):
            self.lookups += 1
            return self.data[key]

        def __contains__(self, key):
            self.lookups += 1
            return key in self.data

        def __iter__(self):
            self.scans += 1
            return iter(self.data)

        def __len__(self):
            return len(self.data)

        def __setitem__(self, key, value):
            self.data[key] = value

        def __delitem__(self, key):
            del self.data[key]

    case = generate_case(512, "consistent_edge", 72011)
    saved, state = branch(case)
    stored = Counting(state._relation_map)
    state._relation_map = stored
    added = tuple((Counter(case.updated.edges) - Counter(case.base.edges)).elements())
    relations = tuple(r for r in case.updated.relations if r[0] not in stored.data)
    assert len(stored) > 500
    trace = state.apply((), added, relations, HASH)
    assert trace["status"] == "PASS" and stored.scans == 0 and stored.lookups <= 4 * (len(added) + len(relations)) + 4


def test_tiny_weight_contradiction_needs_the_fallback_arm():
    tiny = Observation(("a", "b", "c"), (Constraint("a", "b", (1.0, 0.0), 1e-6), Constraint("b", "c", (0.0, 1.0), 1e-6)))
    saved, _ = save_initial_state(tiny, HASH)
    delta = ((), (Constraint("a", "c", (2.0, 0.5), 1e-6),), ())
    queue, fallback = IncrementalGeometry.from_saved(saved), IncrementalGeometry.from_saved(saved)
    assert queue.apply(*delta, HASH)["status"] == "NOT_CONVERGED"
    trace = fallback.apply(*delta, HASH, 100000, FALLBACK)
    assert trace["status"] == "PASS" and trace["fallbacks"] == 1 and trace["fallback_operations"] <= FALLBACK
    matches_reference(fallback, replace(tiny, edges=tiny.edges + delta[1]), tolerance=1e-7)
    # An exhausted fallback cap is an explicit refusal with the prior state intact.
    starved = IncrementalGeometry.from_saved(saved)
    before = starved.export()
    trace = starved.apply(*delta, HASH, 100000, 12)
    assert trace["status"] == "NOT_CONVERGED" and trace["fallbacks"] == 1 and trace["queue_exhausted"]
    assert trace["fallback_operations"] + trace["fallback_exhaustion_required"] > 12 and starved.export() == before


def test_evaluator_negative_controls_two_arms_and_stale_coverage(tmp_path, monkeypatch):
    from geomind.run_c1 import evaluate_case, validate_manifest
    manifest = validate_manifest(json.loads(Path("experiments/c1_manifest.json").read_text()))
    (tmp_path / "states").mkdir()
    case = generate_case(32, "bridge", 72009)
    identity = {"nodes": 32, "kind": "bridge"}
    row = evaluate_case(case, manifest, tmp_path, identity)
    assert row["check_status"] == "PASS" and row["arms_agree"] and all(a["correct_commit"] for a in row["arms"].values())
    with gzip.open(tmp_path / "states/32_bridge_before.json.gz", "rt") as stream:
        assert stream.read().rstrip("\n") == save_initial_state(case.base, digest(manifest))[0]
    original_query = IncrementalGeometry.query
    # A confident answer for a pair that stays unidentifiable must fail.
    monkeypatch.setattr(IncrementalGeometry, "query", lambda self, a, b: Answer("OK", (0.0, 0.0)) if original_query(self, a, b).status == "UNIDENTIFIABLE" else original_query(self, a, b))
    row = evaluate_case(case, manifest, tmp_path, identity)
    assert row["check_status"] == "ASSERTION_FAILURE" and row["arms"]["queue"]["cross_abstention_correct"] < row["excluded_cross_queries"]
    # Correct panel answers cannot hide a wrong committed relation elsewhere.
    asked = set(case.queries + case.affected_queries)
    edge = next(e for e in case.updated.edges if (e.source, e.target) not in asked)
    monkeypatch.setattr(IncrementalGeometry, "query", lambda self, a, b: Answer("OK", tuple(np.add(original_query(self, a, b).displacement, 1e-3))) if (a, b) == (edge.source, edge.target) else original_query(self, a, b))
    row = evaluate_case(case, manifest, tmp_path, identity)
    assert row["arms"]["queue"]["least_squares_displacement_error_max"] <= manifest["displacement_tolerance"]
    assert row["check_status"] == "ASSERTION_FAILURE" and not row["arms"]["queue"]["correct_commit"]
    monkeypatch.setattr(IncrementalGeometry, "query", original_query)
    # A wrong incremental compiled baseline fails the case too.
    from geomind.c1_reference import IncrementalCompiled
    baseline_query = IncrementalCompiled.query
    monkeypatch.setattr(IncrementalCompiled, "query", lambda self, a, b: Answer("OK", (0.5, 0.5)) if baseline_query(self, a, b).status == "OK" else baseline_query(self, a, b))
    row = evaluate_case(case, manifest, tmp_path, identity)
    assert row["check_status"] == "ASSERTION_FAILURE" and not row["incremental_compiled"]["correct"]
    monkeypatch.setattr(IncrementalCompiled, "query", baseline_query)
    # A refused update's prior-state answers are never reported as coverage.
    row = evaluate_case(case, dict(manifest, edge_visit_budget=2), tmp_path, identity)
    queue = row["arms"]["queue"]
    assert row["check_status"] == "PASS" and queue["explicit_rejection"] and not queue["committed"]
    assert queue["update_coverage"] is None and queue["update_total_accuracy"] is None and queue["prior_state_ok_answers"] > 0
    # Contradiction: the queue arm refuses, the fallback arm commits correctly.
    case = generate_case(32, "inconsistent_edge", 72010)
    row = evaluate_case(case, manifest, tmp_path, {"nodes": 32, "kind": "inconsistent_edge"})
    assert row["check_status"] == "PASS"
    assert row["arms"]["queue"]["explicit_rejection"] and row["arms"]["fallback"]["correct_commit"]
    assert row["arms"]["fallback"]["candidate"]["fallbacks"] == 1


def test_registered_endpoint_rules_are_applied_as_written():
    from geomind.run_c1 import evaluate_endpoints, validate_manifest
    manifest = validate_manifest(json.loads(Path("experiments/c1_manifest.json").read_text()))

    def row(kind, nodes, ops, seconds, ratio=0.01, committed=True, regauged=0):
        queue = {"committed": committed, "apply_seconds": seconds, "update_to_fresh_recompute_ratio": ratio if committed else None,
                 "candidate": {"charged_operations": ops, "regauged_components": regauged, "fallback_operations": 0}}
        return {"check_status": "PASS", "kind": kind, "nodes": nodes, "reference_edge_visits": 1000,
                "arms": {"queue": queue, "fallback": dict(queue, committed=True)}, "incremental_compiled": {"apply_seconds": seconds, "operations": ops}}

    def panel(time_large=2e-4, ops_large=36, contradictions=False):
        records = []
        for kind in KINDS:
            for nodes in manifest["sizes"]:
                for _ in range(manifest["replicates"]):
                    hard = kind == "inconsistent_edge"
                    records.append(row(kind, nodes, ops_large if nodes == 2048 else 30, time_large if nodes == 2048 else 1e-4,
                                       committed=not hard or contradictions))
        return records

    _, verdicts = evaluate_endpoints(panel(), manifest)
    assert verdicts["consistent_edge_and_new_node_in_memory_updates"] == "SUPPORTED_WITHIN_SCOPE"
    assert verdicts["contradiction_resolution_by_local_queue"] == "NOT_SUPPORTED"
    # Uncharged work shows up only on the clock: 5x slower at 2048 fails the 4x rule.
    _, verdicts = evaluate_endpoints(panel(time_large=5e-4), manifest)
    assert verdicts["consistent_edge_and_new_node_in_memory_updates"] == "NOT_SUPPORTED"
    _, verdicts = evaluate_endpoints(panel(ops_large=61), manifest)
    assert verdicts["consistent_edge_and_new_node_in_memory_updates"] == "NOT_SUPPORTED"
    _, verdicts = evaluate_endpoints(panel(contradictions=True), manifest)
    assert verdicts["contradiction_resolution_by_local_queue"] == "SUPPORTED_WITHIN_SCOPE"


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
