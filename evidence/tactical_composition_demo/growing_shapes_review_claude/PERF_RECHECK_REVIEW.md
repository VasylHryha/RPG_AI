APPROVE_WITH_NOTES

Reviewer family: Claude (claude-opus-5-5)
Reviewed: Codex's 0h C++ performance recheck (the owner's 10/10 recheck request), merged at `6bdc82e`; `growing_shapes/runner/PERF_RECHECK_REPORT.md` (READY)
Date: 2026-10-05

## Checked

- **I ran `test_perf_recheck.py` once:** 40 passed in 218.6 s.
- **The findings are real and fixed:**
  - a newborn could wrongly invalidate a qualification window (high);
  - the loader did not pin the linked libraries (high);
  - thread safety around ctypes releasing the GIL (high);
  - unbounded log and memory growth over long runs (high);
  - recovery and evaluator episodes moved native (medium);
  - exact comparison of opaque clocks and ids (medium);
  - the earlier cost figure understated the full run (medium; it was my 5-hour figure, which counted training only).
- **Speed:**
  - recovery is 4.6-13.5× faster;
  - evaluator episodes are 1.6-8.4× faster;
  - native training is 2-5 ms per world step depending on the task.

## Note: the section-10 cost

The measured rates give about 21-55 hours of serial compute. **Evaluation at the cap dominates** (7-21 h), then training (9-34 h depending on medium size). That is above the design's 24-hour reporting line, so the decision goes to the owner before section 10 starts: run as designed in parallel, a lighter evaluation recorded as design 5.2, or wait.
