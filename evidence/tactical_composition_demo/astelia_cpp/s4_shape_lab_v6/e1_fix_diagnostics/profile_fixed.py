"""Bounded actual CLI profile, no new fights; fail if preserved receipts drift."""
import cProfile
import faulthandler
import hashlib
import json
import pathlib
import pstats
import runpy
import signal
import sys
import time
HERE=pathlib.Path(__file__).resolve().parent
LAB=HERE.parent
profile=cProfile.Profile()
def deadline(*args):raise TimeoutError('fixed report exceeded 45-second diagnosis limit')
signal.signal(signal.SIGALRM,deadline);signal.alarm(45)
faulthandler.dump_traceback_later(10,repeat=True)
sys.argv=[str(LAB/'lab.py'),'report','--arm','E1']
started=time.monotonic()
try:
    profile.enable();runpy.run_path(str(LAB/'lab.py'),run_name='__main__')
finally:
    profile.disable();signal.alarm(0);faulthandler.cancel_dump_traceback_later()
    with (HERE/'fixed_report_profile.txt').open('w') as out:pstats.Stats(profile,stream=out).sort_stats('cumulative').print_stats(25)
    (HERE/'fixed_report_timing.json').write_text(json.dumps(dict(seconds=time.monotonic()-started,command='lab.py report --arm E1',new_fights=0),indent=2)+'\n')
manifest=json.loads((LAB/'E1_REPORTING_R2.json').read_text())
for name,digest in manifest['historical_files'].items():
    if hashlib.sha256((LAB/name).read_bytes()).hexdigest()!=digest:raise RuntimeError('historical receipt drift: '+name)
summary=json.loads((LAB/'MECHANISM_E1_SUMMARY_R2.json').read_text())
assert summary['arm']=='E1' and list(summary['arms'])==['base','E1'] and list(summary['drills'])==['D5'] and summary['complete']
assert summary['paired']['base minus E1']['n']==20
print('Original receipt hashes unchanged; corrected E1 D5 summary complete at 20 paired fights.')
