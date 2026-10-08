"""Reporting regression tests; synthetic receipts, no fights."""
import copy
import gzip
import hashlib
import json
import pathlib
import subprocess
import sys
from types import SimpleNamespace
import pytest
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import lab_r2 as lab
import report_r2 as report
import receipt_identity_r2 as hashes
import metrics

@pytest.fixture
def local(tmp_path,monkeypatch):
    raw=tmp_path/'raw';raw.mkdir()
    for module in (lab,report):
        monkeypatch.setattr(module,'HERE',tmp_path);monkeypatch.setattr(module,'RAW',raw)
    monkeypatch.setattr(lab,'SELECTED_ARM','E1')
    monkeypatch.setattr(lab,'identity',lambda:dict(pool=[f't{i}' for i in range(19)],timing=dict(mode='base',k=1,radius=400),labels={},reading=[]))
    lab.write(tmp_path/'DECLARATION.json',{})
    lab.write(tmp_path/'TIMING_SELECTION.json',dict(timing=dict(mode='base',k=1,radius=400)))
    return tmp_path

def record(raw,tag='D5_E1_p000'):
    # Measurement happens once, before the receipt is bound to the raw bytes.
    units=[[1,0,1,100,400,100,10,300,0,False,0,0,0,None]]
    terminal=dict(t=1,survivors=1,enemySurvivors=0,controllerFailures=[0,0])
    with gzip.open(raw/(tag+'.jsonl.gz'),'wt') as out:
        for row in (dict(observerV1=True,t=0,step=0,units=units),dict(observerV1=True,t=1,step=30,units=units),terminal):out.write(json.dumps(row)+'\n')
    stats,survivors=metrics.measure(raw/(tag+'.jsonl.gz'))
    lab.write(raw/(tag+'_request.json'),{'seed':1})
    declaration=lab.sha(lab.HERE/'DECLARATION.json');timing=lab.sha(lab.HERE/'TIMING_SELECTION.json')
    meta=dict(stage='mechanism',group='D5',arm='E1',pair=0,pair_key='D5:0')
    lab.write(raw/(tag+'_CLAIM.json'),dict(meta=meta,declaration_sha256=declaration,timing_sha256=timing,request_sha256=lab.sha(raw/(tag+'_request.json'))))
    native=dict(executed_fights=1)
    lab.write(raw/(tag+'_stderr.log'),native)
    r=dict(tag=tag,meta=meta,summary=terminal,stats=stats,survivors=survivors,native_metrics=native,declaration_sha256=declaration,timing_sha256=timing,request_sha256=lab.sha(raw/(tag+'_request.json')),claim_sha256=lab.sha(raw/(tag+'_CLAIM.json')),stderr_sha256=lab.sha(raw/(tag+'_stderr.log')),raw_sha256=lab.sha(raw/(tag+'.jsonl.gz')))
    lab.write(raw/(tag+'_COMPLETE.json'),r)
    lab.write(lab.HERE/'E1_REPORTING_R2.json',dict(inherited_receipts={tag:lab.sha(raw/(tag+'_COMPLETE.json'))}))
    return r

def test_verified_reuse_never_decodes_and_detects_receipt_or_raw_drift(local,monkeypatch):
    r=record(lab.RAW)
    monkeypatch.setattr(metrics,'measure',lambda *a:pytest.fail('receipt reuse decoded raw'))
    monkeypatch.setattr(gzip,'open',lambda *a,**k:pytest.fail('receipt reuse decoded raw'))
    assert lab.verified_record(r['tag'])==r
    path=lab.RAW/(r['tag']+'_COMPLETE.json');before=path.read_bytes()
    changed=copy.deepcopy(r);changed['stats']['shots_fired']=99;lab.write(path,changed)
    with pytest.raises(RuntimeError,match='measurement receipt drift'):lab.verified_record(r['tag'])
    path.write_bytes(before)
    raw=lab.RAW/(r['tag']+'.jsonl.gz');raw.write_bytes(raw.read_bytes()+b'changed')
    with pytest.raises(RuntimeError,match='raw/stderr drift'):lab.verified_record(r['tag'])

def test_new_measurement_seal_and_request_drift(local):
    r=record(lab.RAW);tag=r['tag']
    lab.write(local/'E1_REPORTING_R2.json',dict(inherited_receipts={}))
    lab.write(local/'metrics.py',{})
    lab.write(lab.RAW/(tag+'_VERIFIED_R2.json'),dict(receipt_sha256=lab.sha(lab.RAW/(tag+'_COMPLETE.json')),metrics_sha256=lab.sha(local/'metrics.py')))
    assert lab.verified_record(tag,{'seed':1},r['meta'])==r
    with pytest.raises(RuntimeError,match='request/metadata drift'):lab.verified_record(tag,{'seed':2})
    lab.write(local/'metrics.py',{'changed':True})
    with pytest.raises(RuntimeError,match='measurement seal drift'):lab.verified_record(tag)

def test_scope_filters_before_verification(local,monkeypatch):
    for tag,stage,group,arm in [('D5_base_p000','mechanism','D5','base'),('D5_E1_p000','mechanism','D5','E1'),('D1_base_p000','mechanism','D1','base'),('C3_V2_p000','outcome','C3','V2')]:
        lab.write(lab.RAW/(tag+'_COMPLETE.json'),dict(meta=dict(stage=stage,group=group,arm=arm)))
    calls=[]
    monkeypatch.setattr(lab,'verified_record',lambda tag:calls.append(tag) or tag)
    assert len(lab.records_for('mechanism',arm='E1'))==2
    assert set(calls)=={'D5_E1_p000','D5_base_p000'}
    calls.clear()
    lab.write(local/'E1_REPORTING_R2.json',dict(receipt_order=['D5_E1_p000','D5_base_p000']))
    lab.records_for('mechanism',arm='E1')
    assert calls==['D5_E1_p000','D5_base_p000']

def test_arm_is_explicit_and_legacy_summary_preserved(local,monkeypatch):
    r=record(lab.RAW)
    rows=[]
    for pair in range(20):
        for arm in ('base','E1'):
            row=copy.deepcopy(r);row['meta'].update(arm=arm,pair=pair,pair_key=f'D5:{pair}');row['tag']=f'D5_{arm}_p{pair:03d}';rows.append(row)
    monkeypatch.setattr(lab,'records_for',lambda stage,**kwargs:{r['tag']:r for r in rows} if stage=='mechanism' else {})
    lab.write(local/'MECHANISM_E1_SUMMARY.json',dict(arm='V2',drills=['D1','V2D2']))
    old=(local/'MECHANISM_E1_SUMMARY.json').read_bytes()
    path,summary=lab.stage_summary('mechanism')
    assert path.name=='MECHANISM_E1_SUMMARY_R2.json'
    assert summary['arm']=='E1' and list(summary['drills'])==['D5'] and summary['complete']
    assert summary['paired']['base minus E1']['n']==20
    report.render()
    assert lab.SELECTED_ARM=='E1' and path.exists()
    assert (local/'MECHANISM_E1_SUMMARY.json').read_bytes()==old
    assert list(lab.read(local/'OBSERVATIONS_E1_R2.json')['arms'])==['E1']
    with pytest.raises(RuntimeError,match='inactive mechanism'):lab.review('mechanism',50,'continue','activation absent')
    lab.review('mechanism',50,'stop','activation absent')
    assert lab.require_review('mechanism')['summary_sha256']==lab.sha(path)
    report.render() # idempotent, summary remains immutable
    monkeypatch.setattr(lab,'records_for',lambda stage,**kwargs:{r['tag']:r for r in rows[:-1]} if stage=='mechanism' else {})
    with pytest.raises(RuntimeError,match='stage summary drift'):report.render()
    monkeypatch.setattr(lab,'records_for',lambda stage,**kwargs:{r['tag']:r for r in rows} if stage=='mechanism' else {})
    path.write_text('{}')
    with pytest.raises(RuntimeError,match='stage summary drift'):report.render()

def test_done_run_only_reports(local,monkeypatch):
    lab.write(local/'RUN_mechanism_E1.json',dict(status='DONE'))
    before=(local/'RUN_mechanism_E1.json').read_bytes();calls=[]
    monkeypatch.setattr(lab,'report',lambda:calls.append('report'))
    monkeypatch.setattr(lab,'execute',lambda *a,**k:pytest.fail('DONE stage ran a fight'))
    monkeypatch.setattr(lab,'compute_attempt',lambda *a,**k:pytest.fail('DONE stage ran attempt'))
    lab.run('mechanism',50)
    assert calls==['report'] and (local/'RUN_mechanism_E1.json').read_bytes()==before

def test_hash_cache_invalidates_even_same_length(tmp_path):
    p=tmp_path/'x';p.write_bytes(b'abc');assert hashes.sha(p)==hashlib.sha256(b'abc').hexdigest()
    p.write_bytes(b'xyz');assert hashes.sha(p)==hashlib.sha256(b'xyz').hexdigest()

def test_cli_uses_canonical_revision_without_default_v2():
    code="""import runpy,sys
sys.path.insert(0,sys.argv[1])
import lab_r2
lab_r2.report=lambda:print('CANONICAL_ARM',lab_r2.SELECTED_ARM)
sys.argv=[sys.argv[1]+'/lab.py','report','--arm','E1']
runpy.run_path(sys.argv[0],run_name='__main__')
"""
    result=subprocess.run([sys.executable,'-B','-c',code,str(HERE)],text=True,capture_output=True,timeout=10)
    assert result.returncode==0,result.stderr
    assert 'CANONICAL_ARM E1' in result.stdout


def test_revision_manifest_has_no_document_execution_pins():
    manifest=json.loads((HERE/'E1_REPORTING_R2.json').read_text())
    assert not any('PLAN_CURRENT' in n or n.startswith('DESIGN_') or 'SHAPE_LAB_SPEC' in n for n in manifest['tool_hashes'])
