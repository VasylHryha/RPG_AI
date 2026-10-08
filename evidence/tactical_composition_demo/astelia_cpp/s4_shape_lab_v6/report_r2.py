"""Per-arm staged readings plus a shared two-axis chart; no automatic winner."""
import collections
import itertools
import json
import lab_r2 as lab
from metrics import summarize,paired,average
HERE=lab.HERE;RAW=lab.RAW

def comparison(records,arms):return dict(arms={a:summarize([r for r in records if r['meta']['arm']==a]) for a in arms},paired=paired(records))
def series_data(records,arms):
    grouped=collections.defaultdict(list)
    for r in records:grouped[(r['meta']['arm'],r['meta']['series'])].append(r)
    series=[]
    for (arm,index),rows in sorted(grouped.items()):
        rows.sort(key=lambda r:r['meta']['fight'])
        if [r['meta']['fight'] for r in rows]!=list(range(1,len(rows)+1)) or any(not r['stats']['win'] for r in rows[:-1]):raise RuntimeError('invalid series sequence')
        complete=not rows[-1]['stats']['win'] or len(rows)==10
        series.append(dict(arm=arm,series=index,complete=complete,streak=sum(r['stats']['win'] for r in rows),fights_reached=len(rows),failure_tactic=rows[-1]['meta']['tactic'] if not rows[-1]['stats']['win'] else None))
    data={}
    for a in arms:
        done=[s for s in series if s['arm']==a and s['complete']];rows=[r for r in records if r['meta']['arm']==a]
        data[a]=dict(n_series=len(done),mean_streak=average([s['streak'] for s in done]),streak_distribution={str(k):v for k,v in collections.Counter(s['streak'] for s in done).items()},
            streak_reach=[dict(k=k,n=sum(s['streak']>=k for s in done),denominator=len(done)) for k in range(1,11)],
            roster_before=[dict(fight=f,roles={role:average([r['meta']['roles_before'][role] for r in rows if r['meta']['fight']==f]) for role in ('melee','ranged','artillery')}) for f in range(1,11)],fights=summarize(rows))
    streaks={}
    for a,b in itertools.combinations(arms,2):
        cells=collections.defaultdict(dict)
        for s in series:
            if s['complete'] and s['arm'] in (a,b):cells[s['series']][s['arm']]=s['streak']
        streaks[f'{b} minus {a}']=average([p[b]-p[a] for p in cells.values() if len(p)==2])
    reached=[dict(r,meta=dict(r['meta'],pair_key=f"{r['meta']['series']}:{r['meta']['fight']}")) for r in records]
    return dict(complete=len(series)==len(arms)*lab.SERIES_COUNT and all(s['complete'] for s in series),primary='streak',series=series,arms=data,paired_streak_difference=streaks,paired_reached_fights=paired(reached),reached_limit='Only jointly reached positions; arm-specific survivor composition differs.')

def stage_data(stage,look=None,arm=None,records=None):
    arm=arm or lab.SELECTED_ARM;arms=lab.comparison_arms(arm)
    if records is None:records=list(lab.records_for(stage,arm=arm,look=look).values())
    rows=[r for r in records if r['meta']['arm'] in arms]
    if stage=='series':return series_data(rows,arms)
    if stage=='mechanism':
        rows=[r for r in rows if r['meta']['group'] in lab.groups(arm)]
        data=comparison(rows,arms);candidate=data['arms'][arm];ref=data['arms']['E1' if arm=='E1+R1' else 'base']
        activated=candidate['totals']['planner_assignments']>0 if arm=='V2' else candidate['totals']['engagement_floor_ticks']>0 if arm=='E1' else candidate['totals']['rotation_activations']>0
        data.update(complete=all(data['arms'][a]['n']==20 for a in arms),mechanism_gate_observations=dict(activated=activated,active_ranged=ref['totals']['in_range_seconds']>0,metric_movement='Claude must read paired metric movement, guards and tradeoffs; activation alone is insufficient.'),drills={g:comparison([r for r in rows if r['meta']['group']==g],arms) for g in lab.groups(arm)})
    else:
        rows=[r for r in rows if r['meta']['pair']<look];data=comparison(rows,arms)
        tactics=['regular',*lab.identity()['pool']]
        data.update(look=look,complete=all(data['arms'][a]['n']==look for a in arms),per_tactic={t:comparison([r for r in rows if r['meta']['opponent']==t],arms) for t in tactics})
    data.update(stage=stage,arm=arm,declaration_sha256=lab.sha(HERE/'DECLARATION.json'))
    return data

def render():
    d=lab.identity();selected=lab.SELECTED_ARM;result=dict(status='PREPARED_DEVELOPMENT_ONLY',labels=d['labels'],common_timing=lab.timing(),timing_label='RRG battery phase' if lab.timing()['mode']=='battery_oscillator' else 'script',timing_selection_sha256=lab.sha(HERE/'TIMING_SELECTION.json') if (HERE/'TIMING_SELECTION.json').exists() else None,reading=d['reading'],arms={})
    # One snapshot per stage, selected arm only; no global arm mutation.
    records={stage:list(lab.records_for(stage,arm=selected).values()) for stage in ('mechanism','outcome','series')}
    result['arms'][selected]=dict(mechanism=stage_data('mechanism',arm=selected,records=records['mechanism']),outcomes={str(n):stage_data('outcome',n,arm=selected,records=records['outcome']) for n in lab.LOOKS},series=stage_data('series',arm=selected,records=records['series']))
    summary_path,summary=lab.stage_summary('mechanism',records=records['mechanism'])
    if summary_path.exists():
        if lab.read(summary_path)!=summary:raise RuntimeError('stage summary drift')
    elif summary['complete']:
        lab.write(summary_path,summary,exclusive=True)
    lab.write(HERE/f'OBSERVATIONS_{selected}_R2.json',result)
    points=[]
    for arm in (selected,):
        # Use the latest COMPLETE look only; never compare different arm lengths.
        complete=[(n,v) for n,v in result['arms'][arm]['outcomes'].items() if v['complete']]
        if not complete:continue
        n,v=max(complete,key=lambda item:int(item[0]));ref='E1' if arm=='E1+R1' else 'base'
        rows=records['outcome'];by=collections.defaultdict(dict)
        for r in rows:
            if r['meta']['pair']<int(n) and r['meta']['arm'] in (ref,arm):by[r['meta']['pair']][r['meta']['arm']]=r['stats']
        matched=[p for p in by.values() if len(p)==2]
        points.append(dict(arm=arm,reference=ref,n=len(matched),deaths_saved=average([p[ref]['own_lost']-p[arm]['own_lost'] for p in matched])['mean'],kills_gained=average([p[arm]['enemy_kills']-p[ref]['enemy_kills'] for p in matched])['mean']))
    lab.write(HERE/f'AXIS_CHART_{selected}_R2.json',dict(x='own deaths saved per fight',y='enemy kills gained per fight',points=points))
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="600" height="420" viewBox="0 0 600 420"><rect width="600" height="420" fill="white"/><path d="M40 200H560 M300 30V370" stroke="#888"/><text x="200" y="402">Own deaths saved per fight →</text><text x="20" y="20">Enemy kills gained per fight ↑</text>']
    if not points:svg.append('<text x="200" y="180">No complete outcome look for paired axes</text>')
    extent=max([abs(p[k]) for p in points for k in ('deaths_saved','kills_gained')]+[1])
    for p in points:
        x=300+p['deaths_saved']/extent*220;y=200-p['kills_gained']/extent*155
        svg.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#247"/><text x="{x+8}" y="{y}">{p["arm"]} (n={p["n"]})</text>')
    svg.append(f'<text x="42" y="370">Axis extent ±{extent:.2f}; each point labels its paired n.</text></svg>')
    (HERE/f'AXIS_CHART_{selected}_R2.svg').write_text(''.join(svg))
    (HERE/f'SHAPE_LAB_REPORT_{selected}_R2.md').write_text(f'Prepared development observations; no acceptance claim\n\nAll atoms are script; V2 is script/search. Selected common timing, its independent script/RRG label and selection hash are reported below. Each shape reports both axes over all fights with won/lost/timeout splits. Exchange is a ratio of totals; a zero-death denominator is null with its raw kills retained. Single-fight wins are descriptive.\n\n![Paired axes](AXIS_CHART_{selected}_R2.svg)\n\nMechanism first at 20 pairs; Claude reads actual activation and metric movement. Rotation primary is E1+R1 versus E1, after E1 activates; R1 versus base is diagnostic. All 20 tactic cells are shown, including empty cells. C3 stops at a clear 50/100/200 look; surviving shapes enter ten paired ten-fight series, streak primary. Shots lost are the paired shots_fired delta; triggered survival is observational and predicted deaths are counterfactual, not proven deaths prevented. Heavy diagnostics off.\n\n```json\n'+json.dumps(result,indent=2)+'\n```\n')
    print(f'Report: {HERE / ("SHAPE_LAB_REPORT_"+selected+"_R2.md")}; mechanism summary: {summary_path}')
