# C6 unblocking review request — Claude

**Status:** OWNER-AUTHORIZED REVIEW/PLANNING ONLY  
**Authorization:** [decision 0026](../decisions/0026-authorize-c6-unblocking-review.md)  
**Repository:** `VasylHryha/RPG_AI`  
**Reviewed baseline HEAD:** `7a1e89e46a9a7ebd0f2a7d540edd8f148506e7ac`  
**C6 state:** `BLOCKED / R006 STOP`  
**Required output:** `docs/reviews/c6_unblocking_review_claude.md`

Do not run experiments, change implementation, rerun tests, edit historical evidence, consume final entropy, run mutation/panel stages, or advance milestone status. This task is independent review and prospective planning.

## Read first

1. `AGENTS.md`
2. `STATUS.json`
3. `GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R5.md`
4. `research/rrg/CURRENT.md`
5. current audited RRG v0.2.1 README, 04, 07, 08 and foundation ERRATA under `research/rrg/v0.2.1/`
6. `experiments/c6_proposal_r4.md`
7. `experiments/c6_r4_protocol.json`
8. `experiments/c6_manifest.json`
9. `milestones/c6.json`
10. `docs/decisions/0023-c6-r005-performance-interruption.md`
11. `docs/decisions/0024-c6-r006-runtime-stop.md`
12. `docs/decisions/0025-c6-r006-post-stop-engineering-audit.md`
13. `docs/reviews/c6_r006_post_stop_audit_codex.md`
14. `evidence/c6_r6_design_gate/EARLY_STOP.json`
15. `evidence/c6_r006_post_stop_checks/CHECKS.json`

Inspect relevant implementation, native-kernel sources, profiles and preserved raw evidence as needed.

## Authority and interpretation guard

Use the pinned **RRG v0.2.1** source and GeoMind R5 as the forward scientific interpretation. Do not silently fall back to the older v0.2 locked-core reading.

Keep the R5 claim boundaries separate:
- **H-M:** geometry↔mode closure;
- **H-U:** effective-unit formation;
- **H-COMP:** staged recursive composition;
- **H-BG:** a formed structure causally changes a prospectively defined background response;
- **H-PS:** the changed background changes which later states can form/persist;
- **H-RBG:** at least two causally linked background-generation turns;
- **H-PRED:** bounded effective prediction;
- **H-AI/H-EFF:** task usefulness and matched total efficiency.

A runtime repair can restore experimental readiness; it cannot by itself support H-BG, H-PS, H-RBG, H-AI or H-EFF. Staged hierarchy alone does not establish source recursion.

The current R5 experimental anti-cheating rule may require one procedure across repeated tested turns, but RRG itself does not require one identical equation family at every scale. Do not reintroduce that older conflation.

## Recorded situation to verify independently

### R005

Workers each exceeded 15 minutes without completing a full world. Profiles showed active computation with repeated integration/owner overhead, native workspace allocation and repeated deterministic forcing. R005 was interrupted and preserved.

### Performance repair before R006

The implementation:
- batched integration into 10-C0 blocks;
- reused exact independent source/carrier trajectories;
- reused native workspace;
- cached identical deterministic drive vectors.

The scientific equations, probes and thresholds were intended to remain unchanged.

The reserved descriptor fixture — two 24-element cohorts, all 50 probes and three grids — improved from approximately 83.33 s to 4.85 s with numerical differences below 7e-14. Contracts, smoke and an engineering review passed. This fixture demonstrated descriptor-path performance only, not complete-world readiness.

### R006 readiness STOP

Fresh R006 development passed the recorded reference and covariance checks.

Two complete worlds took:
- world 0: 561.151 s;
- world 1: 546.817 s.

The registered projection is:

`max(world_seconds) * 40 / 2 * 1.5 <= 10800`

Therefore every measured world must be at or below 360 s for the registered runtime gate to remain passable.

The attempt stopped prospectively once the gate could no longer pass. Preserve the exact semantics in decision 0024 and `EARLY_STOP.json`.

Scientific diagnostics from the two completed worlds:
- both initially qualified their source;
- neither completed the required two-link chain;
- first-link witness tuple in both was `[true, false, true]`, so intact-only enablement was not demonstrated there;
- turn-2 source qualification was lost at times 315 and 301.

These are **two development observations**, not a population verdict.

### Post-stop engineering audit

The subsequent audit repaired:
- sampled views retaining full integration buffers;
- NaN/overflow cases concealed by numerical maxima;
- concurrent Python cache lookup/eviction races;
- repeated full-channel calculations and large temporary arrays;
- incomplete comparison validation.

It also added worker CPU timing and clarified RSS-measurement limits.

One end-of-batch validation records:
- 79 passing contracts;
- smoke PASS;
- descriptor fixture 6.072 s versus original 83.333 s baseline = 13.724x;
- maximum raw-response difference 6.8834e-14 against 1e-10 tolerance.

The prior 4.851 s observation was faster; therefore do **not** claim that the post-stop batch added another speedup. It establishes current fixture correctness and bounded engineering behavior only.

No complete development world has run with these latest repairs. Independent review is outstanding.

## Remaining gaps

Verify or correct this list:
- complete-world runtime with current implementation is unmeasured;
- source persistence, complete chains and exclusive intact-only enablement remain unproven at population level;
- complete build/reference, serialization/storage/I/O and failed-work costs are not yet fully accounted for;
- automatic early runtime stopping is absent or incomplete;
- current post-stop repairs lack independent review;
- decision 0024 disallows an automatic R007 retry;
- no final entropy, mutation probe or recorded panel exists.

If any item is overstated, unnecessary, already satisfied, or imposed by Codex rather than by owner/R5/protocol, identify it precisely.

# Review tasks

## A — Verify the record

Independently verify the factual claims above from committed sources and evidence. Separate:
1. confirmed engineering defects/fixes;
2. limited observed facts;
3. procedural requirements;
4. scientific requirements from R5/RRG v0.2.1;
5. unsupported assumptions or overconstraints.

Identify any blocker that earlier Codex work overstated or imposed unnecessarily.

## B — Review the latest repairs

Review the post-stop changes for correctness, conflicts, race conditions, memory/lifetime issues, nonfinite behavior, numerical-equivalence risks and evidence-accounting gaps.

Separate:
- **engineering acceptability of the repair batch**;
- **full-world runtime readiness**;
- **scientific readiness of C6**.

Do not collapse them into one verdict.

## C — Find the remaining full-world bottleneck

From current code and existing profiles/raw records, rank the concrete remaining bottlenecks.

Prioritize optimizations that preserve the approved scientific semantics:
- approved equations;
- all registered probes;
- all three-grid checks;
- continuous ancestor/source evolution;
- compute-before-mask law;
- control comparability;
- exact/declared numerical tolerance.

For each proposed optimization state:
- affected functions/files;
- why the work is redundant or avoidable;
- expected asymptotic or measured savings basis;
- semantic risk;
- memory tradeoff;
- how numerical equivalence would be checked;
- what smallest timing measurement would test the expected saving.

Do not solve the problem by merely adding workers or increasing the timeout.

Do not introduce hidden approximations without explicitly classifying them as a prospective protocol/model change.

## D — Optimization or redesign?

Determine whether implementation optimization is plausibly sufficient to get a complete world under the registered 360 s limit with enough margin for the full readiness/panel workload.

If not, distinguish:
- an engineering redesign that preserves the approved protocol;
- a prospective protocol/runtime-budget revision;
- a scientific-model redesign.

Do not tune thresholds, source qualification, chain criteria or controls against the two observed worlds. Do not reinterpret R006.

## E — Smallest useful next diagnostic

Propose **one smallest diagnostic**, but do not run it.

Specify:
- question answered;
- exact code path/workload;
- input fixture or fresh-development entropy policy;
- explicit wall-time cap and automatic stop;
- measurements;
- required numerical/reference comparisons;
- success / stop criteria;
- what result would support engineering-only continuation versus force redesign;
- whether owner approval is required before execution.

Prefer a diagnostic that isolates the full-world hotspot rather than another descriptor-only microbenchmark.

It must not use final entropy or become a disguised partial panel.

## F — Prospective implementation sequence

Give a concrete sequence from current HEAD to the next legally executable revision. At minimum address:
1. independent acceptance or CHANGES_REQUIRED on the post-stop repair batch;
2. any engineering changes;
3. end-of-batch affected contracts/equivalence check;
4. proposed diagnostic, if still useful;
5. owner decision;
6. prospective R007/new revision registration on fresh development/final namespaces;
7. automatic runtime stop before wasting the budget;
8. only then final mutation/panel if readiness passes.

Identify exactly which owner decision authorizes each irreversible step.

Any budget/protocol change must be explicit, prospective and made before new scored evidence.

## G — Attack your own recommendation

Try to falsify your own proposal. Cover at least:
- false-positive speedups from cache warmup or shared-workstation noise;
- changed numerical order that passes loose aggregate checks;
- hidden approximation or compute-before-mask violation;
- memory amplification;
- cache key aliasing/staleness;
- source/carrier reuse that accidentally correlates controls;
- diagnostic selection biased toward favorable worlds;
- thresholds or stop rules informed by the two R006 worlds;
- incomplete cost accounting;
- optimization that makes the 360 s gate pass while making the 40-world panel or serialization impossible;
- scientific overclaim from an engineering success.

# Required review output

Write exactly one review artifact:

`docs/reviews/c6_unblocking_review_claude.md`

It must contain:

1. first-line bounded verdict, such as `ENGINEERING_REPAIR_ACCEPTABLE; C6_STILL_BLOCKED` or `CHANGES_REQUIRED`;
2. `Reviewer family: Claude:<model>`;
3. reviewed repository HEAD/commit;
4. **SHA256 of the exact reviewed `evidence/c6_r006_post_stop_checks/CHECKS.json`**, computed independently;
5. scope and explicit statement that no experiments/tests were run;
6. ranked findings with file/line evidence;
7. a bottleneck table;
8. engineering-optimization versus redesign conclusion;
9. one smallest diagnostic specification;
10. prospective implementation/validation sequence;
11. explicit owner decisions required;
12. yes/no stop conditions with exactly one action and one responsible role per row;
13. self-attack/failure analysis;
14. explicit boundaries: no C6 acceptance, no universal RRG inference, no population claim from the two worlds.

Do not assign a numeric quality score.

## Stop conditions for this review

| Condition | Action | Responsible role |
|---|---|---|
| Required source/evidence identity cannot be verified? | Mark that finding BLOCKED and do not infer from an assumed file. | Reviewer |
| Review requires running code to establish a point? | Specify the prospective diagnostic instead; do not execute it. | Reviewer |
| A proposed optimization changes equations/probes/grids/continuous evolution/compute-before-mask? | Classify it as protocol/model redesign requiring owner approval. | Reviewer |
| A conclusion depends on the two R006 worlds as if they were a population? | Withdraw that conclusion and bound it to those observations. | Reviewer |
| A new development attempt is needed? | Stop at the owner-decision gate. | Reviewer |
| A new budget is recommended? | State the exact prospective rule and rationale; owner decides before new evidence. | Reviewer |

## Owner decision after review

The review should leave the owner a small explicit choice set, not silently choose for them:

- **A. Engineering-only continuation:** approve a bounded implementation repair/optimization that preserves the protocol, then run the approved diagnostic before any new registration.
- **B. Prospective protocol/budget revision:** approve an explicit new budget/protocol before a fresh revision; old R006 remains unchanged.
- **C. Scientific redesign:** change the C6 model/protocol prospectively because engineering optimization is unlikely to be sufficient.
- **D. Pause C6:** preserve the result and work on another milestone/research lane.

The reviewer may recommend one option but must not enact it.
