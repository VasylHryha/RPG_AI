"""Performance deep-dive measurement batch (engineering only, non-final entropy).

Phase A: back-to-back A/B on smoke world 0. Each pair runs the pre-change code
(a detached git worktree of the parent commit, with its own build) and the
changed code at the same time, as two world processes (the readiness rule's
two-world budget), so both see the same machine load. Two pairs, launch order
swapped. Phase B: changed code on smoke 1 (with the full per-call audit),
development 0, development 1 and smoke 0 (reverse task submission). Every
output is compared with its stored original-reference world at tolerance zero.
"""
import json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PY = str(ROOT / '.venv/bin/python')
OLD = Path(sys.argv[1])  # detached worktree of the parent commit (built)
REF = {('smoke', 0): 'evidence/c6_option_b/reference_smoke_0/world.json.gz',
       ('smoke', 1): 'evidence/c6_option_b/reference_smoke_1/world.json.gz',
       ('development', 0): 'evidence/c6_option_b/profile_run/reference_world_000.json.gz',
       ('development', 1): 'evidence/c6_option_b/quiet_session_20261006_161801/worlds/reference_development_1/world.json.gz'}
EVENTS = HERE / 'EVENTS.jsonl'


def event(**row):
    row.update(utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), load_average=list(os.getloadavg()))
    with EVENTS.open('a') as out:
        out.write(json.dumps(row) + '\n')


def launch(label, code_root, entropy, world, extra=()):
    out = HERE / label
    argv = [PY, 'tools/c6_option_b_check.py', '--backend', 'native', '--parallel', '--entropy', entropy,
            '--world', str(world), '--output', str(out), *extra]
    log = open(HERE / (label + '.log'), 'w')
    event(kind='start', label=label, code_root=str(code_root), argv=argv)
    return label, entropy, world, subprocess.Popen(argv, cwd=code_root, stdout=log, stderr=subprocess.STDOUT)


def finish(procs):
    pending = list(procs)
    while pending:
        for item in list(pending):
            if item[3].poll() is not None:
                event(kind='end', label=item[0], returncode=item[3].returncode)
                pending.remove(item)
        if pending:
            event(kind='sample')
            time.sleep(15)
    for label, entropy, world, proc in procs:
        if proc.returncode:
            raise SystemExit(label + ' failed')


def compare(label, entropy, world):
    out = HERE / (label + '_EXACT.json')
    argv = [PY, 'tools/c6_option_b_compare.py', '--reference', REF[(entropy, world)],
            '--native', str(HERE / label / 'world.json.gz'), '--exact', '--output', str(out)]
    code = subprocess.run(argv, cwd=ROOT, capture_output=True).returncode
    event(kind='compare', label=label, returncode=code)
    return code


def main():
    jobs = []
    for pair, order in ((1, ('old', 'new')), (2, ('new', 'old'))):
        procs = [launch(f'ab{pair}_{v}_smoke_0', OLD if v == 'old' else ROOT, 'smoke', 0) for v in order]
        finish(procs); jobs += [(p[0], 'smoke', 0) for p in procs]
    procs = [launch('new_smoke_1_audit', ROOT, 'smoke', 1, ('--audit',)),
             launch('new_development_0', ROOT, 'development', 0)]
    finish(procs); jobs += [(p[0], p[1], p[2]) for p in procs]
    procs = [launch('new_development_1', ROOT, 'development', 1),
             launch('new_smoke_0_reverse', ROOT, 'smoke', 0, ('--schedule', 'reverse'))]
    finish(procs); jobs += [(p[0], p[1], p[2]) for p in procs]
    failed = [label for label, e, w in jobs if compare(label, e, w)]
    event(kind='done', failed_comparisons=failed)


if __name__ == '__main__':
    main()
