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
