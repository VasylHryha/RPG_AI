CHANGES_REQUIRED
Reviewer family: Codex
Reviewed commit: 183766ae05e416f27f9d431f7ea6935bbd8c80d3
Date: 2026-10-07

Owner request, verbatim:
> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Scope: round-3 owner recheck of Claude's revision-3 OPIN_VALIDATION_REPORT, STORED_ANALYSIS and its analyzer, DESIGN_0H_REV7 §19.7, and PLAN_CURRENT A6s/A6u against the round-2 findings. Supporting reads include Harness.require/F5–F9/run_all, keys(), Run initialization, medium cloning, entropy inventory and local stored traces. No simulations, pilots, fixtures, panels or tests ran. The analyzer's authorized read-only functions were used without its writing entrypoint or project imports. Only this review file was written.

The five scoped files match the reviewed commit byte-for-byte. SHA256:

- Report: `b324f12b1cc759d65a325c7ed7d31a89c4912d887a8aff8777ab95a3faf7ee01`.
- Stored analysis: `3abf831ca24c6d5237f5fbe56c5bdcb94545f42e08d3eaf87115d1723d2afea9`.
- Design: `1b6ef535c0cb74839e2337c7f902a479b36fb9337435b49e88f8a4e210a5da4d`.

R2-F2 and R2-F3 are resolved. The JSON/analyzer correction for R2-F4 reproduces, but the report still mixes per-site and any-site measurements. R2-F1's normal execution path is now specified; its new INVALID recovery rule remains inconsistent. The remaining findings below need document changes, not another experimental run. This review does not approve C2 adoption, §19.7 execution, development or scientific qualification.

## Remaining findings

### R3-F1 — MEDIUM: the downstream INVALID row permits continuation from state that fails its own identity check

DESIGN §19.7 line 1064 combines a missing decision record with a retained g = 1 fingerprint mismatch, then instructs the implementer to “fix; rerun from the same retained state.” A corrupted retained source cannot become an authentic F5 checkpoint merely by rerunning its consumer. Lines 1040–1041 prohibit regeneration/substitution, leaving no operational repair for that case. Unlike the F5/F7 retry rules at lines 1015/1063, this row also gives no restriction to instrumentation defects proved before results are read. It must retain the inherited measurement-failure stop at line 384, which blocks the next stage.

**Concrete fix, drafter before owner approval:** split the two cases. A missing-record instrumentation defect can permit a rerun only if established before outcomes are read, from a fingerprint-verified retained source, with identical worlds and keys; keep the failed attempt and its evidence. A retained-source mismatch must mark INVALID and block continuation, with no regeneration, substitution or rerun under this amendment. If authenticated restoration is intended, specify its immutable source and complete native/Python/RNG identity check in advance. Do not authorize repairing or updating the expected fingerprint to fit the damaged state.

### R3-F2 — MEDIUM: per-site exposure is still overstated in two report sentences

Report §5 line 134 says seeded key 1's “sites 0, 1 and 7 had a path in 95% of the late samples.” The raw trace gives:

| Measurement | Connected / denominator | Fraction |
|---|---|---|
| Any site, all late samples | 1,526 / 1,600 | 95.375% |
| Site 0, site-active late samples | 1,046 / 1,120 | 93.393% |
| Site 1, site-active late samples | 1,206 / 1,280 | 94.219% |
| Site 7, site-active late samples | 1,206 / 1,280 | 94.219% |

Across all late samples, those individual sites have paths in 65.375%, 75.375% and 75.375%, respectively. The 95% figure belongs to the any-path aggregate. Thus R2-F4's denominator/aggregation correction is not yet complete in the prose, although STORED_ANALYSIS is correct.

Report §4 line 118's revised examples have five zero E entries, but “five of eight sites never reaching O” still extends assay/late-window absence to the whole trajectory. Empty C2 key 1 has nonzero whole-run conditional connectivity at site 7 (`0.129`), despite E[7] = 0 and no late site-7 path. Seeded C2 key 0 similarly has a transient site-6 path (`0.018` whole-run conditional connectivity) despite E[6] = 0. Both examples have four sites with no recorded training path, not five.

**Concrete fix, drafter:** describe key 1's 95.375% as the any-site fraction, and give the separate conditional site fractions if retaining per-site detail. Replace “never reaching O” with “zero recorded assay exposure at five of eight sites”; distinguish late training coverage from whole-run connectivity. Retain the supported warning that max-E success does not establish broad causal response.

## Nonblocking notes

**N1 — LOW, precedence wording:** DESIGN line 1017 says §19.7 replaces “only” the single-key F5 verdict/stop row, but lines 1023–1029 also replace F7 aggregation and the downstream order. Existing `Harness.run_all` (rev7_fixtures.py line 378) runs F6 before F7; F6's `require` does not demand F7 PASS. Consequently “no downstream fixture runs, as now” after F7 failure is inaccurate for F6. The proposed sequence is explicit and compatible with the existing guards. State that the amendment also supersedes F7 aggregation and downstream scheduling while preserving `require`; remove “as now.”

**N2 — LOW, new distance overgeneralization:** report §3 line 85 says “passing direction controls end farther away.” Opposite empty key 1 passes at 0.329 m.u., closer than its matched toward-root pass at 0.391. Perpendicular empty key 1 also passes at 0.369. Keep the supported 1.19 opposite-empty-key-0 example, but say that **some** passing direction controls end farther away; avoid a general ordering of distances.

**N3 — LOW, ancillary evidence identity:** report §5 line 146 adds the observation about D3 removing a path element in two failures from A6v's different law. Local `signal_loss/ANALYSIS_OUTPUT.txt` and `D3_EVENTS.txt` describe the two matching examples (element 15 at 560 s and element 12 at 460 s), but that directory is untracked and absent from the reviewed commit; the named raw gzip traces are not present there. This claim cannot be independently rederived from the available bound artifacts here. Link committed evidence with recoverable raw locations/hashes when A6v is delivered, or mark the ancillary observation pending that evidence. It remains separate from the O-pin conclusions.

## Verification and disposition

All 34 regenerated analyzer rows equal STORED_ANALYSIS after JSON-key normalization, including both whole-run and late active counts. A is bound by the analyzer; independent log reads confirm B and every E entry. All 34 raw files match manifest byte counts and SHA256: 30 in RAW_FILES.json and the four earlier assays in the parent directory's RAW_FILES_OUTSIDE_GIT.json. The pooled counts reproduce as 3/10 versus 8/10, with five paired gains and no losses. Direct stored-trace reads confirm the added 16/34 post-refusal-birth count, 280–480 s refusal range, seeded key-3's 13 holds and 360 → 362.4/362.5 → 380 s event order, seeded key-1's 792.6/792.7 s loss bracket, and seeded key-4's 1,120/1,600 active-connected samples. The two corrected five-zero E vectors and the scoped distance ranges reproduce; the new broader distance sentence is addressed in N2.

For the normal gate path, M's four named recipes match keys('i', 'M') with the gate suffix; matching worlds and intact comparator identity are specified. The six g = 1 checkpoints and live source are retained. F6/F8 numeric ranges match their constants, F9 retains its guard, and medium cloning preserves histories/timers/clock/RNG. The existing F8 constructor subsequently seeds its growth RNG from the explicitly retained F8 recipe; source retention does not imply continuing F5's growth stream. The 40 distinct proposed F5/F7 recipes produce 40 distinct master hashes with no registered collision. The 250 training IDs and 100 assay IDs are mutually disjoint and avoid registered/pilot pools. The existing cost arithmetic is 4 h serial or 0.8 h with five parallel workers before other fixture overhead; the illustrative one-sided bound is 0.549280.

The owner's verbatim request was sent to a separate Codex reviewer for supporting adversarial scrutiny. That reviewer independently corroborated the recovery contradiction, schedule wording, raw per-site numerator/denominator counts and distance counterexample, and found no additional normal-path key/world/state mismatch. This supporting scrutiny is same-family; this owner recheck remains cross-family against Claude. The completed review's recheck confirmed both remaining blockers and the notes, with no further finding edits required.

Claude, as drafter, should fix R3-F1/R3-F2 and record the recheck/dispositions in PLAN_CURRENT before seeking approval of §19.7. Existing receipts, raw data, status, design/report files and unrelated work were preserved. `.git` and `.git/config` are not writable; this review is left uncommitted under the user's instruction, with no alternate checkout or hook bypass.
