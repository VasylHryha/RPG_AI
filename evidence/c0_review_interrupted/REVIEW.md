# C0 implementation and evaluator review

Scope: the actual local candidate, generator, three controls, caller/CLI, serialization, tests and R001 receipts against GeoMind R4. The user authorized breaking changes and full rework. This receipt is not a competing plan. The same assistant performed this audit and its repairs; it does not constitute independent acceptance of the repaired implementation.

| Finding | Severity | Repair and evidence |
|---|---|---|
| Checksum-valid artifacts could contain wrong finite coordinates and still return confident answers | High | Strict version/field/type/connectivity/gauge validation plus independent-on-load stationarity checks; regression probes change finite coordinates and recompute checksums |
| Tiny weights could hide large coordinate errors behind small absolute force | High | Additional force divided by exposed weighted degree must converge; tiny-weight solver/load negative controls |
| Invalid sweep types, mutable containers, overflow and malformed artifacts lacked one reliable contract | High | Typed immutable observations, strict settings and SHA256 identity, transactional rejection, unified `ValueError` artifact errors and finite receipts |
| Fresh failed queries lost the `NOT_CONVERGED` reason | Medium | Preserve typed last-attempt failure when no committed state exists; preceding committed geometry remains queryable after rejected updates |
| Final evaluation omitted noisy data and did not guarantee every hidden edge was queried | High | New R002 generator/manifest, noisy arm, all eight hidden redundant edges in each indirect panel, disjoint new world seeds |
| Relation-ID/vector manifest was absent | Medium | Public per-world opaque relation catalogue checked at the owning boundary; no hidden-only vectors included; consistent renaming fixture |
| Baseline coverage without total/conditional accuracy obscured comparisons | High | All methods report each metric; direct-pair diagnostics alongside indirect queries; noisy truth and least-squares endpoints kept separate |
| Evaluator trusted candidate-reported energy and had weak negative controls | High | Independently compute energy from committed answers; inject wrong predictions and generation failures to prove detection |
| Evidence was overwritten on replay and lost on exceptions; hashes were captured only after execution | High | Refuse completed output, stream/flush every world, retain infrastructure failures, capture source before/after and archive actual bytes |
| Work counts omitted scans and learn timing excluded commit | Medium | Detailed preprocessing/dynamics/global-scan counters and full transaction timing; paired cost intervals; anchor selection is one component traversal |
| Original source was not archived | Medium | Preserve historical receipts honestly; no claim that R001 can be replayed from hashes alone. R002 has a complete source snapshot |

The reviewed repair batch's first test run produced 43 passes and 13 failures: newly selected anchors retained NumPy integer types, preventing JSON export. `contracts_initial_failure.xml` preserves the actual failures. Anchors are now serialized as Python integers. The final expanded suite passed **57 tests in 9.95 seconds**; `contracts.xml` is its actual report. Neither check run used R002 final-world results to select settings.

Fresh R002 world verification is pending. Current status: **ACTIVE**, until all registered gates are reached. C1–C8, recursive resonators, tactical integration, browser rendering, C++ porting and hardware energy are NOT_RUN.

A universal 9/10 or 10/10 claim is unsupported: this is a bounded C0 reference experiment. Clean offset reconstruction has a much cheaper compiled-coordinate solution. The purpose here is a trustworthy instrument for the later learning/hierarchy experiments, with correctness, cost and scientific claims kept separate.
