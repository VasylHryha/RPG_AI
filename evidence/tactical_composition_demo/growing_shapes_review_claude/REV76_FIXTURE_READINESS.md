READY_FOR_FIXTURES
Reviewer family: Claude
Reviewed execution-pin SHA256: 43b0f5788f00f18b27f1d4f4c70d5729eac1dc4dcbc8ec5044c408a7ed0939fd
Reviewed commit: 79f894d (diff 529bbb4..79f894d, growing_shapes); design DESIGN_0H_REV7.md section 13, including 13.3
Owner recheck request (verbatim): "Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps."

## Checks run

**Synthetic suite**, run once with temp and cache files in the scratchpad: **93 passed in 1.64 s**. The tree stayed clean.

**Pin, checked against HEAD 79f894d:**
- `sha256(REV7_SOURCE_IDENTITY.json)` = `43b0f578…939fd`.
- `rev7_identity.assert_inputs()` **passes** on all 69 pinned files. That includes `DESIGN_0H_REV7.md` checked against `git show HEAD:`, so this time the pin was generated after the final design commit.
- `configuration_sha256` equals the current `CONFIG_SHA256` (revision 7.6, λ = 32, h = 0.005).
- `REV7_SYNTHETIC_CHECKS.json` reports PASS and binds the same pin and file set.

## The 7.6 change, checked against 13.2 and 13.3

1. **D1, D3 and D4 exemption** (`medium/rev7_design.py`, `growth`):
   - The D1 and D4 loop skips `role == 'output'`.
   - D3 picks only from non-output elements past their protection period, so O can never be pruned.
   - Because O carries no cost, every D3 removal lowers the cost, and the loop terminates.
2. **The budget** (`medium/rev7_native.py::budget_counts`). There is one rule for all three uses:
   - N = ordinary elements.
   - The pair term = undirected N^θ pairs with both ends ordinary.
   - The neighbour selection is the real one. Lists are not recomputed without O; O-incident pairs are simply not charged.
   - It is used by `Rev7Native.cost`, which serves live accounting, the D3 loop, event costs and the U/M blocked checks.
   - It is used by `feasible`, which serves admission for B1, B-path, M and U. Admission builds the trial topology with `geometric_graph`, whose ties match native `neighbors`.
   - The cap counts ordinary elements (+1 > 64 → `cap`), so 64 ordinary elements plus one O are allowed. The native cap does not apply, because native growth is never configured.
   - Physical counts (`len(native)`, `growth_counts`, `peak`) still include O, as 13.3 requires.
3. **B-out** (`b_out`):
   - Cap, cost and the `blocked` flag are no longer consulted.
   - Placement is still required: the origin is reserved, and the birth is refused `placement`.
   - Uniqueness is held twice: `b_out` returns early if an output exists, and the native singleton-output cap rejects a second one.
4. **Tests covering the three requested points:**

| Requested coverage | Tests |
|---|---|
| Budget-full B-out | `test_rev76_Bout_succeeds_with_full_cap_and_protected_budget[False/True]`: 64 ordinary elements at cost exactly 64, and over budget with `protected_over_budget`. B-out is accepted once, and a second call is a no-op. `test_rev76_Bout_placement_still_required_when_budget_blocked` checks placement. |
| Isolated permanent O does not pass F5 trivially | `test_rev76_isolated_immortal_output_has_no_drive_root_coverage_or_path`: with D1 and D4 timers far over threshold and a zero lock, O survives. It has no drive (θ̇ = π exactly), is not a root, has no path from any site, gives no coverage, has an undefined P, and costs 0. F5's unchanged E ≥ 0.5 path criterion therefore cannot pass on O's existence alone. A free-running, uncoupled O gives identical own and donor outputs, so A = 0. |
| Admission, live and D3 consistency | `test_rev76_admission_and_live_cost_share_ordinary_cap_and_pairs`: an O-incident pair is admitted free, then live cost = 64 with 65 physical elements, then the next birth is refused `cap`. Ordinary pairs are still charged (`cost`). `test_rev76_cost_excludes_O_incident_pairs_but_retains_actual_topology`, `test_rev76_D3_preserves_lowest_lock_output_and_prunes_ordinary`, and `test_rev76_death_rules_preserve_output_and_remove_ordinary[D1/D4]` complete the coverage. |

5. **Unchanged:**
   - λ, h, N1 (including N1d and N1g), every F1–F9 gate, the stop sequence, the medium RHS and the native image sources. No C++ file changed.
   - The B1, B-path and M/U birth rules, apart from the shared budget function.
   - The only CONFIG changes are `revision`, `output_port` and `fixture_entropy`. The `fixture_entropy` entry declares the F5 and F7 reuse exception from 13.3.

## Findings

1. **LOW, informational, not blocking:** the native C API still has the old cost definition.
   - `gm_cost` and `Medium::couplings()` in `rev7_medium.cpp`/`_c.cpp` still count O and its incident pairs.
   - The Python `Rev7Native.cost` override replaces it on every revision-7 path, and I found no remaining caller of the raw native cost in the revision-7 runner or medium code.
   - **Suggestion:** a later revision could align or retire the native function, so that a future direct caller cannot get the pre-7.6 budget.

No defect found that would silently invalidate N1, F1–F4 or F5–F9.
