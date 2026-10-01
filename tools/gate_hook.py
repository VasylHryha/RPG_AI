"""PreToolUse hook for Claude Code and Codex (same contract: JSON on stdin; exit 2 + stderr blocks).

Blocks, before they start:
  - direct runs of the recorded panel (python -m geomind.run_c1) or a mutation
    probe, unless tools/gate.py verifies every earlier stage for the current code;
  - independent-review agent launches (Claude Code Agent/Task tools) unless the
    review gate passes;
  - `git commit --no-verify`, which would skip the pre-commit evidence guard.
The gated pipeline (tools/verify_milestone.py) calls these stages as subprocesses,
which never pass through this hook, so it needs no exemption.

Standard library only, so a broken virtualenv cannot make the guard fail open.
Hooks are a guardrail; the self-guards and the git pre-commit hook back them up.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402

# Match execution, not mention: an interpreter must run the module or file.
# Editing or grepping these paths is allowed.
INTERPRETER = r"\bpython[0-9.]*\s+(?:-\S+\s+)*"
STAGES = (("panel", re.compile(INTERPRETER + r"(?:-m\s+geomind\.run_c1\b|(?:\S*/)?geomind/run_c1\.py\b)")),
          ("panel", re.compile(INTERPRETER + r"(?:-m\s+geomind\.run_c2\b|(?:\S*/)?geomind/run_c2\.py\b)")),
          ("mutation", re.compile(INTERPRETER + r"(?:\S*/)?tools/c2_mutation_probe\.py\b")),
          ("mutation", re.compile(INTERPRETER + r"(?:\S*/)?tools/mutation_probe\.py\b")),
          ("mutation", re.compile(INTERPRETER + r"(?:\S*/)?mutation_checks\.py\b.*--live")))
NO_VERIFY = re.compile(r"\bgit\b[^\n;&|]*\bcommit\b[^\n;&|]*--no-verify")


def decide(payload):
    """Return a blocking reason, or None to allow."""
    tool, data = payload.get("tool_name"), payload.get("tool_input") or {}
    if tool == "Bash":
        command = data.get("command") or ""
        if NO_VERIFY.search(command):
            return "git commit --no-verify skips the evidence guard; commit normally."
        for stage, pattern in STAGES:
            if pattern.search(command):
                milestone = "c2" if "run_c2" in pattern.pattern or "c2_mutation_probe" in pattern.pattern else "c1"
                problems = gate.check(stage, milestone=milestone) if milestone == "c2" else gate.check(stage)
                if problems:
                    return f"Gate blocked the {stage} stage. " + " ".join(problems)
    if tool in ("Agent", "Task") and "independent reviewer" in (data.get("prompt") or "").lower():
        problems = gate.check("review")
        if problems:
            return "Gate blocked the independent review. " + " ".join(problems)
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    reason = decide(payload)
    if reason:
        print(reason, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
