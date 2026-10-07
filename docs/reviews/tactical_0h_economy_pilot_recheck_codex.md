APPROVE_WITH_NOTES

Reviewer family: Codex
Reviewed commit: cbe2da2b326ab9f495598ccffc1d6a1630352da2
Scope: stored-data cross-family owner recheck of the exploratory economy pilot, including specification Amendment 1, report, compact/run summaries, raw identities and retained scheduler records. No pilot, medium run, assay, simulation or project test was executed. No design, receipt, status or PLAN_CURRENT file was changed or pinned.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

The completed exploratory measurements and their incomplete-arm reading are usable. This approval is of the stored pilot evidence and bounded descriptive interpretation. It is not scientific acceptance, authorization to execute another run, or permission to complete the missing slots. The report has the errata and reconstruction limits below; the immutable report is preserved, with these corrections recorded here.

## Identity and resume findings

- Verified size and SHA256 of all **58** entries in ECONOMY_RUN_SUMMARIES.json's raw inventory before decoding raw data. All match. Verified all **1490** recorded code/dependency paths against current bytes, all four compact source hashes, and the exact equality of the **20** local completion summaries to their committed run rows. No excluded design/PLAN file appears in the dependency pin set.
- There are **20 distinct** completed slots: ECOF 10 on + 1 off; ECOR 8 on + 1 off. Each has one exclusive `.started`, `.raw.log`, `.harness` directory and `.summary.json`. The only absent planned slots are `ECOR_ii_k3_on` and `ECOR_ii_k4_on`; neither has a started marker. No unexpected or duplicate slot occurs in the receipt or markers.
- The retained launching tickets are `RUN_TICKET_1791390953998839000.json` and `RUN_TICKET_1791399659140384000.json`. Ten markers reference each. Their launch sets are disjoint; the second ticket reuses exactly the first ten completions. Both are PARTIAL with projection stops, not interrupted or incomplete worker completions. All trajectories completed 8000 steps through t=800.0, with positive finite wall/CPU times and clone isolation PASS.
- The stored final tickets were rewritten by the scheduler after completion. Reconstructing each original RUNNING ticket using its initial fields, original ordering and `json.dumps(..., indent=2)` reproduces every completion's `ticket_sha256`: first `3091792dbf15d9d537b8b3f88737f1849fe4a38b573a3dc5931d0db4292c1eeb`, second `c21aa748700cb5988c078c1ef44ae42a9c855393e43bc1555a738b274623f90f`. Final-ticket hashes must not be mistaken for the original grant hashes.
- `execute_economy_plan.py` at ac1fa4b, restoration commit 6bf50d0, reviewed cbe2da2 and current working tree has identical SHA256 `42e9bd1da5688469595280962a708e722abc42a3827a1747cfdb2fa2679c224d`, including cap5400. The cap-edit/restoration history is consistent with 6bf50d0's recorded explanation. Both launch-ticket code maps equal all completion code maps.
- These records support **no slot run twice within the retained schedule**. They do not independently prove the host reboot event or the existence/timing of a failed identity-check invocation: no additional launch ticket was created for such an invocation. The supplied operational history is not a third measurement attempt. This limitation does not invalidate the retained completions.
- Each arm's on/off pair (`i/k0`) has identical aggregate summary and full state-trajectory digest, with clone isolation PASS. ECOF digest includes economy clock/deficit state, unlike historical RD3; differing cross-arm digests are expected and cannot substantiate a failure or a claim of full native-state equality to RD3.

## Numerical audit

All **18** observer-on traces contain exactly 8000 sequential world-step records. Independently recomputed all eight active/active-served counts and fractions from these records; they match completion and compact data. Raw removal, outage, stall, prospective-check/trial, first-candidate-refusal records and the last mass allocation at each recorded time match completion telemetry. All per-site compact totals, per-start gate counts, class means at the 160 fixed5s samples, removal/prospective totals and prospective timing sums agree with independent arithmetic. Class totals conserve the recorded cost.

- ECOF pooled sites3–6 is exactly **19735/229440 = 0.08601377266387726**, matching RD3. Empty **5/5**, seeded **3/5**; all ten runs complete. DESCRIPTIVE is the declared reading: no doubling.
- ECOR pooled sites3–6 is exactly **10484/186400 = 0.056244635193133045**, using its **eight** completed on runs. Empty **0/5**, seeded **0/3**, so **0/8** observed shapes pass. INCOMPLETE is correct; missing trajectories are not failures and the declared full-arm REGRESSION reading is unavailable.
- ECOR **53 D5r removals**, **183 triggered checks**, **53 candidate trials**, **0 failures**, **130 no-candidate checks**, **0 no-passing checks**; prospective wall **0.1645645850002211 s**, CPU **0.061050000000108184 s**. Zero failures has a 53-trial denominator. Neither the prospective timings nor their sum explain the thousands of seconds of worker/scheduler time.
- ECOF has **0 D5f removals**, but **71 D5f_none events**, all `no_eligible_front`. Its stall clock reaches **60 s at 76 end-of-check site records**; five occur at the final t800 check and have no next donor check. Thus all 71 actionable thresholds activated at the next check and found no eligible donor. The arm did not test actual front retraction. The commit message claim that the clock never reached60 is false; replacing only the progress definition is not demonstrated to cure donor ineligibility.
- Every displayed A/B/E value agrees between the run, compact and legacy raw aggregate; every displayed gate flag matches `A>=.3 and B>=.3 and max(E)>=.5`. **A/B/E cannot be independently recomputed from retained traces**: the assay stores its aggregate, not checkpoint snapshots and the individual own/donor/output-lesion decision streams used for its means. This audit verifies consistency and gate arithmetic, not an independently reconstructed assay.
- Reported outage label totals match raw final outage records and compact summation. RD3 retains legacy_B separately. ECOF's revised B16 versus RD3 legacy_B17 is a label-protocol difference, not a trajectory change. Zero D5r break labels establishes no recorded immediate service loss in the observed removal context; it does not establish preserved signal or future robustness.

## Report errata and interpretation notes

0. The reviewed commit message attributes ECOF inertia to its clock never reaching60; raw data refute this (76 threshold records, 71 actual no-donor triggers). The report table’s ECOF “Triggered checks0” counts **prospective ECO-R checks**, not front-clock triggers, and is misleading under a generic heading. ECOF clock/donor analysis must use its stall and D5f_none records.
1. The sentence “Pooling sums ... over ... all ten on runs” is false for ECOR's displayed provisional coverage. It uses eight completed runs, as the numerator/denominator above show. Comparisons intended to attribute an ECOR effect should additionally match RD3's same eight slots; the full ten-slot RD3 total remains the declared target baseline.
2. The historical projection paragraph says **3987.979 s** is “above the fixed cap” and a new schedule must stop before launch. That was true for the old cap3600, not the executed cap5400. Its final denial of native on/off trajectory identity until pairs complete is also stale: both pairs are complete and PASS. The exact unrounded historical projection is **3987.979063749 s**. Final attempt initial projection **4372.95988575 s**, elapsed **2011.138375583 s**, and projection stop **6255.6 s > 5400 s** are consistent with stored timing.
3. The cap5400 is an explicit scheduler change relative to the spec's implementation cap3600; the scheduler attributes it to owner approval/decision0031, and ac1fa4b/restoration preserve it. This review confirms retained byte identity and executed cap, not an independent recovery of the owner's off-repository approval message.
4. ECOF exactly matches RD3's retained 8000-step legacy trajectory fields and fixed5s figure geometry/strong graph/spring pairs for every matched run, and has identical assay aggregates. This is strong stored-observation equality, **not independent equality of every native phase, RNG/history byte or unrecorded intra-boundary state** across arms. Native phases are absent from raw figures/world-step/legacy-step data.
5. ECOR's worse descriptive signal and coverage support the concern that Boolean geometric service redundancy is insufficient as a signal-preserving deletion criterion. They do not alone identify loss of parallel paths or phase coherence as the unique mechanism, nor turn its incomplete arm into a declared regression verdict. Part2 should quantify recorded structural changes and expressly separate them from unrecorded phase/assay chronology.

Recheck disposition: measurement/resume identity checks PASS; report wording corrected by this additive erratum; reconstruction limits made explicit. No rerun is required or authorized by these findings. The separate stored-trace diagnostic and its separate owner recheck remain the next deliverable, outside this Part1 pass.

Reviewed artifact SHA256:

| File | SHA256 |
|---|---|
| ECONOMY_PILOT_SPEC.md | 9ab8366447412c3d27c8fda6cdef6f04dc34deedb355ea903604267e7909636d |
| ECONOMY_PILOT_REPORT.md | 33f4d701156bf6098ed3dfd50d17453a9812d3ae2f9db1f48b08c377683fcd38 |
| ECONOMY_COMPACT_SUMMARIES.json | e9a4fc3799a1ee51d1ebb255386a1caa0b84d03c4e24a1b8216bccef6bfe2d6f |
| ECONOMY_RUN_SUMMARIES.json | 7bfd021374128dcf5ff84692264975cad4d47967cc4987e2a435ff796c7c3761 |
