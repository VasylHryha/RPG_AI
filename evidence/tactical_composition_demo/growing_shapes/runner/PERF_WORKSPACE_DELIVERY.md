REVIEW_READY — engineering checks pass; independent Claude review pending.

Implementation commit: `9c473ff`.
Base: `68c10ac0ae809a1fed2c50d0556b73f7932d31d3`.
Branch: `codex/0h-native-perf`.
Isolated checkout: `/private/tmp/gs_0h_native_perf_20261005`.
Both scoped commits carry `Assisted-by: Codex:GPT-6` and pass the repository's
normal pre-commit and commit-message hooks (`core.hooksPath=.githooks`), without
bypasses. Workspace `.git` is read-only under this session's permissions;
the authorized delivery therefore uses an isolated local clone and bundle.
No workspace Git metadata, remote, status or frozen source was changed.

Only `evidence/tactical_composition_demo/growing_shapes/` is changed. Existing
transport bundles, source archives, original smoke/receipt/test evidence,
C6 option-B work, and unrelated replay data remain untouched. The only old
source changes are `runner/run.py` and the timer audit return in
`medium/design_0h.py`; new orchestration/build/comparison/tests and evidence
live under `runner/`. Build products remain ignored and are explicitly rebuilt.

`PERF_REPORT.md` starts READY: 20.551338 → 1.713530 ms/world step, **11.993567×**,
on the paired eight-episode dev smoke seed 105051. Full event/decision/timer
equivalence passed. Final and qualification check-time native snapshots are
byte-identical; maximum permitted numeric discrepancy is 1.11e-16 under the
predeclared fixed 1e-10 absolute/relative bound. Final tests: 360 passed in
90.62 s; failed attempts are retained separately. No successful verification
was repeated, no judging seeds were used, and no section-10 development run,
projection, evaluator panel, acceptance or scientific verdict was performed.

`perf_commits.bundle` contains implementation and delivery-note commits relative
to the base above. It is a transport artifact outside itself, preserving the
older `commits.bundle`. `PERF_DELIVERY_CHECKS.json`, also outside the bundle,
records the final head, bundle hash, hook checks, every scoped file hash and
successful transport verification. Verification uses `git bundle verify`,
fetch into a second temporary local clone with the prerequisite base objects,
and byte comparison of every changed file between the fetched Git tree,
implementation checkout and workspace. This is artifact verification, not
another numerical run. Original pytest trace whitespace is retained as raw
evidence; source changes pass whitespace checks.

Import into an owner-writable checkout, preserving newer/unrelated work:

```sh
git fetch evidence/tactical_composition_demo/growing_shapes/runner/perf_commits.bundle refs/heads/codex/0h-native-perf:refs/heads/codex/0h-native-perf
```

Claude reviews the performance pass against unchanged DESIGN_0H revision 5.1,
then integration can reconcile the matching workspace files with the two
commits. Native selection is explicit (`Run(..., backend='native')`); reference
remains the compatibility default. Section-10 execution and its projection
still need their own owner go-ahead. No push or integration was performed by
this delivery.
