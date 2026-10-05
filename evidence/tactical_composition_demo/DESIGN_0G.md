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

**A step-refinement check:** compare one full phase/morale step with two half steps on the **same captured snapshots**, holding world dt, damage recurrence and previous assignments fixed; carry both state trajectories across the replay. Maximum absolute commitment difference must be < 0.02 over the 38 default-knob engineering fights per stateful arm. This isolates integration refinement from divergent game worlds; no additional fight is needed. Frozen-position ODE tests also use nonzero role rates, since midpoint resonator rates are zero.

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

The general host rejects passthrough unless started explicitly with `--test-controllers`; that flag is used solely by engineering tests/legacy fixture parity. The S3 runner accepts only fixed-world requests and never enables that flag. Its narrow input is arm, params, seed, swapSides, controlledSide, opponent, diagnostics; opponent may be a doctrine name or novice/regular/elite/elite-fast. Controlled-side skills always use game defaults plus Auto, regardless of opponent profile. The 38 checks are the 19 existing doctrine names × both orientations on fixed development seeds 2026100500+doctrine_index; one checked fight per arm/configuration, no tuning. Determinism uses fresh-process replay of one request per arm; cost uses timed executions from these 38 fights, with nearest on the same requests. Tests may use tiny synthetic worlds; no additional development fight grid.

| Stop question | Yes action | Role |
|---|---|---|
| Does a further unresolved design conflict appear? | Report it without silently changing the contract | implementer |
| Does an engineering check fail? | Complete the repair batch, then rerun only affected failed/invalidated checks | implementer |
| Is S3 engineering ready? | Hand off committed code and evidence for Claude review | implementer |
