# 0h: the failure report of the revision-5.1 development run, and the revision-6 draft

**Status:** DRAFT by the drafter (Claude). Not reviewed, not approved, and no run is authorized. Any change below is a new design revision on **fresh development seeds** (section 12's stop row); the recorded run keeps its verdicts.

## 1. Failure report (the stop row "Does G0' FAIL? → write the failure report", the drafter's duty)

**Run:** `growing_shapes/runner/DEVELOPMENT_REPORT.md`, imported at `7e5f6b0`; Claude review `growing_shapes_review_claude/DEVELOPMENT_REVIEW.md` with addendum 1.

**Verdicts (unchanged):** both arms G0 INCONCLUSIVE, G0' FAIL, G1 PASS, G1c descriptive, G5 PASS. Development stopped.

**What happened, in causal order** (all from the committed `REPORT.json.gz` files):

1. **The read-out region was empty in every run with learning.**
   - The read-out uses elements strictly within 2 m.u. of the origin (section 3).
   - Births are placed on a spiral around the sensor sites, at radius 4. Their final positions lie between radius 3.47 and about 9 in all 16 intact runs, and **not one element is within 2 m.u.**, nor even within 3.
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
| **R6-2** (D2) | The control can never pass: it drops requests at the budget | A request stays in the queue until it is feasible. A seed is compared only if the control's additions are ≥ 0.9 × the intact run's; otherwise it is flagged. Drops at the horizon are reported. | Comparing two policies needs matched birth counts. A rule that flags every seed tests nothing. |
| **R6-3** (D4, the root cause) | Growth cannot reach the read-out, so there is no input-to-output path | **Pending research** (section 3 and `docs/RESEARCH_AND_REVIEW_NEEDED.md`). A minimal placeholder is an **output site** at the origin with its own demand rule ("B-out": no read-out weight for 20 s → a birth on a spiral at the origin). The phase must still come from the inputs through coupling, which is what a learned path means. | This matches the owner's "path" idea: structure has to connect what it senses to what it does. |
| **R6-4** | Process | (a) The path-exists stop row of the lesson above. (b) Unattended runs under `caffeinate -i -s`; report awake time and elapsed time separately. (c) Raw ledgers stay out of git, with each file under 50 MB. (d) A 50-episode engineering smoke must show the read-out is non-empty (Σw > 0) in at least some episodes before any development run. | The 5.1 run could have shown failure 1 within minutes. |

## 3. What needs research before R6-3 is fixed

The open question is no longer about growth: growth works. It is **how a grown oscillator structure produces an action, and how a structure gets credit for it.** Options to compare:

- **(a) A read-out bridge grown by demand** (the B-out placeholder): an output element must lock to sensor phases through intermediate elements. This is closest to the theory, but bridging 2+ m.u. requires chains, which the current B1 does not grow.
- **(b) Per-structure read-outs:** each qualified structure gets its own read-out at its centre (as G1c copies do), and the library chooses which structure answers. That gives modular credit, but risks a trivial echo, because a structure on a sensor reproduces that sensor's phase.
- **(c) Learned phase-to-action maps** (AKOrN-like, or a small trained read-out). This is well studied, but it moves the "intelligence" into a conventional learned layer, which is the repeat-of-existing-AI risk.
- **(d) A read-out on the sensor ring with a delay or a transformation requirement,** so that an echo scores at chance and only a transformation scores.

The research file lists the exact questions. The drafter chooses among (a)–(d) after the research and the Codex recheck, then submits revision 6 for review and owner approval.
