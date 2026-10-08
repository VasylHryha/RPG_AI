"""Compact per-drill and per-series summaries, with explicit unrun criteria."""
import collections
import statistics
from lab import *
from replays import extract, unchanged_scorecard

MEASURES={
 'D1':['t_enemy_guns_wiped','own_guns_lost','gun_damage_on_enemy_guns_share_while_guns_alive','own_shells_no_hit'],
 'D2':['own_units_hit_per_enemy_shell','damage_taken_per_enemy_shell'],
 'D3':['damage_to_own_guns_by_source','escorts_lost','enemy_ranged_killed'],
 'D4':['exchange_ratio','melee_survivors'],
 'D5':['firepower_retained','units_out_of_fight','own_lost'],
 'C1':['win','t_elimination','own_lost'],'C2':['win','t_elimination','own_lost'],'C3':['win','t_elimination','own_lost']}
CRITERIA={'D1':'all enemy guns dead; own guns lost ≤1; gun damage share while enemy guns alive ≥60%',
          'D2':'≤1.5 own units hit per landed enemy shell',
          'D3':'0 enemy ranged/melee damage to own guns',
          'D4':'exchange >1:1; majority of melee survive',
          'D5':'no units out of weapon reach during fight',
          'C1':'elimination before 150s; no own losses',
          'C2':'elimination before 150s; whole-army draft ≤4 own losses',
          'C3':'elimination before 150s; whole-army draft ≤4 own losses'}

def good(drill,s):
    if drill=='D1':return s['enemy_guns_killed']==10 and s['own_guns_lost']<=1 and (s['gun_damage_on_enemy_guns_share_while_guns_alive'] or 0)>=.6
    if drill=='D2':return s['own_units_hit_per_enemy_shell'] is not None and s['own_units_hit_per_enemy_shell']<=1.5
    if drill=='D3':return sum(s['damage_to_own_guns_by_source'].get(r,0) for r in ('ranged','melee'))==0
    if drill=='D4':return (s['exchange_ratio'] is not None and s['exchange_ratio']>1 or s['exchange_zero_loss'] and s['enemy_killed']>0) and s['melee_survivors']>5
    if drill=='D5':return s['units_out_of_fight']==0
    return s['win'] and s['own_lost']<=(0 if drill=='C1' else 4)

def aggregate(rows,keys):
    result={}
    for key in keys:
        vals=[r['stats'][key] for r in rows]
        if any(isinstance(v,dict) for v in vals):
            result[key]={k:sum(v.get(k,0) for v in vals)/len(vals) for k in set().union(*(v.keys() for v in vals))}
        else:
            finite=[v for v in vals if v is not None]
            result[key]=dict(mean=statistics.mean(finite) if finite else None,evaluated=len(finite),total=len(vals))
    return result

def render():
    records=sorted((verified_record(p.name[:-len('_COMPLETE.json')]) for p in RAW.glob('*_COMPLETE.json') if not p.name.startswith('check_')),key=lambda r:r['tag']) if RAW.exists() else []
    grouped=collections.defaultdict(list)
    for r in records:grouped[r['meta']['group']].append(r)
    series=[read(p) for p in RAW.glob('*_SERIES.json')] if RAW.exists() else []
    expected=560  # 7*20 +20 extra v6 D4/D5 + C3(20 opponents*2 arms*10)=560
    complete=len([r for r in records if r['meta']['group']!='S10X'])==expected and len(series)==30
    status='DONE' if complete else 'PARTIAL' if records or (HERE/'BUILD.json').exists() or (HERE/'DECLARATION.json').exists() else 'NOT_RUN'
    text=[status,'','# Shape lab v2: development tooling and observations','',
          'Implements SHAPE_LAB_SPEC §§3–6. No judging seeds, registered endpoints, policy changes or scientific acceptance.',
          'V2 uses fresh development entropy and the unchanged v1 native engine/checks. V1 evidence is preserved.', '']
    checks=read(HERE/'CHECKS.json') if (HERE/'CHECKS.json').exists() else None
    text+=['## Section-3 checks','']
    if checks:
        text+=['| Check | Result |','|---|---|']+[f"| {r['name']} | {'PASS' if r['pass_check'] else 'FAIL'} |" for r in checks['checks']]
        if checks['checks'] and 'lab_stream_sha256' in checks['checks'][0]:
            text += ['', f"Compatibility output stream SHA256: `{checks['checks'][0]['lab_stream_sha256']}`."]
        if 'compatibility_seconds' in checks:
            text += [f"Measured full-output compatibility fight: {checks['compatibility_seconds']:.3f} seconds."]
        text += ['', 'Required check receipt status: '+checks['status'], '']
    else:text+=['NOT_RUN: required checks pending. No drills allowed.','']
    text+=['## Projection and process gate','']
    if (HERE/'CALIBRATION.json').exists():text+=['```json',json.dumps(read(HERE/'CALIBRATION.json'),indent=2),'```','']
    else:text+=['Calibration NOT_RUN; run requires measured timing.','']
    if (HERE/'RUN.json').exists():text+=['```json',json.dumps(read(HERE/'RUN.json'),indent=2),'```','']
    if (HERE/'PROCESS_GATE.json').exists():
        g=read(HERE/'PROCESS_GATE.json');text+=[f"Process gate: **{g['status']}**. {g.get('stderr','').strip()}",'']
    text+=['## Per-drill results','',
           'Criteria apply per fight; the table reports how many fights met the complete conjunction. Missing observations are **not met (not evaluated)**, not measured failures. Conditional times and shares show evaluated denominators in JSON.', '']
    replay_index=[]
    for drill in DRILLS:
        arms=(*ARMS,'v6') if drill in ('D4','D5') else ARMS
        text += [f'### {drill}', '',CRITERIA[drill], '', '| Arm | Opponent | Completed / planned | Section-4 metrics (means) | Draft criteria |','|---|---|---:|---|---|']
        groups=collections.defaultdict(list)
        for r in grouped[drill]:groups[(r['meta']['arm'],r['meta']['opponent'])].append(r)
        pool=read(HERE/'DECLARATION.json')['pool'] if (HERE/'DECLARATION.json').exists() else catalog()['POOL']
        for arm in arms:
            for opponent in (['regular',*pool] if drill=='C3' else [None]):
                rs=groups[(arm,opponent)];metrics=aggregate(rs,MEASURES[drill]) if rs else {'status':'not_run'}
                passed=sum(good(drill,r['stats']) for r in rs)
                verdict=f"{'met' if len(rs)==10 and passed==10 else 'not met'} ({passed}/{len(rs)} evaluated)" if rs else 'not met (not evaluated)'
                text+=[f"| {arm} | {opponent or 'specified dummy/regular'} | {len(rs)} / 10 | {json.dumps(metrics,separators=(',',':'))} | {verdict} |"]
        summary=dict(drill=drill,criteria=CRITERIA[drill],per_arm=[dict(arm=a,opponent=o,completed=len(rs),planned=10,metrics=aggregate(rs,MEASURES[drill]) if rs else {},criteria_met=sum(good(drill,r['stats']) for r in rs)) for (a,o),rs in groups.items()])
        write(HERE/(drill+'_SUMMARY.json'),summary)
        item=extract(grouped[drill],HERE/(drill+'_replays.json'),drill)
        if item:replay_index.append(item)
        text+=['']
    text+=['## S10X: abilities off; regular skills, uniform POOL replacement draws','',
           '| Arm | Series completed / 10 | Streak mean / median / min / max | Fight reached | Mean own losses per fight | Draft ≤4 losses |',
           '|---|---:|---|---|---|---|']
    series_summary=[]
    for arm in SERIES_ARMS:
        runs=sorted([r for r in series if r['arm']==arm],key=lambda r:r['series']);streaks=[r['streak'] for r in runs];fights=[f for r in runs for f in r['fights']]
        dist=dict(mean=statistics.mean(streaks),median=statistics.median(streaks),min=min(streaks),max=max(streaks)) if streaks else None
        losses=statistics.mean(f['units_lost'] for f in fights) if fights else None
        text+=[f"| {arm} | {len(runs)} / 10 | {json.dumps(dist)} | {[r['fight_reached'] for r in runs] or 'not_run'} | {losses if losses is not None else 'not_run'} | {'met' if losses is not None and losses<=4 else 'not met' if losses is not None else 'not met (not evaluated)'} |"]
        tactics=collections.defaultdict(list)
        for f in fights:tactics[f['tactic']].append(f)
        per_tactic={name:dict(fights=len(fs),non_wins=sum(not f['win'] for f in fs),units_lost=sum(f['units_lost'] for f in fs),mean_units_lost=statistics.mean(f['units_lost'] for f in fs)) for name,fs in tactics.items()}
        detail=dict(arm=arm,streak_distribution=dist,series=runs,per_tactic=per_tactic,mean_losses_per_fight=losses)
        series_summary.append(detail)
        for run in runs:
            rs=[r for r in grouped['S10X'] if r['meta']['arm']==arm and r['meta']['series']==run['series']]
            item=extract(rs,HERE/f"S10X_{arm}_s{run['series']:02d}_replays.json",f"S10X {arm} {run['series']}")
            if item:replay_index.append(item)
    text+=['','Reference band: owner recollection of typical streak 6, sometimes 8; no statistical population claim.', '',
           '### Units before each fight and per-tactic losses','', '| Arm | Series | Streak | Fight reached | Units before each fight |','|---|---:|---:|---:|---|']
    for detail in series_summary:
        for run in detail['series']:text+=[f"| {detail['arm']} | {run['series']} | {run['streak']} | {run['fight_reached']} | {[f['units_before'] for f in run['fights']]} |"]
    if not series:text+=['| v7 / forcedP16 / elite | — | not_run | not_run | not_run |']
    text+=['','| Arm | Tactic | Fights | Non-wins | Units lost total / mean |','|---|---|---:|---:|---|']
    for detail in series_summary:
        for name,s in detail['per_tactic'].items():text+=[f"| {detail['arm']} | {name} | {s['fights']} | {s['non_wins']} | {s['units_lost']} / {s['mean_units_lost']:.3f} |"]
    if not series:text+=['| v7 / forcedP16 / elite | not_run | 0 | not_run | not_run |']
    write(HERE/'S10X_SUMMARY.json',dict(arms=series_summary))
    write(HERE/'REPLAY_INDEX.json',dict(groups=replay_index))
    if records:write(HERE/'AUXILIARY_SCORECARD.json',unchanged_scorecard(records))
    gate=read(HERE/'PROCESS_GATE.json') if (HERE/'PROCESS_GATE.json').exists() else {'status':'NOT_CHECKED'}
    delivery=read(HERE/'DELIVERY.json') if (HERE/'DELIVERY.json').exists() else {'status':'UNCOMMITTED','reason':'Delivery bookkeeping pending.'}
    text+=['','## Limits and definitions','',
           '- Drills planned: 560 fights; series at most 300. v6 uses delivered attempt-2 θ_v6 in D4 and D5; v7/forcedP16 use θ* ordinal 161. Elite retains full catalog planning and rollout behavior.',
           '- D1 line axial separation is 500 px; cross-line diagonal distances can exceed 600 px. D5 starts 250 px apart. These geometries are declared before drills.',
           '- Lab heading is radians stored as native guard direction; this engine has no general unit-facing state. Army-facing remains the scripted pack direction.',
           '- Static dummies disable reflex dodges and restore their fixed post after native collision separation; other units still receive native collision pushes.',
           '- All enemy-shell multiplicities use landed shells including zero-hit shells; unresolved shells at termination are censored. Firepower uses native range/gap with no extra margin and integrates all alive-unit seconds.',
           '- D1 gun damage share includes only enemy damage while any enemy gun lives; friendly damage is excluded. Null shares mean no qualifying damage. Conditional kill times do not impute a 150-second success.',
           '- The unchanged scorecard can read these observer streams via its RAW constant. Its hardcoded 50/10 denominators and reach+50 differ from reduced drills; it is explicitly auxiliary.',
           '- Replay files retain every executed drill/series fight; deterministic sampling reduces FPS to enforce 8,000,000-byte limit. Replay index lists actual FPS. No replay is fabricated for an unrun fight.',
           '- Slow-field launches are excluded from damaging-shell denominators. Raw entropy, requests, native streams and claims stay in ignored raw/. Immutable completions verify request/code/raw identity; Complete fights are never repeated. Native cap interruptions preserve partial files in raw/interrupted/ and retry that incomplete fight on resume; an unclosed attempt or other incomplete cell requires investigation.',
           f"- Delivery: {delivery['status']}. {delivery['reason']}",
           f"- Process gate: {gate['status']}. {'Drills and series are NOT_RUN.' if not records else 'Executed cells are listed above.'} Execution requires a clear repository-scoped pgrep gate and the measured remaining projection within the current local cap. Each invocation is capped; standalone report rendering is outside that compute cap.", '',
           '## Local artifact inventory','']
    text += [f'- `{p.relative_to(CPP)}`' for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='SHAPE_LAB_REPORT.md']
    text += ['- `s4_shape_lab_v3/SHAPE_LAB_REPORT.md`','',
             'The native binary remains in ignored `s4_shape_lab_v1/build/`; v3 raw ledgers, streams and interruption archives stay in ignored `s4_shape_lab_v3/raw/`. This inventory is not a Git commit-status assertion.','',
             '## Owner recheck','',
             'See OWNER_RECHECK_GATE.md and GATE_DISPOSITION.md in this folder (separate Codex reviewer, same family).',
             'The recheck and disposition are also tracked in docs/PLAN_CURRENT.md, which is excluded from this delivery commit.','']
    (HERE/'SHAPE_LAB_REPORT.md').write_text('\n'.join(text))
    print('Report',status)

if __name__=='__main__':render()
