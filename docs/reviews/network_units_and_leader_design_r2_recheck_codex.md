PASS — prospective design recheck after corrections
Reviewer family: Codex
Reviewer: separate agent `/root/leader_design_r2_recheck`
Reviewed file: `evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/DESIGN_UNITS_AND_LEADER.md`, revision 2
Date: 2026-10-08
Scope: independent same-family owner design recheck, not milestone acceptance or execution approval. This report records the reviewer's returned findings and the drafter's dispositions.

Claude CLI was attempted with read-only tools but returned “Not logged in”. A separate Codex reviewer performed the recheck. Do not describe this as a completed cross-family recheck. The earlier Claude CHANGES_REQUIRED report remains unchanged.

Owner request delivered verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

The reviewer read the complete revised design, original Claude findings, decisions 0033–0036, engine `artillery.cpp`, the slice teacher/schema/contract and relevant evidence. No code edits, Python, tests, fights, fits or engine execution; no `_local/` access. The drafter changed documents only. `docs/PLAN_CURRENT.md` is unchanged under the owner's explicit delivery instruction; tracking is in this report and the design self-audit.

## Findings and drafter dispositions

| Finding | Reviewer's issue | Drafter's correction |
|---|---|---|
| R2-1 | S3 respective P/R priors/values can yield different search labels while the draft promises a common deterministic teacher. | One frozen S2 plain prior and zero terminal value for first cycle; canonical common slate/streams/ordering; shared labels for both. Later common prior/value frozen by rule; model-specific online search comparators explicitly separate. |
| R2-2 | Full-army work order required S3 first and offered no bypass when timing is parked, conflicting with 0036. | Full army follows working S2 independently of timing utility/claims; first fight may keep timing masked. S3 can follow or run within that slice. |
| R2-3 | Across-draw variation measures seed variability, not controllable contestedness. | Pilot requires within-pair command/physical impact response and policy-sensitive damage/kill/death differences alongside headroom. No repeat broad script-value gate. |
| R2-4 | Absolute cached aim had no explicit current unit input/support dependency; recomposing old offset with moving focus changes the requested point. | Encode cached point relative to current self plus focus/lock/pending/expiry masks and wait budget; candidate radius uses cached point minus current focus. |
| R2-5 | Full-army target head none+50 contradicted admitted 64-enemy token capacity. | None+64 masked pointers, 50 populated in standard roster. |
| R2-6 | Value continuation target lacked bounded horizon/controller/return, and engine branch commands could bypass unit deployment semantics. | Fixed 1 s common frozen-controller continuation, normalized additional HP balance, zero discount, unresolved/cutoff coverage and total-cost accounting; search commands pass through frozen U and native deployment gates. |
| R2-7 | Repeated hold_start commands could renew indefinitely despite a nominal 1 s start-delay horizon. | Cumulative wait origin/remaining budget; plan changes cannot renew origin/deadline; safety-gated autonomous fallback at cap and explicit stop row. |
| R2-8 | First reread found candidate-specific rollout ending at volley landing could score damage over unequal durations. | Common root t+3 s scoring horizon for all candidates, root t+4 s value-tail cutoff, same absorbing terminal treatment. |

The drafter made R2-1–R2-7 corrections in one batch and recorded each cause/fix in the design self-audit, then requested a reread. That reread confirmed the seven fixes but found R2-8 and requested a narrow clarification: only loss of autonomous public eligibility can clear the wait episode, never leader-induced focus/command changes. The drafter corrected both and requested the final reread from the same reviewer. These follow-ups addressed actual defects in one design recheck, not separate evidence reviews.

## Original Claude findings

The reviewer found H1–H3, M1–M5 and L1–L4 otherwise addressed prospectively: planner citations accurate; focus before target lock; Singles empty; timing masked in imitation and taught on starts in S3; unit distance-based lead scored on release opportunities; R replaces plain memory; existing script-level value/timing anchors used; small separate pilot and minimal arms; full-army caps explicit; simplified ties/decidability; K initialization-gradient check; source-reading/self-audit present. This is design closure, not a statement that new labels, competence, coordination or RRG benefit have been measured.

## Final reread

The separate reviewer returned **PASS — prospective design recheck** after rereading the corrected contracts. Its final finding summary:

> All original Claude H1–H3, M1–M5 and L1–L4 findings are addressed. R2-1–R2-8 corrections are internally consistent: shared bounded search labels, deployment-equivalent command execution, encoded cached aims, cumulative timing limits, matched scoring horizons, and full-army progression independent of S3 claims.

No remaining blocking design findings. This is the working-tree revision-2 document recheck, not owner execution approval or evidence of useful training/RRG coordination. No numeric scores assigned. `git diff --check` passed; no project code or tests were run for this document-only delivery.
