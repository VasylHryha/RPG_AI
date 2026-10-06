CHANGES_REQUIRED
Reviewer family: Codex
Reviewed DESIGN_0H_REV7.md SHA256: b1ae8e632d639374da6a5ea48f8eae8bf2915ac9fe9d79f93cf95b417a54f921

## Disposition of round-2 findings R2-1–R2-7

Section 9 of revision 7.2 governs over everything before it. Superseded statements are not counted as current defects.

| Finding | Round-3 disposition | Evidence and remaining work |
|---|---|---|
| R2-1, estimator-frame aliasing | SUBSTANTIALLY RESOLVED; residual MEDIUM | §9.1 accumulates stage-rate bounds over the complete frame and includes pair sums. It correctly labels the remaining stage-sampling limitation. The mapping from a pair flag to live estimator validity is unfinished; finding R3-2. |
| R2-2, frozen N1 recipes | CLOSED; additional numerical gap | §9.2 declares states, schedules, settings, matching endpoints, separate topologies and missing-entry outcomes. No implementer selection of those cases is needed. N1 still lacks a motion-error comparison; new finding R3-3. |
| R2-3, snapshot output membership | CLOSED | §9.3 permits O in the candidate, preserves its pin in extraction, kicks free positions and all candidate phases. G1c/G5 are no longer forced to default by excluding O. |
| R2-4, full vector regularization | CLOSED | §9.4 clamps both denominator appearances, defines coincidence, covers inside-cutoff motion in N1d, recentres F5(ii) and repairs the F4 start. The bound is conservative at fixed phases; accepted C4 element pairs remain unchanged. |
| R2-5, kick admissibility | CLOSED | §9.5 gives free-member spacing/RMS, destination clearances, eight ordered attempts, refusal, no clipping and requested/achieved RMS. Candidate minimum size three and the singleton output cap imply at least two free members when O is present. Keep the inherited zero-spacing/degenerate rejection. |
| R2-6, exact locking law | CLOSED | §9.6 supplies the stable arcsine branch, strict locking inequality, marginal boundary and small-offset qualification; it denies a sufficient network condition. |
| R2-7, governing stop table | PARTIALLY RESOLVED; residual HIGH | §9.7 supplies the requested numerical/fixture/readiness rows and preserves formal registration. But replacing all scattered rows drops inherited development and validity stops; finding R3-1. |

Codex (GPT-6), cross-family design review, round 3, 2026-10-06. Inspected HEAD: `190b8c76958a56a5e50d8a103dfc393eb75cd8e0`. This is a design verdict. Claude, as drafter, owns the repairs and their self-audit causes. No implementation or execution readiness is granted by this report.

Owner request reviewed verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Read AGENTS.md, both earlier revision-7 reviews, the complete revision-7.2 design and revision-6.5 base through 19.9, relevant inherited revision-5.1 rules, the fixture report, C4 model/detector and existing sampling/qualification adapters, current source guidance, plan and decision 0031. Executed only the authorized standalone toy, once: `python3 -B evidence/tactical_composition_demo/growing_shapes_review_claude/rev7_toy/f1b_toy.py`. It imports only `math`. No project code, tests, native library, panel, benchmark or experiment ran. Historical evidence and unrelated workspace changes remain untouched. Git metadata is read-only under this session's policy; the review is left uncommitted.

Evidence notation: **R7** = `evidence/tactical_composition_demo/DESIGN_0H_REV7.md`; **R6** = `.../DESIGN_0H_REV6.md`; **Base** = `.../DESIGN_0H.md`; **Report** = `.../growing_shapes/runner/REV6_FIXTURE_REPORT.md`; **Toy** = `.../growing_shapes_review_claude/rev7_toy/f1b_toy.py`; **C4** = `geomind/c4_model.py`. Other adapter paths are relative to `evidence/tactical_composition_demo/growing_shapes/`. Line references identify the inspected bytes.

Additional SHA256 identities: R6 `ca9c43362e3eebace889c7306784ffe5dd3095a58eb2095473f745eff31b52c5`; Base `39a630c3f4d440a6634538121773253443dcb15e8166406f36cde3727c119925`; Report `d530ae6236cb63e978d5224c33db693e446c9242884a5a4751295855158f7fc8`; C4 `4fafc161b65914a44dccaca6caefb59a5154079f17f564b4cdc4d44f58c59d33`; Toy `3f0513ac76a1dd03a2ed260a3a88d9927d0b0167f8ab730b383b87fc98b076b9`.

## New and residual numbered findings

### 1. R3-1 — HIGH: the replacement stop table loses development stop and INVALID rules

**Evidence:** R7:376 explicitly replaces the scattered rows. Its table (378–388) has no counterpart for R6:391–393: task-blind G1 FAIL, G0' FAIL, or G2 FAIL/INCONCLUSIVE → failure/diagnosis report and stop development. It also loses R6:557–558: unusable perceive → block G2/G0 without substitution, and unmatched full-run M births → that seed is G0-INCONCLUSIVE. Base:297 defines incomplete/interrupted runs and zero usable tasks as INVALID. R7:384 mentions only fixture measurement failures, not development readout failures. R6:619 explicitly retained the reviewed world/remember_static dependencies; the new integration row does not explicitly include them.

This is a live precedence conflict, unlike already withdrawn early pin/locking prose. An implementer following the new exhaustive table can advance after a development failure which 6.5 required to stop, or choose a disposition for unusable/incomplete evidence. Calling the rows merely additive would avoid some loss, but contradicts the declared replacement.

**Fix:** make §9.7 an actual consolidation. Restore the above yes/no rows with their inherited dispositions and responsible roles; include dependency readiness, development INVALID/incomplete evidence and zero usable tasks. Keep the full-run unmatched-seed rule separate from F7's fixture gate. No new scientific cut is needed. Preserve decision 0031's duration/time-of-day permission and the formal-milestone registration/pipeline boundary. The currently stricter F7 failure → block development can stand as a deliberate revision-7 policy; do not confuse it with how individual unmatched development seeds are classified.

### 2. R3-2 — MEDIUM: pair-only flags have no defined recipients or live-estimator scope

**Evidence:** R7:307 flags when an individual E exceeds π/2, or when a pair sum exceeds it for the current candidate/cohort. R7:310 then removes the “flagged elements' samples” from the 10-second estimators. For E_i = E_j = 0.9 rad, each individual passes, but their sum flags the pair. Neither member is individually flagged under the first predicate. The rule does not say whether to remove that pair observation, both members' observations, or every observation in the flagged frame. Those choices alter site coverage/gain and D1 lock differently.

The candidate/cohort scope is sufficient for retrospective structural screening, but the live lock estimator also uses element partners before any 60-second qualification cohort exists (Base:139–149; `medium/design_0h.py`:126–154). A pair of such members can have the above pair sum and still supply live lock samples. There is also a conflict between treating samples as missing and retaining the inherited prerequisite for 100/101 consecutive element samples (`medium/design_0h.py`:120–129,156–158). Dropping whole element records makes the entire estimator undefined, rather than merely reducing the eligible count as R7:310 promises.

This is a validity-mask contract gap, not evidence that a particular trajectory aliases. The frame accumulation itself repairs the original substep-only counterexample.

**Fix:** retain consecutive timestamped state records and E_i values. Declare separately: individual phase-sample validity; element-pair validity when E_i + E_j exceeds π/2; and site-pair validity under the carrier-relative screen (the held site angle/carrier schedule is already known). Apply the pair rule to all pairs actually used by live lock/PLV, irrespective of qualification membership. Use valid active observations for the unchanged 80-of-100 count and PLV denominator. Choose explicitly whether a pair failure invalidates only that pair or also both individual samples; the pair-only policy preserves more usable data. State what happens to P_i when the current frame is invalid and how the unwrapped endpoint ω̂ is retained or suspended. For structural qualification, evaluate the saved bounds on its actual cohort before running circular criteria. Keep the stage-sampling limitation and not-qualified disposition.

### 3. R3-3 — MEDIUM: N1 qualifies a changed motion law without comparing positions

**Evidence:** N1 turns motion on and compares h = 0.02 against 0.005 (R7:317–319), but its PASS metrics (330–333) cover only wrapped phases, entry, neighbour-list agreement and invariant pins. §9.4 then calls the new vector law qualified by N1d (353). No free-member position/velocity or minimum-distance error is compared.

Neighbour-list equality is a discrete condition. Substantially different free-node trajectories can retain the same lists; exact carrier locking can also make phase agreement insensitive to those distance errors. Therefore those endpoints cannot establish numerical accuracy of the inside-cutoff force, compaction or geometry histories. This is not a claim that h = 0.02 fails; no revision-7 integration was run.

**Fix:** before results, add a free-position refinement endpoint, for example maximum matched-endpoint Euclidean difference ≤ 0.01 m.u. over the existing 16-second cases, while retaining the current phase/topology/pin cuts. Declare that tolerance as new engineering admission, rather than inherited C4 evidence. Record minimum site/element distances in both integrations. Because adaptation consumes unwrapped phase endpoints, also compare unwrapped carrier-relative phase differences directly with the existing 0.01-rad cut, alongside the wrapped output comparison. This closes the whole-turn blind spot without changing the task clock or λ. Hash these endpoint definitions with the existing N1 recipes; any later tolerance change follows the fresh-revision rule.

### 4. R3-4 — LOW: the new site-body-off comparator still lacks its assay and cost binding

**Evidence:** R7:162 specifies the intervention but not the task set, panel, checkpoint set or pairing. R6:800 binds “all three” comparators in §19.9 to the final panel; it does not explicitly include this fourth intervention. An implementer could reasonably attach it to F5 checkpoints or the final medium, with different cost and interpretation.

**Fix:** bind site-body-off to fresh paired copies of the final whole medium on the same revision-7 perceive recipient panel and carrier/decoder as intact, removing only sites from N^x and retaining drives and element motion. Report paired differences descriptively beside G2, with no verdict cut. Include its episodes in A7's cost projection. If a wider task set is wanted, freeze that explicit scope before execution.

## Assessment of the requested mechanisms

**Diagnosis and λ.** The diagnosis is appropriately conditional under §8.1. F1b had a path at every step, eventual locking and a 15.4-second delay, so phase transfer was too slow for its deadline (Report:15–19). F1c compacted and lost drive strength despite 100% source drive-presence bins (Report:44–48). The 1,117 element-seconds of no sensor access is pooled over members; it is not source inactivity for 1,117 seconds. These observations support the two hypotheses without identifying their separate causal contributions.

The toy printed absolute entries 31.04, 19.52, 13.76 and 10.88 seconds for λ = 1, 2, 4 and 8. Subtracting the input step at 8 gives 23.04, 11.52, 5.76 and 2.88 seconds. Thus λ = 8 follows from §8.1's declared smallest-power-of-two, four-second-margin policy. It remains fixture-calibrated engineering, not a unique theoretical constant or a general two-second memory guarantee. The toy is zero-detuning, fixed-position forward Euler at h = 0.002; the real mobile RK4 fixture must still pass. Its “continuous entry” bookkeeping stops clearing late exits after t = 16 (Toy:23), so use it as this relaxation calibration, not a general-purpose settling verifier.

Writing β_i = θ_i − πt gives β̇_i = (ω_i − π) + λF_i. At fixed geometry, carrier-matched ω and constant input, relative dynamics time-dilate. With detuning or moving/adapting geometry, they do not. Scaling drive and coupling together retains their instantaneous coefficient ratio. The exact stable single-drive offset is now correctly arcsin[δ/(λa)]; larger λ widens locking and reduces small detuning offsets, but conflicting network drives need not lock. Neither ω nor motion should be multiplied by λ for this design. F1d reports the total λ effect in the pinned mobile system, including changed phase-dependent forces; it does not isolate the cause of the old failure.

**Carrier, sampling and adaptation.** The carrier still advances π·0.02 ≈ 0.063 rad per RK4 substep. The correction can be much faster: a single-site unweighted upper bound at g = 2, k = 4 is 64 rad/s, with additional internal coupling. That upper bound is neither a measured trajectory nor proof of RK4 instability. Carrier resolution, integration accuracy and 0.1-second PLV validity are separate questions. The new frame E is at least a bound on the absolute numerical RK4 endpoint increment, since RK4 uses positive stage weights summing to one. It is not a certified bound on every continuous excursion between stages, as §9.1 correctly discloses. N1 and the warning screen are useful bounded engineering checks once findings 2–3 are completed.

The 10-second unwrapped ω̂ measures realized rate. A net π/2 input encoding displacement contributes about 0.157 rad/s while it spans the estimator endpoints, and can feed intrinsic ω adaptation; speeding relaxation does not identify intrinsic frequency. Gain/reward depend on the valid active PLV samples and must obey the missing-sample policy above. η = 0.05/s still gives a 20-second adaptation clock. Retaining the 10/60-second windows, 0.005-rad/s frequency cut and 0.1-rad angular cuts is defensible as §8.8's fixed admission rules for new driven, anchored snapshots. Dividing all windows by eight would incorrectly change the geometry/carrier experiment. Faster driven recovery can increase admission without demonstrating autonomous closure; old 6.5/C4 qualification rates or accepted evidence do not transfer.

**Pins, normalization and task scope.** The full site vector law has consistent units: A is m.u./s, B is m.u.²/s, J and λ are dimensionless, and phase coupling/drive are rad/s. Inside r₀, the new displacement/max(r,r₀) law has bounded spatial derivative at fixed phases; its zero vector at exact coincidence is defined. It is a new regularization, not literally the unchanged C4 pair law inside the cutoff. Separate N^x and N^θ lists prevent sites from stealing phase-neighbour slots or changing phase normalization. Site forces are unweighted, activity-gated external inputs, separately accounted; they can vanish or jump as inputs hide or rebind.

At the live origin all physical sites are four units away, beyond strict radius three, and sites have no phase-coupling term. O has fixed position and zero direct phase drive, so there is no literal site→O phase echo. Input can reach ordinary geometry through the site cosine/activity channel even when g = 0; the mask means zero direct phase drive and masked sensor histories, not zero observation-to-motion access. With O pinned, removing incoming element phase coupling still removes the terminal input route. A short driven relay can satisfy the narrowed G2 response claim. Phasor/relay/K=0/fixed-position comparisons remain essential for interpreting what computation occurred.

Pins plausibly improve persistence but do not supply permanent tensile bonds or ordered-chain preservation. F1c's effective-root path, source access, entry/hold and long-run response cuts are meaningful; pin invariance is correctly an implementation check. A compacted configuration or newly created shortcut can pass those functional cuts. Report span, distances and shortcuts, and call PASS sustained access/response under the anchored law, not proof that compaction was prevented. F1c may fail; that is a legitimate gate, not a reason to tune λ or thresholds within the same revision.

**Timers, empty start and entropy.** §8.9's active/uncovered increment, covered/birth reset, inactive freeze and refusal retention are coherent. Active-at-check guards prevent stale demand from creating an inactive-source birth. B-path correctly keeps its immediate rule. Cue demand can accumulate structurally while established memory blocks still have undefined P_i and zero eligibility under 80/100. Empty intact/M/U starts share the first check, clock and id rules; variation now comes from growth/world streams rather than nonexistent initial detuning. F5(ii) remains a deliberate literal exception, with its corrected clearance and missing route.

§8.10 supplies new master prefixes and explicit new world ranges, retaining old calibration and historical reference labels. Actual inventory instantiation, disjointness and hashing remain pre-execution obligations. Deterministic fixtures and the calibration toy are engineering recipes, not independent fresh-seed evidence. Current source status is recorded VERIFIED in `research/rrg/CURRENT.md`; this review did not rerun package qualification. Preserve accepted C4 bytes, historical receipts and the 6.5 FAIL/NOT_RUN accounting. The formal lifecycle and drafter-owned repairs in AGENTS.md still apply; no RRG background recursion, selection or reusable functional library is established by this review.

## Drafter handoff and adversarial recheck

Complete R3-1–R3-3 as one small design batch before declaring revision-7 integration ready, and bind the low comparator note before its execution. Record causes in the self-audit. No task-score tuning or wholesale change of the mechanism is required by these findings.

The critique was checked against §9 precedence and the actual inherited adapters. The old scalar-clamp defect, O-exclusion defect, two-second λ contradiction and nonexistent B-path timer are closed, not repeated. No instability is inferred from a rate bound, no autonomous-recovery criterion is added, and no criterion is added to forbid legitimate shortcuts under the narrowed task. The remaining blockers concern lost governing rules and explicit measurement contracts. Plan A6b records this round; repair dispositions remain with Claude before the next review/integration step.

Assisted-by: Codex:GPT-6
