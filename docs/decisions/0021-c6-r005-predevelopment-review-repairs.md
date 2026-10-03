# 0021 — C6 R005 pre-development review repairs and binding choice

Date: 2026-10-03. Implementer: Codex:gpt-6.

[Claude's review](../reviews/c6_r005_predevelopment_review_claude.md) at 1f295fa is CHANGES_REQUIRED. This decision records prospective repairs before any R005 development. It does not replace that review verdict, authorize a development run, or accept C6. R004's original artifacts remain withdrawn and immutable.

The owner explicitly chose Finding 2 option A: “Bind development to experiment code; bind tests and mutants in the final pipeline (recommended)”, then asked for the choice that serves the project in the long term. Development receipt hashes now include the world-generating and interpreting modules, protocol, native source/build tool, readiness gate, serialization support, source pins, environment and milestone config. Test/mutant sources are excluded from that development binding and retained in the final pipeline fingerprint. Stronger tests on an unchanged experiment can therefore be added later; changes to equations, analysis, readiness, protocol or other experiment-producing dependencies still invalidate its development evidence. No pre-development mutation run is authorized or performed.

## Findings and repairs

| Finding | Prospective action | Verification |
|---|---|---|
| 1 missing mutation classes | Extend 27 to 45 semantic mutants, including every listed missing class, primary/diagnostic omissions and additional repair guards. Backstop/timeout exemptions remain empty. | Static uniqueness/syntax check and focused negative contracts; actual mutation kill rate remains unmeasured until the ordered final pipeline. |
| 2 binding lifecycle | Owner-selected option A above. Add the actual serializer support and milestone configuration to development hashes. | Contract checks experiment dependencies remain bound while tests/mutants remain final-bound. |
| 3 chain-scope late failure | A chain endpoint depends on both turns, so any turn's engineering failure invalidates all chain claims. Unfiltered earlier valid claims retain their earlier scope. | Late-error and common complete-chain-mask contracts. |
| 4 seen final entropy | Explicit reserved namespace registry includes C6 R1/R2, R3 development/bootstrap/smoke, withdrawn R004, prospective R005, reference/covariance and known deterministic fixtures. Final entropy must be a nonnegative integer outside that registry. | Rejection contract covers each reserved value; validation performs no RNG draw. |
| 5 probe covariance | Impulse includes each owner's common phase origin. Record world alpha, owner phase origins and realized probe phases separately. | Per-probe gains and raw complex responses transform covariantly. |
| 6 vacuous pending guard | Fabricated pending/exact-path and registered/wrong-path fixtures exercise refusal regardless of current registration. | No output created in either case. |
| 7 unsuccessful-source descriptors | Compute B_before and all three B_after response descriptors before physical-loss return; unqualified R0 gets an explicit no-treatment descriptor. | Real caller contracts with fabricated assays; no new development trajectories. |
| 8 empty resamples | Preserve conservative INCONCLUSIVE_IF_ANY_EMPTY rule, document its effect and count empty draws in endpoint values. No dropping/redrawing. | Fixed fabricated resample truth table. |
| 9 hygiene | Validate before-background episode publications; describe output norms as derived masked-channel diagnostics backed by independent native contracts; convert RSS to bytes and record platform raw units and worker-process lifetime scope. | Publication tamper negatives, existing independent channel contracts and platform-unit contracts. |

Finding 7's descriptor scope is the operation section's B_before/common source prefix and each reached B_after branch. Later measurement-candidate qualification snapshots remain fully recorded; a reserved candidate that becomes the next operation source receives its descriptor at that next B_before. Computing a separate fifty-probe response for every measurement/recovery candidate prefix is not the registered response endpoint or workload. This scope is explicit in the protocol and remains for the reviewer's diff recheck; if the owner intended that broader workload, it requires a prospective clarification before development, not a silent post-outcome addition.

At 10 eligible worlds out of 40, 100000 original-world resamples yield approximately 1.006 empty eligible draws on average, with about 63.4% chance of at least one. Under the existing conservative rule that can make the interval undefined despite meeting the minimum quorum. The ten-world floor is necessary, not sufficient, for a conclusive interval. This is documented rather than changed after inspecting an experiment.

The model coefficients, detector/causal cuts, response and formation margins, horizons, budgets, reserved continuation and measurement design remain unchanged. New response diagnostics execute in snapshot forks and enter the existing runtime budget. No performance or yield claim follows from these repairs.

## Remaining decisions and gates

| Yes/no stop condition | Action | Responsible role |
|---|---|---|
| Focused repair verification failed? | Fix the concrete defect before development; retain failed check provenance. | Implementer |
| Claude diff recheck still reports a blocker? | Repair the finding; do not start development. | Implementer |
| Explicit owner exception to the one-attempt clause absent? | Leave PENDING_DEVELOPMENT_APPROVAL and do not create development output. | Owner |
| R005 development ends STOP, times out, or has engineering-invalid evidence? | Preserve its evidence and stop this design; no automatic retry or tuning. | Implementer |
| Measured readiness absent? | Generate no final entropy or final panel. | Implementer |

The owner has chosen the binding policy, not yet granted the separate fresh-development exception. After focused verification, present a short diff recheck to Claude and obtain that exception before changing registration to REGISTERED_DEVELOPMENT_ONLY. The final ordered pipeline and independent panel review remain mandatory.
