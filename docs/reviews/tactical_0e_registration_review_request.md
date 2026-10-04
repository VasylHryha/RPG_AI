# Review request: experiment 0e registration (for Codex; paste the block below)

```
You are the cross-family reviewer (Codex) named by AGENTS.md for a registered exploratory experiment in /Users/new/RiderProjects/ai_RPG_test
(registration commit 9583017; check HEAD). Read AGENTS.md first. Time cap about 20 minutes.
RULES: read-only except the single review file named below. Do NOT run ze_run.py --run (the recorded run needs the owner's approval
after your review); do not run dev_0e scripts. You MAY run once: .venv/bin/python -m pytest -q -p no:cacheprovider
evidence/tactical_composition_demo/test_ze.py evidence/tactical_composition_demo/test_ze_run.py. No numeric quality scores.

READ: evidence/tactical_composition_demo/{SPECIFICATION_0E.md, PROPOSAL_0E.md (section 12), ze_run.py, ze_core.py, ze_flat.py,
tactics_e2.py, test_ze.py, test_ze_run.py, SPEC_0E.json}, dev_0e/README.md and its step*_results.json, docs/reviews/tactical_0e_plan_review_gpt.md
(the plan review this design answers), docs/decisions/0028-*.md items 8-9.

CHECK, in order:
1. Does ze_run.evaluate implement SPECIFICATION_0E.md section 4 exactly (gates, every component and threshold, strict inequalities,
   negative witnesses at alpha/m, the scale-fault rule relative to the teacher, the B1 normalized ratio bounds, the B3 gate)? Find any input
   where a claim could be SUPPORTED and REFUTED at once, or where a gate is recorded but not enforced.
2. Are the exact intervals right (ze_core.median_interval, clopper_pearson, quantile_bounds, iqr_bounds, ratio_bounds)? Check against known
   values; check the order-statistic index choice and the tail errors.
3. Wire and assemblies (ze_core.Wire, Assembly, play_cell): does each cut/fault do what the contract says; are episode rosters truly paired across
   policies; is the attack target kept while only the MOVE message is faulted; can fault draws perturb the world stream?
4. The task revision: tactics_e2.py V3 and its selection (dev_0e step 4). Was the rule fixed before measurement as claimed (git history)? Does
   V3 make the connection matter for a legitimate reason, or does it favour the pieces? Is the change from the proposal disclosed adequately?
5. Baselines: is the per-slot policy fairly named and fairly tuned; is Fflat's search adequate for the "no flat network qualifies" statement;
   are J and L recipes (from 0d) acceptable without V3 re-tuning?
6. Leakage and provenance: train/test split, standardizers, nested streams (stream keys), saved weights, FILES list vs everything the run
   depends on, smoke consistency.
7. Anything that should block the recorded run versus things to report.
OUTPUT: write ONLY docs/reviews/tactical_0e_registration_review_codex.md. First line one of APPROVE_WITH_NOTES / CHANGES_REQUIRED / REJECT;
second line "Reviewer family: Codex"; third line "HEAD: <git rev-parse HEAD>". Then required changes (file:line, fix), notes, what you
could not verify.
```
