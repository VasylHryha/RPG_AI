ENGINEERING_RECHECK_PASS

# Owner recheck: authorized development shape lab

Reviewer family: Codex
Reviewer: separate Codex agent; same family as implementer, as explicitly requested.
Scope: new s4_shape_lab_v1 tooling against SHAPE_LAB_SPEC §§3–6. This is an engineering recheck, not milestone acceptance or a scientific verdict. No project code, fights or tests were executed by this reviewer.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Findings sent to the implementer

1. **High: dummy abilities escaped the dummy contract when globally enabled.** Delivered World::create resets every named controller's ability policy to Auto, overriding the request's Off setting. Original lab creation did not restore dummy-side Off unless both armies' abilities were disabled. Requests enabling sandboxAbilities could therefore give static/advance dummies charge, disengage or artillery abilities. The delivered request template disables global abilities, so default drills did not exercise this defect; original small checks also disabled abilities globally and hid it. Fix dummy-side policy after delivered creation, independently of global abilities; exercise dummy checks with global abilities enabled. The new native override was inspected and addresses the policy issue; required checks remain the execution proof.

2. **High: run was permanently blocked by its own projection.** Original project() always wrote total_projected_seconds=null; run() immediately rejected null and overwrote any supplied estimate. The revision produces an explicit conservative serial estimate from measured compatibility output plus historical full-elite per-step timings with a declared margin. The historical profile differs, so this remains a planning estimate; it must never be called a measured upper bound. A blocked process gate still legitimately prevents drills.

3. **Medium: failed checks could not be reported.** Original report assumed every CHECKS.json had compatibility_seconds. A FAIL receipt omits that key, making the required stopped report fail with KeyError. Render PASS/FAIL and partial check detail separately.

4. **Medium: non-damaging Slow fields were counted as missed damage shells.** Observer launches include slow=true fields. Original metrics counted them as landed zero-hit shells, inflating D1 missed-shell counts. Exclude Slow field launches from damaging-shell denominators and report their count separately; distinguish ordinary/barrage interpretation.

5. **Medium: deadline and resume accounting.** Original series passed a relative timeout rather than the absolute deadline, permitting admission overhead or queued work to start children after the intended cap. Pass the absolute deadline into each execute and refuse work after expiry. Original run restarted a fresh hour on every invocation; partial resumes must account for earlier attempts under decision 0031. Preserve failed/unfinished cells and never silently replay them.

6. **Medium: full receipt identity on resume.** Original execute's cached path checked request equality, metadata and raw hash but omitted claim, declaration and stderr linkage. Verify these recorded links against the current declaration before returning cached results. The implementer has agreed to tighten this path.

## Retracted finding

The review initially inferred array terminal framing from the delivered one-element request ledger. Inspection of delivered run.py confirmed it sends reqs[0] for singleton native execution. Object framing in the lab is therefore correct. This is not an outstanding issue; entire stored-stream equality remains the required check.

## Static confirmations and limits

- Only the new lab folder appeared in git status during review. Delivered sources are derived into ignored build storage and original objects are reused with hash admission; no frozen/delivered bytes need edits.
- Explicit scenario lists retain standard per-role native slots. Reduced placement sorts the survivor cohort and uses first standard role slots, preserving carried identities outside native role-slot remapping. Full HP is set on carry-over; dead members are omitted.
- v7/forcedP16 parameters come from delivered theta origin; v6 uses historical theta. Doctrine requests explicitly retain regular skills; elite reference leaves full scripted lookahead and artillery rollout enabled.
- S10X uses the same predeclared draws for all three arms, replacement draws from the 19-entry pool, fresh 50 enemies, abilities off on both sides, first non-elimination win stopping, and a maximum of ten fights. Cohort mapping is by role slots rather than survivors' output order.
- Section-4 metrics use actual initial army sizes, conditional kill-time denominators and enemy-guns-alive gun damage share. Auxiliary unchanged scorecard is explicitly labeled with its historical fixed-denominator limitations.
- Replay extraction retains all executed fights, enforces the 8,000,000-byte limit, and reduces sampling deterministically. No replay exists for an unrun fight. This review inspects format compatibility; it does not assert visual acceptance of a viewer page.
- Section-3 checks and final focused tests are implementer responsibilities. The initial report correctly claimed neither drill nor series observations. It must be refreshed with actual check/test receipts and projection before delivery.
- Process-list access is unavailable in the managed sandbox, so runs must remain unexecuted until the process gate can be verified. Read-only .git permits the specified uncommitted delivery, listing all new files.
- Amendment 2 teacher/shadow actions are outside the user's requested §§3–6 scope and belong to a later build.

## Disposition requirement

Record each finding's fix and verification in new REVIEW_DISPOSITION.md. The owner's explicit new-files-only/no-existing-plan-edit instruction overrides AGENTS.md plan tracking for this task. Resolve the findings before the final test batch; leave unavailable compute and owner acceptance gates explicit.

## Static follow-up before implementation checks

Inspected the corrected native dummy-side ability policy, the finite disclosed projection, FAIL-safe report fields, Slow launch exclusion, absolute deadline propagation and cumulative RUN_ATTEMPT accounting. These address findings 1–5 in source. The revised healing check uses the actual compatibility survivors and verifies their prior damage rather than only a synthetic survivor list. Full cached receipt linkage (finding 6), required section-3 checks and final focused tests were still pending when this review concluded; the implementer owns their disposition.

One low report consistency note: generate process-gate and commit-state limit sentences from actual state. Hardcoded unavailable/NOT_RUN/uncommitted prose must not survive into a later DONE/committed report after authorized execution access is restored.

## Final follow-up after section-3 checks, before final pytest

All six code findings are resolved in the inspected batch. Cached reuse now verifies declaration, request, claim, stderr and raw hash links, terminal/native metrics, and recomputed measurements. The report renders actual process and delivery receipt state.

Inspected CHECKS.json: all eight rows PASS, including entire decompressed native stream equality and same terminal, dummy contracts with global abilities enabled, deterministic first role slots, and healing the actual 15 survivors while removing 35 deaths. Both stream SHA256 values are `336df649bbe1409b63fa5429737fdb0a6f8b3698e44074b110bc3dac555f9e75`. This reviewer did not rerun checks.

Verified the ten declared local code/ignore file hashes and binary digest by filesystem hashing. Declaration SHA256: `f558ccbb6502a1db885e49b4b750533aba9cef557079dfb1e91c2e2ac6b9cd22`. Binary SHA256: `dba7f3a12f2f9f251ac8147315db1af7c6ec403505ddc4cf20e7ba11fb4ea159`.

Inspected PROJECTION.json and PROJECTION_INTERPRETATION.md: the disclosed conservative serial planning estimate is 175,939 seconds (48.87 hours), with an idealized full sixfold division of 8.15 hours explicitly labeled unmeasured. This uses trace-heavy compatibility throughput and historical elite timings; it does not establish actual lean-lab throughput. The owner's projection stop applies. PROCESS_GATE.json separately records UNAVAILABLE with return code 3 and unavailable sysmond. No drill or series observations are claimed; all outcome cells remain explicitly not evaluated.

Reviewed SHAPE_LAB_REPORT.md snapshot SHA256: `0bd54fce301bd94d8f92c604c306ab8af5c2eec1fd7eb0797cdface2bceaa543`. This identifies the report before final focused tests and any documentation-only receipt refresh; later final report bytes may differ.

Two documentation notes were sent to the implementer: replace stale pending compatibility/dummy/projection statements in REVIEW_DISPOSITION.md with the observed receipts, and correct README's claim that the existing hardcoded stored-fight viewer directly consumes lab names. The extractor supplies the requested JSON schema; the delivered viewer's STORIES table and default pick require an adapter/picker mapping before it can display arbitrary lab groups. No lab viewer visual acceptance is asserted.

Verdict: no remaining blocking code finding for this authorized, uncommitted, PARTIAL tooling delivery. Finish the single final focused pytest batch and update its receipt/disposition. Drills and series remain intentionally unrun behind the time/process gates; this verdict grants neither execution approval nor milestone/scientific acceptance.

## Final receipt and report check after tests

The final read-only recheck confirms all findings and documentation notes are resolved. TESTS.json records a successful single final caffeinated pytest process, return code 0, measured 1.269819042 seconds; TESTS.stdout.log records `17 passed in 0.71s`, and stderr is empty. The TESTS receipt/log hashes match FINAL_VERIFICATION.json. No test or fight was rerun by this reviewer.

All ten declared local code/ignore hashes, declaration digest and binary digest remain unchanged from the passing section-3 checks. CHECKS.json, PROJECTION.json and PROCESS_GATE.json also match their recorded final verification digests. The final report consistently states PARTIAL, eight checks passed, focused tests passed, zero drill/series completions, conservative projection above the owner's limit, unavailable process gate, uncommitted read-only delivery, and the future viewer adapter limitation. REVIEW_DISPOSITION.md now cites the completed checks/tests rather than pending receipts.

Final reviewed SHAPE_LAB_REPORT.md SHA256: `3fecb64825e6140e44a869fb43f89ccda0ce9a8a8c8dfca550f7f0be7591f038`.

Final verdict: ENGINEERING_RECHECK_PASS for the implemented tooling and documented stopped delivery. No remaining required code or documentation correction was found. This does not claim drill/series execution, viewer visual acceptance, owner acceptance, scientific qualification or milestone acceptance. The unrelated research note recorded in the implementer's git-status snapshot is outside this task and was not touched by this reviewer.
