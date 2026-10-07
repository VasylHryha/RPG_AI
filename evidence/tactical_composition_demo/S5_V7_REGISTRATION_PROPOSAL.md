# S5 registration proposal, revision 2: the v7 resonator controller against the scripted AI (DRAFT for the owner's approval)

**Date:** 2026-10-08, night. **Drafter:** Claude (claude-opus-5-5). **Reviewer:** Codex (cross-family), before the owner sees a final version.
**Revision 2** answers `docs/reviews/tactical_0g_s5_v7_proposal_review_codex.md` (CHANGES_REQUIRED, findings 1–7). The self-audit is in §8.
**Status:** **DRAFT. Nothing here authorizes a run.** A registered (judging) run needs:
- this proposal reviewed;
- a sealed specification derived from it;
- **the owner's explicit approval** (AGENTS.md; plan B6).

## 1. Why now

- **The W4 condition for drafting is met** (plan, "Decisions" §1):
  - a development version beats the regular scripted AI under the owner's criterion (DESIGN_0G §19): elimination wins, not survival to the timeout;
  - **v7 (§20.1–20.3):** 32/40 regular elimination wins, mean S +4.68; novice 40/40. The Codex recheck (`docs/reviews/tactical_0g_v7_validation_recheck_codex.md`) verified it, with wording corrections in DESIGN_0G §20.3.1.
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
- generality beyond this fixed world, roster, rules and the two scripted levels;
- hierarchy or source qualification;
- causal superiority over any labelled comparator.

## 3. The frozen object

| Item | Value |
|---|---|
| The controller | the v7 gate exactly as in `astelia_cpp/s4_v7c`: binary `s4_v7c/build/astelia_native_v7`, SHA256 `9e8781b7…dc2dd`, build manifest `f2e1c916…2b790` |
| θ* | `s4_v7c/THETA_ORIGIN.json`: tuning commit `796d0a8`, ordinal 161, TUNING.json SHA256 `6b146edc…96e65` |
| The world | the fixed S4 world: 50 against 50 (10 melee, 30 ranged, 10 artillery), game rules, `sandboxAbilities = false`, 150 s, dt 1/30 |
| The win definition | enemy 0, own ≥ 1, terminal time < 150 s; a timeout is never a win; the §20.2 overshoot-tick convention |
| Failures | see §5.3 (an attributable failure is coded as a worst-case loss; an infrastructure or integrity failure stops the run as PARTIAL or INVALID) |

**The comparators (labelled, frozen, on the same seeds; descriptive, not endpoints):**
- **P16** (scripted witness), at its historical knobs;
- **forcedP16(θ*)** (v7 with the gate forced to commit);
- **morale v3** at its stage-B knobs (the strongest earlier simple controller);
- **v6 at attempt-2 knobs.**

## 4. Endpoints and inference (revision 2)

**The sampling unit** is a **cluster**: one judging seed, played in both orientations. Clusters are i.i.d. draws from the seed distribution. The two outcomes within a cluster are averaged:
- the cluster win fraction w_c ∈ {0, ½, 1};
- the cluster mean score S_c ∈ [−50, 50].

| Endpoint | Panel | Support (pre-registered, per head) |
|---|---|---|
| **E1, beats regular** | v7 against regular, n_c clusters × 2 orientations | LB_w > 0.5 **and** LB_S > 0 |
| **E2, beats novice** | v7 against novice, n_c clusters × 2 | the same; **a compatibility check, not a no-regression test** |

**The test (finding 2): a distribution-free lower confidence bound for a bounded mean.**
- **The method:** the hedged-capital betting confidence bound for the mean of i.i.d. observations bounded in [0, 1] (Waudby-Smith and Ramdas 2024, JRSS-B).
  - It is applied to w_c directly, and to S_c rescaled to [0, 1] by (S_c + 50)/100.
  - **One-sided level 1 − 0.005 per component.** It is valid for any distribution on the bounded range, including skew, rare losses and the all-win boundary.
- **The implementation is pinned in the sealed specification:**
  - the exact algorithm and parameters;
  - the predictable bet sequence;
  - a fixed processing order of the clusters by schedule key, not by outcome;
  - strict comparisons;
  - the behaviour on degenerate data (the bound stays valid; no fallback).
- **The intersection-union rule:** both components must pass; no further split.
- **Multiplicity:** Bonferroni over E1 and E2, familywise 0.01. Each endpoint is reported separately; **neither verdict depends on the other.**
- **Mean S as a conjunct** comes from the owner's own criterion (§19: "an elimination-win rate > 50% plus S > 0"). **The owner is asked to confirm** this in the approval.

**Verdicts (finding 4), exhaustive per endpoint:**
- **SUPPORTED:** both lower bounds pass, on a complete valid panel.
- **NOT_SUPPORTED:** a complete valid panel on which either bound fails. **This is not a refutation; no REFUTED verdict exists.**
- **PARTIAL:** an infrastructure stop. Endpoint coverage lists the evaluated and unevaluated cells, with reasons.
- **INVALID:** an identity, integrity or seed-hygiene breach.

**Sizing (findings 1 and 5): a conservative fixed alternative, not the 80% development estimate.**
- **The planning alternative:**
  - the regular cluster win fraction is drawn from a distribution with mean **0.70**: the development cluster distribution shrunk toward 0.5 by a declared linear contraction;
  - S_c is drawn from the development cluster S distribution **shifted to mean +2.0**, keeping the development SD of 8.13;
  - the joint (w, S) dependence is kept by resampling development cluster pairs before the shift and contraction.
  - **The same construction applies to novice,** with its own development pairs, with mean win 0.90 and mean S +10.
- **The rule:** the smallest n_c in {60, 80, 100, 120, 150, 200} whose **simulated joint power** (both components of the endpoint) is ≥ 0.90 at the per-component level 0.005, by 20,000 simulated panels with a fixed seed.
  - The same n_c serves both heads (the larger of the two).
  - **If even 200 fails, stop and ask the owner** (DESIGN §10's trade-off rule, adapted).
- **The source:** the fresh v7c validation split. Its 32/40 is **not** the tuning panel, so it carries no winner's-curse from tuning. The remaining optimism (a W4-gated, outcome-informed sequence of designs) is handled by the conservative contraction and shift, **not** by a new development panel.
- **The planning receipt** (the n_c chosen, the power table, the fight and analysis time projections) is published and reviewed **before** any judging entropy is drawn.

## 5. Seeds, execution and safeguards (findings 3, 6 and 7)

**5.1 Seeds.**
- **Fresh OS entropy goes into a new judging ledger,** drawn at execution, inside an executor-only fence.
- **Before any dispatch,** the preflight checks the new seeds against the complete development and retired-root inventory for duplicates and overlap. Reviewers see hashes and the overlap receipt, not the values.
- **An overlap or a premature use** invalidates the ledger and requires a new registration. A consumed-root ledger prevents restarts.
- The heads use distinct seed namespaces.

**5.2 Immutable identity and safeguards** (carried from the historical SPEC):
- **Identity:**
  - the exact native request templates and controller selectors for v7 and for every comparator, all admitted against the frozen binary;
  - game, catalog and opponent fingerprints;
  - side and orientation semantics;
  - terminal-time validation, and the t < 150 win predicate with overshoot handling.
- **Approval:**
  - a review that binds the specification by hash;
  - the owner's authorization record.
- **Execution safeguards:**
  - a pre-dispatch identity fence;
  - exhaustive schedule keys, pairing by (head, cluster, orientation, arm);
  - exclusive output creation and a one-shot latch;
  - attempts written before dispatch;
  - immutable summaries, failure records and receipt hashes;
  - no cached outcomes.
- **Reporting:**
  - endpoint coverage;
  - a normalization ledger.
- **Kept outside the seal:** `docs/PLAN_CURRENT.md`, DESIGN files.
- **The older endpoints are superseded:** P1–P3 and the doctrine pool of DESIGN §6 / SPEC_0G are explicitly superseded for this registration. This S5 claims only E1 and E2.

**5.3 Failures:**
- **An attributable controller or numerical failure in a v7 fight** (detected by the native failure counters, non-finite values or a missing terminal) counts as **W = 0, S = −50** (the worst admissible score), **failure-coded and labelled.** The schedule **continues;** no retry.
- **An attributable failure in a comparator fight** is recorded and does not affect E1 or E2.
- **An infrastructure failure** (host, process, deadline, I/O) stops the run as **PARTIAL**, with no rerun on the same seeds.
- **An identity or integrity failure** makes the run **INVALID.**

**5.4 Budget and outputs:**
- **The primary record** is a minimal endpoint schema per fight: W, S, survivors, terminal time, failure counters, enemy guns destroyed, elimination time, own losses per kill.
- **Diagnostics:** full diagnostics only for a **predeclared subset** of fights, outside the verdicts.
- **The primary receipt** is computed from the minimal records, with **no HTML render and no full-trace parsing.**
- **Sealed:** the per-stage and cumulative caps, the concurrency (at most 10), the per-fight timeouts, deadline enforcement and child cleanup, and the stored-only analysis-interruption procedure (decided in advance; v7c's recovery authorizations do not transfer).
- **The fight count** (5 arms × 2 heads × n_c × 2) and the time projections are recomputed in the planning receipt and announced under decision 0031.

## 6. Stop rows

| Yes/no | Action | Role |
|---|---|---|
| Has the owner approved the sealed specification and the S-conjunct? | If no: no judging run | owner |
| Does the planning receipt need n_c > 200 for 0.90 joint power? | Stop; the owner decides | drafter |
| Does the frozen identity (binary, θ*, world, templates) differ at preflight? | INVALID; no run | implementer |
| Does a judging seed overlap any inventory, or get used early? | INVALID; new ledger and registration | implementer |
| Is there an infrastructure stop? | PARTIAL; no rerun on the same seeds | implementer |
| Does a valid panel fail either bound? | NOT_SUPPORTED as registered; no re-analysis | drafter |

## 7. The open questions, resolved

1. **Morale:** v3 stage-B, pinned to its exact code and knobs. **Its selection metric (mean S) is disclosed.** A stronger v6-era morale package is checked from **stored** development evidence before sealing; if one is materially stronger, both are included descriptively.
2. **E3 (v7 against forcedP16):** **descriptive only.** The paired differences are reported, and an observed match is not called equivalence.
3. **n_c:** by the §4 sizing rule. 60 is no longer assumed.
4. **Novice E2:** retained, as a compatibility check (> 50%), **not** a no-regression claim.

## 8. Self-audit (revision 2)

| Finding | What was wrong | Cause | Fix |
|---|---|---|---|
| 1 | the claimed power for 50–60 clusters was false; there was no joint power | a hand estimate with an optimistic design effect | §4, a simulated joint-power sizing rule under a conservative alternative |
| 2 | "cluster bootstrap" did not guarantee α | the method was named, but not specified or justified | §4, a distribution-free betting bound for bounded means, pinned |
| 3 | failure-as-loss conflicted with stop-on-failure | two policies were written separately | §5.3, failures split by type |
| 4 | "REFUTED" had no rule | wording carried over from older registrations | §4 verdict table; no REFUTED |
| 5 | the selection-bias explanation was wrong | tuning and validation were conflated | §4 sizing source |
| 6 | immutable identity and safeguards were incomplete | a proposal-level sketch | §5.2 |
| 7 | the analysis budget was undefined | the full-trace cost was underestimated | §5.4 |
