DIAGNOSED (narrowed, revision 3): in the empty-start trajectory each closing link is lost because the motion law pulls the bridge tip back; no tested intervention sustained late training connectivity in both starts; the seeded trajectory is sensitive to its scaffold, but no minimal embryo is identified

# Why F5(i) (growth from an empty start) fails: diagnosis after revision 7.11

**Date:** 2026-10-07 (night). **Author:** Claude (claude-opus-5-5), drafter of revisions 7.x.
**Revision 3.** It answers Codex's owner rechecks round 1 (`docs/reviews/tactical_0h_rev711_diagnosis_recheck_codex.md`, R1–R4) and round 2 (`…_r2.md`, R2-F1 to R2-F4); see section 7. Earlier revisions are in git (`15cda3e`, `fa367a0`, `739b167`, `423591c`).

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

**The metric is a late training-connectivity diagnostic, not E.** Per training step, the number of active sites with a strong path to O is divided by the number of active sites; this is averaged over t > 640 s, each step weighted equally.
- F5's E is an unconditional per-site path frequency, measured on fresh growth-frozen assay copies from checkpoints 40/45/50, and its gate uses max over sites. **So the diagnostic must not be compared with E's 0.5 gate.**
  - For example, the baseline seeded run scores 0.323 on it, while its late unconditional site-0 frequency is 0.70 and its fixture max(E) is 0.80.
- Zero training connectivity does not prove an assay FAIL. The pilots measure no A or B.

**Path exposure, one definition throughout.** Recomputed from the stored traces (`durations.txt`), without rerunning:
- "present" = a sample with a strong path for **any** active site;
- "longest any-site interval" = the longest run of consecutive present 0.1 s samples (start–end, and the sample count);
- "longest same-site run" = the longest run for one site.
  - Sites are active only part of the time, so an any-site interval can join different sites, and an inactive episode can interrupt a site's run without the chain breaking.

**All valid pilots ran 8,000 training steps (800 s) with the fixture keys.**
- **One pilot is INVALID and preserved as such:** range 1.5 + bidirectional on (ii) (`kpilot_r15bidir_ii`), finding R2-F1 in section 7.
  - Its recovery clones inherited the closure-wrapped `integrate` and advanced the **live** run: 9,200 steps ending at 920 s.
  - Its 0.096 is withdrawn.
  - The other 25 traces have exactly 8,000 steps ending at 800 s and **no recovery candidates**, so this defect did not touch them.

| Pilot (what changed) | Start | Late connectivity | Present samples (first–last present) | Longest any-site interval (samples) | Longest same-site run (samples) |
|---|---|---:|---|---|---|
| Baseline (7.11 law) | (i) | **0.000** | 365 (220.1–456.7) | 440.1–456.7 (167) | site 3 (167) |
| Baseline (7.11 law) | (ii) | 0.323 | 5,020 (140.1–800.0) | 272.1–608.0 (3,360) | site 2 (960) |
| **Stricter trial graph** (edges incident to the newborn pruned below 1.0 /s in the trial graph only) | (i) | 0.000 | identical to the baseline (traces and events identical) | — | — |
| **Robust service** (B-path decisions use 1.0 /s; E, B1 and measurement keep 0.5) | (i) | 0.000 | 984 (220.1–484.2) | 440.1–484.2 (442) | site 3 (442) |
| Robust service | (ii) | 0.433 | 5,046 | 320.1–608.0 (2,880) | site 6 (960) |
| **Budget 96** (admission, and D3 through scaled cost) | (i) | 0.003 | 644 (220.1–682.3) | 440.1–456.7 (167) | site 3 (167) |
| **Budget 128** | (i) | 0.015 | 687 (220.1–780.4) | 440.1–456.7 (167) | site 3 (167) |
| **Local motion kernel** (scratch; each element and site pair term, attraction and repulsion, × exp(−r²)) | (i) | 0.003 | 659 | 400.1–410.0 (100) | site 2 (100) |
| Local motion kernel | (ii) | 0.000 | 220 (160.1–362.5) | 300.1–304.0 (40) | site 0 (40) |
| **Bidirectional B-path** (unconditional alternation; every second B-path birth grows from O's side) | (i) | **0.605** | 6,903 (80.1–800.0) | **122.6–800.0 (6,775)** | site 3 (2,775) |
| Bidirectional B-path | (ii) | 0.000 | 180 (61.4–401.3) | 61.4–64.0 (27) | site 0 (27) |
| **Motion range 1.5** (scratch; element and site N^x cutoff 3 → 1.5; phase selection stays at 3) | (i) | 0.337 | 3,567 (200.1–800.0) | 461.6–704.0 (2,425) | site 3 (1,120) |
| Motion range 1.5 | (ii) | 0.000 | 38 (200.1–400.6) | 220.1–220.7 (7) | site 0 (7) |
| Motion range 1.5 + bidirectional | (i) | 0.323 | 4,841 (80.1–800.0) | 361.5–608.0 (2,466) | site 2 (960) |
| ~~Motion range 1.5 + bidirectional~~ | (ii) | ~~0.096~~ **INVALID** | — | — | — |
| **O placement swapped** ((i): B-out puts O at (−0.5, 0)) | (i) | 0.000 | 63 (260.1–443.2) | 440.1–443.2 (32) | site 1 (32) |
| O placement swapped ((ii): the literal O at (0, 0)) | (ii) | 0.409 | 5,173 (100.1–800.0) | 320.1–624.0 (3,040) | site 6 (1,120) |
| **Scaffold: hexagon on the ring** (centre (4.0, 0) instead of (3.1, 0)) | (ii) | **0.000** | 5 (380.1–400.4) | 400.1–400.4 (4) | site 0 (4) |
| **Scaffold: random phases** (from a fixed pilot RNG) | (ii) | 0.397 | 5,021 | 272.1–608.0 (3,360) | site 2 (960) |
| **Scaffold: zero gain** (the hexagon elements are not driven roots) | (ii) | **0.000** | 12 (220.1–360.6) | 360.1–360.6 (6) | site 0 (6) |
| **Inward B1** (B1's spiral centred 0.9 or 0.6 m.u. inward; one root per birth) | (i) | 0.000 (both offsets; identical traces) | 818 (220.1–465.9) | 380.1–418.3 (383) | site 2 (383) |
| Inward B1 (0.9) | (ii) | 0.362 | 4,811 | 380.1–608.0 (2,280) | site 2 (960) |
| **B1 root groups, 3** (see the caveats below) | (i) | 0.000 | 2,451 (160.5–564.4) | **330.2–564.4 (2,343)** | site 1 (800) |
| B1 root groups, 6 | (i) | 0.000 | 19 (160.1–240.9) | 240.1–240.9 (9) | site 0 (9) |
| B1 root groups, 3 | (ii) | 0.363 | 4,860 | 320.1–608.0 (2,880) | site 2 (960) |

**Caveats on the B1 root-group pilot** (`pilot_rootgroup.py`; finding R2-F2):
- **What the wrapper does.** The first accepted B1 birth at a site is removed and re-added as a group centre 0.9 m.u. inward, plus up to GROUP−1 members at r* in a ring around it.
- **The centre is re-added with no clearance or cost check.** For example, in (i) group 3, the centre at t = 360 (site 0) took the cost to 64.4, above 64, and D3 then removed two elements.
- **Members bypass the two-birth B1 quota.** Groups can be partial.
- **The group geometry (centre plus ring) differs from the seed's hexagon,** and it forms over time, not at t = 0.
- **Group counts** (counting B1 events includes the removed original and its re-added centre, so these are not net additions):
  - (i) group 3: 6 centres, 8 members;
  - (i) group 6: 3 centres, 15 members;
  - (ii) group 3: **5** centres (sites 2, 3, 5, 6, 7; 240–340 s) and 9 members, on top of the six-element scaffold.
- So the earlier statement that (ii) has exactly one group was wrong, and the pilot **does not identify why late connectivity disappears in (i).** Resource refusals occurred; budget competition is plausible but not isolated.

Earlier revisions changed the birth rules:
- fairness (7.9);
- smallest deficit first (7.10);
- output first (7.11).

**Conclusions (narrowed after round 2; training-connectivity observations only):**
- **No tested intervention sustained late connectivity in both starts.**
  - Unconditional bidirectional growth and a 1.5 m.u. motion range each gave (i) long connected intervals (from 122.6 s, and 461.6–704.0 s), and lost (ii).
  - Robust service raised (ii) and lengthened (i)'s transient (440–484 s).
- **Long transient successes exist in (i):**
  - root groups of 3: 330.2–564.4 s;
  - inward B1: 380.1–418.3 s;
  - range 1.5: 461.6–704.0 s.
  - These are relevant to scheduling and support alternatives, even though none sustained connectivity late.
- **The seeded trajectory was sensitive to its initial scaffold** in these tested realizations:
  - moving the six-root hexagon onto the ring, or setting its gain to 0, removed late connectivity;
  - one random-phase realization kept it. So initial perfect phase coherence was **not necessary in that realization**.
  - These pilots do **not** identify a sufficient or minimal embryo: there is no count ablation, no gain or radius sweep, and no proof that any compact inward root mass succeeds.
- **The seed's growth history is also not equalized with the empty start.** Seed initialization changes O's birth time, phase and identity, and the two starts use different growth and recovery keys.
- **The O swap rules out only the specific explanation that x = 0 versus x = −0.5 by itself determines the contrast.**
  - It measured no F5 verdict.
  - Both pins lie on the x-axis, while (i)'s first root is at site 2 on the +y axis.
  - Placement does affect the dynamics: (ii)'s diagnostic rose from 0.323 to 0.409.
  - **An O placement rule** (for example one relative to the roots) **is not ruled out.**

## 4. Options (the next revision is a design decision)

| Option | What it is | Claim | Cost and risk |
|---|---|---|---|
| **A. A seeded protocol** (owner decision) | A **new protocol revision**, not a flag. F6 takes its baseline from checkpoint (i, 40), and F7/F8 use the (i) run. It must specify the common initial structure (roles, gains, phases, positions, pin), RNG treatment and cost accounting for intact/M/U, and revise the F6–F9 targets and stop rows, before review and implementation. The present F5 stop is not bypassed. **The embryo is a design prior, not an experimentally established minimum.** | Narrowed to **seed-assisted growth**. F5(ii) transmission does not establish learning, qualification, recursive background generation or superiority to scripted AI | A design revision plus implementation; not necessarily the fastest complete route |
| **B. A mechanically supported medium law** | A locally formed, bounded-degree **bond graph**: reciprocal bonds with positive, phase-dependent stiffness k (kept positive over the operating region), rest length ℓ, short-range exclusion, motion as the gradient of the local energy. **A positive tensile prestrain is required:** with equal spacing d > ℓ between fixed ends, the tension T = k(d − ℓ) > 0 balances interior forces and gives transverse restoring stiffness ∝ T/d. This holds only for the specified chain with frozen phases and bonds; the coupled geometry–phase–bond system needs its own analysis. Bond formation, breaking and remodelling, degree and cost accounting, site anchors and the geometry→mode feedback must be defined. | Keeps "from nothing" | A science-level change; its own design, normalization ledger and N1/F1–F4; long; untested |
| **C1. Supported output-side growth under the current law** | Keep forward growth when it is mechanically adequate. When a closing or frontier body's predicted motion (the actual N^x, site terms and full force balance) is away from O, prioritize a **bounded local support structure on the output side**, instead of alternating lone births blindly. Preserve existing strong paths; require adequate closing coefficients. | Keeps "from nothing" | Untested; instantaneous balance does not guarantee dynamic stability. Must pass **both** starts |
| **C2. A declared root-relative O pin** | At a specified initialization event, choose O once in the radius-1 central disk toward the first eligible driven root or demand, then freeze it. That disk stays ≥ 3 m.u. from the radius-4 sites. O keeps its non-root, no-direct-drive role; its pin is copied into assays; the same causal rule, cost and RNG treatment apply to every comparison policy. **The positional prior is disclosed.** | Keeps "from nothing", with a disclosed positional prior | Untested (the x-axis swap does not test it); needs owner approval because it changes the origin-pin contract |
| **C3. A single B1 root group** | One compact group (for example at the first demanding site), with **atomic feasibility including the centre**, explicit group and quota accounting, and a declared geometry | Keeps "from nothing" | Untested |

**Drafter's recommendation (after round 2):**
- **Do not treat A, or a medium rewrite, as compelled by the evidence.**
- Run a fair, separated comparison of C1, C2 and C3 on **both** starts, with corrected instrumentation (below), before choosing.
  - Each variant changes one factor, so support, placement and initialization are separated.
  - Cost: pilots of about 10 minutes each.
- **A remains available** if the owner prefers seed-assisted growth now. That is the owner's decision.
- **B remains the long-term candidate**, with the prestrain condition.
- **Instrumentation fix before any further pilot:**
  - bind the per-step recorder at the Run or world-step boundary, not as an instance function that clones copy;
  - keep a training-only sink outside cloned state;
  - add a synthetic clone-isolation check: clone integration must leave the live state, clock and sink unchanged, and training must contain exactly 160 steps per episode.

## 5. Files

- `diag_f5i_link_hold.py`, `analyze.py`, `trace.json.gz`: the per-step replay (committed).
- In-process pilots, each with its log: `pilot_formation_margin.py`, `pilot_service_margin.py`, `pilot_budget.py`, `pilot_bidirectional.py`, `pilot_oswap.py`, `pilot_scaffold.py`, `pilot_inward_b1.py`, `pilot_rootgroup.py`.
- `durations.txt`: path exposure recomputed from all stored traces, under the single definition of section 3.
- Known comment errors in the pilot scripts, unchanged as evidence: `kpilot.py` calls its metric "what E averages"; `pilot_formation_margin.py` says every incident edge must be robust. Section 3 gives the correct descriptions.
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
| **R2-F1 (high, round 2):** the combined range-1.5 + bidirectional seeded pilot was contaminated: recovery clones inherited the closure-wrapped `integrate` and advanced the live run (9,200 steps, 920 s) | The pilot is marked INVALID and its 0.096 withdrawn; the instrumentation fix is specified (section 4); the other 25 traces are verified at 8,000 steps with no recovery candidates | I instrumented by assigning an instance function that closes over the live object, without considering that clone() deep-copies the instance dictionary |
| **R2-F2 (medium):** the root-group pilot was misreported ((ii) has 5 groups, not 1) and it bypasses feasibility for the centre and the quota | Correct counts; the admission bypass and partial groups disclosed; the causal "budget split" phrase replaced | I read event counts as groups and did not audit my wrapper's admission path |
| **R2-F3 (medium):** the scaffold and O-swap claims were overbroad ("identified", "phase is free", "O placement ruled out") | Narrowed to tested realizations; the untested confounds listed; O placement rules kept as C2 | I generalized single realizations into necessity and exclusion claims, the round-1 error again |
| **R2-F4 (medium):** the durations mixed first appearance, recurrence and exposure | One definition, recomputed from the stored data for every trace (`durations.txt`) | I wrote the durations from different quick queries |
