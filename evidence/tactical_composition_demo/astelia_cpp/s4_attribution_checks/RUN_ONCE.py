"""Evidence supervisor; calls the unmodified readiness command exactly once."""
import datetime,json,pathlib,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parents[4]
CHECKS=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'evidence/tactical_composition_demo/astelia_cpp/s4_attribution_development'
if OUT.exists():
    raise SystemExit('Refuse existing output')
argv=['/usr/bin/caffeinate','-i','-s','.venv/bin/python','evidence/tactical_composition_demo/astelia_cpp/s4_attribution.py','--execute','--quiet-machine-finished','--workers','10','--output','evidence/tactical_composition_demo/astelia_cpp/s4_attribution_development']
start=time.time(); awake=time.monotonic()
record={'argv':argv,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_clock':'time.time wall clock','awake_clock':'time.monotonic, macOS mach_absolute_time (excludes system sleep)','c6_completion_evidence':'evidence/c6_option_b/QUIET_REPORT.md'}
(CHECKS/'RUN_START.json').write_text(json.dumps(record,indent=2)+'\n')
with (CHECKS/'RUN.stdout.log').open('x') as stdout,(CHECKS/'RUN.stderr.log').open('x') as stderr:
    result=subprocess.run(argv,cwd=ROOT,stdout=stdout,stderr=stderr)
record.update(returncode=result.returncode,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake)
(CHECKS/'RUN_RESULT.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
raise SystemExit(result.returncode)
