# Current plan: step by step (the single source of truth for what we do next)

**Rule:** work follows this file, top to bottom, within each track. After every step, update its status line here and commit. If context is lost, read this file first, then `docs/IDEAS_AND_ROADMAP.md` (the tracker) and the files named in the step.

**Last updated:** 2026-10-06, 13:00.

## Standing rules (from the owner; never skip)

1. **Never pause without a reason.** The only reasons to stop are:
   - the owner asks;
   - a hard approval gate (marked **[OWNER]** below);
   - being stuck.
2. **Recheck every serious chunk.** After each finished engine, port, design or run, send the owner's recheck prompt (verbatim, in `memory/recheck-every-serious-chunk.md`) to the other model family, fix the findings, then move on.
3. **Cross-family review:** Codex implements and Claude reviews, or the reverse. One review per revision.
4. **Run nothing big without the owner's approval** of that exact run.
   - **Unattended runs** use `caffeinate -i -s`.
   - **Raw logs** stay out of git: every file under 50 MB, listed by hash.
5. **Change no code while a long run is in progress.** Tests run once per change batch.
6. **Recorded verdicts are never re-analyzed** to change them. A design change means a new revision with fresh seeds.
7. **Keep the tracker current,** and use this file for the plan.

## Track A: 0h growing shapes (the new AI foundation)

**Goal:** a grown oscillator network routes sensor input to an output and does better than simple baselines. Then reusable shapes, then composition.

| # | Step | Status | Who | Gate |
|---|---|---|---|---|
| A1 | Revision-6 design | DONE: 6.5 (`evidence/tactical_composition_demo/DESIGN_0H_REV6.md`), Codex review rounds 1–6, APPROVE_WITH_NOTES | Claude drafts, Codex reviews | — |
| A2 | Implementation | DONE: `growing_shapes/runner/rev6_*`, `medium/rev6_*`; 47 tests | Codex | — |
| A3 | Implementation review | DONE: READY_FOR_FIXTURES (`growing_shapes_review_claude/REV6_INTEGRATION_REVIEW.md`, delta at `bba9348`) | Claude | — |
| A4 | Add 19.9 comparators (input average, K = 0, frozen positions) and review notes D1–D3 | **RUNNING** (Codex; prompt `scratchpad/cmp6_prompt.txt`) | Codex, then a short Claude check | — |
| A5 | **Engineering tests F1–F9** (about 2–6 min) | WAITING | Codex runs, Claude reviews | **[OWNER] approve the F1–F9 run** |
| A6 | Read the F results | — | Claude | If F1/F5 show that structure collapses under C4 motion: go to A6b. Otherwise: A7. |
| A6b | Next revision: an **anchoring decision**, plus the deferred ideas (freeze-not-reset demand timers, empty start, possibly overlap placement); see `docs/reviews/external_web_ai_rev6_recommended_design_assessment.md` | — | Claude drafts, Codex reviews | **[OWNER]** approves the design |
| A7 | Cost projection from the measured F rates | — | Codex | — |
| A8 | **The development run** (48 trainings, about 16 h or more of serial compute) | — | Codex | **[OWNER] approve the run and its time** |
| A9 | Review the results, then the owner's recheck | — | Claude, then Codex | — |
| A10 | Then: reusable shapes, composition (deferred list, design section 10) | later | — | **[OWNER]** |

## Track B: 0g, beating Astelia's scripted AI in the tactical game

**Status:** v3 resonator beats novice (+17.4) and loses to regular (−7.6). Morale beats both.

| # | Step | Status | Who | Gate |
|---|---|---|---|---|
| B1 | v4 design (travel-time hold, commit focus, decision traces): `DESIGN_0G.md` section 15 | DONE | Claude | — |
| B2 | v4 implementation and development run (amended S4 protocol, fresh seeds, 360 min) | **RUNNING** (Codex; prompt `scratchpad/v4b_prompt.txt`) | Codex | (development authorized: "go ahead, improve the AI") |
| B3 | Review the v4 report (`astelia_cpp/S4_V4_DEVELOPMENT_REPORT.md`), then the owner's recheck | — | Claude, then Codex | — |
| B4 | v5: a progress-aware release of the hold (planned in `DESIGN_0G.md` after section 15), with thresholds from the v4 traces | — | Claude drafts, Codex reviews | — |
| B5 | Update the replay viewer (`viz_0g/`) with v4/v5 fights | — | Claude | — |
| B6 | **W4: what to register for S5** (as written, or plus a morale endpoint) | WAITING | — | **[OWNER] decision** |

## Track C: C6 option B (a faster C6 engine)

| # | Step | Status | Gate |
|---|---|---|---|
| C1 | Port, parallel and recheck | DONE (`evidence/c6_option_b/`) | — |
| C2 | Official quiet-machine timing (is each world 360 s or less?) | WAITING for an idle laptop (prompt `scratchpad/c6quiet_prompt.txt`; the stopped partial attempt is in `evidence/c6_option_b/quiet_session/`) | **[OWNER] tells us when the laptop is idle** |
| C3 | If over 360 s: the owner decides the resource rule | — | **[OWNER]** |

## Decisions waiting for the owner (one line each)

1. **Approve the 0h engineering tests F1–F9** (about 2–6 min). (A5)
2. **W4:** register 0g S5 as written, or plus a morale endpoint. (B6)
3. **When is the laptop idle** for the C6 timing? (C2)
4. Confirm the [R] readings in decision 0028, items 16–18.
5. Where to keep the raw files outside git (about 15 GB: `evidence/LARGE_FILES_OUTSIDE_GIT.json`, the 0h ledgers).

## How to resume after a context loss

1. Read this file, the tracker, and `git log --oneline -20`.
2. Check the running jobs: `ps aux | grep "codex exec"`. Their logs are in the session scratchpad (`*_last.txt`, `*.log`). If the scratchpad is gone, look at each step's report file named above. A report that has no final first line (READY / NOT_READY / STOP) means the job did not finish.
3. **Codex deliveries:** when Codex's `.git` is read-only, it leaves files in the workspace plus a bundle or tarball.
   - Verify that the workspace files equal the delivered ones.
   - Commit them with both `Assisted-by` trailers.
   - Ignore the bundles and tarballs; they are listed in `.gitignore`.
4. Continue with the first step that is not DONE and not waiting on **[OWNER]**.
