# C1 incremental-update receipt

`geomind-c1-r4-005`. Implementation: **REVIEW_READY**. Checks: **PASS**. Elapsed: 104.53s.

80 registered interventions, each run in two arms from the same saved state. Queue arm: 63 committed (60 without a relaxation step), 17 explicitly unresolved and rolled back. Fallback arm: 80 committed, 17 through the metered full solve, 0 unresolved.

H-L (registered endpoints): consistent_edge_and_new_node_in_memory_updates: **SUPPORTED_WITHIN_SCOPE**; bridge_in_memory_updates: **NOT_TESTED for size independence: cost grows with the translated frames (reported); faster-than-recompute endpoint met**; contradiction_resolution_by_local_queue: **NOT_SUPPORTED**; durable_persistence: **NOT_TESTED: export/load are O(V+E) by design and reported separately**. H-P: **INCONCLUSIVE**.

[Results](results.json), [per-case stream](instances.jsonl), [contracts](contracts.xml); gzip-compressed canonical states in `states/` (receipts hash the uncompressed text) and source in `source/`.

| Nodes | Intervention | World | Queue arm | Queue operations | Fallback arm | Fallback operations | In-memory update / fresh recompute | Incremental compiled | Max error |
|---:|---|---:|---|---:|---|---:|---:|---|---:|
| 32 | consistent_edge | 0 | PASS | 27 | PASS | 0 | 0.3131 | PASS, 1 ops | 2.7755575615628914e-15 |
| 32 | inconsistent_edge | 0 | NOT_CONVERGED | 100000 | PASS (fallback) | 417 | n/a | NOT_CONVERGED, 1 ops | 3.7586125919101887e-10 |
| 32 | new_node | 0 | PASS | 86 | PASS | 0 | 0.2997 | PASS, 3 ops | 2.401779625492033e-15 |
| 32 | bridge | 0 | PASS | 106 | PASS | 0 | 0.5854 | PASS, 9 ops | 1.0704876105541625e-14 |
| 32 | consistent_edge | 1 | PASS | 36 | PASS | 0 | 0.0687 | PASS, 1 ops | 3.552822097363439e-15 |
| 32 | inconsistent_edge | 1 | NOT_CONVERGED | 100000 | PASS (fallback) | 377 | n/a | NOT_CONVERGED, 1 ops | 9.839188673320205e-10 |
| 32 | new_node | 1 | PASS | 27 | PASS | 0 | 0.2591 | PASS, 3 ops | 3.233018248352212e-15 |
| 32 | bridge | 1 | PASS | 95 | PASS | 0 | 0.3949 | PASS, 9 ops | 1.4383281002407285e-14 |
| 32 | consistent_edge | 2 | PASS | 24 | PASS | 0 | 0.0537 | PASS, 1 ops | 1.790180836524724e-15 |
| 32 | inconsistent_edge | 2 | PASS | 98106 | PASS | 0 | 30.4870 | NOT_CONVERGED, 1 ops | 6.055125806360517e-08 |
| 32 | new_node | 2 | PASS | 86 | PASS | 0 | 0.3769 | PASS, 3 ops | 1.1957467920563633e-15 |
| 32 | bridge | 2 | PASS | 91 | PASS | 0 | 0.3652 | PASS, 9 ops | 1.1234667099445444e-14 |
| 32 | consistent_edge | 3 | PASS | 33 | PASS | 0 | 0.1963 | PASS, 1 ops | 2.2644195468014703e-15 |
| 32 | inconsistent_edge | 3 | PASS | 87623 | PASS | 0 | 224.1314 | NOT_CONVERGED, 1 ops | 3.7466471815045066e-08 |
| 32 | new_node | 3 | PASS | 27 | PASS | 0 | 0.0354 | PASS, 3 ops | 1.807312143953211e-15 |
| 32 | bridge | 3 | PASS | 63 | PASS | 0 | 0.8196 | PASS, 9 ops | 1.4210854715202004e-14 |
| 32 | consistent_edge | 4 | PASS | 85 | PASS | 0 | 0.4769 | PASS, 1 ops | 1.4043333874306805e-15 |
| 32 | inconsistent_edge | 4 | PASS | 68584 | PASS | 0 | 29.3989 | NOT_CONVERGED, 1 ops | 4.090595642234266e-08 |
| 32 | new_node | 4 | PASS | 20 | PASS | 0 | 0.2640 | PASS, 3 ops | 3.774758283725532e-15 |
| 32 | bridge | 4 | PASS | 54 | PASS | 0 | 0.2743 | PASS, 9 ops | 2.6646277760795913e-14 |
| 128 | consistent_edge | 0 | PASS | 33 | PASS | 0 | 0.0227 | PASS, 1 ops | 7.872184540242623e-12 |
| 128 | inconsistent_edge | 0 | NOT_CONVERGED | 99998 | PASS (fallback) | 4599 | n/a | NOT_CONVERGED, 1 ops | 4.540720379342646e-10 |
| 128 | new_node | 0 | PASS | 27 | PASS | 0 | 0.0657 | PASS, 3 ops | 7.255243298658262e-12 |
| 128 | bridge | 0 | PASS | 184 | PASS | 0 | 0.1469 | PASS, 33 ops | 6.394018604661952e-12 |
| 128 | consistent_edge | 1 | PASS | 33 | PASS | 0 | 0.0215 | PASS, 1 ops | 7.381055207681562e-12 |
| 128 | inconsistent_edge | 1 | NOT_CONVERGED | 99998 | PASS (fallback) | 4882 | n/a | NOT_CONVERGED, 1 ops | 8.462519956351234e-10 |
| 128 | new_node | 1 | PASS | 30 | PASS | 0 | 0.0595 | PASS, 3 ops | 1.1346200411961535e-11 |
| 128 | bridge | 1 | PASS | 344 | PASS | 0 | 0.2298 | PASS, 33 ops | 5.534259688977924e-12 |
| 128 | consistent_edge | 2 | PASS | 36 | PASS | 0 | 0.0627 | PASS, 1 ops | 5.077747179349413e-12 |
| 128 | inconsistent_edge | 2 | NOT_CONVERGED | 100000 | PASS (fallback) | 4883 | n/a | NOT_CONVERGED, 1 ops | 1.175597190292522e-09 |
| 128 | new_node | 2 | PASS | 326 | PASS | 0 | 0.2034 | PASS, 3 ops | 3.989517181913977e-12 |
| 128 | bridge | 2 | PASS | 181 | PASS | 0 | 0.0460 | PASS, 33 ops | 8.41924202167233e-12 |
| 128 | consistent_edge | 3 | PASS | 320 | PASS | 0 | 0.1204 | PASS, 1 ops | 5.197612106027764e-12 |
| 128 | inconsistent_edge | 3 | NOT_CONVERGED | 99999 | PASS (fallback) | 4803 | n/a | NOT_CONVERGED, 1 ops | 7.401558321875884e-10 |
| 128 | new_node | 3 | PASS | 317 | PASS | 0 | 0.1308 | PASS, 3 ops | 7.115950277747083e-12 |
| 128 | bridge | 3 | PASS | 473 | PASS | 0 | 0.2778 | PASS, 33 ops | 9.331186425301888e-12 |
| 128 | consistent_edge | 4 | PASS | 39 | PASS | 0 | 0.0284 | PASS, 1 ops | 4.195550437272423e-12 |
| 128 | inconsistent_edge | 4 | NOT_CONVERGED | 99996 | PASS (fallback) | 5078 | n/a | NOT_CONVERGED, 1 ops | 3.4802069429703043e-10 |
| 128 | new_node | 4 | PASS | 24 | PASS | 0 | 0.0301 | PASS, 3 ops | 6.219681832853306e-12 |
| 128 | bridge | 4 | PASS | 333 | PASS | 0 | 0.0775 | PASS, 33 ops | 9.6911399190416e-12 |
| 512 | consistent_edge | 0 | PASS | 1288 | PASS | 0 | 0.0563 | PASS, 1 ops | 1.7414247172842152e-11 |
| 512 | inconsistent_edge | 0 | NOT_CONVERGED | 99998 | PASS (fallback) | 36866 | n/a | NOT_CONVERGED, 1 ops | 3.225305635248412e-09 |
| 512 | new_node | 0 | PASS | 30 | PASS | 0 | 0.0064 | PASS, 3 ops | 1.2627144099584143e-11 |
| 512 | bridge | 0 | PASS | 670 | PASS | 0 | 0.0387 | PASS, 129 ops | 2.057770975284678e-11 |
| 512 | consistent_edge | 1 | PASS | 36 | PASS | 0 | 0.0151 | PASS, 1 ops | 1.6886318696455496e-11 |
| 512 | inconsistent_edge | 1 | NOT_CONVERGED | 99997 | PASS (fallback) | 34474 | n/a | NOT_CONVERGED, 1 ops | 4.191586157404442e-09 |
| 512 | new_node | 1 | PASS | 30 | PASS | 0 | 0.0117 | PASS, 3 ops | 1.3706564914052052e-11 |
| 512 | bridge | 1 | PASS | 1321 | PASS | 0 | 0.0872 | PASS, 129 ops | 2.34320673608866e-11 |
| 512 | consistent_edge | 2 | PASS | 36 | PASS | 0 | 0.0097 | PASS, 1 ops | 1.0847509611658759e-11 |
| 512 | inconsistent_edge | 2 | NOT_CONVERGED | 99999 | PASS (fallback) | 33655 | n/a | NOT_CONVERGED, 1 ops | 1.4332016817247775e-09 |
| 512 | new_node | 2 | PASS | 30 | PASS | 0 | 0.0115 | PASS, 3 ops | 1.1121048973043196e-11 |
| 512 | bridge | 2 | PASS | 658 | PASS | 0 | 0.0891 | PASS, 129 ops | 1.7541326477445416e-11 |
| 512 | consistent_edge | 3 | PASS | 33 | PASS | 0 | 0.0162 | PASS, 1 ops | 1.5823703196702647e-11 |
| 512 | inconsistent_edge | 3 | NOT_CONVERGED | 99998 | PASS (fallback) | 34165 | n/a | NOT_CONVERGED, 1 ops | 2.542948947857684e-09 |
| 512 | new_node | 3 | PASS | 30 | PASS | 0 | 0.0099 | PASS, 3 ops | 1.825866599390339e-11 |
| 512 | bridge | 3 | PASS | 657 | PASS | 0 | 0.0931 | PASS, 129 ops | 1.4028654625868957e-11 |
| 512 | consistent_edge | 4 | PASS | 33 | PASS | 0 | 0.0086 | PASS, 1 ops | 1.0945381268523616e-11 |
| 512 | inconsistent_edge | 4 | NOT_CONVERGED | 99998 | PASS (fallback) | 34846 | n/a | NOT_CONVERGED, 1 ops | 2.6446812774221846e-09 |
| 512 | new_node | 4 | PASS | 30 | PASS | 0 | 0.0098 | PASS, 3 ops | 1.0020507223025233e-11 |
| 512 | bridge | 4 | PASS | 1321 | PASS | 0 | 0.1632 | PASS, 129 ops | 1.3212778722373168e-11 |
| 2048 | consistent_edge | 0 | PASS | 42 | PASS | 0 | 0.0030 | PASS, 1 ops | 2.527255032425584e-11 |
| 2048 | inconsistent_edge | 0 | NOT_CONVERGED | 99997 | PASS (fallback) | 189386 | n/a | NOT_CONVERGED, 1 ops | 6.601321029475371e-09 |
| 2048 | new_node | 0 | PASS | 27 | PASS | 0 | 0.0027 | PASS, 3 ops | 2.17411585890888e-11 |
| 2048 | bridge | 0 | PASS | 2635 | PASS | 0 | 0.0444 | PASS, 513 ops | 2.1417530803065488e-11 |
| 2048 | consistent_edge | 1 | PASS | 39 | PASS | 0 | 0.0055 | PASS, 1 ops | 2.5858211314452238e-11 |
| 2048 | inconsistent_edge | 1 | NOT_CONVERGED | 99998 | PASS (fallback) | 190952 | n/a | NOT_CONVERGED, 1 ops | 3.602720649860556e-09 |
| 2048 | new_node | 1 | PASS | 33 | PASS | 0 | 0.0041 | PASS, 3 ops | 1.7833148088899853e-11 |
| 2048 | bridge | 1 | PASS | 2639 | PASS | 0 | 0.0731 | PASS, 513 ops | 1.8591992320867557e-11 |
| 2048 | consistent_edge | 2 | PASS | 36 | PASS | 0 | 0.0041 | PASS, 1 ops | 2.374533814359264e-11 |
| 2048 | inconsistent_edge | 2 | NOT_CONVERGED | 99997 | PASS (fallback) | 189564 | n/a | NOT_CONVERGED, 1 ops | 3.812891343592397e-09 |
| 2048 | new_node | 2 | PASS | 27 | PASS | 0 | 0.0040 | PASS, 3 ops | 2.2085058177193476e-11 |
| 2048 | bridge | 2 | PASS | 5267 | PASS | 0 | 0.1077 | PASS, 513 ops | 2.5273738681026422e-11 |
| 2048 | consistent_edge | 3 | PASS | 39 | PASS | 0 | 0.0030 | PASS, 1 ops | 1.5962601345217988e-11 |
| 2048 | inconsistent_edge | 3 | NOT_CONVERGED | 99998 | PASS (fallback) | 197713 | n/a | NOT_CONVERGED, 1 ops | 3.3177468294254037e-09 |
| 2048 | new_node | 3 | PASS | 30 | PASS | 0 | 0.0034 | PASS, 3 ops | 2.390505979596815e-11 |
| 2048 | bridge | 3 | PASS | 2637 | PASS | 0 | 0.0336 | PASS, 513 ops | 2.1344836239855715e-11 |
| 2048 | consistent_edge | 4 | PASS | 33 | PASS | 0 | 0.0017 | PASS, 1 ops | 2.247550371193216e-11 |
| 2048 | inconsistent_edge | 4 | NOT_CONVERGED | 99998 | PASS (fallback) | 178861 | n/a | NOT_CONVERGED, 1 ops | 2.9803089462557245e-09 |
| 2048 | new_node | 4 | PASS | 30 | PASS | 0 | 0.0021 | PASS, 3 ops | 2.1944300264350805e-11 |
| 2048 | bridge | 4 | PASS | 5262 | PASS | 0 | 0.2726 | PASS, 513 ops | 3.9097134189929243e-11 |

Unresolved updates keep the preceding snapshot byte-identically; their prior-state answers are counted separately, never as coverage. Fallback commits are reported as a distinct arm, not as local queue successes. Every committed answer is compared with a fresh independent sparse least-squares reference built after both arms and the incremental compiled baseline answered; compiled coordinates are also measured. Fallback operations and reference edge visits use different units, scopes and tolerances and are not compared as a ratio. Persistence (export/load) and reference costs are reported separately from the in-memory update.
