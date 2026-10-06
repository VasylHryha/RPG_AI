# RPG_AI — R2 adversarial recheck and corrected next-work plan

**Date:** 6 October 2026  
**Repository:** `VasylHryha/RPG_AI`  
**Inspected main:** `fba4332a885fa6fa79526dc00045f30ae98cd92b`  
**Status:** Research/design review complete at the scope below. **The earlier handoffs are not ready-to-execute specifications. No new long run is authorized here.**

> **Main correction:** Before introducing a larger shape architecture, establish that the interface preserves the information a task needs, its timing permits that information to be learned or retained, and its evaluator distinguishes meaningful behavior from a default or a simple oscillator.

This file replaces the **forward implementation recommendations** in the two earlier assistant handoffs. Their original bytes are preserved in `archive/`; they remain historical records, not competing current plans. This file does not supersede the repository’s approved definitions, owner decisions, historical protocols, evidence or verdicts. A repository design amendment still needs its normal review/approval. [H1][H2][R01][R11]

## Reading order

Read §1 for the decision, §3–5 for the important counterexamples, §6–10 for the corrected design boundaries, and §11 for the next work. §12 and `SOURCES.md` distinguish useful research from unsupported transfers. §15 is the bounded handoff to the next agent.

---

## 1. Verdict: substantial corrections, not cosmetic polishing

The previous work contained useful source mapping and sensible concerns about disconnected outputs, weak controls and evidence integrity. But I would **not** approve it as an implementation plan. It mixed current scope with future aspirations, selected a detailed growth mechanism too early, and missed hard conflicts between its own rules and the tasks.

The most important corrections are:

**First, the proposed memory-path gate cannot recognize a normal memory cue.** It demands eight seconds of active input inside a ten-second window, while `remember_static` exposes the target for only four seconds and hides it for twelve. The proposed twenty-second demand timer resets during hiding and cannot mature in the steady memory block. [R02][R04][H1]

**Second, `choose` has an information bottleneck before the oscillators.** Different valid combinations of distance and health can yield the same input strength while requiring different target IDs. The current decoder cannot recover the missing distinction. Adding more oscillators or a semantic registry does not repair a non-injective task representation. §3 gives a constructive example. [R03][R04]

**Third, the architecture expansion was premature.** Revision 5.1 explicitly tests a bootstrap and defers combinations, bonds and related library studies. A per-run snapshot archive is a legitimate implementation of that scope. The absence of a production-style `ShapeInstance`/`ShapeRegistry`/recursive composer is not a violation of the current specification. [R01]

**Fourth, the controls and causal tests need more precise estimands.** Same intended births are not necessarily the same accepted births, costs, lifetimes or input exposure. Synchronization is not proof of information transfer, and removing nodes changes more than the presumed signal path. [R02][R05][R09][R11]

**Fifth, research should guide small discriminating experiments, not prescribe a nine-layer architecture.** The cited systems differ substantially in supervision, centralization, communication and resource rules. None establishes that the earlier bridge rule, fixed thresholds or orphan-deletion policy is the best solution for this medium. [S01][S02][S03][S12][S17]

### Recommended decision

Keep the oscillator substrate and the task-blind objective. Retire the earlier executable-looking bridge pseudocode. Proceed first with a **bounded interface-and-lifecycle diagnostic batch**, not a full architecture rewrite and not another 2,000-episode run. Use its results to choose the smallest justified design revision. The particular readout/growth/confinement mechanism is not selected by this audit.

### What this audit actually did

It inspected the two generated files, refreshed the repository checkpoint and critical source paths, checked selected primary publications and scoped HTM implementation files, and executed fourteen standalone formula/counterexample checks. All fourteen current checks passed. A pass means the stated audit assertion was confirmed—not that RPG_AI passes a task.

No native project library was loaded, no project module imported, no project test suite rerun, no development/judging episode executed, no old ledger rescanned, and no repository file or branch modified. The retained Codex recheck is evidence from that recheck, not a new reproduction by this session. Exact read scopes and access limitations are in `SOURCES.md` and `evidence/SOURCE_REGISTER.json`.

---

## 2. Issue register: what changes and who owns it

**P0** blocks treating the previous handoff as a runnable full-run specification. **P1** requires correction or explicit deferral before the affected implementation/claim. “Corrected below” means the recommendation is repaired; it does not mean code in GitHub has been changed.

| ID | Priority / area | Finding | Corrected disposition |
|---|---|---|---|
| A01 | P0 — Timing / lifecycle | Memory cue cannot satisfy proposed eligibility and active-reset growth timers. The proposed sensor gate requires 80 active samples but a memory cue lasts 40; a 20-second timer resetting during each 12-second hidden period cannot mature. | Separate cue/retention/morphology clocks; test burst exposure and block transitions. |
| A02 | P0 — Representation | Choose encoding loses information required for exact target selection. Two valid scenes can produce identical drives and decoder-visible bearings/IDs but require opposite targets. | Audit sufficient input representation before architecture/growth changes; preserve task-relevant fields or explicitly narrow the claim. |
| A03 | P0 — Test coverage | Fifty sequential episodes do not cover the four-task rotation. The proposed smoke under inherited rotation runs 20 perceive, 20 move and 10 memory; no choose. | Use an explicit separate engineering-case manifest, not a larger episode count masquerading as coverage. |
| A04 | P1 — Scope | Deferred composition architecture treated as a bootstrap defect. The protocol explicitly defers combinations, bonds and related library work. | Do not require a new tracker, registry or composer before interface feasibility is known. |
| A05 | P1 — Architecture | Existing neighbour histories described as missing. Frame already records sites, positions and directed endpoint neighbours. | Reuse recorded history; instrument substeps only for questions endpoint samples cannot answer. |
| A06 | P1 — Engineering | Native optimized path omitted from ownership/change plan. perf.cpp implements bindings, action, adaptation, timers and sampling as well as Python reference code. | Specify reference/native equivalence at changed boundaries and test both paths. |
| A07 | P1 — Diagnosis | Global readout and library absence overstated as root architectural failures. A fixed output is a valid interface; the archive is valid for a bootstrap. Current empty outputs and drift are the actual measured problem. | Separate observed failure from future modularity ambitions. |
| A08 | P1 — Causal inference | Locking or persistent graph called a causal path. PLV, radius and per-edge persistence do not imply a complete directed, simultaneous or time-respecting causal computation. | Maintain distinct geometric, dynamical, temporal and intervention evidence. |
| A09 | P1 — Proposed algorithm | Bridge pseudocode not executable or justified as best design. Half-radius placement, zero-distance frontier, newborn history, near-origin overshoot, nondegenerate shape criteria and structural update ordering remain unresolved. | Retire the executable-looking pseudocode; compare bounded candidates after transport/decoder tests. |
| A10 | P1 — Readout | Coherence treated as distance or stopping error. A coherent oscillator can keep C=1 without encoding distance or a zero-error stop signal. | Add zero-demand, retreat, braking and distance-information tests before freezing decoder changes. |
| A11 | P1 — Baselines | Static memory treated as inherently multioscillator. A carrier-matched oscillator can retain an encoded phase after the cue disappears. | Include one-oscillator and explicit sample-and-hold baselines; distinguish encoding from retention. |
| A12 | P1 — Controls | Draft cost asymmetry described as an implementation bug or assured advantage. M and intact use different birth-time admission laws in the draft; moving geometry can change cost even with birth checks. | Label as proposed design asymmetry; measure integrated cost and separate birth checks from continuous bounds. |
| A13 | P1 — Controls | Matched intent confused with realized count/exposure matching. Feasibility, random placement, deaths and protection can yield different accepted births and ages. | Define a conditional feasible-site null and report mismatch; do not assert exact matching without an enforceable protocol. |
| A14 | P1 — Controls | Active-site null advertised as automatically better. M-all and M-active ask different questions; a single active site removes site randomization. | Preserve the owner’s M/U decision; explicitly register which joint effect or component effect is being tested. |
| A15 | P1 — Controls | Same seed equated with identical input exposure. Closed-loop movement changes later observations; a yoked birth schedule is sourced from the intact trajectory. | Separate closed-loop policy comparison from fixed-drive mechanistic experiments. |
| A16 | P1 — Lifecycle | Orphan pruning presented as confinement. Deleting detached members does not keep an attached path in place and can induce churn or erase dormant utility. | Separate occupancy regulation, attachment persistence and response/memory; compare confinement variants explicitly when needed. |
| A17 | P1 — Task-blind boundary | External task-qualified promotion could leak into the claimed task-blind learner. Using score-selected types in future dynamics changes the learning regime. | Keep structural archive and evaluator output separate; any score-informed routing/reuse gets new scope and held-out evaluation. |
| A18 | P1 — Interventions | Three lesions treated as universal necessary tests with no confounds. Node deletion changes resource count, spatial forces and degree normalization; cuts may hit ports; redundancy can mask necessity. | Use mechanism-specific interventions, shams, restoration and explicit not-applicable cases. |
| A19 | P1 — Identity / reuse | Pose normalization and persistent identity prescribed too early. Moving a module relative to fixed ports changes the experiment; symmetric canonical frames and lineage across splits are unspecified. | Keep exact snapshot identity; add descriptors without destructive semantic deduplication; defer operational identity until needed. |
| A20 | P1 — Evidence scope | Snapshots/covariance overread as distinct useful reusable modules. Many snapshots are repeated evolving organizations; saved empty output does not certify all later actions. | Retain historical verdicts and report structural, functional, causal and in-context claims separately. |
| A21 | P1 — Statistics | Directional development gates overread as confirmation. Six of eight signs has a one-sided fair-sign tail of 0.14453125; many snapshots/tasks are not independent tests. | Define the independent unit, margins, multiplicity and held-out confirmation; retain all seed outcomes. |
| A22 | P1 — Replication | Medium-seed replication conflated with environmental generalization. Run.episode selects worlds and permutations by episode index shared across medium seeds. | Describe results conditional on the common environment schedule; add environmental replication only under a new registered plan. |
| A23 | P1 — 0g | Existing hysteresis and oscillator period misdescribed. v3 already has ±0.2 hysteresis; 3.326 s is the free full period, not the half-period. | Reuse the correct state machine and measure actual mode telemetry; do not call hysteresis a new feature. |
| A24 | P1 — 0g | Travel-time dwell treated as a derived universal rule. Distance over speed is a heuristic; motion can cancel, targets move and emergencies require release. | Bound dwell with progress/feasibility and emergency conditions; compare matched wrappers and common budgets. |
| A25 | P1 — Research | Analogies promoted into architectural mandates or novelty guarantees. Papers differ in training, communication, population and centralization; e-prop remains gradient-based. | Use a source-to-mechanism matrix with read scopes and transfer limits; no uniqueness claim. |
| A26 | P1 — Evidence engineering | Operational debt not integrated into the critical path. Reporting can run simulations; aggregation, huge ledgers, deadlines and resume semantics remain unresolved. | Read-only report API, explicit receipt adapters, bounded chunking and deadline tests before new large runs. |

The machine-readable version is `evidence/ISSUE_LEDGER.json`. Several rows concern my previous recommendations, not defects in the project. That distinction must survive any follow-up issue creation.

---

## 3. A representation failure the earlier reviews missed

### 3.1 Exact task rule versus actual oscillator input

For `choose`, the world selects the lowest-health living enemy within range 2.5; if none is in range it selects the nearest. The input adapter encodes bearing in phase, and merges distance, health and range status into one scalar strength:

\[
k(d,h)=2e^{-d/10}(2-h/100)\,a(d),\qquad
 a(d)=\begin{cases}1&d\le2.5\\0.5&d>2.5.\end{cases}
\]

The fixed output adapter uses the medium’s decoded bearing plus visible bearings, IDs and the live mask. It does not recover health and distance from separate channels. Both the Python adapter and optimized native path use this construction. [R03][R04][R08]

### 3.2 Two legal scenes, identical drives, opposite answers

Use three stationary enemies and the same agent position, IDs, physical-site assignment and bearings in both scenes:

| Enemy | Bearing | Scene A distance | Scene A HP | Scene B distance | Scene B HP |
|---|---:|---:|---:|---:|---:|
| ID 0 | −0.7 rad | 0.8 | 50 | 1.4453852113757117 | 40 |
| ID 1 | +0.9 rad | 1.8 | 40 | 1.1546147886242881 | 50 |
| ID 2 | +2.2 rad | 5.0 | 80 | 5.0 | 80 |

The first two distances lie in the generator’s legal inside-range interval `[0.5, 2]`; the third is in its outside interval. Their health values and K=3 are also legal. In A, ID 1 is correct. In B, ID 0 is correct. [R04]

The transformed distances are chosen as:

\[
d'_0=0.8+10\ln(1.6/1.5),\qquad
d'_1=1.8+10\ln(1.5/1.6).
\]

Substitution cancels the changed health factors exactly in real arithmetic. The three strength values are the same in both scenes:

```text
ID 0: 2.7693490391599074
ID 1: 2.6728646765160704
ID 2: 0.7278367916551601
```

Our numerical check returned a maximum strength difference of zero in its floating-point evaluation. Bearings, IDs and visible/live status are unchanged. Because the enemies are stationary, the encoded input sequences remain indistinguishable, not just their first frame. This is check **C01**.

For the same initial medium state, the same dynamics and the same available decoder inputs produce the same action sequence. They cannot select the different correct ID in both scenes. Randomized action selection cannot reliably distinguish identical input distributions either.

### 3.3 What this proves—and does not

This demonstrates **information loss on the task’s allowed continuous observation space**. It rules out exact general target selection through this interface alone under those conditions. It does not prove that above-baseline average accuracy is impossible, that these exact floating-point scenes have appeared under existing discrete seeds, or that the historical scores are invalid. The post-episode reward in the reward arm does not make the missing distinction available during a fresh frozen evaluation episode.

It also does not justify claiming a theorem about all oscillator AI. The problem is this encoding/decoder pair.

### 3.4 Required design decision

Before choosing a new growth rule, explicitly decide what the task claim requires from the representation. Exact general target selection requires preserving the distinctions demonstrated above. A narrower bootstrap claim—improvement over a declared baseline with this lossy interface—may legitimately retain the existing encoder, provided the information ceiling and comparator access are disclosed. This audit does not turn the historical average-score experiment into a universal-exactness test. For a future stronger choice capability, independently distinguishable distance, health, range and item-binding information is the more useful option to investigate first.

However, “add another input channel” is not enough by name. Two drives at the same site and carrier may simply combine into another resultant and recreate the same ambiguity. The revised representation needs collision tests at the **actual physical input**, not just distinct fields in a Python object. Spatial channels, carrier bands or time-multiplexed signals are candidates with different costs and timing implications, not approved answers.

Do not calculate the winning enemy in the encoder and then attribute that decision to emergent oscillator computation. If an engineered ranking prior is used, disclose it and compare with an input-only baseline carrying the same prior.

---

## 4. Timing, memory and decoder feasibility

### 4.1 Three clocks were conflated

The current system combines fast phase integration, medium-term exposure statistics and slower structural changes. That is not inherently wrong. The failure is requiring every capability to satisfy the same exposure window. [R02][R04]

| Quantity | Current or previously proposed value | Consequence |
|---|---:|---|
| World sample interval | 0.1 s | Ten observations per second. |
| Memory visible interval | 40 steps = 4 s | Only forty active samples for that cue. |
| Memory hidden interval | 120 steps = 12 s | Retention must work without an active cue. |
| Local history used for eligibility | 100 samples | Ten-second window. |
| Proposed source-edge exposure | At least 80 active samples | Cannot be met within an ordinary memory cue. |
| B1 / proposed B2 active demand threshold | 20 s, reset on inactivity | Cannot mature during a four-second visible segment. |
| Structural qualification history | 601 endpoints over 60 s | Measures another property on another timescale. |

Within a steady block of repeated memory episodes, any 100-step window contains at most forty visible steps. A change of physical site between episodes cannot increase that bound for one site. At a task-block boundary, inherited samples from the preceding task are a separate transient case; they are not evidence that the regular memory cue passes the rule. Checks **C02/C03** reproduce the timing arithmetic.

The native dynamics still receive the cue during those four seconds. This finding does not say that physical entrainment or memory cannot happen. It says the proposed learning/admission indicators systematically fail to recognize or grow from that kind of exposure.

### 4.2 Correct separation

A revised contract needs three distinct questions:

**Encoding:** During an actual visible cue, did the source causally affect the relevant state? Measure on a cue-length-compatible interval, with a declared minimum amount of evidence. Do not dilute a short cue with unrelated inactive time and call it failed locking.

**Retention:** During hiding, does output depend on the earlier cue rather than an ongoing input or a default? This is a state-memory question, not a demand for a currently active source-to-output edge.

**Morphology:** Across repeated exposures, is structural demand persistently unmet? Specify whether evidence accumulates across cues, decays, resets on a task/site reassignment, or is tracked per physical site. No arbitrary reset may erase all demand before a structural timer can ever fire.

The concrete thresholds must be derived from those contracts and checked on bounded fixtures. This audit deliberately does not replace the old twenty-second number with another unsupported number.

### 4.3 A single oscillator is a necessary memory baseline

Suppose the visible cue has established:

\[
\theta(t_h)=\pi t_h+\alpha,\qquad \omega=\pi.
\]

After removing informative drive, an isolated oscillator can evolve as `theta(t)=pi*t+alpha`. The current carrier-relative decoder retains `alpha` throughout the hidden interval. Check **C08** verifies this conditional retention identity.

This is not a claim that a randomly initialized oscillator acquires every cue accurately in four seconds. Acquisition is exactly what the engineering fixture must measure. It is a counterexample to the earlier assumption that static memory inherently requires a multioscillator structure or an internal bridge.

Use both a lawful single-oscillator baseline and an explicit sample-and-hold reference. If they solve the task, that is useful information about the task’s difficulty. Do not make a gate reject a legitimate simple memory mechanism merely because the desired eventual architecture is more elaborate.

### 4.4 Coherence is not task error

For one oscillator, or several exactly aligned oscillators, normalized coherence is one. It need not encode distance, speed demand or whether the target has already been reached. The current move decoder therefore returns full speed for a coherent state even if its task-error drive has vanished. The current perception distance formula returns zero at coherence one, irrespective of actual distance; its primary historical score uses angular error only. [R03]

Check **C09** establishes the missing guarantee, not an empirical explanation of every failed movement episode. Empty readouts remain the stronger retained explanation for the historical whole-medium floor. [R10]

Before freezing a revised decoder, test zero demand, target approach, retreat from inside desired range, stopping, overshoot, loss of input and changing cue. A fixed decoder is desirable for attribution, but a fixed **incorrectly matched** decoder is not scientifically conservative.

### 4.5 Smoke coverage must be explicit

With twenty episodes per task block, episodes 0–49 contain twenty perception, twenty movement and ten memory episodes. `choose` first appears at episode 60. Check **C04** verifies this. [R03]

Replace the earlier “fifty episodes cover everything” requirement with a named engineering-case manifest. It must explicitly include every task, cue phase, site assignment, hidden interval, boundary and intervention it claims to cover. It is a separate engineering schedule, not a silent amendment of the historical development rotation.

---

## 5. Physical paths, locking and causality: keep the distinctions

### 5.1 A bridge is a hypothesis, not the selected solution

Sensors at radius four with drive reach below three overlap the output disk of radius two. An oscillator at `(1.5, 0)` is 2.5 units from the sensor `(4, 0)` and 1.5 from the output. It can receive input and be read out directly. A chain is not geometrically necessary. **C05** is an explicit witness. [R02][R03]

A direct relay may be a useful transmission primitive. It is not, by itself, a learned selector or a higher-level module. Transmission, memory, selection and closed-loop movement should not share one undifferentiated “task use” gate.

### 5.2 Existing histories should be reused

The first handoff incorrectly said neighbour-edge exposure was absent. `Frame` already records endpoint positions, phases, sites and directed neighbours; the optimized path also produces corresponding frames. Recompute the required endpoint exposure from those records before adding another stateful edge database. [R02][R08]

Those are world-step endpoint observations. They are not complete logs of the neighbour list held for every RK4 substep. Claims about exact substep propagation need additional instrumentation or a scoped replay. This is an important limit on both the old proposal and a proposed “no new telemetry needed” correction.

### 5.3 Four non-equivalent graphs

| Object | What it can establish | What it cannot establish alone |
|---|---|---|
| Geometric reach graph | Two positions lie within a radius. | A directed neighbour slot exists or coupling is strong enough. |
| Actual dynamical-support graph | A term from j participates in i’s update at the stated time. | Informative response, stable locking or successful decoding. |
| Exposure/locking graph | An edge is often present or phases show a persistent relation. | A complete simultaneous path or a causal effect of that relationship. |
| Time-respecting perturbation response | A controlled input change alters later state/output along a specified mechanism. | General task superiority, useful learning or autonomous closure. |

The correct phase-influence direction is `j -> i` when j appears in i’s contributing neighbour list. The cap of eight neighbours matters: lying within radius three does not guarantee that j is selected. Our revised **C06** fixture respects minimum point separation and still excludes the frontier from a newborn’s nearest eight. [R09]

In **C07**, five sequential edges each exist in eighty of one hundred frames, but their missing intervals cover the entire window, leaving no frame with the whole path. This refutes a simultaneous-path inference; time-respecting transmission could still occur and must be analyzed separately.

In **C14**, two uncoupled equal-rate oscillators have PLV one. Common drive can likewise explain observed phase alignment without direct information transfer. Locking is a useful descriptive signal, not proof of necessity or causal credit.

### 5.4 The actual causal system is larger than a phase graph

Positions affect drive strengths, neighbour selection and coupling. Phases affect spatial motion. Thus phase-to-position-to-input pathways exist alongside direct phase coupling. A phase-only path lesion is a deliberately limited intervention; it does not block every possible causal route. Any eventual graph-based explanation must state its variables and what routes it excludes. [R09]

### 5.5 Retire the earlier bridge pseudocode

Its status is **unvalidated candidate**, not “implement this exactly.” It has unresolved cases: division by zero at an origin frontier, overshooting near the output, reliance on newborn histories that do not yet exist, radius without directed-neighbour admission, no measured transfer/relaxation bound for spacing 1.5, and inconsistent orphan-pruning placement in the update order. A perfectly straight chain can also fail the existing nondegenerate-hull structural criterion even while transmitting a signal. [H1][R07][R09]

A future candidate must define these cases, not hide them behind pseudocode. A one-off hand-built transmission witness need not pass every structural qualification test; it must be labelled for the narrower thing it proves.

---

## 6. Corrected architecture and lifecycle scope

### 6.1 What the current architecture already does

The current implementation has a valid research separation: world and observations; generic native medium; revision-specific adaptation/growth; orchestration; structural qualification; isolated evaluation; aggregation and receipts. It should not be collapsed into a new framework merely to match a conceptual picture. [R01][R02][R05][R06][R07][R09]

There are **two implementations of critical per-step contracts**: the Python reference route and the optimized native runner. Any change to binding, decoder, timer or sampling semantics must update/compare both. A design claiming these decisions live only in Python is incomplete. [R05][R08]

| Lifecycle | Current behavior | Correct interpretation |
|---|---|---|
| World | New episode every sixteen seconds. | Environment resets while the medium persists. |
| Medium | Positions, phases, rates, gains and histories carry between episodes. | Continuous developmental state. |
| Element | Birth/protection, local locking adaptation, D1 low-lock death and D3 budget pruning. | Actual implemented element lifecycle. |
| Structural candidate | Cohort/geometry/phase tests over sixty seconds. | A retrospective structural observation, not a production object. |
| Recovery | Saved whole medium replayed under future recorded drive, with kicked/control futures. | Driven, context-dependent robustness evidence. |
| Snapshot | Immutable state excerpt with exact content identity and timestamps. | Legitimate bootstrap archive. |
| Evaluation | Fresh copies, fixed original ports, growth/plasticity off, motion still active. | Isolated behavior under the declared environment. |

The constructor named `world.Library` is the native binding. `Run.snapshots` stores the conceptual structural archive. Clarify this in documentation; renaming the public binding is not a priority unless an actual caller ambiguity or API collision appears. [R05][R12]

### 6.2 What is a current blocker, and what is not

Current blockers are information sufficiency, temporal feasibility, observable output/decoder behavior, fair controls and trustworthy evidence. A universal live shape ID, pose-canonical type registry and recursive compositor are **later research capabilities**. Their absence is compatible with the explicit bootstrap scope. [R01]

A missing persistent tracker becomes a blocker only when a selected rule depends on longitudinal component age, membership inheritance or split/merge history. That requirement is a cost of the selected rule—not evidence that every valid experiment needs that architecture.

### 6.3 Minimal near-term additions

Keep data contracts small and attached to existing owners:

| Contract | Minimal contents | Owner / boundary |
|---|---|---|
| Interface descriptor | Encoded variables, carrier, physical sites, decoder-visible fields, information loss, valid transforms. | Revision protocol. Passive metadata before any new port runtime. |
| Exposure record | Cue activity mask, endpoint reach, sample counts and windows, reset/decay reason. | Existing frame/adapter path. |
| Evaluation receipt | Per-episode score, action/readout exposure, cue phase, intervention, seed and template identity. | Evaluator, never a training callback. |
| Experiment manifest | Config/version/source hashes, arm/null definitions, clocks, seeds, work caps and stop rules. | Orchestrator with read-only report view. |

No mandatory nine-layer refactor, persistent shape ecology or semantic retrieval system is introduced by these contracts.

### 6.4 A future module architecture remains useful—but conditional

Once a copy has repeatable function, it is reasonable to investigate declared ports, allowed poses, exact versions and later composition. Keep those as research questions with evidence gates:

- Does moving the object **with its interface** preserve behavior? Moving it alone against fixed ports is not a symmetry; C13 demonstrates this.
- Does its behavior survive other modules loading the same substrate, changing neighbourhoods and competing for budget?
- Can a higher-level controller treat it as one phase variable without losing essential state? Internal locking alone does not establish such a reduction.
- Are identity across membership turnover, splitting and merging needed for a real operation, or only for plotting?

A content hash identifies exact serialized content. It does not identify a unique organism, prove semantic equivalence, or solve symmetry/canonicalization. Preserve exact hashes and add non-destructive descriptors first; do not erase snapshots under an unvalidated fuzzy equivalence rule. Symmetric objects and interchangeable input ports make a “primary-input axis” ambiguous. [R03][R06]

### 6.5 Preserve the task-blind boundary end to end

It is acceptable to **report** external task scores about a task-blind structural archive. It is not the same experiment if high-scoring snapshots are then routed back into the developing medium while the resulting system is still called task blind. Task-selected admission, reuse and composition are outcome-informed selection at system level even if an individual oscillator never sees reward. [R01]

Keep structural admission unchanged in the historical experiment. Any future task-qualified index must be separately labelled, frozen outside the test panel and evaluated on fresh evidence when it influences behavior. An immutable type file does not make that selection task blind.

---

## 7. Growth, resources and confinement: competing hypotheses

### 7.1 Do not assume the resource cap caused instability

A flat population count can coexist with high birth/death flux and unmet demand. Conversely, living at a cap need not cause rejection if no new births are requested. Keep count trend, demand, turnover, rejection reasons, age distribution, coverage, integrated cost and time over budget separate. [R02][R10]

`C=N+0.1E` is checked at births and pruning events; E changes as geometry changes. Therefore a feasible birth does not imply `C<=64` continuously. C10 illustrates this accounting distinction at fixed N. Do not promise a continuous hard bound without adding a different enforcement law and measuring its effect.

Use exact class rules rather than vague “self-limited”: a reporting interval can be demand-free, have cost rejections, have cap rejections, or have both. Mixed categories and the denominator for rates must be defined. The old run keeps its recorded G0′ result; classification changes belong to a new revision.

### 7.2 Orphan deletion is not an attachment mechanism

Removing a disconnected component after forty seconds does not prevent its earlier drift. An “input OR output attached” condition also permits input-only islands and output-only activity to survive. Timers can be accidentally reset by component splits, and dormant structures can be useful later. These are hypotheses to test, not reasons to replace all pruning with a tuned utility scalar. [H1][R02]

A short input-free interval is normal for memory. Do not treat it as missing structural service. Nor should a task-selected score be smuggled into the task-blind death rule.

### 7.3 A small candidate comparison instead of one declared winner

| Candidate | Question it isolates | Principal limitation |
|---|---|---|
| Hand-built relay/small noncollinear structure with geometry fixed for a diagnostic | Can the signal and decoder work at all? | Not evidence of emergent growth or the original mobile law. |
| Same fixture with original mobile dynamics | Does geometry destroy otherwise feasible transfer? | A hand-built witness is not a learned module. |
| Passive output region plus a fully specified, local structural-demand rule | Can growth discover/maintain service to the output? | A rule can encode the desired topology; compare its prior and cost. |
| Explicitly bounded arena or weak endpoint anchoring, applied identically to relevant arms | Does a modest environmental constraint preserve useful structure? | Changes the dynamics; needs separate provenance and cannot inherit C4 acceptance automatically. |
| Optional low-capacity trained readout, offline only | Is task-relevant information present but inaccessible to the fixed decoder? | Must control capacity, training data and input-only baselines; not the main task-blind claim. |

Test them in the logical order above only as needed to answer the current failure. Do not launch a large parameter sweep or implement all mechanisms together. The literature supports investigating these axes, not asserting that orphan deletion is superior to anchoring. [S02][S07][S10][S11][S19]

---

## 8. Controls: name the effect before choosing the null

### 8.1 Preserve the owner decision

The draft records two controls per intact seed: M is the registered G0 comparison; U retains the historical queue rule for descriptive information. This audit does not replace that choice or silently promote an active-site variant. The exact M mechanism must be resolved with the output/growth design before registration. [R11]

### 8.2 Four different comparisons were being mixed

| Comparison | Estimand | What is not automatically held fixed |
|---|---|---|
| Conditional growth versus all-site random placement/phase | Joint value of demand-selected region and initial phase under the declared protocol. | Informative input exposure, accepted births, lifetime and density. |
| Conditional growth versus active-site random placement/phase | More conditional effect after restricting placement to informative sites. | A single active site leaves no placement randomization; geometry and phase remain coupled. |
| Alternative births from the same saved pre-event state under one exogenous drive replay | Local intervention effect of this birth choice over the declared horizon. | Does not measure an independently learned long-run policy. |
| Independently evolving closed-loop controllers on paired world seeds | Performance of the complete controller/growth packages. | Their later input streams diverge with their actions. |

M-active is not universally “fairer.” It tests a different question. M-all can be legitimate if the claim explicitly includes choosing an informative location. Neither removes the need to account for realized cost and exposure.

### 8.3 Cost symmetry and realized matching

The current Rev6 draft skips birth-time cost rejection for M but not intact. That is a proposed design asymmetry, not evidence of a runtime implementation error. Extra transient density may help or harm; its effect is not established. The phrase “as in the intact run” should not imply identical admission rules. [R02][R11]

Restoring the same birth-time feasibility check removes one asymmetry but cannot guarantee exact accepted counts. State-dependent feasibility is different in independently evolving geometries. A rejection-free matched schedule needs an actual construction, not the word “matched.” Equal births also do not imply equal deaths, ages, integrated cost or sensing duration.

Trying random sites until one is feasible conditions the distribution on feasibility. This is a valid *new* null only if its candidate set, draw order, rejection handling and resulting conditional distribution are specified. It is not identical to one uniform draw over all sites. The inherited spiral rule also matters: a first valid point and a search for any cost-feasible point are not the same proposal law.

The five-percent unmatched threshold has no demonstrated experimental justification in the current handoff. Do not adjust it until seeds pass, discard the flagged seeds, or convert an infeasible comparator into a scientific failure of the intact mechanism.

### 8.4 Recommended immediate control experiment

For engineering, fork a complete state **before** one candidate growth event. Test a conditional candidate and a predeclared random alternative with the same integration law, same fixed external drive replay and identical cost checks. Retain rejection outcomes as part of the result; do not redraw until the desired answer appears. This isolates feasibility and short-horizon sensitivity without pretending to resolve the full longitudinal matching problem.

After that check, draft M’s long-run estimand explicitly. If a strict birth-count-and-time match is required, the design must show how both arms attain it under the same resource policy or label the departures and resulting conditional claim. Do not invent an unreviewed coupling/eviction scheme in the implementer.

### 8.5 Same seed is not the same experience

`Run.episode()` generates the world and sensor permutation from the episode index. Different medium seeds share that initial environment schedule. In closed-loop movement, different actions change later observations and drives. The intact birth schedule therefore carries information from the intact trajectory into a yoked control; it is not an exogenous randomization schedule. [R05]

Use open-loop input replay to answer mechanism questions and paired closed-loop worlds to answer controller-package questions. Clearly report which experiment was performed. Neither substitutes for the other.

---

## 9. Evaluation and causal qualification without circular gates

### 9.1 Preserve a ladder of claims

| Evidence | Allowed claim |
|---|---|
| Structural criteria and recovery pass | A driven structural snapshot meets the declared tests. |
| Readout is occupied and changes | The interface produces observable behavior. |
| Input changes alter later output | A scoped causal input-output response exists. |
| Score beats appropriate baselines on held-out cases | Task performance is demonstrated within that evaluation. |
| Matched learning/growth ablation changes performance | A contribution of the tested learning/growth component is supported. |
| A copied candidate retains function under its declared interface | Functional reuse in that context is supported. |
| Composition changes behavior and preserves child contracts | A scoped composition claim is supported. |

No later row follows from an earlier one alone. In particular, the 11,862 historical snapshots are not 11,862 independently discovered functional modules. G5 is carrier-shift covariance and can pass for default behavior. [R10]

### 9.2 Baselines should distinguish mechanisms, not just provide weak opponents

Retain default and random, evaluated on the same task panel. Add the smallest relevant controls when testing a stronger claim: a single driven oscillator, sample-and-hold for static memory, a fixed-size/frozen-adaptation medium for learning, and a fixed interface-matched construction for growth benefit. A conventional reference policy remains useful as a yardstick; it is not evidence the medium has access to the same information.

Use native oriented task units first. Report improvement over each comparator separately. A normalized score above zero can still be below the task’s default, particularly for `choose`. Numerical tolerance such as `1e-12` distinguishes stored equal values; it is not a meaningful behavioral effect size. Freeze meaningful margins and uncertainty procedures before confirmatory evaluation. [R03][R10]

Do not reject a perception relay because it merely transmits a bearing. That is an appropriate elementary capability. Do not claim multioscillator computation merely because it does so.

### 9.3 Intervention specification

| Intervention | Preserve | Alter | Interpretation limit |
|---|---|---|---|
| Cue-information scramble | Declared activity/strength statistics, workload and legal interface. | The task-bearing relation to the cue. | Specify a valid task counterfactual; arbitrary inconsistent channel combinations can create an out-of-distribution input. |
| Direct phase-coupling mask | Particle presence and other mechanisms as explicitly chosen. | Selected phase influence terms. | Tests that mechanism, not every geometry-mediated route. State whether normalization is preserved. |
| Physical member removal | Everything except a declared set of particles, with no hidden retuning. | N, forces, neighbour relations and phase coupling. | A lesion of the whole physical system, not a pure wire cut. |
| Output mask | Internal evolution. | Contribution of selected elements to readout. | Often establishes readout dependence trivially; it is not a sufficient computation test. |
| Restore / rescue | The original saved state and defined external drive. | Undo the intervention in a paired branch. | Helps separate mechanism disruption from irreversible damage or an unrelated state mismatch. |

Choose masks and analysis rules from protocol/development information before looking at the evaluated outcomes. Include a suitable sham or matched-size/location intervention where feasible. Do not require all three lesions to degrade all modules: redundancy can make one lesion nonessential, and a direct relay has no distinct internal cut. Mark such cases accurately rather than enforcing an impossible success definition.

For memory, compare prior cues with identical hidden inputs, and intervene separately during encoding and retention. A currently absent source edge is expected during hiding. Preserve the carrier/reference correctly; scrambling the carrier can test time reference rather than memory content.

### 9.4 Snapshot sampling and selection

The first twenty snapshots are a valid declared historical sample, not a representative inventory of everything the run eventually learned. Do not retroactively replace them. A later temporal/size-stratified diagnostic sample can reduce early-snapshot bias if its rule is fixed before examining test scores and its results remain separate. [R05][R10]

Best-task selection, repeated snapshots of one organization and shared evaluation episodes all induce dependence. Use the seed/run as the independent developmental unit for claims about growth, with snapshot-level data as nested descriptive evidence. If environmental generalization is claimed, independently vary the environment schedule as well; the current medium-seed replication is conditional on a shared schedule. [R05]

### 9.5 Fresh seeds must cover the claimed source of generalization

Fresh **medium seeds alone** do not provide fresh task stimuli. The current runner uses episode-indexed worlds and assignments, and the evaluator repeatedly uses its declared validation panel. A later seed manifest must name medium initialization, training-world schedule, site binding, control draws, intervention draws, calibration panel, development/selection panel and confirmation panel separately. Deliberate pairing is good; silently reusing an outcome-inspected evaluation panel as untouched evidence is not. [R03][R05][R06]

An existing normalization calibration may be retained as a disclosed fixed transformation. Its reuse does not make a reused evaluation panel fresh. No selection of the successful snapshot, decoder, growth rule, margin or ablation should depend on the same evidence subsequently presented as independent confirmation.

### 9.6 Numerical reproducibility is not scientific confirmation

Six positive directions out of eight have a one-sided fair-sign tail of 0.14453125; seven have 0.03515625; eight have 0.00390625. These are illustrative exact calculations under independent fair signs, not calibrated tests for all current endpoints. **C12** verifies the arithmetic.

Development continuation gates can use directional consistency, but should not be marketed as significance. Confirmation needs a specified effect, estimator, independent unit, error rate/multiplicity treatment and sample-size method checked for the actual design. More samples cannot rescue a representation that omits the needed distinction or establish superiority if the true effect is below the margin.

---

## 10. Engineering reliability and evidence lifecycle

### 10.1 Repairs that remain justified

The retained Codex recheck identifies receipt-aware aggregation debt in `development.execute_arm`, simulation work inside `section10.summarize()`, source-reference mapping after history cleanup, an old bundler that stages raw ledgers, repeated recovery-state storage, and incomplete resource/recovery guarantees. These are real follow-up engineering requirements, not reasons to expand the scientific ontology. [R10][R14][R15][R16]

A report API should accept immutable records and produce a new report without starting the world, loading the engine or modifying a historical receipt. Replay generation should be a separate explicit command with its own exposure record. A focused test should fail if the report path calls a simulation entry point.

Use a single explicit adapter between event rows and receipt-backed stores. Exercise that adapter with both in-memory and spooled data rather than repairing only the successful top-level wrapper.

### 10.2 Bounded storage and restart semantics

A future trace index should bind chunk order, schema, record counts, hash, source/config identity and recovery references. A strict chunk-size limit also needs a solution for one recovery event larger than the limit: content-address the large state and frame payload rather than simply splitting JSON mid-record. Newline/log compaction must preserve information unless a changed retention policy is explicitly approved.

Exclusive-create files and hashes do not create crash-safe resume. A resumable checkpoint must capture the complete medium and world state, RNG streams, clock, pending qualification futures, input schedules, task position, queues and committed output offset consistently. If that capability is not implemented and tested, state **resume unsupported**; interrupted runs remain partial/invalid under their protocol. Do not promise fault tolerance from append-only logging alone.

### 10.3 Resource and clock accounting

Distinguish simulated time, awake monotonic elapsed time, continuous elapsed/UTC duration, worker CPU time and summed worker time. Record actual platform clock semantics and host suspension, not merely a field called `wall_seconds`. An unattended-run power inhibitor is an operational measure, not a timing proof.

Before a resource-capped run, test bounded submission, absolute deadlines, child timeouts limited by remaining allowance, cancellation and cleanup with fake workers. A launch-time check before a large queued panel is not an interruption guarantee. Record memory/disk headroom and predicted trace output where they can stop a run.

The current recheck package contains only small standalone arithmetic tests and documents; it does not implement these project runtime repairs.

---

## 11. Corrected next-work plan

The sequence is designed to answer the next uncertainty with the least new machinery. Phase labels below are proposed work scopes, not replacements for repository milestone or scientific verdict labels.

| Phase | Concrete deliverable | Exit evidence | On failure / boundary |
|---|---|---|---|
| **N0 — reconcile the contract** | One compact interface/timing/null specification referencing existing owners. List current behavior, proposed amendments and deliberately deferred features. | Every required observable has an available input; every gate can be reached within its clock; both native/reference change points named. | Correct the specification. No large simulation. This R2 audit is input, not an approved replacement protocol. |
| **N1 — interface witnesses** | Tiny legal observation/drive fixtures for choose collisions, four-second cue encoding, hidden retention, zero-error move, output occupancy and directed influence. | Expected inputs/actions are explicit; negative fixtures fail for the intended reason; no answer computed secretly by the encoder. | Attribute failure to representation, decoder, acquisition or dynamics. Do not add a registry to fix it. Native fixtures require the scoped normal approval. |
| **N2 — minimal causal capability** | Paired hand-built baseline and mobile/fixed-geometry diagnostic branches; per-episode and short step traces. | A meaningful scoped response beats the applicable simple baseline, or a documented negative result explains the limit. | Write the failure report and choose only the affected mechanism for a new design. No claim of learning from a hand-built witness. |
| **N3 — growth/control feasibility** | One fully specified structural-demand candidate plus the owner-selected M/U roles, source-schedule rules, feasibility and mismatch accounting. | Birth/retention clocks are attainable; masks, resource laws and null distributions are executable; native/reference boundary checks agree. | Redesign the candidate or narrow the estimand. Never replace failed seeds or relax thresholds until results pass. |
| **N4 — bounded engineering integration** | Explicit task/case manifest, source/config freeze, read-only reporting, receipt/storage/deadline fixtures, complete budget estimate. | All promised tasks and memory phases actually occur; faults stop without corrupting receipts; trace output answers the causal questions. | Repair implementation only where the design is unchanged. A protocol change is versioned and reviewed. |
| **N5 — fresh developmental comparison** | Reviewed concrete design, owner approval, fresh registered development entropy and bounded execution. | All planned seed units reported; effect sizes, uncertainty, failures and resource exposure retained without task-selection leakage. | Preserve the result; report the specific failed assumption. No retrospective verdict rewrite. |
| **Later — reuse/composition** | Only when a useful copy motivates it: interface-aware type descriptor, context tests, then a small composition experiment. | Function survives the declared use context and composition effect has a matched explanation. | Keep it as future research; do not block N0–N4 on a general semantic registry. |

### How to choose among R6-3 options

A fixed passive output remains a sound starting interface. First determine whether legal input changes can affect that output on the needed timescale and whether the decoder can express the required action. If fixed geometry works and mobile geometry fails, investigate geometry/attachment. If neither works but a controlled low-capacity probe extracts the information, investigate the decoder. If the representation itself fails the collision test, change it before either growth or readout optimization.

Only after these distinctions are measured should the drafter choose guided growth, an explicit endpoint/boundary mechanism, a structure-relative interface, or a scoped alternative. All are hypotheses. The original strong preference for guided bridge growth was not justified by comparative evidence.

### What to freeze now, versus later

Freeze the current-source checkpoint, evidence/claim boundaries, diagnostic questions and seed separation now. Freeze numerical thresholds, decoder/growth choices and long-run estimands only in the resulting concrete reviewed design. Do not “freeze definitions” by prematurely making speculative data structures mandatory, and do not drift the user’s oscillator/growth goal into a conventional end-to-end neural network.

---

## 12. Rechecked research: what is usable and what was overstated

The corrected research question is not “which existing system looks like a living shape?” It is “which measured mechanism addresses one identified failure, under what assumptions, and how do we distinguish its contribution here?”

| Reference family | Use for this project | Important correction / transfer limit |
|---|---|---|
| AKOrN [S01] | Oscillatory binding and controlled computation comparisons. | Learned architecture/connectivity, not proof that current local growth/readout succeeds. |
| Phase oscillators with weight and structural plasticity [S02] | Explicit separation of dynamical and structural clocks. | Contact rewiring in a fixed population is not unit birth/death; do not copy timescales. |
| Task-driven oscillator structural search [S03] | Closest-prior-art check and supervised comparator. | Uses task-driven search/readout; novelty cannot be “oscillators plus growing connectivity.” |
| GWR / GNG / SOINN [S04][S05][S06] | Local representational demand, incremental complexity and deletion tradeoffs. | Their local error or maturity criteria are not proven causal task utility in this medium. |
| Homeostatic structural plasticity [S07] | Candidate local resource regulation. | Activity stability or network efficiency is not useful task computation. |
| Growing NCA [S08] | Separate formation, persistence and regeneration tests. | Gradient-trained local rule; not evidence of task-blind emergence. |
| Flow-Lenia [S09] | A resource-conservation comparison axis. | Different physical law and parameter-optimization story, not a ready-made budget fix. |
| Swarmalators and pinning [S10][S11] | Closest space/phase dynamics and a warning to label environmental changes. | The pinning study does not prohibit all endpoint anchors. |
| Mergeable nervous systems / self-assembly [S12][S13] | Later interface and compositional-context questions. | MNS has a centralized brain unit; these are engineered/learned modular systems, not proof that a nine-layer software ontology is needed now. |
| Cascade-Correlation / NEAT [S14][S15] | Reuse and innovation protection as later hypotheses. | Frozen incoming weights and population speciation do not derive this project’s lifecycle constants. |
| HTM implementation [S16] | Concrete ownership of segments/connections and C++/Python boundary examples. | Scoped source reading only; no recommendation to import its algorithm, dependency stack or licensed code. |
| E-prop [S17] | A possible later eligibility-learning comparison. | It remains gradient descent; no BPTT is not no gradients. |
| Physarum [S18] | Ask whether structural growth serves complete source–sink demand. | Transport flux is not information transfer or causal credit. |
| Reservoir-computing framework [S19] | A small trained probe can distinguish substrate information from fixed-decoder failure. | Capacity/training/input-only controls required; this remains a diagnostic, not automatic proof of grown intelligence. |
| CPG sensory feedback [S20] | Event-dependent timing as a later 0g hypothesis. | Locomotion findings do not derive combat dwell values. |
| Multihop swarmalators, 2026 [S21] | New comparison of local versus explicit multihop communication. | Uses hop-limited communication/flooding; do not import it as free physical locality. |

The earlier 2026 swarmalator citations were checked rather than discarded merely for being recent. The multihop paper was published on 18 August 2026; the survey [S22] is a 2026 publisher record. Existence of those publications does not validate the proposed algorithm.

### Scope of the comparison

`SOURCES.md` records exactly which materials were full HTML methods, abstracts, author records or code excerpts. Only the HTM files listed were inspected as an external implementation in this pass. I did not run the external systems, audit all their repositories, or reproduce their experiments. The SOINN tutorial timed out; its primary paper supplied the comparison instead.

A concise defensible novelty statement is: **this project explores a particular combination of mobile oscillator dynamics, local structural adaptation and tested reuse; several ingredients and some close combinations already exist.** This targeted search does not establish uniqueness, priority or empirical advantage. The exact novel contribution becomes meaningful when the successful mechanism and its controls are specified.

### A stronger comparator practice

For each borrowed idea, record: source result, assumption that makes it work, project mismatch, minimum implementation change, matched comparator, observable outcome and disconfirming result. If any of those is missing, keep the idea in research notes rather than the implementer’s mandatory instructions.

---

## 13. 0g: correct the existing state before proposing v4

The 0g v3 code already implements pair-mode hysteresis with strict thresholds above +0.2 and below −0.2, retaining mode at the exact boundaries. “Add hysteresis” is therefore not a new corrective mechanism. [R13]

At the reported natural rate magnitude 1.889 rad/s, the free oscillator’s full period is approximately 3.3262 seconds; its half-period is 1.6631 seconds. Coupling, input pressure and threshold placement affect real switches, so neither number is a substitute for actual pair-mode telemetry. C11 checks only the arithmetic. The retained recheck describes rapid reversals as a plausible limitation, not a counterfactual proof that reducing rate fixes the regular-opponent result. [R13]

The typical preferred-distance gap of roughly 336 px is useful for a feasibility diagnostic, not a universal dwell law. `gap / speed` is only a travel-time estimate. Effective radial progress can be zero or negative because of opposing forces, walls or target motion. A hard minimum dwell can then force a unit to persist in an impossible or dangerous action.

A later revision should define a **bounded progress-aware dwell/release policy** with explicit responses to target death, loss of target, infeasible retreat, lack of progress and urgent threat. Use actual projected relative progress, not simply catalogue top speed. Freeze emergency precedence and release/reset semantics; adding a dwell should not create an immortal mode.

Compare the same movement/timing wrapper on oscillator and morale controllers. Separate fixed-parameter mechanism ablations from equally retuned package comparisons. Preserve the current survivor-first S objective unless the owner approves a new one; report timeouts, surviving guns and destruction separately. Timeout survival is not synonymous with winning a destructive combat objective. [R13]

No 0g controller modification or new battle run is part of this audit.

---

## 14. Validation record and remaining uncertainty

### Completed standalone checks

| Check | Confirmed audit assertion |
|---|---|
| C01 | Legal choose observations can collide at the encoded input while target IDs differ. |
| C02–C03 | Memory activity cannot reach the proposed source-eligibility or reset-on-inactivity growth thresholds. |
| C04 | Fifty inherited-schedule episodes omit choose. |
| C05 | Input-drive and output regions overlap. |
| C06 | Radius and legal separation do not guarantee a directed nearest-eight connection. |
| C07 | Eighty-percent persistence of each edge does not guarantee a simultaneous full path. |
| C08 | A carrier-matched oscillator can retain an already encoded static cue. |
| C09 | Unit coherence does not encode zero movement error. |
| C10 | Birth feasibility does not by itself enforce continuous graph-dependent cost. |
| C11 | The reported 0g free full and half periods differ by two. |
| C12 | Six-of-eight directional consistency is not a conventional five-percent sign test. |
| C13 | Translating a module alone changes contact with fixed ports. |
| C14 | Phase locking can occur without causal coupling. |

The current receipt records **14 passed, 0 failed**. It includes script hash, constants, counterexample values and explicit limits. Reproduce from the extracted package using a new output path:

```sh
python3 checks/audit_checks.py --output evidence/COUNTEREXAMPLE_REPRODUCTION.json
```

The script refuses to overwrite an existing output. It does not load RPG_AI or use development/judging entropy. Initial audit-tool errors and the strengthened legal-separation fixture are preserved in `evidence/EXECUTION_NOTES.md` and `evidence/audit_history/`.

### Not established

This audit does not establish a working revised encoder, successful four-second acquisition, an effective growth law, sustained mobile attachment, a fair realized-matching longitudinal control, runtime performance, portability, or causal task superiority. Those are the next experimental questions. It also does not independently certify the large historical raw-ledger audit reported by Codex.

The downloadable Markdown has been checked for package/reference consistency and the archived originals remain byte-identical. Such checks support artifact integrity, not scientific correctness or a numerical quality rating.

### What “ready” should mean

**Ready for scoped engineering:** a concrete proposal has coherent interfaces, attainable clocks, explicit nulls, complete update order and bounded fixtures. An independent reviewer can see what would falsify it.

**Ready for a long developmental run:** the approved proposal has passed the relevant native/reference fixtures, evidence and budget checks, and the owner has approved that exact execution scope.

**Ready for stronger scientific claims:** new evidence supports the preregistered effect against appropriate baselines under calibrated uncertainty. A successful implementation or an attractive architecture diagram is not enough.

This R2 is a corrected research handoff. It should not assign itself “10/10” or certify the still-unbuilt mechanism.

---

## 15. Bounded next-agent brief

> **Repository:** `VasylHryha/RPG_AI`. Resolve current main, compare relevant changes against `fba4332a885fa6fa79526dc00045f30ae98cd92b`, and pin the actual inspected revision. Do not switch to `RPG_theory` or `astelia-hunte`.
>
> **Goal:** Make the next oscillator-growth experiment informative before expanding its module architecture. Preserve the user’s phase/locking/local-growth foundation and the historical bootstrap scope.
>
> **First batch:** Read this R2, the current 0h design/draft and the recheck. Produce a small contract plus bounded native fixture plan for: (1) choose representation collision, (2) four-second visible memory and twelve-second retention, (3) movement stopping/retreat, (4) directed transfer and output reach. State whether each deficiency is representation, readout, timing or dynamics. Reuse current histories. List Python and optimized-native change points.
>
> **Do not implement yet:** a semantic registry, recursive compositor, wholesale live-shape tracker, the archived B2 bridge pseudocode, score-selected task-blind library admission, a permanent pinning law, or a full developmental run.
>
> **Comparators:** default, random, lawful single-oscillator/static-memory baseline, and an appropriate fixed/untrained medium where learning is claimed. Preserve M as the owner’s registered-control role and U as descriptive; do not silently replace the null. Explain accepted-count, cost and input-exposure mismatches before proposing registration.
>
> **Evidence:** pure reports; separate explicit replays; per-episode score plus enough bounded input/output traces to establish the scoped effect; all faults and failed cases retained. No historical receipt rewrite or post-hoc seed replacement.
>
> **Deliver:** exact proposed amendments, tests and falsifying cases, source/parameter ledger, resource scope and remaining questions. Use the existing review/owner approval workflow for implementation and native execution. Do not claim that the fourteen standalone audit checks are project tests.

---

## 16. Final decision in one paragraph

The best next version is **not** the previous plan with more classes and stricter gates. It is a narrower experiment with a sufficient interface, task-compatible clocks, a tested decoder, genuinely defined controls and observable causal effects. Keep the native substrate, source/evidence discipline and task-blind bootstrap. Treat directed growth, anchoring, persistent module identity and recursive reuse as separately justified mechanisms rather than preselected necessities. That preserves the project’s direction while removing avoidable reasons for another expensive uninformative run.

---

## Source links and archive identity

`SOURCES.md` contains the annotated read scopes and transfer limits. Repository links below are pinned to the inspected commit. Original handoff links point to files inside the ZIP archive; their exact hashes are in `evidence/PREDECESSORS.json`.

[R00]: https://api.github.com/repos/VasylHryha/RPG_AI/branches/main "Branch identity"
[R01]: https://github.com/VasylHryha/RPG_AI/blob/fba4332a885fa6fa79526dc00045f30ae98cd92b/evidence/tactical_composition_demo/DESIGN_0H.md "DESIGN_0H revision 5.1"
[R02]: https://github.com/VasylHryha/RPG_AI/blob/fba4332a885fa6fa79526dc00045f30ae98cd92b/evidence/tactical_composition_demo/growing_shapes/medium/design_0h.py "DesignMedium / Frame / timers / growth"
[R03]: https://github.com/VasylHryha/RPG_AI/blob/fba4332a885fa6fa79526dc00045f30ae98cd92b/evidence/tactical_composition_demo/growing_shapes/runner/protocol.py "bindings / action / rotation / template"
[R04]: https://github.com/VasylHryha/RPG_AI/blob/fba4332a885fa6fa79526dc00045f30ae98cd92b/evidence/tactical_composition_demo/growing_shapes/world/world.cpp "World generator, visibility, correct_target and advance"
[R05]: https://github.com/VasylHryha/RPG_AI/blob/fba4332a885fa6fa79526dc00045f30ae98cd92b/evidence/tactical_composition_demo/growing_shapes/runner/run.py "Run lifecycle and native/reference dispatch"
[R06]: https://github.com/VasylHryha/RPG_AI/blob/fba4332a885fa6fa79526dc00045f30ae98cd92b/evidence/tactical_composition_demo/growing_shapes/runner/evaluator.py "copy_template / Evaluator.evaluate"
[R07]: https://github.com/VasylHryha/RPG_AI/blob/fba4332a885fa6fa79526dc00045f30ae98cd92b/evidence/tactical_composition_demo/growing_shapes/runner/qualification.py "start / finish / deviations"
[R08]: https://github.com/VasylHryha/RPG_AI/blob/fba4332a885fa6fa79526dc00045f30ae98cd92b/evidence/tactical_composition_demo/growing_shapes/runner/perf.cpp "Engine::record / endpoint / bindings / action"
[R09]: https://github.com/VasylHryha/RPG_AI/blob/fba4332a885fa6fa79526dc00045f30ae98cd92b/evidence/tactical_composition_demo/growing_shapes/medium/medium.cpp "Medium::neighbors / rhs / step / readout"
[R10]: https://github.com/VasylHryha/RPG_AI/blob/fba4332a885fa6fa79526dc00045f30ae98cd92b/evidence/tactical_composition_demo/growing_shapes/runner/DEVELOPMENT_RECHECK_REPORT.md "Codex retained-evidence recheck"
[R11]: https://github.com/VasylHryha/RPG_AI/blob/fba4332a885fa6fa79526dc00045f30ae98cd92b/evidence/tactical_composition_demo/DESIGN_0H_REV6_DRAFT.md "Unapproved revision-6 draft"
[R12]: https://github.com/VasylHryha/RPG_AI/blob/fba4332a885fa6fa79526dc00045f30ae98cd92b/evidence/tactical_composition_demo/growing_shapes/world/world.py "Library / World / Policy"
[R13]: https://github.com/VasylHryha/RPG_AI/blob/fba4332a885fa6fa79526dc00045f30ae98cd92b/evidence/tactical_composition_demo/astelia_cpp/S4_V3_RECHECK_REPORT.md "0g v3 recheck"
[R14]: https://github.com/VasylHryha/RPG_AI/blob/fba4332a885fa6fa79526dc00045f30ae98cd92b/evidence/tactical_composition_demo/growing_shapes/runner/section10.py "Long-run orchestration and summarize"
[R15]: https://github.com/VasylHryha/RPG_AI/blob/fba4332a885fa6fa79526dc00045f30ae98cd92b/evidence/tactical_composition_demo/growing_shapes/runner/development.py "execute_arm"
[R16]: https://github.com/VasylHryha/RPG_AI/blob/fba4332a885fa6fa79526dc00045f30ae98cd92b/evidence/tactical_composition_demo/growing_shapes/runner/trace_store.py "TraceStore"
[S01]: https://proceedings.iclr.cc/paper_files/paper/2025/hash/6d892051f91812700f427250e95e04f5-Abstract-Conference.html "Miyato et al. — Artificial Kuramoto Oscillatory Neurons (ICLR 2025)"
[S02]: https://www.nature.com/articles/s41598-022-19417-9 "Chauhan et al. — Dynamics of phase oscillator networks with synaptic weight and structural plasticity (2022)"
[S03]: https://www.nature.com/articles/s41598-022-19386-z "Feketa, Meurer and Kohlstedt — Structural plasticity driven by task performance leads to criticality signatures in neuromorphic oscillator networks (2022)"
[S04]: https://research.manchester.ac.uk/en/publications/a-self-organising-network-that-grows-when-required/ "Marsland, Shapiro and Nehmzow — A self-organising network that grows when required (2002)"
[S05]: https://proceedings.neurips.cc/paper/1994/hash/d56b9fc4b0f1be8871f5e1c40c0067e7-Abstract.html "Fritzke — A Growing Neural Gas Network Learns Topologies (NIPS 1994; proceedings 1995)"
[S06]: https://www.sciencedirect.com/science/article/pii/S0893608005000845 "Shen and Hasegawa — An incremental network for on-line unsupervised classification and topology learning (2006)"
[S07]: https://www.frontiersin.org/journals/synaptic-neuroscience/articles/10.3389/fnsyn.2014.00007/full "Butz, Steenbuck and van Ooyen — Homeostatic structural plasticity increases the efficiency of small-world networks (2014)"
[S08]: https://distill.pub/2020/growing-ca/ "Mordvintsev et al. — Growing Neural Cellular Automata (2020)"
[S09]: https://direct.mit.edu/artl/article/31/2/228/130572/Flow-Lenia-Emergent-Evolutionary-Dynamics-in-Mass "Plantec et al. — Flow-Lenia: Emergent Evolutionary Dynamics in Mass Conservative Continuous Cellular Automata (2025)"
[S10]: https://www.nature.com/articles/s41467-017-01190-3 "O’Keeffe, Hong and Strogatz — Oscillators that sync and swarm (2017)"
[S11]: https://doi.org/10.1103/PhysRevE.107.024215 "Sar, Ghosh and O’Keeffe — Pinning in a system of swarmalators (2023)"
[S12]: https://www.nature.com/articles/s41467-017-00109-2 "Mathews et al. — Mergeable nervous systems for robots (2017)"
[S13]: https://proceedings.neurips.cc/paper/2019/hash/c26820b8a4c1b3c2aa868d6d57e14a79-Abstract.html "Pathak et al. — Learning to Control Self-Assembling Morphologies: A Study of Generalization via Modularity (2019)"
[S14]: https://papers.nips.cc/paper_files/paper/1989/hash/69adc1e107f7f7d035d7baf04342e1ca-Abstract.html "Fahlman and Lebiere — The Cascade-Correlation Learning Architecture (NIPS 1989; proceedings 1990)"
[S15]: https://direct.mit.edu/evco/article/10/2/99/1123/Evolving-Neural-Networks-through-Augmenting "Stanley and Miikkulainen — Evolving Neural Networks through Augmenting Topologies (2002)"
[S16]: https://github.com/htm-community/htm.core/blob/master/src/htm/algorithms/Connections.hpp "htm-community/htm.core — README and Connections.hpp"
[S17]: https://www.nature.com/articles/s41467-020-17236-y "Bellec et al. — A solution to the learning dilemma for recurrent networks of spiking neurons (2020)"
[S18]: https://www.biology.ox.ac.uk/publication/46167/pubmed "Tero et al. — Rules for biologically inspired adaptive network design (2010)"
[S19]: https://research.ibm.com/publications/recent-advances-in-physical-reservoir-computing-a-review "Tanaka et al. — Recent advances in physical reservoir computing: A review (2019)"
[S20]: https://is.mpg.de/mg/publications/righetti_pattern_2008 "Righetti and Ijspeert — Pattern generators with sensory feedback for the control of quadruped locomotion (2008)"
[S21]: https://journals.aps.org/pre/abstract/10.1103/7krx-p6hm "Schref, Schilcher and Bettstetter — Swarmalator networks with multihop coupling (2026)"
[S22]: https://www.sciencedirect.com/science/article/abs/pii/S0370157326000165 "Sar et al. — Interplay of sync and swarm: Theory and application of swarmalators (2026)"
[H1]: archive/RPG_AI_0H_REV6_RESEARCH_AND_EXECUTION_PLAN_2026-10-06.md "Superseded first handoff — historical original"
[H2]: archive/RPG_AI_CURRENT_ARCHITECTURE_LIFECYCLE_AND_COMPARATIVE_SYSTEMS_RESEARCH_2026-10-06.md "Superseded architecture handoff — historical original"
