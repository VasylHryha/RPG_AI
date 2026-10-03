# Experiment 0d Part A — development phase (own entropy; NOT a recorded run; no verdict is taken from anything here)

Authority: owner message "continue then" read as approval to start the development phase of `PROPOSAL_0D.md` revision 2 (decision 0028, item 7, **[R]**). Scratch scripts, raw results and this
README are committed in the same session (AGENTS.md pilot rule). The development entropy (`DEV_SPEC.json`) is not used by any recorded run and is distinct from every `SPEC*.json`.
Pools are cached outside the repository (`ZD_CACHE`, default `/tmp/zd_cache`) and regenerated deterministically from the entropy.

| Step | Script | Raw result | What it did |
|---|---|---|---|
| 0 | `../test_zd.py`, `../tcd_common/test_common.py` | (tests) | finite-difference checks of the network and of the S1 route (soft mode and the exact derivative of the straight-through surrogate), exact reproduction of the recorded training recipe, vectorized teacher equals the scalar rule |
| 1 | `dev_pilot.py` | `pilot1_results.json` | all five models at one default setting on 3 seeds; pieces alone and connected |
| 2 | `dev_tune.py` | `tuned.json` | the registered tuning: 12 shared settings, 5 seeds (0–4), objective mean validation `a_joint` |
| 2b | `dev_tune2.py` | `tuned2.json` | the one registered grid extension (every family had a value on the boundary): 12 more shared settings, selection over 24 per family. After it a boundary value is accepted and reported |
| 3 | `dev_gates.py` | `gates_results.json` | adequacy gates, spread of every contrast and the seed count, on 10 seeds (5–14) never used in tuning |
| 4 | `dev_cost.py` | `cost_run/` | full-size cost of the registered job through the real harness on fresh entropy (`cost_spec.json`) |

## Findings (development seeds; descriptive; they set settings and caps, they are not results)

- **The pieces connect without loss.** For C and S1 the joint score equals the product of the right-enemy rate and the step success when told the teacher's target (connection gap 0.000 on average over seeds). The flat models lose in the **step**, not in the connection: their step success when told what to act on is 0.58–0.60 (tuned) against 0.97 for the pieces.
- **Tuning moves the flat model a little.** Mean validation `a_joint` over the 5 tuning seeds: F0 (recorded recipe) 0.49 (pilot), F1 tuned 0.551, F2 tuned 0.536, C 0.962, S1 0.942.
- **Tuned settings** (`tuned2.json`): F1 hidden 8, lr 0.0003, wd 0.01, 8,000 steps (357 parameters); F2 hidden 32, lr 0.0003, wd 0.01, 16,000 steps (3,204); C hidden 16, lr 0.001, wd 0.0001, 32,000 steps (787); S1 hidden 64, lr 0.003, wd 0.001, 16,000 steps (9,283). Boundary values after the extension (accepted, reported): F1 lr and wd; F2 lr and wd; C steps; S1 hidden. F* = F1. **Parameter counts differ widely** (S1 has 12 times C's): the specification reports them and the result must be read with that in mind.
- **Gates on seeds 5–14** (`gates_results.json`): C mean `a_joint` 0.957 (gate 0.90 passed); S1 scorer admissible 0.967 and step success on moving states 0.921 (gate 0.85 passed); all five models had at least 30 states in every stratum on every seed. Medians: F0 0.467, F1 0.541, F2 0.535, C 0.957, S1 0.939.
- **Spread and seed count:** standard deviation of the per-seed paired differences E0 0.021, E1 0.016, E2 0.007, E3 0.020, T1 0.026, T2 0.009; the rule `1.96 × 1.253 × max(sd) / √S ≤ 0.015` gives S = 30, so equivalence is reachable at 30 seeds (a normal-approximation sensitivity calculation, not a measured power).
- **What this suggests for the recorded run, and what it does not.** The development data already point toward "the gain is the structure" (S1, trained jointly, is within about 0.02 of C and 0.4 above the flat models). That is an expectation, not a result: it uses different seeds, the margins and intervals have not been applied, and the recorded run decides.
- **Defect found and fixed during implementation:** the discordance rule was undefined for non-directional verdicts (a first implementation made EQUIVALENT unreachable with enough seeds). Fixed in `PROPOSAL_0D.md` section 4 and `zd_run.py` before registration.

## Cost (step 4)

Step 4 ran 8 seeds at full size on 8 workers (one wave) through the real harness on fresh entropy (`cost_spec.json`): wall **576.7 s** (jobs 576.6 s, evaluation 0.1 s), children CPU 1,335 s, peak 0.33 GB per worker,
all 8 seeds complete. Per seed 563 to 576 s; mean fit seconds at N = 3,000: F0 3.2, F1 2.5, F2 10.4, C 16.5, S1 60.8; closed-loop play 175 s per seed. Thirty seeds on 8 workers are four waves, so about 38 minutes;
caps set in `SPECIFICATION_0D.md` section 4 (soft 3,600 s, hard 3,900 s, evaluation 300 s).

**Disclosure: this cost run also executed the verdict code on 8 development seeds.** Its output (`cost_run/SUMMARY.json`) shows V1 SUPPORTED, V2 EQUIVALENT, V3 SUPPORTED, V4 SUPPORTED, V5 REFUTED, with E1 median 0.411 (interval 0.401 to 0.420)
and E2 median 0.017 (0.013 to 0.027). It was not used to choose anything: every setting, margin, rule, seed count and cap had already been fixed from steps 1 to 3 and from the specification text, and the recorded run uses new
entropy. It means the development phase already saw a preview of the likely answer; the recorded run can still refute it.
