READY_FOR_DEVELOPMENT

Reviewer family: Claude
Implementer family: Codex
Reviewed commit: `7ac1e3347cb8e82bdd0cd51759d02e89790d3548` (HEAD, `main`)
Scope: a narrow, read-only engineering recheck of the C6 performance repair. I ran no code. I did not recompute hashes, tests, mutants or the large JSON arrays.

**What this verdict covers.** It covers only the engineering of the performance repair. I compared `native/c6_r4/field.cpp`, `geomind/c6_r4_field.py` and `geomind/c6_r4_field_assay.py` with the preserved baselines in `evidence/c6_r006_performance_checks/baseline/`. I also read the three new contracts, the three new cache mutants, `tools/c6_r4_performance_check.py`, `CHECKS.json`, `COMPARISON.json`, `README.md`, decision 0023 and `INTERRUPTED.json`. It does not cover whole-world runtime readiness, any scientific claim, the R006 registration or final panel approval. I did not reopen the nine previous findings or B1; I found no regression evidence against them.

## Findings

No blockers.

**Native kernel (`native/c6_r4/field.cpp`)**
- **Arithmetic:** The equation arithmetic is unchanged from `baseline/field.cpp`. This covers the medium terms, pair forces, coupling, readout, emission masking and normalization.
- **Neighbor order:** `Workspace.neighbors` (line 17) builds the neighbor lists in ascending `b` with the same `adj[a*ns+b]` test. Summation order therefore matches the old inner loop.
- **Stage times:** These are unchanged. `drive_path` (lines 40–45) uses `t=start+step*dt`, `t+.5*dt` and `t+dt`, the same expressions as the baseline `field_run` (lines 75–81). Stages b and c both read slot `3*step+1`, which is correct because both are at t+½dt.
- **Fallback path:** When the cache declines (line 124), forcing is computed at the same `t`.
- **Drive arithmetic:** `amplitude/8.*polar(...)` with zero initialization is identical to the old `p[2]/8.*…`.
- **Cache identity:** The cache key (lines 35–36) is `ns`, `steps`, `start`, `dt`, `amplitude` and all `ns*8` phases, compared exactly. The drive depends only on these and the static `nu`. The three mutants (`tools/c6_r4_mutants.py:3-5`) each drop one key term. `test_cached_drive_tracks_absolute_time_phases_and_amplitude` (`tests/test_c6_r4_field.py:560`) checks reuse and invalidation for each term against the independent reference `R`, at a nonzero clock and with a return to an older key.
- **Cache bound:** A single path larger than 32 MiB returns `nullptr`, which falls back to computing forcing per stage. Eviction pops only from the back and stops at size 1, so the entry just pushed (front) cannot be evicted. Total bytes therefore stay at or below 32 MiB with at most 4 entries.
- **Lifetimes and threads:** `std::list::splice` does not invalidate element storage. `drive_path` is called once per `field_run`, so the returned pointer stays valid for the whole integration. The cache is `thread_local`, so concurrent ctypes calls cannot share it.
- **Workspace reuse:** For each cohort, `vx/vy/vt` are zero-filled again, and `phasors` and `saturated` are fully overwritten before they are read. Early `return 2` leaks nothing, because the workspace is RAII.

**Passive source cache (`geomind/c6_r4_field.py:186-198`)**
- The only change is that the bound is now in bytes instead of 1024 keys. The key is unchanged: full passive `identity()` (includes clock, carrier and zeroed actual field) plus duration, `dt` and `sample_dt`.
- A path larger than the bound is used without being cached.
- The newest key cannot be evicted (the `len>1` guard), so `move_to_end(key)` always finds it.

**Blocked assay (`geomind/c6_r4_field_assay.py:31-48`)**
- **Requested samples:** Integration now runs in blocks of up to `int(10/sample_dt)` sample intervals. `block_duration` is an exact multiple of `sample_dt`, so `flow[S::S]` gives exactly the sample-time rows, ending at the block end. That is equivalent to the old `flow[-1]` per interval.
- **Every production step is still compared:** `advance(..., dt/2**k, dt)` still returns every production-grid row, and `state_errors` sees all of them for all three grids. Per-block `flow[1:]` concatenates to the same row sequence as per-interval `flow[1:]`. Trace-hash coverage, `output_power` (excludes each block's initial row, which is the previous block's final row) and `out_max` therefore cover the same steps.
- **First output time:** `first_output_time` subtracts `block_duration`, and the row index is in production `dt`. Correct.
- `test_blocked_assay_retains_every_sample_and_independent_full_scope` checks samples, trace hash, power and `max_errors` against the independent reference.

**Sham preserved-source hashes** (`c6_r4_field_protocol.py:93`, `c6_r4_field_analysis.py:98`)
- Intact and `no_backreaction` start from the same grid and duration, so their block partitions match.
- The cohort equations read only the cohort's own carrier and never the actual field. Cached and computed drive values come from the same `drive()` call with the same `t` expression, so they are bitwise equal.
- Bitwise equality of the source trace between the active and the passive integration is therefore preserved.

**Clocks, descriptor, formation, recovery, causality, persistence and continued owners**
- All three grids advance by the same `block_duration`, so their clocks stay equal across grids.
- Clock values now differ from the old per-interval accumulation only by roundoff. This is the source of the ≤6.9e-14 difference.
- These downstream paths consume `GridSet.run` outputs, whose content is unchanged, and their code is unchanged.
- `test_descriptor_shares_full_exact_source_paths_and_keeps_all_probes` checks:
  - one source integration per grid;
  - 51 check receipts;
  - 50 raw responses of shape (3,25,2);
  - equal trace hashes across probes;
  - the cache byte bound.

**Receipts**
- `COMPARISON.json` and `CHECKS.json` agree with each other:
  - speed: 17.18×;
  - maximum raw-response error: 6.88e-14;
  - maximum full-state check difference: 5.7e-15;
  - tolerance: 1e-10;
  - calls: 31200→312 advances and 600→6 source integrations.
- The `tests` section reports 62 passed; the 49 registered mutants were not run; there is no panel and no final entropy.
- `INTERRUPTED.json` records the withdrawal separately and references the original receipt by SHA. I did not recompute that SHA.
- The modified files are all C6 R4 files. None are in the accepted/frozen or R3-bound lists in AGENTS.md. I did not compute hashes to confirm this.

## Optional follow-up notes (not blocking)

1. **The reducer script is not committed.** No committed script produces `COMPARISON.json`: no `.py` file contains `maximum_raw_response_error`. The raw `baseline.json` and `optimized.json` are committed, so the comparison can be recomputed, but committing the reducer would make it reproducible in one step.
2. **The comparison fixture covers only one path.** It runs the descriptor with every cohort turned off (`c6_r4_performance_check.py:48,52`), so it does not exercise the batched path for an emitting active cohort (operation `intact`). That path is covered only by the small-scale contracts at lines 560 and 573. This is acceptable, because the native arithmetic is the same.
3. **Commit offset.** `CHECKS.json` records `source_commit` 5ec9ccc, while HEAD is 7ac1e33. From its title, 7ac1e33 only adds evidence. I did not independently confirm that the code fingerprint matches HEAD.
4. **Old and new trace hashes are not comparable.** Block-wise clock accumulation changes the last bits of absolute stage times compared with R005-era code. R006 source-trace hashes must not be compared bitwise with hashes from before the optimization. Within R006 the comparisons stay consistent. No R005 world completed, so nothing depends on this today.
