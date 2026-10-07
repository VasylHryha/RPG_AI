"""Render stored diagnostic JSON only; no simulation or project imports."""
import collections
import hashlib
import json
import pathlib
import statistics

HERE = pathlib.Path(__file__).resolve().parent
CPP = HERE.parent


def counter(rows, key):
    return sum((collections.Counter(r[key]) for r in rows), collections.Counter())


def pct(n, d):
    return 100*n/d if d else None


def damage(rows):
    bins = [sum((collections.Counter(r['damage_bins'][i]) for r in rows), collections.Counter()) for i in range(5)]
    incoming = [{k: v for k, v in b.items() if k.startswith(('0_', '1_'))} for b in bins]
    result, cumulative = [], collections.Counter()
    for i, b in enumerate(incoming):
        cumulative.update(b)
        total = sum(b.values())
        running = sum(cumulative.values())
        result.append(dict(bin=i, hp=dict(b), total_hp=total,
                           ranged_share_pct=pct(b.get('1_ranged', 0), total),
                           artillery_share_pct=pct(b.get('1_artillery', 0), total),
                           cumulative_total_hp=running,
                           cumulative_ranged_share_pct=pct(cumulative['1_ranged'], running),
                           cumulative_artillery_share_pct=pct(cumulative['1_artillery'], running)))
    return result


def profile(rows):
    own_kills = [e for r in rows for e in r['enemy_ranged_deaths'] if e['source_team'] == 0]
    friendly = [e for r in rows for e in r['enemy_ranged_deaths'] if e['source_team'] == 1]
    ac = counter(rows, 'commit_action_counts')
    gc = counter(rows, 'geometry_counts')
    out = dict(n=len(rows), mean_enemy_guns_destroyed=statistics.mean(r['enemy_guns_destroyed'] for r in rows),
               mean_own_guns_lost=statistics.mean(r['own_guns_lost'] for r in rows),
               mean_first_reach_s=statistics.mean(r['first_enemy_ranged_reach_s'] for r in rows),
               mean_first_gun_damage_s=statistics.mean(r['first_enemy_ranged_gun_damage_s'] for r in rows),
               mean_enemy_guns_dead_by_20=statistics.mean(sum(t < 20 for t in r['enemy_gun_death_times_s']) for r in rows),
               mean_enemy_guns_dead_by_30=statistics.mean(sum(t < 30 for t in r['enemy_gun_death_times_s']) for r in rows),
               mean_own_guns_dead_by_20=statistics.mean(sum(t < 20 for t in r['own_gun_death_times_s']) for r in rows),
               mean_own_guns_dead_by_30=statistics.mean(sum(t < 30 for t in r['own_gun_death_times_s']) for r in rows),
               own_kills_by_role=dict(collections.Counter(e['source_role'] for e in own_kills)),
               enemy_friendly_ranged_deaths=len(friendly),
               own_kills_before_20_by_role=dict(collections.Counter(e['source_role'] for e in own_kills if e['t'] < 20)),
               own_kills_before_30_by_role=dict(collections.Counter(e['source_role'] for e in own_kills if e['t'] < 30)),
               own_ranged_kill_times_s=[e['t'] for e in own_kills if e['source_role'] == 'ranged'],
               damage_bins=damage(rows), action_counts=dict(ac),
               ranged_threat_reachable_pct=pct(ac['ranged_threat_reachable_ticks'], ac['ranged_ticks']),
               ranged_threat_selected_when_reachable_pct=pct(ac['ranged_selects_reachable_threat_ticks'], ac['ranged_threat_reachable_ticks']),
               ranged_reachable_unselected_threat_pct=pct(ac['ranged_threat_reachable_ticks']-ac['ranged_selects_reachable_threat_ticks'], ac['ranged_ticks']),
               geometry_counts=dict(gc),
               early_guns_threatened_pct=pct(gc['early_10_20_own_gun_enemy_ranged_reach'], gc['early_10_20_own_gun_samples']),
               early_safe_in_gun_target_band_pct=pct(gc['early_10_20_own_gun_safe_and_gun_target_in_range'], gc['early_10_20_own_gun_samples']),
               early_enemy_ranged_in_front_pct=pct(gc['early_10_20_enemy_ranged_in_front'], gc['early_10_20_enemy_ranged_line_samples']),
               early_geometry_median_of_fight_medians={k: statistics.median(r['geometry'][k]['median'] for r in rows if k in r['geometry'])
                                                     for k in rows[0]['geometry'] if k.startswith('early_')})
    return out


def main():
    data = json.loads((HERE/'COMPACT.json').read_text())
    rows = data['fights']
    groups = {a: profile([r for r in rows if r['arm'] == a]) for a in ('P5', 'P10', 'P11')}
    groups['P11_wins'] = profile([r for r in rows if r['arm'] == 'P11' and r['elimination_win']])
    groups['P11_losses'] = profile([r for r in rows if r['arm'] == 'P11' and not r['elimination_win']])
    wins = [r for r in rows if r['arm'] == 'P11' and r['elimination_win']]
    pair_ids = {r['id'] for w in wins for r in rows if r['cluster'] == w['cluster'] and r['orientation'] == w['orientation']}
    individual = {r['id']: profile([r]) for r in rows if r['id'] in pair_ids}
    result = dict(groups=groups, paired_fights=individual, compact_sha256=hashlib.sha256((HERE/'COMPACT.json').read_bytes()).hexdigest(),
                  script_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest())
    (HERE/'DERIVED.json').write_text(json.dumps(result, separators=(',', ':'), allow_nan=False)+'\n')
    text = '''DONE

Stored-data diagnostic of P10/P11 regular, with P5 regular as contrast: 60 fights, 10 paired clusters per arm, reviewed run a13b51cfe7525fd5951e94e73bdae73f2692c597. No fights, simulations, combat tests, or process inspection were executed. All 370 local raw files were size/SHA256 verified before any trace was parsed. The same parser independently reconciled all 120 original probe measurements, including novice sanity cells. Original receipts and raw bytes remain unchanged.

Enemy ranged units are the largest source of **gun last hits** after spacing, but artillery remains the larger source of **total gun HP loss** across the full P10 and P11 panels. Their ranged screen reaches our battery early; our ranged support is usually too far away to contest that screen, and our melee attacks the enemy melee. This supports testing positioning/engagement timing alongside a narrow targeting change. It does not identify a proven cause of the two wins.

Distances below are centres in px. Native ranged-to-gun reach is 259+9+10=278 px; ranged-to-ranged reach is 277 px, melee-to-ranged reach is 36+16+9=61 px. Artillery reach is a centre band [0,320] px here. Geometric reach does not establish line clearance, windup, readiness, or an actual shot. Exact damage events and their times are distinguished from post-step snapshot geometry. Damage-event source/victim distance is measured at impact, not release; it may exceed firing reach after movement and projectile travel.

Geometry uses every 30th tick while both sides have living guns, pooling living unit-snapshots equally; whole-scope results have survival/cohort bias. The early window is literal raw time [10,20), without rounding (floating accumulation means samples are nominal seconds 11–19). “Front” means positive signed projection from the enemy gun centroid toward the own gun centroid, using a perpendicular plane through that centroid; it is a relative gun-front convention, not a fitted line-normal or every-gun guarantee. Singleton batteries are allowed. For action analysis, the inherited gun phase means enemy guns and own guns alive in the **prepare** snapshot; it does not mean every gun actually reached its commitment post. Commanded movement is not measured displacement. Target shares count selected action targets, not shots or damage.

| Early [10,20) s geometry (pooled median; p10–p90) | P5 | P10 | P11 |
|---|---|---|---|
'''
    geometry_fields = [('Enemy ranged → nearest enemy gun', 'enemy_ranged_to_enemy_gun'),
                       ('Enemy ranged → nearest own gun', 'enemy_ranged_to_own_gun'),
                       ('Enemy ranged signed forward offset', 'enemy_ranged_forward_offset'),
                       ('Own ranged → nearest own gun', 'own_ranged_to_own_gun'),
                       ('Own ranged → nearest enemy ranged', 'own_ranged_to_enemy_ranged'),
                       ('Own melee → nearest own gun', 'own_melee_to_own_gun'),
                       ('Own melee → nearest enemy ranged', 'own_melee_to_enemy_ranged')]
    for label, key in geometry_fields:
        values = [c['geometry']['early_10_20_'+key] for c in data['cells']]
        text += '|'+label+'|'+'|'.join(f"{v['median']:.1f} ({v['p10']:.1f}–{v['p90']:.1f})" for v in values)+'|\n'
    for label, key in [('Enemy ranged in front of enemy gun centroid plane', 'early_enemy_ranged_in_front_pct'),
                       ('Own gun snapshots in enemy ranged reach', 'early_guns_threatened_pct'),
                       ('Own gun snapshots safe from ranged AND selected gun target in band', 'early_safe_in_gun_target_band_pct')]:
        text += '|'+label+'|'+'|'.join(f"{groups[a][key]:.2f}%" for a in ('P5','P10','P11'))+'|\n'
    text += '\nAt this window, the enemy ranged screen is about 55–59 px from its own nearest gun and about 51–53 px forward of its battery centroid. P10/P11 own guns are nearer that screen than P5, despite the spacing reducing splash. The screen can reach almost all our gun snapshots, while median own-ranged distance to enemy ranged is 322–324 px, beyond 277 px reach. Own melee is closer to our guns but still about 157 px from enemy ranged, beyond its 61 px reach. Geometry sample counts, whole-scope distances and every first-reach unit identity are in COMPACT.json.\n\n'
    text += '| Timing (median across 20 fights; p10–p90), seconds | P5 | P10 | P11 |\n|---|---|---|---|\n'
    for label, key in [('First observed enemy ranged reach of any own gun', 'first_enemy_ranged_reach_s'),
                       ('First enemy ranged HP damage to an own gun', 'first_enemy_ranged_gun_damage_s')]:
        text += '|'+label+'|'+'|'.join(f"{c[key]['median']:.3f} ({c[key]['p10']:.3f}–{c[key]['p90']:.3f})" for c in data['cells'])+'|\n'
    text += '\nAll 20 fights in each arm have observed reach and ranged gun damage. First reach is the first recorded geometric-reach post-step snapshot (1/30 s cadence); native within-step entry, shot release and first damage can differ. Enemy ranged reaches the guns at about 9.6–9.8 s, with first HP loss about 11.5–11.8 s.\n\n'
    text += '| Arm / damage interval (s) | Enemy ranged HP (% all gun HP lost) | Enemy artillery HP (% all gun HP lost) | Other HP | Cumulative ranged / artillery shares |\n|---|---|---|---|---|\n'
    labels = ['[0,10)', '[10,20)', '[20,30)', '[30,60)', '[60,end]']
    for arm in ('P5','P10','P11'):
        for b in groups[arm]['damage_bins']:
            if not b['total_hp']:
                continue
            hp = b['hp']; other = b['total_hp']-hp.get('1_ranged',0)-hp.get('1_artillery',0)
            text += f"|{arm} {labels[b['bin']]}|{hp.get('1_ranged',0):g} ({b['ranged_share_pct']:.1f}%)|{hp.get('1_artillery',0):g} ({b['artillery_share_pct']:.1f}%)|{other:g}|{b['cumulative_ranged_share_pct']:.1f}% / {b['cumulative_artillery_share_pct']:.1f}%|\n"
        bins = groups[arm]['damage_bins']; totals = sum((collections.Counter(b['hp']) for b in bins), collections.Counter()); total = sum(totals.values())
        text += f"|{arm} full fight|{totals['1_ranged']:g} ({100*totals['1_ranged']/total:.1f}%)|{totals['1_artillery']:g} ({100*totals['1_artillery']/total:.1f}%)|{total-totals['1_ranged']-totals['1_artillery']:g}|same|\n"
    text += '\nDenominator: all actual own-gun HP lost in that interval, including enemy melee and friendly damage; lethal overkill is capped by dealt HP. P5/P10 lose 36,200 HP in total; P11 loses 36,170 (one gun ends with 30 HP). “Other” consists of P5 enemy melee 354 / friendly ranged 163; P10 enemy melee 632 / friendly ranged 1,553 / friendly artillery 81; P11 enemy melee 904 / friendly ranged 1,565 / friendly artillery 60. Per-fight HP conservation was checked against initial and terminal living gun HP. No gun damage is recorded before 10 s. After 20 s ranged becomes the larger interval damage source in both spacing arms; it is not the larger full-fight source.\n\n'
    text += '| Prepare gun-phase own ranged behavior (% living ranged action ticks) | P5 | P10 | P11 |\n|---|---|---|---|\n'
    for label, key in [('No selected target', 'ranged_target_none'), ('Enemy melee target','ranged_target_1_melee'),
                       ('Enemy ranged target','ranged_target_1_ranged'), ('Enemy gun target','ranged_target_1_artillery')]:
        text += '|'+label+'|'+'|'.join(f"{pct(groups[a]['action_counts'].get(key,0),groups[a]['action_counts']['ranged_ticks']):.2f}%" for a in ('P5','P10','P11'))+'|\n'
    text += '|Reachable enemy ranged that threatens an own gun|'+'|'.join(f"{groups[a]['ranged_threat_reachable_pct']:.2f}%" for a in ('P5','P10','P11'))+'|\n'
    text += '|Such a threat selected, conditional on reachable opportunity|'+'|'.join(f"{groups[a]['ranged_threat_selected_when_reachable_pct']:.2f}%" for a in ('P5','P10','P11'))+'|\n'
    text += '\nAll counted own direct-unit ticks carry a movement command; this does not establish actual movement or cancellation of firing. Own ranged mostly has no selected target or targets enemy melee. Own melee selects only enemy melee or no target, has zero geometrically reachable gun-threatening enemy-ranged opportunities, and records zero enemy-ranged last hits. The enemy ranged line is not being removed early by our direct screen.\n\n'
    text += '| Enemy ranged killed by OUR units (panel totals; 30 enemy ranged per fight) | P5 | P10 | P11 |\n|---|---|---|---|\n'
    for label, field, role in [('By ranged before 20 s','own_kills_before_20_by_role','ranged'), ('By ranged before 30 s','own_kills_before_30_by_role','ranged'),
                               ('By ranged full fight','own_kills_by_role','ranged'), ('By artillery before 20 s','own_kills_before_20_by_role','artillery'),
                               ('By artillery full fight','own_kills_by_role','artillery')]:
        text += '|'+label+'|'+'|'.join(str(groups[a][field].get(role,0)) for a in ('P5','P10','P11'))+'|\n'
    text += '\nThese are last hits, not exclusive damage contributions. Enemy friendly fire is separated: '+', '.join(a+' '+str(groups[a]['enemy_friendly_ranged_deaths']) for a in ('P5','P10','P11'))+'. Exact source/victim identities and times are retained in compact JSON. Full-fight counts include cleanup after gun losses; before-20/before-30 counts describe the protection window.\n\n'
    text += '| P11 outcome comparison (descriptive) | Two wins | Eighteen nonwins |\n|---|---|---|\n'
    for label, key in [('Mean enemy guns dead before 20 s','mean_enemy_guns_dead_by_20'), ('Mean enemy guns dead before 30 s','mean_enemy_guns_dead_by_30'),
                       ('Mean own guns dead before 20 s','mean_own_guns_dead_by_20'), ('Mean own guns dead before 30 s','mean_own_guns_dead_by_30'),
                       ('Mean final enemy guns destroyed','mean_enemy_guns_destroyed'), ('Mean final own guns lost','mean_own_guns_lost'),
                       ('Mean first ranged reach, s','mean_first_reach_s'), ('Mean first ranged damage, s','mean_first_gun_damage_s')]:
        text += '|'+label+'|'+'|'.join(f"{groups[g][key]:.3f}" for g in ('P11_wins','P11_losses'))+'|\n'
    for label, field, role in [('Mean OUR ranged enemy-ranged kills before 20 s','own_kills_before_20_by_role','ranged'),
                               ('Mean OUR artillery enemy-ranged kills before 20 s','own_kills_before_20_by_role','artillery')]:
        text += '|'+label+'|'+'|'.join(f"{groups[g][field].get(role,0)/groups[g]['n']:.3f}" for g in ('P11_wins','P11_losses'))+'|\n'
    text += '\nWin-group distance values are **medians of per-fight medians**, not pooled quantiles: own ranged → enemy ranged in the early window is '+f"{groups['P11_wins']['early_geometry_median_of_fight_medians']['early_10_20_own_ranged_to_enemy_ranged']:.1f}"+' px vs '+f"{groups['P11_losses']['early_geometry_median_of_fight_medians']['early_10_20_own_ranged_to_enemy_ranged']:.1f}"+' in nonwins. Neither win avoids the early threat or demonstrates an early ranged screen.\n\n'
    text += '| Paired cluster/orientation | Arm | Final enemy gun kills / own gun losses | Enemy guns dead <30 s | Own guns dead <30 s | OUR artillery/ranged enemy-ranged kills <20 s |\n|---|---|---|---|---|---|\n'
    for fid in sorted(individual):
        g = individual[fid]; r = next(x for x in rows if x['id'] == fid)
        text += f"|c{r['cluster']:02d}/o{r['orientation']}|{r['arm']}|{g['mean_enemy_guns_destroyed']:g}/{g['mean_own_guns_lost']:g}|{g['mean_enemy_guns_dead_by_30']:g}|{g['mean_own_guns_dead_by_30']:g}|{g['own_kills_before_20_by_role'].get('artillery',0)}/{g['own_kills_before_20_by_role'].get('ranged',0)}|\n"
    text += '''
c02/o0 wins at 69.600 s with 18 own survivors and one gun (30 HP). All enemy guns are dead at 32.367 s; nine own guns die by 47.367 s. Own gun HP loss is enemy artillery 781, enemy ranged 943, friendly own ranged 56. OUR artillery kills 28 enemy ranged; OUR ranged kills zero; two enemy ranged die to enemy friendly ranged fire. Ten artillery last hits on enemy ranged occur before 20 s. The surviving gun supplies late cleanup: its last enemy-ranged kill is at 69.600 s.

c09/o1 wins at 73.467 s with 11 own survivors and no own guns. All enemy guns are dead at 34.667 s and all own guns by 42.033 s. Own gun HP loss is enemy artillery 697, enemy ranged 886, enemy melee 75, friendly own ranged 152. OUR artillery kills 14 enemy ranged, OUR ranged 15, enemy friendly ranged one. Eleven artillery enemy-ranged last hits occur before 20 s; only one own-ranged kill occurs before 30 s (23.200 s). The other fourteen own-ranged kills occur from 50.900 to 73.467 s, after the battery is lost. This win relies on later ranged cleanup rather than an early protective ranged screen.

The two wins have faster/more complete early counter-battery kills and more early artillery last hits on enemy ranged than the nonwins. Enemy ranged reaches the battery at essentially the same time. Those are outcome-conditioned associations from two fights, not causal explanations or a win-rate estimate. The paired P5/P10 rows show that the same initial seed/orientation does not reproduce P11's result with the other settings. Nothing here meets the owner's above-50% criterion or authorizes a resonator design.

The smallest single scripted candidates supported by these measurements, **not run or tuned**:

1. **Own ranged targeting only:** retain movement and gun policy; when an enemy ranged is within the unit's native legal reach and itself threatens a living own gun, prioritize that threat using one predeclared ordering. This can use the unselected reachable opportunities, but P11 already selects a threat on 56.79% of reachable ticks, and reach exists on only 14.26% of ranged ticks; the remaining opportunity is 6.16% of all gun-phase ranged ticks. It cannot solve the predominant distance gap alone. Native line clearance/readiness and friendly-fire consequences must still be checked in a future authorized probe.
2. **Own ranged position only:** retain targeting and gun policy; move ranged units to an escort position on the enemy-facing side of the battery so they can reach the gun-threatening enemy ranged before first gun damage. The early distance deficit is roughly 322−277≈45 px for the median own ranged unit in P11. That is a motivation, not a chosen escort constant or achieved-position guarantee: a single battery centroid can poorly represent a dispersed battery, and movement must preserve splash spacing and native clipping/collision behavior. Declare one escort rule before combat; keep targeting separate.
3. **Own gun commitment goal only:** retain targeting, multiplier/stop conventions and spacing; choose a gun-band post outside all observed enemy-ranged reach if a legal post exists, with one predeclared fallback when it does not. Our guns need distance ≤320 px to their gun target but >278 px from each threatening enemy ranged. On a collinear approach with the enemy screen about 52 px ahead of its guns, a 308 px post is only about 256 px from that screen; merely raising the radial distance to 320 px gives about 268 px, still inside reach. A fixed “stand slightly farther back” is therefore poorly supported; safe commitment may require an angular/end-side post or deferral. Only 1.83% of early P11 gun snapshots are both ranged-safe and within the selected gun target's band. Observed safe snapshots do not establish a maintainable, collision-free alternative post. Safety must be evaluated on the final spacing-shifted, native-clipped goal; preserving P5's zero multiplier can prevent movement toward a changed goal. Feasibility is an explicit future probe question, not a result here.

Each candidate changes one scripted policy component on P11 and needs its own owner-authorized sealed declaration/fresh entropy. No escort offset, angle, wait threshold, target ordering, or fallback was selected from these outcomes. The data favors addressing reach/placement at least alongside priority; it does not prove which candidate will win.

Reproduction: `python3 s4_ranged_threat_v1/analyze.py` then `python3 s4_ranged_threat_v1/summarize.py` from astelia_cpp. The first verifies all source raw hashes, independently audits all original probe rows, and emits [COMPACT.json](s4_ranged_threat_v1/COMPACT.json) and [SPACING_RECOMPUTATION.json](s4_ranged_threat_v1/SPACING_RECOMPUTATION.json). The second emits [DERIVED.json](s4_ranged_threat_v1/DERIVED.json) and this report. The separate reviewer pass and fixes are recorded in [OWNER_RECHECK.md](s4_ranged_threat_v1/OWNER_RECHECK.md). Raw remains local; no delivered file exceeds 45 MB. PLAN_CURRENT, DESIGN_0G, and committed source receipts were not edited.
'''
    (CPP/'S4_RANGED_THREAT_DIAGNOSTIC.md').write_text(text)


if __name__ == '__main__':
    main()
