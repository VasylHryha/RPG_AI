# Stage 1 BC: host handoff for attempt 03

Work in `/Users/new/RiderProjects/ai_RPG_test`. Use the existing sealed collection v2 and converted mmap data with pinned `_local/mlenv/bin/python`. Read `CONTRACT_AMENDMENT_STAGE1_V2.md`. Attempts 01/02 and all collected data remain unchanged. This handoff runs no collection, conversion, DAgger or mechanism fights.

Both recurrent arms use stored-state epoch refresh with 30-tick current-weight no-grad burn-in and the unchanged 90-tick gradient window. State is stale for at most one epoch and exact at unchanged weights; the fixtures check full replay equality. All neighbor gradients remain attached within the window. Six-tick held features, accepted assignment history, death pruning and launch resets stay explicit. Prepared geometry remains weight-independent. Features remain mmap float32; phases, memory, forcing, weights and computation remain float64. Current v2 scheduling has 516 steps and 71,508 decision rows per epoch; the host budget computes and records these totals directly from the sealed index. N2 A/B/J/share stay untrained by BC.

Training uses `_local/TRAIN_CAP.json` with `{"cap_seconds": N, "approved_by": "owner", "date": "YYYY-MM-DD"}`. Claude writes it only after owner approval. Missing file means a 3600-second default. Invalid files fail closed. Admission requires projection <= cap. Python/native children retain the 512 MiB per-process limit; five concurrent arms can require five times that memory plus the coordinator. Collection keeps its separate `LAB_CAP.json` authority. The offline admission sample stops at one hour or the smaller training cap.

The training command creates `TRAINING_PROJECTION_03.json` and `STAGE1_BUDGET_03.json`, preserving attempts 01/02. `--epochs N` applies the identical positive epoch count to every arm and all three N1 seeds. The budget records epochs, per-arm steps and rows. It never reduces epochs automatically. Do not repeat the initial command if attempt 03 exists; use `--resume` instead. An incomplete or failed timing sample refuses resume and needs inspection; never delete its receipts.

The projection uses the maximum measured step wall after excluding each arm's declared first-step warm-up. All samples, including warm-up, remain in the receipt. It adds measured chronological refresh, per-epoch validation, final validation/test/law diagnostics and full export parity. It also preserves the actual attempt-02 refused proxy total/hash and recomputes the old work-unit proxy from the new sample for comparison. Code identity changed, so the next host invocation takes nine fresh discarded steps (three per arm); attempt-02 timings are never used to admit training. Resume reuses attempt-03 measurements only if source and data identities still match.

Each N1 seed, N1r and N2 runs in its own process with torch threads 2, interop threads 1 and nice increment 10. Both `sysctl -n hw.perflevel0.physicalcpu` and `sysctl -n hw.ncpu` are recorded. The worker slots use two performance cores each, at most five processes; missing performance-core measurement falls back to one process. Longest-first lanes run sequentially within each lane and concurrently across lanes. Wall projection is the maximum lane sum, with preparation allowances and a sequential parity tail. It is a projection from isolated timing, not a measured concurrent wall guarantee; contention is unmeasured. The coordinator enters the repository process gate once, holding the stage-1 and collector locks throughout sampling, training and parity. Workers inherit those locks, so coordinator death does not unlock a still-running arm. Other tools must honor their own repository ownership gates.

Completed epochs are atomic, fsync-backed transactions in `_local/stage1_v2/epochs/<arm>/epoch_NNNN.pt`: current model, optimizer, RNG state, row/step ledger, validation history and the earliest best validation model. Final `<arm>.pt` retains the selected best weights. A killed run resumes after the last completed epoch; unfinished epoch work is discarded and rerun, with no completed epoch repeated or skipped. Resume preserves the original budget and projection, records a new local resumption receipt, validates identities, and projects only remaining work. Sealed arm outcomes and sealed export parity are reused after their hashes match. Full arm wall/CPU includes worker preparation and finalization; coordinator-observed subprocess wall is also retained. Cumulative checkpoint accounting excludes interrupted, uncheckpointed work and declares that scope. The cap applies per invocation; live owner reductions are checked at least once per second between bounded work units, and increases require a new invocation. A single in-progress optimizer step is not preempted; the coordinator terminates workers if its deadline expires.

For the existing collected/converted data, Claude should only run the training commands below. Do not recollect, reconvert, run DAgger or run mechanism fights as part of this change. First sample and inspect attempt 03 without starting final fits:

```sh
cd /Users/new/RiderProjects/ai_RPG_test
SLICE=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1
PY="$SLICE/_local/mlenv/bin/python"
"$PY" "$SLICE/stage1_train.py" --epochs 10
cat "$SLICE/TRAINING_PROJECTION_03.json"
```

After the owner approves a cap, Claude writes the approved seconds and date (these values must come from that approval):

```sh
TRAIN_CAP_SECONDS=10800  # use only if the owner approved 10800 seconds
TRAIN_CAP_DATE=2026-10-08  # actual approval date
"$PY" -c 'import json,os,sys; from pathlib import Path; p=Path(sys.argv[1]); p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(".tmp"); t.write_text(json.dumps({"cap_seconds":int(sys.argv[2]),"approved_by":"owner","date":sys.argv[3]},indent=2)+"\n"); os.replace(t,p)' "$SLICE/_local/TRAIN_CAP.json" "$TRAIN_CAP_SECONDS" "$TRAIN_CAP_DATE"
"$PY" "$SLICE/stage1_train.py" --resume --epochs 10 --run-if-admitted
```

If that host job is interrupted, use the same resume command. It refuses source/data drift or a changed epoch count; do not delete receipts or alter the matched budget to get through the gate. The 10800-second example is not an approval and was not written here.

Final selected exports undergo complete held-out native/PyTorch Host-path parity, including all six N2 ablations, at atol=rtol=1e-9. A persistent Host and Python Replay retain state across bounded 12-tick chunks; chunk boundaries never reset state. Native CPU and peak RSS come from wait4. Training produces `STAGE1_V2_RESULTS.json` only after parity passes. Per-head diagnostics, N1 seed variation, N2 learned-law statistics and fixed J motion prior remain descriptive. BC differences on a stateless teacher do not establish an RRG mechanism, usefulness, scientific acceptance or a complete H-M claim. Future DAgger/mechanism execution requires its own authorization and is outside this handoff.
