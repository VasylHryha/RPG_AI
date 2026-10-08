# Stage A recorder memory recovery

Decision 0036 quick fix against baseline 78d138633067defc15752af25a531c7c975b7814. No collection or combat ran in the sandbox. Current rebuilt host identity: `774525be1ea36006a12dafa4b802fd8750618c00a331e1224f35a4b3dcb41263`.

The original failed attempt remains unchanged. Its stdout SHA256 is `920f8384906175b45e375ec2881cbed0a00eea41b474d8da8342b1b20a11afd4`. It contains 63,905,792 bytes: 821 training snapshots, 821 observer snapshots and a 6,244-byte truncated final row. Those 1,642 complete JSON rows represent 821 physical ticks. Training snapshots average 61,573 bytes; the combined average per complete row is approximately 39 KB.

Two allocation mechanisms were reproduced without combat, using the unchanged JSON value implementation and copied allocation instrumentation:

1. Objects enter the global JSON arena, which the original host swept only after a complete fight. Reparse/serialize of the first real training snapshot 128 times retained 90,883 objects and peaked at 30,064,640 bytes. Tick collection left three live roots, peaking at 4,210,688 bytes.
2. Dynamic `history` and especially `pairModes` objects used `appendShape`, caching every insertion prefix and copying all existing keys and indices each time. The failed trace has up to 1,800 pair keys and 58 distinct layouts. Replaying these actual key sequences with GC still crossed the probe's 256 MiB stop after 378 ticks: 297,975,808 bytes, 3,493 permanent cached shapes, only three live JSON objects. Flat layouts completed all 821 key sequences at 3,719,168 bytes with one cached shape. This isolates shape-cache retention independently of arena retention. These are allocation probes, not whole-host RSS measurements.

The copied Stage A host now sweeps at the end of every serialized tick. It roots the entire incoming request/batch, previous completed batch results, optional trace history and pending shape/shot/battery telemetry. Consumed Stage A input is released; its flat dynamic layouts are freed only after the JSON sweep. Flat layouts are restricted to consumed snapshots and may not escape into roots surviving that release. Controller copies share layout ownership. Inactive branch-pool controllers are replaced before reuse. Existing oracle histories already prune dead identities; learned state already rebuilds its map from living identities each inference tick. Their scientific contents and update rules were not changed.

Frames still stream to stdout. The Python collector now drains a bounded 64 KiB pipe buffer directly into gzip level 1, retaining a compressed partial file on failure and recording raw/compressed bytes and fresh attempt IDs. No fields are dropped. This preserves oracle input/label history and observer telemetry. A one-fight compressed observer/terminal-only validation file remains transient; successful collection removes it.

From the partial failed trace, a 4,500-tick fight projects to 350,275,352 raw bytes (~334 MiB), or approximately 77,287,664 gzip bytes (~73.7 MiB). All 180 fights project to 63.05 GB raw / 13.91 GB gzip before margin; with 20% margin, 75.66 GB raw / 16.69 GB gzip (70.46 / 15.55 GiB). These extrapolations assume the observed per-tick rate and are not completed-fight measurements. The host fixture reports its actual complete bytes; the twenty-fight sample replaces this projection using the slowest full-duration-normalized raw/compressed fight. Additional training/audit files and original failed evidence need their own disk space.

The original ledger remains intact at SHA256 `9ce08f9bc7255e6d8c6b47d6ed8bf492e0d0aa51b01c169a6c6c9f9893b76bc4`. Recovery `2c956c4343738a11` explicitly registers the rebuilt code/binary prospectively against the same 180 sealed requests and unchanged timing tags. The new ledger SHA256 is `c44be9853988c5eafc59ad49677a698266dd9c6f3001c99c225f2fe9539a0961`. Failed receipt/stdout/stderr hashes are checked whenever the recovered ledger is loaded. Zero completed collection fights was required; unrelated integration fixture completions do not block recovery. Registration did not retry a fight. The next sample creates a new random attempt ID and retains the old failure. Baseline binary, generated host and build manifest were also preserved locally before rebuilding.

Build: 24.736 seconds; identity admission passed. Focused tests ran once after the complete code/review batch: **14 passed, 2 host-only skips**, 8.833 seconds wall (8.16 seconds pytest). Coverage includes existing five-arm native inference parity, a real production `collectTick` contract across 4,501 ticks with changing 2,500-key maps, root/string lifetimes, streaming 32 MiB through bounded reads, retained failed compressed evidence and exact sealed-request recovery/tamper detection.

The full host regression declares a strict 512 MiB bound, records sampled RSS plus native `getrusage` peak and periodic arena/shape counts, and prints/stores bytes and duration. It runs a separate fresh-entropy 150-second fixture with 100 living units in separated armies, ensuring every tick retains the maximum entity bank without early elimination. It does not exercise long combat threat evolution; the existing 3-second network integration and the ensuing collection cover additional behavior. PASS requires the full duration/frame count, surviving armies, final native profile and a positive peak below the bound. This fixture was **not run here**: the binary launches, but sandbox `ps` is denied and `pgrep` cannot get the process list. The repository process/RAM admission cannot pass; it was not bypassed. No full-host RSS bound is claimed.

The quick owner recheck and all dispositions are recorded separately. No living Markdown documents are included in source identity, and the current plan is untouched. All task changed paths are listed only in the task manifest.

Run the host sequence below once; allow approximately 1–5 minutes for the host tests, bounded at 300 seconds for the memory fixture. The twenty-fight sample initially budgets 4–10 minutes; its measured projection and existing LAB_CAP govern further collection. The delivered binary is already rebuilt and admitted, so do not rebuild or repeat the passing focused tests unless sources change. The explicit recovery command is idempotent and verifies its existing registration.

```sh
cd /Users/new/RiderProjects/ai_RPG_test
set -e
export STAGEA=evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stagea
export STAGEA_PYTHON=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/_local/mlenv/bin/python
export PYTHONPYCACHEPREFIX="$STAGEA/_local/pycache"
"$STAGEA_PYTHON" -c 'import sys; from pathlib import Path; sys.path.insert(0, str(Path(sys.argv[1]).resolve())); from collect import identity; print(identity()["binary_sha256"])' "$STAGEA"
STAGEA_HOST_TEST=1 "$STAGEA_PYTHON" -m pytest -q -x -s "$STAGEA/test_stagea_host.py" "$STAGEA/test_stagea_memory_host.py"
"$STAGEA_PYTHON" "$STAGEA/collect.py" recover-memory
"$STAGEA_PYTHON" "$STAGEA/collect.py" sample
```
