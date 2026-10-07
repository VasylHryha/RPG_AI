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

## Amendment 1, answering the Codex spec review (`docs/reviews/tactical_0h_coverage_pilot_spec_review_codex.md`, CHANGES_REQUIRED)

This amendment overrides the sections above where they differ.

**Self-audit (the drafter's causes):**
- **COV-A:** I named a clock ("time since last served while active") without its update rule or its pre-root case.
- **COV-B:** I wrote "retry the same admission" without checking that B-path's geometric trial depends on anchor elements that the donor rule could remove.
- **The churn measure:** I asked for something impossible: removed ids never return.

**COV-A, the waiting clock (kernel-owned, clone-copied, independent of the observer):**
- **One clock w_s per physical site,** starting at 0 at t = 0 in both starts (seeded roots included).
- **Update at every 0.1 s world boundary:**
  - if site s is **served** (RD3's structural definition: a strong route from its effective roots to O), w_s = 0, whether or not s is active;
  - otherwise, if s is **active**, w_s += 0.1;
  - otherwise (inactive and unserved), w_s is unchanged.
- **No updates at intra-check births or removals.** Root loss does not reset the clock.
- **The B-path ordering:**
  - The existing classes stay as they are: sites with a finite directed deficit come first, then rootless sites (infinite deficit).
  - **Within each class, sort by w_s descending** instead of by deficit. The existing pointer breaks ties.
  - **Unchanged:** the live path checks, the pointer advance, two accepted B-path births per check, the repeat after an acceptance, resource-stop propagation, output-first, and B1 with its quota and timers.

**COV-B, recycling:**
- **The donor:** the lowest-ranked eligible **non-service** element under RD3's rank (lowest lock, then id), at the growth check's measured locks, with `step_index − birth_step ≥ 200`.
  - **Excluded:** the attempt's own anchors, meaning B-path's endpoint elements a and b. B1 attempts have no excluded anchors.
  - **Service** is evaluated per physical site on the graph immediately before the removal.
- **The retry:**
  1. after the removal, **re-run the complete admission for the same candidate point on the new graph**, both the geometric trial and the feasibility check;
  2. **if it passes,** the birth is accepted (one terminal, counted as one birth);
  3. **if it fails,** the request ends with the outcome `recycle_failed`, and **the removal stays in place** (logged).
  - There is no new candidate search.
- **Limits:**
  - at most **one recycle per growth check**, shared by B-path and B1;
  - only for requests naming a currently unserved site;
  - only after a terminal **cost** refusal of a candidate admission. A propagated resource-stop has no candidate, so nothing is retried.

**COV-B's replacement for the churn measure:**
- the donor's class, lock and age;
- the retry outcome;
- for accepted retries, whether the requesting site becomes served within 60 s.

**The observer B-label fix (adopting the review's wording):**
- **Recording:** keep the outage objects open before the transition, and record their post-birth gaps before closing them.
- **Exclusion:** exclude the repairing terminal and its endpoint gap sample from the B decision. Keep the sample as restoration evidence, with zero weight in duration statistics.
- **New outages** do not inherit earlier births.
- **Label meanings, unchanged:** B is a global observation of an accepted birth, C a global resource refusal, N a request naming the site. None of them is a causal identification.
- **The RD3 control:** revised labels go only into new outputs, where the retained traces establish the boundary facts. Otherwise they are `legacy_B`, never mixed with revised totals. Coverage and assay values are reused unchanged.

**The reading rules, made exact:**
- **The pooled coverage of sites 3–6:** sum(active_served_steps) / sum(active_steps), over sites 3–6 and the 10 runs of an arm. All eight per-site fractions are always reported.
- **"Coverage improves":**
  - pooled coverage of sites 3–6 ≥ 2 × RD3's value;
  - **and** at least 4/5 empty-start gate-shape passes;
  - **and** all 10 runs complete.
- **"Regression":** at most 3/5 empty-start passes.
- **Missing runs** make the arm INCOMPLETE. They are never counted as a failure or as a positive reading.
- **A7 candidacy is prospective:** it does not authorize A7 or combining the arms.

**Scheduler:**
- **The cap:** 3600 s, using the remaining jobs (including both off controls) and the measured elapsed and CPU limits.
- **Workers:** at most 10.
- **Resume:** reuse of identity-verified completions; started but incomplete slots are never rerun; a process-access error stops the scheduler.
- **The combat pattern must name this repository's own paths in both alternatives,** synthetically tested, and must never match a concurrent pgrep:
  - Python processes running `tactical_composition_demo/astelia_cpp/s4_*_v1/` scripts;
  - native hosts under `ai_RPG_test/…/astelia_native*`.
