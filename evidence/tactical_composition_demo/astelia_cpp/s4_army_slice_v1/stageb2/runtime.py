"""B2 isolation: every executable Python module is a local snapshot."""
from pathlib import Path
import common
HERE=Path(__file__).resolve().parent
STAGEA=HERE # native source snapshot, never a protected source write
A_LOCAL=HERE.parent/'stagea/_local'
B_LOCAL=HERE.parent/'stageb/_local'
LOCAL=common.LOCAL
BINARY=common.BINARY
ARMS=common.ARMS
VARIANT=common.VARIANT
from common import read,write,sha,CPP,ARMY

def sources():
    paths=[*HERE.glob('*.py'),*HERE.glob('*.cpp'),*HERE.glob('*.h'),HERE/'requirements.lock',*(ARMY/'rev2').glob('a0_*.py'),ARMY/'rev2/a0_oracle.cpp',ARMY/'rev2/a0_oracle.h',CPP/'build_admission.py',CPP/'s4_net_slice_v1/process_gate.py']
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
        if 'shadowLabels' in row:row=dict(row,studentLabels=row['labels'],labels=row['shadowLabels'])
        yield row
data.frames=frames
import training
import recording
_original_slim=recording.slim

def slim(row):
    result=_original_slim(row)
    if row.get('stageA'):
        for source,target in zip(row['labels'],result['labels']):
            for key in ('raw','winner'):
                if key in source:target[key]=source[key]
    return result
recording.slim=slim
