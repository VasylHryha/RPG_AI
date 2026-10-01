# C1 incremental-update receipt

Implementation: **REVIEW_READY**. Checks: **PASS**.

48 registered interventions; 36 committed (36 without any relaxation step), 12 explicitly unresolved and rolled back. 0 commits were faster than a fresh recompute. Elapsed: 40.36s.

[Results](results.json), [per-case stream](instances.jsonl), [contracts](contracts.xml); exact before/after states in `states/` and source in `source/`.

| Nodes | Intervention | World | Update | Relaxation steps | Dynamic edge visits | Update / fresh recompute | Reference error |
|---:|---|---:|---|---:|---:|---:|---:|
| 32 | consistent_edge | 0 | PASS | 0 | 57 | 5.27 | 1.6011864169946884e-15 |
| 32 | inconsistent_edge | 0 | NOT_CONVERGED | 16666 | 100000 | 137.43 | not committed |
| 32 | new_node | 0 | PASS | 0 | 55 | 6.82 | 5.4025784115714076e-15 |
| 32 | bridge | 0 | PASS | 0 | 59 | 7.91 | 2.1316282072803006e-14 |
| 32 | consistent_edge | 1 | PASS | 0 | 59 | 6.37 | 2.010699415441723e-15 |
| 32 | inconsistent_edge | 1 | NOT_CONVERGED | 15955 | 100000 | 443.91 | not committed |
| 32 | new_node | 1 | PASS | 0 | 53 | 6.01 | 2.960883838797243e-15 |
| 32 | bridge | 1 | PASS | 0 | 62 | 6.38 | 1.0805156823142815e-14 |
| 32 | consistent_edge | 2 | PASS | 0 | 56 | 6.47 | 1.6011864169946884e-15 |
| 32 | inconsistent_edge | 2 | NOT_CONVERGED | 16662 | 100000 | 83.38 | not committed |
| 32 | new_node | 2 | PASS | 0 | 53 | 6.26 | 6.2803698347351005e-15 |
| 32 | bridge | 2 | PASS | 0 | 60 | 6.41 | 2.1334777765716796e-14 |
| 128 | consistent_edge | 0 | PASS | 0 | 239 | 7.22 | 5.3243649438361604e-12 |
| 128 | inconsistent_edge | 0 | NOT_CONVERGED | 13819 | 100000 | 147.94 | not committed |
| 128 | new_node | 0 | PASS | 0 | 239 | 17.60 | 6.5949243492052935e-12 |
| 128 | bridge | 0 | PASS | 0 | 244 | 2.60 | 6.028998083210939e-12 |
| 128 | consistent_edge | 1 | PASS | 0 | 236 | 6.26 | 7.330524776334487e-12 |
| 128 | inconsistent_edge | 1 | NOT_CONVERGED | 13454 | 100000 | 19.10 | not committed |
| 128 | new_node | 1 | PASS | 0 | 228 | 12.50 | 5.644492303034239e-12 |
| 128 | bridge | 1 | PASS | 0 | 249 | 17.93 | 8.01730012319535e-12 |
| 128 | consistent_edge | 2 | PASS | 0 | 241 | 6.66 | 1.144075075187226e-11 |
| 128 | inconsistent_edge | 2 | NOT_CONVERGED | 13751 | 100000 | 155.12 | not committed |
| 128 | new_node | 2 | PASS | 0 | 240 | 8.95 | 6.252045114112094e-12 |
| 128 | bridge | 2 | PASS | 0 | 245 | 8.36 | 6.066262507773528e-12 |
| 512 | consistent_edge | 0 | PASS | 0 | 1016 | 13.20 | 2.537162192307124e-11 |
| 512 | inconsistent_edge | 0 | NOT_CONVERGED | 12522 | 100000 | 21.48 | not committed |
| 512 | new_node | 0 | PASS | 0 | 1006 | 3.85 | 2.000019222788726e-11 |
| 512 | bridge | 0 | PASS | 0 | 1018 | 6.24 | 1.4237570545656614e-11 |
| 512 | consistent_edge | 1 | PASS | 0 | 1004 | 7.76 | 1.242602036809999e-11 |
| 512 | inconsistent_edge | 1 | NOT_CONVERGED | 12518 | 100000 | 16.95 | not committed |
| 512 | new_node | 1 | PASS | 0 | 1008 | 3.18 | 1.2277503398979054e-11 |
| 512 | bridge | 1 | PASS | 0 | 1021 | 11.29 | 1.1561803286798539e-11 |
| 512 | consistent_edge | 2 | PASS | 0 | 1013 | 6.95 | 2.248310229577112e-11 |
| 512 | inconsistent_edge | 2 | NOT_CONVERGED | 12629 | 100000 | 28.81 | not committed |
| 512 | new_node | 2 | PASS | 0 | 1006 | 8.75 | 9.599099043459214e-12 |
| 512 | bridge | 2 | PASS | 0 | 1026 | 4.85 | 1.7191853894557935e-11 |
| 2048 | consistent_edge | 0 | PASS | 0 | 4178 | 6.38 | 1.4649928788370752e-11 |
| 2048 | inconsistent_edge | 0 | NOT_CONVERGED | 11978 | 100000 | 10.80 | not committed |
| 2048 | new_node | 0 | PASS | 0 | 4188 | 7.32 | 1.8838791486452342e-11 |
| 2048 | bridge | 0 | PASS | 0 | 4198 | 8.76 | 3.308597491743633e-11 |
| 2048 | consistent_edge | 1 | PASS | 0 | 4203 | 7.55 | 2.3504163541545404e-11 |
| 2048 | inconsistent_edge | 1 | NOT_CONVERGED | 11890 | 100000 | 8.34 | not committed |
| 2048 | new_node | 1 | PASS | 0 | 4181 | 7.60 | 1.977935850971835e-11 |
| 2048 | bridge | 1 | PASS | 0 | 4212 | 5.96 | 3.855902897381691e-11 |
| 2048 | consistent_edge | 2 | PASS | 0 | 4193 | 7.15 | 2.2690128512271478e-11 |
| 2048 | inconsistent_edge | 2 | NOT_CONVERGED | 11941 | 100000 | 10.15 | not committed |
| 2048 | new_node | 2 | PASS | 0 | 4199 | 6.73 | 3.155825327354964e-11 |
| 2048 | bridge | 2 | PASS | 0 | 4199 | 6.48 | 2.1940990827409057e-11 |

Unresolved updates preserve the preceding snapshot and are not counted as correct committed answers; their prior-state answers are counted separately and never as coverage. Every accepted result is compared with fresh sparse least squares; the dense reference qualified that solver at small sizes in the contracts. Third disconnected components are retention controls; connected distant nodes are allowed to change.

Shared saved-state preparation, queue work, global proof scans, reference solves, query, load and persistence costs are reported. No full-solve fallback, sublinear computation, broad learning claim or hierarchy is implied. C1 acceptance is pending.
