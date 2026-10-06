CHANGES_REQUIRED

# S4 v4 recheck: stored evidence and the v5 decision

Implementer/rechecker family: Codex (GPT-6). Date: 2026-10-06. Initial workspace HEAD: `9e02224e1577bda4dc4b396237d203661e6320fe`. Verdict concerns the **v4 policy as a development candidate**, not the integrity of its preserved negative result. It is not S5 readiness, scientific acceptance, or authorization to implement/run v5.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Read AGENTS.md, DESIGN_0G sections 13–15 including Planned v5, [v3 development](S4_V3_DEVELOPMENT_REPORT.md), [v3 recheck](S4_V3_RECHECK_REPORT.md), [v4 development](S4_V4_DEVELOPMENT_REPORT.md), stored validation/end states, decision summaries, and raw B regular exports. **Zero new combat, tuning, replay exports, builds, or combat tests.** New analysis is a paced single-process read of existing files, with no project imports. [Reproducible extraction](s4_v4_recheck_checks/analyze_stored.py) and [counts/event examples](s4_v4_recheck_checks/STORED_TRACE_ANALYSIS.json) retain source hashes and reconcile eight count fields per arm against the original decision summary. No original receipt is rewritten.

## 1. High: both hold and focus are implicated; their individual score effects are not identified

The population comparison is Stage B versus Stage B, 100 two-orientation clusters per endpoint:

| Regular endpoint | v3 mean S | v4 mean S | Change | v3 → v4 enemy guns alive/fight | v3 → v4 timeouts/200 |
|---|---:|---:|---:|---|---|
| Resonator | −7.570 | −22.175 | −14.605 | 8.070 → 9.065 | 23 → 0 |
| Morale | +8.550 | −15.405 | −23.955 | 8.960 → 9.645 | 191 → 76 |

These are independently tuned controller packages on different seeds, not paired hold-only/focus-only ablations. The much smaller nearest change (−23.645 → −22.675) is useful context, not a seed adjustment or causal control. The strong conclusion is a package regression, with less survival and less gun removal. The exact division of the regression between hold, focus and optimizer selection is **unresolved**.

**Focus removes opposition to unsafe pursuit.** In `src/native/s3_controller.cpp:195–220`, any committed out-ranged pair among **all living enemies** can select the highest damage-weight focus, outside the inherited 8-nearest-plus-threats movement set. A damage weight is not a requirement that the focus currently threatens or is reachable. Every other enemy velocity term is discarded; ally forces remain. Movement focus and the independently selected legal shooting target are different identities. High feasibility therefore means movement toward the chosen pair's preferred distance, not safe movement, a shot, or a kill.

The one stored B regular seed `941100000`, orientation false, shows:

| Trace event/sample | Resonator | Morale |
|---|---:|---:|
| Focus ticks / own unit ticks | 18,264 / 23,868 | 19,845 / 40,042 |
| Focus ticks with c < −0.2 | 5,742 | 102 |
| Focus ticks already inside at least one gun's 320 px reach | 5,115 | 4,333 |
| Focus on a non-gun while inside gun reach | 228 | 382 |
| Own movement crosses into a gun's reach while focus is active | 448 | 418 |
| Movement toward a gun focus while beyond own reach of that gun | 6,844 | 6,482 |

Crossings compare pre/post **own** position against the gun's prepare position; they are exposure entries relative to that snapshot, not unique units, independently sampled attacks or proof of the gun's next shot. For example, resonator step 254, unit 24 focuses ranged enemy 61 while its movement crosses gun 92's radius from 320.979 px; morale step 256, unit 4 focuses melee enemy 51 while crossing gun 95's radius from 320.952 px. HP is unchanged in those particular ticks. This demonstrates pursuit without preserving the other threats' repulsion, not instant attributed damage.

**The hold makes a stale pair capable of controlling the whole unit.** The 5,742 resonator samples with c < −0.2 and an active focus show escape-requesting state coexisting with a committed pair. Pair-specific band arrivals and expiries stagger the modes. The `any committed pair → singleton focus` rule lets one remaining commit override many escape pairs; a hold does not stabilize a single coherent unit decision or its focus identity. Conversely, the initial mode has no hold: morale starts at c=0 in commit, so focus can pull it in before any travel-time hold begins.

**Elapsed travel time does not certify arrival or safety.** The timer uses the *entire commit-to-escape gap* divided by nominal speed, not remaining distance to the current goal or achieved radial speed. It cannot account for moving enemies, low realized speed, ally cancellation, collisions or clipping. In the resonator replay, 223/393 expiry events occur with the own unit inside some gun's reach; 21 expire inside the expiring gun's unanswered annulus (own reach < distance ≤320). At prepareTime 12.0667, unit 8's commit hold to gun 92 expires after 10.2333 s, planned 10.2275 s, at distance 216.429 px versus own reach 62 px. Its mode **stays commit**. These are holds ending in danger, not evidence that every expiry flips the mode or newly creates danger. Mean cosine 0.9185 cannot refute this: the chosen direction can be feasible and tactically bad.

The resonator replay collapses from 50 units at t≈10 to seven at t=20, ending 0 versus 15 enemies (eight guns) at t=34.2333. It never reaches a gun-only enemy phase. Morale has ten units at t=20, then four versus 34 enemies (all ten guns) from about t=40 through timeout. These differ from the v3 C diagnostic gun-only phase; that older example must not be projected onto v4.

**The 1,237 disappearance releases are mostly our losses.** Native cleanup drops holds when either member is absent/dead, not when a pair falls outside the movement cap. The raw states resolve resonator events into **1,166 own-only deaths and 71 enemy-only deaths**; morale's 97 are all own-only. No both/neither cases occur in these exports. One unit death can release many holds. Thus 94.26% of the resonator count is associated with own death, not successful reference elimination or 1,237 distinct kills. It does not establish that those holds caused the deaths.

**Morale zero displacement is stalled safe escape, mostly after holds.** All 13,218 null cosine samples (33.01% of its unit ticks) are on an actual arena wall, with no focus and no gun within 320 px; only 91 have any active pair hold. Example: unit 13 at x=9,y=791 from step 702, c=−0.0485, no focus. The undefined samples must remain in the denominator when discussing movement coverage: cosine 0.8125 describes only the 26,824 moving/defined samples. This supports an infeasible retreat target and prolonged inactivity; it does **not** support “the hold froze morale under fire” for all 13,218 samples. Escape distances exceeding 1,100 px and hysteresis retaining escape while morale relaxes toward zero make releasing the timer alone insufficient.

## 2. High: the published reversal comparison mixes definitions

[DECISION_TRACE_SUMMARY.json](s4_v4_development/DECISION_TRACE_SUMMARY.json) counts pair changes and unit ticks with **any pair change**, normalized by own living unit-minutes. Pair counts are not unit movement-direction reversals. Many simultaneous pair changes collapse into one unit tick; staggered changes spread one latent state transition across several ticks.

| B regular export | Pair changes / unit-minute | Any-pair-change ticks / unit-minute | Same c-threshold proxy used for v3 / unit-minute |
|---|---:|---:|---:|
| Resonator | 3,364 / 13.26 = 253.695 | 473 / 13.26 = 35.671 | 391 / 13.26 = 29.487 |
| Morale | 343 / 22.2456 = 15.419 | 34 / 22.2456 = 1.528 | 25 / 22.2456 = 1.124 |

The historical v3 C proxy is 33.663 resonator and 0.659 morale. **With the same latent threshold definition, the available resonator proxy is lower, not higher.** Even that is v4 B versus v3 C on unmatched seeds/knobs, so it establishes neither a population reduction nor a failure to reduce it. The report's “35.671 versus 33.663” arithmetic cannot establish a like-for-like reversal regression. Actual realized velocity reversals have not been counted by these metrics.

The timer also does not prevent rapid rearming:

| Hold disposition | Resonator / 3,364 starts | Morale / 343 starts |
|---|---:|---:|
| Target-band releases | 1,718 (51.07%) | 26 (7.58%) |
| Expired | 393 (11.68%) | 220 (64.14%) |
| Disappeared | 1,237 (36.77%) | 97 (28.28%) |
| Active at terminal, censored | 16 | 0 |
| Target-band release immediately rearms on same tick | 421 / 1,718 | 13 / 26 |
| Expiry immediately rearms on same tick | 51 / 393 | 60 / 220 |

Rearming follows the current c after release, including a threshold crossed during the hold. Mean completed/planned holds are 6.153/11.349 s resonator, 11.135/17.066 s morale; completed includes deaths and early bands. Expiry is the dominant *morale* ending, not the resonator ending. Short target-band release, pair staggering, different nominal pair timers and continuing oscillation explain why v4 does not guarantee low unit decision churn even while holding 82.81% of resonator pair ticks. No claim about a matched combat benefit follows.

## 3. Medium: C is missing, but the restart history does not erase completed A/B

The “360.0 minutes” message is a rounded **projected combined cost**, not a fight timeout or an exhausted absolute deadline. [RUN_TIMING](s4_v4_development/RUN_TIMING.json) gives 239.4942 wrapper minutes for the final attempt; the final runner reported 239.4598. The two failed wrappers used 0.00945 and 70.10858 minutes, yielding **309.61226 actual combined minutes**, 50.38774 below the cap. The conservative projection stopped before C push-pull generation 14. Its total-work estimate also counts the eight already exported captures as remaining because its evaluated counter contains only scored fights; that small overestimate is immaterial to the scientific gap and is not grounds to resume this record.

[AUDIT](s4_v4_development/AUDIT.json) accounts for 88,470 scored fights plus eight exports, zero controller failures/cache hits/planner work, completed A/B budgets, and all twelve A/B endpoints with 100 clusters and both orientations. C resonator/morale tuning completes 16 generations each; push-pull completes 13/16 (7,942/9,766 evaluations). **All 84 C validation endpoints and four C exports are not_run**, as are fresh P2/P3 spread, margin and sample-size planning. Positive C morale tuning or a retained C incumbent cannot substitute for validation. There is no v4 final-C head/pool result or matched v3-C versus v4-C trace comparison.

Attempt 1 preserves 38 initial fights, no completed candidate/validation, and the normal-zip closure failure. Attempt 2 preserves 54,000 scored fights and four A captures, then an identity stop when the live parent DESIGN_0G was appended during execution. That was a process breach; detection and preservation are appropriate. The final run pins the approved `914dda4` design extract, restarts all allocations at original midpoint starts on fresh 940/941/942-million bases, and charges both failed attempts to the same cap. Earlier 910/911/912 and 920/921/922 bases and artifacts remain separate. Existing audit/identity records disclose these resets; no earlier winning knobs or results are pooled into final A/B. This inspection confirms the stored summaries/source pin and representative replay bytes, not a new full reconstruction of every tuning record.

The remaining evidence gaps are C absence, no hold/focus ablation, and sparse mechanics exports (one selected seed/orientation per A/B arm), not missing A/B orientations. [LOCAL_ARTIFACTS](s4_v4_development/LOCAL_ARTIFACTS.json) binds raw local files; transporting only summaries cannot independently reconstruct them. Do not extend the historical cap, relabel incomplete C, or reuse this development evidence as untouched confirmation.

## 4. Medium: two design/documentation conflicts matter before v5

1. **Push-pull is affected by focus.** Section 15 calls it “unaffected in effect” because c=1 prevents switches. It indeed has no holds, but v4 still replaces its enemy mean with a singleton focus. It is a hold-free arm, not an unchanged v3 control. Its B regular replay uses G≈0.000227, inflicts zero damage, and ends 50 versus 50 at timeout, S=0. This is a legitimate score under the current objective and a warning about what optimization can reward.
2. **Replay display dimensions are wrong.** `s4_v4_replay.py` hardcodes 1200×700 in stored payloads, while the request does not override `sandboxConfig`'s **1400×800** arena (`src/native/world.cpp:13`). Raw morale coordinates x=9,y=791 confirm the actual bounds. Interpret wall geometry from native configuration/raw states, not the viewer size. Existing captures remain unchanged; repair later viewer metadata without rerunning combat, with provenance and preservation of the originals.

## 5. v5 recommendation: retain v3 baseline; replace, do not merely extend, both v4 rules

**Drop the unqualified per-pair full-gap timer and the “any commit → discard every other threat” focus as defaults. Keep binary hysteresis, range-aware bands, and output-only traces.** Preserve v3 as a selectable baseline. The Planned v5 emergency releases are necessary safeguards but do not fix stale commit dominance, repeated rearming, changing focus identity, initial unheld pursuit or unsafe pursuit with a high cosine.

The drafter should specify one coherent **unit movement intent/reference**, distinct from pair bookkeeping, with the same rules and parameter allowance for resonator/morale. Proposed concrete rules below are engineering choices to freeze before future fights, **not thresholds calibrated or proven optimal from these two exports**:

| Component | Proposed testable rule | Required constructed check |
|---|---|---|
| Hold | On an actual unit intent/reference change, use remaining radial error/v, capped at 2 s; speed≤1 has no timer. Continue evolving underlying state. | A near-arrival intent has a shorter timer than a distant one; clone isolation. |
| Progress | Over each 0.5 s window require reduction of radial error by ≥0.02 own centre reach. A wall-blocked or failing intent releases into replanning, not automatic reversal. | Stationary/clipped motion cannot renew a hold indefinitely; moving reference handled explicitly. |
| Arrival/expiry | Arrival band stays 0.1 own reach. At arrival/expiry unlock the timer but retain the intent; a normal switch requires a **fresh threshold crossing after unlock**, not the stale current c. | A c crossing during a hold cannot immediately rearm on release. |
| Emergency | Death/loss clears reference immediately. Observed incoming pressure whose estimated loss exceeds 0.25 current HP bypasses hold and triggers feasible escape/replan (definition below, with a minimum 0.5 s risk horizon even after arrival). An infeasible retreat also bypasses immediately. | No high-damage lock; severe second-threat damage interrupts even with a legal focus; no reflex release back into the same failed choice. |
| Focus | Choose deterministically from the inherited movement set; do not activate focus merely because some unrelated pair remains committed. Keep a selected reference while feasible and intent-compatible. | A stale commit cannot override unit escape; equal weights have stable ties. |
| Other threats | Keep non-focus unanswered threats in the exposure measure below. Prefer non-increasing exposure when a progress-making alternative exists; otherwise permit transit only under the aggregate loss budget below. | Symmetric targets still give progress; overlapping gun arcs neither disappear from safety nor make every attack impossible by definition. |
| Infeasible escape | Search feasible arena directions, not an impossible off-arena target. If all directions conflict, use a declared deterministic minimum-exposure fallback and log failure rather than claim successful retreat. | Corner/opposing threats, zero displacement and no legal target explicitly covered. |

For a concrete default, define non-focus exposure as the sum, over currently unanswered threats other than the selected attack reference, of damage weight × max(0,(enemy centre reach−distance)/enemy centre reach), with artillery dead zones excluded. Prefer a progress-making one-tick displacement that does not increase this measure (numerical tolerance 1e−6); include newly entered threat reaches in the proposed sum. If every progress-making direction increases exposure, apply the aggregate transit budget rather than an unconditional veto. Use observed geometry and realized movement capacity, not hidden projectiles or a lookahead fight.

**Attack transit has an explicit aggregate risk budget:** permit commit only with positive radial capacity before arrival and estimated loss `q × max(time_to_own_legal_reach, 0.5 s) ≤ 0.25 current HP`, where q is *all* observed incoming cross-team HP loss over the preceding 0.5 s divided by 0.5 s, including fire from the focus and other enemies. Estimate time from remaining distance divided by observed positive radial speed, capped by nominal speed; zero capacity fails after the acquisition window. With no damage/speed history, allow one bounded 2 s acquisition intent, subject to the progress window and minimum-exposure choice among progress-making directions. Arrival permits legal attack subject to the continuing minimum-horizon risk check; reference loss, failed progress or excessive loss replans. Own death removes state; reference death/loss clears intent before deterministic reselection. An invalidated intent cannot reacquire the same reference/mode until its failed condition observably clears and a fresh threshold crossing occurs. The rate is an observation-based risk estimate, not a forecast of unseen shells. This permits deliberate transit through overlapping gun arcs while keeping their combined observed pressure in the budget. Constructed multi-threat/corner cases must test deterministic fallback rather than promise feasible progress in every geometry. The drafter owns the final rule and self-audit before implementation; none of these constants is claimed optimal from v4.

Before choosing a replacement, predeclare a small **2×2 comparison** (hold off/on × focus off/on) using a common v3 skeleton, common geometry/seed/orientation inputs and fixed knobs for mechanism attribution; then equal-budget retuning for package performance. Include v4-style rules as a labelled historical comparator if resources allow. New progress/safety rules require their own declared variant. No such execution is authorized here. Report latent threshold changes, unit-intent switches, pair changes, focus changes, actual movement reversals, exposure-time, arrival/death/censored holds and undefined displacement separately. Predetermine trace seeds; do not generalize one dramatic replay. Proceed to C only after a declared fresh B novice/regular development gate passes, rather than consuming another large C budget with a losing head.

**Objective: retain S for continuity; make the tactical goal explicit.** S=own survivors−enemy survivors values either side's unit removal equally; it does not weight guns, HP or active engagement. V3 morale's +8.55 coexists with 8.96 enemy guns alive/fight and 191 timeouts. “Beats regular on S” and “destroys regular's guns” are different tasks. Do not retrospectively replace S with a score that favors this new policy or use D to break an S tie.

For the stated goal of beating regular, recommend regular-head S as the primary development selection target, with novice performance retained as a declared constraint; the current ten-novice/nine-regular pooled mean can reward novice gains while accepting regular losses. Predeclare that selection rule, eligibility/fallback and resource allocation in v5 rather than changing this record. Keep gun survival/elimination fraction, timeouts, role survival, damage and time-to-elimination alongside S. If the owner instead requires complete enemy/gun destruction, approve a separate task-level win/elimination endpoint before fights and retain S as a labelled comparison; do not hide the change in a gun bonus. A later superiority claim needs fresh judging entropy and the existing approval/registration gates.

Suggested stop rows for the new proposal (yes/no, one action, one role):

| Yes/no condition | Action | Responsible role |
|---|---|---|
| Is attack-versus-retreat intent/safety priority undefined or contradictory? | Return the proposal for repair. | Drafter |
| Does a constructed wall/stale-commit/rearm case violate the declared rule? | Repair the implementation before development. | Implementer |
| Does the declared fresh B gate fail? | Stop before C and report the failure. | Implementer |
| Does source identity change or projected cost exceed the declared cap? | Stop and preserve the attempt. | Implementer |
| Is the requested objective a change from the approved S task? | Decide the new objective before execution. | Owner |
| Does the bounded review find an unresolved design/evidence defect? | Return CHANGES_REQUIRED. | Reviewer |

## Review, preservation and delivery

The mandatory verbatim owner request was sent to a separate Codex reviewer. Only Codex-family reviewers are available through this session's collaboration interface; this is an additional adversarial check, **not** the pending Claude cross-family v4 development review. Its findings and disposition are in [scoped plan/recheck record](s4_v4_recheck_checks/PLAN_AND_REVIEW.md). The user's explicit astelia_cpp-only scope takes precedence over AGENTS.md's root-plan update, so `docs/PLAN_CURRENT.md` is not edited; the record includes a paste-ready B3 update for its owner.

Validation consists of read-only count reconciliation, source/artifact hash checks, report checks and a scoped diff check. No full suite or experiment pipeline is appropriate for this analysis-only delivery while the timing benchmark runs. [Delivery note](s4_v4_recheck_checks/DELIVERY_NOTE.md) records exact scope, provenance and verification. Original fights, seeds, receipts, replay exports, design and controller code remain unchanged. The unresolved gates are a reviewed v5 design and the separate Claude development review; this report completes the requested read-only recheck.
