# What we did, 7–8 October 2026 (day and night)

**Author:** Claude (claude-opus-5-5), with Codex (GPT-6) as implementer and cross-family reviewer.
**Goal:** an AI built on our own foundation (RRG: growing oscillator structures) that beats Astelia's scripted AI. A win means **efficient elimination**, not survival.
**Notes:**
- **Every result below was rechecked by Codex** with your verbatim prompt, and every claim was narrowed to what the data show.
- Nothing is pushed beyond what you pushed (`cbe2da2`). Everything after that is committed locally.
- **The laptop rebooted at 21:51.** No committed work was lost; one analysis was recovered with an auditable record.

## 1. For you to decide (morning)

1. **The S5 registration of v7:** `evidence/tactical_composition_demo/S5_V7_REGISTRATION_PROPOSAL.md` (revision 4; Codex APPROVE_WITH_NOTES after 4 rounds). To approve:
   - **S as a reported secondary,** as in your DESIGN_0G §19; the verdicts use the elimination-win rate only;
   - **the 200-cluster sizing cap,** which replaces the old 2,000;
   - then I have Codex build the sealed specification and the planning receipt (no fights). The registered run needs your final go.
2. **0h direction:** see §3. The coverage problem looks like **capacity**, not ordering. The capacity diagnostic ran overnight (§3).
3. **Already decided by you:**
   - **DESIGN_0H_REV7 §19.7 (the multi-key F5 gate): approved as written.** The seeded-start-secondary and stop-on-first-failure changes remain proposals.
   - **The 0g >50% scripted witness came first** (done; P16).

## 2. 0g: beating the scripted AI

| Step | Elimination wins vs regular | Evidence |
|---|---|---|
| start of 7 Oct | 0/20 (all arms) | — |
| **Spacing** (each enemy shell hit about 4 of our bunched guns) | 2/20 | `S4_SPACING_PROBE.md` |
| **Ranged escorts** (sacrificial shields) | 6–8/20 | `S4_ESCORT_PROBE*.md` |
| **P16: splash-value gun focus** | **19/20**, then **34/40 (85%) replicated**; mean S positive | `s4_escort_probe_v3/v4` |
| **v7: resonator gate** (per-unit oscillator decides commit/escape; commit = P16's action) | **32/40 (80%), mean S +4.68; novice 40/40** | `S4_V7_VALIDATION_REPORT.md`, DESIGN §20.3/20.3.1 |

- **v7 meets your criterion in development:** more than 50% elimination wins, S > 0 on both heads, no failures. It is the first explicit oscillator-gated controller in our series to do so.
- **Honest limit:** against the matched always-commit arm (31/40), the gate is an **observed match** (+1 win). The resonator's timing adds no measurable win gain at this setting. Always-escape wins 0/40.
- **The open RRG question for after S5:** what the resonator itself can add, for example target-group synchrony as the decision source instead of a fixed ordering.
- **Process incidents, all caught by guards and fixed as new versions on fresh seeds:**
  - a projection warm-up defect (v7 → v7b);
  - a native request-flag bug (v7b → v7c);
  - the reboot-interrupted analysis (recovered with the boot-time evidence).

## 3. 0h: growing shapes

- **Solved:**
  - **D3 cut live chains:** service-protected pruning (V1/RD3) fixed it; the empty start went 3/5 → 5/5.
  - **Integrity-checked telemetry** classifies every failure.
  - **COV-A gives the first 10/10 gate shape** on the exploratory keys.
- **Not solved: coverage.** The far sensors (sites 4–6) are served under 10% of the time.
- **What we learned tonight:**
  - **Ordering is not the lever.** COV-A (longest wait) and DEBT (cumulative debt) give **identical** per-site service, and every scheduler only redistributes a fixed total.
  - **The total service index** (Σ of 8 per-site fractions) is RD3 2.15, COV-A 1.74, DEBT 1.74 (identical; Codex N4 corrected the earlier 1.82). **Freeing material raises it** (COV-B recycling 2.50) and **removing material lowers it** (ECO-R thinning 1.16; ECO-R also broke the response, 0/8 gate).
  - **ECO-F (front retraction) was inert:** every "front" body is a sensor root (the reach-3 zones cover 97% of the arena), so there was never an eligible donor.
  - **The waste:** 60–68% of the cost sits in root mass near sensors without a link to O, mostly B-path-born.
- **The capacity diagnostic** (resource ceiling ×1.5 and ×2; night run, 20 runs plus 2 off controls; integrity PASS; `CAPACITY_DIAGNOSTIC_REPORT.md`, commit `f33d194`): the reading is **CAPACITY_SCALES_WITH_RESOURCE_CEILING**, as declared in Amendment 2.

  | Ceiling | Total service index | Sites 3–6 pooled | Weakest site | Gate empty / seeded |
  |---|---|---|---|---|
  | 64 (RD3) | 2.148 | 0.086 | 0.019 (site 4) | 5/5 / 3/5 |
  | 96 | 3.212 (×1.50) | 0.261 (×3.0) | 0.100 (site 5) | 5/5 / 5/5 |
  | 128 | 3.458 (×1.61) | 0.300 (×3.5) | 0.148 (site 5) | 5/5 / 5/5 |

  - **What it means:** in this *dynamic* medium the resource ceiling does bind. That holds even though a *static* eight-spoke star would cost only 22.4. More material buys far-site service, and the gate does not degrade.
  - **Diminishing returns:** most of the gain arrives by 96. Doubling to 128 adds little more, and no site reaches full service (site 5 stays under 15%).
  - **The tension with your research update** ("do not raise the budget yet"): the data show that the budget is a real lever, not that allocation is solved. More budget may only mask waste: 60–68% of the cost sits in fronts. Codex's recheck of this result is in `docs/reviews/tactical_0h_capacity_result_recheck_codex.md`.
  - **Codex's result recheck** (`docs/reviews/tactical_0h_capacity_result_recheck_codex.md`, PASS_WITH_NOTES): every number recomputes, and the reading follows Amendment 2 exactly. Its notes:
    - **The extra material goes into service redundancy, not fronts.** In the late window, redundant cost goes 23.8 → 56.8 → 76.2 while front cost *falls*, 37.7 → 35.1 → 28.7. The front "tax" stays about 29–38 regardless of the ceiling, and the gain comes from more parallel route material. This agrees with ECO-R, where thinning redundancy collapsed the response.
    - **The gain is mixed:** D3 pruning starts later and much less often (34 → 17 → 1 removals), and cost refusals start later. The count ceiling never bound (at most 67 bodies at 96).
    - **Pooled numbers hide starvation:** at ceiling 96, site 5 gets **zero** service in the empty start. At least one site gets zero service in 8 of 10 runs at 96 and in 5 of 10 at 128. The 10/10 gate shape does not mean full coverage.
    - **No contradiction with your research update:** the static 22.4 star shows feasibility, not that the dynamic growth can reach it. "Allocation is the problem" still stands; the ceiling simply binds for the current law.
  - **A stored discriminant settled the options** (`FRONT_TIPS_ROOTZONE_DIAGNOSTIC.md`, `fbf7055`; 50 stored runs, no simulation; Codex recheck PASS_WITH_NOTES):
    - **The front tax is a blob sitting on each sensor.** 96–97% of front cost lies within 1.44 of a sensor.
      - **Correction of my earlier option:** a narrower root zone would release almost nothing (0.08–0.13% of front cost). I withdraw it.
    - **One active front per site targets a minority:** competing tip subtrees own 17–25% of the unserved front cost, and only about 2–3% of checks have several tips inside one blob.
    - **Ordering is ruled out:** DEBT matched COV-A exactly.
    - **Recycling is limited:** COV-B, which may recycle any non-service body including roots, plateaued at index 2.50, against 3.21 at ceiling 96.
    - **The sharpest fact:** about 99% of persistent growth tips make **no meaningful progress** (one in-phase spacing, 0.556) from one sample to the next, and almost every stall of 60 s or more has zero such progress. Front cost is mostly B-path-born (68–73%). **So B-path keeps feeding births into fronts that do not advance:** the motion law pulls them back into the sensor blob.
  - **Your decision (0h):**
    - (a) **adopt ceiling 96** into the candidate law. It is measured: gate 10/10, far sites ×3, and the extra material is shared route redundancy (55–57% supports far sites). It is not full coverage: site 5 gets no service in the empty start.
    - (b) **keep 64 and test one change, a stall gate on B-path funding:** a site whose best tip has not advanced one in-phase spacing (0.556) over a declared window gets no further B-path births until it does, or until its roots change. The budget then goes to sites that progress.
      - The rule is task-blind, and its quantum comes from the placement scale.
      - It is the research update's "meaningful-progress" idea applied to **births**, not removals. Removal is blocked here because every front body is a root.
    - (c) **(b) first, as one exploratory pilot (about 1 h),** with 96 as the measured fallback.

    **My recommendation is (c).** (b) targets the measured mechanism: births that never advance. One-active-front is a weaker second, because it targets 17–25% of the front cost.
- **Your research update** was assessed: adopted except one correction (the fronts are mass sitting on the sensors, not bridge tips). See `docs/reviews/rrg_next_steps_assessment_claude.md`.

## 4. C6

Unchanged: the inexact kernel is adopted; the milestone is BLOCKED.
