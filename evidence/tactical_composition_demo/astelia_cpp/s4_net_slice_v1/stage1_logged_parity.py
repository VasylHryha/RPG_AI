"""Offline parity against actual student Host paths. No engine or fight execution.

The logged Host uses its own cast/launch/death path. Python receives only public
pre-tick snapshots and actual native lifecycle acknowledgements, then compares
its independently computed phases, decision intents and drift with the log.
"""
import argparse
import time
import torch
from collection import read,sha,HERE,atomic
from stage1_data_v2 import frame_rows
from stage1_runtime import Replay
from stage1_export import compare
from models import Policy


def verify(path,weights,ablation='intact',deadline=None):
    payload=read(weights); model=Policy(payload['kind'])
    model.load_state_dict({k:torch.tensor(v['values'],dtype=torch.float64).reshape(v['shape']) for k,v in payload['parameters'].items()})
    replay=Replay(model,ablation); ticks=launches=deaths=decisions=0; previous=set(); maximum=0.
    with torch.no_grad():
        for frame in frame_rows(path):
            if frame.get('terminal'):
                break
            if deadline is not None and time.monotonic()>=deadline:
                raise TimeoutError('logged parity cap')
            ids=frame['gun_ids']; current=set(ids); deaths+=len(previous-current); previous=current
            joint=frame['joint']; snapshots=[{**joint,'self':i} for i in ids]
            launched=[e['unit'] for e in frame['events'] if e['stage']=='launch']; launches+=len(launched)
            result=replay.deployment([snapshots],[launched],start_tick=ticks,deadline=deadline)[0]
            # phase_state is logged after the physical tick and actual launch reset.
            phases=[[i,float(replay.phase[i])] for i in ids]
            maximum=max(maximum,compare(frame['phase_state'],phases))
            maximum=max(maximum,compare(frame['phase_motion'],result['drift']))
            if ticks%6==0:
                intents={e['unit']:e['value'] for e in frame['events'] if e['stage']=='intent'}
                for action in result['actions']:
                    maximum=max(maximum,compare(intents[action['id']],action['action']))
                    decisions+=1
            # Native cast lock is acknowledged after prepare/readout at this tick.
            for event in frame['events']:
                if event['stage']=='cast_start':
                    replay.pending[event['unit']]=event['value']['target']
                elif event['stage'] in ('launch','cancel','consumed_without_launch'):
                    replay.pending.pop(event['unit'],None)
            ticks+=1
    return dict(status='PASS',ticks=ticks,launches=launches,deaths=deaths,decision_rows=decisions,
                maximum_absolute_error=maximum,atol=1e-9,rtol=1e-9,
                raw_sha256=sha(path),weights_sha256=sha(weights),ablation=ablation,
                scope='own native Host path vs independent Python Replay; no physical execution')


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('log'); p.add_argument('weights'); p.add_argument('--ablation',default='intact'); p.add_argument('--output',required=True); a=p.parse_args()
    from pathlib import Path
    if Path(a.output).exists():
        raise RuntimeError('refuse to overwrite logged parity evidence')
    atomic(a.output,verify(a.log,a.weights,a.ablation))
