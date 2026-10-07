# Stage-1 service telemetry and the site-based ranked D3 candidate (spec for plan steps A6w and A6x)

**Date:** 2026-10-07. **Drafter:** Claude (claude-opus-5-5). **Implementer:** Codex.
**Basis:** the owner's second-view plan V3 (§3–5) with Claude's amendments (`docs/reviews/rrg_next_steps_assessment_claude.md` §4). Earlier evidence: `signal_loss/` (D3 cut the live chain in both traced screening failures) and the V1 pilot (8/10, empty start 5/5).
**Status:** exploratory pilot instrumentation on the existing exploratory key sets 0–4 only. No verdict. The fresh §19.7 keys are never touched.

## 0. Reproducible scratch kernels (no dependence on /private/tmp)

The earlier pilots ran from scratch copies of the repository in a session scratchpad.
- **Replace them with a builder** in `medium_variants/kernel_builder/`:
  1. check out `git worktree add <dir> fd21826` (the reviewed 7.11 identity used by the earlier pilots);
  2. copy in the untracked native build inputs exactly as the earlier pilots did (`rev711_diag/pilot_common.py` documents the stub);
  3. apply the variant patches;
  4. build with `build_rev7.py`;
  5. record the source and binary SHA256.
- **The builder must reproduce:**
  - the screening binary `b0b35a16…c9578d`;
  - the V1 Python diff (`bond_v2_screening_V1_path_protected_D3.pydiff`).
- **Variants:**
  - **SCR:** `bond_v2_screening.patch`;
  - **V1:** SCR + the V1 diff;
  - **RD3:** SCR + the ranked D3 of §3.

## 1. Definitions (all task-blind: the medium's own graph and the fixed physical sensor sites)

- **Sites:** the 8 physical sensor sites, with their fixed positions and reach. Use every site, **active or not**. If idle sites are missing from the live drive list, take their positions and reach from the site definitions used by the world bindings, and state where they came from.
- **Site roots** R_s: ordinary elements (not O, not silent, gain > 0) within site s's reach.
  - This differs from `graph()`'s `roots`, which require the drive to be active (`d.strength > 0`).
  - Report both: **served** (any strong path R_s → O) and **active-served** (served, and s is active).
- **Strong graph:** `strong_influence()` edges (rate ≥ 0.5 /s).
- **Selected partners** of element a: its ≤ 2 nearest strong incoming partners, exactly as in the patch's `bonds(a)`.
- **Realized spring degree** of a: the number of b with b ∈ selected(a) or a ∈ selected(b). Report both counts; the realized degree can exceed 2.
- **Saturated** (as the screening patch uses it): |selected(a)| ≥ 2.
- **Service class** of each eligible element e, computed on the current graph:
  - **critical:** removing e makes at least one currently served site unserved;
  - **redundant:** e lies on some R_s → O strong path, but is not critical;
  - **non-service:** neither.
- **The O fragment:** the spring-connected component containing O. Record:
  - its size;
  - whether it contains any site root (rooted or rootless);
  - whether all its members are saturated (screened).

## 2. Stage-1 telemetry (observer only)

**Per world step:**
- active sites; the served and active-served site sets;
- the hop count of the shortest path per served site;
- the O-fragment record;
- counts of service classes;
- the distributions of selected-partner counts and realized degrees.

**Per growth check:**
- D1/D3/D4 removals, each with the removed element's service class and lock;
- birth requests and terminals with outcome (accepted, cost, quota, placement, no_root, deferred);
- cost and cap.

**Every 50 steps:** full positions, the strong edges and the spring pairs (for figures).

**Outages:** an outage of site s starts at a served → unserved transition and ends at unserved → served. For each outage record:
- start, end and duration; whether it was censored at 800 s;
- whether the restored route reuses the same element set or is a new route.

**Break cause** (from the graph immediately before and after the transition):
- **D3, D1 or D4:** an element on every R_s → O path was removed by that rule in that step;
- **G-dist:** a path edge's rate fell below 0.5 because its length grew;
- **G-deg:** a path edge's rate fell below 0.5 because the receiver's held degree grew (crowding);
- **R:** spring selection changed on the path, with the strong edges intact;
- **X:** none of these, or several.

**Non-repair cause** (for outages lasting over 20 s):
- **S:** the O fragment is rootless and screened (all members saturated) for most of the outage;
- **C:** B-path or B1 requests were refused on cost during the outage;
- **N:** no birth request named that site during the outage;
- **B:** births occurred, but the minimum R_s–O-fragment gap did not shrink;
- **G:** a route re-formed and broke again within the outage;
- **X:** none or several.
- Report every applicable label, and mark one as primary: the earliest in time.

**Per run summary:**
- served fraction of active time, per site;
- outage count, maximum outage and the repair-latency distribution;
- tables of break causes and non-repair causes;
- the F5 pilot assay (A, B, E), as in `pilot_common_scratch.py`;
- the fraction of the population protected by V1 or RD3 at each D3 decision;
- every `forced_service_cut`.

**Integrity checks (before any reported run):**
- **observer on/off:** the full state trajectory (positions, phases, element ids per step, as a hash) is byte-identical over one complete 50-episode run of SCR, empty start, key 0;
- **clone isolation:** as in `pilot_common_scratch.py`;
- **SCR and V1 reproduction:** with the observer on, the summaries equal the committed logs (`logs/scr_*.log`, `logs/v1_*.log`).

## 3. The RD3 candidate: site-based ranked D3 (one change on SCR; it replaces V1, it is not added to it)

While cost > 64, with eligibility otherwise unchanged (not O, older than 200 steps), remove one element at a time. Recompute the graph and the classes after each removal.
1. **Remove the lowest-ranked non-service element.** The rank is the existing D3 rank: lowest lock, then id.
2. **Otherwise, a redundant element,** by the same rank.
3. **Otherwise, a critical element,** by the same rank. Emit `forced_service_cut` with the sites that lose service.

**Service uses all 8 sites, active or not.** This is the amendment to V1: V1 counted only active sites, so the routes of idle sites were pruned first.
- **No task, score or label input:** the site positions and reach are fixed physical structure.

## 4. Runs (exploratory key sets 0–4 × starts (i) and (ii); one run each; no tuning; constants exactly as in SCR)

- **Part A (classification):** SCR and V1 with telemetry. That is 20 runs, the 10 SCR runs reproducing the committed logs.
- **Part B (candidate):** RD3 with telemetry, 10 runs.
- **Compute:** about 11 CPU-min per run at low load, so about 30–45 min with 10 in parallel. Stop and report if the projection exceeds 1 h (decision 0031, daytime).
- **Machine load:** do not overlap another heavy run. The machine is shared with other projects; measure honestly.

## 5. Report (`medium_variants/SERVICE_TELEMETRY_REPORT.md`; first line DONE, PARTIAL or NOT_RUN)

- **Per variant:**
  - gate-shape passes, empty and seeded separately;
  - served fraction per site (coverage: how many of the 8 sites are ever, and mostly, served);
  - outages, repair latency, and break and non-repair cause tables;
  - D3 removals by service class;
  - forced cuts;
  - the protected-population fraction;
  - realized degree above 2.
- **For each failure:** its primary break cause and primary non-repair cause.
- **For RD3 against V1:** whether site-based service changes coverage, and whether it ever deadlocks the budget (protected_over_budget, or forced cuts).
- **Descriptive only.** No new thresholds.
- **Entry-filter reading:** whether a variant meets 5/5 empty-start exploratory runs. That is a filter for later formal work, not a verdict.
