# C6 option B workspace delivery

Result: **NOT_READY**. Exact engineering equivalence passes; the worst cold world
is 952.884861 seconds versus 360. The final projection is 28,586.545831 seconds
versus 10,800. All 377 C6 contracts passed once after the final repair batch.
Independent Claude engineering review is pending. C6 remains BLOCKED / R006 STOP.

The workspace .git is read-only under this session's filesystem policy. Commits
were created in `/private/tmp/c6_option_b_delivery_20261005`, using the original
repository author identity, `core.hooksPath=.githooks` and the normal pre-commit /
commit-msg hooks. Every commit carries `Assisted-by: Codex:GPT-6`. No hook was bypassed.
No original branch/index/ref was changed by this task; concurrent sessions advanced
that repository independently. Unrelated dirty/staged/untracked work was preserved.

- Base: `b547d7f8efab06ec83bc47fff45c4dc5ddcff58f` (owner decision 0029).
- Implementation/evidence commit: `7971be06981683fc2e8051929a4e7d5b285f037a`.
- Delivery branch: `codex/c6-option-b-engineering` (implementation, then this note).
- Bundle: [commits.bundle](commits.bundle). Requires the base commit's objects.
- Post-export verification: [BUNDLE_VERIFIED.json](BUNDLE_VERIFIED.json), stored beside
  the bundle; it cannot contain its own enclosing bundle hash inside that bundle.
- Report: [OPTION_B_REPORT.md](OPTION_B_REPORT.md).
- Byte inventory: [DELIVERY_CONTENTS.json](DELIVERY_CONTENTS.json), 100 source/artifact
  payload files, plus the inventory and this delivery note.
- Preservation: [PRESERVATION_CHECKS.json](PRESERVATION_CHECKS.json), 3,572 existing
  protected source/contract/configuration/evidence files unchanged.

The final code is seven new files: `geomind/c6_option_b.py`, two kernels in
`native/c6_option_b/`, the builder/checker/comparator in `tools/`, and
`tests/test_c6_option_b.py`. All other changes are additions under `evidence/c6_option_b/`.
The original R4 sources, C0-C5 freezes, committed receipts and STATUS.json are unchanged.
No final entropy, R007, mutation, panel, C0 run, scientific acceptance or status change.
V1/V2 sources/binaries and failed comparison outputs remain archived for review.

Final proof: the current stored fixture and both complete smoke worlds match the
original exactly, including all digests/decisions/chain outcomes. The complete
development-world audit compares 996,971,880 float64 values bit-for-bit over
4,829 kernel calls, plus all labels over 59,007 component calls. Its complete
stored world is also exactly equal to the original profiled reference. The earlier
3.68e-10 numerical failure is retained; restoring original scalar arithmetic fixed
it without widening the predeclared tolerance. See the report for profile, loads,
costs, memory bounds, deviations and the separate failed-attempt accounting.

## Inspect/import

Use a clean checkout/worktree for review or integration: this original workspace
already contains supplied untracked files at the delivered paths. Do not reset,
clean, stash or overwrite unrelated work to import the bundle. From a clean checkout
that has the base commit, use normal hooks and:

```sh
git bundle verify /Users/new/RiderProjects/ai_RPG_test/evidence/c6_option_b/commits.bundle
git fetch /Users/new/RiderProjects/ai_RPG_test/evidence/c6_option_b/commits.bundle refs/heads/codex/c6-option-b-engineering:refs/heads/c6-option-b-review
git cherry-pick b547d7f8efab06ec83bc47fff45c4dc5ddcff58f..c6-option-b-review
```

Do not rerun unchanged long worlds or suites routinely. The final archived macOS
arm64 binary/build pairs are `option_b.dylib` / `OPTION_B_BUILD.json` and
`reference_field.dylib` / `REFERENCE_BUILD.json`. On a fresh checkout, restore each
matching pair to its ignored build directory before loading, or explicitly build
and record a new binary identity; never silently reuse a mismatched build. The
checker selects `--backend reference|native`; entropy choices are smoke/development,
world choices 0/1, with fresh output directories required. `--audit` on the native
backend additionally checks every full array against the original kernel. One
selection context per isolated process; grids remain sequential.

## Independent Claude engineering handoff

Review the delivered commit(s) once, about 15-20 minutes, within decision 0029.
Check the unchanged scalar evaluator and flags (UNCHANGED_ARITHMETIC.json), complete
cache keys and OFF eligibility, live actual-medium recomputation, full material /
carrier replay at requested production times, byte bounds, exact graph semantics,
backend restoration/identity guards, final exact comparisons and real runtime rule.
Account for the failed vector candidate rather than accepting its local-array pass
as a whole-world pass. Confirm that numerical limits, every qualification/detection
and chain decision, entropy use and all R4 science stay unchanged. State the reviewed
source/evidence identities, findings and engineering verdict. Assign no numeric
quality score or scientific qualification; run no final entropy, new registration,
mutation or panel, and change no frozen file, receipt or milestone status.
