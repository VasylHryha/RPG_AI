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
