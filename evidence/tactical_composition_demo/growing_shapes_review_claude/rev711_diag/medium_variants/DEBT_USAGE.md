DEBT scratch build and tooling delivery. Exploratory keys 0–4 only; no verdict or A7 authorization.

Run from `/Users/new/RiderProjects/ai_RPG_test`:

```sh
MV=evidence/tactical_composition_demo/growing_shapes_review_claude/rev711_diag/medium_variants
```

The local DEBT worktree is detached at `fd2182681ee8ed7b7b3a0772d69de898a8aa17c2`.
`kernel_builder/DEBT_BUILD.json` records the reproduced RD3 parent, exact Python patch,
helper, native/world source and binary identities. The screening native image is
`b0b35a16ba134c57e56a44c9cb128b7a7ce2ae9cd4aaf836b8b1e82392c9578d`.
The builder uses a separate project-local shared clone under `_local/debt_builder_repo`.
It never resets a changed worktree or edits the primary design. Scratch execution
stubs stay in the copied exploratory harness. No production gate is weakened.

On a clean machine, build once; on this workspace the command verifies the existing build:

```sh
.venv/bin/python "$MV/kernel_builder/build_debt_kernel.py" DEBT
```

Focused validation reads actual scratch methods and uses fake graphs/classes,
mocked process results, and project-local temporary fixtures. No native step,
assay, pilot, or actual process listing executes:

```sh
.venv/bin/python -m pytest -q -x "$MV/test_debt_pipeline.py"
```

Claude executes the scheduler and report writer, with all code frozen during execution:

```sh
.venv/bin/python "$MV/execute_debt_plan.py"
.venv/bin/python "$MV/write_debt_report.py"
```

The schedule contains ten observer-on jobs (DEBT × starts i/ii × keys 0–4)
and exactly one off control (empty start/key 0). The on/off pair is dispatched
first inside the single main phase. Summary bytes, full trajectory digest
(including debt and native/Python state), and clone isolation must match.
No fresh §19.7 keys are used. Codex does not execute either command here.

The cap defaults to 5400 seconds. To configure it before launching, create the
following non-hashed file at `$MV/_local/DEBT_CAP.json`:

```json
{"cap_seconds": 5400}
```

The scheduler reads this file at every launch, requires a positive finite value,
and records the value and path in that attempt's run ticket. The cap file is
excluded from completion identity; a cap change permits reuse of valid completed
slots. A running ticket's deadline remains fixed. Keep all code/build files
unchanged between attempts. Run tickets are unique and retained; never edit them.

Workers are `min(10, reported CPUs)`. Projection includes pending jobs, remaining
jobs and the off control, rounded into waves, using the maximum historical/current
elapsed or CPU worker time. At ten workers, eleven fresh jobs require two waves.
The scheduler stops launching when projection exceeds the launch cap. Combat
waiting has its own cap of the same duration; actual execution has one shared
deadline. On macOS caffeinate surrounds execution, and is omitted if every slot
is already complete.

The anchored process gate matches Python executing absolute paths beneath this
repository's `astelia_cpp/s4_*_v1/`, and `astelia_native*` executables beneath this
repository. It cannot match a concurrent `pgrep`. Launch concurrent Python combat
scripts using absolute paths. Process-access errors stop before any job starts;
the Codex sandbox cannot perform this gate, so Claude is the executor.

Resume uses the same scheduler command. It verifies completion code/build identity,
8000 steps through 800s, 8000 observer debt boundaries, clone isolation and the exact
raw file set/size/SHA256. Any started marker, job log, harness directory or raw trace
without a valid completion prevents that slot from running again. Preserve and
report interrupted slots. The exclusive scheduler lock prevents competing grants;
an abnormal exit retains it for inspection. Do not delete markers or change receipts
to obtain a grant. Never launch `run_debt_pilot.py` directly.

The law updates kernel-owned debt once per completed integrate boundary, before
adaptation/timers/growth, using all-site structural service. Only active-unserved
sites receive floating +0.1; debt is never reset. Clones copy debt independently.
B-path sorts initial active-unserved candidates by finite deficit first, descending
debt within each class, then pointer-relative ID. It retains live connectivity checks,
the two accepted-birth quota, output-first repeat, resource-stop, pointer advance,
B1, D3, placement and budget. No intra-check debt update occurs.

The observer reuses unchanged coverage Amendment-1 logic. Every debt boundary is
retained in compressed raw telemetry; compact summaries sample debt/mass at 5s.
It computes the COV-A waiting clock independently on this DEBT history and records
initial order comparisons with RD3 and COV-A, plus the diagnostic's separate
pure-debt order. These are fixed-history comparisons, not counterfactual acceptances.
Settled post-growth coverage and pre-growth integrate debt have distinct boundaries.
Mass partitions conserve current ordinary-plus-held-pair cost; O is free.

Report outputs are new `DEBT_COMPACT_SUMMARIES.json` and `DEBT_PILOT_REPORT.md`;
scheduler outputs are new `DEBT_PREFLIGHT.json` and `DEBT_RUN_SUMMARIES.json`.
Raw traces/tickets/markers/logs remain under `_local/debt/`. Historical RD3 and
COV-A summaries are parsed unchanged. The report inspects interrupted work even
without a scheduler receipt. Missing runs or failed integrity remain INCOMPLETE.

Coverage improves only at the specified pooled sites 3–6 threshold, four empty
passes, ten complete on jobs, and the integrity pair. The spec leaves fairness
minimum aggregation unresolved. Both the minimum of eight pooled site fractions
and all per-run minima are reported, with matching COV-A denominators; the
unqualified FAIRER_THAN_COVA label is withheld pending drafter clarification.
This report limitation changes no DEBT behavior.

The spec and implementation reviews are in `docs/reviews/tactical_0h_debt_*codex.md`.
Rechecks are tracked there under the owner's prohibition on editing/staging
`docs/PLAN_CURRENT.md`. No completion hash manifest pins Markdown design/plan
documents or cap config. Source code (including scratch `rev7_design.py`) and
build/receipt identities remain pinned. Existing committed evidence is unchanged.

If primary `.git` is read-only, the fallback verified bundle is
`DEBT_PILOT_IMPLEMENTATION.bundle`, based on the delivery HEAD recorded in
`DEBT_DELIVERY_VERIFICATION.json`. Its scoped commit uses repository hooks and
`Assisted-by: Codex:GPT-6`. Source and build receipts are packaged; raw/build
products remain local and rebuildable:

```sh
git bundle verify "$MV/DEBT_PILOT_IMPLEMENTATION.bundle"
git fetch "$MV/DEBT_PILOT_IMPLEMENTATION.bundle" debt-pilot-codex-delivery
```
