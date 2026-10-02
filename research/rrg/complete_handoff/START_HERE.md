# RPG_AI + RRG v0.2.1 — complete current handoff

**Date:** 2026-10-02

This bundle puts the latest audited RRG documents and the RPG_AI alignment/forward instructions in one place.

## Read in this order

1. `RRG_CURRENT/README.md` — current audited RRG v0.2.1 reading guide.
2. `RRG_CURRENT/04_recursive_background_generation.md` — current full conceptual/source-direction companion.
3. `RRG_CURRENT/08_claim_coverage.md` — claim registry and boundaries.
4. `RRG_CURRENT/07_audit_report.md` — corrections and remaining gaps.
5. `RRG_CURRENT/foundations/ERRATA.md`, then foundations 01–03 when their historical definitions/details are needed.
6. `instructions/RPG_AI_RRG_V0_2_1_ALIGNMENT_HANDOFF.md` — executable alignment and forward-work instruction for the live `VasylHryha/RPG_AI` repository.

`RRG_CURRENT/05_mathematical_source_model.md` is optional mathematics, not the definition of the theory. `RRG_CURRENT/06_evidence_catalog.md` is the active evidence map. `RRG_CURRENT/MANIFEST.json` and `SHA256SUMS.txt` pin the release contents.

## Live repository rule

The RPG_AI repository itself remains the source for its current code, `AGENTS.md`, `STATUS.json`, accepted evidence, decisions, and milestone files. Do **not** replace the live repository with a stale copied snapshot from this bundle. The alignment handoff tells the implementation agent exactly which live files must be reread and reconciled against RRG v0.2.1 before C6 moves forward.

Reviewed repository during preparation: `VasylHryha/RPG_AI`, `main`, commit `e2e7201eccf4f377cc4185b8370f392149bd662c`. If HEAD has advanced, use the newer actual checkout and reconcile rather than reset.

## History

`history/RRG_Documents_2026-10-02.zip` contains the delivered current package together with archived history. Historical documents are provenance, not current authority.

## Website

`website/UNITY_THEORY_WEBSITE_HANDOFF_R4.zip` is the latest website handoff available in this project. It is included for project continuity but does **not** govern RPG_AI implementation.

## Non-negotiable scientific alignment

Current RRG v0.2.1 keeps `R=(G,M)` and `G↔M`, and makes the source-direction loop central:

`B_n → R_n → B_{n+1}`.

Therefore staged recursive composition `R0 → R1 → R2` is useful but is not by itself the complete current RRG mechanism. RPG_AI must separately test whether formed organization changes the effective background/conditions and whether that change causally affects what can form next.
