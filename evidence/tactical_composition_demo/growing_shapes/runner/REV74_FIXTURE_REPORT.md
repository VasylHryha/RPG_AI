FIXTURES_FAIL

Revision 7.4 fixtures ran ONCE at execution pin `f370c3b5ea17cf0b3c751de794de0c8ab1dffdb35cbffdc35d81f9b8280c3ce5`. All 68 inputs matched at start and completion; the committed design and approval identity passed the execution gate. Grant: `docs/decisions/0031-owner-run-approval-policy.md`. Integration review: `evidence/tactical_composition_demo/growing_shapes_review_claude/REV74_FIXTURE_READINESS.md` (READY_FOR_FIXTURES, Claude). New evidence: `rev74_fixture_run_20261006/`; historical 7.3 evidence and report are unchanged.

The unchanged pinned `Harness.run_all` ran under `caffeinate -i`. The new wrapper observes clocks and writes evidence; it does not replace scientific methods, thresholds, order or verdicts. No code defect, crash or INVALID was recorded. No code was changed during execution; no patch, fixture replay or rerun followed the failure.

Pre-run static-harness scheduling estimate: 2300.160731 s (38.34 min), allowance 2453.504780 s (40.89 min), below one hour. DURATION_ESTIMATE.json retains counts, source hashes and explicit assumed dispatch/substep sensitivity multipliers with contingency. This provisional estimate is not a measured 7.4 total or an upper bound; no benchmark or rehearsal ran. It includes all later stages even though the stop shortened execution.

N1 FAIL because N1d exceeds wrapped phase, unwrapped phase and free-position cuts. N1a/b/c/e/f PASS. The `N1_failed_or_invalid` stop row fires YES: implementer blocks F1 and every later fixture. F1a–d and F2–F9 are NOT_RUN. The F1-F4 rule allowing F2–F4 after an F1 FAIL was never reached; N1 FAIL blocks them all.

| Fixture | Verdict | Start UTC | End UTC | Awake s | Elapsed UTC s |
|---|---|---|---|---:|---:|
| N1 | FAIL | 2026-10-06T12:23:16.140167+00:00 | 2026-10-06T12:23:38.390307+00:00 | 22.250146 | 22.250140 |
| F1a | NOT_RUN | null | null | null | null |
| F1b | NOT_RUN | null | null | null | null |
| F1c | NOT_RUN | null | null | null | null |
| F1d | NOT_RUN | null | null | null | null |
| F2 | NOT_RUN | null | null | null | null |
| F3 | NOT_RUN | null | null | null | null |
| F4 | NOT_RUN | null | null | null | null |
| F5(i) | NOT_RUN | null | null | null | null |
| F5(ii) | NOT_RUN | null | null | null | null |
| F6 | NOT_RUN | null | null | null | null |
| F7 | NOT_RUN | null | null | null | null |
| F8 | NOT_RUN | null | null | null | null |
| F9 | NOT_RUN | null | null | null | null |

Total harness execution: 24.102590 s awake / 24.102589 s elapsed UTC, 2026-10-06T12:23:14.644656+00:00 → 2026-10-06T12:23:38.747245+00:00. N1 method cost excludes compressed-trace writing; total includes gate, trace saving, result validation and close through harness return, and excludes final receipt writing/preservation/reporting. Raw start/end clocks are retained in timing records. Awake: mach_absolute_time, excluding sleep; continuous: mach_continuous_time, including sleep; elapsed: UTC timestamp difference.

N1 criterion: λ=32, production h=0.005 (20 substeps) against h=0.00125 (80), compared at each 0.1 s endpoint. Maximum wrapped and unwrapped carrier-relative phase differences each ≤0.01 rad; maximum free-position difference ≤0.01 m.u.; Nθ and Nx agreement each ≥0.99; pins invariant. Where applicable, both enter within 0.1 s of each other or both lack entry. N1a–e have 160 endpoints per run (16 s); N1f has 240 (24 s). Estimator validity masks and hold agreement are descriptive, distinct from the unchanged numerical gate.

| Case | Verdict | Wrapped rad | Unwrapped rad | Position m.u. | Entry coarse/fine s | Nθ | Nx | Pins |
|---|---|---:|---:|---:|---|---:|---:|---|
| N1a | PASS | 5.20817167171e-10 | 5.20817167171e-10 | 2.24428540148e-05 | [8.1, 8.1] | 1.0 | 1.0 | True |
| N1b | PASS | 4.50215185133e-08 | 4.50215185688e-08 | 3.24866356038e-10 | N/A | 1.0 | 1.0 | True |
| N1c | PASS | 1.7763568394e-13 | 1.7763568394e-13 | 0.000251631968327 | N/A | 1.0 | 1.0 | True |
| N1d | FAIL | 2.17534154084 | 6.28318530718 | 0.0812111748402 | N/A | 1.0 | 1.0 | True |
| N1e | PASS | 1.84294890815e-06 | 1.84294890815e-06 | 8.89399314197e-08 | [8.700000000000001, 8.700000000000001] | 1.0 | 1.0 | True |
| N1f | PASS | 1.71427155848e-06 | 1.71427155848e-06 | 0.000429717852314 | [10.100000000000001, 10.100000000000001] | 1.0 | 1.0 | True |

N1d is the declared near-site-body antiphase/inside-cutoff recipe. Its unwrapped maximum is approximately one full turn; wrapped disagreement also exceeds tolerance, and free-position disagreement exceeds tolerance. These are recorded finite discrepancies, so the harness verdict is FAIL, not INVALID. No causal diagnosis or corrective solver choice is established by this receipt.

N1f coarse/fine hold through t=24 s: [True, True]; agreement=True. Both enter at t=10.1 s (delay 2.1 s after the t=8 step). The F1c hold agrees numerically on this 24 s N1f test. F1c itself remains NOT_RUN: its 160 s path, access and persistence gate has not been measured. No hold-disagreement flag applies.

N1 validity counts are coarse/fine pairs. Counts are descriptive and use π/2 individual E_i / used-pair E_i+E_j cuts; pairs are the undirected union of endpoint Nθ links in each run.

| Case | Individual invalid frames / observations | Used-pair invalid frames / observations | Individual disagreement frames / observations | Used-pair disagreement frames / observations |
|---|---|---|---|---|
| N1a | [1, 1] / [1, 1] | [0, 0] / [0, 0] | 0 / 0 | 0 / 0 |
| N1b | [0, 0] / [0, 0] | [0, 0] / [0, 0] | 0 / 0 | 0 / 0 |
| N1c | [0, 0] / [0, 0] | [0, 0] / [0, 0] | 0 / 0 | 0 / 0 |
| N1d | [1, 1] / [1, 1] | [1, 1] / [1, 1] | 2 / 2 | 2 / 2 |
| N1e | [0, 0] / [0, 0] | [1, 1] / [2, 2] | 0 / 0 | 0 / 0 |
| N1f | [0, 0] / [0, 0] | [0, 0] / [0, 0] | 0 / 0 | 0 / 0 |

Minimum distances over N1, coarse/fine (element-element / element-site, m.u.; null means no pair):

| Case | Coarse | Fine |
|---|---|---|
| N1a | {"element_element": null, "element_site": 0.5555555555555691} | {"element_element": null, "element_site": 0.5555555555556104} |
| N1b | {"element_element": null, "element_site": 0.5556568658238792} | {"element_element": null, "element_site": 0.5556568658239192} |
| N1c | {"element_element": null, "element_site": 0.5169270740692962} | {"element_element": null, "element_site": 0.5169270740688269} |
| N1d | {"element_element": 0.5899244186776489, "element_site": 0.06987472785767235} | {"element_element": 0.5899243745704776, "element_site": 0.069874698161275} |
| N1e | {"element_element": 0.3628202264504896, "element_site": 0.8352986345963771} | {"element_element": 0.36282022644994427, "element_site": 0.8352986345996132} |
| N1f | {"element_element": 0.2127046960002117, "element_site": 0.8700004145712756} | {"element_element": 0.21270467885053135, "element_site": 0.8700004145713542} |

| Fixture | Criterion and required values | Measured values | Stop outcome |
|---|---|---|---|
| F1a, F1b | Entry error ≤0.3 rad by t=16 after t=8 step; hold every endpoint to t=16; effective-root path fraction ≥0.8 | Entry, hold, path/access fractions and compaction span/radius/distances null; NOT_RUN | Blocked by N1 |
| F1c | Entry by t=16; hold to t=24; path ≥0.8 and source access ≥0.8 over 160 s; response persistence ≥0.8 in [16,160] | All F1c values null; NOT_RUN. N1f hold agreement is reported separately above. Sustained entry delay, error at t=12 and four-second margin are unmeasured/descriptive | Blocked by N1 |
| F1d | Descriptive identical F1b starts/input at λ=1 versus 8 versus 32, h=0.005: delay, hold, deadline error, roots/access, geometry/topology histories | All three arms NOT_RUN; comparison values null | Blocked by N1 |
| F2 | Empty default exactly angle=0 and magnitude=0, no path; disconnected stepped/unstepped 160-phase streams bitwise identical, no path | All exactness observations null; NOT_RUN | Blocked by N1 |
| F3 | Output drive +0.0 exactly at every stage: 20 substeps ×4 stages | Stage terms null; NOT_RUN | Blocked by N1 |
| F4 | Output-channel internal phase coupling zero at all 80 stages; site0/oracle relay angle exact; five native/reference assays with 160 decisions each, wrapped angle ≤1e-12, magnitude/choice/path/output exact | Stage, relay and parity observations null; NOT_RUN | Blocked by N1 |
| F5(i), F5(ii) | Both starts: B-out birth for i, B-path birth for ii; max E≥0.5, A≥0.3 and B≥0.3; checkpoint assays at 40/45/50 | A/B/E, B-out/B-path birth/event counts and timing null for both starts; NOT_RUN | Blocked by N1 |
| F6 | Descriptive encoding/retention and JS circular correlation; ≥5 defined pairs; baseline denominator uses unique recipient episodes | Correlation, defined pairs and retention null; NOT_RUN | Blocked by N1 |
| F7 | Match every requested control-M B1 birth; unmatched=0; fraction null if no requests | Requested/matched/unmatched/fraction null; NOT_RUN; no empty-denominator or matching claim | Blocked by N1 |
| F8 | Descriptive retained live F5(i) state; 20 move then 20 remember_static episodes; reward, P/eligibility and B1 demand | All values null; NOT_RUN | Blocked by N1 |
| F9 | Four descriptive literal decoder observations | All actions/demands null; NOT_RUN | Blocked by N1 |

F5 descriptive not-qualified-window summary is NOT_RUN for each start: qualification-window count, invalid-pair count, fraction, world frames and fast-transient frames are null/unmeasured, not zero. No window denominator exists. Intended intervals are (0,640], (640,720], (720,800] s by check endpoint, whole (0,800], retaining small-cohort starts in the denominator. An empty denominator gives null. Every fast-transient world frame is counted once; recovery skips are excluded. The fraction is used_in_verdict=False. N1 transient counts do not estimate F5 window validity.

| Stop question | Outcome | Yes action | Responsible role |
|---|---|---|---|
| integration_not_tested_reviewed | NO | Block all execution | implementer |
| source_unit_endpoint_mismatch | NO | Block execution | implementer |
| N1_failed_or_invalid | YES | Block F1 and every later fixture | implementer |
| F1_F4_failed | NOT_EVALUATED | Block F5 and development; report | implementer |
| fixture_invalid | NO | Report INVALID; block next stage | implementer |
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

NOT_EVALUATED means that stage was never reached; it is not an observed negative result. The original harness stop output is unchanged in RUN_RECEIPT.json. Development is blocked and has not been started.

A7 development cost projection: PARTIAL, qualified total=null / NOT_QUALIFIED. The measured N1 composite rate is 0.000213943709535 awake s/RK4 substep (22.250146 s / 104,000). Multiplying by 20 gives 0.0042788741907 s/production frame; applying that arithmetic to 15,360,000 training frames gives 18.256530 h. This is an unqualified frozen-scaffold arithmetic proxy, not a live training estimate, isolated RHS rate, or lower/upper bound. N1 mixes refinement and production, small populations, construction, diagnostics and observer dispatch.

Development workload (counts only; no execution grant): 48 trainings, 15,360,000 training frames, 76,800 growth checks, 8,512 qualification starts, up to 327,680 snapshot-assay episodes and up to 434,176 total assay episodes with all four tasks usable. The total includes 2,048 site-body-off episodes (128×16 intact trainings); donor capture adds 8,192 world episodes. These inherited workload counts are kept separate from this run’s measured rate.

Live training/growth, B-path search, qualification/recovery, grown-population assays and site-body-off throughput are all unmeasured because N1 blocked F1–F9. Their rates and added seconds remain null in A7_DEVELOPMENT_COST_PROJECTION.json. No qualified total or approval-ready duration can be produced; no additional pricing run occurred.

Evidence: RUN_RECEIPT.json is the original complete 7.4 receipt; N1.json.gz retains both integrations with positions, wrapped/unwrapped phase inputs, E_i, both topologies and pins. MEASURED_SUMMARY.json, timing, identity, inventory, stop and A7 files are small evidence. PRESERVATION.json: all 7,027 tracked paths unchanged, staged diff unchanged, execution pin unchanged, docs/PLAN_CURRENT.md unchanged. New files are confined to growing_shapes/. No training, development, evaluation panels, judging entropy or registration occurred.

Mandatory owner recheck is COMPLETE: the verbatim request was sent to independent read-only Codex reviewer /root/rev74_fixture_recheck (other-family models unavailable in the collaboration roster). Verdict APPROVE for execution/report/delivery, no blocking findings or reporting corrections. See OWNER_RECHECK_REQUEST.md, OWNER_RECHECK_CODEX.md and OWNER_RECHECK_DISPOSITION.md beside this run. Only this completion sentence was updated after review; receipts, measurements, criteria and verdicts are unchanged. The final bundle adds the review records and refreshes verification. This recheck does not accept revision 7.4 scientifically or authorize development. docs/PLAN_CURRENT.md remains unchanged under the owner’s explicit instruction.

Assisted-by: Codex:GPT-6
