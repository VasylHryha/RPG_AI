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

## Amendment 1, answering the Codex spec review (`docs/reviews/tactical_0h_economy_pilot_spec_review_codex.md`, CHANGES_REQUIRED)

This amendment overrides the sections above where they differ.

**Self-audit (cause):** I named "the B-path deficit decreased at the last check" without fixing which snapshots are compared, at which stage, or how a reset persists. RD3 computes the deficit only for active unserved sites, before births, so no existing quantity matched my sentence.

**ECO-F, the stall clock (replaces the clock text above):**
- **The measurement:** at the **end** of every growth check, after all of that check's removals and births, the kernel computes for **every physical site s, active or not**, the directed forward-to-backward deficit d_s(k). This is the same computation B-path uses, applied to s's effective roots (RD3's all-site root definition) on the end-of-check strong graph. d_s(k) = ∞ when s has no effective roots or there is no O.
- **The clock f_s (seconds),** kernel-owned and clone-copied, **updated only at the end of each growth check:**
  1. **if s is served** at the end of check k: f_s = 0;
  2. **else, if this is s's first finite deficit,** or d_s(k−1) = ∞ (roots newly gained), or d_s(k) < d_s(k−1) − 1e-9: f_s = 0 (progress);
  3. **else, if d_s(k) is finite** (stalled): f_s += 20 s (one growth interval);
  4. **else** (no roots): f_s unchanged.
  - Then the kernel stores d_s(k) as the history for check k+1.
  - There is no per-boundary update and no persistence ambiguity. Progress made before a root loss does not carry over: regaining roots counts as progress by rule 2.
- **The removal point:** in each growth check, **after** the measured locks and D1/D4, and **before** D3, B-out, B-path and B1. This way the freed cost is available before D3 and before births.
  - For each site with f_s ≥ 60 s, in ascending site id, remove at most one front body of s, then set f_s = 0.
  - **If s has no eligible donor,** also set f_s = 0 and log `D5f_none`.
  - **With no O,** ECO-F removes nothing, and the clocks follow rules 1–4 with d = ∞.
- **The tip:** over s's **entire** current front, before the donor exclusions, the body with the smallest Euclidean distance to O. Ties go to the lowest id.
- **The donor:** the lowest-ranked body of s's front (by the check's measured lock, then id), with age ≥ 200 steps.
  - **Excluded:** every site's effective roots, and s's tip.
  - **A body in several sites' fronts** is removed at most once, in ascending site order.
  - **The classes are recomputed after each actual removal.**
- **Recorded trade-off:** keeping the roots and the tip does not guarantee that existing routes survive the neighbour and degree rewiring. ECO-F has **no** prospective veto; that would be ECO-R's mechanism.

**ECO-R:** unchanged. The review's implementation notes are adopted:
- the original served set must remain served, idle sites included, in a pure-geometry rebuild that touches no live state;
- trials, failures, no-candidate checks and prospective-check time are recorded;
- removal stops at the first passing donor, and there is at most one removal.
- **The 56 trigger is a declared heuristic, not a guaranteed headroom.** There is no repeated thinning to force it.

**Reading rules:**
- **The doubling target is exact:** pooled coverage of sites 3–6 ≥ 2 × 0.08601377266387726 = 0.17202754532775452.
- Amendment 1 of the coverage spec's incompleteness rule applies to both readings, and both readings need each arm's observer on/off identity and clone isolation.
- All eight sites and both starts are always reported.

**Cap:** the implementation's cap is 3600 s. If the projection exceeds it, the scheduler stops, and Claude resolves it with the owner (decision 0031). The cap is never raised implicitly.

**Hash manifests** exclude `docs/PLAN_CURRENT.md`, `DESIGN_0G.md` and `DESIGN_0H_REV7.md`.
