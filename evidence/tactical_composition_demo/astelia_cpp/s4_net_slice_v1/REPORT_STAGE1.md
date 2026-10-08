# Stage 1 implementation — runtime blocked before timing

Implementation/recheck status: PASS_WITH_NOTES. Runtime status: BLOCKED_PROCESS_DISCOVERY. This is a controller/training implementation delivery, not trained policy acceptance, mechanism qualification, registration, scientific acceptance or release.

The original collected data, inventory, entropy, ledger, binary and contract remain unchanged. COLLECTION_RECEIPT.json verifies all 200 sealed fights and per-fight raw/receipt hashes. Measured sealed raw bytes are 1,736,679,437; collection wall435.256s, CPU418.619s, maximum child RSS114,688,000bytes. Converted180 eligible fights occupy904,249,116array bytes under gitignored _local/stage1/data;20 independent report-only fights remain excluded. Split fight counts: train144, validation24, test12, report20. Decision rows:95,400 /15,919 /7,987 /14,284 respectively.

Delivered: streaming/mmap conversion with whole-fight splits and causal masks; N1/N1r/N2 matched-budget Adam BC;90-tick joint BPTT with current-weight full-prefix burn-in, attached neighbor gradients, six-tick features, accepted visitor target history and launch/death resets; train-only fire weights, checkpoint selection, per-head held-out diagnostics; exported weights and native/PyTorch full-sequence parity tooling; separate native driver with exact impact diagnostics; two-round student/shadow DAgger aggregation/refits retaining round0; paired10–20-draw mechanism runner and N2 interventions/recorded kicks. Future physical jobs use repository ownership discovery, live owner cap, immutable inventories, failed-attempt limits and crash-boundary refusal.

Declared BC budget: ten epochs/arm,772 steps/epoch,7,720 gradient steps and954,000 decision rows per arm. All arms use identical positive-row windows; every actual decision row is counted exactly once per epoch. Empty gun tails are excluded and partial last-live windows retained. Torch threads4, interop1, workers0, CPU, no parallel fits. The planned sample is nine steps total, never more than20. It uses identical early/middle/late-prefix batches across arms, discards sample optimizer states and only admits three fits if the measured total projection is below3600s.

**No timing step ran.** TRAINING_ADMISSION_01.json records the real process gate failure: pgrep returned3, `sysmon request failed with error: sysmond service not found` and `pgrep: Cannot get process list`; gate statusUNAVAILABLE. The alternative `/bin/ps -axo pid=,command=` was denied with `PermissionError: [Errno1] Operation not permitted`. This environment's approval policy forbids escalation. No guard was disabled. Runtime projection is **unavailable/null**, not an invented estimate or an over-one-hour reading. All three fits, selected checkpoints, trained per-head diagnostics and trained export parity are NOT_RUN. DAgger rounds and mechanism fights are NOT_RUN; no new physical inventory/entropy was allocated.

## Measured held-out baselines

These are baselines from the sealed TEST split, not network results. Full values/counts and validation baselines are in STAGE1_BASELINES.json.

| Head | Active test rows | Declared baseline |
|---|---:|---|
| move |7,987|zero-offset top1=.933267; mean error3.23513px|
| target |5,647|nearest-target top1=1.000000; teacher repeat/collected agreement=1 on13 active targets in six held-out joint decisions|
| start |671|permit precision=.904620, recall1, missed-readiness0; hold recall0, missed1|
| release |500|permit precision=.952000, recall1, missed-readiness0; hold recall0, missed1|
| aim |1,083|zero-offset top1=.940905; mean error1.80979px|

Target is a ceiling baseline on this slice. Teacher repeat scope is explicitly a small same-state diagnostic, not all-fight repeatability or usefulness. Hold precision is undefined because it makes no positive predictions. Each of N1, N1r and N2 has NOT_RUN trained diagnostics/export parity due to the admission failure.

## Review, corrections and focused verification

The separate Codex reviewer received the owner's request verbatim; OWNER_RECHECK_STAGE1.md preserves findings and dispositions. Corrections include actual visitor assignment history for DAgger, fixed global round/visitor head weighting, crash-success refusal, supplemental-host ownership discovery, target-subgroup mean threshold, exact native impact/multiplicity/late-shell accounting, numerical parity rejection, source pins, measured baseline/fit resource receipts, and rechecking the child time allowance after ownership waits.

The first complete planned batch passed122 focused cases. Full-data conversion then exposed a real boundary discrepancy in pinned CPython3.11: at sealed fightNS1-d208feef747b50163038e32b682618fe/tick361/unit5, Python hypot returned320.00000000000006 and native hypot320.0. Native decode independently confirmed the recorded positive opportunity. The new isolated native-arithmetic namespace reuses pinned schema/join source without changing ancestor bytes, global math, observations or adding epsilon. Exact boundary/outside-range tests and stale-cache refusal cover it; the failed conversion attempt is retained separately in CONVERSION_ATTEMPT_01.json and local attempts/conversion_001.

Verification after those real changes: full corrective suite123PASS/12.36s pytest; final cache/probe Stage1 batch29PASS/2.15s; sealed-empty-tail scheduling batch31PASS/2.31s; initial targeted ownership-wait cap case1PASS/0.67s; corrective cap batch2PASS/0.69s; final invocation-budget batch4PASS/0.67s. Both runners retain one budget origin across all children, subtract historical child wall once, and charge current waits/children through elapsed time. A fixed pre-wait child deadline and re-read invocation deadline also enforce live cap reductions. Final fixtures cover fresh/historically charged waits, refusal of a second child after the resumed allowance is consumed, and an owner cap reduction during waiting. These are distinct revisions/scopes, not an inflated summed pass count. Only changed/scoped checks were repeated after concrete findings. Supplemental native buildPASS (no fights); source/object/original-binary admission remains valid. Focused parity checks cover complete actions, memory, phases/drift, launch reset and mid-sequence death using held-out records and isolated fixture sequences. They establish fixture/inference readiness; they are **not trained export parity**. The known frozen dynamics tensor-to-scalar warning occurred in old deployment fixtures only.

No original build/evidence receipts were rewritten. Committed accepted/receipt-bound code and other labs were not edited. docs/PLAN_CURRENT.md only receives a new unstaged recheck-tracking append and is explicitly excluded from the delivery commit.

.git is read-only, so no staging/commit was attempted. UNCOMMITTED_STAGE1.txt lists only new slice-folder task files, excluding all _local/data and docs/PLAN_CURRENT.md. Intended commit trailer: `Assisted-by: Codex:GPT-6`; normal hooks must remain enabled.

Claude must first run the BC sample in an environment with working process discovery. If projection exceeds60minutes, stop and ask the owner. See STAGE1_GUIDE.md for exact commands and prerequisites. DAgger/mechanism commands require actual trained, selected, parity-verified exports and retain their resource/process gates.

## 2026-10-08 corrective delivery — supersedes runtime/readiness statements above

Cross-family H1 confirmed that the original drill placements were deterministic per stratum. Original held-out baselines are duplicate-trajectory in-distribution replay diagnostics; they do not establish generalization or independent mechanism replicates. The historical 200-fight collection is preserved. The host's TRAINING_PROJECTION.json records refusal at 2,197.75 minutes (36.6 h); the earlier process-discovery-blocked account above predates that host attempt.

Current implementation adds variation and uniqueness-gated collection/conversion v2; arm-symmetric per-epoch stored-state refresh plus 30-tick burn-in/90-tick TBPTT; float64 tensor replay with cached geometry; numbered admission attempt 02; three predefined N1 seeds; minority-class metrics and binary class balancing; epoch reshuffling; N2 learned-law/phase diagnostics; full test-sequence export parity and actual student-log own-Host parity; direct N2-minus-N1/N1r mechanism contrasts; DAgger training coverage of all six cell/gun types. CONTRACT.md and historical data/receipts/projection remain unchanged. CONTRACT_AMENDMENT_STAGE1_V2.md declares the changes and their limits.

Runtime status: **NOT_RUN** for v2 collection, projection 02, fits, trained parity, DAgger and mechanism. No physical fights or training sample ran here. Under-hour feasibility remains a host measurement, not a claim. docs/PLAN_CURRENT.md is untouched by explicit owner instruction; OWNER_RECHECK_STAGE1_CROSS.md tracks this task's dispositions instead. Focused test and separate reviewer outcomes are recorded there and in new numbered evidence files. UNCOMMITTED_STAGE1_SPEED.txt enumerates this delivery for host staging with normal hooks and a provenance trailer.

Final corrective verification: 54 focused stage-1 cases PASS in 3.74 s pytest /4.638383 s wrapper (STAGE1_SPEED_TESTS_03.json). Attempts01 (pytest setup error) and02 (35 passed then N1r phase bookkeeping mismatch) remain separately preserved. The separate reviewer returned APPROVE_WITH_NOTES; all source findings were fixed, including bounded full-sequence native parity, exact child RSS/CPU, lossless feature snapshot memory, explicit gradients and host prerequisites. The new stream driver compiled successfully without fights. This completes development implementation/recheck; trained effectiveness and under-hour feasibility remain NOT_RUN.
