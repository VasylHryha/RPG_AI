"""Additional lifecycle counts from initial raw bytes; never advances an engine."""
from collections import Counter, defaultdict
import hashlib
import json
import math
from collection import HERE, read, atomic
from s1_public import reaction, retained_threats
ROOT=HERE/'_local/s0s1/pilot'


def trace():
    stats=defaultdict(Counter);lags=defaultdict(list)
    for row in read(ROOT/'INVENTORY.json')['rows']:
        if row['pair']>=10:continue
        key=row['pilot_cell']+'|'+row['arm'];c=stats[key];casts={};commands={};first={};refresh={};locked=set();h=hashlib.sha256()
        with (ROOT/(row['fight']+'.jsonl')).open('rb') as stream:
            for line in stream:
                h.update(line);f=json.loads(line)
                if f.get('terminal'):continue
                units={u['id']:u for u in f['joint']['units']} if f['joint'] else {};tick=f['tick']
                for e in f['events']:
                    id=e['unit'];v=e['value'];k=(id,e['cast_tick']);stage=e['stage']
                    if stage=='cast_start':casts[id]=(tick,v);c['commanded_starts']+=v['volley']!=0
                    if stage=='s1_refresh':
                        refresh[k]=tick
                        if id in casts:
                            c['refresh_focus_differs_from_start']+=v['focus']!=casts[id][1]['target']
                        if k in first:lags[key].append(tick-first[k])
                    if stage=='projection' and id in casts:
                        me=units.get(id);raw=v['raw'];eff=v['effective'];target=units.get(eff['target']);alive=target and target['hp']>0
                        if me and alive:
                            dist=math.hypot(target['x']-me['x'],target['y']-me['y']);aim=eff['aim'];ad=math.dist(aim,[me['x'],me['y']]) if aim else math.inf
                            ready=me['prep']>0 and me['prep']+f['joint']['dt']*me['time_rate']>=me['windup']-1e-9
                            legal=not me['busy'] and me['guard_until']<=f['joint']['t'] and me['min_range']<=dist<=me['range'] and aim and 0<=aim[0]<=f['joint']['width'] and 0<=aim[1]<=f['joint']['height'] and me['min_range']<=ad<=me['range']
                            if ready and legal and k not in first:
                                first[k]=tick;c['first_release_opportunities']+=1
                                c['command_first_release_opportunities']+=casts[id][1]['volley']!=0
                            if v['release']:
                                s={**f['joint'],'self':id};active=reaction(s,retained_threats(s))[0]
                                c['actual_release_reaction_active']+=active
                                c['automatic_release_reaction_active']+=active and v['reason']=='hold_expired_auto_release'
                        if casts[id][1]['volley'] and raw['volley'] and raw['volley']!=casts[id][1]['volley']:c['pending_command_plan_replaced']+=1
                        if v['raw']['aim'] and eff['aim'] and math.dist(v['raw']['aim'],eff['aim'])>1e-9:
                            c['aim_lock_correction_ticks']+=1;c['command_aim_lock_correction_ticks']+=casts[id][1]['volley']!=0
                    if stage=='launch':
                        if id in casts and casts[id][1]['volley']:
                            c['commanded_launches']+=1
                            if k not in refresh:c['command_launch_without_refresh']+=1
                            if k in first:c['command_launch_after_first_opportunity']+=tick>first[k]
                        casts.pop(id,None)
                    if stage in ('cancel','consumed_without_launch'):casts.pop(id,None)
        assert h.hexdigest()==read(ROOT/(row['fight']+'.receipt.json'))['raw_sha256']
    value=dict(physical_fights=0,counts={k:dict(v) for k,v in stats.items()},refresh_lag_ticks={k:dict(n=len(x),sum=sum(x),max=max(x),positive=sum(v>0 for v in x),mean=sum(x)/len(x)) for k,x in lags.items() if x})
    path=HERE/'S1_WRAPPER_LIFECYCLE_COUNTS.json'
    if path.exists():raise RuntimeError('preserve existing diagnosis')
    atomic(path,value);print(json.dumps(value,indent=2))
if __name__=='__main__':trace()
