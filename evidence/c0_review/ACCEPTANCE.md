# Independent C0 implementation acceptance

Verdict: **ACCEPTED**. Reviewer: separate `/root/c0_acceptance` agent, 1 October 2026. Scope: the repaired `geomind-c0-r4-003` implementation and evaluator against the C0 and evidence requirements in `GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md`. No blocking defect found. This satisfies C1's accepted-C0 prerequisite.

This review did not change numerical code, generators, tests, manifests or authoritative status documents. It reused the completed R003 world experiment after checking its identity. The acceptance applies to the exact C0 source below, not to later added implementations or broader research claims.

## Exact identity

- Canonical experiment-manifest SHA256: `3372cbc15b65728180606d94d8380d14a334bdb4fb3a2c280d53fb482d28a249`.
- Manifest file SHA256: `e098d5f7aa79ada9de8f1ae3716da39fa245c305ed01d74e199071f3e75236a4`.
- Original `results.json` SHA256 at review: `9e668784d62f7e1ee069abbae172a8263ee8adc5dcb33c67934a8ac3cb5ffd5f`.
- Original `instances.jsonl` SHA256: `b6f0308499c3acc0cbc8423509c30c83c390eee105acc3fa639f2f56386f6451`.
- Original 58-case `contracts.xml` SHA256: `a55b38412cf055cdb24ae370efde397f4fe14e35a982406c2f7b9012c81613ce`.
- Source commit: none; the experiment uses archived source bytes and SHA256 identities. Current source, archived source, and before/after execution hash maps matched for all 12 registered inputs at review.

| Registered source | SHA256 |
|---|---|
| `geomind/geometry.py` | `973740d321705d9c8633a6cd2da1696af91cec930e53bcb6b6b4831e280066f0` |
| `geomind/dataset.py` | `003fa18f0519bdb177f4594b1565ca91006b8fad8c0b4ca3d1e450ac2927b48e` |
| `geomind/references.py` | `771f9b355083240fa2bf1a5e713bb1f964f9fd493d7e485aa2d4ba1f5e5255f9` |
| `geomind/run_c0.py` | `75708d230390bac8297c8f3a9ebfbf910b37d5d9b688f13989e27b98ba84f0ea` |
| `geomind/__init__.py` | `c68e2354ec176b189254b853c52029546321c6fbe5b85ac554e38986adc43039` |
| `tests/test_c0.py` | `915d8e8fd05b140e775ca164705eb0304353de4d1307a30ff72edf8630763e99` |
| `tests/test_review_contracts.py` | `6afd2fe61c2a1e54018e475443b1e373587ee61306501128de802b357767205e` |
| `experiments/c0_manifest.json` | `e098d5f7aa79ada9de8f1ae3716da39fa245c305ed01d74e199071f3e75236a4` |
| `experiments/c0_r4_001_manifest.json` | `b9f3fdbc52d2c6c0688196517abcfe365e5f0036766cd7f19341ee2976bae995` |
| `experiments/c0_r4_002_manifest.json` | `4c707247b0b71ed35eb52facf95565a4ff8ccf6211e88c3d58257b46732ec05f` |
| `pyproject.toml` | `b13af15c4b02a76b429da4d76965cddf66f73d59198bca80d01fab7b51c705e2` |
| `uv.lock` | `284881c4c71c8282aca81e9053794d2b0333f9ab10b21d9e425cba13bec918c8` |

## Findings and actual checks

Read the handoff, R4 C0/evidence contracts, candidate, generator, all three references, evaluator and both test files. The candidate's numerical dynamics use only typed public observations. `(i,j,d)` consistently means `x_j-x_i=d`; gradients use the same old coordinate state. Gauge fixing follows exposed connectivity and degree. Query answers subtract committed coordinates, with cross-component abstention. The convergence guard requires absolute and degree-normalized force plus update tolerance; nonconvergence and malformed updates leave prior committed state intact. Serialized load validates structure, connectivity, gauge and stationarity in addition to checksum. Query/freeze/load and rollback contracts are represented by concrete fixtures and final-world checks.

The generator exposes a spanning tree in every component and hides redundant edges, includes all eight hidden edges in the indirect query panel, keeps supplied pairs out of that panel, permutes IDs, and sends only exposed vectors in its public relation catalogue. The evaluator fixes predictions before truth comparisons, separately reports noisy truth and least-squares agreement, computes residual energy from committed answers, and measures direct-only abstention as lost total accuracy. BFS coordinates and union-find/dense least squares share public value types and validation, but do not share candidate gradient, component discovery, anchor selection or relaxation numerics. Hand-derived triangle and weighted contradiction fixtures additionally check the numerical convention independently of those references.

Ran one focused reviewer command, preserving the original 58-case report:

```text
.venv/bin/python -m pytest -q tests/test_c0.py::test_triangle_independent_reference_and_residual tests/test_c0.py::test_failure_preserves_previous_transaction_and_no_false_convergence tests/test_review_contracts.py::test_weighted_inconsistent_case_against_hand_solution tests/test_review_contracts.py::test_weak_weights_cannot_fake_equilibrium_with_wrong_coordinates tests/test_review_contracts.py::test_evaluator_rejects_wrong_candidate_even_if_trace_says_pass tests/test_review_contracts.py::test_qualification_handles_solver_success_with_no_answers --junitxml=/private/tmp/geomind-c0-acceptance-focused.xml
```

Result: **7 cases PASS in 0.96 seconds**. Durable copy: `acceptance_contracts.xml`. The selected cases check analytically known equilibria/contradictions, transaction rollback, tiny-weight false convergence, and evaluator rejection of wrong or missing answers.

Also ran a read-only Python integrity check importing `digest`, `qualification_gates` and `contract_result`: independently hashed all current and archived registered files; compared receipt manifest to the live manifest; verified the canonical manifest hash; compared the 1,250 streamed rows exactly to the receipt's instances; checked unique identities and every seed's registered split/arm range; recomputed the nine world qualification gates; parsed and hashed the original contract report; and confirmed all 11 original gates PASS. No world was regenerated or re-solved during this integrity check.

Verified results: **1,250 worlds**, zero solver/infrastructure failures, all 11 gates PASS; **4,000/4,000** cross-component queries abstained; maximum candidate-versus-least-squares indirect displacement error **1.198606e-7**; maximum independently measured energy gap **8.241359e-15**. The original report contains **58 PASS, zero failures/errors/skips**. Original measured world evaluation time is **331.5025 seconds**; this review did not rerun it.

## Limits and next action

No claim of superior computation, learning, recursive hierarchy, tactical utility, production readiness or hardware energy is accepted here. The retained matched compiled baseline explains clean reconstruction more cheaply; for example, the recorded test/lattice paired candidate-minus-compiled fit/query time is approximately +0.0902 seconds per world. That is a valid reference-experiment limitation and supplies no novel mechanism claim. Reported workspace/storage figures do not establish peak process memory, and world bootstrap intervals do not prove zero failure probability or out-of-family generalization.

No additional C0 experiment or implementation repair is required for this verdict. Proceed to C1 under its own registered implementation, metered costs, rollback and independent-reference checks. Preserve the original R003 receipt as historical `REVIEW_READY` execution evidence; this separate acceptance record establishes the later review decision.
