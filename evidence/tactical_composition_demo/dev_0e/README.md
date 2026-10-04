# Experiment 0e — development record (own entropy, `DEV_SPEC.json`; NOT a recorded run; no verdict)

Authority: decision 0028 item 9 (the owner delegated the 0e design decisions; read as authority for the development phase, **[R]**). Scripts, raw results and this README
are committed in the same session. Pools are cached outside the repository (`ZE_CACHE`) and regenerated from the entropy. Code: `../ze_core.py`, `../ze_flat.py`
(tests `../test_ze.py`), new files; nothing frozen was edited.

| Step | Script | Raw result | Finding |
|---|---|---|---|
| 1 | `dev_step1_pieces.py` | `step1_results.json` | Headroom passes: teacher minus rush 0.253 (exact 95% 0.229 to 0.289; rush 0.280, kiter 0.229 per opponent). Learned pieces L pass prequalification (AIM admissible 0.987; MOVE when told the teacher's target 0.974; hold 0.977, approach 0.971, back-off 0.975; at least 17,110 uniquely-best multi-enemy states and 2,058 back-off states per seed). J passes (0.968; 0.973). Reference distance for wire noise 4.72 arena units. One closed-loop cell of 200 episodes costs about 12 s. |
| 2 | `dev_step2_flatplus.py` | `step2_results.json` | **No truly flat network qualifies at 3,000 states**: continuous and 32-direction heads, widths 32 to 128, depths 2 and 3, the best gains +0.002 over rush and the 32-direction heads lose to rush. The per-slot network (one step per enemy slot, the step of the chosen slot: a **structured conventional policy**) beats rush by +0.22 (a_joint 0.86) and is selected (width 32, depth 3, 3,369 parameters). |
| 3 | `dev_step3_matrix.py` | `step3_results.json` | See below: in the original sandbox the connection is used but not useful; the teacher-necessity gate fails. |
| 4 | `dev_step4_task.py` (task variants in `../tactics_e2.py`, declared before measurement) | `step4_results.json` | Fixed rule selects **V3** (glass-cannon ranged units, tank fighters, random starts, damage-first doctrine); V1 and V2 (front/back-line formations) fail. |
| 5 | `dev_step5_v3.py` | `step5_results.json` | Steps 2 and 3 repeated on V3; settings for the registration. |

## Step 3 (development seeds 3 to 7, 100 episodes per opponent per cell): the task cannot test the connection

| Cell | Win score | Joint fidelity |
|---|---|---|
| rush | 0.386 | |
| teacher (O,O) | 0.634 | 1.000 |
| teacher's MOVE, AIM = nearest enemy (D,O) | **0.636** | 0.846 |
| learned pieces (L,L) | 0.610 | 0.962 |
| (L,L), message replaced by the nearest enemy's position | **0.637** | 0.861 |
| (L,L), message = a wrong living enemy | 0.449 | 0.086 |
| (L,L), message zeroed | 0.093 | 0.307 |
| teacher's AIM, approach-only MOVE (O,D) | 0.360 | 0.535 |
| (L,O) / (O,L) | 0.640 / 0.607 | 0.987 / 0.974 |
| (J,J) / (J,L) / (L,J) | 0.613 / 0.612 / 0.597 | 0.940 / 0.940 / 0.962 |
| per-slot conventional policy | 0.578 | 0.839 |

- **In this sandbox choosing a target has no value for winning**: the teacher with nearest-enemy targeting plays as well as the teacher (0.636 against 0.634), and the learned unit whose MOVE message is replaced by the nearest enemy's position plays slightly better than intact (0.637 against 0.610). The wire is **used** (a wrong or zeroed message is heavily punished) but its specific content is **not useful** against a trivial default. The registered teacher-necessity gate (proposal section 7) therefore fails for AIM and for the AIM-to-MOVE connection: under the stop rule the drafter revises the task (a new task revision in new files) before any registration.
- MOVE is what matters (approach-only loses 0.27 and falls below rush).
- Replacement and swap contrasts look within their bars (largest loss: learned MOVE, about −0.027 on win score).
- The directed sensitivity control works (reversing the message: fidelity 0.962 to 0.294); the relabel and sham controls equal intact exactly.
- **A scale fault of ±10% costs about 0.13 fidelity even for the teacher** (scale 0.9: teacher 0.858; and the teacher's play drops to 0.499 while the learned unit keeps 0.601): the task's hold band is sharp, so an absolute fidelity bound under scale faults would test the task, not the wire. The stability predicate for scale faults must be relative to the teacher under the same fault (a design change made in development, before any registration).
- Cost: about 163 s of closed-loop play per seed for 30 cells at 100 episodes per opponent (about 0.03 s per episode); 30 seeds at 300 episodes would be about an hour of wall time on 8 workers under this machine's load.

## Step 4: a task in which the connection can matter (seeds 10 to 14, 200 episodes per opponent, scripted policies only)

| Variant | teacher | rush | nearest-enemy AIM | step toward nearest | approach-only | gates |
|---|---|---|---|---|---|---|
| V1 formation, original units, ranged-first | 0.395 | 0.409 | 0.590 | 0.220 | 0.163 | headroom and AIM fail |
| V2 formation, glass/tank units, damage-first | 0.550 | 0.461 | 0.589 | 0.535 | 0.305 | headroom, AIM, connection fail |
| **V3 random starts, glass/tank units, damage-first** | **0.759** | 0.435 | 0.613 | 0.596 | 0.396 | **all pass** |

V3 necessity losses (teacher minus each): AIM 0.137, connection 0.152, MOVE 0.357; headroom 0.328 (rush 0.395, kiter 0.263 per opponent).

## Step 5: V3 with learned pieces (search seeds 15 to 17; pilot seeds 20 to 24, 100 episodes per opponent per cell)

- **No truly flat network qualifies on V3 either**: the best continuous-head network (width 128, depth 2) scores 0.452 against rush 0.433 (+0.04). The per-slot structured conventional policy (width 32, depth 2, 2,313 parameters) scores 0.728 (+0.32) and is the registered conventional comparator `Fp`; the best flat network is registered as `Fflat` (descriptive, gated).
- Pilot (win score / joint fidelity): teacher 0.760 / 1.000; (L,L) 0.742 / 0.973; (L,O) 0.766; (O,L) 0.737; (J,J) 0.738; (J,L) 0.750; (L,J) 0.729; nearest-enemy AIM with the teacher's MOVE 0.609; approach-only MOVE 0.384; **(L,L) with the nearest-enemy message 0.575 / 0.622** (the connection now matters: +0.167); wrong message 0.478; zeroed 0.086; `Fp` 0.747 / 0.870 (as good as the pieces in play); `Fflat` (best flat) 0.45.
- Prequalification on V3: L AIM admissible 0.992, MOVE 0.981 (hold 0.986, approach 0.982, back-off 0.964); J 0.976 and 0.977; per seed about 14,800 uniquely-best multi-enemy states and 1,480 back-off states.
- Faults: noise 0.02 and wrong-target 0.01 cost at most 0.004 win and 0.010 fidelity; **scale 0.9 costs the learned unit 0.053 win but the teacher 0.125**, and scale 1.1 costs both about 0.025, with fidelity losses close to the teacher's (relative fidelity losses −0.006 to −0.047, all smaller for the learned unit). Stability under scale faults is therefore registered relative to the teacher.
- Precision: per-seed paired win contrasts have a spread of 0.001 to 0.034 at 100 episodes per opponent (cuts and replacements 0.01 to 0.02); at 300 episodes and 30 seeds the exact intervals are narrow compared with the 0.02 to 0.05 bars. Reference distance for wire noise on V3: 4.97 arena units.
- Cost: about 207 s per seed for 30 cells at 100 episodes; at 300 episodes and 32 cells about 600 s per seed, about an hour for 30 seeds on 8 workers under load.

## Design decisions made in development (before any registration)

1. Task: V3 (fixed selection rule, step 4). 2. Conventional comparator `Fp` = the per-slot structured conventional policy (step 5 selection); the best truly flat network `Fflat` is reported and gated. 3. Stability under scale faults is judged relative to the teacher under the same fault; noise and wrong-target faults absolutely. 4. 300 episodes per opponent per cell. 5. Every gate is enforced in `ze_run.py` (headroom, teacher necessity, baseline qualification, pool counts, start load).
