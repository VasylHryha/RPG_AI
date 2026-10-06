# Scoped B3 plan and owner recheck disposition

Task: read-only v4 recheck from existing evidence; no combat, tuning or replay generation. Scope: `evidence/tactical_composition_demo/astelia_cpp/` only. Root `docs/PLAN_CURRENT.md` is intentionally not edited because the user's explicit path restriction supersedes the repository's root-plan-update rule.

| Step | Status | Evidence/disposition |
|---|---|---|
| Read required design/reports and local evidence | DONE | Main report names inputs and distinguishes B population from C historical diagnostics. |
| Extract exact stored B regular mechanics | DONE | `analyze_stored.py`, `STORED_TRACE_ANALYSIS.json`; original counts reconcile. |
| Draft evidence-backed report/v5 recommendation | DONE | `../S4_V4_RECHECK_REPORT.md`, first line CHANGES_REQUIRED. |
| Send owner request verbatim to independent reviewer | DONE | Separate collaboration reviewer `v4_reviewer`, Codex family. Claude is not exposed by this interface. |
| Resolve reviewer findings | DONE | Separate reviewer final pass: no unresolved evidence-interpretation or recommendation defect. |
| Verify scope, preservation and prepare scoped commit/delivery | DONE | `VERIFICATION.json`, `DELIVERY_NOTE.md`; normal hook-checked commit is the final delivery action. |

Exact request sent twice (evidence audit and draft report audit):

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Reviewer findings and disposition:

- Pair versus latent-unit counting can reverse the apparent resonator reversal conclusion. **Fixed:** report supplies both definitions, 391 versus 473 ticks, and unmatched B/C limitations.
- Expiry is not the dominant resonator release and disappeared includes own losses. **Fixed:** full release ledger, same-tick rearming, and own/enemy-death splits are explicit.
- Morale zero displacement and expiry are safe wall retreat in this export, not a general under-fire hold failure. **Fixed:** 13,218 walls/no focus/no gun reach, only 91 active holds, zero under-gun morale expiries.
- Push-pull focus changes its skeleton despite the design's unaffected wording. **Fixed:** named design conflict and no false negative-control claim.
- C stop is forecast-based; capture-count overestimate is small; C has 84 missing endpoints. **Fixed:** actual versus forecast timing and all missing C categories.
- Raw geometry uses native arena bounds rather than reduced-viewer metadata. **Fixed:** analyzer uses 1400×800; report discloses 1200×700 payload mismatch and snapshot gun-radius limits.
- A blanket unanswered-threat veto would prevent deliberate transit through gun arcs; emergency release could immediately reacquire the same failure. **Fixed:** proposed aggregate transit-loss budget, bounded acquisition, observable invalid-condition clearance plus a fresh crossing, and explicit target-versus-other-threat semantics. These are unvalidated future engineering choices, not a proven winning v5.
- Transit-loss cost would become zero upon arrival and miss lethal second-threat pressure. **Fixed:** a minimum 0.5 s risk horizon remains active after arrival, with an explicit constructed check.

Analysis execution accounting: first extraction aborted on duplicate `id` keyword while formatting an example; it produced no completed receipt. Corrected extraction completed in 46.79 s. Arena bounds were then corrected from replay metadata to native defaults; the final paced extraction completed in 47.39 s and supersedes that intermediate derived file. Both operate only on stored bytes; neither executes combat or alters original evidence. `nice` could not set process priority under the sandbox; explicit pacing remained active.

Paste-ready root-plan B3 update for the plan owner:

> B3: DONE — Codex stored-evidence recheck CHANGES_REQUIRED (`astelia_cpp/S4_V4_RECHECK_REPORT.md`): both unsafe focus and stale/incomplete holds implicated, no causal split; reversal definitions corrected; A/B complete, C missing; v5 must replace both unconditional rules with a coherent unit intent and observable risk/progress checks. Separate Codex adversarial recheck completed with findings resolved; Claude cross-family v4 development review remains a separate gate. No new combat, tuning or replay generation.

This disposition records the mandatory owner recheck without assigning a quality score or self-accepting v4/v5.

Final reviewer disposition: “No unresolved defect remains in the report’s evidence interpretation or concrete v5 recommendation.” It supports CHANGES_REQUIRED for the v4 candidate and closes this stored-evidence recheck; it does not approve the future v5 proposal or replace Claude's cross-family development review. Reviewer modified no files and executed no combat.
