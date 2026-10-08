PASS_WITH_NOTES
Reviewer family: Claude
Reviewed commit: cac370a (`evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/DESIGN_UNITS_AND_LEADER.md`, revision 3; `docs/decisions/0037-0g-privileged-search-teacher-staged.md`; with `docs/reviews/network_units_and_leader_design_r3_recheck_codex.md`)
Date: 2026-10-08
Review type: cross-family owner recheck, round 3 (author Codex). Quick check under decision 0036's lighter process. This is not a milestone acceptance or an execution approval.

**What I did.** I read revision 3 in full, decision 0037, Codex's same-family r3 recheck, and my round-2 report. To verify the premise of N-H1's fix, I also read the GAME dodge code (`src/native/combat_rules.cpp:70–92`), the catalog dodge and ability entries (`src/native/catalog_data.h`), the NS1 snapshot and encoder (`s4_net_slice_v1/schema.cpp`), and the NS1 teacher contract (`CONTRACT.md:90–92`). I ran no Python, tests, fits, fights or native code, and I did not open `_local/`.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Summary

Revision 3 addresses all nine round-2 findings on paper. The S3a/S3b split follows the owner's ruling and is stated clearly, and the P0 gate is correct. N-M1 through N-M4 and all the Lows are resolved.

There is one new **High** finding, and it is my own error from round 2. The hidden variable I proposed for the S3 history test, enemy dash-dodge readiness, **never fires against artillery shells in this slice**. So as written, S3a and S3b would teach and test a variable that has no effect. This does not affect S0 or S1, but the S3 variable must be replaced before any S3 build.

For **S0 and S1**, which Codex is building now, I have three Medium notes and two Low notes. None of them blocks starting. Each one changes how an admission row is computed, so they should be folded in before S1 cells are sealed:
- the S1 wrapper-miss stop is likely to fire for the wrong reason;
- the S1 detectability gate does not match the S2 decision rule;
- the S1 "changed command" rate has no stated comparison;
- S0's scope for group labels is ambiguous;
- the S0/S1 approval record is missing.

## Round-2 findings: resolution

| Finding | Status | Evidence in revision 3 / residual |
|---|---|---|
| N-H1: S3 labels snapshot-decidable; no memoryless control | **Resolved in structure; the chosen variable is inert (R3C-H1)** | Decision 0037 is recorded. The privileged sidecar is label-only. S3a is a flagged privileged-student stage with no RRG-state claim (§1, §5 S3a, last stop row). S3b removes the channel structurally (§5 S3b). A trained P0 has matched budget and width. The stateful R/P reading is gated on P0 being measurably worse on both validation loss (≥5%) and paired closed-loop useful benefit. The zero-conflict veto is replaced for S3b by bounded-public-history recoverability (§3 line 73, §5 lines 201–203). All of this is correct. However, the declared variable, dodge readiness, has no effect on shells (R3C-H1). |
| N-M1: stale cached aim through windup | **Resolved, with an S1 metric residual (R3C-M1)** | Focus, assignment and shape are fixed at start. Exactly one actual-distance refresh happens at the first release opportunity, before aim lock, even if U declines (§2 lines 39–43). There is no continuous recomposition. The refresh is shared by teacher labels, U, P/R and branches. The S1 paired raw and shape-subtracted miss and the stop row are present. The residual: the admission stop uses the raw miss, which includes deliberate spread (R3C-M1). |
| N-M2: S1 bar too weak; S2 threshold unscaled; "pathologically" | **Resolved, with a consistency residual (R3C-M2)** | Per-cell paired SD, chi-square-inflated planning MDE at 100 and 200 pairs, saturation and informativeness rules, a roster- and HP-scaled useful/harm ledger, a sealed primary axis and final N. "Pathologically" is replaced by a start rate of at least half the teacher's with at least 20 opportunities (line 152). The park rows cite the sealed rule. The residual: S1 checks primary-axis detectability only, but the S2 verdict also needs the harm bounds and a point estimate at or above the threshold (R3C-M2). |
| N-M3: teacher arms dropped | **Resolved** | Five arms on the same paired fights (U, U+P, U+R, T-unit-alone, T-unit+wrapper). Gaps are reported separately. Separate park rows distinguish leader-learning failure from wrapper/cell utility failure (lines 143–155). The added cost is projected (§7 line 268). |
| N-M4: waiting under-priced; "relevant" undefined | **Resolved** | "Relevant" means root-commanded casts, with failures kept in the denominator (line 171). Every scored candidate gets a common t+3 cutoff plus its own t+3→t+6 continuation under frozen U+P. Next-cycle coverage is derived and verified before labels. There is an immediate-only rerank control, and the cutoff-only score is logged (lines 173–177). |
| N-L1: slate narrow; cycle 1 is not ExIt | **Resolved** | Line 161. |
| N-L2: common prior biases against R | **Resolved** | Line 181. |
| N-L3: no cost formula | **Resolved** | Formula (line 187), a sample of at most 20 states, Q-query and fit projections, and a hold-collection stop (line 218). The sample source is restricted to existing logs. |
| N-L4: readability | **Resolved** | §5 S2/S3 are now in full sentences with separate S3a/S3b paragraphs. §6 and §7 are still terse, but they are not operative for S0–S3. |

Codex's R3-1 to R3-4 corrections (obedience coverage per command type, any-collection cost gate, strict fixed-point residual against a 95% snap tail, Gaussian-approximation wording) are also present in the text. I agree with them.

## New findings

### High

**R3C-H1 (S3 only; does not affect S0/S1): enemy dash-dodge readiness never affects artillery shells in this slice, so the S3a privileged channel and the S3b history variable are inert. This was my round-2 error.**

**Where:** decision 0037 ("initially enemy dodge readiness and remaining cooldown"); design §5 lines 179, 191, 195, 201; §7 ledger rows "Privileged dodge state" and "Public dash history"; my round-2 N-H1 fix item 2.

**Evidence:**
- **The dash only fires on player shots.** The GAME dash dodge is `gameReflexes` in `combat_rules.cpp:70–92`. It sets `dashReady = time + 1/time_rate` for storm (110 px, p = 0.9). It is evaluated only over `w.shots`, and it skips any shot whose source is not `Role::Player`: line 76 is `if(!shot.aimed||!src||src->team==u.team||src->role!=Role::Player||!(shot.manual||…||low))continue;`.
- **Shells never take that path.** Artillery shells live in `w.shells`, not `w.shots`. In my round-2 review I cited only the catalog numbers, not the trigger condition.
- **This slice has no player and abilities are off.** The NS1 contract records "no player/ability/private profile" (`CONTRACT.md:90`). The slice fixture sets `cfg->abilities=false` and checks `w.players.empty()` (`fixture.cpp:13, 21`). The catalog shield only multiplies speed (`combat.cpp:94`).
- **Shell evasion leaves no hidden readiness to learn.** Enemies evade shells by `dodgeShells` stepping out of predicted splash. That reaction is computed from public shells and has no cooldown.
- **Even with a player, the timing would not work.** Start→landing latency is at least windup 0.7 s plus flight. That exceeds the 1 s cooldown for most ranges, so readiness at the start decision would rarely decide the landing.
- **Most other candidate hidden state is already public.** The NS1 snapshot publishes every unit's `cooldown`, `cooldown_max` and current `target`, and enemy guns that are winding up appear as `cast` threats with release and landing times (`schema.cpp`, `snapshot`).

**Consequence:**
- S3a would fit a channel that is constant in effect.
- The readiness-changes-labels row (line 219) would fire only after the search teacher, probe budget and timing sample had been built.
- S3b's recoverability audit would validate a variable that does not matter.

The structure of 0037 is still right. Only the variable is wrong.

**Fix (drafter, before any S3 build; owner confirmation of the replacement variable):**
1. Before choosing a replacement, make a code-read inventory of the enemy state in the admitted cells that is (a) not in the NS1 public snapshot, (b) able to change own-shell damage or own losses within the t+6 horizon, and (c) recoverable from bounded public history. Apparent candidates in this slice:
   - the enemy controller's movement intent or goal, which can be inferred from a velocity history (the engine already has a history-based "smooth lead" over 0.3 s and an "adaptive" lob lead after about 1 s of steady motion);
   - the enemy's think and shell-dodge decision cadence (`thinkEvery` 0.2 s);
   - enemy energy, which is private, though it rarely binds at a cost of 10 and regen of 34/s.
   
   If none of these changes timing labels in at least 5% of probed states, the honest options are:
   - an owner-approved opponent rule that creates a recoverable hidden state, for example enabling enemy abilities so that disengage/shield cooldowns exist, or letting the dash react to visible incoming shells. This is a declared opponent-rule change, not a physics edit of frozen code paths.
   - recording that this slice has no natural history variable for leader timing, so S3b is NOT_EXERCISED by construction.
2. Amend 0037's "initially" variable through the owner, as a one-line confirmation. Update the S3a channel inventory, the §7 ledger rows and the S3b recoverability rule to match.
3. Cheap early evidence: in the S1 pilot logs, also count enemy dash events and `dashReady` changes per cell (expected zero) and enemy shell-dodge movement events. This needs no extra fights and confirms the finding empirically before S3 is designed further.

### Medium

**R3C-M1 (affects S1): the wrapper-miss admission stop uses the raw commanded-point miss. That metric penalises the planner's deliberate spread, and in dodging cells it is confounded by the enemy's reaction to the real shell.**

**Where:** §5 S1 line 109 ("The raw commanded-point miss is still the conservative admission metric; an intentional spread that fails it needs a prospective wrapper revision"); stop row line 131.

**Evidence:**
- **Spread inflates the raw miss by design.** N-M1 was about stale *lead*. On moving and dodging cells the copied planner mostly picks Net, Wall, Trap or Sweep, whose points sit deliberately off the led centre by tens of px. A Net shell that sits off-centre to catch a stepping enemy has a large raw miss against the enemy's observed position by construction. A mean excess above 10 px (splash/4) is then likely whenever the spread families are chosen. The row would demand a "wrapper revision" with no fix available short of removing the teacher's spread, which is the group value S2 is meant to learn.
- **The shadow comparison is confounded in dodging cells.** The autonomous counterfactual is never launched. Its "observed focus position at landing" therefore comes from an enemy that is stepping out of the *real* commanded shell's predicted splash, so the two misses are not measured against the same enemy behaviour.

The design already computes the right quantity: the shape-subtracted miss, which compares the refreshed led centre with the autonomous intercept.

**Fix:**
- Make the S1 stale-lead stop use the **shape-subtracted** paired miss, and evaluate it on a **moving, non-dodging** pilot cell (enemy `dodgeShells` off, otherwise the same). There the observed landing positions do not react to the shell, so the shadow comparison is valid.
- Keep the raw miss and the dodging-cell misses as reported diagnostics, split by planner family, with Focus-family (zero-shape) plans also given their raw miss.
- If adding a non-dodging moving cell exceeds the four-cell S1 cap, it is a wrapper-check cell, not a tactical candidate. Count it separately.

**R3C-M2 (affects S1 cell admission and the sealed N): the S1 detectability gate does not match the S2 "useful" decision rule.**

**Where:** §5 S1 lines 111–113 (admission: primary-axis `MDE_N ≤ useful effect`); line 125 (useful = point estimate ≥ threshold, CI excludes zero, **and** both harm bounds within tolerance).

**Evidence:**
- **The point-estimate rule halves the power at the threshold.** `MDE_N ≤ U` gives about 80% power for "CI excludes zero" at a true effect U. The rule also needs the point estimate to be at least U, and at a true effect exactly U that holds only about 50% of the time. About 80% power for the full primary rule needs `U + 0.84·s/√N ≤ true effect`.
- **The harm bound is never checked for feasibility.** Harm tolerance is 0.5·U. With zero true harm, the one-sided 95% bound fits inside it only if `1.645·s/√N ≤ 0.5·U`, that is `3.29·s/√N ≤ U`. That is *stricter* than the primary MDE (`2.80·s/√N ≤ U`) for an axis with similar normalised spread.
- **Result.** A cell can pass S1 admission yet be likely to end as "inconclusive/tradeoff" at S2 with zero true harm. That outcome then reads as a park or owner tradeoff, not as a power failure.

**Fix:**
- In S1, also report, per non-primary harm axis at the candidate N, the planning one-sided harm half-width `1.645·s_up/√N`. For saturated or sparse axes, use the sealed binomial-fallback bound.
- Admit a cell at that N only if the half-width is at or below the sealed harm tolerance.
- Then do one of two things:
  - state the useful rule's power honestly: about 50% at a true effect equal to U;
  - or plan N so that the effect the drafter expects is at least `U + 0.84·s_up/√N`.
  
  The simplest consistent choice is to keep the rule and say "MDE ≤ U admits detectability of non-zero effects, not an 80% chance of a 'useful' verdict".

**R3C-M3 (affects S1): "changed commanded assignment and physical shell/impact patterns on at least 5%" has no stated comparison.**

**Where:** §5 S1 line 111; stop row line 129.

**Evidence.** The paired T-unit-alone and T-unit+wrapper fights diverge after the first differing action, so decisions cannot be aligned across arms. "Changed" could therefore be computed across arms (chaotic, which is the round-2 R2-3 trap again) or against an unstated baseline.

**Fix:** define it as an on-state shadow, the same as the miss metric. At each eligible multi-gun decision in the T-unit+wrapper arm, a decision counts as changed if:
- the commanded focus differs from the gun's autonomous target, or
- the commanded assignment differs from the autonomous assignment, or
- the refreshed commanded point differs from the autonomous intercept by more than splash/4.

The physical-impact part counts impacts whose commanded point is more than splash/4 from the shadow autonomous point. Report the numerators and denominators.

### Low

**R3C-L1 (affects S0): the scope of S0's group-label conflict check is ambiguous, and so is whether S0 may call the copied planner.**

**Where:** §5 S0 lines 93–103.

**Evidence.**
- **The new group labels cannot be rebuilt from v2.** The new focus/assignment/shape labels need the startable-projected wrapper and the provenance led centre ("a queue point alone may not identify them", line 39). The v2 NS1 teacher was ready-only and logged queue points (`CONTRACT.md:90–92`), so these labels are generally *not* reconstructible from v2.
- **The read-only rule conflicts with rebuilding them.** S0 also says "without executing the engine". Running the copied planner on stored snapshots to rebuild labels is ambiguous under that rule.
- **The conflict row reads two ways.** The line-103 row ("exact active-label conflicts in the corrected oracle's fully encoded context") could be read as covering group and command-conditioned labels that have no command context in v2.

**Fix:**
- Scope S0's conflict row to the **command-absent autonomous unit heads** reconstructible from stored encoded views.
- Mark focus/assignment/shape group labels "unresolved until S1/S2" unless v2 stored the provenance centres.
- State explicitly whether a pure function call of the copied planner on stored public snapshots counts as allowed read-only analysis. My recommendation: it is not allowed in S0; defer it to S1.
- Label the S0 multi-gun coverage as a **ready-only lower bound**, because the S2 wrapper projects startable guns as ready. A <5% reading should then send the case to S1 for measurement, not straight to a cell redesign.

**R3C-L2 (affects S0/S1 start): the approval record and the owner quote.**

- **Approval is not recorded.** The design header (line 3) says the "execution amendment awaits owner approval", and §7's first stop row defers execution without a *recorded* owner approval. Codex is now building S0/S1. The DAgger r1 receipts exist (`DAGGER_V2_R1_RESULTS.json`), so the protected-job half of that row appears satisfied. Record the owner's S0/S1 go-ahead verbatim, in a decision note or the design's status line, before S0/S1 execution (decision 0037 explicitly does not authorize it). PLAN_CURRENT is frozen by owner instruction, so it cannot carry this record.
- **The owner quote may differ.** The quote in the design (line 15) and in 0037 reads "to **be** sure". The ruling relayed to me reads "to sure". I cannot see the original message. Confirm the verbatim text and restore it exactly if the owner wrote "to sure".

## What is sound

- The S3a/S3b separation matches the owner's ruling.
- S3a cannot make RRG-state claims and carries a reviewer withdrawal row.
- S3b's structural channel removal, the evaluation-path audit with zero exceptions, and the conservative note on what child publications may carry to P0 are right.
- The P0 gate needs both validation and closed-loop evidence in the same cell.
- The one-refresh wrapper is precise about locks, expiry, fallbacks and observable inputs.
- The five-arm S2 panel cleanly separates autonomous, leader-learning and wrapper-utility gaps.
- The search horizon, continuation and immediate-only control are fair to waiting.
- The cost formula is honest about a three-second rollout per expansion.
- The yes/no rows each have one action and one role.
- Living documents are not pinned.

No numeric scores are assigned.
