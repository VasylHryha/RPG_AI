PARTIAL

# Escort mechanism diagnostic: temporary protection through sacrificial exposure

Reviewed run: `0f8e823077d83bca76a66532a1988d2ec7c9052a`. Stored traces only: P11/P12/P13 × regular/novice, 20 fights per cell, 10 paired clusters with two orientations. No fights, simulations, tuning or registration. All 620 entries in `s4_escort_probe_v1/RAW_FILES_LOCAL.json` matched bytes and SHA256 before parsing (866,788,710 bytes). Damage, deaths, targets, artillery launches and shell attribution are complete. PARTIAL applies to exact direct-shot interception and causal counterfactuals, which these traces cannot identify. All numbers below derive from adjacent `s4_escort_mechanism_v1/COMPACT.json`, `PER_FIGHT.json` and `SHELL_ATTRIBUTION.json`.

The supported explanation is a brief protection window bought by exposing and clustering our ranged units. Enemy fire toward our guns falls early, those guns survive longer, and our counter-battery shells kill more of the enemy ranged screen incidentally. The escorts themselves almost never kill that screen. This is a mechanism consistent with the traces; position alone was varied, so these observations do not isolate diversion, collision effects and collateral geometry into independent causal effects.

## 1. P11 control first and cost accounting

| Cell | Elimination wins /20 | Mean S | Own losses/fight | Gun losses/fight | Ranged losses/fight | Melee losses/fight |
|---|---|---|---|---|---|---|
| P11 regular | 1 | -13.7 | 43.5 | 9.9 | 23.6 | 10 |
| P12 regular | 6 | -14.2 | 48.75 | 8.75 | 30 | 10 |
| P13 regular | 5 | -17.65 | 49.3 | 9.3 | 30 | 10 |
| P11 novice | 20 | 38.75 | 11.25 | 1.25 | 0 | 10 |
| P12 novice | 20 | 19.05 | 30.95 | 0.05 | 20.9 | 10 |
| P13 novice | 20 | 11.25 | 38.75 | 0.15 | 28.75 | 9.85 |

Against novice, the increase from 11.25 to 30.95/38.75 losses is entirely explained by ranged losses (0 → 20.9/28.75), partly offset by gun savings (1.25 → 0.05/0.15) and P13’s small melee saving (10 → 9.85). Every arm still eliminates novice 20/20. Against regular, all 600 ranged units die in P12 and P13; P11 loses 472/600. The 11 escort wins are genuine but neither arm meets the owner’s >50% criterion. See the separate run review for the declared 19.8.1 readings and the 11 terminal identities.

## 2. What the enemy selects and shoots, over time

Enemy artillery counts below are exact launch events. Enemy ranged “releases” are a lower bound inferred from a living unit’s preparation resetting from positive to zero with Direct/DodgeFire and a selected target. Same-step deceased shooters are unavailable; these are not exact projectile-launch receipts. Exact selected-target tick tables, including no target, are in COMPACT JSON. P11 ranged units are the comparison cohort; only P12/P13 are escorts.

| Cell | Bin s | Enemy shells → guns/ranged/melee | Enemy ranged inferred releases → guns/ranged/melee |
|---|---|---|---|
| P11 regular | 0–10 | 0/0/8 | 0/14/62 |
| P11 regular | 10–20 | 310/131/956 | 1477/436/888 |
| P11 regular | 20–30 | 344/317/0 | 1366/1145/0 |
| P11 regular | 30–60 | 40/215/4 | 259/1122/27 |
| P11 regular | 60–150.1 | 0/84/0 | 0/569/0 |
| P12 regular | 0–10 | 0/0/0 | 0/4/9 |
| P12 regular | 10–20 | 106/462/863 | 470/771/1223 |
| P12 regular | 20–30 | 600/25/15 | 1779/28/8 |
| P12 regular | 30–60 | 46/0/0 | 339/0/0 |
| P12 regular | 60–150.1 | 0/0/0 | 8/0/0 |
| P13 regular | 0–10 | 0/75/78 | 2/22/33 |
| P13 regular | 10–20 | 256/295/850 | 876/560/1314 |
| P13 regular | 20–30 | 584/0/0 | 1856/0/0 |
| P13 regular | 30–60 | 39/0/0 | 351/0/31 |
| P13 regular | 60–150.1 | 0/0/0 | 13/0/0 |
| P11 novice | 0–10 | 0/0/505 | 11/30/319 |
| P11 novice | 10–20 | 148/0/412 | 1688/839/371 |
| P11 novice | 20–30 | 0/0/0 | 84/935/0 |
| P11 novice | 30–60 | 0/0/0 | 8/12/0 |
| P11 novice | 60–150.1 | 0/0/0 | 0/0/0 |
| P12 novice | 0–10 | 0/0/440 | 0/67/224 |
| P12 novice | 10–20 | 0/178/438 | 202/1956/518 |
| P12 novice | 20–30 | 0/0/0 | 434/308/0 |
| P12 novice | 30–60 | 0/0/0 | 7/1/0 |
| P12 novice | 60–150.1 | 0/0/0 | 0/0/0 |
| P13 novice | 0–10 | 0/156/412 | 0/163/251 |
| P13 novice | 10–20 | 0/183/293 | 409/730/1509 |
| P13 novice | 20–30 | 0/0/0 | 460/75/178 |
| P13 novice | 30–60 | 0/0/0 | 9/2/5 |
| P13 novice | 60–150.1 | 0/0/0 | 0/0/0 |

Regular 10–20 s: artillery launches aimed at our guns fall 310 → 106/256; inferred enemy ranged releases aimed at guns fall 1,477 → 470/876. Enemy shells aimed at escorts increase 131 → 462/295. Once escorts die, gun-targeted artillery launches rise during 20–30 s (344 → 600/584), and ranged releases aimed at guns rise (1,366 → 1,779/1,856). Thus the initial protection is temporary, not a reduction of every full-fight threat.

## 3. Actual HP lost, with capped damage and friendly sources

Each row is pooled HP from 20 fights. Event bins are literal [0,10), [10,20), [20,30), [30,60), [60,150.1); HP conservation was independently asserted for every one of the 12,000 initial units. Zero means no damage, not an unavailable observation. Full melee-cohort and opposing-cohort breakdowns remain in JSON.

| Cell | Bin s | Victim | Enemy artillery HP | Enemy ranged HP | Enemy melee HP | Friendly artillery HP | Friendly ranged HP | Friendly melee HP |
|---|---|---|---|---|---|---|---|---|
| P11 regular | 0–10 | guns | 0 | 0 | 0 | 0 | 0 | 0 |
| P11 regular | 0–10 | ranged | 0 | 0 | 0 | 0 | 0 | 0 |
| P11 regular | 10–20 | guns | 12187 | 4733 | 368 | 0 | 1192 | 0 |
| P11 regular | 10–20 | ranged | 5257 | 3454 | 0 | 0 | 32 | 0 |
| P11 regular | 20–30 | guns | 5984 | 8480 | 608 | 39 | 304 | 0 |
| P11 regular | 20–30 | ranged | 11178 | 7078 | 0 | 0 | 96 | 0 |
| P11 regular | 30–60 | guns | 514 | 1625 | 0 | 0 | 0 | 0 |
| P11 regular | 30–60 | ranged | 8595 | 4875 | 0 | 0 | 128 | 0 |
| P11 regular | 60–150.1 | guns | 0 | 0 | 0 | 0 | 0 | 0 |
| P11 regular | 60–150.1 | ranged | 2944 | 2997 | 0 | 0 | 0 | 0 |
| P12 regular | 0–10 | guns | 0 | 0 | 0 | 0 | 0 | 0 |
| P12 regular | 0–10 | ranged | 0 | 0 | 0 | 0 | 0 | 0 |
| P12 regular | 10–20 | guns | 9850 | 1575 | 144 | 15 | 0 | 0 |
| P12 regular | 10–20 | ranged | 51750 | 2463 | 317 | 169 | 92 | 0 |
| P12 regular | 20–30 | guns | 8229 | 9406 | 2202 | 15 | 0 | 0 |
| P12 regular | 20–30 | ranged | 301 | 92 | 16 | 0 | 0 | 0 |
| P12 regular | 30–60 | guns | 564 | 2149 | 20 | 0 | 0 | 0 |
| P12 regular | 30–60 | ranged | 0 | 0 | 0 | 0 | 0 | 0 |
| P12 regular | 60–150.1 | guns | 0 | 48 | 0 | 0 | 0 | 0 |
| P12 regular | 60–150.1 | ranged | 0 | 0 | 0 | 0 | 0 | 0 |
| P13 regular | 0–10 | guns | 0 | 0 | 0 | 0 | 0 | 0 |
| P13 regular | 0–10 | ranged | 7485 | 24 | 0 | 0 | 48 | 0 |
| P13 regular | 10–20 | guns | 8109 | 3311 | 288 | 0 | 0 | 0 |
| P13 regular | 10–20 | ranged | 43045 | 2070 | 1187 | 1247 | 94 | 0 |
| P13 regular | 20–30 | guns | 8183 | 10202 | 2018 | 15 | 0 | 0 |
| P13 regular | 20–30 | ranged | 0 | 0 | 0 | 0 | 0 | 0 |
| P13 regular | 30–60 | guns | 493 | 2237 | 32 | 0 | 0 | 0 |
| P13 regular | 30–60 | ranged | 0 | 0 | 0 | 0 | 0 | 0 |
| P13 regular | 60–150.1 | guns | 0 | 69 | 0 | 0 | 0 | 0 |
| P13 regular | 60–150.1 | ranged | 0 | 0 | 0 | 0 | 0 | 0 |
| P11 novice | 0–10 | guns | 495 | 32 | 0 | 0 | 112 | 0 |
| P11 novice | 0–10 | ranged | 60 | 136 | 0 | 0 | 40 | 0 |
| P11 novice | 10–20 | guns | 2743 | 8894 | 624 | 15 | 1712 | 0 |
| P11 novice | 10–20 | ranged | 0 | 6888 | 0 | 0 | 360 | 0 |
| P11 novice | 20–30 | guns | 0 | 1075 | 0 | 0 | 0 | 0 |
| P11 novice | 20–30 | ranged | 0 | 5152 | 0 | 0 | 120 | 0 |
| P11 novice | 30–60 | guns | 0 | 56 | 0 | 0 | 0 | 0 |
| P11 novice | 30–60 | ranged | 0 | 48 | 0 | 0 | 0 | 0 |
| P11 novice | 60–150.1 | guns | 0 | 0 | 0 | 0 | 0 | 0 |
| P11 novice | 60–150.1 | ranged | 0 | 0 | 0 | 0 | 0 | 0 |
| P12 novice | 0–10 | guns | 0 | 0 | 0 | 0 | 0 | 0 |
| P12 novice | 0–10 | ranged | 11624 | 224 | 0 | 0 | 0 | 0 |
| P12 novice | 10–20 | guns | 210 | 1776 | 208 | 60 | 0 | 0 |
| P12 novice | 10–20 | ranged | 21465 | 10900 | 1242 | 650 | 166 | 0 |
| P12 novice | 20–30 | guns | 0 | 1720 | 0 | 0 | 0 | 0 |
| P12 novice | 20–30 | ranged | 0 | 1307 | 0 | 0 | 40 | 0 |
| P12 novice | 30–60 | guns | 0 | 94 | 0 | 0 | 0 | 0 |
| P12 novice | 30–60 | ranged | 0 | 8 | 0 | 0 | 0 | 0 |
| P12 novice | 60–150.1 | guns | 0 | 0 | 0 | 0 | 0 | 0 |
| P12 novice | 60–150.1 | ranged | 0 | 0 | 0 | 0 | 0 | 0 |
| P13 novice | 0–10 | guns | 90 | 16 | 0 | 0 | 0 | 0 |
| P13 novice | 0–10 | ranged | 27622 | 665 | 415 | 1083 | 64 | 0 |
| P13 novice | 10–20 | guns | 15 | 2160 | 144 | 105 | 8 | 0 |
| P13 novice | 10–20 | ranged | 18120 | 3988 | 836 | 1334 | 134 | 0 |
| P13 novice | 20–30 | guns | 0 | 2199 | 0 | 0 | 0 | 0 |
| P13 novice | 20–30 | ranged | 0 | 298 | 0 | 0 | 0 | 0 |
| P13 novice | 30–60 | guns | 0 | 48 | 0 | 0 | 0 | 0 |
| P13 novice | 30–60 | ranged | 0 | 16 | 0 | 0 | 0 | 0 |
| P13 novice | 60–150.1 | guns | 0 | 0 | 0 | 0 | 0 | 0 |
| P13 novice | 60–150.1 | ranged | 0 | 0 | 0 | 0 | 0 | 0 |

Regular gun HP lost at 10–20 s to enemy ranged falls 4,733 → 1,575/3,311 (P11/P12/P13); at 20–30 s it rises 8,480 → 9,406/10,202. Full-fight enemy artillery damage to guns is 18,685/18,643/16,785: P12 barely changes that total. Full-fight ranged damage to guns is 14,838/13,178/15,819; P13 actually raises it. P12 removes 1,496 HP of friendly ranged damage to guns, while enemy melee damage rises 976 → 2,366.

Own ranged killers (pooled, exact last hits):

| Cell | Enemy artillery | Enemy ranged | Enemy melee | Friendly artillery | Friendly ranged |
|---|---|---|---|---|---|
| P11 regular | 222 | 249 | 0 | 0 | 1 |
| P12 regular | 528 | 59 | 8 | 2 | 3 |
| P13 regular | 453 | 73 | 22 | 49 | 3 |
| P11 novice | 0 | 0 | 0 | 0 | 0 |
| P12 novice | 225 | 163 | 20 | 7 | 3 |
| P13 novice | 416 | 93 | 29 | 33 | 4 |

Regular P12 ranged lose 51,750 HP to enemy artillery in 10–20 s, out of 55,200 initial ranged HP across the panel; only 535 eligible ranged unit-ticks remain in 20–30 s. P13 loses 7,485 artillery HP before 10 s and 43,045 during 10–20 s, and has no eligible ranged unit-ticks in 20–30 s. The whole-phase arrival percentages (36.69%/6.94%) therefore mix approach and rapid destruction; they are not the fraction of units that ever arrived or a sustained defensive line.

## 4. Absorption, splash and body-blocking

Shell attribution matches each positive artillery damage event to exactly one launch by source and scheduled impact within one tick. No ambiguous match was accepted. These counts establish where shells were aimed and whom their splash actually damaged.

| Cell | Shell aimed at | Shells | HP to own ranged | Ranged victims/successful ranged-damaging shell | HP to own guns |
|---|---|---|---|---|---|
| P11 regular | artillery | 694 | 2560 | 1.48 | 8991 |
| P11 regular | ranged | 747 | 25414 | 2.81 | 3173 |
| P11 regular | melee | 968 | 0 | unavailable | 6521 |
| P12 regular | artillery | 752 | 0 | unavailable | 9497 |
| P12 regular | ranged | 487 | 32172 | 6.04 | 7930 |
| P12 regular | melee | 878 | 19879 | 4.83 | 1216 |
| P13 regular | artillery | 879 | 0 | unavailable | 11578 |
| P13 regular | ranged | 370 | 36778 | 7.61 | 4050 |
| P13 regular | melee | 928 | 13752 | 4.3 | 1157 |
| P11 novice | artillery | 148 | 0 | unavailable | 2578 |
| P11 novice | ranged | 0 | 0 | unavailable | 0 |
| P11 novice | melee | 917 | 60 | 1.33 | 660 |
| P12 novice | artillery | 0 | 0 | unavailable | 0 |
| P12 novice | ranged | 178 | 11237 | 4.72 | 210 |
| P12 novice | melee | 878 | 21852 | 3.09 | 0 |
| P13 novice | artillery | 0 | 0 | unavailable | 0 |
| P13 novice | ranged | 339 | 20315 | 4.95 | 30 |
| P13 novice | melee | 705 | 25427 | 4.38 | 75 |

This is absorption and splash exposure, not artillery body-blocking: shells are lobbed area attacks. In regular P12, 32,172 ranged HP comes from shells aimed at ranged and 19,879 from shells aimed at melee; no ranged HP comes from gun-targeted shells. Ranged-targeted shells also cost our guns 7,930 HP, against 3,173 in P11: the assigned-gun-centre clearance guarantee does not protect guns from shells aimed at nearby escorts. P12 ranged-targeted successful shells damage 6.04 ranged units each, P13 7.61 (P11 2.81). Shared escort points are a plausible source of this multiplicity.

Direct ranged body-blocking is not identifiable exactly: raw has no shot ordinals, release positions/directions or hit-to-shot mapping. A deliberately weak snapshot proxy counts enemy ranged damage to our ranged while the source’s current action selects a gun: 427/44/17 events, 3,325/288/104 HP in regular P11/P12/P13. Only 4/7/2 of those hits align geometrically between the impact-time source and current gun target, within the ranged body radius (30/44/9 HP). Current targeting and source position can differ from release-time values. Neither count is a prevented-shot count, and neither supports body-blocking as the main demonstrated explanation. Exact “would have reached our guns” remains unavailable without new instrumentation or a counterfactual run, neither performed here.

## 5. Why own ranged threat selection collapses

| Cell | Bin s | Eligible ranged ticks | Threat opportunities | Opportunities % eligible | Threat chosen % opportunities | Chosen melee | Chosen gun | Chosen ranged |
|---|---|---|---|---|---|---|---|---|
| P11 regular | 10–20 | 178370 | 29603 | 16.6 | 32.6 | 19760 | 191 | 9652 |
| P11 regular | 20–30 | 139161 | 37207 | 26.74 | 68.83 | 5942 | 321 | 30944 |
| P12 regular | 10–20 | 82034 | 69937 | 85.25 | 2.92 | 58966 | 8931 | 2040 |
| P12 regular | 20–30 | 535 | 522 | 97.57 | 8.62 | 72 | 405 | 45 |
| P13 regular | 10–20 | 41758 | 40814 | 97.74 | 0.59 | 27775 | 12779 | 260 |
| P13 regular | 20–30 | 0 | 0 | unavailable | unavailable | 0 | 0 | 0 |
| P11 novice | 10–20 | 93900 | 32705 | 34.83 | 45.96 | 17675 | 0 | 15030 |
| P11 novice | 20–30 | 0 | 0 | unavailable | unavailable | 0 | 0 | 0 |
| P12 novice | 10–20 | 67430 | 67430 | 100 | 16.66 | 34916 | 20334 | 12180 |
| P12 novice | 20–30 | 0 | 0 | unavailable | unavailable | 0 | 0 | 0 |
| P13 novice | 10–20 | 21683 | 21683 | 100 | 4.1 | 11166 | 9626 | 891 |
| P13 novice | 20–30 | 0 | 0 | unavailable | unavailable | 0 | 0 | 0 |

P12 resolves early geometric reach: during 10–20 s, a threat is reachable in 85.25% of eligible ranged ticks, against P11’s 16.60%. Yet it selects the threat in only 2.92% of those opportunities, mostly choosing melee (58,966) or guns (8,931). The all-phase selection figures are 53.58%/2.96%/0.54%; the denominator changes substantially between arms, so the within-window comparison is more informative.

Source inspection: `src/native/s4_v6_controller.cpp` selects among `v2Legal` enemies using group alignment plus tanh of engagement memory; it retains the old target unless the new score improves by at least 0.2. Movement is computed separately. `s4_escort_probe_v1/escort.cpp` replaces movement only. There is no “moving ⇒ no target” rule in v6. Native firing additionally requires reach, windup, a clear aim/lane, and other readiness checks. The traces establish a competing-target preference after repositioning, not which score term caused each rejection: per-enemy scores were not logged. Moving P12 opportunity ticks still select threats (2,009/66,578 at 10–20 s). Movement does not explain selection collapse by itself, although it can change legal sets, memory, physical lanes and release readiness.

## 6. How the 11 wins differ from losses

These are outcome-conditioned associations within each arm, not causal estimates. Survival curves are reconstructed from exact deaths at t≤sample; terminal survivors are held after the fight ends, not treated as continuing simulated survival. The 30-second table uses ≤30 for curves, while early-last-hit endpoints below use strict <20/<30 as declared.

| Arm | Outcome | n | Own guns 20s | Own guns 30s | Own guns 60s | Own gun HP 30s/fight | Enemy guns dead 30s | Enemy ranged alive 30s | Own artillery→ranged kills <20s/fight |
|---|---|---|---|---|---|---|---|---|---|
| P11 | win | 1 | 9 | 4 | 2 | 342 | 8 | 10 | 10 |
| P11 | nonwin | 19 | 8.11 | 1.37 | 0 | 103.32 | 6.32 | 21.16 | 5.89 |
| P12 | win | 6 | 10 | 5.83 | 4.17 | 504.5 | 9.33 | 11.5 | 14.5 |
| P12 | nonwin | 14 | 9.21 | 1.86 | 0 | 124.07 | 7.07 | 18.07 | 10.71 |
| P13 | win | 5 | 9.8 | 4.4 | 2.8 | 430 | 9.2 | 13.6 | 15 |
| P13 | nonwin | 15 | 9.33 | 1.73 | 0.07 | 128.27 | 6.93 | 19.27 | 10.13 |

Every P12/P13 win has zero own ranged survivors: guns finish the fight after the escort cohort is destroyed. At 30 s P12 wins retain 5.83 guns versus 1.86 in losses, P13 4.4 versus 1.73; enemy guns dead are 9.33 versus 7.07 and 9.2 versus 6.93. The enemy ranged screen is also smaller in wins. Own artillery, rather than escorts, removes it early.

| Regular arm | Own artillery ranged last hits <20s: shell aimed gun | Aimed ranged | Aimed melee |
|---|---|---|---|
| P11 | 118 | 1 | 3 |
| P12 | 230 | 6 | 1 |
| P13 | 223 | 4 | 0 |

Early screen kills by our artillery increase 122 → 237/227. Of those, 118/230/223 are incidental victims of shells aimed at enemy guns. This is stronger evidence for a battery/splash mechanism than for successful escort engagement. The traces do not isolate whether changed enemy screen geometry or increased effective battery fire caused the extra collateral kills. Mean own gun launches <30 s are 130.8/140.5/140.6.

The full 0/10/15/20/25/30/45/60/90/150 s gun-survival and gun-HP curves, enemy-gun deaths, enemy-ranged survival, per-fight outcomes and paired-cluster contrasts are in JSON. Ten clusters, not twenty independent orientations or forty independent intervention outcomes, are the sampling units for future uncertainty calculations.

## 7. Why novice costs rise and smallest next single changes on P12

Novice P11 exposes virtually no own ranged to enemy artillery (60 HP and zero artillery last hits). P12/P13 expose them to 33,089/45,742 artillery HP and 225/416 artillery last hits. Much is collateral from shells aimed at melee (21,852/25,427 HP); enemy ranged-targeted shells add 11,237/20,315 HP. P13 is hit sooner: 27,622 artillery HP before 10 s, versus P12’s 11,624. In novice P12, 334/418 ranged deaths occur while both sides have guns alive at prepare; in P13 it is 554/575. Waiting for enemy guns to die is therefore too late to prevent most of these deaths.

Each row below is a separate scripted hypothesis on top of P12. No rule is implemented or run. Constants stated here are prospective choices, not calibrated optima. Test one change at a time on freshly declared development entropy.

| Priority | One rule | Evidence and expected trade-off |
|---|---|---|
| 1 | While P12 escort phase is active, if any geometrically reachable enemy ranged threatens any living own gun, replace the ranged target with the nearest such enemy (ties lowest id); otherwise retain v6 target. | Reach exists but targets prefer melee/guns. May remove the late gun threat; reduces melee/gun focus and does not solve enemy artillery exposure or blocked fire lanes. |
| 2 | While P12 escort phase is active, add to each ranged goal the simultaneous id-ordered sum (58 − current centre distance) times the unit vector away from each other living own ranged closer than 58 px (splash 40 + two ranged radii 18); use P11’s ±x id convention at coincidence, native-clip, then recompute multiplier=1 iff final goal error>2 px, otherwise0, with stop0. | Successful escort-targeted shells hit 6.04 ranged each; multiple escorts share a point. May reduce splash losses; can weaken shielding, disrupt arrival and move units outside reach. 58 only addresses a centred landing and is no global safety guarantee. |
| 3 | In the P12 gun post rule, use the furthest legal focus radius (range = 320 px) instead of range minus the existing 12 px margin, retaining targeting and P11 repulsion. | Enemy ranged remains the late gun threat; a 12 px retreat may reduce screen reach. Trades range margin for exposure reduction; movement/spacing/aim changes can push shots out of range, and a 52–59 px screen offset still makes full exclusion unlikely. |

Do not propose “withdraw escorts once enemy guns are dead” as a new rule: P12 already falls through to complete v6 movement and targeting when either side has no guns (19.8.1 R2 and `escort.cpp`). It would be a no-op. Earlier withdrawal or low-HP withdrawal is a different hypothesis, but the current analysis supplies no uniquely supported threshold. P13’s worse arrival, earlier exposure and higher novice cost give no reason to move the escort further forward again.

## 8. Review and reproducibility

Run the two observation-only scripts `s4_escort_mechanism_v1/analyze.py` and `shell_attribution.py`, then `render.py`; raw stays in the original gitignored local directory. No source, rule, sealed entropy, PLAN_CURRENT, DESIGN_0G or committed receipt was edited. This report is separate from the original sealed reading. Part 2’s verbatim owner recheck and dispositions are recorded in `s4_escort_mechanism_v1/OWNER_RECHECK.md`; the plan is excluded by the owner. Claude CLI returned “Not logged in”, so the separate reviewer pass is explicitly a Codex same-family fallback, not cross-family acceptance. Delivery identity is in the local `DELIVERY_TRANSPORT.json` sidecar.
