DONE

160/160 fights: 10 fresh development clusters ×2 orientations ×P5/P7/P8/P9 ×regular/novice. Controlled team0, unchanged S4 world and v6 attempt-2 knobs; descriptive scripted probe of DESIGN_0G §19.4. No RRG-controller, tuning, registration, judging or status change. [Design review](../../../docs/reviews/tactical_0g_s194_probe_review_codex.md): APPROVE_WITH_NOTES.

Before fights, [POLICY.md](s4_collective_probe_v1/POLICY.md) and [DECLARATION.json](s4_collective_probe_v1/DECLARATION.json) pin all conventions: unique outer staging-ray solve; full-sight timer from first prepare; target retained until death; P9 outward axis acquired per target, live target position and per-tick angular assignment; mathematical post arrival; native inclusive artillery bands/direct surface gap; pooled exposure; censored simultaneity and PCA modulo pi. The original P5 controller is reused unchanged. P7 bundles target sharing, staging, early gun-target suppression and a wave; P8 adds both direct movement and targeting; P9 adds target selection and end-on arc geometry. They do not isolate those mechanisms causally.

P5 sanity was reported before other-arm outcomes: **WITHIN_DECLARED_BOUNDS**, regular mean guns destroyed 3.15/10 and own guns lost 10.00/10. Declared bounds are [1,6] and [7,10], respectively.

|Arm|Head|Eliminations|Timeouts|Mean S|Enemy guns killed|Own guns lost|Own losses|Exposure/gun-tick|First gun kill s|Shell hits/launches at guns|
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|P5|regular|0/20|18/20|-16.05|3.15|10.00|39.40|1.35|14.31 (20/20)|953/1120|
|P5|novice|20/20|0/20|+38.55|10.00|1.25|11.45|1.26|11.54 (20/20)|794/1039|
|P7|regular|0/20|18/20|-22.15|2.45|10.00|41.00|3.69|14.24 (20/20)|683/818|
|P7|novice|20/20|0/20|+38.70|10.00|1.25|11.30|3.11|11.76 (20/20)|732/967|
|P8|regular|0/20|0/20|-37.75|1.85|10.00|50.00|4.00|14.16 (20/20)|553/658|
|P8|novice|20/20|0/20|+27.85|10.00|0.20|22.15|3.58|11.64 (20/20)|751/1047|
|P9|regular|0/20|0/20|-24.90|2.75|10.00|50.00|1.62|23.02 (20/20)|708/837|
|P9|novice|15/20|0/20|+3.35|8.65|6.05|41.65|2.45|22.07 (20/20)|701/768|

|Arm|Head|Waves/reasons|Engagement latency s (observed)|Line-angle change deg (observed)|Fights reaching posts|Fights escort arrival|Escort focus unit-ticks|
|---|---|---|---|---|---:|---:|---:|
|P5|regular|0/20 {}|n/a (0/20)|n/a (0/20)|0/20|0/20|0|
|P5|novice|0/20 {}|n/a (0/20)|n/a (0/20)|0/20|0/20|0|
|P7|regular|20/20 {'ready': 20}|2.46 (20/20)|10.93 (20/20)|20/20|0/20|0|
|P7|novice|20/20 {'ready': 20}|1.92 (20/20)|1.58 (20/20)|20/20|0/20|0|
|P8|regular|20/20 {'ready': 20}|2.17 (20/20)|10.85 (20/20)|20/20|20/20|60613|
|P8|novice|20/20 {'ready': 20}|1.62 (20/20)|1.50 (20/20)|20/20|20/20|114452|
|P9|regular|20/20 {'fallback20s': 20}|0.52 (20/20)|19.69 (20/20)|20/20|10/20|60746|
|P9|novice|20/20 {'fallback20s': 20}|0.77 (20/20)|1.77 (19/20)|20/20|5/20|41503|

Elimination timing audit (before-wave / after-wave): P7 regular 0/0, P7 novice 0/20, P8 regular 0/0, P8 novice 0/20, P9 regular 0/0, P9 novice 0/15.

Own gun killers, totals across 20 fights per cell:

|Arm|Head|Team/role/deaths|
|---|---|---|
|P5|regular|team 0 ranged 2, team 1 artillery 142, team 1 melee 1, team 1 ranged 55|
|P5|novice|team 1 artillery 12, team 1 melee 1, team 1 ranged 12|
|P7|regular|team 0 ranged 2, team 1 artillery 136, team 1 melee 6, team 1 ranged 56|
|P7|novice|team 1 artillery 4, team 1 melee 3, team 1 ranged 18|
|P8|regular|team 1 artillery 171, team 1 melee 2, team 1 ranged 27|
|P8|novice|team 1 ranged 4|
|P9|regular|team 1 artillery 132, team 1 melee 1, team 1 ranged 67|
|P9|novice|team 0 artillery 2, team 1 artillery 96, team 1 ranged 23|

**§19.4 outcome reading:** No arm improves P5 gun exchange at this setting; return to telemetry, without general rejection. This is a descriptive pattern at one declared setting, not causal proof or a resonator result. Novice is a sanity check only; an observed elimination does not establish the above 50% plus positiveS development criterion.

P9 regular realization: all 20/20 waves used the 20s fallback; no readiness trigger. Mathematical staging was outside the arena for 97872 pre-wave gun-ticks; committed posts were outside for 12460 command gun-ticks. Some gun reached a post in 20/20 fights, which does not establish simultaneous whole-battery arrival. Some escort reached its point in 10/20 fights. Mean living guns at wave=6.65/10, at 80% engagement endpoint=6.60/10; mean guns ever reaching a post=5.40/10. The short latency therefore describes an already depleted battery.

P9 novice realization: all 20/20 waves used the 20s fallback; no readiness trigger. Mathematical staging was outside the arena for 46860 pre-wave gun-ticks; committed posts were outside for 757 command gun-ticks. Some gun reached a post in 20/20 fights, which does not establish simultaneous whole-battery arrival. Some escort reached its point in 5/20 fights. Mean living guns at wave=5.50/10, at 80% engagement endpoint=5.40/10; mean guns ever reaching a post=4.90/10. The short latency therefore describes an already depleted battery.

Exposure averages use different policy-defined commitment intervals: P5 includes its full approach from the first tick, while P7–P9 exclude staging. Zero-exposure approach ticks can lower the P5 average; these pooled values are not exposure at a common distance/time. The static 1-versus3–4 geometry estimate was not assumed as a realized measurement.

Elimination requires enemy0, own>=1 and t<150; timeout is never a win. S is survivor difference. Casualties are means per fight; shell counts are summed. Shell-hit numerator counts distinct damaging targeted launches, once across splash victims; incidental gun splash from nongun targets is excluded. Launch denominator includes misses and shells airborne at termination. First kill is conditional; no-kill cases stay censored. Exposure pools committed gun-ticks, excludes staging, uses actual post-step living positions and each enemy's native band. P5 has no wave, so simultaneity and line response are not applicable. Other censored cases are null, never assigned zero/150. The JSON retains denominators, killer unit IDs, per-fight timing, initial-wave cohort and attrition, target changes, post/escort arrival counts, and out-of-arena theoretical goals.

Realization/confounds: native collisions, clipping, reflexes and blockers can prevent theoretical arrivals or shots. The P9 acquired axis is fixed per target; line rotation can defeat it. Dynamic angular reassignment can change approach goals. Wave readiness and engagement use surviving-gun denominators, so attrition can manufacture 80% arrival; cohort audits disclose that. The screen is a movement/targeting bundle and can obstruct own fire; escort arrival alone does not establish protection. PCA angle changes can reflect deformation or casualty/cohort changes, rather than line turning. First gun kills before wave, insufficient geometry and nonidentifiable PCA are unavailable. A named favorable pattern with missing waves/posts/escorts is inconclusive for that intervention; an elimination during staging cannot demonstrate collective commitment. Partial realization limits interpretation even when aggregate outcome thresholds match. No failed intervention is interpreted as rejection of all collective commitment. Auto barrage/slow stay off with sandboxAbilities=false.

Measured completed probe stages before this render: awake time 641.288s. All compute uses caffeinate; two combat workers,1200s stage caps and a total3600s measured/projection guard with 900s analysis/recheck reserve during combat. Build/check/analysis logs retain elapsed/awake times. No code edits during fights or recount. Bootstrap/hash work and review bookkeeping receive a conservative additional 60s reserve; final review timings are adjacent.

Independent stored-data review compute (including failed diagnostic attempts/reservation): 22.908s; completed probe stages plus review plus60s reserve = 724.196s, below3600s. Subsequent render/delivery timing stays in the ledger/transport sidecars.

Protected 2632 tracked engine/controller, accepted, source and historical evidence files retain SHA256 identity. Historical attribution/v6 contract outputs and engineering P5 observer/action/metric streams are byte-identical to previous binaries. All 160 raw/request hashes, deaths, shell attribution and failure/search/fork/rollout counters reconcile. No historical output was rewritten.

Evidence: [COMPACT.json](s4_collective_probe_v1/COMPACT.json), [SUMMARY.json](s4_collective_probe_v1/SUMMARY.json), [FIGHTS.json](s4_collective_probe_v1/FIGHTS.json), [ANALYSIS_VERIFICATION.json](s4_collective_probe_v1/ANALYSIS_VERIFICATION.json), [P5_SANITY.json](s4_collective_probe_v1/P5_SANITY.json), [P5_PARITY.json](s4_collective_probe_v1/P5_PARITY.json), [HISTORICAL_FIXTURES.json](s4_collective_probe_v1/HISTORICAL_FIXTURES.json). Raw compressed 30Hz observer streams and requests stay local by SHA256/byte count in [RAW_FILES_LOCAL.json](s4_collective_probe_v1/RAW_FILES_LOCAL.json). No committed file exceeds 45MB. Reproduce using build.py, check.py, run.py (single-use refuses existing raw), recount_final.py and render.py; bootstrap.py is the historical declaration helper; analyze.py/report.py are retained pre-fight drafts; recount.py is the preserved incorrect post-combat audit draft. stage_final.py selects recount_final.py/render.py. These are not rerun generators.

Stored audit correction: the original pre-fight1400×800 post-outside check was correct. A post-combat audit draft incorrectly used the 1200×700 struct defaults; independent review caught that rules factories set the actual arena to1400×800. boundary_audit.py recounts all 120 intervention streams using the native factory/codec/request chain, changing only post_outside_gun_ticks in 37 fights. Every other measured field, aggregate and outcome is asserted identical. Drafts and before-fix summaries remain preserved. Original fight code pins stay byte-identical; no intervention, seed, threshold or fight changed. Final reproduction uses recount_final.py. [AUDIT_CORRECTION.json](s4_collective_probe_v1/AUDIT_CORRECTION.json) and [BOUNDARY_VERIFICATION.json](s4_collective_probe_v1/BOUNDARY_VERIFICATION.json) retain provenance.

Final independent results recheck: APPROVE_WITH_NOTES, no blocking findings; [RESULTS_RECHECK.md](s4_collective_probe_v1/RESULTS_RECHECK.md) records sampled scope and corrected counter verification.

Owner rechecks: [OWNER_RECHECK.md](s4_collective_probe_v1/OWNER_RECHECK.md), verbatim request and dispositions. Claude CLI loggedIn=false; separate Codex reviewer is the disclosed same-family fallback. PLAN_CURRENT remains unedited by this task. Delivery uses own explicit pathspecs with normal hooks, or an independently fetched verified bundle if .git is unwritable; adjacent DELIVERY_TRANSPORT.json records identity.
