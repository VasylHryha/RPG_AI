"""Prerequisite gate for long verification stages (standard library only).

A stage may start only when every earlier stage passed for exactly the current
code. Stamps in .gate/<fingerprint>.json record each passed stage together with
the SHA256 of the artifact that proves it (test report, mutation report, panel
receipt). Every check re-verifies those artifacts, so a hand-written stamp
without matching evidence does not pass.

The fingerprint hashes the source that the evidence depends on: geomind/,
tests/, experiments/, tools/, pyproject.toml and uv.lock. Committing evidence or
documents leaves it unchanged; any code or tooling change invalidates all stamps.

  python3 tools/gate.py check <stage>   # exit 1 and list reasons if blocked
  python3 tools/gate.py status          # fingerprint and verified stages
"""

import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAMPS = ROOT / ".gate"
ORDER = ("preflight", "tests", "smoke", "mutation", "panel", "review")
SOURCE_GLOBS = ("geomind/*.py", "tests/*.py", "experiments/*.json", "tools/*.py", "native/c2/*.cpp", "pyproject.toml", "uv.lock")


def source_files():
    return sorted({p for pattern in SOURCE_GLOBS for p in ROOT.glob(pattern) if p.is_file()})


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fingerprint():
    listing = {str(p.relative_to(ROOT)): sha256(p) for p in source_files()}
    return hashlib.sha256(json.dumps(listing, sort_keys=True).encode()).hexdigest()


def stage_dir(code=None):
    return STAMPS / (code or fingerprint())


def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout


def tree_problems():
    problems = []
    if _git("status", "--porcelain", "--untracked-files=no").strip():
        problems.append("tracked files have uncommitted changes; commit first")
    untracked = [line for line in _git("ls-files", "--others", "--exclude-standard").splitlines()
                 if (ROOT / line) in set(source_files())]
    if untracked:
        problems.append("uncommitted source files would enter the fingerprint: " + ", ".join(untracked))
    return problems


def record(stage, artifacts=None, detail=None, code=None, milestone="c1"):
    """Stamp a passed stage with the SHA256 of each artifact that proves it."""
    code = code or fingerprint()
    STAMPS.mkdir(exist_ok=True)
    path = stamp_path(code, milestone)
    path.parent.mkdir(parents=True, exist_ok=True)
    stamps = json.loads(path.read_text()) if path.exists() else {}
    stamps[stage] = {"artifacts": {str(Path(a).resolve().relative_to(ROOT)): sha256(a) for a in (artifacts or [])},
                     "commit": _git("rev-parse", "HEAD").strip(), **(detail or {})}
    path.write_text(json.dumps(stamps, indent=2) + "\n")


def _artifact_valid(stage, path):
    """Content checks, so a stamp cannot point at a failing artifact."""
    if stage == "tests" and path.suffix == ".xml":
        cases = list(ET.parse(path).getroot().iter("testcase"))
        return bool(cases) and not any(list(c.iter("failure")) or list(c.iter("error")) or list(c.iter("skipped")) for c in cases)
    if stage == "mutation":
        report = json.loads(path.read_text())
        return report.get("total", 0) > 0 and not report.get("unexpected_survivors") and not report.get("problems")
    if stage == "panel" and path.name == "results.json":
        receipt = json.loads(path.read_text())
        return receipt.get("check_status") == "PASS" and all(receipt.get("gates", {}).values())
    return True


def stamp_path(code, milestone="c1"):
    if milestone not in ("c1", "c2"):
        raise ValueError("Unknown milestone")
    return STAMPS / f"{code}.json" if milestone == "c1" else STAMPS / milestone / f"{code}.json"


def verified(milestone="c1"):
    """Stages whose stamps match current artifacts; stops at the first broken link."""
    path = stamp_path(fingerprint(), milestone)
    stamps = json.loads(path.read_text()) if path.exists() else {}
    good = []
    for stage in ORDER:
        entry = stamps.get(stage)
        if entry is None:
            break
        ok = True
        for name, digest in entry.get("artifacts", {}).items():
            artifact = ROOT / name
            if not artifact.exists() or sha256(artifact) != digest or not _artifact_valid(stage, artifact):
                ok = False
        if not ok:
            break
        good.append(stage)
    return good


def revision(milestone="c1"):
    experiment = json.loads((ROOT / f"experiments/{milestone}_manifest.json").read_text())["experiment_id"]
    return "r" + experiment.rsplit("-", 1)[-1]


def check(stage, milestone="c1"):
    """Reasons the stage must not start yet; empty when it may run."""
    problems = tree_problems()
    done = verified(milestone)
    missing = [s for s in ORDER[:ORDER.index(stage)] if s not in done]
    if missing:
        runner = "tools/verify_milestone.py" if milestone == "c1" else "tools/verify_c2.py"
        problems.append(f"earlier stages not verified for the current code: {', '.join(missing)}; run {runner}")
    if stage == "review":
        report = ROOT / f"evidence/{milestone}_{revision(milestone)}_independent/INDEPENDENT_REVIEW.md"
        if report.exists():
            problems.append(f"{report.relative_to(ROOT)} already exists: one independent review per revision; fix and register a new revision instead")
    return problems


def main():
    args = sys.argv[1:]
    milestone = "c1"
    if args[:2] == ["--milestone", "c2"]:
        milestone = "c2"
        args = args[2:]
    if args == ["status"]:
        print(json.dumps({"fingerprint": fingerprint(), "milestone": milestone, "revision": revision(milestone), "verified": verified(milestone), "tree_problems": tree_problems()}, indent=2))
        return 0
    if len(args) != 2 or args[0] != "check" or args[1] not in ORDER:
        print(__doc__)
        return 2
    problems = check(args[1], milestone)
    for problem in problems:
        print(f"BLOCKED ({args[1]}): {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
