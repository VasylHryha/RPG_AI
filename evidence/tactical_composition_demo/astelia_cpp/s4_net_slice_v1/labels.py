"""Chronological causal joins. Fit decision intents; never backfill launch outcomes."""
import math
from collections import defaultdict
from schema import check,slots

def join(events):
    decisions={};snapshots={};outcomes=defaultdict(list);casts={};seen=set();last_tick={}
    for e in events:
        if e['tick']<last_tick.get(e['fight'],0):raise ValueError('nonchronological events')
        last_tick[e['fight']]=e['tick']
        key=(e['fight'],e['tick'],e['unit'],e['stage'])
        if key in seen:raise ValueError('duplicate label stage')
        seen.add(key);dkey=(e['fight'],e['decision_tick'],e['unit'])
        if e['stage']=='snapshot':
            check(e['value']);snapshots[dkey]=e['value']
        elif e['stage']=='intent':
            if e['tick']!=e['decision_tick'] or (e['tick']-1)%6 or dkey not in snapshots:raise ValueError('decision cadence/snapshot')
            s=snapshots[dkey];me=check(s);v=e['value'];_,enemies,_,_=slots(s)
            target=next((u for u in enemies if u['id']==v['target']),None)
            if v['target'] and target is None:raise ValueError('unavailable target is not none')
            body=me['guard_until']<=s['t'] and not me['busy'];reach=target is not None and me['min_range']<=math.hypot(target['x']-me['x'],target['y']-me['y'])<=me['range']
            aim=v['aim'];aim_legal=aim is not None and 0<=aim[0]<=s['width'] and 0<=aim[1]<=s['height'] and me['min_range']<=math.hypot(aim[0]-me['x'],aim[1]-me['y'])<=me['range']
            start=body and reach and aim_legal and me['prep']<=0 and me['cooldown']<=0 and me['energy']>=me['cost']
            release=body and reach and aim_legal and me['prep']>0 and me['prep']+s['dt']*me['time_rate']>=me['windup']-1e-9
            decisions[dkey]={'action':v,'volley':e['volley'],'masks':{'target':me['prep']<=0,'move':body,'start':start,'release':release,'aim':aim_legal and (v['start'] or v['release'])},'outcomes':[]}
        elif e['stage']=='cast_start':
            if dkey not in decisions:raise ValueError('cast lacks originating decision')
            ckey=(e['fight'],e['cast_tick'],e['unit'])
            if ckey in casts:raise ValueError('duplicate cast')
            casts[ckey]=(dkey,e['volley'])
        elif e['stage'] in ('consume','launch','cancel','consumed_without_launch'):
            ckey=(e['fight'],e['cast_tick'],e['unit'])
            if ckey not in casts:raise ValueError('orphan cast outcome')
            parent,volley=casts[ckey]
            if dkey!=parent or e['volley']!=volley:raise ValueError('cast origin mismatch')
            outcomes[parent].append(e)
    for key,es in outcomes.items():
        if key not in decisions:raise ValueError('orphan decision')
        decisions[key]['outcomes']=es
    return decisions


def unpack_frame(frame):
    """Reconstruct decision snapshot joins from the single shared joint record."""
    import copy
    result=copy.deepcopy(frame['events'])
    for e in result:
        if e['stage']=='snapshot':
            e['value']={**copy.deepcopy(frame['joint']),'self':e['unit']}
    return result
