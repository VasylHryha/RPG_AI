# 0024 — Stop R006 when the registered runtime gate cannot pass

Date: 2026-10-03. Follows owner-directed performance repair (0023) and continuing completion authorization. R006 was registered at def6fd7 on fresh namespaces with the same scientific settings and budgets.

The exact-path performance repair passed all 62 contracts, smoke and independent Claude engineering review. Its full 50-probe/three-grid/two-cohort descriptor fixture improved from 83.333 to 4.851 seconds (17.178x); the largest raw-response difference was 6.884e-14. This is an engineering fixture measurement, not a full-world or final-panel speed claim. The full R006 reference battery then passed (maximum 9.467e-13 versus 1e-10), and covariance passed.

The registered runtime rule is `max(all world seconds) * 40 / 2 * 1.5 <= 10800`. Hence a readiness PASS needs every measured world to finish within 360 seconds. It also requires at least five complete chains, so a PASS necessarily activates that projection; a missing chain quorum cannot bypass the cost gate.

Two profiles of the same still-computing worker at 10:58:47.854 and 11:05:21.949 +0300 established a conservative 392.095-second world-runtime lower bound after subtracting the sampling duration. Both included the native field-law evaluation, inside the worker's sole `run_world` call, excluding final serialization and startup. At that point readiness was impossible regardless of how remaining scientific checks finished. The implementer stopped the exact parent instead of spending the remainder of the 1800-second development cap. No C6 parent/worker remained afterward.

Worlds 0 and 1 completed immediately before shutdown at 561.151 and 546.817 seconds. Their measured cost makes the budget failure stronger: even assuming the remaining source/chain checks succeed, the final-panel projection is at least 16834.531 seconds, beyond 10800. Both original complete raw world files and the original RUNNING receipt remain unchanged. A separate `EARLY_STOP.json` records the superseding STOP, profiles/build hashes and actual completed-world diagnostics. There is no reconstructed trajectory or modified verdict.

Both completed worlds were engineering-valid. Their initial source qualified and persisted through turn 1; the reserved next source qualified. Their first-link tuple was [true, false, true], so those two links did not demonstrate intact-only enablement. In turn 2 the selected source lost qualification during the operation (times 315 and 301). Neither completed the chain. These are two unchanged development observations; they establish no population hypothesis verdict. The remaining eight worlds are incomplete.

This revision is **STOP** for measured resource readiness. No final entropy, mutation probe, recorded panel or scientific acceptance is authorized. The owner-directed replacement in 0023 is consumed; there is no automatic R007 retry. The approved physical model is unchanged; larger future native-kernel/array improvements or experiment revisions must be prospective, separately registered and owner-directed. C0–C5 and all R3-bound evidence/code remain unchanged.

| Yes/no stop condition | Action | Responsible role |
|---|---|---|
| A measured world or conservative active-computation lower bound exceeds 360 seconds? | Stop the current readiness attempt and preserve its bytes. | Implementer |
| Complete ten-world readiness PASS absent? | Keep final entropy absent and do not run mutation/panel stages. | Implementer |
| New prospective owner-directed revision absent? | Do not retry development under a new output name. | Implementer |
| Scientific population claim inferred from these two worlds? | Withdraw that inference; keep it as bounded diagnostics only. | Reviewer |

The immediate performance request is handled: profiling, exact reuse, bounded caches, independent equations, raw numerical equivalence, end-of-batch tests, independent review and real-world budget measurement. The remaining C6 blocker is explicit rather than left in a running process.
