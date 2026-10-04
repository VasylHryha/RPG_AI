# Typed combat development checkpoint

This is engineering validation under the approved performance rework, not an
AI experiment or full-engine qualification. It extends the typed core with
game casts/energy, per-kind stats, mitigation, dash/block, aimed/homing shots,
piercing and friendly fire, lobs, burn, sandbox abilities, the player bot,
carried/custom/asymmetric armies, hunter respawns and skirmish arrivals.

49 focused tests passed in 26.96 seconds. The separate address/undefined
behavior sanitizer run of the combat contracts passed without diagnostics.
Commands and elapsed times are in the corresponding receipts.

13 fresh, five-second fights were run in each engine. All 13 summaries were
identical. Three traces were exactly equal; the other ten first differ by a
last-bit coordinate value. `trace_comparison.json` records each first difference,
and the compressed raw traces preserve both engines' output. These short fights
do not establish coverage of all combat paths or the full check set.

Formation/commander/director brains, full skill support, look-ahead/network and
artillery planning/rollout remain pending and are rejected at the input boundary.
No new performance claim is made for this checkpoint. The data layout remains
provisional until full production-kernel and clone-cost measurements.
