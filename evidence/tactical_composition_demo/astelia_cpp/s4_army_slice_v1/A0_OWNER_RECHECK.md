PASS_WITH_NOTES
Reviewer family: Codex
Date: 2026-10-09
Review type: separate reviewer of the revision 2 development design and A0 tooling. An other-family reviewer is unavailable through the current collaboration tools. This is not milestone acceptance or permission to run fights.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Read-only review: AGENTS.md, the prior Claude design recheck, decisions 0033/0034/0036, the revision 2 design, all A0 implementation files, the reused v6 build manifest/generated sources, the adapter, planner and process gate. No project code, tests, builds or fights were run by this reviewer. No numeric scores are assigned. The owner forbids changes to docs/PLAN_CURRENT.md; this file records the local recheck and its disposition instead.

## Findings from the initial read, resolved in the final batch

1. **Gate refusals have no per-run receipt.** `a0_run.run()` creates the invocation result only after process discovery, measured projection and prior-look checks. A process-gate or owner-cap refusal therefore leaves no per-run result, even though the design says refusals are retained. Create the invocation receipt before preflight, put all preflight in its guarded scope and retain the exact stopping reason. Invalid identity must still fail before any fight.

2. **Several promised diagnostics are lost or wrong in the report.** `measure()` computes label counts, active-fire rate and waypoint distance, but `summary()` discards them. It pools all unit roles, so it cannot answer L3's melee/ranged base-rate question. The eliminated-only time mean lacks its explicit denominator. For T, `geometry()` records zero applied/rejected assignments before calling the historical V2 planner; native planner audit then contains the real assignments, which `measure()` ignores. Aggregate the raw counts and distance sums, report per-role base rates and the eliminated denominator, and count T's actual assignment/rejection audit. Do not imply those zeros are measurements of no assignments.

3. **The declared unit-decomposition gate is not evaluated.** The design stops unit collection when O is practically harmful against T, but `report()` can emit `SCRIPT_CEILING_PASSED_FUTURE_LEADER_DESIGN_ONLY` while the O−T comparison is harmful. Emit a separate unit-decomposition decision using the declared harm tolerance and make future-training readiness reflect it. Parking the group route and repairing the unit oracle are separate decisions.

4. **Runtime source identities are incomplete.** The A0 code fingerprint and inherited build manifest do not bind `s4_net_slice_v1/process_gate.py`, `s4_react_adapter_v1/requests.py`, `s4_shape_lab_v2/lab.py`, or request settings `THETA_ORIGIN.json` and `REGULAR_REQUEST_TEMPLATE.json`. The exact generated requests are sealed, which protects battle inputs after preparation, but runtime gate changes and request-constructor provenance remain unrecorded. Bind these read-only executable/settings dependencies explicitly. Keep living design/process/review documents and the owner cap outside source identity.

5. **The measured projection omits validation overhead.** The completion receipt's elapsed time is captured before `completed(job)` rereads and measures the raw stream. The invocation later rereads all completed streams for reporting. Repeated gzip parsing is material for full-army streams and does not appear in the fight-rate estimate. Include final-validation/report overhead in the measured pilot projection, or measure it separately with an explicit projection term. Check the wall deadline around compression, validation and reporting loops; checking it only while the native child runs can exceed the invocation cap.

6. **Live host RAM is first checked after the child starts.** `vm_stat` and reserve availability should be checked before `Popen`, then RSS/reserve should remain live checks during execution. A missing live-RAM facility or already-low host reserve should not start a fight.

7. **The native fixture does not exercise the group seam.** The current fixture compares O/O+G immediately after `prepare()`, before any geometry command. It does not establish zero-eligible no-op, single-eligible O/O+G equivalence, multi-eligible joint routing, readiness after preparation, or rejected-aim fallback. Add synthetic native checks of `army_a0::geometry()` using manually assembled state and snapshots. They must not call `create()`, `coreStep()` or `fight()`. Collect all edits before the one focused test batch.

8. **Interrupted preparation cannot resume.** `prepare()` exclusively writes requests before sealing the entropy ledger. If it stops halfway, the next invocation draws new entropy and collides with existing request filenames; it cannot reconstruct the original transaction. Seal a recoverable preparation transaction before materializing its requests, or retain/move the incomplete preparation as an abandoned attempt before beginning fresh entropy. Preserve prior attempts and verify every recovered request.

## Prior finding disposition

The revision 2 design resolves the substantive design causes of H1–H4, M1–M6 and L1–L5:

- H1/M3/M4: A0 is first, with O/O+G/T paired regular and balanced C3 panels, a separate 18-fight mechanism/timing sample, 50→100 looks and a script-ceiling parking rule before learned leader work.
- H2/H3: P16 and the one-gun V2 choice belong to O. Only the multi-eligible V2 assignment remains in G. Participation and react/body precedence are explicit and supported by cited source. The code separates the O/O+G base from the historical v6 teacher and changes group aim only.
- H4: shared world encoding at 5 Hz, cheap pooling, float32 fits, float64 export parity, an arithmetic bound, per-fit/fight targets and a ≤20-step timing projection are stated.
- M1/M2: future collection uses O/O+G behavior trajectories; elimination censoring, kills/minute and saturation are present. Finding 2 above concerns delivery of some diagnostics, not the chosen metrics.
- M5/M6/L1/L2: the 2 GiB allowance and owner cap source, matched child-data leader fits, parameter tolerance and K/phase diagnostics are explicit.
- L3/L4/L5: the base-rate requirement, readable A0-first contract and stale-marker deletion are explicit. The base-rate reporting implementation needs finding 2's correction; the path-only replacement marker is still a final-delivery task.

The three-arm outcome comparison cannot causally partition deaths saved between single- and multi-gun events. The design and report state that limit instead of inventing event-level gain attribution. This is an acceptable boundary for the requested A0 arms.

## Disposition

The drafter/implementer received all eight findings during the final change batch. This reviewer read back the revised implementation without executing code:

| Finding | Verified disposition |
|---|---|
| 1 | The invocation receipt is created before process discovery, projection and prior-look checks; those checks are inside the STOP_RESUMABLE/final-receipt scope. Source identity still fails before execution. |
| 2 | T counts real planner/plannerRejected audit. Label counts, rates and distances aggregate into summaries, with melee/ranged/artillery rates and readiness opportunities. Elimination reports include eliminated/censored denominators. |
| 3 | The report emits a separate unit-decomposition decision; a harmful completed 50-pair unit gap blocks progression to 100 until revised. Leader and unit dispositions remain separate. |
| 4 | The fingerprint binds the runtime process gate, request constructors, their build import and JSON request settings. Living documents and LAB_CAP remain excluded. |
| 5 | Measured fight time includes compression, raw validation and hashing. Newly validated completions enter the cache, preventing routine reparse at final reporting. Raw parsing/compression check the deadline; projection is compared with remaining invocation time. |
| 6 | Live host RAM is checked before child creation and live RSS/reserve checks remain active during execution. |
| 7 | The synthetic native fixture manually crosses the preparation boundary without advancing combat or refreshing the 5 Hz base. It exercises no-op, single-event exact O/O+G aim parity, multi-event joint routing and illegal-point fallback. It calls no create/coreStep/fight. |
| 8 | PREPARATION seals paired entropy and source/binary identity before requests. Reinvocation regenerates missing requests and verifies existing ones, with declaration recovery after a ledger-to-declaration interruption. |

No blocking design or tooling defect remains from this read-back. The focused test batch remains the implementer's final verification gate and was not run by this reviewer. The native host has not been checked in a real fight, and the script ceiling, event share and measured fight-time projection are unresolved until the authorized host run. This verdict covers the revision 2 design and script-only tooling on inspection; it is not evidence of scientific efficacy, cross-family milestone acceptance or source qualification.

Final implementer verification: the complete focused batch passed once after all fixes: 17 tests in 2.46 seconds. Native host build completed in 23.10 seconds. The fixtures advance no combat. No fights or measured A0 pilot were run. This adds bounded verification to the reviewer's read-only disposition; it does not establish a script outcome or cross-family acceptance.
