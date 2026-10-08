# RRG 0g — Low-Loss Streak Research: Final Recheck and Replacement Plan (R3)

**Date:** 2026-10-08  
**Project:** RRG  
**Pushed repository state reviewed:** `6dd80506403fec95915eea7da003a174e9515cf3`  
**Local feedback basis:** `RRG_0G_LOW_LOSS_STREAK_RESEARCH_FEEDBACK_CLAUDE_2026-10-08.md`  
**Disposition on the prior revised note:** **CHANGES_REQUIRED**

This document supersedes `RRG_0G_LOW_LOSS_STREAK_RESEARCH_REVISED_2026-10-08.md`.

It is a research/design handoff. It does not authorize a run, change a registered result, or replace the owner-approved repository specification without an explicit amendment.

---

# 0. Final judgment

The previous revised note had a good central diagnosis but was not yet a 9+/10 handoff.

It correctly incorporated:

- full healing means end-of-fight residual HP does not carry over;
- copied reaction/dodge is a script gain, not an RRG mechanism;
- holding fire has a throughput cost;
- a wounded unit must remain in the battle;
- launch synchronization is not the same as time-on-target;
- ranged units have a measured engagement defect;
- search/teacher behavior must be labelled as script/search.

But it still had six major problems:

1. It said its order matched the current owner decision when the pushed owner-approved order is still:
   ```text
   react → V1 timing → V2 geometry
   ```
2. It omitted **V2 artillery geometry**, despite strong project-specific evidence for the existing artillery planner.
3. It reduced the carry-over objective to a simple lexicographic death count, ignoring nonlinear survivor composition and fight number.
4. Its time-on-target rule would let the slowest gun hold the entire battery and omitted cast/wind-up semantics.
5. Its engagement and lethal-rotation rules were not executable under the current arbitration/information contract.
6. It did not preserve the exact V1 decision rule already approved in `SHAPE_LAB_SPEC.md`.

The corrected plan below fixes those issues.

---

# 1. Source authority and current status

## 1.1 Pushed owner-approved project order

Current pushed sources say:

```text
react
→ V1 timing
→ V2 geometry
```

Decision 0033 additionally says:

- mechanism metrics first;
- paired outcome looks at 50, 100 and 200;
- stop when clear;
- do not chase effects invisible at that scale;
- current base = always-commit/P16 + react;
- RRG oscillator's job is battery synchrony.

## 1.2 Claude feedback

Claude's later feedback proposes:

```text
running V1
→ ranged engagement floor
→ predicted-lethal rotation
→ cooldown-aware kiting
→ true time-on-target
→ dodge-profile aim
→ search teacher
```

That is a useful **proposed amendment**, not yet the same thing as the pushed owner-approved order.

## 1.3 This document's recommendation

Do not silently pretend the two orders are identical.

Use this rule:

1. Finish the already-declared V1 timing comparison.
2. Apply the V1 decision rule exactly.
3. Proceed to **V2 geometry** under the current owner-approved order.
4. Then test the ranged engagement floor, predicted-lethal rotation and cooldown-aware kiting.
5. Permit a **V1b true-time-on-target witness before V2 only if V1's mechanism evidence specifically shows that launch synchronization fails because landing times remain dispersed**.

Changing this order requires an explicit owner amendment. The rationale for retaining V2 next is strong: the historical Astelia artillery planner already improved damage per shell from 17.9 to 21.9 (+22%), preserved fire rate, shortened fights by 17%, and was accepted at +1.64 margin in its veteran comparison. This is more direct project evidence than currently exists for the engagement floor's combat outcome.

---

# 2. Recheck findings

## F1 — HIGH: the revised note falsely called a proposed order authoritative

### Problem

The prior note says:

> "This order matches the current owner decision."

It does not.

The current pushed specification says `react → V1 → V2`.

### Fix

Separate:

- **authoritative current order**;
- **Claude's proposed amendment**;
- **this review's recommendation**.

No plan file should be described as changed until the owner records that change.

---

## F2 — HIGH: V2 geometry was omitted

### Problem

The prior revised order goes from V1 timing to ranged engagement, rotation, kiting, time-on-target and GuessFactor-style aiming.

It omits the existing owner-approved V2 geometry phase.

### Why this matters

The historical engine already has a substantial artillery teacher:

- escape-model forward prediction;
- cluster selection;
- focus/net/wall/trap/sweep candidates;
- delayed finisher patterns;
- +22% damage per shell;
- same fire rate;
- 17% shorter fights;
- accepted +1.64 veteran result.

That is exactly the kind of "big lever already present in the engine" the project wants to copy, compare and later rebuild as an RRG shape.

### Fix

Restore V2 geometry immediately after V1 unless an owner amendment changes the order.

Keep timing constant when testing geometry.

---

## F3 — HIGH: "alive versus dead is the only currency" is directionally right but incomplete

### Correct part

With full healing, terminal HP does not carry over.

### Missing parts

The following still matter:

- role composition;
- whether at least one effective gun survives;
- fight number in the 10-fight series;
- tactic distribution;
- whether the fight was won by elimination;
- uncertainty in the comparison.

Ten surviving melee are not necessarily equivalent to ten surviving guns/ranged.

A death in fight 1 can affect nine future fights. A death in fight 10 does not affect a future fight, although the owner still prefers fewer losses.

### Correct series value

For a future search/tuning evaluator, use the already-reviewed project definition:

\[
J_\pi(s,a,k)
=
E_\pi[
  I(\text{fight }k\text{ won by elimination})
  (1 + V_\pi(M,k))
  \mid s,a
].
\]

Where:

- \(M\) is the actual surviving role composition at the canonical terminal;
- survivors then heal;
- \(V_\pi(M,k)\) is expected additional wins from the remaining fights under a named continuation policy \(\pi\).

Do not replace:

\[
E[V_\pi(M,k)\mid win]
\]

with:

\[
V_\pi(E[M\mid win],k)
\]

without measuring approximation error.

### Development selection without a fitted continuation model

Until \(V_\pi\) exists:

1. elimination win first;
2. paired streak / reach probability where available;
3. fewer own deaths when outcome estimates are tied;
4. retained effective guns;
5. total survivors by role;
6. elimination time.

At fight 10, still use the loss-aware tie-break because the owner asks to avoid losses even though there is no future continuation.

---

## F4 — HIGH: deaths conditional on wins can mislead

### Problem

"Deaths per won fight" is important, but not sufficient.

An arm can appear low-loss because it wins only easy fights and loses hard ones.

### Required reporting

For every comparison:

- win/loss/timeout;
- deaths on wins;
- deaths on losses;
- unconditional deaths over all paired fights;
- survivors by role;
- tactic-specific cells;
- series reach probabilities.

Do not optimize only losses conditional on wins.

---

## F5 — HIGH: the time-on-target formula was underspecified and could recreate the hold-fire failure

### Problem

The prior formula:

```text
T = max_i(ready_i + flight_i)
fire_i = T - flight_i
```

implicitly includes every gun.

One late gun can force the entire battery to wait.

It also omits:

- cast/wind-up time;
- exact release semantics;
- target/aim cohort;
- legality changes;
- target motion;
- one/two-gun fallbacks.

### Correct V1b witness

First define a volley cohort:

```text
same declared target / aim cluster
gun is alive
target is legal
gun's earliest feasible release lies within MAX_WAIT
```

For each candidate gun:

```text
tau_i =
    remaining readiness
  + cast/wind-up-to-release
  + projectile flight time
```

Select a common impact time \(T\) and participating subset \(S\) such that:

```text
release_i = T - (windup_i + flight_i)

release_i >= earliest_legal_release_i
release_i - now <= MAX_WAIT
```

Do not require every living gun to join.

A minimal deterministic witness:

1. sort compatible guns by earliest feasible impact;
2. choose the earliest \(T\) that forms a cohort of at least two guns;
3. exclude later outliers;
4. one gun uses ordinary fire;
5. cancel a member if legality changes.

Use the engine's actual projectile/cast timing functions, not a hand-estimated travel speed.

### When V1b is justified

Run V1b only if one of these is true:

- launch synchronization tightens launches but landing spread remains materially large;
- central/oscillator timing shows a mechanism signal but outcome is inconclusive because impacts remain staggered;
- stored flight-time variation is large enough to make launch-sync a poor approximation.

Do not run it merely because V1 loses.

---

## F6 — HIGH: the V1 decision rule was weakened

### Current approved V1 reading

Keep exactly:

- **RRG earns the job:** oscillator clearly beats base on mechanism and outcome at decision-0033 scale, and is not clearly worse than central sync.
- **Script is better:** central sync clearly beats oscillator; keep the script atom and give the oscillator another job.
- **No clear difference:** stop; do not chase it with more fights.

### Required mechanism metrics

- landing-time spread;
- launch-time spread;
- enemy dodge success;
- hits per shell;
- shells per kill;
- hold-induced idle time;
- shells per gun-minute;
- kills per gun-minute;
- behavior with 1–2 guns;
- cluster splitting / unsynchronized surviving subgroups.

Tighter timing is not enough if throughput loss erases the gain.

---

## F7 — HIGH: ranged engagement floor lacked action arbitration

### Problem

The prior rule could override dodging, casts or an already useful movement.

It could also walk ranged units directly into artillery danger.

### Correct minimal E1 rule

Base remains:

```text
always-commit + react
```

Action precedence:

```text
terminal / invalid
→ reaction/dodge
→ already committed cast/attack release
→ engagement floor
→ inherited formation/move
```

Rule:

```text
if no active reaction
   and no committed attack/cast that must complete
   and a visible target chosen by the unchanged selector exists
   and target is outside own legal firing reach:

       move toward the nearest legal point
       that places the target just inside own reach
       using the engine's real body/range semantics

else:
       inherit base behavior
```

For the first experiment:

- no kiting;
- no new target selector;
- no artillery anchor requirement;
- no global threat optimization;
- reaction/dodge still protects against visible shells/casts.

### Mechanism gate

Measure first in D5 / ranged-only drill:

- ready-to-fire time;
- in-range time;
- shots actually fired;
- firepower utilization;
- reaction overrides;
- ranged deaths.

Only proceed to 50/100/200 paired C3 if it actually raises engagement.

---

## F8 — HIGH: predicted-lethal rotation was not executable and risked repeating the old failed wounded rule

### Information boundary

First version may use only:

- in-flight visible shells/shots;
- predicted legal landing regions exposed by the adapter;
- enemy cast/wind-up already committed to a visible target;
- current positions, velocities and HP.

Do not infer unobserved cooldowns or future target choices.

### Arbitration

```text
reaction/dodge tries first
```

Predicted-lethal rotation activates only when:

```text
base + current reaction still predicts lethal committed damage
```

### Counterfactual trigger

For unit \(u\):

```text
D_base =
    committed visible damage predicted at base/react trajectory

for each candidate retreat point p:
    D_p =
        same committed threats evaluated at p's reachable trajectory

trigger only if:
    D_base >= hp(u)
    AND min_p D_p < D_base - MARGIN
```

Prefer a point that makes \(D_p < hp(u)\).

### Participation rule

A candidate is legal only when at least one is true:

- unit remains in own firing reach of a visible target;
- time to the next legal shot remains below a registered participation horizon;
- no such point exists, and this point is the nearest behind-friend survival point within a maximum retreat distance.

The unit does not run to the map edge.

### Required evidence

- activations;
- counterfactual predicted deaths;
- triggered-unit survival;
- false extractions;
- shots/firepower lost while rotating;
- deaths prevented;
- win regression.

This distinguishes the new rule from the historical HP-threshold pull-back that showed no gain.

---

## F9 — MEDIUM: cooldown-aware kiting used the wrong timing primitive

### Problem

Remaining weapon cooldown alone is not enough.

The next attack may include:

- acceleration;
- movement;
- wind-up;
- target movement;
- attack-release constraints.

### Correct rule

Only kite if there is a clear range/mobility advantage.

Use:

```text
time_to_next_legal_fire
```

rather than raw cooldown.

```text
if target outside own range:
    advance

elif attack can release now:
    fire

elif no range/mobility advantage:
    inherit base / local safety move

else:
    compare:
        time to retreat and re-enter legal fire
        versus time to next legal fire

    retreat only if it does not delay the next shot
```

Candidate retreat points must also avoid visible third-party threats.

Reaction/dodge retains precedence.

---

## F10 — MEDIUM: series evaluation was under-specified

The lab uses random draws with replacement, like historical `DRAW=any`.

### Required pairing

Across arms:

- identical draw stream;
- identical initial placements;
- separate controller RNG;
- same fresh enemy army per fight index;
- arm-specific survivor composition naturally diverges.

### Report

For each arm:

- streak distribution;
- paired streak delta;
- \(P(streak \ge k)\) for \(k=1...10\);
- roster by role before each fight;
- failure tactic;
- deaths on won and lost fights separately;
- unconditional deaths;
- fight duration;
- timeouts.

Ten paired series are descriptive development evidence, not a precise population estimate.

Fresh paired C3 at 50/100/200 remains the main decision instrument.

Historical comparisons must use the matched `DRAW=any` rows, not fixed-list or `pool` rows.

---

## F11 — MEDIUM: "nobody reached 6–8" was too absolute

Use:

> No matched project evidence reviewed here establishes a 6–8 average/streak under the current harder rules.

The older 6.1–6.5 results used materially different shell-dodge conditions.

Under later universal shell dodging, matched historical performance fell sharply; the current elite reference is roughly three fights in the current lab setup.

So 6–8 is a new target under current rules, not a recovered same-condition baseline.

---

## F12 — MEDIUM: search teacher boundaries were incomplete

Keep two separate labels:

### Oracle teacher

May use:

- true tactic;
- hidden state;
- fuller clone rollouts.

Use only as an upper reference/diagnosis.

### Deployable teacher

Uses only:

- public unit/projectile/cast observations;
- no tactic ID;
- no enemy RNG;
- no hidden internals.

Before any clone-search teacher:

- branch/main continuation parity or measured ranking error;
- coupled random streams across alternatives;
- exact canonical terminal;
- no projectile damage after fight terminal;
- measured branch cost.

Search remains script/search, not the RRG mechanism.

---

## F13 — MEDIUM: the raid/intercept candidate disappeared

Claude's feedback correctly kept this conditional.

After engagement floor and kiting:

```text
if wolfpack/storm remains a dominant failure:
    test a raid detector + intercept-point movement
```

Do not build it before confirming the failure remains.

Use visible closing velocity/time-to-guns only.

---

## F14 — MEDIUM: the revised note lost its source register

A research handoff must distinguish:

- project measurement;
- owner decision;
- external literature;
- inference.

The replacement plan restores that separation below.

---

# 3. Correct final execution order

## Stage 0 — finish V1 timing as declared

Arms:

```text
A base: always-commit + react
B base + scripted central launch sync
C base + local RRG battery oscillator
```

No target/aim/movement change.

Read mechanism first.

Apply the exact approved V1 decision rule.

Do not extend beyond 200 paired fights.

---

## Stage 0b — conditional true-time-on-target witness

Only if V1 diagnosis justifies it under F5.

This is a script witness.

It does not silently replace V1 or award the oscillator the job.

If TOT succeeds, a later oscillator revision may synchronize predicted impact phase.

---

## Stage 1 — V2 artillery geometry, current owner-approved next stage

Use the engine's artillery planner as the script teacher.

Hold the chosen V1 timing policy constant across geometry arms.

Comparison:

```text
current P16 aim/geometry
vs
copied artillery-plan teacher
vs later RRG geometry shape
```

Do not mix timing and geometry attribution.

Mechanism metrics:

- damage per shell;
- targets affected per shell;
- expected vs actual damage;
- shells per kill;
- fire rate;
- fight duration;
- own losses while enemy artillery remains alive;
- tactic cells.

The existing project evidence makes this a higher-confidence next stage than GuessFactor from scratch.

---

## Stage 2 — ranged engagement floor

Use F7.

One movement change only.

If mechanism utilization does not improve in 10–20 paired drill fights, stop.

If it improves, continue to C3 50/100/200.

---

## Stage 3 — predicted-lethal rotation

Use F8.

Do not reuse the old HP-threshold pull-back.

Do not let units leave the fight.

Run only after engagement-floor behavior is frozen, so extraction is measured against an active ranged unit rather than the old inactive one.

---

## Stage 4 — cooldown-aware kite band

Use F9.

Only if engagement floor raises participation but casualties remain high.

---

## Stage 5 — dodge-profile / statistical aim

First compare against the existing artillery-plan teacher.

Then, if needed, use wave/GuessFactor-style escape distributions.

For splash:

```text
maximize probability mass covered by splash disk
```

not exact point-hit probability.

---

## Stage 6 — conditional raid interception

Only if wolfpack/storm remains dominant after Stages 2–4.

---

## Stage 7 — look-ahead/search teacher

Use as:

- upper bound;
- label generator;
- disagreement detector;
- later distillation source.

Never call it the RRG mechanism.

---

# 4. Candidate-selection contract

## Mechanism stage

10–20 paired fights.

The mechanism must visibly activate and move its declared metric.

Examples:

- V1: landing spread / hold cost;
- engagement: firepower utilization;
- rotation: predicted lethal threats avoided;
- kiting: firing uptime while outside enemy reach;
- V2: damage per shell / coverage.

No activation = inert, stop.

## Outcome stage

Paired looks at:

```text
50
100
200
```

A big lever should show approximately one of:

- about ±10 percentage points elimination wins;
- about 2 units saved per fight;
- clear streak/reach improvement.

Stop early when clearly positive or negative.

No fourth-decimal chase.

## Tactic-level guards

Always report all 20 tactic cells.

A global average can hide a wolfpack/storm regression that dominates the streak.

Do not silently tune on those cells after reading them; a design change means fresh development entropy.

---

# 5. Script versus RRG labels

| Mechanism | Label |
|---|---|
| P16 focus | script |
| copied react/dodge | script |
| central launch sync | script |
| true time-on-target | script |
| engine artillery planner | script/search |
| look-ahead teacher | script/search |
| local battery oscillator | RRG mechanism |
| future locally coupled geometry/routing shape | RRG mechanism only after it uses local dynamics rather than copied centralized decisions |

A script gain is still valuable engineering evidence.

It is not evidence for the RRG mechanism until the RRG form is compared directly on identical fights.

---

# 6. Ranked next three after the current V1 finishes

Under the currently pushed owner-approved order:

1. **V2 artillery geometry**
2. **Ranged engagement floor**
3. **Predicted-lethal rotation**

Conditional insertion:

- true time-on-target between V1 and V2 only when V1's measured launch/landing mechanics justify it.

Cooldown-aware kiting follows engagement/rotation.

---

# 7. What not to do

Do not:

- describe Claude's proposed order as already owner-approved;
- remove V2 geometry from the plan;
- optimize final HP after a won fight;
- rank only deaths conditional on wins;
- make every gun wait for the slowest gun in time-on-target;
- use hand-estimated shell timing when the engine has exact semantics;
- allow engagement movement to override reaction/dodge;
- let predicted-lethal rotation use hidden cooldowns or enemy intent;
- repeat the old wounded HP-threshold rule under a new name;
- make a shorter-ranged unit "kite" an enemy it cannot kite;
- use ten series as a precise reliability estimate;
- compare current random-draw series with historical fixed-list/pool rows;
- call a copied script an RRG result;
- keep tuning V1 if neither script nor oscillator shows a clear 200-pair effect.

---

# 8. Evidence register

## Project evidence

- `docs/decisions/0033-0g-big-levers-and-lighter-tooling-reviews.md`
- `evidence/tactical_composition_demo/SHAPE_LAB_SPEC.md`
- `docs/research/GAME_AI_BEST_PRACTICE_RESEARCH.md`
- Claude feedback uploaded by the owner
- `astelia-hunte/experiments/formation_sandbox/README.md`
- current shape-lab v3/v4 reports and commit receipts

## Key project-history findings

Historical Astelia sandbox:

- look-ahead improved old-rule random gauntlets;
- universal shell dodging reduced the old advantage;
- full healing changed the objective to survivor count/composition;
- hold-fire was often negative;
- a two-gun wait showed a small context-dependent positive result, while four-gun waiting was negative;
- the artillery planner improved damage per shell and fight duration without lowering fire rate;
- wounded pull-back had no measured gain;
- holding reserves back reduced gauntlet performance.

## External sources retained

- Uriarte & Ontañón (2012), kiting with influence maps.
- Usunier et al. (2017), StarCraft micromanagement.
- Churchill, Saffidine & Buro (2012), RTS combat search/LTD2.
- Churchill & Buro (2013), Portfolio Greedy Search.
- Brandner, Schilcher & Bettstetter (2016), decentralized pulse synchronization.
- Robocode wave / GuessFactor targeting documentation.

External results are analogies and priors. The project experiments decide transfer.

---

# 9. Final approval position

I would approve this R3 document as the **research and design handoff** for the next 0g decisions.

I would not call any unrun mechanism effective.

The immediate execution remains:

> finish V1 exactly as declared, read mechanism and throughput together, then follow the approved decision rule.

The most important conceptual correction is:

> **the project is not choosing between "low-loss micro" and "RRG synchrony." It is assigning each candidate one explicit job, comparing it with the strongest script for the same job, and retaining it only when the mechanism and outcome both justify the complexity.**
