# Astelia typed C++ tactical simulator

S2 adds the outside-controller plug: typed copied observations, validated move/target decisions, and the closed `passthrough` (test-only), `nearest`, and `hold` registry on either side. See [S2_PLUG_REPORT.md](S2_PLUG_REPORT.md) for the initial implementation and [S2_RECHECK_REPORT.md](S2_RECHECK_REPORT.md) for the repaired build and fresh engineering checks awaiting Claude review. Nearest/hold control of the special player body is explicitly unsupported; ordinary armies and observing an enemy player remain supported. The qualification below describes the archived pre-S2 build. Current build identities and regression evidence are in [s2_plug_recheck_r1/S2_RECEIPT.json](s2_plug_recheck_r1/S2_RECEIPT.json); the original [S2 receipt](s2_plug_r2/S2_RECEIPT.json) remains unchanged.

The full migration is **ENGINEERING_READY**. All 159 source-function responsibilities are implemented in typed modules. Fresh uncached elapsed speed-ups are **14.23x basic50**, **12.92x elite**, **9.50x elite-fast**, and **15.26x artillery rollout**, exceeding the owner's 3x minimum and 5x target in every fixed group. See [PORT_REPORT.md](PORT_REPORT.md) for behavior changes, work differences and measurements, and [qualification.json](native_qualification_r1/qualification.json) for the bound engineering evidence. Future AI experiments retain the original cross-family review prerequisite; this work changes no scientific status.

Build and run the complete typed target from the repository root:

```sh
python3 evidence/tactical_composition_demo/astelia_cpp/build.py --engine native
evidence/tactical_composition_demo/astelia_cpp/build/astelia_native < fights.jsonl
```

One JSON fight per input line returns one summary with the frozen source's thirteen fields. An input array returns an array of summaries; keep tracing off for array batches. Multiple fights can share a process. For example, a line in `fights.jsonl` can be:

```json
{"mode":"reactive","opponent":"wolfpack","options":{"seed":1,"scenario":"mirror","rules":"game","duration":20,"ai":[{"level":"elite-fast"},{}]}}
```

The complete target supports both rules, every brain/level/skill, formations/plans, abilities, player/hunters/skirmish/custom/carried armies, commands/combos, the frozen network, lookahead and artillery rollout. Game rules enable sandbox abilities through `sandboxAbilities:true`, following the source. `opponent` resolves through the source-derived pool/preset API; explicit options override it. Add `trace:true` for the initial state and every step, or `debug:true` alongside tracing for casting/energy/pack/search diagnostics. `--metrics` writes real execution/branch counters to stderr; `--catalog` returns compiled source-derived constants.

Native controllers include [src/native/api.h](src/native/api.h), [src/native/formation.h](src/native/formation.h), [src/native/search.h](src/native/search.h) and [src/native/artillery.h](src/native/artillery.h). Worlds own mutable typed state; configuration/network data are immutable. Generation-checked references survive slot reuse, and RAII branch leases own independent mutable copies. The C++ simulation invokes no JS engine or Node process. JSON parsing is confined to the host boundary. The [feature/clone/field-reader ledger](native_feature_ledger.json) gives named-function module/check ownership; [NATIVE_FIELD_OWNERSHIP.md](NATIVE_FIELD_OWNERSHIP.md) resolves the 38 table-callback/export-only field reader projections.

The final suite passed 158 checks and combined ASan/UBSan contracts. All 623 requests completed freshly, with 20 invariant-checked complete traces (11,454 frames) and 27 deterministic repeats. Relative to the stored frozen JS baseline, 124 summaries match exactly, 401 differ, and 98 source-crash fixtures now complete. Whole-fight parity was relaxed by the [approved architecture plan](PERFORMANCE_REWORK_PLAN.md); the detailed differences are retained in [coverage.json](native_coverage_r1/coverage.json). This is balanced factor coverage, not a full Cartesian product.

Quickly compare all cached current-build results against the frozen JS reference, without executing combat:

```sh
python3 evidence/tactical_composition_demo/astelia_cpp/compare_native_cached.py
```

The initial cache is populated by exhaustive coverage. It is stored under ignored `build/combat_cache`, bound to request, binary, source, network, host/runtime and validator identities. A missing/stale entry fails the quick comparison. Fresh coverage on a changed admitted build is:

```sh
python3 evidence/tactical_composition_demo/astelia_cpp/verify_native.py --output /private/tmp/astelia-native-coverage-new
```

Verification refuses an existing receipt. Native coverage runs uncached; its JS reference is explicitly stored canonical data. The final cache probe proves replay adds no combat execution and a seed change executes again. Performance always bypasses this cache and uses fresh JS/C++ processes.

The final evidence is:

| Evidence | Receipt |
|---|---|
| Bound completion | [qualification](native_qualification_r1/qualification.json) |
| Final tests and memory/bounds checks | [checkpoint](native_full_checkpoint_r3/README.md) |
| 623 fresh native fights, twenty traces, cache/replay | [coverage](native_coverage_r1/README.md) |
| Four balanced uncached groups | [timing](native_benchmark_r1/benchmark.json) |
| Actual branch/inference/prediction work | [work audit](native_work_r1/work_audit.json) |
| Equal-operation engine costs and record/column layout | [matched costs](native_costs_r4/README.md) |
| Exact admitted sources, three compressed binaries and manifests | [archive](native_qualification_r1/source_archive/ARCHIVE.json) |

The timings include startup/JSON/network setup and full fight execution. All four samples per group are retained in JS/C++/C++/JS order, with wall/CPU/load and zero cache hits. Outcomes naturally change the executed steps and live-body work; the separate audit verifies branch budgets/horizons and equal-state probes show direct engine-cost improvement. Measurements describe this busy M1 Pro/clang/Node environment. No fast math is used. `--portable` omits host CPU tuning but has separate build identity and needs its own qualification.

Pinned frozen sources are unchanged:

| Source | SHA256 |
|---|---|
| `../astelia_snapshot/formation_sim.js` | `85b16e9b84b42b831dd2e64a7055474b6df902e4c1ffd635e6670fc6fb665733` |
| `../astelia_snapshot/bc_net.json` | `d11e9a2da43cb0eb5b8b9539be4ab5834e750b4148121d56e632c75d7fb2e3e5` |

The mechanical exact port remains a historical diagnostic target, built explicitly with `build.py --engine legacy` (also the script's compatibility default). It produces `build/astelia`. `check_reference.py`, `compare.py` and `verify_port.py` retain their strict legacy contracts and do not qualify the typed target. That original build matched 623 outcomes, including 98 errors, and twenty traces but was 4.99x slower; the later r9 reached only 1.169x elapsed speed-up. Historical receipts remain unchanged. The original request is [PORT_REQUEST_CODEX.md](PORT_REQUEST_CODEX.md); later owner-authorized architecture/numeric changes are described in the revision-2 plan and current report.

Browser DOM/export glue, bit-string traces, exact UI prose and browser-only AAR presentation are excluded; native events, observations, commands, ability APIs and search records are retained. Typed simulation uses no external libraries. The legacy compatibility math retains its upstream license notices in `src/v8_ieee754.cpp` and `LICENSE.v8`.
