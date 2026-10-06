# Design 0h, revision 7.6: phase on the task's clock, pinned ends (after the revision-6.5 fixture failure)

**Status:** revision 7.6 (section 13: the output port protected, after the 7.5 F5 failure; under review). Revision 7.5 (section 12) was approved with notes. Revision 7.4 (section 11) was approved with notes. Revision 7.3 was design-approved by the Codex round-4 review (APPROVE_WITH_NOTES; its three low notes applied in 10.6). This is design review only: integration and execution readiness are separate gates. **Section 8 answers the Codex review** `docs/reviews/tactical_0h_rev7_design_review_codex.md` (R7-1 … R7-12) **and governs over sections 1–7. Section 9 (revision 7.2) answers the round-2 review `…_codex_r2.md` (R2-1 … R2-7) and governs over everything before it. Section 10 (revision 7.3) answers round 3 (`…_codex_r3.md`, R3-1 … R3-4) and governs over everything before it.** Drafted by Claude for Codex review. Not approved, and no execution is authorized. **The base is revision 6.5** (`DESIGN_0H_REV6.md`, with every section through 19.9). Every rule not changed below stays as written there. This is a new revision on **fresh entropy**: every key prefix `0h-rev6/` becomes `0h-rev7/`, and every world-id range moves up by 10,000,000.

## 1. What the 6.5 fixtures showed (`growing_shapes/runner/REV6_FIXTURE_REPORT.md`, decision 0030)

| Fixture | Result | Reading |
|---|---|---|
| F1a, one link | PASS; the output follows the input step after 4.6 s | Transmission works |
| F1b, a dense 3-link scaffold | **FAIL**; the path stays present 100% of the time, but the output enters tolerance only **15.4 s** after the step (the deadline is 8 s) and then locks exactly | **Too slow, not broken** |
| F1c, a long chain (descriptive) | Never within tolerance; the chain **compacts toward the origin** (the output radius goes from 1.80 to 0.03 m.u.) | The C4 aggregation predicted in `docs/reviews/external_web_ai_rev6_recommended_design_assessment.md` |
| F2–F4 | PASS, exactly | The mask, lesions and native/Python parity are correct |

**The diagnosis is a timescale mismatch** (the owner's own-level-time principle):
- C4 phase coupling, K · exp(−r²) · sin Δθ averaged over neighbours with K = 1, propagates a phase change like slow diffusion: about 5–15 s per few links.
- The task's input intervals are 4 s (the memory cue) and 16 s (an episode), with decisions every 0.1 s.
- A standalone toy model of F1b, positions fixed (`growing_shapes_review_claude/rev7_toy/f1b_toy.py`, a standalone script, not project code), gives the first continuous entry after the step at:

| Phase-rate scale λ | First continuous entry after the step |
|---|---|
| 1 | 23 s |
| 2 | 11.5 s |
| 4 | 5.8 s |
| 8 | **2.9 s** (error 0.009 rad at 16 s) |

## 2. Change 1: the phase-rate scale λ = 8 (the timescale ledger)

**The rule:** the medium's **phase** dynamics run on the task's clock. Its **geometry** stays on its own, slower clock.
- The internal phase coupling and the site drive are both multiplied by λ, so the drive-to-coupling balance at a source is unchanged:

      dθ_i/dt = ω_i + λ · [ K · mean_j w(r_ij) sin(θ_j − θ_i) + g_i Σ_s k_s K_d(|x_i − q_s|) sin(ψ_s − θ_i) ]

- ω (the carrier band π), motion (A, B, J), adaptation rates and all timers are **unchanged**. The geometry level stays slow; that separation of levels is intended.
- **How λ is derived:** the shortest task interval carrying input is the 4 s visible cue. A dense 3-link path must settle within **half** of it (2 s), leaving the other half for the output to be read.
  - The toy model gives 2.9 s at λ = 8 for the 8 s-deadline criterion, and about 2.9 s settling from the step.
  - λ = 8 is the smallest power of two meeting the F1 criterion with margin.
  - It is **frozen now, before any revision-7 run**. F1 re-tests it on the real engine.
- **Units:** λ is dimensionless. It rescales the time constant of the phase level relative to world time.
- **What it is not:** a tuned task parameter. It is chosen from the clock ledger and a fixture, never from a task score.

## 3. Change 2: pinned ends (anchoring; answers the F1c compaction)

**The output oscillator is pinned** at the origin: its position is fixed, and it still takes part in coupling as a receiver and a sender.
- A designated port has a fixed place, as in oscillatory-network read-outs.
- B-out places the output exactly at the origin (the first clear point of the 6.5 spiral, if the origin is occupied).

**Sensor sites become pinned bodies in the motion law only.**
- Each active site s is treated as a fixed-position neighbour in every element's C4 **motion** term: the same pair law A(1 + J cos(ψ_s − θ_i)) − B/r, with the site's drive phase ψ_s.
- It is counted in the same k ≤ 8 nearest list (r < 3) and the same mean normalization as element neighbours.
- It has **no** phase-coupling term; drive stays the site's only phase channel.
- **Units are those of the C4 pair law,** because a site enters exactly as an element neighbour would. This answers the revision-6 review C4 objection, which concerned a one-way term with no repulsion and a different normalization.
- **Related work:** pinned swarmalators (Sar, Ghosh and O'Keeffe, 2023). Labelled as a **new engineering hypothesis**; no accepted C4 evidence transfers to it.

**Effect:** a chain between a pinned site and the pinned output is held between fixed ends, like a string between two pins. The aggregation that collapsed F1c now pulls toward the ends instead of to an unanchored centroid. Whether this holds is tested by F1c, which becomes a gate (section 5).

## 4. Change 3: the deferred ideas from the owner's external design (adopted now)

- **Demand timers freeze rather than reset while a site is inactive** (B1 and B-path). The external recheck's A01 and the external design's §4: a 4 s memory cue can now accumulate demand across cues.
- **An empty start.** The intact medium starts with no elements, so every element traces to a demand event: B1, B-out or B-path. F5(i) uses the empty start; F5(ii) keeps its literal hand-built start.

## 5. Fixtures (6.5's F1–F9, with these changes)

- **F1 positions:** F1a and F1b as in 6.5, but with O **pinned** and the site acting as a pinned body.
- **F1c becomes a gate:**
  - the output angle within 0.3 rad at every step from its first entry through **t = 24 s**;
  - the directed path present in ≥ 80% of 160 s;
  - the final radius of O exactly 0 (pinned).
- **New F1d (descriptive): λ = 1 vs λ = 8 on F1b,** with the same scaffold. It documents the timescale effect on the real engine.
- **F5(i)** starts empty.
- All other criteria and the stop rows are as in 6.5.

## 6. What does not change

Everything else of 6.5 is unchanged:
- the mask and the role table;
- the directed graph and B-path's post-trial acceptance;
- D4;
- the wall (still applies; it is not expected to bind);
- controls M and U;
- G0, G0', G2 and their estimators;
- the 19.x comparators, baselines and ceilings;
- the identity scope;
- the evidence rules.

## 7. Self-audit

| Item | Cause in 6.5 | Fix |
|---|---|---|
| F1b too slow | Kept the inherited K = 1 without a clock ledger for the phase level | λ from the cue clock (section 2) |
| F1c compaction | Relied on D4 and a wall; neither anchors an aggregating law | Pinned ends (section 3) |
| Memory demand | Reset-on-inactivity timers | Freeze (section 4) |
| Attribution | A random initial scaffold | Empty start (section 4) |

## 8. Revision 7.1 amendments (each replaces or completes the named clause)

### 8.1 How λ is chosen (replaces the derivation in section 2; R7-1, R7-2)

**The rule:** λ is the smallest power of two for which the dense 3-link scaffold settles within **half the inherited F1 deadline (4 s)** after the input step. Settling means the first entry into the 0.3 rad tolerance, held to the end. The case is zero detuning, positions fixed, and the toy's initial phases (all 0).

| λ | Delay (s) | Meets 4 s? |
|---|---|---|
| 4 | 5.76 | no |
| 8 | **2.88** | **yes** |

So **λ = 8**. The section-2 "2 s" claim is **withdrawn**.

**What λ is:** fixture-calibrated engineering. It is chosen from the task's timing, never from a task score. The real F1 tests it on the engine.

**What λ does** (stated, not hidden):
- **Fixed geometry, ω = π:** it is a pure time dilation of the relative phases.
- **With detuning:** the locking range widens to |ω_i − π| ≤ λa, and locked offsets shrink by 1/λ.
- **With moving geometry, adaptation or changing input:** it is not a rescaling of the whole system.

The carrier ω_D = π stays unscaled, as do the demodulator and the task clock.

**The diagnosis is labelled as supported hypotheses:** a slow phase clock (the F1b delay) plus loss of drive access through compaction (F1c had 1,117 element-seconds without sensor access). Neither alone is claimed as the cause.

**F1d** (descriptive): F1b's pinned scaffold at λ = 1 and λ = 8, reporting delays, deadline errors, effective-root and drive exposure, and topology and geometry histories.

### 8.2 Pin coordinates (replaces section 3's pin sentences and section 5's F1 positions; R7-3)

| Case | O's pin | Note |
|---|---|---|
| Live runs (training and controls) | **(0, 0)** | B-out reserves the origin: if any element is within 0.05 of it, the birth is refused `placement` and retried at the next check. It is never relocated. |
| F1a | (2.644, 0), the inherited literal | A local response fixture; exempt from the origin rule |
| F1b | (1.532, 0), the inherited literal | Exempt, as F1a |
| **F1c (new layout)** | **(0, 0)** | S at (3.2, 0); 5 intermediates at x = 3.2 − 0.556·m (m = 1 … 5; the last at 0.42); g = 0; **no initial S → O edge (|S − O| = 3.2 > 3)** |
| F1d | as F1b | — |
| F2, F3 | the 6.5 literals | O pinned there |
| F5(ii) | (−0.5, 0), the 6.5 literal | An explicit exception: it keeps the route missing at the start |
| Copies and evaluation | the stored coordinate | Checked against the stored value, never against a universal radius |

### 8.3 Two neighbour lists (replaces section 3's "same list" sentence; R7-4)

- **N_i^x (motion):** the k ≤ 8 nearest among **elements plus active pinned sites**, strict r < 3, with its own mean count.
  - Ties are broken by distance, then type (elements before sites), then id.
  - Held for all four RK4 stages. ψ_s is advanced on the carrier at each stage.
- **N_i^θ (phase):** the k ≤ 8 nearest **elements only**, strict r < 3, with its own count. It is the **existing** phase list and influence graph.
  - Graph reach, lock eligibility, PLV histories, B-path trials and the cost all use N^θ.
- **Sites are external boundary bodies.** They are excluded from N (the element count), the budget, templates, qualification cohorts and the element-pair cost. Their motion interactions are reported.
- **The edge cases:**
  - An empty N^x gives no motion; an empty N^θ gives no coupling.
  - A silent or lesioned element keeps its N^x role.
  - An inactive site (k_s = 0) is absent from N^x.

### 8.4 Births clear of the sensor bodies (amends placement; R7-5)

- **Every placement must be ≥ 0.3 m.u. from every physical sensor location (all 8, active or not)** and ≥ 0.05 from every element. This applies to B1, B-out, B-path trials, M, U and recovery kicks.
  - For B1, that means the first admissible point of the inherited spiral (j ≥ 3).
  - A refusal keeps the existing codes (`placement`, `exhausted`).
- **The site-body repulsion is regularized** as B / max(r, 0.3), with 0.3 in m.u.
  - This bounds the local stiffness B/r² at about 11 /s before normalization.
  - It applies to site bodies only; element pairs keep C4's ε.

### 8.5 The anchoring claim and the extra input channel (amends section 3; R7-6)

- The "string between pins" sentence is **withdrawn.** Persistence under C4 motion is an **engineering hypothesis**, tested by F1c and F5.
- **A new observation-to-motion channel is disclosed:**
  - Site bodies use ψ_s in the motion cosine, so input reaches geometry even for g = 0 elements.
  - The site bodies are activity-gated (present iff k_s > 0) and unweighted by k_s.
  - G2's claim stays **input-dependent terminal-channel response**: it does not distinguish phase routing from this geometric route.
- **A new descriptive intervention, "site-body off":** the same copy with the site bodies removed from N^x, and the drives kept.

### 8.6 F1c as a gate (replaces section 5's F1c criterion; R7-7)

The layout is that of 8.2: the site steps from 0 to π/2 at t = 8 s, over a 160 s run with free motion of non-pinned members.

**PASS needs all of these:**
1. **Entry:** the first entry into ≤ 0.3 rad by **t = 16 s** (inclusive). No entry means FAIL.
2. **Hold:** ≤ 0.3 rad at every world step from the entry through t = 24 s (inclusive).
3. **Path:** a directed path from an **effective driven root** to O in ≥ 80% of the world steps of the 160 s.
4. **Access:** S within drive reach of the active site in ≥ 80% of the world steps.
5. **Response persistence:** the error is ≤ 0.3 rad in ≥ 80% of the world steps of [16, 160] s.

**Recorded:** source–site distances, the span and radius of ordinary nodes, the minimum distances, shortcuts and link weights.

**The pin-invariance check** (O at exactly (0, 0) throughout) is an implementation check, not an endpoint.

**Stop rows added:** F1c FAIL blocks F5. An F1c measurement failure is INVALID. F1d is descriptive.

### 8.7 Numerical qualification (new fixture N1; R7-8)

**The cases** (h = 0.02 against h = 0.005, the same declared states):
- high gain: k = 4, g = 2, one site;
- detuning: ω = π ± 0.5π;
- conflicting inputs: two sites in antiphase;
- near-pin: an element at r = 0.3 from a site body;
- the F1b scaffold.

**PASS:** the maximum absolute difference of the demodulated phases is ≤ 0.01 rad over 16 s; entry times differ by ≤ 0.1 s; topology is identical in ≥ 99% of the world steps; and the pins are invariant.

**Estimator validity:** the integrator stores the **unwrapped** per-substep relative increment |Δ(θ − πt)| for every element.
- If any increment exceeds π/2 within a world step, that frame is flagged `fast_transient`.
- The flag counts are reported, and qualification windows containing them are marked not-qualified. They are never silently used.
- **N1 failure blocks every other fixture.**

### 8.8 Clocks, adaptation and a constrained recovery adapter (R7-9)

**The ledger of clocks:**

| Clock | Value | Status |
|---|---|---|
| Phase relaxation | ×λ | sped up |
| Geometry (A, B, J) | — | unchanged |
| Carrier | π | unchanged |
| ω̂ estimator | 10 s | unchanged |
| Adaptation | η = 0.05 /s | unchanged |
| Qualification | 60 s window; 0.005 rad/s and 0.1 rad cuts | unchanged |

The 10 s and 60 s windows and their cuts are kept as **fixed engineering admission rules for new driven, anchored snapshots**. The dimensionless ratios that change (λKw against the geometric and carrier rates) are reported. No horizon is divided by λ.

**The recovery adapter `rev7_qual_v1`:**
- Pinned elements keep identical positions in both futures, at every stage.
- **Position kicks act on free members only.** The RMS denominator is the free members. The achieved kick is recorded.
- Phase kicks may include O.
- A candidate with no free member is **skipped** (`no_free_member`), not qualified.
- Pinned elements and sites are never cohort members.
- Roles and pins are preserved in every live, frozen, recovery and extracted copy. Every mode uses the revision-7 RHS.
- Frozen C4 functions stay unedited (new adapter files only).

### 8.9 Demand timers and the empty start (replaces section 4's timer sentence; R7-10)

**The B1 timer per site:**
- active and uncovered: + dt_w;
- active and covered: reset to 0;
- an accepted birth: reset to 0;
- **inactive: frozen** (unchanged);
- a quota or resource refusal: retained.

**A ready site** (timer ≥ 20 s) **requests a birth only at a growth check where it is active.** Inactive ready sites wait for a visible input, which supplies the phase. Queued demand is reported apart from attempts.

**B-path keeps its immediate rule.** It had no timer, and "B-path" is **removed** from the freeze amendment.

**Memory:** freezing lets demand accumulate across cues, but **P_i and e_i stay undefined** within established memory blocks. The 80/100 eligibility is unchanged, F8 is unchanged, and the memory row stays descriptive.

**The empty start** applies to intact, M and U: t = 0, empty histories and timers, an id counter at 0, and the first growth check at t = 20 s. Newborns have ω = π, and there is no initial detuning draw. F5(ii) keeps its literal table (8.2).

**Required checks:**
- a threshold reached during a cue, with the check during the hidden interval: the birth is deferred;
- activity resuming;
- a refusal retaining the timer.

### 8.10 The instantiated revision-7 inventory (replaces section 0's blanket shift; R7-11)

**Seeds:** every master key prefix `0h-rev6/` becomes `0h-rev7/`. Byte order and the recovery sub-derivation are as in 6.4, section 18.2. The donor ranks use `0h-rev7/donor_perm/` + j.

| Use | Namespace | Ids |
|---|---|---|
| Training, slot k | dev | 11,000,000 + 10,000·k + e |
| Evaluation recipients | validation | 10,000,512–10,000,639 |
| Evaluation donors | validation | 10,000,640–10,000,767 |
| F5 assay recipients and donors | validation | 10,000,768–10,000,787 |
| F6 | validation | 10,000,788–10,000,807 |
| F5 growth | dev | 12,000,000 + e |
| F8 | dev | 12,100,000 + e |
| **Calibration (reused and labelled, unchanged)** | validation | 0–255 |
| Historical 5.1 reference | dev | 0–1999 (unchanged) |

- Disjointness from every earlier inventory is checked before execution.
- The F1, F2, F3 and N1 scaffolds are deterministic and have no entropy. This is reported honestly; they are not "fresh-seed" evidence.
- The complete inventory is instantiated and hashed before any result.

### 8.11 Versions and identity (replaces section 6's "identity scope unchanged"; R7-12)

**New versions:**
- `rev7_rhs_v1`;
- `rev7_eval_v1`;
- `rev7_template_v1`: the role, plus a **pin flag and pin coordinate** per member;
- `rev7_qual_v1`.

**The configuration identity binds:** λ, the N^x/N^θ policy, the pin table, site-body regularization, placement clearances, the timer and start rules, and the N1 tolerances.

**The execution-start pin includes:** DESIGN_0H_REV7.md, DESIGN_0H_REV6.md, DESIGN_0H.md, the revision-7 sources and native images, the reused calibration, and the instantiated seed inventory.

**Legacy loading:**
- revision-5.1 and 6.5 templates load under their own versions, with no migration;
- revision-7 code lives in new files.

**The stop table gains a revision-7 readiness row:** if the revision-7 integration is not implemented, tested and reviewed, no fixture runs. **Decision 0030 does not cover revision 7.** Under decision 0031, the revision-7 fixtures (under 1 hour) need no separate approval once this design passes review and the integration is reviewed.

### 8.12 Self-audit (Codex revision-7 review)

| # | Disposition | Cause |
|---|---|---|
| R7-1 | 8.1: the rule restated, so λ = 8 follows from it; the 2 s claim is withdrawn | Mixed two deadlines |
| R7-2 | 8.1: locking consequences; the diagnosis labelled as hypotheses; F1d outputs defined | Overstated the cause |
| R7-3 | 8.2: a pin table; a new F1c layout | Contradictory pin sentences |
| R7-4 | 8.3: separate motion and phase lists | Left the topology implicit |
| R7-5 | 8.4: a 0.3 m.u. clearance from site bodies; regularization | Missed coincident births |
| R7-6 | 8.5: the claim withdrawn; the channel disclosed; the site-body-off intervention | Overclaimed |
| R7-7 | 8.6: a complete gate | A tautological criterion |
| R7-8 | 8.7: N1 and the transient flags | Relied on carrier sampling |
| R7-9 | 8.8: a clock ledger; the constrained recovery adapter | Missed pin and kick conflicts |
| R7-10 | 8.9: an exact recurrence; B-path removed; the memory limit kept | Under-specified |
| R7-11 | 8.10: an instantiated inventory | A blanket shift |
| R7-12 | 8.11: versions and an identity pin | Assumed the 6.5 identity sufficed |

## 9. Revision 7.2 amendments (governs over sections 1–8)

### 9.1 A frame excursion bound (replaces 8.7's transient flag; R2-1)

**The bound:**
- For every element i and every 0.1 s world frame: **E_i = Σ over the 5 substeps of h · max over the 4 RK4 stages of |θ̇_i − π|**, where h = 0.02 s and θ̇_i is evaluated at each stage.
- E_i bounds |Δ(θ_i − πt)| over the frame, under the RK4 stage-sampling assumption. The limitation (excursions between stage evaluations) is stated, not hidden.
- **For a pair (i, j), the bound is E_i + E_j.**

**A frame is flagged `fast_transient`** if E_i > π/2 for any element, or if E_i + E_j > π/2 for any pair of the current candidate or cohort.

**The disposition:**
- In a flagged frame, the flagged elements' samples are **treated as missing** for the 10 s PLV, gain, coverage and lock estimators. This reduces their active-sample counts under the inherited rules.
- **A qualification window containing any flagged frame of its cohort is not-qualified.**
- The screen is a **conservative warning bound**, sufficient only under the stage assumption. Its counts are reported per run.

### 9.2 N1, frozen (replaces 8.7's case list; R2-2)

**Common settings:**
- The clock runs 0 → 16 s, with growth, adaptation and deaths off and λ = 8.
- Motion is on for non-pinned members, using the full revision-7 RHS.
- Runs at h = 0.02 and h = 0.005 are compared at every world endpoint (each 0.1 s).

| Case | Sites (position, k, α) | Members (id: position, θ₀, ω, g, role) | Entry metric |
|---|---|---|---|
| N1a, high gain | (4, 0), k = 4, α = 0, then π/2 at t = 8 | 0: (3.2, 0), 0, π, 2, element | defined: tolerance 0.3 to α after t = 8 |
| N1b, detuned | (4, 0), k = 2, α = 0 constant | 0: (3.2, 0), 0, 1.5π, 1, element | not applicable (declared) |
| N1c, conflict | (4, 0), k = 2, α = 0; and (2.828, 2.828), k = 2, α = π | 0: (3.0, 1.3), 0, π, 1, element | not applicable |
| N1d, near the site body | (4, 0), k = 2, α = 0 | 0: (3.7, 0), θ₀ = π (antiphase, the strongest repulsion), π, 1, element; 1: (3.956, 0), 0, π, 1, element (inside the cutoff) | not applicable |
| N1e, scaffold | as F1b (8.2) | as F1b | defined: as F1b |

**The comparisons:**
- **Phase:** the maximum over endpoints of |wrap((θ − πt) at h = 0.02 minus the same at h = 0.005)| must be ≤ 0.01 rad, for every member.
- **Entry** (where defined): both runs enter → the times must differ by ≤ 0.1 s; neither enters → pass for that metric; only one enters → **FAIL**.
- **Topology:** the fractions of endpoints with identical N^x lists and identical N^θ lists are reported **separately**, and each must be ≥ 99%.
- **Pins** must be invariant.

The recipes are hashed with the configuration identity.

### 9.3 The output belongs to its snapshot (replaces 8.8's cohort exclusion; R2-3)

- **External sites are excluded from cohorts. The pinned output O may be a candidate member,** so G1c and G5 keep meaning.
- **Position kicks** act on the candidate's **free** members, with the RMS over that set.
- **Phase kicks** act on **all** candidate members, O included.
- O stays fixed in both futures, at every stage.
- An extracted snapshot keeps O's role and pin.

### 9.4 The site-body vector law (replaces 8.4's regularization; R2-4)

With r = |q_s − x_i| and r₀ = 0.3 m.u.:

    v_site(i, s) = [A(1 + J cos(ψ_s − θ_i)) − B / max(r, r₀)] · (q_s − x_i) / max(r, r₀)

- **At r = 0** the vector is 0, because the displacement is 0.
- **Bounds:** for r ≤ r₀ the term is linear in the displacement, and its Jacobian norm is ≤ (A(1 + J) + B/r₀)/r₀ ≈ 17 /s, before the N^x mean.
- **Status:** a **new engineering law**, qualified by N1d. It is not inherited C4. The C4 element-pair code is unchanged.

**Changed starts:**
- **F5(ii)'s hexagon is recentred at (3.1, 0).** That gives a clearance of 0.344 from site 0 and a nearest-O distance of 3.044, so the route stays initially missing. This is a new fixture table.
- **The F4 parity scaffold's element at the site moves to (3.7, 0),** 0.3 from it.

Motion inside the cutoff is tested by N1d. Birth clearance (8.4) is a placement rule, not an invariant of motion.

### 9.5 Admissible recovery kicks (completes 8.8; R2-5)

- **Position kicks:** a Gaussian draw from the kick generator, normalized to the inherited RMS (0.1 × the median spacing of the candidate's free members). It is **admissible** if every moved destination is ≥ 0.05 m.u. from every other element and ≥ r₀ from every physical site.
  - Otherwise the draw is repeated, **up to 8 draws**, in fixed RNG order.
  - If none is admissible, the candidate is skipped as `inadmissible_kick`.
  - **No clipping.** The achieved RMS equals the requested RMS, and both are recorded.
- **Phase kicks** keep the inherited RMS (0.3 rad) over all candidate members.
- **Reported:** skip counts with their denominators; and absolute and anchor-relative displacement, beside the inherited centroid-relative relaxation.

### 9.6 Locking, exactly (corrects 8.1; R2-6)

For one fixed oscillator driven with unscaled amplitude a and detuning δ = ω − π, the stable locked offset satisfies sin(β − α) = δ/(λa): β − α = arcsin(δ/(λa)), for |δ| < λa. The boundary is marginal.
- "Shrinks by 1/λ" is the small-offset approximation.
- Networks with conflicting drives have no such sufficient condition.

### 9.7 The governing revision-7 stop table (replaces the scattered rows; R2-7)

| Yes/no question | Yes → one action | Role |
|---|---|---|
| Is the revision-7 integration not implemented, tested and reviewed? | Block all execution | implementer |
| Is a source identity, configuration or inventory pin missing or mismatched at execution start? | Block execution | implementer |
| Does N1 FAIL, or is it INVALID? | Block F1 and every later fixture | implementer |
| Does F1a, F1b, F1c or F2–F4 FAIL? | Block F5 and development; report | implementer |
| Did a fixture measurement fail (crash, non-finite value, missing record)? | Report INVALID; block the next stage | implementer |
| Does F5 or F7 FAIL? | Block development; write the failure report | drafter |
| Has any protocol element changed after results were seen? | Draft a new revision with fresh entropy | drafter |
| Is the development run longer than 1 hour and due to start before 22:00? | Ask the owner (decision 0031) | implementer |
| Has development stopped, and is a next step needed? | Ask the owner | owner |

**The execution basis:**
- fixtures under 1 hour run under decision 0031 once this design passes review and the integration review passes;
- a formal milestone would still need AGENTS.md registration and the gated pipeline;
- decision 0030 covered only the 6.5 fixture run.

### 9.8 Self-audit (round 2)

| # | Disposition | Cause |
|---|---|---|
| R2-1 | 9.1: a frame excursion bound with pairs; flagged frames treated as missing | A per-substep test was too local |
| R2-2 | 9.2: a frozen N1 table and comparison rules | Named cases without states |
| R2-3 | 9.3: O may be a candidate member | Over-broad exclusion |
| R2-4 | 9.4: the full vector law; F5(ii) recentred; the F4 element moved | A scalar-only clamp |
| R2-5 | 9.5: admissibility with up to 8 redraws, no clipping | No refusal policy |
| R2-6 | 9.6: the exact arcsine law | Stated an approximation as exact |
| R2-7 | 9.7: one stop table | Scattered prose |

## 10. Revision 7.3 amendments (governs over sections 1–9)

### 10.1 The complete stop table (9.7 plus these restored rows; R3-1)

**9.7 stays, and these inherited rows are restored to it:**

| Yes/no question | Yes → one action | Role |
|---|---|---|
| Is the world, `remember_static` or the medium's revision-7 dependency integration missing, NOT_READY or unreviewed? | Block all execution | implementer |
| Is a development read-out INVALID (a non-finite value, zero usable tasks, an incomplete or interrupted run)? | Report INVALID with the raw evidence; never reinterpret it as PASS or FAIL | implementer |
| Is perceive not usable under the frozen usable-task rule? | Block G2 and G0; do not substitute another primary task | implementer |
| Does a **development** seed have any unmatched control-M birth? | That seed is G0-INCONCLUSIVE. It is kept and never replaced. This is separate from F7's fixture gate. | implementer |
| Does G1 FAIL in the task-blind arm? | Write the failure report; stop development | drafter |
| Does G0' FAIL? | Write the failure report; stop development | drafter |
| Is G2 FAIL or INCONCLUSIVE? | Write the failure or diagnosis report; stop development | drafter |

The stricter revision-7 rule, that an F7 FAIL blocks development, stays as a deliberate policy.

### 10.2 The validity masks (completes 9.1; R3-2)

Consecutive timestamped records and every E_i are kept. Three validity rules apply:
- **Individual sample** (element i, frame k): **invalid** if E_i > π/2.
- **Element pair** (i, j, frame k): **invalid** if E_i + E_j > π/2. The policy is **pair-only**: it invalidates that pair's observation, not the two individual samples.
- **Site pair** (i, s, frame k): **invalid** if E_i > π/2. The site's phase is known exactly, from the carrier and the held angle.

**Scope:** every pair actually used by a live estimator (lock and PLV for D1, sensor PLV for P_i and coverage), whatever its qualification membership.

**The inherited counts:**
- **Records stay consecutive.** Invalid observations count as **inactive** for that pair: they are excluded from the PLV sum and its denominator.
- The unchanged 80-of-100 active requirement then counts **valid active** observations.
- The 100/101-record history prerequisite counts records, which are never dropped.

**P_i** is undefined in a frame whose own sample is invalid: g is unchanged that step (the inherited no-drive rule).

**ω̂** keeps using unwrapped endpoints, which retain whole-turn information; their numerical accuracy is subject to N1. It is suspended (ω unchanged) only if an endpoint sample is itself invalid.

**Qualification:** the saved bounds are evaluated on the actual cohort's pairs before any circular criterion. A window with any invalid cohort pair is not-qualified. The stage-sampling limitation is stated.

### 10.3 N1 also compares positions and unwrapped phases (completes 9.2; R3-3)

These are added to N1's PASS conditions (new engineering admission; not inherited C4 evidence):
- **free-member positions:** the maximum matched-endpoint Euclidean difference between h = 0.02 and h = 0.005 is ≤ 0.01 m.u.;
- **unwrapped carrier-relative phases:** the maximum |(θ − πt) at h = 0.02 minus the same at h = 0.005|, unwrapped, is ≤ 0.01 rad. This complements the wrapped comparison;
- **recorded in both integrations:** the minimum element–element and element–site distances.

The definitions are hashed with the N1 recipes.

### 10.4 Where the site-body-off comparator runs (completes 8.5; R3-4)

- It runs on fresh paired copies of the **final whole medium** of each intact training, on the revision-7 **perceive** recipient panel (validation 10,000,512–10,000,639), with the same carrier and decoder as intact.
- Only the sites are removed from N^x; drives and element motion are kept.
- It is reported descriptively, as paired differences beside G2, with no verdict cut.
- Its 128 episodes per training are included in A7's cost projection.

### 10.5 Self-audit (round 3)

| # | Disposition | Cause |
|---|---|---|
| R3-1 | 10.1: the inherited development and INVALID rows restored | A "replacement" table dropped rows |
| R3-2 | 10.2: three validity rules, pair-only, consecutive records kept | Under-specified the mask |
| R3-3 | 10.3: position and unwrapped comparisons | Checked only phases and topology |
| R3-4 | 10.4: the panel, copies and cost of the new comparator | Left the scope open |

### 10.6 Codex round-4 low notes (applied)

- **R4-1:** the status line now says revision 7.3. Design approval is recorded separately from integration and execution readiness. Any execution-start pin uses the hash of the final committed design.
- **R4-2:** unwrapped endpoints are described as retaining whole-turn information, with their accuracy subject to N1. They are not "exact".
- **R4-3:** site-body-off **recomputes N^x** under the existing nearest-neighbour and mean rules. It is labelled the **total effect of removing the site bodies**, including normalization and neighbour-selection changes. The N^x count changes are reported with the paired differences. It stays descriptive.

## 11. Revision 7.4: λ chosen on the live-geometry scaffold (an outcome-informed change; disclosed)

**What the 7.3 fixtures showed** (`growing_shapes/runner/REV7_FIXTURE_REPORT.md`; decision 0031; pin `3b6cf563…`):

| Fixture | Result |
|---|---|
| N1 | PASS (every difference ≤ 0.0017) |
| F1a | PASS, 0.6 s delay |
| F1b | PASS, 2.5 s delay (it was 15.4 s in 6.5) |
| F2–F4 | PASS |
| F1d | λ = 1 never settles by 16 s; λ = 8 settles in 2.5 s |
| **F1c** | **FAIL by a hair:** the first entry is at **16.1 s** against the 16 s deadline (error 0.306 rad against 0.3). After that the response holds 99.9% of [16, 160], with path and access 100% and **no collapse** (the pins work). |

**The reading:**
- F1c is the **live geometry**: the source at the sensor, O pinned at the origin, 6 links.
- λ was chosen on F1b, the 3-link scaffold. Phase transmission through the mean C4 coupling is diffusion-like, so longer paths need more speed.
- **The rule of 8.1 is applied to the scaffold that matches the live layout.** That rule: the smallest power of two that settles within half the 8 s deadline, so within 4 s.
- F1c's measured engine delay at λ = 8 is 8.1 s. Delay scales close to 1/λ at fixed geometry: F1d's 23 s → 2.5 s matches it, and so does the toy `rev7_toy/f1c_toy.py`.
  - **λ = 16** predicts about 4.05 s (at the 4 s rule's boundary).
  - **λ = 32** predicts about 2.0 s.
- The fixed-position toy is slower (13.1 s at λ = 8, 6.5 s at 16, 3.3 s at 32), because it lacks the chain's shortening under motion.

**The change:**
- **λ = 32**, the smallest power of two that meets the 4 s rule with margin on both the engine extrapolation and the toy.
- **The integration step is reduced to h = 0.005 s** (20 RK4 substeps per world step) for numerical safety. The conservative high-gain stiffness bound is 32 · 2 · 4 = 256 /s, and 256 × 0.005 = 1.28, well inside RK4's real-axis stability limit of about 2.8.
- **N1's refinement comparison** becomes h = 0.005 against h = 0.00125, with the same tolerances.
- **The frame excursion bound E_i** sums over 20 substeps.

**Unchanged:**
- every F1 criterion (no deadline is relaxed);
- the carrier;
- motion (whose geometric clock stays as it was; at h = 0.005 it is integrated more finely, never faster);
- every other rule.

**Disclosure:**
- This is an **outcome-informed revision**. It is made after seeing F1c's 0.1 s miss, and the 7.3 FAIL is kept as recorded.
- The F1 scaffolds are deterministic (they have no entropy). Their re-run under 7.4 is new engineering evidence about a changed λ and h. It is not an independent replication of 7.3.
- F5 and later fixtures consumed no entropy under 7.3 (they were never run). Their revision-7 inventory stays valid, re-pinned under 7.4's configuration identity.
- **Cost:** h = 0.005 makes integration about 4× slower. The F5 fixture cost and the development projection (A7) are re-estimated from the 7.4 fixture timings.
- **Version:** `rev7_rhs_v1` with configuration λ = 32 and h = 0.005. The configuration identity changes, so the pin changes.

| Item | Cause |
|---|---|
| λ = 8 was too slow for the live geometry | λ was derived on a shorter scaffold than the live path |

### 11.1 Codex 7.4 review notes (APPROVE_WITH_NOTES; all six applied)

- **R74-1, the toy and the engine:**
  - λ = 32 is the smallest power of two meeting the 4 s rule on the **fixed-position toy**. It is a **provisional candidate** for the mobile engine.
  - **F1d** compares λ = 1, 8 and 32 on F1b, all at h = 0.005, with identical starts and input, and the same outputs as before.
  - **F1c** additionally reports its sustained entry delay, its error at t = 12 s (the 4 s margin), and whether that margin is met. **The existing 8 s gate and every hold and persistence cut are unchanged.** A missed 4 s margin is reported, never gated.
- **R74-2, the stiffness bound:** 256 /s is the **one-site maximum drive-derivative scale**.
  - The phase-only Jacobian row bound is λ(2C_i + D_i). It is 320 /s in the one-site envelope (h · 320 = 1.6, inside RK4's negative-real interval of about 2.785).
  - It is not a guarantee of full coupled phase–position stability. **Stability is not accuracy:** N1 checks accuracy.
- **R74-3, N1 completed:** every N1 case runs at λ = 32, with 20 and 80 substeps per world step (h = 0.005 and h = 0.00125), and E_i accumulated with each run's own h.
  - **New case N1f:** the deterministic F1c state, compared through t = 24 s, including entry and the hold, with the same tolerances.
  - The individual and used-pair invalid-frame counts, and their coarse/fine disagreements, are reported.
  - π/2, the 80-of-100 rule, consecutive records and window rejection are unchanged.
- **R74-4, the wording corrected:**
  - The toy's 23.04 → 2.88 s is reported separately from the engine's F1d: λ = 1 is censored at the deadline; λ = 8 takes 2.5 s.
  - F1c is a hand-built mobile scaffold with the live pin layout; its source is 0.8 m.u. from its site, over 6 adjacent intervals, and it can gain shortcuts.
  - "No collapse" is narrowed to: the output pin, the path and access were preserved, despite substantial compaction of ordinary members (span 2.78 → 1.17).
- **R74-5, the clocks in the handoff:**
  - Adaptation, gain, reward and structural updates happen once per world step (or at their inherited checks), **never once per substep**. No horizon or threshold is divided.
  - Positions and phases are integrated together at h = 0.005 in every mode: live, evaluation copies, controls, recovery futures and parity. The carrier advances at each stage.
  - N^x and N^θ are recomputed per substep and held for its 4 stages.
  - Changed valid-window denominators and transient exclusions are reported.
  - The configuration and artifact identities distinguish λ = 32 and h = 0.005 under `rev7_rhs_v1`.
- **R74-6, cost:** "4×" is a nominal ratio of right-hand-side work per substep, not a runtime multiplier. The fixture and A7 costs are re-measured from the 7.4 run, with unavailable parts null.

## 12. Revision 7.5: N1d starts off the unstable equilibrium (an outcome-informed change; disclosed)

**What the 7.4 fixtures showed** (`growing_shapes/runner/REV74_FIXTURE_REPORT.md`; decision 0031; pin `f370c3b5…`):
- **N1a, b, c, e and f PASS.** Every difference is ≤ 0.0004.
- **N1f, the live 6-link F1c geometry at λ = 32, settles 2.1 s after the step.** The coarse and fine runs agree on entry and on the hold through 24 s. **λ = 32 meets the 4 s margin.**
- **N1d FAILS:** the two step sizes differ by exactly one full turn of unwrapped phase (wrapped 2.18 rad, position 0.081 m.u.). That blocks F1–F9.

**The diagnosis:**
- N1d (9.2) starts member 0 at **θ₀ = π against a site with α = 0**: exact antiphase, the **unstable** equilibrium of the driven oscillator.
- Near it, perturbations grow at about λ g k K_d ≈ 32 · 1 · 2 · 0.96 ≈ 61 /s. A round-off difference of 10⁻¹⁶ between two integrations reaches 1 rad in about ln(10¹⁶)/61 ≈ 0.6 s.
- Which way the phase slips (±2π) is therefore decided by rounding. Two step sizes cannot agree on it, however accurate each is.
- **The case tested sensitivity at a saddle, not accuracy.** The fault is the drafter's recipe, not the integrator: at λ = 8 the same case passed, because the growth rate was 4× smaller.

**The change:**
- **N1d member 0 starts at θ₀ = π − 0.5** (0.5 rad off the saddle; the slip direction is determined). Its position stays (3.7, 0), inside the site-body regime it was meant to test.
- Every other N1d field is unchanged: member 1 at (3.956, 0) with θ₀ = 0, both tolerances, and the other cases.
- **New descriptive case N1g:** the original saddle start (θ₀ = π). It reports the slip direction and time in each integration and records **sensitivity, not accuracy**. It has no gate.

**Disclosure:** this is made after seeing N1d's failure, and the 7.4 FAIL is kept as recorded. N1's fixtures are deterministic, so the re-run is new engineering evidence and not an independent replication.

| Item | Cause |
|---|---|
| N1d started at an unstable equilibrium | The recipe was chosen for "the strongest repulsion" without checking the phase stability of that start |

### 12.1 Codex 7.5 review notes (APPROVE_WITH_NOTES; applied)

- The growth-rate figure (about 61 /s) is an order-of-magnitude estimate for the saddle's instability, not an exact eigenvalue.
- **Coverage:** member 0 at (3.7, 0) sits **at** the r₀ = 0.3 boundary in exact arithmetic, not strictly inside. Member 1 at (3.956, 0), 0.044 from the site, is strictly inside. The case therefore still covers the inside-cutoff law. No tolerance is relaxed.
- **Codex's exact figure** (R75-1): the initial two-member phase Jacobian has an unstable eigenvalue of about **+98 /s**. Round-off of order 10⁻¹⁶ reaches order one in about 0.38 s, which strengthens the diagnosis.
- **The N1g measurement** (R75-3): member 0's first endpoint departure of at least 0.5 rad from its initial unwrapped phase π. The direction is the sign; the time is the first crossing, bracketed by the preceding endpoint. It is an escape diagnostic only.

## 13. Revision 7.6: the output port cannot be deleted (the F5 failure report and fix)

### 13.1 Failure report (the stop row F5_failed: the drafter's duty)

**Run:** `growing_shapes/runner/REV75C_FIXTURE_REPORT.md` (`rev75c_fixture_run_20261006`), the measurement-tool re-run of 7.5 at pin `7a63d150…`.
- **N1 and F1–F4 PASS again.** F1c, the live layout, settles in 2.1 s.
- **F5 FAILS in both starts: A = B = 0, E = 0** at every checkpoint.

**Cause** (from the run's own events and assay records):

| Start | What happened to O |
|---|---|
| (i) | Born by B-out at 20 s. **Killed by D1 at 80 s** (no partners, so L = 0 for 40 s after its 20 s protection). Reborn at 80 s; **killed by D1 at 180 s**. Reborn at 180 s; **removed by D3 at 360 s** (the budget rule removes the lowest-lock elements first). |
| (ii) | The literal start; **removed by D3 at 300 s.** |

- After the output was removed, the budget was full of B1 and B-path elements: the cost reached about 62 against 64.
- B-out was then refused for cost: 23 `cost` terminals in start (i), and 114 B-path requests ended `no_output`.
- **Every assay copy at checkpoints 40–50 had no output** (`has_output: false` in every decision). The assays therefore measured the default action, so A = B = E = 0.
- **F5 never tested transmission through grown paths.** The failure is a design defect: the output port could be deleted, and its re-creation competed with growth for the budget.

**Responsibility:** the drafter. The role table (12.3) protected the output from drive and from root status, but not from D1 and D3, or from the budget.

### 13.2 The change

- **The output port O is exempt from D1, D3 and D4.** O is a pinned, designated port, like the sites. It is never removed by the death rules.
- **O does not count in the cost**, and B-out is **never refused for cap or cost**. N counts the elements other than O, against the cap of 64.
- **B-out still requires the reserved origin to be clear** (`placement`). With O never removed, B-out fires only once in live runs.
- Every other rule is unchanged: D1, D3 and D4 for ordinary elements; B-path and B1; λ = 32; h; every gate.

**Disclosure:** this is an outcome-informed revision, made after the 7.5 F5 result. The 7.5 FAIL is kept as recorded.
- F5 consumes the fixture entropy (`0h-rev7/` keys). The re-run under 7.6 **reuses** that inventory, because no F5 result was valid as a transmission test: the output was absent in every assay.
- This reuse is disclosed. The F5 and F7 seeds are not called fresh.
- The development inventory (training and evaluation) is untouched and still fresh.

| Item | Cause |
|---|---|
| The output port could be deleted, and its re-creation competed for the budget | The role table covered drive and roots, not the death rules or the budget |

### 13.3 Codex 7.6 review notes (APPROVE_WITH_NOTES; applied)

- **R76-1, precision:**
  - The two D1 deletions came after low-lock durations of 50.1 s and 46.6 s; the timers ran during the protection.
  - O did have partners later: its locks were 0.717 and 0.733 at the D3 removals.
  - The peak cost before pruning was 65.8 and 65.0.
  - The role table cited as "12.3" is the measurement-role table of revision 6.5, section 12.3.
- **R76-2, the budget definition (pinned):**
  - O is external infrastructure for the growth budget, but stays a live oscillator and neighbour.
  - **N counts ordinary elements.** The cost's pair term counts **only ordinary-to-ordinary** undirected N^θ pairs; pairs incident to O are excluded, without recomputing neighbour selection.
  - Admission, live accounting and D3 use the same rule. The cap allows 64 ordinary elements plus one O.
  - B-out ignores cap, cost and protected-over-budget, but respects placement and output uniqueness.
  - Physical counts and compute time still include O.
- **R76-3, the claim boundary:**
  - A disconnected, permanent O is allowed. It has no direct drive, is not a root, and creates no path by existing. So F5 still fails max(E) ≥ 0.5 without a real path, and A = 0 for a free-running O.
  - A synthetic isolated-O contract is added. The permanence of O is disclosed as supplied infrastructure.
  - A future PASS supports the registered transmission test, not exclusive mediation by one grown path.
- **R76-4, entropy:** reusing the F5 fixture keys is a **limited, disclosed exception** for outcome-informed engineering fixtures only. It supersedes 9.7's fresh-entropy action for those keys alone.
  - The F5 growth entropy was consumed, and its outcome informed this change.
  - F7's own stream was unconsumed, but its targets depend on the reused F5 run.
  - Neither is called fresh or independent. The development inventory is untouched.
