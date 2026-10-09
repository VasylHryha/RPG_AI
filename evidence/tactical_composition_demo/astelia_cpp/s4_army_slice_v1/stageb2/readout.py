"""Fresh paired net/O/T full-army outcomes; mechanism 20 then 50/100."""
import argparse
import gzip
import json
import random
import secrets
import time
from common import ARMS,BINARY,CPP,HERE,LOCAL,ROLES,read,sha,sources,write
from collect import a0,execute,excluded,identity
from jobs import admitted
POLICIES=(*ARMS,'O','T')

def parity_gate():
    from parity import PARITY_RULE, parity_passes
    proof=read(HERE/'PARITY_STAGEA.json')
    expected={(a,f['tag']) for f in read(LOCAL/'INDEX.json')['fights'] if f['split']=='validation' for a in ARMS}
    records=proof.get('records',[])
    if (proof.get('parity_rule')!=PARITY_RULE or len(records)!=len(expected) or
            {(r['arm'],r['fight']) for r in records}!=expected or
            any(r.get('parity_rule')!=PARITY_RULE or r['status']!='PASS' or not parity_passes(r) for r in records)):
        raise RuntimeError('current certified full-sequence parity required')
    if proof['status']!='PASS' or proof['binary']!=identity() or proof['exports']!={a:sha(LOCAL/'training'/(a+'.weights.json')) for a in ARMS} or proof['budget_sha256']!=sha(LOCAL/'TRAIN_BUDGET.json') or proof['index_sha256']!=sha(LOCAL/'INDEX.json'):raise RuntimeError('current full-sequence parity required')
    from parmem_recovery import checked_inference_budget
    checked_inference_budget();return proof

def prepare():
    parity_gate();path=LOCAL/'OUTCOME_LEDGER.json'
    if path.exists():return check()
    base=a0();rng=random.Random(secrets.randbits(256));used=excluded();jobs=[]
    cells=list(base.CELLS);rng.shuffle(cells)
    for panel in ('regular','C3'):
        for i in range(100):
            seed=rng.randrange(1,2**32)
            while seed in used:seed=rng.randrange(1,2**32)
            used.add(seed);cell='regular' if panel=='regular' else cells[i%20];orientation=i%2 if panel=='regular' else (i//20)%2;pair=f'{panel}_{i:03d}'
            for arm in POLICIES:
                req=base.request('T' if arm=='T' else 'O',cell,seed,orientation);req['stageA']={'collect':True}
                if arm in ARMS:req['stageA']['weights']=read(LOCAL/'training'/(arm+'.weights.json'))
                tag='outcome_'+pair+'_'+arm;target=LOCAL/'requests'/(tag+'.json');write(target,req,exclusive=True)
                jobs.append(dict(tag=tag,pair_key=pair,panel=panel,index=i,tactic=cell,orientation=orientation,seed=seed,arm=arm,request_sha256=sha(target),split='outcome'))
    ledger=dict(binary=identity(),sources=sources(),parity_sha256=sha(HERE/'PARITY_STAGEA.json'),jobs=jobs,looks=[20,50,100],leader='PARKED',series='not_run')
    write(path,ledger,exclusive=True);return ledger

def check():
    parity_gate();ledger=read(LOCAL/'OUTCOME_LEDGER.json')
    if ledger['binary']!=identity() or ledger['sources']!=sources() or ledger['parity_sha256']!=sha(HERE/'PARITY_STAGEA.json'):raise RuntimeError('outcome identity drift')
    for j in ledger['jobs']:
        if j['request_sha256']!=sha(LOCAL/'requests'/(j['tag']+'.json')):raise RuntimeError('outcome request drift')
    return ledger

def mechanism(raw):
    deaths={r:0 for r in ROLES};killers={};dodges=launches=0;ready=active=0;predicted=0;zero_targets=0;labels=0;phase_samples=phase_delta=spacing=forcing=0.;previous_phase={}
    with gzip.open(raw,'rt') as f:
        for line in f:
            row=json.loads(line)
            if row.get('observerV1'):
                dodges+=len([x for x in row['dodges'] if x[1]==0]);launches+=len([x for x in row['launches'] if x[2]==0])
                for d in row['damage']:
                    if d['died'] and d['targetTeam']==0:
                        deaths[d['targetRole']]+=1;k=f"{d['sourceTeam']}:{d['sourceRole']}:{d['source']}";killers[k]=killers.get(k,0)+1
            if row.get('stageA'):
                if row.get('networkKind') in ('N2','N2J0'):
                    for v in row.get('networkState',[]):
                        id,theta=v[:2];phase_samples+=1;spacing+=__import__('math').hypot(v[9],v[10]);forcing+=abs(v[6])
                        if id in previous_phase:phase_delta+=abs(theta-previous_phase[id])/row['dt']
                        previous_phase[id]=theta
                for r in row['labels']:labels+=1;ready+=r['ready'];active+=r['active'];predicted+=r['executed']['fire']!='hold';zero_targets+=r['executed']['target']==0
    return dict(per_role_deaths=deaths,killer_sources=killers,dodges=dodges,launches=launches,label_rows=labels,ready_rows=ready,react_rows=active,active_fire_rows=predicted,no_target_rows=zero_targets,phase_samples=phase_samples,phase_abs_rate_sum=phase_delta,spacing_norm_sum=spacing,forcing_abs_sum=forcing,attack_resets=0)

def report(rows,look):
    base=a0();metrics=__import__('common').load('stagea_metrics',HERE.parent/'rev2/a0_metrics.py');panels={}
    for panel in ('regular','C3'):
        part=[r for r in rows if r['panel']==panel];arms={a:metrics.summary([r for r in part if r['arm']==a]) for a in POLICIES}
        for a in POLICIES:
            rr=[r for r in part if r['arm']==a];arms[a]['win_rate']=arms[a]['wins']/len(rr)
            arms[a]['per_role_deaths_per_fight']={role:sum(r['mechanism']['per_role_deaths'][role] for r in rr)/len(rr) for role in ROLES}
            from dodge_metrics import aggregate
            arms[a].update(aggregate([r['mechanism'] for r in rr]))
            from candidate_audit import merge,report as pick_report
            arms[a]['candidate_picks']=pick_report(merge(r['mechanism'].get('candidate_pick_counts',{}) for r in rr)) if a in ARMS or a.endswith('_react_on') else dict(status='not_applicable',reason='no B2 candidate scorer')
            keys={k for r in rr for k in r['mechanism']['killer_sources']};arms[a]['killer_sources']={k:sum(r['mechanism']['killer_sources'].get(k,0) for r in rr) for k in keys}
            for k in ('dodges','launches','ready_rows','active_fire_rows','react_rows','phase_samples','phase_abs_rate_sum','spacing_norm_sum','forcing_abs_sum'):arms[a][k+'_per_fight']=sum(r['mechanism'][k] for r in rr)/len(rr)
        panels[panel]=dict(arms=arms,comparisons={f'{a} minus {reference}':metrics.contrast(part,reference,a) for a in ARMS for reference in ('O','T',__import__('common').BASELINE_PARENT[a]+'_network_only',a+'_react_on') if reference in POLICIES},per_tactic={cell:{a:metrics.summary([r for r in part if r['tactic']==cell and r['arm']==a]) for a in POLICIES} for cell in (('regular',) if panel=='regular' else base.CELLS)})
    from readiness import evaluate
    readiness=evaluate(rows,look,ARMS)
    return dict(readiness=readiness,look=look,status='MECHANISM_ONLY' if look==20 else 'DEVELOPMENT_OUTCOME',panels=panels,series_streak=dict(status='not_run',reason='independent full-army fights'),interpretation='network+tools versus calibrated Stage B network-only, paired fights; body/participation remain shared; react-off disables movement react; body dash stays ON; no RRG recursion claim')

def run(look):
    ledger=check();prior=20 if look==50 else 50 if look==100 else None
    if prior:
        receipt=read(HERE/f'LOOK_STAGEA_{prior}.json')
        if receipt['ledger_sha256']!=sha(LOCAL/'OUTCOME_LEDGER.json') or not receipt['complete']:raise RuntimeError('previous complete look required')
        if receipt['harm_stop']:raise RuntimeError('previous look harmed by >=2 deaths or >=2 kills; stop and report to owner')
    jobs=[j for j in ledger['jobs'] if j['index']<look];cap=a0().owner_cap();run_id=secrets.token_hex(8);result=dict(status='RUNNING',look=look,ledger_sha256=sha(LOCAL/'OUTCOME_LEDGER.json'),cap=cap)
    try:
        with admitted(cap['cap_seconds']) as (deadline,monitor):
            calibration=[]
            # <=20 actual fights, enough to time each arm vs both panels. Reused at 20.
            sample=[j for j in jobs if j['index']==0]
            for j in sample:calibration.append(execute(j,deadline,monitor,result['ledger_sha256']))
            rates={a:max(r['seconds']*150/r['stats']['t_end'] for r in calibration if r['job']['arm']==a) for a in POLICIES}
            todo=[j for j in jobs if not (LOCAL/'raw'/(j['tag']+'_COMPLETE.json')).exists()]
            projection=1.2*sum(rates[j['arm']] for j in todo);write(LOCAL/f'OUTCOME_PROJECTION_{look}.json',dict(projected_seconds=projection,remaining_fights=len(todo),sample_fights=len(sample),per_arm_full150_seconds=rates))
            if projection>deadline-time.monotonic():raise RuntimeError('paired-look projection exceeds current invocation cap')
            records=[]
            for j in jobs:
                r=execute(j,deadline,monitor,result['ledger_sha256']);m=mechanism(LOCAL/r['raw_file'])
                if sum(m['per_role_deaths'].values())!=r['stats']['own_deaths']:raise RuntimeError('killer attribution does not cover every own death')
                records.append(dict(**j,stats=r['stats'],mechanism=m,completion_sha256=sha(LOCAL/'raw'/(j['tag']+'_COMPLETE.json'))))
            summary=report(records,look)
            harm=look>=50 and any(c['deaths_saved']<=-2 or c['enemy_kills_gained']<=-2 for p in summary['panels'].values() for c in p['comparisons'].values())
            payload=dict(ledger_sha256=result['ledger_sha256'],complete=True,harm_stop=harm,report=summary,completion_hashes={r['tag']:r['completion_sha256'] for r in records})
            target=HERE/f'LOOK_STAGEA_{look}.json'
            if target.exists():
                if read(target)!=payload:raise RuntimeError('look drift')
            else:write(target,payload,exclusive=True)
            result.update(status='DONE',**payload)
    except BaseException as e:result.update(status='STOP_RESUMABLE',error=f'{type(e).__name__}: {e}');raise
    finally:write(HERE/('OUTCOME_RUN_'+run_id+'.json'),result,exclusive=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('prepare','run'));p.add_argument('--look',type=int,choices=(20,50,100),default=20);a=p.parse_args()
    if a.command=='prepare':prepare()
    else:run(a.look)
