"""Stored-state-only extra diagnostics: common coarse reversals and death role geometry."""
import collections,gzip,json,math,re,statistics,time
from COMMON import HERE,CPP,PAIRS,REPO,sha,write
from ANALYZE import KIND,dist,legal
PATTERN=re.compile(rb'^\{"step":([0-9]+),"state":')

def main():
    start=time.time();awake=time.monotonic();all_results=[]
    for rec in json.loads((HERE/'FIGHTS.json').read_text()):
        f=json.loads((HERE/(rec['id']+'_SUMMARY.json')).read_text())
        death_steps=collections.defaultdict(list)
        for d in f['deaths']:death_steps[round(d['time_s']*30)].append(d)
        wanted={n-1 for n in death_steps}
        pre_death={};data={w:{'previous':None,'vectors':{},'units':collections.defaultdict(collections.Counter)} for w in (6,30)}
        snapshots={};last=None
        for file in rec['trace_files']:
            with gzip.open(HERE/file,'rb') as source:
                for line in source:
                    match=PATTERN.match(line)
                    if not match:continue
                    step=int(match.group(1))
                    if step%6 and step not in wanted:continue
                    st=json.loads(line)['state'];us={u['id']:u for u in st['units']};last=st
                    if step in wanted:pre_death[step+1]=us
                    for w,entry in data.items():
                        if step%w:continue
                        prev=entry['previous'];entry['previous']=st
                        if prev is None:continue
                        dt=st['t']-prev['t'];assert abs(dt-w/30)<1e-8
                        for a in prev['units']:
                            if a['team'] or not a['alive'] or not us[a['id']]['alive']:
                                entry['vectors'].pop(a['id'],None);continue
                            uid=a['id'];b=us[uid];u=entry['units'][uid];u['seconds']+=dt
                            v=(b['x']-a['x'],b['y']-a['y'])
                            if math.hypot(*v)/dt>=5:
                                old=entry['vectors'].get(uid)
                                if old is not None:u['reversals']+=v[0]*old[0]+v[1]*old[1]<0
                                entry['vectors'][uid]=v
                            else:entry['vectors'].pop(uid,None)
                    if step%60==0:
                        snapshots[str(step//60)]={}
                        for role in ('melee','ranged','artillery'):
                            own=[u for u in us.values() if u['alive'] and u['team']==0 and u['role']==role]
                            guns=[u for u in us.values() if u['alive'] and u['team']==1 and u['role']=='artillery']
                            snapshots[str(step//60)][role]=dict(units=len(own),fraction_near_wall=statistics.mean(min(u['x'],1400-u['x'],u['y'],800-u['y'])<u['debug']['r']+2 for u in own) if own else None,
                                mean_nearest_gun_px=statistics.mean(min(dist(u,g) for g in guns) for u in own) if own and guns else None)
        extra_deaths=[]
        for step,ds in death_steps.items():
            for d in ds:
                us=pre_death[step];u=us[d['id']];enemies=[e for e in us.values() if e['alive'] and e['team']!=0]
                byrole={r:[e for e in enemies if e['role']==r] for r in ('melee','ranged','artillery')}
                row=dict(id=d['id'],time_s=d['time_s'],role=d['role'],near_wall=min(u['x'],1400-u['x'],u['y'],800-u['y'])<u['debug']['r']+2,
                    enemy_reaches_covering_victim={r:sum(legal(e,u) for e in es) for r,es in byrole.items()},
                    nearest_enemy_distance_px={r:min((dist(u,e) for e in es),default=None) for r,es in byrole.items()},
                    own_legal_enemies_by_role={r:sum(legal(u,e) for e in es) for r,es in byrole.items()})
                extra_deaths.append(row)
        assert len(extra_deaths)==len(f['deaths']) and {d['id'] for d in extra_deaths}=={d['id'] for d in f['deaths']}
        role={u['id']:u['role'] for u in f['units']}
        result=dict(id=rec['id'],pair=rec['pair'],deaths=extra_deaths,snapshots_2s=snapshots,coarse_reversals={})
        for w,entry in data.items():
            result['coarse_reversals'][str(w/30)]={}
            for r in ('melee','ranged','artillery'):
                us=[dict(id=uid,**v) for uid,v in entry['units'].items() if role[uid]==r]
                seconds=sum(u['seconds'] for u in us); reversals=sum(u.get('reversals',0) for u in us)
                result['coarse_reversals'][str(w/30)][r]=dict(observed_alive_seconds=seconds,reversals=reversals,
                      reversals_per_unit_minute=60*reversals/seconds if seconds else None,units=us)
        all_results.append(result)
        print(rec['id'],flush=True)
    summary={}
    for p,key in enumerate(PAIRS):
        fs=[f for f in all_results if f['pair']==p];summary['|'.join(key)]={}
        for r in ('melee','ranged','artillery'):
            ds=[d for f in fs for d in f['deaths'] if d['role']==r]
            result=dict(deaths_near_wall=sum(d['near_wall'] for d in ds),
                deaths_covered_by_enemy_melee=sum(d['enemy_reaches_covering_victim']['melee']>0 for d in ds),
                deaths_covered_by_enemy_direct=sum(d['enemy_reaches_covering_victim']['ranged']>0 for d in ds),
                deaths_own_legal_gun=sum(d['own_legal_enemies_by_role']['artillery']>0 for d in ds),coarse_reversals={})
            for w in ('0.2','1.0'):
                secs=sum(f['coarse_reversals'][w][r]['observed_alive_seconds'] for f in fs)
                n=sum(f['coarse_reversals'][w][r]['reversals'] for f in fs)
                result['coarse_reversals'][w]=dict(seconds=secs,count=n,per_unit_minute=60*n/secs if secs else None)
            summary['|'.join(key)][r]=result
    write(HERE/'SUPPLEMENT.json',dict(status='STORED_ONLY_NO_FIGHTS',elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake,
         definitions=dict(coarse='Non-overlapping 0.2 s and 1 s realized displacements; speed >=5 px/s; consecutive dot<0; pauses break adjacency; only intervals alive at both ends',
                          wall='centre within radius + 2 px of an arena edge',death_role_geometry='last-live pre-step; overlapping enemy reaches are not killer attribution'),
         summary=summary,fights=all_results))

if __name__=='__main__':main()
