# Response to the owner's external research recheck R2 (2026-10-06)

**Source:** `docs/reviews/external_web_ai_recheck_r2_2026-10-06.md`, copied unchanged from the owner's download. It inspected `main` at `fba4332`, the revision-6 **draft**. Since then, revision 6 was consolidated and went through six Codex review rounds, ending at revision 6.4, APPROVE_WITH_NOTES (`docs/reviews/tactical_0h_rev6_design_review_codex_r6.md`). Many of its issues were therefore already addressed when it arrived. The new valid points are adopted as revision 6.5, section 19 of `DESIGN_0H_REV6.md`.

**Status codes:**
- **ADDRESSED**: already fixed in 6.0–6.4.
- **ADOPTED**: new, added in 6.5 or in the 0g plan.
- **NOTED**: recorded as direction, with no change now.
- **N/A**: concerns the earlier handoffs, not the repository.

| ID | Status | Where |
|---|---|---|
| A01 memory clocks | NOTED and ADDRESSED | Memory has no-signal declared (12.10). The three-clock direction is recorded for the revision that adds a memory claim (19.4). |
| **A02 choose not injective** | **ADOPTED** | 19.1: choose is secondary and descriptive with a disclosed ceiling; no selection claim |
| A03 smoke omits choose | ADOPTED | 19.5: F5 is perceive-only by design; F9 adds move |
| A04 premature architecture | ADDRESSED | Revision 6 adds no registry or composer; library reuse is deferred (section 10) |
| A05 reuse the histories | ADDRESSED | The endpoint graph is recomputed from recorded positions (14.1) |
| A06 the native path | ADDRESSED | The integration task requires native and reference paths where 5.1 is native |
| A07 the global read-out is not the root failure | ADDRESSED | The measured failure (empty output, drift) is what 6.x fixes; a fixed designated output is kept |
| A08 locking is not causation | ADOPTED | 19.6 |
| A09 the bridge pseudocode | ADDRESSED | Replaced by the post-trial directed-progress rule (12.1, 14.2), reviewed through six rounds; still a hypothesis that F1 and F5 test |
| **A10 coherence is not task error** | **ADOPTED** | 19.2: move cannot stop with one output; F9 documents it |
| **A11 single-oscillator memory** | **ADOPTED** | 19.3: single-oscillator and sample-and-hold baselines |
| A12 M cost asymmetry | ADDRESSED | Control M uses the same cap and cost checks (section 6) |
| A13 matched intent vs realized | ADDRESSED | Exact matching is required; unmatched seeds are INCONCLUSIVE and never replaced (section 6, 14.9) |
| A14 M-all vs M-active | ADDRESSED | M mirrors B1 with a random site over all 8 sites; the estimand is named (section 6) |
| A15 same seed ≠ same exposure | ADDRESSED | G2 is evaluated on frozen copies with open-loop perceive; G0 is a package comparison, as stated |
| A16 orphan pruning ≠ confinement | ADDRESSED | D4 is liveness only, and the wall is separate (sections 3, 4, 12.10) |
| A17 the task-blind boundary | ADDRESSED | No score-based admission or reuse; the library is deferred |
| A18 lesion confounds | ADOPTED | 19.6: the channel lesion tests read-out dependence only; the receiver lesion is descriptive (12.6) |
| A19 identity too early | ADDRESSED | Exact content hashes are kept; no fuzzy deduplication |
| A20 snapshot overreading | ADOPTED | 19.6 |
| A21 6 of 8 is not significance | ADOPTED | 19.6 (it was already called a development rule in 12.5) |
| A22 shared environment schedule | ADDRESSED | Revision-6 training worlds are distinct per slot (14.6) |
| A23 0g hysteresis already exists | ADDRESSED | v4 adds a hold, not hysteresis (section 15 builds on section 14's hysteresis). The period figures are consistent: a 3.33 s full period, so threshold crossings about every 1.66 s. |
| **A24 the 0g dwell needs release rules** | **ADOPTED for 0g v5** | The v4 hold ends early on reaching the band and on death. It has **no** release for lack of progress, an infeasible retreat or an urgent threat. A bounded, progress-aware release is the planned v5, informed by v4's decision traces (velocity feasibility). v4's development run is already executing and keeps its design. |
| A25 research overreach | ADDRESSED | The related-work and claim ledger (section 10) makes no uniqueness claim |
| A26 operational debt | ADDRESSED | In the integration batch (12.10; the recheck's engineering section): a read-only report path, ledger chunking and deadline tests |

**Its recommended order:** interface witnesses, then causal capability, then growth and controls, then integration, then a fresh run.
- Revision 6.x follows that order: fixtures F1–F4 are the witnesses, F5 and F7 the growth and control feasibility, and the development run comes only after they pass and the owner approves.
- The difference is that revision 6 has already chosen one growth candidate, rather than comparing several first. The fixtures are the check: if F1–F5 fail, the stop rows send the design back.
