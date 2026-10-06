SOURCE_ONLY_DELIVERY

Revision 7.7 workspace implementation and source overlay, base checkout `1fce0df77e920c380f565508c8c639fe376752e1`.

Design review: APPROVE_WITH_NOTES, docs/reviews/tactical_0h_rev77_design_review_codex.md. The design remains unchanged. Native and independent Python strong-path graphs are implemented; D4, qualification, phase/motion dynamics and budget keep their full graph. Review explicitly rejects a guaranteed three-second six-link settling time. This is a provisional engineering repair.

Validation: 108 synthetic tests passed in 2.43 s on the single final invocation, after recheck, final native build and last configuration/source regeneration. Tested execution-pin SHA256: `71f876f61921641bea41e36d873a336a2c2d1ae0e642d8ff851226e55fecaa60`. No N1/F1–F9, training, development or panels ran. READY_FOR_REVIEW means pending Claude implementation review of this exact pin, not fixture acceptance or authorization.

Commit refused: scoped git add exited 128 because `.git/index.lock` creation returned `Operation not permitted`. No commit or hook/permission bypass occurred. COMMIT_ATTEMPT.json records the refusal; COMMIT_MESSAGE.txt preserves the intended `Assisted-by: Codex:GPT-6` trailer. Workspace changes remain available.

Verified source fallback: ../REV77_SOURCE_ONLY.tar.gz plus ../REV77_SOURCE_ONLY_MANIFEST.json. Run `python3 evidence/tactical_composition_demo/growing_shapes/runner/rev77_delivery/deliver.py` from this workspace to reverify hashes, preserved inputs and package contents. DELIVERY_VERIFICATION.json records archive identity, member sizes and native-product exclusion. Each member and the archive are strictly below 50,000,000 bytes; native images, caches, scratch directories, old archives and raw experiment outputs are excluded. Historical integration metadata are included as labelled PRIOR_* files; they do not authorize current execution.

This is an overlay on the stated checkout and inherited local dependencies, not a complete standalone checkout. Source-only transport cannot include the tested native binary. After applying the overlay elsewhere, explicitly rebuild the native image from final sources and regenerate the image/source pin before review or any subsequently authorized execution; the local tested pin does not certify a different rebuild. Recorded fixture inputs/results and entropy inventory must remain unchanged. docs/PLAN_CURRENT.md and unrelated dirty/staged work are untouched.

Assisted-by: Codex:GPT-6
