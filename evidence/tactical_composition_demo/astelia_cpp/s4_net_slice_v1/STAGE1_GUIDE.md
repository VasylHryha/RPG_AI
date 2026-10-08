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
