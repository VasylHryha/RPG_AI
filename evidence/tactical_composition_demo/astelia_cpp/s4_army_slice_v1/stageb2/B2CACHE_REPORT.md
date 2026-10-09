# B2 cache correction

The cache now stores lossless float64 native-input packets, rather than materialized candidate banks. Each lazy head read regenerates every unit's exact bank in one native batch using the same candidates.h implementation as native inference. Candidate order, points, all scorer features, type and source are retained without float32 rounding. No native inference code, loss, optimizer, labels, window selection or threshold was changed. Owner settings remain in the unchanged OWNER_APPROVALS.json.

The cache retains only the union of four declared 90-tick head windows: 56,556 rows in the current round-0 index. Full physical rows still feed public velocity reconstruction and recurrent state replay. Policy.tick updates state before its state_only return; candidate heads cannot affect that state. Training.step, evaluation and calibration all score the same rows as before. In particular, evaluation/calibration really use every window tick, so caching only sparse optimizer loss rows would be incorrect. Prefix rows hold no candidate arrays. One loaded input chunk and one regenerated frame bank are shared per worker; lazy row handles retain neither arrays nor full source rows.

Schema 3 participates in content identity, which also binds raw hashes, native code and public reconstruction code. Lossless XOR compression retains the existing chunk hash/schema/offset and coverage checks. Old partial schema-2 files are preserved and cannot be reused as schema 3. The receipt reports active cache bytes separately from directory bytes and old/orphan files. The active compressed cache is projected against a 5,000,000,000-byte engineering storage target and actual free space, retaining the existing 2 GiB reserve. This target does not change any owner timing/parity/coverage threshold.

The measurement includes native regeneration in actual optimizer/evaluation window costs, with the existing 20-step sample, lane scheduling and 1.2 margin. Storage projects by selected window rows, avoiding distortion from different physical fight lengths. Build-time projection retains per-fight original construction seconds when reusing already-built packets; a resumed build cannot make its prospective construction estimate vanish.

## Measured size and verification

All 23 focused checks passed. Reported pytest time was 8.22 seconds total: seven passed before a missing scratch-parent setup error, then the remaining 16 passed without repeating those seven. Checks cover native/Python banks, all five arms' exact cached float32 outputs/state and label mapping, full-prefix state equivalence, window isolation/lazy loading, reuse/corruption, multiple chunks with packet-length changes, invalid packets and recorded rows.

The small recorded-data check read the four largest train/validation timing fights (C3 and regular), then compared every candidate field at the first/last declared window rows, bitwise float64. Its eight-row sample occupied **16,499 bytes compressed** and **116,328 bytes uncompressed native inputs**, replacing **14,616,896 bytes** of materialized float64 candidate arrays. Sample packet construction/compression took **0.01766 seconds**; the entire check, including full raw replay and parity regeneration, took **5.027 seconds**. These are sample measurements, not full-cache build timing.

That compressed sample projects to **116,639,681 bytes (about 117 MB)** for all 56,556 selected rows. Endpoint sampling is not a guarantee of interior compression. Independently, the valid public envelope gives an uncompressed input bound of **2,436,432,480 bytes (2.44 GB)** before small ZIP/offset/metadata overhead: 128 actors, 64 own rows, the existing threat caps and one public velocity row per actor. This leaves substantial margin below the 5 GB target even with incompressible inputs. Full active-cache bytes/build seconds will be reported by the host measurement; the prior partial bank directory was about 262 MiB when inspected and is retained separately.

The separate reviewer found no blocking defect; its two reporting/real-data notes were resolved. This was a same-family review, not cross-family acceptance. No numeric quality score is assigned.

The requested real-host `train.py measure --round 0 --test-mode` was attempted and refused before caching: pgrep returncode 3, `sysmon request failed with error: sysmond service not found`, `pgrep: Cannot get process list`. No process or admission gate was bypassed. The log is retained in this delivery's local scratch area. Full-cache construction time and regeneration-inclusive training admission remain unmeasured here.

## Host continuation

The current gates bind every Python source, including the cache wrapper and new focused checks. **Coverage must rerun** with the existing --preserve-stale mechanism; the successful old receipt is archived, not overwritten. The existing binary's broad source manifest also requires the ordinary B2 rebuild even though C++ is unchanged. No baseline or train prepare rerun is required; their existing checks reuse the baseline and round-0 index. Do not remove old candidate files or edit receipts. The new identity naturally creates a separate cache.

In the normal host terminal:

```sh
cd /Users/new/RiderProjects/ai_RPG_test
B2=evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stageb2
ML=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/_local/mlenv/bin/python
export B2_VARIANT=react_on PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
nice -n 15 "$ML" "$B2/build.py"
nice -n 15 "$ML" "$B2/coverage.py" --round 0 --preserve-stale
```

Build previously took roughly 30–90 seconds; coverage is bounded by the live owner configuration (currently 1,800 seconds). The test-mode and full measurement durations remain unmeasured; both use the unchanged live training cap (currently 16,200 seconds). Native regeneration may change fit cost, so proceed only on an ADMITTED production budget. The fit duration is its measured projected_seconds, with the existing cap and margin. Parity remains mandatory before DAgger collection. The protocol requires a full-fight DAgger refit before paired looks; round-0 readout is not available.

Commands from measurement onward (the test-mode command completes the sandbox-blocked small host check; it seals no production budget):

```sh
nice -n 15 "$ML" "$B2/train.py" measure --round 0 --test-mode
nice -n 15 "$ML" "$B2/train.py" measure --round 0
nice -n 15 "$ML" "$B2/train.py" run --round 0
nice -n 15 "$ML" "$B2/parity_run.py" --round 0
nice -n 15 "$ML" "$B2/baseline_parity.py" --round 0
```
