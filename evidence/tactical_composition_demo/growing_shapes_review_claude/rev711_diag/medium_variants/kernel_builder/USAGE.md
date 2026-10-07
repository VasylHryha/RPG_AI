A6w/A6x scratch implementation, exploratory only, no verdict.

Run from the repository root using the project Python environment. Set `MV=evidence/tactical_composition_demo/growing_shapes_review_claude/rev711_diag/medium_variants`.

Build order is SCR, V1, RD3. Each is a detached `fd21826` worktree. The builder refuses to reset or repatch existing changed worktrees; retain the successful receipts and binaries. If the environment denies Git mutations inside Python, create each worktree with the explicit `git worktree add --detach "$MV/kernel_builder/_worktrees/SCR" fd21826` command (substitute V1 and RD3), then run the builder on that unmodified worktree.

```sh
.venv/bin/python "$MV/kernel_builder/build_kernels.py" SCR
.venv/bin/python "$MV/kernel_builder/build_kernels.py" V1
.venv/bin/python "$MV/kernel_builder/build_kernels.py" RD3
.venv/bin/python -m pytest -q -x "$MV/test_service_telemetry.py"
.venv/bin/python "$MV/execute_service_plan.py"
.venv/bin/python "$MV/write_service_report.py"
```

Execution stops if pgrep cannot see processes, waits for matching combat hosts to finish, and stops when projected remaining compute would exceed the one-hour cap. Every phase uses a shared deadline and at most ten workers. A started marker forbids retries of that variant/start/key/observer slot. No code edits during runs. The off control is the sole additional complete run; SCR i/key0 on is reused as Part A's once-only slot. Part A includes exactly 20 on runs; RD3 includes 10 on runs. Exact reproduction of all SCR and V1 log dictionaries is required before RD3 executes.

The historical native source hashes are frozen in HISTORICAL_SCREENING_IDENTITY.json. Those tracked inputs at fd21826 already match the earlier scratch build's source hashes. The missing untracked inputs are rebuilt native binaries/manifests; the scratch Execution and assert_inputs stubs are copied from the committed pilot_common_scratch.py into the scratch worktree only. They do not weaken any production gate. A fixed Mach-O install-name string reproduces the historical image bytes without accessing historical temporary files.

Raw training/telemetry traces, job logs, started markers and tickets live only in gitignored `_local/`; successful compact run JSON records each raw trace's size and SHA256. `SERVICE_COMPACT_SUMMARIES.json` and `SERVICE_TELEMETRY_REPORT.md` carry missing-data states explicitly. Do not launch the worker directly or edit the grant ticket. Fresh section-19.7 entropy is absent from this scheduler.
