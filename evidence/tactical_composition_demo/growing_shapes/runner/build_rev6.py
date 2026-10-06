"""Build rev6 orchestration against an isolated rev6 medium and the pinned world."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import numpy as np
from ..medium.build_rev6 import build as build_medium
from ..medium.rev6_native import IMAGE as MEDIUM_IMAGE
from ..world.world import Library

HERE=Path(__file__).parent
ROOT=HERE.parents[3]
OUTPUT=HERE/'_rev6_build'/('rev6_perf.dylib' if platform.system()=='Darwin' else 'rev6_perf.so')


def build():
    medium=build_medium()
    # Read/identity verification only: never implicitly replace an existing world image.
    world=Library();world_image=Path(world.api._name)
    OUTPUT.parent.mkdir(exist_ok=True)
    command=[medium['command'][0],'-std=c++17','-O3','-Wall','-Wextra','-Wpedantic','-fno-fast-math','-ffp-contract=off','-fPIC','-dynamiclib' if platform.system()=='Darwin' else '-shared',str(HERE/'rev6_perf.cpp'),str(MEDIUM_IMAGE),str(world_image),'-o',str(OUTPUT)]
    subprocess.run(command,check=True)
    names=[HERE/'rev6_perf.cpp',HERE/'perf.h',HERE/'rev6_native.py',HERE/'build_rev6.py',HERE.parent/'native_guard.py',HERE.parent/'world/world.cpp',HERE.parent/'world/world.h',HERE.parent/'world/world.py',HERE.parent/'medium/rev6_medium.hpp']
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    result=dict(version='rev6_rhs_v1',abi=3,numpy=np.__version__,source_sha256={str(p.relative_to(ROOT)):digest(p) for p in names},binary_sha256=digest(OUTPUT),dependencies={str(p.relative_to(ROOT)):digest(p) for p in (MEDIUM_IMAGE,world_image)},command=command,medium=medium)
    (OUTPUT.parent/'build.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':print(json.dumps(build(),indent=2))
