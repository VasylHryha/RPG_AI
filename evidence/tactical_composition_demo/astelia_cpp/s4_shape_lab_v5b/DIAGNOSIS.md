The 120 s read-only profile confirms finite repeated work before execution,
not evidence of an infinite native fight. At the limit, v5 had called
`verified_record` 503 times, `identity` 505 times, `stage_summary` three times,
and `selected_knobs` twice. 1,472,008 JSON decodes consumed 71.559 s cumulatively
(65.449 s inside raw_decode); `metrics.measure` accounted for 52.398 s and
identity checks for 16.528 s, overlapping the overall verification time.
The 90 s stack is preserved in V5_FAULTHANDLER.log; this sample was inside
identity called from selected_knobs → stage_summary → records_for.

Each summary scans all 220 completed mechanism streams. Each completion is
decoded once to check its terminal and again to re-measure statistics that
are already in its receipt. `plan('outcome', 50)` calls `selected_knobs` inside
the draw/arm loop, causing 150 full mechanism scans per plan. `samples_for`
and the calibration task list each consume such a plan before starting a
fight. This explains prolonged 100% CPU before execution. The actual recorded
inventory is 220 COMPLETE receipts, not 540 distinct fights (1102 raw files
including their companions, seed ledger and lock).

diagnose_v5.py called the real v5 calibrate function with compute_attempt and
all writes blocked, no execution_lock creation, a 120 s alarm, cProfile and
a 90 s faulthandler timer. It temporarily installed only the declared spec
bytes from bc8ed24 after checking their declaration hash, then restored the
original HEAD bytes in a finally block. No fight, process gate or compute
attempt was opened. V5_DIAGNOSIS.json records the restored spec hash and
zero fights. No existing receipt or lab source was edited.

v5b uses receipt-hash admission for already measured statistics and raw-hash
admission for compressed streams; new completions bind the measured receipt
through a measurement seal. The original pick is resolved once per plan, and
unchanged file hashes use stat-invalidated process caches. The mechanism
summary is still recomputed from receipt statistics in the preserved original
receipt order, and must equal the original summary exactly. Source/binary,
request/claim, terminal failure, stage/read, lock, cap and process gates remain.
The living spec/decision paths resolve instead to the exact frozen v5 bytes.

Measured after all changes and the one-pass reviewer correction: real CLI
calibrate outcome --look 50 --preflight-only completed in 1.717503 s. The full
calibrate path including calibration receipt and cost projection completed
in 3.178716 s using synthetic outcome samples in scratch. The 19 focused cases
passed once in 19.80 s. Neither timing includes outcome combat: Claude must
run actual calibration and outcome fights, observing the declared look gates.
