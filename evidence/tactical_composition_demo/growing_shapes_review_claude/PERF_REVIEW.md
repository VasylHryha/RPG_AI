APPROVE

Reviewer family: Claude (claude-opus-5-5)
Reviewed: the 0h native performance pass, merged at `bc00869` (Codex `9c473ff`, delivery `86268e7`); `growing_shapes/runner/PERF_REPORT.md`, `PERF_COMPARISON.md`
Date: 2026-10-05

## Result

- 20.55 → 1.71 ms per world step on the smoke (dev seed 105051, 8 episodes), a 12.0× training speed-up.
- I ran `test_perf.py`: 106 passed.

## Checked

- **The equivalence rule was declared before measuring:**
  - byte-identical where the integrator and its order are reused (RK4 continuation, snapshots, frames, bindings);
  - |a − b| ≤ 1e-10 + 1e-10·|b| only for adapted floating-point state, where NumPy and libm rounding orders differ;
  - **any differing event, eligibility, admission, rejection, drop or decision is a failure.**

  The final and check-time snapshots were byte-identical.
- **Batches stop at episode and 200-step growth boundaries**, and the growth, qualification and admission order is preserved. The Python path stays selectable as the reference.
- No protocol constant changed (`DESIGN_0H.md` 5.1 hash pinned).

## For section 10

At about 1.7 ms per world step, one 2,000-episode run is about 9 minutes of training. The 32 runs (two arms × 8 seeds, plus 16 G0 controls) are about 5 hours on one core, and parallel across seeds. Qualification, recovery and evaluation come on top; the 200-episode projection measures them.
