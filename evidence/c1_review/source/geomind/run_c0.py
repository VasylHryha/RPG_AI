"""Frozen C0 evaluator: independent metrics, append-only instances, explicit failures."""

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import shlex
import shutil
import sys
from time import perf_counter
import xml.etree.ElementTree as ET

import numpy as np

from .dataset import GENERATOR_VERSION, generate
from .geometry import GeometryState, Settings, digest, finite_number
from .references import CompiledCoordinates, DirectEdges, LeastSquares

ROOT = Path(__file__).resolve().parents[1]
ARMS = ("lattice", "continuous", "disconnected", "inconsistent", "noisy")
CLEAN = frozenset(("lattice", "continuous", "disconnected"))


def validate_manifest(manifest):
    if not isinstance(manifest, dict) or manifest.get("generator_version") != GENERATOR_VERSION:
        raise ValueError("Generator version mismatch")
    if manifest.get("algorithm") != GeometryState.algorithm or manifest.get("schema") != "geomind.c0.experiment.v2":
        raise ValueError("Experiment/algorithm version mismatch")
    if manifest.get("arms") != list(ARMS):
        raise ValueError("All five declared arms required in canonical order")
    if manifest.get("anchor_rule") != "maximum_exposed_weighted_degree_then_sorted_id":
        raise ValueError("Unsupported anchor rule")
    Settings(**manifest["settings"]).validate()
    for name, lower in (("nodes_per_world", 16), ("queries_per_world", 8), ("arm_seed_stride", 1)):
        if type(manifest.get(name)) is not int or manifest[name] < lower:
            raise ValueError(f"Invalid {name}")
    for name, lower, upper in (("displacement_tolerance", 0, 1e-5), ("required_fraction", 0.99, 1), ("energy_tolerance", 0, 1e-8)):
        v = manifest.get(name)
        if not finite_number(v) or v <= 0 or not lower <= v <= upper:
            raise ValueError(f"Invalid {name}")
    if manifest.get("noise_sigma") != 0.05:
        raise ValueError("Unsupported noise protocol")
    split_counts = {"train": 100, "validation": 50, "test": 100}
    if not isinstance(manifest.get("splits"), dict) or set(manifest["splits"]) != set(split_counts):
        raise ValueError("Complete train/validation/test splits required")
    seeds = []
    for split, required in split_counts.items():
        config = manifest["splits"][split]
        if not isinstance(config, dict) or config.get("count") != required or type(config["count"]) is not int:
            raise ValueError("C0 qualification requires 100/50/100 worlds per arm")
        start = config.get("seed_start")
        if type(start) is not int or start < 0:
            raise ValueError("Nonnegative integer seeds required")
        for arm in range(len(ARMS)):
            seeds.extend(start + arm * manifest["arm_seed_stride"] + i for i in range(required))
    if len(seeds) != len(set(seeds)):
        raise ValueError("World seeds overlap across splits/arms")
    uncertainty = manifest["uncertainty"]
    if uncertainty.get("unit") != "independent world" or uncertainty.get("method") != "percentile bootstrap":
        raise ValueError("Unsupported uncertainty protocol")
    if type(uncertainty.get("replicates")) is not int or uncertainty["replicates"] < 100 or type(uncertainty.get("seed")) is not int or uncertainty["seed"] < 0:
        raise ValueError("Invalid bootstrap budget/seed")
    return manifest


def evaluate_world(world, settings, manifest_hash, tolerance):
    started = perf_counter()
    if not world.queries or len(set(world.queries)) != len(world.queries):
        raise ValueError("Nonempty unique query panel required")
    supplied = {frozenset((e.source, e.target)) for e in world.observation.edges}
    if any(frozenset(pair) in supplied for pair in world.queries):
        raise ValueError("Primary query was directly exposed")
    if not all(tuple(sorted((e.source, e.target))) in world.queries for e in world.hidden_edges):
        raise ValueError("Every hidden redundant edge must be evaluated")
    state = GeometryState(settings)
    trace = state.learn(world.observation, manifest_hash)
    references = {"compiled": CompiledCoordinates(world.observation), "least_squares": LeastSquares(world.observation), "direct_edge": DirectEdges(world.observation)}
    encoded = None
    if trace["status"] == "PASS":
        state.freeze()
        encoded = state.export()
    # Commit every method's answers before reading evaluator truth.
    panels = {"indirect": world.queries, "cross": world.cross_component_queries,
              "direct": tuple((e.source, e.target) for e in world.observation.edges)}
    methods = dict(candidate=state, **references)
    answers, times = {}, {}
    for name, method in methods.items():
        answers[name], times[name] = {}, {}
        for panel, pairs in panels.items():
            query_started = perf_counter()
            answers[name][panel] = [method.query(a, b) for a, b in pairs]
            times[name][panel] = perf_counter() - query_started
    immutable = encoded is None or encoded == state.export()
    serialization_started = perf_counter()
    reload_equal = False
    if encoded is not None:
        reloaded = GeometryState.load(encoded)
        reload_equal = all([reloaded.query(*p) for p in pairs] == answers["candidate"][panel] for panel, pairs in panels.items())
    serialization_seconds = perf_counter() - serialization_started
    metrics = {}
    for name in methods:
        metrics[name] = {}
        for panel in ("indirect", "direct"):
            values = answers[name][panel]
            errors_truth, errors_ls = [], []
            correct_truth = correct_ls = 0
            for k, ((a, b), answer) in enumerate(zip(panels[panel], values)):
                if answer.status != "OK":
                    continue
                if answer.displacement is None or len(answer.displacement) != 2 or not np.isfinite(answer.displacement).all():
                    raise ValueError("Method returned a nonfinite/malformed OK answer")
                expected = np.asarray(world.truth[b]) - world.truth[a]
                truth_error = float(np.linalg.norm(np.asarray(answer.displacement) - expected))
                ls_answer = answers["least_squares"][panel][k]
                if ls_answer.status != "OK":
                    raise ValueError("Independent reference cannot identify declared query")
                ls_error = float(np.linalg.norm(np.asarray(answer.displacement) - ls_answer.displacement))
                errors_truth.append(truth_error)
                errors_ls.append(ls_error)
                correct_truth += truth_error <= tolerance
                correct_ls += ls_error <= tolerance
            covered = len(errors_truth)
            metrics[name][panel] = {
                "queries": len(values), "answered": covered, "coverage": covered / len(values) if values else None,
                "correct_truth": correct_truth, "total_truth_accuracy": correct_truth / len(values) if values else None,
                "conditional_truth_accuracy": correct_truth / covered if covered else None,
                "correct_least_squares": correct_ls, "total_least_squares_accuracy": correct_ls / len(values) if values else None,
                "conditional_least_squares_accuracy": correct_ls / covered if covered else None,
                "truth_error_max": max(errors_truth) if errors_truth else None,
                "least_squares_error_max": max(errors_ls) if errors_ls else None,
            }
        metrics[name]["cross"] = {"queries": len(panels["cross"]), "unidentifiable": sum(a.status == "UNIDENTIFIABLE" for a in answers[name]["cross"]), "incorrect_ok": sum(a.status == "OK" for a in answers[name]["cross"])}
    # Residual independently evaluated from committed query answers, not trusted trace.
    observed_energy = None
    observed_residual_max = None
    if all(a.status == "OK" for a in answers["candidate"]["direct"]):
        residuals = [np.asarray(a.displacement) - e.offset for a, e in zip(answers["candidate"]["direct"], world.observation.edges)]
        observed_energy = float(sum(0.5 * e.weight * float(np.dot(r, r)) for e, r in zip(world.observation.edges, residuals)))
        observed_residual_max = max((float(np.linalg.norm(r)) for r in residuals), default=0.0)
    agreeing = 0
    for k, (a, b) in enumerate(world.queries):
        candidate = answers["candidate"]["indirect"][k]
        if candidate.status != "OK":
            continue
        values = [np.asarray(world.truth[b]) - world.truth[a], answers["compiled"]["indirect"][k].displacement, answers["least_squares"]["indirect"][k].displacement]
        agreeing += all(v is not None and float(np.linalg.norm(np.asarray(candidate.displacement) - v)) <= tolerance for v in values)
    return {
        "check_status": "PASS", "candidate": trace, "queries": len(world.queries), "agreeing_clean_queries": agreeing,
        "primary_fraction": agreeing / len(world.queries), "methods": metrics,
        "cross_component_queries": len(panels["cross"]), "cross_component_abstentions": metrics["candidate"]["cross"]["unidentifiable"],
        "observed_energy": observed_energy, "observed_residual_max": observed_residual_max,
        "reference_energy": references["least_squares"].energy,
        "energy_gap": abs(observed_energy - references["least_squares"].energy) if observed_energy is not None else None,
        "reported_energy_gap": abs(observed_energy - trace["energy"]) if observed_energy is not None and trace["energy"] is not None else None,
        "query_immutable": immutable, "reload_equal": reload_equal,
        "reference_build_seconds": {name: method.build_seconds for name, method in references.items()},
        "compiled_edge_visits": references["compiled"].edge_visits,
        "least_squares_matrix_bytes": references["least_squares"].matrix_bytes,
        "query_seconds": times, "serialization_load_seconds": serialization_seconds,
        "serialized_bytes": len(encoded.encode()) if encoded else 0,
        "state_hash": hashlib.sha256(encoded.encode()).hexdigest() if encoded else None,
        "total_seconds": perf_counter() - started,
    }


def aggregate(records, manifest):
    summaries = {}
    for split in sorted({r["split"] for r in records}):
        for arm_id, arm in enumerate(ARMS):
            rows = [r for r in records if r["split"] == split and r["arm"] == arm]
            if not rows:
                continue
            rng = np.random.default_rng(manifest["uncertainty"]["seed"] + arm_id + {"train": 0, "validation": 100, "test": 200}[split])
            good = [r for r in rows if r["check_status"] == "PASS"]
            endpoint = "clean agreement" if arm in CLEAN else "least-squares agreement"
            fractions = np.array([r["primary_fraction"] if arm in CLEAN else r.get("methods", {}).get("candidate", {}).get("indirect", {}).get("total_least_squares_accuracy", 0) for r in rows])
            samples = rng.choice(fractions, size=(manifest["uncertainty"]["replicates"], len(rows)), replace=True).mean(axis=1)
            paired = np.array([r["candidate"]["total_learn_seconds"] + sum(r["query_seconds"]["candidate"].values()) - r["reference_build_seconds"]["compiled"] - sum(r["query_seconds"]["compiled"].values()) for r in good])
            paired_ci = np.quantile(rng.choice(paired, size=(manifest["uncertainty"]["replicates"], len(paired)), replace=True).mean(axis=1), [0.025, 0.975]).tolist() if len(paired) else None
            summaries[f"{split}/{arm}"] = {
                "worlds": len(rows), "queries": sum(r["queries"] for r in rows), "endpoint": endpoint,
                "fraction": float(fractions.mean()), "world_bootstrap_95_interval": np.quantile(samples, [0.025, 0.975]).tolist(),
                "infrastructure_failures": len(rows) - len(good),
                "nonconvergences": sum(r["candidate"]["status"] == "NOT_CONVERGED" for r in rows),
                "invalid_states": sum(r["candidate"]["status"] == "INVALID_STATE" for r in rows),
                "cross_component_queries": sum(r["cross_component_queries"] for r in rows),
                "cross_component_abstentions": sum(r["cross_component_abstentions"] for r in rows),
                "energy_gap_max": max((r["energy_gap"] for r in good if r["energy_gap"] is not None), default=None),
                "observed_residual_min": min((r["observed_residual_max"] for r in good if r["observed_residual_max"] is not None), default=None),
                "candidate_fit_seconds": sum(r["candidate"].get("total_learn_seconds", 0) for r in rows),
                "compiled_build_seconds": sum(r["reference_build_seconds"]["compiled"] for r in good),
                "paired_candidate_minus_compiled_fit_and_query_seconds_mean": float(paired.mean()) if len(paired) else None,
                "paired_world_bootstrap_95_interval_seconds": paired_ci,
                "methods": {name: {panel: {metric: float(np.mean([r["methods"][name][panel][metric] for r in good])) if good else None for metric in ("coverage", "total_truth_accuracy", "total_least_squares_accuracy")} for panel in ("indirect", "direct")} for name in ("candidate", "compiled", "least_squares", "direct_edge")},
            }
    return summaries


def qualification_gates(records, manifest, split_names):
    complete = all(sum(r["split"] == split and r["arm"] == arm for r in records) == manifest["splits"][split]["count"] for split in split_names for arm in ARMS)
    valid = bool(records) and all(r["check_status"] == "PASS" for r in records)
    converged = valid and all(r["candidate"]["status"] == "PASS" for r in records)
    return {
        "complete_panels": complete and bool(records), "infrastructure": valid, "convergence": converged,
        "clean_agreement": valid and all(sum(r["agreeing_clean_queries"] for r in records if r["split"] == split and r["arm"] == arm) / (manifest["queries_per_world"] * manifest["splits"][split]["count"]) >= manifest["required_fraction"] for split in split_names for arm in CLEAN),
        "disconnected_abstention": valid and all(r["cross_component_queries"] == r["cross_component_abstentions"] and all(r["methods"][name]["cross"]["unidentifiable"] == r["cross_component_queries"] for name in ("candidate", "compiled", "least_squares")) for r in records if r["arm"] == "disconnected"),
        "contradictions_visible": converged and all(finite_number(r["observed_residual_max"]) and r["observed_residual_max"] > 1e-4 and finite_number(r["energy_gap"]) and r["energy_gap"] <= manifest["energy_tolerance"] for r in records if r["arm"] not in CLEAN),
        "least_squares_agreement": converged and all(r["methods"]["candidate"]["indirect"]["coverage"] == 1 and finite_number(r["methods"]["candidate"]["indirect"]["least_squares_error_max"]) and r["methods"]["candidate"]["indirect"]["least_squares_error_max"] <= manifest["displacement_tolerance"] for r in records),
        "independent_residual": converged and all(finite_number(r["reported_energy_gap"]) and r["reported_energy_gap"] <= manifest["energy_tolerance"] for r in records),
        "persistence": converged and all(r["query_immutable"] and r["reload_equal"] for r in records),
    }


def source_hashes(manifest_path):
    paths = list((ROOT / "geomind").glob("*.py")) + list((ROOT / "tests").glob("*.py")) + list((ROOT / "experiments").glob("*.json")) + [ROOT / "pyproject.toml", ROOT / "uv.lock", manifest_path]
    return {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def snapshot_source(file_hashes, output):
    snapshot_hashes = {}
    for name, expected_hash in file_hashes.items():
        source = ROOT / name if not Path(name).is_absolute() else Path(name)
        relative = Path(name) if not Path(name).is_absolute() else Path("external_manifest.json")
        target = output / "source" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected_hash:
            raise RuntimeError("Source changed during snapshot capture")
        snapshot_hashes[str(relative)] = actual
    return snapshot_hashes


def contract_result(path):
    tree = ET.parse(path)
    cases = list(tree.getroot().iter("testcase"))
    failures = sum(bool(list(case.iter("failure"))) for case in cases)
    errors = sum(bool(list(case.iter("error"))) for case in cases)
    skipped = sum(bool(list(case.iter("skipped"))) for case in cases)
    return {"status": "PASS" if cases and not (failures or errors or skipped) else "ASSERTION_FAILURE", "tests": len(cases), "failures": failures, "errors": errors, "skipped": skipped, "report_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "report": str(path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "experiments/c0_manifest.json")
    parser.add_argument("--split", choices=("all", "train", "validation", "test"), default="all")
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/c0_review")
    parser.add_argument("--contract-report", type=Path, default=ROOT / "evidence/c0_review/contracts.xml")
    args = parser.parse_args()
    manifest = validate_manifest(json.loads(args.manifest.read_text()))
    contracts = contract_result(args.contract_report)
    settings = Settings(**manifest["settings"])
    manifest_hash = digest(manifest)
    split_names = list(manifest["splits"]) if args.split == "all" else [args.split]
    if any((args.output / name).exists() for name in ("results.json", "instances.jsonl", "README.md")):
        raise FileExistsError("Evidence already exists; choose a new output directory")
    args.output.mkdir(parents=True, exist_ok=True)
    initial_hashes = source_hashes(args.manifest.resolve())
    snapshot_hashes = snapshot_source(initial_hashes, args.output)
    records = []
    started = perf_counter()
    with (args.output / "instances.jsonl").open("x") as stream:
        for split in split_names:
            for arm_id, arm in enumerate(ARMS):
                config = manifest["splits"][split]
                for i in range(config["count"]):
                    seed = config["seed_start"] + arm_id * manifest["arm_seed_stride"] + i
                    instance_started = perf_counter()
                    identity = {"split": split, "arm": arm, "seed": seed}
                    try:
                        generation_started = perf_counter()
                        world = generate(seed, arm, manifest["nodes_per_world"], manifest["queries_per_world"])
                        generation_seconds = perf_counter() - generation_started
                        result = evaluate_world(world, settings, manifest_hash, manifest["displacement_tolerance"])
                        result.update(generation_seconds=generation_seconds, observation_hash=digest(asdict(world.observation)), evaluation_world_hash=digest({"truth": world.truth, "queries": world.queries, "hidden_edges": [asdict(e) for e in world.hidden_edges], "cross": world.cross_component_queries}), relation_manifest=world.observation.relations)
                    except Exception as exc:
                        result = {"check_status": "INFRASTRUCTURE_FAILURE", "error_type": type(exc).__name__, "error": str(exc), "candidate": {"status": "NOT_RUN"}, "queries": manifest["queries_per_world"], "agreeing_clean_queries": 0, "primary_fraction": 0, "cross_component_queries": 16 if arm == "disconnected" else 0, "cross_component_abstentions": 0}
                    result.update(identity, instance_total_seconds=perf_counter() - instance_started)
                    stream.write(json.dumps(result, allow_nan=False) + "\n")
                    stream.flush()
                    records.append(result)
                print(f"{split}/{arm}: {config['count']} worlds recorded", flush=True)
    summaries = aggregate(records, manifest)
    gates = qualification_gates(records, manifest, split_names)
    final_hashes = source_hashes(args.manifest.resolve())
    gates.update(contracts=contracts["status"] == "PASS", source_stable=initial_hashes == final_hashes)
    receipt = {
        "experiment_id": manifest["experiment_id"], "manifest": manifest, "split_manifest_hash": manifest_hash,
        "predecessor_experiment": manifest["historical_receipts"],
        "source_commit": None, "source_note": "No Git repository; file hashes captured before and after execution",
        "file_hashes": initial_hashes, "final_file_hashes": final_hashes,
        "source_snapshot": "source/", "source_snapshot_hashes": snapshot_hashes,
        "command": shlex.join([sys.executable, "-m", "geomind.run_c0"] + sys.argv[1:]),
        "environment": {"python": sys.version, "numpy": np.__version__, "platform": platform.platform(), "machine": platform.machine(), "processor": platform.processor()},
        "contract_checks": contracts, "gates": gates, "check_status": "PASS" if all(gates.values()) else "ASSERTION_FAILURE",
        "implementation_status": "REVIEW_READY" if all(gates.values()) and args.split == "all" else "ACTIVE",
        "hypothesis_status": "NOT_TESTED", "hypothesis_note": "Independent hypothesis adjudication pending; C0 is a reference reconstruction experiment, with no superiority or hierarchy claim",
        "checks_not_run": ["independent acceptance after review repairs", "C1-C8", "GeoTactics", "native Godot", "hardware energy"],
        "limitations": ["Transductive reconstruction from known offsets", "No cross-world trained model or recursive resonators", "Compiled coordinates solve clean data much more cheaply", "Paired timings are wall time; query microtimings cannot establish efficiency", "Numeric workspace bytes omit Python heap and temporary/peak allocations", "Bootstrap intervals describe sampled worlds, not out-of-family tasks"],
        "next_action": "Independent acceptance of reviewed C0 before C1" if all(gates.values()) else "Repair explicit C0 failures; preserve this receipt",
        "total_seconds": perf_counter() - started, "summaries": summaries, "instances": records,
    }
    (args.output / "results.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    lines = ["# GeoMind C0 review verification", "", f"Implementation: **{receipt['implementation_status']}**. Checks: **{receipt['check_status']}**. Hypothesis adjudication: **NOT_TESTED**.", "", "[Machine-readable receipt](results.json); [streamed individual worlds](instances.jsonl); [actual contract test report](contracts.xml).", "", f"Experiment: `{manifest['experiment_id']}`. Manifest: `{manifest_hash}`.", "", "| Split/arm | Worlds | Endpoint | Agreement | Unresolved/invalid |", "|---|---:|---|---:|---:|"]
    lines.extend(f"| {key} | {s['worlds']} | {s['endpoint']} | {s['fraction']:.6f} | {s['nonconvergences'] + s['invalid_states'] + s['infrastructure_failures']} |" for key, s in summaries.items())
    lines.extend(["", f"Elapsed: {receipt['total_seconds']:.2f}s. No settings selected from these final worlds. Baseline coverage, conditional/total accuracy, independent residuals and paired cost differences are retained.", "", "Noisy/inconsistent arms use least-squares agreement as their endpoint; exact truth is also reported separately. Direct-only lookup has zero coverage on indirect queries and is separately measured on exposed pairs.", "", "Initial experiment and failed checks remain historical evidence. No hierarchy, resonance or energy result is implied.", "", f"Next: {receipt['next_action']}."])
    (args.output / "README.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"gates": gates, "implementation_status": receipt["implementation_status"], "seconds": receipt["total_seconds"]}, indent=2))
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
