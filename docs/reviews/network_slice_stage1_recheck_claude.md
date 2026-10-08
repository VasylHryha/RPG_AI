CHANGES_REQUIRED
Reviewer family: Claude
Reviewed commit: 5c0ef3e2278b1895203413a24574b999ae1eeb1b (with the later refused-admission receipt from 3c6ed79 read for context)
Reviewed folder: `evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/` (CONTRACT.md SHA256 `872b0256f7117b26171ff0275980986614bb67c9de961fa5cf32413d49f09229`)
Date: 2026-10-08
Review type: cross-family, read-only development recheck of network slice stage 1. This is not a milestone acceptance. I read the stage-1 sources, the contract, the design and the committed receipts. I ran no tests, training, DAgger, mechanism runs or native host, and I did not read or touch `_local/`. A BC run was in progress on the machine and was left undisturbed. The only file written is this review.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Verdict summary

The stage-1 code is careful in the places the earlier rounds pointed at. These parts are sound:

- **Splits:** splits are by whole fight, and report fights are excluded.
- **Training-only statistics:** fire weights and majority modes come from the training split only.
- **Masked losses:** the losses are masked and use the correct column layout (move 0–32, target 33–45, start 46, release 47, aim 48–80; legal 33/13/33).
- **Matched budgets:** N1 and the recurrent arms count exactly the same decision rows per window, and all three arms get the same 772 steps per epoch.
- **DAgger:** students act, the teacher shadow labels the same tick, and the recurrent history comes from actual visitor intents. Round 0 is retained.
- **N2 law:** it matches the C4 law in the design (NETWORK_POLICY_DESIGN_0G.md:170):
  - θ̇ = ω + forcing + Σ_j (1/deg)·K·exp(−r²)·sin(θ_j−θ_i), with r = |Δp|/100;
  - the 8 nearest neighbours within r<3, degree-normalized;
  - RK4 with the envelope check;
  - the C4 motion term with a clamped r;
  - A/B/J/share masked out of the gradient.
- **Launch reset:** the reset happens after the tick, the same way in training and in deployment.
- **Neighbour gradients:** they stay attached, and a test now covers this.

The verdict is **CHANGES_REQUIRED** because of one data-level defect that the code cannot see, H1. In most strata, the per-draw seed apparently does not change the fight. So the "held-out" validation and test fights are near-copies of training fights. That makes these results misleading as written:

- checkpoint selection;
- the per-head held-out diagnostics;
- the "independent paired draws" of the mechanism check.

The second blocker is already known (3c6ed79): full-prefix reconstruction is quadratic, and the projection is 2,198 minutes. M1 sets out what any speed fix has to preserve so that the arms stay comparable.

As designed, stage 1 cannot answer "does N2 differ from N1" (M2, M3), even after H1 and the speed problem are fixed. It can answer "does each network imitate the teacher on this drill" once H1 is fixed.

## Findings

### H1 — High: draws within a stratum are near-identical, so the held-out and paired-draw readings are not held out or independent

**Evidence.**
- `requests.py:3–10` fixes every position by cell/guns/orientation. The only per-draw input is `seed`.
- COLLECTION_RECEIPT.json shows identical `records`/`decision_rows` for every draw in 10 of 12 strata:

  | Stratum | Draws | Identical value in every draw |
  |---|---:|---|
  | D2-shellfire 1-gun | 17 | 472 ticks/78 rows (the gun dies at the same tick in all 17) |
  | D2-shellfire 2-gun | 16 | 1959/133 (orientation 0) and 1978/170 (orientation 1) |
  | D1-static 10-gun | 17 | 524/880 (orientation 0) and 518/870 (orientation 1) |
  | D1-static 1/2-gun | 17 | 4501 ticks, a timeout every time |

- Only D2-10 varies, and even there orientation 1 has just 4 distinct outcomes in 16 draws.

Identical termination ticks across 16–17 draws strongly indicate identical trajectories, apart from the fight ID. I did not open `_local/` to confirm the array hashes.

**Failure scenario.** In 10 of 12 strata, the single test fight (and the two validation fights) per stratum replays a trajectory that is also in train, 12 times over:

- `evaluate()` (stage1_train.py:229–295) reports what is effectively training-set accuracy as "held-out".
- Checkpoint selection (stage1_train.py:366–370) cannot detect overfitting, so it drifts toward the last epoch.

The mechanism inventory (stage1_mechanism.py:29–42) has the same problem. Each of the 12 default draws is one stratum, and in deterministic strata:

- every arm's fight is a deterministic function of the stratum;
- the teacher arm reproduces a training fight exactly;
- `--pairs` 13–20 would add exact duplicates that count as independent pairs.

This is the pseudo-replication that CONTRACT.md:165 forbids. The effective training set is also about 26 distinct trajectories, not 144 fights. 57% of training rows (D1 1/2-gun, 54k of 95.4k) are copies of four 150 s timeout fights. That composition is the likely source of the 0.933 hold and the 1.000 nearest-target baselines.

**Suggested fix.**
1. Before training is interpreted, run a cheap, read-only dedupe on the converted arrays. Hash `x`, `labels`, `pos` and `launch` per fight, excluding IDs, and record the number of unique trajectories per stratum and split in a receipt.
2. If the duplicates are confirmed, add real per-draw variation from sealed draw entropy. Options: placement jitter (the contract and mechanism text already speak of matched "placement"), small spawn offsets, enemy spacing, initial HP/cooldown phase. Then recollect. Collection took 435 s, so this is cheap.
3. Until then, label every held-out diagnostic "in-distribution replay (duplicate trajectories)". Treat the mechanism check as 12 single deterministic contrasts, never as 12–20 replicates.
4. Separately, note that the D1-static 1/2-gun teacher fights all time out at 150 s. The teacher never achieves strict elimination there, so this teacher fails the ES eligibility (≥8/10 completed) in those cells.

### M1 — Medium: the quadratic prefix replay blocks training, and any speed fix must not treat N1r and N2 asymmetrically

**Evidence.**
- stage1_train.py:143–156 replays every window from t=0 under no_grad. The cost is about T²/180 ticks per fight per epoch.
- TRAINING_PROJECTION.json: N1 0.02 s/step, N1r about 1.6 s, N2 about 3.5 s; 2,198 minutes in total.
- 3c6ed79 records the refusal. I did not review the in-progress run's code.

**Failure scenario.** The obvious fix is to truncate burn-in to a fixed number of ticks. That approximation is not symmetric:

- **N1r:** a tanh recurrence that probably forgets.
- **N2:** for an isolated gun, phase integrates ω+forcing with no decay. Its only forgetting is the launch reset θ=0, or coupling-driven locking when neighbours exist. Since cos θ enters the fire logits directly (models.py:35), truncated burn-in hands N2 a different input distribution at train time than at deployment, while N1r barely changes.

The arm difference would then partly reflect the training approximation.

**Suggested fix.** Use stateful chronological truncated BPTT:

- Run B fights as parallel streams.
- Process each fight's 90-tick windows in order, and carry detached state across windows under the weights current at each step. The staleness is at most one window of updates; declare it.
- Shuffle the order of fight streams, not windows.

For an exact cheaper alternative for N2, start burn-in at the latest tick where every live gun in the coupled component was reset by a launch, if one exists.

Whatever the fix, keep:

- identical row and step budgets across arms;
- a test that the training-window forward equals `evaluate`'s full-sequence forward at the same weights. This test is missing today; it would have caught any burn-in mismatch.

### M2 — Medium: BC on this teacher cannot separate N2 from N1, and the BC objective may switch the oscillator off

**Evidence.**
- The teacher is a stateless function of the public snapshot (CONTRACT.md:92). N1 sees that snapshot through the encoder, so memory and phase have no imitation advantage beyond a few cache/lock effects.
- The heads sit at or near ceiling (STAGE1_BASELINES.json): target 1.000, move zero-offset 0.933, aim 0.941, start permit precision 0.905.
- Training-only fire counts: start 7,260 positive vs 559 negative; release 5,700 vs 284.
- Each arm has one seed (stage1_train.py:29).

**Failure scenario.**
- **Readings within seed noise:** the three held-out readings will differ in the third decimal, within seed noise, and a reader may still rank the arms.
- **Oscillator switched off:** in N2, start/release BCE on a 93% positive class pushes the +2·cos θ term toward cos θ = 1. The cheapest way there is ω+forcing ≈ 0, which holds θ at the launch-reset value 0. A trained N2 can therefore have a frozen phase and unused K, so the within-N2 ablations show no harm.
- **Fixed motion difference:** N2's motion still differs from N1 through the fixed, untrained J=0.5 drift (CONTRACT.md:121). So any N2-versus-N1 behaviour difference in the mechanism check may come from the hand-set J prior, not from anything learned.

**Suggested fix.**
1. Report, for each arm's checkpoint, the minority-class metrics:
   - start/release hold-class recall (specificity, already derivable from tn/fp);
   - move top-1 on non-hold rows;
   - aim top-1 on non-center rows;
   - balanced accuracy.
2. Run at least three seeds for N1. It costs about 15 minutes in total, and it gives a seed-noise yardstick before any arm is compared.
3. Add N2 learned-law statistics to STAGE1_RESULTS: K, ω, the |forcing| distribution, the phase-velocity distribution and the order parameter on validation.
4. State in the report that a BC difference between arms is not evidence for or against the RRG mechanism on this teacher. Name the J prior as the main N2 motion difference.

### M3 — Medium: the mechanism report has no direct N2-versus-N1/N1r contrast

**Evidence.** stage1_mechanism.py:51–77 pairs every arm only against the teacher. The within-N2 ablations are paired against intact N2 (78–87). Nothing pairs N2 against N1 or N1r on the same draw.

**Failure scenario.** The question "does N2 differ from N1" would be answered by comparing two separately teacher-paired summaries by eye. With H1 in place, those summaries rest on deterministic single fights.

**Suggested fix.** Add paired per-draw contrasts N2−N1r and N2−N1 for deaths, kills, launches/opportunities, the phase order parameter and command-realized motion. Label them descriptive at this sample size.

### M4 — Medium: the trained export parity covers only the first 90 ticks, and the in-fight reset path is never compared

**Evidence.**
- stage1_export.py:82–94 takes ≤90 ticks from the start of each test fight.
- The report and guide call this "held-out full sequences ... launch reset, mid-sequence death" (REPORT_STAGE1.md:7, STAGE1_GUIDE.md:54).
- In the first 3 s there are typically no launches or deaths. Launch/death coverage exists only in the fixture test (test_stage1.py:82).
- Both sides inject launch resets externally (stage1_driver.cpp, phases set to 0 from recorded launches), so the in-fight `Host` reset path is never compared.

**Failure scenario.** Trained parity can PASS while the in-fight Host resets the phase on a different tick, or prunes a dead gun differently, from the Python Replay. N2's fire logits and drift in the mechanism fights then differ from what was trained and checked.

**Suggested fix.**
- Run parity on whole held-out sequences, or at least on windows that contain the first launch and the first death.
- Add an offline check that replays a recorded student fight's positions and launches (DAgger or mechanism `.jsonl`, which already logs `phase_state`) through Python Replay and compares it with the logged phases and actions at 1e-9.
- Correct the "full-sequence" wording until then.

### M5 — Medium: DAgger never trains on D2-shellfire 10-gun, the only stochastic, threat-rich joint cell

**Evidence.** stage1_dagger.py:22–23,33: visits 0–6 (train) are D1-1×2, D2-1×2, D1-2, D2-2, D1-10. Visits 7 (D2-10) and 8 (D1-10) are validation, and visit 9 (D2-10) is test.

**Failure scenario.** Under H1, D2-10 is the only cell with between-draw variation, and the one where joint REACT and volley coordination matter most. Student-visited D2-10 states are labelled but never fitted, so the refits fix compounding errors everywhere except where they matter most. DAgger validation is also all 10-gun, so refit checkpoint selection ignores the sparse cells.

**Suggested fix.** Rotate the split assignment so that each cell type gets training visits, for example a D2-10 training visit in place of one of the duplicate D1-1 visits, and stratify validation across gun counts.

### L1 — Low: fire class weight points the wrong way for this data

stage1_train.py:127 uses neg/pos, bounded to [1,10]. Positives dominate (start 7,260 vs 559), so the weight is 1.0 and the minority hold class, which carries the REACT suppression, gets no up-weighting. Either declare this as intended, or weight whichever class is the minority, with the bound recorded before the fit.

### L2 — Low: aim metrics and support are conditioned on the teacher's target

stage1_data.py:72–76 builds the aim candidates and legality around the teacher's chosen target. stage1_train.py:263 masks aim predictions with that support. With target top-1 ≈ 1 the effect is negligible today, but the metric should be named "teacher-target-conditioned aim top-1". The same applies to DAgger, if student targets diverge.

### L3 — Low: the window order is identical in every epoch

stage1_train.py:109 shuffles once, with seed 41999. All ten epochs see the same batches in the same order. This is matched across arms, so it is not a fairness issue, but per-epoch reshuffling with a declared seed is the standard choice.

### L4 — Low: the budget receipt is overwritten before the refusal check

stage1_train.py:312 writes `STAGE1_BUDGET.json` before line 314 refuses an existing projection. A re-invocation after source edits silently replaces the budget that TRAINING_PROJECTION.json's `budget_sha256` refers to. It matches today (a277d9…). Write the budget only after the refusal check, or write it to an attempt-numbered file.

### L5 — Low: ω is a single global scalar

models.py:24 has one ω for all guns, while C4 has a per-element ω_i. The per-gun forcing tanh(linear(o)) supplies the individual variation, so this is acceptable, but it should be written into the contract's N2 law row as a deliberate projection choice.

## Can the stage answer its questions?

| Question | Answerable now? | What is needed |
|---|---|---|
| Does each network imitate the teacher? | In-distribution only (H1) | Dedupe receipt; draw variation; minority-class metrics (M2) |
| Does N2 differ from N1 under imitation? | No (M2) | Seed-noise yardstick; learned-law statistics; direct paired contrasts (M3) |
| Are the N2 channels used in play? | Descriptive only | Within-N2 ablations exist. Phase-freeze risk (M2) and parity coverage (M4) first |

## Scope and limits

I reviewed source and receipts only, against the stated focus: leakage, masking, budgets, the N2 law, recurrence, export, DAgger, pairing and answerability. I found no label or feature leakage across splits in the code paths, and no teacher-action leakage into observations: the features are pre-policy snapshots, and the recurrent assignment history is the visitor's previous intent. Training-row and step counts match across arms. I did not review the uncommitted code of the run currently in progress, and I did not execute anything.
