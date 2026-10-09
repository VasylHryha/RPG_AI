"""Bind actual successful parent fights, calibrated fits and warm-start identity."""
import argparse
from pathlib import Path
import runtime as r
ON=r.HERE/'_local/react_on'
OFF=r.HERE/'_local/learned_dodge'

def check():
    proof=r.read(OFF/'DODGE_READY.json')
    if proof.get('schema')!=2:raise RuntimeError('unbound legacy dodge readiness')
    for name,h in proof['inputs'].items():
        if r.sha(name)!=h:raise RuntimeError('learned-dodge parent drift')
    if set(proof['checkpoints'])!=set(r.ARMS):raise RuntimeError('dodge arm mismatch')
    for v in proof['checkpoints'].values():
        if r.sha(v['path'])!=v['sha256']:raise RuntimeError('warm start drift')
    return proof

def bindings(round,ledger,parity):
    """Light-testable binding logic; production additionally calls both live gates."""
    look=ON/f'LOOK_STAGEB2_R{round}_50.json';v=r.read(look);ledgerpath=ON/f'OUTCOME_LEDGER_ROUND{round}.json';digest=r.sha(ledgerpath);local=ON/f'round{round}'
    if r.read(ledgerpath)!=ledger or ledger.get('variant')!='react_on' or v['ledger_sha256']!=digest:raise RuntimeError('successful look disconnected from parent ledger')
    if not v['complete'] or v['harm_stop'] or v['look']!=50 or v['round']!=round:raise RuntimeError('complete non-harmful react-on look 50 required')
    paritypath=local/'PARITY_STAGEB2.json';budgetpath=local/'TRAIN_BUDGET.json';budgetdigest=r.sha(budgetpath)
    if r.read(paritypath)!=parity or parity['status']!='PASS' or parity['budget_sha256']!=budgetdigest or ledger['parity_sha256']!=r.sha(paritypath):raise RuntimeError('parent look/parity/budget mismatch')
    inputs={str(p):r.sha(p) for p in (look,ledgerpath,paritypath,budgetpath,local/'INDEX.json')};checkpoints={}
    for arm in r.ARMS:
        checkpoint=local/'training'/(arm+'.pt');weights=local/'training'/(arm+'.weights.json');outcome=local/'training'/(arm+'.outcome.json');calibration=local/'training'/(arm+'.calibration.json');fit=r.read(outcome)
        if fit['status']!='FIT_CALIBRATED_PARITY_PENDING' or fit['budget_sha256']!=budgetdigest or fit['checkpoint_sha256']!=r.sha(checkpoint) or fit['export_sha256']!=r.sha(weights) or fit['calibration_sha256']!=r.sha(calibration) or parity['exports'][arm]!=r.sha(weights):raise RuntimeError('eligible parent checkpoint/export/fit mismatch')
        for p in (checkpoint,weights,outcome,calibration):inputs[str(p)]=r.sha(p)
        checkpoints[arm]=dict(path=str(checkpoint),sha256=r.sha(checkpoint),export_sha256=r.sha(weights))
    jobs=[j for j in ledger['jobs'] if j['index']<50]
    if len({j['tag'] for j in jobs})!=len(jobs):raise RuntimeError('duplicate parent completion')
    records=[]
    for j in jobs:
        path=ON/'raw'/(j['tag']+'_COMPLETE.json');c=r.read(path)
        if c['status']!='DONE' or c['job']!=j or c['ledger_sha256']!=digest:raise RuntimeError('parent fight completion identity')
        raw=ON/c['raw_file']
        if r.sha(raw)!=c['raw_sha256']:raise RuntimeError('parent raw drift')
        inputs[str(path)]=r.sha(path);inputs[str(raw)]=c['raw_sha256'];records.append(dict(j,stats=c['stats']))
    for panel in ('regular','C3'):
        for arm in r.ARMS:
            group=[c for c in records if c['panel']==panel and c['arm']==arm]
            if len(group)!=50 or {c['index'] for c in group}!=set(range(50)) or not any(c['stats']['win'] for c in group):raise RuntimeError('actual parent wins and complete per-arm panel required')
            if sum(c['stats']['win'] for c in group)!=v['report']['panels'][panel]['arms'][arm]['wins']:raise RuntimeError('parent win summary mismatch')
            for reference in ('O','T',r.common.BASELINE_PARENT[arm]+'_network_only'):
                other=[c for c in records if c['panel']==panel and c['arm']==reference]
                if len(other)!=50:raise RuntimeError('parent comparator coverage')
                deaths_saved=sum(c['stats']['own_deaths'] for c in other)/50-sum(c['stats']['own_deaths'] for c in group)/50
                kills_gained=sum(c['stats']['enemy_kills'] for c in group)/50-sum(c['stats']['enemy_kills'] for c in other)/50
                if deaths_saved<=-2 or kills_gained<=-2:raise RuntimeError('actual parent harm stop')
    return dict(schema=2,round=round,inputs=inputs,checkpoints=checkpoints,gate='actual paired wins, non-harmful complete look, calibrated checkpoint/export/parity identity; development eligibility only')

def enable(round):
    if r.VARIANT!='react_on':raise RuntimeError('enable from react_on variant')
    path=OFF/'DODGE_READY.json'
    if path.exists():return check()
    from parity_run import gate
    from readout_run import check as outcome_gate
    parity=gate(round);ledger=outcome_gate(round)
    proof=bindings(round,ledger,parity);r.write(path,proof,exclusive=True);return proof
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--round',type=int,choices=range(1,11),default=1);enable(p.parse_args().round)
