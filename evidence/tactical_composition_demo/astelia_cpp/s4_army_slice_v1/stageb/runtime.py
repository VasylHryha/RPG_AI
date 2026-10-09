"""Stage B revision isolation. Stage A modules are reused without disk edits."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
STAGEA=HERE.parent/'stagea'
sys.path.insert(0,str(STAGEA));sys.path.insert(0,str(HERE))
import common
A_LOCAL=STAGEA/'_local'
LOCAL=HERE/'_local'
BINARY=LOCAL/'build/tactics_react_host_stageb'
ARMS=('N1','N1h','N1r','N2')
common.HERE=HERE;common.LOCAL=LOCAL;common.BINARY=BINARY;common.ARMS=ARMS
from common import read,write,sha,CPP,ARMY

def sources():
    # Code only: never a living report, owner cap or planning document.
    paths=[*(ARMY/'rev2').glob('a0_*.py'),CPP/'build_admission.py',CPP/'s4_net_slice_v1/process_gate.py',*HERE.glob('*.py'),*HERE.glob('*.cpp'),*HERE.glob('*.h'),*STAGEA.glob('*.py'),*STAGEA.glob('*.cpp'),*STAGEA.glob('*.h'),STAGEA/'requirements.lock']
    return {str(p.relative_to(CPP)):sha(p) for p in sorted(paths)}
common.sources=sources
import collect
collect.disk_note=lambda:None
collect.completion_identity=lambda p,r,h: None if r['ledger_sha256']==h else (_ for _ in ()).throw(RuntimeError('completion ledger drift'))
collect.completion_path=lambda j:LOCAL/'raw'/(j['tag']+'_COMPLETE.json')
collect.ledger_path=lambda:LOCAL/'UNUSED_DATA_LEDGER.json'
import data
_original_frames=data.frames

def frames(path):
    for row in _original_frames(path):
        if 'shadowLabels' in row:
            row=dict(row,studentLabels=row['labels'],labels=row['shadowLabels'])
        yield row
# Training consumes O labels; pack ignores labels, history remains the student's.
data.frames=frames
import training
training.HERE=STAGEA
import training_control
_base_cap=training_control.training_cap
def stageb_cap(here):
    value=_base_cap(here)
    if Path(here).resolve()==HERE and (value.get('written_by')!='Claude' or value['cap_seconds']>16200):raise RuntimeError('Claude-authored Stage B cap, maximum 4.5 h, required')
    return value
training_control.training_cap=stageb_cap
import jobs
# a0() loads original rev2 from unchanged ARMY, owner LAB_CAP remains live.

# Preserve student proposals alongside executed and O labels in compact DAgger.
import recording
_stagea_slim=recording.slim
def stageb_slim(row):
    result=_stagea_slim(row)
    if row.get('stageA'):
        for source,target in zip(row['labels'],result['labels']):
            if 'raw' in source:target['raw']=source['raw']
    return result
recording.slim=stageb_slim

import models
models.ARMS=(*ARMS,'N2J0') # Read-only diagnosis still supports the dropped Stage A control.
