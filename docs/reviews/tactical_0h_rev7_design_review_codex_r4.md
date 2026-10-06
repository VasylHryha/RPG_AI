APPROVE_WITH_NOTES
Reviewer family: Codex
Reviewed DESIGN_0H_REV7.md SHA256: e0789c87d9a23e83360a48e3d963d5005d95eb0da4a8ae7c7b8b9b0b1423ec07

## Disposition of round-3 findings R3-1–R3-4

Revision 7.3 section 10 governs over sections 1–9; those amendments govern over the revision-6.5 base where they replace it. Superseded statements are not counted as current defects.

| Finding | Round-4 disposition | Evidence |
|---|---|---|
| R3-1, lost development stops and INVALID rules | CLOSED | §10.1 explicitly retains §9.7 and restores dependency readiness, development INVALID, unusable perceive, unmatched development M births and G1/G0'/G2 stopping rules. It distinguishes the stricter F7 fixture gate from the full-run seed disposition. |
| R3-2, pair-flag recipients and estimator scope | CLOSED | §10.2 defines individual, element-pair and site-pair validity; applies it to all live estimator pairs; retains consecutive records; counts valid active observations toward 80/100; and specifies P_i, ω̂ and qualification dispositions. A pair-only failure no longer ambiguously removes individual records. The numerical-endpoint wording has a LOW note below. |
| R3-3, missing motion and unwrapped convergence comparisons | CLOSED | §10.3 adds maximum matched-endpoint position error ≤ 0.01 m.u., unwrapped carrier-relative phase error ≤ 0.01 rad, and minimum-distance records in both integrations. These supplement §9.2's wrapped phase, entry, separate topology and pin checks. |
| R3-4, comparator assay and cost | CLOSED | §10.4 binds site-body-off to fresh final-whole-medium copies, the perceive recipient panel, intact carrier/decoder, paired descriptive reporting and A7's cost projection. The interpretation of removing neighbours has a LOW note below. |

Codex (GPT-6), cross-family design review, round 4, 2026-10-06; within the requested approximately 20-minute cap. Inspected HEAD: `7f4ecf9ff1fb37165c30d5a021167711f9b7925c`. This approves the **design with low notes**. Integration readiness, numerical/fixture results, development continuation, milestone acceptance and scientific qualification remain separate gates.

Owner request reviewed verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Read AGENTS.md, all three earlier revision-7 reviews, the revision-7.3 design, the complete revision-6.5 base through 19.9, relevant inherited revision-5.1 rules, the fixture report, C4 model/detector, existing sampling/qualification adapters, current source guidance and decision 0031. Executed only the expressly authorized standalone toy, once: `python3 -B evidence/tactical_composition_demo/growing_shapes_review_claude/rev7_toy/f1b_toy.py`. It imports only `math`. No project code, tests, native library, panel, benchmark or experiment ran. No recorded verdict was recomputed. Only this review file was written; `docs/PLAN_CURRENT.md`, historical evidence and unrelated workspace work were left untouched. Git metadata is read-only under this session's policy; this file is left uncommitted in the workspace.

Evidence notation: **R7** = `evidence/tactical_composition_demo/DESIGN_0H_REV7.md`; **R6** = `.../DESIGN_0H_REV6.md`; **Base** = `.../DESIGN_0H.md`; **Report** = `.../growing_shapes/runner/REV6_FIXTURE_REPORT.md`; **Toy** = `.../growing_shapes_review_claude/rev7_toy/f1b_toy.py`; **C4** = `geomind/c4_model.py`. Adapter paths below are relative to `evidence/tactical_composition_demo/growing_shapes/`. Line references identify the inspected bytes.

Additional SHA256 identities: R6 `ca9c43362e3eebace889c7306784ffe5dd3095a58eb2095473f745eff31b52c5`; Base `39a630c3f4d440a6634538121773253443dcb15e8166406f36cde3727c119925`; Report `d530ae6236cb63e978d5224c33db693e446c9242884a5a4751295855158f7fc8`; C4 `4fafc161b65914a44dccaca6caefb59a5154079f17f564b4cdc4d44f58c59d33`; Toy `3f0513ac76a1dd03a2ed260a3a88d9927d0b0167f8ab730b383b87fc98b076b9`.

## New numbered findings

### 1. R4-1 — LOW: the opening status still identifies revision 7.1

**Evidence:** R7:1 names revision 7.3, but R7:3 starts with “Status: revision 7.1.” The same paragraph correctly establishes section-10 precedence, so this does not resurrect the old clauses or block design review. It can nevertheless mislabel an implementation handoff or a receipt summary based on the opening status.

**Fix:** Claude should change that status to revision 7.3 and record the design-review disposition separately from integration/execution readiness. Recompute the design hash for any later execution-start pin; do not overwrite the hash reviewed here. No dynamics, threshold or entropy change is needed for this metadata correction.

### 2. R4-2 — LOW: unwrapped numerical endpoints are not “exact” physical phases

**Evidence:** R7:441 says the unwrapped endpoints used by ω̂ “are exact.” They retain whole-turn information and avoid wrapping alias, but they are RK4 approximations. R7:304,312,443 correctly acknowledges the stage-sampling limitation, and §10.3 now requires unwrapped refinement agreement. Neither a passing refinement comparison nor unwrapped storage establishes an exact continuous solution.

**Fix:** replace “which are exact” with “which retain whole-turn information; their numerical accuracy is subject to N1.” Keep the declared endpoint-validity suspension policy. Intermediate fast frames need not erase an unwrapped endpoint difference merely because they fail a circular-observation screen. This is a wording correction, not a request to change the estimator or its ten-second window.

### 3. R4-3 — LOW: site-body-off measures the total boundary-removal effect, including neighbour normalization

**Evidence:** R7:135–139 defines N^x as the nearest eight elements plus active sites, with its own mean count. R7:456–459 removes sites from N^x while retaining the element motion law. Removal can change that count and admit additional element neighbours. Even with no saturation, removing one site from a list containing two elements changes each surviving element-pair coefficient from one-third to one-half. This is an algebraic example of the law, not a simulated trajectory.

The paired assay is now fully bound and useful. Its difference is not an isolated additive estimate of the phase-dependent site force: it includes altered normalization, neighbour selection and their subsequent trajectory effects.

**Fix:** state that site-body-off recomputes N^x under the existing nearest-neighbour and mean rules, and label its result the **total effect of removing site bodies**. Report N^x counts/changes with the paired differences where available. Preserve its descriptive status and existing scope. A separate comparator preserving the element list and denominator would answer a different question and belongs in a deliberately specified later revision if needed; it is not required for this design to proceed.

## Assessment of the requested mechanisms

**Diagnosis.** The narrowed diagnosis is supported. F1b retains its path at every endpoint, misses the eight-second deadline and eventually locks; its first recorded entry is 15.4 seconds after the step (Report:15–19). F1c compacts severely, with output radius 1.804 → 0.0337 m.u. and source radius 3.2 → 1.5181 (Report:38–48). However, source drive-presence bins remain 100%. The 1,117 element-seconds without access is pooled across members, not source inactivity. Reduced drive strength and changing geometric weights can matter while both a path and strict source reach remain present. §8.1 correctly treats slow phase response and compaction/access degradation as supported hypotheses, without identifying one exclusive cause. F1d measures the total λ effect under the new pinned, mobile law; it cannot retrospectively isolate the historical failure.

**Derivation of λ.** The toy reproduces these values:

| λ | Absolute first entry, s | Delay after the t = 8 step, s | Error at t = 16, rad |
|---|---:|---:|---:|
| 1 | 31.04 | 23.04 | 1.029 |
| 2 | 19.52 | 11.52 | 0.540 |
| 4 | 13.76 | 5.76 | 0.141 |
| 8 | 10.88 | 2.88 | 0.009 |

Thus 8 follows from §8.1's declared smallest-power-of-two policy with a four-second margin. The earlier two-second derivation is withdrawn. This is a principled, transparent **engineering calibration**, not a unique theoretical constant, proof of optimality or guarantee of encoding arbitrary trained states within a four-second cue. The toy uses fixed positions, zero detuning and forward Euler at 0.002 seconds. Its bookkeeping stops clearing late exits after t = 16 (Toy:23); retain it as the supplied relaxation calibration rather than treating that helper as a general sustained-entry verifier. Actual F1a/b/c must enforce their declared inclusive hold criteria on saved engine traces.

Writing β_i = θ_i − πt gives

    β̇_i = (ω_i − π) + λ F_i(β, x, α, g).

With fixed geometry, ω_i = π, fixed gains and constant input, λ time-dilates the relative-phase dynamics. With detuning, moving geometry, adaptation or changing inputs, it does not rescale the whole system. Scaling coupling and drive together preserves their instantaneous coefficient ratio, while changing their balance against detuning and geometry. For one fixed driven oscillator, §9.6 correctly gives the stable offset arcsin[δ/(λa)] for |δ| < λa, with a marginal boundary and inverse-λ behavior only as a small-offset approximation. No sufficient conflicting-network locking condition follows. Carrier tracking improves within that enlarged single-drive locking range; the carrier itself remains π, and ω and motion remain unscaled. Phase and geometry are separate clocks within the same element state here, not demonstrated recursive levels.

**Numerics and estimator validity.** The carrier advances only π·0.02 ≈ 0.063 rad per medium substep. A single high-gain drive can contribute up to λgk = 64 rad/s before its distance factor; internal coupling and detuning add further corrections. This is a coefficient bound, not a measured rate or proof of RK4 instability. N1 now provides an executable, bounded refinement gate: frozen cases, matching endpoints, wrapped and unwrapped phases, entry dispositions, separate N^x/N^θ agreement, positions, minimum distances and invariant pins. It does not certify accuracy for every later dense or near-collision state; retain the declared runtime validity checks and measurement-failure stops.

The frame E_i accumulation bounds the absolute numerical endpoint increment because the positive RK4 weights sum to one; its continuous-excursion claim remains conditional on stage sampling. Pair sums are conservative and can reject common motion that cancels in a relative phase. That is a declared admission policy, not an error. §10.2 now makes the masks executable. For example, E_i = E_j = 0.9 rad leaves each individual sample valid but invalidates their pair; a sensor pair with either individual remains valid under its own rule. Consecutive records remain available for 100/101-record prerequisites, while only valid active observations enter circular sums and their denominators. The policy applies before a qualification cohort exists and again to the actual cohort before circular qualification. Site-angle changes are known held observations; the screen does not erase the inherited effect of input jumps on PLV.

**Adaptation and 6.5 thresholds.** The ten-second unwrapped ω̂ remains a realized-rate estimate, not an independent estimate of intrinsic ω. A net π/2 encoding change contributes about 0.157 rad/s while it spans the two endpoints and can feed ω adaptation. The twenty-second adaptation clock, gain/reward eligibility and structural timers have not been sped up. At r* with eight neighbours, the nominal local phase coefficient changes from about 0.092/s to 0.734/s, or a local relaxation estimate of 10.9 → 1.36 seconds. These are local coefficient estimates, not measured network relaxation times.

Keeping the ten/sixty-second windows and 0.005-rad/s and 0.1-rad cuts is defensible under §8.8's explicit interpretation as fixed engineering admission rules for **new driven, anchored snapshots**. Their numerical values can be reused; the old dynamical equivalence and acceptance evidence cannot. Dividing every horizon by eight would change the unscaled geometry/carrier experiment. Faster common-input restoration can increase driven admission without establishing autonomous closure. O may now be a cohort/candidate member under §9.3; positional kicks use free members, phase kicks include all candidate members, pins remain fixed, and admissibility/skip accounting is declared. This repairs the earlier G1c/G5 default-only defect without adding an output to extracted groups after the fact.

**Pinned ends, units and the mask.** The final boundary law is dimensionally coherent: A has m.u./s, B has m.u.²/s, J and λ are dimensionless, drive/coupling have rad/s, and the displacement divided by max(r,r₀) is dimensionless. Each motion list has its own mean normalization; sites cannot steal phase-neighbour slots or dilute N^θ coupling. §9.4 specifies the complete vector regularization, including zero at coincidence. Its stated spatial derivative bound is at fixed phases, not a global stiffness bound for the coupled hybrid system. Birth clearance is a placement rule, not a guarantee maintained by motion. N1d covers inside-cutoff evolution, and the repaired F5(ii)/F4 starts are explicit.

Fixed O and active site bodies plausibly improve access and persistence, but supply neither permanent bonds nor a guarantee of ordered-chain span. At the live origin all sites are four units away, beyond strict radius three; sites supply no phase-neighbour term, and O's direct phase drive is masked. There is no literal site→O phase echo. The site cosine and activity nevertheless transmit input to ordinary geometry even at g = 0. The mask therefore means zero direct phase drive and masked sensor histories, not zero observation-to-motion access. Pinning O also makes the incoming-coupling lesion a clean terminal-channel removal. A short driven relay can still satisfy the deliberately narrow G2 claim. Phasor, relay, K=0 and fixed-structure comparisons remain necessary to interpret that result; their descriptive status is retained.

**F1c and F1d.** F1c has no initial S→O edge and now requires entry by t = 16, a hold through t = 24, effective-root path persistence, source access and long-run functional response. These are meaningful gates, with pin invariance correctly separate. Passing could involve ordinary-node compaction or a new direct S→O shortcut. It would establish sustained access/response under the anchored law, not prevention of all compaction or preservation of the original chain. Span, source distances, weights and shortcuts must accompany that interpretation. F1c failure blocks F5/development; measurement failure is INVALID. F1d remains descriptive, reporting rates and geometry together without creating a new primary criterion.

**Timers and empty start.** §8.9 defines active-uncovered accumulation, active-covered/birth reset, inactive freeze and refusal retention, plus active-at-check birth eligibility. This avoids stale inactive-source births and allows structural demand to accumulate across cues. It leaves the established memory block's 80/100 gain/reward limitation intact; B-path correctly retains its immediate rule, and F8 retains its carried-history diagnostic. Intact, M and U all start empty with the same clock, ids and first growth check. No initial detuning draw exists; growth/world streams supply variation. Mark unused medium-initialization consumers honestly in the instantiated inventory. F5(ii) remains the explicit nonempty exception.

**Entropy, inherited contracts and AGENTS.md.** §8.10 specifies fresh master prefixes and world ranges, including the later F6/F8 consumers, and labels reused calibration/historical references and deterministic scaffolds honestly. Actual inventory instantiation, disjointness and hashing remain prerequisites, not completed measurements from this review. §8.11 binds inherited design bytes, new versions/configuration, native images and inventory, while preserving old loaders and accepted C4 bytes through new-file integration. Section 10 closes the inherited stop-table conflict without changing the historical F1b FAIL or NOT_RUN rows. Decision 0031 supplies the stated short-run standing permission after readiness gates; it does not replace formal milestone registration or the gated pipeline, and this session's explicit no-project-code instruction governs the work performed here. Current source status is recorded VERIFIED in `research/rrg/CURRENT.md`; source-package qualification was not rerun. Full RRG background recursion, learned structural transformation, library reuse and computation beyond a phasor remain unestablished.

## Disposition and adversarial recheck

No new HIGH or MEDIUM design blocker remains in the inspected revision. The three LOW notes concern metadata, numerical wording and comparator interpretation; they require no retuning or additional experiment to resolve. Claude owns their disposition and the plan entry. Carry the frozen contracts into new adapter files, complete the integration review before execution, and let N1 and F1/F5/F7 refuse progression if the hypotheses fail. A design approval is not a passing fixture result.

The review was rechecked against section-10 precedence, the earlier findings, the inherited sampling/qualification code and concrete mask/normalization counterexamples. Closed defects were not reopened merely because their old prose remains above the governing amendments. No rate bound was treated as an observed instability, no requirement to preserve a serial chain was invented, and no autonomous-recovery or task-selection claim was added. No change to `docs/PLAN_CURRENT.md` was made.

Assisted-by: Codex:GPT-6
