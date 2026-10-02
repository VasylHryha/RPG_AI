Verdict: **CHANGES_REQUIRED**.

# C6 R4 proposal self-audit and correction record

Reviewer family: Codex
Reviewer model: gpt-6
Date: 2026-10-02
Reviewed commit: 8c2bf51eb93a9c9239479b9b6b8ff31621d32801
Reviewed proposal SHA256: 0149388c461e0146bedf1e986334a3d75dba8f4f4c941ea6f534fb71f37bde04
Reviewed research note SHA256: 912326c5e44c0d0e4c0229cdc3ea548fa2256226ca55da8aeaf5c209c6c90d9b

This verdict applies to the original draft above. This is the drafter's recheck, not an independent cross-family acceptance review. The corrections below are applied to the [revised proposal](../../experiments/c6_proposal_r4.md), whose exact current hash is recorded in a new [receipt](../research/c6_r4_recheck_receipt.json). Owner approval of the completed revised design remains pending. The original design receipt and R3 evidence are preserved.

## Findings and corrections

| ID / severity | Defect in the reviewed draft and cause | Applied correction | Remaining limit |
|---|---|---|---|
| F1 / high | A continuation candidate was also one of four formation measurements. Complete-chain selection guaranteed its intact success and could dominate a .10 contrast. The eligibility and measurement roles were conflated. | Reserve E0 solely for continuation/link evidence; use independently generated E1–4 for the formation mean and bootstrap. Require unfiltered first-turn support. | Common-world chain selection still defines a conditional estimand; no population-rate claim. |
| F2 / high | Mechanical continuation did not establish that the changed environment enabled that candidate: it could also qualify in both control backgrounds. | Record E0's matched qualification tuple in all three backgrounds at R1 and R2. Require ten complete worlds with both (true,false,false) witnesses for the enabled-chain claim. Keep the mechanical mask for primary contrasts. | The witness threshold is an apparatus scope/quorum rule, not a population rate test. No unrestricted or indefinite recursion claim. |
| F3 / medium | Requiring endpoint source persistence as a sham condition conflated identical physical dissolution with implementation failure. | Check rolling persistence of the original set and endpoint recovery/causality; separate SOURCE_LOST_DURING_OPERATION from state-discrepant or output-positive shams. Preserve scheduled dynamics but withhold the qualified-unit causal contrast after physical loss. | Lifetime is tested on a declared discrete observation schedule, not continuously proved. Yield may be too low. |
| F4 / medium | Member-digest tie-breaking and unspecified transformed randomness could select a different physical group or intervene differently after label/coordinate changes. | Independent 128-bit priority tokens travel with elements; realized kick/replacement arrays are drawn once, recorded and transformed with the scene. Digests identify, never select. | Finite equivalence fixtures still need implementation and verification. |
| F5 / medium | The reference requirement could be read as full NumPy copies of every refined world, multiplying a workload with no runtime measurement. | Separate a predeclared full-horizon independent-law battery from full three-grid native refinement of every reached world. Factor independent old-source work while preserving its states, clocks and costs. | No empirical runtime, memory or equivalence evidence yet; the budget gate remains mandatory. |
| F6 / medium | Extreme corrected bootstrap tails had limited draw resolution and no explicit precision assessment. | Use 100,000 common world resamples; state approximate sensitivity and fix the forty-world panel. | Percentile intervals are approximate, especially for small/discrete eligible samples; more resamples do not cure low power or prove familywise coverage. |
| F7 / low | Response probes could be read as small-signal susceptibility despite finite impulses and bistability. | Explicit finite-amplitude descriptor; basin crossing belongs to its measurement fork and cannot alter the later candidate state. | Supplied bistability is an apparatus assumption, and network memory remains unmeasured. |
| F8 / medium | Diagnostic coverage and publication semantics were described but not fully inventoried; witness-shortfall and qualified-FAIL rules could conflict. | Fix 79 endpoint IDs, one finite S-linked publication per accepted candidate/world/episode, and ordered engineering → quorum → qualified FAIL → witness/unresolved → support rules. | The registered manifest/runner must implement these rules exactly, with coverage mutants. |

The physical equations, amplitudes, formation cuts, practical margins and forty-world final size are unchanged by this recheck. No observed new outcomes were available for tuning. Holding out E0 adds a fifth candidate episode to each condition/turn and increases apparatus cost; the budget estimate must include it.

## Rechecking the critique itself

F1 is an endpoint interpretation defect, not a claim that every post-treatment conditional comparison is statistically invalid. The original design already used a common paired-world chain mask and named its conditional scope. The [primary causal-inference paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC4137767/) motivates caution about post-treatment variables; it does not invalidate comparisons of paired potential outcomes in a declared common stratum. The [research note](../research/c6_r4_background_redesign.md) gives an explicit zero-marginal-effect example, carefully distinguished from a sharp zero-effect null. Holdout removes direct outcome reuse, not all selection dependence.

F2 does not require each generated unit to be larger, more complex or better at a task. Those are absent from the owner's requirements. A control-qualified next unit is valid mechanical continuity, just insufficient evidence that this particular background change enabled it. Primary effects are not cherry-picked on successful witness outcomes.

A supplied nonlinear medium is permitted by the declared computational apparatus. Its isolated attractors do not establish sustained coupled-network memory or theory truth. Generic emitted dose is a legitimate mediator for the bounded question; uniqueness relative to an ordinary emitter would need another experiment. We do not add that unrelated constraint here.

Switching previous outputs off is not freezing/deleting previous particles. Their independent full states evolve through both turns. Prescribed introduction centres apply only to newly unformed populations, not relocation of qualified units. The new carrier preserves a clean intervention boundary; it also limits the claim to retained environmental mediation rather than unrestricted mutual feedback.

No counterexample justifies silently relaxing a numerical/formation cut, changing an invalid episode into nonformation, dropping a failed control, widening a final panel after seeing its verdict, or rescoring the R3 STOP. These remain explicit stops or INCONCLUSIVE outcomes.

## Scope and disposition

This recheck used document/source reading, primary literature, analytic reasoning, and documentation-only identity/status/freeze checks. It ran no experimental code, pilot, tests, benchmark, mutation probe, development gate or panel. The new receipt records the actual documentation checks and file hashes.

The revised draft is available for owner review, not accepted or scientifically qualified. New-law formation, persistence, counterfactual witnesses, effect precision, native/reference agreement and runtime must still be measured in the authorized lifecycle. Those unknowns prevent any claim that this is an empirically optimal design. C6 remains BLOCKED; accepted milestones and recorded R3 evidence retain their prior status.
