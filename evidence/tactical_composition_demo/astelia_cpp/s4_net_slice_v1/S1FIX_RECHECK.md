PASS — corrected-source development recheck; initial M1 finding retained below
Reviewer family: Codex
Reviewer: separate agent /root/s1fix_reviewer; same-family independent recheck, not cross-family milestone acceptance.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Scope: read-only source/evidence review of S1FIX-2, approximately ten minutes. No fights, tests, fits, source edits or PLAN_CURRENT edits. This is the owner's development recheck under decisions 0035/0036, not a C-milestone review or an empirical pilot acceptance. Fresh inventory is not sealed at this review boundary. Existing S1 receipts/raw are unchanged.

## Initial review: CHANGES_REQUIRED

## Findings

**M1 — medium, correct before host launch: stored resource projection is not revalidated against current remaining work.** `s1fix_pilot.py:205` trusts `PROJECTION.json`'s ADMITTED flag and its initial wall projection; `:219` checks only the current 5 GB floor. The sample projection at `:173–175` reserves `2 × largest sample output × remaining maximum attempts`, admits sample RSS, and stores sample receipt hashes, but collection/extension never recheck that reserve or those hashes. If another repository task consumes disk after projection, the next invocation can have more than 5 GB free and still lack space for its admitted remaining extent. If initial fights are slower than the sample estimate, extension can start while current charged wall time plus the projected remaining extent exceeds the live owner cap. The timeout limits actual wall time, but does not satisfy prospective admission of the maximum extent.

Required fix: a read-only admission check before each new physical attempt under the existing locks. Verify the stored sample receipt hashes and source/inventory identity; compute current charged time, remaining maximum attempts, sample-based remaining wall/disk reserve, live owner cap and sample RSS; refuse when any admission fails. Preserve the original projection record. Add focused synthetic-receipt tests for reduced disk and increased charge, with no fights.

No other blocking findings identified in this bounded review.

## Checked conclusions and limits

- Original target-lock counts sum to 2,682/8,222 for D2-10/M2-10 and include both arms. The diagnosis distinguishes dead-focus serialization from live command retargeting and reports initial point corruption, release-refresh lag and same-state permissions without causally assigning lost kills to one mechanism.
- Source inspection confirms pending native target identity is imposed before raw logging, locked aim is reused, command focus/shape is retained through winding, refresh happens before native aim lock at the first physical opportunity even with reaction-declined release, and illegal/expired/dead commands use explicit fallback. Reaction is included in the native body/safety gate for both script arms. Existing native range/energy/cooldown/action gates remain in place.
- The deployed wrapper takes the planner-bound `q.point` at assignment. The fixture tests compare that point to accepted command caches and executed intentions, including moving raw-derived snapshots. The immediate-only candidate filter is declared; this does not establish parity with full-army ready-only scheduling or historical full-army utility.
- The 5,453-row support replay is an independent stored-state autonomous-oracle replay, not a trajectory replay and not a new commanded-arm support-rate measurement. Its reported zero bad snaps rely on the explicit prospective physical bound and exact desired-centre candidate. The separate raw bound-tail counts (4/285) and prospective oracle change are disclosed; original pilot failures are not reclassified.
- Existing focused receipt reports 23 passing tests. Earlier failed fixture attempts are preserved. I did not rerun tests. Future source changes require one final focused change-batch run, with old records preserved.
- Dropping both zero-opportunity two-gun cells is within the owner request. Forty paired seeds, eighty maximum arm-fights, twenty timing-sample arm-fights reused within forty initial arm-fights, source/binary pins without living-document hash pins, process discovery/common locks and no automatic failed-fight retries are represented in the new host harness. The real seed inventory must be sealed after fixes and final verification.
- PLAN_CURRENT remains untouched by the explicit owner instruction. The implementer should append the M1 disposition and verification record here and preserve this original review finding.

## Reviewed hashes

- `s1fix_build.py`: `a64f20cff09c5a6d4e6440c78f561654932e8a25eadf8a08548c244a2dbb2900`
- `s1fix_controller.cpp`: `b949620d76a74d60102f041b842cb1e91ba237623bef6b48b74163f7c43d1a4a`
- `s1fix_diagnose.py`: `f4b219f12ea1dc58c3c0f8ff42cd7733c647fce1559643b144801c8787cab99a`
- `s1fix_fixture.inc`: `cf5d98dd2a079a981f57983539c79d4c71be9f038aa7ff3e5dc3cf4e25505dbf`
- `s1fix_metrics.py`: `8704c8b90734be5dd5280afc5c69e824a87407e67a1913ff50926adc24fa6af2`
- `s1fix_pilot.py`: `a0f90471a7c8ff7b4a2b79dde9733ba984381246f3c2b0372caee26030866d01`
- `s1fix_script.h`: `cd9142f49cb9956573ac7d41122cb788c867dbba6f0be818c656943e3461df93`
- `s1fix_test.py`: `f9f86edb4c680b68800a85e6f8f214a517005b7d6a821d9ba5d784ae58a08c92`
- `s1fix_trace.py`: `f06feea0d6db953a0490f76f8dbd888814a03c73c4591d1c5d322215e5b2c8c4`
- `S1_WRAPPER_DIAGNOSIS.md`: `f872bd6bc54875a4c29d093de7ef76a76b5dcf48fb3262b24f670a00b9ec7586`
- `S1_WRAPPER_DIAGNOSIS_COUNTS.json`: `149f10598bea1ea4a930da65f593d9a5f288138371993f108b8051e082b5037d`
- `S1_WRAPPER_LIFECYCLE_COUNTS.json`: `9f45e79006782dbf9adaf3080029eb057ccb0c2f077a3e97e11abc190d3263c0`
- `S1FIX_HOST.md`: `0b44ac95009c56df4673093ef7a5cc3b99eb6bf0b87f9d99c7765db9ad4829b4`
- `S1FIX_TESTS.json`: `822b3ece14bc3bcf0cb6a978e8353b0668e379aa0abadfd2b722183ed7414af1`
- `S1FIX_SUPPORT_REPLAY.json`: `dabaaa07cfa858129ac10ae22472804d9f933a7af70bc7f38e84e177832cd056`
- `fixtures/S1FIX_REPLAY.json`: `1c6c07ddc30fb1d75629fd0e6612fcd07da0027cdb6425fa0a5cc0184bd1fbd8`
- `S1FIX_BUILD.json`: `8406dae5508d8c89e5f65b6861fa4f81b1b1035fe6df9a07d33a869667ea09d3`

## Reviewer corrected-source reread: M1 closed

**PASS — bounded corrected-source development recheck.** The reviewer reread only the M1 repair and its synthetic regression cases; no fights or tests were run by the reviewer.

`s1fix_pilot.py::resource_gate` now verifies the timing-sample receipt hashes, optionally revalidates their raw bytes, computes current charged time and remaining maximum attempts, reads the live owner cap/free disk, and tightens sample wall/RSS/disk maxima using already observed attempts/receipts. It refuses over-cap projected time, insufficient full remaining disk reserve, or excessive observed RSS. The original projection stays unchanged; admission/refusal checks are appended in a separate directory. Invocation admission runs inside the common locks with raw revalidation, and each new non-sample physical attempt calls the gate again. Existing inventory admission supplies current source/build identity before these checks.

Five synthetic cases cover successful admission, disk-reserve rejection while free space remains above the floor, increased charged/observed wall-time rejection, observed RSS rejection and sample receipt hash drift. The implementer's final admission-focused test receipt remains the verification authority; this reread is source review only. Original review finding and original hashes above remain preserved. No blocking M1 issue remains in the corrected source. Native source/build and initial pilot evidence were unchanged by this repair. Fresh pilot results and cell admission remain unmeasured.

Corrected-source hashes:

- `s1fix_pilot.py`: `02c79cb7bd4dc37ab6f6ab2c8c09701ab1405da557a655a1738c8f9f1e1d6697`
- `s1fix_test.py`: `659775ebacb744c1ea9b3a79e62fb1b21063c933f6ce27e885b30be23f9db62b`

## Implementer verification disposition

M1 fixed and reviewer closed it in the corrected-source reread above. `S1FIX_RESOURCE_TESTS.json` records 8 passing admission-focused tests in 0.20 s (0.39 s coordinator), including the five new synthetic gate cases. `S1FIX_TESTS.json` retains the earlier full focused batch, 23 tests in 16.27 s. Review M1 changed only Python host admission and added admission tests; native source/build hashes are identical, so successful native fixture/support replay was not repeated. Zero fights were run. PLAN_CURRENT.md remains untouched under the owner override.

Fresh inventory sealed after correction/verification: `S1FIX_INVENTORY.json`, SHA256 `f06e39fabbb01a3d08e3993af5bf02264d71939f62a26d31b0694973f018cfec`. Forty distinct paired seeds, eighty maximum arm-fights, twenty reused sample arm-fights; all initial pilot seeds excluded. `S1FIX_PILOT_SEED_EXCLUSIONS.json` is published for future pools. Final source/build pins were admitted, unchanged native test hashes and final resource-test hashes verified, and the new physical-attempt directory is empty.
