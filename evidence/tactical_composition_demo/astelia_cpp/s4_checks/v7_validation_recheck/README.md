# Stored v7 validation review evidence

The owner authorized stored data only, a new cross-family review and a Markdown
report. No fights, sealed render or new compute allowance are authorized here.
Existing design, plan, measurement receipts and recovery records are preserved.

`audit_stored.py` verifies raw hash chains before parsing. It independently
reconstructs terminal measurements, candidate metrics/ranking, the deterministic
CMA search, paired clusters, discordance and bootstrap. It checks final living
units/time against terminal summaries. For all telemetry fields it reuses the
reviewed sealed observation analyzer and oracle; this shared implementation is
explicitly disclosed in the review. It writes only a new `AUDIT.json` here. Do not
repeat a passed audit on unchanged code/data or overwrite its output.

The audit command used:

```sh
.venv/bin/python -u evidence/tactical_composition_demo/astelia_cpp/s4_checks/v7_validation_recheck/audit_stored.py
```

`report_from_committed_json.py` imports no engine/runner/analyzer. It reads JSON
from tuning commit `796d0a8` and validation commit `e44b528` through `git show`,
checks linked hashes and renders `astelia_cpp/S4_V7_VALIDATION_REPORT.md`.
Creation is exclusive; its read-only reproducibility check is:

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_checks/v7_validation_recheck/report_from_committed_json.py --check
```

The reviewer findings, all 32 genuine regular wins, owner request and disposition
are in `docs/reviews/tactical_0g_v7_validation_recheck_codex.md`. Additional reviewer
disposition is in `OWNER_RECHECK.md`. Final audit timing and results are in
`AUDIT.json`/logs; the focused final presentation checks are in
`FINAL_VERIFICATION.json`. Delivery identity and bundle verification are separate
transport files under `delivery/`, outside the reviewed measurements.
