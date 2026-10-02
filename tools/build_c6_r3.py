"""Build only the R3-owned directed kernel; preserve prior engines."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'native/c6_r3/background.cpp'
LIBRARY = ROOT / 'build/c6_r3/background.dylib'
FLAGS = ('-std=c++17', '-O2', '-fno-fast-math', '-ffp-contract=off', '-dynamiclib')


def build():
    compiler = subprocess.check_output(['clang++', '--version'], text=True).splitlines()[0]
    LIBRARY.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['clang++', *FLAGS, str(SOURCE), '-o', str(LIBRARY)], check=True)
    record = {'compiler': compiler, 'flags': list(FLAGS),
              'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'binary_sha256': hashlib.sha256(LIBRARY.read_bytes()).hexdigest()}
    (LIBRARY.parent / 'BUILD.json').write_text(json.dumps(record, indent=2) + '\n')
    return record


if __name__ == '__main__':
    print(json.dumps(build()))
