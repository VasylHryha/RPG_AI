Verdict: **CHANGES_REQUIRED (record only).** The implementation acceptance stands, and the corrections are applied; no code change or panel rerun is needed.

# Cross-family review of C2 R002 (Claude reviewing Codex's work)

Reviewer: Claude (Opus 5.5), which did not write C2. The original acceptance (`../c2_r002_independent/INDEPENDENT_REVIEW.md`) came from a separate Codex agent, the same model family as the author. Reviewed: evidence commit `c4400f7`, numerical source commit `63ae7dd`, experiment `geomind-c2-r4-002`.

**Revision note.** This replaces my first version of this review (commit `29f9e70`). That version measured the gradient-direction endpoint on random targets unrelated to the network's output (errors up to about 0.9). On that basis it reported "65.8% of updates, minimum cosine 0.10, NOT MET", which misrepresents training. It also attributed the weak outcomes to the "training budget" without testing that claim. Both points are corrected below with faithful probes, and the stress probe is kept only as a labelled stress test.

## Confirmed correct

- **Mechanism matches R4 C2:** the leaky Laplacian forces, nudge `β(u_out − y)`, step `0.25/(2·max degree + λ + β)`, clamped inputs, convergence at max force < 1e-9, and the local rule `g + η/(2β)·(Δu_F² − Δu_N²)` with the R4 sign and factor, using the same old conductances in both phases.
- **Strict float64** build (`-fno-fast-math -ffp-contract=off`).
- **Independent references:** dense Kirchhoff solve plus adjoint gradient; no candidate imports.
- **The receipt agrees with itself:**
  - candidate = direct-equilibrium local rule (realizable 0.000415);
  - feedback removed = frozen;
  - candidate ≈ exact analytic-gradient training (realizable 0.000415 vs 0.000402; affine 0.017577 vs 0.017548).
- **Verdict logic** follows the registered rules (realizable INCONCLUSIVE, affine NOT_SUPPORTED).
- **Identity:** 43 registered source files match the live files and `source/`; C0 and frozen C1 unchanged; 23 C2 and gate tests pass.

## Findings

1. **Medium: two registered verification endpoints are not evaluated by the panel, and are not listed as not run.** `equilibrium_abs_tolerance = 1e-7` and `gradient_direction_cosine_min = 0.999` each appear only in manifest validation (`run_c2.py`). The focused tests check both, on selected samples. Neither is in `checks_not_run`, and the first review did not flag this. The registration also does not say at what β the cosine endpoint applies, while R4's verification text says to "reduce β … to expose numerical error". Evaluated here:

   | Evidence | Updates with cosine ≥ 0.999 | Minimum | Wrong direction |
   |---|---|---|---|
   | **Actual training updates**, first epoch (worst case), all 40 trials, registered β = 0.05 (`probe_training_updates.py`): realizable | 99.95% of 2,000 | 0.9977 | 0 |
   | the same, affine | 92.65% of 2,000 | 0.9966 | 0 |
   | Reduced β = 0.001, random states (`probe_gradient_direction.py`) | 100% of 1,000 | 0.9994 | 0 |
   | Stress test only: registered β, targets independent of the output (errors up to about 0.9) | 65.8% | 0.100 | 0 |

   **Reading:** under R4's stated procedure (reduced β) the endpoint is **met**. On actual training updates at the training β it is met by most updates but **narrowly missed as a strict minimum** (0.9966 and 0.9977 < 0.999). This is finite-nudge bias that grows with output error, not an implementation error; no update ever points the wrong way.

2. **Medium: the affine NOT_SUPPORTED outcome is budget-limited, not a capacity limit.** `probe_training_budget.py` uses training data only and trains the exact-gradient control on trial 0 for longer. Affine training MSE is 0.0195 at epoch 0, 0.0186 at the registered 100, 0.00074 at 1,000 and 1.1e-8 at 2,000; the realizable task also keeps improving. The passive network can represent the affine target, so the registered 100 epochs at η = 0.01 were far too short. Because the candidate tracks the exact gradient, it is limited by the same budget. This changes no registered result; a longer budget would need a new registration on fresh data.

3. **Low: the error target does not discriminate.** The untrained frozen network already reaches realizable test MSE 0.000991 ≤ 1e-3. Only the frozen-reduction criterion is evidence of learning.

## Effect on the research decision

STOP_THIS_BRANCH stands, on firmer and more precise grounds. The local rule is a faithful approximate gradient method, and its weak registered outcomes are a too-short training budget, not a broken mechanism. Even with an adequate budget, the task family is linear: ordinary linear regression is exact and orders of magnitude cheaper, so the learner cannot add task value or efficiency here (R4 §7). A redesign would need a task beyond linear capacity and a new registration.

## Not run

The panel and the mutation probe were not rerun; nothing here changes a reported number. The longer-budget check used one trial per task, with the exact-gradient control, on training data only.

## Independence

A different model family (Claude) from the author and the first reviewer (Codex). It shares no context with the Codex sessions.
