# Economy pilot: two single-change arms on RD3 (plan step A6z3)

**Date:** 2026-10-07. **Drafter:** Claude (claude-opus-5-5). **Implementer:** Codex. **Executor:** Claude.
**Basis:**
- `MASS_BUDGET_DIAGNOSTIC.md` (`395e4e5`): near capacity, **front** bodies (reachable from a site's roots, but on no route to O) hold 60–68% of the cost in RD3 and COV-A, and **redundant** bodies 30–46%. Critical route bodies hold 2–4%, orphans under 1%.
- An ideal eight-spoke star costs 22.4 of 64.
- **The coverage pilot** (`COVERAGE_PILOT_REPORT.md`): ordering (COV-A) and recycling on refusal (COV-B) raised the coverage of sites 3–6 only ×1.4–1.6.

**Status:** exploratory, key sets 0–4 only. No verdict. The fresh §19.7 keys are never touched. **No hash manifest pins `docs/PLAN_CURRENT.md`.**

## Hypothesis

The medium does not run out of budget: it **parks** budget in stalled fronts (half-built bridges and blobs around unserved sites) and in redundant thickness. Freeing that budget, one body at a time and task-blind, lets growth reach more sites.

## Arms (each is RD3 plus exactly one change; RD3's committed runs are the control and are not rerun)

**ECO-F, retracting stalled fronts:**
- **Per physical site s,** a stall clock f_s, kernel-owned and clone-copied, updated at every 0.1 s world boundary:
  - **reset to 0** if s is served, or if s's B-path directed deficit (the existing deficit computation, at the last growth check) decreased at the last check;
  - **otherwise += 0.1** while s has effective roots;
  - **unchanged** while s has no roots.
- **At each growth check, before B-path,** for each site with f_s ≥ **60 s** (three growth checks), in ascending site id, remove **one** front body of s: the lowest-ranked under RD3's rank (lock, then id), among s's front bodies with age ≥ 200 steps.
  - **Excluded:** any effective root of any site, and **the body of s's front nearest to O** (the bridge tip).
  - Then reset f_s to 0.
- **The class is recomputed before each removal.** At most one removal per site per check, logged as `D5f` with the site and class.
- **"Front of s"** = the bodies reachable forward from R_s in the strong graph, on no route to O for any site. This uses RD3's per-site, all-sites definition.

**ECO-R, sequential redundancy thinning:**
- At each growth check, **after** D1/D4/D3 and before births: if the current cost is > **56** (= 64 − 8, a declared reserve equal to two births at pair-heavy cost), remove **one** service-redundant body.
- **The body:** the lowest-ranked under RD3's rank, age ≥ 200 steps, **chosen only if a prospective check passes.** The all-site strong graph recomputed without the body (nearest-neighbour lists and held degrees recomputed) must keep **every currently served site served.**
- **If the lowest-ranked candidate fails the check,** try the next, up to all candidates. If none passes, remove nothing.
- **At most one removal per check,** logged as `D5r`.

**Both arms are task-blind:** only the medium's own graph, the fixed physical sites and ages are used.

## Runs

- **The plan:** ECO-F and ECO-R × key sets 0–4 × starts (i) and (ii) = **20 runs**, plus one observer-off integrity control per arm.
- **The scheduler:** the coverage scheduler's conventions (resume; the process gate; at most 10 workers).
- **The cap:** at least 3600 s. An owner-approved value is set in code before launch if the projection exceeds 1 h.

## Report (`ECONOMY_PILOT_REPORT.md`; first line DONE, PARTIAL or NOT_RUN)

**Per arm against RD3 (and COV-A/COV-B for context):**
- **Coverage:** the pooled coverage of sites 3–6, with the same formula as Amendment 1, and all eight per-site fractions.
- **The gate shape:** empty and seeded separately.
- **Mass and cost:** the mass and cost by class (critical, redundant, front, orphan) over time; the cost at the first cost refusal.
- **Removals:** D5f/D5r counts, and how often the prospective check fails (ECO-R).
- **Outages:** with the revised B labels.

**Reading rules (declared now; descriptive):**
- **"Coverage improves":** pooled sites 3–6 ≥ 2 × RD3 (0.172 or more), and ≥ 4/5 empty-start passes, and all 10 runs complete.
- **"Regression":** ≤ 3/5 empty-start passes.
- Anything else is descriptive.
