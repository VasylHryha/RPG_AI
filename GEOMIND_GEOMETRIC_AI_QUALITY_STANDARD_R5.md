---
title: "GeoMind — source-aligned research and quality standard"
revision: R5
date: 2026-10-02
supersedes: "R4 for future work only; accepted history remains bound to its original protocols"
source_basis: "Pinned RRG v0.2.1 audited publication companion and owner alignment handoff"
status_authority: STATUS.json
---

# GeoMind R5

This revision carries the owner's current research interpretation into future
experiments. R4 remains unchanged. No accepted measurement or historical hypothesis
verdict is reassigned. The complete source release is pinned byte-for-byte and
verified in [CURRENT.md](research/rrg/CURRENT.md). The owner
[handoff](docs/RRG_V0_2_1_ALIGNMENT_HANDOFF.md) and direct reading of audited README,
04, 05, 07, 08 and foundation ERRATA ground this guidance. Decision
[0012](docs/decisions/0012-align-geomind-to-rrg-v0.2.1.md) records the alignment scope.

## 1. Authority and interpretation

Authority descends from explicit current owner decisions, unchanged foundation
definitions as confirmed by the audited release, current audited RRG publication
and interpretation, this quality standard and accepted decisions, registered
proposals/manifests, implementation, then historical drafts and reviews. Lower
items cannot silently narrow a higher requirement. Expected hashes alone do not
establish access to a source. Pin the actual bytes in `research/rrg/v0.2.1/`, verify
them against the owner identities and release MANIFEST, and read the source before
source qualification. Later releases get new version directories.

RRG's local object is `R_n = (G_n, M_n)` with `G_n ↔ M_n`. Geometry includes
relations, connectivity, position, orientation and boundary conditions. Mode may
include phase, amplitude, propagation, response, coupling and timescale. A scalar
frequency model is a declared projection. A persistent cluster alone does not
establish two-way causal closure.

The forward source hypothesis is `B_n → R_n → B_{n+1}`, repeated when the dynamics
permit it. Define B prospectively as the model's measurable environment, not as
features selected after a group forms. Separate the dynamical change
`(B_n, R_n, interactions) → B'_n` from the descriptive reduction of that changed
system into B at the next description level. Publishing a coarse node is an
interface operation; it does not physically create a unit or transform a background.

The same abstract operation may have different effective equations. Using one
procedure at every tested level remains GeoMind's anti-cheating constraint
(decision 0007). Same-law closure is a stronger separate endpoint. Larger sizes,
slower dynamics, continuing depth and permanently distinct deeper identities are
not universal prerequisites. Measure branching, coexistence, shrinkage, termination
and reorganization. Physical examples do not impose literal force laws on the AI model.

## 2. Claim ledger

Each claim has its own evidence and verdict. No claim automatically inherits
another claim's verdict. Verdicts are SUPPORTED_WITHIN_SCOPE, NOT_SUPPORTED,
INCONCLUSIVE or NOT_TESTED. An implementation acceptance is a separate judgment.

| ID | Claim | Required evidence | Insufficient evidence |
|---|---|---|---|
| H-M | Geometry↔mode closure | Separate causal interventions in both directions and complete matched ablations | Static graph, synchronized clump |
| H-U | Effective-unit formation | Persistent collective state, recovery, live direct parts and causal collective response in full dynamics | Evaluator-created labels or publication alone |
| H-COMP | Staged recursive composition | Accepted units compose into accepted units over at least two transitions | Full source/background recursion |
| H-BG | Background transformation | Formed structure changes a predeclared environmental response through an isolated causal path against both formation and backreaction controls | Descriptive reduction or any unpaired time change |
| H-PS | Changed possibility set | Same later candidate population and detector have a registered formation/persistence change under intact versus both control backgrounds | Moving already-formed units into a fixture |
| H-RBG | Recursive background generation | At least two causally qualified B→R→B turns linked in one model family, with H-BG/H-PS evidence and live underlying state | One transformation, staged hierarchy, same-law closure |
| H-PRED | Effective prediction | Published higher state predicts held-out full-system response within registered bounds against strong controls | Resonator existence |
| H-AI | Task usefulness | Declared task improves against strong matched baselines on held-out cases | Mechanism, stability or persistence alone |
| H-EFF | Computational/energy efficiency | Matched total cost improves with all overheads, named cost units and uncertainty | Fewer visible nodes or cheaper upper query alone |

Historical IDs keep their original meaning in historical receipts. In particular,
R4 H-U meant tactical usefulness, while R5 H-U means effective-unit formation;
R4 H-C covered composition/prediction, and R4 H-E meant hardware energy. New receipts
must include `claim_schema: geomind-r5` and explicit definitions. Do not relabel old
H-U/H-C/H-E verdicts. R4 H-R/H-D/H-P/H-L remain bounded historical research claims;
future reuse must state their definitions and protocol. GeoTactics stays a separate lane.

H-COMP may pass with H-BG untested. H-BG may pass without a later formation
consequence, leaving H-PS unsupported/inconclusive. H-PRED may pass while total cost
fails. Failure of one computational realization does not disprove universal RRG.

## 3. Forward milestone map

This is a research map, not milestone status or authorization. STATUS.json alone
records lifecycle state; the README table is generated from it.

| Milestone | Bounded research purpose | Claim scope |
|---|---|---|
| C0 | Structural representation/reference | Historical accepted scope |
| C1 | Incremental/local updates | Historical accepted scope |
| C2 | Geometry/activity learning | Historical acceptance and stopped task branch |
| C3 | Old learning-stability branch | Deprecated history; no new authorization |
| C4 | Local G↔M resonator | Historical accepted bounded closure |
| C5 | First effective-unit transition | Historical acceptance; prediction/composition remains bounded as recorded |
| C6 Arm A | Two staged composition transitions | H-M, H-U, H-COMP; independent H-PRED |
| C6 Arm B | Causal background change, later-formation assay, repeat once | H-BG, H-PS, H-RBG with separate turn verdicts |
| C7 | Perturb, dissolve, survive, reform after a qualifying mechanism | Separately approved robustness claims |
| C8 | Usefulness, prediction, compression, total matched cost | H-PRED, H-AI, H-EFF |
| Later | Transfer, language, hardware energy | Separate approvals and held-out evidence |

If C6 B is deferred, assign a separate milestone before execution and rename C6
to staged recursive composition. Arm A alone never warrants full source-recursion
language. Later milestones do not start automatically after a mechanism succeeds.

## 4. State ownership, interfaces and normalization

One owner evolves full state; the evaluator owns hidden truth and memberships.
An upper-facing ActiveUnit exposes X (position), L (size), M_eff (mode summary),
boundary ports and S (validity/error). R5 adapters may retain the existing C5
ResonatorState field set. Owner-private member lists and descendant state are not
an upper prediction API. A viewer consumes read-only outputs and owns no dynamics.
Numerical kernels may use Python/NumPy or a qualified C++ implementation; JavaScript
is limited to presentation. No framework/game integration is authorized here.

For each quantity state its units, measured level, estimator, normalization,
censoring and access owner. Apply one detector, promotion and effective-model
recipe per arm at all repeated levels/turns. Measure time and length scales;
dimensionless cuts cannot be hand-tuned by level. Composition from child summaries,
scale ratios and lawful up/down transmission are allowed. Unmeasurable normalization
is a stop, not an invented value. Requirements are fixed before final outcomes.

Promotion never deletes full active elements. Direct-part validity vetoes promotion;
deeper diagnostics cannot veto merely because organization changed (decision 0010).
Each accepted candidate gets one finite, valid publication per world linked to
that candidate's S/digest. Degenerate hulls cannot certify distinctness. Published
natural rates and inherited port capacities need full-versus-coarse qualification
before predictive claims. Invalid coarse states abstain or reopen from an explicit
owner service; open-loop evaluation receives no later full-state refresh.

## 5. Causal design and experimental validity

Arm A can stage already-formed units, provided it reports that restriction. Arm B
must define the background, probe locations/schedules, treatment law, later candidate
population, directional effects and margins before final seeds. Required matched
conditions are INTACT, NO-R (formation closure ablated) and NO-BACKREACTION (the
source-to-background path disabled while preserving local structure as far as possible).
Report B_before and every B_after, costs and treatment side effects. A sham that
destroys the resonator cannot isolate its backreaction. Constituent drift is not
evidence of a formed resonator changing the background.

Expose identical unformed candidate states to the resulting backgrounds. Detector
inputs exclude expected groupings and condition names. Keep later formation and
background endpoints separate. A second turn must inherit the changed first-turn
world; restaging a new fixture is insufficient. A new directed/masked law is a
new model projection requiring qualification, never a modification of frozen C4.

Numerical convergence, symmetry/decoupling checks and analytic or independent
references precede causal claims. Permutations and coordinate transformations
that preserve the problem should preserve answers. Ablations must remove the
complete path named by the claim; sham/confounding checks are engineering gates.
Typed invalid states/nonconvergence stay visible and cannot silently become passes.

## 6. Seeds, uncertainty, cost and evidence

Training/development, smoke and final entropy are disjoint. World/source isolation
prevents shared harvested randomness from becoming pseudo-replication. Average
multiple candidates/probes within a world; frames are not independent trials.
Predeclare primary endpoints, practical margins, aggregation, multiple-comparison
handling, missingness and interval rules. Preserve raw calibration data. No optional
stopping, final-result tuning, rehearsal panel or repeated successful run for the
same code. A clean negative outcome is valid research.

Strong conventional baselines receive the same information and budgets. Report
construction, calibration, fitting, updates, failed formation, harvesting, topology
search, prediction, fallback/reopening, storage, serialization and I/O costs.
Distinguish online savings from total work. Report amortization only if per-query
savings are positive. Hardware energy requires real matched hardware measurement;
runtime, sparse state and simulation counts are not energy evidence.

Receipts bind source commit/hashes, source pins, claim schema/scope, immutable
manifest, generator/seed inventory, fit/calibration choices, normalization, owner
boundaries, controls, per-world raw outcomes, uncertainty, costs and limitations.
Every registered endpoint appears in endpoint_coverage with value/verdict or
not_run/reason, including diagnostics. No operational result implies intelligence.

## 7. Lifecycle and stops

Follow AGENTS.md: propose → owner approval → committed registration before final
seeds → new-file implementation → one ordered gated pipeline → committed evidence
→ one review by the other model family → status/acceptance or fresh revision.
Complete all edits before a long run. Everyday tests follow code changes;
documentation-only work uses affected status/hash/freeze checks. Do not run old panels.
An implementer design defect withdraws the revision through a decision without
changing recorded evidence. Frozen predecessors require new adapters/requalification.

| Yes/no stop condition | One action | Responsible role |
|---|---|---|
| Exact audited source missing/mismatched? | Obtain and qualify the release before execution | Drafter |
| Proposal not owner-approved? | Await approval of the completed proposal | Drafter |
| Protocol cannot implement its registered causal path? | Return the design to the owner | Implementer |
| Gate, normalization, numerical or receipt coverage check fails? | Report the block to the owner | Implementer |
| Runtime projection exceeds the approved budget or is unknown? | Return the measured budget decision to the owner | Implementer |
| Recorded design defect discovered? | Withdraw through a decision preserving evidence | Implementer |
| Independent review requires changes? | Report CHANGES_REQUIRED for a fresh revision | Reviewer |
| Simpler baseline dominates registered task quality/total cost? | Decide the bounded branch's next action | Owner |

No milestone status is assigned by this document. No future proposal is approved
by copying the standard. The next concrete design is `experiments/c6_proposal_r3.md`;
its source prerequisites and owner decisions must be resolved before execution.
