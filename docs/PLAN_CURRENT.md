# Current plan: step by step (the single source of truth for what we do next)

**Rule:** work follows this file, top to bottom, within each track. After every step, update its status line here and commit. If context is lost, read this file first, then `docs/IDEAS_AND_ROADMAP.md` (the tracker) and the files named in the step.

**Last updated:** 2026-10-06, revision 7.2 under review.

## Standing rules (from the owner; never skip)

1. **Never pause without a reason.** The only reasons to stop are:
   - the owner asks;
   - a hard approval gate (marked **[OWNER]** below);
   - being stuck.
2. **Owner recheck after every complex or important task** (also in `AGENTS.md`, "Owner recheck"). Send the owner's prompt **verbatim** to a reviewer from the other model family, fix the findings, then move on:
   > Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

   **The checklist for when it applies:** a design or revision; an engine, port or integration; a run and its report; a major analysis; a delivery others build on. Each step below lists its recheck.
3. **Cross-family review:** Codex implements and Claude reviews, or the reverse. One review per revision.
4. **Run approvals (decision 0031):**
   - **under 1 hour:** just run it;
   - **over 1 hour, before 22:00:** ask first, with the duration;
   - **from 22:00:** run what the plan needs, without asking.
   - **A registered one-shot final-exam run** is still announced first.
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
| A4 | Add 19.9 comparators (input average, K = 0, frozen positions) and review notes D1–D3 | DONE (`855d931`; 71 tests; Claude's short check READY_FOR_FIXTURES) | Codex, then a short Claude check | — |
| A5 | **Engineering tests F1–F9** | DONE: **FIXTURES_FAIL at F1b** (a 3-link path is too slow: 15.4 s; F1c compacts); F2–F4 pass; F5–F9 blocked (`growing_shapes/runner/REV6_FIXTURE_REPORT.md`) | Codex | done |
| A6 | Read the F results | DONE: a timescale mismatch (phase coupling far slower than the task clock) plus compaction | Claude | — |
| A6b | **Revision 7.3** (`DESIGN_0H_REV7.md`): λ = 8, pinned ends with separate neighbour lists, freeze-not-reset demand, empty start, N1, validity masks | DONE: **Codex round 4 APPROVE_WITH_NOTES** (12 → 7 → 4 → 3 low; notes applied) | Claude drafts, Codex reviews | — |
| A6c | Revision-7 integration (new files) | DONE: `55a9f7a` + repair `a660de0`; Claude review READY_FOR_FIXTURES (pin `3b6cf563…b551`; `growing_shapes_review_claude/REV7_FIXTURE_READINESS.md`) | Codex, then Claude | — |
| A6d | Fixtures N1, F1–F9 under 7.3 | DONE: FIXTURES_FAIL at F1c by 0.1 s (live geometry, 6 links); N1, F1a, F1b (2.5 s) and F2–F4 PASS; no collapse | Codex | decision 0031 |
| A6e | Revision 7.4: λ = 32, h = 0.005 | DONE: approved; fixtures **FAIL at N1d** (a knife-edge test start), but **N1f (the live layout) settles in 2.1 s**, so λ = 32 works | Claude, Codex | decision 0031 |
| A6f | Revision 7.5 fixtures | **N1 and F1–F4 PASS** (F1c, the live layout: 2.1 s, persistence 100%); F5 INVALID (Codex's measurement wrapper defect, not science) | Claude, Codex | decision 0031 |
| A6g | **Complete re-run N1–F9 with a new wrapper** (no line tracing) | **RUNNING** (`rev75b_fixture_run_20261006`) | Codex | decision 0031 |
| A7 | Cost projection from the measured F rates | — | Codex | — |
| A8 | **The development run** (48 trainings, about 16 h or more of serial compute) | — | Codex | **[OWNER] approve the run and its time** |
| A9 | Review the results, then the owner's recheck | — | Claude, then Codex | — |
| A10 | Then: reusable shapes, composition (deferred list, design section 10) | later | — | **[OWNER]** |

## Track B: 0g, beating Astelia's scripted AI in the tactical game

**Status:** v3 resonator beats novice (+17.4) and loses to regular (−7.6). Morale beats both.

| # | Step | Status | Who | Gate |
|---|---|---|---|---|
| B1 | v4 design (travel-time hold, commit focus, decision traces): `DESIGN_0G.md` section 15 | DONE | Claude | — |
| B2 | v4 implementation and development run | DONE, **NOT_READY / a negative result**: stage B resonator +9.4 against novice and **−22.2 against regular** (v3 −7.6); morale −15.4 (v3 +8.6); reversals not reduced; stage C stopped by the runtime guard before validation. One restart was caused by Claude editing `DESIGN_0G.md` during the run (a rule violation, owned) | Codex | — |
| B3 | Review v4, then the owner's recheck | DONE: recheck CHANGES_REQUIRED (`astelia_cpp/S4_V4_RECHECK_REPORT.md`): the focus pulls units into gun range; holds expire in danger; the reversal comparison mixed definitions | Codex, Claude | — |
| B3b | **2×2 attribution test** (hold × focus, fixed v3 knobs, fresh seeds; `DESIGN_0G.md` section 16) | Codex reviewing and implementing (light, while C6 measures); **the fights (about 10 min) run after C6 finishes** | Codex | decision 0031 |
| B4 | v5: one coherent intent per unit, progress checks, a damage-risk budget (the recheck's recommendation), informed by the 2×2 test; selection on regular-head S | — | Claude drafts, Codex reviews | — |
| B5 | Update the replay viewer (`viz_0g/`) with v4/v5 fights | — | Claude | — |
| B6 | S5 registration (W4: CLOSED) | DECIDED: no registration until a development version beats regular; then register with morale as a labelled comparator | Claude drafts | **[OWNER] approves the registered run** |

## Track C: C6 option B (a faster C6 engine)

| # | Step | Status | Gate |
|---|---|---|---|
| C1 | Port, parallel and recheck | DONE (`evidence/c6_option_b/`) | — |
| C2 | Official quiet-machine timing (is each world 360 s or less?) | **RUNNING since 16:17** (`evidence/c6_option_b/quiet_session_20261006_161801`); the first development world's reference took 355.9 s | the owner keeps the laptop light |
| C3 | If over 360 s: the owner decides the resource rule | — | **[OWNER]** |

## Decisions: taken by the drafter from the goal (the owner may overrule any of them)

1. **W4, 0g S5 registration: no registration yet.**
   - A registered run of a resonator that still loses to the regular script proves nothing toward the goal of beating the scripted AI with the new foundation.
   - Register only after a development version beats regular (v4 or v5).
   - The registration will then include **morale as a separately labelled comparator**, since it is the strongest simple controller. The resonator must be honest about it, not hide it.
   - The registered run itself still needs the owner's approval (AGENTS.md).
2. **C6 timing: starts automatically as soon as the 0g v4 run finishes** (01:30 at the latest), under `caffeinate`. The laptop should be kept light for the hour or two it takes. The batch waits up to 60 minutes for low load and records the conditions honestly. To cancel, say "no C6 tonight". Script: `scratchpad/c6night.sh`.
3. **Backup of the raw files outside git: not needed for progress (the owner agreed: keep them on the laptop for now).**
   - Almost all of them can be regenerated: deterministic code plus recorded seeds.
   - Their hashes and every report are in git.
   - They stay on the laptop. Deleting them later needs the owner's OK.

## Decisions only the owner can make

- (none open; the 0028 [R] items were ratified in decision 0031)

## How to resume after a context loss

1. Read this file, the tracker, and `git log --oneline -20`.
2. Check the running jobs: `ps aux | grep "codex exec"`. Their logs are in the session scratchpad (`*_last.txt`, `*.log`). If the scratchpad is gone, look at each step's report file named above. A report that has no final first line (READY / NOT_READY / STOP) means the job did not finish.
3. **Codex deliveries:** when Codex's `.git` is read-only, it leaves files in the workspace plus a bundle or tarball.
   - Verify that the workspace files equal the delivered ones.
   - Commit them with both `Assisted-by` trailers.
   - Ignore the bundles and tarballs; they are listed in `.gitignore`.
4. Continue with the first step that is not DONE and not waiting on **[OWNER]**.
