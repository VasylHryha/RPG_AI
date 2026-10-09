"""Stage A paths and durable receipts; no execution on import."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ARMY=HERE.parent
CPP=ARMY.parent
VARIANT=os.environ.get('B2_VARIANT','react_on')
if VARIANT not in ('react_on','learned_dodge'):raise ValueError('B2_VARIANT')
LOCAL=HERE/'_local'/VARIANT
BINARY=HERE/'_local/build/tactics_react_host_stageb2'
ARMS=('N1','N1b','N1r','N1rb','N2')
BASELINE_ARMS=('N1','N1r','N2')
BASELINE_PARENT={'N1':'N1','N1b':'N1','N1r':'N1r','N1rb':'N1r','N2':'N2'}
ROLES=('melee','ranged','artillery')

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024**2),b''):h.update(chunk)
    return h.hexdigest()

def read(path):return json.loads(Path(path).read_text())

def write(path,value,exclusive=False):
    path=Path(path)
    if isinstance(value,dict) and path.suffix=='.json' and path.name!='OWNER_APPROVALS.json' and 'parameters' not in value and path.parent.name!='requests':
        from owner_approvals import snapshot
        value['owner_approvals']=snapshot()
    path.parent.mkdir(parents=True,exist_ok=True)
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
    from runtime import sources as isolated
    return isolated()

def _legacy_sources():
    paths=[*HERE.glob('*.py'),*HERE.glob('*.cpp'),*HERE.glob('*.h'),HERE/'requirements.lock']
    paths += [* (ARMY/'rev2').glob('a0_*.py'),ARMY/'rev2/a0_oracle.cpp',ARMY/'rev2/a0_oracle.h',CPP/'build_admission.py',CPP/'s4_net_slice_v1/process_gate.py']
    return {str(p.relative_to(CPP)):sha(p) for p in sorted(paths)}
