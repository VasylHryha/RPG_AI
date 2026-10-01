"""Freeze guard controls in disposable repositories; no real receipt is changed."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from tools.accepted_freeze import check

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
