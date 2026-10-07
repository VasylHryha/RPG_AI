PARTIAL

Execution complete:160/160 fights. P3’s strict outside-every-enemy-gun-band condition was not realized by the native safe parking/retreat controller; its outcome describes an attempted intervention. No post-outcome repair or second setting was run.

Scripted feasibility probe of DESIGN_0G §19.1; descriptive development evidence, not an RRG controller or a readiness verdict. Exactly 10 fresh seed clusters × 2 orientations × 4 arms × 2 heads =160 fights, controlled team0. One declared setting, no tuning, judging, registration or status change.

Retrospective scope disclosure: P1–P3 clear the target of every gun not assigned to a volley, including guns outside the chosen gun’s reach; there is no soft-target fallback while enemy guns live. This was implemented before fights but omitted from the pre-fight policy prose. The probe changes gun-priority targeting/suppression together with acquisition timing. Its outcomes cannot isolate timing or reject every synchronized-volley mechanism. The original declaration/policy are preserved.

Holding is possible in the fixed S4 world. Three tiny engineering fights: target none gave zero launches; an in-range target gave two launches in 2s, first at 0.7s; barrage/slow trigger calls both failed. The policy is Auto, but `sandboxAbilities=false` disables the separate global ability gate. Thus Auto barrage and slow do nothing for our guns in this world. This also applies to the opponent’s sandbox ability subsystem; game dodge reflexes and the regular shell-dodge policy remain active.

Tiny engineering fights reduce only army/geometry and replace decisions with hold/acquire controls; rules and our default skills remain fixed. Code references: `s3_runner.py:78` fixes sandboxAbilities=false; `src/native/observer_v1_config_codec.cpp:166` decodes the global gate; `observer_v1_world.cpp:94` creates ability state only when enabled and `:134` fixes external policy to Auto. `controller_bridge.cpp:46` sets target none, `combat_rules.cpp:60` blocks new preparation without a living in-range target, and `combat.cpp:26` releases the prepared shell at its current target. Existing preparation can advance while held, so the declared 0.8s acquisition window exceeds native 0.7s windup before the next waiting cycle.

If the global ability gate were enabled, `abilities.cpp:116` scans enemy clusters independently of current target: >=3 enemies within splash triggers two 0.6-damage barrage shells (20s cooldown), sets normal cooldown, and locks abilities1.5s; otherwise >=2 can trigger slow (12s cooldown), which lands after0.8s and creates a radius45 field lasting3s. This enabled-world alternative was read statically; it was not substituted into the fixed world.

Parameters and algorithms were declared before development fights in [POLICY.md](s4_volley_probe_v1/POLICY.md) and [DECLARATION.json](s4_volley_probe_v1/DECLARATION.json): k=3, max wait1.5s, acquisition0.8s. P1 is one-target acquisition; P2 uses the chosen gun’s two nearest neighbours and legal distinct ready-gun matching, with a smaller deadline volley; P3 also parks ranged direct units until fewer than4 enemy guns live. Melee keeps v6. P0 uses the unchanged v6 attempt-2 stage-B knobs. All guns retain v6 movement.

| Arm | Head | Elimination wins | Timeouts | Mean S | Enemy guns destroyed /10 | Own gun losses /10 | Shell hits / fired at guns | Enemy dodge events | Own losses /50 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P0 | regular | 0/20 | 20/20 | +9.30 | 0.55 | 1.55 | 277 / 280 | 73932 | 31.25 |
| P0 | novice | 14/20 | 0/20 | +4.40 | 8.90 | 7.10 | 543 / 559 | 0 | 44.50 |
| P1 | regular | 0/20 | 19/20 | -25.35 | 0.35 | 5.20 | 229 / 236 | 2040 | 36.05 |
| P1 | novice | 0/20 | 0/20 | -37.60 | 0.40 | 10.00 | 112 / 117 | 0 | 50.00 |
| P2 | regular | 0/20 | 19/20 | -25.75 | 0.10 | 5.25 | 166 / 167 | 3048 | 36.05 |
| P2 | novice | 0/20 | 0/20 | -38.30 | 0.00 | 10.00 | 74 / 79 | 0 | 50.00 |
| P3 | regular | 0/20 | 19/20 | -15.80 | 0.15 | 2.40 | 122 / 127 | 1322 | 25.00 |
| P3 | novice | 0/20 | 0/20 | -41.25 | 0.00 | 10.00 | 5 / 5 | 0 | 50.00 |

Regular targeted-launch hit fractions are already high (P0 277/280, P1 229/236, P2 166/167) despite few gun kills. This does not show that dodge defeats these recorded gun-targeted launches; it also does not establish why the landed damage rarely finishes guns.

Elimination requires enemy=0, own>=1 and t<150s. Timeout never counts as a win. Hit numerator counts distinct own damaging shell launches aimed at enemy guns that damage at least one enemy gun; multi-target splash counts once. Denominator includes all own shells fired at enemy guns, including misses and shells still airborne at termination. All artillery damage events on guns resolve to one source/landing-time shell; incidental hits from shells aimed at non-guns are excluded from this ratio. Dodge events are successful native dodgeGoal returns across all enemy roles, not gun-only events or distinct dodged shells. Orientations are paired within clusters; no confidence or acceptance claim is made. Win times, both sides’ dodge counts and losses per enemy kill are in the JSON.

P3 regular: 9564 / 1842700 held ranged unit-ticks inside a legal enemy gun band. P3 commands safe parking/retreat; enemy motion and collisions remain native. This exposure limits the strict outside-every-band interpretation.
P3 novice: 19003 / 489857 held ranged unit-ticks inside a legal enemy gun band. P3 commands safe parking/retreat; enemy motion and collisions remain native. This exposure limits the strict outside-every-band interpretation.

| Arm / head | Targeted release ticks | Release ticks with >=3 guns | With >=3 distinct gun targets |
|---|---:|---:|---:|
| P0 / regular | 264 | 0 | 0 |
| P0 / novice | 533 | 1 | 0 |
| P1 / regular | 92 | 45 | 0 |
| P1 / novice | 54 | 18 | 0 |
| P2 / regular | 73 | 29 | 13 |
| P2 / novice | 41 | 10 | 6 |
| P3 / regular | 43 | 26 | 10 |
| P3 / novice | 5 | 0 | 0 |

Regular elimination wins: P0 0/20, P1 0/20, P2 0/20, P3 0/20. These observations test this single acquisition/net setting; they do not rule out every volley mechanism or establish causal benefits of dodge versus formation. No settings were changed after outcomes.

Combat elapsed/awake: 118.983/118.983s. Stored-only recount elapsed/awake: 155.042/155.042s. Initial projection10–20min; combat guard20min and >1h projection stops work. All runs used caffeinate. Final focused checks:5 passed; elapsed/awake timing is in s4_volley_probe_v1/CHECK_TIMING.json. The initial fixture failure (one test wrongly treated an added ranged enemy as a gun) and its timing remain separately preserved; implementation was unchanged by that correction. No code was edited during fights or analysis.

Historical attribution and v6 fixture stdout/stderr are byte-identical across historical, observer and probe binaries; P0 additionally matches observer legacy states, actions, telemetry and metrics in two short engineering comparisons. Every previously tracked input is preserved by SHA256. All160 raw hashes, every tick, casualty totals, gun losses and targeted shell identities reconcile. No controller failure, search, fork, rollout or branch step occurred.

Owner rechecks and fixes: [OWNER_RECHECK.md](s4_volley_probe_v1/OWNER_RECHECK.md). Claude CLI is not logged in; separate Codex review is the disclosed same-family fallback. The owner forbade PLAN_CURRENT edits; tracking stays adjacent. The initial implementation recheck required P3 scope/target preservation, prompt stopping of child processes, and complete object source fingerprints; all were fixed before fights. Evidence: [compact summary](s4_volley_probe_v1/SUMMARY.json), [native fight outcomes](s4_volley_probe_v1/FIGHTS.json), [verification](s4_volley_probe_v1/ANALYSIS_VERIFICATION.json), [engineering prerequisites](s4_volley_probe_v1/PREREQUISITES.json), [fixtures](s4_volley_probe_v1/HISTORICAL_FIXTURES.json), [P0 parity](s4_volley_probe_v1/P0_PARITY.json). Scripts and versioned controller sources are delivered. Raw traces, requests and entropy are retained locally and identified in [RAW_FILES_LOCAL.json](s4_volley_probe_v1/RAW_FILES_LOCAL.json); files over45MB are never delivered. Delivery identity and normal-hook bundle/fetch verification are in adjacent DELIVERY_TRANSPORT.json.
