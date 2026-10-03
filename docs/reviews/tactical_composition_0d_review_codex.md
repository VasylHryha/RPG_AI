CHANGES_REQUIRED
Reviewer family: Codex
SHA256 of reviewed PROPOSAL_0D.md: 32f4697f78e7e9e03a06d335185ae24b829ecedc52bf24beeb114a3f10096594; HEAD: 3084b68b90ad37e806fc3dfdcf4e66c592562189

This is an independent plan review, not approval to execute or acceptance of the historical exploratory results. The central question is worth testing: does separately teaching modules add anything beyond a matched structured policy? The current proposal cannot reliably answer that question or its MOVE-change question. Amend it before seeking owner approval. A smaller Part A should come first; the entire proposed A/B/C batch is premature.

Scope: read AGENTS.md first; inspected decision 0028, corrections, stored per-seed results, shared tooling and tests, proposal, historical specifications/reports, and current source guidance. Ran only the expressly permitted test command, once, with bytecode writes disabled: **28 passed in 14.17 s**. No separate experiment, development script, reproduction script, mutation probe or panel was invoked. Only this review file was written; no commit was made. Test success does not settle experimental validity.

**Owner-requested recheck, 2026-10-03:** reviewed this report against the unchanged source/hash again. Corrected my definite seven-point-grid assertion, an overly broad fresh-approval requirement, and an overly strong interpretation of noisy row thresholds. Added the asymmetric H-struct verdict, explicit missing-value pairing risk, and hand-traced failure examples. Recomputed the eight historical verdicts from stored JSON under their recorded interpretations; they match. The original test pass above belongs to the first review; tests were not repeated. The verdict remains CHANGES_REQUIRED, for the substantive R1–R5 issues rather than documentation nits.

## 1. Required changes before approval, ranked by severity

These requirements apply to the parts retained in the amended plan. For Part A alone, resolve R2/R3/R5/R7 and the applicable precision/cost issues in R8. R1/R4 concern Part B and R6 concerns Part C; removing those parts prospectively removes their run gates. Historical wording fixes and optional improvements do not require additional experimental runs.

### R1 — High: H-change cannot measure a MOVE-only change

**Location:** PROPOSAL_0D.md §2, lines 42–52; §4, line 73; tcd_common/metrics.py:46–76.

The common levels 0.80/0.90 are raw target agreement. B2 leaves targeting unchanged: a controller already above 0.90 AIM agreement can satisfy that level without learning the new MOVE rule. Measuring step error descriptively does not repair a verdict that never requires it. An unchanged controller is an essential negative control here, and must fail the adaptation endpoint.

The proposed reuse of the repaired metric also needs a new-rule interface. Both step functions regenerate labels with `T.teacher_move`; `change_metrics` does not consume `lab['move']`. Passing the normal tactics module would score B2/B3 against the old rule. The optional T parameter could carry an explicit new-rule adapter, but the proposal does not require this and the default is wrong for these changes.

**Fix:** fix the exact B2 rule, B3 rule and affected strata in the approved plan. Define recovery as a conjunction of target quality, movement quality, hold accuracy, and back-off quality, with numerical tolerances and minimum stratum counts. Pass the registered movement teacher explicitly to evaluation. Score an unchanged old controller at n=0; predeclare a minimum change magnitude and require this control to fail recovery in the changed behavior. For B3 count the AIM and MOVE rows together and state their allocation. Test new-rule scoring and the n=0 negative control before the recorded run.

### R2 — High: S1's learning graph is not specified, and teacher forcing can collapse the intended comparison

**Location:** PROPOSAL_0D.md §2, lines 30–31; §3, lines 59–65; §8, line 115.

“Softmax selection” followed by “the model's own selected enemy” has several materially different implementations. A hard argmax/gather provides no ordinary gradient from MOVE to AIM. A soft weighted enemy provides a differentiable route but is not C's hard selected-enemy computation; averaging enemies can produce a feature vector for no actual target. A straight-through route introduces another training assumption. Finite differences of the separate MLPs do not validate the selection route or establish baseline adequacy.

Teacher forcing is a loophole if adopted silently. With the teacher-selected enemy fed to MOVE, disjoint AIM/MOVE parameters and additive component losses, the loss decomposes. A single optimizer then need not make the training materially joint: suitably matched minibatches, normalization and updates can reproduce separate module training. It is a useful control, but cannot be presented as evidence that end-to-end credit assignment was tested.

**Fix:** specify training selection, inference selection, temperature/schedule if relevant, masks, loss terms/weights, gradient path, input features, normalization, and row construction. For the primary C-versus-S1 training-mode comparison, match source states, accessible labels and score/movement supervision masks; reporting unlike row counts alone does not isolate training mode. Keep the historical 3,000+3,000 recipe as a reference if a separate matched-data arm is needed. Identify teacher-forced structured training as separable: if it duplicates C after matching updates, use it as a mechanics/equivalence check, not an additional supposedly independent recorded model. Specify separately an own-selection structured baseline if that is the intended end-to-end test. If soft training uses hard inference, register that mismatch and test it. Require meaningful held-out component/action performance, beyond “loss falling,” and validate gradients through every claimed differentiable route. S1 is a fair architectural baseline only after these choices are fixed.

### R3 — High: margins and verdict definitions still allow incompatible implementations

**Location:** PROPOSAL_0D.md §2, lines 37–40, 50–52; §3, line 64; §4, lines 69–76.

The proposal names E1–E3 for both win score and chance-corrected AIM agreement, but does not say which measure each verdict requires, whether both must pass, or how discordance is handled. AIM agreement alone is not fidelity of the complete target-plus-move controller, particularly for F2's move-head ablation. One numerical margin cannot silently serve both scales. “Better of F1 and F2” could mean selection on development validation, maximum seed score, or maximum aggregate score, and could differ by endpoint. These define different estimands.

The margin is “fixed from the development spread” with only a lower bound of 0.03. There is no formula, spread estimator, upper limit, or owner-defined practical tolerance. A large margin makes equivalence easy and superiority hard; it changes the meaning of H-struct. Fixing this only after examining development comparisons prevents final-panel tuning but does not prevent favorable development-driven definitions.

H-base compares a new paired result with the old Stage 0 gap, rather than a concurrent F0 comparison. The old 0.240 is a win-score gap, not a chance-corrected fidelity gap. Shrinkage versus that constant does not isolate tuning from fresh-seed variation, F2's changed output, or changes to C. H-change lacks a numerical recovery share and a definition of “at every grid value,” despite promising median/interval requirements globally. At the grid floor, comparing C(n) with a control(3n) can demand an unregistered point; at the ceiling it can demand unavailable data. The listed grid starts at 100, while the prose lowers its floor to 30: it must say whether 30 replaces 100 or is added. H-extrap does not define the interval test for “below F1”; being equivalent to S2 does not require either policy to imitate the teacher adequately.

Two hand-calculated examples expose additional verdict gaps; these are logical witnesses, not experimental measurements. With equivalence margin 0.03 and superiority margin 0.06, an E3 median 0.07 and interval [0.001, 0.12] passes the H-struct table's superiority condition but fails line 76 if “interval bound to clear the bar” means lower bound >0.06. Choose one criterion explicitly. If flat=0.60, C=0.70 and S1=0.85 with narrow intervals, E3=0.25 and E2=−0.15: separate versus joint training clearly matters, but H-struct is neither SUPPORTED nor REFUTED because its REFUTED branch recognizes only a C advantage. Add the reverse direction or rename the claim to the narrower hypothesis actually tested. Equivalence is two-sided; failure of equivalence is not evidence that C wins. Also, `median(E1)` cannot be inferred by adding `median(E2)` and `median(E3)`, even though E1=E2+E3 within a seed when the same comparator is used. If the claim is that structure explains an observed C-over-flat gap, require that gap to be observed directly rather than infer it from the other two median endpoints.

**Fix:** write executable decision rules in prose/pseudocode before approval: one estimand per metric, development-only comparator selection or an explicitly registered max statistic, separate fixed practical margins, exact interval inequalities, equality cases, prerequisite gates and an exhaustive INDETERMINATE branch. Include movement in controller fidelity. Compare concurrent C−F0 and C−F1 for H-base; isolate F2's effect separately. Define the recovery share, exact row-cost statistic, censoring when no grid point succeeds, treatment of two failures, and bootstrap/confidence rule for that statistic. Set the complete grid once. Treat clear C-over-S1 and S1-over-C effects symmetrically when rejecting training-mode equivalence. Show that SUPPORTED and REFUTED cannot overlap for any endpoint, and define discordance between fidelity and win score.

### R4 — High: frozen “heads” are not matched to retraining an entire C piece

**Location:** PROPOSAL_0D.md §2, lines 44–48; §8, line 119.

C retrains a complete AIM or MOVE MLP. If a baseline's “head” means only its last affine layer, the baseline gets fewer adaptable parameters and fixed learned features that may not represent the new rule. That does not remove the construction advantage. In S1 the entire shared scorer is already the AIM branch: retraining that branch while freezing MOVE is the most direct matched control. Its final layer alone is a weaker control. Resetting/retraining a head also needs a defined treatment of input/output scaling and optimizer state.

**Fix:** define every trainable tensor and report trainable parameter counts. Add full affected-branch retraining for the structured policy, preserving the other branch, with matched features, labels, initialization and tuning allowance. Retain final-layer controls as additional engineering controls. Include unchanged-policy controls and retention of the unaffected behavior. State whether adaptation starts from old weights or freshly initialized weights for each allowed tensor. Do not interpret a C advantage over a restricted final layer as evidence against matched modular adaptation. B1/B2 are still changes chosen to align with the designed decomposition; a later cross-cutting change would test broader adaptability.

### R5 — High: movement metrics can hide failures and have undefined populations

**Location:** tcd_common/metrics.py:33–43, 56–81; PROPOSAL_0D.md §2 and §5.

When every tied-best label is hold and the prediction moves, none of the branches at lines 70–76 appends an error. Correct holds enter the angle list as zero, while wrong movement on those same states disappears. The denominator therefore depends on correctness. With many accepted holds, a median of these zeros can also hide poor moving-state performance. On mixed hold/move ties a valid move gets hold agreement zero, so the reported angle and hold statistics have different acceptance semantics. `agreement` also divides by zero when all living candidates tie in every multi-enemy state (chance=1); an empty multi-enemy population produces undefined outputs.

For a concrete source trace, take pref=1.2 and two tied living enemies at (1.2,0) and (0,1.2), both inside the teacher's hold band. A predicted step (1,0) makes `moving=[]`, `holds=True`, `predicts_hold=False`: hold agreement is 0, but `step_tiebest_n=0` and no angle is returned. A correct zero step on the same state yields n=1 and angle 0. Thus this is an omission in the angle metric, not a claim that every reported field accepts the wrong move; a separately enforced hold requirement could catch it. No such requirement is fixed in H-change. In the existing mixed-tie test, hold and move are both accepted by angle, while the valid move scores hold agreement 0; the test does not assert that field for the move case.

Tie-best movement can match a different tied target from the one AIM selected. Together with independently successful AIM agreement, this is not necessarily a coherent target-plus-move action. The chosen-target metric should remain visible and participate in any claim about coordinated behavior.

**Fix:** specify disjoint all-hold, moving-only and mixed-tie strata; score every eligible state, including a wrong move on all-hold states, with explicit denominators. Keep moving/back-off angle distributions separate from hold success. Define a joint action criterion that checks movement for the selected admissible target, alongside any forgiving tie-set diagnostic. Explicitly abstain/stop for absent required populations, chance=1, invalid selections or non-finite data. Add hand-computed negative tests for these cases; the existing tests do not cover them. Preserve historical metrics/results unchanged.

### R6 — Medium: real input extrapolation exists, but the gate does not establish model learnability or a fair task

**Location:** PROPOSAL_0D.md §2, lines 54–55; §3, lines 61–63.

Range 8 and preferred range 6.5 exceed the seen maxima 6 and 5; these are real extrapolations in AIM/MOVE features. Speed 0.45 changes world dynamics but is absent from both piece inputs (`tactics.py:203–209`), while F1 sees it (`tactics.py:220–224`). Thus this condition mixes relevant-feature extrapolation with a nuisance-input/dynamics difference between architectures. The record already identified this speed issue in SPECIFICATION.md:118–120.

A scripted teacher beating rush is a task-adequacy gate, not proof that any model can learn the new type. It also permits a nearly trivial/overpowered type. The remaining type stats, mix population and new opponent are unspecified. Combining a new type and opponent in one condition confounds two shifts. A new scripted opponent in the same sandbox does not establish external validity.

**Fix:** fix all type stats/mixes/opponent rules prospectively. Separate type-only, opponent-only and combined conditions, or narrow the claim to the combined shift. Explicitly disclose architecture input differences. Register teacher headroom/nontriviality and stratum coverage checks, and an in-domain-trained-on-new-type positive control on separate development entropy to establish learnability at the planned capacity. Do not train the zero-shot test policies on the held-out type. Register a minimum absolute teacher-fidelity/teacher-relative performance gate; beating F1 alone is insufficient. Replace the MOVE gate's “agreement OR 5 degrees” with criteria covering move, hold and back-off.

### R7 — Medium: tuning, normalization and stop rows need a complete prospective contract

**Location:** PROPOSAL_0D.md §2, lines 27–35; §3; §5–7.

The tuning space, selection objective, development split and number of development seeds are unspecified. “12 trials” does not determine whether C gets 12 joint trials or 12 per piece. F0's recorded recipe conflicts with “every one gets the same tuning budget.” Only F1 explicitly has the 10% parameter constraint, leaving S1/S2/F2 budgets ambiguous. A boundary-triggered space extension adds an unspecified budget. State-level splits can leak correlated trajectory data; independent episodes should define train/validation/test pools.

The ledger omits feature units/scales, learned standardization and its freeze policy, movement output/quantization, bootstrap population, recovery denominators, and wall/CPU seconds. “Time: ticks” covers simulation time but not build/run cost. The stop table has multiple alternative actions (“drop or redesign”), “no” instead of an action, and an owner row about requesting review rather than a concrete experimental stop. It lacks explicit uncommitted-dependency, consumed-latch, invalid-endpoint and inadequate-control gates.

**Fix:** fix tuning domains, total trial budgets, seed/episode splits, model-selection objective, tie-breaking, all parameter constraints and the exact extension rule. Treat F0 as the intentionally untuned reference. Expand the ledger to include input and output scales and actual resource units. Make every stop row a measurable yes/no question with one action and one role. State which development choices and conditional drops the owner's approval delegates. A specifically approved conditional drop of Part C can be recorded and carried out without another approval; redesign beyond the approved alternatives needs an amended plan. State a concrete registration boundary before smoke/final execution. Preserve seed identity when constructing paired endpoints and require a finite value or explicit not-run reason for every planned endpoint; never silently remove different seeds from each comparator. Put the pre-run review before the run in the numbered order; line 108 currently places it last while calling it “before the run.”

### R8 — Medium: power and timing are estimates without a supporting design

**Location:** PROPOSAL_0D.md §2, lines 39–40; §7, lines 106–108; tcd_common/harness.py:111–126.

Thirty seeds can detect a large gap, but that does not establish power for equivalence at 0.03 or for a joint B1/B2 recovery verdict. Under an illustrative continuous normal seed-difference model, a median interval's approximate 95% half-width is `1.96 × 1.253 × SD / sqrt(30)`, about 0.448 SD; with SD=0.10 it exceeds 0.03 even when the true difference is zero. This is a sensitivity calculation, not a measured power result. There are several model/metric/change comparisons, without a multiplicity or gatekeeping policy.

Twenty–forty minutes is plausible as an order-of-magnitude estimate, not verified. The accounting understates the controls: B1/B2 each have C, full F1/S1 and frozen F1/S1, not simply three fits per grid point; the exact grid size is also unresolved. Twelve tuning trials per class and S1 gradient/learning checks have no measured CPU basis. A two-seed smoke on two workers cannot simply be multiplied by 30/2 to predict an eight-worker run unless the worker/config difference is accounted for; a reduced smoke is not a full-size timing sample. Using 30/2 without correcting for more workers may be a conservative stop screen, but is not a realistic wall-time forecast. The shared harness records wall time before evaluation and cancels the watchdog before evaluation, so the quoted time/cap does not cover all work.

**Fix:** prescribe development-based precision/power assessment after fixing practical margins, including equivalence and recovery shares, and choose/freeze seed count before final data. Either register joint gatekeeping or label intervals and individual claims as unadjusted exploratory evidence. Inventory all fits and episode cells, measure representative full-size development costs, account for worker waves/overhead, and fix soft/hard caps and a separate evaluation bound. Record total time through evaluation and receipt writing. If the budget is insufficient, narrow the experiment rather than weaken thresholds.

## 2. Optional improvements

- Prefer a small trusted autodiff implementation for structured baselines if the owner permits dependencies; handwritten backpropagation adds implementation risk unrelated to the hypothesis. A gradient check is useful but not a substitute for a competent baseline.
- Use paired/nested row subsets across models and grid points where their row semantics permit it. Report both unique source states and scalar supervision counts; do not imply equal information from equal row numbers.
- Register an action-space comparison that controls F2's discretization across the structured models, or limit the conclusion to that particular baseline improvement. Report quantization error against the continuous teacher.
- Save trained policies and evaluation state identifiers/digests for new runs. The historical missing models are why repaired movement metrics cannot be recomputed exactly.
- Report all per-opponent/type/behavior strata, including S2. “Structure versus separate teaching” is an engineering question about this policy factorization, not a universal dichotomy about AI architectures.

## 3. Errors and evidence checks in corrections, governance and shared tooling

### Numeric spot-checks against stored per-seed files

These were recomputed read-only from JSON with standard-library arithmetic, without importing project modules. “Recovered” uses the registered historical relative-recovery conditions and first crossing within the stored grid; it does not mean sustained recovery at every later grid point.

The recheck also independently reconstructed the recorded-rule verdict vector: Stage 0 P1–P5 = SUPPORTED, SUPPORTED, INDETERMINATE, SUPPORTED, INDETERMINATE; r2 C1–C3 = SUPPORTED, SUPPORTED, SUPPORTED. The r2 relative half-seed costs are 1,000 versus infinity for C/equal-flat, and the raw-0.80 first-crossing costs are 100 versus 1,000. This corroborates the stored implementation's interpretation; it does not resolve the specification's P5 aggregation or common-level wording ambiguities, nor qualify a new scientific result.

| Claim / location in CORRECTIONS.md | Independent result | Assessment |
|---|---|---|
| C1 median and 55%, line 16 | median 0.6989882623; 11/20 ≤0.70; quartiles 0.6885863 and 0.7100008 | Matches approximately; margin about 0.001012 |
| C1 interquartile range about 0.02, line 16 | 0.02141443 | Matches |
| Equal-size scratch recovery 5/20, line 27 | 5/20; large 0/20 | Matches |
| Equal-size fine-tuning recovery 4/20, line 27 | 4/20; composed 0/20 | Matches |
| Angles at 12,000 rows, line 28 | equal 11.1671792°; large 9.4157640° | Matches |
| Below rush at all six counts, line 29 | equal-minus-teacher medians −0.4875, −0.465625, −0.415625, −0.3625, −0.33125, −0.303125; rush-minus-teacher −0.2125 | Matches the aggregate median reading |
| P5 joint 65%, separate 85%/80%, line 18 | 13/20 jointly; 17/20 teacher bar; 16/20 rush bar | Matches; historical specification wording leaves aggregation ambiguity |
| Composed at 100 rows: 20/20 at 0.80, 14/20 at 0.90, line 26 | 20/20 and 14/20 | Matches |
| Blocks reaching levels within grid, line 26 | equal: 19/20 at 0.80, 2/20 at 0.90; large: 20/20 at 0.80, 3/20 at 0.90 | Equal and 0.90 counts match; large differs if “the block” is meant to include both |
| Unseen per-seed medians, line 34 | C 0.7083333; 4×-rows block 0.7125; 16×-rows block 0.7479167 | Matches |
| r1 CPU, line 36 | SUMMARY.json children_cpu_seconds = 979.695035 | Matches |
| Seen equal-size advantage, line 64 | paired median 0.2395833 | Matches; I did not independently recompute the stated bootstrap interval |
| C2 supporting counts in REPORT_CHANGE2.md:17 | 19/20 recovered at 1,000; corrected medians 0.9673233 versus pre-change 0.9640439; raw 0.9835107 | Matches |

### Additional findings, ranked

**Medium — CORRECTIONS.md:26, 64; evidence/tactical_composition_demo/README.md:12; MOTIVATION.md:38:** “at least ten times fewer” as a statement about an underlying data requirement is not established. The registered half-seed first-crossing grid values are 100 versus 1,000; those tested-grid statistics do have a tenfold ratio. C succeeding at 100 does not establish the assertion that its need is strictly below 100. The equal block was unsuccessful for half the seeds by 300 and successful by 1,000; its untested intermediate requirements are unknown. Even if monotone thresholds were assumed, those brackets would not imply a lower-bound ratio of ten; noisy retraining/crossings do not themselves establish that monotone assumption. Say “a tenfold ratio of registered first-success grid values, with coarse/floor censoring.” The large-block seed_11 value 0.8005628518 at 100 is an additional scope clarification: “never within 100” is correct for the equal block, not for both. I do not label the equal-block-only reading of that sentence a numeric error.

**Medium — unlisted report error, REPORT_CHANGE.md:23:** “No design recovered its own quality” contradicts its own line 13 and stored r1 seeds. The equal-size model recovered in seeds 6, 11, 14 and 16 under that revision's relative rule. CORRECTIONS lists the similar r2 error but not this r1 assertion. Add an additive correction; leave the historical receipt/verdict intact.

**Low — MOTIVATION.md:37:** the corrected trail says “a block 16 times larger on 16 times the data.” Data are 96,000/6,000=16, but parameters are 5,765/787≈7.33 against C (or 5,765/770≈7.49 against the equal flat block). Replace “16 times larger” with the measured parameter count/ratio. This is an error in the corrected narrative, not just in an old report.

**Medium — tcd_common/legacy.py:1–5, 54–77; verify_legacy.py:17–22; LEGACY_EQUIVALENCE.json note; CORRECTIONS.md:55:** the trace does not exercise “every primitive the recorded harnesses call.” It exercises Stage 0-style collection, original labels, datasets, scratch fits and policies. It does not exercise `teacher2_scores`, `aim_dataset`, changed-doctrine fidelity/metrics or `keep_scaling=True` fine-tuning. The r2 comparison also compares the same tactics source bytes to themselves; it is a determinism check, not independent coverage of new behavior. The historical-version comparison and changed-teacher negative control are useful, but the coverage description is overstated. Enumerate exercised paths and omissions, or add meaningful changed-doctrine traces in future authorized work.

**Low — tcd_common/legacy.py:44–51; verify_legacy.py:21:** equality is exact numerical equality, not literal bit equality: `np.array_equal` accepts opposite signed zeros. The field `recovered_hash_matches_run_started` actually checks a six-character hard-coded prefix, not the full recorded hash. I independently retrieved each historical source with `git show` and verified its full SHA256 against the three RUN_STARTED records; all match, and current tactics hashes to the recorded r2 identity. Strengthen the checker or narrow its labels; no actual identity mismatch was found.

**Medium — tcd_common/SEED_REPRODUCTION.json; reproduce_seed.py:21–40; CORRECTIONS.md:55:** the script is a genuine rerun of the harness's own seed computation, not a comparison of the stored file to itself. The recorded counts are consistent with the stored schemas: Stage 0 has 68 keys, excluding five timing keys leaves 63; r2 has 689, excluding nineteen leaves 670. However, the receipt stores no reviewed HEAD, code/spec/input hashes, environment, or fresh values/digest. It reports exact equality of non-timing JSON values for seed 0 only, not bit-identical trained policies, files or all seeds. I did not rerun it, as instructed. Add provenance to future receipts and retain the narrow claim.

**Medium — tcd_common/harness.py:111–126; test_common.py:352–361:** cancelling the watchdog before evaluation is intentional and tested, but leaves evaluation unbounded and omits it from wall_seconds. Do not call this an end-to-end hard cap or total run cost. Add separate bounded evaluation/accounting for new work.

**Medium — tcd_common/stats.py:5–6, 34–36:** `col` independently drops missing/None values, while `paired_median_ci` subtracts positional arrays without checking seed identity or equal lengths. For rows with A=[0.2,None,0.8] and B=[None,0.5,0.8], separate columns become [0.2,0.8] and [0.5,0.8]; the first difference pairs seed 0 with seed 1. A length-one array can also broadcast against a longer array. This is a source-level counterexample, not an executed test; no missing-value mispair was found in the historical records. Construct differences from common explicit seed IDs, reject unexpected missing endpoints, and validate shapes before bootstrapping. Add a negative test in future authorized tooling work. An undefined movement metric must not silently become a dropped seed.

**Low — tcd_common/test_common.py:138–142, 372–391:** the “zero for a random-like pick” test actually asserts −0.5 for a wrong one-state pick. Rename it or test an analytically balanced population. The historical-equivalence test can skip when history is absent, but its separate changed-primitive negative control calls `source_at` without a skip handler; I do not claim the whole suite passes with missing history. Several tests have real negative controls and real temporary git repositories; they are not generally vacuous. Nevertheless none of the passing tests covers R5's all-hold wrong-move omission, chance=1, B2's new movement teacher or missing-value pairing. Bootstrap tests establish basic mechanics, not calibrated coverage/power. Passing 28 tests is not validation of the proposed verdicts.

### Decision 0028 and RRG boundary

Decision 0028:13–15, 34, 52 explicitly identifies the author's readings and unresolved [R] ratification. Line 33 accurately acknowledges the after-r1 change from a 75%-of-seeds C1 rule to a median rule; the source code and r2 spec corroborate it. Decision 0019 does authorize R4 implementation, so 0028:38 correctly points out stale approval language in CURRENT.md. No approval of 0d is asserted.

**Medium governance note — 0028:9, 18, 20, 32:** the opening still declares that authorizations “existed,” and the r2 “ok go ahead” attribution is unqualified, while the evidence provided is the author's transcription without the chat antecedents. Those authorizations cannot be independently authenticated here. Present them as reported messages/interpretations, attach message references if available, and make the ratification list cover any interpretation without a primary record. This is missing corroboration, not proof the owner did not authorize the work. Also, completion of r1 alone is not the AGENTS reason that withdrawal would be unnecessary: the before-independent-review condition is distinct from completion. If this exploratory run was outside that milestone lifecycle, state that scope rationale explicitly rather than deriving it from completion.

The reviewed proposal and decision explicitly disclaim geometry, oscillators, a second composed level and C6 qualification. That boundary is appropriate. I checked actual hashes for current RRG README, 04, 05, 08 and foundation ERRATA against CURRENT.md; they match. RRG 04:14, 34–60, 70–86 and 08:51 require a much richer geometry↔mode/background mechanism than AIM/MOVE MLP wiring. R5 likewise separates H-COMP, H-BG and H-RBG.

**Medium scope note — MOTIVATION.md:25–27, 70–71:** “matches the theory” and “engineering half” are motivating analogies, not demonstrated RRG links. The future RRG-specific item names compatible pieces/stable combinations but omits causal background transformation and later organization in the transformed background. State explicitly that none of H-M/H-COMP/H-BG/H-PS/H-RBG is tested here and that a future source-aligned experiment must specify the relevant causal links. Calling ordinary modules “shapes” does not establish AI as geometry. Positive 0d results could establish bounded imitation/adaptation behavior only.

## 4. What I could not verify

- Original owner chat messages, their antecedents, chronology and whether particular specifications were approved. Repository quotations are secondary records.
- Fresh seed reproduction, all-seed determinism, actual trained-policy identity, or repaired metrics on historical runs. Reproduction/harness execution was prohibited; historical models were not stored.
- The author's claim about how the earlier self-audit was performed. This recheck independently reconstructed all eight cited Stage 0/r2 verdicts under the recorded implementation's interpretation and verified the listed numeric examples; it did not authenticate that audit's procedure or remove the specification's P5/common-level ambiguity.
- Stated bootstrap confidence limits, full calibration history or test-frequency compliance. I did not execute development code or reconstruct every prior session.
- Runtime, learning quality or power of unimplemented 0d models. There is no implemented gradient route or fixed manifest to audit yet.
- Complete current-release checksum inventory or the outer archive. Selected source bytes and current guidance were checked, not a fresh full import audit.

## 5. Recommended order of next steps

1. **Drafter:** correct the additive narrative errors and amend this proposal/self-audit with causes and fixes. **Owner:** approve a specific amended prospective plan. Historical ratification is a separate governance choice, not an automatic prerequisite for a newly explicit prospective authorization. Do not treat this review as execution authorization.
2. Run a **narrow Part A** after approval: concurrent F0/F1, a competent matched structured policy with explicit own-selection training, and C with matched supervision for the main training-mode comparison. Use the teacher-forced/separable case as a mechanics reference; avoid an additional recorded arm if it is mathematically and operationally identical to C. Use fixed practical margins, adequate component/action metrics and saved policies. F2/S2 can remain if they have a defined role and budget; L need not be retrained merely to repeat a historical reference. If S1 matches or beats C, report that training-mode result directly; it does not invalidate modular architecture or justify tuning until C wins.
3. Add **B1/B2** only with R1/R4/R5 resolved: unchanged negative controls, full affected-branch adaptation, movement-aware recovery and retention tests. Treat B3 as a separate total-budget test. Equivalence between C and a structured modular baseline is an informative result, not a reason to redesign until C wins.
4. If useful modular behavior survives competent controls, test **learning from outcomes** next. This directly addresses the present teacher-graph confound. A narrowed external task/benchmark should accompany the first broader usefulness claim; a new opponent alone is insufficient.
5. Test **squad composition** after units have demonstrated learned useful behavior and clear interfaces. Otherwise the squad risks adding another layer of hand-written decomposition without addressing the current limitation.
6. Keep any **RRG/AI-as-geometry experiment separate**, with its own source-aligned causal hypothesis and owner-approved lifecycle. Neither this sandbox nor its expansion automatically unblocks C6.
