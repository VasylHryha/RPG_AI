"""Once-at-end affected synthetic suite only; no fixtures/worlds or benchmarks."""
import ctypes
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from .rev7_identity import assert_inputs,HERE,ROOT


def clocks():
    if sys.platform=='darwin':
        class Timebase(ctypes.Structure):_fields_=[('numer',ctypes.c_uint32),('denom',ctypes.c_uint32)]
        lib=ctypes.CDLL('/usr/lib/libSystem.B.dylib');base=Timebase();lib.mach_timebase_info(ctypes.byref(base))
        lib.mach_absolute_time.restype=ctypes.c_uint64;lib.mach_continuous_time.restype=ctypes.c_uint64
        scale=base.numer/base.denom/1e9
        return dict(awake=lib.mach_absolute_time()*scale,continuous=lib.mach_continuous_time()*scale,utc=datetime.now(timezone.utc).isoformat())
    return dict(awake=time.monotonic(),continuous=time.monotonic(),utc=datetime.now(timezone.utc).isoformat())


def main():
    identity=assert_inputs();start=clocks()
    cmd=[sys.executable,'-m','pytest','-q','-x',str(HERE/'test_rev7.py'),'--basetemp',str(HERE/'_rev711_test_tmp'),'-o','cache_dir='+str(HERE/'_rev711_pytest_cache')]
    path=HERE/'REV7_SYNTHETIC_TEST_LOG.txt'
    with path.open('w') as output:result=subprocess.run(cmd,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT)
    end=clocks()
    record=dict(status='PASS' if result.returncode==0 else 'FAIL',exit_code=result.returncode,command=cmd,start=start,end=end,awake_seconds=end['awake']-start['awake'],continuous_seconds=end['continuous']-start['continuous'],elapsed_utc_seconds=(datetime.fromisoformat(end['utc'])-datetime.fromisoformat(start['utc'])).total_seconds(),scientific_input_sha256=identity['sha256'],execution_pin_sha256=identity['pin_sha256'],test_log_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),fixture_execution='NOT_RUN',training_development_panels='NOT_RUN')
    (HERE/'REV7_SYNTHETIC_CHECKS.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
    print(json.dumps({key:record[key] for key in ('status','exit_code','awake_seconds','elapsed_utc_seconds')}))
    raise SystemExit(result.returncode)

if __name__=='__main__':main()
