"""Explicit dependency-free C++17 build; no implicit compilation on import."""
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
LIBRARY = ROOT / '_build' / ('medium.dylib' if platform.system() == 'Darwin' else 'medium.so')
CONTRACT = ROOT / '_build' / 'medium_contract'

def build(sanitize=False):
    compiler = os.environ.get('CXX') or shutil.which('clang++') or shutil.which('g++')
    if not compiler:
        raise RuntimeError('C++17 compiler required (CXX, clang++, or g++)')
    LIBRARY.parent.mkdir(exist_ok=True)
    flags = ['-std=c++17', '-O3', '-Wall', '-Wextra', '-Wpedantic', '-fno-fast-math', '-ffp-contract=off']
    if sanitize:
        flags += ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    shared = '-dynamiclib' if platform.system() == 'Darwin' else '-shared'
    commands = [
        [compiler, *flags, '-fPIC', shared, str(ROOT / 'medium.cpp'), str(ROOT / 'medium_c.cpp'), '-o', str(LIBRARY)],
        [compiler, *flags, str(ROOT / 'medium.cpp'), str(ROOT / 'medium_c.cpp'), str(ROOT / 'contract.cpp'), '-o', str(CONTRACT)],
    ]
    for command in commands:
        subprocess.run(command, check=True, cwd=ROOT)
    return {'compiler': subprocess.check_output([compiler, '--version'], text=True).splitlines()[0],
            'platform': platform.platform(), 'commands': commands}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sanitize', action='store_true')
    args = parser.parse_args()
    print(json.dumps(build(args.sanitize), indent=2))
