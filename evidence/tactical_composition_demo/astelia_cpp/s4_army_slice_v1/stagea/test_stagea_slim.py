"""Stage A boundary, lossless replay, bounded binary recording and disk admission."""
import copy
import gzip
import json
import lzma
import sys
import time
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ARMS, write, sha
from data import pack, labels, frames
from recording import Writer, rows, slim
from test_stagea import fixture
import metrics
import collect


def metric_rows(dt=1/30,duration=150,extra=0):
    out=[];t=0.;step=0
    units=[[i,i//50] for i in range(100)]
    while t < duration or extra:
        out.append(dict(observerV1=True,step=step,t=t,units=units,shapeV6=[],damage=[]))
        if t>=duration:extra-=1
        t+=dt;step+=1
    out.append(dict(observerV1=True,step=step,t=t,units=units,shapeV6=[],damage=[]))
    out.append(dict(survivors=50,enemySurvivors=50,t=t,controllerStatus='completed'))
    return out


def metric_file(path,records):
    with gzip.open(path,'wt') as f:
        for row in records:f.write(json.dumps(row)+'\n')
    return path


def test_native_last_tick_boundary_without_relaxing_rev2(tmp_path):
    records=metric_rows();path=metric_file(tmp_path/'fight.gz',records)
    result=metrics.measure(path)
    assert 150<result['t_end']<150+1/30+1e-7
    original=collect.a0() # imports rev2's dependency path without executing fights
    old=collect.load('unchanged_a0metrics',collect.ARMY/'rev2/a0_metrics.py')
    with pytest.raises(RuntimeError,match='invalid end time'):old.measure(path)
    assert records[-2]['step']==4501
    with pytest.raises(RuntimeError,match='invalid end time'):
        metrics.measure(metric_file(tmp_path/'extra.gz',metric_rows(extra=1)))
    for bad in (-1,0,float('nan'),float('inf'),151):
        changed=copy.deepcopy(records);changed[-1]['t']=bad
        with pytest.raises(RuntimeError,match='invalid end time'):metrics.measure(metric_file(tmp_path/'bad.gz',changed))
    changed=copy.deepcopy(records);changed[-1]['enemySurvivors']=49
    with pytest.raises(RuntimeError,match='terminal survivor mismatch'):metrics.measure(metric_file(tmp_path/'survivor.gz',changed))
    changed=copy.deepcopy(records);changed[10]['step']+=1
    with pytest.raises(RuntimeError,match='observer tick'):metrics.measure(metric_file(tmp_path/'gap.gz',changed))
    changed=copy.deepcopy(records);changed[-1]['controllerStatus']='failed'
    with pytest.raises(RuntimeError,match='incomplete or failed'):metrics.measure(metric_file(tmp_path/'failed.gz',changed))
    with pytest.raises(RuntimeError,match='duplicate terminal'):metrics.measure(metric_file(tmp_path/'twice.gz',records+[records[-1]]))
    short=metric_rows(duration=3)
    assert metrics.measure(metric_file(tmp_path/'short.gz',short),duration=3)['t_end']==short[-1]['t']
    with pytest.raises(RuntimeError,match='invalid end time'):metrics.measure(metric_file(tmp_path/'shortextra.gz',metric_rows(duration=3,extra=1)),duration=3)


def test_lossless_all_arm_inputs_labels_masks_and_native_replay(tmp_path):
    source=fixture();source[0]['pairModes']['2:4']=False
    source[0]['labels'][0].update(raw={'unused':True},participation={},react={},winner='teacher')
    path=tmp_path/'fight.slim.xz'
    with lzma.open(path,'wb',preset=1) as out:
        writer=Writer(out)
        for row in source:writer.write(row)
    restored=list(frames(path))
    assert len(restored)==len(source)
    for a,b in zip(source,restored):
        assert b['pairModes']==a['pairModes'] and b['history']==a['history']
        for arm in ARMS:
            x,ids,enemies=pack(a,arm);y,ids2,enemies2=pack(b,arm)
            assert ids==ids2 and enemies==enemies2
            for key in x:np.testing.assert_array_equal(x[key],y[key])
            assert labels(a,ids,enemies)==labels(b,ids2,enemies2)
    assert 'raw' not in restored[0]['labels'][0]
    from models import Policy, export
    from parity import sequence, compare, replay
    import torch
    torch.manual_seed(91);m=Policy('N2').double();weights=export(m,tmp_path/'weights.json')
    assert compare(sequence(m,source),replay(weights,restored))['max_abs_error']<1e-9
    # Missing bytes must not produce a silently complete sequence.
    data=path.read_bytes();path.write_bytes(data[:-10])
    with pytest.raises((EOFError,lzma.LZMAError,RuntimeError)):list(rows(path))


def test_compact_observer_metric_endpoints_match_full_detail(tmp_path):
    records=metric_rows(duration=.2)
    records[1]['shapeV6']=[dict(a0Label=True,role='artillery',rawToExecuted=3.141592653589793,activeFire=True,readyLabel=True,id=77,t=1,react=True),dict(a0Event=True,eligible=3,joint=True,applied=2,rejected=1,unused='diagnostic')]
    records[1].update(dodges=[[1,0]],launches=[[1,1,0]],shotsV6=[],launchAudit=[],battery=[],actions=[],entries=[])
    for row in records:
        if row.get('observerV1'):
            for key in ('dodges','launches'):row.setdefault(key,[])
    full=metric_file(tmp_path/'full.gz',records)
    path=tmp_path/'slim.xz'
    with lzma.open(path,'wb',preset=1) as out:
        w=Writer(out)
        for row in records:w.write(row)
    decoded=metric_file(tmp_path/'decoded.gz',list(rows(path)))
    a=metrics.measure(full,duration=.2);b=metrics.measure(decoded,duration=.2)
    a.pop('max_frame_bytes');b.pop('max_frame_bytes')
    assert a==b


def test_disk_gate_exact_formula_and_refusals(tmp_path,monkeypatch):
    monkeypatch.setattr(collect,'LOCAL',tmp_path)
    free=16*1024**3
    monkeypatch.setattr(collect.shutil,'disk_usage',lambda p:type('Usage',(),{'free':free})())
    records=[dict(compressed_bytes=10_000_000,stats={'t_end':75})]
    p=collect.disk_gate(records,180,160)
    expected=10_000_000*metrics.last_tick_time(150,1/30)/75
    assert p['full_fight_compact_bytes']==expected
    assert p['required_free_bytes']==expected*160*2+5_000_000_000
    assert p['actual_free_bytes']==free
    free=p['required_free_bytes']-1
    with pytest.raises(RuntimeError,match='disk gate'):collect.disk_gate(records,180,160)
    full=[dict(compressed_bytes=10_000_000,stats={'t_end':metrics.last_tick_time(150,1/30)})]
    assert collect.disk_projection(full,180)['full_fight_compact_bytes']==10_000_000
    free=100_000_000_000
    records[0]['compressed_bytes']=12_000_000
    with pytest.raises(RuntimeError,match='4 GB'):collect.disk_gate(records,180,160)


def test_slim_recovery_retains_failure_and_sealed_requests(tmp_path,monkeypatch):
    monkeypatch.setattr(collect,'LOCAL',tmp_path)
    monkeypatch.setattr(collect,'identity',lambda:{'binary':'new'})
    monkeypatch.setattr(collect,'sources',lambda:{'code':'new'})
    req=tmp_path/'requests/train_0000.json';write(req,{'sealed':True})
    job=dict(tag='train_0000',request_sha256=sha(req))
    old=dict(jobs=[job],timing_sample=['train_0000'],binary={},sources={})
    baseline=tmp_path/'DATA_LEDGER.json';write(baseline,old);baseline_sha=sha(baseline)
    raw=tmp_path/'raw/failure.jsonl.gz';raw.parent.mkdir();raw.write_bytes(b'failed evidence')
    attempt=tmp_path/'attempts/fixture.json';write(attempt,dict(status='STOP_RESUMABLE',error='RuntimeError: invalid end time',raw_file='raw/failure.jsonl.gz'))
    attempt_sha=sha(attempt)
    ledger=collect.recover_slim()
    assert ledger['jobs']==old['jobs'] and ledger['timing_sample']==old['timing_sample']
    assert sha(req)==job['request_sha256'] and sha(baseline)==baseline_sha and sha(attempt)==attempt_sha
    assert collect.recover_slim()==ledger
    raw.write_bytes(b'tamper')
    with pytest.raises(RuntimeError,match='failed attempt evidence drift'):collect.check()


def test_compact_pipe_writer_and_failed_evidence(tmp_path,monkeypatch):
    import streaming
    popen=streaming.subprocess.Popen
    monkeypatch.setattr(streaming.subprocess,'Popen',lambda argv,**kw:popen(argv[3:],**kw))
    script=tmp_path/'host';row=fixture()[0]
    script.write_text('#!/usr/bin/env python3\nimport sys\nsys.stdin.readline()\nprint('+repr(json.dumps(row))+')\n')
    script.chmod(0o755)
    class Monitor:
        def live_memory(self,pid):return 1
    raw=tmp_path/'compact.slim.xz';receipt={}
    streaming.stream_host(script,{},raw,tmp_path/'err',time.monotonic()+10,Monitor(),receipt,compact=True)
    decoded=list(rows(raw));assert len(decoded)==1
    assert labels(decoded[0],[1,2,3],[4,5,6])==labels(row,[1,2,3],[4,5,6])
    assert receipt['compressed_bytes']==raw.stat().st_size
    script.write_text('#!/usr/bin/env python3\nimport sys\nsys.stdin.readline()\nprint('+repr(json.dumps(row))+')\nsys.stdout.write("partial")\n')
    failed=tmp_path/'failed.slim.xz'
    with pytest.raises(RuntimeError,match='truncated host'):
        streaming.stream_host(script,{},failed,tmp_path/'err2',time.monotonic()+10,Monitor(),{},compact=True)
    assert failed.exists() and len(list(rows(failed)))==1


@pytest.mark.parametrize('compact', (False, True))
def test_physical_clock_and_parity_validation(tmp_path, compact):
    # Native snapshot time is after clock advance; observer zero has no policy row.
    dt=1/30;source=fixture()[:3]
    for i,row in enumerate(source):
        row['t']=(i+1)*dt
        row['recordingCadence']='physical_tick_after_clock_advance'
    observers=metric_rows(duration=.1)
    for row in observers:
        if row.get('observerV1'):row.update(dodges=[],launches=[])
    def record(stage_rows, parity=False):
        records=[observers[0]]
        for i,row in enumerate(stage_rows):
            if parity:records.append(dict(stageAParity=True,input={k:v for k,v in row.items() if k!='labels'},output=[]))
            records.extend((row,observers[i+1]))
        records.extend(observers[len(stage_rows)+1:])
        path=tmp_path/('test.slim.xz' if compact else 'test.jsonl.gz')
        if compact:
            with lzma.open(path,'wb',preset=1) as out:
                w=Writer(out)
                for row in records:w.write(row)
        else:metric_file(path,records)
        return path
    result=collect.validate_raw(record(source,parity=True),time.monotonic()+10,duration=.1)
    assert result['frames']==3 and result['stats']['t_end']==.1
    for idx,value in ((0,0),(1,3*dt),(2,float('nan'))):
        broken=copy.deepcopy(source);broken[idx]['t']=value
        if not compact or np.isfinite(value):
            with pytest.raises(RuntimeError,match='physical-tick history'):
                collect.validate_raw(record(broken),time.monotonic()+10,duration=.1)
    broken=copy.deepcopy(source);broken[1]['recordingCadence']='decision_5hz'
    with pytest.raises(RuntimeError,match='physical-tick history'):
        collect.validate_raw(record(broken),time.monotonic()+10,duration=.1)
    with pytest.raises(RuntimeError,match='terminal/physical'):
        collect.validate_raw(record(source[:-1]),time.monotonic()+10,duration=.1)
    path=record(source,parity=True);corrupt=list(rows(path))
    next(r for r in corrupt if r.get('stageAParity'))['input']['width']+=1
    if compact:
        with lzma.open(path,'wb',preset=1) as out:
            writer=Writer(out)
            for row in corrupt:writer.write(row)
    else:metric_file(path,corrupt)
    with pytest.raises(RuntimeError,match='parity/recorded input mismatch'):
        collect.validate_raw(path,time.monotonic()+10,duration=.1)


def test_fixture_is_bounded_and_production_admission_still_gates(tmp_path,monkeypatch):
    import fixture_host, jobs
    monkeypatch.setenv('STAGEA_HOST_TEST','1')
    monkeypatch.setattr(fixture_host,'LOCAL',tmp_path)
    with pytest.raises(RuntimeError,match='fixture job required'):
        fixture_host.execute_fixture(dict(tag='train_0000',split='train'))
    with pytest.raises(RuntimeError,match='fixture job required'):
        fixture_host.execute_fixture(dict(tag='../train_0000',split='integration'))
    request=tmp_path/'requests/host_fixture_test.json'
    write(request,dict(options={'duration':150},stageA={'collect':True}))
    with pytest.raises(RuntimeError,match='duration'):
        fixture_host.execute_fixture(dict(tag='host_fixture_test',split='integration',request_sha256=sha(request)))
    import contextlib
    @contextlib.contextmanager
    def lock():yield
    class Gate:
        def process_gate(self,**kw):raise RuntimeError('production process gate called')
    monkeypatch.setattr(jobs,'locked',lock)
    monkeypatch.setattr(jobs,'load',lambda *args:Gate())
    with pytest.raises(RuntimeError,match='production process gate called'):
        with jobs.admitted(10):pass


def test_fix3_recovery_preserves_prior_slim_and_failed_clock_attempt(tmp_path,monkeypatch):
    monkeypatch.setattr(collect,'LOCAL',tmp_path)
    monkeypatch.setattr(collect,'HERE',tmp_path)
    monkeypatch.setattr(collect,'identity',lambda:{'binary':'fix3'})
    monkeypatch.setattr(collect,'sources',lambda:{'code':'fix3'})
    req=tmp_path/'requests/train_0000.json';write(req,{'sealed':True})
    old=dict(jobs=[dict(tag='train_0000',request_sha256=sha(req))],timing_sample=['train_0000'],binary={},sources={})
    baseline=tmp_path/'DATA_LEDGER.json';write(baseline,old);baseline_sha=sha(baseline)
    raw=tmp_path/'raw/clock.jsonl.gz';raw.parent.mkdir();raw.write_bytes(b'failed clock evidence')
    failure=tmp_path/'attempts/clock.json';write(failure,dict(status='STOP_RESUMABLE',raw_file='raw/clock.jsonl.gz',error='incomplete physical-tick history'))
    failure_sha=sha(failure)
    result=collect.recover_fix3()
    assert result['jobs']==old['jobs'] and result['timing_sample']==old['timing_sample']
    assert sha(baseline)==baseline_sha and sha(failure)==failure_sha
    assert collect.recover_fix3()==result
    raw.write_bytes(b'changed')
    with pytest.raises(RuntimeError,match='failed attempt evidence drift'):collect.check()
