# Current plan: step by step (the single source of truth for what we do next)

**Rule:** work follows this file, top to bottom, within each track. After every step, update its status line here and commit. If context is lost, read this file first, then `docs/IDEAS_AND_ROADMAP.md` (the tracker) and the files named in the step.

**Last updated:** 2026-10-06 19:00. Tonight: the 0h 7.7 fixtures at 22:00 → the C6 timing-only re-run (waits for load < 3) → the 0g v5 development (about 4–6 h). Log: `scratchpad/evening_chain.log`. Older note: The 0h fixtures run now (the owner's go). `scratchpad/g16_chain.sh` runs the 0g 2×2 test after the C6 timing finishes (log `evening_chain.log`).

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
| A6g | Revision 7.5 complete re-run (rev75c) | DONE: N1 and F1–F4 PASS; **F5 FAIL**: the output port was deleted (D1 and D3) and could not be reborn (budget), so no assay had an output | Codex | — |
| A6h | **Revision 7.6:** O protected (exempt from D1, D3 and D4; outside the budget) | DONE: Codex review APPROVE_WITH_NOTES; implemented (93 tests); Claude check **READY_FOR_FIXTURES** (pin `43b0f578…`) | Claude, Codex | — |
| A6i | 7.6 fixtures N1–F9 | DONE (the owner's go): N1 and F1–F4 PASS; **F5: paths now form (E 0.8 and 0.7) and the output persists, but the response is too slow** (A 0.22, against 0.3): the last link sits 2.2–2.6 m.u. from O (weight about 0.008) | Codex | — |
| A6j | **Revision 7.7:** strong links (w ≥ 0.5, r ≤ 0.833) | DONE: Codex APPROVE_WITH_NOTES; implemented (108 tests); Claude check **READY_FOR_FIXTURES** (pin `9628282d…`) | Claude, Codex | — |
| A6k | 7.7 fixtures | DONE (the owner's go): **FAIL at F1b and F1c only on the strong-path fraction**; their responses PASS; the pinned last link sits at 0.87 (> 0.833) | Codex | — |
| A6l | Revision 7.8 (a radius 1.177) | **REJECTED** by Codex (F1c degree is 6; F1c's last link sits at 1.41) | — | — |
| A6m | **Revision 7.9:** strong edge = actual coupling rate ≥ 0.5 /s | DONE: Codex APPROVE_WITH_NOTES (saved F1b and F1c strong paths at 100%; weak links excluded); implemented (122 tests); Claude check **READY_FOR_FIXTURES** (pin `27a3c462…`) | Claude, Codex | — |
| A6n | 7.9 fixtures | DONE: N1 and F1–F4 PASS; **F5(ii) PASS (A 1.21, B 1.18 rad, E 0.7): the first grown network responding through its grown path**; F5(i), the empty start, FAILS (8 half-bridges filled the budget) | Codex | — |
| A6o | Revision 7.10 (the smallest deficit first) | DONE; fixtures **FAIL at F5**: (ii) response strong (A 1.14) but max E 0.45 < 0.5; (i) the empty start still never connects (the budget refuses 102 births) | Claude, Codex | — |
| A6p | **Revision 7.11: output first** (both B-path births to the smallest-deficit site; B1 deferred until a strong output path exists) | DONE (`a52ddbd`): **FIXTURES_FAIL**. N1, F1–F4 PASS; **F5(ii) PASS** (A 1.451, B 1.303, max E 0.8); **F5(i) FAIL** (A 0.19, B 0.21, E 0). Claude's reading: in (i) a strong site→O path was **closed at every check from 180 s to 440 s but dissolved before the next check** each time; the budget ran out at about 440 s and the chain then retracted (tip 0.9 → 2.4 m.u.). In (ii), paths held between checks from 280 s, with 4 elements packed around O. **The gap is holding a closed link, not growing one** | Claude, Codex | decision 0031 |
| A6q | **Why F5(i) fails: diagnosis** (`growing_shapes_review_claude/rev711_diag/REV711_F5I_DIAGNOSIS.md`, **revision 3**) | **DONE after two owner rechecks.** Round 1 (`01b2d27`) CHANGES_REQUIRED R1–R4 → revision 2; round 2 (`b4f4d1e`) CHANGES_REQUIRED R2-F1 (one pilot contaminated by recovery clones: INVALID, withdrawn), R2-F2 (root-group pilot misreported), R2-F3 (scaffold and O-swap claims overbroad), R2-F4 (durations) → **all fixed in revision 3**. Finding: in the empty start each closing link is lost because the motion law pulls the tip back (−0.30 to −0.64 m.u./s); **no tested intervention sustained late connectivity in both starts**; long transient successes exist in (i). The seeded trajectory is sensitive to its scaffold (ring or zero gain fail; one random-phase run passes), but **no minimal embryo is identified** | Claude, Codex | decision 0031 |
| A6r | **Separated comparison with fixed instrumentation and the validated F5 pilot assay** (the baseline reproduces the fixture exactly) | **DONE: C2, a root-relative O pin (O placed once 1 m.u. from the origin toward the first effective root, then frozen), meets the F5 gate shape in BOTH starts:** (i) A 1.042, B 1.271, max E 0.8; (ii) A 1.519, B 1.252, max E 0.7. C3 (a single root group) does not rescue (i). Pilot, no verdict (`REV711_F5I_DIAGNOSIS.md` §8) | Claude | decision 0031 |
| A6s | **Revision 7.12 = C2** (DESIGN_0H_REV7 §19 + 19.6): a root-relative output pin; M/U use the same rule; assays copy the pin | **Design APPROVED** (Codex APPROVE_WITH_NOTES, notes applied as 19.6). **Implementation and the registered fixtures wait for the owner's approval of the pin change** | Claude, Codex | **[OWNER] approve the O-pin contract change** |
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
| B3b | **2×2 attribution test** | **DONE**: exactly 3,200 fixed-v3-knob development fights + 80 embedded traces once under caffeinate; 943.418 s elapsed / 943.459 s awake. Report DONE; owner recheck APPROVE_WITH_NOTES, no blocking defect. `astelia_cpp/S4_ATTRIBUTION_REPORT.md` | Codex | decision 0031 |
| B4 | **v5** (`DESIGN_0G.md` section 17, amended): the v3 skeleton, tuned on regular-head S with novice eligibility, **A and B only**, the gate > −7.62 | **DONE: development PROGRESS / S5 NOT_READY.** Exactly 60,996 fresh fights once under caffeinate, 64.198 min elapsed / 64.197 awake; B resonator novice +5.600, regular −6.025 (>−7.62). Regular remains negative; historical v3 B novice +17.350 falls to +5.600. Melee/ranged omega −0.3583/−1.9120 rad/s, diagnostic only. New output `astelia_cpp/s4_v5_development_20261006_2308`; report `astelia_cpp/S4_V5_DEVELOPMENT_REPORT.md`. Owner explicitly removed all C6/low-load waiting; earlier unlaunched attempt preserved. Stored-only audit PASS; owner recheck APPROVE_WITH_NOTES (same-family fallback). Scoped normal-hook bundle/fresh-fetch identities in the adjacent checks/DELIVERY_TRANSPORT.json. No C/S5/judging/registration/status change. | Codex | owner execution request; decision 0031 (night) |
| B4b | **v5 trace diagnostic** (60 fresh traced fights; descriptive) | **DONE** (`632811e`, `astelia_cpp/S4_V5_TRACE_DIAGNOSTIC.md`; Codex same-family recheck APPROVE_WITH_NOTES). The resonator's ranged phase is locked < 0.5% of the time (rotation 1.9 rad/s, half-cycle 1.64 s, against an 8.7 s commit→escape crossing); 24–27 large reversals per unit-minute against morale's 1–2; direct units spend 5.4% of time in gun bands (88% of their deaths) against 1.1%. Morale is stationary 92% of the time, and its hysteresis keeps escape. Against novice the same rotation removes 189/200 guns | Codex | decision 0031 (night) |
| B4c | **v6 design** (`DESIGN_0G.md` §18 + 18.1 + 18.2): an amplitude-and-phase (Stuart-Landau) resonator, damped at rest so the mode memory holds; μ added, ω_melee fixed (11 knobs); an RK4 substep and retry policy, a pressure envelope of 6,000 /s, an accuracy acceptance grid | **APPROVED** after three Codex rounds (`a8a5001` CHANGES_REQUIRED → 18.1; r2 CHANGES_REQUIRED → 18.2; **r3 APPROVE_WITH_NOTES** `54b9240`, low note N1 on fixture coverage passed to the implementer) | Claude drafts, Codex reviews | — |
| B4d | **v6 implementation, no-combat checks, and the development run** (A/B only; gates: novice > 0; progress > −6.025; beats regular > 0) | Implementation DONE (`83c0faf`): **10,763 numerical acceptance cases pass**, 37 integration tests pass, historical paths byte-identical. **Attempt 1 STOPPED after 0.45 s** (`fe5b5f2`): the historical cache validator rejected the new diagnostic field; 0 scored rows; preserved. Cache repaired (27 offline tests). **Attempt 2 RUNNING** (fresh entropy, about 03:00, about 65 min) | Codex | decision 0031 (night) |
| B5 | Update the replay viewer (`viz_0g/`) with v4/v5 fights | — | Claude | — |
| B6 | S5 registration (W4: CLOSED) | DECIDED: no registration until a development version beats regular; then register with morale as a labelled comparator | Claude drafts | **[OWNER] approves the registered run** |


**B3b owner recheck:** COMPLETE — the owner’s verbatim prompt was sent to independent reviewer `s16_report_recheck`; `evidence/tactical_composition_demo/astelia_cpp/s4_attribution_checks/OWNER_RECHECK.md` records its APPROVE_WITH_NOTES, reviewed report hash and findings. **T1 disposition:** timing bold formatting corrected. **T2 disposition:** Claude CLI returned "Not logged in"; disclose the Codex same-family fallback, not cross-family acceptance. **T3 disposition:** all endpoints, paired contrasts/interactions, source/raw hashes and eight complete representative traces independently matched; retain the eight-of-80 raw-tick recount limit. **T4 disposition:** the normal-hook commit and bundle/fresh-fetch identities are in the adjacent Part 2 delivery sidecar; raw seeds/replays/logs stay out of Git and every committed file is below 50 MB. No tuning, judging, registration, source/knob change or additional fight occurred. This completes development attribution, not v5/S5 or scientific acceptance.

**B4 v5 development owner recheck:** COMPLETE — the owner’s verbatim request was sent to separate Codex reviewer `v5_report_recheck`; Claude CLI returned Not logged in, so this is an explicitly disclosed same-family fallback, not scientific acceptance. `astelia_cpp/s4_v5_development_20261006_2308_checks/OWNER_RECHECK.md` records APPROVE_WITH_NOTES, original report SHA256 `d4d08abaca45598983ba79b8cc3e6495f9d889783bf573c861cae5993bf1282b` and final corrected report SHA256 `eaa3a5b43dfc77c868de51340516074f3e8882e820f7ce8c0652b9136b9507b7`. **R1 disposition:** pending review text replaced, family/hashes recorded; actual normal-hook commit and independent bundle/fresh-fetch verification recorded separately in DELIVERY_TRANSPORT.json. **R2 disposition:** literal outer caffeinate invocation added to LAUNCH.json. Reviewer independently confirmed every stored row, all 12 validation endpoints, tuning ordering/ties, comparisons, omegas, 109 pins and preserved prior files. No new fights/tests/audit rerun. Main .git is read-only; bundle carries only this task’s scoped changes, preserving other sessions’ dirty Track A/C plan edits.

## Track C: C6 option B (a faster C6 engine)

| # | Step | Status | Gate |
|---|---|---|---|
| C1 | Port, parallel and recheck | DONE (`evidence/c6_option_b/`) | — |
| C2 | Readiness timing | **The quiet-machine requirement is dropped** (the owner: the engine must work on the normal, busy laptop). The batch already shows the engine itself is too slow: the slowest world is 392 s wall, about 380 s per thread on CPU, against 360 s | — |
| C3 | **Speed up the C6 engine** | **DONE**: `8214f39` + fixes `ec82c43`; Codex round 2 **APPROVE_WITH_NOTES** (`e9757f9`); bit-exact; CPU −34%; the slowest world 152.6 s at normal load (needs about 1.4 cores per world) | Claude, Codex | — |
| C4 | **Round 2 (research done:** `evidence/c6_option_b/round2_research/`): the exact engine is near its floor (55% of time is libm). Only run-level dedup (−3%) and a partial Python port (5–8%) are worth doing; inexact vector maths (−26%, 0 decision flips) is NOT pursued (a tolerance is prepared). Low priority: the engine already has 2.4× headroom | **DECIDED: low-priority backlog** (dedup plus Codex's N1–N4 notes, when the machine is free) | Claude | — |
| C3b | If over 360 s: the owner decides the resource rule | **RESOLVED** by C3: the exact engine runs at 134–153 s at normal load | — |
| C5 | **Inexact-math impact study** (the owner asked: how much does it differ, how much does it change outcomes) | **DONE, current conclusion R3** (`932e98f`, `evidence/c6_option_b/inexact_study/INEXACT_IMPACT_REPORT_R3.md`): **NO_OBSERVED_CHANGE_WITHIN_ASSESSED_SCOPE**. In 10 stored worlds: 0 flips in 77,342 scalar decisions, 10,741 guards and composites, 1.14 M lock tests and 3.12 M link tests; every non-digest value and outcome identical; max deviation 3.3e-9 (grid monitors), 2.4e-10 elsewhere, all within the original 1e-8 bound; CPU about −25% (ratios 0.72–0.77, this machine, shared load). **Not assessed:** fine-grid pair decisions, trajectories, final-panel statistics; **future-panel risk is not quantified.** The R1 headline SAFE_UNDER_PROPOSED_TOLERANCE is withdrawn (kept as history). **Owner rechecks (Codex):** R1 CHANGES_REQUIRED (`428cac8`; F1–F6 fixed in R2), R2 CHANGES_REQUIRED (`3c92fc8`; R2-F1/F2 fixed in R3), **R3 APPROVE_WITH_NOTES** (`a6dfb26`; low notes N3 two guard preconditions, N4 the finite-value proof, open for any future analyzer revision; N5 this row, fixed). Costs of adoption: bit-identity with old receipts ends (new references), the macOS build must be pinned | Claude agent, Codex | **[OWNER] adopt the inexact engine or not** |

**C6 performance owner recheck:** COMPLETE — Codex reviewed Claude commit `8214f39` against the owner’s verbatim request, recorded in `docs/reviews/c6_option_b_perf_review_codex.md`. **F1 disposition:** FIXED in `ec82c43` (Codex round 2 APPROVE_WITH_NOTES); was: implementer must preserve successful earlier inner checks and first sequential error when recovery/causal jobs fail. This inherited seam is not repaired by the new task ordering. **F2–F4 disposition:** retained follow-up notes on optional-cache temporary allocations, publication timing and report rounding/ranges. A second Codex reviewer independently corroborated the static findings; supporting review is same-family, main review is cross-family against Claude. The same reviewer rechecked the completed review against the verbatim owner request and found no required corrections; all findings retained. No source, registered evidence, status or science change; no additional world beyond the one permitted smoke run.

**C6 queued-batch owner recheck:** COMPLETE — `evidence/c6_option_b/quiet_session_20261006_161801/OWNER_RECHECK_CODEX.md` records the verbatim owner request, reviewed report SHA256 and findings. No report, arithmetic, identity, preservation or bundle defect found. **Q1 disposition:** retain NOT_READY and observed timings; absence of scheduler confirmation and a renewed quiet gate before timing leaves verified quiet measurement unavailable. The owner decides any future measurement or resource-rule change; no passed jobs are repeated. **Q2 disposition:** record the available Codex reviewer as same-family; Claude addendum 2 and this recheck do not accept the new batch or milestone. Delivery bookkeeping labels the initial PAYLOAD snapshot and the final bundle is verified again after adding this review/disposition. Project code and STATUS.json remain unchanged.

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

- **C5: adopt the inexact (−25% CPU) C6 engine?** Evidence (R3, Codex APPROVE_WITH_NOTES): no observed decision or outcome change in 10 stored worlds; future-panel risk not quantified. Drafter's advice: not needed now (the exact engine meets the 360 s rule at normal load); adopt only if more speed is needed, with a decision record, new bit-exact references and a pinned macOS build.
- **A6s: approve changing O's pin from the fixed origin to a root-relative pin (C2)?** O is placed once, 1 m.u. from the centre toward the first driven root, then frozen; disclosed positional prior. Pilot evidence: both starts meet the F5 gate shape (i: A 1.04, B 1.27, E 0.8; ii: A 1.52, B 1.25, E 0.7). It keeps growth "from nothing". The seeded protocol (A) is no longer needed.

## How to resume after a context loss

1. Read this file, the tracker, and `git log --oneline -20`.
2. Check the running jobs: `ps aux | grep "codex exec"`. Their logs are in the session scratchpad (`*_last.txt`, `*.log`). If the scratchpad is gone, look at each step's report file named above. A report that has no final first line (READY / NOT_READY / STOP) means the job did not finish.
3. **Codex deliveries:** when Codex's `.git` is read-only, it leaves files in the workspace plus a bundle or tarball.
   - Verify that the workspace files equal the delivered ones.
   - Commit them with both `Assisted-by` trailers.
   - Ignore the bundles and tarballs; they are listed in `.gitignore`.
4. Continue with the first step that is not DONE and not waiting on **[OWNER]**.
