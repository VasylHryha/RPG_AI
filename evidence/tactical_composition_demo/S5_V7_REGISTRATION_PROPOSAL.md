# S5 registration proposal, revision 4 (consolidated): the v7 resonator controller against the scripted AI (DRAFT for the owner's approval)

**Date:** 2026-10-08, night. **Drafter:** Claude (claude-opus-5-5). **Reviewer:** Codex (cross-family).
**History:**
- revision 1 is at `f48a1c9`, revision 2 at `b98306b`, revision 3 at `510fd1d`;
- the reviews are `docs/reviews/tactical_0g_s5_v7_proposal_review{,_r2,_r3}_codex.md`;
- **this consolidated text replaces all earlier wording.** The self-audit is in §9.

**Status:** **DRAFT. Nothing here authorizes a run.** A registered (judging) run needs:
- this proposal approved in review;
- a sealed specification that implements it exactly, and its review bound by hash;
- **the owner's explicit approval** of the specification, of the 200-cluster cap (§5), and of the run (AGENTS.md; plan B6).

## 1. Why now

- **The W4 drafting condition is met** (plan B6; DESIGN §19): a development version beats the regular scripted AI in elimination wins.
- **v7:** 32/40 regular elimination wins and 40/40 novice on fresh validation (DESIGN §20.3 and §20.3.1). Codex's recheck: `docs/reviews/tactical_0g_v7_validation_recheck_codex.md`.
- **The owner's rule:** the strongest simple comparators are reported, labelled.

## 2. Claims and non-claims

**The claims (the registered endpoints, §4):**
- **E1:** the frozen v7 package's **elimination-win rate against the regular scripted AI is above 50%,** on fresh judging seeds. The rate **includes the registered failure penalty**: an attributable v7 failure counts as a lost fight.
- **E2:** the same against the novice scripted AI. **E2 is a compatibility check above 50%, not a no-regression claim** relative to the 100% development rate.
- **Each endpoint is verdicted separately.** No combined "both heads" success claim is made.

**Not claimed:**
- that the oscillator gate is necessary, or better than always committing (development: an observed match);
- synchrony as a cause;
- B→R→B recursion;
- hierarchy or source qualification;
- causal superiority over any labelled comparator;
- generality beyond this fixed world, roster, rules and the two scripted levels.
- **Mean S is a reported secondary (DESIGN §19), not part of any verdict.** An inferential S conjunct would be a new owner decision, with a revised design and sizing.

## 3. The frozen object

| Item | Identity |
|---|---|
| The native binary | `astelia_cpp/s4_v7c/build/astelia_native_v7`, SHA256 `9e8781b7e1004f62d9f4d4964fa855608b3070a9dd07fa4037bfbbd69e9fc2dd` |
| The native build manifest | SHA256 `f2e1c916a08f170342073d5a03ae98e57e70de4e8c32971f469d17ea263b2790` |
| `s4_v7c/BUILD.json` (95 source hashes) | SHA256 `63c7d989288c29095115b72dcea66b7337ba7fb276558da3a6a19773fcab2aea`, a different file from the native manifest |
| θ* | `s4_v7c/THETA_ORIGIN.json`: tuning commit `796d0a8`, ordinal 161, TUNING.json SHA256 `6b146edcbd9d6c2147297deab0bc9149ba9801de979a7d1594f6889a89296e65` |
| The world | the fixed S4 world (50 against 50: 10 melee, 30 ranged, 10 artillery), game rules, `sandboxAbilities = false`, 150 s, dt 1/30 |
| The win predicate | enemy 0, own ≥ 1, terminal time < 150 s, with the §20.2 overshoot-tick convention. A timeout is never a win |

- **The sealed specification adds:** the exact native request templates and controller selectors (v7 and each comparator), the game, catalog and opponent fingerprints, the orientation and side semantics, and the orchestration and analysis identities.
- **Kept outside the seal:** `docs/PLAN_CURRENT.md` and the DESIGN files.
- **The comparators (labelled, descriptive, same seeds, admitted against the frozen binary):**
  - P16 at its historical knobs;
  - forcedP16(θ*);
  - morale v3 stage-B, pinned. Its selection metric (mean S) is disclosed. A stronger v6-era morale package is checked from **stored** evidence before sealing; if one is materially stronger, both are included.
  - v6 at its attempt-2 knobs.
- **E3** (v7 against forcedP16) is **descriptive only:** paired differences, never called equivalence.
- **The older endpoints are superseded for this registration:** P1–P3 and the doctrine pool of DESIGN §6 and SPEC_0G.

## 4. The endpoint test

**The sampling unit** is a cluster: one judging seed in both orientations. Clusters are i.i.d. The cluster win fraction is X_i = w_c ∈ {0, ½, 1}.

**The one-sided betting lower bound** (the predictable plug-in construction of Waudby-Smith and Ramdas 2024, JRSS-B; arXiv 2010.09686: the paper's estimators of equation (26) and Theorem 3, positive capital only, h = 1; a fixed-n final-capital test, a declared one-sided variant of the paper's recommended two-sided procedure):
- **The processing order** is the sealed schedule-key order of the clusters, not the outcome order.
- **The predictable estimates (the paper's equation (26)):**
  - μ̂_i = (1/2 + Σ_{j ≤ i} X_j) / (i + 1);
  - σ̂²_i = (1/4 + Σ_{j ≤ i} (X_j − μ̂_j)²) / (i + 1);
  - with μ̂_0 = 1/2 and σ̂²_0 = 1/4.
- **The bet for observation i, at a null mean m ∈ (0, 1):**
  - the base bet a_i = sqrt( 2 ln(1/α) / (n · σ̂²_{i−1}) ), which depends only on earlier observations;
  - the clipped bet λ_i(m) = min(a_i, c/m), with **c = 1/2**.
- **The capital:** ln K_n(m) = Σ_{i=1..n} ln[1 + λ_i(m)(X_i − m)].
- **The rejection rule:** reject "E[w] ≤ m" iff ln K_n(m) ≥ ln(1/α), with **α = 0.005 per endpoint.** Bonferroni over E1 and E2 gives support-family error ≤ 0.01.
- **Inversion:** on the grid m ∈ {0.0001, 0.0002, …, 0.9999}:
  - LB = **the largest grid point g such that every grid point ≤ g rejects**;
  - LB = 0 if no positive grid point rejects. m = 0 and m = 1 are not evaluated.
  - **K_n(m) is nonincreasing in m** (Codex round 3), so this is conservative.
- **Numerics:**
  - finite inputs in [0, 1] only;
  - the log capital is computed in IEEE double;
  - comparisons with |ln K_n(m) − ln(1/α)| < 10⁻⁹ are re-evaluated deterministically in exact rational or 50-digit decimal arithmetic.
  - There is no outcome-selected epsilon or fallback.
- **The verdict:** **SUPPORTED** iff LB > 0.5 (on the grid, a rejecting point ≥ 0.5001). Otherwise, on a complete valid panel, **NOT_SUPPORTED**, which is neither a refutation nor an equivalence.
- **The same code** serves the planning simulation and the final analysis. Its hash is sealed before sizing.
- **Descriptive only:** the same bound on (S + 50)/100 for mean S, and the other §19 secondaries.

## 5. Sizing: achievable adverse scenarios, a common n

**The failure law, frozen (R3-1):**
- each oriented fight independently becomes an attributable failure with probability f, **independent of its underlying outcome and of the other orientation**;
- a failure replaces that fight's win with 0.

**The scenarios** (cluster probabilities of w = 1 / ½ / 0, after the failure law):

| Scenario | Base per cluster | f | Resulting P(1) / P(½) / P(0) | Mean |
|---|---|---|---|---|
| R-a | P(1) = 0.70, P(0) = 0.30 (concordant) | 0 | 0.70 / 0 / 0.30 | 0.700 |
| R-b | 0.55 / 0.30 / 0.15 (development-like shape) | 0 | 0.55 / 0.30 / 0.15 | 0.700 |
| R-c | independent orientations, p = 0.70 per fight | 0 | 0.49 / 0.42 / 0.09 | 0.700 |
| R-d | R-a | 0.02 | 0.67228 / 0.02744 / 0.30028 | 0.686 |
| N-a | P(1) = 0.85, P(0) = 0.15 (concordant) | 0 | 0.85 / 0 / 0.15 | 0.850 |
| N-b | 0.75 / 0.20 / 0.05 | 0 | 0.75 / 0.20 / 0.05 | 0.850 |
| N-c | independent orientations, p = 0.85 per fight | 0 | 0.7225 / 0.255 / 0.0225 | 0.850 |
| N-d | N-a | 0.02 | 0.81634 / 0.03332 / 0.15034 | 0.833 |

- **N-d derived:** P(1) = 0.85 × 0.98²; P(½) = 0.85 × 2 × 0.98 × 0.02; P(0) = the rest.
- **The power is conditional on these declared scenarios.** It is not a population property.

**The rule (R3-1):**
1. For each n ∈ {60, 80, 100, 120, 150, 200}, simulate 20,000 independent panels per scenario cell (numpy PCG64, seed 20261008, with the version and the order of RNG use sealed) and apply the frozen test.
2. Take each cell's **one-sided Clopper–Pearson lower bound of power at tail 0.01/48.** That is 48 cells: 6 n values × 8 scenarios. It gives ≥ 99% simultaneous Monte Carlo assurance.
3. **n_c = the smallest common n at which all 8 scenarios** (both heads) **have a lower bound ≥ 0.90.**
4. **If no candidate up to 200 qualifies, stop; the owner decides.**
- **The 200 cap** is a new proposal that replaces DESIGN §10's 2,000-cluster boundary for this registration. It needs the owner's approval.
- **A scale check, not a power result:** at n = 60 the best possible test for R-a has power ≈ 0.72, so 60 cannot qualify. The table decides.
- **The planning receipt** (input, code and scenario hashes; the full table; n_c; the fight and analysis time projections) is published and reviewed **before any judging entropy is drawn.** Assumptions and seeds never change after the table is seen.

## 6. Seeds and execution

- **The judging ledger:**
  - fresh OS entropy, drawn at execution inside an executor-only fence;
  - a pre-dispatch overlap and duplicate check against the complete development and retired-root inventory (reviewers see hashes and receipts, not values);
  - distinct per-head namespaces;
  - a consumed-root ledger.
- **An overlap or a premature use** makes the run **INVALID** and needs a new registration.
- **Carried from the historical SPEC:**
  - **identity and approval:** a pre-dispatch identity fence; the review binds the specification by hash; the owner's authorization record;
  - **execution:** exhaustive schedule keys, pairing by (head, cluster, orientation, arm); exclusive outputs and a one-shot latch; attempts written before dispatch; immutable summaries, failure records and receipt hashes; no cached outcomes;
  - **reporting:** endpoint coverage, with evaluated values, bounds and verdicts, or not_run with reasons; a normalization ledger.
- **The primary record:** a minimal schema per fight (W, S, survivors, terminal time, failure counters for both sides, enemy guns destroyed, elimination time, own losses per kill).
  - **Full diagnostics** only for a predeclared subset, outside the verdicts.
  - **The primary receipt** is computed from the minimal records only (no render, no full-trace parsing).
- **Sealed:** the per-stage and cumulative caps; at most 10 workers; per-fight timeouts; deadline enforcement and child cleanup; a stored-only analysis-interruption procedure (v7c's recovery authorizations do not transfer).
- **The fight count** (5 arms × 2 heads × n_c × 2) and the time are taken from the planning receipt and announced under decision 0031.

## 7. Failure attribution (R2-3; precedence in this order)

1. **INVALID:** any identity, integrity or seed-hygiene breach. It voids the run.
2. **PARTIAL:** an infrastructure interruption (host, process exit without a controller failure record, deadline, I/O), or an opponent or world failure, or an opaque failure.
   - **Per endpoint:** a head whose panel completed keeps its verdict; the other is reported not_run, with the reason.
3. **Attributable v7 failure:** our side's native controller failure counter > 0, or a non-finite controller state reported by our controller, in a completed process with a valid terminal record.
   - **The endpoint value is W = 0,** labelled "failure-coded". The schedule continues; no retry.
   - **Actual diagnostics are kept separately.** No survivor counts, times or ratios are invented. Descriptive denominators exclude failure-coded fights and report the exclusions.
4. **An attributable comparator failure** is recorded, with no effect on E1 or E2.

## 8. Stop rows

| Yes/no | Action | Role |
|---|---|---|
| Has the owner approved the sealed specification, the 200 cap and the run? | If no: no judging run | owner |
| Does the planning receipt find no common n ≤ 200? | Stop; the owner decides | drafter |
| Does the identity differ at preflight? | INVALID; no run | implementer |
| Does a judging seed overlap, or get used early? | INVALID; new ledger and registration | implementer |
| Is there an infrastructure stop? | PARTIAL per endpoint; no rerun on the same seeds | implementer |
| Does a complete valid panel fail its bound? | NOT_SUPPORTED as registered; no re-analysis | drafter |

## 9. Self-audit

| Finding | What was wrong | Cause | Fix (revision) |
|---|---|---|---|
| r1-1 | a false power claim for 50–60 clusters | a hand estimate | the §5 sizing table (r2, r3, r4) |
| r1-2 | the bootstrap did not guarantee α | the method was not specified | §4, a distribution-free betting bound (r2) |
| r1-3 | failure-as-loss conflicted with stop-on-failure | two policies written separately | §7 (r2, r3) |
| r1-4 | "REFUTED" had no rule | carried-over wording | §4 verdicts (r2) |
| r1-5 | the selection-bias explanation was wrong | tuning and validation were conflated | §1 and §5 (r2, r4) |
| r1-6/7 | the identity, safeguards and budget were incomplete | a sketch-level draft | §3 and §6 (r2, r4) |
| r2-1 | contraction created impossible outcomes | the data were transformed instead of modelled | §5 achievable scenarios (r3) |
| r2-2 | the algorithm was not frozen before sizing; the S conjunct was costly; Monte Carlo error was ignored | ordering; I misread §19 | §4, §5, §2 (r3, r4) |
| r2-3 | failure attribution was unspecified | principles only | §7 (r3) |
| r3-1 | the failure law and the common-n rule were undefined | a marginal f only; per-head maxima | §5 (r4) |
| r3-2 | the variance estimator was not the paper's | an index error (μ̂_{j−1} instead of μ̂_j) | §4 now uses equation (26) (r4) |
| r3-3 | the S conjunct survived in §2 | revision 3 appended instead of consolidating | this consolidated text (r4) |
