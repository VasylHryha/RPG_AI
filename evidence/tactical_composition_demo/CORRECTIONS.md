# Corrections to the recorded reports (additive; the reports and run records stay unchanged)

Written 2026-10-03 after an owner-requested recheck ("check if it is the best we can do… issues, conflicts, gaps"). Four independent read-only
audits (claims against raw data, scientific design, code, governance) were run by Claude subagents, which is the **same model family** as the
author: that is a self-audit. A fifth review, by **Codex (cross-family)**, then examined decision 0028, this file, `tcd_common` and `PROPOSAL_0D.md`
(`docs/reviews/tactical_composition_0d_review_codex.md`, verdict CHANGES_REQUIRED for the proposal); its findings on these documents are applied here. It reviewed the proposal, not the historical results (see `docs/decisions/0028-owner-directed-exploratory-composable-shapes.md`).

Nothing here changes a verdict. Recorded verdicts were re-derived independently from the per-seed files using only the specification text, and all
eight (Stage 0 P1–P5, change-cost r2 C1–C3) matched. What follows corrects wording that the data do not support, states where a verdict is fragile,
and records known defects of the recorded code. "Checked" means I recomputed it from the stored per-seed files myself; "audit" means a subagent
reported it from the same files and I did not recompute it.

## A. Verdicts that are fragile (read the verdict with these)

| Item | Fact | Source |
|---|---|---|
| Change-cost r2 **C1** (SUPPORTED) | median 0.6989 against a bar of 0.70; 55% of seeds at or below it; the seed interquartile range is about 0.02. C2 and C3 are gated on C1, so the whole chain rests on a margin of 0.001. | audit; the report already says "marginal" |
| C1 rule changed between revisions | r1 required 75% of seeds; r2 uses the median only, after r1 failed on the 75% rule. Recorded in decision 0028. | `change.py:179`, `change2.py:202` |
| Stage 0 **P5** (INDETERMINATE) | "median and 75% of seeds" read jointly (both bars in the same seed) gives 65% of seeds, INDETERMINATE. Read per condition it gives 85% and 80%, which would be SUPPORTED. The specification does not say which. The recorded reading is the joint one. | audit |
| C3 common level 0.80 | The phrase "at or below every design's own raw quality" is ambiguous: by median it gives 0.80; per seed the minimum is 0.7875, so no listed level qualifies. The level was set knowing the block's plateau. | audit |
| Relative-view step metric | The spec does not say whether the relative view uses `step_move` or `step_tiebest`. Both give the same verdict (audit). | audit |

## B. Statements to read differently

| Where | Statement | Correction | Basis |
|---|---|---|---|
| `REPORT_CHANGE2.md`, `MOTIVATION.md` | "about 10 times fewer rows" | The registered statistic is a **tenfold ratio of first-success grid values** (half of seeds: 100 rows against 1,000 at the 0.80 level), with floor and coarse-grid censoring. It is not a bound on the underlying need: the wired unit already reaches 0.80 at the grid floor of 100 rows in 20 of 20 seeds and 0.90 in 14 of 20, so its need may be well below 100; the equal-size block reached 0.80 in 19 of 20 seeds within the grid (never within 100 rows) and 0.90 in only 2 of 20; the large block reached 0.80 in 20 of 20 (one seed already at 100 rows, 0.8006) and 0.90 in 3 of 20; intermediate values were not tested and crossings are noisy. Neither "about" nor "at least" ten times is established; say "100 against 1,000 rows on the registered grid". | checked; Codex review |
| same | "never recovers within 12,000" / "no design recovered in any seed" (fine-tuning) | In the relative view, retraining from scratch recovered the equal-size block in **5 of 20** seeds and the large block in 0 of 20. Fine-tuning recovered the equal-size block in **4 of 20** seeds (the wired unit in 0 of 20). Say "fewer than half of seeds". | checked |
| same | "the big controllers' step angle was 11 to 13 degrees at 12,000" (`MOTIVATION.md`: "11 to 29") | At 12,000 rows the step angle is **11.2** (equal size) and **9.4** (large), the latter under the 10 degree bar. The 29 degrees is the 100-row value. | checked |
| same | "below the rush rule's -0.212 at most row counts" | Below at **all six** row counts (-0.30 to -0.49). | checked |
| same | "Part of this restates the design"; "supports … quick to change" | The change is a monotone function of one input feature; MOVE labels do not depend on the doctrine, and only AIM was retrained, so the cheapness of the wired unit holds by construction. The matching control (a block with everything frozen except its score head) was not run. | audit |
| `REPORT.md` (Stage 0), `MOTIVATION.md` | "the advantage comes from the wired structure" | Structure, weight sharing across enemies, the target-conditioned step and separate teaching are **not separated**. A structured end-to-end baseline was not run. The flat model's step head regresses a multimodal target by squared error, which may explain part of its loss. | audit |
| `MOTIVATION.md` | "cannot be separated by training mode … exactly the same computation" | Too strong. Joint training of the two pieces through the target choice is a different computation; the Stage 0 report itself names an end-to-end shared-scorer test as the natural follow-up. | audit |
| `MOTIVATION.md` trail, Stage 0 row | "needs 16 times the data to approach" | The 96,000-row block (16 times the rows, 7.3 times the parameters: 5,765 against 787) is within 0.05 of the composed unit on seen mixes (+0.05, 95% interval 0.04 to 0.06) and **ahead of it on the unseen type** (-0.05, interval -0.08 to -0.01). The report said this; the trail row left it out. | audit |
| `REPORT.md` (Stage 0) | composed 0.708 on the unseen type | 0.708 is the median of per-seed cells; the prose 0.696 (and the 0.715 and 0.750 for the 4x and 16x blocks) are averages of per-opponent medians. By per-seed cells the larger blocks are 0.7125 and 0.748. The two columns are not comparable. | audit |
| `REPORT.md` (Stage 0) | "no post-hoc analysis" | The causal explanations in the Reading ("error is set by its pieces and adds up", "the advantage comes from structure") are untested statements, not results. | audit |
| `REPORT_CHANGE.md` line 23 | "No design recovered its own quality" | The equal-size block recovered under that revision's relative rule in seeds 6, 11, 14 and 16 (its own line 13 reports the 20%). The INDETERMINATE verdict stands. | Codex review |
| `REPORT_CHANGE.md` | "972 s CPU" | 979.7 s (`run_change/SUMMARY.json`). | audit |
| `REPORT_CHANGE.md` amendment | from-scratch AIM "0.994", "dev_learnability.py, below" | 0.994 was an earlier scratch look; the recorded development check is 0.998 (`dev_learnability.json`). | audit |
| `SPECIFICATION.md` line 28 | skirmisher (70, 0.45, 3.5, 6, 3, 3.0) | Stale. `tactics.py` and the specification's own section 8.4 give hp 60, speed 0.30, range 6.0, damage 7, cooldown 4, preferred range 2.5. The runs used `tactics.py`. | audit |
| Stage 0 P5, unseen type | "tests an unseen unit type" | The skirmisher is an archer with preferred range 2.5. The teacher's back-off rule flips at 2.0 and trained ranges are 1.2, 3.5 and 5.0, so the test asks where a smooth network puts a step function in an untrained gap. It is an interpolation test, not a test of composition. | audit |
| `MOTIVATION.md` | "Two levels worked" | C5's formation caveat applies (AGENTS.md: H-M at level 2 is supported for the formed groups only; formation is near its threshold and the panel does not establish a population formation rate above 50%). | AGENTS.md |

## C. Two-body pilot (`evidence/c6_dev_pilot/a_twobody/`) — see its `ADDENDUM.md`

The same audit found wording issues there (pooled gaps diluting P1 and P3, "near-misses", "zero to machine precision", pooled "R shrinks"). They are
recorded in `ADDENDUM.md`, which also adds the unit-table post-hoc result that `REPORT.md` omits and `MOTIVATION.md` cites.

## D. Known defects of the recorded code (frozen; repaired in `tcd_common/`, see `tcd_common/CHANGES.md`)

| Defect | Effect on recorded results |
|---|---|
| `tactics.change_metrics` step metrics run over all states, and `step_tiebest` drops hold labels when tied-best enemies mix hold and move labels, so a correct hold is scored as an angle error | Inflates the tie-best step angle (mean and p90 most, median only if more than half of states are affected), most under the changed doctrine (28% ties). It affects the relative view and C2's step test; it cannot be recomputed because the trained models were not stored. The verdict is unchanged under the `step_move` metric (audit). |
| Stage 0 `aim_top1` and its nearest-enemy floor include single-enemy states, which agree trivially | Both numbers are inflated by the same states (0.979 and 0.862 in the report). The change-cost code already used multi-enemy states. |
| `ratio_verdict(inf, inf)` returns SUPPORTED | Latent: C3's gate on C2 blocked it in the recorded run, and the common-level view had finite values. |
| `run_jobs` reports "deadline" when the last job finishes after the soft deadline; the watchdog is cancelled after evaluation; `atomic_write` temporary names are shared by the watchdog and main threads | None in the recorded runs (all completed 20/20 before the caps). They could have mislabelled or corrupted a run that ran long. |
| `tactics.py` was extended after the Stage 0 run (hash c0d849… then, 37fa0a… now) | By inspection every change is additive, except `batch=min(batch, len)` in `MLP.fit` (a no-op when the data have at least 128 rows). Checked once (commit `6e92322`): the current file matched all three recorded versions (full sha256 of each recovered file equal to its run record) on collect, original-doctrine labels, piece datasets, from-scratch fits and policies, fidelity and win scores; it did not cover the changed-doctrine and fine-tuning paths, and the r2 version is byte-identical to the current file. Seed 0 of Stage 0 (63 stored values) and of change-cost r2 (670 values) re-ran identically at HEAD (`tcd_common/SEED_REPRODUCTION.json`, which records the HEAD, file hashes and a digest of the fresh values); this is exact equality of the stored values for one seed per harness, not identity of trained policies and not all seeds. `tactics.py` is now frozen and pinned by hash (`tcd_common/test_common.py`). |
| Preflight tests create an empty directory (git never lists it) and the run-directory filter matches substrings | The filters were never exercised by the old tests. New tests in `tcd_common/test_common.py` use a real throwaway git repository. |
| `dev_calibration.py`, `dev_doctrine.py`, `dev_learnability.py` execute at import and overwrite their committed JSON | **Do not run or import them.** They are hashed into the run records and left unchanged. |
| `history_ability_attempt/dev_calibration_with_ability.py` cannot run (`import tactics` after changing `sys.path`) | Kept as history only. |
| The `USE_BURST` global is read at call time by the opponent policy, labels and random action | It is `False` in every recorded run; flipping it would silently change the opponents. Stage 0b must pass it explicitly. |

## E. What stays true

The wired unit (AIM and MOVE) matches the scripted expert within about 0.03 on seen mixes, beats an equal-size flat block by a wide margin (+0.24, interval
0.21 to 0.27, audit), and retraining only AIM reaches the 0.80 level at the grid floor (100 rows) where the flat block first reaches it at 1,000 rows, after a rule change (checked; a ratio of registered first-success grid values, not a bound on the need).
These hold in one invented sandbox, with scripted teachers, imitation, and ordinary networks inside the pieces. They say nothing yet about geometry,
oscillators or "vibration", about a second level of composition, or about learning from outcomes.

## F. After experiment 0d Part A (added 2026-10-04)

Sections B and E above describe the state before 0d. 0d (`REPORT_0D.md`) answers the "structure versus separate teaching" question only narrowly: a jointly trained network of the same graph does about as well as the separately taught pieces, against a **weak** flat baseline (the tuned flat model plays worse than the rush rule; a
probe shows larger flat models climbing with data to 0.74 at 60,000 states). It does not show which element of the graph matters, that flat networks cannot do it, that joint and separate training are equivalent in general, or anything beyond one level and one sandbox. Wording of `REPORT_0D.md` corrected on 2026-10-04: "adds no detectable benefit" became
"a small but consistent benefit of about +0.02, inside the margin"; "within 0.02" became "about 0.02"; "holds at every data size" is restricted to V1's direction with a flat model tuned at N = 3,000 only; the "load afterwards" sentence was removed (the run record has the load at the start only).

## G. Notes on the registered 0d files (they are hashed into the run record and were not edited after the run)

| File | Note |
|---|---|
| `SPECIFICATION_0D.md` | "registered at the commit that adds this file" is imprecise: the registration commit is `c747e76` (the run record's `git_head`); `ad8a17b` was the first registration, fixed before any run. Its authority line reads the owner's message as approval: that reading is **[R]**, decision 0028 item 8. Line "equality cases are strict" holds for the verdict rows; the discordance rules use `≥` and `≤` as written. W (the win-score contrast) is the paired median over seeds of the per-seed mean of the two opponents' scores; it is not defined in the text. The "REFUTED" column for V2 is empty (labels), and V4 and V5 "REFUTED" mean "equivalent to zero within ±0.03", not "worse". Strata are not disjoint (back-off is a subset of moving). Section 6 says F1 is at "the smallest hidden size": the grid included 4 and F1's boundary values after the extension were learning rate and decay only. |
| `PROPOSAL_0D.md` | The header still reads "DRAFT" / "revision 2"; the run followed `SPECIFICATION_0D.md`. Proposal stop row 1 ("unapproved: build and run nothing") was evaluated on the author's reading of the owner's message; see decision 0028 item 8. |
| `zd_run.py`, `test_zd.py` | `c_adequate` is recorded in the configuration but not read by `evaluate` (the proposal's stop row "C fails its adequacy gate: stop" was applied by hand from development, where C passed); the start-load rule is recorded in `RUN_STARTED.json`, not enforced. `evaluate` reuses bootstrap keys 40 to 42 for N = 1,000 and 9,000 (descriptive only). `fit_f0` ignores the recipe's learning rate and decay (they equal `tactics.MLP`'s defaults). Supervision counts treat F1 as 5N and F2 as 4N for the same label content. `test_zd.py` leaves the F0 branch of "every model trains and acts" to the end-to-end test. These were found by the post-run audits; `test_zd_audit.py` adds checks for the untested discordance branches, the comparator, the recipe, the stratum stop, and the saved weights. |
| `tcd_common/` | `SEED_REPRODUCTION.json` records HEAD `13662a4`, earlier than the harness edits of `c747e76` (which do not touch the seed computation). `harness.run_experiment` injects an absolute `run_dir` into the configuration, so the recorded configuration differs from `SPEC_0D.json` by that key. Several functions are unused by 0d (`step_tiebest`, `change_metrics`, `ratio_verdict`). |
| `dev_0d/README.md` | Does not mention the post-run probe: see `dev_0d/POSTRUN_NOTES.md`. Its step table omits the probe and the round-trip check. |

(2026-10-04, after the GPT plan review, `docs/reviews/tactical_0e_plan_review_gpt.md`, R9): the "connect without loss" sentence became "the connection gap is near zero (a diagnostic, not proof of lossless wiring)" (the gap is within ±0.0004 per seed, not literally zero, and compares different target distributions); the structure-versus-separate-teaching reading is stated as consistent-with, not categorical; "at least 20 times" was replaced by the observed 3,000-versus-60,000 comparison.

## H. Notes on the registered 0e files (hashed into `run_0e`; not edited after the run; 2026-10-04 recheck)

| File | Note |
|---|---|
| `SPECIFICATION_0E.md` | Line 5 says the correction is "the commit that follows it": the corrections are `bb5ff7f` and `1e58a6e`. "Mixed teams only" (section 1) is wrong: one of the five V3 mixes (mage, archer, archer) is all ranged. B3 was not attainable (the teacher is +0.030 [0.0125, 0.0375] above Fp), and the B2 IQR component's upper bound is the span of the 2nd to 29th seed and equals episode-sampling noise at 300 episodes; neither was checked before registration. |
| `PROPOSAL_0E.md` | The header and section 4 keep the first draft's four claims at 0.0125; the specification's five claims at 0.01 govern (its section 13 says so). It calls GPT "a third model family"; GPT and Codex are both OpenAI models. |
| `dev_0e/README.md` | "The relabel and sham controls equal intact exactly" describes self-checks that cannot fail by construction, not controls. The step-5 note that `Fflat` was not in the pilot is correct. |
| `ze_core.py`, `ze_run.py`, `test_ze*.py` | No defect changes the record (round trip exact). The registered tests did not cover the V3 code path; `test_ze_audit.py` adds those checks. Fidelity and MOVE prequalification cover multi-enemy states only. The B1 "default" cut keeps the attack on AIM's choice and moves toward the nearest enemy, so it measures the message together with a coherence penalty; the coherent comparison (learned unit against the nearest-enemy unit) is +0.124 [0.106, 0.132]. |
