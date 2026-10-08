"""Bounded recorder, exact request recovery and real native GC roots."""
import gzip
import json
import sys
import time
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import BINARY, HERE, read, sha, write
from streaming import stream_host

def test_stream_gzip_and_failed_attempt(tmp_path,monkeypatch):
    # macOS sandbox rejects priority changes; test pipe/gzip behavior with the
    # same real child process, removing only the unrelated nice wrapper.
    import streaming
    popen=streaming.subprocess.Popen
    monkeypatch.setattr(streaming.subprocess,'Popen',lambda argv,**kw:popen(argv[3:],**kw))
    script=tmp_path/'fake_host'
    script.write_text('#!/usr/bin/env python3\nimport sys\nsys.stdin.readline()\nfor i in range(512):sys.stdout.buffer.write(b"x"*65536)\n')
    script.chmod(0o755)
    class Monitor:
        def live_memory(self,pid):return 1
    raw=tmp_path/'attempt1.gz';err=tmp_path/'attempt1.stderr';receipt={}
    stream_host(script,{},raw,err,time.monotonic()+30,Monitor(),receipt)
    assert receipt['uncompressed_bytes']==32*1024**2 and receipt['compressed_bytes']==raw.stat().st_size
    assert receipt['compressed_bytes']<receipt['uncompressed_bytes']/100
    with gzip.open(raw,'rb') as f:
        count=0
        for chunk in iter(lambda:f.read(65536),b''):count+=len(chunk)
    assert count==receipt['uncompressed_bytes'] and not list(tmp_path.glob('*.stdout'))
    script.write_text('#!/usr/bin/env python3\nimport sys\nsys.stdin.readline()\nsys.stdout.write("partial evidence\\n")\nsys.exit(1)\n')
    second=tmp_path/'attempt2.gz';failed={}
    with pytest.raises(RuntimeError,match='host failed'):
        stream_host(script,{},second,tmp_path/'attempt2.stderr',time.monotonic()+30,Monitor(),failed)
    with gzip.open(second,'rt') as f:assert f.read()=='partial evidence\n'
    assert raw.exists() and second.exists()

def test_explicit_recovery_preserves_requests_and_failure(tmp_path,monkeypatch):
    import collect
    monkeypatch.setattr(collect,'LOCAL',tmp_path)
    monkeypatch.setattr(collect,'sources',lambda:{'new':'source'})
    monkeypatch.setattr(collect,'identity',lambda:{'new':'binary'})
    request=tmp_path/'requests/train_0000.json';write(request,{'sealed':True})
    job=dict(tag='train_0000',request_sha256=sha(request))
    old=dict(jobs=[job],timing_sample=['train_0000'],sources={'old':'source'},binary={'old':'binary'})
    write(tmp_path/'DATA_LEDGER.json',old)
    old_hash=sha(tmp_path/'DATA_LEDGER.json')
    failed=tmp_path/'attempts/train_0000_9d48acc6753c473a.json'
    write(failed,dict(job=job,status='STOP_RESUMABLE',error='RuntimeError: child exceeds 2 GiB RSS',ledger_sha256=old_hash))
    raw=tmp_path/'raw/train_0000_9d48acc6753c473a.jsonl.stdout';raw.parent.mkdir();raw.write_text('failed bytes')
    raw.with_suffix('.stderr').write_text('')
    # A preexisting integration completion must not block collection recovery.
    write(tmp_path/'raw/host_fixture_COMPLETE.json',{'fixture':True})
    result=collect.recover_memory()
    assert result['jobs']==old['jobs'] and result['timing_sample']==old['timing_sample']
    assert sha(tmp_path/'DATA_LEDGER.json')==old_hash and sha(request)==job['request_sha256']
    assert collect.ledger_path()!=tmp_path/'DATA_LEDGER.json'
    assert collect.recover_memory()==result
    raw.write_text('tampered')
    with pytest.raises(RuntimeError,match='failed attempt evidence drift'):collect.check()

def test_native_gc_retains_batch_trace_and_pending_telemetry(tmp_path):
    import subprocess
    record=read(BINARY.with_suffix('.build.json'))
    command=next(c for c in record['commands'] if c[c.index('-c')+1]==str(HERE/'stagea.cpp'))
    flags=command[:command.index('-c')]
    obj=tmp_path/'roots.o';binary=tmp_path/'roots_contract'
    subprocess.run([*flags,'-c',str(HERE/'memory_roots_contract.cpp'),'-o',str(obj)],check=True)
    objects=[p for p in record['link'][1:record['link'].index('-o')] if Path(p).name!='lean_host.o']
    subprocess.run([record['link'][0],str(obj),*objects,'-o',str(binary)],check=True)
    proof=json.loads(subprocess.run([str(binary)],capture_output=True,text=True,check=True).stdout)
    assert proof['gc_ticks']==4501 and proof['roots_preserved'] and proof['live_json_objects']<=20
