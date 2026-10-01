"""Freeze guard controls in disposable repositories; no real receipt is changed."""

import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from tools.accepted_freeze import TOOLING, check, pinned_inventory

ROOT = Path(__file__).resolve().parents[1]


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True)


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "test")
    (tmp_path / "geomind").mkdir()
    (tmp_path / "geomind/c9.py").write_text("answer = 1\n")
    digest = hashlib.sha256((tmp_path / "geomind/c9.py").read_bytes()).hexdigest()
    evidence = tmp_path / "evidence/c9_r001"
    evidence.mkdir(parents=True)
    receipt = {"manifest": {"implementer_family": "Claude", "milestone": "C9"},
               "check_status": "PASS", "complete": True, "gates": {"valid": True},
               "file_hashes": {"geomind/c9.py": digest}}
    (evidence / "results.json").write_text(json.dumps(receipt))
    rdigest = hashlib.sha256((evidence / "results.json").read_bytes()).hexdigest()
    review = tmp_path / "evidence/c9_r001_review_codex"
    review.mkdir()
    (review / "INDEPENDENT_REVIEW.md").write_text(f"Verdict: **ACCEPTED**.\n\nReviewer family: Codex\n\n{rdigest}\n")
    entry = {"implementation": "ACCEPTED", "review": "evidence/c9_r001_review_codex/INDEPENDENT_REVIEW.md",
             "accepted_receipt": "evidence/c9_r001/results.json", "accepted_results_sha256": rdigest,
             "frozen_hashes": receipt["file_hashes"]}
    (tmp_path / "STATUS.json").write_text(json.dumps({"milestones": {"c9": entry}}))
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "fixture")
    return tmp_path


def test_unchanged_acceptance_allows_unrelated_addition(repo):
    (repo / "notes.txt").write_text("unrelated\n")
    git(repo, "add", "notes.txt")
    assert check(repo) == []


def test_working_edit_is_blocked(repo):
    (repo / "geomind/c9.py").write_text("answer = 2\n")
    assert any("working" in p and "accepted file changed: geomind/c9.py" in p for p in check(repo))


def test_staged_edit_is_blocked_after_working_file_is_restored(repo):
    (repo / "geomind/c9.py").write_text("answer = 2\n")
    git(repo, "add", "geomind/c9.py")
    (repo / "geomind/c9.py").write_text("answer = 1\n")
    assert any("index" in p and "accepted file changed: geomind/c9.py" in p for p in check(repo))


def test_staged_deletion_is_blocked(repo):
    (repo / "geomind/c9.py").unlink()
    git(repo, "add", "geomind/c9.py")
    assert any("index" in p and "accepted file unavailable: geomind/c9.py" in p for p in check(repo))


def test_committed_freeze_cannot_be_removed(repo):
    (repo / "STATUS.json").write_text(json.dumps({"milestones": {"c9": {"implementation": "REVIEW_READY"}}}))
    git(repo, "add", "STATUS.json")
    assert any("index: c9 committed freeze metadata cannot be removed" in p for p in check(repo))


def test_forged_status_and_receipt_do_not_replace_committed_anchor(repo):
    (repo / "geomind/c9.py").write_text("answer = 2\n")
    digest = hashlib.sha256((repo / "geomind/c9.py").read_bytes()).hexdigest()
    receipt_path = repo / "evidence/c9_r001/results.json"
    receipt = json.loads(receipt_path.read_text())
    receipt["file_hashes"]["geomind/c9.py"] = digest
    receipt_path.write_text(json.dumps(receipt))
    status = json.loads((repo / "STATUS.json").read_text())
    status["milestones"]["c9"]["frozen_hashes"] = receipt["file_hashes"]
    status["milestones"]["c9"]["accepted_results_sha256"] = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    (repo / "STATUS.json").write_text(json.dumps(status))
    git(repo, "add", ".")
    problems = check(repo)
    assert any("committed freeze metadata cannot be removed or changed" in p for p in problems)
    assert any("accepted file changed: geomind/c9.py" in p for p in problems)
    assert any("accepted file changed: evidence/c9_r001/results.json" in p for p in problems)


def test_new_acceptance_requires_review_in_same_snapshot(repo):
    status = json.loads((repo / "STATUS.json").read_text())
    acceptance = status["milestones"]["c9"]
    (repo / "STATUS.json").write_text(json.dumps({"milestones": {"c9": {"implementation": "REVIEW_READY"}}}))
    git(repo, "add", "STATUS.json")
    git(repo, "commit", "-q", "-m", "pre-acceptance fixture")
    (repo / acceptance["review"]).unlink()
    git(repo, "add", acceptance["review"])
    (repo / "STATUS.json").write_text(json.dumps({"milestones": {"c9": acceptance}}))
    git(repo, "add", "STATUS.json")
    assert any("index: c9 invalid acceptance freeze" in p for p in check(repo))


def test_new_acceptance_with_matching_staged_review_passes(repo):
    status = json.loads((repo / "STATUS.json").read_text())
    (repo / "STATUS.json").write_text(json.dumps({"milestones": {"c9": {"implementation": "REVIEW_READY"}}}))
    git(repo, "add", "STATUS.json")
    git(repo, "commit", "-q", "-m", "pre-acceptance fixture")
    (repo / "STATUS.json").write_text(json.dumps(status))
    git(repo, "add", "STATUS.json")
    assert check(repo) == []


def test_existing_acceptance_rejects_changed_review_verdict(repo):
    report = repo / "evidence/c9_r001_review_codex/INDEPENDENT_REVIEW.md"
    report.write_text(report.read_text().replace("**ACCEPTED**", "**CHANGES_REQUIRED**", 1))
    git(repo, "add", str(report))
    assert any("index: c9 invalid acceptance review" in p for p in check(repo))


def test_new_acceptance_cannot_reuse_another_milestone_receipt(repo):
    status = json.loads((repo / "STATUS.json").read_text())
    status["milestones"]["c10"] = dict(status["milestones"]["c9"])
    (repo / "STATUS.json").write_text(json.dumps(status))
    git(repo, "add", "STATUS.json")
    assert any("c10" in p and "different milestone" in p for p in check(repo))


def test_failed_receipt_is_rejected_even_with_consistent_freeze_metadata(repo):
    receipt_path = repo / "evidence/c9_r001/results.json"
    receipt = json.loads(receipt_path.read_text())
    receipt["gates"]["valid"] = False
    receipt_path.write_text(json.dumps(receipt))
    digest = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    status = json.loads((repo / "STATUS.json").read_text())
    status["milestones"]["c9"]["accepted_results_sha256"] = digest
    (repo / "STATUS.json").write_text(json.dumps(status))
    report = repo / status["milestones"]["c9"]["review"]
    report.write_text(f"Verdict: **ACCEPTED**.\n\nReviewer family: Codex\n\n{digest}\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "invalid acceptance fixture")
    assert any("complete with passing gates" in p for p in check(repo))


def test_new_acceptance_rejects_same_family_review(repo):
    status = json.loads((repo / "STATUS.json").read_text())
    acceptance = status["milestones"]["c9"]
    (repo / "STATUS.json").write_text(json.dumps({"milestones": {"c9": {"implementation": "REVIEW_READY"}}}))
    git(repo, "add", "STATUS.json")
    git(repo, "commit", "-q", "-m", "pre-acceptance fixture")
    report = repo / acceptance["review"]
    report.write_text(report.read_text().replace("Reviewer family: Codex", "Reviewer family: Claude"))
    (repo / "STATUS.json").write_text(json.dumps({"milestones": {"c9": acceptance}}))
    git(repo, "add", ".")
    assert any("independent reviewer family" in p for p in check(repo))


def test_actual_precommit_hook_blocks_staged_edit(repo):
    (repo / "tools").mkdir()
    (repo / ".githooks").mkdir()
    shutil.copyfile(ROOT / "tools/accepted_freeze.py", repo / "tools/accepted_freeze.py")
    shutil.copyfile(ROOT / ".githooks/pre-commit", repo / ".githooks/pre-commit")
    (repo / ".githooks/pre-commit").chmod(0o755)
    for name in ("legacy_precommit.py", "milestone_precommit.py", "status.py"):
        (repo / "tools" / name).write_text("raise SystemExit(0)\n")
    git(repo, "config", "core.hooksPath", ".githooks")
    (repo / "geomind/c9.py").write_text("answer = 2\n")
    git(repo, "add", "geomind/c9.py")
    result = subprocess.run(["git", "commit", "-m", "should be blocked"], cwd=repo, capture_output=True, text=True)
    assert result.returncode != 0
    assert "pre-commit blocked" in result.stderr and "geomind/c9.py" in result.stderr


def pin_shared_tool(repo):
    """Turn the fixture into a C4-style acceptance whose receipt also binds a shared pipeline tool."""
    (repo / "tools").mkdir()
    (repo / "tools/milestones.py").write_text("TOOL = 1\n")
    own = hashlib.sha256((repo / "geomind/c9.py").read_bytes()).hexdigest()
    tool = hashlib.sha256((repo / "tools/milestones.py").read_bytes()).hexdigest()
    receipt_path = repo / "evidence/c9_r001/results.json"
    receipt = json.loads(receipt_path.read_text())
    receipt["file_hashes"] = {"geomind/c9.py": own, "tools/milestones.py": tool}
    receipt_path.write_text(json.dumps(receipt))
    rdigest = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    (repo / "evidence/c9_r001_review_codex/INDEPENDENT_REVIEW.md").write_text(
        f"Verdict: **ACCEPTED**.\n\nReviewer family: Codex\n\n{rdigest}\n")
    status = json.loads((repo / "STATUS.json").read_text())
    status["milestones"]["c9"] = {**status["milestones"]["c9"], "accepted_results_sha256": rdigest,
                                  "frozen_hashes": {"geomind/c9.py": own}}
    # The evidence commit carries no freeze yet; the acceptance (with its pin) is declared afterwards.
    (repo / "STATUS.json").write_text(json.dumps({"milestones": {"c9": {"implementation": "REVIEW_READY"}}}))
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "evidence")  # the disposable repository has no hooks installed
    commit = git(repo, "rev-parse", "HEAD").stdout.strip()
    status["milestones"]["c9"]["pinned_shared"] = {"commit": commit, "hashes": {"tools/milestones.py": tool}}
    return status, commit, tool


def test_pinned_shared_tool_may_evolve_while_owned_files_stay_frozen(repo):
    status, _, _ = pin_shared_tool(repo)
    (repo / "STATUS.json").write_text(json.dumps(status))
    git(repo, "add", "STATUS.json")
    assert check(repo) == []
    git(repo, "commit", "-q", "-m", "pin")
    (repo / "tools/milestones.py").write_text("TOOL = 2\n")
    git(repo, "add", "tools/milestones.py")
    assert check(repo) == []
    (repo / "geomind/c9.py").write_text("answer = 2\n")
    assert any("accepted file changed: geomind/c9.py" in p for p in check(repo))


def test_only_shared_tooling_can_be_pinned(repo):
    status, commit, tool = pin_shared_tool(repo)
    entry = status["milestones"]["c9"]
    own = entry["frozen_hashes"]["geomind/c9.py"]
    swapped = {**entry, "frozen_hashes": {"tools/milestones.py": tool},
               "pinned_shared": {"commit": commit, "hashes": {"geomind/c9.py": own}}}
    (repo / "STATUS.json").write_text(json.dumps({"milestones": {"c9": swapped}}))
    assert any("only shared pipeline tooling" in p for p in check(repo))


def test_pinned_inventory_must_complete_the_receipt_and_match_the_commit(repo):
    status, commit, tool = pin_shared_tool(repo)
    entry = status["milestones"]["c9"]
    unpinned = {k: v for k, v in entry.items() if k != "pinned_shared"}
    (repo / "STATUS.json").write_text(json.dumps({"milestones": {"c9": unpinned}}))
    assert any("freeze inventory differs" in p for p in check(repo))
    wrong = {**entry, "pinned_shared": {"commit": commit, "hashes": {"tools/milestones.py": "0" * 64}}}
    (repo / "STATUS.json").write_text(json.dumps({"milestones": {"c9": wrong}}))
    assert any("does not hold the accepted version" in p for p in check(repo))
    overlap = {**entry, "frozen_hashes": {**entry["frozen_hashes"], "tools/milestones.py": tool}}
    (repo / "STATUS.json").write_text(json.dumps({"milestones": {"c9": overlap}}))
    assert any("freeze inventory differs" in p for p in check(repo))


def test_committed_pin_cannot_be_dropped_later(repo):
    status, _, _ = pin_shared_tool(repo)
    (repo / "STATUS.json").write_text(json.dumps(status))
    git(repo, "add", "STATUS.json")
    git(repo, "commit", "-q", "-m", "pin")
    entry = {k: v for k, v in status["milestones"]["c9"].items() if k != "pinned_shared"}
    (repo / "STATUS.json").write_text(json.dumps({"milestones": {"c9": entry}}))
    assert any("cannot be removed or changed" in p for p in check(repo))


def test_guard_tooling_list_matches_the_pipeline():
    from tools import accepted_freeze, milestones
    assert tuple(accepted_freeze.TOOLING) == tuple(milestones.TOOLING)


@pytest.mark.parametrize("attack", ["drop", "null", "empty", "commit", "hash", "refreeze",
                                   "unfreeze_owned", "drop_milestone", "downgrade_and_drop"])
@pytest.mark.parametrize("snapshot", ["working", "index_restored"])
def test_committed_pin_metadata_attacks(repo, attack, snapshot):
    status, _, _ = pin_shared_tool(repo)
    status_path = repo / "STATUS.json"
    original = json.dumps(status)
    status_path.write_text(original)
    git(repo, "add", "STATUS.json")
    assert check(repo) == []
    git(repo, "commit", "-q", "-m", "pin")
    proposed = copy.deepcopy(status)
    entry = proposed["milestones"]["c9"]
    if attack == "drop":
        del entry["pinned_shared"]
    elif attack == "null":
        entry["pinned_shared"] = None
    elif attack == "empty":
        entry["pinned_shared"]["hashes"] = {}
    elif attack == "commit":
        entry["pinned_shared"]["commit"] = git(repo, "rev-parse", "HEAD").stdout.strip()
    elif attack == "hash":
        entry["pinned_shared"]["hashes"]["tools/milestones.py"] = "0" * 64
    elif attack == "refreeze":
        entry["frozen_hashes"].update(entry.pop("pinned_shared")["hashes"])
    elif attack == "unfreeze_owned":
        entry["pinned_shared"]["hashes"].update(entry["frozen_hashes"])
        entry["frozen_hashes"] = {}
    elif attack == "drop_milestone":
        del proposed["milestones"]["c9"]
    elif attack == "downgrade_and_drop":
        entry["implementation"] = "REVIEW_READY"
        del entry["pinned_shared"]
    status_path.write_text(json.dumps(proposed))
    if snapshot == "index_restored":
        git(repo, "add", "STATUS.json")
        status_path.write_text(original)
    expected = "index" if snapshot == "index_restored" else "working"
    assert any(p.startswith(expected + ": c9 committed freeze metadata cannot be removed or changed")
               for p in check(repo))


@pytest.mark.parametrize("path", sorted(json.loads((ROOT / "STATUS.json").read_text())
                                       ["milestones"]["c4"]["frozen_hashes"]))
def test_every_c4_owned_path_is_ineligible_for_pinning(repo, path):
    status, commit, _ = pin_shared_tool(repo)
    entry = status["milestones"]["c9"]
    entry["pinned_shared"] = {"commit": commit, "hashes": {path: "0" * 64}}
    with pytest.raises(ValueError, match="only shared pipeline tooling"):
        pinned_inventory(repo, entry, entry["accepted_receipt"], entry["accepted_results_sha256"])


@pytest.mark.parametrize("attack", ["old_receipt", "wrong_tool", "nonancestor"])
def test_pin_historical_binding_attacks(repo, attack):
    status, _, _ = pin_shared_tool(repo)
    entry = status["milestones"]["c9"]
    if attack == "old_receipt":
        entry["pinned_shared"]["commit"] = git(repo, "rev-parse", "HEAD~1").stdout.strip()
        expected = "does not hold the accepted version of evidence/c9_r001/results.json"
    elif attack == "wrong_tool":
        (repo / "tools/milestones.py").write_text("TOOL = 999\n")
        git(repo, "add", "tools/milestones.py")
        git(repo, "commit", "-q", "-m", "later tooling")
        entry["pinned_shared"]["commit"] = git(repo, "rev-parse", "HEAD").stdout.strip()
        expected = "does not hold the accepted version of tools/milestones.py"
    else:
        tree = git(repo, "rev-parse", "HEAD^{tree}").stdout.strip()
        entry["pinned_shared"]["commit"] = git(repo, "commit-tree", tree, "-m", "unrelated fixture history").stdout.strip()
        expected = "pinned commit is not in HEAD's history"
    (repo / "STATUS.json").write_text(json.dumps(status))
    git(repo, "add", "STATUS.json")
    assert any(expected in p for p in check(repo))


@pytest.mark.parametrize("tool_path", TOOLING)
@pytest.mark.parametrize("protected_path", ["geomind/c9.py", "evidence/c9_r001/results.json"])
def test_each_committed_tool_can_evolve_without_unfreezing_protected_files(repo, tool_path, protected_path):
    status, _, _ = pin_shared_tool(repo)
    # Bind all three tools to one synthetic evidence commit, just as C4 does.
    for path in TOOLING:
        (repo / path).write_text("TOOL = 1\n")
    receipt_path = repo / "evidence/c9_r001/results.json"
    receipt = json.loads(receipt_path.read_text())
    pinned = {path: hashlib.sha256((repo / path).read_bytes()).hexdigest() for path in TOOLING}
    receipt["file_hashes"].update(pinned)
    receipt_path.write_text(json.dumps(receipt))
    digest = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    entry = status["milestones"]["c9"]
    entry["accepted_results_sha256"] = digest
    (repo / entry["review"]).write_text(f"Verdict: **ACCEPTED**.\n\nReviewer family: Codex\n\n{digest}\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "three-tool evidence")
    entry["pinned_shared"] = {"commit": git(repo, "rev-parse", "HEAD").stdout.strip(), "hashes": pinned}
    (repo / "STATUS.json").write_text(json.dumps(status))
    git(repo, "add", "STATUS.json")
    assert check(repo) == []
    git(repo, "commit", "-q", "-m", "pin three tools")
    (repo / tool_path).write_text("TOOL = 2\n")
    git(repo, "add", tool_path)
    assert check(repo) == []
    git(repo, "commit", "-q", "-m", "later tool")
    assert check(repo) == []
    original = (repo / protected_path).read_bytes()
    (repo / protected_path).write_bytes(original + b"\n")
    git(repo, "add", protected_path)
    (repo / protected_path).write_bytes(original)
    assert any("index: c9 accepted file changed: " + protected_path in p for p in check(repo))


def test_actual_precommit_blocks_pin_removal_after_working_status_is_restored(repo):
    status, _, _ = pin_shared_tool(repo)
    original = json.dumps(status)
    (repo / "STATUS.json").write_text(original)
    git(repo, "add", "STATUS.json")
    git(repo, "commit", "-q", "-m", "pin")
    (repo / ".githooks").mkdir()
    shutil.copyfile(ROOT / "tools/accepted_freeze.py", repo / "tools/accepted_freeze.py")
    shutil.copyfile(ROOT / ".githooks/pre-commit", repo / ".githooks/pre-commit")
    (repo / ".githooks/pre-commit").chmod(0o755)
    # The other hook stages are outside this isolated freeze-guard control.
    for name in ("legacy_precommit.py", "milestone_precommit.py", "status.py"):
        (repo / "tools" / name).write_text("raise SystemExit(0)\n")
    git(repo, "config", "core.hooksPath", ".githooks")
    before = git(repo, "rev-parse", "HEAD").stdout
    del status["milestones"]["c9"]["pinned_shared"]
    (repo / "STATUS.json").write_text(json.dumps(status))
    git(repo, "add", "STATUS.json")
    (repo / "STATUS.json").write_text(original)
    result = subprocess.run(["git", "commit", "-m", "should be blocked"], cwd=repo, capture_output=True, text=True)
    assert result.returncode != 0
    assert "index: c9 committed freeze metadata cannot be removed or changed" in result.stderr
    assert git(repo, "rev-parse", "HEAD").stdout == before
