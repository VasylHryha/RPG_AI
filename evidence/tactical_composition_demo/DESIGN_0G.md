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
