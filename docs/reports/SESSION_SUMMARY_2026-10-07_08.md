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
  - **The total service index** (Σ of 8 per-site fractions) is RD3 2.15, COV-A 1.75, DEBT 1.82. **Freeing material raises it** (COV-B recycling 2.50) and **removing material lowers it** (ECO-R thinning 1.16; ECO-R also broke the response, 0/8 gate).
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
  - **What the stored data already rule out** (`FRONT_ALLOCATION_DIAGNOSTIC.md`):
    - **"One active front per site"** (the research update's rank 1) can free little. An unserved site has 1.15 front components on average, and only 13–18% of the owned front cost lies outside its largest component.
    - **Service-debt ordering** was tested (DEBT) and matched COV-A exactly.
    - The research update's decision tree therefore reaches its last branch: **revisit the geometry or representation.** The measured cause is that the sensor root zones (reach 3) cover 97% of the arena. "Front" mass is therefore mostly root mass near sensors, and no recycling rule may touch roots.
  - **Your decision (0h):**
    - (a) **adopt ceiling 96** into the candidate law. It is measured: gate 10/10, far sites ×3. It is the price of a dynamic medium whose structure is always partly in flux.
    - (b) **keep 64 and test one representation change:** a narrower sensor root zone, matched to the strong-edge range (about 1.44) instead of 3.
      - **Note:** this also changes how sensors drive the medium, not only the bookkeeping.
      - **Recycling root mass is already tested:** COV-B's donor may be any non-service body, roots included. That allocation route plateaued at index 2.50, against 3.21 at ceiling 96.
    - (c) **both:** run (b) at 64 as one exploratory pilot, and keep 96 as the measured fallback.

    My recommendation is (c). Option (b) attacks the measured waste at its cause, and (a) is already known to work if (b) fails.
- **Your research update** was assessed: adopted except one correction (the fronts are root mass, not bridge tips). See `docs/reviews/rrg_next_steps_assessment_claude.md`.

## 4. C6

Unchanged: the inexact kernel is adopted; the milestone is BLOCKED.
