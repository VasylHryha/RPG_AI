"""Git commit-msg check: every commit states who produced it (agent-independent).

A commit message must carry a provenance trailer, either
  Assisted-by: <Agent>:<model>   (e.g. Assisted-by: Claude:claude-opus-5-5, Assisted-by: Codex:gpt-5-codex)
or
  Human-authored: yes
This follows the Linux kernel's Assisted-by convention, and lets the review gate
compare implementer and reviewer model families. Merge commits are exempt.
"""

import re
import sys
from pathlib import Path

TRAILER = re.compile(r"^(Assisted-by: [A-Za-z][\w.-]*:[\w.:-]+|Human-authored: yes)\s*$", re.MULTILINE)


def main():
    message = Path(sys.argv[1]).read_text()
    body = "\n".join(line for line in message.splitlines() if not line.startswith("#"))
    if body.startswith("Merge ") or TRAILER.search(body):
        return 0
    print("commit-msg blocked: add a provenance trailer, e.g. 'Assisted-by: Claude:claude-opus-5-5', "
          "'Assisted-by: Codex:<model>', or 'Human-authored: yes'.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
