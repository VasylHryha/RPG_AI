CHANGES_REQUIRED
Reviewer family: Codex
Reviewer model: gpt-6
Rechecked proposal commit: 290b414
Proposal SHA-256: 70160b0532a0dcfbfcee16016e0f1214a106e1eacfa67b0db0ddb5b75518244f
Original critique SHA-256: 6d2172623eac1c5675728e259eac52794988f02a19755b36f2a407bc803bfec7

Date: 2026-10-02. Short, time-boxed follow-up to `docs/reviews/c6_proposal_critique_codex.md` at 03a6a28, which reviewed 6660692. Both supplied hashes match the current files. Scope is the amendments in `git diff 6660692 290b414 -- experiments/c6_proposal.md`, their necessary context, and the seventh self-audit; this is not another full design review. Locations below are lines of the amended proposal.

The owner decides D1 and D8. I assess the proposed D8 ceiling as a rule, without accepting or rejecting its numerical value. Claude owns the remaining proposal fixes and must record their causes in the self-audit. This report neither authorizes implementation nor changes milestone status.

| finding | status | location | evidence |
|---|---|---|---|
| F14 | PARTIALLY_RESOLVED | §5:283–296; §10:556–563 | Uniform lower-level probes remove the original real-part excitation alignment, but circular summaries with a rigid paired decoder still admit positive specificity in a flat system, as the counterexample below shows. |
| F1 | RESOLVED | §3:95–100; §5:281 | A new wrapper calls the frozen dictionary-producing constructor read-only and assigns its measured isolated rate to `natural_rate` identically for real and fake level-1 parts, with a 30 C₁ estimator and field-routing contract. |
| F3 | RESOLVED | §5:288–293; ledger:195 | Identity-linked element offsets now belong exclusively to the evaluator, remain fixed at t₀, and are used for paired responses without being exposed to the predictor. |
| F4 | RESOLVED | §4:248–255 | The maximum horizon supplies at least one complete 30 C_k window for every descendant level, and INSUFFICIENT_OBSERVATION explicitly fails without imposing C_n ≥ C_k. |
| F5 | PARTIALLY_RESOLVED | §7:353–358; §8:399; §9:466–469; D8:757–760 | The six gains plus a response-normalized ceiling define an additional bounded-error rule with world aggregation and CI directions, conditional on D8, but a zero or very small no-transfer response has no registered handling. |
| F7 | RESOLVED | §3:158–165; §8:402 | The estimator, median aggregation and rounding are explicit, and ρ_lo ≤ ρ ≤ ρ_hi gives conservative support in both directions, with censored numerator infinity explicitly preventing FAIL; the separate baseline-use omission found in the self-audit is N5. |
| F8 | PARTIALLY_RESOLVED | §7:335–341; §9:465 | Steps, reference, general matrix exponential and no-response abstention scoring make E2 executable, but the new raw Frobenius convergence test mixes dimensional blocks and needs the normalization in N2 below. |
| F9 | RESOLVED | §9:470–474; stop rule 6:688 | Calibration retains every contacting input-template pair independently of parent acceptance, defines intactness through dynamic criteria alone, and stops on an empty population. |
| F10 | RESOLVED | §10:520–526; stop rule 9:691 | Resumption now skips only stages verified for identical code and follows fingerprint invalidation after edits, while native preflight and registered timeouts are explicit shared-tool engineering requirements. |
| F11 | RESOLVED | §3:134–136; ledger:191 | Contact placement now brackets and bisects to the stated element-scale tolerance and records deterministic seeded retries for a missed approach. |
| F12 | RESOLVED | §8:430–434; §9:464 | Individual intervals are nominal, H-C is an intersection-union requirement, and selected development gains are explicitly selection-biased readiness measurements. |
| F15 | RESOLVED | §4:262 | The amendment describes the window measurements as non-nested, preserves C5's registered verdicts, and bases C6 on fresh evidence. |
| §G: compiler pin | RESOLVED | §10:619 | The compiler/flag check is explicitly local rather than hermetic, with unchanged-identification SDK/libm drift stated as a remaining limitation. |
| §G: check 4 scope | RESOLVED | §10:630 | The claim is restricted to 15 prespecified development worlds, forbids discarding failures, and disclaims proof for every future verdict. |

## Remaining F14: a concrete paired-response flat null

The probe sites themselves are independent of the real/fake partition: drawing four uniform sub-parts before constructing alternatives gives the uniform-site expectation below. At transition 2 those sub-parts are individual elements. The statement at line 285 that membership in one part makes every grouping equally aligned is stronger than that fact warrants: a circular summary's response also depends on the phase distribution within the part.

Use nine elements with completely flat, all-to-all arithmetic phase consensus, whose exact solution is

```text
θ_i(t) = mean(θ(0)) + exp(-t) [θ_i(0) - mean(θ(0))].
```

There are no privileged dynamical units. Use initial phases `(-2,-2,-2,0,0,0,2,2,2)` radians, real triples `{0,1,2}`, `{3,4,5}`, `{6,7,8}`, and mixed triples `{0,3,6}`, `{1,4,7}`, `{2,5,8}`. On a complete contact graph every triple is contiguous; the mixed triples preserve sizes and mix real parts. There are 36 distinct partitions with one member from each real triple, so K=20 need not duplicate alternatives. All give the same uniform-site expectation. The initial mixed circular resultant is nonzero: `(1 + 2 cos(2))/3 ≈ 0.055902`.

For each possible probe p, pulse only p by a=0.5. Write q=exp(-t). The exact full paired response is

```text
Δθ_i(t) = a(1-q)/9 + a q 1[i=p].
```

Give each partition an oracle for its exact circular part phases on both branches. With one shared fixed offset set, the lifted paired response of each element is its part's circular-phase difference; offsets cancel, but the nonlinear circular means do not become arithmetic means. Score RMS wrapped phase on the same eight directly unexcited elements. Averaging uniformly over all nine p gives:

| time | real error | mixed error | mixed minus real |
|---|---|---|---|
| 0.1 | 0.0748215916681 | 0.302623927450 | +0.227802335782 |
| 1 | 0.0306180955509 | 0.0305884832867 | −0.0000296122642 |

Across the 10 C_n window at C_n=3.2 and samples every 0.1 C_n, computing each probe's temporal RMS and then averaging over sites yields positive specificity `0.0524725355535` rad. Excluding t₀ still gives `0.000839372807650` rad. Averaging frame RMS instead also remains positive (`0.00547966475867`, or `0.0000408428215969` without t₀). Thus this is not solely a scoring-at-t₀ artifact. Independent position consensus gives partition-invariant position error, so adding a grouping-independent push channel dilutes rather than cancels the positive pulse expectation.

If instead the intended decoder uses separately frozen excited/control offsets at t₀, the unexcited-element prediction is `ΔΘ_part(t) - ΔΘ_part(0)`. The same fixture then gives positive per-probe temporal-RMS specificity `0.548431258604` rad. Pin the convention, but neither interpretation alone removes this residual bias.

This is an analytic challenge to the claimed flat-null property and the decoder, using exact summaries to isolate their effect. It is not an E1/E2 simulation, a C4 world, or a prediction of the C6 panel verdict. Paired scoring removes baseline offset drift common to both branches; it does not remove probe-induced internal response that differs between partitions. An equal-initial-phase null alone would miss this case.

**Smallest fix:** specify a null-corrected specificity statistic or another evaluator-side response decoder that passes this heterogeneous-phase flat null as well as the homogeneous null; pin the offset convention, null population and binary chance criterion, and retain the modular positive fixture. A contract saying that the existing statistic must be zero does not provide the missing correction. **Blocks approval: yes.**

## New amendment findings, ranked

### N1 — High: the new normalized-error ratio has an undefined domain

**Location:** §7:356; §8:399; §9:468; D8:757; ledger §3a:176–199.

**Defect:** No rule defines r when `error_no-transfer = 0`, nor handling below numerical response resolution; the new ratio and its threshold are also missing from the normalization ledger. A strictly positive denominator, however small, defines a mathematical ratio: the near-zero concern is numerical robustness and interpretation, not algebraic undefinedness.

**Failure scenario:** An excitation induces no response in the scored non-excited parts and both predictors correctly predict zero: r=0/0, so neither the CI nor its ordered verdict conditions are defined. A response below numerical resolution produces unstable ratios even with finite model errors. The separate mean transfer endpoint does not ensure that every scored pulse and push has a nonzero denominator.

**Smallest fix:** register a denominator-domain rule; one sufficient option is a positive minimum response size in the same dimensionless phase-plus-position metric with an explicit outcome below it. Specify its effect on world aggregation, the ten-world minimum and readiness; add r, any response floor and the owner-selected ceiling to the ledger. Do not silently drop low-response cases or add an unregistered epsilon. The drafter and owner choose the treatment; this review does not require a particular floor value. **Blocks approval: yes.**

D8 addresses F5's substantive baseline-dominance gap: if denominators are defined, a ceiling on the CI of mean r prevents arbitrarily poor prediction relative to the observed response despite positive gains. Its proposed value 0.5 is an owner decision. This is a bound on mean response-normalized error, not a per-excitation guarantee or a bound in raw physical units. Readiness uses the point mean, final evidence the CI, as explicitly stated.

### N2 — Medium: E2 convergence is tested in mixed physical coordinates

**Location:** §7:337–338; ledger §3a:193.

**Defect:** Size-normalized finite-difference steps do not normalize a raw Jacobian Frobenius norm over position and phase coordinates. Its blocks have different units; the relative discrepancy can depend on length units and part size. The ledger does not state a dimensionless coordinate/norm definition for this new check.

**Failure scenario:** In a two-coordinate position/phase illustration, take `J_h=[[1,1],[0,1]]` and `J_(h/2)=[[1,1.01],[0,1]]`. The relative discrepancy is about 0.00577, so the 0.001 rule abstains. Rescale the position coordinate to `x'=0.01x`: with `D=diag(0.01,1)`, both Jacobians become `D J D^-1`, and the relative discrepancy is about 0.0000707, so the same comparison passes. The discrepancy remains below/above the threshold regardless of choosing either reference norm. This is a dimensional counterexample, not a claim that these matrices occur in C4.

**Smallest fix:** define the convergence comparison on the Jacobian in registered dimensionless coordinates (position normalized by the participating part's own L, phase dimensionless, and the declared time normalization), state the denominator and zero-norm convention, and put the steps and norm in the ledger. Keep no-response abstention and the general matrix exponential. **Blocks approval: yes, as an invariant-1 normalization defect.**

### N5 — Medium: censored relaxation calibration has no baseline prediction rule

**Location:** §3:156,158–161; ledger §3a:186; §7:363; named helper `geomind/c5_experiment.py:351–355`.

**Defect:** The new finite-horizon estimator covers the in-world relaxation calibration as well as isolated normalization, but specifies only a censored record and never the prediction to use when the baseline's τ is censored. The bound-only ratio rules in §8 apply to scale separation, not to this baseline.

**Failure scenario:** Isolated development medians are finite, so the timescale gate passes, but one intact push calibration never reaches its e-fold within 10 C_n. The frozen relaxation helper requires a numerical τ for `1-exp(-t/τ)`. Replacing the censored time by its horizon imputes an unobserved point value; replacing it by infinity predicts no response and can weaken the required strongest baseline. Neither policy is registered. A recorded string such as `> 10 C_n` cannot be passed to the helper.

**Smallest fix:** register one deterministic baseline-use policy for censored channel calibration, with its endpoint/readiness action; alternatively stop before scoring that case under an explicit rule. Preserve the raw censor record and do not infer an exact τ from its limit. **Blocks approval: yes, as an incomplete scored-baseline recipe.**

### N6 — Medium: the new element-level push lacks a primitive length definition

**Location:** §5:280,284; ledger §3a:189,195; R4's primitive `Element` and `ActiveUnit` definitions; `geomind/c4_detect.py:75–76`.

**Defect:** At transition 2 a specificity sub-part is a single primitive element, yet its new push is 0.2 times its own L. No positive primitive L is defined in the proposal or selected element state; the existing radius-of-gyration size of a singleton is zero. This ambiguity was introduced by moving the probe from resonator parts to elements.

**Failure scenario:** Reusing the named size helper gives L=0 for an individual element, so every transition-2 specificity push is a zero intervention and contributes no discrimination. Choosing a parent's L would instead refer to the grouping the probe is required to ignore. Choosing element spacing or a fixed microscopic size can work, but neither is the written definition of this probe's L.

**Smallest fix:** define and register a grouping-independent positive primitive characteristic length, or a grouping-independent element-scale push convention, and state its normalization in the ledger. The drafter must supply the definition; the implementation should not invent it. **Blocks approval: yes, for the claimed two-type specificity recipe as written.**

### N3 — Low: formation-time censoring still names the replaced horizon

**Location:** §4:252 versus ledger §3a:197 and §5:300.

**Defect:** The new maximum formation horizon conflicts with the old statement that formation time is censored at 100 C_n and that this is the entire horizon.

**Failure scenario:** With C₃=0.4 and C₂=6.4, the new horizon is 192, whereas 100 C₃ is 40; a parent forming at 100 can persist throughout the final 12-unit parent window and be accepted, yet its formation lies beyond the old descriptive censoring limit. The internal parts can remain valid throughout their own 192-unit observation. No required timescale ordering forbids this example.

**Smallest fix:** update the descriptive formation-time rows to the actual maximum horizon, or explicitly register a separate descriptive censoring window and disclose it. **Blocks approval: no by itself; correct before implementation.**

### N4 — Low: the new median-availability stop has a stale rule reference

**Location:** §3:162–163 and §9:461 versus stop rule 2, §12:684.

**Defect:** The new definition sends censoring of either τ_n or τ₁ to stop rule 2, whose yes/no condition still checks only whether a majority of τ₃ is finite.

**Failure scenario:** Half the development level-1 τ values are censored while a majority of τ₃ values are finite; §3 says to stop because C_n is undefined, but the referenced binary condition is false.

**Smallest fix:** extend that condition to every required development median, including τ₁ and τ₂, and to the stated fewer-than-50%-censored requirement. **Blocks approval: no by itself, because §3 already says to stop; reconcile the written row before implementation.**

## Commands and execution scope

Read-only inspection used these commands and narrowed range/search variants:

```text
pwd
git status --short
git log -4 --oneline
git diff 6660692 290b414 -- experiments/c6_proposal.md
shasum -a 256 experiments/c6_proposal.md docs/reviews/c6_proposal_critique_codex.md
cat AGENTS.md
sed -n '1,205p' docs/reviews/c6_proposal_critique_codex.md
nl -ba experiments/c6_proposal.md
rg -n ... experiments/c6_proposal.md GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md
sed -n '125,170p' geomind/c5_units.py
sed -n '1,130p' geomind/c5_coarse.py
cat .githooks/pre-commit .githooks/commit-msg
git config core.hooksPath
mkdir -p /private/tmp/c6-proposal-recheck
python3 -B /private/tmp/c6-proposal-recheck/flat_null.py
shasum -a 256 /private/tmp/c6-proposal-recheck/flat_null.py
```

Three additional `python3 -B -c` variants evaluated the same closed-form script: initial phase magnitudes 1.4 and 1.6, and separately frozen branch offsets. The final script includes both offset conventions. Probe SHA-256: `6c76ed9f9835042bf2a10af95624f4ee1b23bb5aab67c6e86d75b8c6a4888711`. It uses only Python's standard-library `math` and `cmath`, directly evaluates a closed-form formula and draws no random values. It imports no project modules, executes no project functions and integrates no dynamics.

A quick external memory-registry search for `GeoMind|ai_RPG_test|c6_proposal` returned no matches; no memory-derived fact was used.

The only repository write is this new review. Scoped commit and verification commands:

```text
git add -- docs/reviews/c6_proposal_recheck_codex.md
git diff --cached --check
git diff --cached --stat
git commit -m "Recheck C6 proposal amendments independently" -m "Assisted-by: Codex:gpt-6"
git show --stat --oneline HEAD
git status --short
shasum -a 256 experiments/c6_proposal.md docs/reviews/c6_proposal_critique_codex.md
```

Existing pre-commit/provenance hooks run normally; none are bypassed. No simulations were run and no seeds were drawn or used. No pytest suite, panel, smoke run, mutation probe, design gate, C0 experiment or verification pipeline was run. No proposal, original critique, code, manifest, STATUS.json, evidence receipt or `.gate/` artifact was edited.

## Owner-requested self-audit of this recheck (2026-10-02)

The owner asked to check the review itself for issues, conflicts and gaps. This is an amendment of the same report, not a second independent proposal review. Verdict remains CHANGES_REQUIRED. No numeric quality score is assigned under AGENTS.md.

Corrections to my report:

- N1 now distinguishes the undefined zero-denominator case from numerical fragility of a strictly positive denominator and presents a registered response floor as one sufficient remedy rather than the only permissible remedy.
- N2 corrects the coordinate-unit wording and uses `J_(h/2)` to avoid confusing the half-step Jacobian with division of a matrix by two.
- N3 replaces my weak formation-at-180 example: with the original C₃=1.6, the parent would lack a full final 48-unit persistence window. The new C₃=0.4 example leaves ample parent persistence time and demonstrates the actual horizon conflict without that flaw.
- N5 and N6 add amendment gaps I missed: censored baseline use and the primitive length required by the new element push.

I independently re-derived the flat calculation using a complex-resultant ratio, enumerated all 36 balanced alternatives, and checked every possible single-element probe without drawing seeds. At C_n=3.2, the mean per-probe temporal-RMS differences are:

| initial phase magnitude | shared offsets | separately fixed branch offsets |
|---|---|---|
| 0 (homogeneous negative control) | 0 to floating-point precision | 0 |
| 1.6 | +0.00574235984089 | +0.0665993808741 |
| 2 | +0.0524725355535 | +0.548431258604 |

Every balanced alternative gives the same uniform-site expectation. The 1.6-rad fixture has a larger initial circular resultant, approximately 0.313867; the residual does not require an almost-zero resultant. The 2-rad results independently reproduce the original numerical claims. The oracle calculation establishes a decoder/statistic vulnerability; it does not establish the sign of an unrun E1/E2 C4 experiment. F14 retains that explicit scope.

I also checked both candidate reference denominators in the Jacobian norm example and exhaustively checked 216 positive-time/censor combinations: the bound formula satisfies `ρ_lo ≤ ρ ≤ ρ_hi` in every case. This verifies the deterministic censor algebra, not empirical bootstrap coverage or a population inference beyond the proposal's nominal intervals. F7's bound-direction resolution stands; N5 concerns a different use of censored times.

The independent audit script is `/private/tmp/c6-proposal-recheck/self_audit.py`, SHA-256 `3f73ed297729cf94c851cdcd124758d5007a67715254d9abb5ece6ef481f8d3a`. It uses only `cmath`, `itertools` and `math`, evaluates closed-form formulas, and neither imports project code nor integrates dynamics. Additional reads inspected `response_error`, `relaxation_prediction`, `efold`, `radius_of_gyration`, the R4 primitive interface, the proposal's changed sections and the original diff. Commands included:

```text
git status --short
git log -3 --oneline
cat docs/reviews/c6_proposal_recheck_codex.md
sed -n '1,100p' /private/tmp/c6-proposal-recheck/flat_null.py
git diff 6660692 290b414 -- experiments/c6_proposal.md
nl -ba experiments/c6_proposal.md
rg -n ... experiments/c6_proposal.md GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md geomind/c4_detect.py geomind/c5_units.py geomind/c5_experiment.py docs/PROCESS_REVIEW.md
sed -n '340,358p' geomind/c5_experiment.py
sed -n '460,490p' geomind/c5_experiment.py
sed -n '70,81p' geomind/c4_detect.py
sed -n '225,268p' GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md
python3 -B /private/tmp/c6-proposal-recheck/self_audit.py
shasum -a 256 /private/tmp/c6-proposal-recheck/self_audit.py
git add -- docs/reviews/c6_proposal_recheck_codex.md
git diff --cached --check
git diff --cached --stat
git commit -m "Audit and strengthen C6 proposal recheck" -m "Assisted-by: Codex:gpt-6"
git show --stat --oneline HEAD
git status --short
shasum -a 256 experiments/c6_proposal.md docs/reviews/c6_proposal_critique_codex.md
```

Only this recheck report is amended. Hooks run normally. No simulations, seeds, project tests, design gate or pipeline are used in this self-audit. Claude still owns the proposal fixes, and the owner still decides approval and D8.
