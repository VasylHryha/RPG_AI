# 0008: Approve the C6 proposal

Date: 2026-10-02. Decided by the owner.

## Context

`experiments/c6_proposal.md`, recursive composition R₀ → R₁ → R₂, was drafted by Claude and aligned with the RRG v0.2 locked core. It went through eleven drafter self-audits, an owner-requested development pilot (`evidence/c6_dev_pilot/`, not evidence), and cross-family design review by Codex:
- `docs/reviews/c6_proposal_critique_codex.md` (CHANGES_REQUIRED);
- the re-checks `c6_proposal_recheck_codex.md`, `c6_proposal_followup_audit_codex.md`, `c6_proposal_recheck3_codex.md` and `c6_proposal_recheck4_codex.md`, all CHANGES_REQUIRED, with every finding fixed;
- `c6_proposal_recheck5_codex.md`: **APPROVE**, nothing blocking.

## Decision

- **C6 is APPROVED** as written in `experiments/c6_proposal.md`.
- **D2:** the corrected composition rule (measured isolated rate, sibling-folded capacities, one function at both promotions).
- **D3:** formation PASS on the Wilson 95% lower bound ≥ 0.5 (at least 27 of 40 worlds per level); development target 0.75.
- **D4:** pulses and pushes scored separately against three baselines with channel-matched τ; a development readiness check stops before the panel.
- **D5:** **Codex implements and Claude reviews.** Because Claude also drafted the design, Codex's committed design critique serves as the cross-family design check (proposal §12, stop rule 15).
- **D6:** a C++ engine for the element law, with the compiler identification and flags pinned (G10), the frozen NumPy model as reference, and the `backend_equivalence` gate.
- **D7:** the theory-consistent reading of "same rule", recorded in decision 0007.
- **D8:** bounded prediction also requires an absolute ceiling. The CI upper bound of the mean normalized error, error_model ÷ error_no-transfer, must be ≤ **0.5**, for each excitation type at each transition, with a response floor of 0.01.

## Consequences

- `STATUS.json`: C6 is APPROVED. Nothing is registered yet.
- **Next (implementer, Codex), in the order of proposal §9–§10 and §12:**
  1. the C++ engine and its equivalence checks 1–3;
  2. the development design gate: equivalence check 4 first, then formation in two passes, timescales, interface fidelity, coarse readiness, overlap calibration and the runtime projection;
  3. registration of `experiments/c6_manifest.json` and `milestones/c6.json` on fresh final entropy;
  4. one pipeline run;
  5. the handoff.
- **On any of the 15 stop rules,** the implementer reports to the owner and waits.
- **Before the design gate and before the panel,** the implementer tells the owner how long each will take.
