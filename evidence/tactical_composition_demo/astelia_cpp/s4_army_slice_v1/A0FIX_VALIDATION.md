A0 transport fix validation, 2026-10-09 local time.

Ran focused tests and real-host integration together once after the complete code/test and recheck batch:

```sh
.venv/bin/python -m pytest -q evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/test_a0.py evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/test_a0_host.py
```

Result: **29 passed in 6.33 seconds** (26 focused cases and three real native fights). No tests were repeated. Process discovery and live RAM checks succeeded for all three host fixtures; no gate or resource check was mocked in the integration tests. The build succeeded, with native binary bytes identical to the sealed original. Final build time: 23.1 seconds. Sandbox build subprocesses emitted `nice: setpriority: Operation not permitted` but returned success; real host invocations had empty stderr.

| Arm | Simulated seconds | Executed label rows | Wall seconds |
|---|---:|---:|---:|
| O | 3.033333 | 4550 | 0.597 |
| O+G | 3.033333 | 4550 | 0.606 |
| T | 3.033333 | 4550 | 0.590 |

Each fixture is a separately sealed three-second copy of the first real regular pilot request for that arm. The production launcher generated one compact JSON line, with no `--metrics`, and `a0_metrics.measure()` successfully parsed all observer frames and the terminal summary. All three role label counts were nonzero. Raw, attempt/completion receipts, fixture requests and CLEAR process-gate receipts are retained locally in `_local/a0fix_host_smoke/`; they are test-only evidence and are not pilot/outcome data.

The explicit `repair-tooling` command succeeded. It preserved the original ledger/declaration, requests and failed raw/attempt files, and records the cause, original/current fingerprints, unchanged binary identity and retry permission in `A0_TOOLING_RECOVERY.json`. All 625 snapshotted preexisting sealed/evidence file hashes are unchanged. The original build receipt and binary manifest were copied into `_local/a0fix_before/` before rebuilding. The failed run receipt remains unchanged. The failed stream contains only parser errors (103 invalid JSON, 218 invalid JSON number, 755 trailing JSON input), with no valid fight data.

A new pilot invocation may retry the failed job under a new attempt ID. Each retry names and hashes prior attempt receipts, records their individual causes and preserves original raw bytes. Unknown failures block replay pending explicit diagnosis. The full eighteen-fight pilot and all outcome runs remain pending; this fix makes no fight-result or scientific claim. The separate recheck found one logging issue, now fixed and covered; no remaining blocking findings. No living documents are pinned and PLAN_CURRENT was not changed.
