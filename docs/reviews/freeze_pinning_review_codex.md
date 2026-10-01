Verdict: **ACCEPTED**.

Reviewer family: Codex
Reviewer model: gpt-6
Date: 2026-10-01

Process review of `f521c0dc783585fa010a35efcebd185540da9b75`, implementing the owner's decision to freeze ten C4-owned files and pin three shared pipeline tools. Initially inspected checkout: `6e8421434df1af4b4aae0243a4bb81e7025b687d`; owner-requested recheck followed review commit `abb1447`. The guard and pre-commit wiring remain unchanged from the reviewed commit. The recheck extends only the unfrozen guard tests and this report. This accepts the bounded pinning change; it is not another review of C4's experiment or an acceptance of C5.

No blocking enforcement findings. All three requested properties hold under the repository's existing local enforcement model. The recheck found reproducibility and historical-helper compatibility gaps, addressed below.

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

## Recheck gaps and corrections

**Temporary probes were not durable regression coverage.** The initial review's extra 32 probes existed only under `/private/tmp`. Their important controls now live in `tests/test_accepted_freeze.py`, expanded to 38 additional cases: eighteen committed-metadata/snapshot cases, ten actual C4-owned-path exclusions, three historical-binding refusals, six shared-tool/protected-file combinations, and one actual-hook rejection. Each of the three tools can now evolve in a disposable repository containing all three pins. Owned-code and receipt refusal each get a fresh fixture, so one prior staged failure cannot mask a later control. The hook test stages pin removal, restores working metadata, attempts a commit, and verifies rejection plus unchanged HEAD. Other hook stages are stubbed only in that isolated disposable test; the production hook is unchanged.

**The old review helper describes the pre-decision snapshot.** `evidence/c4_r003_review_codex/REVIEW_CHECKS.py:44` still requires the frozen inventory alone to equal all thirteen receipt entries. Its pure `acceptance_problems()` function returns `['freeze inventory']` on the current, valid C4 entry. Line 83 also requires C5–C8 to remain NOT_STARTED, while C5 is now REVIEW_READY under its separately approved work. Its identity checks require live shared tools and a live dependency fingerprint to match the old receipt, which will cease to hold after a permitted shared-tool change. The adjacent historical review likewise describes the earlier thirteen-file freeze. These are historical audit assertions, not the current status or pinning authority. They were preserved unchanged. Current process validation uses `tools/accepted_freeze.py`, `tools/status.py --check`, the durable regression controls, and the historical-blob audit below. It neither imposes the superseded freeze nor invalidates C4 when C5 proceeds.

## Verification

Initial review:

- `.venv/bin/python -m pytest -q -x tests/test_accepted_freeze.py`: **18 passed in 10.95s**, including the five added tests and the actual pre-commit hook control.
- Reviewer-written `/private/tmp/test_freeze_pinning_review_codex.py`: **32 passed in 29.61s**, subsequently made durable and expanded as described above. Fixtures came from `tests/test_accepted_freeze.py`; all mutations used disposable repositories under pytest's temporary directory.
- `python3 tools/accepted_freeze.py`: exit **0** on the actual checkout. Independent Git-blob SHA256/inventory audit: **PASS**.
- `.githooks/pre-commit` invokes the guard first, and this checkout has `core.hooksPath=.githooks`.

Owner-requested recheck:

- `.venv/bin/python -m pytest -q -x`: **228 passed in 66.10s**, including all **56** guard cases (18 existing plus 38 added).
- `python3 tools/accepted_freeze.py` and `python3 tools/status.py --check`: both exit **0**.
- Historical-blob audit: all ten frozen and three pinned C4 identities still match the accepted receipt. All **24** C1 R006 and **43** C2 R002 receipt-bound files remain unchanged. `tests/test_accepted_freeze.py` is absent from all three accepted receipt inventories and may be extended.
- The historical helper's incompatibility was reproduced by calling only its pure acceptance validator; none of its scientific checks or simulation helpers was rerun.

No panel, smoke stage, mutation probe, or pipeline run was performed in either pass. No production code, accepted evidence, freeze metadata, milestone status, or gate stamps were changed. The repository's documented limitation concerning deliberate forgery remains unchanged. The everyday suite establishes regression coverage, not a new scientific qualification or an absolute tamper-proof boundary.

For a reproducible current-state identity audit, run this with `.venv/bin/python` from the repository root. It reads accepted receipts and Git blobs; it does not execute an experiment:

```python
import hashlib, json, subprocess
from pathlib import Path
from tools.accepted_freeze import check

assert check() == []
entry = json.loads(Path("STATUS.json").read_text())["milestones"]["c4"]
receipt_bytes = Path(entry["accepted_receipt"]).read_bytes()
assert hashlib.sha256(receipt_bytes).hexdigest() == entry["accepted_results_sha256"]
receipt = json.loads(receipt_bytes)
frozen, pin = entry["frozen_hashes"], entry["pinned_shared"]
assert len(frozen) == 10 and len(pin["hashes"]) == 3
assert not set(frozen) & set(pin["hashes"])
assert {**frozen, **pin["hashes"]} == receipt["file_hashes"]
subprocess.run(["git", "merge-base", "--is-ancestor", pin["commit"], "HEAD"], check=True)
historical_receipt = subprocess.check_output(["git", "show", pin["commit"] + ":" + entry["accepted_receipt"]])
assert historical_receipt == receipt_bytes
for path, digest in receipt["file_hashes"].items():
    historical = subprocess.check_output(["git", "show", pin["commit"] + ":" + path])
    assert hashlib.sha256(historical).hexdigest() == digest, path
for revision in ("c1_r006", "c2_r002"):
    legacy = json.loads(Path("evidence", revision, "results.json").read_text())
    for path, digest in legacy["file_hashes"].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest, path
print("Accepted historical versions and current freezes verified")
```
