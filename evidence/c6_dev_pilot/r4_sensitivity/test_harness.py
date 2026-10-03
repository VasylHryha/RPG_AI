"""Supervisor/record tests only: no scientific imports or pilot inputs."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import pytest

MODULE = Path(__file__).with_name('pilot.py')
loader = importlib.util.spec_from_file_location('qh_pilot', MODULE)
pilot = importlib.util.module_from_spec(loader)
loader.loader.exec_module(pilot)


def spec(**overrides):
    caps={'workers':2,'cancel_wall_seconds':3.,'cpu_seconds':10.,'worker_rss_bytes':2*1024**3,'arm_wall_seconds':2.}
    caps.update(overrides)
    return {'caps':caps,'schedule':[[0,'Q'],[0,'H'],[1,'H'],[1,'Q']]}


COMPLETE = "import json,sys;from pathlib import Path;p=Path(sys.argv[1])/('pair_'+int(sys.argv[2]).__format__('02d')+'_'+sys.argv[3]+'.json');p.write_text(json.dumps({'status':'COMPLETE'}))"
PARTIAL_SLEEP = "import json,sys,time;from pathlib import Path;p=Path(sys.argv[1])/('pair_'+int(sys.argv[2]).__format__('02d')+'_'+sys.argv[3]+'.json');p.write_text(json.dumps({'status':'INCOMPLETE','checkpoint':'saved'}));time.sleep(20)"


def test_order_and_accounting(tmp_path):
    result=pilot.supervise(spec(),tmp_path,COMPLETE)
    assert result['stop_reason'] is None
    assert len(result['accounting'])==4
    assert not result['unsubmitted']
    assert all(r['cpu_seconds']>=0 and r['peak_rss_bytes']>0 for r in result['accounting'])


@pytest.mark.parametrize('caps,reason',[
    ({'arm_wall_seconds':.25},'ARM_WALL_CAP'),
    ({'cancel_wall_seconds':.25},'GLOBAL_WALL_CANCELLATION'),
    ({'worker_rss_bytes':1},'WORKER_RSS_CAP'),
    ({'cpu_seconds':.10},'AGGREGATE_CPU_CAP'),
])
def test_caps_preserve_partial_and_cancel_queue(tmp_path,caps,reason):
    fake=PARTIAL_SLEEP if reason!='AGGREGATE_CPU_CAP' else PARTIAL_SLEEP.rsplit(';',1)[0]+'\nwhile True: pass'
    result=pilot.supervise(spec(**caps),tmp_path,fake)
    assert result['stop_reason']==reason
    assert len(result['accounting'])==2
    assert len(result['unsubmitted'])==2
    assert all(r['cancelled'] for r in result['accounting'])
    for p in tmp_path.glob('pair_*.json'):
        assert json.loads(p.read_text())['checkpoint']=='saved'
    assert result['seconds']<6.5


def test_worker_failure_stops_without_replacement(tmp_path):
    result=pilot.supervise(spec(),tmp_path,'raise RuntimeError("synthetic failure")')
    assert result['stop_reason']=='INCOMPLETE_WORKER'
    assert len(result['accounting'])==2
    assert len(result['unsubmitted'])==2


def test_atomic_replaces_complete_json(tmp_path):
    p=tmp_path/'record.json'
    pilot.atomic(p,{'first':1});pilot.atomic(p,{'second':2})
    assert json.loads(p.read_text())=={'second':2}
    assert not p.with_suffix('.json.tmp').exists()
    with pytest.raises(ValueError):pilot.atomic(p,{'bad':float('nan')})
    assert json.loads(p.read_text())=={'second':2}


def test_no_native_load_on_bad_identity(tmp_path):
    with pytest.raises(RuntimeError,match='dependency'):
        pilot.native_without_build({'file_hashes':{'absent_native_artifact':'0'*64}})


def test_partial_pair_is_missing_not_negative():
    assert pilot.interpret([{'pair':0,'arm':'Q','status':'INCOMPLETE'}])['paired_outcomes'][0]['Q'] is None


def test_guard_and_one_shot_latch():
    pilot.guard(json.loads(pilot.SPEC.read_text()))
    source=MODULE.read_text()
    assert 'output.mkdir()' in source
    assert 'exist_ok=True' not in source


def test_owned_descendants_killed_unrelated_survives(tmp_path):
    unrelated=subprocess.Popen([sys.executable,'-c','import time;time.sleep(20)'],start_new_session=True)
    fake="import subprocess,sys,time;from pathlib import Path;c=subprocess.Popen([sys.executable,'-c','import time;time.sleep(20)']);(Path(sys.argv[1])/('descendant_'+sys.argv[2]+sys.argv[3])).write_text(str(c.pid));time.sleep(20)"
    try:
        result=pilot.supervise(spec(arm_wall_seconds=.4),tmp_path,fake)
        assert result['stop_reason']=='ARM_WALL_CAP'
        assert unrelated.poll() is None
        listing=subprocess.check_output(['ps','-axo','pid=,stat='],text=True)
        state={int(line.split()[0]):line.split()[1] for line in listing.splitlines()}
        for p in tmp_path.glob('descendant_*'):
            pid=int(p.read_text())
            assert pid not in state or state[pid].startswith('Z')
    finally:
        unrelated.terminate();unrelated.wait()


def test_asymmetric_shutdown_reaps_only_once(tmp_path):
    fake="import signal,sys,time\nif sys.argv[3]=='H': signal.signal(signal.SIGTERM,lambda *a:time.sleep(.3))\ntime.sleep(20)"
    result=pilot.supervise(spec(arm_wall_seconds=.3),tmp_path,fake)
    assert result['stop_reason']=='ARM_WALL_CAP'
    assert len(result['accounting'])==2


def test_main_refuses_existing_run_directory(tmp_path,monkeypatch):
    (tmp_path/'run').mkdir()
    monkeypatch.setattr(pilot,'HERE',tmp_path)
    monkeypatch.setattr(sys,'argv',['pilot.py','--run'])
    with pytest.raises(FileExistsError): pilot.main()
