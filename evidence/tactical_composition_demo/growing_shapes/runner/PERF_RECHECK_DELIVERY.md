REVIEW_READY — local engineering; independent Claude review pending

Implementation commit: `73fd9f2c8e119de4cbfdf0d51f8219b9b72705bf`.
Bundle prerequisite/base: `54c21c7a0bbbb0fc3259d9f346e3548d3475a7fb`.
Bundle branch: `codex/0h-perf-recheck`.

The workspace `.git` is read-only under the supplied permission profile. The
implementation was committed in a temporary checkout with the repository's
normal `.githooks` enabled. Its freeze, legacy, milestone, status and provenance
guards passed without bypass. This delivery-note commit uses the same hooks.
Both commits carry `Assisted-by: Codex:GPT-6`. No workspace commit, merge, push,
status promotion or experimental execution authorization is implied.

The transport file is `perf_recheck_commits.bundle` beside this note. It contains
the implementation and this note, and excludes itself and the final external
verification receipt `PERF_RECHECK_DELIVERY_CHECKS.json` to avoid circular hashes.
That receipt records both commit identities, bundle integrity, a separate fetch
verification, and byte-for-byte hashes of every delivered file against the
working tree. All changed paths are under
`evidence/tactical_composition_demo/growing_shapes/`. Unrelated active work,
accepted experiment files, existing receipts and older bundles were not staged.

Read `PERF_RECHECK_REPORT.md` for findings, fixes, timing limits and remaining
risks; `PERF_RECHECK_COMPARISON.md` contains the predeclared equivalence contract.
`PERF_RECHECK_PROJECTION.json` contains algebra from measured dev-only rates.
The saved raw trajectories, stricter comparison, long synthetic checks and test
logs accompany the source. No section-10 run, 200-episode projection execution,
judging seed, recorded run or real evaluator panel was performed. READY means
local engineering readiness; the new cross-family review remains outstanding.

To import into an owner-writable checkout containing the base commit, fetch the
bundle branch and cherry-pick its two commits in order. Inspect current changes
and resolve any conflicts while preserving unrelated work; do not reset or clean
the working tree. For example, from that checkout:

```sh
git bundle verify /absolute/path/to/perf_recheck_commits.bundle
git fetch /absolute/path/to/perf_recheck_commits.bundle refs/heads/codex/0h-perf-recheck
git log --reverse --format='%H %s' 54c21c7a0bbbb0fc3259d9f346e3548d3475a7fb..FETCH_HEAD
git cherry-pick 73fd9f2c8e119de4cbfdf0d51f8219b9b72705bf
# Then cherry-pick the delivery-note commit printed by git log above.
```

Native build products are ignored and intentionally absent from the bundle.
After import, rebuild explicitly, then use a fresh Python process:

```sh
.venv/bin/python -m evidence.tactical_composition_demo.growing_shapes.runner.build_perf
```

The loader refuses stale source/dependency identities and changed resident
images. Rebuild and recheck equivalence on a different platform; the measured
results certify only this pinned local build. No long run is needed for import.
Any later owner-authorized section-10 invocation must explicitly select the
native backend and supply a fresh audit_root; the compatibility default remains
reference. Audit files must travel with reports that refer to them.
