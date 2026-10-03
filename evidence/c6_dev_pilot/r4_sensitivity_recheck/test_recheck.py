"""Negative controls and synthetic fault probes; no experimental/native runs."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from types import SimpleNamespace
import pytest

HERE=Path(__file__).resolve().parent

def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

audit=module('qh_read_audit',HERE/'audit.py')
legacy=module('qh_archived_pilot',HERE.parent/'r4_sensitivity/pilot.py')


def minimal_rows():
    return [{'pair':i,'arm':a,'status':'COMPLETE','qualification':{'qualified':False,'candidates':[]},
             'retention':{'retained':False},'paired_material':{},'perturbations':{},'background_condition_held':True} for i in range(16) for a in ('Q','H')]


def synthetic_spec():
    return {'schedule':[[0,'Q']], 'caps':{'workers':1,'cpu_seconds':10.,'worker_rss_bytes':2*1024**3,'arm_wall_seconds':2.,'cancel_wall_seconds':3.,'wall_seconds':4.}}


def test_strict_parser_rejects_nonfinite_and_duplicate_keys(tmp_path):
    p=tmp_path/'bad.json'
    for value in ('{"x":NaN}','{"x":1,"x":2}','{"x":Infinity}'):
        p.write_text(value)
        with pytest.raises(audit.InvalidRecord):audit.read(p)


def test_duplicate_identity_legacy_accepts_new_validator_rejects():
    rows=minimal_rows();rows.append(copy.deepcopy(rows[0]))
    assert legacy.interpret(rows)['status']=='COMPLETE'
    with pytest.raises(audit.InvalidRecord,match='duplicate arm'):audit.index_rows(rows)


def test_identity_validator_rejects_bool_missing_and_out_of_range():
    for change in ('bool','missing','out_of_range'):
        rows=minimal_rows()
        if change=='bool':rows[0]['pair']=False
        elif change=='missing':rows.pop()
        else:rows[0]['pair']=16
        with pytest.raises(audit.InvalidRecord):audit.index_rows(rows)


def test_direct_worker_entry_bypasses_consumed_latch(tmp_path,monkeypatch):
    (tmp_path/'run').mkdir()
    calls=[]
    monkeypatch.setattr(legacy,'HERE',tmp_path)
    monkeypatch.setattr(legacy,'worker',lambda *args:calls.append(args) or 0)
    monkeypatch.setattr(sys,'argv',['pilot.py','--worker','0','Q','--output',str(tmp_path)])
    assert legacy.main()==0 and len(calls)==1
    # Only a stub was called; no population or native load occurs.


def test_native_guard_race_reaches_original_build_fallback(tmp_path,monkeypatch):
    from geomind import c6_r4_field as F
    source=tmp_path/'native/c6_r4/field.cpp';library=tmp_path/'build/c6_r4/field.dylib'
    source.parent.mkdir(parents=True);library.parent.mkdir(parents=True)
    source.write_text('synthetic source');library.write_bytes(b'synthetic binary')
    record={'source_sha256':legacy.digest(source),'binary_sha256':legacy.digest(library)}
    build_record=library.parent/'BUILD.json';build_record.write_text(json.dumps(record))
    spec={'native_build':record,'file_hashes':{str(p.relative_to(tmp_path)):legacy.digest(p) for p in (source,library,build_record)}}
    monkeypatch.setattr(legacy,'ROOT',tmp_path)
    monkeypatch.setattr(F.build,'SOURCE',source);monkeypatch.setattr(F.build,'LIBRARY',library)
    monkeypatch.setattr(F,'_NATIVE',None)
    real_guard=legacy.guard
    def checked_then_changed(s):
        real_guard(s);library.write_bytes(b'changed after guard')
    def blocked_build():
        raise RuntimeError('REBUILD_ATTEMPT_CONFIRMED_NO_COMPILER_CALLED')
    monkeypatch.setattr(legacy,'guard',checked_then_changed)
    monkeypatch.setattr(F.build,'build',blocked_build)
    with pytest.raises(RuntimeError,match='REBUILD_ATTEMPT_CONFIRMED'):
        legacy.native_without_build(spec)


def test_malformed_partial_breaks_final_receipt(tmp_path):
    fake="from pathlib import Path;import sys;p=Path(sys.argv[1])/('pair_'+int(sys.argv[2]).__format__('02d')+'_'+sys.argv[3]+'.json');p.write_text('{');raise SystemExit(2)"
    with pytest.raises(json.JSONDecodeError):legacy.supervise(synthetic_spec(),tmp_path,fake)
    assert not (tmp_path/'SUMMARY.json').exists()
    assert (tmp_path/'pair_00_Q.json').read_text()=='{'


def test_cancellation_failure_breaks_final_receipt(tmp_path,monkeypatch):
    def broken_cancel(active):raise OSError('synthetic cancellation bookkeeping failure')
    monkeypatch.setattr(legacy,'cancel',broken_cancel)
    spec=synthetic_spec();spec['schedule']=[]
    with pytest.raises(OSError,match='bookkeeping'):legacy.supervise(spec,tmp_path,'unused')
    assert not (tmp_path/'SUMMARY.json').exists()


def test_final_cpu_breach_has_no_stop(tmp_path,monkeypatch):
    state={'reaped':False};spec=synthetic_spec()
    class Child:
        pid=987654321;returncode=None
    def popen(*args,**kw):
        (tmp_path/'pair_00_Q.json').write_text('{"status":"COMPLETE"}')
        return Child()
    def wait4(pid,options):
        state['reaped']=True
        return pid,0,SimpleNamespace(ru_maxrss=100,ru_utime=20.,ru_stime=0.)
    monkeypatch.setattr(legacy.subprocess,'Popen',popen)
    monkeypatch.setattr(legacy.os,'wait4',wait4)
    monkeypatch.setattr(legacy,'process_usage',lambda groups:{pid:{'cpu':0.,'rss':100,'pids':[]} for pid in groups})
    monkeypatch.setattr(legacy,'supervisor_cpu',lambda:20. if state['reaped'] else 0.)
    result=legacy.supervise(spec,tmp_path,'synthetic stub')
    assert result['cpu_seconds']>spec['caps']['cpu_seconds'] and result['stop_reason'] is None


def test_final_write_outside_recorded_wall_and_cap(tmp_path,monkeypatch):
    spec=synthetic_spec();spec['schedule']=[];spec['caps'].update(wall_seconds=.1,cancel_wall_seconds=.05)
    original=legacy.atomic
    def delayed(path,value):
        if path.name=='SUMMARY.json':time.sleep(.2)
        return original(path,value)
    monkeypatch.setattr(legacy,'atomic',delayed)
    started=time.monotonic();result=legacy.supervise(spec,tmp_path,'unused')
    elapsed=time.monotonic()-started
    assert elapsed>.1 and result['seconds']<.1 and result['stop_reason'] is None


def test_completed_leader_leaves_unmonitored_descendant(tmp_path,monkeypatch):
    groups=[];original=legacy.subprocess.Popen
    def tracked(*args,**kwargs):
        child=original(*args,**kwargs)
        if kwargs.get('start_new_session'):groups.append(child.pid)
        return child
    monkeypatch.setattr(legacy.subprocess,'Popen',tracked)
    fake="from pathlib import Path;import sys,subprocess;d=Path(sys.argv[1]);c=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)']);(d/'descendant_pid').write_text(str(c.pid));(d/'pair_00_Q.json').write_text('{\"status\":\"COMPLETE\"}')"
    try:
        result=legacy.supervise(synthetic_spec(),tmp_path,fake)
        descendant=int((tmp_path/'descendant_pid').read_text())
        os.kill(descendant,0)
        assert result['stop_reason'] is None and len(result['accounting'])==1
        assert groups
    finally:
        for group in groups:
            try:os.killpg(group,signal.SIGKILL)
            except ProcessLookupError:pass


def test_complete_flag_does_not_replace_required_trajectory():
    row={'pair':0,'arm':'Q','status':'COMPLETE','qualification':{'qualified':False},'retention':{'retained':False,'applicable':False},'checks':[]}
    with pytest.raises(audit.InvalidRecord,match='scope checks'):
        audit.verify_row(row,json.loads(legacy.SPEC.read_text())['settings'])


def test_reconstructed_count_checker_has_no_native_loader(monkeypatch):
    from geomind import c6_r4_field as F
    monkeypatch.setattr(F,'native',lambda:pytest.fail('audit must never load native'))
    row=audit.read(audit.PILOT/'run/pair_15_H.json')
    settings=audit.read(audit.PILOT/'SPEC.json')['settings']
    derived=audit.verify_row(row,settings)
    assert derived['rolling_rederived']
    bad=copy.deepcopy(row);bad['retention']['rolling_by_dt'][0][0]['stats']['freq_change']+=.1
    with pytest.raises(audit.InvalidRecord,match='statistic mismatch'):audit.verify_row(bad,settings)
