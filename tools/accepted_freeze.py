"""Check declared accepted-receipt freezes in HEAD, the index, and working files.

Metadata-bearing milestones in STATUS.json are anchored to their already
committed accepted receipt. A committed freeze cannot be removed from STATUS,
and its receipt or bound files cannot be changed even by staging a different
version and then restoring the working file. Legacy entries without freeze
metadata retain their existing checks. This guard never writes files or stamps.

Shared generic pipeline tools (tools/milestones.py TOOLING) serve every later
milestone, so an acceptance may pin them instead of freezing them:
"pinned_shared": {"commit": <sha>, "hashes": {path: sha256}}. The frozen and
pinned inventories must be disjoint and together equal the receipt's
file_hashes; pinned paths must be shared tooling; the pinned commit must be in
HEAD's history and hold the accepted receipt and every pinned file at its
recorded hash. Pinned files may then evolve in later commits, while git history
keeps the exact accepted versions.
"""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
# Shared generic pipeline tooling; equal to tools/milestones.py TOOLING (a test checks this). Kept local so the
# guard stays self-contained.
TOOLING = ("tools/milestones.py", "tools/verify.py", "tools/milestone_mutation.py")
FIELDS = ("accepted_receipt", "accepted_results_sha256", "frozen_hashes", "pinned_shared")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")


def safe_path(name):
    return (isinstance(name, str) and bool(name) and "\\" not in name
            and not PurePosixPath(name).is_absolute()
            and all(part not in ("", ".", "..") for part in name.split("/")))


def read(root, snapshot, name):
    if not safe_path(name):
        raise ValueError(f"invalid repository path {name!r}")
    if snapshot == "working":
        return (root / name).read_bytes()
    spec = f"HEAD:{name}" if snapshot == "HEAD" else f":{name}" if snapshot == "index" else f"{snapshot}:{name}"
    result = subprocess.run(["git", "show", spec], cwd=root, capture_output=True)
    if result.returncode:
        raise ValueError(f"{snapshot}: missing {name}")
    return result.stdout


def entries(root, snapshot):
    data = json.loads(read(root, snapshot, "STATUS.json"))
    milestones = data["milestones"]
    if not isinstance(milestones, dict):
        raise ValueError("STATUS.json milestones must be an object")
    return milestones


def declared(entry):
    return isinstance(entry, dict) and any(field in entry for field in FIELDS)


def validate_review(root, snapshot, entry, receipt, digest):
    report = read(root, snapshot, entry["review"]).decode("utf-8")
    if not report.startswith("Verdict: **ACCEPTED**.\n") or digest not in report:
        raise ValueError("acceptance review must accept and quote this receipt digest")
    family = re.search(r"^Reviewer family: (\S+)", report, re.MULTILINE)
    implementer = receipt["manifest"]["implementer_family"]
    if not family or (family[1].lower() == implementer.lower() and "SAME-FAMILY REVIEW" not in report):
        raise ValueError("acceptance review must declare an independent reviewer family")


def pinned_inventory(root, entry, receipt_path, digest):
    """Validated {path: sha256} of shared tooling pinned by commit rather than frozen ({} when absent)."""
    pinned = entry.get("pinned_shared")
    if pinned is None:
        return {}
    commit, hashes = pinned.get("commit"), pinned.get("hashes")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit) or not isinstance(hashes, dict) or not hashes:
        raise ValueError("pinned_shared needs a full commit sha and a nonempty hash inventory")
    if not set(hashes) <= set(TOOLING):
        raise ValueError("only shared pipeline tooling may be pinned instead of frozen: " + ", ".join(sorted(set(hashes) - set(TOOLING))))
    if subprocess.run(["git", "merge-base", "--is-ancestor", commit, "HEAD"], cwd=root, capture_output=True).returncode:
        raise ValueError("pinned commit is not in HEAD's history")
    for path, expected in {receipt_path: digest, **hashes}.items():
        if hashlib.sha256(read(root, commit, path)).hexdigest() != expected:
            raise ValueError(f"pinned commit does not hold the accepted version of {path}")
    return hashes


def check(root=ROOT):
    root = Path(root)
    problems, states = [], {}
    for snapshot in ("HEAD", "index", "working"):
        try:
            states[snapshot] = entries(root, snapshot)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            problems.append(f"{snapshot}: cannot validate STATUS.json: {exc}")
    if problems:
        return problems
    committed = {key: value for key, value in states["HEAD"].items() if declared(value)}
    for snapshot in ("index", "working"):
        for key, anchor in committed.items():
            proposed = states[snapshot].get(key, {})
            if not isinstance(proposed, dict) or any(proposed.get(f) != anchor.get(f) for f in FIELDS):
                problems.append(f"{snapshot}: {key} committed freeze metadata cannot be removed or changed")
    anchors = [("HEAD", key, value) for key, value in committed.items()]
    for snapshot in ("index", "working"):
        anchors.extend((snapshot, key, value) for key, value in states[snapshot].items()
                       if declared(value) and key not in committed)
    seen = set()
    for origin, key, entry in anchors:
        try:
            receipt_path = entry["accepted_receipt"]
            digest = entry["accepted_results_sha256"]
            hashes = entry["frozen_hashes"]
            if not isinstance(digest, str) or not DIGEST.fullmatch(digest):
                raise ValueError("accepted receipt digest must be SHA256")
            if not isinstance(hashes, dict) or not hashes:
                raise ValueError("freeze inventory must be a nonempty object")
            receipt_bytes = read(root, "HEAD", receipt_path)
            if hashlib.sha256(receipt_bytes).hexdigest() != digest:
                raise ValueError("accepted digest does not match the committed receipt")
            receipt = json.loads(receipt_bytes)
            if receipt.get("manifest", {}).get("milestone", "").lower() != key.lower():
                raise ValueError("accepted receipt belongs to a different milestone")
            if (receipt.get("check_status") != "PASS" or receipt.get("complete") is not True
                    or not receipt.get("gates") or not all(v is True for v in receipt["gates"].values())):
                raise ValueError("accepted receipt must be complete with passing gates")
            pinned = pinned_inventory(root, entry, receipt_path, digest)
            if set(hashes) & set(pinned) or {**hashes, **pinned} != receipt.get("file_hashes"):
                raise ValueError("freeze inventory differs from the committed receipt")
            if any(not safe_path(path) or not isinstance(h, str) or not DIGEST.fullmatch(h)
                   for path, h in hashes.items()):
                raise ValueError("invalid path or digest in freeze inventory")
            if origin != "HEAD":
                if entry.get("implementation") != "ACCEPTED":
                    raise ValueError("new freeze requires implementation ACCEPTED")
                validate_review(root, origin, entry, receipt, digest)
            identity = (key, receipt_path, digest)
            if identity in seen:
                continue
            seen.add(identity)
            for snapshot in ("index", "working"):
                proposed = states[snapshot].get(key, {})
                if isinstance(proposed, dict) and proposed.get("implementation") == "ACCEPTED":
                    try:
                        validate_review(root, snapshot, proposed, receipt, digest)
                    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
                        problems.append(f"{snapshot}: {key} invalid acceptance review: {exc}")
                for path, expected in {receipt_path: digest, **hashes}.items():
                    try:
                        actual = hashlib.sha256(read(root, snapshot, path)).hexdigest()
                        if actual != expected:
                            problems.append(f"{snapshot}: {key} accepted file changed: {path}")
                    except (OSError, ValueError) as exc:
                        problems.append(f"{snapshot}: {key} accepted file unavailable: {path}: {exc}")
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            problems.append(f"{origin}: {key} invalid acceptance freeze: {exc}")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    problems = check(args.root)
    for problem in problems:
        print(f"pre-commit blocked: {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
