"""Explicit atomic Option B build. The reference library is never overwritten."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (ROOT/'native/c6_option_b/field.cpp', ROOT/'native/c6_option_b/detection.cpp')
LIBRARY = ROOT/'build/c6_option_b/option_b.dylib'
FLAGS = ('-std=c++17','-O2','-fno-fast-math','-ffp-contract=off','-dynamiclib','-framework','Accelerate')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build():
    LIBRARY.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(suffix='.dylib', dir=LIBRARY.parent)
    os.close(fd)
    temp = Path(name)
    started = time.perf_counter()
    try:
        subprocess.run(['clang++', *FLAGS, *(str(s) for s in SOURCES), '-o', str(temp)], check=True)
        record = {'compiler':subprocess.check_output(['clang++','--version'],text=True).splitlines()[0],
                  'flags':list(FLAGS), 'source_hashes':{str(s.relative_to(ROOT)):digest(s) for s in SOURCES},
                  'binary_sha256':digest(temp), 'build_seconds':time.perf_counter()-started}
        os.replace(temp, LIBRARY)
        record_path = LIBRARY.parent/'BUILD.json'
        temp_record = record_path.with_suffix('.tmp')
        temp_record.write_text(json.dumps(record, indent=2)+'\n')
        os.replace(temp_record, record_path)
        return record
    finally:
        temp.unlink(missing_ok=True)

if __name__ == '__main__':
    print(json.dumps(build()))
