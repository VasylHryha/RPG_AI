#!/usr/bin/env python3
"""Render already computed stored-data summaries. No raw parse or combat."""
import json
from analyze import HERE,sha
D=json.loads((HERE/'COMPACT.json').read_text());S=json.loads((HERE/'SHELL_ATTRIBUTION.json').read_text())
C={(c['arm'],c['head']):c for c in D['cells']};SC={(c['arm'],c['head']):c for c in S['cells']}
out=[]
def p(s=''):out.append(s)
def table(headers,rows):
 p('| '+' | '.join(headers)+' |');p('|'+'|'.join(['---']*len(headers))+'|')
 for row in rows:p('| '+' | '.join(str(x) for x in row)+' |')
 p()
def summ(c,field,value,**filters):return sum(r[value] for r in c[field] if all(r.get(k)==v for k,v in filters.items()))
def n(x):return f'{x:.2f}'.rstrip('0').rstrip('.')
def pct(a,b):return n(100*a/b) if b else 'unavailable'
p('PARTIAL');p();p('# Escort mechanism diagnostic: temporary protection through sacrificial exposure');p()
p('Reviewed run: `0f8e823077d83bca76a66532a1988d2ec7c9052a`. Stored traces only: P11/P12/P13 × regular/novice, 20 fights per cell, 10 paired clusters with two orientations. No fights, simulations, tuning or registration. All 620 entries in `s4_escort_probe_v1/RAW_FILES_LOCAL.json` matched bytes and SHA256 before parsing (866,788,710 bytes). Damage, deaths, targets, artillery launches and shell attribution are complete. PARTIAL applies to exact direct-shot interception and causal counterfactuals, which these traces cannot identify. All numbers below derive from adjacent `s4_escort_mechanism_v1/COMPACT.json`, `PER_FIGHT.json` and `SHELL_ATTRIBUTION.json`.')
p();p('The supported explanation is a brief protection window bought by exposing and clustering our ranged units. Enemy fire toward our guns falls early, those guns survive longer, and our counter-battery shells kill more of the enemy ranged screen incidentally. The escorts themselves almost never kill that screen. This is a mechanism consistent with the traces; position alone was varied, so these observations do not isolate diversion, collision effects and collateral geometry into independent causal effects.');p()
p('## 1. P11 control first and cost accounting');p()
rows=[]
for head in ('regular','novice'):
 for arm in ('P11','P12','P13'):
  c=C[arm,head];dead=sum(c['own_ranged_killers'].values())/20;guns=10-c['curves'][-1]['own_guns_alive'];melee=c['mean_own_losses']-dead-guns
  rows.append([arm+' '+head,c['wins'],n(c['mean_S']),n(c['mean_own_losses']),n(guns),n(dead),n(melee)])
table(['Cell','Elimination wins /20','Mean S','Own losses/fight','Gun losses/fight','Ranged losses/fight','Melee losses/fight'],rows)
p('Against novice, the increase from 11.25 to 30.95/38.75 losses is entirely explained by ranged losses (0 → 20.9/28.75), partly offset by gun savings (1.25 → 0.05/0.15) and P13’s small melee saving (10 → 9.85). Every arm still eliminates novice 20/20. Against regular, all 600 ranged units die in P12 and P13; P11 loses 472/600. The 11 escort wins are genuine but neither arm meets the owner’s >50% criterion. See the separate run review for the declared 19.8.1 readings and the 11 terminal identities.');p()
p('## 2. What the enemy selects and shoots, over time');p()
p('Enemy artillery counts below are exact launch events. Enemy ranged “releases” are a lower bound inferred from a living unit’s preparation resetting from positive to zero with Direct/DodgeFire and a selected target. Same-step deceased shooters are unavailable; these are not exact projectile-launch receipts. Exact selected-target tick tables, including no target, are in COMPACT JSON. P11 ranged units are the comparison cohort; only P12/P13 are escorts.');p()
rows=[]
for head in ('regular','novice'):
 for arm in ('P11','P12','P13'):
  c=C[arm,head]
  for b,label in [(0,'0–10'),(1,'10–20'),(2,'20–30'),(3,'30–60'),(4,'60–150.1')]:
   r=[arm+' '+head,label]
   for field,value,source in [('shell_launches','launches','enemy'),('direct_releases_inferred','releases','enemy')]:
    r.append('/'.join(str(summ(c,field,value,bin=b,source=source,target='own_'+role)) for role in ('artillery','ranged','melee')))
   rows.append(r)
table(['Cell','Bin s','Enemy shells → guns/ranged/melee','Enemy ranged inferred releases → guns/ranged/melee'],rows)
p('Regular 10–20 s: artillery launches aimed at our guns fall 310 → 106/256; inferred enemy ranged releases aimed at guns fall 1,477 → 470/876. Enemy shells aimed at escorts increase 131 → 462/295. Once escorts die, gun-targeted artillery launches rise during 20–30 s (344 → 600/584), and ranged releases aimed at guns rise (1,366 → 1,779/1,856). Thus the initial protection is temporary, not a reduction of every full-fight threat.');p()
p('## 3. Actual HP lost, with capped damage and friendly sources');p()
p('Each row is pooled HP from 20 fights. Event bins are literal [0,10), [10,20), [20,30), [30,60), [60,150.1); HP conservation was independently asserted for every one of the 12,000 initial units. Zero means no damage, not an unavailable observation. Full melee-cohort and opposing-cohort breakdowns remain in JSON.');p()
rows=[]
for head in ('regular','novice'):
 for arm in ('P11','P12','P13'):
  c=C[arm,head]
  for b,label in enumerate(['0–10','10–20','20–30','30–60','60–150.1']):
   for target,name in [('own_artillery','guns'),('own_ranged','ranged')]:
    r=[arm+' '+head,label,name]
    for src in ('opposing_artillery','opposing_ranged','opposing_melee','friendly_artillery','friendly_ranged','friendly_melee'):r.append(summ(c,'damage','hp',bin=b,target=target,source=src))
    rows.append(r)
table(['Cell','Bin s','Victim','Enemy artillery HP','Enemy ranged HP','Enemy melee HP','Friendly artillery HP','Friendly ranged HP','Friendly melee HP'],rows)
p('Regular gun HP lost at 10–20 s to enemy ranged falls 4,733 → 1,575/3,311 (P11/P12/P13); at 20–30 s it rises 8,480 → 9,406/10,202. Full-fight enemy artillery damage to guns is 18,685/18,643/16,785: P12 barely changes that total. Full-fight ranged damage to guns is 14,838/13,178/15,819; P13 actually raises it. P12 removes 1,496 HP of friendly ranged damage to guns, while enemy melee damage rises 976 → 2,366.');p()
p('Own ranged killers (pooled, exact last hits):');p()
table(['Cell','Enemy artillery','Enemy ranged','Enemy melee','Friendly artillery','Friendly ranged'],[[arm+' '+head,*[C[arm,head]['own_ranged_killers'].get(k,0) for k in ('enemy_artillery','enemy_ranged','enemy_melee','friendly_artillery','friendly_ranged')]] for head in ('regular','novice') for arm in ('P11','P12','P13')])
p('Regular P12 ranged lose 51,750 HP to enemy artillery in 10–20 s, out of 55,200 initial ranged HP across the panel; only 535 eligible ranged unit-ticks remain in 20–30 s. P13 loses 7,485 artillery HP before 10 s and 43,045 during 10–20 s, and has no eligible ranged unit-ticks in 20–30 s. The whole-phase arrival percentages (36.69%/6.94%) therefore mix approach and rapid destruction; they are not the fraction of units that ever arrived or a sustained defensive line.');p()
p('## 4. Absorption, splash and body-blocking');p()
p('Shell attribution matches each positive artillery damage event to exactly one launch by source and scheduled impact within one tick. No ambiguous match was accepted. These counts establish where shells were aimed and whom their splash actually damaged.');p()
rows=[]
for head in ('regular','novice'):
 for arm in ('P11','P12','P13'):
  c=SC[arm,head]
  for aim in ('own_artillery','own_ranged','own_melee'):
   hp=summ(c,'shells','value',source='enemy',aim=aim,metric='hp_to_own_ranged');vict=summ(c,'shells','value',source='enemy',aim=aim,metric='victims_own_ranged');succ=summ(c,'shells','value',source='enemy',aim=aim,metric='successful_on_own_ranged')
   rows.append([arm+' '+head,aim.removeprefix('own_'),summ(c,'shells','value',source='enemy',aim=aim,metric='shells'),hp,n(vict/succ) if succ else 'unavailable',summ(c,'shells','value',source='enemy',aim=aim,metric='hp_to_own_artillery')])
table(['Cell','Shell aimed at','Shells','HP to own ranged','Ranged victims/successful ranged-damaging shell','HP to own guns'],rows)
p('This is absorption and splash exposure, not artillery body-blocking: shells are lobbed area attacks. In regular P12, 32,172 ranged HP comes from shells aimed at ranged and 19,879 from shells aimed at melee; no ranged HP comes from gun-targeted shells. Ranged-targeted shells also cost our guns 7,930 HP, against 3,173 in P11: the assigned-gun-centre clearance guarantee does not protect guns from shells aimed at nearby escorts. P12 ranged-targeted successful shells damage 6.04 ranged units each, P13 7.61 (P11 2.81). Shared escort points are a plausible source of this multiplicity.');p()
p('Direct ranged body-blocking is not identifiable exactly: raw has no shot ordinals, release positions/directions or hit-to-shot mapping. A deliberately weak snapshot proxy counts enemy ranged damage to our ranged while the source’s current action selects a gun: 427/44/17 events, 3,325/288/104 HP in regular P11/P12/P13. Only 4/7/2 of those hits align geometrically between the impact-time source and current gun target, within the ranged body radius (30/44/9 HP). Current targeting and source position can differ from release-time values. Neither count is a prevented-shot count, and neither supports body-blocking as the main demonstrated explanation. Exact “would have reached our guns” remains unavailable without new instrumentation or a counterfactual run, neither performed here.');p()
p('## 5. Why own ranged threat selection collapses');p()
rows=[]
for head in ('regular','novice'):
 for arm in ('P11','P12','P13'):
  c=C[arm,head]
  for b,label in [(1,'10–20'),(2,'20–30')]:
   count=lambda k:summ(c,'selection','ticks',bin=b,metric=k)
   rows.append([arm+' '+head,label,count('eligible'),count('opportunity'),pct(count('opportunity'),count('eligible')),pct(count('selected_threat'),count('opportunity')),count('selected_melee'),count('selected_artillery'),count('selected_ranged')])
table(['Cell','Bin s','Eligible ranged ticks','Threat opportunities','Opportunities % eligible','Threat chosen % opportunities','Chosen melee','Chosen gun','Chosen ranged'],rows)
p('P12 resolves early geometric reach: during 10–20 s, a threat is reachable in 85.25% of eligible ranged ticks, against P11’s 16.60%. Yet it selects the threat in only 2.92% of those opportunities, mostly choosing melee (58,966) or guns (8,931). The all-phase selection figures are 53.58%/2.96%/0.54%; the denominator changes substantially between arms, so the within-window comparison is more informative.');p()
p('Source inspection: `src/native/s4_v6_controller.cpp` selects among `v2Legal` enemies using group alignment plus tanh of engagement memory; it retains the old target unless the new score improves by at least 0.2. Movement is computed separately. `s4_escort_probe_v1/escort.cpp` replaces movement only. There is no “moving ⇒ no target” rule in v6. Native firing additionally requires reach, windup, a clear aim/lane, and other readiness checks. The traces establish a competing-target preference after repositioning, not which score term caused each rejection: per-enemy scores were not logged. Moving P12 opportunity ticks still select threats (2,009/66,578 at 10–20 s). Movement does not explain selection collapse by itself, although it can change legal sets, memory, physical lanes and release readiness.');p()
p('## 6. How the 11 wins differ from losses');p()
p('These are outcome-conditioned associations within each arm, not causal estimates. Survival curves are reconstructed from exact deaths at t≤sample; terminal survivors are held after the fight ends, not treated as continuing simulated survival. The 30-second table uses ≤30 for curves, while early-last-hit endpoints below use strict <20/<30 as declared.');p()
rows=[]
for c in D['regular_outcomes']:
 at={r['t']:r for r in c['curves']};r30=at[30]
 rows.append([c['arm'],c['outcome'],c['n'],n(at[20]['own_guns_alive']),n(r30['own_guns_alive']),n(at[60]['own_guns_alive']),n(r30['own_gun_hp_remaining']),n(r30['enemy_guns_dead']),n(r30['enemy_ranged_alive']),n(summ(c,'early_enemy_ranged_kills','kills',before=20,source='artillery')/c['n'])])
table(['Arm','Outcome','n','Own guns 20s','Own guns 30s','Own guns 60s','Own gun HP 30s/fight','Enemy guns dead 30s','Enemy ranged alive 30s','Own artillery→ranged kills <20s/fight'],rows)
p('Every P12/P13 win has zero own ranged survivors: guns finish the fight after the escort cohort is destroyed. At 30 s P12 wins retain 5.83 guns versus 1.86 in losses, P13 4.4 versus 1.73; enemy guns dead are 9.33 versus 7.07 and 9.2 versus 6.93. The enemy ranged screen is also smaller in wins. Own artillery, rather than escorts, removes it early.');p()
rows=[]
for arm in ('P11','P12','P13'):
 c=SC[arm,'regular'];rows.append([arm,*[summ(c,'early_enemy_ranged_artillery_last_hits','kills',before=20,aim='enemy_'+role) for role in ('artillery','ranged','melee')]])
table(['Regular arm','Own artillery ranged last hits <20s: shell aimed gun','Aimed ranged','Aimed melee'],rows)
p('Early screen kills by our artillery increase 122 → 237/227. Of those, 118/230/223 are incidental victims of shells aimed at enemy guns. This is stronger evidence for a battery/splash mechanism than for successful escort engagement. The traces do not isolate whether changed enemy screen geometry or increased effective battery fire caused the extra collateral kills. Mean own gun launches <30 s are '+ '/'.join(n(C[a,'regular']['mean_own_gun_launches_before30']) for a in ('P11','P12','P13'))+'.');p()
p('The full 0/10/15/20/25/30/45/60/90/150 s gun-survival and gun-HP curves, enemy-gun deaths, enemy-ranged survival, per-fight outcomes and paired-cluster contrasts are in JSON. Ten clusters, not twenty independent orientations or forty independent intervention outcomes, are the sampling units for future uncertainty calculations.');p()
p('## 7. Why novice costs rise and smallest next single changes on P12');p()
p('Novice P11 exposes virtually no own ranged to enemy artillery (60 HP and zero artillery last hits). P12/P13 expose them to 33,089/45,742 artillery HP and 225/416 artillery last hits. Much is collateral from shells aimed at melee (21,852/25,427 HP); enemy ranged-targeted shells add 11,237/20,315 HP. P13 is hit sooner: 27,622 artillery HP before 10 s, versus P12’s 11,624. In novice P12, 334/418 ranged deaths occur while both sides have guns alive at prepare; in P13 it is 554/575. Waiting for enemy guns to die is therefore too late to prevent most of these deaths.');p()
p('Each row below is a separate scripted hypothesis on top of P12. No rule is implemented or run. Constants stated here are prospective choices, not calibrated optima. Test one change at a time on freshly declared development entropy.');p()
table(['Priority','One rule','Evidence and expected trade-off'],[
 ['1','While P12 escort phase is active, if any geometrically reachable enemy ranged threatens any living own gun, replace the ranged target with the nearest such enemy (ties lowest id); otherwise retain v6 target.','Reach exists but targets prefer melee/guns. May remove the late gun threat; reduces melee/gun focus and does not solve enemy artillery exposure or blocked fire lanes.'],
 ['2','While P12 escort phase is active, add to each ranged goal the simultaneous id-ordered sum (58 − current centre distance) times the unit vector away from each other living own ranged closer than 58 px (splash 40 + two ranged radii 18); use P11’s ±x id convention at coincidence, native-clip, then recompute multiplier=1 iff final goal error>2 px, otherwise0, with stop0.','Successful escort-targeted shells hit 6.04 ranged each; multiple escorts share a point. May reduce splash losses; can weaken shielding, disrupt arrival and move units outside reach. 58 only addresses a centred landing and is no global safety guarantee.'],
 ['3','In the P12 gun post rule, use the furthest legal focus radius (range = 320 px) instead of range minus the existing 12 px margin, retaining targeting and P11 repulsion.','Enemy ranged remains the late gun threat; a 12 px retreat may reduce screen reach. Trades range margin for exposure reduction; movement/spacing/aim changes can push shots out of range, and a 52–59 px screen offset still makes full exclusion unlikely.']])
p('Do not propose “withdraw escorts once enemy guns are dead” as a new rule: P12 already falls through to complete v6 movement and targeting when either side has no guns (19.8.1 R2 and `escort.cpp`). It would be a no-op. Earlier withdrawal or low-HP withdrawal is a different hypothesis, but the current analysis supplies no uniquely supported threshold. P13’s worse arrival, earlier exposure and higher novice cost give no reason to move the escort further forward again.');p()
p('## 8. Review and reproducibility');p()
p('Run the two observation-only scripts `s4_escort_mechanism_v1/analyze.py` and `shell_attribution.py`, then `render.py`; raw stays in the original gitignored local directory. No source, rule, sealed entropy, PLAN_CURRENT, DESIGN_0G or committed receipt was edited. This report is separate from the original sealed reading. Part 2’s verbatim owner recheck and dispositions are recorded in `s4_escort_mechanism_v1/OWNER_RECHECK.md`; the plan is excluded by the owner. Claude CLI returned “Not logged in”, so the separate reviewer pass is explicitly a Codex same-family fallback, not cross-family acceptance. Delivery identity is in the local `DELIVERY_TRANSPORT.json` sidecar.');p()
(HERE.parent/'S4_ESCORT_MECHANISM_DIAGNOSTIC.md').write_text('\n'.join(out).rstrip()+'\n')
