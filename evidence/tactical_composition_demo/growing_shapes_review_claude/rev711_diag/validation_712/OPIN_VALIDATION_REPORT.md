OBSERVED PAIRED IMPROVEMENT IN AN EXPLORATORY BATTERY (revision 4): the root-relative O pin (C2) met the F5 gate shape in 8/10 runs against the control's 3/10 on the same keys; direction dependence is a hypothesis; F5 outcomes depend on the key set under every rule tested, so one key establishes only one configuration

# The root-relative output pin (revision 7.12, C2): pilot tests, possible mechanism and research

**Date:** 2026-10-07. **Author:** Claude (claude-opus-5-5).
**Revision 4** answers the Codex round-3 recheck (`docs/reviews/tactical_0h_opin_validation_recheck3_codex.md`, R3-F1, R3-F2, N1–N3). Revision 3 (`183766a`) answered the round-2 recheck (`docs/reviews/tactical_0h_opin_validation_recheck2_codex.md`, CHANGES_REQUIRED, R2-F1 to R2-F4 and N1). Revision 2 (`b5d8969`) answered round 1 (`docs/reviews/tactical_0h_opin_validation_recheck_codex.md`, R1–R6). Revision 1 is at commit `47b578c`. The self-audit is in §8.
**Why this exists:** the owner, on the proposed pin change, said: "it can not be decision — we should confirm it with tests and explain it etc... maybe do research".
**Status:** exploratory pilots. No verdict, no fixture result. The historical fixture verdicts are unchanged.
- **Provenance:** `PROVENANCE.md` (this directory) lists, per run:
  - the commit recorded at launch;
  - the pilot scripts;
  - the key recipes and world intervals;
  - what can and cannot be proved about the exact script bytes.
  - In short, all 34 runs used the reviewed 7.11 scientific pin `e66c8969…e357`, recorded in each receipt. Four ran at HEAD `553369e`, thirty at HEAD `fd21826`. The pilot scripts are overlays that the receipts do not bind.
- **Instrumentation:** `../pilot_common.py`, a live-only class-level recorder with a clone-isolation check and an exact count of 160 steps per training episode.
  - **The estimator:** the same A/B/E estimator as Harness.F5, with exact baseline metric reproduction at the stored floats (7.12 review N3). It is not complete Harness.F5 equivalence.
  - **The 160-decision guard:** the 30 battery runs have it. The four earlier assays predate it.
- **The stored-data analysis** for this revision (`analyze_stored.py` → `STORED_ANALYSIS.json`) reads only the local raw traces. It ran no simulation.

## 1. What was tested

- **Five key sets per start,** each run under the **origin pin** (the 7.11 law, the control) and under **C2** (O at 1.0 m.u. toward the lowest-id effective root):
  - **Key set 0:** the F5 fixture keys and worlds 12,000,000–12,000,049. **This key set informed the C2 design** (the diagnosis pilots used it).
  - **Key sets 1–4:** the alternative keys (suffix `/altK`) and training worlds 13,000,000 + 100,000·k + e, e = 0…49. These intervals are disjoint from every registered schedule in `REV7_SEED_INVENTORY.json`; that is not a claim that IDs above 13 million are reserved.
- **What is shared:**
  - **Assays:** every run uses the same F5 assay panel (`F5_PAIRS`, worlds 10,000,768–10,000,787).
  - **Training worlds:** within one key set, both starts use the same worlds.
  - So the ten runs per rule are **not independent trials.**
- **Distance** (fixture keys, empty start only): 0.5 and 1.5, besides 1.0.
- **Direction controls** (key sets 0–2, both starts): O at 1.0, but **opposite** to the first root (180°) or **perpendicular** (+90°).
- **Gate shape:** A ≥ 0.3, B ≥ 0.3 and max E ≥ 0.5, as in F5, but per single run and descriptive.
- **C2 is a policy package, not a pure displacement:**
  - O is born later: at 40–60 s in the empty start (20 s in the origin control), after a root exists.
  - In the seeded start, the literal O at (−0.5, 0) is removed, and a new O is inserted at t = 20 s with the inherited phase rule (mean nearby phase, otherwise a random draw).
  - Timing and phase therefore change together with position.
- All rows are in `SUMMARY.md`, with logs `batt*.log` and `../assay_pilot_*.log`.

## 2. Results

| Rule | Empty start (i) | Seeded start (ii) | Pooled |
|---|---|---|---|
| **Origin pin** (7.11; in (ii) the legacy seeded pin at (−0.5, 0)) | 2/5 | 1/5 | 3/10 |
| **C2: toward the first root, 1.0** | 5/5 | 3/5 | 8/10 |
| Both starts passing on the same key set | origin 0/5 | C2 3/5 | — |
| C2 **opposite**, 1.0 (key sets 0–2) | 2/3 | 1/3 | 3/6 |
| C2 **perpendicular**, 1.0 (key sets 0–2) | 2/3 | 1/3 | 3/6 |
| Origin pin, key sets 0–2 (the same seeds) | 2/3 | 1/3 | 3/6 |
| C2 toward the root, key sets 0–2 | 3/3 | 2/3 | 5/6 |
| C2 toward the root, distance 0.5 (i, key 0) | fail | — | — |
| C2 toward the root, distance 1.5 (i, key 0) | PASS | — | — |

**Paired changes, baseline → C2 (distance 1.0, ten runs):** five fail→pass, no pass→fail, three shared passes, two shared failures.

**Exploratory calibration** (Codex's figures, nominal and unregistered; no significance threshold was set or is imposed afterwards):
- **Exact paired (McNemar) two-sided p:**
  - 0.0625 pooled;
  - 0.25 in the empty start;
  - 0.50 in the seeded start;
  - 0.125 on key sets 1–4 only (four gains, no losses), which excludes the design-informing key 0.
- **Toward against opposite:** two gains, no losses (p = 0.50). **Toward against perpendicular:** three gains, one loss (p = 0.625).
- **Illustrative 95% Wilson intervals:**
  - 8/10: about 0.49–0.94;
  - 3/10: about 0.11–0.60;
  - seeded C2 3/5: about 0.23–0.88.
- These p-values treat runs as independent, which they are not (see the sharing in §1).

**Reading:**
1. **An observed paired improvement in this exploratory battery.** C2 passed where the origin pin failed in five runs, and never the reverse. It passed the empty start in all five key sets. The evidence does not establish a robust improvement.
2. **Direction: toward-root had the highest observed pass count (5/6 on key sets 0–2), and direction dependence is a hypothesis.**
   - Opposite and perpendicular each passed 3/6, and **perpendicular rescued seeded key 1, where toward-root failed.**
   - Equal counts to the baseline do not establish that off-centre placement has no benefit.
   - Not isolated: first-root identity against distance to the eventual cluster, the order in which tasks drive sites, phase initialization and birth timing.
3. **Distance: two observed outcomes on one key,** 0.5 failed and 1.5 passed. No threshold, monotonicity or sharp transition is established by three offsets.
4. **F5 outcomes vary between key sets under every rule, including the 7.11 law** (origin pin: empty 2/5, seeded 1/5).
   - The 7.11 fixture's "(ii) passes, (i) fails" is therefore conditional on its key.
   - **In this battery the outcomes depend on the key set, so one key establishes only one configuration, not the rule.** The proposed replacement, an engineering consistency gate over five fresh configurations, is DESIGN_0H_REV7 §19.7, pending the owner's approval. It does not claim a proved reliability.

## 3. Possible mechanism (plausible explanations, not identified)

**The claim boundary:** C2 changes the placement infrastructure. It does not demonstrate a new capability to bridge a fixed gap.

**Plausible explanation, consistent with but not proved by the evidence:**
- **The motion law** is a local form of the swarmalator kernel (O'Keeffe, Hong and Strogatz 2017: constant-magnitude attraction `(A + J cos Δθ)·r̂`, repulsion `r̂/r`). Ours is made local by the 8-nearest-neighbour rule. In-phase swarmalators form compact discs, not filaments (research memo §1).
- **The F5(i) diagnosis measured** a lone closing tip retracting at 0.30–0.64 m.u./s and its strong edge being lost.
- **So,** if the grown mass tends to rest as a compact cluster, its nearest elements stay well away from the control's O. In all 7 control failures the final nearest-element distance is 1.67–2.45 m.u. (`STORED_ANALYSIS.json`): 3 empty-start runs with O at the centre, and 4 seeded runs with the legacy pin at (−0.5, 0). An O placed 1.0 m.u. toward the first root sits closer to where that mass forms. In the 8 passing toward-root, distance-1.0 C2 runs, the final nearest element is 0.34–0.59 m.u. from O; some passing direction controls end farther away, for example 1.19 for opposite, empty, key 0 (others end closer, for example 0.33 for opposite, empty, key 1).
- **Not measured (the recorder kept only O, four nearest distances, the element count, the active sites and path membership):**
  - which element forms the last strong edge, and its degree and coefficient;
  - hop counts;
  - whether O lies inside a cohesive cluster;
  - force balance or any equilibrium test.
- **Nearest-element distance is not a measurement of a cluster face.** A pinned O also exerts repulsion and can reshape the cluster itself.
- **"Does not hold a long one-sided filament" is a plausible explanation of the failures tested here,** not a proved geometric limit of the element law.
- **To distinguish mechanisms later,** a preregistered study would record:
  - the closure and end geometry;
  - the last edge's identity, degree and coefficient;
  - hop counts;
  - hold and break durations;
  - inside-cluster contact checks;
  - matched initialization controls (O inserted at the same time and phase but at the origin).
  - A no-growth control and site-order permutations have not been run.

## 4. Per-site response and connectivity (answers R5)

**What F5's E measures:** for each sensor site, the fraction of assay decisions in which that site has a strong path to O. That is reachability, **not a site-specific causal response.** A and B are averaged over all sites.

**Full E vectors and late conditional connectivity** are in `STORED_ANALYSIS.json`, one row per run. Conditional connectivity is, among the late samples (640–800 s) in which a site is active, the fraction in which it has a path to O. The active-sample counts are given alongside. This is conditional on activity, not joint exposure over the window: in seeded key 4, sites 0, 1 and 7 each have 1.0, while the late any-path fraction is 0.70, because they are not always active.
- **Connectivity is mostly all-or-none per site:** in the passing runs most sites have a path in 85–100% of their active late samples, or in none. The exceptions are partial sites, for example site 3 at 56% in empty key 4 and at 4% in empty key 3.
- **Every passing C2-toward run connects 3 or 4 of the 8 sites:**

| C2 toward, 1.0 | (i) late-connected sites | (i) E | (ii) late-connected sites | (ii) E |
|---|---|---|---|---|
| key 0 | 1, 2, 3 | 0, .7, .8, .6, 0, 0, 0, 0 | 0, 1, 7 | .5, .7, 0, 0, 0, 0, 0, .7 |
| key 1 | 0, 1, 2 | .5, .7, .8, 0, 0, 0, 0, 0 | 0, 1, 7 (fail) | .33, .47, 0, 0, 0, 0, 0, .47 |
| key 2 | 1, 2, 3 | 0, .7, .8, .6, .15, 0, 0, 0 | 0, 6, 7 | .5, 0, 0, 0, 0, 0, .6, .7 |
| key 3 | 0 (88%), 1, 2 (3 at 4%) | .33, .7, .8, .2, 0, 0, 0, 0 | none (fail) | all 0 |
| key 4 | 0, 1, 2, 3 (3 at 56%) | .33, .7, .8, .4, 0, 0, 0, 0 | 0, 1, 7 | .5, .7, 0, 0, 0, 0, 0, .7 |

- **So the gate shape can pass with zero recorded assay exposure at five of eight sites.** For example, empty key 1 passes with E = [0.5, 0.7, 0.8, 0, 0, 0, 0, 0], and seeded key 0 with E = [0.5, 0.7, 0, 0, 0, 0, 0, 0.7]. A max-E pass is not broad causal response. (Training coverage is separate: over the whole run these two examples have four sites, not five, with no recorded training path, because site 7 in empty key 1 and site 6 in seeded key 0 had transient paths.)
- **The connected sites are adjacent ones,** consistent with O sitting nearest one root. This is the selected-root bias the research memo warned about.
- **Unavailable:** the stored traces keep only averaged A/B and per-site E. They do not keep own, donor and lesion decisions, per-pair or per-checkpoint summaries, or per-site input interventions. **So per-site causal response is not measured, and the memo's per-site response condition is open, not met.**
- **Future instrumentation** should keep per-checkpoint × pair summaries, active and connected site exposures, and the per-site interventions that identify contributions to A and B.
- **A coverage gate** (for example, a minimum number of connected sites) would change the design and needs the owner's prior approval. It is not applied to these pilots.

## 5. The seeded start: failures and margins (answers R6)

All from the stored events and per-step traces (`STORED_ANALYSIS.json`):

| C2 (ii) | Gate | A / B | max E | First path | Longest hold | Last path | Late any-path | Final nearest to O |
|---|---|---|---|---|---|---|---|---|
| key 1 | **fail, a narrow miss** | 1.657 / 1.491 | 0.467 | 20.1 s | 490.5–792.6 s | 792.6 s | 0.954 | 1.452 |
| key 3 | **fail, a collapse** | 0.428 / **0.2994** | 0 | 20.1 s | 197.8–260.4 s (the longest of 13 holds) | 362.4 s | 0 | 2.338 |
| key 4 | PASS | 1.626 / 1.493 | 0.70 | 20.1 s | 432.1–656.0 s | 800 s | 0.70 | 0.404 |

- **Key 1, the narrow miss:** some site had a path in 95.4% of all late samples (1,526 of 1,600). Conditional on being active, sites 0, 1 and 7 had a path in 93.4%, 94.2% and 94.2% of their active late samples. The last sample with a path is at 792.6 s and the next sample, at 792.7 s, has none, although all eight sites are active. So the path was lost between those samples, 7.4 s before the last checkpoint at 800 s. **The miss follows a late loss, not a failure to form.**
  - The max E equals 0.7 × 2/3 = 0.467 arithmetically (sites 1 and 7; site 0's E is 0.333). That is consistent with assay paths at checkpoints 40 and 45 and none at 50. **This is a hypothesis:** the individual assay records were not kept, and training paths cannot stand in for the assays, which integrate new worlds.
  - Changing the cutoff to rescue the run would not be justified.
- **Key 3, the collapse:** the longest uninterrupted hold was 197.8–260.4 s, among 13 holds. The last path was seen at 362.4 s and lost by 362.5 s. **The order of events:** the last accepted birth was at 360 s, the path was lost at 362.4–362.5 s, and the first cost refusal came at 380 s, after the loss. So the refusal did not cause the collapse. The mass then settled 2.34 m.u. from O. B = 0.2994 is below 0.3 (rounded 0.299 in SUMMARY.md, not a pass).
- **Key 4 passes the averaged gate** with a late any-path fraction of 0.70. **That fraction is not a structural break.** In all 1,600 late samples, a path exists exactly when one of sites 0, 1 and 7 is active (1,120 samples), and each of those sites has a path in every sample in which it is active. The no-path samples are those in which none of the connected sites is driven. For example, at 656.1 s the active sites change to 2, 3, 4 and 5.
- **Training connectivity, averaged assay exposure and end-state stability are three different measurements.** They disagree in key 1. In key 4 the any-path fraction reflects which sites are driven, not a loss.
- **Budget pressure is common, but a refusal is not exhaustion.**
  - In every one of the 34 runs, the first cost refusal comes between 280 s and 480 s.
  - In 16 of the 34 runs, a birth is accepted after the first cost refusal: admission is recomputed for each candidate, and deaths free budget. For example, empty C2 key 3 is refused at 320 s and accepts births at 460, 640 and 800 s.
  - Connectivity can also return without any birth.
  - `STORED_ANALYSIS.json` reports the first cost refusal and the last accepted birth separately.
  - Budget pressure is an untested possible contributor to late losses, not a cause.
  - **A related observation from another battery (`../medium_variants/`, A6v):** in two traced failures of the chain-bond + screening law, the budget's death rule D3 removed an element on the live root→O path. That law is different, so it is not evidence about these runs. Its evidence is delivered separately in `../medium_variants/signal_loss/`; until then this observation is pending.
- **The seeded protocol is downgraded:** it is a literal-scaffold condition with variable outcomes, not a reliable reference. The six-element scaffold and the recorded verdicts are not changed retrospectively. Causal attribution of the seeded failures needs a preregistered matched-start study.

## 6. What C2 does and does not claim

- **It does:** a growth medium that starts with no ordinary elements, with its output placed once by a declared, state-dependent rule (toward its first driven root). The rule makes no direct task-label, score or assay lookup. The roots themselves depend on task-conditioned medium state (7.12 review N2). In these pilots C2 formed a strong sensor→output path and met the F5 shape in 8 of 10 runs.
- **It does not:**
  - bridge a fixed, distant gap;
  - choose a useful output site autonomously;
  - connect most sensor sites: 3–4 of 8 in these pilots;
  - establish learning, qualification or superiority, or a population reliability.
- **Literature (memo §3):** comparable systems fix seeds or frames from their own state, for example Kilobot seed robots and the single seed cell of neural cellular automata. The memo's conditions were:
  - register the rule before final seeds: **not yet done**, it awaits the owner;
  - state the bridging limit: done, as a plausible explanation;
  - check the response per site: **open** (§4).

## 7. Recommendation (for the owner)

1. **Candidate:** C2 can remain the 7.12 candidate for an **owner-approved, preregistered evaluation**. It is not adopted on this evidence alone.
2. **The gate:** replace the single-key F5 with the multi-key gate of DESIGN_0H_REV7 §19.7 (five fresh key sets, every run passing in each start separately, fixed downstream policy), pending the owner's approval.
3. **The seeded start:** treat it as a variable literal-scaffold condition, not a reference.
4. **The longer term:** keep the medium-law route (`../medium_variants/`: chain bonds and screening) as a hypothesis for a growth claim beyond placement.

## 8. Self-audit (revisions 2–4; the drafter's record of the recheck findings and their causes)

| Finding | What was wrong in revision 1 | Cause | Fix |
|---|---|---|---|
| R1 | "five key sets, with a declared pass-rate criterion" was not an operational gate; the downstream F6–F8 policy was undefined | the recommendation was written before the gate was designed | DESIGN_0H_REV7 §19.7, Codex's rule adopted unchanged, pending the owner |
| R2 | "VALIDATED AS AN IMPROVEMENT", "the direction matters", "other directions do not", "the threshold lies between 0.5 and 1.0" | counts were read as effects, without calibration or controls for shared worlds and the design-informing key 0 | §2 reworded; calibration and the sharing stated |
| R3 | face placement and a filament limit stated as fact; the finite-cutoff paper misdescribed | the memo's inference was promoted to a finding; the Lee et al. equations were not checked | §3 reworded as a plausible explanation; memo corrected (its §1 note) |
| R4 | "every pilot ran at `fd21826`" (four ran at `553369e`); pilot overlays not bound | the receipts' commit field was not read per run | `PROVENANCE.md` |
| R5 | per-site response claimed as a memo condition "adopted" | E (reachability) was taken as response | §4: full E and per-site connectivity; causal response marked unavailable |
| R6 | seeded failures not separated; "largely luck" | outcome counts without the event history | §5 from stored events |
| R2-F1 (round 2) | §19.7's downstream policy conflicted with the Harness guards; F7's matched key and worlds were unnamed | the gate was specified for F5 without reading how F6–F8 consume F5 | §19.7 amended: existing guards kept, M keys and worlds named, g = 1 state retention, INVALID rows |
| R2-F2 | "after that no new elements can be added" (the first cost refusal read as permanent exhaustion) | a single summary time was over-read; admission is recomputed for each candidate | §5: refusal and last birth reported separately; key 3's order of events stated |
| R2-F3 | key 4's no-path samples read as a break; key 1's per-checkpoint E stated as measured; key 3's hold called the only one | site activity was not separated from structure; arithmetic was taken as a record | §5 reworded; key 1's decomposition is a hypothesis; "the longest of 13 holds" |
| R2-F4 | the connectivity denominator misdescribed; the coverage example had four zero sites, not five | the analyzer's definition was not quoted | §4 and the JSON note define conditional connectivity with active counts; a true five-zero example |
| N1 | "a single-key F5 gate is not reliable"; the passing-distance scope; the controls' O positions | wording broader than the data | first line, §2 item 4 and §3 bounded |
| R3-F1 (round 3) | §19.7's INVALID row allowed a rerun from retained state that failed its own identity check | two cases (a missing record, a damaged source) were merged in one row | §19.7: the cases are split; a damaged retained source blocks, with no regeneration or rerun |
| R3-F2 | key 1's 95% was the any-site fraction, stated per site; "never reaching O" extended assay absence to the whole run | the aggregate and conditional measures were still mixed in prose | §5 and §4 give the separate measures |
| R3 N1–N3 | §19.7 precedence ("only", "as now"); "passing direction controls end farther away"; the A6v observation not yet delivered | wording broader than the record | precedence restated; "some", with a counterexample; marked pending its delivery |

## 9. Limits

- One run per configuration. Repeating an identical deterministic seed would add nothing; broader independent configurations are what is missing.
- The distance outcomes cover one key; the direction controls cover three.
- Pilots measure only F5's A/B/E. F6–F9, control M/U and development are not measured.
- Every number is a descriptive pilot value, not a verdict.
- **Raw traces** (30 files, 11–12 MB each) stay local in this directory (gitignored), listed by SHA256 in `RAW_FILES.json`. Receipts are in `growing_shapes/runner/rev711_pilot_*_20261007/`.
