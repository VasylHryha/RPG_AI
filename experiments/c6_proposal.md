# C6 proposal: recursive composition R₀ → R₁ → R₂ with the same rule (DRAFT, not approved)

Status: **PROPOSED**, awaiting owner approval. Nothing is registered: there is no `experiments/c6_manifest.json`, `milestones/c6.json` or C6 code, and nothing has been run. Authority: `GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md` (C6, the recursive unit interface, the ten recursive-resonator invariants, §5–7). Builds on C4 R003 and C5 R003, both independently accepted (`evidence/c4_r003_review_codex/INDEPENDENT_REVIEW.md`, `evidence/c5_r003_review_codex/INDEPENDENT_REVIEW.md`). Format follows `experiments/c5_proposal.md`.

**Level names.** Level 0 is a primitive element. Level 1 is an accepted C4 resonator (the standard's R₀). Level 2 is a C5 composite (R₁). Level 3 is the C6 composite (R₂). "Transition 1" is level 1 → 2 and "transition 2" is level 2 → 3.

## 1. The bounded question

> Take accepted level-2 resonators (groups of C4 resonators) and let them interact only through the unchanged C4 element law. Apply the **same** detector, promotion and composition functions that turn level-1 units into level-2 resonators, with thresholds rescaled only by measured size and timescale. Does a level-3 resonator form? That means a persistent, recovering, frequency-locked group of level-2 units in which every level-2 unit, and every level-1 unit inside it, stays a live, distinct resonator of its own level. Does the level-3 mode depend causally on level-2 geometry and the reverse, with each effect vanishing under its complete matched ablation? Do disturbances travel up from level 1 to level 3, and does level 3 constrain level-2 boundaries downward? Does a coarse model that reads only the published level-2 states predict held-out responses with bounded error, better than strong cheap baselines, and does the same hold again at transition 1?

Hypotheses:
- **H-C (the standard's central gate):** two successive transitions (1 → 2 and 2 → 3) under one composition rule, each with a valid effective state and bounded predictive error. C6 re-measures transition 1 on fresh worlds under the same rule. C5's transition 1 was INCONCLUSIVE, and the H-C gate needs both transitions in one experiment.
- **H-M at level 3** (whole ↔ parts, one level up), and H-M at level 2 replicated on fresh worlds.

**The cheap explanations C6 must rule out.**
1. **"Level 3" is one bigger level-2 group.** Units from different level-2 groups might simply form one large level-2 resonator, so the middle level would be bookkeeping. Three checks rule this out:
   - *Criterion 6, now recursive (§4):* every level-2 part stays a valid, distinct level-2 unit, and so does every level-1 unit inside it.
   - *`timescale_separation_l3`:* relaxation between groups must be slower than relaxation between units inside a group (τ₃/τ₂ > 1). One large flat group has no such separation.
   - *A disclosure:* the level-2 detector is run on the level-3 world's level-1 units, and the receipt reports whether it accepts the union as a single level-2 resonator. C5 disclosed the C4 component view the same way.
2. **A dendrogram or connected-component tree.** Any nested clustering of positions at two distance thresholds yields a tree. C6 requires dynamics at every level: locking, recovery after a kick, two-way causality with complete ablations, dose-response, upward and downward transfer, and timescale separation. It also requires `partition_specificity_l3`: if the same level-1 units are re-partitioned into fake level-2 units that mix real groups, the level-3 detector must reject them. A static tree passes none of these.
3. **A different solver or threshold per level.** There is one generic level-n detector, one promotion function and one coupling law. Level-n thresholds are the level-(n−1) thresholds passed through the same scaling function (`c5_detect.level2_thresholds`, applied again with T₃). A static contract forbids level branches, and the `same_rule_audit` gate records function identities and every threshold at each level.
4. **Trivial lock and clump of clumps** (as in C5). Decoupled controls with drifting rates must fail through mode lock, and controls with static rates must fail through recovery. Both controls receive imposed candidates, so they cannot pass empty.
5. **"The coarse state is just one number."** A relaxation baseline that uses the group's own measured relaxation time is the strongest cheap predictor. The coarse model must beat it at both transitions, for each excitation type separately (§7).

These dynamics are not new. Kuramoto oscillators on hierarchical modular networks synchronize level by level, and frustrated hierarchical synchronization appears at many scales [S1, S2, S6]. Coarse-graining oscillator networks while preserving synchronization is an established method [S7]. Locked populations reduce to a few variables [S3]. Finite-range swarmalators form separate groups [S4, S5]. C6 is a mechanism probe of the R4 recursion rule, not a novelty claim.

## 2. What C5 leaves open, and what C6 takes from it

| Input from C5 | Consequence for C6 |
|---|---|
| Level-2 formation was 15, 13 and then 17 of 30 across R001–R003, near the 0.5 threshold. No formation rate above 50% is established. | Formation must be well clear of its threshold. A development-only design gate with a pre-declared selection rule targets ≥ 0.75 at both levels. The registered PASS rule uses the Wilson lower bound (§9, D3). |
| The coarse law did not beat relaxation with a measured τ₂ (+0.008, CI [−0.004, 0.019]). | A descriptive split of the accepted R003 receipt, made while drafting, shows that the mean hid two different results. On **phase pulses**, the port law beats relaxation in 16/17 groups (mean gain +0.033) and beats "no transfer" in 17/17. On **radial pushes**, it beats "no transfer" in only 4/17 (mean −0.017), so it predicts the other units' response worse than "nothing moves". C6 therefore scores each excitation type separately (§7, D4). This descriptive split does not change C5's recorded verdicts. |
| C5 review: inherited port capacities omit sibling contacts, and the size-weighted natural rate is declared, not measured. The largest published-versus-measured rate gap was 0.0088 against a rate spread of 0.03. | At level 3 the frequency tolerance is about 10× tighter, so these approximations would matter. C6 uses one corrected composition rule at both promotions (§3) and measures how faithful both versions are (`interface_fidelity`). The design gate tests this before anything relies on it. |
| N1: publication was checked by global counts; non-finite fields passed. | `level_interface` gate: exactly one parent per accepted candidate per world, keyed by the candidate's unit set; all numeric fields finite; port and mode structure valid; S equal to the candidate's statistics. |
| N2: the overlap calibration lacked its raw measurements. | The design gate commits per-world raw values for every calibrated quantity, and the manifest pins that artifact by hash. |
| N3: zero-area hulls gave overlap 0 and passed. | A degenerate shape (area ≤ 10⁻¹² L²) cannot certify distinctness, so criterion 6 fails for it. A contract covers collinear units. |

## 3. Units at every level, the composition rule and the level-3 world

**One owner tree.** The evaluator-side owner keeps three labels per element: element → level-1 unit → level-2 group. Member lists stay owner-private at every level. Upper levels see only published `ResonatorState`s (the C5 field set: level, X, L, Θ, Ω, natural rate, mode signature, boundary ports, size, S, member digest).

**Publication at every level.**
- *Level-1 states:* `c5_units.resonator_state`, unchanged.
- *Level-n states (n ≥ 2):* one new function, `c6_units.compose_state`, used for **both** promotions. It equals C5's `compose_state` except for two corrections from the C5 review:
  1. **Natural rate = measured isolated rate.** The owner runs the parent alone (decoupled from everything else, over its own level's window) and publishes its measured collective rate. At level 1 this rule gives exactly ω_g (the rotating-frame symmetry), and a contract checks this, so the rule is the same at every level. It replaces C5's size-weighted mean of the children's rates.
  2. **Port capacity includes sibling contacts.** A parent port's capacity list is the k smallest of its child's own-neighbour distances together with its distances to the ports of the parent's other children. All of these come from published child states. C5 dropped the sibling contacts that become internal on promotion. Non-port sibling members remain invisible, which is a declared approximation.

  C5's `compose_state` is also computed for every accepted parent and reported, but never used for a decision (`interface_fidelity`).
- *Per-frame series for detection:* the owner computes the level-(n−1) X and Θ in every frame from the published rule: X is the unweighted centroid of the child centroids, and Θ is the circular mean of the child phases, unwrapped over frames. The detector receives only these series and the owner-computed validity.

**Harvest (label-free, staged, source-isolated).**
- *Level 1:* fresh C4 identical-arm worlds run with the frozen C4 code, as in C5 (templates of 6–16 members, each used once).
- *Level 2:* fresh level-2 harvest worlds are assembled from those templates and run through the generic detector at n = 2. Every accepted level-2 group becomes a template, which records:
  - all its elements' positions relative to the group centre and phases relative to the group Θ;
  - its per-unit rates;
  - its owner tree;
  - its measured isolated rate;
  - its source path (C4 worlds, level-2 world).
- *Isolation at both tree levels:* every C4 world feeds exactly one level-2 world, and every level-2 harvest world feeds exactly one level-3 world. Templates that do not fit are discarded (C5's `assign_templates` rule). No two level-3 worlds share upstream randomness.

**Rates at level 3 (the same fixture rule, one level up).** C5 gave each unit a rate ω_g ~ U[−δ₂, δ₂] shared by all its members. That is an exact symmetry, because the unit is the accepted resonator in a rotating frame. C6 applies the same rule to whole level-2 groups:
- every element rate in group G is shifted by one constant, so the group's measured isolated rate becomes ω_G ~ U[−δ₃, δ₃];
- the group's internal unit rates and dynamics are untouched;
- δ₃ = δ₂ / T₃, the same dimensionless spread. The non-vacuity bound then repeats exactly: median |Δω| × window = 0.586 × δ₂ × 30 T₂ ≈ 1.7 rad ≥ 1 rad.

**Assembly.**
- A level-n world holds M units of level n−1, with the same M at both levels. Each unit gets a random rotation and a random global phase.
- Centroids are drawn uniformly in a disk of radius R_n = s_R × R₂ × (median L_{n−1} / median L₁), with R₂ = 2.5 from C5 and s_R from the design grid (§9). The rejection rule keeps every cross-unit element pair at least 0.6 apart. That gap is element-scale: it prevents overlapping elements and is not a unit-scale quantity.
- At level 3 with M = 5, a world holds about 120–300 elements (median ≈ 185, from C5's accepted groups).
- No authored grouping: the dynamics and the label-free detector decide which units group.

**Coupling = the C4 law, unchanged, at every level.** The full model is `c4_model.simulate` on the union of all elements. Groups interact only where boundary elements fall inside one another's C4 neighbour sets, so couplings attach and detach under the same neighbour rule at every level. The interaction range stays at element scale (radius 3) at all levels; this is a property of this model (§13).

**Time normalization (owner decision D2 of C5, applied again).**
- T₂ = 3.2 is inherited from the C5 manifest (pinned by hash).
- T₃ = τ₃/τ₂, measured on development level-3 worlds and rounded to the 0.2 grid:
  - τ₂: e-folding time of a level-2 group's inter-unit pattern after a unit-phase kick, with the group alone;
  - τ₃: the same for the inter-group pattern after a group-phase kick, in the intact G→M control.
- The rounding keeps every scaled time a whole number of RK4 steps.
- Level-3 times are the C4 times × T₂ × T₃, and the frequency tolerance is divided by T₂ × T₃.
- The final-world ratios are reported. A ratio outside [T/2, 2T] is a stated limitation and never changes a verdict.

## 4. One detector, one promotion, one coupling (no `if level == …`)

**One function, called at n = 2 and n = 3.** `detect_level(series, validity, thresholds_n, kick_runner)` reuses C5's frozen criteria functions:
- criteria 1–4: `c5_detect.candidates`, which calls the frozen C4 `components`, `locked_pairs` and `window_statistics`;
- criterion 5: `c5_detect.recovery` with `c5_detect.unit_kick`.

The level-n thresholds are `level2_thresholds(thresholds_{n−1}, T_n)`, the frozen C5 function applied once more. Contracts and audit:
- *Regression:* on development worlds, the generic detector at n = 2 reproduces the frozen C5 detector's candidates and statistics exactly, except where the two declared changes apply (criterion 6's degenerate-shape rule; at level 2 the union-of-hulls rule equals C5's convex-hull rule).
- *Static:* no `c6_*` file compares a level number or branches on it.
- *Audit:* `same_rule_audit` records the function objects and every threshold at both levels.

**Criterion 5 keeps the original group** (the C4 R003 rule). The original set of level-(n−1) units must be matched in the control future and in the kicked future, and the two matched groups must agree, each with Jaccard ≥ 0.9. The kick is rigid: it moves and phase-rotates whole level-(n−1) units and leaves their insides bit-identical.

**Criterion 6, stated once and applied recursively: parts alive and distinct.** Each member unit, tracked by its **original** member set and never re-matched, must over the window:
- pass its own criteria 2–4 with its own level's thresholds;
- have no other unit's shape cover more than 0.2 of its shape's area;
- if it is itself a composite, satisfy criterion 6 for its own members.

At level 3 this checks every level-2 group and every level-1 unit inside it.

- *A unit's shape:* the convex hull of its elements for a level-1 unit, and the union of its level-1 hulls for a composite. At level 2 this is exactly C5's rule. At level 3 it avoids false MERGED verdicts caused by the convex hull of a concave composite, which encloses empty space where a neighbouring group can sit.
- *Area computation:* exact convex clipping at level 2. At level 3, an exact union-of-convex-pieces computation or a rasterization at a registered resolution, with a contract that bounds its error against exact clipping.
- *Degenerate shapes:* area ≤ 10⁻¹² L² fails (N3).

**Per-world outcome**, the first that applies: FORMED, MERGED (a criterion-6 failure), DRIFTING (contact but no locked candidate), APART, OTHER.

**Promotion.** An accepted level-n candidate publishes exactly one level-n `ResonatorState` through `c6_units.compose_state` (the `level_interface` gate). Publication is read-only: it never changes the full-model state.

## 5. Lower levels stay real; upward and downward paths

- **Alive and dynamic.** The full simulation always integrates every element. Promotion never deletes, freezes or replaces members (invariant 2). Coarse models are only predictions scored against the full model and are never substituted into it. Recursive criterion 6 shows that accepted level-3 groups contain valid level-2 and level-1 resonators throughout the window. τ₁ and τ₂ measured inside the formed level-3 world are reported next to their isolated values.
- **Upward (`upward_transfer_l3`).** Rotate the phases of **one level-1 unit** inside one level-2 group by 0.5 rad. Measure the response of the **other level-2 groups'** published Θ: the intact world minus the same world with its level-2 groups decoupled, where the response is 0 by construction. A registered margin of 0.01 rad applies. A disturbance must cross two levels.
- **Downward (`downward_effect_l3`).** Compare each level-2 group's port elements' phase offsets, relative to its own Θ, inside the level-3 group and decoupled from it; margin 0.01 rad. This is the level-2 boundary condition changed by the level-3 whole. The level-3 whole acts only through the element law, never by overwriting member states. The same shift for level-1 ports (two levels down) is reported descriptively.
- **Emergent transfer (`emergent_transfer_l3`).** Pulse a whole level-2 group's phase by 0.5 rad and measure the other groups' response, intact minus decoupled, with the same margin. This is behaviour that no isolated level-2 group has.

## 6. Interventions, predictions and complete ablations (level 3; transition 1 uses the same protocol on level-2 worlds)

Every run is paired with an unperturbed control from the same formed state s₀, and every ablation is matched on s₀. The unit of analysis is the world: its value is the mean over its accepted groups. CIs are bootstrap 95% (10,000 resamples). All doses are the C5 doses, which are dimensionless and identical at both levels.

| Test | Intervention (insides of the level-2 groups held bit-identical) | Registered prediction | Complete matched ablation |
|---|---|---|---|
| **G→M** | Move level-2 groups rigidly so each centroid's offset from the level-3 centroid is scaled by s. Both runs of the pair get the same zero-mean group-phase probe (RMS 0.3). | The time-mean inter-group pattern deviation **increases**. | `no_geometry_to_mode`: w = 1 and the phase topology frozen at s₀ (the effect is exactly 0 by construction) |
| **M→G** | Rotate each group's phases rigidly by a zero-mean kick of fixed RMS. | The peak radius of gyration of the group centroids **increases**. | `no_mode_to_geometry`: J = 0 (exactly 0) |
| **Dose-response** | G→M at s = 1.1 / 1.25 / 1.5; M→G at RMS 0.5 / 1.0 / 1.5. Each ladder is **one controlled-size family** (no "uniform" dose). | The means do not decrease with dose, and the highest-minus-lowest per-world difference has CI > 0. | (intact) |
| **G→M channels** | Only w = 1, or only the frozen topology. | Descriptive decomposition. | — |
| **Upward, downward, emergent** | §5. | Each above the 0.01 rad margin. | Level-2 groups decoupled (each response 0 by construction) |
| **Coarse vs full** | Held-out excitations on one group: a phase pulse of 0.5 rad and a radial push of 0.2 × its L. | §7. | — |

The primary doses are s = 1.25 and RMS 1.0. Single-channel ablations are decomposition only and never serve as the primary ablation (C4 R001 lesson).

## 7. Full versus coarse at both transitions

- **Who reads what.** The transition-n coarse model is `c5_coarse.run`, unchanged and level-agnostic, given **only the published level-(n−1) states** of the group's members.
  - At level 3 it reads level-2 states (ports, capacities, natural rates, sizes) and never level-1 states or elements. This is the standard's "an R₂ query reads R₁ effective states".
  - A contract checks the input type, and a mutant that passes level-1 states must be detected.
  - Couplings form and break by the C4 neighbour rule on ports.
- **Open-loop scoring.** The scored prediction never receives full-model states. The reopening protocol (invariant 8) runs alongside and is reported: invalid flags, reopen counts, and error on flagged versus unflagged excitations, which shows whether the validity bound carries information.
- **Baselines**, the same at both transitions, all required:
  1. no transfer;
  2. rigid transfer;
  3. relaxation to an equal share, using the group's own measured τ_n from its intact G→M control. This is a calibrated baseline; the calibration advantage is declared.
- **Scoring per excitation type (D4).** For e ∈ {pulse, push} and each baseline b, gain_{e,b} = error_b − error_coarse per world. The error is the C5 response error over the non-excited units: RMS wrapped phase error plus RMS position error over L. The rule is in §8.
- **Bounded predictive error.** At each transition, the coarse model must be strictly better than every cheap baseline, including "nothing responds" and the measured-τ relaxation, for both excitation types. This is the operational meaning of the standard's "bounded predictive error". It is stricter than C5's averaged rule.
- **Expectation, stated up front.** On C5's data the push channel would fail or be inconclusive. Unless the corrected interface (§3) changes that, the honest prior for H-C is INCONCLUSIVE or NOT_SUPPORTED. Either is a valid result.
- **Descriptive only (no verdict; usefulness is C8's question):**
  - `coarse_depth`: at level 3, the coarse model on level-2 states against a flat coarse model on all level-1 states of the same units. This shows how much the middle level loses.
  - Work counts: pair evaluations for the full model, the flat coarse model and the two-level coarse model.
  - Frequency error and recovery-time error.

## 8. Endpoints and verdict rules (every endpoint evaluated by the panel or listed in `not_run` with a reason)

"Composition endpoints" means the five transition-1 endpoints and the seven transition-2 endpoints marked as such below. The minimum for any inferential verdict is **10 formed worlds** at that level; below it, the endpoint is INCONCLUSIVE.

| Endpoint | Rule (rows in order) |
|---|---|
| `level1_pool` (gate) | Every used level-1 unit, alone with its rate, is re-detected by the frozen C4 detector. |
| `level2_pool` (gate) | Every harvested level-2 group, alone with its shifted rates, is re-detected as an accepted level-2 resonator by `detect_level` at n = 2. |
| `harvest_isolation` (gate) | No C4 world feeds two level-2 worlds, and no level-2 harvest world feeds two level-3 worlds. Source paths are stored per world. |
| `same_rule_audit` (gate) | The level-3 thresholds equal `level2_thresholds(level2_thresholds(C4, T₂), T₃)`. Detector, promotion and coarse calls are the same function objects at both levels. The static no-level-branch check passes. T₂, T₃, the τ's and the final measured ratios are recorded. |
| `numerical_checks` (gate) | The C4 checks on an assembled level-3 world (RK4 order, switching dt error, equivariance under permutation, translation, rotation and global phase), plus unit and group relabelling, plus exact decoupling (each group alone equals the decoupled run, tolerance 10⁻⁹). |
| `level_interface` (gate, N1) | At both levels, exactly one published parent per accepted candidate **per world**, matched by the candidate's unit set. No duplicates, omissions or swaps. Every numeric field finite. Ports non-empty and well-formed. Mode signature consistent with the children. S equal to the candidate's statistics. Digest derived from the children. Gate: not FAIL. |
| `not_independent_l2`, `not_a_clump_l2`, `not_independent_l3`, `not_a_clump_l3` (gates) | Decoupled continuations with imposed candidates: with the assembled rates (expected to fail criterion 3) and with the rates shifted to 0 (expected to fail criterion 5). **FAIL** if any candidate is accepted; **PASS** if at least one was tested and none was accepted; **NOT_TESTED** if none. Gate: all PASS. |
| `formation_l2`, `formation_l3` | Fraction of FORMED worlds, Wilson 95% CI. (1) **PASS** if the Wilson lower bound ≥ 0.5 and ≥ 10 worlds are formed; (2) **FAIL** if the Wilson upper bound < 0.5; (3) **INCONCLUSIVE** otherwise (D3). |
| `formation_outcomes_l2`, `formation_outcomes_l3` | Descriptive: outcome counts, per-criterion failures, and the views from below (the C4 component view at both levels; at level 3, whether the level-2 detector accepts the union of a level-3 group's units as a single level-2 resonator). |
| `g_to_m_l2`, `m_to_g_l2`, `g_to_m_l3`, `m_to_g_l3` | (1) **INCONCLUSIVE** if fewer than 10 formed worlds; (2) **FAIL** if the intact CI includes 0 or lies below it; (3) **PASS** if the complete-ablation CI includes 0 or its \|mean\| ≤ 0.2 × the intact mean; (4) **INCONCLUSIVE** otherwise. |
| `dose_response_l2`, `dose_response_l3` | Per direction: (1) **INCONCLUSIVE** if fewer than 10 worlds; (2) **PASS** if the means do not decrease and the highest-minus-lowest CI > 0; (3) **FAIL** if that CI < 0; (4) **INCONCLUSIVE** otherwise. The endpoint fails if either direction fails and passes only if both pass. |
| `g_to_m_channels_l3`, `parts_alive_l3` | Descriptive: single-channel effects; recursive criterion-6 values for every level-2 group and every level-1 unit of **every** candidate, accepted or not. |
| `downward_effect_l2`, `emergent_transfer_l2`, `downward_effect_l3`, `upward_transfer_l3`, `emergent_transfer_l3` (composition) | Margin rule with 0.01 rad: (1) **INCONCLUSIVE** if fewer than 10 worlds; (2) **FAIL** if the CI upper bound < 0.01; (3) **PASS** if the CI lower bound > 0.01; (4) **INCONCLUSIVE** otherwise. |
| `effective_state_l2`, `effective_state_l3` (composition) | The C5 bounds (position 0.25 of L, size 0.05; frequency 0.01 divided by the level's cumulative T). (1) **INCONCLUSIVE** if fewer than 10 formed worlds; (2) **PASS** if ≥ 90% of published parents meet every bound; (3) **FAIL** otherwise. |
| `coarse_vs_full_l2`, `coarse_vs_full_l3` (composition) | Six paired gains per world (2 excitation types × 3 baselines), open-loop. (1) **INCONCLUSIVE** if fewer than 10 worlds; (2) **FAIL** if any gain CI upper bound < 0; (3) **PASS** if every gain CI lower bound > 0; (4) **INCONCLUSIVE** otherwise. The reopening protocol, flags, frequency and recovery errors and work are reported, never scored. |
| `timescale_separation_l2`, `timescale_separation_l3` (composition) | Per world, the mean over its groups of τ_n / (the mean τ_{n−1} of that group's own parts, measured alone). τ_n censored at its window is a counted lower bound. (1) **INCONCLUSIVE** if fewer than 10 worlds; (2) **FAIL** if the CI upper bound < 1; (3) **PASS** if the CI lower bound > 1; (4) **INCONCLUSIVE** otherwise. |
| `partition_specificity_l3` (composition) | For every accepted level-3 group, the same level-1 units are re-partitioned (seeded) into fake level-2 units with the true size profile, each mixing units from at least two real groups. Their states are composed with the same function and given to the level-3 detector as imposed candidates. **FAIL** if any is accepted; **PASS** if at least one was tested and none was accepted; **NOT_TESTED** if none. The rejecting criteria are reported. |
| `interface_fidelity` | Descriptive, at both levels, per parent: C5's size-weighted rate and C6's measured isolated rate against the parent's observed rate; and per port, the coarse cross-link count from C5's inherited capacity list and from C6's sibling-folded list, against the full model's element-level census of that port element. Raw values are stored. |
| `coarse_depth` | Descriptive (§7). |

**Truth tables.** These are registered in the manifest as ordered rows. The code implements them row by row, and a test enumerates every input combination.

| Hypothesis | Row | Condition | Verdict |
|---|---|---|---|
| H-M level n (n = 2, 3) | 1 | any of `g_to_m_ln`, `m_to_g_ln`, `dose_response_ln` = FAIL | NOT_SUPPORTED |
| | 2 | `formation_ln` = PASS and all three = PASS | SUPPORTED_WITHIN_SCOPE |
| | 3 | otherwise (formation FAIL or INCONCLUSIVE, fewer than 10 formed worlds, any INCONCLUSIVE) | INCONCLUSIVE |
| H-C transition n | 1 | `formation_ln` Wilson upper bound < 0.25 (composition clearly does not occur under this rule) | NOT_SUPPORTED |
| | 2 | any composition endpoint of transition n = FAIL | NOT_SUPPORTED |
| | 3 | H-M level n = SUPPORTED_WITHIN_SCOPE and every composition endpoint of transition n = PASS | SUPPORTED_WITHIN_SCOPE |
| | 4 | otherwise | INCONCLUSIVE |
| **H-C (recursive, the central gate)** | 1 | either transition = NOT_SUPPORTED | NOT_SUPPORTED |
| | 2 | both transitions = SUPPORTED_WITHIN_SCOPE | SUPPORTED_WITHIN_SCOPE |
| | 3 | otherwise | INCONCLUSIVE |

- **Formation and H-M.** Too few groups is no evidence about their coupling (the C4 R003 principle), so formation failure alone never makes H-M NOT_SUPPORTED.
- **Formation and H-C.** Composition that clearly does not happen *is* the H-C answer for this rule (C5 owner decision D3, applied at both levels).
- **Gates.** A gate failure (pools, isolation, same-rule audit, numerical checks, interface, controls) means the run is not REVIEW_READY, whatever the verdicts.

## 9. Formation plan, design gate, sample sizes and seeds

**Why formation needs a plan.** C5's 17/30 has a Wilson interval of [0.39, 0.73]. Level-3 coupling is probably weaker, because a level-2 group of about 40 elements touches its neighbours through a handful of boundary elements. C5's own data say where the losses come from:
- formation hardly changed with rate spread (16, 17 and 16 formed at 0.5δ, δ and 2δ), so a smaller spread is not the lever;
- the losses were DRIFTING (9: contact, but no locked group of three or more units) and MERGED (4).

The levers are therefore how many units a world holds and how close they start. Both are world-assembly fixtures, not composition-rule parameters, and C6 applies them identically at both levels.

**Design gate (development entropy only, before registration; `tools/c6_design_gate.py`).**
1. **Pre-declared grid,** in cost order:
   - (M = 5, s_R = 1);
   - (M = 5, s_R = 0.75);
   - (M = 7, s_R = 1);
   - (M = 7, s_R = 0.75).

   The first setting whose development formation is ≥ 0.75 at level 2 (30 development worlds) and then at level 3 (10 development worlds) is selected. Level 3 is run only for settings that pass level 2, in order, stopping at the first that passes. Nothing else is varied.
2. **Coupling and T₃.**
   - τ₃ must be finite (groups in contact couple).
   - T₃ is measured with a provisional T₃ = 3.2. If the measured value falls outside [1.6, 6.4], development formation is re-run at the measured T₃ before selection.
   - T₂ is re-measured and must lie within [T₂/2, 2T₂].
3. **Interface fidelity.** C5's composition rule and C6's corrected rule are compared on the development groups (`interface_fidelity`). If C6's rule is not at least as faithful on both rate and capacity, the implementer stops.
4. **Shape-overlap calibration.** Union-of-hulls overlap is recorded for touching accepted level-2 groups. If touching but intact groups exceed 0.2, the implementer stops and reports; the threshold is never changed silently.
5. **Runtime projection.** The measured per-world cost is projected to the full panel (§10).
6. **Raw records (N2).** Every per-world measurement (formation outcomes per setting, overlaps, τ's, rate and capacity fidelity, timings) is committed in a development artifact pinned by hash in the manifest. Development outcomes are settings, not evidence.

If no grid setting reaches 0.75 at both levels, or any check above fails, the implementer **stops and reports to the owner before registration**. The model, the law and the thresholds are not changed to make composition happen. A clear level-3 formation failure on development worlds is itself a finding; the owner may then choose a decision record over a panel.

**Final sample sizes.**
- **Transition-1 evidence:** n₂ = 40 fresh level-2 worlds, disjoint from the harvest worlds and run with the full level-2 protocol.
- **Transition-2 evidence:** n₃ = 40 fresh level-3 worlds.
- **Why 40:**
  - Under D3, PASS needs at least 27/40 formed (Wilson lower bound 0.52; 26/40 gives 0.495).
  - At a true rate of 0.75 that happens with probability about 0.9; at 0.65, about 0.4. This is why the design gate targets 0.75.
  - At 0.75, about 30 formed worlds per level feed the causal and coarse endpoints, three times the minimum of 10.
  - If the runtime projection forces n₃ = 30, PASS needs at least 21/30, and the change is made before registration.
- **Harvest volume, about:** 40 × M × 1.5 / f₂ level-2 harvest worlds (about 400 at M = 5 and f₂ = 0.75), and the C4 worlds that feed them (about 3,000, using C5's 7.5 per level-2 world).

**Seeds.**
- Development entropy: 33333, which is new; C5's 22222 is not reused.
- Final entropy: drawn with `secrets.randbits(63)` at registration. Disjoint SeedSequence purposes cover C4 harvest, level-2 harvest, transition-1 worlds, level-3 worlds and every kick, probe and excitation.
- Final worlds and all their upstream harvest worlds are never simulated before the recorded panel. Smoke and tests use development entropy only.

**Receipt detail** (C4/C5 lessons): every value below is stored, and nothing is reduced to a mean only.
- *Per level-1 unit and per level-2 group:* size, rate, criterion-6 values, ports and τ.
- *Per candidate:* all six criteria and the three recovery scores.
- *Per published parent:* its state, its children's states, its C5 comparison state and its fidelity values.
- *Per world, condition and dose:* the effects.
- *Per excitation:* the full, coarse, flat-coarse and baseline errors, plus flags.
- *Per world:* the source paths.

## 10. Engineering, reuse and runtime

**Reused read-only.** These are frozen files, imported and never edited:
- `c4_model`: `simulate`, `neighbors`, `Params`, `ABLATIONS`, `Batch`, `wrap`. The full model is exactly `simulate`.
- `c4_detect`: `detect` (level-1 harvest), `components`, `locked_pairs`, `window_statistics`, `kick`, `best_match`, `jaccard`, `radius_of_gyration`, `pair_differences`, `circular_mean`, `nn_spacing`, `criteria_checks`, `_convex_hull`.
- `c4_experiment`: `initial_worlds`, `form`, `detect_worlds`, `model_params`, `bootstrap_ci`, `wilson`, `causality_verdict`, `dose_response_verdict`, `gm_statistic`, `mg_statistic`, `summarize`.
- `c5_units`: `harvest`, `resonator_state`, `unit_positions`, `unit_phases`, `polygon_area`, `clip_convex`, `member_digest`, and `compose_state` (for the `interface_fidelity` comparison only).
- `c5_detect`: `level2_thresholds` (applied recursively), `candidates`, `imposed`, `recovery`, `unit_kick`, `criteria_checks`.
- `c5_compose`: `pad`, `scale_units`, `rotate_units`, `shift_units`, `unit_kick`, `decouple_offsets`, used with labels at the right level.
- `c5_coarse`: `run`, `CoarseState`, `links`, `rhs`. These are level-agnostic and used at both transitions unchanged.
- `c5_experiment`: `assign_templates`, `efold`, `relaxation_prediction`, `response_error`, `margin_verdict`, `separation_verdict`, `control_verdict`, `mg_dose_rms`.

`milestones/c6.json` lists the C4 and C5 files and both manifests as dependencies, so the C6 fingerprint covers them.

**New files.**
- `geomind/c6_levels.py`: the owner tree, the per-frame published series, `detect_level`, recursive criterion 6 (union-of-hulls area with the degenerate-shape rule) and the threshold composition.
- `geomind/c6_units.py`: the corrected `compose_state`, the isolated-rate measurement, level-2 template harvest with source paths, and the N1 validator.
- `geomind/c6_compose.py`: level-n assembly with internal rates kept and the rotating-frame group offset.
- `geomind/c6_experiment.py`: one transition protocol called at n = 2 and n = 3, evaluation and truth tables.
- `geomind/run_c6.py`: the runner, which calls `check("c6", "panel")` itself.
- `tests/test_c6.py`, `tools/c6_mutants.py`, `tools/c6_design_gate.py`.
- `experiments/c6_manifest.json` and `milestones/c6.json`, registered and committed before any final-seed run.

**Focused contracts** (fast, synthetic or development fixtures):
- *Same rule:*
  - the generic detector at n = 2 reproduces C5's frozen detector on development worlds;
  - the level-3 thresholds equal the composed scaling;
  - static no-level-branch check;
  - `compose_state` at both levels has the same shape;
  - the measured isolated rate of a level-1 unit equals ω_g.
- *Rigid operations:* rigid group moves and rotations leave level-1 and level-2 insides bit-identical.
- *Decoupling:* decoupled groups have no cross-group neighbour, and each group alone equals its decoupled run.
- *Ablations remove their pathway:* the frozen topology freezes cross links, and J = 0 removes the phase-dependent cross term.
- *Detector rejections, each with a positive control:*
  - a merged level-3 pair (criterion 6 at level 2);
  - a broken level-1 unit inside an intact level-2 group (the recursion);
  - collinear and degenerate units (N3);
  - concave composites that touch without interpenetrating, which must pass;
  - drift (criterion 3), static (criterion 5) and the fragment-alike case (criterion 5).
- *Information boundary:* the detector and the level-3 coarse model never receive member lists, rates or labels, and the coarse model rejects level-1 states.
- *N1 cases:* duplicate, omitted and swapped publications, NaN fields, and empty mode or S are rejected.
- *Isolation:* the reviewer's split case at both tree levels.
- *Scoring:* open-loop scoring has no reopen callback, and the six gains are computed per excitation type.
- *Rules:* every truth-table row is covered by enumeration, and every manifest endpoint appears in the coverage.

**Mutants** (`tools/c6_mutants.py`), each of which must be detected by the tests:
- *Same-rule breaks:* T₃ not applied; a level branch with a different threshold.
- *Criterion 6:* not recursive; convex hull instead of the union; degenerate shapes passing.
- *Publication (N1):* a global publication count; NaN fields accepted.
- *Composition:* the size-weighted natural rate instead of the measured one; capacities not folded.
- *Coarse model and scoring:* reading level-1 states at level 3; scoring with reopening; pulse and push averaged; relaxation using τ from the wrong level.
- *Group tracking:* recovery ignoring the original group.
- *Controls:* the decoupled control leaking cross-group links; the wrong-partition control left empty.
- *Doses and harvest:* a mixed dose family; a harvest source shared across worlds.
- *Verdicts:* formation by point estimate instead of the Wilson lower bound; H-C ignoring one transition; a margin ignored.

**Runtime estimate.** Basis:
- *Measured this session:* the frozen `c4_model` RK4 step costs 0.24 ms per world-step at N = 55 and 2.3–3.1 ms at N = 200–250 (this machine, NumPy 2.0.2, one process, random states).
- *C5's measured panel:* 287 s for 30 level-2 worlds plus 225 C4 worlds on 4 processes, about 1.7× the bare stepping cost.

| Stage | Estimate |
|---|---|
| One level-3 world (N ≈ 185, T₃ ≈ 3, about 480 steps per level-3 time unit, about 390 time units: formation 100, recovery 60, controls 60, interventions 150, upward pulse and τ 20) | ≈ 190k world-steps ≈ 8 min of stepping, ≈ 13 min CPU |
| 40 level-3 worlds | ≈ 9 CPU-h |
| Harvest (about 3,000 C4 worlds, about 400 level-2 worlds) and 40 transition-1 worlds | ≈ 2–2.5 CPU-h |
| **Recorded panel, 8 processes** (10-core machine) | **≈ 1.5 h** at M = 5 and T₃ ≈ 3; **up to ≈ 4 h** at M = 7 or T₃ ≈ 5 |
| Tests / smoke (1–2 development level-3 worlds) / mutation probe | < 2 min / ≈ 15–30 min / ≈ 2–5 min |
| Design gate (development only, before registration) | ≈ 1–2 h |

The panel is 20–50× C5's, because level-3 worlds are about 3.5× larger (all-pairs neighbour search and sort grow faster than N²) and every level-3 time is about 3× longer. If the design gate projects more than 4 h, the implementer returns to the owner before registering. The options would be:
- n₃ = 30;
- dropping the level-3 decomposition ablations;
- a faster neighbour selection in a new file that is contract-tested bit-identical to `c4_model.neighbors` (argpartition, then an exact (distance, index) sort, with a fallback on boundary ties);
- a C++ backend.

**C++ backend: not proposed.** At these estimates NumPy with 8 processes is enough. A C++ kernel would raise G10: the toolchain is not pinned, and the binary and its compiler would need to be recorded or locked. Its libm `exp`, `sin` and `cos` would not be bit-identical to NumPy. Neighbour switching then makes long trajectories diverge, so an equivalence protocol, and not only a tolerance, would be needed. That is a separate owner decision.

**Frozen environment.** `pyproject.toml` and `uv.lock` are frozen (Python 3.9, NumPy 2.0.2, pytest 8.4.2). That rules out:
- SciPy, whose KD-trees would cut neighbour search at N ≈ 200 but would change frozen files and tie order;
- Numba;
- Hypothesis; property checks stay hand-written randomized loops.

None is proposed. Any of them needs an owner decision.

**Process.** Verify once, in order: `tools/verify.py --milestone c6 --output evidence/c6_r001`. Before a run of an hour or more, tell the owner how long it will take and why. One independent review follows, by the other model family, capped at about 20 minutes. A design defect found before review means withdrawal through a decision record, and the next revision runs on fresh seeds.

## 11. C4/C5 lessons applied up front

| Lesson | Where C6 applies it |
|---|---|
| Ablations must remove a pathway completely (C4 R001) | `no_geometry_to_mode` and J = 0 are primary; "all inter-group coupling off" is literal decoupling; single channels are decomposition only. |
| Recovery and membership keep the original group (C4 R002 → R003) | Criterion 5 matches the original unit set in both futures and requires them to agree. Recursive criterion 6 tracks original member sets at every level. |
| No verdict on fewer than 10 worlds | Every inferential endpoint at both levels. |
| One written rule, implemented row by row | Ordered truth tables in the manifest, mirrored by the code, with an enumeration test. |
| Non-vacuous controls with imposed candidates | Four decoupled controls and the wrong-partition control all receive imposed candidates. Zero-by-construction effects need the 0.01 rad margin. |
| Per-unit and per-group values in the receipt | §9 receipt detail. |
| Dose ladders are one controlled-size family (C5 R001) | Rigid scales and fixed-RMS kicks at both levels; any other dose is refused. |
| Open-loop coarse scoring, never truth injection (C5 R001) | Scored runs have no reopen callback; reopening is only reported. |
| Area-based merger test, degenerate geometry covered (C5 F2, N3) | Union-of-hulls area; degenerate shapes fail; contracts for crossing, collinear and concave cases. |
| One parent per accepted candidate per world, finite fields (N1) | The `level_interface` gate. |
| Keep raw calibration measurements (N2) | Committed design-gate artifact, pinned by hash. |
| Harvest sources isolated across worlds (C5 F4) | Isolation at both tree levels; the `harvest_isolation` gate. |
| Formation well clear of its threshold (C5 review qualifier) | Design-gate target 0.75; Wilson-lower-bound PASS rule; n = 40 per level. |
| Test inherited capacities and natural rate first (C5 review) | Corrected composition rule, measured in the design gate and in `interface_fidelity`. |
| An averaged score can hide a failing channel (found while drafting, from the C5 R003 receipt) | Pulse and push scored separately. |

## 12. Who implements and who reviews

Claude implemented C4 and C5, and Codex reviewed both. **The drafter recommends that Codex implement C6 and Claude review it.**
- C6 is mostly new generic code (`c6_*`) over frozen C4/C5 functions, so continuity matters less than it did for C5.
- Codex knows these functions closely from its three reviews; it found C5's F1–F4 and N1–N3.
- Alternating roles keeps any single family from both building and judging a whole lane, and it limits same-family blind spots across C4–C6.
- The cost is that Codex has not used this repository's implementer workflow since C2; the pipeline and hooks are the same.

Because Claude drafted this proposal, the owner may also ask Codex for a short critique of the proposal before approval (a registered-report step). That is optional.

## 13. What C6 cannot show

- **Two transitions only.** There is no claim about R₃ or arbitrary depth.
- **No dissolution or reform:** that is C7. **No usefulness, compression or efficiency:** that is C8. `coarse_depth` and the work counts are descriptive.
- **Staged assembly.** Each level is formed separately and then placed together. C6 does not show two levels co-forming from one primitive soup.
- **Rate offsets are fixtures.** Per-unit and per-group offsets are exact rotating-frame symmetries assigned by the experiment; they do not emerge.
- **The physics does not rescale.** The element law's interaction range is fixed, so higher levels couple only through boundary contact. "Same rule" refers to the detector, the promotion, the composition and the scaled thresholds, not to a scale-free interaction.
- **Narrow scope.** One model, one parameter set and one M; level-1 units of 6–16 elements; no internally heterogeneous level-1 unit.
- **Weak spots in the evidence:**
  - complete ablations vanish by construction, so the evidence is the intact effects and their dose-response;
  - the downward effects test existence, not dose.
- **Statistical scope.** Inference is per world, conditional on fresh source-isolated harvests.
- **Not novel.** Hierarchical synchrony and oscillator coarse-graining are known results [S1–S3, S6, S7].

## Sources

- **[S1]** Arenas, Díaz-Guilera and Pérez-Vicente, *Synchronization reveals topological scales in complex networks*, PRL 96, 114102 (2006). [arXiv:cond-mat/0511730](https://arxiv.org/abs/cond-mat/0511730). Synchronization proceeds level by level on hierarchical networks.
- **[S2]** Skardal and Restrepo, *Hierarchical synchrony of phase oscillators in modular networks*, PRE 85, 016208 (2012). [arXiv:1111.0921](https://arxiv.org/abs/1111.0921).
- **[S3]** Ott and Antonsen, *Low dimensional behavior of large systems of globally coupled oscillators*, Chaos 18, 037113 (2008). [arXiv:0806.0004](https://arxiv.org/abs/0806.0004).
- **[S4]** Lee et al., *Collective steady-state patterns of swarmalators with finite-cutoff interaction distance* (2021). [arXiv:2103.11584](https://arxiv.org/abs/2103.11584).
- **[S5]** Sar and Ghosh, *Dynamics of swarmalators: a pedagogical review* (2022). [arXiv:2208.14803](https://arxiv.org/abs/2208.14803).
- **[S6]** Villegas, Moretti and Muñoz, *Frustrated hierarchical synchronization and emergent complexity in the human connectome network*, Sci. Rep. 4, 5990 (2014). [arXiv:1402.5289](https://arxiv.org/abs/1402.5289). Hierarchical modularity with frequency heterogeneity at many scales gives partial, level-wise synchronization.
- **[S7]** Gfeller and De Los Rios, *Spectral coarse graining and synchronization in oscillator networks*, PRL 100, 174104 (2008). [arXiv:0708.2055](https://arxiv.org/abs/0708.2055). Merging nodes can preserve an oscillator network's synchronization behaviour; this is a precedent for testing coarse states against the full dynamics.
- **[R3]** in the standard: O'Keeffe, Hong and Strogatz, *Oscillators that sync and swarm* (2017).

## Decisions for the owner (with the drafter's recommendation)

1. **D1 — Approval. Recommended: approve as written.** The draft was checked against the standard's C6 section, the recursive interface, invariants 1, 2, 6, 8 and 10, the C5 reviews and decisions 0005–0006.
2. **D2 — Corrected composition rule. Recommended: accept.** One new `compose_state` with a measured isolated rate and sibling-folded capacities, used at both promotions. C5's version is reported for comparison only.
3. **D3 — Formation rule. Recommended: PASS on the Wilson lower bound ≥ 0.5**, FAIL on the upper bound < 0.5, INCONCLUSIVE otherwise, with n = 40 per level and a development target of 0.75. The alternative is C5's point-estimate rule, which leaves the C5 qualifier ("no formation rate above 50% established") unresolved.
4. **D4 — Predictive gate. Recommended: score pulse and push separately against all three baselines.** It is stricter than C5's averaged rule, and on C5's data it would likely fail on pushes. The alternative, C5's average, would let a phase-only success hide a position failure.
5. **D5 — Roles. Recommended: Codex implements and Claude reviews** (§12). Optional: a short Codex critique of this proposal before approval.
6. **D6 — Compute. Recommended: NumPy with 8 processes and no C++ backend.** The panel is estimated at about 1.5–4 h; a projection above 4 h comes back to the owner before registration.
