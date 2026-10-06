READY_FOR_FIXTURES
Reviewer family: Claude
Reviewed execution-pin SHA256: e66c8969d434f475c4289b6d09b048940d148055567c7c1acfc8bd2652fde357
Reviewed commit: 7510a29 (diff 316991e..7510a29, growing_shapes); design DESIGN_0H_REV7.md section 18 with amendment 18.3 and notes 18.4
Owner recheck request (verbatim): "Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps."

## Checks run

**Synthetic suite**, run once with temp and cache files in the scratchpad: **154 passed in 1.93 s**. The tree stayed clean.

**Pin, checked against HEAD 7510a29:**
- `sha256(REV7_SOURCE_IDENTITY.json)` = `e66c8969…e357`.
- `assert_inputs()` **passes** on all 69 files, including the design file compared with `git show HEAD:`.
- `configuration_sha256` equals the current `CONFIG_SHA256` (revision 7.11).
- `REV7_SYNTHETIC_CHECKS.json` reports PASS and binds the same pin and file set.

**Scope of the scientific code diff:**
- Changed: `medium/rev7_design.py`, `rev7_config.py` (`revision`, `B_path`, `timers.output_first`), `rev7_reporting.py` (an interpretation row), `rev7_identity.py` (the pinned review file), `rev7_verify.py` (temp directory names) and the tests.
- **Unchanged:** no native or C++ file, `rev7_control.py`, `rev7_run.py`, `rev7_fixtures.py` or `rev7_protocol.py`.
- **Outside the scientific path:** the other new `.py` files are the 7.10 run's analysis and delivery scripts and the 7.11 delivery helper.

## Section 18, 18.3 and 18.4, checked against the code

1. **Live predicate** (`output_first()`): `any(G_s roots) and not any(G_s path(s))`, evaluated on the current strong graph.
   - Roots are computed live. They exclude O and silent, gain-0 and inactive-site members. So death, silencing, zero gain or loss of drive that leaves no root makes the predicate false, and B1 resumes.
   - The test `test_rev711_active_preready_freeze_and_immediate_bootstrap_after_root_loss[gain/silence/death/inactive_drive]` runs on both backends.
2. **B1 deferral:**
   - `b1` evaluates the predicate **before each site request**. A ready, active site under the predicate gets a `deferred_output_first` terminal with zero attempts, and its timer is kept.
   - The first root accepted within a check therefore defers the later sites in that check.
   - Under the predicate, `timers()` freezes all novelty timers (the 8.9 freeze), and the config declares this.
   - **Bootstrap:** with no root, B1 runs normally, so the 18.3 deadlock is closed. This is covered by `test_rev711_empty_start_bootstraps_one_root_then_completes_static_bridge` on both backends.
3. **B-path in output-first mode.** The mode is snapshotted at the start of the check together with the 17.2 order.
   - The smallest-deficit site is retried only after an acceptance, and each request rebuilds the strong graph and receiver degrees.
   - The next site is served only after a connection (the `while not path` exit) or a finite exhaustion. Each request searches 8 pairs × 13 rotations.
   - A cap or cost refusal stops service for the check. Later sites log the same refusal with zero attempts.
   - **The total per check is 2:** once `len(added) >= 2`, every remaining site gets a `quota` terminal and the retry loop breaks.
   - **Connected mode is unchanged from 17.2:** one request per missing-path site.
   - Tests on both backends cover the nearest site advancing twice, a blocked bridge exhausting finitely, a resource stop, partial acceptance then exhaustion keeping the birth count, and a connection releasing the next site.
4. **Native and Python.** All of the logic is shared Python, and its only backend-dependent input is G_s, which is parity-tested since 7.9. The new contracts are parameterized over both backends.
5. **Control M** (`rev7_control.Matched.check`, unchanged) still mirrors the intact run's accepted B1 births (`birth_index`, filled from `b1`'s accepted list). It does not consult its own predicate; covered by `test_rev711_matched_control_bypasses_own_deferral`. Control U is unchanged.
6. **Unchanged:** cap, cost, the D-rules, O's protection, the strong-edge rule, λ, h, N1, every F gate and the stop sequence.

## Findings

No blocking defect.

1. **LOW, theoretical; unreachable in the registered runs: the predicate does not require O to exist.**
   - If an effective root existed while there was no output, `output_first()` would be true, because no path can exist without O. B1 would then be deferred while B-path ends `no_output`, a stall until B-out succeeds.
   - B-out runs before B1 and B-path in every growth check and is budget-exempt. O is never removed (7.6), and the empty start creates O at the first check, before any root.
   - So the state needs B-out to be refused `placement` (an element within 0.05 of the origin) while a root exists. No registered start (empty or F5(ii)) reaches that state.
   - **Optional hardening for a later revision:** add `and g.outputs` to the predicate.
2. **Observation (disclosed in CONFIG `escape='none while root persists without a path'` and in 18.4):** while a root persists and every B-path request exhausts, for example on clearance, B1 stays deferred until the horizon. The failure gates, not a timeout, then decide. Per-site waiting and the `deferred_output_first` counts should be read with the F5 result.
