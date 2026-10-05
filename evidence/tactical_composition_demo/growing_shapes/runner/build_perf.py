"""Explicit native orchestration build with pinned dependency identities."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import numpy as np
from ..medium.build import LIBRARY as MEDIUM_LIBRARY
from ..medium.build import build as build_medium
from ..world.build import build as build_world, LIBRARY as WORLD_LIBRARY

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUTPUT = HERE/'_build'/('perf.dylib' if platform.system() == 'Darwin' else 'perf.so')
SOURCES = [HERE/'perf.cpp', HERE/'perf.h', HERE/'build_perf.py',
           *[HERE.parent/'medium'/n for n in ('medium.cpp','medium_c.cpp','medium.hpp','medium_c.h')],
           *[HERE.parent/'world'/n for n in ('world.cpp','world.h')]]
SOURCES += [HERE.parent/'medium/build.py', HERE.parent/'world/build.py', HERE/'native.py']
SOURCES += [HERE.parent/'medium/medium.py', HERE.parent/'world/world.py']
SOURCES += [HERE.parent/'native_guard.py']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    OUTPUT.parent.mkdir(exist_ok=True)
    (OUTPUT.parent/'build.json').unlink(missing_ok=True)
    medium = build_medium()
    world = build_world()
    OUTPUT.parent.mkdir(exist_ok=True)
    (OUTPUT.parent/'build.json').unlink(missing_ok=True)
    compiler = medium['commands'][0][0]
    flags = ['-std=c++17','-O3','-Wall','-Wextra','-Wpedantic','-fno-fast-math','-ffp-contract=off']
    shared = '-dynamiclib' if platform.system() == 'Darwin' else '-shared'
    command = [compiler,*flags,'-fPIC',shared,str(HERE/'perf.cpp'),
               str(MEDIUM_LIBRARY),str(WORLD_LIBRARY),'-o',str(OUTPUT)]
    subprocess.run(command,check=True)
    manifest = {'source_sha256':{str(p.relative_to(ROOT)):digest(p) for p in SOURCES},
                'binary_sha256':digest(OUTPUT),'command':command,
                'compiler':medium['compiler'],'platform':platform.platform(),
                'numpy':np.__version__, 'abi':3,
                'dependencies':{str(p.relative_to(ROOT)):digest(p) for p in (MEDIUM_LIBRARY,WORLD_LIBRARY)},
                'medium':medium['identity'],'world':world}
    (OUTPUT.parent/'build.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    print(json.dumps(build(),indent=2))
