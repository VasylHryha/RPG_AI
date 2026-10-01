"""Independent reviewer focused checks for C1 R002 (Claude review).

Read-only with respect to the original receipts: loads archived states and the
live source, writes only into this directory. Does not rerun the C0 experiment
or the registered 16-case C1 panel.

Run: .venv/bin/python evidence/c1_claude_review/review_checks.py
"""

import hashlib
import json
import sys
import time
from collections import Counter
from dataclasses import replace
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from geomind.c1_cases import KINDS, generate_case, save_initial_state  # noqa: E402
from geomind.c1_reference import SparseLeastSquares  # noqa: E402
from geomind.geometry import Constraint, GeometryState, Observation, Settings, digest  # noqa: E402
from geomind.incremental import IncrementalGeometry, _C1V1State  # noqa: E402
from geomind.references import LeastSquares  # noqa: E402
from geomind.run_c0 import source_hashes  # noqa: E402

EVIDENCE = ROOT / "evidence/c1_review"
SIZES = (32, 128, 512, 2048)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_identity():
    receipt = json.loads((EVIDENCE / "results.json").read_text())
    live = source_hashes((ROOT / "experiments/c1_manifest.json").resolve())
    archived = {name: sha(EVIDENCE / "source" / name) for name in receipt["file_hashes"]}
    states = {}
    for row in receipt["instances"]:
        label = f"{row['nodes']}_{row['kind']}"
        for suffix, key in (("before", "old_artifact_hash"), ("fork_before", "fork_before_artifact_hash"), ("after", "after_artifact_hash")):
            text = (EVIDENCE / "states" / f"{label}_{suffix}.json").read_text()
            states[f"{label}_{suffix}"] = hashlib.sha256(text.rstrip("\n").encode()).hexdigest() == row[key]
    return {
        "receipt_matches_live": receipt["file_hashes"] == live,
        "receipt_matches_archive": receipt["file_hashes"] == archived == receipt["source_snapshot_hashes"],
        "source_inputs": len(live),
        "saved_states_match_receipt": sum(states.values()),
        "saved_states_total": len(states),
        "manifest_hash": receipt["manifest_hash"],
        "receipt_sha256": {name: sha(EVIDENCE / name) for name in ("results.json", "instances.jsonl", "contracts.xml", "INTEGRITY.json", "acceptance_contracts.xml", "ACCEPTANCE.md", "HANDOFF.md", "REVIEW.md", "README.md")},
        "c0_acceptance_sha256": sha(ROOT / "evidence/c0_review/ACCEPTANCE.md"),
        "c0_acceptance_bound": receipt["c0_acceptance_sha256"] == sha(ROOT / "evidence/c0_review/ACCEPTANCE.md"),
    }


def position_signature(case):
    truth = case.truth
    edges = sorted((tuple(truth[e.source]), tuple(truth[e.target]), tuple(e.offset), e.weight) for e in case.updated.edges)
    added = Counter(case.updated.edges) - Counter(case.base.edges)
    (edge,) = list(added.elements())
    return digest({"nodes": sorted(tuple(truth[n]) for n in case.updated.nodes), "edges": edges,
                   "added": [tuple(truth[edge.source]), tuple(truth[edge.target]), tuple(edge.offset)]})


def check_seed_isomorphism():
    """Do R001 seeds, R002 seeds and an arbitrary seed generate different worlds?"""
    rows = []
    for size_id, nodes in enumerate(SIZES):
        for kind_id, kind in enumerate(KINDS):
            seeds = {"r001": 7000000 + 100 * size_id + kind_id, "r002": 8000000 + 100 * size_id + kind_id, "arbitrary": 123457 + kind_id}
            signatures = {name: position_signature(generate_case(nodes, kind, seed)) for name, seed in seeds.items()}
            rows.append({"nodes": nodes, "kind": kind, "identical_up_to_relabeling": len(set(signatures.values())) == 1})
    return {"cases": len(rows), "identical": sum(r["identical_up_to_relabeling"] for r in rows), "rows": rows}


def check_certificate_share():
    receipt = json.loads((EVIDENCE / "results.json").read_text())
    rows = []
    for row in receipt["instances"]:
        trace = row["candidate"]
        after = json.loads((EVIDENCE / "states" / f"{row['nodes']}_{row['kind']}_after.json").read_text())
        edges = len(after["edges"])
        rows.append({"nodes": row["nodes"], "kind": row["kind"], "status": trace["status"], "edges_after": edges,
                     "node_updates": trace["node_updates"], "certificate_passes": trace["certificate_passes"],
                     "certificate_share": trace["certificate_edge_visits"] / trace["dynamic_edge_visits"],
                     "touched_equals_all_edges": trace["touched_edges"] == edges,
                     "candidate_update_seconds": trace["total_update_seconds"], "candidate_dynamics_seconds": trace["dynamics_seconds"],
                     "fresh_sparse_ls_seconds": row["reference_seconds"], "fresh_compiled_seconds": row["compiled_seconds"],
                     "query_coverage_recorded": row["query_coverage"], "query_total_accuracy_recorded": row["query_total_accuracy"]})
    committed = [r for r in rows if r["status"] == "PASS"]
    return {"rows": rows,
            "committed_without_any_relaxation_step": sum(r["node_updates"] == 0 for r in committed),
            "committed": len(committed),
            "min_certificate_share_when_no_relaxation": min(r["certificate_share"] for r in committed if r["node_updates"] == 0),
            "committed_slower_than_fresh_sparse_ls": sum(r["candidate_update_seconds"] > r["fresh_sparse_ls_seconds"] for r in committed),
            "committed_slower_than_fresh_compiled": sum(r["candidate_update_seconds"] > r["fresh_compiled_seconds"] for r in committed)}


def check_unresolved_replay(budget):
    """Replay the three refused updates from the archived fork state with a larger diagnostic budget."""
    receipt = json.loads((EVIDENCE / "results.json").read_text())
    manifest_hash = receipt["manifest_hash"]
    rows = []
    for row in receipt["instances"]:
        if row["candidate"]["status"] == "PASS":
            continue
        case = generate_case(row["nodes"], row["kind"], row["seed"])
        saved, _ = save_initial_state(case.base, manifest_hash, Settings(**receipt["manifest"]["settings"]))
        archived = (EVIDENCE / "states" / f"{row['nodes']}_{row['kind']}_before.json").read_text().rstrip("\n")
        state = IncrementalGeometry.from_saved(archived)
        started = time.perf_counter()
        trace = state.update(case.updated, manifest_hash, budget)
        seconds = time.perf_counter() - started
        result = {"nodes": row["nodes"], "kind": row["kind"], "regenerated_before_matches_archive": saved == archived,
                  "diagnostic_budget": budget, "status": trace["status"], "dynamic_edge_visits": trace["dynamic_edge_visits"],
                  "local_edge_visits": trace["local_edge_visits"], "certificate_edge_visits": trace["certificate_edge_visits"],
                  "node_updates": trace["node_updates"], "node_pops": trace["node_pops"], "seconds": seconds}
        if trace["status"] == "PASS":
            reference = SparseLeastSquares(case.updated)
            errors = [float(np.linalg.norm(np.subtract(state.query(*p).displacement, reference.query(*p).displacement)))
                      for p in case.queries if reference.query(*p).status == "OK"]
            result["max_displacement_error_vs_sparse_ls"] = max(errors)
            result["reference_edge_visits"] = reference.edge_visits
        rows.append(result)
        print(f"  unresolved replay {row['nodes']}: {trace['status']} visits={trace['dynamic_edge_visits']} {seconds:.1f}s", flush=True)
    return rows


def check_r001_migration():
    """Explicit migration of every real archived R001 artifact (not a relabeled fixture)."""
    rows = Counter()
    failures = []
    answers_preserved = 0
    for path in sorted((ROOT / "evidence/c1/states").glob("*.json")):
        text = path.read_text().rstrip("\n")
        schema = json.loads(text)["schema"]
        try:
            migrated = IncrementalGeometry.from_saved(text)
        except ValueError as exc:
            rows[(schema, "REJECTED")] += 1
            failures.append({"file": path.name, "schema": schema, "reason": str(exc)[:160]})
            continue
        rows[(schema, "MIGRATED")] += 1
        original = (_C1V1State if schema == _C1V1State.schema else GeometryState).load(text)
        nodes = json.loads(text)["nodes"]
        sample = [(a, b) for a in nodes[:12] for b in nodes[-12:]]
        answers_preserved += all(original.query(*p) == migrated.query(*p) for p in sample)
    return {"counts": {f"{s}:{v}": n for (s, v), n in sorted(rows.items())}, "migrated_with_identical_answers": answers_preserved, "rejections": failures}


def random_world(rng, nodes, components):
    positions = {n: rng.normal(scale=3.0, size=2) for n in nodes}
    order = list(nodes)
    rng.shuffle(order)
    groups = [order[i::components] for i in range(components)]
    edges = []
    for group in groups:
        for i in range(1, len(group)):
            j = int(rng.integers(0, i))
            s, t = (group[j], group[i]) if rng.random() < 0.5 else (group[i], group[j])
            edges.append(Constraint(s, t, tuple(float(v) for v in positions[t] - positions[s]), float(rng.uniform(0.25, 3.0))))
    return positions, groups, edges


def compare(state, observation):
    reference = LeastSquares(observation)
    worst = 0.0
    for a in observation.nodes:
        for b in observation.nodes:
            actual, expected = state.query(a, b), reference.query(a, b)
            if actual.status != expected.status:
                return False, float("inf")
            if actual.status == "OK":
                worst = max(worst, float(np.linalg.norm(np.subtract(actual.displacement, expected.displacement))))
    record = json.loads(state.export())
    gauge = all(record["coordinates"][a] == [0.0, 0.0] for a in record["anchors"])
    return gauge and worst <= 1e-6, worst


def check_randomized_differential(trials, seed, budget):
    """Chained random updates: new nodes, bridges, reversed and duplicate edges, weights, contradictions."""
    rng = np.random.default_rng(seed)
    tally = Counter()
    worst = 0.0
    failures = []
    for trial in range(trials):
        count = int(rng.integers(3, 11))
        nodes = tuple(f"n{int(v):03d}" for v in rng.permutation(1000)[:count])
        positions, groups, edges = random_world(rng, nodes, int(rng.integers(1, 4)))
        base = Observation(tuple(sorted(nodes)), tuple(edges))
        saved, _ = save_initial_state(base, digest({"trial": trial}))
        state = IncrementalGeometry.from_saved(saved)
        for stage in range(int(rng.integers(1, 4))):
            old = state.observation()
            fresh = tuple(f"m{trial:03d}{stage}{k}" for k in range(int(rng.integers(0, 3))))
            for name in fresh:
                positions[name] = rng.normal(scale=3.0, size=2)
            universe = list(old.nodes) + list(fresh)
            added = []
            for _ in range(int(rng.integers(1, 5))):
                roll = rng.random()
                if roll < 0.15 and old.edges:
                    added.append(old.edges[int(rng.integers(0, len(old.edges)))])  # duplicate multiplicity
                    continue
                s, t = rng.choice(universe, 2, replace=False)
                noise = rng.normal(scale=0.5, size=2) if roll > 0.6 else np.zeros(2)
                added.append(Constraint(str(s), str(t), tuple(float(v) for v in positions[t] - positions[s] + noise), float(rng.uniform(0.25, 3.0))))
            for name in fresh:  # most new nodes attach; some stay isolated
                if rng.random() < 0.8:
                    other = str(rng.choice(old.nodes))
                    added.append(Constraint(other, name, tuple(float(v) for v in positions[name] - positions[other]), 1.0))
            updated = Observation(tuple(sorted(old.nodes + fresh)), old.edges + tuple(added))
            before = state.export()
            trace = state.update(updated, digest({"trial": trial, "stage": stage}), budget)
            tally[trace["status"]] += 1
            if trace["status"] == "PASS":
                ok, error = compare(state, updated)
                worst = max(worst, error)
                if not ok or IncrementalGeometry.load(state.export()).export() != state.export():
                    tally["WRONG_COMMIT"] += 1
                    failures.append({"trial": trial, "stage": stage, "error": error})
                state.freeze()
                state = IncrementalGeometry.from_saved(state.export())
            else:
                if state.export() != before or not trace["snapshot_retained"]:
                    tally["ROLLBACK_BROKEN"] += 1
                    failures.append({"trial": trial, "stage": stage, "status": trace["status"], "reason": trace["reason"]})
                break
    return {"trials": trials, "seed": seed, "budget": budget, "outcomes": dict(tally), "max_committed_error": worst, "failures": failures[:20]}


def check_probes():
    """Targeted behaviors: no-op cost, isolated node, tiny weights, stale answers after refusal."""
    out = {}
    case = generate_case(512, "consistent_edge", 8000200)
    saved, _ = save_initial_state(case.base, digest({"probe": 1}))
    state = IncrementalGeometry.from_saved(saved)
    trace = state.update(case.base, digest({"probe": 1}))
    out["noop_update_512"] = {"status": trace["status"], "edges": len(case.base.edges), "dynamic_edge_visits": trace["dynamic_edge_visits"], "certificate_passes": trace["certificate_passes"]}

    base = Observation(("a", "b"), (Constraint("a", "b", (1.0, 0.0)),))
    saved, _ = save_initial_state(base, digest({"probe": 2}))
    state = IncrementalGeometry.from_saved(saved)
    trace = state.update(Observation(("a", "b", "c"), base.edges), digest({"probe": 2}))
    out["isolated_new_node"] = {"status": trace["status"], "query": state.query("a", "c").status}

    tiny = Observation(("a", "b"), (Constraint("a", "b", (1.0, 0.0), 1e-6),))
    saved, _ = save_initial_state(tiny, digest({"probe": 3}))
    state = IncrementalGeometry.from_saved(saved)
    updated = replace(tiny, edges=tiny.edges + (Constraint("a", "b", (2.0, 0.0), 1e-6),))
    trace = state.update(updated, digest({"probe": 3}), 2_000_000)
    out["tiny_weight_contradiction"] = {"status": trace["status"], "dynamic_edge_visits": trace["dynamic_edge_visits"],
                                        "reference_status": SparseLeastSquares(updated).status}

    case = generate_case(128, "inconsistent_edge", 8000101)
    saved, _ = save_initial_state(case.base, digest({"probe": 4}))
    state = IncrementalGeometry.from_saved(saved)
    trace = state.update(case.updated, digest({"probe": 4}))
    reference = SparseLeastSquares(case.updated)
    stale = [p for p in case.queries if state.query(*p).status == "OK" and reference.query(*p).status == "OK"
             and np.linalg.norm(np.subtract(state.query(*p).displacement, reference.query(*p).displacement)) > 1e-5]
    out["post_refusal_queries"] = {"update_status": trace["status"],
                                   "answers_status_ok": sum(state.query(*p).status == "OK" for p in case.queries),
                                   "ok_answers_wrong_for_new_observation": len(stale),
                                   "state_exposes_refusal": state.query(*case.queries[0]).status != "OK"}
    return out


def main():
    started = time.perf_counter()
    report = {"identity": check_identity()}
    print("identity done", flush=True)
    report["seed_isomorphism"] = check_seed_isomorphism()
    report["certificate_and_cost"] = check_certificate_share()
    report["r001_migration"] = check_r001_migration()
    print("migration done", flush=True)
    report["probes"] = check_probes()
    print("probes done", flush=True)
    report["randomized_differential"] = check_randomized_differential(300, 20261001, 2_000_000)
    print("randomized done", flush=True)
    report["unresolved_replay"] = check_unresolved_replay(20_000_000)
    report["environment"] = {"python": sys.version.split()[0], "numpy": np.__version__}
    report["total_seconds"] = time.perf_counter() - started
    target = HERE / "focused_checks.json"
    if target.exists():
        raise FileExistsError("focused_checks.json exists; do not overwrite reviewer evidence")
    target.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("certificate_and_cost", "seed_isomorphism")}, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()
