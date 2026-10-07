import pathlib,json,subprocess,time
HERE=pathlib.Path(__file__).resolve().parent;REPO=HERE.parents[3]
start=time.time();awake=time.monotonic();r=subprocess.run(['/usr/bin/caffeinate','-i','-s',str(REPO/'.venv/bin/python'),'-m','pytest','-q','-x',str(HERE/'test_probe.py')],capture_output=True,text=True,timeout=600,cwd=REPO)
(HERE/'TESTS.stdout.log').write_text(r.stdout);(HERE/'TESTS.stderr.log').write_text(r.stderr)
(HERE/'CHECK_TIMING.json').write_text(json.dumps(dict(returncode=r.returncode,elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake,command=r.args),indent=2)+'\n');print(r.stdout);print(r.stderr);raise SystemExit(r.returncode)
