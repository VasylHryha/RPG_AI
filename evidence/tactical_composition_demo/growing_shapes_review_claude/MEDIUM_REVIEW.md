APPROVE_WITH_NOTES

Reviewer family: Claude (claude-opus-5-5)
Reviewed: `growing_shapes/medium/` at commit `7476d36` ("Build exploratory 0h fast C4 medium"), report `growing_shapes/medium/MEDIUM_REPORT.md` (READY)
Date: 2026-10-05

## Checked

- **I ran `test_medium.py` once:** 70 passed in 0.42 s.
- **The report says:**
  - all 5 stored C4 cases × 3 variants match (neighbours, rhs, one RK4 step) to 1e-9;
  - the grid neighbours equal brute force;
  - the C4 law is reproduced with geometry_rate = 1.
- **The formulas in the report** (C4 law, Gaussian drive with strict reach, readout, PLV over shared samples, lock, strain, lock groups, growth rules, protection, snapshots, clone isolation) are clear, and they keep scientific constants out of the engine (no growth defaults).
- **The API** has add, set_element (positions, phase and rate, so the runner can apply rate adaptation), remove, split, silence, set_drives, step, observe, readout, plv, measure, groups, cost, configure_growth, apply_growth_rules, clone, save and load, and events.

## Gaps against DESIGN_0H revision 3 (written after this engine was started; to be closed in one update batch **after** the revision-3 design review passes, so the engine changes once)

1. **Per-element input gain:** design section 3 multiplies the drive by g_i, but the engine's drive term has no per-element gain. Add a per-element gain field (default 1), settable.
2. **B1 coverage** (section 5):
   - the offset condition |circular mean of wrap(θ_i − ψ_s)| ≤ δ_off;
   - site activity eligibility (active in ≥ 80% of the window), with PLV and offset over the active samples only;
   - the site timer reset after a birth.
3. **Lock partner eligibility:** a partner counts only if active in ≥ 80% of the window. L(i) is undefined before a full window, and undefined counts as 0 for D3 ordering.
4. **Cost:** design section 5 counts **undirected** neighbour pairs (the union of directed lists) and no drive links. Make the counting rule a configuration option, with the design's rule as the 0h setting.
5. **Placement:** the fixed spiral (j = 0 … 49, 0.1 m.u. steps, golden angle), with a minimum separation of 0.05 m.u., rejected and logged when exhausted. Newborn g = 1.
6. **Runner-side components, not engine changes:**
   - rate and gain adaptation;
   - the driven qualification adapter with open-loop replay futures;
   - templates and isolated copies;
   - the task-to-action bindings.

## Answers to the report's questions (section "Choices and questions")

1. Strain and B2: **deferred** in revision 3. Keep the implementation, unused.
2. Kernel and reach: Gaussian with σ = 1 and reach 3σ, strict; the drive is additive and unnormalized, then multiplied by g_i (gap 1). Confirmed.
3. Window: a sample count of 100 at the world step (0.1 s). There are no decisions from insufficient history. Confirmed.
4. geometry_rate = 1 (the accepted law). Separation is **measured**, not imposed (design section 2).
5. Cost: undirected pairs, no drive links (gap 4). Readouts are excluded. Confirmed.
6. Rule order: D1, then D3, then B1 (design section 5). B2, D2 and B3 are not used in revision 3.
7. Reward hooks: the reward arm in revision 3 uses only the episodic gain update (runner side); D2 and B3 are not used.
8. Agreed: lock groups are not qualification. The driven qualification adapter is a runner component (gap 6).
