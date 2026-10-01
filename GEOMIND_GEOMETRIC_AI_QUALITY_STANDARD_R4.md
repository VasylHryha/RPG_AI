---
title: "GeoMind — Geometry, Dynamics, Memory: Research and Quality Standard"
revision: R4
date: 2026-10-01
status: C1_REVIEW_READY
supersedes: "GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R3.md in full"
research_status: "C0 reconstruction evaluated locally; hypotheses await independent interpretation and no hierarchy implemented"
companion: GEOMIND_GEOTACTICS_ASTELIA_EXPERIMENT_PLAN_R3.md
---

# GeoMind — test the mechanism, not the appearance

> **The question is whether persistent relational structure, local dynamics and local adaptation can perform useful computation. Geometry is mathematics; this project changes the representation and execution mechanism, not that fact.**

This revision replaces R3 rather than appending a competing hierarchy note. R3 corrected the experimental validity problems, but it left recursive resonator composition as a deferred arm. That underrepresented the original RRG hypothesis: persistent lower-level structures becoming new effective units and recursively composing again is a **core research requirement**, not an optional visualization feature. No accepted implementation is being discarded: the supplied documents still record the research implementation as not started.

## 0. Execution status and scope

| Item | Record |
|---|---|
| Current work | C0 R003 independently ACCEPTED; C1 R002 CHANGES_REQUIRED (`evidence/c1_review/CLAUDE_ACCEPTANCE.md`; it conflicts with the earlier `ACCEPTANCE.md` and must be resolved); C1 R003 superseded; C1 R004 REVIEW_READY, independent acceptance pending |
| First core milestone | **C0 — reproducible structural-memory reference experiment**, ACCEPTED (R003) |
| Last accepted GeoMind code | C0 R003, independent receipt `evidence/c0_review/ACCEPTANCE.md` |
| Checks executed locally | C1 R004: fourteen checks PASS; 80 seed-varied interventions in 83.9s in two arms, all six gates PASS. Queue arm: 60 correct commits (zero relaxation steps) and 20 contradiction rollbacks. Fallback arm: 80 correct commits, 20 through the metered CG. Historical C1 R003: twelve checks PASS in 2.23s; 48 seed-varied interventions in 40.36s, 36 correct commits (all with zero relaxation steps) and 12 budget-exhausted rollbacks (every inconsistent edge), all six gates PASS. Historical C1 R002: ten checks PASS in 1.42s; 16 fresh interventions in 7.28s, 13 correct commits and three budget-exhausted rollbacks, all six gates PASS. Historical C1 R001: seven checks PASS in 3.64s; 16 interventions in 24.76s, five correct commits and 11 rollbacks. C0 revised contracts: 58 PASS in 8.60s; R003: all 11 gates PASS across 1,250 fresh worlds in 331.50s, zero solver/infrastructure failures. Receipts preserve failed checks separately |
| Core artifacts | This standard, one hypothesis/experiment manifest per actual experiment, machine-readable results |
| Astelia work | A separate application experiment governed by the companion plan; not a pass for the core theory |
| Not authorized by this document | A production game cutover, general intelligence claim, new physical theory claim, hardware purchase or unattended execution |

Local implementation: `geomind/`, `tests/test_c0.py`, immutable `experiments/c0_manifest.json`, pinned `uv.lock`. Actual commands: `.venv/bin/python -m pytest -q` and `.venv/bin/python -m geomind.run_c0 --split all --output evidence/c0`. Initial fixture run: 15 passed, three max-sweep failures; before final-world evaluation, gauge selection changed from first opaque ID to maximum exposed weighted degree (stable ID tie-break), retaining the specified dynamics and budgets. Final contracts: 18 passed in 1.58s. Full evaluation: 1,000 worlds in 123.96s, all gates passed, zero nonconvergences. Receipts preserve the initial failures and per-world results. Hypothesis interpretation and independent acceptance remain open; C1–C8 remain NOT_STARTED. No JavaScript dependency or Astelia mutation is needed for C0.

**C0 review revision, 1 October 2026.** The previous paragraph records R001 history. R002 registers a new schema/algorithm/generator, fresh world seeds, a Gaussian-noisy arm and explicit relation manifests. It adds strict input/artifact validation, semantic equilibrium checks on load, a normalized-force guard for tiny positive weights, typed fresh-solve failures, independently computed residuals, complete hidden-edge query coverage, baseline conditional/total accuracy, paired world-level cost uncertainty, full source snapshots and overwrite-resistant streamed evidence. Maximum-weighted-degree anchor discovery is linear in nodes/edges, replacing repeated component-wide scans. Original receipts are historical; exact source snapshots begin with R002. R003 additionally guards qualification against missing answers and missing residual/error values; the interrupted R002 partial run is retained in `evidence/c0_review_interrupted/`, and R003 uses another disjoint set of fresh seeds. Current commands: `.venv/bin/python -m pytest -q --junitxml=evidence/c0_review/contracts.xml` and `.venv/bin/python -m geomind.run_c0 --split all --output evidence/c0_review --contract-report evidence/c0_review/contracts.xml`. Current findings/results: `evidence/c0_review/REVIEW.md` and `results.json`. Independent acceptance after repairs remains pending; no dependent milestone starts here.

**Implementation workflow.** Complete the current session's entire scoped code/caller/config/test batch before running its affected checks. Then run one consolidated verification phase; complete any related repair batch before its affected rerun. Do not run the game fleet or unrelated checks because this research exists. Preserve unrelated work in a shared checkout; do not reset, stash, create worktrees, monitor other sessions, or push without permission. Implementation produces `REVIEW_READY`; a separate review evaluates the reached evidence. These rules follow the supplied Astelia planning standard v3. [P2]

**Separate three statuses:** implementation (`NOT_STARTED / ACTIVE / REVIEW_READY / ACCEPTED / BLOCKED`), check (`PASS / ASSERTION_FAILURE / INFRASTRUCTURE_FAILURE / NOT_RUN`), hypothesis (`SUPPORTED_WITHIN_SCOPE / NOT_SUPPORTED / INCONCLUSIVE / NOT_TESTED`). An accepted implementation may produce evidence against its hypothesis. Neither status implies the other.

## 1. Alignment with the original geometry theory

The recovered RRG framework defines relational geometry broadly: components, positions, connectivity, order, orientation, boundaries and constraints. It pairs this with temporal mode structure: amplitude, phase, frequency, propagation, coupling and timescale. Its stronger proposal includes mutual geometry–mode influence and persistent structures becoming effective units at subsequent scales. It explicitly calls itself a working hypothesis, not established physics. [P1]

### 1.1 Claim ledger — no substitution between claims

| ID | Claim being tested | Evidence needed | What does not establish it |
|---|---|---|---|
| H-R | Persistent geometry encodes useful relationships | Identifiable held-out queries; appropriate compiled-reference baseline | Attractive clusters alone |
| H-D | Dynamics through that structure add useful computation | Quality/cost/robustness beyond a matched static readout | Any lookup becoming worse after its keys are corrupted |
| H-P | Experience changes reusable memory | Frozen versus adaptive comparisons, retention and update costs | A fixed table loaded before every fight |
| H-L | Useful work is local in a meaningful computational sense | Retrieval, input processing, updates, convergence and memory all counted as size grows | A bounded walk after a full-map nearest-neighbor scan |
| H-M | Geometry and activity/modes influence one another | Separate interventions in both directions; recovery and task consequences | A graph with no activity-dependent adaptation |
| H-C | Stable structures become reusable units under a shared rule across scales | Explicit coarse-graining map, at least two transitions, prediction/error tests | Manually naming three clusters “a hierarchy” |
| H-U | A tactical controller is useful | Closed-loop outcomes against strong controls on unseen scenario instances | Teacher-label agreement alone |
| H-E | The physical implementation saves energy | Hardware energy measurements, matched accuracy/throughput and all overheads | Fewer Python lines, fewer nodes visited, or simulated circuit power |

C0 addresses H-R. C1 studies updates and cost. C2 provides a small **weighted-geometry/activity** mechanism test for H-D/H-P/H-M. **C4–C8 are now the core recursive-resonator lane for H-C and the stronger whole↔parts form of H-M.** H-E remains explicitly untested. GeoTactics addresses H-U and the incremental value of a geometric memory/readout; it does not automatically advance C2 or any recursive-resonator milestone.

A fixed-point relaxation is a dynamical mechanism, but a single converged potential is not evidence of oscillatory resonance. Learning edge weights changes weighted relational geometry, not necessarily Euclidean node positions. Any claim specifically about moving positions or phase resonance needs those states and corresponding experiments. These distinctions preserve the original theory instead of quietly redefining it to fit a successful classifier.

### 1.2 What is allowed

Ordinary arithmetic, sparse graphs, distances, local minimization, matrix-based **reference solvers**, and exact symbolic baselines are allowed. The initial candidate has no pretrained encoder, language-model answers, dense attention, automatic differentiation or separately executed reverse-mode backpropagation. This is an experimental boundary, not a claim that gradients are incompatible with geometry.

A local learning rule can approximate a gradient even without executing a backpropagation program. Equilibrium propagation is an explicit precedent; presenting it as “not optimization” would be incorrect. [R4]

## 2. What the research changes in the design

| Precedent | Concrete lesson | Decision here |
|---|---|---|
| Growing Neural Gas | Incremental prototype placement and adaptive adjacency are established methods | Use as a named tactical candidate, not as evidence of a new intelligence architecture. Account for nearest-two search and global error bookkeeping. [R1] |
| Graph label smoothing | Propagating values over nearby nodes has a strong conventional interpretation | Require a matched fixed-graph smoothing control; describe finite diffusion as diffusion, not an unexplained attractor. [R2] |
| Swarmalators | Position and oscillator phase can mutually affect collective behavior | Relevant to a later positional/phase experiment; does not prove memory, recursive abstraction or AI efficiency. [R3] |
| Equilibrium propagation / physical coupled learning | A response and a slightly nudged response can support local parameter changes | Use a transparent small network as a mechanism probe in C2, with numerical references and disclosure of its gradient interpretation. [R4, R5] |
| TransE | Typed translations already provide a relational-model precedent | Do not call displacement reconstruction or translation scoring novel by itself. [R6] |
| Sequential imitation learning | A learner encounters states different from those collected by its teacher | Use training-only learner-state collection in the tactical lane. [R7] |
| Reliable RL evaluation | Point estimates from a few stochastic runs can be misleading | Report training replicates, episode-level uncertainty and paired comparisons. [R8] |

The research supports building small tests. It does **not** establish that present neural models face a geometry-related wall, that geometry avoids computation, or that a geometry-first system will be cheaper.

## 3. Architecture: one state owner, observable operations

Initial implementation: Python, NumPy and pytest; plotting is optional and read-only. Pin actual dependency versions in the project lock/environment record rather than assuming a future package version. CPU-only. Do not build a framework or an engine integration first.

**Owner direction, 1 October 2026:** JavaScript may be limited to drawing and controls. If measured computation cost warrants it, use a C++ backend for numerical dynamics/simulation instead of running those kernels in JavaScript. C0 currently uses Python/NumPy; no JavaScript compute path or C++ backend has been implemented. A later compiled backend must preserve the same snapshot, transaction, typed-answer, convergence and cost-receipt contracts and be checked against the independent numerical references. A viewer consumes read-only committed snapshots/traces and submits explicit requests; it does not own or mutate geometry. This direction does not bypass milestone acceptance or authorize a separate engine/framework build.

```text
frozen experiment manifest + training observations
                 ↓
        candidate state owner
                 ↓
       committed geometry snapshot
                 ↓
     query dynamics → typed answer + trace
                 ↓
         independent evaluator
```

| Meaning | Owner | Mutation / access |
|---|---|---|
| Hidden world/task truth | Dataset/evaluator | Never imported by the candidate |
| Persistent geometry | `GeometryState` | Updated by one explicit `learn` transaction |
| Query activity | Per-query workspace | Reset or warm-started only according to the declared protocol |
| Update proposal | Learner workspace | Committed only after finite/bounds/convergence checks |
| Expected answer / metric | Evaluator | Read after the candidate answer is fixed |
| Plot/camera layout | Visualizer | Never affects the candidate state |
| Hypothesis, split, settings | Immutable manifest | New version required for a material change |

`configure → fit/train → freeze → query → evaluate → export` is the frozen-evaluation lifecycle. **Split and metric definitions are frozen before fitting**, not after relaxation. In an adaptive experiment use `predict → record → reveal permitted feedback → propose update → commit`, with an explicit memory reset policy.

A failed query returns `UNKNOWN`, `UNIDENTIFIABLE`, `NOT_CONVERGED` or `INVALID_STATE`; it must not manufacture a confident answer or consult truth to repair itself. A failed update leaves the preceding snapshot unchanged. Serialization records algorithm/schema versions, node/edge identities, all persistent values, RNG state where relevant, settings and training-manifest hash.

## 4. Core ladder: remove weak gates and test useful mechanisms early

### C0 — structural memory, with a strong compiled baseline

**Why/result.** Establish correct state, data separation and reproducible geometric reconstruction. This is a reference experiment, not the main novelty claim. Separate attraction/repulsion animation is optional; it is no longer a required milestone that can delay a meaningful test.

**Input convention.** A directed edge `(i,j,d)` means exactly `position(j) - position(i) = d`. Use opaque relation IDs mapping to known displacement vectors in the manifest. Do not use ambiguous English `A EAST_OF B`. An integer lattice has vectors `(1,0),(-1,0),(0,1),(0,-1)`; a continuous arm supplies exact numerical offsets, not a cardinal label pretending to encode distance.

**Generator.** Generate 100 training, 50 validation and 100 final-test worlds, each initially 32 nodes. In each connected component, expose a spanning tree and a seeded subset of additional consistent edges. Hide selected *redundant* edges and sample pair queries not supplied directly. Hidden relations must remain identifiable from the exposed component. Permute node IDs independently of positions. Include a separate disconnected-component arm and an inconsistent-loop arm. The evaluator retains true coordinates; the learner sees only IDs, exposed offsets and declared component structure.

A split between worlds tests reuse of the algorithm and parameters, not learned language semantics. Reconstruction within a new world uses that world's exposed constraints and is correctly described as transductive inference.

**Candidate.** Minimize the explicit residual by local simultaneous relaxation:

```text
E(x) = 1/2 Σ_(i,j) w_ij ||(x_j - x_i) - d_ij||²
r_ij = (x_j - x_i) - d_ij
accumulate grad_i -= w_ij r_ij ; grad_j += w_ij r_ij
x_free <- x_free - α grad_free
```

All gradients use the same old state. Fix one arbitrary node per connected component at zero as a gauge; this is not a ground-truth coordinate. All weights are 1 in the clean arm. Use `α = 0.25 / max(1, maximum weighted degree)`, Float64, maximum 10,000 sweeps, and record both residual and update size. Stop when maximum gradient norm is below `1e-8` and maximum coordinate change is below `1e-8` for ten sweeps. A max-sweep exit is `NOT_CONVERGED`, not a pass. These are proposed pilot settings, not measured optimum values.

No inter-component repulsion is introduced: unrelated components have no identifiable relative placement. A separate component ID permits `UNIDENTIFIABLE` answers, but is not used to recover a hidden offset. Answer an identifiable query by subtracting its two committed coordinates; this is a valid geometric readout, not proof that query-time propagation is necessary.

**Mandatory baselines.**

1. Compile one coordinate frame by traversing each exposed spanning tree once; answer subsequent pairs by coordinate subtraction. Clean-data construction is O(V+E), storage O(V), and a known-ID pair lookup/subtraction is O(1) under the declared indexing model.
2. On noisy/inconsistent graphs, anchored least squares over exactly the same exposed constraints; use an independent implementation.
3. A direct-edge-only answerer with explicit abstention. Its low coverage must not be reported as 100% task accuracy.

The compiled baseline prevents a misleading “local query beats graph traversal” claim: ordinary methods can also preprocess geometry once.

**Verify.** Exact 2-node and loop cases; inconsistent triangle; component renaming; independent ID permutations; global translation; rotate offsets and positions together; an excluded cross-component query. Compare candidate residual with the independent reference and report identifiable-query error/coverage separately. No topology-ablation requirement is imposed on a query that does not read topology.

**Done when.** Solver and references agree within `1e-5` displacement on at least 99% of clean identifiable queries, all disconnected-pair cases abstain, and contradictions remain visible. Report every nonconvergence. This certifies the implementation of the reference experiment, not superiority over the compiled baseline.

**Review focus.** Convention, identifiability, gauge, held-out leakage, stopping on small updates despite large residual, and hidden global work.

### C1 — incremental updates, locality and forgetting

**Requires:** C0 accepted implementation, not a claim of superiority.

**Implement.** Add one consistent edge, one inconsistent edge, a new node, and a bridge between previously disconnected components as four separate interventions. Begin from a saved state. An active queue contains affected nodes; an update adds neighbors when their residual exceeds `1e-8`. Process nodes in stable ID order with a configured 100,000 edge-visit budget. This is the same residual law as C0, not a new heuristic. If the budget expires, return `NOT_CONVERGED`; optionally run an explicitly metered full solve as a distinct fallback arm.

A bridge may require a whole component's coordinates to change. “Only a few nodes should ever move” is not an acceptance rule: the correct change can be global. Compare answers invariant to the component gauge, not raw coordinate movement alone.

**Verify.** Compare every result to a fresh compiled/least-squares reference on 32, 128, 512 and 2,048 nodes. Measure accuracy, touched edges, queue maintenance, total update/query time, bytes, and fallback rate. Use truly unaffected disconnected components as retention controls and connected distant nodes as *potentially affected* controls.

**Done when.** Updates are correct or explicitly unresolved, prior snapshots survive rejected updates, and all work is charged. H-L/H-P get their own evidence verdict. No sublinear update claim is allowed merely because local updates exist.

### C2 — a small geometry/activity learning experiment

**Why.** C0 can be solved perfectly by conventional compilation. To study a stronger part of the hypothesis, use a state whose local response changes its future response through persistent relational parameters. This is a deliberate, named precedent-based probe—not an assertion that moving dots creates intelligence.

**Selected candidate: adaptive sparse relaxation network.** Start with a connected 4×4 grid (16 nodes, 24 undirected edges). Node values `u` are fast activity; positive edge conductances `g` are persistent weighted geometry. Plot positions are fixed and are not claimed to perform computation. Number the grid row-major from 0 to 15; nodes 0 and 3 receive inputs and node 10 is the output. Edges connect horizontal/vertical immediate neighbors only. Use the same fixed port IDs for all methods, opaque names elsewhere.

For non-input nodes define:

```text
E_g(u; x) = 1/2 Σ_(i,j) g_ij (u_i-u_j)² + λ/2 Σ_free u_i²
C(u; y)   = 1/2 (u_output-y)²
free dynamics:    du_i/dt = -∂E_g/∂u_i
nudged dynamics:  du_i/dt = -∂(E_g + β C)/∂u_i
```

Inputs are clamped for both phases. A node update reads its immediate neighbors; the output additionally receives training feedback during the nudged phase only. There is no output target at inference. `λ=0.01`, `g ∈ [0.05,5]`, initialize conductances from Uniform[0.5,1.5] with a recorded seed. Use a synchronous Euler relaxation with
`dt = 0.25 / (2*maximum_current_weighted_degree + λ + β)`; recompute this bound once per frozen-geometry phase and charge that scan;
`β=0.05` during training and 0 during inference. Maximum 20,000 sweeps; require max force below `1e-9`. Report nonconvergence and bound saturation; do not hide either by clipping node outputs.

After both phases converge, update each edge locally:

```text
g_new = clip(g + η/(2β) * ((u_i^F-u_j^F)² - (u_i^N-u_j^N)²), 0.05, 5)
η = 0.01
```

F and N are responses with the *same old geometry*. Do not change an edge between the free and nudged solves. This soft-nudging rule is an equilibrium-propagation-style adaptation, related to physical coupled learning; it is not an exact reproduction of every clamped-output protocol in that literature. Its small-nudge relationship to an objective gradient must be disclosed. No autodiff/backward program is executed in the candidate. [R4, R5]

**Task and controls.** Train on 100 input pairs sampled in `[0,1]²`, validate on 50, test on 200. First use an intentionally simple affine target `y=0.2 x1+0.5 x2`; this is a mechanism check, so an ordinary linear model is expected to be excellent. Use a separate realizable-task control generated by a hidden conductance network of the *same topology* and independent parameters. Disclose that matched generator prior; it is not out-of-family generalization. Twenty initialization seeds, 100 training epochs, fixed sample-order seeds. Validation may select among predeclared η values `[0.003,0.01,0.03]`; test settings then freeze.

Baselines: frozen random network; constant mean; ordinary linear regression; the same network with an independent direct equilibrium solver; and the same network trained using a numerical/analytic gradient reference. Since a passive linear network has limited function capacity, arbitrary nonlinear tasks or unrestricted signed outputs are not suitable success criteria. XOR is a capacity counterexample, not evidence that a faulty learner should be tuned forever.

**Verification before task claims.** On a 3-node analytic circuit and selected 16-node samples, compare equilibrium to an independent linear solve. Compare the conductance update direction to finite differences of the true task loss away from clipping boundaries; reduce β and relaxation tolerance to expose numerical error. Test clone/freeze/restore, no-target inference, permutation equivalence, disabling feedback, and an intervention on an edge predicted to change the output. Task MSE, update norm, saturation, convergence sweeps and retention are reported separately.

**Meaningful result.** Held-out error decreases relative to the frozen network, feedback removal removes learning, and both geometry→response and response→geometry paths have direct causal evidence. A provisional implementation target is held-out MSE ≤`1e-3` on the realizable control and ≥50% reduction from the frozen initialization, with uncertainty across seeds. Failure of this target remains a valid research outcome. It must not be relabeled success through a nicer visualization.

**What this can support.** Reusable task learning by a local-response/weighted-geometry mechanism in a small, known model family. It does **not** establish moving-coordinate necessity, phase resonance, recursive scale closure, novel AI, or digital compute efficiency. In software, each sweep still processes all active edges; the local rule is not automatically a local-total-cost algorithm.

**Review focus.** Exact update sign/factor, convergence error mistaken for learning, hidden target access, linear capacity, and candid relation to established learning algorithms.

### C3 — learning stability, then a bounded research decision

**Requires:** C2 correctness and actual learning evidence, or a documented negative result explaining why it is being redesigned.

Train task A, introduce B, and measure A and B both before and after. Use one shared output only when the two tasks are compatible or the task context is explicitly provided; conflicting labels for identical inputs are not solvable without such context. Compare uninterrupted learning, frozen-A memory, and a bounded replay control with the same sample budget. Record plasticity work and memory, not just accuracy.

Decision: `KEEP_SIMPLE_MODEL`, `REWORK_LOCAL_RULE`, `REWORK_REPRESENTATION`, or `STOP_THIS_BRANCH`. Do not add hierarchy merely to rescue an unexplained C2 failure. The recursive-resonator lane below is an **independent core test of H-C**: it may proceed after its own prerequisites even if C2's supervised-learning mechanism is rejected, but a failure in one lane must never be hidden by success in the other.

### Recursive unit interface — the same object shape at every scale

Before C4, lock one recursive contract so hierarchy is not retrofitted later. Both a primitive active element and an accepted resonator implement the same **upper-facing** interface:

```text
ActiveUnit {
    effective_position X
    characteristic_size L
    mode_signature M_eff       # frequency/phase-pattern/amplitude/coherence summary, not one scalar frequency
    boundary_ports[]
    stability/validity S
}
```

A primitive supplies these values directly from its own state. A resonator derives them from its internal dynamics. The same `couple / evolve / attach-detach / test-stability / compose` family consumes `ActiveUnit` values at every reached scale. Internal member lists remain owner-private and evaluator-visible; they are **not** an ordinary upper-level read API.

Coupling topology is allowed to **grow and break**. Use one dimensionless attach/detach protocol at every scale: compatible units inside a normalized capture region may create a coupling after a persistence delay; a coupling may disappear after sustained separation/stress or loss of mode compatibility. Exact capture, release and persistence thresholds are frozen in the experiment manifest before final evidence and are reused across levels after normalization by `L` and the relevant characteristic timescale. No parent labels create edges.

This is the mechanism meant by “geometry grows”: new stable couplings can create a resonator; that resonator exposes the same interface; it can then couple to others and participate in the next composition without changing the governing operation.

### C4 — base resonator: geometry ↔ mode closure

**Why.** The original theory is not only about storing relationships. It proposes a persistent object whose geometry constrains its modes and whose modes help maintain or transform that geometry. C4 therefore builds the smallest explicit `geometry ↔ activity` resonator before any hierarchy claim.

**Selected first model: sparse position–phase elements.** This is a small swarmalator-inspired mechanism probe, not a claim of novelty. Each primitive element has:

```text
Element {
    position x ∈ R²
    phase θ ∈ [-π, π)
    intrinsic rate ω
    local neighbor set
}
```

For neighbors `j` of `i`, use normalized local dynamics of the form:

```text
r_ij = ||x_j - x_i||
unit_ij = (x_j - x_i) / max(r_ij, ε)

x_dot_i = mean_j[
    unit_ij * (A * (1 + J*cos(θ_j-θ_i)) - B/max(r_ij, ε))
]

θ_dot_i = ω_i + mean_j[
    K * w(r_ij) * sin(θ_j-θ_i)
]
```

Start with `A=1`, `B=1`, `J=0.8`, `K=1`, `ε=1e-6`, `w(r)=exp(-r²)`, then freeze those dimensionless defaults before the registered seed sweep. Use bounded integration and declare `dt`, termination, neighbor radius/cap, boundary behavior and numerical tolerances in the experiment manifest. If a different stable integrator is required, change the manifest/version before final evidence rather than silently retuning per seed. [R3]

**Resonator criterion.** A set of elements is a candidate resonator only when all are true for a predeclared persistence window:

1. membership/connectivity remains stable;
2. normalized radius/shape statistics remain bounded;
3. a predeclared **mode-lock/stability** statistic remains within tolerance; for the first synchronized fixture `ρ = |mean(exp(iθ))|` is reported, but stable anti-phase or structured phase-offset modes must be represented by their pairwise phase pattern / spectral signature rather than incorrectly rejected for low `ρ`;
4. its dominant collective frequency/mode signature and internal phase relations are reproducible across a short observation window;
5. after a bounded perturbation, it returns to the same basin or an explicitly equivalent basin within a recovery window.

The thresholds are fixed in the manifest before the final sweep. The evaluator may know intended fixtures; the candidate formation detector does not receive group labels.

**Required interventions.** `G→M`: perturb geometry while holding phase state; the predicted mode statistic must change. `M→G`: perturb phase/activity while holding initial geometry; the predicted geometry/recovery path must change. Removing either coupling direction is a matched ablation. A stable cluster with no two-way causal effect is not an RRG resonator for this project.

**Done when.** Across registered seeds, at least one small resonator forms reproducibly, survives the declared small perturbations, fails or changes under the predicted coupling ablations, and exposes a stable effective state without the evaluator supplying its final geometry.

### C5 — many resonators form one new effective resonator

**Why.** This is the first direct test of the user's hierarchy requirement: several already-persistent resonators couple, create a new collective structure, and remain internally active while the new whole acquires its own mode.

Every accepted lower resonator exposes the same **effective-unit contract** upward:

```text
ResonatorState {
    level
    effective_position X
    mode_signature M_eff      # collective frequency/spectrum, phase relations, amplitude/coherence
    optional_phase Θ            # only when meaningful for this mode family
    collective_rate Ω
    characteristic_size L
    stability_score S
    boundary_ports[]
    member_digest          # identity/provenance, not an upper-level read API
}
```

The upper level may read only this effective state and declared boundary ports during its coarse simulation. It may not inspect every primitive member to make each upper-level decision. The evaluator retains the full lower state for comparison. A boundary port carries the effective coupling quantities required by the same interaction law (for example location/orientation, coupling capacity/strength and mode-facing state); it is derived from active lower boundary interactions, not invented as a new level-specific behavior.

**Composition rule.** `compose({R_n}) -> candidate R_(n+1)` consumes the same `ActiveUnit` contract, dynamic attach/detach rule, normalized geometry↔mode coupling family and resonator criterion as C4 after nondimensionalizing distance by the participating units' characteristic size and time by their collective period. There is **no `if level == 1`/`if level == 2` solver**. Level-specific manually authored geometry, labels or thresholds fail H-C.

A candidate is promoted only after persistence/recovery tests pass. Promotion does not delete or freeze its members: lower resonators continue their internal dynamics. The parent supplies only lawful boundary conditions/coupling back downward; it may not directly overwrite arbitrary member states.

**Required evidence.** Compare full lower-level simulation against the effective-unit prediction on held-out boundary excitations. Report response error, mode/frequency error, recovery error and work. Show at least one collective behavior—phase relation, response mode, or boundary transfer—that is not present in an isolated constituent by itself.

### C6 — recursive composition: `R₀ → R₁ → R₂` with the same rule

This milestone is the central hierarchy gate.

Start from several accepted base resonators `R₀`. Let the C5 operator promote stable groups to `R₁`. Then apply **the same composition, stability, promotion and effective-state rules** to multiple `R₁` units and attempt to form `R₂`.

Required invariants:

- at least two successive promotions occur (`R₀→R₁` and `R₁→R₂`);
- no ground-truth parent labels are provided to the formation detector;
- the same dimensionless coupling, edge birth/death and promotion criteria are reused;
- parameters may be normalized by measured size/timescale, but not separately hand-tuned per level;
- an `R₂` query/controller reads `R₁` effective states, not all `R₀` internals;
- lower levels remain dynamic and can transmit disturbances upward;
- the higher-level state can constrain lower-level boundary behavior downward;
- full versus coarse trajectories are compared under held-out excitations, not only on the formation examples.

**H-C support gate.** H-C is `SUPPORTED_WITHIN_SCOPE` only if two successive scale transitions satisfy these invariants with bounded predictive error. A dendrogram, connected-component tree, manual cluster labels, or a different algorithm per level is explicitly insufficient.

### C7 — perturb, dissolve, survive and reform

A hierarchy is not credible if promotion is permanent bookkeeping. Apply predeclared perturbations of increasing strength to an accepted `R₂`:

```text
small perturbation  -> R₂ returns to its basin
medium perturbation -> R₂ may reorganize to R₂' while lower resonators survive
large perturbation  -> R₂ dissolves into valid lower resonators
removed stress      -> lower resonators may re-couple/reform without restoring a saved parent object
```

Measure survival of lower identities, parent stability, recovery time, changed membership, mode change and energy/work surrogate. Do not force the previous grouping during recovery. This directly tests the theory's distinction between loss of higher organization and destruction of all lower structure.

### C8 — hierarchy usefulness and compression

Only after C6/C7 work may we test the claim that a stable higher structure is a **new useful effective unit** rather than just a label.

Compare:

1. full primitive simulation/readout;
2. one-level coarse simulation;
3. two-level recursive coarse simulation;
4. a matched static clustering/coarse baseline with no dynamic promotion/recovery.

Use held-out external excitations or queries that enter through declared boundary ports. Measure answer/trajectory error, latency, touched state, memory, rebuild/update cost, and the point at which coarse simulation ceases to be accurate. Count the cost of forming and maintaining the hierarchy; do not report only cheap upper-level queries.

A strong result is **not** "fewer objects." It is: the recursively formed effective units preserve enough behavior for a declared task while materially reducing repeated lower-level work, and the full system can still reopen/refine lower levels when the approximation fails.

### Non-negotiable recursive-resonator invariants

These rules apply to C4–C8:

1. **Same rule across scales.** The active-unit interface, coupling law, connection birth/death rule and composition law may normalize by measured scale; they may not switch to a new handcrafted solver at each level.
2. **Lower levels remain real.** Promotion never deletes the internal resonators merely to make the hierarchy cheap.
3. **Whole ↔ parts causality.** Lower dynamics create the collective state; the collective state changes lawful boundary conditions/coupling of the parts.
4. **Promotion is earned.** A group becomes a higher resonator only after persistence, mode and perturbation criteria pass.
5. **Dissolution is real.** A parent can cease to exist while viable children continue.
6. **Effective-state discipline.** Upper levels use the declared effective interface; repeatedly scanning all descendants defeats the abstraction claim.
7. **No manual hierarchy labels.** Ground-truth structure belongs to evaluation, not the formation mechanism.
8. **Error travels with compression.** Every coarse state carries/estimates approximation error or validity bounds; invalid coarse states must reopen/recompute rather than silently continue.
9. **No hierarchy-by-picture.** Nested circles or a clustering tree alone are not evidence.
10. **Recursion must actually recurse.** At least `R₀→R₁→R₂` is required before claiming scale-recursive organization.

### Beyond the current digital core

**Physical-energy arm (H-E):** remains separate. A successful digital hierarchy does not establish lower joules/op on real hardware. That requires matched hardware energy measurements including sensing, memory, hierarchy maintenance and I/O.

**Language/LLM arm:** remains deferred until the core mechanisms have task evidence. An LLM may later translate language into/out of the geometry but cannot answer the registered core task for it.

C4–C8 are now **core research milestones**, not optional future decoration. Their unresolved status is part of the execution plan, and failure is a valid outcome.

## 5. Validity and causality rules

### 5.1 Four different kinds of intervention

| Intervention | Expected interpretation |
|---|---|
| Consistent ID permutation / coordinate-frame change | Same task and result; tests representation equivariance/invariance |
| Corrupt coordinate–content association | Tests whether that association is used, not whether the algorithm is novel |
| Remove one declared mechanism with matched remaining information | Tests that mechanism's incremental contribution |
| Predict a particular consequence of a geometric change, then intervene | Stronger mechanistic evidence than arbitrary destruction |

Coordinate rotation alone must not be required to hurt a rotation-invariant system. Changing all labels and mappings together must not hurt it. Topology need not matter to a direct coordinate readout. A failed topology ablation narrows the claim about topology; it does not disprove all geometric representations.

### 5.2 Equal information and strong controls

Give comparison algorithms the same permitted observations, examples, feedback, preprocessing and decision budget. Report any deliberate difference. Graph methods and kNN are geometric methods in ordinary terminology, not “non-geometric” straw men. The relevant question is what extra value an adaptive topology or temporal dynamics provides.

No test outcome may tune a final model. Split by independent world/episode, not adjacent snapshots. Settings changed after test inspection start a newly identified experiment on new data. A withheld opponent implementation that developers already inspected is developer-known; only fresh instances remain fully untouched. Do not advertise it as an unseen phenomenon.

### 5.3 Persistence is protocol-specific

In frozen evaluation, load the same trained state for each episode; queries must not mutate it. Resetting to that same state should give identical behavior. In continual-learning evaluation, compare retained learned changes against the same initial state restored before each adaptation episode. Do not use one protocol's expected result as the other's negative control.

## 6. Cost and uncertainty

Count the entire path:

```text
input acquisition + features + retrieval/indexing + dynamics/readout
+ decision application + online updates + maintenance + fallbacks
```

Also record offline data/teacher generation, fitting, model selection, storage and load costs. For repeated use, report the break-even query count against the strongest relevant baseline:

`additional offline cost / positive per-query saving`.

If there is no positive saving, there is no amortization break-even. This accounting concerns measured CPU time or energy units explicitly named; it is not provider profit.

Distinguish local update **rule**, sparse representation, bounded query walk and sublinear end-to-end work. A scan of 256 prototypes may be the simplest good implementation; label its O(Md) cost honestly. GPU matrix operations can be fast despite appearing less local. No FLOP/energy conclusion follows from abstract visited-node counts alone.

Use independent dataset and initialization seeds. Report individual runs, paired differences, uncertainty across independent worlds/episodes and variability across training runs. Do not treat every frame as a new independent trial. Primary endpoint and meaningful effect margin are registered before the final test. An interval overlapping both useful and harmful effects is inconclusive, not “basically passed.” [R8]

## 7. Evidence contract and stop rules

Every experiment receipt records:

```text
experiment_id, source_commit, source/file hashes
hypothesis_ids, claim_scope, algorithm/version
split_manifest_hash, data-generator version, all RNG seeds
fit_settings, selected_checkpoint, selection_rule
observability, feedback rules, reset policy
checks_executed, checks_not_run, failures
per-instance results, aggregate uncertainty
preprocessing/update/query/total cost, bytes, fallback frequency
baseline and ablation definitions
implementation_status, hypothesis_status, limitations, next action
```

A reviewer checks the candidate and the evaluator independently. Finite-difference or direct-solve references cannot silently share the bug-bearing implementation. A record of `NOT_RUN` is better than a fabricated result.

Stop the current branch when a matched simpler baseline dominates it on the registered quality/cost criteria, when geometry perturbations do not affect a claim that requires them, or when repeated changes cannot be explained without test-set tuning. Keep a model that matches quality but demonstrably saves memory or improves robustness—but describe that exact gain, not a breakthrough.

## 8. Relationship to the Astelia experiment

The tactical plan is a controlled application lane. It first repairs the measurement boundary, then compares simple models with an adaptive geometric map. A GNG map with per-plan scores is called **prototype regression with bounded graph diffusion**. That description is not a dismissal; it prevents an ordinary useful method from being presented as full RRG.

No C0/C2 pass is required to fix the tactical simulator or run its baseline comparisons. No tactical win can be used to mark C0/C2 accepted. A later transfer must import an actual tested core component and show what it contributes, rather than merely use similar vocabulary.

Production Astelia integration remains separate: lawful Sense, Groups/tactical authority, Formation, Navigation, Motion and Action retain their owners. A sandbox selector cannot validate those native lifecycles by winning a synthetic battle.

## 9. Next implementation prompts

**Core implementation:**

> Read R4 and implement C0 as one complete scoped batch, including the compiled-coordinate and independent least-squares references, identifiable/disconnected/noisy fixtures and deterministic receipts. Do not implement language, tactical control or C2 yet. Then run the affected checks once. Record actual results, all failures and NOT_RUN items. Stop at REVIEW_READY; do not claim novel intelligence from lattice reconstruction.

**Core review:**

> Review the candidate, generator, information access, references and actual receipts. Fix in-scope errors in a complete batch before rerunning affected checks. Decide implementation acceptance separately from the hypothesis verdict. Check that the result is not explained entirely by an omitted cheap baseline. Preserve concurrent work and do not start a dependent milestone before acceptance.

**Recursive-resonator implementation (when C4 is active):**

> Read R4 §§1 and 4 C4–C8. Implement only the current recursive-resonator milestone using the declared effective-unit contract and the same normalized coupling/promotion rules. Do not hand-author parent membership, level-specific solvers or final geometry. Keep lower resonators active, expose full-vs-coarse comparison traces, and batch all code/tests before the affected verification phase. Stop at REVIEW_READY.

**Recursive-resonator review:**

> Verify that the hierarchy genuinely forms through the same rule at each reached level, that the upper solver cannot inspect all descendants as a hidden shortcut, that perturbation/dissolution behaves according to the registered protocol, and that coarse-state error is measured against the full lower simulation. Reject any result that is only clustering, labels, or a different solver per level.

## 10. Source register

**[P1]** User's `02_scientific_framework.md`, RRG v0.1 with later addenda, retrieved from the Library for this review. Relevant original definitions: research status, relational geometry, temporal mode structure, dynamic closure, effective units and coarse-graining. This is the user's working hypothesis, not independent scientific evidence.

**[P2]** User's `ASTELIA_IMPLEMENTATION_PLAN_STANDARD.md`, v3, 26 September 2026, read in full from the Library. Research specificity, target-over-legacy policy, one-plan execution, batched tests and separate review. The root file of this name was not present in the inspected Astelia repository; this standard is not an imaginary repository dependency.

**[R1]** Fritzke, *A Growing Neural Gas Network Learns Topologies*, NeurIPS 1994. [Original paper](https://proceedings.neurips.cc/paper_files/paper/1994/file/d56b9fc4b0f1be8871f5e1c40c0067e7-Paper.pdf). Original algorithm inspected, including the algorithm page.

**[R2]** Zhou et al., *Learning with Local and Global Consistency*, NeurIPS 2003. [Publication](https://papers.nips.cc/paper_files/paper/2003/hash/87682805257e619d49b8e0dfdc14affa-Abstract.html). Nearby method for graph smoothing, not an implementation claim about GeoMind.

**[R3]** O'Keeffe, Hong and Strogatz, *Oscillators that sync and swarm*, Nature Communications 8, 1504 (2017). [Article](https://www.nature.com/articles/s41467-017-01190-3).

**[R4]** Scellier and Bengio, *Equilibrium Propagation: Bridging the Gap Between Energy-Based Models and Backpropagation*. [Primary preprint](https://arxiv.org/abs/1602.05179). Relevant for local relaxation and its gradient interpretation.

**[R5]** Stern, Hexner, Rocks and Liu, *Supervised Learning in Physical Networks: From Machine Learning to Learning Machines*, Physical Review X 11, 021045 (2021). [Article](https://link.aps.org/doi/10.1103/PhysRevX.11.021045), [preprint](https://arxiv.org/abs/2011.03861). Relevant physical-learning precedent; not a demonstration of this proposed digital implementation.

**[R6]** Bordes et al., *Translating Embeddings for Modeling Multi-relational Data*, NeurIPS 2013. [Publication](https://papers.nips.cc/paper/5071-translating-embeddings-for-modeling-multi-relational-data).

**[R7]** Ross, Gordon and Bagnell, *A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning*, AISTATS 2011. [Publication](https://proceedings.mlr.press/v15/ross11a.html).

**[R8]** Agarwal et al., *Deep Reinforcement Learning at the Edge of the Statistical Precipice*, NeurIPS 2021. [Authors' evaluation project](https://agarwl.github.io/rliable/).

---

**Final rule:** a small faithful experiment with a negative result is better than a large successful demonstration that tests a different theory. For the recursive claim specifically, **a resonator must be able to become a part of another resonator under the same rule, while remaining internally alive**; otherwise we have geometric organization, not the hierarchy proposed by RRG.

## Local C1 execution record

**R004 rework after the reviewer's self-recheck:** R004 (`geomind-c1-r4-004`) is REVIEW_READY; its author is the reviewer of R002 and R003, so independent acceptance is pending. The recheck found R003 global by construction: full-observation input, `_prepare`, global re-gauge, a global certificate and whole-snapshot hashing ran inside every update. It also found an unfair comparison against fresh recompute, no fallback arm and no registered endpoints. R004 changes the design:

- the candidate keeps in-memory incremental state and takes additive deltas;
- degree upkeep reproduces the C0 `bincount` bit for bit;
- every mutation is journaled for exact rollback;
- one 100,000-operation cap covers all in-memory work;
- only the smaller frame translates on a merge;
- a local certificate, with a soundness argument and an invariant check, covers every node whose force may change;
- a separately capped (5M) warm-started CG fallback forms a distinct arm;
- export and load stay global and C0-validated.

Endpoints were registered in the manifest before the panel, which used seeds from 10,000,000 and five worlds per cell.

R004 verification: fourteen checks PASS; 80 interventions in 83.9s, all six gates PASS.
- **Queue arm:** 60/60 non-contradiction updates commit correctly (maximum error `3.96e-11`), all with zero relaxation steps. 20/20 contradictions, at every size, exhaust the cap with byte-identical rollback.
- **Fallback arm:** 80/80 correct (maximum error `6.29e-9`). The fallback uses 7.0–7.8× fewer operations than a fresh sparse-LS solve but is slower end to end after exhausting the queue.
- **Scaling:** consistent-edge work goes from 27 to 36 operations between 32 and 2,048 nodes; at 2,048 nodes, in-memory updates take 0.4–0.9% of a fresh recompute's time.
- **Registered verdicts:** H-L is SUPPORTED_WITHIN_SCOPE for consistent additive in-memory updates and NOT_SUPPORTED for contradiction resolution by the local queue. Persistence is global by design. H-P remains INCONCLUSIVE.
- **Mutation probe:** 18/23 defects caught; the survivors are compensated backup guards.

Evidence: `evidence/c1_r004/`; review: `evidence/c1_review/CLAUDE_ACCEPTANCE.md`.

**R003 repair after the Claude review (historical, superseded by R004):** R003 is REVIEW_READY; independent acceptance is pending, and the reviewer who found the R002 issues wrote this repair. R002 seeds only relabeled one fixed geometry per size/intervention, the same geometry R001 used. Its post-inspection frame-initialization redesign was therefore never evaluated on new data. Generator v3 draws grid widths, position jitter, consistent chord cycles, intervention endpoints and the contradiction vector per seed, with three worlds per size/intervention (seeds from 9,000,000). Algorithm/schema v3 commits after one passing certificate of the quiescent workspace; R002 repeated it ten times on unchanged coordinates. Nodes flagged by a failed certificate take one forced step. R002 artifacts migrate explicitly. Refused updates no longer report prior-state answers as coverage, and every case compares update time with a fresh recompute. Two added checks pin exact visit charging, duplicate-copy removal, real R002 migration and evaluator negative controls. The custom-tolerance check now requires real relaxation.

R003 verification: twelve checks PASS; 48 interventions in 40.36s, all six gates PASS. All 36 consistent-edge, new-node and bridge updates commit correctly (maximum displacement error `3.86e-11`), each with zero relaxation steps. All 12 inconsistent edges, including the three 32-node worlds, exhaust the cap and keep byte-identical prior state. R002's single relaxation success did not reproduce on varied geometry. No commit was faster than a fresh recompute (2.6–17.9× slower): dynamics take milliseconds, but whole-state preparation, serialization and hashing dominate each transaction. Evidence: `evidence/c1_r003/`; review and focused checks: `evidence/c1_review/CLAUDE_ACCEPTANCE.md`, `evidence/c1_claude_review/`. H-P/H-L remain INCONCLUSIVE, and the H-L evidence in this panel is unfavorable.

**R002 review repair (historical):** R002 REVIEW_READY at the time; superseded by R003. Historical R001 below is retained unchanged as evidence, not the current implementation. R002 registers algorithm/schema v2 and fresh seeds starting at 8,000,000. Added public constraints initialize rigid translations of existing components and singleton new nodes; all initialization edge reads share the unchanged 100,000 dynamic-visit cap. Existing internal answers are preserved by these frame translations; contradictory cycles still require the same residual relaxation. Ten focused checks cover chained/cyclic/duplicate updates, historical migration, custom stopping tolerances, overflow and strict report/evaluator qualification. The complete scoped batch preceded its consolidated verification phase.

R002 verification: ten checks PASS in 1.42s; 16 fresh interventions complete in 7.28s, all six engineering gates PASS. Thirteen updates commit: every consistent edge, new node and bridge at all sizes, and the 32-node inconsistent edge. The three inconsistent edges at 128/512/2048 nodes remain explicitly unresolved with byte-identical retained states. All 16 independent sparse references converge. Maximum committed displacement error is `5.60e-8`, maximum energy gap `3.47e-15`, and 159/159 excluded cross-component pairs abstain. Evidence is `evidence/c1_review/`, with 19 source inputs, all three states per intervention, per-query answers, exact contract provenance, review findings and post-run artifact integrity checks. The initial check failures and their exact source are retained in `evidence/c1_review_prechecks/`; they preceded final-world execution. Accepted C0 inputs and historical C1 evidence remain unchanged.

H-P/H-L remain INCONCLUSIVE. The frame initialization improvement uses declared constraints and preserves the residual law; it is not adaptive task learning. Global input preparation, coordinate translations and convergence certificates remain visible overhead. The queue still cannot resolve three inconsistent cases under the cap. R001/R002 have different seeds and evaluator coverage, so their timing difference is diagnostic rather than a paired performance claim. C2 and hierarchy work remain unimplemented, pending the separate C1 review.

**Historical R001 record:**

C0 R003 independently accepted on 1 October 2026; see `evidence/c0_review/ACCEPTANCE.md`. C1 is REVIEW_READY, not independently accepted. Current scope is the four specified additive interventions at 32, 128, 512 and 2,048 nodes, a 100,000 dynamic edge-visit cap, and explicit rejected-update retention. No C2 or hierarchy implementation begins here. All 12 accepted C0 inputs remain unchanged. C1 uses exact saved geometry compiled from public exposed constraints as a shared, declared initialization; compilation, gauge conversion, load and save costs are metered rather than attributed to the incremental learner. A separate sparse least-squares reference is qualified against the existing dense reference at small sizes to avoid large dense SVDs.

Registered `geomind-c1-r4-001`: seven focused checks PASS in 3.64s; 16 interventions complete in 24.76s, all four engineering gates PASS. Four consistent-edge updates and the 32-node inconsistent-edge update commit; the remaining 11 exhaust the cap, retain byte-identical fork snapshots and remain explicitly unresolved. Every fresh least-squares reference converges. Maximum committed displacement error is `5.36e-8`; maximum energy gap is `3.25e-15`. Retention, query immutability and artifact reload pass in all cases. Exact source snapshots, per-query answers, costs and before/after states are in `evidence/c1/`; separate review handoff is `evidence/c1/HANDOFF.md`.

H-P and H-L are INCONCLUSIVE: this panel establishes additive transaction correctness or safe refusal, without an adaptive-versus-frozen task-learning comparison or computational locality advantage. The active queue does not resolve most interventions within the cap, and preparation and convergence certification include global scans. Faster native execution could reduce time per operation but would not by itself repair edge-budget exhaustion. No settings were retuned after inspecting final cases; no fallback arm, JavaScript viewer or C++ port was added.
