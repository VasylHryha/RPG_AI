"""Registered C5 runner: many resonators form one new effective resonator.

  .venv/bin/python -m geomind.run_c5 --smoke --output <smoke.json>          # development worlds only
  .venv/bin/python -m geomind.run_c5 --output evidence/c5_rNNN --contract-report <contracts.xml>

Run both through tools/verify.py --milestone c5. The recorded panel refuses to start unless
tools/milestones.py verifies every earlier stage for the exact current code. The smoke run uses
development entropy only and evaluates every implementation gate. Final worlds and their harvest
worlds are never simulated outside the panel.
"""

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from geomind import c5_experiment as E

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "experiments" / "c5_manifest.json"
SMOKE_WORLDS = 3
JOBS = 4

ENDPOINTS = ("level1_pool", "formation_l2", "formation_outcomes", "formation_vs_spread", "not_independent",
             "not_a_clump_l2", "g_to_m_l2", "m_to_g_l2", "dose_response_l2", "g_to_m_channels_l2", "parts_alive",
             "downward_effect", "emergent_transfer", "effective_state_l2", "coarse_vs_full", "timescale_separation",
             "same_rule_audit", "numerical_checks")


def load_manifest(path=MANIFEST):
    manifest = json.loads(Path(path).read_text())
    if manifest.get("experiment_id", "").rsplit("-", 1)[0] != "geomind-c5-r4" or manifest.get("status") != "REGISTERED":
        raise ValueError("A registered C5 manifest is required")
    if set(manifest["endpoints"]) != set(ENDPOINTS):
        raise ValueError("Manifest endpoints do not match the runner's evaluated endpoints")
    return manifest


def _harvest(args):
    manifest, entropy, indices = args
    c4m = E.load_c4(manifest)
    params = E.model_params(c4m)["intact"]
    return E.harvest(c4m, params, entropy, indices, tuple(manifest["level1"]["size_range"]))


def _worlds(args):
    manifest, entropy, indices, templates = args
    return E.run_worlds(manifest, entropy, indices, templates)


def execute(manifest, entropy, worlds, jobs=JOBS):
    """Harvest, all worlds (in parallel chunks), numerical checks and evaluation; return the receipt body."""
    started = time.perf_counter()
    count = E.harvest_count(manifest, worlds)
    chunks = [list(range(count))[k::jobs] for k in range(jobs)]
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        harvested = list(pool.map(_harvest, [(manifest, entropy, c) for c in chunks]))
    # Restore harvest order (world index order) so template assignment does not depend on chunking.
    by_world = sorted(((t["source_world"], n, t) for part in harvested for n, t in enumerate(part[0])), key=lambda r: (r[0], r[1]))
    templates = [t for _, _, t in by_world]
    sizes = [s for part in harvested for s in part[1]["accepted_sizes"]]
    pool_record = {"c4_worlds": count, "worlds_with_resonator": sum(p[1]["worlds_with_resonator"] for p in harvested),
                   "accepted_resonators": len(sizes), "accepted_sizes": sorted(sizes), "templates_in_range": len(templates),
                   "templates_needed": manifest["worlds"]["units_per_world"] * worlds,
                   "size_range": manifest["level1"]["size_range"]}
    if len(templates) < manifest["worlds"]["units_per_world"] * worlds:
        raise SystemExit("too few level-1 templates: the harvest ratio is insufficient")
    world_chunks = [list(range(worlds))[k::jobs] for k in range(jobs)]
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        parts = list(pool.map(_worlds, [(manifest, entropy, c, templates) for c in world_chunks if c]))
    records = sorted((w for part in parts for w in part), key=lambda w: w["seed_index"])
    numerics = E.numerical_checks(manifest, templates, entropy)
    c4m = E.load_c4(manifest)
    S = E.settings(manifest, c4m)
    evaluation = E.evaluate(records, pool_record, manifest, S, np.random.default_rng(np.random.SeedSequence([entropy, 99])))
    audit = E.same_rule_audit(manifest)
    tau1 = [t for w in records for t in w["tau1"] if np.isfinite(t)]
    tau2 = [g["tau2"] for w in records for g in w["groups"] if np.isfinite(g["tau2"])]
    measured = float(np.median(tau2) / np.median(tau1)) if tau1 and tau2 else None
    audit["final_measured"] = {"tau1_median": float(np.median(tau1)) if tau1 else None,
                               "tau2_median": float(np.median(tau2)) if tau2 else None, "ratio": measured,
                               "within_half_to_double_T": (measured is not None and S["T"] / 2 <= measured <= 2 * S["T"])}
    evaluation["same_rule_audit"] = audit
    evaluation["numerical_checks"] = numerics
    verdicts = E.hypothesis_verdicts(evaluation)
    coverage = endpoint_coverage(evaluation)
    gates = implementation_gates(manifest, records, evaluation, coverage, worlds)
    return {"evaluation": evaluation, "hypothesis_status": verdicts, "endpoint_coverage": coverage, "gates": gates,
            "records": records, "templates_used": manifest["worlds"]["units_per_world"] * worlds,
            "seconds": time.perf_counter() - started}


def implementation_gates(manifest, records, e, coverage, worlds):
    """Implementation validity (not hypothesis support): the run is evidence only if all hold."""
    return {
        "complete_panel": len(records) == worlds,
        "numerical_checks": e["numerical_checks"]["verdict"] == "PASS",
        "controls_non_vacuous_reject": e["not_independent"]["verdict"] == "PASS" and e["not_a_clump_l2"]["verdict"] == "PASS",
        "level1_pool": e["level1_pool"]["verdict"] == "PASS",
        "same_rule_audit": e["same_rule_audit"]["verdict"] == "PASS",
        "endpoint_coverage": set(coverage["evaluated"]) | set(coverage["not_run"]) == set(manifest["endpoints"]),
    }


def endpoint_coverage(e):
    return {"evaluated": {name: {"value": e[name], "verdict": e[name]["verdict"]} for name in ENDPOINTS}, "not_run": {}}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def environment():
    return {"python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform()}


def panel_gate():
    sys.path.insert(0, str(ROOT / "tools"))
    import milestones
    return milestones.check("c5", "panel"), milestones


def smoke(path):
    manifest = load_manifest()
    body = execute(manifest, manifest["seeds"]["development_entropy"], SMOKE_WORLDS)
    # The controls must reject; with three worlds they are non-vacuous whenever any world has a candidate group.
    status = "PASS" if all(body["gates"].values()) else "FAIL"
    Path(path).write_text(json.dumps({"status": status, "worlds": SMOKE_WORLDS, "seeds": "development", "gates": body["gates"],
                                      "hypothesis_status": body["hypothesis_status"], "seconds": body["seconds"]},
                                     indent=2, default=_json_default) + "\n")
    print(json.dumps({"status": status, "gates": body["gates"], "seconds": round(body["seconds"], 1)}))
    return 0 if status == "PASS" else 1


def panel(output, contract_report):
    problems, milestones = panel_gate()
    if problems:
        raise SystemExit("C5 panel gate blocked: " + " ".join(problems))
    output = Path(output)
    if output.exists():
        raise SystemExit(f"{output} exists; evidence is never overwritten")
    cases = list(ET.parse(contract_report).getroot().iter("testcase"))
    if not cases or any(list(c.iter("failure")) or list(c.iter("error")) or list(c.iter("skipped")) for c in cases):
        raise SystemExit("Passing focused contracts are required")
    manifest = load_manifest()
    hashes = {str(p.relative_to(ROOT)): sha256(p) for p in milestones.dependency_files("c5")}
    fingerprint = milestones.fingerprint("c5")
    output.mkdir(parents=True)
    shutil.copyfile(contract_report, output / "contracts.xml")
    body = execute(manifest, manifest["seeds"]["final_entropy"], manifest["seeds"]["final_worlds"])
    stable = hashes == {str(p.relative_to(ROOT)): sha256(p) for p in milestones.dependency_files("c5")}
    gates = {"contracts": True, **body["gates"], "source_hashes_stable": stable}
    passed = all(gates.values())
    receipt = {
        "complete": body["gates"]["complete_panel"],
        "check_status": "PASS" if passed else "ASSERTION_FAILURE",
        "implementation_status": "REVIEW_READY" if passed else "CHANGES_REQUIRED",
        "hypothesis_status": body["hypothesis_status"],
        "experiment_id": manifest["experiment_id"],
        "manifest": manifest,
        "manifest_hash": sha256(MANIFEST),
        "source_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
        "dependency_fingerprint": fingerprint,
        "file_hashes": hashes,
        "environment": environment(),
        "contracts": {"count": len(cases), "report_sha256": sha256(contract_report)},
        "gates": gates,
        "endpoint_coverage": body["endpoint_coverage"],
        "endpoints": body["evaluation"],
        "records": body["records"],
        "total_seconds": body["seconds"],
        "checks_not_run": [],
        "limitations": [
            "One composition step (R0 -> R1); no recursion (C6), dissolution (C7), usefulness or efficiency (C8) claim. Work counts are descriptive.",
            "Staged assembly: level-1 units are formed separately and placed together; per-unit rates are an experimental fixture.",
            "One model, one parameter set, M = 5, unit sizes 6-16; no internally heterogeneous unit (the C4 heterogeneous arm is not accepted).",
            "Complete ablations remove their pathway by construction; the evidence is the intact effect and its dose-response.",
            "Downward effect (a), rate entrainment, is largely implied by acceptance; (b) tests existence, not dose.",
            "The frozen C4 component rule (close and locked elements) sees an accepted level-2 group as one component; the level-2 claim rests on criterion 6 (distinct, internally valid units) and timescale separation, both reported.",
            "Hierarchical synchrony and population reduction are known results; this is a mechanism probe of the R4 composition rule.",
            "Development settings (placement radius, rate spread, T, port overlap) and the changes from the proposal are listed in the manifest.",
        ],
        "next_action": "One independent review by the other model family (Codex), on the committed evidence; no C6 work before acceptance.",
    }
    (output / "results.json").write_text(json.dumps(receipt, indent=2, default=_json_default) + "\n")
    print(json.dumps({"check_status": receipt["check_status"], "hypothesis_status": receipt["hypothesis_status"],
                      "gates": gates, "seconds": round(body["seconds"], 1)}))
    return 0 if passed else 1


def _json_default(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"not serializable: {type(value)}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--output", required=True)
    parser.add_argument("--contract-report")
    args = parser.parse_args(argv)
    if args.smoke:
        return smoke(args.output)
    if not args.contract_report:
        parser.error("--contract-report is required for the recorded panel")
    return panel(args.output, args.contract_report)


if __name__ == "__main__":
    sys.exit(main())
