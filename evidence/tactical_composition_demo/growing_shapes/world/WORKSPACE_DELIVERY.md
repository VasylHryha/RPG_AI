REVIEW_READY — note 3 implementation; Claude integration pending

Implementation commit: `29099acbf0fbcb5d4bb1d38a3530b47528c1ccb1`. Branch: `codex/remember-static`.
Base: `d0264cb5e516590d13536d88130e17fac72722d0`.
Original engine baseline: `aeb75a73c1d00706ff8e264563ae0f9a554c5f1c`.
Isolated checkout: `/private/tmp/gs_remember_static_20261005`.
Both implementation and delivery-note commits carry `Assisted-by: Codex:GPT-6`
and pass the repository pre-commit and commit-message hooks.

The workspace permission profile allows reading its `.git`, but not writing it.
The user explicitly authorized verified-bundle delivery in that case. Workspace
Git metadata is untouched. Only files under `growing_shapes/world/` were changed;
unrelated staged, dirty and untracked work was not copied, staged or modified.
The workspace HEAD advanced concurrently to `2616fdcba7c0cdcff08be9c22b041f5423e0e5fe` while this task ran;
its changes do not touch world/. Integrate onto the current history rather than
replacing it. The scoped workspace copies already match the delivered commits.

Implemented only WORLD_REVIEW.md note 3 under decision 0028 item 17:
`remember_static` is task id 7, with one zero-velocity enemy, 40 visible then
120 hidden decisions, the last-visible-position reference and remember's random
policy rule. The original tasks keep ids, generator streams and outputs.

Evidence:

- `REMEMBER_STATIC_CHECKS.json`: current source/build identities, static-task
  dev/validation 0..255 scores, original full-precision comparison scores,
  28 matching stream hashes (7 tasks x 2 namespaces x 2 policies).
- `ORIGINAL_COMPARISON_TABLE.md`: all 30 original table rows, byte-identical.
- Side-by-side original/current builds: every observation (including terminal),
  action field, seed tag and final score matches over 7,168 original episodes.
  Action fields are packed without non-semantic C struct tail padding.
- Original `WORLD_CHECKS.json`, `WORLD_TEST_LOG.txt` and report prefix retain
  their exact original bytes. WORLD_REPORT.md has an appended note-3 section.
- `test_world.py` ran exactly once after all code/test edits: 79 passed in 0.47 s.
  Existing cases remain. Minimal existing-test adaptations move the invalid task
  sentinel from 7 to 8, read current identities from the additive receipt and
  extend shared memory contracts to the new task; test source itself changed.
- Reference angular error: 0 on both namespaces. Random: dev
  1.5783683214759057 radians, validation 1.5723513238614601 radians.
- Total verification: 23.172 s. No speed benchmark was repeated. No growth,
  learning, judging, mutation probe, panel or milestone/status change occurred.

`commits.bundle` contains implementation and this delivery note relative to the
base above. Delivery checks use `git bundle verify`, fetch into a second temporary
repository with the base objects, inspect commit scope/trailers, and compare every
delivered file against the branch and workspace. The bundle is an untracked
transport artifact, created after committing the files, so it is not inside itself.

Import:

```sh
git fetch evidence/tactical_composition_demo/growing_shapes/world/commits.bundle refs/heads/codex/remember-static:refs/heads/codex/remember-static
```

Claude reviews and integrates the two scoped commits after reconciling the matching
local world/ copies; preserve unrelated changes and the newer workspace history.
Remaining gate: Claude confirmation of this note-3 addition. No self-acceptance.
The current bounded verifier is `verify_remember_static.py`; `verify_world.py`'s
CLI delegates to it so historical artifacts remain intact. Successful evidence
need not be rerun for the unchanged implementation.
