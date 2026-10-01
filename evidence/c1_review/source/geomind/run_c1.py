"""Execute the 16 frozen C1 interventions and preserve accepted or rejected results."""

import argparse
import ast
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import re
import shlex
import shutil
import sys
from time import perf_counter
import xml.etree.ElementTree as ET

import numpy as np

from .c1_cases import GENERATOR, KINDS, generate_case, save_initial_state
from .c1_reference import SparseLeastSquares
from .geometry import Answer, GeometryState, Settings, digest, finite_number
from .incremental import IncrementalGeometry
from .references import CompiledCoordinates
from .run_c0 import ROOT, contract_result, snapshot_source, source_hashes

CONTRACT_SCOPE = "geomind.c1.contracts.v2"


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
    if manifest.get("schema") != "geomind.c1.experiment.v1" or manifest.get("generator") != GENERATOR or manifest.get("algorithm") != IncrementalGeometry.algorithm:
        raise ValueError("Unknown C1 experiment version")
    if manifest.get("sizes") != [32, 128, 512, 2048] or manifest.get("interventions") != list(KINDS):
        raise ValueError("Complete registered C1 size/intervention panel required")
    if type(manifest.get("edge_visit_budget")) is not int or manifest["edge_visit_budget"] != 100000:
        raise ValueError("C1 dynamic edge budget must be 100000")
    if type(manifest.get("seed_start")) is not int or manifest["seed_start"] < 0:
        raise ValueError("Nonnegative case seed required")
    for name, maximum in (("displacement_tolerance", 1e-5), ("energy_tolerance", 1e-8), ("reference_tolerance", 1e-11)):
        if not finite_number(manifest.get(name)) or not 0 < manifest[name] <= maximum:
            raise ValueError("Invalid C1 tolerance")
    if type(manifest.get("reference_max_iterations")) is not int or manifest["reference_max_iterations"] < 1:
        raise ValueError("Invalid reference iteration budget")
    Settings(**manifest["settings"]).validate()
    return manifest


def evaluate_case(case, manifest, output, identity):
    started = perf_counter()
    manifest_hash = digest(manifest)
    saved, setup = save_initial_state(case.base, manifest_hash, Settings(**manifest["settings"]))
    label = f"{identity['nodes']}_{identity['kind']}"
    (output / "states" / f"{label}_before.json").write_text(saved + "\n")
    load_started = perf_counter()
    state = IncrementalGeometry.from_saved(saved)
    load_seconds = perf_counter() - load_started
    before = state.export()
    (output / "states" / f"{label}_fork_before.json").write_text(before + "\n")
    old = GeometryState.load(saved)
    expected_retention = [old.query(*pair) for pair in case.retention_queries]
    trace = state.update(case.updated, manifest_hash, manifest["edge_visit_budget"])
    committed = trace["status"] == "PASS"
    persistence_started = perf_counter()
    after = state.export()
    (output / "states" / f"{label}_after.json").write_text(after + "\n")
    persistence_seconds = perf_counter() - persistence_started
    queries = case.queries + case.affected_queries
    query_started = perf_counter()
    actual = [checked_query(state, pair) for pair in queries]
    query_seconds = perf_counter() - query_started
    query_immutable = state.export() == after
    ls = SparseLeastSquares(case.updated, manifest["reference_tolerance"], manifest["reference_max_iterations"])
    compiled = CompiledCoordinates(case.updated)
    reference_query_started = perf_counter()
    expected = [ls.query(*pair) for pair in queries]
    ls_query_seconds = perf_counter() - reference_query_started
    compiled_query_started = perf_counter()
    compiled_answers = [compiled.query(*pair) for pair in queries]
    compiled_query_seconds = perf_counter() - compiled_query_started
    errors, compiled_errors = [], []
    statuses_equal = True
    if ls.status == "PASS":
        for a, b, c in zip(actual, expected, compiled_answers):
            statuses_equal &= a.status == b.status
            if a.status == b.status == "OK":
                error = displacement_error(a, b)
                if error is None:
                    statuses_equal = False
                else:
                    errors.append(error)
                if c.status == "OK":
                    error = displacement_error(a, c)
                    if error is not None:
                        compiled_errors.append(error)
    retention_started = perf_counter()
    retention = [checked_query(state, pair) for pair in case.retention_queries]
    retention_seconds = perf_counter() - retention_started
    reload_started = perf_counter()
    loaded = IncrementalGeometry.load(after)
    reload_equal = all(loaded.query(*p) == a for p, a in zip(queries, actual))
    reload_seconds = perf_counter() - reload_started
    # Independent committed residual, never trust candidate-reported energy alone.
    residuals = []
    if committed:
        for edge in case.updated.edges:
            answer = checked_query(state, (edge.source, edge.target))
            if answer.status != "OK":
                statuses_equal = False
                break
            residuals.append((edge.weight, np.asarray(answer.displacement) - edge.offset))
    with np.errstate(over="ignore", invalid="ignore"):
        observed_energy = float(sum(0.5 * w * float(r @ r) for w, r in residuals)) if committed and len(residuals) == len(case.updated.edges) else None
    if not finite_number(observed_energy):
        observed_energy = None
    ls_error = max(errors) if errors else None
    energy_gap = abs(observed_energy - ls.energy) if observed_energy is not None else None
    # Every OK answer needs a finite error; max() alone can silently ignore NaN.
    expected_ok = sum(a.status == "OK" for a in expected)
    correct_commit = committed and statuses_equal and len(errors) == expected_ok and expected_ok > 0 and all(finite_number(e) and e <= manifest["displacement_tolerance"] for e in errors) and finite_number(energy_gap) and energy_gap <= manifest["energy_tolerance"]
    counters = [trace.get(key) for key in ("dynamic_edge_visits", "warm_start_edge_visits", "local_edge_visits", "certificate_edge_visits")]
    metered = all(type(v) is int and v >= 0 for v in counters) and counters[0] == sum(counters[1:]) and counters[0] <= manifest["edge_visit_budget"]
    required = trace.get("budget_exhaustion_required_visits")
    exhausted = type(required) is int and required > 0 and metered and counters[0] + required > manifest["edge_visit_budget"]
    explicit_rejection = trace["status"] == "NOT_CONVERGED" and before == after and trace["snapshot_retained"] is True and exhausted
    retained = retention == expected_retention
    frozen_before = old.export() == saved
    passed = ls.status == "PASS" and (correct_commit or explicit_rejection) and retained and query_immutable and reload_equal and frozen_before and metered and trace["fallbacks"] == 0
    panel = []
    for pair, a, b, c in zip(queries, actual, expected, compiled_answers):
        error = displacement_error(a, b)
        panel.append({"pair": pair, "candidate": asdict(a), "reference": asdict(b), "compiled": asdict(c), "displacement_error": error, "compiled_displacement_error": displacement_error(c, b)})
    identifiable = [p for p in panel if p["reference"]["status"] == "OK"]
    covered = [p for p in identifiable if p["candidate"]["status"] == "OK"]
    correct = [p for p in covered if finite_number(p["displacement_error"]) and p["displacement_error"] <= manifest["displacement_tolerance"]]
    compiled_covered = [p for p in identifiable if p["compiled"]["status"] == "OK"]
    compiled_correct = [p for p in compiled_covered if finite_number(p["compiled_displacement_error"]) and p["compiled_displacement_error"] <= manifest["displacement_tolerance"]]
    return dict(identity, check_status="PASS" if passed else "ASSERTION_FAILURE", candidate=trace,
                setup=setup, load_seconds=load_seconds, committed=committed, correct_commit=bool(correct_commit),
                explicit_rejection=bool(explicit_rejection), retention_queries=len(case.retention_queries), retention_pass=retained,
                affected_queries=len(case.affected_queries), queries=len(queries), query_seconds=query_seconds,
                query_immutable=query_immutable, reload_equal=reload_equal, reload_seconds=reload_seconds,
                retention_seconds=retention_seconds, reference_status=ls.status, reference_iterations=ls.iterations,
                reference_edge_visits=ls.edge_visits, reference_seconds=ls.build_seconds,
                reference_query_seconds=ls_query_seconds, reference_numeric_workspace_bytes=ls.numeric_workspace_bytes,
                compiled_seconds=compiled.build_seconds, compiled_query_seconds=compiled_query_seconds,
                compiled_residual_max=compiled.residual_max, least_squares_displacement_error_max=ls_error,
                compiled_displacement_error_max=max(compiled_errors) if compiled_errors else None,
                observed_energy=observed_energy, reference_energy=ls.energy, energy_gap=energy_gap,
                source_observation_hash=digest(asdict(case.base)), update_observation_hash=digest(asdict(case.updated)),
                old_artifact_hash=hashlib.sha256(saved.encode()).hexdigest(), after_artifact_hash=hashlib.sha256(after.encode()).hexdigest(),
                fork_before_artifact_hash=hashlib.sha256(before.encode()).hexdigest(),
                query_panel=panel, identifiable_queries=len(identifiable), query_coverage=len(covered) / len(identifiable) if identifiable else None,
                query_total_accuracy=len(correct) / len(identifiable) if identifiable else None,
                query_conditional_accuracy=len(correct) / len(covered) if covered else None,
                compiled_query_coverage=len(compiled_covered) / len(identifiable) if identifiable else None,
                compiled_query_total_accuracy=len(compiled_correct) / len(identifiable) if identifiable else None,
                compiled_query_conditional_accuracy=len(compiled_correct) / len(compiled_covered) if compiled_covered else None,
                excluded_cross_queries=sum(p["reference"]["status"] == "UNIDENTIFIABLE" for p in panel),
                cross_abstention_correct=sum(p["reference"]["status"] == p["candidate"]["status"] == "UNIDENTIFIABLE" for p in panel),
                persistence_seconds=persistence_seconds, serialized_bytes=len(after.encode()), total_seconds=perf_counter() - started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "experiments/c1_manifest.json")
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/c1_review")
    parser.add_argument("--contract-report", type=Path, default=ROOT / "evidence/c1_review/contracts.xml")
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
    with (args.output / "instances.jsonl").open("x") as stream:
        for size_id, nodes in enumerate(manifest["sizes"]):
            for kind_id, kind in enumerate(KINDS):
                seed = manifest["seed_start"] + 100 * size_id + kind_id
                identity = {"nodes": nodes, "kind": kind, "seed": seed}
                case_started = perf_counter()
                try:
                    case = generate_case(nodes, kind, seed)
                    generation_seconds = perf_counter() - case_started
                    row = evaluate_case(case, manifest, args.output, identity)
                    row.update(generation_seconds=generation_seconds)
                except Exception as exc:
                    row = dict(identity, check_status="INFRASTRUCTURE_FAILURE", error_type=type(exc).__name__, error=str(exc), committed=False)
                try:
                    encoded = json.dumps(row, allow_nan=False)
                except (ValueError, TypeError) as exc:
                    row = dict(identity, check_status="INFRASTRUCTURE_FAILURE", error_type=type(exc).__name__, error=f"Nonserializable case evidence: {exc}", committed=False)
                    encoded = json.dumps(row, allow_nan=False)
                stream.write(encoded + "\n")
                stream.flush()
                records.append(row)
                print(f"{nodes}/{kind}: {row['check_status']} / {row.get('candidate', {}).get('status', row.get('error', 'unknown'))}", flush=True)
    valid = [r for r in records if r["check_status"] == "PASS"]
    gates = {"contracts": contracts["status"] == "PASS", "complete_panel": len(records) == 16,
             "correct_or_explicitly_unresolved": len(valid) == 16, "source_stable": hashes == source_hashes(args.manifest.resolve()),
             "contracts_stable": contracts["report_sha256"] == hashlib.sha256(args.contract_report.read_bytes()).hexdigest(),
             "c0_acceptance_stable": acceptance_hash == check_c0_acceptance()}
    successful = [r for r in valid if r["committed"]]
    rejected = [r for r in valid if not r["committed"]]
    receipt = {
        "experiment_id": manifest["experiment_id"], "manifest": manifest, "manifest_hash": digest(manifest),
        "c0_acceptance_sha256": acceptance_hash,
        "command": shlex.join([sys.executable, "-m", "geomind.run_c1"] + sys.argv[1:]),
        "environment": {"python": sys.version, "numpy": np.__version__, "platform": platform.platform()},
        "source_commit": None, "file_hashes": hashes, "source_snapshot_hashes": snapshots,
        "contracts": contracts, "gates": gates, "check_status": "PASS" if all(gates.values()) else "ASSERTION_FAILURE",
        "implementation_status": "REVIEW_READY" if all(gates.values()) else "ACTIVE",
        "hypotheses": {"H-P": "INCONCLUSIVE", "H-L": "INCONCLUSIVE"},
        "hypothesis_limits": "This panel tests additive state persistence and disconnected retention, without an adaptive-versus-frozen task-learning comparison. H-L has no sublinear end-to-end claim: preprocessing and global certificates scan full input. Only one structured world per size/intervention.",
        "committed_updates": len(successful), "explicitly_unresolved_updates": len(rejected),
        "checks_not_run": ["independent C1 acceptance", "C2-C8", "automatic fallback", "C++/browser integration", "hardware energy"],
        "total_seconds": perf_counter() - started, "instances": records,
        "next_action": "Independent C1 review; evaluate unresolved scope before C2",
    }
    (args.output / "results.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    lines = ["# C1 incremental-update receipt", "", f"Implementation: **{receipt['implementation_status']}**. Checks: **{receipt['check_status']}**.", "", f"16 registered interventions; {len(successful)} committed, {len(rejected)} explicitly unresolved and rolled back. Elapsed: {receipt['total_seconds']:.2f}s.", "", "[Results](results.json), [per-case stream](instances.jsonl), [contracts](contracts.xml); exact before/after states in `states/` and source in `source/`.", "", "| Nodes | Intervention | Update | Dynamic edge visits | Reference error |", "|---:|---|---|---:|---:|"]
    for row in records:
        t = row.get("candidate", {})
        lines.append(f"| {row['nodes']} | {row['kind']} | {t.get('status', row['check_status'])} | {t.get('dynamic_edge_visits', 'n/a')} | {row.get('least_squares_displacement_error_max')} |")
    lines.extend(["", "Unresolved updates preserve the preceding snapshot and are not counted as correct committed answers. Every accepted result is compared with fresh sparse least squares; the dense reference qualified that solver at small sizes in the contracts. Third disconnected components are retention controls; connected distant nodes are allowed to change.", "", "Shared saved-state preparation, queue work, global proof scans, reference solves, query, load and persistence costs are reported. No full-solve fallback, sublinear computation, broad learning claim or hierarchy is implied. C1 acceptance is pending."])
    (args.output / "README.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"gates": gates, "committed": len(successful), "unresolved": len(rejected), "seconds": receipt["total_seconds"]}, indent=2))
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
