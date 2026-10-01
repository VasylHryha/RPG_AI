"""Build the measured-cost C2 CPU kernel with strict float64 arithmetic."""
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]


def main():
    source=ROOT/'native/c2/relaxation.cpp'; folder=ROOT/'.gate/c2_backend'; folder.mkdir(parents=True,exist_ok=True)
    output=folder/'relaxation.dylib'
    command=['clang++','-std=c++17','-O3','-fno-fast-math','-ffp-contract=off','-dynamiclib',str(source),'-o',str(output)]
    start=time.perf_counter(); subprocess.run(command,check=True)
    record={'command':command,'compiler':subprocess.check_output(['clang++','--version'],text=True),
            'seconds':time.perf_counter()-start,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'binary_sha256':hashlib.sha256(output.read_bytes()).hexdigest()}
    (folder/'BUILD.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record))


if __name__=='__main__': main()
