"""Decisions of the shared Claude Code / Codex gate hook: block execution, never mere mention."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import gate_hook  # noqa: E402


@pytest.fixture(autouse=True)
def gate_closed(monkeypatch):
    monkeypatch.setattr(gate_hook.gate, "check", lambda stage: [f"{stage} prerequisites missing"])


def bash(command):
    return gate_hook.decide({"tool_name": "Bash", "tool_input": {"command": command}})


@pytest.mark.parametrize("command", [
    ".venv/bin/python -m geomind.run_c1 --output a --contract-report b",
    "uv run --locked python -m geomind.run_c1 --output a",
    "python3 -u geomind/run_c1.py --output a",
    ".venv/bin/python tools/verify_milestone.py --output a; .venv/bin/python -m geomind.run_c1 --output b",
    ".venv/bin/python tools/mutation_probe.py --out x.json",
    "python3 evidence/c1_claude_review/mutation_checks.py /tmp/s --live",
    "git commit --no-verify -m msg",
])
def test_execution_and_bypasses_are_blocked(command):
    assert bash(command)


@pytest.mark.parametrize("command", [
    ".venv/bin/python tools/verify_milestone.py --output evidence/c1_r006",
    "grep -n geomind.run_c1 README.md",
    "sed -n 1,20p geomind/run_c1.py",
    ".venv/bin/python - <<'EOF'\nedit('geomind/run_c1.py', 'old', 'new')\nEOF",
    "cat tools/mutation_probe.py",
    "git commit -m 'gate fix'",
    "ls",
])
def test_mentions_and_ordinary_commands_are_allowed(command):
    assert bash(command) is None


def test_review_agents_are_gated_by_either_tool_name():
    for tool in ("Agent", "Task"):
        assert gate_hook.decide({"tool_name": tool, "tool_input": {"prompt": "You are an Independent Reviewer ..."}})
        assert gate_hook.decide({"tool_name": tool, "tool_input": {"prompt": "Search the code"}}) is None
