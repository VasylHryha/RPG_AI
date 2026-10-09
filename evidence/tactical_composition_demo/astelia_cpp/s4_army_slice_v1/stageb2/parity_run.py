"""Full held-out native numeric parity plus admitted calibrated exports."""
import runtime as r
import argparse,secrets,time
from train import configure,checked,complete,ROOT
import parity
import calibrated_parity as calibrated
from training_control import training_cap,TrainingDeadline

def gate(round):
    local=ROOT/f'round{round}';b=checked(local);digest=r.sha(local/'TRAIN_BUDGET.json')
    if not all(complete(local,a,digest) for a in r.ARMS):raise RuntimeError('all calibrated fits required')
    proof=r.read(local/'PARITY_STAGEB2.json');expected={(a,f['tag']) for a in r.ARMS for f in r.read(local/'INDEX.json')['fights'] if f['split']=='validation'}
    if proof['status']!='PASS' or proof['binary']!=r.collect.identity() or proof['budget_sha256']!=digest or proof['exports']!={a:r.sha(local/'training'/(a+'.weights.json')) for a in r.ARMS} or {(v['arm'],v['fight']) for v in proof['records']}!=expected or not all(calibrated.passes(v) for v in proof['records']):raise RuntimeError('full-sequence calibrated export parity required')
    return proof

def run(round):
    local=configure(round);b=checked(local);digest=r.sha(local/'TRAIN_BUDGET.json')
    if not all(complete(local,a,digest) for a in r.ARMS):raise RuntimeError('calibrated fits required')
    parity.LOCAL=local;parity.RECEIPT_DIRECTORY=local/'parity/certified_near_tie_v1';parity.environment();manifest=dict(binary=r.collect.identity(),budget_sha256=digest,index_sha256=r.sha(local/'INDEX.json'),exports={a:r.sha(local/'training'/(a+'.weights.json')) for a in r.ARMS},parity_rule=parity.PARITY_RULE)
    receipt=dict(status='RUNNING',round=round,manifest=manifest,records=[]);start=time.monotonic()
    from jobs import admitted
    cap=training_cap(r.HERE)
    try:
        with admitted(cap['cap_seconds']) as (absolute,monitor):
            parity.DEADLINE=TrainingDeadline(r.HERE,absolute,cap['cap_seconds']);parity.MONITOR=monitor
            val=[f for f in r.read(local/'INDEX.json')['fights'] if f['split']=='validation'];rates={}
            for index,fight in enumerate(val):
                for arm in r.ARMS:
                    path=parity.RECEIPT_DIRECTORY/(arm+'_'+fight['tag']+'.json')
                    if path.exists():
                        proof=r.read(path)
                        if proof['manifest']!=manifest or not calibrated.passes(proof):raise RuntimeError('parity cache drift')
                    else:
                        proof=calibrated.evaluate(arm,fight);proof['manifest']=manifest;r.write(path,proof,exclusive=True)
                        if not calibrated.passes(proof):raise RuntimeError('native/export numeric parity failed')
                    receipt['records'].append(proof);rates[arm]=max(rates.get(arm,0),proof['seconds']/max(1,proof['frames']))
                if index==0:
                    projection=1.2*sum(rates[a]*f['frames'] for f in val[1:] for a in r.ARMS if not (parity.RECEIPT_DIRECTORY/(a+'_'+f['tag']+'.json')).exists())
                    if projection>parity.DEADLINE-time.monotonic():raise RuntimeError('measured parity tail exceeds cap')
            result=dict(status='PASS',round=round,seconds=time.monotonic()-start,**manifest,records=receipt['records']);r.write(local/'PARITY_STAGEB2.json',result);receipt['status']='DONE'
    except BaseException as e:receipt.update(status='STOP_RESUMABLE',error=str(e));raise
    finally:
        parity.DEADLINE=None;parity.MONITOR=None;receipt['seconds']=time.monotonic()-start;r.write(r.HERE/('PARITY_STAGEB2_RUN_'+r.VARIANT+'_'+secrets.token_hex(8)+'.json'),receipt,exclusive=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--round',type=int,choices=(0,1,2),default=0);a=p.parse_args();run(a.round)
