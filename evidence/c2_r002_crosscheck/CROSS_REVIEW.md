Verdict: **CHANGES_REQUIRED (record only).** The implementation acceptance stands, and the corrections are applied in this commit; no code change or panel rerun is needed.

# Cross-family review of C2 R002 (Claude reviewing Codex's work)

Reviewer: Claude (Opus 5.5), which did not write C2. The original acceptance (`../c2_r002_independent/INDEPENDENT_REVIEW.md`) came from a separate Codex agent, the same model family as the author; this is a second review from a different family. Reviewed: evidence commit `c4400f7`, numerical source commit `63ae7dd`, experiment `geomind-c2-r4-002`. About 15 minutes, as required by `AGENTS.md`.

## Confirmed correct

- **Mechanism matches R4 C2:** the leaky Laplacian force, nudge term `β(u_out − y)`, step `0.25/(2·max degree + λ + β)`, clamped inputs, convergence at max force < 1e-9, and the local rule `g + η/(2β)·(Δu_F² − Δu_N²)` with the R4 sign and factor, using the same old conductances in both phases (`native/c2/relaxation.cpp`).
- **Strict float64:** `-fno-fast-math -ffp-contract=off` (`tools/build_c2.py`).
- **Independent references:** dense Kirchhoff solve plus adjoint gradient; no candidate imports.
- **The receipt agrees with itself:**
  - candidate = direct-equilibrium local rule (0.000415 on both);
  - feedback removed = frozen (learning disappears);
  - candidate ≈ exact analytic-gradient training (realizable 0.000415 vs 0.000402; affine 0.017577 vs 0.017548).
- **Verdict logic** follows the registered rules: realizable INCONCLUSIVE (reduction 95% CI 44.8–60.0% straddles 50%); affine NOT_SUPPORTED (CI upper 10.5% < 50%).
- **Identity:** all 43 registered source files match the live files and `source/`; C0 inputs unchanged; frozen C1 files unchanged. 23 C2 and gate tests pass (1.2 s).

## Findings

1. **Medium: a registered endpoint was never evaluated, and was not listed as not run.** `gradient_direction_cosine_min = 0.999` appears in the manifest and in `validate_manifest`, but the panel never computes it. It is missing from `checks_not_run`, and the first review did not flag it. Evaluated here (`probe_gradient_direction.py`, 1,000 single updates at the registered settings, clipped updates excluded):

   | Setting | Updates with cosine ≥ 0.999 | Minimum cosine | Wrong direction |
   |---|---|---|---|
   | registered β = 0.05 | 65.8% | 0.100 | 0 |
   | registered β = 0.05, output error < 0.1 | 97.8% | 0.995 | 0 |
   | reduced β = 0.001 | 100% | 0.9994 | 0 |

   Read as a minimum over updates, the endpoint is **NOT MET at the registered β**. This is finite-nudge bias at large output errors, not an implementation error: it disappears as β → 0, consistent with the existing small-β focused test, and training still tracks exact-gradient training because errors shrink during learning.

2. **Low: the error target does not discriminate.** The untrained frozen network already reaches test MSE 0.000991 on the realizable task, under the ≤ 1e-3 target. "Error target met" is therefore not evidence of learning; only the frozen-reduction criterion is.

3. **Low: the cause of the weak results is not stated.** Exact-gradient training of the same network reaches the same MSE on both tasks. The INCONCLUSIVE and NOT_SUPPORTED outcomes therefore reflect the registered training budget (η = 0.01, 100 epochs) and the linear task family, not a defect of the local rule. A future redesign should not blame the rule.

## Corrections applied

Addenda (original text kept) in `../c2_r002/HANDOFF.md` and `../c2_r002_independent/RESEARCH_DECISION.md`, plus status lines in `README.md` and the R4 standard. The STOP_THIS_BRANCH decision is unchanged and, if anything, strengthened: the local rule works as an approximate gradient method, but a matched linear baseline dominates on both quality and cost.

## Not run

The panel was not rerun (unnecessary: findings 1–3 change no reported number). The mutation probe was not rerun.

## Independence

A different model family (Claude) from the author and the first reviewer (Codex). It shares no context with the Codex sessions.
