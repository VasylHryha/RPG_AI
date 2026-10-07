# Coverage pilot: two single-change arms on RD3 (plan step A6z)

**Date:** 2026-10-07. **Drafter:** Claude (claude-opus-5-5). **Implementer:** Codex. **Executor:** Claude (the Codex sandbox cannot list processes).
**Basis:**
- `COVERAGE_DIAGNOSTIC.md` (`f8076ab`; I read it as cross-family reviewer and found it consistent with `SERVICE_TELEMETRY_REPORT.md`);
- the telemetry recheck `docs/reviews/tactical_0h_service_telemetry_recheck_codex.md`;
- the owner's second-view V3 (one change per arm; exploratory keys only).

**Status:** exploratory pilots on key sets 0–4. No verdict. The fresh §19.7 keys are never touched.

## Why

- Under RD3, sites 4–6 are served 2–7% of their active time, and site 3 19%. **Every site acquires roots in every run.**
- **Two constraints act in sequence.** Each arm below targets one of them:
  1. **Scheduling, before any cost limit.** B-path serves the smallest directed deficit first, with two accepted births per check. Far sites collect 75–96 quota refusals each before the first cost refusal.
  2. **Weighted cost from about 320–420 s.** cost = N + 0.1 × held pairs. Far-site requests are then refused on cost (112–143 each), although only 44–46 of the 64 elements exist.

## Arms (each is RD3 plus exactly one change; constants exactly as in RD3)

- **RD3 (control):** reused from the committed telemetry runs (identical code, keys and observer). It is not rerun.
- **COV-A, fair ordering:** at each B-path check, active sites with a missing route are ordered by **the longest time since the site was last served while active**. A site never served counts from its first active root. Ties are broken by the existing pointer.
  - Everything else is unchanged: two births per check, the deficit computation and placement, and output-first.
- **COV-B, recycling on cost refusal:** when a B-path or B1 birth **for a currently unserved physical site** is refused on **cost**:
  1. remove **one** eligible **non-service** element, using RD3's class and rank: not O, older than 200 steps, the lowest lock, then the id;
  2. retry that same admission **once**.
  - **If no non-service element is eligible, or the retry is refused,** the request ends as cost, as before.
  - **At most one recycle per growth check.**
  - The removal is logged as rule `D3r`, with its class.
  - Service is computed per physical site (RD3's definition), on the graph immediately before the removal.

**Both arms are task-blind:** they use only the medium's own graph, the fixed physical sites and the birth history.

## Observer revision (answers the telemetry recheck's B-label finding)

- **The fix:** sample the post-birth gap for the outages that were open **before** the transition, and exclude restoring endpoints from the non-repair evidence.
- **The changed definition must be documented.** Apply it to all three arms' reporting. Recompute RD3's labels from its stored traces where possible, and otherwise mark them `legacy_B`.
- **Integrity:**
  - observer on/off byte identity, on one COV-A run and one COV-B run;
  - clone isolation;
  - the RD3 control's committed summaries unchanged.

## Runs

- **The plan:** COV-A and COV-B × key sets 0–4 × starts (i) and (ii) = **20 runs**, plus 2 observer-off integrity controls.
- **Budget:** at most 10 parallel, using the existing scheduler conventions (resume, pgrep gate, caps).
- **Compute:** the last batch ran 30 runs in 66 min at low load. **Projection: about 45 min.** Under 1 h, so decision 0031 needs no approval. Stop and report if the projection exceeds 1 h.

## Report (`COVERAGE_PILOT_REPORT.md`; first line DONE, PARTIAL or NOT_RUN)

**Per arm against RD3:**
- **Coverage:** the served fraction of active time for each of the 8 sites, pooled and per run; the number of sites served for at least 50% of their active time, per run.
- **The gate shape:** empty and seeded separately, with the F5 assay A, B and E.
- **Births:** births per site; request outcomes per site (quota, cost, accepted, no_root, deferred); the first cost-refusal time.
- **COV-B only:** recycle counts; recycled elements' classes; and whether a recycled element later became service (churn).
- **Outages, break and non-repair causes** (revised labels); D3 classes; forced cuts.

**Descriptive reading rules, declared now:**
- **"Coverage improves":** the pooled served fraction of sites 3–6 at least doubles against RD3, **and** the empty-start gate shape stays ≥ 4/5.
- **"Regression":** the empty-start gate shape falls below RD3's 5/5 by 2 or more.
- Anything else is reported descriptively.
- **A positive arm becomes the A7 candidate.** If both are positive, the owner chooses whether to combine them later, as a separate revision.
- Nothing here is a verdict or uses fresh keys.
