"""Owner-requested engineering comparison; no developmental or final worlds.

Compare the preserved R005 kernel/assay to the optimized implementation on the
same already-reserved fixture. Retain every raw response and numerical check.
Run each side in a fresh process; include cache setup and all 50 probes in timing.
"""
import argparse
import ctypes
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from geomind import c6_r4_field as F,c6_r4_field_assay as A,c6_r4_field_protocol as P
from tools import build_c6_r4

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);sys.modules[name]=result;spec.loader.exec_module(result)
    return result

def measure(side,output):
    if side=='baseline':
        old=ROOT/'evidence/c6_r006_performance_checks/baseline'
        field=module('c6_baseline_field',old/'c6_r4_field.py')
        assay=module('c6_baseline_assay',old/'c6_r4_field_assay.py');assay.F=field
        lib=ctypes.CDLL(str(ROOT/'evidence/c6_r5_design_gate/NATIVE_BUILD.dylib'))
        ptr=ctypes.POINTER(ctypes.c_double);iptr=ctypes.POINTER(ctypes.c_int)
        tail=[ptr,ptr,ptr,ptr,iptr,ptr,ptr,iptr,ptr,ptr,ptr]
        lib.field_rhs.argtypes=[ctypes.c_int]*3+[ctypes.c_double]+tail
        lib.field_run.argtypes=[ctypes.c_int]*3+[ctypes.c_double]*2+[ctypes.c_int]*2+tail
        lib.field_rhs.restype=lib.field_run.restype=ctypes.c_int
        # Preserve the real pre-optimization native hash guards, with their
        # original sources and binary redirected to the retained snapshot.
        from types import SimpleNamespace
        field.build=SimpleNamespace(SOURCE=old/'field.cpp',LIBRARY=ROOT/'evidence/c6_r5_design_gate/NATIVE_BUILD.dylib')
        record=json.loads((ROOT/'evidence/c6_r5_design_gate/NATIVE_BUILD.json').read_text())
        field._NATIVE=(lib,record)
    else:field,assay=F,A
    settings=P.load_settings();rng=np.random.default_rng(882901)
    o=field.population(rng,field.medium(rng,settings['model']),0,0,24)
    o.z=.55*np.exp(1j*rng.uniform(-np.pi,np.pi,25));o.cohorts[0].carrier=o.z.copy()
    o.cohorts[0].selected=(0,1,2);o.cohorts[0].output=0.
    # Two live cohorts exercise retained ancestors, without formation or a
    # recorded world, candidate selection, scientific endpoint or verdict.
    o=field.population(np.random.default_rng(552),o,1,0,24)
    o.cohorts[-1].selected=(1,2,3);o.cohorts[-1].output=0.;o.time=17.3
    field.native();calls={'advance':0,'native_source_integrations':0};advance=field.advance
    def counted(state,*args,**kwargs):
        calls['advance']+=1
        if kwargs.get('_factor') is False and state.cohorts:calls['native_source_integrations']+=1
        return advance(state,*args,**kwargs)
    field.advance=counted
    grid=assay.GridSet([o]*3,settings);started=time.perf_counter()
    descriptor=assay.descriptor(grid,.3,'performance-fixture')
    elapsed=time.perf_counter()-started
    record={'kind':'ENGINEERING_FIXTURE_ONLY','side':side,'seconds':elapsed,'initial_identity':o.identity(),
            'fixture_entropies':[882901,552],'duration':10.,'elements_per_cohort':24,'live_cohorts':2,
            'probes':50,'resolutions':[.005,.0025,.00125],'calls':calls,
            'descriptor':descriptor,'checks':grid.checks,'native_build':field.native()[1]}
    output.write_text(json.dumps(record,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:record[k] for k in ('side','seconds','calls','probes','initial_identity')}),flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--side',choices=('baseline','optimized'),required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    measure(args.side,args.output)
if __name__=='__main__':main()
