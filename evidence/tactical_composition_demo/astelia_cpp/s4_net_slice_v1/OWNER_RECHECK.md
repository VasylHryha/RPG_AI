SOURCE_RECHECK_PASS_WITH_FIXTURE_RECEIPTS
Reviewer family: Codex
Review type: separate same-family implementation challenge; not independent Claude acceptance.
Date: 2026-10-08

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Scope: CONTRACT.md; schema/decoder, native host/cast/collector/teacher, PyTorch/native forwards and dynamics, losses, protocol, resource projection, fixture/test sources, requests and verification wrapper; R2 findings; repository instructions and decisions 0033/0034; read-only native combat/controller/preparation and v6 public-projection seams. This review executed no tests, fights, teacher collection or training. The implementer owns the final focused test batch after fixes.

## Findings from the initial source inspection

### NS1-R1 — High: outcome receipt identity changes during a pending cast

`Host::prepare` replaces `decisionTicks[id]` and `cache[id]` each decision tick. `consumedAck`, `launchedAck` and cancellation record that current decision and volley even when the cast began under an earlier decision. `labels.join` can recover an origin through the cast-start map, but the native receipt fields themselves contradict the contract. Store originating decision tick and volley with the pending cast and retain them through consumption/launch/cancellation. Cover a windup spanning multiple decision ticks.

### NS1-R2 — High: label join does not enforce its causal or opportunity contract

The initial `labels.join` ignores snapshots and `consumed_without_launch`, allows reordered events, and creates start/release masks merely from a nonzero target. It does not check required pre-policy snapshots, future/orphan cast origins, selected-target readiness, body blocking or pending target identity. Require chronological snapshots/intents/cast outcomes, retain both consumption and no-launch acknowledgement, and derive legal/opportunity masks from the action's selected or pending target and the declared teacher scratch-readiness convention. A native snapshot's previous target can be none at the first decision; its old readiness bit cannot substitute for selected-target legality.

### NS1-R3 — High: N2's physical drift is suppressed by the hold category

N2 adds the C4 drift to its decoded goal, but `Host` gives move-index zero a movement multiplier of zero. The participation projection preserves that multiplier when the endpoint remains in an engagement band. Thus an intended nonzero N2 drift can fail to reach actual engine movement. Compute the effective movement permission from nonzero displacement after drift while retaining categorical intent separately; test hold-category plus nonzero drift.

### NS1-R4 — Medium: initial-imitation freeze and categorical legality need executable enforcement

The contract fixes A/B/J/movement share during initial imitation, but the initial model exposes all six law entries as trainable through one parameter. Supply an explicit imitation gradient/update mask with its optimizer restrictions, or accurately reserve that enforcement for the next trainer. The loss substitutes `-1e9` for forbidden categories despite unbounded ordinary logits; lawful logits below that sentinel can make forbidden categories dominate normalization. Use true negative infinity after validating at least one legal category and supported truth. Preserve finite-gradient checks.

### NS1-R5 — Medium: shadow identity fixture compares a small state subset

The initial fixture's `bytes()` includes time, RNG, one gun's position/cooldown/energy/prep and shell count. It omits targets, projectile contents, opponent/world state and recurrent policy caches/memory/assignments. Equality of that vector does not establish the requested state-byte identity. Compare a deterministic serialization of all relevant logical world and controller state, excluding only the shadow/diagnostic output itself, and state the isolated-seam scope accurately.

### NS1-R6 — Medium: collection request does not identify its scaffold policy

The initial `requests.drill` emits the roster without its cell name or stationary enemy-scaffold contract; `rpc.collect` then runs all enemies with ordinary native decisions. D1's documented stationary enemy infantry therefore are not stationary. Carry the cell/scaffold policy in the value request and dispatch the named enemy scaffolding accordingly, or explicitly block this generic execution path until that next deliverable exists. Clarify the D1 enemy-gun firing policy versus D2 native shellfire rather than relying on the name alone.

### NS1-R7 — Medium: raw collection format exceeds the declared once-per-tick resource layout

The initial collector emits one full public snapshot per gun per physical tick, each duplicating all units and threats, with another full snapshot per gun at decision ticks. The projection sizes one joint unit/threat record per tick and allows two raw/converted copies. A ten-gun JSON stream does not satisfy that byte arithmetic. Emit one shared joint record plus per-gun identities/events and reconstruct observations, or project the actual raw duplication/JSON representation separately with an enforced record-size bound. Symbolic CPU costs and declared unmeasured memory limits are otherwise clearly separated from measurements.

### NS1-R8 — Medium: public teacher's start label omits selected-target reach

The initial teacher checks cooldown/energy/body and a nonzero target but not the selected target's min/max reach. A legal offset aim can exist while the target centre remains outside native reach, yielding positive start labels native preparation always rejects. Check selected-target native reach for start eligibility and the corresponding readiness/masks. Keep aim reach as a separate gate.

## Disposition and limits

All findings were sent to the implementer before the focused test batch. Final disposition belongs in this delivery's plan record; the owner's path-only scope excludes modifying/staging `docs/PLAN_CURRENT.md`, so its required later tracking must be handed off explicitly. A later addendum here can record source-confirmed fixes, without claiming unperformed tests or a cross-family acceptance verdict.

No implementation acceptance, milestone acceptance, measured policy usefulness, runtime feasibility or scientific RRG claim is established by this source review. Claude should inspect the final contract, corrected causal/legality/state seams, final build pins and focused fixture receipt before teacher-data execution.

## Source closure after the implementation fix batch

The implementer addressed R1–R8 before the focused suite. I inspected the corrected source, not executable results:

- R1: Cast stores originating decision/volley; consumption, launch and cancellation use that retained identity. The native fixture windup now crosses the six-tick decision boundary.
- R2: Join requires prior snapshots and chronological stages, validates supported selected targets and retained cast origins, calculates selected-target/body/preparation opportunity masks, and includes consumed-without-launch acknowledgements. Raw shared snapshots can be reconstructed using `unpack_frame`.
- R3: Intent carries a separate effective multiplier, and nonzero N2 drift enables motion even under categorical hold.
- R4: The model registers a frozen-coordinate gradient mask; losses use negative infinity for forbidden categories. The declared later imitation optimizer must use zero weight decay and fresh/zero frozen-coordinate optimizer moments; the trainer is outside this delivery.
- R5: The fixture serializer now includes unit/state fields, projectile/field contents and policy caches, assignments, phases, forcing, memory and casts; excluded actor classes are asserted inactive. The result still concerns isolated native seams.
- R6: A slice-only native hook makes opponent non-guns stationary/no-target/no-release; opponent guns remain native in both named cells, explicitly declared in the contract.
- R7: The collector emits one shared snapshot per physical tick, enforces unit/threat counts and a 65,536-byte JSON record cap, and projects that raw reserve separately from converted copies.
- R8: Teacher start eligibility checks selected-target native reach separately from the aim gate.
- R9 (small boundary finding sent during this same review): both encoders now reject fractional or out-of-bound persistent identities/ticks/caster/target IDs and require string fight identity/nonnegative physical time.

The remaining wording clarification sent to the implementer is to make the contract's opening native-opponent statement explicitly exempt the declared enemy non-gun scaffold hook. This is already the implemented and detailed cell behavior. Source closure permits the implementer's final build/focused fixture batch; it does not claim that batch has passed. No tests, fights, teacher collection or training were run by this reviewer.

## Final receipt and artifact closure

The implementer sent the owner's same request verbatim for final artifact closure. I read the final receipts and logs and compared stored SHA256 values without rerunning tests or native fixtures.

- `BUILD.json` records PASS in 25.044275333 seconds. Both native binary bytes match its binary hashes. Its pinned source hashes match current bytes except the disclosed later `test_slice.py` fixture correction and `verify_focused.py` resume bookkeeping. No native engine/controller/model/teacher source drift was found. Failed build attempts remain separately logged: missing projection `pos` helper, then fixture pointer-member syntax.
- Test attempt 1 records ten passing cases followed by the malformed fixture ordinal-zero failure. The current test source reconstructed with only `t['ordinal']=i+1` reverted to `i` exactly matches attempt 1's SHA256 and the build-pinned test source. Thus the correction did not alter those ten earlier passing cases.
- Attempt 2 logs 34 passed and ten deselected in 6.89 seconds; its measured wrapper wall time is 7.897642916999757 seconds. `TESTS.json` records its explicit resume provenance and ten unchanged previous passes. The combined batch covers 44 cases; it is not represented as a fresh 44-case single invocation. The final test-source hash matches current bytes. No successful cases were routinely repeated.
- `NATIVE_FIXTURES.json` records 183 isolated checks, 1 shells and 0 fights. These are isolated seam acknowledgements and planner fixtures, not a teacher dataset or whole-fight shadow proof.
- The final contract opening explicitly declares stationary enemy non-gun scaffolding, and its imitation section requires zero weight decay and fresh/zero frozen-coordinate optimizer moments. `assert_imitation_optimizer` implements those restrictions. The earlier wording clarification is closed.

No additional blocking source or receipt finding emerged in this bounded closure. This remains a same-family implementation recheck. Claude's cross-family review, a teacher-data projection and separately authorized execution gates remain outstanding. The final delivery manifest must retain the disclosed post-build Python fixture/runner changes rather than asserting every build-pinned source is unchanged.
