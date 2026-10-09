"""Small no-combat replay executable, same patched inference as host build."""
import subprocess,sys
from pathlib import Path
import runtime as r
from build import prepare_sources

def compile_fixture(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);prepare_sources(out)
    record=r.read((r.A_LOCAL/'build/tactics_react_host_stagea').with_suffix('.build.json'))
    raw=record['commands'][0];includes=[a for a in raw if a.startswith('-I')]
    binary=out/'zero_combat_replay'
    argv=['nice','-n','15',raw[0],'-std=c++17','-O0','-ffp-contract=off','-I'+str(out),'-I'+str(r.HERE),*includes,str(out/'stagea.cpp'),str(r.HERE/'native_fixture.cpp'),'-Wl,-dead_strip','-o',str(binary)]
    subprocess.run(argv,check=True,capture_output=True,text=True,timeout=45)
    return binary
