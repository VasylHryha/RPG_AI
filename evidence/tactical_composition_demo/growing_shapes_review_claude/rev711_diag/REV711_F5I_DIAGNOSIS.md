DIAGNOSED (narrowed, revision 2): in the empty-start trajectory each closing link is lost because the motion law pulls the bridge tip back; in the scaffold pilots, growth succeeded only when started from a driven root mass inside the sensor ring; no tested rule change sustained late connectivity in both starts

# Why F5(i) (growth from an empty start) fails: diagnosis after revision 7.11

**Date:** 2026-10-07 (night). **Author:** Claude (claude-opus-5-5), drafter of revisions 7.x.
**Revision 2.** It answers Codex's owner recheck `docs/reviews/tactical_0h_rev711_diagnosis_recheck_codex.md` (CHANGES_REQUIRED, R1–R4); see the self-audit in section 7. Revision 1 is in git at `15cda3e` and `fa367a0`.

**Status:** diagnostic and pilot evidence only. No verdict, no fixture result, no pinned file changed.
- Pilots patch behaviour **in-process only**, or run on a **scratch copy**.
- Each writes its own receipt folder (`growing_shapes/runner/rev711_diag_*`, `rev711_pilot_*`); the 7.11 fixture receipt is untouched.
- A receipt's pin identifies the unchanged repository inputs, not the patched behaviour. The patch scripts and the raw-file hashes identify that.
- Authority: decision 0031 (runs after 22:00).

**Input:** the 7.11 fixtures (`a52ddbd`): N1 and F1–F4 PASS, F5(ii) PASS (A 1.451, B 1.303, max E 0.8), F5(i) FAIL (A 0.19, B 0.21, E 0).

## 1. What happens in F5(i)

A replay of F5(i) with the fixture keys, recording every 0.1 s world step to t = 480 s (`diag_f5i_link_hold.py`, `trace.json.gz`), shows:

- **Paths do form.** A strong site→O path is closed at **12 growth checks** (220–440 s), each time by a new B-path element. Paths are present in 365 of 4,800 samples (12 observed intervals).
  - Paths born and lost entirely between 0.1 s samples are not inventoried.
- **Each observed path breaks within 0.1–17 s, by geometric coefficient loss.** At every interval's first absent sample:
  - the closing element is still in O's held phase list;
  - O's phase degree is still 8;
  - the element's distance has crossed √(ln 8) = 1.442, so its coupling coefficient 32·exp(−r²)/8 is below 0.5 /s;
  - no D1, D3 or D4 removal occurs in the replay.
- **How the distance grows.** The closing element is born 0.95–1.37 from O and moves away at 0.3–0.6 m.u./s in its first instant. Examples: element 23, 1.30 → 2.20 in 20 s; element 43, 0.95 → 1.49.
- **Phase is not the direct cause of the edge loss.** The strong-edge test does not use the phase difference. From t ≈ 300 s, O is phase-aligned with its weighted neighbourhood (0.06–0.5 rad), and each closing element with O (0.0–0.3 rad). Phase still enters the motion through its cosine and the actual transmission.
- **Then the budget runs out** (about 440 s), the closings stop, and the nearest element settles 1.9–2.4 m.u. from O.

## 2. The mechanism: instantaneous force on the closing element

The motion law (`medium/rev7_medium.cpp`, the `rhs` loop) gives each element the **mean** over its ≤ 8 nearest motion neighbours (elements and active site bodies, r < 3) of
**(A(1 + J cos Δφ) − B/r)** along the unit vector to the neighbour, with A = B = 1 and J = 0.8. For an in-phase pair this is 1.8 − 1/r: repulsive inside 0.556 m.u., attractive beyond.

**Instantaneous RHS projection onto the direction to O,** at the step after birth. These are signed contributions, already divided by |N^x| = 8, and they are velocities, not 0.1 s displacements. The values are Codex's independent reconstruction from unrounded frames; they agree with mine.

| Tip, time | Distance to O | O | Nearest rear element (inside 0.556: repulsive, pushes toward O) | The other six, summed | Sites | **Total toward O** |
|---|---:|---:|---:|---:|---:|---:|
| 43, 440.1 s | 0.95 | +0.093 | +0.016 (element 37) | −0.413 | 0 (none in N^x) | **−0.304 m.u./s** |
| 35, 360.1 s | 1.14 | +0.115 | +0.019 (33) | −0.474 | 0 | **−0.340** |
| 27, 260.1 s | 1.00 | +0.092 | +0.008 (26) | −0.736 | 0 | **−0.635** |

**Reading:**
- O is one of 8 motion neighbours of the tip. The other elements at 0.6–1.5 m.u., behind the tip and in phase, attract it back, and their sum outweighs O's pull.
- **Site bodies are not missing terms here.** The nearest site is ≥ 2.86 m.u. away, farther than every selected element.
- Dividing by 8 sets the speed, not the sign.

**What this does not show** (corrections from revision 1; section 7):
- **It does not show that a one-sided bridge can never hold, or that O must be surrounded.**
  - **The passing F5(ii) is one-sided:** at the end, all 44 ordinary elements have x > −0.5, their angles about O span only −17° to +77°, and the nearest four sit at 0.44, 0.54, 0.56 and 0.78 m.u.
  - **F1c's one-sided scaffold also passes.**
  - Different local spacing, repulsive contacts and neighbour membership can balance the motion without surrounding O.
- **The finding is local and trajectory-specific:** in this empty-start growth trajectory, each closing element is born with more attracting mass behind it than O supplies in front.

## 3. Pilots

**The metric is a late training-connectivity diagnostic, not E.** Per training step, the number of active sites with a strong path to O, divided by the number of active sites, averaged over t > 640 s.
- **It differs from E.** F5's E is an unconditional per-site path frequency, measured on fresh growth-frozen assay copies from checkpoints 40/45/50, and the gate uses max over sites.
- **So the diagnostic must not be compared with E's 0.5 gate.** For example, the baseline seeded run scores 0.323 on it, while its late unconditional site-0 frequency is 0.70 and its fixture max(E) is 0.80.
- Zero training connectivity also does not prove zero connectivity in assay copies. The pilots do not measure A or B.

All pilots run the 50 F5 episodes (800 s) with the fixture keys.

| Pilot (what changed) | (i) late connectivity | (i) longest continuous path | (ii) late connectivity | (ii) longest continuous path | Note |
|---|---:|---:|---:|---:|---|
| Baseline (7.11 law) | **0.000** | 16.7 s | 0.323 | (site 0: 0.70 of late steps) | — |
| **Stricter trial graph** (edges incident to the newborn pruned below 1.0 /s in the trial graph only) | 0.000 | 16.7 s | 0.323 | — | Traces and events identical to the baseline: a deficit-reducing birth is still accepted. **This does not test a rule that requires a robust closing edge.** |
| **Robust service** (B-path decisions use 1.0 /s; E, B1 and measurement keep 0.5) | 0.000 | 44.2 s (440–484 s) | 0.433 | 288 s | Active and verified. Connectivity rises, but is not sustained late in (i) |
| **Budget 96** (admission and D3 limits) | 0.003 | 16.7 s | — | — | 67 elements |
| **Budget 128** | 0.015 | 16.7 s | — | — | 81 elements; zero cost/cap refusals and zero D3. Not sustained **within 800 s with this scheduler**; a larger budget with a different scheduler or horizon is not ruled out |
| **Local motion kernel** (scratch; every element and site pair term, attraction and repulsion, × exp(−r²)) | 0.003 | — | 0.000 | — | Both lose late training connectivity. Says nothing about bonded or other local laws |
| **Bidirectional B-path** (every second B-path birth grows from O's side toward the roots) | **0.605** | **677.5 s** (site max 0.8) | **0.000** | 2.7 s | (i) connects and holds. In (ii), each lone output-side birth, about 15 times at (0.05, −0.09), is pulled into the seed structure |
| **Motion range 1.5 m.u.** (scratch; the N^x cutoff, 3 → 1.5) | 0.337 | path held from 461.5 s | 0.000 | — | — |
| Motion range 1.5 + bidirectional | 0.323 | held from 272 s | 0.096 | — | — |
| **O placement swapped** ((i): B-out puts O at (−0.5, 0); (ii): literal O at (0, 0)) | **0.000** | — | **0.409** | held from 272 s (sites 0, 6, 7: 0.7, 0.8, 0.4) | **O's position is not what separates the two starts** |
| **Scaffold: hexagon on the ring** ((ii) with the six-element hexagon centred at (4.0, 0) on site 0 instead of (3.1, 0)) | — | — | **0.000** | never | Moving the seed onto the ring makes (ii) fail like (i) |
| **Scaffold: random phases** ((ii) hexagon phases uniform from a fixed pilot RNG) | — | — | 0.397 | held from 272 s | Phase coherence of the seed is not needed |
| **Scaffold: zero gain** ((ii) hexagon elements are not driven roots) | — | — | **0.000** | never | The seed must be driven roots |
| **Inward B1** (B1's spiral centred 0.9 or 0.6 m.u. inward from the site; one root per B1 birth) | 0.000 (both offsets) | (20 s-held episode at 380 s only) | 0.362 (0.9) | held from 272 s | A single inward root does not reproduce the seed's effect; (ii) unaffected |
| **B1 root groups** (the first B1 birth at each site becomes a compact group of 3 or 6 driven roots 0.9 m.u. inward; `pilot_rootgroup.py`) | 0.000 (3 and 6) | held from 330 s (group 3) only; any path 31% of all steps (group 3) | 0.363 (group 3) | held from 272 s | Groups form at **every** demanding site (14–18 extra births), which splits the budget; (ii) has exactly **one** group |

Earlier revisions changed the birth rules:
- fairness (7.9);
- smallest deficit first (7.10);
- output first (7.11).

**Conclusions (narrowed):**
- **These specific interventions did not sustain late connectivity in both starts.**
  - Bidirectional growth and a shorter motion range each rescue (i) and fail (ii).
  - Robust service helps (ii) and transiently (i).
- **O placement is ruled out as the separating factor:** with O swapped, (i) still fails and (ii) still passes.
- **What separates the starts is the initial scaffold.** The scaffold pilots isolate its relevant property:
  - **a group of several driven root elements** (six, gain 1), placed as a mass about 0.9 m.u. **inside** the sensor ring;
  - moving the group onto the ring, or removing its drive (gain 0), makes (ii) fail like (i);
  - randomizing its phases does not.
- **One B1 root placed inward is not enough.** It does not reproduce the effect: the empty start still fails with B1 births 0.6–0.9 m.u. inward.
- So the success of (ii) comes from a **driven root mass inside the ring**, which the empty start's one-at-a-time B1 births on the ring never build within this budget and horizon.

## 4. Options (the next revision is a design decision)

| Option | What it is | Claim | Cost and risk |
|---|---|---|---|
| **A. A seeded protocol** (owner decision) | A **new protocol revision**, not a flag. Codex R3 explains why: F6 takes its baseline from checkpoint (i, 40), and F7/F8 use the (i) run, so they cannot simply continue on (ii). It must specify the common initial structure (roles, gains, phases, positions, pin), RNG treatment and cost accounting for intact/M/U; revise F6–F9 targets and stop rows; and pass review before implementation. The present F5 stop is not bypassed. | Narrowed to **seed-assisted growth**. F5(ii) transmission does not establish learning, resonator qualification, recursive background generation or superiority to scripted AI. | A design revision plus implementation; not necessarily the fastest complete route |
| **B. A mechanically supported medium law** | Codex's sharper version: a locally formed, bounded-degree **bond graph** with reciprocal, phase-dependent spring stiffness and a rest length, plus short-range exclusion; motion follows the gradient of that local energy. An aligned chain between two fixed ends then has balanced interior tensions and positive restoring stiffness. Bond formation, breaking and remodelling come from local state; site anchors and the geometry→mode feedback must be defined. Needs its own design, normalization ledger and N1/F1–F4. | Keeps "from nothing" | A science-level change to the medium; long; untested |
| **C. Growth-rule variants** | Two-ended growth (tested: (i) yes, (ii) no); a growth order in which the output-side component is supported before the forward bridge arrives (untested); a robust-closing-edge requirement (untested; the tested trial pruning did not require one) | Keeps "from nothing" | Each needs pilots on **both** starts. Rescuing one start is not a fix |
| ~~D. O placement~~ | Swapping O between the starts did not change either outcome (section 3) | — | Ruled out as the separating factor; no design change proposed |

**Drafter's recommendation (after the scaffold pilots):**
- **A is now a well-founded protocol choice, not an arbitrary seed.** The property that makes growth succeed is identified: a small group of driven root elements as a mass inside the sensor ring. Phase is free.
- **A seeded protocol (A)** would specify that "embryo" explicitly and identically for intact, M and U: k driven elements in a compact group about 0.9 m.u. inward of one site.
- **A "from nothing" alternative within C was piloted:** B1 grows a compact root group (3 or 6) inward of each site at its first birth. It **did not sustain late connectivity in (i)**, because groups formed at every site and split the budget. A variant with **one** group (for example at the first site to demand, with later sites as single roots) is the remaining untested "from nothing" candidate.
- **B stays the long-term root option.**
- **A and the claim narrowing are the owner's decision** (`docs/PLAN_CURRENT.md`).

## 5. Files

- `diag_f5i_link_hold.py`, `analyze.py`, `trace.json.gz`: the per-step replay (committed).
- In-process pilots, each with its log: `pilot_formation_margin.py`, `pilot_service_margin.py`, `pilot_budget.py`, `pilot_bidirectional.py`, `pilot_oswap.py`.
- `kernel_pilot/`: scratch-copy pilots (`kpilot.py`, `kpilot2.py`, logs, `rev7_medium_kernel.patch`, `rev7_medium_motion_range_1p5.patch`).
  - Provenance limit: no launch receipt cryptographically binds those processes to the scratch builds. The scratch build manifests verify their sources and images.
- Raw pilot traces (11–12 MB each) stay local, out of git, listed with SHA256 in `RAW_FILES_OUTSIDE_GIT.json`.
- Receipt folders: `growing_shapes/runner/rev711_diag_link_hold_20261006/` and `rev711_pilot_*`.

## 6. (Revision 1's addendum is merged into section 3.)

## 7. Self-audit (revision 2, answering the Codex recheck)

| Finding | Fix | Cause |
|---|---|---|
| **R1 (high):** "a link holds only if O is surrounded" and "whatever its size" are contradicted by the passing one-sided F5(ii) (all elements at x > −0.5, angles −17° to +77°) and by F1c. The six-sector account of F5(ii) was wrong: I read **birth** positions, not the final stored state. The nearest distances mixed two pilots. | Removed. Section 2 now states the local, trajectory-specific force imbalance and describes (ii) from its stored state. C is a hypothesis. | I generalized from three sampled tips to an impossibility claim, and inferred (ii)'s geometry from birth sectors without checking the final frame |
| **R2 (medium):** the pilots support bounded observations only. The metric is not E. The formation patch prunes the trial graph and does not require a robust edge. The budget result is limited to this scheduler and horizon. The kernel patch also scales repulsion and sites. | Section 3 relabels the metric, adds longest-path durations and per-site values, narrows each conclusion and labels the formation pilot correctly | I wrote the conclusions more broadly than the interventions tested |
| **R3 (medium):** option A cannot continue F6–F9 on (ii) as the code stands | Option A is now described as a new seeded protocol revision, with the required specification items and the narrowed claim | I treated a protocol change as a flag |
| **R4 (low):** the force table omitted the positive nearest-rear term | The table now shows signed O, nearest-rear, other-six and site sums, labelled as instantaneous RHS projections | I listed only the rear terms that pulled back |
| (new) An O-placement confound was raised in the review | Tested by swapping O between the starts: no change in either outcome; ruled out as the separating factor | — |
