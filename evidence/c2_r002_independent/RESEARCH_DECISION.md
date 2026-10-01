# C2 R002 bounded research decision

Date: 2026-10-01. Decision: **STOP_THIS_BRANCH** for the current passive-linear supervised-learning candidate as a claim of additional task quality or digital efficiency. This is a research decision under R4 C3 and §7, separate from the independent implementation verdict in `INDEPENDENT_REVIEW.md`.

## Evidence used

Only the registered R002 panel at committed evidence HEAD `c4400f7` is used: experiment `geomind-c2-r4-002`, numerical source commit `63ae7ddc5d11f4c7b59972227c2c0ebf7fbc0cdf`, results SHA256 `34865a9783c2337afda0578ea46e1ac2954926b5485801c394cf2eb47fccd657`. No settings, endpoints or test instances were changed and no panel was repeated for this decision.

The realizable task shows a bounded learning effect: mean test MSE 0.000414939 and mean paired reduction from frozen 52.49%, with a 95% interval of 44.80–59.96%. The registered >=50% lower-confidence-bound endpoint is **INCONCLUSIVE**. The affine endpoint is **NOT_SUPPORTED** (approximately 8.92% improvement). Linear regression achieves mean test MSE 4.88176e-32 on affine and 8.05163e-32 on realizable. The realizable teacher is linear and shares the candidate topology; this is within-family evidence.

Recorded per-trial wall-time medians, computed from the forty `results.json` instances and preserved with the endpoint values in `RESEARCH_BASIS.json`:

| Task | Candidate fitting (s) | Linear fitting (s) | Candidate 350 queries (s) | Linear 350 queries (s) |
|---|---:|---:|---:|---:|
| Affine | 10.4716 | 0.000105083 | 0.223229 | 0.0000149585 |
| Realizable | 8.84095 | 0.0000994585 | 0.198839 | 0.0000142080 |

These are the actual contended four-worker panel timings, including the implemented methods' different validation and readout paths. They support the bounded choice on these tasks; they are not single-core speed ratios or hardware energy measurements. No positive per-query saving is observed, so no amortization break-even is established. No measured memory or robustness advantage qualifies an exception to §7.

## Prerequisite assessment and boundary

The independent receipt accepts C2: its correctness prerequisite is satisfied and a bounded held-out learning effect is recorded. Acceptance does not convert the inconclusive registered meaningful-effect endpoint into support. Although R4 C3 permits stability research after correctness and actual learning evidence, §7 makes proceeding with this dominated supervised task-value/efficiency branch unwarranted. **C3 remains NOT_STARTED; no A/B, forgetting or replay experiment is authorized by this decision.**

Preserve the candidate and all accepted/historical receipts as a mechanism reference. Do not tune eta, epochs, representation, seeds or endpoint margins against these inspected test results. A future redesign needs a stated scientific reason, a new registration and fresh data before evaluation.

The recursive-resonator H-C lane is scientifically distinct from this passive-linear learning probe. C4 and hierarchy remain **NOT_STARTED**. Before that lane can begin, explicitly select its bounded question and lock the R4 recursive `ActiveUnit` contract and C4 integration, persistence, perturbation, ablation and evaluation registration; qualify each reached milestone separately. No hierarchy is added to rescue C2 and no whole-program or broader-theory conclusion follows from this decision.

## Addendum: cross-family review (Claude, 2026-10-01; corrected)

See `../c2_r002_crosscheck/CROSS_REVIEW.md`. No reported number changes. This addendum replaces my first version, which measured the gradient endpoint on unrealistic targets.

1. Two registered verification endpoints (equilibrium accuracy 1e-7 and gradient-direction cosine 0.999) are checked by focused tests but not evaluated by the panel, and they are not listed as not run. On the actual first-epoch training updates at registered β = 0.05, cosine ≥ 0.999 holds for 99.95% (realizable) and 92.65% (affine) of updates, never in the wrong direction; the minima are 0.9977 and 0.9966. At reduced β = 0.001, which is R4's stated procedure, it holds for 100%. That makes it met under R4's procedure and narrowly missed as a strict minimum at the training β.
2. The affine NOT_SUPPORTED outcome is budget-limited, not capacity-limited. Exact-gradient training on training data reaches MSE 0.00074 at 1,000 epochs and 1e-8 at 2,000, against 0.0186 at the registered 100. The candidate tracks the same gradient.
3. The frozen untrained network already meets realizable MSE ≤ 1e-3, so only the frozen-reduction criterion shows learning.
