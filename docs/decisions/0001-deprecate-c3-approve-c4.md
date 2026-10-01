# 0001: Deprecate C3; approve C4 as the next milestone

Date: 2026-10-01. Decided by the owner, on Claude's recommendation.

## Context

- **What C3 would test.** C3 ("learning stability") tests whether the C2 local learning rule keeps task A after learning task B.
- **Where C2 stands.** C2 R002 is accepted as correct code, but its research decision is STOP_THIS_BRANCH: ordinary linear regression solves the C2 task family exactly at negligible cost (`evidence/c2_r002_independent/RESEARCH_DECISION.md`, `evidence/c2_r002_crosscheck/CROSS_REVIEW.md`). Measuring the stability of a dominated rule could not change that conclusion.
- **C4 is a separate lane.** The R4 standard treats the recursive-resonator lane (C4–C8) as an independent core test of H-C, gated by its own prerequisites (the recursive unit interface), not by C3.

## Decision

- **C3 is DEPRECATED.** No A/B, forgetting or replay experiment will be run on the current C2 rule. It may be revived only after a redesigned C2 (for example a task family that linear models do not solve), under a new proposal.
- **C4 is APPROVED** as proposed in `experiments/c4_proposal.md`.
  - Claude implements and Codex reviews (the other model family).
  - Detector thresholds are settled on development seeds and frozen in `experiments/c4_manifest.json` before any final-seed run.

## Consequences

- `STATUS.json`: C3 DEPRECATED, C4 APPROVED.
- Nothing in C0–C2 changes.
- A C4 failure does not reopen C3, and a C4 success does not rescue C2.
