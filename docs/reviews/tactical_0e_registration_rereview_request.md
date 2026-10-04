# Re-review request: experiment 0e registration corrections (for Codex; paste the block below)

```
You are the cross-family reviewer (Codex) who reviewed the 0e registration (docs/reviews/tactical_0e_registration_review_codex.md,
CHANGES_REQUIRED, R1-R5). The drafter's corrections are in commit bb5ff7f (plus the new smoke record after it); check HEAD.
Repository /Users/new/RiderProjects/ai_RPG_test. Read AGENTS.md first. Time cap about 15 minutes.
RULES: read-only except the single review file named below. Do NOT run ze_run.py --run; do not run dev_0e scripts. You MAY run once:
.venv/bin/python -m pytest -q -p no:cacheprovider evidence/tactical_composition_demo/test_ze.py evidence/tactical_composition_demo/test_ze_run.py
No numeric quality scores.

For EACH of your findings R1-R5 and your notes, verify against `git diff 4a8e792 bb5ff7f` whether it is resolved, partly resolved or not:
R1 (B1 normalized negative witness at error/m; the regression test_r1_* adapted to the corrected per-claim error 0.01),
R2 (gate-to-claim map in evaluate() and SPECIFICATION_0E.md section 4; AIM/MOVE necessity as diagnostics only),
R3 (ze_core.validate_choice / validate_vectors on assemblies, joint3 and ze_run.flat_policy; tests for dead, negative, non-integer
    identities, non-finite steps, empty snapshots),
R4 (SPECIFICATION_0E.md section 1 and 6, dev_0e/README.md, tactics_e2.py, PROPOSAL_0E.md section 13: timing as the author's account,
    the real flat search extent, the corrected +0.042 figure),
R5 (claim A split into A1 and A2; A2 gated on JJ beating rush; five claims at 0.01; SPEC_0E.json alpha changed before any run).
Also check the notes you raised (exact-equality test, FILES includes tcd_common/metrics.py, IQR descriptive values, FpO/OFp naming,
Fp label accounting, deferred items listed). Look for anything the corrections broke or introduced (for example the alpha change and
the order-statistic ranks at 0.01, the SPEC_0E.json edit, the renamed pre-review smoke directory).
OUTPUT: write ONLY docs/reviews/tactical_0e_registration_rereview_codex.md. First line one of APPROVE_WITH_NOTES / CHANGES_REQUIRED /
REJECT; second line "Reviewer family: Codex"; third line "HEAD: <git rev-parse HEAD>". Then one line per finding (resolved / not, with
file:line), anything new, and what you could not verify.
```
