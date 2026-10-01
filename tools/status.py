"""STATUS.json is the single source of milestone status; README shows a generated block.

  python3 tools/status.py --write   # regenerate the README status block from STATUS.json
  python3 tools/status.py --check   # exit 1 if the README block is stale (used by pre-commit)
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN, END = "<!-- STATUS:BEGIN (generated from STATUS.json by tools/status.py; do not edit) -->", "<!-- STATUS:END -->"


def render():
    status = json.loads((ROOT / "STATUS.json").read_text())
    lines = [BEGIN, "", f"| Milestone | Status | Revision | Outcome | Record |", "|---|---|---|---|---|"]
    for key, m in status["milestones"].items():
        record = m.get("review") or m.get("proposal") or ""
        link = f"[{Path(record).name}]({record})" if record else ""
        if m.get("cross_review"):
            link += f", [cross-review]({m['cross_review']})"
        lines.append(f"| {key.upper()}: {m['title']} | **{m['implementation']}** | {m.get('revision', '')} | {m.get('outcome', '')} | {link} |")
    lines += ["", f"Status updated {status['updated']}.", END]
    return "\n".join(lines)


def main():
    readme = ROOT / "README.md"
    text = readme.read_text()
    if BEGIN not in text or END not in text:
        print("README.md has no generated status block; run tools/status.py --write", file=sys.stderr)
        return 1
    current = text[text.index(BEGIN):text.index(END) + len(END)]
    if sys.argv[1:] == ["--write"]:
        readme.write_text(text.replace(current, render()))
        return 0
    if sys.argv[1:] == ["--check"]:
        if current != render():
            print("README status block is stale; run python3 tools/status.py --write", file=sys.stderr)
            return 1
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
