# 0033: 0g works on big levers measured in 100–200 paired fights; small tooling changes get lighter reviews

**Date:** 2026-10-08. **Decided by:** the owner ("overall I agree with your suggestions", after the owner's own rule on measurement size). **Recorded by:** Claude (claude-opus-5-5).

## Context

- Another Astelia session ran about 8,700 fights to resolve a near-zero difference. The owner: chasing the 3rd or 4th decimal gives no value; use approaches whose effect can be measured after 100–200 fights.
- v7's commit/escape gate adds nothing over always-commit (32/40 against 31/40), and it violates the owner's rule that damaged units rotate and never leave.
- The high-impact mechanisms are the dodge trio, coordinated artillery, and splash-value focus (SHAPE_LAB_SPEC §13). Our side has none of the dodge trio (0 dodges per fight).
- Many review loops on small tooling changes (run cap, process gate) slowed progress on 2026-10-08.

## Decision

1. **Measurement size.** A development comparison is sized to show its effect within **100–200 fights**: about ±10 percentage points of elimination wins, about 2 units saved per fight, or a clear streak difference. A change that shows nothing at that size is dropped or parked, not given more fights. A registered confirmation keeps its own declared size.
2. **Paired fights.** The arms of a comparison play the same battles: the same seeds, maps and enemy tactic draws.
3. **Mechanism first.** Check the mechanism metric first (dodges per fight, own units hit per enemy shell, shells per kill, volley landing spread), within 10–20 fights. Outcome metrics (wins, losses, streak) are read at 100–200 fights.
4. **Sequential looks:** at 50, 100 and 200 paired fights. Stop when the result is clear in either direction. No drop decisions from 4-fight samples.
5. **Bundle small tweaks.** Several small changes are tested together once, as a declared bundle, rather than one by one.
6. **The base controller is always-commit (P16) plus the react primitive.** v7's commit/escape gate is retired as a main arm. The oscillator's job moves to battery synchrony (SHAPE_LAB_SPEC §11, V1).
7. **Development fights run with heavy diagnostics off.** Full recording is kept only for the fights selected for viewing or a declared audit.
8. **The research note is final** at revision 3 (Codex round 3 PASS_WITH_NOTES). Its notes are handled when an evaluator is actually built.
9. **Review weight follows importance.**
   - The owner's verbatim recheck by the other model family (AGENTS.md "Owner recheck") stays mandatory for designs and design revisions, controller or engine changes, development or fixture runs with their reports, and major results.
   - **Small tooling changes** get **one quick check** by a separate reviewer, with no multi-round loop unless a real defect is found. Examples: run caps, process gates, report rendering, file moves, viewer pages.
   - Unchanged: the implementer's tests, path-limited commits, identity checks, and never editing committed evidence.

## Consequences

- The next 0g step: **always-commit + react against always-commit**, on paired drills and series. Dodge counts are checked first; then wins, losses and streak at 100–200 fights.
- Then V1 (firing together), then V2 (volley geometry), each sized the same way.
- The impact ranking (SHAPE_LAB_SPEC §13) uses the same sizing.
