# RRG 0h — Revision 6 Functional Bootstrap: Recommended Design

**Date:** 2026-10-06  
**Project name:** **RRG**  
**Current GitHub repository locator:** `VasylHryha/RPG_AI`  
**Inspected baseline:** `main @ fba4332a885fa6fa79526dc00045f30ae98cd92b`  
**Status:** **RECOMMENDED DESIGN FOR CROSS-FAMILY REVIEW — NOT YET AUTHORIZED TO RUN**

> **Naming note:** `RPG_AI` above is only the literal current GitHub repository path. The project/theory name is **RRG**.

This document supersedes the assistant's earlier *forward design recommendations*. It does **not** rewrite historical Revision-5.1 evidence or owner decisions. It incorporates the R2 adversarial recheck and resolves the main open design choices instead of leaving them as a generic “next design pass.”

---

# 0. Decision

## What Revision 5.1 already established

Revision 5.1 answered one useful question:

> **Can the declared mobile oscillator medium + local growth rules produce many structurally qualified groups?**

Yes, within the scope of its detector. It produced 11,862 structurally qualified snapshots and passed the declared structural-formation row.

It did **not** establish useful computation.

The failed run therefore should not be repeated with only more seeds or a larger budget.

## What Revision 6 should answer

Revision 6 should ask one smaller question:

> **Can task-blind local growth populate a physically valid sensor/output interface such that the resulting oscillator population produces a useful, causally input-dependent phase response?**

That is all.

Revision 6 should **not** attempt to prove:

- recursive composition;
- a semantic shape library;
- arbitrary action representations;
- exact target-choice computation;
- general memory superiority;
- multilevel RRG;
- efficiency versus neural networks;
- a universal autonomous growth law.

Those belong later.

---

# 1. Why this is a better experiment

The earlier plans tried to fix too many things simultaneously:

- output reachability;
- drift;
- shape identity;
- semantic ports;
- recursive composition;
- causal credit;
- all four tasks;
- long-run controls.

That creates too many degrees of freedom.

The new strategy is:

```text
Revision 5.1:
    structural formation?  YES
    useful function?       NOT SHOWN

Revision 6:
    functional oscillator interface?  TEST THIS ONLY

Later:
    free structural growth + function
    reusable functional shape
    composition
    recursive composition
```

This gives each experiment one job.

---

# 2. Scope reduction: only two verdict tasks

Revision 6 uses:

1. **`perceive` — angular output only**
2. **`remember_static` — hidden-period angular output**

The training schedule and registered functional verdicts use only these two tasks.

## Why `perceive`

For every visible item, the current input preserves:

- physical input-site identity;
- item bearing in drive phase;
- distance monotonically in drive strength.

So the oscillator substrate receives the information required to improve angular perception.

The task also has multiple simultaneous inputs, making it more interesting than a one-signal relay.

The Revision-5.1 normalized `perceive` readout already judges angular error; distance error need not be used as the Revision-6 scientific endpoint.

## Why `remember_static`

It uses:

- one visible bearing for 4 seconds;
- no visible task input for 12 seconds;
- angular output only.

It provides a clean persistence test.

But it is **not** evidence of sophisticated memory by itself: a single oscillator or explicit sample-and-hold can solve a static cue. Those baselines are mandatory.

## Why `choose` is removed from the Revision-6 verdict

The existing representation is not sufficient for exact general choice.

Distance and health are combined into one drive-strength scalar. Legal situations can produce the same oscillator input while requiring different target IDs.

That is a representation problem, not a growth problem.

`choose` remains an engineering/research item for a later interface revision.

Do not “fix” it by calculating the correct priority in the encoder; that would move the decision outside the oscillator system.

## Why `move` is removed from the Revision-6 verdict

Current movement magnitude is decoded from readout coherence.

Coherence is a measure of phase alignment. It is not, by definition, movement error or distance-to-target.

Revision 6 should not simultaneously invent a new scalar action channel.

`move` is deferred until RRG has an explicitly tested scalar-output representation.

---

# 3. The central Revision-6 change: functional-overlap growth

The earlier bridge proposal was more complex than necessary.

The current geometry already contains a region where an oscillator can:

1. receive a sensor drive; and
2. contribute to the fixed origin readout.

## 3.1 Geometry

Sensor radius:

\[
R_s = 4.
\]

Strict sensor reach:

\[
R_d = 3.
\]

Strict output/readout reach:

\[
R_o = 2.
\]

Along the radial line between a sensor and the origin, direct sensor contact requires:

\[
4-r < 3 \Rightarrow r>1.
\]

Output contact requires:

\[
r<2.
\]

Therefore the direct functional-overlap interval is:

\[
1<r<2.
\]

That fact should have been checked before Revision 5.1.

## 3.2 New B1 placement meaning

Keep the *reason* for birth local:

> an active physical input site has accumulated unresolved service demand.

Change only where its service element is placed.

Instead of placing the newborn around the sensor centre at radius 4, place it inside that sensor's **functional-overlap lens** with the origin readout.

This creates a minimal physical route:

```text
sensor drive
    ↓
grown oscillator
    ↓
fixed readout
```

No task answer is injected.

The output remains passive.

## 3.3 Nominal overlap point

For physical site \(s\), let \(u_s\) be the unit vector from origin toward the site.

The nominal birth point is:

\[
q_s=r_* u_s.
\]

Use:

\[
r_* = 1.9.
\]

Reason:

- the input and output kernels both decay with squared distance;
- inside the radial overlap, their product increases toward the readout boundary;
- `1.9` retains the historical 0.1 spatial granularity as a strict-boundary safety margin;
- sensor distance is `2.1 < 3`;
- output radius is `1.9 < 2`.

This is an **engineering geometry choice**, not a theory constant.

It must receive an engineering sensitivity check at `r = 1.7, 1.8, 1.9` **without using task score to choose the winner**. The registered long-run value remains `1.9` unless the geometry fixture proves it invalid (collision/non-response/numerical-boundary failure), in which case the design must be revised before development.

## 3.4 Collision placement

Do not reuse the unbounded historical sensor spiral around this point.

Candidate offsets must remain inside the valid overlap.

Use this deterministic candidate list:

1. nominal point;
2. eight directions at radius `0.05`;
3. eight directions at radius `0.09`, half-step angularly offset.

All candidates must satisfy:

- strict sensor reach `< 3`;
- strict output reach `< 2`;
- separation `>= 0.05` from every live element;
- element cap;
- declared cost feasibility.

If all candidates fail, the birth is rejected as `placement`, `cap`, or `cost` with the exact reason.

No wider search is allowed in the same revision.

---

# 4. Growth demand: active exposure, not contiguous wall time

Revision 5.1 resets sensor novelty when a sensor becomes inactive.

That makes a 4-second visible memory cue incapable of accumulating the historical 20-second demand threshold.

Revision 6 changes the timer semantics, not the threshold.

For each physical site \(s\):

```text
unserved_active_time[s]
```

updates as follows:

### Site inactive

```text
timer freezes
```

It does **not** reset.

### Site active and currently served

```text
timer = 0
```

### Site active and unserved

```text
timer += dt
```

At the next normal 20-second growth check, a site whose timer is at least 20 active seconds may request a birth.

If the site is inactive at that check, the ready demand remains pending until a growth check at which the site is active.

After an accepted birth:

```text
timer = 0
```

This keeps the historical **20 seconds of unresolved demand**, but correctly interprets it as 20 seconds during which the input actually existed.

No special memory-task label enters the growth rule.

---

# 5. What “served” means

Do **not** make growth wait for an 80-of-100 wall-clock PLV criterion.

For Revision 6, service is deliberately structural and local.

An active physical site is **served** when there is at least one live element satisfying both:

\[
d(\text{element},\text{site}) < 3
\]

and

\[
d(\text{element},\text{origin}) < 2.
\]

That is: an element currently lies in the physical input/output overlap.

Why use geometry here?

Because birth answers the morphological question:

> is there a physical carrier through which this input can reach the output interface?

Phase usefulness remains something to **measure**, not something the birth rule assumes.

This also avoids making memory growth depend on a history window longer than a normal cue.

---

# 6. Element physiology stays almost unchanged

Revision 6 deliberately does **not** redesign the native oscillator law.

Keep:

- native spatial dynamics;
- native phase coupling;
- `A = 1`;
- `B = 1`;
- `J = 0.8`;
- `K = 1`;
- radius `3`;
- max neighbours `8`;
- geometry rate `1`;
- distance-weighted coupling;
- natural-frequency adaptation;
- gain adaptation;
- D1 low-lock death;
- D3 budget enforcement;
- newborn `ω = π`;
- newborn `g = 1`;
- 20-second newborn protection;
- `N_max = 64`;
- cost `N + 0.1 * undirected internal pairs <= 64`.

This is intentional.

If Revision 6 succeeds, we know the main new mechanism was functional placement/demand.

If it fails because mobile geometry drifts out of the overlap, that is a **specific result**. Do not hide it by adding pinning during the same revision.

---

# 7. Initial state

Revision 6 starts the task-blind intact medium **empty**.

Why:

- Revision 5.1 already established that random initial populations plus sensor-side growth can form structures.
- Revision 6 needs clean causal attribution of the functional interface.
- Starting with 24 random elements would allow useful output to arise from the initialization rather than the new growth rule.
- An empty start makes every live oscillator traceable to a declared demand event.

This is a deliberate break from Revision 5.1 and requires fresh seeds.

The random initialization is retained only as a **historical/descriptive comparator**, not mixed into the new intact arm.

---

# 8. Birth/update order

Keep one continuous medium clock.

At a normal growth check:

1. measure current lock/death data;
2. apply D1;
3. apply D3 until the resource contract is satisfied or protected-over-budget is recorded;
4. collect active sites whose `unserved_active_time >= 20s`;
5. process site IDs in deterministic ascending order;
6. accept at most **2 births total**;
7. use the overlap candidate search in §3.4;
8. emit complete event records;
9. reset only timers for accepted/served sites.

There is no B2, no chain-building rule and no new orphan rule in Revision 6.

That is a major simplification from the previous handoff.

---

# 9. Drift is measured, not silently “fixed”

Revision 5.1 observed extreme drift.

Revision 6 does not pretend that overlap birth alone solves it.

For every live element, retain/report:

- radius;
- current sensor reach;
- current output reach;
- age;
- lock;
- birth site;
- time since it last served an active site.

Report per seed:

- fraction of active-site time served;
- readout-empty fraction;
- births;
- deaths;
- replacements;
- cost exposure;
- maximum radius;
- median radius;
- service-loss events;
- duration of service gaps.

## Stop rule

Before a full development run, a 600-second mobile engineering fixture must show that the new interface is not immediately destroyed by geometry.

Pass the *engineering viability gate* only if:

- at least one non-default sensor→output response is observed after growth;
- that response survives for a complete 16-second evaluation episode without a complete readout-loss interval;
- the same result is reproduced in reference and native paths.

This is deliberately a minimal viability gate, not a scientific endpoint.

If it fails:

> stop Revision 6.

The next revision may test endpoint-local tethering, a boundary condition or another confinement mechanism.

Do **not** add a global spring and continue under the same revision.

---

# 10. Output decoder

Keep the existing fixed origin phase decoder for the two Revision-6 tasks.

For `perceive` scientific scoring:

- use **angular error only**;
- distance output is retained descriptively, not part of the R6 functional verdict.

For `remember_static`:

- use hidden-period angular error.

No trained decoder is added.

No MLP, GRU, BPTT or learned linear head enters the primary experiment.

---

# 11. Baselines that make the result interpretable

Default and random are necessary but not enough.

## B0 — default / abstention

Historical fixed output behavior.

## B1 — random action

Existing random policy.

## B2 — input-only phasor (`perceive`)

At each step, bypass the medium.

For active sensor drives with carrier-removed phases \(\alpha_s\) and strengths \(k_s\), compute:

\[
z_{\text{in}}=\sum_s k_s e^{i\alpha_s}.
\]

Output:

\[
\arg z_{\text{in}}.
\]

No learning.
No growth.
No oscillator dynamics.

Purpose:

> Does the grown medium do more than directly average the information already in the inputs?

This baseline receives exactly the same encoded inputs as the medium.

## B3 — one-oscillator memory

A single oscillator with the same natural band receives the visible memory drive and is then left to evolve during hiding.

Purpose:

> Does a multi-element grown structure retain information better than the smallest oscillator-native memory?

## B4 — explicit sample-and-hold memory

Store the last visible target bearing and replay it during the hidden period.

This will likely be extremely strong on `remember_static`.

Purpose:

> establish the trivial engineering ceiling; do not mislabel static retention as sophisticated memory.

Revision 6 does **not** need to beat B4 to be informative.

## B5 — fixed functional ring

Instantiate one oscillator at each of the eight nominal overlap positions from the start, with the same physiology but growth off.

Purpose:

> distinguish benefit of *having the functional geometry* from benefit of *growing it*.

This is critical.

If the fixed ring works and growth learns to construct comparable behavior, that is useful bootstrap evidence.

If growth works no better than the fixed ring, do not claim architecture discovery.

---

# 12. Causal / mechanistic diagnostics

Do not call PLV a causal path.

Revision 6 uses interventions matched to its actual mechanism.

## C1 — input phase scramble

On an isolated evaluation copy:

- preserve active sites;
- preserve drive strengths;
- preserve carrier rate;
- permute or independently rotate the task-bearing phase offsets using frozen intervention entropy.

Expected:

- task performance should deteriorate if behavior depends on input content.

## C2 — output mask

On an isolated copy:

- silence elements currently inside the output/readout region.

Expected:

- output returns to default/abstention or degrades strongly.

## C3 — internal-coupling ablation

For a matched isolated copy, instantiate the same state under a medium with internal phase coupling `K = 0`, while retaining external drives.

This is **not** the same as deleting elements.

Purpose:

> determine whether collective oscillator interaction contributes beyond independently driven port elements.

Interpret carefully:

- if behavior is unchanged, the module may be a set of independent transducers;
- if behavior degrades, internal coupling is functionally relevant.

For the R6 bootstrap, either result is scientifically useful.

## C4 — fixed geometry diagnostic

For selected engineering copies only, hold positions fixed while allowing phase dynamics.

Compare with normal mobile copies.

Purpose:

> separate phase-computation failure from spatial-drift failure.

This is an engineering diagnostic, not the registered long-run policy.

---

# 13. Controls

The owner already decided:

- **M** is the registered matched-birth comparison;
- **U** is the historical queue control, descriptive only.

Preserve that decision.

## 13.1 Control M in Revision 6

M receives the intact run's accepted birth **times and counts**.

At each corresponding birth event:

- choose a physical site uniformly from the 8 sites;
- use that site's **same functional-overlap placement region** as intact;
- choose newborn phase uniformly in `[0, 2π)`;
- same `ω`, `g`, protection and dynamics.

This matters:

> M must also be born into output-reachable geometry.

Otherwise an intact advantage could be explained merely by “intact was allowed to reach the output and M was not.”

### Resource handling

The owner's current matched-count decision requires exact birth count/timing.

Therefore M retains the draft's declared policy:

- cap/placement must be legal;
- cost may temporarily exceed 64;
- D3 resolves excess at the next growth check.

Do **not** pretend this is resource-identical to intact.

Report:

- time-integrated cost;
- time above budget;
- D3 removals;
- N;
- pair count;
- unmatched cap/placement births.

G0's wording must therefore be:

> **intact functional-overlap growth versus the declared matched-count randomized-site/random-phase Control M package**

—not—

> pure causal effect of need-driven placement/phase at identical resources.

### Mechanistic same-state branch

Separately, for engineering/mechanistic analysis:

- clone the exact intact state immediately before a birth;
- branch A uses intact site/phase;
- branch B uses a random site/phase drawn from the same feasible overlap candidate set;
- apply identical resource checks;
- replay identical fixed external drives.

This branch is the cleaner test of the local birth choice.

It does not replace owner M.

## 13.2 Control U

Keep Revision-5.1 U unchanged and descriptive.

It answers a different question:

> what happens under the old random-disk queue policy?

It receives no PASS/FAIL role.

---

# 14. Structural qualification

Keep the existing structural qualification machinery unchanged for Revision 6.

Continue to call its output:

> **structurally qualified driven snapshots**

Do not upgrade the language to autonomous organisms or functional atoms.

Keep:

- 601-frame structural window;
- frozen C4 criterion functions;
- perturbation-recovery check;
- exact snapshots;
- historical G1 interpretation.

Functional results are reported separately.

---

# 15. Functional readouts

Add separate Revision-6 functional rows.

## F0 — interface formation

Per seed:

- at least one demand-grown element enters functional-overlap service.

This is engineering/structural, not task success.

## F1 — active service

Report:

\[
\text{service fraction}
=
\frac{\text{active site-time with a serving element}}
{\text{active site-time}}.
\]

No universal scientific threshold is inferred from theory.

Development results report the distribution.

## F2 — perception utility

Primary R6 functional endpoint.

For each seed/copy:

\[
m_{\text{perceive}}
=
n_{\text{grown}}
-
\max(n_{\text{default}}, n_{\text{random}}, n_{\text{input-phasor}}).
\]

Report paired values and uncertainty.

A positive margin means the oscillator medium contributes beyond direct input averaging.

Do not average this away with `move` or `choose`.

## F3 — memory retention

During hidden `remember_static` decisions:

compare:

- grown medium;
- default;
- random;
- one oscillator;
- sample-and-hold.

The strong claim is **not** “beats sample-and-hold.”

The useful question is:

> does the grown oscillator state carry the previous cue into the hidden period, and how does that compare with the smallest oscillator-native mechanism?

## F4 — mechanistic dependence

Report changes under:

- input scramble;
- output mask;
- K=0;
- fixed geometry diagnostic.

No single ablation is automatically necessary/sufficient proof.

## F5 — copy covariance

Keep historical G5 separately.

Do not rename it functional copying.

---

# 16. What happens to G0 / G0′ / G1 / G5

## G0

Compare intact versus owner Control M.

Use:

- active service;
- `perceive` functional score/margin;
- resource exposure reported beside it.

`remember_static` is a secondary capability readout, not required to hide a perception failure inside an average.

This is development evidence.

## G0′

Replace the Revision-5.1 rejection-as-failure interpretation with explicit regulation categories:

- `demand-free`;
- `cost-limited`;
- `cap-limited`;
- `placement-limited`;
- mixed.

Always report:

- unresolved active demand;
- accepted births;
- rejected births by reason;
- deaths;
- turnover;
- N slope;
- cost;
- time above budget;
- service fraction.

Do not call a cost-pinned population self-limiting.

## G1

Unchanged structural formation row.

## G5

Unchanged carrier-shift numerical covariance row.

---

# 17. Engineering gates before a development run

A full run is forbidden until all gates below are satisfied.

## E0 — exact source contract

Pin:

- design;
- reference implementation;
- optimized/native implementation;
- world source;
- medium source;
- qualification source;
- evaluator;
- runner.

## E1 — geometry contract

For all 8 sites and every overlap candidate:

prove/test:

- `distance_to_sensor < 3`;
- `distance_to_origin < 2`;
- collision rule;
- strict-boundary behavior;
- exact reference/native agreement.

## E2 — empty-start growth

With an explicit engineering drive schedule:

- empty medium;
- demand accumulates only during active time;
- inactive periods freeze demand;
- growth occurs;
- no more than 2 births/check;
- event receipt exact.

## E3 — memory timing

Use an explicit schedule containing:

- 4 s visible;
- 12 s hidden;
- repeated cues.

Verify:

- inactive time does not erase accumulated demand;
- no hidden input is supplied accidentally;
- a grown element can be created after enough **active** unmet exposure.

## E4 — sensor→output response

Hand-built and grown overlap elements must show:

- input phase change changes decoded output phase;
- phase scramble changes/degrades output;
- output mask eliminates the response.

No task score is needed for this gate.

## E5 — collective diagnostic

For a fixed 8-port ring:

compare:

- K=1;
- K=0;
- input-only phasor.

Use a deterministic multi-input phase set.

This tells us whether coupling changes the input transform before a task run.

## E6 — mobile-geometry viability

600 simulated seconds.

Require the minimal viability condition in §9.

Retain complete service-loss/radius traces.

Failure stops the revision.

## E7 — explicit task manifest

Do not say “50 episodes covers everything.”

The smoke manifest explicitly contains:

- perception cases with K = 3 and K = 8 items;
- nearest-item swaps;
- symmetric/opposing bearings;
- memory visible→hidden;
- changed memory cue;
- repeated physical-site permutations.

Each case names its seed/input and expected diagnostic property.

## E8 — Control M fixture

Confirm:

- matched birth events are consumed exactly;
- M placement stays in overlap geometry;
- random phase/site entropy is separate;
- cap/placement mismatch is recorded;
- cost asymmetry is measured, not hidden.

## E9 — reference/native equivalence

All changed lifecycle/binding behavior must match between:

- Python reference;
- optimized native path.

## E10 — evidence runner repair

Before any long run:

- report generation is read-only;
- no summary function runs extra episodes;
- receipt-aware aggregation works;
- ledgers stay outside git;
- chunked/content-addressed evidence;
- absolute/awake timing retained;
- deadline enforcement bounded;
- interruption leaves valid partial evidence.

---

# 18. Development execution

Only after:

1. design review passes;
2. E0–E10 pass;
3. owner approves this exact revision;
4. cost projection passes the declared resource limit.

## Independent unit

The **medium seed/run** is the developmental unit.

Snapshots and evaluator episodes are nested observations, not independent replicates.

## Seeds

Use fresh Revision-6 medium entropy.

Use explicit separately named entropy domains for:

- initial medium;
- world schedule;
- site permutation;
- M site/phase;
- interventions;
- evaluator panel.

Because intact starts empty, the medium seed affects dynamics/entropy but not a hidden random 24-element scaffold.

## Environment schedule

Development may deliberately pair intact/M on the same world schedule.

That is pairing, not independent environmental replication.

A later confirmation run must use a fresh world schedule if a generalization claim is made.

## Number of seeds

Eight seeds may be retained as a **developmental attainability** design for continuity.

Do not call 6/8 a conventional statistical confirmation.

A later confirmation sample size is designed from the observed Revision-6 effect/noise after the mechanism is frozen.

---

# 19. Pass/fail interpretation

Revision 6 should not have one giant verdict hiding different failures.

## Case A — no output response in E4

Cause:

> interface/phase transfer failure.

Do not run development.

## Case B — fixed ring works, grown interface does not

Cause:

> growth/lifecycle failure.

Do not redesign decoder.

## Case C — fixed geometry works, mobile geometry fails

Cause:

> spatial persistence/drift failure.

Next revision investigates confinement/attachment.

## Case D — input-only phasor equals or beats grown medium on perception

Cause:

> oscillator substrate adds no demonstrated perception computation under this task/interface.

This is a valid negative result.

## Case E — K=0 equals K=1

Cause:

> useful behavior may come from independent driven port elements rather than collective oscillator interaction.

Do not claim collective computation.

## Case F — memory equals one oscillator

Cause:

> no evidence that a multi-element shape is needed for static retention.

Still useful as a capability result.

## Case G — useful perception + K dependence + growth constructs the interface

This is the strongest desired Revision-6 outcome.

Allowed claim:

> task-blind local growth constructed an output-reachable oscillator population whose coupled dynamics improved angular perception beyond direct input averaging under this sandbox.

That would be real progress.

It still would not prove recursive RRG.

---

# 20. What is explicitly deferred

Do not implement these before Revision 6 answers its question:

- general `ShapeInstance`;
- semantic `ShapeRegistry`;
- pose-normalized type deduplication;
- recursive compositor;
- shape-level reproduction;
- multilevel effective phase;
- output-port type system;
- learned decoder;
- reward-arm credit assignment;
- generalized `choose`;
- generalized scalar `move`;
- global pinning;
- orphan ecology;
- evolutionary search;
- end-to-end gradient training.

These remain research topics.

---

# 21. What comes after Revision 6 if it works

## Revision 7 — free growth to functional geometry

Relax the engineered overlap placement.

Ask whether local rules can **discover/maintain** the same useful interface instead of being born directly into it.

This is where guided bridge growth, local trophic fields or structural path reinforcement belong.

## Revision 8 — reusable functional snapshot

Take a successful structure and test:

- exact copy;
- translation/rotation where meaningful;
- changed context;
- damage/recovery;
- functional reproducibility.

Only then introduce a reusable semantic type.

## Revision 9 — two-component composition

Connect two proven functional modules.

The composition experiment must test an effect neither module achieves alone.

## Later — recursive RRG

Only after successful composition:

```text
elements
→ functional module
→ reusable module
→ composite module
→ composite becomes a unit
→ next level
```

That is the final RRG program.

---

# 22. Why this is preferable to the earlier bridge plan

Earlier proposal:

```text
sensor-connected component
→ frontier
→ guided intermediate births
→ persistent influence graph
→ orphan pruning
→ functional registry
```

Problems:

- unnecessary because sensor/readout regions already overlap;
- introduced many new constants/rules;
- mixed drift repair with path construction;
- conflicted with memory timing;
- overbuilt future module architecture;
- created more places for causal overclaim.

Recommended Revision 6:

```text
unserved active port
→ one local demand timer
→ one output-reachable birth rule
→ unchanged oscillator physics
→ fixed decoder
→ simple baselines
→ direct causal diagnostics
```

Fewer changes make a successful or failed result much easier to interpret.

---

# 23. Exact implementation ownership

## `medium/design_0h.py` / equivalent new Revision-6 adapter

Change:

- start empty;
- active-time demand timers;
- functional-overlap `served()` rule;
- overlap birth placement;
- exact event fields.

Preserve old Revision-5.1 adapter unchanged for history.

Create a new revision-specific adapter/file rather than silently mutating the historical contract where possible.

## `runner/protocol.py` / new revision protocol

Change:

- R6 task list = `perceive`, `remember_static`;
- R6 rotation;
- R6 endpoint definitions;
- keep phase action decoder for these tasks.

Historical Revision-5.1 protocol remains pinned.

## optimized native path

Mirror every changed rule exactly.

No Python-only experimental semantics in the long-run path.

## evaluator

Add explicit baseline/intervention evaluators.

Do not let `summarize()` trigger evaluation.

## controls

Add new R6 M behavior while preserving historical U.

## readouts

Add R6-specific rows/labels.

Do not edit historical verdict logic to retrospectively change Revision 5.1.

---

# 24. Reviewer checklist

A cross-family reviewer should return **CHANGES_REQUIRED** if any answer is “no.”

- [ ] Does every R6 verdict task have enough encoded information for its claim?
- [ ] Is `choose` excluded from the R6 verdict?
- [ ] Is `move` excluded from the R6 verdict?
- [ ] Is overlap geometry correct under strict boundaries?
- [ ] Does inactive time freeze—not reset—unserved demand?
- [ ] Does growth remain task-score blind?
- [ ] Is no target answer calculated in the growth rule?
- [ ] Does M also receive output-reachable geometry?
- [ ] Is M's resource asymmetry disclosed rather than called matched-resource?
- [ ] Are input-only, one-oscillator and fixed-ring baselines present?
- [ ] Is K=0 distinguished from element deletion?
- [ ] Is drift a measured failure mode rather than hidden by pinning?
- [ ] Are structural and functional qualification separate?
- [ ] Are Python/native implementations tested for equivalence?
- [ ] Is report generation read-only?
- [ ] Are development and confirmation claims separated?
- [ ] Are deferred module/composition features truly deferred?

---

# 25. Final approval position

I would approve **this direction** for implementation review.

I would **not** approve another full Revision-6 development run until E0–E10 pass and the exact repository specification receives the normal cross-family and owner approval.

The conceptual quality improvement is that Revision 6 now has **one scientific job**:

> grow an output-reachable oscillator interface and determine whether its dynamics contribute useful perception/persistence beyond trivial baselines.

If it passes, we have a real functional foundation to build RRG composition on.

If it fails, the failure identifies one concrete layer:

- transfer;
- growth;
- geometry;
- coupling;
- decoder;
- or representation.

Either outcome is informative.

---

# 26. Final goal

The final RRG goal remains:

> **simple local dynamical elements self-organize into useful structures; useful structures become reusable units; reusable units compose into larger useful structures; and that process can repeat across levels.**

Revision 6 is not the final proof.

It is the smallest clean experiment that can give that program a functional foundation instead of another structurally interesting but behaviorally silent medium.

