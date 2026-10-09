APPROVE_WITH_NOTES
Reviewer family: Codex (separate same-family agent; no cross-family claim)

Owner request, sent verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

The reviewer independently read the cache, native wrapper, measurement code, training/state/evaluation/calibration callers and focused checks. No blocking correctness defect was found. Lossless packets feed the same candidates.h builder with identical float64 inputs; schema identity separates old banks; prefix state never reads candidates; head/loss cadence is preserved; regenerated bank costs are included in measured optimizer/evaluation windows.

Findings and disposition:

- Report active schema-3 size separately from old schema-2/orphan storage. Fixed: the cache receipt reports active_cache_bytes (chunks plus per-fight metadata), cache_directory_bytes, and other_cache_bytes. Old evidence is preserved. The disk reserve accounts for existing files through actual free space.
- Confirm parity on real recorded window rows, beyond synthetic fixtures. Fixed: the focused check reads the four largest train/validation timing fights and compares all native candidate points/features/types/source fields at both selected-window endpoints, bitwise float64. Its TEST_ONLY receipt records sizes and limits.
- Existing coverage binds all Python sources. Disposition: rerun the ordinary coverage stage with --preserve-stale after rebuilding; no compatibility waiver or gate bypass. Baseline/index remain reusable.

Validation: 23 focused checks passed, including all five arms' identical float32 head/state outputs, label mapping, native bank ordering/features, chunk boundary and varying-length XOR restoration, lazy window isolation, reuse/corruption, malformed input refusal and recorded-row parity. Seven passed before a missing scratch-parent setup error; after creating that parent the remaining 16 passed without repeating the seven. Reported pytest time was 1.50 + 6.72 = 8.22 seconds. No code changes followed validation.

The real-host measure --round 0 --test-mode invocation stopped at the unchanged process gate (pgrep returncode 3, sysmond unavailable in the sandbox), before cache/optimizer measurement. Full-cache build seconds and regeneration-inclusive fit admission remain host work. This is a development cache correction, not behavioural acceptance or experiment qualification. PLAN_CURRENT was not touched, per the owner's instruction.
