"""Registered C4 runner: base resonator, geometry <-> mode closure.

  .venv/bin/python -m geomind.run_c4 --smoke --output <smoke.json>          # development worlds only
  .venv/bin/python -m geomind.run_c4 --output evidence/c4_rNNN --contract-report <contracts.xml>

Run both through tools/verify.py --milestone c4. The recorded panel refuses to
start unless tools/milestones.py verifies every earlier stage for the exact
current code. The smoke run uses development worlds only and evaluates every
implementation gate, so the recorded panel cannot fail on a gate the smoke
could have caught. Final worlds are never simulated outside the panel.
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

from geomind.c4_experiment import ARMS, evaluate_arm, hypothesis_verdicts, model_params, numerical_checks, run_arm

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "experiments" / "c4_manifest.json"
SMOKE_WORLDS = 3


def load_manifest(path=MANIFEST):
    manifest = json.loads(Path(path).read_text())
    if manifest.get("experiment_id", "").rsplit("-", 1)[0] != "geomind-c4-r4" or manifest.get("status") != "REGISTERED":
        raise ValueError("A registered C4 manifest is required")
    if set(manifest["endpoints"]) != set(ENDPOINTS):
        raise ValueError("Manifest endpoints do not match the runner's evaluated endpoints")
    return manifest


ENDPOINTS = ("formation_identical", "formation_heterogeneous", "g_to_m_identical", "m_to_g_identical",
             "g_to_m_heterogeneous", "m_to_g_heterogeneous", "both_off_identical", "both_off_heterogeneous",
             "not_a_clump_identical", "not_a_clump_heterogeneous", "effective_state_identical",
             "effective_state_heterogeneous", "ablation_formation", "numerical_checks")


def _arm(args):
    manifest, entropy, arm, count = args
    started = time.perf_counter()
    records = run_arm(manifest, entropy, arm, list(range(count)), model_params(manifest))
    records["seconds"] = time.perf_counter() - started
    return arm, records


def execute(manifest, entropy, worlds_per_arm, jobs=2):
    """Run both arms (in parallel processes) and the numerical checks; return the evaluated receipt body."""
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        records = dict(pool.map(_arm, [(manifest, entropy, arm, worlds_per_arm) for arm in ARMS]))
    numerics = numerical_checks(manifest, model_params(manifest), entropy)
    rng = np.random.default_rng(np.random.SeedSequence([entropy, 99]))
    evaluations = {arm: evaluate_arm(records[arm], manifest, rng) for arm in ARMS}
    verdicts = {arm: hypothesis_verdicts(evaluations[arm], manifest["verdict_rules"]) for arm in ARMS}
    coverage = endpoint_coverage(evaluations, numerics)
    gates = implementation_gates(manifest, records, evaluations, numerics, coverage, worlds_per_arm)
    return {"evaluations": evaluations, "hypothesis_status": verdicts["identical"],
            "hypothesis_status_by_arm": verdicts, "numerical_checks": numerics, "endpoint_coverage": coverage,
            "gates": gates, "records": records, "seconds": time.perf_counter() - started}


def implementation_gates(manifest, records, evaluations, numerics, coverage, worlds_per_arm):
    """Implementation validity (not hypothesis support): the run is evidence only if all hold."""
    return {
        "complete_panel": all(len(records[a]["worlds"]) == worlds_per_arm for a in ARMS),
        "numerical_checks": numerics["verdict"] == "PASS",
        "detector_rejects_clumps": all(evaluations[a]["not_a_clump"]["verdict"] == "PASS" for a in ARMS),
        "endpoint_coverage": set(coverage["evaluated"]) | set(coverage["not_run"]) == set(manifest["endpoints"]),
    }


def endpoint_coverage(evaluations, numerics):
    evaluated = {}
    for arm in ARMS:
        e = evaluations[arm]
        evaluated[f"formation_{arm}"] = {"value": e["formation"], "verdict": e["formation"]["verdict"]}
        for name in ("g_to_m", "m_to_g", "both_off", "not_a_clump", "effective_state"):
            evaluated[f"{name}_{arm}"] = {"value": e[name], "verdict": e[name]["verdict"]}
    evaluated["ablation_formation"] = {"value": {arm: evaluations[arm]["ablation_formation"] for arm in ARMS},
                                       "verdict": "REPORTED"}
    evaluated["numerical_checks"] = {"value": numerics, "verdict": numerics["verdict"]}
    return {"evaluated": evaluated, "not_run": {}}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def environment():
    return {"python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform()}


def panel_gate():
    sys.path.insert(0, str(ROOT / "tools"))
    import milestones
    return milestones.check("c4", "panel"), milestones


def smoke(path):
    manifest = load_manifest()
    body = execute(manifest, manifest["seeds"]["development_entropy"], SMOKE_WORLDS)
    status = "PASS" if all(body["gates"].values()) else "FAIL"
    Path(path).write_text(json.dumps({"status": status, "worlds_per_arm": SMOKE_WORLDS, "seeds": "development",
                                      "gates": body["gates"], "hypothesis_status_by_arm": body["hypothesis_status_by_arm"],
                                      "seconds": body["seconds"]}, indent=2) + "\n")
    print(json.dumps({"status": status, "gates": body["gates"], "seconds": round(body["seconds"], 1)}))
    return 0 if status == "PASS" else 1


def panel(output, contract_report):
    problems, milestones = panel_gate()
    if problems:
        raise SystemExit("C4 panel gate blocked: " + " ".join(problems))
    output = Path(output)
    if output.exists():
        raise SystemExit(f"{output} exists; evidence is never overwritten")
    cases = list(ET.parse(contract_report).getroot().iter("testcase"))
    if not cases or any(list(c.iter("failure")) or list(c.iter("error")) or list(c.iter("skipped")) for c in cases):
        raise SystemExit("Passing focused contracts are required")
    manifest = load_manifest()
    hashes = {str(p.relative_to(ROOT)): sha256(p) for p in milestones.dependency_files("c4")}
    fingerprint = milestones.fingerprint("c4")
    output.mkdir(parents=True)
    shutil.copyfile(contract_report, output / "contracts.xml")
    body = execute(manifest, manifest["seeds"]["final_entropy"], manifest["seeds"]["final_worlds_per_arm"])
    stable = hashes == {str(p.relative_to(ROOT)): sha256(p) for p in milestones.dependency_files("c4")}
    gates = {"contracts": True, **body["gates"], "source_hashes_stable": stable}
    passed = all(gates.values())
    receipt = {
        "complete": body["gates"]["complete_panel"],
        "check_status": "PASS" if passed else "ASSERTION_FAILURE",
        "implementation_status": "REVIEW_READY" if passed else "CHANGES_REQUIRED",
        "hypothesis_status": body["hypothesis_status"],
        "hypothesis_status_by_arm": body["hypothesis_status_by_arm"],
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
        "numerical_checks": body["numerical_checks"],
        "arms": body["evaluations"],
        "records": body["records"],
        "total_seconds": body["seconds"],
        "checks_not_run": [],
        "limitations": [
            "A mechanism probe of known swarmalator dynamics: no novelty, hierarchy (C5+), task-usefulness, efficiency or energy claim.",
            "One model family, one element count (N = 24), one neighbor rule and one parameter set; no sweep.",
            "The identical-omega arm is a synchronizing fixture: its mode has collective frequency 0, and G->M is measured through the restoring rate of a probe kick, not through a spontaneous mode change.",
            "Ablations are matched on state (pairs start from the intact formed state); with J = 0 and w = 1, geometry still reaches the phases through neighbor selection (reported as both_off).",
            "Detector thresholds were settled on development worlds; changes from the proposal are listed in the manifest.",
        ],
        "next_action": "One independent review by the other model family (Codex), on the committed evidence; no C5 work before acceptance.",
    }
    (output / "results.json").write_text(json.dumps(receipt, indent=2, default=_json_default) + "\n")
    print(json.dumps({"check_status": receipt["check_status"], "hypothesis_status_by_arm": receipt["hypothesis_status_by_arm"],
                      "gates": gates, "seconds": round(body["seconds"], 1)}))
    return 0 if passed else 1


def _json_default(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
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
