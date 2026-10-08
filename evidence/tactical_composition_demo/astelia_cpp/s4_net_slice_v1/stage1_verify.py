"""Single final focused test batch, new receipts only; no fights or fitting."""
import os
import subprocess
import sys
import time
from collection import HERE,atomic,sha


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--attempt',type=int,default=1); parser.add_argument('--reason')
    parser.add_argument('--stage1-only',action='store_true')
    args=parser.parse_args()
    from stage1_train import environment
    environment()
    if args.attempt>1 and not args.reason:
        raise RuntimeError('a later focused batch needs a concrete change/failure reason')
    prefix=HERE/('STAGE1_TESTS' if args.attempt==1 else f'STAGE1_TESTS_R{args.attempt:02}')
    if prefix.with_suffix('.json').exists():
        raise RuntimeError('focused suite already recorded; rerun only for a specific failure/change')
    env={**os.environ,'OMP_NUM_THREADS':'4','MKL_NUM_THREADS':'4','OPENBLAS_NUM_THREADS':'4',
         'PYTHONDONTWRITEBYTECODE':'1','PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1'}
    names=('test_stage1.py',) if args.stage1_only else ('test_slice.py','test_collection.py','test_disk_reserve_admission.py','test_stage1.py')
    command=[sys.executable,'-m','pytest','-q','-x','--confcutdir='+str(HERE),'--basetemp='+str(HERE/'_local/stage1/pytest'),*[str(HERE/n) for n in names]]
    start=time.monotonic()
    with prefix.with_suffix('.stdout.log').open('w') as out,prefix.with_suffix('.stderr.log').open('w') as err:
        result=subprocess.run(command,env=env,stdout=out,stderr=err)
    value=dict(status='PASS' if not result.returncode else 'FAIL',command=command,wall_seconds=time.monotonic()-start,
               exit_code=result.returncode,test_sources={n:sha(HERE/n) for n in names},reason=args.reason,physical_fights=0,training_steps=0)
    atomic(prefix.with_suffix('.json'),value)
    print(prefix.with_suffix('.stdout.log').read_text()); print(prefix.with_suffix('.stderr.log').read_text())
    if result.returncode:
        sys.exit(result.returncode)
    from stage1_export import teacher_baseline
    teacher_baseline()
