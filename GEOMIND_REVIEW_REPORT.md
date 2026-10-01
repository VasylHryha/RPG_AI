# GeoMind / GeoTactics — adversarial review receipt

**Date:** 1 October 2026  
**Review outcome:** replace the previous two plans; retain the experimental goal, repair the validity/design gaps.  
**Implementation outcome:** no GeoMind or GeoTactics implementation accepted by this review.  
**Scientific outcome:** broader geometry/RRG hypotheses remain untested.

## What was reviewed

- `GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R2.md`, 1,819 lines, read in full.
- `GEOMIND_GEOTACTICS_ASTELIA_EXPERIMENT_PLAN.md`, 850 lines, read in full.
- The user's original Library `02_scientific_framework.md` definitions and central RRG propositions; not a new audit of every physics addendum.
- The user's `ASTELIA_IMPLEMENTATION_PLAN_STANDARD.md`, v3, 26 September 2026, read in full.
- Critical sandbox source at `VasylHryha/astelia-hunte@11df55f6bc478bfe5b48f095a02f4b70225b3ab6`: copy/rollout lifecycle, commander and its mutable reads, guard writes, root instructions and the Formation plan's status.
- The earlier source review supplied the rest of the sandbox/script/consumer context. A fresh full native-game audit was not performed.
- Remote `main` was observed at `67b929c886d8f7ab9900440bd7fcc582cf2dd521`; the one intervening commit did not change the sandbox.
- Primary research concerning GNG, graph smoothing, physical coupled learning/equilibrium propagation, swarmalators, sequential imitation and evaluation. The revised documents contain the primary-source register and adoption/limitation decisions.

## Main findings and their resolution

Severity below is an engineering/research judgment, not a measured score. P0 means a validity or central-meaning blocker; P1 means an important design/interpretation gap.

| Finding | Severity | Why the old version could mislead | Resolution in the replacements |
|---|---|---|---|
| RRG reduced to a static prototype map | P0 | No temporal geometry–mode feedback or recursive abstraction was present, yet the connection was overstated | Separate H-R/H-D/H-P/H-L/H-M/H-C/H-U/H-E claims; add a tiny local-response/weighted-geometry core learning probe; leave full recursive theory explicitly untested |
| “Math versus geometry” false distinction | P0 | Geometric algorithms, gradients and graphs are mathematical; local dynamics can also implement optimization | State mechanism boundary precisely; disclose known learning-algorithm relationships |
| Weak structural-inference reference | P0 | Exact offsets can be compiled once into coordinates; beating repeated graph traversal proves little | Mandatory compiled-coordinate and least-squares baselines; require identifiability and honest query coverage |
| Incompatible query/ablation gates | P0 | A direct-coordinate answer was required to benefit from propagation it never uses | Mechanism-specific ablations, consistent symmetry tests, and predictive interventions |
| Existing teacher described as honest | P0 | Enemy configuration and decision memory survive `continue/rush` copying | Public-snapshot-built hypotheses, explicit privileged diagnostic and leakage fixtures |
| Fork isolation/continuation defects | P0 | Shared mutable guard state, dropped dead-source projectiles and reset memory can change training labels | Exact snapshot contract, retained release provenance, deep reference remapping and structural/behavioral tests before fitting |
| Controller name changes execution | P0 | `geo` could lose reactive-only options; rollout had different dwell rules | Selector/profile split, common friendly action contract, explicitly separate enemy catalogues |
| Observations omit important state | P1 | Same proportions/centroids can hide health, split threats, readiness, incoming shells or current execution state | Typed public snapshot, explicit features, masks, self-state, alias fixtures; no claim compression is sufficient |
| Locality claim omits lookup | P1 | A small graph walk may follow a full O(Md) scan | Complete acquisition/retrieval/dynamics/update accounting; full scans allowed but disclosed |
| kNN labeled both optional and essential | P0 | A claimed special geometry gain could vanish under a trivial omitted control | kNN, same-prototype and fixed-graph diffusion required before expensive qualification |
| Frozen-memory reset misinterpreted | P1 | Reloading the same frozen map should not remove a persistent learned policy | Frozen-reset invariance; continual-memory controls reserved for adaptive experiments |
| Raw damage treated as online causal feedback | P1 | Previous plans/projectiles and action gates can cause the measured reward | Online tactical learning is a separately designed later protocol, not a one-line automatic extension |
| Split leakage and correlated samples | P0 | Adjacent frames treated as independent; changed test data reused; developer-known opponents called unseen | Whole-scenario grouping, training-only aggregation, immutable manifests, multiple fits and paired uncertainty |
| Gauntlet statistics / timeout wins | P1 | Surviving long enough to meet an opponent biases its results; outcome helpers differed | Single outcome taxonomy; fresh fights versus conditional gauntlet results separated |
| V3 described as current execution | P1 | The inspected plan says V2 is production and V3 remains unfinished | Correct source-status statement; no native cutover implied |
| “Material improvement” without a rule | P1 | Acceptance can be moved after seeing results | Proposed practical margins and resource caps registered before final testing; inconclusive remains valid |
| Too much central design left to implementation | P1 | No exact diffusion/metric/cap/missingness/action-lifetime rules | Chosen algorithms, lifetimes, migration map and complete milestones in one tactical plan |

## What was actually executed

The review bundle contains:

- `evidence/fork_excerpt.cjs`: faithfully transcribed `fork()` from the inspected simulator plus its RNG helper. This is not a full repository checkout or the entire simulator.
- `evidence/fork_probe.cjs`: small fixture-only characterization. It can also import the real local `formation_sim.js` via a supplied path.
- `evidence/fork_probe_results.json`: actual Node v22.16.0 execution results.

Command executed in the working environment:

```bash
node evidence/fork_probe.cjs > evidence/fork_probe_results.json
```

**Observed: all eight expected legacy properties reproduced.** Three describe one related guard-alias problem; two describe projectile-copy filtering. They are not eight independent production defects and are not eight successful safety assertions.

| Observation | Result | Limit |
|---|---|---|
| Guard Set shared across copies | Reproduced | Structural test, not battle execution |
| Guard points at original actor | Reproduced | Same root cause as shared Set |
| Writing via child guard changes original actor | Reproduced | Direct fixture write demonstrates reachability; no formation tick executed |
| Live shell from dead/removed source dropped by fork | Reproduced | Did not measure a win-rate effect |
| Live direct shot from dead/removed source dropped by fork | Reproduced | Separate appropriate dead ranged source used in fixture |
| Lure state reset | Reproduced | Shows approximation rather than exact continuation |
| RNG is reseeded rather than continued | Reproduced | Can be a legitimate declared rollout assumption; not inherently an invalid stochastic method |
| Nested configuration shared | Reproduced | Sharing is safe when the shared data is truly immutable |

The original protection option is off by default. Therefore this review does **not** infer that the published default gauntlet score was inflated by the guard alias. The problem is that the old plan trusted a general clone/teacher contract without proving it.

The probe exits successfully when these *old behaviors* are reproduced. After repairs, its characterization expectations should fail or be replaced by positive contract tests. Do not wire this historical script into CI as a “safe clone” test.

To characterize the actual source in a local checkout without running a battle:

```bash
node evidence/fork_probe.cjs /absolute/path/to/astelia-hunte/experiments/formation_sandbox/formation_sim.js
```

### Not executed

No full simulator parity run; no complete gauntlet; no teacher quality or timing comparison; no GeoMind training; no test of the newly specified core learning rule; no browser qualification; no native Godot test; no remote commit or push. None is implied by this receipt.

## What changed in the final document pass

The second pass on the replacement documents tightened additional details: a true fixed Euclidean feature embedding with explicit missingness channels rather than a potentially nonmetric pairwise-deletion distance; separate friendly versus scripted-enemy action vocabularies; an explicit public replacement for the private `pinned` check; bounded training collection; five fitting passes; and a small preselected rollout panel instead of multiplying expensive rollout evaluation by every fitting seed.

The full candidate remains deliberately modest. GNG and finite graph diffusion are recognizable established methods. A separate 16-node adaptive relaxation core experiment makes local response-driven memory concrete, while explicitly acknowledging its equilibrium-propagation/physical-learning lineage. Neither is presented as proof that RRG is a new physical law or that it replaces modern AI.

## Files to use now

1. **`GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R3.md`** — replaces the previous shared standard in full. The core ladder starts at C0; the stronger C2 learning mechanism is precisely specified but not run.
2. **`GEOMIND_GEOTACTICS_ASTELIA_EXPERIMENT_PLAN_R2.md`** — replaces the previous tactical plan in full. Contains the single tactical status table, architecture, source findings, selected algorithms, all milestones, tests and operating prompts.
3. This receipt and `evidence/` — review evidence, not competing execution instructions.

The preceding two Markdown files remain unchanged in the conversation history as historical artifacts. Do not use them alongside the replacements as active instructions. File hashes in the bundle manifest identify the exact delivered revisions.

## Next action

For the Astelia sandbox: **GT0 only — trustworthy snapshots and a single decision boundary. Do not start training yet.**

For the standalone geometry project: **C0 — a small reference experiment with the compiled baseline included.** The core and tactical lanes may proceed independently; neither can certify the other's theory claims.

A 9/10 planning target means no known central design omission disguised as an implementation task. It does not mean a guaranteed successful scientific hypothesis. This review makes the unresolved scientific questions visible rather than assigning an unsupported numerical certification.
