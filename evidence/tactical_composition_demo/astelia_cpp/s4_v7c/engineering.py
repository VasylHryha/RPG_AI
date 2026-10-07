"""One final scoped suite: no combat, no tuning, no validation fight process."""
from common import *
from native_build import build

def engineering():
 if (HERE/'SEAL.json').exists():raise RuntimeError('sealed engineering evidence immutable')
 built=read(HERE/'BUILD.json') if (HERE/'BUILD.json').exists() else build()
 if built['identity']!=admit(BINARY) or built['fixture_sha256']!=sha(HERE/'build/fixture') or built['request_checker_sha256']!=sha(HERE/'build/request_check') or built['request_checker_source_sha256']!=sha(HERE/'request_check.cpp'):raise RuntimeError('build drift')
 if not (HERE/'BUILD.json').exists():exclusive(HERE/'BUILD.json',built)
 input_hashes=engineering_inputs()
 env=dict(os.environ,TMPDIR=str(HERE/'build'));cmd=[str(REPO/'.venv/bin/python'),'-m','pytest','-q','-x',str(HERE/'test_v7.py'),'--basetemp='+str(HERE/'build/pytest_tmp')]
 started=time.monotonic();p=subprocess.run(cmd,cwd=REPO,env=env,capture_output=True,text=True,timeout=180)
 stamp=uuid.uuid4().hex
 stdout=HERE/('TESTS_'+stamp+'.stdout.log');stderr=HERE/('TESTS_'+stamp+'.stderr.log')
 stdout.write_text(p.stdout);stderr.write_text(p.stderr);seconds=time.monotonic()-started
 exclusive(HERE/('CHECK_ATTEMPT_'+stamp+'.json'),dict(status='PASS' if p.returncode==0 else 'FAILED',returncode=p.returncode,seconds=seconds,stdout=stdout.name,stderr=stderr.name,stdout_sha256=sha(stdout),stderr_sha256=sha(stderr)))
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 audit=read(HERE/'REQUEST_AUDIT.json')
 if audit['status']!='PASS' or audit['requests']!=400 or audit['executed_fights'] or audit['executed_steps'] or audit['worlds_created']:raise RuntimeError('request audit missing/invalid')
 if engineering_inputs()!=input_hashes:raise RuntimeError('inputs changed during tests')
 r=dict(status='PASS',noncombat=True,input_hashes=input_hashes,binary=admit(BINARY),fixture_sha256=sha(HERE/'build/fixture'),request_audit_sha256=sha(HERE/'REQUEST_AUDIT.json'),build_sha256=sha(HERE/'BUILD.json'),test_command=cmd,test_seconds=seconds,total_seconds=built['seconds']+sum(read(p)['seconds'] for p in HERE.glob('CHECK_ATTEMPT_*.json')),stdout_sha256=sha(stdout),stderr_sha256=sha(stderr),executed_fights=0,executed_steps=0,checks=['unchanged observation-only controller fixture','actual native parsing of all 400 validation requests','native flag constraint regression and other malformed fields','committed theta identity and no retuning','fresh entropy exclusions','fail-closed raw/attempt resume','validation-only compute cap','aggregate ten-worker throughput projection','unchanged scientific readings/measure/bootstrap'])
 write(HERE/'ENGINEERING.json',r);print(json.dumps({k:v for k,v in r.items() if k!='binary'}))

if __name__=='__main__':engineering()
