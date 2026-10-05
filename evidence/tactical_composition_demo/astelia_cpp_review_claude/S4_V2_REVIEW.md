APPROVE_WITH_NOTES (development record; NOT_READY because of the runtime cap, not a scientific stop)

Reviewer family: Claude (claude-opus-5-5)
Reviewed: the S4 v2 development, merged at `7e83a73` from Codex's bundle; report `astelia_cpp/S4_V2_DEVELOPMENT_REPORT.md`
Date: 2026-10-05

## Process

- v2 was implemented per `DESIGN_0G.md` section 13 with its clarifications (knob cap 11, the enemy-set overflow rule, centre distances).
- 87 tests pass, and 324 v0/v1 fixture summaries are byte-identical.
- Fresh seeds, equal CMA-ES budgets.
- **Stages A and B passed the novice gates.** Stage C stopped after nine resonator generations, when the projected runtime exceeded the protocol's 180-minute cap. That is correct behaviour; no stage-C validation exists.

## Results (validation)

| Setting | Resonator v2 | Morale | Push-pull | Nearest |
|---|---|---|---|---|
| A: melee vs novice | +3.90 | **+5.98** | −2.49 | +0.84 |
| B: full vs novice | **+16.39** [14.91, 17.86] | +9.72 | −5.69 | −16.06 |
| B: full vs regular | −4.10 [−4.80, −3.40] | **+2.93** [1.68, 4.18] | −12.44 | −23.52 |
| Enemy guns alive vs regular | 7.82 of 10 | 8.59 | 10.00 | 10.00 |

## Readings (development)

1. **The range-aware distance worked against novice.** The resonator went from −0.11 (v1) to +16.39, clearly ahead of morale (+9.72). With full armies against novice, the circular state beat the plain number this time.
2. **Against regular the resonator improved** (−9.56 → −4.10) **but still loses**, and most guns survive (7.82 of 10, 107/200 timeouts). Morale wins against regular (+2.93) mostly through timeouts (188/200) with more of its own units alive, not by killing the guns (8.59 survive).
3. **The arms specialize again:** with one knob set, no arm beats both levels. The design's P1 (both levels) still fails for the resonator.

## Notes

- **Stage C is needed for P2 and P3.** The pool panel is slower. Rerunning stage C alone (from the stage-B knobs, same protocol) needs a larger runtime allowance or the 0g controller speed-up (parked, `docs/IDEAS_AND_ROADMAP.md` 4.2). It is the drafter's and owner's decision; not an equation change.
- **The gun problem persists.** The next diagnostic is a replay of resonator against regular with v2 knobs, to see whether units now close on the guns and die, or still hover. It is cheap (`viz_0g/make_replays.py` with v2 knobs).
