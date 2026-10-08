# Stage 1 BC and future runs

The implementation is delivered in new files; current runtime disposition is in REPORT_STAGE1.md. Collected data, inventory, entropy, ledger, contract and original net_host are unchanged. No DAgger or mechanism fights ran. Use the pinned CPU environment; no workspace lock/environment change.

`stage1_data.py receipt` verifies all 200 immutable fight files/receipts and produces compact COLLECTION_RECEIPT.json. `convert` streams 180 eligible fights into local mmap arrays; 20 report-only fights are excluded. Each fight retains its sealed whole-fight split, physical tick geometry, persistent IDs, accepted visitor assignment history, launch acknowledgements, decision features/labels/masks and teacher-target-conditioned legal support. No native launch becomes an earlier training label. Conversion caches fail on arithmetic/data drift; interrupted attempts remain separate.

Pinned Python 3.11 hypot and native libm can differ at exact boundaries. stage1_arithmetic.py gives the pinned schema/join functions private namespaces with native hypot; it changes no global math or ancestor bytes, adds no epsilon, and changes no observations. Native threshold semantics apply to masks, support, encoded readiness, inference and graphs. Exact boundary and outside-range fixtures document this. Old conversion attempt data is preserved under _local/stage1/attempts/conversion_001.

`stage1_train.py --run-if-admitted` first measures nine optimizer steps total (three per arm, same early/middle/late-prefix batches). Sample models/optimizer states are discarded. It projects all three sequential ten-epoch fits plus ten validation passes and test diagnostics. Total projection >=3600 seconds stops after the sample for Claude's owner discussion; measured RSS >512 MiB or numerical failure also refuses. No training starts without repository process discovery. Actual wall/CPU/RSS/latency/RHS/disk measurements are recorded. Source and data hashes bind the declared budget.

Every arm receives the same 90-tick, four-world/window schedule: currently 772 steps/epoch, ten epochs, 7,720 gradient steps and 954,000 gun-decision rows per arm. Zero-row windows after every gun dies are excluded; partial last-live windows remain. Exact scheduled row totals are checked. N1r/N2 reconstruct the complete chronological prefix under current weights with no_grad and detach once at the window boundary. All neighbor gradients remain attached inside the window. Six-tick held features, recorded previous accepted assignments, death pruning and actual-launch resets are explicit. Adam has zero weight decay, clipping norm1 and the contract's masked CE/BCE head weights; positive fire weights come from training only. N2 A/B/J/share raw coordinates and inherited optimizer moments remain zero. CPU Torch threads4/interop1/workers0; no concurrent fits.

Checkpoint selection is minimum validation weighted masked loss with earliest ties. All ten epochs run for the matched budget. Per-head held-out diagnostics compare target against nearest and measured teacher repeat, fire against hold/permit, and move/aim against zero-offset and training majority. Unsupported/numerical failures stop; ceiling/undefined diagnostic heads do not establish usefulness or prevent mechanism review by themselves.

`stage1_native.py build` creates a separate local stage1_host against admitted objects. Original binary is never overwritten. A read-only shell-impact hook observes the exact native post-walk/pre-damage point and reports terminal native raw HP-capped attack totals, including shells after all own guns die. The hook adds no policy behavior. `stage1_export.py` exports selected checkpoints and checks float64 native/PyTorch held-out full sequences (actions, recurrent memory, phases, drift, launch reset) at atol=rtol=1e-9; all N2 ablations are included. This is inference/state parity, not fight usefulness or scientific acceptance. Focused tests also exercise a death mid-sequence.

DAgger seals ten trajectories per visitor per round, two visits to each sparse D1/1 and D2/1 cell, then six two/ten-gun visits. Student actions are never mixed with teacher actions; the constrained teacher shadows the same decision tick without physical advancement. Previous assignment history remains the actual visitor's. All arms refit the same union including round0, using fixed global masked-head denominators with round/visitor balanced gun-row weights. Validation uses its own corresponding balanced strata; test/report data never enter fitting/selection. Two rounds only; 30 physical attempts and 225,000 decision-row queries per round, including unsuccessful attempts. Successful crash boundaries are reconciled by immutable complete receipts or refused for inspection, never silently relaunched.

Mechanism checks use 10–20 fresh independent draws per arm; all arms share each draw's seed/cell/placement/orientation. Default12 covers every cell × guns × orientation stratum. Arms are the constrained teacher, BC N1/N1r/N2, and six N2 ablations. Source/weight/driver inventories are sealed before launch. One native process; repository ownership gate and the owner's live LAB_CAP.json control execution. Partial/failed attempts are preserved and charged. Reports retain all paired fights, both axes, deaths, kills, ratio of totals (null for zero deaths), fire/participation, raw illegal attempts per decision separately from ordinary finite movement projection and cast vetoes, native damage/hits, launch/landing spreads, exact original-target dodge success with death censoring, unresolved shells and matched recorded-context kicks. Productive-cell guard is launch/opportunity >=.25 and enemy kills>0. No 10–20-pair formal outcome reading is produced: those require the contract's50/100/200 looks. No hierarchy or complete H-M proof is claimed.

From repository root, first complete BC timing/training in an environment where process discovery works:

```sh
SLICE=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1
PY="$SLICE/_local/mlenv/bin/python"
"$PY" "$SLICE/stage1_train.py" --run-if-admitted
```

If projection exceeds one hour, stop; Claude asks the owner. DAgger and mechanism commands below require trained, selected, parity-verified checkpoints. They are handoff commands, not execution already performed:

```sh
"$PY" "$SLICE/stage1_dagger.py" --round 1 --refit-if-admitted
"$PY" "$SLICE/stage1_dagger.py" --round 2 --refit-if-admitted
"$PY" "$SLICE/stage1_mechanism.py" --pairs 12
```

The mechanism command deliberately evaluates the initial BC stage1 exports, as requested, even if DAgger refits subsequently exist. Each DAgger refit has its own <=20-step resource sample and separate one-hour gate. Never bypass an unavailable process gate or fabricate a training projection.

## Current correction: collection v2 and admission attempt 02

The preceding instructions and numbers describe the historical deterministic collection and superseded full-prefix implementation. Use this section for the current host handoff. Read CONTRACT_AMENDMENT_STAGE1_V2.md first. Old held-out numbers are duplicate-trajectory in-distribution replay diagnostics; they do not demonstrate held-out generalization. D1 sparse teacher completion failed the old ES eligibility requirement.

Method: **R2D2 stored recurrent state + burn-in** (Kapturowski, Ostrovski, Quan, Munos, Dabney, *Recurrent Experience Replay in Distributed Reinforcement Learning*, ICLR 2019; [paper](https://openreview.net/pdf/387fb2fcee8f74c53cf707a9856f40c458f33933.pdf)), with **truncated backpropagation through time**. This offline adaptation refreshes state under current weights once per epoch, snapshots the entire state, and uses 30-tick no-grad burn-in followed by the unchanged 90-tick gradient window. The paper discusses stored-state staleness/representational drift and combining stored states with burn-in. Our epoch refresh is a declared implementation choice; it is exact only at unchanged weights, and the fixture proves that case. Both N1r and N2 follow the same procedure. Float64 remains throughout; threads 2, no parallel fits. Five fits include the three predefined N1 seeds. The new projection measures and charges refresh, diagnostics, all seeds and full export parity, with the same 60-minute gate. The host has not yet measured attempt 02.

Collection sample typically took minutes in v1, but v2 timing is unknown. Projection will measure it before allowing full collection. Training may consume up to one hour **after** admission; the offline admission sample has its own one-hour hard stop. Tell the owner the measured projection before proceeding if it refuses. Never use old collection or converted indexes with the corrected trainer.

Run from repository root, in this order. These are commands for Claude on the host, not runs performed in this sandbox:

```sh
cd /Users/new/RiderProjects/ai_RPG_test
SLICE=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1
PY="$SLICE/_local/mlenv/bin/python"
"$PY" "$SLICE/collection_v2.py" sample --fights 20
"$PY" "$SLICE/collection_v2.py" project
"$PY" "$SLICE/collection_v2.py" collect --fights 200
"$PY" "$SLICE/stage1_data_v2.py" receipt
"$PY" "$SLICE/stage1_data_v2.py" convert
"$PY" "$SLICE/stage1_native_v2.py" admit
"$PY" "$SLICE/stage1_train.py" --run-if-admitted
```

The training command creates TRAINING_PROJECTION_02.json and STAGE1_BUDGET_02.json, preserving attempt 01. It proceeds only on admission. An existing attempt-02 budget/projection refuses repeated sampling; do not delete it. If projection is over an hour, report per-arm wall costs (N1 also has three seeds) and the smallest common epoch reduction in the receipt to the owner; do not apply it yourself.

Only after STAGE1_V2_RESULTS.json is TRAINED_BC and its export parity is PASS:

```sh
"$PY" "$SLICE/stage1_dagger.py" --round 1 --refit-if-admitted
"$PY" "$SLICE/stage1_dagger.py" --round 2 --refit-if-admitted
"$PY" "$SLICE/stage1_mechanism.py" --pairs 12
```

Jobs write into `_local/stage1_v2/jobs`, and refits into `_local/stage1_v2/dagger_rN`; old jobs stay untouched. Each completed student log receives an offline own-Host-path parity receipt before refit/report use. Mechanism still uses initial BC primary-seed exports. Reading: imitation and descriptive arm differences, with minority-class diagnostics, N1 seed noise, N2 learned-law statistics and the fixed J motion prior explicit. This is not scientific acceptance or a complete H-M claim.

The separate v2 driver was built here without fights; `admit` verifies its new STAGE1_NATIVE_BUILD_V2.json and binary. For a fresh checkout where local v2 native objects/binary are absent, run `"$PY" "$SLICE/stage1_native_v2.py" build` once before `admit`. Preserve any existing build receipt; inspect drift before rebuilding.

Full-sequence parity streams 12-tick chunks, sending the shared joint snapshot once per tick. A persistent native Host and Python Replay carry phases, memory, six-tick features/forcing, assignments, graph IDs and cached intents across every chunk; a chunk boundary never resets state. Native JS arena GC runs after each response with no retained JS snapshot roots, while numeric Host state remains. Exact native child CPU and peak RSS come from wait4 and enforce the 512 MiB child cap; Python RSS is checked too. PreparedFight leaves features mmap-backed and converts only joint decision rows to float64. Stored held-feature snapshots use the original float32 feature representation losslessly, then restore float64; phases, memory, forcing and all computation remain float64. This does not quantize weights or recurrent state.
