# C1 R003 independent review handoff

> **Superseded by R004** (`evidence/c1_r004/`). Its author's self-recheck found that R003's per-update work was O(E log E) by construction: full-observation input, full re-preparation, global re-gauge, a global certificate and whole-snapshot hashing inside every update. That made its H-L result an artifact of the design. Its "0/36 faster than a fresh recompute" figure also compared a transaction that included persistence with an in-memory recompute that did not. R003 had no fallback arm and no registered endpoints. The R003 receipts below are unchanged historical evidence.

C1 R003 (`geomind-c1-r4-003`) is **REVIEW_READY**, not accepted. It repairs the findings in [CLAUDE_ACCEPTANCE.md](../c1_review/CLAUDE_ACCEPTANCE.md), which judged R002 CHANGES_REQUIRED. That reviewer also wrote this repair, so a different reviewer must decide R003 acceptance. R002 and R001 evidence is unchanged. All 12 accepted C0 inputs are unchanged.

## What changed from R002

- **Generator v3.** R001/R002 seeds only relabeled one fixed geometry per size/intervention; all 16 cells are identical up to relabeling. v3 draws grid widths, position jitter, consistent chord cycles, intervention endpoints and the contradiction vector per seed. The panel now has three worlds per size/intervention.
- **Algorithm/schema v3.** The update commits after one passing certificate of the quiescent workspace. R002 recomputed the same certificate ten times on unchanged coordinates, which was 97.4–99.98% of its dynamic visits in no-relaxation commits. Nodes flagged by a failed certificate take one forced step, so a local/global summation-order disagreement cannot burn the budget. R002 artifacts migrate explicitly through `_C1V2State`.
- **Evaluator/receipt.** A refused update's prior-state answers are reported as `prior_state_ok_answers` and `prior_state_answers_wrong_for_update`, never as coverage. Each case records `relaxation_node_updates` and `update_to_fresh_recompute_ratio`. The receipt counts commits without relaxation and commits faster than a fresh recompute.
- **Checks.** There are two new focused checks, twelve in total. They pin exact warm-start, local and certificate charging and the exhaustion point, reject removal of one duplicate copy, and migrate a real R002 artifact with identical answers. They also cover evaluator negative controls: a manufactured cross-component answer, a wrong unqueried relation caught only by the energy gate, and stale-coverage reporting. The custom-tolerance check now requires real relaxation steps.

## Reached evidence

```text
.venv/bin/python -m pytest -q tests/test_c1.py --junitxml=evidence/c1_r003/contracts.xml
.venv/bin/python -m geomind.run_c1 --output evidence/c1_r003 --contract-report evidence/c1_r003/contracts.xml
```

- Twelve checks PASS. The 48-case panel took 40.36 s, and all six gates PASS.
- 36/36 consistent-edge, new-node and bridge updates commit correctly: maximum displacement error `3.86e-11` and maximum energy gap `1.6e-20`. All 36 used **zero** relaxation steps, because the frame initialization alone placed them.
- 12/12 inconsistent-edge updates, at every size **including 32 nodes**, exhaust the 100,000-visit cap and keep byte-identical prior state. These are unresolved, not solved.
- 475/475 excluded cross-component pairs abstain. Retention, query immutability and reload pass everywhere.
- **0/36** commits were faster than a fresh recompute (2.6–17.9× slower). Dynamics take about 1–3 ms at 2,048 nodes. Each transaction also spends about 0.25 s on whole-state preparation, plus export, hashing and serialization.

H-P and H-L remain INCONCLUSIVE, and the H-L evidence in this panel is unfavorable. The residual-law queue resolved no contradiction under the cap on varied worlds.

## Smallest meaningful independent review batch

1. `pytest -q tests/test_c1.py --junitxml=<fresh dir>/contracts.xml` (twelve checks, about 2 s).
2. Read-only identity check of `evidence/c1_r003/`: `results.json` file hashes against live source and `source/`, and saved state hashes against `instances.jsonl`.
3. Optionally, `.venv/bin/python evidence/c1_claude_review/mutation_checks.py <scratch> --live`, which takes about 25 s and touches only the scratch copy.

Rerun the 48-case panel only after a source change, and only into a fresh directory.
