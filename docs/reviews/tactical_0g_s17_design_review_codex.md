CHANGES_REQUIRED

Reviewer family: Codex
Reviewer model: GPT-6
Design SHA256: a58f56d9931f5fa47b046ad43b998f32e6acf9bcc0eb348fa9d0ec26c3a60641
Design: evidence/tactical_composition_demo/DESIGN_0G.md, section 17, revision 9 (v5)
Reviewed repository HEAD: 273dd1d

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

This is Codex's cross-family review of Claude's section-17 design. Read-only inputs: AGENTS.md (including Owner recheck), DESIGN_0G sections 13–17 and the inherited score/panel contract, S4_ATTRIBUTION_REPORT.md, S4_V4_RECHECK_REPORT.md, S4_AMENDED_PROTOCOL.md, S4_V4_PROTOCOL.md and the current panel/request code. No project execution, build, tests, fights, tuning, judging or registration was performed. Historical measurements were inspected, not recomputed.

## F1 — High, blocking: stage C cannot calculate the specified tuning objective or constraint

Section 17 lines 487–491 retains the amended CMA-ES protocol and the same budgets, but specifies regular-head tuning mean S with a novice tuning mean constraint. It explicitly exempts stage A only.

The inherited C tuning allocation is **one two-orientation cluster per each of the 19 elite-no-rollout doctrines**, with no novice or regular head. See S4_AMENDED_PROTOCOL.md lines 5, 7 and 9, and s4_v4.py lines 56–65. Novice and regular full heads appear at C only in the separate validation panel. s3_runner.py also requires a doctrine for s4_p23; an elite doctrine result is not a regular-head result.

Consequently both required C tuning means are undefined. This matters even for Part 1: a runner that successfully passes B would reach an undeclared C selection procedure. Dropping C silently is not the requested implementation.

The drafter must declare how C works before implementation. For example, explicitly limit the new rule to B and retain a stated doctrine objective for C, or define a new C tuning allocation containing the two heads and reconcile its doctrine coverage, equal budgets and cost. These are alternatives requiring a design decision, not reviewer-selected fixes. Adding head fights to all 19 doctrines increases the declared 9,766 evaluations per arm/stage; replacing doctrines changes the inherited allocation. Using C validation to supply either mean violates the separation of selection and validation. Do not implement any of those changes by inference.

## F2 — Medium, interpretation: pair switching does not identify coherent unit intent instability

Section 17 line 478 concludes that instability of the mode is not the main cause of losing to regular. The attribution supports the narrower conclusion that **this pair-hold intervention reduced pair-mode changes without improving regular outcomes at fixed v3 knobs**.

The report distinguishes pair-mode changes from latent unit-intent proxies and physical movement reversals. In the five predeclared regular trace seeds, both orientations (ten fights per arm/cell), resonator pair changes fall from 891.886 to 139.242 per living unit-minute, while latent proxy changes remain 33.263 versus 33.341. Actual movement reversals were not measured. The v4 recheck explains that held pairs do not form a coherent unit decision. This intervention therefore does not rule out instability of coherent unit intent as a contributor. The drafter should narrow the causal statement; retaining v3 as the implementation baseline remains reasonable.

## F3 — Low, interpretation: selected omega is a diagnostic, not a necessity test

Section 17 line 493 correctly requires selected role omegas to be reported. Selection near zero would describe what this bounded optimizer selected on its finite tuning panel. It does not independently demonstrate that rotation is unhelpful: the optimizer can trade off other knobs, and the design has no matched zero-omega ablation. State this as a diagnostic finding, with the selected values retained even on a B stop. No extra ablation is requested here.

## Resolved details and implementation notes after design repair

- The owner's current task supplies the exact B gate: finish all-arm B validation, then proceed only if the resonator's regular validation mean S is **strictly greater than −7.62**, the attribution baseline. Equality stops. This resolves section 17's rounded −7.6; it is a development resource gate, not statistical superiority or beating regular on S.
- At B, calculate each head mean from its own tuning clusters after averaging orientations: ten novice and nine regular. Novice mean **0 meets** the tuning constraint; a negative novice mean ranks below every eligible candidate regardless of regular score. Apply the same ordering to optimizer feedback and retained incumbents. Rank within each eligibility group by regular mean S, retain earlier exact ties and report if the selected candidate is ineligible. Keep the inherited positive-novice A/B validation stop distinct from tuning eligibility.
- Preserve v3 policy/action behavior and the labelled H/F/HF/v4 variants. Use identical rules and unchanged 11/11/3 dimensions across the substantive arms. Validation must never choose knobs. Declare fresh development entropy before execution and retain the bounded absolute deadline, cleanup and 360-minute allowance.
- S remains survivors minus enemy survivors. Gun counts, timeouts, damage and elimination times remain descriptive; they cannot break an S tie. A regular score above −7.62 may still be negative. No P1, S5 or scientific acceptance follows from that gate.

## Mandatory owner recheck and disposition

The exact owner request above was sent to the separate reviewer `design_recheck`. Its initial tentative APPROVE_WITH_NOTES was revised to **CHANGES_REQUIRED** after inspection of the C allocation. It independently confirmed F1 against the protocol and runner and corroborated F2. Only Codex-family collaboration reviewers are available in this session; this additional same-family check is distinct from Codex's cross-family review of Claude's design and does not establish independent implementation acceptance.

The separate reviewer also checked the final review and scoped record against source references and hashes and found no required corrections. Its optional trace-coverage clarification was incorporated above. F1 remains unresolved and belongs to the drafter. F2/F3 are interpretation corrections for the drafter. Per the owner's conditional Job 2, no v5 implementation, readiness claim, build or affected-test run is authorized by this verdict. The scoped recheck/disposition record is astelia_cpp/s4_v5_checks/PLAN_AND_REVIEW.md. The explicit instruction not to edit docs/PLAN_CURRENT.md or DESIGN_0G.md takes precedence over the repository's root-plan update instruction.

| Yes/no condition | Action | Responsible role |
|---|---|---|
| Does C lack its declared tuning score/constraint allocation? | Repair section 17 before implementation. | drafter |
| Does this design review return CHANGES_REQUIRED? | Stop conditional Job 2 and deliver the review. | implementer |
| Has the repaired design received an approving review? | Implement Part 1 within the owner's scope. | implementer |

Stop condition met: CHANGES_REQUIRED. This completes Job 1; Job 2 was not started.
