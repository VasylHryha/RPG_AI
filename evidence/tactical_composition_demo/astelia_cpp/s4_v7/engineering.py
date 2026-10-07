"""Build and all appropriate new tests once; exclusively observation/fake fixtures."""
from common import *
from native_build import build

def engineering():
 start=time.monotonic()
 built=read(HERE/'BUILD.json') if (HERE/'BUILD.json').exists() else build()
 if built['identity']!=admit(BINARY) or built['fixture_sha256']!=sha(HERE/'build/fixture'):raise RuntimeError('existing build drift; rebuild before engineering')
 write(HERE/'BUILD.json',built)
 env=dict(os.environ,TMPDIR=str(HERE/'build'));cmd=[str(REPO/'.venv/bin/python'),'-m','pytest','-q','-x',str(HERE/'test_v7.py'),'--basetemp='+str(HERE/'build/pytest_tmp')]
 test_start=time.monotonic();p=subprocess.run(cmd,cwd=REPO,env=env,capture_output=True,text=True,timeout=180)
 (HERE/'TESTS.stdout.log').write_text(p.stdout);(HERE/'TESTS.stderr.log').write_text(p.stderr)
 seconds=time.monotonic()-test_start
 write(HERE/('CHECK_ATTEMPT_'+uuid.uuid4().hex+'.json'),dict(status='PASS' if p.returncode==0 else 'FAILED',returncode=p.returncode,seconds=seconds,stdout_sha256=sha(HERE/'TESTS.stdout.log'),stderr_sha256=sha(HERE/'TESTS.stderr.log')))
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 r=dict(status='PASS',noncombat=True,binary=admit(BINARY),fixture_sha256=sha(HERE/'build/fixture'),test_command=cmd,test_seconds=seconds,total_seconds=built['seconds']+sum(read(p)['seconds'] for p in HERE.glob('CHECK_ATTEMPT_*.json')),stdout_sha256=sha(HERE/'TESTS.stdout.log'),stderr_sha256=sha(HERE/'TESTS.stderr.log'),checks=['complete forced command/state identity at four vectors','same prepared baseline','mixed mode/all living assignments','hysteresis and pair history','target death/reassignment','clone/isolation','v6 z identity and rejection','CMA ranking/start/cross-generation/failure/boundaries','bootstrap/floor/ceiling','pgrep anchoring/unavailable','ambiguous resume/cap'])
 write(HERE/'ENGINEERING.json',r);print(json.dumps(r))
if __name__=='__main__':engineering()
