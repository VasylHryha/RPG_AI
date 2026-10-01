# Independent C0 acceptance handoff

Review the current candidate and its independent evaluator against `GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md`, especially C0 and the evidence contract. Decide **ACCEPTED** or return specific blocking findings. This is implementation acceptance only; no superiority, hierarchy or energy claim follows. C1 has not started.

The implementation author repaired the earlier issues. The repaired R003 code still needs independent acceptance. Initial and interrupted receipts are historical, not acceptance evidence.

## Exact current inputs

- `geomind/geometry.py`: snapshot owner, synchronous relaxation, gauge selection, stopping, load and transaction rules.
- `geomind/dataset.py`: exposed/hidden separation, relation catalogue, query construction and five world arms.
- `geomind/references.py`: BFS compilation, dense anchored least squares and direct-edge-only control.
- `geomind/run_c0.py`: observations before truth, independent residuals, qualification, costs, immutable source snapshot and streamed failures.
- `tests/test_c0.py`, `tests/test_review_contracts.py`: actual correctness, malformed-state and evaluator negative controls.
- `experiments/c0_manifest.json`: R003 frozen protocol; previous manifest copies retain R001/R002 identity.
- `evidence/c0_review/results.json`, `contracts.xml`, `instances.jsonl`, `source/`: actual R003 measurements, test results and executable source bytes.
- `evidence/c0_review/REVIEW.md`: prior audit findings and limitations; this is not a substitute for reviewing code.

At this handoff, R003 has all 11 gates PASS over 1,250 worlds, zero solver/infrastructure failures, 58 contract cases PASS in 8.60s and 331.50s world-evaluation time. Current source and archived source hashes match the receipt. No numerical code changed after those checks. Reuse the completed world evidence when it remains valid; do not repeat the five-minute experiment solely for a status/documentation edit.

## Review questions

1. Does `(i,j,d)` consistently mean `x_j-x_i=d`, with component-relative answers and no fabricated cross-component placement?
2. Are all candidate inputs exposed facts only, including the relation table? Are hidden edges really redundant and evaluated?
3. Are simultaneous updates, anchors, absolute/normalized force, failure status, rollback and freeze/load semantics correct?
4. Are compiled and least-squares numerics independent of candidate dynamics? Can evaluator negative controls detect incorrect and missing answers?
5. Does R003 evidence correspond to the reached code/protocol and retain costs, baselines, failures and coverage honestly?
6. Do any residual implementation defects block this bounded C0 experiment, as distinct from unsupported broader hypotheses?

If code repairs are necessary, identify and batch them before affected tests. Do not tune on inspected final worlds; material settings/protocol changes require a new experiment with fresh seeds. Preserve all existing receipts and unrelated workspace files. Do not start C1 or rewrite acceptance status until the review verdict is justified.

Suggested cheap verification, only if needed: `.venv/bin/python -m pytest -q`. Expensive replay is warranted only by affected numerical/data changes or an unreconciled evidence finding. Report exact commands, findings, implementation verdict and scientific limits separately.
