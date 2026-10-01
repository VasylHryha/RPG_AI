# C1 incremental-update receipt

Implementation: **REVIEW_READY**. Checks: **PASS**.

16 registered interventions; 13 committed, 3 explicitly unresolved and rolled back. Elapsed: 7.28s.

[Results](results.json), [per-case stream](instances.jsonl), [contracts](contracts.xml); exact before/after states in `states/` and source in `source/`.

| Nodes | Intervention | Update | Dynamic edge visits | Reference error |
|---:|---|---|---:|---:|
| 32 | consistent_edge | PASS | 457 | 1.4043333874306805e-15 |
| 32 | inconsistent_edge | PASS | 74305 | 5.597670464368681e-08 |
| 32 | new_node | PASS | 457 | 1.4043333874306805e-15 |
| 32 | bridge | PASS | 462 | 5.4930801582266845e-15 |
| 128 | consistent_edge | PASS | 2177 | 5.449153341501993e-12 |
| 128 | inconsistent_edge | NOT_CONVERGED | 100000 | 0.5900201436255176 |
| 128 | new_node | PASS | 2177 | 4.9043991718699166e-12 |
| 128 | bridge | PASS | 2183 | 2.3992326760345784e-12 |
| 512 | consistent_edge | PASS | 9477 | 9.87256383430977e-12 |
| 512 | inconsistent_edge | NOT_CONVERGED | 100000 | 0.6312833159629174 |
| 512 | new_node | PASS | 9477 | 1.573796346242743e-11 |
| 512 | bridge | PASS | 9483 | 1.1195343509771849e-11 |
| 2048 | consistent_edge | PASS | 39417 | 4.8661138618411116e-11 |
| 2048 | inconsistent_edge | NOT_CONVERGED | 100000 | 0.6593800267594657 |
| 2048 | new_node | PASS | 39417 | 3.5386695587121585e-11 |
| 2048 | bridge | PASS | 39423 | 5.665081191244732e-11 |

Unresolved updates preserve the preceding snapshot and are not counted as correct committed answers. Every accepted result is compared with fresh sparse least squares; the dense reference qualified that solver at small sizes in the contracts. Third disconnected components are retention controls; connected distant nodes are allowed to change.

Shared saved-state preparation, queue work, global proof scans, reference solves, query, load and persistence costs are reported. No full-solve fallback, sublinear computation, broad learning claim or hierarchy is implied. C1 acceptance is pending.
