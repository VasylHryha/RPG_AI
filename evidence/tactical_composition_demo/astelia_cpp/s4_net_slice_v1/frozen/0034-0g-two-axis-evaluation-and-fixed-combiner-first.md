# 0034: 0g scores every shape on two axes; the decision numbers are deaths, kills per death and the streak; a fixed combiner comes first

**Date:** 2026-10-08. **Decided by:** the owner ("ok, it's up to you, I assume", approving Claude's suggestions after proposing the survival and damage categories). **Recorded by:** Claude (claude-opus-5-5).
**Extends:** decision 0033 and SHAPE_LAB_SPEC §15 (Amendment 8: survival and damage categories). Neither is edited, because shape lab v5 pins both files during its run.

## Decision

1. **Two axes for every shape.** Each shape is measured on **both** axes, survival and damage, whatever its category. The category only names its main effect. Reports place each shape on one chart: own deaths saved per fight against enemy damage or kills gained. A shape that buys damage with deaths, or survival with lost damage, is visible at once.
2. **The decision numbers** for development comparisons, paired, at decision-0033 sizing:
   - **own deaths per fight;**
   - **enemy kills per own death,** the exchange rate that combines the two axes;
   - **the ten-fight series streak,** primary when a series is run.
   - **Single-fight win rate is reported, not decided on.** It is near saturation: 46/50 with dodge.
3. **Category-matched test panels first.**
   - Survival shapes are tested first against artillery-heavy and rushing tactics (e.g., storm, line anvil, regular).
   - Damage shapes are tested first against evasive tactics (loose, loose skirmish, wolfpack).
   - The full 20-tactic C3 and the series follow for any shape that passes.
4. **Survival first.** When two candidates compete for the next slot, the survival shape goes first: survivors heal and carry over, so saved units compound across the series.
5. **All paired fights.** Deaths and kills are reported over all paired fights, not only won ones, plus the won/lost split. This avoids the survivorship bias of "deaths in won fights".
6. **A fixed combiner before an RRG combiner.** The first unit-level combiner of survival and damage is a scripted fixed rule, e.g. "if a lethal hit is predicted, dodge or rotate behind friends while staying in reach; otherwise attack". A resonance or synchrony combiner (RRG mechanism) is tested later against it on the same fights, as the V1 test does for volleys (SHAPE_LAB_SPEC §14).

## Consequences

- The V1 volley test (running) is reported as a **damage** shape: kills per minute, shells per kill, enemy dodge success, plus the survival guard (own deaths), for the scripted sync and the RRG oscillator.
- **The next build** is the ranged engagement floor. It is a damage shape, with its survival guard. Then predicted-lethal rotation, a survival shape inside the never-leave rule.
- **Future lab builds** pin a frozen copy or commit id of the spec and decisions, never the living files (lesson from the v5 drift stop).
