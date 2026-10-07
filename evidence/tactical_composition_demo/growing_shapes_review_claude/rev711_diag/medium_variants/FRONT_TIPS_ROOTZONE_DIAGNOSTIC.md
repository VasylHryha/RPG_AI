DONE

Stored-data-only diagnostic: 50 observer-on runs, RD3/COV-A/COV-B/CAP96/CAP128 × starts i/ii × keys 0–4; 8,000 stored 5 s figures (5..800 s), including 2,000 post-growth 20 s checks (20..800 s). One worker (nice request unavailable), standard-library arithmetic; no simulation, native loading, pilot, policy replay, or changes to existing evidence. Complete for the requested sampled discriminants; continuous histories and changed-law outcomes are unavailable. Base HEAD: `b2f0ac1bcf18696550d280d34c5c9d565e681b33`.

Definitions declared before computation. Reuses `analyze_front_allocation.py` for directed reachability, verified decoding conventions and conserved endpoint allocation. Physical sites are the eight radius-4 positions. Roots are unsilenced positive-gain ordinary bodies at strict distance <3, including idle physical sites. O role comes from seeded ID 6 or retained B-out birth events. Exact gains/silence are absent from legacy figures: eligibility follows the pinned live harness (gain=1 birth, positive convex adaptation, reward disabled, no live silencing); this is a source-supported inference, not decoded gain-state values. All stored strong edges, all-site figure service, growth-end cost, prior front totals and CAP class totals are crosschecked.

Strong edges are source→receiver with coefficient 32 exp(−r²)/held_receiver_degree >= .5. H is backward reachability from O; F_s is forward reachability from site s roots. Its front is F_s minus H and O. Cost = one per ordinary body + .1 per undirected ordinary held pair (union of strict-radius-3 k=8 selections); O participates in neighbor selection/degree but O and incident pairs are free. Split pair cost .05 to each endpoint. Front endpoint cost is split equally among ALL sites whose F_s contains that body, including served/idle owners. This conserves cost; active-unserved selections use only their fractional shares.

A tip is a front body with no strong out-neighbour in that same site front strictly closer to O (minimum Euclidean distance to any present O). No output means undefined, separately counted; an empty front with O has zero tips. Equal-distance edges do not disqualify tips. For a deterministic subtree, each body chooses its strictly closer strong neighbour minimizing (distance-to-O, ID), then follows to a sink. The strictly decreasing forest is acyclic and partitions the front; it is a diagnostic ownership convention, not a recorded sponsor tree. The best tip minimizes (distance to H, distance to O, ID), matching the B-path gap objective more closely than radial rank alone. Best subtree versus rest conserves each site’s allocated front cost. Sensitivity splits each body equally among all tips reachable through strictly decreasing strong edges; it is reported separately.

Meaningful gap progress = decrease of at least .556 model length units, the pinned in-phase placement R_STAR. Gap of a tip is its minimum Euclidean distance to H; O belongs to H. Tip persistence means the SAME body ID remains a tip of the SAME active-unserved site at consecutive sampled endpoints. Report 5 s and 20 s separately; no continuous persistence or intervening eligibility is assumed. Per-pair progress compares endpoint gaps. Spells also track cumulative progress against the initial/last-quantum anchor (not reset for small numerical improvements); span = last minus first observed time. A moving H can change gap without tip motion; identity turnover can carry progress to a child. Initial spells are left-limited by sampling; final spells are right-censored. Persistence pools sole and competing tips: it is not a stalled competing-lineage frequency, because growth may transfer progress to a new child ID or another tip.

Tip distributions below use only active-unserved site/figure or site/growth-end observations WITH O; zero fronts remain in the denominator. Histograms are tips:count. Cost shares pool sums; they are not averages of ratios.

5 s figures

| Arm | Active unserved / no O | Defined denominator | Tip histogram | Mean tips | >=2 tips | >=2 in one component | Best / rest owned cost | Alternate best share |
|---|---:|---:|---|---:|---:|---:|---|---:|
| RD3 | 6499 / 84 | 6415 | {'0': 1206, '1': 2988, '2': 2097, '3': 122, '4': 2} | 1.178 | 34.62% | 2.45% | 76.81% / 23.19% | 76.77% |
| COVA | 6935 / 84 | 6851 | {'0': 1255, '1': 3503, '2': 1970, '3': 123} | 1.140 | 30.55% | 2.09% | 83.27% / 16.73% | 83.18% |
| COVB | 6067 / 84 | 5983 | {'0': 1279, '1': 3300, '2': 1281, '3': 121, '4': 2} | 1.042 | 23.47% | 1.70% | 80.77% / 19.23% | 80.56% |
| CAP96 | 5228 / 84 | 5144 | {'0': 1146, '1': 2214, '2': 1592, '3': 187, '4': 5} | 1.162 | 34.68% | 2.76% | 74.31% / 25.69% | 74.06% |
| CAP128 | 4918 / 84 | 4834 | {'0': 1146, '1': 2032, '2': 1406, '3': 246, '4': 4} | 1.158 | 34.26% | 3.08% | 74.50% / 25.50% | 74.17% |

20 s growth-end checks

| Arm | Active unserved / no O | Defined denominator | Tip histogram | Mean tips | >=2 tips | >=2 in one component | Best / rest owned cost | Alternate best share |
|---|---:|---:|---|---:|---:|---:|---|---:|
| RD3 | 1582 / 0 | 1582 | {'0': 287, '1': 716, '2': 543, '3': 36} | 1.207 | 36.60% | 2.84% | 76.65% / 23.35% | 76.67% |
| COVA | 1719 / 0 | 1719 | {'0': 299, '1': 862, '2': 521, '3': 37} | 1.172 | 32.46% | 2.39% | 82.81% / 17.19% | 82.77% |
| COVB | 1444 / 0 | 1444 | {'0': 302, '1': 796, '2': 313, '3': 33} | 1.053 | 23.96% | 1.80% | 81.59% / 18.41% | 81.41% |
| CAP96 | 1209 / 0 | 1209 | {'0': 270, '1': 518, '2': 377, '3': 43, '4': 1} | 1.162 | 34.82% | 2.81% | 75.47% / 24.53% | 75.20% |
| CAP128 | 1096 / 0 | 1096 | {'0': 270, '1': 468, '2': 316, '3': 42} | 1.119 | 32.66% | 2.46% | 78.51% / 21.49% | 78.28% |

| Arm/spacing | Previous tip opportunities | Same-ID persistent | No .556 progress / persistent | >=60s spells with zero cumulative quantum / all >=60s spells | Max sampled no-quantum span |
|---|---:|---:|---:|---:|---:|
| RD3/5s | 7498 | 5924 | 5915 / 5924 (99.85%) | 117 / 117 | 170s |
| RD3/20s | 1852 | 830 | 827 / 830 (99.64%) | 103 / 106 | 200s |
| COVA/5s | 7752 | 6150 | 6144 / 6150 (99.90%) | 132 / 133 | 220s |
| COVA/20s | 1955 | 884 | 880 / 884 (99.55%) | 126 / 128 | 200s |
| COVB/5s | 6196 | 4533 | 4519 / 4533 (99.69%) | 44 / 44 | 155s |
| COVB/20s | 1484 | 437 | 433 / 437 (99.08%) | 36 / 39 | 140s |
| CAP96/5s | 5941 | 4370 | 4352 / 4370 (99.59%) | 51 / 54 | 180s |
| CAP96/20s | 1367 | 466 | 457 / 466 (98.07%) | 47 / 50 | 180s |
| CAP128/5s | 5588 | 3920 | 3893 / 3920 (99.31%) | 28 / 30 | 140s |
| CAP128/20s | 1216 | 325 | 317 / 325 (97.54%) | 28 / 32 | 180s |

Root-zone geometry: bins use each BODY’s nearest physical-site distance, independent of ownership. Narrow roots use strict distance <1.44; the exact degree-8 strong range is sqrt(log(8)) = 1.4420268866, so 1.44 is the requested rounded geometric threshold, not a universal edge bound. Keep all stored positions, held edges, strong edges and H fixed. Union loss is front cost outside the UNION of narrowed F_s. Allocated-site loss instead counts each existing fractional owner whose narrowed F_s no longer reaches that body; other sites can still reach it. Outside-zone cost is not necessarily union loss because strong chains can remain reachable.

This is a PURE RECLASSIFICATION ON STORED GEOMETRY. It is NOT a counterfactual of a changed sensing law: narrowing the sensor root zone also changes sensor phase drive, dynamics, growth, degree and service. No lost root-reachable cost is assumed safely recyclable or saved.

all_5s (late means t>640 s)

| Arm | Mean front cost | <1.44 | 1.44–3 | >=3 | Union reach lost: mean / % front | Allocated-site reach lost: mean / % front |
|---|---:|---:|---:|---:|---|---|
| RD3 | 28.961 | 96.97% | 3.03% | 0.00% | 0.037 / 0.13% | 17.449 / 60.25% |
| COVA | 32.355 | 97.19% | 2.81% | 0.00% | 0.036 / 0.11% | 19.891 / 61.48% |
| COVB | 23.987 | 97.08% | 2.92% | 0.00% | 0.028 / 0.12% | 14.376 / 59.93% |
| CAP96 | 28.225 | 96.61% | 3.39% | 0.00% | 0.024 / 0.08% | 16.779 / 59.45% |
| CAP128 | 26.732 | 96.39% | 3.61% | 0.00% | 0.024 / 0.09% | 15.808 / 59.13% |

growth_end_20s (late means t>640 s)

| Arm | Mean front cost | <1.44 | 1.44–3 | >=3 | Union reach lost: mean / % front | Allocated-site reach lost: mean / % front |
|---|---:|---:|---:|---:|---|---|
| RD3 | 28.572 | 96.34% | 3.66% | 0.00% | 0.053 / 0.19% | 17.092 / 59.82% |
| COVA | 32.881 | 96.29% | 3.71% | 0.00% | 0.049 / 0.15% | 20.141 / 61.25% |
| COVB | 22.355 | 95.96% | 4.04% | 0.00% | 0.042 / 0.19% | 13.361 / 59.76% |
| CAP96 | 26.469 | 95.74% | 4.26% | 0.00% | 0.041 / 0.15% | 15.565 / 58.81% |
| CAP128 | 23.670 | 95.09% | 4.91% | 0.00% | 0.041 / 0.17% | 13.769 / 58.17% |

late_5s (late means t>640 s)

| Arm | Mean front cost | <1.44 | 1.44–3 | >=3 | Union reach lost: mean / % front | Allocated-site reach lost: mean / % front |
|---|---:|---:|---:|---:|---|---|
| RD3 | 37.688 | 98.63% | 1.37% | 0.00% | 0.056 / 0.15% | 23.612 / 62.65% |
| COVA | 40.241 | 98.60% | 1.40% | 0.00% | 0.013 / 0.03% | 25.202 / 62.63% |
| COVB | 26.222 | 98.52% | 1.48% | 0.00% | 0.010 / 0.04% | 16.245 / 61.95% |
| CAP96 | 35.094 | 97.89% | 2.11% | 0.00% | 0.000 / 0.00% | 21.360 / 60.87% |
| CAP128 | 28.698 | 97.51% | 2.49% | 0.00% | 0.000 / 0.00% | 17.245 / 60.09% |

Per physical site at 20 s growth-end checks (all starts/keys). Mean front/lost-site costs include idle/served checks; tip histogram and best/rest select active-unserved checks with O.

| Arm/site | Defined / no O | Tip histogram | Best / rest cost sums | Mean front / lost-site reach | Old / narrowed structurally served checks |
|---|---:|---|---|---|---:|
| RD3/0 | 126 / 0 | {'0': 9, '1': 53, '2': 61, '3': 3} | 453.10 / 182.32 | 3.725 / 1.953 | 199 / 134 |
| RD3/1 | 93 / 0 | {'0': 3, '1': 47, '2': 39, '3': 4} | 373.71 / 173.20 | 4.144 / 3.207 | 254 / 68 |
| RD3/2 | 172 / 0 | {'0': 27, '1': 65, '2': 78, '3': 2} | 690.17 / 240.93 | 4.626 / 2.604 | 150 / 84 |
| RD3/3 | 240 / 0 | {'0': 37, '1': 118, '2': 74, '3': 11} | 976.51 / 222.75 | 4.574 / 2.226 | 89 / 13 |
| RD3/4 | 273 / 0 | {'0': 60, '1': 106, '2': 102, '3': 5} | 699.62 / 247.30 | 3.537 / 2.649 | 12 / 5 |
| RD3/5 | 280 / 0 | {'0': 59, '1': 189, '2': 32} | 525.43 / 63.13 | 1.871 / 0.850 | 33 / 2 |
| RD3/6 | 239 / 0 | {'0': 71, '1': 78, '2': 88, '3': 2} | 471.17 / 142.94 | 2.545 / 1.888 | 38 / 30 |
| RD3/7 | 159 / 0 | {'0': 21, '1': 60, '2': 69, '3': 9} | 560.17 / 174.54 | 3.550 / 1.716 | 172 / 11 |
| COVA/0 | 149 / 0 | {'0': 10, '1': 81, '2': 56, '3': 2} | 719.12 / 111.15 | 5.336 / 2.293 | 168 / 9 |
| COVA/1 | 159 / 0 | {'0': 3, '1': 99, '2': 50, '3': 7} | 756.52 / 173.76 | 4.287 / 3.350 | 159 / 64 |
| COVA/2 | 145 / 0 | {'0': 29, '1': 79, '2': 37} | 382.77 / 116.94 | 2.985 / 2.262 | 196 / 85 |
| COVA/3 | 207 / 0 | {'0': 37, '1': 119, '2': 49, '3': 2} | 752.64 / 86.62 | 3.204 / 1.274 | 132 / 47 |
| COVA/4 | 243 / 0 | {'0': 66, '1': 71, '2': 90, '3': 16} | 768.94 / 321.84 | 4.101 / 2.800 | 55 / 1 |
| COVA/5 | 295 / 0 | {'0': 73, '1': 146, '2': 73, '3': 3} | 859.10 / 223.61 | 3.471 / 1.749 | 8 / 7 |
| COVA/6 | 256 / 0 | {'0': 60, '1': 135, '2': 58, '3': 3} | 842.91 / 131.41 | 3.836 / 2.647 | 7 / 0 |
| COVA/7 | 265 / 0 | {'0': 21, '1': 132, '2': 108, '3': 4} | 1361.78 / 172.04 | 5.661 / 3.766 | 17 / 2 |
| COVB/0 | 120 / 0 | {'0': 9, '1': 67, '2': 43, '3': 1} | 438.57 / 161.03 | 3.093 / 1.437 | 208 / 149 |
| COVB/1 | 92 / 0 | {'0': 6, '1': 52, '2': 32, '3': 2} | 331.31 / 148.41 | 2.780 / 2.060 | 255 / 84 |
| COVB/2 | 126 / 0 | {'0': 30, '1': 52, '2': 41, '3': 3} | 375.13 / 95.83 | 2.931 / 1.990 | 213 / 132 |
| COVB/3 | 196 / 0 | {'0': 43, '1': 110, '2': 31, '3': 12} | 627.86 / 144.65 | 2.976 / 1.154 | 152 / 35 |
| COVB/4 | 254 / 0 | {'0': 60, '1': 128, '2': 59, '3': 7} | 650.34 / 161.98 | 3.306 / 2.500 | 35 / 9 |
| COVB/5 | 276 / 0 | {'0': 68, '1': 177, '2': 31} | 570.27 / 49.24 | 2.021 / 0.767 | 38 / 3 |
| COVB/6 | 232 / 0 | {'0': 65, '1': 126, '2': 40, '3': 1} | 489.59 / 50.29 | 2.314 / 1.872 | 45 / 30 |
| COVB/7 | 148 / 0 | {'0': 21, '1': 84, '2': 36, '3': 7} | 512.32 / 90.32 | 2.935 / 1.582 | 187 / 28 |
| CAP96/0 | 103 / 0 | {'0': 9, '1': 41, '2': 46, '3': 7} | 425.06 / 148.23 | 3.825 / 2.069 | 231 / 153 |
| CAP96/1 | 72 / 0 | {'0': 3, '1': 43, '2': 25, '3': 1} | 289.71 / 58.44 | 3.148 / 2.199 | 277 / 91 |
| CAP96/2 | 109 / 0 | {'0': 27, '1': 39, '2': 41, '3': 2} | 342.66 / 94.43 | 2.798 / 1.769 | 243 / 154 |
| CAP96/3 | 149 / 0 | {'0': 37, '1': 76, '2': 29, '3': 7} | 459.78 / 58.15 | 2.687 / 1.096 | 213 / 112 |
| CAP96/4 | 184 / 0 | {'0': 60, '1': 41, '2': 69, '3': 13, '4': 1} | 424.07 / 322.35 | 3.769 / 2.771 | 130 / 13 |
| CAP96/5 | 260 / 0 | {'0': 58, '1': 158, '2': 41, '3': 3} | 683.95 / 96.63 | 2.848 / 0.988 | 56 / 23 |
| CAP96/6 | 194 / 0 | {'0': 55, '1': 66, '2': 72, '3': 1} | 437.61 / 248.44 | 3.654 / 2.906 | 98 / 36 |
| CAP96/7 | 138 / 0 | {'0': 21, '1': 54, '2': 54, '3': 9} | 567.98 / 153.64 | 3.740 / 1.769 | 207 / 60 |
| CAP128/0 | 87 / 0 | {'0': 9, '1': 39, '2': 36, '3': 3} | 360.55 / 101.76 | 3.343 / 1.632 | 253 / 159 |
| CAP128/1 | 68 / 0 | {'0': 3, '1': 41, '2': 23, '3': 1} | 274.63 / 55.34 | 3.013 / 2.143 | 285 / 100 |
| CAP128/2 | 105 / 0 | {'0': 27, '1': 39, '2': 37, '3': 2} | 324.46 / 86.18 | 2.527 / 1.538 | 247 / 162 |
| CAP128/3 | 143 / 0 | {'0': 37, '1': 67, '2': 31, '3': 8} | 410.08 / 76.77 | 2.298 / 0.888 | 220 / 131 |
| CAP128/4 | 163 / 0 | {'0': 60, '1': 41, '2': 54, '3': 8} | 298.78 / 161.47 | 3.373 / 2.580 | 157 / 41 |
| CAP128/5 | 237 / 0 | {'0': 58, '1': 147, '2': 30, '3': 2} | 593.64 / 64.88 | 2.593 / 0.763 | 87 / 35 |
| CAP128/6 | 166 / 0 | {'0': 55, '1': 53, '2': 52, '3': 6} | 300.82 / 144.90 | 3.249 / 2.513 | 129 / 41 |
| CAP128/7 | 127 / 0 | {'0': 21, '1': 41, '2': 53, '3': 12} | 508.16 / 149.10 | 3.273 / 1.712 | 220 / 99 |

C. Service-supported redundancy. A redundant body supports site s if it lies in F_s ∩ H: it is on some directed root→O walk, not necessarily a simple/shortest route. Split cost equally among those supporting sites (all are structurally served; idle included). “Far” here is the owner-requested labels 3–6; “near” is 0–2,7. These labels are relative to the seeded side, NOT radial physical-site distance (all sites have radius 4). JSON gives each site, active-only portions with the same ownership denominator, starts, runs and shared-group buckets.

| Arm/window | Mean redundant cost | Far 3–6 | Near 0–2,7 | Far-only / near-only / shared bodies cost |
|---|---:|---:|---:|---|
| RD3/all_5s | 17.519 | 2.903 | 14.617 | 0.000 / 10.401 / 7.118 |
| CAP96/all_5s | 30.478 | 10.356 | 20.121 | 0.043 / 4.431 / 26.004 |
| CAP128/all_5s | 34.909 | 12.983 | 21.926 | 0.043 / 4.334 / 30.532 |
| RD3/late_5s | 23.775 | 4.128 | 19.647 | 0.000 / 12.127 / 11.648 |
| CAP96/late_5s | 56.753 | 22.470 | 34.283 | 0.000 / 0.135 / 56.618 |
| CAP128/late_5s | 76.173 | 33.991 | 42.182 | 0.000 / 0.135 / 76.038 |

| Capacity versus RD3/window | Extra redundant cost | Far-supported increment / share | Near-supported increment / share |
|---|---:|---|---|
| CAP96/all_5s | 12.959 | 7.454 / 57.52% | 5.505 / 42.48% |
| CAP128/all_5s | 17.389 | 10.080 / 57.97% | 7.309 / 42.03% |
| CAP96/late_5s | 32.978 | 18.342 / 55.62% | 14.636 / 44.38% |
| CAP128/late_5s | 52.398 | 29.863 / 56.99% | 22.535 / 43.01% |

The extra redundant cost is slightly more far-supported than near-supported: 55.62%/56.99% of the late CAP96/CAP128 increment is fractionally attributed to sites 3–6. Almost all late CAP redundancy supports BOTH groups (56.618 of 56.753 and 76.038 of 76.173 cost units). Thus it is shared service-connected material, not a collection of exclusively far routes or near-only waste. Cost support is structural, not a measure of causal signal delivery; the start-specific service table below preserves starvation.

| Arm/start | Site 3 | 4 | 5 | 6 | Runs with any zero-service site |
|---|---:|---:|---:|---:|---:|
| RD3/i | 0.178567 | 0.000000 | 0.000000 | 0.010008 | 5/5 |
| RD3/ii | 0.199313 | 0.038771 | 0.115746 | 0.132094 | 5/5 |
| CAP96/i | 0.486715 | 0.214286 | 0.000000 | 0.090721 | 5/5 |
| CAP96/ii | 0.454614 | 0.303194 | 0.200345 | 0.305253 | 3/5 |
| CAP128/i | 0.486715 | 0.213736 | 0.000242 | 0.187232 | 4/5 |
| CAP128/ii | 0.479221 | 0.375034 | 0.295407 | 0.332554 | 1/5 |

Limits: sampled endpoint multiplicity/persistence and a forest partition do not identify accepted sponsors or causally wasted branches. Strong out-neighbour minima can include shared-root blobs, sideways growth and phase-sensitive material; the B-path search considers up to eight pairs, without persistent tip authority. Forest remainder is not a predicted saving; shared-site ownership can overlap the proposed per-site intervention. Gap changes are observational and include moving H. No missing pre-growth deleted positions are inferred. The narrow-zone reclassification can erase existing service support; it cannot predict improved service under modified sensing. Resource arms combine admission headroom with delayed D3 retention; cross-arm extra redundancy is a mean difference, not tracking the same bodies across changed trajectories. Source evidence and existing verdicts are preserved.

What this says for W8: conditional on the proposed FRONT-MASS-RELEASE rationale, rank (A) one-active-front authority ahead of (B) narrower sensor roots. At 20 s, competing subtrees own 17.19–24.53% of active-unserved allocated front cost (RD3 23.35%). However hidden multiplicity within a single component occurs in only 1.80–2.84% of these site/checks: this does not overturn the earlier finding that one-front authority targets a minority of the front tax. Narrowing roots has little stored mass-release premise: 96.39–97.19% of full-time front cost is ALREADY within 1.44 of a physical site, and union reach loss is only 0.08–0.13%. The much larger roughly 59–61% original-owner reach loss changes which sites support shared mass; it does not free those bodies. That large reassignment leaves possible changes in cross-site sponsorship and phase interference unresolved, so it does not support a general ranking of dynamic benefits. This ranks a bounded tip-authority investigation above narrower roots as an efficiency target, without predicting benefit. Narrower sensing could still change phase dynamics, which this analysis cannot assess. Ceiling 96 remains the measured practical fallback: extra service redundancy supports far labels as well as near labels, overwhelmingly through shared material, but site 5 still has zero empty-start service. No adoption, new law or experiment is authorized.

Integrity and reproduction: all 221 retained inventory entries checked for sizes/SHA256 before decoding; all 50 complete slots, 8,000 directed strong graphs, sampled all-site service and 2,000 growth-end costs checked. CAP front/redundant totals match the retained class samples, and RD3/COV-A/COV-B front totals match the prior diagnostic. Compact JSON includes per-arm, per-start, per-run and per-site denominators; raw per-snapshot forest tip costs, gap spells and transitions stay in gitignored `_local/front_tips_rootzone/`. Reproduce with `python3 evidence/tactical_composition_demo/growing_shapes_review_claude/rev711_diag/medium_variants/analyze_front_tips_rootzone.py` (one worker). JSON size <5 MB.

Separate Codex owner recheck request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Recheck/disposition tracking is in these new artifacts because the owner prohibits editing existing files, including docs/PLAN_CURRENT.md. Review state: PASS_WITH_NOTES. This is a same-family stored-data recheck, not experimental/scientific acceptance.

Focused arithmetic validation: PASS — cumulative sub-quantum progress, regression, ID turnover, inactive interruption, and no-output/service interruption; source preservation and output shape checked. No project suite or native code was run.

Separate reviewer record: `_local/front_tips_rootzone/REVIEW_CODEX.md`, SHA256 `cbd884b89435c7fade293b4f15498bb82594234ed78ec28b1a706fc080e4bf03`. Reviewer independently checked all 50 derived identities, all 8,000 allocation/election figures, arm totals/histograms and both persistence recounts; reconstructed 15 original snapshots across five arms and both starts. Original reviewed draft hashes and detailed dispositions are retained in that record.

N1 fixed: persistence pools sole and competing tips and measures endpoint body identity, not stalled competing lineages. N2 fixed: A>B is conditional on front-mass release; roughly 60% ownership reassignment leaves sponsorship and phase interference unresolved, so changed-law benefit is not ranked. Reviewer confirmed both dispositions. Final follow-up confirmed the relative-import render path correction; reviewer corrected its own stationary-body wording. No arithmetic correction, full analysis rerun, new experimental run, or unresolved finding. Main .git is read-only; the three requested files are uncommitted and nothing is staged. Existing PLAN_CURRENT is neither edited nor staged.
