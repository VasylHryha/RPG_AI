PARTIAL

Stored-data mass-budget diagnostic; reviewed commit `e4c6d75d348731d707a1f7dab16250c6a396dc43`. No pilots, medium runs, economy-rule runs, or assay replays.

The stored figures support a complete snapshot allocation, but only sampled residence and last-observed birth classes. Exact continuous residence and orphan/front class at deletion are unavailable; survivor fates are censored. PARTIAL names these limits, not missing trajectories.

An explicit two-node-per-spoke star checks the approximate 22-unit claim using the real k=8/radius-3 held graph and O exemption:

| Start/spoke spacing | Ordinary N | Charged held pairs | Weighted cost | Structurally served sites |
|---|---:|---:|---:|---|
| i/0.556 | 16 | 64 | 22.4 | [0, 1, 2, 3, 4, 5, 6, 7] |
| ii/0.556 | 16 | 64 | 22.4 | [2, 3, 4, 5, 6] |
| i/0.8 | 16 | 64 | 22.4 | [0, 1, 2, 3, 4, 5, 6, 7] |
| ii/0.8 | 16 | 64 | 22.4 | [0, 1, 2, 3, 4, 5, 6, 7] |

Coordinates and root counts are in JSON. Each spoke places two ordinary bodies at one and two times the stated spacing from O toward the fixed sensor site. The .556-spacing estimate costs 22.4 but fails three seeded roots; spacing .8 reaches all eight sites in both starts at the same 22.4 cost (16 bodies + .1 × 64 charged pairs). All static clearances pass .05 for elements and .3 for sites. Cost is N + .1 times ordinary undirected held pairs; O participates in k-nearest selection and receiver degree but O and incident pairs are free. A sparse drawn star still pays cross-spoke proximity pairs. Strong edges use 32 exp(−r²)/full held receiver degree ≥ .5 s⁻¹. No project code is imported.

This is a static structural feasibility illustration, not a constructive growth path, minimum-cost proof, stable dynamic solution, all-site temporal coverage, or A/B/E witness. Seeded O is offset, which requires checking actual sensor-root distances rather than reusing an origin-centered drawing. Thus cheap static geometry alone does not prove the actual controller can achieve/retain service.

Snapshot classification follows RD3 using all eight physical sites, including idle sites. Critical bodies individually preserve at least one served site; redundant bodies are on the forward/backward reachability intersection but individually dispensable; fronts are forward reachable without an output route; orphans are unreachable from every site’s roots. Every ordinary element belongs to exactly one class. Near-O radii are overlays. Each pair’s .1 cost splits equally across endpoints, including mixed-class pairs; this is allocation, not deletion savings.

| Arm/class | Mean elements | Mean pair cost | Mean total cost | Share of arm cost |
|---|---:|---:|---:|---:|
| RD3/critical | 1.008 | 0.446 | 1.454 | 3.0% |
| RD3/redundant | 11.774 | 5.745 | 17.519 | 36.4% |
| RD3/front | 20.835 | 8.126 | 28.961 | 60.1% |
| RD3/orphan | 0.194 | 0.055 | 0.249 | 0.5% |
| COVA/critical | 0.619 | 0.245 | 0.864 | 1.8% |
| COVA/redundant | 9.693 | 4.584 | 14.277 | 30.0% |
| COVA/front | 22.905 | 9.450 | 32.355 | 68.0% |
| COVA/orphan | 0.082 | 0.016 | 0.098 | 0.2% |
| COVB/critical | 1.262 | 0.562 | 1.825 | 3.8% |
| COVB/redundant | 14.977 | 7.210 | 22.187 | 46.1% |
| COVB/front | 17.339 | 6.648 | 23.987 | 49.8% |
| COVB/orphan | 0.126 | 0.034 | 0.161 | 0.3% |

Means equally weight 160 post-growth snapshots per run and ten runs per arm. The JSON retains every 5 s point, cross-class pair matrix, full-time and late (>640 s) allocation per run, radii <1/<3 near O, per-element sampled residence/maximal observed spells, exact event lifetimes and censoring, and class-spell distributions. A 5 s spell means one observed sample; intermediate switches are unknown.

| Arm | New births | Deleted births | Last sampled orphan | Last sampled redundant |
|---|---:|---:|---:|---:|
| RD3 | 449 | 32 | 0.9% | 32.3% |
| COVA | 447 | 35 | 0.0% | 34.5% |
| COVB | 654 | 238 | 0.3% | 38.2% |

These fractions count last observed classes over all new births, including right-censored survivors. They must not be read as exact fractions ending in those classes. Exact pre-removal service-class counts and missing-sample births are in JSON; recorded non-service removals cannot retrospectively distinguish fronts and orphans.

Fronts hold the largest average cost in every arm: RD3 28.961/48.183 = 60.1%; COV-A 32.355/47.595 = 68.0%; COV-B 23.987/48.159 = 49.8%. Redundant mass is the second-largest allocation (36.4%, 30.0%, 46.1% respectively); orphan allocation is only 0.52%, 0.21%, 0.33%. Orphan-only cleanup therefore has little observed headroom to recover. These full-time means hide a change near capacity: late RD3 and COV-A still allocate most cost to fronts (37.688 and 40.241 units), while late COV-B allocates most to redundancy (34.523 units versus 26.222 fronts). Cost>=63 snapshots show the same switch: fronts 37.823/41.529 for RD3/COV-A, redundancy 32.908 for COV-B. The potential economy target is therefore unfinished reachable growth for RD3/COV-A and service redundancy for cost-limited COV-B. Front/orphan allocation is presently outside service; redundant allocation is individually removable in the current strong graph. Neither establishes causal waste: fronts can become routes, redundant elements alter degree and protect against future losses, orphans can return as geometry moves. A rule deleting several individually dispensable bodies can destroy service after the first deletion.

| Smallest single task-blind candidate | Evidence to consult | Expected trade-offs |
|---|---|---|
| Remove an orphan only after continuous orphanhood T (low-yield alternative) | Orphan allocation is below .6% in each arm; sampled spells describe the small target; choose T prospectively, continuous persistence cannot be certified here | Releases unrooted mass; can erase dormant future roots/routes; proximity rewiring may offset pair savings; recompute after each removal |
| Thin one service-redundant body per check only after testing the prospective post-deletion all-site graph | Redundant allocation and spells, exact recorded redundant removals | Frozen-graph redundant labels do not guarantee service after nearest-neighbor rewiring and degree changes. A prospective graph check can preserve instant service; dynamics and resilience remain at risk; reclassify every next donor |
| Add a persistence cost for front bodies | Front allocation and residence quantify unfinished route investment | Encourages completion rather than accumulating fronts; can penalize precisely the difficult sites needing longer construction and worsen fairness |
| Charge age-weighted orphan occupancy in admission | Orphan cost share, avoiding a task-specific signal | Discourages carrying long-unrooted bodies; does not itself free capacity and can further block births; class transitions invite oscillation |

Prioritize investigating a single persistence rule for fronts or a sequential redundancy thinning rule. Orphan deletion has little numerical support as the main budget remedy. These alternatives stand alone and are evidence-supported targets, not validated improvements. No threshold T, combined mechanism, tuned penalty, or future run is authorized by this diagnostic. Keep physical sites/graph/age as inputs; no tasks, scores, assay results, or learned site preferences.

Integrity: all 157 raw inventory sizes/SHA256 verified before decoding. All 30 trajectories have 8000 world boundaries and 160 figures; figure service/root existence and coincident growth cost are checked. Costs conserve across four classes. Hash manifest explicitly excludes docs/PLAN_CURRENT.md.

Separate Part 2 owner recheck requested verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Recheck disposition: see docs/reviews/tactical_0h_mass_budget_recheck_codex.md; the separate available reviewer is Codex (same family as this analyst), not Claude cross-family acceptance. Fixed recheck findings: named/quantified waste by arm and late period; added per-run residence/fate/near-O tables and censoring; tested the offset-O star; pinned actual retained cost/geometry/gain sources; stated that deletion needs a prospective graph check because neighbors and degrees rewire. Plan tracking lives here under the owner’s prohibition on editing docs/PLAN_CURRENT.md.

Budget near the binding limit. Late means t>640 s; near-cap snapshots mean cost>=63 (within one unit of capacity64), a descriptive selection. Values are mean class cost, not marginal reclaimable units.

| Arm/period | Samples | Mean cost | Critical | Redundant | Front | Orphan |
|---|---:|---:|---:|---:|---:|---:|---:|
| RD3/late | 320 | 63.413 | 1.477 | 23.775 | 37.688 | 0.473 |
| RD3/cost_at_least_63 | 662 | 63.618 | 1.686 | 23.761 | 37.823 | 0.348 |
| COVA/late | 320 | 63.308 | 1.122 | 21.945 | 40.241 | 0.000 |
| COVA/cost_at_least_63 | 561 | 63.635 | 1.018 | 21.088 | 41.529 | 0.000 |
| COVB/late | 320 | 63.365 | 2.417 | 34.523 | 26.222 | 0.203 |
| COVB/cost_at_least_63 | 656 | 63.552 | 2.401 | 32.908 | 28.063 | 0.179 |

Per-run mean allocation (C=critical, R=redundant, F=front, U=orphan; each cell elements + pair cost = total). The full 5 s cost series is in JSON.

| Run | C | R | F | U | Near O <1 / <3, mean total cost |
|---|---|---|---|---|---|
| RD3/i/k0 | 0.90 + 0.37 = 1.27 | 12.38 + 6.61 = 18.99 | 18.84 + 7.05 = 25.89 | 0.00 + 0.00 = 0.00 | 1.99 / 5.36 |
| RD3/i/k1 | 0.99 + 0.40 = 1.38 | 12.78 + 6.21 = 18.99 | 18.84 + 6.88 = 25.72 | 0.00 + 0.00 = 0.00 | 1.90 / 4.52 |
| RD3/i/k2 | 0.91 + 0.44 = 1.35 | 14.05 + 6.93 = 20.98 | 16.74 + 5.95 = 22.70 | 0.00 + 0.00 = 0.00 | 2.78 / 7.17 |
| RD3/i/k3 | 1.38 + 0.52 = 1.90 | 8.89 + 4.22 = 13.10 | 22.18 + 9.31 = 31.49 | 0.00 + 0.00 = 0.00 | 2.03 / 7.94 |
| RD3/i/k4 | 1.54 + 0.67 = 2.22 | 11.07 + 5.35 = 16.41 | 19.23 + 7.70 = 26.94 | 0.00 + 0.00 = 0.00 | 2.09 / 5.13 |
| RD3/ii/k0 | 1.48 + 0.54 = 2.02 | 13.61 + 7.23 = 20.84 | 19.91 + 7.44 = 27.36 | 0.36 + 0.07 = 0.43 | 2.35 / 9.71 |
| RD3/ii/k1 | 0.28 + 0.12 = 0.40 | 20.13 + 9.31 = 29.44 | 14.98 + 5.46 = 20.45 | 0.00 + 0.00 = 0.00 | 2.19 / 10.06 |
| RD3/ii/k2 | 1.48 + 0.83 = 2.31 | 7.67 + 3.40 = 11.07 | 26.49 + 9.99 = 36.49 | 0.34 + 0.08 = 0.42 | 2.28 / 7.68 |
| RD3/ii/k3 | 0.23 + 0.10 = 0.33 | 0.89 + 0.40 = 1.28 | 31.71 + 14.26 = 45.97 | 1.24 + 0.40 = 1.64 | 1.88 / 3.75 |
| RD3/ii/k4 | 0.90 + 0.47 = 1.37 | 16.27 + 7.81 = 24.09 | 19.41 + 7.20 = 26.62 | 0.00 + 0.00 = 0.00 | 2.31 / 8.15 |
| COVA/i/k0 | 0.87 + 0.34 = 1.21 | 12.41 + 6.28 = 18.69 | 18.94 + 7.25 = 26.19 | 0.00 + 0.00 = 0.00 | 1.96 / 5.24 |
| COVA/i/k1 | 0.84 + 0.33 = 1.17 | 12.01 + 5.85 = 17.86 | 19.44 + 7.40 = 26.84 | 0.00 + 0.00 = 0.00 | 1.89 / 4.69 |
| COVA/i/k2 | 0.72 + 0.26 = 0.98 | 2.58 + 0.94 = 3.52 | 28.21 + 11.93 = 40.14 | 0.00 + 0.00 = 0.00 | 2.73 / 4.58 |
| COVA/i/k3 | 0.01 + 0.00 = 0.02 | 9.57 + 4.67 = 14.24 | 21.27 + 8.27 = 29.55 | 0.00 + 0.00 = 0.00 | 1.19 / 5.01 |
| COVA/i/k4 | 1.08 + 0.42 = 1.50 | 10.21 + 4.88 = 15.09 | 20.54 + 8.10 = 28.64 | 0.00 + 0.00 = 0.00 | 2.08 / 5.16 |
| COVA/ii/k0 | 0.76 + 0.30 = 1.06 | 14.09 + 6.78 = 20.87 | 19.19 + 7.60 = 26.79 | 0.40 + 0.04 = 0.44 | 2.27 / 9.22 |
| COVA/ii/k1 | 0.28 + 0.12 = 0.40 | 7.15 + 2.97 = 10.12 | 27.71 + 11.87 = 39.58 | 0.00 + 0.00 = 0.00 | 2.19 / 11.65 |
| COVA/ii/k2 | 0.26 + 0.11 = 0.37 | 12.21 + 6.05 = 18.26 | 22.06 + 9.03 = 31.09 | 0.00 + 0.00 = 0.00 | 1.95 / 7.06 |
| COVA/ii/k3 | 1.16 + 0.49 = 1.64 | 12.16 + 5.91 = 18.08 | 20.57 + 8.66 = 29.24 | 0.42 + 0.12 = 0.54 | 1.78 / 8.95 |
| COVA/ii/k4 | 0.21 + 0.08 = 0.29 | 4.54 + 1.52 = 6.05 | 31.11 + 14.40 = 45.51 | 0.00 + 0.00 = 0.00 | 2.14 / 9.76 |
| COVB/i/k0 | 0.94 + 0.40 = 1.35 | 12.34 + 6.55 = 18.88 | 18.77 + 7.18 = 25.94 | 0.00 + 0.00 = 0.00 | 2.00 / 5.73 |
| COVB/i/k1 | 1.42 + 0.60 = 2.02 | 17.57 + 8.47 = 26.04 | 13.22 + 4.72 = 17.95 | 0.00 + 0.00 = 0.00 | 1.91 / 4.70 |
| COVB/i/k2 | 1.35 + 0.66 = 2.01 | 16.42 + 8.03 = 24.45 | 13.81 + 4.71 = 18.51 | 0.00 + 0.00 = 0.00 | 2.79 / 7.31 |
| COVB/i/k3 | 1.73 + 0.71 = 2.44 | 18.51 + 8.85 = 27.35 | 12.22 + 4.43 = 16.65 | 0.00 + 0.00 = 0.00 | 2.03 / 8.62 |
| COVB/i/k4 | 1.95 + 0.86 = 2.81 | 12.41 + 6.04 = 18.46 | 17.56 + 6.70 = 24.26 | 0.00 + 0.00 = 0.00 | 2.10 / 5.32 |
| COVB/ii/k0 | 1.66 + 0.62 = 2.29 | 15.30 + 7.69 = 22.99 | 17.91 + 7.04 = 24.95 | 0.36 + 0.07 = 0.43 | 2.36 / 10.10 |
| COVB/ii/k1 | 0.16 + 0.07 = 0.23 | 25.46 + 11.70 = 37.16 | 9.59 + 3.18 = 12.77 | 0.00 + 0.00 = 0.00 | 2.20 / 11.79 |
| COVB/ii/k2 | 1.61 + 0.86 = 2.47 | 8.43 + 3.72 = 12.15 | 25.45 + 9.75 = 35.20 | 0.33 + 0.08 = 0.41 | 2.30 / 8.39 |
| COVB/ii/k3 | 0.89 + 0.38 = 1.27 | 6.96 + 3.49 = 10.45 | 25.73 + 11.11 = 36.84 | 0.57 + 0.19 = 0.77 | 1.91 / 5.98 |
| COVB/ii/k4 | 0.91 + 0.46 = 1.37 | 16.38 + 7.57 = 23.94 | 19.12 + 7.66 = 26.79 | 0.00 + 0.00 = 0.00 | 2.30 / 9.96 |

Observed spell lengths and fate per run. Initial/final spells and disappearance boundaries are censored; these medians are descriptive sample runs, not a survival estimator. C/R/F/U spell cells give median/max sample weights in seconds (— means never observed). These are sample runs, not verified uninterrupted periods. Endpoint sample allocation can exceed an exact lifetime by one 5 s bin, e.g. a birth at 800 s has zero observed future lifetime but a weighted endpoint. Exact lifespan is separate in JSON.

| Run | C spell median/max | R | F | U | Births / deleted / surviving | Last sample orphan / redundant, % all births | Exact removed-born class |
|---|---|---|---|---|---|---|---|
| RD3/i/k0 | 10/345 | 130/625 | 312.5/625 | — | 50/6/44 | 0.00/34.00 | {'non-service': 6} |
| RD3/i/k1 | 10/590 | 10/605 | 55/585 | — | 50/5/45 | 0.00/32.00 | {'non-service': 5} |
| RD3/i/k2 | 10/405 | 25/585 | 15/585 | — | 49/4/45 | 0.00/44.90 | {'non-service': 4} |
| RD3/i/k3 | 10/610 | 25/625 | 400/705 | — | 44/0/44 | 0.00/25.00 | {} |
| RD3/i/k4 | 15/350 | 65/645 | 350/645 | — | 46/3/43 | 0.00/28.26 | {'non-service': 3} |
| RD3/ii/k0 | 10/545 | 20/545 | 57.5/725 | 55/75 | 42/2/40 | 0.00/42.86 | {'non-service': 2} |
| RD3/ii/k1 | 7.5/50 | 25/665 | 75/625 | — | 41/2/39 | 0.00/75.61 | {'non-service': 2} |
| RD3/ii/k2 | 15/340 | 10/590 | 135/800 | 135/135 | 45/4/41 | 4.44/0.00 | {'non-service': 4} |
| RD3/ii/k3 | 10/35 | 5/75 | 420/800 | 30/420 | 39/1/38 | 5.13/0.00 | {'non-service': 1} |
| RD3/ii/k4 | 7.5/505 | 10/705 | 60/645 | — | 43/5/38 | 0.00/39.53 | {'non-service': 5} |
| COVA/i/k0 | 15/345 | 610/625 | 425/625 | — | 46/2/44 | 0.00/36.96 | {'non-service': 2} |
| COVA/i/k1 | 12.5/590 | 605/605 | 425/720 | — | 47/3/44 | 0.00/34.04 | {'non-service': 3} |
| COVA/i/k2 | 15/540 | 25/585 | 425/785 | — | 50/5/45 | 0.00/6.00 | {'non-service': 5} |
| COVA/i/k3 | 10/10 | 365/365 | 320/785 | — | 49/4/45 | 0.00/42.86 | {'non-service': 4} |
| COVA/i/k4 | 15/285 | 77.5/645 | 465/645 | — | 44/0/44 | 0.00/29.55 | {} |
| COVA/ii/k0 | 15/545 | 545/545 | 150/715 | 160/160 | 40/3/37 | 0.00/50.00 | {'non-service': 3} |
| COVA/ii/k1 | 30/105 | 25/665 | 270/645 | — | 42/4/38 | 0.00/57.14 | {'non-service': 4} |
| COVA/ii/k2 | 30/70 | 502.5/585 | 230/800 | — | 43/5/38 | 0.00/32.56 | {'non-service': 5} |
| COVA/ii/k3 | 230/445 | 445/445 | 200/800 | 85/85 | 43/3/40 | 0.00/48.84 | {'non-service': 3} |
| COVA/ii/k4 | 10/150 | 25/705 | 545/685 | — | 43/6/37 | 0.00/11.63 | {'non-service': 6} |
| COVB/i/k0 | 10/345 | 90/625 | 160/625 | — | 66/22/44 | 0.00/25.76 | {'non-service': 22} |
| COVB/i/k1 | 15/590 | 35/605 | 42.5/585 | — | 67/24/43 | 0.00/40.30 | {'non-service': 24} |
| COVB/i/k2 | 10/405 | 15/585 | 15/565 | — | 68/24/44 | 0.00/54.41 | {'non-service': 24} |
| COVB/i/k3 | 10/610 | 10/625 | 50/320 | — | 66/22/44 | 0.00/51.52 | {'non-service': 22} |
| COVB/i/k4 | 10/350 | 15/645 | 25/645 | — | 67/24/43 | 0.00/31.34 | {'non-service': 24} |
| COVB/ii/k0 | 10/545 | 20/545 | 60/715 | 55/75 | 65/24/41 | 0.00/40.00 | {'non-service': 24} |
| COVB/ii/k1 | 5/35 | 25/665 | 40/320 | — | 62/24/38 | 0.00/53.23 | {'non-service': 24} |
| COVB/ii/k2 | 10/340 | 5/595 | 35/620 | 130/130 | 64/23/41 | 3.12/0.00 | {'non-service': 23} |
| COVB/ii/k3 | 10/225 | 5/225 | 35/800 | 35/70 | 64/24/40 | 0.00/34.38 | {'non-service': 24} |
| COVB/ii/k4 | 5/505 | 10/705 | 80/640 | — | 65/27/38 | 0.00/50.77 | {'non-service': 27} |

All deleted new bodies were recorded non-service at deletion; exact redundant endpoints were zero. Some were redundant at the preceding figure: classification changes before removal, so the last-observed redundant percentage is not the redundant-at-death percentage. The JSON separates deleted/surviving last-sample counts; initial seeded elements are excluded from birth denominators.
