CHANGES_REQUIRED

Reviewer family: Codex
Reviewer model: GPT-6
Reviewed design commit: 037bf1a6dfab53459f953e7886cf384544253bdb
Reviewed workspace HEAD: be1d7c666c30287a0aa42f37da3aa3a33209932c
Design SHA256: faecfbad1de6a034fef9818f8b0d184c3bc6f275a00b49969cdc40a464c445e6
Design: evidence/tactical_composition_demo/DESIGN_0G.md, section 18 (v6)

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Cross-family design review of Claude's proposal. Read AGENTS.md first. Inputs inspected: DESIGN_0G sections 3–5 and 13–18, its inherited normalization/pressure/diagnostic rules (sections 2, 7 and 12), S4_V5_DEVELOPMENT_REPORT.md, S4_V5_TRACE_DIAGNOSTIC.md, the diagnostic's SUMMARY.json, SUPPLEMENT.json, all 60 compact per-fight summaries and final verification/correction records, current native controller/bridge/diagnostic/host sources, s4_v5.py and the amended protocol, both previous section-17 Codex reviews, research/rrg/CURRENT.md and docs/PLAN_CURRENT.md. The design file matches the reviewed commit. No build, project tests, fight, tuning or long job was run. JSON inspection checked compact conservation/arithmetic; raw tick traces were not independently recounted here.

The extension is a reasonable development hypothesis, but not yet an executable design contract. Required repairs belong to the drafter and must be entered in its self-audit before implementation. No existing file is changed by this review.

## F1 — High, blocking: the position/state feedback law is incomplete after deleting theta

Section 18 replaces theta with complex z, but line 549 retains the movement law unchanged. Section 3 line 84 defines resonator ally similarity as cos(theta_j − theta_i). There is now no theta. Native s3_controller.cpp lines 121–125 implements precisely that scalar-phase similarity, and prepare uses it at line 185.

Choosing cos(arg z_j − arg z_i) would be a new definition, with undefined arguments at zero and poorly conditioned arguments near zero. Choosing a complex dot product or amplitude-distance similarity gives different formation forces. Reusing cos(Re z_j − Re z_i) silently interprets amplitude as phase. This decision controls the geometry-to-state-to-geometry loop and cannot be inferred by the implementer.

**Fix:** specify an explicit bounded s_ij(z_i,z_j), its units/range, zero/low-amplitude behavior, and which updated state enters movement. Add sign/range, zero-zero, zero-nonzero, phase/amplitude and deterministic-tie fixtures. If it changes the formation law, disclose that v6 is a changed controller package, not an isolated amplitude intervention. Do not claim unchanged C4 phase-law identity for v6; preserve historical reference adapters and v0–v5 behavior through separate dispatch.

## F2 — Medium, required: exact-zero startup and retained-mode behavior need an explicit contract

For P_i = 0 and z_i = 0 for every unit, every RHS term is exactly zero for any allowed mu, omega, K or K_t. RK4 preserves zero exactly. Neither positive mu nor diffusive coupling spontaneously breaks this symmetry. A driven neighbor can excite an undriven unit, so “without drive” must distinguish no own pressure from no forcing anywhere in its coupling component.

At startup c = 0. Section 14 line 361 and native v3Preferred initialize a new out-ranged pair to **commit** at c >= 0. Quiet startup therefore holds commit, not escape. Decay preserves an already acquired escape mode only if the trajectory never crosses +0.2 again; rotation during decay can still cross either threshold while amplitude is appreciable. New pairs initialize from current c, not from another pair's history. After nonzero excitation, the allowed positive-mu regime need not decay at rest: an isolated unforced unit approaches its nonzero free radius and can keep crossing mode thresholds. With omega_melee fixed to zero, the all-melee stage A stays on the real axis from zero under real forcing/coupling; it does not exercise rotational dynamics.

**Fix:** explicitly retain zero startup as a pressure/coupling-triggered controller, or declare a seeded perturbation and its deterministic provenance before implementation. A perturbation is not required by this review. If retaining zero, add exact all-zero invariance for both signs of mu, first-pressure onset, excitation by a driven neighbor, real-axis stage-A invariance, new-pair c=0 initialization, and a previously escaping pair whose state remains inside the hysteresis band. State that positive-mu oscillation needs a nonzero excitation and that amplitude decay alone does not guarantee safe escape.

## F3 — Medium, required: fix the normalization and mathematically incorrect checks

With dimensionless z and game time in seconds, the cubic term as printed lacks its coefficient's unit. Declare `−nu |z|^2 z` with **fixed nu = 1/s**, rather than adding a tuning knob. The free radius is sqrt(mu/nu), not the dimensioned expression sqrt(mu). The normalization sets how amplitudes interact with the fixed 0.2 mode thresholds and target-distance divisor 2; it is part of the controller, not cosmetic notation.

For an isolated unforced unit with radius r:

    dr/dt = mu r − nu r^3;   d(arg z)/dt = omega only where r > 0.

Check 1's exact exponential decay is false at finite amplitude. For mu<0 and r>0, r falls faster than r0 exp(mu t); exponential behavior is the small-amplitude/asymptotic limit. Check 2 needs r0>0; zero stays zero, and omega=0 gives stationary phase rather than oscillation. Include mu=0's algebraic decay, `r(t)=r0/sqrt(1+2 nu r0^2 t)`. Check 3 is correct after inserting nu: for mu<0 and omega=0, `mu x − nu x^3 = P` has a unique real root opposite in sign to nonzero P.

Check 4 also overstates the full ODE. Diffusion contracts the difference by itself; differing rates/drives need not equalize. Even identical positive-mu oscillators with symmetric coupling rate a have the exact antiphase solution `z2=−z1` of radius sqrt((mu−2a)/nu) when mu>2a. Full-state convergence cannot be universally asserted.

**Fix:** test the radial equation/analytic solution, nonzero-initial-state limit cycle and zero invariance separately. Test the coupling contribution independently, then a declared matched damped case and a differing-rate/drive counterexample. Retain the independent complex RK4 reference and add physical-tick refinement, not only equality between two implementations of one step. Driven amplitude is not capped by the free radius; do not use the approximate free-radius statement as a numerical bound. State the forcing assumptions and test the supported envelope.

## F4 — Medium, required: target alignment changes the contrast and needs complete group semantics

Line 548's `1−min(1,|z_i−zeta_ij|/2)` is **not** the same form as morale's `1−|m_i−mean m|`. On real bounded states, distances 0/1/2 give new alignments 1/0.5/0 versus morale's 1/0/−1. The new range [0,1], slope and saturation change alignment relative to gamma=1's engagement term and the fixed target hysteresis eta=0.2. Undefined alignment 0 can beat an anti-aligned group under morale, whereas no defined group has negative alignment in v6. Thus even omega=0 is only morale-like dynamics, not containment of the complete morale controller.

Line 545 defines a complex arithmetic mean, unlike the old circular group. A nonempty all-zero group or a cancelling group (z and −z) has a **valid mean zero**. It must not inherit aggregate's resultant<0.1 rejection (s3_controller.cpp lines 14–17). The target-coupling term should then be `−K_t z_i`, not omitted. Empty/no-target groups omit the entire term, including the subtraction.

**Fix:** explicitly choose and justify the alignment scale, or match the bounded real-axis scale if that is the intended contrast. State that keeping this formula changes targeting as well as internal dynamics. Specify living own other attackers, self exclusion, previous assignments frozen through the tick, group recomputation from each joint RK4 trial state, and updated-state scoring. Declare that empty groups alone are structurally undefined, nonempty zero means are valid, and non-finite members cause failure rather than an empty-group fallback. Add empty, self-only, singleton, cancellation, real-axis comparison, scale/saturation and exact eta/tie fixtures. Keep the inherited engaged-enemy score, not section 3's superseded beaten-enemy preference.

## F5 — High, blocking: continuous cubic saturation does not establish numerical safety

The existing phase RHS is bounded in its state-dependent sine terms. The proposed cubic RHS is not; its real-axis local slope is mu−3 nu x^2 before diffusion. A dissipative continuous ODE can still be unstable under one explicit RK4 step at dt=1/30. Knob limits bound gains, not by themselves the counter-derived drive or trial-state amplitude. Native World::damage clips credited damage to remaining HP, which helps establish a real bound; the design must actually connect the permitted armies, damage/healing/counters, gains and RK4 trial values to that bound. No instability in the proposed combat controller is claimed to have been observed.

The action clip must not become a state clip. Persist **both unbounded finite components** of z; compute c only after accepting the integration result. Check both components, norms/cubic products, every RHS/stage, group means, scores and raw actions before clipping/min/max can hide infinities or NaNs. Current memory/model/derivative/diagnostic structs are scalar (s3_controller.h lines 11, 29–36), and final-state checks at s3_controller.cpp line 184 are not a complete complex-stage contract.

**Fix:** declare a supported numerical envelope and a no-combat stability/refinement check over it, including high pressure and high K/K_t. If one RK4 step cannot meet it, the drafter must declare a bounded substep/integration policy before the run; do not silently clamp amplitude or change the ODE. Specify atomic last-finite complex-state retention on failure, handling of contaminated dependent trial states, hold/no-target publication, and failure counting. Preserve the inherited runner's raw failure record and stop semantics (s4_v5.py lines 125–130, 184), rather than scoring or dropping failures. Extend clone checks to both components, counters and answered-status memory, previous assignments, pair modes and diagnostics; advance the clone independently and verify the parent is unchanged.

## F6 — Medium, required: remove causal and necessity conclusions that the diagnostic cannot support

The descriptive evidence supports trying a controller whose commitment can fade. It does not establish that amplitude is “the missing degree of freedom” (line 528), that state is irrelevant before melee dies (line 554), or that selected omega near zero means rotation is not helping (line 566). The last inference repeats the issue already corrected by section-17 amendment F3. Melee affects allies through coupling, spatial forces, targeting and screening before death; stage A evaluates melee survivors directly. About 16 s is the resonator–regular **mean** melee death time, not an all-unit cutoff (maximum 28.13 s). There is no matched zero-melee-omega or zero-ranged-omega intervention here.

**Fix:** call amplitude decay a candidate explanation/design hypothesis, fixing omega_melee a disclosed budget tradeoff, and selected mu/omega optimizer diagnostics. Preserve the valid exclusion of oscillation-necessity claims for a zero-omega win, but also exclude them for a nonzero-omega win without a necessity intervention. No extra combat ablation is requested by this review. Do not generalize a selected Hopf normal form into a universal physical-resonator or RRG requirement. No causal background-transformation, C5 or unchanged-C4 claim follows from this one-level controller.

## Evidence and sign checks that pass, with reporting corrections

Compact summaries agree with the report's 20 fights per pairing, 10 seed clusters, 974/603/847 own deaths and 58/2/189 enemy guns removed for resonator–regular/morale–regular/resonator–novice. Diagnostic mean S is −6.35/+9.95/+7.10; these are distinct from the 100-cluster development B means −6.025/+9.530/+5.600. Direct regular exposure is 5.36% versus 1.10%, with 522/591 resonator direct deaths inside gun bands. This is co-occurrence, not killer attribution: lethal sources remain unavailable, and many deaths precede non-gun clearance. The 8.73 s span is a distance/base-speed comparison, not measured travel time.

The selected ranged omega is **−1.91195178 rad/s**; line 516 should write **|omega_ranged| approximately 1.91**, and label the observed rates as absolute rates. The section-18 reversal comparison mixes rounded timescales: at **1 s**, resonator direct/gun values are **27.48/24.32**, morale **0.92/0.74** per living unit-minute; morale's **1.69** direct value belongs to the **0.2 s** definition. Report matched definitions with their speed filter and durations. “Never settles” should become “rarely meets the operational lock threshold in these traces”; operational stationarity does not test relative synchronization.

The new drive sign is correct **for signed inherited P**, and matches morale: at z=0, positive P gives negative Re derivative. Explicitly write the current own pressure `P= kappa(z_in_answered − beta z_out − z_in_unanswered)`, whose status comes from the producing tick, and the target engagement term `tanh(kappa(z_in_enemy+z_out_enemy)·1 s)` with gamma fixed at 1. Do not restore section 2's older own P. Positive answered pressure encourages escape; unanswered damage makes P negative and encourages commit. “Being beaten implies negative commitment” is therefore not a universal description. Unlike v5's `P sin theta`, additive `−P` excites a zero state. With omega≠0 the initial drive sign does not guarantee a permanent Re sign; this should be measured, not promised.

The 11-versus-11 ledger is arithmetically correct: K, K_t, kappa, beta, mu, omega_ranged, G, w, f_c, m_k, lambda_th; omega_melee=0 and artillery inherits omega_ranged. Equal dimension/budget is a declared resource comparison, not proof of matched expressive capacity. Stage A does not identify omega_ranged. Reject removed/unknown/non-finite knobs, keep both role-rate rules explicit and log all selected values even after STOP.

## Protocol and gates

A/B only resolves the old stage-C objective mismatch. Inherit the complete v5 ordering: two orientations averaged within seed; ten novice and nine regular tuning clusters; novice tuning mean >=0 eligibility precedes regular mean S; ineligible candidates rank by regular S below every eligible candidate; earlier exact ties stay incumbent; identical ordering feeds CMA and retention. Keep fixed generations/budgets, new development entropy, no validation-based selection, all-arm validation, explicit unrun C/P2/P3 endpoints, input pins, bounded deadlines and child cleanup.

Retain and explicitly restate the separate **resonator novice validation mean >0** gate at both A and B. Tuning eligibility >=0 does not replace it. At B, progress requires regular validation mean **>−6.025**, equality fails; “beats regular in development” requires **>0**, equality fails, plus the inherited novice validation pass and failure-free completion. Add boundary/negative-novice/failure fixtures using fake records, with no combat.

Both regular thresholds are legitimate development decisions. The −6.025 reference uses a historical, unmatched seed panel and is not a paired improvement or statistical superiority claim. A positive finite-panel mean is an exploratory W4 trigger to **draft** S5, not P1 support, superiority to morale, source qualification, experiment approval or authorization to run S5. Repeated outcome-informed revisions are development selection; final judging must stay fresh and owner-approved. All four arms on common fresh v6 seeds support paired comparator reporting, but v5-versus-v6 mechanism attribution is not supplied by that panel.

## Native feasibility and mandatory recheck

A complex resonator can fit the existing observation/prepare/decide/clone interface without new engine information. Implement separate versioned complex state/RHS and policy dispatch; preserve v5 scalar paths, historical fixtures, regular/novice no-lookahead configuration and byte-identical unchanged-arm actions at fixed knobs/requests. Re-running tuning on fresh seeds need not reproduce earlier selected knobs or fight scores.

The host currently assumes every resonator state is a scalar phase (`host.cpp` lines 105–112; `s3_diagnostics.cpp` lines 20–27). Specify new Re/Im/amplitude fields and phase validity. Do not report atan2(0,0) as phase zero/coherence one. Count arg-rate samples only with both consecutive endpoints above the declared 0.2 amplitude threshold, unwrap within contiguous valid segments, reset across invalid gaps and report null reasons/denominators. Existing phase coherence/target-phase/candidate diagnostics must become amplitude-aware or be explicitly not_run for v6. Add diagnostic-on/off action identity, death/absence cleanup and historical v0–v5 preservation to the check list; these checks need no fight tuning.

The verbatim owner request was sent to separate reviewer `s18_review_recheck`, which independently confirmed CHANGES_REQUIRED and the missing similarity, zero-state invariance, normalization/check and group-semantics findings. It rechecked the final draft and found no further blocking issue or incorrect mathematical/sign/gate conclusion. **Disposition:** corrected the signed-omega magnitude, melee mean-versus-maximum timing and omega=0 stationary-phase wording; clarified that the approximate free radius is not a numerical bound and that no RK4 combat failure was observed. Zero startup remains a legitimate design choice, not a demand for noise. All six findings stand. This additional reviewer is Codex-family; it is a same-family check of this report, while the main review of Claude's design is cross-family. The instruction not to edit existing files takes precedence over AGENTS.md's root-plan location; this new file is the scoped record, and the plan maintainer should link it in docs/PLAN_CURRENT.md.

| Yes/no condition | Action | Responsible role |
|---|---|---|
| Does this review require design changes? | Repair the section-18 contract and self-audit before implementation. | drafter |
| Are complex movement, group, startup and numerical rules still undefined? | Stop v6 implementation rather than infer a controller. | implementer |
| Has the repaired design received an approving review? | Proceed only within the owner's implementation authority. | implementer |
| Does any engineering or controller-failure gate fail? | Preserve the failed attempt and complete a repair batch before further execution. | implementer |
| Do B novice validation and positive regular development gates both pass? | Draft S5 without starting its registered run. | drafter |

Review complete: CHANGES_REQUIRED. No implementation, fights, registration or acceptance was performed or authorized by this verdict.
