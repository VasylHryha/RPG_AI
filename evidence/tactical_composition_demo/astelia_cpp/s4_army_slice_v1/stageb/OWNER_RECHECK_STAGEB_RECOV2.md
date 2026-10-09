# Stage B chained launcher recovery, revision 2

Owner-requested quick fix under decision 0036, based on f0426d3063655dc30d3c53b52551c25d26d9bbaa. Changes stay in stageb; no changes to stageb2, stagea, rev2 or docs/PLAN_CURRENT.md. No full refit or fresh fights ran.

The original sealed recovery receipt remains byte-identical. RECOVERY_STAGEB_EVAL_ROUND0_V2.json links its name and file SHA256, binds the current launcher and fixture hashes, and records the launcher change adding run for rounds 1-2. Its training_sources and approved evaluation_changes match the round-0 recovery/budget. Verification still checks the original admitted budget, index, raw shards, completed fits, all preserved training artifacts and original parity receipts, contemporaneous native sources/build/binary, and the exact approved evaluator revision.

Historical recovery tooling hashes are checked against sealed ancestors; only the chain head pins live tooling. Future tooling edits require an explicit new sealed head, using recover-eval-chain --round 0 --revision 3 (then successive revisions), but do not invalidate or rewrite ancestors. Automatically accepting unsealed future launcher code would lose the requested launcher hash binding. Training-relevant changes cannot be admitted by a new head.

The completed round-1 DAgger ledger also pins the original recovery tooling. The launcher accepts only exact source maps already present in the verified chain, while retaining parent parity, binary and request checks. Aggregate completion/shard and per-arm dataset validation still use the original training functions. No source map, budget, dataset, native build, fitted artifact, or existing DAgger ledger is rewritten. Current measurements continue to register the real current source map.

Later training workers launch through eval_revision.py worker with the same inherited locks, time/RAM admission, cap and original fit function. Parity and readout commands install the same process-local gates. Use launcher readout-prepare/readout-run; direct legacy entrypoints retain their strict historical ledger refusal.

## Separate owner recheck and disposition

Reviewer: separate Codex agent, read-only; another model family was unavailable through the collaboration interface. Request sent verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Two blocking findings were fixed before the single focused test run:

- The subprocess adapter omitted STDOUT, which the original training runner uses before spawning. The adapter now retains it.
- The parity fixture retained imported ROOT/configure bindings. Those bindings now point to the fixture, and installed module gates are restored after tests.

The reviewer found no further blocker in chain integrity or training drift refusal, and confirmed that the actual round-1 DAgger ledger sources equal the original sealed recovery source map. The reviewer required bounded reporting for mocked numerical work and children; that limitation is recorded below.

After validation, the same reviewer checked the final report and V2 receipt: no reporting gaps or remaining blockers; seal, parent hash, training/evaluation proofs and live tooling hashes match. No tests were rerun and no code changed in this closure.

## Validation

One focused invocation with the pinned ML Python: test_eval_revision.py, 70 passed in 2.19 seconds; actual process wall time 2.662 seconds. Fixtures cover training drift before recovery, after the original receipt and after the chain; budget/index/shard/export/native/receipt/tooling drift; resealed ancestor/link/proof tampering; chain gaps; idempotence; successive heads; historical DAgger request/source checks; and original cached parity preservation. The round-1 fixture runs the real measurement, training orchestration, calibrated-completion checks, parity orchestration and parity gate. Numerical model work, process admission and worker subprocess execution are substituted with fixtures. It proves orchestration and receipt/gate integration, not a fresh worker process, numerical fit or host performance.

The actual recover-eval-chain --round 0 command sealed revision 2. Read-only verified_dagger(1), using the installed gates, validated the completed 88-fight aggregate. Combined wall time was 4.289 seconds. The original recovery file hash stayed unchanged. No measured round-1 budget was created in this session; the owner's host measure command remains the live time admission for the refit (reported prior estimate 225 minutes, hard maximum 4.5 hours).

## Host sequence

Run from /Users/new/RiderProjects/ai_RPG_test. Keep sources unchanged after measurement and through parity/readout. recover-eval-chain is idempotent for the existing matching revision-2 head.

```sh
set -e
export STAGEB=evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stageb
export STAGEB_PYTHON=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/_local/mlenv/bin/python
export PYTHONPYCACHEPREFIX="$STAGEB/_local/pycache"
"$STAGEB_PYTHON" "$STAGEB/eval_revision.py" recover-eval-chain --round 0 --revision 2
"$STAGEB_PYTHON" "$STAGEB/eval_revision.py" measure --round 1
"$STAGEB_PYTHON" "$STAGEB/eval_revision.py" run --round 1
"$STAGEB_PYTHON" "$STAGEB/eval_revision.py" parity --round 1
"$STAGEB_PYTHON" "$STAGEB/eval_revision.py" readout-prepare --round 1
"$STAGEB_PYTHON" "$STAGEB/eval_revision.py" readout-run --round 1 --look 20
```
