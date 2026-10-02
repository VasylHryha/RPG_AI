---
title: "RPG_AI — RRG v0.2.1 Alignment and Forward Execution Handoff"
doc_type: alignment_and_execution_handoff
revision: 1
updated: 2026-10-02
repository: VasylHryha/RPG_AI
reviewed_repository_head: e2e7201eccf4f377cc4185b8370f392149bd662c
rrg_release: "v0.2.1 audited publication companion — 2026-10-02"
status: READY_FOR_ALIGNMENT_REPAIR_AND_C6_R3_DESIGN
execution_rule: "Align authority/status/design first; do not run a C6 development gate or panel until the replacement proposal is owner-approved."
---

# RPG_AI — align GeoMind with current RRG v0.2.1, then move forward

> **Purpose:** keep the good experimental discipline already present in RPG_AI, preserve accepted evidence, remove source/meaning drift, and make the next GeoMind experiment test the current RRG idea rather than a narrower older interpretation.

This file is a **forward handoff**, not a new theory document and not a claim that RRG is proven. It is intended to be placed in the RPG_AI repository (recommended path: `docs/RRG_V0_2_1_ALIGNMENT_HANDOFF.md`) and given to Codex/Claude before further C6 work.

The repository was reviewed at:

```text
VasylHryha/RPG_AI
main = e2e7201eccf4f377cc4185b8370f392149bd662c
```

The current RRG reference set is:

```text
RRG v0.2.1 audited publication companion
2 October 2026
```

The current audited package preserves the foundation definitions but adds/clarifies a central source-direction layer:

\[
R_n=(G_n,M_n),\qquad G_n\leftrightarrow M_n
\]

and

\[
\boxed{B_n\rightarrow R_n\rightarrow B_{n+1}}
\]

with repeated organization:

\[
B_0\rightarrow R_0\rightarrow B_1\rightarrow R_1\rightarrow B_2\rightarrow R_2\rightarrow\cdots
\]

The important update for GeoMind is this:

> **Recursive composition of resonators is a relevant component of RRG, but hierarchy/coarse-graining alone is not the whole current RRG source mechanism. A formed structure must be allowed to physically alter the effective background/conditions, and a later organization must be tested in that changed background.**

---

# 0. Do not destroy the useful work already done

The current repository is not a failed toy project. Preserve its strongest properties:

- accepted evidence is immutable history;
- failed or inconclusive hypotheses remain visible;
- implementation acceptance and hypothesis support are separate;
- controls and ablations are explicit;
- strong conventional baselines are allowed to win;
- C2 was not “rescued” after linear regression dominated the selected task family;
- C4 directly tests geometry → mode and mode → geometry rather than calling any cluster a resonator;
- C5 tests a bounded first transition from lower resonators to an effective higher unit;
- C6 stopped on a development design gate rather than forcing a successful panel;
- independent cross-family review is retained;
- final-result tuning is prohibited.

**Do not reset C0–C5. Do not rewrite their receipts. Do not reinterpret old evidence to satisfy new requirements.**

Accepted historical claims remain exactly as scoped when accepted. A newer RRG interpretation changes what we test next; it does not retroactively manufacture or erase experimental results.

---

# 1. Scientific/source authority after this alignment

Use the following hierarchy for future GeoMind work.

## 1.1 Authority order

```text
1. Explicit current owner decisions
2. Stable RRG foundation definitions where the current audited release says they are unchanged
3. Current audited RRG v0.2.1 publication/interpretation documents
4. GeoMind quality standard and accepted decision records
5. Experiment proposals/manifests
6. Implementation code
7. Historical drafts, old reviews and archived RRG material
```

A lower item cannot silently narrow or redefine a higher item.

## 1.2 Current RRG v0.2.1 files to pin

Vendor or otherwise pin an exact read-only copy of the current audited source set into the repository. Recommended location:

```text
research/rrg/v0.2.1/
```

At minimum include these exact current files:

| Path in v0.2.1 package | SHA-256 |
|---|---|
| `README.md` | `0f5c2daaf6be3f3fac88832d566408ea6cdc2c16c42b397c448af83a8af418e7` |
| `04_recursive_background_generation.md` | `e87a91d6ada03000bf231ebddc6eca0b4c6f31798b5588ebc79c904e69697f47` |
| `05_mathematical_source_model.md` | `659e8640c91cb21815f32c45fb6cef9ddda302205cf20027607303721ee9bfab` |
| `06_evidence_catalog.md` | `1306d8e0f86c3c25a09037dadbde0f140f9df30199b89e684f9bc71a6c96a5dc` |
| `07_audit_report.md` | `222487df50faa457b85d5748a846f728f2c4fd9845b4a33ffac181d6e45ebfa7` |
| `08_claim_coverage.md` | `b63eaf69ec9f62085bdafb97536c642eb9d8ea8d2d5f09a377c4fbe28c04568e` |
| `CHANGELOG.md` | `b477cf252760dc2bac3b57202df23383ab2811117b65ec610e21e5ac475f91d2` |
| `foundations/01_world_explanation.md` | `a3c4f376d4a81bf8fc158d3c786c92e5c88b454aeead88173c4139420f4bbddb` |
| `foundations/02_scientific_framework.md` | `269b6e4bd7c76e15f19f4c0ff752276ba2a1de76e0b84294516d2d3ef8c998c5` |
| `foundations/03_mathematical_core.md` | `57d1aaa129d7edb780b83886b8b8ede40f7b30cf77a2d6b1f400c651ad1f92e4` |
| `foundations/ERRATA.md` | `d01091bbc9fec01e1cb7ad16763b344849747b27b32b6e378d5f04d02e65b58f` |
| `MANIFEST.json` | `ee60e0ffc5134596549a5cdc6f6faf6088db62effce5ca34b389036365009f02` |

Prefer copying the complete current release rather than only the minimum list if repository size is acceptable. Preserve the bytes. A later RRG release belongs in a **new version directory**; do not overwrite v0.2.1 history.

## 1.3 How the older locked core should be treated

Existing RPG_AI decisions reference an older project-wide locked-core hash:

```text
b6d3e7c75285889afe94cabf083ba5fb80f401c656613ba6a80d2f0149b655e1
```

Do **not** delete that history. The v0.2.1 audit says foundation definitions remain continuous. However, the old locked-core reading is no longer sufficient by itself to define the forward research program.

Use it for definition continuity where compatible with v0.2.1, not to override the current v0.2.1 source-direction clarification.

Specifically, do **not** infer from old text that:

- the same equation family at every level is the definition of RRG;
- a coarse-graining operation physically creates a new level;
- recursion is proved by a nested clustering tree;
- higher levels must always be larger or slower;
- deeper internal identities must remain byte-for-byte/distinct forever;
- a staged hierarchy alone establishes the current `B_n → R_n → B_{n+1}` source mechanism.

---

# 2. Current RRG interpretation that GeoMind must preserve

## 2.1 Local closure remains core

A GeoMind resonator must retain the two-way relationship:

```text
geometry / relationships → supported dynamics/modes
active dynamics/modes → maintain, restore or transform geometry
```

A persistent cluster without measured two-way causality is not enough.

Existing C4 design is useful precisely because it tests both directions and matched ablations.

## 2.2 Mode is not scalar frequency only

Do not reduce `M` to a single Hertz-like number. It may include phase, amplitude, response, propagation, coupling and timescale.

GeoMind may use a restricted mode representation in a particular experiment, but the proposal must say it is a model projection, not the universal definition.

## 2.3 New effective unit is real only when underlying dynamics support it

Promotion/coarse-graining is a **description and interface operation**. It does not by itself prove physical formation.

The higher object must have a persistent, causally meaningful collective state in the full lower-level dynamics.

## 2.4 Source/background recursion is now central

The missing forward question is not merely:

```text
R0 → R1 → R2
```

It is:

```text
B0 → R0 → B1 → R1 → B2 → R2
```

where a realized `R_n` measurably changes the conditions experienced by later candidates.

For GeoMind, `B_n` does **not** need to be literal physical white noise. It may be the dynamic computational environment available to units at that level: active units, couplings, boundary/port conditions, unresolved lower-level activity, fields/signals, resource/traffic constraints, or other predeclared environmental quantities.

The experiment must define it explicitly.

## 2.5 Physical/environmental change and descriptive reduction are different

Keep two arrows separate:

```text
underlying dynamics:
(B_n, R_n, interactions) → B'_n

model/reduction:
B'_n + realized structures → effective description B_{n+1}
```

A successful summary/predictor is evidence about representation. A measured change in the world caused by a formed resonator is evidence about background transformation. Do not count one as the other.

## 2.6 Same abstract operation ≠ identical low-level equation

RRG v0.2.1 explicitly distinguishes:

- the same **abstract geometry–mode/background operation**, and
- the stronger conjecture that one mathematical equation family remains form-invariant.

Therefore:

- GeoMind may keep “same procedure at both scales” as a strong **anti-cheating experimental constraint**;
- it may test same-law/form closure as a separate stronger endpoint;
- it must not say that identical equation-family closure is required to count as RRG at all.

## 2.7 Levels can coexist, branch, stop, shrink or reorganize

Do not hard-code monotonic hierarchy depth, size or timescale into the theory verdict.

Report:

- formation size,
- timescale separation,
- persistence,
- branch/termination,
- coexistence,

as measured properties unless the experiment explicitly tests a narrower registered prediction.

## 2.8 AI claims remain separate

The current RRG release retains AI as an application hypothesis. It does **not** establish intelligence, transfer or efficiency gains.

GeoMind must therefore keep these claim levels separate:

```text
mechanism exists
≠ useful prediction
≠ learning advantage
≠ transfer/generalization
≠ computational efficiency
≠ hardware energy advantage
≠ intelligence
```

C8/its successor remains the correct place for usefulness/compression claims against strong baselines.

---

# 3. Repository findings that must be repaired before the next C6 run

## 3.1 `AGENTS.md` is scientifically stale

It currently reduces the owner requirement to a frequency → geometry loop repeated at a larger/different scale and says downstream theory examples add no constraints.

Repair it so it says:

1. the local geometry↔mode loop remains required for resonator claims;
2. current RRG v0.2.1 additionally treats background transformation as central to the full source-direction hypothesis;
3. an individual experiment may test only a subset, but must name the subset;
4. physical examples do not impose literal physical-force equations on the AI implementation;
5. current RRG documents can change the interpretation of what a milestone demonstrates without retroactively changing old measurements.

Do not turn `AGENTS.md` into a copy of the theory. Keep the rule concise and link to the pinned v0.2.1 sources.

## 3.2 `STATUS.json` contains a superseded C6 interpretation

The old C6 development STOP measurement stays historical evidence.

But the current status text still says nested C4 overlap violates “lower levels stay alive.” Decision 0010 already corrected that interpretation: direct parts must remain active; deeper organization may transform.

Update the C6 status to state approximately:

```text
BLOCKED / redesign required.
Old development gate stopped under the revision-1 criterion.
The measurements are retained, but decision 0010 supersedes the interpretation
that nested/deeper overlap itself violates the RRG principle.
Current committed C6 code still implements the obsolete nested-veto path.
Replacement C6 proposal is not yet owner-approved or executed.
No H-C/H-M/background-recursion verdict follows from the old gate.
```

Point `proposal` to the active forward proposal only after the owner approves it. Until then record the draft explicitly as awaiting approval.

Regenerate README status using `tools/status.py --write`; do not hand-edit the generated block.

## 3.3 Current C6 code still has the obsolete nested veto

In current `geomind/c6_levels.py`, `recursive_validity()` includes nested child `ok` values in the parent `ok` result.

That conflicts with decision 0010 / Amendment A3.

Do **not** patch this immediately and run the old protocol.

First approve the replacement proposal. Then the new implementation batch must:

- make direct-part validity the promotion veto;
- keep deeper validity as recorded diagnostics;
- preserve all lower elements as dynamically evolving state;
- verify a direct-part failure still rejects promotion;
- verify deeper reorganization alone does not automatically reject the parent;
- preserve old results/receipts unchanged.

## 3.4 `GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md` should become history, not silently mutate

Create a new forward revision:

```text
GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R5.md
```

R5 should supersede R4 as future guidance while preserving R4 because accepted experiments were designed under it.

R5 must add explicit current-source alignment and the background/source-direction claim family described below.

---

# 4. Required claim ledger in GeoMind R5

Keep existing useful claims, but distinguish these at minimum.

| ID | Claim | Meaning | Do not confuse with |
|---|---|---|---|
| `H-M` | geometry↔mode closure | geometry changes mode/response and mode/activity changes geometry | a static graph or synchronized clump |
| `H-U` | effective-unit formation | persistent lower structures form a causally meaningful collective unit | evaluator-created cluster labels |
| `H-COMP` | staged recursive composition | accepted units can compose into another accepted unit for at least two transitions | full source/background recursion |
| `H-BG` | background transformation | a formed structure causally changes measurable environmental/background response | descriptive coarse-graining |
| `H-PS` | changed possibility set | the changed background changes which later organizations can form/persist | merely moving already-formed units together |
| `H-RBG` | recursive background generation | `B_n → R_n → B_{n+1}` succeeds and the operation repeats at least once | same-law closure, bigger/slower hierarchy |
| `H-PRED` | effective prediction | published higher state predicts declared held-out responses within bounds | existence of a resonator |
| `H-AI` | task usefulness | mechanism improves a declared AI task versus strong baselines | stability/persistence alone |
| `H-EFF` | computational/energy efficiency | total matched cost improves | fewer visible nodes or cheaper upper query only |

**No claim automatically inherits another claim's verdict.**

Examples:

- `H-COMP` can pass while `H-BG` remains untested.
- `H-BG` can pass while `H-AI` remains untested.
- `H-PRED` can pass while total efficiency fails.
- a model failure can be `NOT_SUPPORTED` without being a failure of universal RRG.

---

# 5. Replace the forward C6 design before running anything long

Preserve these as history:

```text
experiments/c6_proposal.md
experiments/c6_proposal_r2.md
docs/decisions/0008-approve-c6.md
docs/decisions/0009-c6-stops-at-design-gate.md
docs/decisions/0010-c6-principle-correction.md
all c6 development evidence/reviews
```

Create:

```text
experiments/c6_proposal_r3.md
```

Do not register or run its final panel until owner approval.

## 5.1 What C6 R3 should be

C6 R3 should explicitly contain **two separate arms**, with separate verdicts.

### Arm A — staged recursive composition

Purpose:

```text
C4 units → level-2 effective unit → level-3 effective unit
```

This reuses the useful C6 work and tests `H-COMP`.

Retain the strongest existing requirements:

- label-free formation detection;
- direct parts stay dynamically alive;
- two-way geometry↔mode causality at each promoted level;
- up/down causal transmission;
- finite published interface;
- upper predictor reads only declared higher-level states/ports;
- held-out full-vs-coarse response comparison;
- same procedure at both levels as an anti-cheating constraint;
- same-law closure and timescale separation reported separately;
- strong null/ablation controls;
- no utility/efficiency claim.

State plainly:

> Passing Arm A supports staged recursive composition in this model. It does not establish the full `B_n → R_n → B_{n+1}` source-direction mechanism because the experimenter still stages already-formed units.

### Arm B — causal background transformation and changed possibility

Purpose:

```text
B0 → R0 → changed B1 → altered/new R1 formation
```

This is the missing current-RRG bridge and must test `H-BG` and `H-PS`.

The proposal must define a measurable background state **before looking at final outcomes**.

A background descriptor may include, depending on the selected model:

- response spectrum / susceptibility to declared probes;
- spatial/temporal correlation structure;
- effective coupling/transfer between test ports;
- boundary-condition response;
- unresolved activity/noise statistics;
- reachable stable-state basin under a standardized perturbation;
- other predeclared environmental quantities exposed by the model.

Do not define `B` as “whatever changed after the resonator formed.”

### Required paired causal design for Arm B

For matched initial worlds/seeds, compare at least:

1. **INTACT:** a qualifying resonator forms and continues interacting with the environment.
2. **NO-R / FORMATION ABLATION:** matched constituents/environment but the resonator-forming closure is disabled or prevented by a predeclared ablation.
3. **NO-BACKREACTION / SHAM:** preserve as much local structure as possible while disabling the path by which the resonator changes the measured background.

The exact controls must be chosen from the implemented law and frozen in the proposal.

Measure:

```text
B_before
B_after_intact
B_after_no_R
B_after_no_backreaction
```

`H-BG` needs a predeclared causal difference that survives the matched controls.

### Changed-possibility assay

After the background measurement, expose the **same standardized candidate/probe population** to the intact and control backgrounds.

Use paired seeds/initial states where possible.

The assay must use the same formation criterion in every arm and must not receive the expected grouping/answer.

Measure whether the background change alters at least one predeclared quantity such as:

- probability/rate of later persistent-unit formation;
- lifetime/recovery of a later candidate;
- reachable stable organization class;
- threshold for formation under the same external drive;
- boundary transfer that permits a later unit to close its G↔M loop.

`H-PS` is supported only when the intact background effect changes the later-formation outcome relative to both matched controls with the registered direction/margin.

A descriptive difference in `B` without a later formation consequence supports `H-BG` only, not `H-PS`.

A later formation difference without a measured causal background path is not enough for `H-BG`.

## 5.2 Repeat once before calling it recursive background generation

Do not call one transformation universal recursion.

`H-RBG` requires at least a bounded two-turn chain in one model family, e.g.:

```text
B0 → R0 → B1 → R1 → B2
```

or a deliberately equivalent two-transition operationalization.

The experiment does **not** need to prove indefinite recursion.

If Arm B is too large for C6, split it into a separately numbered milestone **before** execution. Do not hide an unfinished background test inside a “C6 passed” hierarchy verdict.

---

# 6. C6 R3 must avoid these failure modes

Reject or redesign the proposal if any of these are true.

## 6.1 Manual possibility creation

Bad:

```text
form R0 elsewhere
place five R0s in a new fixture
call the new fixture B1
observe R1
```

This is staged composition. It may support `H-COMP`, but not `H-BG`/`H-PS` by itself.

## 6.2 Background defined by the answer

Bad:

```text
B1 = features that best separate worlds where R1 formed
```

Background observables and margins must be fixed before final outcomes.

## 6.3 Coarse-graining counted as physical causation

Bad:

```text
publish an effective node → therefore the environment changed
```

Publishing a summary is not a dynamical event unless the underlying system actually changes through a declared coupling path.

## 6.4 Same-law requirement promoted into theory definition

Bad:

```text
RRG failed because effective equations at level 2 differ from level 1
```

That can fail the optional same-law endpoint. It does not automatically fail the current abstract RRG claim.

## 6.5 Bigger/slower hard-coded as success

Size and timescale may be hypotheses/diagnostics. Do not make monotonic growth a hidden formation criterion unless the owner explicitly selects that narrower hypothesis.

## 6.6 Lower-level deletion used to make hierarchy cheap

Promotion cannot simply replace/delete the underlying active state in the full model.

The coarse predictor may summarize it; the evaluator/full dynamics must still be able to show what exists underneath.

## 6.7 AI usefulness inferred from existence

A stable recursive structure is not automatically useful memory, abstraction or intelligence.

Keep `H-AI` and `H-EFF` for later matched task experiments.

---

# 7. Target forward milestone map

R5 should present the work approximately like this.

```text
C0  structural representation/reference                     ACCEPTED history
C1  incremental/local update mechanism                      ACCEPTED history
C2  geometry/activity learning probe                        ACCEPTED implementation; task branch stopped
C3  old learning-stability branch                           DEPRECATED history

C4  local resonator G↔M closure                             ACCEPTED bounded evidence
C5  first effective-unit composition                        ACCEPTED; composition evidence bounded/inconclusive where recorded

C6  current source-aligned recursion milestone
    A. staged recursive composition                          H-COMP
    B. causal background transformation                      H-BG
    C. changed possibility-set assay                         H-PS
    D. repeat/chain if feasible                              H-RBG

C7  perturb / dissolve / survive / reform                   after a qualifying recursive/background result
C8  usefulness / prediction / compression / total cost      after mechanism works

later
    transfer/generalization
    physical energy/hardware
    language interface
```

If C6 becomes too broad, split B/C/D into a new milestone and explicitly downgrade C6's name to **staged recursive composition**. Do not keep the title “full recursion” while omitting the background source mechanism.

---

# 8. Exact repository change batch before any new long experiment

The next implementation session should perform this **documentation/governance/design batch first**.

## 8.1 Add/pin RRG sources

Create/pin:

```text
research/rrg/v0.2.1/
research/rrg/CURRENT.md
```

`CURRENT.md` should identify v0.2.1 and list hashes. The copied RRG source bytes are read-only project inputs, not GeoMind-generated theory text.

## 8.2 Add one alignment decision record

Create:

```text
docs/decisions/0011-align-geomind-to-rrg-v0.2.1.md
```

It should record:

- current RRG release identity/hashes;
- no change to accepted C0–C5 evidence;
- old C6 measurements preserved;
- old nested-overlap interpretation already superseded by 0010;
- C6 staged composition is only a component of current RRG;
- background transformation/change-of-possibility is now a separate required claim before full source-recursion language;
- same procedure is an experimental anti-cheating rule, not the universal RRG definition;
- R5 and C6 R3 are the forward docs.

## 8.3 Create GeoMind R5

Create:

```text
GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R5.md
```

R5 supersedes R4 for future work only. Do not rewrite history in R4.

R5 must contain the claim ledger in §4 and the updated milestone map.

## 8.4 Repair `AGENTS.md`

Point agents to R5 and the pinned RRG v0.2.1 source directory.

Keep the operational workflow, freeze rules, no-retuning rules and independent review rules that are already good.

Remove/repair wording that lets “old locked core only” or “same procedure = theory” become the full scientific authority.

## 8.5 Repair C6 status truthfully

Update `STATUS.json` as described in §3.2. Regenerate README.

Do not mark C6 ACTIVE/REVIEW_READY from design work alone.

## 8.6 Create C6 R3 proposal

Create:

```text
experiments/c6_proposal_r3.md
```

It must include:

- explicit mapping to current RRG v0.2.1 claims;
- separate Arm A / Arm B verdicts;
- normalization ledger;
- leakage/ownership boundary;
- background descriptor definition;
- background causal controls;
- changed-possibility assay;
- stop conditions;
- estimated runtime plan;
- exact reuse vs replacement map for current C6 code;
- owner decisions still required.

**Stop after this design batch. Do not run the new development gate until the owner approves C6 R3.**

---

# 9. Code reuse map after C6 R3 approval

Do not rewrite everything. Reuse good mechanisms deliberately.

## Keep/reuse where contract still matches

- C4 accepted resonator law and detector as frozen source/reference.
- C5 accepted effective-state/interface concepts as bounded predecessors.
- C6 native/NumPy equivalence machinery.
- C6 effective-state publication boundary.
- open-loop upper-level prediction rule that accepts published state only.
- provenance, manifests, seed discipline, mutation testing and gated verification.
- evidence immutability and independent review.

## Fix/replace in new C6-owned files

- obsolete nested-veto semantics in the forward C6 implementation;
- source authority references to only the old v0.2 core;
- C6 verdict language that implies staged hierarchy = complete RRG recursion;
- missing background-state measurement;
- missing resonator→background causal intervention;
- missing changed-possibility assay;
- any test that encodes the superseded nested-veto rule.

## Do not modify frozen historical files merely to make new tests pass

If a frozen predecessor API is insufficient, adapt through new C6/R5-owned code or explicitly create a new requalified predecessor revision under the existing process.

Do not silently mutate an accepted C4/C5 mechanism and still cite the old receipt.

---

# 10. Verification/acceptance requirements for the alignment batch

Before owner review of C6 R3, verify only the affected lightweight checks.

Required checks:

1. pinned v0.2.1 files match recorded SHA-256;
2. `AGENTS.md` points to R5/current RRG and contains no stale sole-authority wording;
3. `STATUS.json` and generated README agree;
4. R4 remains unchanged as history;
5. old C6 receipts/evidence remain byte-identical;
6. C6 R3 contains distinct `H-COMP`, `H-BG`, `H-PS`, and `H-RBG` semantics;
7. no new experimental result is claimed from design-only work;
8. no C6 panel/final seeds were run;
9. accepted freeze checks for C0–C5 still pass if those standard repository checks are affected by documentation/config changes.

Do not rerun expensive accepted panels just because documentation changed.

---

# 11. Scientific wording rules for future receipts

Use bounded language.

Good:

> C6 Arm A supports staged recursive composition within this model under the registered detector and interventions.

Good:

> The intact resonator changes the registered background response relative to both matched controls; H-BG is supported within scope.

Good:

> The changed background increases formation/recovery of the registered later candidate under paired seeds; H-PS is supported within scope.

Good:

> This is one bounded computational realization of part of the RRG source-direction hypothesis. It does not establish universal physics or AI advantage.

Bad:

> RRG is proven recursively.

Bad:

> Because the effective node predicts well, a new physical level formed.

Bad:

> Same-law closure failed, therefore RRG failed.

Bad:

> A stable hierarchy is automatically intelligence/compression/energy efficiency.

---

# 12. What counts as success from here

The next work is successful if it makes the experiment **more faithful and more falsifiable**, not if every hypothesis passes.

A valid result may be:

- staged composition works but background transformation does not;
- background transformation exists but does not enable a new organization;
- one recursive turn works but the second stops;
- the model branches/coexists instead of forming a deeper level;
- conventional baselines remain better for useful AI tasks;
- the chosen computational law cannot realize the source-direction hypothesis.

Those are useful outcomes.

Do not tune the model until the desired RRG story appears. A clean failure is more valuable than an engineered “proof.”

---

# 13. First task for Codex 6.1 Sol High

Use this prompt after placing this file in the repository:

```text
Read AGENTS.md, STATUS.json, GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md,
this RRG v0.2.1 alignment handoff, current C4/C5/C6 proposals and decisions
0007–0010, then read the pinned RRG v0.2.1 README, 04, 08, foundation
ERRATA, and MANIFEST/SHA256 records before changing anything.

Goal: perform only the source/governance/design alignment batch. Do not run a
C6 development gate or panel.

1. Pin the exact RRG v0.2.1 audited source set in a versioned read-only
   repository directory and verify hashes.
2. Create decision 0011 recording the alignment and preserving all historical
   evidence/accepted results.
3. Create GeoMind R5, superseding R4 for future work, with separate claim
   families H-M, H-U, H-COMP, H-BG, H-PS, H-RBG, H-PRED, H-AI and H-EFF.
4. Repair AGENTS.md so the current RRG source direction B_n -> R_n -> B_{n+1}
   is not lost, while keeping physical analogies from imposing literal physical
   equations on the AI model.
5. Repair STATUS.json / generated README so C6's old STOP measurements remain
   history but the nested-overlap interpretation is marked superseded by
   decision 0010; do not assign a new hypothesis verdict.
6. Preserve experiments/c6_proposal.md and c6_proposal_r2.md as history. Draft
   experiments/c6_proposal_r3.md as the only forward C6 design.
7. C6 R3 must separate:
   A) staged recursive composition, and
   B) causal background transformation + changed-possibility testing.
   Passing A alone must not be called full RRG source recursion.
8. Define B before outcomes, include intact/no-resonator/no-backreaction matched
   controls, and a paired later-formation assay using the same detector/rule.
9. Reuse good C4/C5/C6 mechanisms; do not modify frozen accepted files or old
   evidence receipts.
10. Run only affected lightweight documentation/status/hash/freeze checks after
    the complete edit batch. Record PASS/FAIL/NOT_RUN honestly.

Stop at DESIGN_REVIEW_READY. Do not implement C6 R3 dynamics and do not run
long experiments until the owner approves the proposal.
```

---

# 14. High-review prompt

Use a fresh model family/context for this review:

```text
Review the RPG_AI RRG-v0.2.1 alignment batch against the pinned current RRG
sources and repository history.

Reject the batch if it:
- rewrites accepted C0–C5 evidence;
- treats old v0.2 wording as overriding current v0.2.1 interpretation;
- equates coarse-graining with physical background generation;
- calls staged R0->R1->R2 composition the full B->R->B recursion;
- turns same-equation closure into the universal definition of RRG;
- requires monotonic size/timescale growth without a registered narrower claim;
- keeps the superseded nested-veto interpretation as current status;
- lets C6 R3 tune background metrics or controls after final outcomes;
- infers AI usefulness/efficiency from stable hierarchy alone;
- modifies frozen predecessor source or immutable evidence without a new
  requalification path.

Check that C6 R3 has separate operational verdicts for staged composition,
background transformation, changed possibility and repeated source recursion,
with controls, leakage boundaries, stop rules and owner decisions explicit.

Fix material documentation/design defects in scope. Do not run a long C6 gate or
panel. End with APPROVE or CHANGES_REQUIRED and the exact next owner decision.
```

---

# 15. Bottom line

The target is **not** to make RPG_AI say RRG words.

The target is to make the experiment test the actual current idea without cheating:

```text
activity/background
    ↓
geometry ↔ mode closure
    ↓
persistent resonator
    ↓
measurable change to the environment/background
    ↓
changed conditions for later organization
    ↓
new persistent effective unit
    ↓
repeat when the dynamics permit it
```

Existing C4/C5/C6 work supplies useful pieces of this chain. The next revision must connect the missing causal background step instead of treating hierarchy bookkeeping as the whole theory.

**Preserve evidence. Correct interpretation. Add the missing causal test. Then run.**
