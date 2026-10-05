# C6 option B recheck delivery

Result: NOT_READY pending queued whole-world comparisons, official quiet-machine timing and new Claude engineering review. Final affected tests: 78 passed in 7.46 seconds. Sequential/forward/reverse fixture audits and stored comparisons pass bit for bit. No full C6 world ran during the shared timed 0g task. See [RECHECK_REPORT.md](RECHECK_REPORT.md).

Workspace .git is read-only under this session's filesystem policy. Scoped commits were created in `/private/tmp/c6_option_b_recheck_delivery_e4meng9u/checkout` using normal `.githooks` pre-commit and commit-msg hooks, without bypass. Every commit carries `Assisted-by: Codex:GPT-6`. Original branch, index, refs, unrelated work, original R4 sources, committed receipts and STATUS.json were not written.

- Base: `ad33de908921cd2bed3811139ea86a024b051770`.
- Implementation/evidence commit: `09bbf734015339acfbcfad675231f586799b9d94`.
- Delivery branch: `codex/c6-option-b-recheck` (implementation plus delivery note/log).
- Bundle: [recheck_commits.bundle](recheck_commits.bundle), requiring the base objects.
- External post-export/import verification: [RECHECK_BUNDLE_VERIFIED.json](RECHECK_BUNDLE_VERIFIED.json).
- Payload inventory: [recheck/CONTENTS.json](recheck/CONTENTS.json), 70 payload files plus the inventory; this note and implementation commit log are separate.
- Deferred argv/reference inventory: [recheck/QUEUED_CHECKS.json](recheck/QUEUED_CHECKS.json), 13 equivalence world computations plus four quiet normal timing computations, all unexecuted.
- Preservation: [recheck/PRESERVATION_CHECKS.json](recheck/PRESERVATION_CHECKS.json), 6,786 tracked baseline hashes; no unrelated/protected delta during this task.

The bundle is verified in a separate clean checkout, including imported file bytes, provenance trailers and normal hooks. Verification metadata/logs are outside the bundle to avoid self-referential hashes. The original workspace already contains the task edits; integrate from a clean checkout that contains the base. Preserve unrelated changes and supplied untracked artifacts; do not reset, clean, stash or overwrite them.

```sh
git bundle verify /Users/new/RiderProjects/ai_RPG_test/evidence/c6_option_b/recheck_commits.bundle
git fetch /Users/new/RiderProjects/ai_RPG_test/evidence/c6_option_b/recheck_commits.bundle refs/heads/codex/c6-option-b-recheck:refs/heads/c6-option-b-recheck-review
git config core.hooksPath .githooks
git cherry-pick ad33de908921cd2bed3811139ea86a024b051770..c6-option-b-recheck-review
```

In a fresh checkout, restore the final matched pairs from `evidence/c6_option_b/recheck/` before loading:

```sh
mkdir -p build/c6_option_b build/c6_r4
cp evidence/c6_option_b/recheck/option_b.dylib build/c6_option_b/option_b.dylib
cp evidence/c6_option_b/recheck/OPTION_B_BUILD.json build/c6_option_b/BUILD.json
cp evidence/c6_option_b/recheck/reference_field.dylib build/c6_r4/field.dylib
cp evidence/c6_option_b/recheck/REFERENCE_BUILD.json build/c6_r4/BUILD.json
```

These binaries are identified macOS arm64 artifacts. Explicit rebuilding creates a separately identified build and requires fresh evidence in a fresh process; never rebuild a loaded library or silently select mismatched artifacts. Older batch-1 binaries are archival only. Both kernel arithmetic and compiler flags remain unchanged. New Python/native statistics use an eight-field output including drive bytes: deploy the bound pair together.

Do not rerun unchanged suites or launch the deferred worlds while timed work is active. The queued commands use only existing smoke/development inputs, at most two world processes and four pool workers each, with numerical helper teams one. A passing bounded timing result is not owner approval, scientific qualification, R007 authorization, registered panel permission or milestone acceptance. The historical Claude review covers the earlier code; request one review of this new engineering revision after the queued evidence is collected.
