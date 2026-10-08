"""RSS/recovery tooling only: synthetic files, no native fights or builds."""
from contextlib import nullcontext
import copy
import json
from pathlib import Path
import sys
import types

import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import s1fix_pilot as p


@pytest.fixture
def boundary(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'ROOT',tmp_path)
    monkeypatch.setattr(p,'lock',nullcontext)
    monkeypatch.setattr(p,'clear',lambda *a:pytest.fail('no process launch/discovery in resolution'))
    monkeypatch.setattr(p.collection,'native',lambda *a:pytest.fail('no native execution'))
    old=dict(design_commit='design',build_sha256='build',binary_sha256='binary',sources={'s1fix_pilot.py':p.RSSFIX_BASELINE_SHA256,'physics':'unchanged'})
    current=copy.deepcopy(old);current['sources']['s1fix_pilot.py']='after'
    monkeypatch.setattr(p,'pins',lambda:copy.deepcopy(current))
    request=dict(fight='s1fix_M2-10_01_wrapper')
    row=dict(request=request,sample=True,fight=request['fight'])
    inv=dict(pins=old,rows=[row])
    p.atomic(tmp_path/'INVENTORY.json',inv);p.atomic(tmp_path/'SEAL.json',dict(inventory_sha256=p.sha(tmp_path/'INVENTORY.json')))
    attempt=tmp_path/'attempts/014.json'
    original=dict(status='NATIVE_DONE',sample=True,request=request,resources=dict(exit_code=0,timed_out=False,rss_bytes=580894720,wall_seconds=6.6453,cpu_seconds=6.61))
    p.atomic(attempt,original)
    partial=attempt.with_suffix('.partial.jsonl');partial.write_text('{"terminal":true}\n')
    stderr=attempt.with_suffix('.stderr');stderr.write_text('')
    def measure(frames,request):
        rows=list(frames)
        if not rows or rows[-1]!={'terminal':True}:raise ValueError('missing terminal')
        return dict(fight=request['fight'],rows=len(rows))
    monkeypatch.setattr(p,'measure',measure)
    return types.SimpleNamespace(root=tmp_path,attempt=attempt,partial=partial,row=row,original=original,current=current)


def test_explicit_resolve_preserves_raw_inventory_resources_and_charges_once(boundary):
    b=boundary;inv=(b.root/'INVENTORY.json').read_bytes();raw=b.partial.read_bytes()
    with pytest.raises(RuntimeError,match='unresolved'):p.charged()
    with pytest.raises(RuntimeError,match='explicit resolve'):p.inventory()
    result=p.resolve('014')
    assert result['status']=='COMPLETE'
    assert (b.root/'INVENTORY.json').read_bytes()==inv
    assert (b.root/(b.row['fight']+'.jsonl')).read_bytes()==raw
    assert not b.partial.exists()
    receipt=p.completed(b.row)
    assert receipt['resources']==b.original['resources']
    assert receipt['metrics']==dict(fight=b.row['fight'],rows=1)
    log=p.read(b.root/'resolutions/014.json')
    assert log['original_attempt']==b.original and log['old_process_rss_cap_bytes']==512*1024**2
    assert log['process_rss_cap_bytes']==2*1024**3 and 'without rerun or data edit' in log['reason']
    assert log['completion_receipt_sha256']==p.sha(b.root/(b.row['fight']+'.receipt.json'))
    assert p.charged()==b.original['resources']['wall_seconds'] and len(list((b.root/'attempts').glob('*.json')))==1
    assert p.inventory()['pins']['sources']['s1fix_pilot.py']==p.RSSFIX_BASELINE_SHA256
    before=(b.root/'resolutions/014.json').read_bytes()
    p.resolve('014')
    assert (b.root/'resolutions/014.json').read_bytes()==before
    assert p.charged()==b.original['resources']['wall_seconds']


@pytest.mark.parametrize('failure',['failed','running','exit','timeout','under_old','over_new','truncated','malformed','missing','orphan','request','source','seal'])
def test_resolve_refuses_invalid_boundaries_without_mutation(boundary,failure):
    b=boundary;v=copy.deepcopy(b.original)
    if failure=='failed':v['status']='FAILED'
    if failure=='running':v['status']='RUNNING'
    if failure=='exit':v['resources']['exit_code']=1
    if failure=='timeout':v['resources']['timed_out']=True
    if failure=='under_old':v['resources']['rss_bytes']=512*1024**2
    if failure=='over_new':v['resources']['rss_bytes']=2*1024**3+1
    if failure=='request':v['request']['fight']='unknown'
    p.atomic(b.attempt,v)
    if failure=='truncated':b.partial.write_text('{}\n')
    if failure=='malformed':b.partial.write_text('{\n')
    if failure=='missing':b.partial.unlink()
    if failure=='orphan':(b.root/(b.row['fight']+'.jsonl')).write_text('orphan')
    if failure=='source':b.current['sources']['physics']='drift'
    if failure=='seal':p.atomic(b.root/'SEAL.json',dict(inventory_sha256='wrong'))
    before={str(f.relative_to(b.root)):f.read_bytes() for f in b.root.rglob('*') if f.is_file()}
    with pytest.raises((RuntimeError,ValueError)):p.resolve('014')
    after={str(f.relative_to(b.root)):f.read_bytes() for f in b.root.rglob('*') if f.is_file()}
    assert before==after


@pytest.mark.parametrize('interrupt',['prepared','renamed','receipt','attempt'])
def test_resolution_resume_after_interruption_no_retry(boundary,monkeypatch,interrupt):
    b=boundary;atomic=p.atomic;replace=p.os.replace
    def stop_atomic(path,payload):
        path=Path(path)
        if interrupt=='prepared' and path.name.endswith('.receipt.json'):raise OSError('interrupted')
        if interrupt=='receipt' and path==b.attempt:raise OSError('interrupted')
        if interrupt=='attempt' and path==b.root/'resolutions/014.json' and payload['status']=='COMPLETE':raise OSError('interrupted')
        atomic(path,payload)
    def stop_replace(source,target):
        if interrupt in ('prepared','renamed') and Path(source)==b.partial:
            if interrupt=='renamed':replace(source,target)
            raise OSError('interrupted')
        return replace(source,target)
    monkeypatch.setattr(p,'atomic',stop_atomic);monkeypatch.setattr(p.os,'replace',stop_replace)
    with pytest.raises(OSError,match='interrupted'):p.resolve('014')
    with pytest.raises(RuntimeError,match='explicit resolve'):p.inventory()
    monkeypatch.setattr(p,'atomic',atomic);monkeypatch.setattr(p.os,'replace',replace)
    assert p.resolve('014')['status']=='COMPLETE'
    assert p.charged()==b.original['resources']['wall_seconds']


def test_normal_completion_uses_new_cap_and_same_receipt(boundary):
    b=boundary
    result=p.complete_attempt(b.row,b.attempt,b.partial,b.attempt.with_suffix('.stderr'),b.original['resources'],True)
    assert result['resources']['rss_bytes']==580894720
    assert not (b.root/'resolutions').exists()


def test_inventory_amendment_rejects_later_tooling_and_physics_drift(boundary):
    b=boundary;p.resolve('014');b.current['sources']['s1fix_pilot.py']='later'
    with pytest.raises(RuntimeError,match='explicit resolve'):p.inventory()
    b.current['sources']['s1fix_pilot.py']='after';b.current['sources']['physics']='drift'
    with pytest.raises(RuntimeError,match='source/build'):p.inventory()


@pytest.mark.parametrize('ram,peak,admitted',[(8*1024**3,580894720,True),(1_000_000_000,580894720,False),(8*1024**3,2*1024**3+1,False)])
def test_projection_and_live_gate_check_cap_and_available_ram(tmp_path,monkeypatch,ram,peak,admitted):
    monkeypatch.setattr(p,'ROOT',tmp_path);p.atomic(tmp_path/'INVENTORY.json',{})
    rows=[]
    for i in range(20):
        row=dict(fight=f'f{i}',sample=True);rows.append(row)
        p.atomic(tmp_path/(row['fight']+'.receipt.json'),dict(request=dict(fight=row['fight']),resources=dict(wall_seconds=1,rss_bytes=peak),disk_bytes=1000))
        p.atomic(tmp_path/'attempts'/f'{i:03d}.json',dict(status='COMPLETE',resources=dict(wall_seconds=1,rss_bytes=peak)))
    monkeypatch.setattr(p,'inventory',lambda:dict(rows=rows))
    monkeypatch.setattr(p,'completed',lambda row:p.read(tmp_path/(row['fight']+'.receipt.json')))
    monkeypatch.setattr(p,'free_ram_bytes',lambda:ram)
    monkeypatch.setattr(p,'authority',lambda:dict(cap_seconds=200))
    monkeypatch.setattr(p.shutil,'disk_usage',lambda path:types.SimpleNamespace(free=6_000_000_000))
    projection=p.projection()
    assert (projection['status']=='ADMITTED')==admitted
    assert projection['sample_peak_rss_bytes']==peak and projection['memory_reserve_bytes']==2*peak
    assert projection['free_ram_bytes']==ram and projection['process_rss_cap_bytes']==2*1024**3
    # Admission must use live RAM even after a previously admitted projection.
    stored={**projection,'status':'ADMITTED'};p.atomic(tmp_path/'PROJECTION.json',stored)
    original=(tmp_path/'PROJECTION.json').read_bytes()
    if admitted:assert p.resource_gate(dict(rows=rows))['status']=='PASS'
    else:
        with pytest.raises(RuntimeError,match='RSS|memory reserve'):p.resource_gate(dict(rows=rows))
    assert (tmp_path/'PROJECTION.json').read_bytes()==original
    assert p.read(tmp_path/'resource_checks/0001.json')['observed_peak_rss_bytes']==peak


def test_available_ram_linux_and_macos_and_discovery_failure(monkeypatch):
    monkeypatch.setattr(p.sys,'platform','linux')
    monkeypatch.setattr(p.Path,'read_text',lambda *a,**k:'MemTotal: 90000 kB\nMemAvailable: 12345 kB\n')
    assert p.free_ram_bytes()==12345*1024
    monkeypatch.setattr(p.sys,'platform','darwin')
    monkeypatch.setattr(p.subprocess,'run',lambda *a,**k:types.SimpleNamespace(stdout='Mach Virtual Memory Statistics: (page size of 16384 bytes)\nPages free: 100.\nPages inactive: 200.\nPages speculative: 3.\n'))
    assert p.free_ram_bytes()==303*16384
    monkeypatch.setattr(p.subprocess,'run',lambda *a,**k:types.SimpleNamespace(stdout='unavailable'))
    with pytest.raises(RuntimeError,match='RAM discovery failed'):p.free_ram_bytes()


def test_finalized_resolution_hash_drift_blocks_replay_and_admission(boundary):
    b=boundary;p.resolve('014')
    path=b.root/'resolutions/014.json';log=p.read(path)
    p.atomic(path,{**log,'completion_receipt_sha256':'contradictory'})
    before={str(f):f.read_bytes() for f in b.root.rglob('*') if f.is_file()}
    with pytest.raises(RuntimeError,match='receipt drift'):p.resolve('014')
    with pytest.raises(RuntimeError,match='explicit resolve'):p.inventory()
    assert before=={str(f):f.read_bytes() for f in b.root.rglob('*') if f.is_file()}
