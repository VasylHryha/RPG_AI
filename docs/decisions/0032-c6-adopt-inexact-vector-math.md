# 0032: C6 option B adopts the faster, inexact vector math

**Date:** 2026-10-07
**Owner's words:** "c6 yes use faster math then" (answering decision item C5 in `docs/PLAN_CURRENT.md`)

## 1. What is decided

- **C6 option B switches to the inexact kernel:**
  - Accelerate `vvexp`/`vvsincos`;
  - separable 5×5 site Gaussians.
- **Evidence:** `evidence/c6_option_b/inexact_study/INEXACT_IMPACT_REPORT_R3.md` (Codex owner recheck R3: APPROVE_WITH_NOTES).
  - In 10 stored worlds, no decision or outcome changed: 77,342 scalar decisions, 10,741 guards and composites, 1.14 M lock tests and 3.12 M link tests.
  - The maximum deviation was 3.3e-9.
  - CPU fell by about 25%.
- **This ends decision 0029 item 3's zero-tolerance (bit-exact) contract for option B.**

## 2. The new equivalence contract (from the round-2 memo §7, as corrected in R2/R3)

- **Discrete:** every Boolean, integer, label, membership, chain, invalid field and stop reason must be identical to the exact engine on the same inputs. Physical digests may change; candidate and member identities may not.
- **Numeric:** absolute difference ≤ 1e-8 on every comparable finite float, monitors included. Relative monitor changes are reported separately.
- **The registered diagnostics must still pass:** `b_reference_equivalence` (1e-10) and `b_transform_equivariance` (1e-9).
- **New references:** once adopted, the inexact engine is re-verified against the exact engine on the stored references, then new bit-exact references are generated **with the inexact kernel**. Later work is exact against those.
- **Platform:** the macOS build is pinned (26.6.2, build 25G83 at adoption) and recorded in every run receipt. An OS update requires regenerating and re-verifying the references before further recorded use.
- **Kept:**
  - the exact kernel remains selectable, for audits and for any dispute;
  - the R3 low notes (N3 two guard preconditions, N4 a nonfinite count) are fixed in the adoption analyzer;
  - future-panel risk is **not** quantified by the study. That is a disclosed limit, not a guarantee.

## 3. Not changed

- C6's science, registration, entropy and status: C6 stays BLOCKED / R006 STOP until its own owner-approved steps.
- Frozen C0–C5 files.
- Every run rule of decision 0031.
