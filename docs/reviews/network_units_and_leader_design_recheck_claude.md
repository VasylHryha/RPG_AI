CHANGES_REQUIRED
Reviewer family: Claude
Reviewed commit: e53a49f
Reviewed file: `evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/DESIGN_UNITS_AND_LEADER.md` (plus `docs/reviews/network_units_and_leader_design_recheck_codex.md`)
Date: 2026-10-08
Review type: cross-family owner recheck of a development design (author Codex). Not a milestone acceptance or execution approval.

What I did: I read the design, Codex's same-family recheck, decisions 0033–0036, CONTRACT.md, the trained-results recheck, `teacher.cpp`, `schema.cpp`, and the engine planner `src/native/artillery.cpp`. I ran no Python, tests, training, fights or native code. I did not open `_local/` and did not touch the running DAgger job.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Summary

The unit half of the draft is sound. Every unit label can be decided from the unit's own 1008-feature observation, empty commands keep units valid, and the earlier recheck findings are mapped to fixes. The leader half has two problems the same-family recheck missed, because neither the draft nor that recheck read the engine planner.

1. **The planner's aim points are not relative to the gun's own target.** Many leader labels are therefore blocked or degrade the unit.
2. **The teacher gives no coordination-timing signal.** Its fire-together label repeats the unit's own release label, it never labels hold, and the 6-tick release bound leaves hold almost no power.

As a result, the plain-versus-RRG leader comparison under imitation cannot be the coordination test that 0036 asks for. The draft also predates 0036. It is sized as a multi-hour, 30-fit ceremony with 60 descriptive draws, has no cheap script-level gate, and has no path to the full-army fight.

## High

### H1: The planner's group aims come from its own cluster choice, not from the units' provisional targets. The leader has no focus command, and the Singles family removes lead.

**Where:** §3 line 57 ("It plans from the supplied provisional target publications, not a hidden teacher-only target choice"), line 45 (aim offset "relative to its chosen target"), line 65 (200 px envelope; out-of-envelope labels block collection), §2 line 35.

**Evidence in the engine** (`src/native/artillery.cpp`):
- **Lines 66–68:** the clusters are built over **all** living enemies (`center=led(i)`), scored by enemy count times guns in reach, then sorted.
- **Lines 72–84:** the multi-gun families (Dashnet, Wall, Herd, Split, Battery) place their points around those cluster centres.
- **Lines 8–12:** `assign()` gives each point to the **nearest free gun in reach**. The gun's own target is never consulted.
- **Line 64:** only Game-rules `Singles` uses `gun.target`, and it aims at `target->pos`, the centre with **no lead**.
- **`teacher.cpp:21–25`:** the teacher passes `c.target` in, but the queue point is snapped to the gun's candidates whatever enemy it surrounds.

**Failure scenarios:**
- **Wrong reference point.** In D2-10, gun A's nearest enemy is E1, but the planner's best cluster is E3–E4, 350 px away. The leader label "offset relative to A's chosen target" exceeds the 200 px envelope. The §3/§10 stop fires on the first collection, or such rows are dropped, and focus fire (the planner's main value, splash-value focus from 0033) is never learned.
- **Worse aim.** When the planner picks Singles (likely the most common case, with one gun ready), the leader command is "aim at the target centre". The unit's own label is the raw lead. The leader then teaches units to drop lead on moving targets, so T-unit+T-leader and U+leader are handicapped by construction.

**Fix:**
- **(a) Add a focus/target command** (a pointer over the enemy set), applied at the start decision before the native target lock. Express aim requests as offsets from the commanded focus point, not from the unit's nearest target.
- **(b) Treat Singles as no command:** it becomes the empty command, so the unit's lead aim stands. Only multi-gun families produce aim commands.
- **(c) Correct the line-57 sentence:** the planner chooses its own focus.
- **(d) Before any build, count from the existing v2 collection diagnostics** (`teacher_planner.family`, `raw_aim`, `snap_distance`; this is a read of existing data, not a run):
  - the family distribution;
  - the fraction of ticks with two or more ready guns;
  - the distribution of distances from each planner point to the gun's own target.

  If multi-gun families are rare, the leader's aim label has almost no coverage. Note also that the teacher excludes "coming" guns, which shrinks `n` and so makes the families with n≥3 or n≥4 rarer still.

### H2: There is no teacher signal for "when to fire together". Under imitation, the RRG-versus-plain leader comparison cannot be the coordination test of 0036.

**Where:** §3 line 61, §2 line 47, §3 lines 69–77, §9 line 182.

**Evidence:**
- **Fire-together repeats the release label.** The planner queue is immediate and covers only guns that are already release-ready (`teacher.cpp:21`). "Assigned guns receive fire_together" therefore restates each gun's own release-ready label (`y[47]`); it adds nothing over the unit.
- **Hold is never labelled.** The draft says so itself (line 61).
- **Hold at release has almost no power.** CONTRACT.md line 71 adds a native **automatic release 6 ticks after readiness**, so holding a ready gun can delay it by at most one decision. Real volley synchronisation has to act on **start** timing: delay a windup start until the other guns can finish together. The command schema does not say which permission hold and fire-together act on.
- **Neither leader can show a temporal advantage.** The group teacher is stateless. Imitating it gives the RRG leader's persistent Φ, and the plain leader's 8-coordinate memory, nothing to do. This is the same argument 0036 Change 3 makes against unit-level evidence ("Unit-level imitation of a stateless teacher cannot show an RRG advantage"), and it applies equally at the leader level.

**Failure scenario:** units plus both leaders are trained, and P and R tie on contested cells. Two misreadings are then possible:
- the tie is read as "RRG adds nothing at the leader";
- or a seed-noise difference is read as "the RRG coordination mechanism works".

The task never required timing coordination, so neither reading is valid.

**Fix:**
- **(a) Rename the imitation-stage P versus R comparison** to "leader plumbing and imitation of spread and focus". It is not the 0036 RRG test.
- **(b) Define the timing commands on start permission**, for example "hold start until the battery can release within one decision". Make release-hold diagnostic only.
- **(c) Name where timing labels come from.** Either:
  - a search-guided leader (Expert Iteration at the leader level, 0036 Change 1), where engine look-ahead scores hold/start-together alternatives; or
  - a declared scripted timing teacher, labelled "script".

  The RRG test (R versus P on paired contested fights) is run on that stage.
- **(d) Until then, mask the timing head as NOT_TRAINED** in both leaders, as line 61 already does for hold. Fire-together adds nothing over the release label, so mask it too.

### H3: The scope conflicts with 0036. There is no cheap gate showing that a group layer can earn its place, the sizing cannot answer "does the leader earn its place", and the plan is too heavy for the lighter development loop.

**Where:** §5 lines 109–121, §6 lines 131–135, §7 lines 139–145.

**Evidence:**
- **Size.** The draft's own projection (line 143) is 12 unit fits (about 5.9 h sequential) plus 18 leader fits plus 2 DAgger rounds with leader visitors. That is over the 10,800 s cap before leader costs, which are unmeasured.
- **Draw count.** The outcome panel is 60 descriptive draws per arm across 9+ arms. Decisions 0033 and 0036 (recheck table: "Does the leader earn its place?") require **100–200 paired fights** for that decision. The draft states (line 121) that its panel does not give that reading.
- **Process weight.** 0036 Change 4 asks for simple measured estimates, one quick recheck per build, and full ceremony only for claimed results. The draft has a three-bin entropy battery, Hungarian tie matching, a 3×3 matrix with three seeds each, the N2-J0 three-seed control, and the full J ablation set. Several of these serve unit-level RRG attribution, which 0036 says is not used as RRG evidence.
- **No go/no-go gate.** The decisive and cheap question is never asked first: **does T-unit-alone + T-leader beat T-unit-alone** on paired contested fights? Scripted fights are fast: the v2 collection ran 200 fights in about 7 minutes. If the scripted group layer adds no kills and saves no deaths at 100–200 paired fights, no imitated leader can earn its place, and the 18 leader fits are wasted.

**Failure scenario:** hours of fits and admissions, possibly another refusal for being over the cap (the 0036 lesson), followed by a P/R/no-leader tie that was predictable from scripts alone.

**Fix — staged minimal path:**
1. **Data read only, no runs.** From the v2 diagnostics, take the counts in H1(d), plus the fraction of ticks where the full-public reaction differs from the 8-threat reaction (M1).
2. **Script gate.** Run T-unit-alone (new single-shot oracle) against T-unit+T-leader (with the H1 fixes) at 100–200 paired fights, on cells chosen by M4. Also report the effect size, which tells you whether 100–200 fights can detect a leader effect.
3. **Training, only if step 2 passes.** One recollection. Fit one unit arm (N2, or N1r and N2 with one seed each) and P and R leaders with one seed each. Run 100 paired contested fights for U, U+P and U+R.
4. **Claims only.** Add seeds, the J0 and N2-J0 controls, and DAgger round 2 only for results that will be claimed. Defer N2-J0 and the J battery; unit-level RRG is not the 0036 evidence.
5. **Next slice.** A full-army fight (M3).

## Medium

### M1: The "group reaction" shift label is a representation patch, not a group reaction

**Where:** §3 line 63.

**Evidence:** the label is defined as `shift = full_public_group_goal - autonomous_goal`. Both terms come from the per-unit `net_public::react`. One sees all public threats; the other sees only the 8 retained threats. With 8 or fewer relevant threats the shift is zero. Otherwise it corrects the unit's truncated view.

**Why it matters:** 0035 means a group reaction such as a "shift away from incoming shells" chosen jointly. This label is not that.

**Failure scenario:** the shift head trains on a mostly-zero label. The report then claims the leader provides group reactions.

**Fix:**
- Rename the label "threat-overflow correction".
- Measure its nonzero rate from the v2 data. If it is rare, drop it from 1b.
- A real group-reaction command needs a group teacher, such as a battery-level dodge or spread from the dodge trio, or search.

### M2: The lead horizon does not match engine flight time, and aim is scored on rows where it has no effect

**Where:** §2 line 35.

**Evidence:**
- The label uses `tau = .8*range/lob`. The engine's actual flight time is distance/lob (`schema.cpp:36`, `landing = release + dist/lob`).
- The aim locks at the first positive release, so the true intercept is the fixed point of `tau = |q - p_gun|/lob`. It is computable from public fields (own position and lob, target position and velocity).

**Failure scenario:** a target at 0.5×range gets 1.6× too much lead. The "best single shot" label then misses, and so does the unit, on exactly the moving drills added to test aim.

**Fix:**
- Use a 2–3 iteration fixed point on the actual distance, still raw and still public. Keep the planner horizon only as a baseline.
- Report and weight aim learning on **release-opportunity rows**, where the aim is actually committed. Report other rows separately.

### M3: The fairness of P against R is under-specified, and some outputs are unused

**Where:** §3 lines 71–75, line 45, line 61.

**Evidence:**
- **Nested or crippled.** The draft does not say whether R also carries P's 8-coordinate recurrent memory. If it does, R is P plus Φ features, a nested model, and a tie is expected. If it does not, R swaps 8 memory coordinates for one phase.
- **Slot token is unused.** The volley-slot token is a leader output and a command field, but the conditional unit oracle ignores it (line 47 uses aim, hold, fire-together and shift only).

**Fix:**
- Declare the R architecture explicitly. Recommended: the same encoder, with **R's memory replaced by the parent resonator** (Φ plus the composed state) at a matched parameter count, and P keeping its memory.
- Remove the slot output, or give it a declared unit-side use.

### M4: The drill panel is not yet contested by evidence

**Where:** §5 lines 117 and 121.

**Evidence:**
- D2-10 is death-saturated: every arm lost all 10 guns (trained recheck, H1). Kills still vary.
- D2-2 differed in one draw only.
- The moving and dodging cells do not exist yet, and their contestedness is unknown.
- Choosing cells by outcome variation on the same draws is selection.

**Fix:**
1. Run a script-only contestedness pilot on separate pilot entropy (teacher arms only, about 10–20 fights per cell, per the 0033 "mechanism first" rule).
2. Freeze the cells and the opponent parameters.
3. Then run the 100–200 paired fights.
4. Use D1-10 only for time to clear.

### M5: There is no path to the full-army fight or to search-guided stage 2

**Where:** §3 line 55, §8 line 174, §10 line 211.

**Evidence:**
- **Caps.** The caps are 10 guns, 12 own units, 12 enemies and 64 threats; overflow is "invalid/out-of-scope". The leader is guns-only.
- **Next slice.** 0036 Change 2 makes a full-army fight against the regular enemy the next slice after a contested-drill result. That roster likely exceeds these caps and includes non-gun roles.
- **Stale stage-2 list.** The "before stage2" list is the old ES list.

**Fix:**
- Check the caps against the full-army roster now, while the encoder is being rebuilt, or declare the change needed.
- Add a short section on how the units and leader plug into Expert Iteration: a policy prior, a value head, and search over leader commands, as in H2(c).
- Replace the ES-specific "before stage 2" items with the 0036 stage-2 prerequisites.

## Low

### L1: Exact-tie Hungarian matching and the full-token canonical sort

**Where:** §3 line 59.

Exact ties across all planner-relevant continuous fields are practically measure-zero, and the planner already binds a point to a gun (`q.gun.slot`). Keep the planner binding, a canonical insertion order, and the wire-permutation test. Replace the Hungarian path with an assertion and a counter.

### L2: The decidability battery

**Where:** §2 line 41.

The zero-conflict exact-tensor check is cheap and decisive; keep it. Three bin widths, minority disagreement and decision-boundary inspection are ceremony for a development loop. Use one bin size, reported.

### L3: The closure map marks prior findings as closed

**Where:** §8 lines 153–172.

The map marks prior findings closed "on paper". That is fine for a design. Trained-recheck M1 (K did not train) is only addressed by reporting, not by a cause. Add one line: check the K gradient magnitude at initialisation before refitting.

### L4: The same-family recheck did not open the planner

Its R1–R7 are valid. H1 and H2 above come from `artillery.cpp` and the contract's 6-tick bound, which no reviewer checked. Future leader-teacher designs should cite the planner lines they rely on.

## Answers to the requested checks

1. **Unit label decidability: yes, with M2.** Target is the nearest slot. Move and REACT use the 8 retained threats. Start and release come from columns 28–29 of the observation. Aim lead needs target vx/vy, own lob, range and splash, and relative position, and all of these are in the observation (`schema.cpp:24`). The per-gun aim label is well-defined, but its horizon should be the actual flight time.
2. **Leader label: partially consistent.**
   - **Sound:** the gun-to-point binding is native (`q.gun.slot`), the permutation handling is sound, and commands are optional with empty commands equivalent to the autonomous behaviour (with dropout).
   - **Broken:** aim is referenced to the wrong point and Singles gives centre aims (H1), and the timing labels carry no information (H2).
3. **RRG leader: structurally a level-2 resonator.** The parent phase is composed from direct child modes, uses radius weights, and drives commands, and the up/down transmission is lawful. However, imitation gives it no task reason to use Φ (H2), and the comparison with P is under-specified (M3).
4. **Drills and detectability: not yet.** Contestedness is unvalidated (M4). 60 descriptive draws cannot answer the 0036 question; use 100–200 paired fights after a script gate that estimates the effect size (H3).
5. **Prior findings H1–H3, M1–M5 and L1–L3:** addressed in the design, with L3 above as a note.
6. **Scope: too heavy for 0036, and no full-army path** (H3, M5).
7. **Gaps, conflicts and over-claims:** the line 57 claim (H1); fire-together presented as a trained coordination command (H2); "group reaction" (M1).

## What is sound

- Autonomous and conditional label separation, command dropout, and units staying valid alone.
- A unit oracle constrained to the encoded view.
- Trainable J, with an honest statement that teacher J=0 may drive it to zero.
- Per-cell all-draw accounting with saturation flags, and no pooled kills per minute.
- Per-run results files that refuse to overwrite, and committed per-fight parity.
- The hash boundary that excludes living documents.
- The normalization ledger.
- The bounded claims list.
