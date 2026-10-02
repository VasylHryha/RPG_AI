# C6 proposal: recursive composition R₀ → R₁ → R₂ with the same rule (DRAFT, not approved)

Status: **PROPOSED**, awaiting owner approval. Nothing is registered: there is no `experiments/c6_manifest.json`, `milestones/c6.json` or C6 code. At the owner's request, a development-only pilot was run with scratch code outside the repository (§3b). Authority: `GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md` (C6, the recursive unit interface, the ten recursive-resonator invariants, §5–7). Builds on C4 R003 and C5 R003, both independently accepted (`evidence/c4_r003_review_codex/INDEPENDENT_REVIEW.md`, `evidence/c5_r003_review_codex/INDEPENDENT_REVIEW.md`). Format follows `experiments/c5_proposal.md`. **Theory alignment:** RRG v0.2 locked core (`RPG_theory/research/RRG_CURRENT/00_LOCKED_CORE.md`, SHA-256 `b6d3e7c75285889afe94cabf083ba5fb80f401c656613ba6a80d2f0149b655e1`). Where the R4 standard is narrower than the locked core, this proposal follows the locked core (§0). Decision 0007 (D7, accepted) records that reading in the standard, and it must be committed before registration (stop rule 15), so the standard and the proposal agree when C6 is registered. The drafter's self-audits are at the end.

**Level names.** Level 0 is a primitive element. Level 1 is an accepted C4 resonator (the standard's R₀). Level 2 is a C5 composite (R₁). Level 3 is the C6 composite (R₂). "Transition n" is level n−1 → n, so transition 2 is level 1 → 2 and transition 3 is level 2 → 3. The standard's "two successive transitions" are transitions 2 and 3.

## 0. What C6 tests in RRG, and why it matters for the AI

The project has two goals:
- test the RRG theory;
- build a simple AI that works on its principles.

C6 serves both. It tests the recursion in a model small enough to build on. Every C6 claim below is mapped to the clause of the locked core it tests. Nothing in C6 narrows a locked definition (`05_CHANGE_CONTROL.md`).

**Locked-core claims C6 tests in this model:**

| Locked clause | What it says | C6 test |
|---|---|---|
| §3 | Geometry and mode constrain each other: G ↔ M | G→M and M→G, each removed by a complete ablation, with dose-response, at level 2 and level 3 (`g_to_m`, `m_to_g`, `dose_response`) |
| §4 | Stability is the closed G ↔ M loop for however long it lasts. Recovery and lifetime are tests, not the definition. | Detector criteria 1–5 are **operational tests** of closure in this model ("simulation conveniences", doc 03 §11), never a redefinition of stability |
| §5 | A higher level forms from lower resonators, which stay internally active, and the whole has a new collective mode | Formation; criterion 6 (parts alive on their own scale); emergent transfer (a collective response no part has alone); downward and upward effects (whole ↔ parts, Proposition 4) |
| §7 | A scale is a level whose resonator works as a unit in further interactions. Operationally (doc 03 §37): a reduced set of variables predicts its interactions with bounded error. | The level-2 resonators are used as the units that form level 3. `coarse_vs_full`: an effective model built only from published summaries predicts held-out responses with bounded error. `unit_specificity`: the real groups work better as units than other groupings of the same parts. |
| §8 | Recursion: R₀ → R₁ → R₂ | Both transitions, in one experiment, under one procedure |

**Optional, stronger RRG extensions, each reported with its own verdict and never required for H-C:**
- **Same-law closure** (locked §7; doc 03 §13; proof matrix): the *same* element law, applied to the published summaries, predicts the next level (`same_law_closure`). Locked §7 allows different effective dynamics at different scales; same-law recurrence is a stronger universality result.
- **Scale separation** (doc 02 §5; the owner's expectation: mostly true): higher levels are larger, slower to relax and slower to form. C6 tests it as an explicit RRG prediction with its own verdict (`scale_separation`). It stays outside H-C only because the locked core does not define a scale by being slower. A test is stronger than an assumption: the time normalization *measures* τ at each level, so the method works whichever way the result comes out.

**What C6 does not test, and where it belongs:**
- *Variation (§6):* only a descriptive count of distinct level-3 forms (`variation`).
- *Levels without predefined stages (doc 02 Phase D):* C6 assembles each level separately (§13).
- *Energy and dissipation (Phase E):* the C4 law makes passive structures only.
- *Propagation and recurrence (§9):* not tested.
- *New possibility spaces (Proposition 8):* not tested.

**Why it matters for the AI goal.** RRG's AI reading (docs 01 §13 and 02 §10) is:
- abstraction is promoting a stable cluster to a higher-level node;
- memory is persistent geometry;
- the same rule is repeated recursively.

C6 tests the core of that mechanism. It asks whether stable clusters, found without labels, become nodes whose small published summaries predict the system's behaviour, twice in a row, under one procedure, while the detail underneath keeps running. If that fails, an RRG-style abstraction layer has nothing to stand on. If it holds, the published `ResonatorState` and the one effective-model recipe are the interface an AI prototype would build on. C6 makes no usefulness or efficiency claim; that is C8, and the work counts here are descriptive.

**Where the R4 standard is narrower than the locked core.** The standard's invariant 1 ("same rule across scales") is kept in the sense the locked core allows:
- the same *procedure* at every level: detection, promotion, composition, the effective-model recipe, and thresholds scaled by measured size and time;
- one physics, the C4 element law, everywhere in the full simulation.

The higher level's effective dynamics may differ from the element law (locked §7), so same-law closure is reported as the optional extension. D7 asks the owner to record this reading in the standard.

## 1. The bounded question

> Take accepted level-2 resonators (groups of C4 resonators) and let them interact only through the unchanged C4 element law. Apply the **same** detector, promotion, composition and effective-model recipe that turn level-1 units into level-2 resonators, with thresholds rescaled only by measured timescale (and, implicitly, by measured size). Does a level-3 resonator form, meaning (operationally, §0) a persistent, recovering, frequency-locked group of level-2 units in which every level-2 unit, and every level-1 unit inside it, stays a live, distinct resonator of its own level? Answering it means testing five things:
>
> - whether the level-3 mode depends causally on level-2 geometry and the reverse, each effect vanishing under its complete matched ablation;
> - whether disturbances travel up from level 1 to level 3, and whether level 3 constrains level-2 boundaries downward;
> - whether the formed level-2 groups work better as units than other groupings of the same level-1 units: their summaries predict the full dynamics better (the locked core's meaning of a scale);
> - whether an effective model built only from the published level-2 summaries, by one recipe used at every level, predicts held-out responses with bounded error, better than strong cheap baselines;
> - whether all of this holds again at transition 2, re-measured on fresh worlds.

Hypotheses:
- **H-C (the standard's central gate; locked core §5, §7, §8):** two successive transitions under one procedure, each with a valid effective state, bounded predictive error and real units. C6 re-measures transition 2 on fresh worlds under the same procedure as transition 3. C5's transition was INCONCLUSIVE, and the gate needs both transitions in one experiment.
- **H-M at level 3** (G ↔ M one level up, locked §3), and **H-M at level 2** replicated on fresh worlds.
- **Optional extensions, each with its own verdict and never required for H-C:**
  - same-law closure (`same_law_closure_lN`);
  - scale separation (`scale_separation_lN`), a registered RRG prediction.

**The cheap explanations C6 must rule out.**
1. **"Level 3" is one bigger level-2 group**, so the middle level is bookkeeping. Three checks rule this out:
   - *Recursive criterion 6 (§4):* every level-2 part stays a valid, distinct level-2 unit, and so does every level-1 unit inside it.
   - *`unit_specificity_l3` (§5):* the effective model built from the real level-2 groups predicts the full dynamics better than the same model built from contiguous alternative groupings of the same level-1 units. In a flat blob, no grouping is a better unit than another. This is the locked core's own test of a scale (§7), and it makes no timescale assumption.
   - *A disclosure:* the receipt reports whether the level-2 detector accepts the union of a level-3 group's units as a single level-2 resonator.
2. **A dendrogram or connected-component tree.** Nested clustering at two distance thresholds always yields a tree. C6 requires dynamics at every level: locking, recovery after a kick, two-way causality with complete ablations, dose-response, upward and downward transfer, and units whose summaries predict better than other groupings. A static tree has none of these.
3. **A different solver or threshold per level.** There is one generic level-n detector, one promotion function, one composition function and one effective-model recipe. Level-n thresholds come from one scaling function applied with the cumulative time factor. A static contract forbids level branches, and the `same_rule_audit` gate records function identities and every threshold at each level.
4. **Trivial lock and clump of clumps**, as in C5. Decoupled controls with drifting rates must fail through mode lock, and controls with static rates must fail through recovery. Both controls get imposed candidates, so they cannot pass empty.
5. **"The coarse state is just one number."** A relaxation baseline that uses the group's own measured relaxation time for the excited channel is the strongest cheap predictor. The registered effective model must beat it at both transitions, for each excitation type separately (§7).

These dynamics are not new. Synchronization on hierarchical modular networks proceeds level by level, and pairs inside a community lock first [S1, S2, S6]. Coarse-graining oscillator networks while preserving synchronization is an established method [S7]. Locked populations reduce to a few variables [S3]. Finite-range swarmalators form separate groups [S4, S5]. C6 is a mechanism probe of the RRG recursion (locked §5 and §8) in one model, not a novelty claim.

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
- *Level-1 states:* one new C6 wrapper around the frozen `c5_units.resonator_state` (read-only), used for real **and** fake level-1 parts (§5). The frozen constructor always publishes `natural_rate` as the mean intrinsic element rate. Its `rate` argument changes only `collective_rate` and the mode signature, not the field the effective model reads (`c5_coarse.py:37`; Codex critique F1).
  - *What the wrapper does:* it overwrites `natural_rate` with the part's **measured isolated rate**.
  - *The estimator:* the part runs alone from its published snapshot for 30 C₁. The rate is (Θ(end) − Θ(start)) / duration, where Θ is the circular mean of member phases, unwrapped over frames every C₁.
  - *Consistency:* for a real, homogeneous unit this equals ω_g, which a contract checks. For a fake part, which mixes rates, it is the honest measured value.
  - *Ports:* the wrapper also applies the registered port variant (V2 adds active-contact members).
  - *Contract:* a measured rate different from the intrinsic mean must reach the `natural_rate` field that `c5_coarse.CoarseState` reads.
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
- **The invariant is the dimensionless spread δ_n × C_n = 0.096**, C5's value (δ = 0.03 at C₂ = 3.2), held at every level. So δ₂ = 0.096 / C₂ (C₂ re-measured in C6) and δ₃ = 0.096 / C₃. Keeping C5's raw δ = 0.03 while C₂ changes would silently change the dimensionless spread. The non-vacuity bound then repeats exactly at both levels: the **median** pair drift over a window is 0.586 × 0.096 × 30 ≈ 1.69 rad ≥ 1 rad. It is a typical value, not a guarantee for every pair.

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
  - Each further part approaches the centroid of the parts already placed, from a uniformly random direction, until the minimum cross-part element distance first reaches the contact gap of 0.6. The 0.6 gap is element-scale and is not scaled by level, because it is a property of the element law.
  - *Solving for the contact position:* bracket the crossing with steps of 0.02 element units, then bisect until the minimum distance is within [0.6, 0.6 + 10⁻⁶].
  - *A miss:* if the approach reaches the centroid without contact, the next seeded direction is used, and every retry is recorded.
- *Scale-free at both levels:* every part starts touching the cluster, and the dynamics decide what locks, merges or drifts. The rule applies to every assembled world: level-2 harvest worlds, transition-2 evidence worlds and level-3 worlds.
- *Why it should raise formation, from the detector's definition:* a candidate needs a connected component of at least 3 close, locked parts. Disk placement often leaves fewer than 3 parts in contact, so the world is DRIFTING without any test of locking. With every part touching, that failure mode is removed and the locking criteria decide.
- *At most one group per world:* with M = 5 and a minimum group size of 3, two disjoint groups cannot both exist. So each world contributes at most one group, and the world value is that group's value.
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
- τ_n is the e-folding time of a level-n group's inter-part pattern after a zero-mean part-phase kick (RMS 0.3), against its unkicked control, sampled at 0.1 C_n.
- *Measurement context, one definition per use:*
  - **For normalization (C_n) and for scale separation, τ is measured on the resonator alone**, decoupled from non-members, like the measured natural rate. It is a property of the resonator itself, the same at every level. τ₁ is measured the same way, so C₁ = 1 and C4's times are recovered exactly.
  - **For the relaxation baselines, τ is measured in the world, on the intact control**, the context the excitation happens in, with the same estimator and a horizon of 10 C_n. This is the declared calibration advantage of the strongest baseline.
    - *Censored calibration (Codex N5):* if the channel's in-world τ is censored, no point value is imputed. The baseline is evaluated on the registered admissible grid τ ∈ {1, 2, 4, 8, 16, 32} × the censoring limit, plus τ = ∞.
    - *How the grid is used:* gain_lo uses the grid member with the smallest baseline error, the strongest admissible baseline, and gain_hi uses the one with the largest. The PASS rows use gain_lo and the FAIL rows use gain_hi, so censoring can never manufacture either verdict. The grid is registered, not fitted.
    - *Readiness:* more than 10% censored calibrations among development groups at either transition means stop (stop rule 5).
  - C5 used the in-world τ₂ for both purposes. C6 separates them, so a group's neighbours cannot change its own timescale.
- **The τ estimator:**
  - *Horizon:* 10 C_n, sampled every 0.1 C_n.
  - *Value:* τ is the first sample time at which the deviation falls to 1/e of its initial value (C5's `efold`).
  - *Censoring:* if it never falls that far, τ is censored at 10 C_n and recorded as "> 10 C_n".
- **The cumulative factor:** C_n = median τ_n of the development level-n groups alone ÷ median τ₁ of the development level-1 units alone. Censored values count as +∞ in the medians.
  - It is defined only if fewer than 50% of either set is censored; otherwise stop rule 2 applies.
  - It is **rounded to the nearest multiple of 0.2**, with ties rounded up. At n = 2 this is exactly C5's rule (C5 had C₂ = 3.2).
  - Provisional C values are used only to schedule pass 1 of the design gate (§9).
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
| Rate spread of parts | level n | δ_n = 0.096 / C_n (dimensionless spread held at C5's value) |
| τ_n for normalization and separation; τ_n for baselines | the level-n resonator alone; the intact world | kick RMS 0.3; horizon 10 C_n, sampled every 0.1 C_n; e-folding estimator; censoring at the horizon recorded, never imputed (§3) |
| G→M, M→G, excitation and τ windows; sample interval | level n | × C_n |
| Doses (s, RMS), pulse 0.5 rad, margin 0.01 rad | level n | dimensionless, unchanged |
| Push size | the excited part | 0.2 × its L |
| Element contact gap 0.6; C4 law (A, B, J, K, k = 8, radius 3, dt) | element scale | **not scaled**: the physics does not rescale (§13) |
| Placement | element scale | contact at the 0.6 gap: bracketed in steps of 0.02 element units, then bisected to within 10⁻⁶ (no level-scaled radius) |
| Parts per world M = 5; minimum group size 3; K = 20 alternative groupings | counts | the same at every level |
| Effective-model recipe (E1 or E2, §7) | the published level-(n−1) states of a level-n group | built only from published fields; zero parameters fitted on scored excitations; the same recipe at both transitions; integrated at the element dt, sampled at 0.1 C_n |
| E2 finite differences and convergence | each part's own L; the level's C_n | steps of 10⁻⁴ L_part (position) and 10⁻⁴ rad (phase); convergence of J̃ = C_n D J D⁻¹ in the Frobenius norm, ≤ 10⁻³ × max(‖J̃‖, 1) |
| Normalized error r and the response floor | the scored non-excited parts | r = error_model ÷ error_no-transfer, defined only when the response is ≥ 0.01 (the registered margin); ceiling 0.5 on the CI upper bound of the mean (D8) |
| `unit_specificity` alternative groupings | level-(n−2) sub-parts regrouped into fake level-(n−1) parts | the same size profile, contiguous over the sub-part contact graph, each fake part mixing sub-parts of at least two real parts; composed by the same `compose_state` |
| `unit_specificity` probes and scoring | probes: seeded level-(n−2) sub-parts chosen independently of any grouping; scoring: elements outside the probed sub-part | pulse 0.5 rad; push 0.2 × L* (published L of a resonator sub-part; for a single element, the median nearest-neighbour element spacing of the group at s₀); **linear paired-response summaries** (arithmetic mean of member probed-minus-control responses); an evaluator-only membership decoder fixed at t₀; RMS phase plus RMS position over the element spacing, on the same elements for every grouping |
| Paired-response summary (all scoring) | the members of a part | arithmetic mean of member paired responses: unwrapped phase and displacement; identical for real and fake parts and at every level |
| Effective-state position and size bounds | level n | fractions of L, unchanged |
| Formation time (`scale_separation`, reported) | the level-n group, from assembly | link rule on frames every C_n over the whole horizon; reported in C4 time units and in units of the parts' own τ; censored at the actual formation horizon max(100 C_n, 30 C_k) (§4) |
| Static-control rates (`not_a_clump`) | each level-(n−1) part | each part's rates shifted by one constant so its isolated rate is 0. This leaves its internal rates untouched. At level 2 it equals C5's "all rates 0"; at level 3, zeroing every element rate would turn the parts into different objects. |
| In-place recovery of a level-k part inside a parent (`parts_in_situ`) | the part's own level k | pattern return within the part's own pattern tolerance after its own-level kick, over 30 C_k. **Not membership:** the part's level components inside a parent see the parent's whole cluster, so a Jaccard match against them would fail by construction. Membership is the parent's own criterion 5. |

**Cross-level reads, allowed only on the evaluator side.** The candidate path (detector, promotion, composition, effective model) never reads below the level it acts on. Six evaluator-side quantities cross levels deliberately, and each says so in its endpoint:
- `upward_transfer_l3`: a level-1 pulse, read in level-2 states;
- `unit_specificity`: predictions from different groupings lifted to the same elements, so they can be compared;
- `coarse_depth`: a flat model on level-1 states, as a comparison;
- `coarse_error_decomposition`: a rigid reference on elements;
- `interface_fidelity`: an element-level census;
- the views from below in `formation_outcomes`: the C4 component view and the level-2 detector on level-3 worlds.

Each side of such a quantity is measured in its own level's units.

## 3b. Development pilot (2026-10-02, owner-requested; not evidence)

The owner asked whether the open risks could be checked before registration.
- *What ran:* a development-only pilot, with scratch code outside the repository and pilot entropy 44444. That entropy is neither the C5 development nor the C6 development entropy, and no final entropy exists yet.
- *What it reused:* the frozen C4/C5 functions, applied at provisional C₃ = 9.6.
- *What it changed:* nothing was registered and no repository code was changed.
- *Records:* scripts, raw results, logs, smoke files and hashes are committed in `evidence/c6_dev_pilot/` (N2), with a README marking the void result and the two scripts that never completed.

**Level 1 → 2, C5 rules unchanged:**
- 2,400 C4 worlds gave 2,669 templates.
- 320 level-2 worlds gave FORMED 148 (0.46, Wilson [0.41, 0.52]), MERGED 52, DRIFTING 97, APART 4 and OTHER 19. This replicates C5's near-threshold formation on a larger sample.
- 140 of 148 accepted groups were re-accepted alone.
- τ₂ alone had median 4.8 (1 censored). The median isolated group rate was 0.0075. Median L₁ = 0.45 and L₂ = 0.67.

**Level 2 → 3, 24 worlds per placement:**
- *Disk placement* (sequential, radius 2.5 × median L₂ / median L₁) gave 9/24 DRIFTING, with no coupling between separated groups. At spacing factor 0.6, neither sequential nor C5-style joint rejection placement found any placement.
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
- **Dynamic validity, on its own timescale.**
  - *Windows:* the observation interval is the last W = max(30 C_n, 30 C_k) of the formation run. It is split into consecutive, non-overlapping windows of 30 C_k, sampled at the part's own interval C_k, and a trailing remainder shorter than 30 C_k is not scored.
  - *The test:* the part must pass its own criteria 2–4, with its own level's thresholds, in **every** window.
  - *At least one complete window per part:* a parent faster than its parts would otherwise leave zero windows and pass vacuously (Codex F4). The formation horizon is therefore max(100 C_n, 30 C_k for every part level k), a generic rule that constrains no timescale ordering.
  - *Not observed means failed:* a part with no complete window still fails criterion 6, recorded as INSUFFICIENT_OBSERVATION.
- **Geometric distinctness, which has no timescale.** No other part's shape covers more than 0.2 of its shape's area at any parent frame.
- **Recursion.** A composite part satisfies criterion 6 for its own parts, each again on its own level's windows.

*Why per-window:* criteria 2–4 are fixed-amplitude tolerances (for example, pattern change ≤ 0.1 rad). Measured over a longer window, any slow, harmless drift accumulates beyond them. Judging a level-1 unit over a level-3 window (about 10× its own) mixes two levels in one rule and violates invariant 1. The first two drafts did exactly that. A real merger still fails through the geometric test, whatever the window.

*Consequences:*
- The owner records frames at the finest part level's interval (C₁ = 1 time unit) during every detection window. This is negligible extra storage.
- At level 3, every level-2 group is checked over windows of 30 C₂ and every level-1 unit inside it over windows of 30 C₁.
- *C5 inheritance:* C5 judged level-1 units over one level-2 window (3.2× their own). The old and new checks are **non-nested measurements**, not one stricter than the other. A longer window can reject slow drift, but it can also dilute a short excursion that one own-level window would catch (Codex F15 shows both on the frozen `window_statistics`). C5's accepted receipt and verdicts stand on their own registration. C6 uses neither C5's MERGED counts nor any claim of monotonic strictness, only its own fresh evidence.
- *A unit's shape:* the convex hull of its elements for a level-1 unit, and the union of its level-1 hulls for a composite. At level 2 this is exactly C5's rule. At level 3 it avoids false MERGED verdicts from the empty space inside the convex hull of a concave composite.
- *Area computation:* exact convex clipping at level 2. At level 3, an exact union-of-convex-pieces computation or a registered rasterization, with a contract bounding its error against exact clipping.
- *Degenerate shapes:* area ≤ 10⁻¹² L² fails (N3).

**Outcome per world**, the first that applies: FORMED, MERGED (a criterion-6 failure), DRIFTING (contact but no locked candidate), APART, OTHER.

**Promotion.** An accepted level-n candidate publishes exactly one level-n state through `c6_units.compose_state` (the `level_interface` gate). Publication is read-only.

## 5. Lower levels stay real; upward and downward paths; real units

- **Alive and dynamic.** The full simulation always integrates every element. Promotion never deletes, freezes or replaces members (invariant 2). Coarse models are predictions scored against the full model and are never substituted into it. Recursive criterion 6 holds over the window. Two further measures for every accepted level-3 group are descriptive (`parts_in_situ`):
  - each level-2 part's own recovery **in place**: the level-2 kick, then pattern return within the level-2 pattern tolerance over 30 C₂, on the part's own units. Membership is not re-tested here, because inside a parent the level-2 components see the whole parent cluster (§3a);
  - τ₁ and τ₂ inside the level-3 world against their values alone.
- **Upward (`upward_transfer_l3`).** Rotate the phases of **one level-1 unit** (seeded choice) inside one level-2 group by 0.5 rad. Measure the response of the **other level-2 groups'** published Θ: intact minus the same world with level-2 groups decoupled, where it is 0 by construction. Margin 0.01 rad. The disturbance must cross two levels.
- **Downward (`downward_effect_l3`).** The phase offsets of the elements of each level-2 group's **published** ports (the selected port variant), relative to its own Θ, inside the level-3 group against decoupled; margin 0.01 rad. The same shift for level-1 ports (two levels down) is descriptive. The whole acts only through the element law.
- **Emergent transfer (`emergent_transfer_l3`).** Pulse a whole level-2 group's phase by 0.5 rad and measure the other groups' response, intact minus decoupled, margin 0.01 rad.
- **Unit specificity (`unit_specificity_l2`, `_l3`; one function): are the real groups real units?** Locked §7 defines a scale as a level whose resonator works as a unit in further interactions. The test asks whether the *real* level-(n−1) parts of a group are better units than other groupings of the same material.
  - *Alternative groupings:* K = 20 seeded groupings of the group's level-(n−2) sub-parts into fake level-(n−1) parts. They have the true size profile, are contiguous over the sub-part contact graph, and each fake part mixes sub-parts of at least two real parts. At n = 2 the sub-parts are elements; at n = 3 they are level-1 units.
  - *Fake parts are published by exactly the same procedure as real parts:* `resonator_state` at level 1 and `compose_state` at level ≥ 2. That includes the measured isolated rate: each fake part is run alone over its own level's window, as real parts are. Any shortcut for fake parts, such as a size-weighted rate, would handicap them and bias the test toward the real grouping.
  - *The sub-part contact graph:* two sub-parts are adjacent when any of their elements are C4 neighbours (k nearest within the radius) at s₀.
  - *Partition-independent probes (Codex F14).* Exciting a *real* part rigidly would favour the real grouping by construction (Codex's first counterexample). So the specificity probes are chosen **before and without reference to any grouping**:
    - four seeded level-(n−2) sub-parts per group, drawn uniformly;
    - each one is pulsed by 0.5 rad and, separately, pushed by 0.2 × its primitive-or-published length L* (ledger: L* is its published L for a resonator sub-part, and the median nearest-neighbour element spacing of the group at s₀ for a single element, which has no L of its own);
    - every push is rigid, in the full model;
    - these probes are separate from the real-part excitations of §6 and §7, which stay for `coarse_vs_full`.
  - *Linear paired-response summaries (the convention, used throughout C6).* A part's **response** is the arithmetic mean of its members' paired responses (probed minus unprobed control): unwrapped phase differences, and displacement differences. This applies to the truth, to each grouping's effective-model input (control published state + this summary of the probe) and to the model's lifted output.
    - *Why linear:* a circular mean is nonlinear, so an incoherent fake part's phase swings far more under the same poke than a coherent real part's does. Codex's re-check showed that this alone gives the real grouping a positive score in a flat system with heterogeneous phases. With linear summaries, a flat linear system scores **identically for every grouping at every time and for every initial phase**: the probed element's part has the same size profile in every grouping, and only its partners carry error.
    - *For coherent real parts:* the linear summary equals the circular-mean response to first order, so C5-style scoring is unchanged in substance.
  - *The evaluator-only decoder (Codex F3, simplified).* With linear paired responses, element offsets cancel. The decoder holds only each grouping's membership map, fixed at t₀, and predicts each element's response as its part's predicted response. There are no offsets and no separately frozen branch offsets, so Codex's offset convention question does not arise. The effective model never sees the decoder, and no later full state updates it.
  - *Common scoring:* every grouping is scored on the **same** elements, all elements outside the probed sub-part, over the 10 C_n window.
  - *World statistic:* the mean over the 4 sites × 2 probe types of (mean lifted error of the alternatives − lifted error of the real grouping).
  - *Required contracts (the binary null criterion):*
    - **Heterogeneous flat null:** Codex's nine-element arithmetic-consensus fixture (initial phases −2, −2, −2, 0, 0, 0, 2, 2, 2 rad; real triples against all 36 balanced mixed partitions; every probe site; oracle linear summaries) must give a statistic of 0 to within 10⁻¹² at every sample time.
    - **Homogeneous flat null:** the same with equal phases must also give 0.
    - **Modular positive fixture:** two strongly coupled triples weakly coupled to each other must give a statistic > 0.
    - **Real-part alignment check:** probes must be drawn before groupings exist.
  - *Why this tests real units:* in a flat blob, any contiguous grouping is as good a unit as any other, so the statistic is about 0.
  - *Cost:* coarse runs, plus one isolated-rate run per fake part (K × parts runs, each over its own level's window, on 25–60 elements). That is small next to the level-3 runs.
- **Scale separation (`scale_separation_lN`; a registered RRG prediction, doc 02 §5).** Bigger scales should take more time and more distance.
  - **Relaxation time (verdict):** τ_n of the group alone ÷ the mean τ_{n−1} of its parts alone, both measured by the same protocol on their own level's windows.
  - **Formation time (reported):** the first time from assembly after which the eventually accepted group stays one locked component (the level-n link rule on frames every C_n over the whole horizon). It is given in C4 time units and in units of the parts' own τ, with censoring counted. It is censored at the actual formation horizon, max(100 C_n, 30 C_k) (§4). It is not given a verdict because that horizon itself grows with the measured C values. A level-3 group can therefore show formation times that a level-2 run is too short to record, which biases the comparison toward "bigger is slower".
  - **Size (reported):** L_n ÷ the median L of the parts. A composite is larger by construction, so size growth is reported, not tested.
  - It never enters H-C. Requiring "slower" for a scale would narrow locked §7, but the prediction itself is tested.

## 6. Interventions, predictions and complete ablations

The same protocol applies at both transitions. Every run is paired with an unperturbed control from the same formed state s₀, and every ablation is matched on s₀. The world is the unit of analysis: its value is the mean over its accepted groups. CIs are bootstrap 95% (10,000 resamples). The doses are C5's, dimensionless and identical at both levels.

| Test | Intervention (parts' insides held bit-identical) | Registered prediction | Complete matched ablation |
|---|---|---|---|
| **G→M** | Scale each part's centroid offset from the group centroid by s (rigid moves). Both runs get the same zero-mean part-phase probe (RMS 0.3). | The inter-part pattern deviation **increases**. | `no_geometry_to_mode`: w = 1 and the phase topology frozen at s₀ (the effect is exactly 0 by construction) |
| **M→G** | Rotate each part's phases rigidly by a zero-mean kick of fixed RMS. | The peak radius of gyration of the part centroids **increases**. | `no_mode_to_geometry`: J = 0 (exactly 0) |
| **Dose-response** | G→M at s = 1.1 / 1.25 / 1.5; M→G at RMS 0.5 / 1.0 / 1.5. Each ladder is one controlled-size family, and any other dose is refused. | The means do not decrease, and the highest-minus-lowest per-world difference has CI > 0. | (intact) |
| **G→M channels** | Only w = 1, or only the frozen topology. | Descriptive. | — |
| **Upward, downward, emergent, unit specificity** | §5. | Above the margin; real groupings predict better than alternatives. | Decoupling (0 by construction); alternative groupings |
| **Coarse vs full** | Held-out excitations on one part (seeded choice): a phase pulse of 0.5 rad and a radial push of 0.2 × its L. | §7. | — |

The primary doses are s = 1.25 and RMS 1.0. Single-channel ablations are decomposition only.

*How level-n operations act:* each operates on the level-(n−1) **published** state.
- *G→M scaling:* `c5_compose.scale_units` scales the published part centroids, which are unweighted centroids of child centroids. The resulting translations are applied rigidly to the owned elements with `shift_units`.
- *Pushes:* a push uses the excited part's published L.

## 7. Full versus effective model at both transitions (locked §7; doc 03 §13 and §37)

The locked core defines a scale through prediction: a reduced set of variables predicts the level's interactions with bounded error. It does **not** require the reduced dynamics to be the same law as the level below. C6 therefore separates two claims:
- **The core claim (`coarse_vs_full_lN`, part of H-C).** The registered effective-model recipe predicts with bounded error.
- **The stronger optional claim (`same_law_closure_lN`, its own verdict).** The *same* element law applied to the published summaries predicts with bounded error. This is the "same equation family" universality that the locked core leaves optional.

**Who reads what.**
- The effective model at transition n receives **only the published level-(n−1) states** of the group's parts. At transition 3 it never reads level-1 states or elements: the standard's "an R₂ query reads R₁ effective states".
- A contract checks the input type, and a mutant passing level-1 states must be detected.

**Two pre-declared recipes, each built only from published fields, with no parameter fitted on scored excitations:**
- **E1, same law.** `c5_coarse.run`, unchanged: the C4 element law applied to the parts' ports, with links forming and breaking by the C4 neighbour rule.
- **E2, linear response: a candidate linear-response reduction motivated by doc 03 §28 and §39.** It is not a guaranteed Hessian reduction, because the C4 law is first-order and not a gradient flow.
  - *The Jacobian:* J is the Jacobian of E1's right-hand side with respect to the parts' (X, Θ). It is evaluated at the **published control state at t₀**, in the frame co-rotating with the control (E1 depends only on phase differences), with links held at t₀.
  - *Central-difference steps:* position steps of 10⁻⁴ × the part's L (size-normalized, so the step is the same dimensionless size at every level) and phase steps of 10⁻⁴ rad.
  - *A convergence check, in dimensionless coordinates (Codex N2):*
    - J is first expressed as J̃ = C_n · D J D⁻¹, with D = diag(1/L_part for each position coordinate, 1 for each phase), so positions are in units of each part's own L and time is in units of the level's C_n.
    - The check passes if ‖J̃_h − J̃_{h/2}‖_F ≤ 10⁻³ × max(‖J̃_{h/2}‖_F, 1); the max with 1 covers a near-zero Jacobian.
    - If it fails, E2 abstains for that group, and an abstention is scored as predicting no response.
  - *The response:* δ₀ = published(excited, t₀) − published(control, t₀), with phases wrapped, and the paired prediction is δ(t) = exp(J t) δ₀.
  - *The matrix exponential:* a general method, scaling and squaring with a Taylor or Padé core in NumPy, with no eigendecomposition. Contracts require it to match a diagonalizable case's eigen-solution, to return I + tJ for the Jordan block [[0,1],[0,0]], and to fail loudly on non-finite input.
  - This is a different, linear family, derived from the published summary.

**Two pre-declared port variants:**
- **V1:** C5's rule. Ports are the hull members; a composite's ports are the child ports on the hull of all child ports.
- **V2:** the hull members plus every member with an active cross-part C4 neighbour at publication. This follows "derived from active lower boundary interactions" literally.

**Selection.**
- Exactly one combination of recipe and port variant is registered, chosen on development data by the coarse readiness check (§9). It is the same combination at both transitions.
- `same_law_closure` always uses E1 with the registered port variant.

**Scoring.**
- *Open loop:* the scored prediction never receives full-model states. The reopening protocol (invariant 8) runs alongside and is reported: invalid flags, reopens, and error on flagged against unflagged excitations, which shows whether the validity bound carries information.
- *Per excitation type (D4):* gain_{e,b} = error_b − error_model per world, for e ∈ {pulse, push} and each baseline b. The error is C5's response error over the non-excited parts (RMS phase plus RMS position over L), applied to the linear paired-response summaries (§5). Phase and position parts are stored separately.
- *Bounded predictive error* requires two things, for both excitation types, at each transition:
  1. **The model beats every cheap baseline** (the six gains, as accepted in D4).
  2. **The model's error has an absolute ceiling (Codex F5; D8).** The normalized error r = error_model ÷ error_no-transfer is the model's error relative to the size of the actual response (error_no-transfer is the error of predicting no response). The CI upper bound of its mean across worlds must be ≤ **0.5**.
     - **The response floor (Codex N1).** r is defined only for an excitation whose actual response size, error_no-transfer, is at least **0.01**: the registered meaningful margin already used for every zero-by-construction effect, in the same phase-plus-position metric. An excitation below the floor is labelled BELOW_RESPONSE_FLOOR, is counted and reported, still enters the six gains, and is excluded only from r.
     - *Per world:* r is the mean over that world's eligible excitations of the type. A world with none is r-ineligible for that type.
     - *Minimum:* the ceiling needs at least 10 r-eligible worlds per type; otherwise this part is INCONCLUSIVE.
     - *Readiness:* the readiness check applies the same rule on development data. The model must therefore capture at least half of the observed response, which baseline dominance alone does not guarantee: errors of 99.9 against 100 beat every baseline and still predict almost nothing.

  The conjunction is an intersection-union requirement: all parts must pass.

**Baselines,** the same at both transitions, all required:
1. no transfer;
2. rigid transfer;
3. relaxation to an equal share, with the group's own in-world relaxation time **for the excited channel**: the phase e-folding after the probe for pulses; the position e-folding of the s = 1.25 G→M return for pushes. The calibration advantage is declared.

**Descriptive only:**
- `coarse_error_decomposition`: a rigid-all-members reference (every member a port) splits the error into rigidity error and port-restriction error.
- `coarse_depth`: at transition 3, the registered recipe on level-2 states against the same recipe on all level-1 states of the same units.
- Work counts, frequency error and recovery-time error.
- `compression_ratio` (doc 03 §18): lower-level degrees of freedom (3 per element) ÷ the published state's degrees of freedom (3 per part plus 3 per port). Reported per level, with no verdict.

**Why this matters for the AI goal (§0).** The registered recipe *is* the abstraction operator an RRG-style AI would use. A node's published summary is enough to predict what its neighbours do next, and the same recipe works one level higher. C6 measures whether it holds; C8 measures whether it is cheaper.

## 8. Endpoints and verdict rules (every endpoint evaluated or listed in `not_run` with a reason)

The minimum for any inferential verdict is **10 formed worlds** at that level; below it, the endpoint is INCONCLUSIVE.

**Composition endpoints:**
- transition 2: `downward_effect_l2`, `emergent_transfer_l2`, `effective_state_l2`, `coarse_vs_full_l2`, `unit_specificity_l2` (5);
- transition 3: the same five at level 3, plus `upward_transfer_l3` (6).

Each composition endpoint tests a locked-core clause (§0). The optional extensions (`same_law_closure_lN`, `scale_separation_lN`) have their own truth-table rows and never enter H-C.

| Endpoint | Rule (rows in order) |
|---|---|
| `level1_pool` (gate) | Every used level-1 unit, alone with its rate, is re-detected by the frozen C4 detector. |
| `level2_pool` (gate) | Every used level-2 template, alone with its shifted rates, is re-detected by `detect_level` at n = 2 (the harvest filter, re-checked). |
| `harvest_isolation` (gate) | No C4 world feeds two level-2 worlds, and no level-2 harvest world feeds two level-3 worlds. Source paths are stored. |
| `same_rule_audit` (gate) | Level-n thresholds equal `level2_thresholds(C4, C_n)`. Detector, promotion, composition, effective-model and unit-specificity calls are the same function objects at both levels, and the registered recipe and port variant are the same at both transitions. The static no-level-branch check passes. C₂, C₃, every τ and the final measured ratios are recorded. |
| `backend_equivalence` (gate) | Checks 1–4 of §10, each yes/no; all must pass. |
| `numerical_checks` (gate) | C4's checks on an assembled level-3 world (RK4 order, switching dt error, equivariance under permutation, translation, rotation and global phase), plus unit and group relabelling, plus exact decoupling (each group alone equals its decoupled run within 10⁻⁹). |
| `level_interface` (gate, N1) | At both levels, exactly one published parent per accepted candidate **per world**, matched by unit set: no duplicates, omissions or swaps. Every numeric field finite. Ports and mode well-formed. S equal to the candidate's statistics. Digest derived from the children. Gate: not FAIL. |
| `not_independent_l2/_l3`, `not_a_clump_l2/_l3` (gates) | Decoupled continuations with imposed candidates (the intact candidates, or proximity-only components when none exist). With the assembled rates, rejection is expected by criterion 3. With each part's isolated rate shifted to 0 by one constant per part (§3a), rejection is expected by criterion 5. **FAIL** if any candidate is accepted; **PASS** if at least one was tested and none was accepted; **NOT_TESTED** if none. Gate: all PASS. |
| `formation_l2`, `formation_l3` | Fraction of FORMED worlds, Wilson 95% CI. (1) **PASS** if the lower bound ≥ 0.5 and ≥ 10 worlds formed; (2) **FAIL** if the upper bound < 0.5; (3) **INCONCLUSIVE** otherwise (D3). |
| `formation_outcomes_l2/_l3` | Descriptive: outcome counts, per-criterion failures, the C4 component view and, at level 3, the level-2-detector union view. |
| `g_to_m_lN`, `m_to_g_lN` (N = 2, 3) | (1) **INCONCLUSIVE** if fewer than 10 formed worlds; (2) **FAIL** if the intact CI includes 0 or lies below it; (3) **PASS** if the complete-ablation CI includes 0 or its \|mean\| ≤ 0.2 × the intact mean; (4) **INCONCLUSIVE** otherwise. |
| `dose_response_lN` | Per direction: (1) **INCONCLUSIVE** if fewer than 10 worlds; (2) **PASS** if the means do not decrease and the highest-minus-lowest CI > 0; (3) **FAIL** if that CI < 0; (4) **INCONCLUSIVE** otherwise. The endpoint fails if either direction fails and passes only if both pass. |
| `downward_effect_lN`, `emergent_transfer_lN`, `upward_transfer_l3` | Margin 0.01 rad: (1) **INCONCLUSIVE** if fewer than 10 worlds; (2) **FAIL** if the CI upper bound < 0.01; (3) **PASS** if the CI lower bound > 0.01; (4) **INCONCLUSIVE** otherwise. |
| `effective_state_lN` | C5's bounds (position 0.25 L, size 0.05, frequency 0.01 / C_N). (1) **INCONCLUSIVE** if fewer than 10 formed worlds; (2) **PASS** if ≥ 90% of published parents meet every bound; (3) **FAIL** otherwise. |
| `coarse_vs_full_lN` | The registered recipe (§7). Six paired open-loop gains per world (2 excitation types × 3 baselines), and the normalized error r per excitation type over r-eligible worlds (response ≥ 0.01; BELOW_RESPONSE_FLOOR counted). (1) **INCONCLUSIVE** if fewer than 10 worlds, or fewer than 10 r-eligible worlds for either type; (2) **FAIL** if any gain CI upper bound < 0, **or** any r CI lower bound > 0.5; (3) **PASS** if every gain CI lower bound > 0 **and** every r CI upper bound ≤ 0.5; (4) **INCONCLUSIVE** otherwise. Reopening, flags, the error split, frequency, recovery and work are reported, never scored. |
| `unit_specificity_lN` | Per world, the mean over the 4 grouping-independent probe sites × 2 probe types of (mean lifted error of the K alternative groupings − lifted error of the real grouping). Groups with no valid alternative grouping are NOT_TESTED and counted. (1) **INCONCLUSIVE** if fewer than 10 tested worlds; (2) **FAIL** if the CI upper bound < 0; (3) **PASS** if the CI lower bound > 0; (4) **INCONCLUSIVE** otherwise. |
| `same_law_closure_lN` (optional extension) | E1 with the registered port variant, scored exactly as `coarse_vs_full_lN` (same six gains, same rows). |
| `scale_separation_lN` (registered RRG prediction) | Formation time and size are reported (§5). The verdict is on relaxation time, using **valid bounds only, never an imputed value** (Codex F7). Per world, the ratio is ρ = τ_N of the group alone ÷ the mean τ_{N−1} of its parts alone.<br>**Lower bound ρ_lo:**<br>• a censored numerator enters at its censoring limit, which is valid as a lower bound;<br>• if any denominator τ is censored, ρ_lo = 0, so that world gives no support.<br>**Upper bound ρ_hi:**<br>• a censored numerator gives ρ_hi = +∞, so that world cannot support FAIL;<br>• a censored denominator enters at its limit.<br>**Rows:** (1) **INCONCLUSIVE** if fewer than 10 worlds; (2) **PASS** if the bootstrap CI lower bound of mean ρ_lo > 1; (3) **FAIL** if the bootstrap CI upper bound of mean ρ_hi < 1 (worlds with ρ_hi = +∞ make this impossible); (4) **INCONCLUSIVE** otherwise.<br>These are bound-based claims: PASS means the true mean exceeds 1 even under the least favourable resolution of the censored values. |
| `variation_lN` | Descriptive (locked §6): the distribution of formed groups by part count, phase-pattern type (all inter-part offsets within the pattern tolerance of 0 means in phase; otherwise offset), and shape (L of the group ÷ median L of its parts, in quartiles). |
| `g_to_m_channels_l3`, `parts_alive_l3`, `parts_in_situ_l3` | Descriptive: single-channel effects; recursive criterion-6 values for every part of **every** candidate; in-place recovery and τ inside against alone. |
| `interface_fidelity`, `coarse_error_decomposition`, `coarse_depth`, `compression_ratio` | Descriptive (§3, §7). Raw values are stored. |

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
| Same-law closure (optional RRG extension) | 1 | `same_law_closure_l2` or `_l3` = FAIL | NOT_SUPPORTED |
| | 2 | H-C = SUPPORTED_WITHIN_SCOPE and both = PASS | SUPPORTED_WITHIN_SCOPE |
| | 3 | otherwise | INCONCLUSIVE |
| Scale separation (registered RRG prediction) | 1 | `scale_separation_l2` or `_l3` = FAIL | NOT_SUPPORTED |
| | 2 | both = PASS | SUPPORTED_WITHIN_SCOPE |
| | 3 | otherwise | INCONCLUSIVE |

A NOT_SUPPORTED optional extension rejects that extension only. It never changes H-C or the locked core (proof matrix; `05_CHANGE_CONTROL.md`).

**Multiplicity scope (Codex F12).**
- Every individual endpoint interval and verdict is **nominal** (95%, uncorrected).
- The central H-C claim is an **intersection-union** requirement: every component must pass, which only makes support harder.
- Endpoint verdicts reported alongside are not family-wise evidence.
- Development readiness gains are **selection-biased** (the best of four combinations) and are readiness measurements only. The final test of the selected recipe runs on fresh worlds.

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
  1. **Criterion 6 on each part's own timescale (§4).** The old rule judged parts over a window longer than their own (3.2× at level 2, about 10× at level 3). Fixed-amplitude tolerances then reject harmless slow drift, so some of the MERGED losses may come from this. At level 3 in the pilot, every candidate failed this check, so its effect there cannot yet be separated from real failures.
  2. **Contact placement (§3).** A composite couples only where it touches, so every part starts in contact. Disk placement left 9/24 pilot worlds DRIFTING with no coupling at all.
- *These are not tuning:* each is fixed by the principle before any formation number under it is seen. Neither has a free parameter to adjust.
- *Whether they reach the target is unknown.* The design gate measures it once, and there is no grid to search.

**Design gate (development entropy only, before registration; `tools/c6_design_gate.py`).** Every step writes raw per-world values to a committed artifact pinned by hash in the manifest (N2). Development outcomes are settings, not evidence.
1. **Formation.**
   - 30 development worlds at level 2 and 30 at level 3, with contact placement and the corrected criterion 6.
   - Target: formation ≥ 0.75 at both levels. Below 0.75 at either level means stop and report, with the per-criterion failure counts.
   - *Two passes, so the gate measures the settings that get registered:*
     - pass 1 runs at provisional C₂ = 3.2 and C₃ = 9.6, and measures C₂ and C₃ alone (§3);
     - pass 2 re-runs formation at both levels on fresh development worlds (same entropy, new purpose) at the measured and rounded C₂ and C₃, with δ_n = 0.096 / C_n.
   - Only pass 2 counts against the target. A further change in C between passes is reported, not iterated.
2. **Timescales.** C₂ and C₃ are measured alone under contact placement. τ₁, τ₂ and τ₃ alone must each be censored in fewer than 50% of development measurements (stop rule 2), and C₂ must lie within [1.6, 6.4], which is C5's T = 3.2 within a factor of 2 (stop rule 3).
3. **Interface fidelity.** C5's and C6's composition rules are compared on development parents: rate error against the observed rate, and coarse cross-link counts against the element-level census. C6's rule must be at least as faithful on both measures.
4. **Coarse readiness.** At both transitions, on development groups, compute the six gains for each of the four pre-declared combinations (E1 or E2) × (V1 or V2), and the error decomposition.
   - The combination with the largest worst-cell mean gain at the worse transition is registered. This gain is selection-biased (the best of four) and is a readiness measurement only.
   - A combination whose E2 Jacobian fails the convergence check on more than half of the development groups is excluded.
   - It is used only if both hold at both transitions, on at least 10 development groups per transition:
     - its worst-cell mean gain is > 0;
     - its mean normalized error r is ≤ 0.5 for each excitation type (the D8 ceiling), over at least 10 r-eligible development groups per type;
     - at most 10% of in-world relaxation calibrations are censored.
   - Otherwise, or with fewer groups, stop and report.
5. **Overlap calibration, with a population that does not depend on acceptance (Codex F9).**
   - *Population:* every pair of level-2 **input templates**, the harvested parts, in contact at the end of the development level-3 formation runs, **whether or not** any level-3 candidate is accepted.
   - *"Intact":* both parts pass the dynamic part of criterion 6 (their own criteria 2–4 on own-level windows), which does not involve the geometric cut.
   - *Recorded:* the pre-cut union-of-hulls overlap of every such pair, as raw values.
   - *Stop:* any intact pair above 0.2 means stop (stop rule 6). An empty population also means stop.
6. **Runtime projection** from measured per-world costs (§10).

If any check fails (stop rules 1–7 in §12), the implementer **stops and reports to the owner before registration**. The law, the thresholds and the margins are never changed to make composition or prediction succeed. A failure here is itself a finding. The owner can then:
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
  - 400 level-2 harvest worlds. About 300 are needed: 40 × 5 groups ÷ (0.75 formation × 0.95 re-acceptance alone). Each level-2 world yields at most one group, so isolation discards none. The rest is margin;
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
- *Per group:* the lifted error of the real grouping and of every alternative grouping, per excitation, and each grouping's member sets and isolated rates.
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

`milestones/c6.json` lists the C4 and C5 files, both manifests and the C++ source and build tool as dependencies.

**Required pipeline engineering (Codex F10 note).** The current preflight has no native build step, and command stages time out at 3,600 s. Before any panel, the implementer extends the shared pipeline tools, which are pinned rather than frozen and may lawfully be improved for C6:
- an enforced build of the kernel, with the compiler-pin check, in the preflight;
- a registered per-stage timeout that covers the approved runtime projection.

No unsupported extra stage is added to the exact-schema milestone configuration.

**New files.**
- `geomind/c6_levels.py`: owner tree, per-frame published series, `detect_level`, recursive criterion 6, threshold scaling, alternative groupings and the unit-specificity statistic.
- `geomind/c6_effective.py`: recipe E2 (linear response from the published state) and the lift-to-elements scorer. Recipe E1 is `c5_coarse.run`, unchanged.
- `geomind/c6_units.py`: the corrected `compose_state`, isolated-rate measurement, port variants, level-2 harvest with filter and source paths, and the N1 validator.
- `geomind/c6_compose.py`: level-n assembly with internal rates kept and the rotating-frame offset.
- `geomind/c6_experiment.py`: one transition protocol called at n = 2 and n = 3, evaluation and truth tables.
- `geomind/run_c6.py`: the runner, which calls `check("c6", "panel")` itself.
- `native/c6/element_law.cpp`, `geomind/c6_native.py`, `tools/build_c6.py`: the C++ engine (§10).
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
- *Unit specificity:*
  - a synthetic fixture with two rigid sub-groups, where the real grouping predicts better;
  - a flat fixture where no grouping is better;
  - alternative groupings are contiguous, keep the size profile and mix real parts;
  - every grouping is scored on the same element set;
  - probes are drawn before any grouping exists;
  - the decoder's offsets are fixed at t₀;
  - the heterogeneous and homogeneous flat-consensus nulls give a statistic of 0 to within 10⁻¹² at every sample, and a modular fixture gives a positive one (F14, re-check);
  - responses are summarized linearly (arithmetic mean of member paired responses), never by circular means;
  - a single-element push uses the median nearest-neighbour spacing (N6).
- *Response floor and censored calibration:* below-floor excitations are excluded from r only and counted (N1); a censored in-world τ uses the admissible grid, with gain_lo for PASS and gain_hi for FAIL (N5); the E2 convergence test is unchanged under a rescaling of position units (N2).
- *Criterion 6 observation:* a parent faster than its parts still gets at least one complete own-level window per part, and a part with none fails as INSUFFICIENT_OBSERVATION (F4).
- *Censoring:* the scale-separation bounds behave as defined, including the ρ_hi = +∞ case (F7).
- *Placement:* the contact solve lands within [0.6, 0.6 + 10⁻⁶] (F11).
- *Effective recipes:*
  - the level-1 wrapper's measured rate reaches `natural_rate` (F1);
  - the E2 matrix exponential matches the eigen-solution when J is diagonalizable, gives I + tJ on the Jordan block, and fails on non-finite input;
  - E2 abstains when its Jacobian does not converge;
  - E2 matches E1 to first order for a small poke;
  - both receive only published states;
  - E1 is exactly `c5_coarse.run`.
- *Information boundary:* the detector and the level-3 effective model never receive member lists, rates or labels.
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
- *Unit specificity:* alternatives that are not contiguous; the real grouping included among the alternatives; groupings scored on different element sets; probes aligned to a real part; decoder offsets refreshed from later full states; fake parts published without the measured rate.
- *Error ceiling and censoring:* the normalized-error ceiling ignored; below-floor excitations silently dropped or included in r; a censored τ imputed as a point value; E2 run on an unconverged Jacobian; E2 convergence measured in raw coordinates; responses summarized by circular means; a single-element push of size 0.
- *Theory alignment:* scale separation or same-law closure entering H-C; formation time measured only in the window instead of over the whole horizon; E2 using a parameter fitted on scored excitations; a different recipe at each transition.
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
| One formed level-3 world | About 570 level-3 time units: formation 100, recovery 60, two controls with their recovery runs 180, G→M 50, M→G and excitations 100, upward 20, in-place checks 10, isolated rates 40; unit specificity adds coarse runs only. About 3.6× the measured 160-unit cost: **about 9 min** per process. An unformed world (about 340 units) takes about 5 min. |
| 40 level-3 worlds at 75% formation | about 5.4 process-hours, so **about 40–45 min on 8 processes** |
| Harvest (about 3,300 C4 and 400 level-2 worlds, with filter runs) and 40 transition-2 worlds | about 15–20 min wall |
| **Recorded panel, 8 processes** | NumPy ceiling: **≈ 1–1.5 h** at C₃ ≈ 10; **≈ 2 h** at C₃ ≈ 16. With the C++ engine: measured in the design gate (expected well below the ceiling). |
| Tests / smoke (1 development level-3 world on both engines, small harvest) / mutation probe | < 2 min / ≈ 15–25 min (the NumPy reference run dominates) / ≈ 2–5 min |
| Design gate (development only, before registration; two formation passes) | ≈ 1–1.5 h |

M = 7 would mean about 350 elements, roughly 3.4× the cost per step, so it is not proposed. If the design gate's projection exceeds **3 h**, the implementer returns to the owner before registering. The options would be n₃ = 30, or dropping the level-3 decomposition ablations.

**C++ engine (the owner's D6 answer).** The full model's numerical step, the C4 element law with RK4 and the k-nearest neighbour rule, runs in a C++ kernel. Python keeps everything else: assembly, detection, statistics, receipts. The frozen NumPy `c4_model.simulate` stays the **reference**, and the kernel must prove it matches before any run that counts. The kernel also serves the AI goal (§0): a fast, verified element-law engine is what an RRG prototype would run on.
- *Files:*
  - `native/c6/element_law.cpp`: a batched RK4 step with the C4 neighbour rule (k nearest within the radius, stable ties by element index, held for the four stages), every `Params` field and ablation preset, and the frozen-topology path;
  - `geomind/c6_native.py`: a ctypes wrapper with exactly the signature and return values of `c4_model.simulate`;
  - `tools/build_c6.py`: the build.
- *Build and toolchain pin (G10):*
  - The build uses `clang++ -std=c++17 -O2 -fno-fast-math -ffp-contract=off`, the same flags as C2's kernel.
  - The manifest registers the exact compiler identification line (now `Apple clang version 21.0.0 (clang-2100.3.34.2)`) and the flags.
  - `tools/build_c6.py` refuses to build if either differs.
  - The build record (compiler, flags, source and binary SHA-256) goes into the pipeline artifacts, and the receipt binds it.
  - A container or Nix pin is out of scope. A changed compiler identification or flags stops the work (stop rule 13). This is a local toolchain check, not a hermetic pin: SDK and libm changes that leave the identification line unchanged are not covered, although checks 1–3 rerun at every tests stage would catch numerical drift. The remaining gap is a stated reproducibility limitation.
- *Equivalence protocol against the NumPy reference (gate `backend_equivalence`).* Each check is yes/no:
  1. **Neighbour selection:** indices and masks are identical (exact integers) on 1,000 random states and every development state checked.
  2. **One RK4 step:** |difference| ≤ 10⁻¹² × max(1, |value|) in x and θ, for the intact model and every ablation preset, including frozen topology. θ is unwrapped and can grow large, so the bound is relative above 1.
  3. **Held-neighbour trajectories:** 1,000 steps, max difference ≤ 10⁻⁹.
  4. **End to end on development worlds:** 10 level-2 and 5 level-3 development worlds run with both engines. In every world, the formation outcome and accepted candidate sets are identical, and every detector statistic agrees within max(10⁻⁶ × its magnitude, 10⁻⁹). The absolute floor matters because some statistics are near 0: C5 recorded a shape CV of 3 × 10⁻¹³, where a relative-only test would fail on rounding noise.
- *Where the checks run:*
  - checks 1–3 in the tests stage (fast);
  - check 4 in the design gate before registration, **before** any formation pass, so every design-gate number comes from the engine already shown equivalent; and on one world in the smoke stage;
  - any failure is stop rule 14.
- *Why not bit-identical:* libm `exp`, `sin` and `cos` differ from NumPy's in the last bits.
- *What check 4 shows, and what it does not:* it tests on 15 prespecified development worlds whether this changes any outcome. No failing world may be discarded to obtain equivalence. It does not prove equivalence of every verdict on every future world; that limit is stated.
- *Parallelism:* the kernel is single-threaded, and the runner uses 8 processes as before.
- *Mutants:* they act on the wrapper and the kernel's flags (ignoring an ablation flag, wrong tie order, dropping the J term). The equivalence tests must detect each one.
- *Speed:* unmeasured, because nothing may run before approval. The design gate measures it and re-projects the panel. The NumPy estimate above (about 1–2 h) is the ceiling.

**Frozen environment.** `pyproject.toml` and `uv.lock` are frozen (Python 3.9, NumPy 2.0.2, pytest 8.4.2). That rules out:
- SciPy, whose KD-trees would cut neighbour search but would change frozen files and tie order;
- Numba;
- Hypothesis; property checks stay hand-written randomized loops.

None is proposed.

**Process.** Verify once, in order: `tools/verify.py --milestone c6 --output evidence/c6_r001`. Before the design gate and before the panel, tell the owner how long each will take and why. One independent review follows, by the other model family, capped at 20 minutes. A design defect found before review means withdrawal through a decision record, and the next revision runs on fresh seeds.

## 11. C4/C5 lessons applied up front

| Lesson | Where C6 applies it |
|---|---|
| Ablations remove a pathway completely (C4 R001) | `no_geometry_to_mode` and J = 0 are primary; decoupling is literal; single channels are decomposition only. |
| Recovery and membership keep the original group (C4 R002 → R003) | Criterion 5 matches the original part set in both futures. Recursive criterion 6 tracks original member sets. In-place part recovery uses the same rule. |
| No verdict on fewer than 10 worlds | Every inferential endpoint, both levels. |
| One written rule, implemented row by row | Ordered truth tables with an enumeration test. |
| Non-vacuous controls with imposed candidates | Four decoupled controls with imposed candidates. Zero-by-construction effects carry a 0.01 rad margin. Unit specificity compares against real alternative groupings, not empty ones. |
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
| The experiment must test the theory as locked, not a narrower version (RRG `05_CHANGE_CONTROL.md`) | §0 maps every claim to a locked clause. Same-law closure is an optional extension and scale separation a registered prediction, each with its own verdict. Units are judged by the theory's own criterion (§7 of the locked core). |
| Every check is measured in its own level's units (invariant 1; the level-mixing criterion 6 of drafts 1–2, caught by the owner) | Normalization ledger (§3a), reproduced by `same_rule_audit` with a contract for completeness. Parts are judged on windows of their own level's length. |

## 12. Responsibilities and rules (binary)

Each responsibility has exactly one owner. Each rule is a yes/no condition with one fixed action. Nothing in this section is discretionary for the person it binds.

**Who owns what.**

| Role | Who | Owns | Never |
|---|---|---|---|
| Owner | The project owner | Approving or rejecting this proposal; decisions D1–D8 (D2–D7 answered on 2026-10-02; D1 and D8 open); the decision at every STOP; milestone status | — |
| Drafter | Claude (claude-opus-5-5) | This proposal's text, its ledger and its self-audits; decision record 0007 after approval. Every defect found in the proposal, whoever finds it, is fixed by the drafter and recorded in a self-audit with its cause. | Runs code before approval unless the owner explicitly asks (an owner-requested pilot goes to `evidence/c6_dev_pilot/`); approves its own proposal |
| Implementer | Codex (the owner's D5 answer) | The written design critique (first task), the C++ engine, the design gate, the registration (`experiments/c6_manifest.json`, `milestones/c6.json`), the `c6_*` code, its tests and mutants, the one pipeline run, the handoff | Changes the C4 law, a threshold, a margin, a dose, a baseline or a verdict rule after seeing any development or final outcome; edits frozen C4/C5 files or `.gate/`; bypasses a hook |
| Reviewer | Claude, the other model family from the implementer | One review of the committed evidence, capped at 20 minutes, written to `evidence/c6_r001_review_<family>/INDEPENDENT_REVIEW.md` | Reruns the panel; edits evidence or code |

**Stop rules.** Every row is checked. On STOP, the implementer reports to the owner with the measured values and does nothing else on C6 until the owner decides.

| # | When | Condition (yes/no) | If yes |
|---|---|---|---|
| 1 | Design gate, formation pass 2 | Formation < 0.75 at level 2 **or** at level 3 | STOP |
| 2 | Design gate, timescales | 50% or more of the development τ₁, τ₂ **or** τ₃ values measured alone are censored, so a required median is undefined | STOP |
| 3 | Design gate, timescales | Measured C₂ outside [1.6, 6.4] | STOP |
| 4 | Design gate, interface fidelity | C6's composition is less faithful than C5's on rate **or** on capacity | STOP |
| 5 | Design gate, coarse readiness | At either transition: fewer than 10 development groups, **or** fewer than 10 r-eligible groups for either type, **or** the selected combination's worst-cell mean gain ≤ 0, **or** its mean r > 0.5 for either type, **or** more than 10% censored in-world calibrations | STOP |
| 6 | Design gate, overlap | Any intact touching pair of input templates (§9 step 5) has union-of-hulls overlap > 0.2, **or** the population is empty | STOP |
| 7 | Design gate, runtime | Projected panel > 3 h on 8 processes | STOP |
| 8 | Before registration | Any proposal rule cannot be implemented as written | STOP (the drafter amends the proposal; the owner re-approves) |
| 9 | Pipeline | Any stage fails | The pipeline stops. Fix the cause, then rerun `tools/verify.py`: it skips only stages verified for **identical** code, and any code change reruns every stage its dependency fingerprint invalidates |
| 10 | Panel | Any gate in §8 fails | The run is not REVIEW_READY |
| 11 | Before review | The implementer finds a design defect | Withdraw the revision through a decision record; the next revision uses fresh seeds |
| 12 | Any time | A rule mixes levels outside the evaluator-side list in §3a | It is a defect: the drafter fixes the proposal before registration, or the implementer withdraws after |
| 13 | Build | The compiler identification line or the flags differ from the registered ones | The build refuses; STOP |
| 14 | Tests, design gate, smoke | Any `backend_equivalence` check fails | STOP; the owner decides between fixing the kernel and running on NumPy |
| 15 | Before registration | Decision 0007 (D7) is not committed, or the implementer's design critique is not committed | Registration refuses; STOP |

**Verdicts are binary in their inputs.** Every endpoint rule in §8 and every truth-table row is an ordered list of yes/no conditions with exactly one outcome. No endpoint is decided by judgement.

**Cross-family design check (required).** Claude drafted this proposal and Claude reviews the evidence, so the design itself needs a check by the other family.
- The implementer's (Codex's) first task, before any code, is a written critique of this proposal, capped at 20 minutes, committed as `docs/reviews/c6_proposal_critique_codex.md`.
- Any defect it finds triggers stop rule 8: the drafter amends the proposal, and the owner re-approves.
- No defect: the implementer proceeds.

**Why Codex should implement (D5).**
- Claude implemented C4 and C5, and Codex reviewed both.
- C6 is mostly new generic code over frozen C4/C5 functions, so continuity matters less than it did for C5.
- Codex knows those functions closely from its reviews; it found C5's F1–F4 and N1–N3.
- Alternating roles keeps one family from both building and judging the whole lane.
- The cost is that Codex has not used this repository's implementer workflow since C2; the pipeline and hooks are unchanged.

## 13. What C6 cannot show

- **Two transitions only.** No claim about R₃ or arbitrary depth.
- **No dissolution or reform:** that is C7. **No usefulness, compression or efficiency:** that is C8. `coarse_depth`, the error decomposition and the work counts are descriptive.
- **Staged assembly: the main gap against the theory.** Doc 02 Phase D asks for R₀ → R₁ → R₂ "without predefined levels". In C6, formation at each level is label-free, but each level is formed separately and then placed together, so the stages themselves are programmed. One-soup recursion needs units of different kinds to form, and C4's heterogeneous arm formed only 5/20. It is the natural successor to C6.
- **Passive structures only.** The C4 law has no energy input or dissipation budget (doc 02 §13, Phase E). C6 says nothing about actively maintained structures.
- **The depth is chosen, and there is no noise.** Doc 03 §19 lists two failure conditions: hierarchy depth controlled by the experimenter (6), and recursion that disappears when noise or initial conditions vary (7). In C6 the depth of two is set by staging. Robustness is tested across fresh seeds and initial conditions only, because the C4 dynamics are deterministic, so noise robustness is untested.
- **Variation is only described** (`variation`), not tested against locked §6.
- **Rate offsets are fixtures:** exact rotating-frame symmetries assigned by the experiment.
- **The physics does not rescale.** The element law's interaction range is fixed, so higher levels couple only through boundary contact. "Same rule" refers to the procedure (detection, promotion, composition, one effective-model recipe and the time-scaled thresholds), not to a scale-free interaction. Locked §7 allows different effective dynamics at different scales.
- **Narrow scope:** one model, one parameter set, M = 5, level-1 units of 6–16 elements.
- **Development choices.** The recipe and port variant are chosen on development data by a pre-declared rule, and C₂ and C₃ are measured there. The final evidence is fresh, but it is conditional on those choices.
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

1. **D1 — Approval. Recommended: approve as written.** This draft is aligned with the RRG locked core (§0). It includes the principle-derived rules: each part judged on its own level's windows, the normalization ledger (§3a), contact placement, the uniform τ and rate-spread definitions, units judged by the theory's own criterion, and the optional extensions separated from H-C.
2. **D2 — Corrected composition rule** (measured isolated rate, sibling-folded capacities, one function at both promotions). **Owner's answer (2026-10-02): accepted.**
3. **D3 — Formation rule:** PASS on the Wilson lower bound ≥ 0.5 (at least 27 of 40), FAIL on the upper bound < 0.5, INCONCLUSIVE otherwise; n = 40 per level; development target 0.75. **Owner's answer (2026-10-02): accepted.**
4. **D4 — Predictive gate:** the registered effective recipe (E1 same-law or E2 linear response, chosen on development data) must beat three baselines, with channel-matched τ, for pulses and pushes separately. A development readiness check can stop the work before the panel. Same-law closure is reported as its own optional verdict. **Owner's answer (2026-10-02): accepted** (separate scoring, with the stop).
5. **D5 — Roles. Owner's answer (2026-10-02): Codex implements and Claude reviews** (§12 assigns every responsibility and stop rule). Codex's first task is a written critique of this design (§12), because Claude both drafted it and reviews the evidence.
6. **D6 — Compute. Owner's answer (2026-10-02): plan a C++ engine** (§10): toolchain pinned by registered compiler line and flags, the NumPy model kept as the reference, and the `backend_equivalence` gate with stop rules 13–14. A projection above 3 h still comes back to the owner.
7. **D7 — Record the theory alignment in the R4 standard. Owner's answer (2026-10-02): accepted.** On approval, the drafter writes decision record 0007, stating:
   - invariant 1 ("same rule across scales") means the same procedure at every level: detection, promotion, composition, one effective-model recipe and thresholds scaled by measured size and time;
   - one physics in the full simulation;
   - the effective dynamics may differ from the element law (RRG locked §7), so same-law closure is an optional extension;
   - scale separation is tested as a registered prediction, not required for something to count as a scale.

   The standard's C6 section gets a one-paragraph pointer to 0007, and nothing else in it changes.
8. **D8 — Absolute error ceiling for bounded prediction (Codex F5). Recommended: accept r ≤ 0.5.** At each transition and for each excitation type, the CI upper bound of the mean normalized error error_model ÷ error_no-transfer must be ≤ 0.5: the model captures at least half of the actual response.
   - *Why 0.5:* it is the round, interpretable point where the prediction carries more of the response than it misses.
   - *Disclosure:* C5's accepted data were seen when drafting. There, the port law's median r was 0.38 on pulses and 1.09 on pushes, so pushes would fail unless C6's corrections help. The design gate's readiness check stops before the panel if they don't.
   - *Alternative:* no ceiling, which narrows H-C to "better than baselines". Codex judges that insufficient for R4's bounded-error requirement.

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

## Third self-audit (2026-10-02, owner-requested; reasoning only, nothing run)

Each rule was checked against the normalization ledger and the frozen code.
1. **In-place part recovery mixed levels (high).**
   - *The defect:* §5 applied the level-2 recovery rule, including its membership Jaccard, to level-2 parts inside a level-3 world. Inside a parent, the level-2 component rule links units across the parent's whole cluster, so membership fails by construction.
   - *The fix:* only pattern return on the part's own units counts; membership belongs to the parent's criterion 5 (§3a, §5).
2. **Static control at level 3 changed the parts (high).** C5's "all rates 0" (`c5_experiment.control_rows`) would erase each level-2 group's internal unit rates. It now shifts each part's isolated rate to 0 by one constant per part, which is identical to C5 at level 2.
3. **Rate spread not dimensionless (medium).** δ₂ = 0.03 was kept while C₂ is re-measured. The invariant is now δ_n × C_n = 0.096, C5's value, at every level.
4. **τ context undefined (medium).**
   - *The defect:* C5's τ₂ came from the in-world control, while the pilot measured τ₂ alone.
   - *The fix:* τ measured alone sets normalization and separation; τ in the world sets only the baselines (§3).
5. **Design gate measured formation at provisional C (medium).** A second pass at the measured C now provides the only counted formation figures.
6. **Readiness on too few groups (low).** The coarse readiness check now needs at least 10 development groups per transition, or it stops.
7. **Cross-level reads (low).** The ledger now lists the five deliberate evaluator-side cross-level quantities and forbids any cross-level read in the candidate path.
8. **Definitions made explicit (low).**
   - every assembled world uses contact placement;
   - at most one group per world;
   - the downward effect uses published ports;
   - the upward pulse unit is seeded;
   - the mechanism by which contact placement raises formation is stated.
9. **Stale text (low).** The "spacing" choice in §13, the self-audit pointer, and the pilot formation sentence are fixed.

## Fourth self-audit: alignment with the RRG theory (2026-10-02, owner-requested)

The drafter read the RRG v0.2 package (`RPG_theory/research/RRG_CURRENT/`, documents 00–08), which earlier drafts had only known through the R4 standard's summary. Each change below follows a locked-core clause.
1. **Timescale separation was a requirement for H-C (high).** It narrowed the locked definition of scale (§7; doc 02 §5 calls it a hypothesis to measure). It is now `timescale_hypothesis`, with its own verdict (renamed `scale_separation` and promoted to a registered prediction in the fifth revision).
2. **The same-law coarse model was the core prediction test (high).** Locked §7 lets effective dynamics differ by scale; same-law closure is an optional extension (doc 03 §13; proof matrix).
   - *The fix:* H-C uses one registered recipe (E1 same-law or E2 linear response, the theory's own normal-mode reduction), and `same_law_closure` has its own verdict.
3. **Prediction was called "C8 usefulness" in conversation (high).** That was wrong. Doc 03 §37 defines a new scale operationally by bounded prediction from reduced variables. It is central to H-C.
4. **The "is the middle level real" test assumed faster relocking inside parts (high).** It is replaced by `unit_specificity`: the real groups predict the full dynamics better than alternative groupings of the same material, which is the locked §7 meaning of a unit, with no timescale assumption.
5. **Staged assembly against doc 02 Phase D (medium; disclosed).** Named as the main gap in §13.
6. **Variation (locked §6) was absent (low).** It is now a descriptive endpoint.
7. **Passive structures only (low; disclosed).** Doc 02 §13 and Phase E, in §13.
8. **The AI goal is stated (§0).** C6 tests the abstraction mechanism an RRG-style AI would rest on, and makes no usefulness claim.
9. **The R4 standard's invariant 1 is narrower than the locked core** where it implies same-law closure. D7 proposes recording the theory-consistent reading in decision 0007.

## Fifth revision: the owner's answers and the C++ engine (2026-10-02)

1. **D3, D4 and D7 accepted** as recommended. **D6:** the owner chose a C++ engine.
   - §10 now plans it: compiler identification and flags registered and enforced (G10), the frozen NumPy model kept as the reference, and the four-check `backend_equivalence` gate.
   - Stop rules 13–14 are added.
   - Its speed is unmeasured until the design gate, because nothing runs before approval.
2. **Scale separation promoted to a registered RRG prediction** (the owner: bigger scales mostly take more time and distance).
   - *Verdict:* relaxation time.
   - *Reported:* formation time, measured over the whole horizon, with its horizon-scaling bias stated; and size, which grows by construction.
   - *Scope:* it still does not enter H-C, because the locked core does not define a scale by being slower. It is now a headline prediction with its own pass/fail result.

## Sixth self-audit (2026-10-02, owner-requested; reasoning only, nothing run)

1. **Unit specificity was not a fair comparison (high).** The text published fake parts "by the same function" but never said fake parts get the measured isolated rate. A shortcut would handicap them and bias the test toward the real grouping.
   - *The fix:* fake parts go through exactly the same publication procedure, isolated-rate runs included; the cost line is corrected; the sub-part contact graph is defined.
2. **The C++ equivalence check would fail on noise (high).**
   - *Check 4:* a purely relative 10⁻⁶ test fails for statistics near 0 (C5 recorded a shape CV of 3 × 10⁻¹³). It now has an absolute floor of 10⁻⁹.
   - *Check 2:* an absolute 10⁻¹² test on unwrapped phases, which grow large, is now relative above 1.
   - *Order:* check 4 now runs before any design-gate formation pass, so every development number comes from an engine already shown equivalent.
3. **Governance conflict (medium).** The header said the locked core "wins" over the R4 standard, which is the repository's authority (AGENTS.md). Now decision 0007 must be committed before registration (stop rule 15), so both documents agree at registration.
4. **Design independence (medium).** Claude drafted the design and Claude reviews the evidence, so the design had no cross-family check. The implementer's first task is now a required written critique (§12).
5. **Theory failure conditions not disclosed (medium).** Doc 03 §19 lists depth chosen by the experimenter (6) and robustness to noise and initial conditions (7). Both are now stated in §13.
6. **Theory metric missing (low).** The compression ratio (doc 03 §18) is now reported.
7. **Ledger gaps (low).** Added the parts per world, minimum group size, K and the contact-approach step.
8. **Numbers (low).** The level-2 harvest need is derived (about 300, plus margin), and the smoke time is corrected for the NumPy reference run.
9. **Stale text (low).** The receipt still listed R(true) from the removed timescale-based test; the header still said three self-audits; D7 used the old timescale wording; §1 now marks its stability words as operational.
10. **Checked and unchanged:**
    - every ledger row against invariant 1;
    - the truth tables against the endpoint list;
    - the rate-spread invariant and step-exactness;
    - E1 and E2 use only published fields;
    - the C5 functions named in §10 exist in the frozen code.

## Seventh self-audit: Codex's design critique (2026-10-02)

Codex's critique (`docs/reviews/c6_proposal_critique_codex.md`, commit 03a6a28, verdict CHANGES_REQUIRED) reviewed proposal commit 6660692. The drafter checked F1 and F3 against the frozen source before fixing them: `resonator_state` publishes the mean intrinsic rate, and published states carry only port offsets and sorted phase offsets. Every active finding is fixed.

| Finding | Cause in the draft | Fix |
|---|---|---|
| F14 (high): specificity probes aligned with the real partition | The probe was chosen on a real part, so the comparison favoured the real grouping even in a flat system | Grouping-independent probes on seeded sub-parts; a flat-null contract and a modular positive contract (§5) |
| F1 (high): fake level-1 parts could not get the measured rate | The rule relied on the frozen constructor, whose `rate` argument never reaches `natural_rate` | A C6 level-1 wrapper that writes the measured isolated rate into the consumed field; estimator and window specified; contract (§3) |
| F3 (high): the element lift needed unpublished offsets | The scoring was written as if published states contained every element offset | An evaluator-only decoder with identity-linked offsets fixed at t₀; paired responses; no later updates (§5) |
| F4 (high): criterion 6 could pass without observing a part | Incomplete windows were discarded, so a parent faster than its parts left zero windows | At least one complete own-level window per part, by a generic horizon rule; otherwise INSUFFICIENT_OBSERVATION fails (§4) |
| F5 (high): baseline dominance is not a bounded error | "Bounded predictive error" was defined only relative to baselines | Added an absolute ceiling on normalized error, r ≤ 0.5 (D8, owner decision) (§7, §8) |
| F7 (medium): censored ratios and C_n aggregation undefined | Censored values were called lower bounds even in the denominator, and no estimator was registered | τ horizon, estimator and median aggregation specified; scale separation decided on valid bounds only (§3, §8) |
| F8 (medium): E2 not a complete recipe | Step scale, non-diagonalizable Jacobians and the reference convention were unspecified, and it was overclaimed as the theory's Hessian reduction | Size-normalized steps, a convergence check with abstention, a general matrix exponential, the reference convention, corrected wording (§7) |
| F9 (medium): overlap calibration could be circular | The population was "accepted groups", which already pass the cut | An acceptance-independent population of input-template pairs; empty population means stop (§9, stop rule 6) |
| F10 (medium): the restart rule conflicted with fingerprints | "Rerun from that stage" ignored stage invalidation | Stop rule 9 restated; the native build and stage timeout listed as required pipeline engineering (§10, §12) |
| F15 (medium): "C5 was stricter" was false | Longer windows were assumed to be monotonically stricter | Non-nested measurements; C5 stands on its own registration (§4) |
| F11 (low): contact stepping could not hit the gap exactly | A fixed step was specified with no final solve | Bracket, then bisect to within 10⁻⁶; seeded retry on a miss (§3) |
| F12 (low): multiplicity scope unstated | The proposal had no explicit statement of scope | Individual verdicts nominal; H-C intersection-union; readiness gains labelled selection-biased (§8, §9) |

Also fixed:
- *Codex's §G notes:* the compiler check is described as local, not hermetic, and the scope of check 4 is stated (§10).
- *Wording:* the rate-spread drift is a median, not a guarantee (ledger).
- *F2 note:* published-centroid scaling is spelled out (§6).
- *Withdrawn findings:* Codex withdrew F2, F6 and F13 as defects, and F2 and F6 are used as implementation notes. The critique file is the reviewer's record and is not edited.

## Eighth self-audit: Codex's re-check (2026-10-02)

Codex's re-check (`docs/reviews/c6_proposal_recheck_codex.md`, commit 366bf1e, verdict CHANGES_REQUIRED) confirmed these as resolved: F1, F3, F4, F7, F9, F10, F11, F12, F15 and both §G notes. The remaining items are fixed as follows.

| Finding | Cause in the draft | Fix |
|---|---|---|
| F14 (high, partly resolved): flat systems still favoured the real grouping | Part responses were circular means, which are nonlinear. An incoherent fake part's phase moves more under the same poke than a coherent real part's, even with no dynamical hierarchy. | Every response is summarized linearly (the arithmetic mean of member paired responses), for the truth, the model input and the lift. In a flat linear system every grouping then scores identically at every time and for any initial phases, as checked analytically on Codex's fixture. The decoder needs only the membership map, because offsets cancel. Exact-zero null contracts (heterogeneous and homogeneous) and a modular positive contract (§5) |
| N1 (high): r undefined for a tiny response | The ratio was added without a domain | Response floor 0.01 (the registered margin); BELOW_RESPONSE_FLOOR is counted and excluded from r only; at least 10 r-eligible worlds; the same rule at readiness (§7, §8, §9) |
| N2 (medium): E2 convergence in mixed units | A raw Frobenius norm compared position and phase blocks in different units | Convergence on J̃ = C_n D J D⁻¹ (positions over each part's L, time over C_n), with the max(‖J̃‖, 1) convention; ledger row (§7) |
| N5 (medium): censored baseline calibration had no rule | The censoring rules covered scale separation only | A registered admissible τ grid plus ∞; gain_lo for PASS and gain_hi for FAIL; stop above 10% censored at readiness (§3, §9) |
| N6 (medium): a single element has no L | Moving the probes to sub-parts made level-0 pushes size 0 | L* is the median nearest-neighbour element spacing of the group at s₀, which is grouping-independent; ledger row (§5) |
| N3 (low): stale formation-time censoring | The horizon changed in the F4 fix and this text did not | Censored at the actual horizon max(100 C_n, 30 C_k) |
| N4 (low): stale stop rule 2 | The τ-median definition changed and this rule did not | Stop rule 2 covers the τ₁, τ₂ and τ₃ medians |

The response-summary change also applies to `coarse_vs_full`, so one convention holds across C6. For coherent real parts it equals the circular-mean response to first order.

