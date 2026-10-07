APPROVE_WITH_NOTES
Reviewer family: Codex
Reviewed HEAD: 50ab49dfd089b5b4262c0113160e264b17c346ea

Bounded round-2 static review of DESIGN_0G §§19.6–19.8.1, the prior R1–R6 review, S4_RANGED_THREAT_DIAGNOSTIC.md, spacing POLICY/DECLARATION/common/run/engineering/analyze/render, and controller observation, spacing, focus, bridge and catalog sources. No fights, judging entropy or process listing occurred during this review. §19.8.1 takes precedence. No defect changing the arms' meaning was found; conditional implementation may proceed.

| Prior finding | Disposition |
|---|---|
| R1 movement | Resolved: ranged action uses native-clipped goal; multiplier 1 iff centre error >2 px, otherwise 0; stop0. Gun decisions exactly P11; prepared v6 ranged target preserved. |
| R2 direction | Resolved: hp>0 filters, own/enemy nearest id ties, inclusive400, fixed-id centroid, <1e-9 fallback chain and complete v6 degenerate fallthrough are total and observation-only. No remembered direction or world/shell access. |
| R3 collision/clearance | Resolved: current gun centres; no avoidance, lane, clearance correction or reassignment. Native collisions, clipping and spacing remain unchanged; blocked realization is audited. |
| R4 measurement/readings | Resolved: prepare-point/post-centre arrival, raw/clipped separation, living prepare cohort, strict event cutoffs, native pair reach, unit-tick opportunity denominator, capped HP, opposing last hits, separate friendly damage and declared categorical comparisons. Implementation must seal the remaining reporting details before fights. |
| R5 control | Resolved: all40 P11 fights reported first, flag regular MEAN enemy gun kills<4 or MEAN own gun losses<7, no abort and no P5 window. |
| R6 execution | Resolved by contract: pgrep before each combat block/resume; timestamped attempts, identities, skip verified completions, never replay ambiguous claims, claim only after clearance. Must be implemented and exercised without combat in Codex. |

Findings (nonblocking reporting clarifications, no arm changes):

1. **Medium — name the side of the spacing reading.** Seal “spacing lost” as successful OPPONENT gun-targeted shells' distinct OWN gun victims >1.5, following §19.7's own-guns-damaged table and §19.6's enemy-shell measure. Report both teams and incidental targeting separately; an own shell damaging several enemy guns is not lost own spacing. Null denominator gives unavailable, never false/pass.
2. **Low — separate nominal clearance from realization.** Catalog splash40+ranged-body9+gun-body10=59; rounded up as declared to60, second declared dose120. The assigned-gun exclusion bound is49, with gun radius extra margin. The raw60 point meets it, but clipping and the20px arrival band can violate it (a40px achieved offset is within49). Report raw/clipped assigned-gun clearance and actual centre distance; arrival alone is not splash safety. Other guns can coincide with escort points, including spacing-shifted gun goals; audit rather than move/reassign escorts. Shared goals are allowed.
3. **Low — seal first-arrival/holding and unavailable cohorts.** Count degenerate direction and post-step death in the living-prepare denominator; null point/dead post centre is unavailable, not silently excluded or arrived. Declare first arrival by unit and consecutive holding (and reassignment), exact pooling/quantile convention, bins and phase/window clocks before fights. P11 may carry an output-only counterfactual d60 audit; it must never change P11 actions. Report native guard holds separately.

All needed ids, positions, hp, roles, range/radius and bounds are controller observations. The shell diagnostic is evaluator-only. P11 is a soft goal shift, so neither nominal S60 nor d60 ensures achieved spacing. The new thresholds are descriptive development readings, not rates, permission for v7, or source/resonator qualification. Zero kills under unchanged targeting does not refute positioning.

Owner recheck request, verbatim, sent to the separate read-only reviewer `escort_round2_recheck` (Codex same-family fallback; no Claude tool available):

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Recheck disposition is recorded here because the owner forbids PLAN_CURRENT edits. Reviewer independently confirmed R1/R2 resolved and no meaning-changing blocker; the side/clearance cautions are incorporated above. Final recheck: APPROVE_WITH_NOTES, R1–R6 resolved, no new arm-meaning defect. Its medium side-definition and low clearance/unavailable-cohort findings are retained above and will be sealed in POLICY.md before fights. This is design approval with reporting notes, not acceptance of an unexecuted probe.
