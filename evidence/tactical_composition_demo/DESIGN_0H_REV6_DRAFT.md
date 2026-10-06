# 0h: the failure report of the revision-5.1 development run, and the revision-6 draft

**Status:** DRAFT by the drafter (Claude). Not reviewed, not approved, and no run is authorized. Any change below is a new design revision on **fresh development seeds** (section 12's stop row); the recorded run keeps its verdicts.

## 1. Failure report (the stop row "Does G0' FAIL? → write the failure report", the drafter's duty)

**Run:** `growing_shapes/runner/DEVELOPMENT_REPORT.md`, imported at `a9cbe83` (`7e5f6b0` before the history cleanup); Claude review `growing_shapes_review_claude/DEVELOPMENT_REVIEW.md` with addendum 1.

**Verdicts (unchanged):** both arms G0 INCONCLUSIVE, G0' FAIL, G1 PASS, G1c descriptive, G5 PASS. Development stopped.

**What happened, in causal order** (all from the committed `REPORT.json.gz` files):

1. **The read-out region was empty in every run with learning.**
   - The read-out uses elements strictly within 2 m.u. of the origin (section 3).
   - Births are placed on a spiral around the sensor sites, at radius 4. Their final positions lie between radius 3.47 and 246 in all 16 intact runs (corrected from "about 9"; see section 4, D5), and **not one element is within 2 m.u.**, nor even within 3.
   - So Σw = 0, and the medium **abstains in every evaluation episode.** Its score is the abstention floor: perceive 0.0050, move −0.0329, remember_static −0.1075, choose 0.2231. That is identical to every digit in all 16 runs.
   - Only the two controls whose random placement (a disk of radius 5) left elements near the origin scored differently: task_blind 106062 has 15 elements inside radius 2, and reward 106077 has 1.
2. **The population is pinned by the budget.**
   - The cost N + 0.1 × pairs reaches 64 at N ≈ 44. N is 42–45 over the last 20% in every seed, intact and control alike.
   - Coverage is 6–22%: sites stay uncovered, B1 keeps asking, and the cost cap rejects the births. This is the G0' FAIL.
   - D1 removes unlocked newborns, so the medium churns at the cap.
3. **The G0 control was starved and always flagged.** It made 23–71 additions against the intact run's 74–149, and dropped requests in 16 of 16 seeds.
4. **What does stand:**
   - structures form and qualify (11,862 snapshots, in all 16 seeds);
   - copies reproduce numerically (G5);
   - the engine, runner and accounting are faithful.

**Responsibility:** items 1–3 are design defects of the drafter. They are not implementation errors. Item 1 was in every revision since 2 and passed five reviews: nobody checked that growth can ever reach the read-out.

**Lesson:** for every output path, a design must show that some rule can put state there. A "path from input to output exists" check should be a stop row before any run, demonstrated on the engine with a tiny hand-built configuration.

## 2. Revision-6 changes the drafter can make now

| ID | Defect | Change | Why |
|---|---|---|---|
| **R6-1** (D1) | G0' fails whenever the population lives at its budget | G0' keeps the slope band (±0.5 per 100 episodes) and the protected-over-budget fail. Late rejections **for cap and cost** are reported as a classification, *budget-limited* or *self-limited*, not as failure. Placement rejections stay a failure. | Count stability is the claim. Being limited by the budget is information about capacity, not instability. R2-7's concern (settling forced by cost) is answered by **reporting** the class, not by failing it. |
| **R6-2** (D2) | The control can never pass: it drops requests at the budget | **Decided by the owner, 2026-10-06: both controls.** The matched control (ii) is the registered pass/fail comparison; the unmatched control (i) is reported for information only. Specification in section 5. | A rule that flags every seed tests nothing. Two pass/fail checks on one question would make the verdict ambiguous. |
| **R6-3** (D4, the root cause) | Growth cannot reach the read-out, so there is no input-to-output path | **Pending research** (section 3 and `docs/RESEARCH_AND_REVIEW_NEEDED.md`). A minimal placeholder is an **output site** at the origin with its own demand rule ("B-out": no read-out weight for 20 s → a birth on a spiral at the origin). The phase must still come from the inputs through coupling, which is what a learned path means. | This matches the owner's "path" idea: structure has to connect what it senses to what it does. |
| **R6-4** | Process | (a) The path-exists stop row of the lesson above. (b) Unattended runs under `caffeinate -i -s`; report awake time and elapsed time separately. (c) Raw ledgers stay out of git, with each file under 50 MB. (d) A 50-episode engineering smoke must show the read-out is non-empty (Σw > 0) in at least some episodes before any development run. | The 5.1 run could have shown failure 1 within minutes. |

## 3. What needs research before R6-3 is fixed

The open question is no longer about growth: growth works. It is **how a grown oscillator structure produces an action, and how a structure gets credit for it.** Options to compare:

- **(a) A read-out bridge grown by demand** (the B-out placeholder): an output element must lock to sensor phases through intermediate elements. This is closest to the theory, but bridging 2+ m.u. requires chains, which the current B1 does not grow.
- **(b) Per-structure read-outs:** each qualified structure gets its own read-out at its centre (as G1c copies do), and the library chooses which structure answers. That gives modular credit, but risks a trivial echo, because a structure on a sensor reproduces that sensor's phase.
- **(c) Learned phase-to-action maps** (AKOrN-like, or a small trained read-out). This is well studied, but it moves the "intelligence" into a conventional learned layer, which is the repeat-of-existing-AI risk.
- **(d) A read-out on the sensor ring with a delay or a transformation requirement,** so that an echo scores at chance and only a transformation scores.

The research file lists the exact questions. The drafter chooses among (a)–(d) after the research and the Codex recheck, then submits revision 6 for review and owner approval.

## 4. Refinements from the Codex recheck (accepted by the drafter; self-audit)

| Item | Recheck finding | Drafter's change | Cause of the drafter's error |
|---|---|---|---|
| Failure report, item 1 | Final radii reach 246, not "about 9"; 9,493 of 11,862 snapshots are out of reach of every sensor | **New defect D5: no confinement**, so groups drift out of sensing and action. Revision 6 must keep structures within reach: an anchoring term to the sensor ring, an arena bound, or death on leaving sensor and read-out reach. Which one is chosen with R6-3. | Read only the first members of the final template; did not compute the full radius range |
| R6-1 | Justified; "self-limited" must never describe a cost-limited population; report demand, rejection rate, churn and uncovered exposure | Adopted. Three classes: `cost-limited`, `cap-limited`, `demand-free` (no birth request in the window). Placement and protected-over-budget stay failures. | Under-specified |
| R6-2 | Retained requests can block the queue; a ≥ 0.9 additions rule would flag every current seed; matched additions do not match timing, ages or exposure | **Decided by the owner: both**, with (ii) the registered pass/fail check and (i) descriptive (section 5). | Proposed a fix without checking it against the run's own numbers |
| R6-3 | B-out at the origin receives no direct drive (sensors at r = 4, reach < 3); an output port needs a persistent coupling path, and a learned transformation that the default action, an echo or a single oscillator cannot satisfy | Kept pending the research (`docs/RESEARCH_AND_REVIEW_NEEDED.md` B1 to B4). The endpoint must beat **both** default and random, with paired uncertainty per seed and evaluator-side interventions that break the input, the coupling path or the output. For memory, hidden-period output must depend on the prior visible input. | The placeholder ignored the reach geometry |
| R6-4 | "Σw > 0 at some time" is too weak; the smoke exceeds the CLI cap and needs its own approval; record UTC start and end, suspend status and per-episode traces | Adopted. The path-exists check runs after warm-up, across all four tasks, permutations and hidden intervals: a non-default output that responds causally to the input. Per-episode scores and compact per-step Σw, coherence and actions are retained. Ledgers in chunks under 50 MB, with content-addressed recovery state. | Under-specified |
| Engineering (recheck section 6) | The dormant `development.execute_arm` aggregation bug; `summarize()` is not read-only; old SHA references after the history cleanup; the old bundler stages ledgers | Required in the revision-6 implementation batch (Codex) | Implementation debt, found by the recheck |

## 5. R6-2 as decided: two controls per seed

**The owner's words (2026-10-06):** "so do it", in answer to the drafter's recommendation: "run both, with (ii) as the registered pass/fail check and (i) reported for information only".

Each intact seed gets two paired controls. Both use the intact seed's medium seed and D1/D3 rules, and B1 off.

**Control M, matched births (registered; G0 is decided on it):**
- **Timing and count.** At every growth check, after D1 and D3, control M attempts exactly as many births as the intact run **accepted** at that check, at that same check. There is no queue, no retry and no carry-over.
- **Where and which phase.** Each newborn goes to a uniformly random sensor site s', drawn with replacement from the 8 physical sites. It is placed by the same spiral rule as an intact newborn, with a phase uniform in [0, 2π).

  The intact run puts its newborn at the **uncovered site that asked for it, with that site's phase**. Control M keeps the placement region and changes only these two choices. G0 therefore tests whether need-driven placement and phase beat random ones, at equal birth count and timing.
- **The budget.** A control-M birth checks only the cap (N + 1 ≤ 64) and spiral placement. Cost is **not** checked at birth: a cost excess is removed by D3 at the next check, as in the intact run.

  This keeps the birth schedule identical. The price is that control M can sit up to 20 s over the cost budget. Its time over budget and its D3 removals are reported.
- **Newborns** have ω = π, g = 1 and the same 20 s protection as intact newborns.
- **Validity.** A birth that fails the cap or placement is logged as **unmatched**. A seed with more than 5% unmatched births is flagged and counts as non-PASS for G0. The matched fraction is reported for every seed.
- **Entropy.** Draws come from the control-M entropy domain (`g0_matched`), paired by medium seed.

**Control U, the as-is policy (descriptive only; no verdict):**
- The revision-5.1 control-queue rule, unchanged: FIFO, 2 placements per check, at most 2 attempts per request, drops logged, random position in the disk of radius 5 and random phase.
- **Reported:** its additions, drops, coverage and competence beside the intact run. This answers whether the growth rule also wins by fitting in more births. It never enters a verdict.

**G0 in revision 6:**
- G0 compares the intact run with **control M only**. Its estimands follow R6-3, which is still pending: the output mechanism and the paired endpoint against both default and random.
- Control U's comparison is a separate descriptive row.

**Cost:** control U adds one control training per seed, about a third more compute. The development-run estimate in the revision will include it.

**Open for review (Codex):**
- whether random-site placement (above), or a uniform disk, is the better control region once D5's confinement is chosen;
- the 5% unmatched threshold.
