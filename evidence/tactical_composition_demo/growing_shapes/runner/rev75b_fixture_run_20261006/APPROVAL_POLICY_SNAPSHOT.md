# 0031: The owner's run-approval policy and the ratification of the decision-0028 [R] items

**Date:** 2026-10-06
**Owner's words:** "ratify all [R] ok, so issue here then you just ask or tell I need it; if it is something that takes more than 1 hour you should ask; after 22:00 you can run all you need without restrictions, I mean tests and long tasks."

## 1. Ratification

The owner ratifies **all [R] items** of decision 0028, items 1–18, including:
- item 8: the approval of the recorded 0d run;
- item 10's literal-wording note.

These are now owner-confirmed readings.

## 2. Standing approval policy (from now on)

| Work | Approval |
|---|---|
| **Runs and tests under 1 hour** (fixtures, smoke runs, development checks, test suites, diagnostics) | **No need to ask.** Claude runs them and reports. |
| **Runs over 1 hour, started before 22:00** | **Ask first,** stating the expected duration. |
| **Any run started 22:00 or later** (tests and long tasks) | **No restrictions:** Claude runs what the plan needs. |

**Still kept by the project rules:**
- a **registered one-shot "final exam"** run (judging entropy, a registered specification) is announced to the owner before it runs, because it cannot be redone;
- frozen files and receipts stay untouched;
- every run uses `caffeinate`, keeps raw logs out of git and reports both awake and elapsed time.
