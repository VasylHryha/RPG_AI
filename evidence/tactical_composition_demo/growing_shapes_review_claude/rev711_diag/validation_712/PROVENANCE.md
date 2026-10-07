# Provenance supplement for the O-pin validation pilots (answers Codex owner-recheck R4)

**Date:** 2026-10-07. **Author:** Claude (claude-opus-5-5).
**Scope:** the 34 runs in `SUMMARY.md`. The committed start receipts (`growing_shapes/runner/rev711_pilot_*_20261007/`) are **not** edited. This file only adds what can be established now, and marks what cannot.

## 1. What the receipts bind

Each receipt's `START_IDENTITY.json` records:
- the scientific pin `pin_sha256`;
- the configuration hash;
- the commit of the approval record (`approval_record.commit`), which is the HEAD at launch.

| HEAD at launch | Scientific pin | Runs |
|---|---|---|
| `553369e` | `e66c8969…e357` (7.11) | the four earlier assays: `baseline_assay_{i,ii}`, `c2opin_assay_{i,ii}`. Also, outside this battery: `c2opin_{i,ii}`, `c3group_{i,ii}` |
| `fd21826` | `e66c8969…e357` (7.11) | the 30 battery runs (all `*_alt*`, direction, and distance runs) |

**Both groups ran at the same scientific pin,** so the metric comparison is not affected. Revision 1 of the report wrongly said that every pilot ran at `fd21826`.

**What the receipts do not bind:**
- **The pilot scripts.** `pilot_common.py`, `pilot_baseline.py` and `pilot_c2_opin.py` monkey-patch the medium (the recorder, the O-pin rule and the alternative keys). They are overlays outside the pinned scientific files, and no receipt records their bytes.
- **The pilot entropy substitution.** Each receipt's `PRE_EXECUTION_SEED_INVENTORY.json` lists the original registered inventory, not the `/altK` keys or the 13-million training worlds. Its DISJOINT status does not certify the pilot ranges; §3 below does that check by hand.

## 2. Pilot scripts: the hashes that exist, and what they prove

| Script | At `553369e` | At `fd21826` | At `47b578c` (= current bytes) |
|---|---|---|---|
| `pilot_common.py` | not tracked | `451ff72b…bce0` | `54d1f97e…c251` |
| `pilot_baseline.py` | not tracked | `c5a37efd…0f30` | `eccaea86…6627` |
| `pilot_c2_opin.py` | not tracked | `8b43dba0…4315` | `d08ac321…1e65` |

- **The four earlier assays** (HEAD `553369e`) ran while the scripts were untracked. They were committed at `fd21826`. **The exact bytes executed are unavailable.** The committed `fd21826` versions are the closest record.
- **The 30 battery runs** (HEAD `fd21826`) ran with working-tree edits that were committed together at `47b578c`:
  - the alternative keys and worlds, and the 160-decision guard, in `pilot_common.py`;
  - key-set parsing in `pilot_baseline.py`;
  - distance, key-set and direction arguments in `pilot_c2_opin.py`.
- **What is consistent with that sequence:**
  - the earlier logs lack the `keyset` field, and the later logs contain it;
  - the direction tags and the recorded O coordinates match the implemented rotations;
  - sampled trace events contain the alternative training intervals.
- **What cannot be proved:** a single later commit and result-only logs cannot independently establish the exact script bytes, or when the direction edit was made. No contemporaneous command or source snapshot was kept: the worktree has been removed, and the session scratchpad has no launch script. **These are marked unavailable.**
- **The earlier assays predate the 160-decision guard.** Their status is exact baseline metric reproduction, not full Harness.F5 equivalence (7.12 review N3).

## 3. Per-run mapping, arguments and entropy

**The mapping is machine-readable** in `STORED_ANALYSIS.json`, one row per run. Each row gives:
- the trace file and its SHA256 (these equal `RAW_FILES.json`, and `../RAW_FILES_OUTSIDE_GIT.json` for the four earlier traces);
- the log file;
- the tag, start and key set.

`analyze_stored.py` asserts each trace's A against its log's A, to binding precision.

**Invocation** (`PILOT_ASSAY=1` in every run; each script's own usage line):
- `python -m …rev711_diag.pilot_baseline <i|ii> [keyset]` for the origin control;
- `python -m …rev711_diag.pilot_c2_opin <i|ii> [distance] [keyset] [root|opposite|perp]` for C2.

**Key recipes:**
- **Key set 0:** `growth/F5/<start>/intact`, `recovery/F5/<start>/intact`, and in (i) also `medium/F5/i`.
- **Key set k = 1…4:** the same strings with the suffix `/altk`.

**Training worlds:**

| Key set | World interval |
|---|---|
| 0 | 12,000,000–12,000,049 (the registered F5 growth pool) |
| 1 | 13,100,000–13,100,049 |
| 2 | 13,200,000–13,200,049 |
| 3 | 13,300,000–13,300,049 |
| 4 | 13,400,000–13,400,049 |

- **Checked by hand** against `REV7_SEED_INVENTORY.json`: the highest registered training pool ends at 11,151,999; F5 growth is 12,000,000–12,000,049; F8 is 12,100,000–12,100,039. So the alternative intervals overlap no registered pool. That does not reserve IDs above 13 million for pilots.
- **Assays are reused:** every run's F5 assay uses `F5_PAIRS` (recipients 10,000,768–777, donors 10,000,778–787) at checkpoints 40/45/50.

**O placement per run** (`STORED_ANALYSIS.json`, `output_birth` and `final_O`): the B-out time and the pin label are recorded. The selected root's id is not recorded in these traces.

## 4. For future pilots

Before launch, bind the following in a pilot receipt:
- the pilot sources' hashes;
- the arguments and environment;
- the actual key recipes and world intervals;
- the direction and distance;
- the selected root and the unrounded pin at insertion;
- the phase or RNG branch of O's phase.

The medium-variant pilots (`../medium_variants/`) list their binaries' hashes and patches, but not the launch commands either. The same rule applies to them from now on.

## 5. Naming correction

In `SUMMARY.md` the origin rows of the seeded start (ii) are the **legacy seeded pin at (−0.5, 0)**, the literal start's O, not an origin pin. `SUMMARY.md` now says so.
