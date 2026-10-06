NO_OBSERVED_CHANGE_WITHIN_ASSESSED_SCOPE (10 stored worlds; panel risk not quantified; adoption not assessed)

# C6 option B inexact math: impact study, revision 2

**Date:** 2026-10-07. **Author:** Claude (claude-opus-5-5).
**What it is:** a corrective revision answering Codex's owner recheck, `docs/reviews/c6_inexact_study_recheck_codex.md` (CHANGES_REQUIRED on `7954445`, committed `428cac8`), findings F1–F6 and the low note.
**Method:** stored data only. No C6 world, build or battery ran for this revision.
**Unchanged:** revision 1 (`INEXACT_IMPACT_REPORT.md`, `SUMMARY.json`, `results/`, `scripts/` as delivered); this file supersedes its claims.
**Status:** an engineering diagnostic. It is not an adoption decision. Using the inexact engine needs the owner's decision and a decision record, because it would end the zero-tolerance contract of decision 0029, item 3.

## What the evidence supports, in plain words

**Recorded outcomes:** in the 10 stored worlds (smoke 0–1, development 0–7), every recorded discrete value and outcome is identical between the exact and inexact engines. That includes:
- every Boolean (17,278), integer (992,981) and string;
- every outcome, chain, witness, first-loss time and link count;
- every candidate membership the artifacts store.

**Numbers:** the largest change to any stored number is **3.3 × 10⁻⁹**. That is a grid-error monitor. Outside the monitors, the largest change is **2.4 × 10⁻¹⁰**. No stored number changes by more than 10⁻⁸.

**Margins:** for the decision families that can be checked on stored data (section 2), each engine's signed margin was evaluated with the evaluator's own operator and moving thresholds. There are **0 flips** in 77,342 scalar decision instances, 1,142,364 pair lock tests and 3,121,284 pair link tests.
- **The closest assessed decision** is a frequency-change test 7.3 × 10⁻⁹ from its threshold (development 0). The inexact math moved it by at most 4.2 × 10⁻¹⁶.

**What is not established:**
- **Not every decision is covered.** Several contexts cannot be checked from stored data (the ledger below lists each one, with the reason).
- **The C6 panel analysis is not assessed.** That covers its 16 contrasts, confidence-interval boundaries, quorums and hypothesis combination.
- **Future outcome risk is not quantified.** That includes a 40-world panel.

**Speed:** about **25% less compute CPU** per world, an observation on this machine. Wall-time savings are indicative only, and panel readiness is unassessed (section 5).

## 1. What changed from revision 1

| Finding | Revision 1 | Revision 2 |
|---|---|---|
| **F1: coverage** | Claimed "every decision type" | **Decision-coverage ledger** (section 2), with every family and context marked ASSESSED or UNASSESSED and a reason. Added **paired-gain refinement** (20 instances, from stored gains). Added **pair-level decisions in rolling persistence and endpoint windows** at grid dt, reconstructed from stored operation frames: all 39 cells were checked against the stored grid-0 persistence statistics and reproduce them **exactly**, with a max difference of 0. Headline narrowed to observed agreement within the assessed scope. |
| **F2: panel risk** | "About 2 × 10⁻⁴, conservative" | **Removed.** It extrapolated a near-threshold density over 6–10 orders of magnitude of band width, and assumed sampled perturbations bound future ones. Neither holds. Future-panel risk is **not quantified** by this study. |
| **F3: margins** | Mixed units for the causal floor; fixed thresholds; flips not emitted; closest lock misreported | Signed margins evaluated **separately for each engine**, with each actual operator: strict `>` for the causal floor, per grid; strict `<` for links; `<=` and `>=` elsewhere. The thresholds of spread and ablation move with `min(intact)`. **Flip counts and identities** are emitted for every family (all 0). **Closest qualification lock** corrected (below). The **28 grid monitors** are now separated from the **one recovery statistic**. Lock values use the detector's own `circular_std`, including its clip to [1e-300, 1] and the non-negative square root. Link tests are labelled as a NumPy recomputation of `c4_detect.components`, not the native arithmetic. |
| **F4: tolerance** | Replaced the ≤ 1e-8 bound with a relative bound for monitors | **The original ≤ 1e-8 absolute bound is kept on every comparable float, monitors included.** All stored values meet it; the largest is 3.3e-9, about 3× inside. Relative monitor changes are reported apart. Any relative gate would be a separate owner decision. The macOS build is pinned (section 4). |
| **F5: reproduction** | The scripts pointed at the scratch layout | New `scripts/analyze_r2.py`. It takes explicit `--repo-root` and `--study-root`, uses a fixed ten-world inventory, and checks every raw input against `RAW_FILES_OUTSIDE_GIT.json`. It fails on a missing or mismatched input, refuses to overwrite, and keeps batteries out of the world aggregation. It writes `results_r2/`, `SUMMARY_R2.json` and `RECONCILIATION_R2.json`. |
| **F6: runtime** | "2.4× headroom" without its load qualification | Restored: the exact engine's **396.1 s** case under load about 85 fails the 360 s rule. Wall time is indicative only; panel readiness is unassessed. |
| **Low note: accuracy** | "Both accurate to about 1 ulp" | Replaced with the measured scalar-vs-vector differences, and no claim of equal mathematical accuracy (section 6). |

**Reconciliation with revision 1** (`RECONCILIATION_R2.json`):
- **Reproduced exactly:**
  - float count 17,413,140;
  - changed 8,907,030;
  - 29 above 1e-10;
  - 0 above 1e-8;
  - max 3.3404761575145728e-9;
  - 0 discrete changes;
  - 45,592 digests changed.
- **Changed by definition:**
  - **Scalar decision instances, 76,703 → 77,342:** the causal floor is now 3 rows per grid instead of 1, paired gain was added, and monitor copies under `output_check` are no longer counted.
  - **Lock tests, 55,200 → 1,142,364:** reconstructed persistence windows were added.
  - **Link tests, 1,711,200 → 3,121,284:** each distinct stored frame is now counted once, and persistence frames were added.

## 2. Decision-coverage ledger

Operators and thresholds are those of `geomind/c6_r4_field_assay.py`, `geomind/c6_r4_field_protocol.py` and `geomind/c4_detect.py`, with the protocol settings. All quantities are dimensionless, except where the units column says otherwise.

### ASSESSED: signed margins of both engines on stored values

| Family | Evaluator, operator | Units | Instances | Contexts (count) | Flips | Closest to threshold | Largest margin change | Smallest distance ÷ change |
|---|---|---|---:|---|---:|---:|---:|---:|
| membership Jaccard | `qualification`, `rolling_persistence`: `>= 0.95` | ratio | 12,069 | rolling persistence, 3 grids (11,817); post-operation (150); before-formation (40); endpoint (39); source copy (13); initial source (10). Qualification rows are grid 0 only. | 0 | 6.5e-3 | 0 | no change |
| shape CV | `<= 0.05` | ratio | 12,069 | as above | 0 | 2.4e-2 | 9.3e-14 | 5.2e11 |
| group lock std | `<= 0.1` | rad | 12,069 | as above | 0 | 3.6e-3 | 5.5e-12 | 2.0e10 |
| freq change | `<= 0.01` | rad/C0 | 12,069 | as above | 0 | **7.3e-9** | 4.1e-14 | **1.7e7** |
| pattern change | `<= 0.1` | rad | 12,069 | as above | 0 | 1.8e-4 | 7.3e-12 | 5.4e9 |
| recovery Jaccard | `recovery`: `>= 0.9` | ratio | 558 | 3 grids per accepted grid-0 candidate | 0 | 5.8e-2 | 0 | no change |
| recovery pattern error | `<= 0.1` | rad | 558 | as above | 0 | 9.1e-3 | 2.4e-10 | 2.9e8 |
| causal effect floor | `closure_valid`: each grid `> 1e-8`, strict | effect units | 1,104 | per grid; g→m and m→g | 0 | 8.8e-3 | 1.9e-11 | 4.2e10 |
| causal refinement spread | `max-min <= 0.1·min(intact)`, threshold moves | effect units | 368 | g→m, m→g | 0 | 8.8e-4 | 1.5e-11 | 6.0e9 |
| causal ablation | `max(ablated) <= max(1e-12, 0.2·min(intact))`, threshold moves | effect units | 368 | g→m, m→g | 0 | 1.8e-3 | 9.8e-13 | 8.4e10 |
| descriptor gain refinement | `descriptor`: `max\|g_k−g_dt/4\| <= 0.001` | gain | 53 | operation and before-response descriptors | 0 | 1.0e-3 | 2.8e-15 | 3.5e11 |
| **paired gain refinement** (new) | `operation`: `max\|Δ_k−Δ_dt/4\| <= 0.001`, Δ = intact − control | gain | 20 | eligible cells × 2 controls | 0 | 1.0e-3 | 1.0e-15 | 9.6e11 |
| grid error: position / phase / field | `GridSet.run`: `<= 0.05` | L-normalised / rad / field | 4,656 each | world check list | 0 | 0.048 / 0.050 / 0.050 | 3.3e-9 / 3.2e-10 / 3.4e-12 | 1.5e7 / 1.5e8 / 1.5e10 |
| **pair lock** (qualification) | `locked_pairs`: circular std `<= 0.1`, the detector's clip | rad | 55,200 in 200 windows | stored qualification windows, grid dt | 0 | 1.63e-4 | 1.1e-15 (at the closest test) | 1.5e11 (at the closest test) |
| **pair link** (qualification) | `components`: `d < 1.5·median(nn)`, strict; NumPy recomputation | relative | 1,711,200 in 6,200 frames | as above | 0 | 6.3e-7 | 4.3e-15 (at the closest test) | 1.5e8 (at the closest test) |
| **pair lock** (persistence and endpoint, new) | as above | rad | 1,087,164 in 3,939 windows | 39 turn-condition cells, reconstructed at grid dt and **validated exactly** | 0 | 1.5e-6 | **0** (at the closest test) | no change (at the closest test) |
| **pair link** (persistence and endpoint, new) | as above | relative | 1,410,084 in 5,109 frames | as above | 0 | 4.3e-6 | 4.7e-15 (at the closest test) | 9.1e8 (at the closest test) |

For pair rows, the change is reported at the closest test only. The largest change over all pair tests is not computed; flips are counted over all of them.

**Corrected closest qualification lock (F3):** smoke 1, `/turns/0/before_formation/3`, pair (0, 22).
- Exact engine: 0.1001632847400453. Inexact engine: 0.1001632847400464.
- Margin −1.632847400452886e-4. The pair is on the unlocked side in both engines.
- Change: 1.1e-15.
- Revision 1's "1.8e-3 in development 4" was wrong.

**The closest assessed decision overall** is in development 0, turn 2, persistence window 29: freq change 0.010000007263912924 against `<= 0.01`. It fails in both engines.
- The inexact change is 8e-17 on grid 0, and at most 4.2e-16 over the three grids.
- The exact engine's own dt and dt/4 values differ by about 7.3e-13.

**The persistence and endpoint reconstruction:**
- **How it is built:** each operation cell's grid-dt windows are rebuilt as `prefix[-31:-1] + operation_frames`. The prefix is the stored qualification window of the cell's source episode: the initial source for turn 1, and the turn-1 intact episode-0 record for turn 2.
- **Validation:**
  - **Prefix mapping:** checked in every cell, because operation frame 0 equals the prefix endpoint.
  - **Statistics:** recomputing every stored grid-0 persistence statistic from the rebuilt windows reproduces it **with zero difference** in all 39 cells, 3,939 windows.
- **What it also covers:** the endpoint qualification window is the last persistence window, so its pair decisions at grid dt are covered.

### UNASSESSED: not checkable from stored data, or out of scope

| Decision context | Evaluator | Why it is unassessed |
|---|---|---|
| Pair lock and link decisions at **dt/2 and dt/4**, in every qualification, persistence and endpoint window | `components` and `locked_pairs` on grids 1–2 | Fine-grid frames are not stored; only grid-0 frames are. Their *statistics* (persistence for all 3 grids, recovery for 3 grids, causal for 3 grids) are assessed as values above; the underlying pair decisions are not. |
| Candidate inventories on dt/2 and dt/4, and their **grid agreement** (`grid-dependent structural candidates`, `grid-dependent recovery`, `grid-dependent persistence`) | `qualification`, `operation` | Only `all_rows[0]` is stored. Agreement is observed only indirectly: neither engine raised a numerical failure (`invalid` is null in both). That is not a margin analysis. |
| Pair decisions inside **recovery control and kicked endpoints** (`best_match`) | `recovery` | Recovery trajectories are not stored. Their outputs, the Jaccard and the pattern error, are assessed as values. |
| **Causal** control and treated trajectories | `causal` | Not stored; the effect values are assessed. |
| Candidate **minimum size**, positive geometry and spacing, finite-value checks, **selection and ties** (`select_accepted`) | `qualification` | Discrete or integer branches with no margin. Covered only by the observed equality of stored memberships, selections and identities. |
| **Sham and provenance guards**: trace-hash equality of intact vs no-backreaction, zero output, NO-R must not qualify, controls | `operation` | Each is an equality or Boolean evaluated within one engine. Both passed in every stored world (no invalid run). It is a no-margin check: the digests themselves change between engines, as expected. |
| **Primary analysis**: 16 response and later-formation contrasts, CI bounds ±0.01 and ±0.1, bootstrap and empty-draw policy, eligibility and chain masks, quorum, grid-verdict agreement, hypothesis combination | `geomind/c6_r4_field_analysis.py` | Needs the registered 40-world panel on final entropy, which is not authorized. Ten engineering worlds, two of them smoke, are not that analysis. |
| **Development readiness gate**: source and chain quorums, runtime projection | `tools/c6_r4_design_gate.readiness` | Development worlds 8–9 were not run, and the gate's concurrent schedule was not used. |
| Arm A | — | Outside this study. |

## 3. Where the differences are

| Value class | Floats | Changed | > 1e-10 | > 1e-8 | Max absolute change | Max relative change |
|---|---:|---:|---:|---:|---:|---:|
| Grid-error monitors (`max_errors`) | 14,085 | 10,765 | **28** | 0 | **3.3404761575145728e-9**: development 2 `/checks/323/max_errors/position`, 7.3999889039608e-5 → 7.399654856345048e-5 | **5.0551%**: smoke 0 `/checks/809/max_errors/position`, 9.907616180352751e-11 → 9.406776773112684e-11 |
| All other floats | 17,399,055 | 8,896,265 | **1** | 0 | **2.3871038479228446e-10**: development 7 recovery pattern error (a thresholded statistic), 0.0298175926669 → 0.0298175929056 | Near-zero values only; for example 3.5e-17 changes sign, which is a relative change of 2. Relative change is not meaningful there. |

- **The 28 monitors** are numerical-error diagnostics; the one other value is a thresholded statistic.
- **The two extremes are different values:** the largest absolute monitor change is on a monitor of about 7.4e-5; the largest relative change is on one of about 9.9e-11.
- **Over time:** operation frames, 100 s per turn and condition, deviate by at most about 2.2e-12, with no growth that matters (revision-1 per-world `horizon`, unchanged).

## 4. Tolerance (F4)

**The bound to keep:** every comparable finite float is within 1e-8 absolute, monitors included. This is the memo's §7 bound, unchanged.
- **Stored data:** all of it meets the bound. The largest is 3.3e-9, about 3× inside. Decision values other than monitors are at most 2.4e-10, about 40× inside.
- **Decision identity** is still required, as in memo §7: every Boolean, integer, label, membership, chain, witness, invalid field and stop reason.
- **Monitors:** relative monitor changes are reported (max 5.06%), but they are **not a gate**. If the owner ever wants a relative gate, it is a separate decision. It would need a defined denominator and zero policy, and it would apply in addition to the absolute bound.
- **Platform pin:**
  - **Run receipts:** they record `macOS-26.6.2-arm64-arm-64bit`, a release, not a build.
  - **Build read now:** at this revision, `sw_vers` on the same machine reports **macOS 26.6.2, build 25G83**. It was read now, not at run time. Nothing indicates an OS update in between, but the receipts cannot prove that.
  - **For any future adoption run:** record `sw_vers -buildVersion` and the Accelerate library identity in every receipt. Re-baseline the inexact references after any OS update.

## 5. Speed and runtime (F6)

| Pair (run one after the other, load 27–80 on 10 cores) | CPU ratio | Wall ratio |
|---|---:|---:|
| development 2 / 3 / 4 / 5 / 7, smoke 1 | 0.768 / 0.747 / 0.741 / 0.752 / 0.719 / 0.752 | 0.799 / 0.750 / 0.758 / 0.652 / 0.833 / 0.640 |
| development 6 (trivial, 7 s) | 0.807 | 0.810 |

- **Compute CPU:** mean ratio **0.747** on the six non-trivial pairs (range 0.719–0.768), and 0.755 across all seven.
  - This is an observation on this machine, from one ordered sample per pair.
  - Shared load, core placement and cache contention limit how far it generalises.
- **Wall time:** 0.640–0.833. **Indicative only.** Load changed between the two runs of each pair, and the figure measures compute time, not the full serialised lifecycle.
- **Runtime rule, restored qualification:**
  - **When it passes:** the exact engine passes 360 s only while a world gets enough cores, about 1.37 cores on average by the deep-dive's measure.
  - **When it fails:** under load about 85, the final exact code took **396.1 s** and failed the rule (`PERFORMANCE_DEEPDIVE_REPORT.md`).
- **Not assessed:** two-worker panel throughput, and readiness of either engine for a recorded panel. The existing runtime gate must be applied, at the intended concurrency, before any recorded use.

## 6. Accuracy wording (low note)

Revision 1 said both libraries are "accurate to about 1 unit in the last place". That is withdrawn. What was measured (round-2 memo §3, item 6) is agreement with Apple's scalar libm, not error against the mathematical value:

| Function | Disagreement with scalar libm |
|---|---|
| `vvexp` | up to 1 ulp on 26% of arguments |
| `vvsincos` | up to 3 ulp |
| Separable `exp(a)·exp(b)` against `exp(a+b)` | up to 33 ulp |

Apple's scalar libm is itself not correctly rounded (memo §3). This study relies only on the measured differences in trajectories and statistics. It makes **no** claim that the two engines are equally accurate mathematically.

## 7. Owner recheck applied to this revision

The owner's prompt, applied verbatim: "Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps." No numeric score is assigned.

**Found and fixed while rechecking:**
1. **Issue: persistence validation recorded only the last cell per world.** The first run of `analyze_r2.py` overwrote the record each time, so the summary showed 9 cells. Each cell's check is now kept: 39 cells, all exact, max statistic difference 0. Outputs were regenerated before commit.
2. **Gap: double counting.** Monitor copies under `output_check` were counted in revision 1. Revision 2 counts only the canonical `/checks/` list. Qualification copies under `/source/` remain, and are labelled as a separate context.
3. **Conflict: wrong denominator for the link margin.** The relative link margin is measured against each frame's own moving threshold, in both engines.
4. **Gap: the closest persistence lock** (1.5e-6, smoke 1, no-R window 94) is closer than any qualification lock. It is now reported, with change exactly 0.
5. **Issue: the verdict word.** "SAFE_UNDER_PROPOSED_TOLERANCE" implied an adoption judgement. It is replaced by a scope-limited observation.

**Remaining, disclosed:**
- Ten worlds.
- Unassessed contexts (section 2).
- No fine-grid frames.
- No panel analysis.
- Wall timing indicative only.
- The OS build was read after the fact.

**Is this the best we can do?** On stored data, yes: every family with a stored value is assessed with correct signed margins, and the fine-grid and trajectory contexts are named as gaps. Closing those gaps needs new, owner-authorized instrumented runs. Those would store dt/2 and dt/4 frames and recovery and causal trajectories, and would record the OS build and Accelerate identity. A wall-clock comparison would need both engines launched together at the panel's concurrency.

## Files (new in revision 2)

- `INEXACT_IMPACT_REPORT_R2.md`: this report.
- `scripts/analyze_r2.py`: the stored-data reproduction. From the repository root:

  ```
  .venv/bin/python evidence/c6_option_b/inexact_study/scripts/analyze_r2.py --repo-root . --study-root evidence/c6_option_b/inexact_study
  ```

  It refuses to run if `results_r2/` exists.
- `results_r2/<world>.json`: per world:
  - value classes and the values above 1e-10;
  - decision families, with contexts, flips, closest and smallest ratio;
  - pair-level contexts, with validation;
  - recorded outcomes;
  - input hashes.
- `SUMMARY_R2.json`: the aggregates and the input inventory.
- `RECONCILIATION_R2.json`: the comparison against the revision-1 `SUMMARY.json`.
