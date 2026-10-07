"""One final focused non-combat test batch."""
from common import *
@stage('checks',600)
def main():
 pins();admit(BINARY)
 r=subprocess.run([str(REPO/'.venv/bin/python'),'-m','pytest','-q','-x','--basetemp',str(HERE/'test_scratch'),str(HERE/'test_probe.py')],capture_output=True,text=True,timeout=remaining(),cwd=REPO)
 (HERE/'TESTS.stdout.log').write_text(r.stdout);(HERE/'TESTS.stderr.log').write_text(r.stderr);print(r.stdout+r.stderr,flush=True)
 write(HERE/'CHECKS.json',dict(status='PASS' if r.returncode==0 else 'FAIL',noncombat=True,binary_identity=admit(BINARY),declaration_sha256=sha(HERE/'DECLARATION.json'),utc_end=utc()));assert r.returncode==0
if __name__=='__main__':caffeinate();main()
