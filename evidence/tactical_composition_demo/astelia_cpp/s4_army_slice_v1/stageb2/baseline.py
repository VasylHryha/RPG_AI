"""Bind completed Stage B network-only exports read-only, for paired B2 fights."""
import argparse
from pathlib import Path
import runtime as r

def check():
    proof=r.read(r.LOCAL/'BASELINE.json')
    for a,v in proof['exports'].items():
        if r.sha(v['path'])!=v['sha256']:raise RuntimeError('baseline snapshot drift')
    for p,h in proof['inputs'].items():
        if r.sha(p)!=h:raise RuntimeError('Stage B baseline input drift')
    return proof

def prepare(round):
    path=r.LOCAL/'BASELINE.json'
    if path.exists():return check()
    local=r.B_LOCAL/f'round{round}';parity=local/'PARITY_STAGEB.json';proof=r.read(parity);budget=local/'TRAIN_BUDGET.json'
    if proof['status']!='PASS' or proof['budget_sha256']!=r.sha(budget):raise RuntimeError('completed Stage B parity required')
    if any(Path(p).suffix=='.md' for p in r.read(budget)['sources']):raise RuntimeError('baseline pins living docs')
    inputs={str(parity):r.sha(parity),str(budget):r.sha(budget)};exports={}
    for arm in r.ARMS:
        source=local/'training'/(arm+'.weights.json');outcome=local/'training'/(arm+'.outcome.json');v=r.read(outcome)
        if v['status']!='FIT_CALIBRATED_PARITY_PENDING' or v['budget_sha256']!=r.sha(budget) or v['export_sha256']!=r.sha(source) or proof['exports'][arm]!=r.sha(source):raise RuntimeError('baseline fit/export identity')
        weights=r.read(source)
        if weights['version']!='ARMYA1' or len(weights['fireThresholds'])!=3:raise RuntimeError('network-only calibrated baseline schema')
        target=r.LOCAL/'baseline'/(arm+'.weights.json');target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as f:f.write(source.read_bytes())
        exports[arm]=dict(path=str(target),sha256=r.sha(target));inputs.update({str(source):r.sha(source),str(outcome):r.sha(outcome)})
    result=dict(round=round,inputs=inputs,exports=exports,interpretation='completed Stage B calibrated network-only; same paired scenarios through preserved ARMYA1 decoder')
    r.write(path,result,exclusive=True);return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--round',type=int,choices=(0,1,2),default=1);prepare(p.parse_args().round)
