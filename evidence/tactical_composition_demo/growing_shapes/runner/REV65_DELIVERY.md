# Revision 6.5 repair delivery

Implementation complete; **NOT_READY** for execution pending independent delta re-review and separate owner fixture approval. No F1–F9, training, development or evaluation panel was run. Final affected suite: 47 passed in 0.85 s. One earlier setup failure is retained separately.

The repository permission profile makes `.git` read-only. No commit was attempted or hook bypassed. The delivery is `runner/REV65_REPAIR_BUNDLE.tar.gz`, with `REV65_REPAIR_MANIFEST.json` (member size, SHA256 and committed-before identity) and `REV65_REPAIR_VERIFICATION.json` (archive hash, extracted-byte verification and boundary checks). Paths in the archive are repository-relative. Every member and the archive are below 50 MB. No native build product, build directory, test cache or historical bulk ledger is included.

Base: committed design 702d9aa; imported integration 437e36a. Restore only the manifest-listed growing_shapes paths onto that base, preserving unrelated dirty/staged files, especially astelia_cpp and C6 work. Existing commits already retain the question file; its unchanged bytes and the pre-repair report/inventory are also included here. The report contains the disposition of each Claude finding, the clause coverage and the remaining gate. No accepted/frozen research file or committed result receipt is changed.

Local native images were explicitly rebuilt in isolated `_rev6_build/` directories and are not shipped. The code is accompanied by `REV65_BUILD_LOG.txt` and `REV65_SOURCE_IDENTITY.json`, which identify those images and the native build manifests. In this same workspace, those identities verify against the existing local images. On another workspace, explicitly build the isolated images using `.venv/bin/python -m evidence.tactical_composition_demo.growing_shapes.runner.build_rev6`; a different binary/build identity requires recording and reviewing the new native identities before any execution, not silently ignoring or replacing the delivered pins. There is no implicit legacy rebuild.

The affected test command is recorded exactly in `REV65_TEST_CHECKS.json`; it uses project-local cache/temp paths. Native parity is bounded to supplied synthetic observations in the shared gp_assay loop; actual-world F4 comparisons are implemented for a future owner-gated fixture run. The timing command was `.venv/bin/python -m evidence.tactical_composition_demo.growing_shapes.runner.rev65_timing --output evidence/tactical_composition_demo/growing_shapes/runner/REV65_BPATH_TIMING.json`. It performs only static synthetic B-path search, with zero integrated steps. Its raw timings and the refreshed F1–F9/development cost proxies are included.

A host-side commit can use the message “Fix 0h revision-6.5 integration review and section-19 contracts” with this required trailer:

```
Assisted-by: Codex:GPT-6
```

Commit only the coherent source/report/small-evidence scope. Native products and build directories are intentionally excluded from this delivery. Execution grants remain denied by default; no owner-approval record or review acceptance is supplied by this packet.

Assisted-by: Codex:GPT-6
