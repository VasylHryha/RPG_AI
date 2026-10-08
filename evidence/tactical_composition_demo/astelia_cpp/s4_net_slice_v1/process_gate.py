"""Repository-scoped v3+ ownership pattern; fail closed, one vanished-PID retry."""
import json
import os
import pathlib
import re
import shlex
import subprocess
import time
HERE=pathlib.Path(__file__).resolve().parent
REPO_ROOT=HERE.parents[3].resolve()
GATE_PATH=HERE/'_local/collection/PROCESS_GATE.json'
HEAVY_PATTERN=r'(^|/)(net_host|tactics_lab_host|tactics_react_host[^ ]*|astelia_native[^ ]*)( |$)|[Pp]ython[^ ]* .*medium[^ ]*(runner|run|variants)'
def write(path,row):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(row,indent=2)+'\n')
    os.replace(temporary,path)

SCRATCH_COMPONENT = '-Users-new-RiderProjects-ai-RPG-test'


def scoped_path(value, cwd=None):
    """Resolve path-valued argv entries, with exact directory boundaries."""
    path = pathlib.Path(value).expanduser()
    if not path.is_absolute():
        if cwd is None:
            return None
        path = pathlib.Path(cwd) / path
        # A bare PATH executable (e.g. python3) is not a file in the cwd.
        if '/' not in value and not path.exists():
            return None
    # The encoded Claude directory names are not ordinary repo symlinks.
    lexical = pathlib.Path(os.path.abspath(path))
    if SCRATCH_COMPONENT in lexical.parts and any(
            part.startswith('claude-') for part in lexical.parts):
        return dict(path=str(lexical), reason='this repository encoded Claude scratch directory')
    resolved = path.resolve()
    if resolved.is_relative_to(REPO_ROOT):
        return dict(path=str(resolved), reason='path resolves under this repository')
    return None


def classify_process(pid, command):
    try:
        argv = shlex.split(command)
    except ValueError:
        raise RuntimeError('cannot parse heavy process command')
    if not argv:
        raise RuntimeError('empty heavy process command')
    # Consider executable and path-valued arguments, including --input=/path.
    values = [arg.split('=', 1)[-1] if arg.startswith('-') and '=' in arg else arg for arg in argv]
    paths = [arg for arg in values if not arg.startswith('-') and not re.match(r'^[A-Za-z][A-Za-z0-9+.-]*://', arg)]
    for value in paths:
        if pathlib.Path(value).expanduser().is_absolute():
            match = scoped_path(value)
            if match:
                return dict(pid=pid, command=command, **match)
    executable = argv[0]
    if '/' not in executable and (executable == 'tactics_lab_host' or executable.startswith(('tactics_react_host','astelia_native','net_host'))):
        text_query = subprocess.run(['lsof', '-a', '-p', str(pid), '-d', 'txt', '-Fn'],
                                    capture_output=True, text=True, timeout=10)
        executable_paths = {line[1:] for line in text_query.stdout.splitlines()
                            if line.startswith('n/') and pathlib.Path(line[1:]).name == executable}
        # txt may include libraries; only the named native executable counts.
        if text_query.returncode != 0 or text_query.stderr.strip() or len(executable_paths) != 1:
            raise RuntimeError('heavy process executable path unavailable')
        executable_path = executable_paths.pop()
        match = scoped_path(executable_path)
        if match:
            return dict(pid=pid, command=command, **match)
        paths = [value for value in paths if value != executable]
    relative = [value for value in paths if not pathlib.Path(value).expanduser().is_absolute() and not value.startswith('-')]
    if relative:
        cwd_query = subprocess.run(['lsof', '-a', '-p', str(pid), '-d', 'cwd', '-Fn'],
                                   capture_output=True, text=True, timeout=10)
        cwd_paths = [line[1:] for line in cwd_query.stdout.splitlines() if line.startswith('n/')]
        if cwd_query.returncode != 0 or cwd_query.stderr.strip() or len(cwd_paths) != 1:
            raise RuntimeError('heavy process working directory unavailable')
        for value in relative:
            match = scoped_path(value, cwd_paths[0])
            if match:
                return dict(pid=pid, command=command, **match)
    return dict(pid=pid, command=command, reason='no executable or path-valued argument resolves under this repository or its encoded Claude scratch directory')


def process_gate(wait=True, deadline=None):
    race_retried=False
    while True:
        row = dict(utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
                   scope=str(REPO_ROOT), pattern=HEAVY_PATTERN, matched=[], ignored_foreign=[], unresolved=[])
        try:
            p = subprocess.run(['pgrep','-fl',HEAVY_PATTERN], capture_output=True, text=True, timeout=10)
            row.update(returncode=p.returncode, stdout=p.stdout, stderr=p.stderr)
            if p.returncode == 1 and not p.stdout.strip() and not p.stderr.strip():
                row['status']='CLEAR'
            elif p.returncode == 0 and p.stdout.strip() and not p.stderr.strip():
                for line in p.stdout.splitlines():
                    pid, command = line.split(maxsplit=1)
                    if not pid.isdecimal() or int(pid) <= 0:
                        raise RuntimeError('invalid heavy process PID')
                    try:
                        item = classify_process(int(pid), command)
                    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
                        try:
                            os.kill(int(pid),0)
                        except ProcessLookupError:
                            row.setdefault('vanished',[]).append(dict(pid=int(pid),reason='process exited during ownership query'))
                            continue
                        row['unresolved'].append(dict(pid=int(pid), command=command, reason=str(error)))
                        continue
                    row['matched' if 'path' in item else 'ignored_foreign'].append(item)
                row['status']='UNAVAILABLE' if row['unresolved'] else ('ACTIVE' if row['matched'] else 'CLEAR')
            else:
                row['status']='UNAVAILABLE'
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
            row.update(status='UNAVAILABLE', error=str(error))
        write(GATE_PATH,row)
        if row.get('vanished'):
            if race_retried:raise RuntimeError('process gate repeated vanished-process race')
            race_retried=True
            continue
        if row['status']=='CLEAR': return row
        if row['status']=='UNAVAILABLE' or not wait: raise RuntimeError('process gate '+row['status']+'; no drills/series')
        print('Heavy job active; waiting 30 seconds',flush=True)
        if deadline is not None and time.monotonic()+30>=deadline:raise TimeoutError('local cap while waiting for heavy jobs')
        time.sleep(30)

