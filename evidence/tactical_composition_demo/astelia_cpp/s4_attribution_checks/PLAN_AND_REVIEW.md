# Scoped section-16 Part 1 plan

Explicit user scope: astelia_cpp/ plus docs/reviews/tactical_0g_s16_design_review_codex.md. This overrides the root-plan edit requirement. Preserve C6 timing, other untracked work and all prior fight evidence. No fights, tuning or judging; one build and one final affected-test batch.

| Step | Status | Disposition |
|---|---|---|
| Cross-family review of Claude section 16 | DONE | APPROVE_WITH_NOTES, named review file; notes frozen in runner contract. |
| Separate owner design recheck | DONE | s16_recheck, Codex (Claude unavailable), notes on clustering/proxy/terminal deaths/allocation/claims incorporated. |
| H/F skeleton switches, output-only traces and runner | DONE | Historical policy preserved; no v5 safety modifications. |
| Separate owner implementation recheck | DONE | s16_recheck, Codex; five blocking integration/harness seams fixed before build/tests. Fake trace-worker coverage added. |
| One build, one zero-combat affected-test batch | DONE | One build 24.38 s; 30 tests in 1.42 s; 16,290 synthetic legacy action comparisons. Zero fights; full combat fixture reruns excluded. |
| Readiness and scoped commit or verified bundle | DONE | READY_TO_RUN; scoped hook-checked bundle and adjacent delivery verification sidecar. Stop after Part 1. |

Request sent verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Paste-ready B3b root-plan update will be recorded here after verification.

Implementation recheck findings fixed before validation: factory H/F/HF admission; C++ baseline ADL lookup; explicit successful return in embedded historical contract; transitive build fingerprints; original v3 summation order for H and F fallback. Reviewer reported no unresolved blocking issue by inspection. The proposed fake-native streaming test is included in the final batch. No Claude-family implementation reviewer is available through this interface; this is an additional Codex adversarial recheck, not cross-family implementation acceptance.

Paste-ready root-plan B3b update:

> B3b Part 1 DONE: Codex section-16 design review APPROVE_WITH_NOTES; H/F/HF skeletons and fresh fixed-v3-B-knob 3,200-fight runner ready; READY_TO_RUN at astelia_cpp/S4_ATTRIBUTION_READINESS.md. Mandatory Codex recheck found factory/lookup/embedded-return/build-pin/summation seams, all resolved before one native build and one 30-test zero-combat batch. Full combat fixtures were not rerun while C6 times. No fights/tuning/judging; Part 2 remains after C6 timing ends. Normal hook-checked delivery bundle if workspace .git stays read-only. Claude implementation review remains separate.

Final artifact recheck: same verbatim request sent to s16_recheck after the one build/test batch. Reviewer confirmed timing/count/command/claim limits, with one documentation correction: gun exposure excludes the artillery dead zone while including annulus boundaries. Readiness and design-review wording corrected; review hash refreshed in INPUT_PIN.json. No policy/code/test change or repeat validation run. Bundle verification and workspace byte equality are recorded in S4_ATTRIBUTION_PART1.delivery.json beside the bundle.
