APPROVE_WITH_NOTES (as a development record; the STOP stands)

Reviewer family: Claude (claude-opus-5-5)
Reviewed: the original S4 run (protocol `S4_PROTOCOL.md`, declared at `9690d67`), report `astelia_cpp/S4_DEVELOPMENT_REPORT.md`, evidence `astelia_cpp/s4_development/`
Receipt reviewed: `astelia_cpp/S4_REPORT_RECEIPT.json`, sha256 in the commit of this file
Date: 2026-10-05. The amended CMA-ES run (`S4_AMENDED_PROTOCOL.md`) is reviewed separately once it finishes.

## Verdict

**The original run is a sound development record, and its STOP is correct.**
- The tuned resonator does not beat novice head-to-head with full armies:
  - stage B knobs: −10.98 (SE 0.38);
  - stage C knobs: −6.92 (SE 1.09).
- **The protocol was declared before any tuning fight.** Every arm had an equal budget (7,680 fights) on the same clusters, and validation used separate seeds. The 23,040 tuning fights had zero controller failures and zero cache hits.
- My request was changed during the run (`ee21545`). Codex kept the run under its declared protocol and recorded the change, which was correct.

## Checked independently

- **No opponent simulated our controller:** across all 26,752 fights in `fights.jsonl.gz`, the counters record 0 forks, 0 search calls and 0 artillery rollouts, in all three settings (melee10, full head-to-head,
  the P2/P3 pool).
- **All four arms are reported per stage**, including the STOP stage.
- **The morale anomaly is explained as a configuration difference:** the regular level brings a line formation. It is not a defect.

## What the numbers say (development, validation split; S = survivors − enemy survivors)

| Setting | Resonator | Morale | Push-pull | Nearest |
|---|---:|---:|---:|---:|
| A: 10v10 melee vs novice (clean test, no projectiles) | +0.95 (SE 0.37) | **+4.33** (0.21) | +0.77 (0.41) | +1.30 (0.39) |
| B: full armies vs novice | −10.98 | −5.28 | −4.20 | −18.14 |
| B: full armies vs regular | −10.02 | −0.97 | −0.86 | −21.20 |
| C: the P2/P3 pool (19 doctrines, elite skills without rollout) | **+1.73** | +1.43 | −5.78 | −20.07 |

| Paired contrast on the pool | Block mean | 95% interval |
|---|---:|---|
| resonator − morale (P2) | +0.30 | [−1.25, 1.85]: no difference |
| resonator − push-pull (P3) | **+7.50** | [6.21, 8.80] |

**Readings** (development only):
1. **The damage-driven, neighbour-shared state works against the doctrine pool.** Both the resonator and morale beat plain push-pull forces by a wide margin (+7.5) and the floor by about 21.
2. **The circular beat adds nothing measurable over a plain number** in this run (P2 about 0).
3. **Against the scripted levels head-to-head with full armies, every arm loses.** In melee only, every arm wins slightly. This fits the declared projectile asymmetry (built-in brains see and
   dodge shots and shells, while our controllers cannot), but this run does not establish it as the cause.
4. **Knobs do not transfer between panels.** Morale tuned on the pool (stage C) falls to −16.8 against novice, against −5.3 with its stage B knobs.

## Notes

1. **Under-tuning:** the accept-if-better-by-2-SE gate accepted few rounds (resonator 1 of 8 in B, 2 of 8 in C). With 10 knobs, the arms with more knobs are likely less converged than push-pull's 2.
   The amended CMA-ES run addresses this. Compare the two runs' validation results directly.
2. **The STOP used stage C knobs on the novice panel** ("final resonator"). P1 should be judged with knobs tuned for P1's panel (stage B). Both are negative, so the STOP holds either way.
   Specify the P1 knob source for S5.
3. **The variance unit matters:** the pool's configuration-cluster SD (about 13) is far larger than its shared-seed-block SD (about 3). S5 must fix one inference unit before δ and n are approved.
   The proposed δ = 3.5 derives from the larger, pooled SD.
4. **Controller cost** made this run slow (about 10× the nearest controller per fight in S3). A neighbour grid and fewer state updates should come before any further large run.
