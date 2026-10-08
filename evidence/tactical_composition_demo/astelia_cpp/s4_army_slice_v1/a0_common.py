"""A0 paths, isolated imports and durable JSON. No fights at import time."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
CPP = HERE.parent
LOCAL = HERE / '_local'
BINARY = LOCAL / 'build/tactics_react_host_a0'
CAP_PATH = CPP / 's4_shape_lab_v1/raw/LAB_CAP.json'
MAX_RSS = 2 * 1024**3
ARMS = ('O', 'O+G', 'T')
# regular + the nineteen formation/brain entries = the twenty C3 cells.
POOL = ('line','wide line','wedge','box','column','loose','screen','crescent','ring',
        'wedge hold','line anvil','wedge flank','loose free','swarm','loose skirmish',
        'loose berserk','storm','wolfpack','alone')
CELLS = ('regular', *POOL)

def load(name, path):
    before = list(sys.path)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = before
    return module

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024**2), b''):
            h.update(chunk)
    return h.hexdigest()

def read(path):
    return json.loads(Path(path).read_text())

def write(path, value, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, allow_nan=False) + '\n'
    if len(payload.encode()) >= 45_000_000:
        raise RuntimeError('delivery JSON exceeds 45 MB')
    if exclusive:
        with path.open('x') as f:
            f.write(payload); f.flush(); os.fsync(f.fileno())
    else:
        temp = path.with_suffix(path.suffix + '.tmp')
        with temp.open('w') as f:
            f.write(payload); f.flush(); os.fsync(f.fileno())
        os.replace(temp, path)

def owner_cap():
    payload = CAP_PATH.read_bytes()
    cap = json.loads(payload)
    if (type(cap.get('cap_seconds')) is not int or cap['cap_seconds'] <= 0 or
            cap.get('approved_by') != 'owner' or not cap.get('date')):
        raise RuntimeError('valid owner LAB_CAP.json required')
    return {**cap, 'cap_path': str(CAP_PATH), 'cap_sha256': hashlib.sha256(payload).hexdigest()}

def code_hashes():
    # Living design/process/review documents and local owner settings are excluded.
    paths = sorted([*HERE.glob('a0_*.py'), *HERE.glob('a0_*.cpp'), *HERE.glob('a0_*.h'),
        CPP/'build_admission.py',CPP/'s4_net_slice_v1/process_gate.py',
        CPP/'s4_react_adapter_v1/requests.py',CPP/'s4_shape_lab_v2/lab.py',
        CPP/'s4_shape_lab_v1/build.py',CPP/'s4_v7c/THETA_ORIGIN.json',
        CPP/'s4_v7c/REGULAR_REQUEST_TEMPLATE.json'])
    return {str(p.relative_to(CPP)): sha(p) for p in paths}
