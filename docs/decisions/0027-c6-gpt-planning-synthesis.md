# 0027 — GPT planning synthesis for C6 unblocking

**Date:** 2026-10-03  
**Owner instruction:** GPT should fix the review and check the current project.  
**Scope:** review/planning only. No C6 execution is authorized by this decision.

## Decision

The owner authorizes ChatGPT/GPT to reconcile the current C6 unblocking review with the pinned RRG v0.2.1 source, GeoMind R5, AGENTS lifecycle rules and the current repository state.

The resulting planning synthesis is:

`docs/reviews/c6_unblocking_synthesis_gpt.md`

This decision **supersedes only the extra role-specific planning prerequisite** introduced by the ChatGPT recheck / Codex-edited Revision 3 that required Claude to reread the full source before the owner could even consider an exploratory pilot.

That extra prerequisite is not a scientific requirement of RRG v0.2.1 or GeoMind R5, and AGENTS does not require a cross-family evidence review before an explicitly owner-requested development pilot. The owner may therefore consider the GPT synthesis directly.

This does **not** replace the repository's cross-family independent-review requirement for future qualified experimental evidence, implementation acceptance or milestone acceptance. A future qualifying revision/panel still requires the appropriate other-family review under AGENTS.

## Current fixed boundaries

- C6 remains `BLOCKED / R006 STOP`.
- R006 evidence and historical receipts remain unchanged.
- The post-stop repair remains bounded to static/stored-artifact review; repaired full-world behavior is NOT_VERIFIED.
- No hypothesis verdict is assigned.
- No final entropy, mutation probe or panel is authorized.
- No threshold, control, protocol, source, accepted/frozen code or status change is authorized.
- The proposed minimal Q-versus-H pilot remains **PROPOSED, NOT AUTHORIZED** until the owner explicitly approves it.

## Forward order

1. Use the GPT synthesis as the current planning record.
2. Owner either approves the single minimal Q-versus-H exploratory pilot, declines it, or chooses another route.
3. If approved, commit the pilot specification/harness before generating its fresh pilot inputs, validate only the harness scope explicitly authorized, then run the pilot once under its fixed caps.
4. Review the stored pilot result.
5. Owner chooses unchanged-R4 engineering/resource continuation, a separate prospective scientific redesign, a fresh registered C6 revision, or pause.
6. Any future registered development/final lifecycle follows AGENTS/R5 and still requires cross-family independent evidence review at the proper stage.

No execution follows automatically from this decision.
