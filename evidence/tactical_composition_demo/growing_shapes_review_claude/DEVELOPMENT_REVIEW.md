FINDINGS (the delivery is faithful; the run's FAIL stands; three design defects owned by the drafter, Claude)
Reviewer family: Claude (drafter of DESIGN_0H; reviewing Codex's execution)
Reviewed: `growing_shapes/runner/DEVELOPMENT_REPORT.md` and `development_20261006/RESULTS.json`, delivery commit `f87158b` and its note `71fcbee`, imported at `7e5f6b0` without the raw ledgers (see `LEDGERS_NOT_IN_GIT.md`).

## What the run shows

1. **Structures form, and copies of them are reproducible.**
   - G1 PASS in both arms, with 251–1154 admitted snapshots per seed and 11,862 in all.
   - G5 PASS: each evaluated copy matches its carrier-shifted copy (D ≤ 0.1 in 20 of 20 for every seed). This is numerical copy covariance only, as the design states.
2. **Nothing yet shows that they do a task.**
   - The whole-medium competence is **exactly 0.021918826832967767 in all 16 intact runs and 14 of 16 controls** (the exceptions are the controls of task_blind 106062, −0.278, and reward 106077, −0.050).
   - A score that does not depend on the learned state is a constant floor, most likely the scored abstention: one global readout over about 44 mixed-phase elements gives coherence < 0.05 in every episode. **The competence half of G0 therefore measured nothing.** This is not confirmed yet; it is the first recheck question.
3. **G1c (descriptive):**
   - Snapshot means per task are small: perceive about 0.01, move −0.03 to −0.94, remember_static −0.03 to −0.11, choose 0.10–0.22.
   - `move` is never a best task. `choose` dominates the best-task counts.
   - Two different seeds in different arms (task_blind 106065, reward 106076) have identical move and remember_static means (−0.032916, −0.107498). The recheck must explain why: the same template, an abstention floor, or a shared artifact.

## Defects in the design (the drafter's responsibility under the stop row)

- **D1, G0' cannot pass at a saturated budget.**
  - |slope| ≤ 0.5 per 100 episodes held in 16 of 16 seeds (the largest is 0.18).
  - **Every** seed fails only on the "no late birth rejection" clause. A population living at its budget always rejects some births, so steady turnover at the cap is read as instability. The clause tests the budget, not stability.
- **D2, G0 could never pass.**
  - The paired control dropped requests in 16 of 16 seeds (28–80 drops), and any drop prevents PASS.
  - Together with finding 2, both halves of G0 were uninformative in this configuration.
  - Coverage alone favoured intact in 10 of 16 seeds; this is descriptive only.
- **D3, whole-medium competence uses one global readout.** It cannot credit local structures, which is what 0h grows. Competence should be read per structure (as G1c does) or through the library, not from the whole medium.

Any change to these is a new design revision on fresh development seeds. It is not a re-analysis of this run.

## Accounting and process notes

- **N1, wall time.** "2.059 wall hours" is monotonic time while the laptop was awake. The host went into idle sleep at 01:24 and ran only in short dark wakes (pmset log). Actual elapsed time was about 00:50 → 08:37.

  The stage totals (14.7 worker hours against an 11.4 h projection) are consistent with this. The report should say "awake time".

  **Fix (process):** wrap long overnight runs in `caffeinate -i -s`.
- **N2, evidence volume.** About 14 GB of ledgers came in the delivery commit, and the largest is 680 MB (GitHub's limit is 100 MB). They are kept on disk and on the local branch `codex/0h-development`, identified by hash.

  The next runner should keep ledgers outside git by design, or log recovery events more compactly.
- **N3.** The delivery is consistent: every non-ledger file is byte-identical to the delivery commit. No reviewed code, constants or judging entropy changed.

## Next

1. Run the owner's recheck prompt on this chunk (queued after the C6 quiet timing).
2. Its first questions: confirm or refute the abstention reading of finding 2; explain the duplicate G1c means.
3. Then the drafter proposes revision 6 to the owner. The candidates are a G0' stability clause that tolerates turnover at the budget, a G0 competence read per structure or through the library, and a control queue that cannot always drop.

## Addendum 1: the floor is identical everywhere (from the 16 committed `REPORT.json.gz`)

- **The final whole-medium score per task is identical, to every digit, in all 16 intact runs of both arms:** perceive 0.0050, move −0.0329, remember_static −0.1075, choose 0.2231. The mean of these four is the 0.0219 of finding 2.

  task_blind 106065's G1c means equal the same move and remember_static values, which explains finding 2's duplicate. Its 20 evaluated snapshots scored that same constant.

  **So the whole-medium read-out does not depend on the learned state.** It is a fixed floor, most likely abstention. Snapshot means below it (for example choose 0.10 against the floor 0.22) mean some snapshots act and do **worse** than abstaining.
- **The population is pinned by the budget, not by need.** Over the last 20% of training, N is 42–45 in every seed, intact and control alike.

  Cost = N + 0.1 × undirected pairs reaches 64 at about 44 elements. Meanwhile coverage is only 6–22%: sites stay uncovered, B1 keeps asking, and the cost cap rejects the births. Turnover (D1 deaths of unlocked newborns) replaces elements without raising coverage.
- **The control was starved.** It made 23–71 additions against the intact run's 74–149. It dies less (3–52 deaths), so it sits at the budget and its requests fail feasibility.

**Reading:** growth fills the budget and then churns. Newborns rarely lock to their sites, the read-out never responds to what is learned, and the snapshots that do respond score below abstention.

The engine and the run are faithful. The design does not yet connect structure to action. That is defect D3, and it is now the main one.

## Addendum 2: the owner-requested Codex recheck (`growing_shapes/runner/DEVELOPMENT_RECHECK_REPORT.md`, CHANGES_REQUIRED for the next design; recorded verdicts unchanged)

**Confirmed:**
- An empty read-out explains the constant. All 16 intact and 14 control final media have no element inside radius 2. The 0.0219 is the mean of the four default-action scores.
- D1: 7,481 late rejections, all for cost.
- D2: 775 drops, all for cost. Control additions were 26–71% of intact births.

**Corrections to this review and to the draft (accepted):**
1. **"Radius up to about 9" was wrong.** Final radii reach 246 (intact) and 420 (control): the law has no confinement, so groups drift away. **9,493 of 11,862 snapshots had no member within drive reach of any sensor** at their check time, and only 500 had a read-out member. This is a new defect, **D5: structures drift out of both sensing and action.**
2. **"All 20 snapshots of 106065 and 106076 scored the constant" was too strong.** Move and remember_static were constant, but some perceive and choose scores were not. Copies keep moving during evaluation: 13 initially empty templates scored off the floor.
3. **G1c does not read each structure at its own centre.** It keeps absolute positions and the same origin read-out. D3 therefore applies to G1c as well; a per-structure read-out would be new.
4. Descriptive only (320 snapshots scored, 11,542 not): 64 perceive, 51 remember_static, 1 choose and 0 move snapshots exceed both the default and random. 208 of the 320 sit on the floor in all four tasks, so G5 passes for silent copies too.
5. The choose default (the lowest live id) already beats random, so a positive choose score alone credits nothing.
6. "Wall hours" are awake monotonic time (corrected in the report). The result was written at 08:23 local.

The draft's refinements are recorded in `DESIGN_0H_REV6_DRAFT.md` section 4.
