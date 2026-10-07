APPROVE_WITH_NOTES — initial source findings fixed; static go for the single final test batch and bounded diagnostic. Runtime results remain unreviewed.

Reviewer family: Codex (same-family fallback; not cross-family acceptance).
Scope: read-only review of the new observer_v1 native files, build_observer_v1.py, test_observer_v1.py, and s4_gun_assault_20261007/{common,run,analyze}.py. No fights, tests, or project experiments ran in this review. AGENTS.md, PLAN_CURRENT.md track B and DESIGN_0G.md section 19 were read. PLAN_CURRENT.md was not edited, as the owner explicitly forbids it. Disposition belongs alongside this local evidence.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Findings:

1. **Runtime cap is not independently enforced.** In run.py one(), the blocking stdout iterator and stderr read occur before a deadline check; if the child stops writing or stalls, no worker can call deadline.stop(). execute() also exits the ThreadPoolExecutor context before its finally calls deadline.stop(), so projection rejection can wait for queued/running work instead of stopping it immediately. Add an independent deadline watchdog which kills only owned process groups, and call stop before pool shutdown on projection rejection. The loop's checks remain useful but cannot alone establish a hard cap.

2. **Gun-death geometry combines two observation times.** analyze.py uses previous-tick gun/support positions with exact lethal-event source coordinates. The reported killer angle can therefore reflect a different centre than the damage event. Use targetX/targetY for the killed gun centre, and either record supporting positions at the lethal event or explicitly label them as previous-tick measurements. Exact event-time supporting positions also permit exact event-time cover attribution.

3. **Lethal-tick simultaneity is omitted.** Gun-death prekill samples are completed prior-tick frames. Novice analysis ignores exact movement-entry snapshots, so an attacker which enters its legal reach and kills the gun within the next tick can be absent from every prekill reach sample. Keep the prior-three-second tick series, label its sampling, and add a pre-lethal snapshot of living attackers within legal reach and within the gun band, ideally recorded only for enemy-gun deaths. Regular approach concurrency likewise checks surviving posttick units; an approacher entering and dying within that tick can be lost from its same-tick concurrency count. Include exact entry snapshots or qualify the posttick concurrency field and report a separate entry-time count.

4. **Historical fixture claim needs precise scope.** The proposed observer tests compare two no-combat contract outputs, six fixed-request historical-v6/off/on fight cases, and protected historical source/fixture hashes. They do not themselves execute every old fixture suite. Report exactly those checks, or include the required historical fixture tests in the planned single final batch. Do not turn unchanged file hashes into a claim that the complete historical test battery ran.

Positive findings from source inspection:

- World::damage is the central damage path for melee, shots, shells, friendly fire and damage-over-time; its hook records the post-mitigation amount and capped HP dealt, and identifies the source unit responsible for each lethal application.
- The versioned world/combat_rules/abilities copies change only observation hooks. Dispatch reuses the existing v6 dispatcher; the dodge wrapper calls the unchanged function once and returns its original result. The observer reads state and writes an external sink; no explicit policy, state mutation or RNG consumption was introduced.
- All three requested selected knob arms are loaded from the v6 attempt-2 and v5 B_best files, and the declared matrix is ten seed clusters, two orientations, two heads, three arms: 120 development fights. Engineering parity entropy is separately listed. Preparation reads development declarations and uses OS entropy, with no judging root.
- Damage/death conservation, terminal-count reconciliation and exact-source-distance checks are present. The section-19 elimination-win implementation requires zero enemy survivors, a living own unit, and t < 150; timeouts are separately counted.
- Actions/outcomes parity checks compare historical/off/on nonobserver stdout and metrics byte for byte, and check telemetry decisions against full state decisions. They are planned for the single final change-batch test run.

No quality score is assigned. Fix the substantive findings, then run the one authorized final test batch and diagnostic; this source review alone is not run/report acceptance.


Source disposition after the complete correction batch:

- Finding 1 fixed: run.py adds a daemon watchdog Timer at the 1200-second deadline which calls deadline.stop(), and stops before raising on excessive daytime projection. Its success flag is set only after the final pin check and FIGHTS write, so final drift rejection produces STOP. The independent stop kills only registered owned process groups, allowing blocked pipe readers and executor shutdown to finish.
- Finding 2 fixed: lethal enemy-gun events export exact supporting-gun identities, positions and min/max ranges. Analysis uses the damage target coordinates and that event-time support snapshot for killer angle and cover.
- Finding 3 fixed with explicit sampling limits: lethal gun events export exact living attacker IDs within their own legal reach and the target gun band. The three-second preceding tick series is retained separately, and its maximum is combined with the exact lethal snapshot. Regular approaches retain exact entry-time IDs plus distinct approach starts in the preceding three-second window, which preserves same-tick entrants even when they die. The existing tracked-episode concurrency maximum is a posttick surviving-approach measure and must be described that way; the three-second starts measure must not be described as exact simultaneous occupancy.
- Finding 4 scoped: the implementer confirmed the report will name the two byte-compared contract outputs and protected historical hashes, without implying every historical fixture suite ran.

The corrected native/source paths were re-read statically after these changes. No further blocking source defect found in this bounded review. Static go for the planned final test batch and development diagnostic. The observer snapshot remains output-only, dispatch and engine state transitions remain inherited, and no project fights/tests were run by this reviewer. This does not establish runtime parity, measured outcomes, independent cross-family acceptance, or v7 readiness; those require the evidence/report disposition from the authorized run.

Integration-repair static recheck (after the failed first test batch):

The implementer reports that the first parity batch failed at request validation before executing any fights: the historical decoder rejects unknown killerTelemetry keys, including a false-valued key, and its decisionTrace option requires full trace. This review ran no tests or fights and does not independently recount that failed execution log.

The repaired observer_v1_config_codec.cpp was diffed against the historical config_codec.cpp. Its only changes allow/boolean-validate killerTelemetry, and allow decisionTrace without full trace when killerTelemetry is true. The telemetry flag is not assigned into engine or policy configuration. The historical decoder remains untouched and is explicitly included in the build identity. build_observer_v1.py links the versioned decoder. common.request_for() now omits killerTelemetry altogether for off/historical requests; their parity requests retain full trace and meet the original decoder contract. The new mechanical test reverses precisely the three decoder changes and compares the entire result to the original source; the parity test now explicitly rejects error summaries.

Disposition: static GO for the repaired final test batch. No further blocking integration finding. Preserve the failed first attempt separately from final PASS accounting, and claim runtime parity only from successful post-repair evidence. No diagnostic entropy should be consumed before that parity gate passes. This remains a same-family source review, not cross-family acceptance.
