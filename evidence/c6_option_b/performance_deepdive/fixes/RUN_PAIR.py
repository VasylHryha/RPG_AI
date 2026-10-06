"""Review-fix re-measurement: one back-to-back pair on smoke world 0.

The pre-deep-dive code (detached worktree of 8214f39^, own build) and the
fixed code run at the same time as two world processes; the fixed output is
compared with the stored original reference at tolerance zero.
"""
import json, os, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]; HERE = Path(__file__).resolve().parent
PY = str(ROOT / '.venv/bin/python'); OLD = Path(sys.argv[1])
def event(**row):
    row.update(utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), load_average=list(os.getloadavg()))
    with (HERE / 'EVENTS.jsonl').open('a') as out: out.write(json.dumps(row) + '\n')
procs = []
for label, root in (('fixed_smoke_0', ROOT), ('old_smoke_0', OLD)):
    argv = [PY, 'tools/c6_option_b_check.py', '--backend', 'native', '--parallel', '--entropy', 'smoke',
            '--world', '0', '--output', str(HERE / label)]
    event(kind='start', label=label, code_root=str(root), argv=argv)
    procs.append((label, subprocess.Popen(argv, cwd=root, stdout=open(HERE / (label + '.log'), 'w'), stderr=subprocess.STDOUT)))
while any(p.poll() is None for _, p in procs):
    event(kind='sample'); time.sleep(15)
for label, p in procs:
    event(kind='end', label=label, returncode=p.returncode)
    if p.returncode: raise SystemExit(label + ' failed')
argv = [PY, 'tools/c6_option_b_compare.py', '--reference', 'evidence/c6_option_b/reference_smoke_0/world.json.gz',
        '--native', str(HERE / 'fixed_smoke_0/world.json.gz'), '--exact', '--output', str(HERE / 'fixed_smoke_0_EXACT.json')]
code = subprocess.run(argv, cwd=ROOT, capture_output=True).returncode
event(kind='compare', label='fixed_smoke_0', returncode=code)
