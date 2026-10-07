APPROVE_WITH_NOTES
Reviewer family: Codex
Reviewed run commit: d5044e885056ed6a584ed64d09fda1da3e28c85c
Workspace HEAD at supporting review: cdced329469bb75fbf445a36c872833d6b8ed6f5

This is a separate-agent, same-family supporting recheck of the Codex implementation and Claude-executed v3 development run. Root Codex owns the cross-family review of the Claude-executed run and the complete stored metric recount. That recount was pending when this note was written; this note does not claim to have independently recomputed every reported measurement.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

The supporting reviewer read AGENTS.md, DESIGN_0G sections 19.8 through 19.12, the sealed policy, controller implementation, observer host, relevant native engine sources and fixtures. No combat, process listing or project tests were executed. All work here was read-only stored-data processing and static inspection. No existing v3 files, PLAN_CURRENT or DESIGN_0G were modified.

## Finding requiring presentation correction

The original v3 S4_ESCORT_PROBE.md paired table (lines 26 through 47 before correction) reports wins and win differences but omits each orientation's outcome/S, cluster mean S and intervention-minus-P12 mean S. POLICY.md promises these fields, and COMPACT.json already contains them. Root should expand the report using the existing stored fields and explicitly record this presentation correction. This does not require changing a receipt, controller, rule or entropy.

No invalidating P16 implementation or measurement defect was found within this supporting review's scope. The result remains one development panel; replication is required before using P16 as the v7 witness under section 19.12.

## Independently checked stored evidence

RAW_FILES_LOCAL.json was verified before any raw parsing: all 620 listed files matched both recorded byte count and SHA256.

An independent streaming scan of all 40 P16 panel fights verified:

- 46,165 escort audit rows;
- 672,961 non-gun prepare-unit commands exactly equal the native cached P12 command on that same observation;
- 386,942 gun controllerFailure flags exactly equal P12;
- 32,651 gun targets differ from P12, and 130,487 gun movement tuples differ. These are allowed consequences of the changed individual/anchor ranking. An anchor change can alter movement even while the individual gun retains its baseline target;
- all 40 paired P12/P16 initial observer snapshots are structurally identical;
- terminal actual living-unit counts and time exactly reconcile with native summaries in all 40 P16 fights;
- all 40 P16 fights report completed status, zero controller failures and zero numerical integration failure ticks;
- all 19 P16 regular wins have enemy survivors zero, own survivors at least one and terminal time strictly below 150 s. The sole regular nonwin is c09/o1.

The raw-audit comparison uses the native P12 object embedded in P16 on the same observation sequence. Comparing actions from separate diverged P12/P16 combat trajectories would confound observations with policy. Static inspection establishes that the embedded P12 receives the exact observation at every prepare, starts with the same seed/knobs, and is not mutated by P16; its prepared state is therefore the relevant same-observation baseline.

| Cluster | Orientation | Time, seconds | Own survivors | Enemy survivors |
|---|---|---|---|---|
| c00 | o0 | 60.76666666666578 | 6 | 0 |
| c00 | o1 | 29.966666666667315 | 9 | 0 |
| c01 | o0 | 71.99999999999848 | 2 | 0 |
| c01 | o1 | 48.29999999999982 | 5 | 0 |
| c02 | o0 | 46.06666666666661 | 8 | 0 |
| c02 | o1 | 66.56666666666545 | 3 | 0 |
| c03 | o0 | 43.66666666666675 | 6 | 0 |
| c03 | o1 | 44.40000000000004 | 3 | 0 |
| c04 | o0 | 42.866666666666795 | 8 | 0 |
| c04 | o1 | 41.86666666666685 | 7 | 0 |
| c05 | o0 | 51.433333333332975 | 3 | 0 |
| c05 | o1 | 65.8666666666655 | 1 | 0 |
| c06 | o0 | 32.8000000000007 | 9 | 0 |
| c06 | o1 | 55.49999999999941 | 5 | 0 |
| c07 | o0 | 44.233333333333384 | 8 | 0 |
| c07 | o1 | 53.3666666666662 | 6 | 0 |
| c08 | o0 | 50.43333333333303 | 5 | 0 |
| c08 | o1 | 51.59999999999963 | 3 | 0 |
| c09 | o0 | 46.86666666666657 | 4 | 0 |

A separate stored launch-time audit found zero pending enemy artillery shells at termination in every one of these 19 wins, using scheduled impact time strictly greater than terminal time. Some own shells remain pending; the declared terminal rule permits this. This check does not establish that all hostile direct projectiles had resolved, because the observer lacks complete projectile state.

## Static attribution and engine check

- s4_escort_probe_v3/escort.cpp:13-42 prepares exact P12 first, clears override state each prepare, and keeps full baseline fallthrough when integration is rejected or either battery is absent. It does not write baseline state or consume its RNG.
- P16 changes enemy-gun ordering to descending integer V, then ascending exact HP/id. The original P11 candidate sets, union-reachable anchor fallback, per-gun reachable selection, radial focus construction, ascending-id repulsion, coincidence conventions and multiplier-before-repulsion rule are preserved.
- src/native/s3_controller.cpp:257 implements decide as a pure prepared-map lookup. S4V6Controller inherits this method. Extra audit calls in s4_escort_probe_v3/host.cpp:102-113 cannot advance controller state or consume entropy.
- src/native/controller_bridge.cpp:48 applies the same inclusive artillery centre-distance min/max range used by the independent oracle. Release/body flags are native consequences of role and the decision, not new P16 inputs.
- src/native/combat.cpp:144-149 implements inclusive splash plus victim body radius, capped actual HP and friendly lob damage. These are declared engine semantics. P16 counts current observed centres; it does not read future impact state or hidden rollout information.
- src/native/world.cpp:126-128 terminates a mirror fight when either side is eliminated or duration is reached. The sealed elimination rule explicitly uses that terminal state. This is a shared engine convention and a limit on after-termination claims, with no evidence of a P16-specific exploit.
- The sealed native fixture source includes unchanged-role, clone, phase exit, rejected integration, min/max reach, anchor fallback, radial-zero and repulsion-coincidence cases. Existing fixture logs report PASS; this supporting reviewer inspected those sources/logs without rerunning them.

## Limits and root-owned checks

The full 120-fight recount, every report number, original source/binary/entropy seal identity, development entropy freshness and P12 execution/report ordering remain root-owned checks. This supporting note must be read alongside the root review and its stored verification receipt. No population reliability, scientific acceptance, judging execution, v7 permission or resonator/source claim follows from this supporting approval.
