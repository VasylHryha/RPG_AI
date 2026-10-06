APPROVE_WITH_NOTES

Reviewer family: Codex
Reviewer model: GPT-6
Design SHA256: 3b2599222e3d8bad58d3495252e0249925e20de778f0db722b8ed4bf16f1e592

| Round-1 item | Round-2 disposition | Binding interpretation / remaining limit |
|---|---|---|
| R711-1 | Resolved by 18.3 | B1 can bootstrap when CURRENT effective-root union is empty; resume after death, silence, zero gain or loss of active drive leaves no root. O never qualifies. Apply the predicate live before each B1 request. |
| R711-2 | Resolved with correction retained | 18.3 supersedes 18.1's erroneous chronology. Allocation pressure is supported; an isolated cause or guaranteed cure is not established. |
| R711-3 | Approved with notes | Finite post-insertion retrial at the same site; total quota two. Candidate exhaustion or actual connection permits next-site service. Resource refusal ends service in that check, with visible refusal accounting. Indefinite starvation remains possible. |
| R711-4 | Approved with notes | Instantaneous connection does NOT meet time-averaged E >= 0.5. A/B, both starts, coverage, positive-task gates and exact control-M B1 count/timing matching all remain unchanged. |
| R711-5 | Resolved; failure unrepaired | F5(ii) remains FAIL with max E = 0.454375. No claim of recovery without separately authorized measurement. |

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Scope: AGENTS.md, section 18 including drafter amendment 18.3, inherited timer/root/strong-graph/control/gate definitions, round-1 review, REV710_FIXTURE_REPORT.md and saved rev710_fixture_run_20261006/F5.json.gz and F5i_BIRTH_EVENTS.json. The request's section 12 is the historical N1d amendment; it was read but the F5 diagnosis is section 18. Only standalone standard-library inspection/arithmetic on stored records ran during design review; no project code ran before this verdict. DESIGN_0H_REV7.md is unchanged. These review notes supply the bounded implementation interpretation requested by the owner.

**Diagnosis verified.** Saved F5(i) has 32 accepted B-path births by sites 0–7 [2,8,7,7,5,0,1,2], with terminal counts accepted=32, cost=102, quota=48, no_root=16. At t=300 the growth record is N=42, cost=59.3; t=320 is N=45, cost=63.4; t=800 is N=45, cost=63.3. The first cost refusal is t=340. The 1.327139 m.u. accepted insertion at t=300 is placement geometry, not a final persistent bridge. At lambda=32, K=1 and receiver degree six the single-edge radius cutoff is sqrt(log(32/(0.5*6)))=1.538546. Actual directed neighbor selection, complete path, changing degree and motion still matter. Concentrating insertion quota and delaying sensor expenditure targets observed allocation pressure, without identifying the exclusive cause or promising a cure.

**Bootstrap and bounded scheduling.** Use current ordinary unsilenced gain-positive members in strict reach of positive-strength drives as effective roots. At each B1 site request evaluate whether a root exists and no active site has a strong output path. The first accepted bootstrap birth can therefore defer subsequent ready sites in that same B1 call. This is the literal live reading of “once any effective root exists”; it keeps the inherited two-birth cap as a maximum, not an entitlement. On each frame, freeze all B1 novelty timers under this predicate, including a covered site's stored demand; outside it use 8.9 unchanged. Log ready active deferred requests with a zero-attempt `deferred_output_first` terminal and retained timer. Inactive demand retains its separate queued log. No historical connection/root latch.

B-path snapshots deficit order and output-first mode at check entry. While no active path exists, retry the selected site after acceptance against current geometry, full held receiver degrees, strong graph, clearance and budget. Each request has at most eight frontier pairs times thirteen rotations. With two accepted births maximum, the within-check work is finite. Advance to another site only on actual connection or exhaustion of that site's finite candidates (including an empty frontier/output set with its existing no_root/no_output reason). A cap/cost refusal stops service for the check; later requests may log that resource refusal with zero trial attempts. Once a check begins with an active path, use 17.2's one request per site unchanged. Connection/exhaustion of the selected site permits next-site service within the original quota. Record per-site accepted-birth COUNTS, not a boolean; a second exhausted request must not erase an earlier accepted birth from waiting accounting.

**Unresolved cases and claims.** 18.3 fixes the circular empty-start deadlock, but its broad “No deadlock” sentence means only that prerequisite cycle. A root gives a frontier; it does not guarantee an admissible edge, output placement or resources. If no site can connect and a root persists, B1 remains deferred indefinitely with frozen timers, finite logged B-path refusals and no timeout release. The finite experiment horizon still terminates and unchanged gates fail/block development. Loss of all roots resumes B1; loss of a previously connected path re-enters output-first. No starvation bound or all-site coverage guarantee is introduced.

The sentence “one connected site meets max(E) >= 0.5 structurally” is superseded here: connection at one instant is merely an opportunity for exposure. E is measured over the specified windows and still must reach 0.5. Coverage can regress while B1 is deferred. Keep G0/G0-prime and positive-task requirements unchanged. Control M mirrors the intact arm's accepted B1 births at the exact checks, bypassing M's own output-first predicate; U retains its inherited queue. Any unmatched M slot remains a failure/inconclusive condition under existing rules. A successful static synthetic bridge establishes scheduling feasibility only, not F5 or scientific qualification.

**F5(ii) disclosure.** Stored A=1.1382729819631165, B=0.9752452351518366 and E=[0,0,0,0,0.454375,0.32104166666666667,0.3877083333333333,0] give FAIL and a 0.045625 exposure shortfall. “Narrowly” describes only distance to the fixed threshold; no uncertainty or negligible-regression inference is licensed. 18.3 explicitly preserves that FAIL and requires measurement rather than inference. Output-first can change subsequent geometry even for the hand-built start. Keep outcome-informed fixture reuse disclosure and all earlier evidence unchanged.

Independent owner recheck: request above sent verbatim to read-only reviewer /root/rev711_r2_recheck (Codex; cross-family availability checked separately for implementation). It confirms bootstrap closure and these starvation, exposure, finite-retry and control-matching notes. Recheck and disposition are tracked here and in the scoped delivery under the owner's explicit prohibition on editing docs/PLAN_CURRENT.md. This Codex review of the Claude-authored design is distinct from later implementation review/acceptance.

Verdict authorizes only the owner's conditional 7.11 implementation and affected synthetic validation. It does not authorize N1/F1–F9, training, development, panels or acceptance.

Assisted-by: Codex:GPT-6
