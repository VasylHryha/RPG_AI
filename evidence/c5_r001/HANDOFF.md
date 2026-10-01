# C5 R001: handoff for the independent review

## Identity

| Field | Value |
|---|---|
| Implementer | Claude (claude-opus-5-5) |
| Reviewer | the other model family (Codex): one review, about 15–20 minutes |
| Experiment | `geomind-c5-r4-001`, registered with the code in commit 644a400 |
| Approval | `docs/decisions/0004-approve-c5.md` (proposal `experiments/c5_proposal.md`) |
| `results.json` SHA256 | `b7d6e10372af3663c024e34dc0b0bb5f5f5ea62b62df60e8fab2c32d0ef86796` (quote it in the review) |

**Pipeline:** one run of `tools/verify.py --milestone c5`. Stage times:
- tests: 4.1 s (32 contracts);
- smoke: 31.1 s;
- mutation: 27.1 s (31/31 detected);
- panel: 263.3 s on 30 fresh final worlds, plus 195 fresh C4 harvest worlds.

**Before registration**, the design gate ran on development entropy only (`tools/c5_design_gate.py` and 10 development worlds). It found:
- inter-unit coupling exists;
- units in contact do not interpenetrate;
- τ₁ = 1.5 and τ₂ = 4.94, so T = 3.2.

The manifest lists 15 changes from the approved proposal, each with its reason. The main one: criterion 6 uses port overlap, not the own-neighbour fraction, which measured contact area rather than merging.

## Results (registered rules)

**Implementation gates: all PASS.** Status: **REVIEW_READY**.

**Gate checks:**
- **Numerical checks:**
  - RK4 error ratio 17.3;
  - switching dt error 1.3e-3;
  - equivariance 1.1e-14;
  - unit relabelling 0;
  - decoupled versus alone 2.5e-13.
- **level1_pool:** 150/150 used units are re-detected as accepted C4 resonators. Of 323 accepted C4 resonators from 195 worlds, 223 were in the size range.
- **same_rule_audit:** PASS. The final-world τ₂/τ₁ = 5.44/1.5 = 3.63, within [T/2, 2T].

| Endpoint | Result | Verdict |
|---|---|---|
| Formation (level 2) | 15/30 FORMED (Wilson 95% CI [0.33, 0.67]); exactly at the 0.5 threshold | PASS |
| Formation outcomes | FORMED 15, MERGED 6, DRIFTING 7, APART 0, OTHER 2 | reported |
| Formation vs spread | 0.5δ: 10/30, δ: 15/30, 2δ: 11/30. Not monotone, against the expectation that formation does not increase with spread | reported |
| Decoupled spread control | 25 imposed candidates, 0 accepted (all fail criteria 1, 3, 4, 5) | PASS (gate) |
| Decoupled static control | 25 imposed candidates, 0 accepted (all fail criterion 5; criteria 3–4 pass, as intended) | PASS (gate) |
| G→M (s = 1.25) | +0.0342, CI [0.0186, 0.0520], n = 15; complete ablation exactly 0 | PASS |
| M→G (uniform) | +0.147, CI [0.083, 0.220], n = 15; J = 0 exactly 0 | PASS |
| Dose-response | G→M 0.0125 / 0.0342 / 0.101: PASS. M→G 0.033 / **0.176** / **0.147** (RMS 0.5 / 1.0 / uniform): not monotone, though the highest-minus-lowest CI [0.047, 0.188] > 0, so INCONCLUSIVE | **INCONCLUSIVE** |
| G→M channels | w = 1 only: 74% of intact; frozen topology only: 29% | reported |
| Downward effect (b) | 0.040 rad, CI [0.030, 0.049] > the 0.01 margin; entrainment (a) 0.013 | PASS |
| Emergent transfer | 0.137 rad, CI [0.110, 0.166]; decoupled = 0 | PASS |
| Effective state (level 2) | 15/15 units within the bounds (worst position error 0.16) | PASS |
| Coarse vs full | Gain over no transfer 0.061, CI [0.037, 0.091]; over rigid transfer 0.195, CI [0.167, 0.221]; reopen rate 13%; frequency error 0.001 | PASS |

**Hypotheses (truth table):**
- **H-M (level 2): INCONCLUSIVE** (row 3). It is not supported only because the M→G dose ladder is not monotone: the uniform dose gave a smaller mean effect than RMS 1.0. The same pattern appeared in 2 of 4 groups on development worlds. It was kept as registered, not tuned.
- **H-C first transition: INCONCLUSIVE** (row 4). All four composition endpoints PASS, but row 3 requires H-M SUPPORTED_WITHIN_SCOPE.

## What the reviewer should check

1. **Criterion 6 and the merger rule.**
   - Is port overlap ≤ 0.2 a fair test of "distinct units", and not too lenient?
   - Six worlds were classified MERGED.
2. **The coarse model.**
   - Does it read only `ResonatorState` and ports?
   - Is the 13% reopen rate flattering the scores, given that the error is scored on the trajectory with reopens?
3. **The non-monotone M→G dose.** Is it a property of the dynamics, or a defect in how the uniform dose is built? The uniform dose is a random rigid offset per unit, not zero-mean, while the RMS doses are zero-mean.
4. **Non-vacuity.** Are both controls non-vacuous, and does each reject for the intended reason?
5. **Registered changes.** Do the 15 registered changes from the proposal stay within the approved design?

## Limitations

- **One transition only:** R₀ → R₁. No recursion (C6), dissolution (C7), usefulness or efficiency (C8).
- **Staged assembly with fixture rates:** units are formed separately, and their per-unit rates are set by the experiment.
- **Narrow scope:** one model and one parameter set, M = 5, unit sizes 6–16.
- **The timescale separation is modest** (T ≈ 3.2–3.6).
- **Ablations hold by construction:** complete ablations remove their pathway, so the evidence is the intact effects and the dose ladders.
- **Not novel:** hierarchical synchrony and population reduction are known results.
