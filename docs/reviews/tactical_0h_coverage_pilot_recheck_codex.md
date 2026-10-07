APPROVE_WITH_NOTES
Reviewer family: Codex
Reviewed commit: e4c6d75d348731d707a1f7dab16250c6a396dc43

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Stored-data review of `COVERAGE_PILOT_SPEC.md`, including Amendment 1, `COVERAGE_PILOT_REPORT.md`, both coverage summary files, scheduler/worker/observer/kernel source and build identities, and the RD3 `SERVICE_*` / `COVERAGE_DIAGNOSTIC.*` control evidence. This approves the bounded exploratory reporting with the limitations below. It is no experimental verdict, owner acceptance or A7 authorization. No pilot, medium integration, assay, recorded panel, process-list call or proposed economy mechanism was run.

The repeatable audit is `medium_variants/recheck_coverage_stored_codex.py`; its output is `COVERAGE_RECHECK_VERIFICATION.json`. It uses only standard-library file parsing and arithmetic, and verifies raw identities before gzip decoding. It excludes `docs/PLAN_CURRENT.md` from every identity manifest. The owner's explicit instruction supersedes normal plan tracking here: no plan, design, historical receipt, kernel, observer or scheduler file was edited.

Findings and disposition:

| Finding | Severity | Disposition |
|---|---|---|
| The report retained the historical 3600 s cap although the executed scheduler and both ticket deadlines use the owner-approved 5400 s cap | Presentation | Corrected only the report; the unchanged spec states the original cap and the scheduler source records the owner's pre-run approval. |
| The final-ticket dump obscured the interrupted first attempt and resume; the external 28+2 count does not describe the retained coverage schedule | Presentation | Replaced the report's huge embedded dictionary with both attempts' timings, stop reason and 20+2 coverage-slot partition. The earlier SERVICE batch has 30 runs; the coverage batch has 22 slots. |
| The declared reading requires doubling pooled active time for sites 3–6 and complete runs, not merely a higher coverage value or stronger seeded passes | Interpretation | Both readings are correctly DESCRIPTIVE. Added the exact doubling boundary and rounded ratios to the report. |
| The reviewed commit title says sites 4–6 stay below 10%, but COVA site 4 is 12.5069% | Historical-title overstatement | The report and JSON already give the correct value; immutable commit history is retained and this note qualifies the title. |
| COVA redistributes coverage and reduces service at some other sites | Non-blocking interpretation | All eight fractions remain visible. Report now highlights the reduction at sites 1 and 7; the sites 3–6 pool does not establish overall fairness. |
| Archived A/B/E aggregates exist, but underlying assay decision streams were not retained | Evidence limit | Assay aggregates match archived raw values; gate inequalities and all downstream totals were recomputed. Independent signal-level assay recomputation is unavailable and would require new execution, which is outside this task. |
| Ticket files are finalized in place after worker completion | Provenance limit | Completion `ticket_sha256` binds the original RUNNING ticket bytes; finalized ticket bytes differ and cannot recreate that digest. Identical recorded code baselines, checked current dependency hashes, slot markers, local completion equality and raw hashes provide the retained resume evidence. No claim of an independently recreated original ticket is made. |
| RD3 lacks every intermediate post-birth outage boundary | Evidence limit | Its B remains `legacy_B`, separate in aggregate and per-outage outputs. It is never mixed with Amendment-1 B. |

Resume and integrity:

- All **64 coverage** raw inventory entries, totaling **284,836,747 bytes**, and **93 SERVICE** entries, totaling **407,115,335 bytes**, match their recorded sizes and SHA256 hashes before decoding.
- All **1,486** code/dependency identities match the retained scheduler baseline. Both ticket baselines and all completion baselines agree; local completion JSON agrees exactly with the committed coverage receipt.
- The first ticket started **20** slots and stopped launching on projection **5767.1 s > 5400 s**, while retaining completed work. Its elapsed time was **2840.385959375 s**. The resumed ticket reused these **20** identity-verified completions and started only **COVB ii/k3 on** and **COVB ii/k4 on**, with elapsed time **837.393980041 s**. These are the two slots absent from its reuse list.
- Exactly **22** distinct expected slot markers, local summaries and raw logs exist, partitioned 20/2 by the ticket recorded in each exclusive `.started` marker. The scheduler and worker use exclusive creation and refuse started/incomplete reuse. No stored evidence indicates a slot started twice. This establishes consistency of the retained once-only evidence; it is not a historical OS process census.
- COVA and COVB on/off controls both have equal complete state-trajectory digests and equal legacy summaries. Clone-isolation checks are recorded PASS for every completion; worker source checks live native state, observer/digest state and the new kernel fields around clone operations. Raw stored geometry cannot recreate native save-state trajectory digests independently.

Numeric and label checks:

- Every coverage legacy summary field is recomputed from archived steps/events except A/B/E, which is compared with its raw archived aggregate. RD3 control coverage and gate values are reused without changing the historical receipts.
- Each on run contains **8000** world boundaries at 0.1 s; all eight per-run active, active-served and all-time served censuses agree with telemetry. Per-run sites at 50%, pooled active-time fractions, empty/seeded pass counts and Amendment-1 readings agree with the compact summaries.
- RD3 sites 3–6: **19,735 / 229,440 = 0.08601377266387726**. COVA: **28,120 / 229,440 = 0.12255927475592747**, about **1.425×** RD3. COVB: **31,301 / 229,440 = 0.13642346582984657**, about **1.586×**. The doubling threshold is **0.17202754532775452**. Empty passes are RD3/COVA/COVB **5/5, 5/5, 5/5**; seeded passes **3/5, 5/5, 4/5**. All ten on runs complete for each arm. Neither arm doubles coverage or meets the regression rule.
- Raw outages, latency/cause totals, realized-degree counts, request and terminal records, D3 removals, site births/outcomes and first-cost timing are checked against their summary projections. Revised B is reconstructed from the outage's own non-restoring accepted-birth records, its initial gap and retained world/post-birth gaps. Restoring terminals and endpoint samples are excluded; all post-birth endpoint samples have duration weight zero. New outages are matched by their own site/start identity and inherit no earlier births.
- COVA has **17** outages and **11** revised B observations; COVB has **127** outages and **21** revised B observations. These counts retain B's global descriptive scope. C is a terminal resource refusal and N a request naming the site; none identifies a causal non-repair mechanism.
- COVB has **212** recycle records, all non-service donors; **184** retries are accepted and **28** fail. Of the accepted retries, the requesting site is served within 60 seconds in **51** cases, unserved for that window in **112**, and censored in **21**; the observer checks and compact summaries retain donor age/lock, the single retry terminal, and served-within-60-second outcomes. The implementation excludes attempt anchors, rechecks geometry/admission after removal and retains removal on retry failure. A donor's present non-service class does not establish lifetime waste.

The final expanded stored-data audit returned **PASS with zero errors**, including 30 on-run censuses (ten RD3, ten COVA and ten COVB), both off controls, compact birth/outcome metrics and independently recovered recycle outcomes. Separate byte comparison confirms the spec, both coverage summaries, both SERVICE summaries and COVERAGE_DIAGNOSTIC.json remain identical to the reviewed commit.

No new simulation tests were needed for report-only changes and a stored-data verifier. The audit script performs assertions on the retained evidence; it does not import or execute project simulation modules. Historical receipts and the sealed report writer remain unchanged, so rerunning that historical writer would regenerate its historical presentation errors. Use this recheck and its recorded report corrections as the current review disposition.
