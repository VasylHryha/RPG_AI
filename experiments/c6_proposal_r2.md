# C6 proposal, revision 2: the loop at a third scale (DRAFT, not approved)

Status: **PROPOSED**. It replaces `experiments/c6_proposal.md` (revision 1, stopped at its design gate: decision
0009). Revision 1 stays as history. Nothing is registered.

## 1. The principle being tested

> **frequency → geometry → frequency → geometry**, and each new turn of the loop happens at a bigger scale. A
> resonator is what a closed loop produces.

- C4 showed the loop at the first scale: elements form resonators.
- C5 showed it once more: C4 resonators form a level-2 resonator.
- **C6 asks one question:** does the same loop, run by the same procedure, turn level-2 resonators into a level-3
  resonator, standing on level-2 resonators that stay alive?

This is the standard's central H-C gate: two successive scale transitions under one procedure, with bounded
predictive error.

## 2. What must be true (each item tied to the principle)

| # | Requirement | Principle or standard | How it is measured |
|---|---|---|---|
| 1 | **The loop closes at level 3**: geometry changes frequency (G→M), and frequency changes geometry (M→G) | the loop itself; locked §3 | C5's two causal tests, one level up: rigid moves of the level-2 parts and rigid phase kicks. Each effect vanishes under its complete ablation (w = 1 with frozen topology; J = 0), with a dose ladder in each direction |
| 2 | **A level-3 resonator forms** | "a resonator is what a closed loop produces" | The same detector as C5 (criteria 1–5: membership, shape, lock, signature, recovery), with time thresholds scaled by the measured factor C₃. Formation PASS needs at least 27 of 40 worlds (D3) |
| 3 | **It stands on live resonators one level down** | each new loop stands on the previous one; locked §5 | Every **direct** part, a level-2 resonator, keeps its own criteria 2–4 on its own time windows and does not overlap another part by more than 0.2 of its area (A3). Deeper levels may reorganize; that is reported, not required |
| 4 | **The same procedure at both transitions** | "same rule" (decision 0007) | One detector, one composition function and one prediction recipe; thresholds scaled only by measured size and time; no level-specific code |
| 5 | **Up and down** | lower levels pass disturbances up; the higher level constrains the lower | A kick to one level-1 unit reaches the other level-2 parts (upward). The level-2 parts' boundaries shift inside the level-3 resonator compared with alone (downward). Each must exceed the 0.01 rad margin |
| 6 | **The new level works as a unit** | "the new loop is a new unit at the bigger scale"; the standard's bounded predictive error | A model that reads only the level-2 summaries predicts the response to held-out pulses and pushes. It must beat no transfer, rigid transfer and relaxation, for each excitation type separately (D4), **and** capture at least half of the actual response, r ≤ 0.5 (D8) |
| 7 | **Both transitions** | two successive turns of the loop | Items 1–6 also at transition 2 (C4 units → level 2), re-measured on fresh worlds in the same run |

**Also reported, with its own verdict:** bigger scales are slower (`scale_separation`, the owner's expectation),
measured as the relaxation time at level n against level n−1, each measured alone.

**Dropped from revision 1:** two things go, because the principle does not need them and the causal tests (item 1)
already rule out a static tree:
- the "real units" specificity test, with its alternative groupings and diffusion diagnostic;
- the requirement that units two levels down stay separate.

## 3. Verdicts

- **H-C, for each transition:**
  - **NOT_SUPPORTED** if the formation Wilson upper bound is < 0.25, or any of items 3, 5 or 6 FAILs.
  - **SUPPORTED_WITHIN_SCOPE** if formation PASSes, H-M (item 1) is supported, and items 3, 5 and 6 PASS.
  - **INCONCLUSIVE** otherwise.
- **H-C overall:** SUPPORTED only if both transitions are SUPPORTED; NOT_SUPPORTED if either is NOT_SUPPORTED.
- **The minimum:** fewer than 10 formed worlds at a level makes every inferential item at that level INCONCLUSIVE.
- **Scope:** CIs are bootstrap 95%, and individual verdicts are nominal.

## 4. How it runs: reuse what is built

- **Reused:**
  - the C++ engine (exact against the frozen NumPy model);
  - the committed `c6_*` modules: contact placement, the measured-rate composition (D2), the detector, E1/E2 and
    scoring, the practice-check tool;
  - the frozen C4/C5 code, read-only.
- **The code change:** criterion 6 on direct parts only (A3); the specificity code is removed from the required
  path.
- **The practice check (development seeds only)**, in this order:
  1. engine equivalence;
  2. formation pass 1;
  3. measure C₂ and C₃, and stop if either is undefined (A1);
  4. formation pass 2;
  5. prediction readiness (stop unless both excitation types beat the baselines with r ≤ 0.5);
  6. runtime projection (stop if more than 3 h).

  On any STOP, the owner decides.
- **Then:** register on fresh seeds, with 40 worlds per level, and run the pipeline once.
- **Runtime estimate:** practice check about 20–60 min; panel about 1 h.

## 5. Roles

Codex implements, Claude reviews the evidence (D5), and the owner approves.

## 6. What C6 cannot show

- *One model:* one element law and staged assembly (each level built, then placed).
- *Fixtures:* the rate offsets are experiment fixtures.
- *Not tested:* no usefulness or efficiency (C8), and no dissolution (C7).
