# Service-debt scheduling pilot: one change on RD3 (plan step A6z6)

**Date:** 2026-10-07 (night). **Drafter:** Claude (claude-opus-5-5). **Implementer:** Codex. **Executor:** Claude.
**Basis:**
- `FRONT_ALLOCATION_DIAGNOSTIC.md` (`0fc1608`), which recommends service-debt scheduling first;
- the owner's research update (§3, rank 2);
- `COVERAGE_PILOT_REPORT.md`: COV-A, longest-waiting, gave 10/10 gate shape but coverage only ×1.4, **rotated**: site 7 fell from 0.39 to 0.03, because brief service reset its waiting clock.

**Status:** exploratory, key sets 0–4 only. No verdict; the §19.7 fresh keys are never touched. No manifest pins `docs/PLAN_CURRENT.md` or the design files.

## The arm (RD3 plus exactly one change; RD3's committed runs are the control)

- **DEBT: the B-path site order uses cumulative service debt.**
  - **Per physical site s,** a kernel-owned, clone-copied debt D_s, starting at 0 at t = 0 in both starts.
  - **Update at every 0.1 s integrate boundary,** before growth: if s is **active and not served** at that boundary (RD3's structural service definition, all-site roots), D_s += 0.1. Otherwise D_s is unchanged.
  - **Never reset:** service does **not** reset D_s (this is the difference from COV-A).
- **At each B-path check:** the existing classes are kept (finite-deficit sites first, then rootless sites). Within each class, sites are ordered by **D_s descending**, with the existing pointer-relative id tie-break.
- **Unchanged:** the live path checks, the pointer advance, two accepted B-path births per check, the repeat after an acceptance, resource-stop propagation, output-first, B1 with its quota and timers, D3 (RD3's), and the budget.
- This is exactly the diagnostic's "integrate-boundary debt" key. The lagged-observer variant is not used; per the diagnostic it gives the same first choice at every check.

## Runs

- **The plan:** DEBT × key sets 0–4 × starts (i) and (ii) = 10 runs, plus one observer-off integrity control. The same scheduler conventions as the economy pilot (resume; process gate; at most 10 workers).
- **The cap:** the run happens at night (decision 0031). **The cap must be set in a non-hashed configuration read at launch, not in hashed code,** so that a resume never breaks completion identity (the lesson from `6bf50d0`). Default 5400 s.

## Report (`DEBT_PILOT_REPORT.md`; first line DONE, PARTIAL or NOT_RUN)

- **Coverage:** per-site active served fractions (all eight); pooled coverage of sites 3–6; **the minimum per-site active served fraction**; and the per-run count of sites served ≥ 50% of their active time.
- **The gate shape:** empty and seeded.
- **Debt:** the debt trajectories; how often the debt order differs from the RD3 and COV-A orders; quota and cost refusals per site; the mass by class.

**Reading rules (declared now; descriptive; RD3 is the control, COV-A the context):**
- **"Coverage improves":** pooled sites 3–6 ≥ 2 × 0.08601377266387726 = 0.17202754532775452, **and** ≥ 4/5 empty passes, **and** all runs complete with integrity.
- **"Fairer than COV-A":** the minimum per-site active served fraction is above COV-A's, **and** no site falls below 0.10, **and** ≥ 4/5 empty passes.
- **"Regression":** ≤ 3/5 empty passes.
- Anything else is descriptive.
- **The falsifier** (from the diagnostic): if quota allocation follows debt but the minimum per-site service stays poor, scheduling is not the bottleneck.

## Amendment 1 (before any DEBT fight): the minimum aggregation for "fairer than COV-A"

- **The minimum per-site active served fraction** = min over the 8 sites of (Σ over the arm's 10 runs of the site's active-served steps) / (Σ over the 10 runs of its active steps). That is, the per-site pooled fraction, as in the coverage reports' Arm/site tables, then the minimum over sites.
- **COV-A's value** is computed the same way from its committed report: min over sites of its pooled per-site fractions.
- **"No site falls below 0.10"** uses the same pooled per-site fractions.
- **Also reported, descriptive only:** the per-run minima.
