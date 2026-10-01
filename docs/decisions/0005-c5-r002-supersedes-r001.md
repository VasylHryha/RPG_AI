# 0005: C5 R002 supersedes R001 (withdrawn before review)

Date: 2026-10-01. Decided by the implementer (Claude) on the owner's request to recheck the work and fix every issue. Not yet independently reviewed.

## Context

R001 (`evidence/c5_r001/`) passed every implementation gate. Both hypotheses were INCONCLUSIVE, decided by a single endpoint: the M→G dose ladder was not monotone (uniform 0.147 < RMS 1.0 0.176). The recheck found that this was a design defect, not a finding, and found further gaps.

1. **The top M→G dose was not a larger dose (high).**
   - *The construction:* "uniform" gave each unit an independent random offset, while the other doses were zero-mean kicks of fixed RMS.
   - *Why it is not larger:* the dynamics see only the wrapped pairwise differences between units. For a 3-unit group, the uniform dose has the same mean effective size as RMS 1.0 (1.73 rad), with sd 0.56.
   - *Consequence:* the ladder could not test dose-response. C4's uniform dose replaced the phases of about 12 elements, so its size was nearly constant; at the unit level, with 3–5 units, it is not.
   - *How it was checked:* with random numbers only, not panel data.
2. **The coarse score included truth injection (high).** The scored coarse prediction was the reopening protocol, which replaces the coarse state with the full model's state when the coarse state goes invalid (13% of R001's excitations). That flatters the error.
3. **The cheap baselines were weak (medium–high).** "Rigid transfer" is a strawman. No baseline used the group's measured relaxation time, the obvious cheap predictor of how a pulse spreads.
4. **Merger versus hierarchy was tested only geometrically (medium).**
   - Criterion 6 tests that units do not interpenetrate.
   - The dynamical signature of a hierarchy is slower relaxation between units than within them (τ₂ > τ₁). It was reported, but it was not a registered endpoint.
   - The frozen C4 component rule sees a formed group as one component. R001 did not disclose this.
5. **τ₂ censoring (low–medium).** τ₂ values that never reached 1/e inside the window were dropped silently.
6. **Coverage (medium).** The statistic code (dose construction, the downward comparison, baselines) had weak contract and mutant coverage. There was also dead code.

## Decision

- **R001 is WITHDRAWN** before independent review. Its receipt is preserved unchanged, and its verdicts stand as recorded history.
- **R002 (`geomind-c5-r4-002`) is registered on fresh final entropy** with these changes:
  - M→G doses are zero-mean unit kicks of fixed RMS 0.5/1.0/1.5, with primary 1.0. A non-RMS dose is refused.
  - The scored coarse prediction is open-loop. Reopening is run alongside and reported, along with the number of invalid flags on the open-loop run.
  - There is a third baseline: relaxation to an equal share of the excitation, using the group's own measured τ₂. The coarse law must beat all three baselines.
  - `timescale_separation` (τ₂/τ₁ > 1, censoring counted) is an H-C endpoint. The H-C truth table now has five composition endpoints.
  - The receipt discloses how many accepted groups the C4 component rule sees as one component.
  - There are 37 contracts and 41 mutants, all detected locally. The dead code is removed.

## Guard against post-hoc rescue

- **Settings unchanged from R001:** placement radius, rate spread, T, port overlap, thresholds, number of worlds, formation rule and every other setting. Nothing was tuned on R001's final worlds.
- **The changes make R002 harder to pass, not easier.**
  - There is a stronger baseline.
  - There is no truth injection in the scored prediction.
  - There is one more H-C endpoint that can fail.
  - On one development group, the coarse law beat the new relaxation baseline by only 0.006.
- **The dose fix rests on a stated principle:** one controlled size family. The principle was checked with random numbers, not panel data. The reviewer should judge whether it is fair.
