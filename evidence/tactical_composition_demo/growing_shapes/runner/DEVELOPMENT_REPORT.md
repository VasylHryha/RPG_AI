FAIL

Owner-authorized exploratory development; DESIGN_0H revision 5.1, decision 0028 items 17–19.
Implementer: Codex (GPT-6). Not milestone acceptance or scientific qualification.

Expected cost announced before execution: 21–55 serial hours; ideal 3–7 elapsed hours at eight workers (a pre-run estimate), subject to contention.
Measured cost seed 106060: 200 episodes, 415.407 awake monotonic seconds including calibration.
Measured serial projection: 11.403 hours at the full 20-snapshot evaluator cap.
Stage rates, projection arithmetic, exposure and limitations: [COST.json](development_20261006/COST.json).
The 24-hour report line is retained; owner authorized continuation through 60 serial hours.

Full-run awake monotonic time: 2.059 hours (7,410.865621166 seconds); maximum eight worker processes. This excludes suspended host time and is not elapsed calendar duration or CPU time. The host idle-slept during 01:24–08:00 local time, with dark wakes. RESULTS.json records completion at 2026-10-06 05:23:25 UTC (08:23:25 local). The review’s approximately 00:50–08:37 window includes later delivery work; the exact full-run calendar start was not retained.

| Arm | G0 | G0' | G1 | G1c | G5 |
|---|---|---|---|---|---|
| task_blind | INCONCLUSIVE | FAIL | PASS | DESCRIPTIVE | PASS |
| reward | INCONCLUSIVE | FAIL | PASS | DESCRIPTIVE | PASS |

Ordered rules: execution/measurement failure, nonfinite data, zero usable tasks or incomplete protocol → INVALID first. G0 requires both coverage and competence superiority in ≥6 unflagged seeds; ≤ on both in ≥6 gives FAIL; drops prevent PASS. G0' requires |slope|≤0.5 per 100 episodes and no late rejection/protected over-budget state in ≥6 seeds; ≥3 outside gives FAIL. G1 requires snapshots in ≥6 seeds for PASS, ≤2 for FAIL. G1c is descriptive. G5: INVALID first; <6 snapshot-bearing seeds → INCONCLUSIVE; fractions D≤0.1 of ≥0.8 in ≥6 bearing seeds → PASS; fractions <0.5 in ≥3 → FAIL; otherwise INCONCLUSIVE.

Seed units, G0 coverage denominators and paired competencies, flags, control additions/deaths/retries/drops, D3 removals, late turnover, snapshot counts, G1c per-task/best-task values and G5 differences: [RESULTS.json](development_20261006/RESULTS.json).

| Arm / seed / policy | Steps | Episodes | Qualification frames | Recovery simulated s | Evaluator episodes | Reward episodes | Training / qualification / recovery / evaluation measured s | Peak/final learned coefficients | Final/peak position-phase scalars | Copies |
|---|---:|---:|---:|---:|---:|---:|---|---|---|---:|
| task_blind/106061/intact | 320000 | 2000 | 319732 | 124920.000 | 20992 | 0 | 1027.155 / 307.659 / 398.958 / 262.846 | 90/88 | 132/135 | 20992 |
| task_blind/106061/control | 320000 | 2000 | 0 | 0.000 | 512 | 0 | 986.547 / 0.000 / 0.000 / 22.455 | 88/88 | 132/132 | 512 |
| task_blind/106062/intact | 320000 | 2000 | 319732 | 45720.000 | 20992 | 0 | 1066.845 / 274.005 / 184.120 / 566.761 | 90/88 | 132/135 | 20992 |
| task_blind/106062/control | 320000 | 2000 | 0 | 0.000 | 512 | 0 | 1023.234 / 0.000 / 0.000 / 27.256 | 90/86 | 129/135 | 512 |
| task_blind/106063/intact | 320000 | 2000 | 319732 | 82560.000 | 20992 | 0 | 1034.391 / 322.246 / 284.287 / 480.111 | 90/88 | 132/135 | 20992 |
| task_blind/106063/control | 320000 | 2000 | 0 | 0.000 | 512 | 0 | 1013.432 / 0.000 / 0.000 / 24.565 | 88/88 | 132/132 | 512 |
| task_blind/106064/intact | 320000 | 2000 | 319732 | 89160.000 | 20992 | 0 | 1034.985 / 304.625 / 300.170 / 479.919 | 90/88 | 132/135 | 20992 |
| task_blind/106064/control | 320000 | 2000 | 0 | 0.000 | 512 | 0 | 1004.780 / 0.000 / 0.000 / 24.699 | 88/88 | 132/132 | 512 |
| task_blind/106065/intact | 320000 | 2000 | 319732 | 89160.000 | 20992 | 0 | 1104.663 / 335.797 / 324.334 / 526.792 | 90/88 | 132/135 | 20992 |
| task_blind/106065/control | 320000 | 2000 | 0 | 0.000 | 512 | 0 | 1107.547 / 0.000 / 0.000 / 31.660 | 88/86 | 129/132 | 512 |
| task_blind/106066/intact | 320000 | 2000 | 319732 | 75240.000 | 20992 | 0 | 1124.487 / 345.147 / 282.759 / 509.733 | 90/90 | 135/135 | 20992 |
| task_blind/106066/control | 320000 | 2000 | 0 | 0.000 | 512 | 0 | 1124.826 / 0.000 / 0.000 / 30.360 | 90/88 | 132/135 | 512 |
| task_blind/106067/intact | 320000 | 2000 | 319732 | 82560.000 | 20992 | 0 | 1121.602 / 340.210 / 305.350 / 571.212 | 88/88 | 132/132 | 20992 |
| task_blind/106067/control | 320000 | 2000 | 0 | 0.000 | 512 | 0 | 1117.212 / 0.000 / 0.000 / 37.325 | 88/88 | 132/132 | 512 |
| task_blind/106068/intact | 320000 | 2000 | 319732 | 112080.000 | 20992 | 0 | 1096.323 / 325.162 / 386.841 / 405.862 | 90/88 | 132/135 | 20992 |
| task_blind/106068/control | 320000 | 2000 | 0 | 0.000 | 512 | 0 | 1126.895 / 0.000 / 0.000 / 36.823 | 88/88 | 132/132 | 512 |
| reward/106071/intact | 320000 | 2000 | 319732 | 107880.000 | 20992 | 2000 | 1030.207 / 299.673 / 351.315 / 536.113 | 88/88 | 132/132 | 20992 |
| reward/106071/control | 320000 | 2000 | 0 | 0.000 | 512 | 2000 | 1043.201 / 0.000 / 0.000 / 33.341 | 88/88 | 132/132 | 512 |
| reward/106072/intact | 320000 | 2000 | 319732 | 99840.000 | 20992 | 2000 | 1022.363 / 309.359 / 327.480 / 410.890 | 90/88 | 132/135 | 20992 |
| reward/106072/control | 320000 | 2000 | 0 | 0.000 | 512 | 2000 | 1005.425 / 0.000 / 0.000 / 23.798 | 88/88 | 132/132 | 512 |
| reward/106073/intact | 320000 | 2000 | 319732 | 94560.000 | 20992 | 2000 | 1032.647 / 308.269 / 310.748 / 428.637 | 90/88 | 132/135 | 20992 |
| reward/106073/control | 320000 | 2000 | 0 | 0.000 | 512 | 2000 | 1021.386 / 0.000 / 0.000 / 24.847 | 88/88 | 132/132 | 512 |
| reward/106074/intact | 320000 | 2000 | 319732 | 50520.000 | 20992 | 2000 | 1057.168 / 302.820 / 188.854 / 1002.995 | 90/88 | 132/135 | 20992 |
| reward/106074/control | 320000 | 2000 | 0 | 0.000 | 512 | 2000 | 1034.378 / 0.000 / 0.000 / 31.040 | 90/86 | 129/135 | 512 |
| reward/106075/intact | 320000 | 2000 | 319732 | 137640.000 | 20992 | 2000 | 1114.401 / 380.948 / 453.254 / 520.226 | 90/88 | 132/135 | 20992 |
| reward/106075/control | 320000 | 2000 | 0 | 0.000 | 512 | 2000 | 1112.735 / 0.000 / 0.000 / 33.516 | 90/88 | 132/135 | 512 |
| reward/106076/intact | 320000 | 2000 | 319732 | 139200.000 | 20992 | 2000 | 1114.384 / 391.354 / 475.668 / 321.026 | 90/88 | 132/135 | 20992 |
| reward/106076/control | 320000 | 2000 | 0 | 0.000 | 512 | 2000 | 1143.399 / 0.000 / 0.000 / 41.541 | 88/86 | 129/132 | 512 |
| reward/106077/intact | 320000 | 2000 | 319732 | 31080.000 | 20992 | 2000 | 1150.912 / 345.932 / 138.125 / 503.173 | 90/88 | 132/135 | 20992 |
| reward/106077/control | 320000 | 2000 | 0 | 0.000 | 512 | 2000 | 1101.634 / 0.000 / 0.000 / 25.981 | 88/88 | 132/132 | 512 |
| reward/106078/intact | 320000 | 2000 | 319732 | 78840.000 | 20992 | 2000 | 1113.659 / 334.928 / 287.896 / 517.622 | 90/88 | 132/135 | 20992 |
| reward/106078/control | 320000 | 2000 | 0 | 0.000 | 512 | 2000 | 1086.248 / 0.000 / 0.000 / 29.544 | 90/88 | 132/135 | 512 |

Measured full-run summed worker awake stage times: training 9.528 h, qualification 1.452 h, recovery 1.389 h, evaluation 2.367 h.
Template scalar storage per content hash, complete snapshots with recovery timescales and flags, final templates, evaluator-copy identities, episodes, pending state and raw ledger receipts are retained in each seed’s REPORT.json.gz. Coefficient accounting is not RAM usage or an efficiency comparison.
Qualified atom export (task_blind): [REPLAY_task_blind.json.gz](development_20261006/REPLAY_task_blind.json.gz); one additional diagnostic validation episode, excluded from read-outs.
Qualified atom export (reward): [REPLAY_reward.json.gz](development_20261006/REPLAY_reward.json.gz); one additional diagnostic validation episode, excluded from read-outs.
Stop-row responsibility: drafter if task-blind G1 FAIL or any G0' FAIL; write the failure report and stop development. INVALID is reserved for execution or measurement failures, nonfinite data, zero usable tasks or incomplete protocol. Any protocol change requires a new design revision and fresh development seeds. Owner decides any next development step.

All event logs and drive schedules are retained losslessly as ordered JSONL. Recovery-complete events retain complete immutable check-time native state and 601 frames; drive schedules retain the 600-step replay. All admitted snapshots and templates are retained, including those beyond the evaluation cap. File hashes and sizes: [ARTIFACTS.json](development_20261006/ARTIFACTS.json).
Calibration is frozen once on validation 0–255 and shared by cost, both arms and controls. Training uses dev episode seeds; control uses g0_control entropy. No judging namespace was used. Reviewed code, constants, schedules and receipt files were unchanged. The additive launch harness uses a ledger adapter to expose ordered event rows to the reviewed seed_unit function; receipts remain unchanged in stored reports.
Driven/cohort-restricted structural snapshots do not establish autonomous persistence or internally maintained closure. G5 is numerical copy covariance. H-BG, H-PS and H-RBG are NOT_TESTED; combinations and efficiency yardsticks remain deferred.

task_blind: G0 both-superior unflagged seeds 0/8; both-≤ seeds 1/8; dropped-request flags 8/8. G0' settled and unrejected seeds 0/8; late rejection seeds 8/8. G1 bearing seeds 8/8; admitted snapshots 5780; evaluated snapshots 160. G5 fractions D≤0.1: 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000.

reward: G0 both-superior unflagged seeds 0/8; both-≤ seeds 4/8; dropped-request flags 8/8. G0' settled and unrejected seeds 0/8; late rejection seeds 8/8. G1 bearing seeds 8/8; admitted snapshots 6082; evaluated snapshots 160. G5 fractions D≤0.1: 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000.

G1c descriptive summary: the following are means within each seed over its first 20 admitted snapshots, followed by the counts of snapshot best tasks in the fixed task order. They are not promotion cuts or evidence of superiority.

| Arm / seed | Snapshot mean n: perceive / move / remember_static / choose | Best-task counts in that order |
|---|---|---|
| task_blind/106061 | 0.009619 / -0.162929 / -0.093808 / 0.193048 | 2 / 0 / 0 / 18 |
| task_blind/106062 | 0.012417 / -0.941470 / -0.043300 / 0.105399 | 4 / 0 / 4 / 12 |
| task_blind/106063 | -0.003203 / -0.687533 / -0.034364 / 0.122972 | 2 / 0 / 8 / 10 |
| task_blind/106064 | 0.012293 / -0.307054 / -0.075943 / 0.160981 | 2 / 0 / 2 / 16 |
| task_blind/106065 | 0.004933 / -0.032916 / -0.107498 / 0.223136 | 0 / 0 / 0 / 20 |
| task_blind/106066 | 0.020616 / -0.690319 / -0.045799 / 0.099141 | 7 / 0 / 4 / 9 |
| task_blind/106067 | 0.005599 / -0.295452 / -0.082876 / 0.172415 | 1 / 0 / 1 / 18 |
| task_blind/106068 | 0.003764 / -0.072258 / -0.101052 / 0.212651 | 0 / 0 / 1 / 19 |
| reward/106071 | 0.007774 / -0.353178 / -0.077068 / 0.169860 | 2 / 0 / 3 / 15 |
| reward/106072 | 0.011815 / -0.239249 / -0.091129 / 0.179701 | 2 / 0 / 0 / 18 |
| reward/106073 | 0.014819 / -0.524935 / -0.069575 / 0.151209 | 3 / 0 / 2 / 15 |
| reward/106074 | 0.006821 / -0.622793 / -0.047348 / 0.132461 | 1 / 0 / 6 / 13 |
| reward/106075 | 0.011039 / -0.500325 / -0.059051 / 0.157394 | 3 / 0 / 4 / 13 |
| reward/106076 | 0.005163 / -0.032916 / -0.107498 / 0.222939 | 0 / 0 / 0 / 20 |
| reward/106077 | 0.009125 / -0.747524 / -0.037923 / 0.118217 | 3 / 0 / 7 / 10 |
| reward/106078 | 0.003394 / -0.524270 / -0.081988 / 0.148505 | 3 / 0 / 1 / 16 |

Retention verification: [PROTOCOL_AUDIT.json](development_20261006/PROTOCOL_AUDIT.json) confirms all 32 horizons, exposure totals, calibration identity, snapshot hashes and the reviewed ordered aggregation. The source/build closure was unchanged before and after execution.

Audit transport: every original event/drive ledger is retained in a verified gzip archive. [AUDIT_TRANSPORT.json](development_20261006/AUDIT_TRANSPORT.json) maps original receipt paths to archives, preserving the original decoded SHA256, byte count and record count. Stored Run receipts are unchanged; unpacking restores their exact bytes. No event, snapshot, template or replay was discarded.

Summed stage timings are worker awake monotonic time under parallel execution, not calendar duration or isolated serial CPU measurements. The measured cost seed projected 11.403 serial hours; summed full-run stage time was 14.736 worker hours. Development stops under the G0' failure row; no further development or outcome-informed protocol change was performed.

Accounting correction, 2026-10-06: only prose was amended; all original development receipts, values and verdicts remain unchanged. Historical keys named `wall_seconds` retain their original bytes and mean awake monotonic seconds on this host. See [DEVELOPMENT_RECHECK_REPORT.md](DEVELOPMENT_RECHECK_REPORT.md) for the descriptive artifact audit and its limits.
