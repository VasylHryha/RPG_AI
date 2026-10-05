CHANGES_REQUIRED
Reviewer family: Codex
Reviewed DESIGN_0H.md SHA256: 83a571a88dcb83592ebfce7f0d5d72fcec904855bf0eb4c904d3a37ee1e1dfa3

Reviewed document: `evidence/tactical_composition_demo/DESIGN_0H.md`, revision 4, commit `69cc18c64a5b14362c44b509d1f0cb2d47e1c559`. The working document matched that commit byte-for-byte. Checkout at review start: the same commit. Date: 2026-10-05. Scope: documentation/source re-review within the requested approximately 20-minute cap. No project code or experiments were run.

Revision 4 repairs the detector frame count and finite qualification horizon, specifies complete recovery populations and saved templates, and makes valid reductions of the driven-atom, control and budget claims. Several active instructions still conflict or leave an execution choice open. Section 14 should distinguish those partial repairs from completed ones. The required fixes belong to the drafter; this review changes neither the design nor either READY engine.

## Disposition of R3-1 through R3-10

“Resolved” means resolved as a design contract within the stated bootstrap scope, without experimental verification or milestone acceptance.

| Prior finding | Disposition | Revision-4 evidence |
|---|---|---|
| R3-1: frozen-function frame count | Resolved | Lines 168-169 require 601 endpoint-inclusive frames, immutable ids and a fewer-than-three disposition. This fits `c4_detect.window_statistics` indexing and two exact 30-second halves. The first window requires retaining the initial t=0 state. |
| R3-2: sampling, gain, coverage, eligibility | Partial | Lines 103-109 supply exact rate endpoints, warm-up, exposure, newborn eligibility and clipping. The no-drive gain rule contradicts line 123, and the current-sample boundary is still not explicit (R4-1). |
| R3-3: recovery population, replay and snapshot provenance | Resolved in document scope | Lines 182-198 save all live elements and coefficients, retain entrants in dynamics, label membership cohort-restricted, admit the saved check-time template, preserve it after source death, replay the assigned drive on the original clock, and define aligned relaxation measurements/censoring. The existing planned engine follow-up is noted in R4-2. |
| R3-4: move observation binding | Core binding resolved; site-map consistency remains | Lines 54-65 explicitly encode the legal move target/range fields, retreat, stationary memory and non-choice `choice=-1`. The per-task table, general permutation and serialized bindings still need one interpretation (R4-3). |
| R3-5: run duration and pending terminal qualification | Resolved for duration/recovery horizon | Lines 252-254 correctly give 32,000 seconds and qualification starts through 31,920, completing by 31,980. The new fixed four-task rotation conflicts with possible task exclusion (R4-5); control retries have a separate terminal gap (R4-4). |
| R3-6: G0 coverage/control matching | Partial, with valid claim reduction | Line 268 excludes zero-active-site samples, reports exposure, makes no eligible exposure INVALID, narrows to two budget-constrained policies, and prevents dropped-control seeds from contributing to PASS. Retry execution and entropy remain incomplete (R4-4). |
| R3-7: D3-forced settling | Resolved by narrowed claim | Lines 269 and 290 explicitly test count stability under the budget and report D3 regulation. This permits budget-regulated stability without claiming unrestricted settling. |
| R3-8: G5 aggregation/copy identity | Partial | Lines 212-214 and 272 define ordered members, a scalar D, fixed offsets, fresh copies and no formation. Section 8 still specifies a different copy lifecycle, and the small qualifying-seed case has overlapping verdict rules (R4-6, R4-7). Bindings also need R4-3. |
| R3-9: common-drive recovery versus closure | Resolved by narrowed claim | Line 22 calls atoms structurally qualified driven snapshots and explicitly withholds internal closure/autonomous-persistence claims. Background, composition and efficiency deferrals remain valid. |
| R3-10: false rate bound | Resolved as a correction of the rationale | Line 170 removes the false bound, retains the earlier negative contract and calls the added screen “possibly aliased.” It supplies no universal sampling guarantee; retain that limit (R4-9). |

## Numbered findings and fixes

1. **R4-1 — High: the no-drive gain update still has two contradictory results.**

   Evidence: design lines 103-124. The new sampling contract says that P is undefined and g is unchanged when no drive reaches an element. The adaptation equation still says P=0 in that case and applies `dg/dt = 0.05 (P-g)`. With g=1 and dt=0.1, these give respectively 1 and 0.995. Hidden memory intervals make this a routine case, so the difference changes subsequent dynamics and copies.

   The contract also defines a sample at the post-integration timestamp, but adaptation precedes appending that sample. “Has 101 samples” and “last 100” do not specify whether the current, not-yet-appended endpoint is included in P, its eligibility test and the rate estimate. This leaves an avoidable one-step distinction between adaptation and the subsequent coverage/timer update.

   **Fix:** choose one no-drive rule and remove the incompatible clause. Give one indexed update contract specifying the retained initial endpoint, which last-100 timestamps enter PLV/exposure, whether the current endpoint is included before storage, and the site phase paired with each element phase. Use that convention for gain, coverage, lock and episodic eligibility, with the already declared different warm-up thresholds where intended. Retain the clipping and newborn mean/zero rules.

2. **R4-2 — Low implementation dependency note: preserve the planned medium follow-up separately from current engine readiness.**

   Evidence: design lines 12-13, 69, 99-100, 113, 122-129 and 183; `growing_shapes/medium/medium_c.h:11-16,32-45`; `medium.cpp:84-102`; `MEDIUM_REPORT.md:37-60,89-91`. The built engine stores a natural rate per element, but no g field. Its RHS adds each site's shared strength to every element in reach. A shared site strength cannot supply the design's different `g_i` multipliers after adaptation/reward. Updating g in an external table alone leaves the native `gm_step` dynamics unchanged. Applying a phase correction after native RK4 would define a different integrator from RK4 of the full driven RHS.

   Its other helpers also have declared engine conventions: histories are recorded after every native integration step, a drive-strength change invalidates its old PLV samples, and cost counts directed element and external-drive links. Those differ from this design's world-step histories, continuously carried site histories and undirected internal-pair budget. Engine readiness therefore cannot stand in for complete 0h implementation readiness.

   `growing_shapes_review_claude/MEDIUM_REVIEW.md` already identifies the gain, coverage, eligibility, cost and placement gaps, and explicitly schedules one follow-up batch after the design passes review. It separately assigns adaptation, driven qualification, copies and task bindings to the runner. That is an existing engineering plan, so this is **not a new design blocker** and does not require implementing it before design approval.

   **Fix:** reference that bounded follow-up in the dependency/stop contract, preserving the distinction between the reviewed engine and the completed design-specific integration. The eventual batch must also account for world-step sampling and carried active-site histories, including changing strength. Preserve the full driven RK4 law, gain snapshot state and design-specific budget/events when closing it. No engine work is authorized by this review; the separate owner go-ahead remains required for section 10.

3. **R4-3 — Medium: input-site assignment and template bindings still describe different mappings.**

   Evidence: lines 51, 58-61, 73-76 and 208-214. The general rule permutes every episode's items onto sites using its seed; the new move and memory rows explicitly use site 0. It is unclear whether that is a logical slot subsequently permuted or a fixed physical site exempt from the general rule. The general strength block also retains the enemy-distance formula without stating that the move row overrides it.

   Templates first store a slot-to-site **rule**, then serialize one concrete eight-index `slot_sites` list per task. A fixed list does not encode an episode-seeded permutation rule. Training and both evaluator copies need the same declared binding procedure, including the single-item tasks; storing the last training episode's mapping would give a different procedure.

   **Fix:** state explicitly which table fields are logical slots and which are physical sites, which tasks use the permutation, and that the per-task strength formulas govern. Serialize the binding rule/version and its parameters, or specify how a canonical base list generates the episode-seeded mapping. Apply the same rule to the paired evaluation copies and record realized assignments in replay. Preserve the legal move/action binding already added.

4. **R4-4 — High: the narrowed G0 control still has an undefined retry queue and terminal future.**

   Evidence: lines 152-163, 252-254 and 268. At each growth check the control attempts as many births as the intact run made, and an infeasible birth is retried at the next check. If two retries meet two new requests at one check, the text does not specify their priority or whether the at-most-two limit applies to attempts, successful additions or each category separately. That changes cost, accepted births and which requests are dropped. The control's phase distribution, shared versus separate entropy streams and whether retry placement is redrawn are also not fully specified by “phase from a paired entropy stream.”

   The last growth check can occur at t=32,000. A failed control birth then calls for a retry at 32,020, beyond the reported horizon. No terminal-drop or continuation rule resolves this. Fixing qualification's future does not fix the control's future, and the eventual dropped/pending distinction affects G0's non-PASS and incomplete-run dispositions.

   **Fix:** define a finite ordered control-request queue, its relationship to the intact birth requests and autonomous B1, the feasibility/separation test, the per-check attempt/addition limit, retry draw rule, phase distribution and paired entropy domains. Choose a terminal rule in advance, such as dropping/logging requests whose retry lies beyond the horizon and applying the existing non-PASS flag. Report the narrowed policy comparison with actual additions, deaths, retries and drops. Matched birth counts/times need not be restored under the accepted claim reduction.

5. **R4-5 — Medium: the fixed rotation does not implement the frozen usable-task list.**

   Evidence: lines 240-245, 247 and 253. Screening can remove any of the four tasks; the only stop is an entirely empty list. Revision 4 then fixes the training rotation to all four task names. An excluded task can consequently be trained and used for reward despite its normalization denominator failing the declared qualification. Revision 3 instead rotated usable tasks.

   **Fix:** filter the fixed order through the frozen usable list before making the 20-episode blocks, or explicitly require all four tasks to pass screening and stop otherwise. Keep the same resulting schedule in both arms and their paired controls, with the declared 2,000-episode horizon.

6. **R4-6 — Medium: section 8 retains the copy lifecycle that section 7 replaced.**

   Evidence: lines 214, 220-221 and 272. Section 7 and G5 require a fresh isolated copy for every evaluation episode. Section 8 says each snapshot is copied once and run on each task's panel in its own copy. Carrying a copy's positions/phases across 128 episodes measures a different controller from re-instantiating its saved template each episode. G0 whole-medium competence and G1c both refer to that evaluator, so this discrepancy extends beyond G5.

   **Fix:** rewrite section 8 to use the new per-episode reset consistently for snapshot and final whole-medium evaluation. Pin the primary competence copy's carrier offset and identify the two G5 offsets with the same panel/assignment procedure. Retain empty-readout abstentions as scored episodes. No absolute competence-retention threshold is needed for the narrowed G5 claim.

7. **R4-7 — Medium: G5's fewer-than-six-seed case can receive two verdicts.**

   Evidence: line 272. FAIL requires a snapshot-pass fraction below 0.5 in at least three seeds with snapshots; INCONCLUSIVE also applies whenever fewer than six seeds have snapshots. For five seeds with snapshots all having fraction zero, both conditions hold. There is no stated precedence. The scalar D, fraction aggregation and no-formation disposition otherwise repair the old undefined median.

   **Fix:** write an ordered truth table: INVALID for the declared execution/measurement failures; then, if intended, fewer than six snapshot-bearing seeds means INCONCLUSIVE; then apply the PASS/FAIL cuts to the remaining cases; otherwise INCONCLUSIVE. Alternatively allow FAIL on three poor snapshot-bearing seeds regardless of total formation, and remove the conflicting INCONCLUSIVE clause. Keep no formation distinct from numerical INVALID and report its seed count.

8. **R4-8 — Low: dependency prose and the choice-action table need a document cleanup.**

   Evidence: lines 12-13 and 245 still call the medium “being built” and stationary memory pending, although the supplied engines/reports now exist. Line 92's unescaped absolute-value pipes split the Markdown action row, so its rendered columns no longer faithfully show the rule.

   **Fix:** refresh the dependency descriptions against the supplied reports/reviews, preserving their bounded engine status and the separate owner authorization gate. Escape the pipes or write `abs(wrap(...))`. This finding alone would permit APPROVE_WITH_NOTES.

9. **R4-9 — Low interpretation note: describe the added alias screen and G5 as the limited diagnostics they are.**

   Evidence: lines 170, 209-214 and 272; `c4_model.py:88-101`. A maximum **wrapped** increment cannot detect an integer multiple of 2π between samples. Its threshold can flag some fast changes, but does not certify absence of aliasing. The design's removal of a general bound is correct; this review establishes no new full-detector false PASS on the declared grid.

   Also, uniformly shifting every copy phase and the carrier by π preserves relative phases, C4 geometry/coupling, drive phase differences and decoded direction. With identical seeded observations/bindings and fresh episodes, the two G5 copies are mathematically equivalent. Their expected D is zero even for an abstaining group. G5 is consequently a useful numerical/copy covariance check, with competence reported separately, rather than an independent test of usefulness or persistence through a new history.

   **Fix:** label those limits in the report contract: the alias flag is a warning screen, and G5 assesses reproduction under a uniform carrier-phase shift and identical panels. Preserve the negative contract and descriptive competence/abstention reporting. These interpretations require no additional experiment or stronger bootstrap claim.

## Evidence and boundary

Read AGENTS.md, revision 4 and its commit diff, the R3 review and relevant R2 passages, decision 0028 item 17, R5, CURRENT.md, frozen C4 detector/model and C5 detector functions, the complete world and medium reports and their Claude reviews in `growing_shapes_review_claude/`, the world ABI, and relevant medium ABI/RHS/history/cost implementation passages. The three consulted C4/C5 source hashes match the C5 R003 receipt; source 04's SHA256 matches CURRENT.md. This was no new source audit or engine qualification.

The world report SHA256 was `b5ba3f12c62b12f82448518632d83d6458a09eef1de363d5a438125bd4a180fc`; the medium report SHA256 was `65c2e64f5111eed347a75307bc7245ed4c0217786e59515cf955455d107dde2b`. Their stored check results were read as reported engine evidence and were not rerun. The supplied engine review/readiness boundary is preserved.

The six material repairs are R4-1 and R4-3 through R4-7; R4-2, R4-8 and R4-9 are nonblocking notes. The continuous-run choice, complete score-free recovery replay, saved-template admission, structural admission shared by both arms, clipped reward, count-stability reduction and deferred larger claims can stand. The drafter should reconcile the remaining contracts and update the section-14 dispositions before a passing design review. Section 10 still requires the separate owner go-ahead stated at line 9.

Concurrent-change note: HEAD advanced to `b547d7f8efab06ec83bc47fff45c4dc5ddcff58f` through an unrelated decision/tracker documentation commit. The reviewed design and both engine reports retained their stated hashes. This review remains pinned to revision 4 at `69cc18c`.

Only `docs/reviews/tactical_0h_design_review_codex_r4.md` was written. No project code, tests, scripts, pilots, experiments or panels were run; no commit, engine edit, design edit or status change was made. The unrelated untracked files present at the start were preserved.
