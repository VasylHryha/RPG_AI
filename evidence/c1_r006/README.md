# C1 incremental-update receipt

`geomind-c1-r4-006`. Implementation: **REVIEW_READY**. Checks: **PASS**. Elapsed: 106.37s.

80 registered interventions, each run in two arms from the same saved state. Queue arm: 61 committed (60 without a relaxation step), 19 explicitly unresolved and rolled back. Fallback arm: 80 committed, 19 through the metered full solve, 0 unresolved.

H-L (registered endpoints): consistent_edge_and_new_node_in_memory_updates: **SUPPORTED_WITHIN_SCOPE**; bridge_in_memory_updates: **NOT_TESTED for size independence: cost grows with the translated frames (reported); faster-than-recompute endpoint met**; contradiction_resolution_by_local_queue: **NOT_SUPPORTED**; durable_persistence: **NOT_TESTED: export/load are O(V+E) by design and reported separately**. H-P: **INCONCLUSIVE**.

[Results](results.json), [per-case stream](instances.jsonl), [contracts](contracts.xml); gzip-compressed canonical states in `states/` (receipts hash the uncompressed text) and source in `source/`.

| Nodes | Intervention | World | Queue arm | Queue operations | Fallback arm | Fallback operations | In-memory update / fresh recompute | Incremental compiled | Max error |
|---:|---|---:|---|---:|---|---:|---:|---|---:|
| 32 | consistent_edge | 0 | PASS | 27 | PASS | 0 | 0.3427 | PASS, 1 ops | 3.552713678800501e-15 |
| 32 | inconsistent_edge | 0 | NOT_CONVERGED | 99999 | PASS (fallback) | 339 | n/a | NOT_CONVERGED, 1 ops | 2.2691500445804253e-09 |
| 32 | new_node | 0 | PASS | 24 | PASS | 0 | 0.4064 | PASS, 3 ops | 2.220446049250313e-15 |
| 32 | bridge | 0 | PASS | 95 | PASS | 0 | 0.5378 | PASS, 9 ops | 2.1431618279190542e-14 |
| 32 | consistent_edge | 1 | PASS | 27 | PASS | 0 | 0.3723 | PASS, 1 ops | 1.7817696036042146e-15 |
| 32 | inconsistent_edge | 1 | NOT_CONVERGED | 99998 | PASS (fallback) | 313 | n/a | NOT_CONVERGED, 1 ops | 4.037809460905916e-09 |
| 32 | new_node | 1 | PASS | 27 | PASS | 0 | 0.3300 | PASS, 3 ops | 3.132816463918267e-15 |
| 32 | bridge | 1 | PASS | 64 | PASS | 0 | 0.3426 | PASS, 9 ops | 1.3330075727505561e-14 |
| 32 | consistent_edge | 2 | PASS | 30 | PASS | 0 | 0.2252 | PASS, 1 ops | 1.7763568394002505e-15 |
| 32 | inconsistent_edge | 2 | NOT_CONVERGED | 99999 | PASS (fallback) | 426 | n/a | NOT_CONVERGED, 1 ops | 9.739403860236085e-10 |
| 32 | new_node | 2 | PASS | 27 | PASS | 0 | 0.2872 | PASS, 3 ops | 2.4567236915825255e-15 |
| 32 | bridge | 2 | PASS | 69 | PASS | 0 | 1.1264 | PASS, 9 ops | 2.1334777765716796e-14 |
| 32 | consistent_edge | 3 | PASS | 30 | PASS | 0 | 0.2485 | PASS, 1 ops | 2.220446049250313e-15 |
| 32 | inconsistent_edge | 3 | NOT_CONVERGED | 99998 | PASS (fallback) | 391 | n/a | NOT_CONVERGED, 1 ops | 1.441218422072051e-09 |
| 32 | new_node | 3 | PASS | 27 | PASS | 0 | 0.2562 | PASS, 3 ops | 2.7012892057857038e-15 |
| 32 | bridge | 3 | PASS | 123 | PASS | 0 | 0.5029 | PASS, 9 ops | 1.0986160316453369e-14 |
| 32 | consistent_edge | 4 | PASS | 26 | PASS | 0 | 0.2552 | PASS, 1 ops | 1.790180836524724e-15 |
| 32 | inconsistent_edge | 4 | PASS | 71342 | PASS | 0 | 91.3640 | NOT_CONVERGED, 1 ops | 4.85244229477765e-08 |
| 32 | new_node | 4 | PASS | 89 | PASS | 0 | 0.4094 | PASS, 3 ops | 2.3603665272841412e-15 |
| 32 | bridge | 4 | PASS | 66 | PASS | 0 | 0.3215 | PASS, 9 ops | 1.4211288389453755e-14 |
| 128 | consistent_edge | 0 | PASS | 33 | PASS | 0 | 0.0675 | PASS, 1 ops | 5.994372561977089e-12 |
| 128 | inconsistent_edge | 0 | NOT_CONVERGED | 99998 | PASS (fallback) | 4682 | n/a | NOT_CONVERGED, 1 ops | 1.4462860010391125e-09 |
| 128 | new_node | 0 | PASS | 30 | PASS | 0 | 0.0299 | PASS, 3 ops | 6.5800201742042605e-12 |
| 128 | bridge | 0 | PASS | 338 | PASS | 0 | 0.2322 | PASS, 33 ops | 9.368758496493453e-12 |
| 128 | consistent_edge | 1 | PASS | 36 | PASS | 0 | 0.0722 | PASS, 1 ops | 1.0823279670883928e-11 |
| 128 | inconsistent_edge | 1 | NOT_CONVERGED | 99999 | PASS (fallback) | 4682 | n/a | NOT_CONVERGED, 1 ops | 1.2996743763255843e-09 |
| 128 | new_node | 1 | PASS | 30 | PASS | 0 | 0.0862 | PASS, 3 ops | 2.829583393331755e-12 |
| 128 | bridge | 1 | PASS | 184 | PASS | 0 | 0.1057 | PASS, 33 ops | 8.61709553891124e-12 |
| 128 | consistent_edge | 2 | PASS | 33 | PASS | 0 | 0.0747 | PASS, 1 ops | 7.221121531326099e-12 |
| 128 | inconsistent_edge | 2 | NOT_CONVERGED | 100000 | PASS (fallback) | 4452 | n/a | NOT_CONVERGED, 1 ops | 3.468759784263097e-10 |
| 128 | new_node | 2 | PASS | 317 | PASS | 0 | 0.1433 | PASS, 3 ops | 3.8299053932263456e-12 |
| 128 | bridge | 2 | PASS | 177 | PASS | 0 | 0.1596 | PASS, 33 ops | 5.497925090395836e-12 |
| 128 | consistent_edge | 3 | PASS | 36 | PASS | 0 | 0.0790 | PASS, 1 ops | 6.9288986768424016e-12 |
| 128 | inconsistent_edge | 3 | NOT_CONVERGED | 100000 | PASS (fallback) | 4443 | n/a | NOT_CONVERGED, 1 ops | 2.0886170507674644e-09 |
| 128 | new_node | 3 | PASS | 27 | PASS | 0 | 0.0905 | PASS, 3 ops | 4.0077588743304074e-12 |
| 128 | bridge | 3 | PASS | 342 | PASS | 0 | 0.2060 | PASS, 33 ops | 7.327432128961364e-12 |
| 128 | consistent_edge | 4 | PASS | 317 | PASS | 0 | 0.2442 | PASS, 1 ops | 5.31516914027538e-12 |
| 128 | inconsistent_edge | 4 | NOT_CONVERGED | 99998 | PASS (fallback) | 4644 | n/a | NOT_CONVERGED, 1 ops | 1.6480593154131279e-09 |
| 128 | new_node | 4 | PASS | 322 | PASS | 0 | 0.1120 | PASS, 3 ops | 5.9323769298618636e-12 |
| 128 | bridge | 4 | PASS | 336 | PASS | 0 | 0.2017 | PASS, 33 ops | 6.367049485229734e-12 |
| 512 | consistent_edge | 0 | PASS | 33 | PASS | 0 | 0.0130 | PASS, 1 ops | 1.7686340047085482e-11 |
| 512 | inconsistent_edge | 0 | NOT_CONVERGED | 100000 | PASS (fallback) | 33655 | n/a | NOT_CONVERGED, 1 ops | 2.403564785739734e-09 |
| 512 | new_node | 0 | PASS | 27 | PASS | 0 | 0.0166 | PASS, 3 ops | 1.3305713990514164e-11 |
| 512 | bridge | 0 | PASS | 663 | PASS | 0 | 0.0931 | PASS, 129 ops | 2.0822560059180223e-11 |
| 512 | consistent_edge | 1 | PASS | 36 | PASS | 0 | 0.1924 | PASS, 1 ops | 2.2327389728624676e-11 |
| 512 | inconsistent_edge | 1 | NOT_CONVERGED | 99998 | PASS (fallback) | 34675 | n/a | NOT_CONVERGED, 1 ops | 2.0322466785781146e-09 |
| 512 | new_node | 1 | PASS | 33 | PASS | 0 | 0.0146 | PASS, 3 ops | 7.689623683615965e-12 |
| 512 | bridge | 1 | PASS | 1929 | PASS | 0 | 0.7448 | PASS, 129 ops | 8.50740827682535e-12 |
| 512 | consistent_edge | 2 | PASS | 33 | PASS | 0 | 0.1306 | PASS, 1 ops | 1.1394633409904022e-11 |
| 512 | inconsistent_edge | 2 | NOT_CONVERGED | 100000 | PASS (fallback) | 33785 | n/a | NOT_CONVERGED, 1 ops | 3.507789838126972e-09 |
| 512 | new_node | 2 | PASS | 30 | PASS | 0 | 0.0237 | PASS, 3 ops | 1.1533841604217365e-11 |
| 512 | bridge | 2 | PASS | 669 | PASS | 0 | 0.0377 | PASS, 129 ops | 2.182947452986543e-11 |
| 512 | consistent_edge | 3 | PASS | 39 | PASS | 0 | 0.0208 | PASS, 1 ops | 1.6046624053039407e-11 |
| 512 | inconsistent_edge | 3 | NOT_CONVERGED | 99996 | PASS (fallback) | 32762 | n/a | NOT_CONVERGED, 1 ops | 4.138551631257801e-09 |
| 512 | new_node | 3 | PASS | 1296 | PASS | 0 | 0.2531 | PASS, 3 ops | 1.0423772274200701e-11 |
| 512 | bridge | 3 | PASS | 664 | PASS | 0 | 0.0337 | PASS, 129 ops | 8.921848956791063e-12 |
| 512 | consistent_edge | 4 | PASS | 36 | PASS | 0 | 0.0099 | PASS, 1 ops | 1.3398180918492154e-11 |
| 512 | inconsistent_edge | 4 | NOT_CONVERGED | 100000 | PASS (fallback) | 35322 | n/a | NOT_CONVERGED, 1 ops | 2.806329943353833e-09 |
| 512 | new_node | 4 | PASS | 27 | PASS | 0 | 0.0187 | PASS, 3 ops | 1.2767854403302149e-11 |
| 512 | bridge | 4 | PASS | 1938 | PASS | 0 | 0.4480 | PASS, 129 ops | 1.1116950464872037e-11 |
| 2048 | consistent_edge | 0 | PASS | 36 | PASS | 0 | 0.0034 | PASS, 1 ops | 2.1176748825667578e-11 |
| 2048 | inconsistent_edge | 0 | NOT_CONVERGED | 99999 | PASS (fallback) | 192121 | n/a | NOT_CONVERGED, 1 ops | 2.551071010515155e-09 |
| 2048 | new_node | 0 | PASS | 30 | PASS | 0 | 0.0032 | PASS, 3 ops | 1.780801638593548e-11 |
| 2048 | bridge | 0 | PASS | 2634 | PASS | 0 | 0.0536 | PASS, 513 ops | 2.207426440799031e-11 |
| 2048 | consistent_edge | 1 | PASS | 39 | PASS | 0 | 0.0040 | PASS, 1 ops | 3.384774820053392e-11 |
| 2048 | inconsistent_edge | 1 | NOT_CONVERGED | 99998 | PASS (fallback) | 193505 | n/a | NOT_CONVERGED, 1 ops | 3.959943850577256e-09 |
| 2048 | new_node | 1 | PASS | 36 | PASS | 0 | 0.0030 | PASS, 3 ops | 1.7297000879781274e-11 |
| 2048 | bridge | 1 | PASS | 5284 | PASS | 0 | 0.0989 | PASS, 513 ops | 1.6996168964970683e-11 |
| 2048 | consistent_edge | 2 | PASS | 36 | PASS | 0 | 0.0029 | PASS, 1 ops | 2.206402990944995e-11 |
| 2048 | inconsistent_edge | 2 | NOT_CONVERGED | 100000 | PASS (fallback) | 194233 | n/a | NOT_CONVERGED, 1 ops | 3.0311334553324876e-09 |
| 2048 | new_node | 2 | PASS | 30 | PASS | 0 | 0.0036 | PASS, 3 ops | 1.5477996010885976e-11 |
| 2048 | bridge | 2 | PASS | 2633 | PASS | 0 | 0.2802 | PASS, 513 ops | 1.7739862014697832e-11 |
| 2048 | consistent_edge | 3 | PASS | 36 | PASS | 0 | 0.0032 | PASS, 1 ops | 2.103363677732189e-11 |
| 2048 | inconsistent_edge | 3 | NOT_CONVERGED | 100000 | PASS (fallback) | 193596 | n/a | NOT_CONVERGED, 1 ops | 5.9507653867896215e-09 |
| 2048 | new_node | 3 | PASS | 30 | PASS | 0 | 0.0169 | PASS, 3 ops | 2.243011598189976e-11 |
| 2048 | bridge | 3 | PASS | 2626 | PASS | 0 | 0.0596 | PASS, 513 ops | 1.578613613176541e-11 |
| 2048 | consistent_edge | 4 | PASS | 33 | PASS | 0 | 0.0031 | PASS, 1 ops | 1.5070793065710124e-11 |
| 2048 | inconsistent_edge | 4 | NOT_CONVERGED | 99998 | PASS (fallback) | 193778 | n/a | NOT_CONVERGED, 1 ops | 3.231742669598035e-09 |
| 2048 | new_node | 4 | PASS | 33 | PASS | 0 | 0.0034 | PASS, 3 ops | 2.1752509537842893e-11 |
| 2048 | bridge | 4 | PASS | 5269 | PASS | 0 | 0.1982 | PASS, 513 ops | 3.315908297407759e-11 |

Unresolved updates keep the preceding snapshot byte-identically; their prior-state answers are counted separately, never as coverage. Fallback commits are reported as a distinct arm, not as local queue successes. Every committed answer is compared with a fresh independent sparse least-squares reference built after both arms and the incremental compiled baseline answered; compiled coordinates are also measured. Fallback operations and reference edge visits use different units, scopes and tolerances and are not compared as a ratio. Persistence (export/load) and reference costs are reported separately from the in-memory update.
