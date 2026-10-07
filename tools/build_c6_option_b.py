"""Explicit, serialized Option B build; source snapshots bind the binary identity."""
import fcntl
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (ROOT/'native/c6_option_b/field.cpp', ROOT/'native/c6_option_b/detection.cpp')
LIBRARY = ROOT/'build/c6_option_b/option_b.dylib'
FLAGS = ('-std=c++17','-O2','-fno-fast-math','-ffp-contract=off','-dynamiclib')
PINNED_MACOS = {'ProductName':'macOS','ProductVersion':'26.6.2','BuildVersion':'25G83'}

def kernel():
    value=os.environ.get('C6_OPTION_B_KERNEL','inexact')
    if value not in ('exact','inexact'): raise ValueError('Unknown C6_OPTION_B_KERNEL: '+value)
    return value

def library_for(selected):
    if selected not in ('exact','inexact'): raise ValueError('Unknown kernel: '+selected)
    return LIBRARY if selected=='inexact' else LIBRARY.parent/'exact'/LIBRARY.name

def flags_for(selected):
    library_for(selected)  # validate
    return FLAGS+('-DC6_OPTION_B_INEXACT='+str(int(selected=='inexact')),)+(
        ('-framework','Accelerate') if selected=='inexact' else ())

def macos_build():
    raw=subprocess.check_output(['sw_vers'],text=True)
    return {k.strip():v.strip() for k,v in (line.split(':',1) for line in raw.splitlines())}

def require_platform():
    observed=macos_build()
    if observed!=PINNED_MACOS:
        raise RuntimeError('Option B macOS build changed; reverify and regenerate references before use')
    return observed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(selected=None):
    selected=selected or kernel();library=library_for(selected);flags=flags_for(selected)
    os_build=require_platform()
    library.parent.mkdir(parents=True, exist_ok=True)
    # Binary and record replacement are two operations. Readers verify both and
    # fail closed on a transient mismatch; builders serialize their publication.
    with (library.parent/'BUILD.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        with tempfile.TemporaryDirectory(prefix='option-b-',dir=library.parent) as directory:
            scratch=Path(directory)
            snapshots=[];hashes={}
            for source in SOURCES:
                data=source.read_bytes();snapshot=scratch/source.name
                snapshot.write_bytes(data);snapshots.append(snapshot)
                hashes[str(source.relative_to(ROOT))]=hashlib.sha256(data).hexdigest()
            temp=scratch/'option_b.dylib';started=time.perf_counter()
            compiler=subprocess.check_output(['clang++','--version'],text=True)
            subprocess.run(['clang++', *flags, *(str(s) for s in snapshots), '-o', str(temp)], check=True)
            if hashes!={str(s.relative_to(ROOT)):digest(s) for s in SOURCES}:
                raise RuntimeError('Option B sources changed during build; nothing published')
            record={'compiler':compiler.splitlines()[0], 'compiler_version':compiler,
                    'platform':platform.system(), 'architecture':platform.machine(),
                    'flags':list(flags), 'source_hashes':hashes, 'kernel':selected,
                    'macos_build':os_build,
                    'binary_sha256':digest(temp), 'build_seconds':time.perf_counter()-started}
            temp_record=scratch/'BUILD.json'
            temp_record.write_text(json.dumps(record,indent=2)+'\n')
            os.replace(temp,library)
            os.replace(temp_record,library.parent/'BUILD.json')
            return record


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kernel',choices=('exact','inexact'),default=kernel())
    print(json.dumps(build(parser.parse_args().kernel)))
