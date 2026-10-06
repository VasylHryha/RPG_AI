CHANGES_REQUIRED
Reviewer family: Codex
Reviewed commit: 7954445041e326f3aa2d7d99b71e0b62e8536dcf (7954445)
Reviewer model: GPT-6
Review date: 2026-10-07

## Scope and conclusion

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Reviewed `evidence/c6_option_b/inexact_study/`, the round-2 memo's proposed tolerance, the performance deep-dive, and the actual Option B/protocol/analysis callers. This is an owner recheck of an engineering diagnostic, not C6 acceptance or permission to adopt a different numerical contract.

The stored evidence supports **small observed numerical differences, identical recorded discrete outcomes in the sampled worlds, and approximately 25% lower measured compute CPU**. Kernel identity and the exact baseline are substantiated. However, `SAFE_UNDER_PROPOSED_TOLERANCE`, “every decision type,” and the conservative panel-risk claim overstate what was assessed. Decision contexts are missing, several margin calculations are not changes in the actual signed decision margin, and the proposed correction changes the acceptance contract unnecessarily. No observed outcome flip was established by this review; the requested changes concern coverage, arithmetic, reproducibility and claims.

Reviewed artifact SHA-256:

| Artifact under `evidence/c6_option_b/inexact_study/` | SHA-256 |
|---|---|
| `INEXACT_IMPACT_REPORT.md` | `65dd4d6e2b02611ca00803a2d0301468d33b66adaedb5aa73d6b7e97af859f6e` |
| `SUMMARY.json` | `d269fbb7e29b1779ad30d93d09656cd00aca4c59149147c1dd6f56dc0d42c884` |
| `scripts/impact.py` | `9a5e5147d0f35b6d0b59d5b5efd4c9352f6684b73ca114dc783e59cad8d8bd89` |

## Findings and concrete fixes

### F1 — High: the analysis does not cover every C6 decision family/context

Report §4 and §10 claim every numerical decision and every decision type are covered. `scripts/impact.py:71–105` covers five stored structural statistics, recovery criteria, reduced causal tests, individual descriptor refinement and grid-error monitors. It omits:

- **Paired gain refinement:** `geomind/c6_r4_field_protocol.py:127–129` checks refinement of the intact-minus-control gain, separately from each descriptor's refinement. There is no corresponding margin row. The parallel operation uses this decision too.
- **Primary analysis decisions:** `geomind/c6_r4_field_analysis.py` defines 16 response/later-formation contrasts, CI boundaries at ±0.01/±0.1, eligible-world and chain masks, quorum, empty-bootstrap handling, grid-verdict agreement and hypothesis combination. The study compares world artifacts; these decisions are absent. Ten engineering worlds, including two smoke worlds, are not a registered 40-world analysis. They should be explicitly unassessed, without manufacturing a final-panel verdict.
- **Detector contexts:** `windows()` requires `qualification_window` and `qualified_states`, and extracts grid dt only. The 200 windows cover recorded introduction/qualification episodes. They do not cover pair decisions in rolling operation persistence, endpoint qualification, recovery control/kicked endpoints, or dt/2 and dt/4 qualification. Those paths call the same detector and can change memberships. Qualification stores `all_rows[0]`, not all three candidate inventories (`c6_r4_field_assay.py:166–196`), so the report's general “3 grids × all candidates” description is inaccurate.
- **Other guards and discrete selection:** candidate minimum size, positive geometry/spacing, candidate selection/ties, finite-value checks and sham/provenance equality checks have no explicit decision inventory. The full artifact comparison supplies useful observed discrete equality, but is not a margin analysis of all underlying branches.

**Fix:** add a ledger mapping each actual decision family and context to its evaluator, threshold/operator, units, sample count and `ASSESSED`/`UNASSESSED` reason. Derive paired-gain margins from stored gains. Mark absent fine-grid/recovery trajectories and panel statistics honestly; do not run worlds to repair them in this review. Narrow the headline to observed stored-outcome agreement and list what remains unassessed. Future owner-authorized adoption checks can instrument missing contexts in new evidence. Arm A remains outside this study.

### F2 — High: the panel-risk number is an unsupported extrapolation, not a conservative bound

Report §4's approximately `2e-4` is reproducible as `21 × (40/10) × (2.4e-10/1e-4) = 0.0002016`. Using the frequency maximum gives approximately `3.44e-8`. The arithmetic is not the problem.

This extrapolates a constant near-threshold density from a band of width `1e-4` to widths around `1e-10`/`1e-14`, assumes sampled perturbations bound future perturbations, and transfers engineering-world frequencies to future worlds. None is established. The histogram already contains six entries within `1e-8` and the same six within `1e-6`, demonstrating sensitivity to the chosen band and repeated observations. Counting correlated copies does not certify an upper bound on unsampled thresholds, omitted decision contexts or aggregate CI boundaries. Qualifying the number as “not a guarantee” does not justify calling it conservative or presenting “1 panel in 5,000” as measured risk.

**Fix:** remove the probability/rate recommendation, or label it explicitly as a heuristic sensitivity calculation conditional on unverified density and error-bound assumptions. State that future-panel outcome risk is not quantified by this study. Preserve the useful measured margins and zero observed stored-outcome changes. Any certified bound needs justified perturbation bounds and complete decision coverage; no final entropy or panel computation is authorized here.

### F3 — Medium: several margins/deviations use the wrong quantity, and the closest lock is misreported

`impact.py:95` uses `log10(min(intact)/floor)` as the causal-floor margin but `:149–157` uses the raw intact-effect change as its deviation. Dividing decades by effect units makes the reported ratio meaningless. The protocol actually tests **each** intact grid with strict `> floor`, including grid agreement. Report each grid's raw `v-floor` and raw change, or compare logarithmic margin with logarithmic change consistently.

For causal spread, the threshold is `0.1*min(intact)` and also moves between engines. The current deviation measures only the spread change. For ablation, `max(1e-12,0.2*min(intact))` also moves; zero change in the ablated value does not imply zero change in its margin or infinite margin/change ratio. Raw development-0 source `m_to_g` illustrates this: spread-value change is `1.1102230246251565e-14`, signed-margin change is `8.049116928532385e-15`, and the ablation limit changes by `6.106226635438361e-15` despite zero ablation-value change. These remain small, but the current ratios are not the quantities claimed.

The scalar `flips` computation at `impact.py:182–183` uses unsigned change as though it necessarily moved toward the threshold, and is never emitted. `summarize.py` similarly creates an unused check limited to `closest10`. Full stored Boolean equality remains evidence of observed outcome agreement; these calculations do not provide an exhaustive derived flip receipt.

Report §4 says the closest lock is `1.8e-3` in development 4. Its own `results/smoke_1.json` contains the closer `/turns/0/before_formation/3` case. Independent raw recomputation gives pair `(0,22)`, exact `0.1001632847400453`, inexact `0.1001632847400464`, margin **`1.632847400452886e-4`**, change **`1.1102230246251565e-15`**. There is still no flip. Also, §3's “all 29 ... monitors, not decisions” conflicts with its next bullet: one is the thresholded recovery-pattern statistic.

**Fix:** evaluate the actual signed margin independently for both engines, accounting for moving thresholds, use the exact strict/non-strict operator, and emit counts and actual flip identities for every assessed family. Correct the closest-lock statement and distinguish 28 grid monitors from the one recovery statistic. Match circular-standard-deviation clipping to the actual detector (`clip(...,1e-300,1)` plus nonnegative square-root argument); label NumPy link recomputation as such rather than the literal C++ arithmetic.

### F4 — Medium: the corrected tolerance silently relaxes the original absolute bound

Memo §7 required **every float** to differ by at most `1e-8`, with relative grid errors reported additionally. Report §7 replaces that bound for grid-error diagnostics with relative difference ≤10% and each engine's own grid limit. That permits much larger absolute changes than `1e-8` near the `0.05` limit. It is a substantive contract change, not just correcting the displayed safety factor. All sampled values already satisfy the original `1e-8`; replacing it is unnecessary.

The stated explanation also conflates different extrema. The largest relative monitor change is **5.0551%** at smoke-0 `/checks/809/max_errors/position`, exact `9.907616180352751e-11` versus inexact `9.406776773112684e-11`. It is not on a value around `1e-5`. The largest absolute change is development-2 `/checks/323/max_errors/position`, `7.3999889039608e-5` versus `7.399654856345048e-5`, difference `3.3404761575145728e-9`.

**Fix:** retain ≤`1e-8` on all comparable finite numerical outputs, including monitors, and report relative monitor changes separately. If an additional relative gate is desired, define its denominator and zero policy and require both bounds. Describe any replacement as a separate owner decision. Pin an actual macOS build identifier/library identity for future adoption; the platform string in the receipts supplies a release version, not an explicit macOS build identifier.

### F5 — Medium: archived analysis scripts cannot reproduce this delivery as placed

`scripts/summarize.py` resolves `W` to `scripts/`, looks for `scripts/results/` and `scripts/runs/`, and would write `scripts/SUMMARY.json`. Those inputs do not exist. Even after correcting the root, its unrestricted `results/*.json` loop encounters the two batteries and the exact-baseline comparison, none of which has `pair_level`. `run_impact.sh` similarly targets results and world artifacts beneath `scripts/`, whereas the delivered results are in the study's `results/` and its run artifacts are under `raw_worlds/` with different names. The scripts are a historical scratch layout, not a working reproduction route for the committed report.

**Fix:** provide a new stored-data-only analysis revision with explicit input/output roots, a fixed ten-world inventory, paths resolving through the raw inventory/reference mapping, and separate battery/baseline handling. Fail on missing or mismatched inputs rather than silently aggregating none. Keep original evidence unchanged and do not couple reproduction to `queue.sh` or execute worlds. Reconcile any newly generated summary against the original as a diagnostic correction.

### F6 — Medium: the recommendation drops the documented runtime/load qualification

Measured ratios are correctly reported: six nontrivial pairs have mean CPU ratio **0.7467061**, range **0.7193794–0.7679028**; all seven pairs average **0.7553287**. The wall ratios span **0.6402408–0.8328890**, under changing load, and measure compute time rather than the full serialized lifecycle. CPU seconds are less affected by waiting, but shared-load scheduling, core placement and cache contention still limit generalization from one ordered sample per pair.

Report's “exact engine already meets ... about 2.4× headroom” omits the performance deep-dive's explicit counterexample: final exact code took **396.1 s** under load reaching 84.6, failing the 360 s rule. The suggestion to use inexact for a busy 40-world panel is therefore not a readiness result, and this study's mostly single-world schedule does not establish two-worker panel throughput.

**Fix:** qualify the headroom by measured load/core availability and retain the documented failure case. Describe approximately 25% compute-CPU savings as an observation on this machine, wall savings as indicative, and panel readiness as unassessed. Before future recorded use, apply the existing runtime gate with the intended concurrency and resource conditions. No timing run is needed or authorized for this recheck.

## Evidence that checks out

- All **17 local compressed raw worlds** match the committed inventory's byte lengths and SHA-256 values. Re-adding the ten per-world comparison receipts reproduces the aggregate: `17,413,140` floats, `8,907,030` changed, `29` above `1e-10`, none above `1e-8`, `76,703` assessed scalar instances, `55,200` lock pairs and `1,711,200` link tests. These are assessed/repeated instances, not a complete protocol branch inventory.
- Exact build: source `9ebe2acf7dd873d3437b5d645091e41bb9ed1a3e69a56a6fc36ebdfdfff96920`, binary `3e269f1464b328e660b5b37ee16a72ed7273c090ee00dd27370129f60ff38f90`. Inexact build: source `d27d46bb6053bed84acbed330e0c28fa2c174ae417ad80bd9e4d1f6c5338582d`, binary `e9c3a10fecb81d63558253d4e6eda35cf6b631f4659a05c0e75a4e3d6fd69ec1`. All study run START records consistently distinguish them, as do both battery records. The surviving scratch binary hashes match. `otool -L` shows Accelerate and `nm -u` shows `_vvexp` and `_vvsincos`. The unchanged loader verifies source/flags/binary before and after native selection. This is substantive evidence the comparison used the inexact kernel.
- Independently compared local exact smoke 1 with the stored reference using recursive type and binary-float equality, excluding only root cost/build metadata: **zero mismatches**, including `1,365,412` float leaves and `1,396` Boolean leaves. The baseline confirmation is valid.
- Development-0 closest frequency statistic is exactly `0.010000007263912924` versus `0.010000007263912841`, distance `7.2639129242851874e-9`, change `8.326672684688674e-17`. Across its three grids the largest inexact change is `4.163336342344337e-16`; exact dt-to-dt/4 spread is approximately `7.28e-13`. The reported approximately 17-million ratio is supported for this assessed case.
- Both recorded reference/equivariance diagnostics pass under the respective identified binaries: reference maxima **`9.46687173097871e-13`** exact and **`1.278033234797249e-12`** inexact; scene equivariance **`7.549516567451064e-15`**, renaming zero. These were read, not rerun.

Low note: “Both are accurate to about 1 unit in the last place” is broader than the memo's own measurements, which report up to 3 ulp for vector sin/cos and up to 33 ulp for the separable Gaussian expression relative to scalar evaluation. Agreement with scalar libm is not a certified error against the mathematical value. Use the measured trajectory/statistic differences and avoid asserting equal mathematical accuracy.

## Disposition and command scope

F1–F6 are open and assigned to the study author for a new corrective analysis/report revision. No implementation or adoption change is approved by this recheck. The smallest acceptable correction is an honest decision-coverage ledger, correct signed margins/closest-lock statement, removal or relabeling of unsupported panel probabilities, preservation of the absolute tolerance, working stored-data reproduction, and restored runtime qualification. These changes need no C6 worlds. Any missing execution evidence remains explicitly unassessed until separately authorized.

Used read-only repository inspection, small Python reads/arithmetic on stored JSON, raw-file hashing, and static binary inspection. No project simulations, worlds, tests, battery reruns, mutation probes, panel analysis, native loads or builds ran. Existing files, including the unrelated dirty `docs/PLAN_CURRENT.md`, were not edited. The author/owner should record this recheck and disposition there; the user's one-file restriction controls this review delivery. `.git` is not writable in this session, so the review is left uncommitted.
