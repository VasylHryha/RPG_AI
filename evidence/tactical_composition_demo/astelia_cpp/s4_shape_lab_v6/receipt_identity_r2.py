"""Stream hashes once per unchanged stat identity; preserve native admission."""
import hashlib
import json
import os
import pathlib
import threading
from build_admission import ROOT
_CACHE={}
_LOCK=threading.Lock()

def sha(path):
    path=pathlib.Path(os.path.abspath(path))
    stat=path.stat()
    key=(stat.st_dev,stat.st_ino,stat.st_size,stat.st_mtime_ns,stat.st_ctime_ns)
    with _LOCK:
        cached=_CACHE.get(path)
        if cached and cached[0]==key:return cached[1]
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    after=path.stat()
    if (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)!=key:
        raise RuntimeError('file changed while hashing: '+str(path))
    value=digest.hexdigest()
    with _LOCK:_CACHE[path]=(key,value)
    return value

def admit(executable):
    executable=pathlib.Path(executable).resolve()
    manifest=executable.with_suffix('.build.json')
    record=json.loads(manifest.read_text())
    if record.get('schema')!=2 or record.get('binary_sha256')!=sha(executable):raise RuntimeError('binary/build manifest mismatch: '+str(executable))
    if not record.get('source_hashes'):raise RuntimeError('build manifest lacks source identities')
    for name,expected in record['source_hashes'].items():
        path=pathlib.Path(name)
        if not path.is_absolute():path=ROOT/path
        if sha(path)!=expected:raise RuntimeError('source/build mismatch; rebuild before execution or cache lookup: '+name)
    return dict(manifest_sha256=sha(manifest),binary_sha256=sha(executable),sources=record['source_hashes'],engine=record['engine'],scope=record['scope'],sanitized=record['sanitized'],portable=record['portable'])
