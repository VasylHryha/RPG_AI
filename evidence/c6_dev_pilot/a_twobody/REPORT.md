# Completed exploratory two-body pilot — NOT C6 EVIDENCE

Status: COMPLETE. One execution only, after the specification and harness commit `3173bab`.
C6 remains BLOCKED / R006 STOP. No historical result, equation, threshold, protocol, milestone status or project file was
changed. No R007, final entropy, mutation probe or panel ran. Nothing here assigns a C6 hypothesis verdict.

## Run accounting

1,536 of 1,536 planned runs complete, no errors, no missing, no retry, no stop. Wall 602.5 s (estimate was 6 to 9 minutes),
children CPU 3,438 s, peak child RSS 115 MB. Harvest: 3,430 level-1 templates (pool 1), 260 level-2 worlds (154 FORMED, 68
MERGED, 26 OTHER, 12 DRIFTING), 135 level-2 groups from 135 distinct source worlds, 32 level-2 pairs, 40 level-1 pairs.
Level 2: 640 short runs plus 96 long runs (T=1640, real criterion 6); level 1: 800 short runs.

## Predeclared verdicts (SPECIFICATION.md, applied as written)

| Prediction | Result | Verdict |
|---|---|---|
| P1 phase locking (level 2, effective gaps, informative offsets) | locked fraction 0.081 (n=172); decoupled baseline 0.0 (n=86) | REFUTED |
| P2 no distinct bound pair (coupled at end) | distinct-bound fraction 0.853 (n=416); FUSED fraction 0.0 | REFUTED (reading: a distinct-bound regime exists) |
| P3 phase-dependent push, then slip | push 0.302 (n=96), control quiet 1.0; slip 0.0 (n=64); separated before t=50: 0.0 | REFUTED |

## Defect recorded after the run (verdicts unchanged)

P1 and P3 score both levels in absolute time (`t` in [50,100] and [0,3]). The normalization ledger says own-level windows
scale with the level factor (C=3.4 for level-2 groups), so level 2 had about 3.4 times less own-level time than level 1 in
those windows. The P1 and P3 refutations at level 2 are therefore confounded by an estimator that did not follow the
ledger; the stored data do cover own-level windows (see the post-hoc analysis). This is the drafter's defect: the review
before the run did not catch it.

## What the stored data show (descriptive)

- **Pairs of level-2 groups do not fuse.** Of the long runs (T=1640, the level-3 horizon) at gap 0.6, 90.6% end as distinct
  coupled parts, 3.1% fused, 6.3% separated; the real criterion 6 holds in 96.9%. Hull overlap stays near zero. The
  B/r repulsion acts between elements of different groups too, so groups touch and stay apart.
- **The inter-group interaction is contact-only.** At gaps of 1.2 and above the phase rate and the approach rate are zero to
  machine precision (the k=8 nearest-neighbour rule never selects the other group's elements), at both levels. Pairs at
  gaps 1.2 to 4.5 therefore mostly sit still; "bound" cannot tell "interacting" from "static" there. At gap 0.6 the
  approach is real: R shrinks from 3.09 to 2.64 (median) against +0.17 for the decoupled control.
- **Phase-dependent push is much weaker at level 2.** Early approach slope at offset pi, gap 0.6: +0.034 for units, +0.004
  for groups. Anti-phase unit pairs separate in 40% of runs; anti-phase group pairs in 0%.

## Post-hoc analyses (not predeclared; `posthoc/`; descriptive only)

1. `posthoc_scaling.py` (own-level time): at contact (gap 0.6, offset pi/2) the early phase rate per own-level time unit is
   -0.063 for units and -0.043 for groups, a ratio of 0.68. Over the level-3 horizon, natural-case level-2 pairs at gap 0.6
   phase-lock: 86% of the 22 runs with an informative initial offset are locked in the last 340 time units (median offset
   1.43 rad at the start, 0.16 rad at the end); at gap 2.0 and 2.8 the fractions are 41% and 27%. The approach rate per
   own-level time per part radius is about 5 times weaker for groups (-0.031 versus -0.147 at offset 0; -0.0086 versus
   -0.0447 at pi/2). The own-level normalization (time by C2=3.4, length by part radius) is mine.
2. `posthoc_recovery_split.py` (stored R2-gate data, entropy 33333; no new run): level-3 candidates rejected on criterion 5
   fail on phase-pattern recovery, not membership: 14 of 14 in pass 1 and 16 of 17 in pass 2 (membership fails: 0 and 2).
   The median pattern error is 0.21 rad in pass 1 and 0.13 rad in pass 2, against the frozen 0.1 threshold: near-misses.
   In the same stored runs criterion 5 is the dominant level-3 failure (14 and 17 of 30 worlds), parts-alive only 4.

## Reading

With the C4 law, contact placement does not fuse level-2 groups in pairs, and groups phase-lock at contact given own-level
time. The pair-level evidence therefore does not support "fusion blocks level 3". The stored R2 data point to criterion 5
phase-pattern recovery missing the 0.1 rad threshold by a modest margin, with phase coupling nearly rescaling across
levels in own-level time (0.68) and the approach/position coupling about 5 times weaker. Untested hypotheses from this:
(a) weak position-restoring coupling at group scale and slow phase relaxation make recovery marginal at level 3; (b) in
five-group worlds the deeper units can still be compressed (level-2 failures are dominated by parts-alive: 11 and 9 of
30), which a two-body test cannot show.

## Limits

Two bodies only (level 3 needs at least three parts); one element law; one set of thresholds; pair-level statistics
over 32 level-2 pairs; post-hoc normalization chosen after seeing the data; the two-body map does not test the five-group
worlds in which the earlier merging was observed. No hypothesis verdict, no qualification of the repaired implementation,
no claim that RRG or this model can or cannot form level 3 under another law. Raw runs, plan, harvest records, inputs and
the exclusive latch are preserved in `run/`; `run/SUMMARY.json` is the final accounting record.

## Spec errors made before the run (my own, for the record)

I told the owner twice that a plan would work and each time found the premise weak: first that a placement-gap sweep
would fix merging (the law's contact-only coupling and hard-core repulsion make gap largely irrelevant), then that groups
would phase-lock and fuse (they do not fuse). The pilot was designed so its predictions could fail, and they did.
