"""Development observations with explicit denominators; readings belong to Claude."""
import collections
import itertools
import json
from lab import HERE,RAW,ARMS,GRID,LOOKS,SERIES_COUNT,identity,read,write,records_for,sha,grid_name
from metrics import summarize,paired,average

def comparison(records):
    return dict(arms={a:summarize([r for r in records if r['meta']['arm']==a]) for a in ARMS},paired=paired(records))

def series_data(records):
    grouped=collections.defaultdict(list)
    for r in records:grouped[(r['meta']['arm'],r['meta']['series'])].append(r)
    series=[]
    for (arm,index),rows in sorted(grouped.items()):
        rows.sort(key=lambda r:r['meta']['fight'])
        if [r['meta']['fight'] for r in rows]!=list(range(1,len(rows)+1)) or any(not r['stats']['win'] for r in rows[:-1]):raise RuntimeError('invalid series sequence')
        complete=not rows[-1]['stats']['win'] or len(rows)==10
        series.append(dict(arm=arm,series=index,complete=complete,streak=sum(r['stats']['win'] for r in rows),fights_reached=len(rows)))
    arms={}
    for a in ARMS:
        done=[s for s in series if s['arm']==a and s['complete']];rows=[r for r in records if r['meta']['arm']==a]
        arms[a]=dict(n_series=len(done),mean_streak=average([s['streak'] for s in done]),streak_distribution={str(k):v for k,v in collections.Counter(s['streak'] for s in done).items()},
            reach=[dict(fight=f,n=sum(s['fights_reached']>=f for s in done),denominator=len(done),roles_before={role:average([r['meta']['roles_before'][role] for r in rows if r['meta']['fight']==f]) for role in ('melee','ranged','artillery')}) for f in range(1,11)],
            fights=summarize(rows),per_tactic={t:summarize([r for r in rows if r['meta']['tactic']==t]) for t in sorted({r['meta']['tactic'] for r in rows})})
    streaks={}
    for a,b in itertools.combinations(ARMS,2):
        cells=collections.defaultdict(dict)
        for s in series:
            if s['complete'] and s['arm'] in (a,b):cells[s['series']][s['arm']]=s['streak']
        streaks[f'{b} minus {a}']=average([p[b]-p[a] for p in cells.values() if len(p)==2])
    reached=[dict(r,meta=dict(r['meta'],pair=(r['meta']['series'],r['meta']['fight']))) for r in records]
    return dict(complete=len(series)==len(ARMS)*SERIES_COUNT and all(s['complete'] for s in series),primary='streak',series=series,arms=arms,paired_streak_difference=streaks,paired_reached_fights=paired(reached),reached_limit='Only jointly reached positions; carried cohorts differ and conditioning on survival is descriptive.')

def stage_data(stage,look=None):
    records=list(records_for(stage).values())
    if stage=='series':return series_data(records)
    if stage=='mechanism':
        grids={}
        for knobs in GRID:
            variant=grid_name(knobs)
            rows=[r for r in records if r['meta']['arm']!=ARMS[2] or r['meta']['variant']==variant]
            data=comparison(rows)
            data['drills']={group:comparison([r for r in rows if r['meta']['group']==group]) for group in ('D1','V1D2')}
            data['complete']=all(data['arms'][a]['n']==20 for a in ARMS)
            grids[variant]=data
        return dict(stage=stage,complete=all(g['complete'] for g in grids.values()),grid=grids,declaration_sha256=sha(HERE/'DECLARATION.json'),pick='One-time Claude choice on mechanism only; outcome has no grid search')
    rows=[r for r in records if r['meta']['pair']<look];data=comparison(rows)
    data.update(stage=stage,look=look,complete=all(data['arms'][a]['n']==look for a in ARMS),declaration_sha256=sha(HERE/'DECLARATION.json'),per_tactic={t:comparison([r for r in rows if r['meta']['opponent']==t]) for t in sorted({r['meta']['opponent'] for r in rows})})
    return data

def render():
    d=identity();mechanism=stage_data('mechanism');outcomes={str(n):stage_data('outcome',n) for n in LOOKS};series=stage_data('series')
    result=dict(status='DEVELOPMENT_ONLY',labels=d['labels'],mechanism=mechanism,outcomes=outcomes,series=series,pick=read(HERE/'PICK.json') if (HERE/'PICK.json').exists() else None,reading=d['reading'])
    write(HERE/'OBSERVATIONS.json',result)
    (HERE/'SHAPE_LAB_REPORT.md').write_text('Prepared development test / observations\n\nV1: base script, central-sync script, local battery oscillator (RRG mechanism). No acceptance claim.\n\n'+
        'Read mechanism first, choose once, then C3 at 50/100/200 total pairs and ten paired series. Wins require strict elimination before 150 s. Won/non-win losses have separate n.\n\n'+
        'Volley membership: central starts sharing one preparation tick; oscillator/base share one release tick (1/30 s). Multi-shell volleys only for spread; singleton count disclosed. This is firing synchrony, not time-on-target/V2 geometry.\n\n'+
        'Dodge success is the fraction of all launch-exposed enemies for resolved shells which escape the blast, with pre-landing deaths counted as non-escapes and shown. Hits/shell uses landed shells, zero-hit shells included, unresolved shells censored. Shells/kill uses artillery kills only. Idle is legal suppression by timing (engine preparation-ready for central sync, fully prepared for oscillator). Low-gun intervals and null ratios are shown.\n\n```json\n'+json.dumps(result,indent=2)+'\n```\n')
    from replays import render_selected
    render_selected([*records_for('outcome').values(),*records_for('series').values()])
