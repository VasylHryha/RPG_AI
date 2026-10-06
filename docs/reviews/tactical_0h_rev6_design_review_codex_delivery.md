DELIVERED — CHANGES_REQUIRED design review; verified document bundle; no commit created

Review: [tactical_0h_rev6_design_review_codex.md](tactical_0h_rev6_design_review_codex.md).

Reviewed draft SHA256: `f108fd9b981951f30b6a82d6c675baaf65928b56f587f889b4212f0e08eb78b1`.
Workspace base: `bf11b14695ecc52b979e71129a75974b589410a4` (rewritten history).

The managed filesystem profile permits reading the workspace `.git` but not writing it. The owner also explicitly prohibited project-code execution in this design-review session. No Git commit or hook was run, and no hook was bypassed. The fallback is a **document archive, not a Git bundle**: it includes the review, this delivery note, a two-file patch, and the proposed commit message with `Assisted-by: Codex:GPT-6`. An owner-writable checkout can commit the documents with its normal repository hooks.

Local delivery artifacts, under the project's ignored `build/` directory:

- [Verified document archive](../../evidence/tactical_composition_demo/build/rev6_design_review_codex/tactical_0h_rev6_design_review_codex.documents.tar.gz)
- [Verification record](../../evidence/tactical_composition_demo/build/rev6_design_review_codex/BUNDLE_VERIFIED.json)
- [Two-file patch](../../evidence/tactical_composition_demo/build/rev6_design_review_codex/review.patch)
- [Proposed commit message](../../evidence/tactical_composition_demo/build/rev6_design_review_codex/COMMIT_MESSAGE.txt)

Verification checks the draft's exact identity, review header, unchanged required source hashes, archive allowlist, every archived byte/hash, an independent archive extraction, an independent patch application, patch/workspace byte equality, a sub-1-MB archive and members, and unchanged workspace HEAD/index/refs. The verification record is outside the archive to avoid a circular checksum. Only these two new Markdown files are repository changes from this task. There are no source changes, receipt changes, raw ledgers, native artifacts or unrelated C6 files in the archive. The existing untracked `evidence/c6_option_b/quiet_session/` is preserved.

To commit the already present documents in this workspace when its `.git` is writable:

```sh
git add -- docs/reviews/tactical_0h_rev6_design_review_codex.md docs/reviews/tactical_0h_rev6_design_review_codex_delivery.md
git commit -F evidence/tactical_composition_demo/build/rev6_design_review_codex/COMMIT_MESSAGE.txt
```

For a different checkout, extract the archive into a separate empty delivery directory, inspect `review.patch`, and run the following from the destination repository. Replace `/absolute/delivery/` with that directory; preserve any existing versions of these files and unrelated changes.

```sh
git apply --check /absolute/delivery/review.patch
git apply /absolute/delivery/review.patch
git add -- docs/reviews/tactical_0h_rev6_design_review_codex.md docs/reviews/tactical_0h_rev6_design_review_codex_delivery.md
git commit -F /absolute/delivery/COMMIT_MESSAGE.txt
```

These are delivery instructions, not executed project checks. If a normal hook reports a block, resolve it without bypass. No push, merge, experimental execution, new seeds, recorded-panel reinterpretation, milestone promotion or scientific acceptance is part of this delivery. Claude owns the design fixes; the next gate is a consolidated repaired design and its review, then explicit owner authorization for separately scoped engineering checks.
