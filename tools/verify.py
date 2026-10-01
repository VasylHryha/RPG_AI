"""Generic gated verification pipeline for any configured milestone (C4 onward).

  .venv/bin/python tools/verify.py --milestone c4 --output evidence/c4_r001 [--through STAGE]

The stages run in order: preflight → tests → smoke → mutation → panel. Each starts
only when tools/milestones.py verifies every earlier stage for exactly the current
dependency fingerprint, and each stamps the artifact that proves it. A failure
stops the run. A rerun resumes after the last verified stage and never repeats a
passed one. The panel receipt must account for every registered endpoint
(endpoint_coverage). The committed attestation is <output>/PIPELINE.json.

Stage commands come from milestones/<id>.json and may use {python}, {staging},
{output} and {milestone}.
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import milestones  # noqa: E402

ROOT = milestones.ROOT
STAGES = ("preflight", "tests", "smoke", "mutation", "panel")


class StageFailed(Exception):
    pass


def expand(items, values):
    return [str(item).format(**values) for item in items]


def run_stage(cfg, stage, values, timeout=3600):
    spec = cfg["stages"][stage]
    result = subprocess.run(expand(spec["cmd"], values), cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise StageFailed("\n".join((result.stdout + result.stderr).strip().splitlines()[-15:]))
    artifacts = [Path(p) if Path(p).is_absolute() else ROOT / p for p in expand(spec["artifacts"], values)]
    missing = [str(a) for a in artifacts if not a.exists()]
    if missing:
        raise StageFailed("stage left no artifact: " + ", ".join(missing))
    return artifacts


def preflight(cfg, args):
    problems = milestones.tree_problems(args.milestone)
    if args.output.exists():
        problems.append(f"{args.output} already exists; evidence is never overwritten")
    manifest = json.loads((ROOT / cfg["manifest"]).read_text())
    if not isinstance(manifest.get("endpoints"), dict) or not manifest["endpoints"]:
        problems.append("manifest registers no endpoints")
    if subprocess.run(["git", "cat-file", "-e", f"HEAD:{cfg['manifest']}"], cwd=ROOT, capture_output=True).returncode != 0:
        problems.append("manifest is not committed; register it before running")
    if problems:
        raise StageFailed(" ".join(problems))
    return []


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--milestone", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--through", choices=STAGES, default="panel")
    args = parser.parse_args()
    args.output = args.output if args.output.is_absolute() else ROOT / args.output
    cfg = milestones.config(args.milestone)
    code = milestones.fingerprint(args.milestone)
    staging = milestones.stamp_path(args.milestone, code).with_suffix("")
    staging.mkdir(parents=True, exist_ok=True)
    values = {"python": sys.executable, "staging": str(staging), "output": str(args.output), "milestone": args.milestone}
    for stage in STAGES[:STAGES.index(args.through) + 1]:
        if stage != "preflight" and stage in milestones.verified(args.milestone):
            print(f"[{stage}] already verified for this code; skipped", flush=True)
            continue
        started = time.perf_counter()
        print(f"[{stage}] ...", flush=True)
        try:
            problems = milestones.check(args.milestone, stage) if stage != "preflight" else []
            if problems:
                raise StageFailed(" ".join(problems))
            artifacts = preflight(cfg, args) if stage == "preflight" else run_stage(cfg, stage, values)
            if stage == "panel":
                manifest = json.loads((ROOT / cfg["manifest"]).read_text())
                receipt = json.loads((args.output / "results.json").read_text())
                coverage = milestones.endpoint_coverage_problems(manifest, receipt)
                if coverage or receipt.get("check_status") != "PASS":
                    raise StageFailed(" ".join(coverage) or "panel receipt check_status is not PASS")
        except (StageFailed, subprocess.TimeoutExpired) as exc:
            print(f"[{stage}] FAILED after {time.perf_counter() - started:.1f}s; later stages not run.\n{exc}", flush=True)
            return 1
        if milestones.fingerprint(args.milestone) != code:
            print(f"[{stage}] FAILED: dependencies changed during the run; stamps refused.", flush=True)
            return 1
        seconds = round(time.perf_counter() - started, 2)
        milestones.record(args.milestone, stage, artifacts, {"seconds": seconds}, code)
        print(f"[{stage}] PASS in {seconds:.1f}s", flush=True)
    if args.through == "panel":
        stamps = json.loads(milestones.stamp_path(args.milestone, code).read_text())
        mutation = staging / "mutation.json"
        if mutation.exists():
            shutil.copyfile(mutation, args.output / "MUTATION.json")
        record = {"milestone": args.milestone, "revision": milestones.revision(args.milestone), "fingerprint": code,
                  "implementer_family": cfg["implementer_family"], "stages": [{"stage": s, **stamps[s]} for s in STAGES]}
        (args.output / "PIPELINE.json").write_text(json.dumps(record, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
