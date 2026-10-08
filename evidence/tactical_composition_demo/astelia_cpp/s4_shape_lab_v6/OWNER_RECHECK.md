PASS_WITH_NOTES

Reviewer family: Codex
Reviewer model: GPT-6
Review scope: new shape lab v6 preparation; static inspection only, no fights or tests run by reviewer.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Reviewed AGENTS.md, decisions 0033/0034, B9, the frozen owner R3 F5/F7/F8/F9 and stages/candidate-selection contract, v6 controller/runner/report/fixtures, the unchanged react adapter and engine artillery/movement sources. V5 and living documents were not edited.

## Findings

1. **R1 participation horizon underestimates the next legal release.** `shapes.cpp:26–35` computes `max(move_to_candidate, cooldown + windup) + return_to_range`. For an out-of-range candidate, windup cannot start before range is restored. For example, a 1.0 s retreat plus a 0.8 s return and 0.55 s windup is reported as 1.8 s, though the modeled legal release is at least 2.35 s. This can admit an extraction that violates the registered 2 s horizon. With the existing committed-prep veto, use a conservative `max(move + return, cooldown, energy_wait) + windup` model and a fixture straddling the horizon. The current low-energy path also silently assumes energy never regenerates; that can falsely permit the no-participating-candidate fallback. Expose own public regeneration readiness or fail closed when it is unknown.

2. **False extractions are a tautological trigger check.** `metrics.py:35–38` increments `false_extractions` only if an activation violates the very lethal/margin conditions that produced it. This measures contract violations, not prediction-driven false extractions requested in R3 F8. Rename that numeric diagnostic and report the false-extraction endpoint explicitly as not evaluated, with the missing untreated continuation stated, unless a meaningful declared validation is added. Triggered survival must not be called a saved death. The prose caveat is useful but must match the machine-readable keys.

3. **Selected shared timing is omitted from the delivered report.** `report.py::render` exposes the declaration's static atom labels but not the common timing selection or its label/hash. A later `battery_oscillator` selection therefore yields a report whose arms expose only script/search labels, with the shared RRG mechanism absent. Include selected common timing, its separate script/RRG label and selection identity in the observation/report. Atom attribution remains unchanged.

4. **E1 legality wording overstates collision safety.** `nearestReach` checks the reach disk and arena bounds inset by own radius; it does not avoid occupied endpoints. The engine accepts such movement commands and applies separation after damage, so this does not require a second movement optimizer. Describe command legality precisely and disclose that body separation can alter the endpoint. Existing arena-corner fixture covers the actual bound.

## Checks and limits

The inspected implementation uses fresh public value-only planner projections, private fixed prediction seed, declared simple/robust/battery options and no enabled rollout. Candidate generation and assignment are copied from the engine, with the output replaced by immediate geometry commands; forthcoming-gun delayed assignments are excluded. Planner fixtures compare the copy against the engine on persisted synthetic states, and this limitation is disclosed.

Shared immutable C3 base receipts, E1 reuse for the primary `E1+R1 minus E1` comparison, category-specific mechanism draws, all 20 tactic cells, 50/100/200 read gates, survivor-only series, common draw/placement schedules, roster carryover, ratio-of-totals exchange and unconditional/won/lost/timeout deaths are present. Heavy collectors are removed; selected replay exports and the same cap/process gate are retained. Timing selection is immutable before fight claims and linked in completion receipts. Frozen local documentary copies replace living-document execution pins.

The mechanism metric-movement and clear-outcome decisions intentionally remain Claude's recorded reading; native gates establish activation, not effectiveness. No arm is accepted and no result is claimed. Parent implementer must record dispositions in the new PLAN_V6.md and run focused fixtures once before preparation. This report is a controller preparation recheck, not an independent scientific milestone acceptance.

## Correction inspection

The correction batch was inspected statically before the implementer's final fixture run. All four findings are addressed:

- R1 now waits for return to firing reach before windup, combines movement/cooldown/own public energy readiness, and includes the declared observed-velocity displacement estimate. Missing regeneration with insufficient energy fails closed. Native fixtures cover the horizon boundary, known regeneration and missing-readiness fail-closed behavior; the arena-edge fixture now contains a lethal threat and exercises the retreat constraint.
- Numeric trigger failures are named `rotation_trigger_contract_violations`. `false_extractions` is explicitly `not_evaluated`, with the absence of an untreated continuation stated at fight and aggregate levels. This is a retained evidence limitation, not a zero false-extraction result.
- Reports expose `common_timing`, its independent script/RRG label and the sealed timing-selection hash, while keeping atom labels separate.
- E1 documentation describes arena/body-radius legality and the engine's post-damage separation behavior without claiming occupied endpoints are excluded.

The final light-recording addition was also inspected: only at rotation activation, the raw observer stores the exact committed threat records, self position/radius/speed/protection and both reachable movement commands. The counterfactual base is captured after E1, before R1, so the primary contrast's predicted lethal value can be independently audited without treating the pre-floor inherited goal as its baseline.

The implementer's subsequent V2 aim-boundary correction was inspected before tests. `legalAim` rejects nonfinite/out-of-arena points and checks own minimum/maximum range both at planning and after the inherited one-tick movement, using the same speed/multiplier/stop trajectory. Rejected planner output leaves the inherited command untouched instead of setting a hold or passing an invalid aim to the adapter. A separate raw `plannerRejected` audit entry is excluded from successful assignment and ranged-arbitration metrics. New fixtures cover post-movement maximum-range rejection, a legal aim and out-of-arena rejection. This closes the identified geometry-to-release timing seam without adding movement, target or timing policy; no new static blocker was found.

No further static blocker was found. The next-legal-shot value remains a declared public-state forecast, not a guarantee about future enemy choices, changing lanes or separation. Firepower utilization is specifically the eligible-ready-time fraction; actual shots and damage throughput are also retained, so the report does not rely on that proxy alone. Counterfactual prevented deaths and causal false extractions remain unmeasured. Execution must retain those limits and read activation plus metric movement before C3. Focused tests and zero-fight preparation are still the implementer's final checks; this reviewer has not run them.

## Final fixture and preparation receipt audit

The one-line fixture-only setup correction (`prepareDummies` before `prepareControllers`) matches production ordering and addresses the preserved `dummy snapshot absent` failure. The next attempt passed the native and constructor cases, then failed because pytest's repository-local temporary parent directory did not yet exist. Both failures remain separate FAIL attempts. After that directory was created, only the eight outstanding Python cases ran and passed; the already successful seven were not repeated. The final TESTS receipt records this continuation explicitly.

Read-only final evidence audit: native shape fixture PASS, 141 checks; inherited adapter fixture PASS, 469 assertions; all 15 focused Python cases passed across the final successful portions. Every fixture receipt reports zero fights. PREPARE is PREPARED with zero fights. Its declaration and ledger hashes match current bytes; every declaration source hash matches, and documentary execution pins resolve only to local frozen copies. No calibration/run receipts or top-level raw fight claims/completions exist. OBSERVATIONS has default base timing labelled script, an unsealed null timing-selection hash, zero observations and incomplete stages; the axis chart has no points. The future common timing slot is therefore still selectable before compute.

Verdict remains PASS_WITH_NOTES for preparation. No combat effectiveness, causal false-extraction measurement, scientific acceptance or execution authorization follows from these fixtures. This reviewer audited the supplied receipts and identities, and ran no project tests or fights.
