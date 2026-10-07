# Capacity diagnostic: does total service scale with the budget? (plan step A6z7; a diagnostic, not a candidate law)

**Date:** 2026-10-08, night. **Drafter:** Claude (claude-opus-5-5). **Implementer:** Codex. **Executor:** Claude.
**Status:** exploratory key sets 0–4 only; no verdict; no fresh §19.7 keys; no manifest pins `docs/PLAN_CURRENT.md` or the design files.

## Why

**The total service is about constant under every scheduler.** The sum over the 8 sites of the pooled active served fractions:

| Arm | Total |
|---|---|
| RD3 | 2.15 |
| COV-A (ordering) | 1.75 |
| DEBT (ordering) | 1.82 |
| COV-B (recycling, frees budget) | 2.50 |
| ECO-R (thinning, removes material) | 1.16 |

- **The ordering rules redistribute service:** about 4 sites are served ≥ 30% in each of them.
- **Only freeing material (COV-B) raised the total,** and removing material (ECO-R) lowered it.
- **Hypothesis:** for this dynamic medium the usable budget does bind. Live routes need redundant parallel paths to carry the response (ECO-R), so they cost far more than the static 22.4-unit star.
- The owner's research update advised against raising the budget **as a fix**. This is a **diagnostic** that locates the bottleneck. A positive result would make route **efficiency** (shared trunks, cheaper redundancy) the target, not a bigger budget.

## Arms (each is RD3 plus exactly one change: the cost cap)

| Arm | Cost cap |
|---|---|
| **CAP96** | 96 |
| **CAP128** | 128 |

- The cap is RD3's admission cap and the D3 over-budget trigger. **Everything else is RD3**, including the 64-based reserve wording where it exists: the same constants except the cap.
- **The control:** RD3's committed runs (cap 64).

## Runs and report

- **The plan:** 2 arms × key sets 0–4 × starts (i) and (ii) = **20 runs**, plus one observer-off integrity control per arm.
- **The scheduler:** the DEBT scheduler's conventions, including the non-hashed cap config.
- **The report (`CAPACITY_DIAGNOSTIC_REPORT.md`):**
  - per-site pooled served fractions; their **sum (total service)**; the number of sites served ≥ 30%; the time series of simultaneously served sites;
  - the gate shape;
  - the mass by class, and the cost per served site over time.
- **Readings (declared now):**
  - **"Capacity scales with budget":** total service at cap 128 ≥ 1.5 × RD3's (≥ 3.22), and at cap 96 between the two.
  - **"Not budget-bound":** total service at cap 128 ≤ 1.15 × RD3's (≤ 2.47).
  - Anything else is descriptive.

## Amendment 1, answering the Codex spec review (`docs/reviews/tactical_0h_capacity_diagnostic_spec_review_codex.md`, CHANGES_REQUIRED)

**Self-audit:** I treated "the budget" as only the cost ceiling. RD3 has three 64 literals:
- **line 365:** the ordinary-body **count** admission ceiling;
- **line 370:** the prospective **cost** admission ceiling;
- **line 499:** the D3 over-budget trigger.

**The intervention, redefined as one change: "the resource ceiling" × 1.5 or × 2.**

| Arm | Count ceiling (365) | Cost ceiling (370) | D3 trigger (499) |
|---|---|---|---|
| CAP96 | 96 | 96 | 96 |
| CAP128 | 128 | 128 | 128 |

- **All three are scaled together;** no other constant changes.
- **The telemetry's hardcoded `cap = 64` fields** (observer lines 129 and 156) are reporting constants. They are **parameterized to the arm's ceiling for reporting only**, which changes no policy. The 640 s late-window selector and the other non-RD3 64s stay unchanged.

**The readings, narrowed (N1 adopted: "total service" is a site-normalized coverage index, Σ over the 8 sites of the pooled active served fractions, at most 8):**
- **"Capacity scales with the resource ceiling":** the index at CAP128 ≥ 1.5 × RD3's (≥ 3.22), and CAP96 lies between RD3 and CAP128.
- **"Not resource-bound"** applies **only if** the arm actually used the extra resources (its median cost after 400 s > 80 for CAP128) **and** its index ≤ 1.15 × RD3's (≤ 2.47). If the resources were not used, the reading is "ceiling not reached; the bound is elsewhere" (descriptive).
- Anything else is descriptive.
- **Mass and cost** are reported by class, so a gain can be traced to served routes, fronts or redundancy.
