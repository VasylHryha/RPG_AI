PASS_WITH_NOTES
Reviewer family: Codex
Reviewed commit: f33d1948ac59c9a6412100374e5d4ca1f7e41308

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

The exploratory diagnostic's arithmetic, declared positive reading and stored observer-control identities pass. It supports a response to the **combined resource ceiling under RD3 on these keys**. It does not establish that adopting ceiling 96 is the best candidate-law change, that all eight sites receive adequate service, or that inefficient allocation has been resolved. The recommended next mechanism is one-active-front-per-site growth authority, conditional on first confirming duplicated fronts from stored data; retain ceiling 64, existing branches and service redundancy for that comparison. Owner approval remains separate.

## Scope and identity

Read AGENTS.md; CAPACITY_DIAGNOSTIC_SPEC.md including both amendments; all six named capacity artifacts; SERVICE_TELEMETRY_REPORT.md, COVERAGE_PILOT_REPORT.md, DEBT_PILOT_REPORT.md, ECONOMY_PILOT_REPORT.md and MASS_BUDGET_DIAGNOSTIC.md; the capacity implementation recheck; and the owner's outside research update. Also inspected the retained run summaries, mass diagnostic JSON, raw capacity telemetry, and relevant reporting/kernel source as text. All evidence paths below are relative to `evidence/tactical_composition_demo/growing_shapes_review_claude/rev711_diag/medium_variants/` unless otherwise named.

| Reviewed artifact | SHA256 |
|---|---|
| CAPACITY_DIAGNOSTIC_SPEC.md | `3db347a746965e2b91b372cbf1bc309ba98675fa4bcf36fa1d4c6d5157d02ce5` |
| CAPACITY_DIAGNOSTIC_REPORT.md | `2bae3738dfc482669d7764f59601df55f39d41853448e42fd7ce2733ae981438` |
| CAPACITY_COMPACT_SUMMARIES.json | `42081de56b372ebbc82fdcfac043c398b4850df2ce990ba8d19eabeb33af5880` |
| CAPACITY_RUN_SUMMARIES.json | `e589c51d62bfb945805aec5c5e95f575df0f9bd0c5e25b483c79f6c68d67ec00` |
| CAPACITY_PREFLIGHT.json | `2b676abe45d1efe80b4382ddfb8774658992c72fe164dbebb470c3e0b7088281` |
| CAPACITY_IMPLEMENTATION_VALIDATION.json | `7dc9bb40ca2cbe92ee476934fc574b3e8efe6124d1ca3ccfa8f61011712dc2e9` |

Outside update: `/Users/new/Downloads/RRG_0H_FULL_COVERAGE_RESEARCH_UPDATE_AFTER_PUSH_2026-10-07.md`, SHA256 `e5fd72270c91ab07d14fff0a953e1c6824e9c67efb57dc1740b7ac5175658b12`.

Stored-data arithmetic only: no project imports, simulations, native loading, assay replay, pipeline or tests. Existing files, receipts, STATUS.json and docs/PLAN_CURRENT.md remain unchanged. Review/disposition tracking is here under the owner's single-file restriction.

## Numerical and rule checks

For each physical site, independently summed active-served steps and divided by summed active steps over precisely ten observer-on runs. The total service index sums those eight fractions with equal site weights; it is dimensionless, bounded by eight, and is neither simultaneous coverage nor delivered signal. For sites 3–6, used the coverage Amendment-1 pooling formula: sum all four sites' active-served steps / sum their active steps, rather than averaging four fractions or ten run ratios.

| Quantity | RD3 | CAP96 | CAP128 |
|---|---:|---:|---:|
| Total service index | 2.147575404987718 | 3.2115044931160184 | 3.4582240780108218 |
| Sites 3–6 numerator / denominator | 19735 / 229440 | 59965 / 229440 | 68782 / 229440 |
| Pooled sites 3–6 fraction | 0.08601377266387726 | 0.2613537308228731 | 0.2997820781032078 |
| Minimum pooled site fraction (site 4 / 5 / 5) | 0.0193853021978022 | 0.10017265193370166 | 0.1478245856353591 |
| Pooled sites at least 30% | 4 | 5 | 5 |
| Empty gate shape | 5/5 | 5/5 | 5/5 |
| Seeded gate shape | 3/5 | 5/5 | 5/5 |

The pooled per-site fractions recompute as follows (rounded here only):

| Site | RD3 | CAP96 | CAP128 |
|---|---:|---:|---:|
| 0 | 0.491319 | 0.551700 | 0.587025 |
| 1 | 0.601783 | 0.663438 | 0.680221 |
| 2 | 0.331098 | 0.546439 | 0.555758 |
| 3 | 0.188940 | 0.470664 | 0.482968 |
| 4 | 0.019385 | 0.258740 | 0.294385 |
| 5 | 0.057873 | 0.100173 | 0.147825 |
| 6 | 0.071051 | 0.197987 | 0.259893 |
| 7 | 0.386126 | 0.422364 | 0.450151 |

All 24 report site rows, 30 run indices, start/key pooled indices and ten paired contrasts match. Gate booleans recompute from stored A>=0.3, B>=0.3 and max(E)>=0.5, separately for each start. These are descriptive gate shapes from stored assay values, not an independent assay reconstruction or fresh §19.7 qualification.

**Amendment 2 is applied exactly:** CAP128 exceeds the predeclared literal 3.22; RD3 <= CAP96 <= CAP128; both arms have all ten prescribed on slots and passing integrity pairs. Exact 1.5 times RD3 is 3.2213631074815767, disclosed by the report; CAP128 clears that too. Thus the literal/rounded distinction does not change this result. No withdrawn “not resource-bound” rule was used. CAP96 alone is below both positive cutoffs, but the rule never required CAP96 itself to exceed them. The response is 1.4954× at CAP96 and 1.6103× at CAP128; it is not proportional scaling. CAP128 is slightly below CAP96 for empty key 0 and equal for seeded key 1; the declared ordering is pooled, not per-run.

Verified all 64 raw inventory entries' sizes/SHA256 (351,575,302 bytes), all 1,487 current completion-identity inputs, identical identity maps in all 22 rows, and the five historical-summary preservation pins. Independently recounted all 20 capacity on traces: each has 8,000 consecutive world steps and capacity samples, matching every site's stored exposure/service counts and all 160 compact 5s samples. Class body and cost totals conserve. All clone-isolation flags are PASS. For each arm's empty-key-0 on/off control, complete legacy summaries and stored trajectory digest strings are identical. This checks both prescribed pairs, not unrecorded off controls for every key/start. Full native-state byte streams were not retained here, so the trajectory SHA256 cannot itself be independently recomputed from geometry telemetry.

Preflight records CLEAR, pgrep return 1 with empty stdout/stderr. Implementation validation records 17 synthetic tests passing before execution; it is not the native result evidence. The completed scheduler records a 9,000s launch cap and 4,050.886s elapsed, with 22 jobs and no reused slots; the 5,400s text is the documented default, not this launch's actual cap.

## Findings and concrete dispositions

### N1 — Medium: the identified response combines admission and retention mechanisms

Scaling all three literals is the declared intervention, not an implementation defect. It raises ordinary count admission, prospective cost admission and the threshold at which D3 starts deleting. For realized trajectories, however, these mechanisms do not contribute equally:

| Stored observation | RD3 | CAP96 | CAP128 |
|---|---:|---:|---:|
| Maximum ordinary count at 5s samples | 46 | 67 | 88 |
| Count ceilings | 64 | 96 | 128 |
| First cost-refusal time across runs | 320–420s | 520–680s | 780s in two runs; absent in eight |
| D3 removals | 34 | 17 | 1 |
| First D3 per affected run | 320–720s | 600–780s | 800s, seeded key 2 only |

RD3 first-cost times are the unchanged-trajectory ECO-F exact candidate measurements; CAP times are stored cost-terminal boundaries. Propagated dispatcher refusals are not counted as independent insertion trials. Capacity arms have zero `cap` terminals, all D3 removals are non-service, and there are no forced service cuts/protected-over-budget events. Count admission did not visibly bind; the larger count literals therefore do not independently explain the observed gain. The D3 change did act, substantially reducing and delaying removal, while cost refusal was delayed. Admission headroom and route/front retention remain inseparable causes in this design.

**Disposition/fix:** preserve the positive label but describe it as a combined RD3 resource-ceiling response. Do not infer a pure cost effect or a necessary count increase. Any later causal separation requires a separately approved intervention; this review authorizes no run or changed law.

### N2 — Medium: extra material mostly becomes service redundancy, with real far-site gains

Equal-weighted 5s snapshot means in the fixed late window t>640s (320 samples per arm) show:

| Arm | Total charged cost | Critical | Redundant | Front | Orphan |
|---|---:|---:|---:|---:|---:|
| RD3 | 63.4125 | 1.4766 | 23.7748 | 37.6880 | 0.4731 |
| CAP96 | 95.2369 | 3.3902 | 56.7530 | 35.0938 | 0 |
| CAP128 | 109.7328 | 4.8620 | 76.1728 | 28.6980 | 0 |

Relative to RD3, CAP96 adds 31.8244 total cost and 32.9781 redundant cost, while front cost falls 2.5942; CAP128 adds 46.3203 total and 52.3980 redundant cost, while front cost falls 8.9900. Critical allocation rises too. This is principally more material on service-connected, individually dispensable paths, rather than a larger unfinished-front allocation. Full-time means give the same direction: redundant cost 17.5193 -> 30.4778 -> 34.9087; front cost 28.9612 -> 28.2251 -> 26.7323.

“Redundant” is a graph classification, not a spatial “near O” label or proof of waste. Class membership uses all eight physical sites, including idle sites, while the coverage index uses active time; class cost therefore does not measure material delivering active service. A further stored-figure check reconstructs k=8/radius-3 held pairs, exempts the actual output body, and allocates .05 pair cost per endpoint. At all 320 late figures per capacity arm, ordinary/pair totals and generated strong edges match stored values; no tie at the eighth-neighbor boundary occurs. Mean cost within radius 1 of O is 2.7922 -> 3.2917 -> 3.3606; within radius 3 it is 8.6367 -> 14.9803 -> 17.6075. Only about 20% of the incremental late charged cost lies inside radius 3. Most extra material is outside that near-O region. These spatial overlays do not individually attribute redundant bodies to sites.

All eight pooled site fractions improve over RD3, and the named sites 3–6 fraction rises 3.0385×/3.4853×. Therefore “all extra material is useless near redundancy” is contradicted by stored coverage. “Extra material completes far fronts directly” is also stronger than the evidence: fronts can change class into routes, sites can share bodies, and one arm's bodies are not the counterfactual fate of another arm's bodies.

**Disposition/fix:** use both the class and spatial tables in the owner decision; retain allocation as a mechanism question. Preserve service redundancy. ECO-R's 53 removals and 0/8 completed gate shapes warn against generic thinning, but its two missing runs remain missing, and redundancy labels alone do not prove the removed material's causal signal role.

### N3 — Medium: pooled improvement conceals severe start-specific starvation

The minimum of pooled site fractions is not the minimum site/run fraction. At least one site's active-service fraction is zero in 10/10 RD3 runs, 8/10 CAP96 runs and 5/10 CAP128 runs. CAP96 empty-start pooled site 5 is exactly zero; CAP128 empty-start site 5 is just 7/28,960 = 0.00024171270718232045. Seeded-start minima are much better. Passing A/B/E only requires max(E), so 10/10 gate shape is compatible with these coverage gaps.

**Disposition/fix:** state both pooled and start/run minima whenever considering candidate adoption. Do not turn the improved pooled minimum or gate counts into a full-coverage claim. No new fairness cutoff is retroactively added to Amendment 2.

### N4 — Low: the motivation table contains a stale DEBT baseline

The spec's opening table says DEBT total 1.82, but the committed settled active-service counts give **1.7447545307612755**, identical to COV-A; COV-A's displayed 1.75 is rounded upward rather than the usual two-decimal 1.74. RD3 2.1475754, COV-B 2.5007136 and the eight completed ECO-R runs' 1.1600186 agree with their displayed approximations. DEBT's final report already discloses identical COV-A coverage and unresolved fairness semantics.

**Disposition/fix:** use the committed denominator-based values, label ECO-R's eight-run scope, and correct the motivation in a future drafter addendum. This stale table is not an input to the capacity decision rule and does not invalidate its positive result. Existing spec/report bytes are preserved under this task's restriction.

## Research update and the owner's next single change

The static 22.4-cost star establishes structural feasibility with carefully placed bodies and the actual held-pair charge. As MASS_BUDGET_DIAGNOSTIC.md states, it establishes neither a constructive growth path, stable dynamics, temporal coverage nor A/B/E response. The diagnostic demonstrates that the current **dynamic algorithm** serves more active time when its combined ceiling is raised. Both statements can hold alongside “allocation is the problem and more budget masks it.” The update's recommendation “do not raise the budget yet” concerns choosing a fix, and the diagnostic spec itself says a positive result should target efficiency rather than a bigger budget. There is no necessary contradiction; the stronger assertion that 64 cannot constrain this dynamic law should be narrowed, while the recommendation to investigate allocation remains supported.

**Recommended single mechanism:** one-active-front-per-site B-path growth authority at ceiling 64, if stored analysis confirms multiple competing fronts. Preserve B1, scheduling, D3, physical law, existing branches and served-route redundancy. Specify deterministic tip re-election, loss of root reachability, service/idle transitions and shared-site front ownership prospectively. This targets accumulation before pruning; it is a proposed mechanism, not a demonstrated improvement. A simple ceiling-96 candidate remains a practical fallback for the owner, but current evidence does not establish it as efficient, sufficient for eight-site service or qualified on fresh keys. The smaller additional gain from 96 to 128 is descriptive, not an optimum at 96.

**Cheap stored-data discriminant before another pilot:** join matched 5s figures, strong edges, world-step service and birth/removal histories for RD3/CAP96/CAP128 (plus COV-A/DEBT where useful). Around each site's requests and before/after the first cost refusal and first D3:

1. Count root-connected no-output frontier components and eligible sponsor tips per active unserved physical site. Recover role/gain/silent eligibility from retained legacy state/events rather than assuming proximity alone defines roots; validate reconstruction against stored service and class totals. Distinguish tips within one shared blob from genuinely separate fronts; a weak-component count alone can hide branching.
2. Allocate body and held-pair endpoint cost to site-supported fronts using a declared deterministic shared-site convention; retain a separate shared bucket or fractional allocation, never double-count. Measure cost/residence in competing historical fronts and meaningful gap progress, not merely any numerical improvement.
3. Link accepted B-path sponsor/child IDs to later far-site restoration and front-to-service conversion at observed snapshots. Stratify service-redundant cost by near-O radii and site support. Preserve censoring and the 5s sampling limit; this is an observational history, not marginal deletion savings or a counterfactual rerun.

If repeated competing fronts consume substantial cost before refusals while few complete, that supports one-front authority. If most unserved sites already have a single progressing front and extra ceiling mainly retains later useful shared routes, that weakens one-front and favors a retention/shared-route efficiency investigation or the owner's pragmatic ceiling choice. Stored analysis can rank these explanations; it cannot establish the benefit of either changed dynamic law. DEBT=COV-A and inert ECO-F weaken repeating those exact rules; ECO-R weakens generic redundancy deletion.

## Independent recheck and limits

The owner's request above was sent verbatim to a separate Codex reviewer (`capacity_recheck`), who independently inspected the declared rule, stored numbers and causal/decision limitations. Its findings agreed with the positive reading and highlighted coupled D3/admission, topological-versus-spatial redundancy and start-specific starvation; incorporated above. This supporting recheck is same-family; this result review is Codex reviewing Claude's executed/reported exploratory result, not scientific acceptance. The completed draft's read-only recheck found no blocker and requested one clarification: all-site class allocation and active-time coverage have different scopes. That clarification is incorporated in N2.

| Stop condition | Yes/no | Action | Responsible role |
|---|---|---|---|
| Is an arithmetic, declared-reading or stored integrity-pair defect unresolved? | No | Retain the exploratory positive reading | Reviewer |
| Does this review authorize ceiling-96 adoption or a new experiment? | No | Decide the next proposed single change | Owner |
| Has duplicated-front waste been established by class totals alone? | No | Perform the bounded stored-data discriminant before selecting the efficiency rule | Drafter |
| May existing receipts/spec/report or docs/PLAN_CURRENT.md be edited in this task? | No | Preserve them and deliver only this review | Reviewer |

The primary `.git` directory is not writable in this session; leave this single review file uncommitted, as instructed. No staging, alternate checkout or hook bypass is used.
