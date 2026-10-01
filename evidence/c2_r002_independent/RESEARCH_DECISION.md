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

## Addendum: cross-family review (Claude, 2026-10-01)

See `../c2_r002_crosscheck/CROSS_REVIEW.md`. Three points correct the record; no reported number changes.

1. The registered endpoint `gradient_direction_cosine_min = 0.999` was not evaluated by the panel. A separate probe of 1,000 updates at the registered β = 0.05 finds 65.8% with cosine ≥ 0.999 (minimum 0.10, never the wrong direction): **NOT MET** as a minimum. At β = 0.001, 100% meet it. This is finite-nudge bias at large output errors, not an implementation error.
2. The frozen untrained network already reaches realizable test MSE 0.000991 ≤ 1e-3, so the error target alone does not show learning.
3. Exact-gradient training of the same network reaches the same MSE on both tasks. The outcomes reflect the registered training budget and the linear task family, not a defect of the local rule.
