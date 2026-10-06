# Section 19.9 / D1–D3 source delivery

READY_FOR_FIXTURES as implementer readiness: section 19.9 and notes D1–D3 are implemented, and the single affected synthetic-suite run passed **71 tests in 1.78 s** (2.183 s subprocess wall time). This delta still requires independent review and separate owner fixture authorization. No F1–F9 execution, native World episode, training, development run or evaluation panel was run.

The supplied filesystem profile grants read-only access to `.git`; no commit was attempted and no hook was bypassed. The source-only archive is `runner/REV65_19_9_SOURCE_BUNDLE.tar.gz`. Its `REV65_19_9_SOURCE_MANIFEST.json` records repository-relative paths, sizes, SHA256 hashes and HEAD-before identities. `REV65_19_9_SOURCE_VERIFICATION.json` records the archive hash, extracted-byte verification, local scientific-input verification and the preservation of the historical construct receipt. Every member and the archive are under 50 MB. No native image, object, build manifest/directory, cache or temporary test file is shipped; the textual build log is included.

Apply only manifest-listed paths under `evidence/tactical_composition_demo/growing_shapes/` to the recorded base commit, preserving unrelated dirty or staged work. The committed governing design is `2796010684cc6fff79abd8e383929ae3d3591393`; its bytes are unchanged and pinned at SHA256 `ca9c43362e3eebace889c7306784ffe5dd3095a58eb2095473f745eff31b52c5`. The historical `REV6_CONSTRUCT_ONLY.json` is unchanged. The new labelled construct-only receipt includes its historical hash and the current F3/F6/F9 recipes; it is not fixture evidence.

The source identity also binds local native images and their local build manifests. Those build products are intentionally excluded from the archive. In this workspace the 42 scientific identities verify against the explicitly rebuilt isolated images. In another workspace, build explicitly with:

```
.venv/bin/python -m evidence.tactical_composition_demo.growing_shapes.runner.build_rev6
```

A different native image or build-manifest identity requires recording and reviewing new identities before any execution; do not bypass, silently replace or ignore the delivered pins. The build does not authorize fixtures. The exact affected synthetic test command and execution exclusions are recorded in `REV65_19_9_TEST_CHECKS.json`; the result is in `REV65_19_9_TEST_LOG.txt`. The build log records compiler/source/dependency identities. No source or test edit followed the passing suite.

Suggested host-side commit message:

```
Add 0h revision-6 descriptive comparators and close delta-review notes

Assisted-by: Codex:GPT-6
```

Commit only this coherent source/report/small-evidence scope. Native build products and other-session astelia_cpp/C6 work remain outside the delivery.

Assisted-by: Codex:GPT-6
