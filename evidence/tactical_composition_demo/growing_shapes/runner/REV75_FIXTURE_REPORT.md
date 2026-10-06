INVALID

Revision 7.5 fixtures started ONCE at execution pin `7a63d15064df745bfa63071473e02ffcb327901d6210c8310f5b5f8c3a330bce`; all 69 scientific inputs matched before execution and after the stop. Grant: `docs/decisions/0031-owner-run-approval-policy.md`; integration_review: `evidence/tactical_composition_demo/growing_shapes_review_claude/REV75_FIXTURE_READINESS_CONFIRMED.md` (READY_FOR_FIXTURES, Claude). New output: `rev75_fixture_run_20261006/`. Historical 7.3/7.4 reports and receipts are unchanged.

N1 and F1–F4 PASS. F5 is INVALID because the new measurement wrapper missed per-start cost records; it watched a non-executable structural `finally:` line. This observer was copied from the historical 7.4 wrapper, whose F5 path had not run. Static bytecode inspection confirmed the defect after F5 advanced to start ii. The implementer immediately stopped with SIGINT (exit 130), as instructed. No scientific engine defect is established. No code changed during execution, and no patch or rerun occurred.

F5(i) finished its calculations in memory and reached the next-start boundary, but its A/B/E, events, qualification summaries and component costs were not persisted. F5(ii) was interrupted during growth. The F5 method therefore never returned a result, and KeyboardInterrupt prevented the outer wrapper from writing its final harness receipt. OPERATOR_INTERRUPTION_RECEIPT.json explicitly describes this interrupted run; it is not a substitute passing harness receipt. F6–F9 are NOT_RUN.

Static full-harness estimate before execution: 2305.295380 s (38.421590 min), scheduling allowance 2458.981739 s (40.983029 min), below one hour. Counts include 120,000 N1 substeps (N1g included), 192,000 F1 substeps, both F5 starts, F6–F9 and qualification/recovery sensitivity. Rates reuse historical evidence with assumed multipliers/contingency; this is not a measured total or bound. DURATION_ESTIMATE.json retains all assumptions and source hashes. No rehearsal or benchmark was run.

| Fixture | Verdict/status | Start UTC | End UTC | Awake s | Elapsed UTC s |
|---|---|---|---|---:|---:|
| N1 | PASS | 2026-10-06T12:49:10.500469+00:00 | 2026-10-06T12:49:19.861342+00:00 | 9.360873 | 9.360873 |
| F1 | PASS | 2026-10-06T12:49:19.988643+00:00 | 2026-10-06T12:49:41.853837+00:00 | 21.865183 | 21.865194 |
| F1a | PASS | 2026-10-06T12:49:19.988744+00:00 | 2026-10-06T12:49:23.245811+00:00 | 3.257063 | 3.257067 |
| F1b | PASS | 2026-10-06T12:49:23.246211+00:00 | 2026-10-06T12:49:26.612441+00:00 | 3.366228 | 3.366230 |
| F1c | PASS | 2026-10-06T12:49:26.612906+00:00 | 2026-10-06T12:49:30.587683+00:00 | 3.974773 | 3.974777 |
| F1d | DESCRIPTIVE | 2026-10-06T12:49:30.588087+00:00 | 2026-10-06T12:49:41.675580+00:00 | 11.087486 | 11.087493 |
| F2 | PASS | 2026-10-06T12:49:42.648949+00:00 | 2026-10-06T12:49:43.175294+00:00 | 0.526345 | 0.526345 |
| F3 | PASS | 2026-10-06T12:49:43.176600+00:00 | 2026-10-06T12:49:43.180736+00:00 | 0.004136 | 0.004136 |
| F4 | PASS | 2026-10-06T12:49:43.181998+00:00 | 2026-10-06T12:49:49.982518+00:00 | 6.800515 | 6.800520 |
| F5 | INVALID / interrupted aggregate | 2026-10-06T12:49:50.152870+00:00 | 2026-10-06T13:15:16.343860+00:00 | 1526.190335 | 1526.190990 |
| F5(i) | measurement missing | 2026-10-06T12:49:50.154030+00:00 | null | null | null |
| F5(ii) | measurement missing | 2026-10-06T13:13:41.262977+00:00 | null | null | null |
| F6 | NOT_RUN | null | null | null | null |
| F7 | NOT_RUN | null | null | null | null |
| F8 | NOT_RUN | null | null | null | null |
| F9 | NOT_RUN | null | null | null | null |

Observed fixture envelope: 1565.842721 s awake / 1565.843391 s elapsed UTC (26.097390 min), 2026-10-06T12:49:10.500469+00:00 → 2026-10-06T13:15:16.343860+00:00. Observed N1-method start through interrupted F5-method finally; excludes initial gate/setup and subsequent harness close/process exit/reporting. Full harness total clock not persisted. Awake uses mach_absolute_time (excludes sleep); continuous uses mach_continuous_time; elapsed is the UTC difference. Raw clock endpoints are retained. Method costs exclude subsequent compressed trace writing; F1 includes nested F1d (do not sum them). F1a–c costs include integration/measurement but exclude final close.

F5(i) start-to-next-start boundary: 1431.108947 elapsed UTC s; F5(ii) start-to-aggregate-end boundary: 95.080883 s. These include transition/cleanup and are not complete measured per-start fixture costs. No per-start awake clock or component clock was saved; the missing values stay null.

N1 criterion: production h=0.005 versus refinement h=0.00125, λ=32; wrapped and unwrapped carrier-relative phase differences each ≤0.01 rad, free-position difference ≤0.01 m.u., Nθ and Nx identical in ≥0.99 endpoints, pins invariant; applicable entry times agree within 0.1 s or both absent. N1a–e run 16 s; N1f runs 24 s. N1g runs 16 s descriptively, outside accuracy cuts; missing/nonfinite measurements would still be INVALID.

| Case | Verdict | Wrapped rad | Unwrapped rad | Position m.u. | Entry coarse/fine s | Nθ | Nx | Pins |
|---|---|---:|---:|---:|---|---:|---:|---|
| N1a | PASS | 5.20817167171e-10 | 5.20817167171e-10 | 2.24428540148e-05 | [8.1, 8.1] | 1.0 | 1.0 | True |
| N1b | PASS | 4.50215185133e-08 | 4.50215185688e-08 | 3.24866356038e-10 | N/A | 1.0 | 1.0 | True |
| N1c | PASS | 1.7763568394e-13 | 1.7763568394e-13 | 0.000251631968327 | N/A | 1.0 | 1.0 | True |
| N1d | PASS | 4.58360083533e-06 | 4.58360083516e-06 | 3.79425152719e-06 | N/A | 1.0 | 1.0 | True |
| N1e | PASS | 1.84294890815e-06 | 1.84294890815e-06 | 8.89399314197e-08 | [8.700000000000001, 8.700000000000001] | 1.0 | 1.0 | True |
| N1f | PASS | 1.71427155848e-06 | 1.71427155848e-06 | 0.000429717852314 | [10.100000000000001, 10.100000000000001] | 1.0 | 1.0 | True |
| N1g | DESCRIPTIVE | 2.17534154084 | 6.28318530718 | 0.0812111748402 | N/A | 1.0 | 1.0 | True |

N1f coarse/fine holds through t=24: [True, True]; agreement=True. F1c reported verdict: PASS. The current N1f hold agrees; no numerical-unresolved flag applies. The separate 160 s F1c gate also passed.

N1g slip is an endpoint escape diagnostic, not a completed winding or an accuracy verdict. The first departure ≥0.5 rad from member 0’s initial unwrapped carrier-relative π has opposite signs in the two integrations. Both first crossings occur at 0.6 s, bracketed by [0.5,0.6] s. h=0.005: direction −1, departure −1.18789486378 rad, final phase approximately 0, final displacement −π. h=0.00125: direction +1, departure +2.91994890256 rad, final phase approximately 2π, final displacement +π. DESCRIPTIVE / SENSITIVITY_NOT_ACCURACY / used_in_verdict=False.

N1 validity (coarse/fine; individual and used-pair masks are descriptive):

| Case | Individual invalid frames/observations | Pair invalid frames/observations | Individual disagreement frames/observations | Pair disagreement frames/observations | Minimum distances coarse / fine, m.u. |
|---|---|---|---|---|---|
| N1a | [1, 1] / [1, 1] | [0, 0] / [0, 0] | 0 / 0 | 0 / 0 | [{'element_element': None, 'element_site': 0.5555555555555691}, {'element_element': None, 'element_site': 0.5555555555556104}] |
| N1b | [0, 0] / [0, 0] | [0, 0] / [0, 0] | 0 / 0 | 0 / 0 | [{'element_element': None, 'element_site': 0.5556568658238792}, {'element_element': None, 'element_site': 0.5556568658239192}] |
| N1c | [0, 0] / [0, 0] | [0, 0] / [0, 0] | 0 / 0 | 0 / 0 | [{'element_element': None, 'element_site': 0.5169270740692962}, {'element_element': None, 'element_site': 0.5169270740688269}] |
| N1d | [1, 1] / [1, 1] | [1, 1] / [1, 1] | 0 / 0 | 0 / 0 | [{'element_element': 0.42800732708683054, 'element_site': 0.012644181081127748}, {'element_element': 0.4280029678325552, 'element_site': 0.012642502377364195}] |
| N1e | [0, 0] / [0, 0] | [1, 1] / [2, 2] | 0 / 0 | 0 / 0 | [{'element_element': 0.3628202264504896, 'element_site': 0.8352986345963771}, {'element_element': 0.36282022644994427, 'element_site': 0.8352986345996132}] |
| N1f | [0, 0] / [0, 0] | [0, 0] / [0, 0] | 0 / 0 | 0 / 0 | [{'element_element': 0.2127046960002117, 'element_site': 0.8700004145712756}, {'element_element': 0.21270467885053135, 'element_site': 0.8700004145713542}] |
| N1g | [1, 1] / [1, 1] | [1, 1] / [1, 1] | 2 / 2 | 2 / 2 | [{'element_element': 0.5899244186776489, 'element_site': 0.06987472785767235}, {'element_element': 0.5899243745704776, 'element_site': 0.069874698161275}] |

F1a/b require entry ≤0.3 rad by t=16 after the t=8 step, hold at every endpoint through 16, and path fraction ≥0.8 over 160 s. F1c requires entry by 16, hold through 24, path and source access ≥0.8 over 160 s, and response persistence ≥0.8 over [16,160]. Output pin invariance is an implementation check. Sustained delay, error at 12 and four-second margin are descriptive.

| Case | Entry s / delay s | Hold | Path fraction | Access fraction | Persistence [16,160] | Ordinary span initial / first endpoint / final | Ordinary radius first / final |
|---|---|---|---:|---:|---|---|---|
| F1a | 8.200000 / 0.200000 | True | 1.0 | 1.0 | not gated | 0.000000 / 0 / 0 | 3.22442246 / 3.322 |
| F1b | 8.700000 / 0.700000 | True | 1.0 | 1.0 | not gated | 1.112000 / 1.02732049 / 0.72757609 | 3.16470137 / 3.12978804 |
| F1c | 10.100000 / 2.100000 | True | 1.0 | 1.0 | 1.0 | 2.780000 / 2.62474133 / 1.17479054 | 3.12999959 / 2.5873947 |

F1c sustained-entry delay 2.100000 s; error at t=12 0.0366403259509 rad; four-second margin=True (descriptive). Ordinary-member compaction coexists with preserved pin/path/access; this is not a claim of no compaction or serial chain bandwidth. Geometry/exposure details (first endpoint is t=.1, final t=160):

F1a: `{"first_record_time": 0.1, "initial_declared_ordinary_span": 0.0, "last_record_time": 160.0, "minimum_distances": {"element_element": 0.5804224590412908, "element_site": 0.6780000000000204}, "ordinary_radius_final": 3.3219999999999796, "ordinary_radius_first_endpoint": 3.224422459041291, "ordinary_span_final": 0.0, "ordinary_span_first_endpoint": 0.0, "output_direct_drive_fraction": 0.0, "output_radius_final": 2.644, "output_radius_first_endpoint": 2.644, "shortcut_directed_edges_first_final": [0, 0], "source_access_fraction": 1.0, "source_direct_drive_fraction": 1.0, "source_site_distance_final": 0.6780000000000204, "source_site_distance_first_endpoint": 0.7755775409587091, "unique_Ntheta_lists": 1}`

F1b: `{"first_record_time": 0.1, "initial_declared_ordinary_span": 1.112, "last_record_time": 160.0, "minimum_distances": {"element_element": 0.3628202264504896, "element_site": 0.8352986345963771}, "ordinary_radius_final": 3.129788044836463, "ordinary_radius_first_endpoint": 3.164701365403623, "ordinary_span_final": 0.7275760896731489, "ordinary_span_first_endpoint": 1.027320494099805, "output_direct_drive_fraction": 0.0, "output_radius_final": 1.532, "output_radius_first_endpoint": 1.532, "shortcut_directed_edges_first_final": [6, 6], "source_access_fraction": 1.0, "source_direct_drive_fraction": 1.0, "source_site_distance_final": 0.870211955163537, "source_site_distance_first_endpoint": 0.8352986345963771, "unique_Ntheta_lists": 2}`

F1c: `{"first_record_time": 0.1, "initial_declared_ordinary_span": 2.78, "last_record_time": 160.0, "minimum_distances": {"element_element": 0.2127046960002117, "element_site": 0.8700004145712756}, "ordinary_radius_final": 2.587394699303191, "ordinary_radius_first_endpoint": 3.1299995854287244, "ordinary_span_final": 1.174790535004638, "ordinary_span_first_endpoint": 2.6247413265162987, "output_direct_drive_fraction": 0.0, "output_radius_final": 0.0, "output_radius_first_endpoint": 0.0, "shortcut_directed_edges_first_final": [28, 30], "source_access_fraction": 1.0, "source_direct_drive_fraction": 1.0, "source_site_distance_final": 1.412605300696809, "source_site_distance_first_endpoint": 0.8700004145712756, "unique_Ntheta_lists": 9}`

F1d is descriptive: same F1b start and input at λ=1, 8 and 32, all h=.005.

| λ | Entry / delay s | Hold through 16 | Deadline error rad | Output path fraction | Source access / direct drive | Unique Nθ lists |
|---|---|---|---:|---:|---|---:|
| 1.0 | None / None | False | 0.952856245214 | 1.0 | 1.0 / 1.0 | 3 |
| 8.0 | 10.5 / 2.5 | True | 0.00313200635778 | 1.0 | 1.0 / 1.0 | 2 |
| 32.0 | 8.700000000000001 / 0.7000000000000011 | True | 7.3310246762e-12 | 1.0 | 1.0 / 1.0 | 2 |

F1d geometry endpoints and effective-root/topology histories are retained in F1d.json.gz; endpoints and exposure summaries are also in MEASURED_SUMMARY.json. A missing λ=1 entry is deadline-censored, not a measured delay.

F2 PASS: empty default angle=0 and magnitude=0 exactly, no path; disconnected stepped/unstepped 160-phase streams bitwise_identical=True, any path=False. F3 PASS: output drive exactly +0.0 at all 80 RK4 stages (20 substeps×4). F4 PASS: internal output-channel phase coupling exactly zero at all 80 stages; site0=0.4 and oracle=1.1 angles exactly match wrapped .4 and 1.1. Native/reference magnitude, choice, path and output-presence checks are exact; wrapped-angle tolerance is 1e-12.

| F4 parity mode | Status | Decisions | Maximum wrapped angle difference rad |
|---|---|---:|---:|
| intact | MATCH | 160 | 4.4408920985e-16 |
| donor | MATCH | 160 | 1.7763568394e-15 |
| output_channel | MATCH | 160 | 0 |
| site0 | MATCH | 160 | 0 |
| oracle | MATCH | 160 | 0 |

F5 criterion, both starts: pooled paired frozen assays at checkpoints 40/45/50 require max(E)≥0.5, A≥0.3, B≥0.3; start i additionally requires a B-out birth, start ii a B-path birth. Measured A/B/E, B-out/B-path events, refusal counts and times are unavailable for both starts. Start i reached the next-start boundary but its values were not saved; start ii was interrupted. No zero, PASS or FAIL is inferred.

F5 descriptive not-qualified-window summary: UNAVAILABLE for i and ii (null qualification-window counts, invalid-pair counts/fractions, frame counts). Intended intervals by check endpoint are (0,640], (640,720], (720,800] and whole (0,800] s; small-cohort starts remain in denominators, an empty denominator gives null, fast-transient frames count once, recovery skips are excluded, used_in_verdict=False. The missing summary is part of the INVALID measurement; N1 mask counts do not substitute for it.

| Later fixture | Criterion and measurements | Status / stop |
|---|---|---|
| F6 | Descriptive encoding/retention/circular correlation; ≥5 defined pairs; unique-recipient baseline denominator | NOT_RUN; blocked by INVALID F5 |
| F7 | Match every requested control-M B1 birth; unmatched=0; fraction null if zero requests. Requested/matched/unmatched/fraction all null | NOT_RUN; blocked by INVALID F5 |
| F8 | Descriptive move then memory reward/eligibility/B1 demand on live F5(i) state; all quantities null | NOT_RUN; blocked by INVALID F5 |
| F9 | Four literal descriptive decoder observations; actions/demands null | NOT_RUN; blocked by INVALID F5 |

Order and stops: N1 ran first and passed; F1a–c then descriptive F1d passed/gave measurements; F2–F4 all ran and passed. The F1-F4 FAIL stop was NO. F5 started i then ii, but fixture_invalid fires YES on the measurement-wrapper defect; implementer stops and blocks the next stage. This is an operator stop under §9.7, not a returned harness stop list. All other future/development rows remain NOT_EVALUATED.

| Stop question | Outcome | Action | Role |
|---|---|---|---|
| integration_not_tested_reviewed | NO | Block all execution | implementer |
| source_unit_endpoint_mismatch | NO | Block execution | implementer |
| N1_failed_or_invalid | NO | Block F1 and every later fixture | implementer |
| F1_F4_failed | NO | Block F5 and development; report | implementer |
| fixture_invalid | YES | Report INVALID; block next stage | implementer |
| F5_failed | NOT_EVALUATED | Block development; write failure report | drafter |
| F7_unmatched | NOT_EVALUATED | Block development; write failure report | drafter |
| protocol_changed_after_results | NO | Draft new revision with fresh entropy | drafter |
| development_over_hour_before_22 | NOT_EVALUATED | Ask owner under decision 0031 | implementer |
| development_stopped_next_needed | NOT_EVALUATED | Ask owner | owner |
| engines_not_ready_reviewed | NO | Block all execution | implementer |
| readout_invalid | NOT_EVALUATED | Report INVALID with raw evidence; never reinterpret as PASS or FAIL | implementer |
| perceive_unusable | NOT_EVALUATED | Block G2 and G0; no primary-task substitution | implementer |
| full_seed_M_unmatched | NOT_EVALUATED | Keep seed G0-INCONCLUSIVE; never replace | implementer |
| task_blind_G1_fail | NOT_EVALUATED | Write failure report; stop development | drafter |
| G0prime_fail | NOT_EVALUATED | Write failure report; stop development | drafter |
| G2_fail_or_inconclusive | NOT_EVALUATED | Write failure or diagnosis report; stop development | drafter |

A7 development projection is PARTIAL / TOTAL_NOT_QUALIFIED. Measured N1 composite: 7.8007278125e-05 awake s/substep; F1 composite: 0.000113881161458 s/substep; F4 mixed native/reference composite: 0.680051516666 s/assay episode. At 20 production substeps/frame, arithmetic-only training proxies are 6.656621 h (N1) or 9.717859 h (F1). Applying F4's small mixed-scaffold composite to all assays gives 82.017235 h, including an arithmetic 0.386874 h for 2,048 site-body-off episodes. These are explicitly unqualified scenarios, not isolated RHS rates, native-grown-media estimates, total hours or bounds; do not sum alternative training proxies or add site-body-off twice.

Inherited workload counts: `{"donor_capture_episodes": 8192, "growth_checks": 76800, "intact_trainings": 16, "qualification_starts": 8512, "site_body_off_added_episodes": 2048, "site_body_off_episodes_per_intact_training": 128, "snapshot_assay_episodes_max": 327680, "total_assay_episodes_max_all_four_tasks": 434176, "training_world_frames": 15360000, "trainings": 48}`. Grown-population training/assay, B-path, qualification, recovery and donor-capture rates remain null. Partial F5 cost is 1526.190335 awake s with no persisted workload/component denominator; it cannot price those components. Qualified total=null. The observed F5(i) start-to-next-start boundary alone took 23.851816 minutes; the original 40.98-minute allowance cannot justify a future execution unchanged. A future duration requires a fresh estimate and the applicable decision-0031 policy; no future execution is authorized by this interrupted receipt. No training/development, development evaluation panel, judging entropy or registration occurred; only fixture-specific growth and frozen assays executed.

Repository-wide unchanged check: FAIL; 7082 tracked files checked, pin unchanged, docs/PLAN_CURRENT.md unchanged=False, historical evidence unchanged=True, staged diff empty at both observations=True. RRG source inventory was also read-only verified during the run: 23 manifest entries, 24 checksum entries and all 12 owner hashes match. All task-created artifacts stay in growing_shapes/. The four outside-scope changes observed during execution are listed by before/after SHA256 in CONCURRENT_STATE_CHANGES.json. This task issued no writes to docs/PLAN_CURRENT.md or those Astelia files, and leaves their concurrent current state untouched. The broader unchanged check cannot be claimed to pass; the 69-file execution pin and historical growing_shapes evidence do pass.

Mandatory owner recheck: RECHECK_COMPLETE, independent read-only Codex fallback, no remaining report blocker. All 69 pinned inputs, saved trace/timing records and reported measurements were verified. Recheck and disposition are recorded beside this run, under the owner’s explicit restriction against editing docs/PLAN_CURRENT.md. The report/evidence delivery is distinct from scientific acceptance or development readiness.

Assisted-by: Codex:GPT-6
