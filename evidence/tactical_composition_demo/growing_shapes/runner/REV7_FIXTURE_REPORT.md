FIXTURES_FAIL

Revision 7.3 fixtures executed once at pin `3b6cf5635a29da1b16969155016655c61c534622129d3fbae30605e19fbbb551`. Standing grant: `docs/decisions/0031-owner-run-approval-policy.md`; integration review: `evidence/tactical_composition_demo/growing_shapes_review_claude/REV7_FIXTURE_READINESS.md` (READY_FOR_FIXTURES, Claude). All 68 pinned inputs matched before execution and after completion. The harness ran unchanged under `caffeinate -i`; the wrapper delegates sequencing and verdicts to `Harness.run_all` and only observes timing and saves evidence. No code defect or INVALID was recorded.

Pre-run workload estimate: 5–30 serial minutes, provisional and candidate-dependent, below one hour. Source: integration report and static harness workload; no calibration benchmark or rehearsal was run. The actual stop shortened execution to 16.303344 s awake / 16.303356 s elapsed UTC (2026-10-06T11:37:00.583382+00:00 → 2026-10-06T11:37:16.886738+00:00).

N1 PASS admits F1. F1a and F1b PASS; F1c FAIL because no entry occurs by t=16 s and the required hold is not established. F1d remains descriptive. F2, F3 and F4 subsequently PASS. The implemented `F1_F4_failed` stop row blocks F5 and development; all dependent later fixtures are NOT_RUN.

| Fixture | Verdict | Start UTC | End UTC | Awake s | Elapsed UTC s |
|---|---|---|---|---:|---:|
| N1 | PASS | 2026-10-06T11:37:01.331208+00:00 | 2026-10-06T11:37:03.345824+00:00 | 2.014617 | 2.014616 |
| F1a | PASS | 2026-10-06T11:37:03.384327+00:00 | 2026-10-06T11:37:04.692359+00:00 | 1.308030 | 1.308032 |
| F1b | PASS | 2026-10-06T11:37:04.692713+00:00 | 2026-10-06T11:37:06.802403+00:00 | 2.109687 | 2.109690 |
| F1c | FAIL | 2026-10-06T11:37:06.802776+00:00 | 2026-10-06T11:37:09.580035+00:00 | 2.777255 | 2.777259 |
| F1d | DESCRIPTIVE | 2026-10-06T11:37:09.580442+00:00 | 2026-10-06T11:37:12.777219+00:00 | 3.196773 | 3.196777 |
| F1 | FAIL | 2026-10-06T11:37:03.384212+00:00 | 2026-10-06T11:37:12.873111+00:00 | 9.488894 | 9.488899 |
| F2 | PASS | 2026-10-06T11:37:13.606376+00:00 | 2026-10-06T11:37:13.945263+00:00 | 0.338888 | 0.338887 |
| F3 | PASS | 2026-10-06T11:37:13.946400+00:00 | 2026-10-06T11:37:13.947580+00:00 | 0.001180 | 0.001180 |
| F4 | PASS | 2026-10-06T11:37:13.948239+00:00 | 2026-10-06T11:37:16.766417+00:00 | 2.818174 | 2.818178 |

F1 aggregate includes F1a–d; do not add it again to those sub-fixture costs. F1a–c timestamps cover construction, integration and measurement up to final close. Fixture method costs exclude writing their compressed raw traces; total cost includes gate and receipt work through harness completion. Awake uses mach_absolute_time (excludes sleep); continuous uses mach_continuous_time; elapsed uses UTC timestamps. All per-fixture timing records are retained.

N1 criterion (9.2 + 10.3): matched h=.02 and .005 endpoints, maximum wrapped and unwrapped carrier-relative phase differences ≤.01 rad, free-position error ≤.01 m.u., both topology agreements ≥.99, pins invariant, applicable entry differences ≤.1 s (both missing passes this numerical metric).

| Case | Wrapped rad | Unwrapped rad | Position m.u. | Entry times, coarse/fine s | Nθ | Nx | Pins |
|---|---:|---:|---:|---|---:|---:|---|
| N1a | 0.00115360761 | 0.00115360761 | 9.46234125e-05 | [8.1, 8.1] | 1.0 | 1.0 | True |
| N1b | 1.61703781e-06 | 1.61703781e-06 | 3.13855604e-08 | N/A | 1.0 | 1.0 | True |
| N1c | 3.55271368e-14 | 3.55271368e-14 | 0.00100565366 | N/A | 1.0 | 1.0 | True |
| N1d | 0.000159060899 | 0.000159060899 | 0.00166597107 | N/A | 1.0 | 1.0 | True |
| N1e | 1.12741941e-05 | 1.12741941e-05 | 7.44526372e-07 | [10.5, 10.5] | 1.0 | 1.0 | True |

All five N1 cases PASS; both integrations record 160 endpoints per case. N1a records one individual fast-transient frame in each integration; the others record zero. Minimum distances (element-element / element-site; None means no pair) in coarse/fine integrations:
- N1a: [{"element_element":null,"element_site":0.5555555555556158},{"element_element":null,"element_site":0.5555555555556153}]
- N1b: [{"element_element":null,"element_site":0.5571888142436467},{"element_element":null,"element_site":0.5571888142436578}]
- N1c: [{"element_element":null,"element_site":0.5169270741929209},{"element_element":null,"element_site":0.5169270740692962}]
- N1d: [{"element_element":0.5899366103059527,"element_site":0.069882544959456},{"element_element":0.5899244186776489,"element_site":0.06987472785767235}]
- N1e: [{"element_element":0.3628202265948275,"element_site":0.8352986337541615},{"element_element":0.3628202264504896,"element_site":0.8352986345963771}]

F1a/b criterion: after the step at t=8 s, first entry into the ≤.3 rad tolerance by t=16 s, held at every endpoint to t=16 s, and effective-root path exposure ≥.8 over 1,600 world steps. F1c adds hold through t=24 s, source access ≥.8, and response persistence ≥.8 over [16,160] inclusive.

| Case | Entry s | Delay s | Required hold | Path fraction | Access fraction | Response persistence |
|---|---:|---:|---|---:|---:|---:|
| F1a | 8.6 | 0.5999999999999996 | True | 1.0 | 1.0 | N/A |
| F1b | 10.5 | 2.5 | True | 1.0 | 1.0 | N/A |
| F1c | None | None | False | 1.0 | 1.0 | 0.9993060374739764 |

F1c descriptive timing after the failed deadline: {"first_entry_anytime": 16.1, "deadline_error": 0.3056520003764174, "used_in_verdict": false}. This does not change its recorded FAIL.

Compaction geometry is measured on ordinary members, excluding O. The first-record values below are at t=.1 s, not t=0. All pins remain invariant. Full positions, phase/motion neighbour lists, distances, shortcuts and link weights remain in F1 raw evidence.

| Case | Literal initial span | t=.1 span | t=160 span | t=.1 radius | t=160 radius | Source/site distance range | Min element/element | Min element/site |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| F1a | 0 | 0 | 0 | 3.22442246 | 3.322 | [0.6765254889889079, 0.7755775416596626] | 0.580422458 | 0.676525489 |
| F1b | 1.112 | 1.0273205 | 0.72757609 | 3.16470137 | 3.12978804 | [0.8352986337541615, 0.9387336614995703] | 0.362820227 | 0.835298634 |
| F1c | 2.78 | 2.62475792 | 1.17479054 | 3.12999843 | 2.58739437 | [0.8700015660195355, 1.5681544729388146] | 0.212704665 | 0.870001566 |

F1d compares the F1b scaffold at λ=1 versus 8 descriptively; no gate cut is applied. Carrier π, motion and clock are unchanged.

| λ | Entry s | Delay s | Hold to 16 | Error at 16 rad | Effective-root fraction site0 | Output-path fraction site0 | Mean site0 exposure |
|---|---:|---:|---|---:|---:|---:|---:|
| 1.0 | None | None | False | 0.952856245 | 1.0 | 1.0 | 1 |
| 8.0 | 10.5 | 2.5 | True | 0.00313200943 | 1.0 | 1.0 | 1 |

F2 exactness criterion: empty default is exactly angle=0, magnitude=0 with no path; disconnected output phase streams must be bitwise identical with/without the input step and have no path over 16 s. Measured: empty_default=True; bitwise_identical=True; 160 phases per stream, zero path steps in both. PASS.

F3 exactness criterion: drive contribution at O is +0.0 exactly at every RK4 stage. Measured: five diagnostic substeps × four stages, all 20 output drive terms have the identical float.hex of +0.0. PASS.

F4 exactness criterion: output-channel lesion leaves zero internal phase coupling at all 20 stages; site0/oracle relay angles equal the wrapped selected drive exactly; all five native/reference assays match at 160 decisions each (angle tolerance 1e-12, magnitude/choice/path/output exact). Measured: all lesion output internal terms equal 0; site0=0.3999999999999999, oracle=1.0999999999999996. PASS.

| Assay | Decisions | Maximum angle error rad | Status |
|---|---:|---:|---|
| donor | 160 | 1.77635684e-15 | MATCH |
| intact | 160 | 0 | MATCH |
| oracle | 160 | 0 | MATCH |
| output_channel | 160 | 0 | MATCH |
| site0 | 160 | 0 | MATCH |

| Fixture | Criterion | Measured values / cost | Stop outcome |
|---|---|---|---|
| F5(i), F5(ii) | Both starts: required birth (B-out i / B-path ii), max E≥.5, A≥.3, B≥.3; checkpoints 40/45/50 | NOT_RUN: A, B, E, birth events and not-qualified fraction are null/unmeasured; no timestamps or cost | Blocked by F1c; both starts retained as NOT_RUN |
| F6 | Descriptive memory correlation and encoding/retention; 120 checkpoint copies plus 20 baseline copies | NOT_RUN; no measured correlation or cost | F5 prerequisite blocked |
| F7 | All requested control-M B1 births matched; unmatched count=0 | NOT_RUN; requested/matched/fraction null; no cost | F5 prerequisite blocked; no matching claim |
| F8 | Descriptive continued-live reward/growth, 20 move then 20 remember_static episodes | NOT_RUN; no eligibility/reward/demand measurements or cost | F5/F7 prerequisites blocked |
| F9 | Four descriptive synthetic decoder observations | NOT_RUN; no actions or cost | Earlier sequence stopped |

F5 not-qualified-window summary is NOT_RUN, never zero: no starts or valid-window denominator exists for either start. Its intended descriptive output (used_in_verdict=False) covers (0,640], (640,720], (720,800] s by qualification-check endpoint, retains small-cohort starts in the denominator, reports null without windows, and counts each fast-transient world frame once. No recovery exclusions or fraction can be inferred from N1.

Stop rows: only `F1_F4_failed=YES` fired (implementer: Block F5 and development; report). Integration/readiness mismatch, source/config/inventory mismatch, N1 failure/invalid, fixture invalid and post-result protocol change are NO. F5 failure and F7 unmatched are NOT_EVALUATED, because neither ran. All development-only rows are NOT_EVALUATED. The unchanged implemented stop output is retained in RUN_RECEIPT. Development is blocked, and no next run is started.

A7 development-run projection: partial, total NOT_QUALIFIED. The 48-training workload has 15,360,000 training world steps, 76,800 growth checks, 8,512 qualification starts, up to 327,680 snapshot assays, and up to 434,176 total assay episodes if all four tasks are usable. This includes 2,048 site-body-off episodes (128 × 16 intact trainings); donor captures add 8,192 episodes. These are workload counts, not authorization.

| Measured fixed-scaffold rate source | Awake seconds / world step | Arithmetic for 15,360,000 steps, hours |
|---|---:|---:|
| F1a | 0.000817518906 | 3.488081 |
| F1b | 0.00131855411 | 5.625831 |
| F1c | 0.00173578448 | 7.406014 |
| F1d_two_scales | 0.000998991706 | 4.262365 |
| F2 | 0.00105902513 | 4.518507 |

F4 composite rate is 0.281817362 s/assay episode (five native plus five reference assays, setup/diagnostics/relays/donor capture and measurement overhead included). Applying it mechanically to 434,176 episodes gives 33.988426 hours; the 2,048 site-body-off addition alone gives 577.161958 seconds. These are explicitly unqualified arithmetic proxies, not native evaluation rates, estimates of grown-population work, or bounds.

No qualified total is possible: live growth, B-path search, qualification, recovery/admissibility and native assays at grown populations were blocked and are unmeasured. Observer overhead is included in the rates and is not subtracted. No additional run was used to price missing stages. A7_DEVELOPMENT_COST_PROJECTION.json records the formulas and null qualified_total_hours.

Evidence: `rev7_fixture_run_20261006/RUN_RECEIPT.json` preserves the full original result and verdict (over 50 MB; excluded from delivery and indexed by SHA256); per-fixture gzip traces and MEASURED_SUMMARY.json provide small transferable evidence. PREFLIGHT_IDENTITY, START_IDENTITY, PRE_EXECUTION_SEED_INVENTORY, all timing files, EXECUTION_LOG and PRESERVATION bind the run. Outside-scope tracked bytes (6,631 files), staged diff, execution inputs and docs/PLAN_CURRENT.md remain unchanged. No training, development, evaluation panel, judging entropy, registration, code edit, fixture replay or rerun occurred.

Mandatory owner recheck: the verbatim request was sent to Claude read-only; its CLI returned Not logged in. Independent Codex fallback review found one LOW reporting issue (raw counter snapshots were not retained); the wording now accurately says per-fixture timing records are retained. Measurements, criteria, original receipt and verdict were unchanged. See rev7_fixture_run_20261006/OWNER_RECHECK_CODEX.md and OWNER_RECHECK_DISPOSITION.md; docs/PLAN_CURRENT.md was not edited under the explicit owner scope.
