"""Gated verification pipeline for a GeoMind C1 revision.

Stages run cheapest first. Each starts only when tools/gate.py verifies every
earlier stage for exactly the current code, and each stamps the artifact that
proves it. A failure stops the pipeline before any later stage. Rerunning
resumes after the last verified stage; nothing that already passed reruns.

  0 preflight  committed tree, no uncommitted source files, accepted C0 inputs unchanged, manifest valid
  1 tests      C1 checks (JUnit staged in .gate/) and C0 contracts, stop at first failure
  2 smoke      one 32-node world per intervention through the real evaluator, on non-panel seeds
  3 mutation   parallel fail-fast mutation probe (tools/mutation_probe.py)
  4 panel      the recorded registered panel, run once, serially (its timings are evidence)

The independent review is not a stage here. It runs once per milestone, on the
committed panel evidence, and tools/gate.py checks its prerequisites.

Usage: .venv/bin/python tools/verify_milestone.py --output evidence/c1_rNNN [--through STAGE]
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(ROOT / ".venv/bin/python")
STAGES = ("preflight", "tests", "smoke", "mutation", "panel")


class GateFailed(Exception):
    pass


def run(command, timeout):
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise GateFailed("\n".join((result.stdout + result.stderr).strip().splitlines()[-15:]))
    return result.stdout


def preflight(args, staging):
    sys.path.insert(0, str(ROOT))
    from geomind.run_c1 import check_c0_acceptance, validate_manifest
    problems = gate.tree_problems()
    if problems:
        raise GateFailed(" ".join(problems))
    if args.output.exists():
        raise GateFailed(f"{args.output} already exists; evidence is never overwritten")
    check_c0_acceptance()
    validate_manifest(json.loads((ROOT / "experiments/c1_manifest.json").read_text()))
    return [], {}


def tests(args, staging):
    report = staging / "contracts.xml"
    run([PYTHON, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", "tests/test_c1.py", f"--junitxml={report}"], 900)
    c0_report = staging / "c0_contracts.xml"
    run([PYTHON, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", "tests/test_c0.py", "tests/test_review_contracts.py", "tests/test_gate.py", f"--junitxml={c0_report}"], 900)
    return [report, c0_report], {}


def smoke(args, staging):
    sys.path.insert(0, str(ROOT))
    from geomind.c1_cases import KINDS, generate_case
    from geomind.run_c1 import evaluate_case, validate_manifest
    manifest = validate_manifest(json.loads((ROOT / "experiments/c1_manifest.json").read_text()))
    log = staging / "smoke.json"
    rows = {}
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "states").mkdir()
        for k, kind in enumerate(KINDS):
            # Seeds far from the registered panel's, so the smoke run never previews panel data.
            row = evaluate_case(generate_case(32, kind, 990000 + k), manifest, Path(tmp), {"nodes": 32, "kind": kind})
            rows[kind] = row["check_status"]
            if row["check_status"] != "PASS":
                raise GateFailed(f"Smoke case {kind} failed the evaluator gates")
    log.write_text(json.dumps(rows, indent=2) + "\n")
    return [log], {}


def mutation(args, staging):
    report = staging / "mutation.json"
    if report.exists():
        report.unlink()  # a stale failing report from an earlier attempt on this code
    run([PYTHON, "tools/mutation_probe.py", "--out", str(report)], 3600)
    summary = json.loads(report.read_text())
    return [report], {k: summary[k] for k in ("detected", "total", "survivors", "seconds")}


def panel(args, staging):
    run([PYTHON, "-m", "geomind.run_c1", "--output", str(args.output), "--contract-report", str(staging / "contracts.xml")], 3600)
    shutil.copyfile(staging / "mutation.json", args.output / "MUTATION.json")
    return [args.output / "results.json"], {}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--through", choices=STAGES, default="panel")
    args = parser.parse_args()
    args.output = args.output if args.output.is_absolute() else (ROOT / args.output)
    code = gate.fingerprint()
    staging = gate.stage_dir(code)
    staging.mkdir(parents=True, exist_ok=True)
    log = []
    for stage in STAGES[:STAGES.index(args.through) + 1]:
        if stage in gate.verified() and stage != "preflight":
            print(f"[{stage}] already verified for this code; skipped", flush=True)
            continue
        started = time.perf_counter()
        print(f"[{stage}] ...", flush=True)
        try:
            # The same gate the agent hooks enforce: earlier stages verified for this code.
            problems = gate.check(stage) if stage != "preflight" else []
            if problems:
                raise GateFailed(" ".join(problems))
            artifacts, detail = globals()[stage](args, staging)
        except GateFailed as exc:
            print(f"[{stage}] FAILED after {time.perf_counter() - started:.1f}s; later stages not run.\n{exc}", flush=True)
            return 1
        if gate.fingerprint() != code:
            print(f"[{stage}] FAILED: source changed during the run; stamps refused.", flush=True)
            return 1
        seconds = round(time.perf_counter() - started, 2)
        gate.record(stage, artifacts, {"seconds": seconds, **detail}, code)
        log.append({"stage": stage, "seconds": seconds, **detail})
        print(f"[{stage}] PASS in {seconds:.1f}s", flush=True)
    if args.through == "panel":
        stamps = json.loads((gate.STAMPS / f"{code}.json").read_text())
        record = {"fingerprint": code, "stages": [{"stage": s, **stamps[s]} for s in STAGES]}
        (args.output / "PIPELINE.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(log, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
