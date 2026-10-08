"""Synthetic orchestration tests only: mock child/gate, never launch a native fight."""
import copy
from collections import Counter
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
import torch
import collection as c
import process_gate as pg
from dynamics import baseline_drift
from fixtures import snapshot,threat,reflected
from models import Policy,export
from project import projection
from protocol import split
from test_slice import rpc

@pytest.fixture
def sandbox(monkeypatch,tmp_path):
    monkeypatch.setattr(c,'ROOT',tmp_path)
    monkeypatch.setattr(c,'admission',lambda:{'binary':'sealed'})
    monkeypatch.setattr(c,'cap',lambda:dict(cap_seconds=10800,approved_by='owner',date='2026-10-08'))
    monkeypatch.setattr(c,'process_gate',lambda **kw:{'status':'CLEAR'})
    return tmp_path

def fake_output(path,row):
    raw=[]
    for tick in range(1,3):
        raw.append(dict(fight=row['group'],cell=row['cell'],tick=tick,events=[dict(stage='threat_overflow',value=dict(own_shell=2,enemy_threats=1))]))
    lines=[json.dumps(r,separators=(',',':')) for r in raw]
    terminal=dict(terminal=True,cell=row['cell'],maximum_record_bytes=max(map(len,lines)))
    path.write_text('\n'.join([*lines,json.dumps(terminal)])+'\n')

@pytest.mark.parametrize('count',[12,20,200])
def test_inventory_balance_preassigned_splits_entropy(count):
    inv=c.inventory('collection-only','report-only',count,min(count,20))
    counts=Counter((r['cell'],r['guns'],r['orientation']) for r in inv['rows'])
    assert len(counts)==12 and max(counts.values())-min(counts.values())<=1
    assert len({r['seed'] for r in inv['rows']})==count
    assert all(r['seed']>=10000 and r['request']['fight']==r['group'] for r in inv['rows'])
    assert all(r['split']=='report' or r['split']==split(r['group']) for r in inv['rows'])
    assert not any(r['sample'] and r['split']=='report' for r in inv['rows'])
    changed=c.inventory('collection-only','different-report',count,min(count,20))
    assert [r for r in changed['rows'] if r['split']!='report']==[r for r in inv['rows'] if r['split']!='report']
    if count==200:
        assert Counter(r['split'] for r in inv['rows'])==dict(train=144,validation=24,test=12,report=20)
        for cell in c.STRATA:
            assert {'train','validation','test','report'}=={r['split'] for r in inv['rows'] if (r['cell'],r['guns'],r['orientation'])==cell}

@pytest.mark.parametrize('count,sample',[(201,20),(200,21),(11,11),(20,0)])
def test_inventory_hard_caps(count,sample):
    with pytest.raises(ValueError):c.inventory('a','b',count,sample)

def test_inventory_seal_resume_and_request_drift(sandbox,monkeypatch):
    inv=c.seal(20);assert c.admit_inventory()==inv and c.seal(20)==inv
    with pytest.raises(RuntimeError,match='sample count'):c.seal(12)
    altered=copy.deepcopy(inv);altered['rows'][0]['split']='report';c.atomic(sandbox/'INVENTORY.json',altered)
    with pytest.raises(RuntimeError,match='drift'):c.admit_inventory()

def test_sealed_source_drift(sandbox,monkeypatch):
    c.seal(20);monkeypatch.setattr(c,'admission',lambda:{'binary':'changed'})
    with pytest.raises(RuntimeError,match='drift'):c.admit_inventory()

def test_build_gate_requires_exact_binary_and_generator(sandbox,monkeypatch):
    monkeypatch.undo()
    # Verify admission on a synthetic build rather than rebuilding or fighting.
    root=sandbox/'slice';root.mkdir();binary=root/'_local/build/net_host';binary.parent.mkdir(parents=True);binary.write_text('binary')
    (root/'frozen').mkdir();(root/'frozen/collection_CONTRACT.md').write_text('contract')
    for name in ('requests.py','collection.py','project.py','protocol.py','process_gate.py'):(root/name).write_text(name)
    c.atomic(root/'BUILD.json',dict(status='PASS',sources={str(root/'requests.py'):c.sha(root/'requests.py')},reused_object_sha256={},binaries={'net_host':c.sha(binary)}))
    monkeypatch.setattr(c,'HERE',root);monkeypatch.setattr(c,'BINARY',binary)
    assert 'requests.py' in c.admission()
    (root/'requests.py').write_text('drift')
    with pytest.raises(RuntimeError,match='source/object drift'):c.admission()

def test_stream_measurements_overflow_and_truncation(sandbox):
    row=c.inventory('a','b')['rows'][0];out=sandbox/'data.jsonl';fake_output(out,row)
    values=c.measurements(out,row)
    assert values['decision_count']==2 and values['threat_overflow_by_kind']==dict(own_shell=4,enemy_threats=2)
    assert values['maximum_record_bytes']>=values['mean_record_bytes']>0
    out.write_bytes(out.read_bytes()[:-1])
    with pytest.raises(RuntimeError,match='truncated'):c.measurements(out,row)

def test_execute_atomic_resume_and_metrics(sandbox,monkeypatch):
    inv=c.seal(20);row=inv['rows'][0];calls=[]
    def mock_native(request,out,err,seconds):
        calls.append(request);assert seconds>0;fake_output(out,row);err.write_text('')
        return dict(wall_seconds=1,cpu_seconds=.8,rss_bytes=1234,exit_code=0,timed_out=False)
    monkeypatch.setattr(c,'native',mock_native)
    result=c.execute(row,c.time.monotonic()+30)
    assert result['wall_seconds']==1 and result['rss_bytes']==1234 and result['disk_bytes']>0
    assert c.execute(row,c.time.monotonic()+30)==result and len(calls)==1
    assert c.ledger(inv)['complete']==[row['group']]
    (sandbox/(row['group']+'.jsonl')).write_text('drift')
    with pytest.raises(RuntimeError,match='drift'):c.completed(row)

def test_partial_failure_preserved_and_counted(sandbox,monkeypatch):
    inv=c.seal(20);row=inv['rows'][0]
    def failed(req,out,err,seconds):
        out.write_text('partial\n');err.write_text('timeout')
        return dict(wall_seconds=3,cpu_seconds=2,rss_bytes=12,exit_code=-9,timed_out=True)
    monkeypatch.setattr(c,'native',failed)
    with pytest.raises(RuntimeError,match='interrupted'):c.execute(row,c.time.monotonic()+30)
    assert c.completed(row) is None and c.ledger(inv)['charged_wall_seconds']==3
    assert list((sandbox/'attempts').glob('*.partial.jsonl'))

def test_resume_after_receipt_before_atomic_output(sandbox):
    inv=c.seal(20);row=inv['rows'][0];partial=sandbox/'partial.jsonl';fake_output(partial,row)
    receipt=dict(inventory_sha256=c.sha(sandbox/'INVENTORY.json'),request=row['request'],raw_sha256=c.sha(partial),output=str(partial))
    c.atomic(sandbox/(row['group']+'.receipt.json'),receipt)
    assert c.completed(row)==receipt and not partial.exists()

def test_projection_requires_complete_sample_uses_measured_sizes(sandbox,monkeypatch):
    inv=c.seal(20)
    with pytest.raises(RuntimeError,match='complete sealed timing'):c.projected(inv)
    for row in inv['rows'][:20]:
        out=sandbox/(row['group']+'.jsonl');fake_output(out,row)
        receipt=dict(**c.measurements(out,row),request=row['request'],output=str(out),inventory_sha256=c.sha(sandbox/'INVENTORY.json'),raw_sha256=c.sha(out),wall_seconds=1,cpu_seconds=.5,rss_bytes=1024)
        c.atomic(sandbox/(row['group']+'.receipt.json'),receipt)
    projected=c.projected(inv)
    assert projected['collection_wall_seconds']==200
    assert projected['measurements']['decision_count']==40 and projected['measurements']['threat_overflow_by_kind']==dict(own_shell=80,enemy_threats=40)
    assert projected['hard_150s']['raw_JSON_reserve_bytes']==pytest.approx(200*150*30*1.3*projected['measurements']['maximum_record_bytes'])
    assert projected['hard_150s']['raw_JSON_reserve_bytes']<200*150*30*1048576
    monkeypatch.setattr(c.shutil,'disk_usage',lambda p:SimpleNamespace(free=10**12))
    assert c.resource_gate(inv)==projected
    monkeypatch.setattr(c,'cap',lambda:dict(cap_seconds=2,approved_by='owner',date='2026-10-08'))
    with pytest.raises(RuntimeError,match='run project again'):c.resource_gate(inv)
    c.projected(inv)
    with pytest.raises(RuntimeError,match='exceeds owner'):c.resource_gate(inv)

@pytest.mark.parametrize('mean,maximum',[(None,12),(0,12),(20,10),(10,1048577),(float('nan'),30)])
def test_projection_measured_inputs_rejected(mean,maximum):
    with pytest.raises(ValueError):projection(40,mean,maximum)

def test_projection_without_sample_does_not_budget_at_one_mib():
    assert projection()['disk_allowance_bytes'] is None
    assert projection()['status']=='SIZES_REQUIRED'

@pytest.mark.parametrize('index',[0,1,2,5])
def test_n2_baseline_admission(index,tmp_path):
    m=Policy('N2');weights=export(m,tmp_path/'weights.json')
    weights['parameters']['law']['values'][index]=.01
    assert 'frozen movement baseline' in rpc(dict(operation='forward',weights=weights,features=[0.]*1008,state=[0.]*4,message=[0.]*12),False)
    with torch.no_grad():m.law[index]=.01
    with pytest.raises(ValueError,match='baseline'):export(m,tmp_path/'bad.json')

@pytest.mark.parametrize('mirror',[False,True])
def test_teacher_labels_share_baseline_without_double_application(mirror):
    s=snapshot(2);s['threats']=[]
    if mirror:s=reflected(s)
    views=[s,{**copy.deepcopy(s),'self':2}]
    response=rpc(dict(operation='teacher',snapshots=views))
    positions=torch.tensor([[u['x'],u['y']] for u in s['units'][:2]],dtype=torch.float64)
    drift=baseline_drift(positions,[1,2],torch.tensor([80.,80.],dtype=torch.float64)).tolist()
    spacing=[d['value']['drift'] for d in response['diagnostics'] if d['stage']=='teacher_spacing']
    assert all(a==pytest.approx(b) for a,b in zip(spacing,drift))
    for i,entry in enumerate(response['actions']):
        action=entry['action'];assert action['move_index']==0 and action['multiplier']==1
        assert action['goal']==pytest.approx([positions[i,j].item()+drift[i][j] for j in range(2)])


def test_threat_overflow_kind_parity():
    s=snapshot(1);s['threats']=[threat('own_shell',i+1) for i in range(10)]+[threat('shell',11),threat('cast',12)]
    from schema import encode
    _,meta=encode(s);out=rpc(dict(operation='encode',snapshot=s))
    assert meta['own_shell_overflow']+meta['enemy_threat_overflow']==meta['threat_overflow']==4
    assert out['own_shell_overflow']==meta['own_shell_overflow'] and out['enemy_threat_overflow']==meta['enemy_threat_overflow']


def test_process_gate_foreign_local_and_vanished_retry(tmp_path,monkeypatch):
    monkeypatch.setattr(pg,'GATE_PATH',tmp_path/'gate.json');calls=[]
    outputs=iter([SimpleNamespace(returncode=0,stdout='42 /foreign/net_host\n',stderr=''),SimpleNamespace(returncode=1,stdout='',stderr='')])
    monkeypatch.setattr(pg.subprocess,'run',lambda *a,**kw:next(outputs))
    def gone(pid,command):calls.append(pid);raise RuntimeError('cwd unavailable')
    monkeypatch.setattr(pg,'classify_process',gone)
    monkeypatch.setattr(pg.os,'kill',lambda *a:(_ for _ in ()).throw(ProcessLookupError()))
    assert pg.process_gate()['status']=='CLEAR' and calls==[42]


def test_process_gate_live_unresolved_fails_closed(tmp_path,monkeypatch):
    monkeypatch.setattr(pg,'GATE_PATH',tmp_path/'gate.json')
    monkeypatch.setattr(pg.subprocess,'run',lambda *a,**kw:SimpleNamespace(returncode=0,stdout='42 /foreign/net_host\n',stderr=''))
    monkeypatch.setattr(pg,'classify_process',lambda *a:(_ for _ in ()).throw(RuntimeError('cwd unavailable')))
    monkeypatch.setattr(pg.os,'kill',lambda *a:None)
    with pytest.raises(RuntimeError,match='UNAVAILABLE'):pg.process_gate()


def test_process_gate_waits_only_repo_and_logs_foreign(tmp_path,monkeypatch):
    monkeypatch.setattr(pg,'GATE_PATH',tmp_path/'gate.json');outputs=iter(['42 /foreign/net_host\n43 '+str(pg.REPO_ROOT/'net_host')+'\n','42 /foreign/net_host\n'])
    monkeypatch.setattr(pg.subprocess,'run',lambda *a,**kw:SimpleNamespace(returncode=0,stdout=next(outputs),stderr=''))
    monkeypatch.setattr(pg.time,'sleep',lambda seconds:None)
    row=pg.process_gate()
    assert row['status']=='CLEAR' and row['ignored_foreign'][0]['pid']==42 and row['ignored_foreign'][0]['reason']


def test_launch_refuses_live_cap_below_spent_wall(sandbox,monkeypatch):
    inv=c.seal(20);row=inv['rows'][0];attempts=sandbox/'attempts';attempts.mkdir()
    c.atomic(attempts/'prior.json',dict(status='FAILED',wall_seconds=3,request=inv['rows'][1]['request']))
    monkeypatch.setattr(c,'cap',lambda:dict(cap_seconds=2,approved_by='owner',date='2026-10-08'))
    monkeypatch.setattr(c,'native',lambda *a:pytest.fail('must not launch'))
    with pytest.raises(TimeoutError,match='cap exhausted'):c.execute(row,c.time.monotonic()+30)


def test_exact_child_usage_without_engine(tmp_path,monkeypatch):
    # This synthetic executable only consumes JSON and emits text; no simulation.
    executable=tmp_path/'fake_host'
    executable.write_text('#!/bin/sh\ncat\n');executable.chmod(0o755)
    monkeypatch.setattr(c,'BINARY',executable)
    result=c.native(dict(value=1),tmp_path/'out',tmp_path/'err',10)
    assert result['exit_code']==0 and not result['timed_out']
    assert result['wall_seconds']>0 and result['cpu_seconds']>=0 and result['rss_bytes']>0
    assert json.loads((tmp_path/'out').read_text())==dict(value=1)


def test_repeated_vanished_race_fails_once(tmp_path,monkeypatch):
    monkeypatch.setattr(pg,'GATE_PATH',tmp_path/'gate.json');calls=[]
    monkeypatch.setattr(pg.subprocess,'run',lambda *a,**kw:SimpleNamespace(returncode=0,stdout='42 /foreign/net_host\n',stderr=''))
    monkeypatch.setattr(pg,'classify_process',lambda *a:(_ for _ in ()).throw(RuntimeError('cwd unavailable')))
    def gone(*a):calls.append(a);raise ProcessLookupError()
    monkeypatch.setattr(pg.os,'kill',gone)
    with pytest.raises(RuntimeError,match='repeated vanished'):pg.process_gate()
    assert len(calls)==2
