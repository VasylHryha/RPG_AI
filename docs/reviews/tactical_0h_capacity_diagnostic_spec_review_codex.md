CHANGES_REQUIRED
Reviewer family: Codex

Reviewed 2026-10-08: `CAPACITY_DIAGNOSTIC_SPEC.md` at
`94db744d25726331e8517e4f6d5c1898f6018715`, against the reproduced RD3
scratch source, DEBT spec including Amendment 1, DEBT usage, scheduler,
worker/report/telemetry, non-hashed cap configuration, and kernel builders.
Exploratory development review only; no experimental or scientific acceptance.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## R1 — blocking: the remaining admission ceiling defeats the negative diagnosis

The cost-only intervention changes two executable comparisons in RD3's
`kernel_builder/_worktrees/RD3/evidence/tactical_composition_demo/growing_shapes/medium/rev7_design.py`.
There are exactly three standalone `64` literals in that source:

| Line | Comparison | Meaning | Cost-only disposition |
|---|---|---|---|
| 365 | `sum(e[3]!='output' for e in elements)+1>64` | Ordinary-body count admission ceiling; returns `cap` before computing prospective cost | Retain 64 |
| 370 | `n+.1*pairs>64` | Prospective cost admission ceiling; returns `cost` | Replace with 96 or 128 |
| 499 | `while self.cost()>64` | D3 over-budget trigger | Replace with the same 96 or 128 |

The count ceiling is an executable resource constraint, not reserve wording.
Leaving it unchanged obeys the owner's cost-only scope, but means that a birth
at 64 ordinary bodies is refused even with unused cost headroom. Hypothetically,
a prospective population of 65 ordinary bodies with cost 90 is refused by the
count check before CAP96 or CAP128 evaluates its relaxed cost admission check.
This is an analytic illustration, not an exhibited geometry, simulated
trajectory or claim that these runs reach 64.

There is also a structural upper bound: with default `k=8`, each ordinary
receiver holds at most eight neighbors, so the union of charged ordinary
undirected pairs is at most `8*N`. With `N <= 64`, current cost is at most
`N + 0.1*(8*N) <= 115.2`. Thus CAP128's cost threshold cannot bind normally
admitted populations under this unchanged count ceiling; it does not provide
unrestricted access to 128 units of usable material.

Consequently, the spec's line 43 label **"Not budget-bound"** is not supported
by total service below the declared threshold. The result can be limited by
the retained count ceiling, growth quotas, search/geometry, or the finite
800-second growth horizon. Even removing the count ceiling would not make
absence of a service response prove that cost never binds. Relaxing a necessary
constraint need not improve the endpoint while another constraint remains.

The drafter must resolve the diagnostic's meaning before implementation:
retain the cost-only arm and describe a weak result as **no observed service
gain from relaxing the cost ceiling under the remaining RD3 constraints**;
or explicitly propose a broader admission intervention. Raising the ordinary
count ceiling as well is outside this task's cost-only authorization and cannot
be silently implemented as a constant replacement. A positive result supports
a service response to the intervention on these exploratory runs; it does not
establish proportional scaling, isolate admission from D3, or establish a
general route-efficiency law.

**Disposition: STOP before Step 2.** This changes the advertised bottleneck
diagnosis and requires the drafter's correction/choice. No CAP scratch build,
scheduler, telemetry, report writer, synthetic execution, or pilot was created
or run. The owner explicitly required stopping for a defect changing the arm's
meaning; this review does not resolve that choice by changing the design.

## Metric review and implementation notes for a corrected spec

**N1 — total service is defined, but it is a site-normalized coverage index.**
For each site `s`, pool `active_served_steps` and `active_steps` across precisely
the ten observer-on runs (five keys, both starts), then compute
`f_s = sum(active_served_steps_s) / sum(active_steps_s)`. The declared total is
`T = sum(f_s for s in range(8))`, dimensionless, range 0–8. The off controls
are excluded. Structural service retains all physical-site roots, strict
radius-3 reach and directed strong reachability to O; active service additionally
requires positive drive strength. Counts use the revised observer's settled
post-growth 0.1-second boundary. Missing runs, denominators or failed integrity
must withhold a reading. This index is not a count of simultaneous active
service and is not summed delivered signal or the F5 gate. The active exposures
are unequal between sites, so its weights differ from pooled served site-time.

Read-only arithmetic on the ten committed RD3 summaries gives:

| Site | Active steps | Active-served steps | Pooled fraction |
|---|---:|---:|---:|
| 0 | 54720 | 26885 | 0.4913194444444444 |
| 1 | 54400 | 32737 | 0.6017830882352941 |
| 2 | 52800 | 17482 | 0.33109848484848486 |
| 3 | 61120 | 11548 | 0.18893979057591623 |
| 4 | 58240 | 1129 | 0.0193853021978022 |
| 5 | 57920 | 3352 | 0.05787292817679558 |
| 6 | 52160 | 3706 | 0.07105061349693252 |
| 7 | 53120 | 20511 | 0.3861257530120482 |

`T_RD3 = 2.147575404987718`; four sites have pooled fractions >= 0.30.
The literal ratio thresholds are `1.5*T_RD3 = 3.2213631074815767` and
`1.15*T_RD3 = 2.4697117157358752`. The spec's 3.22 and 2.47 are display
approximations, not interchangeable decision cutoffs. Define "between" as
inclusive `T_RD3 <= T_CAP96 <= T_CAP128` before execution. Apply any reading
only after both complete ten-run arms and both integrity pairs are verified;
partial results remain descriptive/incomplete. Report start-specific and paired
per-key values alongside the declared pooled index, without replacing it.

**N2 — distinguish telemetry from policy constants.** The unchanged coverage
observer hardcodes `cap=64` in `event` (line 129) and `growth_end` (line 156).
The economy observer has analogous fields at lines 186 and 213. These are
reporting values, not admission checks. A future capacity observer must report
the actual cost cap plus the separate ordinary count ceiling, with new-file
overrides or proven compatible additions that preserve historical summaries.
Reuse Amendment-1 transition/restoration semantics and RD3 removal
classification. Existing observers and committed summaries must remain intact.
Neither the active RD3 source nor its runner contains a 64-based reserve
calculation to rescale. The scratch harness's `t > 640` late-window selector
remains unchanged. Historical `design_0h.py` and `rev6_design.py` have their own
64-based policies; they are not the active RD3 law and must remain unchanged.
Unsigned 64-bit seed bounds, historical test fixtures and world verification
batch counts also remain unchanged. Do not use a subtree-wide replacement.

**N3 — give the time-series metrics their own denominators.** Record both
`len(served)` (all-site structural service) and `len(active_served)` on the
settled observer boundary. For cost per served site, declare which count is
the denominator; report both if useful, use null plus an explicit zero-service
flag when that count is zero, and retain total cost. Do not turn zero service
into a zero-cost ratio. Class mass uses ordinary bodies plus 0.1 per undirected
ordinary held pair, allocated 0.05 to each endpoint; O and incident pairs remain
free. Existing `mass_allocation` provides this conserved accounting. These
measures diagnose material distribution, not delivered response; retain A/B/E
and gate shape separately.

**N4 — DEBT documentation drift is not an arm change.** DEBT_USAGE.md and its
report writer still describe unresolved fairness aggregation, whereas the
committed spec's Amendment 1 resolves it as the minimum over eight pooled
site fractions. Do not inherit that stale ambiguity into capacity aggregation
or alter committed DEBT results in this task. The inspected local DEBT runtime
cap is 9000 seconds; its default remains 5400. Capacity's proposed independent
config must default to 5400, remain outside completion identity and be recorded
at launch. This compute-time cap is distinct from the scientific cost ceiling.

## Recheck, scope and provenance

The verbatim request above was sent to independent reviewer agent
`capacity_spec_recheck`. Its review is a separate Codex same-family fallback,
not Claude cross-family acceptance. Recheck findings and disposition are
recorded here under the owner's explicit prohibition on editing or staging
`docs/PLAN_CURRENT.md`; no plan update is implied.

The independent reviewer corroborated R1 and the three-use inventory,
independently derived the 115.2 bound, confirmed the pooling and ratio-threshold
notes, and recommended CHANGES_REQUIRED/STOP. Disposition: retain R1 and stop;
add the bound above and leave the drafter's intervention choice unresolved.
The same reviewer then checked the completed review draft, found no additional
defect, and suggested making the 65-body example explicitly hypothetical;
that wording correction is included above. No numeric quality score was given.

Reviewed identities (observations only, not an execution hash manifest):

- Capacity spec SHA256: `62b80f4c2ec50153c796076226533b45dd52955f5769a31de7edb0b4eda54d30`.
- RD3 scratch Python SHA256: `4136cac62614cb5d2d0f7d4115c2f39d85ee0e83ea0e6ee2113ef59f153b07c1`, matches `RD3_BUILD.json`.
- Committed `SERVICE_RUN_SUMMARIES.json` SHA256: `808f1b0485e647980022a2ed52e644ec5e4990ac646da58fba9044829828616f`.

Only read-only source inspection and standard-library arithmetic over stored
JSON occurred. No project tests, native load, benchmark, process listing,
assay, panel or pilot occurred. No existing source, design, plan, status or
committed evidence was edited. Delivery contains this review only; if primary
Git metadata remains read-only, a normal-hook commit in a project-local clone
and verified incremental bundle carry it from the reviewed HEAD.

| Stop condition | Yes/no | Action | Responsible role |
|---|---|---|---|
| Does the unchanged admission count ceiling invalidate the declared negative bottleneck diagnosis? | Yes | Correct diagnostic scope/readings before Step 2 | Drafter |
