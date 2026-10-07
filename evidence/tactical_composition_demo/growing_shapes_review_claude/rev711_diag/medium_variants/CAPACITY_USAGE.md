CAP96/CAP128 scratch diagnostic tooling. Round-3 spec review: APPROVE_WITH_NOTES.
Exploratory keys 0–4 only, no experimental verdict or A7 authorization.

Run from `/Users/new/RiderProjects/ai_RPG_test`:

```sh
MV=evidence/tactical_composition_demo/growing_shapes_review_claude/rev711_diag/medium_variants
```

Both detached scratch worktrees use
`fd2182681ee8ed7b7b3a0772d69de898a8aa17c2`. The kernel builder reproduces RD3
before changing exactly its three resource-ceiling literals: ordinary-count
admission, prospective-cost admission and D3 cost trigger, together 64 → 96 or
64 → 128. All other policy constants, including the 640s assay selector, remain
unchanged. This is the coupled intervention authorized by Amendments 1–2.
`kernel_builder/CAP96_BUILD.json` and `CAP128_BUILD.json` record the parent,
patched source, helper, service graph, harness and native/world identities.
Both reproduce screening image
`b0b35a16ba134c57e56a44c9cb128b7a7ce2ae9cd4aaf836b8b1e82392c9578d`.

Build once on a clean machine; here these commands verify the existing builds:

```sh
.venv/bin/python "$MV/kernel_builder/build_capacity_kernels.py" CAP96
.venv/bin/python "$MV/kernel_builder/build_capacity_kernels.py" CAP128
```

The builder registers worktrees in the separate project-local shared clone
`_local/capacity_builder_repo`. It refuses to reset changed worktrees and compares
reproductions to immutable existing receipts. Scratch execution stubs stay in
the copied exploratory harness. Production guards and historical code stay intact.

Focused synthetic validation uses actual scratch methods, fake graphs/classes,
mocked process results and project-local temporary fixtures. It executes no native
step, assay, pilot or actual process listing:

```sh
.venv/bin/python -m pytest -q -x "$MV/test_capacity_pipeline.py"
```

Claude executes these commands with all code/build inputs frozen during execution:

```sh
.venv/bin/python "$MV/execute_capacity_plan.py"
.venv/bin/python "$MV/write_capacity_report.py"
```

Codex does not execute the pilots or scheduler here. The schedule has exactly
20 on jobs (two arms × both starts × five keys), plus one empty/key-0 off control
per arm. Both on/off pairs are dispatched first inside the single main phase.
They must match legacy summaries and full native/Python trajectory digests and
pass clone isolation. Observer state and recording remain external to clones.
At most `min(10, reported CPUs)` workers run. At ten workers, 22 fresh jobs project
as three waves using the maximum historical/current elapsed or CPU job duration;
all pending jobs, remaining jobs and off controls count toward the cap.

The independent compute-time cap defaults to 5400s. To change it before launch,
create this non-hashed file at `$MV/_local/CAPACITY_CAP.json`:

```json
{"cap_seconds": 5400}
```

It must be positive and finite. Each launch reads it once and records value/path
in its unique run ticket. It is excluded from completion identity, so changing it
preserves valid completions. A running attempt's shared deadline stays fixed;
combat waiting has a separate cap of the same duration. This compute-time cap is
distinct from the scientific resource ceiling. Projection prevents further grants
when the run would exceed its cap. macOS caffeinate surrounds actual execution.

The anchored process gate matches Python executing absolute combat script paths
under this repository's `astelia_cpp/s4_*_v1/`, and native `astelia_native*`
executables under this repository. It cannot match concurrent pgrep invocations.
Use absolute paths when launching combat scripts. Process-access errors stop
before any job starts; the Codex sandbox cannot perform this gate.

Resume with the same scheduler command. Completions must match code/build identity,
8000 steps through 800s, observer revision and ceilings, valid site counts/fractions,
160 compact capacity samples, clone isolation, full trajectory digest, and the exact
raw file set/size/SHA256. Raw files remain below 50 MB each. A started marker, raw
log, harness directory or trace without a valid completion blocks that slot from
rerunning. Preserve interrupted slots. An exclusive scheduler lock prevents competing
grants and remains after abnormal process death for inspection. Do not delete markers,
change receipts or launch `run_capacity_pilot.py` directly to obtain a grant.

The new observer reuses the revised coverage observer's integrate transitions,
restoration events and settled post-growth 0.1s counts. Only reporting cap fields
and RD3 classification under new arm names are overridden. It retains full raw
cost/count/headroom and simultaneous structural/active-service counts every 0.1s,
with compact class-mass trajectories every 5s. Cost ratios explicitly name either
structural or active-served site counts; zero denominators produce null plus a
zero-service flag. Class mass conserves ordinary bodies plus 0.1 per undirected
ordinary held pair, split 0.05 per endpoint. O and its incident pairs are free.
This is material accounting rather than signal delivery or deletion savings.

The report sums eight pooled active-served fractions across exactly ten on runs
per arm; off controls are excluded. It retains site denominators, gate A/B/E,
counts >=30%, per-run/start/key indices and paired differences, refusal outcomes,
D3 events and class-mass/cost-per-site trajectories. Both complete arms and both
passing integrity pairs are required for any reading. Invalid/missing/duplicate
evidence withholds readings and remains INCOMPLETE. The writer checks stored
completions/raw hashes and executes no medium or process listing.

Amendment 2's latest literal positive cutoff is **3.22**, with inclusive
`T_RD3 <= T_CAP96 <= T_CAP128`. The report separately discloses exact
`T_RD3 = 2.147575404987718` and exact `1.5*T_RD3 = 3.2213631074815767`;
it does not silently replace the declared literal cutoff. A positive reading means
the two doses satisfy this exploratory criterion on these keys; it establishes
neither proportional scaling nor a general efficiency law. Every other complete
outcome is descriptive; no weak/null result identifies what does or does not bind.
The withdrawn after-400s median and negative bottleneck categories are not used.

Scheduler outputs: `CAPACITY_PREFLIGHT.json`, `CAPACITY_RUN_SUMMARIES.json`.
Report outputs: `CAPACITY_COMPACT_SUMMARIES.json`, `CAPACITY_DIAGNOSTIC_REPORT.md`
(first line DONE, PARTIAL or NOT_RUN). Raw traces, tickets, markers and logs stay
under `_local/capacity/`. No historical summary or DEBT output is modified. No hash
manifest pins design/plan Markdown or cap config. Scratch Python policy source
and build inputs are identity-bound. Rechecks and dispositions are tracked in new
`docs/reviews/tactical_0h_capacity_*codex.md` files under the owner's prohibition
on editing/staging `docs/PLAN_CURRENT.md`.

If primary `.git` is read-only, delivery uses a scoped normal-hook commit in a
project-local clone and verified incremental `CAPACITY_IMPLEMENTATION.bundle`
based on the current HEAD. `CAPACITY_DELIVERY_VERIFICATION.json` records the exact
base/commit/branch/bundle identities and clean-clone fetch verification:

```sh
git bundle verify "$MV/CAPACITY_IMPLEMENTATION.bundle"
git fetch "$MV/CAPACITY_IMPLEMENTATION.bundle" capacity-codex-delivery
```
