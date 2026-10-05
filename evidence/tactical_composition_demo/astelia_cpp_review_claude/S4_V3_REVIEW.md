APPROVE_WITH_NOTES (development record; READY_FOR_S5)

Reviewer family: Claude (claude-opus-5-5)
Reviewed: the S4 v3 development, merged at `b7f635d` (Codex `cb9c9df`, `e60fbe5`); report `astelia_cpp/S4_V3_DEVELOPMENT_REPORT.md`
Date: 2026-10-06

## Process

- v3 is implemented per `DESIGN_0G.md` section 14 with the effective-commit clarification.
- 113 tests pass, and 408 v0/v1/v2 fixtures are byte-identical.
- Fresh seeds, equal CMA-ES budgets, stages A/B/C within the 360-minute allowance (167.65 min).
- Validation is complete for all four arms, with timeouts, guns alive, replays, and δ and n planning.

## Results (validation)

| Setting | Resonator v3 | Morale v3 | Push-pull | Nearest |
|---|---|---|---|---|
| A: melee vs novice | **+5.74** | +3.21 | −2.12 | +1.37 |
| B knobs: full vs novice | +17.35 | **+24.68** | −7.25 | −17.41 |
| B knobs: full vs regular | −7.57 | **+8.55** [7.21, 9.89] | −12.25 | −23.65 |
| C knobs: 19-doctrine pool | **+12.45** | +11.99 | −13.63 | −20.12 |
| C knobs: full vs novice / regular | +8.07 / −1.66 | +8.55 / **+5.00** | −6.74 / −12.39 | −17.22 / −23.41 |

| Paired on the pool (C knobs) | Block mean | 95% interval |
|---|---|---|
| P2 resonator − morale | **+0.46** | [0.10, 0.82] |
| P3 resonator − push-pull | **+26.09** | [25.87, 26.30] |

The proposed δ is 3.5 survivors (owner approval required).

## Readings (development)

1. **"Beat the code" is reached, by the morale twin.** With the v3 skeleton, plain morale beats the scripted novice and regular head-to-head with full armies (stage-B knobs; regular +8.55). It does so mostly through timeouts with more of its units alive (191/200): it outlasts the guns rather than destroying them (8.96 of 10 survive).
2. **The circular beat:**
   - leads in melee (+5.74 against +3.21) and on the pool (+0.46, interval above 0, but far below δ = 3.5);
   - trails clearly head-to-head against regular.

   As registered (P2 needs > δ), P2 would be INDETERMINATE at these values.
3. **Both damage-driven shared-state arms dwarf push-pull** (+26 on the pool). The skeleton is the main source of performance; the circular state adds little on average.
4. **P1** (the resonator beats both levels) **would fail on regular** with B knobs; the C knobs come closer (−1.66).

## Notes

- The **owner's recheck** is required before S5 (rule of 2026-10-05). It is launched with at most 2 workers while the 0h run uses the machine.
- **For S5,** the owner should decide what to register:
  - (a) the design as written (P1-P3 on the resonator), honestly expecting P1 to fail and P2 to be indeterminate;
  - (b) adding a registered endpoint for the morale controller's head-to-head result, as a separately labelled claim.

  Option (b) is an outcome-informed addition. It is legitimate only if declared as such and judged on fresh seeds.
