# Design 0g, revision 3: four controllers on the S2 plug, judged against Astelia's scripted AI (S3 engineering contract; owner-authorized correction)

Revision 2 answered the Codex design review `docs/reviews/tactical_0g_design_review_codex.md` (CHANGES_REQUIRED, 13 findings). The self-audit (section 9)
lists each finding, its fix and its cause. Revision 1 is in git history (`85cf576`). This document replaces `PLAN_RESONATOR_AI.md` sections 2, 4 and 5b where they
differ, and it is the single executable contract for S3-S5. Revision 3 resolves the S3 report after the owner explicitly asked Codex to handle/fix the blockers (2026-10-05). Codex owns these corrections. S3 build/checks are authorized; tuning and recorded experiments remain outside this session. The owner's decisions are kept:
- four arms;
- damage dealt and taken as the input;
- full sight;
- abilities left to the game's automatic reflex;
- the survivor-first score;
- development starting small;
- watching fights.

**Claim boundary (v0):** one-level position/phase control of game units by the C4 element law driven by damage, compared with three specified controllers. Not claimed:
- a C5 hierarchy (groups acting as higher-level units);
- causal group necessity;
- novelty over swarmalators or physicomimetics in general;
- that a sustained oscillation, as opposed to a circular state, is necessary.

Groups are diagnostics only (section 7).

## 1. The plug as built (S2, reviewed) and the fixed world for every outside arm

**Observation** (`astelia_cpp/src/native/controller.h`), one copy per tick per controlled side, read-only:
- the world: t, dt, width, height;
- **every living unit of both sides:** id, team, role, x, y, vx, vy, hp, maxhp, radius, speed, range, dmg, cd, cdMax, current target id, cumulative damage dealt and taken.

S3 adds three behaviour-neutral fields (section 8): cross-team damage counters, artillery minimum range, and a failure report.

**The fixed world for every outside arm** (frozen in the runner; each fight request is checked against it):
- rules `game`, `sandboxAbilities` at the game default (off), `perception=false`;
- scenario `mirror`, duration 150 s, the default army (10 melee, 30 ranged, 10 artillery);
- abilities `Auto` (owner decision 1);
- **our side's skills fixed to the game's defaults under game rules**, identical for every outside arm, so projectile leading and similar body skills do not differ between arms;
- decisions every tick (dt = 1/30 s).

The runner refuses `passthrough`, which is test-only.

**Declared asymmetries** (a system comparison, not identical information):
1. A controlled side sees one snapshot at the start of a tick, while built-in units decide one after another within the tick.
2. Built-in brains can read shots, shells and same-tick assignments.
3. **Elite and elite-fast planners simulate a cloned copy of our controller** (`world.cpp:272-276`, `search.cpp:9-18`, `artillery.cpp:45-48`), so they effectively use its private state. Novice and
   regular do not plan this way. P1 uses novice and regular only. The P2 and P3 panels use opponents whose skills include no lookahead or rollout. Elite results are a declared stretch
   comparison against a stronger, state-reading opponent.
4. Every unit's current target is visible, the enemy's included. Who attacks whom is visible on screen.

## 2. Units of measure (the normalization ledger)

| Quantity | Symbol | Unit | Value |
|---|---|---|---|
| Model length | L | px per model unit | 100 (fixed) |
| Model distance | r | model units | distance_px / L |
| Time | Δ | s | each tick integrates the controller's state over Δ = dt = 1/30 s (no separate time scale) |
| Damage rate | z | 1/s | exponential average of cross-team HP per second, divided by own max HP |
| Rates | ω, K, K_t, λ | 1/s | per second of game time |
| Damage gain | κ | dimensionless | multiplies normalized damage rate |
| Reach distance to an enemy | ρ | model units | melee and direct: surface gap = (centre distance − both radii)/L; artillery: centre distance/L (the bridge's own legality, `controller_bridge.cpp:51-53`) |

**Damage rates** (one recurrence for every arm). For each unit u (ours and enemies'), from the cross-team counters C_out (HP dealt to the other team) and C_in (HP taken from the other team):

    q = exp(−dt / T_d),  T_d = 2 s (fixed)
    z_out(u) ← q · z_out(u) + (1 − q) · (ΔC_out / dt) / maxhp(u)          initial 0; same for z_in
    pressure  P(u) = κ · (z_in(u) − β · z_out(u))                          1/s

- **P > 0:** the unit is being beaten; **P < 0:** it is winning.
- κ ≥ 0 and β ≥ 0 are knobs. The owner's two inputs enter as a weighted difference (the review's note: equal weighted inputs cancel by design).
- Friendly fire is excluded from P and reported separately.
- A unit's z is dropped when it dies or leaves the observation.
- An enemy's P is the controller's **inferred damage state**, its own memory. It is not a measured oscillator inside the scripted opponent.

## 3. The shared skeleton (every substantive arm; only the internal state differs, section 4)

Each arm has a **commitment** c_i ∈ [−1, 1] per own unit: resonator cos θ_i, morale m_i, push-pull 1.

**Movement.** A desired velocity v_i, in model units per second, is computed once per tick in `prepare` from the frozen snapshot:

    v_i = mean_{j ∈ N_i} û_ij [A (1 + J s_ij) − B / max(r_ij, ε)]               (allies: the C4 law; A = 1, B = 1, J = 0.8 fixed, C4 values)
        + G · mean_{e ∈ E_i} û_ie (1 − d_i / max(ρ_ie, ε))                      (enemies: restoring toward a preferred reach distance)
    d_i = f · range_i/L · (1 + w (1 − c_i)/2)                                      (commitment 1: d = f·range; commitment −1: d = f·range·(1 + w))

- N_i: up to 8 nearest living allies with r < 3 (the C4 rule: stable by id on ties, empty mean = 0).
- E_i: up to 8 nearest living enemies (empty mean = 0).
- ε = 0.01; û is the unit vector (zero vector when r = 0).
- s_ij is the arm's similarity: resonator cos(θ_j − θ_i), morale 1 − |m_j − m_i|, push-pull 1.

**Sign check (the review's finding 1).** For one enemy at fixed commitment, the radial term is G(1 − d/ρ) with G ≥ 0 and d > 0:
- ρ > d: it pulls toward the enemy;
- ρ < d: it pushes away;
- ρ = d: a stable rest point.

Lower commitment **raises d**, so a unit that is being beaten backs off to a longer distance by a force that still restores toward its new d. The short-range repulsion −B/r from allies does
not depend on commitment. S3 tests the sign of the enemy term inside, at and outside d for c = −1, 0, 1.

**Action.**
- If |v_i| < 1e-9, hold: goal = own position, multiplier 0.
- Otherwise: goal = x_i + L · 2 · v_i/|v_i| (a direction two model units ahead, clipped by the bridge), multiplier min(1, |v_i|), stop 0.

**Target** (computed for all own units in `prepare` from the frozen snapshot and the **previous tick's** assignments; never updated during the shuffled `decide` calls):
- **Legal set:** living enemies within the bridge's reach for the unit's role. Melee and direct: gap ≤ range. Artillery: minRange ≤ centre distance ≤ range.
- An empty legal set gives target none.
- **Score:** S_ij = a_ij + γ · tanh(P(j) · 1 s). The arm's alignment a_ij is defined in section 4. Push-pull instead uses only negative centre distance, with no pressure preference. The second term prefers enemies that are being beaten (γ ≥ 0).
- **Hysteresis:** keep the previous target if it is still legal and the best score exceeds its score by less than η = 0.2 (fixed). Ties in selecting the best candidate go to the lowest id; a still-legal previous target then takes precedence if the improvement is strictly less than η.

**Terminal and degenerate states:**
- With no living enemy, every unit holds with target none.
- A dead or departed id is removed from all memories.
- The empty sums and means above are 0.
- **Any non-finite internal state or raw action is a controller failure:** the unit holds for that tick, and the failure is counted and reported (section 8). The fight is then recorded as a controller
  failure, never as an ordinary win or loss, and never dropped.

## 4. The four arms

| Arm | Internal state per own unit | State update per tick (game time, Δ = dt) | Commitment c | Alignment a_ij (target score) |
|---|---|---|---|---|
| **resonator** | phase θ_i (initial: uniform from the controller's RNG) | one RK4 step of dθ_i/dt = ω_role + K · mean_{N_i} e^{−r²} sin(θ_j − θ_i) + K_t · sin(ψ_i − θ_i) + P(i) · sin θ_i, positions frozen at the snapshot | cos θ_i | cos(θ_i − ψ_ij), with ψ_ij = arg Σ_{k ≠ i, previous target of k = j} e^{iθ_k}; **alignment a_ij = 0** when there are no such k or the resultant is < 0.1 per attacker (ψ is then undefined) |
| **plain morale** | m_i ∈ [−1, 1] (initial 0) | one RK4 step of dm_i/dt = −λ_role m_i + K · mean_{N_i} e^{−r²}(m_j − m_i) + K_t (μ_i − m_i) − P(i), then clipped to [−1, 1] | m_i | 1 − abs(m_i − μ_ij), with μ_ij = the mean m of j's other previous attackers; **alignment a_ij = 0** when there are none (μ is then undefined) |
| **push-pull** | none | none | 1 | target = nearest legal enemy (the review's option: a whole-controller baseline). centre-distance score a_ij = −distance_px/L; hysteresis η = 0.2 in model-distance score units, as above; no damage score |
| **nearest** | none | as built in S2 (untuned floor) | | |

In the resonator, ψ_i in the K_t term is ψ of the unit's own current target, excluding itself, and the term is 0 when that is undefined. In morale, μ_i is defined the same way, and its entire K_t term is zero for an undefined group. Assignments/topology and pressure are held through RK4; ψ/μ and neighbour states are recomputed from the joint trial state at each stage. Integrate all own states together, then compute movement and target scores from the updated state. Artillery uses the ranged rate in both arms. New ids start with damage averages zero and current counters as their baseline; future counter differences are consumed once per prepare. Previous assignments start empty. A failed own unit retains its last finite state but publishes hold/no target for the tick; a non-finite retained state remains failed until removed. All ids are initialized/processed in increasing id order.

- **The resonator's drive P sin θ:** P > 0 pushes θ toward π (pull back), P < 0 toward 0 (attack).
- **Locking** (the review's finding 2): with constant P and no coupling, θ locks only when |P| ≥ |ω|, at an offset from 0 or π. Otherwise it keeps rotating. Both are allowed outcomes, and the logs record which occurs.
- **What the morale contrast isolates:** a linear, bounded state with relaxation λ, against a circular state with rotation ω and sine coupling, everything else equal. It does not isolate "oscillation is necessary" (claim boundary).
- **Push-pull** has no internal state and nearest targeting. **P3 is narrowed** to "beats this specified push-pull baseline".

## 5. Knobs (at most 10 per arm), bounds and tuning protocol

| Knob | Meaning | Bounds | Resonator | Morale | Push-pull |
|---|---|---|---|---|---|
| K | neighbour coupling (1/s) | [0, 5] | ✓ | ✓ | |
| K_t | coupling to the target group (1/s) | [0, 5] | ✓ | ✓ | |
| κ | damage gain | [0, 50] | ✓ | ✓ | |
| β | weight of damage dealt | [0, 3] | ✓ | ✓ | |
| ω_melee, ω_ranged (artillery uses ω_ranged) | rate (1/s) | [−2, 2] | ✓ ✓ | | |
| λ_melee, λ_ranged | relaxation (1/s) | [0, 2] | | ✓ ✓ | |
| G | enemy restoring gain | [0, 5] | ✓ | ✓ | ✓ |
| w | distance increase at full pull-back | [0, 3] | ✓ | ✓ | |
| f | preferred distance as a fraction of range | [0.3, 1.2] | ✓ | ✓ | ✓ |
| γ | preference for beaten enemies | [0, 2] | ✓ | ✓ | |
| **count** | | | **10** | **10** | **2** |

Fixed: A = 1, B = 1, J = 0.8 (C4), L = 100 px, T_d = 2 s, k = 8, ally radius 3, η = 0.2, ε = 0.01, the goal distance 2 model units. Nearest has no knobs.

**Protocol:**
- One optimizer for every arm: the racing bench with the same stages and acceptance rule.
- The same development seeds and the same fight budget for each tuned arm (push-pull spends it on 2 knobs).
- Every evaluated candidate is logged, failures included. Cache hits count as fights for the budget.
- Outcome-informed manual revisions to an arm's equations after S4 starts are logged, and they restart that arm's budget.

## 6. Score, panels and inference (frozen at S5 from S4 measurements)

**Per fight:**
- **S** = survivors − enemySurvivors (the main score).
- **D** = cross-team HP dealt − cross-team HP taken (from the new counters; friendly fire reported separately). D is descriptive only: registered endpoints use S, and a statistical tie on S is never
  resolved by D.
- A timeout is an ordinary fight with its S. A controller failure is a failure record (section 3).

**The sampling unit is a cluster:** one world seed played in both orientations (swapSides false and true), averaged. Pairs of arms are joined by (opponent configuration, seed,
orientation), never by array position.

| Endpoint | Panel | Statistic |
|---|---|---|
| **P1 beat the code** (head-to-head) | our resonator on side 0 against the scripted level on side 1: novice, and separately regular. n_P1 seeds, chosen in S4 by a power rule | mean cluster S > 0, one-sided lower bound. P1 is supported only if **both** the novice and regular subtests pass (intersection-union, one allocation) |
| **P2 beats morale** | the 19-doctrine pool, opponent skills = elite skills without `artyRollout` (no lookahead; the bench setting), n_P2 seeds per doctrine | paired cluster difference S_res − S_morale > δ, one-sided lower bound |
| **P3 beats push-pull** | the same panel | S_res − S_push > δ |

- **Alpha:** familywise 0.01, split equally over P1, P2 and P3 (0.01/3 each). Directional REFUTED claims get their own budget: each endpoint's 0.01/3 is split into 0.0025 for support and 0.00083 for
  the opposite direction.
- **The verdicts:**
  - SUPPORTED: the lower bound exceeds the margin.
  - REFUTED: the upper bound is below 0 (a significant opposite effect).
  - INDETERMINATE: otherwise.
- **Failing to show superiority** establishes neither equivalence nor "phases add nothing".
- **δ** (in survivors) is proposed by the drafter from S4's measured paired spread and approved by the owner. It is never shrunk to obtain a pass.
- **n** is chosen before S5 by a bounded power rule on S4 development **and** a separate development validation split. C++ fights are cheap (about 0.05 s), so large n is affordable.
- **Seeds:** the S1 ladder freeze and all of S4 use development seeds from the ledger. Judging seeds are drawn fresh at S5 and never inspected before the recorded run.

## 7. Groups: diagnostics only

Diagnostics are output-only, sampled from the prepared observation and newly prepared assignments/state, once per integer second (first tick reaching that second, no t=0 row). Keep every prepared frame over the preceding 3 s, including the boundary. Member ids are the stable unit ids; no persistent cluster id is claimed. Output for each controlled side:
- `phaseCoherence`: instantaneous |mean exp(iθ)| for resonator; null for no own units or arms without phases.
- `distinctTargetPhases`: group own units by their newly assigned living enemy target; compute each group's circular mean, discard mean resultants < 0.1, connect means with circular separation ≤ 0.3 rad, and count connected components. Null for arms without phases; zero for no valid occupied groups.
- `targetConcentration`: largest target-group count / number of living own units (untargeted units remain in denominator); zero with no units/targets.
- `candidates`: resonator-only connected components, size ≥ 2. For pairs present in every history frame, connect if current centre distance ≤ 1.5 model units and circular std of their unwrapped phase difference over the window ≤ 0.2 rad. Circular std = sqrt(max(0, −2 log(max(|mean exp(iΔθ)|, 1e−300)))). Wait for a full 3-second window before candidates; `windowReady` reports warmup. Other arms return empty candidates and null phase quantities. Candidate identity is its sorted member-id list; sort candidate lists lexicographically. These thresholds are fixed diagnostics, not tuning knobs.
- Per-unit resonator phases (unwrapped), commitments, normalized damage averages and prepared target ids; morale state/commitment for morale. These support independent trajectory/refinement checks. Locking versus rotation is represented by the unwrapped phase history; no equilibrium classification is inferred under changing drive.

They are labelled candidates: the C4 criteria 1-4 need time windows, and criterion 5 (recovery under kicks) is not tested in combat. There is no detector feedback into the controller, and no
C5 claim. Global synchrony is an allowed outcome, not evidence of several groups.

## 8. S3 work: the plug extensions and checks

**Plug extensions** (behaviour-neutral):
- per-unit cross-team counters (dealtToEnemy, takenFromEnemy) and friendly-fire counters, computed in `World::damage` by team test;
- `minRange` in `ObservedUnit`;
- a per-side `controllerFailures` count in the summary;
- the runner refuses `passthrough`.

**Gate:** the 80 reference requests stay byte-identical, and so do the S2 passthrough fixtures.

**Controller checks:**
1. Check the shared ally/phase RHS against every stored C4 variant using that fixture's parameters and epsilon, and a test-only full coupled RK4 adapter against its stored x/θ step, to 1e-9. Production uses frozen measured positions and epsilon 0.01; it does not claim equality to the stored coupled step or C4's near-contact regularization. Check production frozen-position RK4 against an independent implementation of the section-4 ODE, including K_t and pressure. No accepted/reference file is modified.
2. The sign of the enemy term inside, at and outside d, for c ∈ {−1, 0, 1}.
3. The damage-rate recurrence on a scripted counter sequence (step, constant, decay).
4. Targets are computed once in `prepare` and do not change when `decide` is called in a different order.
5. The cases: an empty legal set, a dead target, coincident units, no enemies, a zero resultant.
6. A non-finite internal state is reported as a failure.
7. A clone carries all memory (phases or morale, damage averages, previous assignments, RNG), and running a branch leaves the parent's state unchanged.
8. Determinism.
9. The cost per fight against nearest, with opponent planning work recorded.
10. All arms play 38 fights with no failure.

**A step-refinement check:** compare one full phase/morale step with two half steps on the **same captured snapshots**, holding world dt, damage recurrence and previous assignments fixed; carry both state trajectories across the replay. Apply morale clipping once at the physical-tick boundary, after the whole integration interval, in both trajectories; half steps do not add an extra clipping operation. Maximum absolute commitment difference must be < 0.02 over the 38 default-knob engineering fights per stateful arm. This isolates integration refinement from divergent game worlds; no additional fight is needed. Frozen-position ODE tests also use nonzero role rates, since midpoint resonator rates are zero.

## 9. Self-audit: the review's findings, fixes and causes

| # | Finding | Fix | Cause |
|---|---|---|---|
| 1 | Two contradicting enemy laws; the retreat version reversed the restoring force | One law, section 3: a non-negative gain toward a commitment-dependent distance, with a sign check | I added the damage version as prose without deleting the first formula, and I did not check signs |
| 2 | Damage averaging undefined; plug counters cumulative and including friendly fire; locking unstated | The recurrence and units (section 2), cross-team counters (section 8), the locking condition (section 4) | I specified the signal before reading the plug's counters |
| 3 | Target group phase circular; zero resultant undefined; focus fire claimed | Previous-tick assignments, all targets in `prepare`, self excluded, a resultant threshold, ties; the focus claim removed | Design by narrative, not by update order |
| 4 | Morale and push-pull undefined | Equations in section 4; P3 narrowed | I named the arms without specifying them |
| 5 | P1 panel undefined; 114 is not independent | Head-to-head P1, clustered seeds, power-chosen n (section 6) | "114" was carried over from the bench without a sampling model |
| 6 | Elite planners simulate our controller's state | Declared (section 1); P1 and the P2/P3 panels avoid planners | Not known when I wrote the design; found in the plug code |
| 7 | Power near 60% is low | n chosen by a power rule in S4; cheap C++ fights | I fixed n before measuring noise |
| 8 | 24 knobs, not 10; unequal tuning | A table of 10 / 10 / 2 / 0 with bounds; one protocol | I added knobs with each revision and never recounted them |
| 9 | Scaling and RK4 unspecified | The ledger in section 2, phases integrated with frozen positions, the action rule, step refinement | Left implicit |
| 10 | Fairness broader than "same for every arm" | The fixed world and declared asymmetries (section 1) | I assumed the arms differed only in the controller |
| 11 | Degenerate cases, silent failures, a friendly-fire score | Section 3; failure records; D from cross-team counters, descriptive only | Not specified |
| 12 | Groups do not implement C5 | Diagnostics only; the claim boundary | I overstated the C4/C5 transfer |
| 13 | Plan rows stale | `PLAN_RESONATOR_AI.md` S3-S6 rows and acceptance now point here; stop rows added | Revisions were patched piecemeal |

## 10. Stop rows (yes/no; one action; one role)

| Question | Yes → action | Role |
|---|---|---|
| Does an S3 check in section 8 fail? | Fix it before any fight development | implementer |
| Does a controller produce failures in development fights? | Fix it; the arm cannot be tuned until it has zero failures on 38 fights | implementer |
| After its full S4 budget, does the tuned resonator fail to beat novice head-to-head on development seeds? | Stop and report to the owner; no registration | drafter |
| Is the S4-measured spread such that the owner-approved δ needs n above 2,000 clusters per endpoint? | Report the trade-off and let the owner choose n or δ | drafter |
| Does any judging seed appear in development logs? | Draw new judging seeds and record it | implementer |
| Is there an outcome-informed equation change after S4 starts? | Log it and restart that arm's budget | implementer |

## 11. Revision-3 S3 correction self-audit and execution boundary

| S3 question | Correction | Cause |
|---|---|---|
| C4 oracle versus frozen-position phase step | Separate shared RHS/full coupled algebra checks from independent production ODE/refinement checks; retain epsilon 0.01 | The old acceptance row confused frozen neighbour indices with frozen geometry |
| Push-pull hysteresis score | Negative centre distance in model units; eta 0.2; no damage score | Nearest targeting was named without its hysteresis scale |
| Group diagnostics | Fixed formulas/window/thresholds, stable member ids and non-phase-arm null semantics in section 7 | Diagnostic names were mistaken for an executable algorithm |
| Pressure units | Dimensionless kappa and a fixed 1-second tanh normalization | The rates row incorrectly included a gain multiplying a rate |
| Empty group scores | Alignment zero, invalid aggregate, entire target-coupling term zero | “0 when empty” failed to name which quantity becomes zero |

Owner steering: “so can oyu ahndel /fix blcokers or what ? we a rewitgin for what to soelve them ?” after the S3 NOT_READY report. This authorizes Codex to repair its reported blockers and continue the previously authorized S3 build/checks, not S4 tuning or S5 execution. Claude remains the independent reviewer of completed S3.

Defaults (untuned midpoints): resonator K=2.5, K_t=2.5, kappa=25, beta=1.5, omega_melee=omega_ranged=0, G=2.5, w=1.5, f=0.75, gamma=1; morale substitutes lambda_melee=lambda_ranged=1; pushpull G=2.5, f=0.75. JSON parameter names are exactly the ASCII names in this sentence. Missing params use defaults; unknown, nonnumeric, nonfinite or out-of-bounds values fail before fight creation.

The general native host retains legacy schemas for nonsubstantive legacy requests. S3 substantive arms or `s3:true` opt into the extended summary: `controllerFailures` (two counts), cross-team dealt/taken and friendly-fire dealt/taken per side, and `controllerStatus` (`completed` or `controller_failure`). Totals are fight-long Stats counters, including dead/reclaimed units; they do not sum living-only observations. Internal failure flags and raw invalid actions each count once per unit per decision tick, and fail to hold/no target. Clone memory is isolated; branch-only failure counts do not taint the parent's played fight. Planning work is separately reported by existing metrics.

The general host rejects passthrough unless started explicitly with `--test-controllers`; that flag is used solely by engineering tests/legacy fixture parity. The S3 runner accepts only fixed-world requests and never enables that flag. Its narrow input is arm, params, seed, swapSides, controlledSide, opponent, diagnostics; opponent may be a doctrine name or novice/regular/elite/elite-fast. Controlled-side skills always use game defaults plus Auto, regardless of opponent profile. The 38 checks are the 19 existing doctrine names × both orientations on fixed development seeds 2026100500+doctrine_index; one checked fight per arm/configuration, no tuning. Determinism uses fresh-process replay of one request per arm; the fresh-process determinism replays double as cost samples (one matching request per arm), with capture and diagnostics off. Report the sample size, startup-inclusive elapsed cost and actual planner counters; there is no registered speed cap. No repeated timing grid is required. Tests may use tiny synthetic worlds; no additional development fight grid.

| Stop question | Yes action | Role |
|---|---|---|
| Does a further unresolved design conflict appear? | Report it without silently changing the contract | implementer |
| Does an engineering check fail? | Complete the repair batch, then rerun only affected failed/invalidated checks | implementer |
| Is S3 engineering ready? | Hand off committed code and evidence for Claude review | implementer |

## 12. Revision 4 (v1): two changes after the development replays (2026-10-05)

**What the replays showed** (`viz_0g/`, development seeds 2026100700-2026100702, stage-B knobs):
- Against the scripted **regular** level, all ten enemy guns survive every fight.
- Our units hover 320-440 px from the nearest gun (gun range 320 px; our shooters' reach about 278 px centre to centre), with commitment between −0.8 and −0.95. No unit ever targets a gun.
- Damage from guns our units cannot reach keeps pushing them toward pull back, which never takes them out of the guns' splash. This is the **retreat trap**.
- Novice charges into us, so the same law beats it.

**Two changes, with no new knobs** (knob table section 5 unchanged; push-pull and nearest unchanged):

1. **Unanswered damage drives commitment, not retreat.**
   - The damage taken by an own unit is split by whether it had a legal target at that tick:
     - z_in,ans: damage taken while it had something in reach;
     - z_in,unans: damage taken while it had nothing in reach.
   - Both use the section 2 recurrence.
   - **Attribution timing** (answering the implementer's stop, `astelia_cpp/S4_V1_DEVELOPMENT_REPORT.md` at `efc3f3a`): at each `prepare` of tick k, the controller records for every own
     unit whether its legal set (section 3) at that frozen snapshot is non-empty. The damage increment ΔC_in consumed at the next `prepare` (tick k+1, from the counters' difference) is the
     damage taken during tick k. It is labelled with the status recorded at tick k: **answered** if the set was non-empty, **unanswered** if it was empty.
   - This is what the unit knew when it chose that tick's action. It uses only the controller's own memory and needs no engine change.
   - On a unit's first `prepare` there is no previous status, so its first increment is answered by convention; the counter baseline is set at that `prepare`, so the increment is 0 anyway.
   - Clones copy the recorded status with the rest of the memory.
   - Own pressure: **P(i) = κ · (z_in,ans(i) − β · z_out(i) − z_in,unans(i))**.
   - Damage the unit can answer still pulls it back when it is losing the exchange. Damage it cannot answer pushes it to close in. Through the K coupling, a group commits together.
   - Enemy pressure P(j) is unchanged.
2. **Target preference toward the most engaged enemies.**
   - The score term γ · tanh(P(j)) preferred enemies being beaten **and not hurting us** (P(j) falls with the damage j deals).
   - It becomes **γ · tanh(κ · (z_in(j) + z_out(j)) · 1 s)**: prefer the enemies most involved in the exchange, being hit by us or hitting us. It keeps the revision-3 normalization: κ is dimensionless and the rates are multiplied by a fixed 1 s inside tanh, exactly as for the term it replaces.

**What stays:**
- the equations of sections 2-4 otherwise;
- the bounds;
- the protocol (the amended S4 CMA-ES protocol, rerun on **fresh** development seeds for all three tuned arms, since the shared skeleton changed);
- the claim boundary;
- P1-P3 as designed.

**Checks to add in S3 terms:**
- the split of damage by legal-target status on a scripted sequence;
- an outranged unit under fire raises its commitment;
- the target term increases with the enemy's damage dealt to us.

The previous checks still pass with these terms switched off.

## 13. Revision 5 (v2): range-aware distance and threats (2026-10-05, after the v1 STOP)

**Logged as an outcome-informed change** (section 10): the v1 review (`astelia_cpp_review_claude/S4_V1_REVIEW.md`) found that the preferred distance could exceed the unit's own reach (tuned f = 1.11), that the "unanswered" label counted any reachable enemy as an answer, and that guns behind a line never attracted committed units. v2 restarts every arm's budget on fresh seeds.

All of the following use only observed fields (positions, radii, range, minRange, damage counters).

1. **Threats to unit i:** enemies e with e's recent damage dealt z_out(e) > 0 whose reach covers i: centre distance ≤ range_e + both radii for melee and direct, and minRange_e ≤ centre distance ≤ range_e for artillery.
2. **Unanswered damage (replaces section 12 item 1's label):**
   - the damage i took during tick k is **unanswered** if, at tick k's snapshot, i was inside the reach of at least one threat that was **not** in i's own legal set;
   - otherwise it is answered;
   - the timing is as section 12 (the status recorded at the producing tick).
3. **Range-aware preferred reach distance to each enemy e** (in reach units: the gap for melee and direct, the centre distance for artillery). Let R_i be i's own reach and R_e the enemy's reach.
   - **We out-range e** (R_e < R_i): the kite band. The committed distance is R_e + m_k · (R_i − R_e), with m_k ∈ [0.2, 1] (a knob), kept ≤ R_i. Pull-back adds w · (R_i − R_e) · (1 − c)/2.
   - **e out-ranges us or matches us** (R_e ≥ R_i): the committed distance is f_c · R_i, with f_c ∈ [0.3, 1.0] (a knob, **≤ 1 by bound**: commit means within one's own reach). The **escape** distance is R_e + w · R_i. The preferred distance interpolates: d = f_c R_i + (escape − f_c R_i) · (1 − c)/2.
   - **The restoring force** G(1 − d/max(ρ, ε)) is unchanged, with the sign checks of section 3 repeated for both cases.
4. **The enemy set in movement:** E_i = the 8 nearest living enemies **∪** i's threats (cap 16 in total). Each enemy term is weighted 1 + λ_th · tanh(z_out(e) · 1 s), with λ_th a knob in [0, 3], and the mean is taken with these weights.
5. **Knobs:** f is replaced by f_c ∈ [0.3, 1.0] and m_k ∈ [0.2, 1.0]; λ_th ∈ [0, 3] is added; and **γ (the target preference) is fixed at 1** to keep the cap of 10 for the resonator and morale. Push-pull uses f_c and m_k with its G (3 knobs; c = 1 always). Bounds are otherwise as section 5.
6. **Section 12 item 2** (the target term toward engaged enemies) is kept.

**Clarifications (answering Codex's contract stop, `astelia_cpp/S4_V2_DEVELOPMENT_REPORT.md`):**

- **(Q1) The knob cap is raised to 11, logged.** The resonator and morale each have 11 knobs: K, K_t, κ, β, two role rates (ω or λ), G, w, f_c, m_k and λ_th. Push-pull has 3: G, f_c, m_k. The two stateful arms stay equal. The increase is a disclosed change from section 5's "at most 10", made before any v2 fight.
- **(Q2) The enemy set, exactly:** E_i = the 8 nearest living enemies (by centre distance, ties by lowest id), always kept. Then i's threats not already in it, in order of descending z_out(e), then ascending centre distance, then lowest id, until |E_i| = 16 or no threats remain.
- **(Q3) All v2 distance comparisons use centre distance, in model units.**
  - For a melee or direct unit u reaching target v: its centre reach is Rc(u → v) = range_u + r_u + r_v. For artillery: Rc(u → v) = range_u, with the minimum Rmin(u) = minRange_u.
  - **Own reach** of i toward e: R_i = Rc(i → e). **Enemy reach** of e onto i: R_e = Rc(e → i), and e threatens i only if Rmin(e) ≤ centre distance ≤ R_e.
  - The kite band, the commit, escape and interpolation formulas of item 3 apply to these centre distances.
  - The restoring force uses ρ_c = centre distance: G(1 − d / max(ρ_c, ε)).
  - **For an artillery unit i**, the committed distance is max(f_c · R_i, 1.05 · Rmin(i)): a committed gun never moves inside its own minimum range. Diving under an enemy gun's minimum range is not used in v2.
  - Sections 3-12 and the v0/v1 skeletons keep their own definitions (the gap for melee and direct), unchanged.

**S3-style checks to add:**
- the threat set on constructed cases (melee, direct, artillery dead zone);
- the unanswered label true only when a threat is out of i's reach;
- the preferred distance never exceeds R_i when c = 1 in either case;
- the sign of the restoring force on both sides of d in both cases;
- the weighted mean reduces to the plain mean at λ_th = 0;
- v0 and v1 fixtures unchanged with the skeleton flag.

## 14. Revision 6 (v3): no hovering in the kill zone (2026-10-05, after the v2 replay)

**Logged as an outcome-informed change** (section 10). It comes from a development replay (`viz_0g/replays_v2.json`, seed 2026100701, v2 stage-B knobs, against regular):
- the resonator destroyed every non-gun enemy by t = 62 s, with 34 of its 50 units alive;
- the remaining 7-8 guns then killed all 34 by t = 93 s, while our units hovered 294-416 px from the nearest gun with mean commitment +0.16.

The cause is section 13 item 3's **interpolation** in the out-ranged case. A middling commitment gives a preferred distance between our own reach (about 278 px centre to centre for shooters) and the enemy's (320 px): exactly where we are hit and cannot hit back.

**Change (out-ranged case only: R_e ≥ R_i, centre distances as in section 13; the kite band is unchanged):**
- **The mode is binary with hysteresis,** per own unit and enemy pair:
  - **commit** sets d = f_c · R_i (artillery: max(f_c R_i, 1.05 Rmin(i)));
  - **escape** sets d = R_e + w · R_i.
- **Switching:** the mode becomes commit when c > +0.2 and escape when c < −0.2. Otherwise it keeps its previous value. The initial mode is commit if c ≥ 0, else escape.
- **The hysteresis band 0.2 is fixed**, not a knob. Knob counts are unchanged (11, 11, 3).
- **The mode is controller memory:** it is cloned with the rest, and it is dropped when either unit dies.

**Checks:**
- no preferred distance strictly between the **effective** commit distance d_c = f_c · R_i (artillery: max(f_c R_i, 1.05 Rmin(i))) and R_e in the out-ranged case (answering Codex's v3 stop, `astelia_cpp/S4_V3_DEVELOPMENT_REPORT.md` at `ae6bc34`). If d_c ≥ R_e (only possible for artillery with a large Rmin), the commit distance is d_c and the check is vacuous for that pair;
- the hysteresis holds the mode for c in [−0.2, 0.2];
- the mode memory is cloned and isolated;
- v0, v1 and v2 fixtures stay unchanged with the skeleton flag.

## 15. Revision 7 (v4): a decision lives as long as it takes to carry out (2026-10-06, after the v3 recheck)

**Logged as an outcome-informed change** (section 10). It comes from the v3 recheck's matched regular replays (`astelia_cpp/S4_V3_RECHECK_REPORT.md`, `s4_v3_recheck_checks/replays/`):
- The resonator's ranged units rotate at ω_ranged ≈ −1.8 rad/s, a period of about 3.4 s. Their commitment c = cos θ therefore crosses ±0.2 about every 1.7 s.
- Crossing the gap between the commit distance (about 270 px) and the escape distance (about 606 px) takes 336 px ÷ 40–120 px/s ≈ 3–8 s. **Units reverse before they reach either safe distance**, and stay in the guns' range.
- Morale has no rotation and keeps its mode. It beats the regular script; the resonator does not.

A second cause is force cancellation (recheck F3): the summed enemy term over up to 16 pairs can cancel even when every pair is committed.

**The principle** (the owner's timescale ledger): a decision belongs to its own level's time. A unit-level movement decision's natural time is the time the unit needs to execute it. The oscillator keeps rotating; the decision holds over its own timescale.

**Change 1, travel-time hold (out-ranged pairs only; the kite band is unchanged):**
- When a pair's binary mode (section 14) **switches**, it is held for

      T_hold,ij = |d_escape,ij − d_commit,ij| / v_i

  Here v_i is the unit's own speed field from the observation, and both distances are as in section 14 (artillery: the effective commit distance).
- **The hold ends early** when the unit reaches its target band: |ρ_ij − d_mode,ij| ≤ 0.1 R_i.
- During a hold, c's threshold crossings are ignored. After it, section 14's hysteresis applies again from the current c.
- **A new pair's first mode** is set as in section 14, with no hold. A pair that dies or disappears drops its hold with its mode.
- If v_i ≤ 1 px/s (immobile or rooted), there is no hold.
- **No new knob:** the hold is computed from observed geometry and speed. Knob counts are unchanged (11, 11, 3).

**Change 2, commit focus** (against force cancellation):
- If a unit has **at least one out-ranged pair in commit mode**, its enemy velocity term uses **only its focus pair**: the committed out-ranged pair with the highest damage weight (section 13's threat weighting), ties by lowest enemy id. The other enemy terms are dropped for that tick.
- The ally force is unchanged.
- If no out-ranged pair is committed, the section-13/14 weighted mean over the threat set applies unchanged (escape from all threats stays coherent).
- Kite pairs keep the inherited law.

**Change 3, decision traces (output-only diagnostics; they change no action):** per unit and tick, retained in the replay export:
- the focus id;
- every out-ranged pair's mode and remaining hold;
- c;
- **velocity feasibility:** cos(the angle between the unit's actual velocity and the direction that reduces |ρ − d_mode| for its focus or main threat).

They report how often a held decision actually moves the unit the right way.

**Applies to:** resonator and morale identically (it is a skeleton feature). Push-pull is unaffected in effect, because c = 1 always: it has no switches and commits to a focus by construction.

**Checks:**
1. A switch starts a hold of exactly T_hold. Crossings of c during a hold are ignored. The hold ends at T_hold or on reaching the band, whichever comes first.
2. A v_i ≤ 1 unit has no hold.
3. **Focus:** with two symmetric enemies and both pairs committed, the summed enemy term is **not** zero (the recheck's counterexample now moves toward the focus).
4. The hold and focus memory are cloned and isolated, and dropped on death.
5. Traces leave actions byte-identical: the v4 run with traces equals the run without them.
6. The v0–v3 fixtures stay unchanged with the skeleton flag.

**Development:** exactly the amended S4 CMA-ES protocol (population, generations, budgets, stages A/B/C, validation sizes, A/B novice gates) for resonator, morale and push-pull with skeleton v4, on **fresh** development seeds in a new ledger.

**Before the capped run**, the runner gets the recheck F2 deadline repairs: bounded submission, an absolute monotonic deadline passed to the workers, timeouts clamped to the remaining allowance, cancellation of pending futures, and termination of active children on stop. They are tested with fake workers and no combat. Allowance: 360 minutes.

No registration, judging seeds or recorded run.

**Clarifications of Change 3, answering Codex's v4 contract stop** (`astelia_cpp/S4_V4_DEVELOPMENT_REPORT.md`, commit `babaaf5`). Traces are output-only and change nothing in the policy.
1. **Reference enemy.** It is the focus pair if one exists. Otherwise it is the **main threat**: the enemy in the unit's section-13 movement threat set E_i with the highest damage weight, ties by lowest enemy id. If E_i is empty, the feasibility is null with reason `no_reference`.
2. **Alignment** (option b). The reducing direction is computed from the **prepare(k) geometry** and that tick's preferred distance d_mode: the unit vector toward the reference if ρ > d_mode, and away from it if ρ < d_mode. It is compared with the **realized displacement during tick k**: the position after movement, collision separation and arena clipping, minus the position at prepare(k).
3. **Undefined samples** are null with a reason, and excluded from the cosine mean. The reasons are:
   - `zero_displacement`: the displacement norm is below 1e-9 px;
   - `coincident`: the centre distance to the reference is below 1e-9 px;
   - `at_distance`: |ρ − d_mode| ≤ 1e-6 px;
   - `no_reference`.

   Their counts are reported per reason, beside the mean and the distribution of the defined cosines.

**Planned v5 (not part of the v4 run; from the owner's external recheck, `docs/reviews/external_web_ai_recheck_r2_response.md`, A24):** the travel-time hold gets a **bounded, progress-aware release**. The hold ends early on:
- **no projected radial progress** over a declared window;
- **an infeasible retreat:** wall contact, or blocking;
- **loss or death of the reference;**
- **an urgent threat:** taking damage above a declared rate while out of reach.

Emergencies take precedence over the hold. The thresholds will come from the v4 decision traces (velocity feasibility, hold durations), and will be frozen before any v5 fight.

## 16. The v4 attribution test (a 2×2 diagnostic; from `astelia_cpp/S4_V4_RECHECK_REPORT.md`)

**The v4 result:** a package regression against regular at stage B. The resonator went from −7.57 (v3) to −22.18; morale from +8.55 to −15.41. The recheck shows that both the hold and the focus are implicated, but their separate effects are not identified.

**The "Planned v5" note above is superseded.** v5 is designed after this test (section 17, to come).

**The test:** four skeleton cells on the v3 skeleton, with every other rule unchanged:

| Cell | Travel-time hold (section 15, change 1) | Commit focus (section 15, change 2) |
|---|---|---|
| v3 | off | off |
| H | on | off |
| F | off | on |
| HF (= v4) | on | on |

- **Fixed knobs** (no tuning): the resonator and morale v3 stage-B selected knobs (`astelia_cpp/s4_v3_development`), the same in all four cells. Cell v3 thus reproduces v3 exactly on the new seeds.
- **Fights:** **fresh** development seeds (a new ledger, never judging): 100 two-orientation clusters on the stage-B full head, against both **novice** and **regular**. That is 4 cells × 2 arms × 2 heads × 200 = 3,200 fights.
- **Reported, descriptive only, with no verdict:** mean S with 95% intervals; the paired cell differences on common seeds; enemy guns alive; timeouts; and the section-15 decision traces for five predeclared regular trace seeds per cell:
  - **unit-intent changes and pair-mode changes counted separately** (the recheck's finding 2);
  - focus-while-escaping ticks;
  - holds expiring inside gun reach;
  - deaths that release holds.
- **Purpose:** attribution only. It answers whether the hold, the focus, or both cause the regression, at fixed knobs. Equal-budget retuning comes later, for whichever v5 package is chosen.
- **Cost:** about 3,200 fights, roughly 10 minutes at v4's measured rate (under 1 hour, decision 0031).

**The objective** (the drafter's decision, from the owner's goal of beating the scripted AI): **S stays the score**, survivors minus enemy survivors, because it decides who wins the fight.
- From v5 on, development selection uses the **regular-head S** as the primary target, with novice performance kept as a declared constraint.
- Guns alive, timeouts, damage and time to elimination are always reported beside S.

## 17. Revision 9 (v5): the v3 skeleton, tuned to beat regular (2026-10-06, after the section-16 attribution)

**What section 16 showed** (`astelia_cpp/S4_ATTRIBUTION_REPORT.md`; fixed v3 knobs; 3,200 fresh fights):
- **Commit focus hurts both controllers** against regular: morale +10.2 → +1.3; resonator −7.6 → −12.6.
- **The hold, alone,** barely moves the regular score (resonator −7.6 → −9.0; morale unchanged), and costs the resonator 10 points against novice.
- **Combined, they collapse the resonator** to −35.3 (an interaction of −21.4).
- The hold **did** cut actual pair-mode switching (892 → 139 per unit-minute), **without** improving outcomes. **So instability of the mode is not the main cause of losing to regular.**
- Against regular, the v3 resonator loses by elimination: 183/200 own eliminations; damage dealt 4,981 against taken 7,108. Morale "wins" by surviving to the timeout (197/200), with 9 enemy guns still alive.

**The reading:**
- The resonator's tuned rotation (ω_ranged ≈ −1.9 rad/s) was **selected on a pooled novice + regular score**. That score rewards aggressive cycling, which wins big against novice and loses to regular.
- The development **selection target** decides what the oscillator learns. The external recheck said the same (recommending regular-head selection, A24 in its response).

**v5:**
- **The skeleton is v3** (sections 13–14): the binary commit/escape mode with ±0.2 hysteresis and range-aware bands. **No travel-time hold and no commit focus** (both are removed as defaults, and stay available as labelled variants). Knob counts are unchanged (11, 11, 3).
- **The tuning protocol** is the amended S4 CMA-ES (population 16, 16 generations, the same budgets per arm) **with one change:**
  - **the selection score is the regular-head mean S** on the stage's tuning clusters;
  - **subject to a novice constraint:** a candidate whose novice tuning mean S is below 0 is ranked below every candidate meeting it.
  - Stage A stays melee-only against novice (unchanged; it has no regular head).
  - Equal budgets for the resonator and morale; push-pull is tuned the same way.
- **Validation** (unchanged sizes, fresh seeds): S against novice and against regular, guns alive, timeouts, damage dealt and taken, and time to elimination.
- **Also reported:** **the selected ω** for each role. If selection drives ω toward 0, the oscillator's rotation is not helping against regular. That is reported as a finding, not hidden.
- **Development stops before stage C** if the stage-B regular head of the resonator does not improve on v3's −7.6. The cost of a full stage C is spent only on a version that moves toward the goal (recheck finding: "proceed to C only after a declared fresh B gate").
- **Fresh development seeds** (a new ledger). No judging, registration or recorded run.

**Cost:** about 4–6 hours with 10 workers, at the measured v4 rate. **It runs only when the laptop is otherwise free:** after the C6 timing tonight (decision 0031: night runs need no approval).

**Section 17 amendments (answering `docs/reviews/tactical_0g_s17_design_review_codex.md`, CHANGES_REQUIRED):**
- **F1, scope:** **v5 development is stages A and B only.** Stage C, whose tuning panel is 19 elite doctrines with no novice or regular heads, is **not part of v5**. If the B gate passes, stage C's allocation and objective are declared in a later revision, before any C fight.
- **The B gate (exact):** after all-arm B validation, v5 is reported as **progress** only if the resonator's regular validation mean S is **strictly greater than −7.62** (the section-16 v3 baseline); equality stops. It is a development resource gate, not statistical superiority, and not "beats regular" (a score above −7.62 may still be negative).
- **The tuning ranking (exact, stage B):**
  - Each head's mean comes from its own tuning clusters (ten novice, nine regular), averaged over both orientations.
  - A **novice mean ≥ 0 is eligible.** Ineligible candidates rank below every eligible one, whatever their regular score. Within each group the ranking is by regular mean S, and exact ties keep the earlier incumbent.
  - The same ordering feeds the optimizer and the incumbent. If the selected candidate is ineligible, that is reported.
  - Stage A is unchanged (melee-only novice).
- **F2, the claim narrowed:** section 16 shows that **this pair-level hold reduced pair-mode changes without improving the regular outcome at fixed v3 knobs**. It does **not** rule out instability of the coherent unit intent as a contributor, because physical movement reversals were not measured. v3 stays the baseline.
- **F3:** the selected ω is a **diagnostic** of what this bounded optimizer chose, not a test of whether rotation is necessary. The values are reported even on a B stop.

## 18. Revision 10 (v6): an amplitude-and-phase resonator (2026-10-07, after the v5 trace diagnostic)

**Logged as an outcome-informed change** (section 10). It comes from `astelia_cpp/S4_V5_DEVELOPMENT_REPORT.md` (v5 B: resonator regular −6.025, morale +9.53) and the trace diagnostic `astelia_cpp/S4_V5_TRACE_DIAGNOSTIC.md` (60 fresh fights, descriptive).

**What the traces show** (descriptive, no causal isolation):
- **The resonator's ranged phase never settles.**
  - Locked (|dθ/dt| < 0.1) in under 0.5% of samples; the observed rate stays near ω_ranged ≈ 1.91 rad/s, a half-cycle of 1.64 s.
  - |P| ≥ |ω| in only about 4% of samples.
  - Its commit→escape span takes about 8.7 s to cross at base speed.
  - Its direct and gun units make 24–27 large (1 s) reversals per unit-minute, against morale's 1–2.
  - Its direct units spend 5.4% of their time inside enemy gun bands, against 1.1% for morale's, and 88% of its direct deaths happen there.
- **Morale's state is stationary about 92% of the time.** Its m relaxes to about 0, and the ±0.2 hysteresis then **keeps the last mode (escape)**: nearest-gun commit fraction 0 from 40 s on.
  - Morale's positive score is survival to timeout. It is not gun killing.
- **Against novice, the same rotating resonator removes 189 of 200 enemy guns and wins.**

**The reading, at the RRG level:**
- The v5 resonator is a **phase-only rotator**. Its commitment cos θ has unit amplitude whatever the drive, so it re-crosses ±0.2 every half-cycle and overwrites the mode memory.
- A physical **resonator** has an **amplitude** that grows with matched drive and decays without it. Its response is strong when driven and fades at rest.
- That is the missing degree of freedom. **Without drive, a resonator's commitment should fall to about 0**, where the hysteresis keeps the last mode as morale's does. **Under sustained pressure, its amplitude should build** in the drive's direction, and its phase rotation stays available for coordinated engagement.

**Change: the resonator's state becomes a complex amplitude z_i** (one per own unit; this replaces θ_i):

    dz_i/dt = (μ + i ω_role) z_i − |z_i|² z_i
              + K · mean_{N_i} e^{−r²} (z_j − z_i)
              + K_t · (ζ_i − z_i)
              − P(i)

- One RK4 step per tick, positions frozen at the snapshot, exactly as section 4.
  - z starts at 0 (morale starts at 0 too; v5's uniform random phase is dropped because the amplitude now carries the state).
- **μ** (1/s) is the **damping or gain**:
  - μ < 0: a damped resonator; z → 0 without drive;
  - μ > 0: a self-sustained oscillation of radius √μ.
  - It is a knob in [−2, 2]. The optimizer chooses the regime, and the selected μ is reported.
- **ω_role** (rad/s): the natural rotation, as before.
- **The coupling is diffusive** on z: the standard linear coupling of Stuart-Landau oscillators.
- **ζ_i** is the mean z of the other previous attackers of the unit's current target (section 4's ψ group); the K_t term is 0 when that group is empty.
- **−P(i)** is the real drive, with the same sign convention as morale. Positive pressure pushes Re z negative (pull back).
- **Commitment:** c_i = clip(Re z_i, −1, 1).
- **Target alignment:** a_ij = 1 − min(1, |z_i − ζ_ij| / 2), and 0 when ζ_ij is undefined. This is the same form as morale's 1 − |m − μ|, on the complex state.
- **Everything else is the v3 skeleton (sections 13–14), unchanged:** range-aware bands, the binary commit/escape mode with ±0.2 hysteresis and its memory, threats and their weighting, targeting, the movement law, pressure, and the stop/failure rules. There is no travel-time hold and no commit focus.

**Knob ledger (resonator; equal count with morale, 11).**
- Added: **μ**.
- Removed: **ω_melee**, now fixed at 0.
  - Reason: v5 melee units die by about 16 s whatever their state (all melee die in every pairing). Their selected ω (−0.36) is a diagnostic of no consequence.
- Kept: K, K_t, κ, β, ω_ranged (artillery uses it), G, w, f_c, m_k, λ_th.
- Bounds: μ ∈ [−2, 2] 1/s. Other bounds as sections 5 and 13.
- Morale (11) and push-pull (3) are unchanged.

**Normalization ledger:**
- z is dimensionless. Every term of dz/dt is in 1/s: μ, ω, the coupling rates K and K_t, and P (κ · damage rates, already 1/s per section 2).
- The cubic saturation bounds |z| at about √max(μ, 0), plus the drive response.
- **The clip to ±1 is the only nonlinearity added at the action level,** exactly as morale's clip.

**What the change can and cannot show (claim boundary):**
- With ω_ranged = 0 and real coupling, the real axis of z is a morale-like relaxation with cubic instead of hard saturation. **So the resonator family now contains a morale-like special case.**
- If selection drives ω_ranged → 0, rotation is not helping. If it drives μ ≪ 0, the amplitude dynamics are acting as relaxation.
- Both are reported as findings. A win at those values would **not** support "oscillation is necessary".
- **Reported diagnostics:** the selected μ and ω_ranged, the fraction of samples with |z| < 0.2, and the rotation rate of arg z when |z| > 0.2.

**Closest known method:**
- **Stuart-Landau (Hopf normal form) oscillators** with diffusive coupling and external forcing, as used for coupled-oscillator robot controllers (central pattern generators).
- **The difference here:** the forcing is the unit's own damage pressure. The amplitude, not the phase alone, sets commitment through the mode hysteresis. And the coupling graph is the army's spatial neighbourhood and target groups.

**Checks** (S3 style, before any fight):
1. **The free amplitude decays.** With μ < 0 and no drive or coupling, |z| decays as e^{μt}.
2. **The limit cycle.** With μ > 0, |z| → √μ and arg z rotates at ω.
3. **Constant drive.** With P constant and μ < 0, ω = 0, z → the real fixed point of μz − z³ = P, and c has the opposite sign to P.
4. **Coupling.** Diffusive coupling of two units equalizes their z.
5. **The c interface.** c = clip(Re z) feeds the unchanged section-14 hysteresis; with c ∈ [−0.2, 0.2] the mode never changes.
6. **The RK4 step** matches an independent implementation of this ODE to 1e-9.
7. **Unchanged arms.** Morale, push-pull and nearest are byte-identical to v5.
8. **Clone and isolation** of z, as for θ.

**Development (the v5 protocol, unchanged otherwise):**
- **Stages A and B only.** CMA-ES with population 16 and 16 generations, the same budgets per arm.
- **Stage-B selection:** regular-head mean S, with novice eligibility (novice tuning mean ≥ 0).
- Fresh development seeds in a new ledger. Validation sizes as v5. All four arms are re-run, so the comparisons are on one seed panel.
- **Gates:**
  - **Progress** if the v6 resonator's stage-B regular validation mean S is **strictly above −6.025** (the v5 value).
  - **"Beats regular in development"** if it is **strictly above 0**.
  - The second is the W4 condition for drafting an S5 registration (section B6 of the plan). It is not itself a registered result.
- **Cost:** about 65 minutes with 10 workers, at the measured v5 rate (60,996 fights in 64.2 min).

No registration, judging seeds or recorded run.

### 18.1 Amendment answering the Codex section-18 review (`docs/reviews/tactical_0g_s18_design_review_codex.md`, CHANGES_REQUIRED, `a8a5001`)

**F1 (high): the ally similarity, now explicit.** Section 3's resonator similarity cos(θ_j − θ_i) is replaced, for v6 only, by an **amplitude-gated phase similarity**:

    s_ij = Re(z_i · conj(z_j)) / max(|z_i| · |z_j|, δ²),    δ = 0.2 (fixed; the hysteresis threshold)

- **Range:** s_ij ∈ [−1, 1], because |Re(z_i z̄_j)| ≤ |z_i||z_j|. It is dimensionless.
- **When both amplitudes are ≥ δ,** s_ij = cos(arg z_j − arg z_i), the v5 form.
- **Toward zero:** if either amplitude is small, s_ij shrinks continuously to 0. Zero–zero and zero–nonzero pairs give exactly 0, with no undefined argument.
- **Which state enters movement:** the state after this tick's accepted integration, as for v5's θ.
- **This changes the formation law.**
  - Morale's similarity at m_i = m_j = 0 is 1 (full in-phase attraction); v6's at z = 0 is 0 (attraction A only).
  - **So v6 is a changed controller package, not an isolated amplitude intervention.**
  - v6 claims no unchanged-C4 phase-law identity. v0–v5 dispatch, historical fixtures and reference adapters are preserved separately.
- **Fixtures:** sign and range; zero–zero; zero–nonzero; equal phase at amplitudes above and below δ; opposite phase; deterministic ties (N_i ties are unchanged: by id).

**F2 (medium): zero startup, kept and stated.**
- z_i = 0 at birth, and P = 0 with all neighbours at 0 keeps z exactly 0 under RK4 **for either sign of μ**. Neither positive μ nor diffusive coupling breaks the symmetry.
- **The controller is therefore pressure- and coupling-triggered.** A unit is excited by its own pressure, or through coupling by a driven neighbour or by its target group.
- Positive-μ oscillation needs a nonzero excitation first. No seeded perturbation is added.
- **The mode hysteresis inherits section 14 unchanged.**
  - A new out-ranged pair starts in **commit** when c ≥ 0, so a quiet start holds commit, not escape. Morale inherits exactly the same rule from m = 0.
  - A new pair initializes from the current c, not from another pair's history.
- **Amplitude decay alone does not guarantee a safe escape:**
  - with μ > 0, an excited, unforced unit approaches its free radius √(μ/ν) and can keep crossing thresholds;
  - while the amplitude is appreciable, rotation can cross either threshold.
- **Stage A is melee-only and ω_melee = 0.** Under real forcing and real coupling from zero, the state stays on the real axis, so stage A does not exercise rotation. It is stated as such.
- **Checks:**
  - exact all-zero invariance for μ < 0 and μ > 0;
  - first-pressure onset;
  - excitation by a driven neighbour;
  - stage-A real-axis invariance;
  - a new pair at c = 0 starting in commit;
  - a previously escaping pair keeping escape while c stays in [−0.2, 0.2].

**F3 (medium): normalization and corrected checks.**
- **The cubic term is −ν|z|²z with ν = 1/s fixed** (not a knob), so every RHS term is in 1/s with z dimensionless.
- **The free radius is √(μ/ν).** It is not a numerical bound: driven amplitude can exceed it.
- For an isolated, unforced unit with r = |z|:

      dr/dt = μr − νr³,    d(arg z)/dt = ω only where r > 0

- **The corrected checks:**
  1. **μ < 0, r₀ > 0:** r(t) follows the radial solution, which falls faster than r₀e^{μt}. Compare with the analytic solution of the Bernoulli equation, and with e^{μt} only in the small-amplitude limit.
  2. **μ = 0:** algebraic decay, r(t) = r₀/√(1 + 2νr₀²t).
  3. **μ > 0, r₀ > 0:** r → √(μ/ν). With ω ≠ 0, arg z rotates at ω; with ω = 0 the phase is stationary. **Zero stays zero** (invariance, separately).
  4. **Constant drive, μ < 0, ω = 0:** the unique real root of μx − νx³ = P has the sign opposite to P (P ≠ 0).
  5. **Coupling,** tested on its own: the diffusive term contracts z_i − z_j by itself. A **matched damped pair** (equal μ < 0, ω, no drive) converges. **Declared counterexamples:** differing ω or drives need not equalize; two identical μ > 2a oscillators with symmetric coupling rate a admit the antiphase solution z₂ = −z₁ of radius √((μ − 2a)/ν).
  6. **An independent complex RK4 reference** to 1e-9 per step, **plus physical-tick refinement:** the same tick at dt and at dt/4 substeps, reported over the declared envelope (F5).

**F4 (medium): target alignment, now on morale's scale.**

    a_ij = max(−1, 1 − |z_i − ζ_ij|)

- **On the real axis with bounded states this is exactly morale's 1 − |m_i − μ_ij|** (1, 0, −1 at distances 0, 1, 2). The lower clip only matters beyond distance 2, which the unbounded complex state can reach. Section 18's [0, 1] form is withdrawn.
- **ζ_ij is the complex arithmetic mean of z_k** over the living own units k ≠ i whose previous-tick target is j. "Previous-tick" means assignments are frozen through the tick.
  - It is recomputed from each joint RK4 trial state, and scoring uses the updated state.
- **Defined and undefined cases:**
  - an **empty** group is the only undefined case: a_ij = 0, and for the unit's own target the whole K_t term is omitted;
  - a **nonempty** group whose mean is 0 (all-zero, or cancelling z and −z) is **valid**: a_ij = max(−1, 1 − |z_i|), and the K_t term is −K_t z_i;
  - the v5 resultant < 0.1 rejection does **not** apply;
  - a non-finite member is a controller failure, never an empty-group fallback.
- **The target score keeps the inherited engaged-enemy term** γ · tanh(κ(z_in(j) + z_out(j)) · 1 s) with γ = 1 (sections 12–13), not section 3's superseded beaten-enemy preference.
- **Fixtures:** empty, self-only (empty), singleton, cancellation, a real-axis comparison with morale's alignment, scale and saturation, and exact η = 0.2 and tie behaviour.

**F5 (high): numerical safety, without clamping the state.**
- **Both components of z are persisted, unbounded but finite.** c = clip(Re z, −1, 1) is computed only after the integration result is accepted. The action clip is never a state clip.
- **The integration policy** (declared before any fight):
  - each tick's RK4 is split into n equal substeps, where n is the smallest integer with h·L ≤ 1, h = dt/n and L = |μ| + |ω| + 3ν·Z² + K + K_t;
  - Z = max(max_i |z_i|, ∛(max_i |P_i| / ν) + √(max(μ, 0)/ν)) + 1, evaluated at the tick start.
    - Z bounds the amplitude the tick can reach: the drive's fixed-point scale ∛(|P|/ν), plus the free radius, plus a unit margin.
    - Z is checked again after the tick, and a tick that ends above its own Z is recomputed once with Z doubled. That recomputation is counted.
  - the cap is n ≤ 64;
  - if the cap is reached, or any stage value is non-finite, the step fails (below).
  - This bounds h·L inside explicit RK4's real-axis stability interval (about 2.78) with margin. **The pressure P enters only through Z;** it is an additive forcing and contributes no Jacobian term of its own.
- **Finiteness is checked** on both components, norms, cubic products, every RHS stage, group means, alignment and similarity values, scores and raw actions, **before** any clip, min or max can hide a non-finite value.
- **On failure:**
  - the unit atomically retains its last finite complex state, publishes hold with target none, and the failure is counted;
  - dependent trial states contaminated by a failed member fail with it;
  - **the inherited runner's raw failure record and stop semantics apply unchanged** (a failed fight is recorded as a controller failure, never scored or dropped).
- **A no-combat stability and refinement check before the run,** over the envelope:
  - μ ∈ [−2, 2], ω ∈ [−2, 2], K and K_t ∈ [0, 5];
  - |z₀| up to 10;
  - |P| up to 500 /s, the κ upper bound 50 × a damage-rate bound of 10 /s, with the per-tick damage clipped to remaining HP by `World::damage`;
  - the result is the substep counts, the refinement error against dt/4, and the absence of non-finite values.
  - **If the envelope cannot be met within n ≤ 64, the drafter declares a different integration policy before any fight.** The ODE is never silently changed.
- **Clone checks** cover both components, counters, answered-status memory, previous assignments, pair modes and diagnostics. A clone is advanced independently and the parent is verified unchanged.

**F6 (medium): claims corrected.**
- The amplitude is a **candidate explanation and design hypothesis**, not "the missing degree of freedom".
- **Fixing ω_melee = 0 is a disclosed budget tradeoff** to keep 11 knobs.
  - About 16 s is the resonator–regular **mean** melee death time; the maximum is 28.1 s.
  - Melee states act on allies before death, through coupling, forces, targeting and screening.
- **The selected μ and ω_ranged are optimizer diagnostics.**
  - **No oscillation-necessity claim is made either way:** not for a zero-ω win, and not for a nonzero-ω win, without a necessity intervention.
  - No universal physical-resonator or RRG requirement follows from selecting a Hopf normal form.
  - No causal background-transformation, C5 or unchanged-C4 claim follows from this one-level controller.
- **Evidence wording:**
  - |ω_ranged| ≈ 1.91 rad/s (selected −1.912), and the observed rates are absolute rates.
  - The phase "rarely meets the operational lock threshold in these traces" (not "never settles").
  - **Reversals, matched definitions** (1 s, speed ≥ 5 px/s): resonator direct/gun 27.48/24.32, morale 0.92/0.74 per living unit-minute.
  - The 8.73 s span is a distance-over-base-speed comparison, not a measured travel time.
  - Gun-band deaths are co-occurrence, not killer attribution.
- **The pressure is restated exactly:** own P = κ(z_in,answered − β z_out − z_in,unanswered), with status from the producing tick (sections 12–13).
  - Positive answered pressure pushes toward escape; unanswered damage makes P negative and pushes toward commit.
  - Additive −P excites a zero state, unlike v5's P sin θ.
  - With ω ≠ 0 the initial drive sign does not fix the sign of Re z permanently; this is measured, not promised.

**Gates (restated in full):**
- **Stage A and stage B:** the resonator's **novice validation mean S must be strictly > 0** (the inherited separate gate; tuning eligibility ≥ 0 does not replace it).
- **Stage B progress:** regular validation mean S strictly > −6.025.
- **"Beats regular in development":** strictly > 0, **and** the novice validation pass, **and** failure-free completion.
  - It is an exploratory W4 trigger to **draft** S5. It is not P1 support, superiority over morale, source qualification, approval or authorization to run S5.
- **Equality fails** every gate.
- The −6.025 reference is a historical, unmatched panel, not a paired comparison.
- **All of v5's tuning ordering is inherited:**
  - both orientations averaged within a seed;
  - ten novice and nine regular tuning clusters;
  - novice tuning mean ≥ 0 eligibility first, then regular mean S;
  - ineligible candidates rank below every eligible one;
  - exact earlier ties stay incumbent;
  - the identical ordering feeds CMA and retention;
  - fixed generations and budgets;
  - fresh development entropy;
  - no validation-based selection;
  - all-arm validation;
  - explicit not_run for C, P2 and P3;
  - input pins, bounded deadlines and child cleanup.
- **Gate fixtures** use fake records (boundary values, negative novice, a failure row), with no combat.

**Diagnostics (amplitude-aware):**
- The host exports Re z, Im z and |z| per unit.
- **arg z is valid only where |z| ≥ 0.2.** No atan2(0, 0) is reported as phase 0 or coherence 1.
- The arg-rate is sampled only when both consecutive endpoints are valid, unwrapped within contiguous valid segments and reset across gaps, with null reasons and denominators.
- The v5 phase-coherence, target-phase and candidate diagnostics become amplitude-aware, or are explicitly not_run for v6.
- Diagnostics on versus off leave actions byte-identical. Death and absence clear all per-unit memory.

**Implementation:**
- separate versioned complex state, RHS and policy dispatch;
- v0–v5 scalar paths, historical fixtures, the regular and novice configurations and unchanged-arm actions preserved byte-identically at fixed knobs and requests;
- no new engine information: the observation, prepare, decide and clone interfaces are reused.

| Finding | Fix | Cause |
|---|---|---|
| F1 the ally similarity undefined after θ was removed | An explicit amplitude-gated similarity; the changed package disclosed | I changed the state without tracing every use of θ in the skeleton |
| F2 zero startup and mode behaviour unstated | Stated, with checks | I assumed "decays at rest" without the exact-zero and positive-μ cases |
| F3 a missing ν; wrong checks | ν = 1/s; corrected radial checks; refinement | I wrote the normal form without units and stated the checks from memory |
| F4 the alignment is not morale's form; group semantics | Morale's scale; a complete group contract | A form chosen by analogy, not checked against morale's range |
| F5 no numerical safety contract | A substep policy, finiteness, failure semantics, an envelope check | I relied on the continuous ODE's saturation |
| F6 overstated claims; mixed reversal definitions | Narrowed; matched definitions | I compressed the diagnostic report too far |

### 18.2 Amendment answering the Codex round-2 review (`docs/reviews/tactical_0g_s18_design_review_codex_r2.md`, CHANGES_REQUIRED; R1, R2, N1)

**Precedence.** 18.2 overrides 18.1, which overrides 18, wherever they differ. The superseded section-18 sentences no longer apply:
- one step per tick;
- the unqualified exponential, limit-cycle and equalization checks;
- the [0, 1] alignment;
- "the missing degree of freedom";
- the ω-necessity wording.

**R1, the pressure envelope, derived.**
- Adopt the reviewer's conservative bound for the admitted A/B rosters (fixed game mirror B):
  - enemy starting HP 7,150; minimum own maxhp 92; no healing or spawning; dt = 1/30;
  - EMA factor q = e^{−dt/2}, b = (1 − q)/dt = 0.495856 /s.
  - With β ≤ 3 and κ ≤ 50: **|P| ≤ 50·b·(1 + 3·7150/92) = 5,805.3 /s.**
- This is a bound argument, not a claim about reachable trajectories.
- **The no-combat envelope becomes |P| ≤ 6,000 /s**, with |z₀| up to Z(6,000) = ∛6000 + √2 + 1 ≈ 20.6.
- **A pressure outside the envelope** (possible only with a roster outside A/B) is checked **before** integration. It is recorded as a controller failure under the inherited runner semantics, never extrapolated.
- **Arithmetic feasibility:** at μ = 2, |ω| = 2, K = K_t = 5 and |P| = 6,000:
  - L ≈ 2 + 2 + 3·20.6² + 10 ≈ 1,287 /s;
  - n = max(1, ⌈dt·L⌉) = 43 ≤ 64.
  - This shows only that the policy is feasible, not that it is accurate (R2).

**R2, numerical acceptance, exact.**
- **Substeps:** n = max(1, ⌈dt · L(Z)⌉). n = 64 is allowed; n > 64 is a failure.
- **Trial-stage amplitudes are monitored:** every RK4 stage state of every unit must satisfy |z| ≤ Z.
- **Retry:** if any stage or the endpoint exceeds Z, the tick is recomputed **once**, from the tick-start joint state, with Z doubled (and n recomputed). Pressure, topology, assignments and counters are frozen; counters are consumed once; only an accepted result is published.
- **Terminal failure:** if the retry also exceeds its Z, or n > 64, or any value is non-finite, the tick fails. The unit retains its last finite states, publishes hold with target none, the failure is counted, and the inherited runner stop applies. A failed tick is never scored as an ordinary outcome.
- **The no-combat acceptance check,** before any fight:
  - **isolated units:** a grid over μ ∈ {−2, −1, 0, 1, 2}, |ω| ∈ {0, 1, 2}, |P| ∈ {0, 1, 10, 100, 1,000, 6,000}, |z₀| ∈ {0, 0.5, 2, 20};
  - **coupled pairs and triples:** K and K_t ∈ {0, 1, 5}, with drives of opposite sign;
  - **refinement:** each policy tick against the same tick integrated with 4n substeps (the reference).
  - **Acceptance:** max |Δ Re z| and max |Δ Im z| ≤ 1e-3, and |Δ c| ≤ 0.02 (the inherited section-8 commitment criterion, kept).
  - Threshold-sensitive decisions are covered by boundary fixtures with explicit margins, not by demanding action equality at discontinuities.
  - **The inherited section-8 check is also retained:** < 0.02 commitment difference over captured default-knob engineering fights.
- **Equality with an independent RK4 implementation (1e-9)** remains as an implementation-agreement check only; it is not an accuracy claim.

| Yes/no stop | Action | Role |
|---|---|---|
| Does the no-combat acceptance check fail anywhere in the envelope? | Stop implementation; the drafter declares a different integration policy (for example a smaller h·L target, or an implicit step) before any fight | drafter |
| Does any development fight record a numerical failure? | Preserve the attempt; stop the arm per the inherited runner rule; report | implementer |
| Is the state ever clipped, or the ODE adjusted, by the implementer? | Not allowed. Any change is a declared drafter revision | implementer → drafter |

**N1, clarified.** The similarity gate uses the amplitude **product**: attenuation applies when |z_i|·|z_j| < δ² = 0.04, not when either amplitude alone is below δ.
- Aligned amplitudes 0.1 and 1 give s = 1; 0.1 and 0.1 give s = 0.25.
- This is the intended choice: a continuous similarity that tends to 0 as either amplitude tends to 0.
- An asymmetric-amplitude fixture is added.

| Finding | Fix | Cause |
|---|---|---|
| R1 the 500 /s envelope was unsupported | A derived conservative bound (5,805 /s); the envelope set to 6,000; out-of-envelope pressure recorded as failure | I cited the victim-side HP cap for an outgoing, multi-victim, β-weighted quantity |
| R2 no accuracy acceptance; trial-stage bounds; retry terminal rule | An acceptance grid with limits; stage monitoring; exact n, retry and failure rules | I specified stability without an accuracy criterion |
| N1 the product gate was unclear | Clarified; fixture added | — |

## 19. The success criterion is efficient killing, not survival (owner, 2026-10-07)

**The owner's words** (on v6's survivor-score result): "surviving doesn't count as a win; it can be part of it, but you survive better if you efficiently kill enemies."

**Why S alone is not enough.**
- With equal armies (50 against 50), S = own survivors − enemy survivors equals kills − losses.
- A controller that kills the enemy's non-gun units and then **stalls until the 150 s timeout** scores positive S while the enemy keeps its guns:
  - v6 resonator against regular: 198/200 timeouts, 9.47 enemy guns alive;
  - morale: 191/200 timeouts, 9.11.
- This is the survivor-score advantage the owner rejects as a win.

**The criterion from now on** (it replaces "mean S > 0" as the W4 condition and as the P1 target):
- **The primary outcome is an elimination win:** the enemy army is destroyed (0 enemy survivors) before the timeout, with ≥ 1 own survivor.
- **Reported with it:**
  - the elimination-win rate per head;
  - S (secondary);
  - enemy guns destroyed;
  - time to elimination;
  - own losses (efficiency: own losses per enemy unit killed).
- **A timeout is never a win**, whatever its S.
- **"Beats the scripted level in development"** requires:
  - an elimination-win rate **above 50%** against that head;
  - mean S > 0;
  - novice and regular both;
  - failure-free.
- **Tuning objective (stage B):**
  - first the elimination-win rate on the tuning clusters (regular head, novice eligibility as before);
  - then mean S as the tie-break;
  - then own losses (fewer is better).
- **P1 for any S5 registration** is restated on the elimination-win rate, with S as a reported secondary. The drafter writes it, and the owner approves it.

**Consequence for v6:** v6 is **NOT_READY** under this criterion. It has 0 eliminations against regular, as v5 and morale do. Its development result stands as recorded (the survivor-score gate), and is not a win.

**What winning requires** (from `astelia_cpp/S4_V5_TRACE_DIAGNOSTIC.md`):
- against regular, every arm loses every melee unit by about 16–28 s;
- the enemy's 10 guns out-range our direct units (320 against 278 px), and the regular profile has a line formation, shell dodge, lead and abilities;
- against novice, the resonator removes 189/200 guns.

**Next step, evidence first:** the host does not export who hit whom. Before designing v7, add an **observer-only killer telemetry**:
- the source unit of every damage event and every kill;
- no policy or engine-behaviour change;
- actions byte-identical with telemetry on and off.

Then run a short diagnostic: how guns die against novice, and why gun assaults fail against regular (timing, approach paths, cover, simultaneity).

**v7 is then designed from that evidence.** The leading hypothesis to test, not assume: **collective commitment.** A phase-locked target group commits **together**, so the guns cannot destroy attackers one at a time. This is a resonator-level mechanism (group synchronization drives a coordinated assault).

### 19.1 What the kill telemetry shows (`astelia_cpp/S4_GUN_ASSAULT_DIAGNOSTIC.md`, `e0afa50`) and the next probe

**Evidence** (120 fresh development fights, observer-only telemetry, actions byte-identical):
- **Enemy guns die to artillery, not to assaults:**
  - against novice, our artillery makes **556 of 565 gun kills (98.4%)**;
  - direct and melee approaches on regular guns almost never connect. Entrants are covered by about 3–4 other gun bands, and most die. The v6 resonator made 3,041 entries; 312 reached its own range and 9 dealt gun damage.
- **Enemy artillery makes 81% of our deaths against regular**, most of them **before** the gun-only phase.
- **The regular guns dodge shells and hold a line:**
  - about 80–95 k dodge-goal returns per 20 fights (novice: none);
  - guns about 46 px apart, each overlapping about 8.8 other bands.
- **The result against regular:** we destroy only **0.4–3.3 of 10 guns** (against novice, 8.6–9.95), and there are **0/20 elimination wins for every arm**.
- **The relevant game facts** (the catalog): a shell aims at the target's position at release (`lobLead` off), with splash radius 40 and storm dodge distance 110. Regular has `dodgeShells` on (it steps out of predicted splashes) and `lead: raw`. Our controller sees no shells, but it sets every unit's target every tick and sees cooldowns.

**The reading: beating regular is an artillery duel against a dodging gun line.**

**Hypothesis to test before any v7 design: synchronized battery volleys.**
- If our guns hold their targets until several are ready and then fire together, the dodge may stop working.
- That works when the guns are assigned to **adjacent** enemy guns in the line (a net), so a sidestep out of one splash lands in another.
- This is a timing-coordination mechanism, a natural job for phase locking in a resonator.

**Feasibility probe (scripted, not an RRG controller; descriptive, fresh development entropy):** probe arms that differ **only** in our artillery's targeting and timing. The rest of the army is fixed to the v6 attempt-2 resonator knobs.
- P0: the v6 resonator as is;
- P1: a synchronized volley on one target gun (hold until k ready);
- P2: a synchronized net on adjacent target guns;
- P3: P2 with our direct units held outside all enemy gun bands until the enemy guns are depleted.

**Prerequisites, checked first:** whether "target none" actually holds fire under game rules, and what the abilities (`Auto`: barrage, slow) do.

**Measurements:** against regular, enemy guns destroyed, our shell hit rate, our gun losses, elimination wins and timeouts. Against novice, the same, for a sanity check.

If a scripted probe cannot kill regular guns, the v7 hypothesis is wrong, and the drafter returns to the evidence before designing.

### 19.2 The volley probe (`astelia_cpp/S4_VOLLEY_PROBE.md`, `07d0b60`, PARTIAL) and the next probe

**Facts:**
- **Holding fire works:** target none gives zero launches.
- **Auto abilities are inactive in the fixed world** (`sandboxAbilities=false`).
- **Synchronized volleys and nets (P1–P3), at one declared setting,** won **0/20 regular and 0/20 novice**. P0, the v6 resonator, won 14/20 novice.
  - **Confound:** the probe also suppressed every non-volley gun target and lost firing time while waiting. Fewer shells were fired at guns: 236 / 167 / 127 against P0's 280.
- **The surprise:** against regular, **our shells aimed at enemy guns hit 277 of 280 times (99%)**. Yet only 0.55 of 10 guns die per fight.
  - **The dodge is not what saves the guns.** Too few shells are aimed at them.
  - We aim about 14 per fight in total, about 1.4 hits per enemy gun.
  - A gun has 181 HP and a shell does about 15 after protection, so about 12 hits kill one.
- **Our guns mostly shoot other targets, or are out of range.**

**The reading, revised:** the artillery duel is lost by **dispersion and low engagement**, not by the dodge. The symmetric range is 320 px, so whichever side concentrates its fire on one gun at a time wins the exchange: Lanchester-style concentration of force.

**Next probe (scripted, descriptive), with the same fixed world and the rest of the army at v6 knobs:**
- **P4, focus fire without holding:** every gun that can reach any enemy gun targets **the reachable enemy gun with the least remaining HP** (ties by id), and fires as soon as it is ready. Otherwise it keeps its v6 target.
- **P5:** P4, plus our guns **commit**: they move to keep the focused enemy gun within reach, while direct units keep their v6 behaviour.
- **P6:** P5, plus direct units focus the same enemy gun when they can reach it.
- **Measured:** elimination wins, enemy guns destroyed, our gun losses, shells fired at guns and hits, time to the first enemy gun kill. Against novice too.

**If concentration kills regular guns, the RRG version is target-group synchrony:** K_t locks the attackers of one target, so commitment to it is collective. That becomes the v7 design. **If it does not,** the drafter returns to the evidence.

### 19.3 The focus-fire probe (`astelia_cpp/S4_FOCUS_PROBE.md`, `3e4ac4f`, DONE)

**Arms,** each one declared setting:
- **P4:** guns focus on the reachable enemy gun with the least remaining HP, with no holding of fire;
- **P5:** P4, plus guns commit radially to their own reach minus 12 px;
- **P6:** P5, plus direct units join. P6 was never realized against novice, so P6 = P5 there.

| Arm | Regular: elimination wins | Regular: enemy guns destroyed / own guns lost | Novice: elimination wins | Novice: S |
|---|---|---|---|---|
| P0 (v6) | 0/20 | 0.65 / 2.60 | 14/20 | +2.95 |
| P4 focus | 0/20 | 0.45 / 2.25 | 17/20 | +11.05 |
| **P5 focus + commit** | 0/20 | **3.40 / 10.00** | **20/20** | **+38.85** |
| P6 | 0/20 | 3.45 / 10.00 | 20/20 | +38.85 |

**Reading:**
- **Focused, committed guns kill guns quickly:** against regular the first enemy gun dies at about 14 s (against about 75 s for v6), and against novice the result is a rout.
- **Against regular they lose the whole battery.** The killers are enemy artillery (133) and **enemy direct units (58)**.
- **The regular line screens and supports its guns.** A committed gun walks into both the enemy battery and the direct screen.
- **Single-unit commitment is therefore not enough. The commitment must be collective:**
  - the guns must commit **together**, so the enemy battery's fire is split;
  - and **with a screen**: our direct units engage the enemy direct screen at the same moment.
- This is a timing and coordination problem: a phase-locking job.

**Next (v7 candidate, after the 0h medium experiments free the machine):**
- **Collective commitment by target-group synchrony:**
  - K_t couples the guns that focus on one enemy gun;
  - a commit wave starts only when the group's coherence (order parameter) exceeds a threshold, so the guns and their screen advance together, then return to escape together.
- **Scripted probe first:** a synchronized group advance of the battery plus a direct screen, against regular. Only then the RRG version.

### 19.4 The collective-commitment probe (B4h; scripted, descriptive; declared before any fight)

**Question:** P5's focused, committed guns kill regular guns fast (first kill at about 14 s) but lose the whole battery. **Is the loss caused by how they commit (one by one, into many enemy gun bands, with no screen), or would any commitment lose?** If a scripted collective commitment wins the artillery duel against regular, v7 encodes it as resonator synchrony. If none does, the drafter returns to the evidence.

**The geometry that motivates the arms** (an estimate to be measured, not assumed):
- The regular guns hold a line about 46 px apart; both sides' guns reach 320 px.
- **A gun committed at 308 px (reach − 12) perpendicular to the line's middle** is inside the reach of every enemy gun within √(320² − 308²) ≈ 87 px of its foot point along the line. That is 3–4 enemy guns, matching the 3–4 gun bands that covered entrants in §19.1.
- **The same gun placed on the line's axis beyond the end gun** is in reach of only that one: the next gun is at 354 px. The second gun stays out of reach up to about ±79° off the axis (at ±60° it is 333 px away).
- So **concentrating on the end of the line** (Lanchester's defeat in detail: crossing the T) could face 1 enemy gun instead of 3–4. That holds only if the line does not turn, which the probe measures.

**Arms** (every arm is the v6 attempt-2 stage-B controller with overlays, the P5 conventions of `s4_focus_probe_v1/POLICY.md`, and fresh development entropy):
- **P5 (control):** exactly as in §19.3, re-run on the new seeds.
- **P7, a synchronized wave on one shared target:**
  - **The shared target:** the shared anchor of P5 (the weakest reachable enemy gun, ties by id). All own guns target it while it is within their reach, otherwise they keep their v6 target.
  - **Staging:** until the wave starts, each own gun moves to its staging point: on the line from the target to itself, at distance (max enemy gun reach + 30 px) from the **nearest living enemy gun** (solved along that line; if it cannot be solved, it holds position). Own guns do not fire at guns while staging, but keep v6 fire at other targets.
  - **The wave starts** when at least 80% of living own guns are within 20 px of their staging points, **or** 20 s after the first enemy gun enters any own gun's sight, whichever comes first. Then every gun commits at once, as in P5, to the shared target at reach − 12 px.
  - **There is one wave per fight.** After it starts, the group continues as P5 with a shared target: when the target dies, the next shared anchor is chosen. There is no re-staging.
- **P8 = P7 plus a direct screen:**
  - From the wave start, every living own direct/ranged unit moves to an **escort point**: 60 px from the centroid of the committed own guns toward the shared target. Its fire targets the nearest enemy direct/ranged unit within its native reach, otherwise its v6 target.
  - Melee stays v6.
- **P9 = P8 with an end-of-line target and staging:**
  - **The target:** for each living enemy gun g, compute u_g, the unit vector from the centroid of the **other** living enemy guns to g; the candidate post is s_g = g + 308·u_g. **Exposure(g)** = the number of living enemy guns whose reach (320 px) covers s_g. The target is the g with the least exposure; ties go to the lowest remaining HP, then the lowest id. It is re-chosen when the target dies.
  - **The posts:** own guns spread over an arc of radius 308 px around g, from −60° to +60° about u_g. Assignment is by angular order around g (the i-th own gun by angle gets the i-th of n equally spaced arc points).
  - **Staging:** as in P7, but each gun's staging point lies on the ray from g through its arc point.
  - Wave start, screen and fire: as P8.
- **When all enemy guns are gone,** every overlay falls through to complete v6 actions (as in §19.3).

**One declared setting per arm.** No threshold, margin, arc or timing is tuned after outcomes. The constants (30 px, 80%, 20 px, 20 s, 60 px, ±60°, 308 px) are declared here.

**Panel:** 10 fresh development clusters × 2 orientations × {P5, P7, P8, P9} × {regular, novice} = 160 fights. Controlled team 0, paired seeds, the fixed S4 world (50 against 50, game rules, 150 s, `sandboxAbilities=false`), as in §19.3. About 3 min of combat at the §19.3 rate (longer on the loaded laptop).

**Measured, per arm and head:**
- elimination wins (enemy 0, own ≥ 1, t < 150 s) and timeouts;
- enemy guns destroyed, own guns lost, own losses, and mean S;
- **exposure as realized:** for each committed own gun and tick, the number of living enemy guns whose reach covers it, averaged over commit ticks;
- **simultaneity:** the time from the wave start until 80% of living own guns are within their own reach of the target;
- **line response:** the change in the enemy gun line's principal-axis angle between the wave start and the first enemy gun kill;
- the killers of own guns, by team and role;
- the first enemy gun kill time, conditional on a kill;
- shell hits and launches at enemy guns.

**What the outcomes mean (descriptive, not verdicts):**
- **P9 wins eliminations against regular, or destroys ≥ 7 of 10 enemy guns while losing fewer guns than it kills:** collective, end-on concentration is a mechanism worth encoding. **v7 design:** target-group synchrony (K_t over each target group, a coherence-triggered commit wave, and the exposure term as a geometric input to the group's phase target).
- **P7 or P8 beat P5 but P9 adds nothing:** synchrony and the screen are the mechanism, and geometry is not.
- **No arm improves on P5's gun exchange against regular:** collective commitment is not the missing piece. The drafter returns to the telemetry before any v7 design.
- **The novice results** are a sanity check only: P5 already routs novice.

**Limits declared in advance:**
- The enemy line can turn, advance or break formation. P9's exposure is measured, not assumed.
- Staging may stall if the enemy advances. The 20 s fallback bounds the stall.
- The arc assignment ignores collisions. Native collisions, clipping and reflexes may obstruct the posts.
- These are scripted policies, not an RRG controller. A win here is evidence for the mechanism, not for the resonator.

**Stop rows:**

| Yes/no | Action | Role |
|---|---|---|
| Is the compute projection over 1 h before 22:00? | Ask the owner first (decision 0031) | implementer |
| Does a protected file, knob, source or binary drift, or does the controller fail? | Stop; preserve the evidence; report PARTIAL | implementer |
| Is any constant or rule changed after a fight has run? | INVALID; a new declaration on fresh seeds | implementer |
| Does P5 on the new seeds differ grossly from §19.3 (regular own gun losses < 7/10 or > 10, or enemy guns destroyed outside 1–6)? | Report it before reading the other arms; it may signal a pipeline difference | implementer |

### 19.5 The collective-commitment probe result (`astelia_cpp/S4_COLLECTIVE_PROBE.md`, `abad882`) and the next step

**Result (160 fights; one declared setting per arm; descriptive):**
- **Against regular: 0/20 elimination wins in every arm, and every arm lost all 10 of its guns.** No arm improved on P5's gun exchange:
  - P5 destroyed 3.15 enemy guns;
  - P7 (synchronized wave) 2.45;
  - P8 (+ screen) 1.85, losing all 50 units;
  - P9 (end-of-line) 2.75.
- **Against novice:** P5, P7 and P8 won 20/20; P9 won 15/20.
- **P9 was not realized as designed, so it is inconclusive, not a test of end-on concentration:**
  - its staging points lay outside the arena (no position is outside every enemy gun's reach + 30 px);
  - every wave started on the 20 s fallback, with only 6.65 of 10 guns still alive;
  - on average, 5.4 guns ever reached a post.
- **The wave was realized in P7 and P8** (readiness reached in 20/20 fights, 80% engagement within about 2 s). Their realized exposure was higher than P5's: 3.7–4.0 enemy guns per committed gun-tick, against 1.35. The pooled definitions differ, since P5's includes its approach ticks. **A synchronized wave enters the overlapping bands together, so it is shot together.**
- **Per Codex's design-review note 1,** each arm bundles several changes (target sharing, staging, fire suppression, movement, screen), so these are descriptive patterns, not isolated causes.

**Reading:** collective commitment as scripted here does not win the artillery duel against regular. **The owner's second-view rule now applies:** with no elimination win, do not encode collective commitment into a resonator. Diagnose first, then test the next smallest scripted hypothesis. From now on, the v7 trigger is **real elimination wins against regular and clearly better than P5** (it replaces §19.4's "≥ 7/10 guns destroyed" reading).

**The open question is the exchange rate:**
- P5 lands about 48 hits on enemy guns per fight (953 of 1,120 launches over 20 fights). That kills about 3 guns.
- The enemy kills all 10 of ours: enemy artillery makes about 7 of those kills per fight, and enemy ranged units about 3.
- Why does the enemy battery put far more effective fire on our guns than ours puts on theirs, with equal guns and equal range?

**Next step (stored data only, no new fights; Codex), the fire-efficiency diagnostic** on the stored P5 and P7 regular traces of this probe:
1. **Per side:** launches per living gun-second; the fraction of gun-time that is moving, in range of any target, ready but not firing, and firing.
2. **Whether moving suppresses firing:** windup interruptions and launch gaps after a move command.
3. **Enemy target choice:** the share of enemy gun launches aimed at our guns rather than at other units, and their hit rate on our (non-dodging) guns.
4. **Range at death:** the distance from each own gun's death to the nearest enemy gun and to the nearest enemy ranged unit.
5. **Where our shells go:** the share of our launches aimed at guns against other targets, over time.

**Then:** the smallest scripted hypothesis that the numbers point to. Candidates, not chosen:
- fire uptime: stop moving once in range;
- a counter-battery priority for our guns;
- a ranged screen placed against the enemy ranged units that kill our guns.

This is a stored-data analysis. It runs while the 0h pilots run.

### 19.6 The fire-efficiency diagnostic (`astelia_cpp/S4_FIRE_EFFICIENCY_DIAGNOSTIC.md`, `ed2633f`) and the spacing probe

**What the stored traces show** (P5 and P7 against regular, P5 against novice, 60 fights; no new fights):
- **Splash multiplicity decides the artillery exchange.** In P5 against regular:
  - each of our successful gun-targeted shells damaged **1.11** enemy guns;
  - each of the enemy's damaged **3.85** of ours, and up to nine.
  - The enemy landed fewer successful gun shells (22.75 per fight against our 47.65), but dealt **2.11×** our artillery damage to guns (31,604 HP against 14,958). In P7 the ratio is 2.96×.
- **Against novice it reverses:** our shells damaged **3.27** novice guns each, and every novice gun died. The regular line keeps its guns about 46 px apart, against a 40 px splash; our committed battery does not.
- **Not the cause:** firing uptime and counter-battery priority.
  - Our guns fire as fast as the enemy's: about 0.82 launches per gun-second in range, a 1.2 s cadence, even while moving.
  - Movement does not cancel the windup.
  - We aim two-thirds of our shells at guns, the enemy under a quarter.
- **Secondary factors:**
  - enemy ranged units add 11.7% of the damage to our guns;
  - 164 of 167 non-hitting shells were aimed at a gun that died before impact (redundant commitment).
- **Why P5 clusters:** its commitment replaces the whole v6 gun movement command, including the v6 neighbour forces, so every gun converges on the same arc around one target.

**The hypothesis (one change): our battery loses because it bunches, so one enemy shell damages several guns.**

**Spacing probe (scripted, descriptive, one change on P5, declared before any fight):**
- **P5 (control)**, re-run on fresh seeds.
- **P10 = P5 plus a battery spacing rule.**
  - After P5 computes each own gun's movement goal, the goal is shifted away from every other living own gun closer than S, by (S − d) along the unit vector away from that gun, summed over neighbours.
  - The multiplier and stop distance are as in P5.
  - Targeting is unchanged.
  - **S = 2·(splash radius + gun radius)** from the catalog. That leaves no shared splash from a shell landing anywhere within one splash radius of a gun's centre (a margin for the shell aiming at the release-time position). The implementer reads both radii from the catalog and declares the number before any fight.
- **P11 = P10 with S = splash radius + 2·gun radius.** That is the minimum, with no shared splash only for a shell landing on a gun's centre. It gives a two-point dose of the same single change.
- **Panel:** 10 fresh development clusters × 2 orientations × {P5, P10, P11} × {regular, novice} = 120 fights. Same world and conventions as §19.3–19.5.

**Measured:**
- elimination wins, timeouts, S;
- enemy guns destroyed, own guns lost, own losses;
- **gun victims per successful shell, for both sides** (the diagnostic's measure);
- realized nearest-own-gun distance (median and 10th percentile);
- artillery HP exchange ratio;
- shells aimed at already-dead guns;
- killers.

**Reading (descriptive, under the owner's criterion):**
- **Enemy victims per shell fall towards 1 and the exchange ratio turns, but there are still no elimination wins:** spacing is necessary but not sufficient. The next single change is chosen from the remaining factors (redundant commitment, the enemy ranged units).
- **Real elimination wins against regular, clearly better than P5:** a candidate for a resonator mechanism. Spacing is an element-level short-range repulsion, which the v6 neighbour forces already contain and P5 discarded.
- **Victims per shell do not fall** (spacing is not realized, for example because of clipping or the arena's width): inconclusive, reported as such.

**Stop rows:**

| Yes/no | Action | Role |
|---|---|---|
| Does the compute projection exceed 1 h? | Stop and report | implementer |
| Is a constant or rule changed after any fight? | INVALID; a new declaration on fresh seeds | implementer |
| Is P5 on the new seeds outside §19.4's sanity bounds? | Report it before reading the other arms | implementer |
| Is a 0h pilot batch running? | Wait for it to finish before combat (no heavy 0h and 0g runs together) | implementer |

### 19.7 The spacing probe result (`astelia_cpp/S4_SPACING_PROBE.md`, `a13b51c`; Codex's owner recheck pending)

**Result** (120 fights; one declared setting per arm; descriptive). Both spacings come from the catalog (splash 40 px, body 10 px): P10 S = 100 px, P11 S = 60 px.

| Against regular | P5 (control) | P10 (S 100) | P11 (S 60) |
|---|---|---|---|
| Elimination wins | 0/20 | 0/20 | **2/20** |
| Enemy guns destroyed | 3.4 | 6.2 | 7.55 |
| Own guns lost | 10 | 10 | 9.95 |
| Our guns damaged per successful enemy shell | 3.55 | 1.00 | 1.05 |
| Enemy artillery HP to ours | 2.06× | 0.78× | 0.59× |
| Own-gun last hits by enemy artillery / ranged | 151 / 40 | 89 / 99 | 64 / 124 |

- **Novice:** 20/20 in every arm.
- **The splash hypothesis is supported:** spacing alone took enemy victims per shell from about 3.6 to about 1, and turned the artillery exchange in our favour.
- **P11's two wins are the first elimination wins ever against regular.** They are an observation (2 of 20), not a rate, and they fall short of the owner's criterion (above 50%).
- **The new limiting factor is the enemy ranged units.** With our guns spaced, they make most of the last hits on our guns.

**Next:**
1. Codex's owner recheck of this run.
2. A stored-data ranged-threat diagnostic: where the enemy ranged units stand relative to their guns and ours; what our own ranged and melee units do meanwhile; what differed in the two wins.
3. Then the smallest single scripted change it supports, on top of P11.

**The resonator reading, for later (not a design yet):** spacing is the v6 element law's short-range repulsion, which P5's commitment discarded. A v7 must keep it in every mode.

### 19.8 The ranged-threat diagnostic (`astelia_cpp/S4_RANGED_THREAT_DIAGNOSTIC.md`, `940208e`) and the escort probe

**Codex's owner recheck of the spacing run:** APPROVE_WITH_NOTES (`docs/reviews/tactical_0g_spacing_probe_recheck_codex.md`).
- Every table number matches the raw data.
- **Both P11 elimination wins are genuine:** cluster c02/o0 at 69.6 s and cluster c09/o1 at 73.5 s.
- Presentation errors were corrected.

**What the stored P5, P10 and P11 traces show** (no new fights):
- **The enemy ranged screen** stands about 52–59 px in front of its own guns.
  - It reaches our battery at about 9.7 s and first damages a gun at about 11.6 s, in all 60 fights.
  - Its reach covers 90–98% of our early gun positions.
  - In P11 it makes 43% of our gun HP loss over the full fight, and most of it after 20 s.
- **Our ranged units do not contest it.** Early in the fight they are a median **322 px** from the nearest enemy ranged unit, about 45 px beyond their 277 px reach.
  - They mostly target enemy melee, or nothing.
  - They kill almost no enemy ranged before 20 s (P11: 4 in 20 fights).
- **Our melee** stays about 157 px from the enemy ranged units (melee reach 61 px).
- **In P11's two wins against its 18 non-wins:**
  - our artillery killed more enemy ranged before 20 s (10.5 against 5.8 per fight);
  - more enemy guns died before 30 s (8.0 against 6.4);
  - fewer of our guns died before 30 s (4.5 against 8.1).
  - These are associations from two fights, not causes.

**The hypothesis (one change on P11): our ranged units stand too far back to engage the enemy screen that shoots our guns.**

**Escort probe (scripted, descriptive, declared before any fight):**
- **P11 (control),** re-run on fresh seeds.
- **P12 = P11 plus a ranged escort position.** It applies while both sides have living guns; otherwise everything is v6/P11.
  - **Assignment:** each living own ranged unit is assigned to its nearest living own gun (ties by id).
  - **The escort direction û:** the unit vector from that gun toward the nearest living enemy ranged unit within 400 px of the gun. If there is none, toward the centroid of the living enemy guns.
  - **The escort point:** gun position + d·û. The unit's movement goal is replaced by the escort point; P5's multiplier and stop-distance conventions apply.
  - **Targeting is unchanged** (v6/P11).
  - **d = 60 px,** derived as splash 40 + ranged body 9 + gun body 10 = 59, rounded up. An escort standing there is outside the splash of a shell aimed at its own gun's centre. This matches P11's own-gun spacing.
- **P13 = P12 with d = 120 px.** A second dose of the same change, further forward, to contest the screen earlier.
- **Panel:** 10 fresh development clusters × 2 orientations × {P11, P12, P13} × {regular, novice} = 120 fights. Same world, conventions and spacing as §19.6; the process gate covers 0h runs.

**Measured:**
- elimination wins, timeouts, S;
- enemy guns destroyed; own guns lost; own losses;
- enemy ranged killed by our ranged units before 20 s and 30 s;
- own-ranged distance to the nearest enemy ranged unit at 10–20 s;
- the share of reachable gun-threatening enemy ranged that is selected as a target;
- gun HP lost to enemy ranged and to enemy artillery, over time;
- our ranged losses and their killers;
- victims per shell (the spacing must stay realized);
- escort arrival (the fraction of the gun phase within 20 px of the escort point).

**Reading (descriptive):**
- **Elimination wins clearly above P11's, moving toward the owner's >50% criterion:** the escort is a candidate mechanism. In the resonator it would be an element-level rule: ranged elements hold a position between their battery and the nearest threat.
- **Our ranged units arrive and engage, but the guns still die:** the escort is not sufficient. The next single change is the targeting priority (candidate 1) or the gun post (candidate 3).
- **The escort is not realized** (no arrival, or the spacing is lost): inconclusive.

**Stop rows:** as §19.6 (a 1 h projection; INVALID on any change after a fight; P11's sanity on the new seeds reported first; wait while a 0h batch runs).

#### 19.8.1 Amendment answering the Codex §19.8 review (`docs/reviews/tactical_0g_s198_probe_review_codex.md`, CHANGES_REQUIRED)

19.8.1 overrides 19.8 where they differ.

**Self-audit (the drafter's causes):**
- **R1:** I wrote "P5's multiplier and stop-distance conventions" for ranged units, but P5 defines them only for guns, around a focus radius. The cause: I copied the gun rule's wording without checking which units it covers.
- **R2:** the zero-vector and tie cases were not specified.
- **R5:** I inherited P5's sanity window for a P11 control.

**R1, the movement rule:**
- P12 and P13 **recompute the ranged movement from the escort-point error.** For each assigned ranged unit:
  - the goal = the escort point **after the native arena clip**;
  - multiplier = 1 if the unit's current centre is more than **2 px** from that clipped goal, otherwise 0;
  - stop distance = 0.
- The v6 ranged multiplier is not used; no gun multiplier is copied.
- **Gun decisions are exactly P11's.** **Ranged targeting is exactly the prepared v6 decision.** Melee is v6.

**R2, the direction (all from the same prepare snapshot, all in fixed id order):**
- **The assigned gun:** the nearest living own gun to the unit; ties go to the lowest gun id.
- **The threat:** the nearest living enemy ranged unit with centre distance **≤ 400 px** (inclusive) from the assigned gun; ties go to the lowest id. û points from the gun toward it.
- **If the vector is shorter than 1e-9 px,** or there is no such threat: û points toward the centroid of the living enemy guns (summed in ascending id order).
- **If that vector is also shorter than 1e-9 px:** û points toward the nearest living enemy gun (ties by id).
- **If even that vector is degenerate:** this unit keeps the complete prepared v6 action for this tick. Such ticks are counted.
- **With no living own gun or no living enemy gun:** the complete P11/v6 fallthrough for everyone. No stale assignment is kept.

**R3, realization (no new mechanism):**
- Escort points use the **current observed** gun positions, not the spacing-shifted gun goals.
- No lanes, avoidance, extra repulsion, reassignment or clearance correction are added. Native collisions and P11's spacing stay as they are.
- **The splash claim is narrowed:** d = 60 keeps an escort centre outside the splash of a shell landing on its **assigned** gun's centre (the bound is 40 + 9 = 49 px; the gun radius is an extra margin). It says nothing about shells aimed at other guns or at the escorts.
- **The audit reports:**
  - raw and clipped escort goals;
  - goal-to-other-gun clearances;
  - shared or coincident escort points;
  - realized ranged-to-gun and gun-to-gun nearest distances;
  - victims per shell for both sides;
  - blocked realization.

**R4, measurement conventions (sealed before any fight):**
- **Arrival:** the unit's post-step centre within 20 px of the point computed from that step's prepare snapshot.
  - Report raw-point arrival and clipped-goal arrival separately.
  - The denominator is living own-ranged unit-ticks while both sides had living guns at prepare.
  - Also report first arrival, holding, and actual displacement.
- **Common windows:** [10, 20) s and [20, 30) s; strict event times (< 20 s, < 30 s).
- **The targeting share** keeps the diagnostic's definition:
  - opportunity = a unit-tick with at least one reachable enemy ranged unit that threatens any living own gun;
  - the numerator = such a threat selected.
  - **Reach** = each pair's native range plus both body radii; geometric reach is not a legal or ready shot.
- **Last hits:** opposing-team kills only; friendly damage is reported separately. HP is actual capped HP lost.
- **Victims per shell** are inherited from the fire-efficiency diagnostic, for both teams, with incidental targeting reported separately.
- **The categorical readings now have declared rules:**
  - **"Clearly above P11":** the arm's regular elimination wins are ≥ 5/20 **and** at least 3 more than P11's on the same seeds.
  - **"Arrive and engage":** clipped-goal arrival ≥ 50% of the arrival denominator **and** own-ranged last hits on enemy ranged before 20 s at least twice P11's (and at least 5 in 20 fights).
  - **"Spacing lost":** enemy victims per successful gun-targeted shell > 1.5.
  - Anything else is reported descriptively, including mixed and unavailable cases.
- **Limits:** none of these readings is a population rate, permission for v7, or a resonator claim. Zero kills under unchanged targeting does not by itself refute the position hypothesis.

**R5, the control:**
- The fresh 40-fight P11 block is run and **reported first, descriptively**, before P12 and P13.
- **It is flagged, not aborted,** if regular enemy guns destroyed < 4 or own guns lost < 7: a gross departure from the historical P11's 7.55 and 9.95.
- **P5's window is not used.** No tuning or reinterpretation after the intervention arms are read.

**R6, execution:**
- The implementer keeps the mandatory pgrep gate before **every** combat block (engineering included), with a separate timestamped gate receipt per attempt.
- **Records:** UTC start and end, with code and binary identities.
- **Resume behaviour:** the scripts resume by skipping verified completions. They never replay a possibly executed or ambiguous fight, and they fail closed on ambiguity.
- Entropy is claimed only after clearance; the worker bounds and the stage limits are kept.
- **Combat is executed by Claude** (the Codex sandbox cannot list processes).

### 19.9 The escort probe result (`astelia_cpp/s4_escort_probe_v1/S4_ESCORT_PROBE.md`, `0f8e823`; Codex's owner recheck pending)

| Against regular (20 fights each) | P11 (fresh control) | P12 (escort d = 60) | P13 (escort d = 120) |
|---|---|---|---|
| Elimination wins | 1 | **6** | **5** |
| Timeouts | 11 | 0 | 0 |
| Enemy guns destroyed | 6.95 | 8.25 | 8.0 |
| Own guns lost | 9.9 | 8.75 | 9.3 |
| Own losses (of 50) | 43.5 | 48.75 | 49.3 |
| Escort arrival (clipped goal) | n/a | 37% | 7% |
| Own ranged selecting a reachable gun threat | 54% | 3% | 0.5% |

- **Novice:** 20/20 in every arm, but our losses rise from 11.25 to 31 (P12) and 39 (P13).
- **Declared readings (§19.8.1):**
  - **both escort arms are "clearly above P11"** (at least 5/20, and at least 3 more wins on the same seeds);
  - "arrive and engage" is **false** for both;
  - spacing is kept (enemy victims per shell 1.05).
- **The escort helps, but not the way the hypothesis said.** Our ranged units almost stop selecting the enemy ranged threat, and make about no early kills. The likely mechanism is that **they shield**: they stand between the screen and our guns and take the fire. That is not yet shown; Codex's stored-data mechanism diagnostic is running.
- **The progress so far against regular:**
  - P5: 0/20;
  - P11 spacing: 2/20 (fresh P11 control: 1/20);
  - P12 spacing + escort: **6/20**.
  - The owner's criterion is above 50%.
- **Next:** the recheck and the mechanism diagnostic, then the smallest single change on P12 that the numbers support.

### 19.10 The escort mechanism (`astelia_cpp/S4_ESCORT_MECHANISM_DIAGNOSTIC.md`, `3898a90`) and two single-change arms on P12

**Recheck:** APPROVE_WITH_NOTES (`docs/reviews/tactical_0g_escort_probe_recheck_codex.md`). All 620 raw hashes, the sealed inputs, every reported number and all 11 wins are verified.

**The mechanism, from the stored traces:**
- **The escorts are sacrificial.** They draw enemy fire and buy the guns an early survival window:
  - at 30 s, P12's wins keep 5.83 guns against 1.86 in its losses;
  - **in every escort win, all our ranged units die**, and the guns finish the fight.
- **Our artillery removes the enemy screen, mostly as splash** from shells aimed at enemy guns: early screen kills rose from 122 to 237, and 230 of those were incidental.
- **The escorts bunch.** Each successful enemy shell aimed at an escort damages **6.04** of our ranged units. That is the same splash failure the guns had before §19.6.
- **Against novice,** the escorts walk into artillery that P11 never exposed them to, so the losses rise.

**Probe (scripted, descriptive, declared before any fight; two single-change arms on P12):**
- **P12 (control),** re-run on fresh seeds.
- **P14 = P12 plus escort target priority.** While the escort phase is active: if a geometrically reachable enemy ranged unit threatens any living own gun, the ranged unit's target is the nearest such enemy (ties go to the lowest id). Otherwise its v6 target is kept. Movement is exactly P12's.
- **P15 = P12 plus escort spacing.** While the escort phase is active, each ranged unit's escort goal is shifted, as P11 shifts guns: by (58 − d) along the unit vector away from every other living own ranged unit closer than 58 px.
  - 58 = splash 40 + two ranged bodies of 9.
  - The shifts are summed in id order, with P11's +x convention at coincidence.
  - The goal is then native-clipped; multiplier = 1 if the final goal error is over 2 px, otherwise 0; stop 0.
  - Targeting is exactly P12's.
- **Panel:** 10 fresh clusters × 2 orientations × {P12, P14, P15} × {regular, novice} = 120 fights. Conventions, measurements and stop rows as in §19.8.1.

**Added measurements:**
- escort victims per successful enemy shell aimed at an escort;
- the threat-selection share;
- early kills of enemy ranged by our ranged units and by our artillery;
- the gun-survival curve at 10–60 s.

**Reading rules:**
- **"Clearly above P12":** regular elimination wins ≥ P12's + 3 on the same seeds, and ≥ 8/20.
- Novice is a sanity check (20/20 expected); its losses are reported.
- Anything else is descriptive.
- **The owner's criterion is above 50%.** Only a win rate in that range would make the scripted controller the feasibility witness for a v7 resonator design.

## 20. Revision 12 (v7): the resonator carries the witnessed mechanisms (2026-10-07, after §19.3–19.10)

**Why now:**
- The §19.5 trigger is met. The scripted P12 (focus + commit + spacing + escort) has **real elimination wins against regular**: 6/20 and 7/20 on two fresh panels, against P5's 0/20.
- The owner's second-view rule is met too: a scripted feasibility witness first, then an RRG controller revision.
- Further single scripted changes have plateaued: P14 8/20, P15 6/20.

**Logged as an outcome-informed change** (section 10): every mechanism below was found by the §19 probes on development seeds.

**The question v7 answers:** do the resonator's dynamics, which decide **when** each unit commits (amplitude, phase, target-group synchrony), add anything over P12's always-on rules?
- **A pass:** v7 at or above P12 on the same validation seeds.
- **An equal result** at a relaxation-like setting (μ ≪ 0, ω → 0) means the oscillation adds nothing. That is reported as a finding.

**What the probes showed, and how v7 expresses each finding:**

| Witness | Finding | v7 element-level rule |
|---|---|---|
| §19.6–19.7 (splash) | Bunched guns lose the artillery exchange 2:1. Spacing turns it. | **C2, same-role spacing in every mode.** v6's swarmalator neighbour law already has an in-phase spacing of 100/(1 + 0.8) ≈ 56 px. P5's commit override discarded it. v7 keeps the v6 neighbour term in every mode, and **adds** P11's shift for guns (S = 60 px) and P15's for ranged units (S = 58 px) to the movement goal, so the spacing holds when commitment forces dominate. Fixed constants from the catalog, not knobs |
| §19.3 (P5) | Committed, focused guns kill guns. v6's guns almost never commit (P0: 0.65 enemy guns destroyed) | **C1, the gun commitment geometry:** an artillery unit in commit mode toward an enemy gun takes the preferred distance **R_i − 12 px** (P5's post) instead of max(f_c R_i, 1.05 Rmin). **The resonator decides whether it commits:** the v3 mode hysteresis on c = clip(Re z) is unchanged |
| §19.3 (P4/P5) | Focus: guns that can reach an enemy gun shoot the weakest reachable one | **C1b, the gun target score:** for artillery units, legal enemy-gun targets get + (1 − hp/maxhp) added to v6's score (alignment + tanh(engagement)). The ±0.2 retention rule is unchanged. No other role's targeting changes |
| §19.8–19.10 (P12) | Escorts between the battery and the enemy screen buy the guns time (6–7 of 20 wins) | **C3, the escort as the ranged commit post:** while both sides have living guns, a ranged unit in commit mode toward a gun-threatening enemy ranged unit takes P12's escort point as its goal (the nearest own gun + 60 px toward the nearest threat, with 19.8.1's tie and fallback rules). In escape mode it uses v6's escape distance. **The resonator decides whether each ranged unit escorts.** P14's threat priority is not included (it did not separate from P12) |

**Unchanged from v6:**
- the z dynamics (μ, ω_role, K diffusive coupling, K_t target-group coupling, −P drive);
- the similarity and alignment;
- the mode hysteresis (±0.2);
- the threats, pressure, melee, the failure rules and the RK4 policy;
- no travel-time hold and no commit focus timer.

**Knob ledger:**
- The **11 v6 knobs:** K, K_t, κ, β, μ, ω_ranged, G, w, f_c (now direct units only), m_k, λ_th.
- **The fixed constants added** are all declared here and come from the catalog or a witness:
  - S_gun = 60 px, S_ranged = 58 px;
  - the escort offset, 60 px;
  - the gun post margin, 12 px;
  - the threat cutoff, 400 px.
- **The comparators are frozen, not re-tuned:** P12 (scripted witness), v6 at its attempt-2 knobs, and morale at its stage-B knobs. They are re-run on the same validation seeds.

**Normalization ledger:**
- distances in px, from the catalog (splash 40, bodies 9 and 10, ranges);
- z dimensionless;
- every term of dz/dt in 1/s, as in §18;
- the spacing and escort shifts act on movement goals (px), exactly as in P11, P12 and P15.

**Development** (the §18 protocol, with the §19 objective):
- **Stages A and B,** CMA-ES with population 16 and 16 generations; fresh development entropy in a new ledger.
- **Stage-B ranking:**
  1. the **elimination-win rate** on the regular tuning clusters (novice eligibility: novice elimination-win rate ≥ 50%);
  2. then mean S;
  3. then own losses.
- **Validation:** 10 fresh clusters × 2 orientations × {v7, P12, v6, morale} × {regular, novice}.
- **Readings (declared now):**
  - **"Progress over the witness":** v7's regular elimination wins on the validation panel ≥ P12's on the same seeds.
  - **"Beats regular in development"** (§19): a regular elimination-win rate > 50%, mean S > 0, novice too, no failures.
  - **The oscillation diagnostics are reported:** the selected μ and ω_ranged, the fraction of samples with |z| < 0.2, and the rotation rate of arg z when |z| > 0.2.
- **Cost:** about 65 min at the v6 rate; the projection is reported first; decision 0031 applies.

**Closest known methods and the difference:**
- **Stuart-Landau central-pattern-generator controllers** for timing; the **separation rule of boids and formation controllers** for spacing; **escort or bodyguard behaviours** in game AI for the screen.
- **The difference:** here one oscillator state per unit, driven by that unit's own damage exchange and coupled to its neighbours and its target group, decides commit or escape for **every** mechanism. The rules give only geometry. That is the RRG claim under test: a local resonance decides when the structure acts.

**Checks before any fight (S3 style):**
1. With every unit forced to commit (c = 1), v7's movement goals for guns and ranged units equal P12's on recorded observations, except for the v6 neighbour term and the spacing shifts. This is checked on fixtures.
2. The spacing shifts equal P11's (guns) and P15's (ranged) on the same observations.
3. With c = 0 hysteresis held, no mode changes.
4. The artillery target score adds (1 − hp/maxhp) only for legal enemy-gun targets.
5. v6, P12 and morale are byte-identical to their delivered versions.
6. Clone and isolation of z and the modes.
7. All §18 checks still pass.

**Stop rows:**

| Yes/no | Action | Role |
|---|---|---|
| Does a pre-fight check fail? | Fix before any fight | implementer |
| Does the compute projection exceed 1 h before 22:00? | Ask the owner | implementer |
| Is a rule, constant or knob bound changed after a development fight? | INVALID; a new revision on fresh seeds | implementer |
| Does v7 fall below P12 on validation? | Report it; the drafter diagnoses (resonator gating against the static rules) before any v8 | drafter |
