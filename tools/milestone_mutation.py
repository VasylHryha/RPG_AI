"""Generic parallel, fail-fast mutation probe for a configured milestone.

  .venv/bin/python tools/milestone_mutation.py --milestone c4 --out <new json>

The mutants module named in milestones/<id>.json must define three names:
  - MUTANTS: {name: (file, exact original text, replacement)}
  - KNOWN_BACKSTOPS: guards another tested guard compensates for
  - EXPECTED_TIMEOUTS: mutants expected to run forever

The probe refuses to start unless the cheap stages are verified, and the
unmutated suite must pass first. Each mutant runs the milestone's test command
with pytest -x in its own scratch copy. Any unexpected survivor or timeout, or a
stale pattern, fails the probe.
"""

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import milestones  # noqa: E402

ROOT = milestones.ROOT
PYTHON = sys.executable  # the interpreter that launched the probe (the project venv in practice)
COPY = ("geomind", "tests", "experiments", "tools", "milestones", "native", "pyproject.toml", "uv.lock")


def load_mutants(path):
    spec = importlib.util.spec_from_file_location("milestone_mutants", ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.MUTANTS, set(module.KNOWN_BACKSTOPS), set(module.EXPECTED_TIMEOUTS)


def test_files(cfg):
    return [a for a in cfg["stages"]["tests"]["cmd"] if str(a).startswith("tests/")]


def build_template(base, cfg):
    template = base / "template"
    template.mkdir()
    for name in COPY:
        source = ROOT / name
        if source.is_dir():
            shutil.copytree(source, template / name, ignore=shutil.ignore_patterns("__pycache__"))
        elif source.exists():
            shutil.copyfile(source, template / name)
    # Evidence files the tests read, found by scanning them.
    for test in test_files(cfg):
        for ref in re.findall(r"evidence/[^\s'\"]+", (ROOT / test).read_text()):
            if (ROOT / ref).is_file():
                (template / ref).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / ref, template / ref)
    return template


def run_suite(cwd, cfg, timeout):
    started = time.perf_counter()
    try:
        result = subprocess.run([PYTHON, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", *test_files(cfg)],
                                cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"detected": None, "timed_out": True, "seconds": time.perf_counter() - started}
    lines = [line for line in result.stdout.splitlines() if " passed" in line or " failed" in line]
    return {"detected": result.returncode != 0, "timed_out": False, "summary": lines[-1] if lines else result.stdout[-300:],
            "seconds": time.perf_counter() - started}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--milestone", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=max(1, min(8, (os.cpu_count() or 2) - 1)))
    args = parser.parse_args()
    problems = milestones.check(args.milestone, "mutation")
    if problems:
        raise SystemExit("Gate blocked the mutation probe: " + " ".join(problems))
    if args.out.exists():
        raise SystemExit(f"{args.out} exists; evidence is never overwritten")
    cfg = milestones.config(args.milestone)
    mutants, backstops, expected_timeouts = load_mutants(cfg["mutants"])
    started = time.perf_counter()
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        template = build_template(base, cfg)
        baseline = run_suite(template, cfg, 900)
        if baseline["detected"] is not False:
            raise SystemExit(f"Gate failed: the unmutated suite does not pass ({baseline.get('summary', 'timed out')})")
        timeout = max(120, int(4 * baseline["seconds"]))

        def one(item):
            name, (path, old, new) = item
            scratch = base / name
            shutil.copytree(template, scratch)
            text = (scratch / path).read_text()
            if text.count(old) != 1:
                return name, {"error": f"pattern occurs {text.count(old)} times; update {cfg['mutants']}"}
            (scratch / path).write_text(text.replace(old, new))
            outcome = run_suite(scratch, cfg, timeout)
            shutil.rmtree(scratch, ignore_errors=True)
            if outcome["timed_out"]:
                outcome["detected"] = name in expected_timeouts
            return name, outcome

        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            results = dict(pool.map(one, mutants.items()))
    survivors = sorted(n for n, r in results.items() if r.get("detected") is False)
    problems = [f"{n}: {r['error']}" for n, r in results.items() if "error" in r]
    problems += [f"{n}: unexpected timeout" for n, r in results.items() if r.get("timed_out") and n not in expected_timeouts]
    report = {"milestone": args.milestone, "fingerprint": milestones.fingerprint(args.milestone), "baseline": baseline,
              "timeout": timeout, "mutants": results, "detected": sum(r.get("detected") is True for r in results.values()),
              "total": len(results), "survivors": survivors, "unexpected_survivors": sorted(set(survivors) - backstops),
              "problems": problems, "seconds": time.perf_counter() - started}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("detected", "total", "survivors", "unexpected_survivors", "problems", "seconds")}))
    return 1 if report["unexpected_survivors"] or problems else 0


if __name__ == "__main__":
    sys.exit(main())
