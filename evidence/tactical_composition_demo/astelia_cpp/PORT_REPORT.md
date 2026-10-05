READY

The complete typed C++ migration is **ENGINEERING_READY** under the owner-approved revision-2 rewrite contract. All four fixed workload groups exceed both the 3x minimum and 5x target. The authoritative bound receipt is [native_qualification_r1/qualification.json](native_qualification_r1/qualification.json). This is engineering completion, not independent scientific acceptance; the requested cross-family review remains a prerequisite before any AI experiment uses this simulator. No experiment, frozen JS, committed historical receipt or milestone status was changed.

The engine uses contiguous typed hot unit records, conditional state pools, generation-checked references, indexed spatial buckets and reusable independent branch worlds. JSON and strings stop at the host/configuration boundary. Combat, all brains/skills/levels, seven shapes, sixteen presets, twenty-six plans, both rules, six abilities, player limbs/manual attacks, spawning, commands/combos, network inference, lookahead and artillery rollout are implemented. [native_feature_ledger.json](native_feature_ledger.json) maps all 159 source functions and separately accounts for table callbacks, field readers and clone responsibilities. [NATIVE_FIELD_OWNERSHIP.md](NATIVE_FIELD_OWNERSHIP.md) resolves the 38 field-reader entries whose source owners are table callbacks/export glue rather than named functions. The typed controller entry points are in [src/native/api.h](src/native/api.h) and [src/native/formation.h](src/native/formation.h).

| Engineering check | Result |
|---|---|
| Final focused suite | 158 passed; 143.40 s reported by pytest, 143.67 s process elapsed |
| Combined address/undefined-behavior instrumentation | Core, combat, formations, search, artillery and public API contracts passed; zero diagnostic stderr |
| Fixed 623 requests, fresh native execution | 623 completed; zero native errors/check failures |
| Stored frozen-JS summary diagnostics | 124 identical; 401 completed with different summaries; 98 documented JS crashes repaired |
| Complete native traces | 20 retained, 11,454 frames including initial states; physical/identity/energy/casting/completion checks passed |
| Determinism | 27 requests repeated freshly with identical full outputs; total coverage execution 650 fights |
| Cache proof | One fresh execution, then one cache hit with no new execution; changed seed executes again |
| Cached comparison | All 623 requests compared in one pass; zero combat execution |
| Work accounting | Four groups passed; source instrumentation preserves every uninstrumented JS output |
| Source/build retention | 99 hash-verified files, three compressed executables and their manifests in [source_archive](native_qualification_r1/source_archive/ARCHIVE.json) |

Fresh JS is used for performance and matched-cost probes. Coverage explicitly uses admitted stored canonical JS reference data; it does not claim 623 new JS executions. Native coverage bypasses the result cache. Raw outcomes and each trace's first semantic difference remain in [native_coverage_r1](native_coverage_r1/coverage.json).

Timing includes process startup, configuration/network setup, JSON IO and simulation. Each fight's simulation is single-threaded; no worker pool distributes fights. Measurements ran serially in the fixed JS/C++/C++/JS order on an Apple M1 Pro (10 cores, 32 GiB), macOS arm64, Node 24.18.0 and Apple clang 21.0.0. The native build uses C++17, O3, ThinLTO and host tuning, with fast math disabled and contraction off. Node may use its normal runtime/background GC or compilation threads. Raw CPU time covers the entire child process.

| Fixed group | Fights per sample | Mean JS wall s | Mean C++ wall s | Elapsed speed-up | Fastest JS / slowest C++ | CPU speed-up |
|---|---:|---:|---:|---:|---:|---:|
| basic50 | 50 | 35.591147 | 2.501419 | **14.228x** | 14.082x | 15.595x |
| elite | 4 | 14.606277 | 1.130698 | **12.918x** | 12.288x | 14.272x |
| elite-fast | 4 | 3.935388 | 0.414354 | **9.498x** | 9.463x | 12.369x |
| artillery-rollout | 4 | 1.395109 | 0.091418 | **15.261x** | 15.208x | 24.745x |

All four samples per group are retained; none was excluded or selected for its speed. The final qualifier requires every group to exceed 3x in both the worst balanced wall comparison and aggregate CPU cost. One-minute machine load ranged 69.53–113.91 during these samples; raw before/after 1/5/15-minute loads are in [native_benchmark_r1/benchmark.json](native_benchmark_r1/benchmark.json). These are busy-machine measurements for this admitted build, not a portable hardware estimate.

Natural work differs with changed outcomes. Basic50 executes exactly 30,000 outer steps in both engines. Native/JS outer-step ratios in elite, elite-fast and artillery rollout are 0.976, 0.957 and 0.978; their branch-step ratios are 0.929, 0.949 and 0.973. Elite branch unit actions are about 0.780 of JS; this contributes to end-to-end throughput. The separate audit verifies unchanged requested budgets and the actual 2/3-second horizons with 0.1 or 1/30-second branch steps. Native elite executes 524 forks and 50 inferences; elite-fast 467 forks and 48 inferences; artillery-only 190 rollout forks. No search path was disabled to meet the timing gate. The complete raw counters are in [native_work_r1/work_audit.json](native_work_r1/work_audit.json).

To isolate engine cost from different outcomes, matched-state probes execute identical operation counts and checksums. Production geometry is 5.896x faster, dense network forward inference 3.708x, and fork/playout 18.715x. Both engines execute exactly 300 forks, 3,000 steps, 300,000 unit actions and 9,000 projectile iterations in that probe. The complete clone comparison includes all hot fields and common mutable conditional/tactical/ability/player/projectile/effect/spawn authority, with identical team/grid rebuilding. Production records take 0.842 of column geometry time and 0.853 of complete column-copy time; both pass the predeclared 1.2 limit. See [native_costs_r4/matched_costs.json](native_costs_r4/matched_costs.json).

The earlier layout probes r1–r3 remain CHANGES_REQUIRED diagnostics. They mixed a production query wrapper with a constant-specialized direct kernel, and r1/r2 also duplicated candidate lookup on the production path. That comparison did not isolate storage layout. A temporary mirrored geometry cache added membership/synchronization cost and was removed. The final r4 probe retains the same caller work, runtime filters, kernel and complete-copy authority for the alternatives. The initial claim that columns required production adoption is withdrawn. Historical failed probe sources were not fully archived; their raw measurements are retained as development diagnostics, not reproducible qualification evidence.

Deviations from the original exact-port request are covered by the approved typed rewrite and recorded repairs:

1. Function-by-function generated dynamic state is replaced by typed modules and a native controller API. The legacy exact translator remains available with `build.py --engine legacy`; the complete typed target is `build.py --engine native`.
2. Whole-fight bit equality is relaxed. Native standard math and explicit typed operations can differ in last bits; chaotic fights and branch ranking can diverge. Physical/algorithm contracts, deterministic execution and complete coverage replace whole-fight equality as engineering gates. A fresh one-tick diagnostic of request 620 retains the source `hunt` versus native `skirmish` mind choice in [mind_first_tick](native_coverage_r1/mind_first_tick/). It is an observed policy divergence, not evidence of a superior policy.
3. Radius-derived blocker/projectile padding and separation reach, collision-free cells and the sandbox null artillery queue repair inherited defects. Native reclamation retains launched attack/effect sources through completion, preserving their source lifetime.
4. Zero authored cooldown terminal-rate scoring uses a declared finite 1-second fallback rather than producing infinity. The finishing shortlist is game-only and retains all seven closing plans, including rush. These choices are covered by focused contracts; balance implications are separate from engineering completion.
5. DOM/global export glue, double-bit trace strings, exact free-form UI event prose and optional browser AAR presentation objects are excluded. Typed events, observations, commands, search records, source-derived catalog constants and public ability APIs remain.
6. JSON input has explicit finite quantity/count/horizon limits and rejects unsupported malformed input rather than truncating work. Qualification applies to the retained fixtures and this compiler/machine; it does not cover all Cartesian combinations or architectures.

Recheck findings were repaired in batches: ADL summary-name collision, implicit return after namespaced contract inclusion, omitted rush finishing candidate, manual ability policy, process leakage before invalid request encoding, actual shortlist-inference instrumentation, misleading layout dispatch and stale status prose. Test/evaluator/binary/source identities are bound in the final qualification receipt. Subsequent source changes invalidate this qualification and the comparison cache.

The original mechanical baseline report follows for historical context only. Its NOT_READY statements and exact-parity claims apply to commit `797ced26`, not this typed build. Its committed raw evidence is unchanged.

---

NOT_READY

The native C++ simulation matches the frozen JavaScript on the complete check
set, but it fails the purpose of making fights faster. On the prescribed fifty
fights it is **4.99 times slower by wall time** and **3.98 times slower by user
CPU time**. This is a behaviorally checked baseline for review, not a qualified
replacement for the experiment runner. Claude's cross-family review is pending.

The simulation, brains, skills, abilities, projectile physics, forks, network
shortlist, artillery rollout, tables and combo API are implemented. No simulation
function was skipped. The browser/CommonJS export shim and enclosing root-binding
wrapper were replaced by the native header and CLI. There is no JS engine or JS
subprocess in the executable. The frozen snapshot, its network and the Astelia
repository were not modified. No milestone status or scientific claim changes.

The authoritative final receipt is [checks_r2/checks.json](checks_r2/checks.json).

| Check | Result |
|---|---|
| Source hashes | Both match the request; hashes are in README and the receipt |
| Math, RNG, conversions, decimal formatting, Unicode contracts | 545 identical |
| Fight outcomes, compared field by field | 623 / 623 identical; zero differences |
| Completed fights within that count | 525 |
| Matching error outcomes within that count | 98, all the documented null-`coming` artillery crash |
| Per-step unit state | 20 / 20 traces identical; 11,465 snapshots including initial states |
| Permanent reference gate | 80 outcomes identical; prints `identical`; 65 completed, 15 matching errors |
| Native determinism | Two runs of the same 80 requests produce byte-identical output |
| Array batch input | 4 requests identical to JS and stored references, from `/private/tmp` |
| Fifty timed fights | All 50 complete; JS and C++ results identical |
| Repository suite, run once after implementation | 579 passed in 174.36 seconds; measured process time 174.65 seconds |

The trace comparison includes every unit's x, y, hp, cd, target id and alive flag,
plus identity, team, role and kind. Position, health, cooldown and clock values
also carry their exact double bit patterns. Dead units remain in the traces.
The saved trace files were checked against their recorded hashes and frame counts.
This is unit-state equivalence, not a claim that every internal world field was
recorded on all twenty fights.

The first 380 requests cover every pool opponent, both placements and seeds 1–10.
Levels, rules and abilities rotate across those requests. The remaining probes
cover each distinct skill def/alt/explicit/level value on novice, disabled and
elite opponent skills with/without rollout, other brains/scenarios, shapes,
coordinated fire, combos, mind, custom kinds and carried armies. The set is
balanced, not a full Cartesian product. Elite/skill probes use eight units per
side in a 650px arena. Two extra elite fights use full armies for twelve seconds.
The twenty detailed traces use game rules; default rules are covered by the
summary comparisons. All fifty timing fights use the default full army size.
Selections were fixed before measurement in `check_selection.json`.

| Fifty fights, one process per implementation | JavaScript | C++ |
|---|---:|---:|
| Wall seconds | 31.621009 | 157.854219 |
| Wall seconds per fight | 0.632420 | 3.157084 |
| User CPU seconds | 30.283621 | 120.677209 |
| System CPU seconds | 0.270772 | 0.519808 |
| Load average before, 1 / 5 / 15 minutes | 66.87 / 76.70 / 71.13 | 48.91 / 71.32 / 69.37 |
| Load average after, 1 / 5 / 15 minutes | 48.91 / 71.32 / 69.37 | 45.11 / 59.87 / 64.91 |

Reported speed-up, JS wall time divided by C++ wall time: **0.200318x**.
The machine was an Apple M1 Pro, ten CPU cores, 32 GiB RAM, macOS arm64.
The load was high and changing, so this is not a quiet-machine performance
estimate. Nevertheless, the nearly fourfold user CPU cost independently shows
that this implementation did not obtain the intended speed improvement.
The processes run serially and each fight is single-threaded. Timing includes
startup, network loading, JSON IO and memory reclamation. There were no repeated
timing trials. Full verification took 2,023.97 seconds.

Node was v24.18.0 with V8 13.6.233.17-node.50. The compiler was Apple clang
21.0.0, C++17, `-O2`, `-fno-fast-math`, `-fwrapv`. Simulation/host arithmetic uses
`-ffp-contract=off`; the vendored V8 math uses `-ffp-contract=on` to match this
Node build. Compiler commands and binary identity are retained in
[checks_r2/build.json](checks_r2/build.json). Behavior on other compilers,
architectures or Node/V8 versions is not qualified by this run.

Deviations and their reasons:

1. **Mechanical translation instead of a hand-written typed port.**
   `generate.cjs` translates the pinned AST into native C++. It emits 159 named
   top-level functions in the original order with JS line references; anonymous
   functions and object methods become native lambdas at their expression sites.
   This preserved the source's dynamic/default/evaluation semantics, but it
   introduced a dynamic-value compatibility layer and did not deliver the
   requested speed benefit. Its maintainability and future policy API need review.
2. **Table initializers are collected in `initialize()`.** They retain their
   runtime initializer order, but physically follow the function definitions,
   instead of appearing first in the C++ file as requested.
3. **Native representation work accompanies the translation.** Heap ownership,
   frame-boundary collection, cached offsets for common properties, and borrowed
   call arguments replace JS runtime mechanisms. These preserve game algorithms
   and operation order; they are additional implementation machinery a reviewer
   must inspect. This is a narrow source-specific value layer, not a general
   ECMAScript engine.
4. **Math contraction differs by translation unit.** A diagnostic found that
   disabling contraction in V8's math changed `sin(9π/8)` by one bit and diverged
   an elite fight. Matching this Node's build required contraction on for that
   math file alone. Vendor algorithm bodies and license notices are retained.
5. **Coverage uses compact elite/skill probes and balanced factors.** This bounds
   verification cost while including all requested categories; it does not prove
   equivalence for every combination, seed, duration or army size. Full-army elite
   callers are supplemented by the two twelve-second fights.
6. **Identical trace bodies are stored once.** Compressed canonical JS traces are
   retained with separately computed, equal C++ hashes. The final run stores both
   summaries for every fight. A differing trace would retain both bodies. This
   avoids duplicating identical large trace files.

Development failures were fixed before the final batch. An initial short elite
diagnostic exposed the math-contraction issue; its unchanged outputs are retained
in [diagnostic_r0/](diagnostic_r0/). The first full batch then matched
200 outcomes before the flank path reached an unimplemented `Map.entries()`;
[checks_r1/checks.json](checks_r1/checks.json) and its raw outputs preserve that
failed run. The complete repair batch also finished decimal-formatting and
UTF-16/JSON handling before the final run. No resistant mismatch was worked around,
no game rule was changed, and failed receipts were not overwritten.

A one-second diagnostic sample during a full-army elite fight, before the speed
measurement, is retained as [checks_r2/native_profile.txt](checks_r2/native_profile.txt).
It shows substantial time in dynamic operator/method dispatch, string comparison,
property hashing and allocation. It is evidence of overhead, not a comprehensive
profile. The next performance work should remove that machinery from hot numeric
and unit-state paths while retaining these fixtures and the smaller reference
gate. The requested gameplay improvements remain separate behavior changes.

The raw final outcomes, math results, twenty traces, reference/determinism outputs,
timing inputs/results, batch outputs, compiler record and pytest log are retained.
The frozen 80-fight reference and `check_reference.py` provide the routine gate;
a successful routine check does not require repeating all 623 fights.

The speed goal remains unmet. S1b is not accepted and no experiment has used this
port. Independent Claude review and performance repair remain before promoting
it as the faster simulator.
