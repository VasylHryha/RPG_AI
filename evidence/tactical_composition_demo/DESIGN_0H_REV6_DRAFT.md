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

## 6. R6-3 (output) and D5 (confinement): the drafter's choice after research

**Research basis** (short; links in `docs/RESEARCH_AND_REVIEW_NEEDED.md`, section E):
- **Oscillatory neural networks** read a decision from a designated output oscillator's synchrony with a reference, or from which cluster locks first. AKOrN uses a trained read-out module per block; that is option (c), which we avoid.
- **Growing neural gas** inserts a unit **between** the unit with the largest accumulated error and its worst neighbour, and removes units with low utility (the increase in error if removed). It is a direct precedent for growing a path where an error persists.
- **Activity-dependent axon guidance** moves growth toward targets by gradients from active targets: a precedent for attraction to active sites.
- **Adaptive-frequency oscillators** (Righetti, Buchli and Ijspeert, 2006) learn input frequencies by a Hebbian rule inside the dynamics. Our ω adaptation is of this kind.
- **The assembly calculus** reads out an assembly in a downstream area, which projection reaches; it needs a path, as we do.

**Diagnosis from the C4 law** (`geomind/c4_model.py`): motion is x_dot_i = mean_j[unit_ij · (A(1 + J cos(θ_j − θ_i)) − B/r_ij)] over **element** neighbours only. Sensors drive phase, never position. A group that locks internally therefore has nothing tying it to the world, and drifts as a unit. D1 cannot remove it, because its members lock to one another (L ≥ 0.5).

### 6.1 D5: anchoring through resonance with the input, and death on losing the world

- **Sites enter the motion law as drive-only neighbours** (no new law: the C4 attraction term with the site's drive phase). For each element i and each active site s with K(|x_i − q_s|) > 0:

      x_dot_i += k_s · K(|x_i − q_s|) · unit_is · A · (1 + J cos(ψ_s − θ_i)) / (1 + n_i)

  Here n_i is the element's neighbour count and unit_is points toward the site. There is no repulsion term: sites are not bodies.

  **An element in phase with a site moves toward it; an element in anti-phase is attracted only weakly** (factor 1 + J cos). Resonance with the input holds structure near the input. This is the "attraction to active sites" precedent, inside our own law.
- **Death rule D4, losing the world.** An element is removed if, for 40 s, it has **no path of C4 neighbour links** (within radius 3) to an element inside a sensor's drive reach or inside the output port. The same protection rules as D1 apply.

  A structure lives only while it is connected to the world's inputs or outputs. This replaces the drift that the 5.1 run showed (radii up to 246).

### 6.2 R6-3: an output port reached by a grown path

- **The output port** stays at the origin: elements within r < 2, with the same read-out and the same default actions on an empty read-out.

  The sensors stay at radius 4, so **the port cannot be driven directly** (drive reach < 3). Any phase at the port must arrive through coupled elements, which is a grown path. A direct echo of the drives is impossible by geometry.
- **B-out, output demand.** If the port has Σw = 0 for 20 s of a timer, one birth on the spiral at the origin is attempted at the growth check. Its phase is the circular mean of the elements within radius 3 of the newborn point, or uniform if there are none.
- **B-path, bridge insertion (the growing-neural-gas rule).** At each growth check, take the port element with the highest port weight and the nearest element locked to an active site (eligible PLV ≥ 0.8). If they are farther apart than the coupling radius 3, insert one element at their midpoint, with the circular mean of their phases. This happens at most once per check, and only if the cap and cost allow it.

  A missing path is the persistent error, and the insertion goes where the error is.
- **Budget order** at the growth check: D1, D4, D3, then B1, B-out and B-path. Sensor births (B1) do not outrank the path rules: they are processed in rule order and each is subject to the cap and cost.
- **Credit** is unchanged: the reward arm's three-factor gain update (Δg = 0.5 (r − r̄) e_i), with the eligibility e_i computed from each element's own drive lock.

  Port and bridge elements have no direct drive, so their e_i is 0. Their credit flows only through structure: they survive through D1 and D4 while they stay locked and connected. The rule is unchanged and declared.

### 6.3 The task-use endpoint (replaces G0's competence half; the recheck's requirements)

- **Per task and seed,** on the fixed panel, with per-episode scores retained:
  1. Δ_default = intact − the default action;
  2. Δ_scramble = intact − **the same final medium with its site bindings scrambled** at evaluation, which breaks the input;
  3. Δ_random = intact − the random policy.
- **"Task use" for a seed and task** requires all three Δ > 0, with a one-sided paired 95% bound above 0 over the episodes.
- **G2 (new, the registered task-use read-out):** PASS if ≥ 6 of 8 seeds show task use in at least one usable task, with **move** reported separately. FAIL if ≤ 2. Otherwise INCONCLUSIVE.

  The choose default already beats random, so choose counts only through Δ_default and Δ_scramble.
- **G0** compares the intact run with control M (section 5) on coverage and on G2's per-seed Δ_scramble.
- **Path-exists stop row (R6-4).** An engineering smoke, separately approved, must show Σw > 0 after warm-up in all four tasks and a non-zero Δ_scramble on at least one task. Without that, no development run starts.

### 6.4 What stays open for the Codex review

- Is the site-attraction term large enough to anchor, and small enough not to crush the free C4 dynamics? The coefficient is fixed at the C4 A and J, with no new constant. The review should check this on paper, then on the separately approved smoke.
- D4's 40 s connectivity timer, and the cost of computing the path (a breadth-first search over the k ≤ 8 neighbour graph at each growth check, which is cheap).
- Whether B-path's midpoint phase, as a circular mean, makes the bridge trivially echo the site. The scramble intervention measures that; it does not prevent it.
- Every new rule gets the same logging, replay and accounting as B1, D1 and D3.
