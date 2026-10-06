READY_FOR_FIXTURES
Reviewer family: Claude
Reviewed execution-pin SHA256: 27a3c46254cbbba16c1eafa48b34379bc40044bcbec08dcebad0cda1ca9d4768
Reviewed commit: a378822 (diff d74fbe2..a378822, growing_shapes); design DESIGN_0H_REV7.md section 16 and 16.1 (section 15 superseded)
Owner recheck request (verbatim): "Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps."

## Checks run

**Synthetic suite**, run once with temp and cache files in the scratchpad: **122 passed in 1.64 s**. The tree stayed clean.

**Pin, checked against HEAD a378822:**
- `sha256(REV7_SOURCE_IDENTITY.json)` = `27a3c462…d4768`.
- `assert_inputs()` **passes** on all 69 files, including the design file compared with `git show HEAD:`.
- `configuration_sha256` equals the current `CONFIG_SHA256` (revision 7.9).
- `REV7_SYNTHETIC_CHECKS.json` reports PASS and binds the same pin and file set.

**Scope of the code diff:** only `rev7_design.py`, `rev7_medium.cpp` (`strong_neighbors`), `rev7_config.py`, `rev7_identity.py` (the pinned review file), `rev7_verify.py` (temp directory names) and the tests changed.

## Section 16 and 16.1, checked against the code

1. **The predicate and denominator are the same in native and Python.**
   - **Native** (`Medium::strong_neighbors`):
     - `degree = row.size()` is taken from the unpadded `neighbors()` row before any filtering, which is the receiver's full held N^θ list.
     - The rate is `phase_scale*p.K*std::exp(-r*r)/degree`.
     - An edge is kept iff `rate >= 0.5`. The test is written `!(rate>=0.5)`, so it is inclusive and a NaN counts as weak.
   - **Python** (`geometric_graph(strong=True)`):
     - `held` is the same top-k list with r < 3, in the same array-index tie order.
     - The rate is `phase_scale*K*math.exp(-r*r)/len(held)`.
     - The operation order is identical: (λ·K)·exp(−r²)/n.
     - r comes from `hypot` of the coordinate differences, which is sign-symmetric with native `distance`.
   - **The live values:**
     - λ comes from the medium's own policy, both natively and in the Python path (`native.policy()[0]`); K comes from `params.K`.
     - The degree is recomputed after a trial insertion.
   - **Boundary tests, on both backends:**
     - `test_rev79_exact_coefficient_inclusive_boundary` uses coincident points, so exp = 1 exactly. With K one ULP below 1/64, at 1/64 and one ULP above, it gives false, true, true; K = 0 and K < 0 give false.
     - `test_rev79_native_python_strong_distance_boundary_subset_and_full_mean` checks that the strong graph is a subset of the full one and that the dynamics' averaging still uses the full count.
     - `test_rev79_full_receiver_degree_direction_and_weak_neighbor_dilution` covers a strong root→O edge, its weaker reverse edge (the receiver degree differs), a weak extra neighbour that removes root→O's strength by raising the receiver degree, and the restoration after that neighbour is silenced or removed.
     - `test_rev79_live_scale_K_and_trial_post_insertion_degree` covers the live λ and K and the post-insertion degree.
2. **The weak-but-connected test still exercises the rule.**
   - The setup has a root at 3.2 and an intermediate at 2.644 with O at the origin. The last link has r = 2.644, w ≈ 9e-4 and c ≤ 0.03 /s, so it is weak at any degree. The scaffold is therefore connected in G but has no path in G_s.
   - B-path then adds strong links until a strong path reaches O, and E reports it. This runs on both backends.
   - It now takes 2 births instead of 4, because the coefficient rule admits longer links than the 7.7 radius did.
3. **Where each graph is used:**
   - G_s is used exactly as in 14.2: the B-path site test, its front and back sets and all trial checks, path exposure E, the effective-root path records, and F1's path fraction (now stated in 16 as "as implemented").
   - The full graph G is still used for D4 liveness (`timers`), the budget and cost (`budget_counts` over `native.neighbors`), qualification and the RHS. None of these were touched in this diff.
4. **Unchanged:** λ, h, N1 (including N1d and N1g), every F gate and cut, the 7.6 output-port and budget rules, and the medium RHS. The only CONFIG changes are `revision` and the `strong_links` block, which records the formula, the inclusive comparison, the full receiver degree and the provisional clock status.

## Findings

No defect found that would silently invalidate N1, F1–F4 or F5–F9.

**Observations (not defects; for reading the fixture results):**
1. **The strong graph depends on degree, so it is not monotone in births.**
   - A new weak neighbour raises a receiver's degree and can weaken an existing strong edge. This is the intended "full receiver degree" semantics, and it is tested.
   - B-path trials guard against it (`paths_kept`), but B1, M and U births do not. G_s-based E can therefore drop after an unrelated birth.
   - The F5 report should read E's time course with this in mind.
2. **Evaluator copies with lesions or comparators.**
   - The predicate uses λ·K (so `k_zero` copies, with K = 0, have no strong edges). It ignores lesions.
   - In `output_channel` copies the lesioned O's incoming edges still count as strong, although their RHS coupling is zero.
   - This has no verdict effect: F5's E is computed from the intact (`own`) decisions only. Any descriptive path exposure reported from lesioned copies should be labelled structural.
