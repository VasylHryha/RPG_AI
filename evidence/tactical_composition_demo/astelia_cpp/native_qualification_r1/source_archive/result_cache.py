"""Content-addressed combat results; benchmark callers deliberately bypass this."""
import gzip
import hashlib
import json
import pathlib
import shutil
import subprocess
import tempfile
import zlib
import queue
import threading
import time
import math
from build_admission import admit
from result_schema import validate_rows

ROOT = pathlib.Path(__file__).resolve().parent
DEFAULT_CACHE = ROOT / 'build/combat_cache'
BASELINE_COMMIT = '797ced26ff95caa5f84ea71e9bb247422068b5c5'


def encoded(value):
    # Preserve key insertion order: JS enumeration/stringify can observe it.
    return json.dumps(value, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(kind, command):
    executable = pathlib.Path(shutil.which(command[0]) or command[0]).resolve()
    files = {str(executable): sha(executable)}
    for arg in command[1:]:
        path = pathlib.Path(arg)
        if path.is_file():
            files[str(path.resolve())] = sha(path)
    snapshot = ROOT.parent / 'astelia_snapshot'
    files[str(snapshot / 'bc_net.json')] = sha(snapshot / 'bc_net.json')
    for filename in ('result_cache.py','result_schema.py','build_admission.py'):
        files[str(ROOT / filename)] = sha(ROOT / filename)
    result = dict(schema=2, kind=kind, command=command, files=files)
    if kind == 'cpp' and executable.parent == (ROOT / 'build').resolve():
        result['build'] = admit(executable)
    if kind == 'js':
        files[str(ROOT / 'js_host.cjs')] = sha(ROOT / 'js_host.cjs')
        files[str(snapshot / 'formation_sim.js')] = sha(snapshot / 'formation_sim.js')
        result['node'] = json.loads(subprocess.check_output(
            [command[0], '-p', 'JSON.stringify(process.versions)'], text=True))
    return result


class Cache:
    def __init__(self, root, engine):
        self.identity = engine
        self.root = pathlib.Path(root) / digest(engine)
        self.root.mkdir(parents=True, exist_ok=True)
        self.rejected = 0

    def path(self, request):
        return self.root / (digest(request) + '.json.gz')

    def load(self, request):
        path = self.path(request)
        if not path.exists():
            return None
        try:
            record = json.loads(gzip.decompress(path.read_bytes()))
            rows = record['rows']
            valid = (record['identity'] == self.identity and
                     encoded(record['request']) == encoded(request) and
                     record['rows_sha256'] == digest(rows))
            if not valid:
                raise ValueError('cache identity, request or result mismatch')
            validate_rows(request, rows)
            return rows
        except (ValueError, KeyError, TypeError, OSError, EOFError, zlib.error, OverflowError):
            self.rejected += 1
            return None

    def put(self, request, rows, provenance='fresh host execution'):
        validate_rows(request, rows)
        record = dict(identity=self.identity, request=request, rows=rows,
                      rows_sha256=digest(rows), provenance=provenance)
        payload = gzip.compress(encoded(record), mtime=0)
        with tempfile.NamedTemporaryFile(dir=self.root, delete=False) as stream:
            stream.write(payload)
            temporary = pathlib.Path(stream.name)
        temporary.replace(self.path(request))


class Engine:
    def __init__(self, kind, command, cache_dir=DEFAULT_CACHE, request_timeout=120, shutdown_timeout=5):
        if not math.isfinite(request_timeout) or request_timeout <= 0 or not math.isfinite(shutdown_timeout) or shutdown_timeout <= 0:
            raise ValueError('host timeouts must be finite and positive')
        self.request_timeout, self.shutdown_timeout = request_timeout, shutdown_timeout
        self.output = self.reader = self.stderr_file = self.reader_stop = None
        self.command = command
        self.identity = identity(kind, command)
        self.cache = Cache(cache_dir, self.identity) if cache_dir is not None else None
        self.process = None
        self.hits = self.executed = 0
        paths = set(self.identity['files'])
        for argument in command:
            path = pathlib.Path(shutil.which(argument) or argument)
            if path.is_file():
                paths.add(str(path.absolute()))
        if 'build' in self.identity:
            paths.add(str(pathlib.Path(command[0]).resolve().with_suffix('.build.json')))
        for name in self.identity.get('build', {}).get('sources', {}):
            path = pathlib.Path(name)
            paths.add(str(path if path.is_absolute() else ROOT / path))
        self.input_stats = {name:self.file_stat(name) for name in paths}

    @staticmethod
    def file_stat(name):
        s = pathlib.Path(name).stat()
        return s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_ino

    def check_input_stats(self):
        try:
            changed = any(self.file_stat(name) != before for name, before in self.input_stats.items())
        except OSError as error:
            raise RuntimeError('engine identity changed during comparison') from error
        if changed:
            raise RuntimeError('engine identity changed during comparison')

    def start(self):
        # Stderr goes to disk, so a chatty child cannot block on an undrained pipe.
        self.stderr_file = tempfile.TemporaryFile(mode='w+b')
        try:
            self.process = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                            stderr=self.stderr_file, text=True, bufsize=1)
        except BaseException:
            self.stderr_file.close(); self.stderr_file = None
            raise
        self.output = queue.Queue(maxsize=256)
        self.reader_stop = threading.Event()
        process, output, stop = self.process, self.output, self.reader_stop
        def read():
            try:
                while not stop.is_set():
                    line = process.stdout.readline(8 * 1024 * 1024 + 1)
                    if len(line) > 8 * 1024 * 1024:
                        raise RuntimeError('combat host response line exceeds 8 MiB')
                    item = line if line else EOFError('combat host exited')
                    while not stop.is_set():
                        try:
                            output.put(item, timeout=.1)
                            break
                        except queue.Full:
                            pass
                    if not line:
                        return
            except BaseException as error:
                while not stop.is_set():
                    try:
                        output.put(error, timeout=.1)
                        return
                    except queue.Full:
                        pass
        self.reader = threading.Thread(target=read, daemon=True)
        self.reader.start()

    def stderr_tail(self):
        if self.stderr_file is None:
            return ''
        self.stderr_file.seek(0, 2)
        length = self.stderr_file.tell()
        self.stderr_file.seek(max(0, length - 65536))
        return self.stderr_file.read().decode(errors='replace')

    def stop(self, graceful=False):
        if self.process is None:
            return 0, ''
        process = self.process
        if graceful:
            process.stdin.close()
            try:
                process.wait(timeout=self.shutdown_timeout)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait(timeout=self.shutdown_timeout)
        else:
            process.kill(); process.wait(timeout=self.shutdown_timeout)
        code, error = process.returncode, self.stderr_tail()
        self.reader_stop.set()
        self.reader.join(timeout=self.shutdown_timeout)
        process.stdout.close()
        if not process.stdin.closed:
            process.stdin.close()
        self.stderr_file.close()
        self.process = self.reader = self.output = self.stderr_file = self.reader_stop = None
        return code, error

    def fight(self, request):
        self.check_input_stats()
        if self.cache is not None:
            rows = self.cache.load(request)
            if rows is not None:
                self.check_input_stats()
                self.hits += 1
                return rows
        payload = encoded(request).decode() + '\n'
        if self.process is None:
            self.start()
        deadline = time.monotonic() + self.request_timeout
        written = queue.Queue(maxsize=1)
        process = self.process
        def write():
            try:
                process.stdin.write(payload)
                process.stdin.flush()
                written.put(None)
            except BaseException as error:
                written.put(error)
        writer = threading.Thread(target=write, daemon=True)
        writer.start()
        rows = []
        try:
            result = written.get(timeout=max(0, deadline - time.monotonic()))
            if isinstance(result, BaseException):
                raise RuntimeError('combat host request failed') from result
            while True:
                line = self.output.get(timeout=max(0, deadline - time.monotonic()))
                if isinstance(line, BaseException):
                    raise RuntimeError(str(line) + ': ' + self.stderr_tail()) from line
                row = json.loads(line)
                rows.append(row)
                if not isinstance(row, dict) or 'step' not in row:
                    break
            validate_rows(request, rows)
            self.check_input_stats()
            self.executed += 1
            if self.cache is not None:
                self.cache.put(request, rows)
            return rows
        except queue.Empty as error:
            _, stderr = self.stop()
            raise RuntimeError(f'combat host request timed out after {self.request_timeout}s: {stderr}') from error
        except BaseException:
            self.stop()
            raise
        finally:
            writer.join(timeout=self.shutdown_timeout)

    def close(self):
        if self.process is not None:
            code, error = self.stop(graceful=True)
            if code:
                raise RuntimeError(f'combat host exit {code}: {error}')
        if identity(self.identity['kind'], self.command) != self.identity:
            raise RuntimeError('engine identity changed during comparison')

    def counts(self):
        return dict(cached=self.hits, executed=self.executed,
                    rejected=self.cache.rejected if self.cache is not None else 0)


def prime_legacy(engine):
    """Import the committed JS baseline only when its source/runtime still match."""
    if engine.cache is None:
        return 0
    # Historical output belongs only to the canonical frozen JS host. Matching
    # Node versions and source files cannot qualify an arbitrary wrapper.
    if (engine.identity.get('kind') != 'js' or len(engine.command) != 2 or
            pathlib.Path(engine.command[1]).resolve() != (ROOT / 'js_host.cjs').resolve()):
        return 0
    engine.check_input_stats()
    baseline = ROOT / 'checks_r2'
    receipt = json.loads((baseline / 'checks.json').read_text())
    snapshot = ROOT.parent / 'astelia_snapshot'
    for name, expected in receipt['source_hashes'].items():
        if sha(snapshot / name) != expected:
            return 0
    host_path = 'evidence/tactical_composition_demo/astelia_cpp/js_host.cjs'
    original_host = subprocess.check_output(['git', 'show', BASELINE_COMMIT + ':' + host_path], cwd=ROOT)
    if hashlib.sha256(original_host).hexdigest() != sha(ROOT / 'js_host.cjs'):
        return 0
    if engine.identity.get('node') != receipt['node'] or receipt['status'] != 'IDENTICAL':
        return 0
    # Refuse edited evidence; source/host matching alone is insufficient.
    for name in ('checks.json', 'fight_results.jsonl', 'math_results.jsonl'):
        old = subprocess.check_output(['git', 'show', BASELINE_COMMIT + ':' +
                                      'evidence/tactical_composition_demo/astelia_cpp/checks_r2/' + name], cwd=ROOT)
        if hashlib.sha256(old).hexdigest() != sha(baseline / name):
            raise RuntimeError('committed baseline evidence changed: ' + name)
    requests = [json.loads(s) for s in (ROOT / 'check_fights.jsonl').read_text().splitlines()]
    if sha(ROOT / 'check_fights.jsonl') != receipt['inputs_sha256']:
        return 0
    count = 0
    for line in (baseline / 'fight_results.jsonl').read_text().splitlines():
        row = json.loads(line)
        request = requests[row['check_id']]
        if request != row['fight'] or row['difference'] is not None:
            raise RuntimeError('inconsistent baseline fight')
        if engine.cache.load(request) is None:
            engine.cache.put(request, [row['js']], 'committed JS baseline ' + BASELINE_COMMIT)
            count += 1
    for trace in receipt['traces']:
        payload = gzip.decompress((baseline / trace['file']).read_bytes())
        if hashlib.sha256(payload).hexdigest() != trace['js_sha256']:
            raise RuntimeError('baseline trace hash mismatch')
        request = dict(requests[trace['check_id']], trace=True)
        if engine.cache.load(request) is None:
            engine.cache.put(request, [json.loads(s) for s in payload.splitlines()],
                             'committed JS trace ' + BASELINE_COMMIT)
            count += 1
    return count
