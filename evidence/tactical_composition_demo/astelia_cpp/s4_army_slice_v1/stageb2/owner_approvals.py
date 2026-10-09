"""Live owner settings; excluded from source pins, with durable change history."""
import fcntl
import hashlib
import json
import math
import os
import time
from pathlib import Path

HERE=Path(__file__).resolve().parent
PATH=HERE/'OWNER_APPROVALS.json'

def _read():
    raw=PATH.read_bytes();cfg=json.loads(raw)
    if cfg.get('schema')!=1 or cfg.get('approved_by')!='owner' or not cfg.get('approval_reference'):
        raise ValueError('owner approvals identity')
    def number(v,lo,hi):
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not lo<=v<=hi:
            raise ValueError('owner approvals numeric bounds')
    train=cfg['training'];number(train['max_seconds'],1,math.inf);number(train['cap_seconds'],1,train['max_seconds'])
    number(cfg['coverage']['max_seconds'],1,train['max_seconds'])
    if set(cfg['coverage']['thresholds'])!={'all','ordinary','dodge'}:raise ValueError('coverage threshold categories')
    for v in cfg['coverage']['thresholds'].values():number(v,0,1)
    if not isinstance(cfg['coverage']['structurally_empty'],dict):raise ValueError('structurally empty mapping')
    parity=cfg['parity'];number(parity['native_atol'],0,1);number(parity['float32_near_tie_ceiling'],0,1)
    if parity['native_categorical_mismatches']!=0:raise ValueError('native categories must match')
    d=cfg['dagger']
    if (d['min_rounds'],d['max_rounds'])!=(5,10) or type(d['rounds']) is not int or not 5<=d['rounds']<=10:
        raise ValueError('declare 5-10 DAgger rounds')
    if (d['teacher_share_start'],d['teacher_share_end'])!=(.5,0):raise ValueError('DAgger share endpoints')
    number(d['cap_seconds'],1,train['max_seconds']);number(cfg['lab']['cap_seconds'],1,train['max_seconds'])
    dart=d['dart']
    if type(dart['enabled']) is not bool:raise ValueError('DART enabled')
    number(dart['movement_sigma_px'],0,1000);number(dart['target_replace_probability'],0,1)
    if dart['enabled'] and dart['movement_sigma_px']==0 and dart['target_replace_probability']==0:
        raise ValueError('enabled DART needs declared nonzero measured noise')
    return cfg,raw

def load():return _read()[0]

def snapshot():
    cfg,raw=_read();digest=hashlib.sha256(raw).hexdigest()
    root=HERE/'_local/owner_approvals';root.mkdir(parents=True,exist_ok=True)
    # One lock covers both the snapshot and chronological transitions, including
    # a return to a previously seen configuration. Concurrent workers share it.
    with (root/'HISTORY.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        archive=root/(digest+'.json')
        if not archive.exists():
            with archive.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
        history=root/'CHANGES.jsonl';previous=None
        if history.exists():
            lines=history.read_text().splitlines()
            if lines:previous=json.loads(lines[-1])['sha256']
        if previous!=digest:
            with history.open('a') as f:
                f.write(json.dumps(dict(time_ns=time.time_ns(),previous_sha256=previous,sha256=digest,approval_reference=cfg['approval_reference']))+'\n');f.flush();os.fsync(f.fileno())
    return dict(path=str(PATH),sha256=digest,history=str(history))

def cap(scope):
    cfg=load()
    return min(cfg['training']['cap_seconds'],cfg[scope]['cap_seconds'])
