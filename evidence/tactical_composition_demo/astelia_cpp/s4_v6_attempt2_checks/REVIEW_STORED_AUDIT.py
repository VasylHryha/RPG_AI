"""Independent stdlib-only stored evidence recount. No project imports or execution."""
import collections
import gzip
import hashlib
import itertools
import json
import math
import pathlib
import statistics

CHECKS = pathlib.Path(__file__).resolve().parent
ROOT = CHECKS.parent
REPO = ROOT.parents[2]
OUT = ROOT / 's4_v6_development_20261007_025024'
def read(p): return json.loads(p.read_text())
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''): h.update(b)
    return h.hexdigest()
def encoded(v): return json.dumps(v, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()
def need(v, msg):
    if not v: raise ValueError(msg)
def close(a, b): return abs(a-b) <= 1e-11 * max(1, abs(a), abs(b))
def matching(a, b, msg):
    if isinstance(a, dict):
        need(set(a)==set(b), msg+' keys')
        for k in a: matching(a[k], b[k], msg+'/'+k)
    elif isinstance(a, (list, tuple)):
        need(len(a)==len(b), msg+' length')
        for x,y in zip(a,b): matching(x,y,msg)
    elif isinstance(a,float): need(close(a,b),msg)
    else: need(a==b,msg)

COMMON = dict(K=(0,5), K_t=(0,5), kappa=(0,50), beta=(0,3), G=(0,5), w=(0,3), f_c=(.3,1), m_k=(.2,1), lambda_th=(0,3))
BOUNDS = dict(resonator=dict(COMMON,mu=(-2,2),omega_ranged=(-2,2)), morale=dict(COMMON,lambda_melee=(0,2),lambda_ranged=(0,2)), pushpull=dict(G=(0,5),f_c=(.3,1),m_k=(.2,1)))
ARMS = (*BOUNDS, 'nearest')
decl = read(ROOT/'S4_V6_ATTEMPT2_SEEDS.json')
logs = {(stage,arm):read(OUT/f'{stage}_{arm}_tuning.json') for stage in ('A','B') for arm in BOUNDS}
ledger = read(OUT/'s4_seeds.json')
summary = read(OUT/'summary.json')
validations = {stage:read(OUT/f'{stage}_validation.json') for stage in ('A','B')}

def expected():
    for stage in ('A','B'):
        for arm in BOUNDS:
            log=logs[stage,arm]
            need(len(log['generations'])==16,'generation count')
            candidates=[('initial',log['initial_knobs'])]
            for g,gen in enumerate(log['generations']):
                need(gen['generation']==g and len(gen['candidates'])==16,'generation/population order')
                for i,c in enumerate(gen['candidates']):
                    need(c['index']==i,'candidate order')
                    normalized=c['normalized']
                    need(len(normalized)==len(BOUNDS[arm]),'normalized dimensions')
                    need(all(math.isfinite(v) and 0<=v<=1 for v in normalized),'normalized bounds')
                    knobs={k:lo+x*(hi-lo) for x,(k,(lo,hi)) in zip(normalized,BOUNDS[arm].items())}
                    need(knobs==c['knobs'],'normalized knobs')
                    candidates.append((f'{g}:{i}',c['knobs']))
            for tag,params in candidates:
                for head,seed,setting in decl['panels'][stage]['tuning']:
                    for swap in (False,True):
                        yield stage,'tuning',tag,dict(arm=arm,params=params,opponent=head,seed=seed,setting=setting,swapSides=swap,skeleton='v6',endCounts=True)
        for arm in ARMS:
            for head,seed,setting in decl['panels'][stage]['validation']:
                for swap in (False,True):
                    yield stage,'validation','best',dict(arm=arm,params=validations[stage]['knobs'].get(arm,{}),opponent=head,seed=seed,setting=setting,swapSides=swap,skeleton='v6',endCounts=True)

def request(s):
    melee=s['setting']=='s4_melee10'
    return dict(trace=False,debug=False,mode='alone',opponent='alone',s3=True,diagnostics=False,
                options=dict(seed=s['seed'],rules='game',scenario='mirror',sandboxAbilities=False,perception=False,duration=150,dt=1/30,
                             army=dict(melee=10,ranged=0 if melee else 30,artillery=0 if melee else 10),swapSides=s['swapSides'],
                             ai=[dict(controller=s['arm'],params=s['params'],skeleton='v6'),dict(level=s['opponent'])]),endCounts=True)

scores=collections.defaultdict(lambda:collections.defaultdict(dict))
validation_rows=collections.defaultdict(list)
counts=collections.Counter()
diag=collections.defaultdict(lambda:dict(samples=0,low=0,rates=0,rate_sum=0,retries=0,numerical_failure_ticks=0))
all_diag=collections.Counter()
with gzip.open(OUT/'fights.jsonl.gz','rt') as stream:
    for n,(line,ex) in enumerate(itertools.zip_longest(stream,expected()),1):
        need(line is not None and ex is not None,'raw planned count/order')
        row=json.loads(line); stage,split,tag,s=ex
        need((row['stage'],row['split'],row['candidate'],row['spec'])==(stage,split,tag,s),'raw planned row '+str(n))
        req=request(s); need(row['request']==req,'request '+str(n))
        need(row['cache_key']==hashlib.sha256(encoded(req)).hexdigest(),'cache digest')
        need(row['cache_hit'] is False,'all fights fresh')
        need(ledger['uses'][n-1]==dict(stage=stage,split=split,candidate=tag,**s,cache_hit=False,cache_key=row['cache_key']),'raw ledger')
        val=row['summary']
        need(val['controllerStatus']=='completed' and val['controllerFailures']==[0,0] and not row.get('failure'),'failure-free scored row')
        need(all(not row['metrics'][k] for k in ('forks','search_calls','artillery_rollouts')),'planner work')
        need(row['S']==val['survivors']-val['enemySurvivors'],'score')
        need(row['D']==val['crossTeamDealt'][0]-val['crossTeamTaken'][0],'damage score')
        need(0<=val['survivors']<=(10 if stage=='A' else 50) and 0<=val['enemySurvivors']<=(10 if stage=='A' else 50),'survivor bounds')
        # Historical native final-time schema permits the final complete tick.
        need(0<=val['t']<=150+1/30+1e-9,'fight time bounds')
        key=(stage,s['arm'],split,tag); battle=(s['opponent'],s['seed'],s['setting'])
        need(s['swapSides'] not in scores[key][battle],'duplicate orientation')
        scores[key][battle][s['swapSides']]=row['S'];counts[stage,s['arm'],split,s['opponent']]+=1
        if split=='validation': validation_rows[stage,s['arm'],s['opponent']].append(val)
        if s['arm']=='resonator':
            d=val['complexDiagnostics']
            need(d['side']==0 and d['mu']==s['params']['mu'] and d['omega_ranged']==s['params']['omega_ranged'] and d['omega_melee']==0,'diagnostic knobs')
            need(d['argValidityThreshold']==.2,'amplitude threshold')
            need(0<=d['lowAmplitudeSamples']<=d['samples'] and 0<=d['argRateSamples']<=d['samples']-d['lowAmplitudeSamples'],'amplitude denominators')
            for k in ('samples','lowAmplitudeSamples','argRateSamples','retryCount','numericalFailureTicks'):
                need(type(d[k]) in (int,float) and math.isfinite(d[k]) and d[k]>=0 and int(d[k])==d[k],'diagnostic counter')
            if d['samples']: need(close(d['fractionBelow02'],d['lowAmplitudeSamples']/d['samples']),'low fraction')
            else: need(d['fractionBelow02'] is None,'zero denominator fraction')
            need(math.isfinite(d['argRateAbsSum']) and d['argRateAbsSum']>=0,'arg rate sum')
            if d['argRateSamples']: need(d['argRateNullReason'] is None and close(d['argRateAbsMean'],d['argRateAbsSum']/d['argRateSamples']),'arg rate mean')
            else: need(d['argRateAbsMean'] is None and d['argRateAbsSum']==0 and d['argRateNullReason']=='no_consecutive_valid_endpoints','arg rate null')
            need(d['numericalFailureTicks']==0 and d['retryCount']<=round(val['t']*30),'numerical ticks')
            all_diag['retry_count']+=d['retryCount'];all_diag['failure_ticks']+=d['numericalFailureTicks']
            if split=='validation':
                a=diag[stage,s['opponent']]
                for k,dk in [('samples','samples'),('low','lowAmplitudeSamples'),('rates','argRateSamples'),('rate_sum','argRateAbsSum'),('retries','retryCount'),('numerical_failure_ticks','numericalFailureTicks')]:a[k]+=d[dk]
need(n==60996==len(ledger['uses']),'raw/ledger coverage')
need(summary['executed_fights']==60996 and summary['cache_hits']==0,'summary fresh accounting')
paired={}
for key,battles in scores.items():
    need(all(set(pair)=={False,True} for pair in battles.values()),'pair coverage')
    paired[key]={b:statistics.mean(pair.values()) for b,pair in battles.items()}
def pick(stage,v):
    novice=statistics.mean(x for b,x in v.items() if b[0]=='novice')
    regular=None if stage=='A' else statistics.mean(x for b,x in v.items() if b[0]=='regular')
    eligible=None if stage=='A' else novice>=0
    return dict(novice_mean=novice,regular_mean=regular,eligible=eligible,rank=[novice] if stage=='A' else [int(eligible),regular],objective=-novice if stage=='A' else -regular+(0 if eligible else 101))
def log_scores(v):return {json.dumps(b):x for b,x in v.items()}
selected={}
generation_count=candidate_count=0
for stage in ('A','B'):
    for arm in BOUNDS:
        log=logs[stage,arm];initial=log['initial_knobs']
        expected_initial={k:(lo+hi)/2 for k,(lo,hi) in BOUNDS[arm].items()} if stage=='A' else selected[arm]
        need(initial==expected_initial,'initial midpoint/inherited incumbent')
        v=paired[stage,arm,'tuning','initial'];need(log['initial_scores']==log_scores(v),'initial scores')
        best=initial;choice=pick(stage,v)
        for g in log['generations']:
            generation_count+=1
            for c in g['candidates']:
                candidate_count+=1
                v=paired[stage,arm,'tuning',f"{g['generation']}:{c['index']}"]
                need(c['scores']==log_scores(v),'candidate scores')
                p=pick(stage,v);matching(p,c['selection'],'candidate selection')
                take=p['rank']>choice['rank'];need(c['accepted_as_best']==take,'strict incumbent and tie')
                need(c['fresh_fights']==38 and c['cache_hits']==0,'candidate accounting')
                if take:best=c['knobs'];choice=p
            need(g['best']==best,'generation incumbent');matching(g['best_selection'],choice,'generation selection')
        need(log['best']==best,'retained winner');matching(log['best_selection'],choice,'retained selection')
        selected[arm]=best
        need(read(OUT/f'{stage}_{arm}_partial.json')['best']==best,'final partial winner')
    need(read(OUT/f'{stage}_best.json')==selected==validations[stage]['knobs'],'stage/validation winner')
    need(validations[stage]['panel']==decl['panels'][stage]['validation'],'common panel')
need(generation_count==96 and candidate_count==1536,'generation/candidate count')
need(selected==summary['best'],'final summary knobs')
for arm in BOUNDS:matching(summary['selections'][arm],logs['B',arm]['best_selection'],'summary selection')
endpoints=[]
for stage in ('A','B'):
    need(set(validations[stage]['results'])==set(ARMS),'all four arms')
    for arm in ARMS:
        expected_heads=('novice',) if stage=='A' else ('novice','regular')
        need(set(validations[stage]['results'][arm])=={('s4_melee10' if stage=='A' else 's4_full_head')+'|'+h for h in expected_heads},'endpoint heads')
        actual=paired[stage,arm,'validation','best']
        need(set(actual)=={tuple(b) for b in decl['panels'][stage]['validation']},'all-arm common fresh validation')
        for endpoint,data in validations[stage]['results'][arm].items():
            setting,head=endpoint.split('|');v={b:x for b,x in actual.items() if b[0]==head}
            need(data['scores']==log_scores(v),'validation scores')
            mean=statistics.mean(v.values());sd=statistics.stdev(v.values());se=sd/math.sqrt(len(v))
            matching(data['stats'],dict(n=100,mean=mean,sd=sd,se=se,descriptive_normal_95=[mean-1.96*se,mean+1.96*se]),'endpoint stats')
            vr=validation_rows[stage,arm,head];need(len(vr)==200,'orientation endpoint count')
            own=[x['t'] for x in vr if x['survivors']==0];enemy=[x['t'] for x in vr if x['enemySurvivors']==0]
            # Recount all stored descriptive fields without runner helpers.
            desc=dict(fights=200,own_guns_alive_mean=sum(x['artilleryAlive'][0] for x in vr)/200,enemy_guns_alive_mean=sum(x['artilleryAlive'][1] for x in vr)/200,
                timeouts=sum(x['survivors']>0 and x['enemySurvivors']>0 for x in vr),damage_dealt_mean=sum(x['crossTeamDealt'][0] for x in vr)/200,
                damage_taken_mean=sum(x['crossTeamTaken'][0] for x in vr)/200,own_eliminations=len(own),own_elimination_time_mean=sum(own)/len(own) if own else None,
                enemy_eliminations=len(enemy),enemy_elimination_time_mean=sum(enemy)/len(enemy) if enemy else None,mean_termination_time=sum(x['t'] for x in vr)/200,
                elimination_time_policy='conditional on elimination; timeouts censored, no imputation')
            matching(data['descriptive'],desc,'descriptives')
            endpoints.append(dict(stage=stage,arm=arm,head=head,mean=mean,sd=sd,se=se,**desc))
need(len(endpoints)==12,'all endpoint coverage')
for stage in ('A','B'):
    gate=summary['gates'][stage];m={e['head']:e['mean'] for e in endpoints if e['stage']==stage and e['arm']=='resonator'}
    need(gate['novice_mean']==m['novice'] and gate['novice_validation_pass']==(m['novice']>0),'strict novice')
    if stage=='B':need(gate['regular_mean']==m['regular'] and gate['regular_progress_pass']==(m['regular']>-6.025) and gate['beats_regular_in_development']==(m['regular']>0 and m['novice']>0),'strict regular')
    need(gate['failure_free'] and gate['numerical_failures']==0 and not gate['C_authorized'] and not gate['S5_run_authorized'],'gated scope')
need(summary['status']=='READY_TO_DRAFT_S5' and summary['gates']['A']['status']=='CONTINUE' and summary['gates']['B']['status']=='READY_TO_DRAFT_S5','final gate status')
need(summary['stages_completed']==['A','B'] and summary['development_only'],'development scope')
need(all(summary[x]['status']=='not_run' for x in ('C','P2','P3')),'not-run scope')
need(summary['budgets']=={arm:19532 for arm in BOUNDS},'budget receipt')
for stage in ('A','B'):
    for arm in BOUNDS:need(sum(v for (st,a,sp,h),v in counts.items() if (st,a,sp)==(stage,arm,'tuning'))==9766,'raw tuning budget')
need(summary['selected_mu']==selected['resonator']['mu'] and summary['selected_omega']==dict(melee=0,ranged=selected['resonator']['omega_ranged']),'selected rates')
omega=read(OUT/'selected_omega.json');need(omega['mu']==summary['selected_mu'] and omega['omega']==summary['selected_omega'],'omega diagnostic receipt')
for entry in read(CHECKS/'REPORT_AUDIT.json')['amplitude_diagnostics']: matching({k:v for k,v in entry.items() if k not in ('stage','head')},diag[entry['stage'],entry['head']],'amplitude aggregate')
runtime=read(OUT/'run_identity.json')['code_hashes']
need(all(sha(ROOT/p)==h for p,h in runtime.items()),'runtime hashes')
preserved=read(CHECKS/'PRESERVATION_BEFORE.json')
need(all(sha(REPO/p)==h for p,h in preserved.items()),'preservation')
inventory=read(CHECKS/'RAW_FILES_LOCAL.json')
need(all(sha(ROOT/e['path'])==e['sha256'] and (ROOT/e['path']).stat().st_size==e['bytes'] for e in inventory['raw_artifacts']),'raw inventory')
need(ledger['declaration_sha256']==sha(ROOT/'S4_V6_ATTEMPT2_SEEDS.json'),'ledger declaration')
panel_seeds={b[1] for pane in decl['panels'].values() for panel in pane.values() for b in panel}
prior=read(ROOT/'S4_V6_SEEDS.json');old_seeds={b[1] for pane in prior['panels'].values() for panel in pane.values() for b in panel}
need(len(panel_seeds)==238 and not panel_seeds&set(decl['prior_seed_inventory']) and old_seeds<=set(decl['prior_seed_inventory']),'fresh/consumed seeds')
loads=[json.loads(l) for l in (CHECKS/'LOAD_SAMPLES.jsonl').read_text().splitlines()]
ls=read(CHECKS/'LOAD_SUMMARY.json');need(ls['samples']==len(loads),'load count')
matching([ls['one_minute_min'],ls['one_minute_mean'],ls['one_minute_max']],[min(x['load_average'][0] for x in loads),statistics.mean(x['load_average'][0] for x in loads),max(x['load_average'][0] for x in loads)],'load values')
timing=read(CHECKS/'SUPERVISOR_TIMING.json');need(timing['returncode']==0 and timing['caffeinate'],'process completion')
launch=read(CHECKS/'LAUNCH.json');need(launch['workers']==10 and launch['command'][:3]==['/usr/bin/caffeinate','-i','-s'],'launch resources')
report=ROOT/'S4_V6_DEVELOPMENT_REPORT_ATTEMPT2.md'
receipt=dict(status='PASS',stored_only=True,project_imports=0,native_processes=0,combat_fights_executed=0,optimizers_executed=0,tests_executed=0,
    report_sha256=sha(report),raw_sha256=sha(OUT/'fights.jsonl.gz'),rows=n,generations=generation_count,candidates=candidate_count,
    endpoints=endpoints,amplitude_validation=[dict(stage=k[0],head=k[1],**d) for k,d in sorted(diag.items())],all_resonator_diagnostics=dict(all_diag),
    runtime_pins=len(runtime),preservation_files=len(preserved),raw_inventory_files=len(inventory['raw_artifacts']),elapsed_minutes=timing['elapsed_seconds']/60,
    awake_minutes=timing['awake_seconds']/60,load=ls,historical_differences=dict(resonator_regular=8.025-(-6.025),resonator_novice=5.19-5.6,morale_regular=8.035-9.53))
(CHECKS/'REVIEW_STORED_AUDIT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('endpoints','amplitude_validation','load')},indent=2))
