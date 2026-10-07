CHANGES_REQUIRED

Reviewer family: Codex
Reviewed commit: `48078a5dc6e8ae273f6d62188e77deb2679084ae`
Review scope: stored A6w/A6x exploratory evidence only. No medium, pilot, simulation, fixture or medium-running test executed. PLAN_CURRENT.md, design files and committed receipts are unchanged.

Owner request, sent verbatim to the separate reviewer `/root/telemetry_recheck`:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

The separate reviewer is Codex-family; this is Codex cross-family review of Claude’s execution/report, not a Claude review of Codex’s diagnostic. No numeric quality score or scientific acceptance is assigned.

Identity before report presentation corrections:

| Artifact | SHA256 |
|---|---|
| SERVICE_RUN_SUMMARIES.json | `808f1b0485e647980022a2ed52e644ec5e4990ac646da58fba9044829828616f` |
| SERVICE_COMPACT_SUMMARIES.json | `2dc71a9bba91dc86aebda36ea2a14deff4560d3c266a30aa614377bbe8363b72` |
| SERVICE_TELEMETRY_REPORT.md at reviewed commit | `b8fdac8ac9a5f64f92baa21a9be4590ed806ca1641ca27788bff2f0515dde997` |

**Medium — B classification contains eight event-boundary artifacts.** The observer appends every accepted terminal to open outages, then calls `transition()`; a restoring birth closes the outage before its reduced gap sample is appended. Eight completed outages receive B solely from the repairing birth at `end`, without an accepted birth earlier in the outage. They therefore do not support “births occurred but the gap did not shrink.” This is a classification defect even though all primary labels remain unchanged.

| Variant/start/key | Site | Outage seconds | Stored primary |
|---|---:|---|---|
| SCR/ii/0 | 5 | 413–440 | X (N/S tie) |
| SCR/ii/0 | 6 | 413–440 | S |
| SCR/ii/0 | 7 | 413–440 | X (N/S tie) |
| SCR/ii/0 | 6 | 680–720 | X (C/S tie) |
| SCR/ii/0 | 7 | 680–720 | X (C/S tie) |
| SCR/ii/1 | 2 | 521.4–600 | C |
| V1/ii/1 | 2 | 521.4–600 | C |
| RD3/ii/1 | 2 | 521.4–600 | C |

Stored B totals SCR/V1/RD3 are 30/17/17; excluding only these known artifacts yields 24/16/16. This filter does not independently qualify all remaining B labels. **Fix:** sample the post-birth gap for the pre-transition open-outage set and exclude restoring endpoints from non-repair evidence in a future observer revision. The owner permits only report presentation corrections here; observer code and receipts remain preserved. The report now identifies the defect and exclusion. This is the outstanding reason for CHANGES_REQUIRED; it does not invalidate stored service fractions or the coverage diagnostic.

**Medium — The DONE report retained obsolete NOT_RUN and cap claims.** Actual execution was 30 reported trajectories plus one off control, with a 12600-second owner-approved resumed cap. The resumed attempt took 3989.0786 seconds; the first attempt took 2298.9542 seconds. First launch through final completion spans 6792.0893 seconds including the pause. **Fixed:** present completed integrity/execution and the measured timing accurately; retain historical implementation-review statements with their scope explicitly marked.

**Low — V1/RD3 equality was real but did not mean idle routes were absent.** All ten paired state-trajectory digests, assays, legacy summaries and decompressed JSONL streams match. Idle-site routes exist at preceding world boundaries for 23/34 D3 decisions. At seeded key 4, t=420, active sites are 3/4/6 while served sites are 0/1/7. V1 protects 0/46; RD3 protects 25/46, including 24 ordinary elements, but both remove non-service id 43 (lock 0.9897779493981766). The differing rules did not change selected deletions in these runs. **Fixed:** explicitly distinguish physical identity from protection metadata, and avoid a claim of general algorithmic equivalence.

**Low — Non-repair labels have different scopes and are not causal identifications.** C is any global B-path/B1 cost refusal during the outage; B is any global accepted birth with the sampled gap condition; N tests requests naming that site. Nine C-labeled outage rows have no named-site cost refusal in the strict pre-restoration interval. N can occur when a site is inactive: SCR empty key 4, site 0, 760–800 has zero active steps. The longest outage attached to an assay failure is an associated observation, not an identified F5 failure cause. **Fixed:** state these limits in the report. The coverage diagnostic uses site-specific requests and activity instead.

**Low — Independent reconstruction is limited by retained data.** Logged G-dist/G-deg lengths, held degrees and `32*exp(-r²)/held_degree` counterfactuals validate, with no arithmetic mismatch. However, figures every 50 steps do not provide every exact pre/post transition graph. A/B/E agree with archived raw assay values, but the assay decision streams are absent. Native states are hashed during execution, not archived; digest equality can be independently checked, while the native digest cannot be rehashed from stored traces. **Fixed:** disclose these limits instead of implying full independent causal or numerical assay reconstruction.

Scheduler provenance checks passed. The initial run ticket starts at 13:36:47 (+03:00); its scheduler hash matches the narrowed-pattern source later committed in `6d59273` at 13:39:49. Thus the edit was present before the run even though its commit was later. The final ticket starts at 14:23:30, pins the scheduler committed in `eea6276` at 14:23:29, and covers all subsequent launches. Across both tickets the measured worker, observer, helper, harness, native and variant-design identities are unchanged; only the scheduler identity differs. The resume change reuses the one completed SCR on-run, narrows process matching, raises the approved cap, and moves the off control into Part A. RD3 starts at 15:07:48 after Part A integrity checks. These edits change scheduling/controls, not measured law. No run was silently repeated.

Stored-data verification passed:

- All 93 inventory entries match bytes and SHA256, totaling 407115335 bytes, verified before decoding.
- All 30 legacy summary fields, per-site activity/service counters, degree distributions, outage/removal records, latency and cause totals, and compact aggregates agree with raw traces and receipts. Pass counts are SCR 3/5 empty and 3/5 seeded; V1/RD3 5/5 empty and 3/5 seeded, descriptive only.
- All 20 SCR/V1 summaries exactly match committed historical logs.
- SCR empty/key-0 on/off summaries and state digest `89fcae9f1c53af91a15634d52e7bedb892acdafd1ca749b0933923f57785f981` match. All workers report clone isolation PASS; assertions in the pinned worker compare native bytes and observer/digest sinks.
- D3 removal totals are SCR critical/redundant/non-service 6/4/21 and V1/RD3 non-service 34 each; no forced cuts or protected-over-budget events.

Presentation corrections in SERVICE_TELEMETRY_REPORT.md:

| Fix | Before | Corrected presentation |
|---|---|---|
| P1 | Integrity described as still required | Completed on/off, clone and reproduction checks, with archival limits |
| P2 | Shared 3600-second deadline; throughput unmeasured | Approved 12600-second cap; resumed and overall measured timing |
| P3 | Future/absent raw traces | Existing 93-entry verified local inventory; completeness heuristic caveat |
| P4 | A6w/A6x pending when NOT_RUN | Thirty completed exploratory runs; no formal acceptance |
| P5 | “No native integration/F5 assay executed” | Historical pre-execution focused validation, followed by Claude’s actual batch |
| P6 | Final result review said zero pilots/process-blocked | Historical implementation review distinguished from this CHANGES_REQUIRED stored-result review |
| P7 | Missing result interpretation qualifications | V1/RD3 idle-route distinction, B artifacts/count exclusion, global C/B scope, inactivity/N, associated longest-outage and reconstruction limits |

Recheck disposition: independent findings reviewed against stored evidence and presentation fixes applied. The eight B artifacts remain an explicitly documented instrumentation defect because code/receipt edits are outside the owner’s authorized scope. No medium rerun is needed or authorized for this delivery. Separate Part 2 recheck/disposition is in COVERAGE_DIAGNOSTIC.md; PLAN_CURRENT.md stays unchanged under the owner’s instruction.
