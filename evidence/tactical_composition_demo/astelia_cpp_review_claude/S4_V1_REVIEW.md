APPROVE_WITH_NOTES (development record; the STOP stands; design defect identified)

Reviewer family: Claude (claude-opus-5-5)
Reviewed: the S4 v1 development (merged at `f54e0cb` from Codex's bundle: implementation `dca84c7`, evidence `68be0d0`, delivery `f0dcde6`), report `astelia_cpp/S4_V1_DEVELOPMENT_REPORT.md`
Date: 2026-10-05

## Verdict and process

- **The STOP at stage B is correct:** the resonator's novice validation mean is −0.110 [−1.69, 1.47].
- **Process:**
  - v0 parity was preserved (164/164 fixtures byte-identical);
  - fresh seeds;
  - equal CMA-ES budgets;
  - all four arms validated.
- **The committed-code concern from the recheck is resolved:**
  - the run used an isolated checkout pinned at `90d6f29` with its own commits;
  - the sandbox could not write this repository's `.git`, so they were delivered as a verified bundle;
  - I merged them unchanged, after checking that the working-tree copies were byte-identical to the branch tip.

## Results (validation)

| Setting | Resonator v1 | Morale | Push-pull | Nearest |
|---|---|---|---|---|
| A: melee vs novice | **+5.05** [4.76, 5.33] (v0 +2.77) | +4.82 | +1.63 | +0.60 |
| B: full vs novice | −0.11 (v0 +5.92) | +1.10 | −2.20 | −17.53 |
| B: full vs regular | −9.56 (v0 −8.69) | −2.17 | −1.15 | −24.04 |
| Enemy guns alive vs regular | 8.01 of 10 | 9.79 | 9.98 | 10.00 |

- **In melee the resonator is ahead of morale for the first time** (+5.05 against +4.82). It is development data and a small gap, but the first sign in that direction.
- **The retreat trap is not fixed:** guns survive in every arm, and most regular fights time out.

## Root cause (a design defect, not tuning noise)

1. **The preferred distance may exceed the unit's own reach.** The knob f has bounds [0.3, 1.2], and the tuned resonator B knobs are f = 1.11 and w = 2.97. A committed unit stands at 1.11 × its range, and a pulling-back one at up to about 4.4×.
   - Against novice's melee this is useful (kiting).
   - Against guns that out-range us (320 against our shooters' reach of about 278 px centre to centre), no commitment level brings a unit into firing distance.
2. **The v1 "unanswered" label is too coarse.** A unit counts as answered whenever *any* enemy is in its reach, even while a gun it cannot reach is hitting it. In full battles that is almost always the case, so the v1 drive rarely fires.
3. **Movement ignores threats beyond the 8 nearest enemies**, so guns behind a line never attract committed units.

## Recommendation

Design revision 5 (v2, `DESIGN_0G.md` section 13): a range-aware preferred distance, a threat-precise "unanswered" label and threat-weighted movement, all from observed ranges. It is an outcome-informed change, so it is logged, and v2 is tuned on fresh seeds with the full budget restarted (section 10 stop row).
