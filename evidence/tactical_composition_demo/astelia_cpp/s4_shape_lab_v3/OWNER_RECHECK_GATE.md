RECHECK_COMPLETE — findings resolved in the inspected sources; focused tests and preparation remain the implementer's next steps.

Reviewer family: Codex
Reviewer: separate Codex agent
Date: 2026-10-08
Repository HEAD at review: `f9889e34ffc8c59a878dd3f4066fcd969df9c534`
Baseline: sealed `s4_shape_lab_v2` from `d4b8dbc`.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

This is the same-family owner recheck explicitly requested for the bounded process-gate implementation. It is not a cross-family milestone acceptance review or permission to run fights. I read AGENTS.md, the v2 declaration/source/tests/README, and all v3 sources, and inspected their differences. I ran no tests, calibration, drill, series, or native admission. A read-only `ps` inspection was unavailable in this sandbox, so live host discovery has not been established by this review.

## Findings and inspected disposition

1. **Repository-owned basename arguments were omitted.** `/foreign/astelia_native --input request.json` with an existing `request.json` in this repository's process cwd must wait, even though the argument has neither a slash nor a `.py` suffix. The implementer now considers non-option arguments and requires existence for bare relative names. The corresponding regression also excludes URL strings from filesystem ownership inference.
2. **Bare native PATH executables were omitted.** `tactics_lab_host --metrics` may execute this repository's `build/tactics_lab_host` without that basename existing in the process cwd. The implementer now queries that target PID's `lsof` text mappings and selects the native executable basename, excluding unrelated libraries. Missing or ambiguous executable identification stops as UNAVAILABLE. Mock regressions cover repository, foreign and encoded Claude scratch executable paths, unrelated repository libraries, and lookup failure.
3. **Literal equals characters in paths were corrupted.** `/Users/new/RiderProjects/ai_RPG_test/a=b/tactics_lab_host` and `--input=/Users/new/RiderProjects/ai_RPG_test/a=b/request.json` previously lost part of the literal path. The implementer now splits only option/value arguments once and leaves filesystem path values intact. Both forms have regressions.
4. **A copied README sentence incorrectly named v2 as the new binary-reuse version.** It now names v3.

All four findings are resolved in the source hashes below. No remaining blocking finding was identified for the authorized scope. The implementer must run the focused tests once after this completed change batch and then `lab.py prepare`; this review does not substitute for either check.

## Scope and preservation checks

- The heavy-candidate regex is unchanged from v2. Ownership now uses the resolved repository boundary or the exact `-Users-new-RiderProjects-ai-RPG-test` component within a Claude scratch directory. Foreign Astelia scratch paths and prefix lookalikes are excluded. Symlink resolution and relative process cwd handling have focused fixtures.
- PROCESS_GATE.json records raw discovery, repository matches, deliberately ignored foreign candidates with reasons, and unresolved candidates. CLEAR proceeds when only foreign candidates remain; ACTIVE still waits 30 seconds; malformed discovery and failed required resolution stop as UNAVAILABLE.
- v1/v2 tracked sources and evidence have no diff. The v2 lab SHA256 matches the sealed `d4b8dbc` source. v3 metrics.py and replays.py are byte-identical to v2. Report changes name v3, the repository-scoped gate, and this recheck/disposition.
- The v1 admitted binary and passing checks are reused through the same imports and admission rules. Preparation additionally validates v2's ledger hash, excludes v1/v2 entropy, and pins the v2 declaration and ledger as inputs. The forced-collision fixture covers both generations and verifies inherited checks/binary identity without fights.
- CAP_PATH is still `../s4_shape_lab_v1/raw/LAB_CAP.json`; its current local owner setting is 10800 seconds. The calibrate/run timing, cap, projection, completed-fight reuse, interruption, caffeinate, request, metric and report rules have no functional change beyond process ownership scoping.
- No concurrent `s4_react_adapter_v1` or `docs/PLAN_CURRENT.md` file was edited by this reviewer. The only reviewer write is this file.

## Reviewed v3 SHA256 identities

| File | SHA256 |
|---|---|
| README.md | `835a02f405c6bf2ce9d502e0ca31da28f0ed32f6f112b5042b68bceebc97de9d` |
| lab.py | `1f65f552a80728910ae28ff0ca262ddc197fa9eb44ba0ea8cbdbd74a63f0bac3` |
| test_lab.py | `e726f9e9522f5061c95dc04883b9d701721dbfc09c91bf2fd80b392559dedc2f` |
| report.py | `327670c0a905dc89838c2cd0887c11fd7c66ab9f55ac0d9dcb405e08b602f65a` |
| metrics.py | `2cb718964ecce645767096f801b803abbbc579939016199af2daa71e0830939f` |
| replays.py | `f3305577f448752cdfc971aa859a4cb2ed2173bc89212857308266baa878af75` |
| .gitignore | `eafb1b84bf0a870ad62c6084323d4a01f7d3dd0c0e274c748fb23fe4e5b806fb` |

Sealed v2 lab.py baseline: `68cb24555885e216435901334d0d0f88b77187071c8a8477ba0c6d86a137e3fa`.

## Post-validation delivery recheck, 2026-10-08

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Disposition: **RECHECK_COMPLETE — no additional blocking findings.** I statically inspected the completed test/preparation logs and receipts, the sealed declaration/check/build identities, fresh entropy and the process-gate snapshot. I did not rerun tests, preparation, process discovery, calibration, drills or series.

The test log reports `64 passed in 1.38s`; GATE_TESTS.json reports returncode 0 and measured process time 1.882931292 seconds. Test stderr is empty. PREPARE.json records returncode 0, zero fights, unchanged cap and measured process time 0.202368209 seconds. Its stdout names the same new ledger hash as the declaration and verification receipt; preparation stderr is empty.

Independent read/hash checks confirm every sealed source/input hash against disk, the actual admitted binary hash, equality with v1's binary identity, and exact inherited checks with only the v3 declaration link and inheritance label changed. The new ledger has 158 unique allocated seeds, no overlap with either v1 or v2, and distinct entropy. The cap file still contains the owner-approved 10800 seconds and matches the verification receipt's SHA256 `96064b88fdf42c0295fa6f1dbd9eff4f1796b95116dad3b35cce809425d38ea4`. There are no completed-fight receipts, compute attempts, CALIBRATION.json or RUN.json in v3.

PROCESS_GATE.json honestly records UNAVAILABLE: pgrep returned 3 with `sysmond service not found` and `Cannot get process list`. Empty matched/ignored lists in this unavailable snapshot do not establish that the host is clear. The mocked scope tests establish classifier behavior; the first Claude host invocation must perform live discovery through the ordinary gate. There is no bypass or fabricated host-ownership claim.

Reviewed receipt SHA256 identities:

| File | SHA256 |
|---|---|
| GATE_TESTS.json | `933815ab71fa8b22d2f86c1cb48bc696009db8753920f4749b227cf9e23a4ae7` |
| GATE_TESTS.stdout.log | `dd53c17d8ad638bb7bc594dd2234bf2ebbb5923dd08ef0f0b2e637004b2ba6a5` |
| GATE_TESTS.stderr.log | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| PREPARE.json | `2c5da2118d8de0ac5cf993df5526383a6fd3d91980ecd87cd33f98caace83ab8` |
| PREPARE.stdout.log | `45a3b04c1bfdb3f266e1b9b9f07b622a61fe7657fa7436a8e21f67e3a091e0e6` |
| PREPARE.stderr.log | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| PREPARE_VERIFICATION.json | `f9cdec3a3321e5773f0f2330d34e752ce73b3f52187e7ff649a737cf121e7ce6` |
| DECLARATION.json | `ab5bcf6eb0bb0ef4fef0c0575e38feb948d9ff1f4900317ac54aef21efc6bdd7` |
| CHECKS.json | `3c59c827aa646aa2402e96bc82246d36c80b58a6c3dafe3c8342651b7cf97b2b` |
| BUILD.json | `3293cbeeff779bf3311d0f9da2852acd598b530fb8b34f62cda80dfede5b6dcc` |
| PROCESS_GATE.json | `808c9bedf3500883f341566b975baa95c1c5fa2d8d36d379169ae50e29827566` |
| SCOPE_CHECK.json | `e317bf665263cc369ddfa2230a56bdf93f74702c68f17b5094ad07078012a9dd` |

The raw development seed ledger hash is `7cf9f2be7513f1f837cf876b8564b0c3dd95214c1709dadd9882e074d61f412b`; the ignored ledger was read only and remains local as designed.
