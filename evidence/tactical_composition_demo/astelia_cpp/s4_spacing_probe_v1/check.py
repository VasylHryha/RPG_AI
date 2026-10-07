"""Run focused tests once after the complete change/recheck batch."""
import subprocess,sys,time
from common import *
@stage('checks',600,'prepare-only; no fights')
def main():
 start=time.time();awake=time.monotonic()
 r=subprocess.run(['/usr/bin/caffeinate','-i','-s',str(REPO/'.venv/bin/python'),'-m','pytest','-q','-x','--basetemp',str(HERE/'test_scratch'),str(HERE/'test_probe.py')],capture_output=True,text=True,timeout=min(600,remaining()),cwd=REPO)
 (HERE/'TESTS.stdout.log').write_text(r.stdout);(HERE/'TESTS.stderr.log').write_text(r.stderr)
 print(r.stdout+r.stderr);assert r.returncode==0, 'focused checks failed'
if __name__=='__main__':
 from common import caffeinate
 caffeinate();main()
