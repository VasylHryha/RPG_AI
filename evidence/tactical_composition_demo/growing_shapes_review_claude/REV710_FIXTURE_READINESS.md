READY_FOR_FIXTURES
Reviewer family: Claude
Reviewed execution-pin SHA256: ebc58aa2fa30509356f97b079cec0f8c089df88047f10f0aad6a9c95cbac0071
Reviewed commit: ff99704 (diff 75ecccc..ff99704, growing_shapes); design DESIGN_0H_REV7.md section 17, including 17.3
Owner recheck request (verbatim): "Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps."

## Checks run

**Synthetic suite**, run once with temp and cache files in the scratchpad: **132 passed in 1.82 s**. The tree stayed clean.

**Pin, checked against HEAD ff99704:**
- `sha256(REV7_SOURCE_IDENTITY.json)` = `ebc58aa2…0071`.
- `assert_inputs()` **passes** on all 69 files, including the design file compared with `git show HEAD:`.
- `configuration_sha256` equals the current `CONFIG_SHA256` (revision 7.10).
- `REV7_SYNTHETIC_CHECKS.json` reports PASS and binds the same pin and file set.

**Scope of the code diff:**
- Changed: `medium/rev7_design.py` (`b_path` only, plus the `path_waiting` counters), `rev7_config.py` (`revision` and a new `B_path` block), `rev7_reporting.py` (`b_path_waiting`, which is descriptive, plus an interpretation row), `rev7_fixtures.py` (it attaches `B_path_waiting` to F5, descriptively), `rev7_identity.py` (the pinned review file) and `rev7_verify.py` (temp directory names).
- New: `rev710_delivery/deliver.py` (a delivery helper) and the tests.
- **No native or C++ file changed.**

## Section 17.3 (R710-4), checked against the code

1. **Snapshot.** At the start of `b_path`, the code computes `initial = strong_influence()` once. It then builds `gaps` = {site: deficit} for the active sites that have no G_s path. The deficit is `deficit(native, F_s, T)`: the minimum Euclidean distance between the strong forward set and the output backward set. An empty set gives `inf`.
   - The snapshot is taken after the same check's D1/D4/D3 and B-out steps. That is the start of the B-path check within the growth check; the D-rules and B-out are unchanged.
2. **Order.** The code is `sorted(gaps, key=(deficit, (site − pointer) mod 8))`, where the pointer is its value before this check's advance.
   - Python orders `inf` above every finite value, and equal `inf` values fall through to the rotating tie key. Infinite deficits therefore join the rotating tie order exactly as specified.
   - NaN cannot occur, because distances are finite and `min` defaults to `inf`.
3. **The pointer advances once per check,** unconditionally at entry, even when no site is eligible.
4. **The topology is re-evaluated per site.** The strong graph, F_s and T are recomputed before each site's trial. A site connected by an earlier birth in the same check is skipped and reported as `connected_by_earlier_birth`.
5. **Native and Python identity.** The ordering is one shared Python routine. The only backend-dependent input is G_s, which is native `strong_neighbors` or the Python `geometric_graph`; its parity was established in 7.9.
   - `test_rev710_native_reference_multisite_order_events_and_geometry_identical` compares the order, the events and the resulting geometry across backends.
   - Ties and infinite deficits are covered on both backends by `..._shortest_deficit_overrides_pointer_and_exact_ties_rotate` and `..._no_root_infinite_ties_empty_checks_and_wait_pause_reset`.
6. **Unchanged:**
   - The maximum of 2 births per check, with `quota` terminals for the rest.
   - The post-trial conditions on G_s, clearance and the budget.
   - The terminal codes, B1, B-out, the D-rules, the 7.9 strong-edge predicate, λ, h, N1 and every F gate.
7. **Waiting reports** (R710-3, R710-5) cover all 8 sites at every check: eligible, unserved, current and maximum waits, accepted births and outcomes.
   - Inactivity pauses the wait. An acceptance or an observed connection resets it.
   - `finite_wait_bound=False` and `used_in_verdict=False`.
   - The windowed `descriptive()` summary filters events by time before calling `b_path_waiting`.
8. **New-behaviour tests** (`..._empty_start_multiple_sites_completes_bridge_before_budget`, `..._far_site_quota_wait_is_reported_and_shared_connection_rechecked`) cover the intended effect and the reported starvation, on both backends.

## Findings

No defect found.

**Observation, not a defect:** as the design itself states (R710-3, R710-5), the rule has no finite service bound, and F5's max(E) can be met by a single site. Read the per-site `B_path_waiting` and E rows alongside the F5 verdict.
