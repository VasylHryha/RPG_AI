CHANGES_REQUIRED
Reviewer family: Codex

Reviewed 2026-10-08 at HEAD `51fe434922c7737ee1dc6db775be2eb2f45a0c1d`:
`CAPACITY_DIAGNOSTIC_SPEC.md` including Amendment 1, the round-1 Codex review,
`DEBT_PILOT_SPEC.md` including Amendment 1, DEBT usage, scheduler, worker,
report writer, observer and local compute-cap config; the kernel builders,
RD3 build receipt, reproduced scratch source, harness and service geometry.
Exploratory development review only; no experimental or scientific acceptance.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## R1 — blocking: Amendment 1 changes the authorized arm

The round-1 count-ceiling defect is recognized, but it is addressed by changing
the intervention. Amendment 1 scales the ordinary-body count ceiling as well
as the cost admission ceiling and D3 trigger. That removes the specific retained
count-ceiling concern for the broader proposed arms. It does **not** resolve
the review within the owner's current explicit instruction: each arm changes
the **cost cap only**, in admission and the D3 over-budget trigger.

The amendment also contradicts the original Arms section, which still calls
the intervention cost-only. Calling all three thresholds one resource ceiling
does not make count admission the same policy as cost admission. A candidate
can be refused by the count check before its prospective cost is evaluated.

Every standalone `64` in the reproduced RD3 `medium/rev7_design.py`:

| Line | Executable use | Current cost-only instruction | Amendment 1 |
|---|---|---|---|
| 365 | `sum(e[3]!='output' for e in elements)+1>64` | Keep ordinary count ceiling 64 | Raise to 96/128 |
| 370 | `n+.1*pairs>64` | Raise prospective cost ceiling to 96/128 | Raise to 96/128 |
| 499 | `while self.cost()>64` | Raise D3 cost trigger to 96/128 | Raise to 96/128 |

Under cost-only scope, the count ceiling remains a possible constraint. At
default `k=8`, at most `8*N` undirected ordinary held pairs can be charged, so
normally admitted `N<=64` populations have cost at most `1.8*N<=115.2`.
CAP128 cannot normally reach its cost ceiling under that count limit. This is
a structural bound, not a claim that the stored trajectories reach it.

**Disposition: STOP before Step 2.** The drafter must reconcile the spec with
the current cost-only scope and narrow the interpretation to that intervention.
A broader count-and-cost experiment requires an explicit owner scope change.
The implementer must not silently choose either interpretation or edit the
design. No CAP96/CAP128 build, scheduler, report writer or telemetry is created.

## R2 — blocking: extra resource use does not identify absence of a resource bound

Amendment 1 narrows the negative reading to CAP128 median cost after 400 s
above 80, together with service index at most `1.15*T_RD3`. The additional
condition establishes use of some extra cost headroom under the
chosen sampling rule. It does not establish that the raised ceiling stops
constraining births or D3, or that resource constraints cannot limit service.
Weak endpoint response can coexist with cost refusals, count refusals, quotas,
search/geometry, growth history or the finite 800 s horizon.

Conversely, failing the median-above-80 condition does not establish "ceiling
not reached." Occasional saturation or costly refused proposals can coexist
with a low median of realized cost. The amendment therefore still permits
unsupported bottleneck labels, even for its broader intervention.

The drafter should use descriptive readings such as **extra cost headroom
used, no material service-index gain observed** and **extra-cost-use criterion
not met**. Retain realized cost/count, headroom, cost/count refusal events and
D3 events to describe constraints. These observations do not prove the general
absence of a resource bottleneck. The positive threshold describes a response
to the specified intervention on these exploratory keys; it does not establish
a proportional scaling law or isolate admission from D3.

Also declare the median's population before execution: pooled samples versus
median of run medians; settled 0.1 s boundaries versus 5 s samples or growth
checks; exact interval (for example `400 < t <= 800`); both starts and ten on
runs; exclusion of off controls. Different choices need not give the same
reading. This is a design clarification for the drafter, not an implementer
choice to make after results exist.

## Metric and constant inventory notes

**N1 — the clarified service index is sound with explicit pooling.** For each
of eight physical sites, pool active-served steps over active steps across
exactly ten on runs (five keys, both starts), then sum the eight fractions:
`T = sum_s(sum_r(active_served_steps[r,s])/sum_r(active_steps[r,s]))`.
It is dimensionless, between 0 and 8. Exclude off controls. Missing runs,
zero denominators, duplicate slots or failed integrity must withhold readings.
The revised coverage observer samples settled post-growth boundaries; active
service additionally requires positive drive strength. This index weights
sites equally despite different active exposures; it is not simultaneous
service, pooled served site-time, delivered signal or the gate metric.

Read-only arithmetic on the ten committed RD3 on summaries confirms
`T_RD3 = 2.147575404987718`, with four pooled site fractions at least 0.30.
Use the exact ratio thresholds `3.2213631074815767` and
`2.4697117157358752`; 3.22 and 2.47 are display approximations.
Define "between" inclusively as `T_RD3 <= T_CAP96 <= T_CAP128`.
Require both complete arms and both passing integrity pairs before readings.
Report start-specific and per-key paired values as descriptive context.

**N2 — reporting constants are separate from policy.** The revised coverage
observer has exactly two reporting `cap=64` fields, in `event` at line 129
and `growth_end` at line 156. A future new capacity observer must report cost
cap and count ceiling separately; under the current instruction the latter
is still 64. Preserve the revised transition/restoration semantics. Its RD3
D3 classification recognizes variants by name, so new capacity names must
receive the RD3 classification rather than fall through to empty protection.
Existing coverage/economy observers and committed summaries stay unchanged.

Other inspected uses of 64, which must not be replaced:

- `service_telemetry.py:117,138` and `economy_telemetry.py:186,213`:
  historical reporting caps; these observers are not the new capacity observer.
- `runner/rev7_control.py:46,47`: a cost-64 comment/assertion in control-U
  `Queue.check`. The exploratory harness constructs default intact `Run`,
  whose growth uses B1 with no control queue; this assertion is not reached by
  the planned arms. A future control-U extension needs a separate review.
- Historical `medium/design_0h.py:217,221,232` and
  `medium/rev6_design.py:210,216,297`: earlier count/cost/D3 laws, not active
  RD3 policy. Imported site geometry does not execute their growth policies.
- `medium/medium.py:147`, `world/world.py:108`, and
  `world/test_world.py:166`: unsigned 64-bit seed limits/tests.
- `world/verify_world.py:168,275,276`: historical 64-episode batch/comment.
  Timing/test fixtures and stored-analysis headroom/static-pair counts are
  historical references, not capacity parameters.
- `execute_debt_plan.py:128`, `execute_coverage_plan.py:109` and
  `execute_economy_plan.py:116`: SHA256 hexadecimal digest length 64.
  Patch-context 64s in older kernel helpers remain exact historical contexts.
- The scratch harness's `t > 640` late window is unchanged. It is distinct
  from the amendment's new after-400 s cost statistic.

No active RD3 reserve calculation using 64 was found. Replacement must target
the two authorized policy comparisons, never the whole subtree.

**N3 — time-series ratios need independent denominators.** Retain both
structurally served and active-served simultaneous counts at the settled
boundary. Define which count divides cost; report both ratios if desired.
Zero service requires null plus a zero-service flag, while retaining total
cost. Class mass is ordinary bodies plus 0.1 per undirected ordinary held
pair, allocated 0.05 to each endpoint, with O and its incident pairs free;
this is conserved current cost, not marginal deletion savings. Retain gate
A/B/E and shape separately from coverage.

**N4 — inherit DEBT safeguards, not stale readings.** DEBT usage/report still
say fairness aggregation is unresolved, although its spec Amendment 1 defines
the minimum of eight pooled site fractions. Preserve DEBT files/results and
do not copy that stale interpretation. The inspected local compute cap is
9000 s; the scheduler default is 5400 s. A future capacity cap config must be
independent, read once per launch, recorded in its ticket and excluded from
completion identity. This is elapsed compute time, not the scientific cost
ceiling. Anchored executable process matching, identity-verified completions,
started-slot refusal, at most ten workers and main-phase integrity pairs are
required. The actual CAP implementation and synthetic validation are deferred
by R1/R2, so this review does not certify any prospective CAP tooling.

## Recheck, disposition and preservation

The owner request above was sent verbatim to independent reviewer agent
`capacity_r2_recheck`. This is a Codex same-family fallback, not Claude
cross-family acceptance. It independently confirmed the scope conflict and
negative-reading defect, and recommended CHANGES_REQUIRED/STOP. Findings and
disposition are tracked here under the owner's explicit prohibition on editing
or staging `docs/PLAN_CURRENT.md`; no plan update is implied.
The reviewer also checked the completed draft, verified the control-U exclusion
and the 115.2 cost bound, and found no additional blocker. Its precision note
to avoid implying continuous resource use from a pooled median is incorporated.

Reviewed identities, observations only (not an execution hash manifest):

- Capacity spec SHA256: `708233800aa71528b4417d9094ccb93706ef314dc03eb6841800b065e2413716`.
- RD3 scratch Python SHA256: `4136cac62614cb5d2d0f7d4115c2f39d85ee0e83ea0e6ee2113ef59f153b07c1`, matching `RD3_BUILD.json`.
- RD3 control summary SHA256: `808f1b0485e647980022a2ed52e644ec5e4990ac646da58fba9044829828616f`.

Only read-only source inspection and standard-library arithmetic on stored
JSON occurred. No project tests, native loading/steps, process listing, panel,
assay or pilot occurred. The requested delivery is this new review only;
no existing source, design, plan, status or committed evidence is edited.
If primary Git metadata is read-only, a normal-hook scoped commit in a
project-local clone and a verified incremental bundle carry this review from
the reviewed HEAD, with `Assisted-by: Codex:GPT-6`.

| Stop condition | Yes/no | Action | Responsible role |
|---|---|---|---|
| Does Amendment 1 change the arm beyond the owner's cost-only instruction? | Yes | Reconcile the proposal with the authorized scope before Step 2 | Drafter |
| Does the negative reading infer absence of a resource bound from insufficient evidence? | Yes | Narrow and define the readings before Step 2 | Drafter |
