"""Explicit, serialized Option B build; source snapshots bind the binary identity."""
import fcntl
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


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    LIBRARY.parent.mkdir(parents=True, exist_ok=True)
    # Binary and record replacement are two operations. Readers verify both and
    # fail closed on a transient mismatch; builders serialize their publication.
    with (LIBRARY.parent/'BUILD.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        with tempfile.TemporaryDirectory(prefix='option-b-',dir=LIBRARY.parent) as directory:
            scratch=Path(directory)
            snapshots=[];hashes={}
            for source in SOURCES:
                data=source.read_bytes();snapshot=scratch/source.name
                snapshot.write_bytes(data);snapshots.append(snapshot)
                hashes[str(source.relative_to(ROOT))]=hashlib.sha256(data).hexdigest()
            temp=scratch/'option_b.dylib';started=time.perf_counter()
            compiler=subprocess.check_output(['clang++','--version'],text=True)
            subprocess.run(['clang++', *FLAGS, *(str(s) for s in snapshots), '-o', str(temp)], check=True)
            if hashes!={str(s.relative_to(ROOT)):digest(s) for s in SOURCES}:
                raise RuntimeError('Option B sources changed during build; nothing published')
            record={'compiler':compiler.splitlines()[0], 'compiler_version':compiler,
                    'platform':platform.system(), 'architecture':platform.machine(),
                    'flags':list(FLAGS), 'source_hashes':hashes,
                    'binary_sha256':digest(temp), 'build_seconds':time.perf_counter()-started}
            temp_record=scratch/'BUILD.json'
            temp_record.write_text(json.dumps(record,indent=2)+'\n')
            os.replace(temp,LIBRARY)
            os.replace(temp_record,LIBRARY.parent/'BUILD.json')
            return record


if __name__ == '__main__':
    print(json.dumps(build()))
