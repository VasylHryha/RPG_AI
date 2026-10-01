"""Execute the registered C1 panel: a queue-only arm and a metered fallback arm.

Every case starts from a certified saved C0 state. The evaluator derives the
additive public delta, fixes both arms' answers, then builds fresh independent
references. Registered endpoints decide the H-L verdicts after the panel.
"""

import argparse
import ast
from collections import Counter
from dataclasses import asdict
import gzip
import hashlib
import json
from pathlib import Path
import platform
import re
import shlex
import shutil
from statistics import median
import sys
from time import perf_counter
import xml.etree.ElementTree as ET

import numpy as np

from .c1_cases import GENERATOR, KINDS, generate_case, save_initial_state
from .c1_reference import SparseLeastSquares
from .geometry import Answer, GeometryState, Settings, digest, finite_number
from .incremental import TRACE_COUNTERS, IncrementalGeometry
from .references import CompiledCoordinates
from .run_c0 import ROOT, contract_result, snapshot_source, source_hashes

CONTRACT_SCOPE = "geomind.c1.contracts.v4"
ARMS = ("queue", "fallback")
ENDPOINT_KEYS = {"locality_kinds", "locality_max_ratio", "speed_kinds", "contradiction_min_nodes", "contradiction_not_supported_below"}


def checked_query(state, pair):
    """Malformed/nonfinite answers are retained as typed evaluation failures."""
    answer = state.query(*pair)
    if not isinstance(answer, Answer) or not isinstance(answer.status, str) or answer.status not in {"OK", "UNKNOWN", "UNIDENTIFIABLE", "NOT_CONVERGED", "INVALID_STATE"}:
        return Answer("INVALID_STATE")
    if answer.status == "OK":
        if not isinstance(answer.displacement, tuple) or len(answer.displacement) != 2 or not all(finite_number(v) for v in answer.displacement):
            return Answer("INVALID_STATE")
    elif answer.displacement is not None:
        return Answer("INVALID_STATE")
    return answer


def displacement_error(a, b):
    if a.status != "OK" or b.status != "OK":
        return None
    with np.errstate(over="ignore", invalid="ignore"):
        error = float(np.linalg.norm(np.asarray(a.displacement) - b.displacement))
    return error if finite_number(error) else None


def check_contract_report(path, hashes):
    contracts = contract_result(path)
    properties = {p.attrib["name"]: p.attrib["value"] for p in ET.parse(path).getroot().iter("property")}
    expected_names = {n.name for n in ast.parse((ROOT / "tests/test_c1.py").read_text()).body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")}
    cases = list(ET.parse(path).getroot().iter("testcase"))
    complete = len(cases) == len(expected_names) and {c.attrib.get("name") for c in cases} == expected_names and all(c.attrib.get("classname", "").endswith("test_c1") for c in cases)
    if contracts["status"] != "PASS" or not complete or properties.get("c1_contract_scope") != CONTRACT_SCOPE or json.loads(properties.get("c1_file_hashes", "null")) != hashes:
        raise ValueError("C1 checks must pass for this exact source and registered manifest; stale/unrelated report")
    return contracts


def check_c0_acceptance(root=ROOT):
    """Bind the human acceptance verdict to its reviewed machine receipt."""
    folder = root / "evidence/c0_review"
    acceptance = folder / "ACCEPTANCE.md"
    text = acceptance.read_text()
    if not re.search(r"^Verdict: \*\*ACCEPTED\*\*\.", text, re.MULTILINE):
        raise ValueError("Explicit independent C0 acceptance required")
    match = re.search(r"Original `results.json` SHA256 at review: `([0-9a-f]{64})`", text)
    result_bytes = (folder / "results.json").read_bytes()
    if match is None or hashlib.sha256(result_bytes).hexdigest() != match[1]:
        raise ValueError("C0 result identity differs from independent acceptance")
    receipt = json.loads(result_bytes)
    for name, expected in receipt["file_hashes"].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Accepted C0 input changed: {name}")
    return hashlib.sha256(acceptance.read_bytes()).hexdigest()


def check_output_directory(output, contract_report):
    if output.exists() and any(p.resolve() != contract_report.resolve() for p in output.iterdir()):
        raise FileExistsError("C1 output contains prior evidence; choose a fresh directory")


def validate_manifest(manifest):
    if not isinstance(manifest, dict) or not isinstance(manifest.get("experiment_id"), str) or re.fullmatch(r"geomind-c1-r4-\d{3}", manifest["experiment_id"]) is None:
        raise ValueError("Registered C1 experiment identity required")
    if manifest.get("schema") != "geomind.c1.experiment.v2" or manifest.get("generator") != GENERATOR or manifest.get("algorithm") != IncrementalGeometry.algorithm:
        raise ValueError("Unknown C1 experiment version")
    if manifest.get("sizes") != [32, 128, 512, 2048] or manifest.get("interventions") != list(KINDS):
        raise ValueError("Complete registered C1 size/intervention panel required")
    if type(manifest.get("edge_visit_budget")) is not int or manifest["edge_visit_budget"] != 100000:
        raise ValueError("C1 dynamic operation budget must be 100000")
    if type(manifest.get("fallback_budget")) is not int or manifest["fallback_budget"] < 1:
        raise ValueError("Positive integer fallback-arm budget required")
    if type(manifest.get("seed_start")) is not int or manifest["seed_start"] < 0:
        raise ValueError("Nonnegative case seed required")
    if type(manifest.get("replicates")) is not int or not 2 <= manifest["replicates"] <= 10:
        raise ValueError("Between two and ten independent worlds per size/intervention required")
    for name, maximum in (("displacement_tolerance", 1e-5), ("energy_tolerance", 1e-8), ("reference_tolerance", 1e-11)):
        if not finite_number(manifest.get(name)) or not 0 < manifest[name] <= maximum:
            raise ValueError("Invalid C1 tolerance")
    if type(manifest.get("reference_max_iterations")) is not int or manifest["reference_max_iterations"] < 1:
        raise ValueError("Invalid reference iteration budget")
    endpoints = manifest.get("endpoints")
    if not isinstance(endpoints, dict) or set(endpoints) != ENDPOINT_KEYS or not set(endpoints["locality_kinds"]) <= set(KINDS) or not set(endpoints["speed_kinds"]) <= set(KINDS):
        raise ValueError("Registered endpoints required before execution")
    Settings(**manifest["settings"]).validate()
    return manifest


def case_delta(case):
    """Evaluator-side delta: exactly the public records this intervention adds."""
    added_edges = tuple((Counter(case.updated.edges) - Counter(case.base.edges)).elements())
    added_nodes = tuple(sorted(set(case.updated.nodes) - set(case.base.nodes)))
    known = dict(case.base.relations)
    return added_nodes, added_edges, tuple(r for r in case.updated.relations if r[0] not in known)


def write_state(output, name, encoded):
    """Deterministic gzip; receipts hash the uncompressed canonical text."""
    with open(output / "states" / f"{name}.json.gz", "wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as stream:
            stream.write((encoded + "\n").encode())


def run_arm(saved, delta, case, manifest, manifest_hash, fallback_budget, queries):
    started = perf_counter()
    state = IncrementalGeometry.from_saved(saved)
    load_seconds = perf_counter() - started
    before = state.export()
    trace = state.apply(*delta, manifest_hash, manifest["edge_visit_budget"], fallback_budget)
    committed = trace["status"] == "PASS"
    export_started = perf_counter()
    after = state.export()
    export_seconds = perf_counter() - export_started
    query_started = perf_counter()
    actual = [checked_query(state, pair) for pair in queries]
    query_seconds = perf_counter() - query_started
    query_immutable = state.export() == after
    retention = [checked_query(state, pair) for pair in case.retention_queries]
    reload_started = perf_counter()
    loaded = IncrementalGeometry.load(after)
    reload_equal = all(checked_query(loaded, pair) == answer for pair, answer in zip(queries, actual))
    reload_seconds = perf_counter() - reload_started
    edge_answers = [checked_query(state, (e.source, e.target)) for e in case.updated.edges] if committed else []
    return {"trace": trace, "committed": committed, "before": before, "after": after, "actual": actual, "retention": retention,
            "edge_answers": edge_answers, "query_immutable": query_immutable, "reload_equal": reload_equal,
            "load_seconds": load_seconds, "export_seconds": export_seconds, "query_seconds": query_seconds, "reload_seconds": reload_seconds}


def grade_arm(name, arm, case, manifest, expected, ls, expected_retention, fresh_seconds):
    trace, committed = arm["trace"], arm["committed"]
    tolerance = manifest["displacement_tolerance"]
    statuses_equal, errors = ls.status == "PASS", []
    if statuses_equal:
        for a, b in zip(arm["actual"], expected):
            statuses_equal &= a.status == b.status
            if a.status == b.status == "OK":
                error = displacement_error(a, b)
                if error is None:
                    statuses_equal = False
                else:
                    errors.append(error)
    observed_energy = None
    if committed and all(a.status == "OK" for a in arm["edge_answers"]):
        with np.errstate(over="ignore", invalid="ignore"):
            observed_energy = float(sum(0.5 * e.weight * float(np.sum((np.asarray(a.displacement) - e.offset) ** 2)) for e, a in zip(case.updated.edges, arm["edge_answers"])))
        observed_energy = observed_energy if finite_number(observed_energy) else None
    energy_gap = abs(observed_energy - ls.energy) if observed_energy is not None else None
    expected_ok = sum(b.status == "OK" for b in expected)
    correct_commit = bool(committed and statuses_equal and len(errors) == expected_ok and expected_ok > 0 and all(e <= tolerance for e in errors)
                          and finite_number(energy_gap) and energy_gap <= manifest["energy_tolerance"])
    counters = [trace.get(key) for key in TRACE_COUNTERS]
    budget = manifest["edge_visit_budget"]
    fallback_budget = manifest["fallback_budget"] if name == "fallback" else 0
    metered = (all(type(v) is int and v >= 0 for v in counters) and sum(counters) == trace["charged_operations"] <= budget
               and type(trace["fallback_operations"]) is int and 0 <= trace["fallback_operations"] <= fallback_budget)
    queue_proof = type(trace["budget_exhaustion_required"]) is int and trace["budget_exhaustion_required"] > 0 and trace["charged_operations"] + trace["budget_exhaustion_required"] > budget
    fallback_proof = type(trace["fallback_exhaustion_required"]) is int and trace["fallback_exhaustion_required"] > 0 and trace["fallback_operations"] + trace["fallback_exhaustion_required"] > fallback_budget
    # The fallback arm can refuse only after its own cap, or before dynamics start.
    exhaustion_proven = queue_proof if name == "queue" else ((fallback_proof and trace["queue_exhausted"]) or (queue_proof and not trace["queue_exhausted"]))
    explicit_rejection = trace["status"] == "NOT_CONVERGED" and arm["before"] == arm["after"] and exhaustion_proven
    fallback_consistent = trace["fallbacks"] == 0 if name == "queue" else trace["fallbacks"] == int(trace["queue_exhausted"])
    retained = arm["retention"] == expected_retention
    passed = (ls.status == "PASS" and (correct_commit or explicit_rejection) and retained and arm["query_immutable"]
              and arm["reload_equal"] and metered and fallback_consistent)
    identifiable = [b.status == "OK" for b in expected]
    correct = [i and a.status == "OK" and finite_number(displacement_error(a, b)) and displacement_error(a, b) <= tolerance
               for i, a, b in zip(identifiable, arm["actual"], expected)]
    prior_ok = [(a, b) for a, b in zip(arm["actual"], expected) if not committed and a.status == "OK" and b.status == "OK"]
    return {"check_status": "PASS" if passed else "ASSERTION_FAILURE", "candidate": trace, "committed": committed,
            "correct_commit": correct_commit, "explicit_rejection": bool(explicit_rejection), "retention_pass": retained,
            "query_immutable": arm["query_immutable"], "reload_equal": arm["reload_equal"], "metered": metered,
            "least_squares_displacement_error_max": max(errors) if errors and committed else None,
            "observed_energy": observed_energy, "reference_energy": ls.energy, "energy_gap": energy_gap,
            "update_coverage": sum(a.status == "OK" and i for a, i in zip(arm["actual"], identifiable)) / sum(identifiable) if committed and any(identifiable) else None,
            "update_total_accuracy": sum(correct) / sum(identifiable) if committed and any(identifiable) else None,
            "post_transaction_total_accuracy": sum(correct) / sum(identifiable) if any(identifiable) else None,
            "prior_state_ok_answers": None if committed else len(prior_ok),
            "prior_state_answers_wrong_for_update": None if committed else sum(not finite_number(displacement_error(a, b)) or displacement_error(a, b) > tolerance for a, b in prior_ok),
            "cross_abstention_correct": sum(b.status == a.status == "UNIDENTIFIABLE" for a, b in zip(arm["actual"], expected)),
            "apply_seconds": trace["total_seconds"], "update_to_fresh_recompute_ratio": trace["total_seconds"] / fresh_seconds if committed and fresh_seconds > 0 else None,
            "load_seconds": arm["load_seconds"], "export_seconds": arm["export_seconds"], "query_seconds": arm["query_seconds"], "reload_seconds": arm["reload_seconds"],
            "after_artifact_hash": hashlib.sha256(arm["after"].encode()).hexdigest(), "fork_before_artifact_hash": hashlib.sha256(arm["before"].encode()).hexdigest(),
            "serialized_bytes": len(arm["after"].encode()), "answers": [asdict(a) for a in arm["actual"]]}


def evaluate_case(case, manifest, output, identity):
    started = perf_counter()
    manifest_hash = digest(manifest)
    saved, setup = save_initial_state(case.base, manifest_hash, Settings(**manifest["settings"]))
    label = f"{identity['nodes']}_{identity['kind']}" + (f"_w{identity['replicate']}" if "replicate" in identity else "")
    write_state(output, f"{label}_before", saved)
    old = GeometryState.load(saved)
    queries = case.queries + case.affected_queries
    frozen = [checked_query(old, pair) for pair in queries]
    expected_retention = [checked_query(old, pair) for pair in case.retention_queries]
    delta = case_delta(case)
    arms = {"queue": run_arm(saved, delta, case, manifest, manifest_hash, 0, queries),
            "fallback": run_arm(saved, delta, case, manifest, manifest_hash, manifest["fallback_budget"], queries)}
    # Both arms' answers are fixed before the fresh references exist.
    ls = SparseLeastSquares(case.updated, manifest["reference_tolerance"], manifest["reference_max_iterations"])
    compiled = CompiledCoordinates(case.updated)
    expected = [ls.query(*pair) for pair in queries]
    compiled_answers = [compiled.query(*pair) for pair in queries]
    compiled_valid = compiled.residual_max <= 1e-10
    fresh_seconds = min(ls.build_seconds, compiled.build_seconds) if compiled_valid else ls.build_seconds
    graded = {name: grade_arm(name, arm, case, manifest, expected, ls, expected_retention, fresh_seconds) for name, arm in arms.items()}
    for name, arm in arms.items():
        if arm["committed"] and (name == "queue" or arm["after"] != arms["queue"]["after"]):
            write_state(output, f"{label}_{name}_after", arm["after"])
    # Without a fallback the two arms are the same deterministic transaction.
    arms_agree = arms["fallback"]["trace"]["fallbacks"] == 1 or arms["fallback"]["after"] == arms["queue"]["after"]
    tolerance = manifest["displacement_tolerance"]
    identifiable = [b.status == "OK" for b in expected]
    frozen_correct = sum(i and a.status == "OK" and finite_number(displacement_error(a, b)) and displacement_error(a, b) <= tolerance for i, a, b in zip(identifiable, frozen, expected))
    passed = all(g["check_status"] == "PASS" for g in graded.values()) and arms_agree and old.export() == saved
    for g in graded.values():
        g.pop("answers")
    panel = [{"pair": pair, "frozen": asdict(f), "queue": asdict(q), "fallback": asdict(b2), "reference": asdict(r), "compiled": asdict(c)}
             for pair, f, q, b2, r, c in zip(queries, frozen, arms["queue"]["actual"], arms["fallback"]["actual"], expected, compiled_answers)]
    smaller_component = len(case.base.nodes) // 4  # generator: components of n/2, n/4 and n/4
    return dict(identity, check_status="PASS" if passed else "ASSERTION_FAILURE", arms=graded, arms_agree=arms_agree, setup=setup,
                frozen_total_accuracy=frozen_correct / sum(identifiable) if any(identifiable) else None,
                identifiable_queries=sum(identifiable), queries=len(queries), retention_queries=len(case.retention_queries),
                affected_queries=len(case.affected_queries), excluded_cross_queries=sum(r.status == "UNIDENTIFIABLE" for r in expected),
                reference_status=ls.status, reference_iterations=ls.iterations, reference_edge_visits=ls.edge_visits,
                reference_seconds=ls.build_seconds, compiled_seconds=compiled.build_seconds, compiled_residual_max=compiled.residual_max,
                compiled_valid=compiled_valid, fresh_recompute_seconds=fresh_seconds, bridge_smaller_component=smaller_component if identity["kind"] == "bridge" else None,
                compiled_displacement_error_max=max((displacement_error(c, r) for c, r in zip(compiled_answers, expected) if displacement_error(c, r) is not None), default=None),
                source_observation_hash=digest(asdict(case.base)), update_observation_hash=digest(asdict(case.updated)),
                old_artifact_hash=hashlib.sha256(saved.encode()).hexdigest(), query_panel=panel, total_seconds=perf_counter() - started)


def evaluate_endpoints(records, manifest):
    """Apply the endpoints registered in the manifest before execution."""
    e = manifest["endpoints"]
    small, large = min(manifest["sizes"]), max(manifest["sizes"])
    valid = [r for r in records if r["check_status"] == "PASS"]

    def cell(kind, nodes):
        return [r for r in valid if r["kind"] == kind and r["nodes"] == nodes]

    complete = len(valid) == len(records)
    locality = {}
    for kind in e["locality_kinds"]:
        a, b = cell(kind, small), cell(kind, large)
        committed = len(a) == len(b) == manifest["replicates"] and all(r["arms"]["queue"]["committed"] for r in a + b)
        ops_a = [r["arms"]["queue"]["candidate"]["charged_operations"] for r in a]
        ops_b = [r["arms"]["queue"]["candidate"]["charged_operations"] for r in b]
        ratio = median(ops_b) / median(ops_a) if committed else None
        locality[kind] = {"median_operations_small": median(ops_a) if ops_a else None, "median_operations_large": median(ops_b) if ops_b else None,
                          "ratio": ratio, "pass": bool(complete and committed and ratio <= e["locality_max_ratio"])}
    speed = {}
    for kind in e["speed_kinds"]:
        rows = cell(kind, large)
        ratios = [r["arms"]["queue"]["update_to_fresh_recompute_ratio"] for r in rows]
        speed[kind] = {"ratios": ratios, "pass": bool(complete and len(rows) == manifest["replicates"] and all(x is not None and x < 1 for x in ratios))}
    hard = [r for r in valid if r["kind"] == "inconsistent_edge" and r["nodes"] >= e["contradiction_min_nodes"]]
    queue_rate = sum(r["arms"]["queue"]["committed"] for r in hard) / len(hard) if hard else None
    fallback_rows = [r for r in hard if r["arms"]["fallback"]["committed"]]
    contradiction = {"cases": len(hard), "queue_resolution_rate": queue_rate,
                     "fallback_arm_resolution_rate": len(fallback_rows) / len(hard) if hard else None,
                     "median_fallback_operations": median(r["arms"]["fallback"]["candidate"]["fallback_operations"] for r in fallback_rows) if fallback_rows else None,
                     "median_fresh_reference_edge_visits": median(r["reference_edge_visits"] for r in hard) if hard else None}
    additive = all(v["pass"] for v in locality.values()) and all(v["pass"] for v in speed.values())
    if queue_rate is None:
        local_queue = "NOT_TESTED"
    elif queue_rate < e["contradiction_not_supported_below"]:
        local_queue = "NOT_SUPPORTED"
    elif queue_rate == 1:
        local_queue = "SUPPORTED_WITHIN_SCOPE"
    else:
        local_queue = "INCONCLUSIVE"
    verdicts = {"consistent_additive_in_memory_updates": "SUPPORTED_WITHIN_SCOPE" if additive else "NOT_SUPPORTED",
                "contradiction_resolution_by_local_queue": local_queue,
                "durable_persistence": "NOT_TESTED: export/load are O(V+E) by design and reported separately"}
    return {"locality": locality, "speed": speed, "contradiction": contradiction}, verdicts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "experiments/c1_manifest.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--contract-report", type=Path, required=True)
    args = parser.parse_args()
    manifest = validate_manifest(json.loads(args.manifest.read_text()))
    acceptance_hash = check_c0_acceptance()
    hashes = source_hashes(args.manifest.resolve())
    contracts = check_contract_report(args.contract_report, hashes)
    check_output_directory(args.output, args.contract_report)
    (args.output / "states").mkdir(parents=True, exist_ok=True)
    report_copy = args.output / "contracts.xml"
    if report_copy.resolve() != args.contract_report.resolve():
        shutil.copyfile(args.contract_report, report_copy)
    if hashlib.sha256(report_copy.read_bytes()).hexdigest() != contracts["report_sha256"]:
        raise ValueError("Contract report changed during capture")
    snapshots = snapshot_source(hashes, args.output)
    records = []
    started = perf_counter()
    cells = [(size_id, nodes, replicate, kind_id, kind) for size_id, nodes in enumerate(manifest["sizes"])
             for replicate in range(manifest["replicates"]) for kind_id, kind in enumerate(KINDS)]
    with (args.output / "instances.jsonl").open("x") as stream:
        for size_id, nodes, replicate, kind_id, kind in cells:
            seed = manifest["seed_start"] + 1000 * size_id + 10 * replicate + kind_id
            identity = {"nodes": nodes, "kind": kind, "replicate": replicate, "seed": seed}
            case_started = perf_counter()
            try:
                case = generate_case(nodes, kind, seed)
                generation_seconds = perf_counter() - case_started
                row = evaluate_case(case, manifest, args.output, identity)
                row.update(generation_seconds=generation_seconds)
            except Exception as exc:
                row = dict(identity, check_status="INFRASTRUCTURE_FAILURE", error_type=type(exc).__name__, error=str(exc))
            try:
                encoded = json.dumps(row, allow_nan=False)
            except (ValueError, TypeError) as exc:
                row = dict(identity, check_status="INFRASTRUCTURE_FAILURE", error_type=type(exc).__name__, error=f"Nonserializable case evidence: {exc}")
                encoded = json.dumps(row, allow_nan=False)
            stream.write(encoded + "\n")
            stream.flush()
            records.append(row)
            arms = row.get("arms", {})
            print(f"{nodes}/{kind}/w{replicate}: {row['check_status']} queue={arms.get('queue', {}).get('candidate', {}).get('status', row.get('error'))} fallback={arms.get('fallback', {}).get('candidate', {}).get('status')}", flush=True)
    expected_cases = len(cells)
    valid = [r for r in records if r["check_status"] == "PASS"]
    gates = {"contracts": contracts["status"] == "PASS", "complete_panel": len(records) == expected_cases,
             "correct_or_explicitly_unresolved": len(valid) == expected_cases, "source_stable": hashes == source_hashes(args.manifest.resolve()),
             "contracts_stable": contracts["report_sha256"] == hashlib.sha256(args.contract_report.read_bytes()).hexdigest(),
             "c0_acceptance_stable": acceptance_hash == check_c0_acceptance()}
    endpoints, hl = evaluate_endpoints(records, manifest)

    def count(arm, predicate):
        return sum(predicate(r["arms"][arm]) for r in valid)

    summary = {arm: {"committed": count(arm, lambda g: g["committed"]), "explicitly_unresolved": count(arm, lambda g: not g["committed"]),
                     "committed_without_relaxation_step": count(arm, lambda g: g["committed"] and g["candidate"]["node_updates"] == 0),
                     "fallback_used": count(arm, lambda g: g["candidate"]["fallbacks"] == 1),
                     "committed_faster_than_fresh_recompute": count(arm, lambda g: g["update_to_fresh_recompute_ratio"] is not None and g["update_to_fresh_recompute_ratio"] < 1),
                     "unresolved_by_kind": {kind: sum(r["kind"] == kind and not r["arms"][arm]["committed"] for r in valid) for kind in KINDS},
                     "max_committed_displacement_error": max((r["arms"][arm]["least_squares_displacement_error_max"] for r in valid if r["arms"][arm]["committed"]), default=None),
                     "max_committed_energy_gap": max((r["arms"][arm]["energy_gap"] for r in valid if r["arms"][arm]["committed"]), default=None)} for arm in ARMS}
    def spread(values):
        values = [v for v in values if v is not None]
        return {"min": min(values), "median": median(values), "max": max(values)} if values else None

    # Per-cell spread across independent worlds (R4 section 7 aggregate uncertainty).
    cells_summary = {}
    for kind in KINDS:
        for nodes in manifest["sizes"]:
            rows = [r for r in valid if r["kind"] == kind and r["nodes"] == nodes]
            cells_summary[f"{kind}/{nodes}"] = {
                "worlds": len(rows), "queue_committed": sum(r["arms"]["queue"]["committed"] for r in rows),
                "fallback_committed": sum(r["arms"]["fallback"]["committed"] for r in rows),
                "queue_operations": spread([r["arms"]["queue"]["candidate"]["charged_operations"] for r in rows]),
                "queue_apply_seconds": spread([r["arms"]["queue"]["apply_seconds"] for r in rows]),
                "fallback_operations": spread([r["arms"]["fallback"]["candidate"]["fallback_operations"] for r in rows]),
                "fallback_apply_seconds": spread([r["arms"]["fallback"]["apply_seconds"] for r in rows]),
                "translated_nodes": spread([r["arms"]["queue"]["candidate"]["translated_nodes"] for r in rows]),
                "fresh_recompute_seconds": spread([r["fresh_recompute_seconds"] for r in rows]),
                "reference_edge_visits": spread([r["reference_edge_visits"] for r in rows]),
                "export_seconds": spread([r["arms"]["queue"]["export_seconds"] for r in rows]),
                "load_seconds": spread([r["arms"]["queue"]["load_seconds"] for r in rows]),
                "frozen_total_accuracy": spread([r["frozen_total_accuracy"] for r in rows]),
                "max_committed_error": max([r["arms"][a]["least_squares_displacement_error_max"] for r in rows for a in ARMS if r["arms"][a]["committed"]], default=None)}
    adaptive = [(r["frozen_total_accuracy"], r["arms"]["queue"]["post_transaction_total_accuracy"], r["arms"]["fallback"]["post_transaction_total_accuracy"]) for r in valid]
    receipt = {
        "experiment_id": manifest["experiment_id"], "manifest": manifest, "manifest_hash": digest(manifest),
        "c0_acceptance_sha256": acceptance_hash,
        "command": shlex.join([sys.executable, "-m", "geomind.run_c1"] + sys.argv[1:]),
        "environment": {"python": sys.version, "numpy": np.__version__, "platform": platform.platform()},
        "source_commit": None, "file_hashes": hashes, "source_snapshot_hashes": snapshots,
        "contracts": contracts, "gates": gates, "check_status": "PASS" if all(gates.values()) else "ASSERTION_FAILURE",
        "implementation_status": "REVIEW_READY" if all(gates.values()) else "ACTIVE",
        "summary": summary, "cells": cells_summary, "endpoints": endpoints,
        "hypotheses": {"H-L": hl, "H-P": "INCONCLUSIVE"},
        "hypothesis_limits": ("H-L verdicts follow the registered endpoints within this generator family and in-memory transactions; export/load are global and reported separately. "
                              "The speed endpoint compares with a fresh full recompute, not with an equally incremental compiled baseline, so no superiority over compiled methods is claimed. "
                              "H-P: the frozen-versus-adaptive comparison is reported, but a store that includes new constraints answers them by construction; no task learning or transfer is tested."),
        "frozen_vs_adaptive": {"median_frozen_total_accuracy": median(a for a, _, _ in adaptive) if adaptive else None,
                               "median_queue_arm_accuracy": median(b for _, b, _ in adaptive) if adaptive else None,
                               "median_fallback_arm_accuracy": median(c for _, _, c in adaptive) if adaptive else None},
        "checks_not_run": ["independent C1 acceptance", "C2-C8", "C++/browser integration", "hardware energy", "incremental compiled baseline"],
        "total_seconds": perf_counter() - started, "instances": records,
        "next_action": "Independent C1 review of R004 before C2",
    }
    (args.output / "results.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    q, f = summary["queue"], summary["fallback"]
    lines = ["# C1 incremental-update receipt", "", f"`{manifest['experiment_id']}`. Implementation: **{receipt['implementation_status']}**. Checks: **{receipt['check_status']}**. Elapsed: {receipt['total_seconds']:.2f}s.", "",
             f"{expected_cases} registered interventions, each run in two arms from the same saved state. Queue arm: {q['committed']} committed ({q['committed_without_relaxation_step']} without a relaxation step), {q['explicitly_unresolved']} explicitly unresolved and rolled back. Fallback arm: {f['committed']} committed, {f['fallback_used']} through the metered full solve, {f['explicitly_unresolved']} unresolved.", "",
             "H-L (registered endpoints): " + "; ".join(f"{k}: **{v}**" for k, v in hl.items()) + ". H-P: **INCONCLUSIVE**.", "",
             "[Results](results.json), [per-case stream](instances.jsonl), [contracts](contracts.xml); gzip-compressed canonical states in `states/` (receipts hash the uncompressed text) and source in `source/`.", "",
             "| Nodes | Intervention | World | Queue arm | Queue operations | Fallback arm | Fallback operations | In-memory update / fresh recompute | Max error |", "|---:|---|---:|---|---:|---|---:|---:|---:|"]
    for row in records:
        arms = row.get("arms")
        if not arms:
            lines.append(f"| {row['nodes']} | {row['kind']} | {row['replicate']} | {row['check_status']} | | | | | |")
            continue
        qa, fa = arms["queue"], arms["fallback"]
        ratio = qa["update_to_fresh_recompute_ratio"]
        error = qa["least_squares_displacement_error_max"] if qa["committed"] else fa["least_squares_displacement_error_max"]
        lines.append(f"| {row['nodes']} | {row['kind']} | {row['replicate']} | {qa['candidate']['status']} | {qa['candidate']['charged_operations']} | {fa['candidate']['status']}{' (fallback)' if fa['candidate']['fallbacks'] else ''} | {fa['candidate']['fallback_operations']} | {f'{ratio:.4f}' if ratio is not None else 'n/a'} | {error if error is not None else 'n/a'} |")
    lines.extend(["", "Unresolved updates keep the preceding snapshot byte-identically; their prior-state answers are counted separately, never as coverage. Fallback commits are reported as a distinct arm, not as local queue successes. Every committed answer is compared with a fresh independent sparse least-squares reference built after both arms answered; compiled coordinates are also measured. Persistence (export/load) and reference costs are reported separately from the in-memory update."])
    (args.output / "README.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"gates": gates, "summary": {k: {kk: v for kk, v in s.items() if kk != "unresolved_by_kind"} for k, s in summary.items()}, "hypotheses": receipt["hypotheses"], "seconds": receipt["total_seconds"]}, indent=2))
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
