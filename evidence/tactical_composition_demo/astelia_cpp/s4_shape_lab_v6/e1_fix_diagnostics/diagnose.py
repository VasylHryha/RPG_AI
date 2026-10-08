"""Bounded diagnosis on saved source; no native execution or receipt writes."""
import cProfile
import faulthandler
import json
import pathlib
import pstats
import subprocess
import sys
import time
HERE=pathlib.Path(__file__).resolve().parent
LAB=HERE.parent
if len(sys.argv)==1:
    # Child reads a source copy, with all telemetry/identity inputs read-only.
    started=time.monotonic()
    with (HERE/'original_report_stack.log').open('w') as out:
        try:
            result=subprocess.run([sys.executable,'-B',__file__,'child'],stdout=out,stderr=out,timeout=12)
            state=dict(returncode=result.returncode)
        except subprocess.TimeoutExpired:
            state=dict(status='TERMINATED_AT_DIAGNOSTIC_LIMIT',limit_seconds=12)
    (HERE/'original_report_timing.json').write_text(json.dumps(dict(seconds=time.monotonic()-started,**state),indent=2)+'\n')
else:
    sys.path.insert(0,str(LAB))
    # Load the saved CLI code as a distinct namespace just like python lab.py.
    source=(HERE/'original/lab.py').read_text().replace("if __name__=='__main__': main()",'')
    cli=dict(__file__=str(LAB/'lab.py'),__name__='__main__')
    exec(compile(source,str(HERE/'original/lab.py'),'exec'),cli)
    cli['SELECTED_ARM']='E1'
    import lab,report
    original=lab.records_for
    lab.records_for=lambda stage:{}
    path,summary=cli['stage_summary']('mechanism')
    print(json.dumps(dict(cli_arm=cli['SELECTED_ARM'],report_arm=lab.SELECTED_ARM,path=path.name,summary_arm=summary['arm'],drills=list(summary['drills'])),indent=2),flush=True)
    lab.records_for=original
    def no_write(*args,**kwargs):raise RuntimeError('diagnosis forbids report writes')
    lab.write=no_write
    faulthandler.dump_traceback_later(3,repeat=True)
    profile=cProfile.Profile()
    try:
        profile.enable()
        report.render()
    finally:
        profile.disable()
        with (HERE/'original_report_profile.txt').open('w') as out:pstats.Stats(profile,stream=out).sort_stats('cumulative').print_stats(25)
