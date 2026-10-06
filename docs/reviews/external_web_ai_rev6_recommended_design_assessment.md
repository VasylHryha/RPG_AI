# Assessment of the owner's external "Revision 6 functional bootstrap" design (2026-10-06)

**Source:** `docs/reviews/external_web_ai_rev6_recommended_design_2026-10-06.md`, written against `fba4332`, the revision-6 draft. **Assessor:** Claude (the drafter of `DESIGN_0H_REV6.md`, now 6.5: approved by Codex round 6, implemented, under implementation re-review).

## What it gets right, adopted into revision 6.5 regardless

1. **An input-only phasor baseline** (its B2): arg Σ k_s e^{iα_s} from the same encoded inputs, with no medium. This is the most important missing comparator in 6.5. A grown relay can beat default, random, donor input and the lesion while doing nothing more than this average. The medium must beat it to show that oscillator dynamics compute anything.
2. **A K = 0 ablation** (its C3): the same state with internal coupling off and drives kept. It separates collective interaction from independent driven elements. It is not element deletion.
3. **A fixed-structure comparator** (its B5): the same geometry, with growth off. It separates having a structure from growing one.
4. **Active-time demand timers** that freeze rather than reset while a site is inactive (its §4). They fix the memory-cue timing defect (external recheck A01) without a task label. (**Correction:** this changes a growth rule, so it goes to the next revision, not 6.5; see design 19.9.)
5. **A case-by-case failure taxonomy** (its §19), so one verdict does not hide different failures.
6. **The scope:** perceive primary, memory with its simple baselines, choose and move deferred. This matches 6.5's sections 19.1–19.3.

## The critical problem: overlap elements collapse inward under the unchanged C4 law

Its §3 places newborns in the lens 1 < r < 2 (at r* = 1.9), where sensor drive (strict < 3 from a site at radius 4) and the read-out (strict < 2) overlap. §6 keeps the C4 law unchanged. But C4 motion is A(1 + J cos Δθ) − B/r toward each neighbour within 3.
- For the eight-site ring at r = 1.9, an element has 4 ring neighbours.
- Computed radial velocity of the element at (1.9, 0): **−0.72 m.u./s with all in phase; −0.28 m.u./s with uncorrelated phases.** The motion is inward.
- The lens is 0.9 m.u. wide (1.9 → 1.0). It is crossed in **about 1.3–3 s**. Below r = 1 the distance to the site exceeds 3, so **drive is lost** while the element stays in the read-out.

So the interface collapses into an undriven clump at the centre within one episode. Its E6 mobile-viability gate would fail by construction, and its §9 stop rule would end the revision. **This is predictable on paper and needs no run.** It is a property of C4's aggregating attraction. Any functional interface in this medium needs an explicit anchoring decision. The document defers that decision to "the next revision", but the collapse makes it necessary now.

(6.5's grown chains face the same aggregating force. Its F1 measures chain persistence over 160 s of free motion, and its soft wall only bounds outward drift.)

## Smaller points

- **Control M with a cost skip** (its §13.1) brings back the asymmetry that Codex review C6 rejected. 6.5 applies the same budget and requires exact matching instead (unmatched seeds INCONCLUSIVE). We keep 6.5's rule.
- **Its r* = 1.9** sits 0.1 from the read-out boundary. Small repulsions move elements across it.
- **The empty start** (§7) is a good attribution choice. It is worth adopting in the next revision.

## Recommendation

- **Keep revision 6.5,** which is approved, implemented and under re-review. **Add its three comparators** (input-only phasor, K = 0, fixed structure) to the evaluator before any development run.
- **Run 6.5's fixtures (about 2–6 minutes, owner approval pending).** F1 and F5 directly measure whether grown structure persists under C4 motion. That is the same question as its E6, and the computation above predicts a real risk.
- **If persistence fails,** the next revision makes the anchoring decision explicitly. Both designs need it. The decision would be followed by the overlap-lens simplification (with anchoring), or by 6.5's path growth (with anchoring), whichever the fixtures favour.
