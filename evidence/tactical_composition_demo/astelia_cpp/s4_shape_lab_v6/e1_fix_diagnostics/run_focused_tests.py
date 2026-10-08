"""Run original v6 and R2 focused tests once, redirecting native fixture outputs."""
import json
import os
import pathlib
import subprocess
import sys
import time
HERE=pathlib.Path(__file__).resolve().parent
LAB=HERE.parent
RUNTIME=HERE/'_runtime'
RUNTIME.mkdir(exist_ok=True)
source=(LAB/'test_lab.py').read_text()
source=source.replace('HERE=pathlib.Path(__file__).resolve().parent',f'HERE=pathlib.Path({str(LAB)!r})\nOUTPUT=pathlib.Path({str(HERE)!r})')
source=source.replace("(HERE/f'{name.upper()}.stdout.log')","(OUTPUT/f'{name.upper()}.stdout.log')").replace("(HERE/f'{name.upper()}.stderr.log')","(OUTPUT/f'{name.upper()}.stderr.log')").replace("lab.write(HERE/'NATIVE_FIXTURES.json'","lab.write(OUTPUT/'NATIVE_FIXTURES_R2.json'")
copy=RUNTIME/'test_original_v6.py';copy.write_text(source)
args=[sys.executable,'-B','-m','pytest','-q','-x',str(copy),str(LAB/'test_e1_r2.py'),'--basetemp',str(RUNTIME/'pytest_tmp'),'-p','no:cacheprovider']
started=time.monotonic()
with (HERE/'TESTS_E1_R2.stdout.log').open('w') as out, (HERE/'TESTS_E1_R2.stderr.log').open('w') as err:
    result=subprocess.run(args,stdout=out,stderr=err,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},timeout=120)
receipt=dict(status='PASS' if result.returncode==0 else 'FAIL',returncode=result.returncode,seconds=time.monotonic()-started,command=args,fights=0,scope='Original v6 focused Python/native fixtures plus R2 reporting regressions. Original test source unchanged; only fixture output paths redirected in runtime copy.')
(HERE/'TESTS_E1_R2.json').write_text(json.dumps(receipt,indent=2)+'\n')
print((HERE/'TESTS_E1_R2.stdout.log').read_text())
print((HERE/'TESTS_E1_R2.stderr.log').read_text())
print(json.dumps(receipt,indent=2))
raise SystemExit(result.returncode)
