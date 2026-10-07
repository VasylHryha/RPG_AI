# S5 registration proposal: the v7 resonator controller against the scripted AI (DRAFT for the owner's approval)

**Date:** 2026-10-08, night. **Drafter:** Claude (claude-opus-5-5). **Reviewer:** Codex (cross-family), before the owner sees a final version.
**Status:** **DRAFT. Nothing here authorizes a run.** A registered (judging) run needs:
- this proposal reviewed;
- a sealed specification derived from it;
- **the owner's explicit approval** (AGENTS.md; plan B6).

## 1. Why now

- **The W4 condition for drafting is met** (plan, "Decisions" §1):
  - a development version beats the regular scripted AI under the owner's criterion (DESIGN_0G §19): elimination wins, not survival to the timeout;
  - **v7 (§20.1–20.3):** 32/40 regular elimination wins, mean S +4.68; novice 40/40.
- **The scripted witness P16** (§19.11–19.13) beat regular 34/40 on its own replication.
- **The owner's rule from W4:** the registration reports the strongest simple comparators, **labelled**, and the resonator must not hide them.

## 2. What is being claimed (and what is not)

**The claims (the endpoints in §4):**
1. **The v7 resonator controller, frozen at θ*** (`s4_v7b` tuning ordinal 161), achieves an elimination-win rate **above 50%** against the regular scripted AI, with mean S > 0, on fresh judging seeds.
2. The same against the novice scripted AI.

**Not claimed:**
- that the oscillator gate is necessary, or better than always committing (§20.3: an observed match);
- synchrony as a cause;
- B→R→B recursion;
- generality beyond this fixed world, roster, rules and the two scripted levels.

## 3. The frozen object

| Item | Value |
|---|---|
| The controller | the v7 gate exactly as in `astelia_cpp/s4_v7c` (same sources and native binary hash) |
| θ* | `s4_v7b/TUNING.json`, ordinal 161 (hash-pinned) |
| The world | the fixed S4 world: 50 against 50 (10 melee, 30 ranged, 10 artillery), game rules, `sandboxAbilities = false`, 150 s, dt 1/30 |
| The win definition | enemy 0, own ≥ 1, terminal time < 150 s; a timeout is never a win; the §20.2 overshoot-tick convention |
| Failures | any controller, numerical or native failure is recorded and **counted as a loss** in the primary analysis. It is never dropped |

**The comparators (labelled, frozen, on the same seeds; descriptive, not endpoints):**
- **P16** (scripted witness), at its historical knobs;
- **forcedP16(θ*)** (v7 with the gate forced to commit);
- **morale v3** at its stage-B knobs (the strongest earlier simple controller);
- **v6 at attempt-2 knobs.**

## 4. Endpoints and inference

**The sampling unit:** a **cluster**, one seed with both orientations (swapped sides). Outcomes within a cluster are paired.

| Endpoint | Panel | Support criterion (pre-registered) |
|---|---|---|
| **E1, beats regular** | v7 against regular, n_c clusters × 2 orientations | the cluster-level elimination-win rate > 0.5, **and** mean S > 0 |
| **E2, beats novice** | v7 against novice, n_c clusters × 2 | the same |

- **The test for each endpoint:** a one-sided test that the mean cluster win fraction exceeds 0.5. A cluster's win fraction is its mean over the two orientations. **A cluster bootstrap with 100,000 resamples and a fixed seed;** support requires the lower bound of the one-sided (1 − α) interval > 0.5. Mean S > 0 is tested the same way.
- **α:** familywise 0.01, split equally over E1 and E2 (0.005 each). Within an endpoint, both conditions must hold (an intersection-union test, no further split).
- **The power rule for n_c, declared now:** from the development validation, v7's regular win rate is 0.80 (32/40), with a cluster-level standard deviation estimated from §20.3's 20 clusters. Choose **n_c = 60 clusters (120 fights) per endpoint.**
  - **The power calculation** (a binomial approximation with design effect ≤ 2): to detect a true rate of 0.70 against 0.5 at one-sided α = 0.005, about 50 clusters already give power above 0.95.
  - **60 adds margin.** The development estimate may be optimistic (selection on the tuning panel). The final n_c will be confirmed by the reviewed power computation.
- **Descriptive (no inference):** comparator win rates and S; the paired v7 − forcedP16 and v7 − P16 differences; gate diagnostics.

## 5. Seeds and execution

- **Fresh judging seeds** come from OS entropy into a new **judging** ledger, drawn when the sealed specification is executed. **They are never inspected before the recorded run.** No development ledger is reused.
- **One recorded run** of the sealed panel:
  - v7 + 4 comparators × 2 heads × 60 clusters × 2 orientations = **1,200 fights**;
  - about 5–10 min of fights at the measured rates, plus analysis;
  - the analysis must have its own allowance. The 7.7 GB full-diagnostic traces of v7c took about 110 min to analyze, so the registered run keeps diagnostics minimal for the endpoints, plus a declared diagnostic subset.
- **The process:** the mandatory process gate; caffeinate; no code edits during the run; one attempt. **Any ambiguity or failure stops the run, and a new registration requires fresh seeds.**

## 6. Stop rows

| Yes/no | Action | Role |
|---|---|---|
| Has the owner approved the sealed specification? | If no: no judging run | owner |
| Does the sealed specification's binary, θ* or world differ from §3? | INVALID; no run | implementer |
| Is any judging seed inspected or used before the recorded run? | INVALID; new ledger, new registration | implementer |
| Does the run fail or stop ambiguously? | Report PARTIAL; no rerun on the same seeds | implementer |
| Does E1 or E2 fail its support criterion? | Report REFUTED or NOT_SUPPORTED as registered; no re-analysis to change it | drafter |

## 7. Open questions for the reviewer and the owner

1. Is morale v3 (rather than morale at v6-era knobs) the right "strongest simple comparator"?
2. Should E3, "v7 against forcedP16" (the gate's contribution), be a registered equivalence or superiority endpoint, or stay descriptive (proposed: descriptive, since development showed a match)?
3. Is 60 clusters per endpoint acceptable, or should the reviewed power rule decide n_c only from a separate development split, as the earlier S5 design required?
4. Should the novice endpoint stay, given that P16 and v7 both win 40/40? It is easy, but it guards against a regression.
