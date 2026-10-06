APPROVE_WITH_NOTES

Reviewer family: Codex
Reviewer model: GPT-6
Design SHA256: 5ca80142c8c6f4bd5dce951cb726d961b0dd36c470513ddb2e89b8cfe0e8caa4
Reviewed: DESIGN_0G.md sections 14–16, especially section 16; S4_V4_RECHECK_REPORT.md; historical native policy and v3 stage-B knob artifact. This is Codex review of Claude's design, not review of Codex's implementation or run approval.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

The common-input, fixed-v3-knob factorial design isolates hold/focus effects for these policies at these knobs. No blocking design defect remains. Implement exactly the historical rules, including all-living-enemy focus selection, initial unheld modes and same-tick rearming after release. Adding the recommended v5 safety rules here would confound attribution.

Findings and required implementation clarifications before fights:

1. **Medium — inference unit and interaction.** Average the two orientation scores within each seed before computing each endpoint's mean and descriptive normal 95% interval over 100 seed clusters. Compute all six paired cell differences and HF−H−F+v3 on common seed clusters. No hypothesis verdict, superiority claim or multiplicity-adjusted acceptance follows from these descriptive intervals.
2. **Medium — unit intent does not yet exist as a policy object.** Report the latent per-unit commitment hysteresis proxy (initialize c≥0, switch at c>0.2/c<−0.2) explicitly as `unit_intent_proxy_changes`, distinct from `pair_mode_changes` and unit ticks with any pair change. Focus while escaping means focus is present with that latent proxy in escape; also report the narrower c<−0.2 count. Neither is a measured physical movement reversal or a coherent v5 intent.
3. **Medium — death and terminal accounting.** Hold-release counts are pair events, not unique deaths. Split own/enemy/both death and missing-unit releases. Reconcile active holds at terminal state because a final death need not be followed by prepare. Separate living-pair censoring. Expiry exposure uses prepare-position legality against any living enemy artillery, between minimum and maximum range, inclusive, excluding its dead zone; this measures coincidence, not caused damage or a mode flip.
4. **Low — trace allocation.** Predeclare five common regular seeds across cells and arms, both orientations; capture their full decision traces during the existing 3,200 fights, with zero extra replay fights. Keep raw traces and their hashes.
5. **Low — historical claim and cost limit.** HF means the v4 skeleton with v3 knobs. This diagnoses fixed-knob effects on fresh seeds, not the exact decomposition of the historical independently retuned v3→v4 package regression. The historical ten-minute estimate assumes ten workers and does not price trace overhead or a quiet-machine constraint. No v5 choice, tuning, judging or S5 execution is authorized by this review.

Separate mandatory owner recheck: the verbatim request was sent to collaboration reviewer `s16_recheck` (Codex; Claude family unavailable in this interface). It independently returned APPROVE_WITH_NOTES with the same counter, clustering, terminal and historical-claim clarifications. No project code, tests, build or fights were run for design review. The scoped plan/disposition is in astelia_cpp/s4_attribution_checks/PLAN_AND_REVIEW.md; the user's explicit scope excludes editing docs/PLAN_CURRENT.md.
