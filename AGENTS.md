# Agent rules for this repository (Codex, Claude Code, any other agent)

GeoMind research workspace. Authority: `GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md`. Milestone status lives only in `STATUS.json` (README shows a generated table). Process design and rationale: `docs/PROCESS_REVIEW.md`.

## Milestone lifecycle (C4 onward)

1. **Propose** (`experiments/cN_proposal.md`), and get owner approval.
2. **Register:** commit `experiments/cN_manifest.json` (all endpoints and verdict rules) and `milestones/cN.json` (dependencies, stage commands, mutants, implementer family) **before** any run on final seeds.
3. **Implement** in new files (`geomind/cN_*.py`, `geomind/run_cN.py`, `tests/test_cN.py`, `tools/cN_mutants.py`). The runner must call `tools/milestones.py` `check("cN", "panel")` itself.
4. **Verify once, in order:** `.venv/bin/python tools/verify.py --milestone cN --output evidence/cN_rNNN` runs preflight → tests → smoke (non-panel seeds) → parallel mutation probe → recorded panel. A rerun resumes after the last stage verified for the same code.
5. **Commit the evidence.** The pre-commit hook checks registration order, the `PIPELINE.json` record, endpoint coverage and the status block.
6. **One independent review** per revision, by the **other model family** (Claude ↔ Codex), with a time cap of about 15–20 minutes. It goes in `evidence/cN_rNNN_review_<family>/INDEPENDENT_REVIEW.md`: first line the verdict, a `Reviewer family: <family>` line, and the SHA256 of the reviewed `results.json`.
7. **ACCEPTED:** update `STATUS.json`, run `python3 tools/status.py --write`, and freeze the files. **CHANGES_REQUIRED:** fix, register a new revision on fresh seeds, verify once, review once.
   An implementer who finds a design defect before review **withdraws** the revision in a decision record (`docs/decisions/`), keeps its evidence unchanged and registers the next revision on fresh seeds. Never re-analyze a recorded panel to change its verdict.

## Verification order (mandatory)

| Stage | Time | How |
|---|---|---|
| tests | ~20–30 s | `.venv/bin/python -m pytest -q -x` after any code change; this is the only everyday check |
| gated pipeline, C4+ | measure on first run | `tools/verify.py --milestone cN --output evidence/cN_rNNN` |
| gated pipeline, C1/C2 (legacy) | C1 R006 measured 185 s | `tools/verify_milestone.py` (C1) and `tools/verify_c2.py` (C2) |
| independent review | ≤ 20 min | once per revision, on committed evidence |

- Finish **all** code and test edits before any long run. Never edit code while a long run is in progress.
- Never run a recorded panel or mutation probe directly; use the pipeline. Do not run a rehearsal panel. Do not repeat runs that already passed for the same code.
- **Every registered endpoint** must appear in the receipt's `endpoint_coverage` as `evaluated` (value and verdict) or `not_run` (reason). No endpoint may be test-only and silently missing (the C2 lesson).
- Before starting anything that takes more than a few minutes, tell the user how long it will take and why.

## Provenance and status

- Every commit carries a provenance trailer: `Assisted-by: Claude:<model>`, `Assisted-by: Codex:<model>`, or `Human-authored: yes`. The commit-msg hook enforces this.
- Change milestone status only in `STATUS.json`, then run `python3 tools/status.py --write`. The pre-commit hook rejects a stale README block. Do not hand-edit status prose in README or the standard.

## Enforcement (do not bypass)

- **C4+ (generic):**
  - `tools/milestones.py` is the gate: per-milestone dependency fingerprints, with stamps in `.gate/<cN>/` re-verified by artifact hash and content.
  - `tools/verify.py` and `tools/milestone_mutation.py` refuse stages that are not ready.
  - `tools/milestone_hook.py` (agent hook) and `tools/milestone_precommit.py` (git) enforce the same rules.
- **C1/C2 (legacy, frozen):** `tools/gate.py`, `tools/gate_hook.py` and `tools/precommit.py`.
- **Wiring:** agent hooks run both hook scripts, in `.claude/settings.json` (Claude Code) and `.codex/hooks.json` (Codex; loaded only after you trust the project's `.codex/` folder). Git hooks are in `.githooks/`; run `git config core.hooksPath .githooks` once per clone. Never use `git commit --no-verify`; the agent hooks block it.
- Hooks are a guardrail, not a hard boundary, in both tools; the self-guards and git hooks back them up. Never work around a block: fix what it reports. Never forge or edit `.gate/`.

## Accepted and frozen

**C1 R006** is independently accepted (commit 721249b). Do not modify these files:

- `geomind/incremental.py` `fcbb18a41f151da3d93c47f9779af0ae46adc3e45fe2f61581f825ab66118b23`
- `geomind/run_c1.py` `c561625056311ecee9ff795844b67775567db49a7b40f1697b4e6a9c74cbdeb5`
- `geomind/c1_cases.py` `56f080e4e06eecdcfcc2910250003d9b5d5a745b37f32d65b564c7876348bf05`
- `geomind/c1_reference.py` `1f853a205d18a26b7c9e544d8c3dd04980096ac56ced259672e40486a3c14df4`
- `tests/test_c1.py` `31ff88acd1c7b7df479153063283d891fde2dd855e9bc9a9ebbf38eee343dd5e`
- `experiments/c1_manifest.json` `a96767c7b9548e35dd1b9974873b7295fd7cc8aea66b21698195489dae6bf4b4`

**Bound by accepted receipts:** the C1 R006 and C2 R002 receipts bind every file listed in their `results.json` `file_hashes`. That includes `tools/gate.py`, `tools/gate_hook.py`, `tools/precommit.py`, `tools/mutation_probe.py`, `tools/verify_milestone.py`, `tools/verify_c2.py`, `tools/c1_mutants.py`, the C2 tools, `tests/test_gate.py`, `tests/test_c2*.py` and the C2 sources. **Never edit them**; add new files instead. Check with the identity snippet in `docs/PROCESS_REVIEW.md` or by comparing against `file_hashes`.

Open low notes for a future C1 revision, not blocking: R1 (`_validate_delta` should require `type(edge) is Constraint`) and R2 (state the re-anchoring cost in receipt-generated limits).

## Known gaps (by design, documented)

- The frozen C1/C2 runners cannot be changed to check the gate themselves; agent hooks and git hooks cover them. Every C4+ runner must call the gate itself.
- An agent that deliberately forges consistent artifacts and stamps can defeat local checks. The pre-commit fingerprint and registration-order checks and the cross-family review are the backstop.

## Never

- Modify accepted code, receipt-bound files or committed evidence receipts (`evidence/*/results.json`, `evidence/c0_review/`).
- Run the C0 world experiment (`geomind.run_c0`) unless explicitly asked.
- Start a milestone whose proposal the owner has not approved, or C3 (not authorized after the C2 stop decision).
- Assign numeric quality scores (such as 9/10).
