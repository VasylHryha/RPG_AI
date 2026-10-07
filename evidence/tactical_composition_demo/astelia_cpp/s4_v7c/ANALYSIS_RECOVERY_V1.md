# Stored-only interruption recovery v1

Owner-authorized recovery of `ATTEMPT_eb681c6dfe8240248636f44adbcd5a4d.json`, stage `analyze_validate`, started `2026-10-07T18:06:31Z`. The owner reports reboot at approximately 21:51 local / 18:51Z because another session froze the laptop. The RUNNING receipt is preserved, never closed or rewritten.

`INTERRUPTION_95d7e6ccbe1043eda90e3b0ea8fe7055.json` binds its exact bytes, stage, start time, declaration, cause and stored-only provenance. `sysctl kern.boottime` was attempted and denied; its command, return code and error are retained. The charge is the entire elapsed wall time until the recovery observation: **3377.771384 s**, including downtime. The approximate owner reboot time is not treated as an exact timestamp or used to discount compute. Added to the closed validation attempt's **227.16235725 s**, cumulative compute is **3604.93374125 s**. No allowance is reset or clipped. The 3600 s cap is exhausted, so neither analysis nor rendering is started. No fight executed during this recovery. Recovery observation was taken at 19:02:48.771384Z; the broad wall-time bound deliberately extends beyond the approximate reboot.

The versioned launcher `analysis_recovery_v1.py` is the only runtime change. It runs the unchanged `analyze.py`/`render.py` entry points with a temporary replacement for `common.spent`, only within a stored-only launch. Every unclosed attempt needs one identity-matching interruption record for exactly `analyze_validate` or `render_validate`. Unclosed combat/unknown stages, missing records, duplicate/orphan records, changed receipts, nonfinite/negative charges, undercharges and bounds preceding the recorded recovery observation fail closed. Supplemental seal verification requires every core recovery/original binding, every interruption, the original delivery identity and the unchanged cap. `run.execute` is disabled during the launch; changes are restored on exit. Direct original commands keep refusing the unclosed attempt, including `run.py validate`. There is no combat recovery entry point.

Analysis imports `common`, `protocol`, read-only helpers from `run`, and the observation-only `s4_escort_probe_v3/metrics.py`. `run` defines combat code but its main invocation is guarded by `if __name__ == '__main__'`; importing it executes no fight. Analysis calls stored receipt/hash/telemetry readers and unchanged scientific functions. Rendering reads stored analysis and emits HTML. Neither stored entry point calls `execute`, `Executor`, or the native host. The existing `attempt` context and absolute deadline/cumulative cap remain authoritative.

`ANALYSIS_RECOVERY_V1_MANIFEST.json` is an additive post-validation analysis-recovery seal. It binds the new implementation, tests, interruption and preservation snapshot, plus the ORIGINAL declaration/seal and entry points. This uses the owner's explicit versioned-analysis-recovery exception; it does not reseal validation, replace historical hashes, allocate entropy, change requests or authorize fresh validation. No existing s4_v7c file is edited. All validation fights, raw traces/claims/completions, theta*, entropy, native sources/binary, protocol/readings and original evidence are untouched. `RECOVERY_V1_PRESERVATION.json` records hashes, sizes and mtimes of 2186 original artifacts and both protected documents; the read-only verifier checks them alongside all original seal pins and PLAN staging.

Audit commands from repository root:

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/analysis_recovery_v1.py ledger validate
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/verify_analysis_recovery_v1.py
```

Versioned stored entry points (currently refuse because the cumulative cap is exhausted; do not reset it):

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/analysis_recovery_v1.py analyze validate
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/analysis_recovery_v1.py render validate
```

| Stop condition (yes/no) | Action | Responsible role |
|---|---|---|
| Does any unclosed attempt lack a valid stored-only interruption? | Refuse further attempts | implementer |
| Is any unclosed combat attempt present? | Preserve and refuse recovery | implementer |
| Does any original/supplemental seal or preservation check fail? | Stop and investigate without editing historical evidence | implementer |
| Is cumulative compute at least 3600 s? | Stop without starting analysis/render or creating an attempt | executor |
| Is an exact reboot bound unavailable? | Charge through recovery observation, including downtime | implementer |

The owner recheck and disposition live in new `RECOVERY_V1_OWNER_RECHECK.md`, because this task explicitly forbids editing `docs/PLAN_CURRENT.md`. No scientific acceptance or S5 authorization is claimed.

Final verification: 53 fake-receipt/manifest/runtime/cap tests passed (pytest 1.62 s; measured process 3.01241325 s). Initial collection failure is retained separately; no tests or fights ran in that attempt. Independent Codex fallback recheck APPROVE after all fixes; preferred Claude was unauthenticated. No full repository suite, parser fixture or combat pipeline was run because this authorization is stored data only.
