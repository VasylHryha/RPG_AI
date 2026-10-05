NOT_READY

# S4 v3 contract-stop report

Implementer family: Codex (GPT-6). Authority read: AGENTS.md, decision 0028 items 16–18, DESIGN_0G.md sections 13–14, S4_AMENDED_PROTOCOL.md and S4_V2_PROTOCOL.md. The owner explicitly requires a written question and a stop if section 14 is ambiguous.

## Q1: artillery exception in the first section-14 check

Section 14 requires commit distance `f_c R_i`, with the explicit artillery override `max(f_c R_i, 1.05 Rmin(i))`. Its first check also forbids any preferred distance strictly between `f_c R_i` and `R_e` in the out-ranged case. These requirements conflict when the artillery minimum-range override binds.

The existing constructed range fixture in `native_s3_contract.cpp` uses own artillery range 250 px, minimum range 80 px, enemy artillery range 400 px and allowed `f_c = 0.3`. Thus `R_i = 250 px`, `R_e = 400 px`, `f_c R_i = 75 px`, and the specified commit distance is `max(75, 84) = 84 px`. That distance is strictly between 75 and 400 px, failing the literal check while satisfying the commit formula. This counterexample is static arithmetic from the existing fixture; no project code was executed.

**Question to the drafter:** should the first check forbid distances strictly between the *effective committed distance* and `R_e`, using `max(f_c R_i, 1.05 Rmin(i))` as the lower bound for own artillery and `f_c R_i` for other roles? This would preserve the specified artillery formula. Please clarify the check in section 14 before implementation resumes.

## Execution status

Stopped before implementation under the owner's ambiguity instruction. No v3 skeleton, rebuild, tests, Part 1 implementation commit, development fight, seed allocation, registration or recorded run exists from this task. V0/v1/v2 code and fixtures are untouched. `s4_v3_development/` was confirmed absent and remains uncreated.

The requested 360-minute total runtime allowance (raised from 180 because v2 stage C hit the projection cap) is acknowledged as a protocol resource change authorized before any v3 fight. No time is charged to development execution. A specific duration estimate and a fresh development-only seed declaration will precede any future run after the contract is clarified. The amended population, generations, per-arm budgets, A/B/C settings, validation sizes and A/B novice gates have not been changed.

All A/B/C tuning, validation, timeout and enemy-gun diagnostics, replay exports, and fresh P2/P3 spread/margin/sample-size planning are **not_run: section-14 contract stop**. This is neither a performance STOP nor development readiness.
