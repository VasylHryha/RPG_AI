"""Stage A paths and durable receipts; no execution on import."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ARMY=HERE.parent
CPP=ARMY.parent
LOCAL=HERE/'_local'
BINARY=LOCAL/'build/tactics_react_host_stagea'
ARMS=('N1','N1h','N1r','N2','N2J0')
ROLES=('melee','ranged','artillery')

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024**2),b''):h.update(chunk)
    return h.hexdigest()

def read(path):return json.loads(Path(path).read_text())

def write(path,value,exclusive=False):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(value,allow_nan=False,indent=2)+'\n'
    if len(text.encode())>=45_000_000:raise ValueError('compact receipt exceeds 45 MB')
    if exclusive:
        with path.open('x') as f:f.write(text);f.flush();os.fsync(f.fileno())
    else:
        tmp=path.with_suffix(path.suffix+'.tmp')
        with tmp.open('w') as f:f.write(text);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)

def load(name,path):
    prior=list(sys.path)
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.path.insert(0,str(Path(path).parent))
    try:spec.loader.exec_module(m)
    finally:sys.path[:]=prior
    return m

def sources():
    paths=[*HERE.glob('*.py'),*HERE.glob('*.cpp'),*HERE.glob('*.h'),HERE/'requirements.lock']
    paths += [* (ARMY/'rev2').glob('a0_*.py'),ARMY/'rev2/a0_oracle.cpp',ARMY/'rev2/a0_oracle.h',CPP/'build_admission.py',CPP/'s4_net_slice_v1/process_gate.py']
    return {str(p.relative_to(CPP)):sha(p) for p in sorted(paths)}
