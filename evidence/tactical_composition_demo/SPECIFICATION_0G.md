# Specification 0g (S5 registration DRAFT): the resonator AI against Astelia's scripted AI

**Status: DRAFT.** Before any judging fight, two things are needed:
- **the owner's approval** of δ = 4.0 survivors and the panel sizes;
- **a Codex review** with the verdict APPROVE or APPROVE_WITH_NOTES.

The machine-readable contract is `SPEC_0G.json`; where the two differ, that file governs. The design is `DESIGN_0G.md` revision 3, whose hash is in the JSON. This is
exploratory, under decision 0028, and changes no milestone status.

## What is tested

1. **P1, beat the code:** does our AI, built on the C4 element law driven by damage, beat the game's scripted novice **and** regular levels head-to-head with full armies?
2. **P2, does the beat matter:** does it beat plain morale, the same controller with a number instead of a circular phase?
3. **P3, beyond known swarm forces:** does it beat the specified push-pull baseline?

## How

- **Engine:** the typed C++ simulator at binary sha256 `a1a2d528…552c74a`, the build used in S4. The runner refuses any other binary.
- **Fixed world:** design section 1.
- **Knobs, frozen from the amended S4 run:**
  - P1 uses each arm's stage-B knobs (tuned on full-army head-to-head play against novice and regular);
  - P2 and P3 use the stage-C knobs (tuned on the 19-doctrine pool).

  The values are copied into `SPEC_0G.json`, so the claim is about the AI as tuned for each panel.
- **P1 panel:** for each level, 100 clusters. A cluster is one seed played in both orientations, and the cluster value is the mean S of the two.
  - The statistic is the mean cluster S, with one-sided t bounds (df 99).
  - **SUPPORTED** if the 99.75% lower bound is above 0 for **both** levels.
  - **REFUTED** if for **either** level the 99.958% upper bound is below 0.
  - **INDETERMINATE** otherwise.
- **P2 and P3 panel:**
  - 32 seed blocks. A block is one seed for all 19 doctrines × 2 orientations, with the opponents' skills = elite skills without rollout or look-ahead.
  - Arms are paired by (doctrine, seed, orientation). The block value is the mean paired difference over its 38 fights. The statistic uses one-sided t bounds (df 31).
  - **SUPPORTED** if the 99.75% lower bound is above δ = 4.0.
  - **REFUTED** if the 99.917% upper bound is below 0.
  - **INDETERMINATE** otherwise.
- **Alpha:** familywise 0.01. Each endpoint gets 0.01/3, split into 0.0025 for support and 0.000833 for refutation. P1's two refutation subtests share theirs.
- **Score:** S = survivors − enemy survivors. A timeout is an ordinary fight. D (damage difference) is descriptive only and never breaks a tie.
- **Failures:** any controller failure in an endpoint's fights makes that endpoint INDETERMINATE (reason `controller_failure`). No fight is dropped or replaced.
- **Seeds:**
  - derived from a 128-bit judging root drawn at drafting and committed with this specification;
  - never used before the recorded run;
  - a new root is required if this draft changes after any fight that uses it.
- **Size:** about 6,000 fights, including the descriptive arms, a few minutes on 10 cores.

## Disclosed development expectations (S4 amended validation; not evidence for the verdicts)

| Endpoint | Development reading | Expectation |
|---|---|---|
| P1 | resonator (B knobs): novice +5.92, regular −8.69 | expected to fail on regular |
| P2 | resonator − morale: −1.09 [−1.69, −0.50] | not expected to be supported |
| P3 | resonator − push-pull: +7.32 [6.91, 7.73] | expected near or above δ |

We register them anyway, as designed. Narrowing P1 to novice, or dropping P2, after seeing development data would be an outcome-informed change.

## Owner decisions needed (yes/no)

| Question | If yes | If no |
|---|---|---|
| Approve δ = 4.0 survivors? | keep | the owner names δ; the specification is revised before any fight |
| Approve 100 clusters per level (P1) and 32 seed blocks (P2/P3)? These are raised from the power-rule floors (49 and 16) because fights are cheap | keep | use the floors |
| After the Codex review, approve running S6 once with exactly this specification? | the run proceeds | stop |

## What is not claimed

- a C5 hierarchy;
- that a sustained oscillation, as opposed to a circular state, is necessary;
- novelty over swarmalators or physicomimetics in general;
- results against elite (planners that simulate our controller);
- anything beyond this game, these panels and these knobs.
