CHANGES_REQUIRED
Reviewer family: Claude
Reviewer model: claude-opus-5-5 (with a Claude sub-agent for the module-by-module pass)
Reviewed: C6 step 2a by Codex (gpt-6): geomind/c6_levels.py, c6_units.py, c6_compose.py, c6_effective.py,
c6_experiment.py, tools/c6_design_gate.py, and the additions to tests/test_c6.py (uncommitted working tree).
Plan: experiments/c6_proposal.md with amendments A1 and A2.

Tests: 95 passed in about 8.5 s; no simulations were run by the review. The sub-agent timed the
alternative-grouping search and the union fragmentation on synthetic geometric fixtures only.

## Blocking

- **D1 (high): `alternative_groupings` does not finish at transition-2 sizes.** `c6_levels.py:275-299`.
  - *The cause:* an exhaustive depth-first search with no pruning. On 35–58-element 8-nearest-neighbour graphs it
    found nothing in 40 s in 4 of 4 cases.
  - *A second defect:* it samples with replacement when fewer than K exist.
  - *The fix:* implement the registered seeded constructive sampler of amendment A2 (§5): no replacement, dedupe,
    at most 2,000 attempts, NOT_TESTED at zero. Add a realistic-size test.
- **D2 (high): amendment A1 is not implemented.** `tools/c6_design_gate.py:255-285`.
  - *Order:* evaluate stop rules 2 and 3 on the pass-1 τ, immediately after pass 1 and before pass 2.
  - *Rule 2:* fewer than 5 measurements, or 50% or more censored, for τ₁, τ₂ or τ₃. Add the minimum of 5 to
    `cumulative_C` as well.
  - *Rule 3:* C₂ outside [1.6, 6.4].
  - *Cleanup:* remove the obsolete rule-8 branch and the later checks for rules 2 and 3.
  - *Test:* pass 2 is never scheduled after a rule-2 or rule-3 stop.
- **D3 (medium): nested criterion 6 uses too short an observation interval.** `c6_levels.py:168-182`.
  - *The defect:* the recursion passes the child's C as the parent's, so level-1 units inside a level-3 group are
    observed over 30 C₂ instead of W = max(30 C₃, 30 C₁) (§4).
  - *The fix:* carry the top-level W and its frames through the recursion. Add a test in which a level-1 unit
    breaks only early in the level-3 window.

## Medium and low

- **D4 (medium): interface fidelity.** Use the independent observed-rate run and the mean comparison of amendment
  A2 (stop rule 4). The current version is vacuous on rate and applies `any(...)` per parent on capacity.
- **D5 (low–medium): check-4 banks.** Label the check-4 harvest banks as inputs only (amendment A2), and make sure
  no later number reuses them.
- **D6 (low): level-1 isolated rate.** Level-1 templates set `isolated_rate=0.` without measuring it. Measure it
  with the same isolated-rate rule as level 2, and add a contract that it equals ω_g within the estimator's
  resolution.
- **D7 (low):**
  - `same_rule_audit` must compute, not hard-code, its check that the recipe and port variant are the same at both
    transitions.
  - A rule-14 stop must add a `stop_rules` row.
  - Fix the `interface_fidelity` docstring.
  - Re-project the gate runtime: the bank sizes (about 600 level-2 and 4,800 C4 harvest worlds per level-3 bank per
    pass) exceed §9's estimate.

## Required before the gate run

Rerun `tools/c6_design_gate.py --smoke` after these fixes. The first attempt hit the exact-union fragmentation;
the repaired routine measures about 0.65 s per 31-frame check at level-3 sizes. Report the projected full-gate
runtime.

## Sound (no defect found)

- one `detect_level`, with no branch on level number;
- top-level criterion 6;
- publication: measured rates, sibling-folded capacities, fake parts published identically;
- unit specificity apart from D1: probes drawn first, linear summaries, a membership-only decoder, pairwise
  exclusion, an uncorrected primary statistic, the diagnostic's NOT_COMPUTED rule, L*;
- the E2 recipe and the shared linear input;
- the coarse scoring: six gains, the r floor, certified censored bounds;
- placement and rate shift; harvest isolation;
- entropy restricted to 33333;
- smoke never writes to evidence/.
