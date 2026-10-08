"""Two sealed DAgger rounds: students act, constrained teacher labels same tick.

No teacher action mixing. Round zero is always retained. Execution is explicit;
no entropy, native process or refit is created on import or in tests.
"""
import argparse
from collections import Counter
import hashlib
from pathlib import Path
import secrets
import time
from collection import HERE, ROOT, read, sha, atomic, cap
from protocol import split
from requests import drill
from stage1_data import DATA, admit, convert_fight,validate_arithmetic
from stage1_jobs import JOBS, job_lock, pins, execute, physical_budget
from stage1_native import BINARY

ARMS=('N1','N1r','N2')
# Sparse = one-gun cell: two visits each. Six other visits include two-gun
# recovery and ten-gun joint control, with both orientations represented.
CELLS=(('D1-static',1),('D1-static',1),('D2-shellfire',1),('D2-shellfire',1),
       ('D1-static',2),('D2-shellfire',2),('D1-static',10),('D2-shellfire',10),('D1-static',10),('D2-shellfire',10))


def inventory(round_id,entropy,weights,excluded):
    if round_id not in (1,2):
        raise ValueError('two DAgger rounds only')
    rows=[]; used=set(excluded)|set(range(10000))
    for i,(cell,guns) in enumerate(CELLS):
        counter=0
        # Preassign 7/2/1 train/validation/test draws identically across visitors.
        desired='train' if i<7 else 'validation' if i<9 else 'test'
        while True:
            h=hashlib.sha256(f'NS1-dagger:{round_id}:{entropy}:{i}:{counter}'.encode()).hexdigest()
            counter+=1; seed=int(h[:8],16); group='NS1-DA-'+h[8:40]
            if seed not in used and split(group)==desired:
                break
        used.add(seed)
        for arm in ARMS:
            # Each entire fight gets its own identity with the same sealed split.
            n=0
            while True:
                fight='NS1-DA-'+hashlib.sha256(f'{group}:{arm}:{n}'.encode()).hexdigest()[:32]; n+=1
                if split(fight)==desired:
                    break
            request=drill(cell,guns,seed,i%2,arm,weights[arm],fight)
            request['shadow']=True; request['ablation']='intact'
            rows.append(dict(fight=fight,group=fight,paired_group=group,split=desired,round=round_id,visitor=arm,
                             cell=cell,guns=guns,orientation=i%2,request=request))
    return dict(version='NS1-DAgger-1',round=round_id,entropy=entropy,rows=rows,
                max_physical_attempts=30,max_decision_row_queries=225000,
                sparse_definition='two visits to each D1/1 and D2/1 cell per visitor; other six visits cover 2/10 guns',
                pins=pins(weights))


def aggregate(round_id):
    if round_id not in (1,2):
        raise ValueError('two rounds')
    initial=read(DATA/'INDEX.json')['fights']
    union=[dict(m,round=0,visitor='teacher') for m in initial]
    for r in range(1,round_id+1):
        path=JOBS/f'dagger_r{r}'
        inv=read(path/'INVENTORY.json')
        for row in inv['rows']:
            receipt=read(path/(row['fight']+'.receipt.json'))
            if receipt['inventory_sha256']!=sha(path/'INVENTORY.json') or receipt['raw_sha256']!=sha(path/(row['fight']+'.jsonl')):
                raise RuntimeError('DAgger receipt drift')
            target=DATA/row['fight']
            if not (target/'META.json').exists():
                partial=DATA/(row['fight']+'.partial')
                meta=convert_fight(row,path/(row['fight']+'.jsonl'),receipt['record_count'],partial,shadow=True)
                partial.rename(target)
            else:
                meta=read(target/'META.json')
                validate_arithmetic(meta)
            if meta['raw_sha256']!=receipt['raw_sha256']:
                raise RuntimeError('DAgger converted provenance')
            union.append(dict(meta,round=r,visitor=row['visitor']))
    totals=Counter()
    for m in union:
        if m['split']=='train':
            totals[m['round'],m['visitor']]+=m['counts']['decision_rows']
    for r in range(round_id+1):
        for visitor in (('teacher',) if r==0 else ARMS):
            if not totals[r,visitor]:
                raise ValueError('empty round/visitor training stratum')
    for m in union:
        visitors=1 if m['round']==0 else 3
        m['row_weight']=1/((round_id+1)*visitors*totals[m['round'],m['visitor']]) if m['split']=='train' else 1.
    # Selection has the same round/visitor balance, using ONLY validation rows.
    val=Counter()
    for m in union:
        if m['split']=='validation':
            val[m['round'],m['visitor']]+=m['counts']['decision_rows']
    if any(val[r,v]==0 for r in range(round_id+1) for v in (('teacher',) if r==0 else ARMS)):
        raise ValueError('empty validation round/visitor stratum')
    for m in union:
        if m['split']=='validation':
            m['row_weight']=1/((round_id+1)*(1 if m['round']==0 else 3)*val[m['round'],m['visitor']])
    value=dict(round=round_id,fights=union,round0_retained=True,
               collection_receipt_sha256=sha(HERE/'COLLECTION_RECEIPT.json'),source_sha256=sha(HERE/'stage1_data.py'),
               round_inventory_sha256={str(r):sha(JOBS/f'dagger_r{r}'/'INVENTORY.json') for r in range(1,round_id+1)})
    atomic(JOBS/f'dagger_r{round_id}'/'AGGREGATE.json',value)
    return value


def run(round_id,refit=False):
    directory=JOBS/f'dagger_r{round_id}'; directory.mkdir(parents=True,exist_ok=True)
    model_root=HERE/'_local/stage1' if round_id==1 else HERE/'_local/stage1/dagger_r1'
    result_path=HERE/'STAGE1_RESULTS.json' if round_id==1 else HERE/'DAGGER_R1_RESULTS.json'
    result=read(result_path)
    if result['status']!='TRAINED_BC' or result['export_parity']['status']!='PASS':
        raise RuntimeError('selected trained, parity-verified prior fit required')
    weights={a:model_root/(a+'.weights.json') for a in ARMS}
    for a,w in weights.items():
        if sha(w)!=result['models'][a]['export_sha256']:
            raise RuntimeError('prior trained export drift')
    excluded=[r['seed'] for r in admit()['rows']]
    if round_id==2:
        excluded += [r['request']['seed'] for r in read(JOBS/'dagger_r1/INVENTORY.json')['rows']]
    path=directory/'INVENTORY.json'
    if path.exists():
        inv=read(path)
        if inv!=inventory(round_id,inv['entropy'],weights,excluded):
            raise RuntimeError('DAgger inventory/pins drift')
    else:
        inv=inventory(round_id,secrets.token_hex(32),weights,excluded); atomic(path,inv)
    digest=sha(path); deadline=physical_budget(directory); queries=0; receipts=[]
    for row in inv['rows']:
        if pins(weights)!=inv['pins']:
            raise RuntimeError('DAgger pins drift')
        r=execute(directory,row,digest,BINARY,30,deadline); queries+=r['decision_count']; receipts.append(r)
        if queries>225000:
            raise RuntimeError('DAgger query cap')
    union=aggregate(round_id)
    atomic(HERE/f'DAGGER_R{round_id}_COLLECTION.json',dict(status='COLLECTED',inventory_sha256=digest,
           fights=30,queries=queries,aggregate_sha256=sha(directory/'AGGREGATE.json'),
           raw_sha256={r['request']['fight']:r['raw_sha256'] for r in receipts},refit_run=False))
    if refit:
        from stage1_train import run as fit
        fit(True, directory/'AGGREGATE.json')
    return union


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--round',type=int,choices=(1,2),required=True)
    p.add_argument('--refit-if-admitted',action='store_true'); a=p.parse_args()
    with job_lock('dagger'):
        run(a.round,a.refit_if_admitted)
