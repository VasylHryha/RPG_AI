# Measured collection disk reserve fix

Owner-authorized small tooling fix, 2026-10-08, decision 0033 / review note N4.
The old collector gate required the `hard_150s.disk_allowance_bytes` allowance
(88,527,485,472 bytes in the existing projection), which includes raw-record
worst cases and converted/training storage. Collection now requires
`ceil(max(sample strata disk_bytes) * remaining sealed fights * 2) + 5,000,000,000`
free bytes. The floor is decimal 5 GB and stays available after the projected
collection. All unfinished sealed fights are counted, conservatively including
those beyond a smaller invocation's `--fights` limit.

The existing sample maximum is 18,930,573 bytes per cell/fight. With 20 completed
and 180 remaining, the reserve is 11,815,006,280 bytes. The gate records inputs,
inventory/projection hashes, required/free bytes and PASS/REFUSED in local
`RESOURCE_GATE.json`. Equality passes; less free space refuses. Existing sample,
projection freshness, owner time cap, RSS and source drift checks remain active.

This owner's collection-only reserve policy supersedes the broader collector
storage allowance in frozen `collection_CONTRACT.md` section 149. That contract
and the historical projection remain unchanged. Training/converted data require
their own resource admission.

`collection.py` was hashed by the local seal. `DISK_RESERVE_REPIN.json` records
the exact original and updated seal and hashes; only its existing `collection.py`
pin changes, and a pin for `BUILD_TOOLING_AMENDMENT.json` is added. The original
seal bytes are backed up in ignored
`_local/SEAL_BEFORE_DISK_RESERVE_FIX.json`. Inventory, entropy, binary, contract,
request generator, other source pins, sample and projection bytes are preserved.
Historical delivery/build/test receipts remain unchanged. No collection, fights,
training, new entropy or inventory regeneration is performed.

The final identity check found that historical `BUILD.json` also includes
noncompiled Python tooling/test files. The initial seal-only repin therefore
refused with `build source/object drift: .../test_collection.py`. The immutable
build receipt is now complemented by `BUILD_TOOLING_AMENDMENT.json`: it binds
the original build hash and exact before/after hashes for only `collection.py`
and `test_collection.py`. Admission checks the original hashes against the
historical build and the updated hashes against actual files. Its amendment
bytes are sealed too. No native build input, object or binary hash is amended.

## One quick separate review

Owner request sent verbatim to separate Codex reviewer `disk_gate_quick_review`:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Result: no blocking findings. Reviewer confirmed measured reserve arithmetic,
PASS/REFUSED receipt, boundary behavior and resume/completion coverage. The
documentation note about the frozen contract's broader allowance is addressed
above. Read-only check; reviewer ran no tests or fights. Same-family tooling
review under decision 0033, not scientific acceptance.

The real build-pin integration defect required a bounded follow-up check of the
amendment repair and its new synthetic admission test. Disposition recorded
below after that check.

Follow-up result: no blocking findings. Reviewer independently checked the
historical build hash, both tooling files' before/after hashes, and the amended
seal's collector/amendment hashes; all matched. The new regression covers
unamended admission, missing/valid amendments, subsequent source/generator
drift, invalid amendment baseline/build/scope, and amendment-byte seal drift.

## Validation

Focused `test_collection.py` suite runs once after the complete change/review
batch, using the existing isolated ML interpreter. Synthetic orchestration and
isolated RPC fixtures only; no collection or fights. Results recorded below.

- Focused suite once: **37 passed in 5.17 s** (process wall 6.041 s), no failures.
  Command: `_local/mlenv/bin/python -m pytest -q -x --confcutdir="$PWD"
  --basetemp="$PWD/_local/pytest_disk_reserve" test_collection.py` from this slice,
  with plugin autoload disabled and OMP/MKL/OpenBLAS threads set to 4.
  Complete test logs/receipt are in ignored `_local/disk_reserve_tests.*`.
- The subsequent build-pin defect required an admission-only code/test change.
  The 37 successful checks are not repeated. New `test_disk_reserve_admission.py`
  runs once after the repair/review batch. Final admission and protected-file
  identity results are recorded below; no real resource gate invocation or
  collection is run. Gate receipts are exercised only in synthetic tests.
- New admission regression once: **1 passed in 0.06 s** (process wall 0.448 s).
  Same isolated interpreter/pytest flags, `test_disk_reserve_admission.py` and
  dedicated `_local/pytest_disk_reserve_admission` scratch directory; complete
  logs/receipt in `_local/disk_reserve_admission_tests.*`. No further code/test
  changes after this check.
- Final read-only admission PASS: exact amended tooling admission, sealed
  derivation of all 200 requests, unchanged inventory/sample/projection hashes,
  unchanged original seal backup, and all 20 sample receipt/raw hashes verified.
  The existing collector pin changed and the build-amendment pin was added;
  all other existing pins match. Record: `_local/disk_reserve_identity.json`.

## Changed-file scope

Delivery files relative to this slice:

- `collection.py`
- `test_collection.py`
- `test_disk_reserve_admission.py`
- `BUILD_TOOLING_AMENDMENT.json`
- `DISK_RESERVE_REPIN.json`
- `DISK_RESERVE_FIX.md`

Additionally, ignored `_local/collection/SEAL.json` has the documented tooling
repin; `_local/` contains the original seal backup and verification logs/scratch.
`docs/PLAN_CURRENT.md` has an appended recheck/disposition tracking entry only;
its pre-existing dirty content is preserved and it is excluded from delivery.

`.git` is read-only under this session's sandbox. No staging/commit attempted;
the requested provenance for a later path-limited commit is
`Assisted-by: Codex:GPT-6`. The unrelated existing dirty files are preserved.
