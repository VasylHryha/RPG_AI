# C1 incremental-update receipt

Implementation: **REVIEW_READY**. Checks: **PASS**.

16 registered interventions; 5 committed, 11 explicitly unresolved and rolled back. Elapsed: 24.76s.

[Results](results.json), [per-case stream](instances.jsonl), [contracts](contracts.xml); exact before/after states in `states/` and source in `source/`.

| Nodes | Intervention | Update | Dynamic edge visits | Reference error |
|---:|---|---|---:|---:|
| 32 | consistent_edge | PASS | 456 | 9.930136612989092e-16 |
| 32 | inconsistent_edge | PASS | 97178 | 5.354147576288634e-08 |
| 32 | new_node | NOT_CONVERGED | 99998 | 1.3773047751714558e-15 |
| 32 | bridge | NOT_CONVERGED | 99999 | 5.347542221830668e-15 |
| 128 | consistent_edge | PASS | 2176 | 2.7584239772488078e-12 |
| 128 | inconsistent_edge | NOT_CONVERGED | 99998 | 0.5900201436249147 |
| 128 | new_node | NOT_CONVERGED | 99998 | 3.3754878467861866e-12 |
| 128 | bridge | NOT_CONVERGED | 100000 | 9.528792879521127e-12 |
| 512 | consistent_edge | PASS | 9476 | 1.2285427330181073e-11 |
| 512 | inconsistent_edge | NOT_CONVERGED | 99998 | 0.6312833159631327 |
| 512 | new_node | NOT_CONVERGED | 99998 | 1.88969916146552e-11 |
| 512 | bridge | NOT_CONVERGED | 99998 | 9.587425073620893e-12 |
| 2048 | consistent_edge | PASS | 39416 | 3.013172824201419e-11 |
| 2048 | inconsistent_edge | NOT_CONVERGED | 99996 | 0.6593800267616572 |
| 2048 | new_node | NOT_CONVERGED | 100000 | 3.166435724743072e-11 |
| 2048 | bridge | NOT_CONVERGED | 99994 | 2.272277480856073e-11 |

Unresolved updates preserve the preceding snapshot and are not counted as correct committed answers. Every accepted result is compared with fresh sparse least squares; the dense reference qualified that solver at small sizes in the contracts. Third disconnected components are retention controls; connected distant nodes are allowed to change.

Shared saved-state preparation, queue work, global proof scans, reference solves, query, load and persistence costs are reported. No full-solve fallback, sublinear computation, broad learning claim or hierarchy is implied. C1 acceptance is pending.
