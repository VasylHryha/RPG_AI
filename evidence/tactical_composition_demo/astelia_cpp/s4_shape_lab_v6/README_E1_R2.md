# E1 reporting repair

Use the existing `lab.py report --arm E1` command. It writes
`MECHANISM_E1_SUMMARY_R2.json`, `OBSERVATIONS_E1_R2.json`,
`SHAPE_LAB_REPORT_E1_R2.md`, and `AXIS_CHART_E1_R2.{json,svg}`.
Read the R2 summary; the original E1 summary accidentally contains V2 data.
The corrected E1 activation gate is false. No E1 continuation is authorized.

See `DEFECT_E1_SUMMARY.md` for causes, preserved receipt identities, measured
profiling, review disposition and exact Claude read/stop commands. Receipt
reuse verifies hashes and original measured values without new fights. Report
commands do not regenerate replay telemetry. The revision CLI uses one shared
module identity for its selected arm. Historical imported `lab` and `report`
APIs remain available for the original synthetic fixture tests.
