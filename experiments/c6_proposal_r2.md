# C6 revision 2: the loop repeats at the next scale

Draft for owner approval; no registration or runs authorized yet. Current milestone status is in `STATUS.json`.
This proposal supersedes revision 1's operational plan; its evidence, decisions and reviews remain history.
Authority: the owner's instruction, R4 C6 and recursive invariants, locked core §§3–8, and decisions 0007–0008 (D2–D8).
Correction and audit: `docs/decisions/0010-c6-principle-correction.md`, `docs/reviews/c6_principle_audit_codex.md`.

## Question and requirements

**Frequency → geometry → frequency → geometry**, repeated at a bigger or different scale.
A resonator is the product of a closed loop. Test two successive turns in this model: C4 units → level 2 → level 3.
Re-measure both transitions on fresh worlds: C5 established one transition's closure, but its prediction was inconclusive.
Level 1 = C4 unit (R₀), level 2 = R₁, level 3 = R₂; transition n means level n−1 → n.

| Requirement | Source | Measurement at both transitions unless stated |
|---|---|---|
| Earn both promotions | Loop repeats; R4 C6, invariant 4; D3 | Same C5 criteria 1–5: membership, shape, lock, signature and recovery of the original group. Formation PASS needs Wilson 95% lower bound ≥0.5: at least 27/40 worlds per level. |
| Stand on live direct parts | Owner's principle/A3; locked §5; R4 invariant 2 | Criterion 6 tests **direct parts only**: own criteria 2–4 in complete own-level windows, and sibling overlap ≤0.2 of each part's union-of-hulls area. Area ≤10⁻¹² L² cannot certify distinctness. Deeper validity is retained as a diagnostic and cannot veto the parent. All elements keep evolving. |
| Close the loop causally | Loop itself; R4 C4/C6 and invariant 3 | Rigid centroid moves change mode; rigid phase kicks change geometry. Complete ablations: w=1 with frozen phase topology for G→M; J=0 for M→G. Keep the approved dose ladders and matched controls. |
| Use one procedure | R4 C6/invariant 1; D7 | One detector, promotion, composition and effective-model recipe at both levels; same coupling and edge birth/death procedure, scaled by measured quantities. No parent labels reach the detector and no level gets a handcrafted solver or threshold. |
| Transmit up and down | R4 C6/invariant 3 | Whole-part pulse reaches other parts (`emergent_transfer`); boundary phase offsets differ from decoupled parts (`downward_effect`). At level 3, also pulse one level-1 unit and read the other level-2 summaries (`upward_transfer_l3`). Each effect uses the approved 0.01-rad margin. |
| Publish an effective unit | R4 interface/invariants 6, 8; D2 | One finite, valid state per accepted candidate per world, with matching S and digest. Publish measured isolated rate and sibling-folded capacities. Retain C5 state bounds: position 0.25 L, relative size 0.05, frequency 0.01/C_n; ≥90% of parents within all bounds. |
| Predict from summaries | R4 C6 held-out full/coarse comparison; D4, D8 | At level 3 the predictor reads level-2 states/ports only. Pulse and push must separately beat no transfer, rigid transfer and channel-matched relaxation, and meet r≤0.5 as defined below; repeat at transition 2. |
| Carry prediction validity | R4 invariant 8 | Apply C5's port-link/phase-basin validity rule to reconstructed published states for either recipe; report flags. Separate service reopens from current owner publications and resumes the same recipe. Score open-loop prediction with no later full-state inputs; report response, frequency/recovery error and work. |
| Verify the chosen engine | D6; R4 numerical/evidence discipline | Reuse pinned C++ engine and frozen NumPy reference; four existing equivalence checks, declared numerical tolerances and symmetry/decoupling checks. The pin is local, not a hermetic environment. |

These are operational tests of this model, not definitions of RRG. The element law is a design choice.
Same-law closure and scale separation retain separate verdicts as R4/0007 require; neither enters H-C.
Drop alternative-grouping specificity, its diffusion/compactness diagnostics, flat-depth/decomposition/compression endpoints,
the C5-relative fidelity superiority gate, the C₂ proximity-to-C5 gate and the additional overlap-calibration veto.
The loop, direct-part checks and bounded prediction supply the required evidence without those extra conditions.

## Fixed protocol and normalization ledger

Keep the existing C4 element law, dt=0.02, k=8, radius=3, five input parts per world, minimum candidate size three,
and C4 templates of 6–16 elements. Harvest label-free, re-accept templates alone and isolate source worlds at both transitions.
Use `c6_compose.assemble` at both levels: random rigid rotation/phase and bracketed contact placement, gap 0.6 within 10⁻⁶.
Keep internal rates; one constant shift per part gives an isolated rate drawn from U[−0.096/C_n, 0.096/C_n].
These retained fixtures implement the approved model; none is a physical constraint on the principle.

| Quantity / level | Normalization and retained rule |
|---|---|
| Candidate n: window, sampling, recovery, frequency | `c5_detect.level2_thresholds(C4 detector, C_n)`: times ×C_n, frequency tolerance ÷C_n; dimensionless shape/lock/pattern/Jaccard/link cuts unchanged. |
| Direct part k: criterion 6 | W=max(30 C_n, largest direct-part 30 C_k); own windows 30 C_k at interval C_k; ≥1 complete window, otherwise insufficient observation fails. Geometry at parent frames throughout W. Formation horizon max(100 C_n, W); deeper diagnostics do not lengthen or veto required observations. |
| τ at each level | Alone for normalization; intact world for channel-matched baseline. E-fold estimator over 10 C_n at 0.1 C_n. Phase kick RMS 0.3; position calibration s=1.25. Censoring is a bound, never a point estimate. |
| C_n | Isolated median τ_n / isolated median τ₁; ≥5 measurements each, <50% censored; censored values +∞ in medians. Round cumulative C_n to 0.2, ties up; require a positive finite result, otherwise undefined; C₁=1. No ordering or C5-proximity requirement. |
| Causal interventions / candidate n | G→M scales 1.1/1.25/1.5 with RMS-0.3 phase probe; M→G RMS 0.5/1/1.5; primary 1.25 and 1. Times scale with C_n as in C5. |
| Excitation / direct part | Pulse 0.5 rad; radial rigid push 0.2 L_part. Observe 10 C_n every 0.1 C_n. |
| Prediction error / responding parts | Linear arithmetic means of member paired displacement and unwrapped phase responses, computed by evaluator; error = RMS wrapped phase residual + RMS displacement residual/L_part, excluding the excited part. Same summary rule for both recipes/transitions. |
| r / responding parts | error_model/error_no-transfer; response floor 0.01. Below-floor cases stay in gains, are counted and excluded only from r. World mean over eligible excitations; ≥10 eligible worlds per type. |
| E2 / published parts and candidate n | Fixed-topology E1 Jacobian at t₀, steps 10⁻⁴ L_part and 10⁻⁴ rad; compare J̃=C_n D J D⁻¹, D positions=1/L_part, phases=1. Frobenius difference ≤10⁻³ max(norm(J̃_half),1). General matrix exponential; failed convergence predicts zero response. |
| Up/down, isolated publication, deeper diagnostics | Owner/evaluator reads lower state to apply rigid interventions, measure rates, expose ports and score truth. Detector gets summaries/validity; composition gets child summaries; upper prediction gets no descendants. |

E1=`c5_coarse.run`; E2=existing summary-derived linear response. V1=hull ports; V2=hull plus active-contact ports.
Choose one E1/E2 × V1/V2 combination by largest worst-cell development mean gain across both transitions (lexically greatest name on ties),
excluding E2 combinations with >50% abstaining groups at either transition; register that same combination at both levels.
Censored relaxation uses existing certified continuous-domain error bounds (65 inverse-τ points plus Lipschitz margin):
lower gain for PASS/readiness, upper gain for FAIL. No calibration is fitted on scored excitations.

## Endpoints and verdicts

The world is the independent unit; average its accepted groups. Bootstrap 95% CIs use 10,000 resamples; individual intervals are nominal.
Below 10 formed worlds, inferential endpoints are INCONCLUSIVE; formation is still measured on all 40 worlds.

| Endpoint, each at n=2,3 unless stated | Ordered rule |
|---|---|
| `formation_lN` | PASS if Wilson lower ≥0.5; FAIL if upper <0.5; otherwise INCONCLUSIVE. |
| `g_to_m_lN`, `m_to_g_lN` | After minimum: FAIL if intact CI includes/below zero; PASS if intact CI >0 and complete-ablation CI includes zero or abs(mean)≤0.2×intact mean; otherwise INCONCLUSIVE. |
| `dose_response_lN` | Each direction: PASS if means nondecreasing and high−low CI >0; FAIL if CI <0; otherwise INCONCLUSIVE. Both must pass; either failure fails endpoint. |
| `parts_alive_lN` | Every promoted parent's direct parts satisfy criterion 6; failures reject promotion. Store direct and diagnostic deeper records for rejected candidates too. |
| `downward_effect_lN`, `emergent_transfer_lN`, `upward_transfer_l3` | After minimum: PASS if CI lower >0.01; FAIL if upper <0.01; otherwise INCONCLUSIVE. |
| `effective_state_lN` | After minimum: PASS if ≥90% of published parents meet every bound; FAIL otherwise (no parents: INCONCLUSIVE). |
| `coarse_vs_full_lN` | INCONCLUSIVE below minimum formed/eligible worlds; FAIL if any gain CI upper <0 or either r CI lower >0.5; PASS if all six gain CI lowers >0 and both r CI uppers ≤0.5; otherwise INCONCLUSIVE. |
| `same_law_closure_lN` | E1 with selected ports, same prediction scoring; optional extension, outside H-C. |
| `scale_separation_lN` | Ratio isolated parent τ / mean isolated direct-part τ. Lower bound=0 if any denominator censored, else numerator lower/denominator; upper=∞ if numerator censored, else numerator/denominator lower. After minimum: PASS if mean lower-bound CI lower >1; FAIL if mean upper-bound CI upper <1; otherwise INCONCLUSIVE. Report size and formation time, censored at actual horizon. |

Gates: used pools valid alone; harvest source isolation; same procedure/scaling; backend/numerical checks; `level_interface`;
and non-vacuous decoupled drifting/static controls (`not_independent_lN`, `not_a_clump_lN`), with imposed candidates.
Static controls shift each whole part's isolated rate to zero, preserving its internal rate differences.
Every registered endpoint is evaluated with value/verdict or `not_run` with reason; receipt also preserves raw values, settings, hashes, seeds and costs.
H-M_n: NOT_SUPPORTED if any causal/dose endpoint FAILs; SUPPORTED_WITHIN_SCOPE if formation and all three PASS; otherwise INCONCLUSIVE.
H-C_n: NOT_SUPPORTED if formation Wilson upper <0.25 or a required transfer/effective-state/prediction endpoint FAILs;
SUPPORTED_WITHIN_SCOPE only with supported H-M_n, live direct parts and all required composition endpoints PASS; otherwise INCONCLUSIVE.
Overall H-C: either transition NOT_SUPPORTED → NOT_SUPPORTED; both supported → SUPPORTED_WITHIN_SCOPE; otherwise INCONCLUSIVE.
A gate failure prevents REVIEW_READY; hypothesis failure alone is an honest outcome, not an implementation failure.

## Execution after approval and stops

Codex drafts/implements; Claude independently reviews committed evidence once, within 20 minutes (D5).
After approval: finish changes listed in the audit, run everyday tests, then the development gate with **new development purposes**.
Keep the old receipt unchanged. Check 4 first (10 level-2, 5 level-3 worlds; harvest inputs only), then two formation passes,
30 worlds per level each: provisional C₂=3.2/C₃=9.6; measure isolated factors and check availability **before** pass 2 (A1).
Pass 2 uses measured factors/new purposes; later factor changes are reported, not iterated. Then readiness and runtime projection.
Development readiness requires ≥10 groups and ≥10 r-eligible groups/type/transition, every selected mean gain >0,
each mean r≤0.5 and ≤10% censored channel calibrations. Pass-2 formation target remains ≥0.75 (0008 D3).

| Yes/no stop condition | One action | Responsible role |
|---|---|---|
| Proposal unapproved? | Await owner decision | Drafter |
| Approved protocol cannot be implemented, or needs an outcome-driven change? | Return to owner | Implementer |
| Compiler/flags, equivalence or required numerical check fails? | Return to owner | Implementer |
| Required isolated factor undefined before pass 2? | Return to owner | Implementer |
| Pass-2 formation target or prediction readiness fails? | Return to owner | Implementer |
| Panel projection unknown or >3 h on eight processes (retained 0008 budget)? | Return to owner | Implementer |
| Pipeline stage/gate fails? | Report failure to owner; await decision | Implementer |
| Design defect found after recording? | Withdraw through a new decision record; preserve receipt | Implementer |
| Independent review requires changes? | Report verdict to owner | Reviewer |

Tell the owner the expected duration and basis before each long run. The old gate stopped after about 18 minutes;
revision-2 total gate/panel time is unknown until the changed workload is measured. Do not promise an hour-long panel.
After the development gate passes: commit registration on fresh final entropy, 40 fresh worlds per level with isolated upstream sources;
complete panel code/tests before the long run; runner calls `check("c6","panel")`; verify once via `tools/verify.py`, commit evidence, review once.
Resumption skips only stages verified for identical dependencies. No rehearsal panel, direct mutation run or receipt rewrite.
Scope: one model, staged assembly, two transitions and rate fixtures. Usefulness/efficiency belongs to C8; dissolution/reform to C7.

## Drafter self-audit

Codex owns this revision. Cause of the main defect: recursive bookkeeping was promoted into a requirement that deeper identities survive;
fix: direct-part criterion 6 only (owner/A3), with fresh evaluation after approval. Cause of expansion: optional comparisons and physical examples
became gates; fix: remove them, retaining explicit R4 tests and owner decisions. The earlier lean draft also omitted effective-state/validity rules,
censor handling and stop ownership; restored here from R4 and the existing executable protocol. No project experiments or tests run while drafting.
