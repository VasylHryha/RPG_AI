# C6 option B parallel delivery

Engineering exact-equivalence checks pass. Official runtime readiness remains pending
Claude's quiet-machine measurement. PARALLEL_REPORT.md starts NOT_READY; no milestone
status or scientific verdict changed.

The workspace .git is read-only under this session's filesystem policy. Scoped
commits were created in `/private/tmp/c6_option_b_parallel_delivery_20261005` with
`core.hooksPath=.githooks`, normal pre-commit/commit-msg hooks and the repository's
author identity. Every commit carries `Assisted-by: Codex:GPT-6`. No hook was bypassed.
The original branch, index and refs were not written by this task. Unrelated work
is excluded, including the independently changed growing-shapes PERF_REPORT.md.

- Base: `54c21c7a0bbbb0fc3259d9f346e3548d3475a7fb`.
- Implementation/evidence commit: `57b34ee0942f348fe140dc7139cf2a7b120ef9fa`.
- Delivery branch: `codex/c6-option-b-parallel` (implementation, then this note/log).
- Bundle: [parallel_commits.bundle](parallel_commits.bundle), requiring the base objects.
- Post-export/import verification: [PARALLEL_BUNDLE_VERIFIED.json](PARALLEL_BUNDLE_VERIFIED.json).
- Report: [PARALLEL_REPORT.md](PARALLEL_REPORT.md).
- Inventory: [PARALLEL_CONTENTS.json](PARALLEL_CONTENTS.json), 75 payload files plus
  the inventory itself; this delivery note and implementation commit log are separate.
- Checks: [parallel/ENGINEERING_CHECKS.json](parallel/ENGINEERING_CHECKS.json).
- Preservation: [parallel/PRESERVATION_CHECKS.json](parallel/PRESERVATION_CHECKS.json),
  6,670 baseline tracked files compared; no protected change.

New implementation/test files are geomind/c6_option_b_parallel.py and
tests/test_c6_option_b_parallel.py. Existing edits are confined to the preceding
option-B backend, checker, comparator and test. Native kernels, C0-C5 frozen files,
original R4 sources, committed receipts and STATUS.json are unchanged. No final
entropy, R007, mutation probe, panel or acceptance action ran.

Declared k=5: one coordinator plus four compute workers per world; two world
processes × five threads = ten. Grids, control/kick recovery futures and all causal
forks use the same bounded pool with fixed merge order. Both submission schedules
match the stored fixture, smoke worlds 0/1 and development world 0 exactly against
the sequential option-B outputs and original reference. The full development audit
matches 1,017,108,092 float64 values bit-for-bit, plus 59,007 detector calls. All
382 distinct affected contracts have valid successful evidence; two test-setup
failures and their bounded retries are retained separately in the report.

Observed one-minute load was 34.44-86.66 on ten logical CPUs. Timing and the rough
quiet-machine estimate are information only. Normal-path CPU/wall, audit cost,
serialization, RSS, cache counters and start/end load are separately recorded.
No readiness rule is evaluated from these noisy times or the estimate.

## Inspect/import

Use a clean checkout/worktree containing the base commit; the original workspace
already contains these source changes and supplied untracked evidence. Preserve
unrelated edits and do not reset, clean, stash or overwrite them to import.
Enable the normal hooks in that clean checkout, then:

```sh
git bundle verify /Users/new/RiderProjects/ai_RPG_test/evidence/c6_option_b/parallel_commits.bundle
git fetch /Users/new/RiderProjects/ai_RPG_test/evidence/c6_option_b/parallel_commits.bundle refs/heads/codex/c6-option-b-parallel:refs/heads/c6-option-b-parallel-review
git cherry-pick 54c21c7a0bbbb0fc3259d9f346e3548d3475a7fb..c6-option-b-parallel-review
```

Bundle verification additionally imports into an isolated temporary repository and
checks every delivered file byte-for-byte. The post-export verification JSON and
the delivery-commit log are external to the bundle, to avoid self-referential hashes.

## Quiet-machine handoff

Claude schedules the official measurement with no other heavy jobs, the supplied
source/build identities and exactly two cold world processes. Use the existing
engineering checker with `--backend native --parallel --entropy smoke --world 0|1
--output <fresh-directory>`; omit --audit for normal runtime cost. The sequential
option-B path remains `--backend native` without --parallel; original reference
remains `--backend reference`. The CLI caps numerical-library helper threads.
The unchanged inherited build/library pairs must be restored together to their
ignored build directories in a new checkout, or explicitly rebuilt and separately
identified; no silent mismatch/rebuild is permitted. The extension requires its
own independent engineering review. Scientific registration, execution and status
changes remain outside this delivery.
