---
title: "GeoMind × Astelia — Validated Geometric Tactical-Memory Experiment"
revision: R3
date: 2026-10-01
status: REVISED_DESIGN_FIRST_MILESTONE_NOT_STARTED
supersedes: "GEOMIND_GEOTACTICS_ASTELIA_EXPERIMENT_PLAN_R2.md in full"
parent_standard: GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md
repository: VasylHryha/astelia-hunte
reference_commit: 11df55f6bc478bfe5b48f095a02f4b70225b3ab6
observed_remote_head: 67b929c886d8f7ab9900440bd7fcc582cf2dd521
scope: "experiments/formation_sandbox and its documentation/evidence only"
---

# GeoTactics — validate the experiment before training the model

> **A controller comparison is useful only when the simulation, information boundary, action contract and evaluation are trustworthy. A winning prototype classifier does not, by itself, validate Recursive Resonant Geometry.**

This is the only execution plan for this tactical experiment. It replaces the previous plan coherently. It does not replace the production Formation plan or the broader GeoMind theory. All interfaces marked **NEW** are proposed, not APIs verified to exist.

## 0. Execution status

| Field | Current record |
|---|---|
| Current milestone | **GT0 — trusted snapshot and decision boundary**, NOT_STARTED |
| Actual source inspected | Pinned sandbox `11df55f6…`; `formation_sim.js` blob `92d7e114733b03c1219cece548edb1ea93a53378` |
| Remote drift check | Observed `main` at `67b929c8…`, one commit after the pinned source; comparison showed monster-model changes, not sandbox changes |
| Last accepted GeoTactics code | None |
| Review checks executed | Isolated source-excerpt `fork()` characterization: eight expected legacy observations reproduced; no battle ticks |
| NOT_RUN | Full simulator parity, teacher qualification, model fitting, gauntlets, browser qualification and native Godot checks |
| Critical finding | Existing `fork()` is neither fully isolated nor an exact continuation; existing “honest” look-ahead retains enemy policy state |
| Exact next action | Implement GT0's complete boundary/clone/refactor batch and its fixtures, then run the named targeted checks |

| Milestone | Working result | Depends on | State |
|---|---|---|---|
| GT0 | One correct simulation snapshot and decision/application boundary | Source access | NOT_STARTED |
| GT1 | Explicit observations, action legality and fair baseline policies | GT0 | NOT_STARTED |
| GT2 | Qualified bounded teacher and leakage-safe collection | GT0–GT1 | NOT_STARTED |
| GT3 | Portable geometric map and matched simpler estimators | GT1 | NOT_STARTED |
| GT4 | Training-only collection/adaptation, model selection and freeze | GT2–GT3 | NOT_STARTED |
| GT5 | Closed-loop qualification, costs, controls and independent verdict | GT4 | NOT_STARTED |

**Execution rules.** Finish the current session's entire scoped code/caller/configuration/test batch before running builds or tests. Then run only the affected named checks. Complete related repairs before affected reruns. A documentation-only edit does not require a game rerun. Comparison fixtures can execute the historical and revised implementations during the consolidated verification phase; do not invent an unrequested pre-work benchmark run. Preserve other sessions' changes; do not reset/stash/clean, create worktrees or branches, coordinate other sessions, or push without permission. Use the repository's current root instructions for local commits. [P2, S1]

Implementation ends at `REVIEW_READY`. An independent review accepts the implementation or records exact blockers. Scientific outcomes are separately `SUPPORTED_WITHIN_SCOPE / NOT_SUPPORTED / INCONCLUSIVE`. Do not self-award a quality score in place of evidence.

## 1. Goal and limits

**Practical goal:** choose among the existing tactical plans at substantially lower runtime cost than qualified forward simulation, without unacceptable loss of fight/gauntlet quality. The experiment may also find that simple kNN or rules are already better; that is a legitimate result.

**Research question:** do learned prototype geometry, adaptive adjacency and bounded diffusion add measurable value over matched static representations and simple readouts?

**Theory boundary:** the initial candidate is **prototype regression with bounded graph diffusion**. It does not contain recursive coarse-graining or a coupled position/phase mechanism. It tests an application subclaim, not full RRG. The revised parent standard now treats **recursive resonator formation (`R₀→R₁→R₂`) as a core theory milestone**, alongside memory, dynamics and local adaptation. This tactical candidate implements none of that hierarchy unless a future milestone explicitly imports an accepted core resonator implementation. [P1]

**In scope:** the JS sandbox, clone/RNG correctness, its commander boundary, observation and action contracts, teacher, learner, baselines, tests, evaluation and the two existing browser consumers. Infrastructure changes needed for valid comparison may break the old sandbox API and benchmark numbers.

**Preserve because useful:** existing unit stats and action catalogue, shared low-level movement/attack routines, formations, role skills and synthetic opponents. Do not tune balance while changing controllers. Preserve the old source as a Git reference for characterization, not as a second permanent runtime.

**Out of scope:** changes to native Groups, Formation, Navigation, Motion, Sense, Action/Effect, Godot integration, new attacks, terrain, LLMs, reinforcement learning against live users, and hardware-efficiency claims. The sandbox still uses invented stats and simplified shared execution. Even its controlled observation contract is not production Sense.

### 1.1 Recursive-hierarchy isolation rule

GeoTactics R3 deliberately **does not** create parent resonators from prototype nodes, promote clusters into effective units, perform `R₀→R₁→R₂` composition, or claim whole↔parts circular causality. A cluster/prototype/subgraph inside `GeoTacticalMap` remains an implementation detail of one flat tactical memory.

If a later tactical experiment wants hierarchy, it must import an actually accepted C4–C8 mechanism from the parent standard and compare it against the flat tactical controller. Renaming GNG components, opponent groups, formations, or plan regions as “resonators” is forbidden. A successful GeoTactics result therefore supports only its registered tactical/usefulness claims.

## 2. Source audit: retain, repair or replace

These are source findings, not claims of a full runtime audit. `S2` refers to the pinned simulator and the named symbols, not shifting line numbers.

| ID | Current mechanism | Finding and consequence | Selected action |
|---|---|---|---|
| F01 | `fork()` shallow pack copy | `guards` remains the same mutable Set and its actors point into the original world. `formationPlan()` writes guard targets/goals | Deeply remap retained actors and containers; test parent/sibling immutability. The option is off by default, so this does not establish that old default win numbers were affected |
| F02 | `fork()` projectile filters | A shot/shell is copied only while its source is in active `w.units`; a released projectile can outlive its dead source | Preserve release provenance and every still-live projectile, including dead-source/dead-target cases according to original impact semantics |
| F03 | `fork()` RNG and `lure` | RNG is reseeded from time; lure is reset | Exact snapshot preserves both. Alternative rollout randomness is a named intervention, never called exact continuation |
| F04 | `fork()` nested option sharing | Nested objects and base configuration can be shared | Share only recursively immutable definitions; otherwise copy. No blanket claim that every shared object is already being mutated |
| F05 | `lookahead()` enemy `continue/rush` | Disabling `e.brain` still keeps actual `e.f`, base, targets and maneuver memory | Replace central teacher with observation-built hypotheses. Retain a privileged diagnostic only when clearly labeled |
| F06 | `lookahead()` default `oracle` | Access to real enemy policy plus a short horizon is not an optimal-policy upper bound | Rename evidence to `privileged_policy_rollout`; never call it an oracle upper bound |
| F07 | `readEnemy()/threatRead()` | A “read” mutates fast-seen, learned-fast and raid-spent state | Separate observation from policy memory update; selector input is immutable |
| F08 | `commander()` | Look-ahead bypasses ordinary 2-second dwell; `hold` also has an exception | Common decision schedule and action mask in controlled comparisons; preserve differences only in a historical diagnostic |
| F09 | `create()/commander()` | Adding `geo` as a brain is not a complete integration: pack creation and reactive-only dodge/volley/protect/lease application depend on old strings | Separate selector choice from execution profile; one plan-application owner |
| F10 | `look2.js` | Its seven-plan list omits `lure`, although the catalogue has eight | One eight-plan catalogue and eligibility mask for all controlled methods; qualify lure snapshots before inclusion |
| F11 | Legacy outcome helpers | Some scripts accept survivor advantage as a win; gauntlets require elimination | One outcome classifier with separate timeout and mutual-elimination outcomes |
| F12 | `note()` and log-parsing reports | Event display is capped; it is unsuitable for complete loss/attribution metrics | Structured metrics collected at their actual owners; keep short UI logs for display only |
| F13 | Earlier observation proposal | Role fractions and centroids omit health, readiness, delayed projectiles and own execution history | Define a typed snapshot plus explicit features, missingness and alias fixtures |
| F14 | Earlier GNG cost claim | Finding the closest prototype can scan the whole map | Meter O(Md) retrieval explicitly; bounded diffusion does not make total inference local |
| F15 | Earlier statistical protocol | Neighboring states are correlated; gauntlet opponent statistics are survival-conditioned | Episode/scenario blocks, multiple fit seeds, fresh-fight and gauntlet results reported separately |

**Evidence from this review.** The bundled source-excerpt probe reproduced container/actor aliasing, a cross-copy write, omitted dead-source projectiles, reset lure state, non-continuation RNG and nested configuration sharing. These are eight characterization observations, not eight independent game bugs or eight passed safety tests. The probe did not execute `step()` or prove a particular win-rate impact. See `GEOMIND_REVIEW_REPORT.md` and `evidence/` in the review bundle.

## 3. Target architecture and ownership

```text
World at a declared tick boundary
        ↓ read-only public-sandbox observation
Selector (rules / fixed / kNN / prototype / diffusion / rollout)
        ↓ proposal scores, reason, trace
Common legal-action mask + one plan application
        ↓ same execution profile and same PLANS catalogue
Formation/individual routines → shared combat → structured outcome
```

| State/meaning | Owner | Permitted consumers and mutation |
|---|---|---|
| World, time, combat, projectiles | Existing simulator | `step()`/lifecycle routines only |
| Simulation RNG state | Simulator RNG object, **NEW explicit state API** | Snapshot exact copy; controller RNG cannot consume it |
| Immutable unit/catalogue definitions | Simulator configuration | Read-only sharing permitted after recursive freeze |
| Public snapshot | `captureObservation`, **NEW** | Value-only, no `w`/pack callbacks or mutable aliases |
| Incumbent action and application time | `CommanderState`, **NEW** | Only common application writes these |
| Selector-specific memory | Selector instance | Explicit reset/advance calls; never combat writes |
| Prototype map/plan field | Model artifact | Fitted offline, immutable during frozen evaluation |
| Teacher copies | Teacher workspace | Disposable; cannot reach live world objects |
| Scenarios, truth, reports | Evaluation runner | Never imported by a frozen predictor |

**No production ownership claim.** At the inspected commit, the Formation document says V2 is the production executor and the V3 goal/method redesign is not yet implemented. This experiment preserves that separation as a future integration constraint; it does not announce V3 as shipped. [S5]

### 3.1 NEW contracts

```text
captureObservation(world, team, tick) -> ObservationV1
extractFeatures(observation, commander_state) -> FeatureV1
propose(observation, features, selector_memory, decision_rng) -> Proposal
legalActions(commander_state, tick) -> PlanMask
applyDecision(world, team, proposal, mask, profile) -> AppliedDecision
cloneWorldExact(world) -> IndependentWorld
buildHypothesisWorld(observation, friendly_execution, hypothesis, seed) -> IndependentWorld
scoreActions(...) -> ScoreVector + rollout diagnostics
classifyOutcome(world) -> WIN | LOSS | DRAW_TIMEOUT | MUTUAL_ELIMINATION
```

A `Proposal` contains eight finite scores or one valid plan ID, a source ID, optional `ABSTAIN`, and a bounded trace. `AppliedDecision` records both proposed and executed action, tick, rejection/retention reason and catalogue hash. Learning/evaluation must use the executed action, not a proposal the dwell gate rejected.

Invalid schemas or nonfinite model values fail the run with an explicit infrastructure/model error. Legitimate out-of-distribution inputs can return `ABSTAIN`; retain the incumbent when legal, otherwise use `hold`. Count this fallback in quality and cost. Do not silently fall back to `RULES` and attribute the rescue to geometry.

### 3.2 One action vocabulary and execution profile

Catalogue order is fixed: `hold, siege, lure, counter, intercept, hunt, push, flank`. Opaque ID tests permute IDs and all mappings together. Tie-break by the canonical catalogue order, not object enumeration or display text.

Keep `PLANS` parameter contents unchanged for this experiment. Use the same base formation and execution options for all controlled selectors: `wide line`, dodge enabled, volley disabled, protect 0, unlimited lease unless the scenario explicitly sets a shared alternative. The profile carries these values independently of selector name.

The eight-plan contract is for the experimental friendly controller and its matched baselines. Existing scripted enemies keep their own catalogues (`STORM_PLANS`, `WOLF_PLANS`, or fixed formation), profiles and selector memory through explicit environment-policy adapters. The common application API accepts a catalogue/profile ID; it must not map `rush` or `raid` to an unrelated friendly action or give every opponent our profile. Enemy policy identity remains evaluator/environment data, unavailable to the friendly learner. Equal-action claims compare friendly methods against the same opponent, not every opposing army against the same eight actions.

The old `learnedFast` override changes the meaning of `intercept`; it is not a neutral actuator. Disable that additional override in the controlled catalogue. A pure rule-policy memory can use observations to change its *choice*, but cannot privately redefine an action. Historical results with the override belong to a different named configuration.

### 3.3 Schedule and ordering

The controlled simulator uses integer tick counts with `dt=1/30`. First decision is at the first tick, then every 15 ticks (0.5 seconds). Ordinary changes require 60 ticks since the last applied change. `hold` remains an explicitly shared immediate exception on a decision tick. All methods see the same legal mask. Teacher candidates are masked identically; no proposal bypasses dwell because it came from look-ahead.

On each simulation tick: advance time/cooldowns; capture the immutable pre-decision observation for **both** teams; run due selectors; apply proposals; build both formation plans; execute the existing shuffled unit actions and combat settlement; update structured outcomes. This removes reliance on one team's policy reading the other team's freshly mutated target decisions. It is an intentional controlled-simulator change and requires a benchmark-version bump.

The original unit action/combat update order remains unchanged unless a GT0 integrity defect specifically requires repair. A parity checkpoint validates the mechanical extraction; intentional corrections are tested against their new contract, not forced to preserve a bug.

## 4. Exact snapshot and teacher fidelity

### 4.1 Clone contract

An exact clone must preserve simulation time, RNG continuation, cooldowns, all live actors, references needed by in-flight actions, pack memory, pending reservations, maneuver/lure/guard state, spawn state and outcome counters. It must own every mutable descendant.

Implement explicit snapshot records using stable actor IDs. Build the actor registry from active actors **and** retained projectile/target/provenance references. Reconstruct references in a second pass. Preserve dead-source provenance until the last dependent action retires. Remap Sets, Maps and nested maneuver memberships. Rebuild derived callbacks so none captures the original world. Share only frozen definitions. Do not JSON-round-trip a graph containing Maps, Sets, functions or `Infinity` and assume it is exact.

RNG exposes `getState()/fromState()` (or equivalent constructor) rather than an inaccessible closure. Clone the current state for exact continuation. Teacher stochastic replicates may deliberately replace the rollout RNG afterwards and record that replacement. No call to the teacher can advance live RNG.

**Snapshot checks:** original and clone continue identically under identical supplied decisions; mutate each child container without changing parent/sibling; reversing candidate rollout order changes neither score vector nor original state; compare hashes of complete canonical mutable state before/after teacher calls. Include guards on, active lure, a shell from a dead shooter, a homing shot after target death, spawn queues, pending fire and current maneuver phase. Exactness is structural and behavioral, not equal final survivor totals alone.

### 4.2 Observation-built hypotheses, not renamed omniscience

Use the central teacher only with `ObservationV1` plus friendly execution state legitimately available to its own controller. Enemy `brain`, `f`, base preset, target assignments, plan, hidden flank/lure memory and enemy RNG are forbidden inputs.

`continue` means a **declared visible-motion continuation model**, not copying the enemy's current formation configuration: project observed motion toward a short-lived goal, continue shared attacks with generic nearest eligible targets, then use the same generic individual controller. `rush` uses shared individual movement and attacks toward visible eligible opponents. Both are data-defined assumptions built from allowed observations. They are not claims about the enemy's actual decision process. The models must also work when the actual enemy had no pack object.

Public-sandbox observations expose physical actors, health, cooldowns and in-flight threats for this first measurement; this is a deliberately generous toy observation contract. Enemy tactical program state remains hidden. Existing shared formation/individual routines contain handcrafted tactical behavior; the experiment measures selection *on top of them*, not emergence of all tactics from geometry. This limitation must remain in every result summary.

A separate privileged diagnostic can retain the actual enemy policy. Label it `privileged_policy_rollout`. Do not train the main model from it, mix its results into the main comparison, or describe it as an upper bound.

### 4.3 Teacher score and bounded work

Initial settings are explicit pilot choices: eight actions, two hypotheses, two rollout RNG replicates, six-second horizon, real `dt=1/30`. On each permitted decision state, evaluate each **legal** candidate as a macro-action held through that horizon. The branch uses the same formation execution and incoming delayed actions. End on terminal combat or horizon. An incumbent-only state can skip scoring alternatives and records why.

For a candidate, compute each hypothesis's mean across the two RNG replicates, then take the minimum:

```text
branch_score = (enemy HP lost - 1.5 * own HP lost) / (initial own HP + initial enemy HP)
teacher_score[a] = min_hypothesis mean_replicate(branch_score[a])
```

Use HP snapshots at the start of each branch; the denominator comes from the paired encounter's initial armies and is constant across its branches. Raw scores and absolute HP losses are retained. This is short-horizon damage-trade supervision, not proof of long-horizon optimality. Closed-loop gauntlet outcomes remain the primary product measurement.

Use the same replicate seeds across actions for paired noise reduction; do not claim all later random events remain matched after trajectories diverge. Record all branch seeds and work counts. Runtime deadline uses a deterministic step/branch budget, not a wall-clock-dependent action that destroys reproducibility.

Before fitting, evaluate horizon sensitivity at 3/6/12 seconds on a small training-only diagnostic subset. Keep six seconds unless a versioned, pre-test change is justified. Do not use coarse `dt=0.1` in the initial teacher: fixed per-tick coefficients and collisions can change the modeled dynamics. A cheaper integrator becomes a separate convergence-qualified approximation later.

## 5. Observation and feature contract

### 5.1 ObservationV1 — exact permissions

Value-only records include arena dimensions, tick, actor IDs/team/role, position, radius, velocity, HP/maxHP and cooldown/cooldown maximum; all are exposed by this toy experiment. In-flight shots/shells include their mock-observable physical state, flight/landing information and release team. Friendly commander/formation execution memory is available to all selectors. Public impact totals from the preceding three seconds are available.

Do **not** include enemy preset/selector name, hidden action selection targets, enemy method memory, spawn RNG, ground-truth future outcomes, teacher winner or test metadata. Projectile homing/landing data is an explicit toy observable, not permission to access the enemy's tactical target pointer. Episode IDs, opponent labels and seeds are evaluator metadata and cannot enter feature construction.

Production integration would have to replace this observation with lawful Sense/physical-evidence projections. Hiding names alone is not enough to claim an honest game AI.

### 5.2 FeatureV1 — a specified first compression, not guaranteed sufficient

Reference frame: origin at our pack anchor; forward axis is its normalized heading, lateral axis its perpendicular. A side without a pack uses its living-actor centroid and the unit vector toward the opposing centroid; coincident/absent opponent centroids use the declared initial team-facing direction. An empty own team returns an explicit terminal/empty observation and is not asked to choose a plan. These fallbacks belong to observation construction and are identical for all selectors. `R=ROLE.ranged.range` and `V=max configured unit speed` are fixed by the scenario catalogue, not fitted per sample. Project positions/velocities into that frame. All arrays have stable role/field order.

For each of three roles on each team, include these nine fields:

1. living count / 50;
2. total positive HP / (50 × role maximum HP);
3. mean HP / role maximum HP;
4. centroid forward / R;
5. centroid lateral / R;
6. mean forward velocity / V;
7. mean lateral velocity / V;
8. root-mean-square distance from that centroid / R;
9. ready fraction (`cooldown <= 0`).

Add a presence bit per role group. Features 3–9 are missing when the group is empty, not “zero means at the anchor.” These fields distinguish absolute strength from composition. Configurations above 50 units per team require a new declared normalization/schema arm; do not silently clip all larger armies to the same state.

Additional scalar groups:

- For hostile melee → friendly ranged and hostile melee → friendly artillery: minimum and median nearest surface gap / R, and relative closing velocity / V for the minimum pair; missing when either role is absent. Nearest ties use stable IDs only.
- Four ray distances from our anchor to the arena rectangle along forward/back/left/right, divided by R; compute exact ray intersections, not global-X clearance masquerading as a heading-relative feature.
- Per team: number of in-flight direct shots / 50, number of shells / 50. For hostile shells, minimum remaining landing time / 3 seconds and minimum signed splash clearance to any friendly soft actor / R, with an explicit missing bit when no such shell/actor exists.
- Public damage dealt and taken in the preceding three seconds, each divided by the encounter's initial total HP.
- Incumbent plan one-hot, time since application capped at two seconds / 2, current friendly formation error (maximum slot distance / R), formed flag, and friendly flank/lure phase as one-hot values with `none`. These are lawful self-state, not enemy leakage.

The bit/one-hot blocks and continuous blocks are separately specified in a schema table emitted by `extractFeatures`. Record ordered names and a schema hash; tests derive the expected dimension from that table rather than duplicating a magic number.

**Metric.** For each continuous feature, fit its mean and scale `max(training_std, 0.1)` using observed training values only. Clip standardized observed values to `[-5,5]` and count clipping. Encode a field as `(m*z, m)`, where `m` is 1 for observed and 0 for missing. Missing is therefore distinct from an observed standardized zero. A feature never observed in training uses mean 0/scale 1 and remains visibly marked in the artifact. Append the fixed bit/one-hot blocks.

Use squared Euclidean distance on this complete encoded vector. Each semantic block is multiplied by `1/sqrt(block_dimension)` so its squared-distance contribution is a mean rather than growing automatically with its length; all block weights are 1 in the initial schema. The schema freezes the exact block partition. Do not use pairwise deletion or an arbitrary constant mismatch penalty: those can violate metric properties. A nearest-neighbor baseline receives exactly the same embedding. This hand-selected geometry is not claimed to be optimal.

Prototypes are points in that complete encoded space. Move all encoded coordinates toward the encoded sample. Mask coordinates can become fractional prototypes of observation availability; they are not decoded as new factual observations. Only input snapshots carry factual validity. The full vector and its schema, not a reconstructed physical actor, determine distance.

### 5.3 Alias and symmetry checks

Required fixtures distinguish identical role fractions with different total health; identical centroids with a dangerous split flank; an incoming shell about to land versus none; identical physical positions with different friendly action phase; no artillery versus artillery at the origin; and a singleton survivor. Check finite output and stable identity permutation. Reflect world geometry, velocities, heading, boundaries and signed lateral fields together; compare expected transformed features. Do not demand unchanged signed coordinates under an inconsistent frame transformation.

Centroid compression still cannot preserve every tactical distinction. Store the original permitted snapshot for evaluator diagnosis. If highly similar feature vectors have sharply different qualified teacher scores, report representation aliasing. A failed compressed-observation model does not by itself falsify the geometry hypothesis. Reworking features after final-test inspection requires a new experiment/test set.

## 6. Candidate algorithms and matched baselines

Start with simple models, not a giant self-organizing framework. All frozen predictors implement the same `propose()` contract and see the same action mask through the application owner.

| Model | Role in the comparison |
|---|---|
| `constant_plan` | One friendly plan under the shared `wide line` execution profile; choose the best constant on validation, then freeze it |
| `public_rules_v1` | Existing ordered-rule logic rebuilt from permitted observations and explicit own policy memory; no enemy private-target reads |
| `uniform_legal` | Uniform random legal proposal, independent decision RNG |
| `knn` | Raw training samples, the same feature transform and teacher score vectors |
| `prototype` | The same learned prototypes and local values, nearest-prototype readout, no graph diffusion |
| `fixed_graph_diffusion` | Same prototypes/values but a geometric k-nearest-prototype graph rather than learned adjacency |
| `adaptive_graph_diffusion` | Experimental GNG-derived adjacency and bounded diffusion |
| `public_rollout` | Qualified runtime teacher, same action/mask/schedule, expensive comparison |

For `public_rules_v1`, replace the private `pinned(enemy)` check with the explicit public estimate `some friendly melee has surface gap < 24 to that enemy`; this is an estimate, not truth about the enemy's current target. Other scalar reductions retain the source formulas where their input fields are permitted. Update `fastSeen`/`raidSpent` only in the policy's own memory from friendly execution facts. `learnedFast` remains disabled in the controlled action contract. Version this baseline because its observation semantics intentionally differ from the old one.

Historical `alone`, fixed formations and original reactive/look-ahead results remain characterization evidence at their original source/configuration. They are not mixed into the controlled benchmark. Reusing a historical source for a test is not a second production executor.

### 6.1 Topology learner — defined GNG-style variant

Use Float64 and a maximum of 256 prototype nodes for the primary pilot. Two distinct training samples initialize the map (a constant-data fixture has one prototype and no insertion). Nearest and second-nearest search is an exact full scan with stable node-ID tie-breaks. Node IDs are monotonic and not array positions. [R1]

For each observation-only training sample:

```text
find nearest s1 and second-nearest s2
increment age of edges incident to s1
error[s1] += metric(sample, s1)
move s1 toward the complete encoded sample: εw = 0.05
move s1's existing neighbors toward sample: εn = 0.005
create/reset undirected (s1,s2), age = 0
remove edges older than 50 samples of their incident winner's aging
remove isolated nodes, but retain at least two when distinct data exists
on every 100th sample, if below cap and an edge exists:
    choose max-error q; choose its max-error neighbor f
    insert midpoint r; replace edge(q,f) with (q,r),(r,f)
    halve error[q], error[f]; error[r] = error[q]
decay all retained errors by 0.995
```

Insertion uses the ordinary midpoint in encoded space. Select q only among nodes with at least one edge; if none exists, skip insertion and record it. `metric` already returns squared normalized distance; do not square it a second time when accumulating error. This is a documented finite-cap/encoded-input variant of GNG, not an exact reproduction. Global winner search, insertion search and error decay are explicitly counted. Edges can be O(M²) at the finite cap; report actual edges/bytes and do not promise bounded-degree scaling.

Fit geometry on observations only for five passes of the training set, with the pass shuffle derived from the recorded fit seed and a single continuing insertion/age clock. Count all five passes. Freeze it before attaching any plan scores. In a second pass assign each training sample's complete score vector to its nearest prototype, accumulating per-action sums/counts. A state with only one legal action provides a score for that action only; missing action labels remain missing, never zero. Store `count` and mean separately per action.

No query updates the prototypes or fields in frozen evaluation. Refit or changed schema requires a new artifact. Do not move a prototype after labeling it without rebuilding or explicitly transporting its statistics.

### 6.2 Bounded diffusion readout — do not call it unexplained resonance

Find the closest two nodes (full scan charged). For each query build a local induced subgraph: breadth-first expansion, neighbors visited in increasing edge distance then stable ID, maximum 32 nodes and maximum four hops. Include only nodes in that discovered set; record truncated boundary edges. Runtime topology is this induced graph, not an invisible full-graph solver.

For each retained edge, use conductance `w_ij = exp(-metric(i,j)/(2 σ²))`, with `σ=1` initially. Row-normalize to transition probabilities; isolated nodes get a self-loop. Seed probability `p0` on the two closest nodes proportional to `exp(-metric(query,node)/(2σ²))`; normalize robustly by subtracting the largest log weight. Perform exactly four updates:

`p_(t+1) = 0.2 p0 + 0.8 P^T p_t`.

For each action average local prototype values with weights `p_i * n_i,a/(n_i,a+4)`. Ignore unsupported action-node pairs and renormalize; no support means `UNSUPPORTED`, not an artificially favorable zero. Select among supported legal actions; application owns all dwell/inertia. No second stickiness term is inserted into the model.

This is finite diffusion with restart. Four steps do not demonstrate attractor convergence or recurrent intelligence. The `prototype` baseline uses only the nearest node's supported means. The fixed-graph baseline uses the union of each prototype's four nearest neighbors, same conductances, same budget and values. Raw kNN uses weighted averaging of k in `[1,4,16]`, selected on validation; it uses the same support and missing-value rules.

### 6.3 Out-of-distribution handling and artifact schema

Let `novelty` be the nearest-prototype squared distance. After fitting and value attachment, set an abstention threshold to `max(1e-9, q99)` of training-sample distances to their nearest supported prototype; compute and charge this scan. This is an in-sample heuristic and may be optimistic, not a calibrated probability of novelty. Inspect coverage on validation without silently changing the definition; any new threshold rule is registered before the final test. Freeze the threshold. Sparse support can still abstain even inside that distance. Report fallback frequency by scenario family and compare models both including fallbacks and on shared covered cases. A model that abstains everywhere has not solved tactics.

Artifact fields: schema/algorithm/catalogue/feature hashes, source version, training manifest, normalization, prototype IDs/positions/validity/counts, edges/ages, plan sums/counts, all fitting settings, freeze flag and checksum. JSON uses `null` for an explicitly named disabled bound where needed, never serialized `Infinity` silently becoming a different meaning. Canonical serialization sorts IDs/edges; load rejects incompatible dimensions, unknown actions, dangling edges and invalid numeric state at the owning boundary. These are artifact-contract checks, not a new repository-wide validation framework.

The portable predictor imports no simulator, filesystem, browser, teacher or global RNG. Node wrappers own loading. A separate tiny consumer imports the same core artifact/predictor and exercises prediction, missing data, invalid load, reset and disposal. Browser consumers load the artifact through that same predictor; no parallel browser inference algorithm.

## 7. Data collection, split and experiment budget

### 7.1 Split independent scenarios before collecting states

Initial seed namespaces remain TRAIN 101–300, VALIDATION 301–400, TEST 1001–1200, but **a seed number alone is not a split guarantee**. A scenario ID hashes scenario-generator version, source/configuration, opponent schedule, army composition, seed and reset protocol. The complete scenario manifest is immutable before collection.

Training opponents are exactly `alone, line, wide line, wedge hold, line anvil, box, screen, crescent, loose`; do not collect from the ambient full `POOL`. Validation uses this same opponent list with distinct scenario instances. `storm`, `wolfpack`, `loose skirmish`, and `swarm` are held out from fitting, but already known to developers from this project; label them **withheld-from-fit families**, not unknown discoveries. Add composition/initial-position perturbations through data, not opponent-name code branches. Mirror comparisons hold the same initial capabilities on both teams.

Split by whole encounter and whole gauntlet. All snapshots from one episode, all variants derived from that episode and their teacher branches stay in one partition. Do not split consecutive frames randomly. Validation chooses settings; it does not join the final fit. Test labels may be computed by an isolated evaluator after predictions for diagnostic regret, but cannot enter fitting or runtime decisions.

### 7.2 Training coverage and covariate shift

Collect states from a predeclared mixture of public rules, fixed plans and uniform legal decisions, not the teacher alone. Sample at most one state per two simulation seconds and 32 states per encounter, stratified across early/middle/late phases. Keep selection independent of the teacher's eventual favorite action.

Use development fit seed 0 to construct the shared dataset. Fit an initial model, then permit two further collection rounds where it acts on **training scenarios only**. Label those newly visited states with the same qualified teacher and refit from the combined training collection. After those rounds, freeze one shared dataset; the five qualification fits vary initialization/sample order on that same data and do not each launch an additional collection budget. This is a bounded data-aggregation approach motivated by sequential imitation distribution shift, not a license to collect from the final test. [R7]

### 7.3 Work levels

**Integrity level:** deterministic handcrafted fixtures and a small set of simulation seeds. No broad win-rate claims.

**Development pilot:** first collect 100 labeled training snapshots to expose teacher/schema defects, then at most 1,000 training and 200 validation snapshots; two data-aggregation rounds stay inside that total. Hard maximum 32 branches × 180 steps per fully eligible snapshot at the initial teacher settings. Record skipped incumbent-only branches and terminal truncation. Use a smoke pilot below this cap before committing to the full dataset; its results are development evidence.

**Qualification:** five independent fitting/sample-order seeds, one selected configuration, 200 test scenario seeds for the inexpensive models and controls. The primary gauntlet draws ten opponents with replacement (`DRAW=any`) from the exact pool serialized in the manifest; all methods use the same schedule. Run deterministic non-learning baselines once per scenario, not needlessly once per fit seed.

Expensive runtime rollout uses a preselected subset of 20 of those gauntlets, selected by scenario-hash order before outcomes are known. The quality-versus-rollout claim applies only to that paired subset; report its smaller statistical support explicitly. Register a 24-million-forward-step total cap for that rollout panel. On cap exhaustion, preserve partial receipts and mark the rollout-quality gate INCONCLUSIVE; do not choose a favorable completed subset, alter dt, or silently shrink horizons. The inexpensive-model comparison and mechanism verdict can still complete.

Fresh-fight family/composition panels are separate declared diagnostic arms. Dataset growth or a larger prototype cap is a new version, not an unrecorded retry.

These are proposed CPU experiment budgets, not estimates of completion time or measurements already obtained. If available resources prevent the declared qualification, report the reached level and do not substitute a five-seed pilot for acceptance.

## 8. Evaluation and causal tests

### 8.1 Outcomes and gauntlet semantics

`WIN`: enemy eliminated and at least one friendly actor alive. `LOSS`: reverse. `MUTUAL_ELIMINATION`: both eliminated. `DRAW_TIMEOUT`: both survive when time expires. A larger surviving army at timeout is diagnostic, not a win.

Gauntlets preserve each friendly survivor's role and exact positive HP into the next fight; other actor/pack/cooldown state resets by the existing gauntlet rule. Document that reset explicitly. Frozen model parameters persist unchanged; episode-local query/controller memory resets. Every enemy is fresh. Timeouts and mutual elimination stop the streak without adding a win.

Keep the owner's goals of at least 4, 6 and 8 wins as named product targets on a **specified finite suite**. Report the observed minimum and the fraction below each threshold. A finite suite cannot establish a universal guarantee over all random gauntlets.

Per-opponent win/loss in a gauntlet is conditioned on reaching that opponent with previous losses. Use fresh matched fights to compare opponent difficulty or policy strength; do not treat survival-biased gauntlet rows as unconditional statistics.

### 8.2 Primary and secondary metrics

Primary product outcome: mean gauntlet wins out of ten, paired by scenario seed. Tail outcomes: minimum, 10th percentile and fraction below four. Secondary: fresh-fight wins/draws, remaining role HP, unit losses, damage, churn, invalid proposals, abstention/fallback frequency and action dwell.

Teacher agreement is diagnostic. Report action-score regret only where the teacher produced comparable supported labels; do not call noisy or near-tied winner disagreements tactical failures. Raw HP scores and true episode outcomes expose short-horizon reward mistakes.

Cost: observation capture, features, normalization, nearest search, graph discovery, diffusion, application, allocation/GC, model loading, total decision time, total fight time, branch/step counts, nodes/edges examined and bytes. Include p50/p95/p99 after a declared warmup and runtime/hardware/version information. Interleave benchmark methods or counterbalance order. No rendering in headless timing. All methods use the same precision and environment.

Offline teacher/fitting/validation cost is reported separately and included in an amortization calculation. `world_forks=0` for a predictor is necessary for its claim, but says nothing by itself about speed or useful correctness.

### 8.3 Registered decision rules

The following are **proposed practical margins**, not scientific constants or observed results. Freeze them with the experiment before viewing test results.

- **Integrity:** zero isolation, information-boundary, illegal-action or unexplained nondeterminism failures. Any violation invalidates the affected experiment regardless of wins.
- **Useful fast controller on the preselected rollout panel:** lower bound of the paired 95% interval for Geo minus qualified runtime rollout is above −0.5 gauntlet wins, and measured median end-to-end decision time is at most one tenth of rollout. This is a product target, not a promised outcome.
- **Reason to keep adaptive dynamics:** compare with both raw kNN and the same-prototype readout. Either the paired lower 95% bound exceeds +0.25 gauntlet wins without more than 2× decision time, or quality is noninferior within −0.25 and decision time or persistent bytes improve by at least 20%. Report the two comparisons separately; one weak comparator is insufficient.
- **Reason to keep learned topology:** compare adaptive and fixed-graph diffusion under the same rules above. If there is no useful difference, keep the simpler fixed graph or no graph. Do not call that failure of all geometry.
- **Fallback guardrail:** report model-covered decisions and outcomes; a claimed useful controller must cover at least 90% of decisions in the in-distribution test panel. Withheld-family coverage is reported separately and may block a broad claim.

Choose the reference configuration on validation. Do not choose whichever baseline looks weakest on the test set. An interval crossing the meaningful margin is `INCONCLUSIVE`, not an automatic pass. A result can fail the product target while still revealing a correct local mechanism.

For uncertainty, keep episode/scenario pairing and the crossed training-seed dimension. Report per-fit-seed differences and a two-way resampling analysis over fitting seed and scenario seed (the same resampled indices for both compared methods); list its assumptions. Do not resample individual frames as independent observations. With only five trained maps, uncertainty about training variability remains limited; state that limitation. [R8]

### 8.4 Mandatory controlled variants

| Variant | What it tests | Required interpretation |
|---|---|---|
| Consistent opaque IDs | Hidden dependence on names/order | Same decisions after reversing the permutation |
| Consistent frame reflection | Geometric equivariance | Expected transformed features and equivalent behavior in a correspondingly reflected simulator |
| Coordinate–value association shuffle | Dependence on learned metric indexing | A drop alone does not establish special dynamics; kNN also depends on indexing |
| Degree-aware edge rewiring | Contribution of the learned adjacency | Preserve node values/positions and report degree/connectivity changes; unmatched rewiring is not a clean test |
| No diffusion, same prototypes | Incremental propagation value | Equal quality/cost means no reason yet to keep propagation |
| Fixed geometric graph | Adaptive topology versus ordinary smoothing | Controls the strongest obvious explanation |
| Randomized score association | Use of supervision | Negative control, not evidence for resonance |
| Frozen artifact reset each fight | Frozen-evaluation state integrity | Results must be unchanged, not collapse |
| Measured targeted edge/node intervention | Predicted mechanistic consequence | Predictions stated before intervention; verify locality of effects, not just global score deterioration |

No online-learning persistence ablation appears in this frozen experiment. It belongs to a future adaptive protocol. Run at least three fixed ablation random seeds on the declared diagnostic subset; do not cherry-pick the most damaging shuffle.

## 9. Concrete change map and consumer migration

All paths below are under `experiments/formation_sandbox/`. Proposed files are **NEW** and may be combined only when ownership stays clear; central algorithms and contracts cannot be omitted.

| Existing file/symbol | Change / destination | Consumers and retirement | Milestone |
|---|---|---|---|
| `formation_sim.js::rng/fork/create/step` | Explicit RNG/snapshot owner; exact clone; buffered decision boundary | All look-ahead callers, snapshot fixtures; retire shallow fork implementation | GT0 |
| `formation_sim.js::commander/readEnemy/threatRead` | Extract common application and pure selector interface; explicit policy-memory update | Existing reactive and opponent policies; remove hidden mutation from observation | GT0–GT1 |
| `formation_sim.js::create` brain-string branches | Selector and execution profile become separate options | Headless scripts and both HTML viewers; no duplicated `geo` combat pipeline | GT1 |
| `formation_sim.js::lookahead` and `look2.js` | `geo_teacher.js`: observation-built hypotheses and shared scorer | Scripts use one catalogue/mask; remove old “honest” shortcut from main experiment | GT2 |
| `compare.js/shapes.js/reactive.js/fresh.js/gauntlet.js/trace_gauntlet.js/audit.js` | Use one `classifyOutcome` and structured metrics; record benchmark version | Stop silently mixing timeout advantage and strict wins; stop loss accounting from truncated UI logs | GT0–GT1 |
| `gauntlet.js/gauntlet.html` | One opponent schedule helper and carry/reset contract | Replace comparator-based random sort with deterministic Fisher–Yates where shuffle is requested; version intentional change | GT1 |
| **NEW** `geo_observation.js` | Snapshot-to-feature schema, masks, transform | All statistical predictors receive identical representation | GT1 |
| **NEW** `geo_tactics.js` | GNG variant, frozen artifact, bounded readouts and simple baselines | One core for Node and browser, no simulator import | GT3 |
| **NEW** `geo_collect.js/geo_train.js/geo_eval.js` | Collection, fitting/selection, frozen evaluation | Fixed manifests and JSON receipts; no alternative runtime scorer | GT2–GT5 |
| **NEW** `geo_contract.test.cjs/geo_teacher.test.cjs/geo_model.test.cjs` | Named focused contract suites | No repository-wide gate, fleet or new hook machinery | Owning milestone |
| `formation_sandbox.html/gauntlet.html` | Shared options, predictor loading, decision/coverage/cost display | No browser-only logic; display synthetic benchmark status | GT1/GT5 |
| `README.md`, this installed plan, `evidence/geotactics_r3/` | Update meanings, commands, status, findings | Preserve historical receipts as historical; no second tracker | All |

The old commit can be materialized as a temporary reference **during tests**, without checkout/reset. Remove any runtime compatibility wrapper by GT1. Old baseline policies are permitted as intentionally isolated research comparators, not competing owners of movement or live state.

## 10. Complete implementation milestones

### GT0 — trusted world and decision boundary

**Why/result:** teacher experimentation cannot mutate live combat or discard existing incoming actions. One snapshot and one decision/apply boundary exist before a model is added.

**Requires:** current relevant source and root instructions. Preserve newer unrelated HEAD changes.

**Implement in order:**

- [ ] Record inspected current sandbox source/configuration and the exact historical reference hashes.
- [ ] Extract observation/policy/application without changing the original behavior for a mechanical-refactor fixture. Prepare the reference comparison to run in the final verification phase, not after every edit.
- [ ] Implement explicit RNG state and exact snapshot/remap; replace shallow fork. Add active/dead provenance retention, container isolation, lure/maneuver state and derived-callback reconstruction.
- [ ] Implement the controlled buffered decision order, shared application receipt and structured outcome classifier. Increment simulator benchmark version for intentional corrections.
- [ ] Add complete contract fixtures and move relevant source callers to the surviving API. Update README and this status section before validation.

**Verify:** `node --test geo_contract.test.cjs` (**NEW**, created in this batch). It compares the extraction checkpoint to historical code on declared small seeds and independently tests intended corrections on final code. Test parent/sibling identity, exact RNG continuation, candidate order, pending actions, both teams' observation time and all outcome classes. No gauntlet tuning.

**Done when:** final code has one owner per mutated state and all exactness/ordering fixtures pass. A historical parity mismatch is either corrected or tied to one documented intended change with a specific replacement assertion. No unknown difference is waved away as “new version.”

**Review focus:** shallow aliases, callbacks into original state, released projectile lifetime, two-stage mutation, and a parity test comparing two copies of the same new code.

### GT1 — equal observations, legal actions and migrated consumers

**Why/result:** controllers receive comparable information and cannot gain different skills by choosing a different name.

**Requires:** GT0 accepted.

**Implement in order:**

- [ ] Implement ObservationV1/FeatureV1 exactly, including health/readiness/history/missingness and pure extraction.
- [ ] Introduce the selector/profile split, common schedule/mask/dwell, stable catalogue and applied-action receipt.
- [ ] Port ordered rules to the permitted snapshot and explicit own memory; disable private plan-content overrides in controlled runs.
- [ ] Add fixed/uniform controls; migrate listed headless and browser callers, shared gauntlet schedule, resets and outcome accounting. Remove compatibility mutation paths.
- [ ] Write alias, symmetry, singleton/empty-role, invalid-model, profile-equality and legal-action tests; make browser controls use the new schema even before learned model support.

**Verify:** affected `geo_contract.test.cjs` and `geo_model.test.cjs` checks; explicitly test identical proposed plan sequences yield identical combat state regardless of selector label. Verify changing metadata/opponent names cannot alter features. Execute a short seeded controlled fight and a carry-over fixture, not a broad performance benchmark.

**Done when:** the documented contract reaches every caller, no selector sees live pointers, features have named schema and uncertainty/missingness semantics, and controlled execution profile is identical.

**Review focus:** hidden enemy-state access through helpers, mutable “read” methods, information omitted as “geometry only,” and action gates different for rollout.

### GT2 — qualified teacher and bounded collection

**Why/result:** training labels come from a reproducible declared approximation, not privileged or defective copies.

**Requires:** GT0–GT1 accepted.

**Implement in order:**

- [ ] Build both public hypotheses from permitted snapshots; construct generic enemy policy memory rather than retaining actual enemy `f`/targets/brain.
- [ ] Implement masked macro-action score vectors, same physics step, branch isolation, shared replicate seeds and explicit branch/step counters.
- [ ] Add the separately named privileged diagnostic without allowing it into main training.
- [ ] Implement immutable scenario manifests, source-policy mixture, episode-level splitting and sampled-state caps.
- [ ] Add teacher determinism, hidden-state counterfactual, incoming-projectile, `alone` enemy and all-eight-action fixtures. Record horizon sensitivity on a training-only subset.

**Verify:** `node --test geo_teacher.test.cjs` plus affected contract checks. Two worlds differing only in forbidden enemy metadata but with identical public snapshots/friendly execution must give identical public-teacher inputs and scores for identical hypothesis seeds. Hash the original before/after every candidate sequence. Verify metric sign using hand-computed damage branches.

**Done when:** teacher qualification passes and one small training collection replays exactly. This does not certify that short-horizon choices are tactically best.

**Review focus:** reconstruction accidentally copying enemy state, mislabeled “oracle,” teacher action versus executed action, stochastic order effects, and coarse-step shortcuts.

### GT3 — portable candidate and mandatory simple baselines

**Why/result:** a deterministic geometric estimator exists with controlled alternatives before expensive training is scaled.

**Requires:** GT1 accepted; synthetic score fixtures permit work before GT2's full collection exists.

**Implement in order:**

- [ ] Implement metric/masks and artifact schema, exact nearest search and all counters.
- [ ] Implement the specified bounded GNG variant; freeze geometry, then attach supported per-action means/counts.
- [ ] Implement nearest prototype, raw kNN, fixed-graph and adaptive-graph diffusion with the same supervised data and action/missingness contract.
- [ ] Implement abstention, immutable load/query, consistent permutations and synthetic known-score fixtures.
- [ ] Create a separate consumer importing the actual predictor and artifact; no copied algorithm or simulator dependency.

**Verify:** `node --test geo_model.test.cjs`. Compare the four-step diffusion to an independent tiny dense transition-matrix calculation used only as a test oracle. Test row normalization/probability mass, no-neighbor self-loop, isolated/missing data, cap reached, value-field attachment after freeze, unsupported actions, save/load equivalence and query immutability.

**Done when:** all readouts match their references, the portable consumer executes the same implementation, and complete retrieval/diffusion cost is visible. No learned-quality claim is needed here.

**Review focus:** missing scores treated as zero, prototype values becoming stale after movement, hidden full-graph passes and artificial novelty claims.

### GT4 — collect, fit, select and freeze without test contamination

**Why/result:** model artifact and experiment design are fixed before qualification.

**Requires:** GT2–GT3 accepted.

**Implement/run in order:**

- [ ] Finalize the manifest and proposed margins using training/validation only; register any departures from pilot settings.
- [ ] Collect the declared mixture and up to two learner-state aggregation rounds, all inside the training partition and total cap.
- [ ] Fit normalization/topology/score fields and simple baselines. Select k/allowed settings/checkpoint on validation using the declared primary metric, not a cherry-picked screenshot.
- [ ] Produce five fit-seed artifacts, configuration/checksum manifest, cost records, and a frozen predictor package with no teacher import/call path.
- [ ] Retain every failed fit and capacity/convergence result; verify training and test scenario hashes do not intersect.

**Verify:** affected artifact/data tests and a training-replay receipt; do not run final test as a “smoke check.” No normalization or OOD threshold fit on validation/test snapshots. Model-query hashes are stable before/after a frozen episode.

**Done when:** final settings and artifacts are immutable, teacher fitting/validation cost is recorded, all baseline artifacts exist, and the test manifest remains unused.

**Review focus:** repeated validation becoming undisclosed search, learner-state contamination, test metadata in features and missing support in rare actions.

### GT5 — closed-loop evidence and decision

**Why/result:** determine whether the added mechanism is worth keeping and what it does/does not say about the theory.

**Requires:** GT4 accepted.

**Implement/run in order:**

- [ ] Run the frozen methods on paired test gauntlets, fresh-fight panels and declared controlled variants. Keep full per-episode data.
- [ ] Measure complete runtime and amortized cost, fit variability, uncertainty, coverage, tails, action legality and benchmark-version consistency.
- [ ] Load the accepted candidate in both browser views through the same predictor; show proposed/executed plan, finite trace, model version and fallback status. Browser visuals do not replace headless evidence.
- [ ] Apply the registered decision rules; remove unused experimental runtime wiring when a candidate is rejected, while preserving reproducible algorithms/receipts as named research artifacts.
- [ ] Update this plan and README with one verdict, exact limitations and next action. Do not begin a native cutover or online-learning experiment automatically.

**Verify:** final targeted model/contract checks only if affected by integration, the registered evaluation commands, and browser consumer smoke behavior. Record commands actually executed, environment, source and artifact checksums. Broken browser qualification is a host-integration blocker, not permission to conceal it behind core tests.

**Done when:** independent review can reproduce results and distinguish correctness, usefulness, efficiency and theory support. `KEEP_KNN`, `KEEP_PROTOTYPE`, `KEEP_FIXED_GRAPH`, `KEEP_ADAPTIVE_GRAPH`, `REWORK_OBSERVATION`, `REWORK_TEACHER`, `INCONCLUSIVE` and `STOP_BRANCH` are all valid decisions.

**Review focus:** survival bias, correlated samples, hidden fallbacks, selective seed reporting, total-cost exclusions, and rhetorical promotion of a classifier into full RRG.

## 11. Operating commands and handoffs

Commands below are **planned interfaces**, not commands already available or executed. Implement their argument contracts in the owning milestone and show exact actual commands in the receipt.

```bash
# From experiments/formation_sandbox; scoped checks after the complete batch.
node --test geo_contract.test.cjs
node --test geo_teacher.test.cjs
node --test geo_model.test.cjs

node geo_collect.js --manifest evidence/geotactics_r3/manifest.json --split train
node geo_train.js --manifest evidence/geotactics_r3/manifest.json
node geo_eval.js --manifest evidence/geotactics_r3/manifest.json --split test
```

The manifest names output locations, exact source/model hashes, model list and budgets. `--split test` refuses fitting/update mode. Wrappers cannot override locked test settings implicitly through environment variables.

**Implementation prompt:**

> Read this R2 plan and the current root/owning instructions. Resume the complete current milestone, starting with GT0 while it is not accepted. Inspect newer relevant source but preserve unrelated edits. Implement all in-scope code, callers, schemas, fixtures and documentation as one connected batch; then run only the affected named checks. Do not train a model before the snapshot, observation and teacher gates. Record actual checks and exact NOT_RUN/blockers. Stop at REVIEW_READY; no native game changes, extra trackers, resets, worktrees or push.

**Independent review prompt:**

> Review the actual milestone diff, all callers and evidence, not its completion summary. Check its specific review risks and the global information/ownership/cost contracts. Make necessary in-scope repairs as a batch before affected retests. Accept implementation only when the reached checks justify it; assign the hypothesis verdict separately. Preserve unrelated work. Update this same plan and advance only to the already specified next milestone.

## 12. Evidence schema and final acceptance

Every run writes one structured JSON result and a short Markdown summary in `evidence/geotactics_r3/`. The summary is a receipt, not a second execution plan.

```text
experiment and benchmark version; source commit and per-file hashes
runtime/hardware; exact command; split/scenario manifest hashes
observability and action/profile/catalogue schema hashes
controller/model/normalization hashes; fit and evaluation RNG seeds
teacher hypotheses/horizon/dt/replicates/budget; dataset counts
per-scenario outcomes and all fit seeds; mean/tail/coverage/uncertainty
proposed versus applied actions; legality and isolation failures
retrieval, diffusion, teacher, training, load and total runtime costs
bytes/allocations/fallbacks; ablations and intervention predictions
checks: PASS / ASSERTION_FAILURE / INFRASTRUCTURE_FAILURE / NOT_RUN
implementation status; hypothesis verdict; limits; next action
```

| Gate | Cannot be substituted by |
|---|---|
| Snapshot isolation and correct lifecycle | A good win rate |
| Equal observation/action contract | Equal army statistics alone |
| Useful controller quality and cost | Teacher-label accuracy |
| Adaptive topology/dynamics contribution | Failure after arbitrary label shuffling |
| Persistence/locality | Loading a fixed map and counting only its final walk |
| Production integration | A successful JS sandbox |
| RRG recursive theory (`R₀→R₁→R₂`, same-rule composition) | A successful GNG classifier, flat prototype graph, nested visualization, or tactical win |

## 13. Deliberately deferred work

**Online tactical learning** needs a separate causal protocol: executed-action windows, outstanding prior projectiles, exploration policy, delayed credit, known propensities where applicable, recurrence/context, memory reset and retention. `reward = recent damage trade` alone does not identify which plan caused that reward. Do not add online plasticity to rescue a weak frozen result without that design.

**Production-shaped lab** requires an explicit mapping from lawful native Sense and friendly execution facts to the observation contract, native goal/pattern authority, transaction/abort semantics, and the existing Formation/Navigation/Motion/Action owners. Generic model confidence cannot grant movement or attack authority. This plan neither blocks independent production work nor authorizes its cutover.

**Closer RRG mechanism** must import an actually accepted core mechanism from the parent standard. In particular, hierarchy means lower resonators remain internally active, several form a new effective resonator, and the same composition rule can recurse at least through `R₀→R₁→R₂`. Renaming graph diffusion, formations, prototype clusters or plan regions “resonance” is not such a transfer. A successful simpler tactical model may be retained for game value while the broader research proceeds independently.

## 14. Source register and review limits

**[P1]** `GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md` and the user's Library `02_scientific_framework.md`. Distinguish the proposed RRG framework from independent evidence.

**[P2]** `ASTELIA_IMPLEMENTATION_PLAN_STANDARD.md`, v3, 26 September 2026, supplied through the Library and read in full. It is not present as a root file in the inspected repository.

All source anchors below use repository `VasylHryha/astelia-hunte` at `11df55f6bc478bfe5b48f095a02f4b70225b3ab6` unless noted. Repository access is private; links require the user's access.

**[S1]** [Root AGENTS.md](https://github.com/VasylHryha/astelia-hunte/blob/11df55f6bc478bfe5b48f095a02f4b70225b3ab6/AGENTS.md): scope, batch verification, parallel work and local commits.

**[S2]** [formation_sim.js](https://github.com/VasylHryha/astelia-hunte/blob/11df55f6bc478bfe5b48f095a02f4b70225b3ab6/experiments/formation_sandbox/formation_sim.js): `fork`, `lookahead`, `readEnemy`, `threatRead`, `commander`, `create`, `step`, `formationPlan`, `damage`, `note`, `summary`. Its critical source ranges were reread in this review; additional lifecycle/script context was available from the preceding source review. The isolated diagnostic uses a faithfully transcribed `fork` excerpt, not a complete checked-out simulator.

**[S3]** [Sandbox README](https://github.com/VasylHryha/astelia-hunte/blob/11df55f6bc478bfe5b48f095a02f4b70225b3ab6/experiments/formation_sandbox/README.md), `look2.js`, `gauntlet.js`, comparison scripts and the two HTML viewers: sandbox scope, action lists, reported historical outcomes and consumers. Historical numbers were not rerun here.

**[S4]** [PACK_TACTICS_DESIGN.md](https://github.com/VasylHryha/astelia-hunte/blob/11df55f6bc478bfe5b48f095a02f4b70225b3ab6/systems/ai_tactics/PACK_TACTICS_DESIGN.md): previously inspected ownership and earned-perception constraints, not a full fresh native-code audit.

**[S5]** [Formation implementation plan](https://github.com/VasylHryha/astelia-hunte/blob/11df55f6bc478bfe5b48f095a02f4b70225b3ab6/systems/ai/formation/AI_FORMATION_IMPLEMENTATION_PLAN.md), opening and execution status reread: V2 executor is the production owner; V3 is a forward plan with work still outstanding.

**[R1]** Fritzke, *A Growing Neural Gas Network Learns Topologies*, NeurIPS 1994. [Original paper](https://proceedings.neurips.cc/paper_files/paper/1994/file/d56b9fc4b0f1be8871f5e1c40c0067e7-Paper.pdf).

**[R2]** Zhou et al., *Learning with Local and Global Consistency*, NeurIPS 2003. [Publication](https://papers.nips.cc/paper_files/paper/2003/hash/87682805257e619d49b8e0dfdc14affa-Abstract.html). Basis for a conventional smoothing comparison, not a claim that the proposed four-step readout reproduces that paper.

**[R7]** Ross, Gordon and Bagnell, *A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning*, 2011. [Publication](https://proceedings.mlr.press/v15/ross11a.html).

**[R8]** Agarwal et al., *Deep Reinforcement Learning at the Edge of the Statistical Precipice*, 2021. [Authors' project](https://agarwl.github.io/rliable/).

---

**First step: make the experimental instrument trustworthy. Only then ask which model deserves to win.**
