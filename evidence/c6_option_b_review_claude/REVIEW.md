APPROVE_WITH_NOTES (engineering; equivalence exact; the runtime rule still fails, so C6 stays BLOCKED)

Reviewer family: Claude (claude-opus-5-5)
Reviewed: the C6 option B port, merged from Codex's bundle (`7971be0` port, `474f77b` delivery), report `evidence/c6_option_b/OPTION_B_REPORT.md` (NOT_READY), under decision 0029
Date: 2026-10-05

## Findings

1. **The profile changes the premise of option B.**
   - Before porting, the complete development world spent **70% of its wall time in the already-native element-law RHS** (all-pairs smooth law), plus the work it is called for: qualification (358 s inclusive), recovery futures (213 s) and causal forks (144 s).
   - The Python orchestration itself is a few seconds. A Python-to-C++ port therefore cannot give the 2-3× hoped for; the ceiling is set by the native compute and the number of forks (Amdahl).
2. **The gain that was possible was taken exactly.**
   - A typed exact trajectory cache avoids repeated material-law integrations: 9,215,000 RK steps on smoke world 0 and 2,401,000 on world 1. Every returned array matches the original bit for bit, and every decision matches: zero-tolerance whole-world comparisons on both smoke worlds and the development world.
   - The vectorized-math variant (V2) failed the predeclared 1e-10 tolerance by 3.6e-10 and was correctly abandoned, not tolerated.
3. **Runtime still fails:** the worst cold world took 952.9 s (661.6 s of CPU) against 360 s, a projection of 28,587 s against 10,800 s.
   - The load was 5-55 on 10 cores, from concurrent jobs of this line. That explains part of the wall time, but **the CPU time alone exceeds 360 s**, so the failure is real.
   - The report rightly refuses to normalize it.
4. **The process was sound:**
   - new files only; the original path selectable;
   - the source pin was verified before each world;
   - no final entropy;
   - failed attempts (the V2 equivalence failure, a comparator misclassification) retained with their corrections.

## The recommended next engineering step (exact, no arithmetic change)

- **Parallelize inside a world:** the three grids of a world run sequentially, and recovery futures and causal forks are independent of each other. Running them concurrently changes no arithmetic, so exact equivalence remains checkable. It could cut world wall time roughly in proportion to the cores used. The worker budget must be declared (2 world workers × k threads ≤ 10 cores).
- **Measure on a quiet machine**, with no concurrent heavy jobs, recording the load, because the readiness rule is wall-clock.
- If the CPU time per world (662 s) remains above 360 s with full parallelism, the remaining option is a **registered resource-rule change** (a larger budget, or fewer worlds). That is an owner decision under AGENTS.md, not an engineering one.

## Addendum: the parallel-inside-world step (merged from Codex `57b34ee` / `5782c58`; `evidence/c6_option_b/PARALLEL_REPORT.md`, NOT_READY pending measurement)

- **Thread budget:** 2 world workers × 5 threads = 10 logical CPUs.
- **Exact equivalence in both schedules** (forward and reverse): zero maximum error and zero changed digests on the stored fixture, both smoke worlds and the development world. 378 existing checks and 4 new tests pass.
- **Under load 34-87, world wall times were 267-643 s.** The report's quiet-machine planning estimate for the worst world is about 304 s (band 190-434 s), uncalibrated and correctly labelled as an estimate.
- **Next:** the official quiet-machine measurement, scheduled after the 0g v3 and 0h development runs. If it exceeds 360 s, the remaining option is the owner's resource-rule decision.

## Addendum 2: the owner-requested recheck (merged at `6960782`; `evidence/c6_option_b/RECHECK_REPORT.md`, NOT_READY pending the queued checks)

- **Four high findings fixed:**
  - F1: the drive cache was not fully cleared, and its key merged ±0;
  - F2: oversized entries were allocated before being rejected;
  - F3: allocation exceptions crossed the C boundary, with integer overflow risks;
  - F4: implicit rebuilds, and unbound compiler flags.
- **Five medium findings fixed or corrected** (F5-F9), including overclaims in the earlier reports (an exhausted speed ceiling, full coldness, the only remaining option). Those claims are withdrawn.
- **I ran `tests/test_c6_option_b.py`:** 72 passed. The fixture is bit-exact in the sequential and both parallel schedules.
- **The full-world zero-tolerance reruns and the official quiet-machine timing are queued** exactly as the report lists them. They run automatically after the 0h development run, when no other heavy job runs.
