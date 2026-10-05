READY

Codex implementer report, 2026-10-05. Revision-4 runner changes pass the final test-file run and are ready for independent runner review. READY concerns implementation readiness for review, not S6 execution authorization or experimental acceptance. This exploratory decision 0028 work changes no milestone status.

Governing registration: `../SPEC_0G.json`, revision 4, SHA256 `158031e9e90b9cc86feb840eca81917ca4913416bb683be6172434a64f7c8335`. The specification and companion `../SPECIFICATION_0G.md` were read and left unchanged.

Implemented in this revision:

- Only revision 4 is admitted. The review file comes from `gates.codex_review`, taking the path before its colon-delimited rule, relative to the repository root. No revision-specific review filename is inferred. Its first line must be APPROVE or APPROVE_WITH_NOTES and its text must name the exact specification digest.
- The manifest comes directly from the literal `engine.build_manifest` path, relative to the specification directory. No filename is inferred or explanatory prose removed. Its digest must equal `engine.build_manifest_sha256`; the binary digest must equal `engine.binary_sha256`; the manifest's `binary_sha256` must equal that admitted binary digest. `engine.manifest_rule` describes these enforced checks.
- The fake fixture retains revision 4's registered review and manifest paths instead of correcting either field. Regression checks relocate each registered path and verify that a valid alternate file cannot substitute when the named file is absent. Missing path fields refuse before seed derivation or output creation. Revision 3's malformed manifest path remains a synthetic negative case. Existing digest-mismatch and manifest-to-binary binding negatives remain.

Existing request construction, endpoint dependency/failure rules, exact alpha allocations, t bounds, registered host timeouts, whole-batch failure attribution, atomic output latch, pre-dispatch identity/schedule, durable attempt/return journals, and interruption coverage remain enforced.

Tests: **177 passed in 15.50 s**, measured wall time **15.67 s**. Ran `.venv/bin/python -m pytest -q evidence/tactical_composition_demo/astelia_cpp/test_s6_run.py` exactly once after the complete code/test batch, timed with `/usr/bin/time -p`. No code or test edits followed. The autouse guards permit seed derivation only from `000102030405060708090a0b0c0d0e0f` and subprocess launches only of the synthetic executable in pytest's fake repository. Full registered accounting uses synthetic integers without judging-seed derivation; subprocess integration uses small fake panels.

Remaining questions: none for the drafter concerning the two revision-3 path defects; revision 4 resolves both. During this task, the concurrent `docs/reviews/tactical_0g_spec_review_codex_r4.md` appeared with first line APPROVE_WITH_NOTES and the exact revision-4 spec digest. It was read and left outside this task's commit; that specification review does not accept this runner. Independent runner review remains, as do explicit owner delta/n approval and S6 authorization recorded in the registered authorization file. The real authorization file remains absent. This implementation report supplies no owner approval or authorization.

Scope: only `s6_run.py`, `test_s6_run.py` and this report. No real engine was launched, real judging seed derived, real fight run, real `astelia_cpp/s6_run` directory created or real `S6_AUTHORIZATION.json` written. Synthetic gate records and run outputs exist only inside pytest's temporary fake repositories. The next step is independent runner review and the remaining recorded execution gates.
