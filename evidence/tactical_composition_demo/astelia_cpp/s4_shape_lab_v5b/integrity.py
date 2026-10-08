"""Hash admission with per-process, stat-invalidated caches; never decode raw."""
import hashlib
import json
import pathlib

_HASHES = {}


def sha(path):
    path = pathlib.Path(path)
    before = path.stat()
    key = (before.st_dev, before.st_ino, before.st_size,
           before.st_mtime_ns, before.st_ctime_ns)
    cached = _HASHES.get(path)
    if cached and cached[0] == key:
        return cached[1]
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    after = path.stat()
    if key != (after.st_dev, after.st_ino, after.st_size,
               after.st_mtime_ns, after.st_ctime_ns):
        raise RuntimeError('file changed during hash verification: ' + str(path))
    value = digest.hexdigest()
    _HASHES[path] = key, value
    return value


def admit(executable):
    """Same identity as build_admission.admit, with fresh stat checks each call."""
    executable = pathlib.Path(executable).resolve()
    manifest = executable.with_suffix('.build.json')
    record = json.loads(manifest.read_text())
    if record.get('schema') != 2 or record.get('binary_sha256') != sha(executable):
        raise RuntimeError('binary/build manifest mismatch: ' + str(executable))
    if not record.get('source_hashes'):
        raise RuntimeError('build manifest lacks source identities')
    root = pathlib.Path(__file__).resolve().parent.parent
    for name, expected in record['source_hashes'].items():
        path = pathlib.Path(name)
        if not path.is_absolute():
            path = root / path
        if sha(path) != expected:
            raise RuntimeError('source/build mismatch: ' + name)
    return dict(manifest_sha256=sha(manifest), binary_sha256=sha(executable),
                sources=record['source_hashes'], engine=record['engine'],
                scope=record['scope'], sanitized=record['sanitized'], portable=record['portable'])
