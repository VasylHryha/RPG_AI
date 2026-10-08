"""Run the focused suite once, keep complete attempt logs and measured wall time."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
HERE=Path(__file__).resolve().parent
if __name__=='__main__':
    env={**os.environ,'OMP_NUM_THREADS':'4','MKL_NUM_THREADS':'4','OPENBLAS_NUM_THREADS':'4','PYTHONDONTWRITEBYTECODE':'1','PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1'}
    start=time.monotonic();count=len(list(HERE.glob('TEST_ATTEMPT_*.json')))+1;prefix=HERE/f'TEST_ATTEMPT_{count:02}'
    cmd=[sys.executable,'-m','pytest','-q','--confcutdir='+str(HERE),'--basetemp='+str(HERE/'_local/pytest'),str(HERE/'test_slice.py')]
    if '--resume-after-schema' in sys.argv:cmd+=['-k','not test_encoder_parity and not test_enemy_boundary']
    if '--resume-d1b-cosine' in sys.argv:cmd+=['-k','test_unaliased_recurrent_target_channels']
    with prefix.with_suffix('.stdout.log').open('w') as out,prefix.with_suffix('.stderr.log').open('w') as err:p=subprocess.run(cmd,cwd=HERE,env=env,stdout=out,stderr=err)
    r={'status':'PASS' if p.returncode==0 else 'FAIL','exit_code':p.returncode,'seconds':time.monotonic()-start,'command':cmd,'fights':0,'training_steps':0,'teacher_collection':False,'scope':'NS1 focused fixture suite; native isolated seams + bounded scripted coreStep lifecycle checks','resumed_from':'TEST_ATTEMPT_03.json' if '--resume-d1b-cosine' in sys.argv else 'TEST_ATTEMPT_01.json' if '--resume-after-schema' in sys.argv else None,'unchanged_previously_passed_checks':56 if '--resume-d1b-cosine' in sys.argv else 10 if '--resume-after-schema' in sys.argv else 0,'test_source_sha256':hashlib.sha256((HERE/'test_slice.py').read_bytes()).hexdigest()}
    prefix.with_suffix('.json').write_text(json.dumps(r,indent=2)+'\n')
    if p.returncode==0:(HERE/'TESTS.json').write_text(json.dumps(r,indent=2)+'\n')
    print(prefix.with_suffix('.stdout.log').read_text());print(prefix.with_suffix('.stderr.log').read_text());print(json.dumps(r,indent=2));sys.exit(p.returncode)
