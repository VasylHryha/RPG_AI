PARTIAL

Stored-data fire-efficiency diagnostic, DESIGN_0G §19.5 (f169a42). All 20 fights each of P5 regular, P7 regular and P5 novice: 60/60, ten paired clusters × two orientations, team 0 controlled. All selected raw/request SHA256 and byte counts match RAW_FILES_LOCAL.json before analysis; contiguous 30 Hz frames, shell attribution and historical launch/hit/casualty counts reconcile. No fights, simulations, tuning, registration or status changes. PARTIAL refers to unavailable readiness, exact nearest-at-death positions and causal switch losses, not missing fights.

Definitions and normalization

Observer `units` indices: 0 id, 1 team, 2 role (0 melee, 1 ranged, 2 artillery), 3–4 centre x/y, 5 HP, 6 radius, 7 native range, 8 minimum range, 9–11 formation slot, 12 prep (windup progress), 13 actual target. `actions`: 0 id, 1 team, 2 target, 3–4 goal, 5 multiplier, 6 stop distance, 7 release kind, 8 move, 9 keep, 10 post, 11 bound, 12 decision inReach. `launches`: 0 source, 1 target, 2 team, 3–4 fixed shell aim point, 5 born, 6 scheduled impact, 7 splash, 8 barrage, 9 slow. Damage uses source/target IDs, team/role, dealt HP, t, died/killer and exact source/target coordinates. Schema and semantics sources match original declaration pins.

Living gun-time sums guns alive at each interval's start ×1/30 s, including the death interval; this is a discrete exposure denominator, not an assumption about survival within the tick. Range opportunity samples that same start snapshot: any living opposing target with inclusive centre distance in [minRange,range]; no guessed line-of-fire or readiness requirement. Moving means >1e-6 px centre displacement across adjacent snapshots, including collisions/separation/reflexes; death intervals lack end positions and are excluded from its known denominator. Movement-command proxy: move=true, multiplier>0 and goal farther than stop+1e-9 from the preceding position. It is an intent proxy, not native movement execution; enemy formation may issue it while physically stationary. Windup means start-snapshot prep>0. Firing means a damaging shell launch in the interval, with each launch interval contributing 1/30 s; it is not sustained fire time. These indicators overlap and do not sum to 100%.

Ready but not firing: **unavailable for both sides**, since observer frames omit cooldown, energy, castOk and cast target. Windup is reported separately and is not readiness. A reset without a launch is a surviving gun's decreasing prep; it is observable consumption/reset, not automatically an interrupted windup or a movement cause. Switch losses are unavailable as a causal/counterfactual count.

Gun-time and firing (pooled; rates in launches/gun-second)

|Arm/head|Side|Launches / living gun-s|Moving / known ticks|Move-command / living ticks|Any target range / living ticks|Enemy gun range / living ticks|Windup / living ticks|Launch intervals / living ticks|
|---|---|---|---|---|---|---|---|---|
|P5 regular|0|1676/3650.07 = 0.459|104863/109302 (95.9%)|108518/109502 (99.1%)|61091/109502 (55.8%)|40656/109502 (37.1%)|34788/109502 (31.8%)|1676/109502 (1.5%)|
|P5 regular|1|2249/20362.10 = 0.110|256777/610800 (42.0%)|610863/610863 (100.0%)|81077/610863 (13.3%)|38046/610863 (6.2%)|407816/610863 (66.8%)|2249/610863 (0.4%)|
|P7 regular|0|1550/3497.00 = 0.443|102805/104710 (98.2%)|104424/104910 (99.5%)|56499/104910 (53.9%)|35185/104910 (33.5%)|32199/104910 (30.7%)|1550/104910 (1.5%)|
|P7 regular|1|2053/21801.17 = 0.094|280353/653986 (42.9%)|654035/654035 (100.0%)|74871/654035 (11.4%)|34563/654035 (5.3%)|420405/654035 (64.3%)|2053/654035 (0.3%)|
|P5 novice|0|2867/5698.13 = 0.503|169423/170919 (99.1%)|170562/170944 (99.8%)|100406/170944 (58.7%)|37156/170944 (21.7%)|73781/170944 (43.2%)|2867/170944 (1.7%)|
|P5 novice|1|1059/2651.87 = 0.399|54058/79356 (68.1%)|42689/79556 (53.7%)|38062/79556 (47.8%)|22362/79556 (28.1%)|21830/79556 (27.4%)|1059/79556 (1.3%)|

Moving excludes 200 death intervals per regular own battery, 63/49 per regular enemy battery, and 25/200 for novice own/enemy. All other samples are included. Long enemy survival after our battery dies dilutes whole-fight rates; compare matched clock windows below rather than reading that dilution as inefficient enemy fire.

Movement, windup and target changes

|Arm/head|Side|Launches while displaced / launches with known displacement|Resets without launch (at command start / at displacement start / with target change)|Launch-to-launch gap median, observed n|Command starts: observed / next-start censored / death censored / end censored|In-range command-start→launch mean, observed n|
|---|---|---|---|---|---|---|
|P5 regular|0|1547/1667 (92.8%)|8 (0/0/3)|1.200s, 1476|351/203/50/0 (all 604)|0.450s, 151|
|P5 regular|1|1671/2248 (74.3%)|98 (0/3/9)|1.200s, 2049|200/0/0/0 (all 200)|unavailable, 0|
|P7 regular|0|1499/1546 (97.0%)|6 (0/0/2)|1.200s, 1350|292/116/39/0 (all 447)|0.428s, 92|
|P7 regular|1|1515/2052 (73.8%)|100 (0/10/10)|1.200s, 1853|200/0/0/0 (all 200)|unavailable, 0|
|P5 novice|0|2825/2867 (98.5%)|0 (0/0/0)|1.200s, 2667|242/3/0/0 (all 245)|0.591s, 42|
|P5 novice|1|366/1056 (34.7%)|1 (1/0/0)|1.200s, 859|271/16/22/0 (all 309)|0.468s, 67|

Command-start gaps run from the stored decision tick to the first launch before another start, death or fight end. Censored cases remain null; observed means do not represent all starts. In-range conditions use the preceding snapshot. Physical displacement-start gap distributions and every start/reset/switch record are also in JSON, with their censor counts; they include collision motion. Enemy regular has no in-range command starts: its proxy stays active from initial approach. Its unavailable cell is not zero delay.

|Arm/head|Side|In-range command launch rate / exposure|In-range hold launch rate / exposure|Displacement starts: observed / censored|In-range displacement-start→launch mean, observed n|Windup target changes / all changes; launching same tick|
|---|---|---|---|---|---|
|P5 regular|0|1646/2003.57s = 0.822|30/32.80s = 0.915|552/1128 (all 1680)|0.359s, 352|869/1645; 22|
|P5 regular|1|2249/2702.57s = 0.832|unavailable (0s)|1640/17723 (all 19363)|0.436s, 1459|1283/3296; 583|
|P7 regular|0|1536/1867.10s = 0.823|14/16.20s = 0.864|359/502 (all 861)|0.356s, 159|689/1368; 13|
|P7 regular|1|2052/2495.70s = 0.822|unavailable (0s)|1570/16855 (all 18425)|0.531s, 1428|1190/3080; 530|
|P5 novice|0|2857/3334.13s = 0.857|10/12.73s = 0.785|312/56 (all 368)|0.571s, 112|2222/4091; 178|
|P5 novice|1|44/39.83s = 1.105|1015/1228.90s = 0.826|559/316 (all 875)|0.466s, 445|528/1656; 19|

Pinned gamePrep keeps increasing prep while moving or changing targets. The measured 1.2s typical cadence and launches during displacement do not support movement-cancelled windup as the main loss. Hold exposure for our guns is tiny and selected, so the rates cannot identify a stop-moving benefit. Resets may be releases consumed without a shell because the current target is absent/outside the release band; no cast-target/energy log identifies their exact cause. Target changes during prep usually do not reset prep.

Target allocation and hits over time

|Arm/head|Side|Launch-time window s|All launches / living gun-s (rate)|Aimed at guns / all launches|Gun-targeted shells hitting any gun / aimed at guns|Hitting intended gun / aimed at guns|Nongun-targeted shells damaging guns / aimed elsewhere|Gun victim hits from gun / other targeting|
|---|---|---|---|---|---|---|---|---|
|P5 regular|0|[0,10)|336/2006.67 (0.167)|0/336 (0.0%)|0/0 (unavailable)|0/0 (unavailable)|0/336 (0.0%)|0/0|
|P5 regular|0|[10,20)|1300/1594.33 (0.815)|1080/1300 (83.1%)|915/1080 (84.7%)|887/1080 (82.1%)|0/220 (0.0%)|1018/0|
|P5 regular|0|[20,30)|40/49.07 (0.815)|40/40 (100.0%)|38/40 (95.0%)|38/40 (95.0%)|0/0 (unavailable)|38/0|
|P5 regular|1|[0,10)|5/2006.67 (0.002)|0/5 (0.0%)|0/0 (unavailable)|0/0 (unavailable)|0/5 (0.0%)|0/0|
|P5 regular|1|[10,20)|1325/1750.63 (0.757)|439/1325 (33.1%)|412/439 (93.8%)|349/439 (79.5%)|127/886 (14.3%)|1705/420|
|P5 regular|1|[20,30)|491/1371.40 (0.358)|72/491 (14.7%)|43/72 (59.7%)|37/72 (51.4%)|5/419 (1.2%)|47/5|
|P5 regular|1|[30,60)|399/4073.40 (0.098)|0/399 (0.0%)|0/0 (unavailable)|0/0 (unavailable)|0/399 (0.0%)|0/0|
|P5 regular|1|[60,150)|29/11160.00 (0.003)|0/29 (0.0%)|0/0 (unavailable)|0/0 (unavailable)|0/29 (0.0%)|0/0|
|P7 regular|0|[0,10)|336/2006.67 (0.167)|0/336 (0.0%)|0/0 (unavailable)|0/0 (unavailable)|0/336 (0.0%)|0/0|
|P7 regular|0|[10,20)|1205/1479.53 (0.814)|809/1205 (67.1%)|675/809 (83.4%)|663/809 (82.0%)|0/396 (0.0%)|750/0|
|P7 regular|0|[20,30)|9/10.80 (0.833)|9/9 (100.0%)|8/9 (88.9%)|8/9 (88.9%)|0/0 (unavailable)|8/0|
|P7 regular|1|[0,10)|5/2006.67 (0.002)|0/5 (0.0%)|0/0 (unavailable)|0/0 (unavailable)|0/5 (0.0%)|0/0|
|P7 regular|1|[10,20)|1358/1808.27 (0.751)|448/1358 (33.0%)|397/448 (88.6%)|323/448 (72.1%)|154/910 (16.9%)|1674/500|
|P7 regular|1|[20,30)|418/1516.13 (0.276)|22/418 (5.3%)|13/22 (59.1%)|12/22 (54.5%)|0/396 (0.0%)|15/0|
|P7 regular|1|[30,60)|253/4320.10 (0.059)|0/253 (0.0%)|0/0 (unavailable)|0/0 (unavailable)|0/253 (0.0%)|0/0|
|P7 regular|1|[60,150)|19/12150.00 (0.002)|0/19 (0.0%)|0/0 (unavailable)|0/0 (unavailable)|0/19 (0.0%)|0/0|
|P5 novice|0|[0,10)|554/2006.67 (0.276)|163/554 (29.4%)|162/163 (99.4%)|162/163 (99.4%)|0/391 (0.0%)|646/0|
|P5 novice|0|[10,20)|1522/1919.27 (0.793)|876/1522 (57.6%)|632/876 (72.1%)|522/876 (59.6%)|1/646 (0.2%)|1952/2|
|P5 novice|0|[20,30)|729/1622.17 (0.449)|0/729 (0.0%)|0/0 (unavailable)|0/0 (unavailable)|0/729 (0.0%)|0/0|
|P5 novice|0|[30,60)|62/150.03 (0.413)|0/62 (0.0%)|0/0 (unavailable)|0/0 (unavailable)|0/62 (0.0%)|0/0|
|P5 novice|1|[0,10)|506/2006.67 (0.252)|0/506 (0.0%)|0/0 (unavailable)|0/0 (unavailable)|33/506 (6.5%)|0/33|
|P5 novice|1|[10,20)|553/645.20 (0.857)|109/553 (19.7%)|109/109 (100.0%)|104/109 (95.4%)|0/444 (0.0%)|430/0|

Bins use launch time, not damage time; eventual hits can cross a bin boundary. Living exposure uses interval-start time. Last bin includes any floating-point endpoint at 150s. Hit means positive dealt damage, not a projectile near miss. Any-gun success counts a shell once; intended-gun success requires its release target. Gun-victim hits count all distinct opposing guns damaged by that shell. Shell attribution uses source and unique scheduled-impact interval; all launches including airborne end shells remain denominators. Incidental gun splash from other targeting is reported separately.

|Arm/head|Side|Gun targeting / all launches|Any-gun successful targeted shells|Gun victims / successful targeted shell|Gun damage from gun / other targeting (HP)|Already dead before scheduled impact / gun launches; no gun hit|Airborne target switches / all launches; gun-targeted hit / switched gun launches|
|---|---|---|---|---|---|---|
|P5 regular|0|1120/1676 (66.8%)|953/1120 (85.1%)|1056/953 = 1.11|14958/0|191/1120; 164|447/1676; 132/289|
|P5 regular|1|511/2249 (22.7%)|455/511 (89.0%)|1752/455 = 3.85|25238/6366|122/511; 56|1280/2249; 238/294|
|P7 regular|0|818/1550 (52.8%)|683/818 (83.5%)|758/683 = 1.11|10698/0|139/818; 128|376/1550; 30/149|
|P7 regular|1|470/2053 (22.9%)|410/470 (87.2%)|1689/410 = 4.12|24180/7486|130/470; 58|1207/2053; 215/273|
|P5 novice|0|1039/2867 (36.2%)|794/1039 (76.4%)|2598/794 = 3.27|36198/2|343/1039; 235|1200/2867; 180/415|
|P5 novice|1|109/1059 (10.3%)|109/109 (100.0%)|430/109 = 3.94|6369/495|5/109; 0|330/1059; 37/37|

Launches lost **because of** target switches: unavailable. Released shells retain a fixed aim point; a later target switch does not cancel them. Observed switches, resets and misses do not identify a counterfactual loss. Already-dead-target counts compare exact logged death time strictly before scheduled impact, exclude same-time ties, and may include splash on survivors. These support examining redundant commitments to doomed targets, not attributing losses to switching itself. Every gun-targeted launch here resolved before fight end; airborne end counts remain explicit in JSON.

Own gun deaths

Exact killer and death x/y are retained for every own gun death in JSON (`fights[].deaths[]`, 425 rows). Exact distance to the killer is `killer_distance_exact`. Exact nearest living enemy gun/ranged distance at death is **unavailable**: other units' coordinates and within-step alive ordering are absent at that instant. The following are centre-distance estimates from the exact victim death point to enemy centres alive in the preceding snapshot, 1/30s old. A nearest enemy may move or die in that step; no invented error bound is applied. Ranged reach estimates use surface gap (distance minus both radii); gun bands use centre distance.

|Arm/head|Deaths|Nearest enemy gun previous-snapshot mean / median px (available n)|Nearest enemy ranged previous-snapshot mean / median px (available n)|Within gun band / available; within ranged reach / available|Killers (team_role: count)|
|---|---|---|---|---|---|
|P5 regular|200|297.4/301.7 (200)|221.8/221.4 (200)|200/200; 199/200|1_ranged: 55, 1_artillery: 142, 1_melee: 1, 0_ranged: 2|
|P7 regular|200|282.3/287.4 (200)|205.6/209.9 (200)|200/200; 200/200|1_ranged: 56, 1_artillery: 136, 0_ranged: 2, 1_melee: 6|
|P5 novice|25|304.5/307.9 (14)|214.8/210.2 (25)|14/14; 20/25|1_artillery: 12, 1_melee: 1, 1_ranged: 12|

What explains the exchange in these traces

**Splash multiplicity and exposure explain the recorded HP exchange.** P5 regular's 953/1120 gun-targeted hits (47.65 successful shells/fight) delivered 1056 gun-victim hits and 14958 HP. Enemy gun-targeted hits were fewer, 455/511 (22.75/fight), but each successful shell damaged 3.85 guns against our 1.11: 1752 victim hits and 25238 HP. A further 132/1738 shells aimed at other units splashed 425 gun victims for 6366 HP. Total enemy artillery damage to our guns was 31604 HP (1580.2/fight), **2.11×** our 14958 HP (747.9/fight). It accounts for 87.3% of the 36200 HP lost by all 200 own guns; enemy ranged adds 4240 HP (11.7%), enemy melee 148 and friendly ranged 208. Killer counts (142 artillery, 55 ranged, 1 melee, 2 friendly) record last hits and differ from damage shares. Our shells damaged mostly one or two enemy guns; theirs damaged up to nine of ours per shell. Equal reach and equal successful-shell counts would still not imply equal damage.

P7 repeats and worsens the same exchange: our 683/818 hits yield 758 victim hits, 10698 HP; their 410/470 yield 1689 victim hits, 24180 HP, plus 500 incidental victims/7486 HP. Artillery total 31666 HP is **2.96×** our shell damage. Enemy ranged adds 3961 HP. All 200 own guns die; only 49 enemy guns die, versus 63 in P5. The bundles do not isolate why clustering/exposure changes.

**Enemy firing uptime or stronger counter-battery priority is not demonstrated.** Own gun-target shares are 66.8% P5 /52.8% P7 versus enemy 22.7%/22.9%. Own normalized whole-fight firing rates are higher; in [10,20)s they are about 0.815/0.814 versus enemy 0.757/0.751 launches/gun-second. Range-conditioned command rates are own 0.822/0.823 versus enemy 0.832/0.822 for P5/P7. Own interlaunch medians are 1.2s despite motion. The enemy's advantage is damage per successful shell and supported exposure, not more launches per living gun-second. P5 and P7 spend only 37.1%/33.5% of own gun-time in enemy-gun range; early shells go to other units. P7 sends 302 fewer shells at guns than P5 (818 vs1120), delivering 4260 less HP to enemy guns. Staging/targeting/movement remain a combined intervention.

**The novice contrast reverses splash effectiveness.** Our 794/1039 successful gun-targeted shells hit 2598 gun victims (3.27 per success) and deal 36198 HP plus 2 incidental HP: the full 200 enemy guns' HP. All 200 enemy guns die while only 25 own guns die. Our hit rate is lower than against regular (76.4% vs85.1%) yet the gun exchange is vastly better. The regular line's dispersed gun geometry is consistent with the lower victim multiplicity; this stored comparison does not isolate formation or dodge as a causal treatment. Already-dead targets account for 164/167 P5 regular and 128/135 P7 regular gun-targeted no-gun-hit launches. Avoidable overcommitment is plausible; changing targets itself is not proven to cause those misses.

Smallest scripted hypotheses supported; **not run**

1. Preserve P5 target/movement rules and add only a battery spacing rule sized to avoid shared splash footprints. The 3.85-versus1.11 victim multiplicity supports a spacing/exposure hypothesis. Native clipping, arena space and maintaining focus/range must be checked in any separately authorized probe; no setting is selected here.
2. Preserve P5 and add only an estimated-in-flight-damage cap on further shells committed to a gun, retargeting once outstanding damage covers its HP. The 164/167 and128/135 no-gun-hit shells whose target died before scheduled impact support redundant-shell allocation as a candidate. Current controllers lack shell observations; a scripted probe would need explicitly authorized launch bookkeeping, not hidden observer input.
3. Preserve gun actions and change only ranged screen targeting toward enemy ranged threatening our guns. Enemy ranged contributes 4240/3961 HP and55/56 gun last hits; nearby ranged exposure supports a screen hypothesis, but a screen may obstruct own fire or cluster with guns.
4. A range-hold rule could test reduced approach/exposure or better spacing, but these traces do not support windup cancellation as its mechanism. Blanket counter-battery priority is also weakly supported: P5 already assigns two-thirds of shells to guns. Neither is the leading fire-efficiency fix from these numbers.

Reproduce with `python3 evidence/tactical_composition_demo/astelia_cpp/s4_fire_efficiency_v1/analyze.py` then `python3 evidence/tactical_composition_demo/astelia_cpp/s4_fire_efficiency_v1/render.py`. [COMPACT.json](s4_fire_efficiency_v1/COMPACT.json) retains pooled counts, time bins and every fight's denominators/deaths/gaps/resets/switches; [VERIFICATION.json](s4_fire_efficiency_v1/VERIFICATION.json) pins inputs and script. [OWNER_RECHECK.md](s4_fire_efficiency_v1/OWNER_RECHECK.md) records the verbatim request, independent findings and disposition. Per user instruction PLAN_CURRENT and DESIGN_0G remain untouched. Raw stays local; no delivered file exceeds45 MB.
