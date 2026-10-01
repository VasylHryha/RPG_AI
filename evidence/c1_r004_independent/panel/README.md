# C1 incremental-update receipt

`geomind-c1-r4-004`. Implementation: **REVIEW_READY**. Checks: **PASS**. Elapsed: 117.46s.

80 registered interventions, each run in two arms from the same saved state. Queue arm: 60 committed (60 without a relaxation step), 20 explicitly unresolved and rolled back. Fallback arm: 80 committed, 20 through the metered full solve, 0 unresolved.

H-L (registered endpoints): consistent_additive_in_memory_updates: **SUPPORTED_WITHIN_SCOPE**; contradiction_resolution_by_local_queue: **NOT_SUPPORTED**; durable_persistence: **NOT_TESTED: export/load are O(V+E) by design and reported separately**. H-P: **INCONCLUSIVE**.

[Results](results.json), [per-case stream](instances.jsonl), [contracts](contracts.xml); gzip-compressed canonical states in `states/` (receipts hash the uncompressed text) and source in `source/`.

| Nodes | Intervention | World | Queue arm | Queue operations | Fallback arm | Fallback operations | In-memory update / fresh recompute | Max error |
|---:|---|---:|---|---:|---|---:|---:|---:|
| 32 | consistent_edge | 0 | PASS | 23 | PASS | 0 | 0.1763 | 1.4221956945448255e-13 |
| 32 | inconsistent_edge | 0 | NOT_CONVERGED | 100000 | PASS (fallback) | 495 | n/a | 1.562959304193056e-10 |
| 32 | new_node | 0 | PASS | 24 | PASS | 0 | 0.1631 | 2.7465400791133423e-15 |
| 32 | bridge | 0 | PASS | 53 | PASS | 0 | 0.2796 | 1.0741085019148343e-14 |
| 32 | consistent_edge | 1 | PASS | 30 | PASS | 0 | 0.8165 | 1.897149936107019e-15 |
| 32 | inconsistent_edge | 1 | NOT_CONVERGED | 100000 | PASS (fallback) | 392 | n/a | 8.408000883453428e-10 |
| 32 | new_node | 1 | PASS | 24 | PASS | 0 | 0.5369 | 2.7135600152522366e-15 |
| 32 | bridge | 1 | PASS | 48 | PASS | 0 | 0.2454 | 3.552991223715482e-14 |
| 32 | consistent_edge | 2 | PASS | 33 | PASS | 0 | 0.1717 | 1.3348671786163112e-15 |
| 32 | inconsistent_edge | 2 | NOT_CONVERGED | 99998 | PASS (fallback) | 494 | n/a | 1.9457821157363626e-10 |
| 32 | new_node | 2 | PASS | 27 | PASS | 0 | 0.2045 | 1.790180836524724e-15 |
| 32 | bridge | 2 | PASS | 46 | PASS | 0 | 0.2262 | 1.790180836524724e-14 |
| 32 | consistent_edge | 3 | PASS | 27 | PASS | 0 | 0.1907 | 1.7798229048217483e-15 |
| 32 | inconsistent_edge | 3 | NOT_CONVERGED | 99998 | PASS (fallback) | 502 | n/a | 3.624437398225262e-10 |
| 32 | new_node | 3 | PASS | 24 | PASS | 0 | 0.1742 | 3.58766985720938e-15 |
| 32 | bridge | 3 | PASS | 49 | PASS | 0 | 0.2444 | 1.778575899402738e-14 |
| 32 | consistent_edge | 4 | PASS | 27 | PASS | 0 | 0.0597 | 1.790180836524724e-15 |
| 32 | inconsistent_edge | 4 | NOT_CONVERGED | 99998 | PASS (fallback) | 366 | n/a | 1.0185000563910788e-09 |
| 32 | new_node | 4 | PASS | 27 | PASS | 0 | 0.2015 | 1.831026719408895e-15 |
| 32 | bridge | 4 | PASS | 45 | PASS | 0 | 0.2146 | 1.422645865968639e-14 |
| 128 | consistent_edge | 0 | PASS | 37 | PASS | 0 | 0.0672 | 5.196579415701528e-12 |
| 128 | inconsistent_edge | 0 | NOT_CONVERGED | 100000 | PASS (fallback) | 4922 | n/a | 7.773267923628627e-10 |
| 128 | new_node | 0 | PASS | 30 | PASS | 0 | 0.0551 | 5.740511333899422e-12 |
| 128 | bridge | 0 | PASS | 83 | PASS | 0 | 0.1707 | 4.583830790297411e-12 |
| 128 | consistent_edge | 1 | PASS | 33 | PASS | 0 | 0.0247 | 6.494517761490734e-12 |
| 128 | inconsistent_edge | 1 | NOT_CONVERGED | 99999 | PASS (fallback) | 4568 | n/a | 1.1802480939441416e-09 |
| 128 | new_node | 1 | PASS | 27 | PASS | 0 | 0.0730 | 7.801157877052166e-12 |
| 128 | bridge | 1 | PASS | 80 | PASS | 0 | 0.0280 | 4.1176692776919565e-12 |
| 128 | consistent_edge | 2 | PASS | 36 | PASS | 0 | 0.0613 | 6.723479662276194e-12 |
| 128 | inconsistent_edge | 2 | NOT_CONVERGED | 99998 | PASS (fallback) | 4682 | n/a | 4.462230664824174e-10 |
| 128 | new_node | 2 | PASS | 33 | PASS | 0 | 0.0295 | 2.2229829944660555e-12 |
| 128 | bridge | 2 | PASS | 77 | PASS | 0 | 0.0369 | 4.66082525789357e-12 |
| 128 | consistent_edge | 3 | PASS | 33 | PASS | 0 | 0.0172 | 5.051633190952319e-12 |
| 128 | inconsistent_edge | 3 | NOT_CONVERGED | 99997 | PASS (fallback) | 4764 | n/a | 1.1137849881936786e-09 |
| 128 | new_node | 3 | PASS | 31 | PASS | 0 | 0.0604 | 7.070948456549503e-12 |
| 128 | bridge | 3 | PASS | 80 | PASS | 0 | 0.1915 | 5.970153060991903e-12 |
| 128 | consistent_edge | 4 | PASS | 37 | PASS | 0 | 0.0296 | 9.453568870481028e-12 |
| 128 | inconsistent_edge | 4 | NOT_CONVERGED | 99998 | PASS (fallback) | 5042 | n/a | 5.506973820141055e-10 |
| 128 | new_node | 4 | PASS | 27 | PASS | 0 | 0.0325 | 2.7742821640672425e-12 |
| 128 | bridge | 4 | PASS | 77 | PASS | 0 | 0.0720 | 3.761620998309499e-12 |
| 512 | consistent_edge | 0 | PASS | 42 | PASS | 0 | 0.0137 | 9.41804253087823e-12 |
| 512 | inconsistent_edge | 0 | NOT_CONVERGED | 99999 | PASS (fallback) | 34877 | n/a | 2.3773156332906696e-09 |
| 512 | new_node | 0 | PASS | 33 | PASS | 0 | 0.0187 | 1.1373659867167873e-11 |
| 512 | bridge | 0 | PASS | 181 | PASS | 0 | 0.0151 | 1.1907082211544212e-11 |
| 512 | consistent_edge | 1 | PASS | 39 | PASS | 0 | 0.0073 | 1.3758049228681584e-11 |
| 512 | inconsistent_edge | 1 | NOT_CONVERGED | 100000 | PASS (fallback) | 34846 | n/a | 2.1765443848466788e-09 |
| 512 | new_node | 1 | PASS | 30 | PASS | 0 | 0.2209 | 1.2235950857258453e-11 |
| 512 | bridge | 1 | PASS | 181 | PASS | 0 | 0.0205 | 1.2798673710000167e-11 |
| 512 | consistent_edge | 2 | PASS | 36 | PASS | 0 | 0.0073 | 1.2676061900423051e-11 |
| 512 | inconsistent_edge | 2 | NOT_CONVERGED | 100000 | PASS (fallback) | 32890 | n/a | 6.289286849819841e-09 |
| 512 | new_node | 2 | PASS | 30 | PASS | 0 | 0.0179 | 1.2825184742599462e-11 |
| 512 | bridge | 2 | PASS | 181 | PASS | 0 | 0.0218 | 1.0374765367676111e-11 |
| 512 | consistent_edge | 3 | PASS | 33 | PASS | 0 | 0.0158 | 9.885150665639122e-12 |
| 512 | inconsistent_edge | 3 | NOT_CONVERGED | 99997 | PASS (fallback) | 35254 | n/a | 2.690495346248246e-09 |
| 512 | new_node | 3 | PASS | 30 | PASS | 0 | 0.0185 | 1.3118470486324758e-11 |
| 512 | bridge | 3 | PASS | 175 | PASS | 0 | 0.0273 | 1.5143299842487063e-11 |
| 512 | consistent_edge | 4 | PASS | 36 | PASS | 0 | 0.0576 | 9.303754584170298e-12 |
| 512 | inconsistent_edge | 4 | NOT_CONVERGED | 100000 | PASS (fallback) | 35926 | n/a | 1.7348321864585488e-09 |
| 512 | new_node | 4 | PASS | 30 | PASS | 0 | 0.0107 | 1.569729464101508e-11 |
| 512 | bridge | 4 | PASS | 181 | PASS | 0 | 0.0173 | 1.121330091476134e-11 |
| 2048 | consistent_edge | 0 | PASS | 36 | PASS | 0 | 0.0066 | 3.702035477622854e-11 |
| 2048 | inconsistent_edge | 0 | NOT_CONVERGED | 100000 | PASS (fallback) | 190009 | n/a | 5.741839162822071e-09 |
| 2048 | new_node | 0 | PASS | 33 | PASS | 0 | 0.0049 | 2.197499350007529e-11 |
| 2048 | bridge | 0 | PASS | 565 | PASS | 0 | 0.0624 | 2.5222195702279967e-11 |
| 2048 | consistent_edge | 1 | PASS | 33 | PASS | 0 | 0.0022 | 2.17177509276882e-11 |
| 2048 | inconsistent_edge | 1 | NOT_CONVERGED | 99999 | PASS (fallback) | 187633 | n/a | 3.9533297120125815e-09 |
| 2048 | new_node | 1 | PASS | 30 | PASS | 0 | 0.0022 | 1.4130187552118523e-11 |
| 2048 | bridge | 1 | PASS | 567 | PASS | 0 | 0.0265 | 3.9639493151673966e-11 |
| 2048 | consistent_edge | 2 | PASS | 39 | PASS | 0 | 0.0036 | 2.950551895833801e-11 |
| 2048 | inconsistent_edge | 2 | NOT_CONVERGED | 99998 | PASS (fallback) | 189831 | n/a | 3.75025303091911e-09 |
| 2048 | new_node | 2 | PASS | 30 | PASS | 0 | 0.0025 | 1.9656122716659457e-11 |
| 2048 | bridge | 2 | PASS | 567 | PASS | 0 | 0.0069 | 3.148619110506349e-11 |
| 2048 | consistent_edge | 3 | PASS | 36 | PASS | 0 | 0.0021 | 2.1886172839965208e-11 |
| 2048 | inconsistent_edge | 3 | NOT_CONVERGED | 100000 | PASS (fallback) | 196345 | n/a | 6.068073875723405e-09 |
| 2048 | new_node | 3 | PASS | 30 | PASS | 0 | 0.0043 | 1.8704825383899615e-11 |
| 2048 | bridge | 3 | PASS | 567 | PASS | 0 | 0.0138 | 2.7118802521911723e-11 |
| 2048 | consistent_edge | 4 | PASS | 33 | PASS | 0 | 0.0028 | 2.4218755356856715e-11 |
| 2048 | inconsistent_edge | 4 | NOT_CONVERGED | 99997 | PASS (fallback) | 197620 | n/a | 2.264234847271587e-09 |
| 2048 | new_node | 4 | PASS | 30 | PASS | 0 | 0.0026 | 2.1231862320899668e-11 |
| 2048 | bridge | 4 | PASS | 567 | PASS | 0 | 0.0071 | 3.098982328902464e-11 |

Unresolved updates keep the preceding snapshot byte-identically; their prior-state answers are counted separately, never as coverage. Fallback commits are reported as a distinct arm, not as local queue successes. Every committed answer is compared with a fresh independent sparse least-squares reference built after both arms answered; compiled coordinates are also measured. Persistence (export/load) and reference costs are reported separately from the in-memory update.
