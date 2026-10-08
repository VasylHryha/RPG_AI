# Stage A FIX3: physical clock and sandbox fixture execution

Decision 0036 quick correction from eee589e. The failed recordings had complete physical-tick sequences, rather than a five-Hz decision sequence. Native coreStep advances the clock before controller preparation; the first policy snapshot is therefore at dt and the last shares terminal time. Validation incorrectly required a first snapshot at zero and a terminal time one dt beyond the final snapshot.

The native snapshot now declares physical_tick_after_clock_advance. Full JSON and compact STAGEASLIM1 recordings retain every physical input/history row. Validation checks finite dt/time, contiguous ticks from dt, terminal agreement, and observer step coverage. Parity inputs use that same clock and must exactly match their corresponding collected public snapshot, with complete one-to-one coverage. The five-Hz encoder refresh and per-tick recurrent/phase update behavior remain as implemented. Legacy recordings lacking the new cadence field retain their documented physical-tick interpretation; recorded times are not rewritten.

Fixture execution requires STAGEA_HOST_TEST=1, a fixture split and tag, matching request hash, and a duration envelope of three seconds (150 only for the memory fixture). Both repository locks, live available-RAM admission, wall/stdout/row bounds, and native RSS profiling remain enforced. The native child's getrusage reports replace ps for fixture RSS measurement, with a 512 MiB bound. The sandbox fixture launches the binary directly because nice emits a sandbox permission warning. Production collection, diagnostics, audit, training, readout and parity still use the process-ownership gate and normal RSS monitoring. Setting the fixture environment flag does not alter production admission.

Final focused run: STAGEA_HOST_TEST=1, all five Stage A test files, 31 passed in 40.32 seconds (40.92 seconds measured wall). Both requested host files passed here, with no skips. All five network arms passed real-binary wiring and Python/native sequence parity. Two fresh, opposite-orientation O fixtures passed recording, raw validation, compact decoding, all-arm packing/label conversion, and Python float64/native replay of their complete physical prefixes. Each produced 91 frames and 4,550 converted unit rows per arm.

| Fixture | Peak native RSS, bytes | Compressed bytes/fight | Physical ticks |
|---|---:|---:|---:|
| 150-second memory, all 100 units alive | 7,471,104 | 9,308,752 | 4,501 |
| Three-second teacher, orientation 0 | 7,127,040 | 291,384 | 91 |
| Three-second teacher, orientation 1 | 6,619,136 | 295,660 | 91 |
| Three-second N1 | 8,765,440 | 1,215,631 | 91 |
| Three-second N1h | 9,666,560 | 2,564,209 | 91 |
| Three-second N1r | 8,306,688 | 1,183,382 | 91 |
| Three-second N2 | 8,994,816 | 2,786,794 | 91 |
| Three-second N2J0 | 8,388,608 | 2,756,873 | 91 |

The memory fight used 402,080,697 uncompressed bytes and took 21.26 seconds through recording and validation. Its full compact projection is 1.676 decimal GB for 180 fights. The larger of the two short teacher measurements projects conservatively to 14,623,798.46 bytes/full fight and 2.632 decimal GB for 180 fights. These are development fixtures; the real twenty-fight timing sample must still pass production disk/time admission.

Attempt 001 is preserved: 20 tests passed before the new NaN-clock regression failed because feature packing rejected nonfinite input before the expected clock validator. The correction moved clock validation ahead of conversion and added a corrupt parity-input rejection. The separate reviewer rechecked that correction before attempt 002. Both build/test attempts and their logs remain, including the harmless build-time nice warnings. The first FIX3 build manifest and the original binary/manifest are copied locally; no previous receipt was replaced. No routine successful test or fight was repeated after attempt 002.

The prospective fix3 recovery is registered locally and passes current binary/source admission. All 180 sealed requests and all 195 baseline artifacts were hash-verified unchanged; 18 prior failed artifacts are bound into the new recovery record. Earlier ledger/recovery records remain unchanged. Zero sealed collection jobs were retried. New fixture attempts use fresh tags and entropy, separate from the training index. The existing failed collection invocation that was untracked on arrival remains unchanged.

The separate Codex recheck contains the owner's request verbatim and reports no blocking findings. Its disposition is recorded with this correction, as instructed; docs/PLAN_CURRENT.md and sealed evidence are untouched. No living Markdown files are source-pinned. The changed-path list is only in UNCOMMITTED_STAGEA_FIX3.txt. The implementation remains uncommitted.

Production continuation uses the existing owner caps. Initial planning estimates: twenty-fight sample 4–10 minutes; remaining collection 25–75 minutes; audit 15–60 minutes; training measurement 5–20 minutes. Fit/parity/outcome projections are computed by their own admission paths. A refusal stops the chain; preserve it and resume only that failed command after resolving its cause. Do not rebuild or rerun passed tests for unchanged sources. The 20-pair outcome is mechanism-only; later looks retain the existing harm and completeness gates.

The exact host test command that passed was:

```sh
STAGEA_HOST_TEST=1 "$STAGEA_PYTHON" -m pytest -q -x -s \
  "$STAGEA/test_stagea.py" "$STAGEA/test_stagea_mem.py" \
  "$STAGEA/test_stagea_slim.py" "$STAGEA/test_stagea_host.py" \
  "$STAGEA/test_stagea_memory_host.py"
```

The standalone two-fight equivalent is `STAGEA_HOST_TEST=1 "$STAGEA_PYTHON" "$STAGEA/collect.py" fixture-sample`; it was already exercised through the host test. Production continuation (fixture mode unset):

```sh
cd /Users/new/RiderProjects/ai_RPG_test
set -e
export STAGEA=evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stagea
export STAGEA_PYTHON=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/_local/mlenv/bin/python
export PYTHONPYCACHEPREFIX="$STAGEA/_local/pycache"
unset STAGEA_HOST_TEST
"$STAGEA_PYTHON" -c 'import sys; from pathlib import Path; sys.path.insert(0, str(Path(sys.argv[1]).resolve())); from collect import identity; print(identity()["binary_sha256"])' "$STAGEA"
"$STAGEA_PYTHON" "$STAGEA/collect.py" recover-fix3
"$STAGEA_PYTHON" "$STAGEA/collect.py" sample
"$STAGEA_PYTHON" "$STAGEA/collect.py" run
"$STAGEA_PYTHON" "$STAGEA/collect.py" audit
"$STAGEA_PYTHON" "$STAGEA/train.py" measure --epochs 2 --windows 4
"$STAGEA_PYTHON" "$STAGEA/train.py" run
"$STAGEA_PYTHON" "$STAGEA/parity.py"
"$STAGEA_PYTHON" "$STAGEA/readout.py" prepare
"$STAGEA_PYTHON" "$STAGEA/readout.py" run --look 20
"$STAGEA_PYTHON" "$STAGEA/readout.py" run --look 50
"$STAGEA_PYTHON" "$STAGEA/readout.py" run --look 100
```
