# 0009: C6 stops at the development design gate; plan a redesign

Date: 2026-10-02. Decided by the owner.

## Context

C6 (recursive composition R₀ → R₁ → R₂) was approved in decision 0008 and amended by A1 and A2, which the owner
re-approved. Implementer Codex built the C++ engine (step 1) and the level-generic modules and design gate
(step 2a); Claude reviewed both. The development design gate ran with entropy 33333 only (`evidence/c6_design_gate/`).

## What the gate found (development data, so no hypothesis verdict)

- **Equivalence check 4 passed:** the C++ engine equals the frozen NumPy model exactly.
- **Formation pass 1:**
  - level 2: 18 of 30 worlds formed;
  - **level 3: 0 of 30** (29 MERGED, 1 DRIFTING).
- **The stop:** with no level-3 group, τ₃ is unmeasurable and C₃ is undefined, so stop rule 2 stopped the gate
  before pass 2 (amendment A1).
- **The mechanism, from the stored validity records:**
  - level-2 groups stay distinct from each other: 7 of 150 overlap > 0.2;
  - the C4 units *inside* them interpenetrate: 167 of 606 overlap > 0.2, in all 30 worlds.
- **The owner-requested diagnostic:**
  - the same 150 groups, rebuilt identically and run **alone** over the level-3 span, keep their units distinct:
    1 of 606 overlap > 0.2, and 0 dynamic failures;
  - 87 groups fail only in contact.
- **Conclusion:** the fusion is caused by contact. In this model, assembling level 3 compresses the lowest level,
  which violates the requirement that lower levels stay internally active (RRG locked §5).

## Decision

- **C6, as registered in the approved proposal, stops at the design gate.**
  - Nothing was registered, and no final seeds were drawn.
  - No panel runs, and no H-C or H-M verdict is claimed.
  - The finding is a development result about this model and this element law. It is not evidence against the RRG
    locked core.
- **STATUS:** C6 is BLOCKED.
- **Redesign:** the drafter writes a redesign proposal for the owner (`experiments/c6_redesign_proposal.md`). It
  must not tune thresholds after seeing these data, and it must keep the procedure-level "same rule" of decision
  0007.

## Consequences

- C4 R003 and C5 R003 stay accepted and unchanged.
- The committed C6 engine, modules and gate stay as the starting point for a redesign, which will register as a new
  revision.
- Any change to the element law needs its own validation at level 1 before it can carry a level-3 claim.
