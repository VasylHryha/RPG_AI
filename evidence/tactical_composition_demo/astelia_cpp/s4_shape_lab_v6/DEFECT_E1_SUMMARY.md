# E1 summary/report defect and R2 repair

Development reporting repair only. No new fights, entropy, calibration, selection,
scientific acceptance, or owner read decision. Historical receipts remain intact.
Commit `8fb23d0f230d295f876a4771a16517cb1ac2a79d` records the original defect.

The original CLI executes `lab.py` as `__main__`, setting that module's
`SELECTED_ARM=E1`. `stage_summary()` names its file from this CLI state, then
imports `report`. `report.py` imports a second `lab` module, whose selected arm
is the default V2. It calculates a V2/D1+V2D2 summary under the E1 filename.
`e1_fix_diagnostics/original_report_stack.log` reproduces the E1 filename,
V2 summary arm and D1/V2D2 drills using the saved source copy and empty synthetic
records. The real original receipt has the same mismatched identity.

The apparent hangs are expensive work after fight execution. `run()` writes
DONE and then invokes `report()`. Report renders every arm, every outcome look,
and series, repeatedly collecting all completions. Each `verified_record()`
decodes the full JSONL stream to find its terminal, then `measure()` decodes it
again. It also repeatedly hashes all native/source identities without caching.
After aggregation, `render_selected()` regenerates selected replay telemetry.
Bounded copied-code diagnosis was terminated after 12 seconds; stack dumps
show `json.decoder.raw_decode` and `metrics.measure` actively processing raw
telemetry. This is consistent with the original process remaining busy after
DONE, not evidence of a stuck fight or an executor deadlock. The historical
10-minute incident itself was not rerun. The v5b README/lab receipt-reuse fix
provides the same remedy: bind the already-measured receipt to its exact raw
bytes, then verify hashes rather than decoding and remeasuring on admission.

`lab.py` now dispatches CLI commands to canonical `lab_r2`; `report_r2` imports
that same module and takes the arm explicitly. The old lab source is retained
at `e1_fix_diagnostics/original/lab.py` and must match its original declaration
pin. `E1_REPORTING_R2.json` binds the original declaration, unchanged metrics,
324 existing measured completion receipts, and the revised executable tooling.
Reused receipts still verify request/claim/declaration/timing links, raw and
stderr hashes, native fight count and controller failures. New completions
receive a separate R2 measurement seal after their first measurement. Hashes
are streamed and cached only while device/inode/size/mtime/ctime are unchanged.
No new manifest adds a living plan, DESIGN document or SHAPE_LAB_SPEC execution
pin. Existing historical declaration pins, including frozen document copies,
are retained unchanged.

Reports collect selected-arm receipts once per stage and reuse those snapshots
for sequential looks. They write revision-labelled report/chart/observation
files, preserve existing replay exports, and do not regenerate raw replays.
The E1 mechanism summary is exclusively `MECHANISM_E1_SUMMARY_R2.json`; both
review and dependency gates bind that corrected file. A repeated completed
`run` only reports the existing DONE stage and cannot replace its RUN/gate/
attempt receipts or run another fight. Original `MECHANISM_E1_SUMMARY.json`,
RUN files, and raw receipts are preserved for audit.

The final actual CLI profile completed in 3.334 seconds, versus the original bounded
report which had not completed at 12 seconds. See
`e1_fix_diagnostics/fixed_report_profile.txt` and `fixed_report_timing.json`.
The fixed profile contains no calls to `metrics.measure` or gzip telemetry
JSON decoding. The profile's historical-receipt hash check passed. Final
unprofiled checks completed E1 report in 2.423 s, completed E1 run/report
in 2.408 s, and V2 report in 4.144 s. `VERIFY_E1_R2.json` checks all 324
inherited receipts and their raw/request/claim/stderr sidecars, plus 53
historical JSON artifacts, before and after those commands.

The corrected data are 20 D5 base + 20 D5 E1 fights, 20 matched pairs, complete.
E1 and base both have zero engagement-floor ticks, 9,337 shots, zero ranged
deaths, 2,512.8 eligible seconds and 4,617.8667 ready seconds. The declared
activation gate is false. These measurements do not support proceeding to E1
outcomes or rotation; Claude still owns the actual mechanism read/stop receipt.
No read decision was issued by this repair. The historical `metrics.paired`
alphabetically sorts arms, so its explicitly labelled signed comparison is
`base minus E1`. The declared usual candidate-minus-reference reading must
reverse that direction; all these E1 differences are zero. R2 preserves the
original metric definition.

The separate reviewer found and fixed a stale-summary case when a required
completion disappeared, an inaccurate no-outcome chart caption, and receipt
sorting which perturbed floating sums and broke historical V2 equality. R2
records original receipt iteration order in `E1_REPORTING_R2.json` and preserves
it for every inherited aggregate; synthetic regression covers that order.
The initial sorted R2 summary is retained only as a superseded development
attempt in `e1_fix_diagnostics/MECHANISM_E1_SUMMARY_R2_ATTEMPT_SORTED.json`.
Final verification is one focused batch: 23 tests passed in 1.58 s (1.899 s
including the runner), with zero fights and native fixture outputs redirected
to the diagnostics directory so original fixture receipts stay unchanged.

The owner's recheck and disposition are recorded in `OWNER_RECHECK_E1_R2.md`.
Per the task's explicit exclusion, `docs/PLAN_CURRENT.md` is untouched. Focused
verification is recorded in `e1_fix_diagnostics/TESTS_E1_R2.json`. `.git` is
read-only in this sandbox, so task paths are listed in `UNCOMMITTED_E1_FIX.txt`.
`nice -n 19` was requested but rejected by the sandbox (`Operation not
permitted`); diagnostics used one bounded worker and no native fights.

Claude commands from repository root:

```sh
LAB=evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v6/lab.py
nice -n 19 .venv/bin/python -B "$LAB" report --arm E1
cat evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v6/MECHANISM_E1_SUMMARY_R2.json
# After reading the corrected activation/utilization and tradeoff data:
nice -n 19 .venv/bin/python -B "$LAB" review --arm E1 --stage mechanism --decision stop --note "20 D5 pairs: zero E1 engagement-floor ticks; measured totals match base. Park E1: activation gate failed."
```
