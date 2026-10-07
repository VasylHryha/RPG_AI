RECHECK_COMPLETE_WITH_LIMITS

Reviewer family: Codex (GPT-6), separate analyst/reviewer pass. Claude CLI was unavailable because it was not logged in; this is a same-family stored-evidence review, not cross-family milestone acceptance or authorization for an experiment.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Reviewed base HEAD: `b87bf596181a59757a8a2ce2750d18cb2b27c653`.

| Reviewed artifact | Bytes | SHA256 |
|---|---:|---|
| FRONT_ALLOCATION_DIAGNOSTIC.md | 17069 | `517dcbe1b0a14530e88895378f61c3dbb84bbdf51d89da33788f7891a77949b6` |
| FRONT_ALLOCATION_DIAGNOSTIC.json | 707929 | `bde1b3afe9d00457a7c1cce7e65d2e89f49ebcb46a9006f507ee2dfa3dc9c845` |
| analyze_front_allocation.py | 36126 | `aa6b7e4e0179aa4d003e049b417e0b769c800d3d72f2d608a3daa2bebabf6a64` |
| _local/front_allocation/DETAILS.json.gz | 10421940 | `f63d0e072ce9a54c265f6011f5b77d5063584c09f05b4c413d3bc5a148da3a2f` |

All findings below were fixed or explicitly bounded before the final artifact review. No blocking defect remains for delivery of this PARTIAL stored-data diagnostic. This does not establish that the proposed scheduler improves coverage.

| Priority | Finding | Final disposition |
|---|---|---|
| High | Summing endpoint costs accumulated floating-point error at the descriptive cost>=63 boundary. Intended 63-unit snapshots became 62.99999999999997–62.99999999999999, excluding 6 RD3, 13 COV-A and 11 COV-B snapshots. | Fixed: total cost is computed directly as N+.1 times charged pairs; allocated endpoint costs are checked for conservation with tolerance. Final near-cap counts are 662/561/656, matching the prior mass diagnostic. |
| High | Debt through the last completed observer record at t−.1 is lagged at a growth decision t; the integration interval ending at t is already complete. Calling the lagged value exact elapsed predecision debt obscured the sampling convention. | Fixed: primary quota/scheduler debt uses historical active-unserved integrate boundaries through t. The lagged observer convention is retained and clearly named. Both complete 8,000-point histories are present. First debt choices change on zero eligible checks between conventions, so the corrected timing preserves the reported comparison. |
| Medium | Waiting reconstructed as count/10 loses accumulated IEEE floating-point distinctions. Also, legacy paths omit idle sites while the real waiting clock resets idle served sites; growth-boundary idle service can be unrecorded before edits. | Fixed/bounded: accumulated float +.1 is used; missing pre-growth idle reset values are declared proxies. COV-A order comes from exact recorded ranks. The proxy agrees with all 400 COV-A recorded orders, but that does not identify its missing clock values. RD3/COV-B offline waiting comparisons remain explicitly proxies. |
| Medium | Component-tip cost was present, but the separately defined single nearest-O site-tip ID had no dedicated cost/count summary. | Fixed: each component has tip_owned_cost; each site has B_path_site_tip_owned_cost; compact summaries include both component-tip counts and defined single-site-tip counts/shares. The report distinguishes these diagnostic tips from actual B-path sponsor selection. |
| Medium | ECO-F described as byte-equivalent could imply identical telemetry/state digests, contradicting the economy diagnostic's different clock fields. | Fixed: retained trajectories and assays match RD3; clock state/digests and telemetry bytes differ. No causal phase/RNG equivalence is claimed. |
| Medium | Scheduler ordering disagreements and old front mass could be overstated as proof of the next policy's benefit or of donor safety. | Bounded: recommendation is one service-debt scheduling hypothesis. It acknowledges material cost refusals, cannot reclaim historical cost, does not infer stagnation from age, and does not infer safe recycling from strong-graph labels. A falsifier and owner-proposal boundary are explicit. |

Independent verification used standard-library stored arithmetic only. No project runner, simulator, pilot, medium execution, assay replay, mutation probe or hypothetical sequential deletion was executed. The reviewer edited only this file; plan, design, receipts and source telemetry were preserved.

Before decoding source gzip files, independently verified all 157 original inventory sizes/SHA256 values. Independently verified final derived raw size/SHA256 before decoding it and verified every recorded interpretation/source hash, including the final script identity.

Reconstructed front sets, charged k=8/radius-3 pairs and equal-split ownership independently from original coordinates/strong edges for k0 of every arm and both starts at 20, 400 and 800 seconds: all 18 figures matched. Checked all 4,800 final allocations for site/component cost conservation, all birth-origin front cost totals, component-tip cost sums and single-site-tip membership/bounds. Final unserved/multiple-component denominators reproduce RD3 2253/769, COV-A 2458/762 and COV-B 2067/473. Component-tip totals are 2634/2818/2121; defined nearest-O site-tip totals are 1838/2029/1619 over those unserved growth-end site/check denominators. They do not count persistent active fronts or all leaves.

Checked both complete 240,000-point histories for active minus served active = debt, all 1,200 decision-time debt keys and every quota terminal's refused-site debt. Independently accumulated COV-A i/k0 historical debt at 20/400/800 seconds from its source steps; final records matched. Recorded COV-A ranks independently reproduce 98/399 first-choice disagreements, including 43 checks containing quota refusals. Last B-path-check outcomes reproduce the report's RD3 755 cost/505 quota, COV-A 796/592, COV-B 392/539 plus 28 recycle_failed. These are initial-candidate site/check outcomes, not counts of all attempted births.

Independent composite midpoint radial integration at 100,000 and 400,000 bins gave nominal-arena at-least-one fractions .970114522284 and .970114528961; at-least-two fractions .718655735402 and .718655735459. The adaptive result is consistent with the independent calculation. The radius-6 area denominator is declared despite a soft wall. Strict reach-zone distance infima are 1 from origin O and .5 from seeded O; area boundaries have zero measure. Element-position fractions count body/snapshot observations rather than unique bodies or area.

The owner's section-6 tree is applied cautiously. Extra-component cost is only 18.15%, 13.52% and 13.44% of allocated unserved front cost, so duplicate components do not dominate this measured cost. Service-debt scheduling offers a limited, observable change to existing admission order; large cost-refusal counts keep geometry and budget allocation unresolved. Roughly nine tenths of front observations are shared direct roots, and every retained front observation is a direct root of some physical site. This supports scrutiny of shared-root representation, but narrowing physical service reach would change the measurement and has no demonstrated benefit. Old-body age is not a meaningful-progress test. No generic redundancy thinning or combined policy is supported.

Remaining limits are accurately carried by PARTIAL: post-growth figures cannot recover every intra-check geometry, continuous ownership, or missing idle pre-growth clock reset; snapshot components are not persistent sponsor identities; birth-origin attribution is not causal blame; allocated cost is not deletion savings; no stored ordering comparison predicts new acceptances, future coverage or gate success. Those gaps require a reviewed future design or additional telemetry, not reinterpretation of recorded verdicts.

Recheck tracking and disposition are recorded here and in the new diagnostic under the owner's explicit prohibition on editing or pinning docs/PLAN_CURRENT.md. No numeric quality score is assigned.
