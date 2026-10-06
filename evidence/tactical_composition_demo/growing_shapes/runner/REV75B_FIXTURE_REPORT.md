INVALID

**Pre-execution duration stop; every real fixture is NOT_RUN.** This first-line delivery status does not assert a fixture measurement failure or a scientific code defect. No new Harness.run_all receipt exists.

Requested revision 7.5 measurement-tool re-run; execution pin `7a63d15064df745bfa63071473e02ffcb327901d6210c8310f5b5f8c3a330bce` verified before preparation: all 69 inputs match, including final committed designs and the current configuration/inventory. Execution grant reference = `docs/decisions/0031-owner-run-approval-policy.md`; integration_review = `evidence/tactical_composition_demo/growing_shapes_review_claude/REV75_FIXTURE_READINESS_CONFIRMED.md` (READY_FOR_FIXTURES, Claude). The grant was not started. Decision 0031 standing approval is subject to the owner's explicit instruction here to stop if the estimate exceeds one hour, regardless of clock time.

The earlier rev75_fixture_run_20261006 and REV75_FIXTURE_REPORT.md remain unchanged. That attempt was invalidated by execute_once.py observing a non-executable finally line. F5 results of the first attempt were never persisted or observed; no A/B/E or F5 verdict is inferred. This requested re-run is a measurement-tool correction, not new scientific code, fresh entropy, independent replication or registration.

Complete sequence planning estimate: **5476.771067 s (91.280 minutes)**; explicit 20% scheduling allowance **109.535 minutes**. The historical first-start transition took 1431.108947 elapsed UTC s (23.852 minutes). Its 8000 live frames, 90 frozen assays and 12 qualification starts are extrapolated against 30400 live frames, 320 late assays and 34 qualification starts. Maximum workload ratio = 3.8; add 38.557068 s of early measured costs once (including F4's ten assays). No rehearsal, benchmark or real fixture was run to price this.

Alternative single-component allocations, before scheduling allowance: live_frame_dominant: 91.280 minutes; frozen_assay_dominant: 85.449 minutes; qualification_recovery_dominant: 68.223 minutes. These are arithmetic sensitivity scenarios, not bounds. The historical boundary included line tracing; the new wrapper removes it, but the size of that speedup is unmeasured. Population/task differences, transition cleanup and unknown component costs prevent a qualified prediction. The conservative operational estimate triggers the explicit stop; it does not prove the true untraced execution would exceed an hour.

The new execute_once.py uses whole-call timing and calls the unchanged pinned Harness.run_all. It persists every returned field, including both F5 starts, the descriptive qualification summary, all records/events and the exact harness receipt. There are no line or bytecode observation hooks. Individual F1a-c/F5i-ii execution costs are unavailable because they are inline blocks and the harness returns no execution clocks for them; their enclosing calls are timed. F1 contains F1d, so their aggregate clocks must not be summed. test_wrapper_double.py tests fabricated multi-start PASS and FAIL gate returns without importing the scientific harness. Its once-run result is in WRAPPER_SYNTHETIC_CHECK.json.

The synthetic double passed once: both fabricated starts and every nested field matched the saved stage and original receipt in the complete and failed-gate cases; one run_all call per case. Synthetic wall time was 0.004321 awake s / 0.004317 elapsed UTC s. Synthetic FIXTURES_PASS is a fabricated persistence test, with no real fixture qualification. For a later execution, the F1 aggregate includes nested F1d persistence, F1d excludes its own persistence, and the harness total includes stage persistence but excludes final receipt serialization.

| Fixture | Criterion / quantities required | New measurement | Start UTC / end UTC / awake s / elapsed UTC s |
|---|---|---|---|
| N1a-f | h=.005 vs .00125; wrapped/unwrapped phase differences each ≤.01 rad; free-position difference ≤.01 m.u.; Nθ and Nx agreement ≥.99; pins invariant; applicable entry times agree within .1 s or both absent. Report phase, position, unwrapped, entry, topology and masks. | NOT_RUN; all null | null / null / null / null |
| N1g | Descriptive saddle escape as specified below; no accuracy cut. | NOT_RUN; all null | null / null / null / null |
| F1a/F1b | Entry within .3 rad by t=16 after t=8 step; hold every endpoint through 16; path ≥.8 over 160 s. Report entry/delay, hold, access, direct drive, compaction spans/radii and topology. | NOT_RUN; all null | null / null / null / null |
| F1c | Entry by 16; hold through 24; path and access ≥.8 over 160 s; response persistence ≥.8 over [16,160]; output pin invariant. Report compaction geometry, sustained delay, error at 12 and descriptive 4-second margin. | NOT_RUN; all null | null / null / null / null |
| F1d | Descriptive same F1b at λ=1 vs 8 (also 32), h=.005: entry/delay, hold, deadline error, paths/access, geometry/topology; absent entry is censored. | NOT_RUN; all null | null / null / null / null |
| F2 | Exact zero empty angle/magnitude; no paths; disconnected stepped/unstepped phases bitwise identical for 160 endpoints. | NOT_RUN; all null | null / null / null / null |
| F3 | Output site-drive exactly +0.0 at all 80 RK4 stages. | NOT_RUN; all null | null / null / null / null |
| F4 | Output internal coupling exactly zero at all 80 stages; exact site0/oracle decoder angles; native/reference magnitude/choice/path/output-presence exact, wrapped-angle tolerance 1e-12. | NOT_RUN; all null | null / null / null / null |
| F5(i)/F5(ii) | Pool checkpoints 40/45/50: A≥.3, B≥.3, max(E)≥.5; B-out birth for i, B-path birth for ii. Record both A/B/E, complete B-out/B-path events and not-qualified fractions. | NOT_RUN; all null | null / null / null / null |
| F6 | Descriptive encoding, retention and circular correlations with ≥5 defined pairs; baseline denominator uses unique recipient episodes. | NOT_RUN; all null | null / null / null / null |
| F7 | Every requested control-M B1 birth matched; unmatched=0; fraction null if zero requests. Record requested/matched/unmatched/fraction and events. | NOT_RUN; all null | null / null / null / null |
| F8 | Descriptive live F5(i) move then memory reward/eligibility/B1 demand. | NOT_RUN; all null | null / null / null / null |
| F9 | Four literal descriptive decoder observations; demand and actions. | NOT_RUN; all null | null / null / null / null |

N1f coarse/fine F1c hold agreement = NOT_RUN / null; coarse hold=null, fine hold=null. F1c has no new verdict. If measured holds disagree in an authorized later execution, report F1c NUMERICALLY_UNRESOLVED while preserving the harness verdict. Earlier agreement is historical and cannot stand in for this attempt.

N1g definition: member 0's first endpoint departure ≥0.5 rad from its initial unwrapped carrier-relative phase π; direction is displacement sign; time is first crossing, bracketed by preceding endpoint (initial t=0 if first). At each h=.005/.00125: status, direction, time, preceding-endpoint bracket, departure displacement, final unwrapped phase/displacement and raw records are null / NOT_RUN here. With an actual no-crossing run, status would be NOT_OBSERVED with null direction/time/bracket. DESCRIPTIVE / SENSITIVITY_NOT_ACCURACY / used_in_verdict=False; escape does not mean a completed 2π winding.

F5 descriptive not-qualified-window summary: for each start, check-endpoint intervals (0,640], (640,720], (720,800], and whole (0,800] s. Record qualification-window counts, not-qualified invalid-pair counts/fractions and frame counts. All starts including small cohorts stay in denominators; zero denominator gives null; fast-transient frames count once; recovery skips excluded; used_in_verdict=False. Every new value is null because F5 was not started.

Required sequence retained in unchanged Harness.run_all: N1 first; FAIL/INVALID blocks all. F1a-c then descriptive F1d; F2-F4 still run after F1 FAIL; any F1-F4 FAIL stops before F5. Then F5 both starts; F5 FAIL stops. Then F6, F7; F7 FAIL stops; then F8, F9. Any fixture INVALID blocks the next stage. This preparation stopped before the sequence, so no scientific stop row was evaluated.

| Stop question | Outcome | Yes action | Role |
|---|---|---|---|
| Does the complete fixture estimate exceed one hour? | YES | Stop before real fixtures; report estimate | implementer |
| integration_not_tested_reviewed | NO | Block all execution | implementer |
| source_unit_endpoint_mismatch | NO | Block execution | implementer |
| N1_failed_or_invalid | NOT_EVALUATED | Block F1 and every later fixture | implementer |
| F1_F4_failed | NOT_EVALUATED | Block F5 and development; report | implementer |
| fixture_invalid | NOT_EVALUATED | Report INVALID; block next stage | implementer |
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

A7: no new measured rates. Qualified development total=null / NOT_QUALIFIED. Historical small-scaffold composites retained only as explicitly unqualified arithmetic scenarios: N1 training proxy 6.656621 h OR F1 proxy 9.717859 h; mixed F4 all-assay proxy 82.017235 h, including 0.386874 h for the 2048 site-body-off episodes. Do not sum alternatives or count the comparator twice. Grown training/assay, qualification/recovery, B-path and donor-capture rates remain null. No development cost is qualified by the F5 boundary estimate.

No real fixtures, training, development, evaluation panels, judging entropy or registration occurred. The scientific code and earlier evidence are unchanged. Review and disposition are tracked beside this attempt under the explicit owner restriction against editing docs/PLAN_CURRENT.md. Commit/bundle outcome and final preservation verification are in REV75B_FIXTURE_DELIVERY_NOTE.md and DELIVERY_VERIFICATION.json.

Assisted-by: Codex:GPT-6
