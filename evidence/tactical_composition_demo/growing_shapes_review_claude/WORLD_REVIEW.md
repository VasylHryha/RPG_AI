APPROVE_WITH_NOTES

Reviewer family: Claude (claude-opus-5-5)
Reviewed: `growing_shapes/world/` at commit `aeb75a7` ("Build tiny 2D growing-shapes task world and C ABI"), report `growing_shapes/world/WORLD_REPORT.md` (READY)
Date: 2026-10-05

## Checked

- **The report:** task definitions, generators, observation masking, action validation, namespaces, speed, and the reference and random scores.
- **I ran `test_world.py` once:** 67 passed in 0.33 s.
- **Independently:**
  - the judging namespace is refused without `allow_judging` (WorldError);
  - the same seed gives identical observations and scores, and a different seed differs;
  - on `remember`, the hidden decisions leak no position (dx, dy and distance are zero while invisible; 120 hidden steps).
- **The reference beats random on every task by wide margins.** For example: choose 1.00 against 0.20; remember angular error about 0 against 1.57; pursuit in-range 0.96 against 0.

## Notes (none block the engine; items 1-3 change DESIGN_0H before development)

1. **Slot counts:** perceive and choose have K in {3, …, 8}, so the medium needs 8 sensor slots, not the 4 written in `DESIGN_0H.md` section 3 (a drafter error).
2. **One primary score per task** must be named in the design for atom competence:
   - perceive: angular error (distance error is descriptive);
   - move: goal error (settle time is descriptive);
   - remember: angular error on hidden decisions;
   - choose: correct-choice rate.
3. **The memory task is not attainable for a held-phase memory as it stands.** With visible velocities, the reference extrapolates motion exactly (error about 0), so the normalized competence threshold (n ≥ 0.5) would demand motion prediction, not holding a direction. A **static-target variant** of `remember` (enemy speed 0) is needed for the atom bootstrap: a small, additive engine change, with the moving variant kept for combined tasks.
4. **Combined-task choices** (no kite-with-damage task, occlusion that blocks vision only, non-lethal stationary focus targets) are acceptable for the deferred combination stage. They are revisited when that design is written.
5. **Batch means truncate `hidden_steps` to an integer;** it is diagnostic only. Not a defect.
