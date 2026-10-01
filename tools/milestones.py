"""Generic, declarative milestone gate for C4 onward (standard library only).

Each milestone declares, in milestones/<id>.json:
  - the files its evidence depends on;
  - its manifest;
  - the commands of its stages and the artifact each stage leaves;
  - its mutation definitions;
  - the implementer's model family.

Stamps are stored per milestone in .gate/<id>/<fingerprint>.json. The fingerprint
hashes only that milestone's dependencies, so work on one milestone never
invalidates another's (DVC's per-stage dependency rule). Every check re-verifies
the stamped artifacts by hash and content. The committed attestation is the
PIPELINE.json that tools/verify.py writes into the evidence folder.

Accepted C1 and C2 keep their frozen legacy tooling (tools/gate.py and related
files are bound by their receipts and must not change).

  python3 tools/milestones.py check <milestone> <stage>
  python3 tools/milestones.py status <milestone>
"""

import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORDER = ("preflight", "tests", "smoke", "mutation", "panel", "review")
TOOLING = ("tools/milestones.py", "tools/verify.py", "tools/milestone_mutation.py")
CONFIG_KEYS = {"milestone", "manifest", "deps", "stages", "mutants", "implementer_family", "evidence_prefix"}


def config(milestone, root=ROOT):
    path = root / "milestones" / f"{milestone}.json"
    if not re.fullmatch(r"c\d+", milestone or "") or not path.exists():
        raise ValueError(f"No milestone config for {milestone!r}")
    cfg = json.loads(path.read_text())
    if set(cfg) != CONFIG_KEYS or cfg["milestone"] != milestone or set(cfg["stages"]) != {"tests", "smoke", "mutation", "panel"}:
        raise ValueError(f"Invalid milestone config {path.name}")
    return cfg


def configured(root=ROOT):
    return sorted(p.stem for p in (root / "milestones").glob("c*.json") if re.fullmatch(r"c\d+", p.stem))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dependency_files(milestone, root=ROOT):
    cfg = config(milestone, root)
    patterns = list(cfg["deps"]) + [cfg["manifest"], cfg["mutants"], f"milestones/{milestone}.json", *TOOLING]
    return sorted({p for pattern in patterns for p in root.glob(pattern) if p.is_file()})


def fingerprint(milestone, root=ROOT):
    listing = {str(p.relative_to(root)): sha256(p) for p in dependency_files(milestone, root)}
    return hashlib.sha256(json.dumps(listing, sort_keys=True).encode()).hexdigest()


def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True).stdout


def tree_problems(milestone, root=ROOT):
    problems = []
    if _git(root, "status", "--porcelain", "--untracked-files=no").strip():
        problems.append("tracked files have uncommitted changes; commit first")
    deps = {str(p.relative_to(root)) for p in dependency_files(milestone, root)}
    untracked = [line for line in _git(root, "ls-files", "--others", "--exclude-standard").splitlines() if line in deps]
    if untracked:
        problems.append("uncommitted dependency files: " + ", ".join(untracked))
    return problems


def stamp_path(milestone, code, root=ROOT):
    return root / ".gate" / milestone / f"{code}.json"


def record(milestone, stage, artifacts=(), detail=None, code=None, root=ROOT):
    code = code or fingerprint(milestone, root)
    path = stamp_path(milestone, code, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    stamps = json.loads(path.read_text()) if path.exists() else {}
    stamps[stage] = {"artifacts": {str(Path(a).resolve().relative_to(root)): sha256(a) for a in artifacts},
                     "commit": _git(root, "rev-parse", "HEAD").strip(), **(detail or {})}
    path.write_text(json.dumps(stamps, indent=2) + "\n")


def endpoint_coverage_problems(manifest, receipt):
    """Every registered endpoint must be evaluated or explicitly not run (the C2 lesson)."""
    registered = set((manifest.get("endpoints") or {}).keys())
    coverage = receipt.get("endpoint_coverage") or {}
    evaluated, not_run = set((coverage.get("evaluated") or {}).keys()), set((coverage.get("not_run") or {}).keys())
    problems = []
    if registered - evaluated - not_run:
        problems.append("registered endpoints neither evaluated nor listed as not run: " + ", ".join(sorted(registered - evaluated - not_run)))
    if evaluated & not_run:
        problems.append("endpoints listed as both evaluated and not run: " + ", ".join(sorted(evaluated & not_run)))
    if (evaluated | not_run) - registered:
        problems.append("coverage names unregistered endpoints: " + ", ".join(sorted((evaluated | not_run) - registered)))
    return problems


def _artifact_valid(milestone, stage, path, root):
    if path.suffix == ".xml":
        cases = list(ET.parse(path).getroot().iter("testcase"))
        return bool(cases) and not any(list(c.iter("failure")) or list(c.iter("error")) or list(c.iter("skipped")) for c in cases)
    data = json.loads(path.read_text())
    if stage == "mutation":
        return data.get("total", 0) > 0 and not data.get("unexpected_survivors") and not data.get("problems")
    if stage == "panel":
        manifest = json.loads((root / config(milestone, root)["manifest"]).read_text())
        return data.get("check_status") == "PASS" and all((data.get("gates") or {"_": False}).values()) and not endpoint_coverage_problems(manifest, data)
    return data.get("status") == "PASS"


def verified(milestone, root=ROOT):
    path = stamp_path(milestone, fingerprint(milestone, root), root)
    stamps = json.loads(path.read_text()) if path.exists() else {}
    good = []
    for stage in ORDER:
        entry = stamps.get(stage)
        if entry is None:
            break
        if any(not (root / name).exists() or sha256(root / name) != digest or not _artifact_valid(milestone, stage, root / name, root)
               for name, digest in entry.get("artifacts", {}).items()):
            break
        good.append(stage)
    return good


def revision(milestone, root=ROOT):
    experiment = json.loads((root / config(milestone, root)["manifest"]).read_text())["experiment_id"]
    match = re.search(r"-(\d{3})$", experiment)
    if not match:
        raise ValueError(f"Experiment id must end in a three-digit revision: {experiment}")
    return "r" + match[1]


def review_reports(milestone, root=ROOT):
    prefix = config(milestone, root)["evidence_prefix"]
    return sorted((root / "evidence").glob(f"{prefix}_{revision(milestone, root)}_review_*/INDEPENDENT_REVIEW.md"))


def check(milestone, stage, root=ROOT):
    """Reasons the stage must not start yet; empty when it may run."""
    problems = tree_problems(milestone, root)
    done = verified(milestone, root)
    missing = [s for s in ORDER[:ORDER.index(stage)] if s not in done]
    if missing:
        problems.append(f"{milestone}: earlier stages not verified for the current code: {', '.join(missing)}; run tools/verify.py --milestone {milestone}")
    if stage == "review" and review_reports(milestone, root):
        problems.append(f"{milestone} {revision(milestone, root)} already has an independent review; one review per revision")
    return problems


def main():
    args = sys.argv[1:]
    if len(args) == 2 and args[0] == "status":
        m = args[1]
        print(json.dumps({"milestone": m, "fingerprint": fingerprint(m), "revision": revision(m), "verified": verified(m),
                          "tree_problems": tree_problems(m)}, indent=2))
        return 0
    if len(args) == 3 and args[0] == "check" and args[2] in ORDER:
        problems = check(args[1], args[2])
        for problem in problems:
            print(f"BLOCKED ({args[1]} {args[2]}): {problem}")
        return 1 if problems else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
