"""One authorized engineering verification batch; no section-10 execution."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
MEDIUM = HERE.parent/'medium'
PYTHON = ROOT/'.venv/bin/python'


def command(args, output):
    start = time.perf_counter()
    with output.open('w') as log:
        result = subprocess.run(args, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    return {'command': [str(a) for a in args], 'seconds': time.perf_counter()-start,
            'exit_code': result.returncode, 'log': output.name}


def main():
    build = command([PYTHON, MEDIUM/'build.py'], HERE/'BUILD_LOG.txt')
    if build['exit_code']:
        raise SystemExit('Build failed; see BUILD_LOG.txt')
    tests = command([PYTHON, '-m', 'pytest', '-q', '-x', '-p', 'no:cacheprovider',
                     MEDIUM/'test_medium.py', MEDIUM/'test_design_0h.py', HERE/'test_runner.py'], HERE/'TEST_LOG.txt')
    stages = {'build':build, 'tests':tests}
    if tests['exit_code'] == 0:
        stages['smoke'] = command([PYTHON, '-m', 'evidence.tactical_composition_demo.growing_shapes.runner.run',
                                  '--smoke', '--seed', '105051', '--episodes', '8', '--output', HERE/'SMOKE.json'],
                                 HERE/'SMOKE_LOG.txt')
    sources = list(MEDIUM.glob('*.py'))+list(MEDIUM.glob('*.cpp'))+list(MEDIUM.glob('*.hpp'))+list(MEDIUM.glob('*.h'))+list(HERE.glob('*.py'))
    frozen = [ROOT/'geomind/c4_detect.py',ROOT/'geomind/c4_model.py',ROOT/'geomind/c5_detect.py']
    receipt = {'label':'engineering-only; not development evidence', 'stages':stages,
               'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
               'frozen_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in frozen if p.exists()},
               'design_sha256':hashlib.sha256((HERE.parents[1]/'DESIGN_0H.md').read_bytes()).hexdigest(),
               'native_build':json.loads((MEDIUM/'_build/build.json').read_text())}
    (HERE/'CHECKS.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(stages,indent=2))
    if tests['exit_code'] or stages.get('smoke',{}).get('exit_code'):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
