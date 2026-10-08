"""Real three-arm native smoke: shortened copies of sealed requests, no panel data."""
import json
from pathlib import Path
import sys
import time

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import a0_common as common
import a0_metrics as metrics
import a0_run as run


@pytest.mark.parametrize('arm',common.ARMS)
def test_real_host_measure_each_arm(arm,tmp_path,monkeypatch):
    admission=common.load('a0_host_admission',common.CPP/'build_admission.py')
    admission.admit(common.BINARY)
    ledger=common.read(run.LEDGER)
    sealed=next(j for j in ledger['jobs'] if j['stage']=='pilot' and
                j['panel']=='regular' and j['index']==0 and j['arm']==arm)
    source=run.REQUESTS/(sealed['tag']+'.json')
    before=source.read_bytes()
    assert common.sha(source)==sealed['request_sha256']
    request=json.loads(before)
    assert request['labShapes']['arm']==arm
    request['options']['duration']=3
    # Seal a separate short-duration fixture; original bytes and ledger stay intact.
    fixture=tmp_path/'requests'/(sealed['tag']+'.json')
    common.write(fixture,request,exclusive=True)
    job={**sealed,'request_sha256':common.sha(fixture)}
    fixture_ledger=tmp_path/'fixture_ledger.json'
    common.write(fixture_ledger,{'status':'INTEGRATION_FIXTURE_ONLY','source_request_sha256':sealed['request_sha256']})
    monkeypatch.setattr(run,'LOCAL',tmp_path)
    monkeypatch.setattr(run,'HERE',tmp_path)
    monkeypatch.setattr(run,'LEDGER',fixture_ledger)
    monkeypatch.setattr(run,'REQUESTS',fixture.parent)
    monkeypatch.setattr(run,'RAW',tmp_path/'raw')
    monkeypatch.setattr(run,'RECOVERY',tmp_path/'unused_recovery.json')
    deadline=time.monotonic()+60
    monkeypatch.setattr(run,'_DEADLINE',deadline)
    # Exercise the production launch and resource checks, without mocking the host.
    with run.lock():
        run.process_gate(deadline)
        result=run.execute(job,deadline)
    receipt=common.read(run.RAW/(job['tag']+'_COMPLETE.json'))
    measured=metrics.measure(run.RAW/receipt['raw_file'])
    assert measured==result['stats']
    assert 3<=measured['t_end']<3.1 and measured['label_rows']>0
    assert all(measured['per_role_labels'][r]['rows']>0 for r in ('melee','ranged','artillery'))
    assert receipt['wire_form']==run.WIRE_FORM
    attempt=common.read(run.RAW/(job['tag']+'_'+receipt['attempt_id']+'_ATTEMPT.json'))
    assert attempt['status']=='DONE' and '--metrics' not in attempt['host_command']
    assert (run.RAW/(job['tag']+'_'+receipt['attempt_id']+'.stderr')).read_bytes()==b''
    assert source.read_bytes()==before
