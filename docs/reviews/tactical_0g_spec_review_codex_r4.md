APPROVE_WITH_NOTES
Reviewer family: Codex
Reviewed SPEC_0G.json SHA256: 158031e9e90b9cc86feb840eca81917ca4913416bb683be6172434a64f7c8335

Reviewed revision 4 on 2026-10-05 within the requested approximately 10-minute cap. Reviewed HEAD: `599d2b084d1f1f4095f979cd0c86c69867207d47`. The working tree was clean at entry. Companion `SPECIFICATION_0G.md` SHA256: `6f2f354f3cfaf5ae76f793ce036f5fd807b1866be8df72b9d3059ee0c8336ea7`.

The registration as a whole is approved with the execution notes below. Both revision-3 findings are resolved; no blocking registration finding remains. This verdict is specification approval, not runner acceptance, owner approval or authorization to execute S6. Unless prefixed with `docs/`, paths below are relative to `evidence/tactical_composition_demo/`.

## Revision-3 findings

| Finding | Revision-4 disposition |
|---|---|
| 1 — stale review gate | **Resolved.** `SPEC_0G.json:331` names `docs/reviews/tactical_0g_spec_review_codex_r4.md`, requires an approving first-line verdict and this specification's exact hash, and requires later revisions to name their own review file. This report satisfies that registered review condition. Historical rejection reports remain unchanged. |
| 2 — explanation embedded in manifest path | **Resolved.** `SPEC_0G.json:22` is exactly `astelia_cpp/build/astelia_native.build.json`. The separate `engine.manifest_rule` at line 23 requires both the registered manifest digest and equality of its `binary_sha256` field with `engine.binary_sha256`. The named file exists; its digest and binary-hash equality both match. The binary also matches its registered digest. |

The Markdown self-audit records both fixes and their causes (`SPECIFICATION_0G.md:110–111`).

## Exact change boundary and whole-registration assessment

Inspected the requested `git diff 2b023e7..599d2b0 -- evidence/tactical_composition_demo/SPEC_0G.json` and independently compared the parsed JSON objects. The complete set of changed semantic paths is:

- `/revision`: 3 → 4;
- `/authority_chain`: append the revision-3 review reference, preserving all previous entries;
- `/engine/build_manifest`: remove the parenthetical explanation;
- `/engine/manifest_rule`: add the explicit manifest identity rule;
- `/gates/codex_review`: name this revision's report and retain verdict/hash requirements.

Nothing else in the governing JSON changed. In particular, requests, opponent profiles, knobs and their source pins, scoring, judging root/derivation, panels, statistics, alpha, endpoint predicates, delta, n, validity/dependency rules, host timeouts, persistence/latch rules and diagnostic selection are unchanged. Current specification bytes also equal the committed revision-4 bytes. The companion Markdown diff changes only the revision heading and adds the two self-audit rows.

Re-reading the whole registration preserves the revision-3 assessment: P1 requires both levels for support; P2/P3 use fixed paired comparators and complete blocks; exact alpha allocations total `1/100`; invalid or missing required fights prevent endpoint bounds; descriptive arms cannot veto substantive endpoints; P1 cannot stop POOL; schedule and attempt retention precede dispatch; the one-shot latch forbids retries. Totals remain 400 required P1 fights, 1,216 fights per POOL arm, 6,464 scheduled fights overall, and 57 diagnostics reusing scheduled fights. The t calibration remains explicitly approximate, and the adverse development expectations and limited claims remain disclosed. No new statistical or experimental registration defect was found in this bounded re-review. Unchanged historical development calculations were not rerun.

## Notes and remaining execution gates

1. **Runner compatibility remains separate.** The inspected runner (`astelia_cpp/s6_run.py` SHA256 `a2d66caa62b61134ae81d0791a1fe4477ff371a47f321cad9d7ae87be7174a08`) still accepts only revision 3 (lines 112–113). Its review-path parser splits on a comma (line 115), whereas revision 4 separates the path from its rule with a colon; accepting revision 4 alone would therefore still select an incorrect path. The implementer must adapt both before execution and verify the complete revision-4 contract. Its explicit manifest-path and digest/equality checks at lines 132–140 align with the corrected registration. This document review does not certify the rest of the runner or its tests.
2. **Owner gates remain outstanding.** The owner must approve delta and n and authorize S6 naming the reviewed specification hash. `astelia_cpp/S6_AUTHORIZATION.json` and the fixed `astelia_cpp/s6_run` directory were absent during this review. The unused-root statement remains a drafter assertion; no judging seeds or run history were reconstructed to validate it.

At final scope verification, concurrent modifications to `astelia_cpp/s6_run.py` and `astelia_cpp/test_s6_run.py` had appeared. I did not create or modify them, and did not review the new bytes. The runner note above refers only to the identified snapshot. HEAD and both specification hashes remained unchanged; the registration verdict does not depend on the concurrent implementation edits. Whitespace checks passed for the review file.

Scope: read AGENTS.md, current-source guidance, the read-only review skill, both specifications, the revision-3 report and the relevant runner preflight; inspect Git diffs/state; use standalone standard-library JSON comparison and artifact hashing. No project module was imported or executed. No real judging seed was derived; no fight, game code, project test, smoke, optimizer, build, mutation probe, recorded panel or commit was run. This reviewer wrote only this review file.
