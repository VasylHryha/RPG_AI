APPROVE_WITH_NOTES
Reviewer family: Codex

Reviewed at HEAD `36b069f3d204ed5363208a267815442a7e264968`: CAPACITY_DIAGNOSTIC_SPEC.md including Amendments 1 and 2, both prior Codex reviews, DEBT_PILOT_SPEC.md including Amendment 1, DEBT_USAGE.md, the DEBT scheduler/worker/report/observer and non-hashed compute-cap configuration, and kernel_builder/ with the reproduced RD3 law. Exploratory development review; no scientific acceptance or experimental verdict.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Round-2 dispositions

**R1 resolved.** The owner's current instruction explicitly authorizes one coupled resource-ceiling change: RD3 ordinary-count admission (line 365), prospective-cost admission (370), and D3 over-budget trigger (499), all 64 → 96 or all 64 → 128. Amendment 2 withdraws the stale cost-only instruction. Earlier Arms wording is superseded by Amendments 1–2. No other policy constant changes. This is a bundled ceiling intervention; it does not isolate admission from D3. No active RD3 reserve calculation uses 64. Historical laws, the 640s assay selector, control-U queue assertions, unsigned seed widths and digest lengths remain unchanged.

**R2 resolved.** Amendment 2 withdraws “not resource-bound” and makes every non-positive result descriptive. It also supersedes the median-after-400 condition, so an undeclared median sampling population no longer controls a reading. Retain realized cost/count, count/cost refusals, and D3 events as observations. Neither unused headroom nor a weak endpoint response identifies what does or does not bind.

No new defect changes the arm's meaning. Step 2 may proceed within the current owner's scope.

## Notes fixed before execution

**N1 — latest declared cutoff is literal 3.22.** Amendment 2 explicitly writes index >= 3.22. This supersedes the earlier exact-ratio language for implementation; it is not mathematically identical to 1.5 times the unrounded baseline. Read-only recomputation on exactly ten RD3 observer-on summaries gives `T_RD3 = 2.147575404987718`, so exact `1.5*T_RD3 = 3.2213631074815767`. The report must disclose both, apply the latest literal 3.22, and not silently substitute the exact ratio. Define “between” inclusively: `T_RD3 <= T_CAP96 <= T_CAP128`. The positive label means that these two doses satisfy this exploratory reading on these keys; it establishes neither proportional scaling nor a general efficiency law.

**N2 — aggregation and integrity.** For each physical site pool active-served counts over active counts across precisely five keys and both starts (ten on jobs); sum the eight fractions. This dimensionless index ranges from 0 to 8 and weights sites equally despite unequal active exposure. It is neither simultaneous service, delivered signal, nor the A/B/E gate. Exclude off controls. Missing/duplicate jobs, nonpositive denominators, invalid counts or either failed/missing integrity pair withhold all readings. Retain start-specific and paired per-key values as descriptive context.

**N3 — observer additions.** Reuse the revised coverage observer's integrate transitions, per-birth restoration semantics and settled post-growth counting in new files. Override reporting-only cap fields with the actual cost ceiling and separate count ceiling; map CAP labels to RD3 removal classification. Do not modify historical observers or summaries. Record structural and active-served simultaneous counts separately. Cost-per-site ratios use explicit denominators, null plus a zero-service flag for zero denominators; mass uses ordinary bodies plus 0.1 per undirected ordinary held pair, allocated 0.05 per endpoint, with O free. These measures retain their material rather than signal interpretation.

**N4 — implementation boundary.** Reuse the anchored DEBT process gate, at most ten workers, main-phase on/off pairs, identity-verified resume, and refusal to rerun any started/incomplete slot. Read the independent compute cap once at launch from non-hashed _local/CAPACITY_CAP.json (default 5400s) and record it in the ticket. No identity manifest pins Markdown design/plan files or cap configuration. The stale DEBT fairness wording must not be inherited; DEBT files and results stay unchanged. This spec review does not certify future implementation or actual run integrity.

## Independent recheck and preservation

The owner request above was sent verbatim to reviewer agent `capacity_r3_recheck`, a Codex same-family fallback; Claude execution/review remains separate. The reviewer independently confirmed both blockers resolved and the literal 3.22 disposition, with no arm-meaning blocker. Recheck tracking is here because the owner explicitly prohibits edits or staging of docs/PLAN_CURRENT.md. No plan update is implied.

Step 1 involved read-only inspection and standard-library arithmetic over committed JSON only. No project tests, native loading/steps, process listing, assay, panel or pilot ran. Existing design, plan, status, code and committed evidence remain unchanged.

| Stop condition | Yes/no | Action | Responsible role |
|---|---|---|---|
| Does the current scope still conflict with the three-ceiling intervention? | No | Proceed with exactly three targeted replacements | Implementer |
| Does the current reading infer absence of a bottleneck from weak/null results? | No | Keep those results descriptive | Implementer |
| Does a new defect change the arm's meaning? | No | Proceed to scratch tooling and synthetic validation | Implementer |

Reviewed SHA256 observation (not an execution manifest): `CAPACITY_DIAGNOSTIC_SPEC.md` = `3db347a746965e2b91b372cbf1bc309ba98675fa4bcf36fa1d4c6d5157d02ce5`.

Reviewed SHA256 observation (not an execution manifest): `SERVICE_RUN_SUMMARIES.json` = `808f1b0485e647980022a2ed52e644ec5e4990ac646da58fba9044829828616f`.

Reviewed SHA256 observation (not an execution manifest): `kernel_builder/RD3_BUILD.json` = `cf1d2b0a14283faa736876085e97c8a74cf4ab20c1db108fc887d7c8a081df67`.
