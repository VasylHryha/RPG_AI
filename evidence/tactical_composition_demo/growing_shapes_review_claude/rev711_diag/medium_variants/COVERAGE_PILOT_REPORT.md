DONE

Amendment-1 exploratory coverage pilots, COVA/COVB × starts i/ii × keys 0–4; two off controls. No verdict or A7 authorization.

Observer integrity: {'COVA': 'PASS', 'COVB': 'PASS'}. Verification errors: [].

RD3 control: {'i': {'passes': 5, 'runs': 5}, 'ii': {'passes': 3, 'runs': 5}}; pooled active-time coverage at sites 3–6: 0.08601377266387726. Existing coverage and A/B/E reused unchanged.

RD3 B is legacy_B: retained traces do not establish every per-birth post-transition gap. Historical totals are never mixed with revised B. Other labels retain their original scopes. C/B are global observations, N names the site; these are not causal identifications.

| Arm | Status | Empty passes/runs | Seeded passes/runs | Pooled sites 3–6 | Reading |
|---|---|---|---|---|---|
| COVA | DONE | {'passes': 5, 'runs': 5} | {'passes': 5, 'runs': 5} | 0.12255927475592747 | DESCRIPTIVE |
| COVB | DONE | {'passes': 5, 'runs': 5} | {'passes': 4, 'runs': 5} | 0.13642346582984657 | DESCRIPTIVE |

Pooled fraction = sum(active_served_steps)/sum(active_steps), sites 3–6 and ten on runs. Positive requires doubling RD3 and at least four of five empty passes. Regression is at most three empty passes. Missing trajectories or a missing integrity pair make the arm incomplete, never a failure/positive.

| Arm/site | Pooled active served fraction |
|---|---|
| RD3/0 | 0.4913194444444444 |
| RD3/1 | 0.6017830882352941 |
| RD3/2 | 0.33109848484848486 |
| RD3/3 | 0.18893979057591623 |
| RD3/4 | 0.0193853021978022 |
| RD3/5 | 0.05787292817679558 |
| RD3/6 | 0.07105061349693252 |
| RD3/7 | 0.3861257530120482 |
| COVA/0 | 0.4127923976608187 |
| COVA/1 | 0.38235294117647056 |
| COVA/2 | 0.4485227272727273 |
| COVA/3 | 0.31223821989528794 |
| COVA/4 | 0.12506868131868132 |
| COVA/5 | 0.013173342541436464 |
| COVA/6 | 0.01896088957055215 |
| COVA/7 | 0.0316453313253012 |
| COVB/0 | 0.5085526315789474 |
| COVB/1 | 0.602389705882353 |
| COVB/2 | 0.4617613636363636 |
| COVB/3 | 0.3327715968586387 |
| COVB/4 | 0.05729739010989011 |
| COVB/5 | 0.05828729281767956 |
| COVB/6 | 0.08146088957055214 |
| COVB/7 | 0.39819277108433737 |

COVERAGE_COMPACT_SUMMARIES.json includes all eight per-site/per-run fractions, per-run sites at >=50%, A/B/E, site births and request outcomes, first cost refusal, outages and break/non-repair causes, D3 classes and forced cuts. COVB additionally gives donor class/lock/age, retry outcomes and served-within-60s YES/NO/CENSORED; removal persists on failure.

Initial candidate cost refusals are reported separately; C retains terminal cost-refusal evidence and does not acquire an initial refusal whose retry succeeds. A cost-refused candidate before recycling is logged separately from its single final terminal. recycle_failed does not propagate a cost resource-stop under the unchanged dispatcher. B1 rechecks original clearance/count/cost only. Revised B excludes the repairing terminal and its restoring gap sample; restoration evidence has zero duration weight.

COVA clocks are kernel-owned and clone-copied, sampled at the completed integrate boundary before adapt/timers/growth; no intra-check update. The observer remains external to clone state. Full on/off trajectory digest plus legacy summary identity is required for each arm in the main phase.

Scheduler cap **5400 s**, raised by Claude under the owner's approval before execution (the spec's original 3600 s cap is historical). At most 10 workers; all remaining jobs/off controls included in projection using the maximum measured elapsed/CPU duration. Resume reuses identity-verified completed jobs and forbids started/incomplete reruns. Process-list errors stop execution. Caffeinate surrounds actual execution.

The coverage schedule has **22 slots**: 20 observer-on trajectories and two observer-off controls. The first ticket started and completed 20 slots, then stopped launching because its projection was 5767.1 s against the 5400 s cap; actual elapsed time was 2840.386 s (47.34 min). The second ticket reused those 20 completions and started only the never-started COVB seeded ii/k3 and ii/k4 slots; its projection was 1533.401 s and elapsed time 837.394 s (13.96 min). The two ticket elapsed times sum to 3677.780 s (61.30 min), excluding the pause between them. The 30 runs in SERVICE_RUN_SUMMARIES.json are the earlier telemetry batch; the retained coverage tickets do not support a 28+2 coverage-job count. Full ticket identities and timings remain in COVERAGE_RUN_SUMMARIES.json.

Neither arm meets Amendment 1's doubling requirement: COVA is 1.425 times and COVB 1.586 times RD3's pooled coverage; doubling requires at least 0.17202754532775452. Both have 5/5 empty-start passes and all ten observer-on runs complete, so both readings remain DESCRIPTIVE. COVA trades coverage toward sites 3–4 while sites 1 and 7 lose substantial served time; the pooled sites 3–6 statistic alone is not a measure of overall fairness.

Presentation corrections from the Codex stored-data recheck:

| Correction | Disposition |
|---|---|
| Scheduler sentence incorrectly retained the original 3600 s cap | Replaced with the approved executed cap of 5400 s; spec and receipts left unchanged. |
| Huge embedded final-ticket hash dictionary obscured the interrupted run and resume | Replaced with both tickets' concise timing, the stop reason, and the identity-verified 20+2 slot partition; full receipt retained. |
| External description said 28+2 coverage jobs | Clarified the 22 coverage slots and distinguished the prior 30-run SERVICE batch. |
| Reading needed its exact doubling boundary and complete-run condition in prose | Added the boundary and ratios; JSON readings unchanged. |


This report does not execute a pilot. Raw traces stay under _local/coverage and are pinned by size/SHA256. USAGE commands: COVERAGE_USAGE.md. Recheck tracking: docs/reviews/tactical_0h_coverage_implementation_recheck_codex.md; PLAN_CURRENT.md remains unchanged.
