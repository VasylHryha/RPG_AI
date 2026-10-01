"""The generic C4+ process tooling, exercised end to end on a throwaway fake milestone "c9"."""

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ("milestones.py", "verify.py", "milestone_mutation.py", "milestone_hook.py", "milestone_precommit.py", "provenance.py")

FAKE_PANEL = '''import json, sys
from pathlib import Path
out = Path(sys.argv[sys.argv.index("--output") + 1]); out.mkdir(parents=True)
mode = Path("panel_mode.txt").read_text().strip() if Path("panel_mode.txt").exists() else "full"
coverage = {"evaluated": {"a": {"value": 1, "verdict": "PASS"}}, "not_run": {"b": "not applicable to the fake"}}
if mode == "missing":
    coverage = {"evaluated": {"a": {"value": 1, "verdict": "PASS"}}, "not_run": {}}
(out / "results.json").write_text(json.dumps({"check_status": "PASS", "gates": {"ok": True}, "endpoint_coverage": coverage}))
'''


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout


@pytest.fixture()
def repo(tmp_path):
    (tmp_path / "tools").mkdir()
    for name in TOOLS:
        shutil.copyfile(ROOT / "tools" / name, tmp_path / "tools" / name)
    (tmp_path / "geomind").mkdir()
    (tmp_path / "geomind/__init__.py").write_text("")
    (tmp_path / "geomind/fake.py").write_text("def f():\n    return 1\n")
    (tmp_path / "geomind/fake_panel.py").write_text(FAKE_PANEL)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_fake.py").write_text("import sys\nsys.path.insert(0, '.')\nfrom geomind.fake import f\n\ndef test_f():\n    assert f() == 1\n")
    (tmp_path / "tools/c9_mutants.py").write_text("MUTANTS = {'flip': ('geomind/fake.py', 'return 1', 'return 2')}\nKNOWN_BACKSTOPS = set()\nEXPECTED_TIMEOUTS = set()\n")
    (tmp_path / "tools/fake_smoke.py").write_text("import json, sys\nopen(sys.argv[1], 'w').write(json.dumps({'status': 'PASS'}))\n")
    (tmp_path / "experiments").mkdir()
    (tmp_path / "experiments/c9_manifest.json").write_text(json.dumps({"experiment_id": "geomind-c9-r4-001", "endpoints": {"a": 1, "b": 2}}))
    (tmp_path / "milestones").mkdir()
    (tmp_path / "milestones/c9.json").write_text(json.dumps({
        "milestone": "c9", "manifest": "experiments/c9_manifest.json", "evidence_prefix": "c9", "implementer_family": "Claude",
        "deps": ["geomind/*.py", "tests/test_fake.py"], "mutants": "tools/c9_mutants.py",
        "stages": {"tests": {"cmd": ["{python}", "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", "tests/test_fake.py", "--junitxml={staging}/contracts.xml"], "artifacts": ["{staging}/contracts.xml"]},
                   "smoke": {"cmd": ["{python}", "tools/fake_smoke.py", "{staging}/smoke.json"], "artifacts": ["{staging}/smoke.json"]},
                   "mutation": {"cmd": ["{python}", "tools/milestone_mutation.py", "--milestone", "{milestone}", "--out", "{staging}/mutation.json", "--jobs", "1"], "artifacts": ["{staging}/mutation.json"]},
                   "panel": {"cmd": ["{python}", "-m", "geomind.fake_panel", "--output", "{output}"], "artifacts": ["{output}/results.json"]}}}))
    (tmp_path / ".gitignore").write_text(".gate/\n__pycache__/\n")
    (tmp_path / "README.md").write_text("fake\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "test")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "fixture")
    return tmp_path


def run(repo, *args):
    return subprocess.run([sys.executable, *args], cwd=repo, capture_output=True, text=True)


def tool(repo, name):
    sys.path.insert(0, str(repo / "tools"))
    try:
        sys.modules.pop("milestones", None)
        sys.modules.pop(name, None)
        return __import__(name)
    finally:
        sys.path.pop(0)


def test_pipeline_runs_in_order_resumes_and_attests(repo):
    partial = run(repo, "tools/verify.py", "--milestone", "c9", "--output", "evidence/c9_r001", "--through", "smoke")
    assert partial.returncode == 0, partial.stdout + partial.stderr
    full = run(repo, "tools/verify.py", "--milestone", "c9", "--output", "evidence/c9_r001")
    assert full.returncode == 0, full.stdout + full.stderr
    assert "[tests] already verified" in full.stdout and "[smoke] already verified" in full.stdout
    pipeline = json.loads((repo / "evidence/c9_r001/PIPELINE.json").read_text())
    assert [s["stage"] for s in pipeline["stages"]] == ["preflight", "tests", "smoke", "mutation", "panel"]
    mutation = json.loads((repo / "evidence/c9_r001/MUTATION.json").read_text())
    assert mutation["detected"] == mutation["total"] == 1


def test_stage_order_isolation_and_forged_artifacts(repo):
    milestones = tool(repo, "milestones")
    assert run(repo, "tools/verify.py", "--milestone", "c9", "--output", "evidence/c9_r001", "--through", "tests").returncode == 0
    assert any("earlier stages not verified" in p for p in milestones.check("c9", "panel", repo))
    # A change outside the milestone's dependencies keeps its stamps (per-milestone fingerprint).
    (repo / "README.md").write_text("changed\n")
    git(repo, "commit", "-qam", "unrelated")
    assert milestones.verified("c9", repo) == ["preflight", "tests"]
    # A forged or edited artifact breaks verification from that stage on.
    contracts = next((repo / ".gate/c9").glob("*/contracts.xml"))
    contracts.write_text(contracts.read_text() + "<!-- edited -->")
    assert milestones.verified("c9", repo) == ["preflight"]
    # A dependency change invalidates every stamp.
    (repo / "geomind/fake.py").write_text("def f():\n    return 1  # edited\n")
    git(repo, "commit", "-qam", "dependency")
    assert milestones.verified("c9", repo) == []


def test_panel_refuses_unaccounted_endpoints(repo):
    (repo / "panel_mode.txt").write_text("missing")
    result = run(repo, "tools/verify.py", "--milestone", "c9", "--output", "evidence/c9_r001")
    assert result.returncode == 1 and "neither evaluated nor listed as not run: b" in result.stdout
    milestones = tool(repo, "milestones")
    assert milestones.endpoint_coverage_problems({"endpoints": {"a": 1}}, {"endpoint_coverage": {"evaluated": {"a": {}, "x": {}}}})


def test_precommit_registration_order_pipeline_and_reviewer_family(repo):
    assert run(repo, "tools/verify.py", "--milestone", "c9", "--output", "evidence/c9_r001").returncode == 0
    git(repo, "add", "evidence/c9_r001")
    assert run(repo, "tools/milestone_precommit.py").returncode == 0
    # Changing the manifest in the same commit as its results is refused.
    manifest = repo / "experiments/c9_manifest.json"
    manifest.write_text(manifest.read_text().replace('"a": 1', '"a": 3'))
    git(repo, "add", str(manifest))
    blocked = run(repo, "tools/milestone_precommit.py")
    assert blocked.returncode == 1 and "same commit" in blocked.stderr
    git(repo, "checkout", "HEAD", "--", "experiments/c9_manifest.json")
    git(repo, "commit", "-qm", "evidence")
    digest = hashlib.sha256((repo / "evidence/c9_r001/results.json").read_bytes()).hexdigest()
    review = repo / "evidence/c9_r001_review_claude/INDEPENDENT_REVIEW.md"
    review.parent.mkdir()
    review.write_text(f"Verdict: **ACCEPTED**.\n\nReviewer family: Claude\n\nresults.json {digest}\n")
    git(repo, "add", str(review))
    same = run(repo, "tools/milestone_precommit.py")
    assert same.returncode == 1 and "both Claude" in same.stderr
    git(repo, "rm", "-q", "--cached", str(review))
    shutil.rmtree(review.parent)
    other = repo / "evidence/c9_r001_review_codex/INDEPENDENT_REVIEW.md"
    other.parent.mkdir()
    other.write_text(f"Verdict: **ACCEPTED**.\n\nReviewer family: Codex\n\nresults.json {digest}\n")
    git(repo, "add", str(other))
    assert run(repo, "tools/milestone_precommit.py").returncode == 0


def test_hook_blocks_execution_not_mention(repo):
    hook = tool(repo, "milestone_hook")

    def bash(command):
        return hook.decide({"tool_name": "Bash", "tool_input": {"command": command}})

    assert bash(".venv/bin/python -m geomind.fake_panel --output x")
    assert bash("python3 geomind/fake_panel.py --output x")
    assert bash(".venv/bin/python tools/milestone_mutation.py --milestone c9 --out m.json")
    assert bash("grep -n geomind.fake_panel README.md") is None
    assert bash(".venv/bin/python tools/verify.py --milestone c9 --output evidence/c9_r001") is None
    assert hook.decide({"tool_name": "Agent", "tool_input": {"prompt": "You are an independent reviewer of C9 R001"}})
    assert hook.decide({"tool_name": "Agent", "tool_input": {"prompt": "You are an independent reviewer of C1"}}) is None


def test_hook_allows_the_smoke_run_of_the_panel_module(repo):
    config = repo / "milestones/c9.json"
    cfg = json.loads(config.read_text())
    cfg["stages"]["smoke"]["cmd"] = ["{python}", "-m", "geomind.fake_panel", "--smoke", "--output", "{staging}/smoke.json"]
    config.write_text(json.dumps(cfg))
    hook = tool(repo, "milestone_hook")

    def bash(command):
        return hook.decide({"tool_name": "Bash", "tool_input": {"command": command}})

    assert bash(".venv/bin/python -m geomind.fake_panel --smoke --output s.json") is None
    assert bash(".venv/bin/python -m geomind.fake_panel --output x")
    assert bash(".venv/bin/python -m geomind.fake_panel --smoke --output s.json; .venv/bin/python -m geomind.fake_panel --output x")


def test_provenance_trailer(tmp_path):
    message = tmp_path / "msg"
    for text, code in (("Fix\n\nAssisted-by: Claude:claude-opus-5-5\n", 0), ("Fix\n\nAssisted-by: Codex:gpt-5-codex\n", 0),
                       ("Fix\n\nHuman-authored: yes\n", 0), ("Fix\n\nCo-Authored-By: Someone\n", 1), ("Merge branch x\n", 0)):
        message.write_text(text)
        assert subprocess.run([sys.executable, str(ROOT / "tools/provenance.py"), str(message)], capture_output=True).returncode == code


def test_readme_status_block_matches_status_json():
    assert subprocess.run([sys.executable, str(ROOT / "tools/status.py"), "--check"], capture_output=True).returncode == 0
