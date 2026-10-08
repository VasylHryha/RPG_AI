CHANGES_REQUIRED
Reviewer family: Claude
Reviewed commit: b5cc3cff9bcec07d6731271344baa9d17630ff5a
Reviewed folder: `evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/`
Date: 2026-10-08
Review type: cross-family, read-only development recheck of the first trained results and how they were read. Codex implemented the code. This is not a milestone acceptance.

What I did: I read the committed receipts and the code that produced them. I ran no tests, training, fights, DAgger, mechanism runs or native host, and I did not open `_local/`. A DAgger run was in progress on the machine.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Answers to the specific questions

### 1. Are the identical ablation outcomes real, or a wiring bug?

They are real. Each ablation is applied in both the native and the Python paths:

- **Where it is applied:**
  - The request carries `ablation` (`stage1_mechanism.py:37`).
  - The native Host reads it and validates it (`stage1_native_v2.py:25-26`).
  - The native Host applies it in four places: `host.cpp:22` (held forcing), `host.cpp:24` (phaseStep/motion), `host.cpp:30` (blind move logits) and `host.cpp:48` (launch reset).
  - The logged parity check replays each student fight with the same ablation string (`stage1_mechanism.py:153-155`).
- **The fights do differ underneath.** Within a draw, the ablation arms differ in phase order, command-realized motion, launches, decisions and seconds. Draw NS1-M-dabcc168bb (D1-10) shows it:

  | Arm | Phase-order sum | Command-realized dot sum |
  |---|---:|---:|
  | N2 | 598.1 | 316.4 |
  | frozen_phase | 268.0 | −3.2 |
  | no_reset | 441.9 | — |

- **Why the totals match anyway: the outcome is saturated (finding H1).** Kills and deaths are at a ceiling or floor in 10 of the 12 draws.
- **topology_only is close to a no-op by construction (finding M3).** It matches N2 exactly in 7 of 12 draws.

### 2. Is the identical nonzero-aim 0.206 a bug or a collapse?

It is a real collapse, and the 0.206 overstates it (finding H2):

- **Validation:** nonzero aim is 0/198 for all five models.
- **Test:** all five models hit exactly the same 14/68 rows, 7 in class 1 and 7 in class 7. Five different initializations and three architectures would not land on identical hits by learning. These are almost certainly rows where legality forces the choice.
- **Top-1 against the majority baseline:** aim top-1 is at or below the majority baseline everywhere (test: 1287/1284/1288 correct vs 1288 majority).
- **Error against always-zero:** mean aim error is worse than always-zero for N1 and N2 (2180 and 2331 px vs 2140 px, summed).

### 3. Is checkpoint selection per model?

Yes:

- **Per-model selection:** each worker keeps its own `best/best_epoch` (`stage1_training_worker.py:38,69-70,84`).
- **Epoch 7 is a real minimum for every model.**
- **Why all five pick it:** every arm and every N1 seed sees the same batch order. The order is `random.Random(41999+epoch)` (`stage1_train.py:127`) and does not depend on the seed. That shared, systematic data-order effect is not a bug, but it weakens the seed-noise yardstick (finding M4).
- **N1r's 0.58 vs 0.75:** the test split is 12 fights with 61 start negatives. N1r's test start loss of 0.53 comes from a few confident errors, while its false negatives (16) are actually lower than N1's (25). Read it as small-test noise, not leakage.

### 4. Are the mechanism pairs paired and independent?

They are paired: one seed, cell, guns and orientation per draw, and the variation depends only on the seed (`requests_v2.py:20`). They are independent across draws, with fresh seeds that exclude the collection seeds.

But there is only one draw per (cell, guns, orientation). The 1-gun cells are policy-independent:

- **D2-1:** every arm, including the teacher, produces byte-identical counts.
- **D1-1:** the teacher stalls for 150 s in 12 of 17 collection draws.

So only about 4 draws carry outcome information: D2-10 ×2, D2-2 ×2, plus the one D1-1 o1 perturbation.

### 5. Leakage, budget mismatch, misleading metrics

- **Leakage:** I found none in splits or seeds.
- **Budget mismatch:** there is a documentation conflict. The amendment requires sequential fits with no concurrency credit, but the run used concurrent lanes under an owner cap of 10800 s (finding L1).
- **Misleading metrics:** the pooled kills, deaths and kills-per-minute are misleading (H1, M1).
- **Parity evidence:** the committed mechanism receipt contains no logged-parity evidence (M2).

## Findings

### H1 — High: "networks play near teacher level" and "phase coupling has no outcome effect" rest on saturated outcomes

**Evidence** (STAGE1_V2_MECHANISM_RESULTS.json `all_fights`):

- **Where kills are fixed:**
  - In D1-2 and D1-10, every arm kills everything (4/4 and 12/12).
  - In D2-1, all ten arms are identical (1 death, 1 kill, 15.77 s, 13 launches).
  - In D1-1 o0, every arm times out at 150.03 s with 1 kill.
- **Deaths:** every D2-10 fight loses all 10 guns, so per-arm deaths can differ in one draw only (D2-2 o0, teacher 2 vs nets 1).
- **The only contested cell is D2-10** (2 draws). There the networks are far below the teacher:

  | Arm | Kills | Launches |
  |---|---:|---:|
  | teacher | 11 | 182 |
  | N1 | 2 | 80 |
  | N1r | 6 | 107 |
  | N2 | 2 | 66 |

  Launch-per-opportunity fraction is 0.67 for the teacher and 0.10–0.55 for the networks. The 48 vs 42–46 pooled totals hide this.
- **Pooled kills per minute** (`stage1_mechanism.py:74`) is dominated by the two D1-1 150-s timeouts, about 300 s of the roughly 600 s per arm. The "kpm 5.77" for no_mode_to_geometry comes mostly from one D1-1 o1 draw that ended at 66 s instead of 150 s. no_geometry_to_mode got the same result in that draw, with identical counts.
- **Where no_mode_to_geometry's +6 kills over N2 come from:**

  | Draw | Kills vs N2 |
  |---|---:|
  | D1-1 o1 | +2 |
  | D2-10 o0 | +1 |
  | D2-10 o1 | +4 |
  | D2-2 o1 | −1 |

  The +4 is one draw in which intact N2 is pathological: launch fraction 0.10 (24 launches out of 238 opportunities) and 0 kills.

**Failure scenario.** The owner reads "near teacher" and "phase coupling has no outcome effect". He then moves to DAgger and stage 2 believing the BC students are adequate and the phase channel is inert. In the only cell that tests tactics, the students actually fire at half the teacher's rate or less. And this design cannot show the ablations have no effect: they could not change kills or deaths in 10 of 12 draws whatever they did.

**Fix:**
1. Correct the readings in the commit-message lineage, in docs/PLAN_CURRENT.md and in docs/IDEAS_AND_ROADMAP.md: "near teacher on saturated cells; far below teacher in D2-10; ablation equality is outcome saturation, not evidence of no effect".
2. In `report()`, add a per-draw informativeness flag: outcome identical across all arms, or at a ceiling or floor. Report pooled totals only over informative draws, and per cell.
3. Replace pooled kills per minute with per-cell median time-to-kill, with time-out fights censored.
4. Report launches, launch fraction, damage and dodge per cell as first-class columns.
5. For future mechanism samples, put the draws where outcomes vary (D2-10, D2-2, D1-10 time to clear) rather than spreading them evenly over 12 strata, two of which are policy-independent.

### H2 — High: the aim head did not learn, and nonzero-aim 0.206 is a legality artifact

**Evidence** (STAGE1_V2_RESULTS.json heads.aim):

- **Validation:** nonzero is 0/198 for all five models.
- **Test:** all five models get 14/68 = `class_1_correct:7, class_7_correct:7`.
- **Top-1:** at or below majority (validation 2545–2549 vs 2563 majority).
- **Error:** mean px error is above the zero-offset baseline. Test N2 is 2331 vs 2140, and validation is 7245–7280 vs 6720 for all models.
- **The label comes from the teacher's joint volley planner.** It is a snap to the nearest of 33 offsets (`teacher.cpp:23-25`), with `family/variant` per queue slot. A per-gun policy most likely cannot see its slot in the volley, so nonzero aim is likely unlearnable from the current features.
- **Legality forcing:** evaluation argmaxes over the legal set (`stage1_train.py:301`). When offset 0 is illegal, the choice is forced. That explains identical hits across unrelated models.

**Failure scenario:**
- Every network fires every shell at the zero offset.
- In D2-10, where the enemy dodges, the teacher's spread is gone. Part of the D2-10 deficit is aim, not only fire timing.
- DAgger relabels with the same unlearnable target. The aim head stays collapsed, and its 0.206 is reported as partial learning.

**Fix:**
1. Report aim rows with a legal-set size of 1 (or with class 0 illegal) as forced, separately. Report learned nonzero aim only on unforced rows; on current evidence it is 0.
2. Decide the aim design before stage 2 (owner fork):
   - (a) add the observable inputs the teacher's offset depends on (volley slot or variant, target velocity lead);
   - (b) label aim per gun, not as the planner's joint spread;
   - (c) declare aim scripted and label it "script" under the script-vs-RRG rule.
3. Do not count aim top-1 as a learned head in any comparison until then.

### H3 — High: the no_mode_to_geometry "cost" comes from an untrained motion prior that only N2 carries

**Evidence:**
- **Teacher, N1 and N1r drift:** they deploy with baseline drift at J=0 (`host.cpp:25` `common.J=0`; `dynamics.py:67-70`). The teacher data was collected with the same drift (`movement_baseline: shared_phase_free_A.5_B.5_share.125`).
- **N2 drift:** N2 deploys with J = sigmoid(0) = 0.5. J's gradient is masked (`models.py:26`), and drift is never in the BC loss: positions are engine authority, and drift is added only at deployment (`stage1_runtime.py:166-179`).
- **no_mode_to_geometry is two changes in one arm:** it sets J to 0 (`dynamics.py:52`), which makes N2's motion law identical to the baseline drift the teacher data contains. It also blinds the move logits (`models.py:61-63`, `stage1_runtime.py:77-79`).
- **Phases are near-synchronized:** the learned-law order parameter has mean 0.983 and median 1.0. So `cos(θj−θi)≈1`, and J=0.5 mostly adds about 50% extra constant cohesion.

**Failure scenario.** "The phase→motion path costs kills" gets recorded as an RRG finding. What was actually measured is that adding an untrained, never-imitated cohesion drift to one arm moves it off the training distribution. Removing that drift returns it to the teacher's drift. The comparison among N2, N1 and N1r is confounded the same way: N2 is the only arm that deploys off-distribution motion.

**Fix:**
1. Relabel the result as "untrained J=0.5 drift is off-distribution; removing it restores baseline drift".
2. Split the ablation into `J0_only` and `blind_move_only`.
3. For the main N2-vs-N1 contrast before stage 2, choose one:
   - deploy N2 with J=0 until J is learnable;
   - make J learnable through a channel the training signal can see (outcome or RL stage, or imitate realized motion);
   - give N1 and N1r the identical J=0.5 drift driven by a matched non-learned phase.
4. Say in the report which of these the stage-2 design uses.

### M1 — Medium: K did not train, and phase is mostly a reset-synchronized clock, so K0 and topology_only cannot show much

**Evidence:**
- **K:** learned K = 0.99838, against an initial value of 2·sigmoid(0) = 1.0. Adam took 5160 steps at lr 1e-3, so a consistent gradient sign could have moved it by up to about 5. It moved by about 0.003 in raw parameter. That is gradient-sign noise, meaning no consistent training signal.
- **ω:** it moved from 0 to 0.237.
- **Synchronization:** the order parameter is about 1 and dispersion about 0 (`learned_law`). Guns that launch in a volley reset to θ=0 together (`host.cpp:48`). The phase signal entering the start/release logits (`models.py:35`) and the neighbour state is therefore close to a shared post-volley clock.

**Failure scenario.** The report says "N2 learned K≈1.0". A reader takes the coupling as fitted, and the ablation null as a property of RRG coupling. Neither holds.

**Fix:**
1. Report raw parameter deltas from initialization, and the mean |gradient| per law coordinate.
2. Report order and dispersion per gun-count stratum (1-gun fights contribute order 1 trivially) and separately for ticks before and after a reset.
3. State that K0 and topology_only are not interpretable on static, volley-synchronized drills.

### M2 — Medium: the committed mechanism receipt has no logged-parity evidence

**Evidence:**
- `run()` writes the per-fight `.parity.json` only under `_local/stage1_v2/jobs/mechanism/` (`stage1_mechanism.py:153-160`).
- STAGE1_V2_MECHANISM_RESULTS.json contains the word "parity" zero times.
- The amendment's stop row "Actual-log launch/death coverage absent? record the coverage gap" cannot be checked from committed evidence.
- The coverage depends on the fight: D1-1/D2-1 fights have no deaths among own guns until the end.

**Failure scenario.** A later reviewer cannot confirm that the ablated native fights matched Python. That includes, for example, whether frozen_phase really skipped resets in the logged path. They must trust `_local/`, which is not committed.

**Fix.** Embed per-fight parity summaries in the results file: status, ticks, launches, deaths, decision rows, maximum error, and ablation and weights hashes. Include their combined hash. Do the same for DAgger rounds.

### M3 — Medium: topology_only is close to a no-op on these drills

**Evidence:**
- topology_only equals N2 exactly in 7 of 12 draws, including D1-2 o0 and o1 and D2-2 o0 and o1 (identical phase-order and motion sums).
- The graph radius is 300 px with up to 8 neighbours. Formations barely move, so the frozen tick-1 graph equals the live graph (`stage1_runtime.py:33`, `host.cpp:24`).

**Failure scenario.** "Topology carries no information" gets inferred from an intervention that never changed the topology.

**Fix.** Log, per fight, the fraction of ticks where the frozen and live graphs differ. Report topology_only as "not exercised" where that fraction is near 0.

### M4 — Medium: the N1 seed yardstick covers initialization only and is smaller than the training-order noise

**Evidence:**
- All seeds and arms share the per-epoch shuffle (`stage1_train.py:127`).
- Validation for one model swings 0.6035 → 0.6666 → 0.7284 between epochs 7 and 9. That is about 10× the cross-seed test spread (aim and move SD ≈ 0.002).
- All five models select epoch 7.
- N2's test loss of 0.663 vs N1's 0.671–0.687 is well inside that swing.

**Failure scenario.** An N2-vs-N1 head difference gets read against an SD of 0.002–0.0024 and looks "outside seed noise". The real run-to-run variance, which includes data order and checkpoint choice, is much larger.

**Fix:**
1. For the yardstick, vary the shuffle together with the init seed (for example `41999+epoch+seed`), or add a second shuffle stream.
2. Give N2 at least the same three-seed treatment as N1 before any N2-vs-N1 head comparison.
3. Consider averaging the last k epochs, or using a smaller learning rate, to reduce the swings.

### M5 — Medium: the D2-10 start head under-fires in closed loop, which the offline metrics do not show

**Evidence:**
- Offline, start recall on test is 0.96–0.98 and hold recall 0.87.
- In closed-loop D2-10, cast starts per opportunity are far lower:

  | Arm | Starts | Opportunities |
  |---|---:|---:|
  | teacher | 125 | 147 |
  | N1 | 46 | 174 |
  | N2 (o1) | 25 | 238 |

  Each gun's `start_opportunity` decision is mostly declined.
- This is the compounding-error signature that DAgger targets.

**Failure scenario.** DAgger results get read through the offline heads, which already look near-perfect. The improvement or failure that matters, closed-loop fire rate in D2-10, is not a declared DAgger readout.

**Fix.** Before DAgger results are read, declare the closed-loop per-cell metrics that will be compared before and after DAgger: launch per opportunity, kills, time to kill and dodge in D2-10/D2-2. The offline heads stay secondary.

### L1 — Low: the amendment says fits are sequential, but the run was concurrent under a different cap

**Evidence:**
- CONTRACT_AMENDMENT_STAGE1_V2.md "Training and admission" says: "fits run sequentially under one repository job lock. No wall-time concurrency credit is assumed."
- STAGE1_BUDGET_03.json has `concurrent_fits: true`, slots 4 and `training_cap_seconds: 3600` (default authority, null sha).
- The admission used an owner cap of 10800 s.
- The 46-minute projection takes concurrency credit. The sequential sum is about 87 minutes, which would have been refused at 3600 s.
- The owner did approve parallel fits (TRAIN_CAP note), and STAGE1_GUIDE.md documents it. But the binding amendment and the budget file were not updated.

**Fix.** Add a short amendment row that records the owner's concurrency and 3-hour-cap decision and points to the TRAIN_CAP sha. No rerun is needed; concurrency does not change float64 results.

### L2 — Low: mechanism and DAgger seed hygiene, and overwriting the results file

**Evidence:**
- **Seed exclusion:** DAgger excludes collection and earlier DAgger seeds but not mechanism seeds (`stage1_dagger.py:124-126`). A collision is negligible at 32-bit seeds, but the guarantee is not symmetric.
- **Overwrite risk:** `run()` writes to a fixed path, STAGE1_V2_MECHANISM_RESULTS.json (`stage1_mechanism.py:166`). A post-DAgger mechanism run would need a new inventory, because the weights pins change. It would then overwrite the BC mechanism receipt.

**Fix:**
1. Exclude `jobs/mechanism/INVENTORY.json` seeds in DAgger.
2. Version the mechanism output by weights round (for example `..._BC.json` and `..._DAGGER_R2.json`), and refuse to overwrite.

### L3 — Low: the 1-gun cells are policy-independent, and D1-1 still stalls

**Evidence:**
- In collection v2, D1-1 has 12 of 17 draws timing out with identical counts per orientation, and D2-1 has 4 distinct outcomes in 17.
- In the mechanism sample, all ten arms tie in D2-1.
- The teacher stops starting casts after 13 launches in D1-1 (14 opportunities in 150 s).

**Failure scenario.** One sixth of the mechanism sample and of the training stratum weight goes to cells where no policy difference can show. D1-1 also carries a teacher defect that the students imitate.

**Fix.** Keep D1-1/D2-1 for imitation coverage, but mark them as non-informative in outcome reports. Record the D1-1 teacher stall as a known teacher gap (ES ineligible) and as a candidate scripted-teacher fix.

## What is sound

- Splits are by whole fight, and mechanism seeds exclude every collection split.
- The fire-class weights are training-only. Class weights of (10, 1) for start and release match the recorded counts (386/9347, 162/7554).
- Selection is per model. Export parity passes at 1.1e-13 on all 12 test sequences for every model and every N2 intervention, covering 626 launches and 26 deaths.
- Ablation wiring is consistent across the Python Replay, the native Host and the logged parity check.
- Peak RSS stayed under the 512 MiB cap (N1r 492 MiB).
- The receipts already label the mechanism sample as descriptive, and state the J confound in `interpretation` and `cause_limits`. The problem is the summary reading, not the receipts.

## Before DAgger results are read

1. H1: report per cell and per informative draw, with no pooled kills per minute.
2. M5: declare the closed-loop D2-10/D2-2 metrics as the primary DAgger readout.
3. H2: separate forced aim rows, and treat aim as not learned.
4. M2: commit the logged-parity summaries for the mechanism fights and the DAgger rounds.
5. L2: version the mechanism output before any post-DAgger mechanism run.

## Before stage 2

1. H3: resolve the J confound, either with J=0 for N2 or with a learnable J, and split the no_mode_to_geometry ablation.
2. H2: settle the aim design (owner fork: observable volley slot, per-gun aim label, or scripted aim).
3. M1/M3: use drills where phase diversity and topology change can matter, check that the interventions actually change their target quantities, and report law parameter deltas.
4. M4: use data-order-varied seeds for N1 and at least three N2 seeds.
5. L1: record the owner's concurrency and cap decision in the amendment.
