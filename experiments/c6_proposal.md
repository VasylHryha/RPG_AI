# C6 proposal: recursive composition R₀ → R₁ → R₂ with the same rule (DRAFT, not approved)

Status: **PROPOSED**, awaiting owner approval. Nothing is registered: there is no `experiments/c6_manifest.json`, `milestones/c6.json` or C6 code. At the owner's request, a development-only pilot was run with scratch code outside the repository (§3b). Authority: `GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md` (C6, the recursive unit interface, the ten recursive-resonator invariants, §5–7). Builds on C4 R003 and C5 R003, both independently accepted (`evidence/c4_r003_review_codex/INDEPENDENT_REVIEW.md`, `evidence/c5_r003_review_codex/INDEPENDENT_REVIEW.md`). Format follows `experiments/c5_proposal.md`. The drafter's self-audit of the first draft is at the end.

**Level names.** Level 0 is a primitive element. Level 1 is an accepted C4 resonator (the standard's R₀). Level 2 is a C5 composite (R₁). Level 3 is the C6 composite (R₂). "Transition n" is level n−1 → n, so transition 2 is level 1 → 2 and transition 3 is level 2 → 3. The standard's "two successive transitions" are transitions 2 and 3.

## 1. The bounded question

> Take accepted level-2 resonators (groups of C4 resonators) and let them interact only through the unchanged C4 element law. Apply the **same** detector, promotion, composition and coarse-model functions that turn level-1 units into level-2 resonators, with thresholds rescaled only by measured timescale (and, implicitly, by measured size). Does a level-3 resonator form, meaning a persistent, recovering, frequency-locked group of level-2 units in which every level-2 unit, and every level-1 unit inside it, stays a live, distinct resonator of its own level? Answering it means testing five things:
>
> - whether the level-3 mode depends causally on level-2 geometry and the reverse, each effect vanishing under its complete matched ablation;
> - whether disturbances travel up from level 1 to level 3, and whether level 3 constrains level-2 boundaries downward;
> - whether the dynamics single out the formed partition: parts re-lock internally faster than across, more clearly than for any other contiguous partition;
> - whether a coarse model that reads only the published level-2 states predicts held-out responses better than strong cheap baselines;
> - whether all of this holds again at transition 2, re-measured on fresh worlds.

Hypotheses:
- **H-C (the standard's central gate):** two successive transitions under one composition rule, each with a valid effective state and bounded predictive error. C6 re-measures transition 2 on fresh worlds under the same rule as transition 3. C5's transition was INCONCLUSIVE, and the H-C gate needs both transitions in one experiment under one rule.
- **H-M at level 3** (whole ↔ parts, one level up), and **H-M at level 2** replicated on fresh worlds.

**The cheap explanations C6 must rule out.**
1. **"Level 3" is one bigger level-2 group**, so the middle level is bookkeeping. Four checks rule this out:
   - *Recursive criterion 6 (§4):* every level-2 part stays a valid, distinct level-2 unit, and so does every level-1 unit inside it.
   - *`timescale_separation_l3`:* relaxation between groups is slower than relaxation between units inside a group.
   - *`hierarchy_specificity_l3` (§5):* within one perturbed run, the formed partition separates fast internal re-locking from slow cross re-locking better than contiguous alternative partitions of the same units. A flat blob gives no partition an advantage.
   - *A disclosure:* the receipt reports whether the level-2 detector accepts the union of a level-3 group's units as a single level-2 resonator.
2. **A dendrogram or connected-component tree.** Nested clustering at two distance thresholds always yields a tree. C6 requires dynamics at every level: locking, recovery after a kick, two-way causality with complete ablations, dose-response, upward and downward transfer, timescale separation and hierarchy specificity. A static tree has none of these.
3. **A different solver or threshold per level.** There is one generic level-n detector, one promotion function, one composition function and one coarse model. Level-n thresholds come from one scaling function applied with the cumulative time factor. A static contract forbids level branches, and the `same_rule_audit` gate records function identities and every threshold at each level.
4. **Trivial lock and clump of clumps**, as in C5. Decoupled controls with drifting rates must fail through mode lock, and controls with static rates must fail through recovery. Both controls get imposed candidates, so they cannot pass empty.
5. **"The coarse state is just one number."** A relaxation baseline that uses the group's own measured relaxation time for the excited channel is the strongest cheap predictor. The coarse model must beat it at both transitions, for each excitation type separately (§7).

These dynamics are not new. Synchronization on hierarchical modular networks proceeds level by level, and pairs inside a community lock first; C6's hierarchy-specificity statistic applies that observation [S1, S2, S6]. Coarse-graining oscillator networks while preserving synchronization is an established method [S7]. Locked populations reduce to a few variables [S3]. Finite-range swarmalators form separate groups [S4, S5]. C6 is a mechanism probe of the R4 recursion rule, not a novelty claim.

## 2. What C5 leaves open, and what C6 takes from it

| Input from C5 | Consequence for C6 |
|---|---|
| Level-2 formation was 15, 13 and 17 of 30 across R001–R003, near the 0.5 threshold; no rate above 50% is established. | The development pilot (§3b) replicates level-2 formation at 148/320. Two principle-derived corrections address the losses: criterion 6 on each part's own timescale, and contact placement. A development design gate measures formation once (target 0.75 at both levels, 30 worlds each) and stops if it is not met. The registered PASS rule uses the Wilson lower bound (§9, D3). |
| The coarse law did not beat relaxation with a measured τ (+0.008, CI [−0.004, 0.019]). | A descriptive split of the accepted R003 receipt, made while drafting, shows that the mean hid two different results:<br>• *Phase pulses:* the port law beats relaxation in 16/17 groups (mean gain +0.033) and beats "no transfer" in 17/17.<br>• *Radial pushes:* it beats "no transfer" in only 4/17 (mean −0.017), so it predicts the other units worse than "nothing moves".<br>• *Weak baseline:* the push relaxation baseline used the **phase** relaxation time.<br>C6 therefore:<br>• scores each excitation type separately;<br>• uses a relaxation time measured for the excited channel;<br>• stores the phase and position parts of every error;<br>• requires a development **coarse readiness** check before the panel (§9).<br>This split changes no C5 verdict. |
| C5 review: inherited port capacities omit sibling contacts; the size-weighted natural rate is declared, not measured (largest gap 0.0088 against a spread of 0.03). | At level 3 the frequency tolerance is about 10× tighter, so these approximations matter. One corrected composition function is used at both promotions (§3). Its fidelity against C5's version is measured in the design gate and reported in the panel (`interface_fidelity`). |
| N1: publication was checked by global counts; non-finite fields passed. | `level_interface` gate: exactly one parent per accepted candidate **per world**, keyed by the candidate's unit set; all numeric fields finite; ports and mode valid; S equal to the candidate's statistics. |
| N2: the overlap calibration lacked its raw measurements. | The design gate commits per-world raw values for every calibrated quantity, and the manifest pins that artifact by hash. |
| N3: zero-area hulls passed with overlap 0. | A degenerate shape (area ≤ 10⁻¹² L²) cannot certify distinctness, so criterion 6 fails for it. A contract covers collinear units. |
| C5 ran the C4 element law with the C4 neighbour rule only. | Unchanged. The interaction range stays at element scale at every level (§13). |

## 3. Units at every level, composition, and the level-3 world

**One owner tree.** The evaluator-side owner keeps labels element → level-1 unit → level-2 group. Member lists stay owner-private at every level. Upper levels see only published `ResonatorState`s (C5's field set: level, X, L, Θ, Ω, natural rate, mode signature, boundary ports, size, S, member digest).

**Publication.**
- *Level-1 states:* `c5_units.resonator_state`, unchanged, except for the port rule if the coarse readiness check selects variant V2 (§7).
- *Level-n states (n ≥ 2):* one new function, `c6_units.compose_state`, used for **both** promotions. It equals C5's `compose_state` except for two corrections from the C5 review:
  1. **Natural rate = measured isolated rate.** The owner runs the parent alone (decoupled from everything else, over its own level's window) and publishes its measured collective rate. At level 1 this gives exactly ω_g (the rotating-frame symmetry), and a contract checks this, so the rule is the same at every level.
  2. **Port capacity includes sibling contacts.** A parent port's capacity list is the k smallest of its child's own-neighbour distances and its distances to the ports of the parent's other children. All of these come from published child states. Non-port sibling members stay invisible, a declared approximation.

  C5's `compose_state` is also computed for every accepted parent, for `interface_fidelity` only.
- *Per-frame series for detection:* the owner computes level-(n−1) X and Θ in every frame by the published rule: X is the unweighted centroid of the child centroids; Θ is the circular mean of the child phases, unwrapped over frames. The detector receives only these series and the owner-computed validity.

**Harvest (label-free, staged, source-isolated).**
- *Level 1:* fresh C4 identical-arm worlds run with the frozen C4 code, as in C5 (templates of 6–16 members, each used once).
- *Level 2:* fresh level-2 harvest worlds are assembled from those templates and run through the generic detector at n = 2. An accepted group becomes a template only if it is **also re-accepted alone**: the same detector, with the group decoupled from non-members, during the run that measures its isolated rate. This filter is label-free. A template records:
  - all element positions relative to the group centre and phases relative to the group Θ;
  - per-unit rates;
  - its owner tree;
  - its measured isolated rate;
  - its source path.
- *Isolation at both tree levels:* every C4 world feeds one level-2 world, and every level-2 harvest world feeds one level-3 world. Templates that do not fit are discarded (C5's `assign_templates` rule), so no two level-3 worlds share upstream randomness.

**Rates (the same fixture rule, one level up).** C5 gave each unit one rate ω_g ~ U[−δ₂, δ₂] for all its members. That is an exact symmetry, because the unit is the accepted resonator in a rotating frame. C6 applies the rule to whole level-2 groups:
- every element rate in group G is shifted by one constant, so the group's measured isolated rate becomes ω_G ~ U[−δ₃, δ₃];
- the group's insides are untouched;
- δ₃ = δ₂ × C₂/C₃, the same dimensionless spread (C is defined below). The non-vacuity bound then repeats exactly: median |Δω| × window = 0.586 × δ₂ × 30 C₂ ≈ 1.7 rad ≥ 1 rad.

**Assembly: contact placement, the same rule at both levels.** The rule follows from the coupling law.
- *Why disk placement cannot work at level 3:*
  - The C4 law couples each element only to its k = 8 nearest neighbours within radius 3.
  - A boundary element of a level-2 group (about 40 elements) almost always finds its 8 nearest neighbours inside its own group.
  - So separated groups do not feel each other at all, and they can couple only where they touch.
  - C5's units (6–16 elements) could still couple across a gap, which is why its disk placement worked one level down.
  - C5's disk radius was scaled by L, the spread of the part centres. That understates a composite's real extent, and at small spacings no placement exists.
  - The development pilot (§3b) confirms both points.
- *The rule:*
  - A level-n world holds M = 5 parts of level n−1. Each part gets a random rotation and a random global phase.
  - The first part sits at the origin.
  - Each further part approaches the centroid of the parts already placed, from a uniformly random direction, and stops at the first position where some element pair across parts is at the element contact gap of 0.6. The 0.6 gap is element-scale and is not scaled by level, because it is a property of the element law.
- *Scale-free at both levels:* every part starts touching the cluster, and the dynamics decide what locks, merges or drifts.
- *A declared change from C5:* C5 used disk placement at level 2. Transition 2 in C6 uses contact placement, so it is a new measurement, not a replication.
- *Size:* a level-3 world holds about 120–300 elements (pilot: 145–242, median about 190).
- *M:* a world fixture, not part of the composition rule. M = 5 at both levels; M = 7 (about 350 elements) exceeds the compute budget (§10).
- *No authored grouping.*

**Coupling = the C4 law, unchanged.** The full model is `c4_model.simulate` on all elements. The standard's edge birth and death protocol maps onto existing parts:
- *Element edges* attach and detach through the C4 k-nearest-within-radius rule.
- *Unit-level edges* at every level n are the detector's link rule: close by the relative link factor, and locked, which is a mode-compatibility test.
- *Persistence* comes from the membership Jaccard over the window, and *release* from the recovery test.

The capture region is relative (link factor × median spacing), and the persistence window scales with time. That is the standard's "normalized by L and timescale", applied identically at levels 2 and 3. In the coarse model, port links form and break by the same C4 rule.

**Time normalization (C5 owner decision D2, generalized step-exactly).**
- τ_n is the e-folding time of the level-n inter-part pattern after a part-phase kick.
- The cumulative factor is C_n = τ_n/τ₁, measured on C6 development worlds and **rounded to the 0.2 grid**. At n = 2 this is exactly C5's rule (C5 had C₂ = 3.2).
- Rounding the cumulative factor, not each ratio, keeps every scaled time a whole number of RK4 steps: the smallest is the 0.1 C sample interval, which is 5C steps. A per-level ratio T₃ rounded to 0.2 does not; for example T₃ = 3.2 gives 51.2 steps.
- T₃ = C₃/C₂ is reported.
- Level-n thresholds are `c5_detect.level2_thresholds(C4 thresholds, C_n)`. At n = 2 this is exactly C5's call.
- C₂ is re-measured under contact placement and the corrected criterion 6, not inherited.
- Final-world ratios are reported. A ratio outside [C/2, 2C] is a stated limitation and never changes a verdict.

## 3a. Normalization ledger (every quantity derived from invariant 1)

Invariant 1 is the governing rule: one rule at every level, normalized only by that level's own measured size and timescale. Every quantity in C6 is listed with the level whose units it is measured in. A check may not mix levels. Where a rule touches two levels, the ledger says how each side is scaled. The implementation's `same_rule_audit` reproduces this table from the code, and a contract fails on any quantity missing from it.

| Quantity | Measured on | Normalization |
|---|---|---|
| Detector window, frame interval, recovery time | the candidate's level n | × C_n |
| Frequency tolerance; effective-state frequency bound | level n | ÷ C_n |
| Shape CV, lock std, pattern tolerance, Jaccard thresholds | level n | dimensionless, unchanged |
| Link rule (relative spacing), kick position (fraction of spacing), kick phase | level n | relative or dimensionless, unchanged |
| **Criterion 6 dynamic validity of a level-k part** | **the part's own level k** | **windows of 30 C_k at interval C_k, consecutive across the parent window** |
| Criterion 6 geometric overlap | geometry, no time | area fraction 0.2, at every parent frame |
| Degenerate shape | the part's level | area ≤ 10⁻¹² L² |
| Rate spread of parts | level n | δ_n = δ₂ × C₂ / C_n (constant dimensionless spread) |
| G→M, M→G, excitation and τ windows; sample interval | level n | × C_n |
| Doses (s, RMS), pulse 0.5 rad, margin 0.01 rad | level n | dimensionless, unchanged |
| Push size | the excited part | 0.2 × its L |
| Element contact gap 0.6; C4 law (A, B, J, K, k = 8, radius 3, dt) | element scale | **not scaled**: the physics does not rescale (§13) |
| Placement | element scale | contact at the 0.6 gap (no level-scaled radius) |
| Hierarchy-specificity sub-part kick (RMS 0.3), pair e-folding | within-part pairs relax on level n−1 time; across-part pairs on level n time | dimensionless kick; sampled at 0.1 C_{n−1} (resolves the faster, within-part relocking on its own scale) over a window of 10 C_n (covers the slower, across-part relocking) |
| Effective-state position and size bounds | level n | fractions of L, unchanged |

## 3b. Development pilot (2026-10-02, owner-requested; not evidence)

The owner asked whether the open risks could be checked before registration.
- *What ran:* a development-only pilot, with scratch code outside the repository and pilot entropy 44444. That entropy is neither the C5 development nor the C6 development entropy, and no final entropy exists yet.
- *What it reused:* the frozen C4/C5 functions, applied at provisional C₃ = 9.6.
- *What it changed:* nothing was registered and no repository code was changed.
- *Records:* the raw records are to be committed with the design-gate artifact (N2).

**Level 1 → 2, C5 rules unchanged:**
- 2,400 C4 worlds gave 2,669 templates.
- 320 level-2 worlds gave FORMED 148 (0.46, Wilson [0.41, 0.52]), MERGED 52, DRIFTING 97, APART 4 and OTHER 19. This replicates C5's near-threshold formation on a larger sample.
- 140 of 148 accepted groups were re-accepted alone.
- τ₂ alone had median 4.8 (1 censored). The median isolated group rate was 0.0075. Median L₁ = 0.45 and L₂ = 0.67.

**Level 2 → 3, 24 worlds per placement:**
- *Disk placement* at C5's normalized radius gave 9/24 DRIFTING, with no coupling between separated groups. At spacing factors ≤ 0.6, no placement exists.
- *Contact placement* gave a locked candidate group of level-2 groups in **22/24** worlds. Level-3 locking does occur once groups touch.
- **0/24 formed** in both placements. Every candidate failed criterion 6, almost always because level-1 units inside the groups failed criteria 2–4 over the 288-unit level-3 window.
- *The cause is a rule defect, not the model.* Groups in drifting worlds that never touched anything also failed. Those same groups had passed when judged alone over the shorter level-2 window. This is the level-mixing defect corrected in §4, identified by the owner.
- **The pilot's level-3 formation rate is therefore void.** The design gate measures it again under the corrected rule.
- *Recovery:* criterion 5 failed in 13 of the 22 contact candidates. With the parts check corrected, recovery may become the binding criterion. Only the design gate can say.

**Cost:** formation plus detection took 66–249 s per level-3 world (median about 150 s) on one process, with 8 running in parallel. The harvest took 208 s for 2,400 C4 worlds and 362 s for 320 level-2 worlds, wall time on 8 processes. These measurements replace the earlier estimate in §10.

## 4. One detector, one promotion, one coupling (no `if level == …`)

**`detect_level(series, validity, thresholds_n, kick_runner)`** is called at n = 2 and n = 3. It reuses C5's frozen criteria:
- criteria 1–4: `c5_detect.candidates`, which calls the frozen C4 `components`, `locked_pairs` and `window_statistics`;
- criterion 5: `c5_detect.recovery` with `c5_detect.unit_kick`.

Contracts and audit:
- *Regression:* on the same development world states, the generic detector at n = 2 reproduces the frozen C5 detector exactly for criteria 1–5 and for the geometric part of criterion 6. The dynamic part of criterion 6 differs by design: it uses own-level windows, and the change is declared. Both values are stored, so the effect of the correction is visible.
- *Static:* no `c6_*` file branches on a level number.
- *Audit:* `same_rule_audit` records function identities and every threshold at both levels.

**Criterion 5 keeps the original group** (the C4 R003 rule). The original part set must be matched in the control future and in the kicked future, and the two matched groups must agree, each with Jaccard ≥ 0.9. Kicks are rigid on whole parts and leave their insides bit-identical.

**Criterion 6, stated once and applied recursively: parts alive and distinct, each judged on its own level's scale.** Each level-k part, tracked by its **original** member set and never re-matched, must satisfy three conditions:
- **Dynamic validity, on its own timescale.** The parent's window is split into consecutive, non-overlapping windows of the part's **own** level length, 30 C_k, sampled at the part's own frame interval C_k. The part must pass its own criteria 2–4, with its own level's thresholds, in **every** one of those windows. A trailing remainder shorter than 30 C_k is not scored.
- **Geometric distinctness, which has no timescale.** No other part's shape covers more than 0.2 of its shape's area at any parent frame.
- **Recursion.** A composite part satisfies criterion 6 for its own parts, each again on its own level's windows.

*Why per-window:* criteria 2–4 are fixed-amplitude tolerances (for example, pattern change ≤ 0.1 rad). Measured over a longer window, any slow, harmless drift accumulates beyond them. Judging a level-1 unit over a level-3 window (about 10× its own) mixes two levels in one rule and violates invariant 1. The first two drafts did exactly that. A real merger still fails through the geometric test, whatever the window.

*Consequences:*
- The owner records frames at the finest part level's interval (C₁ = 1 time unit) during every detection window. This is negligible extra storage.
- At level 3, every level-2 group is checked over windows of 30 C₂ and every level-1 unit inside it over windows of 30 C₁.
- *C5 inheritance:* C5 judged level-1 units over one level-2 window (3.2× their own). That made C5 stricter, never looser, so its accepted support stands. But some of C5's MERGED worlds may reflect this effect rather than real merging, and C6 does not reuse C5's MERGED counts as a merger rate.
- *A unit's shape:* the convex hull of its elements for a level-1 unit, and the union of its level-1 hulls for a composite. At level 2 this is exactly C5's rule. At level 3 it avoids false MERGED verdicts from the empty space inside the convex hull of a concave composite.
- *Area computation:* exact convex clipping at level 2. At level 3, an exact union-of-convex-pieces computation or a registered rasterization, with a contract bounding its error against exact clipping.
- *Degenerate shapes:* area ≤ 10⁻¹² L² fails (N3).

**Outcome per world**, the first that applies: FORMED, MERGED (a criterion-6 failure), DRIFTING (contact but no locked candidate), APART, OTHER.

**Promotion.** An accepted level-n candidate publishes exactly one level-n state through `c6_units.compose_state` (the `level_interface` gate). Publication is read-only.

## 5. Lower levels stay real; upward, downward and hierarchy paths

- **Alive and dynamic.** The full simulation always integrates every element. Promotion never deletes, freezes or replaces members (invariant 2). Coarse models are predictions scored against the full model and are never substituted into it. Recursive criterion 6 holds over the window. Two further measures for every accepted level-3 group are descriptive (`parts_in_situ`):
  - each level-2 part's own recovery **in place**: the level-2 kick and the level-2 recovery rule, applied inside the level-3 world;
  - τ₁ and τ₂ inside the level-3 world against their values alone.
- **Upward (`upward_transfer_l3`).** Rotate the phases of **one level-1 unit** inside one level-2 group by 0.5 rad. Measure the response of the **other level-2 groups'** published Θ: intact minus the same world with level-2 groups decoupled, where it is 0 by construction. Margin 0.01 rad. The disturbance must cross two levels.
- **Downward (`downward_effect_l3`).** Each level-2 group's port elements' phase offsets, relative to its own Θ, inside the level-3 group against decoupled; margin 0.01 rad. The same shift for level-1 ports (two levels down) is descriptive. The whole acts only through the element law.
- **Emergent transfer (`emergent_transfer_l3`).** Pulse a whole level-2 group's phase by 0.5 rad and measure the other groups' response, intact minus decoupled, margin 0.01 rad.
- **Hierarchy specificity (`hierarchy_specificity_l2`, `_l3`; one function).** It runs at both transitions and is the dynamical test that the middle level is real. It is cheap: one extra kicked run per group.
  - *The kick:* at transition n, kick every level-(n−2) sub-part of an accepted group rigidly in phase (zero mean, RMS 0.3). At n = 2 the sub-parts are elements; at n = 3 they are level-1 units.
  - *Pair relocking times:* τ_ij is the e-folding time of each sub-part pair's phase-difference deviation from the unkicked control. Values censored at the window count as the window, a lower bound.
  - *Score of a partition P of the sub-parts:* R(P) = median τ over pairs in different parts ÷ median τ over pairs in the same part.
  - *Comparison:* R(true partition) against the mean R of K = 20 seeded **contiguous** alternative partitions. They are grown over the sub-part contact graph, have the same size profile, and each alternative part mixes sub-parts of at least two true parts.
  - *World statistic:* R(true) − mean R(alternatives).
  - *Descriptive:* the partition recovered from relocking times alone (components of the pairs faster than the geometric mean of the within and across medians), compared with the true partition by adjusted Rand index.

## 6. Interventions, predictions and complete ablations

The same protocol applies at both transitions. Every run is paired with an unperturbed control from the same formed state s₀, and every ablation is matched on s₀. The world is the unit of analysis: its value is the mean over its accepted groups. CIs are bootstrap 95% (10,000 resamples). The doses are C5's, dimensionless and identical at both levels.

| Test | Intervention (parts' insides held bit-identical) | Registered prediction | Complete matched ablation |
|---|---|---|---|
| **G→M** | Scale each part's centroid offset from the group centroid by s (rigid moves). Both runs get the same zero-mean part-phase probe (RMS 0.3). | The inter-part pattern deviation **increases**. | `no_geometry_to_mode`: w = 1 and the phase topology frozen at s₀ (the effect is exactly 0 by construction) |
| **M→G** | Rotate each part's phases rigidly by a zero-mean kick of fixed RMS. | The peak radius of gyration of the part centroids **increases**. | `no_mode_to_geometry`: J = 0 (exactly 0) |
| **Dose-response** | G→M at s = 1.1 / 1.25 / 1.5; M→G at RMS 0.5 / 1.0 / 1.5. Each ladder is one controlled-size family, and any other dose is refused. | The means do not decrease, and the highest-minus-lowest per-world difference has CI > 0. | (intact) |
| **G→M channels** | Only w = 1, or only the frozen topology. | Descriptive. | — |
| **Upward, downward, emergent, hierarchy** | §5. | Above the margin; R(true) > R(alternatives). | Decoupling (0 by construction); alternative partitions |
| **Coarse vs full** | Held-out excitations on one part (seeded choice): a phase pulse of 0.5 rad and a radial push of 0.2 × its L. | §7. | — |

The primary doses are s = 1.25 and RMS 1.0. Single-channel ablations are decomposition only.

## 7. Full versus coarse at both transitions

- **Who reads what.** The transition-n coarse model is `c5_coarse.run`, unchanged and level-agnostic, given **only the published level-(n−1) states** of the group's parts.
  - At transition 3 it reads level-2 states and never level-1 states or elements: the standard's "an R₂ query reads R₁ effective states".
  - A contract checks the input type; a mutant passing level-1 states must be detected.
  - Port links form and break by the C4 neighbour rule.
- **Port variant (chosen once, before registration, by the coarse readiness check in §9; used at both levels).**
  - **V1:** C5's rule. Ports are the hull members; a composite's ports are the child ports on the hull of all child ports.
  - **V2:** ports are the hull members plus every member that has an active cross-part C4 neighbour at publication. This follows the standard's "derived from active lower boundary interactions" more literally. C5's hull vertices miss contact-face members that lie inside a flat hull edge.

  Both variants have zero fitted parameters.
- **Open-loop scoring.** The scored prediction never receives full-model states. The reopening protocol (invariant 8) runs alongside and is reported: invalid flags, reopens, and error on flagged versus unflagged excitations, which shows whether the validity bound carries information.
- **Baselines**, the same at both transitions, all required:
  1. no transfer;
  2. rigid transfer;
  3. relaxation to an equal share, with the group's own relaxation time **measured for the excited channel**: the phase e-folding after the probe for pulses, and the position e-folding of the scaled-geometry return in the s = 1.25 G→M run for pushes. Both measurements come from runs that already exist, and the calibration advantage is declared.
- **Scoring per excitation type (D4).** gain_{e,b} = error_b − error_coarse per world, for e ∈ {pulse, push} and each baseline b. The error is C5's response error over the non-excited parts: RMS wrapped phase error plus RMS position error over L. The receipt stores the phase and position parts separately.
- **Bounded predictive error,** operationally: at each transition, the coarse model is strictly better than every cheap baseline, including "nothing responds" and channel-matched measured-τ relaxation, for both excitation types. This is stricter than C5's averaged rule. The conjunction of six one-sided comparisons per transition only makes support harder to reach; it does not inflate it.
- **Descriptive only (no verdict; usefulness is C8):**
  - `coarse_error_decomposition`: a rigid-all-members reference (every member a port; not a coarse model) splits the error into rigidity error (full against rigid) and port-restriction error (rigid against coarse).
  - `coarse_depth`: at transition 3, the coarse model on level-2 states against a flat coarse model on all level-1 states of the same units.
  - Work counts, frequency error and recovery-time error.

## 8. Endpoints and verdict rules (every endpoint evaluated or listed in `not_run` with a reason)

The minimum for any inferential verdict is **10 formed worlds** at that level; below it, the endpoint is INCONCLUSIVE.

**Composition endpoints:**
- transition 2: `downward_effect_l2`, `emergent_transfer_l2`, `effective_state_l2`, `coarse_vs_full_l2`, `timescale_separation_l2`, `hierarchy_specificity_l2` (6);
- transition 3: the same six at level 3, plus `upward_transfer_l3` (7).

| Endpoint | Rule (rows in order) |
|---|---|
| `level1_pool` (gate) | Every used level-1 unit, alone with its rate, is re-detected by the frozen C4 detector. |
| `level2_pool` (gate) | Every used level-2 template, alone with its shifted rates, is re-detected by `detect_level` at n = 2 (the harvest filter, re-checked). |
| `harvest_isolation` (gate) | No C4 world feeds two level-2 worlds, and no level-2 harvest world feeds two level-3 worlds. Source paths are stored. |
| `same_rule_audit` (gate) | Level-n thresholds equal `level2_thresholds(C4, C_n)`. Detector, promotion, composition, coarse and hierarchy calls are the same function objects at both levels. The static no-level-branch check passes. C₂, C₃, every τ and the final measured ratios are recorded. |
| `numerical_checks` (gate) | C4's checks on an assembled level-3 world (RK4 order, switching dt error, equivariance under permutation, translation, rotation and global phase), plus unit and group relabelling, plus exact decoupling (each group alone equals its decoupled run within 10⁻⁹). |
| `level_interface` (gate, N1) | At both levels, exactly one published parent per accepted candidate **per world**, matched by unit set: no duplicates, omissions or swaps. Every numeric field finite. Ports and mode well-formed. S equal to the candidate's statistics. Digest derived from the children. Gate: not FAIL. |
| `not_independent_l2/_l3`, `not_a_clump_l2/_l3` (gates) | Decoupled continuations with imposed candidates (the intact candidates, or proximity-only components when none exist). With the assembled rates, rejection is expected by criterion 3; with rates shifted to 0, by criterion 5. **FAIL** if any candidate is accepted; **PASS** if at least one was tested and none was accepted; **NOT_TESTED** if none. Gate: all PASS. |
| `formation_l2`, `formation_l3` | Fraction of FORMED worlds, Wilson 95% CI. (1) **PASS** if the lower bound ≥ 0.5 and ≥ 10 worlds formed; (2) **FAIL** if the upper bound < 0.5; (3) **INCONCLUSIVE** otherwise (D3). |
| `formation_outcomes_l2/_l3` | Descriptive: outcome counts, per-criterion failures, the C4 component view and, at level 3, the level-2-detector union view. |
| `g_to_m_lN`, `m_to_g_lN` (N = 2, 3) | (1) **INCONCLUSIVE** if fewer than 10 formed worlds; (2) **FAIL** if the intact CI includes 0 or lies below it; (3) **PASS** if the complete-ablation CI includes 0 or its \|mean\| ≤ 0.2 × the intact mean; (4) **INCONCLUSIVE** otherwise. |
| `dose_response_lN` | Per direction: (1) **INCONCLUSIVE** if fewer than 10 worlds; (2) **PASS** if the means do not decrease and the highest-minus-lowest CI > 0; (3) **FAIL** if that CI < 0; (4) **INCONCLUSIVE** otherwise. The endpoint fails if either direction fails and passes only if both pass. |
| `downward_effect_lN`, `emergent_transfer_lN`, `upward_transfer_l3` | Margin 0.01 rad: (1) **INCONCLUSIVE** if fewer than 10 worlds; (2) **FAIL** if the CI upper bound < 0.01; (3) **PASS** if the CI lower bound > 0.01; (4) **INCONCLUSIVE** otherwise. |
| `effective_state_lN` | C5's bounds (position 0.25 L, size 0.05, frequency 0.01 / C_N). (1) **INCONCLUSIVE** if fewer than 10 formed worlds; (2) **PASS** if ≥ 90% of published parents meet every bound; (3) **FAIL** otherwise. |
| `coarse_vs_full_lN` | Six paired open-loop gains per world (2 excitation types × 3 baselines). (1) **INCONCLUSIVE** if fewer than 10 worlds; (2) **FAIL** if any gain CI upper bound < 0; (3) **PASS** if every gain CI lower bound > 0; (4) **INCONCLUSIVE** otherwise. Reopening, flags, the error split, frequency, recovery and work are reported, never scored. |
| `timescale_separation_lN` | Per world, the mean over groups of τ_N ÷ the mean τ_{N−1} of the group's own parts measured alone. Censored values are counted lower bounds. (1) **INCONCLUSIVE** if fewer than 10 worlds; (2) **FAIL** if the CI upper bound < 1; (3) **PASS** if the CI lower bound > 1; (4) **INCONCLUSIVE** otherwise. |
| `hierarchy_specificity_lN` | Per world, R(true) − mean R(alternatives). Groups with no valid alternative partition are NOT_TESTED and counted. (1) **INCONCLUSIVE** if fewer than 10 tested worlds; (2) **FAIL** if the CI upper bound < 0; (3) **PASS** if the CI lower bound > 0; (4) **INCONCLUSIVE** otherwise. |
| `g_to_m_channels_l3`, `parts_alive_l3`, `parts_in_situ_l3` | Descriptive: single-channel effects; recursive criterion-6 values for every part of **every** candidate; in-place recovery and τ inside against alone. |
| `interface_fidelity`, `coarse_error_decomposition`, `coarse_depth` | Descriptive (§3, §7). Raw values are stored. |

**Truth tables.** Registered in the manifest as ordered rows; the code implements them row by row, and a test enumerates every input combination.

| Hypothesis | Row | Condition | Verdict |
|---|---|---|---|
| H-M level N (N = 2, 3) | 1 | any of `g_to_m_lN`, `m_to_g_lN`, `dose_response_lN` = FAIL | NOT_SUPPORTED |
| | 2 | `formation_lN` = PASS and all three = PASS | SUPPORTED_WITHIN_SCOPE |
| | 3 | otherwise | INCONCLUSIVE |
| H-C transition N | 1 | `formation_lN` Wilson upper bound < 0.25 (composition clearly does not occur under this rule) | NOT_SUPPORTED |
| | 2 | any composition endpoint of transition N = FAIL | NOT_SUPPORTED |
| | 3 | H-M level N = SUPPORTED_WITHIN_SCOPE and every composition endpoint of transition N = PASS | SUPPORTED_WITHIN_SCOPE |
| | 4 | otherwise | INCONCLUSIVE |
| **H-C (recursive, the central gate)** | 1 | either transition = NOT_SUPPORTED | NOT_SUPPORTED |
| | 2 | both transitions = SUPPORTED_WITHIN_SCOPE | SUPPORTED_WITHIN_SCOPE |
| | 3 | otherwise | INCONCLUSIVE |

- **Formation and H-M.** Too few groups is no evidence about coupling (C4 R003), so formation failure alone never makes H-M NOT_SUPPORTED.
- **Formation and H-C.** Composition that clearly does not happen is the H-C answer for this rule (C5 D3, applied at both levels).
- **Gates.** A gate failure means the run is not REVIEW_READY, whatever the verdicts.

## 9. Design gate, formation plan, sample sizes and seeds

**Formation: what is known, and how it is raised without tuning.**
- *What the data show:*
  - C5's 17/30 has a Wilson interval of [0.39, 0.73], and the pilot's 148/320 has [0.41, 0.52]. Level-2 formation under C5's rules is about 0.46.
  - Rate spread is not the lever: C5 formed 16, 17 and 16 at 0.5δ, δ and 2δ.
  - The losses are DRIFTING and MERGED.
- *Two corrections raise formation:* the rules derived from invariant 1 and the coupling law, not a search over settings.
  1. **Criterion 6 on each part's own timescale (§4).** The old rule judged parts over a window longer than their own (3.2× at level 2, about 10× at level 3). Fixed-amplitude tolerances then reject harmless slow drift, so some of the MERGED losses may come from this, and at level 3 all of them did in the pilot.
  2. **Contact placement (§3).** A composite couples only where it touches, so every part starts in contact. Disk placement left 9/24 pilot worlds DRIFTING with no coupling at all.
- *These are not tuning:* each is fixed by the principle before any formation number under it is seen. Neither has a free parameter to adjust.
- *Whether they reach the target is unknown.* The design gate measures it once, and there is no grid to search.

**Design gate (development entropy only, before registration; `tools/c6_design_gate.py`).** Every step writes raw per-world values to a committed artifact pinned by hash in the manifest (N2). Development outcomes are settings, not evidence.
1. **Formation.**
   - 30 development worlds at level 2 and 30 at level 3, with contact placement and the corrected criterion 6.
   - Target: formation ≥ 0.75 at both levels. Below 0.75 at either level means stop and report, with the per-criterion failure counts.
   - Provisional C₃ = 9.6. If the measured C₃ is outside [4.8, 19.2], level-3 formation is re-run once at the measured value.
2. **Timescales.** C₂ and C₃ are measured under contact placement, and τ₃ must be finite (groups in contact couple; the pilot's locked candidates in 22/24 worlds suggest they do).
3. **Interface fidelity.** C5's and C6's composition rules are compared on development parents: rate error against the observed rate, and coarse cross-link counts against the element-level census. C6's rule must be at least as faithful on both measures.
4. **Coarse readiness.** At both transitions, on development groups, compute the six gains for V1 and V2 and the error decomposition.
   - The variant with the larger worst-cell mean gain at the worse transition is selected.
   - It is used only if that worst-cell mean gain is > 0 at both transitions.
5. **Overlap calibration.** Record union-of-hulls overlap for touching accepted groups at level 3. Intact touching groups above 0.2 means stop.
6. **Runtime projection** from measured per-world costs (§10).

If any check fails, the implementer **stops and reports to the owner before registration**. The law, the thresholds and the margins are never changed to make composition or prediction succeed. A failure here is itself a finding. The owner can then:
- run the panel anyway, to record the expected negative with full evidence;
- write a decision record instead;
- authorize a redesign in a new proposal: for example M = 6–7 with a longer panel, or a new coarse law.

**Final sample sizes.**
- **Transition-2 evidence:** n₂ = 40 fresh level-2 worlds, disjoint from the harvest worlds, with the full protocol.
- **Transition-3 evidence:** n₃ = 40 fresh level-3 worlds.
- **Why 40:**
  - Under D3, PASS needs at least 27/40 formed (Wilson lower bound 0.52; 26/40 gives 0.495).
  - At a true rate of 0.75 that happens with probability 0.90; at 0.65, 0.44.
  - At 0.75, about 30 formed worlds per level feed every inferential endpoint, three times the minimum.
  - If the runtime projection forces n₃ = 30, PASS needs at least 21/30 (probability 0.80 at 0.75), decided before registration.
- **Harvest, about:**
  - 400 level-2 harvest worlds (40 × 5 × 1.5 / 0.75);
  - 3,300 C4 worlds (C5's 7.5 per level-2 world), including those for the transition-2 worlds.

**Seeds.**
- Development entropy: 33333, which is new; C5's 22222 is not reused.
- Final entropy: drawn with `secrets.randbits(63)` at registration. Disjoint SeedSequence purposes cover C4 harvest, level-2 harvest, transition-2 worlds, level-3 worlds and every kick, probe, excitation and alternative partition.
- Final worlds and all their upstream harvest worlds are never simulated before the recorded panel. Smoke and tests use development entropy only. The final excitations are held out: development excitations are used only in the readiness check.

**Receipt detail.** Everything below is stored, and nothing is reduced to a mean only:
- *Per level-1 unit and level-2 group:* size, rates, criterion-6 values, ports and every τ.
- *Per candidate:* all six criteria and the three recovery scores.
- *Per published parent:* its state, its children's states, the C5-rule state and its fidelity values.
- *Per world, condition and dose:* the effects.
- *Per excitation:* full, coarse, flat-coarse, rigid-reference and baseline errors, with phase and position parts and flags.
- *Per group:* R(true), every R(alternative) and the pair τ's.
- *Per world:* source paths.

## 10. Engineering, reuse and runtime

**Reused read-only.** These are frozen files, imported and never edited:
- `c4_model`: `simulate`, `neighbors`, `Params`, `ABLATIONS`, `Batch`, `wrap`. The full model is exactly `simulate`.
- `c4_detect`: `detect` (level-1 harvest), `components`, `locked_pairs`, `window_statistics`, `kick`, `best_match`, `jaccard`, `radius_of_gyration`, `pair_differences`, `circular_mean`, `nn_spacing`, `criteria_checks`, `_convex_hull`.
- `c4_experiment`: `initial_worlds`, `form`, `detect_worlds`, `model_params`, `bootstrap_ci`, `wilson`, `causality_verdict`, `dose_response_verdict`, `gm_statistic`, `mg_statistic`, `summarize`.
- `c5_units`: `harvest`, `resonator_state`, `unit_positions`, `unit_phases`, `polygon_area`, `clip_convex`, `member_digest`, and `compose_state` (fidelity comparison only).
- `c5_detect`: `level2_thresholds` (called with C_n), `candidates`, `imposed`, `recovery`, `unit_kick`, `criteria_checks`.
- `c5_compose`: `pad`, `scale_units`, `rotate_units`, `shift_units`, `unit_kick`, `decouple_offsets`, used with labels at the right level.
- `c5_coarse`: `run`, `CoarseState`, `links`, `rhs`. These are level-agnostic and used at both transitions.
- `c5_experiment`: `assign_templates`, `efold`, `relaxation_prediction`, `response_error`, `margin_verdict`, `separation_verdict`, `control_verdict`, `mg_dose_rms`.

`milestones/c6.json` lists the C4 and C5 files and both manifests as dependencies.

**New files.**
- `geomind/c6_levels.py`: owner tree, per-frame published series, `detect_level`, recursive criterion 6, threshold scaling and the hierarchy-specificity statistic.
- `geomind/c6_units.py`: the corrected `compose_state`, isolated-rate measurement, port variants, level-2 harvest with filter and source paths, and the N1 validator.
- `geomind/c6_compose.py`: level-n assembly with internal rates kept and the rotating-frame offset.
- `geomind/c6_experiment.py`: one transition protocol called at n = 2 and n = 3, evaluation and truth tables.
- `geomind/run_c6.py`: the runner, which calls `check("c6", "panel")` itself.
- `tests/test_c6.py`, `tools/c6_mutants.py`, `tools/c6_design_gate.py`.
- `experiments/c6_manifest.json` and `milestones/c6.json`, registered before any final-seed run.

**Focused contracts** (fast, synthetic or development fixtures):
- *Same rule:*
  - the n = 2 regression against C5's detector;
  - the threshold scaling;
  - the static no-level-branch check;
  - `compose_state` has the same shape at both levels;
  - the isolated rate of a level-1 unit equals ω_g;
  - every scaled time is a whole number of steps.
- *Rigid operations:* rigid moves and rotations leave insides bit-identical at both levels.
- *Decoupling and ablations:* decoupling is exact and has no cross-group neighbour; each ablation removes its pathway.
- *Criterion 6, each case with a positive control:*
  - a merged level-3 pair;
  - a broken level-1 unit inside an intact group;
  - collinear and degenerate units;
  - concave composites that touch without interpenetrating, which must pass;
  - crossing hexagons (C5 F2).
- *Hierarchy specificity:*
  - a synthetic two-timescale fixture where R(true) > R(alternatives);
  - a flat fixture where R(true) ≈ R(alternatives);
  - alternative partitions are contiguous, keep the size profile and mix true parts.
- *Information boundary:* the detector and the level-3 coarse model never receive member lists, rates or labels.
- *N1 cases:* duplicate, omitted and swapped publications, NaN fields, and empty mode or S are rejected.
- *Isolation:* the reviewer's split case at both tree levels.
- *Scoring:* open-loop scoring has no reopen callback; gains are per excitation type with channel-matched τ.
- *Rules:* truth-table enumeration, and every endpoint in the coverage.

**Mutants** (`tools/c6_mutants.py`), each of which must be detected by the tests:
- *Same-rule breaks:* C₃ not applied; a per-level ratio rounded instead of the cumulative factor; a level branch.
- *Criterion 6:* not recursive; convex hull instead of the union; degenerate shapes passing.
- *Publication (N1):* a global publication count; NaN fields accepted.
- *Composition:* the size-weighted natural rate; capacities not folded.
- *Coarse model and scoring:* reading level-1 states at level 3; scoring with reopening; pulse and push averaged; the push baseline using the phase τ; the relaxation τ taken from the wrong level.
- *Hierarchy test:* alternative partitions that are not contiguous; the true partition included among the alternatives.
- *Controls and harvest:* recovery ignoring the original group; the decoupled control leaking links; a harvest source shared across worlds; the harvest filter skipped.
- *Doses:* a mixed dose family.
- *Verdicts:* formation by point estimate; H-C ignoring one transition; a margin ignored.

**Runtime estimate.** Basis:
- *Development pilot (§3b), measured:*
  - formation plus detection per level-3 world (about 160 level-3 time units at C₃ = 9.6, N = 145–242) took 66–249 s, median about 150 s, per process with 8 running in parallel;
  - harvest took 208 s for 2,400 C4 worlds and 362 s for 320 level-2 worlds, wall time on 8 processes.
- *Earlier step benchmark:* 0.24 ms per world-step at N = 55 and 2.3–3.1 ms at N = 200–250. It was a few seconds on random arrays, run before approval although the owner had asked that nothing be run, and is disclosed here.

| Stage | Estimate (from the pilot's measured costs) |
|---|---|
| One formed level-3 world | About 570 level-3 time units: formation 100, recovery 60, two controls with their recovery runs 180, G→M 50, M→G and excitations 100, upward 20, hierarchy 10, in-place checks 10, isolated rates 40. About 3.6× the measured 160-unit cost: **about 9 min** per process. An unformed world (about 340 units) takes about 5 min. |
| 40 level-3 worlds at 75% formation | about 5.4 process-hours, so **about 40–45 min on 8 processes** |
| Harvest (about 3,300 C4 and 400 level-2 worlds, with filter runs) and 40 transition-2 worlds | about 15–20 min wall |
| **Recorded panel, 8 processes** | **≈ 1–1.5 h** at C₃ ≈ 10; **≈ 2 h** at C₃ ≈ 16 |
| Tests / smoke (1 development level-3 world, small harvest) / mutation probe | < 2 min / ≈ 10–15 min / ≈ 2–5 min |
| Design gate (development only, before registration) | ≈ 45–60 min |

M = 7 would mean about 350 elements, roughly 3.4× the cost per step, so it is not proposed. If the design gate's projection exceeds **3 h**, the implementer returns to the owner before registering. The options would be:
- n₃ = 30;
- dropping the level-3 decomposition ablations;
- a faster neighbour selection in a new file, contract-tested bit-identical to `c4_model.neighbors` (argpartition, then an exact (distance, index) sort, with a fallback on boundary ties); its gain is unmeasured;
- a C++ backend.

**C++ backend: not proposed.** It would raise G10: the toolchain is unpinned, and the binary and compiler would need to be recorded or locked. libm `exp`, `sin` and `cos` would not be bit-identical to NumPy, and neighbour switching makes long trajectories diverge, so an equivalence protocol would be needed, not only a tolerance. That is a separate owner decision.

**Frozen environment.** `pyproject.toml` and `uv.lock` are frozen (Python 3.9, NumPy 2.0.2, pytest 8.4.2). That rules out:
- SciPy, whose KD-trees would cut neighbour search but would change frozen files and tie order;
- Numba;
- Hypothesis; property checks stay hand-written randomized loops.

None is proposed.

**Process.** Verify once, in order: `tools/verify.py --milestone c6 --output evidence/c6_r001`. Before the design gate and before the panel, tell the owner how long each will take and why. One independent review follows, by the other model family, capped at about 20 minutes. A design defect found before review means withdrawal through a decision record, and the next revision runs on fresh seeds.

## 11. C4/C5 lessons applied up front

| Lesson | Where C6 applies it |
|---|---|
| Ablations remove a pathway completely (C4 R001) | `no_geometry_to_mode` and J = 0 are primary; decoupling is literal; single channels are decomposition only. |
| Recovery and membership keep the original group (C4 R002 → R003) | Criterion 5 matches the original part set in both futures. Recursive criterion 6 tracks original member sets. In-place part recovery uses the same rule. |
| No verdict on fewer than 10 worlds | Every inferential endpoint, both levels. |
| One written rule, implemented row by row | Ordered truth tables with an enumeration test. |
| Non-vacuous controls with imposed candidates | Four decoupled controls with imposed candidates. Zero-by-construction effects carry a 0.01 rad margin. Hierarchy specificity compares against real alternatives, not empty ones. |
| Per-unit and per-group values in the receipt | §9 receipt detail. |
| Dose ladders are one controlled-size family (C5 R001) | Rigid scales and fixed-RMS kicks; any other dose is refused. |
| Open-loop coarse scoring (C5 R001) | No reopen callback in scored runs. |
| Area-based merger test, degenerate geometry covered (C5 F2, N3) | Union-of-hulls area; degenerate shapes fail; crossing, collinear and concave contracts. |
| One parent per candidate per world, finite fields (N1) | `level_interface` gate. |
| Keep raw calibration measurements (N2) | Committed design-gate artifact pinned by hash. |
| Harvest sources isolated (C5 F4) | Both tree levels; `harvest_isolation` gate. |
| Formation well clear of the threshold (C5 review qualifier) | 0.75 development target on 30 worlds per level; Wilson-lower-bound PASS; n = 40. |
| Test inherited capacities and natural rate first (C5 review) | Corrected composition; design-gate fidelity check; `interface_fidelity`. |
| An averaged score can hide a failing channel; a baseline must use the matching timescale (C5 receipt, found while drafting) | Per-excitation scoring, channel-matched τ, stored error parts, and a readiness check before the panel. |
| Every check is measured in its own level's units (invariant 1; the level-mixing criterion 6 of drafts 1–2, caught by the owner) | Normalization ledger (§3a), reproduced by `same_rule_audit` with a contract for completeness. Parts are judged on windows of their own level's length. |

## 12. Who implements and who reviews

Claude implemented C4 and C5, and Codex reviewed both. **The drafter recommends that Codex implement C6 and Claude review it.**
- C6 is mostly new generic code over frozen C4/C5 functions, so continuity matters less.
- Codex knows those functions closely from its reviews; it found C5's F1–F4 and N1–N3.
- Alternating roles keeps any one family from both building and judging the whole lane.
- The cost is that Codex has not used this repository's implementer workflow since C2; the pipeline and hooks are unchanged.

Because Claude drafted this proposal, the owner may ask Codex for a short critique of it before approval (optional).

## 13. What C6 cannot show

- **Two transitions only.** No claim about R₃ or arbitrary depth.
- **No dissolution or reform:** that is C7. **No usefulness, compression or efficiency:** that is C8. `coarse_depth`, the error decomposition and the work counts are descriptive.
- **Staged assembly.** Each level is formed separately and then placed together. C6 does not show two levels co-forming from one primitive soup.
- **Rate offsets are fixtures:** exact rotating-frame symmetries assigned by the experiment.
- **The physics does not rescale.** The element law's interaction range is fixed, so higher levels couple only through boundary contact. "Same rule" refers to detection, promotion, composition, coarse modelling and the time-scaled thresholds, not to a scale-free interaction.
- **Narrow scope:** one model, one parameter set, M = 5, level-1 units of 6–16 elements.
- **Development choices.** The port variant and the spacing are chosen on development data by pre-declared rules. The final evidence is fresh, but it is conditional on those choices.
- **Weak spots in the evidence:**
  - complete ablations vanish by construction; the evidence is the intact effects and their dose-response;
  - the downward effects test existence, not dose.
- **Statistical scope.** Inference is per world, conditional on fresh source-isolated harvests.
- **Not novel.** Hierarchical synchrony and oscillator coarse-graining are known [S1–S3, S6, S7].

## Sources

- **[S1]** Arenas, Díaz-Guilera and Pérez-Vicente, *Synchronization reveals topological scales in complex networks*, PRL 96, 114102 (2006). [arXiv:cond-mat/0511730](https://arxiv.org/abs/cond-mat/0511730). Communities lock first; locking times reveal the levels.
- **[S2]** Skardal and Restrepo, *Hierarchical synchrony of phase oscillators in modular networks*, PRE 85, 016208 (2012). [arXiv:1111.0921](https://arxiv.org/abs/1111.0921).
- **[S3]** Ott and Antonsen, *Low dimensional behavior of large systems of globally coupled oscillators*, Chaos 18, 037113 (2008). [arXiv:0806.0004](https://arxiv.org/abs/0806.0004).
- **[S4]** Lee et al., *Collective steady-state patterns of swarmalators with finite-cutoff interaction distance* (2021). [arXiv:2103.11584](https://arxiv.org/abs/2103.11584).
- **[S5]** Sar and Ghosh, *Dynamics of swarmalators: a pedagogical review* (2022). [arXiv:2208.14803](https://arxiv.org/abs/2208.14803).
- **[S6]** Villegas, Moretti and Muñoz, *Frustrated hierarchical synchronization and emergent complexity in the human connectome network*, Sci. Rep. 4, 5990 (2014). [arXiv:1402.5289](https://arxiv.org/abs/1402.5289).
- **[S7]** Gfeller and De Los Rios, *Spectral coarse graining and synchronization in oscillator networks*, PRL 100, 174104 (2008). [arXiv:0708.2055](https://arxiv.org/abs/0708.2055).
- **[R3]** in the standard: O'Keeffe, Hong and Strogatz, *Oscillators that sync and swarm* (2017).

## Decisions for the owner (with the drafter's recommendation)

1. **D1 — Approval. Recommended: approve as written.**
2. **D2 — Corrected composition rule** (measured isolated rate, sibling-folded capacities, one function at both promotions). **Recommended: accept.**
3. **D3 — Formation rule:** PASS on the Wilson lower bound ≥ 0.5, FAIL on the upper bound < 0.5, INCONCLUSIVE otherwise; n = 40 per level; development target 0.75. **Recommended: accept.** The alternative, C5's point-estimate rule, leaves the C5 qualifier unresolved.
4. **D4 — Predictive gate:** score pulse and push separately against three baselines with channel-matched τ, after a development coarse readiness check that can stop the work before the panel. **Recommended: accept.** The alternative, C5's average, would let a phase-only success hide a position failure.
5. **D5 — Roles. Recommended: Codex implements and Claude reviews** (§12). Optional: a short Codex critique of this proposal before approval.
6. **D6 — Compute. Recommended: NumPy with 8 processes and no C++ backend.** From the pilot's measured costs, the panel takes about 1–2 h and the design gate about 1 h; a projection above 3 h comes back to the owner.

## Self-audit of the first draft (2026-10-02, owner-requested)

The first draft (commit e594e58) was rechecked against the standard, the frozen code and the C5 receipt. Changes:

1. **Time grid (high).** Rounding T₃ to 0.2 is not step-exact: the 0.1 C sample interval would be 51.2 steps at T₃ = 3.2. Now the cumulative factor C_n is rounded to 0.2, which equals C5's rule at n = 2. The draft also inherited T₂ in §3 while re-measuring it in §9; C₂ is now re-measured under C6's settings.
2. **Coarse test predetermined (high).**
   - The strict per-excitation rule combined with C5's unchanged port law would very likely have failed on pushes for a known reason, after a multi-hour panel.
   - The push relaxation baseline used a phase timescale.
   - Added: channel-matched τ, stored error parts, the error decomposition, the pre-declared V1/V2 port variants, and a development readiness check that stops before the panel.
3. **Partition test (high).** The static wrong-partition control was nearly vacuous, because fake parts that mix groups fail on geometry alone. Conversely, contiguous fake parts in a fully locked group could pass criteria 1–6. It is replaced by the dynamical hierarchy-specificity statistic at both transitions.
4. **Runtime (medium).** The draft missed the controls' recovery runs, isolated-rate runs and in-place checks. The panel is about 2.5–3 h, not 1.5. M = 7 (about 350 elements) is removed from the grid as over budget.
5. **Design-gate power (medium).** 10 development level-3 worlds cannot support a 0.75 selection (Wilson [0.49, 0.94] for 8/10). Now 30 worlds per level, with selection by the best minimum across levels and the winner's curse noted.
6. **Harvest filter (medium).** Re-acceptance alone is now a label-free harvest filter, so the `level2_pool` gate cannot fail on groups that only held together with non-members.
7. **Edge protocol (low).** The standard's attach, persist and release rule is mapped explicitly onto the C4 neighbour rule and the detector's link and persistence tests.
8. **In-place parts (low).** In-place recovery and τ inside against alone are added as descriptive endpoints.
9. **Combined comparisons (low).** A note states that the conjunction of comparisons only makes support harder to reach.
10. **Process (disclosure).** The few-second step benchmark was run before approval, although the owner had asked that nothing be run. It touched no seeds or evidence; it is disclosed here.

## Second self-audit (2026-10-02, after the owner's review of the pilot)

1. **Criterion 6 mixed levels (high; caught by the owner, not the drafter).**
   - *The defect:* drafts 1 and 2 judged each part's fixed-amplitude criteria 2–4 over the parent's window, about 10× the part's own at level 3. That violates invariant 1, the governing rule.
   - *The fix:* parts are now judged on consecutive windows of their own level's length (§4). Every quantity is derived and listed in the normalization ledger (§3a).
   - *What went wrong in drafting:* the drafter scaled thresholds by level but never derived each check's window from the principle. The first self-audit compared rules with the standard's wording instead of auditing units and timescales.
2. **Placement (high).**
   - *The defect:* disk placement scaled by L understates a composite's extent. It also cannot couple level-2 groups at all, because the k = 8 nearest-neighbour rule hides separated composites from each other. That follows from the law; the pilot confirmed it.
   - *The fix:* contact placement at the element gap, at both levels (§3). The spacing grid is removed.
3. **Formation plan (medium).** The grid search is replaced by the two principle-derived corrections and a single development measurement, which stops if the target is not met (§9). Item 5 of the first self-audit is superseded.
4. **Hierarchy-specificity sampling (low).** Within-part pairs are now sampled on their own level's interval (§3a).
5. **Runtime (medium).** The estimate was rebased on the pilot's measured costs: panel about 1–2 h, design gate about 1 h.
6. **Process (disclosure).** The pilot ran at the owner's request. Its level-3 formation result (0/24) was produced under the defective criterion 6 and is void. The drafter first proposed further diagnostic runs where reasoning from the rule sufficed; that request was declined.

