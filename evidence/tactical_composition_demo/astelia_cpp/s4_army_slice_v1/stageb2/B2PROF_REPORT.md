# B2 real-window profiling and cache optimization

TEST_ONLY sample meets the requested step target. No full training ran. Production admission, full-cache size, and held-out native replay remain host gates.

| Arm | Before, seconds | Final cold maximum, seconds | Speedup |
|---|---:|---:|---:|
| N1 | 7.553 | 1.068 | 7.07x |
| N1b | 7.649 | 0.995 | 7.68x |
| N1r | 7.546 | 0.966 | 7.81x |
| N1rb | 7.703 | 1.082 | 7.12x |
| N2 | 8.282 | 1.269 | 6.53x |

The final sample contains20 optimizer steps: first and last declared windows of the largest-frame training fight in each panel, all five arms. Every first window is90 physical ticks and4500 own-unit decision rows; late windows retain their actual physical lengths and population. Before profiles use the same first C3 fight/window and initial models. Largest validation fights supply prefix/diagnostic costs. These are real recorded rows, not synthetic timing fixtures. Both samples use unity pointer weights for a controlled comparison; focused parity tests additionally use nonuniform weights. Final first-C3 losses match all five baseline losses exactly.

All runs pin PyTorch intra/inter-op and OMP/MKL/OpenBLAS to one thread. The shell requested nice15 and the sandbox printed setpriority denied; the Python processes actually ran at nice10, as recorded in both receipts. The existing job was left running. The final cache/timing sample took116.82s. Sampled peak process high-water RSS was1.147GB (1.069GiB), below the inherited exclusive1.5GiB bound.

## Measured hotspots

Seconds are cProfile cumulative wall time per first-C3 optimizer step. Rows include nested calls; do not add their columns. In BEFORE, public packing consumed6.61–6.67s and contains the native generation and hierarchy costs shown below. The dominant cost was rebuilding and partitioning banks, rather than the hierarchical scoring architecture.

| Arm | Before native generation | Before hierarchy partition | Final cache load | Final lossless bank decode | Final batched tensors | Final model tick |
|---|---:|---:|---:|---:|---:|---:|
| N1 | 2.809 | 3.438 | 0.437 | 0.175 | 0.146 | 0.332 |
| N1b | 2.796 | 3.438 | 0.423 | 0.172 | 0.141 | 0.318 |
| N1r | 2.804 | 3.429 | 0.416 | 0.169 | 0.137 | 0.305 |
| N1rb | 2.796 | 3.457 | 0.447 | 0.179 | 0.154 | 0.358 |
| N2 | 2.822 | 3.464 | 0.456 | 0.181 | 0.153 | 0.487 |

Final profiles contain zero native candidate-generation or hierarchy-partition calls. Cold loading includes compressed shard reads, bit-plane decoding, geometry/field correction decoding and reverse-index decoding. Candidate scoring and backward remain weight-dependent. Full pstats and35-entry hotspot lists are retained in the before/after receipts and local profiling artifacts.

## Final behavior and exactness

The versioned compact cache stores public inputs for every physical tick and materialized native banks only for the four declared head windows. Candidate validity/type/source arrays, family/member tables, static nearest labels, mapped labels and neighbor edges are prepared once under source/raw identity hashes. A completed cache is reused. Optimizer steps never enumerate/prune candidates, sort families, or remap static teacher targets again; N2 movement nearest remains weight-dependent and is recomputed. Validation retains the existing per-role diagnostic loop over compact labels.

Float64 geometry is encoded with reversible unsigned64 corrections; model points cross the original float64-to-float32 boundary. Numeric features use reversible unsigned32 corrections. Geometry and rational-field predictors are compression operations: their approximations cannot change recovered inputs because all bit corrections are stored. Native decoding batches candidates; typed temporal differences and byte planes reduce disk storage. Reverse family/member indices decode from the stored table in one native batch. Type onehots and peer readouts use batch scatter/broadcast operations.

N2 movement-nearest labels remain dynamic because they depend on learned drift; they are explicitly excluded from static reuse. Inference and recurrent prefixes never consume teacher inputs. Raw float64 and native parity always read the original complete public rows. Compact selected-window metadata retains calibration safety fields. Memoryless arms retain only selected rows. Recurrent arms stream every physical prefix tick once and retain the identical detached snapshots; autograd inputs/labels own small storage rather than retaining entire cache shards.

The final focused batch passed41 tests in7.81s. It checks exact float32 outputs/losses, gradient closeness, original loop versus batch peer readout, label isolation, N2 dynamic nearest behavior, tie/boundary family partitioning, arbitrary32/64-bit transport, geometry/image clipping, sparse prefix snapshots, metadata corruption, buffer ownership, calibration safety, raw native replay routing and reverse-index bounds. No full suite or full training was run. Earlier changed-code test batches and failed cache/timing designs remain recorded; successful tests were repeated only after the relevant implementation changed.

## Bounds and remaining host checks

Four complete fight caches cover6744 physical ticks and1254 head ticks, taking109.52MB including row metadata and cache descriptors. Panel-specific extrapolation across the180-fight round0 corpus gives4.805GB for the active cache identity. Preserved older identities are outside this estimate. With an additional disk-only20% sensitivity margin it would be5.765GB; this is not a verified whole-corpus disk bound. The storage estimate has limited headroom. Production cache construction enforces the5,000,000,000-byte projection and free-space reserve and must finish before claiming actual whole-corpus size.

Using the repository lane projection for five arms,10 epochs, four windows/fight and four CPU lanes gives11576.41s (3.216h), already multiplied by1.2. The cap is16200s (4.5h). Measured prefix refresh, raw/compact row reload, validation and tail estimates are included. Production source/raw admission hashing, train-only class-weight setup and actual concurrent-lane scaling are not measured here. The current TEST_ONLY receipt cannot authorize training. Fresh production measurement must return ADMITTED, and the existing process/memory/coverage gates remain in force. Earlier contended schema10 N2 wall1.954s versus CPU1.470s remains preserved; CPU time was never substituted for wall admission.

The separate owner recheck found and resolved cache identity/manifest routing, metadata authentication, tensor-storage retention, deferred head expansion, calibration safety inputs, and raw replay routing issues. Final source and receipt checks are recorded separately. This is development timing/exactness evidence, not held-out native parity acceptance or scientific source qualification. Tracked edits and retained task artifacts are confined to stageb2; existing dirty work and protected stages were preserved. The requested path inventory is only in UNCOMMITTED_B2PROF.txt.

Host commands are in HOST_COMMANDS_B2PROF.md. Run them after the existing Stage B job finishes, and stop at any failed gate.
