"""Git pre-commit checks for configured milestones (C4 onward); agent-independent.

For newly added panel evidence, evidence/<prefix>_rNNN/results.json:
  - registration order: the manifest is already committed (in HEAD) and not
    changed in this commit, so results cannot predate their registration;
  - PIPELINE.json in the same folder matches the milestone and the current
    dependency fingerprint, covers every stage, and its stamped artifacts
    re-verify;
  - every registered endpoint is evaluated or explicitly listed as not run.

For a newly added review, evidence/<prefix>_rNNN_review_<family>/INDEPENDENT_REVIEW.md:
  - the first line is a verdict;
  - it declares "Reviewer family: <family>", matching the folder name;
  - it quotes the SHA256 of the revision's results.json it reviewed;
  - the reviewer's family differs from the implementer's, unless the review
    explicitly declares "SAME-FAMILY REVIEW" (LLM judges favor their own family).
"""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import milestones  # noqa: E402

ROOT = milestones.ROOT
STAGES = ["preflight", "tests", "smoke", "mutation", "panel"]


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def by_prefix():
    return {milestones.config(m)["evidence_prefix"]: m for m in milestones.configured()}


def panel_problems(path, milestone):
    cfg, folder = milestones.config(milestone), (ROOT / path).parent
    problems = []
    if git("cat-file", "-e", f"HEAD:{cfg['manifest']}").returncode != 0:
        problems.append(f"{path}: manifest {cfg['manifest']} was not committed before its results")
    if cfg["manifest"] in git("diff", "--cached", "--name-only").stdout.split():
        problems.append(f"{path}: the manifest changes in the same commit as its results")
    record = folder / "PIPELINE.json"
    if not record.exists():
        return problems + [f"{path}: no PIPELINE.json; produce evidence with tools/verify.py"]
    pipeline = json.loads(record.read_text())
    if pipeline.get("milestone") != milestone or [s.get("stage") for s in pipeline.get("stages", [])] != STAGES:
        problems.append(f"{path}: PIPELINE.json does not cover every stage for {milestone}")
    if pipeline.get("fingerprint") != milestones.fingerprint(milestone):
        problems.append(f"{path}: PIPELINE.json was produced for different code than is being committed")
    missing = [s for s in STAGES if s not in milestones.verified(milestone)]
    if missing:
        problems.append(f"{path}: stamped artifacts do not re-verify for: {', '.join(missing)}")
    manifest = json.loads((ROOT / cfg["manifest"]).read_text())
    problems += [f"{path}: {p}" for p in milestones.endpoint_coverage_problems(manifest, json.loads((ROOT / path).read_text()))]
    return problems


def review_problems(path, milestone, family):
    cfg, text = milestones.config(milestone), (ROOT / path).read_text()
    problems = []
    if not re.match(r"Verdict: \*\*(ACCEPTED|CHANGES_REQUIRED)\*\*\.", text):
        problems.append(f"{path}: first line must be the verdict")
    declared = re.search(r"^Reviewer family: (\S+)", text, re.MULTILINE)
    if not declared or declared[1].lower() != family.lower():
        problems.append(f"{path}: must declare 'Reviewer family: {family}' (matching its folder)")
    results = ROOT / Path(path).parent.parent / Path(path).parent.name.split("_review_")[0] / "results.json"
    if not results.exists() or hashlib.sha256(results.read_bytes()).hexdigest() not in text:
        problems.append(f"{path}: must quote the SHA256 of the reviewed {results.relative_to(ROOT)}")
    if family.lower() == cfg["implementer_family"].lower() and "SAME-FAMILY REVIEW" not in text:
        problems.append(f"{path}: reviewer and implementer are both {cfg['implementer_family']}; use the other family or declare SAME-FAMILY REVIEW")
    return problems


def main():
    prefixes = by_prefix()
    problems = []
    for path in git("diff", "--cached", "--name-only", "--diff-filter=A").stdout.split():
        panel = re.fullmatch(r"evidence/(c\d+)_(r\d{3})/results\.json", path)
        review = re.fullmatch(r"evidence/(c\d+)_(r\d{3})_review_([A-Za-z]+)/INDEPENDENT_REVIEW\.md", path)
        if panel and panel[1] in prefixes:
            problems += panel_problems(path, prefixes[panel[1]])
        if review and review[1] in prefixes:
            problems += review_problems(path, prefixes[review[1]], review[3])
    for problem in problems:
        print(f"pre-commit blocked: {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
