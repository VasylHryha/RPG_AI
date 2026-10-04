# Astelia formation simulation in C++

Session S1b of `../PLAN_RESONATOR_AI.md`, exploratory work under decision 0028.
Current qualification: **NOT_READY**. The owner approved revision 2 of the
[native architecture and performance plan](PERFORMANCE_REWORK_PLAN.md), and
implementation is in progress. The first typed novice core passed
[bounded checkpoint checks](native_checkpoint_r1/README.md): 28 focused checks,
address/undefined-behavior instrumentation, independent geometry oracles and
fork/lifetime checks. Eight full-army novice fights on that build measured **15.631x** faster
than uncached JS, with identical summaries and audited work counts. This is a
limited core diagnostic on a busy machine, **not full-engine qualification**.
An [adversarial recheck](native_checkpoint_review_r1/RECHECK.md) then found numeric,
spawn/index, timing-admission and cache defects plus gaps in the layout/isolation
evidence. The repair batch passed 39 focused tests and sanitizer contracts; that
historical timing cannot qualify the repaired source. Abilities, formations,
other profiles, game rules and branching
AI remain to port.
The original [PORT_REPORT.md](PORT_REPORT.md) applies to commit `797ced26`:
623 matching outcomes and twenty matching traces, but C++ was 4.99 times slower.
The later r9 optimization measured 1.169x elapsed-time speed-up, still below the
owner's 3x minimum. The complete legacy working changes after r9 have not had
fresh full coverage; the new typed core has separate evidence. Those historical
receipts do not qualify the current source. See [PERFORMANCE_RESEARCH.md](PERFORMANCE_RESEARCH.md)
for the research and measured bottlenecks.
The [adversarial self-review](PERFORMANCE_REWORK_REVIEW.md) found missing branch
workloads, inherited grid defects and incomplete benchmark/cache gates. The
The core repairs the radius/grid defects; build/cache admission and benchmark
guards now reject stale binaries, malformed results and incomplete qualification.
Full-engine correctness and work qualification remain pending.
The legacy simulation and its controllers execute in native C++17. Its executable loads
the existing network JSON and accepts one JSON fight per input line. It also
accepts an array of fights on a line for batch operation. Results have the fields
of the frozen JS `summary`; a failed fight returns `{"error":"..."}`.

Build from any directory:

```sh
python3 /Users/new/RiderProjects/ai_RPG_test/evidence/tactical_composition_demo/astelia_cpp/build.py
```

Build the typed development core separately with `build.py --engine native`.
It produces `build/astelia_native`, accepts sandbox mirror fights with two
explicit novice profiles, and returns an explicit error for unsupported features.
It is not a replacement for the full legacy engine yet.

Run from the repository root:

```sh
echo '{"mode":"alone","opponent":"wolfpack","options":{"seed":1,"scenario":"mirror","duration":20,"rules":"game","ai":[{"level":"regular"},{}]}}' | evidence/tactical_composition_demo/astelia_cpp/build/astelia
```

`opponent` is optional convenience syntax for `enemyOf`; fields supplied in
`options` override it. The original `enemy` and `enemyF` fields work directly.
The network path defaults relative to the executable and can be supplied as its
first command-line argument. Each fight independently resolves its options;
mixed rule sets in the same process retain the JS table-switch behavior.

Game rules preserve the original override of `abilities`: the source enables
the sandbox abilities over game rules through `sandboxAbilities:true`. To
exercise those abilities use both flags. This is source behavior.

Append `"trace":true` to a request to emit an initial snapshot and a snapshot
after every step before the final result. Snapshots retain dead units and contain
each unit's identity, role, position, health, cooldown, target id and alive flag.
The `bits` entries encode double values as sixteen hexadecimal digits, including
signed zero. `"debug":true` adds sanitized internal unit, pack and projectile
state for failure diagnosis.

Compare a list of fights, with the first differing step/field reported:

```sh
python3 evidence/tactical_composition_demo/astelia_cpp/compare.py fights.jsonl --trace
```

The strict legacy behavior comparison (the proposed native rewrite will use it
as a diagnostic rather than an exact-match acceptance gate):

```sh
python3 evidence/tactical_composition_demo/astelia_cpp/check_reference.py
```

Check array batch input and mixed rules from a different working directory:

```sh
python3 evidence/tactical_composition_demo/astelia_cpp/check_batch.py --output /private/tmp/astelia-batch-new-check
```

Its 80 frozen requests and JS results are in `reference_fights.jsonl`. Every later
change claiming exact behavior preservation must produce `identical`. The owner
has subsequently allowed a native rewrite without bit-exact JS matching; its
proposed replacement contract is in `PERFORMANCE_REWORK_PLAN.md`. Frozen JS and
committed historical references remain unchanged. A changed native engine cannot
inherit the JS ladder's qualification merely because it uses the same requests.

Comparison commands now cache combat results by engine, network and request
identity. Use `--no-cache` for fresh execution. A changed native executable
invalidates its entries. Timing in `benchmark.py` bypasses the comparison cache
and records real fight/step execution counts; cached speed is never an engine
speed-up measurement. The owner approved bounded engineering execution in the
revised plan. `benchmark.py --group all` now requires every fixed group to clear
3x and a complete engine build; a core/subset run requires `--diagnostic` and
cannot qualify the engine. `work_audit_host.cjs` separately counts lexical JS
branch steps, forks, unit actions and projectile work without changing the frozen
snapshot. Complete work-audit, matched-state and correctness gates remain pending.

Pinned source identities:

| Source | SHA256 |
|---|---|
| `../astelia_snapshot/formation_sim.js` | `85b16e9b84b42b831dd2e64a7055474b6df902e4c1ffd635e6670fc6fb665733` |
| `../astelia_snapshot/bc_net.json` | `d11e9a2da43cb0eb5b8b9539be4ab5834e750b4148121d56e632c75d7fb2e3e5` |

`src/formation_sim.cpp` contains 159 named top-level functions, in their source
order, with JS line references. Anonymous functions and object methods become
native lambdas at their original expression sites. `generate.cjs` performs the
mechanical translation using Node's bundled Acorn; generation is a development
step. The original committed build used `-O2`. The current development build
uses `-O3`, LTO and host CPU tuning; `--portable` omits host-specific CPU tuning.
It requires clang++ or g++ and no external libraries.
`build.py` records its commands and binary identity in
`build/build.json`. No fast-math flag is used.

The compatibility layer supplies the dynamic values the JS state uses, including
missing fields, function closures, insertion-ordered maps and sets, integer-key
object enumeration, stable numeric sorting, ToInt32/ToUint32, decimal formatting,
and UTF-16 string/JSON behavior used by the source. It keeps references within
forks and collects unreachable values at host frame boundaries. The state remains
accessible by the original unit field names for a future native policy adapter.

The vendored V8 13.6.233 `ieee754` math comes from
[V8's source](https://github.com/v8/v8/blob/13.6.233/src/base/ieee754.cc), and is
byte-identical upstream to
[the math shipped by Node 24.18.0](https://github.com/nodejs/node/blob/v24.18.0/deps/v8/src/base/ieee754.cc).
Sun's notice remains at the top of the file and V8's BSD license is retained in
`LICENSE.v8`. Standalone adaptations replace V8's include dependencies, bit casts,
wrapping-integer helpers and export macros. The algorithm bodies are unchanged.
V8's math file uses `-ffp-contract=on` to match this Node build; simulation code
uses `-ffp-contract=off`. The distinction matters at `sin(9π/8)`. The two-argument
V8 `Math.hypot` scaling algorithm is implemented in `src/builtins.h`, with separate
arithmetic operations. `Math.round` preserves ties toward positive infinity.

The source math inventory is: sin 15, cos 16, atan2 11, hypot 1, sqrt 5, floor 32,
ceil 6, abs 17, round 10, min 62, max 55, and PI 23. There are also three binary
squaring expressions (`** 2`). The inventory counts expression sites, not dynamic
calls. No simulation function was skipped. The skipped code is the browser/CommonJS
export shim and its enclosing root-binding wrapper; the native header and host
provide those entry points. All ability API functions and combo examples remain
in the port.

The documented `artilleryVolley` null-`coming` crash is preserved as
`{"error":"Cannot read properties of null (reading 'length')"}`. Matching error
cases are counted separately from completed fights.

The check set in `check_fights.jsonl` has 623 requests. `check_selection.json`
records every label and the trace/reference/timing selections. It covers all 19
pool opponents, both placements, seeds 1–10, both rules, abilities, all five
levels plus alone, and each distinct skill def/alt/explicit/level value on novice.
It adds opponents with disabled skills and elite skills with/without rollout,
hunters and skirmish scenarios, homing shots, all shapes, combo/mind paths, custom
kinds, perception, and carried/asymmetric armies.

Coverage is balanced across factors. It is not their full Cartesian product.
Baseline fights last 20 seconds. Elite and skill probes use 2 melee, 4 ranged and
2 artillery per side in a 650px arena; the other pool probes use the default
50-unit armies. Two additional full-army elite fights last 12 seconds. Timing
uses the same 50 preselected full-army fights in one process per implementation.

Run a fresh complete check batch (the script refuses to overwrite existing raw
fight outputs):

```sh
python3 evidence/tactical_composition_demo/astelia_cpp/verify_port.py --output /private/tmp/astelia-port-new-check
```

The script checks source hashes, compares math/conversion/formatting contracts,
then compares all fights, retains twenty compressed complete traces, writes the
80 references from JS outputs, checks them against C++, compares two native runs
for determinism, and times the same fifty fights serially. The speed receipt
records CPU time and machine load before/after each measurement. Verification
results and qualification status are stated in `PORT_REPORT.md`.

Claude's independent cross-family review is required before any experiment uses
the port. This work does not change milestone status or accept a scientific claim.
