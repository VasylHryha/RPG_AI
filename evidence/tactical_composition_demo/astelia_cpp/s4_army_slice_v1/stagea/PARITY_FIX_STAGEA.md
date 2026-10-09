# Stage A certified float32 near-tie recovery (decision 0036)

The training model remains float32; export/deployed inference remains float64. The native gate is unchanged: zero categorical mismatches and maximum absolute error <= 1e-8. Nonfinite output or sequence-dimension differences fail.

For each categorical head, compare all physical ticks against the float64 reference and measure that head's maximum absolute logit error e. The declared near-tie bound is min(2e, 1e-4). A perturbation bounded by e can reverse two logits only across a gap <= 2e. The independent 1e-4 ceiling prevents a large measured error from excusing a material flip. Every float32 mismatch must have both its float64 top-two gap and the float64 winner-minus-selected-class deficit <= this bound. The second condition prevents a third class from hiding behind an unrelated top-two tie. Every mismatch records its frame, row, unit, time, head, classes, gap, selected-class deficit, error, bound and certification. An uncertified mismatch fails. Matching categorical outputs are unchanged.

Real-host evidence for the original failing N2J0 validation_0083 fight, in explicitly opted-in test mode: all 1,517 frames and 47,963 unit rows were replayed against the trained export. The single mismatch is fire, unit 21, frame index 1486, row index 2, time 49.566666666666414 s. Float32 chose automatic (class 0); float64 chose hold (class 1). The float64 top-two gap and selected-class deficit are both **1.9220437083244946e-5**. Fire-head measured error is **5.1614879754247056e-5**, so 2e = 1.0322975950849411e-4; the ceiling makes the declared bound **1e-4**. It is certified. Overall float32 error remains **5.563866880287094e-5**, one mismatch, zero uncertified mismatches. Native float64 has **zero mismatches** and error **1.0658141036401503e-14**. Native replay peak RSS is 9,388,032 bytes, below the fixture's 512 MiB bound. This test-mode evidence does not complete production parity or authorize outcomes.

The original failed per-fight receipt and failed invocation remain unchanged, as do all twenty old per-fight receipts. Recovery seals their hashes and the previous inference recovery. All 431 original baseline artifact hashes and all host-test fixed training hashes are unchanged. Both builds used the existing build script and admission gate and produced the exact original native binary hash. Rebuilding was required because the build manifest pins the Python sources as well as C++ sources. No native sources, trained exports, checkpoints, data, sealed training budget, owner cap, or living documents were changed.

Production parity reruns every arm on every validation fight into a distinct rule-version directory; old-rule successful receipts are retained and are not reused. The normal invocation remains resumable within the new rule. Readout requires the current rule and exact all-arm/all-validation coverage. Full production parity (250 arm/fight sequences) and readout are pending; this repair ran only the required failing fight in test mode.

Validation ended with **47 passed**, no skips, in 24.09 s pytest / 24.712 s measured wall. The first launcher resolved the virtualenv symlink and failed before any test could run; its receipt remains. The first actual batch passed 46 checks, then the host test stopped before replay because a recovery module was first imported while fixture paths were mocked. Importing it during test collection fixed that isolation issue; the failed batch and first registration remain as evidence. The complete corrected batch then passed once. No successful batch was routinely repeated. Build walls were 24.623 s and 24.822 s. The separate requested owner recheck found the isolation issues and inconsistent cached-certification handling; all were fixed and its final evidence disposition has no blocking findings.

No changes were made to docs/PLAN_CURRENT.md. The recheck is recorded within this delivery under the owner's explicit override. The path-only delivery manifest is UNCOMMITTED_STAGEA_PARTIE.txt; it also identifies the preexisting failed invocation retained for delivery. Local scratch logs/raw replay streams are under the existing ignored _local directory and are not publication receipts.

Recovery is already registered. Run the following on the real host from the repository root. Existing cap, process/RAM admission and sequential look/harm gates remain authoritative; set -e stops at any refusal.

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
