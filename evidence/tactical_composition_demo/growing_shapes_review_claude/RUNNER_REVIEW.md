APPROVE_WITH_NOTES

Reviewer family: Claude (claude-opus-5-5)
Reviewed: the 0h medium follow-up and runner, merged at `1c1535e` from Codex's bundle (`5496b7e` implementation, `ff59a0d` delivery), report `growing_shapes/runner/RUNNER_REPORT.md` (READY), against `DESIGN_0H.md` revision 5.1 (`af3e7dd`, Codex review r5 APPROVE_WITH_NOTES)
Date: 2026-10-05

## Checked

- **I ran the runner and medium tests once:** 175 passed in 11.85 s. C4 reference parity (1e-9) is retained.
- **The frozen C4 detector** (`geomind/c4_detect.py`) is imported unchanged, and its hash is pinned in `qualification.py` (sha256 `ba7fd94e…`, equal to the frozen file).
- **Contract tests exist for the risky rules:**
  - the revision-2 aliasing counter-example is a negative contract;
  - the alias flag blocks recovery and admission;
  - the control queue (FIFO, two attempts, redraw, terminal drop; own entropy; two per check);
  - template hash order, binding identity and isolation;
  - copies at carrier offsets 0 and π, including zero-resultant groups;
  - 128 fresh evaluator copies per panel;
  - a changed binding rule is rejected.
- **The report states the design's limits honestly:** driven snapshots do not establish autonomy or closure; G5 is a copy-covariance check; H-BG, H-PS and H-RBG are NOT_TESTED. No section-10 entry point is exposed.
- **One engineering smoke** (dev seed 105051, 8 episodes) completed, with 5 births and one 601-frame qualification check (no qualifying candidate). It is not development evidence.

## Notes

1. **Throughput: the main gap before section 10.**
   - The smoke's training stage took 35.18 s for 8 episodes (1,280 world steps), about **27 ms per world step**.
   - The medium itself runs about 6,900 steps per second at N = 50, so the 5 substeps cost under 1 ms. **About 97% of the time is the Python per-step orchestration**: drives, sampling, adaptation, timers.
   - At this rate, the 32 development runs (2 arms × 8 seeds, plus 16 G0 controls) × 2,000 episodes × 4.4 s come to about **78 hours** of compute, before qualification, recovery and evaluation. That is above the design's 24-hour reporting line.
   - **Recommendation:** an engineering performance pass that moves the per-world-step loop (drive setup from the bound observation, append-first sampling, rate and gain adaptation, timers) into the native library, with the Python path kept as the reference and a byte-identical (or declared-tolerance) equivalence check on the smoke seed. This is within decision 0028 item 17 (engine parts) and changes no protocol constant.
2. **Coverage of tasks in the smoke:** only perceive ran (the first rotation block). The other bindings are covered by synthetic contracts. The 200-episode projection run (section 10) exercises the rotation.
3. **The first test attempt failed** on an exact PLV assertion (1 against 0.9999999999999998) and was fixed by numeric tolerance in the test. Its receipts are retained, which is correct.
