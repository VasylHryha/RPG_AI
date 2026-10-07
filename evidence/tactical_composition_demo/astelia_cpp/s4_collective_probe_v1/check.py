import pathlib,json,subprocess,time,sys
HERE=pathlib.Path(__file__).resolve().parent;REPO=HERE.parents[3]
selectors=[str(HERE/'test_probe.py')+'::'+n for n in ('test_p5_parity','test_measurement_axes','test_stored_telemetry_metrics')] if '--resume' in sys.argv else [str(HERE/'test_probe.py')]
start=time.time();awake=time.monotonic();r=subprocess.run(['/usr/bin/caffeinate','-i','-s',str(REPO/'.venv/bin/python'),'-m','pytest','-q','-x','--basetemp',str(HERE/'test_scratch'),*selectors],capture_output=True,text=True,timeout=600,cwd=REPO)
(HERE/'TESTS.stdout.log').write_text(r.stdout);(HERE/'TESTS.stderr.log').write_text(r.stderr);(HERE/'CHECK_TIMING.json').write_text(json.dumps(dict(returncode=r.returncode,elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake),indent=2)+'\n');print(r.stdout);print(r.stderr);raise SystemExit(r.returncode)
