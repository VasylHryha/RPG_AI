READY_FOR_FIXTURES
Reviewer family: Claude
Reviewed execution-pin SHA256: f370c3b5ea17cf0b3c751de794de0c8ab1dffdb35cbffdc35d81f9b8280c3ce5
Reviewed commit: 776d208 (diff 233bd5d..776d208, growing_shapes); design DESIGN_0H_REV7.md sections 11 and 11.1 (revision 7.4)
Owner recheck request (verbatim): "Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps."

## What I checked

- **Code read:** the whole 7.4 diff to the revision-7 source code. The recorded 7.3 fixture evidence was not reviewed beyond file names.
  - Native: `rev7_medium.cpp`/`.hpp`/`_c.cpp`.
  - Python: `rev7_rhs.py`, `rev7_design.py`, `rev7_config.py`, `rev7_protocol.py`, `rev7_qualification.py`, `rev7_run.py`, `rev7_fixtures.py`, `rev7_execution.py`, `rev7_verify.py`.
  - The new and changed contracts in `test_rev7.py`.
- **Synthetic suite**, run once with temp and cache files in the scratchpad: **77 passed in 3.37 s** (3.69 s wall). The repository tree stayed clean.
- **Pin:** `sha256(REV7_SOURCE_IDENTITY.json)` = `f370c3b5…3ce5`.
  - `assert_inputs()` passes on all 68 pinned files, and the committed designs match `git show HEAD`.
  - The pin's `configuration_sha256` equals the current `CONFIG_SHA256`, which binds `revision 7.4`, `phase_scale 32`, `excursion.h 0.005` with 20 substeps, and N1 at h 0.005/0.00125 with 20/80 substeps.
  - `REV7_SYNTHETIC_CHECKS.json` reports PASS and binds the same pin and file set.
  - `build.json` is `rev7_rhs_v1`. Its source hashes are re-verified when the library loads, so the image matches the current sources.

## The focus items, checked

1. **λ = 32 and h = 0.005 in every mode.**
   - **Native and Python:** the native default `phase_scale` is 32. The setter and snapshot loader accept only 1, 8 or 32, and the Python reference reads λ from the native policy.
   - **Every medium constructor** defaults to `h = PRODUCTION_H`:
     - live `Run`;
     - controls M and U, which share the run's medium;
     - scaffolds, N1, the single-oscillator baseline and F3/F4, which now step `round(0.1/h)` times at `m.h`.
   - **Recovery futures** clone `saved`, which carries `h` and the native policy.
   - **Evaluation copies** rebuild `h`, λ and the comparator flags from the template's new, validated `solver_policy`.
   - I found no remaining hard-coded 0.02, λ = 8 or 5-substep loop in the revision-7 sources.
2. **Neighbour lists held per substep.** Each `step(h)` call, native and reference, recomputes N^θ and N^x once and holds them over its 4 stages. The carrier advances at 0, h/2, h/2 and h. Contract: `test_substep_lists_held_stage_carrier_and_single_frame`, at both h.
3. **E_i accumulation.** `integrate` sums `h · max-stage |θ̇ − π|` over `round(0.1/h)` substeps: 20 or 80. Contract: `test_frame_bound_sums_stages_and_recorded_endpoints[h]`. The π/2 cuts, pair-only policy and 80-of-100 rule are unchanged.
4. **Once-per-world-step updates.** Adaptation, gain, reward, timers and growth still run once per `integrate` call (one world step) in `Run.episode`. Nothing was moved inside the substep loop.
5. **N1.**
   - Every case runs at λ = 32 (native default) with h = 0.005 against 0.00125, and records per-run E_i.
   - N1f is the F1c state: S at 3.2, five intermediates at 3.2 − 0.556·j with g = 0, and O pinned at (0, 0). The site is (4, 0), k = 2, stepping to π/2 at t = 8, run to 24 s (240 endpoints), with entry measured on O. Contract: `test_rev74_configuration_identity_and_N1f_literal_recipe`.
   - The tolerances are unchanged.
   - Individual and used-pair invalid counts, and their coarse/fine disagreements, are reported descriptively.
6. **F1d.** λ ∈ {1, 8, 32} on F1b at h = 0.005 (20 substeps), with identical starts and input. It is descriptive.
7. **F1c gate.** The gate is unchanged: entry by 16 s, hold through 24 s, path, access, and persistence ≥ 80%. The new outputs are descriptive only: the sustained entry delay, the error at t = 12 s, and `four_second_margin_met`, with `margin_used_in_verdict=False`.
8. **Native/Python parity** is covered at λ ∈ {1, 8, 32} × h ∈ {0.005, 0.00125} × every comparator mode. The receipt revision is now 7.4.

## Findings

1. **LOW: N1f's hold agreement is reported but not gated** (`rev7_fixtures.py`, `compare_n1`: `entry_hold_through_24`, `hold_used_in_verdict=False`).
   - **What 11.1 says:** N1f is compared "including entry and the hold". The implementation gates only entry agreement (≤ 0.1 s, or both absent). The hold result for each run is reported, but a disagreement between the two runs does not fail N1.
   - **Why it matters:** the 7.3 F1c miss was 0.306 against 0.3. If F1c sits that close to the 0.3 rad cut again, the coarse and fine runs could disagree on the hold, even though they agree within the 0.01 phase tolerance. The F1c verdict would then not be numerically resolved, and nothing would flag it.
   - **It is not blocking**, for three reasons:
     - the phase tolerances still gate N1;
     - the per-run holds are recorded, so the case is visible in the receipt;
     - entry disagreement already fails.
   - **Recommendation:** in the fixture report, state explicitly whether the two N1f holds agree. If they disagree, treat the F1c verdict as numerically unresolved. A later revision could gate it with the same "only one holds → FAIL" rule as entry.
2. **OBSERVATION (design risk, carried over from finding 4 of the 7.3 review):** with λ = 32, a driven element's first-frame excursion after a cue change grows further. The per-frame bound is roughly the whole phase jump, so π/2 flags will be more frequent than at λ = 8. Qualification windows, screened over the whole cohort, may then be rarely valid. This is a design property, not a code defect. It is now measured descriptively by the F5 `qualification_validity` and `estimator_validity` rows. Read them before any development decision.

No defect found that would silently invalidate N1, F1–F4 or the later fixtures.
