READY

S2 engineering implementation, 2026-10-05, under decision 0028 and the approval recorded in [S2_PLUG_REQUEST_CODEX.md](S2_PLUG_REQUEST_CODEX.md). Ready for Claude's independent review; this is not acceptance of an AI controller, an experiment, or a milestone. Only `passthrough`, `nearest`, and `hold` are registered. No tuning or AI experiment was performed.

## Acceptance results

All seven requested checks passed on the same typed C++ build. The bound receipt is [s2_plug_r2/S2_RECEIPT.json](s2_plug_r2/S2_RECEIPT.json), SHA256 `1ae077ba28cdf5e9b13adc8d097457640846cd9defc15d5945b4ce782a13bb29`. Tested binary SHA256: `afae380adca8c5046624e760d123affdf01c0a749202fc24b29c9379a261148e`.

| Check | Result and evidence |
|---|---|
| Exact plumbing | **228/228 full fights match byte for byte**, summaries and complete traces, including debug and pre-action decision traces. 114 with the controller on side 0, 114 on side 1: 19 pool opponents × novice/regular/elite-fast × both field orientations × both controller sides. Each fight uses game rules, full default armies and a 20-second limit. 137,028 initial/step frames per arm. See `plumbing.requests.json`, `plumbing.results.json`, and receipt output mappings. |
| Other side untouched | **38/38** first-tick decision lists on side 1 equal the built-in run with nearest on side 0: every pool opponent, both field orientations. The trace is captured after decisions and before movement/attacks; it includes shuffled order, target, goal, movement flags, release relation and in-range state. See `other_side.results.json` and the mapped first-tick streams. |
| Observation fence | The standalone controller header cannot name `World`; the negative compilation fails and the positive control compiles. Static member checks and complete aggregate structured bindings enforce the field counts. Runtime output matches the exact four world quantities and eighteen unit fields. See `fence_negative.stderr.txt` and `controller_contract.stdout.txt`. The view owns copied values, contains only living units, and has no shots, shells, pack/plan state, world/unit pointers or engine RNG. |
| Validation | Contract checks cover NaN and both infinities in each movement field, out-of-field goals, multiplier/stop clamping, dead targets, own-team targets, missing IDs, and stale IDs after slot reuse. Also checks snapshot ownership, damage on both teams, counter reset on reuse, role-based release, guard reflex, callback order, and branch state/RNG isolation. |
| Cost | **0.8327579172**, below the **1.2** cap. Uses the qualification's 50 `basic50` request contexts, replacing only the player profile with built-in alone or nearest. Fresh processes in built-in/nearest/nearest/built-in order, the existing `benchmark.measure` validator, startup/JSON/full execution included, zero cache hits. Mean elapsed per fight: built-in **39.184 ms**, nearest **32.631 ms**. Raw outputs and wall/CPU/load/work counters retained. |
| Existing behavior | **171 passed in 214.80 s**: all existing 158 checks plus 13 new S2 checks. **80/80** no-controller reference requests produce byte-identical stdout to the archived admitted binary `679a06557424b6e5b85177ae0bb7a50de8e81fa71077db494b27e957a8a597e1`. The admitted archive's stored/decompressed identities are checked before execution. No JS/C++ score comparison is made. |
| Determinism | **114/114** nearest outputs match repeated runs byte for byte. Every request executes in a fresh host; repeats run in reversed request order. |

The controller contracts also pass combined AddressSanitizer/UndefinedBehaviorSanitizer with empty stderr; instrumented build and execution took 30.11 seconds. These checks concern the changed controller path, not a repeat of the historical whole-engine sanitizer qualification.

Cost is the requested end-to-end comparison, not an isolated adapter overhead measurement. Outcomes change the executed work: each built-in sample has 30,000 outer steps and 2,798,891 unit actions; each nearest sample has 29,910 steps and 2,670,672 unit actions. Per-fight time does not establish tactical quality or equal-work computational cost.

## Implementation

The controller-facing API is `astelia::control::Observation`, `ObservedUnit`, `UnitDecision`, and `Controller` in `src/native/controller.h`. Its only dependencies are scalar/container types and the owned RNG implementation. `prepare` runs once per tick per controlled side after the unchanged kind reflexes, before any unit decision. `decide` runs at the existing shuffled unit decision point. All units on that side use the same const snapshot.

The JSON profile works on either side:

```json
{"mode":"alone","options":{"seed":7,"scenario":"mirror","rules":"game","ai":[{"controller":"nearest","params":{}},{}]}}
```

`nearest` chooses the closest enemy by center distance, walks at full speed to 90% of the weapon's range, and sets that enemy as target. Range is a surface gap for melee/direct weapons and center distance for artillery, matching the game's range convention. `hold` returns its observed position, zero speed and no target. Neither receives the world. Their registry is closed to the three authorized names; nonempty params are rejected because S2 authorizes no tunable parameters.

For real external controllers the engine disables the side's pack, which gates lookahead, director, commander, formation, artillery planning/volley and coordinated abilities. It forces only that side's ability policy to the unchanged game's Auto implementation, even if an inherited profile requested Off or Coordinated. It leaves the other side's configuration and decision caller unchanged. Downstream wind-up/release, energy, cooldown, aim, projectile/damage and kind dash/block code are unchanged.

Invalid numeric decisions fail closed to hold/no target; finite goals are clipped to `[0,width] × [0,height]`, multiplier to `[0,1]`, and stop distance to at least zero. Target IDs resolve to current generation-checked handles only if the unit is living and an enemy. Public IDs are monotonically allocated and never reused. The engine computes release relation and in-range state from the role and body. A current block guard holds movement and release, as in the built-in decision path.

Cumulative `damageDealt` and `damageTaken` count actual HP removed, after protection/block/shield and capped by remaining HP, for both teams. They include friendly damage when the game's rules produce it. These new counters do not replace the historical side-0 `dealt` telemetry. They reset with a new unit, survive branch copies, and contain no averaging or time constant. Controllers compute recent averages themselves. Native hunter roles map to melee, archer/player roles to ranged, preserving the specified three-role view.

Worlds own the controllers. A branch clones controller state and RNG and clears its observation scratch storage; it cannot mutate its parent. An instrumented hold spy exists only inside the contract executable to test callback ordering and clone isolation; it is not a registered controller or combat arm.

## Deviations and reasons

1. **Privileged passthrough preserves pack planning and the complete built-in internal decision.** Skipping planning cannot reproduce the regular/elite-fast brains. Reapplying the narrow external decision would discard private move/release flags and early-return behavior. The explicitly test-only adapter therefore calls `decideUnit` at the same shuffled position and leaves its full result untouched. Only this adapter can see `World`; nearest and hold use the validated narrow bridge and skip all planning. This exception proves plumbing/order parity, not that a restricted observation can reproduce every built-in brain.
2. **The observation has its own namespace.** The existing engine already has `astelia::Observation` for the formation director. `astelia::control::Observation` preserves that public API and keeps the new view independent of engine headers. The initial `s2_plug_r1` batch stopped at this name collision during compilation, before any tests or fights; its failure logs remain unchanged. After fixing the name, one completed change batch ran in `s2_plug_r2`; successful tests and fights were not rerun after documentation or packaging.
3. **Explicit policy for unspecified invalid-number handling.** The request requires validation without choosing an invalid-number fallback. Hold/no target avoids allowing non-finite values into physics. Invalid targets alone become none without discarding valid movement.
4. **Broader engineering coverage.** The request's minimum of 40 fights per controller side is exceeded by the complete 114-per-side grid. The plan's additional 114-nearest-fight check is also retained. These are simulator engineering checks on fixed engineering seeds, not an AI experiment or recorded scientific panel.
5. **Lossless output packaging.** Large full traces are stored as content-addressed XZ archives, deduplicating identical raw streams. Every logical capture retains its own raw SHA256 and maps to the stored archive. Packing checks decoded byte identity and changes no result, trace, timing, or verdict. The original pre-pack receipt is retained for provenance; read current archive locations from `S2_RECEIPT.json`.

The historical JS equivalence study is not rerun: S2 supplies intentionally different decisions for external profiles, and the requested admitted-C++ regression gate proves sampled no-controller behavior unchanged. Historical qualification/review receipts and source archives remain intact. Scientific claims, later controller sessions and acceptance remain separate.

## Changed files and reproduction

All changes are under `evidence/tactical_composition_demo/astelia_cpp/`:

- New controller API/implementations: `src/native/controller.h`, `controller.cpp`, `controller_bridge.h`, `controller_bridge.cpp`.
- Engine wiring/counters/host diagnostics: `src/native/config.h`, `config_codec.cpp`, `world.h`, `world.cpp`, `types.h`, `combat.cpp`, `host.cpp`.
- Build/test/evidence tools: `build.py`, `native_controller_contract.cpp`, `test_native_controller.py`, `verify_s2.py`, `pack_s2.py`.
- Documentation: this report and the S2 note in `README.md`.
- New engineering evidence: `s2_plug_r1/` (failed compilation only) and `s2_plug_r2/` (completed checks, requests, raw outputs, identities, test/compiler/sanitizer logs).

Build the current host with `python3 evidence/tactical_composition_demo/astelia_cpp/build.py --engine native`. The complete verification command is `verify_s2.py --output <fresh-directory>`; it refuses existing evidence. It runs the test batch once, controller sanitizer contracts, admitted-build regression, plumbing grid, untouched-side check, nearest completion/repeats, then uncached timing. Do not repeat the successful batch just to inspect evidence.

To verify stored outputs without running combat:

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/pack_s2.py evidence/tactical_composition_demo/astelia_cpp/s2_plug_r2 --check
```

An archive is ordinary XZ: `lzma.decompress(path.read_bytes())` returns the exact captured UTF-8 stdout. `plumbing.results.json` identifies which logical baseline/passthrough streams to compare. Receipt identity sections pin binary/source/test/harness/compiler manifests; timings pin executed fights/steps and zero cache hits.
