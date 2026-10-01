# Agent rules for this repository (Codex, Claude Code, any other agent)

GeoMind research workspace. Authority: `GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md`. The current state is in `README.md`.

## Verification order (mandatory)

Run the cheapest checks first. A long stage starts only after every earlier stage has passed for exactly the current code:

| Stage | Time | How |
|---|---|---|
| tests | ~20 s | `.venv/bin/python -m pytest -q -x` after any code change; this is the only everyday check |
| full gated pipeline | estimate ~5 min (to be measured on first run) | `.venv/bin/python tools/verify_milestone.py --output evidence/c1_rNNN`: preflight → tests → smoke → mutation probe → recorded panel |
| independent review | 20–30 min | **once per milestone**, on the committed pipeline result |

- Finish **all** code and test edits before any long run. Never edit code while a long run is in progress.
- Never run the recorded panel (`-m geomind.run_c1`) or the mutation probe directly. Use the pipeline. Rerunning the pipeline resumes after the last stage verified for the same code; it never repeats a passed stage.
- Do not run a rehearsal before the recorded panel, and do not repeat long runs that already passed for the same code.
- Run one independent review per revision. Write a time cap (about 20 minutes) and a focused check list into the reviewer's instructions. A rejected review means: fix the code, register a new revision, run the pipeline once, then review once.
- Before starting anything that takes more than a few minutes, tell the user how long it will take and why.

## Enforcement (do not bypass)

- `tools/gate.py` is the single source of truth. Stamps in `.gate/` (git-ignored) are tied to a fingerprint of the hashed source files.
- Self-guards: `tools/verify_milestone.py` and `tools/mutation_probe.py` refuse to start a stage that is not ready.
- Agent hooks run `tools/gate_hook.py`: `.claude/settings.json` for Claude Code and `.codex/hooks.json` for Codex. Codex loads project hooks only after you trust the project's `.codex/` folder.
- Git pre-commit hook: run `git config core.hooksPath .githooks` once per clone. It refuses new panel evidence unless `PIPELINE.json` matches the committed code and its stamped artifacts re-verify. Never use `git commit --no-verify`; the agent hooks block it.
- Mutation definitions live in `tools/c1_mutants.py`. Update them there when code changes, never in the recorded evidence scripts.
- Hooks are a guardrail, not a hard boundary, in both Claude Code and Codex. The self-guards and the pre-commit hook back them up. Never work around a block: fix what it reports.

## Known gaps (by design, documented)

- The accepted C1 panel runner (`geomind/run_c1.py`) is frozen and cannot check the gate itself. Agent hooks and the pre-commit hook cover it. **Every new milestone runner (C2+) must call `tools/gate.py` `check("panel")` itself before running.**
- An agent that deliberately forges consistent artifacts and stamps can defeat local checks. The pre-commit fingerprint match and the once-per-milestone independent review are the backstop. Never forge or edit `.gate/`.

## Never

- Modify accepted code or existing evidence: `evidence/c0_review/`, and any `evidence/*/results.json` already committed.
- Run the C0 world experiment (`geomind.run_c0`) unless explicitly asked.
- Start a later milestone (C2+) before the current one is independently accepted.
- Assign numeric quality scores (such as 9/10).
