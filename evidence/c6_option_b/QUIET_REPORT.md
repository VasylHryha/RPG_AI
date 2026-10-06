NOT_READY

C6 option B queued batch, 6 October 2026. Implementer: Codex, GPT-6. All 17 full-world computations and all 16 zero-tolerance comparisons completed successfully. The normal timing rule fails on smoke world 0: **392.269264667 seconds**, above 360 seconds. The machine was not demonstrably quiet during timing; these are observed, unadjusted times, not quiet-machine estimates. C6 remains BLOCKED / R006 STOP; STATUS.json is unchanged.

**Conditions and execution**

Initial load at 16:17 Europe/Kiev was **5.34 / 6.10 / 18.20** (1/5/15 minutes). The supervisor sampled every 30 seconds and waited 210 seconds, from 2026-10-06T13:18:19Z until 2026-10-06T13:21:49Z, when load was **2.981 / 4.751 / 14.248**. The one-minute load fell below 3 before ten minutes, so the ten-minute-high trigger and additional 60-minute wait were not reached. Load rose again during execution; its maximum recorded one-minute value was **49.07470703125**. No time is divided by load or otherwise normalized.

The owner's message reports that the 0g and 0h runs had finished. Global process inspection (`ps -axo pid,ppid,%cpu,%mem,etime,command -r`) was sandbox-refused with `operation not permitted`; the optional follow-up confirmation received no answer. Therefore absence of other heavy jobs is **not independently confirmed**. Unrelated 0g/0h source changes and commits landed while this batch ran; they are listed in the preservation record and were not made by this task. Their CPU contribution is not inferred. The timing phase started under elevated load, not an independently verified quiet condition.

Normal smoke pair start: 2026-10-06T15:29:21Z, load 28.275 / 20.235 / 17.591. Development pair start: 2026-10-06T15:36:21Z, load 12.562 / 17.364 / 17.670. Batch completed 2026-10-06T15:41:51Z.

New output root: [quiet_session_20261006_161801/](quiet_session_20261006_161801/). The stopped 09:15 session is unchanged, including its untracked files and Python cache. The argv and order match `recheck/QUEUED_CHECKS.json`; only its output prefix was relocated to this fresh folder. One new original-reference world (development 1), then twelve audited worlds (sequential, forward, reverse for smoke/development 0/1), then two normal smoke processes together, then two normal development processes together, then the four timing-output comparisons. Each computation and comparison used a fresh process. Maximum simultaneous world processes: **2**; each parallel world used **4 compute workers plus one coordinator**, with numerical helper teams set to one before NumPy import. `caffeinate -i -s` kept the machine awake and was stopped after batch completion.

Periodic UTC, load, child PID and observed process wall were recorded. Periodic per-process CPU/RSS/cache counters were unavailable: process telemetry is restricted and the pinned helpers publish these only at completion. Final compute CPU time, peak RSS, cache counters and separate serialization costs are in each COSTS.json. Event end times include up to 30 seconds of supervisor polling delay; the readiness rule uses the helper's world_seconds, not these observed process durations.

**Pinned identities**

All delivery inventory hashes, both live library/BUILD pairs and all three existing reference hashes matched before execution and after completion. Source-pin validation passed in all **17** computations. Every START/COSTS helper hash matches the initial tracked-file snapshot; native and reference BUILD records match [VALIDATED_IDENTITIES.json](quiet_session_20261006_161801/VALIDATED_IDENTITIES.json). No rebuild occurred.

- Option B dylib SHA-256: `6ba390940719dd7b77cd81cee1878faebce296201be728b4c487baf9d43b23a5`.
- Reference dylib SHA-256: `4830141d5585f6a0e684808ccf339314bc3205f7dd6a30c4a5838b0dce5e01f4`.
- Comparator SHA-256: `046e9ed04b5059626f6119246d151198872ed1b9d9a56d41f72b419e1b8fe01f`.

Compiler flags retain `-O2 -fno-fast-math -ffp-contract=off`. The scientific model, thresholds, entropy settings and project code were not changed by this task. The evidence-only supervisor was copied from the stopped attempt with fresh output mapping and matching preflight-record handling.

**Every stored comparison**

All used `--exact`: zero absolute tolerance, float bit/type checking, no changed scientific digests, and every nested diagnostic and discrete/Boolean value retained. Only the established root cost/build fields are excluded by the unchanged comparator. Compressed whole-file hashes differ because those root costs differ; input/output/result SHA-256 bindings are recorded separately in RUN_RECEIPT.json.

| Computation | Result | Numeric values | Boolean values | Max error | Changed digests |
|---|---|---:|---:|---:|---:|
| [smoke_0_sequential](quiet_session_20261006_161801/worlds/smoke_0_sequential_EXACT.json) | PASS | 3,045,093 | 2,847 | 0 | 0 |
| [smoke_0_forward](quiet_session_20261006_161801/worlds/smoke_0_forward_EXACT.json) | PASS | 3,045,093 | 2,847 | 0 | 0 |
| [smoke_0_reverse](quiet_session_20261006_161801/worlds/smoke_0_reverse_EXACT.json) | PASS | 3,045,093 | 2,847 | 0 | 0 |
| [smoke_1_sequential](quiet_session_20261006_161801/worlds/smoke_1_sequential_EXACT.json) | PASS | 1,460,200 | 1,396 | 0 | 0 |
| [smoke_1_forward](quiet_session_20261006_161801/worlds/smoke_1_forward_EXACT.json) | PASS | 1,460,200 | 1,396 | 0 | 0 |
| [smoke_1_reverse](quiet_session_20261006_161801/worlds/smoke_1_reverse_EXACT.json) | PASS | 1,460,200 | 1,396 | 0 | 0 |
| [development_0_sequential](quiet_session_20261006_161801/worlds/development_0_sequential_EXACT.json) | PASS | 2,601,660 | 2,512 | 0 | 0 |
| [development_0_forward](quiet_session_20261006_161801/worlds/development_0_forward_EXACT.json) | PASS | 2,601,660 | 2,512 | 0 | 0 |
| [development_0_reverse](quiet_session_20261006_161801/worlds/development_0_reverse_EXACT.json) | PASS | 2,601,660 | 2,512 | 0 | 0 |
| [development_1_sequential](quiet_session_20261006_161801/worlds/development_1_sequential_EXACT.json) | PASS | 2,600,554 | 2,501 | 0 | 0 |
| [development_1_forward](quiet_session_20261006_161801/worlds/development_1_forward_EXACT.json) | PASS | 2,600,554 | 2,501 | 0 | 0 |
| [development_1_reverse](quiet_session_20261006_161801/worlds/development_1_reverse_EXACT.json) | PASS | 2,600,554 | 2,501 | 0 | 0 |
| [quiet_smoke_0](quiet_session_20261006_161801/worlds/quiet_smoke_0_EXACT.json) | PASS | 3,045,093 | 2,847 | 0 | 0 |
| [quiet_smoke_1](quiet_session_20261006_161801/worlds/quiet_smoke_1_EXACT.json) | PASS | 1,460,200 | 1,396 | 0 | 0 |
| [quiet_development_0](quiet_session_20261006_161801/worlds/quiet_development_0_EXACT.json) | PASS | 2,601,660 | 2,512 | 0 | 0 |
| [quiet_development_1](quiet_session_20261006_161801/worlds/quiet_development_1_EXACT.json) | PASS | 2,600,554 | 2,501 | 0 | 0 |

The smoke 0/1 and development 0 comparisons reuse exactly the three existing references pinned by QUEUED_CHECKS.json. Development 1 uses this session's newly generated original-reference world; its world computation took 355.870119042 seconds and serialization 6.375965625 seconds. This reference timing is not part of the normal-runtime verdict.

**Full returned-array audits**

| Audited computation | Calls / bit-identical calls | Float64 values | Max error |
|---|---:|---:|---:|
| [smoke_0_sequential](quiet_session_20261006_161801/worlds/smoke_0_sequential/COSTS.json) | 9,824 / 9,824 | 2,231,845,380 | 0 |
| [smoke_0_forward](quiet_session_20261006_161801/worlds/smoke_0_forward/COSTS.json) | 9,755 / 9,755 | 2,208,097,512 | 0 |
| [smoke_0_reverse](quiet_session_20261006_161801/worlds/smoke_0_reverse/COSTS.json) | 9,810 / 9,810 | 2,227,026,972 | 0 |
| [smoke_1_sequential](quiet_session_20261006_161801/worlds/smoke_1_sequential/COSTS.json) | 4,194 / 4,194 | 906,468,540 | 0 |
| [smoke_1_forward](quiet_session_20261006_161801/worlds/smoke_1_forward/COSTS.json) | 4,178 / 4,178 | 900,961,788 | 0 |
| [smoke_1_reverse](quiet_session_20261006_161801/worlds/smoke_1_reverse/COSTS.json) | 4,182 / 4,182 | 902,338,476 | 0 |
| [development_0_sequential](quiet_session_20261006_161801/worlds/development_0_sequential/COSTS.json) | 4,829 / 4,829 | 996,971,880 | 0 |
| [development_0_forward](quiet_session_20261006_161801/worlds/development_0_forward/COSTS.json) | 4,818 / 4,818 | 993,185,988 | 0 |
| [development_0_reverse](quiet_session_20261006_161801/worlds/development_0_reverse/COSTS.json) | 4,819 / 4,819 | 993,530,160 | 0 |
| [development_1_sequential](quiet_session_20261006_161801/worlds/development_1_sequential/COSTS.json) | 4,733 / 4,733 | 977,364,492 | 0 |
| [development_1_forward](quiet_session_20261006_161801/worlds/development_1_forward/COSTS.json) | 4,723 / 4,723 | 973,922,772 | 0 |
| [development_1_reverse](quiet_session_20261006_161801/worlds/development_1_reverse/COSTS.json) | 4,725 / 4,725 | 974,611,116 | 0 |

Every full production-step array returned in those audited executions matched the original bit for bit. Audit call counts can differ across schedules because cache reuse differs; all calls actually performed were audited. These are three schedules of four reserved worlds, not independent populations.

**Normal timing and registered rule**

| World | World seconds | Compute CPU seconds | Serialization seconds | Peak RSS after serialization (MiB) | ≤360 s |
|---|---:|---:|---:|---:|---|
| [quiet_smoke_0](quiet_session_20261006_161801/worlds/quiet_smoke_0/COSTS.json) | 392.269264667 | 759.793077 | 7.129522 | 1831.766 | FAIL |
| [quiet_smoke_1](quiet_session_20261006_161801/worlds/quiet_smoke_1/COSTS.json) | 184.238800792 | 322.078673 | 3.791560 | 1075.266 | PASS |
| [quiet_development_0](quiet_session_20261006_161801/worlds/quiet_development_0/COSTS.json) | 195.965555167 | 347.762849 | 6.743232 | 1196.219 | PASS |
| [quiet_development_1](quiet_session_20261006_161801/worlds/quiet_development_1/COSTS.json) | 186.391564458 | 328.968707 | 6.654708 | 1100.266 | PASS |

These four timing runs used native/parallel/forward with **no audit**, fresh process caches and the same pinned builds/helpers. World seconds exclude startup and serialization. Compute CPU is summed across the process threads; RSS is the helper's measured process peak through serialization, not a cache budget or a machine memory-capacity claim.

**FAIL using unrounded recorded values:**

`392.269264667 × 40 / 2 × 1.5 = 11768.07794001 > 10800`

Smoke world 0 exceeds its 360-second limit by **32.269264667 seconds**. The other three worlds meet it. All four timing outputs pass their independent stored exact comparisons. This failed observed rule does not establish what the same code would cost on a genuinely quiet machine; no such adjusted time or extrapolation is supplied.

| Normal world | Retired hits | Control hits | Eligible misses | Avoided material RK steps | Final worker cache payload (MiB) |
|---|---:|---:|---:|---:|---:|
| quiet_smoke_0 | 1,399 | 19 | 3,999 | 6,231,000 | 1092.009 |
| quiet_smoke_1 | 330 | 7 | 1,765 | 1,497,000 | 783.624 |
| quiet_development_0 | 351 | 5 | 1,742 | 1,645,000 | 989.664 |
| quiet_development_1 | 422 | 11 | 1,615 | 1,997,000 | 845.756 |

The full per-worker counter snapshots remain in COSTS.json. Counters are final snapshots, not peaks. Smoke 0 traversed a complete chain; the other three worlds ended without chain completion according to the unchanged protocol, with invalid=null in all four. This evidence covers those observed paths and does not bound unobserved later panel workloads.

**Records, preservation and remaining boundary**

- [RUN_RECEIPT.json](quiet_session_20261006_161801/RUN_RECEIPT.json): all argv, input/output/result hashes, comparison results, source/build/helper checks, timings and unrounded rule calculation.
- [EVENTS.jsonl](quiet_session_20261006_161801/EVENTS.jsonl), [PREFLIGHT.json](quiet_session_20261006_161801/PREFLIGHT.json), [INITIAL_CONDITIONS.json](quiet_session_20261006_161801/INITIAL_CONDITIONS.json): conditions, waiting, process starts/ends and telemetry limits.
- [PRESERVATION_CHECKS.json](quiet_session_20261006_161801/PRESERVATION_CHECKS.json): original C6/source/build/reference and stopped-session identities unchanged; unrelated concurrent workspace changes preserved.
- [RAW_FILES_OUTSIDE_GIT.json](quiet_session_20261006_161801/RAW_FILES_OUTSIDE_GIT.json): hashes and byte counts for all raw world dumps and command logs, retained on disk outside git. Python caches and raw dumps are ignored locally; no file over 50 MB is included in the delivery. The existing global large-file inventory remains unchanged.

No extra worlds, final entropy, R007 registration, mutation probe, recorded panel, C0 experiment, full-suite rerun, gate-stamp edit, or milestone-status change occurred. Exactness passed; observed normal runtime failed; independently verified quiet conditions remain unavailable. No scientific qualification or milestone acceptance follows. The owner recheck and its disposition are tracked in docs/PLAN_CURRENT.md; delivery provenance and bundle verification are recorded separately.
