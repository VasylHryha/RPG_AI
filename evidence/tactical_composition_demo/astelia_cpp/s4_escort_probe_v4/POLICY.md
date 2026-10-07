DECLARED_BEFORE_FIGHTS

Owner-authorized scripted descriptive replication of DESIGN_0G §19.12 at 69e13a2, conditional on the stored v3 owner recheck finding no invalidating P16 defect. That recheck is APPROVE_WITH_NOTES in docs/reviews/tactical_0g_escort_probe_v3_recheck_codex.md. No tuning, judging, registration, status, scientific acceptance or resonator/source claim. Plan/design files are excluded from edits and seal by explicit owner instruction; rechecks and dispositions live in OWNER_RECHECK.md.

P12 and P16 are EXACTLY v3: unchanged ../build/astelia_native_escort_probe_v3 and .build.json, exact source hashes and original native v3 controller dispatch/skeleton. No new controller binary is compiled. P12 instantiates original EscortProbeV1 arm12; P16 wraps it without mutating its state/RNG. P16 changes only descending inclusive prepare-snapshot all-role splash V, then HP/id, for individual reachable gun choice and shared anchor; focus movement follows that choice. Reach, retained unreachable v6 target, radial focus geometry, ascending-id P11 repulsion, pre-spacing multiplier, phase/failure fallthrough and every non-gun action are unchanged. The exact v3 POLICY.md and controller/host/build/measurement sources are pinned. Static V is not future impact victims or a hidden engine prediction.

20 fresh unused development clusters × 2 paired orientations × {P12,P16} × {regular,novice}=160 panel fights. Separate fresh engineering seed; all 21 unique high-partition OS development integers are collision-checked against all prior declared development ledgers and engineering declarations. Judging ledger is never opened. Templates and historical v6 knobs are unchanged except entropy. All 80 fresh P12 controls complete and their sanity table is reported first, then all 80 P16 fights. Broad regular bounds (mean enemy guns destroyed<4 or own guns lost<7) flag only; novice<40 wins flags only. No sanity flag permits retuning, abort/replay or seed replacement.

Mandatory pgrep before every missing combat block/resume, including engineering: separate timestamped receipt per attempt with declaration and native identity. Active rev711_diag pilots / medium_variants telemetry wait 30 s; unavailable/error process list stops before request/claim. All planned engineering and panel tags scanned for ambiguity before new combat. Requests and claims are exclusive/durable before spawn. Verified completion requires admitted exact binary, request/claim/gate/raw/stderr hashes, successful native exit, zero controller/numerical failures and zero hidden fork/search/rollout counters. Ambiguous possibly executed fights stop, are preserved, never replayed or deleted. Verify all raw inventory hashes before analysis. Analysis completion pins outputs for fail-closed resume; render verifies them. Up to two workers, bounded queue and owned process-group deadlines. No code changes during runs.

Total cumulative compute<=3600s; engineering<=1200s; panel blocks COMBINED<=1200s; analysis<=1200s; checks<=600s. Projection reserves900s for analysis (v3 measured ~460s for120 fights). Gate waiting excluded. UTC start/end and identities in stage/claim receipts. Exact binary/manifest and source hashes are protected; PLAN_CURRENT and DESIGN_0G are not. They do not need restoration for Claude execution.

Normalization ledger (sealed measurement definitions):

| Quantity | Level / units | Clock, cohort and normalization |
|---|---|---|
| Elimination / timeout / S | fight, units/seconds | enemy0,own>=1,t<150 wins; t>=150 timeout, never win; S=own-enemy survivors. Counts/40 and means/40 per arm/head; 20 paired clusters |
| Gun kills/losses / own losses | fight, units |10-final enemy/own guns;50-final own survivors; cohort deaths/killers identified with team/role; means/40 |
| Chosen-target V | gun prepare unit-tick, count | Mean=sum V/count of prepare-living own guns selecting living enemy gun; explicit numerator/denominator, null0; whole fight. Focus and shared-anchor V separate over both-battery own-gun ticks, no-reachable ticks counted. Includes ticks without ready shot |
| Actual all-role splash multiplicity | shell, distinct units | Own shell aimed at opposing gun at launch, success iff positive capped HP to>=1 opposing unit ANY role; sum distinct opposing victims/successful shells; null0. Role breakdown same denominator. Unique source/scheduled-impact match within one tick or STOP; friendly HP and other-aim victims separate |
| Inherited gun-only shell multiplicity / HP ratio | shell/gun, units/HP | Both teams: distinct opposing gun victims per gun-targeted shell successful on>=1 opposing gun, separate from all-role denominator. Incidental gun HP separately; enemy->own gun HP/own->enemy gun HP, null0 |
| Ranged and melee arrival | separate role unit-ticks, fraction/px | ALL prepare-living own role ticks while both batteries living, even unavailable direction/post death. Post centre<=20px from SAME tick prepare raw/clipped point; separate raw/clipped fractions and unavailable counts. P12/P16 melee goals are hypothetical diagnostic points, no assertion they were commanded |
| First arrival / holding / displacement | role unit/time/ticks/px | First clipped arrival per eligible unit, never-arriving censored; holding counts arrived ticks continuing same-gun previous arrived tick, gaps/death/phase exit clear; reassignments separate. Post-minus-prepare displacement, post-dead unavailable. Whole phase and post-time[10,20),[20,30) geometry; pooled median/p10 linear interpolation at p*(n-1), not means of fight quantiles |
| Threat selection | ranged prepare unit-tick, fraction | Opportunity>=1 reachable enemy ranged threatening ANY living own gun; each inclusive native source range+both radii. Numerator any such threat selected. Whole phase and common windows explicit counts/null; geometry not legal/ready shot |
| Early screen last hits | event, units | Own ranged and own artillery opposing-ranged last hits separately strict event t<20,<30, full fight. Friendly damage separately, actual capped HP; no exclusive-contribution inference |
| Gun HP / cohort killers | event, HP/units | Actual capped gun HP loss by enemy source role or friendly source, bins[0,10),[10,20),[20,30),[30,60),[60,150.1); reconcile initial-final gun HP. Own ranged/melee losses and killer team/role separately |
| Gun survival | event/fight, units |10,20,30,45,60s; death<=sample removed, terminal survivors held after early ending; mean/40, no claim of continued simulation |
| Realization | prepare/post, px/counts | Raw/clipped points, direction/assignment, clearance to other gun bodies, shared points, shifted gun-goal coincidence, own-radius splash clearance, native-guard holds, degenerate/clipped/post-dead/singleton/unavailable ticks, post nearest gun/cohort/enemy-ranged distances and errors, P11 spacing audit |
| Paired cluster table | cluster, units/mean S | For both heads, 20 rows with each arm's two orientation outcomes, wins/2, mean S, and P16-minus-P12 differences; orientations paired on same entropy, no independent-trial claim |

Replication reading supersedes v3 categorical rules: Replicated iff P16 regular>=26/40 AND regular mean S>0 AND novice mean S>0 AND novice>=21/40 AND zero failures across the complete panel AND P16 wins>P12 wins in>=12/20 regular paired clusters. Not replicated iff P16 regular<=20/40. Otherwise descriptive when any replication conjunct fails (including >=26 regular with failed novice/S/paired requirement). Only a complete verified failure-free panel receives an outcome reading; execution failures stop as PARTIAL, never manufactured nonwins.

Cluster uncertainty: for each head, compute P12/P16 win proportions per cluster (wins/2) and paired difference ((P16 wins-P12 wins)/2). Across20 clusters report mean, sample SD/sqrt20 and an approximate unbounded t95 interval with19df (factor2.093024054). This descriptive estimator assumes independent development clusters, treats two orientations as paired, has no population guarantee and zero observed variance does not establish certainty. No uncertainty threshold changes the declared reading.

If replicated, P16 supplies the scripted feasibility witness required for the owner-directed v7 revision; draft §20 still needs revision against P16 and resolution of R2–R9. No registered/resonator/scientific conclusion follows automatically.

| Yes/no stop condition | One action | Responsible role |
|---|---|---|
| pgrep unavailable/error? | STOP before combat, preserve NOT_RUN/PARTIAL | implementer |
| 0h pilot batch active? | Wait and recheck | implementer |
| Code/binary/policy/constant/ledger/template drift? | STOP and preserve evidence | implementer |
| Rule changed after any fight? | Mark INVALID for a new declaration and fresh entropy | implementer |
| Ambiguous request/claim/raw without verified completion? | STOP, never replay | implementer |
| Controller/integration/action/HP/shell-attribution failure? | STOP and preserve evidence | implementer |
| Projected/measured total>3600s or stage cap exhausted? | STOP owned children and preserve PARTIAL | implementer |
| P12/novice sanity flagged? | Report flag before intervention interpretation | implementer |
| Reviewer finds precombat implementation defect? | Fix before seal/final checks | implementer |

Normal-hook scoped commit with Assisted-by: Codex:GPT-6, or verified current-HEAD bundle if main .git unwritable. Never stage PLAN_CURRENT. Claude executes engineering.py, run.py, analyze.py, render.py without edits. Codex runs no combat or process listing.
