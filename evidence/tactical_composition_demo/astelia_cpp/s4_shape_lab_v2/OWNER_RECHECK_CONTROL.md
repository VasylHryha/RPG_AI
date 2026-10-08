APPROVE_WITH_NOTES
Reviewer family: Codex
Reviewer model: GPT-6
Date: 2026-10-08
Scope: source-only owner recheck of v2 runner control and the v1 continuation/local cap. No scientific acceptance or host execution certification.

## Owner request (verbatim)

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Findings and disposition

All identified source-level changes required for this scope are resolved in the reviewed sources. The implementer made the fixes; the reviewer only read sources and wrote this file.

1. **Partial report state and stale inventory wording — resolved.** V2 inherited the native build but never initially created a local BUILD receipt, causing a partial run to render NOT_RUN. Preparation now writes an explicit inherited-build receipt; report state also recognizes a declaration or completed records. The inventory avoids claiming every local file is uncommitted and names the actual v1 binary location.
2. **Series remaining-time arithmetic — resolved.** The original ten-fight bound stayed constant even after nine wins. Projection now computes each reachable remaining suffix, excludes continuations after non-wins, and applies the longest remaining sequential chain. The three-arm, one-fight-left fixture expects three pending fights, a ten-second chain and twelve projected seconds; zero remaining work projects zero. The mixed drill/series fixture correctly expects 120 seconds (20/2 + max(180/2, 90), then the declared 20% margin).
3. **Existing calibration admission — resolved.** Reopening calibration originally checked its initial remaining projection. It now derives remaining work from verified completed receipts without repeating a timing fight, allowing progress and the current cap to govern the decision.
4. **Measured wall-time provenance — resolved.** Calibration now binds the complete set of calibration attempt files by SHA256, validates closed status, kind, worker count and declaration, and checks their summed wall time against the recorded measurement. Added fixtures cover timing-file tampering and an inconsistent stored wall time.
5. **Control-flow coverage gaps — resolved in test source; execution pending.** New mocked tests cover first-only series sampling for both wins and non-wins, calibration orchestration/receipt/idempotence, cap refusal, cached completion reuse, suffix reduction and timing provenance. No drill/series/calibration execution is added to tests. Native admission tests have duration zero.
6. **Prior incomplete-cell preservation — resolved.** The implementer independently identified that an expired call could quarantine pre-existing incomplete files as retryable. The timeout wrapper now records whether files predated the call and refuses to move them. A fixture checks preservation. New partial files from a native cap timeout retain requests/claims/streams and hashes in an explicit interruption archive.

## Confirmed contracts

- The owner local file contains cap_seconds 10800, approved_by owner and date 2026-10-08; git check-ignore confirms v1 /raw/ excludes it. Missing settings default to 3600. Each invocation snapshots the exact parsed bytes and hash; the setting is excluded from preparation, source, binary and seed identities.
- V2 is a fresh version, allocating new development entropy and excluding all v1 ledger seed integers. The reviewed v1 tracked diff is only the eight-line README continuation; v1 runner, declaration, checks and committed observations remain preserved. No judging ledger is opened.
- Native engine admission and v1 capability-check provenance are inherited explicitly. Request construction, survivor placement, metrics and native code are unchanged. The host pgrep function is unchanged in the source diff.
- Calibration declares 56 first-cluster/first-orientation drill cells plus the first series fight for each of v7, forcedP16 and elite. Series sampling never advances past fight one. Full run uses identical tags/requests, validates cached receipts and resumes survivor cohorts through the ordinary series path.
- Calibration uses the same six-worker executor as the full run. The method keeps wall-time units distinct from simulated seconds, scales sample costs conservatively to the 150-second horizon, uses observed worker utilization and a 20% margin, and accounts for separate drill/series phases and sequential series limits.
- Run recomputes remaining projection and refuses above the current cap before native compute; cap pauses preserve completed receipts and retry only explicitly interrupted unfinished native fights. Unclosed attempts, identity drift and other incomplete cells stop for investigation.

## Limits and next gate

This review executed no tests, native admission, drill, series or calibration. Focused tests remain the implementer's final gate after the complete change batch. Claude must prepare/calibrate on the host, stop and ask the owner if the measured projection exceeds the local cap, and inspect PAUSED_CAP versus DONE before reporting completion. Host pgrep availability and real timing are unverified here. The per-invocation cap bounds native child execution; compression/hashing/initial metrics may finish at the boundary, while standalone report rendering is outside the compute cap. Throughput is an estimate and later tactics, survivors and host load may differ. Source edits after preparation require another version.

## Reviewed source SHA256

| File (relative to astelia_cpp) | SHA256 |
|---|---|
| s4_shape_lab_v2/lab.py | `68cb24555885e216435901334d0d0f88b77187071c8a8477ba0c6d86a137e3fa` |
| s4_shape_lab_v2/test_lab.py | `9cb2154e58934d7e970491e0a4a013154a115024c4e50f02c9430e65f4ac8cb7` |
| s4_shape_lab_v2/report.py | `b3b778350acc0e5a1f46891f748ea9c7a78936c9e343c7bfddc2a61233c12597` |
| s4_shape_lab_v2/metrics.py | `2cb718964ecce645767096f801b803abbbc579939016199af2daa71e0830939f` |
| s4_shape_lab_v2/replays.py | `f3305577f448752cdfc971aa859a4cb2ed2173bc89212857308266baa878af75` |
| s4_shape_lab_v2/README.md | `c49d997c6e2964cfed835e2341b3c86fe7515acbf51f37cec9b9c7310cb72586` |
| s4_shape_lab_v2/.gitignore | `eafb1b84bf0a870ad62c6084323d4a01f7d3dd0c0e274c748fb23fe4e5b806fb` |
| s4_shape_lab_v1/README.md | `874358a092a5c590883f226e830be31fc1c569d806bf0a8679506a3f8c6234a5` |
| s4_shape_lab_v1/lab.py | `786093f770dab015a51652db95c143fe3f7a9214ffddb2302e0a310ccec678a5` |
| s4_shape_lab_v1/test_lab.py | `e322e3c22378b9b812fddd3595caf9d71700831829d98e5d8a8df766b0463cd6` |
| s4_shape_lab_v1/DECLARATION.json | `f558ccbb6502a1db885e49b4b750533aba9cef557079dfb1e91c2e2ac6b9cd22` |
| s4_shape_lab_v1/CHECKS.json | `59341cacd3c9058322be822cc2bb5a78fdf1e24ec78de021e77d7868f8785eb1` |
| s4_shape_lab_v1/PROJECTION_INTERPRETATION.md | `73b9c0932df082e4d42252d3bd85fc9ae996da9fcdc1db27c60b83f56a420e3d` |
| s4_shape_lab_v1/SHAPE_LAB_REPORT.md | `3fecb64825e6140e44a869fb43f89ccda0ce9a8a8c8dfca550f7f0be7591f038` |

Local-setting snapshot SHA256 (review provenance only; excluded from sealed identities): `96064b88fdf42c0295fa6f1dbd9eff4f1796b95116dad3b35cce809425d38ea4`.

## Final verification addendum

The implementer's retained `CONTROL_TESTS.json` and stdout report **32 passed in 1.07 seconds**, with measured process time **1.80560825 seconds** and exit code zero. The initial attempt stopped at fixture setup after nine tests because the explicit basetemp parent did not exist; its FAIL receipt and logs remain separately preserved as `CONTROL_TESTS_ATTEMPT_01.*`. The successful rerun followed creation of the ignored parent directory, with no runner or test-source changes.

The reviewer read these receipts and logs without executing tests or project code. The sole subsequent README change adds `mkdir -p .../s4_shape_lab_v2/.pytest_cache` before the focused command; this correctly creates the missing parent under the existing ignored directory. Its reviewed hash above is updated. The source-only verdict remains APPROVE_WITH_NOTES. Fresh preparation, host calibration, the real pgrep gate and measured full-run throughput remain subsequent gates; the test PASS does not claim their completion or scientific acceptance.
