"""PreToolUse hook for configured milestones (C4 onward), shared by Claude Code and Codex.

Runs alongside the frozen legacy hook (tools/gate_hook.py, which covers C1/C2).
Blocks, before they start:
  - direct runs of a milestone's recorded panel or mutation probe whose earlier
    stages are not verified for the current code (tools/milestones.py);
  - independent-review agent launches that name a milestone (e.g. "C4") whose
    review gate is closed.
Patterns are derived from milestones/<id>.json, so each new milestone is covered
by adding its config, not by editing this hook. Standard library only. Execution
is matched, not mention: editing or grepping files is allowed.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import milestones  # noqa: E402

INTERPRETER = r"\bpython[0-9.]*\s+(?:-\S+\s+)*"


def patterns(milestone):
    cfg = milestones.config(milestone)
    found = []
    panel = [str(a) for a in cfg["stages"]["panel"]["cmd"]]
    if "-m" in panel:
        module = panel[panel.index("-m") + 1]
        found.append(("panel", re.compile(INTERPRETER + rf"(?:-m\s+{re.escape(module)}\b|(?:\S*/)?{re.escape(module.replace('.', '/'))}\.py\b)")))
    found.append(("mutation", re.compile(INTERPRETER + rf"(?:\S*/)?tools/milestone_mutation\.py\b[^\n;&|]*--milestone\s+{milestone}\b")))
    return found


def decide(payload):
    tool, data = payload.get("tool_name"), payload.get("tool_input") or {}
    for milestone in milestones.configured():
        if tool == "Bash":
            command = data.get("command") or ""
            for stage, pattern in patterns(milestone):
                if pattern.search(command):
                    problems = milestones.check(milestone, stage)
                    if problems:
                        return f"Gate blocked {milestone} {stage}. " + " ".join(problems)
        if tool in ("Agent", "Task"):
            prompt = data.get("prompt") or ""
            if "independent reviewer" in prompt.lower() and re.search(rf"\b{milestone}\b", prompt, re.IGNORECASE):
                problems = milestones.check(milestone, "review")
                if problems:
                    return f"Gate blocked the {milestone} independent review. " + " ".join(problems)
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
