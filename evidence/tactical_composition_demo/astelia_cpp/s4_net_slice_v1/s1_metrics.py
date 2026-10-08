"""Pilot-only paired planning diagnostics; no tactical verdict from pilot outcomes."""
from collections import Counter, defaultdict
import bisect
import math
import statistics
from s0_analysis import distribution


def gamma_cdf(a,x):
    if x<=0:return 0.
    factor=math.exp(-x+a*math.log(x)-math.lgamma(a))
    if x<a+1:
        term=1/a;total=term
        for n in range(1,10000):
            term*=x/(a+n);total+=term
            if abs(term)<abs(total)*1e-14:break
        return total*factor
    b=x+1-a;c=1e300;d=1/b;h=d
    for n in range(1,10000):
        an=-n*(n-a);b+=2;d=an*d+b
        if abs(d)<1e-300:d=1e-300
        c=b+an/c
        if abs(c)<1e-300:c=1e-300
        d=1/d;delta=d*c;h*=delta
        if abs(delta-1)<1e-14:break
    return 1-factor*h


def chi2_quantile(p,df):
    if not 0<p<1 or df<=0:raise ValueError('chi square quantile domain')
    lo=0.;hi=max(1.,float(df))
    while gamma_cdf(df/2,hi/2)<p:hi*=2
    for _ in range(100):
        mid=(lo+hi)/2
        if gamma_cdf(df/2,mid/2)<p:lo=mid
        else:hi=mid
    return (lo+hi)/2


def spread(d,reason=None):
    if reason or len(d)<2 or not all(math.isfinite(x) for x in d):return dict(status='UNRESOLVED',reason=reason or 'missing/<2 finite paired draws',pairs=len(d),mean=None if not d else statistics.mean(d))
    sd=statistics.stdev(d);mean=statistics.mean(d)
    if sd==0:return dict(status='UNUSABLE',reason='constant paired differences; MDE is not zero',pairs=len(d),mean=mean,paired_sd=sd,MDE_100=None,MDE_200=None)
    upper=sd*math.sqrt((len(d)-1)/chi2_quantile(.05,len(d)-1));z=statistics.NormalDist().inv_cdf(.975)+statistics.NormalDist().inv_cdf(.8)
    return dict(status='PLANNING_ONLY',pairs=len(d),mean=mean,paired_sd=sd,sd_upper=upper,ordinary_MDE_100=z*sd/10,ordinary_MDE_200=z*sd/math.sqrt(200),MDE_100=z*upper/10,MDE_200=z*upper/math.sqrt(200),assumption='Gaussian paired-difference planning approximation; not a guarantee of power')


def exchange(pairs):
    ka=sum(a['kills'] for a,b in pairs);kb=sum(b['kills'] for a,b in pairs);da=sum(a['deaths'] for a,b in pairs);db=sum(b['deaths'] for a,b in pairs);m=len(pairs)
    result=dict(denominators=[da,db],kills=[ka,kb],arm_ratio_of_totals=[ka/da if da else None,kb/db if db else None])
    if min(da,db)<5 or m<2:return {**result,**spread([],reason='fewer than five own deaths in either arm')}
    theta=kb/db-ka/da;pseudo=[]
    for a,b in pairs:
        if da-a['deaths']<=0 or db-b['deaths']<=0:return {**result,**spread([],reason='nonfinite delete-one denominator')}
        leave=(kb-b['kills'])/(db-b['deaths'])-(ka-a['kills'])/(da-a['deaths'])
        pseudo.append(m*theta-(m-1)*leave)
    return {**result,**spread(pseudo), 'mean':theta,'spread_method':'paired delete-one ratio-of-totals jackknife pseudovalues'}


def interpolate(trace,id,t):
    times=[q[0] for q in trace];i=bisect.bisect_left(times,t)
    if i<len(trace) and abs(times[i]-t)<1e-9:return trace[i][1].get(id)
    if i==0 or i==len(trace):return None
    left,right=trace[i-1],trace[i]
    if id not in left[1] or id not in right[1]:return None
    f=(t-left[0])/(right[0]-left[0]);a,b=left[1][id],right[1][id]
    return [a[k]+f*(b[k]-a[k]) for k in (0,1)]


def measure(frames,request):
    """Read one fight; full public position history is evaluator-side only."""
    counts=Counter();supports=[];refresh={};launches=[];trace=[];terminal=None;plans={};assignment_changed={};impacts=[];intents=[];last=0;initial=None
    for f in frames:
        if terminal is not None:raise ValueError('record after terminal')
        if f.get('terminal'):terminal=f;continue
        if f['fight']!=request['fight'] or f['tick']!=last+1:raise ValueError('identity/chronology')
        last=f['tick'];joint=f['joint']
        if joint and initial is None:initial=joint
        post=f.get('post_joint')
        if joint:trace.append((joint['t'],{u['id']:[u['x'],u['y']] for u in joint['units'] if u['hp']>0}))
        # Post-action positions are used at impact times (movement before damage).
        if post:trace.append((post['t'],{u['id']:[u['x'],u['y']] for u in post['units'] if u['hp']>0}))
        for e in f['events']:
            stage=e['stage'];v=e['value'];counts[stage]+=1
            if stage=='s1_joint':
                counts['eligible_multi']+=v['eligible']>=2;counts['command_multi']+=v['feasible']>=2;counts['changed_assignment_multi']+=v.get('changed_assignment',False)
                if v['feasible']>=2:plans[f['tick']]=[];assignment_changed[f['tick']]=bool(v.get('changed_assignment',False))
            elif stage=='s1_refresh':refresh[(e['unit'],e['cast_tick'])]=(f['tick'],v)
            elif stage=='s1_support':supports.append(v)
            elif stage=='intent':
                intents.append(v);counts['start_opportunities']+=v['start_opportunity'];counts['release_opportunities']+=v['release_opportunity'];counts['start_permissions']+=v['start'];counts['release_permissions']+=v['release']
            elif stage=='s1_rejection':counts['rejection:'+v['reason']]+=1
            elif stage=='launch':launches.append(e)
            elif stage=='shell_impact':impacts.append(e)
            elif stage=='projection':
                if v['reason']=='hold_expired_auto_release':counts['automatic_release']+=1
                if v['effective']['target']!=v['raw']['target']:counts['native_target_lock_correction']+=1
    if terminal is None or initial is None:raise ValueError('missing initial/terminal')
    # At duplicate time, use post-action snapshot; interpolate per-target only
    # between two living observations. Terminal/dead trajectories stay missing.
    unique={t:p for t,p in trace};trace=sorted(unique.items())
    miss=[];missing=Counter();patterns=defaultdict(list);response_plans=set();response_shells=set()
    for e in launches:
        patterns[e['decision_tick']].append((e['unit'],e['value']['aim']))
        item=refresh.get((e['unit'],e['cast_tick']))
        if not item:continue
        tick,v=item;native=e['value']
        if tick!=e['tick'] or abs(v['t']-native['born'])>1e-8:missing['launch_after_first_release_opportunity']+=1;continue
        pos=v['self'];focus=v['focus'];lob=v['lob'];requested=v['requested'];auto=v['autonomous'];snapped=native['aim']
        if math.dist(snapped,v['autonomous_snapped'])>v['splash']/4:response_plans.add(v['plan']);response_shells.add((e['unit'],native['born']))
        times=dict(raw=native['born']+math.dist(pos,requested)/lob,native=native['landing_at'],autonomous=native['born']+math.dist(pos,auto)/lob)
        land={k:interpolate(trace,focus,t) for k,t in times.items()}
        if any(p is None for p in land.values()):missing['terminal_dead_or_unobserved_focus_landing']+=1;continue
        raw=math.dist(requested,land['raw']);nm=math.dist(snapped,land['native']);am=math.dist(auto,land['autonomous']);shape=v['shape']
        miss.append(dict(focus=focus,gun=e['unit'],plan=v['plan'],raw_miss=raw,native_miss=nm,autonomous_miss=am,raw_difference=raw-am,native_difference=nm-am,normalized_difference=(raw-am)/v['splash'],shape_subtracted_raw_miss=math.dist([requested[k]-shape[k] for k in (0,1)],land['raw']),shape_subtracted_native_miss=math.dist([snapped[k]-shape[k] for k in (0,1)],land['native']),splash=v['splash'],times=times,points=dict(requested=requested,native=snapped,autonomous=auto),observed_focus=land))
    impact_patterns=defaultdict(list);response_impacts=0
    launch_origins={(e['unit'],e['value']['born']):e['decision_tick'] for e in launches}
    for e in impacts:
        if e['value']['source_team']!=0:continue
        response_impacts+=(e['unit'],e['value']['born']) in response_shells
        origin=launch_origins.get((e['unit'],e['value']['born']))
        if origin is not None:impact_patterns[origin].append((e['unit'],e['value']['aim'],e['value']['hits']))
    missing['commanded_casts_without_matched_launch']=len(set(refresh)-{(e['unit'],e['cast_tick']) for e in launches})
    own=[u for u in initial['units'] if u['team']==0];enemy=[u for u in initial['units'] if u['team']==1];own_guns=sum(u['role']==2 for u in own)
    unforced=[s for s in supports if not s['forced']];bad_residual=sum(s['residual']>s['splash']/4 for s in unforced);bad_snap=sum(s['snap_error']>s['splash']/4 for s in unforced)
    totals=terminal['native_shell_totals'];deaths=len(own)-terminal['own_alive'];kills=len(enemy)-terminal['enemy_alive'];clear=terminal['enemy_alive']==0 and terminal['own_alive']>0 and terminal['time']<150
    outcome='won' if terminal['strict_win'] else 'lost' if terminal['own_guns_alive']==0 else 'timeout'
    def rate(n,d):return None if not counts[d] else counts[n]/counts[d]
    fire_rates=dict(starts_per_start_opportunity=rate('cast_start','start_opportunities'),launches_per_start_opportunity=rate('launch','start_opportunities'),release_permits_per_release_opportunity=rate('release_permissions','release_opportunities'))
    own_splash_hits=sum(h['team']==0 for e in impacts if e['value']['source_team']==0 for h in e['value']['hits'])
    return dict(fight=request['fight'],outcome=outcome,outcome_definition='won: strict clear; lost: all controlled guns dead (held scaffolds excluded); otherwise timeout',fire_rates=fire_rates,own_splash_hits=own_splash_hits,deaths=deaths,gun_deaths=own_guns-terminal['own_guns_alive'],kills=kills,damage=totals['enemy_damage'],clear_time=terminal['time'],cleared=clear,death_before_clear=terminal['own_alive']==0 and terminal['enemy_alive']>0,win=terminal['strict_win'],own_roster=len(own),enemy_roster=len(enemy),enemy_hp=sum(u['maxhp'] for u in enemy),own_hp=sum(u['maxhp'] for u in own),counts=dict(counts),support=dict(unforced=len(unforced),forced=sum(s['forced'] for s in supports),center_illegal=sum(s['center_illegal'] for s in supports),bad_residual=bad_residual,bad_snap=bad_snap,snap_pass_fraction=None if not unforced else 1-bad_snap/len(unforced)),miss=miss,missing_miss=dict(missing),plans=sorted(plans),assignment_changed=assignment_changed,on_state_response_plans=sorted(response_plans),on_state_changed_physical_decisions=sum(assignment_changed.get(plan,False) for plan in response_plans),on_state_changed_impact_count=response_impacts,physical_patterns=dict(patterns),impact_patterns=dict(impact_patterns),enemy_dash_events=counts['enemy_dash'],resolved_shells=totals['resolved_shells'],friendly_damage=totals['friendly_damage'],impacts=len(impacts),damage_per_shell=None if not totals['resolved_shells'] else totals['enemy_damage']/totals['resolved_shells'],shells_per_kill=None if not kills else len(launches)/kills)


def summarize(pairs,moving):
    if len(pairs) not in (10,20):raise ValueError('complete ten or twenty paired pilots required')
    a,b=pairs[0];ledger=dict(deaths=dict(useful=.1*a['own_roster'],harm=.05*a['own_roster']),kills=dict(useful=.1*a['enemy_roster'],harm=.05*a['enemy_roster']),damage=dict(useful=.1*a['enemy_hp'],harm=.05*a['enemy_hp']),exchange=dict(useful=.1,harm=.05),clear_time=dict(useful=15,harm=None))
    axes={}
    for axis,bound in [('deaths',a['own_roster']),('kills',a['enemy_roster']),('damage',a['enemy_hp']),('clear_time',150)]:
        reason='censored/death-before-clear time is diagnostic' if axis=='clear_time' and not all(x['cleared'] for pair in pairs for x in pair) else None
        d=[y[axis]-x[axis] for x,y in pairs];v=spread(d,reason)
        sat=[max(sum(x[axis]==0 for x in arm),sum(x[axis]>=bound for x in arm))/len(pairs) for arm in zip(*pairs)]
        v['planning_harm_halfwidth']={str(n):None if not v.get('sd_upper') else 1.6448536269514722*v['sd_upper']/math.sqrt(n) for n in (100,200)};v['effect_for_80pct_point_threshold']={str(n):None if not v.get('sd_upper') else ledger[axis]['useful']+.8416212335729143*v['sd_upper']/math.sqrt(n) for n in (100,200)};v['saturation_fraction']=sat;v['informative']=v['status']=='PLANNING_ONLY' and max(sat)<=.9 and axis!='clear_time'
        axes[axis]=v
    axes['exchange']=exchange(pairs)
    axes['exchange']['informative']=axes['exchange']['status']=='PLANNING_ONLY' and all(axes[k]['informative'] for k in ('deaths','kills'))
    eligible=sum(y['counts'].get('eligible_multi',0) for x,y in pairs);commands=sum(y['counts'].get('command_multi',0) for x,y in pairs);changed=0;changed_impacts=0
    for x,y in pairs:
        for plan in y['plans']:
            # Paired actual shell points from casts originating at this decision.
            ys=y['physical_patterns'].get(plan,y['physical_patterns'].get(str(plan),[]));xs=x['physical_patterns'].get(plan,x['physical_patterns'].get(str(plan),[]))
            yi=y['impact_patterns'].get(plan,y['impact_patterns'].get(str(plan),[]));xi=x['impact_patterns'].get(plan,x['impact_patterns'].get(str(plan),[]))
            changed_impacts+=bool(yi and yi!=xi)
            if (ys and ys!=xs) or (yi and yi!=xi):changed+=1
    command_rate=commands/eligible if eligible else None;response_rate=sum(y['on_state_changed_physical_decisions'] for x,y in pairs)/commands if commands else None;assignment_rate=sum(y['counts'].get('changed_assignment_multi',0) for x,y in pairs)/commands if commands else None
    support_rows=[z for pair in pairs for z in pair];unforced=sum(z['support']['unforced'] for z in support_rows);bad_snap=sum(z['support']['bad_snap'] for z in support_rows);bad_residual=sum(z['support']['bad_residual'] for z in support_rows)
    lock_fail=sum(z['counts'].get('native_target_lock_correction',0) for z in support_rows)
    misses=[m for x,y in pairs for m in y['miss']];miss_fights=sum(bool(y['miss']) for x,y in pairs);diffs=[m['raw_difference'] for m in misses]
    wrapper_stop=(not unforced or bad_residual>0 or bad_snap/unforced>.05 or lock_fail>0)
    mean=statistics.mean(diffs) if diffs else None;miss_bad=moving and (mean is not None and mean>statistics.mean(m['splash'] for m in misses)/4)
    coverage_bad=moving and (len(misses)<20 or miss_fights<5)
    options=[]
    for primary in ('damage','kills','deaths','exchange'):
        if primary=='deaths' and a['own_roster']==12:continue # D2-10 death saturation: never promote survival.
        v=axes[primary]
        if not v['informative']:continue
        for n in (100,200):
            if v.get('MDE_'+str(n)) is not None and v['MDE_'+str(n)]<=ledger[primary]['useful']:options.append((n,primary));break
    admitted=bool(options) and command_rate is not None and command_rate>=.05 and response_rate is not None and response_rate>=.05 and assignment_rate is not None and assignment_rate>=.05 and not(wrapper_stop or miss_bad or coverage_bad)
    chosen=min(options,key=lambda v:(v[0],('damage','kills','deaths','exchange').index(v[1]))) if admitted else None
    outcome_splits={}
    for arm,index in [('T-unit-alone',0),('T-unit+wrapper',1)]:
        outcome_splits[arm]={}
        for status in ('won','lost','timeout'):
            rows=[pair[index] for pair in pairs if pair[index].get('outcome','timeout')==status]
            deaths=sum(z['deaths'] for z in rows);kills=sum(z['kills'] for z in rows)
            totals=Counter()
            for z in rows:totals.update(z['counts'])
            outcome_splits[arm][status]=dict(fights=len(rows),mean_deaths=None if not rows else deaths/len(rows),mean_gun_deaths=None if not rows else sum(z['gun_deaths'] for z in rows)/len(rows),mean_kills=None if not rows else kills/len(rows),mean_enemy_damage=None if not rows else sum(z['damage'] for z in rows)/len(rows),exchange_ratio_of_totals=None if not deaths else kills/deaths,kills=kills,deaths=deaths,fire_counts=dict(totals),starts_per_start_opportunity=None if not totals['start_opportunities'] else totals['cast_start']/totals['start_opportunities'],launches_per_start_opportunity=None if not totals['start_opportunities'] else totals['launch']/totals['start_opportunities'],release_permits_per_release_opportunity=None if not totals['release_opportunities'] else totals['release_permissions']/totals['release_opportunities'])
    return dict(pairs=len(pairs),moving=moving,axes=axes,outcome_splits=outcome_splits,outcome_split_limit='descriptive post-outcome conditioning only; admission/paired effects retain all draws',thresholds=ledger,command_rate=command_rate,physical_response_rate=response_rate,assignment_change_rate=assignment_rate,eligible_decisions=eligible,command_decisions=commands,paired_changed_shell_or_impact_decisions_diagnostic=changed,on_state_changed_shell_or_impact_decisions=sum(y['on_state_changed_physical_decisions'] for x,y in pairs),on_state_changed_impact_count=sum(y['on_state_changed_impact_count'] for x,y in pairs),changed_impact_decisions=changed_impacts,enemy_dash_events=sum(z['enemy_dash_events'] for pair in pairs for z in pair),miss=dict(observations=len(misses),represented_fights=miss_fights,mean_raw_difference_px=mean,raw_difference_px=distribution(diffs),mean_splash_normalized_difference=None if not misses else statistics.mean(m['normalized_difference'] for m in misses),raw_miss_px=distribution([m['raw_miss'] for m in misses]),native_miss_px=distribution([m['native_miss'] for m in misses]),autonomous_miss_px=distribution([m['autonomous_miss'] for m in misses]),shape_subtracted_raw_px=distribution([m['shape_subtracted_raw_miss'] for m in misses]),shape_subtracted_native_px=distribution([m['shape_subtracted_native_miss'] for m in misses]),missing=dict(sum((Counter(y['missing_miss']) for x,y in pairs),Counter()))),support=dict(unforced=unforced,bad_residual=bad_residual,bad_snap=bad_snap,lock_violations=lock_fail),admitted=admitted,primary=None if not chosen else chosen[1],final_N=None if not chosen else chosen[0],status='PILOT_CELL_ADMISSIBLE' if admitted else 'UNRESOLVED_OR_REVISE',power_limit='MDE <= useful effect plans detection of nonzero effects, not 80% probability of the full useful/CI/harm verdict; point threshold alone has ~50% power at a true effect equal to that threshold',stops=[dict(condition='Cell fails command/physical 5%, saturation or MDE_N useful threshold?',yes=not options or command_rate is None or command_rate<.05 or response_rate is None or response_rate<.05 or assignment_rate is None or assignment_rate<.05,action='Redesign pilot cells',role='drafter'),dict(condition='Any lock/nonfinite/residual failure or <95% snap support?',yes=wrapper_stop,action='Revise command wrapper',role='drafter'),dict(condition='Moving raw wrapper miss exceeds autonomous by splash/4?',yes=miss_bad,action='Revise command wrapper',role='drafter'),dict(condition='Moving finite paired misses <20 or represented fights <5?',yes=coverage_bad,action='Resolve wrapper-miss coverage before admission',role='drafter'),dict(condition='Cell lacks sealed definition/primary/threshold/allocation/N before outcome entropy?',yes=True,action='Hold outcome allocation',role='implementer')])
