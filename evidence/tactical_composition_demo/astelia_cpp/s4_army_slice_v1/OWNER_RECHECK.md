# Owner design recheck

Initial verdict: CHANGES_REQUIRED.

Reviewer family: Codex. This is a separate same-family owner recheck, not cross-family independent experiment acceptance. Review was read-only apart from this report. No project code, tests, binaries, fights, collection or fitting ran. `docs/PLAN_CURRENT.md` remains untouched under the owner's explicit instruction.

Initial reviewed SHA256 of `DESIGN_ARMY_SLICE.md`: `7564749a4d501ed9d0dbc836624367b1b5f5336deaaf241da833bc5949e67e07`.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Findings and required repairs

**F1 — Exact group points need an explicit reachable learned action.** Sections 2 and 4 use a categorical 33-point autonomous aim support and 33-way movement support, but the leader emits arbitrary exact V2 gun points and escort/approach waypoints. Neither support currently guarantees a representation of the incoming command. The generic unsupported-command-to-empty rule can discard genuine coordination even when the leader predicts the exact teacher point. Add a masked command candidate to the corresponding unit head, with the exact feasible point represented. The unit network must predict whether to choose it; candidate construction must not directly overwrite its action. State loss labels, empty equivalence and invalid-command handling for that slot. This repair is necessary for a structurally learnable units-plus-leader interface.

**F2 — Command input and recurrent update order need one explicit protocol.** Sections 2, 3 and 6 say that commands belong to the encoded input, while the live order publishes child state before the leader and then runs conditioned heads. It is not specified whether the second readout mutates memory, whether commands influence the already-published state, or how stored replay treats present/empty command augmentation. Specify exactly one physical-tick state update, which inputs it consumes, and a side-effect-free command-conditioned head pass. If commands enter recurrence on a later tick, name that delayed channel and reproduce it in refresh, burn-in and export. This removes a circular/update-order implementation choice and makes empty-command equivalence testable.

**F3 — Start target locks and the six-tick ready bound are NS1 additions, not native full-army mechanics.** The design repeatedly calls both native. In the actual full-army bridge, `src/native/controller_bridge.cpp:46` rewrites `u.target` on every dispatch. `src/native/combat_rules.cpp:60–68` consumes energy once at preparation start and then increments preparation, without storing a target lock. `src/native/combat.cpp:11,20–33` resolves the current target for the act. NS1 adds pending-target enforcement and the six-tick behavior in its own `host.cpp:30,40,46`. The smallest repair is to match the full-army target lifecycle: base decisions may retarget during preparation; a release event uses its current target and submitted aim unchanged for that act. Keep started-target/current-target/aim-reference identities distinct. Remove the custom six-tick cancellation unless explicitly introduced as an AS1 policy change. Place the release-event snapshot after `gamePrep`, before the act, as the v6 planner does; ready casts held by the network need a fresh eligible release readout on subsequent ticks, not only at the first ready tick. State role reach semantics separately: melee/free artillery act checks pre-walk target reach; direct ranged fire checks post-walk reach (`combat.cpp:13–16`).

**F4 — A decomposition ceiling needs a small closed-loop control.** The honest public autonomous oracle is a new decomposition, not the historical best script: it replaces inherited v6 history, changes target/movement rules and improves Singles aim. The current T-versus-U sanity result cannot distinguish a poor decomposition from a learning failure. Run the public autonomous oracle as a labelled script control on the same existing stage-A 10–20-pair sanity inventory only. Report oracle-versus-source and network-versus-oracle gaps. It does not need another broad script-value panel or any new run in this design session. Keep source T as the required outcome comparator. If the decomposition itself fails competent full-army participation, repair that dependency before calling it a network-learning defect.

**F5 — Aggregate admission omits stage-A sanity fights.** The outcome table counts the six-arm stage-B sanity maximum of 120 physical fights, but stage A separately requests T/U-P/U-R sanity, adding 30–60 physical fights; F4 would add 10–20 more. Add the separate stage-A extent to the complete admitted budget and explicitly count any later series extension. The historical 126/252-minute outcome-only extrapolation is correctly labelled historical; it must not be presented as total slice time.

## Positive bounded conclusions

The full roster and C3 inventory match the source: `s4_shape_lab_v2/lab.py:86–99` constructs 10 melee, 30 ranged and 10 artillery per side; the v6 declaration has 19 pool tactics, with regular making twenty cells. The draft correctly distinguishes source-teacher history from public snapshot labels, preserves full-army neutral dispatch, avoids hidden P16/react fallback, puts planner binding at group level, and labels stateless imitation as insufficient for an RRG-state claim. The added U-R+P bridge isolates leader architecture on a fixed child checkpoint. Whole-fight splitting, fresh independent inventories, logged conflict denominators, living-document pin exclusions and a bounded timing sample are appropriate. No historical result or accepted receipt is changed.

## Disposition

Final verdict: NO UNRESOLVED DESIGN FINDINGS in the bounded reviewed scope.

Final reviewed SHA256 of `DESIGN_ARMY_SLICE.md`: `04c0126c8595390d1d61fda565b4a36ef68b0f060e58fcc7ff7f4846e41c0706`.

The drafter repaired F1–F5 in one batch. A bounded reread confirmed the explicit masked 34th command candidate, one state update with side-effect-free conditioned heads, source-compatible preparation/retarget mechanics with post-preparation readouts on every eligible held-ready tick, a sanity-only autonomous-oracle control, and complete aggregate fight accounting. The full 3440-fight maximum is 240 collection + 80 stage-A sanity + 120 stage-B sanity + 2400 outcomes + 600 initial series; later extensions require separate admission.

The reread also requested an explicit numerical rule for absent plain-child mode/rate publications in pooled leader training. The drafter added zero placeholders with false presence masks, excludes absent angles from sums, disables R parent-phase evolution for U-P contexts, and separates family histories. Shared command heads still train on declared physical/public contexts. This closes the undefined numerical inputs without presenting plain memory coordinates as inherited resonator rates. Actual parent-law interpretation remains limited to valid U-R publications.

This closure assesses the design contract, not measured competence, teacher-decomposition utility, runtime feasibility, learned export parity, RRG attribution or experiment acceptance. Those remain the prospective gates stated in the design. No execution is authorized by this review, and no numeric score is assigned.
