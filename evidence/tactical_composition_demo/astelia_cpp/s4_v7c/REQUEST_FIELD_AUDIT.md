# Validation request argument audit

The unchanged combat binary has no successful parse-only operation. In `src/native/s4_v7_host.cpp`, valid combat input calls `configuration`, then `World::create` and increments `executed_fights`. `--catalog`, RNG and contract operations do not validate combat requests. A zero-duration fight would still construct a world and count a fight, so it is not used.

The separate `request_check.cpp` calls the exact native configuration codec and registry constructors, plus the scalar guard from `World::create`. It never constructs a world or calls prepare, decide or coreStep. `native_build.py` copies the combat executable unchanged, compiles the original registry/controller sources into this separate checker, and verifies every reused engine object against the combat build manifest. The actual codec object is the manifest-pinned `observer_v1_observer_v1_config_codec.o`, not the older codec lacking `killerTelemetry`. The checker records zero worlds, fights and steps for every request. `REQUEST_AUDIT.json` binds all 400 requests, covering ten arm/head combinations and both orientations (20 templates), all fresh seeds and both parameter vectors. This is additional parser proof, not a claimed dry run of the combat executable.

Exactly one field differs from v7b's built validation request: `trace` becomes true. `attributionDiagnostics`, `decisionDiagnostics`, `decisionTrace` and `killerTelemetry` remain true. The attribution constraint requires both trace and decisionDiagnostics; decisionDiagnostics separately requires trace. Keeping attribution output preserves the delivered diagnostic stream, and trace also satisfies the independent decisionDiagnostics constraint. This changes output flags only. The unit test reconstructs v7b's builder from its function AST and checks that trace is the sole difference for every arm/head/orientation. Original template JSON files remain byte-identical.

| Present field | Native validation and fixed value |
|---|---|
| request object and keys | `observer_v1_config_codec.cpp`, `only(request, ...)`; no operation or unsupported keys |
| mode, opponent | `alone`; mode passes `brain`; opponent is a supported mirror fallback, superseded by the explicit head profile |
| trace, debug | boolean true / false; host uses truth values, codec validates trace through diagnostic constraints |
| s3, diagnostics, endCounts | codec booleans: true / false / true |
| killerTelemetry | codec boolean true; observer provides units, launches and damage |
| decisionTrace | codec boolean true; allowed with trace or killerTelemetry |
| decisionDiagnostics, attributionDiagnostics | codec booleans true; both trace constraints satisfied |
| options object and keys | `only(o, ...)`; fixed inherited key set, no unsupported options |
| seed | finite JSON integer in [0xC0000000, 0xffffffff]; native number and uint32 RNG conversion; fresh ledger allocation checked independently |
| rules, scenario | supported enums `game`, `mirror`; default game bodies and mirror allocation |
| sandboxAbilities, perception | codec booleans false / false; no experimental body/perception overrides |
| duration, dt | finite native numbers 150 and 1/30; positive dt, nonnegative duration, duration/dt = 4500 < 1e7 |
| swapSides | boolean, constructed from orientation 0 or 1 |
| army | closed object, counts 10 melee / 30 ranged / 10 artillery; integer counts within [0,1e6] |
| ai | array length 2; codec permits at most two profiles |
| ai[0] keys | closed controller/params/skeleton object |
| ai[0].controller, skeleton | five supported v7 arms, skeleton `v7`; `s4_v7_dispatch.cpp` constructs the correct controller; omega0 overrides only omega_ranged internally |
| ai[0].params | finite native object of exactly 11 inherited knobs; v6 admits mu in [-2,2], rejects omega_melee; s3 admits the other ten names/bounds under v5; both committed theta vectors pass constructors |
| ai[1] | closed profile with supported `regular` or `novice` level; neither enables lookahead or artillery rollouts |
| omitted world dimensions and bodies | unchanged game defaults width 1400 / height 800, default brute/spitter/shaman definitions; no custom unitSet, skirmish, player, enemyArmy or role overrides |
| omitted skills/formations/search | native level defaults; regular's valid line preset and novice's empty formation; no user skill/formation/network/lookahead fields to reject |

The scalar world guard is also checked without constructing a world. Default game body validity, supported three-role placement and the 50-unit identity capacity are inherited from the exact binary and its observation fixture. Dynamic controller/numerical failures remain possible during actual combat and are fail-closed; this audit proves argument admissibility, not fight outcomes. Native negative fixtures reject unknown fields, invalid enums, bad numeric/boolean/count values, unknown controller/skeleton/parameter names and out-of-bound parameters, including the two original flag constraints.
