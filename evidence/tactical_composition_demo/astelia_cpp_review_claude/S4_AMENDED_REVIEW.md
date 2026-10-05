APPROVE_WITH_NOTES (development; READY_FOR_S5 accepted as the owner-directed label)

Reviewer family: Claude (claude-opus-5-5)
Reviewed: the amended S4 run (`S4_AMENDED_PROTOCOL.md`, frozen at `8c89561`), the report `astelia_cpp/s4_amended_development/S4_DEVELOPMENT_REPORT_AMENDED.md`, and the owner gate decision `s4_checks/AMENDED_GATE_OWNER_DECISION.json`
Date: 2026-10-05

## Verdict

A fair development run.
- CMA-ES (pycma 4.5.0, population 16, 16 generations), with equal budgets of 9,766 evaluations per arm per stage on shared clusters.
- Validation on separate seeds, with about 100 clusters per head-to-head cell.
- The A/B-only stop gates were asked and answered as a clarification. They match my amended request ("in stage A **or** stage B"), so they are not an outcome-informed change of rule.
- The C-stage head results are reported, as the owner required.

## Results (validation; S = survivors − enemy survivors; 95% intervals)

| Setting | Resonator | Morale | Push-pull | Nearest |
|---|---|---|---|---|
| A: 10v10 melee vs novice | +2.77 [2.37, 3.16] | **+4.53** [4.36, 4.69] | +1.41 | +1.36 |
| B knobs: full vs novice | **+5.92** [5.07, 6.77] | −7.62 | −2.41 | −16.62 |
| B knobs: full vs regular | −8.69 [−8.82, −8.55] | **+3.10** [1.87, 4.33] | −0.98 | −23.81 |
| C knobs: 19-doctrine pool | +2.24 | **+3.33** | −5.08 | −19.93 |
| C knobs: full vs novice | −6.57 | −11.07 | −4.76 | −17.26 |

| Paired on the pool (C knobs) | Block mean | 95% interval |
|---|---:|---|
| resonator − morale (P2) | **−1.09** | [−1.69, −0.50] |
| resonator − push-pull (P3) | **+7.32** | [6.91, 7.73] |

## Readings (development only)

1. **First "beat the code" result:** with B knobs the resonator beats the scripted novice head-to-head with full armies (+5.9).
2. **Each arm specialized.** The B objective averaged novice and regular equally. The resonator found a novice-beating optimum that loses to regular, and morale the reverse. With one knob set,
   **no arm beats both novice and regular**, which is what P1 requires (intersection-union, design section 6). If registered as designed, P1 is expected to fail on regular.
3. **The beat against a plain number:** on the pool, morale is slightly ahead (−1.1, interval excludes 0). The development evidence does **not** favour the circular beat.
4. **Damage-driven shared state against plain forces:** strongly positive (+7.3), robust across both runs.

## Notes for S5

1. **The knob source per endpoint must be frozen before judging seeds exist:** P1 from `B_best.json`, P2/P3 from `C_best.json`. The registered claim is then "the AI as tuned for that panel".
2. **Keep P1 as designed (both levels).** Do not narrow it to novice after seeing regular's development result. Report the novice and regular subtests separately as diagnostics.
3. **The resonator's regular SD is suspiciously small** (0.70 over 100 clusters at −8.69). Check a replay for a degenerate repeated pattern (for example a stalemate or timeout) before registering.
4. δ = 4.0 (Codex's rule applied to amended validation) and n (P1 49 per level, P2/P3 16 per doctrine) need owner approval. The inference unit is the shared seed block for P2/P3,
   as computed.
