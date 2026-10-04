# Experiment 0e — replacement and connection, two pieces: results (exploratory; NOT a milestone, NOT C6 evidence)

**Corrected 2026-10-04 after a recheck** (four same-family audits and a full round trip): the verdicts are unchanged and every number re-derives exactly, but several readings below
were too strong and are rewritten; the first text is in git history (`b507190`). The essential corrections: (1) the connection's value against a **coherent** alternative is +0.124,
not the +0.164 of the registered cut, which also counts a 0.045 penalty for attacking one enemy while walking to another; (2) **B3 could not have been won**: the scripted teacher
itself is only +0.030 [0.0125, 0.0375] above the conventional policy; (3) **B2's spread test measured episode-sampling noise**, not the unit's stability; (4) the learned unit is within
0.035 of the teacher (not "about 0.03"). Section "Post-run recheck" at the end lists everything.

Status: COMPLETE. One execution from commit `1d21533` (registration `9583017`, corrected `bb5ff7f` and `1e58a6e` after the Codex pre-run review and two re-reviews, the last
APPROVE_WITH_NOTES), started after the owner's explicit approval of `SPECIFICATION_0E.md` (decision 0028 item 10). 30 of 30 seeds, no errors, no retry. Wall 2,140 s (36 minutes),
children CPU 14,631 s, peak 0.34 GB per worker; load at the start 5.7 (the run record has the start load only; no cap was reached). **Conduct:** at the owner's request ("can you check what is already done and its results"), the author read the 24 per-seed files finished by 12:19 and showed descriptive medians before the run ended; nothing was changed, stopped or re-run, the verdicts were computed by the registered code at the end, and on those 24 seeds every verdict would have been the same. The approval quoted in decision 0028 item 10 does not name the specification literally (it answered the author's plain explanation of it). Raw records, saved models and the
accounting are in `run_0e/` (`SUMMARY.json` is the record). Verdict words are exploratory vocabulary. Every interval below is an exact order-statistic interval of the median over
30 seeds (Clopper-Pearson for the seed share) at error 0.01 per claim; the run used one invented task (V3 of `tactics_e2.py`), a scripted teacher, imitation and two scripted opponents.

## What was tested

A unit of two pieces: **AIM** picks which enemy to attack; **MOVE** decides the step toward the enemy AIM chose. The **connection** is AIM telling MOVE that enemy's position.
Pieces: L (learned, taught separately), J (a conventional jointly trained policy with the same two branches), O (the scripted teacher's). Comparators: Fp (a conventional network
with one step per enemy slot: a structured conventional policy), Fflat (the best tested truly flat network), rush (walk at the nearest enemy).

## Gates (all as registered)

Headroom teacher minus rush 0.335 [0.324, 0.351] (against rush 0.381, against kiter 0.292): passed. The task needs each part: replacing the teacher's target choice with "nearest enemy"
costs 0.145 [0.131, 0.166], replacing the connection with "nearest enemy's position" costs 0.160 [0.149, 0.177], an approach-only step costs 0.367 [0.356, 0.383] (diagnostics; the
connection one gates B1). J qualifies as a host (0.305 [0.289, 0.321] over rush); Fp qualifies (0.303 [0.292, 0.319]); **Fflat does not** (0.040 [0.018, 0.057], lower bound below 0.03; against rush alone its lower bound is −0.013).

## Verdicts

| Claim | Main numbers (median [interval]) | Verdict |
|---|---|---|
| **A1. Learned pieces replace the scripted ones** | prequalification: AIM admissible 0.992, MOVE 0.981 (hold 0.985, approach 0.983, back-off 0.960); win score against the teacher: AIM swapped +0.007 [0.002, 0.009], MOVE swapped −0.035 [−0.043, −0.030], both −0.028 [−0.037, −0.019] (per opponent all above −0.05); fidelity −0.008, −0.019, −0.027 | **SUPPORTED** (bar −0.05; the closest component is both pieces against kiter, bound −0.045; the learned MOVE's bounds are −0.043) |
| **A2. Swap compatibility with a conventional policy** | J's AIM with our MOVE +0.013 [0.008, 0.020]; our AIM with J's MOVE −0.010 [−0.015, −0.005] (win, against J itself); fidelity +0.001 and +0.011 | **SUPPORTED** (bar −0.03) |
| **B1. Useful connection** | intact against "nearest enemy's position": +0.164 [0.153, 0.179]; against a wrong living enemy +0.249 [0.235, 0.269]; against an empty message +0.680 [0.658, 0.698]; normalized by headroom 0.42 to 0.56, 0.66 to 0.85, 1.86 to 2.19; reversing the message drops fidelity by 0.733 | **SUPPORTED** |
| **B2. Stable within the tested envelope** | function: +0.306 [0.293, 0.324] over rush, 30 of 30 seeds above +0.10 (share bound 0.838 > 0.80); small noise costs 0.000 win / 0.004 fidelity; 1% wrong targets 0.005 / 0.009; a 10% scale fault costs our unit **less** than the teacher (win −0.073, fidelity −0.013 relative at 0.9; −0.000 and −0.038 at 1.1); spread across seeds: observed IQR 0.024, **exact upper bound 0.054 against the bar 0.05** | **INDETERMINATE** (every other component passed; the spread component's upper bound is the span of the 2nd to the 29th seed, and the observed spread equals what 600 episodes per seed produce by sampling alone: the scripted teacher, Fp, J and rush would all fail this bar too) |
| **B3. Stronger than a qualified conventional policy** | our unit minus Fp: −0.004 [−0.011, +0.011] (negative witness: clearly below the 0.03 bar); our unit minus Fflat: +0.272 [0.256, 0.291] (Fflat did not qualify, reported only) | **REFUTED** (but not winnable: the teacher itself is only +0.030 [0.0125, 0.0375] above Fp, so even a perfect copy of the teacher would not have cleared +0.03) |

## What this shows, in plain words (corrected)

- **Small pieces with one job each can be built, checked alone, swapped and combined into a unit that plays within the registered 0.05 margin of the scripted teacher** (medians from 0.007 better, AIM swapped, to 0.035 worse, MOVE swapped; both swapped 0.028 worse; worst bound −0.045). They swap with the branches of J at a cost of at most 0.015 (99% bound), and J's AIM with our MOVE gains 0.013. J has the same two-branch architecture as L, so this swap compatibility is close to automatic. (A1, A2)
- **The connection is used and is worth about 0.12 in win score.** Against a coherent unit that targets and walks toward the nearest enemy (0.610), the learned unit gains +0.124 [0.106, 0.132]. The registered cut (attack the chosen enemy but walk to the nearest) costs 0.164, because it also makes the unit incoherent (0.045 below the coherent nearest-enemy unit). A wrong enemy costs 0.249. The empty message (0.680) breaks the unit (it freezes, far below rush) and measures that MOVE needs an input, not the message's value. A cut-based measure therefore gives cut-dependent values; the coherent comparison is the one to use. (B1)
- **The unit tolerates the registered small faults** (noise 0.02: 0.000; 1% wrong targets: 0.005), and a 10% scale fault costs it less than the teacher at 0.9 and about the same at 1.1. Its absolute loss at 0.9 is 0.040 [0.026, 0.047], above the 0.03 used for the other small faults. Larger faults are not tolerated: a 50% scale fault collapses it (0.70 loss, far below rush), scale 2 costs 0.13, 10% wrong targets 0.034, noise 0.10 costs 0.015. Whether its spread across seeds is small was not measurable at 300 episodes per cell (B2 INDETERMINATE). (B2)
- **Built from pieces is not stronger than a conventional policy with the same per-enemy structure**: the difference is −0.004 [−0.011, +0.011] (the unit ahead in 13 seeds, behind in 16), and under imitation the teacher is the ceiling, which Fp already almost reaches. The tested flat network is far weaker (0.27 behind) at 3,000 states with the tested recipes; whether the per-enemy structure is the cause is not tested (Fflat also differs in head, width and recipe). (B3)
- **Fidelity to the teacher does not rank play.** The unit's joint fidelity is 0.096 above Fp's in every seed while their wins are equal, and a learned AIM wins slightly more than the teacher's own (LO minus OO +0.007 [0.002, 0.009]; Fp's AIM +0.014): the teacher is not the best player, which leaves room for learning from outcomes.

## Limits (stated plainly)

- One invented task, chosen (by a rule fixed beforehand, by the author's account) so that the connection matters (V3 is not all mixed teams: one of the five team mixes is all ranged, about 1 in 5 draws); one scripted teacher; imitation, not learning from outcomes; two scripted opponents; 30 seeds replicate one environment.
- The connection is **hand-specified** (I defined what AIM sends and what MOVE receives). Nothing here tests whether pieces can **discover** a compatible connection, which is the part of the owner's idea that ordinary modular AI does not already contain.
- Stability under scale faults is judged relative to the teacher (a large loss the teacher shares is the task's sharp hold band, not the wire); fault draws are sequential per episode; fidelity is measured on a held-out pool, not on the states each policy met in play.
- Fp computes per-slot teacher labels for every slot (9,000 computed, 7,604 living supervised); J queries the teacher on its own choice 2,048,000 times; L none; parameter counts differ (L 787, J 9,283, Fp 2,313, Fflat 20,997).
- Fixed-state fidelity and MOVE prequalification cover multi-enemy states only (about 13% of test states, mostly end-game, have one enemy); faults also act on those in play.
- The relabel and sham "controls" cannot fail by construction (the relabel decodes before MOVE sees anything; the sham discards its draw): they are implementation self-checks, not evidence.
- The registered cut applied on 35% of decisions (default) and 88% (wrong); "1% wrong targets" applied on 0.88%.
- Nothing here tests geometry, oscillators, "vibration" or any RRG hypothesis.

## What we learn and what follows (corrected)

1. Composition by pieces is **viable and checkable**: pieces can be qualified alone, swapped, and their connection's value measured, **if the comparison is coherent** (the connection is worth about 0.12 here against a coherent nearest-enemy unit). A cut that makes the unit incoherent, or breaks it, overstates the value.
2. Composition by pieces is **not a performance advantage** over a conventional policy with the same per-enemy structure here, and under imitation it could not be: the teacher is the ceiling. The case for pieces must rest on what they make possible (checking, swapping, changing one part, reusing at the next level).
3. Lessons for the next design: compare against coherent alternatives, check before the run that every claim is attainable by an ideal policy, size spread endpoints to the episode noise (or drop them), choose on one set of games and confirm on another, and do not treat fidelity to the teacher as play quality.
4. Next (owner's idea, 2026-10-04): **build structure bottom-up by measured connections**: connect every pair of pieces from a pool that includes decoys (and each piece with itself, a memory loop), measure each by performance against coherent alternatives, grow by adding a third and fourth piece only while performance clearly rises, stop when it no longer does, then treat the result as one piece and repeat one level up. This is the first test in which the wiring is not given by the author.

No cross-family review of this result exists yet (Codex reviewed the registration, not the result); none is claimed.

## Post-run recheck (2026-10-04)

- **Round trip:** all 120 saved models rebuilt; all 30 test pools regenerated with matching digests; all 1,050 fixed-state scores and all prequalification values identical to the record; 12 closed-loop cells replayed identically (`verify_run_0e.py`, `verify_run_0e_result.json`).
- **Independent re-derivation** of every gate, interval and verdict from the per-seed files by an auditor with its own code: identical to 1e-12.
- **New checks** of the V3 code path, which the registered tests did not cover (`test_ze_audit.py`): the batch doctrine equals the scalar doctrine; the oracle assembly plays exactly as the V3 teacher; the attack target stays AIM's choice under every wire fault; a tiny V3 seed's oracle fidelity is 1.0.
- **Corrections** (this report, rewritten above; registered files untouched, notes in `CORRECTIONS.md` section H): the connection value against a coherent alternative; B3 unattainable; B2's spread test is episode noise; A1 is within 0.035, not 0.03; "no loss beyond 0.01" is 0.015; scale 1.1 indistinguishable from the teacher and scale 0.9 absolute loss above 0.03; large faults collapse the unit; "exactly as well" is within ±0.011; the per-enemy structure as the cause is untested; fidelity does not rank play; the interim look is disclosed; V3 includes an all-ranged mix; J's 2,048,000 teacher queries; relabel and sham are self-checks.
