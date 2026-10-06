CHANGES_REQUIRED

Codex (GPT-6), 2026-10-06. Owner-requested implementer recheck of the retained revision-5.1 development run, imported at `a9cbe83fc0400362a43669f00770bccfc3ec7422` (formerly `7e5f6b0`; history map in `docs/HISTORY_CLEANUP_2026-10-06_MAP.tsv`). This disposition concerns the next design and delivery gaps. The recorded run keeps both arms’ G0 INCONCLUSIVE, G0′ FAIL, G1 PASS, G1c DESCRIPTIVE and G5 PASS. It is not a new independent review, revised experimental verdict, acceptance or authorization to execute revision 6.

The readout layout explains the constant final score. The evidence also contradicts two stronger readings in Claude’s review/draft: some evaluated snapshots do respond and exceed both comparison baselines; an empty readout in a saved template does not prove abstention throughout its subsequent moving evaluation copy. Revision 6 needs an informative causal task endpoint, beyond putting an element at the output.

**1. The whole-medium constant and abstention**

[ANALYSIS.json](recheck_20261006/full/ANALYSIS.json) independently checks every retained policy’s final template, competence, copy identities, all snapshot hashes and the source closure. The four identical intact scores are:

| Task | Normalized default score | Oriented raw mean reconstructed with unchanged calibration | Final evaluation abstention rate |
|---|---:|---:|---|
| perceive | 0.004953791662960241 | −1.5579175080472514 rad | Not retained; default scores are compatible with 128/128 episodes entirely abstaining in each of the 30 floor policies |
| move | −0.0329161871079006 | −4.718976980279208 goal-error units | Not retained; same limitation |
| remember_static | −0.1074982787726681 | −1.7413763848024941 rad | Not retained; same limitation |
| choose | 0.22313598154947953 | 0.375 correct-choice rate | Not retained; same limitation |

Their arithmetic mean is exactly `0.021918826832967767`. All 16 intact final templates and 14 controls have zero elements at radius strictly below 2, so their saved-state Σw and coherence are exactly zero. The minimum intact final radius across seeds is 3.4702829560944477. The other two controls contain readout members: task_blind 106062 has 15; reward 106077 has one. Both have different scores on every task. The claim that **all 32 final policies abstain in every episode is refuted**.

The dominant explanation for the other 30 is an empty output, rather than cancellation among 44 mixed phases: no element contributes to that saved-state resultant. `protocol.action` and `perf.cpp:Engine::action` agree on the default: zero angle/magnitude for the non-choice tasks, lowest visible live ID for choose. The latter is an active deterministic decision. The world deliberately places the first two IDs in range on some choose episodes, so the lowest-ID default is already above random. A positive choose score alone cannot credit a structure.

An exact per-task episode abstention rate for the 30 policies **cannot be independently certified from the stored artifacts**. `Evaluator.evaluate` stores only each task’s 128-episode mean; its per-episode score list is discarded. The native evaluator returns an index, and `copy_instances` records identities rather than coherence/actions. Training event/drive ledgers do not supply evaluation traces. Copies integrate for five RK4 substeps before their first action and positions continue evolving for 16 seconds. Thus saved-state emptiness and equal aggregate scores strongly support the explanation but do not measure every later action. No missing rate is manufactured and no episode is rerun.

**2. Why the two G1c means duplicate**

For task_blind 106065 and reward 106076, every one of their 20 recorded `move` scores equals −0.0329161871079006 and every `remember_static` score equals −0.1074982787726681. Averaging the same constants produces identical means. All 40 saved templates start with an empty readout; their template-hash sets are disjoint. There is no shared template/artifact explanation.

The explanation does not extend to all their task scores. Task_blind 106065 snapshot index 2 has perceive 0.004547844120470128. Reward 106076 indices 0, 2, 11 and 14 have non-floor perceive scores, and index 0 also has choose 0.2191909689557855. Claude’s addendum statement that all 20 snapshots scored the same constant on every task is therefore too strong. The scored copy moved into readout reach in at least some of these evaluations; empty initial geometry is insufficient to classify an entire episode.

**3. D1–D3 and other reasons the output was uninformative**

| Finding | Evidence and assessment |
|---|---|
| D1: late-rejection clause at saturated budget | Correct for this run. All 16 intact slopes are inside ±0.5 per 100 episodes, no protected-over-budget state is reported, and every intact seed has late cost rejections. Independent ledger extraction finds **7,481 late rejections, all reason `cost`**, with no late `cap` or `placement` rejection. The count range over the late window is 42–45 across all policies. The clause answers whether demand ever exceeds capacity, rather than whether the count trend settles. It is not a theorem that every population at the cap must reject: a fully covered population may make no birth request. |
| D2: dropped controls prevent G0 PASS | Correct for every seed in this run. There are **775 drops, all reason `cost`**, no terminal or placement drops; 1,670 intact births become 895 control additions. Each seed’s addition ratio is only 0.264–0.711. All 16 controls are flagged. The original two-attempt queue permits zero drops in principle; it is not universally incapable of PASS. |
| D3: one global readout for competence | Correct as a task-attribution problem, with an important correction: **G1c does not read at each structure’s centre**. Sections 7–8 and `copy_template` retain absolute positions and the same origin readout. It isolates a group but gives it no new output port. A single global endpoint could still be valid for a explicitly grown input–output controller; isolation alone does not solve the layout mismatch. |
| Disconnection and drift | Only **500/11,862** snapshots have a readout member at copy time; only **99/320** evaluated snapshots do. **9,493/11,862** have no member within drive reach of any of the eight sensor sites at their check time, even allowing every site to be active. Intact final radii reach 245.89738284482542; a control reaches 420.3490509488179. The draft’s upper radius “about 9” is incorrect. The law has moving geometry and no arena confinement; internally locked groups can survive D1 while drifting away from both sensing and action. This is not an implementation violation of the specified law. |
| Vacuous G5 successes | **208/320** evaluated snapshots have all four scores at the floor. G5’s carrier-shift covariance can pass for a silent/default policy. Its existing PASS is a numerical check, not usefulness. |
| Weak functional evidence | Some scores exceed the default, but no per-episode differences, uncertainty, untrained-template comparator, input-scrambling intervention or coupling/output ablation were retained for G1c. The first-20 cap heavily samples early structures; the other 11,542 have no recorded task evaluation. Repeated snapshots of evolving groups and best-task selection are not independent task-success observations. |
| Task metric limits | `oriented(perceive)` uses angular error only, although the world also records distance error. It cannot certify distance decoding. A single global resultant also mixes item phases while perceive targets the nearest item. Coherence alone supplies neither item identity nor proof of memory; the stationary memory task needs evidence that hidden-period output depends on prior visible input. These are endpoint/architecture limitations, not grounds to replace the recorded scores. |

[LEDGER_CHECKS.json](recheck_20261006/full/LEDGER_CHECKS.json) supplies every archive’s checked decoded identity and per-policy event/rejection/drop counts. [SNAPSHOTS.csv](recheck_20261006/full/SNAPSHOTS.csv) supplies every snapshot’s geometry and the existing G1c values where available. Empty score cells mean not evaluated, not failure or abstention.

**4. Descriptive task use among the retained snapshots**

There are 11,862 admitted snapshots, but **only 320 were evaluated** under the declared cap. The following counts use those 320 existing scores. “Random” first means n=0 under the frozen validation-0–255 calibration. The additional same-panel comparator uses the already stored random-policy rows 0–127, with the original 256-row normalization unchanged. No calibration was refit and no policy was run.

| Task | Mean n | Range n | Above / equal / below floor | Above calibrated random (0) | Above same-panel random | Above floor AND either random comparator |
|---|---:|---|---|---:|---:|---:|
| perceive | 0.0084991903 | −0.0296131374 … 0.1113311252 | 64 / 210 / 46 | 282 | 290 | 64 |
| move | −0.4209451534 | −1.7123718899 … −0.0329161871 | 0 / 220 / 100 | 0 | 221 | 0 |
| remember_static | −0.0722639410 | −0.1129885906 … 0.1329688898 | 96 / 221 / 3 | 51 | 51 | 51 |
| choose | 0.1606268777 | −0.0365672321 … 0.2264740691 | 1 / 218 / 101 | 305 | 300 | 1 |

Comparisons use absolute tolerance 1e-12 and leave raw scores unchanged. The same-panel random means in normalized units are respectively −0.0043020277, −0.0411184632, 0.0001868360 and 0.0070706764. In particular, 221 move scores beating that sampled random baseline does not mean useful movement: **none beats doing nothing**. Details and input hashes are in [SAME_PANEL_RANDOM.json](recheck_20261006/SAME_PANEL_RANDOM.json).

The single above-floor choose snapshot is task_blind 106066 index 5, type `d0687085803384ba650b496cba24840d942c592e6d4597b48b203d69b023bc35`, check/admission times 900/960 s. Its n=0.22647406912875911 improves the oriented choice rate from 0.375 to 0.377685546875. It initially has **no** readout member (minimum radius 2.369016433103596). Overall, **13 initially empty evaluated templates** have at least one non-floor score. These are direct counterexamples to inferring evaluation-long silence from initial emptiness.

The retained diagnostic replays provide actual frame-level evidence, excluded from the recorded readouts: task_blind’s choose replay abstains on **160/160 frames**, while reward’s remember_static replay abstains on **0/160**, with coherence 0.999999991470826–0.9999999999504902. These two extra episodes do not estimate the main panel’s abstention rates.

There is limited descriptive above-baseline response in perceive and stationary memory, and one tiny choice improvement. No positive move result is present. These counts do not establish statistically reliable task use, learned competence, superiority or new verdicts. For the unscored 11,542 snapshots, task use is unknown.

**5. Accounting correction**

`RESULTS.json:wall_seconds` is **7,410.865621166 awake monotonic seconds = 2.058573783657 hours** on this host. It excludes suspended time; it is neither calendar elapsed duration nor CPU time. The owner/review identifies host idle sleep during 01:24–08:00 local, including dark wakes. Do not add that whole interval to the awake duration as if all of it were suspended. The result receipt records completion at 05:23:25 UTC / 08:23:25 local; the review’s approximately 08:37 end refers to later delivery work. Exact calendar start/end and suspend counters were not both retained, so exact full-run elapsed duration cannot be recovered. An approximately 00:50 start would imply about 7 h 33 min to the result timestamp, explicitly an estimate.

Full-run summed worker awake stage times: training 9.527520 h, qualification 1.452260 h, recovery 1.388933 h, evaluation 2.367408 h; total **14.736121 worker hours** under parallel contention. The one-seed projection remains 11.402521 serial hours, not an isolated CPU benchmark or elapsed-time guarantee. The cost seed’s legacy `wall_seconds` likewise means awake monotonic seconds (415.407179792). All historical fields and values remain byte-identical.

| Exposure source | Training episodes | Evaluator/diagnostic episodes | Separate calibration episodes |
|---|---:|---:|---:|
| Full 32 policies | 64,000 | 344,064 | 0 |
| Cost seed | 200 | 14,848 | 0 |
| Two exported replays | 0 | 2 | 0 |
| Frozen four tasks × reference/random × 256 | 0 | 0 | 2,048 |

The full-run training exposure is 10,240,000 steps, qualification 5,115,712 frames, recovery 1,440,960 simulated seconds, and reward 32,000 episodes. The full evaluator count includes both offsets for each of the 320 snapshots and the 32 final whole-medium templates. Coefficient/scalar counts are state accounting, not RAM or efficiency measurements. The report and historical delivery note now say awake monotonic time. The report’s erroneous instruction to mark a valid G0′ FAIL as INVALID was corrected to “write the failure report and stop”; the actual FAIL verdict stays unchanged.

**6. Remaining runner and delivery gaps**

The source audit covered the Python orchestration, native bindings/evaluator/RK4/readout, growth/control rules, qualification/recovery adapter, aggregation and delivery scripts, plus the prior implementation/performance reviews. The 37 retained source/harness hash checks match, pre/post source and build identities agree, and all 59 non-ledger entries in ARTIFACTS match bytes/hashes. All **66 ledgers** also match compressed identities and decoded hashes/bytes/record counts: **59,322,474,661 decoded bytes and 22,175,556 records**. The complete horizons, first-20 order, template hashes, copy task/episode/offset identities and stored G1c-to-UNIT-to-RESULTS correspondence were checked without recomputing a verdict. No new engine-law or scorer mismatch was found in this bounded audit. Native libraries were not loaded, rebuilt or replayed; prior equivalence evidence remains prior evidence, not a new full-horizon equivalence run.

Specific unresolved engineering issues for the next implementation:

- `development.execute_arm` passes receipt-bearing reports directly to `seed_unit`, which expects iterable event rows. With the required `audit_root`, this dormant driver can fail aggregation. The actually used `section10.pair` wraps reports in `LedgerView` and avoids that bug. Unify receipt-aware aggregation in the next revision; do not rerun the old driver.
- `section10.summarize()` is not a read-only report command: it executes two replay episodes and rewrites STAGE_TOTALS, replays and ARTIFACTS. Use the new offline tools for rechecks. Future report generation must have no simulation or immutable-receipt writes.
- `section10.identity()` references the pre-cleanup review SHA `6bdc82e`. The current map records its rewritten merge as `770b135a46b648201000529133c11451ff595dde`. Preserve the old run identity; explicitly map history references in a future driver rather than bypassing the source guard.
- The old `bundle_development.py` stages all output files, including the raw ledgers, and produced a 13.846 GB bundle. The old bundle remains historical and is unsuitable for this delivery. The new bundle uses an explicit whitelist and excludes every raw event/drive ledger.
- Recovery events repeat the complete native state plus 601 frames. This caused 13,952,315,481 compressed bytes across 66 archives (59.322 GB decoded). Future delivery needs bounded chunks below 50 MB, an ordered/hash-bound index and lossless content-addressed state/frame references; do not discard recovery provenance or silently downsample.
- Peak RSS, isolated serial CPU cost, disk headroom and exact calendar/suspend timing were not measured. Native failure recovery is nontransactional and resume is unsupported. These remain delivery/runtime limits; no crash recovery, portability or optimal-throughput claim is made.

Only report prose/accounting and new offline analysis/testing/delivery tooling were changed. DESIGN_0H, the revision-6 draft, runner/engine law, training schedule, calibration, all historical receipts, raw ledgers and STATUS are untouched. Unrelated `evidence/c6_option_b/quiet_session/` is preserved.

**7. Concrete review of R6-1–R6-4 for Claude’s revision**

| Draft change | Required refinement before a next run |
|---|---|
| R6-1 | Classifying cap/cost limitation separately from count trend is justified. Register exact classification/aggregation and keep placement and protected-budget errors distinct. Report late count range/variation, turnover, birth demand, rejection rates, cost and uncovered exposure; a flat slope alone can hide churn. Do not call a cost-limited population self-limited or autonomously stable. |
| R6-2 | Retaining requests avoids the artificial two-attempt loss, but cannot create feasible capacity. A head can block the FIFO until the horizon; a ≥0.9 additions rule would flag **all current seeds**. Define redraw/attempt/horizon semantics and what the comparison means when counts differ. Check feasibility on separately authorized engineering fixtures before launch. Choose explicitly between comparing two budget-constrained policies with differing realized births, and an actually matched birth-exposure experiment. Matching only total additions does not match birth timing, deaths, ages or sensor exposure. Do not filter or replace development seeds until a result passes. |
| R6-3 | The pending output mechanism is the main unresolved gate. B-out at the origin guarantees neither input reach nor a learned transformation: sensors at radius 4 have drive reach 3, so an origin element receives no direct drive. A bridge needs an actual directed-neighbour coupling path that persists while geometry evolves, legal binding across site permutations, and an output decoder whose task endpoint can beat the default. Alternatively specify structure-relative sensing/output ports, anchoring/pose and a library routing rule learned/selected outside the evaluation panel. Current G1c is not already such an implementation. A sole output oscillator, an echo or fixed-ID default must be unable to satisfy the intended task-use endpoint. |
| R6-4 | Retain awake, UTC start/end, continuous elapsed/suspend accounting, host power-inhibition status and stage/worker identity separately. Use the proposed power wrapper for unattended runs. Keep raw ledgers outside git with individually bounded chunks. A path-exists stop row must include an action, responsible role and observable pass/fail criterion. The proposed 50-episode smoke exceeds the current 1–10 CLI cap and is not authorized by this recheck; include it in the new approval. “Σw > 0 at some time” is insufficient: test after warmup and across all four tasks/permutations and hidden intervals, check non-default output and causal response, and detect disconnection over the run. |

Recommended next-run endpoint: preregister per-task oriented scores and paired differences against **both** default/abstention and random, uncertainty at the declared independent unit, action/readout exposure and an untrained or appropriate fixed-medium comparator. Add evaluator-side interventions that break input information, coupling paths or the output structure, with expected direction stated before execution; for memory, distinguish visible encoding from hidden retention. Record per-episode scores and compact per-step Σw, coherence, output/member identities and decoded actions. Keep the task-blind arm’s growth/admission free of task-score feedback. Freeze a routing/readout procedure without using evaluator outcomes to choose winners; reserve fresh evaluation evidence for any stronger claim. Structural qualification and numerical carrier covariance remain separate from task use and RRG/background claims.

Claude owns the design fixes and their self-audit. Owner approval of a concrete revision and its engineering checks precedes new execution. Nothing in this recheck changes the old measurements or supplies that approval.

**8. Reproduction and validation**

From the repository root, the offline audit and same-panel comparison can write to new directories:

```sh
python3 evidence/tactical_composition_demo/growing_shapes/runner/recheck_development.py --ledgers --output evidence/tactical_composition_demo/growing_shapes/runner/recheck_20261006/reproduction
python3 -m evidence.tactical_composition_demo.growing_shapes.runner.recheck_validation_chance --analysis-dir evidence/tactical_composition_demo/growing_shapes/runner/recheck_20261006/reproduction --output evidence/tactical_composition_demo/growing_shapes/runner/recheck_20261006/reproduction/SAME_PANEL_RANDOM.json
```

Each output refuses an existing target and any write inside the historical receipt tree. The first command can omit `--ledgers` for the small-artifact analysis, explicitly labelled inventory/size/receipt-mapping verification only. Existing full ledger verification need not be repeated. [ANALYSIS_LOG.txt](recheck_20261006/ANALYSIS_LOG.txt) records this session’s complete scan. The additional chance tool’s first attempt stopped before writing output because a relative input path could not be made relative to the absolute runner directory; resolving that input path fixed it, and the bounded retry succeeded. That failed attempt is not counted as a test pass.

The six focused offline fixture tests passed once (pytest 0.04 s; subprocess awake duration 0.205 s). A later packaging whitespace check rejected the generated CSV’s CRLF terminators; only the exporter terminator and new CSV formatting were changed to LF, with a byte comparison proving identical content after newline conversion. The same-panel input hash was refreshed. The unchanged analysis fixtures were not rerun for that formatting-only correction. The first packaging attempt is retained separately in DELIVERY_ATTEMPT_1_LOG.txt; no commit was made in that attempt. Scoped hook/bundle verification and test records are recorded in [TESTS.json](recheck_20261006/TESTS.json) and [DEVELOPMENT_RECHECK_DELIVERY.md](DEVELOPMENT_RECHECK_DELIVERY.md). No training, new seeds, judging entropy, recorded panel or mutation probe was run.
