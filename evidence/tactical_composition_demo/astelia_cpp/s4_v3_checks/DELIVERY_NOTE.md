# 0g v3 delivery

Status: READY_FOR_S5 (completed development only; independent Claude review, owner margin and a fresh S5 specification remain pending). Final regular-head resonator mean S = −1.655. No registration, judging seeds or recorded run.

Shared `.git` is read-only. Commits are in an isolated clone, `/private/tmp/ai_rpg_0g_v3_delivery`, with `.githooks` enabled. Both commits carry `Assisted-by: Codex:GPT-6`; no enforcement bypass was used. The shared working tree contains all delivered files, but its index, refs and unrelated growing_shapes/C6 changes were not altered by this task.

- Base: `f98376413da023bd889f4590469e94a43d17c738` (f983764, answering the section-14 artillery check).
- Part 1: `cb9c9df2fb16c80501096078521d75361d10901e`, committed and bundled before development. The 113 affected tests passed once; 408 predecessor fixture summaries are byte-identical. The bundle was imported independently and all 18 committed file hashes matched.
- Part 2: the next commit after Part 1 in `commits.bundle`; final identity and transport hash are in the adjacent `BUNDLE_VERIFIED.json` (external transport receipt, avoiding circular bundle hashes).

Part 2 includes the complete fresh-seed development, final report, audit, planning, timeout/gun counts and all twelve HTML/raw/packaged replays. Full amended budgets and validation completed in 167.65 measured execution minutes, with the predeclared combined 360-minute cap and 34.48 prior minutes. Audit: 107,094 fresh score fights plus 12 replay captures, 2,304 CMA candidates, zero failures/forks/search calls/artillery rollouts. No native fight or test was executed by the post-run reconstruction.

`DELIVERY_CONTENTS.json` binds every task file to its SHA256. `BUNDLE_VERIFIED.json` records verification of the complete bundle, a separate repository import, the exact two commits, the path-only scope check and every imported blob against the delivered workspace. `commits.bundle` requires base f983764; `part1.bundle` is the earlier standalone Part 1 delivery. Existing v1/v2 transport artifacts are unrelated and were not included or modified.

For a reviewer, start with `S4_V3_DEVELOPMENT_REPORT.md`, `s4_v3_development/AUDIT.json`, `s4_v3_checks/PART1_PARITY.json` and `s4_v3_development/run_identity.json`. The run code and its optimizer/source/build/design pins are unchanged since execution. Build products and the shared result cache remain local and ignored; their identities are preserved in the committed evidence. Do not rerun development or reuse its seeds as judging entropy.

To inspect/import the delivery in a separate clean review worktree, preserving the shared workspace's unrelated work:

```sh
git bundle verify /Users/new/RiderProjects/ai_RPG_test/evidence/tactical_composition_demo/astelia_cpp/s4_v3_checks/commits.bundle
git fetch /Users/new/RiderProjects/ai_RPG_test/evidence/tactical_composition_demo/astelia_cpp/s4_v3_checks/commits.bundle HEAD:refs/heads/codex-0g-v3-delivery
```

The imported branch is based on f983764. Review or cherry-pick its two task commits only after reconciling the already-delivered local task files in the intended worktree. Do not reset, clean or stash unrelated work. The old stop report remains in the base commit's history; the final report replaces it at the requested path.
