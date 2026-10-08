CHANGES_REQUIRED
Reviewer family: Claude
Reviewed commit: 0380d2a (`evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/DESIGN_UNITS_AND_LEADER.md`, revision 2; with `docs/reviews/network_units_and_leader_design_r2_recheck_codex.md`)
Date: 2026-10-08
Review type: cross-family owner recheck, round 2 (author Codex). Quick check under decision 0036's lighter process. This is not a milestone acceptance or an execution approval.

**What I did.** I read revision 2, my round-1 report, Codex's r2 self-check, decisions 0035 and 0036, the planner `src/native/artillery.cpp`, `teacher.cpp`, the GAME artillery catalog entry in `src/native/catalog_data.h`, and the V2 lab read cited in §1. I ran no Python, tests, fits, fights or native code, and I did not open `_local/`.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Summary

Revision 2 is a large improvement:
- All round-1 findings are addressed on paper.
- The planner citations are accurate. I checked each line range in the §2 table against `artillery.cpp`, and `teacher.cpp:21–25` against its description.
- The staged path matches 0036.

There are four remaining problems:
1. **S3 is not yet a fair test of RRG's stateful mechanism (High).** The design's own construction makes the S3 timing labels a deterministic function of the current encoded view, so a memoryless leader can imitate them. The design concedes this ("a snapshot may solve it") but still names S3 the RRG test.
2. **The start-time wrapper makes the leader's aim stale at release (Medium).** This brings back the round-1 "worse aim" failure on moving targets.
3. **The S1 and S2 thresholds are too weak or not scaled to the cell (Medium).** The S1 policy-sensitivity bar is almost always met, and S2's "two own units saved per fight" is a full-army size applied to 2- and 10-gun drills.
4. **The first search cycle under-prices waiting (Medium).**

**What can proceed.** S0 is unaffected and can start once the protected job ends. S1 needs the metric additions in N-M1 and N-M2. S3 needs N-H1 resolved before any S3 data is collected.

## Round-1 findings: resolution

| Finding | Status | Evidence in revision 2 / residual |
|---|---|---|
| H1: labels anchored to the wrong point; no focus command; Singles removes lead | **Resolved, with a new residual (N-M1)** | §2 table (line ranges verified: 8–14 assign, 57–63 ready/coming and `.8*range/lob`, 64–65 Game Singles at `target->pos`, 66–69 clusters, 72–84 families, 86–96 scoring/rollout, 38–41 and 97–99 launch/leftover). Focus pointer before lock. Provenance-relative label offset. Singles, leftovers and plans with fewer than two guns give empty commands. The line-57 claim is corrected. The S0 counts are listed. The residual: the new start-time wrapper caches an absolute point through windup (N-M1). |
| H2: no timing signal; stateless teacher | **Resolved for S2; only partly resolved for S3 (N-H1)** | In S2, timing is masked and P/R is explicitly plumbing, with a reviewer stop row. Timing acts on start permission, with a cumulative 1 s wait cap. A search teacher is named. However, the S3 teacher is still Markov in the encoded view, so the "temporal coordination" test of 0036 still gives Φ or memory no task reason. |
| H3: scope against 0036 | **Resolved, with a note (N-M3)** | S0–S3 order, one U fit, P/R once each, 100–200 pairs, full army after a working S2, no 30-fit matrix. Citing V2 (`d533e26`) in place of a new script-value gate is acceptable. That evidence is from the full 50-unit C3 army (deaths 36.22 → 33.47), which supports going to the full army next, but it gives no teacher-level reference for the drill cells (N-M3). |
| M1: the "group reaction" shift label | **Resolved** | Renamed threat-overflow correction, kept as a diagnostic rate only, and shift omitted. A real group reaction needs a joint teacher. |
| M2: lead horizon; aim scored on no-effect rows | **Resolved** | Three-step fixed point on the actual distance/lob, with a residual gate. Aim loss is on release-opportunity rows. No windup is added to release-row lead (correct). The contraction factor is about speed/lob ≈ 55/300, so three steps are ample. |
| M3: P/R fairness; unused slot token | **Resolved** | R replaces P's memory, parameters are matched within 10%, and the slot output is removed. |
| M4: contestedness unvalidated | **Partly resolved (N-M2)** | A separate pilot entropy and cells frozen before outcome entropy are in place. The within-pair sensitivity bar is too weak to do its job. |
| M5: no full-army or Expert Iteration path | **Resolved** | 50-unit roster cited (`lab.py:86–100`). 64+64 tokens, all-public threats, none+64 target pointers. Hybrid bridge with an honest label. Value head and Expert Iteration section. Stale ES prerequisites removed. |
| L1: Hungarian matching | **Resolved** | Native binding, canonical insertion, assertion/counter, tied rows masked. |
| L2: decidability battery | **Resolved** | Exact-conflict gate plus one 0.02 bin. |
| L3: K cause | **Resolved** | K gradient magnitude checked at initialisation before refitting. |
| L4: planner not read | **Resolved** | Planner read and cited; citations accurate. |

## New findings

### High

**N-H1: The S3 timing labels are snapshot-decidable by construction, so the S3 P/R contrast still cannot test a stateful RRG mechanism.**

**Where:** §5 S3, lines 133–135 ("same serialized public group view… Equal inputs with deterministic search/tie order yield equal labels") and line 145 ("a snapshot may solve it"); §3 line 65 (zero exact conflicts required); §4 line 77.

**Evidence.** The search starts from the current public view. Hidden state is set to neutral defaults, and the line-151 stop row bans hidden opponent state. Every commitment the label depends on (outstanding plan, cumulative wait origin, remaining budget, expiry) is encoded as an observable input (§2 line 35, §5 line 131). So the improved label is a deterministic function of the current encoded input. That is exactly what the zero-conflict gate requires.

A trained memoryless leader can therefore fit the labels. Neither P's 8-coordinate memory nor R's persistent Φ has any task reason to be used. This is the round-1 H2 argument, which is also the argument of 0036 Change 3, moved from a stateless planner to a stateless search.

The design records the risk (line 145) and adds NOT_EXERCISED and "inconclusive" rows. However, it still calls S3 "the eventual RRG-vs-plain coordination test" (line 129). The most likely outcome is a tie that cannot be read, after the most expensive stage.

**Fix:**
1. Add a trained **memoryless leader P0** (the same encoder with no memory, one fit) as a development control in S3. Measure validation and closed-loop P0 against P before reading R against P.
   - If P0 is about equal to P, S3 is "Markov coordination imitation". Any R/P difference is then an inductive-bias or generalisation reading, never a temporal-mechanism one. State this now, in the S3 heading and the claims.
2. Give the owner a declared history-dependent variant (an owner decision). The source of this variant is **enemy dodge readiness**:
   - The GAME artillery "storm" dodge has a 1 s cooldown, probability 0.9 and 110 px distance, against a 40 px splash (`catalog_data.h` GAME/dodge). Dodge is the main way volleys miss.
   - Enemy EP and dash readiness are private (§7 ledger: "no private enemy EP"), but they can be inferred from the **public history** of observed dashes.
   - Let the search branches use the true dodge-readiness state **as a label source only**. This is privileged-teacher distillation: the closest method is Chen et al. 2019, "Learning by Cheating", and asymmetric actor-critic. The student sees only public observations and its own state.
   - "Volley when the target's dodge is spent" is then decidable from history but not from the current snapshot. P0 should lose, and P memory against R Φ becomes a real contest.
   - This needs:
     - a change to the line-151 stop row (allow the declared label-only use; features stay public);
     - replacing the zero-conflict gate for those labels with a check that the hidden variable is recoverable from a bounded public history window (for example, time since the last observed dash);
     - a coverage row for how often dodge readiness changes the label.
3. Read R against P as RRG evidence only on the variant where P0 is measurably worse than P.

### Medium

**N-M1: The start-time wrapper caches an absolute aim point through windup, so U+leader aims behind moving targets that U-alone leads.**

**Where:** §2 lines 33–39 ("Store/cache the resulting absolute requested point once"; "Preserve each feasible gun's start-plan aim through winding"); §3 line 57.

**Evidence:**
- The S2 wrapper runs the planner at **start** decisions, with startable guns projected as ready.
- The planner's led centres use `flight = .8*range/lob` with no windup (`artillery.cpp:62–63`). The original engine planner runs only on prepared guns, so it never had this lag.
- The GAME artillery windup is 0.7 s at speed 55 (`catalog_data.h`), so a moving focus drifts about 38 px during windup. That is about one splash radius (40 px).
- No leader label is defined at release-opportunity rows, so in S2 the cached start-time point is what the unit is conditioned on at commit.
- The result is a systematic aim handicap for both leader arms on exactly the moving and dodging cells S1 adds. This is the round-1 H1 "worse aim" failure in a new form. It can trigger the S2 park row for a wrapper reason, not a learning reason.

**Fix:**
- Split the command in two phases:
  - At start: focus, assignment and spread shape (the offset from the focus's *led* centre).
  - At the first release-opportunity row: **one declared refresh**. Recompute the led centre with the M2 actual-distance fixed point, add the spread offset, and cache the result once. This does not conflict with R2-4, because it is a single declared recomposition at commit, not continuous drift.
- Alternatively, at start, lead by the remaining windup divided by time_rate, plus the flight time.
- Add to S1 the commanded-point landing miss against the autonomous-intercept miss on moving cells.
- Add an S1 stop row: wrapper miss above the autonomous miss by more than one-quarter splash → revise the wrapper (drafter).

**N-M2: The S1 sensitivity bar is almost always met, and the S2 "useful" threshold is not scaled to the cell.**

**Where:** §5 S1 line 101 ("nonzero paired enemy-damage, kill or death difference in at least two of the 10–20 pilot battles"); S2 lines 117, 122 and 124.

**Evidence:**
- **S1 bar.** Any command change in a chaotic simulation perturbs the trajectory, so paired damage differs from zero in almost every battle. Death-saturated D2-10 passes on damage alone. The bar does not select a cell where a policy effect can be *detected*, and it omits what round-1 H3 step 2 asked for (an effect-size and detectability estimate).
- **S2 threshold.** "Roughly two own units saved per fight" is the 0033 size from the full army, where C3 has 36 deaths per fight. In D2-2 it is the whole roster, and in D2-10 deaths are saturated. Only "clear damage/exchange gain" is left, and that is undefined. So the park row (line 124) is a judgement call, not a yes/no row as AGENTS.md requires.
- **"Pathologically"** (line 122) is not measurable either.

**Fix:**
- In S1, report per cell and per axis the paired SD of the arm differences and the minimum detectable effect at 100 and 200 pairs.
- Declare per-cell useful effects before outcome entropy, for example own deaths as a fraction of the roster, kills per fight and exchange ratio. Retain a cell only if its minimum detectable effect is at or below the declared useful effect.
- Make the S2 park row cite those numbers.
- Replace "pathologically" with a numeric rule, for example closed-loop starts per start opportunity below one half of the teacher's on the same frozen cells.

**N-M3: The S2 outcome panel drops the teacher arms. That conflicts with 0036 and leaves the park row uninterpretable.**

**Where:** §5 line 117 ("Teacher snapshot head baselines are diagnostic, not extra full outcome arms"); 0036 recheck table, question 1 ("units+leader kills and fire per chance in D2-10, **vs teacher**").

**Evidence.** If U+P and U+R do not beat U on the drill cells, the design cannot tell "learning failed" from "group planning has no value in these cells". The V2 evidence is full-army only. Scripted arms are cheap: `COLLECTION_RECEIPT_V2.json` records 436.53 s for 200 fights.

**Fix:** run T-unit-alone and T-unit+wrapper on the same frozen paired fights as reference arms. Report the U/T and leader/T gaps.

**N-M4: The first search cycle's score under-prices waiting, and "relevant volleys" is undefined.**

**Where:** §5 lines 133 and 137 (common t+3 s cutoff; first-cycle terminal value zero); stop row at line 152.

**Evidence:**
- **Root volleys are covered.** With a delay of at most 1 s, windup 0.7 s and flight at most 320/300 ≈ 1.07 s, the root volleys land by about 2.77 s, inside the cutoff.
- **The cost of waiting is not covered.** The cost of a delayed start is the gun's lost fire rate (cooldown 1.2 s), which falls after the cutoff. With zero terminal value, that cost is invisible, so cycle-1 labels are biased toward hold/sync. Meanwhile, the enemy damage taken while waiting *is* counted.
- **The stop row is ambiguous.** Second volleys from immediate starts routinely cross 3 s, so the ">5% relevant volleys unresolved" row could fire every time or never, depending on how "relevant" is read.

**Fix:**
- Define "relevant" as the root-commanded volleys.
- Price throughput with a common fixed continuation under the frozen U+P autonomous controller, long enough for each gun's next cycle after the latest allowed start (about t+6 s). Alternatively, credit in-flight shells and remaining cooldown symmetrically for both sides, as `artilleryOutcome` does for in-flight shells (`artillery.cpp:48`, the `fly` term).
- Report the hold-label rate against an immediate-only search to show the bias is gone.

### Low

**N-L1: The slate is narrow, and cycle 1 is distillation, not yet Expert Iteration.** The slate covers artillery timing with two planner assignments. The 0036 precedent (a 6.1–6.5 streak) came from a commander-level look-ahead.
- State that parking S3 means "this timing slate does not help", not "search does not help".
- With a fixed planner slate and zero value, cycle 1 is search-teacher distillation. The ExIt property, where the apprentice guides the expert, starts only in a later cycle. Name it that way.

**N-L2: The common plain prior biases the labels against R.** "Current-focus" candidates come from the frozen S2 P (line 137), so the spatial labels follow P's choices. State that this bias works against R, and that an R spatial deficit under these labels is not RRG evidence.

**N-L3: The search cost has no formula.** Give per-state cost = expansions (≤36) × (3 s of simulated ticks plus the tail) × (engine tick plus U forwards per gun-decision). My rough order of magnitude is 1–4 s per search state. Clarify whether the 1 s value tail is per candidate or per state. Measure this before collecting.

**N-L4: Readability.** Several paragraphs (§5 S2 lines 111–117, S3 lines 133–141) are written in compressed shorthand with dropped articles and verbs. The owner has to approve the operative amendment, so the S3 search, timing and value paragraphs should be rewritten in plain sentences before approval.

## What is sound

- The planner facts are now accurate and line-cited.
- Focus before lock, empty Singles, and an explicit no-fabrication mask.
- The S2 P/R contrast is honestly labelled plumbing, with a reviewer stop row.
- The cumulative 1 s wait cap cannot be reset by renaming a plan (R2-7).
- A common score horizon (R2-8).
- Search commands pass through the frozen U and the deployment gates (R2-6).
- Shared labels for P and R (R2-1).
- Full army comes after a working S2 and does not wait for S3 (R2-2, matching 0036).
- Hybrid-army claims are labelled.
- Living documents are excluded from hash pins.

No numeric scores are assigned.
