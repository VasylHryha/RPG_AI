# 0004: Approve the C5 proposal

Date: 2026-10-01. Decided by the owner.

## Context

`experiments/c5_proposal.md` was drafted by Claude and self-audited against the R4 standard's C5 section, the recursive-resonator invariants and the C4 lessons (commits c5fa19d, 25835ba). The owner's rule: if the proposal fits the standard and the requirements, it is approved. It fits. The two points the standard does not settle were put to the owner directly.

## Decision

- **C5 is APPROVED** as written in `experiments/c5_proposal.md`.
- **Time normalization (D2):** the measured relaxation-time ratio T = τ₂/τ₁ (owner's answer). It replaces the standard's collective period, which is undefined at Ω = 0.
- **Formation failure (D3):** if the Wilson 95% upper bound of level-2 formation is below 0.25, the first H-C transition is NOT_SUPPORTED (owner's answer). H-M at level 2 stays INCONCLUSIVE in that case.
- **Fixed numbers (D4):** as proposed. Formation PASS at ≥ 0.5 of 30 final worlds; M = 5 units; unit sizes 6–16; q ≈ 0.75, settled on development worlds; a 0.01 rad margin.
- **Roles (D5):** Claude implements and Codex reviews (the other model family), as for C4.

## Consequences

- `STATUS.json`: C5 is APPROVED.
- **Next:** the development-world design gate (does coupling between units exist, and does a run fit the time budget). Then register `experiments/c5_manifest.json` and `milestones/c5.json` on fresh final entropy, before any final-seed run.
- If the design gate fails, the implementer returns to the owner. The model is not changed to make composition happen.
