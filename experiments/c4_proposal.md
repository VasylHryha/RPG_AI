# C4 proposal: base resonator, geometry ↔ mode closure (APPROVED 2026-10-01)

Status: **APPROVED** by the owner on 2026-10-01 (`docs/decisions/0001-deprecate-c3-approve-c4.md`) and registered as `experiments/c4_manifest.json` (experiment `geomind-c4-r4-001`). The manifest is authoritative; its `registered_changes_from_proposal` lists every change made while settling the design on development worlds. Authority: `GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md` (C4, the recursive unit interface, the invariants, §5–7).

## 1. The bounded question

> In the R4 position–phase element model, do label-free detected resonators form reproducibly, survive small perturbations, and depend causally on **both** coupling directions? Geometry→mode means a geometric intervention changes the mode as predicted; mode→geometry means a phase intervention changes the geometry as predicted. Each direction's effect must vanish when that direction is ablated.

Hypotheses: **H-M** (geometry and activity influence one another) and the C4 precursor of **H-C** (a stable structure exposes a reusable effective unit). C4 does **not** test hierarchy, task usefulness, novelty or efficiency.

**The cheap explanation, named up front.** Attraction/repulsion alone (J = 0, K = 0) also forms geometric clusters, with no modes at all. "Clusters formed" is therefore not evidence (R4 claim ledger: "attractive clusters alone"). Only two-way causality, with matched ablations, separates a resonator from a clump. These dynamics are known swarmalator behavior [R3]; reproducing their states is not novel, and C4 is a mechanism probe.

## 2. Model (R4 C4, unchanged)

`x_dot_i = mean_j[unit_ij·(A(1+J cos(θ_j−θ_i)) − B/max(r_ij,ε))]` and `θ_dot_i = ω_i + mean_j[K·w(r_ij)·sin(θ_j−θ_i)]`, with A = 1, B = 1, J = 0.8, K = 1, ε = 1e-6, w(r) = exp(−r²).

Proposed registration values (frozen before final seeds):

| Item | Proposal | Reason |
|---|---|---|
| Elements per world | N = 24 | Small and fast; several clusters possible |
| Initial positions | uniform in a disk of radius 3; phases uniform | Seeded; no planted groups |
| ω arms | (a) identical ω = 0, the synchronizing fixture; (b) heterogeneous ω ~ U[−0.5, 0.5] | (a) is the expected-positive control; (b) is the generic case |
| Neighbors | up to 8 nearest within radius 3, recomputed every step (charged) | Local and sparse; the mean is over the actual neighbor set |
| Integrator | fixed-step RK4, dt = 0.02, horizon T = 100 (5,000 steps) | Must pass a dt-halving convergence check |
| Boundary | open plane | Avoids periodic artifacts |
| Seeds | 10 development seeds per arm (settings and thresholds only); **20 fresh final seeds per arm**, never inspected before freezing | R4 §5.2 |

## 3. Label-free resonator detector (the candidate never sees fixture labels)

Over the persistence window (the last 30 time units), a group is a resonator only if all five R4 criteria hold. Threshold values are proposals, to be settled on development seeds and then frozen:

1. **Membership:** the connected component of the coupling graph (edge if r < 1.5 × median nearest spacing) has Jaccard similarity ≥ 0.95 between window start and end, with size ≥ 3.
2. **Shape:** normalized radius of gyration, coefficient of variation ≤ 0.05.
3. **Mode lock:** every within-group wrapped pairwise phase difference has standard deviation ≤ 0.1 rad. The pairwise pattern is reported; low ρ alone is never a rejection, so anti-phase groups are allowed.
4. **Reproducible signature:** the collective frequency (mean dθ/dt) differs by ≤ 0.01 between window halves, and the phase pattern by ≤ 0.1 rad up to global rotation.
5. **Recovery:** after perturbation (positions + N(0, 0.1·spacing), phases + N(0, 0.3 rad)), it returns within 30 time units to the same membership (Jaccard ≥ 0.9) and phase pattern (≤ 0.1 rad).

**Effective unit (ActiveUnit, upper-facing only):** X = centroid; L = radius of gyration; M_eff = (collective frequency, pairwise phase-offset pattern, coherence ρ); ports = boundary members (convex hull); S = stability margins of criteria 1–5, plus the error of predicting the unit's next-window X/L/M_eff from its own current values. Member lists stay owner-private.

## 4. Interventions, predictions and ablations (registered before final seeds)

Each intervention is applied to each detected resonator, against an unperturbed paired control run from the same state. Effects are paired differences across final seeds, reported with bootstrap 95% CIs.

| Test | Intervention | Registered prediction (direction) | Ablation where it must vanish |
|---|---|---|---|
| **G→M** | scale the group's geometry by 1.5 about its centroid, phases held | peak within-group phase-lock error in the next 5 time units **increases** (w(r) weakens) | w ≡ 1 among neighbors (distance-independent phase coupling) |
| **M→G** | randomize the group's phases, positions held | peak radius of gyration in the next 10 time units **increases** (cos term weakens attraction) | J = 0 (phase-blind motion) |
| Both off | — | — | J = 0 and w ≡ 1 |
| Cheap clump | — | clusters may still form | J = 0, K = 0 (attraction/repulsion only) |

## 5. Endpoints and verdict rules (all evaluated by the panel; no endpoint is test-only)

- **Formation:** the fraction of final seeds with ≥ 1 resonator, per arm (Wilson 95% CI). Registered expectation: ≥ 0.8 in the identical-ω arm.
- **Two-way causality:** for both G→M and M→G, the intact model's paired-effect CI excludes 0 in the predicted direction, **and** in the matching ablation the effect CI includes 0 or its mean is ≤ 20% of the intact mean.
- **Not a clump:** in the J = K = 0 control, the detector must reject the clusters on criteria 3 and 4, with no mode lock. If it accepts them, the detector is invalid and the run fails.
- **Effective-state validity:** the next-window prediction error of X, L and M_eff stays below a registered bound. It is reported as S.

**H-M verdicts:**
- **SUPPORTED_WITHIN_SCOPE** if formation ≥ 0.8 and both causality endpoints pass in the identical-ω arm;
- **NOT_SUPPORTED** if either causality endpoint fails clearly (intact CI includes 0, or the effect has the wrong direction);
- **INCONCLUSIVE** otherwise.

The heterogeneous arm is reported separately. Failure is a valid outcome.

## 6. Engineering and process (lessons from C1/C2 applied)

- **New files only:** `geomind/c4_*.py`, `geomind/run_c4.py`, `tests/test_c4.py` and `tools/c4_mutants.py`. Accepted C0–C2 files stay frozen.
- **Generic pipeline:** C4 is the first milestone on `tools/verify.py --milestone c4`, configured by the committed `milestones/c4.json` (dependencies, stage commands, mutants, `implementer_family`). The manifest `experiments/c4_manifest.json` must be committed before the panel runs; the pre-commit hook checks this.
- **Gate in the runner:** `run_c4.py` calls `tools/milestones.py` `check("c4", "panel")` itself.
- **Gated pipeline:** tests → smoke on non-panel seeds → parallel mutation probe → recorded panel, each run once. Estimated: tests under 30 s, panel about 5 min (to be measured; move to C++ only if measured cost warrants it).
- **Focused checks:**
  - a 2-element analytic case;
  - dt-halving convergence;
  - permutation equivariance and translation/rotation invariance;
  - the detector rejecting J = K = 0 clumps;
  - each ablation actually removing its coupling term;
  - the intervention leaving the "held" variables bit-identical;
  - no fixture-label access in the candidate.
- **Every registered check computed in the panel,** and anything skipped listed under checks not run (the C2 lesson).
- **Review:** one independent review by the other model family: if Claude implements, Codex reviews, or the reverse. 15-minute cap.

## 7. What C4 cannot show

No hierarchy (C5+), no task usefulness, no efficiency or energy claim, no novelty over swarmalator dynamics. A "formed" result without two-way causality is a clump, not an RRG resonator.

## Decisions for the owner

1. Approve the question, model values, detector thresholds (settled on development seeds), predictions and verdict rules, or name changes.
2. Who implements and who reviews (recommended: Claude implements, Codex reviews; or the reverse).
