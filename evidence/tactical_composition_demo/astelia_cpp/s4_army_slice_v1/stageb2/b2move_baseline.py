"""Read-only HEAD candidate twin for repeatable before/after fixture metrics."""
import ctypes, hashlib, subprocess, sys
from pathlib import Path
import common as c
import native_candidates as nc

def baseline_library():
    root=c.HERE/'_local/b2move/baseline';root.mkdir(parents=True,exist_ok=True)
    head=subprocess.run(['git','rev-parse','HEAD'],check=True,capture_output=True,text=True).stdout.strip()
    paths=('native_candidates.cpp','candidates.h','tools.h');hashes={}
    for name in paths:
        relative=str((c.HERE/name).relative_to(c.CPP.parents[2]))
        value=subprocess.run(['git','show',head+':'+relative],check=True,capture_output=True).stdout
        hashes[name]=hashlib.sha256(value).hexdigest();(root/name).write_bytes(value)
    # Refuse comparing an unrelated HEAD vocabulary against the named diagnosis.
    expected=c.read(c.HERE/'COVERAGE_ROUND0_V1.json')['sources']
    for name,h in hashes.items():
        if expected['s4_army_slice_v1/stageb2/'+name]!=h:raise RuntimeError('HEAD differs from named old coverage builder')
    digest=hashlib.sha256(''.join(hashes[n] for n in paths).encode()).hexdigest()
    path=root/(digest+('.dylib' if sys.platform=='darwin' else '.so'))
    if not path.exists():subprocess.run(['c++','-std=c++17','-O3','-ffp-contract=off','-fPIC','-shared',str(root/'native_candidates.cpp'),'-o',str(path)],check=True,capture_output=True,timeout=60)
    lib=ctypes.CDLL(str(path));D=ctypes.POINTER(ctypes.c_double)
    lib.candidate_batch.argtypes=[D,ctypes.POINTER(ctypes.c_int),ctypes.c_double,ctypes.c_double,ctypes.c_int,ctypes.POINTER(D)]
    lib.candidate_batch.restype=ctypes.c_long;lib.candidate_error.restype=ctypes.c_char_p
    return lib,dict(head=head,sources=hashes)

def baseline_batch(row,lib):
    prior=nc.LIB;nc.LIB=lib
    try:return nc.batch(row,allow_missing_aim=True)
    finally:nc.LIB=prior
