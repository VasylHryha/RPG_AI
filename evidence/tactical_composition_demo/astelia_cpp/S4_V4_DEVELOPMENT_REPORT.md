NOT_READY

# S4 v4 contract stop, 2026-10-06

The owner requested implementation of DESIGN_0G.md section 15 revision 7, F2 deadline repairs, then exactly the amended S4 CMA-ES development protocol with skeleton v4 and a 360-minute execution allowance. The same request explicitly says: **"If section 15 is ambiguous, write the question in the report and stop."** This is that stop, before implementation or execution; it is not an A/B novice-gate STOP or a combat result.

## Questions requiring clarification

1. **Which enemy is the "main threat" for velocity feasibility when a unit has no committed focus?** Section 13 defines a threat set and damage weights, but neither section 15 nor the existing controller defines a unique main threat. Should it be the highest-damage-weight currently threatening out-ranged enemy, ties by lowest id? Should the search include all living enemies or only the movement set E_i? If there is no such threat, should the trace report no reference and null feasibility? Choosing a nearest enemy instead can reverse the diagnostic direction when threats lie on opposite sides of the unit.

2. **Which tick's actual velocity and geometry define feasibility?** Should the held mode/focus selected at prepare(k) be compared with (a) the incoming observed velocity from tick k-1, or (b) the realized displacement during tick k, after movement, collision separation and arena clipping? For (b), should the reducing direction use the prepare(k) geometry and preferred distance? The phrase "how often a held decision actually moves the unit the right way" suggests (b) with the decision's original geometry, but the current controller diagnostics are prepared before movement and exported in a post-step frame. This needs an explicit alignment rule before implementing the requested summary.

3. **How are undefined feasibility samples represented and summarized?** The requested cosine has no angle for zero actual velocity, coincident centres, or a pair exactly at its preferred distance. May those samples carry null feasibility with a reason and be excluded from the cosine mean, with their counts reported separately? Encoding them as zero would mean perpendicular motion and change the summary.

These questions concern required output-only evidence. They do not authorize adding a policy constraint, changing the oscillator, or altering the amended tuning protocol. No default has been silently selected.

## Evidence for the stop

- DESIGN_0G.md section 15 Change 3 requires feasibility for "its focus or main threat" without defining main-threat selection, tick alignment or undefined angles.
- `src/native/s3_controller.cpp` prepares state, motion and diagnostic rows in `S3Controller::prepare`; it defines no main threat or feasibility metric.
- `src/native/controller_bridge.cpp` copies `u.velocity` into the observation before the action. `src/native/combat.cpp` calls `prepareControllers` before actions and computes realized `u.velocity` after movement and separation. `src/native/host.cpp` exports its trace after `coreStep`. The two velocity alignments therefore exist and need not agree on a switch tick.
- AGENTS.md, decision 0028 items 16-18, DESIGN_0G.md sections 13-15, S4_AMENDED_PROTOCOL.md, S4_V3_PROTOCOL.md and S4_V3_RECHECK_REPORT.md F2/F3 were read. The rewritten history map was inspected; historical short hashes were not treated as current identities.

## Execution and reporting status

Expected development duration if all A/B/C stages run: **150-240 wall minutes**, based on the v3 declaration; the requested execution allowance is **360 minutes** for v4. This is an estimate, not a measurement or a run reservation.

Part 1: not implemented; no rebuild or test run. The six section-15 checks and fake-worker F2 checks remain unrun. V0-v3 source and fixtures have not been modified, and fixture parity has not been rerun.

Part 2: not started. `s4_v4_development/` was absent when checked and has not been created. No v4 seed ledger, tuning, validation, replay, registration, judging-seed use or recorded run exists. Every requested combat endpoint, timeout/gun-count table, hold/focus/feasibility summary and v3 reversal comparison is **not_run: section-15 clarification required**. No READY_FOR_S5 claim is made.

After clarification, the outstanding batch is v4 plus the F2 repairs, the six skeleton checks, fake-worker deadline/failure cleanup tests, rebuild, affected tests once at the end, and a verified Part 1 commit before the fresh-seed development run. Keep the amended population 16, generations 16, 9,766 evaluations per tuned arm/stage, A/B/C settings, 100-cluster validation endpoints and A/B novice gates unchanged.

| Stop condition | Yes/no | Action | Responsible role |
|---|---|---|---|
| Section 15 leaves required diagnostic selection/alignment undefined | Yes | Clarify the questions above before implementation or execution | Owner |

Delivery identity and verification are recorded in `s4_v4_checks/DELIVERY_NOTE.md` and the external bundle verification receipt. Only this report and the delivery note are included in the scoped document commit.
