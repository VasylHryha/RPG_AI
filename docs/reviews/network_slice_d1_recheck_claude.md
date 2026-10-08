CHANGES_REQUIRED
Reviewer family: Claude
Reviewed commit: 54fe0d91d911051e0baf631db9a5579ae5fc3ef2
Reviewed folder: `evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/` (CONTRACT.md SHA256 `4fb03f5bb7113fe735d789564684846efd16f7446f1c7077c3fdca2edfadb297`)
Date: 2026-10-08
Review type: cross-family read-only code and design review of network slice deliverable 1. No fights, collection, training, `--collect` or ES were run. I ran the focused suite once (44 cases), in a scratch copy of the folder so that the committed `NATIVE_FIXTURES.json` and receipts were not rewritten. 43 cases passed on the first invocation. The 44th failed only because my copy omitted `host.h`/`host.cpp`; after copying them, that one case passed. No repository file was changed.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Verdict summary

The delivery is a substantial and mostly faithful answer to R2. These parts are sound:

- **Wire and schema:** the allowlisted wire with its exact tensor table.
- **Host:** the neutral host structure.
- **N2 law:** a C4-faithful phase/motion law in dimensionless units with valid bounds.
- **Parity:** independent Python/C++ implementations with meaningful parity tests.
- **Heads:** categorical heads.
- **Hash pins:** living documents are not pinned.

One High finding blocks teacher-data collection: the training labels do not match the cast semantics that the networks are deployed with. If teacher data were collected first, they would need recollection. Several Medium findings would make later readings or attributions misleading. They are cheap to fix now and expensive later. Teacher-data **projection** (`project.py`) is pure arithmetic and is not blocked.

## R2-F1…F10 disposition

| R2 finding | Disposition | Remaining issue (finding below) |
|---|---|---|
| F1 allowlist/tensor/support | Resolved in code and tests (schema.cpp:9–31, CONTRACT.md:15–64) | Own in-flight shells are absent from the wire (M3). The boundary test only rejects injected keys and does not vary native internals (L6). |
| F2 cast state machine | Largely resolved (cast.cpp:3–8, host.cpp:37–46) | The integrated overlay path is not exercised; two contract statements disagree with the code (M2, L1, L2) |
| F3 teacher and causal join | Partial | Masks versus cached-permission semantics (H1); planner input differs from v6 (M3); the DAgger shadow-label join is not implemented yet (next deliverable) |
| F4 gradients/recurrent state | Resolved for this delivery: differentiable fire head, fixed radius, gradient mask, declared burn-in (models.py:26,35; CONTRACT.md:126–128) | The training loop is the next deliverable |
| F5 numerics | Resolved: L0=100 px, eps=.1, bounded transforms, substeps and atomic failure (models.cpp:7–13, dynamics.py:11–57) | — |
| F6 ablations | Mostly resolved: complete no_geometry_to_mode with held forcing, phase-blind movement readout | The launch-reset channel is unledgered (L3); the matched-kick harness is absent (L4) |
| F7 losses/DAgger/splits | Partial: categorical heads and masks are good | `aggregate()` drops initial teacher data (M4) |
| F8 resources/equal access | Partial | N1r target-group channel is aliased (M5); N2 has a unique untrained spacing prior (M6) |
| F9 ES contract | Partial (stage deferred) | Incumbent retention is not implemented (L4) |
| F10 readings/stops | Partial | Interval rule cannot reach a verdict for 0033-sized effects (M1) |

Checked and found sound:

- **Neutrality (item 1):**
  - `Host` derives from `control::Controller` (host.h:5). Network arms never call P16/v7/REACT/E1/R1 or `artilleryVolley`: the source test at test_slice.py:88–92 confirms it, and so does my read of host.cpp.
  - Shadow is a pure function of the views (teacher.cpp:10). Native physics and reflexes are the same overlay binary for every arm.
  - The opponent has **no planner** in collection: the direct `World(config)` constructor leaves `packs[].enabled=false` (rpc.cpp:19; packs are enabled only in `World::create`, observer_v1_world.cpp:183). This is the same for every arm, so it is fair, but it contradicts CONTRACT.md:7 ("the opponent's planner remain native").
- **Information boundary (item 7):**
  - No tactic, skills, enemy energy or RNG reaches the wire. Enemy preparation appears only as the adapter-derived `cast` threat (schema.cpp:33–38).
- **C4 fidelity (item 5):**
  - The x_dot and θ_dot forms match `geomind/c4_model.py:3–8,82–100`: k=8 nearest within r<3, a degree-normalised mean, the neighbour set held across RK4 stages, and w=exp(−r²) on r=d/100.
  - The rate bound is 5. The Jacobian bound is 2K (correct row-sum bound). The motion bound is ≤A(1+J)+B/eps≤12, mapped smoothly to ≤share·speed.
  - The engine positions are authoritative (host.cpp:23,28).
  - The fire head `6·tanh(b/6)+2cos θ` matches the native decoder threshold ≥0 (models.cpp:17, models.py:35, schema.cpp:30).
- **Hash pins (item 8):**
  - `BUILD.json` pins only the in-folder `frozen/` copies (build.py:82–83). All six copies are byte-identical to the living files at HEAD. PLAN_CURRENT, SHAPE_LAB_SPEC and ~/Downloads are not pinned.

## Findings

### H1 — High: cached start/release permissions apply between decisions, but their labels are masked exactly where the cache matters

**Evidence.**

- A decision's `request-start` and `permit-release` are cached and applied on **every** physical tick until the next decision:
  - start-ready uses `c.start` from the cache (cast.cpp:8);
  - prepared uses `c.release || age>=6` (cast.cpp:6);
  - CONTRACT.md:68,77 states this ("cached; does not skip windup").
- The teacher's labels at a decision tick are:
  - `start=false` whenever cooldown>0 or prep>0;
  - `release=false` whenever the gun will not be ready **this** tick (teacher.cpp:16–19).

  Under the six-tick cache, these "false" labels have a real behavioural effect. A gun whose cooldown expires 2 ticks after a decision waits until the next decision to start. A gun that becomes ready mid-window holds until the next decision.
- `labels.join` masks out the start label unless start is possible at the decision tick, and the release label unless the gun is ready this tick (labels.py:23–25).

  So the network's start/release outputs on cooldown and winding decision ticks are **never trained**. At deployment they nevertheless decide whether the gun starts or releases mid-window, and N2's +2cos θ term shifts exactly those untrained logits.

With windup .7 s, cooldown 1.2 s and 6-tick decisions, cooldown expiry and readiness fall between decisions in most cycles. Imitators will therefore fire on a systematically different schedule from the "timing-matched" teacher, in either direction. This confounds:

- the participation/offense readings;
- the noninferiority comparison against the teacher;
- N2 phase attribution through the fire head.

The label definition fixes what the teacher data mean, so the fix must precede collection.

**Fix (choose one rule and apply it to the teacher, the masks and the deployment alike):**

- **(a) Forward-looking permissions.** The teacher's start label means "start if the gun becomes start-ready within this six-tick window". Its release label means "release when ready within this window". Both are computed from public cooldown/prep/windup arithmetic. The masks include every decision tick where the opportunity can arise inside the window. For release, the teacher's planner aim must then be computed at readiness, or the aim locks at the next decision (state which).
- **(b) Decision-tick opportunity only.** A cached start or release permission is honoured only if the opportunity existed at its decision tick. `Cast::project` then needs the decision-tick opportunity bit. The current masks then match the deployed semantics exactly.

Rule (a) keeps responsiveness. Rule (b) is the smallest change. Add a native fixture: cooldown expiring at decision+2, and readiness at decision+3, each under teacher and network intents, with identical lifecycle outcomes for equal labels.

### M1 — Medium (blocks freezing a report inventory): the reading rule cannot reach a verdict for decision-0033-sized effects

**Evidence.** protocol.py:57–71 and CONTRACT.md:162 use a Hoeffding interval with α=.05/9 on [−1,1] contrasts. The half-widths are .485 at n=50, .343 at n=100 and .243 at n=200.

- **NONINFERIOR:** every lower bound must be ≥ −.10. At n=200, that requires the network to be **better** than the teacher by ≥.143 on every axis.
- **POSITIVE:** one axis must be ≥.343 better.
- **NEGATIVE:** requires a deficit of ≤ −.343.

An equal-performing student always ends PARK. Decision 0033 sizes comparisons to detect about ±10 points within 100–200 fights. With this rule, no 0033-sized effect is ever decided. The rule is decidable in form, but at the registered sizes it gives no verdict.

**Fix:**

- Declare one primary metric per axis with a pre-declared order, not three equally weighted rows.
- Replace the variance-free Hoeffding bound with a paired bootstrap (BCa) or a paired t interval on whole-draw contrasts. Optionally add an empirical-Bernstein check as a robustness row.
- Spend α across the 50/100/200 looks with a declared group-sequential rule, such as O'Brien–Fleming, instead of Bonferroni ×3.
- Before freezing, show on synthetic paired data that a true ±.10 effect with a plausible per-draw SD reaches a decision by n=200.

Keep margin .10 per normalised axis. It is a reasonable drafter proposal, and as far as I can review it, I approve it, subject to this interval change.

### M2 — Medium: the real patched combat path is compiled but never exercised, and the contract misstates two of its timings

**Evidence.**

- The native seam fixture hand-sequences `bind→prepare→decide→prePrep→gamePrep→postPrep→(release/fire)` (fixture.cpp:22). It never runs the overlay `combat.cpp`/`rules.cpp` produced at build.py:42–51.
- The real `actNovice` moves the unit **before** the artillery branch (src/native/combat.cpp:15). The overlay aim gate `net_slice::aimReach` is therefore evaluated **post-walk** (combat.cpp:26 plus overlay). CONTRACT.md:85 says "explicit aim gate is checked at act entry".

  When the post-walk aim fails, the tick is still recorded as projection state `released` (host.cpp:40). No consume, launch or no-launch event follows, so the diagnostics claim a release that did not happen.
- `decide` runs before `gamePrep` (combat.cpp:116 vs :124), so `Cast::project` sees "winding" on the tick that preparation completes. Release can occur one tick after readiness at the earliest. The teacher's "ready this tick" planner aim (teacher.cpp:16,22–24) is therefore launched one tick later than planned.
- The pre-walk `before` reach failure (combat.cpp:29: `released()` without `fireShellAt`) is never exercised. It is the only route to `consumed_without_launch`.

R2-F2 asked for fixtures covering target death, min/max range, walking across reach, cooldown expiry, Hold during prep and body blocking. The `Cast::project` unit transitions cover these only as pure functions.

**Fix:**

- Add a bounded integration fixture that calls the overlay `coreStep` for about 60 ticks in a 1v1 or 2v1 fixture world. This is a seam check, not a fight; it reads no outcomes. It should assert the lifecycle event sequences for:
  - start → windup across a decision boundary → hold → permission/auto-release → launch;
  - post-walk aim failure;
  - pre-walk target-reach consumption without launch;
  - target death while winding → cancel at the bound;
  - cooldown expiry between decisions.
- Record the projection state `released` only when release was actually attempted at act. Otherwise mark it `released_vetoed_post_walk`.
- Correct CONTRACT.md:85 (aim gate post-walk) and state the one-tick ready→release lag. Alternatively, move `Cast::project` readiness to `prep + dt·rate ≥ windup` so that the first ready tick can release, mirroring the teacher's convention.

### M3 — Medium: the teacher planner gets no in-flight shells, and the wire omits own in-flight shells

**Evidence.**

- v6's projection feeds the planner every live non-slow shell of both teams (`s4_shape_lab_v6/shapes.cpp:120`; used by `project`, :112).
- The slice teacher never fills `input.shells` (teacher.cpp:10–22), although CONTRACT.md:89 says "v6 `project()`".
- The wire publishes only enemy shells (schema.cpp:36). Neither the teacher nor the student knows that an own shell is about to land on a target.

As a result, the planner and the target head both over-commit to targets already under fire (overkill), and the teacher deviates from v6 without a declaration.

**Fix:**

- Add own in-flight shells as a public own-side threat kind: landing point, `at`, splash and damage. They are own knowledge, recorded by `launchedAck`.
- Pass both teams' shells to `project()` exactly as v6 does.
- Extend the tensor table, its normalization and the encoder parity fixtures to the new kind.

### M4 — Medium: `aggregate()` silently excludes the initial teacher data from the DAgger union

**Evidence.** protocol.py:18 keeps only trajectories with `visitor ∈ ('N1','N1r','N2')` for every round, including round 0. Initial teacher trajectories, whose visitor is the teacher, therefore yield `limit=0` and are dropped. CONTRACT.md:138 requires "round-balanced 1/3 including initial data". test_slice.py:171 labels round-0 data with arm visitors, which hides the bug.

In addition:

- `min()` over arms truncates every arm to the smallest train-split count, which can empty a round.
- The constant `weight=1/3` per trajectory does not balance trajectories of different lengths.

**Fix:**

- Treat round 0 as the single teacher-visitor pool.
- Balance by gun-decision rows within each round/visitor stratum, not by trajectory count.
- Fail loudly if any stratum is empty.
- Add a test with real round-0 teacher trajectories.

### M5 — Medium: N1r's previous-target channel is aliased and is not the per-target access N2 gets

**Evidence.**

- N2 receives one clean alignment scalar for each of the 12 candidate targets (host.cpp:25; models.py:50–57).
- N1r adds each candidate's peer-group memory rolled by `slot mod 8` and scaled by 1/12 into the same 8 channels as the neighbour mean (host.cpp:26; models.py:71–82). Slots k and k+8 collide, and group information mixes with neighbour memory. The network cannot tell which target a group belongs to.

CONTRACT.md:111 claims "the same graph/public target-group access". This is not equal access, so any N2 > N1r difference is partly representational.

**Fix:** give N1r a 12-wide per-candidate group scalar, for example the cosine between own memory and the mean memory of the peers previously assigned to that candidate. This mirrors N2's alignment scalar. Keep the neighbour mean as a separate 8-wide channel and adjust the hidden width so the parameter counts stay matched.

### M6 — Medium: N2 alone carries an untrained, undeclared C4 spacing prior, which confounds N2-versus-N1/N1r attribution

**Evidence.**

- A, B, J and share are gradient-masked during imitation (models.py:26) and excluded from ES (CONTRACT.md:152). They therefore stay at their zero-raw initial values: A=B=J=.5, share=.125 (models.cpp:16).
- With guns at 30 px spacing, r=.3. Then A(1+J cos)−B/r ≈ .75−1.67 < 0, a strong repulsion, with equilibrium spacing r ≈ B/(A(1+J cos)) ∈ [.67, 2], that is 67–200 px.
- This drift is added to every N2 goal, with multiplier 1 even on Hold (host.cpp:28). The teacher labels contain no such motion, and N1/N1r have none.

N2 thus deploys a fixed, hand-valued spreading policy. Its effect on splash exposure can dominate any oscillator effect in the N2-versus-N1r comparison. Within-N2 ablations (J=0, K0) remain valid isolations.

**Fix:**

- Declare the four constants and their rationale in the normalization ledger, because they are now design choices.
- Give N1r, and optionally N1, the same J=0 C4 drift (C4's `clump` analogue: same A, B, share; no phase), so that the arms differ only by the oscillator/coupling channel.
- Alternatively, make A/B/share learnable through a declared auxiliary objective or the ES subset.

State which attribution each arm pair supports.

### M7 — Medium: D1 and D2 are not distinct threat drills, and the request does not carry the cell

**Evidence.**

- Enemy guns run native `decideUnit` in both cells (host.cpp:16 `builtinDecision`; rpc.cpp:19–21). D1 therefore has exactly the same incoming shellfire as D2, plus two enemy dummies (requests.py:9–10).
- The request carries neither a cell name nor a threat-timing seal (requests.py:11), so collected fights cannot be stratified by cell from the record.
- CONTRACT.md:9 reads as if only D2 supplies incoming shells.

Geometry matters here:

- In D1 the nearest enemies to own guns are the static dummies: 233 px versus 250 px for the enemy guns. The nearest-target teacher (teacher.cpp:12) therefore shells 258-HP non-firing dummies first, while it is being shelled.
- Enemy guns' nearest targets are the own dummies at x=440, about 47 px from own guns, inside splash 40 plus radius 10. Own guns are therefore mainly hit by splash aimed at the dummies.

**Fix:**

- Put `cell` into the request and the terminal record.
- Make D1 either genuinely static (enemy guns hold, no release) or rename it.
- Seal D2's threat source and timing: who fires, at what, and the expected dodge demand.
- Reconsider dummy placement or a threat-first teacher target rule, so that the D1 teacher is not a degenerate policy.
- Correct CONTRACT.md:7 ("opponent's planner remain native"): collection has no opponent planner.

### L1 — Low: before the aim lock, legality uses the stale start-time aim

host.cpp:37 sets `c.aim=cast.lockedAim` (the aim at start) for every pending tick before the lock. Newer cached aims are taken only at the lock moment, so `ad`/aimReach and the recorded state `blocked/aim_range` can reflect an aim the policy no longer holds. CONTRACT.md:70 says "a later 5 Hz decision can supply an aim".

**Fix:** use the latest cached aim as the provisional aim until the lock.

### L2 — Low: the sequence parity test checks only target/start/release

test_slice.py:156 does not compare goal, multiplier, aim or N2 drift, which are the paths H1 and M6 depend on.

**Fix:** extend the test to the full action plus the drift vector, and add a death mid-sequence so the frozen-topology ID remap at host.cpp:22 is covered. Python has no equivalent remap helper yet.

### L3 — Low: the launch reset θ=0 is an action-to-mode channel missing from the intervention ledger

The reset at host.cpp:45 depends on geometry through target and aim reach. It persists in `no_geometry_to_mode`, `frozen_phase` and `K0`. A launch, for example, un-freezes `frozen_phase`.

**Fix:** declare the channel. Optionally add `no_reset` and make `frozen_phase` ignore resets.

### L4 — Low: the ES and probe contracts are only partly in code

- `SliceES` (protocol.py:41–55) has no incumbent, no common ten-draw panel and no survival-deterioration retention rule, although CONTRACT.md:154 describes all three.
- Its update uses unclipped noise while the evaluated candidates are clipped to [−2,2].
- The matched geometry/phase kick probe (CONTRACT.md:132) has no harness.

All of these can follow later, but the contract should label them as not yet implemented.

### L5 — Low: the 65,536-byte record cap aborts the whole collection

At a ten-gun teacher decision tick, one row carries the joint snapshot (about 20 KB) plus per-gun intent, teacher diagnostics and projection events (about 2.5 KB per gun). Shadow labels may add more. The total approaches the cap (rpc.cpp:22), and exceeding it throws and ends the process.

**Fix:** measure the maximum row size in the authorized timing sample, and either compact the projection events or split decision-tick rows.

### L6 — Low: boundary invariance is tested only by key rejection

test_slice.py:46–50 injects foreign keys. Add a native fixture: two worlds that differ only in enemy energy, cost, skills and RNG state must produce byte-identical `snapshot()` output and policy output.

### L7 — Low: tracking and wording

- PLAN_CURRENT_APPEND.md is not yet applied to `docs/PLAN_CURRENT.md`, which AGENTS.md requires for recheck tracking.
- CONTRACT.md:160 mentions "tactic" pairing, but the slice has no tactics.
- `strict_win` counts own infantry dummies as survivors (rpc.cpp:23). Report "own guns alive" beside it.

## What the next steps need

1. **Before any teacher collection:**
   - fix H1 (label rule) and M3 (shell inputs), because both change what teacher labels mean;
   - fix M7 (cell definition and request);
   - add the M2 integration fixture.
2. **Before stage-1 attribution:** fix M5 and M6.
3. **Before DAgger:** fix M4.
4. **Before freezing any report inventory:** fix M1.
5. **Not blocked:** `project.py` (teacher-data projection), since it allocates and runs nothing.

Do not count the authorized ≤20-fight timing sample as the M2 lifecycle fixture.

## Scope and limits

- This review establishes no runtime behaviour, usefulness, stability or RRG claim.
- My single focused run reproduced the committed fixture behaviour: 44 cases and the isolated native seams. It ran in scratch and left the repository unchanged.
- Claims about uncovered paths come from reading the source, not from executions.
- This file is new and uncommitted. If the authorized writer commits it, commit only this path, with the `Assisted-by: Claude:claude-opus-5-5` trailer and normal hooks.
