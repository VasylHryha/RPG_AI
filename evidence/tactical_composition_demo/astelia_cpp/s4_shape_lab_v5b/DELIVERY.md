Delivered uncommitted: this workspace permits reading `.git` but not writing
it (`test -w .git` is false). No staging, commit, hook bypass or push attempted.
All deliverable files are listed with exact paths and hashes in DELIVERY.json.
The only file outside the new v5b folder written by this task is the required
unstaged recheck tracking append in docs/PLAN_CURRENT.md; exclude that file.

New files consist of the v5b runner/admission/request/metric/report/replay
tooling and tests; unchanged inherited declaration/build/prepare/mechanism
receipts and seed ledger; 220 groups of COMPLETE/request/CLAIM/stderr bytes;
frozen declared spec/decision; abandoned attempt/observations audit copies;
profile diagnosis and text trace; one-pass review/disposition; focused test
logs and measured no-fight calibration timing receipts. Compressed raw streams
remain in v5 and are never copied into the commit. Local profiler binary,
scratch and caches are ignored. No other lab was edited by this task.

Focused batch: 19 PASS in 19.80 s (20.427 s process). Real recorded-receipt
outcome calibration preflight: 1.718 s. Full calibration control flow with
synthetic outcomes: 3.179 s. No native fights or new mechanism selection.
Actual combat calibration runtime has not been measured. The separate
reviewer's single finding was fixed before this test batch; its disposition
is appended to OWNER_RECHECK.md without rewriting the original verdict.

Claude starts here, from repository root:

```sh
LAB=evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v5b/lab.py
.venv/bin/python -B "$LAB" calibrate --stage outcome --look 50 --preflight-only
.venv/bin/python -B "$LAB" calibrate --stage outcome --look 50
.venv/bin/python -B "$LAB" run --stage outcome --look 50
.venv/bin/python -B "$LAB" report
```

Read the 50-pair outcome summary before recording continue/stop. Exact later
look/review/series commands and stop conditions are in README.md. No new
prepare, mechanism calibration/run or pick. If committing this delivery from
a writable host, stage only `s4_shape_lab_v5b/` paths from DELIVERY.json (plus
the delivery files), preserve unrelated staged changes, use normal hooks,
and include `Assisted-by: Codex:GPT-6`. Never stage docs/PLAN_CURRENT.md.
