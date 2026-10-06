CHANGES_REQUIRED

Reviewer family: Codex
Reviewer model: GPT-6
Reviewed commit: a843d6ec9b874aa1c98bcfbd699df6e6c7696edf
Reviewed amendments: a253674 and a843d6e
Design SHA256: ba72e65b804006954cf21558be15380ce9c131428919c14e2275d394053690a5
Design: evidence/tactical_composition_demo/DESIGN_0G.md, sections 18 and 18.1

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Cross-family review of Claude's revised design. Read AGENTS.md first. Inputs inspected: DESIGN_0G sections 3–5 and 13–18.1, inherited normalization/group/pressure rules, both section-17 Codex reviews and the first section-18 review; S4_V5_DEVELOPMENT_REPORT.md, S4_V5_TRACE_DIAGNOSTIC.md, SUMMARY.json, SUPPLEMENT.json, FINAL_VERIFICATION.json and all 60 compact fight summaries; native controller, factory, host, bridge, damage and ability paths; s4_v5.py and S4_V5_PROTOCOL.md; research/rrg/CURRENT.md and docs/PLAN_CURRENT.md. Inspection of compact JSON independently reproduced allocation, cluster means and death totals. Raw tick traces were not independently recounted. No project code, build, tests, fights, tuning or long job was run; only read-only stored-data inspection and elementary bound arithmetic.

The amendment repairs the state, geometry, startup, target-group and claim contracts. **F5 is partially resolved, with two required numerical-contract repairs below.** These are design gaps, not evidence that the proposed controller has failed in combat. The drafter owns their repair and self-audit. This verdict does not authorize implementation or development execution.

## Disposition of F1–F6

| Original finding | Round-two disposition | Evidence |
|---|---|---|
| F1: movement similarity absent after removing theta | Resolved; low clarification N1 | Lines 598–610 define a bounded, dimensionless complex similarity, exact-zero behavior, updated-state movement and separate historical dispatch. The changed formation/package contrast is disclosed. |
| F2: exact-zero startup and mode behavior unstated | Resolved | Lines 612–629 explicitly retain pressure/coupling-triggered startup, zero invariance for both signs of mu, initial commit, pair-specific memory, real-axis A and the limits of decay as an escape guarantee. |
| F3: units and incorrect mathematical checks | Resolved, with refinement acceptance addressed under R2 | Lines 631–644 fix nu=1/s, the free radius and radial checks, separate nonzero excitation from zero invariance, and replace universal equalization with a coupling-only check, damped case and counterexamples. |
| F4: alignment scale and group semantics incomplete | Resolved | Lines 646–659 restore morale's bounded real-axis alignment scale; living own other attackers, frozen previous assignments, joint trial-state means, updated scoring, valid zero/cancelling groups and empty-only omission are explicit. |
| F5: no numerical safety contract | Partially resolved; R1 and R2 required | Lines 661–682 preserve both finite components without state clipping, add substeps, stage finiteness, failure receipts and expanded clone coverage. The envelope derivation and executable accuracy/acceptance conditions remain incomplete. |
| F6: descriptive traces over-read | Resolved | Lines 684–702 narrow amplitude to a hypothesis and fixing melee omega to a budget tradeoff, correct the descriptive definitions, state signed pressure and exclude necessity/source claims. |

Section 18.1 must take precedence over the superseded section-18 sentences: one step per tick, the unqualified exponential/limit-cycle/equalization checks, [0,1] alignment, the missing-degree-of-freedom inference and omega-necessity wording. The previous section-17 round-two review used the same amendment precedence. An implementer must not combine the earlier and corrected contracts.

## R1 — Medium, required: the 500/s envelope is not established by the cited damage cap

Design lines 677–680 assert |P| up to 500/s from kappa<=50 and a damage-rate bound of 10/s, citing World::damage's remaining-HP cap. But the actual pressure is

    P = kappa * (z_in_answered - beta*z_out - z_in_unanswered), beta<=3.

Native s3_controller.cpp lines 174–182 divides **outgoing** credited damage by the source's maxhp. World::damage lines 225–228 caps **each victim's** credited damage and accumulates it into that source's counter. An artillery splash can credit multiple victims. A victim cap therefore does not establish a 10/s bound on the weighted outgoing contribution, and the text neither includes beta in its derivation nor supplies a tighter firing/splash bound. It also does not declare a runtime stop for pressure outside the checked envelope.

A sufficient conservative bound can be derived without fights. In fixed game mirror B, enemy starting HP is 10*258 + 30*92 + 10*181 = 7150; minimum own maxhp is 92. No healing or replenishment applies in this configuration. With dt=1/30 and q=exp(-dt/2), let b=(1-q)/dt=0.495856/s. The EMA and lifetime HP caps give

    z_in_answered + z_in_unanswered <= b,
    z_out <= b * 7150 / maxhp(source),
    |P| <= 50*b*(1 + 3*7150/92) = 5805.293/s.

The conservative concentration of all allowable credited damage into one recent tick is a bound argument, **not a claim of a reachable default-army trajectory or observed pressure above 500/s**. A tighter proof may legitimately retain 500/s. Incoming damage alone is much more tightly bounded than the outgoing expression, so they should not share an unexplained rate bound.

**Concrete fix:** derive the supported pressure bound from the actual admitted A/B roster, source maxhp, beta, EMA, multi-victim damage and absence of healing/spawning; either expand the no-combat envelope to cover it or establish a tighter bound. If an envelope is an admission restriction, explicitly reject/record out-of-envelope input before integration rather than silently extrapolate a passed check. Match the initial-state envelope to the reachable driven amplitude, too. Expanding need not require changing the ODE: with the conservative bound above, mu=2 and nu=1, the proposed Z is about 20.387 and the printed policy asks for n=43 at maximum rates/gains and dt=1/30, below 64. This is arithmetic feasibility, not a stability or accuracy qualification.

## R2 — Medium, required: refinement reports error but cannot reject an inaccurate finite integrator

Lines 644 and 676–681 compare the physical tick with finer integration, but the listed result is substep counts, refinement error and absence of non-finite values. **The new no-combat complex-state envelope has no explicit error acceptance limit.** Section 8 line 213 already requires maximum absolute commitment difference <0.02 over captured default-knob phase/morale engineering fights; that inherited criterion must be preserved, rather than described as absent. It does not specify acceptance for this new envelope or bound the imaginary component: commitment clipping can hide state error, while Im z still directly affects similarity and target alignment. Equality to an independent implementation of the same RK4 algorithm at 1e-9 tests implementation agreement, not accuracy relative to the ODE. The drafter must connect the expanded check to an explicit rejection criterion.

The follow-up Z formula is a sensible **continuous-solution** maximum-amplitude bound: for a unit at the global maximum radius, nonnegative diffusive averages cannot increase the outward radial contribution, and mu_+*r - nu*r^3 + max|P| is negative above the stated drive/free-radius scale. However, a continuous invariant disk is not by itself a guarantee that explicit RK4 trial states stay in that disk. The text checks trial values for finiteness, but checks Z only at the endpoint. Its real-axis linear stability comparison is not a complete nonlinear accuracy qualification. No actual stage-bound violation or instability is asserted here.

The retry also lacks a terminal rule if the second endpoint remains above doubled Z, and "n<=64" versus "if the cap is reached" leaves n=64 acceptance ambiguous.

**Concrete fix, before implementation:**

- Preserve the inherited <0.02 commitment check and explicitly extend or supplement numerical error limits and the reference/refinement procedure over the supported isolated and coupled envelopes. Make excess error a yes/no stop with one action and responsible role. Include both complex components and commitment; cover threshold-sensitive decisions with explicit margins/boundary fixtures rather than demand universal action equality at discontinuities.
- Either establish that all RK4 trials obey the bound used for L, or monitor their amplitudes and define a bounded reject/recompute rule. Do not use finiteness as the only trial acceptance criterion.
- State n=max(1,ceil(dt*L)), whether exactly 64 is allowed, and the terminal disposition of an unsuccessful single retry. Retry from the tick-start joint state with pressure/topology/assignments frozen; consume counters once and publish only an accepted result. Exhaustion must retain last finite states, publish hold/no-target, count failures and trigger the inherited runner stop.
- Keep state unclipped; a different substep policy is a declared drafter revision, not an implementer adjustment during development.

These repairs can be bounded design edits and no-combat checks. No rehearsal panel, extra combat ablation or tuning is needed to close them.

## N1 — Low, nonblocking: the similarity gate uses the amplitude product

At lines 600–604, attenuation occurs when |z_i|*|z_j| < delta^2, rather than whenever either unit is below delta. Aligned amplitudes 0.1 and 1 give similarity 1, while 0.1 and 0.1 give 0.25. The formula is continuous and tends to zero as either amplitude tends to zero with the other fixed; its range and exact-zero claims are correct. Clarify this product threshold and add the asymmetric-amplitude fixture. If separate low-amplitude gating is intended, the drafter must explicitly change the formula; this review does not require that choice.

## Evidence, signs, fairness and claim checks that pass

The trace evidence justifies investigating a fading commitment; it does not select Stuart-Landau uniquely or establish amplitude as the cause of regular losses. Compact records reproduce 20 fights and ten clusters per pairing, mean S -6.35/+9.95/+7.10 and own deaths 974/603/847. The corrected 1-second reversal rates and gun-band associations match the summaries. The development reference -6.025 is distinct from the diagnostic -6.35. Killing sources remain unmeasured. The corrected mean-versus-maximum melee death times and signed omega magnitude are honest.

At zero, additive -P gives a negative real derivative for positive signed P, matching morale; v5 instead has P*sin(theta). Answered and unanswered pressure have opposite signs under the inherited producing-tick classification. Rotation can later change the real sign. All-zero own states with zero pressure and zero group/neighbour forcing stay exactly zero even for positive mu; a driven neighbour can excite a unit with zero own P. No symmetry-breaking perturbation is required. With omega_melee=0, melee-only A stays real from zero and does not test rotation. New out-ranged pairs initialize commit at c=0; existing escape memory survives only while the thresholds are not crossed.

The ledger contains eleven knobs per stateful arm. Resonator: K, K_t, kappa, beta, mu, omega_ranged, G, w, f_c, m_k, lambda_th. Artillery inherits omega_ranged; omega_melee is fixed at zero. This is equal dimension and budget, not equal expressive capacity. Preserve parameter rejection: omega_melee is a removed v6 input, unknown/non-finite knobs fail, and mu belongs only to the v6 resonator. Retain every selected knob on stops. The real, zero-omega case is **morale-like internal relaxation**, not containment of the whole morale controller: cubic versus hard saturation, shared versus role-specific decay and the changed similarity/package prevent that stronger claim. The amendment already discloses those boundaries adequately.

The A/B-only protocol and regular-head ordering are sound development choices. Average both orientations within seed, then each head's clusters separately; novice tuning mean>=0 eligibility precedes regular S; ineligible candidates remain below eligible ones; earlier exact ties remain incumbent; identical ordering drives CMA and retention. Fresh entropy, fixed budgets, no validation selection, common-seed all-arm reporting and explicit unrun C/P2/P3 remain required.

Separate novice validation mean>0 applies at both A and B. B progress requires regular mean>-6.025; beating regular requires regular mean>0, novice pass and failure-free completion. Equality fails the validation gates. Boundary/failure fixtures using fake records are appropriate. The historical progress reference is unmatched, and positive finite-panel mean is an exploratory trigger to draft S5, not superiority, P1 support or owner approval to execute S5.

## Native feasibility and recheck record

The existing observation/prepare/decide/clone interface can support this controller without additional engine information. Implementation must extend the factory/configuration admission, complex state/RHS, movement/target dispatch and host diagnostics together; the current native scalar ModelUnit/Memory/Derivative and phase-assuming host cannot simply reinterpret z as theta. Preserve v0–v5 and byte-identical unchanged-arm actions at fixed requests/knobs. The listed complex clone/isolation, counter/status, assignment, mode and diagnostic checks are adequate. Failure propagation must include downstream trial-state consumers, with raw failure receipts never scored or dropped. Amplitude-aware phase validity, contiguous arg-rate segments, explicit not_run diagnostics, diagnostic-on/off identity and dead/absent-id cleanup are appropriately specified.

The owner's verbatim request was sent to separate reviewer `s18_r2_recheck` under AGENTS.md's mandatory recheck rule. It independently corroborated the remaining pressure-envelope and refinement-acceptance gaps and the low product-gate clarification. This supporting review is Codex-family, while the main review of Claude's design is cross-family. A tentative sandbox-pressure example was rejected as outside the fixed game contract and excluded; neither reviewer claims observed pressure above 500/s or combat instability. Final-draft recheck confirmed the conservative bound, continuous Z reasoning, dispositions and proportional CHANGES_REQUIRED verdict. **Disposition:** retained R1/R2 and N1, simplified ledger wording, and explicitly acknowledged the inherited <0.02 commitment criterion while requiring acceptance for the new complex envelope.

The explicit instruction not to edit existing files takes precedence over the usual PLAN_CURRENT tracking location. This new review is the scoped recheck/disposition record; the plan maintainer should link it and track the drafter's R1/R2 responses in docs/PLAN_CURRENT.md. The main .git is read-only, so this file is left uncommitted as requested; no alternate checkout or delivery bundle is created.

| Yes/no condition | Action | Responsible role |
|---|---|---|
| Does this review require design changes? | Repair R1/R2 and record their causes in the self-audit. | drafter |
| Is the supported numerical envelope or its acceptance still incomplete? | Stop v6 implementation. | implementer |
| Has the amended numerical contract received an approving design review? | Assess the repaired design within the owner's authorized scope. | reviewer |
| Is a development or registered run requested? | Obtain the applicable owner execution authorization. | owner |

Stop condition met: CHANGES_REQUIRED. Only this review file was added; existing files and unrelated evidence remain unchanged.
