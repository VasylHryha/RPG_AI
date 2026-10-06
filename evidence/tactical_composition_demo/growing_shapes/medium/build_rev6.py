"""Explicit, isolated build of revision-6 images. Builds no legacy artifacts."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
from .rev6_native import BUILD, IMAGE, HERE


def build():
    BUILD.mkdir(exist_ok=True)
    compiler=os.environ.get('CXX') or shutil.which('clang++') or shutil.which('g++')
    if not compiler: raise RuntimeError('C++17 compiler required')
    flags=['-std=c++17','-O3','-Wall','-Wextra','-Wpedantic','-fno-fast-math','-ffp-contract=off']
    shared='-dynamiclib' if platform.system()=='Darwin' else '-shared'
    command=[compiler,*flags,'-fPIC',shared,str(HERE/'rev6_medium.cpp'),str(HERE/'rev6_medium_c.cpp'),'-o',str(IMAGE)]
    subprocess.run(command,check=True)
    names=('rev6_medium.cpp','rev6_medium_c.cpp','rev6_medium.hpp','medium_c.h','rev6_native.py','medium.py','build_rev6.py','../native_guard.py')
    receipt=dict(version='rev6_rhs_v1',source_sha256={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in names},binary_sha256=hashlib.sha256(IMAGE.read_bytes()).hexdigest(),command=command,compiler=subprocess.check_output([compiler,'--version'],text=True).splitlines()[0])
    (BUILD/'build.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt

if __name__=='__main__': print(json.dumps(build(),indent=2))
