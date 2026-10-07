"""Launch exactly once under caffeinate; preserve load and elapsed/awake clocks."""
import datetime, json, os, pathlib, subprocess, time
from s4_v6_attempt2 import V
REPO = V.ROOT.parents[2]
def main():
    now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    out = V.ROOT / ('s4_v6_development_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    if out.exists() or (V.CHECKS/'LAUNCH.json').exists():
        raise RuntimeError('attempt 2 already claimed; never repeat')
    if json.loads((V.CHECKS/'CACHE_SMOKE.json').read_text())['status'] != 'PASS':
        raise RuntimeError('no-combat cache smoke did not pass')
    delivery = json.loads((V.CHECKS/'PART1_DELIVERY.json').read_text())
    V.check_inputs(delivery['runtime_hashes']); V.declaration(); V.admit(V.BINARY)
    command = ['/usr/bin/caffeinate', '-i', '-s', str(REPO/'.venv/bin/python'),
               str(V.ROOT/'s4_v6_attempt2.py'), '--implementation-commit',
               delivery['implementation_commit'], '--output', str(out)]
    elapsed = time.time(); awake = time.monotonic()
    with (V.CHECKS/'LAUNCH.json').open('x') as f:
        json.dump(dict(start_utc=now(),command=command,output=str(out),load_average=os.getloadavg(),
                       workers=10,expected_minutes=65,allowance_minutes=360,
                       policy='owner/0031: authorized second attempt; launch immediately; no load waiting'), f, indent=2)
    with (V.CHECKS/'RUN.stdout.log').open('x') as stdout, (V.CHECKS/'RUN.stderr.log').open('x') as stderr:
        p = subprocess.Popen(command, cwd=REPO, stdout=stdout, stderr=stderr)
        print('LAUNCHED', p.pid, str(out), flush=True)
        with (V.CHECKS/'LOAD_SAMPLES.jsonl').open('x') as f:
            while True:
                f.write(json.dumps(dict(utc=now(),elapsed_seconds=time.time()-elapsed,
                                        awake_seconds=time.monotonic()-awake,load_average=os.getloadavg()))+'\n');f.flush()
                try:
                    p.wait(timeout=30); break
                except subprocess.TimeoutExpired: pass
    V.write(V.CHECKS/'SUPERVISOR_TIMING.json', dict(elapsed_seconds=time.time()-elapsed,
            awake_seconds=time.monotonic()-awake,end_utc=now(),returncode=p.returncode,
            load_average_end=os.getloadavg(),caffeinate=True))
    print('FINISHED', p.returncode, flush=True)
    raise SystemExit(p.returncode)
if __name__ == '__main__': main()
