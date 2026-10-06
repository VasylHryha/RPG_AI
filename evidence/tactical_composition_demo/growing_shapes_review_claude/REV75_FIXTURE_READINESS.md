CHANGES_REQUIRED
Reviewer family: Claude
Approved execution pin: NONE. The delivered pin df5b19603e8fe89ff28c25eefea53ebb98deb4221c4c902432ef2f05c5e79b7d is stale against HEAD's design file (finding 1), so it is not approved.
Reviewed: code at b0c046b (diff 546ae12..b0c046b, growing_shapes); working tree at HEAD 874a927
Owner recheck request (verbatim): "Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps."

## Summary

The 7.5 code change is correct and contained. The only blocker is identity bookkeeping: the pin was generated before the later design-wording commits.

- **Synthetic suite**, run once with temp and cache files in the scratchpad: **84 passed in 1.95 s**. The tree stayed clean.
- **Pinned configuration:** `configuration_sha256` equals the current `CONFIG_SHA256`.
- **Synthetic checks:** `REV7_SYNTHETIC_CHECKS.json` reports PASS and binds df5b1960….

## Findings

1. **BLOCKING: the execution pin no longer matches HEAD's design file.**
   - **Evidence:**
     - `REV7_SOURCE_IDENTITY.json` (sha256 df5b1960…, unchanged since b0c046b) pins `evidence/tactical_composition_demo/DESIGN_0H_REV7.md` at its b0c046b content.
     - Commits 4cf85f4 and 874a927 then added design section 12.1 (wording only, +7 lines).
     - Running `rev7_identity.assert_inputs()` on the current tree fails with: `INVALID: scientific identity mismatch: evidence/tactical_composition_demo/DESIGN_0H_REV7.md`. It also compares the pin against `git show HEAD:` for the three design files.
     - `Execution.start` calls `assert_inputs()`, so fixture execution would refuse at start. This is not silent, but the delivery cannot run as delivered.
     - The other new pinned input, `docs/reviews/tactical_0h_rev75_design_review_codex.md`, still matches.
   - **Exact fix**, with the design final and committed:
     1. Regenerate the pin: `.venv/bin/python -m evidence.tactical_composition_demo.growing_shapes.runner.rev7_identity`. This is `create_pin()` and rewrites `runner/REV7_SOURCE_IDENTITY.json`.
     2. Rerun the synthetic receipt once: `.venv/bin/python -m evidence.tactical_composition_demo.growing_shapes.runner.rev7_verify`. `Execution.start` requires `REV7_SYNTHETIC_CHECKS.json` to bind the new `scientific_input_sha256` and the new pin digest.
     3. Commit the pin and the receipt. Make no further design edits after the pin, or repeat steps 1–2.
     4. Get a one-line Claude confirmation that binds the new pin digest (`Reviewed execution-pin SHA256: <new digest>`). The code needs no re-review unless it changes.

## Verified (no defect)

- **Scope of the diff:** only the 7.5 change, the regenerated identities and receipts, and version strings changed.
  - **Medium:** no change to native or Python medium files (`medium/` diff empty).
  - **rev7_run.py and rev7_protocol.py:** docstrings only.
  - **rev7_verify.py:** temp directory names only.
  - **rev7_execution.py:** the receipt revision is now read from `CONFIG['revision']`, which is `'7.5'`.
- **N1d:** only member 0's θ₀ changed, to π − 0.5 = 2.641592653589793. Positions, ω, g, role, site, tolerances, entry rule (not applicable) and 16 s horizon are unchanged. It remains `used_in_verdict=True`.
- **N1g:** a `deepcopy` of the old N1d, taken before the edit. It keeps θ₀ = π at (3.7, 0) and (3.956, 0), with 16 s and `used_in_verdict=False`.
  - `compare_n1` returns `verdict='DESCRIPTIVE'` for it.
  - `n1_verdict` checks that every registered case is present and follows its verdict policy (otherwise INVALID), and aggregates PASS/FAIL over N1a–f only. **N1g therefore has no verdict effect.**
  - The slip diagnostic reports the first endpoint with |unwrapped carrier-relative phase − π| ≥ 0.5, its sign, its time and bracket, and NOT_OBSERVED otherwise. It matches the 12.1 definition.
- **Unchanged:** λ = 32, h = 0.005 against 0.00125 (20/80 substeps), every N1 tolerance, F1c's gate (4 s margin still descriptive), F1d, the stop sequence and every other CONFIG entry. Only `revision`, the N1 recipes and `N1.saddle_diagnostic` changed.
