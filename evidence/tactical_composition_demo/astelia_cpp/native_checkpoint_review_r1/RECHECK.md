CHANGES_REQUIRED
Reviewer family: Codex
Review type: implementer adversarial self-review; not independent acceptance
Reviewed HEAD: 797ced26ff95caa5f84ea71e9bb247422068b5c5 with uncommitted engineering changes
Evidence: native_checkpoint_r1/core_slice_timing/benchmark.json and native_checkpoint_review_r1/counterexamples.json

The typed direction is promising, but the first checkpoint did not establish an
optimal layout or complete core correctness. The 15.6309x number is a historical,
contended, eight-fight novice diagnostic. Its uncached execution, matching
summaries, and matching unit/projectile counts withstand this recheck. It does
not qualify current repaired sources or any missing feature.

## Findings and repair batch

1. **High: accepted numeric inputs produce invalid hidden state or output.**
   `combat.cpp` multiplied displacement by `1/dt`; at `dt=1e-310` zero movement
   becomes `0 * infinity`. The bounded probe found invalid velocities in all
   four units. At `dt=duration=1e308`, the host returned `aliveSeconds:null`.
   Finite inputs alone do not ensure finite intermediates/aggregates. Repair:
   direct velocity division, checked time advance, explicit aggregate-overflow
   errors. Add subnormal-motion and host-overflow regressions.

2. **High: spawn/movement are not integrated with spatial membership.**
   `World::add` appended slots without updating an already built live grid.
   A blocker added between existing endpoints was omitted; moving the new slot
   threw. Moving a freshly created unit before its first step also threw, after
   mutating position. Repair: indexed insertion/removal, generation-slot reuse
   checks, initial/lazy grid construction, and a live-grid spawn/death stress
   test. Team indexes still have an explicit rebuild boundary; complete spawning
   integration must preserve that boundary in stage C.

3. **High: timing admission accepts unfinished fights and fake counter types.**
   A host returned `t=0`, two surviving sides and no deaths for a 20-second mirror
   fight, reporting booleans as fight/step counts. `measure` accepted it.
   Repair: necessary observable termination checks, supported time limits,
   exact integer counter types and consistency between outer counts and final
   times. This is still not sufficient mechanics proof: full traces, population
   accounting and scenario-specific hidden spawn state remain stage-F gates.

4. **High: historical cache import does not bind the chosen JS host.**
   A different JS host imported 643 canonical historical records and returned a
   cache hit that differed from its own fresh execution. Snapshot/runtime-version
   checks do not identify a wrapper. Repair: allow historical imports only for
   the canonical host command, with stable input identities.

5. **High: source drift is detected after its result has already been cached.**
   A host changed its own source during a fight. `fight()` cached the result;
   only `close()` rejected the session. Repair: recheck input stats after the
   response and before cache insertion, including cache-hit return. Add a
   source-changing host negative control that requires no entry to remain.

6. **Medium: the layout probe does not justify the architecture choice.**
   Every opposing pair in its initial world is outside attack reach: our x is
   at most 300, theirs at least 1100, versus maximum range plus radii below 350.
   Its HP-hit branch never runs. It does not implement production nearest-target
   selection, movement or projectile queries; the column variant omits most
   unit state, and only records receive a complete copy benchmark. The 4%
   geometry difference cannot establish the best complete layout. Retain typed
   records provisionally. Before freezing the full layout, compare closing and
   engaged states, production kernels and equivalent complete branch schemas.
   This remains open; do not promote the old probe into a layout acceptance.

7. **Medium: isolation checks omit active effects and much mutable state.**
   The first branches start in early, non-contact ticks. The snapshot omits most
   unit state, shells, fields, dots, hit sets and statistics. The geometry suite
   checks blockers/separation, not the shot path. Repair batch adds nonempty
   nested-effect/reused-buffer checks, 128 independent shot-scan cases and the
   radius-16 shot-cell boundary. Full player/ability/pack/spawn clone state must
   still be covered when implemented.

8. **Medium: build and benchmark identities have holes.**
   Object fingerprints did not include compiler executable bytes or verify
   reused object contents. Same-version compiler replacement and changed
   object bytes could inherit a stamp. Repair: compiler-byte fingerprints,
   object checksums, and checks across linking. Timing receipts omitted
   `benchmark.py`, its engineering contract and the supplied input file identity.
   Repair: bind and recheck those harness inputs and enforce the frozen workload
   hash. Supplemental timing admission must also require positive native search,
   inference and artillery-rollout work rather than just named groups.

## Remaining gates

The full engine is deliberately incomplete: game casting/energy/player effects,
abilities, kinds/spawning, formations/skills/combos, network inference, look-ahead
and artillery rollouts are pending. The fork pool has no aggregate telemetry or
branch-local option overrides yet. The native host explicitly rejects those
features, which prevents an accidental simplified-engine qualification.

Persistent comparison reads still lack a request timeout and can deadlock if a
host fills its stderr pipe before writing a result. Fix this before the long
coverage batch. Load-aware final qualification, complete correctness/work-audit
receipts, matched-state probes, and a cross-family review before experiment use
remain required. No independent reviewer or external system is needed to finish
the authorized migration, implementation checks and performance work here.

The original code/build inputs and compressed executable for the eight-fight
diagnostic are preserved in `native_checkpoint_r1/source_archive/`; every
archived source hash matches that receipt's manifest. Historical receipts remain
unchanged. The counterexamples are bounded engineering controls, not scientific
panels. Do not rerun `reproduce.py` on repaired sources and expect the original
acceptance bugs: its recorded harness/native identities describe the old code.

Repair batch validation: **39 focused tests passed in 25.70 seconds**, followed
by a successful address/undefined-behavior sanitizer contract run with no
diagnostics. See `repair_tests_receipt.json` and `repair_sanitizer_receipt.json`.
These checks cover the repaired core/admission paths, not the full engine.
The layout finding, complete feature migration, request-timeout/stderr handling,
and final qualification remain open. Continue stages C–F under the owner's
existing authorization; no additional approval is needed for that work.
