PASS — bounded Stage B implementation, existing-raw diagnosis, focused/native fixture evidence, and host handoff; no scientific or outcome acceptance.

Reviewer family: Codex

Reviewed checkout: `a795ee4`, uncommitted Stage B revision. Read-only source review; no project execution, experiments, tests, or new fights by this reviewer. Stage A, accepted evidence, and `docs/PLAN_CURRENT.md` were not edited. A separate Codex reviewer was used because the local Claude CLI is not authenticated; this is an owner recheck, not a cross-family milestone acceptance.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Findings

1. **High — calibrated decisions are not covered by the parity gate.** `parity_run.py` delegates to Stage A `parity.evaluate` / `parity.parity_passes`, whose categorical comparison uses the original three-way fire argmax. Stage B live commands instead compare the active-versus-hold score against a per-role threshold. `calibration.choose` sets that threshold at an observed float32 score, so a tiny float64/native score change can flip an active row even when the inherited argmax parity passes. Certify threshold-based decisions, including role lookup and safety masks, and report/bound near-threshold export changes. Midpoint operating points between distinct scores reduce this avoidable boundary instability.

2. **High — aggregation does not verify the DAgger revision chain.** `train.prepare(round > 0)` trusts `DAGGER_ROUND*.json` if its status is `DONE`, without calling `dagger.check`, matching the ledger digest or parent proof, or verifying completion receipts against registered jobs. An existing `INDEX.json` bypasses preparation checks entirely. `train.checked` checks raw hashes and its own budget/index, but ignores the stored `dagger_sha256` and previous-index chain. Occupancy from another source revision can therefore be accepted under a newly measured fit. Verify the completed DAgger collection and its registered source/binary/parent proof before aggregation and resume.

3. **Medium — executable Python dependencies were dropped from source bindings.** `runtime.sources` omits the ARMY `rev2/a0_*.py` request/metric/monitor dependencies and shared `build_admission.py` / `process_gate.py` that Stage A included. Native build identity may bind some of them for binary-dependent stages, but training preparation/admission uses only the reduced source set. Include all executable dependencies in source bindings while continuing to exclude living documents and owner caps.

4. **Medium — N2 mechanism fields are fabricated zeroes.** `readout_run.mechanism` initializes `phase_samples`, `phase_abs_rate_sum`, `spacing_norm_sum`, and `forcing_abs_sum` to zero and never reads `networkState`. The resulting readout falsely implies no N2 dynamics or forcing. Accumulate the recorded fields with the correct indices and persistent unit identity, or explicitly mark them unavailable rather than zero.

5. **Medium — early refusals have no per-invocation readout.** `readout_run.run` calls ledger checks and reads the look-50 prerequisite before entering its receipt `try/finally`. Those refused invocations produce no readout, despite the explicit per-run contract. The same structure occurs in training and DAgger runs. Initialize an invocation receipt first and place admission/provenance/prerequisite checks inside the protected receipt block.

6. **Medium — cached diagnosis can silently survive changed inputs or analysis.** `diagnose.run` training-distribution caches have no input/model/source binding, and per-fight diagnosis caches bind raw/completion/native binary but omit diagnosis source and request identity. New analysis or changed model exports can reuse older disagreement statistics as current. Bind all inputs and the analysis implementation; preserve or reject stale caches explicitly.

7. **Medium — the reported distribution gap mixes command representations.** `offline_distribution` compares raw Python movement/aim/fire output with executed O labels, while on-policy `heads` compares post-safety/engine student commands with O. Participation clipping and artillery aim projection can appear as a distribution effect. Compare raw-to-executed errors using `raw_heads` where available, or reproduce the same adapter on offline states, and explicitly qualify the remaining representation difference. Original compact Stage A outcome rows may lack raw proposals; do not invent the missing comparator.

## Scope checks and remaining review

The live O shadow runs on a cloned predecision world with a separate controller and work counters, does not call a combat step, and does not transfer commands or RNG back to the student. This is the appropriate isolation design. Public-snapshot offline reconstruction differs from the live clone; opening-only fixtures cannot establish its accuracy throughout a full fight. The diagnosis should report its measured O-versus-replayed-O control mismatches by role/head, clearly qualify unrecorded state, and avoid upgrading descriptive shadow disagreement to a causal claim.

The fixed four-window rule is reused through `selected_starts`; validation/test remain round-0 whole fights. The dropped N2J0 lane is described as a cost decision rather than proof that J is irrelevant. Full-fight DAgger uses fresh entropy and student actions with O labels stored separately. Long training, DAgger collections, and fresh looks remain host execution stages; this review does not establish their outcomes.

The final diagnosis, proposed target-class loss correction, fixed implementation, and parent's focused/real-host test receipts still need follow-up review. Findings were sent promptly to the implementer before routine end-of-batch testing.

## Existing-raw diagnosis recheck

The owner's same request was sent verbatim for this follow-up. Read-only aggregation of the 73 existing completed-fight diagnosis JSON files confirms ten complete matching pairs per net, comprising nine regular fights and one C3 fight. Three further net completions lack completed matching O fights and must remain descriptive unmatched evidence. This supports explanation of the stopped partial look, not general qualification across C3 tactics.

The primary combat failure is stronger than fire underprediction alone: every melee row for every net selects no target, and none of the 100 melee units per arm over the ten paired fights records outgoing damage. N2J0 has zero prep starts in every role and zero own-attributed enemy damage across all ten pairs, despite 46 enemy body deaths. N2 has 14 ranged and 38 artillery observed prep starts, and 52 own-attributed damage. The retained N2 and dropped N2J0 are therefore not exactly identical in raw behavior; the lane drop remains a pragmatic cost decision without a J-effect claim.

Artillery aim disagreement with shadow O is 15,618/15,620 rows for N1, 35,793/35,793 for N1h, 50,101/50,101 for N1r, and 5,293/5,293 for N2. For N2J0, the shadow O aim denominator is zero: an apparent zero disagreement rate must be shown as unavailable, not perfect agreement. These conditional rows are repeated prepared states and are not independent shots. Target starvation, fire suppression, and aim failure should be presented as interacting failure modes rather than implying calibration alone will restore wins.

Enemy artillery accounts for the largest absolute own-death count, but excess deaths against matched O are mainly enemy melee: O loses seven own units to enemy melee across the ten fights; nets lose 137–180. Enemy artillery kills 254 O units versus 307–335 net units. O also loses 37 units to its own artillery/ranged fire, versus 0–23 for nets. Report source team as well as role and distinguish absolute counts from excess deaths. This does not independently prove a causal contribution of any one learned head.

The legacy `enemy_kills` statistic counts enemy body deaths, including enemy friendly fire. Keep the original receipt metric unchanged, and add explicit final-blow source-team/role attribution and own-inflicted damage. A net with no attacks can otherwise appear to have kills. Current `releases` counts repeated engine release intentions, not actual births, while current direct first-shot time uses outgoing damage. Correct actual projectile births where `shotsV6` is retained, and use an explicit damage-time proxy/censoring when births are absent.

All ten paired O-control replays have zero head errors over 447,270 labeled rows, including aim. This full-fight control is strong empirical support for offline reconstruction on those recorded trajectories; it does not remove the documented unrecorded-state limitation elsewhere. Raw first-command divergence occurs at the first physical tick for every net, so first paired position divergence and opportunity-conditioned target/fire counts should accompany that trivial opening difference.

The lower artillery out-of-any-range fraction in net trajectories does not imply improved positioning: enemy approach and longer time alive in losing occupancy alter the denominator. Opportunity counts are physical ticks of prolonged unconsumed chances, not independent attack chances. Display denominators, role strata, duration/censoring, and ratio definitions explicitly. The complete training-distribution gap and final report remain pending.

## Implementation follow-up

The owner request was sent verbatim again. Source inspection confirms executable dependency pins, shared native calibrated-fire decoding, threshold-aware float32/export/native parity, midpoint thresholds, real N2 mechanism accumulation, refusal wrappers, and stronger DAgger provenance. The revised loss installation and reused worker bindings are coherent: installation precedes worker import, the original objective is retained, evaluation resolves the installed objective dynamically, and arm-specific aggregated training states receive O shadow labels without replacing public student history.

Follow-up findings sent before the final change/test batch:

1. **Medium — aggregate metadata and global index coverage need exact equality.** Matching tag/raw/completion identity alone does not validate each aggregate fight's `arm`, `split`, seed, tactic, orientation, and request hash. Nor does checking only `arm_fights` validate the separate global `fights` bank used by calibration/parity. The implementer reports fixes requiring every registered job field and the exact deduplicated union, respectively; final code/test inspection remains pending.

2. **Medium — repeated provenance checks need admission cost.** `validate_index` recursively verifies prior DAgger rounds, including full raw hash passes per arm, and workers call it at startup, each epoch, and completion. Those checks were missing from projected fit cost. The implementer reports timing one complete index/raw check and charging it each epoch plus tail; final inspection remains pending. This avoids silently spending a large part of the owner cap on unmeasured validation.

3. **Medium — a native fixture assumes an unseeded active subtype.** `test_native_replay_calibrated_roles` constructs a random model but expects class zero for every active role. Thresholds choose active versus hold, not automatic versus release. Fix deterministic logit ordering or compare against the Python decoder.

4. **Medium — fixture replay lacks a tiny-work envelope.** `calibrated_parity.replay` checks the fixture monitor marker and environment variable but does not restrict frame count, simulated duration, or timeout, and does not hold the shared fixture lock. Bound standalone fixture replay before bypassing production admission, consistent with `execution.execute`.

5. **Residual finding 7 — native raw commands already include projection.** Native `stageRaw` clamps movement endpoints and projects artillery aims into legal ranges; `offline_distribution` directly scales Python output without those operations. Target/fire categorical and multiplier comparisons are comparable, but movement/aim differences retain adapter semantics. Reproduce the decoder or explicitly narrow the reported distribution-gap claim. The archive-backed finalizer can preserve existing measurements and qualify them without repeating expensive inference.

Final diagnosis finalization and the complete focused/native fixture test batch remain pending; no numeric quality score or release acceptance is assigned.

## Final disposition

The owner request was sent verbatim for the final recheck. All seven initial findings and the substantive follow-up findings are resolved for this delivery:

- Calibrated decoding is shared by native replay/live commands, thresholds use midpoint operating points, and parity checks threshold/subtype decisions with measured export-error bounds.
- Executable dependencies are pinned. DAgger aggregation verifies every registered job field and completion; global and per-arm indexes must match the exact intended union and immutable whole-fight validation/test bank. Measured provenance-check overhead is charged to epoch/tail budgets.
- N2 readouts consume actual recorded state. Training, DAgger, and outcome run wrappers emit early-refusal receipts. Native fixture replay now has a shared lock, bounded frame/duration/timeout envelope, and deterministic subtype expectations.
- Future diagnosis caches have strict input/source bindings. Delivered historical analysis retains its archive bindings; supplemental causal/state analysis and the missing historical arm replay retain a separate archived implementation with matching hashes.
- The diagnosis reports categorical fire/target and multiplier comparisons as comparable and explicitly qualifies movement/aim projection differences. Zero aim denominators, censored first attacks, physical-tick opportunity counts, and enemy friendly-fire credit are explicit.

Read-only final checks confirmed 73 completed recordings, ten matching O pairs for each net, and the O replay control's 447,270 rows with zero total head error. Every one of the 73 source-attributed enemy-death and own-death totals reconciles to its original receipt statistics. All nine supplemental archived source-content hashes match their payload pins. The report preserves unmatched recordings and the single C3 paired seed as limits.

The implementer's focused/native fixture receipt reports 18 passing tests, pytest elapsed 3.56 s and invocation elapsed 4.277398 s. The scope includes native shadow isolation and calibrated decoding, geometric loss gradients, aggregation provenance attacks, N2 readout, and early refusal. The final admitted binary SHA256 reported by the implementer is `229b808eb247e8a6d71914514da4d6d31dd2873d544f737e1f1e2fd5a2eb3b8f`; rebuild elapsed 29.304 s. The reviewer did not repeat project tests or run new fights.

Reviewed artifact SHA256:

- `STAGEB_DIAGNOSIS.md`: `e5d3cfbab4d376c5b2c580b4e0ba923aa12d66c616f5a56cbc06e1025c766fd1`
- `STAGEB_DIAGNOSIS_COUNTS.json`: `1e81ff6a9176ebcb0378c5c9703b1c1927db0dc12b57876b3879facd53647135`
- `TESTS_STAGEB.json`: `6b462c1ce61a8075176221def4d9fa9a472b04c6e6d8df592c1cc9bdd4cba100`
- `HOST_COMMANDS_STAGEB.md`: `04de9244cf5495d983e30f7218d590f18271dfff8f07bdcde6d3cdd40fc9ffe1`
- `STAGEB_PROTOCOL.md`: `b6de06651545f1c7bb72916a5da1973cddc4fe13e69e9b82c86267ad274c61cf`

The approved long host stages are not represented as completed: ten-epoch fits, DAgger, and fresh look 20/50 remain unrun because local Claude authentication is unavailable for the specifically requested cap authorship. The handoff starts with authenticated Claude cap authorship, preserves the live owner cap, and gives measured versus expected time distinctions. No claim is made that the new loss will win or that aggregate training will fit its cap; each measured stage can refuse.

Two minor handoff wording corrections were completed and verified: the duplicated lane-saving phrase was removed, and the command-receipt claim was narrowed to the actual run-stage receipt contract. They do not alter the reviewed diagnosis/counts/test hashes or authorize additional execution. No unresolved implementation or reporting finding remains within this bounded delivery.
