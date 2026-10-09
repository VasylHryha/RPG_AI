"""Zero-combat native Stage B versus preserved B2 ARMYA1 branch, full sequences."""
import argparse,time,secrets
import numpy as np
import runtime as r
import parity,calibrated_parity as cal
from baseline import check

def run(round):
    from train import configure,prepare
    from jobs import admitted
    from training_control import training_cap,TrainingDeadline
    local=configure(round);index=prepare(round);baseline=check();proof=dict(status='RUNNING',baseline_sha256=r.sha(r.LOCAL/'BASELINE.json'),binary=r.collect.identity(),records=[])
    admission=r.common.load('baseline_admission',r.CPP/'build_admission.py');original=r.B_LOCAL/'build/tactics_react_host_stageb';proof['original_binary']=admission.admit(original)
    token=secrets.token_hex(8);start=time.monotonic();cap=training_cap(r.HERE);saved=cal.BINARY
    try:
        with admitted(cap['cap_seconds']) as (absolute,monitor):
            parity.MONITOR=monitor;parity.DEADLINE=TrainingDeadline(r.HERE,absolute,cap['cap_seconds']);cal.LOCAL=local
            for fight in (f for f in index['fights'] if f['split']=='validation'):
                if r.sha(fight['raw_file'])!=fight['raw_sha256']:raise RuntimeError('baseline parity raw drift')
                for arm in r.common.BASELINE_ARMS:
                    weights=r.read(baseline['exports'][arm]['path']);classes=[];cal.BINARY=original
                    a=cal.replay(weights,r.data.frames(fight['raw_file']),timeout=max(1,parity.DEADLINE-time.monotonic()),fire_classes=classes)
                    reference=[];cal.BINARY=r.BINARY;b=cal.replay(weights,r.data.frames(fight['raw_file']),timeout=max(1,parity.DEADLINE-time.monotonic()),fire_classes=reference)
                    equal=len(a)==len(b) and all(np.array_equal(x,y) for x,y in zip(a,b)) and all(np.array_equal(x,y) for x,y in zip(classes,reference))
                    proof['records'].append(dict(arm=arm,fight=fight['tag'],frames=len(a),exactly_equal=equal))
                    if not equal:raise RuntimeError('preserved Stage B decoder changed')
            proof['status']='PASS';r.write(local/'BASELINE_PARITY.json',proof,exclusive=True)
    except BaseException as e:proof.update(status='STOP',error=str(e));raise
    finally:
        cal.BINARY=saved;parity.MONITOR=None;parity.DEADLINE=None;proof['seconds']=time.monotonic()-start;r.write(r.HERE/('BASELINE_PARITY_RUN_'+r.VARIANT+'_'+token+'.json'),proof,exclusive=True)

def gate(round):
    proof=r.read(r.LOCAL/f'round{round}/BASELINE_PARITY.json')
    expected={(a,f['tag']) for a in r.common.BASELINE_ARMS for f in r.read(r.LOCAL/f'round{round}/INDEX.json')['fights'] if f['split']=='validation'}
    if proof['status']!='PASS' or proof['binary']!=r.collect.identity() or proof['baseline_sha256']!=r.sha(r.LOCAL/'BASELINE.json') or len(proof['records'])!=len(expected) or {(v['arm'],v['fight']) for v in proof['records']}!=expected or not all(v['exactly_equal'] for v in proof['records']):raise RuntimeError('network-only native bridge parity required')
    check();return proof
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--round',type=int,choices=range(11),default=1);run(p.parse_args().round)
