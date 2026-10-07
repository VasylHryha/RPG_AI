DONE

Stored-data diagnostic of P10/P11 regular, with P5 regular as contrast: 60 fights, 10 paired clusters per arm, reviewed run a13b51cfe7525fd5951e94e73bdae73f2692c597. No fights, simulations, combat tests, or process inspection were executed. All 370 local raw files were size/SHA256 verified before any trace was parsed. The same parser independently reconciled all 120 original probe measurements, including novice sanity cells. Original receipts and raw bytes remain unchanged.

Enemy ranged units are the largest source of **gun last hits** after spacing, but artillery remains the larger source of **total gun HP loss** across the full P10 and P11 panels. Their ranged screen reaches our battery early; our ranged support is usually too far away to contest that screen, and our melee attacks the enemy melee. This supports testing positioning/engagement timing alongside a narrow targeting change. It does not identify a proven cause of the two wins.

Distances below are centres in px. Native ranged-to-gun reach is 259+9+10=278 px; ranged-to-ranged reach is 277 px, melee-to-ranged reach is 36+16+9=61 px. Artillery reach is a centre band [0,320] px here. Geometric reach does not establish line clearance, windup, readiness, or an actual shot. Exact damage events and their times are distinguished from post-step snapshot geometry. Damage-event source/victim distance is measured at impact, not release; it may exceed firing reach after movement and projectile travel.

Geometry uses every 30th tick while both sides have living guns, pooling living unit-snapshots equally; whole-scope results have survival/cohort bias. The early window is literal raw time [10,20), without rounding (floating accumulation means samples are nominal seconds 11–19). “Front” means positive signed projection from the enemy gun centroid toward the own gun centroid, using a perpendicular plane through that centroid; it is a relative gun-front convention, not a fitted line-normal or every-gun guarantee. Singleton batteries are allowed. For action analysis, the inherited gun phase means enemy guns and own guns alive in the **prepare** snapshot; it does not mean every gun actually reached its commitment post. Commanded movement is not measured displacement. Target shares count selected action targets, not shots or damage.

| Early [10,20) s geometry (pooled median; p10–p90) | P5 | P10 | P11 |
|---|---|---|---|
|Enemy ranged → nearest enemy gun|55.1 (25.7–87.0)|58.5 (28.8–85.0)|59.0 (28.8–85.6)|
|Enemy ranged → nearest own gun|255.4 (217.8–295.8)|220.8 (175.3–263.0)|231.3 (192.1–270.0)|
|Enemy ranged signed forward offset|53.3 (5.3–108.5)|50.6 (4.4–105.6)|51.9 (7.8–106.3)|
|Own ranged → nearest own gun|162.2 (94.7–281.8)|96.1 (41.8–156.0)|110.5 (51.5–174.3)|
|Own ranged → nearest enemy ranged|333.0 (265.6–420.7)|323.7 (261.8–388.8)|321.6 (264.1–388.5)|
|Own melee → nearest own gun|98.1 (47.1–143.5)|55.9 (26.2–104.3)|69.6 (27.7–119.7)|
|Own melee → nearest enemy ranged|155.1 (128.4–199.6)|157.0 (129.5–205.4)|156.7 (128.2–202.8)|
|Enemy ranged in front of enemy gun centroid plane|92.69%|92.26%|93.76%|
|Own gun snapshots in enemy ranged reach|98.30%|89.79%|96.18%|
|Own gun snapshots safe from ranged AND selected gun target in band|0.54%|4.14%|1.83%|

At this window, the enemy ranged screen is about 55–59 px from its own nearest gun and about 51–53 px forward of its battery centroid. P10/P11 own guns are nearer that screen than P5, despite the spacing reducing splash. The screen can reach almost all our gun snapshots, while median own-ranged distance to enemy ranged is 322–324 px, beyond 277 px reach. Own melee is closer to our guns but still about 157 px from enemy ranged, beyond its 61 px reach. Geometry sample counts, whole-scope distances and every first-reach unit identity are in COMPACT.json.

| Timing (median across 20 fights; p10–p90), seconds | P5 | P10 | P11 |
|---|---|---|---|
|First observed enemy ranged reach of any own gun|9.633 (9.433–9.770)|9.767 (9.317–9.973)|9.750 (9.497–9.867)|
|First enemy ranged HP damage to an own gun|11.517 (10.817–13.437)|11.467 (11.063–12.383)|11.767 (11.090–12.637)|

All 20 fights in each arm have observed reach and ranged gun damage. First reach is the first recorded geometric-reach post-step snapshot (1/30 s cadence); native within-step entry, shot release and first damage can differ. Enemy ranged reaches the guns at about 9.6–9.8 s, with first HP loss about 11.5–11.8 s.

| Arm / damage interval (s) | Enemy ranged HP (% all gun HP lost) | Enemy artillery HP (% all gun HP lost) | Other HP | Cumulative ranged / artillery shares |
|---|---|---|---|---|
|P5 [10,20)|3260 (9.6%)|30313 (89.5%)|295|9.6% / 89.5%|
|P5 [20,30)|608 (26.1%)|1502 (64.4%)|222|10.7% / 87.9%|
|P5 full fight|3868 (10.7%)|31815 (87.9%)|517|same|
|P10 [10,20)|5271 (27.0%)|12335 (63.3%)|1890|27.0% / 63.3%|
|P10 [20,30)|7438 (52.4%)|6372 (44.9%)|376|37.7% / 55.5%|
|P10 [30,60)|1374 (54.6%)|1144 (45.4%)|0|38.9% / 54.8%|
|P10 full fight|14083 (38.9%)|19851 (54.8%)|2266|same|
|P11 [10,20)|4727 (26.9%)|11116 (63.2%)|1749|26.9% / 63.2%|
|P11 [20,30)|8268 (53.9%)|6282 (41.0%)|780|39.5% / 52.8%|
|P11 [30,60)|2603 (80.9%)|613 (19.1%)|0|43.2% / 49.8%|
|P11 [60,end]|32 (100.0%)|0 (0.0%)|0|43.2% / 49.8%|
|P11 full fight|15630 (43.2%)|18011 (49.8%)|2529|same|

Denominator: all actual own-gun HP lost in that interval, including enemy melee and friendly damage; lethal overkill is capped by dealt HP. P5/P10 lose 36,200 HP in total; P11 loses 36,170 (one gun ends with 30 HP). “Other” consists of P5 enemy melee 354 / friendly ranged 163; P10 enemy melee 632 / friendly ranged 1,553 / friendly artillery 81; P11 enemy melee 904 / friendly ranged 1,565 / friendly artillery 60. Per-fight HP conservation was checked against initial and terminal living gun HP. No gun damage is recorded before 10 s. After 20 s ranged becomes the larger interval damage source in both spacing arms; it is not the larger full-fight source.

| Prepare gun-phase own ranged behavior (% living ranged action ticks) | P5 | P10 | P11 |
|---|---|---|---|
|No selected target|58.01%|61.76%|55.74%|
|Enemy melee target|39.67%|30.56%|34.66%|
|Enemy ranged target|1.78%|7.35%|9.26%|
|Enemy gun target|0.54%|0.33%|0.34%|
|Reachable enemy ranged that threatens an own gun|7.24%|11.20%|14.26%|
|Such a threat selected, conditional on reachable opportunity|18.18%|55.84%|56.79%|

All counted own direct-unit ticks carry a movement command; this does not establish actual movement or cancellation of firing. Own ranged mostly has no selected target or targets enemy melee. Own melee selects only enemy melee or no target, has zero geometrically reachable gun-threatening enemy-ranged opportunities, and records zero enemy-ranged last hits. The enemy ranged line is not being removed early by our direct screen.

| Enemy ranged killed by OUR units (panel totals; 30 enemy ranged per fight) | P5 | P10 | P11 |
|---|---|---|---|
|By ranged before 20 s|2|7|4|
|By ranged before 30 s|17|46|53|
|By ranged full fight|31|82|101|
|By artillery before 20 s|158|64|126|
|By artillery full fight|158|79|156|

These are last hits, not exclusive damage contributions. Enemy friendly fire is separated: P5 2, P10 15, P11 21. Exact source/victim identities and times are retained in compact JSON. Full-fight counts include cleanup after gun losses; before-20/before-30 counts describe the protection window.

| P11 outcome comparison (descriptive) | Two wins | Eighteen nonwins |
|---|---|---|
|Mean enemy guns dead before 20 s|3.500|3.333|
|Mean enemy guns dead before 30 s|8.000|6.444|
|Mean own guns dead before 20 s|1.000|1.778|
|Mean own guns dead before 30 s|4.500|8.056|
|Mean final enemy guns destroyed|10.000|7.278|
|Mean final own guns lost|9.500|10.000|
|Mean first ranged reach, s|9.750|9.691|
|Mean first ranged damage, s|11.750|11.759|
|Mean OUR ranged enemy-ranged kills before 20 s|0.000|0.222|
|Mean OUR artillery enemy-ranged kills before 20 s|10.500|5.833|

Win-group distance values are **medians of per-fight medians**, not pooled quantiles: own ranged → enemy ranged in the early window is 315.0 px vs 324.2 in nonwins. Neither win avoids the early threat or demonstrates an early ranged screen.

| Paired cluster/orientation | Arm | Final enemy gun kills / own gun losses | Enemy guns dead <30 s | Own guns dead <30 s | OUR artillery/ranged enemy-ranged kills <20 s |
|---|---|---|---|---|---|
|c02/o0|P10|7/10|5|7|6/0|
|c09/o1|P10|6/10|6|9|0/0|
|c02/o0|P11|10/9|8|4|10/0|
|c09/o1|P11|10/10|8|5|11/0|
|c02/o0|P5|4/10|4|10|7/0|
|c09/o1|P5|2/10|2|10|4/0|

c02/o0 wins at 69.600 s with 18 own survivors and one gun (30 HP). All enemy guns are dead at 32.367 s; nine own guns die by 47.367 s. Own gun HP loss is enemy artillery 781, enemy ranged 943, friendly own ranged 56. OUR artillery kills 28 enemy ranged; OUR ranged kills zero; two enemy ranged die to enemy friendly ranged fire. Ten artillery last hits on enemy ranged occur before 20 s. The surviving gun supplies late cleanup: its last enemy-ranged kill is at 69.600 s.

c09/o1 wins at 73.467 s with 11 own survivors and no own guns. All enemy guns are dead at 34.667 s and all own guns by 42.033 s. Own gun HP loss is enemy artillery 697, enemy ranged 886, enemy melee 75, friendly own ranged 152. OUR artillery kills 14 enemy ranged, OUR ranged 15, enemy friendly ranged one. Eleven artillery enemy-ranged last hits occur before 20 s; only one own-ranged kill occurs before 30 s (23.200 s). The other fourteen own-ranged kills occur from 50.900 to 73.467 s, after the battery is lost. This win relies on later ranged cleanup rather than an early protective ranged screen.

The two wins have faster/more complete early counter-battery kills and more early artillery last hits on enemy ranged than the nonwins. Enemy ranged reaches the battery at essentially the same time. Those are outcome-conditioned associations from two fights, not causal explanations or a win-rate estimate. The paired P5/P10 rows show that the same initial seed/orientation does not reproduce P11's result with the other settings. Nothing here meets the owner's above-50% criterion or authorizes a resonator design.

The smallest single scripted candidates supported by these measurements, **not run or tuned**:

1. **Own ranged targeting only:** retain movement and gun policy; when an enemy ranged is within the unit's native legal reach and itself threatens a living own gun, prioritize that threat using one predeclared ordering. This can use the unselected reachable opportunities, but P11 already selects a threat on 56.79% of reachable ticks, and reach exists on only 14.26% of ranged ticks; the remaining opportunity is 6.16% of all gun-phase ranged ticks. It cannot solve the predominant distance gap alone. Native line clearance/readiness and friendly-fire consequences must still be checked in a future authorized probe.
2. **Own ranged position only:** retain targeting and gun policy; move ranged units to an escort position on the enemy-facing side of the battery so they can reach the gun-threatening enemy ranged before first gun damage. The early distance deficit is roughly 322−277≈45 px for the median own ranged unit in P11. That is a motivation, not a chosen escort constant or achieved-position guarantee: a single battery centroid can poorly represent a dispersed battery, and movement must preserve splash spacing and native clipping/collision behavior. Declare one escort rule before combat; keep targeting separate.
3. **Own gun commitment goal only:** retain targeting, multiplier/stop conventions and spacing; choose a gun-band post outside all observed enemy-ranged reach if a legal post exists, with one predeclared fallback when it does not. Our guns need distance ≤320 px to their gun target but >278 px from each threatening enemy ranged. On a collinear approach with the enemy screen about 52 px ahead of its guns, a 308 px post is only about 256 px from that screen; merely raising the radial distance to 320 px gives about 268 px, still inside reach. A fixed “stand slightly farther back” is therefore poorly supported; safe commitment may require an angular/end-side post or deferral. Only 1.83% of early P11 gun snapshots are both ranged-safe and within the selected gun target's band. Observed safe snapshots do not establish a maintainable, collision-free alternative post. Safety must be evaluated on the final spacing-shifted, native-clipped goal; preserving P5's zero multiplier can prevent movement toward a changed goal. Feasibility is an explicit future probe question, not a result here.

Each candidate changes one scripted policy component on P11 and needs its own owner-authorized sealed declaration/fresh entropy. No escort offset, angle, wait threshold, target ordering, or fallback was selected from these outcomes. The data favors addressing reach/placement at least alongside priority; it does not prove which candidate will win.

Reproduction: `python3 s4_ranged_threat_v1/analyze.py` then `python3 s4_ranged_threat_v1/summarize.py` from astelia_cpp. The first verifies all source raw hashes, independently audits all original probe rows, and emits [COMPACT.json](s4_ranged_threat_v1/COMPACT.json) and [SPACING_RECOMPUTATION.json](s4_ranged_threat_v1/SPACING_RECOMPUTATION.json). The second emits [DERIVED.json](s4_ranged_threat_v1/DERIVED.json) and this report. The separate reviewer pass and fixes are recorded in [OWNER_RECHECK.md](s4_ranged_threat_v1/OWNER_RECHECK.md). Raw remains local; no delivered file exceeds 45 MB. PLAN_CURRENT, DESIGN_0G, and committed source receipts were not edited.
