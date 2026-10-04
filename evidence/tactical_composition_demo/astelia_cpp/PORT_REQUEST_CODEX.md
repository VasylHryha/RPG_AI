# Request to Codex: port the Astelia formation sandbox from JavaScript to C++ (exact behaviour)

Repository: `/Users/new/RiderProjects/ai_RPG_test`. Read `AGENTS.md` first. This is exploratory work under decision 0028 (`docs/decisions/0028-owner-directed-exploratory-composable-shapes.md`), not a milestone.
The owner chose C++ and assigned the port to Codex (2026-10-04). Plan: `evidence/tactical_composition_demo/PLAN_RESONATOR_AI.md` (session S1b).
Commit with the trailer `Assisted-by: Codex:<model>`.

## Why

Our AI experiments play tens of thousands of fights in this game. JS costs about 2.9 ms per step, about 0.5-1 s per fight on a quiet machine. A faithful C++ port makes every later run faster.
After this port, the AI plug and our controllers are written once, in C++.

## Source (do not modify)

- `evidence/tactical_composition_demo/astelia_snapshot/formation_sim.js`, sha256 `85b16e9b84b42b831dd2e64a7055474b6df902e4c1ffd635e6670fc6fb665733`, 3,376 lines.
- `bc_net.json`, sha256 `d11e9a2da43cb0eb5b8b9539be4ab5834e750b4148121d56e632c75d7fb2e3e5`.
- Provenance: `astelia_snapshot/SOURCE.md`. Never touch the Astelia repository itself.

## Scope

Port the whole simulation: `create`, `step`, `done`, `summary`, `run`, every brain, skill, level (`LEVELS`), preset, plan, the opponent pool (`POOL`, `enemyOf`), abilities, shots and shells,
the `game` and default rule sets, `fork` and look-ahead (including the `bc_net` shortlist), and `artyRollout`. The opponent ladder uses elite-fast, which needs look-ahead and the rollout.
Not needed: browser/HTML code and any function only the HTML uses (list what you skipped and why).

Put it in `evidence/tactical_composition_demo/astelia_cpp/`:
- `src/`;
- `build.py`: clang++ or g++, `-O2`, C++17 or later, no external dependencies; never `-ffast-math`;
- a command-line host: JSON lines in (one fight per line, the same fields the JS `run` takes: mode, options with `seed`, `scenario`, `duration`, `abilities`, `swapSides`, `rules`, the `enemyOf(...)` fields and `ai: [profile, profile]`) and JSON lines out, with exactly the fields of JS `summary()`. Also a batch mode for many fights per process.

## The hard requirement: the same fight, bit for bit

The fights are chaotic, so one last-bit difference early changes the outcome. Target: for every fight in the check set, the C++ `summary()` equals the JS one **exactly**, and the
full state (every unit's x, y, hp, cd, target, alive) is equal at every step on a sample of fights. Traps to handle explicitly:

1. **Transcendental math.** The source uses `Math.sin` (15), `Math.cos` (16), `Math.atan2` (11) and `Math.hypot` (1). V8 implements sin, cos and atan2 with its own fdlibm port
   (`src/base/ieee754.cc`), and `Math.hypot` with its own scaling algorithm. The platform libm can differ in the last bit. Port those exact implementations (check their licence and keep the notice), or prove the
   platform functions agree on every call made in the check set. `sqrt`, `floor`, `ceil`, `abs`, `min` and `max` are exact in both. **Verify this list yourself; do not rely on it.**
2. **`Math.round`** rounds .5 toward +infinity (`Math.round(-2.5) = -2`). C `round` does not.
3. **Integer operators on doubles:** `>>>`, `|0`, `^` and `<<` are ToInt32/ToUint32 of a double. The RNG (`rng`, line 597) and the seeds (lines 95, 541, 713, 744) depend on them.
4. **Iteration order.**
   - `Map` and `Set` iterate in insertion order.
   - Plain-object keys iterate with integer-like keys first (ascending), then the others in insertion order.
   - `Object.keys`, `Object.entries` and `for...in` over profiles, skills and plans must keep that order.
5. **Sorting.** `Array.prototype.sort` is stable in V8. Use `std::stable_sort` with the same comparator, including the numeric-comparator sign semantics and NaN.
6. **Evaluation order.** Expressions with side effects, and floating-point sums, must be evaluated in the same order. Do not reassociate.
7. **`undefined`/`null` and defaults:** `||` and `??` default chains, and `JSON.stringify` comparisons where the source uses them.
8. **The known crash** (`SOURCE.md`): `artilleryVolley` reads `coming.length` with `coming` null under the default (non-`game`) rules. Reproduce it as an error result with the same message. Do not fix it in the port: the fix is a separate, recorded change to both versions.

## Checks (all must pass; commit their outputs)

1. **Exact equivalence:**
   - at least 400 fights compared field by field with the JS: every `POOL` opponent; both sides; seeds 1-10; rules `game` and default; abilities on and off;
   - our side's profiles: every `LEVELS` entry (including elite-fast with look-ahead), `{brain:'alone'}` and `{level:'novice'}` with each `SKILLS` key set to each value in its `def`/`alt`/level values one at a time;
   - opponents with no skills, and with elite skills with and without `artyRollout`.

   Report the count that is identical. **Any mismatch is a failure:** find its first differing step and fix it.
2. **Step trace:** on 20 of those fights, the full unit state after every step is equal.
3. **Speed:** single-thread time per fight, JS against C++, on the same 50 fights, measured on the same machine. Report the machine load during the measurement.
4. **A determinism test:** two runs of the C++ host give identical output.
5. A `README.md` stating the source hashes, what was skipped, the check results, and how to run.

## Report

When done, write `evidence/tactical_composition_demo/astelia_cpp/PORT_REPORT.md`:
- the first line is `READY` or `NOT_READY`;
- the check numbers;
- the speed-up;
- every deviation from this request, with its reason.

Claude will then review the port (cross-family) before any experiment uses it. Estimated effort: about 6-10 hours, most of it in the equivalence checks.
