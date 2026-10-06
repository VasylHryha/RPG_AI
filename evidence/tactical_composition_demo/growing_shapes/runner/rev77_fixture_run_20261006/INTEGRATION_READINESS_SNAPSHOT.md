READY_FOR_FIXTURES
Reviewer family: Claude
Reviewed execution-pin SHA256: 9628282d3407038a6b6947e86cb8ae1b7e7b2ef82fcdd3f9ecd540895c82e42e
Reviewed commit: 4d78114 (diff 1fce0df..4d78114, growing_shapes); design DESIGN_0H_REV7.md section 14, including 14.3
Owner recheck request (verbatim): "Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps."

## Checks run

**Synthetic suite**, run once with temp and cache files in the scratchpad: **108 passed in 1.81 s**. The tree stayed clean.

**Pin, checked against HEAD 4d78114:**
- `sha256(REV7_SOURCE_IDENTITY.json)` = `9628282d…e42e`.
- `assert_inputs()` **passes** on all 69 files, including the design file compared with `git show HEAD:`.
- `configuration_sha256` equals the current `CONFIG_SHA256` (revision 7.7).
- `REV7_SYNTHETIC_CHECKS.json` reports PASS and binds the same pin and file set.

## Section 14 and 14.3, checked against the code

1. **The inclusive boundary is identical in native and Python.**
   - Native: `Medium::strong_neighbors` (`rev7_medium.cpp`) keeps `distance <= sqrt(log(2.0))`.
   - Python: `geometric_graph(strong=True)` keeps `r <= STRONG_LINK_RADIUS = sqrt(-log(0.5))`.
   - The two radii are the same double, 0.8325546111576977 (checked: `sqrt(-log .5) == sqrt(log 2)`).
   - Both use `hypot` of the coordinate differences. The sign order differs, but `hypot` is symmetric, so the distances are the same.
   - The test `test_rev77_native_python_strong_boundary_subset_and_full_mean` checks the exact boundary, one ULP inside and one ULP outside, 2.2 and 3.0, in both implementations. It also checks that G_s ⊆ G.
2. **G_s filters edges after selection.** The full k-nearest N^θ selection is made first, then the edges are filtered by strength. So G_s ⊆ G, with the same direction (j → i). The RHS and the mean normalization still use the full list; covered by `test_rev77_strong_filter_does_not_change_RHS_normalization_or_cost`.
3. **G_s is used for the following:**
   - B-path's site test (`g = strong_influence()`) and its front and back sets.
   - All six trial checks in `geometric_trial`: both `before` and `after` are strong, including `edge_a_to_new`. That is harmless, because r* = 0.556 < r_s.
   - Path exposure E: `endpoint_diagnostics` feeds the per-decision `paths` used by F5's E and by G2.
   - The F1d effective-root records.
4. **The full graph G is kept for the following:**
   - D4 liveness (`timers`: `influence()`).
   - Budget and cost (`native.neighbors`).
   - Qualification (C4 components; untouched).
   - The B-out uniqueness test.
   - F2's mask path, which is stricter on G.
   - Root eligibility is unchanged.
5. **The weak-but-connected scaffold test**, `test_rev77_weak_connected_scaffold_grows_until_strong_path_reaches_O`, runs on both backends.
   - The setup has a path in G but none in G_s.
   - B-path then adds exactly one element per call, four times. Every accepted trial passes all of its checks, O's pin holds, and G stays connected throughout.
   - After that a strong path reaches O, E reports it, and B-path stops.
   - Further tests cover the rest of this item:
     - weak edges are rejected in trials (`test_rev77_trials_reject_weak_edges_preserve_strong_paths_and_clearance`);
     - weak connectivity cannot bypass a budget refusal (`test_rev77_weak_connectivity_does_not_bypass_budget_refusal`);
     - D4, the budget and qualification history survive a weak path (`test_rev77_full_D4_budget_and_qualification_history_survive_weak_path`, both backends).
6. **Unchanged:**
   - λ, h, N1 (including N1d and N1g), the B-out and budget rules from 7.6, the medium RHS and every numeric cut.
   - The only CONFIG changes are `revision` and the `strong_links` block, which declares the uses of G and G_s and the clock rationale.

## Findings

1. **LOW: disclosure only, not blocking. F1's path condition now uses G_s.**
   - **Evidence:** `rev7_fixtures.py` F1: `path=bool(m.strong_influence().forward()&outputs)`. This is the "directed path from an effective driven root to O in ≥ 80%" condition of F1a, F1b and F1c (8.6 item 3).
   - **The gap:** section 14.2 lists G_s for "the effective-root paths of F5 and G2" and says every gate is unchanged. It does not name F1. CONFIG's `strong_links.uses` does declare "effective-root-to-output paths" generically, so the code is consistent with the configuration identity. The 7.7 F1 path cut therefore differs from 7.6's.
   - **Why it is not blocking:** G_s ⊆ G, so the change can only make F1 stricter, never looser. The F1 scaffolds' links are 0.556 or 0.42 m.u., all below r_s.
   - **Recommendation:**
     - Say in the 7.7 fixture report that F1's path fraction is measured on G_s.
     - Optionally report the G fraction beside it; it can be derived from the stored `neighbors` records.

No defect found that would silently invalidate N1, F1–F4 or F5–F9.
