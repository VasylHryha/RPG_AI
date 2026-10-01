# 0002: C4 R002 supersedes R001 (withdrawn before review)

Date: 2026-10-01. Decided by the implementer (Claude) on the owner's request to recheck the work. Not yet independently reviewed.

## Context

R001 (`evidence/c4_r001/`) passed every implementation gate. Its identical-arm H-M verdict was INCONCLUSIVE because the G→M effect did not vanish under its matched ablation (w = 1 kept 32% of it, concentrated in 2 of 19 worlds). The recheck found that this was a registration error, not a finding:

1. **The G→M ablation was incomplete.** Geometry reaches the phases through two channels: the distance weight w(r) and the choice of neighbours. w = 1 removes only the first. The M→G ablation (J = 0) was complete, so the two tests were asymmetric.
2. **Verdicts on tiny samples.** Causality verdicts were issued on 2 worlds in the heterogeneous arm.
3. **No falsifiable causal test remained.** Once ablations are complete, their vanishing holds by construction. R001 had no prediction that could fail apart from the sign of the intact effect.
4. **Receipt detail.** The receipt held per-world means only.

## Decision

- **R001 is WITHDRAWN** before independent review. Its receipt is preserved unchanged, and its verdicts stand as recorded history.
- **R002 (`geomind-c4-r4-002`) is registered on fresh final seeds**, with these changes:
  - The complete G→M ablation (w = 1 and the phase coupling's neighbour topology frozen at the formed state) is primary.
  - The two single-channel ablations are reported as a decomposition.
  - Dose-response is a registered prediction (G→M over scales 1.25/1.5/2.0; M→G over phase kicks of RMS 0.5/1.0 and uniform). It is part of the H-M rule.
  - Verdicts need at least 10 worlds.
  - The receipt stores per-resonator effects.
- **The gate refuses a second recorded panel for the same code.**

## Guard against post-hoc rescue

- **The dose-response rule** was settled on development worlds only and can fail: it fails if effects decrease with dose.
- **Unchanged from R001:** detector thresholds, model values, formation and effective-state rules.
- **Decomposition and history:** the single-channel w = 1 result, the R001 ablation, is still reported in R002 as a decomposition. R001's INCONCLUSIVE remains on record.
- **Review focus:** the reviewer should judge whether the complete ablation and dose-response make a fair test.
