APPROVE_WITH_NOTES

Reviewer family: Codex
Reviewed design: evidence/tactical_composition_demo/DESIGN_0H_REV7.md, section 12 (revision 7.5), with sections 9.2/9.4 and 11/11.1 as governing context.
Design SHA256: 72b51ee1723a0b24c02755be352155c48d3673cc61ec5dec082e35aeed53f696
Evidence read: growing_shapes/runner/REV74_FIXTURE_REPORT.md. No project code or fixture was run for this design review. Standalone arithmetic used only math/hashlib/pathlib and the equations read from source.

Owner request (verbatim):

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

The bounded recipe change is sound. The old rotating-frame phases (pi, 0) cancel both site and member sine terms in exact arithmetic, even as geometry changes. They lie on an unstable phase branch. The offset pi - 0.5 removes that exact symmetry without changing geometry, gain, duration, solver, tolerances or the accuracy gates of N1a-f. Keeping the old recipe as descriptive N1g preserves visibility of that difficult start without pretending to certify its trajectory accuracy. This is explicitly outcome-informed engineering evidence; the 7.4 FAIL stays unchanged.

Findings and implementation dispositions:

1. R75-1 (LOW, diagnosis precision). 32*2*exp(-0.3^2/2) = 61.18383884/s is the initial site-drive derivative only. At member separation 0.256, the initial frozen-geometry phase Jacobian in the rotating frame is [[91.15392939, -29.97009055], [-29.97009055, -33.96798742]] /s, with eigenvalues +97.96212728 and -40.77618531 /s. A 1e-16 unstable-mode perturbation grows to order one in about 0.376 s at these initial coefficients, rather than the drive-only 0.602 s estimate. Geometry changes, so neither is a measured escape time. The saddle diagnosis is supported, but the receipt alone does not prove the complete causal history or eliminate every solver defect. "Two step sizes cannot agree, however accurate" is too categorical: finite precision can choose different branches; agreement is possible, and a convergent exact-arithmetic calculation is not ruled out. The lambda=8 historical PASS is consistent with slower amplification, not proof of its sole cause. Disposition: qualify these statements in the integration report; no design-file edit within this task's scope.

2. R75-2 (LOW, coverage wording). Member 0 at (3.7, 0) is at the r0=0.3 boundary in exact arithmetic, not strictly inside. Member 1 at (3.956, 0) is 0.044 from the site and is strictly inside; thus the two-member case retains the intended inside-cutoff coverage. The site radial bracket for member 0 changes from -3.13333333 to -3.03539938 (96.8744% of its old repulsive magnitude). Its initial rotating-frame phase rate is -43.70152169 rad/s, with member coupling and drive both selecting the lower-phase branch. There is no phase/position pin, no tolerance relaxation and no new initial clearance requirement. Disposition: state boundary/inside coverage accurately and verify both literal members synthetically. A future PASS remains unmeasured here.

3. R75-3 (LOW, descriptive measurement contract). "Slip direction and time" needs a fixed operational definition. Implement N1g with the unchanged old two-member recipe and 16 s horizon at both existing h values. Report member 0's first endpoint departure of at least 0.5 rad from its unwrapped carrier-relative initial phase pi; direction is the sign of that displacement, time is the first 0.1 s endpoint crossing, with the preceding endpoint as a bracket. This is an escape/branch diagnostic, not a literal completed 2pi winding: report final unwrapped phase/displacement separately. If no crossing occurs, direction/time are null and status is NOT_OBSERVED. Retain both raw integrations and descriptive discrepancy/validity measurements. N1g must have verdict DESCRIPTIVE and used_in_verdict=False, and be excluded from every N1 numerical-cut reduction. Structural/nonfinite data remain INVALID under the existing harness rule; that is data integrity, not a new slip/accuracy gate. Disposition: pin the convention in configuration and test opposite branches, censoring, endpoint timing, whole-turn unwrapped information and gate exclusion with fabricated records/stubs only.

No blocking design finding. Approval covers only implementation and the owner's requested affected synthetic suite. N1/F1-F9, training, development, panels and scientific acceptance remain outside this review and task. Claude implementation review of the final tested identity remains a separate gate. docs/PLAN_CURRENT.md is untouched under the owner's explicit restriction; dispositions are tracked in this review and the scoped integration report.

Assisted-by: Codex:GPT-6
