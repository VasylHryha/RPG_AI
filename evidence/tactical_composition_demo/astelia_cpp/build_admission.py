"""Refuse results from binaries that do not match their current source manifest."""
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def admit(executable):
    executable = pathlib.Path(executable).resolve()
    manifest = executable.with_suffix('.build.json')
    record = json.loads(manifest.read_text())
    if record.get('schema') != 2 or record.get('binary_sha256') != sha(executable):
        raise RuntimeError('binary/build manifest mismatch: ' + str(executable))
    if not record.get('source_hashes'):
        raise RuntimeError('build manifest lacks source identities')
    for name, expected in record['source_hashes'].items():
        path = pathlib.Path(name)
        if not path.is_absolute():
            path = ROOT / path
        if sha(path) != expected:
            raise RuntimeError('source/build mismatch; rebuild before execution or cache lookup: ' + name)
    return dict(manifest_sha256=sha(manifest), binary_sha256=sha(executable),
                sources=record['source_hashes'], engine=record['engine'],
                scope=record['scope'], sanitized=record['sanitized'], portable=record['portable'])
