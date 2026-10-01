# C4 R001: handoff for the independent review

## Identity

| Field | Value |
|---|---|
| Implementer | Claude (claude-opus-5-5) |
| Reviewer | the other model family (Codex): one review, about 15–20 minutes |
| Experiment | `geomind-c4-r4-001`, registered in commit 4d820bd (`experiments/c4_manifest.json`) |
| `results.json` SHA256 | `0b476a705b16ccbbd1778e707f64c44f2731a5ef4c47d43a020ca5178518b6e5` (quote it in the review) |
| Pipeline | `tools/verify.py --milestone c4`, one run, about 91 s, attested in `PIPELINE.json` |

The pipeline stages:

| Stage | Result |
|---|---|
| tests | 23 contracts in 5.3 s |
| smoke | development worlds, 8.0 s |
| mutation | 21/21 detected, 24.6 s |
| panel | 20 + 20 final worlds, 53.2 s |

## Results (registered rules, no re-analysis)

**Implementation gates: all PASS** (contracts, complete panel, numerical checks, detector rejects clumps, endpoint coverage, source hashes stable). Status: **REVIEW_READY**.

**Numerical checks:**
- RK4 error ratio with held neighbour sets: 17.1 and 17.4 (order ≈ 4).
- Switching-limited full-model dt error: ≤ 1.3e-3.
- Equivariance error: ≤ 2e-14.

### Identical-ω arm (primary)

| Endpoint | Result | Verdict |
|---|---|---|
| Formation | 19/20 worlds (Wilson 95% CI [0.76, 0.99]) | PASS |
| M→G | intact +1.106 peak relative Rg, CI [0.88, 1.35]; J = 0 ablation exactly 0 | PASS |
| G→M | intact +0.0136 rad, CI [0.0120, 0.0153]; w ≡ 1 ablation mean 0.0044 (32% of intact), CI [0.0004, 0.0106] | INCONCLUSIVE |
| Not a clump | 20/20 clump candidates rejected, all by criterion 5 (recovery) | PASS |
| Effective state | 36/36 units within bounds (worst position error 0.18 L) | PASS |

The registered G→M rule needs the ablation CI to include 0 or the ablated mean to be ≤ 20% of intact, so it does not fully vanish. **Per-world detail:**
- In 17 of 19 worlds the ablated effect is ≤ 0.004.
- In worlds 0 and 18 it is 0.026 and 0.047, larger than their intact effects.
- The likely mechanism is neighbour selection: scaling a group changes which elements are neighbours, which w ≡ 1 does not remove. Both-off shows the same channel. **This mechanism is not verified.**

**Hypotheses (registered rules):** H-M **INCONCLUSIVE**, H-C precursor **INCONCLUSIVE**.

### Heterogeneous-ω arm (reported separately)

| Endpoint | Result | Verdict |
|---|---|---|
| Formation | 2/20 worlds (CI [0.03, 0.30]) | FAIL |
| M→G | n = 2 | PASS |
| G→M | n = 2 | INCONCLUSIVE |
| Effective state | 2/3 units within bounds | FAIL |

Hypotheses: H-M INCONCLUSIVE, H-C precursor NOT_SUPPORTED.

### Descriptive

**Formation from scratch under each ablation** (worlds with an accepted resonator):

| Ablation | Identical arm | Heterogeneous arm |
|---|---|---|
| J = 0 | 18 | 0 |
| w ≡ 1 | 19 | 8 |
| both off | 20 | 5 |

The identical arm forms locked groups without either coupling direction. This is why formation alone is not evidence; only the causal tests separate a resonator from a clump.

## Where to push hardest

1. **Design changes made after the proposal** (manifest `registered_changes_from_proposal`): are any of them post-hoc rescues?
2. **The G→M residual:** is it the neighbour-selection channel? Worlds 0 and 18 are the place to look.
3. **Detector validity:** the clump must be rejected for the right reason; with identical ω, frozen phases trivially pass criteria 3–4.
4. **Seed separation:** no final world was simulated before the panel. Smoke and tests use `development_entropy`, and a test checks it.
5. **Recompute the endpoints** from `records`: the per-world effects are stored. Check the bootstrap and Wilson CIs.

## Next decision (after review, owner's call)

A cleaner G→M ablation would freeze the phase-coupling neighbour topology as well as setting w ≡ 1. It would need a new revision (R002) with fresh seeds; it must not be a re-analysis of R001.
