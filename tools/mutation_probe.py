"""Parallel, fail-fast mutation probe for the C1 suite.

Mutants come from tools/c1_mutants.py. The probe refuses to start unless
tools/gate.py verifies the cheap stages for the current code, and the unmutated
suite must pass first. Each mutant gets its own scratch copy and runs pytest with
-x, several at a time. A timeout counts as detection only for mutants expected to
run forever. Any other timeout, any surviving non-backstop mutant, or a stale
pattern fails the probe.

Usage: .venv/bin/python tools/mutation_probe.py --out <new json path> [--jobs N] [--timeout S]
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import c1_mutants  # noqa: E402
import gate  # noqa: E402

PYTHON = str(ROOT / ".venv/bin/python")
ARCHIVED_STATES = ("evidence/c1_review/states/32_inconsistent_edge_after.json",
                   "evidence/c1_r003/states/32_bridge_w0_after.json",
                   "evidence/c1_r004/states/32_bridge_w0_queue_after.json.gz")


def build_template(base):
    template = base / "template"
    template.mkdir()
    for name in ("geomind", "tests", "experiments"):
        shutil.copytree(ROOT / name, template / name, ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("pyproject.toml", "uv.lock"):
        shutil.copyfile(ROOT / name, template / name)
    (template / "evidence/c0_review").mkdir(parents=True)
    for name in ("results.json", "ACCEPTANCE.md"):
        shutil.copyfile(ROOT / "evidence/c0_review" / name, template / "evidence/c0_review" / name)
    for archived in ARCHIVED_STATES:
        (template / archived).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / archived, template / archived)
    return template


def run_suite(cwd, timeout):
    started = time.perf_counter()
    try:
        result = subprocess.run([PYTHON, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", "tests/test_c1.py"],
                                cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"detected": None, "timed_out": True, "summary": f"timed out after {timeout} s", "seconds": time.perf_counter() - started}
    lines = [line for line in result.stdout.splitlines() if " passed" in line or " failed" in line]
    return {"detected": result.returncode != 0, "timed_out": False, "summary": lines[-1] if lines else result.stdout[-300:],
            "failed": [line.split(" - ")[0] for line in result.stdout.splitlines() if line.startswith("FAILED")],
            "seconds": time.perf_counter() - started}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=max(1, min(8, (os.cpu_count() or 2) - 1)))
    parser.add_argument("--timeout", type=int, default=None, help="per-mutant seconds (default: 4x the unmutated suite, at least 120)")
    args = parser.parse_args()
    # Self-guard for any agent or human: never start before the cheap stages are verified.
    problems = gate.check("mutation")
    if problems:
        raise SystemExit("Gate blocked the mutation probe: " + " ".join(problems))
    if args.out.exists():
        raise SystemExit(f"{args.out} exists; choose a new path (evidence is never overwritten)")
    started = time.perf_counter()
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        template = build_template(base)
        baseline = run_suite(template, 900)
        if baseline["detected"] is not False:
            raise SystemExit(f"Gate failed: the unmutated suite does not pass ({baseline['summary']})")
        # Parallel load slows every suite; size the timeout from the measured baseline.
        timeout = args.timeout or max(120, int(4 * baseline["seconds"]))

        def one(item):
            name, (path, old, new) = item
            scratch = base / name
            shutil.copytree(template, scratch)
            target = scratch / path
            text = target.read_text()
            if text.count(old) != 1:
                return name, {"error": f"pattern occurs {text.count(old)} times; update tools/c1_mutants.py"}
            target.write_text(text.replace(old, new))
            outcome = run_suite(scratch, timeout)
            shutil.rmtree(scratch, ignore_errors=True)
            if outcome["timed_out"]:
                outcome["detected"] = name in c1_mutants.EXPECTED_TIMEOUTS
            return name, outcome

        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            results = dict(pool.map(one, c1_mutants.MUTANTS.items()))
    survivors = sorted(n for n, r in results.items() if r.get("detected") is False)
    problems = [f"{n}: {r['error']}" for n, r in results.items() if "error" in r]
    problems += [f"{n}: unexpected timeout" for n, r in results.items() if r.get("timed_out") and n not in c1_mutants.EXPECTED_TIMEOUTS]
    unexpected = sorted(set(survivors) - c1_mutants.KNOWN_BACKSTOPS)
    report = {"fingerprint": gate.fingerprint(), "baseline": baseline, "jobs": args.jobs, "timeout": timeout, "mutants": results,
              "detected": sum(r.get("detected") is True for r in results.values()), "total": len(results),
              "survivors": survivors, "unexpected_survivors": unexpected, "problems": problems,
              "seconds": time.perf_counter() - started}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("detected", "total", "survivors", "unexpected_survivors", "problems", "seconds")}))
    return 1 if unexpected or problems else 0


if __name__ == "__main__":
    sys.exit(main())
