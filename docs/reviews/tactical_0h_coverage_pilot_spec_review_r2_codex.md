APPROVE_WITH_NOTES

Reviewer family: Codex
Reviewed commit: `0bf4210eca8f5615adf08567cef20d43595c64ea`
Spec SHA256: `ca0def0dff6c352f1cb53d3f2aad6f7e9cc0be9556d7a30ae6d7bc74e4494cc5`

Round-2 static review of Amendment 1, the round-1 review, coverage diagnostic,
service telemetry report/recheck, kernel builder, service graph/observer, worker,
scheduler and report writer. The fd21826 admission code was read directly from
Git. No pilot, medium, assay or process-list command ran during this review.

Amendment 1 resolves both arm-definition blockers and the impossible churn
measure. No remaining finding requires a drafter change to an arm's meaning;
step 2 is unblocked within the owner's explicit build-only scope.

| Round-1 finding | Amendment / disposition |
|---|---|
| Undefined waiting clock and pre-root priority | Eight zero-initialized, kernel-owned clocks accumulate active-unserved time at 0.1-second boundaries; physical-site service resets even during inactivity. Inactivity and root loss do not reset an unserved clock. Finite/infinite classes and pointer ties are explicit. |
| Recycle can remove birth anchors / stale geometry | Exclude a/b; remove one eligible non-service donor using measured lock/id; revalidate the same fixed point on the new graph. Failed retry keeps the deletion and ends recycle_failed. No new search. |
| Impossible donor churn | Donor class/lock/age, retry result and requesting-site service within 60 seconds replace it. An observation horizon ending early must be censored when service has not occurred. |
| Age threshold and quotas | Explicit >=200, one recycle shared across B-path/B1, one terminal, successful retry counts as one birth. Propagated resource-stop requests have no candidate to retry. |
| B-label boundary | Retain pre-transition outage objects and post-birth samples; exclude restoring terminals and restoring gap samples from B while retaining zero-duration restoration evidence. New outages inherit no preceding birth. |
| Historical control and reading rules | Reuse coverage/assay unchanged; corrected RD3 labels require retained boundary evidence in new outputs, otherwise legacy_B. Pool steps over sites 3–6 and all ten runs. Incomplete arms cannot receive positive or regression readings. A7 remains prospective. |
| Scheduler scope | Explicit 3600-second cap, <=10 workers, both off controls included, identity-verified reuse, no incomplete reruns, and repo-qualified anchored process alternatives. |

Implementation notes, not new arm rules:

1. Preserve RD3's dispatcher condition `outcome in ('cap','cost')`. The new
   explicit `recycle_failed` result therefore does not propagate a resource
   stop. Later sites can try against the changed graph. No eligible donor
   remains `cost` and does propagate. Requiring propagation after every failed
   recycle would add an unstated rule. Test both paths, including quota and
   output-first behavior.
2. B1 has no B-path geometric progress trial. Its complete admission is its
   existing clearance/count/cost check on the retained candidate. Adding a
   B-path strong-progress test to B1 would change the arm.
3. Use RD3's physical-site service snapshot for clock resets and donor classes,
   including idle routes. The active-only root graph is insufficient. Clocks
   must remain independent of the optional observer and clone-copied.
4. Log the initial cost refusal separately from the final retry outcome.
   A failed geometric retry is not itself a terminal cost refusal. Preserve
   the declared global C/B and site-named N scopes; none establishes causality.
5. Synthetic validation and build identity do not establish observer on/off
   trajectory identity. Both complete pairs belong inside Claude's main phase.
   The scheduler must stop on process-access errors without launching jobs.

Owner recheck request sent verbatim to separate reviewer
`/root/coverage_r2_recheck`:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Disposition: the independent static Codex pass returned APPROVE_WITH_NOTES,
confirmed all Amendment 1 resolutions and adversarially withdrew a proposed
resource-stop blocker after checking literal dispatcher inheritance. Its B1,
physical-service, censoring and refusal-recording notes are incorporated above.
Only Codex-family reviewers are available; this is not other-family acceptance.
Tracking stays here because the owner prohibits edits to docs/PLAN_CURRENT.md.

Stop condition: if an implementation finding requires changing either arm's
meaning, the implementer stops and returns it to the drafter. No pilot execution
is authorized for Codex in this session.
