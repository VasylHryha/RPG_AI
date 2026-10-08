"""Final focused corrective batch. No fights, samples, fits or baseline rewrites."""
import argparse
import os
import subprocess
import sys
import time
from collection import HERE,sha,atomic

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--attempt',type=int,default=1); parser.add_argument('--reason',required=True); args=parser.parse_args()
    prefix=HERE/f'STAGE1_SPEED_TESTS_{args.attempt:02}'
    if prefix.with_suffix('.json').exists():
        raise RuntimeError('focused batch already recorded; preserve and use next attempt for concrete failure/change only')
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1',
         'OMP_NUM_THREADS':'2','MKL_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2'}
    names=('test_stage1.py','test_stage1_v2.py')
    command=[sys.executable,'-m','pytest','-q','-x','--confcutdir='+str(HERE),'--basetemp='+str(HERE/'_local/stage1_v2/pytest'),*[str(HERE/n) for n in names]]
    (HERE/'_local/stage1_v2').mkdir(parents=True,exist_ok=True)
    start=time.monotonic()
    with prefix.with_suffix('.stdout.log').open('w') as out,prefix.with_suffix('.stderr.log').open('w') as err:
        result=subprocess.run(command,env=env,stdout=out,stderr=err)
    atomic(prefix.with_suffix('.json'),dict(status='PASS' if result.returncode==0 else 'FAIL',exit_code=result.returncode,
        wall_seconds=time.monotonic()-start,command=command,reason=args.reason,
        physical_fights=0,training_steps=0,test_sources={n:sha(HERE/n) for n in names}))
    print(prefix.with_suffix('.stdout.log').read_text());print(prefix.with_suffix('.stderr.log').read_text())
    sys.exit(result.returncode)
