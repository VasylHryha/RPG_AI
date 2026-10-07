import pathlib,subprocess,time,json
HERE=pathlib.Path(__file__).resolve().parent;CPP=HERE.parent;REPO=CPP.parents[2]
start=time.time();awake=time.monotonic()
r=subprocess.run(['/usr/bin/caffeinate','-i','-s',str(REPO/'.venv/bin/python'),str(CPP/'build_focus_probe_v1.py')],capture_output=True,text=True,timeout=300,cwd=REPO)
(HERE/'BUILD.stdout.log').write_text(r.stdout);(HERE/'BUILD.stderr.log').write_text(r.stderr)
(HERE/'BUILD_TIMING.json').write_text(json.dumps(dict(returncode=r.returncode,elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake,command=r.args),indent=2)+'\n');print(r.stdout);print(r.stderr);raise SystemExit(r.returncode)
