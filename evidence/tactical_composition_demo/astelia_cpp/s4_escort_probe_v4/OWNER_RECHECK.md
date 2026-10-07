APPROVE_WITH_NOTES
Reviewer family: Codex (separate-agent same-family implementation recheck)
Reviewed workspace HEAD: cdced329469bb75fbf445a36c872833d6b8ed6f5
Scope: new uncommitted v4 implementation batch, before seal and final focused checks

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

This independent supporting agent reviewed v4 against DESIGN_0G section 19.12 and inspected the complete planned implementation and review-driven correction batch. It is explicitly a same-family fallback: the root reports Claude CLI authentication as loggedIn false. Root Codex separately owns the cross-family stored-run review of the Claude-executed v3 run. No numeric quality scores are assigned. No combat, process listing or tests were executed by this reviewer.

The owner explicitly excludes edits to docs/PLAN_CURRENT.md and DESIGN_0G.md. This file records the implementation recheck and dispositions instead. Existing v3 code, declarations, entropy and evidence receipts are unchanged; the root's separately authorized v3 report correction is presentation only.

## Findings and dispositions

1. **Completion metric revalidation.** The initial resume verifier hashed stderr but did not parse/recheck its one-fight and hidden-work counters or compare those metrics with the completion receipt. Fixed in new v4 run.py: verified_metrics requires exactly one executed fight, positive executed steps, empty fork_settings and zero for all thirteen recorded hidden-work counters. Both execute and verified use it; resume also requires exact equality with receipt metrics. A synthetic matching-hash hidden-work rejection case was added. Static inspection confirms the native v3 stderr schema contains the required fields.

2. **Durable receipt names.** The initial exclusive/atomic writers fsynced file contents without syncing their containing directory. Fixed in new v4 common.py: sync_directory follows exclusive receipt creation and atomic replace, and make_directory syncs the parent when RAW is created. Requests and claims complete those operations before process spawn. Engineering and panel paths use make_directory. A synthetic sync-order case was added. This narrows the filesystem crash window; actual durability still depends on the host filesystem honoring fsync.

3. **Pgrep malformed-negative consistency.** Resume required an actual final pgrep attempt with return code one and empty stderr/stdout, while the live gate initially accepted nonempty stdout with return code one. Fixed: the live CLEAR condition now also requires empty stdout. The malformed-negative synthetic case was added, and each test attempt keeps its own receipt.

4. **Control receipt canonicalization; initial async explanation withdrawn.** The reviewer initially alleged a routine resume ordering defect caused by asynchronous completion order. Inspecting the inherited BoundedPool showed it yields futures in submission order, so that explanation was incorrect and is withdrawn. Root nevertheless sorted control_ids and added an order-invariance synthetic check as defensive canonicalization. This is a robustness improvement, not evidence of a failed ordinary v3/v4 resume.

All four dispositions were statically checked after the complete correction batch. No remaining preseal implementation blocker was found.

## Confirmed implementation boundaries

- The declared panel is twenty clusters times two paired orientations times P12/P16 times regular/novice: 160 fights, forty per arm/head. Eighty P12 controls complete and their sanity receipt is reported before P16.
- No new controller executable is built. v4 uses the exact admitted v3 native executable, its source manifest, original controller dispatch and inherited knobs/templates. Its native fixture includes the original v3 header and links existing v3 objects while replacing only the fixture host object.
- Seal generation checks original v3 implementation hashes and admitted binary identity, records twenty development seeds plus a separate engineering seed, and collision-checks prior declared development ledgers/declarations without opening judging files. The final actual entropy collision/identity check belongs to root's seal/validation pass.
- The prospective seal protects code, native binaries/manifests, policies, templates and development ledgers. It explicitly excludes docs/PLAN_CURRENT.md and DESIGN_0G.md; their restoration is unnecessary for Claude execution.
- Engineering checks all planned panel tags, then all engineering tags before new combat. Panel execution verifies all four engineering tags and scans every planned panel tag. Exclusive pre-spawn requests/claims preserve ambiguous attempts; they are never replayed. Missing combat blocks/resumes obtain unique timestamped pgrep gate receipts; active pilot batches wait and unreadable/error process access fails closed.
- The inherited pool has at most two workers with a bounded submitted queue. Deadlines track and kill only owned child process groups. Stage receipts enforce cumulative compute and combined panel caps; the projection reserves 900 seconds for analysis.
- Analysis verifies the exact raw inventory and every expected completion before parsing gzip streams. Analysis completion binds COMPACT/SUMMARY hashes, declaration, fight ledger and inventory; resume verifies those identities and skips recounting a completed analysis. Rendering verifies that receipt and reports all inherited measurements, paired orientation outcomes/S, mean-S differences and uncertainty.
- Replicated requires all six section 19.12 conditions: P16 regular wins at least 26/40, positive regular and novice mean S, novice wins at least 21/40, no failures, and P16 having more wins than P12 in at least twelve of twenty regular clusters. Regular wins at most 20/40 means Not replicated; other failed conjunctions are descriptive. Execution failures stop as partial evidence rather than becoming manufactured nonwins.
- Cluster uncertainty averages the two paired orientations first and uses twenty cluster observations with sample SD divided by sqrt(20), an approximate unbounded t95 interval with nineteen degrees of freedom, and explicit descriptive/zero-variance limits. It does not count forty orientations as independent trials or add an uncertainty threshold to the reading.
- Delivery uses explicit task paths, normal hooks and the required provenance trailer. It excludes plan/design, preserves unrelated staged paths, supports an isolated current-HEAD bundle when main .git is unwritable, independently fetches that bundle and compares each intended committed blob.

## Remaining verification and limits

Seal generation, the final focused noncombat test batch, exact sealed-artifact validation and commit/bundle verification are pending at the time of this preseal note and belong to root. No test success or delivery success is claimed here. Root may record their receipts separately after they complete without changing scientific rules.

Claude must subsequently run engineering.py, run.py, analyze.py and render.py without edits, with the mandatory live process gate. Those engineering/combat results and the eventual replication outcome remain unmeasured. This review authorizes no judging run, registration, scientific acceptance, automatic approval of draft v7, or resonator/source claim.

## Final sealed-artifact recheck

APPROVE_WITH_NOTES. After the seal and final checks, this supporting reviewer independently hashed all 503 protected files and all sixteen v4 implementation files, plus declaration/seal/policy/development-ledger/templates. All identities matched. The actual seal excludes both PLAN_CURRENT.md and DESIGN_0G.md. BUILD, CHECKS and the declaration all identify the exact original v3 executable SHA256 83a6c10f24901760bc028c328895024dbc3a14cc9da4799928b6ad1f8699c871 and original manifest SHA256 bb62a17635af34546c924ae53db9dd678e5bedf58ac5198a02406cc9f4f69fe9; the local executable and manifest bytes match those hashes.

All twenty panel development seeds and the separate engineering seed are unique, agree between declaration and ledger, and are absent from all integer values in the twenty-five recorded prior development ledgers/declarations, whose hashes were also verified. No judging ledger was opened. The final test log reports seventeen noncombat checks passed in 2.14 seconds with empty stderr, and its CHECKS receipt binds the same declaration/native identity. This reviewer read the existing logs without rerunning tests.

Rendered report and COMPACT are NOT_RUN with zero completed fights and unclaimed entropy. There is no v4 raw directory, ENGINEERING receipt or live PILOT_GATE receipt. The existing VALIDATION is PASS and all its checked hashes match; all delivery paths are within the two task evidence directories plus the explicitly authorized corrected v3 report and root review. This note append requires root to refresh VALIDATION before delivery; no scientific or executable bytes changed. Final commit/bundle hook success and independent bundle-fetch verification remain root-owned and are not claimed here.

The root reports its complete stored v3 recount has now passed in 495.530 seconds. The earlier supporting v3 note's pending-at-time wording remains an accurate historical record; the completed root receipt supplies that verification. No new issue was found in this final artifact pass. No tests, combat or process listing were executed by this reviewer.
