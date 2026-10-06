# Design 0h, revision 7: phase on the task's clock, pinned ends (after the revision-6.5 fixture failure)

**Status:** drafted by Claude for Codex review. Not approved, and no execution is authorized. **The base is revision 6.5** (`DESIGN_0H_REV6.md`, with every section through 19.9). Every rule not changed below stays as written there. This is a new revision on **fresh entropy**: every key prefix `0h-rev6/` becomes `0h-rev7/`, and every world-id range moves up by 10,000,000.

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
