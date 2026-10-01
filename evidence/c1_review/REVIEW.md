# C1 recheck and repairs

Current implementation: **R002 REVIEW_READY**, checks **PASS**, independent acceptance **pending**. This is the implementation owner's recheck and repair record, not independent acceptance. The [R4 standard](../../GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md) remains authoritative.

The earlier implementation safely refused most updates, but did avoidable work and had gaps in stopping and evidence qualification. The review produced these repairs:

| Finding | Repair and evidence |
|---|---|
| Arbitrary new-node/component frames wasted relaxation work | Existing components become rigid frames and new nodes singleton frames. Added public constraints initialize their translations through a deterministic spanning tree. Internal answers survive frame changes. Every initialization edge read shares the same dynamic cap; translations and global preparation remain charged overhead. All eight new-node/bridge cases now commit through 2,048 nodes. |
| Custom update tolerances were ignored | Both active-node quiet checks and final certificates enforce force, normalized force and implied step tolerance. C1 artifact load enforces the step bound too. A stricter-tolerance solve passes; a checksummed perturbation below the force tolerance but above the step tolerance is rejected. |
| BLAS norm overflow could bypass NumPy exception handling | Explicit finite scalar/vector norm guards now reject arithmetic overflow with retained state and charged reads. This was exposed by the initial focused checks; their report and exact source remain in `../c1_review_prechecks/`. |
| Nonfinite or malformed query answers could corrupt evidence or hide behind max-error aggregation | Typed finite 2D answers are required, every identifiable answer must have a finite qualified error, and incorrect, missing, NaN, huge, Boolean and malformed answers fail evaluation without nonfinite JSON. Candidate answers are fixed before fresh reference construction. |
| A stale, unrelated or incomplete passing test report could qualify the run | The actual complete C1 report carries its scope and exact source/manifest hashes. The runner checks every expected case, provenance and before/after report identity. C0's acceptance is bound to the separately reviewed result and its original source hashes. |
| Partial output could be overwritten and aborted records could disappear on JSON serialization | Output directories must be fresh except for their actual test report. External reports are copied with checked identities. Nonserializable case evidence becomes a retained infrastructure failure. Both successful and rejected transactions retain initial C0, fork-before and after artifacts. |
| Missing chained, duplicate, cyclic and excluded-component checks | Ten focused checks cover persisted update chains, reverse bridge direction, parallel constraints, duplicate removal rejection, cyclic contradictions, frozen parent/sibling isolation and explicit historical C1 migration. The final panel adds unrelated cross-component negatives. Tiny-weight reference checks prevent false sparse-reference convergence. |

Final commands:

```text
.venv/bin/python -m pytest -q tests/test_c1.py --junitxml=evidence/c1_review/contracts.xml
.venv/bin/python -m geomind.run_c1 --output evidence/c1_review --contract-report evidence/c1_review/contracts.xml
```

Ten focused checks PASS in **1.42 seconds**. R002 runs the same four intervention types at 32/128/512/2048 nodes, with fresh seeds starting at 8,000,000, unchanged Float64 residual dynamics and the unchanged **100,000 dynamic edge-visit cap**. No relaxation setting was tuned after inspecting final cases. The 16-case evaluation took **7.28 seconds**. All six engineering gates pass; all fresh independent least-squares references converge.

**Thirteen commits are correct:** all consistent-edge, new-node and bridge updates, plus the 32-node inconsistent edge. Maximum committed displacement error is `5.59767e-8`, and maximum independently measured energy gap is `3.46945e-15`. All **159** excluded cross-component queries abstain. Retention, query immutability and reload checks pass in every case.

**Three updates remain unresolved:** inconsistent edges at 128, 512 and 2,048 nodes exhaust the cap. Their previous fork snapshots are byte-identical after rejection. These refusals satisfy the transaction contract and are not correct updated answers. A faster language would reduce time per operation without resolving the edge-visit limit by itself. The reference solves all three, so this queue is not established as the best general numerical update method. Changing the relaxation mechanism or adding a separately metered fallback would require another declared experiment.

R001's five commits/11 refusals and 24.76-second run are retained in `../c1/`; its archived source and per-case stream were checked unchanged. R002 has different seeds and additional negative queries, so the two durations are recorded observations, not a paired speed benchmark. All 12 independently accepted C0 inputs remain unchanged. No C0 world experiment was repeated.

Post-run [INTEGRITY.json](INTEGRITY.json) checks all sixteen registered identities, the complete source-bound report, accepted C0 identity, current and archived source hashes, each fork/after hash, saved query answers, additive constraint preservation, dynamic visit arithmetic and proof of budget exhaustion. It independently recomputes residual energy from the committed artifacts and verifies historical source/stream preservation. This inspection loads saved artifacts; it does not run another relaxation experiment.

H-P and H-L remain **INCONCLUSIVE**: the panel does not compare adaptive versus frozen task learning, establish computational locality, prove generalization or measure energy. Numeric workspace bytes cover selected arrays, not peak memory. Preparation and certification still perform global work. One world per intervention and size is bounded evidence.

Next gate: independent C1 review of correctness, cost accounting, evaluator controls and the three unresolved cases. C2 and recursive hierarchy remain unimplemented. Current evidence/source is exact and reviewable; a numerical 9/10 or 10/10 quality rating would be subjective and is not established by passing these checks.
