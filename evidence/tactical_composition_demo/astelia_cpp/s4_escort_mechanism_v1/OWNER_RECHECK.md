APPROVE_WITH_NOTES
Reviewer family: Codex
Review mode: Separate Part 2 reviewer pass; explicit same-family fallback. The requested Claude reviewer was unavailable because Claude CLI returned “Not logged in”. This is an independent-agent owner recheck, not cross-family scientific acceptance.
Reviewed run commit: `0f8e823077d83bca76a66532a1988d2ec7c9052a`.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Verification and coverage

Read AGENTS.md, DESIGN_0G.md §19.8.1, the analysis/render/attribution scripts, all new compact/per-fight outputs, and native v6 targeting, bridge, observer, combat, preparation/release and probe movement sources. Before any raw parse, independently checked all 620 inventory entries for exact bytes and SHA256: PASS, 866,788,710 bytes; inventory SHA256 `4c76805ea88d3bb7b59d3c7b57a76a53fc4581158806416ba92ef6047cc63ef1`.

Independently parsed all 120 raw traces with a separate inline recount, without importing the analysis functions: every capped HP event grouped by victim/source cohort, all own-ranged last-hit killers, own/enemy artillery launch counts, 100 initial units per fight and terminal own counts matched PER_FIGHT.json exactly. Independently reconciled SHELL_ATTRIBUTION.json against COMPACT.json for artillery HP to every cohort on both sides. No fights, engine execution or simulations occurred.

All rendered table cells trace to the stated JSON loops; audited narrative arithmetic, percentages, source dimensions and counts against those tables/JSON. COMPACT.json and SHELL_ATTRIBUTION.json bind unchanged analysis script hashes. Observer launch, combat, observer combat-rules and v6 controller source hashes match the stored COMPLETE binary source identity; inspected code explains why artillery attribution by unique source/scheduled impact is valid, why direct release inference remains a lower bound, and why direct interception remains unidentified. The request disables abilities, so prep resets do not include disengage cancellations here.

## Findings and dispositions

| Finding | Disposition in final report and render.py |
|---|---|
| P13 regular gun HP from enemy ranged was misstated in prose as 2,442/11,175 for the two common windows. | Fixed to 3,311/10,202, matching JSON and table. |
| P12 early opportunity share was rounded to 85.26%. | Fixed to 85.25% from 69,937/82,034. |
| Novice loss explanation omitted the P13 melee saving. | Explicitly accounts for 0.15 fewer melee deaths per fight, in addition to gun savings. |
| Proposed gun-post retreat inherited the wrong margin. | Root source check corrected it to the native 12 px margin; 320 px remains a prospective boundary radius subject to repulsion/range loss. |
| Proposed ranged spread changed the goal while potentially retaining multiplier zero from the original escort goal. | The single movement rule now clips its final goal and recomputes the multiplier from final goal error, with the existing 2 px criterion and zero stop distance; coincidence and ordering are explicit. |
| Novice post-gun-death wording implied in-flight artillery caused all residual added deaths. | Replaced with exact gun-phase counts: 334/418 P12 and 554/575 P13 ranged deaths while both sides still have guns at prepare. |

Every finding was corrected by the analyst; the final reviewed hashes below bind the corrected artifacts. No reviewer edits to the report, scripts, PLAN_CURRENT.md, DESIGN_0G.md or committed receipts were made. This review records the owner-requested plan exclusion rather than modifying PLAN_CURRENT.md.

## Remaining notes

The supported account is temporary early protection coupled to severe ranged exposure and incidental counter-battery splash. It does not establish exact prevented gun shots or disentangle diversion, movement/collision and enemy-screen geometry into independent causal effects. Direct-shot receipts, source positions at release and hit-to-shot identity are absent; impact-time targeting proxies are labelled accordingly. PARTIAL is the correct diagnostic scope.

Enemy gun-targeted launches and ranged gun damage rise again after the short protection window; full-fight P12 artillery damage to guns barely changes, and P13 ranged damage to guns increases. The report preserves these adverse cases, all-ranged deaths in the regular intervention arms, novice costs, and outcome-conditioning limits. The eleven wins have exact opposing elimination and surviving own guns; this is development evidence rather than a population win-rate claim. Ten paired clusters are the sampling units, not independent orientations or pooled outcome-conditioned fights.

The three proposed modifications are distinct unrun single-rule hypotheses, with trade-offs and prospective constants. Withdrawal after enemy guns die is correctly excluded as an existing P12 fallthrough. None is tuning, registration, permission for v7 or scientific acceptance.

validate.py and deliver.py were inspected for scoped stored-data validation and normal-hook/explicit-path delivery; this pass did not execute either. Their execution and transport receipt remain the root analyst’s final delivery check.

## Mechanical delivery follow-up

The initial delivery stopped at `git diff --check` because the rendered report had an extra blank line at EOF; it did not reach a commit attempt or hooks. Reviewed the exact subsequent changes: render.py strips trailing whitespace before emitting one final newline, and deliver.py uses `delivery/attempt2.git` to preserve the earlier staging attempt. Reconstructing the prior report/render/delivery files by undoing only those two changes reproduced their previously reviewed SHA256 hashes exactly. There are no report content, numeric, analysis or simulation changes. The verdict remains APPROVE_WITH_NOTES; the final hashes below are refreshed. Main HEAD was verified as `0bf4210eca8f5615adf08567cef20d43595c64ea`, and current worktree `git diff --check` passed. No analysis rerun occurred.

## Reviewed SHA256

- `../S4_ESCORT_MECHANISM_DIAGNOSTIC.md`: `c78131fd74333ca045f7a0b892e3e98461e8ae6ba4947ea94b9b586b26fff8e7`
- `analyze.py`: `d249366989b108d920a97b85190a5dbe78c1642fd1ce7dc574325a0d0d95ae6f`
- `COMPACT.json`: `580f7a1f7ad9b2fbed729336d5d14f99968d3c8056ecd121be27bbe542050fac`
- `PER_FIGHT.json`: `3c028b0241a36cebf39c75bcd0a4e686c491e37bbad3af5baa7cd2faaf08ede7`
- `shell_attribution.py`: `651e15deb1cb1bf16b18955baa5e3c1d063dd597679cd8c607b9847222541b68`
- `SHELL_ATTRIBUTION.json`: `1136c38ab8bfe65980c350b73c41843f42698ee3b214f547839a67c48b1fd1bc`
- `render.py`: `1dcd32a4fa132dd789b1a9275061d14d09d89f59747a2585287dd6a6344f9229`
- `validate.py`: `1413d838448da965cf4685f6d38cf0a0f9ee66b1656a167c510d5fcfd1454484`
- `deliver.py`: `66c8e7d3d40e799d5fc1831cbf982f9a3900de6ae9567cd63b10f87df21f6a0d`
