READY

# S4 v3 adversarial recheck

Reviewer/repair family: Codex (GPT-6). Reviewed workspace HEAD: `03fe69e715f48e6bdc26c06cbd715041c2c30c96`, including implementation `cb9c9df2fb16c80501096078521d75361d10901e`, development `e60fbe5`, and Claude review `527c1fb`. Date: 2026-10-06.

READY means the completed **development record** survives this recheck with the corrections below. It does not establish optimality, tactical superiority, scientific acceptance, calibrated S5 sample sizes, or permission for another long run. No production-mode defect contradicting section 14 was found. The historical runtime guard requires repair before future capped execution; the measured historical run did not breach its allowance.

Scope: section 14 and inherited section 13, native v3 mode logic/tests, `s4_v3.py`, the full development record, report and Claude review. Changes are confined to new files or v3 files under `astelia_cpp/`. Native production code, historical harness/code pins, original results, receipts, seeds, knobs, protocol and Claude's review remain unchanged. No tuning, panel, mutation probe or new experiment was run. Exactly **two** diagnostic replays used recorded C knobs and the preselected regular-validation seed `712101000`, orientation false, with at most two native processes. They took 11.70 seconds and matched the original orientation summaries byte-for-field. They are excluded from original run counts.

## Findings and repairs

### F1 — Medium: the fixture test rewrote committed evidence and used ten workers (fixed)

`test_s4_v3.py::test_v0_v1_v2_fixture_bytes_and_v3_engineering` wrote `s4_v3_checks/PART1_PARITY.json` every time it ran and used ten workers for both fixture groups. That conflicts with receipt preservation and this session's two-worker restriction. The previous receipt is valid historical evidence; it is not a disposable test output.

**Repair:** its output now goes to pytest's `tmp_path`, and both pools use two workers. This does not change the controller or recorded measurements. The unchanged 408 predecessor fixture results and v3 engineering receipt were inspected and preserved, rather than launching hundreds of combat fixtures again. The modified full parity test is intentionally excluded from this bounded session; its original behavioral assertions remain unchanged.

### F2 — Medium: historical cap enforcement is incomplete (report corrected; future runner repair required)

`Bench.evaluate()` checks time only before `pool.map()` queues the whole panel. `execute()` has a fixed 120-second subprocess timeout, without the remaining global allowance. A C validation arm queues 4,200 fights; it can continue after the deadline. Replays check launch time only; `close()` waits for queued work. The conservative forecast occurs before tuning generations, not before every validation task. Deadline-launch checks therefore cannot enforce a strict cap on ongoing work or exception cleanup.

**Impact on this record:** none observed. Outer execution was 167.65 minutes, plus 34.48 retained prior minutes = 202.13, inside the 360-minute cap. The pre-fight protocol declares that cap, and code uses the corresponding 325.52-minute execution allowance. Its implementation commit is timestamped 18:47:16 UTC, before execution starts at 18:47:31 UTC. There was no retrospective extension. This is wall-time accounting with ten workers, not summed CPU-minutes. The naive guard must not be described as an interruption guarantee.

The reported combined 202.13 minutes is the explicitly declared **v3 + original-run** accounting, not cumulative revision cost: intervening amended/v1/v2 runs are excluded. Stored elapsed values across original/amended/v1/v2/v3 sum to about 487.21 wall minutes, excluding tests/builds/reconstruction and wrapper overhead. This is not a violation of v3's predeclared allowance, but a reason to avoid presenting 202.13 as all development expenditure. The report now makes that distinction.

**Repair:** corrected the development report's claim and documented the limitation. The historical runner is retained at its recorded hash. Before any future capped run, implement bounded submission, an absolute monotonic deadline carried to workers, timeouts clamped to remaining allowance, pending-future cancellation and termination of active children on stop. Test near-deadline validation and failure cleanup with fake workers, without combat. That is a later runner revision, not a change to the completed record.

### F3 — Medium: correct binary pair distances do not guarantee escape from the kill zone

Section 14 fixes the *preferred distance of one out-ranged pair*. The full velocity still adds the damage-weighted mean over up to sixteen enemies and the ally force. Opposing terms can cancel even with every pair committed. Kite pairs retain their continuous inherited law. Collision, arena boundaries and repeated mode reversals further separate preferred distances from actual trajectories.

The new synthetic native contract constructs two symmetric enemies and obtains zero summed enemy velocity although each pair is committed. This is a counterexample to a global no-hovering guarantee, **not** a section-14 implementation failure. The effective artillery bound can exceed enemy reach, as the design explicitly allows; the exclusion check is then vacuous. Q3's own-artillery override also applies in the inherited kite case, even where that reduces the direct protection expected from a kite band. These are disclosed inherited law choices, not repairs to apply retrospectively.

**Repair:** the development report now states the scope of the binary guarantee. Recommendations below address the remaining dynamics on fresh evidence.

### F4 — Medium: Claude's causal attribution exceeds the comparisons (corrected in report; review retained)

The review's claim that the skeleton is the main source of performance is not identified by these comparisons. Push-pull lacks the stateful arms' pressure processing, target alignment and tunable retreat width/threat weighting, has three rather than eleven parameters, and has constant commitment. Resonator and morale have different state equations, initial conditions and independently selected knobs. Equal fight budgets and common environments make this a fair comparison of the **declared controller packages**, not an isolated effect of circular state or the skeleton.

The pool difference +0.460 describes final separately tuned packages. It does not establish equivalence, prove phases add nothing, or identify which mechanism produced the large advantage over push-pull. The report now states these limits. Claude's review remains unchanged outside the allowed write scope.

Claude's development readings are otherwise materially consistent: morale has positive regular head means at both B and C; resonator is negative at both. Its hypothetical P2 INDETERMINATE reading is consistent with section 6: REFUTED requires an upper bound **below zero**, not merely below δ. No registered verdict follows from the displayed descriptive 95% intervals, and B knobs are not the final C configuration.

### F5 — Medium: n planning is arithmetic, not finite-sample power qualification (report corrected)

Independent arithmetic reproduces δ = 3.5, P1 n = 99 per head, P2/P3 n = 16 shared seed blocks per doctrine. The squared normal quantile sum is 16.7165300325. P2/P3 use the recorded maximum block variance, tuning pooled variance/19 and stratum floor; P1 takes the larger B-tuning/C-validation upper SD and a common head count. No bootstrap results or planning receipts were rewritten; the existing bootstrap was not rerun.

Limits: the rule assumes hypothetical favorable effects (P1 +δ over zero; P2/P3 +2δ over margin δ), rather than the observed negative regular mean or small P2 effect. At sixteen independent blocks, estimated variance and the eventual t/bootstrap inference procedure can require more samples than known-variance normal planning. The tuning variance/19 allowance assumes independent doctrine contributions; taking a maximum with observed validation block variance is prudent but does not guarantee coverage of unseen covariance. Selected tuning spreads are exploratory, and marginal bootstrap upper SD is not a joint noise bound for every endpoint.

**Repair:** added these caveats to the development report. A later S5 specification must name and calibrate its inference procedure before presenting the proposed counts as a 90% power guarantee. Increasing n cannot rescue a true effect below the superiority margin. The proposed owner margin was not shrunk to pass.

### F6 — Low: stale review status and missing regular trajectory evidence (fixed)

The report still said Claude review was next after that review existed. Original A/B/C replay exports cover novice, novice and line; none shows regular. Thus they alone cannot substantiate a causal account of the regular weakness.

**Repair:** updated the review status and added the two matched, explicitly post-development diagnostic captures in `s4_v3_recheck_checks/replays/`. No new seeds, knobs, tuning choices or validation observations entered the original record.

## Section-14 audit

| Case | Finding |
|---|---|
| Initial pair | `emplace(c >= 0)`; negative initial values inside the band escape; zero commits. |
| Hysteresis | Only strict `c > .2` / `c < -.2` switch. Exact boundaries retain memory. Adjacent floating-point values outside the boundaries switch. |
| Own/enemy reach | Centre-distance role/radius definitions match Q3; equal reach is in the binary branch. |
| Artillery | Commit is `max(f_c R_i, 1.05 Rmin)`; escape is `R_e + w R_i`; effective lower bound exceptions are explicit. |
| Kite | Returns inherited `v2Preferred`; does not create or mutate a binary mode. Static catalogue ranges make branch eligibility stable in these fights. |
| Enemy-set changes | Production updates all living out-ranged pairs before truncated motion. An excluded pair's threshold crossing survives reentry inside the band. New pairs initialize separately. |
| Death/absence | Either absent/dead id removes the pair before preparing new decisions. Reappearance initializes anew; ids are monotonic in real worlds. |
| Clone | Production base-class clone copies the maps, prepared decisions and RNG by value. Clone death/update cannot change the parent. |
| Coincidence/failure | Zero-distance motion skips its undefined direction; production's earlier all-pair update preserves modes. Nonfinite state/action is failure-counted and held; zero recorded failures. |
| Force law | Weighting, restoring sign, target hysteresis and ally law are inherited. Pair binary distance is not a constraint on summed force or final position. |

No code change is justified in these valid-input mode paths. Synthetic tests extend the original checks for excluded-pair crossings/reentry, production clone rather than test clone override, absence/death/revival, input permutation, exact/adjacent hysteresis boundaries, equal reach and force cancellation. Existing historical fixture parity is unchanged evidence for predecessors; passing fixtures alone is not universal equivalence proof.

## Evidence and comparison integrity

[ANALYSIS.json](s4_v3_recheck_checks/ANALYSIS.json) contains the rerun reconstruction, independent calculation and preservation hashes. The unchanged original `audit()` writes its reconstructed receipt only to the new checks directory. A separate stream calculation strips only the controlled arm/knobs to compare the world requests, recomputes validation means/SD/SE from orientation scores, checks end-state counts and reconstructs equal stage budgets. It does not trust the report's numbers.

- 107,094 fresh scored fights; zero cache hits; 87,894 tuning and 19,200 validation fights; 2,304 CMA candidates. Twelve original replay captures bring historical native executions to 107,106.
- Every tuned arm uses 9,766 evaluations per stage, including its initial candidate. The initial stage/preceding winner, CMA ask/tell feedback, highest-mean retention and stable earlier ties reconstruct. Nearest is explicitly untuned; three-dimensional push-pull and eleven-dimensional arms receive equal evaluations, not equal search difficulty or CPU budgets.
- 57 tuning seed ids and 400 distinct validation seed ids; no overlap within v3. Pure declaration checks cover original/amended/v1/v2/S3 separation. Shared seeds across arms, doctrines and orientations are intentional pairing, not independent replicate counts. The pool has 100 independent seed blocks, not 1,900 independent draws.
- Each validation endpoint has 100 clusters/200 orientations. No dropped orientation, raw/ledger mismatch, missing endpoint, failure or planner work was found. Both new diagnostic summaries match their exact original orientations, not merely a cluster average.
- `s3_runner.request` gives all arms the same army, arena, time/dt, skills and opponent per comparison. A is melee-only; B/C full armies. Novice has off/default reduced skills, regular has formation/default regular skills; C doctrine profiles have elite-no-rollout skill overrides. All recorded planner counters are zero. Projectiles remain an observation asymmetry against script arms; this is documented and not a claim that every opponent receives the restricted API.
- Validation never chooses knobs or starts a subsequent stage: B/C inherit preceding tuning winners. A/B validation may stop execution, as declared; every arm completes before that gate. Development validation was used for spread/margin planning, and earlier revisions informed v3. Thus it remains development evidence, not untouched scientific confirmation. Fresh S5 entropy is still required.
- The original binary/source/optimizer/design/spec identities pass admission and hash checks. All 84 preserved development/check files listed in the new analysis retain their hashes. Original transport bundles are unrelated to the new bundle and were not rewritten.

## What limits resonator against regular

Population evidence is stronger than either new replay: B regular resonator-minus-morale mean is −16.12 (descriptive 95% interval [−17.517, −14.723]); C is −6.65 ([−8.325, −4.975]). Final resonator itself is −1.655. C improves that head descriptively versus B but optimizes the nineteen-doctrine objective, not regular head performance; those objectives need not agree.

In the matched C diagnostic, at t = 60.87 seconds the resonator has 40 units while only ten enemy guns remain. It ends with zero versus six guns at t = 114.10. Morale reaches the analogous gun-only phase at t = 64.67 with 24 units; it ends at timeout with six ranged units versus nine guns. That morale orientation scores −3 and the resonator −6; this one pair is illustrative and does not replace the 100-cluster population means.

Captured commitment after integration, aligned to the **previous** pre-step trace, shows the resonator's ranged threshold state committing for roughly half its unit-ticks (49.8% before t=60; 50.6% thereafter). Its ranged median lifetime threshold-switch count is 45.5, versus 1 for morale. These are deterministic threshold reconstructions for persistent out-ranged pairs, not exported pair-mode telemetry. The final ranged natural rate is −1.889 rad/s, a free period near 3.33 s; measured absolute uncoupled angular drive remains about 1.75 rad/s after t=60. K = .00758 and K_t = .09722 provide little relative coupling in these selected knobs. The evidence supports rapid reversals rather than sustained progress or retreat as a plausible limit; no counterfactual proves that reducing this rate alone would improve combat.

For a typical shooter versus a gun, centre reach is about 278 versus 320 px. C's binary preferred distances are about 270 and 606 px. Roughly half-cycle changes can reverse the radial force well before traversing that gap. The v3 change removes the interpolated pair equilibrium, but does not remove time-averaged oscillation, mixed-force cancellation or boundary clipping. Morale can hold its escape mode as its state relaxes back inside the hysteresis band; at t≈80 onward this diagnostic's six survivors sit near x=25 without targets. Its timeout survival is real under the declared survivor-first S objective, but does not show gun destruction or unrestricted tactical strength.

## Principled later improvements (not applied to this record)

1. **Match mode dwell to geometry and travel time.** A bounded pair dwell/release condition based on effective commit/escape reach and observed movement capacity can prevent reversal before either safe region is reached. Define behavior under damage, target death and arena infeasibility; use the same rule/knob budget in resonator and morale. Do not hard-code gun ids or an outcome-specific timer. This changes section 14 and needs a declared later revision with fresh tuning/validation.
2. **Test vector feasibility before interpreting commitment as progress.** Diagnose projected velocity toward the chosen reachable threat, cancellation ratio and boundary clipping. A common constrained motion rule could require progress toward commit or a feasible safe retreat, while retaining lawful ally interactions. First use synthetic contradictory-threat and boundary cases; do not remove terms solely because this seed lost. Pair distances alone cannot supply this guarantee.
3. **Separate oscillation from structure with matched ablations.** Compare circular vs damped state, frozen vs active state coupling, and common movement/pressure/target rules with matched parameter budgets, then retune each equally on fresh development seeds. Predeclare a regular-head retention constraint or multi-objective tradeoff if head performance must survive C tuning. The current results cannot select which ablation will win.
4. **Improve development objective coverage within equal budgets.** C uses one tuning seed per doctrine and B ten/nine head clusters. More balanced common clusters, fewer generations if necessary, and a separately reserved fresh validation split can reduce objective selection noise. No budget increase or retuning is justified retrospectively. Population evidence should report survivor outcomes, timeouts, damage, gun counts and role survival separately; changing the scientific objective requires owner approval.
5. **Capture decision mechanics and qualify planning.** A later output-only trace should include actual pair modes, selected enemy ids/weights, raw ally/enemy velocity, sanitization and clipping, with exact tick labels. Use a bounded deadline-aware runner, preserved immutable source snapshots and a predeclared finite-sample inference method. Keep diagnostic instrumentation out of the policy API and do not use validation trajectories to tune that same revision.

## Verification and delivery

Affected tests ran once after the complete code/test edit batch: **12 passed, 7 deselected in 3.10 seconds**. Exact command, wrapper timing and output are in `s4_v3_recheck_checks/TEST_TIMING.json` and `tests.stdout.txt`. The bounded selection includes the new synthetic native tests, original admitted native contracts, v3 report tests and pure v3 seed/protocol/optimizer tests. It excludes receipt-writing predecessor suites, the hundreds-of-fights parity/engineering test, and unrelated rebuild-driven native parameter tests. Production controller code was not changed, so no historical full suite or fight grid is repeated. Later edits only clarify prose and delivery metadata.

Delivery and exact committed identity are recorded in `s4_v3_recheck_checks/DELIVERY_NOTE.md` and `BUNDLE_VERIFIED.json`. The shared `.git` is read-only under this session's permission profile; the task is committed with repository hooks enabled in an isolated temporary clone and delivered as a verified bundle. Unrelated concurrent 0h/C6 work is preserved.
