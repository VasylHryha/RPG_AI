# B2 speed delivery

HEAD remains 8df62a8934fb132802676afcd26267bc1ad80392. Owner authority remains the existing Claude-written cap, at most 16200 seconds. No training cap, availability threshold, optimizer count, loss, label, split, or promotion/parity gate was lowered. No commit was made. Stage A, Stage B, rev2, PLAN_CURRENT and living-document pins were untouched.

Coverage now checks every sixth recorded physical tick, with a deterministic phase `sha256(tag)[:8] modulo 6`, across all indexed fights. At 30 Hz this is 5 Hz. Round 0 declares 180 fights, 228456 physical rows and **38077 expected sampled frames**. Achieved sample size in this session is **zero**: the host process gate refused before replay. Raw, fit-target and checkpoint-target tables report sample denominators and exact worst-case finite-population error bounds. A deterministic correlated sample cannot justify a narrow distribution-free confidence interval; unsampled outcomes may all pass or all fail. Existing numerical thresholds apply to this declared sample. This is availability admission, not certification of the full population or closed-loop behavior.

One native C++ call builds every own unit's banks per frame. Python nearest-label mapping reuses those banks. Only N2 needs drift evaluation; it updates all units together at every physical tick with unchanged dt and exact recurrent state, while skipping unused candidate/output heads. Other arms have identically zero drift. Sampling does not alter or reset N2's physical-prefix evolution.

Measurement precomputes public candidates once per fight and shares the cache across arms, epochs, optimizer reloads and calibration. The compressed arrays retain exact float64 points, seven nonzero feature-tail fields, type and source; padding and the one-hot prefix are reconstructed on consumption. Cache keys cover raw identity, native code and public-input reconstruction code. Raw and cache hashes are checked. Scratch materialization streams to a temporary file; a fight is limited to 512 MiB uncompressed, total compressed storage is projected against 20 GiB and actual free space, retaining a 2 GiB reserve. Actual cache projection is **unmeasured** until a host run succeeds.

The timing sample selects the largest-frame training and validation fight per panel from metadata. Each core arm executes two optimizer windows per training panel, **12 optimizer steps total** (16 with optional N1h), bounded to 20. It reports each step's wall/CPU/RSS cost, separate prefix/read/window/validation costs, cache build seconds/bytes and the 10-epoch lane projection with the existing 1.2 margin. Memoryless stored-state refresh requires no prefix forward; recurrent refresh skips unused heads. Calibration skips unused heads outside its unchanged four windows. Tail projection includes worker test evaluation plus calibration validation and test. Training reads the sealed cache, and refuses a projection above the live owner cap.

## Verification and remaining host work

Two focused pytest batches consumed 6.35 + 11.97 = 18.32 seconds of reported test time. The first stopped at one pre-existing snapshot failure after seven passes; the continuation deselected those already-run checks and passed the remaining 29. Thus **36 passed, one pre-existing failure**. The failure is the old expected hash for stageb/calibrated_parity.py in PROTECTED_SOURCE_BASELINE.json: actual/current-HEAD hash is a97ee31133ea655a5294aaa50c9805966a04d2547ad4811b910a56ab106b1ec3, while the snapshot expects 0d48a0384a0acb47755631f95af084badac7094128505cab206adbce8f5292c8. Neither file was changed here. Native inference, native bank values/order/source indices, cached labels, recurrent prefix state equivalence, cache roundtrip/reuse/corruption, empty aim audits, malformed values, sampling bounds, and diagnostic timing fields passed.

A separate reviewer received the owner's request verbatim. All reported material issues were fixed before the final tests. The reviewer report and validation receipt record the disposition and limits. No numeric quality score is assigned.

Both coverage and measurement test-mode invocations were refused by the unchanged process gate: `pgrep` returned 3, `sysmon request failed with error: sysmond service not found`, `Cannot get process list`. No gate was bypassed. **Achieved full coverage time, training per-step cost, disk projection and round-0 fit projection are not available from this sandbox.** The delivery does not claim that coverage achieved 15 minutes or that training was admitted.

## Exact host commands

Run in the normal host terminal, with the existing cap authority and prior round-0 preparation. The B2 build source identity changed, so rebuild first; no Stage A/B/rev2 rebuild is requested. Retain old receipts. The earlier stopped coverage did not seal round0/COVERAGE.json, and this session did not seal a training budget.

```sh
cd /Users/new/RiderProjects/ai_RPG_test
B2=evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stageb2
ML=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/_local/mlenv/bin/python
export B2_VARIANT=react_on PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
nice -n 15 "$ML" "$B2/build.py"
nice -n 15 "$ML" "$B2/coverage.py" --round 0
nice -n 15 "$ML" "$B2/train.py" measure --round 0
nice -n 15 "$ML" "$B2/train.py" run --round 0
```

Expected times: build approximately 30–90 seconds based on the prior 30.68-second build (new build unmeasured); coverage has a strict **900-second maximum**, projects its remaining work and reports achieved seconds/sample size; measurement time is **unmeasured** and includes one shared full candidate preprocessing pass plus 12 optimizer steps, with the live 4.5-hour maximum; training's expected time is exactly `round0/TRAIN_BUDGET.json:projected_seconds`, and it is admitted only when that value is **at most 16200 seconds**. Measurement prints per-step seconds and the disk/time projection. Do not turn these bounds into measured performance claims.

Optional smaller host diagnostics, if wanted before the full sampled check: `coverage.py --round 0 --test-mode` selects the largest train fight per panel and writes only a TEST_ONLY run receipt; `train.py measure --round 0 --test-mode` builds four timing-fight caches under round0/speed_test and writes TEST_ONLY timing there. Both retain the process gate/cap and cannot authorize training. Their run times are unmeasured. After these diagnostics, use the production commands above to seal actual coverage/cache/budget admissions.
