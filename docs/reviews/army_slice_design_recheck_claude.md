CHANGES_REQUIRED
Reviewer family: Claude
Reviewed commit: a959664 (`evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/DESIGN_ARMY_SLICE.md`, with its same-family `OWNER_RECHECK.md`)
Date: 2026-10-08
Review type: cross-family owner recheck of a development design (author Codex). This is a quick check under decision 0036's lighter process. It is not an execution approval or a milestone acceptance. It was read-only: no Python, tests, builds or fights were run. No numeric score is given.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Summary

The design is careful in many places:
- The roster and the C3 inventory match the source (`s4_shape_lab_v2/lab.py:86–99`: 10/30/10 per side, mirrored).
- The full-army bridge semantics are now correct: `controller_bridge.cpp:46` retargets on every dispatch, `combat_rules.cpp:60–68` locks no target, and `combat.cpp:13–16` uses pre-walk reach for melee/artillery and post-walk reach for ranged.
- The neutral host keeps P16, react and the planner out of the learned arms.
- Whole-fight splits and fresh entropy pools are sound.
- Exact-input conflict counting is in place.
- The U-R+P bridge arm is a real improvement.
- The RRG wording is honest: stateless imitation is not claimed as RRG evidence.

Four structural problems remain. Each one could waste the whole build or produce a leader that hurts:
1. The S1FIX lesson is not applied. There is no scripted units-alone versus units-plus-scripted-leader gate on the decomposed units before any leader is trained.
2. The P16 escort label is not what the teacher executed. The teacher passes it through `participate()` and react precedence first.
3. Most of the "leader" labels are unit-decidable, which confounds the main 0035 readout.
4. There is no order-of-magnitude compute estimate. The described per-tick, per-unit egocentric attention in float64 is very likely far outside the fast-iteration budget.

A smaller first runnable stage, script-only through the AS1 host, fixes 1 and 3 cheaply and sizes 4.

## High

### H1 — The S1FIX lesson is not applied: no scripted O-alone versus O+G gate before training any leader

**Where:**
- Design line 7: the authority paragraph.
- Line 143: stage A runs T, O, U-P and U-R.
- Line 141 and line 176: the stage B arms.
- Stop table, lines 183–200.

**Evidence:**
- **The drill harm.** S1FIX (`s4_net_slice_v1/S1FIX_PILOT_INITIAL.json`, D2-10) put a scripted planner leader on top of the decomposed autonomous units. It was worse than those units alone: kills 54 vs 74, deaths 115 vs 98, paired kills −2.0 (sd 2.6).
- **What the full-army evidence measured.** The full-army V2 gain (`s4_shape_lab_v6/OUTCOME_V2_LOOK_100.json`: deaths 36.22 → 33.47, paired +2.75 saved, kills per own death +0.103) was measured with V2 layered on forcedP16+react units, not on the design's new public oracle O.
- **What O changes.** By the design's own account (lines 35, 44 and 83), O changes:
  - targets: v6 memory is removed;
  - movement: no escort or approach;
  - Singles aim: O uses its own best single shot, where V2 Singles aims at the target centre (`artillery.cpp:64`).
- **Overlap with V2.** O's own best single shot already captures part of what V2 adds for single guns. When only one gun is ready, V2 can choose its Focus family, a led best-cluster point (`artillery.cpp:67–74`), over Singles. So the marginal value of G on top of O is unknown. The only direct evidence for this configuration (S1FIX) says it can be negative.
- **Gate already raised once.** The prior Claude recheck (`docs/reviews/network_units_and_leader_design_recheck_claude.md`, H3) asked for exactly this gate: "does T-unit-alone + T-leader beat T-unit-alone". S1FIX then answered it negatively in the drill.
- **What the arms can show.** None of the arms in stages A–C can separate "the leader learned badly" from "the leader learned a teacher that is harmful on these units".
- **Size of the planned check.** Stage A's 10–20 sanity pairs cannot detect a 2-death effect. S1FIX's paired death SD was 2.4 on ten guns, and full-army SDs will be larger.

**Failure scenario:** U+P and U+R lose to U-alone at stage C after 2,400 outcome fights. The cause is the teacher, which was knowable from scripts in about an hour.

**Fix:** Add a script-only leader gate before any leader fit. Run **O** against **O+G** through the AS1 host, with G being the scripted group commands routed through the exact command interface and obeyed. Use paired full-army fights at 50 → 100 pairs (regular plus C3 balanced), on the deaths and exchange axes of 0034.

Add this stop row: "Does O+G fail to save deaths versus O, or show harm beyond tolerance, at 100 pairs? → do not train leaders on these labels; revise the group teacher. Role: drafter."

The same run also reports the O−T decomposition gap at decision size, not only at the 10-pair sanity size. Scripts ran at about 33 serial-seconds per fight in v6 (design line 179), so 2 × 100 to 2 × 200 fights are cheap.

### H2 — The P16 escort label is the raw escort point, but the teacher executes `participate(escort)` with react precedence; obeying the raw point can pull ranged units out of their band

**Where:** Design line 72 ("Label escort gun binding and the exact clipped waypoint"), line 48 (obedience labels "select the exact command slot only on feasible present-command opportunities") and line 40.

**Evidence:**
- **The raw escort point.** `s4_v7_controller.cpp:17` writes the escort point (`escortPoints(o,side_,60)`, `s4_escort_probe_v1/escort.cpp:20–29`) into the overlay. That point is 60 px forward of the nearest own gun.
- **What the teacher actually executes.** forcedP16+react is `react_v1::Controller` (`s4_react_adapter_v1/dispatch.cpp:6–8`). Its `prepare()` passes every overlay goal through `participate()` (`react.cpp:96`, defined at lines 69–86). `participate()` keeps the endpoint only if it lies in some enemy's engagement band (line 74). Otherwise it projects the endpoint onto the band around the nearest enemy (lines 75–79).
- **React precedence.** An active react then replaces the movement and holds fire (`react.cpp:101–102`).
- **Ranged reach is short.** Ranged reach is much shorter than artillery range, so an escort point 60 px ahead of a gun at preferred artillery range is often outside every enemy band. In those cases the teacher moved to the projected band point, not to the escort point.
- **The resulting harm.** The leader is labelled with the raw point. The unit's conditioned head is labelled to pick the command slot on every feasible present command, and the design never says react overrides a present command. So a perfectly trained U+L sends ranged units to places the teacher itself never went: out of range, and walking into threats it would have dodged. This is a direct way for the leader to cause the drill-type harm.

**Fix:** Either move escort into the unit oracle (H3, preferred), or label the executed goal (post-`participate`, post-react) and not the raw clipped point. In both cases, state that react and body precedence override any present movement command in both the conditioned oracle and the deployed host. Then give the conditioned obedience label the same precedence, so it is not "always select the command slot". Log the escort-to-executed distance per row.

### H3 — Most leader labels are unit-decidable; only V2's multi-gun assignment is a group decision, so "leader adds value" is confounded

**Where:** Design lines 66 and 72–74 (the P16 rows of the teacher table), line 81 (focus command) and line 83.

**Evidence:**
- **Every P16 overlay quantity is a function of public state that each unit fully observes.** The design's own §1 (line 21) says all 49 friends and 50 enemies are represented:
  - **Escort** (`escort.cpp:20–29`): the nearest own gun to *this* ranged unit, then the enemy ranged within 400 px of that gun, otherwise the centroid of the enemy guns. No other unit's choice enters.
  - **Gun focus** (`s4_v7_controller.cpp:22–28`): enemy guns sorted by `splashValue`, a count of enemy units within 40 px plus radius of the enemy gun (`s4_escort_probe_v3/escort.cpp:4–6`), then the first gun reachable by *this* gun. This is the same rule as the design's autonomous artillery target row (line 39), so the leader's focus command duplicates the unit label.
  - **Anchor** (line 23): the first sorted enemy gun reachable by *any* own gun. Each gun sees all own guns' positions and ranges.
  - **Approach and repulsion** (lines 29–36): a point at the preferred radius from this gun's focus, plus repulsion from own guns within 60 px. Again, this uses only the gun's own view.
- **None of this is a joint decision.** The teacher computes it per unit with no assignment or coupling. The genuinely joint decision is the V2 battery plan: the ready-set model at `s4_shape_lab_v6/shapes.cpp:103–124`, and family scoring with nearest-free assignment at `artillery.cpp:8–14, 86–91`. Even V2 is unit-decidable when only one gun is ready (n=1: Singles or a single Focus point).
- **The confound.** Taking P16 behaviour out of the units and handing it to the leader:
  - weakens U-alone below the per-unit behaviour that the best script has;
  - makes any U+L gain partly "the leader restores per-unit escort and approach", not group coordination. That breaks the 0035 reading "the leader must earn its place by its added kills or saved deaths";
  - makes the focus-command ≥95% response check (line 145) nearly trivial;
  - widens the O−T decomposition gap that F4 had to add a control for.
- **Over-claim.** Line 66 calls the whole-army leader "the smallest way to preserve global P16 escort relationships". Those relationships are not global.

**Fix:**
- Put the P16 overlay (escort post-`participate`, focus, anchor, approach and repulsion) into the **autonomous oracle O** as per-unit labels. The movement head's 33-way support may need the exact escort/approach point as an extra autonomous candidate, using the same mechanism as the 34th slot.
- Make the leader carry only what no single unit can decide: the V2 assignment on events with **≥2 eligible guns**.
- Define what happens on n=1 V2 events with a non-Singles family. Recommended: an autonomous label, or an explicit leader label with a stated reason.
- Measure the multi-gun event fraction, and V2's share of gain on multi-gun versus single-gun events, in the H1 script gate before building the leader. S0 found only 1–4% multi-gun coverage in drills. If it is similarly low in the full army, the leader has little to learn, and the 2-death threshold cannot be met by the leader alone.
- Add this stop row: "multi-gun eligible-event share below the declared floor in the script gate → park the leader route. Role: drafter."

### H4 — No order-of-magnitude compute estimate; the described network is likely far outside a fast-iteration budget

**Where:** Design lines 21–25, 31, 56–58 ("State advances once per physical tick"), 125, 129–131 (float64, ten epochs, 90-tick TBPTT with 30-tick burn-in) and 175–181.

**Evidence and reviewer arithmetic.** These figures are illustrative, not measured:
- **View size.** Each unit has an egocentric view of 1 + 64 + 64 entity tokens plus 128 + 64 threat tokens, about 321 tokens at width 64, with two attention blocks.
- **Cadence.** The recurrence advances every physical tick (30 Hz) and consumes the current observation, so the encoder runs about 4,500 ticks × 50 units per fight.
- **Cost per unit-forward.** The cheapest reading (token MLP plus single-query pooling) costs roughly 2–5 MFLOP. Full token self-attention costs roughly 60–120 MFLOP.
- **Training cost.** One epoch over 180 training fights is about 40 M unit-steps. Forward plus backward then costs about 0.6 PFLOP even at the cheap end. In float64 on CPU that is about an hour per epoch on many cores, and many hours on few cores. Ten epochs per arm and four arms (U-P, U-R, P, R) follows.
- **Outcome-panel cost.** With about 2,000 network fights, inference alone could reach tens of seconds to over an hour per fight, against the historical 33 s/fight for scripts.

The design deliberately postpones every estimate to post-build measurement (lines 175–181). That repeats the 0036 lesson (three refusals cost hours) at a larger scale. The architecture choice that drives cost is fixed before any measurement exists.

**Fix:** Before approval, add a one-paragraph FLOP and memory bound for the chosen architecture, and pick the cheap structure deliberately. Recommended:
- encode the world **once per frame**, AlphaStar-style shared entity encoding with per-unit relative queries, not 50 egocentric re-encodings;
- run the encoder only at the base cadence (5 Hz) and at ready events. The per-tick U-R phase update and the per-tick U-P update consume cheap physical features and the last encoder output;
- use float32 for training, keeping float64 only for parity replay;
- subsample highly correlated base rows for training.

State a target per fit (for example, under one hour) and per network fight. Add this stop row: "the pre-build bound exceeds the target → change the architecture before building. Role: drafter."

## Medium

### M1 — Training and labelling are off-policy, with no correction step

**Where:** Line 35 and line 119: T rolls out and O labels. Line 131: leader contexts are built on T histories.

The units imitate O on T's state distribution. O moves differently from T (lines 40 and 83), so a deployed U-alone visits O-like states it never trained on. The design has no DAgger or on-policy step in stages A–C ("on-policy repair" appears only as a later extension, line 177). Prior NS1 work needed DAgger for hold-fire collapse.

**Fix:** Use O as the behaviour policy for unit data, and O+G for leader data. Both already run through the AS1 host (H1). Keep T as the comparator. If T rollouts are kept, budget one DAgger relabelling round in stage A.

### M2 — Kills are saturated, so the damage axis collapses

**Where:** Lines 149–151.

The teacher kills 49.9 of 50 enemies per fight (v6 V2: 4,989 kills over 100 fights). So "enemy kills/fight" and "loss of ≤2 enemy kills" are near ceiling for T-level arms, and kills per own death becomes about 50 / deaths, which is the survival axis restated. Decision 0034's second axis then carries no information.

**Fix:** Add time-to-elimination, or kills per minute over all fights, as the declared damage-axis readout. v6 used kills per minute (65.8 → 69.1). Report damage-axis saturation fractions as S1FIX did.

### M3 — The useful-effect thresholds equal the whole V2 script effect

**Where:** Line 151.

The thresholds are 2 deaths saved per fight and +0.10 kills per own death. The entire scripted V2 effect was 2.75 deaths and +0.103 (`OUTCOME_V2_LOOK_100.json`). A learned leader would have to recover about 73% of V2's full death effect, and all of its exchange effect, to be "useful". After H3 (P16 moved into units), the leader's ceiling is only V2's multi-gun share. The most likely stage C outcome is "park", decided at 2,400 fights.

**Fix:** Use the H1 script gate as the leader's ceiling. If the ceiling (O+G − O) is below the threshold at 100 pairs, do not run leader outcome panels; park or redesign the group teacher. Also state the planned MDE using the script-gate SD, not only stage-B sanity SDs.

### M4 — The first runnable stage is too large for 0036

**Where:** Lines 169–177.

Stage A bundles the AS1 schema, host, fixtures, a timing sample, a 240-fight collection, two network fits and sanity runs. Nothing runnable exists before most of the stack is built.

**Fix:** Name **Stage A0: script-only AS1 host**. Contents:
- O, O+G and T on the neutral host;
- event schedule and empty-command parity;
- the H1 gate at 50 → 100 pairs, which also serves as the timing, frame-size and event-rate sample;
- multi-gun share;
- O−T gap.

Networks start only after A0 passes. This is the smallest stage that answers whether the leader route is worth building.

### M5 — The 512 MiB per-process stop row is stale

**Where:** Line 194.

Commit `af3724f` (`S1FIX_RSSFIX_RECHECK.md:14`) replaced the 512 MiB cap with a declared 2 GiB cap plus live RAM checks. A full-army attention model will not train in 512 MiB.

**Fix:** Cite the current cap source and the live-RAM rule instead of a number.

### M6 — R's pooled leader training disables its distinctive path on half the data

**Where:** Lines 87 and 93.

R is fitted on pooled U-P and U-R contexts with equal mass, but its parent phase is disabled on U-P contexts. R is deployed only as U-R+R. So half of R's training never exercises the mechanism it is deployed with, while P trains its memory on all rows. Matched parameter counts do not make this a matched budget for the mechanism.

**Fix:** Fit R on U-R contexts only, and fit P twice: once on U-P contexts (for U-P+P) and once on U-R contexts (for the U-R+P bridge, which then holds both child and data fixed against U-R+R). Alternatively, declare the asymmetry and its expected direction.

## Low

- **L1 — Unit parameter matching is not stated.** Line 31 seals capacity but gives no plain-versus-RRG parameter tolerance for U-P against U-R, while leaders get "within 10%" (line 85). Use the same rule.
- **L2 — Prior K and phase lessons need diagnostics.** `network_slice_trained_results_recheck_claude.md` (M1) found that K never trained and that phase was a reset-synchronized clock. Add "K and forcing moved from initialization" and "phase variance not explained by attack resets" as U-R diagnostics. Without them, U-R versus U-P differences have no mechanism reading even descriptively.
- **L3 — Start/release labels for melee and ranged are mostly constant.** In T they equal "not reacting, not guarded, not busy" (`react.cpp:101–104`; native `combat.cpp:20–25` releases a prepared melee even out of reach). This is decidable. Report the active-label base rate so that "start/release accuracy" is not read as competence.
- **L4 — The document is hard to use as a contract.** It is 62 KB in 227 lines, with many paragraphs of 150+ words, which makes it hard to implement or check. A one-page A0 contract (M4) with the rest as appendix would help.
- **L5 — Stale marker file.** `UNCOMMITTED_DESIGN.txt` was committed in a959664 and still lists the three files as uncommitted. Remove or update it in the next commit.

## Checks that passed

- **Unit observation fit.** The entity caps cover the real 50v50 roster, and pointer heads are none+64. Threat banks are counted, and an omission that changes a label blocks admission.
- **Label decidability for units.** Movement (with the H2 precedence fix), target and own-shot aim come from the encoded view. Exact-input conflict checks are on collected data.
- **Data hygiene.** Whole-fight splits cover all twenty cells in every split. Fresh, exclusive entropy pools are used. Trajectory fingerprints are checked, augmentations stay with the parent split, and no checkpoint is selected on test or outcome data.
- **Stop rows.** All rows are yes/no with one action and one role. H1, H3, H4 and M3 add the missing rows.
- **Claims.** RRG, formation, source recursion and teacher optimality are explicitly not claimed. Stage B/C R/P differences are labelled practical observations (lines 157, 167 and 208).
