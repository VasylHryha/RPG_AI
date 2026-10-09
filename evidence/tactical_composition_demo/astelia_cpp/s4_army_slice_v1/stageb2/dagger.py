"""Full-fight student occupancy, exact live O shadow labels, fresh seeds."""
import runtime as r
import argparse,random,secrets,time
from execution import execute,disk_projection
from parity_run import gate
from recording import rows
from diagnose import counter,disagreements
from coverage import accumulate,report


def used_seeds():
    used=r.collect.excluded()
    for p in r.LOCAL.glob('*LEDGER*.json'):
        for j in r.read(p).get('jobs',[]):used.add(j['seed'])
    return used

def prepare(round):
    from dagger_schedule import seal,round_check
    schedule=seal(r)
    if not 1<=round<=schedule['rounds']:raise ValueError('round outside declared DAgger schedule')
    round_check(r,round)
    proof=gate(round-1);path=r.LOCAL/f'DAGGER_LEDGER_ROUND{round}.json'
    if path.exists():return check(round)
    rng=random.Random(secrets.randbits(256));used=used_seeds();jobs=[];base=r.collect.a0()
    cells=['regular','regular',*base.CELLS];rng.shuffle(cells)
    paired=[]
    for i,cell in enumerate(cells):
        seed=rng.randrange(1,2**32)
        while seed in used:seed=rng.randrange(1,2**32)
        used.add(seed);paired.append((cell,seed,random.Random((seed<<8)^round).random()<schedule['teacher_driving_share'][round-1]))
    for arm in r.ARMS:
        for i,(cell,seed,teacher_driving) in enumerate(paired):
            tag=f'dagger{round}_{arm}_{i:03}'
            req=base.request('O',cell,seed,i%2);req['stageA']=dict(collect=True,shadow=True,weights=r.read(r.LOCAL/f'round{round-1}/training/{arm}.weights.json'));req['decisionTrace']=False
            dart=schedule['dart'];req['stageA']['dagger']=dict(teacher_driving=teacher_driving,seed=seed,movement_sigma_px=dart['movement_sigma_px'] if teacher_driving and dart['enabled'] else 0,target_replace_probability=dart['target_replace_probability'] if teacher_driving and dart['enabled'] else 0)
            p=r.LOCAL/'requests'/(tag+'.json');r.write(p,req,exclusive=True)
            jobs.append(dict(tag=tag,split='train',arm=arm,teacher_driving=teacher_driving,panel='regular' if cell=='regular' else 'C3',tactic=cell,seed=seed,orientation=i%2,request_sha256=r.sha(p)))
    ledger=dict(schedule_sha256=r.sha(r.LOCAL/'DAGGER_SCHEDULE.json'),schedule=schedule,round=round,binary=r.collect.identity(),sources=r.sources(),parent_parity_sha256=r.sha(r.LOCAL/f'round{round-1}/PARITY_STAGEB2.json'),jobs=jobs,teacher='clean O shadow labels on cloned predecision state; declared collection-only whole-fight mixture, optional DART; evaluation is student-only',full_fight=True,fresh_entropy=True)
    r.write(path,ledger,exclusive=True);return ledger

def check(round):
    ledger=r.read(r.LOCAL/f'DAGGER_LEDGER_ROUND{round}.json');gate(round-1)
    from dagger_schedule import round_check
    round_check(r,round)
    if ledger['schedule_sha256']!=r.sha(r.LOCAL/'DAGGER_SCHEDULE.json'):raise RuntimeError('sealed DAgger schedule drift')
    if ledger['binary']!=r.collect.identity() or ledger['sources']!=r.sources() or ledger['parent_parity_sha256']!=r.sha(r.LOCAL/f'round{round-1}/PARITY_STAGEB2.json'):raise RuntimeError('DAgger identity drift')
    for j in ledger['jobs']:
        if r.sha(r.LOCAL/'requests'/(j['tag']+'.json'))!=j['request_sha256']:raise RuntimeError('DAgger request drift')
    return ledger

def disagreement(raw):
    coverage={}
    counts={role:counter() for role in ('melee','ranged','artillery')}
    for row in rows(raw):
        if not row.get('stageA'):continue
        accumulate(coverage,dict(row,labels=row['shadowLabels']))
        teacher={v['id']:v for v in row['shadowLabels']}
        for v in row['labels']:
            disagreements(counts[v['role']],v,teacher[v['id']],row['width'],row['height'],row['t'])
            if 'raw' in v:disagreements(dict(heads=counts[v['role']]['raw_heads']),dict(v,executed=v['raw']),teacher[v['id']],row['width'],row['height'],row['t'])
    return dict(heads={role:dict(executed_heads=c['heads'],raw_heads=c['raw_heads']) for role,c in counts.items()},label_coverage=report(coverage))

def _run(round,run_id):
    ledger=check(round);digest=r.sha(r.LOCAL/f'DAGGER_LEDGER_ROUND{round}.json');jobs=ledger['jobs'];start=time.monotonic();receipt=dict(status='RUNNING',round=round,ledger_sha256=digest,fights=[],mixture=dict(declared_share=ledger['schedule']['teacher_driving_share'][round-1],realized_share=sum(j['teacher_driving'] for j in jobs)/len(jobs),teacher_fights=sum(j['teacher_driving'] for j in jobs),total_fights=len(jobs)))
    from jobs import admitted
    from training_control import training_cap,TrainingDeadline
    cap=training_cap(r.HERE)
    from owner_approvals import cap as scope_cap
    cap['cap_seconds']=scope_cap('dagger');receipt['cap']=cap
    try:
        with admitted(cap['cap_seconds']) as (absolute,monitor):
            deadline=TrainingDeadline(r.HERE,absolute,cap['cap_seconds'],scope='dagger')
            # <= 20 complete fights; one regular and one C3 from each lane.
            sample=[next(j for j in jobs if j['arm']==a and j['panel']==p) for a in r.ARMS for p in ('regular','C3')]
            calibration=[execute(j,deadline,monitor,digest) for j in sample]
            todo=[j for j in jobs if not (r.LOCAL/'raw'/(j['tag']+'_COMPLETE.json')).exists()]
            rates={a:max(c['seconds']*150.04/c['stats']['t_end'] for c in calibration if c['job']['arm']==a) for a in r.ARMS}
            projection=1.2*sum(rates[j['arm']] for j in todo);receipt['projection']=dict(seconds=projection,per_arm_full150_seconds=rates,disk=disk_projection(calibration,todo))
            if projection>deadline-time.monotonic():raise RuntimeError('full-fight DAgger projection exceeds live B2 TRAIN_CAP')
            for j in jobs:
                c=execute(j,deadline,monitor,digest);receipt['fights'].append(dict(**j,raw_file=c['raw_file'],raw_sha256=c['raw_sha256'],frames=c['frames'],stats=c['stats'],seconds=c['seconds'],on_policy=disagreement(r.LOCAL/c['raw_file'])))
                todo=[k for k in jobs if not (r.LOCAL/'raw'/(k['tag']+'_COMPLETE.json')).exists()];disk_projection(calibration,todo)
            receipt.update(status='DONE',seconds=time.monotonic()-start);r.write(r.LOCAL/f'DAGGER_ROUND{round}.json',receipt,exclusive=True)
    except BaseException as e:receipt.update(status='STOP_RESUMABLE',error=str(e));raise
    finally:
        receipt['seconds']=time.monotonic()-start;r.write(r.HERE/('DAGGER_STAGEB2_RUN_'+r.VARIANT+'_'+run_id+'.json'),receipt,exclusive=True)

def run(round):
    run_id=secrets.token_hex(8);start=time.monotonic();path=r.HERE/('DAGGER_STAGEB2_RUN_'+r.VARIANT+'_'+run_id+'.json')
    try:return _run(round,run_id)
    except BaseException as e:
        if not path.exists():r.write(path,dict(status='REFUSED',round=round,error=str(e),seconds=time.monotonic()-start),exclusive=True)
        raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('prepare','run'));p.add_argument('--round',type=int,choices=range(1,11),default=1);a=p.parse_args();globals()[a.command](a.round)
