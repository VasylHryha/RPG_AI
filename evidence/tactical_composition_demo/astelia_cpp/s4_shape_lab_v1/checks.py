"""Required section-3 checks; these precede every drill, not a rehearsal panel."""
import copy
import gzip
import hashlib
import json
from lab import *

def stream_hash(path):
    h=hashlib.sha256()
    with gzip.open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def observers(tag):
    with gzip.open(RAW/(tag+'.jsonl.gz'),'rt') as f:
        for line in f:
            r=json.loads(line)
            if r.get('observerV1'):yield r

def checks():
    identity()
    output=HERE/'CHECKS.json'
    if output.exists():
        c=read(output)
        if c['status']!='PASS' or c['declaration_sha256']!=sha(HERE/'DECLARATION.json'):raise RuntimeError('checks identity drift')
        print('Existing checks verified; no fights repeated')
        return c
    rows=[]
    def require(name,ok,**detail):
        rows.append(dict(name=name,pass_check=bool(ok),**detail))
        if not ok:
            write(output,dict(status='FAIL',checks=rows,declaration_sha256=sha(HERE/'DECLARATION.json')))
            raise RuntimeError('section-3 check failed: '+name)
    # The one explicit delivered-validation compatibility seed is owner-authorized.
    original=CPP/'s4_v7c/raw/validation_v7_regular_c00_o0'
    req=read(str(original)+'_request.json')[0]
    req['labScenario']=dict(sides=standard(req['options']['seed'],req['options']['swapSides']))
    row=execute('check_compatibility',req,dict(group='checks',arm='v7',purpose='owner-required byte equality'))
    require('50v50 entire output byte equality',stream_hash(RAW/'check_compatibility.jsonl.gz')==stream_hash(str(original)+'.jsonl.gz'),
            lab_stream_sha256=stream_hash(RAW/'check_compatibility.jsonl.gz'),delivered_stream_sha256=stream_hash(str(original)+'.jsonl.gz'),
            same_terminal=row['summary']==read(str(original)+'_COMPLETE.json')['summaries'][0])
    seeds=read(RAW/'SEED_LEDGER.json')['checks']
    def small(arm,enemy,seed,roles=('ranged','ranged'),xs=(600,750),duration=2):
        sides=[select(side,{r:1}) for side,r in zip(standard(seed),roles)]
        for side,x in zip(sides,xs):line(side,x)
        q=request(arm,controller(enemy),seed,sides=sides,abilities_off=False)
        q['options']['sandboxAbilities']=True
        q['options']['duration']=duration
        return q
    q=small('dummy_static','dummy_static',seeds[0])
    execute('check_dummy_static',q,dict(group='checks',arm='dummy_static'))
    obs=list(observers('check_dummy_static'));start={u[0]:(u[3],u[4]) for u in obs[0]['units']}
    require('dummy_static no damage/no launches/no movement',all(not r['damage'] and not r['launches'] and all(start[u[0]]==(u[3],u[4]) for u in r['units']) for r in obs))
    q=small('dummy_static_fire','dummy_static',seeds[1])
    execute('check_dummy_static_fire',q,dict(group='checks',arm='dummy_static_fire'))
    obs=list(observers('check_dummy_static_fire'));start={u[0]:(u[3],u[4]) for u in obs[0]['units']}
    require('dummy_static_fire attacks and never moves',any(d['sourceTeam']==0 and d['dealt']>0 for r in obs for d in r['damage']) and all(start[u[0]]==(u[3],u[4]) for r in obs for u in r['units']))
    for index,arm in enumerate(('dummy_advance','dummy_advance_fire'),2):
        q=small(arm,'dummy_static',seeds[index],roles=('ranged','artillery'),xs=(400,600),duration=1)
        execute('check_'+arm,q,dict(group='checks',arm=arm))
        obs=list(observers('check_'+arm));own0=next(u for u in obs[0]['units'] if u[1]==0);own1=next(u for u in obs[-1]['units'] if u[1]==0)
        distance=math.hypot(own1[3]-own0[3],own1[4]-own0[4])
        has_damage=any(d['sourceTeam']==0 and d['dealt']>0 for r in obs for d in r['damage'])
        require(arm+' catalog speed, gun pursuit, fire contract',abs(distance-55*obs[-1]['t'])<1e-8 and own1[3]>own0[3] and has_damage==(arm=='dummy_advance_fire'),distance=distance,t=obs[-1]['t'])
    q=small('dummy_advance','dummy_static',seeds[4],roles=('melee','artillery'),xs=(580,600),duration=.2)
    execute('check_static_collision',q,dict(group='checks',arm='dummy_static'))
    require('static body stays fixed under collision',all((u[3],u[4])==(600,400) for r in observers('check_static_collision') for u in r['units'] if u[1]==1))
    remaining=[dict(cohort_id=1,role='melee',kind='brute',hp=1),dict(cohort_id=14,role='ranged',kind='spitter',hp=2),dict(cohort_id=49,role='artillery',kind='shaman',hp=3)]
    a=placement(seeds[5],remaining);b=placement(seeds[5],list(reversed(remaining)))
    require('placement deterministic and first role slots',a==b and all(u['position']==next(s for s in standard(seeds[5])[0] if s['role']==u['role'])['position'] for u in a))
    actual=[dict(cohort_id=u['id'],role=u['role'],kind=u['kind'],hp=u['hp']) for u in row['survivors']]
    healed=placement(seeds[5],actual)
    q=request('v7',controller('dummy_static'),seeds[5],sides=[healed,standard(seeds[5])[1]],abilities_off=True);q['options']['duration']=0
    execute('check_heal',q,dict(group='checks',arm='v7'))
    obs=next(observers('check_heal'));our=[u for u in obs['units'] if u[1]==0]
    require('carry-over heals survivors, dead stay absent',len(our)==len(actual) and all(u[5]==(258,92,181)[u[2]] for u in our) and any(u['hp']<{'brute':258,'spitter':92,'shaman':181}[u['kind']] for u in actual),survivors=len(actual),removed=50-len(actual),cohort_survivors=[u['cohort_id'] for u in actual])
    # Native parser rejects bad health and body/kind errors before stepping (tested in final suite).
    result=dict(status='PASS',checks=rows,compatibility_seconds=row['seconds'],compatibility_t=row['summary']['t'],declaration_sha256=sha(HERE/'DECLARATION.json'))
    write(output,result,exclusive=True)
    print('Section-3 checks PASS',len(rows))
    return result
