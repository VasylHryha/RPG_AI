# C4 R002: handoff for the independent review

## Identity

| Field | Value |
|---|---|
| Implementer | Claude (claude-opus-5-5) |
| Reviewer | the other model family (Codex): one review, about 15–20 minutes |
| Experiment | `geomind-c4-r4-002`, registered in commit e8efb1d (`experiments/c4_manifest.json`) |
| Supersedes | R001, withdrawn before review (`docs/decisions/0002-c4-r002-supersedes-r001.md`; `evidence/c4_r001/` unchanged) |
| `results.json` SHA256 | `24a583ecc83a7efbfec3ea90966d99fa95c67937ae75c65e87d12559c1fb66d7` (quote it in the review) |
| Pipeline | `tools/verify.py --milestone c4`, one run, about 95 s, attested in `PIPELINE.json` |

The pipeline stages:

| Stage | Result |
|---|---|
| tests | 24 contracts in 5.2 s |
| smoke | development worlds, 7.9 s |
| mutation | 27/27 detected, 31.1 s |
| panel | 20 + 20 fresh final worlds, 51.3 s |

## Results (registered rules)

**Implementation gates: all PASS.** Status: **REVIEW_READY**.

**Numerical checks:**
- RK4 error ratio: 17.2–17.3 (order ≈ 4).
- Switching-limited dt error: ≤ 2.1e-3.
- Equivariance error: ≤ 1.1e-14.

### Identical-ω arm (primary)

| Endpoint | Result | Verdict |
|---|---|---|
| Formation | 17/20 = 0.85 (Wilson 95% CI [0.64, 0.95]) | PASS (point-estimate rule) |
| G→M | intact +0.0135 rad, CI [0.0122, 0.0149], n = 17; complete ablation 0 | PASS |
| M→G | intact +0.958 peak relative Rg, CI [0.82, 1.12], n = 17; J = 0 ablation 0 | PASS |
| Dose-response, G→M | 0.0057 → 0.0135 → 0.0389 (scale 1.25/1.5/2.0); high − low CI [0.025, 0.044] | PASS |
| Dose-response, M→G | 0.057 → 0.306 → 0.958 (RMS 0.5/1.0/uniform); high − low CI [0.76, 1.06] | PASS |
| Not a clump | 20/20 rejected, all by criterion 5 | PASS |
| Effective state | 33/33 units within bounds (worst position error 0.07 L) | PASS |

**G→M channels (descriptive):**
- With only w = 1, 43% of the effect remains (CI [−0.0001, 0.0144], wide).
- With only the frozen topology, 92% remains (CI [0.0116, 0.0134]).
- So on average the distance weight carries most of the effect, but neighbour choice matters strongly in a few worlds. This is the R001 residual, now measured instead of misattributed.

**Hypotheses:** H-M **SUPPORTED_WITHIN_SCOPE**, H-C precursor **SUPPORTED_WITHIN_SCOPE**.

### Heterogeneous-ω arm (reported separately)

| Endpoint | Result | Verdict |
|---|---|---|
| Formation | 4/20 (CI [0.08, 0.42]) | FAIL |
| Causality and dose-response | n = 4 < 10 | INCONCLUSIVE (point estimates in the predicted direction) |
| Effective state | 3/4 units within bounds | FAIL |

Hypotheses: H-M INCONCLUSIVE, H-C precursor NOT_SUPPORTED. **Note:** the clump control produced **no candidates** in this arm, so its "not a clump" PASS is vacuous there.

## Caveats the reviewer should weigh

1. **Formation rests on the point estimate.** It passes on 0.85 ≥ 0.8 (as registered), but the Wilson lower bound is 0.64.
2. **Complete ablations vanish by construction.** That checks the statistic, not the hypothesis. The evidence is the intact effects and their dose-response.
3. **R002 was designed after seeing R001's final-world result.** The decision record lists why. Judge whether the complete ablation and dose-response make a fair, non-rescuing test. R001's INCONCLUSIVE stays on record.
4. **The identical arm is a synchronizing fixture.** Its mode has frequency 0, and G→M is measured through the restoring rate of a probe kick.
5. **Scope.** This is known swarmalator dynamics: one N, one parameter set and one neighbour rule. It makes no novelty, hierarchy, task or efficiency claim.

## Where to push hardest

- `intervene` in `geomind/c4_experiment.py`: pairing of controls and treated runs per condition, the frozen topology taken from the unperturbed s0, and dose labels.
- **Recompute the endpoints** from `records`: `resonator_effects` hold every per-resonator value.
- **Seed separation:** smoke and tests use `development_entropy`; R002's final entropy is new.
