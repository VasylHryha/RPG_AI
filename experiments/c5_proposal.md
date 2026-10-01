# C5 proposal: many resonators form one new effective resonator (PROPOSED, awaiting owner approval)

Status: **PROPOSED** on 2026-10-01. Not registered: there is no `experiments/c5_manifest.json`, `milestones/c5.json` or C5 code, and nothing has been run. Authority: `GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md` (C5, the recursive unit interface, the recursive-resonator invariants, §5–7). Builds on C4 R003, which is accepted (`evidence/c4_r003/results.json`, `evidence/c4_r003_review_codex/INDEPENDENT_REVIEW.md`).

**Level names.** Level 0 is a primitive element. Level 1 is an accepted C4 resonator. Level 2 is the C5 composite. In the standard's C6 notation, level 1 is R₀ and level 2 is R₁. C5 is one transition (R₀ → R₁), not recursion.

## 1. The bounded question

> Take accepted C4 resonators (level-1 units) with distinct collective rates. Let them interact only through the unchanged C4 element law, so only their boundary members touch. Does a label-free detector that reads only the units' `ResonatorState` find a level-2 resonator? That means a persistent, recovering, frequency-locked group of units in which every unit stays a live, distinct C4 resonator. Does the level-2 mode depend causally on unit geometry, and unit geometry on the level-2 mode, with each effect vanishing under its complete matched ablation?

Hypotheses:
- **H-M at level 2** (whole ↔ parts): geometry and modes influence one another at the unit scale.
- **H-C, first transition only:** one stable composition step under the same rule, with a valid effective state and a coarse prediction that beats cheap baselines. Full H-C needs R₀ → R₁ → R₂ (C6). C5 cannot support H-C on its own.

**The cheap explanations, named up front.**
1. **Merger:** the "level-2 group" is just one bigger level-1 resonator. Touching in-phase units attract under the C4 law and may fuse into a single blob. Criterion 6 (parts alive and distinct, §3) rules this out. Merged worlds are counted and reported, not hidden.
2. **Trivial lock:** C4 identical-arm units all have collective frequency 0. Units that never interact keep constant phase differences and pass a level-2 mode-lock test without any coupling. C5 therefore gives each unit a distinct intrinsic rate (§2), which a decoupled control must expose as drift. It also keeps C4's recovery criterion, which a static decoupled control must fail.
3. **Clump of clumps:** units stay near one another with no mode relation. The level-2 criteria 3–5 reject this, as at level 1.

These dynamics are not new. Hierarchical synchrony, where communities lock first and then lock with one another, is known for Kuramoto oscillators on modular networks [S1, S2]. Treating a locked oscillator population as one effective oscillator is the content of the Ott–Antonsen reduction [S3]. Finite-range swarmalators form spatially separate groups [S4, S5]. C5 is a mechanism probe of the R4 composition rule, not a novelty claim.

## 2. Level-1 units, and how they couple through the same interface

**Harvest (label-free).** Fresh C4 identical-arm worlds (N = 24) run with the frozen C4 code and parameters. The frozen C4 detector, unchanged, selects the accepted resonators. Each accepted resonator with 6–16 members becomes a unit template: its member positions relative to the centroid, its phases, and its C4 `ActiveUnit`. Each template is used once. These harvest runs also give a descriptive replication of C4 formation.

**`ResonatorState` (upper-facing).** It extends C4's `active_unit` with the fields the standard's C5 interface requires:
- `level` = 1;
- `effective_position` X (centroid) and `characteristic_size` L (radius of gyration);
- `optional_phase` Θ (circular mean phase; meaningful here because units are in-phase synchronized);
- `collective_rate` Ω (measured mean dΘ/dt);
- `mode_signature` (Ω, coherence, the sorted phase-offset pattern);
- `boundary_ports` (convex-hull members' positions and phases, plus the number of active cross-unit links at each port);
- `stability_score` S (the C4 criterion margins and the next-window prediction errors);
- `member_digest` (a SHA-256 of the sorted member ids).

The level-1 owner keeps the member lists private. The level-2 detector never receives them; the evaluator may use them.

**Distinct rates.** Every member of unit g gets ω_g ~ U[−δ, δ]. All its members share one rate, and the C4 law depends only on phase differences, so a unit with rate ω_g is exactly the accepted ω = 0 resonator in a frame rotating at ω_g. This makes level-2 locking non-trivial without leaving the accepted C4 regime. (C4's heterogeneous arm, where ω varies within a group, formed only 5/20 and is not accepted, so it is not used.) Two rules fix δ:
- *Lower bound, fixed by this proposal:* the median |ω_g − ω_h| × window ≥ 10 × lock_std, so decoupled units visibly drift.
- *Value:* settled on development worlds, then frozen.

**Assembly.** A level-2 world holds M = 5 units (about 40–70 elements). Each unit gets a random rotation and a random global phase. Centroids are drawn uniformly in a disk of radius R₂ by rejection sampling, with no cross-unit member pair closer than one equilibrium spacing. R₂ is settled on development worlds. The proposal does not author which units group: the dynamics and the label-free detector decide that.

**Coupling = the C4 law, unchanged.** The full model is `c4_model.simulate` on the union of all members, with the C4 parameters and the k = 8 nearest within radius 3 neighbour rule. Units interact only where boundary members fall inside one another's neighbour sets. These are the boundary ports, and the coupling topology grows and breaks through the same neighbour rule. Nothing in the dynamics knows that units exist. Interventions and ablations use C4's `Params` presets unchanged.

**One normalization.** The C4 detector's spatial thresholds are already relative: the link threshold is 1.5 × the median nearest spacing, kicks are 0.1 × spacing, shape is a coefficient of variation, membership is a Jaccard score. Applied to unit centroids, they normalize by scale automatically. Phase thresholds are dimensionless. Only the time quantities scale, by one factor T = τ₂/τ₁:
- τ₁ is the measured e-folding time of a unit's internal phase pattern after a small kick (isolated units).
- τ₂ is the same for inter-unit phase differences after a small unit-phase kick (units in contact).
- T is measured as a median on development worlds and frozen. It scales the window, recovery time, frame interval, `freq_tol`, intervention windows and sample interval. The final-world ratio is reported. A value outside [T/2, 2T] is a stated limitation; it never changes a verdict.

This applies the standard's "nondimensionalize time by the collective timescale". The collective period 2π/Ω cannot be used: identical-arm units have Ω = 0 before rates are assigned, and ω_g can be near 0. That is owner decision D2.

**Design gate before registration.** On development worlds only, the implementer checks two things:
- that units in contact couple at all, i.e. τ₂ is finite;
- that a run fits the time budget (§7).

If either fails, the implementer stops and reports to the owner before registering. The model is not changed to make composition happen.

## 3. Label-free level-2 detector

The input is only the time series of the units' `ResonatorState` (X, L, Θ, Ω, ports, S). The detector is the C4 detector applied one level up, with the same thresholds and the same code where possible:

1. **Membership:** the C4 `components` rule on unit centroids. An edge joins units that are close (by the C4 relative link rule) and phase-locked over the window. The group needs at least 3 units, and Jaccard ≥ 0.95 across the window.
2. **Shape:** the coefficient of variation of the group's radius of gyration, over unit centroids, is ≤ 0.05.
3. **Mode lock:** every inter-unit wrapped phase difference has circular standard deviation ≤ 0.1 rad. Offset patterns are allowed. With distinct ω_g this requires actual locking.
4. **Reproducible signature:** the group frequency and the inter-unit phase pattern agree between window halves, using C4 tolerances with `freq_tol` scaled by 1/T.
5. **Recovery (the C4 R003 rule, kept whole):**
   - The kick: units are displaced rigidly by RMS 0.1 × the median unit spacing, and each unit's phases are rotated rigidly by a zero-mean kick of RMS 0.3 rad. Internal patterns are untouched.
   - The run: the full model runs for the scaled recovery time.
   - Membership: the **original unit set** must be matched with Jaccard ≥ 0.9 in the control future and in the kicked future, and the two matched groups must agree with Jaccard ≥ 0.9.
   - Pattern: the inter-unit pattern returns to within 0.1 rad.
   - All three scores are stored.
6. **Parts alive and distinct (new, stated for every level).** Each member unit's **original member set**, tracked by the owner and not re-matched to whatever component exists later, must stay a valid unit of its own level over the window:
   - C4 criteria 2–4 hold, computed on that member set;
   - at least a fraction q of its members' C4 neighbours belong to the same unit, which rules out interpenetration and merger. q is settled on development worlds; the proposed value is 0.75.

   For primitives (level 0) the criterion is vacuous, so the rule is the same at every level. A candidate that fails it is recorded as MERGED.

**Level-2 `ResonatorState`.** The same fields at `level` = 2:
- X is the centroid of the unit centroids;
- L is their radius of gyration;
- Θ and Ω come from the unit phases;
- ports are the boundary units' ports;
- S holds the margins of criteria 1–6 and the next-window prediction errors.

That is the same object shape, so C6 can reuse it unchanged.

**Per-world formation outcome (descriptive).** Each world gets the first outcome that applies, in this order:
1. FORMED: at least one accepted level-2 resonator;
2. MERGED: a candidate failed criterion 6;
3. DRIFTING: units are in contact but fail criterion 3;
4. APART: no unit pair is within the link rule at the end of the window;
5. OTHER.

## 4. Interventions, predictions and ablations (registered before final seeds)

Each intervention is applied to each accepted level-2 resonator. The treated run is paired with an unperturbed control from the same formed state, and every ablation is matched on that state. The unit of analysis is the world. Effects are paired differences with bootstrap 95% CIs (10,000 resamples).

| Test | Intervention (internal unit states held bit-identical) | Registered prediction | Complete matched ablation |
|---|---|---|---|
| **G→M (level 2)** | Move units rigidly so each centroid's offset from the group centroid is scaled by s. Both runs get the same zero-mean unit-phase probe (RMS 0.3), the C4 lesson: a locked pattern at its fixed point does not move otherwise. | The time-mean inter-unit phase-pattern deviation **increases**: separated ports lose w(r) and cross-unit neighbours. | `no_geometry_to_mode`: w = 1, and phase coupling uses the neighbour topology frozen at the formed state. This removes both geometric channels. |
| **M→G (level 2)** | Rotate each unit's phases rigidly by an independent unit-level offset. Positions and internal patterns are held. | The peak radius of gyration of the unit centroids **increases**: the cross-unit attraction A(1 + J cos Δ) weakens. | `no_mode_to_geometry`: J = 0. |
| **Dose-response** | G→M at s = 1.1 / 1.25 / 1.5; M→G at RMS 0.5 / 1.0 / uniform. | Mean effects are non-decreasing with dose, and the highest-minus-lowest per-world difference has CI > 0. | (intact dynamics) |
| **G→M channels** | As G→M, with only w = 1, or only the frozen topology. | Descriptive decomposition. | — |
| **Decoupled, spread** | Each unit is simulated alone (one world per unit, so no cross links at all). The candidate groups are the matched intact world's groups, or its proximity-only components if it has none, so the control is never empty. | The detector rejects every candidate, through drift (criterion 3). | (this is the ablation of all inter-unit coupling) |
| **Decoupled, static** | δ = 0 and units are simulated alone: the level-2 clump control. | The detector rejects every candidate through criterion 5: no restoring force on unit phases. | — |
| **Downward effect** | Compare each unit in the group with the same unit alone. | (a) Ω_unit is pulled from ω_g to the group rate; reported, and partly implied by acceptance. (b) The phase offsets of the unit's port members shift relative to its isolated self: the whole changes the parts' boundary, a lawful downward constraint. | Decoupled runs, where both are 0. |
| **Coarse vs full** | Held-out boundary excitations on one unit of a group: a phase pulse of 0.5 rad, and a radial push of 0.2 × L. | The coarse law predicts the other units' responses better than two cheap baselines. | — |

**Coarse model (zero fitted parameters).**
- *Law:* the C4 law applied to `ResonatorState`s. Distances are divided by ℓ_IJ = L_I + L_J and time by T.
- *Coupling:* the coupling between units I and J is K × (the active cross-unit links at their ports ÷ the unit size). This is read from the ports when the excitation is applied and then held fixed.
- *What the standard allows:* ports carry coupling quantities derived from active lower boundary interactions, and nothing is fitted.
- *Baselines:* (i) **no transfer**: the other units do not respond; (ii) **rigid transfer**: the whole group shifts with the kicked unit immediately.
- *Metric:* the RMS error, over the non-excited units and the response window, between predicted and full-model responses (excited minus unexcited control). It is computed separately for Θ and for X/L.
- *Work:* element-steps and unit-steps are recorded as descriptive only; there is no efficiency claim.
- *Held out:* nothing about the excitations is used to settle any setting.

**Dose values.** These are registered by this proposal. Development worlds are used only to check that they are in range: no non-finite state, and contact still exists at s = 1.1.

## 5. Endpoints and verdict rules (every endpoint evaluated by the panel or listed in `not_run` with a reason)

| Endpoint | Rule (rows in order) |
|---|---|
| `level1_pool` (gate + descriptive) | Harvest counts and sizes; every used unit passes the C4 detector alone with its ω_g. Gate: all pass. |
| `formation_l2` | Fraction of the final level-2 worlds that are FORMED, with a Wilson 95% CI. **PASS** if ≥ 0.5 **and** ≥ 10 worlds are formed; **FAIL** otherwise. The 0.5 is fixed by this proposal, not tuned. |
| `formation_outcomes` | Descriptive: counts of FORMED / MERGED / DRIFTING / APART / OTHER, plus per-candidate criterion failures. |
| `formation_vs_spread` | Descriptive: formation at 0.5δ, δ and 2δ, with the expectation that it does not increase as δ grows [S1, S2]. |
| `not_independent` (gate) | **FAIL** if the decoupled-spread control accepts any candidate; **PASS** if at least one candidate was tested and none was accepted; **NOT_TESTED** if there were none. The gate requires PASS. |
| `not_a_clump_l2` (gate) | The same rule for the decoupled-static control; it must be rejected by criterion 5. The gate requires a non-vacuous PASS. |
| `g_to_m_l2`, `m_to_g_l2` | (1) **INCONCLUSIVE** if fewer than 10 worlds are FORMED. (2) **FAIL** if the intact CI includes 0 or lies below it. (3) **PASS** if the intact CI lies above 0 and the complete ablation's CI includes 0 or its \|mean\| ≤ 0.2 × the intact mean. (4) **INCONCLUSIVE** otherwise. |
| `dose_response_l2` | Per direction: (1) **INCONCLUSIVE** if fewer than 10 worlds; (2) **FAIL** if the highest-minus-lowest CI lies below 0; (3) **PASS** if the means are non-decreasing and that CI lies above 0; (4) **INCONCLUSIVE** otherwise. The endpoint fails if either direction fails, and passes only if both pass. |
| `g_to_m_channels_l2` | Descriptive: each single-channel effect as a fraction of the intact effect. |
| `parts_alive` | Descriptive: criterion 6 values for **every unit in every candidate**, accepted or not. |
| `downward_effect` | Statistic (b), intact minus decoupled, paired: (1) **INCONCLUSIVE** if fewer than 10 worlds; (2) **FAIL** if the CI includes 0 or lies below it; (3) **PASS** if the CI lies above 0. (a) is reported alongside. |
| `effective_state_l2` | The C4 rule with bounds scaled by the same normalization (position by the unit spacing, frequency by 1/T): **PASS** if ≥ 90% of accepted level-2 units meet every bound; **FAIL** if fewer do; **INCONCLUSIVE** if there are no units. |
| `coarse_vs_full` | Paired per world, (baseline error − coarse error) for each baseline: (1) **INCONCLUSIVE** if fewer than 10 worlds; (2) **FAIL** if either CI lies below 0, meaning the coarse law is worse than a cheap baseline; (3) **PASS** if both CIs lie above 0; (4) **INCONCLUSIVE** otherwise. |
| `same_rule_audit` (gate) | The level-2 detector's thresholds equal C4's after the single declared factor T; T, τ₁ and τ₂ are recorded. |
| `numerical_checks` (gate) | C4's checks on assembled worlds: RK4 order with held neighbour sets, switching-limited dt error, equivariance under permutation, translation, rotation and global phase, **plus unit relabelling**. |

**Truth table** (registered in the manifest as ordered rows; the code and a test implement it row by row, and the test enumerates every input combination):

| Hypothesis | Row | Condition | Verdict |
|---|---|---|---|
| H-M (level 2) | 1 | any of `g_to_m_l2`, `m_to_g_l2`, `dose_response_l2` = FAIL | NOT_SUPPORTED |
| | 2 | `formation_l2` = PASS and all three = PASS | SUPPORTED_WITHIN_SCOPE |
| | 3 | otherwise (formation FAIL; < 10 formed worlds; any INCONCLUSIVE) | INCONCLUSIVE |
| H-C first transition | 1 | `formation_l2` Wilson 95% upper bound < 0.25: composition clearly fails under this rule | NOT_SUPPORTED |
| | 2 | any of `downward_effect`, `effective_state_l2`, `coarse_vs_full` = FAIL | NOT_SUPPORTED |
| | 3 | H-M (level 2) = SUPPORTED_WITHIN_SCOPE and those three = PASS | SUPPORTED_WITHIN_SCOPE |
| | 4 | otherwise | INCONCLUSIVE |

Formation failure alone never makes H-M NOT_SUPPORTED: too few groups is no evidence about their coupling (the C4 R003 principle). For H-C it is different. If composition clearly does not happen, that *is* evidence against "the same rule composes" in this model, hence H-C row 1 (owner decision D3). Gate failure (the controls, `level1_pool`, `same_rule_audit`, numerical checks) means the run is not REVIEW_READY, whatever the verdicts.

## 6. Seeds, sample sizes and the receipt

- **Development:** fixed entropy, 10 level-2 worlds and their harvest worlds. They are used only to settle δ, R₂, T and q, to check the dose range, and for smoke and tests.
- **Final:** fresh entropy drawn with `secrets.randbits(63)` when the manifest is registered. The final worlds are 30 level-2 worlds and their own harvest worlds (about 110 C4 worlds for 150 single-use units). They are never simulated before the recorded panel.
- **Why 30:**
  - Verdicts need ≥ 10 formed worlds (the C4 rule), which is reachable if formation is ≥ 1/3.
  - Formation PASS needs ≥ 15/30.
  - At n = 30, the Wilson half-width is about 0.17.
- **One arm.** The alternatives give no usable units: the C4 heterogeneous arm is not accepted, and δ = 0 is the vacuous case, used only as the static control.
- **Receipt detail** (C4 lessons):
  - per unit: size, ω_g, Ω, criterion-6 values, port links and the downward-effect statistics;
  - per candidate: all six criteria and the three recovery scores;
  - per world, dose and condition: the effects;
  - per excitation: full, coarse and baseline errors;
  - T, τ₁ and τ₂;
  - the formation outcome of every world.

## 7. Engineering, reuse and runtime

**C4 code reused read-only (frozen; imported, never edited):**
- `geomind/c4_model.py`: `Params`, `ABLATIONS`, `simulate`, `neighbors`, `wrap`; the full model is exactly this.
- `geomind/c4_detect.py`: `detect` (harvest), `components`, `locked_pairs`, `window_statistics`, `jaccard`, `best_match`, `radius_of_gyration`, `pair_differences`, `circular_mean`, `active_unit`.
- `geomind/c4_experiment.py`: `initial_worlds`, `form`, `world_rng`, `probe_kick`, `bootstrap_ci`, `wilson`, plus `gm_statistic` and `mg_statistic` wherever their signatures fit unit-state arrays.

`milestones/c5.json` lists these C4 files as dependencies, so the C5 fingerprint covers them.

**New files:**
- `geomind/c5_units.py`: harvest, `ResonatorState`, owner-private unit tracking.
- `geomind/c5_compose.py`: assembly, rate assignment, decoupled runs, interventions.
- `geomind/c5_detect.py`: the level-2 detector (criteria 1–6).
- `geomind/c5_coarse.py`: the coarse law and baselines.
- `geomind/c5_experiment.py`, `geomind/run_c5.py`: the runner, which calls `check("c5", "panel")` itself.
- `tests/test_c5.py`, `tools/c5_mutants.py`.
- `experiments/c5_manifest.json` and `milestones/c5.json`, registered and committed before any final-seed run.

The shared pipeline tools (`tools/milestones.py`, `verify.py`, `milestone_mutation.py`) are used as they are.

**Focused contracts** (fast, on synthetic or development fixtures):
- A unit with a shared ω_g passes C4 exactly as in the ω = 0 frame (rotating-frame symmetry).
- Rigid unit moves and unit-phase rotations leave internal relative states bit-identical.
- Decoupled runs have no cross-unit neighbour at all.
- Each ablation removes its pathway: the frozen topology really freezes cross links, and J = 0 really removes the phase-dependent cross term.
- The detector rejects:
  - a synthetic merger (criterion 6);
  - drifting units (criterion 3);
  - static units (criterion 5);
  - a group that fragments the same way in both futures (the R003 rule at level 2);
  each alongside a positive control.
- The detector never receives member lists, ω_g or fixture labels.
- Equal-size padding, if used for batching, is bit-identical to unpadded runs.
- Every truth-table row is covered by an enumeration test.
- Every manifest endpoint appears in the receipt's coverage.

**Mutants** (`tools/c5_mutants.py`):
- recovery ignoring the original unit set;
- criterion 6 dropped;
- the decoupled control leaking cross links;
- H-M ignoring formation;
- dose ignored;
- a coarse model reading member states;
- T not applied.

**Runtime estimate** (to be measured on development worlds and recorded in the manifest before registration):
- tests: under 60 s;
- smoke: about 2 min;
- mutation probe: about 3–8 min;
- recorded panel: **about 30–60 min**.

The basis is C4's measured 119 s panel for 40 worlds at N = 24, scaled by:
- (N ≈ 50 / 24)² ≈ 4× for all-pairs neighbour search;
- the time factor T, about 2–3× if T ≈ 3;
- 30 worlds;
- the extra controls and excitations.

If development measurement projects a panel above 90 minutes, the implementer brings options to the owner before registering. Options include fewer doses or a pure-NumPy cell list. A C++ backend has the unpinned-toolchain issue G10.

**Frozen environment limits.** `pyproject.toml` and `uv.lock` are frozen by the C4 acceptance and enforced by `tools/accepted_freeze.py`. C5 therefore has Python 3.9, NumPy 2.0.2 and pytest 8.4.2 only:
- no SciPy (KD-trees, curve fitting); τ fits use a log-linear least-squares in NumPy;
- no Hypothesis; property checks are hand-written randomized loops;
- no Numba.

Adding any library would change frozen files and needs an owner decision. None is proposed.

**Process.** Verify once in order: `tools/verify.py --milestone c5 --output evidence/c5_r001`. Then one independent review by the other model family, capped at about 20 minutes. A design defect found before review means withdrawal through a decision record, and the next revision runs on fresh seeds.

## 8. C4 lessons applied up front

| C4 lesson | Where C5 applies it |
|---|---|
| Ablations must remove a pathway completely (R001) | G→M uses the complete `no_geometry_to_mode`; M→G uses J = 0; "all inter-unit coupling off" is literal separate worlds. Single channels are decomposition only. |
| Recovery and membership must keep the original group (R002 → R003) | Criterion 5 matches the original **unit set** in both futures and requires the futures to agree. Criterion 6 tracks each unit's **original member set**, never a re-matched component. |
| No verdict on tiny n (R001) | Every causal, dose, downward and coarse endpoint is INCONCLUSIVE below 10 formed worlds. Formation also needs ≥ 10 worlds. |
| One written rule implemented row by row (R002) | Ordered truth tables in the manifest, mirrored by the code, with an enumeration test over all combinations. |
| Non-vacuous controls (R003) | Both decoupled controls receive imposed candidates, so they cannot pass empty. The static control is the level-2 analogue of C4's clump test. Distinct ω_g removes the trivial lock. |
| Per-unit values in the receipt (R001) | Per unit, per candidate, per world, dose and condition, and per excitation (§6). |
| Falsifiable causal test beyond the sign (R001) | Dose-response in both directions, and a coarse model that must beat two cheap baselines. |

## 9. What C5 cannot show

- **No recursion:** one transition (R₀ → R₁). Scale-recursive organization needs C6 (R₁ → R₂ with the same operator).
- **No dissolution and reform:** that is C7. No usefulness, compression or efficiency claim: that is C8. Work counts are descriptive.
- **Staged assembly:** level-1 units are formed separately and then placed together. C5 does not show units co-forming from one primitive soup. That would need either labels for the per-unit rates or identical rates, which makes level-2 locking trivial.
- **Per-unit rates are a fixture:** a property assigned to each level-1 unit, not something that emerges.
- **Narrow scope:** one model, one parameter set, one element law, M = 5 and unit sizes 6–16. There is no internally heterogeneous unit, because the C4 heterogeneous arm is not accepted.
- **The weak parts of the evidence:**
  - downward effect (a) is largely implied by acceptance; only (b) is a real test, and it tests existence, not dose;
  - complete ablations vanish by construction, so the evidence is the intact effect and its dose-response.
- **No novelty:** hierarchical synchrony and population-level reduction are known [S1–S3].

## Sources

- **[S1]** Arenas, Díaz-Guilera and Pérez-Vicente, *Synchronization reveals topological scales in complex networks*, PRL 96, 114102 (2006). [arXiv:cond-mat/0511730](https://arxiv.org/abs/cond-mat/0511730). Communities synchronize first, then the network, in hierarchical order.
- **[S2]** Skardal and Restrepo, *Hierarchical synchrony of phase oscillators in modular networks*, PRE 85, 016208 (2012). [arXiv:1111.0921](https://arxiv.org/abs/1111.0921). Local versus global synchrony, using low-dimensional community equations.
- **[S3]** Ott and Antonsen, *Low dimensional behavior of large systems of globally coupled oscillators*, Chaos 18, 037113 (2008). [arXiv:0806.0004](https://arxiv.org/abs/0806.0004). A locked population reduces to a few effective variables.
- **[S4]** Lee et al., *Collective steady-state patterns of swarmalators with finite-cutoff interaction distance* (2021). [arXiv:2103.11584](https://arxiv.org/abs/2103.11584). A finite interaction range gives spatially separate groups.
- **[S5]** Sar and Ghosh, *Dynamics of swarmalators: a pedagogical review* (2022). [arXiv:2208.14803](https://arxiv.org/abs/2208.14803).
- **[R3]** in the standard: O'Keeffe, Hong and Strogatz, *Oscillators that sync and swarm* (2017).

## Decisions for the owner

1. **D1 — Approval.** Approve the question, the staged assembly, the per-unit rates, the level-2 detector (criteria 1–6), the interventions and doses, the endpoints and the truth tables, or name changes.
2. **D2 — Time normalization.** Accept the measured relaxation-time ratio T = τ₂/τ₁ in place of the standard's "collective period", which is undefined at Ω = 0.
3. **D3 — Formation as evidence for H-C.** Accept H-C row 1, under which a Wilson upper bound below 0.25 makes the first transition NOT_SUPPORTED. The alternative keeps it INCONCLUSIVE, as for H-M.
4. **D4 — Fixed numbers.** Formation PASS at ≥ 0.5 with 30 final worlds, q proposed at 0.75, M = 5, unit sizes 6–16.
5. **D5 — Who implements and who reviews.** Recommended: Claude implements, for continuity with the C4 code it reuses, and Codex reviews. The reverse is also valid. The reviewer must be the other model family.
