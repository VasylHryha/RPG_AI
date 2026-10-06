"""Stored-only reconstruction of every tick; executes zero combat fights."""
import collections, json, math, statistics, time
from COMMON import CPP,HERE,OLD,PAIRS,RAW,REPO,pins,rows,sha,write
ROLES=('melee','ranged','artillery')
# Defaults and unit conversion in unchanged world.cpp::gameConfig/spawn.
KIND={'brute':(64,16,0),'warden':(64,16,0),'hound':(56,6,0),'runner':(60,6,0),
      'spitter':(280,9,0),'shaman':(320,10,0)}

def dist(a,b): return math.hypot(a['x']-b['x'],a['y']-b['y'])

def legal(a,b):
    reach,r,rmin=KIND[a['kind']]
    assert a['debug']['r']==r
    d=dist(a,b)
    return rmin<=d<=reach if a['role']=='artillery' else d<=reach-r-12+r+b['debug']['r']

def mean(xs): return statistics.mean(xs) if xs else None

def stat(xs):
    xs=list(xs); m=mean(xs)
    return dict(n=len(xs),mean=m,min=min(xs) if xs else None,max=max(xs) if xs else None,
                median=statistics.median(xs) if xs else None)

def fresh_unit(u):
    return dict(id=u['id'],role=u['role'],alive_seconds=0.,physical_reversals=0,displacement_pairs=0,
        derivative_samples=0,locked={str(t):0 for t in (.05,.1,.2)},abs_rate_sum=0.,
        pressure_sum=0.,abs_pressure_sum=0.,pressure_ge_abs_omega=0,
        locked_pressure_sum=0.,locked_abs_pressure_sum=0.,rotating_abs_pressure_sum=0.,
        nearest_gun_mode_switches=0,pair_mode_changes=0)


def analyze_fight(rec):
    prev=None; pending=None; diag=None; cap=None; previous_capture=None; last_vectors={}; intent={}; modes={}
    units={}; deaths=[]; guns={}; bins=collections.defaultdict(lambda:collections.Counter()); samples={};
    times=[]; tick=0; non_gun_clear=None; frames=[]; first=None; last_phase_rate={}
    exposure_by_mode=collections.defaultdict(collections.Counter)
    def consume(st, decision, captured):
        nonlocal prev,previous_capture,tick,non_gun_clear,first
        if prev is None:
            prev=st;first=st
            assert len(st['units'])==100 and collections.Counter((u['team'],u['role']) for u in st['units'])=={
                (s,r):n for s in (0,1) for r,n in zip(ROLES,(10,30,10))}
            for u in st['units']:
                if u['team']==0: units[u['id']]=fresh_unit(u)
                if u['team']==1 and u['role']=='artillery':
                    guns[u['id']]=dict(id=u['id'],death_time_s=None,killer_id=None,killer_role=None,
                                      killer_unavailable_reason='Original v5 host does not export lethal hit identities')
            frames.append([0.,[[u['id'],u['team'],ROLES.index(u['role']),round(u['x']),round(u['y']),1.,-1,None,None] for u in st['units']]])
            return
        tick+=1; assert decision['step']==tick and decision['side']==0
        assert not decision['holdEvents'] and all(d['focus'] is None and all(p['remainingHold']==0 for p in d['pairs']) for d in decision['units'])
        dt=st['t']-prev['t']; assert abs(dt-1/30)<1e-10
        pre={u['id']:u for u in prev['units']}; post={u['id']:u for u in st['units']}
        ds={u['id']:u for u in decision['units']}; cs={u['id']:u for u in captured['units']}
        living=[u for u in pre.values() if u['alive']]; enemies=[u for u in living if u['team']==1]; eguns=[u for u in enemies if u['role']=='artillery']
        assert set(ds)=={u['id'] for u in living if u['team']==0}==set(cs)
        if non_gun_clear is None and not any(u['role']!='artillery' for u in enemies): non_gun_clear=prev['t']
        b=int((prev['t']+1e-8)//2); bn=bins[b]; bn['fight_seconds']+=dt
        for side in (0,1):
            for role in ROLES: bn[f'{side}_{role}_survivor_seconds']+=sum(u['team']==side and u['role']==role for u in living)*dt
        for u in living:
            if u['team']!=0: continue
            uid=u['id']; role=u['role']; d=ds[uid]; c=cs[uid]; un=units[uid]
            # Capture's phase is the pre-integration state. commitment is post-integration.
            assert abs(c['x']*100-u['x'])<1e-8 and abs(c['y']*100-u['y'])<1e-8
            assert abs(c['commitment']-d['c'])<1e-12
            un['alive_seconds']+=dt; bn[role+'_unit_seconds']+=dt;bn[role+'_c_seconds']+=d['c']*dt
            old=intent.get(uid,d['c']>=0); mode=True if d['c']>.2 else False if d['c']<-.2 else old; intent[uid]=mode
            bn[role+'_intent_commit_seconds']+=mode*dt
            nearest=min(eguns,key=lambda e:(dist(u,e),e['id'])) if eguns else None
            inside=any(legal(e,u) for e in eguns); assert inside==d['insideGunReach']
            can_reach=any(legal(u,e) for e in enemies)
            bn[role+'_inside_gun_seconds']+=inside*dt; bn[role+'_legal_seconds']+=can_reach*dt
            bn[role+'_inside_gun_no_legal_seconds']+=(inside and not can_reach)*dt
            if nearest:
                bn[role+'_gun_distance_seconds']+=dist(u,nearest)*dt; bn[role+'_gun_present_seconds']+=dt
            pair={p['enemy']:p for p in d['pairs']}
            for p in d['pairs']:
                key=(uid,p['enemy']);un['pair_mode_changes']+=key in modes and modes[key]!=p['mode'];modes[key]=p['mode']
                bn[role+'_pair_seconds']+=dt;bn[role+'_pair_commit_seconds']+=(p['mode']=='commit')*dt
            reference=pair.get(d['reference'])
            if reference:
                bn[role+'_reference_mode_seconds']+=dt;bn[role+'_reference_commit_seconds']+=(reference['mode']=='commit')*dt
            ngpair=pair.get(nearest['id']) if nearest else None
            if ngpair:
                bn[role+'_gun_pair_seconds']+=dt;bn[role+'_gun_commit_seconds']+=(ngpair['mode']=='commit')*dt
                ex=exposure_by_mode[(role,ngpair['mode'])];ex['seconds']+=dt;ex['inside_seconds']+=inside*dt;ex['no_legal_seconds']+=(inside and not can_reach)*dt
                ex['nearest_distance_seconds']+=dist(u,nearest)*dt
            v=(post[uid]['x']-u['x'],post[uid]['y']-u['y'])
            if math.hypot(*v)/dt>=1:
                if uid in last_vectors:
                    lv=last_vectors[uid];un['physical_reversals']+=v[0]*lv[0]+v[1]*lv[1]<0;un['displacement_pairs']+=1
                last_vectors[uid]=v
            else: last_vectors.pop(uid,None)
            # Difference of consecutive pre-integration captures equals the preceding tick's phase increment.
            if previous_capture and uid in previous_capture:
                pc=previous_capture[uid]; rate=(c['state']-pc['state'])/dt
                un['derivative_samples']+=1;un['abs_rate_sum']+=abs(rate);un['pressure_sum']+=pc['pressure'];un['abs_pressure_sum']+=abs(pc['pressure'])
                un['pressure_ge_abs_omega']+=abs(pc['pressure'])>=abs(pc['rate'])
                for threshold in (.05,.1,.2):un['locked'][str(threshold)]+=abs(rate)<threshold
                locked=abs(rate)<.1
                un['locked_pressure_sum']+=pc['pressure'] if locked else 0
                un['locked_abs_pressure_sum']+=abs(pc['pressure']) if locked else 0
                un['rotating_abs_pressure_sum']+=abs(pc['pressure']) if not locked else 0
                pb=bins[int((prev['t']-dt+1e-8)//2)]
                pb[role+'_phase_seconds']+=dt;pb[role+'_locked_seconds']+=locked*dt;pb[role+'_abs_phase_rate_seconds']+=abs(rate)*dt
                pb[role+'_pressure_seconds']+=pc['pressure']*dt;pb[role+'_abs_pressure_seconds']+=abs(pc['pressure'])*dt
                pb[role+'_abs_pressure_ge_abs_rate_seconds']+=(abs(pc['pressure'])>=abs(pc['rate']))*dt
                last_phase_rate[uid]=dict(abs_derivative=abs(rate),P=pc['pressure'],abs_omega=abs(pc['rate']),
                                           interval_ends_s=prev['t'],locked_at_point1=locked)
            if not post[uid]['alive']:
                death=dict(id=uid,role=role,time_s=st['t'],killer_id=None,killer_role=None,distance_to_killer_px=None,
                    pair_mode_toward_killer=None,killer_unavailable_reason='No exported lethal attacker; target is not killer',
                    nearest_enemy_gun_id=nearest['id'] if nearest else None,
                    distance_to_nearest_enemy_gun_px=dist(u,nearest) if nearest else None,
                    post_step_distance_to_same_gun_px=dist(post[uid],post[nearest['id']]) if nearest else None,
                    inside_any_enemy_gun_band=inside,inside_nearest_enemy_gun_band=legal(nearest,u) if nearest else False,
                    legal_set_nonempty=can_reach,commitment=d['c'],unit_intent_proxy_mode='commit' if mode else 'escape',
                    mode_toward_nearest_gun=ngpair['mode'] if ngpair else 'kite_or_no_pair',
                    phase_state_pre=c['state'],P=c['pressure'],abs_role_rate=abs(c['rate']),
                    previous_interval_phase_rate=last_phase_rate.get(uid),
                    enemy_non_guns_alive=sum(e['role']!='artillery' for e in enemies),
                    pre_step_xy=[u['x'],u['y']],post_step_xy=[post[uid]['x'],post[uid]['y']])
                deaths.append(death)
        for e in enemies:
            if e['role']=='artillery' and not post[e['id']]['alive']: guns[e['id']]['death_time_s']=st['t']
        if tick%6==0 or not any(u['alive'] and u['team']==0 for u in post.values()) or not any(u['alive'] and u['team']==1 for u in post.values()):
            frames.append([round(st['t'],6),[[u['id'],u['team'],ROLES.index(u['role']),round(u['x']),round(u['y']),round(u['hp']/u['debug']['maxhp'],3),
                u['target'] if u['target'] is not None else -1,
                round(cs[u['id']]['state']%(2*math.pi),3) if rec['arm']=='resonator' and u['id'] in cs else round(cs[u['id']]['state'],3) if u['id'] in cs else None,
                round(ds[u['id']]['c'],3) if u['id'] in ds else None] for u in post.values() if u['alive']]])
        # Every 2 s survivor snapshot. Terminated fights carry their actual terminal survivors, never invented deaths.
        if tick%60==0:samples[tick//60]={f'{s}_{r}':sum(u['alive'] and u['team']==s and u['role']==r for u in post.values()) for s in (0,1) for r in ROLES}
        prev=st;previous_capture=cs
    terminal=None
    for row in rows(rec['trace_files']):
        if 'state' in row:
            if pending is not None:consume(pending,diag,cap)
            pending=row['state'];diag=cap=None
        elif row.get('decisionDiagnostics'):
            assert diag is None;diag=row
        elif row.get('capture'):
            assert cap is None;cap=row
        else: terminal=row
    consume(pending,diag,cap)
    assert terminal==rec['summary']
    end={f'{s}_{r}':sum(u['alive'] and u['team']==s and u['role']==r for u in prev['units']) for s in (0,1) for r in ROLES}
    assert sum(end['0_'+r] for r in ROLES)==terminal['survivors']
    assert sum(end['1_'+r] for r in ROLES)==terminal['enemySurvivors']
    assert len(deaths)==50-terminal['survivors']
    assert sum(g['death_time_s'] is None for g in guns.values())==terminal['artilleryAlive'][1]
    for s in range(1,76):
        if s not in samples:
            assert s*2>prev['t']-1e-8;samples[s]=end
    for u in units.values():
        n=u['derivative_samples'];lk=u['locked']['0.1'];rt=n-lk
        u['reversals_per_unit_minute']=60*u['physical_reversals']/u['alive_seconds']
        u['state_stationary_fraction_by_threshold']={k:v/n if n else None for k,v in u['locked'].items()}
        u['state_derivative_seconds']=n/30;u['unobserved_derivative_seconds']=u['alive_seconds']-n/30
        u['mean_abs_state_rate']=u['abs_rate_sum']/n if n else None
        u['mean_P']=u['pressure_sum']/n if n else None;u['mean_abs_P']=u['abs_pressure_sum']/n if n else None
        u['fraction_abs_P_ge_abs_role_rate']=u['pressure_ge_abs_omega']/n if n else None
        u['mean_P_while_stationary']=u['locked_pressure_sum']/lk if lk else None
        u['mean_abs_P_while_stationary']=u['locked_abs_pressure_sum']/lk if lk else None
        u['mean_abs_P_while_rotating']=u['rotating_abs_pressure_sum']/rt if rt else None
        u['phase_lock_applicable']=rec['arm']=='resonator'
    result=dict(id=rec['id'],pair=rec['pair'],cluster=rec['cluster'],orientation=rec['orientation'],arm=rec['arm'],head=rec['head'],
                S=terminal['survivors']-terminal['enemySurvivors'],terminal=terminal,end_roles=end,
                enemy_non_gun_clear_time_s=non_gun_clear,deaths=deaths,enemy_guns=list(guns.values()),units=list(units.values()),
                exposure_by_nearest_gun_mode=[dict(role=r,mode=m,**v) for (r,m),v in exposure_by_mode.items()],
                raw_bins={str(k):dict(v) for k,v in bins.items()},survivor_snapshots={str(k):v for k,v in samples.items()})
    replay=dict(name=rec['arm']+'_vs_'+rec['head'],arm=rec['arm'],opponent=rec['head'],
        source_fight_id=rec['id'],summary={k:terminal[k] for k in ('survivors','enemySurvivors','t','crossTeamDealt','crossTeamTaken')},
        left_at_end={f'team{s}_{r}':end[f'{s}_{r}'] for s in (0,1) for r in ROLES},frames=frames)
    return result,replay


def aggregate(fights):
    clusters=[mean([f['S'] for f in fights if f['cluster']==c]) for c in range(10)]
    result=dict(fights=20,seed_clusters=10,S_cluster=stat(clusters),timeouts=sum(f['terminal']['t']>=150-1e-7 for f in fights),
        own_eliminations=sum(f['terminal']['survivors']==0 for f in fights),enemy_eliminations=sum(f['terminal']['enemySurvivors']==0 for f in fights),
        mean_terminal_s=mean([f['terminal']['t'] for f in fights]),end_role_means={k:mean([f['end_roles'][k] for f in fights]) for k in fights[0]['end_roles']},
        mean_cross_team_dealt=mean([f['terminal']['crossTeamDealt'][0] for f in fights]),
        mean_cross_team_taken=mean([f['terminal']['crossTeamTaken'][0] for f in fights]),roles={})
    series=[]
    for b in range(75):
        summed=collections.Counter()
        for f in fights:summed.update(f['raw_bins'].get(str(b),{}))
        item=dict(start_s=b*2,end_s=(b+1)*2,observed_fight_seconds=summed['fight_seconds'],
            survivor_means_at_bin_end={k:mean([f['survivor_snapshots'][str(b+1)][k] for f in fights]) for k in fights[0]['end_roles']},roles={})
        for r in ROLES:
            n=summed[r+'_unit_seconds'];pn=summed[r+'_phase_seconds']
            def fraction(k,den=n):return summed[r+'_'+k]/den if den else None
            item['roles'][r]=dict(unit_seconds=n,mean_commitment=fraction('c_seconds'),
                fraction_intent_commit=fraction('intent_commit_seconds'),fraction_inside_gun_band=fraction('inside_gun_seconds'),
                fraction_legal_set_nonempty=fraction('legal_seconds'),fraction_inside_gun_no_legal=fraction('inside_gun_no_legal_seconds'),
                fraction_reference_pair_commit=fraction('reference_commit_seconds',summed[r+'_reference_mode_seconds']),
                reference_mode_seconds=summed[r+'_reference_mode_seconds'],fraction_nearest_gun_pair_commit=fraction('gun_commit_seconds',summed[r+'_gun_pair_seconds']),
                gun_pair_seconds=summed[r+'_gun_pair_seconds'],fraction_all_pairs_commit=fraction('pair_commit_seconds',summed[r+'_pair_seconds']),
                mean_nearest_gun_distance_px=fraction('gun_distance_seconds',summed[r+'_gun_present_seconds']),
                state_stationary_fraction=fraction('locked_seconds',pn),mean_abs_state_rate=fraction('abs_phase_rate_seconds',pn),
                mean_P=fraction('pressure_seconds',pn),mean_abs_P=fraction('abs_pressure_seconds',pn),
                fraction_abs_P_ge_abs_role_rate=fraction('abs_pressure_ge_abs_rate_seconds',pn),phase_seconds=pn)
        series.append(item)
    result['time_series_2s']=series
    for role in ROLES:
        us=[u for f in fights for u in f['units'] if u['role']==role]
        ds=[d for f in fights for d in f['deaths'] if d['role']==role];n=len(ds)
        secs=sum(u['alive_seconds'] for u in us);ns=sum(u['derivative_samples'] for u in us)
        rolebins=collections.Counter()
        for f in fights:
            for v in f['raw_bins'].values():rolebins.update(v)
        def frac(k):return rolebins[role+'_'+k]/secs
        result['roles'][role]=dict(deaths=n,death_time=stat([d['time_s'] for d in ds]),
            death_nearest_gun_distance_px=stat([d['distance_to_nearest_enemy_gun_px'] for d in ds if d['distance_to_nearest_enemy_gun_px'] is not None]),
            death_commitment=stat([d['commitment'] for d in ds]),
            deaths_inside_gun_band=sum(d['inside_any_enemy_gun_band'] for d in ds),
            deaths_no_legal_set=sum(not d['legal_set_nonempty'] for d in ds),
            deaths_inside_gun_no_legal=sum(d['inside_any_enemy_gun_band'] and not d['legal_set_nonempty'] for d in ds),
            deaths_enemy_guns_only=sum(d['enemy_non_guns_alive']==0 for d in ds),
            death_nearest_gun_modes=dict(collections.Counter(d['mode_toward_nearest_gun'] for d in ds)),
            death_intent_modes=dict(collections.Counter(d['unit_intent_proxy_mode'] for d in ds)),
            alive_unit_seconds=secs,physical_reversals=sum(u['physical_reversals'] for u in us),
            physical_reversals_per_unit_minute=60*sum(u['physical_reversals'] for u in us)/secs,
            pair_mode_changes_per_unit_minute=60*sum(u['pair_mode_changes'] for u in us)/secs,
            stationary_fraction_thresholds={str(t):sum(u['locked'][str(t)] for u in us)/ns if ns else None for t in (.05,.1,.2)},
            mean_abs_state_rate=sum(u['abs_rate_sum'] for u in us)/ns if ns else None,
            phase_lock_applicable=fights[0]['arm']=='resonator',fraction_inside_gun_band=frac('inside_gun_seconds'),
            fraction_inside_gun_no_legal=frac('inside_gun_no_legal_seconds'),mean_commitment=frac('c_seconds'),fraction_intent_commit=frac('intent_commit_seconds'))
    result['gun_death_times']=stat([g['death_time_s'] for f in fights for g in f['enemy_guns'] if g['death_time_s'] is not None])
    result['gun_deaths']=result['gun_death_times']['n'];result['gun_survived_censored']=200-result['gun_deaths']
    result['enemy_non_gun_clear_times']=stat([f['enemy_non_gun_clear_time_s'] for f in fights if f['enemy_non_gun_clear_time_s'] is not None])
    result['death_times']=stat([d['time_s'] for f in fights for d in f['deaths']])
    result['deaths_after_60s']=sum(d['time_s']>=60 for f in fights for d in f['deaths'])
    result['deaths_enemy_guns_only']=sum(d['enemy_non_guns_alive']==0 for f in fights for d in f['deaths'])
    result['deaths_total']=sum(len(f['deaths']) for f in fights)
    return result


def main():
    start=time.time();awake=time.monotonic();pins()
    recs=json.loads((HERE/'FIGHTS.json').read_text());assert len(recs)==60
    expected={(p,c,o) for p in range(3) for c in range(10) for o in (0,1)}
    assert {(r['pair'],r['cluster'],r['orientation']) for r in recs}==expected
    all_fights=[];replays=[]
    for rec in recs:
        f,replay=analyze_fight(rec);all_fights.append(f)
        if rec['cluster']==0 and rec['orientation']==0: replays.append(replay)
        write(HERE/(rec['id']+'_SUMMARY.json'),f)
        print(json.dumps(dict(analyzed=rec['id'],S=f['S'],deaths=len(f['deaths']))),flush=True)
    endpoints={'|'.join(PAIRS[p]):aggregate([f for f in all_fights if f['pair']==p]) for p in range(3)}
    deltas=[mean([f['S'] for f in all_fights if f['pair']==1 and f['cluster']==c])-mean([f['S'] for f in all_fights if f['pair']==0 and f['cluster']==c]) for c in range(10)]
    summary=dict(status='DESCRIPTIVE_DEVELOPMENT_ONLY',endpoints=endpoints,paired_morale_minus_resonator_regular=stat(deltas),
                 metrics_complete_except_killer_attribution=True,killer_attribution='not_run: absent from unchanged original v5 output schema',
                 phase_rate_scope='unwrapped pre-integration capture differences; previous tick P/rate; final lethal/terminal integration excluded',
                 survivor_series_scope='mean of all 20 fights; actual terminal survivors carried to 150 s after termination',
                 exposure_series_scope='time weighted living own units during observed active fight time only',
                 lock_threshold_rad_s=.1,lock_sensitivity_rad_s=[.05,.2],locking_for_morale='not applicable: stationary scalar is reported, no phase',
                 death_geometry_scope='pre-step last-live geometry; c and pair modes applied in lethal tick; post distance also supplied',
                 elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake)
    write(HERE/'SUMMARY.json',summary)
    viz=CPP.parent/'viz_0g'; target=viz/'v5_trace_diagnostic_20261007';target.mkdir(exist_ok=True)
    write(target/'replays_v5.json',dict(note='Predeclared cluster 0 orientation 0; selected v5 B knobs; descriptive only; phase is pre-integration, c post-integration',
         width=1400,height=800,role_codes={r:i for i,r in enumerate(ROLES)},unit_fields=['id','team','role','x','y','hp_fraction','target','phase_or_morale','commitment'],fights=replays))
    inventory=[dict(path=str(p.relative_to(REPO)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(RAW.rglob('*')) if p.is_file()]
    assert all(p['bytes']<45_000_000 for p in inventory)
    write(HERE/'RAW_FILES_OUTSIDE_GIT.json',dict(policy='All original traces, request/seed/use files stay local. Every compressed chunk <45 MB.',files=inventory))
    write(HERE/'VERIFICATION.json',dict(status='PASS_WITH_TELEMETRY_LIMITATION',combat_executions_by_analysis=0,
        analyzed_fights=60,allocation_complete=True,all_ticks_reconstructed=True,terminal_survivors_and_guns_and_deaths_match=True,
        original_runtime_pins_verified=109,all_raw_files_below_45_MB=True,killer_attribution_available=False,
        elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake))

if __name__=='__main__':main()
