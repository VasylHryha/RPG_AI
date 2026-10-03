ENGINEERING_REPAIR_REVIEW_READY; C6_BLOCKED
Reviewer family: Codex (implementer self-audit, not independent acceptance).

Scope: audit of the R006 performance repair and runtime STOP at `8570072`, followed by task-owned C6 engineering repairs. The approved model, scientific thresholds, native equations and recorded evidence are preserved. C6 remains BLOCKED; this report does not assign a numeric score or a population verdict.

## Findings and repairs

| Finding | Consequence | Repair and regression |
|---|---|---|
| Sampled rows were views into complete integration blocks. | All blocks stayed live until the scope ended, defeating streaming and inflating memory. | Copy only requested samples; weak-reference regression checks that a complete prior block is freed before the next block starts, while sample times and emitted-power accounting remain correct across 10+10+1 C0. |
| Numerical maxima could conceal NaN, and finite phase differences could overflow before wrapping. | Malformed full-state input or normalization could produce a deceptively small error. Production paths already have other guards; this finding does not show that historical worlds were nonfinite. | Validate all three full-state layouts, finite input, positive finite scales, finite differences and finite derived errors. Regressions cover actual medium, position, phase, carrier and finite-to-infinite subtraction. |
| Passive trajectory lookup/eviction and first native loading were unsynchronized. | Concurrent callers could evict between lookup/use or mutate a cache during iteration. Existing process-worker runs did not exercise this thread race. | Lock cache lookup/insertion/eviction and first native loading; compute outside the cache lock, use immutable local references, and recheck concurrent insertion. Four-thread regression forces eviction and compares unfactored trajectories. |
| Identical source channels were recomputed for every probe; long scopes created large Gaussian temporaries. | Avoidable array work and temporary memory after the native speedup. | Compute the complete selected-member channel in chunks, cache at most 16 MiB of immutable results, then apply each mask. Keys bind geometry, selected trajectories, sigma and output coefficient. OFF still computes the full channel; actual medium does not enter this law. Independent Python RHS comparisons and cache-invalidation regressions check this. |
| Comparison helper trusted reported gains, coverage and check values too readily. | Duplicate probes, NaN checks or inconsistent reported gains could survive a nominal comparison. | Require all 25 sites × two quadratures, all 51 matched checks, finite arrays, exact grid/horizon coverage, source hashes, zero outgoing diagnostics, raw/coarse gains, mean gains, phases and matched clocks. Contract corruption cases cover each omission. |
| Worker CPU cost was missing, and RSS wording obscured measurement timing. | Cost reports could appear more complete than measured. | Record worker CPU time and expose it in costs; mark historical absence explicitly. State that RSS is sampled before serialization and may include earlier worlds in a reused worker. Full cost accounting remains open. |

The passive cache is limited to 64 MiB, the new full-channel cache to 16 MiB, and the existing native drive cache to 32 MiB per thread. These bounds describe retained cache arrays, not total process memory. Concurrent misses may compute duplicate temporary results. Chunking bounds scope-dependent temporary size for the approved site/member inventory; at least one frame is used for larger inventories.

Four additional semantic mutants target overflow rejection, finite normalization, sigma in the channel key, and retained sampled views. All 53 mutation targets are unique by static source inspection. A kill result is not claimed: mutation execution remains gated on development readiness.

## Recheck of the prior conclusions

The early runtime STOP remains sound. Completed worlds took 561.151 and 546.817 seconds, both beyond the registered 360-second maximum. The fixture's historical 17.178× speedup was explicitly a descriptor measurement, not whole-world readiness. Neither completed world established a chain or intact-only enablement. Two development worlds cannot establish a population hypothesis. The original RUNNING receipts and separate superseding STOP records remain immutable; `def6fd7` reconstructs the R006 implementation that produced them.

The new engineering implementation has a new dependency fingerprint. Old test/review/readiness evidence does not certify it. Validation below must bind the new source commit and artifacts.

## Validation

Validated source commit: `8561ab596220387ac4c8bc90b8985d85ea2e0f13`. Evidence: `evidence/c6_r006_post_stop_checks/CHECKS.json`.

- One gated end-of-batch run passed all **79 contracts** in 95.47 seconds, then smoke in 0.27 seconds. Its original generated stamps and artifact hashes are copied to `GATED_STAGES.json`; no mutation or panel stage ran.
- The already reserved full 50-probe/three-grid/two-cohort descriptor fixture passed strict numerical comparison. Maximum raw-response difference against the preserved baseline is **6.8834e-14**, below 1e-10. All 51 numerical scopes and all 50 probes are accounted for.
- The new fixture observation took **6.0720 seconds**, versus the original 83.3329-second baseline (**13.7241×**). The earlier optimized observation was 4.8511 seconds (17.1780×). These are single fresh-process observations on a shared workstation: this repair demonstrates correctness and bounded memory behavior, and does **not** demonstrate a further speedup or whole-world readiness. The historical comparison also passes the stricter new validator without rerunning either old fixture.
- C1/C2 accepted receipt identities (24 and 43), R3-bound identities (18), 20 unique frozen C4/C5/environment files, all 16 committed R005/R006 artifacts, all 22 historical R006 implementation identities at `def6fd7`, and the audited source pin pass identity checks.
- All 53 mutation targets match exactly once. Mutants were not executed; no kill rate is claimed.

No new development world, pilot, final entropy, mutation probe or recorded panel ran. The repaired implementation is **REVIEW_READY**, not independently accepted. C6 stays BLOCKED.

## Remaining gaps and next work

1. **Resource readiness:** a new implementation must prospectively demonstrate that complete worlds fit the registered budget. Descriptor speed alone is insufficient. Profile the native full-world law and retained-ancestor work before proposing the next development attempt; do not change equations or thresholds merely to make old outcomes pass.
2. **Chain readiness:** two completed R006 worlds lost the selected source in turn 2, and their first-link witness tuple was `[true, false, true]`. Fresh prospective evidence must establish source persistence, complete chains and exclusive causal enablement. Replaying or reclassifying these worlds cannot repair this gap.
3. **Complete cost ledger:** CPU/RSS additions do not measure native/reference/build work, serialization/storage/I/O, supervisor transport peaks or failed/discarded work. Those measurements must be added at their actual owners before claiming complete endpoint coverage.
4. **Automatic runtime stopping:** the manual lower-bound stop was valid, but the readiness driver still lacks a supervisor that stops as soon as passing the registered budget becomes impossible. Implement that prospectively with explicit failed-work accounting; do not fabricate completed-world durations from partial workers.
5. **Independent qualification:** this is an implementer audit. The repaired implementation needs independent review and fresh registered readiness before mutation/panel; a later committed panel needs the required cross-family acceptance review. The prior Claude engineering review applies to its historical source commit only.

Decision: `docs/decisions/0025-c6-r006-post-stop-engineering-audit.md`. C0–C5 and R3 receipt-bound files are outside the repair scope.
