"""Git pre-commit guard (agent-independent): new panel evidence must come from the gated pipeline.

Refuses a commit that adds evidence/<milestone>_rNNN/results.json unless the same
directory holds a PIPELINE.json that:
  - covers every stage through the panel;
  - was produced for the code being committed (same tools/gate.py fingerprint);
  - is backed by stamps whose artifacts tools/gate.py re-verifies.
C1 r001-r005 predate the pipeline and are exempt.
Enable once per clone: git config core.hooksPath .githooks (bypass with --no-verify is blocked by the agent hooks).
"""

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LEGACY = {("c1", f"r{n:03d}") for n in range(1, 6)}
REQUIRED = ["preflight", "tests", "smoke", "mutation", "panel"]


def problems_for(path):
    match = re.fullmatch(r"evidence/(c\d+)_(r\d{3})/results\.json", path)
    if not match or (match[1], match[2]) in LEGACY:
        return []
    record_path = ROOT / Path(path).parent / "PIPELINE.json"
    if not record_path.exists():
        return [f"{path}: no PIPELINE.json; produce evidence with tools/verify_milestone.py"]
    record = json.loads(record_path.read_text())
    problems = []
    if [s.get("stage") for s in record.get("stages", [])] != REQUIRED:
        problems.append(f"{path}: PIPELINE.json does not cover every stage through the panel")
    milestone = match[1]
    if record.get("fingerprint") != gate.fingerprint():
        problems.append(f"{path}: PIPELINE.json was produced for different code than is being committed")
    missing = [s for s in REQUIRED if s not in gate.verified(milestone)]
    if missing:
        problems.append(f"{path}: stamped artifacts do not re-verify for: {', '.join(missing)}")
    return problems


def main():
    added = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=A"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    problems = [p for path in added for p in problems_for(path)]
    for problem in problems:
        print(f"pre-commit blocked: {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
