"""Build, then one affected test batch; retains timing and exact commands."""
import json,pathlib,subprocess,sys,time
root=pathlib.Path(__file__).resolve().parents[1]
repo=root.parents[2]
checks=root/'s4_v3_checks'
started=time.monotonic()
with (checks/'build.stdout.txt').open('w') as log:
    for target in ('native','s3-check','controller-check'):
        subprocess.run([sys.executable,str(root/'build.py'),'--engine',target],stdout=log,stderr=subprocess.STDOUT,check=True)
built=time.monotonic()
tests=['test_s3_controllers.py','test_native_controller.py','test_s4_v1.py','test_s4_v2.py','test_s4_v3.py','test_s4_v3_report.py','test_s4_amended.py','test_s4_amended_report.py','test_result_cache.py']
command=[sys.executable,'-m','pytest','-q','-x',*[str(root/t) for t in tests],'-k','not test_v0_fixture_summary_bytes_and_v1_engineering_fights and not test_v0_v1_fixture_bytes_and_v2_engineering']
# V3 parity has its own name and writes only its new receipt.
with (checks/'tests.stdout.txt').open('w') as log:
    result=subprocess.run(command,cwd=repo,stdout=log,stderr=subprocess.STDOUT)
(checks/'TEST_TIMING.json').write_text(json.dumps(dict(build_seconds=built-started,test_seconds=time.monotonic()-built,exit_code=result.returncode,command=command),indent=2)+'\n')
print((checks/'tests.stdout.txt').read_text())
sys.exit(result.returncode)
