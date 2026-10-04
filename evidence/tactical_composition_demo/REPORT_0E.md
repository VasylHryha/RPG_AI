# Experiment 0e — replacement and connection, two pieces: results (exploratory; NOT a milestone, NOT C6 evidence)

Status: COMPLETE. One execution from commit `1d21533` (registration `9583017`, corrected `bb5ff7f` and `1e58a6e` after the Codex pre-run review and two re-reviews, the last
APPROVE_WITH_NOTES), started after the owner's explicit approval of `SPECIFICATION_0E.md` (decision 0028 item 10). 30 of 30 seeds, no errors, no retry. Wall 2,140 s (36 minutes),
children CPU 14,631 s, peak 0.34 GB per worker; load at the start 5.7 (another project's jobs raised it during the run; no cap was reached). Raw records, saved models and the
accounting are in `run_0e/` (`SUMMARY.json` is the record). Verdict words are exploratory vocabulary. Every interval below is an exact order-statistic interval of the median over
30 seeds (Clopper-Pearson for the seed share) at error 0.01 per claim; the run used one invented task (V3 of `tactics_e2.py`), a scripted teacher, imitation and two scripted opponents.

## What was tested

A unit of two pieces: **AIM** picks which enemy to attack; **MOVE** decides the step toward the enemy AIM chose. The **connection** is AIM telling MOVE that enemy's position.
Pieces: L (learned, taught separately), J (a conventional jointly trained policy with the same two branches), O (the scripted teacher's). Comparators: Fp (a conventional network
with one step per enemy slot: a structured conventional policy), Fflat (the best tested truly flat network), rush (walk at the nearest enemy).

## Gates (all as registered)

Headroom teacher minus rush 0.335 [0.324, 0.351] (rush 0.381, kiter 0.292 per opponent): passed. The task needs each part: replacing the teacher's target choice with "nearest enemy"
costs 0.145 [0.131, 0.166], replacing the connection with "nearest enemy's position" costs 0.160 [0.149, 0.177], an approach-only step costs 0.367 [0.356, 0.383] (diagnostics; the
connection one gates B1). J qualifies as a host (0.305 [0.289, 0.321] over rush); Fp qualifies (0.303 [0.292, 0.319]); **Fflat does not** (0.040 [0.018, 0.057], lower bound below 0.03).

## Verdicts

| Claim | Main numbers (median [interval]) | Verdict |
|---|---|---|
| **A1. Learned pieces replace the scripted ones** | prequalification: AIM admissible 0.992, MOVE 0.981 (hold 0.985, approach 0.983, back-off 0.960); win score against the teacher: AIM swapped +0.007 [0.002, 0.009], MOVE swapped −0.035 [−0.043, −0.030], both −0.028 [−0.037, −0.019] (per opponent all above −0.05); fidelity −0.008, −0.019, −0.027 | **SUPPORTED** (bar −0.05; the learned MOVE is the closest, its worst bound −0.045 against rush and kiter) |
| **A2. Swap compatibility with a conventional policy** | J's AIM with our MOVE +0.013 [0.008, 0.020]; our AIM with J's MOVE −0.010 [−0.015, −0.005] (win, against J itself); fidelity +0.001 and +0.011 | **SUPPORTED** (bar −0.03) |
| **B1. Useful connection** | intact against "nearest enemy's position": +0.164 [0.153, 0.179]; against a wrong living enemy +0.249 [0.235, 0.269]; against an empty message +0.680 [0.658, 0.698]; normalized by headroom 0.42 to 0.56, 0.66 to 0.85, 1.86 to 2.19; reversing the message drops fidelity by 0.733 | **SUPPORTED** |
| **B2. Stable within the tested envelope** | function: +0.306 [0.293, 0.324] over rush, 30 of 30 seeds above +0.10 (share bound 0.838 > 0.80); small noise costs 0.000 win / 0.004 fidelity; 1% wrong targets 0.005 / 0.009; a 10% scale fault costs our unit **less** than the teacher (win −0.073, fidelity −0.013 relative at 0.9; −0.000 and −0.038 at 1.1); spread across seeds: observed IQR 0.024, **exact upper bound 0.054 against the bar 0.05** | **INDETERMINATE** (every other component passed; the spread component could not be confirmed at 30 seeds and, as disclosed before the run, can never refute) |
| **B3. Stronger than a qualified conventional policy** | our unit minus Fp: −0.004 [−0.011, +0.011] (negative witness: clearly below the 0.03 bar); our unit minus Fflat: +0.272 [0.256, 0.291] (Fflat did not qualify, reported only) | **REFUTED** |

## What this shows, in plain words

- **Small pieces with one job each can be built, checked alone, swapped and combined into a unit that plays nearly as well as the expert** (within about 0.03 win score), and they swap with the parts of a conventional AI in both directions with no loss beyond 0.01. (A1, A2)
- **The connection between pieces is real, measurable and matters**: when AIM's choice reaches MOVE intact the unit wins clearly more than when MOVE is given a default, a wrong or an empty message (0.16 to 0.68 win score). The task was revised in development precisely so that this question can be asked: in the original sandbox target choice did not matter and the connection could not be useful. (B1)
- **The assembly tolerates small faults on the connection** (noise and 1% wrong targets cost almost nothing; a scale fault hurts it less than the scripted expert). Whether its seed-to-seed spread is below 0.05 is not established at 30 seeds (observed 0.024, bound 0.054), so the stability claim as registered is undecided, not refuted. (B2)
- **Built from pieces is not stronger than a well-built conventional policy**: a network with one step output per enemy plays exactly as well. A truly flat network is far weaker (0.27 behind) and does not even qualify. What matters here is the **structure** (decide per enemy, then act on the chosen one), whether it is built from separate pieces or trained as one network. (B3)

## Limits (stated plainly)

- One invented task, chosen (by a rule fixed beforehand, by the author's account) so that the connection matters; one scripted teacher; imitation, not learning from outcomes; two scripted opponents; 30 seeds replicate one environment.
- The connection is **hand-specified** (I defined what AIM sends and what MOVE receives). Nothing here tests whether pieces can **discover** a compatible connection, which is the part of the owner's idea that ordinary modular AI does not already contain.
- Stability under scale faults is judged relative to the teacher (a large loss the teacher shares is the task's sharp hold band, not the wire); fault draws are sequential per episode; fidelity is measured on a held-out pool, not on the states each policy met in play.
- Fp computes per-slot teacher labels for every slot; J queries the teacher on its own choice; parameter counts differ (L 787, J 9,283, Fp 2,313, Fflat 20,997).
- Nothing here tests geometry, oscillators, "vibration" or any RRG hypothesis.

## What we learn and what follows

1. Composition by pieces is **viable and checkable**: each piece can be qualified alone, swapped, and its connection measured by cutting it. That is the engineering half of the owner's idea, now with a definition of connection quality (gain of the intact connection over a cut one, with the pieces fixed) that works.
2. Composition by pieces is **not a performance advantage** over a conventional policy with the same structure in this task. The case for pieces must rest on what they make possible (swapping, checking, reusing, changing one part), not on winning more.
3. The open question is the one this experiment could not ask: **can pieces find their own connection** (compatibility by declared signature, among distractors, without being told the wiring)? The recommended next proposal is that small discovery pilot; then the three-piece ladder (if a third behavior qualifies), the squad level, and learning from outcomes.

No cross-family review of this result exists yet (Codex reviewed the registration, not the result); none is claimed.
