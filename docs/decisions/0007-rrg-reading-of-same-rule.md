# 0007: How "same rule across scales" is read, in line with the RRG locked core

Date: 2026-10-02. Decided by the owner (C6 proposal decision D7, accepted). Recorded by the drafter, Claude.

## Context

R4 recursive-resonator invariant 1 says that the interface, coupling law, connection rule and composition law are the same at every scale, normalized by measured scale. Read literally, it can imply that the *same element law* must also predict the next level. The theory the project tests says otherwise:
- *The source:* RRG v0.2 locked core, `RPG_theory/research/RRG_CURRENT/00_LOCKED_CORE.md`, SHA-256 `b6d3e7c75285889afe94cabf083ba5fb80f401c656613ba6a80d2f0149b655e1`.
- *§7:* different scales may have different effective mechanisms and equations.
- *Doc 03 §13 and the proof matrix:* same-equation closure is an optional, stronger extension.
- *Doc 02 §5:* slower dynamics at higher levels is a hypothesis to measure, not part of what a scale is.

## Decision

1. **"Same rule across scales" means the same procedure at every level:**
   - one detector;
   - one promotion function;
   - one composition function;
   - one effective-model recipe;
   - thresholds scaled only by measured size and time.

   One physics runs in the full simulation everywhere. No level-specific solver, threshold or hand-authored grouping is allowed; that guard is unchanged.
2. **A higher level's effective dynamics may differ from the element law** (locked §7). That the same law predicts the next level is reported as an optional extension with its own verdict ("same-law closure"). It is never required for H-C.
3. **Scale separation** (higher levels are slower) is tested as a registered prediction with its own verdict. It is never required for something to count as a scale.
4. **Geometry is part of a unit** (locked R = (G, M)). Tests of whether a level is a real unit must not subtract geometry-supported structure.

## Consequences

- The R4 standard's C6 section carries a one-paragraph pointer to this record. No other normative text changes.
- `experiments/c6_proposal.md` (approved in decision 0008) implements this reading.
- Earlier milestones are unaffected: C4 and C5 used one physics and one detector procedure, which this reading preserves.
