"""Scope the frozen legacy pre-commit check (tools/precommit.py, bound by the C1/C2 receipts) to legacy milestones.

Evidence of a milestone configured in milestones/<id>.json (C4 onward) is checked by
tools/milestone_precommit.py instead; the legacy gate does not know those milestones.
"""

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import milestones  # noqa: E402
import precommit  # noqa: E402


def legacy_paths(added, configured):
    return [p for p in added if not ((m := re.match(r"evidence/(c\d+)_", p)) and m[1] in configured)]


def main():
    added = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=A"], cwd=milestones.ROOT,
                           capture_output=True, text=True).stdout.split()
    problems = [p for path in legacy_paths(added, set(milestones.configured())) for p in precommit.problems_for(path)]
    for problem in problems:
        print(f"pre-commit blocked: {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
