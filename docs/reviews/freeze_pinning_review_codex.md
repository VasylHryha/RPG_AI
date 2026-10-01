Verdict: **ACCEPTED**.

Reviewer family: Codex
Reviewer model: gpt-6
Date: 2026-10-01

Process review of `f521c0dc783585fa010a35efcebd185540da9b75`, implementing the owner's decision to freeze ten C4-owned files and pin three shared pipeline tools. Inspected checkout: `6e8421434df1af4b4aae0243a4bb81e7025b687d`. The guard, its tests, and pre-commit wiring are unchanged from the reviewed commit. This accepts the bounded pinning change; it is not another review of C4's experiment or an acceptance of C5.

No blocking findings. All three requested properties hold under the repository's existing local enforcement model.

## Findings

**A pin cannot unfreeze C4-owned code.** `tools/accepted_freeze.py:30` defines a local, exact allowlist: `tools/milestones.py`, `tools/verify.py`, and `tools/milestone_mutation.py`. `pinned_inventory()` rejects every other path before reading its historical contents. Independent probes rejected each of the ten actual C4-owned paths, including the manifest, milestone configuration, tests, `pyproject.toml`, and `uv.lock`. The guard also requires disjoint frozen/pinned inventories whose combined path-to-digest mapping equals the committed receipt's entire `file_hashes` mapping (`:132`). Omitting a file, overlapping inventories, or substituting its hash cannot grant an exception. Frozen files and the receipt continue to be checked separately in the index and working tree (`:153`).

**A committed pin cannot be dropped or changed.** `pinned_shared` is included in `FIELDS` (`:31`). The guard compares all four metadata fields against the committed HEAD entry in both proposed snapshots (`:103–109`). Dictionary equality covers the full commit/hash inventory. Its enforcement anchor remains HEAD even if proposed metadata is removed. Reviewer probes rejected pin deletion, null replacement, empty inventory, commit replacement, hash replacement, moving pins back into the frozen inventory, moving owned files into pins, deleting the milestone, and downgrading implementation status while deleting the pin. Each was checked both as a working edit and as a staged edit followed by restoration of the working `STATUS.json`. Restoration did not conceal the staged change.

**Pins bind the accepted historical versions.** A pin requires a full 40-character commit SHA, a nonempty shared-tool inventory, and an ancestor of HEAD (`:80–86`). The guard hashes both the receipt and every pinned Git blob at that commit (`:87–89`); the combined inventory is then checked against the committed receipt. Independent controls rejected an ancestor carrying the old receipt, a later ancestor carrying a changed tool with the same receipt, and an unrelated commit carrying otherwise matching contents. A positive control committed a subsequent shared-tool change and still passed; staged owned-code and receipt changes remained blocked even after their working files were restored.

## Actual C4 identity audit

The pinned commit is `a774d441f0409b7010a7321e52976539f48ca435`, an ancestor of the inspected HEAD. The receipt is `evidence/c4_r003/results.json`, SHA256 `5a95025fc65487e00cf1012044535745fe212077d9b2f0ed2683b5ad6b42b1ab`. Its bytes match the pinned commit, HEAD, index, and working tree, and the accepted Codex review names that same commit and digest.

All ten frozen files match their registered SHA256 in the pinned commit, HEAD, index, and working tree. Frozen and pinned inventories are disjoint and together equal all thirteen receipt entries. The pinned blobs independently hash to:

| Path | SHA256 at the pinned commit |
|---|---|
| `tools/milestones.py` | `f389ba5e7ff4d0249e53a3b0bb7d0a7600833926dd698c155956ce0632fb34af` |
| `tools/verify.py` | `5d6a986c5d1371b70d27acd3bf3923e903e6cf78ee030444b2bc94ad02ae0d75` |
| `tools/milestone_mutation.py` | `a49d4e7025d4d37aa80545815f9d038a31db73a4fc161375fd7d93b65c8baef2` |

The current three tools also match these hashes. Permission for future changes is established by the disposable-repository positive control, rather than inferred from an existing tool change in this checkout.

## Verification

- `.venv/bin/python -m pytest -q -x tests/test_accepted_freeze.py`: **18 passed in 10.95s**, including the five added tests and the actual pre-commit hook control.
- Reviewer-written `/private/tmp/test_freeze_pinning_review_codex.py`: **32 passed in 29.61s**. These comprise eighteen metadata/snapshot controls, ten actual-owned-path eligibility controls, three historical-binding controls, and one committed-tool-evolution control. Fixtures came from `tests/test_accepted_freeze.py`; all mutations used disposable repositories under pytest's temporary directory.
- `python3 tools/accepted_freeze.py`: exit **0** on the actual checkout. Independent Git-blob SHA256/inventory audit: **PASS**.
- `.githooks/pre-commit` invokes the guard first, and this checkout has `core.hooksPath=.githooks`.

No panel, smoke stage, mutation probe, or pipeline run was performed. No production code, tests, accepted evidence, freeze metadata, milestone status, or gate stamps were changed. The repository's documented limitation concerning deliberate forgery remains unchanged.

For a compact reproduction of the staged-pin-removal control, run from the repository root:

```python
import importlib.util, json, tempfile
from pathlib import Path
from tools.accepted_freeze import check

spec = importlib.util.spec_from_file_location("fixtures", "tests/test_accepted_freeze.py")
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)
with tempfile.TemporaryDirectory() as directory:
    root = fixtures.repo.__wrapped__(Path(directory))
    status, _, _ = fixtures.pin_shared_tool(root)
    path = root / "STATUS.json"
    original = json.dumps(status)
    path.write_text(original)
    fixtures.git(root, "add", "STATUS.json")
    assert check(root) == []
    fixtures.git(root, "commit", "-q", "-m", "pin fixture")
    del status["milestones"]["c9"]["pinned_shared"]
    path.write_text(json.dumps(status))
    fixtures.git(root, "add", "STATUS.json")
    path.write_text(original)
    assert any(p.startswith("index: c9 committed freeze metadata cannot be removed or changed")
               for p in check(root))
```
