# Section-16 Part 1 delivery

Design review: APPROVE_WITH_NOTES in docs/reviews/tactical_0g_s16_design_review_codex.md. Engineering status: READY_TO_RUN in ../S4_ATTRIBUTION_READINESS.md. This delivery stops before all fights and tuning.

Session filesystem policy exposes workspace .git as read-only. Delivery uses an isolated writable Git directory under astelia_cpp/build/, a parent at the current workspace HEAD, and the original project hooks via an absolute core.hooksPath. No workspace Git metadata is changed and no hook is disabled. Provenance trailer: `Assisted-by: Codex:GPT-6`.

The bundle `S4_ATTRIBUTION_PART1.bundle` contains the scoped commit. Its head, hash, hook results and workspace-to-commit byte comparison are recorded in the adjacent delivery verification sidecar. Verify it with `git bundle verify evidence/tactical_composition_demo/astelia_cpp/S4_ATTRIBUTION_PART1.bundle` before fetching its `attribution-part1` branch. Preserve unrelated dirty/untracked work. The bundle excludes ignored build outputs, temporary test roots and delivery Git metadata.

Scope: only astelia_cpp/ files and the named design review. Native changes add H/F/HF admission, independently switch historical hold/focus, and opt in to attribution trace fields. New scripts declare the exact fight allocation, fixed knobs, observer counters, cluster statistics and bounded future run. New synthetic contract embeds namespace-isolated pre-change controller sources for exact zero-combat action comparisons. Original DESIGN_0G, prior receipts, seeds, reports and combat rules are preserved.

Validation: one sequential native build 24.38 s; one affected pytest batch, 30 passed in 1.42 s (1.68 s process elapsed), with 16,290 synthetic action output/bit comparisons. Tests invoke only --attribution-contract plus fake workers/executable. No World/fight is advanced by those tests, no native test rebuild occurs, and no combat panel/fixture or tuning executes. BUILD_RESULT.json, TEST_RESULT.json, NATIVE_CONTRACT.json and logs retain the evidence. Full historical combat-summary parity remains unexecuted under the explicit no-fights instruction.

Owner recheck and fixes: PLAN_AND_REVIEW.md. The additional reviewer was Codex (Claude unavailable in the interface); this does not substitute for cross-family implementation acceptance. The design review itself is Codex review of Claude's design. Root docs/PLAN_CURRENT.md is outside the permitted edit scope; a paste-ready update is in the scoped plan.

Use the exact future command in the readiness report only after C6 quiet-machine timing finishes. Expected ten-worker cost is about 10–30 minutes, cap 60 minutes; exactly 3,200 fights including 80 traced fights, no extra captures. A consumed ledger cannot be reused. No run result, superiority claim, v5 choice, milestone acceptance or S5 approval is made.
