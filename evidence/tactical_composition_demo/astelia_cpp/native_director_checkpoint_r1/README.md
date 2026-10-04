# Typed combo and command checkpoint, development only

The batch passed 96 focused checks: 16 core/combat tests completed on attempt 1; a narrowing conversion in the new test fixture then stopped compilation. After correcting that fixture, the remaining 80 formation/runtime/admission/cache tests passed in 24.93 seconds. Both raw attempts are retained. The final formation contract, including director and order checks, also passed AddressSanitizer/UndefinedBehaviorSanitizer with no stderr diagnostics.

Added both authored combos and observation features, role assignment, phase dwell/timeout/success/abort/cooldown, expiring goals, external goal precedence, and move/attack/hold/retreat orders with completion events. Branch copies own their director, goals and orders. Repaired the skirmish reserve termination and carried-skirmish precedence; ordinary shot releases preserve resolved dead targets rather than silently skipping that source work. Game formation reach/pace medians are cached per tick and membership revision. Persistent comparisons now have bounded request/write/shutdown deadlines and drain stderr to disk, with hostile-host controls.

This is a development checkpoint, not full-engine acceptance or performance qualification. Neural/lookahead and artillery prediction/planning/rollouts remain pending. No scientific panel or AI experiment was run.
