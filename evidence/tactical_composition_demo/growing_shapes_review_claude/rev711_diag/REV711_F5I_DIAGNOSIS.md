DIAGNOSED: the empty-start failure is caused by the motion law, not by the birth rules or the budget

# Why F5(i) (growth from an empty start) fails: diagnosis after revision 7.11

**Date:** 2026-10-07 (night). **Author:** Claude (claude-opus-5-5), drafter of revisions 7.x.
**Status:** diagnostic and pilot evidence only. No verdict, no fixture result, no pinned file changed.
- The pilots patch behaviour **in-process only**, or run on a **scratch copy**.
- Each one writes its own receipt folder (`growing_shapes/runner/rev711_diag_*`, `rev711_pilot_*`), so the 7.11 fixture receipt is untouched.
- Authority: decision 0031 (runs after 22:00).

**Input:** the 7.11 fixtures (`a52ddbd`): N1 and F1–F4 PASS, F5(ii) PASS (A 1.451, B 1.303, max E 0.8), F5(i) FAIL (A 0.19, B 0.21, E 0).

## 1. What happens in F5(i)

A replay of F5(i) with the fixture keys, recording every 0.1 s world step to t = 480 s (`diag_f5i_link_hold.py`, `trace.json.gz`), shows:

- **Paths do form.** A strong site→O path is closed at **12 growth checks** (220–440 s), each time by a new B-path element. Paths are present in 365 of 4,800 steps.
- **Each path breaks within 0.1–17 s.** In every case the closing element's edge into O stops being strong.
  - O always holds 8 phase neighbours, so the edge needs r ≤ 1.442; that threshold is 32·exp(−r²)/8 = 0.5.
  - The closing element is born 0.95–1.37 from O, then **moves away from O** at 0.3–0.6 m.u./s.
  - It settles 1.5–2.2 m.u. from O. Examples: element 23, 1.30 → 2.20 in 20 s; element 43, 0.95 → 1.49.
- **It is not a phase problem.** From t ≈ 300 s, O is phase-locked with its weighted neighbourhood (0.06–0.5 rad), and each closing element is in phase with O (0.0–0.3 rad).
- **Then the budget runs out** (about 440 s), the closings stop, and the tip settles 1.9–2.4 m.u. from O.

## 2. The mechanism: the motion law makes a one-sided bridge mechanically unstable

The motion law (`medium/rev7_medium.cpp`, the `rhs` loop) gives each element the **mean** pull of its ≤ 8 nearest motion neighbours. A neighbour at distance r with phase difference Δφ contributes, along the unit vector toward it, A(1 + J cos Δφ) − B/r (A = B = 1, J = 0.8). For an in-phase pair that is 1.8 − 1/r: attractive beyond 0.556 m.u., up to the 3 m.u. cutoff.

**Decomposed from the recorded state, for three closing elements at the step after birth:**

| Element, time | Distance to O | Pull toward O by O | Pull from the 7 other neighbours (all behind, in phase) | Net velocity toward O |
|---|---:|---:|---:|---:|
| 43, 440.1 s | 0.95 | +0.093 | −0.016 … −0.111 each | **−0.30 m.u./s** |
| 35, 360.1 s | 1.14 | +0.115 | −0.049 … −0.108 each | **−0.34 m.u./s** |
| 27, 260.1 s | 1.00 | +0.092 | −0.105 … −0.141 each | **−0.64 m.u./s** |

O is one of 8 neighbours. Everything else lies behind the tip, so the tip is pulled back into its cluster.
- A grown structure is therefore a **compact blob anchored by the sensor-site bodies**. Its face toward O settles about 1.5–2 m.u. from O.
- That holds **whatever the blob's size**: each boundary element always has about 7 neighbours behind it.
- A link to O can hold only if **O is surrounded**, by elements on several sides that balance one another. That is what happens in F5(ii): bridges from 6 angular sectors converge on O, and its four nearest elements end at 0.41–0.48 m.u.

## 3. Pilots: what does not fix it

Every pilot runs the full 50 F5 episodes (800 s). The metric is the late active-path fraction: per step, the fraction of active sites with a strong path to O, over t > 640 s. It is a proxy for E, measured outside the evaluator's assay copies, so it is not E itself.

| Pilot | What changed | F5(i) late path fraction | F5(ii) late path fraction | Elements at end (i) |
|---|---|---:|---:|---:|
| Baseline (7.11 law) | — | **0.000** | 0.323 | 45 |
| Formation margin in the trial (2×) | new-element edges need ≥ 1.0 /s | 0.000 (no effect: deficit-reducing births are accepted anyway) | 0.323 | 45 |
| Robust service (2×) | B-path serves a site until every path edge is ≥ 1.0 /s | 0.000 (any path 12% of steps overall, vs 4.6%) | 0.433 | 45 |
| Budget 96 | cap and cost limit 64 → 96, D3 scaled | 0.003 | — | 67 |
| Budget 128 | 64 → 128 | 0.015 (no path held 20 s) | — | 81 |
| Local motion kernel (scratch copy) | each motion pair term × exp(−r²) | 0.003 | **0.000** (worse) | 44 |

Earlier revisions already tested the birth-rule side:
- fairness (7.9);
- smallest deficit first (7.10);
- output first (7.11).

**Conclusion:** the birth rules, the margins and up to twice the budget do not make a one-sided bridge hold. Simply making the motion pull local makes both starts fail. The limit is the cohesive mean-field motion law together with the geometry of the empty start, in which the roots sit on the sensor ring about 4 m.u. from O. It is not the growth rules.

## 4. Options (the next revision is a design decision)

| Option | What it is | Claim | Cost and risk |
|---|---|---|---|
| **A. The seeded start becomes the standard start** | Development grows from a small hand-built seed, as F5(ii) does. That is the start that passes today. | **Narrowed:** "a seeded network grows a functional sensor→output path, and responds through it", not "from nothing" | Fast: F6–F9 can run, then the cost projection and the development request. **Owner decision** (it changes the claim). |
| **B. A motion law in which a resonant chain is mechanically stable** | For example, bonded attraction only between direct chain partners plus repulsion from all, so geometry follows the coupling graph. Needs a new design revision (8.x), new N1/F1–F4 and its own pilots. | Keeps "from nothing" | Long, and uncertain: one local-kernel variant already failed. Science-level change to the medium law. |
| **C. Growth that surrounds O** | B-path aims bridges at O from several angular directions, as in F5(ii) | Keeps "from nothing" | Uncertain: in (i) the roots sit on one side (sites 1–3, 6–7), and the budget must cover several bridges. Testable with an in-process pilot. |

**Drafter's recommendation, from the goal (a new AI foundation that beats the scripted AI):**
- **Take A now, as an explicit narrowing**, so that F6–F9 and the development run can measure whether grown shapes learn the task at all.
- **Keep B and C as a parallel research item**, tested with pilots before any design revision.
- "From nothing" is a stronger claim, but it is not what the task needs. A is the owner's decision (`docs/PLAN_CURRENT.md`, "Decisions only the owner can make").

## 5. Files

- `diag_f5i_link_hold.py`, `analyze.py`, `trace.json.gz`: the per-step replay (committed).
- `pilot_formation_margin.py`, `pilot_service_margin.py`, `pilot_budget.py`, plus their logs: in-process pilots.
- `kernel_pilot/`: the scratch-copy kernel pilot (`kpilot.py`, logs, `rev7_medium_kernel.patch`).
- Raw pilot traces (11–12 MB each) stay local, out of git, listed with SHA256 in `RAW_FILES_OUTSIDE_GIT.json`.
- Receipt folders: `growing_shapes/runner/rev711_diag_link_hold_20261006/`, `rev711_pilot_margin_*`, `rev711_pilot_service_*`, `rev711_pilot_budget_*`.

## 6. Addendum (same night): growth from the output side, and a shorter motion range

These are further pilots of option C, plus one more medium variant. The metric and the 800 s horizon are the same as in section 3. "Held" means the first path that lasted ≥ 20 s continuously.

| Pilot | (i) late path fraction | (i) first held path | (ii) late path fraction | (ii) first held path |
|---|---:|---:|---:|---:|
| Baseline (7.11 law) | 0.000 | none | 0.323 | (held from about 280 s in the fixture) |
| **Bidirectional B-path** (every second B-path birth grows from O's side toward the roots; `pilot_bidirectional.py`) | **0.605** | **122.5 s** | **0.000** | none |
| Motion range 1.5 m.u. (scratch copy; N^x cutoff 3 → 1.5; `kernel_pilot/rev7_medium_motion_range_1p5.patch`) | 0.337 | 461.5 s | 0.000 | none |
| Motion range 1.5 + bidirectional | 0.323 | 272.0 s | 0.096 | 868 s (simulated time, including assay steps) |

**What this shows:**
- **(i) can connect and hold.**
  - With bidirectional growth, an output-side cluster forms around O: 13 of 25 B-path births were output-side, and the four nearest elements ended 0.35–0.38 from O.
  - Forward bridges then meet it, and the path holds from 122 s with 45 elements, including 19 B1 sensor births.
- **The same rule breaks (ii).**
  - (ii)'s O at (−0.5, 0) lies within 3 m.u. of the seed blob.
  - Each lone output-side birth, at (0.05, −0.09) about 15 times, is dragged into the seed blob by the mean pull, so the budget is spent on births that do not stay.
- **A 1.5 m.u. motion range rescues (i) but not (ii).**
- **No variant tested passes both starts.**
  - Growth success depends on the start geometry: whether O's neighbourhood lies beyond the motion cutoff from the root blob.
  - So the growth rule is not yet robust, and any fix must be judged on both starts. A pilot that rescues one start is not a fix.

**Updated options:**
- **A**, the seeded start as standard, is unchanged.
- **C has a working mechanism:** an output-side cluster that is not inside the motion reach of the root blob. Its two candidate implementations:
  - bidirectional growth, plus a rule that the output-side cluster is grown **before** the forward bridge arrives;
  - a shorter motion range.
- Each succeeded on one start only.
- **B**, a motion law where a resonant chain is mechanically stable, remains the root fix. The 1.5 m.u. range is a crude version of it.

The recommendation is unchanged: A now, with B and C as research, pending the owner and the Codex recheck. Raw traces are local and hashed (`RAW_FILES_OUTSIDE_GIT.json`).
