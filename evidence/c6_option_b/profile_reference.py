"""One complete current R4 world: engineering profile, not a readiness retry."""
import cProfile
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import pstats
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from geomind import c6_r4_field as F, c6_r4_field_protocol as P
from geomind.c6_r4_integrity import validate_pin, sha256
from tools import build_c6_r4 as B


def load_record():
    record = json.loads((B.LIBRARY.parent / 'BUILD.json').read_text())
    if record['source_sha256'] != sha256(B.SOURCE) or record['binary_sha256'] != sha256(B.LIBRARY):
        raise RuntimeError('Existing reference source/build identity mismatch')
    return record


def machine():
    return {'load_average': os.getloadavg(), 'cpu_count': os.cpu_count(),
            'platform': platform.platform(), 'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'process_inventory': 'Unavailable: sandbox denies ps; load averages recorded.'}


def main():
    folder = Path(__file__).parent / 'profile_run'
    folder.mkdir(exist_ok=False)
    native_record = load_record()
    source_pin = validate_pin(ROOT)
    # Diagnostics only: add timers to an exact copy of the original equations.
    # This is not the port. The original source/library remain untouched.
    source = B.SOURCE.read_text()
    source = '#include <chrono>\nstatic double field_seconds=0., element_seconds=0.;\nusing Clock=std::chrono::steady_clock;\n' + source
    source = source.replace('auto medium=[&](const double* z,double* dz){',
        'auto medium=[&](const double* z,double* dz){ auto timer=Clock::now();')
    source = source.replace('medium(y,out);', 'medium(y,out);')
    source = source.replace('put(dz,a,r);\n   }\n };',
        'put(dz,a,r);\n   }\n field_seconds+=std::chrono::duration<double>(Clock::now()-timer).count();\n };')
    source = source.replace('int mode=modes[c];', 'auto element_timer=Clock::now();\n   int mode=modes[c];')
    source = source.replace('}\n for(int i=0;i<count;i++)',
        'element_seconds+=std::chrono::duration<double>(Clock::now()-element_timer).count();\n }\n for(int i=0;i<count;i++)')
    source += '\nextern "C" void option_b_profile(double* out){out[0]=field_seconds;out[1]=element_seconds;}\n'
    instrumented = folder / 'instrumented_field.cpp'
    instrumented.write_text(source)
    library = folder / 'instrumented_field.dylib'
    build_started = time.perf_counter()
    subprocess.run(['clang++', *B.FLAGS, str(instrumented), '-o', str(library)], check=True)
    build_seconds = time.perf_counter() - build_started
    import ctypes
    lib = ctypes.CDLL(str(library.resolve()))
    reference_lib, original_record = F.native()
    lib.field_run.argtypes = reference_lib.field_run.argtypes
    lib.field_run.restype = reference_lib.field_run.restype
    lib.option_b_profile.argtypes = [ctypes.POINTER(ctypes.c_double)]
    lib.option_b_profile.restype = None
    # Temporarily select instrumentation inside this isolated process only.
    F.native = lambda: (lib, original_record)
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    baseline = {name: sha256(ROOT / name) for name in tracked if name and (ROOT / name).is_file()}
    settings = P.load_settings()
    meta = {'kind': 'OPTION_B_PROFILE_ONLY', 'entropy': settings['development_entropy'],
            'world': 0, 'pid': os.getpid(), 'native_build': native_record, 'source_pin': source_pin,
            'start_machine': machine(), 'baseline_hashes': baseline}
    meta.update(instrumented_source_sha256=sha256(instrumented), instrumented_binary_sha256=sha256(library),
                instrumentation_build_seconds=build_seconds)
    (folder / 'START.json').write_text(json.dumps(meta, indent=2) + '\n')
    print('PROFILE START pid=' + str(os.getpid()), flush=True)
    profile = cProfile.Profile()
    started = time.perf_counter()
    row = profile.runcall(P.run_world, settings, settings['development_entropy'], 0)
    compute = time.perf_counter() - started
    native_times = (ctypes.c_double * 2)()
    lib.option_b_profile(native_times)
    profile.dump_stats(str(folder / 'reference.prof'))
    stats = pstats.Stats(profile)
    functions = [{'file': k[0], 'line': k[1], 'function': k[2], 'primitive_calls': v[0],
                  'calls': v[1], 'self_seconds': v[2], 'cumulative_seconds': v[3]}
                 for k, v in stats.stats.items()]
    io_start = time.perf_counter()
    raw = json.dumps(row, allow_nan=False, separators=(',', ':')).encode()
    compressed = gzip.compress(raw, mtime=0)
    (folder / 'reference_world_000.json.gz').write_bytes(compressed)
    io_seconds = time.perf_counter() - io_start
    meta.update(compute_seconds=compute, serialization_write_seconds=io_seconds,
                total_seconds=compute + io_seconds, raw_bytes=len(raw), compressed_bytes=len(compressed),
                world_sha256=hashlib.sha256(compressed).hexdigest(), end_machine=machine(),
                native_field_rhs_seconds=native_times[0], native_element_rhs_seconds=native_times[1],
                invalid=row['invalid'], chain_complete=row['chain_complete'],
                functions=sorted(functions, key=lambda v: -v['self_seconds']))
    (folder / 'PROFILE.json').write_text(json.dumps(meta, indent=2) + '\n')
    print(json.dumps({k: meta[k] for k in ('compute_seconds', 'serialization_write_seconds', 'invalid', 'chain_complete')}), flush=True)


if __name__ == '__main__':
    main()
