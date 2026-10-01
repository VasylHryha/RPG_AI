# C2 R002 handoff

**Implementation: REVIEW_READY. Independent acceptance is pending.** C0 and C1 R006 are independently accepted. R004/R005 remain CHANGES_REQUIRED; preserved historical receipts cannot bypass the repaired C1 prerequisite. C3 and hierarchy remain NOT_STARTED.

Experiment `geomind-c2-r4-002`, source commit `63ae7ddc5d11f4c7b59972227c2c0ebf7fbc0cdf`; result SHA256 `34865a9783c2337afda0578ea46e1ac2954926b5485801c394cf2eb47fccd657`. The source snapshot includes Python candidate/evaluator/reference, strict float64 C++ kernel, tools, tests and both C2 registrations.

## Reached checks and exact experiment

23 focused checks PASS. They include 3-node analytic free/nudged equilibrium, selected 16-node independent equilibria, one-sweep synchronous ordering, same-old-conductance phase equality, update sign/factor and small-nudge gradient direction, independent finite differences, freeze/clone/load/restore, no-target inference, permutation equivalence, disabled feedback, saturation and refusal controls, actual evaluator serialization, and milestone gate isolation. Four focused numerical mutants are detected. The non-panel smoke performs 100 updates. The final panel has all five engineering gates PASS and records forty task/initialization trials in 203.456 seconds.

Each task has twenty initialization seeds and independent dataset/teacher/order seeds; 100 training examples, 50 validation examples and 200 final-test examples; 100 epochs with the same fixed per-trial sample orders across learning methods. Fixed eta 0.01 and final epoch 100 were registered before fitting. Validation does not select settings. The realizable teacher uses an independently parameterized network of the same topology; this is a matched prior, not out-of-family transfer.

Candidate free activity starts at zero. Nudged activity starts from converged free activity; both phases use identical old conductances. Only after both meet max-force <1e-9 does the specified local rule update g. Inference has beta=0 and accepts x only. No autodiff/backward program runs in the candidate. The independent dense control and analytic implicit gradient are never called by the candidate. Soft nudging approximates an objective gradient and is related to established equilibrium propagation.

## Observed held-out results

| Method | Affine mean test MSE | Realizable mean test MSE | Median fitting CPU s per trial |
|---|---:|---:|---:|
| candidate | 0.0175769 | 0.000414939 | 4.483 |
| frozen_random | 0.019335 | 0.000991207 | 0 (initialization shared) |
| feedback_removed | 0.019335 | 0.000991207 | 2.821 |
| constant_train_mean | 0.0247595 | 0.0386103 | Wall time only; per-trial receipts |
| ordinary_linear_regression | 4.88176e-32 | 8.05163e-32 | Wall time only; per-trial receipts |
| direct_equilibrium_local_rule | 0.0175769 | 0.000414938 | 1.089 |
| analytic_gradient_training | 0.0175479 | 0.000401681 | 0.662 |

- **Realizable:** candidate MSE 0.000414939, bootstrap 95% CI [0.000213921, 0.000650806]. Mean per-trial relative reduction 52.49199%, CI [44.80293%, 59.96338%]. The error target <=1e-3 is met, but the registered lower-confidence-bound >=50% reduction condition is not. Primary provisional learning endpoint: **INCONCLUSIVE**. Paired MSE difference is negative: -0.000576268, CI [-0.000949191, -0.000281515]. This demonstrates a bounded improvement; it does not qualify the full meaningful-effect target.
- **Affine:** MSE 0.0175769, CI [0.0167254, 0.0184758]; reduction 8.92047%, CI [7.45249%, 10.45595%]. The registered target is **NOT_SUPPORTED** on this task.
- **Feedback removal:** outputs and serialized conductances equal the initial frozen model in every trial, so the observed learning depends on permitted feedback.
- **Numerics:** maximum final output difference against independent equilibrium is 6.47003e-9; maximum difference from the independently trained direct-equilibrium local-rule control is 1.88349e-7. All predicted edge interventions and paired response-to-geometry controls pass. These causal paths concern this weighted activity model, not recursive resonators.
- **Strong simple baseline:** ordinary linear regression gives near-zero MSE on both tasks with trivial fitting/readout. The candidate has no registered quality/cost advantage over it. Under R4 section 7, stop claims of additional task value/efficiency from this mechanism; no hierarchy is added to rescue the outcome.

## Failure, saturation, work and persistence

Candidate: 400,000 committed sample updates, 800,000 phases, 2,667,643,381 synchronous sweeps; zero refused sample updates, zero failed inference queries, zero bound-saturated edge updates or final edges. The feedback-removal control also records its actual work separately. Every sweep scans active edges; a local rule is not sublinear total work. Native counters name edge scans/node writes, not FLOPs or joules. Degree-bound scans are charged once per phase. Allocation, Python dispatch, validation, control fitting, teacher generation, query, load/storage and compilation are included in total time or separately identified receipt fields.

Summed contended candidate fitting wall time across the forty trials is 382.732s; direct-equilibrium local-rule fitting is 91.847s, analytic-gradient fitting 54.887s. These sums exceed parallel-panel elapsed time; do not compare them as single-core elapsed speed ratios. Process CPU times, native counts, query times, fitting times, bytes, load times and per-trial total times are recorded. There is no claim of hardware energy savings. The measured development NumPy phase probe justified the C++ kernel; C0/C1 remain unchanged.

Frozen exports are immutable, cloned training does not alter parents, loaded answers match exactly, and restoring initial g reproduces frozen predictions. Retention here is this snapshot/query protocol. Task A/B forgetting and replay belong to C3 and are NOT_RUN.

## Preserved interrupted R001

`evidence/c2_r001/FAILURE.json` and `INTEGRITY.json` preserve the evaluator serialization failure, eleven completed trial artifacts, old source and contract report. The first row could not serialize a NumPy boolean, so timing/epoch receipts were lost. It is not qualified evidence. R002 fixes receipt scalar typing and saves each trial receipt before process aggregation. It keeps the same numerical rule/settings/endpoints and uses newly registered, disjoint initialization/data/teacher/order seeds. The earlier extreme-input test assertion failure is preserved byte-for-byte in `evidence/c2_dev_checks/initial_contracts.xml.gz`.

## Smallest useful separate review

1. Inspect `PIPELINE.json`, actual contracts, `MUTATION.json`, `BUILD.json`, result/source hashes, JSONL/individual-receipt equality and per-trial artifact hashes. Verify accepted C0/C1 hashes without rerunning their experiments.
2. Review native synchronous ordering, dt scan, same-old-g free/nudged phases, local sign/factor, sample transaction refusal and target-free query path. Review independent matrix assembly, adjoint sign and finite-difference tests separately.
3. Reuse the forty recorded varied trials. Run only affected focused checks into a fresh review directory; do not repeat the panel or C1 mutation suite absent a concrete finding.
4. Check all baselines, seed-level uncertainty, honest INCONCLUSIVE primary endpoint and stronger linear-regression control. Decide implementation acceptance independently from hypothesis support.

**Stop:** separate C2 acceptance is pending. Do not advance C3, recursive hierarchy, or broad theory claims.

## Addendum: cross-family review (Claude, 2026-10-01; corrected)

See `../c2_r002_crosscheck/CROSS_REVIEW.md`. No reported number changes. This addendum replaces my first version, which measured the gradient endpoint on unrealistic targets.

1. Two registered verification endpoints (equilibrium accuracy 1e-7 and gradient-direction cosine 0.999) are checked by focused tests but not evaluated by the panel, and they are not listed as not run. On the actual first-epoch training updates at registered β = 0.05, cosine ≥ 0.999 holds for 99.95% (realizable) and 92.65% (affine) of updates, never in the wrong direction; the minima are 0.9977 and 0.9966. At reduced β = 0.001, which is R4's stated procedure, it holds for 100%. That makes it met under R4's procedure and narrowly missed as a strict minimum at the training β.
2. The affine NOT_SUPPORTED outcome is budget-limited, not capacity-limited. Exact-gradient training on training data reaches MSE 0.00074 at 1,000 epochs and 1e-8 at 2,000, against 0.0186 at the registered 100. The candidate tracks the same gradient.
3. The frozen untrained network already meets realizable MSE ≤ 1e-3, so only the frozen-reduction criterion shows learning.
