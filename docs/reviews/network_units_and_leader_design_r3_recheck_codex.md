PASS — prospective design recheck after corrections
Reviewer family: Codex
Date: 2026-10-08
Review type: separate-agent owner recheck of prospective design revision 3; same family, not cross-family. This is neither execution approval nor milestone acceptance.
Reviewed design SHA256: `205c9caf2a27d351276f6f873ef1f7f9269a69573e18e1d154ed2f586265f32a`
Reviewed decision 0037 SHA256: `6f24c00221eedeb568579781626f1081b2b52a86f360c40e035de25cfcbd6430`

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

I read AGENTS.md, the entire revision-3 design, decision 0037 and every finding in the revision-2 Claude review. I inspected documents and computed document digests only. I ran no Python, tests, project code, collection, fits, fights or fixtures and did not open `_local/`, training artifacts, code or PLAN_CURRENT.md. The parent reports Claude authentication is unavailable; this report honestly identifies the separate reviewer as Codex. Findings go to the drafter for correction; I do not edit the design.

## Ranked findings

### Medium

**R3-1 — Insufficient conditional-command coverage can pass the working-S2 gate.**

Where: §5 S2, lines 147 and 153.

The stop asks whether legal focus/deadline obedience is below 95% **over at least twenty eligible commands**. With zero or nineteen eligible commands, that condition does not fire. The surrounding start-opportunity row checks a different denominator, so it does not close this gap. A working S2 can consequently admit a full-army bridge or S3 with an unmeasured command interface. S3 also says U must pass timing obedience without declaring whether the twenty-command count applies separately to focus, hold and deadline.

Fix: define the command types that must be checked at each stage and fail coverage explicitly when any required type has fewer than twenty eligible commands. For each required type, define the obedience numerator and opportunity denominator. S2 may use the already declared synthetic legal timing commands to qualify frozen U without claiming learned leader timing. Make the working-S2 sentence and stop row reference the same definition.

**R3-2 — The timing gate says “bulk collection”, whereas the owner required the sample before any S3 collection.**

Where: §5 S3, lines 185, 187 and 218; §7 line 268.

The sample source is correctly limited to frozen training/validation logs and unavailable states correctly require a separate fixture amendment. However, every operative timing stop is scoped to **bulk** collection. That leaves a route to collect fresh “small” S3 visits before the search-cost admission, despite the current owner's explicit “before any S3 collection” requirement. It also weakens the drafter's self-audit closure of N-L3.

Fix: require the completed sample and query/fit/memory projections before **any new S3a/S3b state/data collection**, with the sole declared exception being the at-most-twenty-state timing sample drawn from existing approved logs. Keep unavailable-source fixtures behind their already required separately authorized amendment. Use that wording consistently in the prose, stop row, resource paragraph and self-audit.

### Low

**R3-3 — Fixed-point admission is stated as both an individual-row veto and a 95%-coverage check.**

Where: §3 line 65 versus §5 S1 line 130 and S2 line 151.

The intercept definition says residual exceeding splash/4 on an unforced release-opportunity row returns to oracle/support revision. The stop rows allow up to 5% of such rows to exceed that bound, combining snap and fixed-point error. Implementers cannot tell whether a single excessive fixed-point residual blocks admission or is counted within an allowed tail.

Fix: choose one rule explicitly. A reasonable distinction is zero invalid/nonfinite intercepts and a strict splash/4 bound on the analytic fixed-point residual, alongside at least 95% splash/4 coverage for discretized aim snapping. Name the denominators and distinguish undefined/forced rows. Align the prose and both stops without relaxing a threshold after outcomes.

**R3-4 — “Conservative” chi-square upper spread assumes a sampling model not stated in the design.**

Where: §5 S1 line 113.

The chi-square upper-SD formula is a Gaussian-pair-difference construction. It is not generally a 95% upper bound for discrete deaths, sparse kills, bounded/mixture damage or exchange jackknife pseudovalues. The text does call the MDE a normal approximation and disclaims guaranteed student power, which is good, but repeatedly naming the spread/MDE conservative still implies more protection than this distributional calculation establishes.

Fix: explicitly state the Gaussian approximation behind the upper-SD estimate and call the MDE a planning estimate, not a distribution-free conservative bound. Before outcomes, seal the actual paired confidence-interval method for additive axes, ratio-of-totals contrasts and harm bounds. Define what happens for sparse/degenerate estimates; do not choose the method after seeing outcomes. Retain both ordinary and uncertainty-inflated estimates and all pilot counts.

## Traceability to the revision-2 Claude findings

| Finding | Revision-3 disposition in the reviewed text |
|---|---|
| N-H1 | Addressed prospectively. Owner quote and 0037 are present. The search sidecar is allowed for labels in both stages; students have explicitly flagged privilege in S3a only. S3a forbids all RRG-state claims. S3b removes student channels structurally, audits public-history recoverability, trains P0, and admits a stateful R/P reading only after a same-cell validation and paired useful P-over-P0 gate. Child-state leakage to P0 is honestly acknowledged rather than hidden. |
| N-M1 | Addressed prospectively. Focus/assignment/shape are fixed at start; exactly one actual-distance aim refresh happens at the first release opportunity, before aim lock, even if U declines release. S1 pairs shadow misses for the same gun/focus/release instant, reports raw and shape-subtracted error, and stops on mean excess above splash/4. Finite coverage is explicit. R3-3 concerns the separate intercept/support admission rule. |
| N-M2 | Addressed with the R3-1/R3-3/R3-4 residuals above. Per-cell paired SD, MDE at 100/200, saturation and roster/HP-scaled useful/harm thresholds are present and sealed before outcomes. Teacher-rate under-firing is numeric; utility and tradeoff stops have declared criteria. The remaining coverage and statistical-method ambiguities should be corrected before closure. |
| N-M3 | Addressed. S2 has the two teacher reference arms on the same five-arm paired outcome panel, explicit U/teacher and leader/teacher gaps, and the added outcome cost. The full-army historical script result does not replace drill references. |
| N-M4 | Addressed prospectively. Relevant volleys are root-commanded casts, with failures retained in the attempted denominator. Every scored candidate has a common t+3 cutoff and its own common-controller continuation to t+6. Latest-start next-cycle coverage is derived and measured before labels, with prospective horizon revision if necessary. Immediate-only reranking, score change and throughput are reported. Six seconds remains a finite-horizon limit, not a universal guarantee. |
| N-L1 | Addressed. Cycle one is search-teacher distillation; later apprentice-guided cycles are distinguished. Parking is explicitly restricted to this artillery timing slate. |
| N-L2 | Addressed. The P spatial prior's teaching bias is declared, and an R spatial deficit under those labels is excluded from RRG evidence. |
| N-L3 | Formula, per-candidate-tail accounting, query/fit/RSS projection and an at-most-twenty-state sample are present. R3-2 is the remaining discrepancy with the owner's stricter timing of that gate. |
| N-L4 | Addressed. Operative S2/S3 controller, label, continuation and value rules now use full sentences. The S3a/S3b split is visible and plain. |

Decision 0037 records the date, owner as decision maker, Codex as recorder and the owner's words verbatim. It separates Learning by Cheating from related asymmetric actor-critic rather than claiming the exact same algorithm. I found no conflict between that decision and the core staged privilege design. No empirical claims or numeric quality scores are assigned.

## Disposition

The drafter must fix R3-1 through R3-4 and record each cause/fix in the design self-audit. This report is the recheck record because the owner forbids editing PLAN_CURRENT.md. A corrected-text reread and final digest will be appended here after correction; the initial reviewed digest and findings remain intact.

## Final corrected-text reread

Date: 2026-10-08. Reviewer family: Codex.

Final reviewed design SHA256: `1522b1a743625a4fccd2d629cfb4c207ae6d0e0e60bd7ec23fb592e3b3465fc9`
Final reviewed decision 0037 SHA256: `6f24c00221eedeb568579781626f1081b2b52a86f360c40e035de25cfcbd6430`

I reread the drafter's corrected measurement, command-interface, collection-admission, stop and self-audit text. I checked that the corrections preserve the owner decision and the original N-H1/N-M1..4/N-L1..4 resolutions.

| Finding | Corrected-text disposition |
|---|---|
| R3-1 | Resolved. Focus, hold_start and start_at have separate opportunity/success definitions, counted safety exclusions, at least twenty eligible commands per required type/cell and at least 95% success. Sparse coverage explicitly blocks; the same qualification governs working S2 and U frozen for S3. |
| R3-2 | Resolved. Cost/timing admission now precedes any new S3 state/data collection. The default exception is the declared at-most-twenty-state timing sample from existing approved logs. Missing source states require a separately authorized sample-only fixture amendment and cannot silently authorize fresh S3 visits. The prose, stop, resource paragraph and self-audit agree. |
| R3-3 | Resolved. Invalid/nonfinite intercepts and any analytic fixed-point residual above splash/4 block. The 95% coverage rule applies separately to snapping on unforced release rows. S1/S2 stops agree with the strict residual statement and retain forced/undefined counts. |
| R3-4 | Resolved. Gaussian/chi-square assumptions are explicit; ordinary and uncertainty-inflated planning estimates replace claims of distribution-free conservatism. Paired t and jackknife/t intervals are sealed before outcomes. Sparse/degenerate primary benefit is unestimable, exchange denominators must qualify, and sparse additive harm uses a bounded one-sided exact-binomial fallback. The latter conservatively bounds expected positive harm by maximum positive harm times the upper probability of a harmed pair, while retaining raw axes and limits. Actual-student contrast spread/MDE is checked on the already planned separate mechanism sample before fresh outcome entropy. |

The drafter records each finding's cause and fix in the revision-3 self-audit. I found no remaining blocking document defect in the corrected design or decision. All nine revision-2 Claude findings are addressed prospectively, including the owner's staged privileged-state exception. The first-line verdict has been updated to the final corrected-text verdict; initial findings and initial hashes remain unchanged above.

This PASS qualifies the prospective design text only. It does not qualify a training run, prove effect size or recoverability, approve execution, establish RRG state, accept a milestone or certify full source recursion. No Python, tests, project code, collection, fits, fights or fixtures were run for this reread. The protected job, `_local/`, code, existing reviews and PLAN_CURRENT.md were not opened or modified. No numeric quality score is assigned.
