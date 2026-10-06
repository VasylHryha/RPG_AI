APPROVE_WITH_NOTES

Reviewer family: Codex
Reviewer model: GPT-6
Reviewed commit: 87d9cc58bfd02f0bc63d34d1f1a17a501e873189
Design SHA256: 8a87a8f56fb60c23400b099d4c26bbe013e7b16d087e29cea79f396037fee24b
Design: evidence/tactical_composition_demo/DESIGN_0G.md, sections 18, 18.1 and 18.2 together

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Cross-family review of Claude's amended design. Read AGENTS.md first. Inputs inspected: DESIGN_0G sections 3–5 and 13–18.2, inherited normalization/pressure/group/refinement rules, both section-17 reviews and both earlier section-18 reviews; S4_V5_DEVELOPMENT_REPORT.md, S4_V5_TRACE_DIAGNOSTIC.md, SUMMARY.json, SUPPLEMENT.json, FINAL_VERIFICATION.json and all 60 compact fight summaries; native controller/state/dispatch, bridge, host, diagnostic, damage and ability sources; s4_v5.py and S4_V5_PROTOCOL.md; research/rrg/CURRENT.md and docs/PLAN_CURRENT.md. Read-only compact-data arithmetic independently reproduced allocation, cluster outcomes, deaths, gun removals and phase-rate/lock fractions. Raw tick traces were not recounted. No project code, build, tests, fights, tuning or long job was run.

**R1, R2 and N1 are resolved. No new blocking design finding.** Approval concerns the design contract, including its mandatory pre-fight numerical acceptance gate; it does not assert that this unimplemented policy has passed that gate or will beat regular. This review supplies no additional implementation, development, registration or S5 execution authority.

## Round-2 dispositions

| Finding | Disposition | Evidence and remaining boundary |
|---|---|---|
| R1: unsupported pressure envelope | Resolved | Lines 756–767 derive the beta-weighted outgoing bound using source maxhp and total victim HP, admit 6,000/s, expand initial amplitude coverage and reject out-of-envelope pressure before integration. This is a conservative envelope, not observed pressure or proof of a reachable concentrated-damage event. |
| R2: no complex accuracy acceptance or complete trial/retry rule | Resolved | Lines 769–787 specify both component errors <=1e-3, commitment error <=0.02, policy versus 4n refinement, the retained captured-trajectory <0.02 check, monitored stage amplitudes, one joint-state retry with frozen inputs/counters, n=64 acceptance and terminal failure. A failed acceptance check requires a drafter revision before any fight. Numerical qualification remains to be performed. |
| N1: product gate unclear | Resolved | Lines 789–792 explicitly choose the amplitude product threshold and the asymmetric-amplitude fixture. Similarity is not gated independently by each unit's amplitude. |

The precedence at line 749 is explicit: **18.2 > 18.1 > 18**. It withdraws the earlier one-step rule, universal decay/limit-cycle/equalization claims, [0,1] alignment and overstrong mechanism/necessity wording. Read implementation and reporting requirements using that precedence, including the corrected signed pressure from section 18.1 rather than section 2's historical expression.

For R1, with b=(1-exp(-dt/2))/dt, each unit's incoming answered-plus-unanswered EMA is at most b because lifetime incoming credited damage cannot exceed its starting HP. Outgoing EMA is at most b times enemy starting HP divided by the **source's** maxhp. Thus

    |P| <= 50*b*(1 + 3*7150/92) = 5805.292529/s.

The native default B roster supplies 7,150 enemy HP and minimum own maxhp 92; melee-only A is covered conservatively by B. Credited damage is capped per victim; artillery splash can credit several victims, which the total-HP bound includes. The admitted mirror configuration has no healing or replenishment. Ordinary automatic abilities do not invalidate that cap.

Elementary arithmetic gives Z(6000)=20.58541949, L=1285.278487/s and n=43 at the printed maximum knobs, consistent with the rounded amendment. If the initial maximum amplitude is already Z(6000), the tick-start formula adds another unit margin, giving n=48, still below 64. A doubled-Z retry may exceed the cap and fail; the amendment permits that outcome and does not promise a successful retry. These calculations establish feasibility only. The continuous radial bound, finiteness and same-algorithm agreement do not substitute for the new refinement acceptance check.

## N1 — Low, nonblocking: pin the complex numerical fixture cases before checking them

Lines 775–777 specify magnitudes |z0| and |P|, and coupled pairs/triples with opposite drives, but do not enumerate initial arguments, signed omega/pressure cases, geometry/target assignments or the exact upper amplitude endpoint. A test implementation could accidentally exercise mostly real or symmetric states even though both component errors are reported. A finite grid is sampled qualification, not an exhaustive guarantee over every point in the continuous envelope.

**Concrete fix:** in the engineering fixture declaration, pin representative real, imaginary and oblique initial states; both signs of drive and rotation; equal and opposing phases; asymmetric amplitudes; empty, singleton and cancelling target groups; and asymmetric neighbour lists. Include the declared amplitude edge Z(6000), in addition to 20, with the tick-start margin recomputed normally. Add explicit n=64/n>64, stage-bound retry, retry exhaustion and non-finite failure fixtures, verifying that counters are consumed once, rejected states are never published and parents remain unchanged after advancing a clone. Do not manufacture a combat trajectory to trigger these cases. Preserve the acceptance thresholds; change the integration policy only through a declared drafter revision if the checks fail.

This completes fixture coverage within the already declared checks. It does not require another design revision or a combat ablation.

## Evidence, state, signs and claims

The trace evidence supports investigating fading commitment and mode retention. It does not identify missing amplitude as the cause of regular losses, uniquely select Stuart–Landau dynamics, or show that rotation is useless. The amended wording respects those limits. Compact records reproduce three pairings with 20 fights/ten clusters each, means S -6.35/+9.95/+7.10, own deaths 974/603/847 and enemy gun removals 58/2/189. Resonator regular direct/gun lock fractions are 0.472%/0.487%; morale direct stationarity is 91.92%. SUPPLEMENT.json supplies the matched one-second reversal rates 27.48/24.32 versus 0.92/0.74. Direct gun-band deaths are 522/591. Killing sources remain unavailable; gun-band membership is co-occurrence. The 8.73-second crossing is distance/base speed, not measured travel time. The historical development gate reference -6.025 is distinct from the diagnostic mean -6.35.

With z dimensionless and fixed nu=1/s, every RHS term has units 1/s. The free radial equation is dr/dt=mu*r-nu*r^3; the unforced free radius is sqrt(mu/nu) when mu>0 and the initial state is nonzero. The corrected exponential-limit, algebraic-decay, damped-pair and antiphase-counterexample checks are mathematically consistent. Cubic saturation is continuous dynamics, not a hard state bound; both complex components must remain unclipped. Only c=clip(Re z,-1,1) is clipped for actions after acceptance. The inherited morale reference applies its state clip once per physical tick, not at every RK4 substep.

The signed pressure is P=kappa*(z_in_answered-beta*z_out-z_in_unanswered), with the classification stored from the producing tick. At zero, additive -P drives Re z negative for positive P, matching morale. Unanswered incoming damage contributes negative P and initially drives commitment positive; this is intentional inherited behavior. v5 instead applies P*sin(theta). Rotation can later change the real sign, so the initial drive sign is not a permanent retreat/commit guarantee.

All-zero states in an unforced coupling component stay exactly zero for either sign of mu. Diffusive coupling does not spontaneously break symmetry, but a driven neighbour or target group can excite a unit with no own pressure. New out-ranged pairs at c=0 initialize commit; an existing escaping pair retains escape only while threshold crossings do not overwrite it. Melee-only A stays real with omega_melee=0 and does not test rotation. Positive mu remains a permitted optimizer regime and need not fade at rest after excitation.

The similarity formula is bounded and defined at exact zero. Its intended attenuation threshold is |z_i|*|z_j|<0.04. Alignment max(-1,1-|z_i-zeta_ij|) recovers morale's alignment scale on bounded real states. zeta_ij is the arithmetic mean of living own other previous attackers, recomputed from joint trial states with assignments frozen. Only an empty group is undefined; a zero or cancelling nonempty mean is valid, and non-finite membership fails. Target scoring retains the engaged-enemy term tanh(kappa*(z_in+z_out)*1s), gamma=1, rather than the older beaten-enemy preference.

The ledger is eleven versus eleven: resonator K, K_t, kappa, beta, mu, omega_ranged, G, w, f_c, m_k, lambda_th. omega_melee is fixed at zero; artillery inherits omega_ranged. Fixing melee rotation is a disclosed budget tradeoff, not evidence that melee state is irrelevant before death. Equal dimension and fight budget are resource fairness, not equal expressive capacity. Admission must reject the removed omega_melee input, unknown/non-finite/out-of-bound knobs and mu on unchanged arms; retain all selected knobs on stops.

The zero-omega, real-axis case is **morale-like internal relaxation**, not containment of the whole morale controller. Cubic versus hard saturation, shared versus role-specific decay, and the changed similarity/formation law matter. v6 is a changed controller package, not an isolated amplitude intervention. Selected mu/omega values do not establish oscillation necessity in either direction. The one-level controller does not establish RRG causal background transformation, C5 formation or unchanged C4 identity.

## Protocol, gates and native implementation

A/B-only scope is sound for this development question and avoids section 17's original undefined C selection objective. In B, average orientations within seed and then each head separately: ten novice and nine regular tuning clusters. Novice tuning mean>=0 eligibility precedes regular S; all ineligible candidates rank below eligible candidates, regular S orders each group, and earlier exact ties remain incumbent. The same ranking drives CMA and retention. Stage A retains novice melee selection. Fresh entropy, fixed generations/budgets, no validation selection, all-arm common-seed validation, input pins, deadlines/cleanup and explicit not_run C/P2/P3 remain mandatory.

The separate resonator novice validation mean>0 gate applies at both A and B. B regular progress requires mean>-6.025; beating regular in development requires mean>0, novice pass and failure-free completion. Equality fails these validation gates; tuning eligibility still includes equality. Use fake-record boundary, negative-novice and failure fixtures. Historical progress is unmatched descriptive comparison. A positive finite-panel mean permits drafting S5 under W4; it is not registered superiority, P1 support, superiority over morale or owner approval to execute S5. Repeated outcome-informed development selection must remain separate from fresh judging.

The existing observation/prepare/decide/clone interface is sufficient. A separate versioned complex path must extend configuration/factory admission, state/RHS, policy consumers and host diagnostics together. Current Memory/ModelUnit/Derivative and host capture fields are scalar, and host phase diagnostics currently treat every resonator as theta; substituting Re z into those paths would be wrong. Preserve v0–v5 and byte-identical unchanged-arm actions at fixed knobs/requests. Re-tuning unchanged arms on fresh seeds need not reproduce previous selected knobs or outcomes.

Clone coverage includes both components, counter baselines/EMAs, answered-status memory, previous assignments, pair modes and diagnostics. Retry is from the tick-start **joint** state, with no partial publication. Dependency failures must propagate through integration and downstream movement/target consumers. Explicit stage/norm/cubic/RHS/score/raw-action finiteness checks precede clips or min/max. The bridge already has an explicit controllerFailure flag/count, and the runner preserves raw failure rows and stops before scoring; use that path rather than a successful-looking hold fallback. A failed member cannot silently become an empty group. These are implementation obligations, not evidence of a current v6 failure.

Diagnostics export Re/Im/amplitude, valid arg only at amplitude>=0.2, rates only across consecutive valid endpoints and contiguous segments, and null reasons/denominators. Phase-coherence/target-phase/candidate fields must use declared amplitude-aware definitions or explicit not_run. Diagnostic-on/off action identity and death/absence cleanup remain required. The approximately 65-minute cost is extrapolated from v5, not a measured v6 duration; retain the bounded deadline/projection guard and report actual v6 cost if execution is separately authorized.

## Owner recheck and scoped disposition

The owner's verbatim request was sent to separate reviewer `s18_r3_recheck` under AGENTS.md. Its independent inspection corroborated R1/R2/N1 resolution, the native pressure/failure paths and the nonblocking complex-fixture note. This supporting recheck is Codex-family; the main review is cross-family against Claude's design. **Final-draft disposition:** the reviewer found no further blocker and retained N1. The upper-initial-amplitude arithmetic was corrected to n=48; this does not change feasibility or the verdict. No additional design repair was required.

The owner's prohibition on editing existing files takes precedence over the usual PLAN_CURRENT tracking location. This new file is the scoped review/disposition record; the plan maintainer should link it and track N1 with the implementation checks. Main .git is not writable (`test -w .git` returned false), so the review is left uncommitted as requested. No alternate checkout or bundle was created.

| Yes/no condition | Action | Responsible role |
|---|---|---|
| Is the amended design approved by this review? | Record design approval with N1 as an engineering fixture note. | drafter |
| Does any pre-fight numerical acceptance check fail? | Declare a revised integration policy before any fight. | drafter |
| Does integration exhaust its retry/cap or encounter a non-finite value? | Preserve the failed attempt and stop under the inherited runner rule. | implementer |
| Do positive regular and novice development gates pass without failures? | Draft S5 without executing its registered run. | drafter |

Stop condition: review complete, APPROVE_WITH_NOTES. Only this new review file is written; existing files and unrelated evidence are preserved.
