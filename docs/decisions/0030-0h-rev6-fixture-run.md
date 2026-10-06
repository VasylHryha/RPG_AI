# 0030: Owner approval of the 0h revision-6.5 engineering fixture run F1–F9

**Date:** 2026-10-06
**Owner's words:** "yes", in answer to: "Yes, run the 0h engineering tests F1–F9. About 2–6 minutes, no full training."

## What is approved

- **One execution of fixtures F1–F9** exactly as specified in `evidence/tactical_composition_demo/DESIGN_0H_REV6.md`: revision 6.5, sections 14.3–14.5, 16.1, 18.1, 18.6, 19.2, 19.7 and 19.8. It uses the integration at commit `855d931` (READY_FOR_FIXTURES; Claude's review and short check in `growing_shapes_review_claude/REV6_INTEGRATION_REVIEW.md`).
- **Entropy:** the `rev6_fixture` world episodes and the fixture seed keys of 16.2 and 18.1 only.
- **Resources:** the projected cost is about 2–6 minutes serial, under `caffeinate -i -s`. Awake and elapsed time are both reported.

## What is not approved

- training;
- the development run (48 trainings);
- evaluation panels (validation 512–767);
- judging entropy;
- any registration;
- any change to the recorded 5.1 verdicts.

The development run needs its own approval, after the fixture results and the measured cost projection (plan step A7).

## Stop rows that apply

`DESIGN_0H_REV6.md` 12.8, 14.9 and 16.3:
- a failure of F1–F4 blocks F5;
- a failure of F5 blocks development and sends the design back to the drafter;
- a measurement failure is INVALID.
