# 0003: C4 R003 fixes the two findings of the R002 review

Date: 2026-10-01. Implementer: Claude. Trigger: Codex's independent review of R002, CHANGES_REQUIRED (`evidence/c4_r002_review_codex/INDEPENDENT_REVIEW.md`). Both findings were verified against the code before any change.

## Findings and fixes

- **R1 (high): recovery accepted fragmentation.**
  - The defect: criterion 5 compared the kicked future with the control future's best-matching component, but never required the original group to survive. A group that split identically in both futures passed.
  - The fix: the original members must be matched (Jaccard ≥ 0.9) in the control future and in the kicked future, and the two matched components must agree. All three scores are now stored in the receipt.
  - The reviewer's reproduction is now a contract that must reject such a group, alongside a positive control.
  - This applies to every candidate, so formation counts and the population used for causal endpoints may change. That is why R003 reruns everything on fresh seeds.
- **R2 (medium): conflicting formation rule.**
  - The conflict: the R002 manifest said "NOT_SUPPORTED if any of these FAILs", which includes formation. The code and the owner-approved proposal make formation failure INCONCLUSIVE.
  - The correction: decision 0002 wrongly said the formation rules were unchanged from R001. This record corrects it.
  - R003 registers an explicit truth table that follows the approved proposal. The reason is a principle, not an outcome: too few resonators is no evidence about their two-way coupling, and formation failure is reported by its own endpoint.
  - This rule was chosen without R003 data. R002's recorded verdicts stay as recorded, with this conflict noted.
- **Reviewer observation, also fixed:**
  - The issue: the clump control was vacuous in the heterogeneous arm.
  - The fix: the clump endpoint now reports NOT_TESTED when there are no candidates, and the gate requires a non-vacuous PASS in the identical arm.

## Unchanged

- Model, integration, detector thresholds, interventions, doses and effective-state bounds.
- Development worlds and every other registered rule.
- R001 and R002 evidence and reviews are preserved as committed.
