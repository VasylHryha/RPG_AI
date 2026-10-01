# C5 R002: handoff for the independent review

## Identity

| Field | Value |
|---|---|
| Implementer | Claude (claude-opus-5-5) |
| Reviewer | the other model family (Codex): one review, about 15–20 minutes |
| Experiment | `geomind-c5-r4-002`, registered with the code in commit b5dbc68 |
| Supersedes | R001 (`evidence/c5_r001/`), withdrawn before review; decision `docs/decisions/0005-c5-r002-supersedes-r001.md` |
| Approval | `docs/decisions/0004-approve-c5.md` (proposal `experiments/c5_proposal.md`) |
| `results.json` SHA256 | `a2c4f52fdd2c86696b81659beeea84729cb7084cbe243a11bb3d47322d840407` (quote it in the review) |

**Pipeline:** one run of `tools/verify.py --milestone c5`. Stage times:
- tests: 9.3 s (37 contracts);
- smoke: 60.4 s;
- mutation: 36.1 s (41/41 detected);
- panel: 247.8 s on 30 fresh final worlds, plus 195 fresh C4 harvest worlds.

## Results (registered rules)

**Implementation gates: all PASS.** Status: **REVIEW_READY**.

**Gate checks:**
- numerical checks PASS;
- level1_pool: 150/150 units re-detected;
- same_rule_audit PASS (final τ₂/τ₁ = 3.63, within [T/2, 2T]);
- both controls non-vacuous: 24 imposed candidates each, 0 accepted.

| Endpoint | Result | Verdict |
|---|---|---|
| Formation (level 2) | 13/30 FORMED (Wilson [0.27, 0.61]); below the registered 0.5 | **FAIL** |
| Formation outcomes | FORMED 13, MERGED 8, DRIFTING 9 | reported |
| Formation vs spread | 0.5δ: 12, δ: 13, 2δ: 12 (flat) | reported |
| C4 view | the frozen C4 component rule sees 13/13 accepted groups as one component | reported |
| G→M (s = 1.25) | +0.0248, CI [0.0155, 0.0346], n = 13; complete ablation exactly 0 | PASS |
| M→G (RMS 1.0) | +0.209, CI [0.155, 0.265], n = 13; J = 0 exactly 0 | PASS |
| Dose-response | G→M 0.0065 / 0.0248 / 0.081; M→G 0.038 / 0.209 / 0.879; both rise with dose | PASS |
| G→M channels | w = 1 only: 64% of intact; frozen topology only: 39% | reported |
| Downward effect (b) | 0.028 rad, CI [0.019, 0.037] > the 0.01 margin; entrainment 0.013 | PASS |
| Emergent transfer | 0.152 rad, CI [0.130, 0.176] | PASS |
| Effective state | 13/13 within bounds | PASS |
| Coarse vs full (open-loop) | Gain over no transfer +0.061, CI [0.044, 0.077]; over rigid transfer +0.175, CI [0.147, 0.201]; **over relaxation −0.004, CI [−0.021, 0.011]** | **INCONCLUSIVE** |
| Coarse, descriptive | open-loop error 0.143; reopened-protocol error 0.156; 2/26 excitations flagged invalid; frequency error 0.0006 | reported |
| Timescale separation | τ₂/τ₁ = 3.21, CI [2.75, 3.66]; 0/13 τ₂ censored | PASS |

**Hypotheses (truth table):**
- **H-M (level 2): INCONCLUSIVE** (row 3: formation FAIL). Both directions, both complete ablations and both dose ladders pass on the 13 formed worlds. Formation failure is not evidence about coupling.
- **H-C first transition: INCONCLUSIVE** (row 4). Downward effect, emergent transfer, effective state and timescale separation pass. The coarse port law does not beat a one-parameter relaxation baseline that uses the group's measured τ₂.

## What R002 shows, in plain terms

- **When level-2 groups form, they behave like real two-level structures.**
  - Units stay distinct.
  - Units relax about 3× more slowly between themselves than within.
  - Geometry and phase drive each other at the unit scale, with clean dose-response.
  - The group shifts its parts' boundaries and passes pulses between units.
- **They form in only about 43% of worlds** (R001: 50%), below the registered 0.5.
- **The zero-parameter port-level coarse model is no better than simple relaxation with a measured time.** The port mechanics add no predictive value at this level.

## What the reviewer should check

1. Whether the R001 withdrawal (decision 0005) is a design fix and not a post-hoc rescue. All settings are unchanged, and the changes make passing harder.
2. Whether the relaxation baseline is fair. It uses the same group's τ₂, measured from the intact G→M control.
3. Criterion 6 (port overlap ≤ 0.2) and the MERGED classification (8 worlds).
4. Whether the coarse model reads only `ResonatorState` and ports, and whether the scored prediction is truly open-loop.
5. Non-vacuity, and whether each control rejects for the intended reason.

## Limitations

- **One transition only:** R₀ → R₁, with staged assembly and per-unit rates set as a fixture.
- **Narrow scope:** one model and one parameter set, M = 5, unit sizes 6–16.
- **The C4 view:** the frozen C4 component rule sees each group as one component. The level-2 claim rests on criterion 6 and timescale separation.
- **Ablations hold by construction:** complete ablations remove their pathway, so the evidence is the intact effects and the dose ladders.
- **Not novel:** hierarchical synchrony and population reduction are known results.
