# Stage A parity memory recovery (decision 0036)

The failed parity invocation remains immutable. The failure was native RSS above 2 GiB, after collection, audit, measured 2-epoch/4-window budgeting and all five training arms completed. No fitting, re-exporting, data recollection or recorded outcome run is part of this repair.

Replay already used one frame per RPC. Its input parser still populated the global appendShape cache, copying and retaining every dynamic-key insertion prefix. JSON arena collection between requests did not release those cached layouts. The rebuilt host parses incoming request objects into flat, request-owned layouts, roots requests throughout combat/batches, and releases layouts only after the response and JSON sweep, including exceptions. It preserves duplicate-key last-wins behavior and the host's scalar/string parser. Replay accepts exactly one frame per RPC; its numeric state, encoder-refresh schedule, phase law, identity pruning and exported weights are unchanged. Native getrusage reports the actual high-water RSS after request GC and at EOF.

Parity decodes the compact shard afresh for each inference pass and writes one-row RPCs to a disk stream. It retains output arrays for comparison, not the full JSON sequence. Failed request/output/stderr streams remain available for diagnosis; successful streams are removed after their final RSS/completeness report is verified.

The inference-only recovery records both identities and hashes the old failure, original ledger, audit, index, sealed budget and all fixed training files. It checks every sealed request and all unchanged source/build pins. The original ledger, budget, audit, checkpoints, exports and outcome files are not rewritten. Parity/readout use the explicit recovery; training and collection retain their original source gates. Production process discovery, locks, live RAM reserve, live RSS and owner caps remain active. Only explicitly opted-in fixtures use the existing fixture monitor, which skips ownership discovery and consumes child-native RSS reports.

The 150-second regression uses fresh validation-fixture entropy, the trained N2 export and a real recorded 100-unit sequence. Both armies are separated so every physical tick retains the maximum entity bank. Its strict native RSS bound is 512 MiB. None of the actual sealed held-out fights lasts 150 seconds; a second regression replays the longest actual validation fight. Both compare every tick against float64 Python inference. A separate native parser contract changes 2,500 dynamic keys on each of 4,501 requests, verifies zero permanent layout growth, checks rooted GC lifetimes, duplicate/Unicode semantics and malformed-input cleanup. Existing real-host fixtures cover all five arms, compact conversion, ordinary combat and recorder RSS.

## Training measurements and future projection

These are checkpoint wall differences, not total fit time divided by two. Epoch wall includes the full stored-state refresh, optimizer windows, reload/checks and validation. No training was run to produce this report.

| Arm | Epoch 1 wall (s) | Epoch 2 wall (s) |
|---|---:|---:|
| N1 | 374.54 | 385.75 |
| N1h | 458.49 | 470.89 |
| N1r | 412.34 | 423.44 |
| N2 | 828.16 | 821.57 |
| N2J0 | 828.11 | 821.17 |

Four two-thread lanes, assigning arms longest-first, with a 20% margin:

| Future budget | Projected fit wall | With margin | Fits 3 h |
|---|---:|---:|---|
| 10 epochs, 4 windows/fight | 2 h 22 m | 2 h 50 m | yes |
| 10 epochs, 8 windows/fight | 3 h 34 m | 4 h 17 m | no |
| 10 epochs, 16 windows/fight | 5 h 57 m | 7 h 09 m | no |

Projection uses the slower measured epoch per arm. Full refresh and residual overhead stay fixed; optimizer, whole validation and final export/test overhead scale by windows/4. This conservatively scales the fixed refresh component inside validation too. Window saturation, extra saved-state I/O and changed contention are unmeasured. Measurement and separate full-sequence parity are outside the fit projection. The machine-readable projection preserves the source receipts and exact arithmetic.

**Separate future step, not executed:** prepare a fresh isolated training revision with its own source-qualified data/audit identity, output directory and newly measured budget. Preserve the current run in full. The existing additional one-hour-per-arm admission rule must be explicitly revised for that future revision; it refuses these ten-epoch budgets even when the concurrent 10x4 projection fits three hours. A current sealed budget cannot be replaced, and `run` takes its budget from that receipt rather than CLI flags.

After that preparation, the exact longer-fit commands (four windows, the option projected inside three hours) are:

```sh
"$STAGEA_PYTHON" "$FUTURE_STAGEA/train.py" measure --epochs 10 --windows 4
"$STAGEA_PYTHON" "$FUTURE_STAGEA/train.py" run
```

Eight windows would use `measure --epochs 10 --windows 8`, but the conservative projection exceeds the current three-hour cap. A new measurement must admit the future fit before `run`; these commands are not instructions to alter today's sealed budget or artifacts.

## Validation and handoff

Build completed in 24.754 seconds. The focused test batch ran once after all code/recheck changes: **53 passed**, no skips, in 133.95 seconds pytest / 134.6175 seconds measured wall. The N2 150.033-second fixture replayed all 4,501 physical ticks (225,050 unit rows), peaking at **7,618,560 bytes (7.27 MiB)** against the strict **512 MiB** bound. It had zero categorical mismatches and maximum absolute numeric error 1.67e-13. The longest actual held-out fight replayed 1,811 ticks (53,804 unit rows), peaking at **9,764,864 bytes (9.31 MiB)**, with zero categorical mismatches and error 1.47e-13. The native reports end with an empty JSON arena and constant replay shape count. The existing recorder regression also passed all 4,501 ticks at 7,471,104 bytes. Recovery was registered and checked idempotently, with all **431** baseline artifact hashes unchanged. Full all-arm/all-validation parity and outcome looks remain the host handoff below. The separate quick owner recheck uses the verbatim request; its findings and dispositions are recorded locally in this Stage A delivery. The current plan and living-document identities are untouched. Changed paths are listed only in the requested task manifest.

The recovery registration is idempotent and performs no replay. It is applied before the following host sequence. Do not retrain or rebuild unchanged sources. `set -e` stops the chain at a refusal, and the existing look gates remain authoritative.

```sh
cd /Users/new/RiderProjects/ai_RPG_test
set -e
export STAGEA=evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stagea
export STAGEA_PYTHON=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/_local/mlenv/bin/python
export PYTHONPYCACHEPREFIX="$STAGEA/_local/pycache"
"$STAGEA_PYTHON" "$STAGEA/parity.py"
"$STAGEA_PYTHON" "$STAGEA/readout.py" prepare
"$STAGEA_PYTHON" "$STAGEA/readout.py" run --look 20
"$STAGEA_PYTHON" "$STAGEA/readout.py" run --look 50
"$STAGEA_PYTHON" "$STAGEA/readout.py" run --look 100
```
