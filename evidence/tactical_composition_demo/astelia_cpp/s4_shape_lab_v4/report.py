"""Development observations only: mechanism, sequential outcomes, primary streak."""
import collections
from lab import HERE, V3, RAW, ARMS, LOOKS, SERIES_COUNT, identity, read, write, records_for, sha
from metrics import summarize, paired, average


def comparison(records):
    return dict(arms={arm:summarize([r for r in records if r['meta']['arm']==arm]) for arm in ARMS},
                paired=paired(records),
                paired_losses_both_won=paired([r for r in records if all(
                    other['stats']['win'] for other in records if other['meta']['pair']==r['meta']['pair'])]),
                paired_losses_both_nonwin=paired([r for r in records if all(
                    not other['stats']['win'] for other in records if other['meta']['pair']==r['meta']['pair'])]))


def series_data(records):
    grouped=collections.defaultdict(list)
    for row in records:
        grouped[(row['meta']['arm'],row['meta']['series'])].append(row)
    series=[]
    for (arm,index),rows in sorted(grouped.items()):
        rows.sort(key=lambda r:r['meta']['fight'])
        if [r['meta']['fight'] for r in rows]!=list(range(1,len(rows)+1)):
            raise RuntimeError('noncontiguous series receipts')
        if any(not r['stats']['win'] for r in rows[:-1]):
            raise RuntimeError('series continued after non-win')
        finished=not rows[-1]['stats']['win'] or len(rows)==10
        series.append(dict(arm=arm,series=index,complete=finished,
                           streak=sum(r['stats']['win'] for r in rows),fights_reached=len(rows),
                           fights=[dict(fight=r['meta']['fight'],tactic=r['meta']['tactic'],
                                        seed=r['meta']['seed'],orientation=r['meta']['orientation'],
                                        units_before=r['meta']['units_before'],roles_before=r['meta']['roles_before'],
                                        win=r['stats']['win'],own_lost=r['stats']['own_lost']) for r in rows]))
    arms={}
    for arm in ARMS:
        completed=[s for s in series if s['arm']==arm and s['complete']]
        rows=[r for r in records if r['meta']['arm']==arm]
        arms[arm]=dict(n_series=len(completed),streak_distribution=dict(collections.Counter(s['streak'] for s in completed)),
                       mean_streak=average([s['streak'] for s in completed]),
                       reach=[dict(fight=f,n=sum(s['fights_reached']>=f for s in completed),denominator=len(completed),
                                   units_before=average([r['meta']['units_before'] for r in rows if r['meta']['fight']==f]),
                                   role_units_before={role:average([r['meta']['roles_before'][role] for r in rows if r['meta']['fight']==f]) for role in ('melee','ranged','artillery')}) for f in range(1,11)],
                       fights=summarize(rows),
                       per_tactic={t:summarize([r for r in rows if r['meta']['tactic']==t]) for t in sorted({r['meta']['tactic'] for r in rows})})
    complete_pairs=collections.defaultdict(dict)
    for s in series:
        if s['complete']: complete_pairs[s['series']][s['arm']]=s['streak']
    differences=[p[ARMS[1]]-p[ARMS[0]] for p in complete_pairs.values() if len(p)==2]
    # Same reached fight positions only. Arm-specific stopping creates attrition;
    # never fabricate later fights or call the survival subsets exchangeable.
    reached=[]
    for row in records:
        copied=dict(row,meta=dict(row['meta'],pair=(row['meta']['series'],row['meta']['fight'])))
        reached.append(copied)
    return dict(complete=len(series)==2*SERIES_COUNT and all(s['complete'] for s in series),
                primary='streak distribution and paired streak difference',series=series,arms=arms,
                paired_streak_difference=dict(direction='react minus base',**average(differences)),
                paired_reached_fights=paired(reached),
                reached_limit='Fight differences use only positions reached by both arms, with differing carried cohorts; conditioning on survival is descriptive.')


def stage_data(stage,look=None):
    records=list(records_for(stage).values())
    if stage=='series': return series_data(records)
    limit=10 if stage=='mechanism' else look
    records=[r for r in records if r['meta']['pair']<limit]
    data=comparison(records)
    data.update(stage=stage,look=limit,complete=all(data['arms'][a]['n']==limit for a in ARMS) and data['paired']['n']==limit,
                declaration_sha256=sha(HERE/'DECLARATION.json'))
    if stage=='outcome':
        data['per_tactic']={t:comparison([r for r in records if r['meta']['opponent']==t])
                            for t in sorted({r['meta']['opponent'] for r in records})}
    return data


def render():
    identity()
    mechanism=stage_data('mechanism')
    outcomes={str(n):stage_data('outcome',n) for n in LOOKS}
    series=stage_data('series')
    reference=read(V3/'S10X_SUMMARY.json')
    write(HERE/'OBSERVATIONS.json',dict(mechanism=mechanism,outcomes=outcomes,series=series,
                                       historical_elite_reference=reference,
                                       reference_note='v3 historical series, unpaired to v4; not rerun or a paired effect estimate'))
    lines=['Development preparation / observations','',
           'REACT v4: forcedP16 versus forcedP16+react. No scientific verdict or acceptance.',
           '', 'Mechanism first: D2, 10 paired seeds / 20 actual fights.',
           'Counts are own successful dodge intent ticks, not independent evade events. Shell ratios include zero-hit landed enemy shells; unresolved shells are censored. Damage units are HP. Null means no denominator.',
           'All summaries show their n; paired differences are react minus base. Pooled shell ratios are shell-weighted; paired ratios average per-fight differences over pairs with both denominators.',
           'Won fights and all non-wins (losses/timeouts/draws) have separate loss denominators.',
           '', 'Mechanism:', '```json',__import__('json').dumps(mechanism,indent=2),'```']
    for n,data in outcomes.items():
        lines += ['',f'C3 sequential look {n} paired fights (total across 20 opponents):',
                  '```json',__import__('json').dumps(data,indent=2),'```']
    lines += ['', 'S10X: streak is primary. Ten paired series, at most ten fights each; first non-win stops that arm.',
              '```json',__import__('json').dumps(series,indent=2),'```',
              '', 'Elite reference: ../s4_shape_lab_v3/SHAPE_LAB_REPORT.md and S10X_SUMMARY.json (historical, unpaired).',
              'C3 retains v3 abilities settings; S10X abilities off, survivors healed, dead cohort IDs absent. Map seed and orientation are identical for both arms at each scheduled position; survivor populations diverge by design.',
              'C3 50/100/200 is not 200 per tactic. Individual tactic samples are descriptive (2–3, 5, 10 pairs); no fine per-tactic claims.',
              'At each look Claude records continue/stop before more C3 fights. No automatic significance rule or tuning; stop or park at 200.',
              'Calibration reuses allocated fights. Cap bounds native execution per invocation; bookkeeping/rendering may finish afterwards. No elapsed timing is claimed before calibration.']
    (HERE/'SHAPE_LAB_REPORT.md').write_text('\n'.join(lines)+'\n')
    from replays import render_selected
    render_selected([*records_for('outcome').values(),*records_for('series').values()])
