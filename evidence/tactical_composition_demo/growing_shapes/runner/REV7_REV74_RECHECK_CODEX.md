APPROVE_WITH_NOTES

Reviewer family: Codex
Scope: 7.4 source/report changes against DESIGN_0H_REV7.md §§11/11.1 and docs/reviews/tactical_0h_rev74_design_review_codex.md. Separate read-only reviewer rev74_recheck; other-family agents unavailable. This is the mandatory owner recheck, not Claude implementation acceptance or fixture authorization. Review and bounded follow-ups executed no code or tests and made no edits.

Owner request (verbatim):

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

| Finding | Disposition before the single final suite |
|---|---|
| Existing synthetic topology case has no E_i for added IDs, causing KeyError | Populate all three synthetic members/bounds. Reject missing/nonfinite/negative used-pair bounds as INVALID. |
| Estimator active-window denominators and transient exclusions were not summarized | Add descriptive unique requested window ledger: eligible and valid observations, E_i/E_i+E_j exclusions, active-count histogram, below-80 rejections, null when unmeasured. Expose in Run/F5; test 79/80 cases and dedup. No threshold or returned estimator value changed. |
| N1f used theoretical 1/1.8 spacing instead of F1c literal .556 | Match .556 exactly; strict construction equality test retained. |

Reviewer final disposition: all findings resolved; APPROVE_WITH_NOTES for inspected source/report changes. It confirmed solver propagation, held stage lists/carrier, unchanged F1c gate, descriptive margin/hold, source-only packaging size/product guards, historical separation and null costs. Final synthetic testing, pin regeneration and artifact verification remained implementer responsibilities. All disposition tracking stays here and in REV7_INTEGRATION_REPORT.md under the owner's restriction; docs/PLAN_CURRENT.md is untouched.

Assisted-by: Codex:GPT-6

Post-test bounded recheck: the only failing assertion used exact floating-point equality for 11.1 s. Reviewer approved pytest.approx with 1e-12 absolute tolerance and recommended rel=0, applied. No production change. Final corrected synthetic suite: 77 PASS in 4.55 s. Tested execution-pin SHA256: f370c3b5ea17cf0b3c751de794de0c8ab1dffdb35cbffdc35d81f9b8280c3ce5 (not a Claude acceptance binding).

Final delivery recheck: APPROVE_WITH_NOTES. The reviewer independently verified all 68 pinned inputs, the PASS log, 7,010 preservation baseline paths, historical metadata, outer member hashes and the preserved failed attempt. One documentation finding: the delivery note incorrectly stated all archives were excluded, although REV7_FIXTURE_EVIDENCE.tar.gz preserves historical text evidence. Corrected note to distinguish excluded prior delivery archives from that retained fixture archive. Nested historical archive verified: 38 file members, maximum 1,106,238 bytes, text/source/gzip receipts only; zero native products and zero members reaching 50 MB. No production or test source changed; no suite was repeated. The bundle was repacked to include this disposition, then hashes were checked again.
