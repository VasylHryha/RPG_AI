# Request to Codex: session S3, the controllers on the S2 plug (build only; no tuning, no experiment)

Repository `/Users/new/RiderProjects/ai_RPG_test`. Read `AGENTS.md`.
- **Approval:** the owner approved this session and assigned it to Codex (2026-10-05). Exploratory, under decision 0028. Commit with `Assisted-by: Codex:<model>`.
- **The contract:** `../DESIGN_0G.md` **revision 2** (commit `3a29450`), sections 1-4, 7 and 8. It answers your design review `docs/reviews/tactical_0g_design_review_codex.md`.
- **If the design is wrong or ambiguous anywhere,** stop and write it in the report. Do not choose silently.

## Build

1. **Plug extensions** (design section 8): per-unit cross-team damage counters (dealt to and taken from the other team) and friendly-fire counters in `World::damage`; `minRange`
   in `ObservedUnit`; a per-side `controllerFailures` count in the summary; a runner-level refusal of `passthrough` outside tests. Behaviour-neutral: the 80 reference requests
   and the S2 passthrough fixtures stay byte-identical.
2. **Three controllers** registered by name, each accepting its knobs as `params`:
   - `resonator` (10 knobs);
   - `morale` (10 knobs);
   - `pushpull` (2 knobs).

   They implement exactly design sections 2-4: the damage-rate recurrence, the shared movement law, the action rule, targets computed in `prepare` from the previous tick's assignments,
   hysteresis, the degenerate cases and failure reporting. Unknown or out-of-bounds params are rejected, with bounds from design section 5. `nearest` stays as built.
3. **The group diagnostics** of design section 7, written per fight on request (`diagnostics:true`) as one JSON line per second. They never feed back into the controller.

## Acceptance

Every check in design section 8 passes:
- the C4 reference to 1e-9 (`../c4_reference/c4_reference_states.json`);
- the enemy-term sign;
- the damage recurrence;
- independence from the order of `decide` calls;
- the degenerate cases;
- failure reporting;
- clone memory and parent isolation;
- determinism;
- the cost per fight against `nearest`;
- 38 failure-free fights per arm with default knobs (choose them mid-range and state them);
- step refinement.

Also:
- the existing test suite passes once, at the end of the batch;
- no tuning, no development fights beyond these checks, no recorded run.

## Report

`S3_CONTROLLERS_REPORT.md`: the first line `READY` or `NOT_READY`, then the check results, the default knobs used, every deviation and every design question raised. Claude reviews it.
