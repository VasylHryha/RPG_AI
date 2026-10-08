# A0 revision 2 — prospective decomposition repair

Status: prepared engineering revision; no pilot/outcome fights authorized or run in this delivery. Decision 0035 and the owner's current request authorize the tooling and state-only diagnosis. The rev-1 look and all its raw fights, requests, declarations and reports remain historical evidence with the original `REVISE_O_BEFORE_TRAINING` verdict.

The unchanged look protocol is three arms, independent 18-fight timing/mechanism pilot, then 50 paired fights per regular/C3 panel (300 outcome fights), with the same twenty C3 cells, orientation balancing, 50/100 sequential stop rules, practical usefulness/harm thresholds, process gate, live RAM checks, 2 GiB RSS cap and owner wall cap. Fresh OS entropy is sealed under this folder's `_local`, with every rev-1 pilot/outcome seed excluded. Nothing resumes a rev-1 fight. The first fifty pairs are two or three per C3 cell; the optional later look is five per cell. No networks or training are implemented.

## Corrected unit contract

The stateless nearest-enemy replacement and 5 Hz cache in the original design are superseded for this A0 revision. They were experimental simplifications, and the look failed their decomposition test. Every arm now independently runs the read-only `S4V7Controller::prepare` and P16 policy on every physical tick, at T's cadence. O owns v6 movement, legal-target selection, target-retention margin, damage-filter history, deterministic complex-state reconstruction, P16 escort/focus/anchor/repulsion, participation, react and native body precedence. O's internal reconstruction is driven by its own public observation sequence, never T's actions, a T controller object, engine handles, RNG, private enemy preparation, or copied teacher state. The v6 default complex initialization is deterministic; its prepare does not use the inherited RNG.

“Unit observation” here includes the complete public observation **history**, not just a current frame. `ObservedUnit` includes each visible unit's public cross-team damage dealt/taken counters, HP/maxHP, identity, role, position/velocity, speed, damage, cooldown and reach, and the public target ID. Own preparation, guard/busy and resource facts and public threats feed the existing adapter. The v6 target/complex states are private **derived oracle state**, not privileged facts or inputs to a future network. Each unit's decision can be reproduced from the same public history independently; reproducing other units' latent derived states from that history is computationally allowed in this script ceiling, but is not a demonstrated learned-unit architecture. A future learner must receive sufficient public history/counters, or declare and test an approximation; the original 5 Hz network budget is not assumed to have passed this repair.

Sources: `src/native/s4_v6_controller.cpp` (public-counter updates, coupled derived state, legal target score and 0.2 retention margin), `src/native/s4_v7_controller.cpp` (P16 overlay preserves that baseline), and the admitted v6 `react.cpp` (participation → react → guard/body/failure). These inputs remain read-only.

## Only multi-gun decisions belong to G

O projects the public planner input separately for each eligible gun, marking only that gun eligible. It includes the complete one-gun candidate/scoring procedure, not just Singles. O+G uses the historical V2 planner at a multi-gun event, including joint family scoring and nearest-free gun assignment. For zero/one eligible guns O+G follows the same historical path, mathematically identical to O's singleton projection. G supplies only aim points; it does not set movement, targets, release times, delay fire or create new preparation locks. Arena/current/post-move annulus rejection and react/body precedence remain unchanged. The shared read-only planner is used without copying another arm's decisions. Autonomous planner families/aims are now audited, and `decisionTrace` is enabled prospectively so rev-1's missing execution traces do not recur.

## Same-state equivalence gate

`a0_equivalence.py` compiles a no-combat fixture executable. It independently instantiates O+G and T controllers, feeds identical public-history sequences, applies their native bridge decisions, and compares base movement, target, participation/react/body output, bridge movement/target/release and final executed commands including fire, aim and volley. Artillery reports separate no-ready, one-ready and multi-ready decision opportunities. Thirty-six synthetic frames cover readiness, target removal, movement, guard/busy and shell reaction. Six rev-1 fight prefixes provide recorded post-step position/target/prep/counter fixtures.

The recorded fixture fields not present in telemetry use **declared deterministic fixture values**: velocity is a displacement estimate; speed, damage, cooldown, own energy/cost/windup are fixture values. This is equivalence on identical supplied states/history, not exact reconstruction of historical T execution. No simulation step, projectile advancement or combat is run. Comparators contain deliberate target, movement, fire and aim perturbation checks. The report records fixture/raw hashes, per-role/type mismatch counts and source/binary hashes. Target: zero mismatches, with no declared O+G-versus-T differences. The fixture result is not population combat-outcome evidence.

Preparation and every fight invocation require a current zero-mismatch report; code/binary drift fails closed. The host pilot and 50-pair look remain required to measure revised outcomes. The separately shortened real-host integration fixture is tooling validation only; it does not count as a pilot or panel fight.

## Stop conditions

| Yes/no condition | Action if yes | Responsible role |
|---|---|---|
| Does the same-state fixture mismatch or have stale code/binary identity? | Stop preparation/execution and repair the implementation | implementer |
| Does public-history reconstruction need a fact absent from the future learner's input? | Revise that future learner before collecting labels | drafter |
| Does the revised look fail a rev-1 harm, unit-gap, mechanism or sequential continuation rule? | Follow the unchanged A0 report stop action | drafter |
| Does host process discovery, source admission, RAM or wall-cap admission fail? | Stop before the affected fight and preserve evidence | implementer |

The owner explicitly excludes `docs/PLAN_CURRENT.md` and living-document pins. Recheck and disposition live in `A0R2_OWNER_RECHECK.md` beside this revision. `UNCOMMITTED_A0R2.txt` contains changed paths only.
